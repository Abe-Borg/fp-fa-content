#!/usr/bin/env python3
"""Check that calcs/fp/ is reproducible from a kernel source folder.

Stages formulas.py, run.py and test_formulas.py from --kernel-dir into a temp
folder with scripts/fp_kernel_stage.py, then byte-compares the three files with
calcs/fp/. Line endings are normalised first, so a Windows checkout compares
the same as a Linux one.

Usage:
    python3 scripts/check_fp_kernel_reproduce.py --kernel-dir DIR [--pack-dir calcs/fp]

Exit 0: all three files are byte-identical.
Exit 1: at least one differs. A short diff summary is printed.
Exit 2: the kernel folder could not be staged (missing file or edited text the
staging rules do not expect).
"""

from __future__ import annotations

import argparse
import difflib
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fp_kernel_stage as stage  # noqa: E402

REPO = HERE.parent
MAX_DIFF_LINES = 12


def _text(path: pathlib.Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def compare(staged_dir: pathlib.Path, pack_dir: pathlib.Path) -> list[str]:
    """Return one summary block per differing file; empty when identical."""
    problems = []
    for name in stage.KERNEL_FILES:
        want = _text(staged_dir / name)
        have_path = pack_dir / name
        if not have_path.is_file():
            problems.append(f"{name}: missing from {pack_dir}")
            continue
        have = _text(have_path)
        if want == have:
            continue
        diff = list(
            difflib.unified_diff(
                have.splitlines(), want.splitlines(), f"pack/{name}", f"staged/{name}", lineterm="", n=0
            )
        )
        changed = sum(1 for d in diff if d[:1] in "+-" and d[:3] not in ("+++", "---"))
        shown = diff[:MAX_DIFF_LINES]
        more = "" if len(diff) <= MAX_DIFF_LINES else f"\n  ... {len(diff) - MAX_DIFF_LINES} more diff lines"
        problems.append(f"{name}: {changed} changed line(s)\n" + "\n".join("  " + d for d in shown) + more)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reproduce calcs/fp kernel files from a kernel source folder.")
    parser.add_argument("--kernel-dir", required=True, type=pathlib.Path, help="folder holding the kernel source .py files")
    parser.add_argument("--pack-dir", type=pathlib.Path, default=REPO / "calcs" / "fp", help="pack copy to compare (default: calcs/fp)")
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        staged_dir = pathlib.Path(tmp)
        try:
            stage.stage_dir(args.kernel_dir, staged_dir)
        except (stage.StageError, SyntaxError, OSError) as exc:
            print(f"FAIL: could not stage the kernel: {exc}", file=sys.stderr)
            return 2
        problems = compare(staged_dir, args.pack_dir)
    if problems:
        print("FAIL: calcs/fp differs from the staged kernel:")
        print("\n".join(problems))
        return 1
    print("OK: formulas.py, run.py, test_formulas.py are byte-identical to the staged kernel")
    return 0


if __name__ == "__main__":
    sys.exit(main())
