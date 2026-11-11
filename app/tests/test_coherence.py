"""The record stays coherent when something changes.

Project inputs are record facts. A calc records which inputs it used and which earlier calcs it
took a figure from. When an input changes, every calc that used the old value, and every finding
and decision resting on one, is marked out of date with the reason, until it is run again,
replaced, or withdrawn. Nothing here calls a model.
"""

from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-coherence-")) / "fpfa.db")


def _seed_inputs(record, project_id="job1", di=None, basis=None):
    """The sample zone's inputs on the record, as the desk writes them."""
    from fpfa import inputs
    from fpfa.record import BASIS_LABELS
    from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI

    di = dict(di or EXAMPLE_DI)
    basis = dict(basis or EXAMPLE_BASIS)
    record.ensure_project(project_id, "Sample")
    record.sync_form(project_id, inputs.BASIS_KIND, {key: basis[key] for key, _ in BASIS_LABELS if basis.get(key)},
                     labels=dict(BASIS_LABELS))
    record.sync_form(project_id, inputs.INPUT_KIND, {name: inputs.encode(name, di.get(name)) for name in inputs.ZONE_FIELDS},
                     sources={name: "sample data" for name in inputs.ZONE_FIELDS})
    return di, basis


def _change(record, name, value, project_id="job1", agent="job form"):
    from fpfa import inputs

    kind = inputs.kind_of(name)
    text = inputs.encode(name, value) if kind == inputs.INPUT_KIND else str(value)
    return record.set_given(project_id, kind=kind, key=name, value=text, label="GIVEN" if kind == inputs.INPUT_KIND else "CODE",
                            source="zone form", agent=agent)


def _run_plan(record, di, basis, project_id="job1"):
    from fpfa.workflow import run_di_zone

    return run_di_zone(REPO, di, basis, record=record, project_id=project_id)


def _states(record, project_id="job1"):
    from fpfa.coherence import analyze

    analysis = analyze(record.snapshot(project_id))
    by_tool = {}
    for row in record.calcs(project_id):
        by_tool.setdefault(row["tool"], []).append(analysis["calcs"][row["id"]]["state"])
    return analysis, by_tool


class InputValueTests(unittest.TestCase):
    def test_values_are_checked_and_a_blank_stays_blank(self):
        from fpfa import inputs

        self.assertEqual(inputs.coerce("q_fill_gpm", "750"), 750.0)
        self.assertIsNone(inputs.coerce("trim_gal", ""))
        self.assertIsNone(inputs.coerce("trim_gal", None))
        self.assertIs(inputs.coerce("qod", "yes"), True)
        self.assertEqual(inputs.coerce("delivery_basis", "NFPA-OH"), "NFPA-OH")
        self.assertEqual(inputs.coerce("ahj", "  City fire marshal "), "City fire marshal")
        for name, bad in (("q_fill_gpm", "fast"), ("q_fill_gpm", -1), ("q_fill_gpm", float("inf")),
                          ("delivery_basis", "FMX"), ("qod", "maybe"), ("segments", "900 ft"),
                          ("nonsense", 1)):
            with self.assertRaises(inputs.InputError, msg=f"{name}={bad!r}"):
                inputs.coerce(name, bad)
        with self.assertRaises(inputs.InputError):
            inputs.coerce("segments", [{"nps": "1", "length_ft": 0}])
        with self.assertRaises(inputs.InputError):
            inputs.coerce("segments", [{"length_ft": 10}])
        self.assertEqual(inputs.encode("trim_gal", None), "null")
        self.assertEqual(inputs.decode(inputs.encode("q_fill_gpm", "600")), 600.0)

    def test_the_same_value_written_two_ways_is_one_value(self):
        from fpfa import inputs

        self.assertTrue(inputs.same("15", 15.0))
        self.assertTrue(inputs.same(None, ""))
        self.assertTrue(inputs.same("FM", "FM "))
        self.assertFalse(inputs.same(0, None))
        self.assertFalse(inputs.same(600, 750))
        self.assertFalse(inputs.same(True, False))
        # The diameter the form looks up is display. The same pipe is one stored value with or without it.
        plain = [{"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 900}]
        resolved = [{"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 900.0, "d_in": 1.049}]
        self.assertEqual(inputs.encode("segments", plain), inputs.encode("segments", resolved))
        longer = [{"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 950}]
        self.assertNotEqual(inputs.encode("segments", plain), inputs.encode("segments", longer))

    def test_the_form_defaults_match_the_inputs_module(self):
        """A blank form and fpfa.inputs must agree on the starting values, or 'not confirmed' would lie."""
        from fpfa import inputs

        os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-coherence-data-")
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        loop = Loop()
        self.addCleanup(loop.destroy)
        desk = loop.open_desk()
        di = desk.collect_di()
        self.assertEqual(set(di), set(inputs.ZONE_FIELDS))
        for name, value in di.items():
            self.assertTrue(inputs.same(inputs.canonical(name, value), inputs.canonical(name, inputs.default_of(name))),
                            f"{name}: form {value!r} vs default {inputs.default_of(name)!r}")
        for name, value in desk.collect_basis().items():
            self.assertEqual(value, inputs.default_of(name), name)

    def test_who_supplied_a_value(self):
        from fpfa import inputs

        project = {"di": {"q_fill_gpm": 600, "t_detect_s": 8}}
        self.assertEqual(inputs.provenance(project, "q_fill_gpm", 600), inputs.SOURCE_DEFAULT)
        self.assertEqual(inputs.provenance(project, "t_detect_s", 8), inputs.SOURCE_DESIGNER)
        inputs.note_given(project, ["q_fill_gpm"], inputs.SOURCE_CHAT)
        self.assertEqual(inputs.provenance(project, "q_fill_gpm", 600), inputs.SOURCE_CHAT)
        self.assertIn("not confirmed by the designer", inputs.source_text(inputs.SOURCE_DEFAULT))
        self.assertEqual(inputs.show("trim_gal", None), "blank")
        self.assertEqual(inputs.show("q_fill_gpm", 600.0), "600 gpm")
        self.assertEqual(inputs.show("qod", False), "no")


class FormSyncTests(unittest.TestCase):
    def test_first_sync_writes_given_facts_and_a_second_writes_nothing(self):
        from fpfa import inputs

        record = _record()
        _seed_inputs(record)
        rows = record.facts("job1", inputs.INPUT_KIND)
        self.assertEqual({row["key"] for row in rows}, set(inputs.ZONE_FIELDS))
        self.assertEqual({row["label"] for row in rows}, {"GIVEN"})
        self.assertEqual({row["agent"] for row in rows}, {"job form"})
        again = record.sync_form("job1", inputs.INPUT_KIND,
                                 {row["key"]: row["value"] for row in rows},
                                 sources={row["key"]: "sample data" for row in rows})
        self.assertEqual(again, {"written": [], "pulled": {}})
        givens = record.givens("job1")
        self.assertEqual(givens["insurer"]["value"], "FM")
        self.assertEqual(inputs.decode(givens["q_fill_gpm"]["value"]), 600.0)

    def test_a_changed_field_supersedes_and_logs_the_change(self):
        from fpfa import inputs

        record = _record()
        _seed_inputs(record)
        before = {row["key"]: row["value"] for row in record.facts("job1", inputs.INPUT_KIND)}
        now = dict(before, q_fill_gpm=inputs.encode("q_fill_gpm", 750))
        out = record.sync_form("job1", inputs.INPUT_KIND, now, sources={key: "sample data" for key in now},
                               shown_before=before)
        self.assertEqual([row["key"] for row in out["written"]], ["q_fill_gpm"])
        self.assertEqual(out["written"][0]["previous"], "600.0")
        history = [row for row in record.facts("job1", inputs.INPUT_KIND, include_superseded=True) if row["key"] == "q_fill_gpm"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["superseded_by"], history[1]["id"])
        event = record.latest_event("job1", "input_changed")
        self.assertEqual(event["payload"]["key"], "q_fill_gpm")
        self.assertEqual((event["payload"]["old"], event["payload"]["new"]), ("600.0", "750.0"))

    def test_an_input_the_lead_set_stands_until_the_designer_changes_the_field(self):
        from fpfa import inputs

        record = _record()
        _seed_inputs(record)
        shown = {row["key"]: row["value"] for row in record.facts("job1", inputs.INPUT_KIND)}
        sources = {key: "sample data" for key in shown}
        row = _change(record, "q_fill_gpm", 750, agent="lead")
        self.assertTrue(row["changed"])
        self.assertEqual(row["previous"], "600.0")
        # The form still shows 600 and the designer has not touched it: the record's value is put on the form.
        out = record.sync_form("job1", inputs.INPUT_KIND, shown, sources=sources, shown_before=shown)
        self.assertEqual(out["written"], [])
        self.assertEqual(out["pulled"], {"q_fill_gpm": "750.0"})
        self.assertEqual(inputs.decode(record.givens("job1")["q_fill_gpm"]["value"]), 750.0)
        # Once the form shows 750, a later sync is quiet and keeps who said it.
        shown_now = dict(shown, q_fill_gpm="750.0")
        out = record.sync_form("job1", inputs.INPUT_KIND, shown_now, sources=sources, shown_before=shown_now)
        self.assertEqual(out, {"written": [], "pulled": {}})
        self.assertEqual(record.givens("job1")["q_fill_gpm"]["agent"], "lead")
        # A form that was never synced before (an older job file) does not overrule the lead either.
        out = record.sync_form("job1", inputs.INPUT_KIND, shown, sources=sources, shown_before=None)
        self.assertEqual(out["pulled"], {"q_fill_gpm": "750.0"})
        # The designer then types 800: the form wins.
        typed = dict(shown_now, q_fill_gpm="800.0")
        out = record.sync_form("job1", inputs.INPUT_KIND, typed, sources=sources, shown_before=shown_now)
        self.assertEqual([item["key"] for item in out["written"]], ["q_fill_gpm"])
        self.assertEqual(record.givens("job1")["q_fill_gpm"]["agent"], "job form")
        # And typing the old value back is a change too, not a field left alone.
        back = dict(typed, q_fill_gpm="600.0")
        out = record.sync_form("job1", inputs.INPUT_KIND, back, sources=sources, shown_before=typed)
        self.assertEqual(inputs.decode(record.givens("job1")["q_fill_gpm"]["value"]), 600.0)

    def test_a_reconfirmed_value_is_a_new_row_and_not_a_change(self):
        from fpfa import inputs
        from fpfa.coherence import analyze

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        values = {row["key"]: row["value"] for row in record.facts("job1", inputs.INPUT_KIND)}
        out = record.sync_form("job1", inputs.INPUT_KIND, values, sources={key: "zone form" for key in values},
                               shown_before=values)
        self.assertEqual(len(out["written"]), len(values))
        self.assertIsNone(record.latest_event("job1", "input_changed"))
        analysis = analyze(record.snapshot("job1"))
        self.assertFalse(analysis["any_stale"])
        self.assertEqual({item["state"] for item in analysis["calcs"].values()}, {"current"})


class CallBasisTests(unittest.TestCase):
    def test_the_tool_plan_follows_the_inputs_and_chains_through_the_volume(self):
        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        calcs = {row["tool"]: row for row in record.calcs("job1")}
        givens = record.givens("job1")
        for tool, row in calcs.items():
            self.assertEqual(row["varies"], {}, tool)
            self.assertTrue(row["depends"], tool)
        self.assertIn(givens["q_fill_gpm"]["id"], calcs["di_trip_to_water"]["depends"])
        self.assertIn(givens["segments"]["id"], calcs["zone_trapped_volume"]["depends"])
        self.assertIn(givens["segments"]["id"], calcs["dry_delivery_screen"]["depends"])
        self.assertIn(givens["insurer"]["id"], calcs["elect_di_trim"]["depends"])
        # The trip time and the nitrogen fill took their gallons from the takeoff; the demand took its minutes from the hose table.
        self.assertIn(calcs["zone_trapped_volume"]["id"], calcs["di_trip_to_water"]["depends"])
        self.assertIn(calcs["zone_trapped_volume"]["id"], calcs["nitrogen_gate"]["depends"])
        self.assertIn(calcs["hose_duration"]["id"], calcs["density_area"]["depends"])

    def test_a_call_on_another_value_is_recorded_as_an_alternative_and_the_model_is_told(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        zone_gal = next(row["outputs"]["zone_gal"] for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        shown = session.execute("di_trip_to_water", {
            "v_gal": zone_gal, "q_fill_gpm": 750, "t_detect_s": 8, "t_release_s": 2, "basis": "FM",
        })
        self.assertIn("differs_from_project_inputs", shown)
        self.assertIn("q_fill_gpm 750 where the project input q_fill_gpm is 600", shown["differs_from_project_inputs"])
        self.assertIn("alternative, not the design case", shown["differs_from_project_inputs"])
        row = record.calc("job1", shown["record_id"])
        self.assertEqual(row["varies"]["q_fill_gpm"], {"used": 750, "project": 600.0, "input": "q_fill_gpm"})
        analysis, _ = _states(record)
        self.assertEqual(analysis["calcs"][row["id"]]["state"], "alternative")
        # The same call on the project's own values says nothing.
        same = session.execute("di_trip_to_water", {
            "v_gal": zone_gal, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
        })
        self.assertNotIn("differs_from_project_inputs", same)

    def test_an_argument_left_out_is_compared_on_what_the_tool_used(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        _seed_inputs(record)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        # The project says supervised waterflow. Leaving it out runs the tool's own default, unsupervised.
        shown = session.execute("hose_duration", {"hazard": "ordinary"})
        self.assertIn("supervised False where the project input supervised is True", shown["differs_from_project_inputs"])
        # The detection time is 8 s on the project. A call that leaves it out used 0.
        shown = session.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600})
        note = shown["differs_from_project_inputs"]
        self.assertIn("t_detect_s 0 where the project input t_detect_s is 8", note)
        self.assertIn("v_gal 281.3: no zone_trapped_volume result is on the record", note)

    def test_a_rounded_figure_still_chains_and_an_invented_one_does_not(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        volume = next(row for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        common = {"q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM"}
        rounded = session.execute("di_trip_to_water", dict(common, v_gal=281.3))
        self.assertNotIn("differs_from_project_inputs", rounded)
        self.assertIn(volume["id"], record.calc("job1", rounded["record_id"])["depends"])
        invented = session.execute("di_trip_to_water", dict(common, v_gal=200))
        self.assertIn("v_gal 200: matches no recorded zone_trapped_volume result", invented["differs_from_project_inputs"])

    def test_a_job_with_no_inputs_and_an_untracked_tool_record_no_basis(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        record.ensure_project("job1")
        session = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        shown = session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        self.assertNotIn("differs_from_project_inputs", shown)
        self.assertEqual(record.calcs("job1")[0]["depends"], [])
        _seed_inputs(record)
        session.execute("fp_calc", {"op": "pipe_volume", "inputs": {"segments": [{"d_in": 1.049, "length_ft": 10}]}})
        untracked = next(row for row in record.calcs("job1") if row["tool"] == "fp_calc")
        self.assertEqual((untracked["depends"], untracked["varies"]), ([], {}))

    def test_a_tool_session_without_a_record_is_unchanged(self):
        from fpfa.calc_tools import ToolSession

        bare = ToolSession(REPO).execute("hose_duration", {"hazard": "ordinary"})
        self.assertNotIn("record_id", bare)
        self.assertNotIn("differs_from_project_inputs", bare)


class StalenessTests(unittest.TestCase):
    def _seeded(self):
        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        return record, di, basis

    def test_a_changed_input_marks_exactly_the_calcs_that_used_it(self):
        record, di, basis = self._seeded()
        _change(record, "q_fill_gpm", 750)
        analysis, by_tool = _states(record)
        self.assertEqual(by_tool["dry_delivery_screen"], ["stale"])
        self.assertEqual(by_tool["di_trip_to_water"], ["stale"])
        for tool in ("zone_trapped_volume", "hose_duration", "density_area", "nitrogen_gate", "elect_di_trim",
                     "releasing_truth_table"):
            self.assertEqual(by_tool[tool], ["current"], tool)
        trip = next(row for row in record.calcs("job1") if row["tool"] == "di_trip_to_water")
        reason = analysis["calcs"][trip["id"]]["reasons"][0]
        self.assertIn("q_fill_gpm changed from 600 gpm to 750 gpm", reason)
        self.assertEqual([item["key"] for item in analysis["changes"]], ["q_fill_gpm"])
        self.assertEqual(analysis["changes"][0]["calcs"], 2)
        self.assertTrue(analysis["any_stale"])

    def test_a_changed_takeoff_reaches_the_calcs_that_took_its_gallons(self):
        record, di, basis = self._seeded()
        segments = copy.deepcopy(di["segments"])
        segments[0]["length_ft"] = 1200
        _change(record, "segments", segments)
        analysis, by_tool = _states(record)
        self.assertEqual(by_tool["zone_trapped_volume"], ["stale"])
        self.assertEqual(by_tool["dry_delivery_screen"], ["stale"])
        # These never took a segment argument. They are out of date because the volume they used is.
        self.assertEqual(by_tool["di_trip_to_water"], ["stale"])
        self.assertEqual(by_tool["nitrogen_gate"], ["stale"])
        self.assertEqual(by_tool["density_area"], ["current"])
        nitrogen = next(row for row in record.calcs("job1") if row["tool"] == "nitrogen_gate")
        self.assertIn("took a figure from zone_trapped_volume", analysis["calcs"][nitrogen["id"]]["reasons"][0])
        self.assertIn("segments changed", analysis["calcs"][nitrogen["id"]]["reasons"][0])

    def test_running_again_brings_the_record_current_and_keeps_the_old_rows_as_history(self):
        record, di, basis = self._seeded()
        _change(record, "q_fill_gpm", 750)
        before = len(record.calcs("job1"))
        _run_plan(record, dict(di, q_fill_gpm=750), basis)
        analysis, by_tool = _states(record)
        # Six tools replayed. The two that used the fill flow computed fresh; their old rows are the history.
        self.assertEqual(len(record.calcs("job1")), before + 2)
        self.assertEqual(sorted(by_tool["di_trip_to_water"]), ["current", "stale"])
        self.assertEqual(sorted(by_tool["dry_delivery_screen"]), ["current", "stale"])
        self.assertEqual(by_tool["zone_trapped_volume"], ["current"])
        replayed = next(row for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        self.assertEqual(replayed["replay_count"], 1)

    def test_setting_the_input_back_and_replaying_makes_the_old_calc_current_again(self):
        record, di, basis = self._seeded()
        _change(record, "q_fill_gpm", 750)
        _change(record, "q_fill_gpm", 600)
        analysis, by_tool = _states(record)
        # The value is what it was when the calcs ran. Nothing is out of date.
        self.assertFalse(analysis["any_stale"])
        _run_plan(record, di, basis)
        self.assertEqual(len(record.calcs("job1")), 8)

    def test_findings_and_decisions_follow_what_they_rest_on(self):
        from fpfa.coherence import analyze

        record, di, basis = self._seeded()
        calcs = {row["tool"]: row["id"] for row in record.calcs("job1")}
        givens = record.givens("job1")
        screen = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                       text="The FM 30 s screen misses at 38.1 s.", supports=[calcs["di_trip_to_water"]])
        demand = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                       text="Total demand is 640.0 gpm.", supports=[calcs["density_area"]])
        on_input = record.record_finding("job1", agent="fa-releasing", label="ASSUMED",
                                         text="The 8 s detection allowance is not tied to a detector type.",
                                         supports=[givens["t_detect_s"]["id"]])
        chained = record.record_finding("job1", agent="lead", label="use best judgment",
                                        text="Split the zone or raise the fill flow.", supports=[screen["id"]])
        decision = record.record_decision("job1", text="Keep one zone; verify by a listed calculation.",
                                          decided_by="lead", label="use best judgment",
                                          supports=[calcs["di_trip_to_water"]])
        legacy = record.record_decision("job1", text="Trim family El/El, provisional.", decided_by="fp-sprinkler",
                                        label="use best judgment", basis=calcs["elect_di_trim"])
        self.assertFalse(analyze(record.snapshot("job1"))["any_stale"])
        _change(record, "q_fill_gpm", 750)
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual(analysis["findings"][screen["id"]]["state"], "stale")
        self.assertIn("di_trip_to_water", analysis["findings"][screen["id"]]["reasons"][0])
        self.assertIn("q_fill_gpm changed from 600 gpm to 750 gpm", analysis["findings"][screen["id"]]["reasons"][0])
        self.assertEqual(analysis["findings"][demand["id"]]["state"], "current")
        self.assertEqual(analysis["findings"][on_input["id"]]["state"], "current")
        self.assertEqual(analysis["findings"][chained["id"]]["state"], "stale")
        self.assertEqual(analysis["decisions"][decision["id"]]["state"], "stale")
        self.assertEqual(analysis["decisions"][legacy["id"]]["state"], "current")
        self.assertEqual(set(analysis["stale"]["findings"]), {screen["id"], chained["id"]})
        # A finding that cites the input itself goes out of date when that input changes.
        _change(record, "t_detect_s", 20)
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual(analysis["findings"][on_input["id"]]["state"], "stale")
        self.assertIn("t_detect_s changed from 8 s to 20 s", analysis["findings"][on_input["id"]]["reasons"][0])
        # A decision whose basis names a calc id in prose follows that calc.
        _change(record, "prime_held_by", "pneumatic_actuator")
        self.assertEqual(analyze(record.snapshot("job1"))["decisions"][legacy["id"]]["state"], "stale")

    def test_replacing_a_finding_clears_it_and_what_rested_on_it_is_told(self):
        from fpfa.coherence import analyze
        from fpfa.record import RecordError

        record, di, basis = self._seeded()
        calcs = {row["tool"]: row["id"] for row in record.calcs("job1")}
        old = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                    text="The FM 30 s screen misses at 38.1 s.", supports=[calcs["di_trip_to_water"]])
        follow = record.record_finding("job1", agent="lead", label="use best judgment",
                                       text="Split the zone.", supports=[old["id"]])
        _change(record, "q_fill_gpm", 750)
        _run_plan(record, dict(di, q_fill_gpm=750), basis)
        fresh = next(row for row in record.calcs("job1") if row["tool"] == "di_trip_to_water" and row["inputs"]["q_fill_gpm"] == 750)
        with self.assertRaises(RecordError):
            record.record_finding("job1", agent="fa-releasing", label="calculated", text="x",
                                  supports=[fresh["id"]], replaces=old["id"])
        new = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                    text="The FM 30 s screen misses at 32.5 s.", supports=[fresh["id"]], replaces=old["id"])
        self.assertEqual(new["replaces"], old["id"])
        current = {row["id"] for row in record.findings("job1")}
        self.assertIn(new["id"], current)
        self.assertNotIn(old["id"], current)
        snap = record.snapshot("job1")
        self.assertEqual([row["id"] for row in snap["retired_findings"]], [old["id"]])
        self.assertEqual(snap["retired_findings"][0]["superseded_by"], new["id"])
        analysis = analyze(snap)
        self.assertEqual(analysis["findings"][new["id"]]["state"], "current")
        self.assertEqual(analysis["findings"][follow["id"]]["state"], "stale")
        self.assertIn(f"rests on finding [{old['id']}], which was replaced", analysis["findings"][follow["id"]]["reasons"][0])
        with self.assertRaises(RecordError):
            record.record_finding("job1", agent="fp-sprinkler", label="calculated", text="again", replaces=old["id"])
        gone = record.retire_finding("job1", follow["id"], by="lead", reason="The screen changed.")
        self.assertEqual(gone["superseded_by"], "withdrawn")
        self.assertEqual({row["id"] for row in record.findings("job1")}, {new["id"]})
        self.assertFalse(analyze(record.snapshot("job1"))["stale"]["findings"])

    def test_a_cite_follows_the_edition_on_the_basis_tab(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze

        record, di, basis = self._seeded()
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        nfpa13 = session.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                                      "note": "Double-interlock at or under 500 gal"})
        nfpa72 = session.execute("record_evidence", {"document": "NFPA 72", "edition": "2025", "section": "17.19.2.2.2"})
        other = session.execute("record_evidence", {"document": "NFPA 25", "edition": "2023", "section": "13.4"})
        finding = session.execute("record_finding", {"text": "No specific delivery time is required at this size.",
                                                      "label": "CODE", "supports": [nfpa13["id"]]})
        rows = {row["id"]: row for row in record.evidence("job1")}
        self.assertEqual(rows[nfpa13["id"]]["depends"], [record.givens("job1")["nfpa_13"]["id"]])
        self.assertEqual(rows[other["id"]]["depends"], [])
        _change(record, "nfpa_13", "2022")
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual(analysis["evidence"][nfpa13["id"]]["state"], "stale")
        self.assertIn("basis/nfpa_13 changed from 2025 to 2022", analysis["evidence"][nfpa13["id"]]["reasons"][0])
        self.assertIn("verify the section in that edition", analysis["evidence"][nfpa13["id"]]["reasons"][0])
        self.assertEqual(analysis["evidence"][nfpa72["id"]]["state"], "current")
        self.assertEqual(analysis["findings"][finding["id"]]["state"], "stale")

    def test_calcs_recorded_before_the_basis_was_kept_get_one_from_the_inputs(self):
        from fpfa.coherence import analyze, backfill

        record = _record()
        record.ensure_project("job1")
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI

        _run_plan(record, EXAMPLE_DI, EXAMPLE_BASIS)                     # no inputs on the record yet
        self.assertEqual({tuple(row["depends"]) for row in record.calcs("job1")}, {()})
        _seed_inputs(record)
        self.assertEqual(backfill(record, "job1"), 8)
        self.assertEqual(backfill(record, "job1"), 0)
        self.assertTrue(all(row["depends"] for row in record.calcs("job1")))
        _change(record, "q_fill_gpm", 750)
        self.assertEqual(len(analyze(record.snapshot("job1"))["stale"]["calcs"]), 2)

    def test_two_contributors_that_disagree_on_a_key_both_stay_and_the_lead_settles_it(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.record import RecordError

        record = _record()
        _seed_inputs(record)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        lead = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        first = fp.execute("record_fact", {"kind": "assumption", "key": "detection_leg", "value": "Fire 1", "label": "ASSUMED"})
        same = fa.execute("record_fact", {"kind": "assumption", "key": "detection_leg", "value": "Fire 1", "label": "ASSUMED"})
        self.assertEqual(same["id"], first["id"])
        self.assertIn("Already on the record", same["note"])
        other = fa.execute("record_fact", {"kind": "assumption", "key": "detection_leg", "value": "Action", "label": "OWNER"})
        self.assertEqual([item["by"] for item in other["conflicts_with"]], ["fp-sprinkler"])
        conflicts = analyze(record.snapshot("job1"))["conflicts"]
        self.assertEqual([(item["kind"], item["key"]) for item in conflicts], [("assumption", "detection_leg")])
        self.assertEqual({row["agent"] for row in conflicts[0]["rows"]}, {"fp-sprinkler", "fa-releasing"})
        # An agent that changes its own mind replaces its own row only.
        fp.execute("record_fact", {"kind": "assumption", "key": "detection_leg", "value": "Fire 2", "label": "ASSUMED"})
        self.assertEqual(len([row for row in record.facts("job1", "assumption")]), 2)
        settled = lead.execute("record_fact", {"kind": "assumption", "key": "detection_leg", "value": "Action",
                                                "label": "GIVEN", "source": "designer, in chat"})
        self.assertEqual([row["id"] for row in record.facts("job1", "assumption")], [settled["id"]])
        self.assertEqual(analyze(record.snapshot("job1"))["conflicts"], [])
        # Only the lead writes GIVEN, and nobody writes a project input with record_fact.
        with self.assertRaises(RecordError):
            fa.execute("record_fact", {"kind": "assumption", "key": "x", "value": "y", "label": "GIVEN"})
        for session in (fp, lead):
            with self.assertRaises(RecordError):
                session.execute("record_fact", {"kind": "input", "key": "q_fill_gpm", "value": "750", "label": "ASSUMED"})
            with self.assertRaises(RecordError):
                session.execute("record_fact", {"kind": "basis", "key": "nfpa_13", "value": "2022", "label": "CODE"})
        with self.assertRaises(RecordError):
            fp.execute("record_finding", {"text": "x", "label": "GIVEN"})


class DeskInputTests(unittest.TestCase):
    def _desk(self):
        os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-coherence-data-")
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        from fpfa.paths import write_config

        write_config({"key_backend": "file"})
        loop = Loop()
        self.addCleanup(loop.destroy)
        desk = loop.open_desk()
        loop.update()
        return desk

    def test_the_sample_job_puts_its_inputs_on_the_record_with_their_source(self):
        from fpfa import inputs
        from fpfa.coherence import analyze

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        rows = {row["key"]: row for row in desk.record.facts(project_id, inputs.INPUT_KIND)}
        self.assertEqual(set(rows), set(inputs.ZONE_FIELDS))
        self.assertEqual({row["source"] for row in rows.values()}, {"sample data"})
        self.assertEqual(inputs.decode(rows["q_fill_gpm"]["value"]), 600.0)
        analysis = analyze(desk.record.snapshot(project_id))
        self.assertEqual({item["state"] for item in analysis["calcs"].values()}, {"current"})
        self.assertTrue(all(item["tracked"] for item in analysis["calcs"].values()))

    def test_typing_a_field_marks_the_calcs_that_used_it_and_a_run_clears_them(self):
        from fpfa import inputs
        from fpfa.coherence import analyze

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        desk.patch_form({"q_fill": "750"})
        desk.save_current()
        row = desk.record.givens(project_id)["q_fill_gpm"]
        self.assertEqual(inputs.decode(row["value"]), 750.0)
        self.assertEqual(row["source"], "zone form")
        self.assertEqual(desk.project["given"]["q_fill_gpm"], inputs.SOURCE_DESIGNER)
        analysis = analyze(desk.record.snapshot(project_id))
        stale = {desk.record.calc(project_id, ident)["tool"] for ident in analysis["stale"]["calcs"]}
        self.assertEqual(stale, {"dry_delivery_screen", "di_trip_to_water"})
        desk.start_zone_run()
        desk.pump()
        analysis = analyze(desk.record.snapshot(project_id))
        current = [desk.record.calc(project_id, ident) for ident, item in analysis["calcs"].items() if item["state"] == "current"]
        self.assertEqual(len(current), 8)
        trip = next(row for row in current if row["tool"] == "di_trip_to_water")
        self.assertEqual(trip["inputs"]["q_fill_gpm"], 750.0)
        self.assertEqual(len(analysis["stale"]["calcs"]), 2)        # the two old rows, kept as history

    def test_a_fresh_job_says_its_starting_values_were_not_confirmed(self):
        from fpfa import inputs

        desk = self._desk()
        desk.patch_form({"t_detect": "12"})
        desk.save_current()
        project_id = desk.project["id"]
        rows = desk.record.givens(project_id)
        self.assertEqual(rows["t_detect_s"]["source"], "zone form")
        self.assertIn("not confirmed by the designer", rows["q_fill_gpm"]["source"])
        self.assertEqual(rows["q_fill_gpm"]["label"], "GIVEN")
        self.assertEqual(inputs.decode(rows["segments"]["value"]), [])

    def test_an_input_the_lead_recorded_is_put_on_the_form_and_survives_a_relaunch(self):
        from fpfa import inputs
        from fpfa.projects import load_project

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        _change(desk.record, "q_fill_gpm", 750, project_id=project_id, agent="lead")
        _change(desk.record, "nfpa_13", "2022", project_id=project_id, agent="lead")
        # A turn ended: the desk pulls what the lead recorded onto the form and the job file.
        pulled = desk._pull_inputs_onto_form(desk.project)
        self.assertEqual(set(pulled), {"q_fill_gpm", "nfpa_13"})
        self.assertEqual(desk.q_fill.get(), "750.0")
        self.assertEqual(desk.nfpa_13.get(), "2022")
        self.assertEqual(desk.collect_di()["q_fill_gpm"], 750.0)
        desk.save_current()
        saved = load_project(project_id)
        self.assertEqual(saved["di"]["q_fill_gpm"], 750.0)
        self.assertEqual(saved["given"]["q_fill_gpm"], inputs.SOURCE_CHAT)
        row = desk.record.givens(project_id)["q_fill_gpm"]
        self.assertEqual((row["agent"], inputs.decode(row["value"])), ("lead", 750.0))
        # The designer then types over it: the form wins and the record says who.
        desk.patch_form({"q_fill": "800"})
        desk.save_current()
        row = desk.record.givens(project_id)["q_fill_gpm"]
        self.assertEqual((row["agent"], inputs.decode(row["value"])), ("job form", 800.0))

    def test_a_lead_input_set_just_before_a_kill_is_not_lost_to_the_old_form_value(self):
        """The job file still holds 600 when the app dies. The next launch must not write 600 over the lead's 750."""
        from fpfa import inputs
        from fpfa.desk import Desk

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        desk.save_current()
        _change(desk.record, "q_fill_gpm", 750, project_id=project_id, agent="lead")
        desk.instance_lock.release()                     # the process is gone; nothing was pulled onto the form
        second = Desk()
        self.addCleanup(second.close)
        second.open_project(project_id)
        self.assertEqual(inputs.decode(second.record.givens(project_id)["q_fill_gpm"]["value"]), 750.0)
        self.assertEqual(second.record.givens(project_id)["q_fill_gpm"]["agent"], "lead")


if __name__ == "__main__":
    unittest.main()
