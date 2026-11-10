"""Recovery: jobs on the record, the launch pass, a forced kill, and sleep/wake.

This is Tests C (continuity) and D (recovery) from docs/prototype-plan.md as far
as a test process can drive them. A child process is really killed. The manual
Windows steps are in docs/recovery-protocol.md. No API call is made.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402



class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def _turn(stop_reason, *blocks):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks), usage=None)


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-recovery-")) / "fpfa.db")


class Recorder:
    """create() that ends the turn at once and keeps what it was sent."""

    def __init__(self, text="Noted."):
        self.calls: list[dict] = []
        self.text = text

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return _turn("end_turn", Block(type="text", text=self.text))


class JobRowTests(unittest.TestCase):
    def test_jobs_persist_once_per_status_and_never_move_back(self):
        from fpfa.record import RecordError

        record = _record()
        record.ensure_project("p1", "Job one")
        row = record.set_job("p1", job_id="j1", kind="chat", title="Size DH-1", status="queued")
        self.assertEqual(row["status"], "queued")
        record.set_job("p1", job_id="j1", kind="chat", title="Size DH-1", status="running")
        record.set_job("p1", job_id="j1", kind="chat", title="Size DH-1", status="running")
        late = record.set_job("p1", job_id="j1", kind="chat", title="Size DH-1", status="queued")
        self.assertEqual(late["status"], "running", "a late queued write must not move the job back")
        record.set_job("p1", job_id="j1", kind="chat", title="Size DH-1", status="done")
        after = record.set_job("p1", job_id="j1", kind="chat", status="running")
        self.assertEqual(after["status"], "done", "a finished job stays finished")
        kinds = [event["kind"] for event in record.events("p1") if event["kind"].startswith("job_")]
        self.assertEqual(kinds, ["job_queued", "job_running", "job_done"])
        self.assertEqual([row["status"] for row in record.jobs("p1")], ["done"])
        self.assertEqual(record.jobs("p1", status="running"), [])
        with self.assertRaises(RecordError):
            record.set_job("p1", job_id="j2", kind="chat", status="paused")
        self.assertIn("jobs", record.snapshot("p1"))
        self.assertEqual(record.detail("p1", "jobs", "j1")[0]["kind"], "chat")
        record.delete_project("p1")
        self.assertEqual(record.jobs("p1"), [])


def _seed_in_flight(record):
    """A record as a kill leaves it: work on p1 in flight, p2 finished."""
    record.ensure_project("p1", "Job one")
    record.ensure_project("p2", "Job two")
    record.set_job("p1", job_id="run1", kind="chat", title="Size the DH-1 zone", status="running")
    record.set_job("p1", job_id="q1", kind="claim", title="Blind check", status="queued")
    record.set_job("p1", job_id="d1", kind="zone", title="Zone run", status="done")
    record.set_job("p2", job_id="d2", kind="bess", title="Starter", status="cancelled")
    record.set_agent("p1", name="Lead", role_slug="lead", status="working")
    record.set_agent("p1", name="Sprinkler specialist", role_slug="fp-sprinkler", status="working")
    record.set_agent("p1", name="Tool plan", role_slug="tool-plan", status="done")
    delivered = record.create_handoff("p1", from_agent="lead", to_agent="fp-sprinkler",
                                      brief="Check the trim volume", payload={"gal": 5})
    record.set_handoff("p1", delivered["id"], status="delivered", by="lead")
    pending = record.create_handoff("p1", from_agent="fp-sprinkler", to_agent="fa-releasing",
                                    brief="Confirm the releasing sequence")
    returned = record.create_handoff("p1", from_agent="lead", to_agent="fa-releasing", brief="Earlier brief")
    record.set_handoff("p1", returned["id"], status="delivered", by="lead")
    record.set_handoff("p1", returned["id"], status="returned", result="done", by="fa-releasing")
    return delivered, pending, returned


class RecoverTests(unittest.TestCase):
    def test_recover_marks_in_flight_rows_interrupted_and_requeues_delivered_handoffs(self):
        from fpfa.record import INTERRUPTED_NOTE, REQUEUED_NOTE

        record = _record()
        delivered, pending, returned = _seed_in_flight(record)
        report = record.recover()
        self.assertEqual(sorted(report), ["p1"], "the finished project is not touched")
        item = report["p1"]
        self.assertEqual(item["name"], "Job one")
        self.assertEqual(sorted(row["id"] for row in item["jobs"]), ["q1", "run1"])
        self.assertEqual(sorted(item["agents"]), ["Lead", "Sprinkler specialist"])
        self.assertEqual([row["id"] for row in item["handoffs"]], [delivered["id"]])
        jobs = {row["id"]: row for row in record.jobs("p1")}
        self.assertEqual(jobs["run1"]["status"], "interrupted")
        self.assertEqual(jobs["run1"]["error"], INTERRUPTED_NOTE)
        self.assertEqual(jobs["q1"]["status"], "interrupted")
        self.assertEqual(jobs["d1"]["status"], "done")
        self.assertEqual(record.jobs("p2")[0]["status"], "cancelled")
        agents = {row["name"]: row["status"] for row in record.agents("p1")}
        self.assertEqual(agents, {"Lead": "interrupted", "Sprinkler specialist": "interrupted", "Tool plan": "done"})
        rows = {row["id"]: row for row in record.handoffs("p1")}
        self.assertEqual(len(rows), 3, "no handoff row is copied")
        self.assertEqual(rows[delivered["id"]]["status"], "pending")
        self.assertIsNone(rows[delivered["id"]]["delivered"])
        self.assertEqual(rows[delivered["id"]]["result"], REQUEUED_NOTE)
        self.assertEqual(rows[pending["id"]]["status"], "pending")
        self.assertEqual(rows[pending["id"]]["result"], "")
        self.assertEqual(rows[returned["id"]]["status"], "returned")
        self.assertEqual([row["id"] for row in record.pending_handoffs("p1", to_agent="fp-sprinkler")], [delivered["id"]])
        recovered = record.latest_event("p1", "recovered")["payload"]
        self.assertEqual(sorted(row["id"] for row in recovered["jobs"]), ["q1", "run1"])
        self.assertEqual(recovered["jobs"][0].keys(), {"id", "kind", "title"})
        self.assertEqual(sorted(recovered["agents"]), ["Lead", "Sprinkler specialist"])
        self.assertEqual([row["id"] for row in recovered["handoffs"]], [delivered["id"]])
        self.assertIsNone(record.latest_event("p2", "recovered"))
        self.assertEqual(record.recover(), {}, "a second pass finds nothing")
        self.assertEqual(len(record.handoffs("p1")), 3)

    def test_recovery_notices_wait_until_the_note_is_posted(self):
        record = _record()
        self.assertEqual(record.unnoted_recoveries(), {})
        delivered, _pending, _returned = _seed_in_flight(record)
        first = record.recover()
        owed = record.unnoted_recoveries()
        self.assertEqual(sorted(owed), ["p1"])
        self.assertEqual(owed["p1"]["name"], "Job one")
        self.assertEqual(sorted(row["id"] for row in owed["p1"]["jobs"]), ["q1", "run1"])
        self.assertEqual(owed["p1"]["agents"], first["p1"]["agents"])
        self.assertEqual([row["id"] for row in owed["p1"]["handoffs"]], [delivered["id"]])
        # A second launch recovers nothing new but still owes the note.
        self.assertEqual(record.recover(), {})
        self.assertEqual(sorted(row["id"] for row in record.unnoted_recoveries()["p1"]["jobs"]), ["q1", "run1"])
        record.note_recovery("p1")
        self.assertEqual(record.unnoted_recoveries(), {})
        # A later kill owes a new note that holds only the new work.
        record.set_job("p1", job_id="run2", kind="zone", title="Zone run again", status="running")
        record.recover()
        owed = record.unnoted_recoveries()
        self.assertEqual([row["id"] for row in owed["p1"]["jobs"]], ["run2"])
        self.assertEqual(owed["p1"]["agents"], [])
        self.assertEqual(owed["p1"]["handoffs"], [])

    def test_a_requeued_handoff_is_delivered_once_by_the_next_delegation(self):
        from fpfa.team import delegate

        record = _record()
        delivered, _pending, _returned = _seed_in_flight(record)
        record.recover()
        create = Recorder("Trim volume checked.")
        contribution = delegate(REPO, record, "p1", create, specialist="fp-sprinkler", brief="Finish the trim check.")
        user = create.calls[0]["messages"][0]["content"]
        self.assertIn("Handoffs waiting for you:", user)
        self.assertIn("from lead: Check the trim volume", user)
        self.assertIn('"gal": 5', user)
        self.assertEqual(contribution["delivered_handoffs"], [delivered["id"]])
        rows = {row["id"]: row for row in record.handoffs("p1")}
        self.assertEqual(rows[delivered["id"]]["status"], "returned")
        self.assertEqual(len(rows), 4, "the delegation wrote its own handoff and nothing else")
        self.assertEqual({row["name"]: row["status"] for row in record.agents("p1")}["Sprinkler specialist"], "done")

    def test_the_lead_sees_pending_handoffs_at_the_top_of_its_turn(self):
        from fpfa.everyday import run_everyday
        from fpfa.team import pending_handoff_note

        record = _record()
        delivered, pending, _returned = _seed_in_flight(record)
        record.recover()
        note = pending_handoff_note(record, "p1")
        self.assertIn("Handoffs waiting on the record", note)
        self.assertIn(f"[{delivered['id']}] from lead to fp-sprinkler (re-queued after a relaunch): Check the trim volume", note)
        self.assertIn(f"[{pending['id']}] from fp-sprinkler to fa-releasing: Confirm the releasing sequence", note)
        create = Recorder()
        run_everyday(REPO, create, "What is left on DH-1?", record=record, project_id="p1")
        user = create.calls[0]["messages"][0]["content"]
        self.assertTrue(user.startswith("Handoffs waiting on the record"))
        self.assertTrue(user.endswith("What is left on DH-1?"))
        self.assertEqual(pending_handoff_note(_record(), "none"), "")
        clean = Recorder()
        record.set_handoff("p1", delivered["id"], status="returned", by="fp-sprinkler")
        record.set_handoff("p1", pending["id"], status="returned", by="fa-releasing")
        run_everyday(REPO, clean, "Anything else?", record=record, project_id="p1")
        self.assertEqual(clean.calls[0]["messages"][0]["content"], "Anything else?")

    def test_recovery_text_names_what_was_in_flight(self):
        from fpfa.team_panel import blocker_lines, recovery_text

        record = _record()
        _seed_in_flight(record)
        report = record.recover()
        text = recovery_text(report["p1"])
        self.assertTrue(text.startswith("**Recovered after a relaunch.**"))
        self.assertIn('The chat job "Size the DH-1 zone" was interrupted.', text)
        self.assertIn('The claim job "Blind check" was interrupted.', text)
        self.assertIn("Lead was interrupted before it returned.", text)
        self.assertIn("Sprinkler specialist was interrupted before it returned.", text)
        self.assertIn("handoff from lead to fp-sprinkler (Check the trim volume) was re-queued", text)
        self.assertNotIn("Zone run", text, "a finished job is not reported")
        self.assertEqual(recovery_text(None), "")
        self.assertEqual(recovery_text({"name": "x", "jobs": [], "agents": [], "handoffs": []}), "")
        blockers = blocker_lines(record.snapshot("p1"))
        self.assertIn("… handoff waiting for fp-sprinkler (re-queued after a relaunch): Check the trim volume", blockers)
        self.assertIn("… handoff waiting for fa-releasing: Confirm the releasing sequence", blockers)
        self.assertIn("! chat job interrupted by a relaunch: Size the DH-1 zone. Run it again; recorded calcs replay.", blockers)
        self.assertFalse(any("Zone run" in line for line in blockers))


HOLDER = textwrap.dedent(
    """
    import sys, time
    app_dir, path = sys.argv[1:3]
    sys.path.insert(0, app_dir)
    from fpfa.instance_lock import InstanceLock
    lock = InstanceLock(path)
    print("held" if lock.acquire() else "refused", flush=True)
    time.sleep(60)
    """
)


class InstanceLockTests(unittest.TestCase):
    def test_one_holder_per_file_in_one_process(self):
        from fpfa.instance_lock import InstanceLock

        folder = Path(tempfile.mkdtemp(prefix="fpfa-lock-"))
        first = InstanceLock(folder / "fpfa.lock")
        second = InstanceLock(folder / "fpfa.lock")
        other = InstanceLock(folder / "other.lock")
        self.assertTrue(first.acquire())
        self.assertTrue(first.acquire(), "acquiring again is a no-op for the holder")
        self.assertFalse(second.acquire())
        self.assertTrue(other.acquire(), "a different file is a different lock")
        self.assertTrue(first.held)
        self.assertFalse(second.held)
        first.release()
        first.release()
        self.assertFalse(first.held)
        self.assertTrue(second.acquire())
        self.assertEqual((folder / "fpfa.lock").read_text(encoding="ascii").strip(), str(os.getpid()))
        second.release()
        other.release()

    def test_the_lock_follows_the_process_that_holds_it(self):
        from fpfa.instance_lock import InstanceLock

        folder = Path(tempfile.mkdtemp(prefix="fpfa-lock-proc-"))
        script = folder / "holder.py"
        script.write_text(HOLDER, encoding="utf-8")
        path = folder / "fpfa.lock"
        proc = subprocess.Popen(
            [sys.executable, str(script), str(APP_DIR), str(path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            self.assertEqual(proc.stdout.readline().strip(), "held")
            mine = InstanceLock(path)
            self.assertFalse(mine.acquire(), "a live process holds the data directory")
        finally:
            proc.kill()
            proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()
        # Killed, not closed: the operating system released it, so a relaunch can go ahead.
        self.assertTrue(mine.acquire())
        mine.release()


CHILD = textwrap.dedent(
    """
    import json, sys, time
    app_dir, repo, db, plan = sys.argv[1:5]
    sys.path.insert(0, app_dir)
    from fpfa.calc_tools import ToolSession
    from fpfa.record import Record

    record = Record(db)
    record.ensure_project("p1", "Kill test")
    record.set_job("p1", job_id="zone1", kind="zone", title="Zone run", status="running")
    record.set_agent("p1", name="Tool plan", role_slug="tool-plan", status="working")
    record.set_agent("p1", name="Lead", role_slug="lead", status="working")
    handoff = record.create_handoff("p1", from_agent="lead", to_agent="fp-sprinkler", brief="Check the trim")
    record.set_handoff("p1", handoff["id"], status="delivered", by="lead")
    session = ToolSession(repo, record=record, project_id="p1", agent="tool-plan")
    with open(plan, encoding="utf-8") as handle:
        calls = json.load(handle)
    for call in calls:
        session.execute(call["name"], call["input"])
        print("done " + call["name"], flush=True)
        time.sleep(0.15)
    print("finished", flush=True)
    time.sleep(60)
    """
)


class ForcedKillTests(unittest.TestCase):
    """Test D, the kill half: a child process is killed between calc records."""

    def test_a_killed_run_leaves_no_duplicate_calcs_and_recovery_marks_the_job(self):
        from fpfa.record import CALC_TOOLS, Record
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        plain = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        calls = [
            {"name": call["name"], "input": call["input"]}
            for call in plain["transcript"]
            if call.get("name") in CALC_TOOLS and not call.get("is_error")
        ]
        self.assertEqual(len(calls), 8)
        folder = Path(tempfile.mkdtemp(prefix="fpfa-kill-"))
        db = folder / "fpfa.db"
        plan = folder / "plan.json"
        plan.write_text(json.dumps(calls), encoding="utf-8")
        script = folder / "child.py"
        script.write_text(CHILD, encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(script), str(APP_DIR), str(REPO), str(db), str(plan)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        done = 0
        deadline = time.time() + 60
        try:
            while done < 3 and time.time() < deadline:
                line = proc.stdout.readline()
                if not line:
                    break
                if line.startswith("done "):
                    done += 1
        finally:
            proc.kill()
            proc.wait(timeout=10)
        stderr = proc.stderr.read()
        proc.stdout.close()
        proc.stderr.close()
        self.assertEqual(done, 3, f"the child did not get three calcs down before the kill: {stderr}")

        record = Record(db)
        before = record.calcs("p1")
        self.assertIn(len(before), (3, 4), "three commits were seen; a fourth may have landed before the kill")
        self.assertTrue(all(row["replay_count"] == 0 for row in before))
        report = record.recover()
        self.assertEqual([row["id"] for row in report["p1"]["jobs"]], ["zone1"])
        self.assertEqual(sorted(report["p1"]["agents"]), ["Lead", "Tool plan"])
        self.assertEqual(len(report["p1"]["handoffs"]), 1)
        self.assertEqual(record.jobs("p1")[0]["status"], "interrupted")

        again = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="p1")
        rows = record.calcs("p1")
        self.assertEqual(len(rows), 8, "the re-run adds only the calcs the kill prevented")
        self.assertEqual(sum(row["replay_count"] for row in rows), len(before), "every surviving calc replayed once")
        self.assertEqual(again["tools"], plain["tools"], "the figures are the known answer either way")
        agents = {row["name"]: row["status"] for row in record.agents("p1")}
        self.assertEqual(agents, {"Lead": "interrupted", "Tool plan": "done"})
        self.assertEqual(record.recover(), {})


class RecoveryWindowTests(unittest.TestCase):
    def _data_dir(self):
        data = Path(tempfile.mkdtemp(prefix="fpfa-recovery-ui-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        return data

    def _app(self, *, key: bool = False):

        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config
        
        write_config({"key_backend": "file"})
        if key:
            save_api_key("sk-ant-local-test")
        root = Loop()
        self.addCleanup(self._destroy, root)
        app = root.open_desk()
        root.update()
        return app

    @staticmethod
    def _destroy(root) -> None:
        try:
            root.destroy()
        except Exception:
            pass

    def _settle(self, app, rounds: int = 5) -> None:
        for _ in range(rounds):
            app._poll()
            app.pump()
            time.sleep(0.02)

    def test_window_jobs_are_written_to_the_record(self):
        self._data_dir()
        app = self._app()
        app.ask_claude.set(False)
        app.start_sample_di()
        self._settle(app)
        project_id = app.project["id"]
        rows = app.record.jobs(project_id)
        self.assertEqual([(row["kind"], row["status"]) for row in rows], [("zone", "done")])
        kinds = [event["kind"] for event in app.record.events(project_id) if event["kind"].startswith("job_")]
        self.assertIn("job_done", kinds)
        self.assertNotIn("job_interrupted", kinds)

    def test_a_relaunch_shows_the_roster_the_requeued_handoff_and_the_interrupted_job(self):
        self._data_dir()
        first = self._app()
        first.ask_claude.set(False)
        first.start_sample_di()
        self._settle(first)
        project_id = first.project["id"]
        record = first.record
        # The process dies with a chat turn, a delegation, and its handoff in flight.
        record.set_job(project_id, job_id="chat9", kind="chat", title="Size the DH-1 zone", status="running")
        record.set_agent(project_id, name="Lead", role_slug="lead", status="working")
        record.set_agent(project_id, name="Sprinkler specialist", role_slug="fp-sprinkler", status="working")
        handoff = record.create_handoff(project_id, from_agent="lead", to_agent="fp-sprinkler", brief="Check the trim volume")
        record.set_handoff(project_id, handoff["id"], status="delivered", by="lead")
        waiting = record.create_handoff(project_id, from_agent="fp-sprinkler", to_agent="fa-releasing",
                                        brief="Confirm the releasing sequence")
        first._persist_open_work()
        first.close()

        # A launch that never opens the job still owes its note to the next one.
        middle = self._app()
        self.assertIn("Recovered after a relaunch: 1 job interrupted, 1 handoff re-queued", middle.status.get())
        self.assertEqual(middle.jobs.get("chat9").status, "interrupted")
        self.assertEqual(middle.record.recover(), {})
        middle.close()

        app = self._app()
        self.assertIn("Recovered after a relaunch: 1 job interrupted, 1 handoff re-queued", app.status.get())
        lines = tuple(app.inbox_lines)
        self.assertTrue(any(line.startswith("interrupted chat") and line.endswith("chat9") for line in lines), lines)
        self.assertEqual(app.jobs.get("chat9").status, "interrupted")
        self.assertEqual(app.record.jobs(project_id, status="interrupted")[0]["id"], "chat9")
        self.assertNotIn("Recovered", app.thread_text(), "the note waits for the job to open")

        app.open_project(project_id)
        self._settle(app)
        thread = app.thread_text()
        self.assertIn("Recovered after a relaunch.", thread)
        self.assertIn('The chat job "Size the DH-1 zone" was interrupted.', thread)
        self.assertIn("handoff from lead to fp-sprinkler (Check the trim volume) was re-queued", thread)
        self.assertEqual(thread.count("Recovered after a relaunch."), 1)
        roster = app.team["roster_text"]
        self.assertIn("! Lead (lead) interrupted", roster)
        self.assertIn("! Sprinkler specialist (fp-sprinkler) interrupted", roster)
        self.assertIn("✓ Tool plan (tool-plan) done", roster)
        blockers = app.team["blockers_text"]
        self.assertIn("handoff waiting for fp-sprinkler (re-queued after a relaunch): Check the trim volume", blockers)
        self.assertIn("handoff waiting for fa-releasing: Confirm the releasing sequence", blockers)
        self.assertIn("chat job interrupted by a relaunch: Size the DH-1 zone", blockers)
        rows = {row["id"]: row for row in app.record.handoffs(project_id)}
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[handoff["id"]]["status"], "pending")
        self.assertEqual(rows[waiting["id"]]["status"], "pending")
        self.assertEqual(len(app.record.calcs(project_id)), 8, "the tool plan's calcs are back")
        # Opening it again posts nothing new, and the record holds the note too.
        saved = app.project
        app.open_project(project_id)
        self._settle(app)
        self.assertEqual(app.thread_text().count("Recovered after a relaunch."), 1)
        self.assertEqual(sum(1 for turn in saved["chat"] if "Recovered after a relaunch" in turn.get("text", "")), 1)
        self.assertEqual(app.record.unnoted_recoveries(), {})
        app._persist_open_work()
        app.close()

        # Once the note has been read, a later launch owes nothing and lists nothing.
        fourth = self._app()
        self.assertNotIn("Recovered", fourth.status.get())
        self.assertEqual(tuple(fourth.inbox_lines), ())
        fourth.open_project(project_id)
        self._settle(fourth)
        self.assertEqual(fourth.thread_text().count("Recovered after a relaunch."), 1)
        self.assertEqual(fourth.record.jobs(project_id, status="interrupted")[0]["id"], "chat9")

    def test_a_second_window_on_the_same_data_directory_is_refused_and_recovers_nothing(self):

        from fpfa.instance_lock import LOCK_NAME, InstanceLock, InstanceLockError
        from fpfa.record import Record
        
        data = self._data_dir()
        # The first window's live work, as its record shows it while it runs.
        record = Record(data / "fpfa.db")
        record.ensure_project("p1", "Live job")
        record.set_job("p1", job_id="live1", kind="chat", title="Still running", status="running")
        record.set_agent("p1", name="Lead", role_slug="lead", status="working")
        holder = InstanceLock(data / LOCK_NAME)
        self.assertTrue(holder.acquire())
        root = Loop()
        self.addCleanup(self._destroy, root)
        with self.assertRaises(InstanceLockError) as caught:
            root.open_desk()
        self.assertIn("already open on this data directory", str(caught.exception))
        self.assertEqual(record.jobs("p1")[0]["status"], "running", "the live job was not touched")
        self.assertEqual(record.agents("p1")[0]["status"], "working")
        self.assertEqual(record.unnoted_recoveries(), {})
        holder.release()
        # With the first window gone, the next launch owns the directory and recovers.
        app = self._app()
        self.assertTrue(app.instance_lock.held)
        self.assertIn("Recovered after a relaunch: 1 job interrupted", app.status.get())
        self.assertEqual(app.record.jobs("p1")[0]["status"], "interrupted")
        app.close()
        self.assertFalse(app.instance_lock.held, "destroying the window releases the directory")

    def test_a_long_gap_between_polls_is_reported_as_a_resume(self):
        self._data_dir()
        app = self._app()
        app.ask_claude.set(False)
        app.start_sample_di()
        self._settle(app)
        project_id = app.project["id"]
        app._poll()
        self.assertNotIn("Resumed", app.status.get())
        app._last_tick = time.time() - 600
        app._poll()
        self.assertIn("Resumed after about 10 min. No job was running.", app.status.get())
        event = app.record.latest_event(project_id, "wake")
        self.assertGreaterEqual(event["payload"]["gap_seconds"], 599)
        self.assertEqual(event["payload"]["running_jobs"], [])
        # With a job on the queue, the line says what to expect of it.
        hold = __import__("threading").Event()
        app.jobs.submit(project_id=project_id, project_name="n", kind="chat", title="busy", work=lambda _id: hold.wait(5))
        self._settle(app, 2)
        app._last_tick = time.time() - 125
        app._poll()
        self.assertIn("Resumed after about 2 min. 1 job still running", app.status.get())
        hold.set()
        self._settle(app, 3)


if __name__ == "__main__":
    unittest.main()
