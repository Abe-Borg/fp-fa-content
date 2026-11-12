"""The team on the existing tool loop.

One lead, the specialists the content pack names, and a checker. The
designer talks to the lead. The lead owns the objective: it puts what the
designer said on the record, decides which specialists the request needs,
delegates, makes them reconcile, runs the check, and answers.

How the agents work together, and what the record keeps of it:

- delegate runs one specialist in its own context: that role's ROLE.md as
  the system text, the skill index, the calc and record tools, and a brief
  from the lead. Its brief carries the project inputs, what on the record
  needs it, and the other contributors' findings it has not reviewed.
- consult lets one specialist ask another a question and get the answer
  inside its own turn, when its work depends on a fact the other owns.
  The app runs the second specialist and keeps the exchange as a row.
- review_finding is a specialist's position on another's finding: agree,
  or object with the reason. An objection stays open until the author
  revises the finding, the lead settles it, or the lead escalates it.
- handoff leaves work for another agent, delivered at its next delegation.

Every one of these is a record row with a sender, a receiver, a time, and
content, so what the team did can be inspected afterwards. Nothing here
computes. Specialists call the same calc tools the lead has, and every
call records itself on the job.

The checker and the export gate are in fpfa.checker and are re-exported
here, where they used to live.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from fpfa import inputs, status, units
from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import TurnCancelled, attach_usage, empty_usage, incomplete_notice, run_tool_loop, safe_error
from fpfa.record import ANSWERED_IN_CHAT, BASIS_LABELS, CONVERT_TOOL, GIVEN, Record, RecordError
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, spec_notes

LEAD = "lead"
LEAD_ROLE = "lead"
CHECKER_ROLE = "qa-specialist"
SHELL_ROLE = "everyday"
# Roles that are not specialists a lead may delegate to.
_NOT_SPECIALISTS = frozenset({SHELL_ROLE, CHECKER_ROLE, LEAD_ROLE})
# Specialists that draft against the master language and so need the spec files.
_SPEC_READERS = frozenset({"spec-draft"})
# Tools only the lead has.
TEAM_TOOL_NAMES = (
    "list_specialists", "delegate", "request_check",
    "set_input", "answer_question", "set_plan", "resolve_disagreement",
)
# The lead's tools that run a model and so stop for a cancel before they start.
_MODEL_TOOLS = frozenset({"delegate", "request_check"})
CONSULT = "consult"
# Model rounds a context may take. A specialist reads skills, runs the calcs, records, and reviews.
LEAD_ROUNDS = 24
SPECIALIST_ROUNDS = 20
CONSULT_ROUNDS = 8
# Questions one specialist may put to others inside one delegation.
MAX_CONSULTS = 3
_TEAM_HEADING = "## Working with the team"


def _obj(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required}


_LEAD_TOOLS = [
    {
        "name": "list_specialists",
        "description": (
            "List the specialist roles in this content pack that the lead may delegate to: what each owns, "
            "what it needs from the others, and which of the others' findings it reviews."
        ),
        "input_schema": _obj({}, []),
    },
    {
        "name": "delegate",
        "description": (
            "Run one specialist in its own context on this job and return its contribution: its summary, the "
            "findings, reviews, questions, cites, and calc record ids it wrote, any question it put to another "
            "specialist, and what on the record is still unsettled. Call this for any work that sets or changes "
            "a design basis; do not do a specialist's work yourself. Pass a brief that says what to decide, what "
            "the designer said, and which of the other specialist's findings to review. The specialist reads the "
            "project inputs and the record itself. One specialist per call."
        ),
        "input_schema": _obj(
            {
                "specialist": {"type": "string", "description": "Role slug from list_specialists."},
                "brief": {"type": "string", "description": "The task, in plain sentences."},
                "inputs": {"type": "object", "description": "Record ids or figures from the record the specialist needs. Optional."},
            },
            ["specialist", "brief"],
        ),
    },
    {
        "name": "request_check",
        "description": (
            "Run the trace check over the findings on this job's record. The checker sees only the claim list "
            "and the rows each claim cites. It returns a verdict per finding. It does not open the standards. "
            "Run it before presenting a design basis, and again after findings change."
        ),
        "input_schema": _obj({}, []),
    },
    {
        "name": "set_input",
        "description": (
            "Record a project input the designer stated: a zone input (fill flow, a time, the trim, the pipe "
            "takeoff, a pressure) or a basis field (ahj, nfpa_13, nfpa_72, insurer, hazard_notes). It replaces "
            "the old value for the whole team and appears on the zone form. The result lists the calculations "
            "and findings that used the old value and are now out of date. Record only what the designer "
            "gave; never a value you chose. Inputs and what each takes: " + inputs.describe() + "."
        ),
        "input_schema": _obj(
            {
                "name": {"type": "string", "description": "The input's name."},
                "value": {"type": "string", "description": (
                    "The new value as text: a number in the input's unit, one of the input's choices, true or "
                    "false, or plain text. A figure the designer gave in another unit goes in as they wrote it, "
                    "with its unit (\"12.2 mm/min\", \"139 m²\"): the application converts it to the input's unit "
                    "on a recorded conversion and keeps both. Never pass an SI number bare. Leave it out for segments."
                )},
                "segments": {
                    "type": "array",
                    "description": "For name segments only: the whole pipe list. It replaces the list on the form.",
                    "items": _obj(
                        {
                            "role": {"type": "string", "description": "branch, drop, cross, main, feed, or riser"},
                            "nps": {"type": "string", "description": "Nominal size in inches."},
                            "schedule": {"type": "string", "description": "sch10 or sch40. Blank for the shop default."},
                            "length_ft": {"type": "number"},
                        },
                        ["nps", "length_ft"],
                    ),
                },
                "why": {"type": "string", "description": "Where the designer gave it, in a few words."},
            },
            ["name"],
        ),
    },
    {
        "name": "answer_question",
        "description": (
            "Close an open question with the answer the designer gave in chat. Then act on the answer: "
            "set_input or record_fact for what it changes."
        ),
        "input_schema": _obj(
            {"id": {"type": "string"}, "answer": {"type": "string", "description": "The designer's answer, in their words."}},
            ["id", "answer"],
        ),
    },
    {
        "name": "set_plan",
        "description": (
            "Say what the team will do on this request, or update it: the objective in one sentence and the "
            "steps, each with an owner. The designer sees it on the Team panel. Call it before the first "
            "delegation and again when a step finishes or the plan changes. It replaces the earlier plan."
        ),
        "input_schema": _obj(
            {
                "objective": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": _obj(
                        {
                            "title": {"type": "string"},
                            "owner": {"type": "string", "description": "lead, a specialist slug, or checker."},
                            "status": {"type": "string", "description": "todo, doing, done, or blocked."},
                        },
                        ["title"],
                    ),
                },
            },
            ["objective", "steps"],
        ),
    },
    {
        "name": "resolve_disagreement",
        "description": (
            "End an open objection one specialist recorded against another's finding, when you are not sending "
            "it back to the author. outcome stands: the finding holds and reason says why. outcome escalated: "
            "only the designer or the engineer of record can decide; a question is opened for them (to) and the "
            "objection stays visible as unresolved. If the objection is right, do not use this: delegate to the "
            "author to revise the finding, or withdraw the finding."
        ),
        "input_schema": _obj(
            {
                "id": {"type": "string", "description": "The review id, or the id of the finding objected to."},
                "outcome": {"type": "string", "description": "stands or escalated"},
                "reason": {"type": "string"},
                "to": {"type": "string", "description": "For escalated: designer or engineer. Default engineer."},
            },
            ["id", "outcome", "reason"],
        ),
    },
]
_CONSULT_TOOL = {
    "name": CONSULT,
    "description": (
        "Ask another specialist on this team a question you need answered to finish your task, and get its "
        "answer now. Call this when your work depends on a fact the other specialist owns and the record does "
        "not hold it; do not assume the answer. The other specialist answers from its own method and tools and "
        "may record findings. The exchange is kept on the record. A few questions per task at most. You cannot "
        "consult while you are answering a consult."
    ),
    "input_schema": _obj(
        {
            "specialist": {"type": "string", "description": "Role slug of the specialist to ask."},
            "question": {"type": "string", "description": "One question, with what you need it for."},
            "context": {"type": "string", "description": "What you have so far that bears on it. Optional."},
        },
        ["specialist", "question"],
    ),
}

# The lead with the plain shell (a pack with no lead role): every tool the shell has, plus the lead's.
TEAM_SCHEMAS = SCHEMAS + _LEAD_TOOLS
# The lead with its own role file. It does not read a specialist's role and answer in its place.
LEAD_SCHEMAS = [item for item in SCHEMAS if item["name"] not in ("read_role", "list_roles")] + _LEAD_TOOLS
SPECIALIST_SCHEMAS = [item for item in SCHEMAS] + [_CONSULT_TOOL]

TEAM_PARAGRAPH = (
    "Team tools. list_specialists shows the specialists in this content pack: what each owns, what it needs "
    "from the others, and what it reviews. delegate(specialist, brief, inputs) runs that specialist in its own "
    "context on this job's record and returns its contribution: its summary, the findings, reviews, questions, "
    "cites, and calc record ids it wrote, any question it put to another specialist, and what on the record "
    "is still unsettled. Delegate when the request needs a specialist's method, one specialist per call. "
    "A handoff one specialist writes for another is delivered when you delegate to the receiver. "
    "set_input(name, value, why) records a zone input or a basis field the designer stated; the result lists "
    "what is now out of date. answer_question(id, answer) closes a question the designer answered. "
    "set_plan(objective, steps) says what the team will do. resolve_disagreement(id, outcome, reason) ends "
    "an open objection: stands when the finding holds, escalated when the designer or the engineer of record "
    "has to decide. request_check runs the trace check over the record's findings and returns a verdict per "
    "finding; run it before you present a design basis, and say which findings are not Supported. You reconcile "
    "the contributions, surface blockers and open questions, and write the summary. You do not compute, and "
    "you do not restate a specialist's figure without its calc record id."
)
SPECIALIST_PARAGRAPH = (
    "You are one specialist on a team. The lead delegated a task to you, or another specialist asked you a "
    "question. Your message carries the task, the project inputs, what on the record needs you, and the record "
    "with its row ids. Work from the project inputs. They are what the designer gave the team, and every "
    "contributor reasons from the same ones. If one is wrong or missing, do not put your own value in its "
    "place: object, ask, or run the alternative and say it is an alternative. "
    "Read the skill that matches the task with read_skill before you apply the method. Call the calc tools for "
    "every number. Record each finding with record_finding, one statement per finding, with the ids of the calc "
    "records, cites, or input facts it rests on. Record a cite with record_evidence. Before you cite a section, "
    "find it with search_corpus and write the document, the edition, and the section the way the pack's note "
    "does: the trace check reads your cite in the pack's own notes, and a section the pack does not hold rests "
    "on your note alone and is reported that way. "
    "Where another contributor's finding states or assumes something your work owns, say where you stand with "
    "review_finding: agree, or object with the reason and what would settle it. When you need a fact another "
    "specialist owns and the record does not hold it, ask that specialist with consult. Do not assume it. "
    "When a finding of yours is out of date, or an objection to it is right, replace it (record_finding with "
    "replaces) or withdraw it. A question only the designer can answer is open_question with to designer. One "
    "for the engineer of record is open_question. Work another specialist must do later is handoff, by role "
    "slug. Do not delegate; only the lead does. End with a short summary for the lead: what you found, what you "
    "reviewed and where you stand, what you could not settle, and what is open."
)


def has_lead_role(content_root: Path) -> bool:
    return (Path(content_root) / "roles" / LEAD_ROLE / "ROLE.md").is_file()


def lead_schemas(content_root: Path) -> list[dict]:
    """The lead's tool list. The same list object every call, so a turn's requests are byte-identical."""
    return LEAD_SCHEMAS if has_lead_role(content_root) else TEAM_SCHEMAS


def team_notes(role_text: str) -> str:
    """The "Working with the team" section of a role file: what it owns, needs, and reviews."""
    index = (role_text or "").find(_TEAM_HEADING)
    if index < 0:
        return ""
    body = role_text[index + len(_TEAM_HEADING):]
    cut = body.find("\n## ")
    if cut >= 0:
        body = body[:cut]
    return " ".join(body.split())[:2400]


def list_specialists(content_root: Path) -> list[dict]:
    """Specialist roles: every ROLE.md except the lead, the everyday shell, and the checker."""
    rows = []
    for row in list_roles(content_root):
        if row["slug"] in _NOT_SPECIALISTS:
            continue
        item = dict(row)
        try:
            notes = team_notes(read_role(content_root, row["slug"]))
        except (OSError, ValueError):
            notes = ""
        if notes:
            item["works_with_the_team"] = notes
        rows.append(item)
    return rows


def specialist_slugs(content_root: Path) -> list[str]:
    return [row["slug"] for row in list_roles(content_root) if row["slug"] not in _NOT_SPECIALISTS]


def _specialist_name(content_root: Path, slug: str) -> str:
    return next((row["name"] for row in list_roles(content_root) if row["slug"] == slug), slug)


def specialist_system(content_root: Path, slug: str) -> str:
    """ROLE.md as the system text, with the team paragraph and the skill index."""
    if slug in _NOT_SPECIALISTS or slug not in specialist_slugs(content_root):
        raise RecordError(
            f"{slug!r} is not a specialist on this content pack. Specialists: "
            + ", ".join(specialist_slugs(content_root))
        )
    lines = [read_role(content_root, slug).strip(), ""]
    lines.append(SPECIALIST_PARAGRAPH)
    others = [item for item in specialist_slugs(content_root) if item != slug]
    if others:
        lines.append("")
        lines.append("The other specialists on this team: " + ", ".join(others) + ".")
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
            lines.append(f"- your earlier summary [{row['id']}]: {row['result']}")
    return lines


def _input_lines(digest: dict) -> list[str]:
    rows = digest["inputs"]
    if not rows:
        return ["Project inputs: none on the record yet. Ask the lead for what you need; do not invent inputs."]
    lines = ["Project inputs. The whole team works from these. Cite an input's id when a finding rests on it:"]
    for row in rows:
        if row["blank"]:
            continue
        note = " (starting value, not confirmed by the designer)" if row["unconfirmed"] else ""
        lines.append(f"- [{row['id']}] {row['name']}: {row['text']}{note}")
    blank = [row["name"] for row in rows if row["blank"]]
    if blank:
        lines.append("- Blank on the form: " + ", ".join(blank))
    return lines


def specialist_request(
    record: Record,
    project_id: str,
    slug: str,
    brief: str,
    inputs_given: dict | None,
    pending: list[dict],
) -> str:
    """The user message a specialist receives: the brief, the inputs, what needs it, and the record."""
    snapshot = record.snapshot(project_id)
    digest = status.build(snapshot)
    parts = [
        f"You are the specialist {slug} on this job. The lead delegated this task:",
        brief.strip(),
    ]
    if inputs_given:
        parts.append("Inputs from the lead:\n" + json.dumps(inputs_given, indent=2, sort_keys=True, default=str))
    parts.append("\n".join(_input_lines(digest)))
    attention = status.attention_for(digest, slug, snapshot)
    if attention:
        parts.append("What on the record needs you:\n" + "\n".join(attention))
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
    parts.append("Project record so far (cite these ids in supports):\n" + status.record_text(snapshot))
    return "\n\n".join(parts)


def consult_request(record: Record, project_id: str, asker: str, slug: str, question: str, context: str) -> str:
    """The user message a specialist receives when another specialist asks it something."""
    snapshot = record.snapshot(project_id)
    digest = status.build(snapshot)
    parts = [
        f"You are the specialist {slug} on this job. The specialist {asker} is in the middle of its task and "
        "needs this from you before it can go on:",
        question.strip(),
    ]
    if context.strip():
        parts.append(f"What {asker} has so far:\n" + context.strip())
    parts.append(
        "Answer from your own method. Read the skill if you need it. If the answer is a number, run the calc "
        "tool. If the design rests on the answer, record it as a finding so it is on the record under your "
        f"name. Then answer {asker} in a few sentences with the record ids. If you cannot answer without "
        f"something from the designer, say exactly what is missing. You cannot consult in turn."
    )
    parts.append("\n".join(_input_lines(digest)))
    parts.append("Project record so far (cite these ids in supports):\n" + status.record_text(snapshot))
    return "\n\n".join(parts)


def pending_handoff_note(record: Record, project_id: str) -> str:
    """The lines on handoffs waiting on the record, as the lead's status block carries them.

    A handoff is delivered when the lead delegates to its receiver, so the lead
    has to see it. Recovery puts an interrupted delivery back here, so this is
    also how a relaunch reaches the lead. Empty when nothing is pending.
    """
    pending = record.pending_handoffs(project_id)
    if not pending:
        return ""
    lines = [status.PENDING_HEADER]
    for row in pending:
        note = " (re-queued after a relaunch)" if str(row.get("result") or "").startswith("Re-queued") else ""
        lines.append(f"- [{row['id']}] from {row['from_agent']} to {row['to_agent']}{note}: {row['brief']}")
    return "\n".join(lines)


def lead_status(record: Record, project_id: str) -> str:
    """The status block at the top of the lead's message, read from the record."""
    from fpfa.checker import check_line, coverage_lines

    snapshot = record.snapshot(project_id)
    text = status.lead_text(status.build(snapshot), check_line(snapshot))
    # What a design basis written now would be missing, so the lead does not present a partial one as whole.
    gaps = coverage_lines(snapshot)
    return text + ("\n" + "\n".join(gaps) if gaps else "")


def _new_rows(before: set[str], rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["id"] not in before]


def _unsettled(record: Record, project_id: str) -> dict:
    """What on the record still needs an end, as a delegate result carries it to the lead."""
    digest = status.build(record.snapshot(project_id))
    return {
        "objections": [
            {"review_id": row["id"], "finding_id": row["finding_id"], "by": row["by"], "against": row["author"],
             "finding": row["finding"], "note": row["note"], "status": row["status"]}
            for row in digest["objections"]
        ],
        "conflicting_facts": [
            {"key": f"{item['kind']}/{item['key']}",
             "values": [{"by": row["agent"], "value": row["value"], "id": row["id"]} for row in item["rows"]]}
            for item in digest["conflicts"]
        ],
        "on_another_value_than_the_project_input": [
            {"finding_id": row["finding_id"], "by": row["by"], "finding": row["finding"], "why": row["notes"]}
            for row in digest["alternatives"]
        ],
        "out_of_date": [
            {"kind": row["kind"], "id": row["id"], "by": row["by"], "what": row["text"], "why": row["reasons"][:2]}
            for row in digest["stale"]
        ],
    }


class SpecialistSession:
    """execute() for a specialist. consult runs here; everything else is the tool session.

    depth is 0 for a specialist the lead delegated to and 1 for one answering a
    consult, which may not consult in turn. usage sums what the consults cost.
    """

    def __init__(
        self,
        content_root: Path,
        record: Record,
        project_id: str,
        create: Callable[..., Any],
        *,
        agent: str,
        depth: int = 0,
        max_tokens: int = 16000,
        cancel: Any = None,
        observe: Callable[[dict], Any] | None = None,
    ):
        self.root = Path(content_root)
        self.record = record
        self.project_id = project_id
        self.create = create
        self.agent = agent
        self.depth = depth
        self.max_tokens = max_tokens
        self.cancel = cancel
        self.observe = observe
        self.tools = ToolSession(content_root, record=record, project_id=project_id, agent=agent)
        self.consults: list[dict] = []
        self.failed_consults = 0
        self.usage = empty_usage()

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name != CONSULT:
            return self.tools.execute(name, args)
        if self.depth > 0:
            raise RecordError(
                "You are answering a consult and cannot consult in turn. Answer from the record and your own "
                "tools, and say in your answer what you still need."
            )
        if len(self.consults) >= MAX_CONSULTS:
            raise RecordError(
                f"This task has used its {MAX_CONSULTS} consults. Record what is still open as a question or a "
                "handoff and say so in your summary."
            )
        if self.cancel is not None and self.cancel.is_set():
            raise TurnCancelled("Cancelled by the designer before the consult ran.")
        try:
            answer = consult(
                self.root, self.record, self.project_id, self.create,
                asker=self.agent, specialist=str(args.get("specialist") or ""),
                question=str(args.get("question") or ""), context=str(args.get("context") or ""),
                max_tokens=self.max_tokens, cancel=self.cancel, observe=self.observe,
            )
        except TurnCancelled as exc:
            _merge_usage(self.usage, getattr(exc, "usage", None))
            raise
        except Exception as exc:
            # The asker goes on with an error in place of an answer. What the failed consult had already
            # spent still belongs to this task.
            _merge_usage(self.usage, getattr(exc, "usage", None))
            self.failed_consults += 1
            raise
        self.consults.append(answer)
        _merge_usage(self.usage, answer.get("usage"))
        return {key: value for key, value in answer.items() if key != "usage"}


def consult(
    content_root: Path,
    record: Record,
    project_id: str,
    create: Callable[..., Any],
    *,
    asker: str,
    specialist: str,
    question: str,
    context: str = "",
    max_rounds: int = CONSULT_ROUNDS,
    max_tokens: int = 16000,
    cancel: Any = None,
    observe: Callable[[dict], Any] | None = None,
) -> dict:
    """One specialist asks another a question and gets its answer. The exchange is a record row.

    The asked specialist runs in its own context with its own role file and
    tools, may run calcs and record findings under its own name, and returns
    a short answer. It cannot consult in turn.
    """
    slug = (specialist or "").strip()
    text = (question or "").strip()
    if not text:
        raise RecordError("consult needs a question")
    if slug == asker:
        raise RecordError("consult asks another specialist. Name one of: "
                          + ", ".join(item for item in specialist_slugs(content_root) if item != asker))
    system = specialist_system(content_root, slug)
    name = _specialist_name(content_root, slug)
    started = time.time()
    was = next((row["status"] for row in record.agents(project_id) if row["name"] == name), "")
    record.set_agent(project_id, name=name, role_slug=slug, status="working")
    payload = {"context": context.strip()} if context.strip() else {}
    row = record.create_handoff(project_id, from_agent=asker, to_agent=slug, brief=text, payload=payload, kind=CONSULT)
    record.set_handoff(project_id, row["id"], status="delivered", by=asker)
    before_findings = {item["id"] for item in record.findings(project_id, include_retired=True)}
    before_calcs = {item["id"] for item in record.calcs(project_id)}
    session = SpecialistSession(content_root, record, project_id, create, agent=slug, depth=1,
                                max_tokens=max_tokens, cancel=cancel, observe=observe)
    heard = None if observe is None else (lambda event: observe({**event, "agent": f"{slug}, asked by {asker}"}))
    try:
        out = run_tool_loop(
            create,
            system=system,
            user_text=consult_request(record, project_id, asker, slug, text, context),
            tools=SPECIALIST_SCHEMAS,
            execute=session.execute,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
            cancel=cancel,
            observe=heard,
        )
    except TurnCancelled as exc:
        record.set_agent(project_id, name=name, role_slug=slug, status="interrupted")
        record.set_handoff(project_id, row["id"], status="cancelled", result="Cancelled by the designer.", by=asker)
        record.log_event(project_id, CONSULT, {
            "from": asker, "to": slug, "handoff": row["id"], "findings": 0, "cancelled": True,
            "usage": dict(getattr(exc, "usage", None) or empty_usage()), "stop_reason": "cancelled",
            "seconds": round(time.time() - started, 1),
        }, agent=asker)
        raise
    except Exception as exc:
        record.set_agent(project_id, name=name, role_slug=slug, status="error")
        record.set_handoff(project_id, row["id"], status="cancelled",
                           result=("The specialist did not answer: " + safe_error(exc))[:4000], by=asker)
        # The rounds it ran before it failed were billed. The request that failed returned no usage.
        spent = dict(getattr(exc, "usage", None) or empty_usage())
        record.log_event(project_id, CONSULT, {
            "from": asker, "to": slug, "handoff": row["id"], "findings": 0, "failed": True,
            "error": safe_error(exc)[:400], "usage": spent, "stop_reason": "error",
            "seconds": round(time.time() - started, 1),
        }, agent=asker)
        raise
    answer = (out.get("text") or "").strip()
    unfinished = incomplete_notice(out.get("stop_reason"))
    if not answer:
        answer = "(The specialist returned no answer.)"
    findings = [item for item in _new_rows(before_findings, record.findings(project_id, agent=slug))]
    calcs = [item for item in _new_rows(before_calcs, record.calcs(project_id)) if item.get("agent") == slug]
    record.set_handoff(project_id, row["id"], status="returned", result=answer[:4000], by=slug)
    # Answering a question does not change whether its own task was finished.
    record.set_agent(project_id, name=name, role_slug=slug, status=was if was in ("done", "idle") else "done")
    usage = out.get("usage") or empty_usage()
    record.log_event(project_id, CONSULT, {
        "from": asker, "to": slug, "handoff": row["id"], "findings": len(findings), "usage": usage,
        "stop_reason": out.get("stop_reason") or "", "seconds": round(time.time() - started, 1),
    }, agent=asker)
    result = {
        "from": slug,
        "exchange_id": row["id"],
        "answer": answer,
        "findings": [{"id": item["id"], "text": item["text"], "label": item["label"]} for item in findings],
        "calc_records": [{"id": item["id"], "tool": item["tool"]} for item in calcs],
        "question": text,
        "usage": usage,
    }
    if unfinished:
        result["note"] = f"{slug} did not finish its answer ({out.get('stop_reason')}). Treat it as partial."
    return result


def delegate(
    content_root: Path,
    record: Record,
    project_id: str,
    create: Callable[..., Any],
    *,
    specialist: str,
    brief: str,
    inputs: dict | None = None,
    max_rounds: int = SPECIALIST_ROUNDS,
    max_tokens: int = 16000,
    cancel: Any = None,
    observe: Callable[[dict], Any] | None = None,
) -> dict:
    """Run one specialist and return its structured contribution.

    observe hears the specialist's rounds and tools, each event carrying
    "agent": the specialist's slug.

    The lead's brief is written to the record first and marked returned when
    the specialist finishes. Handoffs waiting for the specialist are delivered
    with the brief. Rows the specialist writes carry its slug. The result
    also lists what on the record is still unsettled, so the lead reconciles
    from the tool result and not from memory.
    """
    slug = (specialist or "").strip()
    text = (brief or "").strip()
    if not text:
        raise RecordError("delegate needs a brief")
    if inputs is not None and not isinstance(inputs, dict):
        raise RecordError("inputs must be an object")
    system = specialist_system(content_root, slug)
    name = _specialist_name(content_root, slug)
    started = time.time()
    record.set_agent(project_id, name=name, role_slug=slug, status="working")
    lead_handoff = record.create_handoff(
        project_id, from_agent=LEAD, to_agent=slug, brief=text, payload=inputs or {}, kind="delegation",
    )
    record.set_handoff(project_id, lead_handoff["id"], status="delivered", by=LEAD)
    pending = [row for row in record.pending_handoffs(project_id, to_agent=slug) if row["id"] != lead_handoff["id"]]
    for row in pending:
        record.set_handoff(project_id, row["id"], status="delivered", by=LEAD)
    before = {
        "findings": {row["id"] for row in record.findings(project_id, include_retired=True)},
        "retired": {row["id"] for row in record.findings(project_id, include_retired=True) if row.get("superseded_by")},
        "questions": {row["id"] for row in record.questions(project_id)},
        "evidence": {row["id"] for row in record.evidence(project_id)},
        "calcs": {row["id"] for row in record.calcs(project_id)},
        "handoffs": {row["id"] for row in record.handoffs(project_id)},
        "reviews": {row["id"]: (row["position"], row["updated"]) for row in record.reviews(project_id)},
    }
    session = SpecialistSession(content_root, record, project_id, create, agent=slug, depth=0,
                                max_tokens=max_tokens, cancel=cancel, observe=observe)
    request = specialist_request(record, project_id, slug, text, inputs, pending)
    heard = None if observe is None else (lambda event: observe({**event, "agent": slug}))
    try:
        out = run_tool_loop(
            create,
            system=system,
            user_text=request,
            tools=SPECIALIST_SCHEMAS,
            execute=session.execute,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
            cancel=cancel,
            observe=heard,
        )
    except TurnCancelled as exc:
        record.set_agent(project_id, name=name, role_slug=slug, status="interrupted")
        record.set_handoff(project_id, lead_handoff["id"], status="cancelled", result="Cancelled by the designer.", by=LEAD)
        # The rounds the specialist ran were billed, and so were its consults. They close on the record
        # like a finished delegation.
        spent = dict(getattr(exc, "usage", None) or empty_usage())
        _merge_usage(spent, session.usage)
        exc.usage = spent
        record.log_event(project_id, "delegation", {
            "specialist": slug, "handoff": lead_handoff["id"], "findings": 0, "questions": 0, "handoffs": 0,
            "usage": spent, "stop_reason": "cancelled", "cancelled": True,
            "seconds": round(time.time() - started, 1),
        }, agent=LEAD)
        raise
    except Exception as exc:
        record.set_agent(project_id, name=name, role_slug=slug, status="error")
        record.set_handoff(project_id, lead_handoff["id"], status="cancelled",
                           result=("The specialist did not finish: " + safe_error(exc))[:4000], by=LEAD)
        # A failure does not un-spend what ran before it: the specialist's earlier rounds and its consults
        # were billed, and they close on the record like a finished delegation. The request that failed
        # returned no usage, so whether any part of it was billed is not known and is not in this figure.
        attach_usage(exc, session.usage)
        spent = dict(getattr(exc, "usage", None) or empty_usage())
        record.log_event(project_id, "delegation", {
            "specialist": slug, "handoff": lead_handoff["id"], "findings": 0, "questions": 0, "handoffs": 0,
            "usage": spent, "stop_reason": "error", "failed": True, "error": safe_error(exc)[:400],
            "seconds": round(time.time() - started, 1),
        }, agent=LEAD)
        raise
    unfinished = incomplete_notice(out.get("stop_reason"))
    summary = (out.get("text") or "").strip() or "(The specialist returned no text.)"
    findings = _new_rows(before["findings"], record.findings(project_id, agent=slug))
    retired = [row for row in record.findings(project_id, agent=slug, include_retired=True)
               if row.get("superseded_by") and row["id"] not in before["retired"]]
    questions = [row for row in _new_rows(before["questions"], record.questions(project_id)) if row["raised_by"] == slug]
    evidence = [row for row in _new_rows(before["evidence"], record.evidence(project_id)) if row.get("agent") == slug]
    calcs = [row for row in _new_rows(before["calcs"], record.calcs(project_id)) if row.get("agent") == slug]
    new_handoffs = [row for row in _new_rows(before["handoffs"], record.handoffs(project_id)) if row["from_agent"] == slug]
    handoffs = [row for row in new_handoffs if (row.get("kind") or "handoff") != CONSULT]
    current = {row["id"]: row for row in record.findings(project_id)}
    reviews = [row for row in record.reviews(project_id)
               if row["agent"] == slug and before["reviews"].get(row["id"]) != (row["position"], row["updated"])]
    for row in pending:
        record.set_handoff(project_id, row["id"], status="returned", result=f"Handled in {slug}'s contribution.", by=slug)
    record.set_handoff(project_id, lead_handoff["id"], status="returned", result=summary[:4000], by=slug)
    # A specialist that ran out of rounds did not finish. Its rows are kept; the roster says so.
    record.set_agent(project_id, name=name, role_slug=slug, status="interrupted" if unfinished else "done")
    usage = dict(out.get("usage") or empty_usage())
    _merge_usage(usage, session.usage)
    record.log_event(project_id, "delegation", {
        "specialist": slug, "handoff": lead_handoff["id"], "findings": len(findings),
        "questions": len(questions), "handoffs": len(handoffs), "reviews": len(reviews),
        "consults": len(session.consults), "usage": usage,
        "stop_reason": out.get("stop_reason") or "", "seconds": round(time.time() - started, 1),
    }, agent=LEAD)
    contribution = {
        "specialist": slug,
        "handoff_id": lead_handoff["id"],
        "complete": not unfinished,
        "summary": summary,
        "findings": [
            {"id": row["id"], "text": row["text"], "label": row["label"], "supports": row["supports"]}
            for row in findings
        ],
        "replaced_or_withdrawn": [
            {"id": row["id"], "now": "withdrawn" if row["superseded_by"] == "withdrawn" else row["superseded_by"],
             "note": row.get("retire_note") or ""} for row in retired
        ],
        "reviews": [
            {"id": row["id"], "finding_id": row["finding_id"], "position": row["position"], "note": row["note"],
             "of": (current.get(row["finding_id"]) or {}).get("agent", "")}
            for row in reviews
        ],
        "consults": [
            {"id": item["exchange_id"], "asked": item["from"], "question": item["question"], "answer": item["answer"]}
            for item in session.consults
        ],
        "questions": [{"id": row["id"], "text": row["text"], "to": row.get("audience") or "engineer"} for row in questions],
        "evidence": [{"id": row["id"], "document": row["document"], "section": row["section"], "status": row["status"]} for row in evidence],
        "calc_records": [{"id": row["id"], "tool": row["tool"]} for row in calcs],
        "handoffs": [{"id": row["id"], "to": row["to_agent"], "brief": row["brief"]} for row in handoffs],
        "delivered_handoffs": [row["id"] for row in pending],
        "still_unsettled_on_the_record": _unsettled(record, project_id),
        "stop_reason": out.get("stop_reason") or "",
        "usage": usage,
    }
    if unfinished:
        contribution["note"] = (
            f"{slug} did not finish: {unfinished} What it recorded is kept. Delegate to it again to finish; "
            "recorded calcs replay."
        )
    return contribution


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
        max_rounds: int = SPECIALIST_ROUNDS,
        max_tokens: int = 16000,
        cancel: Any = None,
        observe: Callable[[dict], Any] | None = None,
    ):
        self.observe = observe
        self.root = Path(content_root)
        self.record = record
        self.project_id = project_id
        self.create = create
        self.max_rounds = max_rounds
        self.max_tokens = max_tokens
        self.cancel = cancel
        self.tools = ToolSession(content_root, record=record, project_id=project_id, agent=LEAD)
        self.delegations: list[dict] = []
        self.checks: list[dict] = []
        # What the lead did besides delegating, for the app-written block under its reply.
        self.inputs_set: list[dict] = []
        self.answered: list[dict] = []
        self.resolved: list[dict] = []
        # Delegations and checks that ended on an error this turn: what, who, and the error.
        self.failed: list[dict] = []
        self.usage = empty_usage()
        self.usage["rounds"] = 0

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name in TEAM_TOOL_NAMES and self.cancel is not None and self.cancel.is_set():
            raise TurnCancelled("Cancelled by the designer before the team tool ran.")
        if name == "list_specialists":
            return {"specialists": list_specialists(self.root)}
        if name == "delegate":
            try:
                contribution = delegate(
                    self.root, self.record, self.project_id, self.create,
                    specialist=str(args.get("specialist") or ""), brief=str(args.get("brief") or ""),
                    inputs=args.get("inputs"), max_rounds=self.max_rounds, max_tokens=self.max_tokens,
                    cancel=self.cancel, observe=self.observe,
                )
            except TurnCancelled as exc:
                # The interrupted specialist's rounds count toward the task.
                _merge_usage(self.usage, getattr(exc, "usage", None))
                raise
            except Exception as exc:
                # The lead goes on with an error in place of a contribution. What the specialist had spent
                # before it failed counts toward the task, and the block under the reply says it failed.
                _merge_usage(self.usage, getattr(exc, "usage", None))
                self.failed.append({"what": "delegation", "who": str(args.get("specialist") or ""),
                                    "error": safe_error(exc)[:300]})
                raise
            self.delegations.append(contribution)
            _merge_usage(self.usage, contribution.get("usage"))
            return contribution
        if name == "request_check":
            from fpfa.checker import check_record

            try:
                outcome = check_record(self.root, self.record, self.project_id, self.create, cancel=self.cancel)
            except TurnCancelled:
                raise
            except Exception as exc:
                self.failed.append({"what": "trace check", "who": CHECKER_ROLE, "error": safe_error(exc)[:300]})
                raise
            # The check's usage closes on its own record_check event, which the cost report counts.
            # It is not added to the turn's total, or it would be counted twice.
            self.checks.append(outcome)
            return {key: value for key, value in outcome.items() if key != "verdict"} | {"verdict": outcome.get("verdict", "")}
        if name == "set_input":
            return self._set_input(args)
        if name == "answer_question":
            return self._answer_question(args)
        if name == "set_plan":
            return self._set_plan(args)
        if name == "resolve_disagreement":
            return self._resolve(args)
        return self.tools.execute(name, args)

    def _set_input(self, args: dict) -> dict:
        name = str(args.get("name") or "").strip()
        converted: dict | None = None
        try:
            kind = inputs.kind_of(name)
            if name == "segments":
                raw = args.get("segments")
                if raw is None and isinstance(args.get("value"), str) and args["value"].strip():
                    try:
                        raw = json.loads(args["value"])
                    except json.JSONDecodeError as exc:
                        raise inputs.InputError("segments takes the pipe list in the segments argument") from exc
                cooked = inputs.coerce(name, raw)
            else:
                # A figure the designer gave in another unit is converted to the input's own on a recorded
                # conversion row, and the input takes the result. Nothing is converted any other way.
                converted = self._converted_input(name, args.get("value"))
                cooked = inputs.coerce(name, converted["result"]["value"] if converted else args.get("value"))
                problem = inputs.run_problem(name, cooked) if cooked is not None and name in inputs.POSITIVE else ""
                if problem:
                    # A 0 density, area, fill flow, fill pressure, or fill time does not describe a zone.
                    raise inputs.InputError(problem)
        except (inputs.InputError, units.UnitError) as exc:
            raise RecordError(str(exc)) from exc
        if kind == inputs.BASIS_KIND:
            text = str(cooked)
            if not text:
                raise RecordError(f"{name} cannot be set to blank here. The designer clears it on the Inputs tab.")
            label = dict(BASIS_LABELS).get(name, GIVEN)
        else:
            text = inputs.encode(name, cooked)
            label = GIVEN
        why = str(args.get("why") or "").strip()
        source = inputs.source_text(inputs.SOURCE_CHAT) + (f": {why}" if why else "")
        if converted:
            # The designer's own figure and unit stay on the record beside the value the form takes.
            given, result = converted["given"], converted["result"]
            source += (f" (given as {given['value']:g} {given['unit']}; converted by the application to "
                       f"{result['value']:.6g} {result['unit']}, convert_units [{converted.get('record_id', '')}])")
        row = self.record.set_given(
            self.project_id, kind=kind, key=name, value=text, label=label, source=source[:2000], agent=LEAD,
        )
        shown_old = "not on the record"
        if row["previous"] is not None:
            old = inputs.decode(row["previous"]) if kind == inputs.INPUT_KIND else row["previous"]
            shown_old = inputs.show(name, old)
        shown_new = inputs.show(name, inputs.decode(text) if kind == inputs.INPUT_KIND else text)
        out: dict[str, Any] = {"id": row["id"], "name": name, "was": shown_old, "now": shown_new, "changed": row["changed"]}
        if converted:
            out["converted"] = {
                "given": f"{converted['given']['value']:g} {converted['given']['unit']}",
                "result": f"{converted['result']['value']:.6g} {converted['result']['unit']}",
                "record_id": converted.get("record_id", ""),
            }
        if row["changed"]:
            unsettled = _unsettled(self.record, self.project_id)["out_of_date"]
            out["out_of_date"] = unsettled
            out["note"] = (
                "Recorded. It will show on the zone form. " + (
                    f"{len(unsettled)} row{'s' if len(unsettled) != 1 else ''} used the old value and "
                    "must be brought up to date by the author before you quote them." if unsettled
                    else "Nothing on the record used the old value."
                )
            )
            self.inputs_set.append({"name": name, "was": shown_old, "now": shown_new})
        else:
            out["note"] = "The record already held this value. It is now marked as stated by the designer."
        return out

    def _converted_input(self, name: str, value: Any) -> dict | None:
        """A figure the designer gave in another unit, converted to the input's own by convert_units. Else None.

        "12.2 mm/min" for the density becomes gpm/ft² on a conversion row the
        record keeps, so the figure the designer gave and the one the form takes
        are both on the record. A bare number, a figure in the input's own unit,
        and a unit that does not convert to it are left to coerce(), which takes
        the first two and says what the input takes for the third.
        """
        own = inputs.unit_of(name)
        written = units.split(value)
        if not own or written is None:
            return None
        number, spelled = written
        try:
            source, target = units.unit(spelled), units.unit(own)
        except units.UnitError:
            return None
        if source.key == target.key:
            return None
        if source.dimension != target.dimension:
            raise units.UnitError(f"{name} takes {target.display}, and {value!r} is {units.kind(source.dimension)}, "
                                  f"not {units.kind(target.dimension)}.")
        return self.tools.execute(CONVERT_TOOL, {"value": number, "from_unit": spelled, "to_unit": own})

    def _answer_question(self, args: dict) -> dict:
        question_id = str(args.get("id") or "").strip()
        row = next((item for item in self.record.questions(self.project_id) if item["id"] == question_id), None)
        if row is None:
            raise RecordError(f"no question {question_id} on this job")
        if row["status"] != "open":
            raise RecordError(f"question {question_id} is already {row['status']}")
        done = self.record.answer_question(self.project_id, question_id, answer=args.get("answer"), by=ANSWERED_IN_CHAT)
        self.answered.append({"id": question_id, "text": row["text"], "answer": done["answer"]})
        return {"id": question_id, "status": done["status"],
                "note": "Closed. Now record what the answer changes: set_input for a project input, record_fact for a project fact."}

    def _set_plan(self, args: dict) -> dict:
        objective = str(args.get("objective") or "").strip()
        raw = args.get("steps")
        if not objective:
            raise RecordError("set_plan needs the objective")
        if not isinstance(raw, list) or not raw:
            raise RecordError("set_plan needs at least one step")
        steps = []
        for item in raw[:20]:
            if not isinstance(item, dict) or not str(item.get("title") or "").strip():
                raise RecordError("each step needs a title")
            state = str(item.get("status") or "todo").strip().lower()
            if state not in status.STEP_STATES:
                raise RecordError("a step's status is one of: " + ", ".join(status.STEP_STATES))
            steps.append({"title": str(item["title"]).strip()[:300], "owner": str(item.get("owner") or "").strip()[:80],
                          "status": state})
        self.record.log_event(self.project_id, status.PLAN_EVENT, {"objective": objective[:600], "steps": steps}, agent=LEAD)
        return {"objective": objective, "steps": len(steps), "done": sum(1 for step in steps if step["status"] == "done")}

    def _resolve(self, args: dict) -> dict:
        ident = str(args.get("id") or "").strip()
        outcome = str(args.get("outcome") or "").strip().lower()
        reason = str(args.get("reason") or "").strip()
        if outcome not in ("stands", "escalated"):
            raise RecordError(
                "outcome is stands or escalated. If the objection is right, delegate to the author to revise the "
                "finding, or withdraw the finding."
            )
        if not reason:
            raise RecordError("resolve_disagreement needs the reason")
        open_rows = [row for row in self.record.reviews(self.project_id)
                     if row["position"] == "object" and row["status"] in ("open", "escalated")]
        review = next((row for row in open_rows if row["id"] == ident), None)
        if review is None:
            on_finding = [row for row in open_rows if row["finding_id"] == ident]
            if len(on_finding) == 1:
                review = on_finding[0]
            elif len(on_finding) > 1:
                raise RecordError("more than one objection is open on that finding. Pass the review id: "
                                  + ", ".join(row["id"] for row in on_finding))
        if review is None:
            raise RecordError(f"no open objection {ident} on this job")
        finding = next((row for row in self.record.findings(self.project_id, include_retired=True)
                        if row["id"] == review["finding_id"]), {})
        out: dict[str, Any] = {"id": review["id"], "finding_id": review["finding_id"], "outcome": outcome}
        if outcome == "stands":
            decision = self.record.record_decision(
                self.project_id, decided_by=LEAD, label="use best judgment", supports=[review["finding_id"]],
                text=(f"The objection by {review['agent']} to {finding.get('agent', 'the')} finding "
                      f"[{review['finding_id']}] is not upheld. The finding stands."),
                basis=reason, review_id=review["id"],
            )
            self.record.close_review(self.project_id, review["id"], status="resolved", by=LEAD,
                                     resolution=f"The lead settled it; the finding stands: {reason} [decision {decision['id']}]")
            out["decision_id"] = decision["id"]
        else:
            audience = str(args.get("to") or "engineer").strip().lower()
            audience = "designer" if audience in ("designer", "user", "the designer") else "engineer"
            question = self.record.open_question(
                self.project_id, raised_by=LEAD, audience=audience,
                text=(f"The team could not settle this. {finding.get('agent', 'One specialist')} found: "
                      f"\"{finding.get('text', '')}\" {review['agent']} objects: {review['note']} {reason}"),
            )
            self.record.close_review(self.project_id, review["id"], status="escalated", by=LEAD,
                                     resolution=f"Escalated to the {audience if audience == 'designer' else 'engineer of record'} "
                                                f"as question [{question['id']}]: {reason}")
            out["question_id"] = question["id"]
            out["to"] = audience
        self.resolved.append({"review_id": review["id"], "finding_id": review["finding_id"], "outcome": outcome,
                              "by": review["agent"], "against": finding.get("agent", ""), "reason": reason})
        return out


def team_summary(out: dict | None, audit: dict | None = None) -> str:
    """Markdown the window appends under a lead reply: who contributed what, what passed between
    the specialists, the check, and what the application found when it looked up the reply's figures.

    Written by the app from the turn's result, not by the model. audit is
    reply_audit.audit()'s result for the reply. Empty when the turn delegated
    nothing, ran no check, changed no input, and every figure was found.
    """
    if not isinstance(out, dict):
        return ""
    from fpfa import reply_audit

    delegations = out.get("delegations") or []
    checks = out.get("checks") or []
    changed = out.get("inputs_set") or []
    resolved = out.get("resolved") or []
    failed = out.get("failed") or []
    figure_lines = reply_audit.lines(audit)
    if not delegations and not checks and not changed and not resolved and not failed:
        about_figures = bool((audit or {}).get("unfound") or (audit or {}).get("stale"))
        head = "**Figures in this reply**" if about_figures else "**In this reply**"
        return "\n".join([head] + figure_lines) if figure_lines else ""
    lines = ["**Team**"]
    for item in failed:
        who = f" to {item.get('who')}" if item.get("what") == "delegation" and item.get("who") else ""
        lines.append(f"- FAILED: the {item.get('what')}{who} ended on an error ({_clip(item.get('error'), 160)}). "
                     "What had been recorded before it is kept and may be partial. Asking again repeats that work "
                     "and is billed again; recorded calculations replay.")
    for item in changed:
        lines.append(f"- input {item.get('name')}: {item.get('was')} → {item.get('now')} (from the chat)")
    exchanges: list[str] = []
    # One line per specialist, however many times the lead went back to it.
    totals: dict[str, dict] = {}
    for item in delegations:
        row = totals.setdefault(str(item.get("specialist")), {"passes": 0, "unfinished": False})
        row["passes"] += 1
        row["unfinished"] = item.get("complete") is False
        for key in ("findings", "questions", "handoffs", "calc_records"):
            row[key] = row.get(key, 0) + len(item.get(key) or [])
    for who, row in totals.items():
        counts = []
        for key, word in (("findings", "finding"), ("questions", "question"), ("handoffs", "handoff"), ("calc_records", "calc record")):
            number = row.get(key, 0)
            if number:
                counts.append(f"{number} {word}{'s' if number != 1 else ''}")
        detail = ", ".join(counts) if counts else "no rows written"
        if row["passes"] > 1:
            detail += f", in {row['passes']} passes"
        if row["unfinished"]:
            detail += " (did not finish)"
        lines.append(f"- {who}: {detail}")
    for item in delegations:
        who = item.get("specialist")
        for consult_row in item.get("consults") or []:
            exchanges.append(f"- {who} asked {consult_row.get('asked')}: {_clip(consult_row.get('question'), 140)}")
        agreed = [row for row in item.get("reviews") or [] if row.get("position") == "agree"]
        if agreed:
            authors = sorted({row.get("of") or "another contributor" for row in agreed})
            exchanges.append(f"- {who} reviewed and agreed with {len(agreed)} finding"
                             f"{'s' if len(agreed) != 1 else ''} by {', '.join(authors)}")
        for row in item.get("reviews") or []:
            if row.get("position") == "object":
                exchanges.append(f"- {who} objected to a finding by {row.get('of') or 'another contributor'}: "
                                 f"{_clip(row.get('note'), 180)}")
        for row in item.get("replaced_or_withdrawn") or []:
            how = "withdrew" if row.get("now") == "withdrawn" else "revised"
            exchanges.append(f"- {who} {how} a finding")
    for item in resolved:
        if item.get("outcome") == "stands":
            exchanges.append(f"- the lead settled {item.get('by')}'s objection: the finding stands")
        else:
            exchanges.append(f"- the lead escalated {item.get('by')}'s objection as a question")
    if exchanges:
        lines.append("Between the specialists:")
        lines.extend(exchanges)
    if delegations:
        still = (delegations[-1].get("still_unsettled_on_the_record") or {})
        open_count = len([row for row in still.get("objections") or [] if row.get("status") == "open"])
        if open_count:
            lines.append(f"- {open_count} objection{'s' if open_count != 1 else ''} still open")
    if checks:
        from fpfa.checker import summary_line

        lines.append("- " + summary_line(checks[-1]))
    lines.extend(figure_lines)
    lines.append("Details are on the Team tab.")
    return "\n".join(lines)


def _clip(text: Any, limit: int) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _merge_usage(total: dict, usage: dict | None) -> None:
    if not isinstance(usage, dict):
        return
    for key, value in usage.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        total[key] = int(total.get(key, 0)) + int(value)


def __getattr__(name: str):
    """The checker's names, where they used to live. Imported late: fpfa.checker imports this module."""
    if name in ("CHECK_EVENT", "build_record_packet", "check_record", "check_token", "export_gate", "latest_check"):
        from fpfa import checker

        return getattr(checker, name)
    raise AttributeError(name)
