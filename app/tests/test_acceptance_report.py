"""What the app-v0.2.0 acceptance report found and 0.3.0 had not yet closed, held as tests.

One class per defect, named for what the application must do now. The
report is the acceptance run CYN020-20261111; NEXT-STEPS.md at the
repository root reviews each of its findings against the source.

No model is called. A checker here is a function written in advance: it
returns what the test tells it to, including a reply cut off the way the
provider returned one on the report's live job. These tests show what the
application does with such a reply. They show nothing about what the live
model returns, and nothing here checks an engineering statement against a
standard.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from test_checker import yes_to_everything  # noqa: E402
from test_coherence import _run_plan, _seed_inputs  # noqa: E402


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-acceptance-")) / "fpfa.db")


def _planned():
    """A record with the sample inputs and the tool plan run on them. Returns (record, calc ids by tool)."""
    record = _record()
    di, basis = _seed_inputs(record)
    _run_plan(record, di, basis)
    return record, {row["tool"]: row["id"] for row in record.calcs("job1")}


def _usage(fresh: int, out: int, read: int = 0, written: int = 0):
    return SimpleNamespace(input_tokens=fresh, output_tokens=out, cache_read_input_tokens=read,
                           cache_creation_input_tokens=written)


def _reply(text: str = "", stop_reason: str = "end_turn", usage=None):
    content = [SimpleNamespace(type="text", text=text)] if text else []
    return SimpleNamespace(stop_reason=stop_reason, content=content, usage=usage or _usage(2600, 180))


def _cut_off(**_kwargs):
    """The reply the report's observer captured on the live job: the output ceiling reached, every output
    token spent thinking, and an empty content list."""
    return _reply("", "max_tokens", _usage(30046, 4000, written=1439))


def _claim_lines(kwargs) -> list[tuple[int, str]]:
    """The numbered claims of one checker request: (number, text)."""
    claims = kwargs["messages"][0]["content"].split("sources.md")[0]
    found = []
    for line in claims.splitlines():
        head, _, rest = line.partition(". ")
        if head.isdigit():
            found.append((int(head), rest))
    return found


def _findings(record, calcs, count: int) -> list[dict]:
    """count findings, each a true statement of the sample zone's total with its own wording."""
    return [record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[calcs["zone_trapped_volume"]],
                                  text=f"Statement {index}: the zone total is 281.3 gal.") for index in range(1, count + 1)]


class UnfinishedCheckTests(unittest.TestCase):
    """BUG-006. A trace check whose reply was cut off said nothing. It must not read as "Not supported"."""

    def test_a_reply_cut_off_with_no_text_changes_no_finding_and_is_not_a_check(self):
        from fpfa import checker
        from fpfa.usage_report import job_totals, report_text, usage_events

        record, calcs = _planned()
        rows = _findings(record, calcs, 3)
        sent = {}

        def cut_off(**kwargs):
            sent.update(kwargs)
            return _cut_off()

        outcome = checker.check_record(REPO, record, "job1", cut_off)
        self.assertTrue(outcome["incomplete"])
        self.assertEqual(outcome["rows"], [])
        self.assertEqual(outcome["unjudged"], [1, 2, 3])
        self.assertEqual(outcome["stop_reason"], "max_tokens")
        self.assertIn("Trace check did not finish: the checker's reply was cut off (stop_reason max_tokens) with no "
                      "verdict on 3 of 3 findings. No finding was changed", outcome["status_line"])
        self.assertEqual([row["status"] for row in record.findings("job1")], ["open", "open", "open"])
        snapshot = record.snapshot("job1")
        self.assertIsNone(checker.latest_check(record, "job1"), "a check that was cut off is never the latest check")
        self.assertFalse(checker.check_is_current(snapshot))
        self.assertEqual(checker.check_line(snapshot),
                         "Trace check: the last run did not finish: the checker's reply was cut off (stop_reason "
                         "max_tokens). No finding was changed. Run it again.")
        self.assertIn("the last run did not finish", checker.export_reason(snapshot))
        self.assertEqual({item["tier"] for item in checker.assurance(snapshot).values()}, {"stated"})
        # It was billed, so it is counted, and the report says what it was.
        events = usage_events(record, "job1")
        self.assertEqual([(row["kind"], row["counted"], row["usage"]["output_tokens"]) for row in events],
                         [("check_incomplete", True, 4000)])
        self.assertEqual(job_totals(events)["input_tokens"], 30046)
        self.assertIn("trace check, NOT FINISHED (max_tokens)", report_text(record, "job1"))
        self.assertGreaterEqual(sent["max_tokens"], 16000, "the ceiling covers the model's thinking and its reply together")
        self.assertEqual(rows[0]["status"], "open")

    def test_the_last_complete_check_stands_when_a_later_one_is_cut_off(self):
        from fpfa import checker

        record, calcs = _planned()
        _findings(record, calcs, 2)
        good = checker.check_record(REPO, record, "job1", yes_to_everything)
        self.assertTrue(good["all_supported"])
        again = checker.check_record(REPO, record, "job1", _cut_off)
        self.assertTrue(again["incomplete"])
        self.assertEqual([row["status"] for row in record.findings("job1")], ["Supported", "Supported"])
        snapshot = record.snapshot("job1")
        self.assertEqual(checker.latest_check(record, "job1")["token"], good["token"])
        self.assertTrue(checker.check_is_current(snapshot))
        self.assertEqual(checker.check_line(snapshot), good["status_line"])
        self.assertEqual(checker.export_reason(snapshot), "")
        self.assertEqual(checker.summary_line(again),
                         "trace check: did not finish (stop_reason max_tokens); no finding was changed. Run it again.")

    def test_a_record_larger_than_one_request_is_checked_in_batches_numbered_from_one(self):
        from fpfa import checker

        record, calcs = _planned()
        rows = _findings(record, calcs, 11)
        seen: list[list[int]] = []

        def reads(**kwargs):
            lines = _claim_lines(kwargs)
            seen.append([number for number, _text in lines])
            # Not supported for one statement by its words, wherever in a request it falls.
            return _reply("\n".join(f'{number}. {"Not supported" if "Statement 10:" in text else "Supported"}. Cite: "row"'
                                    for number, text in lines))

        outcome = checker.check_record(REPO, record, "job1", reads)
        self.assertEqual(seen, [[1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3]])
        self.assertEqual(outcome["usage"]["rounds"], 2)
        self.assertEqual(outcome["usage"]["input_tokens"], 5200)
        verdicts = {row["finding_id"]: row["verdict"] for row in outcome["rows"]}
        self.assertEqual(verdicts[rows[9]["id"]], "Not supported", "the second request's claim 2 is the record's finding 10")
        self.assertEqual(sum(1 for word in verdicts.values() if word == "Supported"), 10)
        self.assertEqual([row["n"] for row in outcome["rows"]], list(range(1, 12)))
        self.assertTrue(checker.check_is_current(record.snapshot("job1")))

    def test_a_batch_that_is_cut_off_ends_the_check_and_keeps_what_was_spent(self):
        from fpfa import checker
        from fpfa.usage_report import usage_events

        record, calcs = _planned()
        _findings(record, calcs, 11)
        calls: list[int] = []

        def second_is_cut_off(**kwargs):
            calls.append(len(_claim_lines(kwargs)))
            return yes_to_everything(**kwargs) if len(calls) == 1 else _cut_off()

        outcome = checker.check_record(REPO, record, "job1", second_is_cut_off)
        self.assertTrue(outcome["incomplete"])
        self.assertEqual(outcome["cut_off_at"], [9, 10, 11])
        self.assertEqual(outcome["unjudged"], [9, 10, 11])
        # The first request's eight verdicts are not kept: a check speaks for all the findings or for none.
        self.assertEqual({row["status"] for row in record.findings("job1")}, {"open"})
        event = usage_events(record, "job1")[0]
        self.assertEqual((event["kind"], event["usage"]["rounds"], event["usage"]["output_tokens"]), ("check_incomplete", 2, 4000))

        # Cut off on the first request: the second is never sent.
        other, other_calcs = _planned()
        _findings(other, other_calcs, 11)
        sent: list[int] = []

        def first_is_cut_off(**kwargs):
            sent.append(1)
            return _cut_off()

        self.assertTrue(checker.check_record(REPO, other, "job1", first_is_cut_off)["incomplete"])
        self.assertEqual(len(sent), 1)

    def test_a_request_that_fails_after_one_finished_keeps_the_finished_ones_usage(self):
        from fpfa import checker
        from fpfa.usage_report import usage_events

        record, calcs = _planned()
        _findings(record, calcs, 11)
        calls: list[int] = []

        def second_fails(**kwargs):
            calls.append(1)
            if len(calls) == 1:
                return _reply("\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, 9)), usage=_usage(15000, 300))
            raise ConnectionError("the connection dropped")

        with self.assertRaises(ConnectionError) as caught:
            checker.check_record(REPO, record, "job1", second_fails)
        self.assertEqual(caught.exception.usage["input_tokens"], 15000)
        event = usage_events(record, "job1")[0]
        self.assertEqual((event["kind"], event["failed"], event["usage"]["rounds"], event["usage"]["input_tokens"]),
                         ("check_failed", True, 1, 15000))
        self.assertEqual({row["status"] for row in record.findings("job1")}, {"open"})
        self.assertIn("the last run failed before it returned (ConnectionError: the connection dropped)",
                      checker.check_line(record.snapshot("job1")))

    def test_a_claim_a_finished_reply_skips_is_not_a_no(self):
        from fpfa import checker

        record, calcs = _planned()
        rows = _findings(record, calcs, 3)
        checker.check_record(REPO, record, "job1", yes_to_everything)
        self.assertEqual(record.findings("job1")[1]["status"], "Supported")

        def skips_the_second(**_kwargs):
            return _reply('1. Supported. Cite: "row"\n3. Supported. Cite: "row"')

        outcome = checker.check_record(REPO, record, "job1", skips_the_second)
        self.assertNotIn("incomplete", outcome)
        row = outcome["rows"][1]
        self.assertEqual((row["verdict"], row["reason"]), ("No verdict", checker.NO_VERDICT_REASON))
        self.assertFalse(outcome["all_supported"])
        self.assertIn("2 of 3 findings are consistent with the rows they cite", outcome["status_line"])
        self.assertIn("The checker returned no verdict for: 2; they stay not checked.", outcome["status_line"])
        self.assertNotIn("Not supported or without a source", outcome["status_line"])
        # The earlier check's Supported does not stand in for this one's silence.
        self.assertEqual([item["status"] for item in record.findings("job1")], ["Supported", "open", "Supported"])
        tiers = checker.assurance(record.snapshot("job1"))
        self.assertEqual(tiers[rows[1]["id"]]["tier"], "stated")
        self.assertIn("The trace check returned no verdict for it, so it stays not checked.", tiers[rows[1]["id"]]["reasons"])

    def test_a_finding_may_rest_on_a_decision_and_goes_out_of_date_with_it(self):
        from fpfa import checker
        from fpfa.coherence import analyze

        record, _calcs = _planned()
        decision = record.record_decision("job1", text="Carry the 30 s screen as the governing time screen.",
                                          decided_by="lead", label="use best judgment")
        # PRACTICE, not a judgment label: a judgment goes to the engineer's group whatever it rests on.
        finding = record.record_finding("job1", agent="fa-releasing", label="PRACTICE", supports=[decision["id"]],
                                        text="The releasing sequence is timed against the lead's election of the time screen.")
        packet = checker.build_record_packet(record, "job1", REPO)
        self.assertIn("DECISION by lead: Carry the 30 s screen as the governing time screen.", packet["sources"])
        self.assertFalse(packet["meta"][0]["open"], "the decision is on the record")
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        row = outcome["rows"][0]
        self.assertEqual((row["verdict"], row["basis"]), ("Supported", "author"))
        self.assertEqual(row["sources"], [{"id": decision["id"], "kind": "decision", "text": "decision by lead"}])
        self.assertEqual(checker.assurance(record.snapshot("job1"))[finding["id"]]["tier"], "reviewed",
                         "a decision is the team's own statement and adds no independent source")
        record.retire_decision("job1", decision["id"], by="lead", reason="Superseded by the owner's standard.", may_retire_any=True)
        standing = analyze(record.snapshot("job1"))["findings"][finding["id"]]
        self.assertEqual(standing["state"], "stale")
        self.assertIn(f"it rests on decision [{decision['id']}], which was withdrawn", standing["reasons"])

    def test_a_support_id_on_no_table_is_said_to_the_model_that_wrote_it(self):
        from fpfa.calc_tools import ToolSession

        record, calcs = _planned()
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        good = session.execute("record_finding", {"text": "The zone total is 281.3 gal.", "label": "calculated",
                                                  "supports": [calcs["zone_trapped_volume"]]})
        self.assertNotIn("not_on_the_record", good)
        bad = session.execute("record_finding", {"text": "The riser is adequate.", "label": "use best judgment",
                                                 "supports": [calcs["zone_trapped_volume"], "0123456789abcdef"]})
        self.assertEqual(bad["not_on_the_record"], ["0123456789abcdef"])
        self.assertIn("These ids are on no table of this job's record: 0123456789abcdef.", bad["note"])
        self.assertIn("id", bad, "the finding is written all the same; the record never edits what a model wrote")
        ruled = session.execute("record_decision", {"text": "Elect the screen.", "label": "use best judgment",
                                                    "supports": ["feedfacefeedface"]})
        self.assertEqual(ruled["not_on_the_record"], ["feedfacefeedface"])

    def test_the_section_check_says_a_cut_off_reply_did_not_finish(self):
        from fpfa import claim_check
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        packet = claim_check.build_packet(run_di_zone(REPO, dict(EXAMPLE_DI), dict(EXAMPLE_BASIS)))
        count = packet["claim_count"]
        cut = claim_check.judge(REPO, packet, _cut_off)
        self.assertTrue(cut["incomplete"])
        self.assertFalse(cut["all_supported"])
        self.assertEqual({row["verdict"] for row in cut["rows"]}, {"No verdict"})
        self.assertIn(f"The claim check did not finish (stop_reason max_tokens): {count} of {count} claims have no verdict.",
                      cut["block_reason"])
        self.assertNotIn("Not supported", cut["verdict"])

        def skips_the_last(**_kwargs):
            return _reply("\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, count)))

        partial = claim_check.judge(REPO, packet, skips_the_last)
        self.assertNotIn("incomplete", partial)
        self.assertEqual(partial["rows"][-1]["verdict"], "No verdict")
        self.assertIn(f"The checker returned no verdict for: {count}.", partial["block_reason"])


class SectionCheckUsageTests(unittest.TestCase):
    """BUG-010. The blind claim check before a Section export is a billed request. It was on no ledger."""

    # What the provider returned for the report's one live Section check, and what that costs at list price.
    LIVE = dict(fresh=7992, out=1862, read=1439)
    LIVE_USD = 0.0694958

    def _packet(self):
        from fpfa import claim_check
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        return claim_check.build_packet(run_di_zone(REPO, dict(EXAMPLE_DI), dict(EXAMPLE_BASIS)))

    def _answers(self, packet, **usage):
        def create(**_kwargs):
            text = "\n".join(f'{n}. Not supported. Cite: "row"' for n in range(1, packet["claim_count"] + 1))
            return _reply(text, usage=_usage(**usage))

        return create

    def test_a_check_that_blocks_the_export_is_still_on_the_ledger(self):
        from fpfa import claim_check
        from fpfa.usage_report import cost, job_totals, report_text, usage_events

        record = _record()
        record.ensure_project("job1", "Sample")
        packet = self._packet()
        outcome = claim_check.judge_recorded(REPO, packet, self._answers(packet, **self.LIVE), record, "job1")
        self.assertFalse(outcome["all_supported"], "the export is blocked, and the request was billed all the same")
        self.assertEqual(outcome["usage"]["output_tokens"], 1862)
        rows = usage_events(record, "job1")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual((row["kind"], row["counted"], row["agent"]), ("section_check", True, "qa-specialist"))
        self.assertEqual((row["usage"]["input_tokens"], row["usage"]["output_tokens"], row["usage"]["cache_read_input_tokens"]),
                         (7992, 1862, 1439))
        self.assertAlmostEqual(cost(job_totals(rows))["total"], self.LIVE_USD, places=7)
        text = report_text(record, "job1")
        self.assertIn("Section export claim check", text)
        self.assertIn("Estimated cost $0.0695", text)

    def test_a_check_whose_request_fails_is_on_the_ledger_as_failed_with_no_usage_guessed(self):
        from fpfa import claim_check
        from fpfa.usage_report import failures, report_text, usage_events

        record = _record()
        record.ensure_project("job1", "Sample")

        def broken(**_kwargs):
            raise TimeoutError("no answer in 300 s")

        with self.assertRaises(TimeoutError):
            claim_check.judge_recorded(REPO, self._packet(), broken, record, "job1")
        rows = usage_events(record, "job1")
        self.assertEqual([(row["kind"], row["failed"], row["usage"]["output_tokens"]) for row in rows],
                         [("section_check", True, 0)])
        self.assertEqual(failures(rows), {"count": 1, "kinds": ["section_check"]})
        self.assertIn("Section export claim check, FAILED", report_text(record, "job1"))

    def test_a_record_that_cannot_be_written_does_not_hide_the_verdicts(self):
        from fpfa import claim_check

        packet = self._packet()
        outcome = claim_check.judge_recorded(REPO, packet, self._answers(packet, **self.LIVE), None, "job1")
        self.assertEqual(len(outcome["rows"]), packet["claim_count"])

    def test_the_window_writes_the_checks_usage_to_the_jobs_record(self):
        from desk_loop import Loop
        from test_prototype import _isolate_data

        from fpfa.usage_report import usage_events

        _isolate_data()
        loop = Loop()
        try:
            desk = loop.open_desk()
            loop.update()
            desk.send_chat("/sample-di")
            loop.update()
            packet = self._packet()
            with self.assertRaises(RuntimeError) as blocked:
                desk.export_to(Path(tempfile.mkdtemp(prefix="fpfa-acceptance-")) / "section.docx",
                               create=self._answers(packet, **self.LIVE))
            self.assertIn("is blocked until every claim is Supported", str(blocked.exception))
            rows = [row for row in usage_events(desk.record, desk.project["id"]) if row["kind"] == "section_check"]
            self.assertEqual(len(rows), 1)
            self.assertEqual((rows[0]["usage"]["input_tokens"], rows[0]["usage"]["output_tokens"]), (7992, 1862))
            desk.send_chat("/usage")
            loop.update()
            self.assertIn("Section export claim check", desk.thread_text())
        finally:
            loop.destroy()


if __name__ == "__main__":
    unittest.main()
