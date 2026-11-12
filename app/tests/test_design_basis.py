"""The Design Basis and Open Questions export reads the project record and nothing else."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402



def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-basis-")) / "fpfa.db")


def _docx_text(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    parts = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def _seed_sample(record, project_id="job1"):
    """The sample zone's tool plan plus the rows a team would write, as the known answer expects."""
    from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
    from fpfa.workflow import run_di_zone

    record.ensure_project(project_id, "Sample data hall DI zone")
    run = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id=project_id)
    record.import_project({"id": project_id, "name": "Sample data hall DI zone", "basis": dict(EXAMPLE_BASIS)})
    calc_ids = {row["tool"]: row["id"] for row in record.calcs(project_id)}
    cite = record.record_evidence(
        project_id, document="NFPA 13", edition="2025", section="8.3.2.3.1.1",
        note="Double-interlock at or under 500 gal needs no specific delivery time", status="held",
        agent="fp-sprinkler",
    )
    record.set_agent(project_id, name="FP specialist", role_slug="fp-sprinkler", status="done")
    record.set_agent(project_id, name="FA specialist", role_slug="fa-releasing", status="done")
    record.record_finding(
        project_id, agent="fp-sprinkler",
        text="Zone total 281.3 gal is inside the 500 gal cap; the FM 30 s screen still misses at 38.1 s.",
        label="calculated", supports=[calc_ids["zone_trapped_volume"], calc_ids["di_trip_to_water"], cite["id"]],
    )
    record.record_finding(
        project_id, agent="fa-releasing",
        text=("Solenoid opens on the detection leg (one detection zone, or a manual station in its place) "
              "AND P, the pressure drop from sprinkler operation, and not isolated. "
              "Low air is supervisory only."),
        label="calculated", supports=[calc_ids["releasing_truth_table"]],
    )
    record.record_decision(
        project_id, text="Trim family El/El, provisional; no catalog number elected.",
        decided_by="fp-sprinkler", label="use best judgment", basis=calc_ids["elect_di_trim"],
    )
    record.open_question(project_id, raised_by="fp-sprinkler", text="Trim volume from the elected valve data sheet?")
    record.open_question(project_id, raised_by="lead", text="Enforced NFPA 13 edition for this AHJ?")
    answered = record.open_question(project_id, raised_by="fa-releasing", text="Manual station on this zone?")
    record.answer_question(project_id, answered["id"], answer="Yes, one station at the riser.", by="owner")
    handoff = record.create_handoff(
        project_id, from_agent="fp-sprinkler", to_agent="fa-releasing",
        brief="Trim family El/El with a 15 psi low-air supervisory switch",
        payload={"family": "El/El", "low_air_supervisory_psi": 15},
    )
    record.set_handoff(project_id, handoff["id"], status="delivered", by="lead")
    record.set_handoff(project_id, handoff["id"], status="returned", result="Releasing boolean written")
    return run, calc_ids


class DesignBasisExportTests(unittest.TestCase):
    def test_export_shows_every_section_from_the_record(self):
        from fpfa.checker import NOT_STANDARD, TIER_TITLE
        from fpfa.design_basis_docx import (DESIGN_BASIS_TITLE, DRAFT_LINE, NO_CHECK_LINE, SCREEN_LINE,
                                            write_design_basis)

        record = _record()
        run, calc_ids = _seed_sample(record)
        snapshot = record.snapshot("job1")
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-out-")) / "basis.docx"
        write_design_basis(out, {"name": "Sample data hall DI zone"}, snapshot)
        text = _docx_text(out)
        self.assertIn(DESIGN_BASIS_TITLE, text)
        self.assertIn("Sample data hall DI zone", text)
        self.assertIn(SCREEN_LINE, text)
        self.assertIn("use best judgment", text)
        # The opening says what kind of document this is and how far each statement was taken.
        self.assertIn(DRAFT_LINE, text)
        self.assertIn(NOT_STANDARD, text)
        self.assertIn("How far each statement was taken", text)
        self.assertIn(f"{TIER_TITLE['stated']} | 2 | A specialist recorded these. No trace check has judged them.", text)
        self.assertIn(f"{TIER_TITLE['source']} | 0 |", text)
        # 1. the project inputs, with the label and who supplied each
        for needle in ("ahj | Local fire marshal (sample)", "nfpa_13 | 2025 | CODE", "insurer | FM | OWNER"):
            self.assertIn(needle, text)
        # 9. cites, with who recorded each
        self.assertIn("NFPA 13 | 2025 | 8.3.2.3.1.1", text)
        self.assertIn("| held | fp-sprinkler |", text)
        # 2. elections read from the calc records and the decision
        self.assertIn("Trim family | El/El (provisional)", text)
        # The second leg is P. The kernel's deprecated low_air alias is never printed.
        self.assertIn(
            "Releasing logic | solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated", text
        )
        self.assertNotIn("AND low_air", text)
        self.assertIn("p_second_leg is P, the pressure drop from sprinkler operation", text)
        self.assertIn("Low air is supervisory only (PSL-SUP) and is never a release input.", text)
        self.assertIn("Design Hazen-Williams C | 100", text)
        self.assertIn("Trim family El/El, provisional; no catalog number elected.", text)
        self.assertIn("fp-sprinkler (use best judgment)", text)
        # 3. calc records: all eight tools, each with its id
        for tool, calc_id in calc_ids.items():
            self.assertIn(tool, text)
            self.assertIn(calc_id, text)
        # 4. findings grouped by how far each was taken, each with its author and what it rests on
        self.assertIn(f"{TIER_TITLE['stated']} (2)", text)
        self.assertIn(f"{TIER_TITLE['open']} (0)", text)
        self.assertIn("the FM 30 s screen still misses at 38.1 s. | calculated | fp-sprinkler | "
                      f"zone_trapped_volume [{calc_ids['zone_trapped_volume']}]; di_trip_to_water [{calc_ids['di_trip_to_water']}]; "
                      "NFPA 13-2025 §8.3.2.3.1.1 [", text)
        self.assertIn("| calculated | fa-releasing | releasing_truth_table [", text)
        self.assertIn("| No trace check has judged it. |", text)
        # 5 and 10. nobody reviewed anything and no checker ran, and the document says so
        self.assertIn("No contributor has reviewed another's finding on this record.", text)
        self.assertEqual(text.count(NO_CHECK_LINE), 2)
        # 6. assumptions from the calc flags and the screen limit
        self.assertIn("ASSUMED trim volume 5 gal", text)
        self.assertIn("ASSUMED from time basis FM", text)
        # 7. open and answered questions
        self.assertIn("Trim volume from the elected valve data sheet? (raised by fp-sprinkler)", text)
        self.assertIn("Enforced NFPA 13 edition for this AHJ? (raised by lead)", text)
        self.assertIn("For the engineer of record, the owner, or the authority:", text)
        self.assertNotIn("The team needs these from the designer", text)
        self.assertIn("Manual station on this zone? Answer: Yes, one station at the riser. (answered by owner)", text)
        # 8. what passed between the agents, with what came back
        self.assertIn(
            "handoff | fp-sprinkler | fa-releasing | Trim family El/El with a 15 psi low-air supervisory switch | "
            "Releasing boolean written | returned", text
        )
        # 11. nothing changed on this record
        self.assertIn("Nothing on this record was changed, replaced, or withdrawn.", text)
        # contributors line
        self.assertIn("FP specialist (fp-sprinkler, done)", text)

    def test_export_carries_the_known_answer_figures_for_dh1(self):
        """Section 2 of docs/known-answer-dh1.md, as the tool plan alone produces it."""
        from fpfa.design_basis_docx import write_design_basis

        record = _record()
        _seed_sample(record)
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-out-")) / "basis.docx"
        write_design_basis(out, {"name": "DH-1"}, record.snapshot("job1"))
        text = _docx_text(out)
        for needle in (
            "Pipe 276.3 gal (calculated)",
            "Zone total 281.3 gal (calculated)",
            "5.0 gal trim ASSUMED",
            "Exemption threshold: the 500 gal exemption threshold (NFPA 13-2025 §8.3.2.3.1.1); size exemption on the "
            "zone total of 281.3 gal: yes",
            "what in that total is ASSUMED is on the zone_trapped_volume record",
            "Fill 28.1 s, t_total 38.1 s, margin -8.1 s; the zone-total screen does not pass",
            "About 200.0 gal meets the limit",
            "Screen limit 30.0 s",
            "Family El/El, status provisional, prime held by nc_solenoid, supervisory 15 psi, medium nitrogen",
            "6 true rows of 32",
            "FM basis: no cross-zone",
            "Design Hazen-Williams C 100",
            "multiplies friction by about 0.714",
            "Fill 3.41 scfm gauge basis, 4.67 scfm absolute basis",
            "Design area 1950 ft²",
            "Sprinklers 390.0 gpm",
            "Hose 250.0 gpm",
            "Total demand 640.0 gpm (calculated)",
            "Duration volume 38,400 gal over 60 min",
            "Duration 60 min (table range 60 to 90), combined hose 250 gpm",
            "NFPA 13-2025 s8.3.2.3.1.1",
        ):
            self.assertIn(needle, text, needle)

    def test_checker_rows_are_shown_when_a_claim_check_exists(self):
        from fpfa.design_basis_docx import NO_CHECK_LINE, write_design_basis

        record = _record()
        _seed_sample(record)
        check = {
            "all_supported": False,
            "status_line": "Export of Section 21 13 19 is blocked until every claim is Supported. Open claims: 2.",
            "rows": [
                {"n": 1, "verdict": "Supported", "cite": "PACKAGE ASSERTION. Tool-plan figures: 281.3"},
                {"n": 2, "verdict": "Source not found", "cite": "NOT PULLED"},
            ],
        }
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-out-")) / "basis.docx"
        write_design_basis(out, {"name": "DH-1"}, record.snapshot("job1"), claim_check=check)
        text = _docx_text(out)
        self.assertNotIn(NO_CHECK_LINE, text)
        self.assertIn("Export of Section 21 13 19 is blocked until every claim is Supported. Open claims: 2.", text)
        self.assertIn("1 | Supported | PACKAGE ASSERTION. Tool-plan figures: 281.3", text)
        self.assertIn("2 | Source not found | NOT PULLED", text)
        self.assertIn("Not every finding is supported by the rows it cites.", text)
        self.assertIn("It is not cleared for issue.", text)

    def test_empty_record_exports_a_document_that_says_so(self):
        from fpfa.design_basis_docx import write_design_basis

        record = _record()
        record.ensure_project("empty", "Nothing yet")
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-out-")) / "basis.docx"
        write_design_basis(out, {"name": "Nothing yet"}, record.snapshot("empty"))
        text = _docx_text(out)
        for needle in (
            "No project inputs are on the record yet.",
            "No elections are on the record yet.",
            "No calculation has been recorded on this job.",
            "No findings are on the record yet.",
            "No contributor has reviewed another's finding on this record.",
            "No ASSUMED rows are on the record.",
            "No open questions are on the record.",
            "No exchanges between agents are on the record.",
            "No cites are on the record.",
            "Nothing on this record was changed, replaced, or withdrawn.",
        ):
            self.assertIn(needle, text)

    def test_replayed_calc_shows_its_replay_count_and_nothing_from_the_thread(self):
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("job1", "Sample")
        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        project = {"name": "Sample", "chat": [{"role": "user", "text": "SECRET-THREAD-TEXT"}]}
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-out-")) / "basis.docx"
        write_design_basis(out, project, record.snapshot("job1"))
        text = _docx_text(out)
        self.assertIn("zone_trapped_volume | tool-plan", text)
        self.assertIn("| 1 | Pipe 276.3 gal", text)
        self.assertNotIn("SECRET-THREAD-TEXT", text)

    def test_unknown_tool_falls_back_to_compact_inputs_and_outputs(self):
        from fpfa.design_basis_docx import key_figures

        line = key_figures("fp_calc", {"op": "hw", "inputs": {"q_gpm": 500}}, {"psi_per_ft": 0.1234})
        self.assertIn('"op": "hw"', line)
        self.assertIn("0.1234", line)
        broken = key_figures("zone_trapped_volume", {}, {"pipe_gal": "not a number"})
        self.assertIn("Outputs", broken)


class DesignBasisWindowTests(unittest.TestCase):
    """The menu export writes the document for the open job. Needs a display."""

    def _app(self):
        import os
        data = Path(tempfile.mkdtemp(prefix="fpfa-basis-ui-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"

        from fpfa.paths import write_config
        
        write_config({"key_backend": "file"})
        root = Loop()
        self.addCleanup(root.destroy)
        app = root.open_desk()
        root.update()
        return app

    def test_sample_run_then_export_from_the_menu_path(self):
        from fpfa.design_basis_docx import DESIGN_BASIS_TITLE

        app = self._app()
        self.assertEqual(app.design_basis_ready(), "Open a job first.")
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        self.assertEqual(app.design_basis_ready(), "")
        out = Path(tempfile.mkdtemp(prefix="fpfa-basis-ui-out-")) / "basis.docx"
        written = app.export_design_basis_to(out)
        text = _docx_text(written)
        self.assertIn(DESIGN_BASIS_TITLE, text)
        self.assertIn("Sample data hall DI zone", text)
        self.assertIn("Zone total 281.3 gal (calculated)", text)
        self.assertIn("zone_trapped_volume | tool-plan", text)
        self.assertIn("insurer | FM | OWNER | SAMPLE data", text)
        # The zone inputs are in the document with who supplied them, and the plan's calcs follow them.
        self.assertIn("q_fill_gpm | 600 gpm | GIVEN | SAMPLE data", text)
        self.assertIn("| follows the project inputs |", text)
        # The ⋯ menu's row names the document from the state the page reads.
        self.assertEqual(app.snapshot()["app"]["design_basis_title"], DESIGN_BASIS_TITLE)

    def test_a_new_empty_job_is_not_ready(self):
        app = self._app()
        app.new_job()
        app._ensure_project()
        self.assertIn("Nothing is on this job's record yet", app.design_basis_ready())


if __name__ == "__main__":
    unittest.main()
