"""Check the figures in the lead's reply against what it could have read them from.

The lead does not compute. Every figure with a unit that it tells the
designer should come from somewhere: a calculation record, a project
input, a statement a specialist put on the record, a tool result it read
this turn, the content pack text in its own instructions, or the
designer's own words. This module looks each figure up in those places.

Two things come out, and the window prints both under the reply in the
application's words:

- unfound: figures that appear in none of those places. The lead most
  likely worked them out or misremembered them.
- stale: figures found only on calculation records that are out of date,
  because an input changed after they ran.

It is arithmetic on text. No model is called, and nothing here decides
whether a figure is right. The lookup is by number and not by quantity, so
900 gpm is found if a 900 ft pipe is on the record. A figure that is found
is only known to match a number the designer can go and look at; one that
is not found matches nothing at all, which is the case worth a warning.
"""

from __future__ import annotations

import json
from typing import Any

from fpfa import coherence, inputs
from fpfa.checker import _calc_numbers, _figures_with_units, _normal, _numbers_in, _strip_cites

AUDIT_EVENT = "reply_audit"
_MAX_LISTED = 8


def _text_numbers(text: Any) -> set[str]:
    return _numbers_in(_strip_cites(str(text or "")))


def _walk_numbers(value: Any, found: set[str]) -> None:
    """Every number in a tool result: numeric values, and the numbers written in its strings."""
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        # As a sentence would print it: in full, or rounded to a whole, one, or two decimals.
        found.add(_normal(repr(abs(float(value)))))
        for places in (0, 1, 2):
            found.add(_normal(f"{abs(float(value)):.{places}f}"))
        return
    if isinstance(value, str):
        found |= _text_numbers(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _walk_numbers(item, found)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _walk_numbers(item, found)


def record_numbers(snapshot: dict | None) -> tuple[set[str], set[str]]:
    """(numbers on current rows, numbers only on out-of-date calculation records)."""
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    current: set[str] = set()
    old: set[str] = set()
    for row in snap.get("calcs") or []:
        numbers = _calc_numbers(row.get("tool") or "", row.get("outputs"), row.get("inputs"))
        _walk_numbers(row.get("outputs"), numbers)
        if analysis["calcs"].get(row["id"], {}).get("state") == coherence.STALE:
            old |= numbers
        else:
            current |= numbers
    for row in snap.get("facts") or []:
        if row.get("kind") == inputs.INPUT_KIND:
            _walk_numbers(inputs.decode(row.get("value")), current)
        else:
            current |= _text_numbers(row.get("value"))
    for row in snap.get("findings") or []:
        current |= _text_numbers(row.get("text"))
    for row in snap.get("decisions") or []:
        current |= _text_numbers(row.get("text")) | _text_numbers(row.get("basis"))
    for row in snap.get("evidence") or []:
        current |= _text_numbers(row.get("note"))
    for row in snap.get("questions") or []:
        current |= _text_numbers(row.get("text")) | _text_numbers(row.get("answer"))
    return current, old - current


def _has(number: str, unit: str, have: set[str]) -> bool:
    if number in have:
        return True
    if unit in ("%", "percent"):
        # A row may hold the same share as a fraction: 30 percent is 0.3.
        try:
            return _normal(str(float(number) / 100.0)) in have
        except ValueError:
            return False
    return False


def audit(
    reply: str,
    snapshot: dict | None,
    *,
    tool_calls: list[dict] | None = None,
    said: list[str] | None = None,
    pack_text: str = "",
    earlier_replies: list[str] | None = None,
    flagged_before: list[str] | None = None,
) -> dict:
    """Look up every figure with a unit in reply. Returns {"figures", "unfound", "stale"}.

    tool_calls are the turn's own tool results (run_tool_loop's "tool_calls").
    said is what the designer wrote, this turn and before. pack_text is the
    content-pack text in the lead's instructions. earlier_replies are the
    lead's earlier answers; a figure repeated from one counts as found unless
    it was flagged then (flagged_before).
    """
    figures = _figures_with_units(reply or "")
    if not figures:
        return {"figures": 0, "unfound": [], "stale": []}
    current, old = record_numbers(snapshot)
    seen: set[str] = set()
    for call in tool_calls or []:
        if not call.get("is_error"):
            _walk_numbers(call.get("output"), seen)
    for text in said or []:
        seen |= _text_numbers(text)
    if pack_text:
        seen |= _text_numbers(pack_text)
    repeated: set[str] = set()
    for text in earlier_replies or []:
        repeated |= _text_numbers(text)
    repeated -= {_normal(item.split()[0]) for item in flagged_before or [] if item.split()}
    unfound: list[str] = []
    stale: list[str] = []
    for number, unit in figures:
        shown = f"{number} {unit}"
        if _has(number, unit, current) or _has(number, unit, seen):
            continue
        if _has(number, unit, old):
            if shown not in stale:
                stale.append(shown)
            continue
        if _has(number, unit, repeated):
            continue
        if shown not in unfound:
            unfound.append(shown)
    return {"figures": len(figures), "unfound": unfound, "stale": stale}


def flagged_before(record: Any, project_id: str) -> list[str]:
    """Figures an earlier audit on this job could not find."""
    found: list[str] = []
    for event in record.events_by_kind(project_id, (AUDIT_EVENT,)):
        for item in (event.get("payload") or {}).get("unfound") or []:
            if item not in found:
                found.append(item)
    return found


def lines(result: dict | None) -> list[str]:
    """What the window says under the reply. Empty when every figure was found on something current."""
    if not result:
        return []
    out: list[str] = []
    stale = result.get("stale") or []
    unfound = result.get("unfound") or []
    if stale:
        more = f" and {len(stale) - _MAX_LISTED} more" if len(stale) > _MAX_LISTED else ""
        out.append(
            "- figures in this reply that are only on out-of-date calculations: "
            + ", ".join(stale[:_MAX_LISTED]) + more
            + ". An input changed after they ran. Do not use them."
        )
    if unfound:
        more = f" and {len(unfound) - _MAX_LISTED} more" if len(unfound) > _MAX_LISTED else ""
        out.append(
            "- figures in this reply the application could not find on the record or in anything the lead read: "
            + ", ".join(unfound[:_MAX_LISTED]) + more
            + ". Treat them as unverified."
        )
    return out


def to_json(result: dict) -> str:
    return json.dumps(result, sort_keys=True)
