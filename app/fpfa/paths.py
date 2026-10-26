"""Locate the content pack and the per-user data directory."""

from __future__ import annotations

import json
import os
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


def write_config(updates: dict) -> dict:
    data = read_config()
    data.update(updates)
    config_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def content_root() -> Path:
    """Repo checkout, FPFA_CONTENT_ROOT, or the folder saved in Settings.

    A content pack has the same top-level layout: skills/, roles/, modes/, calcs/, corpus/, specs/.
    """
    candidates = []
    env = os.environ.get("FPFA_CONTENT_ROOT")
    if env:
        candidates.append(Path(env))
    saved = read_config().get("content_root")
    if saved:
        candidates.append(Path(saved))
    candidates.append(repo_root())
    for path in candidates:
        if (path / "skills").is_dir() and (path / "calcs" / "fp" / "formulas.py").is_file():
            return path.resolve()
    raise FileNotFoundError(
        "Content pack not found. Expected skills/ and calcs/fp/formulas.py. "
        "Set FPFA_CONTENT_ROOT or choose the folder in Settings."
    )
