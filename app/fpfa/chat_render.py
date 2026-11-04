"""Light markdown for the chat thread.

Claude replies in markdown. The thread is a tkinter Text widget, so a reply
is turned into (text, tags) runs here and ui.py inserts them. Headings,
bullets, numbered lists, fenced code, table rows, **bold**, and `code` are
handled. Single asterisks and underscores are left alone so names such as
t_total and zone_gal stay intact. Only the markers change. The words, the
figures, and the ASSUMED labels are inserted as written.

The first line of a job reply is its heading (Job <id> | project | kind |
title). It is kept word for word and tagged "meta" so it reads as a caption.
"""

from __future__ import annotations

import re

_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUMBERED = re.compile(r"^(\s*)(\d{1,3}[.)])\s+(.*)$")
_RULE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
_INLINE = re.compile(r"(\*\*[^*\n]+?\*\*|`[^`\n]+`)")
_JOB_HEADING = re.compile(r"^Job [0-9a-f]{6,} \| ")

Segment = tuple[str, tuple[str, ...]]


def is_job_heading(line: str) -> bool:
    return bool(_JOB_HEADING.match(line or ""))


def meta_caption(line: str) -> str:
    """Job heading as shown in the thread.

    A chat job's title is the question itself, which is already on screen
    just above, so the caption stops at the kind. The stored reply keeps the
    full heading.
    """
    parts = line.split(" | ", 3)
    if len(parts) == 4 and parts[2].strip() == "chat":
        return " | ".join(parts[:3])
    return line


def inline_segments(text: str, base: tuple[str, ...] = ()) -> list[Segment]:
    """Split one line on **bold** and `code`. Other characters pass through."""
    out: list[Segment] = []
    position = 0
    for match in _INLINE.finditer(text):
        if match.start() > position:
            out.append((text[position:match.start()], base))
        token = match.group(0)
        if token.startswith("**"):
            out.append((token[2:-2], base + ("bold",)))
        else:
            out.append((token[1:-1], base + ("code",)))
        position = match.end()
    if position < len(text):
        out.append((text[position:], base))
    return out


def _line_segments(line: str, *, first: bool) -> list[Segment] | None:
    """Segments for one line, or None when the line is dropped (a rule)."""
    if first and is_job_heading(line):
        return [(meta_caption(line), ("meta",))]
    if _RULE.match(line):
        return None
    heading = _HEADING.match(line)
    if heading:
        return inline_segments(heading.group(2), ("heading",))
    bullet = _BULLET.match(line)
    if bullet:
        level = "bullet2" if len(bullet.group(1).replace("\t", "    ")) >= 2 else "bullet"
        return [("• ", (level,))] + inline_segments(bullet.group(2), (level,))
    numbered = _NUMBERED.match(line)
    if numbered:
        level = "bullet2" if len(numbered.group(1).replace("\t", "    ")) >= 2 else "bullet"
        return [(numbered.group(2) + " ", (level,))] + inline_segments(numbered.group(3), (level,))
    return inline_segments(line)


_TABLE_RULE_CELL = re.compile(r"^:?-{2,}:?$")
# A cell boundary is a pipe that is not escaped. "A \| B" stays in one cell.
_CELL_BOUNDARY = re.compile(r"(?<!\\)\|")


def _table_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip().replace("\\|", "|") for cell in _CELL_BOUNDARY.split(body)]


def _strip_inline(text: str) -> str:
    return "".join(chunk for chunk, _tags in inline_segments(text))


def _table_lines(rows: list[str]) -> list[list[Segment]]:
    """Align a markdown table in the mono font. The header row is bold mono.

    A table with no |---| rule row is shown as written.
    """
    parsed = [_table_cells(row) for row in rows]
    rule_at = next(
        (index for index, cells in enumerate(parsed)
         if cells and all(_TABLE_RULE_CELL.match(cell) for cell in cells if cell)),
        None,
    )
    if rule_at is None or len(parsed) < 2:
        return [[(row, ("pre",))] for row in rows]
    body = [cells for index, cells in enumerate(parsed) if index != rule_at]
    count = max(len(cells) for cells in body)
    plain = [[_strip_inline(cell) for cell in cells] + [""] * (count - len(cells)) for cells in body]
    widths = [max(len(cells[column]) for cells in plain) for column in range(count)]
    out: list[list[Segment]] = []
    for index, cells in enumerate(plain):
        text = "  ".join(cell.ljust(widths[column]) for column, cell in enumerate(cells)).rstrip()
        tags = ("pre", "pre_head") if index == 0 and rule_at == 1 else ("pre",)
        out.append([(text, tags)])
        if index == 0 and rule_at == 1:
            out.append([("  ".join("─" * width for width in widths), ("pre", "rule"))])
    return out


def markdown_segments(text: str) -> list[Segment]:
    """Turn a reply into runs for a Text widget. Lines are joined with newlines.

    The newline after a code or table line carries the "pre" tag too, so the
    shaded block spans the text column instead of stopping at the last word.
    """
    lines = (text or "").split("\n")
    rendered: list[list[Segment]] = []
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith("```"):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence:
            rendered.append([(line, ("pre",))])
            index += 1
            continue
        if line.strip().startswith("|") and not (index == 0 and is_job_heading(line)):
            group = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                group.append(lines[index])
                index += 1
            rendered.extend(_table_lines(group))
            continue
        segments = _line_segments(line, first=index == 0)
        rendered.append([] if segments is None else segments)
        index += 1
    out: list[Segment] = []
    for position, segments in enumerate(rendered):
        if position:
            previous = rendered[position - 1]
            shaded = bool(previous) and all("pre" in tags for _chunk, tags in previous)
            out.append(("\n", ("pre",) if shaded else ()))
        out.extend(segment for segment in segments if segment[0])
    return out


def plain_text(text: str) -> str:
    """What the thread shows for a reply, without tags. Used by tests."""
    return "".join(chunk for chunk, _tags in markdown_segments(text))
