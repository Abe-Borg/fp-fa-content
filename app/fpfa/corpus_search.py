"""Read the content pack's reviewed notes: search them, and look one cite up in them.

Edition pins and decision notes live in corpus/. search_corpus is the tool
a model calls; it returns short hits so a turn can quote a pin instead of
assuming one. trace_cite is what the trace check calls: given a document,
an edition, and a section, it returns the pack's own sentences on that
section from corpus/ and specs/, so a claim is judged against the content
team's reviewed words and not against a note its own author wrote. Both
return paraphrases the content team reviewed. Neither opens a standard.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
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


# -- looking one cite up in the pack's notes -------------------------------------------------

# A section number as a note writes it: two or more dotted parts.
_SECTION = re.compile(r"\d+(?:\.\d+)+")
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_SENTENCE = re.compile(r"(?<=[.;])\s+")
_TRACE_DIRS = ("corpus", "specs")
_MAX_PASSAGES = 3
_PASSAGE = 700
# Any document a note might name, to tell when a paragraph has moved on to another one.
_ANY_DOC = re.compile(r"\b(?:NFPA\s*\d+[A-Z]?|(?:FM\s+)?DS\s*\d{1,2}-\d{1,3}|IBC|IFC|NBC|NFC|NEC|UL\s*\d+)\b")


def _doc_pattern(document: str) -> re.Pattern | None:
    """A pattern for a document's name as the pack's notes write it. None when there is nothing to match."""
    text = " ".join(str(document or "").split())
    if not text:
        return None
    nfpa = re.match(r"(?i)NFPA\s*(\d+[A-Z]?)\b", text)
    if nfpa:
        return re.compile(rf"\bNFPA\s*{re.escape(nfpa.group(1))}(?![\dA-Z])", re.IGNORECASE)
    fm = re.search(r"(?i)\b(\d{1,2}-\d{1,3}[A-Z]?)\b", text)
    if re.match(r"(?i)FM\b", text) and fm:
        return re.compile(rf"\b(?:FM\s+)?(?:DS|Data\s+Sheet)\s*{re.escape(fm.group(1))}\b", re.IGNORECASE)
    code = re.match(r"(?i)(IBC|IFC|NBC|NFC|NEC|UL)\b", text)
    if code:
        return re.compile(rf"\b{code.group(1)}\b", re.IGNORECASE)
    words = [re.escape(word) for word in text.split()[:4]]
    return re.compile(r"\b" + r"\s+".join(words) + r"\b", re.IGNORECASE)


def _section_pattern(section: str) -> re.Pattern | None:
    found = _SECTION.search(str(section or ""))
    if not found:
        return None
    number = found.group(0)
    # The section itself: not a longer number that starts with it, and not the tail of another.
    return re.compile(rf"(?<![\d.]){re.escape(number)}(?!\.?\d)")


@lru_cache(maxsize=8)
def _pack_lines(root: str, stamp: float) -> tuple:
    """Every prose line of the pack's reviewed notes: (relative path, line number, text)."""
    base = Path(root)
    lines = []
    for folder in _TRACE_DIRS:
        top = base / folder
        if not top.is_dir():
            continue
        for path in sorted(top.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = path.relative_to(base).as_posix()
            for number, line in enumerate(text.splitlines(), start=1):
                if line.strip():
                    lines.append((rel, number, line.strip()))
    return tuple(lines)


def _pack_stamp(root: Path) -> float:
    """Changes when a note under the traced folders changes, so the cache follows a pack update."""
    newest = 0.0
    for folder in _TRACE_DIRS:
        top = root / folder
        if not top.is_dir():
            continue
        for path in top.rglob("*.md"):
            try:
                newest = max(newest, path.stat().st_mtime)
            except OSError:
                continue
    return newest


def trace_cite(content_root: Path | str, document: str, edition: str = "", section: str = "") -> list[dict]:
    """The pack's own notes on one section of one document. Empty when the pack holds none.

    The match is one sentence of a note in corpus/ or specs/ that names the
    section and either names the document or follows a sentence of the same
    paragraph that does. With an edition, a sentence that names other years
    and not that one does not count: the pack holds the section for another
    edition. The passage returned is that sentence with the one before it
    and the one after it in the same paragraph, because the notes put a
    figure and its section in neighbouring sentences.
    Each passage is {"path", "line", "text", "sentence"}. These are the
    content team's reviewed paraphrases. They are not the standard.
    """
    doc = _doc_pattern(document)
    sec = _section_pattern(section)
    if doc is None or sec is None:
        return []
    root = Path(content_root).resolve()
    year = (_YEAR.search(str(edition or "")) or [None])[0] if edition else None
    if year is None:
        in_name = _YEAR.search(str(document or ""))
        year = in_name.group(0) if in_name else None
    found: list[dict] = []
    seen: set[str] = set()
    for rel, number, line in _pack_lines(str(root), _pack_stamp(root)):
        if not sec.search(line):
            continue
        named = False
        sentences = _SENTENCE.split(line)
        for index, sentence in enumerate(sentences):
            # A section number belongs to the document named last in its paragraph.
            if doc.search(sentence):
                named = True
            elif _ANY_DOC.search(sentence):
                named = False
            if not sec.search(sentence) or not named:
                continue
            years = set(_YEAR.findall(sentence))
            if year and years and year not in years:
                # The pack holds this section number for another edition.
                continue
            matched = " ".join(sentence.split())
            if matched in seen:
                continue
            seen.add(matched)
            around = sentences[max(0, index - 1): index + 2]
            text = " ".join(" ".join(around).split())
            found.append({"path": rel, "line": number, "text": text[:_PASSAGE], "sentence": matched[:_PASSAGE]})
            if len(found) >= _MAX_PASSAGES:
                return found
    return found
