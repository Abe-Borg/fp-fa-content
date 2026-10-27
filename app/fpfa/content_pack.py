"""Build a content zip from the curated trees.

The pack copies skills, calcs, corpus, specs, modes, and roles. It does not
search those folders, and it does not read the API key or project files.
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
_FORBIDDEN = frozenset({
    "_sources",
    "foam",
    "foam-water",
    "foam_water",
    "clean-agent",
    "clean_agent",
    "cleanagent",
    "canada",
    "canadian",
    "catalog",
    "catalogs",
    "vendor-catalog",
    "__pycache__",
})
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


def forbidden_part(part: str) -> bool:
    """True for a path component the release zip must omit."""
    name = part.casefold()
    if name in _FORBIDDEN:
        return True
    stem = name.rsplit(".", 1)[0]
    return stem in _FORBIDDEN and stem != name


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

    A key file or an API-key string fails the build. Foam, clean-agent,
    Canada, catalog, and `_sources` paths are omitted and reported.
    """
    if not is_content_pack(source):
        raise ContentPackError("source is missing skills/ or calcs/fp/formulas.py")
    files: list[tuple[Path, str]] = []
    stripped: list[str] = []
    for top in ALLOWED_TOP:
        folder = source / top
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            rel = path.relative_to(source)
            rel_name = rel.as_posix()
            parts = rel.parts
            if path.is_symlink():
                stripped.append(rel_name)
                continue
            if not path.is_file():
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
    files.sort(key=lambda item: item[1])
    return files, stripped


def copy_pack(source: Path, dest: Path) -> list[str]:
    """Copy a seed tree. The destination must not already exist. No pack.json."""
    if dest.exists():
        raise ContentPackError("destination already exists")
    files, stripped = collect_pack_files(source)
    for path, rel in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
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
