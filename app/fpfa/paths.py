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


def content_root() -> Path:
    """Env pin, the folder saved in Settings, then the bundled seed.

    A content pack has the same top-level layout: skills/, roles/, modes/, calcs/, corpus/, specs/.
    The bundled seed is the source checkout, or the seed folder shipped with a frozen app.
    An incomplete saved folder is skipped so a bad update cannot blank the app.
    """
    candidates = []
    env = os.environ.get("FPFA_CONTENT_ROOT")
    if env:
        candidates.append(Path(env))
    saved = read_config().get("content_root")
    if saved:
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
