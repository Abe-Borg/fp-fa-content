"""Where a job stands, read from its project record.

One digest serves four readers: the designer (the /status command and the
Team panel), the lead (the block at the top of each of its messages), each
specialist (the "needs your attention" part of its brief), and the export
gate. It is derived every time from Record.snapshot() and
coherence.analyze(); nothing here is stored, and nothing here calls a model.

The digest answers the questions a person has on coming back to a job:
what the team was asked, who did what, what is settled, what changed since,
what the team needs from the designer, and what is still for the engineer
of record.
"""

from __future__ import annotations

from typing import Any

from fpfa import coherence, inputs
from fpfa.releasing import reader_view

PLAN_EVENT = "plan"
# Who writes the fixed tool plan's calc rows: the plan itself, and a bare session with no agent.
PLAN_AGENTS = ("tool-plan", "")
STEP_STATES = ("todo", "doing", "done", "blocked")
STEP_MARK = {"todo": "○", "doing": "●", "done": "✓", "blocked": "!"}
LEAD = "lead"
PENDING_HEADER = "Handoffs waiting on the record. Each is delivered when you delegate to its receiver:"


def _short(text: Any, limit: int = 160) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def latest_plan(snapshot: dict | None) -> dict | None:
    """The lead's current plan: the objective and its steps. None before the lead has set one."""
    found = ((snapshot or {}).get("latest") or {}).get(PLAN_EVENT)
    if found is None:
        for row in (snapshot or {}).get("events") or []:
            if row.get("kind") == PLAN_EVENT:
                found = row
    if found is None:
        return None
    payload = found.get("payload") or {}
    steps = []
    for item in payload.get("steps") or []:
        if not isinstance(item, dict) or not str(item.get("title") or "").strip():
            continue
        state = str(item.get("status") or "todo").strip().lower()
        steps.append({
            "title": _short(item.get("title"), 200),
            "owner": str(item.get("owner") or "").strip(),
            "status": state if state in STEP_STATES else "todo",
        })
    return {"objective": _short(payload.get("objective"), 400), "steps": steps, "ts": found.get("ts") or ""}


def input_rows(snapshot: dict | None) -> list[dict]:
    """The project inputs as a reader sees them: name, value, who supplied it."""
    rows = []
    for row in (snapshot or {}).get("facts") or []:
        if row.get("kind") == inputs.BASIS_KIND and row.get("key") in inputs.BASIS_FIELDS:
            value: Any = row.get("value")
            name = row["key"]
        elif row.get("kind") == inputs.INPUT_KIND:
            value = inputs.decode(row.get("value"))
            name = row["key"]
        else:
            continue
        source = str(row.get("source") or "")
        rows.append({
            "id": row["id"], "name": name, "value": value, "text": inputs.show(name, value),
            "source": source, "by": row.get("agent") or "", "label": row.get("label") or "",
            "unconfirmed": inputs.UNCONFIRMED_MARK in source,
            "blank": value is None or value == "" or value == [],
        })
    order = {name: index for index, name in enumerate(inputs.BASIS_FIELDS + tuple(inputs.ZONE_FIELDS))}
    rows.sort(key=lambda item: order.get(item["name"], 999))
    return rows


def build(snapshot: dict | None, *, export_reason: str | None = None) -> dict:
    """The digest. export_reason is the export gate's answer when the caller has it ("" means ready)."""
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    findings = list(snap.get("findings") or [])
    calcs = {row["id"]: row for row in snap.get("calcs") or []}
    by_id = {row["id"]: row for row in findings}
    decisions = {row["id"]: row for row in snap.get("decisions") or []}
    evidence = {row["id"]: row for row in snap.get("evidence") or []}
    reviews = list(snap.get("reviews") or [])

    stale = []
    for ident in analysis["stale"]["findings"]:
        row = by_id[ident]
        stale.append({"kind": "finding", "id": ident, "by": row.get("agent") or "", "text": _short(row.get("text")),
                      "reasons": analysis["findings"][ident]["reasons"]})
    for ident in analysis["stale"]["decisions"]:
        row = decisions[ident]
        stale.append({"kind": "decision", "id": ident, "by": row.get("decided_by") or "", "text": _short(row.get("text")),
                      "reasons": analysis["decisions"][ident]["reasons"]})
    # What a current finding or decision rests on. An out-of-date row nothing current rests on is history:
    # it is marked where it is listed and it is not exported as current, but nobody has to act on it.
    cited = {support for row in findings for support in row.get("supports") or []}
    cited |= {support for row in decisions.values() for support in row.get("supports") or []}
    for ident in analysis["stale"]["calcs"]:
        row = calcs[ident]
        if ident not in cited:
            # The tool plan's rows feed the tables and the exports directly, so they count until the zone is run again.
            if (row.get("agent") or "") not in PLAN_AGENTS:
                continue
            rerun = any(
                other["tool"] == row["tool"] and other["id"] != ident and (other.get("agent") or "") in PLAN_AGENTS
                and analysis["calcs"][other["id"]]["state"] != coherence.STALE
                for other in calcs.values()
            )
            if rerun:
                continue
        stale.append({"kind": "calc", "id": ident, "by": row.get("agent") or "", "text": row["tool"],
                      "reasons": analysis["calcs"][ident]["reasons"]})
    for ident in analysis["stale"]["evidence"]:
        if ident not in cited:
            continue
        row = evidence[ident]
        where = " ".join(part for part in (row.get("document"), row.get("edition"), row.get("section")) if part)
        stale.append({"kind": "cite", "id": ident, "by": row.get("agent") or "", "text": where,
                      "reasons": analysis["evidence"][ident]["reasons"]})

    objections = []
    for row in reviews:
        if row.get("position") != "object" or row.get("status") not in ("open", "escalated"):
            continue
        finding = by_id.get(row["finding_id"]) or {}
        objections.append({
            "id": row["id"], "finding_id": row["finding_id"], "by": row.get("agent") or "",
            "author": finding.get("agent") or "", "finding": _short(finding.get("text")),
            "note": _short(row.get("note"), 400), "status": row.get("status"),
            "resolution": _short(row.get("resolution"), 300),
        })
    alternatives = []
    for ident, item in analysis["findings"].items():
        if item["state"] == coherence.CURRENT and item.get("notes"):
            row = by_id[ident]
            alternatives.append({"finding_id": ident, "by": row.get("agent") or "", "finding": _short(row.get("text")),
                                 "notes": item["notes"]})
    questions = list(snap.get("questions") or [])
    asks = [row for row in questions if row.get("status") == "open" and row.get("audience") == "designer"]
    rfis = [row for row in questions if row.get("status") == "open" and row.get("audience") != "designer"]
    # Answers the designer gave on the panel that no lead turn has read yet (Record.unseen_answers).
    unseen = set(snap.get("unseen_answers") or [])
    answered = [row for row in questions if row.get("status") == "answered" and row["id"] in unseen]
    pending = [row for row in snap.get("handoffs") or [] if row.get("status") == "pending"]
    interrupted = [row for row in snap.get("agents") or [] if row.get("status") in ("interrupted", "error")]
    interrupted_jobs = [row for row in snap.get("jobs") or [] if row.get("status") == "interrupted"]

    people = []
    counts: dict[str, int] = {}
    for row in findings:
        counts[row.get("agent") or ""] = counts.get(row.get("agent") or "", 0) + 1
    review_counts: dict[str, int] = {}
    for row in reviews:
        review_counts[row.get("agent") or ""] = review_counts.get(row.get("agent") or "", 0) + 1
    for row in snap.get("agents") or []:
        slug = row.get("role_slug") or ""
        people.append({"slug": slug, "name": row.get("name") or slug, "status": row.get("status") or "",
                       "findings": counts.get(slug, 0), "reviews": review_counts.get(slug, 0),
                       "last_active": row.get("last_active") or ""})
    rows = input_rows(snap)
    return {
        "plan": latest_plan(snap),
        "inputs": rows,
        "unconfirmed": [row for row in rows if row["unconfirmed"] and not row["blank"]],
        # A change is news while something that used the old value still has to be brought up to date.
        "changes": [item for item in analysis["changes"]
                    if any(item["reason"] in reason for row in stale for reason in row["reasons"])],
        "people": people,
        "findings": len(findings),
        "calcs": sum(1 for item in analysis["calcs"].values() if item["state"] != coherence.STALE),
        "stale": stale,
        "objections": objections,
        "conflicts": analysis["conflicts"],
        "alternatives": alternatives,
        "asks": [{"id": row["id"], "text": row["text"], "by": row.get("raised_by") or ""} for row in asks],
        "answered": [{"id": row["id"], "text": row["text"], "answer": row.get("answer") or ""} for row in answered],
        "rfis": [{"id": row["id"], "text": row["text"], "by": row.get("raised_by") or ""} for row in rfis],
        "pending": [{"id": row["id"], "from": row.get("from_agent"), "to": row.get("to_agent"),
                     "brief": _short(row.get("brief")), "kind": row.get("kind") or "handoff",
                     "requeued": str(row.get("result") or "").startswith("Re-queued")} for row in pending],
        "interrupted": [{"name": row.get("name"), "slug": row.get("role_slug"), "status": row.get("status")}
                        for row in interrupted],
        "interrupted_jobs": [{"id": row["id"], "kind": row.get("kind"), "title": _short(row.get("title"), 80)}
                             for row in interrupted_jobs],
        "export": {"ready": export_reason == "", "reason": export_reason or ""} if export_reason is not None else None,
        "analysis": analysis,
    }


def needs_attention(digest: dict) -> int:
    """How many things on the job are waiting on someone."""
    return (len(digest["stale"]) + len(digest["objections"]) + len(digest["conflicts"])
            + len(digest["asks"]) + len(digest["pending"]))


def strip_text(digest: dict | None, check_line: str = "") -> str:
    """One calm line for the window: who contributed, what is waiting. Empty before any team work."""
    if not digest or (not digest["people"] and not digest["findings"]):
        return ""
    # What is waiting on someone comes first: the line is cut short when the window is narrow.
    bits = []
    if digest["asks"]:
        bits.append(f"{len(digest['asks'])} need{'s' if len(digest['asks']) == 1 else ''} your answer")
    if digest["stale"]:
        bits.append(f"{len(digest['stale'])} out of date")
    waiting = len(digest["objections"]) + len(digest["conflicts"])
    if waiting:
        bits.append(f"{waiting} disagreement{'s' if waiting != 1 else ''} open")
    if digest["findings"]:
        bits.append(f"{digest['findings']} finding{'s' if digest['findings'] != 1 else ''}")
    done = [row for row in digest["people"] if row["slug"] not in ("tool-plan", "narrator", LEAD)]
    if done:
        bits.append(", ".join(f"{row['slug']} {row['status']}" for row in done))
    return " · ".join(bits)


def _input_lines(digest: dict, *, full: bool) -> list[str]:
    rows = digest["inputs"]
    if not rows:
        return ["Project inputs: none on the record. The zone form has not been filled in or saved."]
    lines = ["Project inputs (GIVEN: what the designer supplied; the team works from these):"]
    given = [row for row in rows if not row["blank"] and not row["unconfirmed"]]
    loose = [row for row in rows if not row["blank"] and row["unconfirmed"]]
    blank = [row for row in rows if row["blank"]]
    if full:
        for row in given:
            lines.append(f"- {row['name']}: {row['text']} [{row['id']}] ({row['source'] or row['by']})")
    else:
        lines.append("- " + "; ".join(f"{row['name']} {row['text']}" for row in given) if given else "- none confirmed")
    if loose:
        lines.append("- Starting values the designer has not confirmed (not their input until they say so): "
                     + "; ".join(f"{row['name']} {row['text']}" for row in loose))
    if blank:
        lines.append("- Blank: " + ", ".join(row["name"] for row in blank))
    return lines


def lead_text(digest: dict, check_line: str = "") -> str:
    """The status block at the top of the lead's message. Plain lines with record ids."""
    lines = ["Status of this job, read from the project record by the application:"]
    plan = digest.get("plan")
    if plan and (plan["objective"] or plan["steps"]):
        lines.append(f"Plan. Objective: {plan['objective'] or '(not stated)'}")
        for step in plan["steps"]:
            owner = f" ({step['owner']})" if step["owner"] else ""
            lines.append(f"- {STEP_MARK[step['status']]} {step['title']}{owner}: {step['status']}")
    else:
        lines.append("Plan: none set on this job yet.")
    lines.extend(_input_lines(digest, full=False))
    if digest["changes"]:
        lines.append("Inputs changed after work was done on them:")
        for item in digest["changes"]:
            lines.append(f"- {item['reason']}")
    if digest["answered"]:
        lines.append("The designer answered these on the panel. You have not acted on them yet. Act on each answer:")
        for row in digest["answered"]:
            lines.append(f"- [{row['id']}] {_short(row['text'])} Answer: {_short(row['answer'], 400)}")
    if digest["stale"]:
        lines.append("Out of date. Their basis changed. Do not quote them; have the author bring each up to date "
                     "(run again, then replace or withdraw):")
        for row in digest["stale"]:
            lines.append(f"- {row['kind']} [{row['id']}] by {row['by'] or 'the app'}: {row['text']}. "
                         + "; ".join(row["reasons"][:2]))
    if digest["objections"]:
        lines.append("Open objections. Each needs an end: the author revises, you settle it, or you escalate it:")
        for row in digest["objections"]:
            mark = " (escalated, waiting on an answer)" if row["status"] == "escalated" else ""
            lines.append(f"- review [{row['id']}]{mark}: {row['by']} objects to {row['author']}'s finding "
                         f"[{row['finding_id']}] \"{row['finding']}\": {row['note']}")
    if digest["conflicts"]:
        lines.append("Conflicting facts. Two contributors recorded different values for one key:")
        for item in digest["conflicts"]:
            values = "; ".join(f"{row['agent']}: {row['value']} [{row['id']}]" for row in item["rows"])
            lines.append(f"- {item['kind']}/{item['key']}: {values}")
    if digest["alternatives"]:
        lines.append("Findings that rest on a value other than the project input. Either the input is wrong "
                     "(set_input) or the finding is an alternative and must say so:")
        for row in digest["alternatives"]:
            lines.append(f"- [{row['finding_id']}] by {row['by']}: {row['finding']}. " + "; ".join(row["notes"][:2]))
    if digest["pending"]:
        lines.append(PENDING_HEADER)
        for row in digest["pending"]:
            note = " (re-queued after a relaunch)" if row["requeued"] else ""
            lines.append(f"- [{row['id']}] from {row['from']} to {row['to']}{note}: {row['brief']}")
    if digest["interrupted"] or digest["interrupted_jobs"]:
        names = ", ".join(str(row["name"]) for row in digest["interrupted"]) or "a job"
        lines.append(f"Interrupted before it finished: {names}. Its rows so far are on the record. "
                     "Delegate again to finish; recorded calcs replay.")
    if digest["asks"]:
        lines.append("Waiting on the designer:")
        for row in digest["asks"]:
            lines.append(f"- [{row['id']}] {_short(row['text'], 300)} (asked by {row['by']})")
    if digest["rfis"]:
        lines.append(f"Open for the engineer of record: {len(digest['rfis'])} "
                     f"question{'s' if len(digest['rfis']) != 1 else ''} on the record.")
    people = [row for row in digest["people"] if row["slug"] not in ("tool-plan", "narrator", LEAD)]
    if people:
        lines.append("Contributors so far: " + "; ".join(
            f"{row['slug']} ({row['status']}, {row['findings']} finding{'s' if row['findings'] != 1 else ''}"
            f"{', ' + str(row['reviews']) + ' review' + ('s' if row['reviews'] != 1 else '') if row['reviews'] else ''})"
            for row in people))
    else:
        lines.append("Contributors so far: none. No specialist has worked on this job.")
    if check_line:
        lines.append(check_line)
    return "\n".join(lines)


def designer_text(digest: dict, check_line: str = "", name: str = "") -> str:
    """What /status posts into the thread: where the job stands, in the designer's words. Markdown."""
    lines = [f"**Where {name or 'this job'} stands**"]
    plan = digest.get("plan")
    if plan and plan["objective"]:
        lines.append(f"Objective: {plan['objective']}")
    if plan and plan["steps"]:
        for step in plan["steps"]:
            owner = f" ({step['owner']})" if step["owner"] else ""
            lines.append(f"- {STEP_MARK[step['status']]} {step['title']}{owner}")
    people = [row for row in digest["people"] if row["slug"] not in ("tool-plan", "narrator")]
    if people:
        lines.append("")
        lines.append("**Team**")
        for row in people:
            bits = [row["status"]]
            if row["findings"]:
                bits.append(f"{row['findings']} finding{'s' if row['findings'] != 1 else ''}")
            if row["reviews"]:
                bits.append(f"reviewed {row['reviews']} of the others' findings")
            lines.append(f"- {row['name']} ({row['slug']}): " + ", ".join(bits))
    elif not digest["findings"]:
        lines.append("")
        lines.append("No specialist has worked on this job yet. Ask for what you need and the lead brings them in.")
    if digest["asks"]:
        lines.append("")
        lines.append("**The team needs from you**")
        for index, row in enumerate(digest["asks"], start=1):
            lines.append(f"{index}. {row['text']}")
    if digest["changes"] or digest["stale"]:
        lines.append("")
        lines.append("**Out of date since an input changed**")
        for item in digest["changes"]:
            lines.append(f"- {item['reason']}")
        for row in digest["stale"]:
            lines.append(f"- {row['kind']} by {row['by'] or 'the tool plan'}: {row['text']}")
        lines.append("Ask the lead to bring these up to date, or run the zone again. They are not exported as current.")
    waiting = digest["objections"] or digest["conflicts"] or digest["alternatives"]
    if waiting:
        lines.append("")
        lines.append("**Not yet reconciled**")
        for row in digest["objections"]:
            mark = " Escalated; waiting on an answer." if row["status"] == "escalated" else ""
            lines.append(f"- {row['by']} objects to {row['author']}'s finding \"{row['finding']}\": {row['note']}{mark}")
        for item in digest["conflicts"]:
            values = "; ".join(f"{row['agent']} says {row['value']}" for row in item["rows"])
            lines.append(f"- {item['key']}: {values}")
        for row in digest["alternatives"]:
            lines.append(f"- {row['by']}'s finding \"{row['finding']}\" rests on a value other than the project input.")
    if digest["unconfirmed"]:
        lines.append("")
        lines.append("**Starting values you have not confirmed**")
        lines.append("; ".join(f"{row['name']} {row['text']}" for row in digest["unconfirmed"]) + ".")
    if digest["interrupted"] or digest["interrupted_jobs"]:
        lines.append("")
        lines.append("**Interrupted**")
        for row in digest["interrupted"]:
            lines.append(f"- {row['name']} did not finish. What it had recorded is kept. Ask again to finish; calcs replay.")
    if digest["rfis"]:
        lines.append("")
        lines.append(f"**Open for the engineer of record** ({len(digest['rfis'])})")
        for index, row in enumerate(digest["rfis"][:12], start=1):
            lines.append(f"{index}. {row['text']}")
        if len(digest["rfis"]) > 12:
            lines.append(f"…and {len(digest['rfis']) - 12} more on the Team panel.")
    lines.append("")
    summary = f"{digest['findings']} finding{'s' if digest['findings'] != 1 else ''} and " \
              f"{digest['calcs']} current calculation record{'s' if digest['calcs'] != 1 else ''} on the record."
    lines.append(summary + (" " + check_line if check_line else ""))
    export = digest.get("export")
    if export is not None:
        lines.append("Design Basis export: ready." if export["ready"] else f"Design Basis export waits: {export['reason']}")
    return "\n".join(lines)


def attention_for(digest: dict, slug: str, snapshot: dict | None) -> list[str]:
    """The part of a specialist's brief that says what on the record needs it. Lines with record ids."""
    snap = snapshot or {}
    lines: list[str] = []
    mine = [row for row in digest["stale"] if row["by"] == slug and row["kind"] in ("finding", "decision")]
    if mine:
        lines.append("Your findings and decisions whose basis changed. Run the calcs again on the current inputs, "
                     "then replace each (record_finding or record_decision with replaces) or withdraw it:")
        for row in mine:
            lines.append(f"- [{row['id']}] {row['text']}. " + "; ".join(row["reasons"][:2]))
    against = [row for row in digest["objections"] if row["author"] == slug]
    if against:
        lines.append("Objections to your findings. Revise the finding if the objection is right. "
                     "If it is not, say why in your summary and leave the finding:")
        for row in against:
            lines.append(f"- finding [{row['finding_id']}] \"{row['finding']}\": {row['by']} objects: {row['note']}")
    conflicts = [item for item in digest["conflicts"] if any(row["agent"] == slug for row in item["rows"])]
    for item in conflicts:
        values = "; ".join(f"{row['agent']}: {row['value']}" for row in item["rows"])
        lines.append(f"A fact you recorded conflicts with another contributor's: {item['kind']}/{item['key']}: {values}")
    reviewed = {row["finding_id"] for row in snap.get("reviews") or [] if row.get("agent") == slug}
    others = [row for row in snap.get("findings") or []
              if row.get("agent") not in (slug, "") and row["id"] not in reviewed]
    if others:
        analysis = digest["analysis"]
        lines.append("Other contributors' findings you have not reviewed. Read them. Where one states or assumes "
                     "something your work owns, record where you stand with review_finding (agree, or object and say why). "
                     "Leave the ones that do not touch your work:")
        for row in others[:40]:
            state = " OUT OF DATE" if analysis["findings"].get(row["id"], {}).get("state") == coherence.STALE else ""
            lines.append(f"- [{row['id']}] {row['agent']} ({row['label']}){state}: {_short(row['text'], 300)}")
    return lines


def record_text(snapshot: dict | None, *, max_rows: int = 40) -> str:
    """The record as a model reads it, with row ids and each row's standing. Not the export."""
    snap = snapshot or {}
    analysis = coherence.analyze(snap)
    lines: list[str] = []
    other_facts = [row for row in snap.get("facts") or []
                   if row.get("kind") != inputs.INPUT_KIND]
    if other_facts:
        lines.append("Facts:")
        for row in other_facts[:max_rows]:
            lines.append(f"- [{row['id']}] {row['kind']}/{row['key']}: {row['value']} ({row['label']})")
    zone = [row for row in snap.get("facts") or [] if row.get("kind") == inputs.INPUT_KIND]
    if zone:
        lines.append("Zone inputs (cite the id when a finding rests on one):")
        for row in zone:
            value = inputs.decode(row["value"])
            note = " (starting value, not confirmed)" if inputs.UNCONFIRMED_MARK in str(row.get("source") or "") else ""
            lines.append(f"- [{row['id']}] {row['key']}: {inputs.show(row['key'], value)}{note}")
    calcs = list(snap.get("calcs") or [])
    current = [row for row in calcs if analysis["calcs"][row["id"]]["state"] != coherence.STALE]
    old = [row for row in calcs if analysis["calcs"][row["id"]]["state"] == coherence.STALE]
    if current:
        lines.append("Calculation records (cite the id in supports):")
        for row in current[-max_rows:]:
            standing = analysis["calcs"][row["id"]]
            note = f" ALTERNATIVE: ran on {standing['note']}" if standing["state"] == coherence.ALTERNATIVE else ""
            lines.append(
                f"- [{row['id']}] {row['tool']} by {row['agent'] or 'tool'}; "
                f"inputs {_clip(_json(row['inputs']), 160)}; "
                f"outputs {_clip(_json(_scalars(reader_view(row['tool'], row['outputs']))), 240)}{note}"
            )
    if old:
        lines.append("Out-of-date calculation records (an input changed after they ran; do not cite them):")
        for row in old[-max_rows:]:
            lines.append(f"- [{row['id']}] {row['tool']}: " + "; ".join(analysis["calcs"][row["id"]]["reasons"][:1]))
    if snap.get("evidence"):
        lines.append("Evidence (cite the id in supports):")
        for row in snap["evidence"][:max_rows]:
            where = " ".join(part for part in (row["document"], row.get("edition") or "", row.get("section") or "") if part)
            stale = " OUT OF DATE: the edition changed" if analysis["evidence"][row["id"]]["state"] == coherence.STALE else ""
            lines.append(f"- [{row['id']}] {where}: {row.get('note') or ''} [{row['status']}]{stale}")
    reviews: dict[str, list[dict]] = {}
    for row in snap.get("reviews") or []:
        reviews.setdefault(row["finding_id"], []).append(row)
    if snap.get("findings"):
        lines.append("Findings:")
        for row in snap["findings"][:max_rows]:
            stale = " OUT OF DATE" if analysis["findings"][row["id"]]["state"] == coherence.STALE else ""
            positions = "".join(
                f" [{item['agent']} {'objects' if item['position'] == 'object' else 'agrees'}"
                f"{'' if item['status'] in ('open', 'escalated') or item['position'] == 'agree' else ', settled'}]"
                for item in reviews.get(row["id"], [])
            )
            lines.append(f"- [{row['id']}] {row['agent']}: {row['text']} ({row['label']}){stale}{positions}")
    if snap.get("decisions"):
        lines.append("Decisions:")
        for row in snap["decisions"][:max_rows]:
            lines.append(f"- [{row['id']}] {row['text']} ({row['label']}; {row['decided_by']})")
    open_questions = [row for row in snap.get("questions") or [] if row["status"] == "open"]
    if open_questions:
        lines.append("Open questions:")
        for row in open_questions[:max_rows]:
            who = "the designer" if row.get("audience") == "designer" else "the engineer of record"
            lines.append(f"- [{row['id']}] {row['text']} (raised by {row['raised_by']}, for {who})")
    pending = [row for row in snap.get("handoffs") or [] if row["status"] == "pending"]
    if pending:
        lines.append("Pending handoffs:")
        for row in pending[:max_rows]:
            lines.append(f"- [{row['id']}] {row['from_agent']} to {row['to_agent']}: {row['brief']}")
    return "\n".join(lines) if lines else "The project record is empty."


def _json(value: Any) -> str:
    import json

    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str, ensure_ascii=False)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _scalars(outputs: Any) -> Any:
    if not isinstance(outputs, dict):
        return outputs
    return {key: value for key, value in outputs.items() if isinstance(value, (int, float, str, bool)) or value is None}
