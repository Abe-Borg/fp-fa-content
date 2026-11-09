"""Design Basis and Open Questions export. Every line comes from the project record.

This is the second document the app writes. The Section 21 13 19 export
stays as it is. Nothing here is typed by hand: basis facts, elections,
calculation records, findings, checker verdicts, assumptions, open
questions, and the handoff log are read from Record.snapshot(). A figure
is shown with the label the record holds for it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docx import Document

from fpfa.workflow import (
    fmt1,
    judgment_label_line,
    screen_limit_assumption_text,
    trim_assumption_text,
)

DESIGN_BASIS_TITLE = "Design Basis and Open Questions (draft)"
NO_CHECK_LINE = (
    "No blind claim check has run on this record. "
    "Every finding below is unverified against its cite until the checker runs."
)
SCREEN_LINE = (
    "A delivery time in this document is an optimistic screen from trapped volume and an "
    "assumed fill flow. It is not a listed water-delivery-time calculation."
)
_BASIS_KINDS = ("basis", "edition", "owner", "insurer", "ahj", "jurisdiction")
_MAX_JSON = 600


def _yn(value: Any) -> str:
    return "yes" if value else "no"


def _compact(value: Any, limit: int = _MAX_JSON) -> str:
    text = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def _table(doc: Document, headers: list[str], rows: list[list[Any]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        table.rows[0].cells[index].text = header
    for r_index, row in enumerate(rows, start=1):
        for c_index, value in enumerate(row):
            table.rows[r_index].cells[c_index].text = "" if value is None else str(value)


def key_figures(tool: str, inputs: Any, outputs: Any) -> str:
    """One sentence of the figures that matter from a calc record, with their labels."""
    out = outputs if isinstance(outputs, dict) else {}
    inp = inputs if isinstance(inputs, dict) else {}
    try:
        if tool == "zone_trapped_volume":
            return (
                f"Pipe {fmt1(out['pipe_gal'])} gal (calculated). "
                f"Fittings {fmt1(out['fittings_gal'])} gal at {float(out['fittings_percent']):g}%. "
                f"{trim_assumption_text(out)}. Zone total {fmt1(out['zone_gal'])} gal (calculated)."
            )
        if tool == "dry_delivery_screen":
            exempt = out.get("nfpa_delivery_time_exempt")
            return (
                f"Pipe-only t_total {fmt1(out['t_total_s'])} s against the {fmt1(out['limit_s'])} s "
                f"{out.get('limit_basis', '')} limit: {'passes' if out.get('passes_screen') else 'does not pass'}. "
                f"NFPA size cap {float(out['nfpa_size_cap_gal']):.0f} gal; zone-total exemption {_yn(exempt)}. "
                f"{out.get('nfpa_basis', '')}"
            )
        if tool == "di_trip_to_water":
            return (
                f"Fill {fmt1(out['t_fill_s'])} s, t_total {fmt1(out['t_total_s'])} s, "
                f"margin {fmt1(out['margin_s'])} s; the zone-total screen "
                f"{'passes' if out.get('passes_screen') else 'does not pass'}. "
                f"About {fmt1(out['v_max_gal_at_limit'])} gal meets the limit at this fill flow and these allowances. "
                f"{screen_limit_assumption_text(out)}"
            )
        if tool == "hose_duration":
            low, high = out["duration_range_min"]
            return (
                f"Duration {float(out['duration_min']):g} min (table range {float(low):g} to {float(high):g}), "
                f"combined hose {float(out['hose_total_gpm']):g} gpm. {out.get('basis', '')}."
            )
        if tool == "density_area":
            text = (
                f"Design area {float(out['design_area_ft2']):.0f} ft². Sprinklers {fmt1(out['q_spr_gpm'])} gpm. "
                f"Hose {fmt1(out['hose_gpm'])} gpm. Total demand {fmt1(out['qd_gpm'])} gpm (calculated)."
            )
            if out.get("gallons") is not None:
                text += f" Duration volume {float(out['gallons']):,.0f} gal over {float(out['duration_min']):g} min."
            return text
        if tool == "nitrogen_gate":
            return (
                f"Design Hazen-Williams C {out['design_c']}. C {out['comparison_c']} is comparison only and "
                f"multiplies friction by about {float(out['friction_ratio_c100_vs_c120']):.3f}. "
                f"Fill {float(out['scfm_gauge_basis']):.2f} scfm gauge basis, "
                f"{float(out['scfm_abs_basis']):.2f} scfm absolute basis (calculated)."
            )
        if tool == "elect_di_trim":
            psi = out.get("supervisory_psi")
            psi_text = f"{float(psi):g} psi" if psi is not None else "not given"
            return (
                f"Family {out.get('family') or 'none'}, status {out.get('status')}, prime held by "
                f"{out.get('prime_held_by') or 'unresolved'}, supervisory {psi_text}, medium {out.get('medium') or 'unelected'}. "
                "No catalog number is elected."
            )
        if tool == "releasing_truth_table":
            return (
                f"{out['boolean']}. Manual station {'on' if out.get('manual_station') else 'off'}. "
                f"{out['solenoid_true_count']} true rows of {out['row_count']}; a second smoke zone changes nothing. "
                f"{'FM basis: no cross-zone.' if out.get('fm_no_cross_zone') else ''}"
            ).strip()
        if tool == "lfl_setpoints":
            rows = ", ".join(
                f"{row.get('name') or row.get('basis')} {float(row['pct']):g}% of LFL = "
                f"{float(row['vol_pct']):.2f} vol% ({float(row['ppm']):.0f} ppm)"
                for row in out.get("setpoints") or []
            )
            return (
                f"Mixture LFL {float(out['lfl_fuel_vol_pct']):.2f} vol% fuel-only, "
                f"{float(out['lfl_diluted_vol_pct']):.2f} vol% with diluent (calculated). "
                f"Setpoints: {rows or 'none'}."
            )
        if tool == "resolve_pipe_id":
            return (
                f"NPS {out.get('nps')} {out.get('schedule')} inside diameter {float(out['d_in']):.3f} in. "
                f"({out.get('id_source')})."
            )
    except (KeyError, TypeError, ValueError):
        pass
    return f"Inputs {_compact(inp, 240)}. Outputs {_compact(out, 360)}."


def elections_from_calcs(calcs: list[dict]) -> list[list[str]]:
    """Election rows the tool plan settled, read from calc records. Not typed by hand."""
    rows: list[list[str]] = []
    for row in calcs:
        tool = row.get("tool")
        out = row.get("outputs") if isinstance(row.get("outputs"), dict) else {}
        inp = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
        if tool == "elect_di_trim":
            rows.append([
                "Trim family",
                f"{out.get('family') or 'none'} ({out.get('status')})",
                "tool plan: elect_di_trim",
                row.get("id", ""),
            ])
            if inp.get("system_type"):
                rows.append(["System family", str(inp["system_type"]), "zone form", row.get("id", "")])
            if out.get("medium") and out.get("medium") != "unelected":
                rows.append(["Supervisory medium", str(out["medium"]), "zone form", row.get("id", "")])
        elif tool == "releasing_truth_table":
            rows.append(["Releasing logic", str(out.get("boolean", "")), "tool plan: releasing_truth_table", row.get("id", "")])
        elif tool == "nitrogen_gate":
            rows.append(["Design Hazen-Williams C", str(out.get("design_c", "")), "tool plan: nitrogen_gate", row.get("id", "")])
    return rows


def assumption_lines(snapshot: dict) -> list[str]:
    """Every ASSUMED row and every ASSUMED flag a calc returned."""
    lines: list[str] = []
    for row in snapshot.get("facts") or []:
        if row.get("label") == "ASSUMED":
            lines.append(f"{row['kind']}/{row['key']}: {row['value']} [{row['id']}]")
    for row in snapshot.get("findings") or []:
        if row.get("label") == "ASSUMED":
            lines.append(f"{row['agent']}: {row['text']} [{row['id']}]")
    for row in snapshot.get("decisions") or []:
        if row.get("label") == "ASSUMED":
            lines.append(f"{row['decided_by']}: {row['text']} [{row['id']}]")
    for row in snapshot.get("calcs") or []:
        out = row.get("outputs") if isinstance(row.get("outputs"), dict) else {}
        for flag in out.get("flags") or []:
            if isinstance(flag, str) and "ASSUMED" in flag:
                lines.append(f"{row['tool']}: {flag} [{row['id']}]")
        if row.get("tool") == "di_trip_to_water" and out.get("limit_basis") not in (None, "explicit"):
            lines.append(f"{row['tool']}: {screen_limit_assumption_text(out)} [{row['id']}]")
    return lines


def write_design_basis(
    path: Path | str,
    project: dict,
    snapshot: dict,
    *,
    claim_check: dict | None = None,
) -> Path:
    """Write the document from a Record.snapshot(). Returns the path written."""
    path = Path(path)
    facts = list(snapshot.get("facts") or [])
    calcs = list(snapshot.get("calcs") or [])
    findings = list(snapshot.get("findings") or [])
    questions = list(snapshot.get("questions") or [])
    decisions = list(snapshot.get("decisions") or [])
    handoffs = list(snapshot.get("handoffs") or [])
    evidence = list(snapshot.get("evidence") or [])
    agents = list(snapshot.get("agents") or [])

    doc = Document()
    doc.core_properties.title = DESIGN_BASIS_TITLE
    doc.core_properties.subject = "Design basis, calculation records, findings, and open questions"
    doc.add_heading(DESIGN_BASIS_TITLE, level=1)
    doc.add_paragraph(
        f"Project: {project.get('name') or 'Untitled job'}. "
        "Draft for the engineer of record. Every line is read from the project record; nothing is typed by hand. "
        "Pipe gallons and t_total are calculated. Figures marked ASSUMED were not calculated from the zone."
    )
    doc.add_paragraph(SCREEN_LINE)
    doc.add_paragraph(judgment_label_line())
    if agents:
        doc.add_paragraph(
            "Contributors: " + ", ".join(f"{row['name']} ({row['role_slug']}, {row['status']})" for row in agents) + "."
        )

    doc.add_heading("1. Basis of design", level=2)
    basis_rows = [row for row in facts if row.get("kind") in _BASIS_KINDS]
    other_rows = [row for row in facts if row.get("kind") not in _BASIS_KINDS and row.get("label") != "ASSUMED"]
    if basis_rows or other_rows:
        _table(
            doc,
            ["Item", "Value", "Label", "Source", "By", "Id"],
            [[f"{row['kind']}/{row['key']}", row["value"], row["label"], row.get("source") or "", row.get("agent") or "", row["id"]]
             for row in basis_rows + other_rows],
        )
    else:
        doc.add_paragraph("No basis facts are on the record yet.")
    if evidence:
        doc.add_paragraph("Cites held on the record:")
        _table(
            doc,
            ["Document", "Edition", "Section", "Note", "Applies to", "Status", "Id"],
            [[row["document"], row.get("edition") or "", row.get("section") or "", row.get("note") or "",
              row.get("applicability") or "", row["status"], row["id"]] for row in evidence],
        )

    doc.add_heading("2. Elections", level=2)
    election_rows = elections_from_calcs(calcs)
    for row in decisions:
        election_rows.append([
            "Decision",
            row["text"] + (f" Basis: {row['basis']}" if row.get("basis") else ""),
            f"{row['decided_by']} ({row['label']})",
            row["id"],
        ])
    if election_rows:
        _table(doc, ["Election", "Value", "Basis", "Id"], election_rows)
    else:
        doc.add_paragraph("No elections are on the record yet.")

    doc.add_heading("3. Calculation records", level=2)
    if calcs:
        _table(
            doc,
            ["Tool", "By", "Recorded", "Replays", "Figures", "Id"],
            [[row["tool"], row.get("agent") or "", row.get("created") or "", row.get("replay_count", 0),
              key_figures(row["tool"], row.get("inputs"), row.get("outputs")), row["id"]] for row in calcs],
        )
        doc.add_paragraph(
            "Inputs for each record, as passed to the tool:"
        )
        for row in calcs:
            doc.add_paragraph(f"[{row['id']}] {row['tool']}: {_compact(row.get('inputs'))}", style="List Bullet")
    else:
        doc.add_paragraph("No calculation has been recorded on this job.")

    doc.add_heading("4. Findings by contributor", level=2)
    if findings:
        by_agent: dict[str, list[dict]] = {}
        for row in findings:
            by_agent.setdefault(row.get("agent") or "unknown", []).append(row)
        for agent, rows in by_agent.items():
            doc.add_heading(agent, level=3)
            for row in rows:
                supports = ", ".join(row.get("supports") or []) or "none"
                doc.add_paragraph(
                    f"{row['text']} ({row['label']}; supports: {supports}) [{row['id']}]",
                    style="List Bullet",
                )
    else:
        doc.add_paragraph("No findings are on the record yet.")

    doc.add_heading("5. Checker verdicts", level=2)
    rows = (claim_check or {}).get("rows") if isinstance(claim_check, dict) else None
    if rows:
        status = (claim_check or {}).get("status_line") or ""
        if status:
            doc.add_paragraph(str(status))
        _table(doc, ["Claim", "Verdict", "Cite"], [[row.get("n"), row.get("verdict"), row.get("cite")] for row in rows])
        if not (claim_check or {}).get("all_supported"):
            doc.add_paragraph("Not every claim is Supported. This draft is not cleared for issue.")
    else:
        doc.add_paragraph(NO_CHECK_LINE)

    doc.add_heading("6. Assumptions", level=2)
    assumed = assumption_lines(snapshot)
    if assumed:
        for line in assumed:
            doc.add_paragraph(line, style="List Bullet")
    else:
        doc.add_paragraph("No ASSUMED rows are on the record.")

    doc.add_heading("7. Open questions and RFIs", level=2)
    open_rows = [row for row in questions if row.get("status") == "open"]
    answered_rows = [row for row in questions if row.get("status") == "answered"]
    if open_rows:
        for row in open_rows:
            doc.add_paragraph(f"{row['text']} (raised by {row['raised_by']}) [{row['id']}]", style="List Number")
    else:
        doc.add_paragraph("No open questions are on the record.")
    if answered_rows:
        doc.add_paragraph("Answered:")
        for row in answered_rows:
            doc.add_paragraph(f"{row['text']} Answer: {row['answer']} [{row['id']}]", style="List Bullet")

    doc.add_heading("8. Handoff log", level=2)
    if handoffs:
        _table(
            doc,
            ["From", "To", "Brief", "Status", "Created", "Returned", "Id"],
            [[row["from_agent"], row["to_agent"], row["brief"], row["status"], row.get("created") or "",
              row.get("returned") or "", row["id"]] for row in handoffs],
        )
    else:
        doc.add_paragraph("No handoffs are on the record.")

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    return path
