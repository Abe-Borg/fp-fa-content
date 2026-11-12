"""PR-C of the 2026-11-12 brief: what the application must do with a zone's delivery rows, its form, and its exports.

One class per item of the brief. No model is called: where a checker's reply
is needed it is a string written here, and an approve-all reply is used on
purpose to show it is not evidence. Nothing here checks an engineering
statement against a standard. Where a figure is compared, the expected value
is either a contract property the brief states (the fill-time margin is the
limit less the fill time; a zone total within 1% of the threshold is flagged)
or the kernel's own figure on another call, never a number worked out from
the code under test.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from test_coherence import _change, _seed_inputs  # noqa: E402
from test_team import _record  # noqa: E402

DELIVERY = ("dry_delivery_screen", "di_trip_to_water")
# The dry-pipe 60 s option and the dry-pipe QOD size, as the kernel labels them in both held editions. A
# double-interlock row must never cite either.
DRY_ONLY_CITES = ("s8.2.4.2 (60 s", "s8.2.3.2 (60 s", "750 gal", "§8.2.4.2.2", "§8.2.3.4")


def _sample(variant="dh1", **changes):
    from fpfa import sample_data

    _name, basis, di = sample_data.SAMPLE_ZONES[variant]
    di = copy.deepcopy(di)
    di.update(changes)
    return di, copy.deepcopy(basis)


def _run(di, basis, assumed=(), record=None, project_id=None):
    from fpfa.workflow import run_di_zone

    return run_di_zone(REPO, di, basis, assumed=assumed, record=record, project_id=project_id)


def _session(agent="lead"):
    from fpfa.calc_tools import ToolSession

    return ToolSession(REPO, agent=agent)


def _screen_args(**changes):
    args = {
        "segments": [{"d_in": 4.26, "length_ft": 300}],
        "q_fill_gpm": 600,
        "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 1,
        "basis": "FM",
        "system_type": "di",
        "edition": "2025",
    }
    args.update(changes)
    return {key: value for key, value in args.items() if value is not None}


class DeliveryArgumentTests(unittest.TestCase):
    """The delivery rows get the system type, the declared interlock, the job's edition, and v_basis caller."""

    def test_the_plan_passes_what_the_kernel_is_owed(self):
        di, basis = _sample()
        result = _run(di, basis)
        sent = {call["name"]: call["input"] for call in result["transcript"]}
        for name in DELIVERY:
            self.assertEqual(sent[name]["system_type"], "di")
            self.assertEqual(sent[name]["edition"], "2025")
        self.assertEqual(sent["dry_delivery_screen"]["declared_interlock"], "double")
        trip = result["tools"]["di_trip_to_water"]
        self.assertEqual(trip["v_basis"], "caller")
        self.assertEqual(result["tools"]["dry_delivery_screen"]["declared_interlock"], "double")
        for name in DELIVERY:
            self.assertNotIn("system_type_default_warning", result["tools"][name])

    def test_a_dry_zone_declares_no_interlock_and_keeps_the_dry_cites(self):
        di, basis = _sample(system_type="dry")
        result = _run(di, basis)
        sent = {call["name"]: call["input"] for call in result["transcript"]}
        self.assertEqual(sent["dry_delivery_screen"]["declared_interlock"], "none")
        self.assertEqual(result["tools"]["dry_delivery_screen"]["system_type"], "dry")

    def test_a_blank_system_type_refuses_the_run_and_the_tools(self):
        from fpfa.workflow import validate_di

        di, _basis = _sample(system_type=None)
        with self.assertRaisesRegex(ValueError, "System is blank"):
            validate_di(di)
        session = _session()
        for name, args in (("dry_delivery_screen", _screen_args(system_type=None)),
                           ("di_trip_to_water", {"v_gal": 300, "q_fill_gpm": 600, "basis": "FM"}),
                           ("elect_di_trim", {})):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "system_type"):
                session.execute(name, args)

    def test_no_or_di_fallback_is_left_in_the_application(self):
        for path in (APP_DIR / "fpfa").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn('or "di"', text)

    def test_a_wet_zone_skips_the_delivery_rows(self):
        di, basis = _sample(system_type="wet", q_fill_gpm=None, delivery_basis=None, qod=None,
                            supervisory_psig=None, fill_minutes=None, manual_station=None,
                            t_detect_s=None, t_release_s=None, t_exhaust_s=None)
        result = _run(di, basis)
        for name in (*DELIVERY, "nitrogen_gate", "releasing_truth_table"):
            self.assertNotIn(name, result["tools"])
        self.assertIn("A wet zone has no delivery rows", result["narrative"])
        with self.assertRaisesRegex(ValueError, "wet zone has no delivery rows"):
            _session().execute("dry_delivery_screen", _screen_args(system_type="wet"))

    def test_a_double_interlock_row_never_cites_the_dry_pipe_paths(self):
        for variant in ("dh1", "dh2"):
            di, basis = _sample(variant)
            result = _run(di, basis)
            for name in DELIVERY:
                text = json.dumps(result["tools"][name], ensure_ascii=False)
                for cite in DRY_ONLY_CITES:
                    with self.subTest(variant=variant, row=name, cite=cite):
                        self.assertNotIn(cite, text)

    def test_the_threshold_is_named_with_its_section_and_never_a_cap(self):
        di, basis = _sample()
        result = _run(di, basis)
        self.assertIn("500 gal exemption threshold (NFPA 13-2025 §8.3.2.3.1.1)", result["narrative"])
        printed = result["narrative"] + "\n".join(result["flags"])
        self.assertNotIn("gal cap", printed)
        self.assertNotIn("exempt, so it passes", printed.lower())

    def test_the_kernel_cite_is_shown_as_the_kernel_wrote_it(self):
        from fpfa.results_panel import zone_figures

        di, basis = _sample("dh2")
        result = _run(di, basis)
        note = result["tools"]["di_trip_to_water"]["note_60s_option"]
        tile = next(item for item in zone_figures(result["tools"]) if item["key"] == "t_total")
        self.assertIn(f"Kernel cite: {note}", tile["lines"])

    def test_fp_calc_does_not_run_the_delivery_screens(self):
        session = _session()
        for op in ("dry_delivery_screen", "di_trip_to_water", "dry-delivery-screen"):
            with self.subTest(op=op), self.assertRaisesRegex(ValueError, "tool"):
                session.execute("fp_calc", {"op": op, "inputs": {"v_gal": 300, "q_fill_gpm": 600}})


class EditionTests(unittest.TestCase):
    """The job's NFPA 13 edition goes to the kernel. Not pinned, or not labeled by the pack, the cites are withheld."""

    def _rows(self, nfpa_13, assumed=()):
        di, basis = _sample()
        basis["nfpa_13"] = nfpa_13
        return _run(di, basis, assumed=assumed)

    def test_a_blank_edition_runs_the_figures_and_withholds_every_cite(self):
        from fpfa.calc_tools import EDITION_NOT_SET

        pinned = self._rows("2025")["tools"]
        result = self._rows("")
        sent = {call["name"]: call["input"] for call in result["transcript"]}
        for name in DELIVERY:
            row = result["tools"][name]
            with self.subTest(row=name):
                self.assertNotIn("edition", sent[name])
                self.assertIsNone(row["edition"])
                self.assertEqual(row["edition_status"], "not set")
                self.assertEqual(row["note_60s_option"], EDITION_NOT_SET)
                self.assertNotIn("NFPA 13-", json.dumps(row, ensure_ascii=False))
                # The figures are the kernel's either way: the edition changes its labels only.
                self.assertEqual(row["t_total_s"], pinned[name]["t_total_s"])
        self.assertIn(EDITION_NOT_SET, result["narrative"])

    def test_2019_is_cited_as_2019(self):
        result = self._rows("2019")
        for name in DELIVERY:
            with self.subTest(row=name):
                self.assertEqual(result["tools"][name]["edition"], 2019)
                self.assertIn("NFPA 13-2019", result["tools"][name]["note_60s_option"])

    def test_2022_is_withheld_until_the_pack_holds_its_labels(self):
        result = self._rows("2022")
        for name in DELIVERY:
            row = result["tools"][name]
            with self.subTest(row=name):
                self.assertEqual(row["edition_status"], "not held")
                self.assertEqual(row["edition_requested"], "2022")
                self.assertIn("2022 labels are not in this calc pack", row["note_60s_option"])
                self.assertNotIn("NFPA 13-2025", json.dumps(row, ensure_ascii=False))

    def test_an_assumed_edition_pins_nothing(self):
        result = self._rows("2025", assumed={"nfpa_13"})
        for name in DELIVERY:
            self.assertEqual(result["tools"][name]["edition_status"], "not set")

    def test_the_record_holds_no_2025_for_a_blank_edition(self):
        record = _record()
        di, basis = _sample()
        basis["nfpa_13"] = ""
        _seed_inputs(record, di=di, basis=basis)
        _run(di, basis, record=record, project_id="job1")
        for row in record.calcs("job1"):
            if row["tool"] in DELIVERY:
                with self.subTest(row=row["tool"]):
                    self.assertNotIn("2025", json.dumps(row["inputs"]))
                    self.assertNotIn("NFPA 13-2025", json.dumps(row["outputs"], ensure_ascii=False))

    def test_a_changed_edition_puts_the_delivery_rows_out_of_date(self):
        from fpfa.coherence import STALE, analyze

        record = _record()
        di, basis = _sample()
        _seed_inputs(record, di=di, basis=basis)
        _run(di, basis, record=record, project_id="job1")
        _change(record, "nfpa_13", "2019")
        analysis = analyze(record.snapshot("job1"))
        for row in record.calcs("job1"):
            if row["tool"] in DELIVERY:
                self.assertEqual(analysis["calcs"][row["id"]]["state"], STALE, row["tool"])


class ExportGateTests(unittest.TestCase):
    """Section 21 13 19 and the Design Basis stay shut on an unpinned edition; the section is DI only."""

    def test_the_section_refuses_an_unpinned_edition_a_dry_or_wet_zone_and_an_assumed_demand(self):
        from fpfa.spec_docx import section_problem

        di, basis = _sample()
        self.assertEqual(section_problem(_run(di, basis)), "")
        blank = dict(basis, nfpa_13="")
        self.assertIn("edition not pinned", section_problem(_run(di, blank)))
        dry_di, _ = _sample(system_type="dry")
        self.assertIn("a dry-pipe zone", section_problem(_run(dry_di, basis)))
        assumed = _run(di, basis, assumed={"density_gpm_ft2"})
        self.assertIn("ASSUMED INPUT — not for release", section_problem(assumed))

    def test_write_docx_refuses_what_section_problem_names(self):
        import tempfile

        from fpfa.spec_docx import write_docx

        di, basis = _sample()
        result = _run(di, dict(basis, nfpa_13=""))
        with self.assertRaisesRegex(ValueError, "edition not pinned"):
            write_docx(Path(tempfile.mkdtemp()) / "x.docx", {"name": "t", "basis": result["basis"]}, result)

    def test_the_design_basis_waits_for_a_pinned_edition_once_delivery_rows_are_on_the_record(self):
        from fpfa.checker import EDITION_EXPORT_HOLD, export_reason

        record = _record()
        di, basis = _sample()
        basis["nfpa_13"] = ""
        _seed_inputs(record, di=di, basis=basis)
        _run(di, basis, record=record, project_id="job1")
        self.assertEqual(export_reason(record.snapshot("job1")), EDITION_EXPORT_HOLD)

        pinned = _record()
        di, basis = _sample()
        _seed_inputs(pinned, di=di, basis=basis)
        _run(di, basis, record=pinned, project_id="job1")
        self.assertEqual(export_reason(pinned.snapshot("job1")), "")

    def test_the_pipe_only_row_has_no_verdict_and_the_gas_fill_prints_the_typed_figures(self):
        import tempfile

        from docx import Document

        from fpfa.spec_docx import PIPE_ONLY_NOTE, write_docx

        di, basis = _sample("dh2")
        result = _run(di, basis)
        path = write_docx(Path(tempfile.mkdtemp()) / "s.docx", {"name": "t", "basis": basis}, result)
        doc = Document(str(path))
        table = next(t for t in doc.tables if t.rows[0].cells[0].text == "Screen")
        headers = [cell.text for cell in table.rows[0].cells]
        self.assertNotIn("Passes", headers)
        pipe = [cell.text for cell in table.rows[1].cells]
        self.assertIn(f"— ({PIPE_ONLY_NOTE})", pipe)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        # DH-2's typed supervisory fill is 20 psig: nothing put 40 or 30 in its place.
        self.assertIn("Both rates use 20 psig and 30 min.", text)
        source = (APP_DIR / "fpfa" / "spec_docx.py").read_text(encoding="utf-8")
        self.assertNotIn("or 40", source)
        self.assertNotIn("or 30", source)


class SubTimeTests(unittest.TestCase):
    """A blank sub-time is never 0: the rows are the fill time alone. A typed 0 is ASSUMED-ZERO."""

    def test_a_blank_sub_time_gives_the_fill_time_and_its_margin_and_nothing_else(self):
        from fpfa.calc_tools import FILL_ONLY

        full = _run(*_sample())["tools"]["di_trip_to_water"]
        result = _run(*_sample(t_detect_s=None))
        sent = {call["name"]: call["input"] for call in result["transcript"]}
        for name in DELIVERY:
            row = result["tools"][name]
            with self.subTest(row=name):
                self.assertNotIn("t_detect_s", sent[name])
                for gone in ("t_total_s", "passes_screen", "v_max_gal_at_limit", "margin_s"):
                    self.assertNotIn(gone, row)
                self.assertEqual(row["screen_status"], FILL_ONLY)
                self.assertEqual(row["subtimes_missing"], ["t_detect_s"])
                self.assertAlmostEqual(row["fill_margin_s"] + row["t_fill_s"], row["limit_s"], places=9)
        trip = result["tools"]["di_trip_to_water"]
        # The fill time is the kernel's own, the same on a call that had every sub-time.
        self.assertAlmostEqual(trip["t_fill_s"], full["t_fill_s"], places=9)
        self.assertIn(FILL_ONLY, result["narrative"])
        self.assertNotIn("does not pass", result["narrative"])

    def test_a_typed_zero_is_flagged_assumed_zero(self):
        result = _run(*_sample(t_release_s=0))
        note = result["tools"]["di_trip_to_water"]["assumed_zero_note"]
        self.assertIn("t_release_s = 0 s", note)
        self.assertIn("ASSUMED-ZERO", note)
        self.assertIn("NEEDS PE REVIEW", note)
        self.assertIn(note, result["flags"])

    def test_a_negative_sub_time_holds_the_run(self):
        from fpfa.workflow import validate_di

        with self.assertRaisesRegex(ValueError, "Detection time cannot be negative"):
            validate_di(_sample(t_detect_s=-1)[0])


class DemandTests(unittest.TestCase):
    """Density, base area, and a duration are > 0 on every path; an ASSUMED one is labeled and not for release."""

    def test_the_density_area_tool_refuses_a_meaningless_demand(self):
        session = _session()
        good = {"density_gpm_ft2": 0.2, "base_area_ft2": 1500, "area_increase": 0.3, "hose_gpm": 250}
        for change, words in (({"density_gpm_ft2": 0}, "density_gpm_ft2 must be"),
                              ({"base_area_ft2": 0}, "base_area_ft2 must be"),
                              ({"duration_min": 0}, "duration_min must be"),
                              ({"hose_gpm": None}, "hose_gpm is required"),
                              ({"area_increase": None}, "area_increase is required")):
            args = {key: value for key, value in {**good, **change}.items() if value is not None}
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, words):
                session.execute("density_area", args)
        self.assertGreater(session.execute("density_area", {**good, "hose_gpm": 0})["qd_gpm"], 0)

    def test_fp_calc_density_area_takes_the_same_checks(self):
        with self.assertRaisesRegex(ValueError, "density_gpm_ft2 must be"):
            _session().execute("fp_calc", {"op": "density_area", "inputs": {"density_gpm_ft2": 0, "base_area_ft2": 1500}})

    def test_no_density_and_no_area_runs_no_demand_and_one_blank_holds(self):
        from fpfa.workflow import validate_di

        result = _run(*_sample(density_gpm_ft2=None, base_area_ft2=None))
        self.assertNotIn("density_area", result["tools"])
        self.assertIn("dry_delivery_screen", result["tools"])
        with self.assertRaisesRegex(ValueError, "Base area is blank"):
            validate_di(_sample(base_area_ft2=None)[0])

    def test_an_assumed_density_is_labeled_and_not_for_release(self):
        from fpfa.calc_tools import ASSUMED_NOT_FOR_RELEASE

        result = _run(*_sample(), assumed={"density_gpm_ft2"})
        demand = result["tools"]["density_area"]
        self.assertEqual(demand["release_status"], ASSUMED_NOT_FOR_RELEASE)
        self.assertEqual(demand["assumed_inputs"][0]["name"], "density_gpm_ft2")
        self.assertIn("NEEDS PE REVIEW", demand["assumed_note"])
        self.assertTrue(any(ASSUMED_NOT_FOR_RELEASE in flag for flag in result["flags"]))
        # The delivery and gas-fill rows never read a demand.
        for name in (*DELIVERY, "nitrogen_gate"):
            self.assertNotIn("density", json.dumps(next(c["input"] for c in result["transcript"] if c["name"] == name)))
        with self.assertRaisesRegex(ValueError, "assumed_reason"):
            _session().execute("density_area", {"density_gpm_ft2": 0.2, "base_area_ft2": 1500, "area_increase": 0,
                                                "hose_gpm": 0, "assumed": ["density_gpm_ft2"]})

    def test_fp_calc_takes_no_elevation_as_zero_unless_it_is_passed(self):
        session = _session()
        branch = {"k": 5.6, "p_end_psi": 7, "c": 120, "segments": [{"d_in": 1.049, "length_ft": 10}]}
        with self.assertRaisesRegex(ValueError, r"segments\[1\]\.dz_ft"):
            session.execute("fp_calc", {"op": "tapered_branch", "inputs": branch})
        branch["segments"][0]["dz_ft"] = 0
        self.assertIn("nodes_detail", session.execute("fp_calc", {"op": "tapered_branch", "inputs": branch}))


class ExemptionTests(unittest.TestCase):
    """Fittings left out of the screen's own zone total take the kernel's ASSUMED allowance, never 0; near 1% is flagged."""

    def test_omitted_fittings_take_the_kernels_assumed_allowance(self):
        session = _session()
        # PR-D: the basis is the caller's (length_basis); cut lengths take the kernel's ASSUMED allowance.
        without = session.execute("dry_delivery_screen", _screen_args(trim_gal=5, length_basis="cut"))
        self.assertGreater(without["exemption_volume_gal"], without["volume_gal"] + 5)
        self.assertTrue(any("ASSUMED fittings" in flag for flag in without["exemption_assumptions"]))
        explicit_zero = session.execute("dry_delivery_screen", _screen_args(trim_gal=5, fittings_percent=0,
                                                                            length_basis="cut"))
        self.assertAlmostEqual(explicit_zero["exemption_volume_gal"], explicit_zero["volume_gal"] + 5, places=9)

    def test_a_zone_total_within_one_percent_of_the_threshold_is_flagged(self):
        session = _session()
        threshold = session.execute("dry_delivery_screen", _screen_args(zone_gal=100))["nfpa_size_threshold_gal"]
        near = session.execute("dry_delivery_screen", _screen_args(zone_gal=threshold * 1.009))
        far = session.execute("dry_delivery_screen", _screen_args(zone_gal=threshold * 1.011))
        self.assertIn("NEEDS PE REVIEW", near["near_threshold"])
        self.assertNotIn("near_threshold", far)


class UnitTests(unittest.TestCase):
    """An unmarked kPa or bar: ASSUMED gauge on a sprinkler-pressure field, refused on a gas-law field."""

    def test_unmarked_si_pressure(self):
        from fpfa import units

        with self.assertRaisesRegex(units.UnitError, "gauge or absolute"):
            units.convert(100, "kPa", "psi")
        for field in units.GAS_LAW_FIELDS:
            with self.subTest(field=field), self.assertRaisesRegex(units.UnitError, "gas-law field"):
                units.convert(2, "bar", "psi", field=field)
        out = units.convert(100, "kPa", "psi", field="p_psi")
        self.assertEqual(out["label"], "ASSUMED")
        self.assertIn("ASSUMED gauge", out["pressure_basis"])
        marked = units.convert(100, "kPa(g)", "psi", field="p_psig")
        self.assertNotIn("label", marked)
        self.assertEqual(units.convert(1, "bar", "kPa")["result"]["value"], 100.0)

    def test_k_si_is_a_display_figure(self):
        from fpfa.releasing import K_SI_SHOWN, reader_view

        out = _session().execute("fp_calc", {"op": "k_factor", "inputs": {"k": 5.6, "p_psi": 7}})
        self.assertNotIn("k_si", out)
        self.assertIn(K_SI_SHOWN, out)
        self.assertIn("not a design figure", out["k_si_note"])
        self.assertEqual(reader_view("fp_calc", {"q": 1}), {"q": 1})

    def test_the_gas_fill_names_the_larger_basis(self):
        gate = _run(*_sample())["tools"]["nitrogen_gate"]
        larger = "absolute" if gate["scfm_abs_basis"] >= gate["scfm_gauge_basis"] else "gauge"
        self.assertEqual(gate["sizing_basis"], larger)
        self.assertIn("size on the larger", gate["sizing_note"])


class ClaimCiteTests(unittest.TestCase):
    """Each claim's cite is built from named outputs; an approve-all checker carries nothing they do not hold."""

    def test_a_claim_cite_names_the_output_with_its_unit_inputs_condition_and_kernel_cite(self):
        from fpfa.claim_check import build_packet, numbered_bodies

        result = _run(*_sample())
        packet = build_packet(result)
        claims, sources = numbered_bodies(packet["claims"]), numbered_bodies(packet["sources"])
        number = next(n for n, body in claims.items() if "t_total" in body)
        source = sources[number]
        self.assertIn("Named outputs: di_trip_to_water.t_total_s = ", source)
        self.assertIn(" s.", source)
        self.assertIn("GIVEN inputs:", source)
        self.assertIn("ASSUMED inputs: t_exhaust_s 0", source)
        self.assertIn("condition: limit_basis FM, edition_status pinned", source)
        self.assertIn("kernel cite:", source)

    def test_a_large_figure_is_read_back_at_the_precision_it_was_quoted(self):
        from fpfa.claim_check import _package_source, _package_supports, named_outputs

        named = named_outputs({"tools": {"density_area": {"gallons": 120003.6}}, "transcript": []})
        source = _package_source("Duration volume 120003.6 gal", named, [])
        self.assertIn("density_area.gallons = 120003.6", source)
        self.assertTrue(_package_supports("Duration volume 120003.6 gal", source))
        self.assertFalse(_package_supports("Duration volume 120004.6 gal", source))

    def test_an_approve_all_checker_does_not_carry_a_figure_no_output_holds(self):
        from fpfa.claim_check import VERDICT_NOT, VERDICT_SUPPORTED, _from_model, build_packet, numbered_bodies

        result = _run(*_sample())
        result["narrative"] += "\nThe zone total is 912.4 gal."
        packet = build_packet(result)
        claims = numbered_bodies(packet["claims"])
        bad = next(n for n, body in claims.items() if "912.4" in body)
        source = numbered_bodies(packet["sources"])[bad]
        self.assertIn("No named output holds 1 of the claim's figures", source)
        self.assertNotIn("912.4", source)
        approve_all = "\n".join(f'{n}. Supported. Cite: "x" (looks right)' for n in claims)
        outcome = _from_model(packet, approve_all)
        verdicts = {row["n"]: row["verdict"] for row in outcome["rows"]}
        self.assertEqual(verdicts[bad], VERDICT_NOT)
        self.assertFalse(outcome["all_supported"])
        self.assertTrue(any(word == VERDICT_SUPPORTED for word in verdicts.values()))


class FaCallTests(unittest.TestCase):
    """charger_ok takes the caller's listed cap; a blank LFL holds; the starter block holds by name."""

    def test_charger_ok_holds_without_a_listed_cap(self):
        # PR-D: the HOLD is a result with one message, recorded like any calc, never a pass or a fail and never a
        # maker cap. The installed pack's charger_ok still takes a maker key, so even a usable cap holds.
        from fpfa.fa_calc import CHARGER_HOLD, run_fa_calc

        for inputs_ in ({"req_ah": 50, "maker_key": "simplex_es_ps"}, {"req_ah": 50},
                        {"req_ah": 50, "listed_charger_max_ah": 0}, {"req_ah": 50, "listed_charger_max_ah": "110"},
                        {"req_ah": 50, "listed_charger_max_ah": 110},
                        {"req_ah": 50, "listed_charger_max_ah": 110, "maker_key": "simplex_es_ps"}):
            with self.subTest(inputs=inputs_):
                out = run_fa_calc(REPO, {"module": "battery", "op": "charger_ok", "inputs": inputs_})
                self.assertEqual((out["status"], out["message"], out["charger_ok"]), ("HOLD", CHARGER_HOLD, None))

    def test_charger_ok_passes_the_cap_to_a_kernel_that_takes_it(self):
        from fpfa import fa_calc

        def charger_ok(req_ah, listed_charger_max_ah):
            return req_ah <= listed_charger_max_ah

        module = SimpleNamespace(charger_ok=charger_ok)
        self.assertIsNone(fa_calc.charger_hold(module, {"req_ah": 50, "listed_charger_max_ah": 110}))
        held = fa_calc.charger_hold(SimpleNamespace(charger_ok=lambda req_ah, maker_key: True),
                                    {"req_ah": 50, "listed_charger_max_ah": 110})
        self.assertEqual(held["message"], fa_calc.CHARGER_HOLD)
        # A maker key is never a fallback, even beside a cap and a kernel that takes it.
        self.assertIsNotNone(fa_calc.charger_hold(module, {"req_ah": 50, "listed_charger_max_ah": 110,
                                                           "maker_key": "simplex_es_ps"}))

    def test_a_blank_missing_or_zero_lfl_holds(self):
        session = _session()
        mix = {"H2": 50, "CH4": 30, "CO2": 20}
        for lfl in ({"H2": 4.0, "CH4": None, "CO2": "inert"}, {"H2": 4.0, "CO2": "inert"},
                    {"H2": 4.0, "CH4": 0, "CO2": "inert"}, {"H2": 4.0, "CH4": "", "CO2": "inert"},
                    {"H2": 4.0, "CH4": 5.0, "CO2": None}):
            with self.subTest(lfl=lfl), self.assertRaisesRegex(ValueError, "HOLD"):
                session.execute("lfl_setpoints", {"mix": mix, "lfl": lfl, "screens": []})
        out = session.execute("lfl_setpoints", {"mix": mix, "lfl": {"H2": 4.0, "CH4": 5.0, "CO2": "inert"}, "screens": []})
        self.assertGreater(out["lfl_fuel_vol_pct"], 0)

    def test_a_missing_starter_block_holds_naming_the_skill(self):
        import shutil
        import tempfile

        from fpfa import bess, sample_data

        root = Path(tempfile.mkdtemp()) / "pack"
        shutil.copytree(REPO / "calcs", root / "calcs")
        shutil.copytree(REPO / "skills", root / "skills")
        skill = root / "skills" / bess.BESS_SKILL / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("```starter", "```text"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, f"HOLD: .*{bess.BESS_SKILL}"):
            bess.run_bess_plan(root, sample_data.EXAMPLE_BESS, sample_data.EXAMPLE_BESS_BASIS)


class InputSourceTests(unittest.TestCase):
    """A value typed from a hint is GIVEN, said to be typed from it; a sample says SAMPLE, DH-2 OWNER TO CONFIRM."""

    def test_typed_from_a_hint(self):
        from fpfa import inputs

        self.assertEqual(inputs.typed_source("density_gpm_ft2", 0.20), inputs.SOURCE_TYPED_HINT)
        self.assertEqual(inputs.typed_source("density_gpm_ft2", 0.25), inputs.SOURCE_DESIGNER)
        self.assertEqual(inputs.typed_source("base_area_ft2", "3,500"), inputs.SOURCE_TYPED_HINT)
        self.assertEqual(inputs.label_for(inputs.SOURCE_TYPED_HINT), inputs.GIVEN)
        self.assertEqual(inputs.source_text(inputs.SOURCE_TYPED_HINT), "typed from form hint")

    def test_samples_say_so(self):
        from fpfa import inputs, sample_data

        self.assertEqual(inputs.source_text(inputs.SOURCE_SAMPLE), "SAMPLE data")
        self.assertIn("OWNER TO CONFIRM", inputs.source_text(inputs.SOURCE_SAMPLE_UNCONFIRMED))
        self.assertIn("dh2", sample_data.OWNER_TO_CONFIRM)


if __name__ == "__main__":
    unittest.main()
