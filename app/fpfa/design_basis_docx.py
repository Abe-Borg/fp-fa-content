"""Design Basis and Open Questions export. Every line comes from the project record.

This is the second document the app writes. The Section 21 13 19 export
stays as it is. Nothing here is typed by hand: project inputs, elections,
calculation records, findings, reviews, the trace check, assumptions, open
questions, and the exchanges between agents are read from Record.snapshot().
A figure is shown with the label the record holds for it.

The document is built so an engineer can tell four kinds of statement apart
without reading the code: what the trace check found consistent with a row
the application identified, what it found consistent only with its author's
own cite, what a specialist stated and nothing judged, and what still needs
evidence or an engineer's review. fpfa.checker derives the tier of each
finding; no model types one. Rows whose basis changed, and rows that were
replaced or withdrawn, are shown as history and never as current.

Two things are said at the head, before any finding, so the document
cannot be read as more than it is. Coverage: what a design basis written
from this record is still missing (checker.coverage); a document with a gap
opens with INCOMPLETE DRAFT and the list. And the kinds of assurance: every
kind a reader might assume, with the two this application never performs
(verification against the primary standard, and a qualified engineer's
review) named as not performed (checker.LADDER).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docx import Document

from fpfa import checker, coherence, content_use, inputs, status
from fpfa.inputs import SUBTIMES_MISSING
from fpfa.workflow import (
    cite_note,
    exemption_answer,
    fill_only,
    fmt1,
    judgment_label_line,
    releasing_logic,
    screen_limit_assumption_text,
    threshold_words,
    trim_assumption_text,
)

DESIGN_BASIS_TITLE = "Design Basis and Open Questions (draft)"
NO_CHECK_LINE = (
    "No trace check has run on this record. "
    "No finding below has been judged against the rows it cites."
)
STALE_CHECK_LINE = (
    "Findings changed after the last trace check. The verdicts shown are for the findings that check saw; "
    "a finding written since is listed as not reviewed."
)
SCREEN_LINE = (
    "A delivery time in this document is an optimistic screen from trapped volume and an "
    "assumed fill flow. It is not a listed water-delivery-time calculation."
)
DRAFT_LINE = (
    "This is a draft for the engineer of record. It is not cleared for issue. The team that wrote it is one "
    "AI model in several roles; the trace check is a second pass by the same model on a blind packet."
)
_MAX_JSON = 600
_PLAN = status.PLAN_AGENTS


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
            answer = exemption_answer(out)
            if "exemption_volume_gal" in out:
                size = (f"size exemption on the zone total of {fmt1(out['exemption_volume_gal'])} gal: {answer} "
                        f"(judged on {out.get('exemption_volume_basis') or 'the zone total'}; what in that total "
                        "is ASSUMED is on the zone_trapped_volume record)")
            else:
                # A pipe-only screen, or a row recorded before the screen was handed the zone total.
                size = (f"size exemption: {answer}. This record is a pipe-only screen of "
                        f"{fmt1(out['volume_gal'])} gal; fittings and trim are not in it, and the exemption is "
                        "judged on the zone total")
            if fill_only(out):
                timing = (f"Pipe-only fill time {fmt1(out['t_fill_s'])} s against the {fmt1(out['limit_s'])} s "
                          f"{out.get('limit_basis', '')} limit: {SUBTIMES_MISSING}. ")
            else:
                timing = (f"Pipe-only t_total {fmt1(out['t_total_s'])} s against the {fmt1(out['limit_s'])} s "
                          f"{out.get('limit_basis', '')} limit (a lower bound, not the governing screen). ")
            near = f" {out['near_threshold']}" if out.get("near_threshold") else ""
            return (
                f"{timing}Exemption threshold: {threshold_words(out)}; {size}.{near} "
                f"{out.get('nfpa_basis', '')}"
            ).strip()
        if tool == "di_trip_to_water":
            if fill_only(out):
                return (
                    f"Fill time alone {fmt1(out['t_fill_s'])} s; margin to the limit on the fill time alone "
                    f"{fmt1(out['fill_margin_s'])} s; {SUBTIMES_MISSING}. {screen_limit_assumption_text(out)} "
                    f"{('Kernel cite: ' + cite_note(out)) if cite_note(out) else ''}"
                ).strip()
            zero = f" {out['assumed_zero_note']}" if out.get("assumed_zero_note") else ""
            return (
                f"Fill {fmt1(out['t_fill_s'])} s, t_total {fmt1(out['t_total_s'])} s, "
                f"margin {fmt1(out['margin_s'])} s; the zone-total screen "
                f"{'passes' if out.get('passes_screen') else 'does not pass'}.{zero} "
                f"About {fmt1(out['v_max_gal_at_limit'])} gal meets the limit at this fill flow and these allowances. "
                f"{screen_limit_assumption_text(out)} "
                f"{('Kernel cite: ' + cite_note(out)) if cite_note(out) else ''}"
            ).strip()
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
            if out.get("release_status"):
                text += f" {out.get('assumed_note') or ''} {out['release_status']}.".replace("  ", " ")
            return text
        if tool == "nitrogen_gate":
            return (
                f"Design Hazen-Williams C {out['design_c']}. C {out['comparison_c']} is comparison only and "
                f"multiplies friction by about {float(out['friction_ratio_c100_vs_c120']):.3f}. "
                f"Fill {float(out['scfm_gauge_basis']):.2f} scfm gauge basis, "
                f"{float(out['scfm_abs_basis']):.2f} scfm absolute basis (calculated)."
                + (f" {out['sizing_note']}" if out.get("sizing_note") else "")
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
            logic = releasing_logic(out)
            return (
                f"{logic['expression']}. {logic['second_leg']} {logic['supervisory']} "
                f"Manual station {'on' if out.get('manual_station') else 'off'}. "
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


def _who(row: dict) -> str:
    agent = row.get("agent") or ""
    return "tool plan" if agent in _PLAN else agent


def elections_from_calcs(calcs: list[dict], analysis: dict | None = None) -> list[list[str]]:
    """Election rows read from calc records. Not typed by hand.

    With analysis, a calc whose basis changed is left out, and one that ran
    on another value than the project input says so.
    """
    states = (analysis or {}).get("calcs") or {}
    rows: list[list[str]] = []
    for row in calcs:
        standing = states.get(row.get("id"), {})
        if standing.get("state") == coherence.STALE:
            continue
        note = f" (alternative: ran on {standing['note']})" if standing.get("state") == coherence.ALTERNATIVE else ""
        tool = row.get("tool")
        out = row.get("outputs") if isinstance(row.get("outputs"), dict) else {}
        inp = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
        source = f"{_who(row)}: {tool}{note}"
        if tool == "elect_di_trim":
            rows.append([
                "Trim family",
                f"{out.get('family') or 'none'} ({out.get('status')})",
                source,
                row.get("id", ""),
            ])
            if inp.get("system_type"):
                rows.append(["System family", str(inp["system_type"]), "zone form", row.get("id", "")])
            if out.get("medium") and out.get("medium") != "unelected":
                rows.append(["Supervisory medium", str(out["medium"]), "zone form", row.get("id", "")])
        elif tool == "releasing_truth_table":
            rows.append(["Releasing logic", releasing_logic(out)["expression"], source, row.get("id", "")])
        elif tool == "nitrogen_gate":
            rows.append(["Design Hazen-Williams C", str(out.get("design_c", "")), source, row.get("id", "")])
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
    states = coherence.analyze(snapshot)["calcs"]
    for row in snapshot.get("calcs") or []:
        if states.get(row["id"], {}).get("state") == coherence.STALE:
            continue
        out = row.get("outputs") if isinstance(row.get("outputs"), dict) else {}
        for flag in out.get("flags") or []:
            if isinstance(flag, str) and "ASSUMED" in flag:
                lines.append(f"{row['tool']}: {flag} [{row['id']}]")
        if row.get("tool") == "di_trip_to_water" and out.get("limit_basis") not in (None, "explicit"):
            lines.append(f"{row['tool']}: {screen_limit_assumption_text(out)} [{row['id']}]")
    return lines


def _clip(text: Any, limit: int) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _rests_on(finding: dict, rows: dict[str, dict]) -> str:
    """What a finding or a decision cites, in words, each with its id."""
    parts = []
    for ident in finding.get("supports") or []:
        row = rows.get(ident)
        if row is None:
            parts.append(f"[{ident}] (not on the record)")
        elif row["_kind"] == "calc":
            parts.append(f"{row['tool']} [{ident}]")
        elif row["_kind"] == "evidence":
            parts.append(f"{checker.cite_name(row)} [{ident}]")
        elif row["_kind"] == "fact":
            word = "input" if row.get("kind") in (inputs.INPUT_KIND, inputs.BASIS_KIND) else "fact"
            parts.append(f"{word} {row['key']} [{ident}]")
        elif row["_kind"] == "decision":
            parts.append(f"decision [{ident}]")
        else:
            parts.append(f"finding [{ident}]")
    return "; ".join(parts) or "nothing cited"


_SOURCE_WORDS = {
    "calc": "calculation record",
    "pack": "content-pack note",
    "author": "its author's own note; the section is not in the content pack",
    "input": "project input",
    "fact": "a fact a contributor recorded, not a project input",
    "finding": "another finding",
    "decision": "a decision the team recorded",
    "missing": "a row that is not on the record",
}


def _checked_against(item: dict) -> str:
    """How far the trace check took one finding, and why it stands where it does."""
    parts = []
    for source in item.get("sources") or []:
        text = f"{_SOURCE_WORDS.get(source.get('kind'), source.get('kind'))}: {source.get('text')}"
        if source.get("where"):
            text += " (" + ", ".join(source["where"]) + ")"
        parts.append(text)
    lines = []
    if item.get("checked"):
        lines.append(f"Trace check: {item.get('verdict')}." + (" Against " + "; ".join(parts) + "." if parts else ""))
    else:
        lines.append("No trace check has judged it.")
    lines.extend(item.get("reasons") or [])
    return " ".join(lines)


def write_design_basis(
    path: Path | str,
    project: dict,
    snapshot: dict,
    *,
    claim_check: dict | None = None,
    content_root: Path | str | None = None,
) -> Path:
    """Write the document from a Record.snapshot(). Returns the path written.

    claim_check is the trace check to print. None reads the newest one the
    snapshot carries. content_root is the content pack, read only to say
    whether a cite a specialist recorded is one the skill it read holds.
    """
    path = Path(path)
    facts = list(snapshot.get("facts") or [])
    calcs = list(snapshot.get("calcs") or [])
    findings = list(snapshot.get("findings") or [])
    questions = list(snapshot.get("questions") or [])
    decisions = list(snapshot.get("decisions") or [])
    handoffs = list(snapshot.get("handoffs") or [])
    evidence = list(snapshot.get("evidence") or [])
    agents = list(snapshot.get("agents") or [])
    reviews = list(snapshot.get("reviews") or [])
    analysis = coherence.analyze(snapshot)
    digest = status.build(snapshot)
    check = claim_check if isinstance(claim_check, dict) else checker._latest_check_in(snapshot)
    tiers = checker.assurance(snapshot, check)
    rows_by_id: dict[str, dict] = {}
    for row in calcs:
        rows_by_id[row["id"]] = dict(row, _kind="calc")
    for row in evidence:
        rows_by_id[row["id"]] = dict(row, _kind="evidence")
    for row in snapshot.get("fact_history") or facts:
        rows_by_id[row["id"]] = dict(row, _kind="fact")
    for row in findings + list(snapshot.get("retired_findings") or []):
        rows_by_id[row["id"]] = dict(row, _kind="finding")
    for row in list(snapshot.get("decisions") or []) + list(snapshot.get("retired_decisions") or []):
        rows_by_id[row["id"]] = dict(row, _kind="decision")

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
    plan = digest.get("plan")
    if plan and plan["objective"]:
        doc.add_paragraph(f"Objective the team worked to: {plan['objective']}")

    covered = checker.coverage(snapshot)
    doc.add_heading("What this document covers", level=2)
    if covered["complete"]:
        doc.add_paragraph(checker.COMPLETE_LINE)
    else:
        doc.add_paragraph(checker.INCOMPLETE_HEAD)
        for gap in covered["gaps"]:
            doc.add_paragraph(gap, style="List Bullet")
        doc.add_paragraph(
            "It is exported so the engineer of record can see where the work stands. Do not issue it or rely on "
            "it as a complete design basis."
        )

    doc.add_heading("How far each statement was taken", level=2)
    doc.add_paragraph(DRAFT_LINE)
    doc.add_paragraph(
        "Kinds of assurance, in order. The last two were not performed on anything in this document."
    )
    _table(doc, ["Kind of assurance", "What it is", "Where it applies here"],
           [[name, what, where] for name, what, where in checker.LADDER])
    if check and check.get("rows"):
        doc.add_paragraph(str(check.get("status_line") or "A trace check ran."))
        if check.get("token") and check.get("token") != checker.check_token(findings):
            doc.add_paragraph(STALE_CHECK_LINE)
    else:
        doc.add_paragraph(NO_CHECK_LINE)
    counts = {tier: 0 for tier in checker.TIERS}
    for item in tiers.values():
        counts[item["tier"]] += 1
    _table(
        doc,
        ["Standing", "Findings", "What it means"],
        [[checker.TIER_TITLE[tier], counts[tier], checker.TIER_NOTE[tier]] for tier in checker.TIERS],
    )
    doc.add_paragraph(checker.NOT_STANDARD)
    if digest["stale"]:
        doc.add_paragraph(
            f"{len(digest['stale'])} row{'s' if len(digest['stale']) != 1 else ''} on this record "
            f"{'are' if len(digest['stale']) != 1 else 'is'} out of date because an input changed. They are marked "
            "where they appear and listed in section 11. Do not read them as current."
        )
    open_objections = [row for row in digest["objections"]]
    if open_objections or digest["conflicts"]:
        count = len(open_objections) + len(digest["conflicts"])
        doc.add_paragraph(
            f"{count} disagreement{'s' if count != 1 else ''} between contributors "
            f"{'are' if count != 1 else 'is'} not settled. See section 5."
        )

    doc.add_heading("1. Project inputs and basis of design", level=2)
    given = digest["inputs"]
    if given:
        doc.add_paragraph(
            "What the designer supplied. The team works from these. A starting value the designer has not "
            "confirmed is marked; it is the form's default and not their input."
        )
        _table(
            doc,
            ["Input", "Value", "Label", "Supplied by", "Id"],
            [[row["name"], "(blank)" if row["blank"] else row["text"], row["label"],
              (row["source"] or row["by"]) + (" UNCONFIRMED" if row["unconfirmed"] and not row["blank"] else ""),
              row["id"]] for row in given],
        )
    other_rows = [row for row in facts
                  if row.get("kind") != inputs.INPUT_KIND
                  and not (row.get("kind") == inputs.BASIS_KIND and row.get("key") in inputs.BASIS_FIELDS)
                  and row.get("label") != "ASSUMED"]
    if other_rows:
        doc.add_paragraph("Other facts the team recorded:")
        _table(
            doc,
            ["Item", "Value", "Label", "Source", "By", "Id"],
            [[f"{row['kind']}/{row['key']}", row["value"], row["label"], row.get("source") or "", row.get("agent") or "", row["id"]]
             for row in other_rows],
        )
    if not given and not other_rows:
        doc.add_paragraph("No project inputs are on the record yet.")

    doc.add_heading("2. Elections and decisions", level=2)
    election_rows = elections_from_calcs(calcs, analysis)
    for row in decisions:
        standing = analysis["decisions"].get(row["id"], {})
        stale = " OUT OF DATE: " + "; ".join(standing.get("reasons") or [])[:300] if standing.get("state") == coherence.STALE else ""
        election_rows.append([
            "Decision",
            row["text"] + (f" Basis: {row['basis']}" if row.get("basis") else "") + stale,
            f"{row['decided_by']} ({row['label']})",
            row["id"],
        ])
    if election_rows:
        _table(doc, ["Election", "Value", "Basis", "Id"], election_rows)
    else:
        doc.add_paragraph("No elections are on the record yet.")

    doc.add_heading("3. Calculation records", level=2)
    current_calcs = [row for row in calcs if analysis["calcs"][row["id"]]["state"] != coherence.STALE]
    if current_calcs:
        def standing_of(row: dict) -> str:
            item = analysis["calcs"][row["id"]]
            hold = item.get("edition_hold") or ""
            if item["state"] == coherence.ALTERNATIVE:
                return f"ALTERNATIVE: ran on {item['note']}. Not the design case." + (f" {hold}" if hold else "")
            if hold:
                # The figures follow the zone inputs. The cite does not follow the edition the job states,
                # so the row is never called "follows the project inputs" while that stands.
                return hold + (" Its figures follow the zone inputs." if item.get("tracked") else "")
            if item.get("tracked"):
                return "follows the project inputs"
            if item.get("unchecked"):
                return "NOT RECONCILED. " + item["unchecked"]
            if row.get("tool") in coherence.TRACKED_TOOLS:
                # Recorded with no project inputs on the record to follow.
                return "current; no project inputs were on the record when it ran"
            return "not tied to the project inputs: a change to an input will not mark it out of date"

        _table(
            doc,
            ["Tool", "By", "Recorded", "Replays", "Figures", "Standing", "Id"],
            [[row["tool"], row.get("agent") or "", row.get("created") or "", row.get("replay_count", 0),
              key_figures(row["tool"], row.get("inputs"), row.get("outputs")), standing_of(row), row["id"]]
             for row in current_calcs],
        )
        doc.add_paragraph(
            "Inputs for each record, as passed to the tool:"
        )
        for row in current_calcs:
            code = row.get("calc_identity") or "unknown"
            pack = row.get("pack_version") or "unknown"
            doc.add_paragraph(
                f"[{row['id']}] {row['tool']} (pack {pack}, calc code {code}): {_compact(row.get('inputs'))}",
                style="List Bullet",
            )
    else:
        doc.add_paragraph("No calculation has been recorded on this job." if not calcs
                          else "Every calculation on this job is out of date. See section 11.")

    doc.add_heading("4. Findings, by how far each was taken", level=2)
    if findings:
        agreed: dict[str, list[str]] = {}
        for item in reviews:
            if item.get("position") == "agree":
                agreed.setdefault(item["finding_id"], []).append(item.get("agent") or "")
        for tier in checker.TIERS:
            rows = [row for row in findings if tiers[row["id"]]["tier"] == tier]
            doc.add_heading(f"{checker.TIER_TITLE[tier]} ({len(rows)})", level=3)
            doc.add_paragraph(checker.TIER_NOTE[tier])
            if not rows:
                doc.add_paragraph("None.")
                continue
            _table(
                doc,
                ["Finding", "Label", "By", "Rests on", "How far it was taken", "Agreed by", "Id"],
                [[row["text"], row["label"], row.get("agent") or "unknown", _rests_on(row, rows_by_id),
                  _checked_against(tiers[row["id"]]), ", ".join(sorted(set(agreed.get(row["id"], [])))) or "",
                  row["id"]] for row in rows],
            )
    else:
        doc.add_paragraph("No findings are on the record yet.")

    doc.add_heading("5. Reviews and disagreements", level=2)
    all_findings = {row["id"]: row for row in findings + list(snapshot.get("retired_findings") or [])}
    if reviews or digest["conflicts"]:
        if reviews:
            doc.add_paragraph(
                "One contributor's position on another's finding. An objection ends when the author revises or "
                "withdraws the finding, the lead settles it with a recorded decision, or it is sent to the designer "
                "or the engineer of record as a question."
            )

            def ended(row: dict) -> str:
                if row.get("position") == "agree":
                    return ""
                if row.get("status") == "open":
                    return "OPEN. Not settled."
                if row.get("status") == "escalated":
                    return "ESCALATED, not settled. " + str(row.get("resolution") or "")
                return str(row.get("resolution") or row.get("status") or "")

            _table(
                doc,
                ["Finding", "Author", "Reviewer", "Position", "Note", "How it ended"],
                [[_clip((all_findings.get(row["finding_id"]) or {}).get("text") or f"[{row['finding_id']}]", 220),
                  (all_findings.get(row["finding_id"]) or {}).get("agent") or "", row.get("agent") or "",
                  "objects" if row.get("position") == "object" else "agrees", row.get("note") or "", ended(row)]
                 for row in reviews],
            )
        for item in digest["conflicts"]:
            values = "; ".join(f"{row['agent']} recorded {row['value']} [{row['id']}]" for row in item["rows"])
            doc.add_paragraph(f"Conflicting values for {item['kind']}/{item['key']}, not settled: {values}.", style="List Bullet")
    else:
        doc.add_paragraph("No contributor has reviewed another's finding on this record.")

    doc.add_heading("6. Assumptions", level=2)
    assumed = assumption_lines(snapshot)
    if assumed:
        for line in assumed:
            doc.add_paragraph(line, style="List Bullet")
    else:
        doc.add_paragraph("No ASSUMED rows are on the record.")
    for row in digest["unconfirmed"]:
        doc.add_paragraph(f"Starting value not confirmed by the designer: {row['name']} {row['text']} [{row['id']}]",
                          style="List Bullet")

    doc.add_heading("7. Open questions and RFIs", level=2)
    open_rows = [row for row in questions if row.get("status") == "open"]
    answered_rows = [row for row in questions if row.get("status") == "answered"]
    for_designer = [row for row in open_rows if row.get("audience") == "designer"]
    for_engineer = [row for row in open_rows if row.get("audience") != "designer"]
    if for_designer:
        doc.add_paragraph("The team needs these from the designer before the work they block can go on:")
        for row in for_designer:
            doc.add_paragraph(f"{row['text']} (raised by {row['raised_by']}) [{row['id']}]", style="List Number")
    if for_engineer:
        doc.add_paragraph("For the engineer of record, the owner, or the authority:")
        for row in for_engineer:
            doc.add_paragraph(f"{row['text']} (raised by {row['raised_by']}) [{row['id']}]", style="List Number")
    if not open_rows:
        doc.add_paragraph("No open questions are on the record.")
    if answered_rows:
        doc.add_paragraph("Answered:")
        for row in answered_rows:
            by = f" (answered by {row['answered_by']})" if row.get("answered_by") else ""
            doc.add_paragraph(f"{row['text']} Answer: {row['answer']}{by} [{row['id']}]", style="List Bullet")

    doc.add_heading("8. Exchanges between agents", level=2)
    if handoffs:
        doc.add_paragraph(
            "A delegation is the lead's brief to a specialist and the summary that came back. A consult is one "
            "specialist's question to another, answered inside the asker's turn. A handoff is work left for later."
        )
        _table(
            doc,
            ["Kind", "From", "To", "Brief", "What came back", "Status", "Created", "Id"],
            [[row.get("kind") or "handoff", row["from_agent"], row["to_agent"], row["brief"],
              _clip(row.get("result"), 500), row["status"], row.get("created") or "", row["id"]] for row in handoffs],
        )
    else:
        doc.add_paragraph("No exchanges between agents are on the record.")

    doc.add_heading("9. Cites on the record", level=2)
    if evidence:
        doc.add_paragraph(
            "Each cite is a contributor's paraphrase with the section it names. held means the contributor says "
            "it read the section in the content pack. It does not mean the standard was opened."
        )
        _table(
            doc,
            ["Document", "Edition", "Section", "Note", "Applies to", "Status", "By", "Id"],
            [[row["document"], row.get("edition") or "", row.get("section") or "", row.get("note") or "",
              row.get("applicability") or "",
              row["status"] + (" OUT OF DATE: the edition changed" if analysis["evidence"][row["id"]]["state"] == coherence.STALE else ""),
              row.get("agent") or "", row["id"]] for row in evidence],
        )
    else:
        doc.add_paragraph("No cites are on the record.")

    doc.add_heading("10. Trace check, claim by claim", level=2)
    rows = (check or {}).get("rows") if isinstance(check, dict) else None
    if rows:
        _table(doc, ["Claim", "Verdict", "Cite", "Why"],
               [[row.get("n"), row.get("verdict"), _clip(row.get("cite"), 900), row.get("reason") or ""] for row in rows])
        if not (check or {}).get("all_supported"):
            doc.add_paragraph(
                "Not every finding is supported by the rows it cites. Those are listed in section 4 under "
                f"\"{checker.TIER_TITLE[checker.TIER_OPEN]}\"."
            )
    else:
        doc.add_paragraph(NO_CHECK_LINE)

    doc.add_heading("11. History: changed inputs and replaced, withdrawn, or out-of-date rows", level=2)
    history: list[str] = []
    for item in analysis["changes"]:
        history.append(f"Input changed: {item['reason']}")
    for row in snapshot.get("retired_findings") or []:
        how = (f"withdrawn: {row.get('retire_note') or ''}" if row.get("superseded_by") == "withdrawn"
               else f"replaced by [{row.get('superseded_by')}]")
        history.append(f"Finding by {row.get('agent')}, {how}: {_clip(row.get('text'), 300)} [{row['id']}]")
    for row in snapshot.get("retired_decisions") or []:
        how = (f"withdrawn: {row.get('retire_note') or ''}" if row.get("superseded_by") == "withdrawn"
               else f"replaced by [{row.get('superseded_by')}]")
        history.append(f"Decision by {row.get('decided_by')}, {how}: {_clip(row.get('text'), 300)} [{row['id']}]")
    for row in calcs:
        item = analysis["calcs"][row["id"]]
        if item["state"] == coherence.STALE:
            history.append(f"Calculation out of date: {row['tool']} by {_who(row)} [{row['id']}]. "
                           + _clip("; ".join(item["reasons"]), 400))
    for row in digest["stale"]:
        if row["kind"] in ("finding", "decision", "cite"):
            history.append(f"OUT OF DATE and still on the record as current: {row['kind']} by {row['by'] or 'the app'} "
                           f"[{row['id']}]: {row['text']}. " + _clip("; ".join(row["reasons"]), 400))
    if history:
        for line in history:
            doc.add_paragraph(line, style="List Bullet")
    else:
        doc.add_paragraph("Nothing on this record was changed, replaced, or withdrawn.")

    doc.add_heading("12. Content the team worked from", level=2)
    context = snapshot.get("context") or {}
    doc.add_paragraph(
        f"Content pack version: {context.get('content_version') or 'unknown'}. "
        f"Content fingerprint: {context.get('content_fingerprint') or 'unknown'}. "
        f"Calc code: {context.get('calc_identity') or 'unknown'}. "
        "The fingerprint is a hash of every method, role, note, and calc file the team could read; two documents "
        "with the same fingerprint were written from the same content."
    )
    used = content_use.skill_use(snapshot, content_root)
    if used:
        doc.add_paragraph(
            "Methods (skills) each contributor read on this job. A read shows the method was in front of the "
            "contributor. It does not show the method was followed; the last column is the only trace of that a "
            "program can see, and it is a weak one."
        )
        _table(
            doc,
            ["Contributor", "Skill", "Read", "Text read (hash)", "Findings recorded after", "Cites it recorded that the skill holds"],
            [[row["agent"], row["slug"],
              ("before its findings" if row["before_findings"] else "AFTER its first finding")
              + (f", {row['reads']} times" if row["reads"] > 1 else ""),
              row["sha256"] + (" (the pack's copy has changed since)" if row["changed"] else ""),
              row["findings_after"],
              "; ".join(" ".join(part for part in (item["document"], item["edition"], item["section"]) if part)
                        for item in row["carried"]) or "none"] for row in used],
        )
    else:
        doc.add_paragraph("No contributor read a skill on this job. Its findings rest on the role files and the tools alone.")
    for agent in content_use.unread(snapshot):
        doc.add_paragraph(f"{agent} recorded findings on this job and read no skill.", style="List Bullet")

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    return path
