"""Read roles/<slug>/ROLE.md from the content pack.

Same idea as skills/<slug>/SKILL.md. The application lists these files and
returns one file when the model calls read_role. It does not copy the prompt
into Python.
"""

from __future__ import annotations

from pathlib import Path

from fpfa.skills_loader import frontmatter


def roles_dir(content_root: Path) -> Path:
    return content_root / "roles"


def list_roles(content_root: Path) -> list[dict]:
    root = roles_dir(content_root)
    found = []
    if not root.is_dir():
        return found
    for path in sorted(root.iterdir()):
        role = path / "ROLE.md"
        if not role.is_file():
            continue
        text = role.read_text(encoding="utf-8")
        meta = frontmatter(text)
        found.append({
            "slug": path.name,
            "name": meta.get("name") or path.name,
            "description": meta.get("description") or "",
        })
    return found


def read_role(content_root: Path, slug: str) -> str:
    slug = slug.strip().strip("/").replace("\\", "/")
    if "/" in slug or slug in ("", ".", ".."):
        raise ValueError("role slug must be a single folder name")
    path = roles_dir(content_root) / slug / "ROLE.md"
    if not path.is_file():
        known = ", ".join(item["slug"] for item in list_roles(content_root)) or "(none)"
        raise FileNotFoundError(f"No role {slug!r}. Known roles: {known}")
    return path.read_text(encoding="utf-8")
