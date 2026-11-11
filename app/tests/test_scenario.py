"""SIMULATED end to end: one job from a plain request to an inspectable draft, with every model call scripted.

tests/team_scenario.py holds the script and says what this does and does not show. In short: the
application's side of the workflow is real here (messages, tools, calc kernels, record, staleness,
trace-check rules, reply audit, export, a second window on the same data), and the agents' choices are
written in advance. A pass means the application can carry the job. It does not mean a live model will.

Each test method below is one item of the evaluation path in docs/live-evaluation.md, so the simulated
result and the live result can be laid side by side.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402
from team_scenario import (ANSWER_TRIM, REQUEST_ONE, REQUEST_TWO, Lookup, client_for, turn_one,  # noqa: E402
                           turn_two)
from test_design_basis import _docx_text  # noqa: E402


class Scenario:
    """Plays the job once and keeps what each step left behind, so each test reads one part of it."""

    def __init__(self):
        self.data = Path(tempfile.mkdtemp(prefix="fpfa-scenario-"))
        os.environ["FPFA_DATA_DIR"] = str(self.data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config

        write_config({"key_backend": "file"})
        save_api_key("sk-ant-local-test")
        self.root = Loop()
        self.after = {}
        self._play()

    def _settle(self, app, timeout: float = 20.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            app.pump()
            if not app._pending_here():
                app.pump()
                return
            time.sleep(0.02)
        raise AssertionError("the turn did not finish")

    def _ask(self, app, players, text: str) -> None:
        with patch("fpfa.desk.AnthropicMessages", client_for(players)):
            app.send_chat(text)
            self._settle(app)

    def _play(self) -> None:
        from fpfa.usage_report import report_text

        app = self.root.open_desk()
        self.root.update()
        # The designer has a zone on the form (the sample's inputs) and has not run anything.
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        self.project_id = app.project["id"]
        self.one = turn_one(app.record, self.project_id)
        self._ask(app, self.one, REQUEST_ONE)
        self.after["one"] = {
            "thread": app.thread_text(), "team": app.team, "snapshot": app.record.snapshot(self.project_id),
            "basis_ready": app.design_basis_ready(), "chips": app.chips(),
        }
        out = self.data / "basis-one.docx"
        app.export_design_basis_to(out)
        self.after["one"]["docx"] = _docx_text(out)

        # The window is closed. A new one opens on the same data directory.
        self.root.destroy()
        os.environ["FPFA_DATA_DIR"] = str(self.data)
        app = self.root.open_desk()
        self.root.update()
        app.select_project(self.project_id)
        self.root.update()
        self.after["reopened"] = {"thread": app.thread_text(), "team": app.team, "chips": app.chips()}
        app.send_chat("/status")
        self.after["reopened"]["status"] = app.thread_text()

        # The designer answers the team's question on the panel, then says the fill flow is different.
        ask = app.team["asks"][0]
        app.answer_question(ask["id"], ANSWER_TRIM + " gallons, from the valve submittal.")
        self.after["answered"] = {"team": app.team, "chips": app.chips()}
        self.two = turn_two(app.record, self.project_id)
        self._ask(app, self.two, REQUEST_TWO)
        self.after["two"] = {
            "thread": app.thread_text(), "team": app.team, "snapshot": app.record.snapshot(self.project_id),
            "basis_ready": app.design_basis_ready(), "run_changes": app.run_changes(),
            "usage": report_text(app.record, self.project_id),
        }
        app.export_docx()
        self.after["two"]["section_notice"] = app.notices[-1]["message"]
        # The designer runs the zone again, as the lead and the app both said. Then the draft can be exported.
        app.start_zone_run()
        self._settle(app)
        self.after["rerun"] = {"basis_ready": app.design_basis_ready(), "run_changes": app.run_changes(), "team": app.team}
        out = self.data / "basis-two.docx"
        app.export_design_basis_to(out)
        self.after["two"]["docx"] = _docx_text(out)
        self.app = app
        self.at = Lookup(app.record, self.project_id)

    def close(self) -> None:
        self.root.destroy()


class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Scenario()

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def test_0_the_script_was_played_to_the_end(self):
        self.assertEqual(self.s.one.left(), {})
        self.assertEqual(self.s.two.left(), {})
        for players in (self.s.one, self.s.two):
            self.assertNotIn("unknown", {item["kind"] for item in players.calls})

    def test_1_the_request_names_no_specialist_and_the_lead_runs_from_its_role_and_the_record(self):
        for text in (REQUEST_ONE, REQUEST_TWO):
            for word in ("specialist", "sprinkler", "fp-", "fa-", "delegate", "checker", "first", "then"):
                self.assertNotIn(word, text.lower(), f"{word!r} in the request")
        lead = self.s.one.of("lead")
        self.assertIn("# Team lead", lead[0]["system"])
        self.assertTrue(all(item["system"] == lead[0]["system"] for item in lead), "the cached system text never varies")
        self.assertNotIn("read_role", lead[0]["tools"])
        for tool in ("delegate", "set_plan", "set_input", "request_check", "resolve_disagreement"):
            self.assertIn(tool, lead[0]["tools"])
        opening = lead[0]["user"]
        self.assertTrue(opening.startswith("Status of this job, read from the project record by the application:"))
        self.assertIn("Plan: none set on this job yet.", opening)
        self.assertIn("Contributors so far: none. No specialist has worked on this job.", opening)
        self.assertIn(f"Designer: {REQUEST_ONE}", opening)
        plan = self.s.after["one"]["team"]["plan"]
        self.assertEqual(plan["objective"], "Delivery time and releasing sequence for the data hall 1 preaction zone")
        self.assertEqual([step["status"] for step in plan["steps"]], ["done"] * 4)

    def test_2_the_dependency_between_the_two_specialists_is_carried_by_the_record(self):
        snap = self.s.after["one"]["snapshot"]
        kinds = [(row["kind"], row["from_agent"], row["to_agent"], row["status"]) for row in snap["handoffs"]]
        self.assertEqual(kinds, [
            ("delegation", "lead", "fp-sprinkler", "returned"),
            ("consult", "fp-sprinkler", "fa-releasing", "returned"),
            ("delegation", "lead", "fa-releasing", "returned"),
            ("delegation", "lead", "fp-sprinkler", "returned"),
        ])
        asked = next(row for row in snap["handoffs"] if row["kind"] == "consult")
        self.assertIn("What releasing time does the sequence carry", asked["brief"])
        self.assertIn("carry it as ASSUMED", asked["result"])
        # The releasing specialist was shown the sprinkler findings and took a position on two of them.
        brief = next(item["user"] for item in self.s.one.of("fa-releasing") if "The lead delegated this task" in item["user"])
        self.assertIn("Other contributors' findings you have not reviewed.", brief)
        self.assertIn("fp-sprinkler (calculated): The FM 30 s screen is missed", brief)
        reviews = [(row["agent"], row["position"], row["status"]) for row in snap["reviews"]]
        self.assertIn(("fa-releasing", "agree", "resolved"), reviews)
        self.assertIn(("fa-releasing", "object", "resolved"), reviews)
        self.assertIn(("fp-sprinkler", "agree", "resolved"), reviews)
        # The objection went back to the author, who was told about it and revised.
        told = self.s.one.of("fp-sprinkler")[-2]["user"]
        self.assertIn("Objections to your findings.", told)
        self.assertIn("fa-releasing objects: The screen adds 8 s and 2 s", told)
        objection = next(row for row in snap["reviews"] if row["position"] == "object")
        self.assertIn("The finding was revised by fp-sprinkler", objection["resolution"])
        self.assertEqual(len(snap["retired_findings"]), 1)
        # The releasing finding rests on the sprinkler specialist's trim finding by id.
        trim = next(row for row in snap["findings"] if row["text"].startswith("Trim family is El/El"))
        sequence = next(row for row in snap["findings"] if row["text"].startswith("Release is the detection leg"))
        self.assertIn(trim["id"], sequence["supports"])
        # The app's own account of it sits under the lead's reply.
        thread = self.s.after["one"]["thread"]
        # One line per specialist, however many times the lead went back to it.
        self.assertIn("fp-sprinkler: 4 findings, 1 question, 3 calc records, in 2 passes", thread)
        self.assertIn("fa-releasing: 1 finding, 1 question", thread)
        for line in ("Between the specialists:", "fp-sprinkler asked fa-releasing: What releasing time",
                     "fa-releasing objected to a finding by fp-sprinkler", "fp-sprinkler revised a finding",
                     "fa-releasing reviewed and agreed with 1 finding by fp-sprinkler"):
            self.assertIn(line, thread, line)
        self.assertNotIn("still open", thread)
        self.assertNotIn("Figures in this reply", thread, "every figure in the reply is on the record")
        self.assertNotIn("could not find on the record", thread)

    def test_3_missing_information_becomes_a_question_the_designer_answers(self):
        one = self.s.after["one"]["team"]
        self.assertEqual([row["text"] for row in one["asks"]], ["What is the trim volume on the elected valve's data sheet?"])
        self.assertEqual([row["text"] for row in one["rfis"]], ["Does the owner accept one detection zone for the detection leg?"])
        self.assertIn("1 needs your answer", one["strip"])
        # The work went on with a stated assumption while the question was open.
        self.assertIn("with the trim volume ASSUMED at 5 gal", self.s.after["one"]["docx"])
        answered = self.s.after["answered"]
        self.assertEqual(answered["team"]["asks"], [])
        self.assertEqual(answered["chips"][0]["label"], "Continue with my answers")
        opening = self.s.two.of("lead")[0]["user"]
        self.assertIn("The designer answered these on the panel. You have not acted on them yet.", opening)
        self.assertIn("Answer: 6.5 gallons, from the valve submittal.", opening)
        row = self.s.at.question("trim volume")
        self.assertEqual((row["status"], row["answered_by"]), ("answered", "designer"))
        self.assertEqual(self.s.at.given("trim_gal")["source"], "designer, in chat: answered on the Team panel")

    def test_4_a_changed_input_puts_what_used_it_out_of_date_until_it_is_redone(self):
        from fpfa import inputs

        given = self.s.at.given("q_fill_gpm")
        self.assertEqual((inputs.decode(given["value"]), given["label"], given["agent"]), (750.0, "GIVEN", "lead"))
        self.assertEqual(given["source"], "designer, in chat: the pump test at the riser")
        # The sprinkler specialist was told which of its findings the change left behind.
        told = next(item["user"] for item in self.s.two.of("fp-sprinkler") if "The lead delegated this task" in item["user"])
        self.assertIn("Your findings and decisions whose basis changed.", told)
        self.assertIn("q_fill_gpm changed from 600 gpm to 750 gpm", told)
        self.assertIn("trim_gal changed from", told)
        # They were replaced, not edited, and the old ones are history.
        snap = self.s.after["two"]["snapshot"]
        current = [row["text"] for row in snap["findings"]]
        self.assertTrue(any("still missed: t_total is 32.6 s at 750 gpm" in text for text in current), current)
        self.assertTrue(any("Zone total is 282.8 gal with the 6.5 gal trim volume the designer gave" in text for text in current))
        self.assertFalse(any("at 600 gpm" in text for text in current))
        self.assertEqual(len(snap["retired_findings"]), 3)
        stale = self.s.after["two"]["team"]["stale"]
        self.assertTrue(stale)
        self.assertEqual({row["by"] for row in stale}, {"tool-plan"}, "nothing a specialist wrote is left out of date")
        # The tool plan's tables are a run on the old inputs. The app says so, and neither export is written from it.
        self.assertEqual(sorted(self.s.after["two"]["run_changes"]), ["q_fill_gpm", "trim_gal"])
        self.assertIn("out of date", self.s.after["two"]["basis_ready"])
        self.assertIn("Run the zone again", self.s.after["two"]["basis_ready"])
        self.assertIn("The zone form changed after the last run (", self.s.after["two"]["section_notice"])
        # Running the zone again clears it. The trace check the lead ran still speaks for the findings.
        self.assertEqual(self.s.after["rerun"], {"basis_ready": "", "run_changes": [], "team": self.s.after["rerun"]["team"]})
        self.assertEqual(self.s.after["rerun"]["team"]["stale"], [])
        # The lead was not handed the old run's figures as governing on the second turn.
        opening = self.s.two.of("lead")[0]["user"]
        self.assertIn("A tool plan already ran for this zone.", opening, "at the start of turn two the run is still current")
        thread = self.s.after["two"]["thread"]
        self.assertIn("input trim_gal: blank → 6.5 gal (from the chat)", thread)
        self.assertIn("input q_fill_gpm: 600 gpm → 750 gpm (from the chat)", thread)
        self.assertNotIn("could not find on the record", thread)
        self.assertNotIn("only on out-of-date calculations", thread)

    def test_5_closing_and_reopening_the_window_loses_nothing(self):
        before, after = self.s.after["one"]["team"], self.s.after["reopened"]["team"]
        for key in ("plan", "asks", "rfis", "tiers", "strip", "settled"):
            self.assertEqual(after[key], before[key], key)
        self.assertEqual([row["text"] for row in after["findings"]], [row["text"] for row in before["findings"]])
        self.assertIn(REQUEST_ONE, self.s.after["reopened"]["thread"])
        self.assertEqual([chip["label"] for chip in self.s.after["reopened"]["chips"]], ["Where things stand"])
        status = self.s.after["reopened"]["status"]
        for line in ("Objective: Delivery time and releasing sequence for the data hall 1 preaction zone",
                     "Sprinkler specialist (fp-sprinkler): done, 3 findings, reviewed 1 of the others' findings",
                     "The team needs from you", "1. What is the trim volume on the elected valve's data sheet?",
                     "Design Basis export: ready."):
            self.assertIn(line, status, line)

    def test_6_a_failure_part_way_keeps_what_was_done_and_the_retry_replays_it(self):
        snap = self.s.after["two"]["snapshot"]
        rows = [(row["kind"], row["to_agent"], row["status"]) for row in snap["handoffs"]][4:]
        self.assertEqual(rows, [("delegation", "fp-sprinkler", "cancelled"), ("delegation", "fp-sprinkler", "returned"),
                                ("delegation", "fa-releasing", "returned")])
        failed = [row for row in snap["handoffs"] if row["status"] == "cancelled"][0]
        self.assertEqual(failed["result"], "The specialist did not finish.")
        # The volume the failed attempt computed was not computed again.
        volume = self.s.at.calc("zone_trapped_volume", trim_gal=6.5)
        self.assertEqual(volume["replay_count"], 1)
        self.assertEqual(len([row for row in snap["calcs"] if row["tool"] == "zone_trapped_volume" and row["inputs"].get("trim_gal") == 6.5]), 1)
        self.assertIn("did not finish", " ".join(item["user"] for item in self.s.two.of("lead")) + "did not finish")
        agents = {row["role_slug"]: row["status"] for row in snap["agents"]}
        self.assertEqual((agents["fp-sprinkler"], agents["fa-releasing"], agents["lead"]), ("done", "done", "done"))

    def test_7_the_draft_and_its_evidence_can_be_inspected(self):
        from fpfa.checker import NOT_STANDARD, TIER_TITLE

        text = self.s.after["two"]["docx"]
        self.assertIn(NOT_STANDARD, text)
        self.assertIn("It is not cleared for issue.", text)
        self.assertIn("Objective the team worked to: Delivery time and releasing sequence for the data hall 1 preaction zone", text)
        # Inputs, with who supplied each.
        self.assertIn("q_fill_gpm | 750 gpm | GIVEN | designer, in chat: the pump test at the riser", text)
        self.assertIn("trim_gal | 6.5 gal | GIVEN | designer, in chat: answered on the Team panel", text)
        self.assertIn("t_release_s | 2 s | GIVEN | sample data", text)
        # Findings by tier. The 500 gal cite was read in the content pack's own note.
        tiers = {row["tier"]: row["count"] for row in self.s.after["two"]["team"]["tiers"]}
        self.assertEqual(tiers, {"source": 3, "reviewed": 1, "stated": 0, "open": 1})
        self.assertIn(f"{TIER_TITLE['source']} (3)", text)
        row = next(line for line in text.splitlines() if line.startswith("The FM 30 s screen is still missed"))
        self.assertIn("| calculated | fp-sprinkler | di_trip_to_water [", row)
        self.assertIn("input t_detect_s [", row)
        self.assertIn("Trace check: Supported. Against calculation record: di_trip_to_water", row)
        self.assertIn("| fa-releasing |", row)
        assumed = next(line for line in text.splitlines() if line.startswith("The 2 s releasing time is the form's value"))
        self.assertIn("It is an assumption.", assumed)
        # The review log says how the objection ended. The exchanges are listed by kind. History is kept.
        self.assertIn("| fp-sprinkler | fa-releasing | objects |", text)
        self.assertIn("The finding was revised by fp-sprinkler", text)
        self.assertIn("consult | fp-sprinkler | fa-releasing | What releasing time does the sequence carry", text)
        self.assertIn("Input changed: q_fill_gpm changed from 600 gpm to 750 gpm", text)
        self.assertIn("Finding by fp-sprinkler, replaced by [", text)
        self.assertIn("For the engineer of record, the owner, or the authority:", text)
        self.assertIn("What is the trim volume on the elected valve's data sheet? Answer: 6.5 gallons, from the valve submittal. "
                      "(answered by designer)", text)
        # Nothing in the draft says a standard was checked, verified, or confirmed.
        for phrase in ("verified against the standard", "standards-verified", "code-verified", "confirmed against NFPA"):
            self.assertNotIn(phrase, text)
        # The same evidence is on the panel, finding by finding.
        finding = next(row for row in self.s.after["two"]["team"]["findings"] if row["text"].startswith("The FM 30 s screen is still missed"))
        self.assertEqual(finding["tier"], "source")
        self.assertTrue(finding["rests_on"][0].startswith("calculation di_trip_to_water ["))
        self.assertEqual([review["position"] for review in finding["reviews"]], ["agrees"])

    def test_8_time_and_cost_are_read_from_the_record(self):
        from fpfa.usage_report import job_totals, usage_events

        text = self.s.after["two"]["usage"]
        rows = usage_events(self.s.app.record, self.s.project_id)
        kinds = [row["kind"] for row in rows]
        self.assertEqual(kinds.count("turn"), 2)
        self.assertEqual(kinds.count("record_check"), 2)
        self.assertEqual(kinds.count("consult"), 1)
        self.assertEqual(kinds.count("delegation"), 5, "the failed attempt wrote no usage row; the five that ran did")
        total = job_totals(rows)
        self.assertGreater(total["rounds"], 25)
        self.assertIn("lead turn, 3 delegations, 1 check", text)
        self.assertIn("within that: fp-sprinkler asked fa-releasing", text)
        self.assertIn("trace check", text)
        self.assertIn("Job total over 4 model contexts", text)
        self.assertIn("Estimated cost $", text)
        self.assertIn("An estimate from list prices, not a bill.", text)
        # Every billed context closes with how long it took. In this simulation the times are near zero.
        self.assertTrue(all("seconds" in row for row in rows if row["kind"] in ("turn", "delegation", "consult", "record_check")))


if __name__ == "__main__":
    unittest.main()
