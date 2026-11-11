"""The releasing statement: release is the detection leg AND P. Low air is supervisory only.

docs/releasing-basis.md is the basis. These tests hold the app to it three ways. The logic
is evaluated row by row, so a relabel cannot hide a change in behaviour. Everything the app
writes or sends to a model is read back and scanned. And the prose the pack lint does not
reach (docs/, the README, the app's own source strings) is scanned with the same detector.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DEPRECATED_BOOLEAN = "AND low" + "_air"


def _pack_lint():
    """The pack's own lint module, loaded by path."""
    path = REPO / "calcs" / "fp" / "test_pack_content_lowair.py"
    spec = importlib.util.spec_from_file_location("pack_lowair_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _detector():
    """The pack's own detector, loaded by path so the app suite and the pack suite cannot drift."""
    return _pack_lint().low_air_release_hits


# Where the app's own detector begins in fpfa/releasing.py. Below it the file is the forbidden phrasings
# themselves, written as patterns.
DETECTOR_MARK = "# -- the wording the releasing rule forbids"


def _docx_text(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    parts = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def _sample_run():
    from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
    from fpfa.workflow import run_di_zone

    return run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)


class TruthTableLogicTests(unittest.TestCase):
    """The behaviour, row by row, as a model reads it. Not a string comparison."""

    def setUp(self):
        from fpfa.calc_tools import ToolSession

        self.table = ToolSession(REPO, agent="lead").execute(
            "releasing_truth_table", {"manual_station": True, "insurer": "FM"}
        )
        self.rows = self.table["rows"]

    def _solenoid(self, **want) -> set[bool]:
        return {row["solenoid"] for row in self.rows if all(row[key] == value for key, value in want.items())}

    def test_every_row_is_the_detection_leg_and_p_and_not_isolated(self):
        self.assertEqual(len(self.rows), 32)
        for row in self.rows:
            expected = bool((row["detection"] or row["manual"]) and row["p_second_leg"] and not row["isolated"])
            self.assertEqual(row["solenoid"], expected, row)
        self.assertEqual(sum(1 for row in self.rows if row["solenoid"]), 6)
        self.assertEqual(self.table["solenoid_true_count"], 6)

    def test_p_alone_does_not_release(self):
        """A pressure drop with no detection: a leak, a compressor fault, a broken pipe."""
        self.assertEqual(self._solenoid(detection=False, manual=False, p_second_leg=True), {False})

    def test_detection_alone_does_not_release(self):
        self.assertEqual(self._solenoid(detection=True, p_second_leg=False), {False})

    def test_a_manual_station_stands_in_for_detection_and_still_needs_p(self):
        self.assertEqual(self._solenoid(detection=False, manual=True, p_second_leg=False), {False})
        self.assertEqual(self._solenoid(detection=False, manual=True, p_second_leg=True, isolated=False), {True})

    def test_an_isolated_zone_never_releases(self):
        self.assertEqual(self._solenoid(isolated=True), {False})

    def test_a_second_smoke_zone_changes_nothing(self):
        for row in self.rows:
            twin = next(
                other for other in self.rows
                if other["second_smoke"] != row["second_smoke"]
                and all(other[key] == row[key] for key in ("detection", "manual", "p_second_leg", "isolated"))
            )
            self.assertEqual(twin["solenoid"], row["solenoid"])

    def test_without_a_manual_station_only_detection_arms_the_leg(self):
        from fpfa.calc_tools import ToolSession

        table = ToolSession(REPO, agent="lead").execute("releasing_truth_table", {"manual_station": False})
        fired = [row for row in table["rows"] if row["solenoid"]]
        self.assertTrue(fired)
        self.assertTrue(all(row["detection"] and row["p_second_leg"] and not row["isolated"] for row in fired))
        self.assertEqual(
            {row["solenoid"] for row in table["rows"] if row["manual"] and not row["detection"]}, {False}
        )


class ModelViewTests(unittest.TestCase):
    """What a model is told. The kernel's deprecated alias never reaches it."""

    def test_the_tool_result_a_model_reads_names_p_and_has_no_deprecated_key(self):
        from fpfa.calc_tools import ToolSession

        shown = ToolSession(REPO, agent="fa-releasing").execute("releasing_truth_table", {})
        self.assertEqual(
            shown["boolean_p"], "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated"
        )
        for key in ("boolean", "deprecated", "low_air_note"):
            self.assertNotIn(key, shown)
        for name in ("rows", "rows_without_second_smoke"):
            for row in shown[name]:
                self.assertIn("p_second_leg", row)
                self.assertNotIn("low_air", row)
        self.assertEqual(shown["low_air"], "Low air is supervisory only (PSL-SUP) and is never a release input.")
        self.assertNotIn(DEPRECATED_BOOLEAN, str(shown))
        self.assertEqual(_detector()(str(shown)), [])

    def test_the_recorded_result_a_model_reads_is_the_same_view_with_its_record_id(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.record import Record

        record = Record(Path(tempfile.mkdtemp(prefix="fpfa-releasing-")) / "fpfa.db")
        record.ensure_project("job1")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        first = session.execute("releasing_truth_table", {})
        replay = session.execute("releasing_truth_table", {})
        for shown in (first, replay):
            self.assertIn("record_id", shown)
            self.assertNotIn("boolean", shown)
            self.assertNotIn(DEPRECATED_BOOLEAN, str(shown))
        # The record keeps the kernel's full output; only the view leaves the alias out.
        stored = record.calcs("job1")[0]["outputs"]
        self.assertIn("boolean_p", stored)
        self.assertEqual(record.calcs("job1")[0]["replay_count"], 1)

    def test_the_fixed_tool_plan_still_gets_the_kernel_output_unchanged(self):
        from fpfa.calc_tools import ToolSession

        raw = ToolSession(REPO, agent="tool-plan").execute("releasing_truth_table", {})
        bare = ToolSession(REPO).execute("releasing_truth_table", {})
        self.assertEqual(raw, bare)
        self.assertIn("boolean_p", raw)

    def test_the_tool_description_states_the_rule(self):
        from fpfa.calc_tools import SCHEMAS

        description = next(item["description"] for item in SCHEMAS if item["name"] == "releasing_truth_table")
        self.assertIn("AND P AND NOT isolated", description)
        self.assertIn("Low air is supervisory only and is not a release input", description)
        self.assertIn("boolean_p", description)
        self.assertEqual(_detector()(description), [])

    def test_an_older_pack_or_saved_run_is_printed_with_the_leg_named_p(self):
        """A result from before the relabel carries only the deprecated names."""
        from fpfa.releasing import reader_view, releasing_logic, releasing_sentence, second_leg_value

        old = {
            "boolean": "solenoid = (detection_leg OR manual_release) AND low" + "_air AND NOT isolated",
            "rows": [{"detection": True, "manual": False, "low" + "_air": True, "isolated": False, "solenoid": True}],
            "rows_without_second_smoke": [],
            "row_count": 32, "solenoid_true_count": 6,
        }
        logic = releasing_logic(old)
        self.assertEqual(logic["expression"], "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated")
        self.assertIn("pressure drop from sprinkler operation", logic["second_leg"])
        self.assertTrue(second_leg_value(old["rows"][0]))
        shown = reader_view("releasing_truth_table", old)
        self.assertNotIn("boolean", shown)
        self.assertEqual(list(shown["rows"][0]), ["detection", "manual", "p_second_leg", "isolated", "solenoid"])
        sentence = releasing_sentence(old)
        self.assertNotIn(DEPRECATED_BOOLEAN, sentence)
        self.assertEqual(_detector()(sentence), [])
        # Another tool's output is never touched.
        self.assertEqual(reader_view("hose_duration", {"boolean": "x"}), {"boolean": "x"})


class WrittenOutputTests(unittest.TestCase):
    """What the app writes for a designer: the narrative, the Results tab, and both documents."""

    def test_the_tool_plan_narrative_states_d_and_p(self):
        run = _sample_run()
        line = next(text for text in run["narrative"].splitlines() if text.startswith("Releasing"))
        self.assertIn("solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated", line)
        self.assertIn("pressure drop from sprinkler operation", line)
        self.assertIn("Low air is supervisory only (PSL-SUP) and is never a release input.", line)
        self.assertNotIn(DEPRECATED_BOOLEAN, run["narrative"])
        self.assertEqual(_detector()(run["narrative"]), [])

    def test_another_trim_family_is_told_the_table_is_a_reference(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        run = run_di_zone(REPO, dict(EXAMPLE_DI, prime_held_by="pneumatic_actuator"), EXAMPLE_BASIS)
        self.assertEqual(run["tools"]["elect_di_trim"]["family"], "El/Pn")
        line = next(text for text in run["narrative"].splitlines() if text.startswith("Releasing"))
        self.assertIn("the elected trim family is El/Pn", line)
        self.assertIn("electric/electric reference, not this valve's logic", line)
        self.assertIn("PA-REL", line)

    def test_the_results_tab_transcript_leaves_the_alias_out(self):
        from fpfa.workflow import format_transcript

        text = format_transcript(_sample_run()["transcript"])
        self.assertIn("p_second_leg", text)
        self.assertNotIn(DEPRECATED_BOOLEAN, text)
        self.assertNotIn('"low' + '_air":', text)

    def test_the_section_export_has_a_p_column_and_no_low_air_column(self):
        from fpfa.spec_docx import write_docx

        out = Path(tempfile.mkdtemp(prefix="fpfa-releasing-")) / "section.docx"
        write_docx(out, {"name": "Sample"}, _sample_run())
        text = _docx_text(out)
        self.assertIn("Detection | Manual | P (second leg) | Isolated | Solenoid", text)
        self.assertNotIn("| Low air |", text)
        self.assertIn("solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated", text)
        self.assertNotIn(DEPRECATED_BOOLEAN, text)
        self.assertEqual(_detector()(text), [])
        # The eight rows without the second-smoke duplicate, three of them true.
        rows = [line for line in text.splitlines() if re.fullmatch(r"(Yes|No)( \| (Yes|No)){4}", line)]
        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(1 for line in rows if line.endswith("| Yes")), 3)

    def test_a_run_saved_before_the_relabel_exports_with_the_leg_named_p(self):
        """An old job on disk: its stored truth table has only the deprecated names."""
        import copy

        from fpfa.spec_docx import write_docx

        run = copy.deepcopy(_sample_run())
        truth = run["tools"]["releasing_truth_table"]
        for key in ("boolean_p", "second_leg", "low_air_note", "deprecated"):
            truth.pop(key, None)
        for name in ("rows", "rows_without_second_smoke"):
            for row in truth[name]:
                row.pop("p_second_leg", None)
        out = Path(tempfile.mkdtemp(prefix="fpfa-releasing-")) / "old.docx"
        write_docx(out, {"name": "Old job"}, run)
        text = _docx_text(out)
        self.assertIn("AND p_second_leg AND NOT isolated", text)
        self.assertNotIn(DEPRECATED_BOOLEAN, text)
        self.assertIn("Detection | Manual | P (second leg) | Isolated | Solenoid", text)

    def test_the_design_basis_export_states_d_and_p(self):
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.record import Record
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        record = Record(Path(tempfile.mkdtemp(prefix="fpfa-releasing-")) / "fpfa.db")
        record.ensure_project("job1", "Sample")
        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        out = Path(tempfile.mkdtemp(prefix="fpfa-releasing-")) / "basis.docx"
        write_design_basis(out, {"name": "Sample"}, record.snapshot("job1"))
        text = _docx_text(out)
        self.assertIn("AND p_second_leg AND NOT isolated", text)
        self.assertNotIn(DEPRECATED_BOOLEAN, text)
        self.assertEqual(_detector()(text), [])


class ProseOutsideThePackTests(unittest.TestCase):
    """docs/, the README, and the app's own strings. The pack lint covers the pack's folders."""

    def test_docs_and_readme_never_name_low_air_as_a_release_input(self):
        detect = _detector()
        files = sorted((REPO / "docs").rglob("*.md")) + [REPO / "README.md", REPO / "CLAUDE.md"]
        self.assertTrue(any(path.name == "known-answer-dh1.md" for path in files))
        # The one place a doc carries the wrong wording on purpose: the claim the owner is asked to plant, in
        # step 8 of the live evaluation, so the trace check can be seen to reject it. It has to be there, once.
        planted = "the valve releases on detection and low" + " air, citing the releasing truth table"
        found = []
        seen_planted = 0
        for path in files:
            for line_no, sentence in detect(path.read_text(encoding="utf-8")):
                if path.name == "live-evaluation.md" and planted in sentence:
                    seen_planted += 1
                    continue
                found.append(f"{path.relative_to(REPO)}:{line_no}: {sentence[:160]}")
        self.assertEqual(found, [], "low air is supervisory only; release is D and P:\n" + "\n".join(found))
        self.assertEqual(seen_planted, 1, "the guide's planted claim is one the detector catches")

    def test_the_app_source_and_the_page_never_name_low_air_as_a_release_input(self):
        detect = _detector()
        files = sorted((APP_DIR / "fpfa").glob("*.py")) + sorted((APP_DIR / "fpfa" / "web").glob("*.py"))
        files += sorted((APP_DIR / "frontend" / "src").rglob("*.ts")) + sorted((APP_DIR / "frontend" / "src").rglob("*.tsx"))
        found = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            if path.name == "releasing.py":
                self.assertIn(DETECTOR_MARK, text)
                text = text.split(DETECTOR_MARK)[0]
            for line_no, sentence in detect(text):
                found.append(f"{path.relative_to(REPO)}:{line_no}: {sentence[:160]}")
        self.assertEqual(found, [], "\n".join(found))

    def test_the_known_answer_states_the_reviewed_logic(self):
        text = (REPO / "docs" / "known-answer-dh1.md").read_text(encoding="utf-8")
        self.assertIn("AND p_second_leg AND NOT isolated", text)
        self.assertIn("Low air is supervisory only (PSL-SUP) and is never a release input.", text)
        self.assertIn("docs/releasing-basis.md", text)
        self.assertNotIn(DEPRECATED_BOOLEAN, text)

    def test_the_basis_note_says_what_is_held_and_what_is_not(self):
        text = (REPO / "docs" / "releasing-basis.md").read_text(encoding="utf-8")
        for needle in ("PSL-REL", "PA-REL", "PSL-SUP", "NOT PULLED",
                       "**Status: UNRESOLVED as engineering. Internally consistent as software.**",
                       # What a file here says, what a reviewer reported, and what was read in the standard, kept apart.
                       "### 3a. Inspected in this repository", "### 3b. Reported by reviewers, not inspected here",
                       "### 3c. Opened and read in the primary text", "**None.** No standard, data sheet, or manufacturer document was opened",
                       "**That was a reconciliation for internal consistency.**",
                       "## 8. The acceptance gate", "**A qualified engineer's review**"):
            self.assertIn(needle, text)
        # The page does not call the rule verified, reviewed, or accepted anywhere.
        self.assertNotRegex(text, r"(?i)\bhas been (verified|reviewed by a qualified|accepted)\b")

    def test_the_two_detectors_agree_sentence_for_sentence(self):
        """The pack's lint and the application's detector are the same rules. Neither may drift from the other."""
        from fpfa.releasing import release_wording_hits

        lint = _pack_lint()
        cases = []
        for name in ("test_flags_low_air_as_a_release_leg", "test_allows_the_supervisory_wording"):
            source = Path(lint.__file__).read_text(encoding="utf-8")
            body = source[source.index(f"def {name}"):]
            body = body[: body.index("self.assert")]
            cases += re.findall(r'^\s+"(.+)",$', body, flags=re.M)
        self.assertGreater(len(cases), 40)
        for sentence in cases:
            self.assertEqual(bool(release_wording_hits(sentence)), bool(lint.low_air_release_hits(sentence)), sentence)
        for folder in ("corpus", "specs", "skills", "roles", "modes", "docs"):
            for path in sorted((REPO / folder).rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(release_wording_hits(text), lint.low_air_release_hits(text), str(path))

    def test_only_the_releasing_module_reads_the_deprecated_names(self):
        """One place in the app knows the kernel's alias. Nothing else may read it."""
        offenders = []
        for path in sorted((APP_DIR / "fpfa").rglob("*.py")):
            if path.name == "releasing.py":
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"""\[["']low_air["']\]|\[["']boolean["']\]|\.get\(["'](low_air|boolean)["']""", text):
                offenders.append(path.name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
