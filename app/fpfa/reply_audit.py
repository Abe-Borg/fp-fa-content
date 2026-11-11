"""Check the figures in the lead's reply against what it could have read them from.

The lead does not compute. Every figure with a unit that it tells the
designer should come from somewhere: a calculation record, a project
input, a statement a specialist put on the record, a tool result it read
this turn, the content pack text in its own instructions, or the
designer's own words. This module looks each figure up in those places.

Three things come out, and the window prints them under the reply in the
application's words:

- unfound: figures that appear in none of those places. The lead most
  likely worked them out or misremembered them.
- stale: figures the record holds only on rows that are no longer current:
  a calculation an input changed under, the value an input had before it
  changed, a finding or a decision that is out of date, replaced, or
  withdrawn.
- wording: sentences that depart from the releasing rule, under which low
  air is never a release input (fpfa.releasing.release_wording_hits).

Where a figure may be read from, in three ranks:

1. Current rows: a calculation record that is not out of date, a project
   input as it stands, the content pack text, a calc or content tool the
   lead called this turn, and the designer's own words in this turn's
   message.
2. Out-of-date rows, as listed under stale above.
3. The team's own statements and the conversation: a current finding, a
   decision, a cite's note, a question, what a record or team tool returned
   this turn, the designer's earlier messages, and the lead's earlier replies.

A figure on rank 1 is found. A figure that is on rank 2 and not on rank 1
is out of date, whatever rank 3 says: a finding that still repeats the old
number cannot make it current, and neither can the lead having said it
before. Only a figure on neither rank 1 nor rank 2 is looked up on rank 3.

It is matching on text. No model is called, and nothing here decides
whether a figure is right. The lookup is by number and the kind of unit it
carries (fpfa.quantities): 900 gpm is not found on a 900 ft pipe. It is
still found on a 900 with no unit beside it, because nothing says what
that is. A figure that is found is only known to match a number the
designer can go and look at. A reply that recounts a change ("it was 600
gpm") is flagged like one that still uses the old value; the note under
the reply says only that the figure is not the current basis, which is
true of both.
"""

from __future__ import annotations

import json
from typing import Any

from fpfa import coherence, inputs, quantities
from fpfa.checker import _figures_with_units, _normal, _strip_cites
from fpfa.releasing import release_wording_hits

AUDIT_EVENT = "reply_audit"
_MAX_LISTED = 8
# Tools whose results are the record or the team said back: what they return may be out of date.
# Everything else the lead can call is a calc tool or a content-pack lookup.
_SAID_BACK_TOOLS = frozenset({
    "read_record", "record_fact", "record_evidence", "record_finding", "withdraw_finding", "review_finding",
    "open_question", "record_decision", "handoff", "list_specialists", "delegate", "request_check", "set_input",
    "answer_question", "set_plan", "resolve_disagreement",
})


def _text_numbers(text: Any) -> set:
    """Every number in prose with the kind of unit written after it."""
    return quantities.in_text(_strip_cites(str(text or "")))


def _walk_numbers(value: Any, found: set, name: str | None = None) -> None:
    """Every number in a stored value: numeric fields with the unit their name gives, and the numbers in its strings."""
    found |= quantities.in_value(value, name, prose=_strip_cites, loose=True)


def record_numbers(snapshot: dict | None) -> tuple[set, set]:
    """(quantities on current calculation records and inputs, quantities on out-of-date rows).

    The team's own statements are not in either set (statement_numbers). A
    finding that is out of date, or that was replaced or withdrawn, counts
    with the out-of-date rows: it cannot keep its own figures current by
    staying on the record.
    """
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    current: set = set()
    old: set = set()
    for row in snap.get("calcs") or []:
        numbers: set = set()
        _walk_numbers(row.get("outputs"), numbers)
        _walk_numbers(row.get("inputs"), numbers)
        if analysis["calcs"].get(row["id"], {}).get("state") == coherence.STALE:
            old |= numbers
        else:
            current |= numbers
    stated = {row["id"] for row in snap.get("facts") or []}
    for row in snap.get("facts") or []:
        if row.get("kind") == inputs.INPUT_KIND:
            value = inputs.decode(row.get("value"))
            _walk_numbers(value, current, row.get("key"))
            # As the form shows it, with the unit the form gives it.
            current |= quantities.in_text(inputs.show(row["key"], value))
        elif row.get("kind") == inputs.BASIS_KIND or row.get("label") == inputs.GIVEN:
            current |= _text_numbers(row.get("value"))
    # What an input was before it changed, and what it was before the designer emptied it.
    for row in snap.get("fact_history") or []:
        if row["id"] in stated or not analysis["facts"].get(row["id"], {}).get("changed"):
            continue
        if row.get("kind") == inputs.INPUT_KIND:
            value = inputs.decode(row.get("value"))
            _walk_numbers(value, old, row.get("key"))
            old |= quantities.in_text(inputs.show(row["key"], value))
        else:
            old |= _text_numbers(row.get("value"))
    for row in snap.get("findings") or []:
        if analysis["findings"].get(row["id"], {}).get("state") == coherence.STALE:
            old |= _text_numbers(row.get("text"))
    for row in snap.get("decisions") or []:
        if analysis["decisions"].get(row["id"], {}).get("state") == coherence.STALE:
            old |= _text_numbers(row.get("text")) | _text_numbers(row.get("basis"))
    for row in snap.get("retired_findings") or []:
        old |= _text_numbers(row.get("text"))
    for row in snap.get("retired_decisions") or []:
        old |= _text_numbers(row.get("text")) | _text_numbers(row.get("basis"))
    for row in snap.get("evidence") or []:
        if analysis["evidence"].get(row["id"], {}).get("state") == coherence.STALE:
            old |= _text_numbers(row.get("note"))
    return current, old


def statement_numbers(snapshot: dict | None) -> set:
    """Quantities in what the team itself wrote and still stands by: findings, decisions, cites, questions, facts."""
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    found: set = set()
    for row in snap.get("facts") or []:
        if row.get("kind") not in (inputs.INPUT_KIND, inputs.BASIS_KIND) and row.get("label") != inputs.GIVEN:
            found |= _text_numbers(row.get("value"))
    for row in snap.get("findings") or []:
        if analysis["findings"].get(row["id"], {}).get("state") != coherence.STALE:
            found |= _text_numbers(row.get("text"))
    for row in snap.get("decisions") or []:
        if analysis["decisions"].get(row["id"], {}).get("state") != coherence.STALE:
            found |= _text_numbers(row.get("text")) | _text_numbers(row.get("basis"))
    for row in snap.get("evidence") or []:
        if analysis["evidence"].get(row["id"], {}).get("state") != coherence.STALE:
            found |= _text_numbers(row.get("note"))
    for row in snap.get("questions") or []:
        found |= _text_numbers(row.get("text")) | _text_numbers(row.get("answer"))
    return found


def _has(number: str, unit: str, have: set) -> bool:
    return quantities.has(number, unit, have)


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
    """Look up every figure with a unit in reply. Returns {"figures", "unfound", "stale", "wording"}.

    tool_calls are the turn's own tool results (run_tool_loop's "tool_calls").
    said is what the designer wrote: this turn's message first, then the
    earlier ones. pack_text is the content-pack text in the lead's
    instructions. earlier_replies are the lead's earlier answers; a figure
    repeated from one counts as found unless it was flagged then
    (flagged_before) or the record now holds it only on out-of-date rows.
    """
    wording = [sentence for _line, sentence in release_wording_hits(reply or "")]
    figures = _figures_with_units(reply or "")
    if not figures:
        return {"figures": 0, "unfound": [], "stale": [], "wording": wording}
    current, old = record_numbers(snapshot)
    said = list(said or [])
    loose: set = statement_numbers(snapshot)
    for call in tool_calls or []:
        if call.get("is_error"):
            continue
        # A calc or a content lookup the lead ran this turn is as current as anything gets. What a record
        # or team tool hands back is the record said back, out-of-date rows included.
        _walk_numbers(call.get("output"), loose if call.get("name") in _SAID_BACK_TOOLS else current)
    if said:
        current |= _text_numbers(said[0])
    for text in said[1:]:
        loose |= _text_numbers(text)
    if pack_text:
        current |= _text_numbers(pack_text)
    flagged = {_normal(item.split()[0]) for item in flagged_before or [] if item.split()}
    repeated: set = set()
    for text in earlier_replies or []:
        repeated |= {item for item in _text_numbers(text) if item[0] not in flagged}
    unfound: list[str] = []
    stale: list[str] = []
    for number, unit in figures:
        shown = f"{number} {unit}"
        if _has(number, unit, current):
            continue
        if _has(number, unit, old):
            if shown not in stale:
                stale.append(shown)
            continue
        if _has(number, unit, loose) or _has(number, unit, repeated):
            continue
        if shown not in unfound:
            unfound.append(shown)
    return {"figures": len(figures), "unfound": unfound, "stale": stale, "wording": wording}


def flagged_before(record: Any, project_id: str) -> list[str]:
    """Figures an earlier audit on this job could not find, or found only on out-of-date rows."""
    found: list[str] = []
    for event in record.events_by_kind(project_id, (AUDIT_EVENT,)):
        payload = event.get("payload") or {}
        for item in list(payload.get("unfound") or []) + list(payload.get("stale") or []):
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
    wording = result.get("wording") or []
    if stale:
        more = f" and {len(stale) - _MAX_LISTED} more" if len(stale) > _MAX_LISTED else ""
        out.append(
            "- figures in this reply that the record now holds only on out-of-date rows: "
            + ", ".join(stale[:_MAX_LISTED]) + more
            + ". An input changed after they were written, or the finding that carried them was replaced or "
            "withdrawn. They are not the current basis. Do not use them as current."
        )
    if unfound:
        more = f" and {len(unfound) - _MAX_LISTED} more" if len(unfound) > _MAX_LISTED else ""
        out.append(
            "- figures in this reply the application could not find on the record or in anything the lead read: "
            + ", ".join(unfound[:_MAX_LISTED]) + more
            + ". Treat them as unverified."
        )
    if wording:
        out.append(
            "- a sentence in this reply departs from the releasing logic on the calculation record: \""
            + _clip(wording[0], 200) + "\""
            + (f" and {len(wording) - 1} more" if len(wording) > 1 else "")
            + ". The record's logic is the detection leg AND P. Low air is supervisory only and is never a "
            "release input. Do not act on that sentence."
        )
    return out


def _clip(text: str, limit: int) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def to_json(result: dict) -> str:
    return json.dumps(result, sort_keys=True)
