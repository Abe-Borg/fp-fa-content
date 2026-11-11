"""The project record: a SQLite store that calc tools write to automatically.

Every test uses its own database file. No API call is made.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def _record():
    from fpfa.record import Record

    folder = tempfile.mkdtemp(prefix="fpfa-record-")
    return Record(Path(folder) / "fpfa.db")


class RecordStoreTests(unittest.TestCase):
    def test_default_path_is_in_the_data_directory(self):
        folder = tempfile.mkdtemp(prefix="fpfa-record-data-")
        os.environ["FPFA_DATA_DIR"] = folder
        from fpfa.record import Record, default_path

        self.assertEqual(default_path(), Path(folder) / "fpfa.db")
        Record()
        self.assertTrue((Path(folder) / "fpfa.db").is_file())

    def test_fact_requires_one_of_the_labels_and_keeps_the_pack_spelling(self):
        from fpfa.record import RecordError

        record = _record()
        record.ensure_project("p1", "Job one")
        row = record.record_fact("p1", kind="basis", key="nfpa_13", value="2025", label="code")
        self.assertEqual(row["label"], "CODE")
        row = record.record_fact("p1", kind="assumption", key="trim", value="5 gal", label="assumed")
        self.assertEqual(row["label"], "ASSUMED")
        with self.assertRaises(RecordError):
            record.record_fact("p1", kind="basis", key="x", value="y", label="calculated-ish")
        with self.assertRaises(RecordError):
            record.record_fact("p1", kind="basis", key="", value="y", label="CODE")
        self.assertEqual([row["key"] for row in record.facts("p1")], ["nfpa_13", "trim"])
        self.assertEqual([row["kind"] for row in record.events("p1")], ["fact", "fact"])

    def test_calc_record_dedupes_identical_inputs_and_counts_replays(self):
        record = _record()
        record.ensure_project("p1")
        first = record.record_calc("p1", tool="hose_duration", inputs={"hazard": "ordinary", "supervised": True},
                                   outputs={"duration_min": 60}, agent="tool-plan", pack_version="source checkout")
        self.assertFalse(first["replayed"])
        again = record.record_calc("p1", tool="hose_duration", inputs={"supervised": True, "hazard": "ordinary"},
                                   outputs={"duration_min": 60}, agent="lead")
        self.assertTrue(again["replayed"])
        self.assertEqual(again["id"], first["id"])
        self.assertEqual(again["replay_count"], 1)
        rows = record.calcs("p1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["outputs"], {"duration_min": 60})
        self.assertEqual(rows[0]["pack_version"], "source checkout")
        # A different project keeps its own row.
        record.ensure_project("p2")
        other = record.record_calc("p2", tool="hose_duration", inputs={"hazard": "ordinary", "supervised": True},
                                   outputs={"duration_min": 60})
        self.assertFalse(other["replayed"])
        self.assertEqual([row["kind"] for row in record.events("p1")], ["calc", "calc_replay"])

    def test_handoff_lifecycle_and_pending_filter(self):
        from fpfa.record import RecordError

        record = _record()
        record.ensure_project("p1")
        one = record.create_handoff("p1", from_agent="fp-sprinkler", to_agent="fa-releasing",
                                    brief="Trim family El/El, low air 15 psi", payload={"family": "El/El"})
        two = record.create_handoff("p1", from_agent="lead", to_agent="fp-sprinkler", brief="Size the zone")
        self.assertEqual([row["id"] for row in record.pending_handoffs("p1")], [one["id"], two["id"]])
        self.assertEqual([row["id"] for row in record.pending_handoffs("p1", "fa-releasing")], [one["id"]])
        delivered = record.set_handoff("p1", one["id"], status="delivered", by="lead")
        self.assertEqual(delivered["status"], "delivered")
        self.assertIsNotNone(delivered["delivered"])
        returned = record.set_handoff("p1", one["id"], status="returned", result={"boolean": "ok"})
        self.assertEqual(returned["status"], "returned")
        self.assertIsNotNone(returned["returned"])
        self.assertEqual(record.handoffs("p1")[0]["payload"], {"family": "El/El"})
        self.assertEqual([row["id"] for row in record.pending_handoffs("p1")], [two["id"]])
        with self.assertRaises(RecordError):
            record.set_handoff("p1", "nope", status="delivered")
        with self.assertRaises(RecordError):
            record.set_handoff("p1", two["id"], status="lost")

    def test_questions_decisions_evidence_tasks_and_agents(self):
        from fpfa.record import RecordError

        record = _record()
        record.ensure_project("p1")
        question = record.open_question("p1", raised_by="fp-sprinkler", text="Trim volume from the valve sheet?")
        self.assertEqual(record.questions("p1", "open")[0]["id"], question["id"])
        answered = record.answer_question("p1", question["id"], answer="12 gal per the sheet", by="owner")
        self.assertEqual(answered["status"], "answered")
        self.assertEqual(record.questions("p1", "open"), [])
        decision = record.record_decision("p1", text="Keep double-interlock", decided_by="lead", label="OWNER",
                                          basis="owner standard")
        self.assertEqual(record.decisions("p1")[0]["id"], decision["id"])
        with self.assertRaises(RecordError):
            record.record_evidence("p1", document="NFPA 13", status="maybe")
        cite = record.record_evidence("p1", document="NFPA 13", edition="2025", section="8.3.2.3.1.1",
                                      note="500 gal double-interlock cap", status="held")
        self.assertEqual(record.evidence("p1")[0]["id"], cite["id"])
        task = record.add_task("p1", title="Size DH-1", owner="fp-sprinkler")
        self.assertEqual(record.set_task("p1", task["id"], status="done")["status"], "done")
        record.set_agent("p1", name="FP specialist", role_slug="fp-sprinkler", status="working")
        record.set_agent("p1", name="FP specialist", role_slug="fp-sprinkler", status="done")
        agents = record.agents("p1")
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["status"], "done")
        finding = record.record_finding("p1", agent="fp-sprinkler", text="Zone total 281.3 gal",
                                        label="calculated", supports=[cite["id"]])
        self.assertEqual(record.findings("p1")[0]["supports"], [cite["id"]])
        self.assertEqual(finding["label"], "calculated")

    def test_snapshot_summary_and_delete(self):
        record = _record()
        record.ensure_project("p1", "Sample")
        record.record_fact("p1", kind="basis", key="insurer", value="FM", label="OWNER")
        record.open_question("p1", raised_by="lead", text="Enforced edition?")
        snap = record.snapshot("p1")
        self.assertEqual(set(snap), {"project", "facts", "fact_history", "evidence", "calcs", "findings",
                                     "retired_findings", "reviews", "questions", "decisions", "handoffs",
                                     "retired_decisions", "tasks", "agents", "jobs", "events", "latest",
                                     "unseen_answers"})
        # The newest plan and trace-check rows ride with the snapshot whatever the event window holds.
        self.assertEqual(set(snap["latest"]), {"plan", "record_check"})
        self.assertEqual(snap["project"]["name"], "Sample")
        text = record.summary_text("p1")
        self.assertIn("basis/insurer: FM (OWNER)", text)
        self.assertIn("Enforced edition?", text)
        self.assertEqual(record.summary_text("p9"), "The project record is empty.")
        record.delete_project("p1")
        self.assertIsNone(record.project_row("p1"))
        self.assertEqual(record.facts("p1"), [])
        self.assertEqual(record.events("p1"), [])

    def test_writes_from_many_threads_land_once_each(self):
        record = _record()
        record.ensure_project("p1")
        errors = []

        def work(n):
            try:
                for i in range(20):
                    record.record_fact("p1", kind="thread", key=f"t{n}-{i}", value="v", label="CODE")
            except Exception as exc:  # noqa: BLE001 - collected for the assertion
                errors.append(exc)

        threads = [threading.Thread(target=work, args=(n,)) for n in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(record.facts("p1")), 160)

    def test_import_project_brings_basis_and_finished_runs_once(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        run = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        project = {"id": "job1", "name": "Sample data hall DI zone", "basis": dict(EXAMPLE_BASIS), "last_run": run}
        record = _record()
        first = record.import_project(project)
        self.assertEqual(first, {"migrated": True, "facts": 5, "calcs": 8})
        self.assertEqual({row["key"] for row in record.facts("job1", "basis")},
                         {"ahj", "nfpa_13", "nfpa_72", "insurer", "hazard_notes"})
        self.assertEqual({row["tool"] for row in record.calcs("job1")}, set(run["tools"]))
        self.assertTrue(all(row["agent"] == "tool-plan" for row in record.calcs("job1")))
        self.assertEqual(record.import_project(project), {"migrated": False, "facts": 0, "calcs": 0})
        self.assertEqual(len(record.calcs("job1")), 8)


class ReviewFollowUpTests(unittest.TestCase):
    """The three review findings on the first record commit."""

    def test_a_different_calc_identity_is_a_new_row_not_a_replay(self):
        record = _record()
        record.ensure_project("p1")
        first = record.record_calc("p1", tool="hose_duration", inputs={"hazard": "ordinary"},
                                   outputs={"duration_min": 60}, calc_identity="aaaa")
        same = record.record_calc("p1", tool="hose_duration", inputs={"hazard": "ordinary"},
                                  outputs={"duration_min": 60}, calc_identity="aaaa")
        changed = record.record_calc("p1", tool="hose_duration", inputs={"hazard": "ordinary"},
                                     outputs={"duration_min": 75}, calc_identity="bbbb")
        self.assertTrue(same["replayed"])
        self.assertFalse(changed["replayed"])
        self.assertNotEqual(changed["id"], first["id"])
        rows = record.calcs("p1")
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["calc_identity"] for row in rows}, {"aaaa", "bbbb"})
        self.assertIsNone(record.find_calc("p1", "hose_duration", {"hazard": "ordinary"}, "cccc"))
        self.assertEqual(record.find_calc("p1", "hose_duration", {"hazard": "ordinary"}, "aaaa")["id"], first["id"])

    def test_tool_session_identity_follows_the_calc_code(self):
        import shutil

        from fpfa.calc_tools import ToolSession, calc_identity

        record = _record()
        record.ensure_project("p1")
        session = ToolSession(REPO, record=record, project_id="p1", agent="lead")
        self.assertEqual(session.calc_identity, calc_identity(REPO))
        self.assertEqual(len(session.calc_identity), 16)
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        # A pack whose kernel differs by one byte has another identity and does not replay.
        pack = Path(tempfile.mkdtemp(prefix="fpfa-pack-")) / "pack"
        shutil.copytree(REPO / "calcs", pack / "calcs")
        shutil.copytree(REPO / "skills", pack / "skills")
        for folder in ("roles", "modes", "specs", "corpus"):
            shutil.copytree(REPO / folder, pack / folder)
        formulas = pack / "calcs" / "fp" / "formulas.py"
        formulas.write_text(formulas.read_text(encoding="utf-8") + "\n# changed kernel\n", encoding="utf-8")
        other = ToolSession(pack, record=record, project_id="p1", agent="lead")
        self.assertNotEqual(other.calc_identity, session.calc_identity)
        other.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        rows = record.calcs("p1")
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["replay_count"] for row in rows], [0, 0])

    def test_model_facing_results_carry_the_record_id_and_the_tool_plan_does_not(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("p1")
        lead = ToolSession(REPO, record=record, project_id="p1", agent="lead")
        out = lead.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        self.assertEqual(out["record_id"], record.calcs("p1")[0]["id"])
        again = lead.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        self.assertEqual(again["record_id"], out["record_id"])
        self.assertNotIn("record_id", record.calcs("p1")[0]["outputs"])
        plan = ToolSession(REPO, record=record, project_id="p1", agent="tool-plan")
        self.assertNotIn("record_id", plan.execute("hose_duration", {"hazard": "light", "supervised": False}))
        plain = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        recorded = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="p1")
        self.assertEqual(plain["tools"], recorded["tools"])

    def test_sync_basis_supersedes_changed_form_values(self):
        record = _record()
        record.ensure_project("p1")
        first = record.sync_basis("p1", {"ahj": "Sample AHJ", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM"})
        self.assertEqual(len(first), 4)
        self.assertEqual(record.sync_basis("p1", {"ahj": "Sample AHJ", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM"}), [])
        changed = record.sync_basis("p1", {"ahj": "Sample AHJ", "nfpa_13": "2022", "nfpa_72": "2025", "insurer": "FM"})
        self.assertEqual([row["key"] for row in changed], ["nfpa_13"])
        current = {row["key"]: row for row in record.facts("p1", "basis")}
        self.assertEqual(current["nfpa_13"]["value"], "2022")
        self.assertEqual(len(record.facts("p1", "basis")), 4)
        history = record.facts("p1", "basis", include_superseded=True)
        self.assertEqual(len(history), 5)
        old = next(row for row in history if row["value"] == "2025" and row["key"] == "nfpa_13")
        self.assertEqual(old["superseded_by"], changed[0]["id"])
        self.assertIn("basis/nfpa_13: 2022 (CODE)", record.summary_text("p1"))
        self.assertNotIn("basis/nfpa_13: 2025", record.summary_text("p1"))

    def test_import_then_sync_follows_the_form_on_later_opens(self):
        record = _record()
        project = {"id": "job1", "name": "J", "basis": {"ahj": "A", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM", "hazard_notes": "notes"}}
        record.import_project(project)
        self.assertEqual(record.facts("job1", "basis")[1]["value"], "2025")
        project["basis"]["nfpa_13"] = "2022"
        self.assertEqual(record.import_project(project)["migrated"], False)
        record.sync_basis("job1", project["basis"])
        values = {row["key"]: row["value"] for row in record.facts("job1", "basis")}
        self.assertEqual(values["nfpa_13"], "2022")
        self.assertEqual(values["insurer"], "FM")

    def test_read_record_shows_inputs_outputs_evidence_and_full_rows_by_kind(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.record import RecordError

        record = _record()
        record.ensure_project("p1")
        session = ToolSession(REPO, record=record, project_id="p1", agent="fp-sprinkler")
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        session.execute("hose_duration", {"hazard": "light", "supervised": False})
        cite = session.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "19.2.3.1.3",
                                                    "note": "duration band", "status": "held"})
        summary = session.execute("read_record", {})["summary"]
        self.assertIn('"hazard":"ordinary"', summary)
        self.assertIn('"hazard":"light"', summary)
        self.assertIn('"duration_min":60', summary)
        self.assertIn('"duration_min":30', summary)
        self.assertIn(f"[{cite['id']}] NFPA 13 2025 19.2.3.1.3: duration band [held]", summary)
        calcs = session.execute("read_record", {"kind": "calcs"})
        self.assertEqual(calcs["kind"], "calcs")
        self.assertEqual(len(calcs["rows"]), 2)
        self.assertEqual(calcs["rows"][0]["inputs"], {"hazard": "ordinary", "supervised": True})
        self.assertEqual(calcs["rows"][0]["outputs"]["duration_min"], 60)
        one = session.execute("read_record", {"kind": "evidence", "id": cite["id"]})
        self.assertEqual([row["id"] for row in one["rows"]], [cite["id"]])
        self.assertEqual(one["rows"][0]["section"], "19.2.3.1.3")
        with self.assertRaises(RecordError):
            session.execute("read_record", {"kind": "secrets"})

    def test_an_older_database_gains_the_new_columns(self):
        import sqlite3

        from fpfa.record import Record

        path = Path(tempfile.mkdtemp(prefix="fpfa-old-")) / "fpfa.db"
        conn = sqlite3.connect(path)
        conn.executescript("""
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO meta VALUES ('schema_version', '1');
            CREATE TABLE facts (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL, key TEXT NOT NULL,
                value TEXT NOT NULL, label TEXT NOT NULL, source TEXT NOT NULL DEFAULT '', agent TEXT NOT NULL DEFAULT '',
                created TEXT NOT NULL);
            CREATE TABLE calc_records (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, tool TEXT NOT NULL,
                input_hash TEXT NOT NULL, inputs TEXT NOT NULL, outputs TEXT NOT NULL, pack_version TEXT NOT NULL DEFAULT '',
                agent TEXT NOT NULL DEFAULT '', replay_count INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL,
                last_used TEXT NOT NULL, UNIQUE (project_id, input_hash));
            INSERT INTO facts VALUES ('f1', 'p1', 'basis', 'insurer', 'FM', 'OWNER', '', '', '2026-01-01T00:00:00+00:00');
        """)
        conn.commit(); conn.close()
        record = Record(path)
        self.assertEqual(record.facts("p1", "basis")[0]["value"], "FM")
        self.assertIsNone(record.facts("p1", "basis")[0]["superseded_by"])
        row = record.record_calc("p1", tool="hose_duration", inputs={}, outputs={}, calc_identity="zz")
        self.assertEqual(record.calcs("p1")[0]["calc_identity"], "zz")
        # The version-2 database had no jobs table. Opening it with this code adds one.
        record.set_job("p1", job_id="j1", kind="chat", title="t", status="running")
        self.assertEqual(record.jobs("p1")[0]["status"], "running")
        conn = sqlite3.connect(path)
        self.assertEqual(conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0], "4")
        # Version 4 columns: what a calc followed, a finding's replacement, who a question is for.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(calc_records)").fetchall()}
        self.assertTrue({"depends", "varies"} <= columns)
        self.assertIn("reviews", {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")})
        conn.close()
        self.assertEqual(row["depends"], "[]")
        self.assertEqual(record.calcs("p1")[0]["depends"], [])
        self.assertEqual(record.calcs("p1")[0]["varies"], {})


class ToolSessionRecordingTests(unittest.TestCase):
    def test_calc_tools_record_themselves_and_replay_identical_calls(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        record.ensure_project("p1")
        session = ToolSession(REPO, record=record, project_id="p1", agent="lead")
        args = {"hazard": "ordinary", "supervised": True}
        first = session.execute("hose_duration", args)
        second = session.execute("hose_duration", {"supervised": True, "hazard": "ordinary"})
        self.assertEqual(first["duration_min"], 60)
        self.assertEqual(second, first)
        rows = record.calcs("p1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["replay_count"], 1)
        self.assertEqual(rows[0]["agent"], "lead")
        self.assertEqual(rows[0]["tool"], "hose_duration")
        # Content tools are not calc records.
        session.execute("list_modes", {})
        self.assertEqual(len(record.calcs("p1")), 1)

    def test_a_session_without_a_record_writes_nothing(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.record import RecordError

        session = ToolSession(REPO)
        self.assertFalse(session.recording)
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        with self.assertRaises(RecordError):
            session.execute("record_fact", {"kind": "basis", "key": "x", "value": "y", "label": "CODE"})
        with self.assertRaises(RecordError):
            session.execute("read_record", {})

    def test_record_tools_write_rows_as_the_session_agent(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        record.ensure_project("p1")
        session = ToolSession(REPO, record=record, project_id="p1", agent="fp-sprinkler")
        fact = session.execute("record_fact", {"kind": "owner", "key": "owner_standard", "value": "none stated",
                                               "label": "OWNER"})
        cite = session.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                                    "note": "500 gal cap", "status": "held"})
        finding = session.execute("record_finding", {"text": "Zone total 281.3 gal", "label": "calculated",
                                                      "supports": [cite["id"]]})
        question = session.execute("open_question", {"text": "Trim volume from the valve sheet?"})
        decision = session.execute("record_decision", {"text": "El/El trim", "label": "use best judgment",
                                                        "basis": "prime held by a solenoid"})
        self.assertEqual(fact["label"], "OWNER")
        self.assertEqual(record.findings("p1")[0]["agent"], "fp-sprinkler")
        self.assertEqual(record.findings("p1")[0]["supports"], [cite["id"]])
        self.assertEqual(record.questions("p1")[0]["raised_by"], "fp-sprinkler")
        self.assertEqual(record.decisions("p1")[0]["decided_by"], "fp-sprinkler")
        self.assertEqual(decision["label"], "use best judgment")
        shown = session.execute("read_record", {})
        self.assertIn("Zone total 281.3 gal", shown["summary"])
        self.assertEqual(shown["counts"]["findings"], 1)
        self.assertEqual(shown["counts"]["questions"], 1)
        self.assertEqual(finding["id"], record.findings("p1")[0]["id"])
        self.assertEqual(question["status"], "open")

    def test_schemas_list_the_record_tools_and_the_shell_names_them(self):
        from fpfa.calc_tools import RECORD_TOOLS, SCHEMAS
        from fpfa.everyday import assemble_system

        names = [item["name"] for item in SCHEMAS]
        for tool in RECORD_TOOLS:
            self.assertIn(tool, names)
        self.assertEqual(len(names), len(set(names)))
        system = assemble_system(REPO)
        self.assertIn("record_finding", system)
        self.assertIn("open_question", system)


class ModelPathRecordingTests(unittest.TestCase):
    def test_zone_run_records_eight_calcs_and_a_rerun_replays_them(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("job1")
        first = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        rows = record.calcs("job1")
        self.assertEqual(len(rows), 8)
        self.assertEqual({row["tool"] for row in rows}, set(first["tools"]))
        self.assertTrue(all(row["agent"] == "tool-plan" and row["replay_count"] == 0 for row in rows))
        second = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        self.assertEqual(second["tools"], first["tools"])
        self.assertEqual(second["narrative"], first["narrative"])
        rows = record.calcs("job1")
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["replay_count"] == 1 for row in rows))
        kinds = [row["kind"] for row in record.events("job1")]
        self.assertEqual(kinds.count("calc"), 8)
        self.assertEqual(kinds.count("calc_replay"), 8)

    def test_zone_run_without_a_record_is_unchanged(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        plain = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        record = _record()
        record.ensure_project("job1")
        recorded = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="job1")
        self.assertEqual(plain["tools"], recorded["tools"])
        self.assertEqual(plain["flags"], recorded["flags"])

    def test_narrator_calls_are_recorded_as_narrator(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("job1")

        def narrator(_system, _user, _tools, execute):
            execute("hose_duration", {"hazard": "light", "supervised": False})
            execute("record_finding", {"text": "Light hazard duration 30 min", "label": "calculated"})
            return {"text": "", "tool_calls": [], "stop_reason": "end_turn"}

        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator, record=record, project_id="job1")
        by_agent = {}
        for row in record.calcs("job1"):
            by_agent.setdefault(row["agent"], 0)
            by_agent[row["agent"]] += 1
        self.assertEqual(by_agent, {"tool-plan": 8, "narrator": 1})
        self.assertEqual(record.findings("job1")[0]["agent"], "narrator")

    def test_bess_starter_records_the_lfl_call(self):
        from fpfa.bess import run_bess_plan
        from fpfa.sample_data import EXAMPLE_BESS, EXAMPLE_BESS_BASIS

        record = _record()
        record.ensure_project("room1")
        run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, record=record, project_id="room1")
        rows = record.calcs("room1")
        self.assertEqual([row["tool"] for row in rows], ["lfl_setpoints"])
        self.assertEqual(rows[0]["agent"], "tool-plan")

    def test_everyday_turn_records_findings_as_the_lead(self):
        from fpfa.everyday import run_everyday

        record = _record()
        record.ensure_project("job1")
        script = [
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="t1", name="hose_duration", input={"hazard": "ordinary", "supervised": True}),
            ]),
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="t2", name="record_finding",
                      input={"text": "Duration 60 min", "label": "calculated"}),
                Block(type="tool_use", id="t3", name="open_question", input={"text": "Which hose allowance?"}),
            ]),
            SimpleNamespace(stop_reason="end_turn", content=[Block(type="text", text="Recorded.")]),
        ]
        seen = []

        def create(**kwargs):
            seen.append(kwargs)
            return script[len(seen) - 1]

        out = run_everyday(REPO, create, "What duration applies?", record=record, project_id="job1")
        self.assertEqual(out["text"], "Recorded.")
        self.assertEqual([row["tool"] for row in record.calcs("job1")], ["hose_duration"])
        self.assertEqual(record.calcs("job1")[0]["agent"], "lead")
        self.assertEqual(record.findings("job1")[0]["agent"], "lead")
        self.assertEqual(record.questions("job1", "open")[0]["raised_by"], "lead")
        self.assertFalse(any(call["is_error"] for call in out["tool_calls"]))


if __name__ == "__main__":
    unittest.main()
