"""Read modes/<slug>/MODE.md from the content pack.

Same idea as roles/<slug>/ROLE.md. The application lists these files and
returns one file when the model calls read_mode. It does not copy the mode
text into Python.
"""

from __future__ import annotations

from pathlib import Path

from fpfa.skills_loader import frontmatter

DEFAULT_MODE = "mixed"
MODE_SLUGS = (
    "brainstorm",
    "calculator",
    "synthesis",
    "mixed",
)


def modes_dir(content_root: Path) -> Path:
    return content_root / "modes"


def normalize_mode(slug: str | None) -> str:
    text = (slug or "").strip().lower()
    return text or DEFAULT_MODE


def list_modes(content_root: Path) -> list[dict]:
    root = modes_dir(content_root)
    found = []
    if not root.is_dir():
        return found
    for path in sorted(root.iterdir()):
        mode = path / "MODE.md"
        if not mode.is_file():
            continue
        text = mode.read_text(encoding="utf-8")
        meta = frontmatter(text)
        found.append({
            "slug": path.name,
            "name": meta.get("name") or path.name,
            "description": meta.get("description") or "",
        })
    return found


def read_mode(content_root: Path, slug: str) -> str:
    slug = (slug or "").strip().strip("/").replace("\\", "/")
    if "/" in slug or slug in ("", ".", ".."):
        raise ValueError("mode slug must be a single folder name")
    slug = slug.lower()
    path = modes_dir(content_root) / slug / "MODE.md"
    if not path.is_file():
        known = ", ".join(item["slug"] for item in list_modes(content_root)) or "(none)"
        raise FileNotFoundError(f"No mode {slug!r}. Known modes: {known}")
    return path.read_text(encoding="utf-8")
