#!/usr/bin/env python3
"""Build a distributable +Cynosure folder with a seed content pack.

PyInstaller builds for the OS it is running on. A Windows run writes
dist/Cynosure/Cynosure.exe. A Linux run writes a Linux folder. The packaged
app checks the release feed on launch. On Windows,
packaging/build_installer.ps1 compiles the setup exe after this script.
Upload Cynosure-Setup-<version>.exe to a GitHub Release.

The folder carries its license terms. After PyInstaller finishes, this
script copies the repository's LICENSE into the folder as LICENSE.txt and
writes THIRD-PARTY-NOTICES.txt beside it (third_party_notices.py), so the
installer and the portable zip both ship them. A license text that cannot be
found fails the build.

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

# The exe and its folder. The app's name is "+Cynosure"; a file name leaves the plus off.
BUNDLE_NAME = "Cynosure"
ICON = APP_DIR / "packaging" / "assets" / "Cynosure.ico"
LICENSE_SOURCE = REPO / "LICENSE"
LICENSE_NAME = "LICENSE.txt"
NOTICES_NAME = "THIRD-PARTY-NOTICES.txt"


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


def version_metadata_flags(*, windows: bool) -> list[str]:
    """Package metadata the About box reads, so a packaged app reports its dependency versions.

    Without it, importlib.metadata finds nothing in the bundle and About
    says "not installed" for a package that is in fact bundled. keyring's
    metadata is already copied for its backends.
    """
    names = ["anthropic", "python-docx"]
    if windows:
        names.append("pywin32-ctypes")
    flags: list[str] = []
    for name in names:
        flags += ["--copy-metadata", name]
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
        BUNDLE_NAME,
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
        *version_metadata_flags(windows=windows),
        "--windowed" if windowed else "--console",
    ]
    if windows:
        # The icon of the exe, the taskbar, and the shortcuts. Other systems have no exe icon.
        command += ["--icon", str(ICON)]
    command.append(str(entry))
    return command


def finish_bundle(folder: Path, *, notices: bool = True) -> list[str]:
    """Put the license terms in the built folder. Returns the names written.

    LICENSE.txt is the repository's LICENSE, byte for byte.
    THIRD-PARTY-NOTICES.txt holds the license of everything bundled; a text
    that cannot be found raises NoticesError and nothing is written for it.
    """
    written = []
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LICENSE_SOURCE, folder / LICENSE_NAME)
    written.append(LICENSE_NAME)
    if notices:
        sys.path.insert(0, str(APP_DIR / "packaging"))
        try:
            import third_party_notices
        finally:
            sys.path.pop(0)
        third_party_notices.write_notices(folder / NOTICES_NAME)
        written.append(NOTICES_NAME)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a distributable +Cynosure app folder")
    parser.add_argument("--seed-only", action="store_true", help="Write the seed folder and stop")
    parser.add_argument("--seed", default=str(APP_DIR / "build" / "seed"), help="Seed output directory")
    parser.add_argument("--dist", default=str(APP_DIR / "dist"), help="PyInstaller dist directory")
    parser.add_argument("--console", action="store_true", help="Keep a console window")
    parser.add_argument("--windowed", action="store_true", help="Hide the console")
    parser.add_argument(
        "--skip-notices",
        action="store_true",
        help="Leave out THIRD-PARTY-NOTICES.txt. For a local trial only: do not distribute the folder.",
    )
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
    folder = dist / BUNDLE_NAME
    exe = folder / (f"{BUNDLE_NAME}.exe" if os.name == "nt" else BUNDLE_NAME)
    try:
        written = finish_bundle(folder, notices=not args.skip_notices)
    except Exception as exc:
        sys.stderr.write(f"The folder was built, but its license terms could not be written.\n{exc}\n")
        return 1
    for name in written:
        sys.stdout.write(f"wrote {folder / name}\n")
    if args.skip_notices:
        sys.stderr.write(f"{NOTICES_NAME} was skipped. Do not distribute this folder.\n")
    sys.stdout.write(f"built {exe}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
