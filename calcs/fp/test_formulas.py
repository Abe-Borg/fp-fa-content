#!/usr/bin/env python3
"""unittest for formulas.py. No pytest required.

From calcs/fp:
    python3 -m unittest test_formulas
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_CALC = Path(__file__).resolve().parent
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from formulas import (  # noqa: E402
    CalcError,
    density_area,
    hazen_williams,
    hydrant_supply,
    louver_free_area,
    pump_envelope,
    pipe_volume,
    air_fill_scfm,
)


class DensityAreaTests(unittest.TestCase):
    def test_owner_floor_density(self):
        r = density_area(
            density_gpm_ft2=0.20,
            base_area_ft2=2500,
            area_increase=0.30,
            hose_gpm=250,
        )
        self.assertAlmostEqual(r["design_area_ft2"], 3250, delta=0.5)
        self.assertAlmostEqual(r["q_spr_gpm"], 650, delta=0.5)
        self.assertAlmostEqual(r["qd_gpm"], 900, delta=0.5)

    def test_optional_gallons_labels_hose_inside_qd(self):
        r = density_area(0.20, 2500, 0.30, 250, duration_min=60)
        self.assertAlmostEqual(r["gallons"], 900 * 60, delta=0.5)
        self.assertIn("hose already inside qd", r["gallons_note"])

    def test_rejects_negative_density(self):
        with self.assertRaises(CalcError):
            density_area(density_gpm_ft2=-0.1, base_area_ft2=2500)


class HydrantTests(unittest.TestCase):
    def test_supply_900_gpm(self):
        r = hydrant_supply(ps_psi=70, ph_psi=55, qf_gpm=1600, q_gpm=900, derate=0.9)
        self.assertAlmostEqual(r["p_raw_psi"], 64.83, delta=0.02)
        self.assertAlmostEqual(r["p_derated_psi"], 58.34, delta=0.02)

    def test_supply_table_endpoints(self):
        qs = [0, 750, 900, 1000, 1125, 1500, 1600]
        r = hydrant_supply(70, 55, 1600, qs, derate=0.9)
        by_q = {row["q_gpm"]: row for row in r["rows"]}
        self.assertAlmostEqual(by_q[0]["p_raw_psi"], 70.0, delta=0.02)
        self.assertAlmostEqual(by_q[1600]["p_raw_psi"], 55.0, delta=0.02)
        self.assertAlmostEqual(by_q[1000]["p_derated_psi"], 57.34, delta=0.02)

    def test_rejects_qf_non_positive(self):
        with self.assertRaises(CalcError):
            hydrant_supply(70, 55, 0, 900)
        with self.assertRaises(CalcError):
            hydrant_supply(70, 55, -1600, 900)

    def test_rejects_negative_q(self):
        with self.assertRaises(CalcError):
            hydrant_supply(70, 55, 1600, -1)
        with self.assertRaises(CalcError):
            hydrant_supply(70, 55, 1600, [0, -10])


class PumpEnvelopeTests(unittest.TestCase):
    def test_pump_750_at_40(self):
        r = pump_envelope(
            qr_gpm=750,
            pr_psi=40,
            qd_gpm=900,
            churn_frac=1.20,
            suction_static_psi=70,
            ceiling_psi=175,
        )
        self.assertAlmostEqual(r["min_qr_fm_gpm"], 642.86, delta=0.5)
        self.assertAlmostEqual(r["qd_over_qr"], 1.20, delta=1e-6)
        self.assertAlmostEqual(r["churn_net_pref_psi"], 48, delta=0.02)
        self.assertAlmostEqual(r["churn_system_pref_psi"], 118, delta=0.02)
        self.assertAlmostEqual(r["churn_net_max_psi"], 56, delta=0.02)
        self.assertAlmostEqual(r["churn_system_max_psi"], 126, delta=0.02)
        self.assertAlmostEqual(r["p150_min_psi"], 26, delta=0.02)
        self.assertAlmostEqual(r["q150_gpm"], 1125, delta=0.5)
        self.assertTrue(r["qd_le_fm_cap"])
        self.assertTrue(r["qd_le_nfpa_cap"])
        self.assertTrue(r["churn_system_pref_le_ceiling"])
        self.assertTrue(r["churn_system_max_le_ceiling"])
        self.assertTrue(r["interpolation_applied"])
        self.assertAlmostEqual(r["p_net_qd_psi"], 34.4, delta=0.02)

    def test_100_psi_fails_ceiling(self):
        r = pump_envelope(
            qr_gpm=750,
            pr_psi=100,
            qd_gpm=900,
            churn_frac=1.20,
            suction_static_psi=70,
            ceiling_psi=175,
        )
        self.assertAlmostEqual(r["churn_system_max_psi"], 210.0, delta=0.02)
        self.assertFalse(r["churn_system_max_le_ceiling"])
        self.assertAlmostEqual(r["churn_system_pref_psi"], 190.0, delta=0.02)
        self.assertFalse(r["churn_system_pref_le_ceiling"])


class HazenWilliamsTests(unittest.TestCase):
    def test_q_zero_is_zero_loss(self):
        r = hazen_williams(q_gpm=0, c=100, d_in=6.065, length_ft=200)
        self.assertAlmostEqual(r["p_psi"], 0.0, delta=1e-12)
        self.assertAlmostEqual(r["hf_ft"], 0.0, delta=1e-12)
        self.assertAlmostEqual(r["psi_per_ft_water"], 0.4333, delta=1e-9)

    def test_doubling_length_doubles_p(self):
        a = hazen_williams(q_gpm=900, c=100, d_in=6.065, length_ft=200)
        b = hazen_williams(q_gpm=900, c=100, d_in=6.065, length_ft=400)
        self.assertAlmostEqual(b["p_psi"], 2.0 * a["p_psi"], delta=1e-9)
        self.assertGreater(a["p_psi"], 0)

    def test_hf_uses_0_4333(self):
        r = hazen_williams(q_gpm=900, c=100, d_in=6.065, length_ft=200)
        self.assertAlmostEqual(r["hf_ft"], r["p_psi"] / 0.4333, delta=1e-12)

    def test_rejects_non_positive_c_or_d(self):
        with self.assertRaises(CalcError):
            hazen_williams(900, 0, 6.065, 200)
        with self.assertRaises(CalcError):
            hazen_williams(900, 100, 0, 200)


class LouverTests(unittest.TestCase):
    def test_12000_cfm_500_fpm_45pct(self):
        r = louver_free_area(cfm=12000, face_fpm=500, free_area_pct=45)
        self.assertAlmostEqual(r["free_area_ft2"], 24.0, delta=0.02)
        self.assertAlmostEqual(r["gross_area_ft2"], 53.3333, delta=0.0001)

    def test_rejects_non_positive_and_pct_over_100(self):
        with self.assertRaises(CalcError):
            louver_free_area(0, 500, 45)
        with self.assertRaises(CalcError):
            louver_free_area(12000, 0, 45)
        with self.assertRaises(CalcError):
            louver_free_area(12000, 500, 0)
        with self.assertRaises(CalcError):
            louver_free_area(12000, 500, 101)



class VolumeFillTests(unittest.TestCase):
    def test_pipe_volume_4in(self):
        r = pipe_volume([{"d_in": 4.26, "length_ft": 60}])
        self.assertAlmostEqual(r["volume_gal"], 44.4, delta=0.1)

    def test_air_fill_viking_shortcut(self):
        r = air_fill_scfm(1000, 40, 30)
        self.assertAlmostEqual(r["scfm_gauge_basis"], 12.1, delta=0.1)
        self.assertGreater(r["scfm_abs_basis"], r["scfm_gauge_basis"])
        self.assertIn(f"Gauge-basis fill rate is {r['scfm_gauge_basis']:.2f} scfm", r["fill_bases"])
        self.assertIn(f"Absolute-basis fill rate is {r['scfm_abs_basis']:.2f} scfm", r["fill_bases"])

    def test_positive_inputs_reject_non_finite(self):
        import math
        from formulas import _as_float, _require_positive, di_trip_to_water
        for bad in ("1e309", math.inf, math.nan, "-inf"):
            with self.assertRaises(CalcError):
                _as_float("q_fill_gpm", bad)
            with self.assertRaises(CalcError):
                _require_positive("q_fill_gpm", bad)
            with self.assertRaises(CalcError):
                di_trip_to_water(100, bad)
            with self.assertRaises(CalcError):
                air_fill_scfm(100, bad, 30)
        with self.assertRaises(CalcError):
            _require_positive("q_fill_gpm", 0)
        with self.assertRaises(CalcError):
            _require_positive("q_fill_gpm", -1)

    def test_pipe_volume_rejects_empty(self):
        with self.assertRaises(CalcError):
            pipe_volume([])


class Inc5MethodOpTests(unittest.TestCase):
    def test_k_factor_density_mode_hand_check(self):
        # HAND CHECK (batch7 R5): K5.6, 0.15 gpm/ft2 x 130 ft2 = 19.5 gpm;
        # 19.5/5.6 = 3.48214; 3.48214^2 = 12.1253 psi (> 7 psi floor, so the floor does not govern).
        from formulas import k_factor
        r = k_factor(5.6, density=0.15, area_ft2=130, min_p_psi=7)
        self.assertAlmostEqual(r["q_req_gpm"], 19.5, delta=1e-9)
        self.assertAlmostEqual(r["p_psi"], 12.1253, delta=1e-3)
        self.assertFalse(r["floor_governs"])

    def test_k_factor_min_pressure_floor_governs(self):
        # K8.0, 0.10 x 100 = 10 gpm -> (10/8)^2 = 1.5625 psi < 7 -> P = 7, Q = 8*sqrt(7) = 21.166 gpm
        from formulas import k_factor
        r = k_factor(8.0, density=0.10, area_ft2=100, min_p_psi=7)
        self.assertTrue(r["floor_governs"])
        self.assertEqual(r["p_psi"], 7)
        self.assertAlmostEqual(r["q_gpm"], 21.166, delta=1e-3)
        self.assertAlmostEqual(r["q_req_gpm"], 10.0, delta=1e-9)

    def test_k_factor_si_and_mode_errors(self):
        from formulas import k_factor, CalcError
        self.assertAlmostEqual(k_factor(5.6, p_psi=7)["k_si"], 80.64, delta=1e-9)
        with self.assertRaises(CalcError):
            k_factor(5.6, p_psi=7, density=0.1, area_ft2=100)
        with self.assertRaises(CalcError):
            k_factor(5.6)
        self.assertNotIn("floor_governs", k_factor(5.6, p_psi=7))  # backward compatible

    def test_k_factor_both_ways(self):
        from formulas import k_factor
        self.assertAlmostEqual(k_factor(5.6, p_psi=7)["q_gpm"], 14.816, delta=0.01)
        self.assertAlmostEqual(k_factor(8.0, q_gpm=40)["p_psi"], 25.0, delta=1e-9)
        with self.assertRaises(CalcError):
            k_factor(5.6, p_psi=7, q_gpm=10)

    def test_tapered_branch_two_heads(self):
        from formulas import tapered_branch
        r = tapered_branch(5.6, 7.0, 100, [{"d_in": 1.049, "length_ft": 12, "head": True},
                                         {"d_in": 1.380, "length_ft": 12, "head": False}])
        # hand: q1=14.816; pf=4.52*14.816^1.85/(100^1.85*1.049^4.87)*12
        import math
        pf1 = 4.52 * 14.816**1.85 / (100**1.85 * 1.049**4.87) * 12
        q2 = 5.6 * math.sqrt(7 + pf1)
        self.assertAlmostEqual(r["q_inlet_gpm"], 14.816 + q2, delta=0.02)
        self.assertGreater(r["p_inlet_psi"], 7 + pf1)

    def test_di_trip(self):
        from formulas import di_trip_to_water
        r = di_trip_to_water(623, 1250, 0, 5, 10, 30)
        self.assertAlmostEqual(r["t_fill_s"], 29.904, delta=0.01)
        self.assertFalse(r["passes_screen"])

    def test_seismic_fp_bounds(self):
        from formulas import seismic_fp
        r = seismic_fp(1.0, 1.5, 1.0, 1.0, 1.3, 1.0, 1.5)
        self.assertAlmostEqual(r["fp"], 0.4*1.5*3.5/1.3/1.5, delta=1e-6)
        r2 = seismic_fp(1.0, 1.5, 1.0, 0.0, 1.3, 0.1, 6.0)
        self.assertAlmostEqual(r2["fp"], 0.45, delta=1e-9)

    def test_brace_load_pipe_table_hand_check(self):
        # HAND CHECK (batch7 R6): 23 lb/ft x 40 ft = 920 lb; Wp = 1.15 x 920 = 1058 lb; Fpw = 0.5 x 1058 = 529 lb.
        # NFPA 13-2025 Table 18.5.5.2, Sch40 4 in @ 35-40 ft = 850 lb -> OK; Sch40 2 in = 149 lb -> FAIL.
        from formulas import brace_load
        r = brace_load(0.5, [{"lb_per_ft": 23.0, "length_ft": 40}], pipe="sch40-4", spacing_ft=40)
        self.assertAlmostEqual(r["fpw_lb"], 529.0, delta=1e-9)
        self.assertEqual(r["pipe_fpw_max_lb"], 850); self.assertTrue(r["pipe_ok"])
        r2 = brace_load(0.5, [{"lb_per_ft": 23.0, "length_ft": 40}], pipe="sch40-2", spacing_ft=40)
        self.assertFalse(r2["pipe_ok"])
        self.assertEqual(brace_load(0.5, [{"lb_per_ft": 23.0, "length_ft": 40}], pipe="sch40-4", spacing_ft=20)["pipe_fpw_max_lb"], 1807)

    def test_brace_load_angle_divisor(self):
        from formulas import brace_load
        seg = [{"lb_per_ft": 23.0, "length_ft": 40}]
        r = brace_load(0.5, seg, listed_capacity_lb=1000, angle_deg=45)   # 1000/1.414 = 707.2 >= 529
        self.assertAlmostEqual(r["brace_cap_lb"], 707.21, delta=0.01); self.assertTrue(r["brace_ok"])
        r2 = brace_load(0.5, seg, listed_capacity_lb=1000, angle_deg=30)  # 1000/2 = 500 < 529
        self.assertFalse(r2["brace_ok"])

    def test_brace_load_guards(self):
        from formulas import brace_load, CalcError
        seg = [{"lb_per_ft": 23.0, "length_ft": 40}]
        for kw in ({"pipe": "sch40-4", "spacing_ft": 45}, {"pipe": "sch80-4", "spacing_ft": 20},
                   {"listed_capacity_lb": 1000, "angle_deg": 20}):
            with self.assertRaises(CalcError):
                brace_load(0.5, seg, **kw)
        self.assertNotIn("pipe_ok", brace_load(0.5, seg))  # backward compatible

    def test_brace_load(self):
        from formulas import brace_load
        r = brace_load(0.5, [{"lb_per_ft": 23.0, "length_ft": 40}])
        self.assertAlmostEqual(r["fpw_lb"], 0.5*1.15*920, delta=1e-6)



class Inc5AtGradeTests(unittest.TestCase):
    def test_at_grade_pump(self):
        from formulas import seismic_fp
        r = seismic_fp(1.0, 1.5, 1000, car=1.0, rpo=1.5, at_grade=True)
        # raw 0.4*1*1.5*1000*(1/1)*(1/1.5)=400; min 450 governs
        self.assertAlmostEqual(r["fp"], 450.0, places=6)
        self.assertEqual(r["r_mu_used"], 1.0)

# batch8 R17 (A1): unittest.main() moved to end of file so all classes run.


class Batch6TaperedBranchTests(unittest.TestCase):
    def test_hand_checked_three_heads(self):
        # Hand check: K5.6 end head 7 psi -> q0 = 5.6*sqrt(7) = 14.816 gpm.
        # seg1 1in (1.049) 10 ft: pf = 4.52*14.816^1.85/(100^1.85*1.049^4.87)*10 = 1.047 psi -> 8.047
        # head1 q = 5.6*sqrt(8.047) = 15.885 -> Q = 30.702
        # seg2 1.25in (1.380) 10 ft: pf = 4.52*30.70^1.85/(100^1.85*1.38^4.87)*10 = 1.060 -> 9.106
        # head2 q = 5.6*sqrt(9.106) = 16.899 -> Q = 47.601 ; seg3 to inlet, no head.
        from formulas import tapered_branch
        r = tapered_branch(5.6, 7.0, 100, [{"d_in": 1.049, "length_ft": 10},
                                         {"d_in": 1.380, "length_ft": 10},
                                         {"d_in": 1.610, "length_ft": 5, "head": False}])
        n = r["nodes"]
        self.assertAlmostEqual(n[1]["pf_psi"], 1.047, delta=0.01)
        self.assertAlmostEqual(n[1]["q_cum_gpm"], 30.70, delta=0.03)
        self.assertAlmostEqual(n[2]["p_psi"], 9.106, delta=0.02)
        self.assertAlmostEqual(n[2]["q_cum_gpm"], 47.60, delta=0.05)
        self.assertAlmostEqual(r["q_inlet_gpm"], 47.60, delta=0.05)
        self.assertTrue(r["end_head_ok"])

    def test_eq_ft_equals_added_length(self):
        from formulas import tapered_branch
        a = tapered_branch(8.0, 10, 100, [{"d_in": 1.049, "length_ft": 10, "eq_ft": 2}])
        b = tapered_branch(8.0, 10, 100, [{"d_in": 1.049, "length_ft": 12}])
        self.assertAlmostEqual(a["p_inlet_psi"], b["p_inlet_psi"], places=9)

    def test_elevation_and_k_override(self):
        from formulas import tapered_branch
        r = tapered_branch(5.6, 7, 120, [{"d_in": 1.049, "length_ft": 1, "dz_ft": 10, "k": 8.0}])
        self.assertAlmostEqual(r["nodes"][1]["pe_psi"], 4.333, delta=0.001)
        p1 = r["nodes"][1]["p_psi"]
        self.assertAlmostEqual(r["nodes"][1]["q_head_gpm"], 8.0 * p1 ** 0.5, places=9)

    def test_low_end_pressure_flag_and_rejects(self):
        from formulas import CalcError, tapered_branch
        self.assertFalse(tapered_branch(5.6, 5, 100, [{"d_in": 1.049, "length_ft": 10}])["end_head_ok"])
        with self.assertRaises(CalcError):
            tapered_branch(5.6, 7, 100, [])
        with self.assertRaises(CalcError):
            tapered_branch(5.6, 7, 100, [{"d_in": 0, "length_ft": 10}])


class Batch6DiTripTests(unittest.TestCase):
    def test_hand_checked_fm_default(self):
        # 200 gal / 800 gpm -> 15 s fill; + 5 + 10 = 30.0 s; FM 30 s -> pass at limit, margin 0.
        from formulas import di_trip_to_water
        r = di_trip_to_water(200, 800, 0, 5, 10)
        self.assertEqual(r["limit_basis"], "FM"); self.assertEqual(r["limit_s"], 30.0)
        self.assertAlmostEqual(r["t_total_s"], 30.0, places=9)
        self.assertTrue(r["passes_screen"])
        self.assertAlmostEqual(r["v_max_gal_at_limit"], 200.0, places=9)

    def test_nfpa_basis_and_explicit_override(self):
        from formulas import di_trip_to_water
        r = di_trip_to_water(623, 1250, 0, 5, 10, basis="NFPA")
        self.assertEqual(r["limit_s"], 50.0); self.assertEqual(r["limit_basis"], "NFPA-OH")
        self.assertTrue(r["passes_screen"])  # 44.9 s <= 50 s (NFPA 13-2025 Table 8.2.4.3.2, OH)
        self.assertEqual(di_trip_to_water(623, 1250, basis="NFPA-LH")["limit_s"], 60.0)
        self.assertAlmostEqual(r["t_total_s"], 44.904, delta=0.001)
        r2 = di_trip_to_water(623, 1250, 0, 5, 10, limit_s=45, basis="FM")
        self.assertEqual(r2["limit_basis"], "explicit"); self.assertTrue(r2["passes_screen"])

    def test_rejects(self):
        from formulas import CalcError, di_trip_to_water
        with self.assertRaises(CalcError):
            di_trip_to_water(0, 800)
        with self.assertRaises(CalcError):
            di_trip_to_water(200, 800, basis="UNLISTED")
        with self.assertRaises(CalcError):
            di_trip_to_water(200, 800, t_release_s=-1)


class Batch7JunctionBalanceTests(unittest.TestCase):
    """batch7 R19: NFPA 13-2025 s28.2.2.4 junction balance."""

    def test_hand_check_square_root_law(self):
        from formulas import junction_balance
        # Hand: K = 100/sqrt(16) = 25; q_adj = 25*sqrt(25) = 125; total 120+125 = 245
        r = junction_balance(100, 16, 25, q_high_gpm=120)
        self.assertAlmostEqual(r["k_equiv"], 25.0)
        self.assertAlmostEqual(r["q_low_adjusted_gpm"], 125.0)
        self.assertAlmostEqual(r["q_total_gpm"], 245.0)
        self.assertEqual(r["p_carried_psi"], 25)
        self.assertFalse(r["within_tolerance"])

    def test_within_half_psi_tolerance(self):
        from formulas import junction_balance
        r = junction_balance(150, 40.0, 40.4, q_high_gpm=160)
        self.assertTrue(r["within_tolerance"])
        self.assertAlmostEqual(r["q_low_adjusted_gpm"], 150 * (40.4 / 40.0) ** 0.5, places=2)

    def test_tolerance_edge_and_bad_inputs(self):
        from formulas import junction_balance, dispatch
        self.assertTrue(junction_balance(100, 50, 50.5)["within_tolerance"])
        self.assertFalse(junction_balance(100, 50, 50.6)["within_tolerance"])
        self.assertIn("q_total_gpm", dispatch("junction_balance",
                      {"q_low_gpm": 100, "p_low_psi": 50, "p_high_psi": 60}))
        with self.assertRaises(CalcError):
            junction_balance(100, 60, 50)
        with self.assertRaises(CalcError):
            junction_balance(100, 50, 60, q_high_gpm=-1)


class Batch8ReliefCheckTests(unittest.TestCase):
    """batch8 R4: NFPA 20-2025 s4.20.1.2 diesel main relief valve test."""

    def test_hand_check_relief_valve(self):
        from formulas import relief_check
        # Hand: 1.21*91 = 110.11; +82 = 192.11 > 175 -> relief valve required
        r = relief_check(91, 82)
        self.assertAlmostEqual(r["relief_check_psi"], 192.11)
        self.assertTrue(r["relief_valve_required"])
        self.assertAlmostEqual(r["margin_psi"], -17.11)

    def test_below_rating_no_valve_and_elevation(self):
        from formulas import relief_check
        r = relief_check(60, 50)          # 72.6 + 50 = 122.6
        self.assertAlmostEqual(r["relief_check_psi"], 122.6)
        self.assertFalse(r["relief_valve_required"])
        r2 = relief_check(91, 82, elevation_adj_psi=-20)   # 172.11 <= 175
        self.assertFalse(r2["relief_valve_required"])

    def test_edge_and_bad_inputs(self):
        from formulas import relief_check, dispatch
        # exactly at rating is not "exceeds"
        self.assertFalse(relief_check(100, 54, component_rating_psi=175)["relief_valve_required"])
        self.assertIn("relief_check_psi", dispatch("relief_check",
                      {"net_shutoff_psi": 98, "max_static_suction_psi": 82}))
        with self.assertRaises(CalcError):
            relief_check(0, 82)
        with self.assertRaises(CalcError):
            relief_check(91, -1)


class Batch8CpFromSdsTests(unittest.TestCase):
    """batch8 R5: NFPA 13-2025 s18.5.9.3 / .5."""

    def test_hand_check(self):
        from formulas import cp_from_sds
        # Hand: 0.754*0.80 = 0.6032
        r = cp_from_sds(0.80)
        self.assertAlmostEqual(r["cp"], 0.6032)
        self.assertEqual(r["height_factor"], 1.0)

    def test_default_and_height_factors(self):
        from formulas import cp_from_sds
        self.assertEqual(cp_from_sds()["cp"], 0.5)
        self.assertAlmostEqual(cp_from_sds(1.0, 0.60, True)["cp"], 0.65975, places=3)
        self.assertAlmostEqual(cp_from_sds(1.0, 0.40, True)["cp"], 0.5655, places=4)
        self.assertEqual(cp_from_sds(1.0, 0.505, True)["height_factor"], 1.0)
        self.assertEqual(cp_from_sds(1.0, 0.90, True)["height_factor"], 1.0)

    def test_bad_inputs_and_dispatch_chain(self):
        from formulas import cp_from_sds, dispatch, brace_load
        with self.assertRaises(CalcError):
            cp_from_sds(0)
        with self.assertRaises(CalcError):
            cp_from_sds(1.0, apply_height_factor=True)
        cp = dispatch("cp_from_sds", {"sds": 0.5})["cp"]
        self.assertAlmostEqual(cp, 0.377)
        r = brace_load(cp, [{"lb_per_ft": 10.0, "length_ft": 40}])
        self.assertAlmostEqual(r["fpw_lb"], 0.377 * 1.15 * 400, places=0)


import formulas as f  # noqa: E402


class Batch8HoseDurationTests(unittest.TestCase):
    def test_table_values(self):
        self.assertEqual(f.hose_duration("light")["hose_total_gpm"], 100)
        self.assertEqual(f.hose_duration("OH2")["duration_min"], 90)
        self.assertEqual(f.hose_duration("EH1", supervised=True)["duration_min"], 90)
        self.assertEqual(f.hose_duration("extra")["hose_total_gpm"], 500)

    def test_bad_hazard(self):
        with self.assertRaises(f.CalcError):
            f.hose_duration("storage")


class Batch8DryDeliveryScreenTests(unittest.TestCase):
    SEG = [{"d_in": 4.026, "length_ft": 60}, {"d_in": 2.469, "length_ft": 240}, {"d_in": 1.049, "length_ft": 480}]

    def test_chain_matches_parts(self):
        r = f.dry_delivery_screen(self.SEG, 900, t_release_s=5, t_exhaust_s=10, limit_s=30)
        v = f.pipe_volume(self.SEG)["volume_gal"]
        d = f.di_trip_to_water(v, 900, 0, 5, 10, 30)
        self.assertAlmostEqual(r["volume_gal"], v)
        self.assertAlmostEqual(r["t_total_s"], d["t_total_s"])
        self.assertTrue(r["nfpa_delivery_time_exempt"])

    def test_qod_cap(self):
        big = [{"d_in": 6.065, "length_ft": 400}]  # ~600 gal
        self.assertFalse(f.dry_delivery_screen(big, 1000)["nfpa_delivery_time_exempt"])
        self.assertTrue(f.dry_delivery_screen(big, 1000, qod=True)["nfpa_delivery_time_exempt"])

    def test_dispatch(self):
        r = f.dispatch("dry-delivery-screen", {"segments": self.SEG, "q_fill_gpm": 900})
        self.assertEqual(r["limit_basis"], "FM")


class Batch9StepReferenceTests(unittest.TestCase):
    """batch9 pre-work: run.py step references "@<step>.<key>"."""

    def _run(self, steps):
        import io, contextlib, run
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run.run_steps("t", None, steps)
        return buf.getvalue()

    def test_cp_chained_into_brace_load(self):
        out = self._run([
            {"id": "cp", "op": "cp_from_sds", "sds": 1.2},
            {"id": "br", "op": "brace_load", "cp": "@cp.cp",
             "segments": [{"lb_per_ft": 23.0, "length_ft": 40}]},
        ])
        self.assertIn("0.9048", out)
        self.assertIn("TRANSCRIPT_OK", out)

    def test_bad_reference_raises(self):
        import run
        with self.assertRaises(run.CalcError):
            self._run([{"id": "a", "op": "brace_load", "cp": "@nope.cp",
                        "segments": [{"lb_per_ft": 23.0, "length_ft": 40}]}])

    def test_bad_key_raises(self):
        import run
        with self.assertRaises(run.CalcError):
            self._run([{"id": "cp", "op": "cp_from_sds", "sds": 1.2},
                       {"id": "b", "op": "brace_load", "cp": "@cp.nokey",
                        "segments": [{"lb_per_ft": 23.0, "length_ft": 40}]}])



class Batch10DiNoQodExemptionTests(unittest.TestCase):
    """batch10 R1: DI gets NO 750 gal QOD size exemption (NFPA 13-2025 s8.3.2.3.1.1 / s8.3.2.3.2)."""
    BIG = [{"d_in": 6.065, "length_ft": 400}]  # hand check: pi/4*6.065^2/144*7.48*400 = 600.4 gal

    def test_hand_check_volume(self):
        v = f.pipe_volume(self.BIG)["volume_gal"]
        self.assertAlmostEqual(v, 3.141592653589793 / 4 * 6.065 ** 2 / 144 * 7.48 * 400, places=6)
        self.assertAlmostEqual(v, 600.4, delta=0.2)

    def test_di_with_qod_not_exempt(self):
        r = f.dry_delivery_screen(self.BIG, 1000, qod=True, system_type="di")
        self.assertEqual(r["nfpa_size_cap_gal"], 500.0)
        self.assertFalse(r["nfpa_delivery_time_exempt"])
        self.assertIn("8.3.2.3.1.1", r["nfpa_basis"])

    def test_dry_with_qod_still_750(self):
        r = f.dry_delivery_screen(self.BIG, 1000, qod=True, system_type="dry")
        self.assertEqual(r["nfpa_size_cap_gal"], 750.0)
        self.assertTrue(r["nfpa_delivery_time_exempt"])

    def test_di_small_exempt_and_alias(self):
        small = [{"d_in": 4.026, "length_ft": 60}, {"d_in": 2.469, "length_ft": 240}]
        r = f.dry_delivery_screen(small, 900, system_type="double-interlock")
        self.assertEqual(r["system_type"], "di")
        self.assertTrue(r["nfpa_delivery_time_exempt"])

    def test_rejects_single_interlock(self):
        with self.assertRaises(f.CalcError):
            f.dry_delivery_screen(self.BIG, 1000, system_type="single_interlock")

    def test_run_py_dispatch(self):
        r = f.dispatch("dry_delivery_screen", {"segments": self.BIG, "q_fill_gpm": 1000, "qod": True, "system_type": "di"})
        self.assertFalse(r["nfpa_delivery_time_exempt"])


class Batch10BraceFmOnceTests(unittest.TestCase):
    """FM horizontal listings skip the Table 18.5.2.3 angle divisor (FM factor once)."""
    SEG = [{"lb_per_ft": 16.3, "length_ft": 30}, {"lb_per_ft": 2.92, "length_ft": 54}]

    def _cp(self):
        return f.cp_from_sds(1.2, attach_height_ratio=0.4, apply_height_factor=False)["cp"]

    def test_horizontal_listing_crosscheck(self):
        r = f.brace_load(self._cp(), self.SEG, pipe="sch10-4", spacing_ft=30,
                         listed_capacity_lb=1070, angle_deg=45, capacity_is_horizontal=True)
        self.assertAlmostEqual(r["fpw_lb"], 672.8835, places=2)
        self.assertEqual(r["brace_cap_lb"], 1070.0)
        self.assertTrue(r["brace_ok"]); self.assertFalse(r["pipe_ok"])

    def test_hand_check(self):
        # hand: Cp 0.5 * 1.15 * (10 lb/ft * 40 ft) = 230 lb vs FM 300 lb used directly at 30 deg -> pass;
        # UL path at 30 deg divides by 2.0 -> 150 lb -> fail.
        fm = f.brace_load(0.5, [{"lb_per_ft": 10, "length_ft": 40}], listed_capacity_lb=300, angle_deg=30,
                          capacity_is_horizontal=True)
        ul = f.brace_load(0.5, [{"lb_per_ft": 10, "length_ft": 40}], listed_capacity_lb=300, angle_deg=30)
        self.assertAlmostEqual(fm["fpw_lb"], 230.0)
        self.assertTrue(fm["brace_ok"]); self.assertEqual(fm["angle_divisor"], 1.0)
        self.assertFalse(ul["brace_ok"]); self.assertEqual(ul["angle_divisor"], 2.0)

    def test_default_unchanged(self):
        r = f.brace_load(self._cp(), self.SEG, listed_capacity_lb=1070, angle_deg=45)
        self.assertAlmostEqual(r["brace_cap_lb"], 1070 / 1.414)
        self.assertFalse(r["capacity_is_horizontal"])

    def test_spacing_passthrough(self):
        cp = self._cp()
        a = f.brace_spacing_max(cp, "sch40-4", 16.3, listed_capacity_lb=1070, angle_deg=45, capacity_is_horizontal=True)
        self.assertEqual(a["brace_cap_lb"], 1070.0)

    def test_angle_range_still_enforced(self):
        with self.assertRaises(f.CalcError):
            f.brace_load(0.5, self.SEG, listed_capacity_lb=1070, angle_deg=20, capacity_is_horizontal=True)


class Batch10DieselDerateTests(unittest.TestCase):
    """NFPA 20-2025 s11.2.2.4/.5 additive derate (design practice)."""

    def test_high_altitude_58_1(self):
        r = f.diesel_derate(46.9, 5280, 120)
        self.assertAlmostEqual(r["alt_deduction_pct"], 14.94, places=2)
        self.assertAlmostEqual(r["temp_deduction_pct"], 4.3, places=6)
        self.assertAlmostEqual(r["required_engine_hp"], 58.07, delta=0.01)
        self.assertEqual(round(r["required_engine_hp"], 1), 58.1)

    def test_hand_check_round_numbers(self):
        # hand: 1,300 ft -> 3 %; 97 F -> 2 %; additive 5 % -> 95 / 0.95 = 100 hp
        r = f.diesel_derate(95, 1300, 97)
        self.assertAlmostEqual(r["total_deduction_pct"], 5.0)
        self.assertAlmostEqual(r["required_engine_hp"], 100.0)

    def test_additive_exceeds_multiplicative(self):
        r = f.diesel_derate(46.9, 5280, 120)
        mult = 46.9 / ((1 - 0.1494) * (1 - 0.043))
        self.assertGreater(r["required_engine_hp"], mult)

    def test_no_derate_below_thresholds(self):
        self.assertAlmostEqual(f.diesel_derate(50, 250, 70)["required_engine_hp"], 50.0)
        self.assertAlmostEqual(f.diesel_derate(46.9, 50, 120)["required_engine_hp"], 49.01, delta=0.01)

    def test_stepwise_and_nameplate(self):
        r = f.diesel_derate(46.9, 5280, 120, nameplate_hp=50, stepwise=True)
        self.assertAlmostEqual(r["total_deduction_pct"], 3 * 4 + 4)  # 4 whole 1,000 ft steps, 4 whole 10 F steps
        self.assertFalse(r["engine_ok"]); self.assertGreater(r["deficit_hp"], 0)

    def test_bad_and_dispatch(self):
        with self.assertRaises(f.CalcError):
            f.diesel_derate(0, 5280, 120)
        self.assertIn("required_engine_hp", f.dispatch("diesel-derate", {"pump_bhp": 46.9, "altitude_ft": 5280, "ambient_f": 120}))

if __name__ == "__main__":
    unittest.main()


class Batch9CompressorN2Tests(unittest.TestCase):
    SYS = [{"id": "DI-1", "v_gal": 750, "p_psig": 40}, {"id": "DI-2", "v_gal": 500, "p_psig": 40},
           {"id": "DRY-3", "v_gal": 300, "p_psig": 30}]

    def test_compressor_on_largest(self):
        from formulas import compressor_n2_sizing
        r = compressor_n2_sizing(self.SYS, 30)
        self.assertEqual(r["largest_system_id"], "DI-1")
        self.assertAlmostEqual(r["compressor_scfm_gauge"], 750*40/(7.48*14.7*30), places=6)
        self.assertGreater(r["compressor_scfm_abs"], r["compressor_scfm_gauge"])
        self.assertIn(
            f"Compressor gauge-basis fill rate is {r['compressor_scfm_gauge']:.2f} scfm",
            r["fill_bases"],
        )
        self.assertIn(
            f"Compressor absolute-basis fill rate is {r['compressor_scfm_abs']:.2f} scfm",
            r["fill_bases"],
        )

    def test_n2_on_campus_total(self):
        from formulas import compressor_n2_sizing
        r = compressor_n2_sizing(self.SYS, 30)
        exp = (750*40 + 500*40 + 300*30)/(7.48*14.7*30)
        self.assertAlmostEqual(r["n2_campus_scfm_gauge"], exp, places=6)
        self.assertGreater(r["n2_campus_scfm_abs"], r["n2_campus_scfm_gauge"])
        self.assertEqual(r["connected_v_gal"], 1550)

    def test_rejects_empty(self):
        from formulas import compressor_n2_sizing
        with self.assertRaises(Exception):
            compressor_n2_sizing([], 30)

    def test_run_py_dispatch(self):
        from formulas import dispatch
        r = dispatch("compressor_n2_sizing", {"systems": self.SYS, "t_min": 30})
        self.assertIn("NFPA 13-2025 s8.2.7.3", r["basis"])


class Batch9BraceSpacingTests(unittest.TestCase):
    """batch9 R13: brace_spacing_max, cross-checked vs brace_load at 30 ft (batch8 R14 672.88 lb)."""
    def test_matches_brace_load_at_30(self):
        from formulas import brace_spacing_max, brace_load
        r = brace_spacing_max(0.9048, "sch40-4", 16.3, 2.92 * 54 / 30)
        b = brace_load(0.9048, [{"lb_per_ft": 16.3, "length_ft": 30}, {"lb_per_ft": 2.92, "length_ft": 54}])
        self.assertIn("Fpw=%.1f" % b["fpw_lb"], r["rows"][2])
        self.assertEqual(r["max_spacing_ft"], 35)
    def test_sch10_limited_to_25(self):
        from formulas import brace_spacing_max
        self.assertEqual(brace_spacing_max(0.9048, "sch10-4", 16.3, 5.256)["max_spacing_ft"], 25)
    def test_none_pass(self):
        from formulas import brace_spacing_max
        r = brace_spacing_max(0.9048, "sch40-2", 50.0)
        self.assertFalse(r["any_pass"]); self.assertEqual(r["max_spacing_ft"], 0)
    def test_bad_pipe(self):
        from formulas import brace_spacing_max, CalcError
        with self.assertRaises(CalcError):
            brace_spacing_max(0.9, "sch5-4", 10)
