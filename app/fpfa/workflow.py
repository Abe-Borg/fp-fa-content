"""Double-interlock zone workflow.

The numbers in the result come from a fixed tool plan on the designer's form.
A Claude narrative is optional. If the model skips a tool, uses different
arguments, or is unreachable, the tables still use this plan.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import REQUIRED_DI_TOOLS, SCHEMAS, ToolSession
from fpfa.claude_client import MODEL_ID, SYSTEM_PROMPT, safe_error
from fpfa.skills_loader import list_skills, spec_notes

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


def fmt1(value: Any) -> str:
    return f"{float(value):.1f}"


def system_prompt(content_root: Path) -> str:
    lines = [SYSTEM_PROMPT, "", "Skills in this content pack:"]
    for skill in list_skills(content_root):
        lines.append(f"- {skill['slug']}: {skill['description']}")
    notes = spec_notes(content_root)
    if notes:
        lines.append("")
        lines.append("Spec notes from the content pack. They are draft language. Verify before issuing.")
        for note in notes:
            lines.append(f"## {note['name']}")
            lines.append(note["text"])
    return "\n".join(lines)


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc


def validate_di(di: dict) -> None:
    segments = di.get("segments") or []
    if not isinstance(segments, list) or not segments:
        raise ValueError("Add at least one pipe segment.")
    for index, segment in enumerate(segments, start=1):
        if _blank(segment.get("length_ft")):
            raise ValueError(f"Segment {index} needs a length in feet.")
        if _blank(segment.get("d_in")) and _blank(segment.get("nps")):
            raise ValueError(f"Segment {index} needs a nominal size or an inside diameter.")
    if _float(di.get("q_fill_gpm"), "Fill flow") <= 0:
        raise ValueError("Fill flow must be greater than 0 gpm.")


def _opt_float(value: Any) -> float | None:
    if _blank(value):
        return None
    return float(value)


def run_tool_plan(session: ToolSession, di: dict, basis: dict) -> tuple[dict[str, Any], dict[str, dict]]:
    """Run the zone tools in order. Later steps use earlier tool outputs.

    The second value is the argument dict actually passed to each tool. The
    transcript and the Claude request advertise that dict, not a shorter copy.
    """
    validate_di(di)
    sent: dict[str, dict] = {}

    def call(name: str, arguments: dict) -> Any:
        sent[name] = arguments
        return session.execute(name, arguments)

    volume = call("zone_trapped_volume", {
        "segments": di.get("segments"),
        "length_basis": di.get("length_basis") or "center_to_center",
        "fittings_percent": _opt_float(di.get("fittings_percent")),
        "trim_gal": _opt_float(di.get("trim_gal")),
    })
    pipe_only = [
        {"d_in": row["d_in"], "length_ft": row["length_ft"]}
        for row in volume["segments"]
    ]
    common_time = {
        "q_fill_gpm": di.get("q_fill_gpm"),
        "t_detect_s": di.get("t_detect_s") or 0,
        "t_release_s": di.get("t_release_s") or 0,
        "t_exhaust_s": di.get("t_exhaust_s") or 0,
        "basis": di.get("delivery_basis") or "FM",
    }
    screen = call("dry_delivery_screen", {
        "segments": pipe_only,
        "qod": bool(di.get("qod")),
        "system_type": di.get("system_type") or "di",
        **common_time,
    })
    # The kernel screen exempts on pipe volume. Capacity gates use the zone total.
    screen = govern_nfpa_exemption(screen, volume["zone_gal"])
    trip = call("di_trip_to_water", {
        "v_gal": volume["zone_gal"],
        **common_time,
    })
    hose = call("hose_duration", {
        "hazard": di.get("hazard") or "ordinary",
        "supervised": bool(di.get("supervised")),
    })
    density = call("density_area", {
        "density_gpm_ft2": di.get("density_gpm_ft2"),
        "base_area_ft2": di.get("base_area_ft2"),
        "area_increase": di.get("area_increase") or 0,
        "hose_gpm": di.get("hose_gpm") or 0,
        "duration_min": hose["duration_min"],
    })
    nitrogen = call("nitrogen_gate", {
        "v_gal": volume["zone_gal"],
        "p_psig": di.get("supervisory_psig") or 40,
        "t_min": di.get("fill_minutes") or 30,
    })
    trim = call("elect_di_trim", {
        "system_type": di.get("system_type") or "di",
        "prime_held_by": di.get("prime_held_by") or "unknown",
        "failsafe_on_total_power_loss": bool(di.get("failsafe_on_total_power_loss")),
        "supervisory_psi": _opt_float(di.get("supervisory_psi")),
        "medium": di.get("medium") or "unelected",
        "insurer": (basis or {}).get("insurer") or "",
    })
    truth = call("releasing_truth_table", {
        "manual_station": bool(di.get("manual_station", True)),
        "insurer": (basis or {}).get("insurer") or "FM",
    })
    tools = {
        "zone_trapped_volume": volume,
        "dry_delivery_screen": screen,
        "di_trip_to_water": trip,
        "hose_duration": hose,
        "density_area": density,
        "nitrogen_gate": nitrogen,
        "elect_di_trim": trim,
        "releasing_truth_table": truth,
    }
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


def govern_nfpa_exemption(screen: dict, zone_gal: float) -> dict:
    """Size exemption follows the zone total (pipe + fittings + trim).

    ``dry_delivery_screen`` reports the exemption on pipe volume. Timing for that
    pipe-only screen stays. ``nfpa_delivery_time_exempt`` becomes the zone-total
    check against the same cap, including the double-interlock rule that a
    quick-opening device does not raise the 500 gal cap.
    """
    governed = dict(screen)
    cap = float(screen["nfpa_size_cap_gal"])
    governed["pipe_only_volume_gal"] = float(screen["volume_gal"])
    governed["pipe_only_nfpa_delivery_time_exempt"] = bool(screen["nfpa_delivery_time_exempt"])
    governed["exemption_volume_gal"] = float(zone_gal)
    governed["nfpa_delivery_time_exempt"] = float(zone_gal) <= cap + 1e-9
    return governed


def trim_assumption_text(volume: dict) -> str:
    """Say whether trim gallons were typed or filled with the 5 gal assumption."""
    if "trim_gal" not in volume:
        return "Trim was not on this result."
    gallons = fmt1(volume["trim_gal"])
    if volume.get("trim_assumed"):
        return (
            f"{gallons} gal trim ASSUMED (blank trim; 5 gal, no valve data sheet; not calculated)"
        )
    return f"{gallons} gal trim (entered on the form, not assumed)"


def screen_limit_assumption_text(trip: dict) -> str:
    """The limit seconds are a basis lookup. t_total is the calculated trip time."""
    if "limit_s" not in trip or "t_total_s" not in trip:
        return "Screen limit was not on this result."
    limit = fmt1(trip["limit_s"])
    total = fmt1(trip["t_total_s"])
    basis = trip.get("limit_basis") or ""
    calculated = f"t_total {total} s is calculated."
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
    session = ToolSession(content_root)
    table = session.formulas.DI_LIMITS_S
    key = str(basis or "FM").strip().upper()
    if key == "NFPA":
        key = "NFPA-OH"
    if key not in table:
        raise ValueError(f"Time basis {basis!r} has no screen limit in the calc pack.")
    return {"limit_s": float(table[key]), "limit_basis": key}


def form_assumption_lines(trim_text: str, basis: str, content_root: Path) -> list[str]:
    """Live form copy: blank trim and the basis lookup are ASSUMED, not calculated."""
    if _blank(trim_text):
        trim_line = "Trim: ASSUMED 5 gal when Trim gal is blank (no valve data sheet). Not calculated."
    else:
        trim_line = f"Trim: {str(trim_text).strip()} gal entered on the form. Not assumed."
    limit = lookup_screen_limit(content_root, basis)
    limit_line = (
        f"Screen limit: {fmt1(limit['limit_s'])} s ASSUMED from time basis {limit['limit_basis']}. "
        "This limit is a lookup, not calculated. Trip time is calculated when the zone runs."
    )
    return [trim_line, limit_line]


def template_narrative(di: dict, tools: dict[str, Any]) -> str:
    volume = tools["zone_trapped_volume"]
    screen = tools["dry_delivery_screen"]
    trip = tools["di_trip_to_water"]
    trim = tools["elect_di_trim"]
    truth = tools["releasing_truth_table"]
    nitrogen = tools["nitrogen_gate"]
    density = tools["density_area"]
    hose = tools["hose_duration"]
    exempt = "yes" if screen["nfpa_delivery_time_exempt"] else "no"
    screen_word = "passes" if trip["passes_screen"] else "does not pass"
    family = trim.get("family") or "unresolved"
    manual = "on" if truth["manual_station"] else "off"
    user_hose = _float(di.get("hose_gpm") or 0, "Hose")
    return "\n".join([
        (
            f"Zone {di.get('zone_id') or '(unnumbered)'} double-interlock preaction. "
            "Draft for the engineer of record."
        ),
        (
            f"Trapped volume is {fmt1(volume['pipe_gal'])} gal of pipe, "
            f"{fmt1(volume['fittings_gal'])} gal fittings allowance "
            f"({volume['fittings_percent']:g}%), and {trim_assumption_text(volume)}. "
            f"Zone total is {fmt1(volume['zone_gal'])} gal."
        ),
        (
            f"NFPA size exemption on the zone total of {fmt1(volume['zone_gal'])} gal "
            f"against the {screen['nfpa_size_cap_gal']:.0f} gal cap: {exempt}. "
            "A quick-opening device does not raise the double-interlock cap. "
            f"{screen_limit_assumption_text(trip)} "
            f"The zone-total screen {screen_word}. "
            "This screen is not a listed water-delivery-time calculation."
        ),
        (
            f"Trim family: {family} ({trim['status']}). "
            f"{trim.get('power_loss_behavior') or 'Prime holder is unresolved, so no family is elected.'}"
        ),
        (
            f"Design Hazen-Williams C is {nitrogen['design_c']}. "
            f"Gauge-basis fill rate is {nitrogen['scfm_gauge_basis']:.2f} scfm."
        ),
        (
            f"Releasing: {truth['boolean']}. Manual station {manual}. "
            f"A second smoke zone does not change the solenoid "
            f"({truth['solenoid_true_count']} true rows of {truth['row_count']})."
        ),
        (
            f"Demand screen: design area {density['design_area_ft2']:.0f} ft2, "
            f"sprinklers {fmt1(density['q_spr_gpm'])} gpm, "
            f"hose {fmt1(density['hose_gpm'])} gpm, "
            f"total {fmt1(density['qd_gpm'])} gpm. "
            f"Table duration {hose['duration_min']:g} min "
            f"(range {hose['duration_range_min'][0]:g}–{hose['duration_range_min'][1]:g}). "
            f"Designer hose is {user_hose:g} gpm."
        ),
    ])


def narrative_checks(text: str, tools: dict[str, Any]) -> dict[str, Any]:
    volume = fmt1(tools["zone_trapped_volume"]["zone_gal"])
    total = fmt1(tools["di_trip_to_water"]["t_total_s"])
    return {
        "volume": volume,
        "t_total": total,
        "quotes_volume": volume in (text or ""),
        "quotes_time": total in (text or ""),
    }


def _flags(di: dict, tools: dict[str, Any], extra: list[str]) -> list[str]:
    flags: list[str] = []
    flags.extend(tools["zone_trapped_volume"].get("flags") or [])
    flags.extend(tools["elect_di_trim"].get("flags") or [])
    screen = tools["dry_delivery_screen"]
    trip = tools["di_trip_to_water"]
    if trip.get("limit_basis") != "explicit" and "limit_s" in trip:
        flags.append(screen_limit_assumption_text(trip))
    if screen["nfpa_delivery_time_exempt"] and not trip["passes_screen"]:
        flags.append(
            "Zone total is inside the NFPA size cap and the zone-total time screen still misses. "
            "The cap does not close the insurer time screen."
        )
    elif not trip["passes_screen"]:
        flags.append("Zone-total delivery screen does not pass.")
    flags.append("Delivery times are an optimistic screen, not a listed water-delivery-time calculation.")
    user_hose = float(di.get("hose_gpm") or 0)
    table_hose = float(tools["hose_duration"]["hose_total_gpm"])
    if abs(user_hose - table_hose) > 0.01:
        flags.append(
            f"Designer hose {user_hose:g} gpm differs from the table combined hose {table_hose:g} gpm. "
            "Demand uses the designer value."
        )
    if tools["releasing_truth_table"].get("fm_no_cross_zone"):
        flags.append("FM basis: do not cross-zone two smoke detectors to trip the valve.")
    flags.extend(extra)
    return flags


def _user_message(
    content_root: Path,
    di: dict,
    basis: dict,
    tools: dict[str, Any],
    plan_inputs: dict[str, dict],
) -> str:
    """Ask Claude to quote the tool plan. The plan already ran; its figures govern."""
    known = {item["slug"] for item in list_skills(content_root)}
    present = [slug for slug in DI_SKILL_SLUGS if slug in known]
    volume = tools["zone_trapped_volume"]
    trip = tools["di_trip_to_water"]
    governing = {
        "zone_gal_text": fmt1(volume["zone_gal"]),
        "t_total_s_text": fmt1(trip["t_total_s"]),
        "trim": trim_assumption_text(volume),
        "screen_limit": screen_limit_assumption_text(trip),
    }
    return (
        "The tool plan on this form already ran in the app. Those figures govern the tables and the export.\n"
        f"The draft must contain the exact text {governing['zone_gal_text']} and {governing['t_total_s_text']}.\n"
        "Pipe gallons and t_total are calculated. "
        "If the notes below say ASSUMED for trim or the screen limit, write ASSUMED next to that figure. "
        "Do not describe an ASSUMED value as calculated.\n"
        "Read a listed skill with read_skill when you apply that method. "
        "You can call several tools in one reply. "
        "If you call a calc tool, use tool_plan_inputs. Do not invent gallons, seconds, gpm, or scfm.\n\n"
        + json.dumps(
            {
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
) -> dict[str, Any]:
    basis = dict(basis or {})
    session = ToolSession(content_root)
    tools, sent = run_tool_plan(session, di, basis)
    template = template_narrative(di, tools)
    transcript = _plan_transcript(tools, sent)
    warnings: list[str] = []
    narrative = template
    source = "tool-plan"
    model = None
    known = {item["slug"] for item in list_skills(content_root)}
    missing = [slug for slug in DI_SKILL_SLUGS if slug not in known]
    if missing:
        warnings.append("Content pack is missing skills: " + ", ".join(missing))
    if narrator is not None:
        model = MODEL_ID
        try:
            drafted = narrator(
                system_prompt(content_root),
                _user_message(content_root, di, basis, tools, sent),
                SCHEMAS,
                session.execute,
            )
            if drafted.get("stop_reason") == "max_tokens":
                warnings.append(
                    "Claude stopped because the reply hit the output limit. Tables stay on the tool plan."
                )
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
                if model_text:
                    narrative = template + "\n\nModel draft (tables govern if the figures differ):\n" + model_text
            have = {call["name"] for call in transcript if call.get("by") == "claude" and not call.get("is_error")}
            skipped = [name for name in REQUIRED_DI_TOOLS if name not in have]
            if skipped:
                warnings.append(
                    "Claude did not successfully call: " + ", ".join(skipped) + ". The tool plan still ran them."
                )
        except Exception as exc:
            warnings.append("Claude was not used. " + safe_error(exc))
            source = "tool-plan"
            narrative = template
    checks = narrative_checks(narrative, tools)
    return {
        "source": source,
        "model": model,
        "tools": tools,
        "transcript": transcript,
        "narrative": narrative,
        "narrative_checks": checks,
        "warnings": warnings,
        "flags": _flags(di, tools, warnings),
        "inputs": di,
        "basis": basis,
    }


def format_transcript(calls: list[dict]) -> str:
    chunks = []
    for index, call in enumerate(calls, start=1):
        chunks.append(f"{index}. {call.get('name')}  ({call.get('by') or 'tool'})")
        chunks.append("input: " + json.dumps(call.get("input"), default=str))
        output = json.dumps(call.get("output"), default=str)
        if len(output) > 4000:
            output = output[:4000] + " …"
        chunks.append("output: " + output)
        if call.get("is_error"):
            chunks.append("ERROR")
        chunks.append("")
    return "\n".join(chunks).rstrip() + ("\n" if chunks else "")
