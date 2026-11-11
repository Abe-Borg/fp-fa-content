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
- Every figure with a unit in a claim has to appear in the rows it cites: a
  calc record's figures, the pack note, or a project input. This is
  arithmetic on text and does not depend on the model.
- A finding whose basis changed is not judged at all. It is out of date.

What it is not. No standard is opened. The pack's notes are paraphrases
the content team reviewed, and the checker is a second pass by the same
model on a blind packet. checked_against_standard is always False. The
tiers below say exactly how far each finding was taken, and the export
prints them.

Tiers, derived from the record and never typed by a model:

- source     checked against an identified source: a calc record whose
             figures match, a content-pack note, or a project input.
- reviewed   the checker found it consistent with a cite its author wrote,
             which the app did not find in the pack.
- stated     produced by a specialist; no check has judged it.
- open       needs further evidence or engineering review: not supported,
             no source, objected to, out of date, or by its label an
             assumption or a judgment for the engineer of record.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from fpfa import coherence, inputs, status
from fpfa.corpus_search import trace_cite
from fpfa.record import Record
from fpfa.releasing import reader_view

CHECKER_ROLE = "qa-specialist"
CHECK_EVENT = "record_check"

TIER_SOURCE = "source"
TIER_REVIEWED = "reviewed"
TIER_STATED = "stated"
TIER_OPEN = "open"
TIERS = (TIER_SOURCE, TIER_REVIEWED, TIER_STATED, TIER_OPEN)
TIER_TITLE = {
    TIER_SOURCE: "Checked against an identified source",
    TIER_REVIEWED: "Reviewed by the checker",
    TIER_STATED: "Produced by a specialist, not reviewed",
    TIER_OPEN: "Needs further evidence or engineering review",
}
TIER_NOTE = {
    TIER_SOURCE: (
        "The trace check found each of these consistent with a calculation record, a content-pack note the "
        "application looked up, or a project input. The source is named beside each. The standard itself was not opened."
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
PACK_MARK = "CONTENT-PACK NOTE"
AUTHOR_MARK = "AUTHOR'S NOTE (written by the claim's author; not found in the content pack)"
INPUT_MARK = "PROJECT INPUT"
STALE_MARK = "OUT OF DATE"
NOT_STANDARD = "The standards were not opened. Engineer-of-record review still applies."
_JUDGMENT_LABELS = ("ASSUMED", "use best judgment")

# A figure the check can verify: a number followed by an engineering unit.
_FIGURE = re.compile(
    r"(?<![\w.§-])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(gallons?|gal|gpm|psig|psi|scfm|seconds?|sec|s|minutes?|min|ft2|ft²|sq\s*ft|percent|%)(?![\w²])",
    re.IGNORECASE,
)
_ANY_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])")


def _claim_check():
    """claim_check imports workflow, which imports everyday. Imported late to keep the cycle open."""
    from fpfa import claim_check

    return claim_check


# -- figures -----------------------------------------------------------------------------

def _normal(number: str) -> str:
    """A number as text, so 38,400 and 38400.0 and 38400 compare equal."""
    text = number.replace(",", "")
    try:
        value = float(text)
    except ValueError:
        return text
    return f"{value:.10g}"


def figures(text: str) -> list[str]:
    """The figures in a claim the check can verify: numbers that carry an engineering unit."""
    return [number for number, _unit in _figures_with_units(text)]


def _figures_with_units(text: str) -> list[tuple[str, str]]:
    cleaned = _strip_cites(text)
    return [(_normal(match.group(1)), match.group(2).lower()) for match in _FIGURE.finditer(cleaned)]


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


# -- the packet --------------------------------------------------------------------------

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
    author_notes: list[str] = []
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
            state = analysis["calcs"].get(ident, {})
            label = "calculation record"
            if state.get("state") == coherence.ALTERNATIVE:
                label = "calculation record on another value than the project input"
            sources.append({"id": ident, "kind": "calc", "text": f"{row['tool']} ({label})"})
        elif kind == "evidence":
            edition = f"-{row['edition']}" if row.get("edition") else ""
            section = f" §{row['section']}" if row.get("section") else ""
            where = f"{row['document']}{edition}{section}"
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
                    numbers |= _numbers_in(_strip_cites(item["text"]))
                sources.append({"id": ident, "kind": "pack", "text": where,
                                "where": [f"{item['path']}:{item['line']}" for item in passages]})
            else:
                note = str(row.get("note") or "").strip()
                pieces.append(f"{where}. {AUTHOR_MARK}: {note or '(no note)'} [{row['status']}]")
                numbers |= _numbers_in(_strip_cites(note))
                author_only = True
                author_notes.append(note)
                sources.append({"id": ident, "kind": "author", "text": where})
        elif kind == "fact":
            if row.get("kind") == inputs.INPUT_KIND:
                value = inputs.show(row["key"], inputs.decode(row["value"]))
            else:
                value = str(row.get("value"))
            source = row.get("source") or row.get("agent") or ""
            pieces.append(f"{INPUT_MARK} {row['key']}: {value} ({row['label']}; {source})")
            numbers |= _numbers_in(value)
            sources.append({"id": ident, "kind": "input", "text": f"{row['key']}: {value}"})
        elif kind == "finding":
            pieces.append(f"FINDING by {row['agent']}: {row['text']} [{row['status']}]")
            numbers |= _numbers_in(_strip_cites(row["text"]))
            # A finding is the team's own statement. Resting on one adds no independent source.
            author_only = True
            author_notes.append(str(row["text"]))
            sources.append({"id": ident, "kind": "finding", "text": f"finding by {row['agent']}"})
    if not pieces:
        return {"cite": claim_check.OPEN_MARK, "open": True, "basis": "none", "numbers": set(), "sources": sources,
                "author_notes": []}
    return {
        "cite": " | ".join(pieces), "open": open_cite, "basis": "author" if author_only else "source",
        "numbers": numbers, "sources": sources, "author_notes": author_notes,
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
    claims: list[str] = []
    sources: list[str] = []
    meta: list[dict] = []
    for index, finding in enumerate(findings, start=1):
        standing = analysis["findings"].get(finding["id"], {})
        stale = standing.get("state") == coherence.STALE
        if stale:
            cite = {"cite": f"{STALE_MARK}: " + "; ".join(standing.get("reasons") or [])[:400], "open": True,
                    "basis": "none", "numbers": set(), "sources": [], "author_notes": []}
        else:
            cite = _cite_for(content_root, rows, finding, analysis)
        claims.append(f"{index}. {finding['text'].rstrip('.')}.")
        sources.append(f"{index}. {cite['cite']}")
        meta.append({
            "n": index, "finding_id": finding["id"], "open": cite["open"], "stale": stale,
            "calc_only": cite["basis"] == "source" and all(item["kind"] == "calc" for item in cite["sources"]),
            "basis": cite["basis"], "numbers": sorted(cite["numbers"]), "sources": cite["sources"],
            "author_notes": cite["author_notes"], "requirement": finding["text"], "cite": cite["cite"],
        })
    return {
        "claims": "\n".join(claims),
        "sources": "\n".join(sources),
        "claim_count": len(findings),
        "meta": meta,
        "token": check_token(findings),
    }


def _missing_figures(requirement: str, numbers: list[str]) -> list[str]:
    """Figures in the claim that none of its cited rows hold."""
    have = set(numbers)
    missing = []
    for number, unit in _figures_with_units(requirement):
        if number in have:
            continue
        if unit in ("%", "percent"):
            # A row may hold the same share as a fraction: 30 percent is 0.3.
            try:
                if _normal(str(float(number) / 100.0)) in have:
                    continue
            except ValueError:
                pass
        missing.append(f"{number} {unit}")
    return missing


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
    system = claim_check.checker_system(content_root)
    model_text, usage = claim_check._ask_usage(
        create, system, claim_check.checker_request(packet["claims"], packet["sources"])
    )
    words = claim_check._verdict_words(model_text)
    rows: list[dict] = []
    for item in packet["meta"]:
        reason = ""
        if item["stale"]:
            verdict = claim_check.VERDICT_OPEN
            reason = "its basis changed; it is out of date"
        elif item["open"]:
            verdict = claim_check.VERDICT_OPEN
            reason = "no source on the record, or the cite was not pulled"
        elif any(claim_check._echoes(item["requirement"], note) for note in item["author_notes"]):
            # Only a note the claim's own author wrote can be the claim said back. A pack note
            # that states the claim word for word is what support looks like.
            verdict = claim_check.VERDICT_NOT
            reason = "its author's note only repeats the claim"
        else:
            verdict = words.get(item["n"], claim_check.VERDICT_NOT)
            if verdict not in (claim_check.VERDICT_SUPPORTED, claim_check.VERDICT_NOT, claim_check.VERDICT_OPEN):
                verdict = claim_check.VERDICT_NOT
            missing = _missing_figures(item["requirement"], item["numbers"])
            if verdict == claim_check.VERDICT_SUPPORTED and missing:
                # No verdict stands against the arithmetic: a figure in the claim is not in what it cites.
                verdict = claim_check.VERDICT_NOT
                reason = "figure not in the rows it cites: " + ", ".join(missing)
        rows.append({
            "n": item["n"], "finding_id": item["finding_id"], "verdict": verdict,
            "cite": item["cite"].replace('"', "'"), "basis": item["basis"] if verdict == claim_check.VERDICT_SUPPORTED else "",
            "sources": item["sources"], "reason": reason,
        })
        record.set_finding_status(project_id, item["finding_id"], status=verdict, by=CHECKER_ROLE)
    supported = [row for row in rows if row["verdict"] == claim_check.VERDICT_SUPPORTED]
    on_source = sum(1 for row in supported if row["basis"] == "source")
    on_author = len(supported) - on_source
    not_ok = [row for row in rows if row["verdict"] != claim_check.VERDICT_SUPPORTED]
    all_supported = bool(rows) and not not_ok
    split = (f"{on_source} against a calculation record, a content-pack note, or a project input, "
             f"{on_author} against a cite their author wrote")
    if all_supported:
        status_line = (
            f"Trace check: all {len(rows)} findings are consistent with the rows they cite ({split}). "
            + NOT_STANDARD
        )
        block_reason = ""
    else:
        listed = ", ".join(str(row["n"]) for row in not_ok)
        status_line = (
            f"Trace check: {len(supported)} of {len(rows)} findings are consistent with the rows they cite ({split}). "
            f"Not supported or without a source: {listed}. " + NOT_STANDARD
        )
        block_reason = status_line
    outcome = {
        "usage": usage,
        "rows": rows,
        "all_supported": all_supported,
        "claim_count": len(rows),
        "supported": len(supported),
        "on_source": on_source,
        "on_author": on_author,
        "token": packet["token"],
        "status_line": status_line,
        "block_reason": block_reason,
        "checked_against_standard": False,
        "verdict": "\n".join(
            f'{row["n"]}. {row["verdict"]}. Cite: "{_clip(row["cite"], 320)}"' + (f" ({row['reason']})" if row["reason"] else "")
            for row in rows
        ),
    }
    record.log_event(project_id, CHECK_EVENT, outcome, agent=CHECKER_ROLE)
    return outcome


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
    return bool(payload) and payload.get("token") == check_token(list((snapshot or {}).get("findings") or []))


def check_line(snapshot: dict | None) -> str:
    """One line on the trace check for the panel and the lead. It speaks for the findings the check saw."""
    snap = snapshot or {}
    payload = _latest_check_in(snap)
    if payload is None:
        if snap.get("findings"):
            return "Trace check: not run on the current findings."
        return "Trace check: nothing to check yet."
    # A check speaks for the findings it saw. New or changed findings need a new one.
    if payload.get("token") and payload.get("token") != check_token(list(snap.get("findings") or [])):
        return "Trace check: findings changed since the last check. Run it again."
    return str(payload.get("status_line") or "Trace check ran.")


def summary_line(outcome: dict | None) -> str:
    """The check in a few words for the block under a lead reply."""
    rows = (outcome or {}).get("rows") or []
    if not rows:
        return "trace check: nothing to check"
    supported = sum(1 for row in rows if row.get("verdict") == "Supported")
    on_source = sum(1 for row in rows if row.get("verdict") == "Supported" and row.get("basis") == "source")
    text = f"trace check: {supported} of {len(rows)} findings consistent with what they cite"
    if supported:
        text += f" ({on_source} against a calc record, a pack note, or an input; {supported - on_source} against the author's own cite)"
    return text + ". The standards were not opened."


# -- tiers -------------------------------------------------------------------------------

def assurance(snapshot: dict | None) -> dict[str, dict]:
    """The tier each current finding has earned, with the reasons a reader needs.

    Returns {finding id: {"tier", "reasons", "sources", "verdict", "checked"}}.
    Derived from the finding's label, its checker verdict, the open objections
    on it, and whether its basis changed. Nothing here is typed by a model.
    """
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    payload = _latest_check_in(snap) or {}
    by_finding = {row.get("finding_id"): row for row in payload.get("rows") or []}
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
            basis = seen.get("basis") or "author"
            tier = TIER_SOURCE if basis == "source" else TIER_REVIEWED
            if finding.get("label") in _JUDGMENT_LABELS:
                # Consistent with what it cites, and still an assumption or a judgment by its own label.
                tier = TIER_OPEN
                kind = "an assumption" if finding["label"] == "ASSUMED" else "a judgment the tools did not return"
                reasons.append(f"It is {kind}. The trace check found it consistent with what it cites; "
                               "the engineer of record confirms it.")
        else:
            tier = TIER_STATED
            if finding.get("label") in _JUDGMENT_LABELS:
                tier = TIER_OPEN
                kind = "an assumption" if finding["label"] == "ASSUMED" else "a judgment the tools did not return"
                reasons.append(f"It is {kind}, and no trace check has judged it.")
        for note in standing.get("notes") or []:
            reasons.append("Alternative: " + note)
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
    snapshot = record.snapshot(project_id)
    digest = status.build(snapshot)
    if digest["stale"]:
        changed = "; ".join(item["reason"] for item in digest["changes"][:3])
        count = len(digest["stale"])
        return (
            f"{count} row{'s' if count != 1 else ''} on the record {'are' if count != 1 else 'is'} out of date"
            + (f" ({changed})" if changed else "")
            + ". Run the zone again, or ask the lead to bring the findings up to date. /status lists them."
        )
    findings = snapshot["findings"]
    if not findings:
        return ""
    check = _latest_check_in(snapshot)
    if not check:
        return "The record has findings that no trace check has judged. Ask the lead to run it, or press Run trace check."
    if check.get("token") != check_token(findings):
        return "Findings changed after the last trace check. Run it again."
    return ""
