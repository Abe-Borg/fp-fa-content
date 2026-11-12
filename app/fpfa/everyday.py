"""Everyday agent path.

A typed question loads roles/<slug>/ROLE.md, modes/<slug>/MODE.md, and
skills/<slug>/SKILL.md from the content pack, then calls the calc tools.
The tool plan in workflow.py still owns the tables and the docx. This module
does not paste method bodies, role prompts, or mode text.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import SCHEMAS, ToolSession, designer_words
from fpfa.claude_client import MAX_OUTPUT_TOKENS, TurnCancelled, incomplete_notice, run_tool_loop
from fpfa.modes_loader import list_modes, normalize_mode, read_mode
from fpfa.record import TURN_START, Record
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, spec_notes

EVERYDAY_ROLE = "everyday"
# Drafting roles the zone narrative is asked to read. The QA specialist is
# listed with them from the pack. The blind check is a separate turn.
SPECIALIST_ROLES = (
    "fp-sprinkler",
    "fa-releasing",
    "spec-draft",
)


def assemble_system(content_root: Path, mode: str | None = None, *, team: bool = False) -> str:
    """System text for one everyday turn.

    team=True appends the lead's team paragraph. It is set when the turn has
    a project record and a client to run specialists with.

    The everyday role file is the shell. The active mode file is the behavior
    for this reply. Other mode files and specialist role files are listed by
    slug and description. Their bodies stay on disk until read_mode or
    read_role is called, the same way skill bodies stay on disk until
    read_skill is called.
    """
    selected = normalize_mode(mode)
    if team:
        from fpfa.team import has_lead_role

        if has_lead_role(content_root):
            return _lead_system(content_root, selected)
    shell = read_role(content_root, EVERYDAY_ROLE).strip()
    active = read_mode(content_root, selected).strip()
    lines = [
        shell,
        "",
        f"Active mode file ({selected}). This is the behavior for this reply.",
        active,
        "",
        "Other modes in this content pack. Call read_mode before you apply one. "
        "The description is not the mode.",
    ]
    for item in list_modes(content_root):
        if item["slug"] == selected:
            continue
        lines.append(f"- {item['slug']}: {item['description']}")
    lines.append("")
    lines.append(
        "Specialist roles in this content pack. Call read_role before you apply one. "
        "The description is not the role."
    )
    for role in list_roles(content_root):
        if role["slug"] == EVERYDAY_ROLE:
            continue
        lines.append(f"- {role['slug']}: {role['description']}")
    lines.append("")
    lines.append("Skills in this content pack:")
    for skill in list_skills(content_root):
        lines.append(f"- {skill['slug']}: {skill['description']}")
    lines.append("")
    lines.append(
        "Project record. record_fact, record_evidence, record_finding, open_question, and "
        "record_decision write to this job's record. read_record shows it with row ids. "
        "Calc tools record themselves. Write a finding with the calc record ids that support it. "
        "A question the designer must answer is open_question."
    )
    if team:
        from fpfa.team import TEAM_PARAGRAPH

        lines.append("")
        lines.append(TEAM_PARAGRAPH)
    # Every spec file goes in whole. Nothing here shortens or summarizes it.
    notes = spec_notes(content_root)
    if notes:
        lines.append("")
        lines.append("Spec notes from the content pack. They are draft language. Verify before issuing.")
        for note in notes:
            lines.append(f"## {note['name']}")
            lines.append(note["text"])
    return "\n".join(lines)


def _lead_system(content_root: Path, selected: str) -> str:
    """System text for the lead of a team: its own role file, the active mode, and the indexes.

    The lead's role file is the shell. It is told who the specialists are and
    delegates to them; it is not handed their role bodies to wear. The text is
    the same on every round and every turn in a mode, so it is read from the
    cache after the first request.
    """
    from fpfa.team import CHECKER_ROLE, LEAD_ROLE, TEAM_PARAGRAPH, list_specialists

    lines = [
        read_role(content_root, LEAD_ROLE).strip(),
        "",
        f"Active mode file ({selected}). It shapes the reply. The team rules above still hold.",
        read_mode(content_root, selected).strip(),
        "",
        "Other modes in this content pack. Call read_mode before you apply one. "
        "The description is not the mode.",
    ]
    for item in list_modes(content_root):
        if item["slug"] == selected:
            continue
        lines.append(f"- {item['slug']}: {item['description']}")
    lines.append("")
    lines.append(
        "Specialists on this team. Delegate to them with delegate. list_specialists says what each owns, "
        "what it needs from the others, and what it reviews."
    )
    for role in list_specialists(content_root):
        lines.append(f"- {role['slug']}: {role['description']}")
    lines.append(f"The checker is {CHECKER_ROLE}. request_check runs it. You do not delegate to it.")
    lines.append("")
    lines.append("Skills in this content pack:")
    for skill in list_skills(content_root):
        lines.append(f"- {skill['slug']}: {skill['description']}")
    lines.append("")
    lines.append(
        "Project record. record_fact, record_evidence, record_finding, open_question, and "
        "record_decision write to this job's record. read_record shows it with row ids. "
        "Calc tools record themselves. Write a finding with the calc record ids that support it. "
        "A question the designer must answer is open_question with to designer."
    )
    lines.append("")
    lines.append(TEAM_PARAGRAPH)
    # Every spec file goes in whole. Nothing here shortens or summarizes it.
    notes = spec_notes(content_root)
    if notes:
        lines.append("")
        lines.append("Spec notes from the content pack. They are draft language. Verify before issuing.")
        for note in notes:
            lines.append(f"## {note['name']}")
            lines.append(note["text"])
    return "\n".join(lines)


def everyday_reply(out: dict) -> str:
    """Thread text for one everyday turn. An unfinished reply is labeled first."""
    text = out.get("text") or "(Claude returned no text.)"
    notice = incomplete_notice(out.get("stop_reason"))
    if notice:
        return f"{notice}\n\n{text}"
    return text


def _task_total(lead_usage: dict | None, team_usage: dict | None) -> dict:
    """The lead's own rounds plus every delegation and check it ran."""
    total = dict(lead_usage or {})
    for key, value in (team_usage or {}).items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        total[key] = int(total.get(key, 0)) + int(value)
    return total


def run_everyday(content_root: Path, create: Callable[..., Any], user_text: str, **options: Any) -> dict:
    """One everyday turn (_run_everyday), with the designer's SI figures held for its length.

    A calc tool any agent calls in the turn refuses one of those figures in
    a field that takes US units (calc_tools.si_figure_problem): the figure
    goes through convert_units first.
    """
    with designer_words(user_text):
        return _run_everyday(content_root, create, user_text, **options)


def _run_everyday(
    content_root: Path,
    create: Callable[..., Any],
    user_text: str,
    *,
    mode: str | None = None,
    required: list[str] | None = None,
    max_rounds: int | None = None,
    max_tokens: int = MAX_OUTPUT_TOKENS,
    record: Record | None = None,
    project_id: str | None = None,
    agent: str = "lead",
    cancel: Any = None,
    observe: Callable[[dict], Any] | None = None,
) -> dict:
    """One everyday turn. create() is Messages.create. Tools run in calcs/.

    observe is the window's progress listener (claude_client.run_tool_loop).
    It hears the lead's rounds and tools, and each specialist's with the
    specialist's slug on the event.

    With record and project_id, calc calls and record tools write to that
    job's record as agent, and the turn is the lead of a team: it gets
    list_specialists, delegate, and request_check, and the result carries
    the specialists' contributions and the summed usage. Without them,
    nothing is recorded and the tool list is the plain one.
    """
    if record is not None and project_id:
        from fpfa.team import LEAD_ROUNDS, SPECIALIST_ROUNDS, TeamSession, lead_schemas, lead_status

        started = time.time()
        team = TeamSession(
            content_root, record, project_id, create,
            max_rounds=SPECIALIST_ROUNDS, max_tokens=max_tokens, cancel=cancel, observe=observe,
        )
        # Where the job stands rides at the top of the user message, read from the record: the plan,
        # the inputs, what changed, what is out of date, open objections, and handoffs waiting. It
        # varies per turn, so it is never part of the cached system text.
        user_text = lead_status(record, project_id) + "\n\n" + user_text
        # What the block showed has now been read. An answer given on the panel after this is news to the next turn.
        record.log_event(project_id, TURN_START, {}, agent=agent)
        record.set_agent(project_id, name="Lead", role_slug=agent, status="working")
        try:
            out = run_tool_loop(
                create,
                system=assemble_system(content_root, mode, team=True),
                user_text=user_text,
                tools=lead_schemas(content_root),
                execute=team.execute,
                required=list(required or []),
                max_rounds=max_rounds or LEAD_ROUNDS,
                max_tokens=max_tokens,
                cancel=cancel,
                observe=observe,
            )
        except TurnCancelled as exc:
            # The rounds that ran were billed. Close the task on the record with what they cost.
            record.set_agent(project_id, name="Lead", role_slug=agent, status="interrupted")
            record.log_event(project_id, "turn", {
                "usage": _task_total(getattr(exc, "usage", None), team.usage),
                "lead_usage": dict(getattr(exc, "usage", None) or {}),
                "delegations": len(team.delegations), "checks": len(team.checks),
                "cancelled": True, "stop_reason": "cancelled", "seconds": round(time.time() - started, 1),
            }, agent=agent)
            raise
        except Exception as exc:
            record.set_agent(project_id, name="Lead", role_slug=agent, status="error")
            # The turn failed. Its rounds up to the failure, and every delegation it had run, were billed, and
            # the record closes the task with them. The request that failed returned no usage.
            from fpfa.claude_client import safe_error

            known = _task_total(getattr(exc, "usage", None), team.usage)
            record.log_event(project_id, "turn", {
                "usage": known, "lead_usage": dict(getattr(exc, "usage", None) or {}),
                "delegations": len(team.delegations), "checks": len(team.checks),
                "cancelled": False, "failed": True, "error": safe_error(exc)[:400], "stop_reason": "error",
                "failed_inside": len(team.failed), "seconds": round(time.time() - started, 1),
            }, agent=agent)
            raise
        record.set_agent(project_id, name="Lead", role_slug=agent, status="done")
        lead_usage = dict(out.get("usage") or {})
        total = _task_total(lead_usage, team.usage)
        out["usage"] = total
        out["lead_usage"] = lead_usage
        out["delegations"] = team.delegations
        out["checks"] = team.checks
        out["inputs_set"] = team.inputs_set
        out["answered"] = team.answered
        out["resolved"] = team.resolved
        out["failed"] = team.failed
        out["seconds"] = round(time.time() - started, 1)
        # The events row that closes the task carries the whole task's usage.
        record.log_event(project_id, "turn", {
            "usage": total, "lead_usage": lead_usage,
            "delegations": len(team.delegations), "checks": len(team.checks),
            "cancelled": False, "stop_reason": out.get("stop_reason") or "", "seconds": out["seconds"],
            "failed_inside": len(team.failed),
        }, agent=agent)
        return out
    session = ToolSession(content_root, record=record, project_id=project_id, agent=agent)
    return run_tool_loop(
        create,
        system=assemble_system(content_root, mode),
        user_text=user_text,
        tools=SCHEMAS,
        execute=session.execute,
        required=list(required or []),
        max_rounds=max_rounds or 16,
        max_tokens=max_tokens,
        cancel=cancel,
        observe=observe,
    )
