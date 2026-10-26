"""Everyday agent path.

A typed question loads roles/<slug>/ROLE.md and skills/<slug>/SKILL.md from
the content pack, then calls the calc tools. The tool plan in workflow.py
still owns the tables and the docx. This module does not paste method bodies
or specialist prompts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import run_tool_loop
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, spec_notes

EVERYDAY_ROLE = "everyday"
SPECIALIST_ROLES = (
    "fp-sprinkler",
    "fa-releasing",
    "spec-draft",
)


def assemble_system(content_root: Path) -> str:
    """System text for one everyday turn.

    The everyday role file is the shell. Other role files are listed by slug
    and description. Their bodies stay on disk until read_role is called,
    the same way skill bodies stay on disk until read_skill is called.
    """
    shell = read_role(content_root, EVERYDAY_ROLE).strip()
    lines = [
        shell,
        "",
        "Specialist roles in this content pack. Call read_role before you apply one. "
        "The description is not the role.",
    ]
    for role in list_roles(content_root):
        if role["slug"] == EVERYDAY_ROLE:
            continue
        lines.append(f"- {role['slug']}: {role['description']}")
    lines.append("")
    lines.append("Skills in this content pack:")
    for skill in list_skills(content_root):
        lines.append(f"- {skill['slug']}: {skill['description']}")
    notes = spec_notes(content_root)
    if notes:
        lines.append("")
        lines.append("Spec notes from the content pack. They are draft language. Verify before issuing.")
        for note in notes:
            lines.append(f"## {note['name']}")
            lines.append(note["text"])
    return "\n".join(lines)


def run_everyday(
    content_root: Path,
    create: Callable[..., Any],
    user_text: str,
    *,
    required: list[str] | None = None,
    max_rounds: int = 16,
    max_tokens: int = 16000,
) -> dict:
    """One everyday turn. create() is Messages.create. Tools run in calcs/."""
    session = ToolSession(content_root)
    return run_tool_loop(
        create,
        system=assemble_system(content_root),
        user_text=user_text,
        tools=SCHEMAS,
        execute=session.execute,
        required=list(required or []),
        max_rounds=max_rounds,
        max_tokens=max_tokens,
    )
