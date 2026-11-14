"""The app's name, its license, and the versions of everything it runs on.

Acceptance test A records the runtime and dependency versions of an install.
These lines are what the About box and `python -m fpfa --versions` print, so
the record is the same whether it comes from a frozen exe or a source checkout.

The name and the license facts live here once. The window title, the About
box, the installer script, and the README repeat them, and tests keep the
copies in step.
"""

from __future__ import annotations

import platform
import sys
from importlib import metadata
from pathlib import Path

from fpfa import __version__
from fpfa.claude_client import MODEL_ID

APP_NAME = "+Cynosure"
# The name without the plus sign, for a file or folder name.
APP_FILE_NAME = "Cynosure"
APP_TAGLINE = "Fire protection and fire alarm design"
# The line under the wordmark, short enough for the sidebar.
APP_STRAPLINE = "FP/FA design assistant"
APP_AUTHOR = "Abraham Borg"
COPYRIGHT = "Copyright (c) 2026 Abraham Borg"
PROJECT_URL = "https://github.com/Abe-Borg/fp-fa-content"
LICENSE_NAME = "Proprietary License Notice"
LICENSE_URL = f"{PROJECT_URL}/blob/main/LICENSE"
# Brief permission summary. The full notice and any separate agreement govern.
LICENSE_SUMMARY = (
    f"{APP_NAME} is proprietary under the {LICENSE_NAME}. All rights reserved. "
    "Use, copying, modification, and redistribution require separate written permission from Abraham Borg, "
    "except where applicable law or an existing applicable license permits them."
)
# What every designer should know before relying on a figure from the app.
USE_NOTICE = (
    "It comes as is, without warranty. Its output is a draft for the engineer of record to review. "
    "A delivery time from its tools is an optimistic screen, not a listed water-delivery-time calculation."
)
LICENSE_FILE = "LICENSE.txt"
NOTICES_FILE = "THIRD-PARTY-NOTICES.txt"

# pywebview and pythonnet show the window (WebView2); the page adds the WebView2 version it runs in.
DEPENDENCIES = ("anthropic", "python-docx", "keyring", "pywin32-ctypes", "pywebview", "pythonnet", "pyinstaller")


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
        f"{APP_NAME} {__version__}" + (" (frozen)" if getattr(sys, "frozen", False) else " (source)"),
        f"Model {MODEL_ID}",
        f"Python {platform.python_version()} on {platform.system()} {platform.release()} ({platform.machine()})",
    ]
    for name in DEPENDENCIES:
        lines.append(f"{name} {_dist_version(name)}")
    try:
        root = content_root or resolve_root()
        lines.append(f"Content pack {content_version_text()} at {root}")
        try:
            from fpfa.calc_tools import calc_identity, content_fingerprint

            # What the pack actually holds, whatever its label says. An evaluation report and an export print
            # the same two values, so a result can be tied to the content that produced it.
            lines.append(f"Content fingerprint {content_fingerprint(root)}, calc code {calc_identity(root)}")
        except Exception:
            lines.append("Content fingerprint: could not be read")
    except FileNotFoundError:
        lines.append("Content pack: not found")
    lines.append(f"Data directory {data_dir or resolve_data()}")
    lines.append(f"Record schema {SCHEMA_VERSION}")
    return lines


def version_text(content_root: Path | None = None, data_dir: Path | None = None) -> str:
    return "\n".join(version_lines(content_root, data_dir))


def _document_candidates(name: str) -> list[Path]:
    """Where a shipped text file can be, earliest first.

    The installer puts LICENSE.txt and the notices beside the exe. PyInstaller
    also carries the license inside the bundle. A source checkout has the
    license at the repository root, named LICENSE.
    """
    here = Path(__file__).resolve()
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / name)
        bundle = getattr(sys, "_MEIPASS", None)
        if bundle:
            candidates.append(Path(bundle) / name)
    repo = here.parents[2]
    candidates.append(repo / name)
    if name == LICENSE_FILE:
        candidates.append(repo / "LICENSE")
    candidates.append(here.parents[1] / "dist" / name)
    return candidates


def read_document(name: str) -> str:
    """The text of LICENSE.txt or the third-party notices, or "" when this copy has none."""
    for path in _document_candidates(name):
        try:
            if path.is_file():
                return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return ""


def license_text() -> str:
    """The license terms this copy ships with. A copy without the file names where the terms are."""
    found = read_document(LICENSE_FILE)
    if found:
        return found
    return f"{LICENSE_NAME}\n{LICENSE_URL}\n\n{COPYRIGHT}. All rights reserved.\n\n{LICENSE_SUMMARY}\n"


def notices_text() -> str:
    """The license texts of the software the app bundles. Written by the Windows build."""
    found = read_document(NOTICES_FILE)
    if found:
        return found
    return (
        "The third-party notices are written when the Windows app is built "
        f"(app/packaging/third_party_notices.py) and installed beside the app as {NOTICES_FILE}. "
        "A source checkout does not carry the file: each dependency's license is in its own "
        "installed package."
    )


def about_text(content_root: Path | None = None, data_dir: Path | None = None) -> str:
    """What the About box shows: the name, the license in brief, and the version lines."""
    return "\n".join([
        f"{APP_NAME}: {APP_TAGLINE.lower()} for hyperscale data centers.",
        COPYRIGHT + ".",
        "",
        LICENSE_SUMMARY,
        USE_NOTICE,
        "",
        *version_lines(content_root, data_dir),
    ])
