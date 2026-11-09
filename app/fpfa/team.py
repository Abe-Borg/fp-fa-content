"""The team on the existing tool loop.

The lead is the everyday path with four more tools. list_specialists names
the specialist roles in the content pack. delegate runs one specialist in
its own context: that role's ROLE.md as the system text, the skill index,
the calc and record tools, and a brief from the lead. The specialist's
findings, questions, cites, and handoffs land on the project record as
that specialist, and the lead gets a structured contribution back.
request_check runs the blind checker over the record's findings. handoff
writes a pending row that is delivered when the lead next activates the
receiver. No specialist talks to another directly.

Nothing here computes. Specialists call the same calc tools the lead
has, and every call records itself on the job.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import add_usage, empty_usage, run_tool_loop
from fpfa.record import Record, RecordError
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, spec_notes

LEAD = "lead"
CHECKER_ROLE = "qa-specialist"
SHELL_ROLE = "everyday"
# Roles that are not specialists a lead may delegate to.
_NOT_SPECIALISTS = frozenset({SHELL_ROLE, CHECKER_ROLE})
# Specialists that draft against the master language and so need the spec files.
_SPEC_READERS = frozenset({"spec-draft"})
TEAM_TOOL_NAMES = ("list_specialists", "delegate", "request_check")
CHECK_EVENT = "record_check"

TEAM_SCHEMAS = SCHEMAS + [
    {
        "name": "list_specialists",
        "description": (
            "List the specialist roles in this content pack that the lead may delegate to, with what each one owns."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "delegate",
        "description": (
            "Run one specialist in its own context on this job and return its contribution: findings, "
            "questions, cites, handoffs, and calc record ids it wrote. Pass a brief that says what to decide "
            "and the inputs it needs. Pending handoffs addressed to that specialist are delivered with the brief. "
            "One specialist per call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "specialist": {"type": "string", "description": "Role slug from list_specialists."},
                "brief": {"type": "string", "description": "The task, in plain sentences."},
                "inputs": {"type": "object", "description": "Figures, form values, or ids the specialist needs. Optional."},
            },
            "required": ["specialist", "brief"],
        },
    },
    {
        "name": "request_check",
        "description": (
            "Run the blind checker over the findings on this job's record. The checker sees only the claim "
            "list and the short cites. Returns a verdict per finding. Run it before presenting the design "
            "basis as checked."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]
SPECIALIST_SCHEMAS = [item for item in SCHEMAS]

TEAM_PARAGRAPH = (
    "Team. You are the lead. list_specialists shows the specialists in this content pack. "
    "delegate(specialist, brief, inputs) runs that specialist in its own context on this job's record and "
    "returns its contribution: findings, questions, cites, handoffs, and calc record ids. Delegate when the "
    "request needs a specialist's method, one specialist per call, and pass the figures it needs in inputs. "
    "A handoff one specialist writes for another is delivered when you delegate to the receiver. "
    "request_check runs the blind checker over the record's findings and returns a verdict per finding; run it "
    "before you present a design basis as checked, and say which findings are not Supported. You reconcile "
    "the contributions, surface blockers and open questions, and write the summary. You do not compute, and "
    "you do not restate a specialist's figure without its calc record id."
)


def list_specialists(content_root: Path) -> list[dict]:
    """Specialist roles: every ROLE.md except the everyday shell and the checker."""
    return [row for row in list_roles(content_root) if row["slug"] not in _NOT_SPECIALISTS]


def specialist_slugs(content_root: Path) -> list[str]:
    return [row["slug"] for row in list_specialists(content_root)]


def specialist_system(content_root: Path, slug: str) -> str:
    """ROLE.md as the system text, with the skill index and the record paragraph."""
    if slug in _NOT_SPECIALISTS or slug not in specialist_slugs(content_root):
        raise RecordError(
            f"{slug!r} is not a specialist on this content pack. Specialists: "
            + ", ".join(specialist_slugs(content_root))
        )
    lines = [read_role(content_root, slug).strip(), ""]
    lines.append(
        "You are one specialist on a team. The lead delegated a task to you. Read the skill that matches it "
        "with read_skill before you apply the method. Call the calc tools for every number. Record each "
        "finding with record_finding and the ids of the calc records or evidence rows it rests on. Record a "
        "cite with record_evidence. A question the designer must answer is open_question. Work another "
        "specialist must do is handoff, by role slug. Do not delegate; only the lead does. End with a short "
        "summary for the lead: what you found, what you recorded, and what is open."
    )
    lines.append("")
    lines.append("Skills in this content pack:")
    for skill in list_skills(content_root):
        lines.append(f"- {skill['slug']}: {skill['description']}")
    if slug in _SPEC_READERS:
        notes = spec_notes(content_root)
        if notes:
            lines.append("")
            lines.append("Spec notes from the content pack. They are draft language. Verify before issuing.")
            for note in notes:
                lines.append(f"## {note['name']}")
                lines.append(note["text"])
    return "\n".join(lines)


def _prior_contribution(record: Record, project_id: str, slug: str) -> list[str]:
    lines: list[str] = []
    for row in record.findings(project_id, agent=slug):
        lines.append(f"- finding [{row['id']}] ({row['label']}, {row['status']}): {row['text']}")
    for row in record.questions(project_id):
        if row.get("raised_by") == slug:
            lines.append(f"- question [{row['id']}] ({row['status']}): {row['text']}")
    for row in record.handoffs(project_id):
        if row.get("to_agent") == slug and row.get("status") == "returned" and row.get("result"):
            lines.append(f"- your earlier summary for the lead [{row['id']}]: {row['result']}")
    return lines


def specialist_request(
    record: Record,
    project_id: str,
    slug: str,
    brief: str,
    inputs: dict | None,
    pending: list[dict],
) -> str:
    """The user message a specialist receives. Brief, inputs, prior work, handoffs, and the record."""
    parts = [
        f"You are the specialist {slug} on this job. The lead delegated this task:",
        brief.strip(),
    ]
    if inputs:
        parts.append("Inputs from the lead:\n" + json.dumps(inputs, indent=2, sort_keys=True, default=str))
    prior = _prior_contribution(record, project_id, slug)
    if prior:
        parts.append("Your earlier contribution on this job:\n" + "\n".join(prior))
    if pending:
        lines = ["Handoffs waiting for you:"]
        for row in pending:
            payload = row.get("payload")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    pass
            lines.append(f"- [{row['id']}] from {row['from_agent']}: {row['brief']}")
            if payload:
                lines.append("  payload: " + json.dumps(payload, sort_keys=True, default=str))
        parts.append("\n".join(lines))
    parts.append("Project record so far (cite these ids in supports):\n" + record.summary_text(project_id))
    return "\n\n".join(parts)


def _new_rows(before: set[str], rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["id"] not in before]


def delegate(
    content_root: Path,
    record: Record,
    project_id: str,
    create: Callable[..., Any],
    *,
    specialist: str,
    brief: str,
    inputs: dict | None = None,
    max_rounds: int = 12,
    max_tokens: int = 16000,
) -> dict:
    """Run one specialist and return its structured contribution.

    The lead's handoff to the specialist is written first and marked returned
    when the specialist finishes. Pending handoffs addressed to the specialist
    are delivered with the brief. Rows the specialist writes carry its slug.
    """
    slug = (specialist or "").strip()
    text = (brief or "").strip()
    if not text:
        raise RecordError("delegate needs a brief")
    if inputs is not None and not isinstance(inputs, dict):
        raise RecordError("inputs must be an object")
    system = specialist_system(content_root, slug)
    name = next((row["name"] for row in list_specialists(content_root) if row["slug"] == slug), slug)
    record.set_agent(project_id, name=name, role_slug=slug, status="working")
    lead_handoff = record.create_handoff(project_id, from_agent=LEAD, to_agent=slug, brief=text, payload=inputs or {})
    record.set_handoff(project_id, lead_handoff["id"], status="delivered", by=LEAD)
    pending = [row for row in record.pending_handoffs(project_id, to_agent=slug) if row["id"] != lead_handoff["id"]]
    for row in pending:
        record.set_handoff(project_id, row["id"], status="delivered", by=LEAD)
    before = {
        "findings": {row["id"] for row in record.findings(project_id)},
        "questions": {row["id"] for row in record.questions(project_id)},
        "evidence": {row["id"] for row in record.evidence(project_id)},
        "calcs": {row["id"] for row in record.calcs(project_id)},
        "handoffs": {row["id"] for row in record.handoffs(project_id)},
    }
    session = ToolSession(content_root, record=record, project_id=project_id, agent=slug)
    request = specialist_request(record, project_id, slug, text, inputs, pending)
    try:
        out = run_tool_loop(
            create,
            system=system,
            user_text=request,
            tools=SPECIALIST_SCHEMAS,
            execute=session.execute,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
        )
    except Exception:
        record.set_agent(project_id, name=name, role_slug=slug, status="error")
        record.set_handoff(project_id, lead_handoff["id"], status="cancelled", result="The specialist did not finish.", by=LEAD)
        raise
    summary = (out.get("text") or "").strip() or "(The specialist returned no text.)"
    findings = _new_rows(before["findings"], record.findings(project_id, agent=slug))
    questions = [row for row in _new_rows(before["questions"], record.questions(project_id)) if row["raised_by"] == slug]
    evidence = [row for row in _new_rows(before["evidence"], record.evidence(project_id)) if row.get("agent") == slug]
    calcs = [row for row in _new_rows(before["calcs"], record.calcs(project_id)) if row.get("agent") == slug]
    handoffs = [row for row in _new_rows(before["handoffs"], record.handoffs(project_id)) if row["from_agent"] == slug]
    for row in pending:
        record.set_handoff(project_id, row["id"], status="returned", result=f"Handled in {slug}'s contribution.", by=slug)
    record.set_handoff(project_id, lead_handoff["id"], status="returned", result=summary[:4000], by=slug)
    record.set_agent(project_id, name=name, role_slug=slug, status="done")
    usage = out.get("usage") or empty_usage()
    record.log_event(project_id, "delegation", {
        "specialist": slug, "handoff": lead_handoff["id"], "findings": len(findings),
        "questions": len(questions), "handoffs": len(handoffs), "usage": usage,
        "stop_reason": out.get("stop_reason") or "",
    }, agent=LEAD)
    return {
        "specialist": slug,
        "handoff_id": lead_handoff["id"],
        "summary": summary,
        "findings": [{"id": row["id"], "text": row["text"], "label": row["label"], "supports": row["supports"]} for row in findings],
        "questions": [{"id": row["id"], "text": row["text"]} for row in questions],
        "evidence": [{"id": row["id"], "document": row["document"], "section": row["section"], "status": row["status"]} for row in evidence],
        "calc_records": [{"id": row["id"], "tool": row["tool"]} for row in calcs],
        "handoffs": [{"id": row["id"], "to": row["to_agent"], "brief": row["brief"]} for row in handoffs],
        "delivered_handoffs": [row["id"] for row in pending],
        "stop_reason": out.get("stop_reason") or "",
        "usage": usage,
    }


# -- the blind checker over the record ------------------------------------

def _claim_check():
    """claim_check imports workflow, which imports everyday, which imports this module lazily."""
    from fpfa import claim_check

    return claim_check


def _cite_for(record_rows: dict[str, dict], finding: dict) -> tuple[str, bool, bool]:
    """Short cite text for a finding, whether it is open, and whether it rests on a calc only."""
    claim_check = _claim_check()
    pieces: list[str] = []
    open_cite = False
    has_evidence = False
    has_calc = False
    for ident in finding.get("supports") or []:
        row = record_rows.get(ident)
        if row is None:
            open_cite = True
            continue
        if row.get("_kind") == "calc":
            has_calc = True
            figures = claim_check._package_figures({row["tool"]: row["outputs"]})
            pieces.append(f"{claim_check.PACKAGE_MARK}. {row['tool']}: {figures}")
        else:
            if row.get("status") in ("NOT PULLED", "NEEDS HOLD"):
                open_cite = True
            has_evidence = True
            edition = f"-{row['edition']}" if row.get("edition") else ""
            section = f" §{row['section']}" if row.get("section") else ""
            note = f" {row['note']}" if row.get("note") else ""
            pieces.append(f"{row['document']}{edition}{section}.{note} [{row['status']}]")
    if not pieces:
        return claim_check.OPEN_MARK, True, False
    return " | ".join(pieces), open_cite, (has_calc and not has_evidence)


def check_token(findings: list[dict]) -> str:
    payload = json.dumps(
        [[row["id"], row["text"], row["label"], row.get("supports") or []] for row in findings],
        sort_keys=True, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_record_packet(record: Record, project_id: str) -> dict:
    """Claims from the record's findings; cites from the rows they cite."""
    findings = record.findings(project_id)
    rows: dict[str, dict] = {}
    for row in record.calcs(project_id):
        rows[row["id"]] = dict(row, _kind="calc")
    for row in record.evidence(project_id):
        rows[row["id"]] = dict(row, _kind="evidence")
    claims: list[str] = []
    sources: list[str] = []
    meta: list[dict] = []
    for index, finding in enumerate(findings, start=1):
        cite, open_cite, calc_only = _cite_for(rows, finding)
        claims.append(f"{index}. {finding['text'].rstrip('.')}.")
        sources.append(f"{index}. {cite}")
        meta.append({"n": index, "finding_id": finding["id"], "open": open_cite, "calc_only": calc_only,
                     "requirement": finding["text"], "cite": cite})
    return {
        "claims": "\n".join(claims),
        "sources": "\n".join(sources),
        "claim_count": len(findings),
        "meta": meta,
        "token": check_token(findings),
    }


def check_record(content_root: Path, record: Record, project_id: str, create: Callable[..., Any]) -> dict:
    """Blind check over the record. Verdicts are written back onto the findings."""
    claim_check = _claim_check()
    packet = build_record_packet(record, project_id)
    if not packet["claim_count"]:
        outcome = {
            "rows": [], "all_supported": False, "claim_count": 0, "token": packet["token"],
            "status_line": "The record has no findings to check.",
            "block_reason": "The record has no findings to check.",
            "checked_against_standard": False,
        }
        record.log_event(project_id, CHECK_EVENT, outcome, agent=CHECKER_ROLE)
        return outcome
    system = claim_check.checker_system(content_root)
    model_text = claim_check._ask(create, system, claim_check.checker_request(packet["claims"], packet["sources"]))
    words = claim_check._verdict_words(model_text)
    rows: list[dict] = []
    for item in packet["meta"]:
        if item["open"]:
            verdict = claim_check.VERDICT_OPEN
        elif claim_check._echoes(item["requirement"], item["cite"]):
            verdict = claim_check.VERDICT_NOT
        else:
            verdict = words.get(item["n"], claim_check.VERDICT_NOT)
            if verdict not in (claim_check.VERDICT_SUPPORTED, claim_check.VERDICT_NOT, claim_check.VERDICT_OPEN):
                verdict = claim_check.VERDICT_NOT
            if (
                verdict == claim_check.VERDICT_SUPPORTED
                and item["calc_only"]
                and not claim_check._package_supports(item["requirement"], item["cite"])
            ):
                verdict = claim_check.VERDICT_NOT
        rows.append({"n": item["n"], "finding_id": item["finding_id"], "verdict": verdict,
                     "cite": item["cite"].replace('"', "'")})
        record.set_finding_status(project_id, item["finding_id"], status=verdict, by=CHECKER_ROLE)
    supported = bool(rows) and all(row["verdict"] == claim_check.VERDICT_SUPPORTED for row in rows)
    open_rows = ", ".join(str(row["n"]) for row in rows if row["verdict"] != claim_check.VERDICT_SUPPORTED)
    if supported:
        status_line = (
            f"Blind check: every one of the {len(rows)} findings is Supported on its cite. "
            "A package assertion is not a passage from the standard. Engineer-of-record review still applies."
        )
        block_reason = ""
    else:
        status_line = f"Blind check: findings not Supported: {open_rows}. The design basis is not cleared for issue."
        block_reason = status_line
    outcome = {
        "rows": rows,
        "all_supported": supported,
        "claim_count": len(rows),
        "token": packet["token"],
        "status_line": status_line,
        "block_reason": block_reason,
        "checked_against_standard": False,
        "verdict": "\n".join(f'{row["n"]}. {row["verdict"]}. Cite: "{row["cite"]}"' for row in rows),
    }
    record.log_event(project_id, CHECK_EVENT, outcome, agent=CHECKER_ROLE)
    return outcome


def latest_check(record: Record, project_id: str) -> dict | None:
    event = record.latest_event(project_id, CHECK_EVENT)
    return event["payload"] if event else None


def export_gate(record: Record, project_id: str) -> str:
    """Empty when the design basis may be exported. Otherwise the reason it waits.

    A record with no findings has nothing a checker could judge, so the
    tool-plan figures export on their own. A record with findings needs a
    check that is current and all Supported.
    """
    findings = record.findings(project_id)
    if not findings:
        return ""
    check = latest_check(record, project_id)
    if not check:
        return "The record has findings that no blind check has judged. Ask the lead to run request_check."
    if check.get("token") != check_token(findings):
        return "Findings changed after the last blind check. Ask the lead to run request_check again."
    if not check.get("all_supported"):
        return check.get("block_reason") or "The last blind check did not support every finding."
    return ""


# -- the lead's tool session -----------------------------------------------

class TeamSession:
    """execute() for the lead. Team tools run here; everything else is the tool session."""

    def __init__(
        self,
        content_root: Path,
        record: Record,
        project_id: str,
        create: Callable[..., Any],
        *,
        max_rounds: int = 12,
        max_tokens: int = 16000,
    ):
        self.root = Path(content_root)
        self.record = record
        self.project_id = project_id
        self.create = create
        self.max_rounds = max_rounds
        self.max_tokens = max_tokens
        self.tools = ToolSession(content_root, record=record, project_id=project_id, agent=LEAD)
        self.delegations: list[dict] = []
        self.checks: list[dict] = []
        self.usage = empty_usage()
        self.usage["rounds"] = 0

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name == "list_specialists":
            return {"specialists": list_specialists(self.root)}
        if name == "delegate":
            contribution = delegate(
                self.root, self.record, self.project_id, self.create,
                specialist=str(args.get("specialist") or ""), brief=str(args.get("brief") or ""),
                inputs=args.get("inputs"), max_rounds=self.max_rounds, max_tokens=self.max_tokens,
            )
            self.delegations.append(contribution)
            _merge_usage(self.usage, contribution.get("usage"))
            return contribution
        if name == "request_check":
            outcome = check_record(self.root, self.record, self.project_id, self.create)
            self.checks.append(outcome)
            return {key: value for key, value in outcome.items() if key != "verdict"} | {"verdict": outcome.get("verdict", "")}
        return self.tools.execute(name, args)


def _merge_usage(total: dict, usage: dict | None) -> None:
    if not isinstance(usage, dict):
        return
    for key, value in usage.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        total[key] = int(total.get(key, 0)) + int(value)
