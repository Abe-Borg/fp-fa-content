"""Phase 4: the Team tab, the sidebar roster, cancel, and the blind-check job.

Window tests need a display. Loop and helper tests do not.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
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

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-team-ui-")) / "fpfa.db")


def _system_text(kwargs) -> str:
    system = kwargs.get("system")
    if isinstance(system, str):
        return system
    return "".join(block.get("text", "") for block in system or [])


class CancelTests(unittest.TestCase):
    def test_loop_stops_before_the_next_round_when_cancelled(self):
        from fpfa.claude_client import TurnCancelled, run_tool_loop

        cancel = threading.Event()
        calls = []

        def create(**kwargs):
            calls.append(kwargs)
            cancel.set()
            return _turn("tool_use", Block(type="tool_use", id="t1", name="noop", input={}))

        ran = []
        with self.assertRaises(TurnCancelled):
            run_tool_loop(create, system="s", user_text="go", tools=[{"name": "noop"}],
                          execute=lambda _n, _a: ran.append(1) or {}, cancel=cancel)
        # The round in flight finished, its tool ran, and the next round did not start.
        self.assertEqual(len(calls), 1)
        self.assertEqual(ran, [1])

    def test_cancel_set_before_the_first_round_makes_no_call(self):
        from fpfa.claude_client import TurnCancelled, run_tool_loop

        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(TurnCancelled):
            run_tool_loop(lambda **_k: self.fail("no call expected"), system="s", user_text="go", tools=[],
                          execute=lambda _n, _a: {}, cancel=cancel)

    def test_cancel_reaches_a_delegated_specialist_and_marks_it_interrupted(self):
        from fpfa.claude_client import TurnCancelled
        from fpfa.everyday import run_everyday

        record = _record()
        record.ensure_project("job1")
        cancel = threading.Event()

        def create(**kwargs):
            system = _system_text(kwargs)
            if "# Sprinkler specialist" in system:
                cancel.set()
                return _turn("tool_use", Block(type="tool_use", id="s1", name="hose_duration",
                                               input={"hazard": "ordinary", "supervised": True}))
            return _turn("tool_use", Block(type="tool_use", id="l1", name="delegate",
                                           input={"specialist": "fp-sprinkler", "brief": "Size it."}))

        with self.assertRaises(TurnCancelled):
            run_everyday(REPO, create, "Design basis?", record=record, project_id="job1", cancel=cancel)
        agents = {row["role_slug"]: row["status"] for row in record.agents("job1")}
        self.assertEqual(agents["fp-sprinkler"], "interrupted")
        self.assertEqual(agents["lead"], "interrupted")
        self.assertEqual(record.handoffs("job1")[0]["status"], "cancelled")
        self.assertEqual(record.handoffs("job1")[0]["result"], "Cancelled by the designer.")

    def test_jobs_accept_the_cancelled_status(self):
        from fpfa.jobs import JobInbox

        inbox = JobInbox(worker_count=1)
        try:
            job = inbox.record(project_id="p", project_name="n", kind="chat", title="t", status="running")
            inbox.mark(job.id, "cancelled", "by the designer")
            self.assertEqual(inbox.get(job.id).status, "cancelled")
        finally:
            inbox.close()


class CancelledNarrationTests(unittest.TestCase):
    def test_zone_and_starter_report_a_cancelled_narration_and_keep_the_tool_plan(self):
        from fpfa.bess import run_bess_plan
        from fpfa.claude_client import TurnCancelled
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_DI
        from fpfa.workflow import NARRATION_CANCELLED, run_di_zone

        def narrator(_system, _user, _tools, _execute):
            raise TurnCancelled("Cancelled by the designer before the next model round.")

        plain = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        zone = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator)
        self.assertTrue(zone["cancelled"])
        self.assertFalse(plain["cancelled"])
        self.assertEqual(zone["tools"], plain["tools"])
        self.assertEqual(zone["source"], "tool-plan")
        self.assertIn(NARRATION_CANCELLED, zone["warnings"])
        self.assertIn(NARRATION_CANCELLED, zone["flags"])
        self.assertFalse(any(item.startswith("Claude was not used") for item in zone["warnings"]))
        bess = run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, narrator=narrator)
        self.assertTrue(bess["cancelled"])
        self.assertIn(NARRATION_CANCELLED, bess["warnings"])
        self.assertEqual(bess["source"], "tool-plan")

    def test_check_line_notices_findings_that_changed_after_the_check(self):
        from fpfa.team import check_record
        from fpfa.team_panel import check_line

        record = _record()
        record.ensure_project("job1")
        record.record_finding("job1", agent="fp-sprinkler", text="Duration is 60 min", label="PRACTICE")

        def create(**_kwargs):
            return SimpleNamespace(content=[Block(type="text", text='1. Supported. Cite: "x"')])

        # A PRACTICE finding with no supports is open, so the check does not pass; the line still speaks for it.
        check_record(REPO, record, "job1", create)
        before = check_line(record.snapshot("job1"))
        self.assertIn("Blind check:", before)
        self.assertNotIn("changed since", before)
        record.record_finding("job1", agent="fp-sprinkler", text="A new claim", label="PRACTICE")
        self.assertEqual(check_line(record.snapshot("job1")),
                         "Blind check: findings changed since the last check. Run it again.")


class PanelHelperTests(unittest.TestCase):
    def test_roster_blockers_check_line_and_summary(self):
        from fpfa.team import team_summary
        from fpfa.team_panel import NO_TEAM_LINE, blocker_lines, check_line, roster_lines

        record = _record()
        record.ensure_project("job1")
        self.assertEqual(roster_lines(record.snapshot("job1")), [])
        self.assertEqual(blocker_lines(record.snapshot("job1")), [])
        self.assertEqual(check_line(record.snapshot("job1")), "Blind check: nothing to check yet.")
        record.set_agent("job1", name="FP specialist", role_slug="fp-sprinkler", status="done")
        record.set_agent("job1", name="Lead", role_slug="lead", status="working")
        record.record_finding("job1", agent="fp-sprinkler", text="Zone total 281.3 gal", label="calculated")
        record.record_finding("job1", agent="fp-sprinkler", text="Screen misses", label="calculated")
        record.open_question("job1", raised_by="fp-sprinkler", text="Trim sheet?")
        pending = record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing", brief="Boolean")
        snap = record.snapshot("job1")
        lines = roster_lines(snap)
        self.assertEqual(lines[0], "✓ FP specialist (fp-sprinkler) done · 2 findings · 1 question")
        self.assertEqual(lines[1], "● Lead (lead) working")
        blockers = blocker_lines(snap)
        self.assertIn("? Trim sheet? (raised by fp-sprinkler)", blockers)
        self.assertIn("… handoff waiting for fa-releasing: Boolean", blockers)
        self.assertEqual(check_line(snap), "Blind check: not run on the current findings.")
        record.set_finding_status("job1", record.findings("job1")[0]["id"], status="Not supported")
        self.assertIn("! finding not supported: Zone total 281.3 gal", blocker_lines(record.snapshot("job1")))
        record.log_event("job1", "record_check", {"status_line": "Blind check: findings not Supported: 1."})
        self.assertEqual(check_line(record.snapshot("job1")), "Blind check: findings not Supported: 1.")
        self.assertEqual(NO_TEAM_LINE[:22], "No team activity on th")
        self.assertEqual(team_summary({"text": "x"}), "")
        summary = team_summary({
            "delegations": [{"specialist": "fp-sprinkler", "findings": [1, 2], "questions": [1], "handoffs": [], "calc_records": [1]}],
            "checks": [{"rows": [{"verdict": "Supported"}, {"verdict": "Not supported"}]}],
        })
        self.assertIn("**Team**", summary)
        self.assertIn("- fp-sprinkler: 2 findings, 1 question, 1 calc record", summary)
        self.assertIn("- checker: 1 of 2 findings Supported", summary)
        self.assertIn("Team tab", summary)
        self.assertEqual(pending["status"], "pending")


class TeamWindowTests(unittest.TestCase):
    def _wait_for(self, app, needle: str, timeout: float = 5.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.thread_text():
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")

    def _wait_until(self, app, predicate, timeout: float = 5.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            app.pump()
            if predicate():
                return
            time.sleep(0.02)
        self.fail("timed out")

    def _app(self, *, key: bool = True):
        data = Path(tempfile.mkdtemp(prefix="fpfa-team-ui-data-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"

        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config
        
        write_config({"key_backend": "file"})
        if key:
            save_api_key("sk-ant-local-test")
        root = Loop()
        self.addCleanup(root.destroy)
        app = root.open_desk()
        root.update()
        return app

    def test_team_tab_roster_and_sidebar_after_the_sample_run(self):
        app = self._app(key=False)
        self.assertFalse(bool(app.team["roster"]))
        self.assertIn("No team activity", app.team["roster_text"])
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        roster = app.team["roster_text"]
        self.assertIn("✓ Tool plan (tool-plan) done", roster)
        self.assertTrue(bool(app.team["roster"]))
        self.assertEqual(tuple(app.team["roster"]), ("✓ Tool plan (tool-plan) done",))
        self.assertIn("Blind check: nothing to check yet.", app.team["blockers_text"])
        self.assertFalse(app._pending_here())
        # The page draws the Team tab and the sidebar roster from this view.
        self.assertEqual(app.snapshot()["team"]["roster"], ["✓ Tool plan (tool-plan) done"])

    def test_handoff_rows_show_and_selecting_one_opens_the_detail(self):
        app = self._app(key=False)
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        project_id = app.project["id"]
        handoff = app.record.create_handoff(project_id, from_agent="fp-sprinkler", to_agent="fa-releasing",
                                            brief="Trim family El/El with a 15 psi low-air supervisory switch",
                                            payload={"family": "El/El", "low_air_supervisory_psi": 15})
        app.record.set_handoff(project_id, handoff["id"], status="returned", result="Boolean written.")
        app.record.open_question(project_id, raised_by="fp-sprinkler", text="Trim volume from the valve sheet?")
        app._refresh_team()
        app.pump()
        rows = app.team["handoffs"]
        self.assertEqual([row["id"] for row in rows], [str(handoff["id"])])
        row = rows[0]
        self.assertEqual(row["from"], "fp-sprinkler")
        self.assertEqual(row["to"], "fa-releasing")
        self.assertEqual(row["status"], "✓ returned")
        self.assertIn("Trim family El/El", row["brief"])
        # Selecting the row in the page opens this detail.
        detail = row["detail"]
        self.assertIn("fp-sprinkler → fa-releasing: returned", detail)
        self.assertIn('"low_air_supervisory_psi": 15', detail)
        self.assertIn("Boolean written.", detail)
        self.assertIn("? Trim volume from the valve sheet?", app.team["blockers_text"])
        # A refresh keeps the row and its detail.
        app._refresh_team()
        self.assertIn("Boolean written.", app.team["handoffs"][0]["detail"])

    def test_run_blind_check_posts_the_verdict_and_updates_the_panel(self):
        app = self._app()
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        project_id = app.project["id"]
        calc_id = app.record.calcs(project_id)[0]["id"]
        app.record.record_finding(project_id, agent="fp-sprinkler", text="Zone total 281.3 gal", label="calculated",
                                  supports=[calc_id])
        app._refresh_team()
        self.assertIn("Blind check: not run", app.team["blockers_text"])

        class Checker:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                return SimpleNamespace(content=[Block(type="text", text='1. Supported. Cite: "281.3"')])

        with patch("fpfa.desk.AnthropicMessages", Checker):
            app.start_record_check()
            self._wait_for(app, "every one of the 1 findings is Supported")
        self.assertEqual([job.kind for job in app.jobs.snapshot() if job.kind == "claim"], ["claim"])
        self.assertIn("every one of the 1 findings is Supported", app.team["blockers_text"])
        self.assertEqual(app.record.findings(project_id)[0]["status"], "Supported")
        self.assertEqual(app.design_basis_ready(), "")

    def test_blind_check_without_findings_or_key_explains_itself(self):
        app = self._app(key=False)
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        app.start_record_check()
        self.assertIn("no findings to check yet", app.thread_text())
        app.record.record_finding(app.project["id"], agent="lead", text="x", label="PRACTICE")
        app.start_record_check()
        self.assertIn("Save an Anthropic API key", app.thread_text())

    def test_cancel_stops_a_running_chat_turn(self):
        app = self._app()
        app.new_job()
        entered = threading.Event()
        release = threading.Event()

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                entered.set()
                if not release.wait(5):
                    raise TimeoutError("not released")
                return _turn("tool_use", Block(type="tool_use", id="t1", name="hose_duration",
                                               input={"hazard": "ordinary", "supervised": True}))

        with patch("fpfa.desk.AnthropicMessages", Blocking):
            app.send_chat("What duration applies?")
            self.assertTrue(entered.wait(3), "the turn did not start")
            self._wait_until(app, lambda: app._pending_here())
            app.cancel_running_jobs()
            self.assertIn("Cancel requested for 1 job", app.status.get())
            release.set()
            self._wait_for(app, "Cancelled.")
        thread = app.thread_text()
        self.assertIn("Cancelled by the designer before the next model round", thread)
        chat_jobs = [job for job in app.jobs.snapshot() if job.kind == "chat"]
        self.assertEqual([job.status for job in chat_jobs], ["cancelled"])
        self.assertFalse(app._pending_here())
        self.assertEqual(app._cancel_events, {})
        # The one tool that ran before the cancel still recorded itself as the lead.
        self.assertEqual([row["agent"] for row in app.record.calcs(app.project["id"])], ["lead"])

    def test_team_summary_is_appended_under_the_lead_reply(self):
        app = self._app()
        app.new_job()

        class Scripted:
            def __init__(self, _key):
                pass

            lead = [
                _turn("tool_use", Block(type="tool_use", id="l1", name="delegate",
                                        input={"specialist": "fp-sprinkler", "brief": "Size DH-1."})),
                _turn("end_turn", Block(type="text", text="Design basis follows.")),
            ]
            specialist = [
                _turn("tool_use", Block(type="tool_use", id="s1", name="hose_duration",
                                        input={"hazard": "ordinary", "supervised": True})),
                _turn("tool_use", Block(type="tool_use", id="s2", name="record_finding",
                                        input={"text": "Duration 60 min", "label": "calculated"})),
                _turn("end_turn", Block(type="text", text="Done.")),
            ]

            def create(self, **kwargs):
                system = _system_text(kwargs)
                script = self.specialist if "# Sprinkler specialist" in system else self.lead
                return script.pop(0)

        with patch("fpfa.desk.AnthropicMessages", Scripted):
            app.send_chat("Give me the design basis for zone DH-1.")
            self._wait_for(app, "Design basis follows.")
        thread = app.thread_text()
        self.assertIn("Team", thread)
        self.assertIn("fp-sprinkler: 1 finding, 1 calc record", thread)
        roster = app.team["roster_text"]
        self.assertIn("✓ Sprinkler specialist (fp-sprinkler) done · 1 finding", roster)
        self.assertIn("✓ Lead (lead) done", roster)
        self.assertEqual(len(app.team["handoffs"]), 1)
        self.assertIn("rounds", app.status.get())

    def test_cancelling_a_narrated_zone_run_keeps_the_figures_and_marks_the_job(self):
        app = self._app()
        app.ask_claude.set(True)
        entered = threading.Event()
        release = threading.Event()

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                entered.set()
                if not release.wait(5):
                    raise TimeoutError("not released")
                return _turn("tool_use", Block(type="tool_use", id="t1", name="hose_duration",
                                               input={"hazard": "ordinary", "supervised": True}))

        with patch("fpfa.desk.AnthropicMessages", Blocking):
            app.start_sample_di()
            self.assertTrue(entered.wait(3), "the narration did not start")
            self._wait_until(app, lambda: app._pending_here())
            app.cancel_running_jobs()
            release.set()
            self._wait_for(app, "Cancelled. The designer stopped the narration")
        thread = app.thread_text()
        self.assertIn("Zone total is 281.3 gal", thread)
        zone_jobs = [job for job in app.jobs.snapshot() if job.kind == "zone"]
        self.assertEqual([job.status for job in zone_jobs], ["cancelled"])
        self.assertTrue(app.project["last_run"]["cancelled"])
        self.assertTrue(any("Narration cancelled by the designer" in flag for flag in app.project["last_run"]["flags"]))
        self.assertIn("Cancelled.", app.status.get())
        self.assertEqual(app._cancel_events, {})

    def test_a_queued_blind_check_that_was_cancelled_makes_no_model_call(self):
        app = self._app()
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        project_id = app.project["id"]
        calc_id = app.record.calcs(project_id)[0]["id"]
        app.record.record_finding(project_id, agent="fp-sprinkler", text="Zone total 281.3 gal",
                                  label="calculated", supports=[calc_id])
        hold = threading.Event()
        started = [threading.Event(), threading.Event()]

        def block(index):
            def work(_job_id):
                started[index].set()
                hold.wait(5)
            return work

        # Both workers busy, so the blind check waits in the queue.
        for index in range(2):
            app.jobs.submit(project_id=project_id, project_name="n", kind="chat", title="busy", work=block(index))
        self.assertTrue(started[0].wait(3) and started[1].wait(3))

        class Boom:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                raise AssertionError("a cancelled check must not call the model")

        with patch("fpfa.desk.AnthropicMessages", Boom):
            app.start_record_check()
            claim = [job for job in app.jobs.snapshot() if job.kind == "claim"]
            self.assertEqual([job.status for job in claim], ["queued"])
            app.cancel_running_jobs()
            self.assertIn("Cancel requested for 3 jobs", app.status.get())
            hold.set()
            self._wait_for(app, "Cancelled before the blind check started")
        claim = [job for job in app.jobs.snapshot() if job.kind == "claim"]
        self.assertEqual([job.status for job in claim], ["cancelled"])
        self.assertEqual(app.record.findings(project_id)[0]["status"], "open")
        # The check dropped its own event. The two stand-in jobs never pop theirs.
        self.assertNotIn(claim[0].id, app._cancel_events)


if __name__ == "__main__":
    unittest.main()
