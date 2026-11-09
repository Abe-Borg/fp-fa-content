#!/usr/bin/env python3
"""Write the app icon, packaging/assets/Cynosure.ico.

The icon is the four-point star from the window (fpfa.shapes.star_mark) on a
rounded square, at the sizes Windows asks for. PyInstaller puts it on the
exe, and the installer uses it for Setup and the shortcuts. The drawing is
pure Python, so this needs nothing installed. Run it again after a change to
the star or its colours, and commit the file:

    python packaging/make_icon.py
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from fpfa import shapes  # noqa: E402

ICON_PATH = Path(__file__).resolve().parent / "assets" / "Cynosure.ico"
SIZES = (16, 20, 24, 32, 40, 48, 64, 256)
# The colours of fpfa.theme.ICON_STAR and ICON_BACKGROUND. tests/test_branding.py keeps them equal.
STAR = "#d97757"
BACKGROUND = "#1d1d1b"


def icon_bytes() -> bytes:
    return shapes.encode_ico([shapes.star_mark(size, STAR, BACKGROUND) for size in SIZES])


def main() -> int:
    ICON_PATH.parent.mkdir(parents=True, exist_ok=True)
    ICON_PATH.write_bytes(icon_bytes())
    sys.stdout.write(f"wrote {ICON_PATH} ({ICON_PATH.stat().st_size} bytes, sizes {SIZES})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
