"""Search corpus/**/*.md in a content pack.

Edition pins and decision notes live in that tree. The tool returns short
hits so a turn can quote a pin instead of assuming one.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_CAP = 40_000
_LINE = 200
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")


def search_corpus(content_root: Path, args: dict | None) -> dict:
    """Case-insensitive search. Up to `limit` hits (default 8), two lines each."""
    payload = dict(args or {})
    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")
    query = query.strip()
    limit = _limit(payload.get("limit"))
    root = Path(content_root) / "corpus"
    hits: list[dict] = []
    if not root.is_dir():
        return {"query": query, "hits": hits}
    needle = query.casefold()
    base = Path(content_root).resolve()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        text = _read_markdown(path)
        if text is None:
            continue
        hit = _hit(path, base, text, needle)
        if hit is None:
            continue
        trial = {"query": query, "hits": hits + [hit]}
        if len(json.dumps(trial)) > _CAP:
            break
        hits.append(hit)
        if len(hits) >= limit:
            break
    return {"query": query, "hits": hits}


def _limit(value) -> int:
    if value is None:
        return 8
    if isinstance(value, bool):
        raise ValueError("limit must be an integer")
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, str) and value.strip().isdigit():
        value = int(value.strip())
    if not isinstance(value, int):
        raise ValueError("limit must be an integer")
    if value < 1:
        raise ValueError("limit must be >= 1")
    return value


def _read_markdown(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _hit(path: Path, content_root: Path, text: str, needle: str) -> dict | None:
    try:
        rel = path.resolve().relative_to(content_root).as_posix()
    except ValueError:
        return None
    heading = ""
    matched: list[str] = []
    matched_heading = ""
    for line in text.splitlines():
        found = _HEADING.match(line.strip())
        if found:
            heading = found.group(1).strip()
        if needle not in line.casefold():
            continue
        if not matched:
            matched_heading = heading
        matched.append(_clip(line, needle))
        if len(matched) == 2:
            break
    if not matched:
        return None
    hit = {"path": rel, "lines": matched}
    if matched_heading:
        hit["heading"] = matched_heading
    return hit


def _clip(line: str, needle: str) -> str:
    text = line.strip()
    if len(text) <= _LINE:
        return text
    idx = text.casefold().find(needle)
    if idx < 0:
        return text[:_LINE]
    start = max(0, idx - 40)
    if start + _LINE > len(text):
        start = max(0, len(text) - _LINE)
    return text[start:start + _LINE]
