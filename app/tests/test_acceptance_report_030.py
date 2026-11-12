"""What the app-v0.3.0 acceptance report found, held as tests against 0.3.2.

One class per finding, named for what the application must do now. The
report tested 0.3.0 (04196bd) on 2026-11-11; NEXT-STEPS.md at the repository
root says which of its findings 0.3.1 had already closed and what 0.3.2 does
about the rest.

No model is called. Where an agent takes part, it is a script written in
advance (Play, as in test_team_protocol): it calls the tools the test tells
it to, including a metric figure passed into a field that takes US units,
the way the report's live specialist did. These tests show what the
application does with such a call. They show nothing about what the live
model will call, and nothing here checks an engineering statement against a
standard. The unit conversions are checked against the definitions of the
units, written out here independently of fpfa.units.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from test_acceptance_report import _claim_lines, _findings, _planned, _reply  # noqa: E402
from test_coherence import _run_plan, _seed_inputs  # noqa: E402
from test_team import _record  # noqa: E402
from test_team_protocol import Play, call, say, use  # noqa: E402

# The definitions, written out here and not read from fpfa.units: the international foot, the US gallon of
# 231 cubic inches, the pound-force, and a density in mm/min as L/min over each m².
FOOT_M = 0.3048
INCH_M = 0.0254
GALLON_L = 231 * (INCH_M * 100) ** 3 / 1000
PSI_KPA = 4.4482216152605 / INCH_M ** 2 / 1000


def _sample_di(**changes):
    from fpfa.sample_data import EXAMPLE_DI

    di = json.loads(json.dumps(EXAMPLE_DI))
    di.update(changes)
    return di


class ZoneInputTests(unittest.TestCase):
    """F-001 and what lay under it. A zone run is made on what the form holds, or not at all.

    The report ran a density of 0 and a base area of 0 to a "successful" demand of the hose alone. Under
    that, the form and the tool plan put 40 psig, 30 min, and 0 in place of a blank or a 0, so a run never
    showed what it was given.
    """

    def test_a_zero_density_or_base_area_is_refused_before_anything_runs(self):
        from fpfa.workflow import validate_di

        for name, words in (("density_gpm_ft2", "Density must be greater than 0 gpm/ft²."),
                            ("base_area_ft2", "Base area must be greater than 0 ft²."),
                            ("q_fill_gpm", "Fill flow must be greater than 0 gpm."),
                            ("supervisory_psig", "Supervisory fill must be greater than 0 psig."),
                            ("fill_minutes", "Fill time must be greater than 0 min.")):
            for bad in (0, "0", -1):
                with self.assertRaises(ValueError, msg=(name, bad)) as caught:
                    validate_di(_sample_di(**{name: bad}))
                self.assertIn(words, str(caught.exception))
        # Nothing is run or recorded on the way to the refusal.
        record = _record()
        di, basis = _seed_inputs(record, di=_sample_di(density_gpm_ft2=0))
        with self.assertRaises(ValueError):
            _run_plan(record, di, basis)
        self.assertEqual(record.calcs("job1"), [])

    def test_a_blank_the_run_needs_is_named_and_never_filled_in(self):
        from fpfa.workflow import validate_di

        blanks = _sample_di(area_increase=None, hose_gpm="", supervisory_psig=None, fill_minutes=None)
        with self.assertRaises(ValueError) as caught:
            validate_di(blanks)
        said = str(caught.exception)
        # Every problem at once, in the form's words, and what to enter.
        self.assertIn("Area increase is blank. Enter it as a fraction (0.30 is a 30 percent increase), or 0 when "
                      "no increase applies.", said)
        self.assertIn("Hose is blank. Enter the hose stream in gpm, or 0 when none is included.", said)
        self.assertIn("Supervisory fill is blank. Enter it in psig.", said)
        self.assertIn("Fill time is blank. Enter it in min.", said)

    def test_zero_is_an_answer_for_the_area_increase_and_the_hose(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.workflow import run_tool_plan

        tools, sent = run_tool_plan(ToolSession(REPO), _sample_di(area_increase=0, hose_gpm=0), {"insurer": "FM"})
        self.assertEqual((sent["density_area"]["area_increase"], sent["density_area"]["hose_gpm"]), (0, 0))
        self.assertAlmostEqual(tools["density_area"]["qd_gpm"], 0.2 * 1500)

    def test_the_run_sends_the_forms_own_values(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.workflow import run_tool_plan

        _tools, sent = run_tool_plan(ToolSession(REPO), _sample_di(supervisory_psig=25, fill_minutes=45), {"insurer": "FM"})
        self.assertEqual((sent["nitrogen_gate"]["p_psig"], sent["nitrogen_gate"]["t_min"]), (25, 45))

    def test_a_zero_passed_to_the_gas_fill_reaches_the_kernel_and_is_refused_there(self):
        from fpfa.calc_tools import ToolSession

        session = ToolSession(REPO)
        for args in ({"v_gal": 280, "p_psig": 0}, {"v_gal": 280, "t_min": 0}):
            with self.assertRaises(session.formulas.CalcError, msg=args):
                session.execute("nitrogen_gate", args)
        # Left out, they are the form's starting values, as the tool's description now says.
        omitted = session.execute("nitrogen_gate", {"v_gal": 280})
        stated = session.execute("nitrogen_gate", {"v_gal": 280, "p_psig": 40, "t_min": 30})
        self.assertEqual(omitted, stated)
        schema = next(item for item in __import__("fpfa.calc_tools", fromlist=["SCHEMAS"]).SCHEMAS
                      if item["name"] == "nitrogen_gate")
        self.assertIn("40 psig and 30 min", schema["description"])

    def test_the_form_keeps_a_zero_and_a_blank_as_typed(self):
        from desk_loop import Loop
        from test_prototype import _isolate_data

        _isolate_data()
        root = Loop()
        try:
            desk = root.open_desk()
            desk.area_increase.set("")
            desk.hose.set("0")
            desk.supervisory_psig.set("0")
            desk.fill_minutes.set("")
            di = desk.collect_di()
            self.assertEqual((di["area_increase"], di["hose_gpm"], di["supervisory_psig"], di["fill_minutes"]),
                             (None, 0.0, 0.0, None))
            # A saved blank comes back blank. A job saved before the fields existed starts from the form's values.
            desk._apply_di(dict(di))
            self.assertEqual((desk.supervisory_psig.get(), desk.fill_minutes.get()), ("0.0", ""))
            older = {key: value for key, value in di.items() if key not in ("supervisory_psig", "fill_minutes")}
            desk._apply_di(older)
            self.assertEqual((desk.supervisory_psig.get(), desk.fill_minutes.get()), ("40", "30"))
        finally:
            root.destroy()

    def test_the_lead_cannot_record_a_zero_density_from_the_chat(self):
        from fpfa.record import RecordError
        from fpfa.team import TeamSession

        record = _record()
        _seed_inputs(record)
        lead = TeamSession(REPO, record, "job1", lambda **_kwargs: None)
        with self.assertRaises(RecordError) as caught:
            lead.execute("set_input", {"name": "density_gpm_ft2", "value": "0"})
        self.assertIn("Density must be greater than 0 gpm/ft²", str(caught.exception))
        # A hose of 0 is an answer.
        self.assertEqual(lead.execute("set_input", {"name": "hose_gpm", "value": "0"})["now"].split()[0], "0")


class UnitConversionTests(unittest.TestCase):
    """F-008. The report's specialist ran 12.2 mm/min over 139 m² as 12.2 gpm/ft² over 139 ft², recorded
    1695.8 as gpm, called it L/min, and could not give gpm because nothing could convert."""

    def test_conversions_follow_the_definitions(self):
        from fpfa import units

        cases = (
            (12.2, "mm/min", "gpm/ft2", 12.2 * FOOT_M ** 2 / GALLON_L),
            (139, "m²", "ft²", 139 / FOOT_M ** 2),
            (1695.8, "L/min", "gpm", 1695.8 / GALLON_L),
            (447.98296638894806, "gpm", "L/min", 447.98296638894806 * GALLON_L),
            (40, "psig", "kPa", 40 * PSI_KPA),
            (1, "bar", "kPa", 100.0),
            (30, "m", "ft", 30 / FOOT_M),
            (150, "mm", "in", 0.150 / INCH_M),
            (1000, "L", "gal", 1000 / GALLON_L),
            (36, "m³/h", "L/min", 600.0),
            (5, "min", "s", 300.0),
        )
        for value, source, target, expected in cases:
            result = units.convert(value, source, target)
            self.assertAlmostEqual(result["result"]["value"], expected, places=9, msg=(value, source, target))
            self.assertEqual(result["given"]["value"], float(value))
        self.assertAlmostEqual(GALLON_L, 3.785411784, places=12)

    def test_a_conversion_that_needs_an_assumption_or_mixes_kinds_is_refused(self):
        from fpfa import units

        for args, words in (((14.7, "psia", "kPa"), "absolute pressure"),
                            ((1, "gpm", "ft²"), "gpm is a flow and ft² is an area"),
                            ((10, "ft³", "gal"), "does not convert"),
                            (("x", "m", "ft"), "takes a number")):
            with self.assertRaises(units.UnitError, msg=args) as caught:
                units.convert(*args)
            self.assertIn(words, str(caught.exception))

    def test_the_reports_case_gives_both_figures_with_a_record_for_each(self):
        from fpfa import checker, quantities
        from fpfa.calc_tools import ToolSession

        record = _record()
        _seed_inputs(record)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        density = session.execute("convert_units", {"value": 12.2, "from_unit": "mm/min", "to_unit": "gpm/ft2"})
        area = session.execute("convert_units", {"value": 139, "from_unit": "m²", "to_unit": "ft²"})
        demand = session.execute("density_area", {"density_gpm_ft2": density["result"]["value"],
                                                  "base_area_ft2": area["result"]["value"]})
        self.assertAlmostEqual(demand["q_spr_gpm"], 1695.8 / GALLON_L, places=9)
        metric = session.execute("convert_units", {"value": demand["q_spr_gpm"], "from_unit": "gpm", "to_unit": "L/min"})
        self.assertAlmostEqual(metric["result"]["value"], 1695.8, places=9)
        tools = [row["tool"] for row in record.calcs("job1")]
        self.assertEqual(tools.count("convert_units"), 3)
        self.assertEqual(tools.count("density_area"), 1)
        # Each figure is held, with its own unit, by the row it came from; the metric one by the conversion row.
        held = checker._calc_quantities(metric, {})
        self.assertTrue(quantities.has("1695.8", "L/min", held))
        self.assertFalse(quantities.has("1695.8", "gpm", held))
        recorded = next(row for row in record.calcs("job1") if row["tool"] == "density_area")
        on_demand = checker._calc_quantities(recorded["outputs"], recorded["inputs"])
        self.assertTrue(quantities.has("448.0", "gpm", on_demand))
        # The report's record: 1695.8 held as gpm, which an L/min claim cannot rest on.
        wrong = checker._calc_quantities({"q_spr_gpm": 1695.8}, {"density_gpm_ft2": 12.2, "base_area_ft2": 139})
        self.assertFalse(quantities.has("1695.8", "L/min", wrong))
        self.assertFalse(quantities.has("139", "m²", wrong))

    def test_the_designers_si_figure_is_refused_in_a_us_field(self):
        from fpfa import units
        from fpfa.calc_tools import ToolSession, designer_words

        record = _record()
        _seed_inputs(record)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        with designer_words("Canadian job: design density 12.2 mm/min over 139 m². Give demand in gpm and L/min."):
            for args in ({"density_gpm_ft2": 12.2, "base_area_ft2": 1500}, {"density_gpm_ft2": 0.2, "base_area_ft2": 139}):
                with self.assertRaises(units.UnitError, msg=args) as caught:
                    session.execute("density_area", args)
                self.assertIn("Convert it first with convert_units", str(caught.exception))
            self.assertEqual(record.calcs("job1"), [], "nothing was run or recorded")
            # A segment length in metres is held the same way, and a conversion itself is never refused.
            with designer_words("about 30 m of main"):
                with self.assertRaises(units.UnitError):
                    session.execute("zone_trapped_volume", {"segments": [{"nps": 6, "length_ft": 30}]})
            session.execute("convert_units", {"value": 12.2, "from_unit": "mm/min", "to_unit": "gpm/ft2"})
        # Outside a turn, and for a figure the designer also gave in US units, nothing is refused.
        session.execute("density_area", {"density_gpm_ft2": 12.2, "base_area_ft2": 139})
        with designer_words("139 m² (1,496 ft²)"):
            session.execute("density_area", {"density_gpm_ft2": 0.2, "base_area_ft2": 1496})

    def test_a_specialist_in_the_turn_is_held_to_the_same_rule(self):
        from fpfa.everyday import run_everyday

        record = _record()
        _seed_inputs(record)
        to_fp = use("delegate", specialist="fp-sprinkler", brief="Demand for 12.2 mm/min over 139 m², in gpm and L/min.")
        as_given = use("density_area", density_gpm_ft2=12.2, base_area_ft2=139)

        def convert_both(kwargs):
            refused = [block for message in kwargs["messages"] if message["role"] == "user"
                       and isinstance(message["content"], list) for block in message["content"]
                       if block.get("type") == "tool_result" and block.get("is_error")]
            self.assertTrue(refused and "Convert it first" in str(refused[-1]["content"]))
            return call(use("convert_units", value=12.2, from_unit="mm/min", to_unit="gpm/ft2"),
                        use("convert_units", value=139, from_unit="m²", to_unit="ft²"))

        create = Play({
            "lead": [call(to_fp), say("Done.")],
            "fp-sprinkler": [call(as_given), convert_both,
                             call(use("density_area", density_gpm_ft2=0.2994171183147561, base_area_ft2=1496.1835479226513)),
                             say("447.983 gpm, 1695.8 L/min.")],
        })
        run_everyday(REPO, create, "Canadian job: design density 12.2 mm/min over 139 m². Give demand in gpm and L/min.",
                     record=record, project_id="job1")
        demand = [row for row in record.calcs("job1") if row["tool"] == "density_area"]
        self.assertEqual(len(demand), 1, "the SI call ran nothing and recorded nothing")
        self.assertAlmostEqual(demand[0]["inputs"]["density_gpm_ft2"], 0.2994171183147561)

    def test_the_lead_records_a_figure_given_in_another_unit_and_keeps_both(self):
        from fpfa import inputs
        from fpfa.record import RecordError
        from fpfa.team import TeamSession

        record = _record()
        _seed_inputs(record)
        lead = TeamSession(REPO, record, "job1", lambda **_kwargs: None)
        out = lead.execute("set_input", {"name": "density_gpm_ft2", "value": "12.2 mm/min", "why": "stated in chat"})
        self.assertEqual(out["converted"]["given"], "12.2 mm/min")
        fact = next(row for row in record.facts("job1") if row["key"] == "density_gpm_ft2")
        self.assertAlmostEqual(inputs.decode(fact["value"]), 12.2 * FOOT_M ** 2 / GALLON_L, places=12)
        self.assertIn("given as 12.2 mm/min", fact["source"])
        conversion = next(row for row in record.calcs("job1") if row["tool"] == "convert_units")
        self.assertIn(conversion["id"], fact["source"])
        self.assertEqual(conversion["outputs"]["given"], {"value": 12.2, "unit": "mm/min"})
        area = lead.execute("set_input", {"name": "base_area_ft2", "value": "139 m²"})
        self.assertIn("ft²", area["converted"]["result"])
        # The input's own unit, a bare number, and a unit of another kind are not converted.
        own = lead.execute("set_input", {"name": "base_area_ft2", "value": "1,500 ft2"})
        self.assertNotIn("converted", own)
        with self.assertRaises(RecordError) as caught:
            lead.execute("set_input", {"name": "density_gpm_ft2", "value": "12.2 m"})
        self.assertIn("is a length, not a sprinkler design density", str(caught.exception))
        self.assertEqual(sum(1 for row in record.calcs("job1") if row["tool"] == "convert_units"), 2)

    def test_the_reply_audit_reads_a_figure_given_in_si(self):
        from fpfa.reply_audit import audit

        record = _record()
        _seed_inputs(record)
        from fpfa.calc_tools import ToolSession

        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("density_area", {"density_gpm_ft2": 12.2, "base_area_ft2": 139})
        reply = "The sprinkler demand is 1,695.8 L/min."
        self.assertEqual(audit(reply, record.snapshot("job1"))["unfound"], ["1695.8 L/min"])
        session.execute("convert_units", {"value": 447.98296638894806, "from_unit": "gpm", "to_unit": "L/min"})
        self.assertEqual(audit(reply, record.snapshot("job1"))["unfound"], [])
        # Narrative lengths, inches, hours, and counts are still not read.
        self.assertEqual(audit("A 6 in. main, 2 hours, 30 m away, in two zones.", record.snapshot("job1"))["figures"], 0)

    def test_a_figure_stored_with_its_unit_has_that_units_class(self):
        from fpfa import quantities

        self.assertEqual(quantities.in_value({"value": 1695.8, "unit": "L/min"}, strings=False),
                         {("1695.8", "lpm")})
        # A unit the module does not class leaves the figure with none, as a compound field name does.
        self.assertEqual({cls for _number, cls in quantities.in_value({"value": 0.2994, "unit": "gpm/ft²"})}, {None})
        # A kernel output that names its unit once for several figures is not a pair, and reads as before.
        self.assertIn(("4", None), quantities.in_value({"unit": "pct_obs_per_ft", "sh": 4.0, "sc_max": 1.0}))


class CheckerReasonTests(unittest.TestCase):
    """F-007, and the parser under it. The checker's reasons were thrown away, so a specialist revising a
    finding the check did not support could not tell why. And a verdict line in bold, or "Not Supported",
    was read as no verdict at all."""

    def _check(self, record, answer, **options):
        from fpfa import checker

        def create(**kwargs):
            return _reply(answer(_claim_lines(kwargs)))

        return checker.check_record(REPO, record, "job1", create, **options)

    def test_the_checkers_reason_is_kept_apart_from_the_applications(self):
        from fpfa import checker, team_panel

        record, calcs = _planned()
        _findings(record, calcs, 4)
        # The live reply's own form (checker-parser-diagnostic.json): the verdict, the quoted cite, the reason.
        outcome = self._check(record, lambda lines: "\n".join(
            f'{n}. Not supported. Cite: "zone_gal=281.346" (marker {n}: the cite does not state statement {n})'
            for n, _text in lines))
        for row in outcome["rows"]:
            self.assertEqual(row["checker_reason"], f"marker {row['n']}: the cite does not state statement {row['n']}")
            self.assertEqual(row["checker_cite"], "zone_gal=281.346")
            self.assertEqual(row["reason"], "", "the application's own reason stays its own")
        self.assertIn("Checker: marker 1:", outcome["verdict"])
        snapshot = record.snapshot("job1")
        why = [line for item in team_panel.finding_rows(snapshot) for line in item["why"]]
        self.assertIn(f"{checker.CHECKER_SAID}: marker 2: the cite does not state statement 2. "
                      'It quoted: "zone_gal=281.346".', why)
        event = record.latest_event("job1", checker.CHECK_EVENT)["payload"]
        self.assertIn("marker 4", event["replies"][0]["text"], "the reply is kept for an audit of the check")

    def test_a_reason_the_checker_did_not_give_is_said_and_not_made_up(self):
        from fpfa import checker

        record, calcs = _planned()
        finding = _findings(record, calcs, 1)[0]
        self._check(record, lambda lines: "1. Not supported.")
        reasons = checker.assurance(record.snapshot("job1"))[finding["id"]]["reasons"]
        self.assertIn(checker.CHECKER_SAID_NOTHING, reasons)
        # A check made before the reasons were kept says nothing about them either way.
        old = checker.assurance(record.snapshot("job1"), {"rows": [{"finding_id": finding["id"], "reason": ""}]})
        self.assertNotIn(checker.CHECKER_SAID_NOTHING, old[finding["id"]]["reasons"])

    def test_a_verdict_line_in_any_common_form_is_read(self):
        record, calcs = _planned()
        _findings(record, calcs, 6)
        forms = ["1. **Supported**. Cite: \"x\"", "2. Not Supported. Cite: \"x\" (it lacks y)",
                 "3) Supported", "- 4. Supported. Cite: \"x\"", "`5. SUPPORTED. Cite: \"x\"`",
                 "6. Unsupported. Cite: \"x\" Reason: no figure"]
        outcome = self._check(record, lambda lines: "\n".join(forms))
        verdicts = [row["verdict"] for row in outcome["rows"]]
        self.assertEqual(verdicts, ["Supported", "Not supported", "Supported", "Supported", "Supported", "Not supported"])
        self.assertEqual(outcome["rows"][5]["checker_reason"], "no figure")

    def test_stop_is_heard_between_the_checks_requests(self):
        import threading

        from fpfa import checker
        from fpfa.claude_client import TurnCancelled

        record, calcs = _planned()
        _findings(record, calcs, checker.CLAIMS_PER_REQUEST + 2)
        stop = threading.Event()
        asked = []

        def answer(lines):
            asked.append(len(lines))
            stop.set()  # The designer presses Stop while the first request is out.
            return "\n".join(f"{n}. Supported." for n, _text in lines)

        with self.assertRaises(TurnCancelled):
            self._check(record, answer, cancel=stop)
        self.assertEqual(asked, [checker.CLAIMS_PER_REQUEST], "the second request was never sent")
        failed = record.latest_event("job1", checker.CHECK_FAILED_EVENT)["payload"]
        self.assertTrue(failed["cancelled"])
        self.assertEqual(failed["usage"]["rounds"], 1, "the request that ran was billed and is kept")
        self.assertIsNone(record.latest_event("job1", checker.CHECK_EVENT), "nothing was judged")
        self.assertEqual({row["status"] for row in record.findings("job1")}, {"open"})

    def test_the_section_check_keeps_the_reason_too(self):
        from fpfa import claim_check

        packet = {"claims": "1. NFPA 13-2025 §8.2.3 requires the trim.\n2. Exported narrative (no code section) requires 281.3 gal.",
                  "sources": "1. PACKAGE ASSERTION. elect_di_trim: family El/El\n2. PACKAGE ASSERTION. zone_gal 281.3",
                  "claim_count": 2, "draft_token": "t"}
        outcome = claim_check._from_model(packet, '1. Not supported. Cite: "family El/El" (it names no section)\n'
                                                  '2. Supported. Cite: "zone_gal 281.3" (the figure is stated)')
        self.assertEqual(outcome["rows"][0]["checker_reason"], "it names no section")
        self.assertIn("(checker: it names no section)", outcome["verdict"])


class _ApiError(Exception):
    """An API error as the SDK raises it: a status, the error code and message from the body, the request id."""

    def __init__(self, status, *, code=None, message="", retry_after=None, request_id=None):
        super().__init__(f"Error code: {status} - {message}")
        self.status_code = status
        self.error_code = code
        self.api_message = message
        self.request_id = request_id
        self.workspace_id = "wrkspc_test"
        headers = {"retry-after": retry_after} if retry_after is not None else {}
        self.response = SimpleNamespace(headers=headers)


def _fake_client(outcomes):
    """An AnthropicMessages whose requests return or raise the outcomes in order. Never reaches the network."""
    from fpfa.claude_client import AnthropicMessages

    client = AnthropicMessages("sk-ant-test-not-sent")
    queue = list(outcomes)

    class Messages:
        calls = 0

        def create(self, **_kwargs):
            Messages.calls += 1
            item = queue.pop(0) if queue else SimpleNamespace(content=[])
            if isinstance(item, BaseException):
                raise item
            return item

    client._client = SimpleNamespace(messages=Messages())
    return client, Messages


class ApiClientTests(unittest.TestCase):
    """The known gaps LIV-R2, LIV-R5, and LIV-U2, and the time on the model the report could not use.

    No request leaves the machine: the provider is a stand-in that raises the errors the API documents.
    """

    def test_the_monthly_spend_cap_is_not_sent_again(self):
        from unittest.mock import patch

        from fpfa.claude_client import SpendLimitReached

        said = ("You have reached your API usage limits: your organization has crossed its monthly API usage threshold, "
                "set based on your organization's API tier. You will regain access on 2026-12-01 at 00:00 UTC.")
        client, messages = _fake_client([_ApiError(429, code="enforced_spend_limit_reached", message=said,
                                                   request_id="req_cap")])
        with patch("fpfa.claude_client.time.sleep") as sleep:
            with self.assertRaises(SpendLimitReached) as caught:
                client.create(max_tokens=8, messages=[])
        self.assertEqual(messages.calls, 1, "the report's scripted cap was sent five times")
        sleep.assert_not_called()
        self.assertIn("monthly API spend cap", str(caught.exception))
        self.assertIn("You will regain access on 2026-12-01", str(caught.exception))
        self.assertEqual(caught.exception.request_id, "req_cap")
        # The same 429 told by the body the SDK kept, and a plain rate limit, which is still sent again.
        body_only = _ApiError(429, message=said)
        body_only.error_code = None
        body_only.body = {"error": {"type": "rate_limit_error", "message": said,
                                    "details": {"error_code": "enforced_spend_limit_reached"}}}
        client, messages = _fake_client([body_only])
        with self.assertRaises(SpendLimitReached):
            client.create(max_tokens=8, messages=[])
        client, messages = _fake_client([_ApiError(429, retry_after="3")])
        with patch("fpfa.claude_client.time.sleep") as sleep:
            client.create(max_tokens=8, messages=[])
        self.assertEqual((messages.calls, [item.args[0] for item in sleep.call_args_list]), (2, [3.0]))

    def test_a_spend_limit_the_owner_set_and_a_billing_problem_stop_in_plain_words(self):
        from fpfa.claude_client import SpendLimitReached

        for error, words in (
            (_ApiError(400, message="You have reached your specified workspace API usage limits. You will regain "
                                    "access on 2026-12-01 at 00:00 UTC."), "spend limit set on the organization"),
            (_ApiError(402, message="Your payment method was declined."), "billing problem (402)"),
        ):
            client, messages = _fake_client([error])
            with self.assertRaises(SpendLimitReached) as caught:
                client.create(max_tokens=8, messages=[])
            self.assertEqual(messages.calls, 1)
            self.assertIn(words, str(caught.exception))

    def test_a_retry_after_is_waited_out_whole_or_not_at_all(self):
        from unittest.mock import patch

        from fpfa.claude_client import RETRY_AFTER_MAX, RetryWaitTooLong

        client, messages = _fake_client([_ApiError(429, retry_after="90")])
        with patch("fpfa.claude_client.time.sleep") as sleep:
            client.create(max_tokens=8, messages=[])
        self.assertEqual([item.args[0] for item in sleep.call_args_list], [90.0], "not clipped to 30 s")
        client, messages = _fake_client([_ApiError(429, retry_after=str(int(RETRY_AFTER_MAX) + 480))])
        with patch("fpfa.claude_client.time.sleep") as sleep:
            with self.assertRaises(RetryWaitTooLong) as caught:
                client.create(max_tokens=8, messages=[])
        sleep.assert_not_called()
        self.assertEqual(messages.calls, 1)
        self.assertIn(f"{int(RETRY_AFTER_MAX) + 480} s", str(caught.exception))

    def test_stop_ends_a_wait_to_send_again(self):
        import threading
        import time

        from fpfa.claude_client import TurnCancelled, run_tool_loop

        client, messages = _fake_client([_ApiError(529, retry_after="25")])
        client.cancel = threading.Event()
        threading.Timer(0.2, client.cancel.set).start()
        started = time.monotonic()
        with self.assertRaises(TurnCancelled):
            client.create(max_tokens=8, messages=[])
        self.assertLess(time.monotonic() - started, 5.0, "the 25 s wait ended when Stop was pressed")
        self.assertEqual(messages.calls, 1)
        # A cancel heard in such a wait carries the rounds of the loop that ran before it.
        replies = [SimpleNamespace(stop_reason="end_turn", content=[], usage=SimpleNamespace(
            input_tokens=10, output_tokens=5, cache_read_input_tokens=0, cache_creation_input_tokens=0))]

        def create(**_kwargs):
            if replies:
                return SimpleNamespace(stop_reason="tool_use", usage=replies.pop(0).usage,
                                       content=[SimpleNamespace(type="tool_use", id="t1", name="noop", input={})])
            raise TurnCancelled("Cancelled by the designer while waiting to send a refused request again.")

        with self.assertRaises(TurnCancelled) as caught:
            run_tool_loop(create, system="s", user_text="u", tools=[], execute=lambda name, args: {})
        self.assertEqual(caught.exception.usage["rounds"], 1)

    def test_every_request_id_is_kept_and_written_to_the_job(self):
        from unittest.mock import patch

        from fpfa.desk import Desk
        from fpfa.usage_report import REQUESTS_EVENT, report_text

        answered = SimpleNamespace(content=[], _request_id="req_ok", _workspace_id="wrkspc_dc")
        client, _messages = _fake_client([_ApiError(529, request_id="req_busy"), answered])
        with patch("fpfa.claude_client.time.sleep"):
            client.create(max_tokens=8, messages=[])
        self.assertEqual([(item["id"], item["status"]) for item in client.requests], [("req_busy", 529), ("req_ok", "ok")])
        self.assertEqual(client.requests[1]["workspace"], "wrkspc_dc")

        # A streamed reply's id is the stream's: its final message carries none of its own.
        class Stream:
            request_id = "req_streamed"
            workspace_id = "wrkspc_dc"

            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def __iter__(self):
                return iter(())

            def get_final_message(self):
                return SimpleNamespace(content=[])

        client._client = SimpleNamespace(messages=SimpleNamespace(stream=lambda **_kwargs: Stream()))
        client.streaming(lambda _event: None)(max_tokens=8, messages=[])
        self.assertEqual(client.requests[-1]["id"], "req_streamed")

        record = _record()
        record.ensure_project("job1", "Ids")
        record.log_event("job1", "turn", {"usage": {"rounds": 3, "input_tokens": 10, "output_tokens": 5}}, agent="lead")
        desk = SimpleNamespace(record=record, _note_retries=lambda *_args: None)
        Desk._note_client(desk, "job1", client)
        event = record.latest_event("job1", REQUESTS_EVENT)["payload"]
        self.assertEqual(event["count"], 3)
        text = report_text(record, "job1")
        self.assertIn("Request ids: 3 on the record", text)
        self.assertIn("billed to workspace wrkspc_dc", text)

    def test_a_check_inside_a_turn_is_counted_once_for_time(self):
        from fpfa.usage_report import job_seconds, job_totals, usage_events

        record = _record()
        record.ensure_project("job1", "Timed")
        use_row = {"rounds": 1, "input_tokens": 100, "output_tokens": 10}
        record.log_event("job1", "turn", {"usage": use_row, "checks": 1, "seconds": 100.0}, agent="lead")
        record.log_event("job1", "record_check", {"usage": use_row, "seconds": 20.0, "within_turn": True}, agent="qa-specialist")
        record.log_event("job1", "record_check", {"usage": use_row, "seconds": 10.0}, agent="qa-specialist")
        rows = usage_events(record, "job1")
        self.assertEqual(job_seconds(rows), 110.0, "the report's CHAT-01 read 10 min 18 s for a 9 min 06 s wait")
        self.assertEqual(job_totals(rows)["input_tokens"], 300, "the check's tokens are still counted")


if __name__ == "__main__":
    unittest.main()
