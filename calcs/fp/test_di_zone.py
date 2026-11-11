"""Tests for the double-interlock screens in di_zone.py."""

from __future__ import annotations

import inspect
import unittest

import di_zone


class VolumeTests(unittest.TestCase):
    def test_trim_adds_to_pipe_volume(self):
        segments = [
            {"nps": "1", "schedule": "sch40", "role": "branch", "length_ft": 900},
            {"nps": "4", "schedule": "sch10", "role": "cross", "length_ft": 160},
        ]
        out = di_zone.zone_trapped_volume(segments, length_basis="center_to_center")
        pipe = di_zone.formulas.pipe_volume([
            {"d_in": 1.049, "length_ft": 900},
            {"d_in": 4.260, "length_ft": 160},
        ])
        self.assertAlmostEqual(out["pipe_gal"], pipe["volume_gal"], places=6)
        self.assertAlmostEqual(out["zone_gal"], pipe["volume_gal"] + 5.0, places=6)
        self.assertTrue(out["trim_assumed"])
        self.assertEqual(out["fittings_percent"], 0.0)

    def test_cut_lengths_use_five_percent(self):
        out = di_zone.zone_trapped_volume(
            [{"d_in": 4.026, "length_ft": 100}],
            length_basis="cut",
            trim_gal=0,
        )
        self.assertAlmostEqual(out["zone_gal"], out["pipe_gal"] * 1.05, places=6)

    def test_shop_id_branch_versus_main(self):
        branch = di_zone.pipe_ids.resolve(2, None, "branch")
        main = di_zone.pipe_ids.resolve(2, None, "main")
        self.assertEqual(branch["schedule"], "sch40")
        self.assertEqual(branch["d_in"], 2.067)
        self.assertEqual(main["schedule"], "sch10")
        self.assertEqual(main["d_in"], 2.157)


class TrimAndReleaseTests(unittest.TestCase):
    def test_electric_family_and_actuator_collision(self):
        ok = di_zone.elect_di_trim("double-interlock", prime_held_by="nc_solenoid",
                                   supervisory_psi=15, medium="nitrogen", insurer="FM")
        self.assertEqual(ok["family"], "El/El")
        self.assertEqual(ok["status"], "provisional")
        self.assertTrue(ok["controlling"])
        bad = di_zone.elect_di_trim("di", prime_held_by="nc_solenoid", supervisory_psi=30)
        self.assertTrue(any("Collision" in flag for flag in bad["flags"]))

    def test_unknown_prime_does_not_default(self):
        out = di_zone.elect_di_trim("di", prime_held_by="unknown")
        self.assertEqual(out["status"], "unresolved")
        self.assertIsNone(out["family"])

    def test_failsafe_and_out_of_scope(self):
        fail = di_zone.elect_di_trim("di", failsafe_on_total_power_loss=True, prime_held_by="nc_solenoid")
        self.assertEqual(fail["family"], "named-failsafe")
        stop = di_zone.elect_di_trim("single-interlock")
        self.assertEqual(stop["status"], "RFI-variance")
        self.assertFalse(stop["controlling"])
        self.assertEqual(di_zone.elect_di_trim("foam")["family"], None)
        self.assertEqual(di_zone.elect_di_trim("wet")["status"], "N/A")

    def test_second_smoke_does_not_change_solenoid(self):
        table = di_zone.releasing_truth_table(manual_station=True, insurer="FM")
        self.assertEqual(table["row_count"], 32)
        self.assertEqual(table["solenoid_true_count"], 6)
        self.assertTrue(table["fm_no_cross_zone"])
        self.assertNotIn("low_air", table["boolean"])
        self.assertEqual(table["boolean"], table["boolean_p"])


class SecondLegLabelTests(unittest.TestCase):
    """The second DI leg is P, the pressure drop from sprinkler operation.

    Low air is supervisory only and is never a release input. No output of the
    truth table carries a ``low_air`` key or a ``low_air`` term in any string.
    """

    def setUp(self):
        self.table = di_zone.releasing_truth_table(manual_station=True, insurer="FM")

    def test_no_row_carries_a_low_air_key_and_p_second_leg_is_on_every_row(self):
        self.assertEqual(self.table["row_count"], 32)
        for name in ("rows", "rows_without_second_smoke"):
            self.assertTrue(self.table[name])
            for row in self.table[name]:
                self.assertIn("p_second_leg", row)
                self.assertNotIn("low_air", row)

    def test_no_key_at_any_depth_and_no_string_names_low_air(self):
        import json

        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield str(key)
                    yield from keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from keys(item)

        for key in keys(self.table):
            self.assertNotIn("low_air", key.lower(), key)
        for key in ("low_air_note", "deprecated"):
            self.assertNotIn(key, self.table)
        text = json.dumps(self.table)
        self.assertNotIn("low_air", text.lower())
        self.assertNotIn("AND low_air", text)
        self.assertNotIn("low air", text.lower())

    def test_boolean_structure_and_counts_unchanged(self):
        self.assertEqual(self.table["solenoid_true_count"], 6)
        for row in self.table["rows"]:
            det_leg = row["detection"] or row["manual"]
            self.assertEqual(row["solenoid"], bool(det_leg and row["p_second_leg"] and not row["isolated"]))
        before = [(r["detection"], r["manual"], r["isolated"], r["second_smoke"], r["solenoid"])
                  for r in self.table["rows"] if r["p_second_leg"]]
        self.assertEqual(len(before), 16)
        no_manual = di_zone.releasing_truth_table(manual_station=False)
        self.assertEqual(no_manual["solenoid_true_count"], 4)

    def test_p_boolean_label_names_p_not_low_air(self):
        label = self.table["boolean_p"]
        self.assertEqual(label, "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated")
        self.assertNotIn("low", label.lower())

    def test_p_is_defined_as_sprinkler_operation_pressure_drop(self):
        text = self.table["second_leg"].lower()
        self.assertIn("pressure drop", text)
        self.assertIn("sprinkler operation", text)
        self.assertIn("psl-rel", text)
        self.assertIn("pa-rel", text)

    def test_the_docstring_keeps_low_air_supervisory_and_names_no_alias(self):
        doc = di_zone.releasing_truth_table.__doc__.lower()
        self.assertIn("low air is supervisory only (psl-sup)", doc)
        self.assertNotIn("low_air", doc)
        self.assertNotIn("alias", doc)

    def test_no_new_text_names_low_air_as_a_release_input(self):
        import re
        fields = [self.table["boolean"], self.table["boolean_p"], self.table["second_leg"],
                  self.table["detection_leg"], self.table["second_smoke"], self.table["abort"]]
        for text in fields:
            for sentence in re.split(r"(?<=[.;])\s+", text):
                low = sentence.lower()
                if "low air" in low or "low_air" in low:
                    self.assertIn("supervisory", low, sentence)
                    self.assertNotRegex(low, r"and low[ _]air|low[ _]air (releases|opens|leg)", sentence)
        src = inspect.getsource(di_zone.releasing_truth_table).lower()
        self.assertNotIn("and low air", src)
        doc = di_zone.releasing_truth_table.__doc__.lower()
        self.assertIn("p_second_leg", doc)
        self.assertIn("supervisory", doc)
        self.assertIn("not a release input", doc)

    def test_detection_leg_label_says_manual_is_inside_d_and_needs_p(self):
        label = self.table["detection_leg"]
        self.assertIn("manual_release is a station inside D (still needs P).", label)
        self.assertIn("A panel zone typed Manual Release that bypasses the AND is not modeled "
                      "and is never a default (C&E skill footnote \u2079 election).", label)
        self.assertTrue(label.startswith("one detection zone, or a manual station in place of that zone"))

    def test_boolean_string_is_the_p_form_and_never_says_low_air(self):
        expected = "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated"
        self.assertEqual(self.table["boolean"], expected)
        self.assertEqual(self.table["boolean"], self.table["boolean_p"])
        self.assertNotIn("low_air", self.table["boolean"])
        self.assertNotIn("deprecated", self.table)


class ElectricElectricScopeTests(unittest.TestCase):
    """The solenoid truth table states electric/electric trim only.

    P in this table is the sprinkler-operation pressure drop sensed by PSL-REL.
    On electric/pneumatic trim the solenoid is D AND not isolated, and PA-REL
    gates the valve mechanically, outside this table.
    """

    def setUp(self):
        self.table = di_zone.releasing_truth_table(manual_station=True, insurer="FM")
        self.doc = di_zone.releasing_truth_table.__doc__

    def _sentences(self, text: str) -> list[str]:
        import re
        return [part.strip() for part in re.split(r"(?<=[.])\s+", text.strip()) if part.strip()]

    def test_scope_label_and_second_leg_name_electric_electric_and_psl_rel(self):
        for text in (self.doc, self.table["second_leg"]):
            low = text.lower()
            self.assertIn("this solenoid truth table is electric/electric trim", low)
            self.assertIn("pressure drop from sprinkler operation", low)
            self.assertIn("sensed by psl-rel", low)
            self.assertIn("on electric/pneumatic trim the solenoid is d and not isolated", low)
            self.assertIn(
                "the valve actuator pa-rel gates the valve mechanically, which is outside this table",
                low,
            )

    def test_second_leg_does_not_present_pa_rel_as_p_second_leg(self):
        sentences = self._sentences(self.table["second_leg"])
        defining = [sentence for sentence in sentences if "p_second_leg" in sentence]
        self.assertTrue(defining)
        for sentence in defining:
            self.assertNotIn("PA-REL", sentence)
            self.assertIn("PSL-REL", sentence)
        outside = [sentence for sentence in sentences if "PA-REL" in sentence]
        self.assertTrue(outside)
        for sentence in outside:
            self.assertNotIn("p_second_leg", sentence)
            self.assertIn("outside this table", sentence)
            self.assertIn("mechanically", sentence)
        self.assertNotIn("or the listed pneumatic actuator", self.table["second_leg"])
        doc_low = self.doc.lower()
        self.assertNotIn("it is the listed pneumatic actuator", doc_low)
        for sentence in self._sentences(self.doc):
            if "p_second_leg" in sentence:
                self.assertNotIn("PA-REL", sentence)

    def test_boolean_strings_row_structure_and_solenoid_count_unchanged(self):
        self.assertEqual(
            self.table["boolean_p"],
            "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated",
        )
        self.assertEqual(self.table["boolean"], self.table["boolean_p"])
        self.assertEqual(self.table["row_count"], 32)
        self.assertEqual(self.table["solenoid_true_count"], 6)
        keys = ("detection", "manual", "p_second_leg", "isolated", "second_smoke", "solenoid")
        fires = 0
        for row in self.table["rows"]:
            self.assertEqual(tuple(row), keys)
            det_leg = row["detection"] or row["manual"]
            expected = bool(det_leg and row["p_second_leg"] and not row["isolated"])
            self.assertEqual(row["solenoid"], expected)
            fires += int(expected)
        self.assertEqual(fires, 6)
        self.assertEqual(len(self.table["rows"]), 32)


class NitrogenAndScreenTests(unittest.TestCase):
    def test_design_c_is_100(self):
        out = di_zone.nitrogen_gate(281.3, 40, 30)
        self.assertEqual(out["design_c"], 100)
        self.assertGreater(out["friction_ratio_c100_vs_c120"], 0.70)
        self.assertLess(out["friction_ratio_c100_vs_c120"], 0.73)
        fill = di_zone.formulas.air_fill_scfm(281.3, 40, 30)
        self.assertAlmostEqual(out["scfm_gauge_basis"], fill["scfm_gauge_basis"], places=6)
        self.assertAlmostEqual(out["scfm_abs_basis"], fill["scfm_abs_basis"], places=6)
        self.assertGreater(out["scfm_abs_basis"], out["scfm_gauge_basis"])
        self.assertIn(f"{out['scfm_gauge_basis']:.2f}", out["fill_bases"])
        self.assertIn(f"{out['scfm_abs_basis']:.2f}", out["fill_bases"])
        self.assertIn("Gauge-basis", out["fill_bases"])
        self.assertIn("Absolute-basis", out["fill_bases"])

    def test_example_zone_misses_fm_30s_and_stays_under_500(self):
        segments = [
            {"d_in": 1.049, "length_ft": 900},
            {"d_in": 2.067, "length_ft": 220},
            {"d_in": 4.260, "length_ft": 160},
            {"d_in": 6.357, "length_ft": 48},
        ]
        zone = di_zone.zone_trapped_volume(segments, trim_gal=5, fittings_percent=0)
        screen = di_zone.formulas.dry_delivery_screen(
            segments, q_fill_gpm=600, qod=True, t_detect_s=8, t_release_s=2,
            system_type="di", basis="FM",
        )
        trip = di_zone.formulas.di_trip_to_water(
            zone["zone_gal"], 600, t_detect_s=8, t_release_s=2, basis="FM",
        )
        self.assertLess(zone["zone_gal"], 500)
        self.assertTrue(screen["nfpa_delivery_time_exempt"])
        self.assertEqual(screen["nfpa_size_cap_gal"], 500)
        self.assertFalse(screen["passes_screen"])
        self.assertFalse(trip["passes_screen"])
        self.assertGreater(trip["t_total_s"], 30)


if __name__ == "__main__":
    unittest.main()
