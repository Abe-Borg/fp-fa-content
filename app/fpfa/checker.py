"""The trace check over the project record, the tier each finding has earned, and the export gate.

What the check is. Each finding on the record is one claim. The app builds
the claim's cite from the rows the finding names in supports and hands the
checker (the QA role, one blind call) only the claim list and the cites.
The checker says, per claim, whether the cite states it. Then the app
applies rules of its own that no model verdict can override.

What makes it more than a self-check:

- A cite to a standard is looked up in the content pack's own reviewed
  notes (corpus_search.trace_cite). When the pack holds a note on that
  section, the checker judges the claim against the pack's words, not the
  words the claim's author wrote beside the cite. A specialist cannot
  support a wrong claim by writing a matching note.
- Every figure with a unit in a claim has to appear in the rows it cites,
  with that kind of unit: a calc record's figures, the pack note, or a
  project input (fpfa.quantities). This is matching on text and does not
  depend on the model. A 900 ft pipe does not back a 900 gpm claim.
- Low air is never a release input. A claim that says otherwise is not
  supported, whatever it cites and whatever the checker said
  (fpfa.releasing.release_wording_hits). The releasing calc record says
  what the release is.
- A finding whose basis changed is not judged at all. It is out of date.

What it is not. No standard is opened. The pack's notes are paraphrases
the content team reviewed, and the checker is a second pass by the same
model on a blind packet. checked_against_standard is always False. Whether
a claim's meaning, conditions, and applicability follow from what it cites
is the checker's judgment alone; the application's own rules look at
figures, units, and one known wrong statement. The tiers below say how far
each finding was taken, LADDER says which kinds of assurance exist and
which this application never performs, and the export prints both.

Tiers, derived from the record and never typed by a model:

- source     the trace check found it consistent with rows the application
             identified itself: a calc record whose figures match, a
             content-pack note, or a project input.
- reviewed   the trace check found it consistent with a cite its author
             wrote, which the app did not find in the pack.
- stated     produced by a specialist; no check has judged it.
- open       needs further evidence or engineering review: not supported,
             no source, objected to, out of date, or by its label an
             assumption or a judgment for the engineer of record.

Coverage (coverage()) is a separate question from the tiers: whether the
record holds a specialist's statement for each calculation that was run,
and whether anything is still waiting on the team. An export with a gap is
allowed, and says at its head that it is incomplete.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from fpfa import coherence, inputs, quantities, status
from fpfa.corpus_search import trace_cite
from fpfa.record import Record
from fpfa.releasing import LOW_AIR_SUPERVISORY, TRUTH_TABLE_TOOL, reader_view, release_wording_hits, releasing_logic

CHECKER_ROLE = "qa-specialist"
CHECK_EVENT = "record_check"
# A trace check whose request failed. Kept apart from CHECK_EVENT so the last good check stays the latest one.
CHECK_FAILED_EVENT = "check_failed"
# A trace check whose reply was cut off before every claim had a verdict. Its requests were billed and its
# usage is on the event. No finding was changed by it, and it is never the latest check.
CHECK_INCOMPLETE_EVENT = "check_incomplete"
# Claims sent to the checker in one request. On a live job a packet of sixteen claims was about 30,000
# input tokens, and the reply's ceiling covers the model's thinking as well as its verdict lines. A cut-off
# then loses one batch's claims, not the whole check's.
CLAIMS_PER_REQUEST = 8
NO_VERDICT_REASON = "the checker returned no verdict for this claim; it stays not checked"

TIER_SOURCE = "source"
TIER_CHECKER = "checker"
TIER_REVIEWED = "reviewed"
TIER_STATED = "stated"
TIER_OPEN = "open"
TIERS = (TIER_SOURCE, TIER_CHECKER, TIER_REVIEWED, TIER_STATED, TIER_OPEN)
TIER_TITLE = {
    TIER_SOURCE: "Trace-consistent with a row the application identified",
    TIER_CHECKER: "Trace-consistent with an identified row, on the checker's reading alone",
    TIER_REVIEWED: "Trace-consistent with its author's own cite only",
    TIER_STATED: "Stated by a specialist, not checked",
    TIER_OPEN: "Needs further evidence or engineering review",
}
TIER_NOTE = {
    TIER_SOURCE: (
        "The trace check (a second pass by the same AI model) found each of these consistent with a calculation "
        "record, a content-pack note the application looked up, or a project input, and every figure in it is in "
        "those rows with its unit. The row is named beside each. This is consistency with the team's own record. "
        "It is not verification: the standard was not opened, and no engineer has reviewed it."
    ),
    TIER_CHECKER: (
        "The trace check found each of these consistent with a calculation record, a content-pack note, or a "
        "project input. The statement carries no figure, and not the releasing record's own expression, that the "
        "application could hold to those rows itself. So only the checker's reading (a second pass by the same AI "
        "model) connects the words to the row. Whether they follow from it is for the engineer of record."
    ),
    TIER_REVIEWED: (
        "The trace check found each of these consistent with a cite its own author wrote. The application did "
        "not find that section in the content pack, so nothing independent of the author backs the cite."
    ),
    TIER_STATED: "A specialist recorded these. No trace check has judged them.",
    TIER_OPEN: (
        "Not supported by what they cite, without a source, objected to by another specialist, out of date, "
        "or by their label an assumption or a judgment. These are for the engineer of record."
    ),
}
# Every kind of assurance a reader might assume, in order, and whether this application performs it.
# The last two are never performed here, on any finding, and the export says so in a table.
LADDER = (
    ("Specialist output", "A specialist (an AI model in a role) wrote the statement and named the rows it rests on.",
     "Every finding."),
    ("Model review", "Another specialist (the same AI model in another role) agreed or objected.",
     "Where the Agreed-by column or section 5 names a reviewer."),
    ("Trace consistency", "A second pass by the same AI model judged the statement against the rows it cites. "
     "The application also holds each figure, with its unit, to those rows.",
     "Findings in the first three groups of section 4."),
    ("Support from an identified row", "The rows are ones the application found itself: a calculation record, a "
     "content-pack note, or a project input. A content-pack note is the content team's paraphrase.",
     "Findings in the first two groups of section 4. In the first the application itself matched a figure, or "
     "the releasing record's expression, to the row. In the second only the checker's reading connects them."),
    ("Verification against the primary standard", "The adopted standard, the insurer data sheet, or the "
     "manufacturer's listing was opened and the statement checked against its text.",
     "NOT PERFORMED by this application, for any finding."),
    ("Qualified engineering review", "A licensed engineer reviewed the basis and accepted it.",
     "NOT PERFORMED by this application. None is recorded on this job."),
)
PACK_MARK = "CONTENT-PACK NOTE"
AUTHOR_MARK = "AUTHOR'S NOTE (written by the claim's author; not found in the content pack)"
INPUT_MARK = "PROJECT INPUT"
# A fact a contributor wrote to the record: an assumption, an owner standard, a reading. It is not a value
# the designer gave, and the checker is told so.
FACT_MARK = "RECORDED FACT"
GIVEN_LABEL = "GIVEN"
# What stands behind a Supported verdict. "checker": the rows are ones the application identified and it
# could match nothing in the claim to them itself.
BASIS_SOURCE, BASIS_CHECKER, BASIS_AUTHOR = "source", "checker", "author"
CHECKER_ONLY_REASON = (
    "It carries no figure, and not the releasing record's own expression, that the application could hold to "
    "the rows it cites. Only the checker's reading connects it to them."
)
STALE_MARK = "OUT OF DATE"
NOT_STANDARD = "The standards were not opened. Engineer-of-record review still applies."
_JUDGMENT_LABELS = ("ASSUMED", "use best judgment")

# A figure the check can verify: a number followed by an engineering unit (fpfa.quantities).
_FIGURE = quantities.FIGURE
_ANY_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])")
RELEASE_WORDING_REASON = (
    "the releasing calculation record says the release is the detection leg AND P, and "
    + LOW_AIR_SUPERVISORY[0].lower() + LOW_AIR_SUPERVISORY[1:] + " This finding says otherwise."
)


def _claim_check():
    """claim_check imports workflow, which imports everyday. Imported late to keep the cycle open."""
    from fpfa import claim_check

    return claim_check


# -- figures -----------------------------------------------------------------------------

def _normal(number: str) -> str:
    """A number as text, so 38,400 and 38400.0 and 38400 compare equal."""
    return quantities.normal(number)


def figures(text: str) -> list[str]:
    """The figures in a claim the check can verify: numbers that carry an engineering unit."""
    return [number for number, _unit in _figures_with_units(text)]


def _figures_with_units(text: str) -> list[tuple[str, str]]:
    cleaned = _strip_cites(text)
    return [(_normal(match.group(1)), match.group(2).lower()) for match in _FIGURE.finditer(cleaned)]


def _claim_figures(text: str) -> list[tuple[str, str, str]]:
    """Every figure a claim states, for the trace check: (number, the unit as written, its class).

    Wider than figures(): any unit the application knows, a number written
    out in words before a unit, and the dotted spellings (fpfa.quantities).
    The reply audit keeps the narrower reading.
    """
    return quantities.claim_figures(_strip_cites(text))


def _strip_cites(text: str) -> str:
    """A claim without its document and section tokens, so NFPA 13 is not read as the figure 13."""
    out = re.sub(r"(?i)\b(?:NFPA|IBC|IFC|NBC|NFC|NEC|UL)\s*\d+[A-Z]?(?:-\d{4})?", " ", text or "")
    out = re.sub(r"(?i)\bFM\s+(?:DS\s+)?\d{1,2}-\d{1,3}[A-Z]?", " ", out)
    out = re.sub(r"(?i)\bDS\s+\d{1,2}-\d{1,3}[A-Z]?", " ", out)
    out = re.sub(r"(?i)(?:§|\bsection\s+|\btable\s+|(?<![A-Za-z])s(?=\d))\s*\d+(?:\.\d+)*(?:\([A-Za-z0-9]+\))*", " ", out)
    out = re.sub(r"\[[0-9a-f]{16}\]", " ", out)
    return out


def _numbers_in(text: str) -> set[str]:
    return {_normal(match.group(1)) for match in _ANY_NUMBER.finditer(text or "")}


def _calc_numbers(tool: str, outputs: Any, calc_inputs: Any) -> set[str]:
    """Every number a calc record holds, in the forms a sentence would print it."""
    claim_check = _claim_check()
    tokens = claim_check._package_number_tokens({tool: outputs, "inputs": calc_inputs})
    return {_normal(token) for token in tokens}


def _calc_quantities(outputs: Any, calc_inputs: Any) -> set:
    """A calc record's figures, each with the unit its field names. Its notes and formulas are not figures."""
    return quantities.in_value(outputs, strings=False) | quantities.in_value(calc_inputs, strings=False)


def _text_quantities(text: Any) -> set:
    return quantities.in_text(_strip_cites(str(text or "")))


def _pairs(have: set) -> list[list]:
    """A set of quantities as JSON keeps it: sorted [number, class] pairs."""
    return sorted(([number, cls] for number, cls in have), key=lambda item: (item[0], item[1] or ""))


# -- the packet --------------------------------------------------------------------------

def cite_name(row: dict) -> str:
    """A cite as a reader writes it: NFPA 13-2025 §8.3.2.3.1.1, or NFPA 13-2025 Table 19.2.3.1.2."""
    edition = f"-{row['edition']}" if row.get("edition") else ""
    section = str(row.get("section") or "").strip()
    if section:
        section = (" " if section[:1].isalpha() or section.startswith("§") else " §") + section
    return f"{row.get('document') or ''}{edition}{section}"


def check_token(findings: list[dict]) -> str:
    payload = json.dumps(
        [[row["id"], row["text"], row["label"], row.get("supports") or []] for row in findings],
        sort_keys=True, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _cite_for(content_root: Path | None, rows: dict[str, dict], finding: dict, analysis: dict) -> dict:
    """The cite the checker reads for one finding, and what the application knows about it.

    Returns {"cite", "open", "basis", "numbers", "sources", "note"}. basis is
    "source" when every support is a calc record, a pack note the app found,
    or a project input; "author" when a cite rests on its author's note alone.
    numbers are the figures the cited rows hold. sources names each support
    for the reader.
    """
    claim_check = _claim_check()
    pieces: list[str] = []
    sources: list[dict] = []
    numbers: set[str] = set()
    held: set = set()
    author_notes: list[str] = []
    expressions: list[str] = []
    open_cite = False
    author_only = False
    for ident in finding.get("supports") or []:
        row = rows.get(ident)
        if row is None:
            open_cite = True
            sources.append({"id": ident, "kind": "missing", "text": "not on the record"})
            continue
        kind = row["_kind"]
        if kind == "calc":
            shown = claim_check._package_figures({row["tool"]: row["outputs"]})
            stated = _calc_text(row["tool"], row["outputs"])
            pieces.append(f"{claim_check.PACKAGE_MARK}. {row['tool']}: {stated + '. ' if stated else ''}{shown}")
            numbers |= _calc_numbers(row["tool"], row["outputs"], row.get("inputs"))
            held |= _calc_quantities(row["outputs"], row.get("inputs"))
            if row["tool"] == TRUTH_TABLE_TOOL:
                # The one thing a releasing record holds that is not a figure: its own logic expression.
                expression = releasing_logic(row["outputs"])["expression"]
                if expression:
                    expressions.append(expression)
            state = analysis["calcs"].get(ident, {})
            label = "calculation record"
            if state.get("state") == coherence.ALTERNATIVE:
                label = "calculation record on another value than the project input"
            elif not state.get("tracked"):
                label = "calculation record, not tied to the project inputs"
            sources.append({"id": ident, "kind": "calc", "text": f"{row['tool']} ({label})"})
        elif kind == "evidence":
            where = cite_name(row)
            passages = trace_cite(content_root, row["document"], row.get("edition") or "", row.get("section") or "") \
                if content_root is not None else []
            # NEEDS HOLD is the content team's own stop and stays one. NOT PULLED is the author saying
            # it did not hold the text: that stays open unless the pack itself holds a note on the section.
            if row.get("status") == "NEEDS HOLD" or (row.get("status") == "NOT PULLED" and not passages):
                open_cite = True
            if passages:
                quoted = " | ".join(f"({item['path']}:{item['line']}) {item['text']}" for item in passages)
                pieces.append(f"{where}. {PACK_MARK}: {quoted}")
                for item in passages:
                    # The figures this cite can carry are the ones the pack gives for this section,
                    # not every figure in the paragraph around it.
                    numbers |= _numbers_in(_strip_cites(item.get("scope") or item["text"]))
                    held |= _text_quantities(item.get("scope") or item["text"])
                sources.append({"id": ident, "kind": "pack", "text": where,
                                "where": [f"{item['path']}:{item['line']}" for item in passages]})
            else:
                note = str(row.get("note") or "").strip()
                pieces.append(f"{where}. {AUTHOR_MARK}: {note or '(no note)'} [{row['status']}]")
                numbers |= _numbers_in(_strip_cites(note))
                held |= _text_quantities(note)
                author_only = True
                author_notes.append(note)
                sources.append({"id": ident, "kind": "author", "text": where})
        elif kind == "fact":
            if row.get("kind") == inputs.INPUT_KIND:
                value = inputs.show(row["key"], inputs.decode(row["value"]))
            else:
                value = str(row.get("value"))
            source = row.get("source") or row.get("agent") or ""
            is_input = row.get("kind") == inputs.INPUT_KIND or (
                row.get("kind") == inputs.BASIS_KIND and row.get("key") in inputs.BASIS_FIELDS)
            if is_input or str(row.get("label") or "").upper() == GIVEN_LABEL:
                # A zone input, a basis field, or a value the lead recorded as the designer's own words.
                pieces.append(f"{INPUT_MARK} {row['key']}: {value} ({row['label']}; {source})")
                numbers |= _numbers_in(value)
                if row.get("kind") == inputs.INPUT_KIND:
                    held |= quantities.in_value(inputs.decode(row["value"]), row["key"], strings=False)
                # As the input is shown, with the unit the form gives it.
                held |= quantities.in_text(value)
                sources.append({"id": ident, "kind": "input", "text": f"{row['key']}: {value}"})
            else:
                # A fact a contributor wrote: an assumption, an owner standard, a reading. It is the team's
                # own statement, like a finding, and adds no independent source. Packaged as a project input
                # it told the checker the designer gave it, and a specialist could back a claim with a fact
                # it had written a moment before.
                writer = row.get("agent") or "a contributor"
                pieces.append(f"{FACT_MARK} {row.get('kind')}/{row['key']}: {value} ({row['label']}; recorded by {writer})")
                numbers |= _numbers_in(_strip_cites(value))
                held |= _text_quantities(value)
                author_only = True
                if writer == finding.get("agent"):
                    # The claim's own author wrote it. A claim that only says it back is not supported by it.
                    author_notes.append(value)
                sources.append({"id": ident, "kind": "fact",
                                "text": f"{row.get('kind')}/{row['key']}: {_clip(value, 120)} (recorded by {writer})"})
        elif kind == "finding":
            pieces.append(f"FINDING by {row['agent']}: {row['text']} [{row['status']}]")
            numbers |= _numbers_in(_strip_cites(row["text"]))
            held |= _text_quantities(row["text"])
            # A finding is the team's own statement. Resting on one adds no independent source.
            author_only = True
            author_notes.append(str(row["text"]))
            sources.append({"id": ident, "kind": "finding", "text": f"finding by {row['agent']}"})
        elif kind == "decision":
            # An election or a judgment the team recorded. Like a finding it is the team's own statement:
            # it is on the record, so the claim is not without a source, and it adds no independent one.
            basis = f" Basis: {row['basis']}" if row.get("basis") else ""
            pieces.append(f"DECISION by {row.get('decided_by') or 'the team'}: {row['text']}{basis} [{row.get('label') or ''}]")
            numbers |= _numbers_in(_strip_cites(row["text"]))
            held |= _text_quantities(row["text"])
            author_only = True
            author_notes.append(str(row["text"]))
            sources.append({"id": ident, "kind": "decision", "text": f"decision by {row.get('decided_by') or 'the team'}"})
    if not pieces:
        return {"cite": claim_check.OPEN_MARK, "open": True, "basis": "none", "numbers": set(), "held": set(),
                "sources": sources, "author_notes": [], "expressions": []}
    return {
        "cite": " | ".join(pieces), "open": open_cite, "basis": BASIS_AUTHOR if author_only else BASIS_SOURCE,
        "numbers": numbers, "held": held, "sources": sources, "author_notes": author_notes,
        "expressions": expressions,
    }


def build_record_packet(record: Record, project_id: str, content_root: Path | None = None) -> dict:
    """Claims from the record's findings; cites from the rows they name, looked up in the pack where they can be."""
    snapshot = record.snapshot(project_id)
    analysis = coherence.analyze(snapshot)
    findings = list(snapshot["findings"])
    rows: dict[str, dict] = {}
    for row in snapshot["calcs"]:
        rows[row["id"]] = dict(row, _kind="calc")
    for row in snapshot["evidence"]:
        rows[row["id"]] = dict(row, _kind="evidence")
    for row in snapshot["facts"]:
        rows[row["id"]] = dict(row, _kind="fact")
    for row in findings:
        rows[row["id"]] = dict(row, _kind="finding")
    for row in snapshot.get("decisions") or []:
        # A finding may rest on a decision. Left out of this index it read as "not on the record".
        rows[row["id"]] = dict(row, _kind="decision")
    claims: list[str] = []
    sources: list[str] = []
    meta: list[dict] = []
    for index, finding in enumerate(findings, start=1):
        standing = analysis["findings"].get(finding["id"], {})
        stale = standing.get("state") == coherence.STALE
        if stale:
            cite = {"cite": f"{STALE_MARK}: " + "; ".join(standing.get("reasons") or [])[:400], "open": True,
                    "basis": "none", "numbers": set(), "held": set(), "sources": [], "author_notes": [],
                    "expressions": []}
        else:
            cite = _cite_for(content_root, rows, finding, analysis)
        claims.append(f"{index}. {finding['text'].rstrip('.')}.")
        sources.append(f"{index}. {cite['cite']}")
        meta.append({
            "n": index, "finding_id": finding["id"], "open": cite["open"], "stale": stale,
            "calc_only": cite["basis"] == "source" and all(item["kind"] == "calc" for item in cite["sources"]),
            "basis": cite["basis"], "numbers": sorted(cite["numbers"]), "held": _pairs(cite["held"]),
            "sources": cite["sources"], "expressions": cite["expressions"],
            "author_notes": cite["author_notes"], "requirement": finding["text"], "cite": cite["cite"],
        })
    return {
        "claims": "\n".join(claims),
        "sources": "\n".join(sources),
        "claim_count": len(findings),
        "meta": meta,
        "token": check_token(findings),
    }


def _missing_figures(requirement: str, numbers: list[str], held: list | None = None) -> list[str]:
    """Figures in the claim that none of its cited rows hold.

    numbers are the cited rows' numbers alone. held, when given, are the same
    rows' numbers with the unit each is kept in ([number, class] pairs): a
    figure then has to be held as that kind of quantity, so a length does
    not back a flow. Without held the lookup is by number alone.
    """
    if held is not None:
        have = {(str(number), cls) for number, cls in held}
        return [f"{number} {unit}" for number, unit, cls in _claim_figures(requirement)
                if not quantities.holds(number, cls or None, have)]
    have_numbers = set(numbers)
    missing = []
    for number, unit in _figures_with_units(requirement):
        if number in have_numbers:
            continue
        if unit in ("%", "percent"):
            # A row may hold the same share as a fraction: 30 percent is 0.3.
            try:
                if _normal(str(float(number) / 100.0)) in have_numbers:
                    continue
            except ValueError:
                pass
        missing.append(f"{number} {unit}")
    return missing


def _wrong_unit(requirement: str, numbers: list[str], held: list) -> list[str]:
    """Of the figures the cited rows do not hold as that quantity, the ones they hold as something else."""
    have_numbers = set(numbers) | {str(number) for number, _cls in held}
    return [item for item in _missing_figures(requirement, numbers, held) if item.split()[0] in have_numbers]


def _calc_text(tool: str, outputs: Any) -> str:
    """What a calc record states, in words the checker can judge a claim against: its short outputs and flags."""
    view = reader_view(tool, outputs)
    if not isinstance(view, dict):
        return ""
    parts: list[str] = []
    for key, value in view.items():
        if key in ("formula", "record_id"):
            continue
        if isinstance(value, bool):
            parts.append(f"{key}={str(value).lower()}")
        elif isinstance(value, (int, float)):
            parts.append(f"{key}={value:g}")
        elif isinstance(value, str) and value.strip():
            parts.append(f"{key}: {_clip(value, 260)}")
        elif key == "flags" and isinstance(value, list):
            flags = "; ".join(str(item) for item in value if isinstance(item, str))
            if flags:
                parts.append("flags: " + _clip(flags, 500))
    return _clip("; ".join(parts), 1600)


def _clip(text: str, limit: int) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def check_record(content_root: Path, record: Record, project_id: str, create: Callable[..., Any]) -> dict:
    """The trace check over the record. Verdicts are written back onto the findings."""
    claim_check = _claim_check()
    started = time.time()
    packet = build_record_packet(record, project_id, content_root)
    if not packet["claim_count"]:
        outcome = {
            "rows": [], "all_supported": False, "claim_count": 0, "token": packet["token"],
            "status_line": "Trace check: the record has no findings to check.",
            "block_reason": "The record has no findings to check.",
            "checked_against_standard": False,
        }
        record.log_event(project_id, CHECK_EVENT, outcome, agent=CHECKER_ROLE)
        return outcome
    from fpfa.claude_client import attach_usage, empty_usage, incomplete_notice, safe_error

    system = claim_check.checker_system(content_root)
    usage = empty_usage()
    # By claim number: what the checker said. A claim it said nothing about has no entry, and no entry is
    # never read as a verdict.
    words: dict[int, str] = {}
    cut_off: dict | None = None
    try:
        for batch in _batches(packet["meta"]):
            reply = claim_check.ask(create, system, _batch_request(claim_check, batch))
            for field, value in reply["usage"].items():
                usage[field] = int(usage.get(field, 0)) + int(value or 0)
            said_here = claim_check._verdict_words(reply["text"])
            for position, item in enumerate(batch, start=1):
                if position in said_here:
                    words[item["n"]] = said_here[position]
            silent = [item["n"] for item in batch
                      if item["n"] not in words and _without_checker(claim_check, item) is None]
            if silent and (incomplete_notice(reply["stop_reason"]) or not reply["text"].strip()):
                # The reply ran into its ceiling, was declined, or held no text. What it did not say about
                # these claims is not a verdict, and the batches after it are not sent: the check as a
                # whole cannot speak for the findings now.
                cut_off = {"stop_reason": reply["stop_reason"], "claims": silent}
                break
    except Exception as exc:
        # The batches that finished were billed, whatever ended this one. The request that failed returned
        # no usage. Nothing was judged, and the last good check stands as it was.
        attach_usage(exc, usage)
        spent = dict(getattr(exc, "usage", None) or {})
        cancelled = type(exc).__name__ == "TurnCancelled"
        if not cancelled or spent.get("rounds"):
            record.log_event(project_id, CHECK_FAILED_EVENT, {
                "failed": not cancelled, "cancelled": cancelled, "error": safe_error(exc)[:400], "usage": spent,
                "claim_count": packet["claim_count"], "seconds": round(time.time() - started, 1),
            }, agent=CHECKER_ROLE)
        raise
    if cut_off is not None:
        return _incomplete(record, project_id, packet, usage, cut_off, words, started, claim_check)
    rows: list[dict] = []
    # Where the application's own rules set aside what the checker said. A checker that approves a claim
    # the rules catch is a checker to distrust on the claims no rule covers.
    overruled: list[dict] = []
    for item in packet["meta"]:
        reason = ""
        decided = _without_checker(claim_check, item)
        if decided is not None:
            verdict, reason = decided
        elif item["n"] not in words:
            # The reply finished and skipped this claim. It is not a "no": the finding goes back to not
            # checked, and the row says why.
            verdict = claim_check.VERDICT_NONE
            reason = NO_VERDICT_REASON
        else:
            verdict = words[item["n"]]
            if verdict not in (claim_check.VERDICT_SUPPORTED, claim_check.VERDICT_NOT, claim_check.VERDICT_OPEN):
                verdict = claim_check.VERDICT_NOT
            said = verdict
            missing = _missing_figures(item["requirement"], item["numbers"], item["held"])
            if release_wording_hits(item["requirement"]):
                # A known wrong statement about the release. No cite and no verdict stands against the rule.
                verdict = claim_check.VERDICT_NOT
                reason = RELEASE_WORDING_REASON
            elif verdict == claim_check.VERDICT_SUPPORTED and missing:
                # No verdict stands against the arithmetic: a figure in the claim is not in what it cites.
                verdict = claim_check.VERDICT_NOT
                other = _wrong_unit(item["requirement"], item["numbers"], item["held"])
                reason = "figure not in the rows it cites: " + ", ".join(missing)
                if other:
                    reason += ". The rows hold " + ", ".join(text.split()[0] for text in other) + " only as another quantity"
            if verdict != said:
                overruled.append({"n": item["n"], "finding_id": item["finding_id"], "checker_said": said})
        basis, matched = "", []
        if verdict == claim_check.VERDICT_SUPPORTED:
            basis = item["basis"]
            # What the application itself could hold to the cited rows. Every figure in a supported claim is
            # held, or the verdict would not have stood, so a claim with a figure has one.
            matched = _held_by_app(item)
            if basis == BASIS_SOURCE and not matched:
                # The rows are ones the application identified, and nothing in the claim could be matched to
                # them by the application. Only the checker's word connects the two.
                basis = BASIS_CHECKER
                reason = CHECKER_ONLY_REASON
        rows.append({
            "n": item["n"], "finding_id": item["finding_id"], "verdict": verdict,
            "cite": item["cite"].replace('"', "'"), "basis": basis, "held_by_app": matched,
            "sources": item["sources"], "reason": reason,
        })
        # A finding the checker said nothing about goes back to "open", which is where it started: an
        # earlier check's verdict must not stand in for this one's silence.
        record.set_finding_status(
            project_id, item["finding_id"],
            status="open" if verdict == claim_check.VERDICT_NONE else verdict, by=CHECKER_ROLE)
    supported = [row for row in rows if row["verdict"] == claim_check.VERDICT_SUPPORTED]
    on_source = sum(1 for row in supported if row["basis"] == BASIS_SOURCE)
    on_checker = sum(1 for row in supported if row["basis"] == BASIS_CHECKER)
    on_author = len(supported) - on_source - on_checker
    no_word = [row for row in rows if row["verdict"] == claim_check.VERDICT_NONE]
    not_ok = [row for row in rows if row["verdict"] not in (claim_check.VERDICT_SUPPORTED, claim_check.VERDICT_NONE)]
    all_supported = bool(rows) and not not_ok and not no_word
    split = (f"{on_source} against a calculation record, a content-pack note, or a project input, "
             f"{on_author} against a cite their author wrote")
    if on_checker:
        split += f", {on_checker} against such a row on the checker's reading alone"
    if overruled:
        split += (f"; the application's own rules set aside the checker's verdict on "
                  f"{len(overruled)} finding{'s' if len(overruled) != 1 else ''}")
    if all_supported:
        status_line = (
            f"Trace check: all {len(rows)} findings are consistent with the rows they cite ({split}). "
            + NOT_STANDARD
        )
        block_reason = ""
    else:
        status_line = f"Trace check: {len(supported)} of {len(rows)} findings are consistent with the rows they cite ({split}). "
        if not_ok:
            status_line += "Not supported or without a source: " + ", ".join(str(row["n"]) for row in not_ok) + ". "
        if no_word:
            status_line += ("The checker returned no verdict for: " + ", ".join(str(row["n"]) for row in no_word)
                            + "; they stay not checked. ")
        status_line += NOT_STANDARD
        block_reason = status_line
    outcome = {
        "usage": usage,
        "seconds": round(time.time() - started, 1),
        "rows": rows,
        "all_supported": all_supported,
        "claim_count": len(rows),
        "supported": len(supported),
        "on_source": on_source,
        "on_checker": on_checker,
        "on_author": on_author,
        "token": packet["token"],
        "status_line": status_line,
        "block_reason": block_reason,
        "checked_against_standard": False,
        "overruled": overruled,
        "content": dict(snapshot_context(record, project_id)),
        "verdict": "\n".join(
            f'{row["n"]}. {row["verdict"]}. Cite: "{_clip(row["cite"], 320)}"' + (f" ({row['reason']})" if row["reason"] else "")
            for row in rows
        ),
    }
    record.log_event(project_id, CHECK_EVENT, outcome, agent=CHECKER_ROLE)
    return outcome


def _plain(text: str) -> str:
    """Text as two spellings of one expression compare equal: no code marks, one case, single spaces."""
    return " ".join(str(text or "").replace("`", " ").lower().split())


def _held_by_app(item: dict) -> list[str]:
    """What in a claim the application itself can hold to the rows it cites. Empty when nothing can be.

    Its figures, each with its unit, and the releasing record's own logic
    expression when the claim quotes it (whole, or the part after the equals
    sign). A claim with neither states something the application has no way
    to match: whatever the checker says of it rests on the checker alone.
    """
    found = [f"{number} {unit}" for number, unit, _cls in _claim_figures(item["requirement"])]
    said = _plain(item["requirement"])
    for expression in item.get("expressions") or []:
        whole = _plain(expression)
        body = _plain(expression.split("=", 1)[1]) if "=" in expression else whole
        if whole and (whole in said or (body and body in said)):
            found.append("the releasing record's expression")
            break
    return found


def _batches(meta: list[dict]) -> list[list[dict]]:
    """The claims in the order they stand, CLAIMS_PER_REQUEST to a request."""
    return [meta[start:start + CLAIMS_PER_REQUEST] for start in range(0, len(meta), CLAIMS_PER_REQUEST)]


def _batch_request(claim_check, batch: list[dict]) -> str:
    """The checker's two files for one batch, numbered from 1 so every request reads the same way.

    A record with one batch sends exactly the claims and cites build_record_packet numbered.
    """
    claims = "\n".join(f"{position}. {item['requirement'].rstrip('.')}." for position, item in enumerate(batch, start=1))
    sources = "\n".join(f"{position}. {item['cite']}" for position, item in enumerate(batch, start=1))
    return claim_check.checker_request(claims, sources)


def _without_checker(claim_check, item: dict) -> tuple[str, str] | None:
    """The verdict the application gives a claim itself, whatever the checker says. None when it gives none."""
    if item["stale"]:
        return claim_check.VERDICT_OPEN, "its basis changed; it is out of date"
    if item["open"]:
        return claim_check.VERDICT_OPEN, "no source on the record, or the cite was not pulled"
    if any(claim_check._echoes(item["requirement"], note) for note in item["author_notes"]):
        # Only a note the claim's own author wrote can be the claim said back. A pack note
        # that states the claim word for word is what support looks like.
        return claim_check.VERDICT_NOT, "its author's note only repeats the claim"
    return None


def _incomplete(record: Record, project_id: str, packet: dict, usage: dict, cut_off: dict, words: dict,
                started: float, claim_check) -> dict:
    """Close a trace check whose reply was cut off. Nothing is written to a finding.

    The check speaks for the findings it saw or for none of them: a verdict
    on half the record beside an older check's on the rest would read as one
    check. So the verdict lines that did come back are counted and dropped,
    the usage is kept, and the last complete check stays the latest one.
    """
    waiting = [item["n"] for item in packet["meta"]
               if item["n"] not in words and _without_checker(claim_check, item) is None]
    stop_reason = str(cut_off.get("stop_reason") or "")
    why = f"stop_reason {stop_reason}" if stop_reason and stop_reason != "end_turn" else "the reply held no text"
    count = packet["claim_count"]
    status_line = (
        f"Trace check did not finish: the checker's reply was cut off ({why}) with no verdict on "
        f"{len(waiting)} of {count} finding{'s' if count != 1 else ''}. No finding was changed, and the last complete "
        "check, if there was one, stands as it was. Run the trace check again."
    )
    outcome = {
        "incomplete": True, "usage": usage, "seconds": round(time.time() - started, 1), "rows": [],
        "all_supported": False, "claim_count": count, "unjudged": waiting, "cut_off_at": list(cut_off.get("claims") or []),
        "stop_reason": stop_reason, "token": packet["token"], "status_line": status_line, "block_reason": status_line,
        "checked_against_standard": False,
    }
    record.log_event(project_id, CHECK_INCOMPLETE_EVENT, outcome, agent=CHECKER_ROLE)
    return outcome


def snapshot_context(record: Record, project_id: str | None = None) -> dict:
    """What was installed when a check ran: the pack's version and fingerprint and the calc code's identity."""
    return dict(getattr(record, "context", None) or {})


def latest_check(record: Record, project_id: str) -> dict | None:
    event = record.latest_event(project_id, CHECK_EVENT)
    return event["payload"] if event else None


def _latest_check_in(snapshot: dict | None) -> dict | None:
    found = ((snapshot or {}).get("latest") or {}).get(CHECK_EVENT)
    if found is None:
        for row in (snapshot or {}).get("events") or []:
            if row.get("kind") == CHECK_EVENT:
                found = row
    return (found.get("payload") or {}) if found else None


def check_is_current(snapshot: dict | None) -> bool:
    payload = _latest_check_in(snapshot)
    if not payload or payload.get("token") != check_token(list((snapshot or {}).get("findings") or [])):
        return False
    was = str((payload.get("content") or {}).get("content_fingerprint") or "")
    now = str(((snapshot or {}).get("context") or {}).get("content_fingerprint") or "")
    return not (was and now and was != now)


def _newest(snapshot: dict | None, kind: str) -> dict | None:
    """The newest event of one kind a snapshot carries: from its latest table, else from its recent window."""
    found = ((snapshot or {}).get("latest") or {}).get(kind)
    if found is None:
        for row in (snapshot or {}).get("events") or []:
            if row.get("kind") == kind:
                found = row
    return found


def unfinished_check(snapshot: dict | None) -> str:
    """Why the newest trace check gave no verdicts, when it came after the last complete one. Else "".

    A check that was cut off, or whose request failed, changed nothing. A
    view that only knew the last complete check would say "not run" or "run
    it again" with no word on why the run just made left nothing behind.
    """
    done = _newest(snapshot, CHECK_EVENT)
    done_seq = int((done or {}).get("seq") or 0)
    newest: dict | None = None
    for kind in (CHECK_INCOMPLETE_EVENT, CHECK_FAILED_EVENT):
        event = _newest(snapshot, kind)
        if event is not None and int(event.get("seq") or 0) > max(done_seq, int((newest or {}).get("seq") or 0)):
            newest = event
    if newest is None:
        return ""
    payload = newest.get("payload") or {}
    if newest.get("kind") == CHECK_INCOMPLETE_EVENT:
        stop_reason = str(payload.get("stop_reason") or "")
        why = f"stop_reason {stop_reason}" if stop_reason and stop_reason != "end_turn" else "the reply held no text"
        return f"the last run did not finish: the checker's reply was cut off ({why})"
    if payload.get("cancelled"):
        return "the last run was cancelled before it finished"
    return "the last run failed before it returned (" + _clip(payload.get("error") or "no reason recorded", 160) + ")"


def check_line(snapshot: dict | None) -> str:
    """One line on the trace check for the panel and the lead. It speaks for the findings the check saw."""
    snap = snapshot or {}
    payload = _latest_check_in(snap)
    unfinished = "" if check_is_current(snap) else unfinished_check(snap)
    if unfinished and snap.get("findings"):
        return f"Trace check: {unfinished}. No finding was changed. Run it again."
    if payload is None:
        if snap.get("findings"):
            return "Trace check: not run on the current findings."
        return "Trace check: nothing to check yet."
    # A check speaks for the findings it saw. New or changed findings need a new one.
    if payload.get("token") and payload.get("token") != check_token(list(snap.get("findings") or [])):
        return "Trace check: findings changed since the last check. Run it again."
    was = str((payload.get("content") or {}).get("content_fingerprint") or "")
    now = str((snap.get("context") or {}).get("content_fingerprint") or "")
    if was and now and was != now:
        return "Trace check: the content pack changed since the last check. Run it again."
    return str(payload.get("status_line") or "Trace check ran.")


def summary_line(outcome: dict | None) -> str:
    """The check in a few words for the block under a lead reply."""
    if (outcome or {}).get("incomplete"):
        stop_reason = str(outcome.get("stop_reason") or "")
        why = f" (stop_reason {stop_reason})" if stop_reason and stop_reason != "end_turn" else ""
        return f"trace check: did not finish{why}; no finding was changed. Run it again."
    rows = (outcome or {}).get("rows") or []
    if not rows:
        return "trace check: nothing to check"
    supported = sum(1 for row in rows if row.get("verdict") == "Supported")
    on_source = sum(1 for row in rows if row.get("verdict") == "Supported" and row.get("basis") == BASIS_SOURCE)
    on_checker = sum(1 for row in rows if row.get("verdict") == "Supported" and row.get("basis") == BASIS_CHECKER)
    text = f"trace check: {supported} of {len(rows)} findings consistent with what they cite"
    if supported:
        text += (f" ({on_source} against a calc record, a pack note, or an input; "
                 f"{supported - on_source - on_checker} against the author's own cite")
        if on_checker:
            text += f"; {on_checker} against such a row on the checker's reading alone"
        text += ")"
    return text + ". The standards were not opened."


# -- tiers -------------------------------------------------------------------------------

def assurance(snapshot: dict | None, check: dict | None = None) -> dict[str, dict]:
    """The tier each current finding has earned, with the reasons a reader needs.

    Returns {finding id: {"tier", "reasons", "sources", "verdict", "checked"}}.
    Derived from the finding's label, its checker verdict, the open objections
    on it, and whether its basis changed. Nothing here is typed by a model.
    check is the trace check to read the sources from; None reads the newest
    one the snapshot carries.
    """
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    payload = check if isinstance(check, dict) else (_latest_check_in(snap) or {})
    by_finding = {row.get("finding_id"): row for row in payload.get("rows") or []}
    calcs = {row["id"]: row for row in snap.get("calcs") or []}
    objections: dict[str, list[dict]] = {}
    agreements: dict[str, list[str]] = {}
    for row in snap.get("reviews") or []:
        if row.get("position") == "object" and row.get("status") in ("open", "escalated"):
            objections.setdefault(row["finding_id"], []).append(row)
        elif row.get("position") == "agree":
            agreements.setdefault(row["finding_id"], []).append(row.get("agent") or "")
    out: dict[str, dict] = {}
    for finding in snap.get("findings") or []:
        ident = finding["id"]
        verdict = finding.get("status") or "open"
        seen = by_finding.get(ident) or {}
        reasons: list[str] = []
        standing = analysis["findings"].get(ident, {})
        if standing.get("state") == coherence.STALE:
            tier = TIER_OPEN
            reasons.append("Out of date: " + "; ".join(standing.get("reasons") or [])[:400])
        elif objections.get(ident):
            tier = TIER_OPEN
            for row in objections[ident]:
                mark = " (escalated)" if row.get("status") == "escalated" else ""
                reasons.append(f"{row.get('agent')} objects{mark}: {row.get('note')}")
        elif verdict == "Not supported":
            tier = TIER_OPEN
            reasons.append("The trace check did not support it" + (f": {seen['reason']}" if seen.get("reason") else "") + ".")
        elif verdict == "Source not found":
            tier = TIER_OPEN
            reasons.append("No source on the record" + (f": {seen['reason']}" if seen.get("reason") else "") + ".")
        elif verdict == "Supported":
            basis = seen.get("basis") or BASIS_AUTHOR
            if basis == BASIS_SOURCE and "held_by_app" not in seen:
                # A check made before the application kept what it had matched itself. Worked out again
                # here from the finding and the releasing records it cites, so an old check cannot keep a
                # statement with nothing matched in the first group.
                expressions = [releasing_logic(calcs[item].get("outputs"))["expression"]
                               for item in finding.get("supports") or []
                               if item in calcs and calcs[item].get("tool") == TRUTH_TABLE_TOOL]
                if not _held_by_app({"requirement": finding.get("text") or "", "expressions": expressions}):
                    basis = BASIS_CHECKER
            tier = {BASIS_SOURCE: TIER_SOURCE, BASIS_CHECKER: TIER_CHECKER}.get(basis, TIER_REVIEWED)
            if tier == TIER_CHECKER:
                reasons.append(CHECKER_ONLY_REASON)
            if finding.get("label") in _JUDGMENT_LABELS:
                # Consistent with what it cites, and still an assumption or a judgment by its own label.
                tier = TIER_OPEN
                kind = "an assumption" if finding["label"] == "ASSUMED" else "a judgment the tools did not return"
                reasons.append(f"It is {kind}. The trace check found it consistent with what it cites; "
                               "the engineer of record confirms it.")
        else:
            tier = TIER_STATED
            if seen.get("verdict") == "No verdict":
                reasons.append("The trace check returned no verdict for it, so it stays not checked.")
            if finding.get("label") in _JUDGMENT_LABELS:
                tier = TIER_OPEN
                kind = "an assumption" if finding["label"] == "ASSUMED" else "a judgment the tools did not return"
                reasons.append(f"It is {kind}, and no trace check has judged it.")
        for note in standing.get("notes") or []:
            reasons.append("Alternative: " + note)
        for note in standing.get("unchecked") or []:
            reasons.append("Not reconciled by the application: " + note)
        if standing.get("unchecked") and tier in (TIER_SOURCE, TIER_CHECKER, TIER_REVIEWED):
            # Consistent with a row the record cannot vouch for any more. It goes to the engineer.
            tier = TIER_OPEN
        out[ident] = {
            "tier": tier, "reasons": reasons, "verdict": verdict,
            "sources": seen.get("sources") or [], "checked": verdict != "open",
            "agreed_by": sorted(set(agreements.get(ident) or [])),
        }
    return out


def tier_counts(snapshot: dict | None) -> dict[str, int]:
    counts = {tier: 0 for tier in TIERS}
    for item in assurance(snapshot).values():
        counts[item["tier"]] += 1
    return counts


# -- coverage ------------------------------------------------------------------------------

# A calc tool in a reader's words, for the line that says no finding speaks for it.
_TOOL_WORDS = {
    "zone_trapped_volume": "the trapped volume",
    "dry_delivery_screen": "the pipe timing and the size exemption",
    "di_trip_to_water": "the delivery-time screen",
    "density_area": "the sprinkler demand",
    "hose_duration": "the hose stream and duration",
    "nitrogen_gate": "the supervisory gas fill and design C",
    "elect_di_trim": "the trim family",
    "releasing_truth_table": "the releasing logic",
    "lfl_setpoints": "the gas detection setpoints",
}
# Lookups a finding is not expected to speak for by themselves.
_HELPER_TOOLS = frozenset({"resolve_pipe_id"})
# A handoff addressed to the lead is a note the lead reads in its status block. Nothing delivers it, so it
# never leaves pending, and it is not work waiting on a specialist.
LEAD_AGENT = "lead"
COMPLETE_LINE = (
    "Coverage: every calculation on this record has a specialist's finding, the plan's steps are done, no "
    "handoff is waiting for a specialist, and nothing else is waiting on the team. That is a statement about the record, not about the design. The table "
    "below says what kind of checking each statement had, and what kind it did not."
)
INCOMPLETE_HEAD = "INCOMPLETE DRAFT. This document does not yet cover the whole design basis:"


def coverage(snapshot: dict | None) -> dict:
    """What a design basis written from this record would be missing. Derived; no model is asked.

    Returns {"complete", "gaps", "uncovered"}. gaps are sentences for the
    reader. uncovered are the calc tools whose current result no current
    finding or decision rests on, directly or through a calculation that took
    a figure from it: the work was computed and no specialist has said what
    it means. A record with nothing on it is not complete either.

    This does not know what a design basis ought to contain. It knows what
    was computed, what the lead planned, and what is still open, and it
    reports the distance between those and what was stated. A team that
    computes less is not caught here; the plan the lead set is the only
    statement of intent the record holds.
    """
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    digest = status.build(snap)
    calcs = {row["id"]: row for row in snap.get("calcs") or []}
    findings = [row for row in snap.get("findings") or []
                if analysis["findings"].get(row["id"], {}).get("state") != coherence.STALE]
    decisions = [row for row in snap.get("decisions") or []
                 if analysis["decisions"].get(row["id"], {}).get("state") != coherence.STALE]
    spoken: set[str] = set()
    queue = [ident for row in findings + decisions for ident in row.get("supports") or [] if ident in calcs]
    while queue:
        ident = queue.pop()
        if ident in spoken:
            continue
        spoken.add(ident)
        queue.extend(dep for dep in calcs[ident].get("depends") or [] if dep in calcs)
    by_tool: dict[str, list[str]] = {}
    for ident, row in calcs.items():
        if analysis["calcs"][ident]["state"] == coherence.CURRENT and row.get("tool") not in _HELPER_TOOLS:
            by_tool.setdefault(row["tool"], []).append(ident)
    # A calculation that only feeds another one is spoken for, or not, with the one it feeds.
    feeds = {dep for row in calcs.values() if analysis["calcs"][row["id"]]["state"] == coherence.CURRENT
             for dep in row.get("depends") or [] if dep in calcs}
    uncovered = [tool for tool, ids in by_tool.items()
                 if not any(ident in spoken for ident in ids) and not all(ident in feeds for ident in ids)]
    gaps: list[str] = []
    if not calcs and not findings:
        gaps.append("Nothing has been calculated or stated on this job yet.")
    elif not findings:
        gaps.append("No specialist has stated a finding. The figures below are the tool plan's alone, with "
                    "nobody's reading of what they mean.")
    for tool in uncovered:
        if not findings:
            break
        gaps.append(f"No finding rests on {_TOOL_WORDS.get(tool, tool)} ({tool}). It was calculated and no "
                    "specialist has stated what follows from it.")
    plan = digest.get("plan")
    for step in (plan or {}).get("steps") or []:
        if step["status"] != "done":
            owner = f", {step['owner']}" if step["owner"] else ""
            gaps.append(f"Plan step not finished: {step['title']} ({step['status']}{owner}).")
    for row in digest["interrupted"]:
        how = "stopped on an error" if row.get("status") == "error" else "was interrupted"
        gaps.append(f"{row['name']} {how} before it finished. What it had recorded is kept and may be partial.")
    if digest["objections"] or digest["conflicts"]:
        count = len(digest["objections"]) + len(digest["conflicts"])
        gaps.append(f"{count} disagreement{'s' if count != 1 else ''} between contributors "
                    f"{'are' if count != 1 else 'is'} not settled.")
    if digest["asks"]:
        count = len(digest["asks"])
        gaps.append(f"{count} question{'s' if count != 1 else ''} the team put to the designer "
                    f"{'are' if count != 1 else 'is'} not answered.")
    waiting = [row for row in digest["pending"] if row.get("to") != LEAD_AGENT]
    if waiting:
        count = len(waiting)
        who = ", ".join(sorted({str(row.get("to") or "") for row in waiting}))
        gaps.append(f"{count} handoff{'s' if count != 1 else ''} {'are' if count != 1 else 'is'} waiting for {who}: "
                    "work one contributor left for another has not been picked up.")
    if digest["unchecked"]:
        count = len(digest["unchecked"])
        gaps.append(f"{count} calculation{'s' if count != 1 else ''} the application cannot reconcile after an "
                    "input change: the tool is not tied to the project inputs. Check by hand or run again.")
    for line in digest.get("edition_lines") or []:
        # The cites of a calculation name another edition of a standard than the job states.
        gaps.append(line)
    if digest["stale"]:
        count = len(digest["stale"])
        gaps.append(f"{count} row{'s' if count != 1 else ''} on the record {'are' if count != 1 else 'is'} out of date.")
    return {"complete": not gaps, "gaps": gaps, "uncovered": uncovered}


def coverage_lines(snapshot: dict | None) -> list[str]:
    """The coverage gaps as the lead's status block and /status carry them. Empty when there are none."""
    found = coverage(snapshot)
    if found["complete"] or not ((snapshot or {}).get("findings") or (snapshot or {}).get("calcs")):
        return []
    return ["Not yet covered. A design basis written now would be incomplete, and must say so:"] + [
        f"- {gap}" for gap in found["gaps"]]


# -- the export gate -----------------------------------------------------------------------

def export_gate(record: Record, project_id: str) -> str:
    """Empty when the design basis may be exported. Otherwise the reason it waits.

    The export prints the tier every finding has earned, so it does not wait
    for every finding to be supported: an unsupported finding is exported
    under "needs further evidence or engineering review", where the engineer
    of record can see it. It does wait for two things that would make the
    document misstate where the job stands. Nothing on the record may be out
    of date. And when the record has findings, a trace check must have judged
    exactly the findings that are there now.
    """
    return export_reason(record.snapshot(project_id))


def export_reason(snapshot: dict | None) -> str:
    """export_gate for a snapshot the caller already holds."""
    snapshot = snapshot or {}
    digest = status.build(snapshot)
    if digest["stale"]:
        changed = "; ".join(item["reason"] for item in digest["changes"][:3])
        count = len(digest["stale"])
        return (
            f"{count} row{'s' if count != 1 else ''} on the record {'are' if count != 1 else 'is'} out of date"
            + (f" ({changed})" if changed else "")
            + ". Run the zone again, or ask the lead to bring the findings up to date. /status lists them."
        )
    findings = list(snapshot.get("findings") or [])
    if not findings:
        return ""
    check = _latest_check_in(snapshot)
    unfinished = "" if check_is_current(snapshot) else unfinished_check(snapshot)
    if unfinished:
        # The run that was just made left nothing behind. Say why, not only that a check is wanted.
        return (f"The trace check has not judged the findings as they are now: {unfinished}. "
                "Ask the lead to run it again, or press Run trace check.")
    if not check:
        return "The record has findings that no trace check has judged. Ask the lead to run it, or press Run trace check."
    if check.get("token") != check_token(findings):
        return "Findings changed after the last trace check. Run it again."
    was = str((check.get("content") or {}).get("content_fingerprint") or "")
    now = str((snapshot.get("context") or {}).get("content_fingerprint") or "")
    if was and now and was != now:
        # A cite is read in the content pack. A check made against other content speaks for that content.
        return "The content pack changed after the last trace check. Run it again."
    return ""
