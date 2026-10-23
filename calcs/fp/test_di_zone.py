"""Tests for the double-interlock screens in di_zone.py."""

from __future__ import annotations

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
        self.assertIn("low_air", table["boolean"])


class NitrogenAndScreenTests(unittest.TestCase):
    def test_design_c_is_100(self):
        out = di_zone.nitrogen_gate(281.3, 40, 30)
        self.assertEqual(out["design_c"], 100)
        self.assertGreater(out["friction_ratio_c100_vs_c120"], 0.70)
        self.assertLess(out["friction_ratio_c100_vs_c120"], 0.73)
        fill = di_zone.formulas.air_fill_scfm(281.3, 40, 30)
        self.assertAlmostEqual(out["scfm_gauge_basis"], fill["scfm_gauge_basis"], places=6)

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
