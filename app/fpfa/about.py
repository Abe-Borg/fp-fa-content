"""Versions of the app, its runtime, its dependencies, and the content pack.

Acceptance test A records the runtime and dependency versions of an install.
These lines are what the About box and `python -m fpfa --versions` print, so
the record is the same whether it comes from a frozen exe or a source checkout.
"""

from __future__ import annotations

import platform
import sys
from importlib import metadata
from pathlib import Path

from fpfa import __version__
from fpfa.claude_client import MODEL_ID

DEPENDENCIES = ("anthropic", "python-docx", "keyring", "pywin32-ctypes", "pyinstaller")


def _dist_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"


def version_lines(content_root: Path | None = None, data_dir: Path | None = None) -> list[str]:
    """One line per fact. Nothing here reads the network or the key store."""
    from fpfa.content_update import content_version_text
    from fpfa.paths import content_root as resolve_root
    from fpfa.paths import data_dir as resolve_data
    from fpfa.record import SCHEMA_VERSION

    lines = [
        f"FP/FA Design Assistant {__version__}" + (" (frozen)" if getattr(sys, "frozen", False) else " (source)"),
        f"Model {MODEL_ID}",
        f"Python {platform.python_version()} on {platform.system()} {platform.release()} ({platform.machine()})",
    ]
    for name in DEPENDENCIES:
        lines.append(f"{name} {_dist_version(name)}")
    try:
        root = content_root or resolve_root()
        lines.append(f"Content pack {content_version_text()} at {root}")
    except FileNotFoundError:
        lines.append("Content pack: not found")
    lines.append(f"Data directory {data_dir or resolve_data()}")
    lines.append(f"Record schema {SCHEMA_VERSION}")
    return lines


def version_text(content_root: Path | None = None, data_dir: Path | None = None) -> str:
    return "\n".join(version_lines(content_root, data_dir))
