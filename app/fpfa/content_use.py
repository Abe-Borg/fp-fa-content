"""Which content each agent actually read on a job, and whether its work carries any of it.

A skill is a method in the content pack. A specialist is told which skills
apply and may call read_skill for the body. Nothing forces the read, and a
read proves little: it shows the method was in front of the agent, not that
the agent followed it. So this module reports three things and keeps them
apart, for the Team panel, the Design Basis, and the evaluation:

1. Read. Which agent read which skill, in which order, and a hash of the
   exact text it was given (calc_tools logs one skill_read event per call).
2. Read before it wrote. Whether the read came before that agent's first
   finding. A method read after the conclusions were recorded did not shape
   them.
3. Carried. Whether a cite that agent then put on the record names a
   section the skill itself holds. That is a trace of the method's own pins
   reaching the work. It is the only link a program can see, and it is a
   weak one: a specialist can copy a section number without applying the
   method, and can apply a method that pins no section.

Whether the specialist used the method well is for a person to read. This
module never says so.
"""

from __future__ import annotations

import re
from pathlib import Path

_SECTION = re.compile(r"(?<![\w.])(\d{1,2}(?:\.\d{1,3}){1,6})(?![\w])")


def _sections(text: str) -> set[str]:
    return set(_SECTION.findall(text or ""))


def _skill_text(content_root: Path | None, slug: str) -> str:
    if content_root is None:
        return ""
    try:
        return (Path(content_root) / "skills" / slug / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return ""


def skill_use(snapshot: dict | None, content_root: Path | str | None = None) -> list[dict]:
    """One row per agent and skill it read, oldest first.

    Each row: agent, slug, reads, first_read (the time), sha256 (of the text
    it got), before_findings (the read came before the agent's first finding,
    or it wrote none), findings_after (its findings recorded after the read),
    carried (cites it recorded after the read whose section the skill holds),
    and changed (the skill in the pack now is not the text it read).
    """
    import hashlib

    snap = snapshot or {}
    root = Path(content_root) if content_root is not None else None
    findings = list(snap.get("findings") or []) + list(snap.get("retired_findings") or [])
    evidence = list(snap.get("evidence") or [])
    # The order rows were written in. The clock on a row is whole seconds; the event sequence is exact.
    seq = snap.get("row_seq") or {}
    rows: dict[tuple[str, str], dict] = {}
    for event in snap.get("skill_reads") or []:
        payload = event.get("payload") or {}
        agent, slug = str(event.get("agent") or ""), str(payload.get("slug") or "")
        if not slug:
            continue
        row = rows.get((agent, slug))
        if row is None:
            row = rows[(agent, slug)] = {"agent": agent, "slug": slug, "reads": 0,
                                        "first_read": str(event.get("ts") or ""), "seq": int(event.get("seq") or 0),
                                        "sha256": str(payload.get("sha256") or ""),
                                        "content_version": str(payload.get("content_version") or "")}
        row["reads"] += 1
    out = []
    for (agent, slug), row in rows.items():
        mine = [item for item in findings if (item.get("agent") or "") == agent]
        written = [int(seq.get(item["id"]) or 0) for item in mine]
        after = [number for number in written if number > row["seq"]]
        text = _skill_text(root, slug)
        held = _sections(text)
        carried = []
        for cite in evidence:
            if (cite.get("agent") or "") != agent or int(seq.get(cite["id"]) or 0) < row["seq"]:
                continue
            section = re.sub(r"^[§\s]+", "", str(cite.get("section") or ""))
            number = _SECTION.search(section)
            if number and number.group(1) in held:
                carried.append({"id": cite["id"], "document": cite.get("document") or "",
                                "edition": cite.get("edition") or "", "section": cite.get("section") or ""})
        now = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""
        out.append(dict(
            {key: value for key, value in row.items() if key != "seq"},
            before_findings=not written or row["seq"] < min(written),
            findings_after=len(after), carried=carried, changed=bool(now and row["sha256"] and now != row["sha256"]),
        ))
    out.sort(key=lambda item: item["first_read"])
    return out


def use_line(row: dict) -> str:
    """One row in words, for a document or a status line."""
    when = "before its findings" if row["before_findings"] else "AFTER it had already recorded findings"
    text = f"{row['agent'] or 'an agent'} read {row['slug']} {when}"
    if row["reads"] > 1:
        text += f" ({row['reads']} times)"
    if row["carried"]:
        cites = "; ".join(" ".join(part for part in (item["document"], item["edition"], item["section"]) if part)
                          for item in row["carried"][:4])
        text += f". Cites it then recorded that the skill holds: {cites}"
    elif row["findings_after"]:
        text += (f". It recorded {row['findings_after']} finding{'s' if row['findings_after'] != 1 else ''} "
                 "afterwards; none carries a cite the skill holds")
    else:
        text += ". It recorded no finding afterwards"
    if row["changed"]:
        text += ". The skill in the content pack has changed since"
    return text + "."


def unread(snapshot: dict | None, slugs_by_agent: dict[str, list[str]] | None = None) -> list[str]:
    """Agents that recorded findings on this job and read no skill at all."""
    snap = snapshot or {}
    readers = {str(event.get("agent") or "") for event in snap.get("skill_reads") or []}
    authors: dict[str, int] = {}
    for row in snap.get("findings") or []:
        authors[row.get("agent") or ""] = authors.get(row.get("agent") or "", 0) + 1
    return sorted(agent for agent in authors if agent and agent not in readers and agent not in ("lead", "evaluation-probe"))
