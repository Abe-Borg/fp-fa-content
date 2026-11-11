"""The live-evaluation runner, driven with a scripted stand-in for the model.

SIMULATED. This shows the runner's own plumbing: it opens its own data directory, sends the steps,
reads the record, stops at its spend cap, and writes the report and the files beside it. What a live
model does with those steps is exactly what the runner exists to find out, and no test here says.
"""

from __future__ import annotations

import json
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

from team_scenario import (  # noqa: E402
    Players, call, client_for, discerning, say, supported_by_default, turn_one, turn_two, use,
)


class Proxy:
    """The record of whichever desk the runner has open now. The runner opens a second one after its relaunch."""

    def __init__(self, get):
        self._get = get

    def __getattr__(self, name):
        return getattr(self._get(), name)


def scripted(runner, probe_checker=discerning):
    """A client class that plays the whole run: both scenario turns, a turn that is cancelled, its resume,
    the trace check over the planted probes, and the check the export needs once they are withdrawn."""
    state = {"players": None}

    def build():
        record = Proxy(lambda: runner.desk.record)
        one = turn_one(record, runner.project_id)
        two = turn_two(record, runner.project_id)

        def slow(_kwargs):
            # Long enough for the runner's cancel to land before the next round.
            time.sleep(0.6)
            return call(use("read_record"))

        scripts = {kind: list(one.scripts.get(kind, [])) + list(two.scripts.get(kind, []))
                   for kind in ("lead", "fp-sprinkler", "fa-releasing", "checker")}
        # The cancelled turn gets one round in before the cancel lands. The turn after it answers.
        scripts["lead"] += [slow, say("The design basis stands as recorded. One question is open for the engineer.")]
        scripts["checker"] += [probe_checker, supported_by_default]
        return Players(scripts)

    def play(**kwargs):
        if state["players"] is None:
            state["players"] = build()
        return state["players"](**kwargs)

    return client_for(play), state


def _isolated():
    keep = os.environ.get("FPFA_DATA_DIR")
    home = Path(tempfile.mkdtemp(prefix="fpfa-eval-home-"))
    os.environ["FPFA_DATA_DIR"] = str(home)
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    return keep


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self._keep = _isolated()
        self.addCleanup(lambda: os.environ.__setitem__("FPFA_DATA_DIR", self._keep) if self._keep else os.environ.pop("FPFA_DATA_DIR", None))

    def _run(self, probe_checker=discerning, **options):
        from fpfa.live_eval import Runner

        out = Path(tempfile.mkdtemp(prefix="fpfa-eval-")) / "run"
        runner = Runner(out, api_key="sk-ant-local-test", cancel_after=0.2, **options)
        factory, state = scripted(runner, probe_checker)
        runner.client_factory = factory
        runner.simulated = True
        return runner, state, out

    def test_the_whole_path_runs_and_the_report_says_what_the_record_shows(self):
        from fpfa.live_eval import FAIL, INFO, NOT_SEEN, OWNER_GATES, PASS, STEPS

        runner, state, out = self._run()
        report = runner.run(STEPS)
        self.assertEqual(report["stopped"], "")
        self.assertTrue(report["simulated"])
        self.assertEqual(report["steps"], list(STEPS))
        self.assertIn("probe", STEPS)
        checks = {item["check"]: item for item in report["checks"]}
        for name in (
            "The lead set out a plan before it delegated",
            "The lead brought in the specialists the request needs without being told which",
            "The lead did not do a specialist's calculation itself",
            "Each specialist that was brought in put a finding of its own on the record",
            "One specialist asked the other for something it needed and got an answer",
            "A specialist's finding rests on the other's work, not on a repeat of its own calculation",
            "A specialist took a position, with a reason, on a finding it did not write",
            "An exchange changed, supported, or left open a conclusion on the record",
            "Every objection has an end: revised, settled with a decision, or escalated as a question",
            "Each specialist read a method before it recorded findings",
            "A cite a specialist recorded is one the method it read holds",
            "A trace check judged the findings as they stand",
            "After a relaunch the plan, the findings, and the open questions are as they were",
            "The app says where the job stands without a model call",
            "The designer answers the team's questions on the panel",
            "The lead put the value the designer stated on the record",
            "Every finding that rested on the old value was replaced or withdrawn by its author",
            "Nothing a specialist wrote is still marked out of date",
            "The lead told the designer the tables are from the earlier run",
            "A turn cancelled part-way stops and says so",
            "The next turn picks the job up from the record and finishes",
            "The application's own rules reject a wrong figure, a wrong unit, and a wrong releasing claim",
            "The checker itself rejects a wrong claim that no rule covers",
            "The Design Basis can be exported",
            "The draft says how far each finding was taken and that no standard was opened",
            "The draft does not name low air as a release input",
            "The draft says at its head what it does not cover",
        ):
            self.assertIn(name, checks, name)
            self.assertEqual(checks[name]["result"], PASS, f"{name}: {checks[name]['evidence']}")
        # One check is not met, and it is right not to be. The scripted team states the volume, the screen
        # against the insurer's time, the trim, and the releasing logic. It never states the size exemption,
        # the demand, or the gas fill, which the tool plan calculated. The draft says so and so does the runner.
        missing = "The record holds a specialist's finding for every calculation, and nothing is waiting on the team"
        self.assertEqual([item["check"] for item in report["checks"] if item["result"] == FAIL], [missing],
                         json.dumps([item for item in report["checks"] if item["result"] == FAIL], indent=1))
        for tool in ("density_area", "dry_delivery_screen", "nitrogen_gate"):
            self.assertIn(f"({tool})", checks[missing]["evidence"])
        self.assertNotIn("(hose_duration)", checks[missing]["evidence"], "it only feeds the demand, which is named")
        self.assertGreaterEqual(report["counts"][INFO], 5)
        self.assertEqual(report["counts"][NOT_SEEN], 0)
        self.assertIn("delegated to: fa-releasing, fp-sprinkler", checks["The lead brought in the specialists the request needs without being told which"]["evidence"])
        self.assertIn("q_fill_gpm is 750 gpm", checks["The lead put the value the designer stated on the record"]["evidence"])
        self.assertIn("1 rested on it: 1 replaced, 0 withdrawn, 0 left standing",
                      checks["Every finding that rested on the old value was replaced or withdrawn by its author"]["evidence"])
        self.assertIn("fp-sprinkler: dry-preaction-water-delivery-screen; fa-releasing: fa-double-interlock-releasing-cause-and-effect",
                      checks["Which specialist read which method (skill)"]["evidence"])
        self.assertIn("fp-sprinkler from dry-preaction-water-delivery-screen: 8.3.2.3.1.1",
                      checks["A cite a specialist recorded is one the method it read holds"]["evidence"])
        # The planted claims were judged on current calculations, rejected, and then withdrawn. None is current now,
        # and each is in the history under its own name.
        rules = checks["The application's own rules reject a wrong figure, a wrong unit, and a wrong releasing claim"]["evidence"]
        self.assertIn("figure: Not supported (figure not in the rows it cites: 765 gal", rules)
        self.assertIn("unit: Not supported", rules)
        self.assertIn("release: Not supported", rules)
        snap = json.loads((out / "record.json").read_text(encoding="utf-8"))
        self.assertEqual([row for row in snap["findings"] if row["agent"] == "evaluation-probe"], [])
        self.assertEqual(len([row for row in snap["retired_findings"] if row["agent"] == "evaluation-probe"]), 4)
        # The turns, with time and cost, and which one was cancelled.
        self.assertEqual([(turn["label"], turn["cancelled"]) for turn in report["turns"]],
                         [("request", False), ("change", False), ("interrupt", True), ("resume", False)])
        self.assertGreater(report["usd"], 0)
        # The scripted change turn loses a connection part-way. The report says a context failed.
        self.assertEqual(report["failed_contexts"], 1)
        self.assertEqual(report["job"], "dh1")
        self.assertEqual(len(report["content_fingerprint"]), 16)
        # The files a person reads.
        for name in ("report.md", "report.json", "progress.log", "thread.md", "usage.txt", "record.json", "team-panel.json",
                     "status-after-reopen.md", "status-at-end.md", "design-basis.docx"):
            self.assertTrue((out / name).is_file(), name)
        text = (out / "report.md").read_text(encoding="utf-8")
        self.assertIn("**SIMULATED.** The model was a scripted stand-in.", text)
        self.assertIn("| request | A | The lead set out a plan before it delegated | met |", text)
        self.assertIn("## What a program cannot tell you", text)
        self.assertIn("An estimate from the usage the API reported, not a bill.", text)
        self.assertIn("Failures: 1 model context ended on an error", text)
        self.assertIn("**What this run cannot be, whatever its checks say:**", text)
        for gate in OWNER_GATES:
            self.assertIn(gate, text)
        self.assertIn("docs/known-answer-dh1.md", text)
        self.assertIn("The designer answered", (out / "thread.md").read_text(encoding="utf-8") + "The designer answered")
        self.assertIn("**Where Sample data hall DI zone stands**", (out / "status-after-reopen.md").read_text(encoding="utf-8"))
        self.assertIn("Time on the model:", (out / "usage.txt").read_text(encoding="utf-8"))
        # The run kept to its own data directory, and every scripted move was played.
        self.assertTrue((out / "data" / "fpfa.db").is_file())
        self.assertEqual(state["players"].left(), {})

    def test_a_checker_that_approves_everything_is_caught_by_the_planted_claims(self):
        """The same run with the stand-in checker that says Supported to every claim it is shown."""
        from fpfa.live_eval import FAIL, PASS, STEPS

        runner, _state, _out = self._run(probe_checker=supported_by_default)
        report = runner.run(STEPS)
        self.assertEqual(report["stopped"], "")
        checks = {item["check"]: item for item in report["checks"]}
        # The three claims a rule covers are rejected whatever the checker said, and the report says it was overruled.
        self.assertEqual(checks["The application's own rules reject a wrong figure, a wrong unit, and a wrong releasing claim"]["result"], PASS)
        self.assertIn("it approved 3 of 3 (figure, unit, release) and was overruled",
                      checks["What the checker said about the three claims the rules caught"]["evidence"])
        # The fourth has no rule behind it. An approving checker lets it through, and the run says so.
        own = checks["The checker itself rejects a wrong claim that no rule covers"]
        self.assertEqual(own["result"], FAIL)
        self.assertIn("The checker approved a claim that contradicts the row it cites.", own["evidence"])
        self.assertIn("Treat every trace-consistent finding in this run as unproven.", own["evidence"])

    def test_it_stops_between_steps_at_the_spend_cap_and_keeps_what_it_wrote(self):
        from fpfa.live_eval import STEPS

        runner, _state, out = self._run(max_usd=0.05)
        report = runner.run(STEPS)
        self.assertIn("the cap is $0.05", report["stopped"])
        self.assertEqual([turn["label"] for turn in report["turns"]], ["request"], "the first turn ran; the next was not sent")
        text = (out / "report.md").read_text(encoding="utf-8")
        self.assertIn("**The run stopped early:**", text)
        self.assertTrue(any(item["step"] == "request" for item in report["checks"]))

    def test_a_run_that_fails_part_way_still_writes_its_report(self):
        from fpfa.live_eval import Runner

        out = Path(tempfile.mkdtemp(prefix="fpfa-eval-")) / "run"

        class Broken:
            def __init__(self, _key):
                pass

            def create(self, **_kwargs):
                raise RuntimeError("no route to host")

        runner = Runner(out, api_key="sk-ant-local-test", client_factory=Broken)
        report = runner.run(("request", "export"))
        self.assertEqual(report["stopped"], "")
        self.assertTrue((out / "report.md").is_file())
        failed = [item["check"] for item in report["checks"] if item["result"] == "NOT MET"]
        self.assertIn("The lead brought in the specialists the request needs without being told which", failed)
        self.assertIn("no route to host", (out / "thread.md").read_text(encoding="utf-8"))

    def test_the_request_names_no_specialist_and_the_steps_are_the_guides(self):
        from fpfa import live_eval

        said = [live_eval.REQUEST, live_eval.CHANGE, live_eval.INTERRUPTED, live_eval.RESUME, live_eval.DEFAULT_ANSWER]
        said += [job[key] for job in live_eval.JOBS.values() for key in ("request", "change")]
        for text in said:
            for word in ("specialist", "sprinkler specialist", "fp-", "fa-", "delegate", "checker", "consult"):
                self.assertNotIn(word, text.lower(), f"{word!r} in {text!r}")
        # The second job is asked for in other words than the first.
        self.assertNotEqual(live_eval.JOBS["dh2"]["request"], live_eval.JOBS["dh1"]["request"])
        with self.assertRaises(ValueError):
            live_eval.Runner(Path(tempfile.mkdtemp()) / "y", job="dh9")
        guide = (REPO / "docs" / "live-evaluation.md").read_text(encoding="utf-8")
        for text in (live_eval.REQUEST, live_eval.CHANGE):
            self.assertIn(text, guide, "the guide and the runner send the same words")
        with self.assertRaises(ValueError):
            live_eval.Runner(Path(tempfile.mkdtemp()) / "x", client_factory=object).run(("export",))


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self._keep = _isolated()
        self.addCleanup(lambda: os.environ.__setitem__("FPFA_DATA_DIR", self._keep) if self._keep else os.environ.pop("FPFA_DATA_DIR", None))

    def test_nothing_runs_without_a_key_a_fresh_folder_and_a_yes(self):
        from fpfa import live_eval

        out = Path(tempfile.mkdtemp(prefix="fpfa-eval-cli-"))
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}), patch("fpfa.keystore.load_api_key", return_value=""), \
                patch("fpfa.live_eval.Runner") as runner:
            self.assertEqual(live_eval.main(["--out", str(out / "a")]), 2)
            runner.assert_not_called()
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-local-test"}), patch("fpfa.live_eval.Runner") as runner:
            self.assertEqual(live_eval.main(["--out", str(out / "b"), "--effort", "turbo"]), 2)
            self.assertEqual(live_eval.main(["--out", str(out / "b"), "--steps", "request,dance"]), 2)
            (out / "c" / "data").mkdir(parents=True)
            self.assertEqual(live_eval.main(["--out", str(out / "c"), "--yes"]), 2, "a folder that holds a run is refused")
            with patch("builtins.input", return_value="no"):
                self.assertEqual(live_eval.main(["--out", str(out / "d")]), 1)
            runner.assert_not_called()
            runner.return_value.run.return_value = {"stopped": "", "counts": {live_eval.FAIL: 0}}
            with patch.dict(os.environ, {}, clear=False):
                self.assertEqual(live_eval.main(["--out", str(out / "e"), "--yes", "--effort", "high", "--max-usd", "3",
                                                 "--steps", "request,export"]), 0)
                self.assertEqual(os.environ.get("FPFA_EFFORT"), "high")
            runner.assert_called_once()
            self.assertEqual(runner.call_args.kwargs["max_usd"], 3.0)
            self.assertEqual(runner.call_args.kwargs["api_key"], "sk-ant-local-test")
            runner.return_value.run.assert_called_once_with(("request", "export"))
        os.environ.pop("FPFA_EFFORT", None)


if __name__ == "__main__":
    unittest.main()
