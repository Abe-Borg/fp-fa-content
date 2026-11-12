"""PR-D of the post-merge review of PR #100 (QA, FP Lead, FA Lead): no silent defaults, the releasing table, the
volume basis, the export gates, the charger HOLD, the LFL bypass, and live_eval's threshold name.

One class per item of the review. No model is called and no agent is scripted here. Nothing here checks an
engineering statement against a standard: where a figure is compared, the expected value is the kernel's own
figure on another call or a contract property the review states, never a number worked out from the code under
test. The cite in the friction sentence is the calc pack's own label, read from the pack file that holds it.
"""

from __future__ import annotations

import copy
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402
from test_coherence import _seed_inputs  # noqa: E402
from test_team import _record  # noqa: E402

SEGMENTS = [{"d_in": 4.26, "length_ft": 300}]


def _sample(variant="dh1", **changes):
    from fpfa import sample_data

    _name, basis, di = sample_data.SAMPLE_ZONES[variant]
    di = copy.deepcopy(di)
    di.update(changes)
    return di, copy.deepcopy(basis)


def _run(di, basis, assumed=(), record=None, project_id=None):
    from fpfa.workflow import run_di_zone

    return run_di_zone(REPO, di, basis, assumed=assumed, record=record, project_id=project_id)


def _session(agent="lead", record=None, project_id=None):
    from fpfa.calc_tools import ToolSession

    return ToolSession(REPO, agent=agent, record=record, project_id=project_id)


def _screen(**changes):
    args = {"segments": SEGMENTS, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 1,
            "basis": "FM", "system_type": "di", "edition": "2025"}
    args.update(changes)
    return {key: value for key, value in args.items() if value is not None}


class DensityAreaThroughFpCalcTests(unittest.TestCase):
    """1. fp_calc density_area: an omitted area_increase or hose_gpm is refused, never run as 0."""

    def test_each_omitted_one_is_refused_by_name(self):
        demand = {"density_gpm_ft2": 0.2, "base_area_ft2": 1500, "area_increase": 0.3, "hose_gpm": 250}
        for left_out in ("area_increase", "hose_gpm"):
            payload = {key: value for key, value in demand.items() if key != left_out}
            with self.subTest(left_out=left_out), self.assertRaisesRegex(ValueError, f"{left_out} is required"):
                _session().execute("fp_calc", {"op": "density_area", "inputs": payload})
            blank = {**demand, left_out: ""}
            with self.subTest(blank=left_out), self.assertRaisesRegex(ValueError, f"{left_out} is required"):
                _session().execute("fp_calc", {"op": "density_area", "inputs": blank})

    def test_a_typed_zero_still_runs_and_matches_the_tool(self):
        demand = {"density_gpm_ft2": 0.2, "base_area_ft2": 1500, "area_increase": 0, "hose_gpm": 0}
        through = _session().execute("fp_calc", {"op": "density_area", "inputs": demand})
        direct = _session().execute("density_area", demand)
        self.assertEqual(through["qd_gpm"], direct["qd_gpm"])


class NoLengthBasisDefaultTests(unittest.TestCase):
    """2. An omitted length_basis is refused; a direct screen with allowances needs one; nothing assumes cut."""

    def test_the_takeoff_refuses_an_omitted_blank_or_unknown_basis(self):
        for value in (None, "", "  ", "centre", "measured"):
            args = {"segments": SEGMENTS} if value is None else {"segments": SEGMENTS, "length_basis": value}
            with self.subTest(length_basis=value), self.assertRaisesRegex(ValueError, "length_basis"):
                _session().execute("zone_trapped_volume", args)

    def test_the_schemas_require_it(self):
        from fpfa.calc_tools import SCHEMAS

        schema = {item["name"]: item["input_schema"] for item in SCHEMAS}
        self.assertIn("length_basis", schema["zone_trapped_volume"]["required"])
        self.assertIn("length_basis", schema["dry_delivery_screen"]["properties"])

    def test_a_direct_screen_with_allowances_needs_a_basis(self):
        for allowance in ({"trim_gal": 5}, {"fittings_percent": 3}, {"trim_gal": 5, "fittings_percent": 0}):
            with self.subTest(**allowance), self.assertRaisesRegex(ValueError, "needs length_basis"):
                _session().execute("dry_delivery_screen", _screen(**allowance))

    def test_the_screen_takes_the_basis_it_is_given_not_cut(self):
        # The zone total on each basis is the takeoff's own figure on the same basis and allowances.
        for basis in ("center_to_center", "cut"):
            with self.subTest(basis=basis):
                screen = _session().execute("dry_delivery_screen", _screen(trim_gal=5, length_basis=basis))
                takeoff = _session().execute("zone_trapped_volume",
                                             {"segments": SEGMENTS, "length_basis": basis, "trim_gal": 5})
                self.assertAlmostEqual(screen["exemption_volume_gal"], takeoff["zone_gal"], places=9)
                self.assertEqual(screen["exemption_length_basis"], basis)
                self.assertAlmostEqual(screen["exemption_fittings_percent"], takeoff["fittings_percent"], places=9)
        on_c2c = _session().execute("dry_delivery_screen", _screen(trim_gal=5, length_basis="center_to_center"))
        on_cut = _session().execute("dry_delivery_screen", _screen(trim_gal=5, length_basis="cut"))
        self.assertNotIn("exemption_assumptions", on_c2c)
        self.assertTrue(any("ASSUMED fittings" in flag for flag in on_cut["exemption_assumptions"]))

    def test_zone_gal_alone_still_answers_and_a_pipe_only_call_still_does_not(self):
        on_zone = _session().execute("dry_delivery_screen", _screen(zone_gal=300))
        self.assertEqual(on_zone["exemption_status"], "zone total")
        self.assertNotIn("exemption_length_basis", on_zone)
        pipe_only = _session().execute("dry_delivery_screen", _screen())
        self.assertNotIn("exemption_volume_gal", pipe_only)


class ManualStationTests(unittest.TestCase):
    """3. An omitted or blank manual_station holds the releasing table: it is not taken as on."""

    def test_omitted_or_blank_holds(self):
        for args in ({}, {"manual_station": None}, {"manual_station": ""}, {"insurer": "FM"}):
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, "manual_station"):
                _session().execute("releasing_truth_table", args)

    def test_given_either_way_it_runs_on_what_was_given(self):
        on = _session().execute("releasing_truth_table", {"manual_station": True})
        off = _session().execute("releasing_truth_table", {"manual_station": False})
        self.assertTrue(on["manual_station"])
        self.assertFalse(off["manual_station"])

    def test_the_schema_requires_it(self):
        from fpfa.calc_tools import SCHEMAS

        schema = next(item for item in SCHEMAS if item["name"] == "releasing_truth_table")["input_schema"]
        self.assertIn("manual_station", schema["required"])


class ZoneTotalPositiveTests(unittest.TestCase):
    """4. A zone_gal of 0 or less, or one that is not a finite number, is refused by the screen."""

    def test_zero_negative_and_non_finite_are_refused(self):
        for value in (0, 0.0, -1, -0.001, float("nan"), float("inf"), "abc"):
            with self.subTest(zone_gal=value), self.assertRaisesRegex(ValueError, "zone_gal"):
                _session().execute("dry_delivery_screen", _screen(zone_gal=value))

    def test_a_small_positive_total_is_used(self):
        out = _session().execute("dry_delivery_screen", _screen(zone_gal=0.5))
        self.assertEqual(out["exemption_volume_gal"], 0.5)


class ReleasingForDoubleInterlockOnlyTests(unittest.TestCase):
    """5. Only a double-interlock zone gets the releasing table and is asked for the manual station and failsafe."""

    def test_the_plan_rows(self):
        from fpfa.workflow import plan_rows, planned_tools

        self.assertTrue(plan_rows({"system_type": "di"})["releasing"])
        for system in ("dry", "wet", ""):
            with self.subTest(system=system):
                self.assertFalse(plan_rows({"system_type": system})["releasing"])
        dry = planned_tools({"system_type": "dry"})
        self.assertIn("dry_delivery_screen", dry)
        self.assertIn("nitrogen_gate", dry)
        self.assertNotIn("releasing_truth_table", dry)

    def test_a_dry_zone_runs_with_neither_answer_and_gets_no_table(self):
        di, basis = _sample(system_type="dry", manual_station=None, failsafe_on_total_power_loss=None)
        result = _run(di, basis)
        self.assertNotIn("releasing_truth_table", result["tools"])
        self.assertIn("dry_delivery_screen", result["tools"])
        self.assertIn("The releasing table is for double-interlock zones", result["narrative"])
        self.assertEqual(result["tools"]["elect_di_trim"]["status"], "N/A")

    def test_a_double_interlock_zone_still_needs_both(self):
        from fpfa.workflow import validate_di

        for name in ("manual_station", "failsafe_on_total_power_loss"):
            di, _basis = _sample(**{name: None})
            with self.subTest(name=name), self.assertRaises(ValueError) as caught:
                validate_di(di)
            self.assertIn("anual station" if name == "manual_station" else "ailsafe", str(caught.exception))


class VolumeBasisTests(unittest.TestCase):
    """6. The basis is printed beside the volume, with the friction sentence, and each row says which basis it used."""

    def test_the_friction_cite_is_the_packs_own_label(self):
        from fpfa.workflow import FRICTION_NOTE, FRICTION_PACK_FILE, FRICTION_PACK_PHRASE

        self.assertIn(FRICTION_PACK_PHRASE, (REPO / FRICTION_PACK_FILE).read_text(encoding="utf-8"))
        year, section = FRICTION_PACK_PHRASE.split("-")[1].split(" s")
        self.assertIn(f"NFPA 13-{year} §{section}", FRICTION_NOTE)
        self.assertIn("VERIFY", FRICTION_NOTE)

    def test_center_to_center_with_no_allowance_is_said_beside_every_volume_line(self):
        from docx import Document

        from fpfa.design_basis_docx import key_figures
        from fpfa.results_panel import zone_figures
        from fpfa.spec_docx import write_docx
        from fpfa.workflow import FRICTION_NOTE, NO_ALLOWANCE

        di, basis = _sample()
        result = _run(di, basis)
        volume = result["tools"]["zone_trapped_volume"]
        self.assertEqual((volume["length_basis"], volume["fittings_percent"]), ("center_to_center", 0.0))
        # The narrative: beside the volume, and no section number (the trace check would read it as a claim).
        self.assertIn(f"(0%; {NO_ALLOWANCE})", result["narrative"])
        self.assertNotIn("28.2.3", result["narrative"])
        self.assertTrue(any(FRICTION_NOTE in flag for flag in result["flags"]))
        tile = next(item for item in zone_figures(result["tools"]) if item["key"] == "zone_total")
        self.assertIn(f"0.0 gal fittings allowance (0%; {NO_ALLOWANCE})", tile["lines"])
        self.assertIn(FRICTION_NOTE, tile["lines"])
        figures = key_figures("zone_trapped_volume", {}, volume)
        self.assertIn(f"(0%; {NO_ALLOWANCE})", figures)
        self.assertIn(FRICTION_NOTE, figures)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_docx(Path(tmp) / "section.docx", {"name": "t", "basis": basis}, result)
            text = "\n".join(p.text for p in Document(path).paragraphs)
        self.assertIn(f"(0%; {NO_ALLOWANCE})", text)
        self.assertIn(FRICTION_NOTE, text)
        self.assertIn("on the zone total passed as zone_gal (pipe + fittings + trim), on center-to-center", text)

    def test_cut_lengths_say_their_assumed_allowance_and_no_friction_sentence(self):
        from fpfa.workflow import FRICTION_NOTE, allowance_text

        di, basis = _sample("dh2", fittings_percent=None)
        result = _run(di, basis)
        volume = result["tools"]["zone_trapped_volume"]
        self.assertEqual(volume["length_basis"], "cut")
        self.assertEqual(allowance_text(volume), f"{volume['fittings_percent']:g}%; cut lengths, allowance ASSUMED")
        self.assertIn(f"({allowance_text(volume)})", result["narrative"])
        self.assertFalse(any(FRICTION_NOTE in flag for flag in result["flags"]))

    def test_the_takeoff_and_the_screen_each_name_their_basis(self):
        from fpfa.design_basis_docx import key_figures
        from fpfa.results_panel import zone_figures
        from fpfa.workflow import exemption_basis_text

        # The zone run: the screen is handed the takeoff's total and its basis.
        di, basis = _sample()
        result = _run(di, basis)
        screen = result["tools"]["dry_delivery_screen"]
        self.assertEqual(screen["exemption_length_basis"], "center_to_center")
        self.assertIn("The zone total was taken on center-to-center lengths.", result["narrative"])
        tile = next(item for item in zone_figures(result["tools"]) if item["key"] == "size_exemption")
        self.assertIn("The zone total was taken on center-to-center lengths.", tile["lines"])
        self.assertIn("on center-to-center", key_figures("dry_delivery_screen", {}, screen))
        # A direct call with allowances: its own basis and its own (kernel) allowance, ASSUMED on cut lengths.
        direct = _session().execute("dry_delivery_screen", _screen(trim_gal=5, length_basis="cut"))
        self.assertEqual(exemption_basis_text(direct),
                         f"The zone total was taken on cut lengths, fittings {direct['exemption_fittings_percent']:g}% "
                         "ASSUMED.")
        self.assertIn("cut lengths", direct["exemption_volume_basis"])
        self.assertIn("ASSUMED allowance for cut lengths", direct["exemption_volume_basis"])


class SectionGateTests(unittest.TestCase):
    """7. Section 21 13 19 holds on every ASSUMED input, a blank or ASSUMED insurer, and withheld NFPA 13 cites."""

    def test_the_sample_is_still_exported(self):
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        self.assertEqual(section_problem(_run(di, basis), {"basis": basis}), "")

    def test_every_assumed_input_is_named_in_one_message(self):
        from fpfa import inputs
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        names = ["area_increase", "hose_gpm", "delivery_basis", "fill_minutes"]
        result = _run(di, basis, assumed=names)
        project = {"basis": basis, "given": {name: inputs.SOURCE_ACCEPTED for name in names}}
        problem = section_problem(result, project)
        for name in names:
            with self.subTest(name=name):
                self.assertIn(f"{inputs.FORM_LABELS[name][0]} ({name}) is ASSUMED", problem)
        self.assertTrue(problem.startswith("Section 21 13 19 is not exported."), problem)
        # The run's own list holds it without the job's notes, and the record's labels without either.
        self.assertIn("Fill time (fill_minutes) is ASSUMED", section_problem(result, {"basis": basis}))
        plain = _run(di, basis)
        self.assertIn("Supervisory fill (supervisory_psig) is ASSUMED",
                      section_problem(plain, {"basis": basis}, assumed={"supervisory_psig"}))

    def test_a_blank_or_assumed_insurer_holds(self):
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        blank = {**basis, "insurer": ""}
        self.assertIn("Insurer (insurer) is blank", section_problem(_run(di, blank), {"basis": blank}))
        self.assertIn("Insurer (insurer) is ASSUMED (FM)",
                      section_problem(_run(di, basis), {"basis": basis}, assumed={"insurer"}))

    def test_an_edition_with_withheld_cites_holds(self):
        from fpfa.calc_tools import EDITION_NOT_HELD
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        for year in ("2022", "2024"):
            pinned = {**basis, "nfpa_13": year}
            result = _run(di, pinned)
            rows = [result["tools"][name] for name in ("dry_delivery_screen", "di_trip_to_water")]
            if not all(row.get("edition_status") == "not held" for row in rows):
                # The kernel holds this edition's labels now: nothing is withheld, and nothing holds for it.
                self.assertNotIn(EDITION_NOT_HELD.format(year=year), section_problem(result, {"basis": pinned}))
                continue
            with self.subTest(year=year):
                problem = section_problem(result, {"basis": pinned})
                self.assertIn(EDITION_NOT_HELD.format(year=year), problem)
                self.assertIn("not exported", problem)

    def test_a_blank_nfpa_72_holds_the_section(self):
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        blank = {**basis, "nfpa_72": ""}
        self.assertIn("HOLD: NFPA 72 edition not pinned", section_problem(_run(di, blank), {"basis": blank}))

    def test_holds_are_listed_together(self):
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        both = {**basis, "insurer": "", "nfpa_72": ""}
        problem = section_problem(_run(di, both, assumed=["hose_gpm"]), {"basis": both})
        for part in ("(1)", "(2)", "(3)", "NFPA 72", "Insurer", "Hose (hose_gpm)"):
            self.assertIn(part, problem)

    def test_the_desk_reads_the_records_assumed_labels_before_a_billed_check(self):
        from test_prototype import _isolate_data

        _isolate_data()
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        loop = Loop()
        self.addCleanup(loop.destroy)
        app = loop.open_desk()
        app.ask_claude.set(False)
        app.start_sample_di()
        loop.update()
        project_id = app.project["id"]
        row = app.record.givens(project_id)["supervisory_psi"]
        app.record.set_given(project_id, kind=row["kind"], key="supervisory_psi", value=row["value"],
                             label="ASSUMED", source="an unmarked kPa read as gauge", agent="lead")
        self.assertIn("supervisory_psi", app._record_assumed())
        app.start_claim_check()
        loop.update()
        self.assertIn("supervisory_psi is ASSUMED (15 psi)", app.notices[-1]["message"])


class Nfpa72DesignBasisTests(unittest.TestCase):
    """8. A blank NFPA 72 edition: the Design Basis is a working draft whose cover says so and whose FA figures hold."""

    def _write(self, nfpa_72: str, with_delivery: bool = False) -> str:
        from docx import Document

        from fpfa.design_basis_docx import write_design_basis

        record = _record()
        di, basis = _sample()
        basis = {**basis, "nfpa_72": nfpa_72}
        _seed_inputs(record, di=di, basis=basis)
        if with_delivery:
            _run(di, basis, record=record, project_id="job1")
        session = _session("fa-releasing", record=record, project_id="job1")
        battery = session.execute("fa_calc", {"module": "battery", "op": "ah_required", "inputs": {
            "i_standby_a": 1.5, "i_alarm_a": 4.0, "edition": 2025}})
        self.figure = f"{battery['req_ah']:.2f}"
        calc = next(row for row in record.calcs("job1") if row["tool"] == "fa_calc")
        record.record_finding("job1", text=f"The panel needs {self.figure} Ah of battery", label="calculated",
                              agent="fa-releasing", supports=[calc["id"]])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_design_basis(Path(tmp) / "basis.docx", {"name": "t"}, record.snapshot("job1"),
                                      content_root=REPO)
            doc = Document(path)
            parts = [p.text for p in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    parts.extend(cell.text for cell in row.cells)
        return "\n".join(parts)

    def test_an_fa_only_job_with_no_nfpa_72_is_a_working_draft_with_its_figures_held(self):
        from fpfa.design_basis_docx import NFPA72_FIGURES_HELD, NFPA72_FINDING_HELD

        text = self._write("")
        self.assertIn("HOLD: NFPA 72 edition not set", text.split("\n", 2)[1])
        self.assertIn("working draft", text)
        self.assertIn(NFPA72_FIGURES_HELD, text)
        self.assertIn(NFPA72_FINDING_HELD, text)
        self.assertNotIn(self.figure, text)

    def test_with_delivery_rows_too(self):
        text = self._write("", with_delivery=True)
        self.assertIn("HOLD: NFPA 72 edition not set", text)
        self.assertNotIn(self.figure, text)

    def test_a_pinned_edition_prints_the_figures_and_no_hold(self):
        text = self._write("2025")
        self.assertNotIn("HOLD: NFPA 72 edition not set", text)
        self.assertIn(self.figure, text)

    def test_which_rows_are_held(self):
        from fpfa.design_basis_docx import nfpa72_dependent

        self.assertTrue(nfpa72_dependent({"tool": "fa_calc", "inputs": {"module": "battery"}, "outputs": {}}))
        self.assertTrue(nfpa72_dependent({"tool": "fa_calc", "inputs": {"module": "nac_vdrop.py"}, "outputs": {}}))
        self.assertFalse(nfpa72_dependent({"tool": "fa_calc", "inputs": {"module": "lfl"}, "outputs": {}}))
        self.assertTrue(nfpa72_dependent({"tool": "x", "inputs": {}, "outputs": {"basis": "NFPA 72-2025 18.4"}}))
        self.assertFalse(nfpa72_dependent({"tool": "zone_trapped_volume", "inputs": {}, "outputs": {"zone_gal": 1}}))


class ChargerHoldTests(unittest.TestCase):
    """9. charger_ok without the listed cap: one HOLD message that stands on the job and in the export."""

    def test_one_message_for_every_cause_and_never_a_verdict(self):
        from fpfa.fa_calc import CHARGER_HOLD, run_fa_calc

        self.assertEqual(CHARGER_HOLD, "HOLD: listed_charger_max_ah required from the listed charger datasheet")
        for inputs_ in ({"req_ah": 50}, {"req_ah": 50, "maker_key": "any"}, {"req_ah": 50, "listed_charger_max_ah": -1},
                        {"req_ah": 50, "listed_charger_max_ah": math.nan}, {"req_ah": 50, "listed_charger_max_ah": True},
                        {"req_ah": 50, "listed_charger_max_ah": 110}):
            with self.subTest(inputs=inputs_):
                out = run_fa_calc(REPO, {"module": "battery", "op": "charger_ok", "inputs": inputs_})
                self.assertEqual(out, {"module": "battery", "op": "charger_ok", "status": "HOLD",
                                       "message": CHARGER_HOLD, "charger_ok": None})

    def test_the_hold_stands_in_the_status_and_the_export(self):
        from docx import Document

        from fpfa import checker, status
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.fa_calc import CHARGER_HOLD

        record = _record()
        di, basis = _sample()
        _seed_inputs(record, di=di, basis=basis)
        session = _session("fa-releasing", record=record, project_id="job1")
        session.execute("fa_calc", {"module": "battery", "op": "charger_ok", "inputs": {"req_ah": 50}})
        snapshot = record.snapshot("job1")
        digest = status.build(snapshot)
        self.assertEqual(digest["holds"], [CHARGER_HOLD])
        self.assertIn(CHARGER_HOLD, status.lead_text(digest))
        self.assertIn(CHARGER_HOLD, checker.coverage(snapshot)["gaps"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_design_basis(Path(tmp) / "basis.docx", {"name": "t"}, snapshot, content_root=REPO)
            doc = Document(path)
        self.assertIn(CHARGER_HOLD, [p.text for p in doc.paragraphs])
        # The charger row's figures are the one message, with no pass or fail beside it.
        cells = [[cell.text for cell in row.cells] for table in doc.tables for row in table.rows]
        charger = next(row for row in cells if row[0] == "fa_calc")
        self.assertEqual(charger[4], CHARGER_HOLD)

    def test_a_later_run_on_the_listed_cap_ends_it(self):
        from fpfa.fa_calc import standing_holds

        held = {"id": "a", "tool": "fa_calc", "inputs": {"module": "battery", "op": "charger_ok"},
                "outputs": {"status": "HOLD"}}
        ran = {"id": "b", "tool": "fa_calc", "inputs": {"module": "battery", "op": "charger_ok"},
               "outputs": {"value": True}}
        self.assertEqual(len(standing_holds([held])), 1)
        self.assertEqual(standing_holds([held, ran]), [])
        self.assertEqual(standing_holds([held], stale={"a"}), [])

    def test_no_maker_table_is_read(self):
        from fpfa import fa_calc

        def charger_ok(req_ah, listed_charger_max_ah):
            return req_ah <= listed_charger_max_ah

        self.assertIsNone(fa_calc.charger_hold(SimpleNamespace(charger_ok=charger_ok),
                                               {"req_ah": 50, "listed_charger_max_ah": 110}))
        self.assertIsNotNone(fa_calc.charger_hold(SimpleNamespace(charger_ok=charger_ok),
                                                  {"req_ah": 50, "listed_charger_max_ah": 110, "maker_key": "x"}))


class LflBypassTests(unittest.TestCase):
    """10. The LFL ops reached through fa_calc hold on a blank, zero, negative, or non-finite LFL, as lfl_setpoints does."""

    MIX = {"H2": 50, "CH4": 30, "CO2": 20}
    BAD_TABLES = ({"H2": 4.0, "CH4": None, "CO2": "inert"}, {"H2": 4.0, "CO2": "inert"},
                  {"H2": 4.0, "CH4": 0, "CO2": "inert"}, {"H2": 4.0, "CH4": "", "CO2": "inert"},
                  {"H2": 4.0, "CH4": -5, "CO2": "inert"}, {"H2": 4.0, "CH4": math.nan, "CO2": "inert"},
                  {"H2": 4.0, "CH4": 5.0, "CO2": None})

    def test_the_table_ops_hold(self):
        for op in ("lfl_mix", "lfl_with_diluent", "setpoints_for"):
            for table in self.BAD_TABLES:
                payload = {"mix": self.MIX, "lfl": table}
                if op == "setpoints_for":
                    payload["screens"] = []
                with self.subTest(op=op, lfl=table), self.assertRaisesRegex(ValueError, "HOLD"):
                    _session().execute("fa_calc", {"module": "lfl", "op": op, "inputs": payload})

    def test_the_figure_ops_hold(self):
        for op, extra in (("pct_of_lfl", {"conc_vol_pct": 1.0}), ("setpoint", {"pct": 10}), ("trigger_paths", {})):
            for value in (None, "", 0, -1, math.nan, math.inf):
                payload = {**extra, "lfl_vol_pct": value}
                if value is None:
                    payload.pop("lfl_vol_pct")
                with self.subTest(op=op, lfl_vol_pct=value), self.assertRaisesRegex(ValueError, "HOLD"):
                    _session().execute("fa_calc", {"module": "lfl", "op": op, "inputs": payload})

    def test_a_good_table_matches_lfl_setpoints_and_the_record_keeps_what_was_passed(self):
        record = _record()
        record.ensure_project("job1", "t")
        table = {"H2": 4.0, "CH4": 5.0, "CO2": "inert"}
        session = _session(record=record, project_id="job1")
        through = session.execute("fa_calc", {"module": "lfl", "op": "lfl_mix", "inputs": {"mix": self.MIX, "lfl": table}})
        own = _session().execute("lfl_setpoints", {"mix": self.MIX, "lfl": table, "screens": []})
        self.assertAlmostEqual(through["value"], own["lfl_fuel_vol_pct"], places=12)
        row = next(item for item in record.calcs("job1") if item["tool"] == "fa_calc")
        self.assertEqual(row["inputs"]["inputs"]["lfl"]["CO2"], "inert")


class LiveEvalThresholdTests(unittest.TestCase):
    """11. live_eval reads the exemption threshold under its own name."""

    def test_no_cap_name_is_read(self):
        text = (APP_DIR / "fpfa" / "live_eval.py").read_text(encoding="utf-8")
        self.assertNotIn("nfpa_size_cap_gal", text)
        self.assertIn("threshold_gal(out)", text)


if __name__ == "__main__":
    unittest.main()
