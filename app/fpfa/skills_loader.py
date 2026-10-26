"""Read skills/<slug>/SKILL.md from the content pack."""

from __future__ import annotations

import re
from pathlib import Path


def skills_dir(content_root: Path) -> Path:
    return content_root / "skills"


def list_skills(content_root: Path) -> list[dict]:
    root = skills_dir(content_root)
    found = []
    if not root.is_dir():
        return found
    for path in sorted(root.iterdir()):
        skill = path / "SKILL.md"
        if not skill.is_file():
            continue
        text = skill.read_text(encoding="utf-8")
        meta = _frontmatter(text)
        found.append({
            "slug": path.name,
            "name": meta.get("name") or path.name,
            "description": meta.get("description") or "",
        })
    return found


def read_skill(content_root: Path, slug: str) -> str:
    slug = slug.strip().strip("/").replace("\\", "/")
    if "/" in slug or slug in ("", ".", ".."):
        raise ValueError("skill slug must be a single folder name")
    path = skills_dir(content_root) / slug / "SKILL.md"
    if not path.is_file():
        known = ", ".join(item["slug"] for item in list_skills(content_root)) or "(none)"
        raise FileNotFoundError(f"No skill {slug!r}. Known skills: {known}")
    return path.read_text(encoding="utf-8")


def spec_notes(content_root: Path, limit: int = 12, chars: int = 4000) -> list[dict]:
    """Master language from specs/*.md. README is the folder guide, not a spec.

    The cap covers the in-scope section set. A cap of three dropped
    Section 21 13 19 once the earlier section files sorted first.
    """
    folder = content_root / "specs"
    notes = []
    if not folder.is_dir():
        return notes
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        notes.append({"name": path.name, "text": path.read_text(encoding="utf-8")[:chars]})
        if len(notes) >= limit:
            break
    return notes


def frontmatter(text: str) -> dict[str, str]:
    """name and description from a SKILL.md or ROLE.md frontmatter block."""
    return _frontmatter(text)


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    name = _field(block, "name")
    description = _field(block, "description")
    return {"name": name, "description": description}


def _field(block: str, key: str) -> str:
    match = re.search(rf"(?m)^{key}:\s*(.*)$", block)
    if not match:
        return ""
    first = match.group(1).strip()
    if first in (">-", ">", "|"):
        lines = []
        for line in block[match.end():].splitlines():
            if re.match(r"^[A-Za-z0-9_]+:\s*", line):
                break
            lines.append(line.strip())
        return re.sub(r"\s+", " ", " ".join(lines)).strip()
    return first.strip("\"'")
