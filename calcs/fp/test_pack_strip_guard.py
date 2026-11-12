"""Guards on what a content pack may ship.

These tests read the repository's scripts/ folder (the strip scan and the pack builder). They
are skipped when calcs/fp is copied alone into a bare content pack, where scripts/ is absent.

What each guard covers:
  - the strip scan runs over every folder a pack ships, not only calcs/, and catches the
    QA-EX tag form as well as plain QA ids and batch tags;
  - the names the scan bans may stay only where a reviewed baseline records the exact count;
  - a banned name or a tag in a directory or a file name is a finding on its own. The per-file
    content baseline does not cover it, and the builder refuses the tree;
  - the builder stops on an out-of-scope slug, and packs a Canada-named path under its own name
    (Canada is in scope through a skill's Country gate), so nothing is dropped without a message;
  - the held draft folder under calcs/fp is left out of the zip.

A pass shows the scripts behave as described on these trees. It is not an engineering review.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
BUILD = SCRIPTS / "build_content_pack.py"
SCAN = SCRIPTS / "check_pack_strip.py"

if SCRIPTS.is_dir():
    sys.path.insert(0, str(SCRIPTS))

_FP = Path(__file__).resolve().parent
sys.path.insert(0, str(_FP))
from place_name_scan import banned_words  # noqa: E402


def _scan():
    import check_pack_strip

    return check_pack_strip


# The tags the scan must catch are assembled here so this file does not carry them itself.
QA_EX = "QA" + "-EX33-77"
QA_PLAIN = "q" + "a2"
QA_DASH = "QA" + "-6"
BATCH = "bat" + "ch 41"
BATCH_DIR = "bat" + "ch12"
ROUND_STD = "ROUND" + "-STANDARD"
# The held-draft scan in test_draft_held.py flags literal draft paths, so these are built from pieces.
DRAFT_DIR = "calcs/fp/" + "dr" + "aft"
DRAFT_MODULE = "el_pn" + "_release"
# Out-of-scope slugs, built from pieces so this file does not add to the scope-word counts.
OOS_A = "cl" + "ean-agent-concentration-and-quantity"
OOS_B = "cl" + "ean_agent_zone"
OOS_C = "fo" + "am-water-demand"
OOS_D = "cl" + "ean-agent-enclosure-integrity"


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mini_pack(root: Path) -> None:
    _write(root, "skills/demo-skill/SKILL.md", "---\nname: demo-skill\n---\nA short skill.\n")
    _write(root, "calcs/fp/formulas.py", "VALUE = 1\n")
    _write(root, f"{DRAFT_DIR}/{DRAFT_MODULE}.py", "HELD = True\n")
    _write(root, f"{DRAFT_DIR}/README.md", "held draft\n")


def _build(source: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILD), "--source", str(source), "--out", str(out), "--version", "9.9.9"],
        capture_output=True,
        text=True,
    )


def _insurer_word() -> str:
    return next(word for word in banned_words() if len(word) == 3 and word.lower().startswith("a") and word.lower().endswith("a"))


@unittest.skipUnless(SCRIPTS.is_dir(), "scripts/ is not in this tree")
class StripScanTests(unittest.TestCase):
    def test_shipped_tree_is_strip_clean(self):
        findings = _scan().strip_findings(ROOT)
        self.assertEqual(findings, [], "\n".join(findings))

    def test_qa_ex_tag_is_caught(self):
        scan = _scan()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "calcs/fa/lib/demo.py", f"# Do not stack the factor ({QA_EX} F-2).\n")
            _write(root, "skills/a/SKILL.md", f"Checked in {QA_PLAIN} and {QA_DASH}.\n")
            _write(root, "corpus/n.md", "Clean line.\n")
            findings = scan.strip_findings(root, baseline={})
        text = "\n".join(findings)
        self.assertIn("calcs/fa/lib/demo.py:1", text)
        self.assertIn("skills/a/SKILL.md:1", text)
        self.assertNotIn("corpus/n.md", text)

    def test_batch_and_round_standard_tags_are_caught(self):
        scan = _scan()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "specs/s.md", f"Added in {BATCH}.\nSee {ROUND_STD}.\n")
            findings = scan.strip_findings(root, baseline={})
        self.assertEqual(len([f for f in findings if f.startswith("specs/s.md:")]), 2)

    def test_names_are_caught_in_every_pack_folder(self):
        scan = _scan()
        word = next(w for w in banned_words() if len(w) >= 6)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for top, name in (("skills", "a/SKILL.md"), ("corpus", "c.md"), ("specs", "s.md"), ("roles", "r/ROLE.md"), ("modes", "m/MODE.md")):
                _write(root, f"{top}/{name}", f"Job at {word} site.\n")
            findings = scan.strip_findings(root, baseline={})
        for top in ("skills", "corpus", "specs", "roles", "modes"):
            self.assertTrue(any(f.startswith(top + "/") for f in findings), top)

    def test_baseline_must_match_exactly(self):
        scan = _scan()
        word = _insurer_word()
        cls = scan.name_class(word)
        self.assertIsNotNone(cls, "the insurer name must have a baseline class")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "skills/a/SKILL.md", f"{word} one.\n{word} two.\n")
            _write(root, "skills/b/SKILL.md", f"{word} three.\n")
            base = {"skills/a/SKILL.md": {cls: 2}}
            findings = scan.strip_findings(root, baseline=base)
            self.assertTrue(any(f.startswith("skills/b/SKILL.md") for f in findings), "unbaselined file must fail")
            self.assertFalse(any(f.startswith("skills/a/SKILL.md") for f in findings), "exact count passes")
            more = scan.strip_findings(root, baseline={"skills/a/SKILL.md": {cls: 1}, "skills/b/SKILL.md": {cls: 1}})
            self.assertTrue(any("skills/a/SKILL.md" in f for f in more), "a new hit must fail")
            fewer = scan.strip_findings(root, baseline={"skills/a/SKILL.md": {cls: 3}, "skills/b/SKILL.md": {cls: 1}})
            self.assertTrue(any("skills/a/SKILL.md" in f for f in fewer), "a shrunk count must be reported")

    def test_baseline_never_covers_calcs(self):
        baseline = json.loads((SCRIPTS / "strip_scan_baseline.json").read_text(encoding="utf-8"))
        for rel in baseline["counts"]:
            self.assertFalse(rel.startswith("calcs/"), rel)

    def test_banned_name_in_a_directory_component_is_a_finding(self):
        scan = _scan()
        word = _insurer_word()
        cls = scan.name_class(word)
        rel = f"skills/{word}/SKILL.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, rel, f"Sheet cites {word} once.\n")
            # The in-file count matches the baseline. The directory hit must still be reported.
            findings = scan.strip_findings(root, baseline={rel: {cls: 1}})
        self.assertEqual(findings, [f"skills/{word} (directory name carries a banned name)"])

    def test_banned_name_in_a_file_name_is_a_finding(self):
        scan = _scan()
        word = _insurer_word()
        cls = scan.name_class(word)
        rel = f"corpus/{word}.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, rel, f"Sheet cites {word} once.\n")
            findings = scan.strip_findings(root, baseline={rel: {cls: 1}})
        self.assertEqual(findings, [f"{rel} (file name carries a banned name)"])

    def test_tag_in_a_file_name_is_a_finding(self):
        scan = _scan()
        rel = f"corpus/{QA_EX}.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, rel, "Clean line.\n")
            findings = scan.strip_findings(root, baseline={})
        self.assertEqual(findings, [f"{rel} (file name carries a QA tag)"])

    def test_tag_in_a_directory_name_is_a_finding(self):
        scan = _scan()
        rel = f"skills/{BATCH_DIR}/SKILL.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, rel, "Clean line.\n")
            findings = scan.strip_findings(root, baseline={})
        self.assertEqual(findings, [f"skills/{BATCH_DIR} (directory name carries a batch or round tag)"])

    def test_scope_names_in_a_path_are_findings_and_canada_names_are_not(self):
        scan = _scan()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, f"skills/{OOS_A}/SKILL.md")
            _write(root, f"skills/{OOS_B}/SKILL.md")
            _write(root, f"skills/{OOS_C}/SKILL.md")
            _write(root, "corpus/canada/notes.md")
            _write(root, "corpus/fp/canadian.md")
            _write(root, "corpus/fp/canada-delta.md")
            _write(root, "skills/ok-skill/SKILL.md")
            findings = scan.path_findings(root)
        text = "\n".join(findings)
        self.assertIn(OOS_A, text)
        self.assertIn(OOS_B, text)
        self.assertIn(OOS_C, text)
        # Canada is in scope through a skill's Country gate. The builder packs these under their own names.
        self.assertNotIn("canad", text)
        self.assertNotIn("ok-skill", text)


@unittest.skipUnless(SCRIPTS.is_dir(), "scripts/ is not in this tree")
class BuilderGuardTests(unittest.TestCase):
    def test_zip_leaves_out_the_held_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            out = Path(tmp) / "out"
            result = _build(source, out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(out / "fp-fa-content-v9.9.9.zip") as archive:
                names = archive.namelist()
        self.assertIn("calcs/fp/formulas.py", names)
        self.assertFalse([n for n in names if n.startswith(DRAFT_DIR + "/")], names)

    def test_out_of_scope_slug_fails_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, f"skills/{OOS_D}/SKILL.md")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(OOS_D, result.stderr)
            self.assertFalse((Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip").exists())

    def test_a_canada_named_path_ships_under_its_own_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, "corpus/fp/canada.md")
            _write(source, "corpus/canadian/notes.md")
            out = Path(tmp) / "out"
            result = _build(source, out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("canad", result.stderr, "nothing Canada-named is stripped or reported")
            with zipfile.ZipFile(out / "fp-fa-content-v9.9.9.zip") as archive:
                names = archive.namelist()
        self.assertIn("corpus/fp/canada.md", names)
        self.assertIn("corpus/canadian/notes.md", names)

    def test_a_canada_delta_file_with_a_longer_name_still_ships(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, "corpus/fp/canada-delta.md")
            out = Path(tmp) / "out"
            result = _build(source, out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(out / "fp-fa-content-v9.9.9.zip") as archive:
                self.assertIn("corpus/fp/canada-delta.md", archive.namelist())

    def test_a_qa_tag_fails_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, "skills/demo-skill/extra.md", f"Checked ({QA_EX} F-2).\n")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("extra.md:1", result.stderr)

    def test_banned_name_in_a_directory_fails_the_build(self):
        word = _insurer_word()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, f"skills/{word}/SKILL.md")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"skills/{word} (directory name carries a banned name)", result.stderr)
            self.assertFalse((Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip").exists())

    def test_banned_name_in_a_file_name_fails_the_build(self):
        word = _insurer_word()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, f"corpus/{word}.md")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"corpus/{word}.md (file name carries a banned name)", result.stderr)
            self.assertFalse((Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip").exists())

    def test_tag_in_a_file_name_fails_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, f"corpus/{QA_EX}.md")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"corpus/{QA_EX}.md (file name carries a QA tag)", result.stderr)
            self.assertFalse((Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip").exists())

    def test_tag_in_a_directory_name_fails_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            _mini_pack(source)
            _write(source, f"skills/{BATCH_DIR}/SKILL.md")
            result = _build(source, Path(tmp) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"skills/{BATCH_DIR} (directory name carries a batch or round tag)", result.stderr)
            self.assertFalse((Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip").exists())

    def test_the_repository_builds_without_the_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _build(ROOT, Path(tmp) / "out")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(Path(tmp) / "out" / "fp-fa-content-v9.9.9.zip") as archive:
                names = archive.namelist()
        self.assertIn("calcs/fp/formulas.py", names)
        self.assertFalse([n for n in names if n.startswith(DRAFT_DIR + "/")])
        self.assertIn("calcs/fp/test_draft_held.py", names)


if __name__ == "__main__":
    unittest.main()
