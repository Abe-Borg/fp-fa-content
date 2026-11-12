"""Draft specification section. Every figure is copied from the tool-plan JSON.

Double-interlock preaction is CSI Section 21 13 19. Dry pipe is a different section
and is not this export.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document

from fpfa import inputs
from fpfa.workflow import (
    allowance_text,
    cite_note,
    exemption_answer,
    exemption_qualifier,
    fill_only,
    fmt1,
    friction_note,
    governing_narrative,
    judgment_label_line,
    releasing_sentence,
    screen_limit_assumption_text,
    screen_verdict,
    second_leg_value,
    threshold_gal,
    threshold_words,
    trim_assumption_text,
)

DRAFT_SECTION = "21 13 19"
DRAFT_HEADING = "Section 21 13 19 — Double-interlock preaction (draft)"
# The pipe-only row is a lower bound: it is never the screen a verdict is read from.
PIPE_ONLY_VERDICT = "—"
PIPE_ONLY_NOTE = "lower bound, not the governing screen"


EDITION_EXPORT_HOLD = (
    "HOLD: NFPA 13 " + inputs.EDITION_NOT_PINNED + ". The delivery rows ran with their cites withheld "
    "(EDITION NOT SET — cites withheld, VERIFY), so {document} is not exported. Type the job's NFPA 13 edition on "
    "the Inputs tab and run the zone again."
)
# An edition the job pins and the calc pack holds no labels for (2022 and 2024 today): the rows ran with their cites
# withheld, and a section with no cites is not issued.
EDITION_NOT_HELD_HOLD = (
    "HOLD: {why}. The delivery rows ran with every NFPA 13 cite withheld, so {document} is not exported until the "
    "calc pack labels that edition."
)
SECTION_HOLD_HEAD = "Section {section} is not exported. Each of these holds it:"


def _form_name(name: str) -> str:
    label = inputs.FORM_LABELS.get(name, (name, ""))[0]
    return f"{label} ({name})" if label != name else name


def section_problem(result: dict | None, project: dict | None = None, assumed: Any = ()) -> str:
    """Why a run cannot be written as Section 21 13 19, or "". The section is double-interlock only.

    Dry pipe is a different section and a wet zone has no delivery rows,
    so neither is written here. Otherwise every hold is named at once:

    - an NFPA 13 edition that is not pinned (blank, or ASSUMED from its hint),
      or one the delivery rows ran on with their cites withheld (an edition the
      calc pack holds no labels for);
    - an NFPA 72 edition that is not pinned: the section specifies the
      detection and releasing;
    - every input the run used that is ASSUMED (a hint the designer used, or a
      value the record labels ASSUMED), named;
    - an insurer that is blank or ASSUMED (an earlier form's starting value on
      an older job is marked in the basis line, as before, not held);
    - a row built on an ASSUMED input (its release_status).

    assumed names further inputs the record labels ASSUMED (the desk reads them
    from the record); the run's own and the job's accepted hints are read here.
    """
    result = result if isinstance(result, dict) else {}
    basis = result.get("basis") if isinstance(result.get("basis"), dict) else (project or {}).get("basis") or {}
    tools = result.get("tools") if isinstance(result.get("tools"), dict) else {}
    system = str((result.get("inputs") or {}).get("system_type") or "")
    if system != "di" or "dry_delivery_screen" not in tools or "di_trip_to_water" not in tools:
        named = {"dry": "a dry-pipe zone, which is a section of its own", "wet": "a wet zone"}.get(system, "this zone")
        return (f"Section {DRAFT_SECTION} is double-interlock preaction. This run is {named}, so it is not written "
                "as this section.")
    taken = set(inputs.accepted_inputs(project) if project is not None else set())
    taken |= set(result.get("assumed") or ()) | set(assumed or ())
    document = f"Section {DRAFT_SECTION}"
    holds: list[str] = []
    # The job's edition as it stands, and the edition the run's own rows ran on: a run made before the designer
    # typed the edition still has its cites withheld, and is run again first.
    rows = [row for row in tools.values() if isinstance(row, dict)]
    unset = any(row.get("edition_status") == "not set" for row in rows)
    unpinned = inputs.unpinned_editions(basis, taken)
    if "NFPA 13" in unpinned or unset:
        holds.append(EDITION_EXPORT_HOLD.format(document=document))
    else:
        withheld = next((row for row in rows if row.get("edition_status") == "not held"), None)
        if withheld is not None:
            holds.append(EDITION_NOT_HELD_HOLD.format(why=withheld.get("cites_withheld") or "cites withheld",
                                                      document=document))
    if "NFPA 72" in unpinned:
        holds.append(f"HOLD: NFPA 72 {inputs.EDITION_NOT_PINNED}. The section specifies the detection and releasing, "
                     "so it is not issued until the designer types the job's NFPA 72 edition.")
    editions = {field for field, _document in inputs.EDITION_FIELDS}
    values = {**basis, **(result.get("inputs") or {})}
    for name in sorted(taken - editions - {"insurer"},
                       key=lambda item: inputs.INPUT_NAMES.index(item) if item in inputs.INPUT_NAMES else 999):
        shown = inputs.show(name, values[name]) if name in values else "its value"
        holds.append(f"{_form_name(name)} is ASSUMED ({shown}): type the job's own value.")
    insurer = str(basis.get("insurer") or "").strip()
    if not insurer:
        holds.append("Insurer (insurer) is blank: type the job's insurer.")
    elif "insurer" in taken:
        holds.append(f"Insurer (insurer) is ASSUMED ({insurer}): type the job's insurer.")
    for name, row in tools.items():
        if isinstance(row, dict) and row.get("release_status"):
            holds.append(f"The {name} row is built on an ASSUMED input: {row['release_status']}.")
    if not holds:
        return ""
    if len(holds) == 1 and holds[0].startswith("HOLD: NFPA 13"):
        return holds[0]
    return " ".join([SECTION_HOLD_HEAD.format(section=DRAFT_SECTION)] + [f"({n}) {text}" for n, text in
                                                                         enumerate(holds, start=1)]
                    + ["Run the zone again once each is settled."])


def _yn(value) -> str:
    return "Yes" if value else "No"


def _limit_cell(row: dict) -> str:
    text = fmt1(row["limit_s"])
    if row.get("limit_basis") != "explicit":
        return f"{text} ASSUMED"
    return text


def basis_line(project: dict, basis: dict) -> str:
    """The basis fields as the section prints them. A starting value nobody stated is marked as one.

    The run's basis is read against the job's own note of who supplied each
    field (inputs.provenance): the export is written only while the form
    still holds the values the run used.
    """
    unconfirmed = set(inputs.unconfirmed_basis(project, basis))
    # A hint the designer used is ASSUMED, and an edition that is ASSUMED or blank is not pinned.
    assumed = inputs.accepted_inputs(project) & set(inputs.BASIS_FIELDS)
    editions = {name for name, _document in inputs.EDITION_FIELDS}

    def field(name: str) -> str:
        raw = str(basis.get(name) or "").strip()
        value = raw or "—"
        if raw and name in unconfirmed:
            return f"{value} {inputs.UNCONFIRMED_NOTE}"
        if raw and name in assumed:
            pinned = f"; {inputs.EDITION_NOT_PINNED}" if name in editions else ""
            return f"{value} (ASSUMED, a hint the designer used{pinned})"
        if not raw and name in editions:
            return f"{value} ({inputs.EDITION_NOT_PINNED})"
        return value

    line = (f"AHJ: {field('ahj')}. NFPA 13: {field('nfpa_13')}. "
            f"NFPA 72: {field('nfpa_72')}. Insurer: {field('insurer')}.")
    if unconfirmed:
        line += (" A starting value is the job form's own; the designer did not state it. "
                 "Confirm it before this section is relied on.")
    if assumed & {name for name in inputs.BASIS_FIELDS if str(basis.get(name) or "").strip()}:
        line += " An ASSUMED value is a hint the designer used, not a design value. Confirm it before this section is relied on."
    return line


def _table(doc: Document, headers: list[str], rows: list[list]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        table.rows[0].cells[index].text = header
    for r_index, row in enumerate(rows, start=1):
        for c_index, value in enumerate(row):
            table.rows[r_index].cells[c_index].text = "" if value is None else str(value)


def write_docx(path: Path | str, project: dict, result: dict, assumed: Any = ()) -> Path:
    problem = section_problem(result, project, assumed)
    if problem:
        raise ValueError(problem)
    path = Path(path)
    tools = result["tools"]
    volume = tools["zone_trapped_volume"]
    screen = tools["dry_delivery_screen"]
    trip = tools["di_trip_to_water"]
    trim = tools["elect_di_trim"]
    truth = tools["releasing_truth_table"]
    nitrogen = tools["nitrogen_gate"]
    density = tools.get("density_area")
    hose = tools.get("hose_duration")
    if result.get("basis") is not None:
        basis = result["basis"]
    else:
        basis = project.get("basis") or {}
    di = result.get("inputs") or project.get("di") or {}

    doc = Document()
    doc.core_properties.title = DRAFT_HEADING
    doc.core_properties.subject = f"Draft Section {DRAFT_SECTION} double-interlock preaction"
    doc.add_heading(DRAFT_HEADING, level=1)
    doc.add_paragraph(
        f"Draft Section {DRAFT_SECTION} for review. Verify with the engineer of record. "
        "The delivery times in this section are an optimistic screen from the trapped volume "
        "and an assumed fill flow. They are not a listed water-delivery-time calculation. "
        "Figures marked ASSUMED were not calculated from the zone. "
        "Pipe gallons and t_total are calculated."
    )
    doc.add_paragraph(judgment_label_line())
    doc.add_paragraph(
        f"Project: {project.get('name') or 'Untitled job'}. "
        f"Zone: {di.get('zone_id') or '—'}. "
        f"Narrative source: {result.get('source') or 'tool-plan'}."
    )

    doc.add_heading("Basis of design", level=2)
    doc.add_paragraph("Recorded with this calculation.")
    doc.add_paragraph(basis_line(project, basis))
    if basis.get("hazard_notes"):
        doc.add_paragraph(
            "Hazard notes (use best judgment; the tools did not return this text): "
            + str(basis["hazard_notes"])
        )

    doc.add_heading("Trapped volume", level=2)
    doc.add_paragraph(volume["formula"])
    _table(
        doc,
        ["Role", "NPS", "Schedule", "Length ft", "ID in", "ID source"],
        [[
            row.get("role") or "",
            row.get("nps") if row.get("nps") is not None else "",
            row.get("schedule") or "",
            f"{float(row['length_ft']):g}",
            f"{float(row['d_in']):.3f}",
            row.get("id_source") or "",
        ] for row in volume["segments"]],
    )
    doc.add_paragraph(
        f"Pipe {fmt1(volume['pipe_gal'])} gal (calculated). "
        f"Fittings {fmt1(volume['fittings_gal'])} gal ({allowance_text(volume)}). "
        f"{trim_assumption_text(volume)}. "
        f"Zone total {fmt1(volume['zone_gal'])} gal."
        + (f" {friction_note(volume)}" if friction_note(volume) else "")
    )

    doc.add_heading("Water-delivery screen", level=2)
    doc.add_paragraph(screen["formula"])
    doc.add_paragraph(
        "Pipe-only row is the pipe timing comparison: a lower bound, not the governing screen. "
        "The size exemption uses the zone total (pipe, fittings, and trim) against the exemption threshold."
    )
    threshold = threshold_gal(screen)
    threshold_cell = f"{threshold:.0f}" if threshold is not None else "—"
    zone_time = "—" if fill_only(trip) else fmt1(trip["t_total_s"])
    pipe_time = "—" if fill_only(screen) else fmt1(screen["t_total_s"])
    _table(
        doc,
        ["Screen", "Volume gal", "t_total s", "Limit s", "Basis", "Screen result", "Exemption threshold gal",
         "Size exemption"],
        [
            [
                "Pipe only",
                fmt1(screen["volume_gal"]),
                pipe_time,
                _limit_cell(screen),
                screen["limit_basis"],
                f"{PIPE_ONLY_VERDICT} ({PIPE_ONLY_NOTE})",
                threshold_cell,
                "—",
            ],
            [
                "Zone total",
                fmt1(volume["zone_gal"]),
                zone_time,
                _limit_cell(trip),
                trip["limit_basis"],
                screen_verdict(trip).capitalize(),
                threshold_cell,
                exemption_answer(screen).capitalize(),
            ],
        ],
    )
    if fill_only(trip):
        doc.add_paragraph(
            f"Fill time alone, 60·V/Q: {fmt1(trip['t_fill_s'])} s (calculated). Margin to the "
            f"{fmt1(trip['limit_s'])} s limit on the fill time alone: {fmt1(trip['fill_margin_s'])} s. "
            f"{inputs.SUBTIMES_MISSING.capitalize()}."
        )
    elif trip.get("assumed_zero_note"):
        doc.add_paragraph(str(trip["assumed_zero_note"]))
    doc.add_paragraph(f"Size exemption judged against {threshold_words(screen)}"
                      + (f", on {screen['exemption_volume_basis']}." if screen.get("exemption_volume_basis") else "."))
    qualifier = exemption_qualifier(volume, screen)
    if qualifier:
        doc.add_paragraph(qualifier)
    if screen.get("near_threshold"):
        doc.add_paragraph(str(screen["near_threshold"]))
    doc.add_paragraph(screen["nfpa_basis"])
    if cite_note(trip):
        doc.add_paragraph(f"Kernel cite: {cite_note(trip)}")
    doc.add_paragraph(screen_limit_assumption_text(trip))
    doc.add_paragraph(
        f"Quick-opening device: {_yn(screen['qod'])}. "
        "On double-interlock the quick-opening device does not raise the exemption threshold."
    )

    doc.add_heading("Trim election", level=2)
    doc.add_paragraph(
        f"Status: {trim['status']}. Family: {trim.get('family') or 'none'}. "
        f"Controlling: {_yn(trim.get('controlling'))}."
    )
    if trim.get("power_loss_behavior"):
        doc.add_paragraph(str(trim["power_loss_behavior"]))
    doc.add_paragraph(
        "This screen does not elect a catalog number. Specify the valve, solenoid, and panel by function and listing."
    )

    doc.add_heading("Releasing cause and effect", level=2)
    # The second leg is P, the pressure drop from sprinkler operation. Low air is a
    # supervisory signal and has no column here.
    doc.add_paragraph(releasing_sentence(truth, trim.get("family")))
    doc.add_paragraph(
        f"{truth['detection_leg']}. {truth['second_smoke']}. {truth['abort']}."
    )
    _table(
        doc,
        ["Detection", "Manual", "P (second leg)", "Isolated", "Solenoid"],
        [[
            _yn(row["detection"]),
            _yn(row["manual"]),
            _yn(second_leg_value(row)),
            _yn(row["isolated"]),
            _yn(row["solenoid"]),
        ] for row in truth["rows_without_second_smoke"]],
    )
    doc.add_paragraph(
        f"Rows with the solenoid true, counting the second-smoke duplicate: {truth['solenoid_true_count']} "
        f"of {truth['row_count']}. The duplicate does not change the result."
    )

    doc.add_heading("Nitrogen and demand", level=2)
    # The pressure and the time the gas fill ran on, as the run's own call passed them. Nothing stands in for one.
    sent = next((call.get("input") for call in result.get("transcript") or []
                 if call.get("name") == "nitrogen_gate" and call.get("by") == "tool-plan"), None) or {}
    pressure = sent.get("p_psig", di.get("supervisory_psig"))
    minutes = sent.get("t_min", di.get("fill_minutes"))
    pressure_text = f"{float(pressure):g} psig" if pressure not in (None, "") else "a fill pressure not given"
    minutes_text = f"{float(minutes):g} min" if minutes not in (None, "") else "a fill time not given"
    doc.add_paragraph(
        f"Design Hazen-Williams C is {nitrogen['design_c']}. "
        f"Comparison C {nitrogen['comparison_c']} multiplies friction by about "
        f"{nitrogen['friction_ratio_c100_vs_c120']:.3f} and is not the design value. "
        f"{nitrogen['fill_bases']} "
        + (f"{nitrogen['sizing_note']} " if nitrogen.get("sizing_note") else "")
        + f"Both rates use {pressure_text} and {minutes_text}. "
        f"{nitrogen['formula']}."
    )
    _table(
        doc,
        ["Fill basis", "scfm"],
        [
            ["Gauge", f"{nitrogen['scfm_gauge_basis']:.2f}"],
            ["Absolute", f"{nitrogen['scfm_abs_basis']:.2f}"],
        ],
    )
    if density is None or hose is None:
        doc.add_paragraph("No demand was run for this zone: the form holds no density or base area.")
    else:
        _demand(doc, density, hose)

    doc.add_heading("Draft narrative", level=2)
    for paragraph in governing_narrative(result.get("narrative") or "").split("\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())

    doc.add_heading("Flags", level=2)
    flags = result.get("flags") or ["None."]
    for flag in flags:
        doc.add_paragraph(str(flag), style="List Bullet")

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    return path


def _demand(doc: Document, density: dict, hose: dict) -> None:
    doc.add_paragraph(
        f"Design area {density['design_area_ft2']:.0f} ft2. "
        f"Sprinklers {fmt1(density['q_spr_gpm'])} gpm. "
        f"Hose {fmt1(density['hose_gpm'])} gpm. "
        f"Total demand {fmt1(density['qd_gpm'])} gpm. "
        f"Table duration {hose['duration_min']:g} min "
        f"(range {hose['duration_range_min'][0]:g}–{hose['duration_range_min'][1]:g} min). "
        f"{hose['basis']}."
    )
    if density.get("gallons") is not None:
        doc.add_paragraph(
            f"Duration volume {fmt1(density['gallons'])} gal ({density.get('gallons_note') or 'includes hose'})."
        )
