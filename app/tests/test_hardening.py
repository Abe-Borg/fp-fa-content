"""The hardening milestone: what two independent reviews found, held as tests.

Each class takes one defect a reviewer reproduced or reported against version
0.2.0 and holds the application to the corrected behaviour. No model is
called. Where an agent takes part it is a script written in advance, and a
checker is the stand-in that says Supported to everything it is shown, which
is the worst case: only the application's own rules are left.

What these tests show is what the application does. They do not show what a
live model does, and nothing here checks an engineering statement against a
standard.
"""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from team_scenario import call, say, system_text, use  # noqa: E402
from test_prototype import _isolate_data  # noqa: E402
from test_checker import yes_to_everything  # noqa: E402
from test_coherence import _change, _run_plan, _seed_inputs  # noqa: E402
from test_design_basis import _docx_text  # noqa: E402

WRONG_RELEASE = "The valve releases on detection AND low" + " air; 6 of 32 rows are true."


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "fpfa.db")


def _planned(di=None, basis=None):
    """A record with the sample inputs and the tool plan run on them. Returns (record, calc ids by tool)."""
    record = _record()
    di, basis = _seed_inputs(record, di=di, basis=basis)
    _run_plan(record, di, basis)
    return record, {row["tool"]: row["id"] for row in record.calcs("job1")}, di, basis


class StaleFiguresInAReplyTests(unittest.TestCase):
    """A flow changes from 600 to 750 gpm. Nothing that still says 600 may make 600 current."""

    def test_an_out_of_date_finding_cannot_validate_its_own_figures(self):
        from fpfa.reply_audit import audit, lines

        record, calcs, _di, _basis = _planned()
        record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[calcs["di_trip_to_water"]],
                              text="At a fill flow of 600 gpm the zone-total trip time is 38.1 s against the 30 s screen.")
        _change(record, "q_fill_gpm", 750.0)
        result = audit("The fill flow is 600 gpm and the trip time is 38.1 s.", record.snapshot("job1"),
                       said=["Does that change the answer?"])
        self.assertEqual(result["stale"], ["600 gpm", "38.1 s"])
        self.assertEqual(result["unfound"], [])
        self.assertIn("holds only on out-of-date rows: 600 gpm, 38.1 s.", lines(result)[0])
        self.assertIn("They are not the current basis.", lines(result)[0])

    def test_a_finding_with_no_basis_cannot_rescue_an_out_of_date_figure_either(self):
        """A finding that cites nothing is never marked out of date. It still cannot make the old flow current."""
        from fpfa.reply_audit import audit

        record, _calcs, _di, _basis = _planned()
        record.record_finding("job1", agent="fp-sprinkler", label="use best judgment", supports=[],
                              text="The riser delivers 600 gpm.")
        _change(record, "q_fill_gpm", 750.0)
        self.assertEqual(audit("The riser delivers 600 gpm.", record.snapshot("job1"))["stale"], ["600 gpm"])
        # The same finding does back a figure the record holds on no out-of-date row.
        record.record_finding("job1", agent="fp-sprinkler", label="use best judgment", supports=[],
                              text="The owner asked for 45 psi at the riser.")
        self.assertEqual(audit("The owner asked for 45 psi.", record.snapshot("job1")),
                         {"figures": 1, "unfound": [], "stale": [], "wording": []})

    def test_a_replaced_or_withdrawn_finding_is_an_out_of_date_row(self):
        from fpfa.reply_audit import audit

        record, calcs, _di, _basis = _planned()
        old = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[calcs["zone_trapped_volume"]],
                                    text="A what-if with 77 gal of extra branch.")
        record.retire_finding("job1", old["id"], by="fp-sprinkler", reason="The what-if was dropped.")
        self.assertEqual(audit("The what-if adds 77 gal.", record.snapshot("job1"))["stale"], ["77 gal"])

    def test_only_this_turns_words_and_a_fresh_calculation_make_an_old_figure_current(self):
        from fpfa.reply_audit import audit

        record, _calcs, _di, _basis = _planned()
        _change(record, "q_fill_gpm", 750.0)
        snapshot = record.snapshot("job1")
        reply = "The fill flow was 600 gpm."
        # The designer wrote 600 in this turn's message: it is theirs to see.
        self.assertEqual(audit(reply, snapshot, said=["The pump test gave 750 gpm, not the 600 on the form."])["stale"], [])
        # An earlier message, the lead's own earlier reply, and the record said back do not make it current.
        self.assertEqual(audit(reply, snapshot, said=["And now?", "It was 600 gpm on the form."])["stale"], ["600 gpm"])
        self.assertEqual(audit(reply, snapshot, earlier_replies=["Fill flow is 600 gpm."])["stale"], ["600 gpm"])
        said_back = [{"name": "set_input", "output": {"was": "600 gpm", "now": "750 gpm"}, "is_error": False},
                     {"name": "read_record", "output": {"summary": "q_fill_gpm 600 gpm (out of date)"}, "is_error": False}]
        self.assertEqual(audit(reply, snapshot, tool_calls=said_back)["stale"], ["600 gpm"])
        # A calculation the lead ran this turn on that value is a current result.
        fresh = [{"name": "di_trip_to_water", "output": {"q_fill_gpm": 600, "t_total_s": 38.1}, "is_error": False}]
        self.assertEqual(audit(reply, snapshot, tool_calls=fresh)["stale"], [])

    def test_a_flagged_figure_stays_flagged_when_the_lead_repeats_it(self):
        from fpfa.reply_audit import audit, flagged_before

        record, _calcs, _di, _basis = _planned()
        _change(record, "q_fill_gpm", 750.0)
        first = audit("At 600 gpm the trip time is 38.1 s.", record.snapshot("job1"))
        record.log_event("job1", "reply_audit", first, agent="app")
        self.assertEqual(flagged_before(record, "job1"), ["600 gpm", "38.1 s"])

    def test_a_reply_that_breaks_the_releasing_rule_is_called_out_with_or_without_figures(self):
        from fpfa.reply_audit import audit, lines
        from fpfa.team import team_summary

        record, _calcs, _di, _basis = _planned()
        snapshot = record.snapshot("job1")
        result = audit("The preaction valve opens on smoke detection together with low" + " air.", snapshot)
        self.assertEqual(result["figures"], 0)
        self.assertEqual(len(result["wording"]), 1)
        text = lines(result)[0]
        self.assertIn("departs from the releasing logic on the calculation record", text)
        self.assertIn("Low air is supervisory only and is never a release input.", text)
        self.assertTrue(team_summary({"text": "x"}, result).startswith("**In this reply**\n- a sentence in this reply"))
        ok = audit("Release is the detection leg AND P. Low air is supervisory only and is never a release input.", snapshot)
        self.assertEqual(ok["wording"], [])


class QuantityTests(unittest.TestCase):
    """A figure is a number and a kind of unit. A length does not back a flow."""

    def test_a_number_is_classed_by_its_unit_or_by_the_field_it_sits_in(self):
        from fpfa import quantities

        self.assertEqual(quantities.unit_class("gallons"), "gal")
        self.assertEqual(quantities.unit_class("psig"), "psi")
        self.assertEqual(quantities.unit_class("sq ft"), "ft2")
        self.assertEqual(quantities.name_class("zone_gal"), "gal")
        self.assertEqual(quantities.name_class("t_total_s"), "s")
        self.assertEqual(quantities.name_class("v_max_gal_at_limit"), "gal")
        # A unit a claim did not use to carry has a class of its own now, not one class shared by all of them.
        self.assertEqual(quantities.name_class("length_ft"), "ft")
        self.assertIsNone(quantities.name_class("density_gpm_ft2"), "a compound unit says nothing")
        self.assertIsNone(quantities.name_class("area_increase"))
        found = quantities.in_text("Hold 900 gpm for 60 minutes; 2 zones; about 38,400 gal; ratio 0.714.")
        self.assertIn(("900", "gpm"), found)
        self.assertIn(("60", "min"), found)
        self.assertIn(("2", "count"), found)
        self.assertIn(("38400", "gal"), found)
        self.assertIn(("0.714", None), found)

    def test_a_figure_is_held_as_the_same_kind_or_as_no_kind(self):
        from fpfa import quantities

        row = quantities.in_value({"length_ft": 900, "q_fill_gpm": 600, "area_increase": 0.3, "note": "cap is 500 gal"})
        self.assertTrue(quantities.has("600", "gpm", row))
        self.assertFalse(quantities.has("600", "gal", row), "600 is a flow on this row")
        self.assertFalse(quantities.has("900", "gpm", row), "900 is a length on this row")
        self.assertTrue(quantities.has("30", "percent", row), "a share held as a fraction with no unit")
        self.assertTrue(quantities.has("500", "gallons", row), "a string in the row is read as prose")
        self.assertTrue(quantities.has("12", "psi", quantities.in_text("the note says 12")), "a bare number backs anything")

    def test_the_trace_check_holds_a_claims_figure_to_its_unit(self):
        from fpfa.checker import _missing_figures, _wrong_unit

        held = [["281.3", "gal"], ["38.1", "s"], ["900", "other"], ["0.3", None]]
        numbers = ["281.3", "38.1", "900", "0.3"]
        self.assertEqual(_missing_figures("The zone total is 281.3 gal.", numbers, held), [])
        self.assertEqual(_missing_figures("The trip time is 281.3 s.", numbers, held), ["281.3 s"])
        self.assertEqual(_wrong_unit("The trip time is 281.3 s.", numbers, held), ["281.3 s"])
        self.assertEqual(_missing_figures("Hold 900 gpm.", numbers, held), ["900 gpm"])
        self.assertEqual(_missing_figures("The increase is 30 percent.", numbers, held), [])
        # With no units to go by, the lookup is by number alone, as it always was.
        self.assertEqual(_missing_figures("Hold 900 gpm.", numbers), [])


class SizeExemptionTests(unittest.TestCase):
    """475 gal of pipe and a zone total over 500. Every surface gives the same answer, from the same record."""

    def _boundary(self):
        from fpfa.sample_data import EXAMPLE_BASIS_2, EXAMPLE_DI_2
        from fpfa.workflow import run_di_zone

        record = _record()
        record.ensure_project("job1", "Boundary")
        _seed_inputs(record, di=EXAMPLE_DI_2, basis=EXAMPLE_BASIS_2)
        run = run_di_zone(REPO, EXAMPLE_DI_2, EXAMPLE_BASIS_2, record=record, project_id="job1")
        return record, run

    def test_the_recorded_screen_carries_the_zone_total_answer(self):
        from fpfa.design_basis_docx import key_figures, write_design_basis
        from fpfa.results_panel import zone_figures
        from fpfa.spec_docx import write_docx

        record, run = self._boundary()
        volume, screen = run["tools"]["zone_trapped_volume"], run["tools"]["dry_delivery_screen"]
        self.assertAlmostEqual(volume["pipe_gal"], 475.1, delta=0.05)
        self.assertAlmostEqual(volume["zone_gal"], 505.5, delta=0.05)
        self.assertFalse(volume["trim_assumed"])
        # The row on the record is the row the run used: the zone-total answer, with the pipe-only flag kept under its name.
        row = next(item for item in record.calcs("job1") if item["tool"] == "dry_delivery_screen")
        self.assertEqual(row["outputs"], screen)
        self.assertIs(row["outputs"]["nfpa_delivery_time_exempt"], False)
        self.assertIs(row["outputs"]["pipe_only_nfpa_delivery_time_exempt"], True)
        self.assertAlmostEqual(row["outputs"]["exemption_volume_gal"], volume["zone_gal"], places=9)
        self.assertEqual(row["inputs"]["zone_gal"], volume["zone_gal"])
        # The narrative, the tile, the Design Basis, and the Section export all say no.
        self.assertIn("NFPA size exemption on the zone total of 505.5 gal against the 500 gal cap: no.", run["narrative"])
        tile = {item["key"]: item for item in zone_figures(run["tools"])}["size_exemption"]
        self.assertEqual(tile["value"], "no")
        self.assertIn("Zone total of 505.5 gal against the 500 gal cap.", tile["lines"])
        line = key_figures("dry_delivery_screen", row["inputs"], row["outputs"])
        self.assertIn("size exemption on the zone total of 505.5 gal: no", line)
        self.assertNotIn("exemption yes", line)
        out = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "basis.docx"
        write_design_basis(out, {"name": "Boundary"}, record.snapshot("job1"))
        self.assertIn("size exemption on the zone total of 505.5 gal: no", _docx_text(out))
        section = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "section.docx"
        write_docx(section, {"name": "Boundary"}, run)
        self.assertIn("Zone total | 505.5 | 46.7", _docx_text(section))
        self.assertRegex(_docx_text(section), r"Zone total \| 505\.5 \|.*\| 500 \| No")

    def test_the_screen_follows_the_takeoff_and_goes_out_of_date_with_it(self):
        from fpfa.coherence import analyze

        record, _run = self._boundary()
        rows = {item["tool"]: item for item in record.calcs("job1")}
        self.assertIn(rows["zone_trapped_volume"]["id"], rows["dry_delivery_screen"]["depends"])
        _change(record, "trim_gal", 9.5)
        states = analyze(record.snapshot("job1"))["calcs"]
        self.assertEqual(states[rows["zone_trapped_volume"]["id"]]["state"], "stale")
        self.assertEqual(states[rows["dry_delivery_screen"]["id"]]["state"], "stale")
        self.assertIn("it took a figure from zone_trapped_volume", states[rows["dry_delivery_screen"]["id"]]["reasons"][0])

    def test_an_assumed_trim_qualifies_a_yes(self):
        from fpfa.results_panel import zone_figures

        _record_, _calcs, di, basis = _planned()
        from fpfa.workflow import run_di_zone

        run = run_di_zone(REPO, di, basis)
        said = ("NFPA size exemption on the zone total of 281.3 gal against the 500 gal cap: yes. That zone total includes "
                "trim that is ASSUMED, so the answer holds only while the measured trim and fittings keep the zone total "
                "at or under the cap.")
        self.assertIn(said, run["narrative"])
        tile = {item["key"]: item for item in zone_figures(run["tools"])}["size_exemption"]
        self.assertEqual(tile["value"], "yes")
        self.assertIn("That zone total includes trim that is ASSUMED, so the answer holds only while the measured trim and "
                      "fittings keep the zone total at or under the cap.", tile["lines"])

    def test_a_pipe_only_screen_never_says_the_exemption_is_met(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.design_basis_docx import key_figures
        from fpfa.workflow import exemption_answer

        session = ToolSession(REPO, agent="fp-sprinkler")
        under = [{"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 288}]   # about 475 gal, by nominal size
        times = {"t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM"}
        got = session.execute("dry_delivery_screen", {"segments": under, "q_fill_gpm": 600, "system_type": "di", **times})
        self.assertIsNone(got["nfpa_delivery_time_exempt"])
        self.assertTrue(got["pipe_only_nfpa_delivery_time_exempt"])
        self.assertEqual(got["exemption_status"], "not determined")
        self.assertEqual(exemption_answer(got), "not determined")
        self.assertIn("size exemption: not determined. This record is a pipe-only screen", key_figures("dry_delivery_screen", {}, got))
        over = [{"d_in": 6.357, "length_ft": 320}]                                         # about 528 gal of pipe alone
        got = session.execute("dry_delivery_screen", {"segments": over, "q_fill_gpm": 600, "system_type": "di", **times})
        self.assertIs(got["nfpa_delivery_time_exempt"], False, "the pipe alone is over the cap, which settles it")
        self.assertEqual(exemption_answer(got), "no")
        # A row recorded before the screen was handed the zone total holds only the kernel's pipe-only flag.
        legacy = {"volume_gal": 475.0, "nfpa_delivery_time_exempt": True, "nfpa_size_cap_gal": 500.0, "t_total_s": 57.5,
                  "limit_s": 30.0, "limit_basis": "FM", "passes_screen": False, "nfpa_basis": ""}
        self.assertEqual(exemption_answer(legacy), "not determined")
        self.assertNotIn("exemption: yes", key_figures("dry_delivery_screen", {}, legacy))

    def test_a_rounded_zone_total_cannot_cross_the_cap(self):
        """A takeoff of 500.3 gal passed to the screen as 500. The answer is the takeoff's, not the rounding's."""
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.sample_data import EXAMPLE_DI

        record = _record()
        di = copy.deepcopy(EXAMPLE_DI)
        di.update(segments=[{"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 300.45}],
                  trim_gal=5.0, fittings_percent=0)
        _seed_inputs(record, di=di)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        takeoff = session.execute("zone_trapped_volume", {"segments": di["segments"], "fittings_percent": 0, "trim_gal": 5.0})
        self.assertTrue(500.0 < takeoff["zone_gal"] < 500.5, takeoff["zone_gal"])
        times = {"t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "qod": False}
        screen = session.execute("dry_delivery_screen", {"segments": di["segments"], "q_fill_gpm": 600,
                                                         "system_type": "di", "zone_gal": 500, **times})
        self.assertIs(screen["nfpa_delivery_time_exempt"], False, "500 is within the match's tolerance and across the cap")
        self.assertEqual(screen["exemption_volume_gal"], takeoff["zone_gal"])
        self.assertIn("zone_gal was passed as 500. The calculation used the figure on the zone_trapped_volume record "
                      f"[{takeoff['record_id']}] itself", screen["figure_taken_from_the_record"])
        row = next(item for item in record.calcs("job1") if item["id"] == screen["record_id"])
        self.assertEqual(row["inputs"]["zone_gal"], takeoff["zone_gal"], "the record holds the figure the call ran on")
        self.assertIn(takeoff["record_id"], row["depends"])
        self.assertEqual(analyze(record.snapshot("job1"))["calcs"][row["id"]]["state"], "current")
        # The same rounded call again replays that row. The takeoff's own figure passed as it is needs no note.
        again = session.execute("dry_delivery_screen", {"segments": di["segments"], "q_fill_gpm": 600,
                                                        "system_type": "di", "zone_gal": 500, **times})
        self.assertEqual(again["record_id"], screen["record_id"])
        exact = session.execute("dry_delivery_screen", {"segments": di["segments"], "q_fill_gpm": 600,
                                                        "system_type": "di", "zone_gal": takeoff["zone_gal"], **times})
        self.assertEqual(exact["record_id"], screen["record_id"])
        self.assertNotIn("figure_taken_from_the_record", exact)
        # A figure that matches no takeoff is used as passed, and the record says it is another case.
        other = session.execute("dry_delivery_screen", {"segments": di["segments"], "q_fill_gpm": 600,
                                                        "system_type": "di", "zone_gal": 450, **times})
        self.assertIs(other["nfpa_delivery_time_exempt"], True)
        self.assertEqual(other["exemption_volume_gal"], 450)
        self.assertIn("matches no recorded zone_trapped_volume result", other["differs_from_project_inputs"])

    def test_a_rounded_volume_cannot_carry_the_trip_time_across_its_limit(self):
        """The same takeoff, 500.3 gal, passed to the trip time as 500. At 1500 gpm with 10 s of delays the
        exact volume misses the 30 s screen by a hundredth of a second and the rounded one meets it. The
        expected time is the tool's own stated sum on the takeoff's recorded volume, not on the rounding."""
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.sample_data import EXAMPLE_DI

        record = _record()
        di = copy.deepcopy(EXAMPLE_DI)
        di.update(segments=[{"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 300.45}],
                  trim_gal=5.0, fittings_percent=0, q_fill_gpm=1500, t_detect_s=8, t_release_s=2, t_exhaust_s=0)
        _seed_inputs(record, di=di)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        takeoff = session.execute("zone_trapped_volume", {"segments": di["segments"], "fittings_percent": 0, "trim_gal": 5.0})
        self.assertTrue(500.0 < takeoff["zone_gal"] < 500.5, takeoff["zone_gal"])
        times = {"q_fill_gpm": 1500, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM"}
        exact = session.execute("di_trip_to_water", {"v_gal": takeoff["zone_gal"], **times})
        self.assertNotIn("figure_taken_from_the_record", exact)
        rounded = session.execute("di_trip_to_water", {"v_gal": 500, **times})
        expected = 8 + 2 + 0 + 60.0 * takeoff["zone_gal"] / 1500
        self.assertGreater(expected, 30.0)
        self.assertAlmostEqual(rounded["t_total_s"], expected, places=9)
        self.assertIs(rounded["passes_screen"], False, "500 gal would give exactly 30.0 s, which meets the screen")
        self.assertEqual(rounded["record_id"], exact["record_id"], "one calculation, so one row")
        self.assertIn("v_gal was passed as 500. The calculation used the figure on the zone_trapped_volume record "
                      f"[{takeoff['record_id']}] itself", rounded["figure_taken_from_the_record"])
        trips = [row for row in record.calcs("job1") if row["tool"] == "di_trip_to_water"]
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]["inputs"]["v_gal"], takeoff["zone_gal"], "the record holds the figure the call ran on")
        self.assertEqual(analyze(record.snapshot("job1"))["calcs"][trips[0]["id"]]["state"], "current")
        # The gas fill takes the same volume the same way: the rounded call is the exact call's row.
        fill = session.execute("nitrogen_gate", {"v_gal": takeoff["zone_gal"], "p_psig": 40, "t_min": 30})
        again = session.execute("nitrogen_gate", {"v_gal": 500, "p_psig": 40, "t_min": 30})
        self.assertEqual(again["record_id"], fill["record_id"])
        # A volume that matches no takeoff is used as passed and is marked as another case, as before.
        other = session.execute("di_trip_to_water", {"v_gal": 450, **times})
        self.assertIs(other["passes_screen"], True)
        self.assertIn("matches no recorded zone_trapped_volume result", other["differs_from_project_inputs"])

    def test_the_sprinkler_role_tells_the_specialist_to_pass_the_zone_total(self):
        text = (REPO / "roles" / "fp-sprinkler" / "ROLE.md").read_text(encoding="utf-8")
        self.assertIn("pass its `zone_gal` to `dry_delivery_screen`", text)
        self.assertIn("Do not state the exemption from a pipe-only screen", text)


class WhatAChangeReachesTests(unittest.TestCase):
    """What the record can reconcile by itself, and what it says when it cannot."""

    def test_a_calculation_made_by_other_calc_code_is_out_of_date(self):
        from fpfa.checker import export_reason
        from fpfa.coherence import analyze

        record, calcs, _di, _basis = _planned()
        now = record.context["calc_identity"]
        self.assertEqual(len(now), 16)
        self.assertFalse(analyze(record.snapshot("job1"))["any_stale"])
        # A content update replaced a kernel file: the pack's calc code has another identity now.
        record.set_context(calc_identity="0123456789abcdef")
        analysis = analyze(record.snapshot("job1"))
        self.assertTrue(analysis["code_changed"])
        self.assertEqual(sorted(analysis["stale"]["calcs"]), sorted(calcs.values()))
        reason = analysis["calcs"][calcs["zone_trapped_volume"]]["reasons"][0]
        self.assertEqual(reason, f"the calc code changed after it ran (it was computed by calc code {now}; "
                                 "the installed content pack's is 0123456789abcdef)")
        self.assertIn("out of date", export_reason(record.snapshot("job1")))
        # A snapshot that does not say what is installed judges nothing.
        bare = dict(record.snapshot("job1"), context={})
        self.assertFalse(analyze(bare)["any_stale"])

    def test_a_calculation_on_a_tool_the_record_does_not_track_says_so(self):
        from fpfa import checker, status
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import UNCHECKED_NOTE, analyze

        record, _calcs, _di, _basis = _planned()
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        got = session.execute("fp_calc", {"op": "pipe_volume", "inputs": {"segments": [{"d_in": 4.26, "length_ft": 100}]}})
        self.assertIn("Not tied to the project inputs", got["not_tied_to_project_inputs"])
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[got["record_id"]],
                                        text="A 100 ft run of 4 in. pipe holds 74.0 gal.")
        before = analyze(record.snapshot("job1"))
        self.assertEqual(before["unchecked"], [])
        self.assertFalse(before["calcs"][got["record_id"]]["tracked"])
        import time

        time.sleep(1.1)   # the record's clock is whole seconds
        _change(record, "q_fill_gpm", 750.0)
        snapshot = record.snapshot("job1")
        after = analyze(snapshot)
        self.assertEqual(after["unchecked"], [got["record_id"]])
        self.assertEqual(after["calcs"][got["record_id"]]["state"], "current", "it is not called out of date: nobody knows")
        self.assertEqual(after["calcs"][got["record_id"]]["unchecked"], UNCHECKED_NOTE)
        digest = status.build(snapshot)
        self.assertEqual([row["tool"] for row in digest["unchecked"]], ["fp_calc"])
        self.assertIn("The application cannot reconcile these", status.designer_text(digest))
        self.assertIn("Calculations the application cannot reconcile after an input change", status.lead_text(digest))
        checker.check_record(REPO, record, "job1", yes_to_everything)
        tier = checker.assurance(record.snapshot("job1"))[finding["id"]]
        self.assertEqual(tier["tier"], "open", "consistent with a row the record cannot vouch for any more")
        self.assertTrue(any(reason.startswith("Not reconciled by the application") for reason in tier["reasons"]))
        self.assertTrue(any("cannot reconcile" in gap for gap in checker.coverage(record.snapshot("job1"))["gaps"]))


    def test_running_an_untracked_calculation_again_reconciles_it(self):
        """The views tell the author to run it again. Doing that has to clear what they said."""
        import time

        from fpfa import checker, status
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze

        record, _calcs, _di, _basis = _planned()
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        args = {"op": "pipe_volume", "inputs": {"segments": [{"d_in": 4.26, "length_ft": 100}]}}
        first = session.execute("fp_calc", args)
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[first["record_id"]],
                                        text="A 100 ft run of 4 in. pipe holds 74.0 gal.")
        time.sleep(1.1)   # the record's clock is whole seconds
        _change(record, "q_fill_gpm", 750.0)
        time.sleep(1.1)
        self.assertEqual(analyze(record.snapshot("job1"))["unchecked"], [first["record_id"]])
        # Run again with the same arguments: the row is replayed, and that is the author saying they still hold.
        again = session.execute("fp_calc", args)
        self.assertEqual(again["record_id"], first["record_id"])
        self.assertEqual(analyze(record.snapshot("job1"))["unchecked"], [])
        self.assertEqual(status.build(record.snapshot("job1"))["unchecked"], [])
        # A second change, answered this time with other arguments: a new row, and the finding moved onto it.
        time.sleep(1.1)
        _change(record, "q_fill_gpm", 800.0)
        time.sleep(1.1)
        other = session.execute("fp_calc", {"op": "pipe_volume", "inputs": {"segments": [{"d_in": 4.26, "length_ft": 120}]}})
        self.assertNotEqual(other["record_id"], first["record_id"])
        record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[other["record_id"]],
                              text="A 120 ft run of 4 in. pipe holds 88.8 gal.", replaces=finding["id"])
        snapshot = record.snapshot("job1")
        # The old row is still marked where it is listed. Nothing current rests on it, so nobody has to act on it.
        self.assertEqual(analyze(snapshot)["unchecked"], [first["record_id"]])
        self.assertEqual(status.build(snapshot)["unchecked"], [])
        self.assertFalse(any("cannot reconcile" in gap for gap in checker.coverage(snapshot)["gaps"]))


class AssuranceTests(unittest.TestCase):
    """What a tier is called, what earns it, and what the application says it never did."""

    def test_a_wrong_releasing_finding_is_not_supported_whatever_the_checker_says(self):
        from fpfa import checker

        record, calcs, _di, _basis = _planned()
        wrong = record.record_finding("job1", agent="fa-releasing", label="calculated",
                                      supports=[calcs["releasing_truth_table"]], text=WRONG_RELEASE)
        right = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                      supports=[calcs["zone_trapped_volume"]], text="The zone total is 281.3 gal.")
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        self.assertEqual(rows[wrong["id"]]["verdict"], "Not supported")
        self.assertEqual(rows[wrong["id"]]["reason"], checker.RELEASE_WORDING_REASON)
        self.assertIn("This finding says otherwise.", rows[wrong["id"]]["reason"])
        self.assertEqual(rows[right["id"]]["verdict"], "Supported")
        # The checker approved it. The record keeps that it was overruled, and the status line says so.
        self.assertEqual(outcome["overruled"], [{"n": 1, "finding_id": wrong["id"], "checker_said": "Supported"}])
        self.assertIn("the application's own rules set aside the checker's verdict on 1 finding", outcome["status_line"])
        tiers = checker.assurance(record.snapshot("job1"))
        self.assertEqual((tiers[wrong["id"]]["tier"], tiers[right["id"]]["tier"]), ("open", "source"))

    def test_a_figure_the_cited_row_holds_as_another_quantity_is_not_supported(self):
        from fpfa import checker

        record, calcs, _di, _basis = _planned()
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                        supports=[calcs["zone_trapped_volume"]], text="The trip-to-water time is 281.3 s.")
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        row = outcome["rows"][0]
        self.assertEqual(row["finding_id"], finding["id"])
        self.assertEqual(row["verdict"], "Not supported")
        self.assertEqual(row["reason"], "figure not in the rows it cites: 281.3 s. The rows hold 281.3 only as another quantity")

    def test_no_tier_is_named_as_verification(self):
        from fpfa.checker import LADDER, TIER_NOTE, TIER_TITLE

        for text in list(TIER_TITLE.values()):
            self.assertNotRegex(text.lower(), r"verif|checked against|approved|validated")
        self.assertIn("It is not verification: the standard was not opened, and no engineer has reviewed it.", TIER_NOTE["source"])
        self.assertIn("a second pass by the same AI model", TIER_NOTE["source"])
        names = [name for name, _what, _where in LADDER]
        self.assertEqual(names[-2:], ["Verification against the primary standard", "Qualified engineering review"])
        self.assertTrue(all(where.startswith("NOT PERFORMED") for _name, _what, where in LADDER[-2:]))

    def test_a_check_made_against_other_content_has_to_be_run_again(self):
        from fpfa import checker

        record, calcs, _di, _basis = _planned()
        record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                              supports=[calcs["zone_trapped_volume"]], text="The zone total is 281.3 gal.")
        outcome = checker.check_record(REPO, record, "job1", yes_to_everything)
        self.assertEqual(outcome["content"]["content_fingerprint"], record.context["content_fingerprint"])
        self.assertTrue(checker.check_is_current(record.snapshot("job1")))
        self.assertEqual(checker.export_gate(record, "job1"), "")
        record.set_context(content_fingerprint="feedfacefeedface")
        snapshot = record.snapshot("job1")
        self.assertFalse(checker.check_is_current(snapshot))
        self.assertEqual(checker.check_line(snapshot), "Trace check: the content pack changed since the last check. Run it again.")
        self.assertEqual(checker.export_reason(snapshot), "The content pack changed after the last trace check. Run it again.")


class CoverageTests(unittest.TestCase):
    """A design basis with work missing may be exported. It may not look complete."""

    def test_a_design_basis_with_no_releasing_finding_says_so_at_its_head(self):
        from fpfa import checker
        from fpfa.design_basis_docx import write_design_basis

        record, calcs, _di, _basis = _planned()
        record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                              supports=[calcs["zone_trapped_volume"]], text="The zone total is 281.3 gal.")
        checker.check_record(REPO, record, "job1", yes_to_everything)
        self.assertEqual(checker.export_gate(record, "job1"), "", "a partial draft is still exported")
        found = checker.coverage(record.snapshot("job1"))
        self.assertFalse(found["complete"])
        self.assertIn("releasing_truth_table", found["uncovered"])
        self.assertIn("No finding rests on the releasing logic (releasing_truth_table). It was calculated and no specialist "
                      "has stated what follows from it.", found["gaps"])
        self.assertNotIn("hose_duration", found["uncovered"], "it only feeds the demand, which is named")
        out = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "basis.docx"
        write_design_basis(out, {"name": "Sample"}, record.snapshot("job1"), content_root=REPO)
        text = _docx_text(out)
        self.assertLess(text.index(checker.INCOMPLETE_HEAD), text.index("How far each statement was taken"))
        self.assertIn("Do not issue it or rely on it as a complete design basis.", text)
        self.assertNotIn(checker.COMPLETE_LINE, text)
        for name, _what, _where in checker.LADDER:
            self.assertIn(name, text)
        self.assertIn("NOT PERFORMED by this application, for any finding.", text)
        self.assertIn("NOT PERFORMED by this application. None is recorded on this job.", text)
        self.assertIn("12. Content the team worked from", text)
        self.assertIn(f"Content fingerprint: {record.context['content_fingerprint']}", text)

    def test_a_record_with_a_finding_for_every_calculation_is_covered_and_says_what_that_means(self):
        from fpfa import checker
        from fpfa.design_basis_docx import write_design_basis

        record, calcs, _di, _basis = _planned()
        for tool in ("dry_delivery_screen", "di_trip_to_water", "density_area", "nitrogen_gate", "elect_di_trim",
                     "releasing_truth_table"):
            record.record_finding("job1", agent="fp-sprinkler", label="use best judgment", supports=[calcs[tool]],
                                  text=f"A statement on {tool}.")
        found = checker.coverage(record.snapshot("job1"))
        self.assertEqual((found["complete"], found["gaps"], found["uncovered"]), (True, [], []),
                         "the volume and the hose table are spoken for through what was built on them")
        self.assertEqual(checker.coverage_lines(record.snapshot("job1")), [])
        out = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "basis.docx"
        checker.check_record(REPO, record, "job1", yes_to_everything)
        write_design_basis(out, {"name": "Sample"}, record.snapshot("job1"), content_root=REPO)
        text = _docx_text(out)
        self.assertIn(checker.COMPLETE_LINE, text)
        self.assertIn("That is a statement about the record, not about the design.", text)
        self.assertNotIn(checker.INCOMPLETE_HEAD, text)
        self.assertIn("NOT PERFORMED", text, "complete is never verified")

    def test_a_handoff_no_specialist_has_picked_up_is_a_gap(self):
        """Every calculation has a finding, and one specialist left work for the other that was never delivered."""
        from fpfa import checker
        from fpfa.design_basis_docx import write_design_basis

        record, calcs, _di, _basis = _planned()
        for tool in ("dry_delivery_screen", "di_trip_to_water", "density_area", "nitrogen_gate", "elect_di_trim",
                     "releasing_truth_table"):
            record.record_finding("job1", agent="fp-sprinkler", label="use best judgment", supports=[calcs[tool]],
                                  text=f"A statement on {tool}.")
        self.assertTrue(checker.coverage(record.snapshot("job1"))["complete"])
        # A note for the lead is read in its status block. It is not work waiting on a specialist.
        record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="lead", brief="The trim sheet is still owed.")
        self.assertTrue(checker.coverage(record.snapshot("job1"))["complete"])
        waiting = record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing",
                                        brief="Review the releasing sequence against the trim family.")
        found = checker.coverage(record.snapshot("job1"))
        self.assertFalse(found["complete"])
        self.assertEqual(found["gaps"], ["1 handoff is waiting for fa-releasing: work one contributor left for another "
                                         "has not been picked up."])
        out = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "basis.docx"
        write_design_basis(out, {"name": "Sample"}, record.snapshot("job1"), content_root=REPO)
        text = _docx_text(out)
        self.assertIn(checker.INCOMPLETE_HEAD, text)
        self.assertNotIn(checker.COMPLETE_LINE, text)
        # Once the receiver has it, nothing is waiting.
        record.set_handoff("job1", waiting["id"], status="delivered", by="lead")
        self.assertTrue(checker.coverage(record.snapshot("job1"))["complete"])
        self.assertIn("no handoff is waiting for a specialist", checker.COMPLETE_LINE)

    def test_the_lead_is_told_what_is_not_covered_and_the_role_says_what_to_do_about_it(self):
        from fpfa.team import lead_status

        record, calcs, _di, _basis = _planned()
        self.assertNotIn("Not yet covered", lead_status(record, "job1").split("Contributors so far")[0])
        record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                              supports=[calcs["zone_trapped_volume"]], text="The zone total is 281.3 gal.")
        block = lead_status(record, "job1")
        self.assertIn("Not yet covered. A design basis written now would be incomplete, and must say so:", block)
        self.assertIn("- No finding rests on the releasing logic (releasing_truth_table).", block)
        role = (REPO / "roles" / "lead" / "ROLE.md").read_text(encoding="utf-8")
        self.assertIn('lists, under "Not yet covered"', role)
        self.assertIn("Never call a design basis complete while that list has a line in it.", role)


class FailureAccountingTests(unittest.TestCase):
    """A failure does not un-spend what ran before it, and the record says what is not known."""

    def _failing(self, steps, error="the connection dropped"):
        steps = list(steps)

        def create(**_kwargs):
            if steps:
                return steps.pop(0)
            raise ConnectionError(error)

        return create

    def test_a_failed_delegation_keeps_the_usage_of_the_rounds_that_finished(self):
        from fpfa import team
        from fpfa.usage_report import usage_events

        record = _record()
        di, _basis = _seed_inputs(record)
        create = self._failing([call(use("zone_trapped_volume", segments=di["segments"]))])
        with self.assertRaises(ConnectionError) as caught:
            team.delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Find the trapped volume.")
        self.assertEqual(caught.exception.usage["rounds"], 1)
        self.assertEqual(caught.exception.usage["cache_read_input_tokens"], 9000)
        rows = usage_events(record, "job1")
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["kind"], rows[0]["failed"], rows[0]["usage"]["rounds"], rows[0]["stop_reason"]),
                         ("delegation", True, 1, "error"))
        self.assertIn("ConnectionError: the connection dropped", rows[0]["error"])
        handoff = record.handoffs("job1")[0]
        self.assertEqual((handoff["status"], handoff["result"]),
                         ("cancelled", "The specialist did not finish: ConnectionError: the connection dropped"))
        self.assertEqual(record.agents("job1")[0]["status"], "error")
        self.assertEqual([row["tool"] for row in record.calcs("job1")], ["zone_trapped_volume"], "what it computed is kept")

    def test_a_failed_turn_closes_on_the_record_with_what_it_and_its_team_had_used(self):
        from fpfa.everyday import run_everyday
        from fpfa.usage_report import failures, job_totals, report_text, usage_events

        record = _record()
        di, _basis = _seed_inputs(record)
        lead = [call(use("delegate", specialist="fp-sprinkler", brief="Find the trapped volume."))]
        specialist = [call(use("zone_trapped_volume", segments=di["segments"])), say("The volume is on the record.")]

        def create(**kwargs):
            script = lead if "# Team lead" in system_text(kwargs) else specialist
            if script:
                return script.pop(0)
            raise ConnectionError("the connection dropped")

        with self.assertRaises(ConnectionError):
            run_everyday(REPO, create, "What is the trapped volume?", record=record, project_id="job1")
        rows = usage_events(record, "job1")
        turn = next(row for row in rows if row["kind"] == "turn")
        self.assertTrue(turn["failed"])
        # One lead round and the delegation's two rounds had finished before the request that failed.
        self.assertEqual(turn["usage"]["rounds"], 3)
        self.assertEqual(job_totals(rows)["rounds"], 3)
        self.assertEqual(failures(rows), {"count": 1, "kinds": ["turn"]})
        self.assertEqual(record.agents("job1")[0]["status"], "error")
        text = report_text(record, "job1")
        self.assertIn("lead turn, 1 delegation, FAILED", text)
        self.assertIn("Failures: 1 model context ended on an error (marked FAILED above); the usage shown for each is what "
                      "had finished before the failure.", text)
        self.assertIn("Read the total as the usage the API reported: a floor, not a ceiling.", text)

    def test_a_failed_consult_is_counted_in_the_delegation_that_asked(self):
        from fpfa import team
        from fpfa.usage_report import usage_events

        record = _record()
        _seed_inputs(record)
        asker = [call(use("consult", specialist="fa-releasing", question="What releasing time does the sequence carry?")),
                 say("The releasing specialist did not answer. I carried the form's value as ASSUMED.")]
        answerer = [call(use("read_record"))]

        def create(**kwargs):
            script = answerer if "# Releasing specialist" in system_text(kwargs) else asker
            if script:
                return script.pop(0)
            raise ConnectionError("the connection dropped")

        out = team.delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen the zone.")
        self.assertTrue(out["complete"], "the asker went on with an error in place of an answer")
        rows = {row["kind"]: row for row in usage_events(record, "job1")}
        self.assertTrue(rows["consult"]["failed"])
        self.assertEqual(rows["consult"]["usage"]["rounds"], 1)
        # The asker's two rounds and the consult's one finished round.
        self.assertEqual(rows["delegation"]["usage"]["rounds"], 3)
        self.assertEqual(out["usage"]["rounds"], 3)

    def test_a_failed_trace_check_is_on_the_record_and_the_last_good_one_stands(self):
        from fpfa import checker
        from fpfa.usage_report import report_text, usage_events

        record, calcs, _di, _basis = _planned()
        record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                              supports=[calcs["zone_trapped_volume"]], text="The zone total is 281.3 gal.")
        good = checker.check_record(REPO, record, "job1", yes_to_everything)

        def broken(**_kwargs):
            raise TimeoutError("no answer in 300 s")

        with self.assertRaises(TimeoutError):
            checker.check_record(REPO, record, "job1", broken)
        self.assertEqual(checker.latest_check(record, "job1")["token"], good["token"])
        self.assertTrue(checker.check_is_current(record.snapshot("job1")))
        rows = [row for row in usage_events(record, "job1") if row["kind"] == "check_failed"]
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["failed"] and rows[0]["counted"])
        self.assertIn("trace check, FAILED", report_text(record, "job1"))

    def test_requests_sent_again_are_counted_and_said(self):
        from fpfa.usage_report import report_text, retries

        record, _calcs, _di, _basis = _planned()
        record.log_event("job1", "turn", {"usage": {"rounds": 2, "input_tokens": 10, "output_tokens": 5}}, agent="lead")
        self.assertEqual(retries(record, "job1"), 0)
        self.assertNotIn("Failures:", report_text(record, "job1"))
        record.log_event("job1", "api_retry", {"retries": 2}, agent="app")
        record.log_event("job1", "api_retry", {"retries": 1}, agent="app")
        self.assertEqual(retries(record, "job1"), 3)
        self.assertIn("Failures: 3 requests were sent again after a failed attempt. A request that fails returns no usage.",
                      report_text(record, "job1"))

    def test_the_client_counts_what_it_sent_again_and_usage_rides_on_the_failure(self):
        from fpfa.claude_client import attach_usage, run_tool_loop

        error = RuntimeError("boom")
        attach_usage(error, {"rounds": 1, "input_tokens": 5})
        attach_usage(error, {"rounds": 2, "input_tokens": 7, "flag": True})
        self.assertEqual(error.usage, {"rounds": 3, "input_tokens": 12})
        steps = [call(use("read_record"))]

        def create(**_kwargs):
            if steps:
                return steps.pop(0)
            raise RuntimeError("second round failed")

        with self.assertRaises(RuntimeError) as caught:
            run_tool_loop(create, system="s", user_text="u", tools=[], execute=lambda name, args: {})
        self.assertEqual(caught.exception.usage["rounds"], 1)
        from fpfa import claude_client

        source = (APP_DIR / "fpfa" / "claude_client.py").read_text(encoding="utf-8")
        self.assertIn("self.retries += 1", source)
        self.assertTrue(hasattr(claude_client, "attach_usage"))

    def test_the_block_under_a_reply_and_the_status_say_what_failed_and_what_a_retry_repeats(self):
        from fpfa import status, team
        from fpfa.team import team_summary

        text = team_summary({"failed": [{"what": "delegation", "who": "fa-releasing", "error": "ConnectionError: dropped"}]})
        self.assertIn("- FAILED: the delegation to fa-releasing ended on an error (ConnectionError: dropped).", text)
        self.assertIn("is kept and may be partial", text)
        self.assertIn("is billed again; recorded calculations replay.", text)
        record = _record()
        di, _basis = _seed_inputs(record)
        create = self._failing([call(use("zone_trapped_volume", segments=di["segments"]))])
        with self.assertRaises(ConnectionError):
            team.delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Find the trapped volume.")
        digest = status.build(record.snapshot("job1"))
        said = status.designer_text(digest)
        self.assertIn("**Interrupted or failed**", said)
        self.assertIn('- Sprinkler specialist stopped on an error before it finished ("Find the trapped volume."). '
                      "Kept from that task: 1 calculation. Treat them as partial", said)
        self.assertIn(status.RETRY_LINE, said)
        self.assertIn("billed again", status.RETRY_LINE)


class SkillUseTests(unittest.TestCase):
    """Who read which method, when, and whether a cite in its work is one the method holds."""

    def test_a_read_is_recorded_with_who_and_which_text_and_placed_against_the_findings(self):
        from fpfa import content_use
        from fpfa.calc_tools import ToolSession

        record = _record()
        _seed_inputs(record)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        fp.execute("read_skill", {"slug": "dry-preaction-water-delivery-screen"})
        fp.execute("read_skill", {"slug": "dry-preaction-water-delivery-screen"})
        cite = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                             "note": "At or under 500 gal a double-interlock zone carries no delivery-time proof."})
        fp.execute("record_finding", {"text": "The size exemption turns on the zone total.", "label": "use best judgment",
                                      "supports": [cite["id"]]})
        # The releasing specialist records first and reads afterwards.
        fa.execute("record_finding", {"text": "The sequence is detection and P.", "label": "use best judgment"})
        fa.execute("read_skill", {"slug": "fa-double-interlock-releasing-cause-and-effect"})
        # A third contributor reads nothing at all.
        ToolSession(REPO, record=record, project_id="job1", agent="spec-draft").execute(
            "record_finding", {"text": "Section 21 13 19 is the draft.", "label": "use best judgment"})
        rows = {row["agent"]: row for row in content_use.skill_use(record.snapshot("job1"), REPO)}
        self.assertEqual((rows["fp-sprinkler"]["reads"], rows["fp-sprinkler"]["before_findings"],
                          rows["fp-sprinkler"]["findings_after"]), (2, True, 1))
        self.assertEqual([item["section"] for item in rows["fp-sprinkler"]["carried"]], ["8.3.2.3.1.1"])
        self.assertEqual(len(rows["fp-sprinkler"]["sha256"]), 16)
        self.assertFalse(rows["fp-sprinkler"]["changed"])
        self.assertEqual((rows["fa-releasing"]["before_findings"], rows["fa-releasing"]["findings_after"],
                          rows["fa-releasing"]["carried"]), (False, 0, []))
        self.assertIn("AFTER it had already recorded findings", content_use.use_line(rows["fa-releasing"]))
        self.assertIn("Cites it then recorded that the skill holds: NFPA 13 2025 8.3.2.3.1.1", content_use.use_line(rows["fp-sprinkler"]))
        self.assertEqual(content_use.unread(record.snapshot("job1")), ["spec-draft"])

    def test_a_session_with_no_record_logs_nothing_and_a_changed_skill_is_noticed(self):
        from fpfa import content_use
        from fpfa.calc_tools import ToolSession

        self.assertIn("text", ToolSession(REPO, agent="lead").execute("read_skill", {"slug": "blind-claim-check"}))
        record = _record()
        _seed_inputs(record)
        ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler").execute("read_skill", {"slug": "blind-claim-check"})
        snapshot = record.snapshot("job1")
        snapshot["skill_reads"][0]["payload"]["sha256"] = "0000000000000000"
        self.assertTrue(content_use.skill_use(snapshot, REPO)[0]["changed"])
        self.assertEqual(content_use.skill_use({"skill_reads": []}, REPO), [])

    def test_the_team_panel_and_the_design_basis_show_what_was_read(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.team_panel import team_view

        record, calcs, _di, _basis = _planned()
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("read_skill", {"slug": "sprinkler-system-volume-takeoff"})
        session.execute("record_finding", {"text": "The zone total is 281.3 gal.", "label": "calculated",
                                           "supports": [calcs["zone_trapped_volume"]]})
        view = team_view(record.snapshot("job1"), content_root=REPO)
        self.assertEqual([(row["agent"], row["slug"]) for row in view["skills_used"]],
                         [("fp-sprinkler", "sprinkler-system-volume-takeoff")])
        self.assertIn("fp-sprinkler read sprinkler-system-volume-takeoff before its findings", view["skills_used"][0]["line"])
        self.assertEqual(view["content"]["content_fingerprint"], record.context["content_fingerprint"])
        self.assertFalse(view["coverage"]["complete"])
        self.assertEqual(len(view["ladder"]), 6)
        out = Path(tempfile.mkdtemp(prefix="fpfa-hardening-")) / "basis.docx"
        write_design_basis(out, {"name": "Sample"}, record.snapshot("job1"), content_root=REPO)
        text = _docx_text(out)
        self.assertIn("fp-sprinkler | sprinkler-system-volume-takeoff | before its findings", text)
        self.assertIn("A read shows the method was in front of the contributor. It does not show the method was followed", text)


class EvaluationEvidenceTests(unittest.TestCase):
    """What the runner counts as two specialists working together, and what it refuses to count."""

    def _two_specialists(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        di, _basis = _seed_inputs(record)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        return record, di, fp, fa

    def test_a_repeated_calculation_is_not_one_specialist_using_the_others_work(self):
        from fpfa.live_eval import collaboration

        record, _di, fp, fa = self._two_specialists()
        trim = fp.execute("elect_di_trim", {"system_type": "di", "prime_held_by": "nc_solenoid", "supervisory_psi": 15,
                                            "medium": "nitrogen", "insurer": "FM"})
        # The releasing specialist runs the very same call. The record replays the first row, under the first name.
        again = fa.execute("elect_di_trim", {"system_type": "di", "prime_held_by": "nc_solenoid", "supervisory_psi": 15,
                                             "medium": "nitrogen", "insurer": "FM"})
        self.assertEqual(again["record_id"], trim["record_id"])
        self.assertEqual(record.calcs("job1")[0]["agent"], "fp-sprinkler")
        fa.execute("record_finding", {"text": "The sequence is written for El/El.", "label": "calculated",
                                      "supports": [again["record_id"]]})
        replays = record.events_by_kind("job1", ("calc_replay",))
        found = collaboration(record.snapshot("job1"), replays)
        self.assertEqual(found["built_on"], [])
        self.assertEqual(len(found["replayed_only"]), 1)
        self.assertEqual((found["answered"], found["objections"], found["reasoned_agreements"], found["effects"]), ([], [], [], []))
        # Left out of the count, the same row would have passed for the other's work.
        self.assertEqual(len(collaboration(record.snapshot("job1"), [])["built_on"]), 1)

    def test_resting_on_the_others_finding_or_on_a_calculation_it_never_ran_does_count(self):
        from fpfa.live_eval import collaboration

        record, di, fp, fa = self._two_specialists()
        volume = fp.execute("zone_trapped_volume", {"segments": di["segments"]})
        finding = fp.execute("record_finding", {"text": "Trim family is El/El.", "label": "use best judgment"})
        fa.execute("record_finding", {"text": "The sequence follows the El/El trim.", "label": "use best judgment",
                                      "supports": [finding["id"]]})
        fa.execute("record_finding", {"text": "The zone is one releasing zone.", "label": "use best judgment",
                                      "supports": [volume["record_id"]]})
        found = collaboration(record.snapshot("job1"), record.events_by_kind("job1", ("calc_replay",)))
        self.assertEqual(len(found["built_on"]), 2)
        self.assertEqual(found["replayed_only"], [])

    def test_a_bare_agreement_and_an_unanswered_question_are_not_an_exchange(self):
        from fpfa.live_eval import collaboration

        record, _di, fp, fa = self._two_specialists()
        finding = fp.execute("record_finding", {"text": "Trim family is El/El.", "label": "use best judgment"})
        fa.execute("review_finding", {"id": finding["id"], "position": "agree"})
        asked = record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing", brief="What delay?", kind="consult")
        record.set_handoff("job1", asked["id"], status="returned", result="(The specialist returned no answer.)", by="fa-releasing")
        found = collaboration(record.snapshot("job1"), [])
        self.assertEqual((found["consults"], found["answered"], found["bare_agreements"], found["reasoned_agreements"]), (1, [], 1, []))
        self.assertEqual(found["effects"], [])
        # An objection with a reason, and the author's revision, are an exchange with an effect.
        review = fa.execute("review_finding", {"id": finding["id"], "position": "object",
                                               "note": "Nothing on the record says what holds the prime."})
        fp.execute("record_finding", {"text": "Trim family is El/El: a normally closed solenoid holds the prime.",
                                      "label": "use best judgment", "replaces": finding["id"]})
        found = collaboration(record.snapshot("job1"), [])
        self.assertEqual(found["objections"], [review["id"]])
        self.assertEqual(found["effects"], ["fa-releasing's objection: the author revised the finding"])

    def test_the_exemption_phrase_check_reads_a_claim_and_not_a_denial(self):
        from fpfa.live_eval import _CLAIMS_EXEMPTION, _DENIES_EXEMPTION

        def claims(sentence):
            return bool(_CLAIMS_EXEMPTION.search(sentence)) and not _DENIES_EXEMPTION.search(sentence)

        for wrong in ("At 475 gallons of pipe the zone is exempt from a delivery time.",
                      "The zone stays inside the 500 gal cap.",
                      "No specific delivery-time requirement applies.",
                      "Yes, it still gets the small-system break."):
            self.assertTrue(claims(wrong), wrong)
        for right in ("The zone total is 505.5 gal, so the zone is not exempt.",
                      "It is over the 500 gal cap once fittings and trim are counted.",
                      "The pipe alone is under the cap, but the zone total exceeds it.",
                      "It no longer gets the break."):
            self.assertFalse(claims(right), right)

    def test_the_runner_never_calls_its_cap_a_limit(self):
        from fpfa import live_eval

        self.assertIn("--max-usd is a guard, not a spending limit.", live_eval.__doc__)
        self.assertIn("so a run can pass", live_eval.__doc__)
        self.assertEqual(len(live_eval.OWNER_GATES), 3)
        self.assertTrue(any("OWNER TO CONFIRM" in gate for gate in live_eval.OWNER_GATES))
        self.assertTrue(any("qualified" in gate for gate in live_eval.OWNER_GATES))


class BlankInputHoldTests(unittest.TestCase):
    """A blank input stays blank and holds what needs it (FA Lead's ruling, 2026-11-12; app-content hand-back 5.2).

    A desk probe found the form sending a blank detection, releasing, or exhaust time as 0, a blank time basis
    and a blank insurer as FM, and a blank edition as 2025, and the tool plan doing the same again.
    """

    def _desk(self):
        import os

        from desk_loop import Loop

        _isolate_data()
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        loop = Loop()
        self.addCleanup(loop.destroy)
        return loop.open_desk()

    def test_the_form_sends_a_blank_as_blank(self):
        desk = self._desk()
        di, basis = desk.collect_di(), desk.collect_basis()
        for name in ("t_detect_s", "t_release_s", "t_exhaust_s", "delivery_basis", "system_type", "hazard",
                     "supervised", "qod", "manual_station", "failsafe_on_total_power_loss", "length_basis",
                     "q_fill_gpm", "density_gpm_ft2", "supervisory_psig", "fill_minutes"):
            self.assertIsNone(di[name], name)
        self.assertEqual((basis["nfpa_13"], basis["nfpa_72"], basis["insurer"]), ("", "", ""))
        # A typed 0 is a 0, and a yes or a no is that answer.
        desk.patch_form({"t_detect": "0", "qod": "no", "supervised": True})
        di = desk.collect_di()
        self.assertEqual((di["t_detect_s"], di["qod"], di["supervised"]), (0.0, False, True))
        # The form names no basis for a screen limit it has not got.
        self.assertIn("no time basis is chosen", desk.snapshot()["form"]["assumptions"])
        self.assertNotIn("FM", desk.snapshot()["form"]["assumptions"].split("Screen limit")[1].split("\n")[0])

    def test_a_run_holds_on_each_blank_and_names_it(self):
        import copy as _copy

        from fpfa.calc_tools import ToolSession
        from fpfa.sample_data import EXAMPLE_DI
        from fpfa.workflow import run_tool_plan, validate_di

        for name, label in (("t_detect_s", "Detection time is blank."), ("t_release_s", "Releasing time is blank."),
                            ("t_exhaust_s", "Exhaust time is blank."), ("delivery_basis", "Time basis is blank."),
                            ("hazard", "Hazard is blank."), ("supervised", "Supervised waterflow is blank."),
                            ("system_type", "System is blank."), ("length_basis", "Lengths is blank."),
                            ("manual_station", "Manual station is blank."), ("qod", "Quick-opening device is blank.")):
            di = _copy.deepcopy(EXAMPLE_DI)
            di[name] = None
            with self.assertRaises(ValueError, msg=name) as caught:
                validate_di(di)
            self.assertIn(label, str(caught.exception))
        di = _copy.deepcopy(EXAMPLE_DI)
        di.update(t_detect_s=None, delivery_basis="")
        with self.assertRaises(ValueError) as caught:
            run_tool_plan(ToolSession(REPO), di, {"insurer": "FM"})
        self.assertIn("Detection time is blank.", str(caught.exception))
        self.assertIn("Time basis is blank.", str(caught.exception))
        # A typed 0 runs as 0. The trim medium and the prime holder may be blank: the kernel says no election.
        di = _copy.deepcopy(EXAMPLE_DI)
        di.update(t_detect_s=0, medium=None, prime_held_by=None)
        tools, sent = run_tool_plan(ToolSession(REPO), di, {"insurer": "FM"})
        self.assertEqual(sent["di_trip_to_water"]["t_detect_s"], 0)
        self.assertIsNone(sent["elect_di_trim"]["medium"])

    def test_a_blank_insurer_stays_blank(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.sample_data import EXAMPLE_DI
        from fpfa.workflow import run_tool_plan

        tools, sent = run_tool_plan(ToolSession(REPO), dict(EXAMPLE_DI), {"insurer": ""})
        self.assertEqual((sent["releasing_truth_table"]["insurer"], sent["elect_di_trim"]["insurer"]), ("", ""))
        self.assertEqual(tools["releasing_truth_table"]["insurer"], "")
        self.assertFalse(tools["releasing_truth_table"]["fm_no_cross_zone"])
        # The model's own call: a blank insurer is not taken as FM either.
        truth = ToolSession(REPO).execute("releasing_truth_table", {"manual_station": True})
        self.assertEqual(truth["insurer"], "")

    def test_the_delivery_tools_refuse_a_time_or_a_basis_left_out(self):
        from fpfa.calc_tools import SCHEMAS, ToolSession

        session = ToolSession(REPO)
        full = {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM"}
        for left_out in ("t_detect_s", "t_release_s", "t_exhaust_s", "basis"):
            args = {key: value for key, value in full.items() if key != left_out}
            with self.assertRaises(ValueError, msg=left_out) as caught:
                session.execute("di_trip_to_water", args)
            self.assertIn(f"di_trip_to_water needs {left_out}.", str(caught.exception))
            with self.assertRaises(ValueError):
                session.execute("di_trip_to_water", dict(full, **{left_out: ""}))
        self.assertEqual(session.execute("di_trip_to_water", dict(full, t_exhaust_s=0))["t_total_s"],
                         session.execute("di_trip_to_water", full)["t_total_s"])
        for name in ("dry_delivery_screen", "di_trip_to_water"):
            required = next(item for item in SCHEMAS if item["name"] == name)["input_schema"]["required"]
            for key in ("t_detect_s", "t_release_s", "t_exhaust_s", "basis"):
                self.assertIn(key, required, (name, key))
        with self.assertRaises(ValueError):
            session.execute("hose_duration", {"hazard": "", "supervised": True})

    def test_a_new_job_states_no_edition_and_the_lead_is_told_it_holds(self):
        from fpfa import status
        from fpfa.projects import new_project

        project = new_project("Fresh")
        self.assertEqual((project["basis"]["nfpa_13"], project["basis"]["nfpa_72"], project["basis"]["insurer"]),
                         ("", "", ""))
        desk = self._desk()
        desk.patch_form({"zone_id": "Z-1"})
        desk.save_current()
        digest = status.build(desk.record.snapshot(desk.project["id"]))
        lead = status.lead_text(digest)
        self.assertIn("HOLD: NFPA 13 edition not pinned.", lead)
        self.assertIn("HOLD: NFPA 72 edition not pinned.", lead)
        self.assertIn("Edition not pinned", status.designer_text(digest))
        desk.patch_form({"nfpa_72": "2022"})
        desk.save_current()
        digest = status.build(desk.record.snapshot(desk.project["id"]))
        self.assertEqual([line.split(".")[0] for line in digest["unpinned"]], ["HOLD: NFPA 13 edition not pinned"])

    def test_no_starting_value_is_written_into_app_code_outside_the_hints(self):
        """The starting values live in one place, fpfa.inputs.HINTS, and only as hints."""
        import re

        from fpfa import inputs

        self.assertEqual(inputs.default_of("q_fill_gpm"), None)
        self.assertEqual(inputs.default_of("nfpa_13"), "")
        for name in ("t_detect_s", "t_release_s", "t_exhaust_s"):
            self.assertIsNone(inputs.hint_of(name))
        for path in ("desk.py", "workflow.py", "projects.py"):
            text = (APP_DIR / "fpfa" / path).read_text(encoding="utf-8")
            self.assertIsNone(re.search(r'or "(?:FM|2025)"|or 0,|get\("t_(?:detect|release|exhaust)_s"\) or', text), path)


class SecondJobTests(unittest.TestCase):
    """The second sample zone: other inputs, another answer, and its expected basis written down in advance."""

    def test_the_second_zone_differs_from_the_first_where_it_changes_an_answer(self):
        from fpfa.sample_data import EXAMPLE_DI, EXAMPLE_DI_2, SAMPLE_ZONES

        self.assertEqual(sorted(SAMPLE_ZONES), ["dh1", "dh2"])
        for name in ("zone_id", "q_fill_gpm", "t_detect_s", "t_release_s", "manual_station", "length_basis",
                     "fittings_percent", "trim_gal", "supervisory_psig", "segments"):
            self.assertNotEqual(EXAMPLE_DI[name], EXAMPLE_DI_2[name], name)
        self.assertEqual(EXAMPLE_DI["prime_held_by"], EXAMPLE_DI_2["prime_held_by"],
                         "the truth table models electric/electric only; the second job does not leave it")

    def test_its_known_answer_holds_the_figures_the_tool_plan_returns(self):
        from fpfa.sample_data import EXAMPLE_BASIS_2, EXAMPLE_DI_2
        from fpfa.workflow import exemption_answer, fmt1, run_di_zone

        tools = run_di_zone(REPO, copy.deepcopy(EXAMPLE_DI_2), EXAMPLE_BASIS_2)["tools"]
        volume, screen, trip = tools["zone_trapped_volume"], tools["dry_delivery_screen"], tools["di_trip_to_water"]
        truth, gas = tools["releasing_truth_table"], tools["nitrogen_gate"]
        self.assertEqual((fmt1(volume["pipe_gal"]), fmt1(volume["fittings_gal"]), fmt1(volume["trim_gal"]), fmt1(volume["zone_gal"])),
                         ("475.1", "23.8", "6.6", "505.5"))
        self.assertEqual((exemption_answer(screen), screen["pipe_only_nfpa_delivery_time_exempt"]), ("no", True))
        self.assertEqual((fmt1(trip["t_fill_s"]), fmt1(trip["t_total_s"]), fmt1(trip["margin_s"]), trip["passes_screen"]),
                         ("33.7", "46.7", "-16.7", False))
        self.assertEqual((truth["solenoid_true_count"], truth["row_count"], truth["manual_station"]), (4, 32, False))
        self.assertEqual((f"{gas['scfm_gauge_basis']:.2f}", f"{gas['scfm_abs_basis']:.2f}"), ("3.06", "5.32"))
        text = (REPO / "docs" / "known-answer-dh2.md").read_text(encoding="utf-8")
        for needle in ("475.1 gal", "23.8 gal", "6.6 gal", "505.5 gal", "33.7 s", "46.7 s", "−16.7 s", "4 true rows of 32",
                       "3.06 scfm", "5.32 scfm", "OWNER TO CONFIRM", "## 4. Wrong answers to look for", "## 5. Pass criteria"):
            self.assertIn(needle, text, needle)

    def test_the_slash_command_loads_it_into_a_job_of_its_own(self):
        from desk_loop import Loop

        from fpfa.desk import parse_slash_command, slash_help_text

        self.assertEqual(parse_slash_command("/sample-di2"), ("sample-di2", ""))
        self.assertEqual(parse_slash_command("/sample_di2"), ("sample-di2", ""))
        self.assertIn("/sample-di2", slash_help_text())
        _isolate_data()
        loop = Loop()
        try:
            desk = loop.open_desk()
            loop.update()
            desk.send_chat("/sample-di2")
            loop.update()
            self.assertEqual(desk.project["di"]["zone_id"], "DH-2")
            self.assertEqual(desk.project["name"], "Second sample DI zone (size-exemption boundary)")
            thread = desk.thread_text()
            self.assertIn("Sample loaded: data-hall double-interlock zone DH-2", thread)
            self.assertIn("NFPA size exemption on the zone total of 505.5 gal against the 500 gal cap: no.", thread)
            self.assertIn("6.6 gal trim (entered on the form, not assumed)", thread)
        finally:
            loop.destroy()


if __name__ == "__main__":
    unittest.main()
