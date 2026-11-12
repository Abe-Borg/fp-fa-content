"""Locate the content pack and the per-user data directory."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    """Directory that contains app/, skills/, and calcs/ in a source checkout."""
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    override = os.environ.get("FPFA_DATA_DIR")
    if override:
        path = Path(override)
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        path = base / "fpfa-assistant"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        path = base / "fpfa-assistant"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return data_dir() / "config.json"


def read_config() -> dict:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_config(data: dict) -> dict:
    config_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def write_config(updates: dict) -> dict:
    data = read_config()
    data.update(updates)
    return save_config(data)


def is_content_pack(path: Path) -> bool:
    """True when this folder has the skills tree and the calc kernel the app imports."""
    try:
        return (path / "skills").is_dir() and (path / "calcs" / "fp" / "formulas.py").is_file()
    except OSError:
        return False


def _bundled_seed_candidates() -> list[Path]:
    """Seed folders, earliest first.

    A frozen app looks beside the executable and inside the PyInstaller bundle.
    A source checkout uses the repo root. The saved Settings folder is not a seed.
    """
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "seed")
        candidates.append(Path(sys.executable).resolve().parent / "seed")
    candidates.append(repo_root())
    return candidates


def _marker_numbers(root: Path) -> tuple[int, ...] | None:
    """The numbered version in a folder's pack.json, or None."""
    from fpfa.content_pack import MARKER_NAME, parse_version_numbers

    try:
        data = json.loads((root / MARKER_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = data.get("version") if isinstance(data, dict) else None
    return parse_version_numbers(version) if isinstance(version, str) else None


def _older_than_seed(saved: Path) -> bool:
    """True when the saved folder is a pack the updater installed and the bundled seed is numbered higher.

    After an app upgrade the new seed can be newer than the pack an earlier
    version downloaded. That pack is passed over so it does not stand in for
    the newer seed. A folder the designer chose elsewhere is never passed
    over, and FPFA_CONTENT_ROOT is not affected.
    """
    try:
        installs = (data_dir() / "content-packs").resolve()
        if saved.resolve().parent != installs:
            return False
    except OSError:
        return False
    installed = _marker_numbers(saved)
    if installed is None:
        return False
    for seed in _bundled_seed_candidates():
        if is_content_pack(seed):
            numbers = _marker_numbers(seed)
            return numbers is not None and numbers > installed
    return False


def content_root() -> Path:
    """Env pin, the folder saved in Settings, then the bundled seed.

    A content pack has the same top-level layout: skills/, roles/, modes/, calcs/, corpus/, specs/.
    The bundled seed is the source checkout, or the seed folder shipped with a frozen app.
    An incomplete saved folder is skipped so a bad update cannot blank the app, and so
    is a downloaded pack older than the bundled seed (_older_than_seed).
    """
    candidates = []
    env = os.environ.get("FPFA_CONTENT_ROOT")
    if env:
        candidates.append(Path(env))
    saved = read_config().get("content_root")
    if saved and not _older_than_seed(Path(saved)):
        candidates.append(Path(saved))
    candidates.extend(_bundled_seed_candidates())
    seen = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if is_content_pack(path):
            return resolved
    raise FileNotFoundError(
        "Content pack not found. Expected skills/ and calcs/fp/formulas.py. "
        "Set FPFA_CONTENT_ROOT or choose the folder in Settings."
    )
