"""The Results tab. A saved run laid out as the figures a designer looks for first.

results_view() turns a run's result into what the page draws: the headline
figures with the label each one carries, the lines that say what is ASSUMED,
the narrative, the flags, and the tool transcript.

Nothing here is computed. Every number is a field of a calc tool's output,
printed with the same rounding and the same words the narrative uses
(fpfa.workflow), so the tiles, the thread, and the exports cannot disagree.
The three labels stay distinct: pipe gallons and t_total are calculated, a
blank trim and the screen-limit lookup are ASSUMED, and what the tools did
not return is use best judgment. A delivery time is an optimistic screen,
not a listed water-delivery-time calculation, and the view says so.

The view holds no state. Desk keeps the plain text of a run (results_text)
beside it for the thread and the tests that read it.
"""

from __future__ import annotations

from typing import Any

from fpfa.claude_client import MODEL_ID
from fpfa.releasing import TRUTH_TABLE_TOOL, releasing_logic
from fpfa.workflow import (
    allowance_text,
    cite_note,
    exemption_answer,
    exemption_basis_text,
    exemption_qualifier,
    fill_only,
    fmt1,
    friction_note,
    format_transcript,
    judgment_label_line,
    screen_limit_assumption_text,
    threshold_gal,
    threshold_words,
    trim_assumption_text,
)
from fpfa.inputs import SUBTIMES_MISSING

CALCULATED = "calculated"
ASSUMED = "ASSUMED"
SCREEN_NOTE = "Delivery times are an optimistic screen, not a listed water-delivery-time calculation."
NO_RUN_TITLE = "No zone run on this job yet"
NO_RUN_LINES = (
    "Fill in the Inputs tab and press Run zone, or type /run.",
    "The run is posted in the thread, and its figures stay here for the exports.",
)


def empty_view() -> dict:
    """What the tab shows before any run: a title and what to do next."""
    return {"kind": "", "run": "", "title": NO_RUN_TITLE, "lines": list(NO_RUN_LINES)}


def _figure(key: str, title: str, value: str, unit: str = "", *, label: str = "", tone: str = "",
            verdict: str = "", code: str = "", lines: list[str] | None = None) -> dict:
    """One tile. value may be empty: a figure the kernel returns on two bases has no one headline number."""
    return {"key": key, "title": title, "value": value, "unit": unit, "label": label, "tone": tone,
            "verdict": verdict, "code": code, "lines": [line for line in (lines or []) if line]}


def _source_line(result: dict, with_model: str, alone: str) -> str:
    """Who wrote the narrative, in the words the plain text of the run uses."""
    if (result.get("source") or "tool-plan") == "claude":
        return f"Narrative from {result.get('model') or MODEL_ID}. {with_model}"
    return alone


def _cite_line(row: dict) -> str:
    """The kernel's own cite for a delivery row, as it wrote it, or the words that say it is withheld."""
    note = cite_note(row)
    return f"Kernel cite: {note}" if note else ""


def zone_figures(tools: dict[str, Any]) -> list[dict]:
    """The zone run's headline figures, each printed the way template_narrative prints it."""
    volume = tools.get("zone_trapped_volume") or {}
    screen = tools.get("dry_delivery_screen") or {}
    trip = tools.get("di_trip_to_water") or {}
    density = tools.get("density_area") or {}
    hose = tools.get("hose_duration") or {}
    trim = tools.get("elect_di_trim") or {}
    nitrogen = tools.get("nitrogen_gate") or {}
    truth = tools.get(TRUTH_TABLE_TOOL) or {}
    figures: list[dict] = []

    if "zone_gal" in volume:
        lines = []
        if "pipe_gal" in volume:
            lines.append(f"{fmt1(volume['pipe_gal'])} gal of pipe ({CALCULATED})")
        if "fittings_gal" in volume:
            # The basis beside the allowance, not only in the flags: "0%; center-to-center, no allowance".
            lines.append(f"{fmt1(volume['fittings_gal'])} gal fittings allowance ({allowance_text(volume)})")
            if friction_note(volume):
                lines.append(friction_note(volume))
        lines.append(trim_assumption_text(volume))
        figures.append(_figure(
            "zone_total", "Zone total", fmt1(volume["zone_gal"]), "gal",
            label=f"{CALCULATED}, trim {ASSUMED}" if volume.get("trim_assumed") else CALCULATED, lines=lines,
        ))

    if "t_total_s" in trip:
        passes = bool(trip.get("passes_screen"))
        lines = []
        if "t_fill_s" in trip:
            # The tool's own part of t_total that is the water alone, and its margin, beside the verdict: the
            # acceptance run's team called a screen independent of its assumed times when the fill time alone
            # was inside the limit (F-006). Printed as the tool returned them; nothing is worked out here.
            lines.append(f"Fill time alone, 60·V/Q: {fmt1(trip['t_fill_s'])} s ({CALCULATED}). The detection, "
                         "releasing, and exhaust times on the inputs are added to it.")
        if "margin_s" in trip and "limit_s" in trip:
            lines.append(f"Margin to the {fmt1(trip['limit_s'])} s limit: {fmt1(trip['margin_s'])} s.")
        if trip.get("assumed_zero_note"):
            lines.append(str(trip["assumed_zero_note"]))
        lines += [screen_limit_assumption_text(trip), SCREEN_NOTE, _cite_line(trip)]
        figures.append(_figure(
            "t_total", "Delivery screen, t_total", fmt1(trip["t_total_s"]), "s", label=CALCULATED,
            tone="ok" if passes else "warn",
            verdict="The zone-total screen passes." if passes else "The zone-total screen does not pass.",
            lines=lines,
        ))
    elif fill_only(trip) and "t_fill_s" in trip:
        # A sub-time was blank: the fill time alone and its margin, and no verdict of any kind.
        lines = []
        if "fill_margin_s" in trip and "limit_s" in trip:
            lines.append(f"Margin to the {fmt1(trip['limit_s'])} s limit on the fill time alone: "
                         f"{fmt1(trip['fill_margin_s'])} s.")
        lines += [screen_limit_assumption_text(trip), SCREEN_NOTE, _cite_line(trip)]
        figures.append(_figure(
            "t_fill", "Delivery screen, fill time only", fmt1(trip["t_fill_s"]), "s", label=CALCULATED,
            tone="warn", verdict=SUBTIMES_MISSING.capitalize() + ".", lines=lines,
        ))

    if "nfpa_delivery_time_exempt" in screen and threshold_gal(screen) is not None and "zone_gal" in volume:
        # The tool's own answer. A saved run from before the screen was handed the zone total was governed
        # on it in memory and carries the same keys; a pipe-only result has no answer to print. The answer is
        # about the size threshold only: it never says the delivery screen passes.
        answer = exemption_answer(screen)
        judged_on = screen.get("exemption_volume_gal")
        lines = [
            f"Zone total of {fmt1(judged_on)} gal against {threshold_words(screen)}."
            if judged_on is not None else "Pipe-only screen. Fittings and trim are not in it.",
        ]
        if judged_on is not None and exemption_basis_text(screen):
            # Which basis the screen's zone total was taken on, as the screen's own row says.
            lines.append(exemption_basis_text(screen))
        qualifier = exemption_qualifier(volume, screen) if judged_on is not None else ""
        if qualifier:
            lines.append(qualifier)
        if screen.get("near_threshold"):
            lines.append(str(screen["near_threshold"]))
        if str(screen.get("system_type") or "") == "di":
            lines.append("A quick-opening device does not raise the double-interlock exemption threshold.")
        figures.append(_figure(
            "size_exemption", "NFPA size exemption", answer, "",
            tone="warn" if answer == "not determined" or screen.get("near_threshold") else "", lines=lines,
        ))

    if "qd_gpm" in density:
        lines = []
        if "design_area_ft2" in density:
            lines.append(f"Design area {density['design_area_ft2']:.0f} ft2")
        if "q_spr_gpm" in density and "hose_gpm" in density:
            lines.append(f"Sprinklers {fmt1(density['q_spr_gpm'])} gpm, hose {fmt1(density['hose_gpm'])} gpm")
        span = hose.get("duration_range_min")
        if "duration_min" in hose:
            around = f" (range {span[0]:g}–{span[1]:g})" if isinstance(span, (list, tuple)) and len(span) == 2 else ""
            lines.append(f"Table duration {hose['duration_min']:g} min{around}")
        if hose.get("basis"):
            lines.append(str(hose["basis"]))
        label = CALCULATED
        if density.get("release_status"):
            # Built on an ASSUMED density or area: the label, the reason, and that it is not for release.
            label = f"{CALCULATED}, {ASSUMED} input"
            lines += [str(density.get("assumed_note") or ""), str(density["release_status"])]
        figures.append(_figure("demand", "Demand screen", fmt1(density["qd_gpm"]), "gpm", label=label,
                               tone="warn" if density.get("release_status") else "", lines=lines))

    if trim:
        family = str(trim.get("family") or "unresolved")
        figures.append(_figure(
            "trim", "Trim family", family, "", label=str(trim.get("status") or ""),
            lines=[str(trim.get("power_loss_behavior") or "Prime holder is unresolved, so no family is elected.")],
        ))

    if nitrogen.get("fill_bases"):
        # The kernel returns a gauge-basis and an absolute-basis rate and elects neither, so no one
        # number is the headline here.
        lines = [str(nitrogen["fill_bases"])]
        if nitrogen.get("sizing_note"):
            lines.append(str(nitrogen["sizing_note"]))
        if "design_c" in nitrogen:
            lines.append(f"Design Hazen-Williams C is {nitrogen['design_c']}.")
        figures.append(_figure("gas_fill", "Supervisory gas fill", "", "", label=CALCULATED, lines=lines))

    if truth:
        logic = releasing_logic(truth)
        lines = []
        family = str(trim.get("family") or "").strip()
        if family and family != "El/El":
            lines.append(
                f"The elected trim family is {family}. The truth table is the electric/electric reference, "
                "not this valve's logic."
            )
        lines += [logic["second_leg"], logic["supervisory"]]
        if "solenoid_true_count" in truth and "row_count" in truth:
            lines.append(
                f"A second smoke zone does not change the solenoid "
                f"({truth['solenoid_true_count']} true rows of {truth['row_count']})."
            )
        figures.append(_figure("releasing", "Releasing logic", "", "", code=logic["expression"], lines=lines))
    return figures


def results_view(result: dict | None) -> dict:
    """What the Results tab draws for one saved run. The empty view when there is none."""
    if not isinstance(result, dict) or not isinstance(result.get("tools"), dict):
        return empty_view()
    tools = result["tools"]
    kind = "bess" if result.get("kind") == "bess" else "zone"
    view: dict[str, Any] = {
        "kind": kind,
        # Which run this is. The page shows the tab when a new one lands on the open job.
        "run": str(result.get("job_id") or ""),
        "heading": str(result.get("job_heading") or ""),
        "narrative": str(result.get("narrative") or ""),
        "flags": [str(flag) for flag in result.get("flags") or []],
        "warnings": [str(item) for item in result.get("warnings") or []],
        "transcript": format_transcript(result.get("transcript") or []),
    }
    if kind == "bess":
        view.update({
            "title": "Explosion-control starter",
            "source": _source_line(result, "The LFL tool plan governs.", "Narrative from the LFL tool plan."),
            "figures": [],
            "governing": [str(text) for text in (result.get("governing") or {}).get("texts") or []],
            "notes": [
                "vol% and ppm come from the LFL tool.",
                f"An election or a duration the tool did not return is {ASSUMED}.",
                "Zone gallons and seconds stay on the zone tool plan when one has run.",
            ],
        })
        return view
    volume = tools.get("zone_trapped_volume") or {}
    trip = tools.get("di_trip_to_water") or {}
    view.update({
        "title": "Zone tool plan",
        "source": _source_line(result, "Tables use the tool plan.", "Narrative from the tool plan."),
        "figures": zone_figures(tools),
        "governing": [],
        "notes": [trim_assumption_text(volume)] + ([screen_limit_assumption_text(trip)] if trip else [])
                 + [judgment_label_line()],
    })
    return view
