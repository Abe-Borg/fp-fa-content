"""The Team tab. Roster, blockers, and the handoff log, read from the project record.

team_view() turns a Record.snapshot() into what the page draws. It holds no
state of its own, so a refresh after any job is one call. Specialist
activity stays collapsed: the handoff table shows one line per exchange,
and the detail pane opens the brief, the payload, and the result for the
selected row.
"""

from __future__ import annotations

import json
from typing import Any

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
    lines.append("Nothing on the record was lost. The Team tab under Zone details shows the state.")
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


def team_view(snapshot: dict | None) -> dict:
    """What the Team tab and the sidebar roster draw for one job's record."""
    roster = roster_lines(snapshot)
    blockers = blocker_lines(snapshot)
    handoffs = []
    for row in (snapshot or {}).get("handoffs") or []:
        handoffs.append({
            "id": str(row.get("id")),
            "when": _time(row.get("created")),
            "from": str(row.get("from_agent") or ""),
            "to": str(row.get("to_agent") or ""),
            "status": f"{HANDOFF_GLYPH.get(row.get('status') or '', '')} {row.get('status') or ''}".strip(),
            "brief": _short(row.get("brief")),
            "detail": handoff_detail(row),
        })
    return {
        "roster": roster,
        "roster_text": "\n".join(roster) if roster else NO_TEAM_LINE,
        "blockers": blockers,
        "blockers_text": ("\n".join(blockers) if blockers else "None open.") + "\n" + check_line(snapshot),
        "check_line": check_line(snapshot),
        "handoffs": handoffs,
    }
