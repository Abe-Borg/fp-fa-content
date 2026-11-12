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


class IdentityTests(unittest.TestCase):
    """The calc-code identity and the content fingerprint say what the content is, not which system wrote the
    files. The report's Windows seed carried the tag's kernel with CRLF line endings and so another identity
    than the same commit on Linux, and a calculation whose identity differs from the installed pack's is out
    of date."""

    FOLDERS = ("skills", "roles", "modes", "corpus", "specs", "calcs")

    def _copy(self, endings: bytes) -> Path:
        """The content folders copied to a new root with every text file's line endings rewritten."""
        root = Path(tempfile.mkdtemp(prefix="fpfa-acceptance-pack-"))
        for folder in self.FOLDERS:
            for path in sorted((REPO / folder).rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
                    continue
                data = path.read_bytes()
                if b"\0" not in data:
                    data = data.replace(b"\r\n", b"\n").replace(b"\n", endings)
                target = root / path.relative_to(REPO)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        return root

    def test_the_same_content_with_other_line_endings_has_the_same_identity(self):
        from fpfa.calc_tools import calc_identity, content_fingerprint

        windows = self._copy(b"\r\n")
        kernel = (windows / "calcs" / "fp" / "formulas.py").read_bytes()
        self.assertIn(b"\r\n", kernel, "the copy really is a CRLF copy")
        self.assertNotEqual(kernel, (REPO / "calcs" / "fp" / "formulas.py").read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(calc_identity(windows), calc_identity(REPO))
        self.assertEqual(content_fingerprint(windows), content_fingerprint(REPO))

    def test_a_change_to_the_code_or_the_content_still_changes_it(self):
        from fpfa.calc_tools import calc_identity, content_fingerprint

        # Each copy is changed before its identity is first read: the identity is cached by folder for the
        # life of the process, which is right for an installed pack and would hide the change here.
        changed = self._copy(b"\n")
        kernel = changed / "calcs" / "fp" / "di_zone.py"
        kernel.write_bytes(kernel.read_bytes() + b"\n# one more line\n")
        other = self._copy(b"\n")
        skill = sorted((other / "skills").rglob("SKILL.md"))[0]
        skill.write_bytes(skill.read_bytes() + b"\nOne more sentence.\n")
        self.assertNotEqual(calc_identity(changed), calc_identity(REPO))
        self.assertNotEqual(content_fingerprint(changed), content_fingerprint(REPO))
        self.assertEqual(calc_identity(other), calc_identity(REPO), "a skill is not calc code")
        self.assertNotEqual(content_fingerprint(other), content_fingerprint(REPO))

    def test_a_calculation_run_on_a_crlf_copy_is_current_on_the_lf_one(self):
        """The case that would have bitten: a job run on the bundled seed, read after a content update."""
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze

        record = _record()
        di, basis = _seed_inputs(record)
        windows = self._copy(b"\r\n")
        on_seed = ToolSession(windows, record=record, project_id="job1", agent="tool-plan")
        on_seed.execute("zone_trapped_volume", {"segments": di["segments"], "length_basis": "center_to_center",
                                                "fittings_percent": None, "trim_gal": None})
        after_update = ToolSession(REPO, record=record, project_id="job1", agent="tool-plan")
        self.assertEqual(after_update.calc_identity, on_seed.calc_identity)
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual([item["state"] for item in analysis["calcs"].values()], ["current"])
        self.assertFalse(analysis["code_changed"])


class TraceGuardTests(unittest.TestCase):
    """BUG-003. With a checker that says Supported to everything, only the application's own rules are left.

    The report's seven claims and three more. No false claim may come back in
    the first group, "a row the application identified", and the claims that
    are true and that the application can match must stay there.
    """

    def _given(self, record, key: str, value: str) -> str:
        """A value the designer stated, recorded by the lead: it stands as a project input."""
        return record.record_fact("job1", kind="owner", key=key, value=value, label="GIVEN",
                                  source="designer, in chat", agent="lead")["id"]

    def _check(self, record, cases):
        from fpfa import checker

        ids = {}
        for name, text, supports in cases:
            ids[name] = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=supports, text=text)["id"]
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        tiers = checker.assurance(record.snapshot("job1"))
        return {name: (rows[ident]["verdict"], rows[ident]["basis"], tiers[ident]["tier"], rows[ident]["reason"])
                for name, ident in ids.items()}, outcome

    def test_a_figure_is_held_to_its_unit_whatever_unit_it_is_in(self):
        record, calcs = _planned()
        feet = self._given(record, "main_run", "900 ft")
        litres = self._given(record, "pump_test", "600 L/min")
        riser = self._given(record, "riser_height", "99 ft")
        lpm = self._given(record, "pump_test_b", "600 lpm")
        hose = self._given(record, "hose_run", "450 feet of hose")
        battery = self._given(record, "battery", "The panel carries a 99 Ah battery set.")
        found, outcome = self._check(record, [
            ("flow from a length", "The fill flow is 900 gpm.", [feet]),
            ("flow in words from a length", "The fill flow is nine hundred g.p.m.", [feet]),
            ("gpm from L/min", "The fill flow is 600 gpm.", [litres]),
            ("gpm from lpm", "The pump delivers 600 gpm.", [lpm]),
            ("amp-hours from feet", "The battery capacity required is 99 Ah.", [riser]),
            ("gallons from feet", "The hose holds 450 gal.", [hose]),
            ("true: a length from that length", "The main run is 900 ft.", [feet]),
            ("true: amp-hours from amp-hours", "The battery set is 99 Ah.", [battery]),
            ("true: a nominal size and a length from the takeoff", "The 6 in. main is 48 ft long.", [calcs["zone_trapped_volume"]]),
            ("true: a row count from the truth table", "The table has 32 rows.", [calcs["releasing_truth_table"]]),
        ])
        for name in ("flow from a length", "flow in words from a length", "gpm from L/min", "gpm from lpm",
                     "amp-hours from feet", "gallons from feet"):
            verdict, basis, tier, reason = found[name]
            self.assertEqual((verdict, basis, tier), ("Not supported", "", "open"), name)
            self.assertIn("figure not in the rows it cites:", reason, name)
            self.assertIn("only as another quantity", reason, name)
        for name in ("true: a length from that length", "true: amp-hours from amp-hours",
                     "true: a nominal size and a length from the takeoff", "true: a row count from the truth table"):
            self.assertEqual(found[name][:3], ("Supported", "source", "source"), name)
        self.assertEqual(found["flow in words from a length"][3],
                         "figure not in the rows it cites: 900 gpm. The rows hold 900 only as another quantity")
        self.assertEqual(len(outcome["overruled"]), 6, "the stand-in approved all six and the record keeps that it was overruled")

    def test_a_statement_the_application_can_match_nothing_in_is_not_in_the_first_group(self):
        from fpfa import checker

        record, calcs = _planned()
        truth = calcs["releasing_truth_table"]
        found, outcome = self._check(record, [
            ("false: one leg", "The solenoid releases the valve on detection alone.", [truth]),
            ("false: either leg", "The valve releases on either detection OR the pressure drop from sprinkler operation.", [truth]),
            ("true, in other words", "Release needs the detection leg AND the pressure drop from sprinkler operation, "
                                     "with the zone not isolated.", [truth]),
            ("true, quoting the record", "The record gives solenoid = (detection_leg OR manual_release) AND p_second_leg "
                                         "AND NOT isolated.", [truth]),
            ("true, quoting the right-hand side", "The valve is released on `(detection_leg OR manual_release) AND "
                                                  "p_second_leg AND NOT isolated`.", [truth]),
            ("trim family", "The trim family is El/El.", [calcs["elect_di_trim"]]),
        ])
        # The application cannot tell the two false statements from the true one said in other words: none
        # carries anything it can hold to the record. So none of the three is in the first group, whatever the
        # checker said, and each says that only the checker's reading stands behind it.
        for name in ("false: one leg", "false: either leg", "true, in other words", "trim family"):
            verdict, basis, tier, reason = found[name]
            self.assertEqual((verdict, basis, tier), ("Supported", "checker", "checker"), name)
            self.assertEqual(reason, checker.CHECKER_ONLY_REASON, name)
        for name in ("true, quoting the record", "true, quoting the right-hand side"):
            self.assertEqual(found[name][:3], ("Supported", "source", "source"), name)
        self.assertEqual((outcome["on_source"], outcome["on_checker"], outcome["on_author"]), (2, 4, 0))
        self.assertIn("2 against a calculation record, a content-pack note, or a project input, 0 against a cite their "
                      "author wrote, 4 against such a row on the checker's reading alone", outcome["status_line"])
        self.assertIn("4 against such a row on the checker's reading alone", checker.summary_line(outcome))
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        quoted = [row["held_by_app"] for row in rows.values() if row["basis"] == "source"]
        self.assertEqual(quoted, [["the releasing record's expression"], ["the releasing record's expression"]])

    def test_the_new_group_is_named_and_explained_and_no_name_reads_as_verification(self):
        from fpfa.checker import LADDER, TIER_NOTE, TIER_TITLE, TIERS

        self.assertEqual(TIERS, ("source", "checker", "reviewed", "stated", "open"))
        self.assertEqual(TIER_TITLE["checker"], "Trace-consistent with an identified row, on the checker's reading alone")
        for text in TIER_TITLE.values():
            self.assertNotRegex(text.lower(), r"verif|checked against|approved|validated")
        self.assertIn("only the checker's reading (a second pass by the same AI model) connects the words to the row",
                      TIER_NOTE["checker"])
        where = {name: place for name, _what, place in LADDER}
        self.assertIn("first three groups", where["Trace consistency"])
        self.assertIn("In the second only the checker's reading connects them.", where["Support from an identified row"])

    def test_a_check_made_before_this_rule_cannot_keep_a_bare_statement_in_the_first_group(self):
        from fpfa import checker

        record, calcs = _planned()
        bare = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[calcs["elect_di_trim"]],
                                     text="The trim family is El/El.")
        figure = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[calcs["zone_trapped_volume"]],
                                       text="The zone total is 281.3 gal.")
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        # The check as 0.3.0 wrote it: every supported row on an identified row said "source", with no account
        # of what the application had matched.
        old = dict(outcome, rows=[{key: value for key, value in dict(row, basis="source").items() if key != "held_by_app"}
                                  for row in outcome["rows"]])
        tiers = checker.assurance(record.snapshot("job1"), old)
        self.assertEqual((tiers[bare["id"]]["tier"], tiers[figure["id"]]["tier"]), ("checker", "source"))

    def test_a_fact_a_specialist_wrote_is_not_a_project_input(self):
        """N-3. A specialist records an assumption, then a finding in the same words citing it."""
        from fpfa import checker
        from fpfa.calc_tools import ToolSession

        record, _calcs = _planned()
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        own = fp.execute("record_fact", {"kind": "assumption", "key": "pump_churn", "label": "ASSUMED",
                                         "value": "The fire pump delivers 1,250 gpm at 140 psi."})
        other = fa.execute("record_fact", {"kind": "assumption", "key": "panel_delay", "label": "ASSUMED",
                                           "value": "The panel adds 2 s between alarm and release."})
        given = self._given(record, "owner_medium", "The owner requires nitrogen at 40 psi.")
        said_back = fp.execute("record_finding", {"text": "The fire pump delivers 1,250 gpm at 140 psi.",
                                                  "label": "calculated", "supports": [own["id"]]})
        built_on = fp.execute("record_finding", {"text": "At 1,250 gpm the pump carries the 640 gpm demand with margin.",
                                                 "label": "PRACTICE", "supports": [own["id"]]})
        from_other = fp.execute("record_finding", {"text": "The panel adds 2 s between alarm and release.",
                                                   "label": "PRACTICE", "supports": [other["id"]]})
        from_designer = fp.execute("record_finding", {"text": "The supervisory gas is held at 40 psi.",
                                                      "label": "OWNER", "supports": [given]})
        packet = checker.build_record_packet(record, "job1", REPO)
        self.assertIn("RECORDED FACT assumption/pump_churn: The fire pump delivers 1,250 gpm at 140 psi. "
                      "(ASSUMED; recorded by fp-sprinkler)", packet["sources"])
        self.assertIn("PROJECT INPUT owner_medium: The owner requires nitrogen at 40 psi. (GIVEN; designer, in chat)",
                      packet["sources"])
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        tiers = checker.assurance(record.snapshot("job1"))
        # Its own fact said back: the same rule as an author's note that only repeats the claim.
        self.assertEqual((rows[said_back["id"]]["verdict"], rows[said_back["id"]]["reason"]),
                         ("Not supported", "its author's note only repeats the claim"))
        self.assertEqual(tiers[said_back["id"]]["tier"], "open")
        # A claim that goes past its own fact: 640 gpm is not in the fact, so the figure rule stops it.
        self.assertEqual(rows[built_on["id"]]["verdict"], "Not supported")
        self.assertIn("640 gpm", rows[built_on["id"]]["reason"])
        # Another contributor's fact is still the team's own statement: consistent, and never the first group.
        self.assertEqual((rows[from_other["id"]]["verdict"], rows[from_other["id"]]["basis"]), ("Supported", "author"))
        self.assertEqual(tiers[from_other["id"]]["tier"], "reviewed")
        self.assertEqual(rows[from_other["id"]]["sources"][0]["kind"], "fact")
        # What the designer stated, recorded by the lead, stands as an input.
        self.assertEqual((rows[from_designer["id"]]["verdict"], rows[from_designer["id"]]["basis"]), ("Supported", "source"))
        self.assertEqual(tiers[from_designer["id"]]["tier"], "source")

    def test_the_checker_is_told_what_the_two_new_marks_mean(self):
        role = (REPO / "roles" / "qa-specialist" / "ROLE.md").read_text(encoding="utf-8")
        self.assertIn("- RECORDED FACT is a fact a contributor wrote to the record", role)
        self.assertIn("The designer did not give it.", role)
        self.assertIn("- DECISION is an election or a judgment the team recorded on the same record.", role)

    def test_the_reply_audit_still_reads_only_the_eight_units_it_always_read(self):
        from fpfa import checker

        self.assertEqual(checker.figures("6 true rows of 32; the 4 in. cross main is 160 ft; 24 VDC; 7 Ah"), [])
        self.assertEqual(checker.figures("281.3 gal at 600 gpm in 38.1 s"), ["281.3", "600", "38.1"])
        self.assertEqual([f"{number} {unit}" for number, unit, _cls in checker._claim_figures(
            "6 true rows of 32; the 4 in. cross main is 160 ft; 24 VDC; 7 Ah")], ["4 in.", "160 ft", "24 VDC", "7 Ah"])


class EditionHoldTests(unittest.TestCase):
    """BUG-005. The job states one edition of a standard and a calculation's own cites name another.

    Nothing here says whether the rule reads the same in both. The test is
    that the application stops calling such a row "follows the project
    inputs", says what the two labels are, and leaves applicability open,
    before a rerun and after one.
    """

    HOLD = ("EDITION NOT RECONCILED. This calculation's cites are NFPA 13-2025 and the job states NFPA 13-2022. "
            "Whether the rule and the section apply in the edition the job states was not resolved here. "
            "The engineer of record confirms it.")
    LINE = ("EDITION NOT RECONCILED. The dry_delivery_screen, di_trip_to_water, hose_duration cites are NFPA 13-2025 "
            "and the job states NFPA 13-2022. Whether the rule and the section apply in the edition the job states was "
            "not resolved here. The engineer of record confirms it.")
    CITING = {"dry_delivery_screen", "di_trip_to_water", "hose_duration"}

    def _seeded(self):
        record = _record()
        di, basis = _seed_inputs(record)
        result = _run_plan(record, di, basis)
        return record, di, basis, result

    def _export(self, record) -> dict[str, str]:
        """The Design Basis as written: its whole text, and each calculation row's standing by tool."""
        from test_design_basis import _docx_text

        from fpfa.design_basis_docx import write_design_basis

        path = Path(tempfile.mkdtemp(prefix="fpfa-acceptance-")) / "basis.docx"
        write_design_basis(path, {"id": "job1", "name": "Sample"}, record.snapshot("job1"), content_root=REPO)
        text = _docx_text(path)
        standing = {}
        for line in text.splitlines():
            cells = [cell.strip() for cell in line.split(" | ")]
            if len(cells) == 7 and cells[1] == "tool-plan":
                standing[cells[0]] = cells[5]
        return {"text": text, **standing}

    def test_a_job_on_the_edition_the_calculations_cite_has_no_hold(self):
        from fpfa import checker
        from fpfa.coherence import analyze

        record, _di, _basis, result = self._seeded()
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual(analysis["edition_holds"], [])
        self.assertFalse([flag for flag in result["flags"] if "EDITION" in flag])
        written = self._export(record)
        self.assertEqual(written["dry_delivery_screen"], "follows the project inputs")
        self.assertNotIn("EDITION NOT RECONCILED", written["text"])
        self.assertFalse([gap for gap in checker.coverage(record.snapshot("job1"))["gaps"] if "EDITION" in gap])

    def test_another_edition_is_held_before_a_rerun_and_after_one(self):
        from test_coherence import _change

        from fpfa import checker, status
        from fpfa.coherence import analyze

        record, di, basis, _result = self._seeded()
        _change(record, "nfpa_13", "2022")
        for stage in ("before a rerun", "after a rerun"):
            if stage == "after a rerun":
                again = _run_plan(record, di, dict(basis, nfpa_13="2022"))
                self.assertEqual(again["flags"][0], self.LINE, "the run says it first, ahead of the cites it qualifies")
                self.assertEqual(again["warnings"], [])
            snapshot = record.snapshot("job1")
            analysis = analyze(snapshot)
            calcs = {row["id"]: row for row in record.calcs("job1")}
            self.assertEqual({calcs[ident]["tool"] for ident in analysis["edition_holds"]}, self.CITING, stage)
            self.assertEqual(analysis["stale"]["calcs"], [], "the figures are not out of date; the cite is unresolved")
            self.assertEqual({analysis["calcs"][ident]["edition_hold"] for ident in analysis["edition_holds"]}, {self.HOLD})
            written = self._export(record)
            for tool in self.CITING:
                self.assertEqual(written[tool], self.HOLD + " Its figures follow the zone inputs.", f"{tool}, {stage}")
            self.assertEqual(written["zone_trapped_volume"], "follows the project inputs", "a row that cites no edition")
            self.assertIn("INCOMPLETE DRAFT", written["text"])
            self.assertIn(self.LINE, written["text"])
            found = checker.coverage(snapshot)
            self.assertFalse(found["complete"])
            self.assertIn(self.LINE, found["gaps"])
            self.assertEqual(checker.export_reason(snapshot), "", "the draft is exported, and says what is unresolved")
            digest = status.build(snapshot)
            self.assertEqual(digest["edition_lines"], [self.LINE])
            said = status.designer_text(digest, coverage=found["gaps"])
            self.assertEqual(said.count(self.LINE), 1, "said once, under its own heading, not again as a coverage gap")
            self.assertIn("**Edition not reconciled**", said)
            self.assertIn("Running the zone again does not change this", said)
            self.assertIn("- " + self.LINE, checker.coverage_lines(snapshot), "the lead's status block carries it")

    def test_the_hold_clears_when_the_job_states_the_edition_the_cites_carry(self):
        from test_coherence import _change

        from fpfa.coherence import analyze
        from fpfa.team_panel import team_view

        record, _di, _basis, _result = self._seeded()
        _change(record, "nfpa_13", "2022")
        self.assertIn(self.LINE, team_view(record.snapshot("job1"))["unchecked"])
        _change(record, "nfpa_13", "2025")
        self.assertEqual(analyze(record.snapshot("job1"))["edition_holds"], [])
        self.assertEqual(team_view(record.snapshot("job1"))["unchecked"], [])
        self.assertEqual(self._export(record)["dry_delivery_screen"], "follows the project inputs")

    def test_what_is_compared_and_what_is_not(self):
        from fpfa.coherence import cited_editions, edition_gaps, edition_hold_text, stated_edition

        outputs = {"nfpa_basis": "NFPA 13-2025 s8.3.2.3.1.1 (a paraphrase)", "edition": 2025,
                   "note": "see NFPA 72-2025 for the releasing panel", "rows": [{"cite": "NFPA 13-2025 Table 8.2.4.3.2"}]}
        self.assertEqual(cited_editions(outputs), {"NFPA 13": ["2025"], "NFPA 72": ["2025"]})
        self.assertEqual(cited_editions({"zone_gal": 281.3, "flags": ["no cite here"]}), {})
        self.assertEqual((stated_edition("2022"), stated_edition("NFPA 13-2022"), stated_edition(2022)), ("2022", "2022", "2022"))
        self.assertIsNone(stated_edition("2019 or 2022"))
        self.assertIsNone(stated_edition(""))
        # The same edition, however the field writes it: no gap.
        self.assertEqual(edition_gaps(outputs, {"nfpa_13": "NFPA 13-2025", "nfpa_72": "2025"}), [])
        # A field that is not on the job at all is not compared. A blank one, or one that names two years, is.
        self.assertEqual(edition_gaps(outputs, {}), [])
        self.assertEqual([gap["job"] for gap in edition_gaps(outputs, {"nfpa_13": "", "nfpa_72": "2025"})],
                         ["the job states no NFPA 13 edition"])
        self.assertEqual([gap["job"] for gap in edition_gaps(outputs, {"nfpa_13": "2019 or 2022", "nfpa_72": "2025"})],
                         ['the job\'s NFPA 13 edition reads "2019 or 2022", which does not name one edition'])
        both = edition_gaps(outputs, {"nfpa_13": "2022", "nfpa_72": "2022"})
        self.assertEqual([gap["cited"] for gap in both], ["NFPA 13-2025", "NFPA 72-2025"])
        text = edition_hold_text(both)
        self.assertTrue(text.startswith("EDITION NOT RECONCILED. "))
        # It leaves the question open. It never says the rule applies, or that it does not.
        self.assertNotRegex(text.lower(), r"\bsame\b|equivalent|identical|does not apply|verified|complies")
        self.assertEqual(edition_hold_text([]), "")

    def test_a_record_with_no_basis_on_it_is_not_judged(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze

        record = _record()
        record.ensure_project("job1", "Bare")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        self.assertEqual(analyze(record.snapshot("job1"))["edition_holds"], [])


if __name__ == "__main__":
    unittest.main()
