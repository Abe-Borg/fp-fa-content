#!/usr/bin/env python3
"""Build a distributable folder with a seed content pack.

PyInstaller builds for the OS it is running on. A Windows run writes
fpfa.exe. A Linux run writes a Linux folder. The packaged app checks the
release feed on launch. On Windows, packaging/build_installer.ps1 compiles
the setup exe after this script. Upload fpfa-setup-<version>.exe to a
GitHub Release.

From the app directory:

    python3 packaging/build_app.py
    python3 packaging/build_app.py --seed-only
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

from fpfa.content_pack import copy_pack  # noqa: E402
from fpfa.paths import is_content_pack  # noqa: E402


def write_seed(dest: Path) -> list[str]:
    """Copy the curated trees into dest. The seed has no pack.json and no app/."""
    if dest.exists():
        shutil.rmtree(dest)
    stripped = copy_pack(REPO, dest)
    if not is_content_pack(dest):
        raise SystemExit("seed is missing skills/ or calcs/fp/formulas.py")
    return stripped


def keyring_bundle_flags(*, windows: bool) -> list[str]:
    """PyInstaller flags that let the frozen app reach the OS keyring.

    keyring finds its backends through importlib.metadata entry points, so the
    bundle needs keyring's dist-info and the backend modules those entry points
    name. On Windows the backend uses pywin32-ctypes, which loads its ctypes or
    cffi submodules at run time, where static analysis cannot see them.
    PyInstaller 6 ships hooks (hook-keyring, hook-win32ctypes.core) that already
    do this. These flags keep the build correct if a PyInstaller release drops
    or changes those hooks.
    """
    flags = [
        "--copy-metadata",
        "keyring",
        "--collect-submodules",
        "keyring.backends",
    ]
    if windows:
        flags += [
            "--hidden-import",
            "keyring.backends.Windows",
            "--hidden-import",
            "win32ctypes.pywin32.win32cred",
            "--hidden-import",
            "win32ctypes.pywin32.pywintypes",
            "--collect-submodules",
            "win32ctypes",
        ]
    return flags


def pyinstaller_command(
    seed: Path, dist: Path, work: Path, *, windowed: bool, windows: bool | None = None
) -> list[str]:
    if windows is None:
        windows = os.name == "nt"
    entry = APP_DIR / "fpfa" / "__main__.py"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "fpfa",
        "--paths",
        str(APP_DIR),
        "--distpath",
        str(dist),
        "--workpath",
        str(work),
        "--specpath",
        str(work),
        "--add-data",
        f"{seed}{os.pathsep}seed",
        "--hidden-import",
        "fpfa",
        "--hidden-import",
        "anthropic",
        "--hidden-import",
        "docx",
        "--hidden-import",
        "keyring",
        *keyring_bundle_flags(windows=windows),
        "--windowed" if windowed else "--console",
        str(entry),
    ]
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a distributable FP/FA app folder")
    parser.add_argument("--seed-only", action="store_true", help="Write the seed folder and stop")
    parser.add_argument("--seed", default=str(APP_DIR / "build" / "seed"), help="Seed output directory")
    parser.add_argument("--dist", default=str(APP_DIR / "dist"), help="PyInstaller dist directory")
    parser.add_argument("--console", action="store_true", help="Keep a console window")
    parser.add_argument("--windowed", action="store_true", help="Hide the console")
    args = parser.parse_args(argv)
    if args.console and args.windowed:
        parser.error("choose one of --console or --windowed")
    seed = Path(args.seed)
    stripped = write_seed(seed)
    for rel in stripped:
        sys.stderr.write(f"stripped {rel}\n")
    sys.stdout.write(f"seed {seed}\n")
    if args.seed_only:
        return 0
    if importlib.util.find_spec("PyInstaller") is None:
        sys.stderr.write(
            "PyInstaller is not installed. From the app directory:\n"
            "  python3 -m pip install pyinstaller\n"
            "Then re-run this script. A Windows exe is produced when the script runs on Windows.\n"
        )
        return 2
    windowed = args.windowed or (os.name == "nt" and not args.console)
    dist = Path(args.dist)
    work = APP_DIR / "build" / "pyinstaller"
    if work.exists():
        shutil.rmtree(work)
    command = pyinstaller_command(seed, dist, work, windowed=windowed)
    proc = subprocess.run(command, check=False)
    if proc.returncode != 0:
        return proc.returncode
    folder = dist / "fpfa"
    exe = folder / ("fpfa.exe" if os.name == "nt" else "fpfa")
    sys.stdout.write(f"built {exe}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
