"""Usage and cost from the record, and the About versions.

Every model call is a stand-in that reports a usage block. No API call is made.
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
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


def _usage(inp=1000, out=200, write=0, read=0):
    return SimpleNamespace(input_tokens=inp, output_tokens=out, cache_creation_input_tokens=write,
                           cache_read_input_tokens=read)


def _turn(stop_reason, *blocks, usage=None):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks), usage=usage or _usage())


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-usage-")) / "fpfa.db")


class CostMathTests(unittest.TestCase):
    def test_cost_prices_each_token_class_at_its_rate(self):
        from fpfa.usage_report import RATES_PER_MILLION, cost, normalize

        usage = {"rounds": 2, "input_tokens": 1_000_000, "output_tokens": 100_000,
                 "cache_creation_input_tokens": 200_000, "cache_read_input_tokens": 5_000_000}
        money = cost(usage)
        self.assertAlmostEqual(money["input"], RATES_PER_MILLION["input"])
        self.assertAlmostEqual(money["output"], RATES_PER_MILLION["output"] / 10)
        self.assertAlmostEqual(money["cache_write"], RATES_PER_MILLION["cache_write"] / 5)
        self.assertAlmostEqual(money["cache_read"], RATES_PER_MILLION["cache_read"] * 5)
        self.assertAlmostEqual(money["total"], sum(v for k, v in money.items() if k != "total"))
        cheaper = cost(usage, {"output": 10.0})
        self.assertAlmostEqual(cheaper["output"], 1.0)
        self.assertEqual(normalize(None)["input_tokens"], 0)
        self.assertEqual(normalize({"input_tokens": "12"})["input_tokens"], 12)
        self.assertEqual(cost({})["total"], 0.0)

    def test_report_counts_turns_narrations_and_checks_but_not_delegations_twice(self):
        from fpfa.usage_report import job_totals, report_text, usage_events

        record = _record()
        record.ensure_project("p1", "DH-1 design basis")
        self.assertIn("No model usage is on this job's record yet", report_text(record, "p1"))
        record.log_event("p1", "delegation", {"specialist": "fp-sprinkler", "usage": {
            "rounds": 3, "input_tokens": 300, "output_tokens": 30}}, agent="lead")
        record.log_event("p1", "turn", {"usage": {"rounds": 5, "input_tokens": 1000, "output_tokens": 100,
                                                   "cache_read_input_tokens": 4000},
                                         "delegations": 1, "checks": 0, "cancelled": False}, agent="lead")
        record.log_event("p1", "narration", {"usage": {"rounds": 1, "input_tokens": 500, "output_tokens": 50},
                                              "source": "claude", "cancelled": False}, agent="narrator")
        record.log_event("p1", "record_check", {"usage": {"rounds": 1, "input_tokens": 200, "output_tokens": 20},
                                                 "rows": []}, agent="qa-specialist")
        record.log_event("p1", "wake", {"gap_seconds": 300})
        rows = usage_events(record, "p1")
        self.assertEqual([row["kind"] for row in rows], ["delegation", "turn", "narration", "record_check"])
        self.assertEqual([row["counted"] for row in rows], [False, True, True, True])
        total = job_totals(rows)
        self.assertEqual(total["input_tokens"], 1700)
        self.assertEqual(total["output_tokens"], 170)
        self.assertEqual(total["cache_read_input_tokens"], 4000)
        self.assertEqual(total["rounds"], 7)
        text = report_text(record, "p1")
        self.assertIn("Usage and cost for DH-1 design basis", text)
        self.assertIn("lead turn, 1 delegation", text)
        self.assertIn("within the turn: fp-sprinkler", text)
        self.assertIn("(inside the turn above, not added)", text)
        self.assertIn("narration (narrator, claude)", text)
        self.assertIn("trace check", text)
        self.assertIn("Job total over 3 model contexts", text)
        self.assertIn("Estimated cost $", text)
        self.assertIn("Rates per million tokens as of", text)
        self.assertIn("70% of input tokens were read from the cache", text)

    def test_job_totals_read_the_whole_history_not_a_recent_window(self):
        from fpfa.usage_report import job_totals, report_text, usage_events

        record = _record()
        record.ensure_project("p1", "Long job")
        record.log_event("p1", "turn", {"usage": {"rounds": 1, "input_tokens": 1000, "output_tokens": 100}}, agent="lead")

        def flood(conn):
            conn.executemany(
                "INSERT INTO events (project_id, ts, kind, agent, payload) VALUES ('p1', '2026-11-09T00:00:00Z', 'wake', '', '{}')",
                [()] * 6000,
            )

        record._write(flood)
        recent = record.events("p1", limit=5000)
        self.assertFalse(any(event["kind"] == "turn" for event in recent), "the window has lost the turn")
        rows = usage_events(record, "p1")
        self.assertEqual([row["kind"] for row in rows], ["turn"])
        self.assertEqual(job_totals(rows)["input_tokens"], 1000)
        self.assertIn("Job total over 1 model context", report_text(record, "p1"))
        self.assertEqual(record.events_by_kind("p1", ()), [])

    def test_cli_prints_text_or_json_for_a_database(self):
        from fpfa.usage_report import main

        record = _record()
        record.ensure_project("p1", "Job one")
        record.log_event("p1", "turn", {"usage": {"rounds": 1, "input_tokens": 10, "output_tokens": 1}}, agent="lead")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--db", str(record.path), "--output-rate", "10"])
        self.assertEqual(code, 0)
        self.assertIn("Usage and cost for Job one", out.getvalue())
        self.assertIn("output $10.00", out.getvalue())
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--db", str(record.path), "--json"])
        self.assertIn('"rates_date"', out.getvalue())
        self.assertEqual(main(["--db", str(Path(tempfile.mkdtemp()) / "missing.db")]), 2)


class UsageEventTests(unittest.TestCase):
    def test_a_lead_turn_closes_with_a_turn_event_that_carries_the_task_total(self):
        from fpfa.everyday import run_everyday

        record = _record()
        record.ensure_project("p1", "Job one")
        calls = []

        def create(**kwargs):
            calls.append(kwargs)
            return _turn("end_turn", Block(type="text", text="Done."), usage=_usage(1500, 300, 100, 2000))

        out = run_everyday(REPO, create, "Hello", record=record, project_id="p1")
        event = record.latest_event("p1", "turn")
        self.assertEqual(event["agent"], "lead")
        self.assertEqual(event["payload"]["usage"]["input_tokens"], 1500)
        self.assertEqual(event["payload"]["usage"]["cache_read_input_tokens"], 2000)
        self.assertEqual(event["payload"]["delegations"], 0)
        self.assertFalse(event["payload"]["cancelled"])
        self.assertEqual(event["payload"]["usage"], out["usage"])

    def test_a_cancelled_lead_turn_still_records_what_it_spent(self):
        from fpfa.claude_client import TurnCancelled
        from fpfa.everyday import run_everyday

        record = _record()
        record.ensure_project("p1", "Job one")
        cancel = threading.Event()

        def create(**kwargs):
            cancel.set()
            return _turn("tool_use", Block(type="tool_use", id="t1", name="hose_duration",
                                           input={"hazard": "ordinary", "supervised": True}),
                         usage=_usage(900, 90))

        with self.assertRaises(TurnCancelled):
            run_everyday(REPO, create, "Hello", record=record, project_id="p1", cancel=cancel)
        event = record.latest_event("p1", "turn")
        self.assertTrue(event["payload"]["cancelled"])
        self.assertEqual(event["payload"]["usage"]["input_tokens"], 900)
        self.assertEqual(event["payload"]["usage"]["rounds"], 1)
        self.assertEqual({row["name"]: row["status"] for row in record.agents("p1")}["Lead"], "interrupted")

    def test_a_cancel_inside_a_specialist_keeps_the_specialists_spend(self):
        from fpfa.claude_client import TurnCancelled
        from fpfa.everyday import run_everyday

        record = _record()
        record.ensure_project("p1", "Job one")
        cancel = threading.Event()

        def create(**kwargs):
            system = kwargs.get("system")
            text = system if isinstance(system, str) else "".join(block.get("text", "") for block in system or [])
            if "# Sprinkler specialist" in text:
                # The specialist runs one round, then the designer cancels.
                cancel.set()
                return _turn("tool_use", Block(type="tool_use", id="s1", name="hose_duration",
                                               input={"hazard": "ordinary", "supervised": True}),
                             usage=_usage(900, 90))
            return _turn("tool_use", Block(type="tool_use", id="l1", name="delegate",
                                           input={"specialist": "fp-sprinkler", "brief": "Check the hose duration."}),
                         usage=_usage(100, 10))

        with self.assertRaises(TurnCancelled):
            run_everyday(REPO, create, "Design basis?", record=record, project_id="p1", cancel=cancel)
        turn = record.latest_event("p1", "turn")["payload"]
        self.assertTrue(turn["cancelled"])
        self.assertEqual(turn["usage"]["input_tokens"], 1000, "lead 100 plus the interrupted specialist's 900")
        self.assertEqual(turn["usage"]["output_tokens"], 100)
        self.assertEqual(turn["lead_usage"]["input_tokens"], 100)
        delegation = record.latest_event("p1", "delegation")["payload"]
        self.assertTrue(delegation["cancelled"])
        self.assertEqual(delegation["specialist"], "fp-sprinkler")
        self.assertEqual(delegation["usage"]["input_tokens"], 900)
        agents = {row["role_slug"]: row["status"] for row in record.agents("p1")}
        self.assertEqual(agents, {"lead": "interrupted", "fp-sprinkler": "interrupted"})
        from fpfa.usage_report import report_text

        text = report_text(record, "p1")
        self.assertIn("within the turn: fp-sprinkler, cancelled", text)
        self.assertIn("lead turn, cancelled", text)

    def test_narrations_and_checks_record_their_usage(self):
        from fpfa.bess import run_bess_plan
        from fpfa.claude_client import TurnCancelled
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_DI
        from fpfa.team import check_record
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("p1", "Job one")

        def narrator(_system, _user, _tools, _execute):
            return {"text": "", "tool_calls": [], "stop_reason": "end_turn",
                    "usage": {"rounds": 2, "input_tokens": 700, "output_tokens": 70}}

        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator, record=record, project_id="p1")
        zone = record.latest_event("p1", "narration")
        self.assertEqual(zone["agent"], "narrator")
        self.assertEqual(zone["payload"]["kind"], "zone")
        self.assertEqual(zone["payload"]["usage"]["input_tokens"], 700)
        self.assertEqual(zone["payload"]["source"], "tool-plan")
        self.assertFalse(zone["payload"]["cancelled"])

        def cancelled(_system, _user, _tools, _execute):
            exc = TurnCancelled("Cancelled by the designer before the next model round.")
            exc.usage = {"rounds": 1, "input_tokens": 400, "output_tokens": 40}
            raise exc

        run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, narrator=cancelled, record=record, project_id="p1")
        bess = record.latest_event("p1", "narration")
        self.assertEqual(bess["payload"]["kind"], "bess")
        self.assertTrue(bess["payload"]["cancelled"])
        self.assertEqual(bess["payload"]["usage"]["input_tokens"], 400)
        # The tool plan alone writes no narration event.
        before = len([e for e in record.events("p1") if e["kind"] == "narration"])
        run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, record=record, project_id="p1")
        self.assertEqual(len([e for e in record.events("p1") if e["kind"] == "narration"]), before)

        calc = record.calcs("p1")[0]["id"]
        record.record_finding("p1", agent="fp-sprinkler", text="Zone total 281.3 gal", label="calculated", supports=[calc])

        def checker(**kwargs):
            return _turn("end_turn", Block(type="text", text='1. Supported. Cite: "x"'), usage=_usage(250, 25))

        outcome = check_record(REPO, record, "p1", checker)
        self.assertEqual(outcome["usage"]["input_tokens"], 250)
        event = record.latest_event("p1", "record_check")
        self.assertEqual(event["payload"]["usage"]["output_tokens"], 25)

        from fpfa.usage_report import job_totals, usage_events

        total = job_totals(usage_events(record, "p1"))
        self.assertEqual(total["input_tokens"], 700 + 400 + 250)
        self.assertEqual(total["rounds"], 4)


class AboutTests(unittest.TestCase):
    def test_version_lines_name_the_app_runtime_dependencies_and_record(self):
        from fpfa import __version__
        from fpfa.about import version_lines

        lines = version_lines(REPO, Path("/data"))
        self.assertTrue(lines[0].startswith(f"+Cynosure {__version__} ("))
        self.assertEqual(lines[1], "Model claude-opus-5-5")
        self.assertTrue(lines[2].startswith("Python 3."))
        self.assertTrue(any(line.startswith("anthropic ") for line in lines))
        self.assertTrue(any(line.startswith("python-docx ") for line in lines))
        self.assertTrue(any(line.startswith("keyring ") for line in lines))
        self.assertTrue(any(line.startswith("Content pack ") and str(REPO) in line for line in lines))
        self.assertIn("Data directory /data", lines)
        self.assertEqual(lines[-1], "Record schema 4")

    def test_the_versions_flag_prints_and_exits_without_a_window(self):
        from fpfa.web.shell import main

        out = io.StringIO()
        with patch("fpfa.web.shell.Desk") as desk, patch("fpfa.web.shell.WindowServer") as server, redirect_stdout(out):
            main(["--versions"])
        desk.assert_not_called()
        server.assert_not_called()
        self.assertIn("+Cynosure", out.getvalue())
        self.assertIn("Record schema", out.getvalue())


class UsageWindowTests(unittest.TestCase):
    def _app(self):
        data = Path(tempfile.mkdtemp(prefix="fpfa-usage-ui-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"

        from fpfa.paths import write_config
        
        write_config({"key_backend": "file"})
        root = Loop()
        self.addCleanup(root.destroy)
        app = root.open_desk()
        root.update()
        return app

    def test_slash_usage_posts_the_report_and_the_menu_has_the_entries(self):
        app = self._app()
        app.ask_claude.set(False)
        app.start_sample_di()
        app.pump()
        project_id = app.project["id"]
        app.record.log_event(project_id, "turn", {"usage": {"rounds": 2, "input_tokens": 1200, "output_tokens": 300},
                                                   "delegations": 1, "checks": 1, "cancelled": False}, agent="lead")
        app.send_chat("/usage")
        app.pump()
        thread = app.thread_text()
        self.assertIn("Usage and cost for", thread)
        self.assertIn("lead turn, 1 delegation, 1 check", thread)
        self.assertIn("Estimated cost $", thread)
        self.assertIn("/usage", app.project["chat"][-2]["text"])
        # About and versions: the page reads this text from the server's /api/text/about.
        from fpfa.web.server import TEXTS

        about = TEXTS["about"]()
        self.assertIn("+Cynosure", about)
        self.assertIn("Record schema 4", about)
        # The About box says what the license allows and that the output is a draft.
        self.assertIn("Proprietary License Notice", about)
        self.assertIn("engineer of record", about)


if __name__ == "__main__":
    unittest.main()
