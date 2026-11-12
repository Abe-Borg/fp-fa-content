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
        self.assertEqual(again, {"written": [], "pulled": {}, "cleared": []})
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
        self.assertEqual(out, {"written": [], "pulled": {}, "cleared": []})
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

    def _basis_form(self, record, **fields):
        """A job whose Basis tab was synced once. Returns the labels and what the tab showed."""
        from fpfa import inputs
        from fpfa.record import BASIS_LABELS

        record.ensure_project("job1", "Sample")
        shown = {"ahj": "", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM", "hazard_notes": ""}
        shown.update(fields)
        record.sync_form("job1", inputs.BASIS_KIND, shown, labels=dict(BASIS_LABELS))
        return dict(BASIS_LABELS), shown

    def test_a_basis_field_the_lead_recorded_reaches_a_form_field_that_was_empty(self):
        from fpfa import inputs

        record = _record()
        labels, shown = self._basis_form(record)
        quiet = {"written": [], "pulled": {}, "cleared": []}
        # An empty field writes nothing: a fact has a value.
        self.assertEqual(set(record.givens("job1")), {"nfpa_13", "nfpa_72", "insurer"})
        self.assertEqual(record.sync_form("job1", inputs.BASIS_KIND, shown, labels=labels, shown_before=shown), quiet)
        # The designer states the AHJ in chat and the lead records it. The Basis tab still shows an empty field.
        record.set_given("job1", kind=inputs.BASIS_KIND, key="ahj", value="City fire marshal", label=labels["ahj"],
                         source="designer, in chat", agent="lead")
        out = record.sync_form("job1", inputs.BASIS_KIND, shown, labels=labels, shown_before=shown)
        self.assertEqual(out, {"written": [], "pulled": {"ahj": "City fire marshal"}, "cleared": []})
        # A job file last synced when an empty field was left out of the sync holds no note of the field.
        older = {key: value for key, value in shown.items() if value}
        out = record.sync_form("job1", inputs.BASIS_KIND, shown, labels=labels, shown_before=older)
        self.assertEqual(out["pulled"], {"ahj": "City fire marshal"})
        out = record.sync_form("job1", inputs.BASIS_KIND, shown, labels=labels, shown_before=None)
        self.assertEqual(out["pulled"], {"ahj": "City fire marshal"})
        # Once the tab shows it, a later sync is quiet and the row is still the lead's.
        shown_now = dict(shown, ahj="City fire marshal")
        self.assertEqual(record.sync_form("job1", inputs.BASIS_KIND, shown_now, labels=labels, shown_before=shown_now), quiet)
        row = record.givens("job1")["ahj"]
        self.assertEqual((row["agent"], row["source"]), ("lead", "designer, in chat"))

    def test_a_basis_field_the_designer_emptied_leaves_the_record_and_does_not_come_back(self):
        from fpfa import inputs

        record = _record()
        labels, shown = self._basis_form(record, ahj="City fire marshal")
        quiet = {"written": [], "pulled": {}, "cleared": []}
        held = record.givens("job1")["ahj"]
        emptied = dict(shown, ahj="")
        out = record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=shown)
        self.assertEqual(out, {"written": [], "pulled": {}, "cleared": ["ahj"]})
        self.assertNotIn("ahj", record.givens("job1"))
        history = [row for row in record.facts("job1", inputs.BASIS_KIND, include_superseded=True) if row["key"] == "ahj"]
        self.assertEqual([(row["id"], row["value"], row["superseded_by"]) for row in history],
                         [(held["id"], "City fire marshal", "withdrawn")])
        event = record.latest_event("job1", "input_changed")
        self.assertEqual((event["payload"]["key"], event["payload"]["old"], event["payload"]["new"]),
                         ("ahj", "City fire marshal", ""))
        # The field stays empty and nothing more happens.
        self.assertEqual(record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=emptied), quiet)
        # Emptying a value the lead recorded is the designer's change as well, and the value does not come back.
        record.set_given("job1", kind=inputs.BASIS_KIND, key="ahj", value="County fire district", label=labels["ahj"],
                         source="designer, in chat", agent="lead")
        with_lead = dict(shown, ahj="County fire district")
        out = record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=with_lead)
        self.assertEqual(out, {"written": [], "pulled": {}, "cleared": ["ahj"]})
        self.assertEqual(record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=emptied), quiet)
        self.assertNotIn("ahj", record.givens("job1"))
        # The lead records it once more after that. The field was empty and untouched, so it is put on the form.
        record.set_given("job1", kind=inputs.BASIS_KIND, key="ahj", value="City fire marshal", label=labels["ahj"],
                         source="designer, in chat", agent="lead")
        out = record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=emptied)
        self.assertEqual(out["pulled"], {"ahj": "City fire marshal"})
        # A zone input never arrives empty. Its blank is a value, written like any other.
        self.assertEqual(inputs.encode("trim_gal", None), "null")
        self.assertEqual(record.clear_given("job1", kind=inputs.BASIS_KIND, key="hazard_notes", agent="job form"), [])


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
            "v_gal": zone_gal, "q_fill_gpm": 750, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
            "system_type": "di",
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
            "system_type": "di",
        })
        self.assertNotIn("differs_from_project_inputs", same)

    def test_a_calc_that_took_a_figure_from_an_alternative_is_an_alternative_and_the_model_is_told(self):
        """A what-if takeoff, then a trip time on its gallons. The trip time is not the design case either."""
        from fpfa import status
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.team_panel import team_view

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        design = next(row for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        design_trip = next(row for row in record.calcs("job1") if row["tool"] == "di_trip_to_water")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        longer = copy.deepcopy(di["segments"])
        longer[1]["length_ft"] = 420                     # 200 ft more 2 in branch than the project inputs hold
        takeoff = session.execute("zone_trapped_volume", {"segments": longer})
        own = "segments 4 segments where the project input segments is 4 segments"
        self.assertIn(own, takeoff["differs_from_project_inputs"])
        self.assertGreater(takeoff["zone_gal"], design["outputs"]["zone_gal"])
        # The trip time uses the project's own fill flow and times. Only its gallons belong to another case.
        common = {"q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
                  "system_type": "di"}
        trip = session.execute("di_trip_to_water", dict(common, v_gal=takeoff["zone_gal"]))
        carried = f"a figure from zone_trapped_volume [{takeoff['record_id']}], which ran on {own}"
        self.assertEqual(
            trip["differs_from_project_inputs"],
            f"This call used {carried}. It is recorded as an alternative, not the design case. "
            "If the project input is wrong, the lead changes it; do not present this result as the design case.",
        )
        row = record.calc("job1", trip["record_id"])
        self.assertEqual(row["varies"], {})
        self.assertIn(takeoff["record_id"], row["depends"])
        nitrogen = session.execute("nitrogen_gate", {"v_gal": takeoff["zone_gal"], "p_psig": 40, "t_min": 30})
        self.assertIn(carried, nitrogen["differs_from_project_inputs"])
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                        text="With 200 ft more branch the trip time is longer.",
                                        supports=[trip["record_id"]])
        snapshot = record.snapshot("job1")
        analysis = analyze(snapshot)
        self.assertEqual(analysis["calcs"][takeoff["record_id"]]["state"], "alternative")
        # The job states NFPA 13 2025, which is the edition this calculation's cites carry: no edition gap.
        self.assertEqual(analysis["calcs"][trip["record_id"]],
                         {"state": "alternative", "reasons": [], "note": carried, "tracked": True, "unchecked": "",
                          "edition_gaps": [], "edition_hold": ""})
        self.assertEqual(analysis["calcs"][nitrogen["record_id"]]["state"], "alternative")
        # The finding on the derived trip time is named as resting on another case, to the lead and on the panel.
        self.assertEqual(analysis["findings"][finding["id"]]["state"], "current")
        self.assertEqual(analysis["findings"][finding["id"]]["notes"],
                         [f"di_trip_to_water [{trip['record_id']}] ran on {carried}"])
        self.assertEqual([item["finding_id"] for item in status.build(snapshot)["alternatives"]], [finding["id"]])
        self.assertIn(f"[{finding['id']}] by fp-sprinkler", status.lead_text(status.build(snapshot)))
        self.assertEqual([item["id"] for item in team_view(snapshot)["alternatives"]], [finding["id"]])
        # The design case is untouched, and the same call on its gallons says nothing.
        self.assertEqual(analysis["calcs"][design_trip["id"]]["state"], "current")
        self.assertFalse(analysis["any_stale"])
        again = session.execute("di_trip_to_water", dict(common, v_gal=design["outputs"]["zone_gal"]))
        self.assertNotIn("differs_from_project_inputs", again)

    def test_a_figure_two_takeoffs_share_is_tied_to_the_one_on_the_project_inputs(self):
        """An alternative takeoff can land on the design gallons. The design trip time must not inherit its case."""
        from fpfa.calc_tools import ToolSession

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        design = next(row for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        # The same pipe with a zero fittings allowance, where the project leaves the allowance blank.
        twin = session.execute("zone_trapped_volume", {"segments": di["segments"], "fittings_percent": 0})
        self.assertIn("fittings_percent 0 where the project input fittings_percent is blank",
                      twin["differs_from_project_inputs"])
        self.assertEqual(twin["zone_gal"], design["outputs"]["zone_gal"])
        # The job's own edition, as the tool plan passes it, so the call is the plan's own (PR-C).
        common = {"q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
                  "system_type": "di", "edition": "2025"}
        trip = session.execute("di_trip_to_water", dict(common, v_gal=design["outputs"]["zone_gal"]))
        self.assertNotIn("differs_from_project_inputs", trip)
        row = record.calc("job1", trip["record_id"])
        self.assertIn(design["id"], row["depends"])
        self.assertNotIn(twin["record_id"], row["depends"])
        # The tool plan run again replays its own calls. Every one of them still follows the project inputs.
        _run_plan(record, di, basis)
        analysis, by_tool = _states(record)
        self.assertEqual(by_tool["di_trip_to_water"], ["current"])
        self.assertEqual(by_tool["nitrogen_gate"], ["current"])
        self.assertEqual(sorted(by_tool["zone_trapped_volume"]), ["alternative", "current"])
        # With only the alternative left standing on that figure, a call on it is tied to the alternative.
        from fpfa.coherence import call_basis

        givens = record.givens("job1")
        calcs = record.calcs("job1")
        depends, varies = call_basis("di_trip_to_water", dict(common, v_gal=design["outputs"]["zone_gal"]), givens, calcs,
                                     stale={design["id"]}, alternative={twin["record_id"]})
        self.assertIn(twin["record_id"], depends)
        self.assertEqual(varies, {})

    def test_an_argument_left_out_is_compared_on_what_the_tool_used(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        _seed_inputs(record)
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        # The project says supervised waterflow. Leaving it out runs the tool's own default, unsupervised.
        shown = session.execute("hose_duration", {"hazard": "ordinary"})
        self.assertIn("supervised False where the project input supervised is True", shown["differs_from_project_inputs"])
        # The detection time is 8 s on the project. A call that leaves the basis or the system type out is refused,
        # naming them: no FM and no "di" is put in their place. A time left out is not taken as 0 either: the row is
        # then the fill time alone (test_pr_c).
        with self.assertRaises(ValueError) as caught:
            session.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600})
        self.assertIn("di_trip_to_water needs basis, system_type.", str(caught.exception))
        shown = session.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 0,
                                                     "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
                                                     "system_type": "di"})
        note = shown["differs_from_project_inputs"]
        self.assertIn("t_detect_s 0 where the project input t_detect_s is 8", note)
        self.assertIn("v_gal 281.3: no zone_trapped_volume result is on the record", note)

    def test_a_blank_project_input_is_never_read_as_a_default(self):
        """A job whose time basis is blank: a call on FM does not follow it, and a call that names none cannot run."""
        from fpfa import inputs
        from fpfa.calc_tools import ToolSession

        record = _record()
        record.ensure_project("job1", "Blank basis")
        record.sync_form("job1", inputs.INPUT_KIND, {"delivery_basis": inputs.encode("delivery_basis", None),
                                                     "t_detect_s": inputs.encode("t_detect_s", 8)})
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        shown = session.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8,
                                                     "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
                                                     "system_type": "di"})
        self.assertIn("basis FM where the project input delivery_basis is", shown["differs_from_project_inputs"])
        row = record.calc("job1", shown["record_id"])
        self.assertEqual(row["varies"]["basis"]["project"], None)
        # A tool's own default for an argument left out is not the project's blank either: hose_duration runs
        # unsupervised when supervised is left out, and that is a departure, not the designer's choice.
        record.sync_form("job1", inputs.INPUT_KIND, {"supervised": inputs.encode("supervised", None),
                                                     "medium": inputs.encode("medium", None)})
        hose = session.execute("hose_duration", {"hazard": "ordinary"})
        self.assertIn("supervised False where the project input supervised is", hose["differs_from_project_inputs"])
        self.assertEqual(record.calc("job1", hose["record_id"])["varies"]["supervised"]["used"], False)
        # The kernel's own word for no election is a blank: a trim election with no medium follows a blank medium.
        trim = session.execute("elect_di_trim", {"system_type": "di"})
        self.assertNotIn("medium", record.calc("job1", trim["record_id"]).get("varies") or {})

    def test_a_rounded_figure_still_chains_and_an_invented_one_does_not(self):
        from fpfa.calc_tools import ToolSession

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        volume = next(row for row in record.calcs("job1") if row["tool"] == "zone_trapped_volume")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        common = {"q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
                  "system_type": "di"}
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

    def test_what_rests_on_an_input_the_designer_emptied_is_out_of_date_until_it_is_stated_again(self):
        from fpfa import inputs
        from fpfa import status
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.record import BASIS_LABELS

        record, di, basis = self._seeded()
        labels = dict(BASIS_LABELS)
        shown = {key: basis[key] for key, _ in BASIS_LABELS}
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        cite = session.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1"})
        on_ahj = record.record_finding("job1", agent="fp-sprinkler", label="use best judgment",
                                       text="The submittal goes to the fire marshal named on the Basis tab.",
                                       supports=[record.givens("job1")["ahj"]["id"]])
        on_cite = record.record_finding("job1", agent="fp-sprinkler", label="CODE",
                                        text="No specific delivery time is required at this size.", supports=[cite["id"]])
        emptied = dict(shown, ahj="", nfpa_13="")
        out = record.sync_form("job1", inputs.BASIS_KIND, emptied, labels=labels, shown_before=shown)
        self.assertEqual(out["cleared"], ["ahj", "nfpa_13"])
        snapshot = record.snapshot("job1")
        analysis = analyze(snapshot)
        self.assertEqual(analysis["findings"][on_ahj["id"]],
                         {"state": "stale", "notes": [], "unchecked": [],
                          "reasons": [f"basis/ahj was emptied on the form; it was {basis['ahj']}"]})
        self.assertEqual(analysis["evidence"][cite["id"]]["reasons"],
                         ["basis/nfpa_13 was emptied on the form; it was 2025; the job states no edition for this cite now"])
        self.assertEqual(analysis["findings"][on_cite["id"]]["state"], "stale")
        # The calcs follow the zone inputs, and none of those moved. The delivery rows follow the job's NFPA 13
        # edition too (PR-C), so emptying it puts them, and only them, out of date.
        calcs = {row["id"]: row["tool"] for row in record.calcs("job1")}
        self.assertEqual({calcs[ident] for ident in analysis["stale"]["calcs"]}, {"dry_delivery_screen", "di_trip_to_water"})
        # The status names both changes while something current still rests on the old values.
        digest = status.build(snapshot)
        self.assertEqual({item["key"] for item in digest["changes"]}, {"ahj", "nfpa_13"})
        self.assertNotIn("ahj", {row["name"] for row in digest["inputs"]})
        # Typed back as they were: both rest on values the job states again.
        out = record.sync_form("job1", inputs.BASIS_KIND, shown, labels=labels, shown_before=emptied)
        self.assertEqual({row["key"] for row in out["written"]}, {"ahj", "nfpa_13"})
        analysis = analyze(record.snapshot("job1"))
        self.assertFalse(analysis["any_stale"])
        # Emptied and then stated as something else: it changed, from what the finding used to what the job says now.
        record.sync_form("job1", inputs.BASIS_KIND, dict(shown, ahj=""), labels=labels, shown_before=shown)
        record.sync_form("job1", inputs.BASIS_KIND, dict(shown, ahj="County fire district"), labels=labels,
                         shown_before=dict(shown, ahj=""))
        analysis = analyze(record.snapshot("job1"))
        reason = analysis["findings"][on_ahj["id"]]["reasons"][0]
        self.assertTrue(reason.startswith(f"basis/ahj changed from {basis['ahj']} to County fire district"), reason)
        self.assertEqual(analysis["findings"][on_cite["id"]]["state"], "current")

    def test_a_decision_is_replaced_withdrawn_or_closes_with_the_finding_it_ruled_on(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.coherence import analyze
        from fpfa.record import RecordError

        record, di, basis = self._seeded()
        calcs = {row["tool"]: row["id"] for row in record.calcs("job1")}
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        lead = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        first = fp.execute("record_decision", {"text": "Keep one zone; verify by a listed calculation.",
                                               "label": "use best judgment", "supports": [calcs["di_trip_to_water"]]})
        _change(record, "q_fill_gpm", 750)
        self.assertEqual(analyze(record.snapshot("job1"))["decisions"][first["id"]]["state"], "stale")
        # Only the author or the lead replaces it. The old row is kept as history.
        with self.assertRaises(RecordError):
            fa.execute("record_decision", {"text": "x", "label": "use best judgment", "replaces": first["id"]})
        _run_plan(record, dict(di, q_fill_gpm=750), basis)
        fresh = next(row["id"] for row in record.calcs("job1")
                     if row["tool"] == "di_trip_to_water" and row["inputs"]["q_fill_gpm"] == 750)
        second = fp.execute("record_decision", {"text": "Keep one zone at the higher fill flow.", "label": "use best judgment",
                                                "supports": [fresh], "replaces": first["id"]})
        self.assertEqual(second["replaces"], first["id"])
        self.assertEqual([row["id"] for row in record.decisions("job1")], [second["id"]])
        snap = record.snapshot("job1")
        self.assertEqual([(row["id"], row["superseded_by"]) for row in snap["retired_decisions"]], [(first["id"], second["id"])])
        self.assertFalse(analyze(snap)["stale"]["decisions"])
        with self.assertRaises(RecordError):
            fp.execute("record_decision", {"text": "again", "label": "use best judgment", "replaces": first["id"]})
        # withdraw_finding takes a decision's id too. A specialist withdraws its own; the lead withdraws any.
        with self.assertRaises(RecordError):
            fa.execute("withdraw_finding", {"id": second["id"], "reason": "not mine"})
        gone = lead.execute("withdraw_finding", {"id": second["id"], "reason": "The designer split the zone."})
        self.assertEqual((gone["withdrawn"], gone["kind"]), (True, "decision"))
        self.assertEqual(record.decisions("job1"), [])
        self.assertEqual(len(record.decisions("job1", include_retired=True)), 2)

        # A ruling on an objection is over when the finding it ruled on is revised. Another decision that
        # rests on the same finding is not: it is out of date until its author deals with it.
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated", text="The screen misses.", supports=[fresh])
        review = record.put_review("job1", finding_id=finding["id"], agent="fa-releasing", position="object", note="Clock start.")
        ruling = record.record_decision("job1", text="The objection is not upheld. The finding stands.", decided_by="lead",
                                        label="use best judgment", supports=[finding["id"]], review_id=review["id"])
        plain = record.record_decision("job1", text="Carry the miss to the owner.", decided_by="lead",
                                       label="use best judgment", supports=[finding["id"]])
        record.record_finding("job1", agent="fp-sprinkler", label="calculated", text="The screen misses by 2.5 s.",
                                  supports=[fresh], replaces=finding["id"])
        current = [row["id"] for row in record.decisions("job1")]
        self.assertEqual(current, [plain["id"]])
        closed = next(row for row in record.decisions("job1", include_retired=True) if row["id"] == ruling["id"])
        self.assertEqual(closed["superseded_by"], "withdrawn")
        self.assertIn("The finding it ruled on was revised", closed["retire_note"])
        analysis = analyze(record.snapshot("job1"))
        self.assertEqual(analysis["decisions"][plain["id"]]["state"], "stale")
        self.assertNotIn(ruling["id"], analysis["decisions"])

    def test_only_what_something_current_rests_on_is_waiting_on_anyone(self):
        """An out-of-date row nothing current rests on is history. It must not hold a job up for ever."""
        from fpfa import status
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import export_gate

        record, di, basis = self._seeded()
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        # A specialist's exploratory calc with no finding on it, a calc with one, and a cite with and without one.
        # The exploratory one is a what-if on the fill time. With the plan's own fill time it would be the
        # plan's row: the rounded volume is run as the takeoff's figure, so the call replays.
        loose = fp.execute("nitrogen_gate", {"v_gal": 281.3, "p_psig": 40, "t_min": 20})
        self.assertNotIn(loose["record_id"], {row["id"] for row in record.calcs("job1") if row["agent"] == "tool-plan"})
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        used = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1"})
        unused = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.2"})
        finding = fp.execute("record_finding", {"text": "The FM screen misses.", "label": "calculated", "supports": [screen["record_id"]]})
        cited = fp.execute("record_finding", {"text": "No delivery time at this size.", "label": "CODE", "supports": [used["id"]]})
        self.assertEqual(status.build(record.snapshot("job1"))["stale"], [])
        _change(record, "q_fill_gpm", 750)
        _change(record, "supervisory_psig", 30)
        _change(record, "nfpa_13", "2022")
        digest = status.build(record.snapshot("job1"))
        waiting = {(row["kind"], row["id"]) for row in digest["stale"]}
        self.assertIn(("finding", finding["id"]), waiting)
        self.assertIn(("calc", screen["record_id"]), waiting, "a current finding rests on it")
        self.assertIn(("finding", cited["id"]), waiting)
        self.assertIn(("cite", used["id"]), waiting)
        self.assertNotIn(("calc", loose["record_id"]), waiting, "nothing rests on the specialist's loose calc")
        self.assertNotIn(("cite", unused["id"]), waiting, "nothing rests on the unused cite")
        plan_rows = {row["id"] for row in record.calcs("job1") if row["agent"] == "tool-plan"}
        self.assertTrue(plan_rows & {ident for kind, ident in waiting if kind == "calc"},
                        "the tool plan's own rows feed the tables, so they wait for a re-run")
        self.assertEqual({item["key"] for item in digest["changes"]}, {"q_fill_gpm", "supervisory_psig", "nfpa_13"})
        self.assertIn("out of date", export_gate(record, "job1"))
        # It is still marked where a model reads the record, so it is not cited by mistake.
        self.assertIn(f"- [{loose['record_id']}] nitrogen_gate:", status.record_text(record.snapshot("job1")).split(
            "Out-of-date calculation records")[1])

        # Bring it up to date: run the zone again, replace the two findings on fresh rows.
        _run_plan(record, dict(di, q_fill_gpm=750, supervisory_psig=30), dict(basis, nfpa_13="2022"))
        again = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 750, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        fp.execute("record_finding", {"text": "The FM screen still misses.", "label": "calculated",
                                      "supports": [again["record_id"]], "replaces": finding["id"]})
        newer = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2022", "section": "8.3.2.3.1.1"})
        fp.execute("record_finding", {"text": "No delivery time at this size.", "label": "CODE",
                                      "supports": [newer["id"]], "replaces": cited["id"]})
        digest = status.build(record.snapshot("job1"))
        self.assertEqual(digest["stale"], [])
        self.assertEqual(digest["changes"], [], "a change is not news once nothing waits on it")
        self.assertNotIn("out of date", export_gate(record, "job1"))
        self.assertNotIn("Inputs changed after work was done on them", status.lead_text(digest))

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
        self.assertEqual({row["source"] for row in rows.values()}, {"SAMPLE data"})
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

    def test_a_fresh_job_holds_blanks_and_an_accepted_hint_is_assumed(self):
        """FA Lead's ruling (2026-11-12): a hint is never an input until the designer accepts it, and then ASSUMED."""
        from fpfa import inputs, status

        desk = self._desk()
        state = desk.snapshot()["form"]
        # Every field starts blank. A hint shows a value the pack pins, with its cite and edition, to VERIFY.
        self.assertTrue(all(value in ("", None) for value in state["values"].values()), state["values"])
        self.assertEqual(state["hints"]["density"],
                         "0.20 gpm/ft² (ordinary hazard group 2; NFPA 13-2025 Table 19.2.3.1.1) VERIFY")
        for name in ("q_fill", "supervisory_psig", "supervisory_psi", "t_detect", "t_release", "t_exhaust",
                     "insurer", "hazard", "supervised", "system_label"):
            self.assertNotIn(name, state["hints"], name)
        desk.patch_form({"t_detect": "12"})
        desk.save_current()
        project_id = desk.project["id"]
        rows = desk.record.givens(project_id)
        self.assertEqual(rows["t_detect_s"]["source"], "zone form")
        self.assertEqual((rows["t_detect_s"]["label"], inputs.decode(rows["t_detect_s"]["value"])), ("GIVEN", 12.0))
        # A blank stays blank on the record. Nothing nobody entered is an input.
        for name in ("q_fill_gpm", "t_release_s", "delivery_basis", "supervised", "hazard", "density_gpm_ft2"):
            self.assertIsNone(inputs.decode(rows[name]["value"]), name)
        for name in ("nfpa_13", "nfpa_72", "insurer"):
            self.assertNotIn(name, rows)
        self.assertEqual(inputs.decode(rows["segments"]["value"]), [])
        # Use hints fills a field with one hint. Base area has two (NFPA 13's and FM's), and the fill flow none.
        filled = desk.accept_hints(["density", "base_area", "q_fill", "t_release", "hose"])
        self.assertEqual(filled, ["density", "hose"])
        self.assertEqual(desk.snapshot()["form"]["assumed"], ["density", "hose"])
        self.assertNotIn("base_area", desk.snapshot()["form"]["accept"])
        desk.save_current()
        rows = desk.record.givens(project_id)
        self.assertEqual((rows["hose_gpm"]["label"], inputs.decode(rows["hose_gpm"]["value"])), ("ASSUMED", 250.0))
        self.assertIn(inputs.ACCEPTED_MARK, rows["hose_gpm"]["source"])
        self.assertEqual(rows["density_gpm_ft2"]["label"], "ASSUMED")
        self.assertEqual(rows["t_detect_s"]["label"], "GIVEN")
        # Each ASSUMED input has its own line, with the cite of the hint it came from, in every status view.
        snapshot = desk.record.snapshot(project_id)
        digest = status.build(snapshot)
        line = next(line for line in digest["assumed"] if line.startswith("hose_gpm ASSUMED:"))
        self.assertIn("NFPA 13-2025 Table 19.2.3.1.2, VERIFY", line)
        self.assertIn("until the designer types a value", line)
        self.assertIn("- density_gpm_ft2 ASSUMED: 0.2 gpm/ft2 is a hint the designer used", status.lead_text(digest))
        self.assertIn("**ASSUMED inputs**", status.designer_text(digest))
        from fpfa.checker import coverage

        self.assertTrue(any(gap.startswith("hose_gpm ASSUMED:") for gap in coverage(snapshot)["gaps"]))
        # Typing a value, even the hint's own, makes it the designer's: GIVEN, and its ASSUMED line goes. The source
        # says it was typed from the form's hint (PR-C).
        desk.patch_form({"hose": "250"})
        desk.save_current()
        rows = desk.record.givens(project_id)
        self.assertEqual((rows["hose_gpm"]["label"], rows["hose_gpm"]["source"]), ("GIVEN", "typed from form hint"))
        self.assertNotIn("hose", desk.snapshot()["form"]["assumed"])
        digest = status.build(desk.record.snapshot(project_id))
        self.assertFalse(any(line.startswith("hose_gpm ASSUMED") for line in digest["assumed"]))
        self.assertTrue(any(line.startswith("density_gpm_ft2 ASSUMED") for line in digest["assumed"]))

    def test_an_accepted_edition_hint_never_clears_the_hold(self):
        """The edition sets the battery factor (1.20 or 1.25) and the cites. A hint used for it is not a pin."""
        from fpfa import inputs, status
        from fpfa.checker import coverage
        from fpfa.coherence import analyze

        desk = self._desk()
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        # The sample states 2025 for both: pinned, so no HOLD. Then the designer clears NFPA 13 and uses its hint.
        self.assertEqual(status.build(desk.record.snapshot(project_id))["unpinned"], [])
        desk.patch_form({"nfpa_13": ""})
        desk.accept_hints(["nfpa_13"])
        self.assertEqual(desk.nfpa_13.get(), "2025")
        desk.save_current()
        row = desk.record.givens(project_id)["nfpa_13"]
        self.assertEqual((row["label"], row["value"]), ("ASSUMED", "2025"))
        snapshot = desk.record.snapshot(project_id)
        digest = status.build(snapshot)
        self.assertEqual(len(digest["unpinned"]), 1)
        hold = digest["unpinned"][0]
        self.assertTrue(hold.startswith("HOLD: NFPA 13 edition not pinned. 2025 is ASSUMED, a hint the designer used"))
        self.assertIn(hold, status.lead_text(digest))
        self.assertIn(hold, coverage(snapshot)["gaps"])
        # The calculations whose cites name NFPA 13-2025 hold too: an ASSUMED 2025 is not the job's stated edition.
        analysis = analyze(snapshot)
        self.assertTrue(analysis["edition_holds"])
        gap = analysis["calcs"][analysis["edition_holds"][0]]["edition_gaps"][0]
        self.assertIn("is ASSUMED, a hint the designer used (edition not pinned)", gap["job"])
        # A run on it keeps the HOLD in its flags.
        desk.start_zone_run()
        desk.pump()
        flags = "\n".join(desk.project["last_run"]["flags"])
        self.assertIn("EDITION NOT RECONCILED", flags)
        self.assertIn("ASSUMED, a hint the designer used", flags)
        # The designer types the edition: now it is pinned, and the HOLD goes.
        desk.patch_form({"nfpa_13": "2025"})
        desk.save_current()
        self.assertEqual(desk.record.givens(project_id)["nfpa_13"]["label"], "CODE")
        snapshot = desk.record.snapshot(project_id)
        self.assertEqual(status.build(snapshot)["unpinned"], [])
        self.assertEqual(analyze(snapshot)["edition_holds"], [])

    def test_a_run_names_each_input_taken_from_a_hint(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        result = run_di_zone(REPO, dict(EXAMPLE_DI), dict(EXAMPLE_BASIS), assumed=["density_gpm_ft2", "nfpa_72"])
        flags = result["flags"]
        self.assertTrue(any(flag.startswith("density_gpm_ft2 ASSUMED: 0.2 gpm/ft2 is a hint the designer used")
                            for flag in flags), flags)
        self.assertFalse(any(flag.startswith("nfpa_72 ASSUMED") for flag in flags), "an edition is a HOLD of its own")
        plain = run_di_zone(REPO, dict(EXAMPLE_DI), dict(EXAMPLE_BASIS))
        self.assertFalse(any("ASSUMED: " in flag and "hint the designer used" in flag for flag in plain["flags"]))

    def test_an_earlier_versions_unconfirmed_starting_values_leave_the_job(self):
        from fpfa import inputs
        from fpfa.projects import load_project, new_project, save_project

        desk = self._desk()
        project = new_project("Saved by 0.3.2", {"nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM"})
        project["di"] = {"q_fill_gpm": 600.0, "density_gpm_ft2": 0.25, "t_detect_s": 0.0, "hazard": "ordinary"}
        project["given"] = {"density_gpm_ft2": inputs.SOURCE_DESIGNER}
        save_project(project)
        self.assertEqual(sorted(inputs.unconfirmed_starting_values(project)),
                         ["hazard", "insurer", "nfpa_13", "nfpa_72", "q_fill_gpm"])
        desk.refresh_projects()
        desk.open_project(project["id"])
        # The typed density stays. The rest nobody entered: blank, with their hints, and said in the status line.
        self.assertEqual((desk.density.get(), desk.q_fill.get(), desk.hazard.get(), desk.nfpa_72.get()),
                         ("0.25", "", "", ""))
        # A 0 time was the old form's placeholder, not a hint: it was a value and is kept for the designer to see.
        self.assertEqual(desk.t_detect.get(), "0.0")
        self.assertIn("hints now", desk.status.get())
        saved = load_project(project["id"])
        self.assertEqual((saved["di"]["q_fill_gpm"], saved["basis"]["nfpa_72"]), (None, ""))

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
        # The form shows the lead's value as well, so the next save does not read 600 off it as a change.
        self.assertEqual(second.q_fill.get(), "750.0")
        second.save_current()
        row = second.record.givens(project_id)["q_fill_gpm"]
        self.assertEqual((row["agent"], inputs.decode(row["value"])), ("lead", 750.0))

    def test_an_input_the_lead_set_mid_turn_reaches_the_form_and_unsaved_typing_stays(self):
        """The team is working and has recorded 750. The designer has typed a field and asks where things stand.

        /status opens the record without saving the form first. The lead's value must show on the form at once,
        or the next save reads the old 600 off it as the designer's change. What the designer typed and has not
        saved must not be lost to that.
        """
        from fpfa import inputs

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        project_id = desk.project["id"]
        desk.save_current()
        desk.patch_form({"t_detect": "12", "ahj": "County fire district"})        # typed, not saved
        _change(desk.record, "q_fill_gpm", 750, project_id=project_id, agent="lead")
        desk.show_status()
        self.assertEqual(desk.q_fill.get(), "750.0")
        self.assertEqual(desk.t_detect.get(), "12.0")
        self.assertEqual(desk.ahj.get(), "County fire district")
        desk.save_current()
        rows = desk.record.givens(project_id)
        self.assertEqual((rows["q_fill_gpm"]["agent"], inputs.decode(rows["q_fill_gpm"]["value"])), ("lead", 750.0))
        self.assertEqual((rows["t_detect_s"]["agent"], inputs.decode(rows["t_detect_s"]["value"])), ("job form", 12.0))
        self.assertEqual(rows["t_detect_s"]["source"], "zone form")
        self.assertEqual((rows["ahj"]["agent"], rows["ahj"]["value"]), ("job form", "County fire district"))
        self.assertEqual(desk.project["given"]["t_detect_s"], inputs.SOURCE_DESIGNER)
        self.assertEqual(desk.project["given"]["q_fill_gpm"], inputs.SOURCE_CHAT)

    def test_a_basis_field_stated_in_chat_reaches_an_empty_field_on_the_basis_tab(self):
        """The AHJ field is empty and the designer names the AHJ in chat. The lead's set_input must show on the tab."""
        from fpfa import inputs
        from fpfa.projects import load_project
        from fpfa.team import TeamSession

        desk = self._desk()
        desk.patch_form({"t_detect": "12"})
        desk.save_current()
        project_id = desk.project["id"]
        self.assertEqual(desk.ahj.get(), "")
        self.assertNotIn("ahj", desk.record.givens(project_id))
        # The lead's own tool, as a turn would call it. No model is involved: the call is made directly.
        lead = TeamSession(REPO, desk.record, project_id, lambda **_kwargs: None)
        out = lead.execute("set_input", {"name": "ahj", "value": "City fire marshal", "why": "stated in chat"})
        self.assertEqual((out["was"], out["now"]), ("not on the record", "City fire marshal"))
        # The turn ends: the desk puts what the lead recorded on the form and the job file.
        pulled = desk._pull_inputs_onto_form(desk.project)
        self.assertEqual(pulled, ["ahj"])
        self.assertEqual(desk.ahj.get(), "City fire marshal")
        desk.save_current()
        saved = load_project(project_id)
        self.assertEqual(saved["basis"]["ahj"], "City fire marshal")
        self.assertEqual(saved["given"]["ahj"], inputs.SOURCE_CHAT)
        row = desk.record.givens(project_id)["ahj"]
        self.assertEqual((row["agent"], row["value"]), ("lead", "City fire marshal"))
        # The designer empties the field on the Basis tab. The record stops stating it and it does not come back.
        desk.patch_form({"ahj": ""})
        desk.save_current()
        self.assertNotIn("ahj", desk.record.givens(project_id))
        desk.save_current()
        self.assertEqual(desk.ahj.get(), "")
        self.assertNotIn("ahj", desk.record.givens(project_id))
        self.assertEqual(load_project(project_id)["basis"]["ahj"], "")
        # A blank edition or insurer is not on the record either: no 2025 and no FM is put in its place.
        self.assertEqual({"nfpa_13", "nfpa_72", "insurer"} & set(desk.record.givens(project_id)), set())



# A new job's basis as fpfa.projects.new_project writes it: three starting values nobody stated.
_NEW_JOB_BASIS = {"ahj": "", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM", "hazard_notes": ""}
_STARTING_SOURCE = "job form (starting value, not confirmed by the designer)"


class BasisStartingValueTests(unittest.TestCase):
    """A new job's NFPA 13, NFPA 72, and insurer start blank (FA Lead's ruling, 2026-11-12). An earlier version
    started them at 2025, 2025, and FM; where an older record still holds one, it is shown as a starting value
    not confirmed by the designer, and an edition that is one pins nothing.

    These tests check how the application labels values; they do not say an edition or an insurer is right.
    """

    _desk = DeskInputTests._desk

    def _fresh(self):
        """A new job the designer typed one zone field on, and saved."""
        desk = self._desk()
        desk.patch_form({"t_detect": "12"})
        desk.save_current()
        return desk, desk.project["id"]

    def test_provenance_reads_a_basis_starting_value_as_not_confirmed(self):
        from fpfa import inputs

        project = {"basis": dict(_NEW_JOB_BASIS, nfpa_72="2022")}
        self.assertEqual(inputs.provenance(project, "nfpa_13", "2025"), inputs.SOURCE_DEFAULT)
        self.assertEqual(inputs.provenance(project, "insurer", "FM"), inputs.SOURCE_DEFAULT)
        self.assertEqual(inputs.provenance(project, "nfpa_72", "2022"), inputs.SOURCE_DESIGNER)
        # A blank AHJ is blank, not a starting value.
        self.assertEqual(inputs.unconfirmed_basis(project), ["nfpa_13", "insurer"])
        inputs.note_given(project, ["nfpa_13"], inputs.SOURCE_DESIGNER)
        self.assertEqual(inputs.unconfirmed_basis(project), ["insurer"], "typed, the starting value is the designer's")
        self.assertEqual(inputs.unconfirmed_basis(project, {"insurer": "FM", "nfpa_72": "2025"}), ["nfpa_72", "insurer"])
        self.assertEqual(inputs.source_text(inputs.SOURCE_DEFAULT, "insurer"), _STARTING_SOURCE)
        self.assertIn(inputs.UNCONFIRMED_MARK, _STARTING_SOURCE)
        self.assertEqual(inputs.source_text(inputs.SOURCE_DESIGNER, "nfpa_13"), "job form")
        self.assertEqual(inputs.source_text(inputs.SOURCE_CHAT, "nfpa_13"), "designer, in chat")
        self.assertEqual(inputs.source_text(inputs.SOURCE_SAMPLE, "nfpa_13"), "SAMPLE data")
        # The zone form's words are unchanged.
        self.assertEqual(inputs.source_text(inputs.SOURCE_DESIGNER), "zone form")
        self.assertEqual(inputs.source_text(inputs.SOURCE_DEFAULT, "q_fill_gpm"),
                         "zone form (starting value, not confirmed by the designer)")

    def test_a_fresh_job_records_no_basis_starting_value_and_holds_its_editions(self):
        from fpfa import inputs, status
        from fpfa.projects import load_project

        desk, project_id = self._fresh()
        self.assertEqual({key: load_project(project_id)["basis"][key] for key in ("nfpa_13", "nfpa_72", "insurer")},
                         {"nfpa_13": "", "nfpa_72": "", "insurer": ""})
        rows = desk.record.givens(project_id)
        for name in ("nfpa_13", "nfpa_72", "insurer", "ahj"):
            self.assertNotIn(name, rows, "a blank basis field has no fact: nothing is put in its place")
        digest = status.build(desk.record.snapshot(project_id))
        self.assertEqual(digest["unconfirmed"], [])
        self.assertEqual([line.split(".")[0] for line in digest["unpinned"]],
                         ["HOLD: NFPA 13 edition not pinned", "HOLD: NFPA 72 edition not pinned"])
        self.assertNotIn(inputs.UNCONFIRMED_MARK, status.lead_text(digest))

    def test_an_older_records_starting_values_are_shown_as_not_confirmed(self):
        """An older record can still hold 2025, 2025, and FM as starting values. Every view says what they are."""
        from fpfa import inputs, status, team
        from fpfa.team_panel import team_view

        record = _record()
        record.ensure_project("job1", "Older job")
        for name, value, label in (("nfpa_13", "2025", "CODE"), ("nfpa_72", "2025", "CODE"), ("insurer", "FM", "OWNER")):
            record.set_given("job1", kind=inputs.BASIS_KIND, key=name, value=value, label=label,
                             source=_STARTING_SOURCE, agent="job form")
        rows = record.givens("job1")
        snapshot = record.snapshot("job1")
        digest = status.build(snapshot)
        unconfirmed = {row["name"]: row["text"] for row in digest["unconfirmed"]}
        self.assertEqual(unconfirmed, {"nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM"})
        # A starting value pins no edition: both editions hold.
        self.assertEqual(len(digest["unpinned"]), 2)
        lead = status.lead_text(digest).splitlines()
        loose = [line for line in lead if line.startswith("- Starting values the designer has not confirmed")]
        self.assertEqual(len(loose), 1)
        self.assertIn("insurer FM", loose[0])
        said = status.designer_text(digest)
        self.assertIn("**Starting values you have not confirmed**", said)
        line = team_view(snapshot)["unconfirmed_line"]
        self.assertTrue(line.startswith("Starting values you have not confirmed: nfpa_13 2025; nfpa_72 2025; insurer FM"), line)
        self.assertIn(f"- [{rows['nfpa_13']['id']}] nfpa_13: 2025 (starting value, not confirmed by the designer)",
                      team._input_lines(digest))
        self.assertIn(f"- [{rows['insurer']['id']}] basis/insurer: FM (OWNER) (starting value, not confirmed)",
                      status.record_text(snapshot).splitlines())
    def test_the_team_tab_says_nothing_when_every_value_was_supplied(self):
        from fpfa.team_panel import team_view

        desk = self._desk()
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        view = team_view(desk.record.snapshot(desk.project["id"]))
        self.assertEqual(view["unconfirmed_line"], "")
        self.assertEqual(team_view(None)["unconfirmed_line"], "")

    def test_typing_or_stating_a_basis_value_records_it_and_emptying_one_leaves_it_blank(self):
        from fpfa import inputs, status
        from fpfa.team import TeamSession

        desk, project_id = self._fresh()
        # Typing the edition makes it the designer's, a value equal to the hint included.
        desk.patch_form({"nfpa_13": "2025"})
        desk.save_current()
        row = desk.record.givens(project_id)["nfpa_13"]
        self.assertEqual((row["value"], row["source"], row["agent"], row["label"]),
                         ("2025", "typed from form hint", "job form", "CODE"))
        # Emptying it leaves it blank: no starting value comes back, and the HOLD returns.
        desk.patch_form({"nfpa_13": ""})
        desk.save_current()
        self.assertNotIn("nfpa_13", desk.record.givens(project_id))
        self.assertEqual(desk.project["basis"]["nfpa_13"], "")
        self.assertTrue(any(line.startswith("HOLD: NFPA 13 edition not pinned")
                            for line in status.build(desk.record.snapshot(project_id))["unpinned"]))
        # Stated in chat: the lead records it with set_input. No model is involved; the call is made directly.
        lead = TeamSession(REPO, desk.record, project_id, lambda **_kwargs: None)
        lead.execute("set_input", {"name": "insurer", "value": "FM", "why": "stated in chat"})
        desk._pull_inputs_onto_form(desk.project)
        desk.save_current()
        row = desk.record.givens(project_id)["insurer"]
        self.assertEqual(row["agent"], "lead")
        self.assertTrue(row["source"].startswith("designer, in chat"), row["source"])
        unconfirmed = {item["name"] for item in status.build(desk.record.snapshot(project_id))["unconfirmed"]}
        self.assertFalse(unconfirmed & set(inputs.BASIS_FIELDS), unconfirmed)
    def test_a_starting_value_noted_on_an_older_job_leaves_it_whatever_its_value(self):
        """An older job noted an untouched field as a starting value. That note, not today's list, says so."""
        from fpfa import inputs
        from fpfa.projects import load_project, new_project, save_project

        desk = self._desk()
        project = new_project("Older job", {"nfpa_13": "2022", "nfpa_72": "2019", "insurer": "XL"})
        project["given"] = {"nfpa_13": inputs.SOURCE_DEFAULT, "nfpa_72": inputs.SOURCE_DESIGNER}
        save_project(project)
        self.assertEqual(sorted(inputs.unconfirmed_starting_values(project)), ["nfpa_13"])
        desk.refresh_projects()
        desk.open_project(project["id"])
        self.assertEqual((desk.nfpa_13.get(), desk.nfpa_72.get(), desk.insurer.get()), ("", "2019", "XL"))
        self.assertEqual(load_project(project["id"])["basis"]["nfpa_13"], "")
    def test_correcting_an_older_jobs_basis_source_keeps_its_calcs_current(self):
        """A job recorded before called its untouched editions 'job form'. The new source is not a change."""
        from fpfa import inputs
        from fpfa.coherence import analyze
        from fpfa.record import BASIS_LABELS

        record = _record()
        di, basis = _seed_inputs(record)                       # basis rows with the source "job form"
        _run_plan(record, di, basis)
        shown = {key: str(basis.get(key) or "") for key, _label in BASIS_LABELS}
        sources = {key: inputs.source_text(inputs.provenance({}, key, value), key) for key, value in shown.items()}
        out = record.sync_form("job1", inputs.BASIS_KIND, shown, labels=dict(BASIS_LABELS), sources=sources,
                               shown_before=shown)
        self.assertEqual({row["key"] for row in out["written"]}, {"nfpa_13", "nfpa_72", "insurer"})
        self.assertEqual(record.givens("job1")["nfpa_13"]["source"], _STARTING_SOURCE)
        self.assertEqual(record.givens("job1")["ahj"]["source"], "job form")
        self.assertIsNone(record.latest_event("job1", "input_changed"))
        analysis = analyze(record.snapshot("job1"))
        self.assertFalse(analysis["any_stale"])
        self.assertEqual({item["state"] for item in analysis["calcs"].values()}, {"current"})

    def test_an_edition_hold_never_says_the_job_states_a_starting_value(self):
        from fpfa import inputs, status
        from fpfa.coherence import EDITION_HOLD, EDITION_OPEN, EDITION_OPEN_STARTING, analyze, edition_gaps, edition_hold_text

        # Synthetic cite strings: only the edition label in them is read.
        older = {"cite": "NFPA 13-2019 section text, synthetic"}
        stated = edition_gaps(older, {"nfpa_13": "2025"})
        self.assertEqual(stated[0]["job"], "the job states NFPA 13-2025")
        starting = edition_gaps(older, {"nfpa_13": "2025"}, unconfirmed={"nfpa_13"})
        self.assertEqual(len(starting), 1)
        self.assertEqual(starting[0]["job"], 'the job\'s NFPA 13 edition is the form\'s starting value "2025", '
                                             "not confirmed by the designer (edition not pinned)")
        self.assertTrue(edition_hold_text(starting).endswith(EDITION_OPEN_STARTING))
        self.assertTrue(edition_hold_text(stated).endswith(EDITION_OPEN), "a stated edition keeps its wording")
        self.assertNotIn("the job states", edition_hold_text(starting))
        # A starting value pins nothing: even one that names the cites' edition holds (the owner's review,
        # 2026-11-12), and so does an ASSUMED one taken from a hint.
        self.assertEqual(len(edition_gaps({"cite": "NFPA 13-2025 synthetic"}, {"nfpa_13": "2025"}, unconfirmed={"nfpa_13"})), 1)
        assumed = edition_gaps({"cite": "NFPA 13-2025 synthetic"}, {"nfpa_13": "2025"}, assumed={"nfpa_13"})
        self.assertIn("is ASSUMED, a hint the designer used (edition not pinned)", assumed[0]["job"])
        self.assertTrue(edition_hold_text(assumed).endswith(EDITION_OPEN_STARTING))
        # On the record, the mark is read from the basis row's source.
        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        record.set_given("job1", kind=inputs.BASIS_KIND, key="nfpa_13", value="2022", label="CODE",
                         source=_STARTING_SOURCE, agent="job form")
        analysis = analyze(record.snapshot("job1"))
        self.assertTrue(analysis["edition_holds"])
        for ident in analysis["edition_holds"]:
            hold = analysis["calcs"][ident]["edition_hold"]
            self.assertTrue(hold.startswith(EDITION_HOLD), hold)
            self.assertIn('the form\'s starting value "2022", not confirmed by the designer', hold)
            self.assertNotIn("the job states", hold)
        lines = status.build(record.snapshot("job1"))["edition_lines"]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith(EDITION_OPEN_STARTING), lines[0])
        self.assertNotIn("the job states", lines[0])
    def test_the_zone_run_flags_never_say_the_job_states_an_assumed_edition(self):
        from unittest import mock

        from fpfa import desk as desk_module
        from fpfa.coherence import EDITION_HOLD
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        moved = dict(EXAMPLE_BASIS, nfpa_13="2022")
        held = [flag for flag in run_di_zone(REPO, EXAMPLE_DI, moved)["flags"] if flag.startswith(EDITION_HOLD)]
        self.assertIn("the job states NFPA 13-2022", held[0])
        held = [flag for flag in run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, assumed=("nfpa_13",))["flags"]
                if flag.startswith(EDITION_HOLD)]
        self.assertEqual(len(held), 1, "an ASSUMED 2025 holds even though the cites name 2025")
        self.assertIn("is ASSUMED, a hint the designer used (edition not pinned)", held[0])
        self.assertNotIn("the job states", held[0])
        # The desk tells the run which inputs the designer took from a hint.
        desk, _project_id = self._fresh()
        desk.ask_claude.set(False)
        desk._apply_di(copy.deepcopy(EXAMPLE_DI))
        desk.accept_hints(["nfpa_13", "nfpa_72"])
        with mock.patch.object(desk_module, "run_di_zone", wraps=run_di_zone) as spy:
            desk.start_zone_run()
            desk.pump()
        self.assertEqual(sorted(spy.call_args.kwargs["assumed"]), ["nfpa_13", "nfpa_72"])
    def test_the_section_export_marks_a_basis_starting_value(self):
        from fpfa import inputs
        from fpfa.sample_data import EXAMPLE_DI
        from fpfa.spec_docx import basis_line, write_docx
        from fpfa.workflow import run_di_zone
        from test_design_basis import _docx_text

        # An older job that still holds the earlier version's starting values, noted as such.
        project = {"name": "Older job", "basis": dict(_NEW_JOB_BASIS),
                   "given": {name: inputs.SOURCE_DEFAULT for name in ("nfpa_13", "nfpa_72", "insurer")}}
        line = basis_line(project, project["basis"])
        self.assertIn("AHJ: —. NFPA 13: 2025 (starting value, not confirmed by the designer). "
                      "NFPA 72: 2025 (starting value, not confirmed by the designer). "
                      "Insurer: FM (starting value, not confirmed by the designer).", line)
        self.assertIn("the designer did not state it", line)
        result = run_di_zone(REPO, EXAMPLE_DI, project["basis"])
        path = write_docx(Path(tempfile.mkdtemp(prefix="fpfa-coherence-spec-")) / "section.docx", project, result)
        self.assertIn(line, _docx_text(path))
        typed = dict(project, given={name: inputs.SOURCE_DESIGNER for name in inputs.BASIS_FIELDS})
        self.assertEqual(basis_line(typed, typed["basis"]), "AHJ: —. NFPA 13: 2025. NFPA 72: 2025. Insurer: FM.")
        sample = dict(project, given={name: inputs.SOURCE_SAMPLE for name in inputs.BASIS_FIELDS})
        self.assertNotIn(inputs.UNCONFIRMED_MARK, basis_line(sample, sample["basis"]))
        # A new job's blank editions are not pinned; an edition taken from a hint is ASSUMED and not pinned either.
        blank = {"name": "New job", "basis": {"ahj": "", "nfpa_13": "", "nfpa_72": "", "insurer": "", "hazard_notes": ""}}
        self.assertEqual(basis_line(blank, blank["basis"]),
                         "AHJ: —. NFPA 13: — (edition not pinned). NFPA 72: — (edition not pinned). Insurer: —.")
        hinted = {"name": "New job", "basis": dict(blank["basis"], nfpa_72="2025"),
                  "given": {"nfpa_72": inputs.SOURCE_ACCEPTED}}
        line = basis_line(hinted, hinted["basis"])
        self.assertIn("NFPA 72: 2025 (ASSUMED, a hint the designer used; edition not pinned).", line)
        self.assertIn("An ASSUMED value is a hint the designer used, not a design value.", line)

    def test_the_design_basis_export_marks_a_basis_starting_value(self):
        from fpfa import inputs
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.record import BASIS_LABELS
        from test_design_basis import _docx_text

        record = _record()
        record.ensure_project("job1", "New job")
        record.sync_form("job1", inputs.BASIS_KIND, dict(_NEW_JOB_BASIS), labels=dict(BASIS_LABELS),
                         sources={key: inputs.source_text(inputs.provenance({}, key, value), key)
                                  for key, value in _NEW_JOB_BASIS.items()})
        path = Path(tempfile.mkdtemp(prefix="fpfa-coherence-basis-")) / "basis.docx"
        text = _docx_text(write_design_basis(path, {"id": "job1", "name": "New job"}, record.snapshot("job1"),
                                             content_root=REPO))
        rows = record.givens("job1")
        self.assertIn(f"nfpa_13 | 2025 | CODE | {_STARTING_SOURCE} UNCONFIRMED | {rows['nfpa_13']['id']}", text)
        self.assertIn(f"insurer | FM | OWNER | {_STARTING_SOURCE} UNCONFIRMED | {rows['insurer']['id']}", text)
        self.assertIn(f"Starting value not confirmed by the designer: nfpa_72 2025 [{rows['nfpa_72']['id']}]", text)

    def test_the_bess_sample_basis_is_sample_data(self):
        desk = self._desk()
        desk._open_bess_project()
        rows = desk.record.givens(desk.project["id"])
        self.assertEqual({rows[name]["source"] for name in ("nfpa_13", "nfpa_72", "insurer")}, {"SAMPLE data"})


if __name__ == "__main__":
    unittest.main()
