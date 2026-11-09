"""Everyday agent path.

A typed question loads roles/<slug>/ROLE.md, modes/<slug>/MODE.md, and
skills/<slug>/SKILL.md from the content pack, then calls the calc tools.
The tool plan in workflow.py still owns the tables and the docx. This module
does not paste method bodies, role prompts, or mode text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import incomplete_notice, run_tool_loop
from fpfa.modes_loader import list_modes, normalize_mode, read_mode
from fpfa.record import Record
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


def everyday_reply(out: dict) -> str:
    """Thread text for one everyday turn. An unfinished reply is labeled first."""
    text = out.get("text") or "(Claude returned no text.)"
    notice = incomplete_notice(out.get("stop_reason"))
    if notice:
        return f"{notice}\n\n{text}"
    return text


def run_everyday(
    content_root: Path,
    create: Callable[..., Any],
    user_text: str,
    *,
    mode: str | None = None,
    required: list[str] | None = None,
    max_rounds: int = 16,
    max_tokens: int = 16000,
    record: Record | None = None,
    project_id: str | None = None,
    agent: str = "lead",
    cancel: Any = None,
) -> dict:
    """One everyday turn. create() is Messages.create. Tools run in calcs/.

    With record and project_id, calc calls and record tools write to that
    job's record as agent, and the turn is the lead of a team: it gets
    list_specialists, delegate, and request_check, and the result carries
    the specialists' contributions and the summed usage. Without them,
    nothing is recorded and the tool list is the plain one.
    """
    if record is not None and project_id:
        from fpfa.team import TEAM_SCHEMAS, TeamSession

        team = TeamSession(
            content_root, record, project_id, create,
            max_rounds=max_rounds, max_tokens=max_tokens, cancel=cancel,
        )
        record.set_agent(project_id, name="Lead", role_slug=agent, status="working")
        try:
            out = run_tool_loop(
                create,
                system=assemble_system(content_root, mode, team=True),
                user_text=user_text,
                tools=TEAM_SCHEMAS,
                execute=team.execute,
                required=list(required or []),
                max_rounds=max_rounds,
                max_tokens=max_tokens,
                cancel=cancel,
            )
        except Exception:
            record.set_agent(project_id, name="Lead", role_slug=agent, status="error")
            raise
        record.set_agent(project_id, name="Lead", role_slug=agent, status="done")
        lead_usage = dict(out.get("usage") or {})
        total = dict(lead_usage)
        for key, value in team.usage.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            total[key] = int(total.get(key, 0)) + int(value)
        out["usage"] = total
        out["lead_usage"] = lead_usage
        out["delegations"] = team.delegations
        out["checks"] = team.checks
        return out
    session = ToolSession(content_root, record=record, project_id=project_id, agent=agent)
    return run_tool_loop(
        create,
        system=assemble_system(content_root, mode),
        user_text=user_text,
        tools=SCHEMAS,
        execute=session.execute,
        required=list(required or []),
        max_rounds=max_rounds,
        max_tokens=max_tokens,
        cancel=cancel,
    )
