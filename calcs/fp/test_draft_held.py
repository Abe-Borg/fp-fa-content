"""The El/Pn draft in calcs/fp/draft/ is held: nothing loads it and no tool can reach it.

This test fails if a pack module, the tool plan, or app code starts importing the draft,
if the dispatch tables learn its name, or if the draft stops saying it is held.
It also runs the draft's own tests in a separate process, so the draft is never imported here.
"""

import pathlib
import re
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DRAFT = HERE / "draft"
ROOT = HERE.parents[1]
# Built from pieces so this file does not match its own scan.
MODULE = "el_pn" + "_release"
LOAD = re.compile(r"(?:import|from)\s+[\w.]*" + MODULE + r"|" + MODULE + r"\s*\.\s*py|calcs/fp/draft|[\"']draft[\"']|\bdraft\b\s*/")


def _sources():
    """Every .py file under calcs/ (outside draft/) and, when present, app/."""
    folders = [HERE.parent]
    if (ROOT / "app").is_dir():
        folders.append(ROOT / "app")
    for folder in folders:
        for path in sorted(folder.rglob("*.py")):
            if DRAFT in path.parents or path.resolve() == pathlib.Path(__file__).resolve():
                continue
            if "node_modules" in path.parts:
                continue
            yield path


class DraftHeldTests(unittest.TestCase):
    def test_draft_files_are_present_and_say_held(self):
        text = (DRAFT / (MODULE + ".py")).read_text(encoding="utf-8")
        self.assertIn('STATUS = "DRAFT, HELD, NOT WIRED"', text)
        self.assertIn("do not import", text.splitlines()[1].lower())
        self.assertIn("HELD", (DRAFT / "README.md").read_text(encoding="utf-8"))

    def test_nothing_in_the_pack_or_the_app_loads_the_draft(self):
        offenders = []
        for path in _sources():
            text = path.read_text(encoding="utf-8", errors="replace")
            for number, line in enumerate(text.splitlines(), 1):
                if MODULE in line or LOAD.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}")
        self.assertEqual(offenders, [], "the held draft is referenced from live code")

    def test_dispatch_and_output_tables_do_not_know_the_draft(self):
        formulas = (HERE / "formulas.py").read_text(encoding="utf-8")
        cli_text = (HERE / "run.py").read_text(encoding="utf-8")
        for text in (formulas, cli_text):
            self.assertNotIn("el_pn", text.lower())
            self.assertNotIn("valve_release", text)

    def test_draft_directory_is_not_a_package(self):
        self.assertFalse((DRAFT / "__init__.py").exists())

    def test_draft_own_tests_pass_in_their_own_process(self):
        done = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(DRAFT), "-p", "test_*.py"],
            capture_output=True,
            text=True,
            cwd=str(DRAFT),
        )
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
