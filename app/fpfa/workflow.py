"""Double-interlock zone workflow.

The numbers in the result come from a fixed tool plan on the designer's form.
A Claude narrative is optional. If the model skips a tool, uses different
arguments, or is unreachable, the tables still use this plan.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Callable

from fpfa import coherence, inputs
from fpfa.calc_tools import REQUIRED_DI_TOOLS, SCHEMAS, ToolSession
from fpfa.claude_client import MODEL_ID, TurnCancelled, incomplete_notice, safe_error
from fpfa.everyday import EVERYDAY_ROLE, SPECIALIST_ROLES, assemble_system
from fpfa.modes_loader import MODE_SLUGS, NARRATION_MODE, list_modes, normalize_mode
from fpfa.record import Record
from fpfa.releasing import reader_view, releasing_logic, releasing_sentence, second_leg_value  # noqa: F401  (re-exported)
from fpfa.roles_loader import list_roles
from fpfa.skills_loader import list_skills

# Methods this workflow asks the model to read. Bodies stay in skills/<slug>/SKILL.md.
DI_SKILL_SLUGS = [
    "sprinkler-system-volume-takeoff",
    "dry-preaction-water-delivery-screen",
    "preaction-el-el-trim-election",
    "preaction-releasing-c-and-e-soo",
    "fa-double-interlock-releasing-cause-and-effect",
    "nitrogen-inerting-and-c-factor-gate",
    "density-area-dry-increase",
]


# Warning and flag text when the designer cancels a narration mid-run.
NARRATION_CANCELLED = "Narration cancelled by the designer. Tables stay on the tool plan."


def fmt1(value: Any) -> str:
    return f"{float(value):.1f}"


def system_prompt(content_root: Path, mode: str | None = None) -> str:
    """Shell, active mode, and indexes from the content pack.

    Specialist bodies stay in ROLE.md. Other mode bodies stay in MODE.md.
    """
    return assemble_system(content_root, mode)


def judgment_label_line() -> str:
    """Designer judgment the tools did not return. Not ASSUMED and not calculated."""
    return (
        "Designer judgment the tools did not return: use best judgment. "
        "Not a calculated figure."
    )


def label_glossary() -> str:
    """The three figure labels, kept as different words."""
    return (
        "Three labels stay distinct. "
        "Pipe gallons and t_total are calculated. "
        "ASSUMED stays on blank trim and on the screen-limit lookup. "
        "A value the designer types is not assumed. "
        + judgment_label_line()
    )


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _float(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    return number


# The rows a zone run makes beyond the takeoff and the trim screen, by what the zone is and what the form holds.
DELIVERY_TOOLS = ("dry_delivery_screen", "di_trip_to_water")
DEMAND_TOOLS = ("hose_duration", "density_area")
DELIVERY_SYSTEMS = ("dry", "di")
# Inputs a row needs, by the rows that run. A blank one holds the run, named (inputs.run_problem).
_ALWAYS = ("system_type", "length_basis")
_DELIVERY_NEEDS = ("qod", "delivery_basis", "q_fill_gpm")
_GAS_NEEDS = ("supervisory_psig", "fill_minutes")
# The releasing table and the trim election are double-interlock only: a dry zone is not asked for either answer.
_RELEASING_NEEDS = ("manual_station", "failsafe_on_total_power_loss")
_DEMAND_NEEDS = ("hazard", "supervised", "density_gpm_ft2", "base_area_ft2", "area_increase", "hose_gpm")
WET_NOTE = "A wet zone has no delivery rows, no supervisory gas fill, and no releasing table: none was run."
DRY_RELEASING_NOTE = "The releasing table is for double-interlock zones. None was run for this dry-pipe zone."
# What the volume rows say beside the volume when the lengths are center-to-center and no allowance is added, and the
# friction sentence that goes with it. The section and its edition are the calc pack's own label (calcs/fp/formulas.py
# cites "NFPA 13-2025 s28.2.3" for fitting equivalent lengths); a test reads the phrase there.
NO_ALLOWANCE = "center-to-center, no allowance"
FRICTION_NOTE = ("Friction still adds fitting equivalent lengths (NFPA 13-2025 §28.2.3, as the calc pack labels it, "
                 "VERIFY).")
FRICTION_PACK_FILE = "calcs/fp/formulas.py"
FRICTION_PACK_PHRASE = "NFPA 13-2025 s28.2.3"
NO_DEMAND_NOTE = ("No demand was run: the form holds no density or base area. The delivery and gas-fill screens "
                  "do not use one.")


def plan_rows(di: dict) -> dict[str, bool]:
    """Which rows a zone run makes. Read from the form, never defaulted.

    Dry and double-interlock zones get the delivery rows and the supervisory
    gas fill; only a double-interlock zone gets the releasing table, and only
    it is asked for the manual station and the failsafe answer. A wet zone
    gets none of them. The demand (hose duration and density/area) runs when
    the form holds a density or a base area, and never feeds the delivery or
    gas-fill screens.
    """
    system = str(di.get("system_type") or "").strip()
    wetted = system in DELIVERY_SYSTEMS
    demand = not (_blank(di.get("density_gpm_ft2")) and _blank(di.get("base_area_ft2")))
    return {"delivery": wetted, "gas": wetted, "releasing": system == "di", "demand": demand}


def planned_tools(di: dict) -> list[str]:
    """The tools a zone run on this form calls, in order (plan_rows)."""
    rows = plan_rows(di)
    names = ["zone_trapped_volume"]
    if rows["delivery"]:
        names += list(DELIVERY_TOOLS)
    if rows["demand"]:
        names += list(DEMAND_TOOLS)
    if rows["gas"]:
        names.append("nitrogen_gate")
    names.append("elect_di_trim")
    if rows["releasing"]:
        names.append("releasing_truth_table")
    return names


def validate_di(di: dict) -> None:
    """Refuse a zone run its tools cannot make on what the form holds, naming every problem at once.

    A blank stays blank here as everywhere: the run does not put a 0, a hint,
    or a starting value in its place, and a 0 is not replaced either. What is
    needed follows the rows that run (plan_rows): a fill flow, a supervisory
    fill, and a fill time greater than 0 and a time basis for a dry or
    double-interlock zone; a density and a base area greater than 0, and an
    area increase and a hose that may be 0 but not blank, for a demand. The
    detection, releasing, and exhaust times may be blank (the delivery rows are
    then the fill time alone, with no pass or fail) or 0 (ASSUMED-ZERO), never
    negative. A choice or a yes/no a row takes must be chosen.
    """
    segments = di.get("segments") or []
    if not isinstance(segments, list) or not segments:
        raise ValueError("Add at least one pipe segment.")
    for index, segment in enumerate(segments, start=1):
        if _blank(segment.get("length_ft")):
            raise ValueError(f"Segment {index} needs a length in feet.")
        if _blank(segment.get("d_in")) and _blank(segment.get("nps")):
            raise ValueError(f"Segment {index} needs a nominal size or an inside diameter.")
    problems = [problem for problem in (inputs.run_problem(name, di.get(name)) for name in _ALWAYS) if problem]
    if problems:
        raise ValueError(" ".join(problems))
    rows = plan_rows(di)
    names: list[str] = []
    if rows["delivery"]:
        names += [*_DELIVERY_NEEDS, *inputs.SUB_TIMES]
    if rows["gas"]:
        names += list(_GAS_NEEDS)
    if rows["releasing"]:
        names += list(_RELEASING_NEEDS)
    if rows["demand"]:
        names += list(_DEMAND_NEEDS)
    problems = [problem for problem in (inputs.run_problem(name, di.get(name)) for name in names) if problem]
    if problems:
        raise ValueError(" ".join(problems))


def _opt_float(value: Any, label: str) -> float | None:
    if _blank(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    return number


def plan_edition(basis: dict | None, assumed: Any = ()) -> str | None:
    """The NFPA 13 edition year the job pins, for the delivery rows. None when it pins none.

    Blank, not one year, or ASSUMED (a hint the designer used) pins nothing:
    the rows then run with their cites withheld. No edition is taken for it.
    """
    if "nfpa_13" in set(assumed or ()):
        return None
    return coherence.stated_edition((basis or {}).get("nfpa_13"))


def run_tool_plan(session: ToolSession, di: dict, basis: dict, assumed: Any = ()) -> tuple[dict[str, Any], dict[str, dict]]:
    """Run the zone tools in order. Later steps use earlier tool outputs.

    The second value is the argument dict actually passed to each tool. The
    transcript and the Claude request advertise that dict, not a shorter copy.
    Only the rows plan_rows names run; a row that does not is absent.
    """
    validate_di(di)
    rows = plan_rows(di)
    assumed = set(assumed or ())
    sent: dict[str, dict] = {}

    def call(name: str, arguments: dict) -> Any:
        sent[name] = arguments
        return session.execute(name, arguments)

    # Every value below is the form's own, as validate_di accepted it: no 0, hint, or starting value stands in
    # for a blank. The trim medium, the prime holder, the low-air setting, the fittings allowance, and the trim
    # volume may be blank; the first two then reach the kernel as its own words for no election ("unelected",
    # "unknown", calc_tools), the last two as the kernel's ASSUMED allowance and trim, and the record keeps them
    # blank.
    system = di.get("system_type")
    tools: dict[str, Any] = {}
    volume = tools["zone_trapped_volume"] = call("zone_trapped_volume", {
        "segments": di.get("segments"),
        "length_basis": di.get("length_basis"),
        "fittings_percent": _opt_float(di.get("fittings_percent"), "Fittings percent"),
        "trim_gal": _opt_float(di.get("trim_gal"), "Trim"),
    })
    if rows["delivery"]:
        pipe_only = [
            {"d_in": row["d_in"], "length_ft": row["length_ft"]}
            for row in volume["segments"]
        ]
        # A blank sub-time is left out, never sent as 0: the rows are then the fill time alone (calc_tools).
        common_time = {
            "q_fill_gpm": di.get("q_fill_gpm"),
            **{name: di.get(name) for name in inputs.SUB_TIMES if not _blank(di.get(name))},
            "basis": di.get("delivery_basis"),
            "system_type": system,
        }
        # The job's own NFPA 13 edition. Not pinned, none is sent and the rows' cites are withheld.
        edition = plan_edition(basis, assumed)
        if edition is not None:
            common_time["edition"] = edition
        # The kernel screen compares pipe volume with the threshold. The size exemption is judged on the zone
        # total, so the screen is handed the takeoff's own zone_gal and the recorded row carries that answer.
        # What is recorded is then what the narrative, the tiles, and both documents print.
        tools["dry_delivery_screen"] = call("dry_delivery_screen", {
            "segments": pipe_only,
            "qod": di.get("qod"),
            "zone_gal": volume["zone_gal"],
            # The basis the zone total was taken on, so the screen's row names it beside its answer.
            "length_basis": di.get("length_basis"),
            "declared_interlock": "double" if system == "di" else "none",
            **common_time,
        })
        tools["di_trip_to_water"] = call("di_trip_to_water", {
            "v_gal": volume["zone_gal"],
            **common_time,
        })
    if rows["demand"]:
        hose = tools["hose_duration"] = call("hose_duration", {
            "hazard": di.get("hazard"),
            "supervised": di.get("supervised"),
        })
        # The form's own values, as validate_di accepted them. A 0 stays 0 and nothing blank reaches here. A density
        # or an area the designer took from its hint is ASSUMED, and the demand says so.
        demand_assumed = [name for name in ("density_gpm_ft2", "base_area_ft2") if name in assumed]
        demand = {
            "density_gpm_ft2": di.get("density_gpm_ft2"),
            "base_area_ft2": di.get("base_area_ft2"),
            "area_increase": di.get("area_increase"),
            "hose_gpm": di.get("hose_gpm"),
            "duration_min": hose["duration_min"],
        }
        if demand_assumed:
            demand["assumed"] = demand_assumed
            demand["assumed_reason"] = "a hint the designer used on the zone form: " + "; ".join(
                hint.cite for name in demand_assumed for hint in inputs.hints_of(name)) + ", VERIFY"
        tools["density_area"] = call("density_area", demand)
    if rows["gas"]:
        tools["nitrogen_gate"] = call("nitrogen_gate", {
            "v_gal": volume["zone_gal"],
            "p_psig": di.get("supervisory_psig"),
            "t_min": di.get("fill_minutes"),
        })
    tools["elect_di_trim"] = call("elect_di_trim", {
        "system_type": system,
        "prime_held_by": di.get("prime_held_by"),
        "failsafe_on_total_power_loss": di.get("failsafe_on_total_power_loss"),
        "supervisory_psi": _opt_float(di.get("supervisory_psi"), "Supervisory pressure"),
        "medium": di.get("medium"),
        "insurer": (basis or {}).get("insurer") or "",
    })
    if rows["releasing"]:
        # A blank insurer stays blank. It is not taken as FM.
        tools["releasing_truth_table"] = call("releasing_truth_table", {
            "manual_station": di.get("manual_station"),
            "insurer": (basis or {}).get("insurer") or "",
        })
    return tools, sent


def _plan_transcript(tools: dict[str, Any], sent: dict[str, dict]) -> list[dict]:
    """Pair each tool output with the arguments run_tool_plan actually passed."""
    calls = []
    for name, output in tools.items():
        calls.append({
            "name": name,
            "input": sent[name],
            "output": output,
            "is_error": False,
            "by": "tool-plan",
        })
    return calls


EXEMPTION_NOT_DETERMINED = (
    "Not determined. This is a pipe-only screen: fittings and trim are not in it, and the size exemption is "
    "judged on the zone total. Run zone_trapped_volume and pass its zone_gal."
)
EXEMPTION_PIPE_ALREADY_OVER = (
    "No. The pipe alone is over the exemption threshold, so the zone total is too."
)


def threshold_gal(screen: dict | None) -> float | None:
    """The size exemption threshold the kernel returned: nfpa_size_threshold_gal, or its legacy alias on an older row."""
    screen = screen if isinstance(screen, dict) else {}
    for key in ("nfpa_size_threshold_gal", "nfpa_size_cap_gal"):
        value = screen.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


_SECTION = re.compile(r"(?<![A-Za-z])s(\d+(?:\.\d+)+)")


def threshold_words(screen: dict) -> str:
    """The threshold as the narrative names it, with the section and edition the kernel's own cite gives.

    "the 500 gal exemption threshold (NFPA 13-2025 §8.3.2.3.1.1)". The section
    is read from the kernel's nfpa_basis, never written here. Cites withheld
    (no edition pinned, or one the pack does not label), the bracket says so.
    """
    threshold = threshold_gal(screen)
    figure = f"{threshold:.0f} gal " if threshold is not None else ""
    withheld = screen.get("cites_withheld")
    if withheld:
        return f"the {figure}exemption threshold ({withheld})"
    basis = str(screen.get("nfpa_basis") or "")
    found = _SECTION.search(basis)
    edition = screen.get("edition")
    if found and edition:
        return f"the {figure}exemption threshold (NFPA 13-{edition} §{found.group(1)})"
    return f"the {figure}exemption threshold"


def govern_nfpa_exemption(screen: dict, zone_gal: float, volume_basis: str = "") -> dict:
    """Size exemption follows the zone total (pipe + fittings + trim).

    ``dry_delivery_screen`` reports the exemption on pipe volume. Timing for that
    pipe-only screen stays. ``nfpa_delivery_time_exempt`` becomes the zone-total
    check against the same threshold, including the double-interlock rule that a
    quick-opening device does not raise it. ``exemption_volume_basis`` says
    what the zone total was made of.
    """
    governed = dict(screen)
    threshold = threshold_gal(screen)
    governed["pipe_only_volume_gal"] = float(screen["volume_gal"])
    governed["pipe_only_nfpa_delivery_time_exempt"] = bool(
        screen.get("pipe_only_nfpa_delivery_time_exempt", screen["nfpa_delivery_time_exempt"]))
    governed["exemption_volume_gal"] = float(zone_gal)
    governed["nfpa_delivery_time_exempt"] = float(zone_gal) <= threshold + 1e-9
    governed["exemption_volume_basis"] = volume_basis or "the zone total (pipe + fittings + trim)"
    governed["exemption_status"] = "zone total"
    return governed


def pipe_only_screen(screen: dict) -> dict:
    """A screen with no zone total behind it. It never says the size exemption is met.

    The kernel's own flag is kept under its true name. When the pipe alone is
    over the threshold the answer is no. Otherwise there is no answer.
    """
    shown = dict(screen)
    pipe_exempt = bool(screen["nfpa_delivery_time_exempt"])
    shown["pipe_only_volume_gal"] = float(screen["volume_gal"])
    shown["pipe_only_nfpa_delivery_time_exempt"] = pipe_exempt
    shown["nfpa_delivery_time_exempt"] = None if pipe_exempt else False
    shown["exemption_status"] = "not determined" if pipe_exempt else "pipe alone is over the threshold"
    shown["exemption_note"] = EXEMPTION_NOT_DETERMINED if pipe_exempt else EXEMPTION_PIPE_ALREADY_OVER
    return shown


def exemption_answer(screen: dict | None) -> str:
    """yes, no, or not determined: the size exemption as a calc record states it.

    A row from before the screen was handed the zone total carries only the
    kernel's pipe-only flag. That flag is not the exemption, so such a row
    reads not determined unless the pipe alone is already over.
    """
    screen = screen if isinstance(screen, dict) else {}
    if "exemption_volume_gal" in screen:
        return "yes" if screen.get("nfpa_delivery_time_exempt") else "no"
    if screen.get("nfpa_delivery_time_exempt") is False:
        return "no"
    return "not determined"


def exemption_text(volume: dict | None, screen: dict) -> str:
    """One sentence on the size exemption for the narrative, the tile, and the documents.

    It names the volume the answer was judged on, and says so when part of
    that volume is an assumption: the answer then holds only while the real
    trim and fittings keep the zone total at or under the threshold. The
    answer is about the size threshold only; it never says the delivery
    screen passes.
    """
    answer = exemption_answer(screen)
    words = threshold_words(screen)
    if "exemption_volume_gal" not in screen:
        return (f"NFPA size exemption against {words}: {answer}. "
                "This is a pipe-only screen; fittings and trim are not in it.")
    text = (f"NFPA size exemption on the zone total of {fmt1(screen['exemption_volume_gal'])} gal "
            f"against {words}: {answer}.")
    qualifier = exemption_qualifier(volume, screen)
    text = f"{text} {qualifier}" if qualifier else text
    if exemption_basis_text(screen):
        text += " " + exemption_basis_text(screen)
    if screen.get("near_threshold"):
        text += " " + str(screen["near_threshold"])
    return text


def exemption_basis_text(screen: dict | None) -> str:
    """The length basis (and allowance) the screen's zone total was taken on, as its row records it. Empty without one."""
    screen = screen if isinstance(screen, dict) else {}
    basis = screen.get("exemption_length_basis")
    if basis not in ("center_to_center", "cut"):
        return ""
    text = "The zone total was taken on " + ("center-to-center lengths" if basis == "center_to_center" else "cut lengths")
    percent = screen.get("exemption_fittings_percent")
    if isinstance(percent, (int, float)) and not isinstance(percent, bool):
        assumed = any(isinstance(flag, str) and flag.startswith("ASSUMED fittings")
                      for flag in screen.get("exemption_assumptions") or [])
        text += f", fittings {float(percent):g}%" + (" ASSUMED" if assumed else "")
    return text + "."


def exemption_qualifier(volume: dict | None, screen: dict) -> str:
    """What in the zone total behind the exemption is an assumption. Empty when nothing is.

    It carries no figure of its own: the assumed trim and the allowance are
    stated, with their labels, in the sentence on the trapped volume.
    """
    assumed = []
    if isinstance(volume, dict):
        if volume.get("trim_assumed"):
            assumed.append("trim that is ASSUMED")
        if any(isinstance(flag, str) and flag.startswith("ASSUMED fittings") for flag in volume.get("flags") or []):
            assumed.append("a fittings allowance that is ASSUMED")
    if not assumed:
        return ""
    if exemption_answer(screen) == "yes":
        return ("That zone total includes " + " and ".join(assumed) + ", so the answer holds only while the "
                "measured trim and fittings keep the zone total at or under the threshold.")
    return "That zone total includes " + " and ".join(assumed) + "."


def trim_assumption_text(volume: dict) -> str:
    """Say whether trim gallons were typed or filled with the kernel's assumption. The figure is the kernel's."""
    if "trim_gal" not in volume:
        return "Trim was not on this result."
    gallons = fmt1(volume["trim_gal"])
    if volume.get("trim_assumed"):
        return f"{gallons} gal trim ASSUMED (blank trim; the kernel's assumption, no valve data sheet; not calculated)"
    return f"{gallons} gal trim (entered on the form, not assumed)"


def volume_basis_text(volume: dict | None) -> str:
    """The length basis a takeoff used, in words, for beside its fittings percent: "center-to-center, no allowance".

    Read from the zone_trapped_volume row as recorded. An allowance the kernel
    took for a blank one on cut lengths is marked ASSUMED, as its flag says.
    """
    volume = volume if isinstance(volume, dict) else {}
    basis = str(volume.get("length_basis") or "")
    percent = volume.get("fittings_percent")
    number = isinstance(percent, (int, float)) and not isinstance(percent, bool)
    if basis == "center_to_center" and number and float(percent) == 0.0:
        return NO_ALLOWANCE
    words = {"center_to_center": "center-to-center", "cut": "cut lengths"}.get(basis, basis or "length basis not recorded")
    if any(isinstance(flag, str) and flag.startswith("ASSUMED fittings") for flag in volume.get("flags") or []):
        words += ", allowance ASSUMED"
    return words


def allowance_text(volume: dict | None) -> str:
    """The fittings percent and the basis beside it, as every volume line prints them: "0%; center-to-center, no allowance"."""
    volume = volume if isinstance(volume, dict) else {}
    percent = volume.get("fittings_percent")
    shown = f"{float(percent):g}%; " if isinstance(percent, (int, float)) and not isinstance(percent, bool) else ""
    return shown + volume_basis_text(volume)


def friction_note(volume: dict | None) -> str:
    """The friction sentence that goes beside a center-to-center volume with no allowance. Empty otherwise."""
    return FRICTION_NOTE if volume_basis_text(volume) == NO_ALLOWANCE else ""


def cite_note(row: dict | None) -> str:
    """The kernel's note_60s_option, printed as the kernel wrote it, or the withheld-cite words. Empty with none."""
    row = row if isinstance(row, dict) else {}
    note = row.get("note_60s_option")
    return str(note) if isinstance(note, str) and note.strip() else ""


def fill_only(trip: dict | None) -> bool:
    """A delivery row run without every sub-time: the fill time alone and its margin, and no pass or fail."""
    return bool((trip or {}).get("fill_only"))


def screen_verdict(trip: dict | None) -> str:
    """passes, does not pass, or the fill-time-only words. Never a verdict the row does not carry."""
    trip = trip if isinstance(trip, dict) else {}
    if fill_only(trip) or "passes_screen" not in trip:
        return inputs.SUBTIMES_MISSING
    return "passes" if trip["passes_screen"] else "does not pass"


def governing_time(trip: dict | None) -> tuple[str, str] | None:
    """(the row's key, the text) of the delivery time a narrative must quote: t_total, or the fill time alone."""
    trip = trip if isinstance(trip, dict) else {}
    if "t_total_s" in trip:
        return "t_total_s", fmt1(trip["t_total_s"])
    if "t_fill_s" in trip:
        return "t_fill_s", fmt1(trip["t_fill_s"])
    return None


def screen_limit_assumption_text(trip: dict) -> str:
    """The limit seconds are a basis lookup. t_total, or the fill time alone, is the calculated trip time."""
    if "limit_s" not in trip:
        return "Screen limit was not on this result."
    limit = fmt1(trip["limit_s"])
    basis = trip.get("limit_basis") or ""
    if "t_total_s" in trip:
        calculated = f"t_total {fmt1(trip['t_total_s'])} s is calculated."
    elif "t_fill_s" in trip:
        calculated = (f"The fill time alone, {fmt1(trip['t_fill_s'])} s, is calculated; "
                      f"{inputs.SUBTIMES_MISSING}.")
    else:
        return "Screen limit was not on this result."
    if basis == "explicit":
        return (
            f"Screen limit {limit} s is an explicit value, not a calculated delivery time. {calculated}"
        )
    return (
        f"Screen limit {limit} s — ASSUMED from time basis {basis}. "
        f"The limit is a lookup, not calculated. {calculated}"
    )


def lookup_screen_limit(content_root: Path, basis: str) -> dict[str, Any]:
    """Read the screen-limit table from the calc pack. Do not copy the seconds here."""
    if _blank(basis):
        raise ValueError("No time basis is chosen. The screen limit is not looked up until one is.")
    session = ToolSession(content_root)
    table = session.formulas.DI_LIMITS_S
    key = str(basis).strip().upper()
    if key == "NFPA":
        key = "NFPA-OH"
    if key not in table:
        raise ValueError(f"Time basis {basis!r} has no screen limit in the calc pack.")
    return {"limit_s": float(table[key]), "limit_basis": key}


def kernel_default_trim(content_root: Path) -> float | None:
    """The trim the kernel assumes for a blank, when the kernel exports it (DEFAULT_TRIM_GAL). Never written here."""
    try:
        session = ToolSession(content_root)
    except Exception:
        return None
    for module in (session.di, session.formulas):
        value = getattr(module, "DEFAULT_TRIM_GAL", None)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def form_assumption_lines(trim_text: str, basis: str, content_root: Path) -> list[str]:
    """Live form copy: blank trim and the basis lookup are ASSUMED, not calculated."""
    if _blank(trim_text):
        default = kernel_default_trim(content_root)
        figure = f"{default:g} gal, " if default is not None else ""
        trim_line = (f"Trim: ASSUMED ({figure}the kernel's assumption) when Trim gal is blank (no valve data sheet). "
                     "Not calculated.")
    else:
        trim_line = f"Trim: {str(trim_text).strip()} gal entered on the form. Not assumed."
    if _blank(basis):
        # No basis is taken in place of a blank one: the run holds until the designer chooses.
        return [trim_line, "Screen limit: no time basis is chosen. A run holds until one is.", judgment_label_line()]
    limit = lookup_screen_limit(content_root, basis)
    limit_line = (
        f"Screen limit: {fmt1(limit['limit_s'])} s ASSUMED from time basis {limit['limit_basis']}. "
        "This limit is a lookup, not calculated. Trip time is calculated when the zone runs."
    )
    return [trim_line, limit_line, judgment_label_line()]


def govern_note(result: dict | None) -> str:
    """Remind a later chat turn that the tool plan still owns the tables and the docx."""
    if not isinstance(result, dict):
        return ""
    tools = result.get("tools") or {}
    volume = tools.get("zone_trapped_volume") or {}
    trip = tools.get("di_trip_to_water") or {}
    timed = governing_time(trip)
    if "zone_gal" not in volume:
        return ""
    lines = [
        "A tool plan already ran for this zone. Tables and the docx use that plan when a narrative disagrees.",
        f"Governing zone total text: {fmt1(volume['zone_gal'])}.",
    ]
    if timed is not None:
        key, text = timed
        lines.append(f"Governing {'t_total' if key == 't_total_s' else 'fill time (sub-times not provided)'} text: {text}.")
        lines.append(screen_limit_assumption_text(trip))
    lines += [
        trim_assumption_text(volume),
        judgment_label_line(),
        "Do not replace those figures with a number you computed.",
    ]
    if timed is not None:
        lines.append("A delivery time from dry_delivery_screen or di_trip_to_water is an optimistic screen, "
                     "not a listed water-delivery-time calculation.")
    return "\n".join(lines)


def _delivery_lines(volume: dict, screen: dict, trip: dict) -> list[str]:
    """The narrative's lines on the size exemption and the delivery screen, from the rows as recorded."""
    lines = [exemption_text(volume, screen)]
    if str(screen.get("system_type") or "") == "di":
        lines.append("A quick-opening device does not raise the double-interlock exemption threshold.")
    lines.append(screen_limit_assumption_text(trip))
    if fill_only(trip):
        lines.append(
            f"Fill time alone, 60·V/Q: {fmt1(trip['t_fill_s'])} s (calculated); margin to the "
            f"{fmt1(trip['limit_s'])} s limit on the fill time alone: {fmt1(trip['fill_margin_s'])} s. "
            f"{inputs.SUBTIMES_MISSING.capitalize()}."
        )
    else:
        lines.append(f"The zone-total screen {screen_verdict(trip)}.")
        if trip.get("assumed_zero_note"):
            lines.append(str(trip["assumed_zero_note"]))
    lines.append("This screen is not a listed water-delivery-time calculation.")
    # The kernel's own cite (note_60s_option) is printed as it wrote it beside the narrative (the Results tile, the
    # Section body, the Design Basis) and handed to a narrating model, not written into the narrative: a claim
    # check would read it back as a claim of its own.
    return [" ".join(lines)]


def template_narrative(di: dict, tools: dict[str, Any], basis: dict | None = None) -> str:
    volume = tools["zone_trapped_volume"]
    screen = tools.get("dry_delivery_screen")
    trip = tools.get("di_trip_to_water")
    trim = tools["elect_di_trim"]
    truth = tools.get("releasing_truth_table")
    nitrogen = tools.get("nitrogen_gate")
    density = tools.get("density_area")
    hose = tools.get("hose_duration")
    family = trim.get("family") or "unresolved"
    system = str(di.get("system_type") or "")
    kind = {"di": "double-interlock preaction", "dry": "dry pipe", "wet": "wet pipe"}.get(system, system)
    lines = [
        (
            f"Zone {di.get('zone_id') or '(unnumbered)'} {kind}. "
            "Draft for the engineer of record."
        ),
        (
            f"Trapped volume is {fmt1(volume['pipe_gal'])} gal of pipe (calculated), "
            f"{fmt1(volume['fittings_gal'])} gal fittings allowance "
            f"({allowance_text(volume)}), and {trim_assumption_text(volume)}. "
            f"Zone total is {fmt1(volume['zone_gal'])} gal."
        ),
    ]
    if screen is not None and trip is not None:
        lines += _delivery_lines(volume, screen, trip)
    elif system == "wet":
        lines.append(WET_NOTE)
    if system == "dry" and truth is None:
        lines.append(DRY_RELEASING_NOTE)
    lines.append(
        f"Trim family: {family} ({trim['status']}). "
        f"{trim.get('power_loss_behavior') or 'Prime holder is unresolved, so no family is elected.'}"
    )
    if nitrogen is not None:
        sizing = f" {nitrogen['sizing_note']}" if nitrogen.get("sizing_note") else ""
        lines.append(f"Design Hazen-Williams C is {nitrogen['design_c']}. {nitrogen['fill_bases']}{sizing}")
    if truth is not None:
        manual = "on" if truth["manual_station"] else "off"
        lines.append(
            f"{releasing_sentence(truth, trim.get('family'))} Manual station {manual}. "
            f"A second smoke zone does not change the solenoid "
            f"({truth['solenoid_true_count']} true rows of {truth['row_count']})."
        )
    if density is not None and hose is not None:
        # validate_di held the run on a blank hose, so the form's own value is here: a typed 0 is 0.
        user_hose = _float(di.get("hose_gpm"), "Hose")
        demand = (
            f"Demand screen: design area {density['design_area_ft2']:.0f} ft2, "
            f"sprinklers {fmt1(density['q_spr_gpm'])} gpm, "
            f"hose {fmt1(density['hose_gpm'])} gpm, "
            f"total {fmt1(density['qd_gpm'])} gpm. "
            f"Table duration {hose['duration_min']:g} min "
            f"(range {hose['duration_range_min'][0]:g}–{hose['duration_range_min'][1]:g}). "
            f"Designer hose is {user_hose:g} gpm."
        )
        if density.get("release_status"):
            demand += f" {density.get('assumed_note') or ''} {density['release_status']}.".replace("  ", " ")
        lines.append(demand)
    elif system in DELIVERY_SYSTEMS or system == "wet":
        lines.append(NO_DEMAND_NOTE)
    if str((basis or {}).get("hazard_notes") or "").strip():
        lines.append(
            "Hazard notes are a designer judgment the tools did not return. "
            "Label: use best judgment."
        )
    lines.append(judgment_label_line())
    return "\n".join(lines)


def narrative_checks(text: str, tools: dict[str, Any]) -> dict[str, Any]:
    """Whether a draft quotes the governing zone total and the governing delivery time (none on a wet zone)."""
    volume = fmt1(tools["zone_trapped_volume"]["zone_gal"])
    timed = governing_time(tools.get("di_trip_to_water"))
    total = timed[1] if timed is not None else ""
    return {
        "volume": volume,
        "t_total": total,
        "quotes_volume": volume in (text or ""),
        "quotes_time": (total in (text or "")) if total else True,
    }


# The heading run_di_zone used to append when the model draft missed the tool plan.
# Anything after it is rejected prose and is not part of the export.
_REJECTED_DRAFT = "\nModel draft (tables govern if the figures differ):"


def governing_narrative(text: str) -> str:
    """Narrative written beside the tables.

    A model draft that does not quote the tool-plan volume and delivery time
    is not part of this text. The tool-plan narrative stays.
    """
    raw = text or ""
    index = raw.find(_REJECTED_DRAFT)
    if index >= 0:
        raw = raw[:index]
    return raw.strip()


def _flags(di: dict, tools: dict[str, Any], extra: list[str], basis: dict | None = None,
           assumed: Any = ()) -> list[str]:
    flags: list[str] = []
    # First, because it qualifies every cite below it: the calculations name one edition of a standard and
    # the job states another, or the job pins none and the delivery rows' cites are withheld. An edition the
    # designer took from its hint is ASSUMED and not pinned.
    flags.extend(coherence.edition_flags(tools, basis, assumed))
    # Each other input the designer took from its hint: ASSUMED, named, until the designer types a value.
    flags.extend(inputs.assumed_lines(assumed, {**(basis or {}), **di}))
    flags.extend(tools["zone_trapped_volume"].get("flags") or [])
    friction = friction_note(tools["zone_trapped_volume"])
    if friction:
        flags.append(f"Trapped volume is {NO_ALLOWANCE}. {friction}")
    flags.extend(tools["elect_di_trim"].get("flags") or [])
    screen = tools.get("dry_delivery_screen")
    trip = tools.get("di_trip_to_water")
    if screen is not None and trip is not None:
        withheld = trip.get("cites_withheld") or screen.get("cites_withheld")
        if withheld:
            flags.append(f"Delivery rows: {withheld}. The figures ran; no NFPA 13 cite is given for them until the "
                         "job states an edition this calc pack labels.")
        if trip.get("limit_basis") != "explicit" and "limit_s" in trip:
            flags.append(screen_limit_assumption_text(trip))
        if fill_only(trip):
            missing = ", ".join(trip.get("subtimes_missing") or [])
            flags.append(f"Delivery rows: {inputs.SUBTIMES_MISSING} ({missing} blank). The fill time and its margin "
                         "are given, nothing else.")
        elif screen.get("nfpa_delivery_time_exempt") and not trip.get("passes_screen"):
            flags.append(
                "Zone total is inside the NFPA size exemption threshold and the zone-total time screen still misses. "
                "The exemption does not close the insurer time screen."
            )
        elif not trip.get("passes_screen"):
            flags.append("Zone-total delivery screen does not pass.")
        for row in (trip, screen):
            if row.get("assumed_zero_note") and row["assumed_zero_note"] not in flags:
                flags.append(str(row["assumed_zero_note"]))
        if screen.get("near_threshold"):
            flags.append(str(screen["near_threshold"]))
        flags.append("Delivery times are an optimistic screen, not a listed water-delivery-time calculation.")
    elif str(di.get("system_type") or "") == "wet":
        flags.append(WET_NOTE)
    flags.append(judgment_label_line())
    if "hose_duration" in tools and "density_area" in tools:
        user_hose = _float(di.get("hose_gpm"), "Hose")
        table_hose = float(tools["hose_duration"]["hose_total_gpm"])
        if abs(user_hose - table_hose) > 0.01:
            flags.append(
                f"Designer hose {user_hose:g} gpm differs from the table combined hose {table_hose:g} gpm. "
                "Demand uses the designer value."
            )
        density = tools["density_area"]
        if density.get("release_status"):
            flags.append(f"{density.get('assumed_note') or ''} Demand: {density['release_status']}.".strip())
    else:
        flags.append(NO_DEMAND_NOTE)
    if (tools.get("releasing_truth_table") or {}).get("fm_no_cross_zone"):
        flags.append("FM basis: do not cross-zone two smoke detectors to trip the valve.")
    flags.extend(extra)
    return flags


def _user_message(
    content_root: Path,
    di: dict,
    basis: dict,
    tools: dict[str, Any],
    plan_inputs: dict[str, dict],
    mode: str,
) -> str:
    """Ask Claude to quote the tool plan. The plan already ran; its figures govern."""
    known = {item["slug"] for item in list_skills(content_root)}
    present = [slug for slug in DI_SKILL_SLUGS if slug in known]
    known_roles = {item["slug"] for item in list_roles(content_root)}
    present_roles = [slug for slug in SPECIALIST_ROLES if slug in known_roles]
    volume = tools["zone_trapped_volume"]
    trip = tools.get("di_trip_to_water") or {}
    timed = governing_time(trip)
    governing = {
        "zone_gal_text": fmt1(volume["zone_gal"]),
        "t_total_s_text": timed[1] if timed is not None else "",
        "trim": trim_assumption_text(volume),
        "screen_limit": screen_limit_assumption_text(trip) if trip else "No delivery rows ran for this zone.",
    }
    if timed is not None and fill_only(trip):
        governing["delivery"] = (f"Fill time alone {timed[1]} s; {inputs.SUBTIMES_MISSING}. Do not state a pass or a "
                                 "fail, and do not put a time in for a blank one.")
    if cite_note(trip):
        governing["kernel_cite"] = cite_note(trip)
    must = (f"{governing['zone_gal_text']} and {governing['t_total_s_text']}" if governing["t_total_s_text"]
            else governing["zone_gal_text"])
    return (
        "The tool plan on this form already ran in the app. Those figures govern the tables and the export.\n"
        f"Active mode: {mode}. Apply that mode file.\n"
        f"The draft must contain the exact text {must}.\n"
        "Quote the kernel's cite (kernel_cite) as written. Where a cite reads EDITION NOT SET or says its labels "
        "are not in this calc pack, give no section or edition for it.\n"
        "Pipe gallons and t_total are calculated. "
        "If the notes below say ASSUMED for trim or the screen limit, write ASSUMED next to that figure. "
        "Do not describe an ASSUMED value as calculated. "
        "A designer judgment the tools did not return is use best judgment, not ASSUMED and not calculated.\n"
        "Read a listed role with read_role before you answer as that specialist. "
        "Read a listed skill with read_skill when you apply that method. "
        "Read a listed mode with read_mode before you apply a different mode. "
        "You can call several tools in one reply. "
        "If you call a calc tool, use tool_plan_inputs. Do not invent gallons, seconds, gpm, or scfm.\n\n"
        + json.dumps(
            {
                "roles_to_read": present_roles,
                "skills_to_read": present,
                "basis": basis,
                "inputs": di,
                "tool_plan_inputs": plan_inputs,
                "governing": governing,
            },
            indent=2,
            default=str,
        )
    )


Narrator = Callable[[str, str, list, Callable[[str, dict], Any]], dict]


def run_di_zone(
    content_root: Path,
    di: dict,
    basis: dict | None = None,
    narrator: Narrator | None = None,
    mode: str | None = None,
    *,
    record: Record | None = None,
    project_id: str | None = None,
    assumed: Any = (),
) -> dict[str, Any]:
    """Run the fixed tool plan, then the optional narrative.

    With record and project_id, the plan's eight calls are written to that
    job's record as tool-plan, and a narrator's own calls as narrator. A
    repeat run with the same inputs replays the recorded figures. assumed
    names the inputs the designer took from a hint: the run's flags keep an
    ASSUMED edition's HOLD and name every other ASSUMED input.
    """
    basis = dict(basis or {})
    # A zone narration is a draft after the tool plan. The app picks its mode; no menu does.
    selected = normalize_mode(mode or NARRATION_MODE)
    session = ToolSession(content_root, record=record, project_id=project_id, agent="tool-plan")
    narrator_session = ToolSession(content_root, record=record, project_id=project_id, agent="narrator")
    tools, sent = run_tool_plan(session, di, basis, assumed)
    if session.recording:
        record.set_agent(project_id, name="Tool plan", role_slug="tool-plan", status="done")
    template = template_narrative(di, tools, basis)
    transcript = _plan_transcript(tools, sent)
    warnings: list[str] = []
    narrative = template
    source = "tool-plan"
    model = None
    usage = None
    cancelled = False
    known = {item["slug"] for item in list_skills(content_root)}
    missing = [slug for slug in DI_SKILL_SLUGS if slug not in known]
    if missing:
        warnings.append("Content pack is missing skills: " + ", ".join(missing))
    known_roles = {item["slug"] for item in list_roles(content_root)}
    missing_roles = [slug for slug in (EVERYDAY_ROLE, *SPECIALIST_ROLES) if slug not in known_roles]
    if missing_roles:
        warnings.append("Content pack is missing roles: " + ", ".join(missing_roles))
    known_modes = {item["slug"] for item in list_modes(content_root)}
    missing_modes = [slug for slug in MODE_SLUGS if slug not in known_modes]
    if selected not in known_modes and selected not in missing_modes:
        missing_modes.append(selected)
    if missing_modes:
        warnings.append("Content pack is missing modes: " + ", ".join(missing_modes))
    if narrator is not None:
        model = MODEL_ID
        try:
            drafted = narrator(
                system_prompt(content_root, selected),
                _user_message(content_root, di, basis, tools, sent, selected),
                SCHEMAS,
                narrator_session.execute,
            )
            usage = drafted.get("usage")
            unfinished = incomplete_notice(drafted.get("stop_reason"))
            if unfinished:
                warnings.append(unfinished + " Tables stay on the tool plan.")
            for call in drafted.get("tool_calls") or []:
                transcript.append({
                    "name": call.get("name"),
                    "input": call.get("input"),
                    "output": call.get("output"),
                    "is_error": bool(call.get("is_error")),
                    "by": "claude",
                })
            model_text = (drafted.get("text") or "").strip()
            checks = narrative_checks(model_text, tools)
            if model_text and checks["quotes_volume"] and checks["quotes_time"]:
                narrative = model_text
                source = "claude"
            else:
                warnings.append(
                    "The model draft did not quote the tool-plan zone volume and delivery time. "
                    "Tables and the narrative below use the tool plan."
                )
                narrative = template
            have = {call["name"] for call in transcript if call.get("by") == "claude" and not call.get("is_error")}
            # Only the rows this zone runs: a wet zone has no delivery rows and no releasing table.
            skipped = [name for name in REQUIRED_DI_TOOLS if name in tools and name not in have]
            if skipped:
                warnings.append(
                    "Claude did not successfully call: " + ", ".join(skipped) + ". The tool plan still ran them."
                )
        except TurnCancelled as exc:
            # The designer stopped the narration. The tool plan already ran and stands.
            cancelled = True
            usage = getattr(exc, "usage", None)
            warnings.append(NARRATION_CANCELLED)
            source = "tool-plan"
            narrative = template
        except Exception as exc:
            warnings.append("Claude was not used. " + safe_error(exc))
            source = "tool-plan"
            narrative = template
        if narrator_session.recording:
            # The narration's usage closes on the record, so the job's cost can be read back.
            record.log_event(project_id, "narration", {
                "usage": dict(usage or {}), "source": source, "cancelled": cancelled, "kind": "zone",
            }, agent="narrator")
    checks = narrative_checks(narrative, tools)
    return {
        "source": source,
        "model": model,
        "tools": tools,
        "transcript": transcript,
        "narrative": narrative,
        "narrative_checks": checks,
        "warnings": warnings,
        "flags": _flags(di, tools, warnings, basis, assumed),
        "inputs": di,
        "basis": basis,
        # The inputs the designer took from a hint: ASSUMED, as the claim cites name them.
        "assumed": sorted(set(assumed or ())),
        "mode": selected,
        "usage": usage,
        "cancelled": cancelled,
    }


def format_transcript(calls: list[dict]) -> str:
    chunks = []
    for index, call in enumerate(calls, start=1):
        chunks.append(f"{index}. {call.get('name')}  ({call.get('by') or 'tool'})")
        chunks.append("input: " + json.dumps(call.get("input"), default=str))
        # The Results tab is read by the designer: the kernel's deprecated names stay out of it.
        output = json.dumps(reader_view(str(call.get("name") or ""), call.get("output")), default=str)
        if len(output) > 4000:
            output = output[:4000] + " …"
        chunks.append("output: " + output)
        if call.get("is_error"):
            chunks.append("ERROR")
        chunks.append("")
    return "\n".join(chunks).rstrip() + ("\n" if chunks else "")
