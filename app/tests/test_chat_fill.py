"""An input the designer states in chat, on the Inputs tab: filled in as the lead records it, listed on a card
under the reply with Show and Undo, marked on its field, and, in ask-first mode, written only on Apply.

SIMULATED. Every model call is a scripted lead (test_team_protocol.Play): these tests show what the
application does with a set_input call, never whether a live model makes one. No display, no network.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402
from test_team_protocol import Play, call, say, use  # noqa: E402

MESSAGE = ("New job. The AHJ is the City of Irvine, and the insurer is FM Global. "
           "What do you still need from me?")
AHJ = use("set_input", name="ahj", value="City of Irvine", why="“The AHJ is the City of Irvine.”")
INSURER = use("set_input", name="insurer", value="FM Global", why="“the insurer is FM Global”")


def client_for(play):
    class Client:
        def __init__(self, _key):
            pass

        def create(self, **kwargs):
            return play(**kwargs)

    return Client


class ChatFillCase(unittest.TestCase):
    def setUp(self):
        data = Path(tempfile.mkdtemp(prefix="fpfa-chat-fill-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config

        write_config({"key_backend": "file"})
        save_api_key("sk-ant-local-test")
        self.loop = Loop()
        self.addCleanup(self.loop.destroy)
        self.app = self.loop.open_desk()
        self.loop.update()

    def play(self, *lead_steps) -> Play:
        """The lead's script, with the stand-in client in place for the rest of the test (the worker builds its own)."""
        play = Play({"lead": list(lead_steps)})
        patcher = patch("fpfa.desk.AnthropicMessages", client_for(play))
        patcher.start()
        self.addCleanup(patcher.stop)
        return play

    def settle(self, timeout: float = 15.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.pump()
            if not self.app._pending_here():
                self.app.pump()
                return
            time.sleep(0.02)
        self.fail("the turn did not finish")

    def turn(self, text: str = MESSAGE) -> dict:
        self.app.send_chat(text)
        self.settle()
        return self.app.chat_log[-1]

    def card(self) -> list[dict]:
        return self.app.chat_log[-1].get("inputs") or []

    def row(self, name: str) -> dict:
        return next(item for item in self.card() if item["name"] == name)


class FilledAsRecorded(ChatFillCase):
    def test_the_form_takes_the_value_when_set_input_finishes_not_when_the_reply_ends(self):
        gate = threading.Event()

        def held(_kwargs):
            gate.wait(10)
            return say("Recorded the AHJ.")

        self.play(call(AHJ), held)
        self.app.send_chat(MESSAGE)
        deadline = time.time() + 10
        while self.app.ahj.get() != "City of Irvine" and time.time() < deadline:
            self.app.pump()
            time.sleep(0.02)
        try:
            self.assertEqual(self.app.ahj.get(), "City of Irvine")
            self.assertTrue(self.app._pending_here(), "the lead is still working")
            state = self.app.snapshot()
            self.assertEqual(state["form"]["marks"]["ahj"]["was"], "blank")
            self.assertEqual(state["pending"]["fills"], [{"label": "AHJ", "now": "City of Irvine", "field": "ahj"}])
        finally:
            gate.set()
        self.settle()
        self.assertEqual([item["name"] for item in self.card()], ["ahj"], "one row, from the fill made mid-turn")

    def test_the_card_says_each_field_in_the_forms_words_and_keeps_the_values_for_undo_to_itself(self):
        self.play(call(AHJ, INSURER), say("Recorded both."))
        turn = self.turn()
        ahj, insurer = self.row("ahj"), self.row("insurer")
        self.assertEqual((ahj["label"], ahj["was"], ahj["now"], ahj["state"]), ("AHJ", "blank", "City of Irvine", "applied"))
        self.assertEqual((insurer["label"], insurer["was"], insurer["now"]), ("Insurer", "FM (starting value)", "FM Global"))
        self.assertTrue(ahj["quoted"], "the lead's reason is found in the designer's message")
        shown = self.app.snapshot()["thread"]["turns"][-1]["inputs"]
        for item in shown:
            for private in ("was_raw", "now_raw", "value_text", "source"):
                self.assertNotIn(private, item)
        # The Team block no longer lists the inputs: the card does.
        self.assertNotIn("input ahj", turn["text"])
        text = self.app.thread_text()
        self.assertIn("Filled in on the Inputs tab\nAHJ: blank → City of Irvine\nInsurer: FM (starting value) → FM Global", text)

    def test_a_reason_not_found_in_the_designers_words_is_the_leads_note(self):
        self.play(call(use("set_input", name="ahj", value="City of Irvine", why="AHJ given as Irvine")), say("Done."))
        self.turn()
        self.assertFalse(self.row("ahj")["quoted"])
        self.assertFalse(self.app.snapshot()["form"]["marks"]["ahj"]["quoted"])

    def test_the_record_says_the_designer_gave_it_in_chat(self):
        self.play(call(AHJ), say("Done."))
        self.turn()
        row = self.app.record.givens(self.app.project["id"])["ahj"]
        self.assertEqual((row["value"], row["agent"]), ("City of Irvine", "lead"))
        self.assertTrue(row["source"].startswith("designer, in chat: "))

    def test_typing_over_a_filled_field_takes_its_mark_away_and_makes_the_value_the_designers(self):
        self.play(call(AHJ), say("Done."))
        self.turn()
        self.app.patch_form({"ahj": "City of Irvine Fire Department"})
        self.assertNotIn("ahj", self.app.snapshot()["form"]["marks"])
        self.app.save_current()
        row = self.app.record.givens(self.app.project["id"])["ahj"]
        self.assertEqual((row["value"], row["agent"]), ("City of Irvine Fire Department", "job form"))
        self.assertNotIn("ahj", self.app.snapshot()["form"]["marks"])

    def test_a_job_opened_again_keeps_its_marks_without_the_highlight(self):
        self.play(call(AHJ), say("Done."))
        self.turn()
        job = self.app.project["id"]
        self.assertGreater(self.app.form_marks()["ahj"]["fill"], 0)
        self.app.new_job()
        self.assertEqual(self.app.form_marks(), {})
        self.app.select_project(job)
        mark = self.app.form_marks()["ahj"]
        self.assertEqual((mark["fill"], mark["was"], mark["quoted"]), (0, "blank", True))

    def test_the_next_turn_tells_the_lead_what_became_of_each_row(self):
        play = self.play(call(AHJ, INSURER), say("Recorded both."), say("Noted."))
        self.turn()
        self.app.undo_fill(self.app.chat_log[-1]["job_id"], "insurer")
        self.turn("Thanks. What next?")
        opening = play.of("lead")[-1]["user"]
        self.assertIn("[Inputs card under that reply, written by the application: AHJ: blank -> City of Irvine "
                      "(on the form); Insurer: FM (starting value) -> FM Global (undone by the designer)]", opening)


class TypingDuringTheTurn(ChatFillCase):
    def test_a_field_the_designer_is_typing_in_keeps_their_value_and_their_edit_wins(self):
        gate, reply = threading.Event(), threading.Event()

        def first(_kwargs):
            gate.wait(10)
            return call(INSURER)

        def last(_kwargs):
            reply.wait(10)
            return say("Recorded the insurer.")

        self.play(first, last)
        self.app.send_chat(MESSAGE)
        # The designer types in the field while the lead is working, and the lead then records the same field.
        self.app.patch_form({"insurer": "Zurich"})
        gate.set()
        try:
            deadline = time.time() + 10
            while not self.app._job_fills and time.time() < deadline:
                self.app.pump()
                time.sleep(0.02)
            self.assertTrue(self.app._job_fills, "the lead's value was taken mid-turn")
            self.assertEqual(self.app.insurer.get(), "Zurich", "the field being typed in keeps its value")
            self.assertNotIn("insurer", self.app.form_marks())
        finally:
            reply.set()
        self.settle()
        self.assertEqual(self.app.insurer.get(), "Zurich")
        given = self.app.record.givens(self.app.project["id"])["insurer"]
        self.assertEqual((given["value"], given["agent"]), ("Zurich", "job form"))
        history = [row["value"] for row in self.app.record.facts(self.app.project["id"], "basis", include_superseded=True)
                   if row["key"] == "insurer"]
        self.assertIn("FM Global", history, "the lead's row stays as history")
        self.assertEqual(self.row("insurer")["state"], "overtaken")
        self.assertNotIn("insurer", self.app.form_marks())

    def test_typing_the_same_value_the_lead_records_is_no_conflict(self):
        gate, reply = threading.Event(), threading.Event()

        def first(_kwargs):
            gate.wait(10)
            return call(INSURER)

        def last(_kwargs):
            reply.wait(10)
            return say("Recorded the insurer.")

        self.play(first, last)
        self.app.send_chat(MESSAGE)
        self.app.patch_form({"insurer": "FM Global"})
        gate.set()
        try:
            deadline = time.time() + 10
            while not self.app._job_fills and time.time() < deadline:
                self.app.pump()
                time.sleep(0.02)
        finally:
            reply.set()
        self.settle()
        self.assertEqual(self.row("insurer")["state"], "applied")

    def test_a_form_that_does_not_parse_is_left_alone_until_the_reply_ends(self):
        gate = threading.Event()

        def held(_kwargs):
            gate.wait(10)
            return say("Recorded the AHJ.")

        self.play(call(AHJ), held)
        self.app.send_chat(MESSAGE)
        self.app.patch_form({"q_fill": "7,5,0"})
        try:
            deadline = time.time() + 2
            while time.time() < deadline:
                self.app.pump()
                time.sleep(0.02)
            self.assertTrue(self.app._pending_here())
            self.assertEqual(self.app.q_fill.get(), "7,5,0", "what was typed is kept")
            self.assertEqual(self.app.ahj.get(), "", "the fill waits for the reply's end")
        finally:
            gate.set()
        self.settle()


class UndoTests(ChatFillCase):
    def test_undo_of_a_value_the_designer_typed_puts_it_back_as_theirs(self):
        self.app.patch_form({"insurer": "Zurich"})
        self.app.save_current()
        self.play(call(INSURER), say("Done."))
        self.turn()
        self.assertEqual(self.row("insurer")["was"], "Zurich")
        self.app.undo_fill(self.app.chat_log[-1]["job_id"], "insurer")
        given = self.app.record.givens(self.app.project["id"])["insurer"]
        self.assertEqual((given["value"], given["source"]), ("Zurich", "job form"))

    def test_undo_puts_back_the_old_value_and_who_gave_it_and_the_record_keeps_both(self):
        self.play(call(INSURER), say("Done."))
        self.turn()
        job = self.app.chat_log[-1]["job_id"]
        self.app.undo_fill(job, "insurer")
        self.assertEqual(self.app.insurer.get(), "FM")
        self.assertEqual(self.row("insurer")["state"], "undone")
        self.assertNotIn("insurer", self.app.form_marks())
        project = self.app.project["id"]
        given = self.app.record.givens(project)["insurer"]
        self.assertEqual(given["value"], "FM")
        # It goes back as what it was: the form's starting value, which the designer has not confirmed.
        self.assertEqual(given["source"], "job form (starting value, not confirmed by the designer)")
        history = [row["value"] for row in self.app.record.facts(project, "basis", include_superseded=True)
                   if row["key"] == "insurer"]
        self.assertIn("FM Global", history, "the lead's row stays as history")
        self.assertIn("Undone: Insurer is back to FM (starting value).", self.app.status.get())
        # Twice is once.
        self.app.undo_fill(job, "insurer")
        self.assertEqual(self.app.insurer.get(), "FM")

    def test_a_field_typed_over_since_is_left_alone(self):
        self.play(call(INSURER), say("Done."))
        self.turn()
        self.app.patch_form({"insurer": "Zurich"})
        self.app.undo_fill(self.app.chat_log[-1]["job_id"], "insurer")
        self.assertEqual(self.app.insurer.get(), "Zurich")
        self.assertEqual(self.row("insurer")["state"], "overtaken")

    def test_undo_of_a_basis_field_that_was_blank_takes_it_off_the_record(self):
        self.play(call(AHJ), say("Done."))
        self.turn()
        self.app.undo_fill(self.app.chat_log[-1]["job_id"], "ahj")
        self.assertEqual(self.app.ahj.get(), "")
        self.assertNotIn("ahj", self.app.record.givens(self.app.project["id"]))


class RunUsedTheOldValue(ChatFillCase):
    def test_a_number_the_last_run_used_says_the_results_no_longer_describe_the_form(self):
        self.app.ask_claude.set(False)
        self.app.start_sample_di()
        self.app.pump()
        self.play(call(use("set_input", name="q_fill_gpm", value="750", why="“750 gpm at the riser”")), say("Done."))
        self.turn("The pump test came back at 750 gpm at the riser. Use that.")
        row = self.row("q_fill_gpm")
        self.assertEqual((row["label"], row["was"], row["now"]), ("Fill flow", "600 gpm", "750 gpm"))
        self.assertTrue(self.shown("q_fill_gpm")["stale_run"])
        self.assertEqual(self.app.q_fill.get(), "750.0")
        self.app.undo_fill(self.app.chat_log[-1]["job_id"], "q_fill_gpm")
        self.assertEqual(float(self.app.q_fill.get()), 600.0)
        self.assertEqual(self.app.run_changes(), [], "the form is back to what the run used")
        self.assertEqual(self.app.record.givens(self.app.project["id"])["q_fill_gpm"]["source"], "sample data",
                         "the sample's value goes back as the sample's")
        self.assertFalse(self.shown("q_fill_gpm")["stale_run"], "an undone row says nothing about the run")

    def test_the_note_goes_when_the_zone_is_run_on_the_new_value(self):
        self.app.ask_claude.set(False)
        self.app.start_sample_di()
        self.app.pump()
        self.play(call(use("set_input", name="q_fill_gpm", value="750", why="“750 gpm at the riser”")), say("Done."))
        self.turn("The pump test came back at 750 gpm at the riser. Use that.")
        self.assertTrue(self.shown("q_fill_gpm")["stale_run"])
        self.app.run_zone()
        self.settle(30)
        self.assertEqual(self.app.run_changes(), [])
        self.assertFalse(self.shown("q_fill_gpm")["stale_run"], "the run used the new value")
        self.assertNotIn("stale_run", self.app.chat_log[-2 if self.app.chat_log[-1].get("inputs") is None else -1]
                         .get("inputs", [{}])[0], "the note is read from the run, never stored")

    def shown(self, name: str) -> dict:
        turn = next(turn for turn in reversed(self.app.snapshot()["thread"]["turns"]) if turn.get("inputs"))
        return next(item for item in turn["inputs"] if item["name"] == name)


class AskFirst(ChatFillCase):
    def setUp(self):
        super().setUp()
        self.app.set_fill_mode("ask")

    def test_set_input_proposes_and_writes_nothing(self):
        play = self.play(call(AHJ), say("The AHJ waits for your OK."))
        self.turn()
        self.assertEqual(self.app.ahj.get(), "")
        self.assertNotIn("ahj", self.app.record.givens(self.app.project["id"]))
        row = self.row("ahj")
        self.assertEqual((row["state"], row["was"], row["now"], row["quoted"]), ("proposed", "blank", "City of Irvine", True))
        self.assertEqual(self.app.form_marks(), {})
        told = str(play.of("lead")[-1]["messages"])
        self.assertIn("Proposed, not recorded.", told)
        self.assertIn("Inputs wait for your OK", self.app.status.get())

    def test_apply_writes_the_row_as_the_designers_from_the_chat_and_fills_the_form(self):
        self.play(call(AHJ, INSURER), say("Both wait for your OK."))
        self.turn()
        job = self.app.chat_log[-1]["job_id"]
        self.app.apply_fill(job, "ahj")
        self.assertEqual(self.app.ahj.get(), "City of Irvine")
        given = self.app.record.givens(self.app.project["id"])["ahj"]
        self.assertEqual(given["agent"], "designer")
        self.assertTrue(given["source"].startswith("designer, in chat: "))
        self.assertTrue(given["source"].endswith("(applied by the designer)"))
        self.assertEqual(self.row("ahj")["state"], "applied")
        self.assertEqual(self.row("insurer")["state"], "proposed")
        self.assertIn("ahj", self.app.form_marks())
        self.assertEqual(self.app.form_marks()["ahj"]["why"], "“The AHJ is the City of Irvine.”")
        # Applied, it can be undone like any fill.
        self.app.undo_fill(job, "ahj")
        self.assertEqual(self.app.ahj.get(), "")
        # Apply with no name takes every row still waiting.
        self.app.apply_fill(job, "")
        self.assertEqual(self.app.insurer.get(), "FM Global")

    def test_skip_leaves_the_record_and_the_form_alone_and_the_lead_hears_it(self):
        play = self.play(call(AHJ), say("Waits for your OK."), say("Understood."))
        self.turn()
        self.app.skip_fill(self.app.chat_log[-1]["job_id"], "ahj")
        self.assertEqual(self.row("ahj")["state"], "skipped")
        self.assertEqual(self.app.ahj.get(), "")
        self.assertNotIn("ahj", self.app.record.givens(self.app.project["id"]))
        self.turn("Leave the AHJ for now.")
        self.assertIn("AHJ: blank -> City of Irvine (skipped by the designer; not applied)", play.of("lead")[-1]["user"])

    def test_the_setting_is_kept_and_an_unknown_one_is_ignored(self):
        self.assertEqual(self.app.settings_view()["fill_from_chat"], "ask")
        self.app.set_fill_mode("sometimes")
        self.assertEqual(self.app.settings_view()["fill_from_chat"], "ask")
        self.app.set_fill_mode("auto")
        self.assertEqual(self.app.settings_view()["fill_from_chat"], "auto")


class TheQuoteCheck(unittest.TestCase):
    def test_the_designers_words_are_found_whatever_the_quote_marks_case_and_spacing(self):
        from fpfa.desk import said_by_designer

        said = [MESSAGE]
        self.assertTrue(said_by_designer("“The AHJ is the City of Irvine.”", said))
        self.assertTrue(said_by_designer('"the  insurer is FM GLOBAL"', said))
        self.assertFalse(said_by_designer("AHJ stated as Irvine", said))
        self.assertFalse(said_by_designer("", said))
        self.assertFalse(said_by_designer("“.”", said))


class ThePageCanAskForThem(unittest.TestCase):
    def test_each_card_action_and_the_setting_is_one_server_action(self):
        from fpfa.web.server import ACTIONS

        for name in ("input-undo", "input-apply", "input-skip", "fill-mode"):
            self.assertIn(name, ACTIONS)


if __name__ == "__main__":
    unittest.main()
