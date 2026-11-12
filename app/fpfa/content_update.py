"""Download a content pack, verify sha256, and switch the saved content folder.

The pointer in Settings moves only after the new tree is complete. A failed
check leaves the last good pack, and the bundled seed remains the fallback
when that folder is missing. The API key and project files stay in the data
directory. This module does not search the pack.
"""

from __future__ import annotations

import hmac
import json
import os
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fpfa.content_pack import (
    ALLOWED_TOP,
    BLOCKED_FILE_NAMES,
    MARKER_NAME,
    canonical_version,
    forbidden_part,
    out_of_scope_part,
    parse_version_numbers,
    sha256_file,
)
from fpfa.paths import content_root, data_dir, is_content_pack, read_config, write_config

# Stable asset on the latest GitHub Release. Join the zip name to this URL
# before following redirects so a CDN host does not become the pack address.
DEFAULT_FEED_URL = (
    "https://github.com/Abe-Borg/fp-fa-content/releases/latest/download/manifest.json"
)
MAX_MANIFEST_BYTES = 1_000_000
MAX_PACK_BYTES = 80 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 200 * 1024 * 1024
MAX_MEMBERS = 5000


class ContentUpdateError(Exception):
    def __init__(self, message: str, status: str = "error"):
        super().__init__(message)
        self.status = status


@dataclass
class UpdateResult:
    status: str
    message: str
    version: str = ""
    changelog: list[str] | None = None
    root: str = ""


def request_headers() -> dict[str, str]:
    """Headers for the feed. The Anthropic key is never attached."""
    return {
        "User-Agent": "fpfa-content-update",
        "Accept": "application/octet-stream, application/json;q=0.9, */*;q=0.8",
    }


class _HttpOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme not in {"http", "https"}:
            raise ContentUpdateError(
                "The content feed redirected away from http. The last good pack is still in use.",
                status="rejected",
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def resolved_feed_url(explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    env = os.environ.get("FPFA_CONTENT_FEED_URL", "").strip()
    if env:
        return env
    saved = str(read_config().get("content_feed_url") or "").strip()
    if saved:
        return saved
    return DEFAULT_FEED_URL


def remember_feed_url(url: str) -> str:
    """Store the feed a designer just checked, including the default."""
    cleaned = url.strip() or DEFAULT_FEED_URL
    _require_http(cleaned)
    write_config({"content_feed_url": cleaned})
    return cleaned


def updates_on_launch() -> bool:
    """Packaged apps check on launch. A source checkout checks after a feed is saved.

    FPFA_CONTENT_UPDATES=0 skips the check. A folder the designer picked by
    hand (version "custom") stays put until they press Check for content updates.
    """
    flag = os.environ.get("FPFA_CONTENT_UPDATES", "").strip().lower()
    if flag in {"0", "off", "false", "no"}:
        return False
    if flag in {"1", "on", "true", "yes"}:
        return True
    if content_version_text() == "custom":
        return False
    if os.environ.get("FPFA_CONTENT_FEED_URL", "").strip():
        return True
    if str(read_config().get("content_feed_url") or "").strip():
        return True
    return bool(getattr(sys, "frozen", False))


def current_changelog() -> list[str]:
    raw = read_config().get("content_changelog")
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if isinstance(item, str) and str(item).strip()]


def content_version_text() -> str:
    """Version label for Settings. Seed checkouts stay unlabeled until an install."""
    try:
        root = content_root()
    except FileNotFoundError:
        return "unavailable"
    cfg = read_config()
    saved_root = str(cfg.get("content_root") or "").strip()
    saved_version = str(cfg.get("content_version") or "").strip()
    saved_matches = False
    if saved_root:
        try:
            saved_matches = Path(saved_root).resolve() == root.resolve()
        except OSError:
            saved_matches = False
    if saved_matches and saved_version == "custom":
        return "custom"
    numbered = canonical_version(saved_version) if saved_matches else None
    if numbered:
        return numbered
    marker = _marker_version(root)
    if marker:
        return marker
    if _is_seed(root):
        return "bundled seed" if getattr(sys, "frozen", False) else "source checkout"
    if saved_version:
        return saved_version
    return "unversioned"


def content_status_line() -> str:
    return f"Content {content_version_text()}"


def format_changelog(lines: list[str] | None) -> str:
    if not lines:
        return "No content-pack changelog yet."
    return "\n".join(f"• {line}" for line in lines)


def update_banner(version: str, lines: list[str]) -> str:
    extra = " ".join(lines[:6]).strip()
    if len(extra) > 420:
        extra = extra[:417] + "..."
    lead = f"Content pack {version} is installed."
    return f"{lead} {extra}".strip() if extra else lead


def remember_selected_root(folder: str) -> None:
    """Save a folder the designer picked. A pack.json version is kept."""
    path = Path(folder).expanduser()
    resolved = path.resolve()
    marker = _marker_version(resolved)
    numbered = canonical_version(marker) if marker else None
    updates: dict = {"content_root": str(resolved)}
    if numbered:
        updates["content_version"] = numbered
        if numbered != str(read_config().get("content_version") or ""):
            updates["content_changelog"] = []
    else:
        updates["content_version"] = "custom"
        updates["content_changelog"] = []
    write_config(updates)


def resolve_pack_url(manifest: dict, requested_manifest_url: str) -> str:
    """Zip URL joined to the feed URL that was requested, not a redirect target."""
    raw = str(manifest.get("url") or "").strip()
    if raw:
        joined = urllib.parse.urljoin(requested_manifest_url, raw)
    else:
        filename = str(manifest.get("filename") or "").strip()
        if not filename:
            raise ContentUpdateError(
                "The manifest has no pack address. The last good pack is still in use.",
                status="rejected",
            )
        joined = urllib.parse.urljoin(requested_manifest_url, filename)
    _require_http(joined)
    return joined


def check_for_content_update(url: str | None = None, *, apply: bool = True) -> UpdateResult:
    """Fetch the feed and maybe install. Network and pack errors return a result."""
    try:
        return _check(url, apply=apply)
    except Exception as exc:
        status = _failure_status(exc)
        return UpdateResult(
            status=status,
            message=_failure_message(exc, status),
            version=content_version_text(),
            changelog=None,
        )


def _check(url: str | None, *, apply: bool) -> UpdateResult:
    requested = resolved_feed_url(url)
    _require_http(requested)
    opener = urllib.request.build_opener(_HttpOnlyRedirect())
    manifest, manifest_url = _load_manifest(requested, opener)
    local = content_version_text()
    remote = manifest["version"]
    newer = _is_newer(remote, local)
    if not newer:
        if canonical_version(local) == remote:
            write_config({"content_changelog": manifest["changelog"]})
            message = f"Content pack {remote} is already installed."
        else:
            message = (
                f"Content pack {local} is newer than the feed ({remote}). "
                "The installed pack was left in place."
            )
        return UpdateResult(
            status="current",
            message=message,
            version=content_version_text(),
            changelog=list(manifest["changelog"]),
        )
    if os.environ.get("FPFA_CONTENT_ROOT", "").strip():
        return UpdateResult(
            status="pinned",
            message=(
                f"Content pack {remote} is published. "
                "FPFA_CONTENT_ROOT is set, so the content folder was left as it is."
            ),
            version=local,
            changelog=list(manifest["changelog"]),
        )
    _enforce_min_app(manifest)
    if not apply:
        return UpdateResult(
            status="available",
            message=f"Content pack {remote} is available.",
            version=remote,
            changelog=list(manifest["changelog"]),
        )
    pack_url = resolve_pack_url(manifest, manifest_url)
    final = _download_and_install(pack_url, manifest, opener)
    return UpdateResult(
        status="updated",
        message=f"Content pack {remote} is installed.",
        version=remote,
        changelog=list(manifest["changelog"]),
        root=str(final),
    )


def _load_manifest(requested_url: str, opener) -> tuple[dict, str]:
    document = _get_json(requested_url, opener)
    hop = _manifest_hop(document)
    if hop is None:
        return _parse_manifest(document), requested_url
    _require_http(hop)
    hopped = _get_json(hop, opener)
    if _manifest_hop(hopped) is not None:
        raise ContentUpdateError(
            "The release feed did not return a content manifest. The last good pack is still in use.",
            status="rejected",
        )
    return _parse_manifest(hopped), hop


def _manifest_hop(document: dict) -> str | None:
    """GitHub release JSON points at a manifest asset. Our manifest does not."""
    if "sha256" in document and "version" in document:
        return None
    assets = document.get("assets")
    if not isinstance(assets, list):
        raise ContentUpdateError(
            "The feed is not a content manifest. The last good pack is still in use.",
            status="rejected",
        )
    for asset in assets:
        if not isinstance(asset, dict) or asset.get("name") != "manifest.json":
            continue
        download = asset.get("browser_download_url") or asset.get("url")
        if isinstance(download, str) and download.strip():
            return download.strip()
    raise ContentUpdateError(
        "The release has no manifest.json asset. The last good pack is still in use.",
        status="rejected",
    )


def _parse_manifest(document: dict) -> dict:
    if not isinstance(document, dict):
        raise ContentUpdateError(
            "The feed is not a content manifest. The last good pack is still in use.",
            status="rejected",
        )
    version = canonical_version(str(document.get("version") or ""))
    if version is None:
        raise ContentUpdateError(
            "The manifest version is not a numbered content version. The last good pack is still in use.",
            status="rejected",
        )
    digest = str(document.get("sha256") or "").strip().lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ContentUpdateError(
            "The manifest sha256 is not 64 hex characters. The last good pack is still in use.",
            status="rejected",
        )
    filename = document.get("filename") or ""
    url = document.get("url") or ""
    if not isinstance(filename, str) or not isinstance(url, str):
        raise ContentUpdateError(
            "The manifest pack address is not text. The last good pack is still in use.",
            status="rejected",
        )
    filename = filename.strip()
    url = url.strip()
    if filename:
        if not _zip_name_ok(filename):
            raise ContentUpdateError(
                "The manifest filename must be a zip name. The last good pack is still in use.",
                status="rejected",
            )
    elif not url:
        raise ContentUpdateError(
            "The manifest needs a filename or a pack url. The last good pack is still in use.",
            status="rejected",
        )
    created = document.get("created", "")
    if created is None:
        created = ""
    if not isinstance(created, str) or len(created) > 40:
        raise ContentUpdateError(
            "The manifest created value must be a short timestamp. The last good pack is still in use.",
            status="rejected",
        )
    notes = _coerce_changelog(document.get("changelog"))
    minimum = document.get("min_app_version") or ""
    if minimum is None:
        minimum = ""
    if not isinstance(minimum, str) or (minimum and canonical_version(minimum) is None):
        raise ContentUpdateError(
            "min_app_version is not a numbered version. The last good pack is still in use.",
            status="rejected",
        )
    return {
        "version": version,
        "created": created,
        "sha256": digest,
        "filename": filename,
        "url": url,
        "changelog": notes,
        "min_app_version": canonical_version(minimum) if minimum else "",
    }


def _coerce_changelog(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        raw_lines = value.splitlines()
    elif isinstance(value, list):
        raw_lines = []
        for item in value:
            if not isinstance(item, str):
                raise ContentUpdateError(
                    "Changelog entries must be text. The last good pack is still in use.",
                    status="rejected",
                )
            raw_lines.append(item)
    else:
        raise ContentUpdateError(
            "The changelog must be a list of text lines. The last good pack is still in use.",
            status="rejected",
        )
    notes = []
    for line in raw_lines:
        text = " ".join(line.split())
        if text:
            notes.append(text[:300])
        if len(notes) == 20:
            break
    return notes


def _enforce_min_app(manifest: dict) -> None:
    need = manifest.get("min_app_version") or ""
    if not need:
        return
    from fpfa import __version__

    have = canonical_version(__version__)
    need_numbers = parse_version_numbers(need)
    have_numbers = parse_version_numbers(have or "")
    if have_numbers is not None and need_numbers is not None and need_numbers > have_numbers:
        raise ContentUpdateError(
            f"This pack needs app {need}. This app is {__version__}. The last good pack is still in use.",
            status="needs_app",
        )


def _download_and_install(pack_url: str, manifest: dict, opener) -> Path:
    parent = data_dir() / "content-packs"
    parent.mkdir(parents=True, exist_ok=True)
    _sweep_leftovers(parent)
    work = Path(tempfile.mkdtemp(prefix=".incoming-", dir=parent))
    try:
        zip_path = work / "pack.zip"
        _download_file(pack_url, zip_path, opener)
        actual = sha256_file(zip_path)
        if not hmac.compare_digest(actual, manifest["sha256"]):
            raise ContentUpdateError(
                "The downloaded pack did not match the published sha256. The last good pack is still in use.",
                status="rejected",
            )
        extract = work / "extract"
        extract.mkdir()
        _safe_extract(zip_path, extract)
        staged = _locate_pack_root(extract)
        if not is_content_pack(staged):
            raise ContentUpdateError(
                "The pack is missing skills/ or calcs/fp/formulas.py. The last good pack is still in use.",
                status="rejected",
            )
        return _install_root(staged, manifest)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _install_root(staged_root: Path, manifest: dict) -> Path:
    """Move the finished tree into place, then save the pointer.

    The saved folder is the atomic step: readers keep the previous path until
    settings name the new directory. Same-version replacement restores the
    previous directory when the move or the settings write fails.
    """
    parent = data_dir() / "content-packs"
    parent.mkdir(parents=True, exist_ok=True)
    version = manifest["version"]
    final = parent / version
    backup = parent / f".backup-{version}"
    replaced = False
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)
    try:
        if final.exists():
            os.rename(final, backup)
            replaced = True
        try:
            os.rename(staged_root, final)
        except OSError:
            shutil.move(str(staged_root), str(final))
    except OSError as exc:
        if replaced and backup.exists() and not final.exists():
            os.rename(backup, final)
        raise ContentUpdateError(
            "The new pack could not be moved into place. The last good pack is still in use.",
            status="error",
        ) from exc
    try:
        write_config({
            "content_root": str(final.resolve()),
            "content_version": version,
            "content_sha256": manifest["sha256"],
            "content_changelog": manifest["changelog"],
            "content_updated": manifest.get("created") or "",
        })
    except OSError as exc:
        if final.exists():
            shutil.rmtree(final, ignore_errors=True)
        if replaced and backup.exists():
            os.rename(backup, final)
        raise ContentUpdateError(
            "The new pack could not be saved in settings. The last good pack is still in use.",
            status="error",
        ) from exc
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)
    _prune_old_packs(parent, final)
    return final.resolve()


def _prune_old_packs(parent: Path, current: Path) -> None:
    """Keep the installed pack and one previous pack."""
    try:
        others = [
            path for path in parent.iterdir()
            if path.is_dir() and not path.name.startswith(".") and path.resolve() != current.resolve()
        ]
    except OSError:
        return
    def sort_key(path: Path):
        numbers = parse_version_numbers(path.name)
        return numbers if numbers is not None else (0,)

    others.sort(key=sort_key, reverse=True)
    for stale in others[1:]:
        shutil.rmtree(stale, ignore_errors=True)


def _sweep_leftovers(parent: Path) -> None:
    try:
        names = list(parent.iterdir())
    except OSError:
        return
    for path in names:
        if path.name.startswith(".incoming-") or path.name.startswith(".backup-"):
            shutil.rmtree(path, ignore_errors=True)


def _locate_pack_root(extract_dir: Path) -> Path:
    if is_content_pack(extract_dir):
        return extract_dir
    children = [path for path in extract_dir.iterdir() if path.is_dir() and not path.name.startswith(".")]
    if len(children) == 1 and is_content_pack(children[0]):
        return children[0]
    raise ContentUpdateError(
        "The pack is missing skills/ or calcs/fp/formulas.py. The last good pack is still in use.",
        status="rejected",
    )


def _safe_extract(zip_path: Path, dest: Path) -> None:
    try:
        archive = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as exc:
        raise ContentUpdateError(
            "The download was not a zip. The last good pack is still in use.",
            status="rejected",
        ) from exc
    root = dest.resolve()
    written = 0
    members = 0
    with archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            members += 1
            if members > MAX_MEMBERS or info.file_size > MAX_UNCOMPRESSED_BYTES:
                raise ContentUpdateError(
                    "The pack is larger than this app will install. The last good pack is still in use.",
                    status="rejected",
                )
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ContentUpdateError(
                    "The pack contains a symlink. The last good pack is still in use.",
                    status="rejected",
                )
            parts = _safe_parts(info.filename)
            _check_member(parts)
            target = dest.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                raise ContentUpdateError(
                    "The pack contains an unsafe path. The last good pack is still in use.",
                    status="rejected",
                )
            resolved = target.resolve()
            if resolved != root and root not in resolved.parents:
                raise ContentUpdateError(
                    "The pack contains an unsafe path. The last good pack is still in use.",
                    status="rejected",
                )
            with archive.open(info, "r") as src, target.open("wb") as out:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > MAX_UNCOMPRESSED_BYTES:
                        raise ContentUpdateError(
                            "The pack is larger than this app will install. The last good pack is still in use.",
                            status="rejected",
                        )
                    out.write(chunk)


def _safe_parts(name: str) -> tuple[str, ...]:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ContentUpdateError(
            "The pack contains an unsafe path. The last good pack is still in use.",
            status="rejected",
        )
    pure = Path(name)
    if pure.is_absolute():
        raise ContentUpdateError(
            "The pack contains an unsafe path. The last good pack is still in use.",
            status="rejected",
        )
    parts = pure.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ContentUpdateError(
            "The pack contains an unsafe path. The last good pack is still in use.",
            status="rejected",
        )
    return parts


def _check_member(parts: tuple[str, ...]) -> None:
    if any(out_of_scope_part(part) for part in parts):
        raise ContentUpdateError(
            "The pack contains a foam or clean-agent path, which is out of scope. The last good pack is still in use.",
            status="rejected",
        )
    if any(forbidden_part(part) for part in parts):
        raise ContentUpdateError(
            "The pack contains a stripped path. The last good pack is still in use.",
            status="rejected",
        )
    top = parts[0]
    if top == MARKER_NAME:
        if len(parts) != 1:
            raise ContentUpdateError(
                "The pack contains an unsafe path. The last good pack is still in use.",
                status="rejected",
            )
        return
    if top not in ALLOWED_TOP:
        raise ContentUpdateError(
            "The pack contains a file outside the content folders. The last good pack is still in use.",
            status="rejected",
        )
    lowered = parts[-1].casefold()
    if lowered in BLOCKED_FILE_NAMES or lowered.startswith(".env"):
        raise ContentUpdateError(
            "The pack contains a key or settings file. The last good pack is still in use.",
            status="rejected",
        )


def _zip_name_ok(name: str) -> bool:
    if "/" in name or "\\" in name or name in {".", ".."}:
        return False
    if not name.endswith(".zip"):
        return False
    stem = name[:-4]
    return bool(stem) and all(char.isalnum() or char in "._-" for char in stem)


def _is_newer(remote: str, local: str) -> bool:
    """Whether the feed's pack replaces what is in use: only a numbered version greater than a numbered local one.

    The bundled seed carries its own number (fpfa.content_pack.seed_marker), so
    a published pack older than or equal to the seed leaves it in place. A
    local label with no number (a source checkout, a seed built before seeds
    were numbered) is replaced by any numbered pack.
    """
    remote_numbers = parse_version_numbers(remote)
    local_numbers = parse_version_numbers(local)
    if remote_numbers is None:
        return False
    if local_numbers is None:
        return True
    return remote_numbers > local_numbers


def _marker_version(root: Path) -> str:
    path = root / MARKER_NAME
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(data, dict):
        return ""
    version = data.get("version")
    if not isinstance(version, str):
        return ""
    numbered = canonical_version(version)
    if numbered:
        return numbered
    if version.strip() == "seed":
        return "bundled seed"
    return ""


def _is_seed(root: Path) -> bool:
    from fpfa.paths import _bundled_seed_candidates

    try:
        resolved = root.resolve()
    except OSError:
        return False
    for candidate in _bundled_seed_candidates():
        try:
            if candidate.resolve() == resolved and is_content_pack(candidate):
                return True
        except OSError:
            continue
    return False


def _require_http(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContentUpdateError(
            "The pack address must be an http or https URL. The last good pack is still in use.",
            status="rejected",
        )


def _opener_open(opener, url: str, timeout: float):
    request = urllib.request.Request(url, headers=request_headers())
    return opener.open(request, timeout=timeout)


def _get_json(url: str, opener) -> dict:
    try:
        with _opener_open(opener, url, 20) as response:
            payload = response.read(MAX_MANIFEST_BYTES + 1)
    except ContentUpdateError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise _transport_error(exc) from exc
    if len(payload) > MAX_MANIFEST_BYTES:
        raise ContentUpdateError(
            "The manifest is too large. The last good pack is still in use.",
            status="rejected",
        )
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContentUpdateError(
            "The feed did not return a content manifest. The last good pack is still in use.",
            status="rejected",
        ) from exc
    if not isinstance(document, dict):
        raise ContentUpdateError(
            "The feed is not a content manifest. The last good pack is still in use.",
            status="rejected",
        )
    return document


def _download_file(url: str, dest: Path, opener) -> None:
    total = 0
    try:
        with _opener_open(opener, url, 60) as response, dest.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_PACK_BYTES:
                    raise ContentUpdateError(
                        "The pack is larger than this app will install. The last good pack is still in use.",
                        status="rejected",
                    )
                handle.write(chunk)
    except ContentUpdateError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise _transport_error(exc) from exc


def _transport_error(exc: BaseException) -> ContentUpdateError:
    status = _failure_status(exc)
    return ContentUpdateError(_failure_message(exc, status), status=status)


def _failure_status(exc: BaseException) -> str:
    if isinstance(exc, ContentUpdateError):
        return exc.status
    if isinstance(exc, urllib.error.HTTPError):
        return "error"
    if isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError)):
        return "offline"
    return "error"


def _failure_message(exc: BaseException, status: str) -> str:
    if isinstance(exc, ContentUpdateError):
        return str(exc)
    if status == "offline":
        return "The content feed did not answer. The last good pack is still in use."
    return "The content update did not finish. The last good pack is still in use."

