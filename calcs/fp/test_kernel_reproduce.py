"""Reproduce check for the kernel files in this folder.

Skipped unless FP_KERNEL_DIR names a kernel source folder. The check lives in
the repository's scripts/ folder, so it is also skipped in a bare content pack.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
CHECK = HERE.parents[1] / "scripts" / "check_fp_kernel_reproduce.py"
KERNEL_DIR = os.environ.get("FP_KERNEL_DIR", "")


def _run(kernel_dir):
    return subprocess.run(
        [sys.executable, str(CHECK), "--kernel-dir", str(kernel_dir), "--pack-dir", str(HERE)],
        capture_output=True,
        text=True,
    )


@unittest.skipUnless(KERNEL_DIR, "set FP_KERNEL_DIR to a kernel source folder to run the reproduce check")
@unittest.skipUnless(CHECK.is_file(), "scripts/check_fp_kernel_reproduce.py is not in this tree")
class KernelReproduceTests(unittest.TestCase):
    def test_pack_kernel_is_reproduced_and_an_edit_is_caught(self):
        same = _run(KERNEL_DIR)
        self.assertEqual(same.returncode, 0, same.stdout + same.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            altered = pathlib.Path(tmp)
            for name in ("formulas.py", "run.py", "test_formulas.py"):
                shutil.copy(pathlib.Path(KERNEL_DIR) / name, altered / name)
            text = (altered / "formulas.py").read_text(encoding="utf-8")
            self.assertIn("7.48", text)
            (altered / "formulas.py").write_text(text.replace("7.48", "7.49", 1), encoding="utf-8")
            diff = _run(altered)
        self.assertEqual(diff.returncode, 1, diff.stdout + diff.stderr)
        self.assertIn("formulas.py", diff.stdout)


if __name__ == "__main__":
    unittest.main()
