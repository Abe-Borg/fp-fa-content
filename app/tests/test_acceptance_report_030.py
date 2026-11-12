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

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

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


if __name__ == "__main__":
    unittest.main()
