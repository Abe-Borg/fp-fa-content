"""The window's side of the team: where a job stands, what the designer can do about it, and what the
application says about a reply. No display, no network: every model call is a stand-in.

Covered here: /status, answering a team question on the panel, the one-tap next steps a returning
designer is offered, a zone run that an input change left behind, the figures in the lead's reply
looked up on the record, a request the API asked to have sent again, and the time a job took.
"""

from __future__ import annotations

import os
import sys
import tempfile
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
from test_coherence import _run_plan, _seed_inputs  # noqa: E402
from test_team import _record  # noqa: E402
from test_team_protocol import SEGMENTS, Play, _calc, _finding, _screen_steps, call, say, use  # noqa: E402


def client_for(play):
    """An AnthropicMessages stand-in that plays a script. It has no streaming call, so a reply arrives whole."""

    class Client:
        def __init__(self, _key):
            pass

        def create(self, **kwargs):
            return play(**kwargs)

    return Client


class DeskCase(unittest.TestCase):
    def _app(self, *, key: bool = True):
        data = Path(tempfile.mkdtemp(prefix="fpfa-desk-team-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config

        write_config({"key_backend": "file"})
        if key:
            save_api_key("sk-ant-local-test")
        root = Loop()
        self.addCleanup(root.destroy)
        self.root = root
        app = root.open_desk()
        root.update()
        return app

    def _settle(self, app, timeout: float = 8.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            app.pump()
            if not app._pending_here():
                app.pump()
                return
            time.sleep(0.02)
        self.fail("the job did not finish")

    def _sample(self, app):
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        return app.project["id"]

    def _ask(self, app, play, text: str) -> None:
        with patch("fpfa.desk.AnthropicMessages", client_for(play)):
            app.send_chat(text)
            self._settle(app)


class StatusAndAnswerTests(DeskCase):
    def test_status_says_where_the_job_stands_without_a_model_call(self):
        app = self._app(key=False)
        app.send_chat("/status")
        self.assertIn("No specialist has worked on this job yet.", app.thread_text(),
                      "a status on a new job opens the job and says nothing has happened")
        project_id = self._sample(app)
        fp_finding = app.record.record_finding(project_id, agent="fp-sprinkler", label="calculated",
                                               text="The FM screen misses at 38.1 s",
                                               supports=[_calc(app.record, "di_trip_to_water", project_id=project_id)["id"]])
        app.record.set_agent(project_id, name="Sprinkler specialist", role_slug="fp-sprinkler", status="done")
        app.record.log_event(project_id, "plan", {"objective": "Design basis for DH-1", "steps": [
            {"title": "Delivery screen", "owner": "fp-sprinkler", "status": "done"},
            {"title": "Releasing sequence", "owner": "fa-releasing", "status": "todo"}]}, agent="lead")
        app.record.open_question(project_id, raised_by="fp-sprinkler", audience="designer",
                                 text="What is the trim volume from the valve sheet?")
        app.record.open_question(project_id, raised_by="fa-releasing", text="Does the owner accept one detection zone?")
        app.record.put_review(project_id, finding_id=fp_finding["id"], agent="fa-releasing", position="object",
                              note="The 2 s releasing time has no basis.")
        app.send_chat("/status")
        text = app.thread_text()
        for needle in (
            "Where Sample data hall DI zone stands",
            "Objective: Design basis for DH-1",
            "✓ Delivery screen (fp-sprinkler)",
            "○ Releasing sequence (fa-releasing)",
            "Sprinkler specialist (fp-sprinkler): done, 1 finding",
            "The team needs from you",
            "1. What is the trim volume from the valve sheet?",
            "Not yet reconciled",
            "fa-releasing objects to fp-sprinkler's finding",
            "Open for the engineer of record (1)",
            "1 finding and 8 current calculation records on the record.",
            "Trace check: not run on the current findings.",
            "Design Basis export waits: The record has findings that no trace check has judged.",
        ):
            self.assertIn(needle, text, needle)
        # The server offers it as an action, and the help lists it.
        from fpfa.web import server

        self.assertIn("status", server.ACTIONS)
        self.assertIn("answer", server.ACTIONS)
        app.send_chat("/help")
        self.assertIn("/status — where this job stands", app.thread_text())

    def test_the_designer_answers_a_team_question_on_the_panel(self):
        app = self._app()
        project_id = self._sample(app)
        asked = app.record.open_question(project_id, raised_by="fp-sprinkler", audience="designer",
                                         text="What is the trim volume from the valve sheet?")
        rfi = app.record.open_question(project_id, raised_by="fa-releasing", text="One detection zone?")
        app._refresh_team()
        self.assertEqual([row["id"] for row in app.team["asks"]], [asked["id"]])
        self.assertEqual([row["id"] for row in app.team["rfis"]], [rfi["id"]])
        self.assertEqual(app.team["attention"], 1)
        self.assertIn("1 needs your answer", app.team["strip"])
        # Nothing typed is not an answer.
        app.answer_question(asked["id"], "   ")
        self.assertEqual(app.notices[-1]["message"], "Type the answer first.")
        app.answer_question(asked["id"], "6.5 gallons, from the submittal.")
        row = next(item for item in app.record.questions(project_id) if item["id"] == asked["id"])
        self.assertEqual((row["status"], row["answer"], row["answered_by"]),
                         ("answered", "6.5 gallons, from the submittal.", "designer"))
        thread = app.thread_text()
        self.assertIn('Answer to the team\'s question "What is the trim volume from the valve sheet?":', thread)
        self.assertIn("6.5 gallons, from the submittal.", thread)
        self.assertIn("Recorded. The lead reads it at the start of its next turn.", thread)
        self.assertEqual(app.team["asks"], [])
        self.assertEqual(app.team["unseen_answers"], 1)
        self.assertEqual([row["by"] for row in app.team["answered"]], ["designer"])
        self.assertEqual(app.chips()[0], {"label": "Continue with my answers",
                                          "action": "I answered your questions on the Team panel. Continue from there."})
        # Twice, or a question that is gone, is a notice and not a crash.
        app.answer_question(asked["id"], "again")
        self.assertEqual(app.notices[-1]["message"], "That question was already answered.")
        app.answer_question("nope", "x")
        self.assertEqual(app.notices[-1]["message"], "That question is not on this job any more.")

        # The chip sends an ordinary message. The lead's turn opens with the answer, and then it is not news.
        play = Play({"lead": [say("Noted the trim volume.")]})
        self._ask(app, play, app.chips()[0]["action"])
        opening = play.of("lead")[0]["user"]
        self.assertIn("The designer answered these on the panel. You have not acted on them yet.", opening)
        self.assertIn("Answer: 6.5 gallons, from the submittal.", opening)
        self.assertEqual(app.team["unseen_answers"], 0)
        self.assertNotIn("Continue with my answers", [chip["label"] for chip in app.chips()])


class ResumeTests(DeskCase):
    def test_a_returning_designer_is_offered_where_things_stand_and_what_is_waiting(self):
        from fpfa.desk import resume_prompts

        self.assertEqual(resume_prompts(None, key_saved=True, busy=False, untouched=True), [])
        quiet = {"people": [], "findings": [], "stale": [], "interrupted": [], "disagreements": [], "conflicts": []}
        self.assertEqual(resume_prompts(quiet, key_saved=True, busy=False, untouched=True), [])
        worked = dict(quiet, people=[{"slug": "fp-sprinkler"}])
        self.assertEqual(resume_prompts(worked, key_saved=True, busy=False, untouched=True), [("Where things stand", "/status")])
        self.assertEqual(resume_prompts(worked, key_saved=True, busy=False, untouched=False), [],
                         "once the designer is typing, a quiet job offers nothing")
        self.assertEqual(resume_prompts(worked, key_saved=True, busy=True, untouched=True), [])
        waiting = dict(worked, stale=[{}], interrupted=["Sprinkler specialist"], disagreements=[{}], unseen_answers=2)
        labels = [label for label, _action in resume_prompts(waiting, key_saved=True, busy=False, untouched=False)]
        self.assertEqual(labels, ["Continue with my answers", "Bring it up to date", "Finish what was interrupted",
                                  "Settle what is open"])
        # Without a key nothing that needs the model is offered. Status still is.
        self.assertEqual(resume_prompts(waiting, key_saved=False, busy=False, untouched=True), [("Where things stand", "/status")])

    def test_closing_and_reopening_a_job_brings_back_its_team_state(self):
        app = self._app()
        project_id = self._sample(app)
        play = Play({
            "lead": [call(use("set_plan", objective="Water delivery for DH-1", steps=[{"title": "Screen", "owner": "fp-sprinkler"}]),
                          use("delegate", specialist="fp-sprinkler", brief="Screen DH-1.")),
                     say("The screen is on the record.")],
            "fp-sprinkler": _screen_steps(app.record, t_release=2, text="Trip to water screens against the 30 s clock"),
        })
        # The helpers read job1 by default; this job has its own id.
        play.scripts["fp-sprinkler"] = [
            lambda _k: call(use("zone_trapped_volume", segments=SEGMENTS)),
            lambda _k: call(use("di_trip_to_water", v_gal=281.3, q_fill_gpm=600, t_detect_s=8, t_release_s=2, basis="FM")),
            lambda _k: call(use("record_finding", text="Trip to water screens against the 30 s clock", label="calculated",
                                supports=[_calc(app.record, "di_trip_to_water", "fp-sprinkler", project_id)["id"]])),
            say("Screen recorded."),
        ]
        self._ask(app, play, "Will DH-1 make the delivery time?")
        self.assertIn("Team\n• fp-sprinkler: 1 finding, 2 calc records", app.thread_text())
        self.assertEqual(app.team["plan"]["objective"], "Water delivery for DH-1")
        self.assertEqual([row["slug"] for row in app.team["people"] if row["slug"] == "fp-sprinkler"], ["fp-sprinkler"])
        self.assertEqual(len(app.team["findings"]), 1)
        before = {key: app.team[key] for key in ("plan", "findings", "strip", "people")}
        data_dir = os.environ["FPFA_DATA_DIR"]
        self.root.destroy()

        # A new window on the same data directory. Nothing is in memory; the record is all there is.
        os.environ["FPFA_DATA_DIR"] = data_dir
        again = self.root.open_desk()
        self.root.update()
        again.select_project(project_id)
        self.root.update()
        self.assertEqual(again.team["plan"], before["plan"])
        self.assertEqual([row["text"] for row in again.team["findings"]], [row["text"] for row in before["findings"]])
        self.assertEqual(again.team["strip"], before["strip"])
        self.assertIn("Will DH-1 make the delivery time?", again.thread_text())
        self.assertEqual([chip["label"] for chip in again.chips()], ["Where things stand"])
        again.send_chat("/status")
        text = again.thread_text()
        self.assertIn("Objective: Water delivery for DH-1", text)
        self.assertIn("Sprinkler specialist (fp-sprinkler): done, 1 finding", text)
        # The next turn's lead is told the same thing, from the record.
        later = Play({"lead": [say("Nothing changed.")]})
        self._ask(again, later, "Remind me where we are.")
        opening = later.of("lead")[0]["user"]
        self.assertIn("Plan. Objective: Water delivery for DH-1", opening)
        self.assertIn("Contributors so far: fp-sprinkler (done, 1 finding)", opening)


class StaleRunTests(DeskCase):
    def test_a_run_on_inputs_that_changed_does_not_govern_the_lead_the_tables_or_the_export(self):
        from fpfa.desk import EXPORT_STALE_RUN, STALE_RUN_NOTE

        app = self._app()
        self._sample(app)
        self.assertEqual(app.run_changes(), [])
        self.assertEqual(app.snapshot()["run_changes"], [])
        first = Play({"lead": [say("Fine.")]})
        self._ask(app, first, "Is the run current?")
        self.assertIn("A tool plan already ran for this zone.", first.of("lead")[0]["user"])
        self.assertIn("Governing t_total text: 38.1.", first.of("lead")[0]["user"])

        # The designer changes the fill flow on the form after the run.
        app.patch_form({"q_fill": "750"})
        app.save_current()
        self.assertEqual(app.run_changes(), ["q_fill_gpm"])
        self.assertEqual(app.snapshot()["run_changes"], ["q_fill_gpm"])
        self.assertIn("Bring it up to date", [chip["label"] for chip in app.chips()])
        self.assertTrue(any(row["kind"] == "calc" for row in app.team["stale"]))
        self.assertIn("q_fill_gpm changed from 600 gpm to 750 gpm", app.team["changes"][0])

        # The lead is no longer handed the old run's figures as governing. It is told they are out of date.
        second = Play({"lead": [say("The run is out of date.")]})
        self._ask(app, second, "What is t_total now?")
        opening = second.of("lead")[0]["user"]
        self.assertNotIn("Governing t_total text", opening)
        self.assertNotIn("A tool plan already ran for this zone.", opening)
        self.assertIn(STALE_RUN_NOTE.format(names="q_fill_gpm", section="21 13 19"), opening)
        self.assertIn("Inputs changed after work was done on them:", opening)
        self.assertIn("Out of date. Their basis changed. Do not quote them", opening)

        # Neither export is written from the old run.
        app.export_docx()
        self.assertEqual(app.notices[-1]["message"], EXPORT_STALE_RUN.format(names="q_fill_gpm", section="21 13 19"))
        with self.assertRaises(RuntimeError) as caught:
            app.export_to(Path(tempfile.mkdtemp()) / "section.docx", create=lambda **_k: None)
        self.assertIn("The zone form changed after the last run (q_fill_gpm).", str(caught.exception))
        self.assertIn("out of date", app.design_basis_ready())
        app.send_chat("/status")
        self.assertIn("These figures are from a run before the form changed (q_fill_gpm). Run the zone again.", app.thread_text())

        # Running the zone again brings everything back.
        app.start_zone_run()
        self._settle(app)
        self.assertEqual(app.run_changes(), [])
        self.assertEqual(app.team["stale"], [])
        self.assertEqual(app.design_basis_ready(), "")
        third = Play({"lead": [say("Current again.")]})
        self._ask(app, third, "And now?")
        self.assertIn("A tool plan already ran for this zone.", third.of("lead")[0]["user"])
        self.assertIn("Governing t_total text: 32.5.", third.of("lead")[0]["user"])


class ReplyAuditTests(unittest.TestCase):
    def _seeded(self):
        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        return record, di, basis

    def test_a_figure_is_found_where_the_lead_could_have_read_it(self):
        from fpfa.reply_audit import audit, lines

        record, _di, _basis = self._seeded()
        snapshot = record.snapshot("job1")
        clean = audit("Zone total is 281.3 gal. Fill takes 28.1 s at 600 gpm, so t_total is 38.1 s against 30 s. "
                      "Demand is 640 gpm for 60 min, 38,400 gal. The area increase is 30 percent.", snapshot)
        self.assertEqual((clean["unfound"], clean["stale"]), ([], []))
        self.assertEqual(clean["figures"], 9)
        self.assertEqual(lines(clean), [])
        # Rounded the way a person says it is still the record's figure.
        self.assertEqual(audit("About 281 gal, and 38 s.", snapshot)["unfound"], [])
        # Worked out by the lead, or misremembered: on no row at all.
        bad = audit("At 925 gpm the fill would take 18.2 s, so t_total is 28.2 s and the zone passes.", snapshot)
        self.assertEqual(bad["unfound"], ["925 gpm", "18.2 s", "28.2 s"])
        self.assertEqual(lines(bad), [
            "- figures in this reply the application could not find on the record or in anything the lead read: "
            "925 gpm, 18.2 s, 28.2 s. Treat them as unverified."])
        # The lookup is by number and kind of unit: 900 is on the record as a pipe length, and a length does
        # not back a flow. A figure that is found is only known to match a number the designer can go and look at.
        self.assertEqual(audit("At 900 gpm it would pass.", snapshot)["unfound"], ["900 gpm"])
        self.assertEqual(audit("The fill flow is 600 gpm.", snapshot)["unfound"], [])
        self.assertEqual(audit("The zone holds 600 gal.", snapshot)["unfound"], ["600 gal"], "600 is a flow on this record")
        # Section numbers, counts, and ids are not figures.
        self.assertEqual(audit("NFPA 13-2025 §8.3.2.3.1.1 and Table 19.2.3.1.2; 6 true rows of 32.", snapshot)["figures"], 0)
        self.assertEqual(audit("", snapshot), {"figures": 0, "unfound": [], "stale": [], "wording": []})

    def test_what_the_lead_read_this_turn_and_what_the_designer_said_are_sources(self):
        from fpfa.reply_audit import audit

        record, _di, _basis = self._seeded()
        snapshot = record.snapshot("job1")
        reply = "You said 750 gpm. The skill puts the dry-pipe criterion at 60 seconds, and the note allows 45 psi."
        self.assertEqual(audit(reply, snapshot)["unfound"], ["750 gpm", "45 psi"])   # 60 is on the hose table's record
        found = audit(
            reply, snapshot,
            said=["Our pump test gave 750 gpm."],
            tool_calls=[{"name": "read_skill", "output": {"slug": "x", "text": "Hold the gauge at 45 psi."}, "is_error": False},
                        {"name": "read_skill", "output": {"error": "also 99 psi"}, "is_error": True}],
        )
        self.assertEqual(found["unfound"], [])
        self.assertEqual(audit("The pack says 12 psi.", snapshot, pack_text="Low-pressure switch at 12 psi decreasing.")["unfound"], [])
        # A figure the lead repeats from its own earlier reply is not news, unless it was flagged then.
        earlier = ["Earlier I said 77 gpm."]
        self.assertEqual(audit("As before, 77 gpm.", snapshot, earlier_replies=earlier)["unfound"], [])
        self.assertEqual(audit("As before, 77 gpm.", snapshot, earlier_replies=earlier, flagged_before=["77 gpm"])["unfound"],
                         ["77 gpm"])

    def test_a_figure_from_an_out_of_date_calculation_is_called_out(self):
        from fpfa.reply_audit import audit, lines
        from test_coherence import _change

        record, di, basis = self._seeded()
        _change(record, "q_fill_gpm", 750)
        result = audit("t_total is 38.1 s and the fill takes 28.1 s. The zone total is 281.3 gal.", record.snapshot("job1"))
        self.assertEqual(result["stale"], ["38.1 s", "28.1 s"])
        self.assertEqual(result["unfound"], [], "the volume did not use the fill flow and is still current")
        self.assertEqual(lines(result), [
            "- figures in this reply that the record now holds only on out-of-date rows: 38.1 s, 28.1 s. "
            "An input changed after they were written, or the finding that carried them was replaced or withdrawn. "
            "They are not the current basis. Do not use them as current."])
        _run_plan(record, dict(di, q_fill_gpm=750), basis)
        self.assertEqual(audit("t_total is 32.5 s.", record.snapshot("job1"))["stale"], [])

    def test_the_note_goes_under_the_reply_and_onto_the_record(self):
        from fpfa.team import team_summary

        self.assertEqual(team_summary({"text": "x"}, {"figures": 2, "unfound": [], "stale": []}), "")
        alone = team_summary({"text": "x"}, {"figures": 1, "unfound": ["42 s"], "stale": []})
        self.assertTrue(alone.startswith("**Figures in this reply**\n- figures in this reply the application could not find"))
        both = team_summary({"delegations": [{"specialist": "fp-sprinkler", "findings": [1]}]},
                            {"figures": 2, "unfound": ["42 s"], "stale": ["38.1 s"]})
        self.assertIn("- fp-sprinkler: 1 finding", both)
        self.assertIn("holds only on out-of-date rows: 38.1 s.", both)
        self.assertIn("could not find on the record or in anything the lead read: 42 s.", both)
        self.assertTrue(both.endswith("Details are on the Team tab."))


class ReplyAuditWindowTests(DeskCase):
    def test_a_reply_with_a_figure_the_lead_worked_out_is_marked_in_the_thread(self):
        from fpfa.reply_audit import AUDIT_EVENT, flagged_before

        app = self._app()
        project_id = self._sample(app)
        good = Play({"lead": [say("The zone total is 281.3 gal and t_total is 38.1 s against the 30 s screen.")]})
        self._ask(app, good, "What are the two governing figures?")
        self.assertNotIn("Figures in this reply", app.thread_text())
        bad = Play({"lead": [say("Splitting the zone in two gives 140.7 gal each and about 24.1 s.")]})
        self._ask(app, bad, "What if we split it?")
        thread = app.thread_text()
        self.assertIn("Figures in this reply", thread)
        self.assertIn("could not find on the record or in anything the lead read: 140.7 gal, 24.1 s. Treat them as unverified.", thread)
        self.assertEqual(flagged_before(app.record, project_id), ["140.7 gal", "24.1 s"])
        self.assertEqual(len(app.record.events_by_kind(project_id, (AUDIT_EVENT,))), 2)
        # Saying it again next turn does not make it found.
        again = Play({"lead": [say("As I said, 140.7 gal each.")]})
        self._ask(app, again, "Say that again?")
        self.assertEqual(app.thread_text().count("could not find on the record"), 2)


class RetryTests(unittest.TestCase):
    def _client(self, errors, reply=None):
        from fpfa.claude_client import AnthropicMessages

        client = AnthropicMessages("sk-ant-test-not-sent")
        queue = list(errors)

        class Messages:
            calls = 0
            kwargs = None

            def create(inner, **kwargs):
                Messages.calls += 1
                Messages.kwargs = kwargs
                if queue:
                    raise queue.pop(0)
                return reply or SimpleNamespace(content=[])

        client._client = SimpleNamespace(messages=Messages())
        return client, Messages

    def _error(self, status, retry_after=None):
        class Busy(Exception):
            status_code = status

        exc = Busy("busy")
        if retry_after is not None:
            exc.response = SimpleNamespace(headers={"retry-after": retry_after})
        return exc

    def test_the_wait_is_the_apis_when_it_names_one(self):
        from fpfa.claude_client import RETRY_WAITS, retry_wait

        self.assertEqual(retry_wait(self._error(429, "7"), 0), 7.0)
        # Whole: the API says an attempt before its retry-after fails. A wait longer than the client waits out
        # by itself stops the request instead (test_acceptance_report_030.ApiClientTests).
        self.assertEqual(retry_wait(self._error(429, "600"), 0), 600.0)
        self.assertEqual(retry_wait(self._error(429, "soon"), 1), RETRY_WAITS[1])
        self.assertEqual([retry_wait(self._error(529), n) for n in range(6)], [2.0, 4.0, 8.0, 16.0, 16.0, 16.0])
        self.assertEqual(retry_wait(RuntimeError("no response at all"), 0), 2.0)

    def test_a_refused_request_is_sent_again_and_the_window_is_told(self):
        from fpfa.claude_client import RETRY_ATTEMPTS
        from fpfa.desk import describe_activity

        client, messages = self._client([self._error(429, "3"), self._error(529)])
        heard = []
        client.on_retry = heard.append
        with patch("fpfa.claude_client.time.sleep") as sleep:
            client.create(max_tokens=8, messages=[])
        self.assertEqual(messages.calls, 3)
        self.assertEqual([item.args[0] for item in sleep.call_args_list], [3.0, 4.0])
        self.assertEqual([(item["attempt"], item["of"], item["status"]) for item in heard], [(2, RETRY_ATTEMPTS, 429), (3, RETRY_ATTEMPTS, 529)])
        self.assertEqual(describe_activity(heard[0]), f"waiting to try again (attempt 2 of {RETRY_ATTEMPTS})")
        # It gives up after the last attempt and raises what the API said.
        client, messages = self._client([self._error(529)] * 9)
        with patch("fpfa.claude_client.time.sleep"):
            with self.assertRaises(Exception) as caught:
                client.create(max_tokens=8, messages=[])
        self.assertEqual(getattr(caught.exception, "status_code", None), 529)
        self.assertEqual(messages.calls, RETRY_ATTEMPTS)
        # A request the API will never accept is not sent twice.
        client, messages = self._client([self._error(400)])
        with patch("fpfa.claude_client.time.sleep") as sleep:
            with self.assertRaises(Exception):
                client.create(max_tokens=8, messages=[])
        self.assertEqual(messages.calls, 1)
        sleep.assert_not_called()

    def test_effort_is_sent_only_when_the_owner_sets_it(self):
        from fpfa.claude_client import EFFORT_ENV, AnthropicMessages, configured_effort

        self.assertEqual(configured_effort(""), "")
        self.assertEqual(configured_effort(" High "), "high")
        self.assertEqual(configured_effort("turbo"), "")
        with patch.dict(os.environ, {EFFORT_ENV: ""}):
            client, messages = self._client([])
            client.effort = configured_effort()
            client.create(max_tokens=8, messages=[])
            self.assertNotIn("output_config", messages.kwargs)
        with patch.dict(os.environ, {EFFORT_ENV: "high"}):
            plain = AnthropicMessages("sk-ant-test-not-sent")
            self.assertEqual(plain.effort, "high")
            a = plain._prepare({"max_tokens": 8, "messages": [], "system": "s", "tools": [{"name": "t"}]})
            b = plain._prepare({"max_tokens": 8, "messages": [], "system": "s", "tools": [{"name": "t"}]})
            self.assertEqual(a["output_config"], {"effort": "high"})
            self.assertEqual(a, b, "the streamed request and the plain one are prepared by the same code")
            for banned in ("temperature", "top_p", "top_k", "tool_choice", "thinking"):
                self.assertNotIn(banned, a)
        self.assertEqual(AnthropicMessages("sk-ant-test-not-sent", effort="low").effort, "low")


class UsageTimeTests(unittest.TestCase):
    def test_the_report_prints_how_long_each_context_took_and_the_job_in_all(self):
        from fpfa.usage_report import clock, job_seconds, report_text, usage_events

        record = _record()
        record.ensure_project("p1", "Timed")
        use_row = {"rounds": 2, "input_tokens": 1000, "output_tokens": 100}
        record.log_event("p1", "consult", {"from": "fp-sprinkler", "to": "fa-releasing", "usage": use_row, "seconds": 21.4}, agent="fp-sprinkler")
        record.log_event("p1", "delegation", {"specialist": "fp-sprinkler", "usage": use_row, "seconds": 95.0}, agent="lead")
        record.log_event("p1", "turn", {"usage": use_row, "delegations": 1, "checks": 1, "cancelled": False, "seconds": 188.2}, agent="lead")
        record.log_event("p1", "record_check", {"usage": use_row, "rows": [], "seconds": 12.0}, agent="qa-specialist")
        record.log_event("p1", "turn", {"usage": use_row, "delegations": 0, "checks": 0, "cancelled": False}, agent="lead")
        rows = usage_events(record, "p1")
        self.assertEqual(job_seconds(rows), 200.2, "the delegation and the consult are inside the turn")
        self.assertEqual([clock(value) for value in (0, 42.4, 60, 188.2)], ["", "42 s", "1 min 00 s", "3 min 08 s"])
        text = report_text(record, "p1")
        self.assertIn("within that: fp-sprinkler asked fa-releasing", text)
        self.assertIn("  21 s   (inside the turn above, not added)", text)
        self.assertIn("  3 min 08 s", text)
        self.assertIn("trace check", text)
        self.assertIn("Time on the model: 3 min 20 s, the wall time of the turns, narrations, and checks that recorded one.", text)
        self.assertIn("Job total over 3 model contexts", text)


class TeamViewTests(unittest.TestCase):
    def test_the_panel_view_carries_what_each_specialist_found_and_how_far_it_was_taken(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import check_record, export_reason
        from fpfa.team_panel import team_view
        from test_checker import yes_to_everything

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        self.assertEqual(team_view(None)["findings"], [])
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        record.set_agent("job1", name="Sprinkler specialist", role_slug="fp-sprinkler", status="done")
        record.set_agent("job1", name="Releasing specialist", role_slug="fa-releasing", status="interrupted")
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "basis": "FM"})
        cap = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                             "note": "DI at or under 500 gal needs no delivery-time proof"})
        on_calc = fp.execute("record_finding", {"text": "t_total is 38.1 s against a 30 s limit", "label": "calculated",
                                                "supports": [screen["record_id"], record.givens("job1")["t_release_s"]["id"]]})
        on_pack = fp.execute("record_finding", {"text": "A double-interlock zone up to 500 gal needs no delivery-time proof",
                                                "label": "CODE", "supports": [cap["id"]]})
        bare = fa.execute("record_finding", {"text": "One detection zone releases", "label": "PRACTICE"})
        fa.execute("review_finding", {"id": on_calc["id"], "position": "object", "note": "The 2 s has no stated basis."})
        fa.execute("review_finding", {"id": on_pack["id"], "position": "agree"})
        asked = record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing", kind="consult", brief="Releasing time?")
        record.set_handoff("job1", asked["id"], status="returned", result="2 s.", by="fa-releasing")
        check_record(REPO, record, "job1", yes_to_everything)
        snapshot = record.snapshot("job1")
        view = team_view(snapshot, export_reason=export_reason(snapshot))
        rows = {row["id"]: row for row in view["findings"]}
        self.assertEqual((rows[on_pack["id"]]["tier"], rows[on_pack["id"]]["verdict"]), ("source", "Supported"))
        self.assertTrue(rows[on_pack["id"]]["checked_against"][0].startswith("content-pack note: NFPA 13-2025 §8.3.2.3.1.1 (corpus/"))
        self.assertTrue(rows[on_pack["id"]]["rests_on"][0].startswith("cite NFPA 13-2025 §8.3.2.3.1.1: DI at or under 500 gal"))
        self.assertEqual(rows[on_pack["id"]]["reviews"], [{"by": "fa-releasing", "position": "agrees", "note": "", "status": "", "how": ""}])
        # Supported by the check and still held open by the other specialist's objection.
        self.assertEqual(rows[on_calc["id"]]["tier"], "open")
        self.assertEqual(rows[on_calc["id"]]["why"], ["fa-releasing objects: The 2 s has no stated basis."])
        self.assertEqual(rows[on_calc["id"]]["rests_on"][0], f"calculation di_trip_to_water [{screen['record_id']}]")
        self.assertTrue(rows[on_calc["id"]]["rests_on"][1].startswith("project input t_release_s: 2 s ["))
        self.assertEqual(rows[bare["id"]]["tier"], "open")
        self.assertEqual({row["tier"]: row["count"] for row in view["tiers"]},
                         {"source": 1, "checker": 0, "reviewed": 0, "stated": 0, "open": 2})
        self.assertEqual([(row["by"], row["author"], row["status"]) for row in view["disagreements"]],
                         [("fa-releasing", "fp-sprinkler", "open")])
        self.assertEqual(view["interrupted"], ["Releasing specialist"])
        self.assertEqual([row["kind_word"] for row in view["handoffs"]], ["question"])
        self.assertEqual(view["attention"], 1)
        self.assertIn("fp-sprinkler done", view["strip"])
        self.assertIn("3 findings", view["strip"])
        self.assertIn("1 disagreement open", view["strip"])
        self.assertEqual(view["export"], {"ready": True, "reason": ""})
        self.assertIn("q_fill_gpm", [row["name"] for row in view["inputs"]])
        self.assertEqual(view["not_standard"], "The standards were not opened. Engineer-of-record review still applies.")
        # The older text fields the sidebar reads are still there.
        self.assertIn("✓ Sprinkler specialist (fp-sprinkler) done · 2 findings", view["roster"])
        self.assertTrue(view["check_line"].startswith("Trace check: 2 of 3 findings"))
        # An objection that ended is kept as how the team reconciled.
        fp.execute("record_finding", {"text": "t_total is 38.1 s against a 30 s limit, on the form's 2 s releasing time",
                                      "label": "calculated", "supports": [screen["record_id"]], "replaces": on_calc["id"]})
        after = team_view(record.snapshot("job1"))
        self.assertEqual(after["disagreements"], [])
        self.assertEqual([(row["by"], row["author"]) for row in after["settled"]], [("fa-releasing", "fp-sprinkler")])
        self.assertIn("The finding was revised by fp-sprinkler", after["settled"][0]["how"])
        self.assertTrue(_finding(record, "on the form's 2 s releasing time"))


if __name__ == "__main__":
    unittest.main()
