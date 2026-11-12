"""The Team tab. Where the job stands and what the team did, read from the project record.

team_view() turns a Record.snapshot() into what the page draws. It holds no
state of its own, so a refresh after any job is one call.

The view answers, in order, what a person coming back to a job asks: what
the team was asked and how far it got, what it needs from me, what changed
and is now out of date, where the specialists disagree, what each of them
found and how far each finding was taken, and what passed between them.
Every row is a record row. Nothing here is typed by a model, and nothing
here calls one.

The older text fields (roster, blockers, the handoff list) are kept: the
sidebar and the tests read them.
"""

from __future__ import annotations

import json
from typing import Any

from fpfa import checker, content_use, inputs, status
from fpfa.checker import check_line, check_token  # noqa: F401  (check_line is read from here by older callers)

STATUS_GLYPH = {
    "working": "●",
    "done": "✓",
    "error": "!",
    "interrupted": "!",
    "idle": "·",
}
HANDOFF_GLYPH = {
    "pending": "…",
    "delivered": "→",
    "returned": "✓",
    "cancelled": "✕",
}
NO_TEAM_LINE = "No team activity on this job yet. Ask a question and the lead will delegate as needed."


def roster_lines(snapshot: dict | None) -> list[str]:
    """One line per agent: glyph, name, role, status, and what it has written."""
    snap = snapshot or {}
    agents = list(snap.get("agents") or [])
    if not agents:
        return []
    findings = {}
    questions = {}
    for row in snap.get("findings") or []:
        findings[row.get("agent")] = findings.get(row.get("agent"), 0) + 1
    for row in snap.get("questions") or []:
        questions[row.get("raised_by")] = questions.get(row.get("raised_by"), 0) + 1
    lines = []
    for row in agents:
        slug = row.get("role_slug") or ""
        glyph = STATUS_GLYPH.get(row.get("status") or "", "·")
        parts = [f"{glyph} {row.get('name') or slug} ({slug}) {row.get('status') or ''}"]
        count = findings.get(slug, 0)
        asked = questions.get(slug, 0)
        if count:
            parts.append(f"{count} finding{'s' if count != 1 else ''}")
        if asked:
            parts.append(f"{asked} question{'s' if asked != 1 else ''}")
        lines.append(" · ".join(parts))
    return lines


def blocker_lines(snapshot: dict | None) -> list[str]:
    snap = snapshot or {}
    lines = []
    for row in snap.get("questions") or []:
        if row.get("status") == "open":
            lines.append(f"? {row.get('text')} (raised by {row.get('raised_by')})")
    for row in snap.get("handoffs") or []:
        if row.get("status") == "pending":
            requeued = " (re-queued after a relaunch)" if str(row.get("result") or "").startswith("Re-queued") else ""
            lines.append(f"… handoff waiting for {row.get('to_agent')}{requeued}: {row.get('brief')}")
    for row in snap.get("findings") or []:
        if row.get("status") in ("Not supported", "Source not found"):
            lines.append(f"! finding {row.get('status').lower()}: {row.get('text')}")
    for row in snap.get("jobs") or []:
        if row.get("status") == "interrupted":
            title = _short(row.get("title") or "", 60)
            lines.append(f"! {row.get('kind')} job interrupted by a relaunch{': ' + title if title else ''}. Run it again; recorded calcs replay.")
    return lines


def recovery_text(item: dict | None) -> str:
    """The app-written note a thread gets once after a relaunch found work in flight.

    item is one project's entry from Record.recover(). Empty when nothing was touched.
    """
    if not item:
        return ""
    jobs = list(item.get("jobs") or [])
    agents = list(item.get("agents") or [])
    handoffs = list(item.get("handoffs") or [])
    if not jobs and not agents and not handoffs:
        return ""
    lines = ["**Recovered after a relaunch.** The app was not running when this work would have ended."]
    for row in jobs:
        title = _short(row.get("title") or "", 70)
        quoted = f' "{title}"' if title else ""
        lines.append(
            f"- The {row.get('kind')} job{quoted} was interrupted. "
            "Run it again from the thread or the form; calcs already on the record replay instead of recomputing."
        )
    for name in agents:
        lines.append(f"- {name} was interrupted before it returned.")
    for row in handoffs:
        brief = _short(row.get("brief") or "", 70)
        lines.append(
            f"- The handoff from {row.get('from_agent')} to {row.get('to_agent')} ({brief}) was re-queued. "
            f"It is delivered again at the next delegation to {row.get('to_agent')}."
        )
    lines.append("Nothing on the record was lost. The Team tab shows the state.")
    return "\n".join(lines)


def _short(text: Any, limit: int = 90) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _time(text: Any) -> str:
    text = str(text or "")
    return text[11:16] if len(text) >= 16 else text


def handoff_detail(row: dict) -> str:
    """The detail pane for one handoff: who, when, the brief, the payload, and the result."""
    payload = row.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            pass
    lines = [
        f"[{row.get('id')}] {row.get('from_agent')} → {row.get('to_agent')}: {row.get('status')}",
        f"Created {row.get('created') or ''}. Delivered {row.get('delivered') or '—'}. Returned {row.get('returned') or '—'}.",
        "",
        "Brief:",
        str(row.get("brief") or ""),
    ]
    if payload:
        lines += ["", "Payload:", json.dumps(payload, indent=2, sort_keys=True, default=str)]
    if row.get("result"):
        lines += ["", "Result:", str(row.get("result"))]
    return "\n".join(lines)


EXCHANGE_WORD = {"delegation": "brief", "consult": "question", "handoff": "handoff"}
_SOURCE_WORD = {
    "calc": "calculation record",
    "pack": "content-pack note",
    "author": "its author's own note (not in the content pack)",
    "input": "project input",
    "fact": "a fact a contributor recorded, not a project input",
    "finding": "another finding",
    "decision": "a decision the team recorded",
    "missing": "a row that is not on the record",
}


def _rests_on(row: dict, rows: dict[str, dict]) -> list[str]:
    """What a finding cites, one line per row, in words a designer reads."""
    out = []
    for ident in row.get("supports") or []:
        found = rows.get(ident)
        if found is None:
            out.append(f"[{ident}] is not on the record")
        elif found["_kind"] == "calc":
            out.append(f"calculation {found['tool']} [{ident}]")
        elif found["_kind"] == "evidence":
            note = f": {_short(found.get('note'), 140)}" if found.get("note") else ""
            out.append(f"cite {checker.cite_name(found)}{note} [{ident}]")
        elif found["_kind"] == "fact":
            if found.get("kind") == inputs.INPUT_KIND:
                value = inputs.show(found["key"], inputs.decode(found["value"]))
                out.append(f"project input {found['key']}: {_short(value, 80)} [{ident}]")
            else:
                out.append(f"fact {found.get('kind')}/{found.get('key')}: {_short(found.get('value'), 80)} [{ident}]")
        elif found["_kind"] == "decision":
            out.append(f"decision by {found.get('decided_by')}: {_short(found.get('text'), 100)} [{ident}]")
        else:
            out.append(f"finding by {found.get('agent')}: {_short(found.get('text'), 100)} [{ident}]")
    return out


def _checked_lines(item: dict) -> list[str]:
    """What the trace check read for one finding, and why the finding stands where it does."""
    lines = []
    for source in item.get("sources") or []:
        text = f"{_SOURCE_WORD.get(source.get('kind'), source.get('kind'))}: {source.get('text')}"
        if source.get("where"):
            text += " (" + ", ".join(source["where"]) + ")"
        lines.append(text)
    return lines


def finding_rows(snapshot: dict | None) -> list[dict]:
    """Every current finding with its author, its label, what it rests on, and the tier it earned."""
    snap = snapshot or {}
    findings = list(snap.get("findings") or [])
    if not findings:
        return []
    tiers = checker.assurance(snap)
    rows: dict[str, dict] = {}
    for row in snap.get("calcs") or []:
        rows[row["id"]] = dict(row, _kind="calc")
    for row in snap.get("evidence") or []:
        rows[row["id"]] = dict(row, _kind="evidence")
    for row in snap.get("fact_history") or snap.get("facts") or []:
        rows[row["id"]] = dict(row, _kind="fact")
    for row in findings + list(snap.get("retired_findings") or []):
        rows[row["id"]] = dict(row, _kind="finding")
    for row in list(snap.get("decisions") or []) + list(snap.get("retired_decisions") or []):
        rows[row["id"]] = dict(row, _kind="decision")
    reviews: dict[str, list[dict]] = {}
    for row in snap.get("reviews") or []:
        reviews.setdefault(row["finding_id"], []).append(row)
    out = []
    for row in findings:
        item = tiers[row["id"]]
        positions = []
        for review in reviews.get(row["id"], []):
            if review.get("position") == "agree":
                positions.append({"by": review.get("agent") or "", "position": "agrees", "note": review.get("note") or "",
                                  "status": "", "how": ""})
            else:
                positions.append({"by": review.get("agent") or "", "position": "objects", "note": review.get("note") or "",
                                  "status": review.get("status") or "", "how": review.get("resolution") or ""})
        out.append({
            "id": row["id"], "text": row["text"], "label": row["label"], "by": row.get("agent") or "",
            "tier": item["tier"], "tier_title": checker.TIER_TITLE[item["tier"]],
            "verdict": item["verdict"] if item["checked"] else "",
            "rests_on": _rests_on(row, rows), "checked_against": _checked_lines(item),
            "why": list(item["reasons"]), "reviews": positions,
        })
    return out


def _settled(snapshot: dict) -> list[dict]:
    """Objections that have ended, newest last: who objected to what, and how it ended."""
    every = {row["id"]: row for row in list(snapshot.get("findings") or []) + list(snapshot.get("retired_findings") or [])}
    rows = []
    for review in snapshot.get("reviews") or []:
        if review.get("position") != "object" or review.get("status") != "resolved":
            continue
        finding = every.get(review["finding_id"]) or {}
        rows.append({
            "id": review["id"], "by": review.get("agent") or "", "author": finding.get("agent") or "",
            "finding": _short(finding.get("text"), 200), "note": _short(review.get("note"), 400),
            "how": _short(review.get("resolution"), 400),
        })
    return rows


def team_view(snapshot: dict | None, *, export_reason: str | None = None,
              content_root: Any = None) -> dict:
    """What the Team tab, the status strip, and the sidebar roster draw for one job's record."""
    snap = snapshot or {}
    roster = roster_lines(snapshot)
    blockers = blocker_lines(snapshot)
    handoffs = []
    for row in snap.get("handoffs") or []:
        kind = row.get("kind") or "handoff"
        handoffs.append({
            "id": str(row.get("id")),
            "when": _time(row.get("created")),
            "from": str(row.get("from_agent") or ""),
            "to": str(row.get("to_agent") or ""),
            "status": f"{HANDOFF_GLYPH.get(row.get('status') or '', '')} {row.get('status') or ''}".strip(),
            "brief": _short(row.get("brief")),
            "detail": handoff_detail(row),
            "kind": kind,
            "kind_word": EXCHANGE_WORD.get(kind, kind),
        })
    line = check_line(snapshot)
    view = {
        "roster": roster,
        "roster_text": "\n".join(roster) if roster else NO_TEAM_LINE,
        "blockers": blockers,
        "blockers_text": ("\n".join(blockers) if blockers else "None open.") + "\n" + line,
        "check_line": line,
        "handoffs": handoffs,
    }
    if not snapshot:
        view.update({
            "strip": "", "attention": 0, "plan": None, "people": [], "asks": [], "rfis": [], "answered": [],
            "stale": [], "changes": [], "disagreements": [], "conflicts": [], "alternatives": [], "settled": [],
            "tiers": [], "findings": [], "inputs": [], "unconfirmed_line": "", "interrupted": [], "export": None,
            "not_standard": checker.NOT_STANDARD, "partial": [], "retry_line": "", "unchecked": [],
            "coverage": {"complete": False, "gaps": [], "uncovered": []}, "ladder": [], "skills_used": [], "content": {},
        })
        return view
    digest = status.build(snap, export_reason=export_reason)
    findings = finding_rows(snap)
    counts = {tier: 0 for tier in checker.TIERS}
    for row in findings:
        counts[row["tier"]] += 1
    plan = digest["plan"]
    if plan:
        plan = {"objective": plan["objective"],
                "steps": [dict(step, mark=status.STEP_MARK[step["status"]]) for step in plan["steps"]]}
    view.update({
        "strip": status.strip_text(digest, line),
        "attention": status.needs_attention(digest),
        "plan": plan,
        "people": [dict(row, glyph=STATUS_GLYPH.get(row["status"], "·")) for row in digest["people"]],
        "asks": digest["asks"],
        "rfis": digest["rfis"],
        "answered": [{"id": row["id"], "text": row["text"], "answer": row.get("answer") or "",
                      "by": row.get("answered_by") or ""}
                     for row in snap.get("questions") or [] if row.get("status") == "answered"],
        "stale": [{"kind": row["kind"], "id": row["id"], "by": row["by"] or "tool plan", "text": row["text"],
                   "why": "; ".join(row["reasons"][:2])} for row in digest["stale"]],
        "changes": [item["reason"] for item in digest["changes"]],
        "disagreements": digest["objections"],
        "conflicts": [{"key": f"{item['kind']}/{item['key']}",
                       "values": [{"by": row["agent"], "value": str(row["value"])} for row in item["rows"]]}
                      for item in digest["conflicts"]],
        "alternatives": [{"id": row["finding_id"], "by": row["by"], "finding": row["finding"],
                          "why": "; ".join(row["notes"][:2])} for row in digest["alternatives"]],
        "settled": _settled(snap),
        "tiers": [{"tier": tier, "title": checker.TIER_TITLE[tier], "note": checker.TIER_NOTE[tier], "count": counts[tier]}
                  for tier in checker.TIERS],
        "findings": findings,
        "inputs": [{"id": row["id"], "name": row["name"], "text": row["text"], "source": row["source"] or row["by"],
                    "unconfirmed": row["unconfirmed"], "blank": row["blank"]} for row in digest["inputs"]],
        # A zone or basis input still at the form's starting value (NFPA 13 2025, insurer FM): nobody stated it.
        "unconfirmed_line": status.unconfirmed_line(digest),
        "interrupted": [str(row["name"]) for row in digest["interrupted"]],
        # The same agents with what each had recorded when it stopped, and what asking again repeats.
        "partial": [status.partial_text(row) for row in digest["interrupted"]],
        "retry_line": status.RETRY_LINE if digest["interrupted"] or digest["interrupted_jobs"] else "",
        # The page prints each of these after "Not reconciled by the app:". An edition the calculations cite
        # and the job does not state is one of them, said once for the tools that share it.
        "unchecked": [f"{row['tool']} by {row['by'] or 'the app'}: {row['note']}" for row in digest["unchecked"]]
        + list(digest.get("edition_lines") or []),
        "export": digest["export"],
        "not_standard": checker.NOT_STANDARD,
        # What a design basis exported now would be missing, and the kinds of assurance with the two never performed.
        "coverage": checker.coverage(snap) if (snap.get("findings") or snap.get("calcs")) else {"complete": False, "gaps": [], "uncovered": []},
        "ladder": [{"name": name, "what": what, "where": where} for name, what, where in checker.LADDER],
        "skills_used": [dict(row, line=content_use.use_line(row)) for row in content_use.skill_use(snap, content_root)],
        "content": dict(snap.get("context") or {}),
    })
    return view
