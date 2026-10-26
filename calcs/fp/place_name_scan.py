"""Scan calcs/ for job, client, and place names.

The banned spellings are assembled at runtime so this file does not contain them.
"""

from __future__ import annotations

import re
from pathlib import Path

CALCS_ROOT = Path(__file__).resolve().parents[1]
_TEXT_SUFFIXES = {".py", ".md", ".json", ".txt"}


def banned_words() -> list[str]:
    parts = (
        ("Hyper", "ion"),
        ("Hou", "ston"),
        ("Den", "ver"),
        ("Phoe", "nix"),
        ("Nov", "va"),
        ("Micro", "soft"),
        ("Cal", "gary"),
        ("Que", "bec"),
        ("Onta", "rio"),
        ("Alber", "ta"),
        ("Ut", "ah"),
        ("Abra", "ham"),
        ("A", "XA"),
    )
    words = ["".join(part) for part in parts]
    words.append("A" + "be")
    words.append("Bo" + "rg")
    return words


def banned_pattern() -> re.Pattern[str]:
    return re.compile(r"\b(?:" + "|".join(banned_words()) + r")\b", re.IGNORECASE)


def place_name_hits(root: Path | None = None) -> list[str]:
    root = CALCS_ROOT if root is None else Path(root)
    banned = banned_pattern()
    found: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if banned.search(path.name):
            found.append(f"{rel} (filename)")
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if banned.search(line):
                found.append(f"{rel}:{number}")
    return found


def assert_no_place_names(root: Path | None = None) -> None:
    found = place_name_hits(root)
    if found:
        raise AssertionError("job, client, or place name under calcs/:\n" + "\n".join(found))
