"""Blind claim check before a Section 21 13 19 export.

The procedure is skills/blind-claim-check/SKILL.md. This module does not copy
that method. The designer step writes the claim file and the cites file from
cites the zone tools returned. A citation in the draft that those tools did
not return is marked NOT PULLED.

The checker turn loads roles/qa-specialist/ROLE.md and receives only those two
files. It does not receive the draft, the spec section, or the designer's
notes, and it does not call the hosted runtime. Export waits until every
claim is Supported. A cite that was not retrieved stays open.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from fpfa.claude_client import MODEL_ID
from fpfa.paths import data_dir
from fpfa.roles_loader import read_role
from fpfa.spec_docx import DRAFT_SECTION

QA_ROLE = "qa-specialist"
BLIND_CLAIM_SKILL = "blind-claim-check"

VERDICT_SUPPORTED = "Supported"
VERDICT_NOT = "Not supported"
VERDICT_OPEN = "Source not found"
OPEN_MARK = "NOT PULLED"
_VERDICTS = (VERDICT_NOT, VERDICT_OPEN, VERDICT_SUPPORTED)

_TOOL_ORDER = (
    "zone_trapped_volume",
    "dry_delivery_screen",
    "di_trip_to_water",
    "hose_duration",
    "density_area",
    "nitrogen_gate",
    "elect_di_trim",
    "releasing_truth_table",
)

# A document token, or a section token that attaches to the document already
# seen in the same string. Section numbers stay the ones the tool returned.
_TOKEN = re.compile(
    r"(?P<doc>NFPA\s+\d{2,4}-\d{4}|IBC\s+\d{4}|IFC\s+\d{4}|FM\s+DS\s+\d+(?:-\d+)?)"
    r"|(?P<kind>Table|§|(?<![A-Za-z])s(?=\d)|Section)\s*(?P<section>\d+(?:\.\d+)+)",
    re.IGNORECASE,
)
_NUMBERED = re.compile(r"(?m)^(?P<n>\d+)\.\s+(?P<body>\S.*?)\s*$")
_VERDICT_LINE = re.compile(
    r"(?m)^\s*(?P<n>\d+)\.\s*(?P<word>Not supported|Source not found|Supported)\b"
)
_KEY_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")


def section_slug() -> str:
    """File token for the draft section. The section string itself stays DRAFT_SECTION."""
    return DRAFT_SECTION.replace(" ", "-")


def claims_filename() -> str:
    return f"{section_slug()}-claims.md"


def sources_filename() -> str:
    return f"{section_slug()}-sources.md"


def verdict_filename() -> str:
    return f"{section_slug()}-claimcheck.md"


def claim_dir(project_id: str) -> Path:
    path = data_dir() / "claim-checks" / project_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def checker_system(content_root: Path) -> str:
    """QA role file only. Spec notes, the draft, and designer notes stay out."""
    return read_role(content_root, QA_ROLE).strip()


def checker_request(claims: str, sources: str) -> str:
    """The only user text the checker receives: the two files."""
    return (
        f"{claims_filename()}\n{claims.strip()}\n\n"
        f"{sources_filename()}\n{sources.strip()}\n"
    )


def split_checker_request(text: str) -> tuple[str, str]:
    marker = f"\n\n{sources_filename()}\n"
    if not text.startswith(f"{claims_filename()}\n") or marker not in text:
        raise ValueError("checker request is not the claims file and the cites file")
    head, sources = text.split(marker, 1)
    claims = head.split(f"{claims_filename()}\n", 1)[1]
    return claims.strip("\n"), sources.strip("\n")


def numbered_bodies(text: str) -> dict[int, str]:
    found: dict[int, str] = {}
    for match in _NUMBERED.finditer(text or ""):
        found[int(match.group("n"))] = match.group("body").strip()
    return found


def source_is_open(text: str) -> bool:
    """A cite that was not retrieved stays open."""
    body = text or ""
    return OPEN_MARK in body or not body.strip()


def same_packet(stored: dict | None, packet: dict) -> bool:
    stored = stored or {}
    return (
        stored.get("claims") == packet.get("claims")
        and stored.get("sources") == packet.get("sources")
        and stored.get("draft_token") == packet.get("draft_token")
    )


def build_packet(result: dict) -> dict:
    """Designer step. Reads the zone result. The checker is not called here."""
    claims_rows = _claims_from_result(result or {})
    claim_lines = []
    source_lines = []
    for index, row in enumerate(claims_rows, start=1):
        claim_lines.append(
            f"{index}. {row['doc']} {row['section']} requires {row['requirement']}."
        )
        if row["open"]:
            source_lines.append(f"{index}. {OPEN_MARK}")
        else:
            source_lines.append(f"{index}. {row['doc']} {row['section']}. {row['cite']}")
    claims = "\n".join(claim_lines)
    sources = "\n".join(source_lines)
    return {
        "section": DRAFT_SECTION,
        "claims": claims,
        "sources": sources,
        "claim_count": len(claims_rows),
        "draft_token": _draft_token(result or {}, claims, sources),
    }


def judge(content_root: Path, packet: dict, create: Callable[..., Any]) -> dict:
    """QA checker. create() is Messages.create. Only the two files are sent."""
    if not packet.get("claim_count"):
        return _empty(packet)
    system = checker_system(content_root)
    user_text = checker_request(packet["claims"], packet["sources"])
    model_text = _ask(create, system, user_text)
    return _from_model(packet, model_text)


def unanswered(packet: dict) -> dict:
    """No checker ran. Nothing is Supported, so export stays blocked."""
    if not packet.get("claim_count"):
        return _empty(packet)
    reason = (
        f"Export of Section {DRAFT_SECTION} is blocked. "
        "The QA checker did not run. Save an API key in Settings."
    )
    outcome = _shell(packet, verdict="", rows=[], checker="absent")
    outcome["all_supported"] = False
    outcome["block_reason"] = reason
    outcome["thread"] = (
        f"Blind claim check for Section {DRAFT_SECTION}.\n"
        f"{reason}\n"
        f"{claims_filename()}\n"
        f"{(packet.get('claims') or '').strip()}"
    )
    return outcome


def write_packet_files(folder: Path, outcome: dict) -> None:
    """Write the claim file, the cites file, and the verdict file when it exists."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / claims_filename()).write_text(_with_newline(outcome.get("claims") or ""), encoding="utf-8")
    (folder / sources_filename()).write_text(_with_newline(outcome.get("sources") or ""), encoding="utf-8")
    if outcome.get("verdict"):
        (folder / verdict_filename()).write_text(_with_newline(outcome["verdict"]), encoding="utf-8")


def _empty(packet: dict) -> dict:
    reason = (
        f"Export of Section {DRAFT_SECTION} is blocked. The draft has no claim list."
    )
    outcome = _shell(packet, verdict="", rows=[], checker="absent")
    outcome["all_supported"] = False
    outcome["block_reason"] = reason
    outcome["thread"] = f"Blind claim check for Section {DRAFT_SECTION}.\n{reason}"
    return outcome


def _from_model(packet: dict, model_text: str) -> dict:
    words = _verdict_words(model_text)
    sources = numbered_bodies(packet["sources"])
    rows = []
    for number in sorted(numbered_bodies(packet["claims"])):
        source = sources.get(number, OPEN_MARK)
        if source_is_open(source):
            word = VERDICT_OPEN
        else:
            word = words.get(number, VERDICT_NOT)
            if word not in _VERDICTS:
                word = VERDICT_NOT
        rows.append({
            "n": number,
            "verdict": word,
            "cite": source.replace('"', "'"),
        })
    verdict = _render(rows)
    supported = bool(rows) and all(row["verdict"] == VERDICT_SUPPORTED for row in rows)
    outcome = _shell(packet, verdict=verdict, rows=rows, checker=MODEL_ID)
    outcome["all_supported"] = supported
    if supported:
        outcome["block_reason"] = ""
        outcome["thread"] = (
            f"Blind claim check for Section {DRAFT_SECTION}.\n"
            "Every claim is Supported.\n"
            f"{verdict_filename()}\n"
            f"{verdict.strip()}"
        )
    else:
        open_claims = ", ".join(str(row["n"]) for row in rows if row["verdict"] != VERDICT_SUPPORTED)
        reason = (
            f"Export of Section {DRAFT_SECTION} is blocked until every claim is Supported. "
            f"Open claims: {open_claims}."
        )
        outcome["block_reason"] = reason
        outcome["thread"] = (
            f"Blind claim check for Section {DRAFT_SECTION}.\n"
            f"{reason}\n"
            f"{verdict_filename()}\n"
            f"{verdict.strip()}"
        )
    return outcome


def _shell(packet: dict, *, verdict: str, rows: list[dict], checker: str) -> dict:
    return {
        "section": DRAFT_SECTION,
        "claims": packet.get("claims") or "",
        "sources": packet.get("sources") or "",
        "verdict": verdict,
        "rows": rows,
        "all_supported": False,
        "draft_token": packet.get("draft_token") or "",
        "claim_count": packet.get("claim_count") or 0,
        "checker": checker,
        "block_reason": "",
        "thread": "",
    }


def _render(rows: list[dict]) -> str:
    lines = [
        f'{row["n"]}. {row["verdict"]}. Cite: "{row["cite"]}"'
        for row in rows
    ]
    return "\n".join(lines)


def _verdict_words(text: str) -> dict[int, str]:
    found: dict[int, str] = {}
    for match in _VERDICT_LINE.finditer(text or ""):
        found[int(match.group("n"))] = match.group("word")
    return found


def _ask(create: Callable[..., Any], system: str, user_text: str) -> str:
    """One Messages call. No tools, so the checker cannot fetch the draft."""
    response = create(
        model=MODEL_ID,
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": user_text}],
    )
    return _scrub(_response_text(response))


def _response_text(response: Any) -> str:
    chunks = []
    for block in getattr(response, "content", []) or []:
        if isinstance(block, dict):
            if block.get("type") == "text" and block.get("text"):
                chunks.append(str(block["text"]))
            continue
        if getattr(block, "type", None) == "text" and getattr(block, "text", None):
            chunks.append(str(block.text))
    return "\n".join(chunks).strip()


def _scrub(text: str) -> str:
    return _KEY_RE.sub("[key]", text or "")


def _with_newline(text: str) -> str:
    if text and not text.endswith("\n"):
        return text + "\n"
    return text


def _draft_token(result: dict, claims: str, sources: str) -> str:
    basis = result.get("basis") if isinstance(result.get("basis"), dict) else {}
    payload = json.dumps(
        {
            "narrative": result.get("narrative") or "",
            "flags": result.get("flags") or [],
            "hazard_notes": (basis or {}).get("hazard_notes") or "",
            "claims": claims,
            "sources": sources,
        },
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _claims_from_result(result: dict) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    tools = result.get("tools") if isinstance(result.get("tools"), dict) else {}
    for text in _tool_strings(tools):
        pairs = _pairs(text)
        if not pairs:
            continue
        cite = _short_cite(text)
        for doc, section in pairs:
            key = (doc, section)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "doc": doc,
                "section": section,
                "cite": cite,
                "requirement": cite.rstrip("."),
                "open": False,
            })
    for sentence in _sentences(_draft_prose(result)):
        pairs = _pairs(sentence)
        if not pairs:
            continue
        requirement = _short_cite(sentence).rstrip(".")
        requirement = re.sub(r"(?i)^requires\s+", "", requirement).strip() or _short_cite(sentence)
        for doc, section in pairs:
            key = (doc, section)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "doc": doc,
                "section": section,
                "cite": OPEN_MARK,
                "requirement": requirement.rstrip("."),
                "open": True,
            })
    return rows


def _tool_strings(tools: dict) -> list[str]:
    names = [name for name in _TOOL_ORDER if name in tools]
    names.extend(name for name in tools if name not in names)
    found: list[str] = []
    for name in names:
        _collect_strings(tools.get(name), found)
    return found


def _collect_strings(value: Any, found: list[str]) -> None:
    if isinstance(value, str):
        if value.strip():
            found.append(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, found)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _collect_strings(item, found)


def _draft_prose(result: dict) -> str:
    parts = [str(result.get("narrative") or "")]
    for flag in result.get("flags") or []:
        parts.append(str(flag))
    basis = result.get("basis") if isinstance(result.get("basis"), dict) else {}
    notes = (basis or {}).get("hazard_notes") or ""
    if str(notes).strip():
        parts.append(str(notes))
    return "\n".join(parts)


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"\n+|(?<=[.!?])\s+", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _pairs(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    last_doc = ""
    for match in _TOKEN.finditer(text or ""):
        if match.group("doc"):
            last_doc = _norm_doc(match.group("doc"))
            continue
        section = match.group("section")
        if not last_doc or not section:
            continue
        found.append((last_doc, _section_label(match.group("kind") or "", section)))
    return found


def _norm_doc(raw: str) -> str:
    parts = raw.split()
    head = parts[0].upper()
    if head == "NFPA" and len(parts) >= 2:
        return f"NFPA {parts[1]}"
    if head in {"IBC", "IFC"} and len(parts) >= 2:
        return f"{head} {parts[1]}"
    if head == "FM":
        rest = ["DS" if part.upper() == "DS" else part for part in parts[1:]]
        return "FM " + " ".join(rest)
    return " ".join(parts)


def _section_label(kind: str, number: str) -> str:
    if kind.lower() == "table":
        return f"Table {number}"
    return f"§{number}"


def _short_cite(text: str) -> str:
    """One short cite from a retrieved line. Not a judgment of the claim."""
    collapsed = " ".join((text or "").split())
    match = re.search(r"\(([^)]+)\)", collapsed)
    body = match.group(1) if match else collapsed
    stripped = " ".join(_TOKEN.sub(" ", body).split()).strip(" ;,./")
    if len(stripped) >= 8:
        return stripped
    return collapsed
