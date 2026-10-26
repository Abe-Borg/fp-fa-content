"""Draft specification section. Every figure is copied from the tool-plan JSON.

Double-interlock preaction is CSI Section 21 13 19. Dry pipe is a different section
and is not this export.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document

from fpfa.workflow import fmt1, judgment_label_line, screen_limit_assumption_text, trim_assumption_text

DRAFT_SECTION = "21 13 19"
DRAFT_HEADING = "Section 21 13 19 — Double-interlock preaction (draft)"


def _yn(value) -> str:
    return "Yes" if value else "No"


def _limit_cell(row: dict) -> str:
    text = fmt1(row["limit_s"])
    if row.get("limit_basis") != "explicit":
        return f"{text} ASSUMED"
    return text


def _table(doc: Document, headers: list[str], rows: list[list]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        table.rows[0].cells[index].text = header
    for r_index, row in enumerate(rows, start=1):
        for c_index, value in enumerate(row):
            table.rows[r_index].cells[c_index].text = "" if value is None else str(value)


def write_docx(path: Path | str, project: dict, result: dict) -> Path:
    path = Path(path)
    tools = result["tools"]
    volume = tools["zone_trapped_volume"]
    screen = tools["dry_delivery_screen"]
    trip = tools["di_trip_to_water"]
    trim = tools["elect_di_trim"]
    truth = tools["releasing_truth_table"]
    nitrogen = tools["nitrogen_gate"]
    density = tools["density_area"]
    hose = tools["hose_duration"]
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
    doc.add_paragraph(
        f"AHJ: {basis.get('ahj') or '—'}. "
        f"NFPA 13: {basis.get('nfpa_13') or '—'}. "
        f"NFPA 72: {basis.get('nfpa_72') or '—'}. "
        f"Insurer: {basis.get('insurer') or '—'}."
    )
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
        f"Fittings {fmt1(volume['fittings_gal'])} gal at {volume['fittings_percent']:g}%. "
        f"{trim_assumption_text(volume)}. "
        f"Zone total {fmt1(volume['zone_gal'])} gal."
    )

    doc.add_heading("Water-delivery screen", level=2)
    doc.add_paragraph(screen["formula"])
    doc.add_paragraph(
        "Pipe-only row is the pipe timing comparison. "
        "The size exemption uses the zone total (pipe, fittings, and trim) against the cap."
    )
    _table(
        doc,
        ["Screen", "Volume gal", "t_total s", "Limit s", "Basis", "Passes", "NFPA size cap gal", "Size exemption"],
        [
            [
                "Pipe only",
                fmt1(screen["volume_gal"]),
                fmt1(screen["t_total_s"]),
                _limit_cell(screen),
                screen["limit_basis"],
                _yn(screen["passes_screen"]),
                f"{screen['nfpa_size_cap_gal']:.0f}",
                "—",
            ],
            [
                "Zone total",
                fmt1(volume["zone_gal"]),
                fmt1(trip["t_total_s"]),
                _limit_cell(trip),
                trip["limit_basis"],
                _yn(trip["passes_screen"]),
                f"{screen['nfpa_size_cap_gal']:.0f}",
                _yn(screen["nfpa_delivery_time_exempt"]),
            ],
        ],
    )
    doc.add_paragraph(screen["nfpa_basis"])
    doc.add_paragraph(screen_limit_assumption_text(trip))
    doc.add_paragraph(
        f"Quick-opening device: {_yn(screen['qod'])}. "
        "On double-interlock the quick-opening device does not raise the 500 gal cap."
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
    doc.add_paragraph(truth["boolean"])
    doc.add_paragraph(
        f"{truth['detection_leg']}. {truth['second_smoke']}. {truth['abort']}."
    )
    _table(
        doc,
        ["Detection", "Manual", "Low air", "Isolated", "Solenoid"],
        [[
            _yn(row["detection"]),
            _yn(row["manual"]),
            _yn(row["low_air"]),
            _yn(row["isolated"]),
            _yn(row["solenoid"]),
        ] for row in truth["rows_without_second_smoke"]],
    )
    doc.add_paragraph(
        f"Rows with the solenoid true, counting the second-smoke duplicate: {truth['solenoid_true_count']} "
        f"of {truth['row_count']}. The duplicate does not change the result."
    )

    doc.add_heading("Nitrogen and demand", level=2)
    doc.add_paragraph(
        f"Design Hazen-Williams C is {nitrogen['design_c']}. "
        f"Comparison C {nitrogen['comparison_c']} multiplies friction by about "
        f"{nitrogen['friction_ratio_c100_vs_c120']:.3f} and is not the design value. "
        f"Gauge-basis fill {nitrogen['scfm_gauge_basis']:.2f} scfm "
        f"at {di.get('supervisory_psig') or 40} psig in {di.get('fill_minutes') or 30} min. "
        f"{nitrogen['formula']}."
    )
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

    doc.add_heading("Draft narrative", level=2)
    for paragraph in (result.get("narrative") or "").split("\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())

    doc.add_heading("Flags", level=2)
    flags = result.get("flags") or ["None."]
    for flag in flags:
        doc.add_paragraph(str(flag), style="List Bullet")

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    return path
