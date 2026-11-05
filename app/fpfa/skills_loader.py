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


def read_starter_cites(content_root: Path, slug: str) -> dict:
    """Cite list from a skill's starter block. The method body stays in the file.

    A percent in the block is an input. This loader does not invent one.
    """
    text = read_skill(content_root, slug)
    match = re.search(r"(?ms)^```starter\s*\n(.*?)^```\s*$", text)
    if not match:
        raise ValueError(f"Skill {slug} has no starter block")
    return _parse_starter(match.group(1), slug)


def _parse_starter(block: str, slug: str) -> dict:
    screens: list[dict] = []
    current: dict | None = None
    election: dict[str, str] = {}
    duration: dict[str, str] = {}
    notes: list[str] = []
    screen_keys = {"pct", "basis", "section", "edition", "path"}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "screen":
            current = {"id": value}
            screens.append(current)
            continue
        if key in screen_keys:
            if current is None:
                raise ValueError(f"Skill {slug} starter has {key} before a screen")
            current[key] = value
            continue
        if key == "election":
            current = None
            election["value"] = value
            continue
        if key == "election_section":
            election["section"] = value
            continue
        if key == "duration":
            current = None
            duration["value"] = value
            continue
        if key == "duration_section":
            duration["section"] = value
            continue
        if key == "note":
            current = None
            notes.append(value)
    if not screens:
        raise ValueError(f"Skill {slug} starter has no screen")
    seen = set()
    for screen in screens:
        ident = screen.get("id") or ""
        if not ident or ident in seen:
            raise ValueError(f"Skill {slug} starter needs a unique screen id")
        seen.add(ident)
        if "pct" not in screen or "basis" not in screen or "section" not in screen:
            raise ValueError(f"Skill {slug} screen {ident} needs pct, basis, and section")
        try:
            pct = float(screen["pct"])
        except ValueError as exc:
            raise ValueError(f"Skill {slug} screen {ident} pct is not a number") from exc
        if screen["basis"] not in {"fuel", "diluted"}:
            raise ValueError(f"Skill {slug} screen {ident} basis must be fuel or diluted")
        screen["pct"] = pct
    if not election.get("value"):
        raise ValueError(f"Skill {slug} starter has no election")
    if not duration.get("value"):
        raise ValueError(f"Skill {slug} starter has no duration")
    return {
        "screens": screens,
        "election": election,
        "duration": duration,
        "notes": notes,
    }


def read_skill(content_root: Path, slug: str) -> str:
    slug = slug.strip().strip("/").replace("\\", "/")
    if "/" in slug or slug in ("", ".", ".."):
        raise ValueError("skill slug must be a single folder name")
    path = skills_dir(content_root) / slug / "SKILL.md"
    if not path.is_file():
        known = ", ".join(item["slug"] for item in list_skills(content_root)) or "(none)"
        raise FileNotFoundError(f"No skill {slug!r}. Known skills: {known}")
    return path.read_text(encoding="utf-8")


def spec_notes(content_root: Path) -> list[dict]:
    """Master language from specs/*.md, every file in full, sorted by name.

    README is the folder guide, not a spec. There is no file-count cap and
    no character cap. A file cap once dropped Section 21 13 19, and a
    character cap later cut 28-31-00 off before Sections 3.8 and 3.9.
    The model's context window still applies to the whole request. The
    client reports a request that is too large. It does not trim this text.
    """
    folder = content_root / "specs"
    notes = []
    if not folder.is_dir():
        return notes
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        notes.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
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
