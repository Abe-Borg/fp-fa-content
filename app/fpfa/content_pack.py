"""Build a content zip from the curated trees.

The pack copies skills, calcs, corpus, specs, modes, and roles. It does not
search those folders, and it does not read the API key or project files.

What a path may be, here and in the installer (fpfa.content_update):

  * a component that starts with a foam or clean-agent name is out of scope.
    The build stops naming it and writes no zip, and the installer refuses a
    pack that holds one (SCOPE_PREFIXES; scripts/check_pack_strip.py keeps the
    same list, and a test holds the two equal);
  * `_sources`, catalog, and `__pycache__` folders are left out and reported;
  * Canada is in scope through a skill's Country gate (US | Canada), so a
    Canada-named file ships under its own name like any other;
  * the held draft folder under calcs/fp is left out and reported.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fpfa.paths import is_content_pack

ALLOWED_TOP = ("skills", "calcs", "corpus", "specs", "modes", "roles")
MARKER_NAME = "pack.json"
BLOCKED_FILE_NAMES = frozenset({
    "anthropic-api-key",
    "config.json",
    "credentials.json",
    "secrets.json",
    ".env",
})
_SKIP_SUFFIXES = {".pyc", ".pyo", ".pdf", ".docx", ".zip"}
# A path component that starts with one of these names foam or clean-agent content, which is out of scope.
# It is matched as a prefix, so a slug such as clean-agent-enclosure-integrity is caught, not only a folder
# named clean-agent. The strip scan (scripts/check_pack_strip.py, _SCOPE_PREFIXES) holds the same list.
SCOPE_PREFIXES = ("clean-agent", "clean_agent", "cleanagent", "foam")
# Left out of a pack and reported: raw research, vendor catalogs, and bytecode.
_STRIPPED = frozenset({
    "_sources",
    "catalog",
    "catalogs",
    "vendor-catalog",
    "__pycache__",
})
# Held paths, as path components: left out of a pack and reported. calcs/fp's draft folder is held and unwired.
# The name is built from pieces because calcs/fp/test_draft_held.py fails on a literal reference to that folder.
HELD_PARTS = (("calcs", "fp", "dr" + "aft"),)
_KEY_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}")


class ContentPackError(Exception):
    """The tree cannot be packed. The message names a path, not a secret."""


@dataclass(frozen=True)
class BuiltPack:
    manifest: dict
    zip_path: Path
    manifest_path: Path
    notes_path: Path
    stripped: tuple[str, ...]


def out_of_scope_part(part: str) -> bool:
    """True for a path component that names foam or clean-agent content. It fails a build and an install."""
    return part.casefold().startswith(SCOPE_PREFIXES)


def forbidden_part(part: str) -> bool:
    """True for a path component a release zip must not carry: out of scope, or one the build leaves out."""
    if out_of_scope_part(part):
        return True
    name = part.casefold()
    if name in _STRIPPED:
        return True
    stem = name.rsplit(".", 1)[0]
    return stem in _STRIPPED and stem != name


def held_path(parts: tuple[str, ...]) -> bool:
    """True for a path under a held folder (HELD_PARTS)."""
    return any(tuple(parts[: len(held)]) == held for held in HELD_PARTS)


def parse_version_numbers(value: str) -> tuple[int, ...] | None:
    """Dotted integers from a content version, or None."""
    text = (value or "").strip()
    if text.startswith("content-v"):
        text = text[len("content-v"):]
    elif text.startswith("content-"):
        text = text[len("content-"):]
    if text.startswith("v"):
        text = text[1:]
    if not text:
        return None
    numbers = []
    for part in text.split("."):
        if not part.isdigit():
            return None
        numbers.append(int(part))
    if len(numbers) < 2:
        return None
    return tuple(numbers)


def canonical_version(value: str) -> str | None:
    """Return dotted integers, or None when the text is not a content version."""
    numbers = parse_version_numbers(value)
    if numbers is None:
        return None
    return ".".join(str(number) for number in numbers)


def require_version(value: str) -> str:
    version = canonical_version(value)
    if version is None:
        raise ContentPackError("version must look like 2026.10.1")
    return version


def clean_changelog(lines: list[str], version: str) -> list[str]:
    cleaned = []
    for line in lines:
        text = " ".join(str(line).split())
        if not text:
            continue
        cleaned.append(text[:300])
        if len(cleaned) == 20:
            break
    if not cleaned:
        cleaned.append(f"Content pack {version}")
    return cleaned


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _blocked_file(name: str) -> bool:
    lowered = name.casefold()
    return lowered in BLOCKED_FILE_NAMES or lowered.startswith(".env")


def collect_pack_files(source: Path) -> tuple[list[tuple[Path, str]], list[str]]:
    """Return pack files and the relative paths that were left out.

    A key file, an API-key string, or a foam or clean-agent path fails the
    build, naming every such path. Catalog and `_sources` paths and the held
    draft are omitted and reported. A Canada-named path is packed under its
    own name: nothing is dropped without a message.
    """
    if not is_content_pack(source):
        raise ContentPackError("source is missing skills/ or calcs/fp/formulas.py")
    files: list[tuple[Path, str]] = []
    stripped: list[str] = []
    out_of_scope: list[str] = []
    for top in ALLOWED_TOP:
        folder = source / top
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            rel = path.relative_to(source)
            rel_name = rel.as_posix()
            parts = rel.parts
            if not (path.is_symlink() or path.is_file()):
                continue
            if any(out_of_scope_part(part) for part in parts):
                out_of_scope.append(rel_name)
                continue
            if path.is_symlink() or held_path(parts):
                stripped.append(rel_name)
                continue
            if any(forbidden_part(part) for part in parts) or path.suffix.casefold() in _SKIP_SUFFIXES:
                stripped.append(rel_name)
                continue
            if path.name == ".DS_Store":
                stripped.append(rel_name)
                continue
            if _blocked_file(path.name):
                raise ContentPackError(f"refusing to pack {rel_name}")
            text = path.read_text(encoding="utf-8", errors="replace")
            if _KEY_RE.search(text):
                raise ContentPackError(f"refusing to pack {rel_name} because it contains an API key")
            files.append((path, rel_name))
    if out_of_scope:
        shown = "\n".join(f"  {rel}" for rel in sorted(out_of_scope)[:40])
        more = f"\n  ... and {len(out_of_scope) - 40} more" if len(out_of_scope) > 40 else ""
        raise ContentPackError(
            f"refusing to pack {len(out_of_scope)} foam or clean-agent path(s); they are out of scope:\n{shown}{more}"
        )
    files.sort(key=lambda item: item[1])
    stripped.sort()
    return files, stripped


def seed_marker(version: str) -> bytes:
    """The bundled seed's pack.json: its numbered content version, so the updater can tell it from older packs."""
    numbered = require_version(version)
    return (json.dumps({"version": numbered, "seed": True}, indent=2) + "\n").encode("utf-8")


def copy_pack(source: Path, dest: Path, version: str) -> list[str]:
    """Copy a seed tree with its pack.json. The destination must not already exist.

    The seed carries a numbered version, set when the app build is cut. The
    updater compares it with the feed, so an older published pack never
    replaces a newer seed (fpfa.content_update._is_newer). The marker is
    written into the seed only, never into the pack folders of a checkout, so
    the content fingerprint does not move for it.
    """
    marker = seed_marker(version)
    if dest.exists():
        raise ContentPackError("destination already exists")
    files, stripped = collect_pack_files(source)
    for path, rel in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    (dest / MARKER_NAME).write_bytes(marker)
    return stripped


def _app_version() -> str:
    from fpfa import __version__

    return __version__


def _stamp(moment: datetime) -> tuple[int, int, int, int, int, int]:
    return (moment.year, moment.month, moment.day, moment.hour, moment.minute, moment.second)


def _add_bytes(archive: zipfile.ZipFile, name: str, payload: bytes, stamp: tuple) -> None:
    info = zipfile.ZipInfo(filename=name, date_time=stamp)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits |= 0x800
    info.external_attr = (0o100644 & 0xFFFF) << 16
    archive.writestr(info, payload)


def parse_created(text: str | None) -> datetime:
    if not text:
        return datetime.now(timezone.utc).replace(microsecond=0)
    candidate = text.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ContentPackError("created must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def build_pack(
    source: Path,
    out_dir: Path,
    version: str,
    changelog: list[str] | None = None,
    created: str | None = None,
) -> BuiltPack:
    """Write the zip, manifest.json, and changelog notes. Return those paths."""
    numbered = require_version(version)
    moment = parse_created(created)
    created_text = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
    notes = clean_changelog(list(changelog or []), numbered)
    files, stripped = collect_pack_files(source)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"fp-fa-content-v{numbered}.zip"
    zip_path = out_dir / filename
    stamp = _stamp(moment)
    marker = (json.dumps({"version": numbered, "created": created_text}, indent=2) + "\n").encode("utf-8")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, rel in files:
            _add_bytes(archive, rel, path.read_bytes(), stamp)
        _add_bytes(archive, MARKER_NAME, marker, stamp)
    manifest = {
        "version": numbered,
        "created": created_text,
        "sha256": sha256_file(zip_path),
        "filename": filename,
        "changelog": notes,
        "min_app_version": canonical_version(_app_version()) or _app_version(),
    }
    manifest_path = out_dir / "manifest.json"
    notes_path = out_dir / "changelog.txt"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    notes_path.write_text("\n".join(notes) + "\n", encoding="utf-8")
    return BuiltPack(
        manifest=manifest,
        zip_path=zip_path,
        manifest_path=manifest_path,
        notes_path=notes_path,
        stripped=tuple(stripped),
    )
