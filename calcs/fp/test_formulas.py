#!/usr/bin/env python3
"""unittest for _calc/formulas.py. No pytest required.

Run from repo root:
    python3 -m unittest _calc/test_formulas.py
or from _calc:
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
    def test_owner_floor(self):
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
    def test_owner_900_gpm(self):
        r = hydrant_supply(ps_psi=70, ph_psi=55, qf_gpm=1600, q_gpm=900, derate=0.9)
        self.assertAlmostEqual(r["p_raw_psi"], 64.83, delta=0.02)
        self.assertAlmostEqual(r["p_derated_psi"], 58.34, delta=0.02)

    def test_owner_table_endpoints(self):
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
    def test_owner_750_40(self):
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

    def test_pipe_volume_rejects_empty(self):
        with self.assertRaises(CalcError):
            pipe_volume([])


class Inc5MethodOpTests(unittest.TestCase):
    def test_k_factor_density_mode_hand_check(self):
        # HAND CHECK: K5.6, 0.15 gpm/ft2 x 130 ft2 = 19.5 gpm;
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
        # HAND CHECK: 23 lb/ft x 40 ft = 920 lb; Wp = 1.15 x 920 = 1058 lb; Fpw = 0.5 x 1058 = 529 lb.
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

# unittest.main() moved to end of file so all classes run.


class TaperedBranchTests(unittest.TestCase):
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


class DiTripTests(unittest.TestCase):
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
            di_trip_to_water(200, 800, basis="UNKNOWN")
        with self.assertRaises(CalcError):
            di_trip_to_water(200, 800, t_release_s=-1)


class JunctionBalanceTests(unittest.TestCase):
    """NFPA 13-2025 s28.2.2.4 junction balance."""

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


class ReliefCheckTests(unittest.TestCase):
    """NFPA 20-2025 s4.20.1.2 diesel main relief valve test."""

    def test_hand_check_mrv(self):
        from formulas import relief_check
        # Hand: 1.21*91 = 110.11; +82 = 192.11 > 175 -> MRV required
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


class CpFromSdsTests(unittest.TestCase):
    """NFPA 13-2025 s18.5.9.3 / .5."""

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


import formulas  # noqa: E402
f = formulas  # legacy alias used by older suites


class HoseDurationTests(unittest.TestCase):
    def test_table_values(self):
        self.assertEqual(f.hose_duration("light")["hose_total_gpm"], 100)
        self.assertEqual(f.hose_duration("OH2")["duration_min"], 90)
        self.assertEqual(f.hose_duration("EH1", supervised=True)["duration_min"], 90)
        self.assertEqual(f.hose_duration("extra")["hose_total_gpm"], 500)

    def test_bad_hazard(self):
        with self.assertRaises(f.CalcError):
            f.hose_duration("storage")


class DryDeliveryScreenTests(unittest.TestCase):
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


class StepReferenceTests(unittest.TestCase):
    """run.py step references "@<step>.<key>"."""

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



class DiNoQodExemptionTests(unittest.TestCase):
    """DI gets NO 750 gal QOD size exemption (NFPA 13-2025 s8.3.2.3.1.1 / s8.3.2.3.2)."""
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


class BraceFmOnceTests(unittest.TestCase):
    """FM horizontal listings skip the Table 18.5.2.3 angle divisor (FM factor once)."""
    SEG = [{"lb_per_ft": 16.3, "length_ft": 30}, {"lb_per_ft": 2.92, "length_ft": 54}]

    def _cp(self):
        return f.cp_from_sds(1.2, attach_height_ratio=0.4, apply_height_factor=False)["cp"]

    def test_crosscheck_design_practice(self):
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


class DieselDerateTests(unittest.TestCase):
    """NFPA 20-2025 s11.2.2.4/.5 additive derate (design practice ruling)."""

    def test_derate_58_1(self):
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

    def test_no_derate_below_thresholds_cool_site(self):
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

class ElectricOverpressureTests(unittest.TestCase):
    """NFPA 20-2025 s4.7.7.1/.2/.3.1/.3.2 electric_overpressure."""

    def test_hand_check_actual_static(self):
        # hand: 1,000 gpm @ 40 psi pump, churn 56 psi (140 % of 40) + 95 static = 151 <= 175 -> OK, margin 24
        r = f.electric_overpressure(56, 95, 175)
        self.assertAlmostEqual(r["churn_max_psi"], 151.0)
        self.assertAlmostEqual(r["churn_margin_psi"], 24.0)
        self.assertTrue(r["churn_ok_4771"]); self.assertTrue(r["compliant"])

    def test_fail_relief_not_credited(self):
        r = f.electric_overpressure(120, 70, 175, relief_credited=True)
        self.assertAlmostEqual(r["churn_max_psi"], 190.0)
        self.assertFalse(r["churn_ok_4771"]); self.assertFalse(r["compliant"])
        self.assertIn("relief/PRV not permitted", r["compliance_path"])

    def test_elevation_below_pump_adds_pressure(self):
        # component 20 ft below discharge: +8.666 psi
        r = f.electric_overpressure(100, 60, 175, elevation_ft=-20)
        self.assertAlmostEqual(r["churn_max_psi"], 168.666, places=3)
        self.assertTrue(r["compliant"])

    def test_vsp_path(self):
        r = f.electric_overpressure(120, 70, 175, vs_set_psi=150, vs_variance_psi=10)
        self.assertFalse(r["churn_ok_4771"]); self.assertTrue(r["vs_ok_47732"])
        self.assertAlmostEqual(r["vs_max_psi"], 160.0)
        self.assertTrue(r["compliant"]); self.assertIn("variable speed", r["compliance_path"])

    def test_bad_input(self):
        with self.assertRaises(f.CalcError):
            f.electric_overpressure(-1, 60)


class RatedPressureSelectTests(unittest.TestCase):
    def test_hand_checked(self):
        # Hand: q=600, qr=500 -> 120% rated, rated-150 seg: f = 1 + (0.65-1)*(100/250) = 1 - 0.14 = 0.86
        # floor = 86 / 0.86 = 100.000 psi; candidates [90,105,120] -> 105; envelope at 600 @105 = 105*0.86 = 90.3 >= 86
        r = formulas.rated_pressure_select(600, 86, 500, pr_candidates_psi=[120, 90, 105])
        self.assertAlmostEqual(r["envelope_factor"], 0.86)
        self.assertAlmostEqual(r["rated_pressure_floor_psi"], 100.0)
        self.assertEqual(r["selected_pr_psi"], 105.0)
        self.assertAlmostEqual(r["candidates"][0]["p_net_at_q_check_psi"], 90.3)
        self.assertTrue(r["meets_demand"])

    def test_multi_qr_best_and_beyond(self):
        r = formulas.rated_pressure_select(750, 65, [400, 500, 750])
        c = {x["qr_gpm"]: x for x in r["candidates"]}
        self.assertFalse(c[400.0]["feasible"])            # 187.5% > 150%
        self.assertAlmostEqual(c[500.0]["rated_pressure_floor_psi"], 100.0)
        self.assertAlmostEqual(c[750.0]["rated_pressure_floor_psi"], 65.0)
        self.assertEqual(r["best"]["qr_gpm"], 750.0)
        # consistency with bor_demand_pressure floor
        b = formulas.bor_demand_pressure(750, 65, 100, qr_gpm=500)
        self.assertAlmostEqual(b["rated_pressure_floor_psi"], c[500.0]["rated_pressure_floor_psi"])

    def test_churn_roundtrip_and_bad(self):
        r = formulas.rated_pressure_select(250, 55, 500, churn_frac=1.2)  # f = 1.2-0.2*0.5 = 1.1 -> 50
        self.assertAlmostEqual(r["rated_pressure_floor_psi"], 50.0)
        self.assertAlmostEqual(r["candidates"][0]["p_net_at_q_check_psi"], 55.0)
        for kw in ({"churn_frac": 1.5}, {"p150_frac": 0.6}, {"pr_candidates_psi": []}):
            with self.assertRaises(formulas.CalcError):
                formulas.rated_pressure_select(500, 60, 500, **kw)
        with self.assertRaises(formulas.CalcError):
            formulas.rated_pressure_select(0, 60, 500)
        r = formulas.rated_pressure_select(500, 60, 500, pr_candidates_psi=[40, 50])
        self.assertFalse(r["feasible"])

    def test_dispatch_alias(self):
        r = formulas.dispatch("pump_rated_pressure", {"q_demand_gpm": 500, "p_net_demand_psi": 60, "qr_gpm": 500})
        self.assertAlmostEqual(r["rated_pressure_floor_psi"], 60.0)


class AirSetpointStackTests(unittest.TestCase):
    def test_hand_checked_b28r4_stack(self):
        # Hand : trip 11 +2 tol -> T_worst 13; L 18 -> 5 >= 5; P 23 - L = 5; H 28 - 23 = 5;
        # P - M(16) = 7; cap 30 - 28 = 2; cut-in 26 > 23; 26 >= 16.  All pass.
        r = formulas.air_setpoint_stack(23, 11, 18, high_air_switch_psig=28, trip_tol_psi=2, table_a_min_psig=16,
                                        max_pneumatic_psig=30, pmd_cut_in_psig=26, pmd_cut_out_psig=32,
                                        held=["system_air_psig", "trip_psig", "trip_tol_psi", "max_pneumatic_psig"])
        b = {x["band"]: x for x in r["bands"]}
        self.assertEqual(r["t_worst_psi"], 13.0)
        self.assertAlmostEqual(b["low_air - T_worst"]["value_psi"], 5.0)
        self.assertAlmostEqual(b["high_air - system"]["value_psi"], 5.0)
        self.assertAlmostEqual(b["system - Table A min"]["value_psi"], 7.0)
        self.assertTrue(r["all_pass"]); self.assertEqual(r["tags"]["low_air_switch_psig"], "ASSUMED")
        self.assertEqual(r["tags"]["trip_psig"], "HELD"); self.assertTrue(any("cut-out 32.0 > cap" in n for n in r["notes"]))

    def test_neg3_rrma_direct(self):
        # RRMA 20/26 direct, low-air 20, maintain 26, high 31 > cap 30
        r = formulas.air_setpoint_stack(26, 11, 20, high_air_switch_psig=31, trip_tol_psi=2, max_pneumatic_psig=30,
                                        pmd_cut_in_psig=20, pmd_cut_out_psig=26)
        b = {x["band"]: x for x in r["bands"]}
        self.assertFalse(b["cut_in - system"]["pass"]); self.assertFalse(b["cap - high_air"]["pass"])
        self.assertFalse(r["all_pass"]); self.assertFalse(r["maker_pass"])

    def test_low_water_row_needs_pe(self):
        # 505 50-psi row: trip 7 +2 = 9, min 12, cap 16; L 12, P 15, H 16 -> code margins 3 / 1 fail, maker ok
        r = formulas.air_setpoint_stack(15, 7, 12, high_air_switch_psig=16, trip_tol_psi=2, table_a_min_psig=12,
                                        max_pneumatic_psig=16)
        self.assertFalse(r["code_pass"]); self.assertTrue(r["maker_pass"]); self.assertTrue(r["needs_pe"])
        self.assertTrue(any("NEEDS PE" in n for n in r["notes"]))
        r2 = formulas.air_setpoint_stack(23, 11, 18, release_psig=15)  # release governs T_worst
        self.assertEqual(r2["t_worst_psi"], 15.0); self.assertFalse(r2["code_pass"])

    def test_rejects_nonsense(self):
        for a, kw in (((23, 25, 18), {}), ((23, 11, -1), {}), ((23, 11, 18), {"pmd_cut_in_psig": 26}),
                      ((23, 11, 18), {"pmd_cut_in_psig": 26, "pmd_cut_out_psig": 26}),
                      ((23, 11, 18), {"table_a_min_psig": 20, "max_pneumatic_psig": 16}), (("x", 11, 18), {})):
            with self.assertRaises(formulas.CalcError):
                formulas.air_setpoint_stack(*a, **kw)

    def test_dispatch_alias(self):
        r = formulas.dispatch("pmd_margin_stack", {"system_air_psig": 23, "trip_psig": 13, "low_air_switch_psig": 18})
        self.assertTrue(r["code_pass"])



class ReliefEditionTests(unittest.TestCase):
    """relief_check edition gate (NFPA 20-2016 s4.19.1.2 vs 2025 s4.20.1.2)."""

    def test_hand_check_pr65_2016(self):
        # hand: 1.21*91 = 110.11; +75 static = 185.11 > 175 -> required
        from formulas import relief_check
        r = relief_check(91, 75, edition=2016)
        self.assertAlmostEqual(r["relief_check_psi"], 185.11)
        self.assertTrue(r["relief_valve_required"])
        self.assertIn("NFPA 20-2016 s4.19.1.2", r["basis"])
        self.assertIn("verify with engineer of record", r["basis"])

    def test_pr75_2016(self):
        from formulas import relief_check
        r = relief_check(105, 75, edition="2016")   # 127.05 + 75 = 202.05
        self.assertAlmostEqual(r["relief_check_psi"], 202.05)
        self.assertTrue(r["relief_valve_required"])
        self.assertAlmostEqual(r["margin_psi"], -27.05)

    def test_default_2025_unchanged_and_bad_edition(self):
        from formulas import relief_check, CalcError
        r = relief_check(91, 82)
        self.assertEqual(r["basis"], "NFPA 20-2025 s4.20.1.2 (diesel)")
        self.assertEqual(r["relief_check_psi"], relief_check(91, 82, edition=2016)["relief_check_psi"])
        with self.assertRaises(CalcError):
            relief_check(91, 82, edition=2019)
        with self.assertRaises(CalcError):
            relief_check(91, 82, edition="x")

# unittest.main() must stay at true EOF so direct runner sees all classes.


class CompressorN2Tests(unittest.TestCase):
    SYS = [{"id": "DI-1", "v_gal": 750, "p_psig": 40}, {"id": "DI-2", "v_gal": 500, "p_psig": 40},
           {"id": "DRY-3", "v_gal": 300, "p_psig": 30}]

    def test_compressor_on_largest(self):
        from formulas import compressor_n2_sizing
        r = compressor_n2_sizing(self.SYS, 30)
        self.assertEqual(r["largest_system_id"], "DI-1")
        self.assertAlmostEqual(r["compressor_scfm_gauge"], 750*40/(7.48*14.7*30), places=6)

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


class BraceSpacingTests(unittest.TestCase):
    """brace_spacing_max, cross-checked vs brace_load at 30 ft (672.88 lb)."""
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


class PumpNetAtQTests(unittest.TestCase):
    """pump_net_at_q (NFPA 20-2025 s6.2.1/s6.2.2 listed envelope)."""
    def test_hand_check_1113(self):
        # Hand: 40 + (26-40)*(1113.28-1000)/500 = 40 - 14*0.22656 = 36.8282 psi (36.83)
        from formulas import pump_net_at_q
        r = pump_net_at_q(1000, 40, 1113.28)
        self.assertAlmostEqual(r["p_net_psi"], 36.8282, places=3)
        self.assertAlmostEqual(r["p150_net_psi"], 26.0)
    def test_churn_rated_segment_and_anchors(self):
        from formulas import pump_net_at_q
        r = pump_net_at_q(1000, 40, [0, 500, 1000, 1500])
        p = [x["p_net_psi"] for x in r["points"]]
        self.assertAlmostEqual(p[0], 48.0); self.assertAlmostEqual(p[1], 44.0)
        self.assertAlmostEqual(p[2], 40.0); self.assertAlmostEqual(p[3], 26.0)
        self.assertTrue(r["all_within_150"])
    def test_beyond_150_flagged(self):
        from formulas import pump_net_at_q
        r = pump_net_at_q(1000, 40, 1590)
        self.assertIsNone(r["p_net_psi"]); self.assertFalse(r["all_within_150"])
    def test_bad_churn(self):
        from formulas import pump_net_at_q, CalcError
        with self.assertRaises(CalcError):
            pump_net_at_q(1000, 40, 900, churn_frac=1.5)
    def test_dispatch_alias(self):
        from formulas import dispatch
        self.assertAlmostEqual(dispatch("pump-net-at-q", {"qr_gpm": 750, "pr_psi": 100, "q_gpm": 1125})["p_net_psi"], 65.0)



class CrossMainWalkTests(unittest.TestCase):
    def test_hand_checked_two_branches(self):
        # Hand: pf = 4.52*100^1.85/(120^1.85*4.026^4.87)*10 = 0.003655 psi/ft*10 = 0.0366 psi
        # P = 20.0366; branch raised 100*sqrt(20.0366/20) = 100.091 -> Q = 200.09
        r = formulas.cross_main_walk(120, [{"q_gpm": 100, "p_psi": 20}, {"q_gpm": 100, "p_psi": 20}],
                                     [{"d_in": 4.026, "length_ft": 10}])
        self.assertAlmostEqual(r["p_inlet_psi"], 20.037, places=3)
        self.assertAlmostEqual(r["q_total_gpm"], 200.09, places=2)
        self.assertEqual(r["tees"][0]["adjusted"], "branch raised")
        self.assertTrue(r["all_tees_within_tolerance"])

    def test_branch_higher_raises_cross_main(self):
        r = formulas.cross_main_walk(100, [{"q_gpm": 100, "p_psi": 16}, {"q_gpm": 120, "p_psi": 25}],
                                     [{"d_in": 4.026, "length_ft": 10}])
        self.assertEqual(r["tees"][0]["adjusted"], "cross main raised")
        self.assertAlmostEqual(r["p_inlet_psi"], 25.0, places=3)
        self.assertFalse(r["all_tees_within_tolerance"])
        self.assertGreater(r["q_total_gpm"], 220.0)

    def test_tapered_integration_and_tail(self):
        tb = {"k": 5.6, "p_end_psi": 10, "segments": [{"d_in": 1.049, "length_ft": 12}, {"d_in": 1.38, "length_ft": 12}]}
        one = formulas.tapered_branch(5.6, 10, 100, tb["segments"])
        r = formulas.cross_main_walk(100, [{"tapered": tb}, {"tapered": tb}, {"tapered": tb}],
                                     [{"d_in": 3.068, "length_ft": 10}, {"d_in": 3.068, "length_ft": 10},
                                      {"d_in": 4.026, "length_ft": 50, "dz_ft": 10}])
        self.assertEqual(len(r["tees"]), 2)
        self.assertGreater(r["q_total_gpm"], 3 * one["q_inlet_gpm"])
        self.assertGreater(r["p_inlet_psi"], r["tees"][-1]["p_psi"] + 4.33)
        self.assertIn("tail to riser", r["rows"][-1])

    def test_bad_segment_count(self):
        with self.assertRaises(formulas.CalcError):
            formulas.cross_main_walk(100, [{"q_gpm": 1, "p_psi": 1}] * 3, [{"d_in": 2, "length_ft": 1}])

    def test_dispatch_alias(self):
        r = formulas.dispatch("cross-main-walk", {"c": 120, "branches": [{"q_gpm": 100, "p_psi": 20}],
                                                  "segments": []})
        self.assertAlmostEqual(r["q_total_gpm"], 100.0)


class BatteryStandbyTests(unittest.TestCase):
    def test_hand_checked(self):
        # Hand: 121 mA*24 h = 2.904 AH; 274 mA*5/60 = 0.022833; sum 2.926833 *1.25 = 3.658542
        r = formulas.battery_standby([{"id": "panel", "qty": 1, "standby_ma": 121, "alarm_ma": 274}])
        self.assertAlmostEqual(r["standby_ah"], 2.904, places=6)
        self.assertAlmostEqual(r["ah_required"], 3.658542, places=5)

    def test_vendor_derate_and_battery(self):
        r = formulas.battery_standby([{"qty": 2, "standby_ma": 100, "alarm_ma": 1000}], aging_factor=1.0,
                                     vendor_derate=0.8, battery_ah=7)
        # (0.2*24 + 2*5/60)=4.8+0.1667=4.9667 /0.8 = 6.2083
        self.assertAlmostEqual(r["ah_required_vendor_derated"], 6.208333, places=5)
        self.assertTrue(r["battery_ok"])

    def test_fail_and_bad(self):
        r = formulas.battery_standby([{"qty": 1, "standby_ma": 500, "alarm_ma": 0}], battery_ah=12)
        self.assertFalse(r["battery_ok"])  # 0.5*24*1.25 = 15 > 12
        with self.assertRaises(formulas.CalcError):
            formulas.battery_standby([])
        with self.assertRaises(formulas.CalcError):
            formulas.battery_standby([{"qty": 1, "standby_ma": 1}], vendor_derate=1.5)

    def test_dispatch_alias(self):
        r = formulas.dispatch("battery-standby", {"loads": [{"standby_ma": 1000, "alarm_ma": 0}], "aging_factor": 1})
        self.assertAlmostEqual(r["ah_required"], 24.0)


class BorDemandPressureTests(unittest.TestCase):
    def test_hand_checked(self):
        # Hand: 500^1.85=98,422.5; 100^1.85=5,011.87; 6.065^4.87=6,492.11 -> pf/ft=4.52*98422.5/(5011.87*6492.11)
        # =0.013672 psi/ft x 100 ft = 1.3672 psi; dz 20 ft*0.4333=8.666; P_dis = 60+1.3672+8.666 = 70.033
        r = formulas.bor_demand_pressure(500, 60, 100, [{"d_in": 6.065, "length_ft": 100, "dz_ft": 20}])
        self.assertAlmostEqual(r["friction_psi"], 1.3672, places=3)
        self.assertAlmostEqual(r["p_discharge_required_psi"], 70.033, places=2)
        # suction 20 psi -> net 50.048; qr=500 -> factor 1 -> floor = net
        r2 = formulas.bor_demand_pressure(500, 60, 100, [{"d_in": 6.065, "length_ft": 100, "dz_ft": 20}],
                                          suction_residual_psi=20, qr_gpm=500)
        self.assertAlmostEqual(r2["rated_pressure_floor_psi"], r2["p_net_required_psi"], places=9)
        self.assertAlmostEqual(r2["p_net_required_psi"], 50.033, places=2)

    def test_overload_floor_and_beyond(self):
        # q=150% qr: factor 0.65 -> floor = net/0.65
        r = formulas.bor_demand_pressure(750, 65, 100, qr_gpm=500)
        self.assertAlmostEqual(r["envelope_factor"], 0.65)
        self.assertAlmostEqual(r["rated_pressure_floor_psi"], 100.0)
        r = formulas.bor_demand_pressure(800, 65, 100, qr_gpm=500)
        self.assertIsNone(r["rated_pressure_floor_psi"])
        # roundtrip vs pump_net_at_q at floor
        r = formulas.bor_demand_pressure(600, 70, 100, dz_ft=10, qr_gpm=500)
        back = formulas.pump_net_at_q(500, r["rated_pressure_floor_psi"], 600)["p_net_psi"]
        self.assertAlmostEqual(back, r["p_net_required_psi"], places=9)

    def test_c_lock_and_bad(self):
        with self.assertRaises(formulas.CalcError):
            formulas.bor_demand_pressure(500, 60, 120, system="di")
        with self.assertRaises(formulas.CalcError):
            formulas.bor_demand_pressure(500, 60, 120, system="foam")
        r = formulas.bor_demand_pressure(500, 60, 120, system="wet", friction_allow_psi=5)
        self.assertTrue(r["lump_allowance_flag"])
        self.assertAlmostEqual(r["p_discharge_required_psi"], 65.0)

    def test_dispatch_alias(self):
        r = formulas.dispatch("rated_pressure_screen", {"q_gpm": 500, "p_bor_psi": 60, "dz_ft": 10})
        self.assertAlmostEqual(r["p_discharge_required_psi"], 64.333)


class TestLoopTwoPath(unittest.TestCase):
    def test_hand_check_equal_legs(self):
        # hand (log-table manual): 500^1.85~98,500; 100^1.85~5,012; 8^4.87~25,030; 8 in, 600 ft, 500 gpm/leg, C=100: 4.52*600*500^1.85/(100^1.85*8^4.87)
        r = formulas.loop_two_path(1000, 8, 600)
        hand = 4.52 * 600 * 500 ** 1.85 / (100 ** 1.85 * 8 ** 4.87)
        self.assertAlmostEqual(r["q1_gpm"], 500.0)
        self.assertAlmostEqual(r["p_governing_psi"], hand, places=6)
        self.assertAlmostEqual(hand, 2.130, places=2)  # manual: 2712*98,500/(5,012*25,030)=2.13

    def test_unequal_balanced(self):
        r = formulas.loop_two_path(950, 8, 400, l2_ft=800)
        self.assertAlmostEqual(r["q1_gpm"] + r["q2_gpm"], 950)
        self.assertAlmostEqual(r["p1_psi"], r["p2_psi"], places=6)
        self.assertGreater(r["equal_split_governing_psi"], r["p_governing_psi"])
        self.assertAlmostEqual(r["q1_gpm"] / r["q2_gpm"], 2 ** (1 / 1.85), places=6)

    def test_forced_split_and_dispatch(self):
        r = formulas.dispatch("looped_main", {"q_total_gpm": 700, "d1_in": 8, "l1_ft": 600, "split_frac": 0.5})
        self.assertAlmostEqual(r["p_governing_psi"], r["equal_split_governing_psi"])
        with self.assertRaises(formulas.CalcError):
            formulas.loop_two_path(700, 8, 600, split_frac=1.5)

    # --- unequal-leg sensitivity harness (SCREEN only; no design credit; C=100) ---
    def test_hand_check_unequal_length_balanced(self):
        # hand: w_i ~ (1/L_i)^(1/1.85), equal d/C. L 400/800 -> Q1/Q2 = 2^0.5405 = 1.4545
        # Q2 = 950/2.4545 = 387.04, Q1 = 562.96; hf = 4.52*400*562.96^1.85/(100^1.85*8^4.87)
        r = formulas.loop_two_path(950, 8, 400, l2_ft=800)
        ratio = 2 ** (1 / 1.85)
        q2 = 950 / (1 + ratio)
        self.assertAlmostEqual(r["q2_gpm"], q2, places=6)
        self.assertAlmostEqual(r["q2_gpm"], 387.0, places=0)
        hand = 4.52 * 400 * (950 - q2) ** 1.85 / (100 ** 1.85 * 8 ** 4.87)
        self.assertAlmostEqual(r["p_governing_psi"], hand, places=6)
        self.assertAlmostEqual(hand, 1.77, places=1)

    def test_unequal_diameter_balanced(self):
        # 8 in vs 6 in, equal L: Q1/Q2 = (8/6)^(4.87/1.85); losses equal
        r = formulas.loop_two_path(1000, 8, 600, d2_in=6)
        self.assertAlmostEqual(r["q1_gpm"] / r["q2_gpm"], (8 / 6) ** (4.87 / 1.85), places=6)
        self.assertAlmostEqual(r["p1_psi"], r["p2_psi"], places=6)
        self.assertGreater(r["equal_split_governing_psi"], r["p_governing_psi"])
        self.assertAlmostEqual(r["equal_split_governing_psi"], r["equal_split_p2_psi"])

    def test_sensitivity_monotonic_leg2_length(self):
        # longer leg2 -> more flow on leg1 and higher balanced loss; equal-split governing = leg2
        prev_q1, prev_p = 0.0, 0.0
        for L2 in (600, 900, 1200, 2400):
            r = formulas.loop_two_path(1000, 8, 600, l2_ft=L2)
            self.assertGreaterEqual(r["q1_gpm"], prev_q1 - 1e-9)
            self.assertGreaterEqual(r["p_governing_psi"], prev_p - 1e-9)
            self.assertLessEqual(r["p_governing_psi"], r["equal_split_governing_psi"] + 1e-9)
            prev_q1, prev_p = r["q1_gpm"], r["p_governing_psi"]

    def test_c2_default_lock_and_basis_screen(self):
        r = formulas.loop_two_path(800, 8, 500, l2_ft=700)
        self.assertEqual(r, formulas.loop_two_path(800, 8, 500, l2_ft=700, c=100, c2=100))
        self.assertIn("SCREEN", r["basis"])
        self.assertIn("C=100", r["basis"])



class FusRffTests(unittest.TestCase):
    """new fus_rff op (FUS 1999 Part II)."""

    def test_hand_check_fus_1999_unsprinklered(self):
        # Hand: A=12000 m², C=0.8, occ=-0.15,
        # spr=0.40, exp=0.15 → F0=19279.83→19000; E=16150; H=12112.5→RFF=12000;
        # duration 2.5 h; volume 1800 m³.
        from formulas import fus_rff
        r = fus_rff(
            a_m2=12000,
            c_construction=0.8,
            occupancy_factor=-0.15,
            sprinkler_credit=0.40,
            exposure_factor=0.15,
        )
        self.assertAlmostEqual(r["f0_raw_lpm"], 19279.834024181848, places=6)
        self.assertEqual(r["f0_rounded_lpm"], 19000)
        self.assertAlmostEqual(r["e_occupancy_lpm"], 16150.0)
        self.assertFalse(r["e_floor_applied"])
        self.assertAlmostEqual(r["sprinkler_reduction_lpm"], 6460.0)
        self.assertAlmostEqual(r["exposure_addition_lpm"], 2422.5)
        self.assertAlmostEqual(r["h_raw_lpm"], 12112.5)
        self.assertEqual(r["rff_lpm"], 12000)
        self.assertEqual(r["duration_h"], 2.5)
        self.assertAlmostEqual(r["volume_m3"], 1800.0)
        self.assertEqual(r["edition"], 1999)
        self.assertIn("FUS 1999", r["basis"])
        self.assertIn("verify with engineer of record", r["basis"])
        self.assertIn("GAP-B35R8-1", r["basis"])
        self.assertIn("no FUS 2020 claim", r["basis"])
        self.assertNotIn("FUS 2020 Part", r["basis"])

    def test_unsprinklered_and_floor_clamp(self):
        from formulas import fus_rff
        # Same A/C/occ as above but unsprinklered: H=16150+2422.5=18572.5→19000;
        # 19000 not tabulated → next-higher 20000 → 4.5 h (conservative; the source noted 18k/20k interp band).
        r = fus_rff(12000, 0.8, occupancy_factor=-0.15, sprinkler_credit=0.0, exposure_factor=0.15)
        self.assertEqual(r["rff_lpm"], 19000)
        self.assertEqual(r["duration_h"], 4.5)
        # Tiny FR building → occupancy floor 2000 then final 2000 / 1.0 h
        r2 = fus_rff(10, 0.6, occupancy_factor=-0.25, sprinkler_credit=0.50, exposure_factor=0.0)
        self.assertTrue(r2["e_floor_applied"])
        self.assertEqual(r2["rff_lpm"], 2000)
        self.assertEqual(r2["duration_h"], 1.0)

    def test_rejects_bad_inputs_and_edition_2020(self):
        from formulas import fus_rff, CalcError, dispatch
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.5)  # C below 0.6
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.8, occupancy_factor=-0.30)
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.8, sprinkler_credit=0.55)
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.8, exposure_factor=0.80)
        # 2020 now supported (held cells); other editions still raise
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.8, edition=2022)
        with self.assertRaises(CalcError):
            fus_rff(12000, 0.8, edition="2010")
        # dispatch aliases
        r = dispatch("fus-rff", {"a_m2": 1000, "c_construction": 1.0})
        self.assertEqual(r["edition"], 1999)
        self.assertIn("rff_lpm", r)

    def test_duration_gap_next_higher_and_run_py(self):
        from formulas import fus_rff, _fus1999_duration_h
        # 11000 not tabulated → next-higher 12000 → 2.5 h
        d, note = _fus1999_duration_h(11000)
        self.assertEqual(d, 2.5)
        self.assertIn("SCREEN engineering assumption", note)
        self.assertIn("not a FUS code/clause", note)
        self.assertIn("next-higher", note.lower())
        # 40000 and over
        self.assertEqual(_fus1999_duration_h(45000)[0], 9.5)
        # run.py JSON path smoke
        import json, subprocess, tempfile, os
        payload = {
            "job": "fus-rff",
            "steps": [{
                "id": "rff",
                "op": "fus_rff",
                "a_m2": 12000,
                "c_construction": 0.8,
                "occupancy_factor": -0.15,
                "sprinkler_credit": 0.40,
                "exposure_factor": 0.15,
            }],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".calc.json", delete=False) as fh:
            json.dump(payload, fh)
            path = fh.name
        try:
            out = subprocess.check_output(
                ["python3", "run.py", path], cwd=str(Path(__file__).resolve().parent),
                text=True,
            )
        finally:
            os.unlink(path)
        self.assertIn("TRANSCRIPT_OK", out)
        self.assertIn("12000", out)
        self.assertIn("2.5", out)




class FusRff2020Tests(unittest.TestCase):
    """fus_rff edition=2020 (GAP-B37R46-3) — held cells only; unheld raise."""

    def test_hand_check_2020_same_inputs_as_1999(self):
        # Hand: A=12000, C=0.8 (Type II), occ=-0.15, spr=0.40, exp=0.15
        # F0=220*0.8*sqrt(12000)=19279.83→19000; E=16150; H=16150-6460+2422.5=12112.5→12000;
        # Table 1 exact key 12000 → 2.5 h; V=12000*2.5*60/1000=1800 m³ (same as 1999).
        from formulas import fus_rff
        r = fus_rff(12000, 0.8, occupancy_factor=-0.15, sprinkler_credit=0.40,
                    exposure_factor=0.15, edition=2020)
        self.assertEqual(r["edition"], 2020)
        self.assertEqual(r["f0_rounded_lpm"], 19000)
        self.assertAlmostEqual(r["h_raw_lpm"], 12112.5)
        self.assertEqual(r["rff_lpm"], 12000)
        self.assertEqual(r["duration_h"], 2.5)
        self.assertAlmostEqual(r["volume_m3"], 1800.0)
        self.assertIn("II", r["construction_type_2020"])
        self.assertIsNone(r["clamp_max_lpm"])
        self.assertIn("FUS 2020", r["basis"])
        self.assertIn("verify with engineer of record", r["basis"])
        self.assertIn("GAP-B35R8-1", r["basis"])

    def test_interpolated_duration_delta_and_mass_timber_label(self):
        from formulas import fus_rff
        # Unsprinklered: H=18572.5→19000. 2020 Table 1 interpolate 18k(4.0)/20k(4.5) → 4.25 h;
        # V=19000*4.25*60/1000=4845 m³. (1999 path: next-higher SCREEN → 4.5 h — unchanged.)
        r20 = fus_rff(12000, 0.8, occupancy_factor=-0.15, sprinkler_credit=0.0,
                      exposure_factor=0.15, edition=2020)
        self.assertEqual(r20["rff_lpm"], 19000)
        self.assertAlmostEqual(r20["duration_h"], 4.25)
        self.assertAlmostEqual(r20["volume_m3"], 4845.0)
        self.assertIn("interpolat", r20["duration_note"].lower())
        r99 = fus_rff(12000, 0.8, occupancy_factor=-0.15, sprinkler_credit=0.0, exposure_factor=0.15)
        self.assertEqual(r99["edition"], 1999)
        self.assertEqual(r99["duration_h"], 4.5)
        # IV-B Rated Mass Timber C=0.9: A=10000 → 220*0.9*100=19800→20000; spr 0.5 → 10000; 2.0 h
        r = fus_rff(10000, "Type IV-B", sprinkler_credit=0.50, edition="2020")
        self.assertAlmostEqual(r["c_construction"], 0.9)
        self.assertEqual(r["rff_lpm"], 10000)
        self.assertEqual(r["duration_h"], 2.0)
        self.assertAlmostEqual(r["volume_m3"], 1200.0)

    def test_unheld_2020_cells_raise_not_default(self):
        from formulas import fus_rff, CalcError, dispatch
        bad = [
            dict(a_m2=12000, c_construction=0.7),                      # C not in held 2020 set (no interp)
            dict(a_m2=12000, c_construction="IV-E"),                   # unknown NBC type
            dict(a_m2=12000, c_construction=0.8, sprinkler_credit=0.75),  # +25% community ITM not auto
            dict(a_m2=12000, c_construction=0.8, occupancy_factor=-0.30),
            dict(a_m2=12000, c_construction=0.8, exposure_factor=0.80),
            dict(a_m2=10, c_construction=0.6),                         # E<2000: 2020 floor not held
            dict(a_m2=100000, c_construction=1.5),                     # H>45000: 2020 ceiling not held
            dict(a_m2=1000, c_construction=0.6, occupancy_factor=-0.25, sprinkler_credit=0.5),  # H<2000
        ]
        for kw in bad:
            with self.subTest(kw=kw):
                with self.assertRaises(CalcError):
                    fus_rff(edition=2020, **kw)
        # 1999 still clamps the same tiny case (unchanged behaviour)
        self.assertEqual(fus_rff(10, 0.6)["rff_lpm"], 2000)
        r = dispatch("fus-rff", {"a_m2": 12000, "c_construction": 0.8, "edition": 2020})
        self.assertEqual(r["edition"], 2020)


class DryDeliveryEditionTests(unittest.TestCase):
    """dry_delivery_screen / di_trip_to_water NFPA 13 edition gate (GAP-B27R2-2)."""

    # Hand boundary: Sch40 4 in. ID ~4.026; L such that V just at 500 gal size exemption.
    # gal/ft = pi/4*(4.026**2)/144*7.48 ≈ 0.6615; 500/0.6615 ≈ 755.9 ft → use exact volume path.
    SEG_500 = [{"d_in": 6.065, "length_ft": 280.0}]  # used only if volume path preferred

    # Correction (doc-only): 500 gal is the no-delivery-test size THRESHOLD (DI s8.3.2.3.1.1; dry s8.2.3.3), not a cap;
    # 'caps_same' / nfpa_size_cap_gal are legacy names. DI >500 gal -> s8.3.2.3.1.2-.4; 750 gal is dry-pipe + QOD only.
    def test_hand_check_500gal_exempt_cites_differ_caps_same(self):
        # Hand: V = pi/4 * (4.026**2) / 144 * 7.48 * L
        # Prefer calling with known volume via di_trip + dry segments tuned to ~500 gal.
        # Exact hand volume for 6.065 in × 279.0 ft:
        #   gal/ft = pi/4*(6.065**2)/144*7.48 = 1.50115...; *279 ≈ 418.8 — not 500.
        # Use segments that pipe_volume already trusts; assert exemption at V<=500.
        from formulas import dry_delivery_screen, pipe_volume
        # Build length for exactly 500 gal at d=6.065: L = 500 / gal_per_ft
        import math
        d = 6.065
        gpf = math.pi / 4.0 * (d ** 2) / 144.0 * 7.48
        L = 500.0 / gpf
        seg = [{"d_in": d, "length_ft": L}]
        v = pipe_volume(seg)["volume_gal"]
        self.assertAlmostEqual(v, 500.0, places=6)
        r19 = dry_delivery_screen(seg, 1000, qod=False, system_type="dry", edition=2019)
        r25 = dry_delivery_screen(seg, 1000, qod=False, system_type="dry", edition=2025)
        self.assertTrue(r19["nfpa_delivery_time_exempt"])
        self.assertTrue(r25["nfpa_delivery_time_exempt"])
        self.assertEqual(r19["nfpa_size_cap_gal"], 500.0)
        self.assertEqual(r25["nfpa_size_cap_gal"], 500.0)
        self.assertEqual(r19["edition"], 2019)
        self.assertEqual(r25["edition"], 2025)
        self.assertIn("NFPA 13-2019 s8.2.3.3", r19["nfpa_basis"])
        self.assertIn("NFPA 13-2025 s8.2.4.2.1", r25["nfpa_basis"])
        # doctrinal: numerics identical; only cite labels differ
        self.assertEqual(r19["volume_gal"], r25["volume_gal"])
        self.assertIn("no-water-delivery-test threshold", r19["note_60s_option"])   # dry <=500 volume-aware
        self.assertIn("§8.2.3.3", r19["note_60s_option"])      # dry <=500 -> s8.2.3.3 / s8.2.4.2.1 no-test wording
        self.assertIn("§8.2.4.2.1", r25["note_60s_option"])

    def test_table_cites_and_di_qod_unchanged_by_edition(self):
        from formulas import di_trip_to_water, dry_delivery_screen
        # Table times unchanged; cite labels edition-correct
        a = di_trip_to_water(200, 800, basis="NFPA-OH", edition=2019)
        b = di_trip_to_water(200, 800, basis="NFPA-OH", edition=2025)
        self.assertEqual(a["limit_s"], b["limit_s"])
        self.assertEqual(a["limit_s"], 50.0)
        self.assertIn("Table 8.2.3.6.1", a["nfpa_table_cite"])
        self.assertIn("Table 8.2.4.3.2", b["nfpa_table_cite"])
        # DU 15 s both editions; 2019 cite notes not-a-table-row
        du19 = di_trip_to_water(50, 500, basis="NFPA-DU", edition=2019)
        du25 = di_trip_to_water(50, 500, basis="NFPA-DU", edition=2025)
        self.assertEqual(du19["limit_s"], 15.0)
        self.assertEqual(du25["limit_s"], 15.0)
        self.assertIn("not a Table 8.2.3.6.1 row", du19["nfpa_table_cite"])
        self.assertIn("dwelling-unit row", du25["nfpa_table_cite"])
        # DI + QOD still capped at 500 both editions (preserved)
        big = [{"d_in": 6.065, "length_ft": 450}]  # >>500 gal
        di19 = dry_delivery_screen(big, 1000, qod=True, system_type="di", edition=2019)
        di25 = dry_delivery_screen(big, 1000, qod=True, system_type="di", edition=2025)
        self.assertEqual(di19["nfpa_size_cap_gal"], 500.0)
        self.assertEqual(di25["nfpa_size_cap_gal"], 500.0)
        self.assertFalse(di19["nfpa_delivery_time_exempt"])
        self.assertIn("2019 s8.3.2.3.1.1", di19["nfpa_basis"])
        self.assertIn("2025 s8.3.2.3.1.1", di25["nfpa_basis"])
        # default edition remains 2025 (backward compatible)
        self.assertEqual(di_trip_to_water(100, 500)["edition"], 2025)

    def test_rejects_unsupported_edition_and_r07_screen_label(self):
        from formulas import di_trip_to_water, dry_delivery_screen, CalcError, _fus1999_duration_h, dispatch
        for bad in (2022, 2016, 2013, "2020", "x"):
            with self.assertRaises(CalcError):
                di_trip_to_water(100, 500, edition=bad)
            with self.assertRaises(CalcError):
                dry_delivery_screen([{"d_in": 4, "length_ft": 10}], 500, edition=bad)
        # duration gap remains SCREEN engineering assumption — not a code claim
        note = _fus1999_duration_h(11000)[1]
        self.assertIn("SCREEN engineering assumption", note)
        self.assertIn("not a FUS code/clause", note)
        # dispatch still works with edition
        r = dispatch("dry-delivery-screen", {
            "segments": [{"d_in": 4.026, "length_ft": 50}],
            "q_fill_gpm": 800,
            "edition": 2019,
            "basis": "FM",
        })
        self.assertEqual(r["edition"], 2019)




class ObscurationScTests(unittest.TestCase):
    """new obscuration_sc op (Sc<=Sh/N). GAP-B33R8-1 HOLD untouched."""

    def test_hand_check_fm_examples(self):
        # Hand (KB): 0.2/50=0.004; 0.2/20=0.010; 1.0/25=0.040; 0.2/25=0.008
        from formulas import obscuration_sc
        r50 = obscuration_sc(0.2, 50, "pct_obs_per_ft")
        self.assertAlmostEqual(r50["sc_max"], 0.004)
        self.assertEqual(r50["unit"], "pct_obs_per_ft")
        self.assertAlmostEqual(obscuration_sc(0.2, 20, "pct_obs_per_ft")["sc_max"], 0.010)
        self.assertAlmostEqual(obscuration_sc(1.0, 25, "pct_obs_per_ft")["sc_max"], 0.040)
        self.assertAlmostEqual(obscuration_sc(0.2, 25, "pct_obs_per_ft")["sc_max"], 0.008)
        # optional sc check + sh_eff
        ok = obscuration_sc(0.2, 50, "pct_obs_per_ft", sc=0.004)
        self.assertTrue(ok["passes_sc"])
        self.assertAlmostEqual(ok["sh_eff"], 0.2)
        bad = obscuration_sc(0.2, 50, "pct_obs_per_ft", sc=0.005)
        self.assertFalse(bad["passes_sc"])
        self.assertIn("GAP-B33R8-1 HOLD untouched", r50["gap_b33r8_1"])
        self.assertIn("FA owns", r50["port_layout"])
        self.assertIn("not NFPA 13/72 code trip", r50["basis"])

    def test_listing_floor_n_max_and_pct_m_unit(self):
        from formulas import obscuration_sc
        # KB: 0.2 %/ft / 0.009 %/ft TITANUS floor -> N_max floor = 22
        r = obscuration_sc(0.2, 25, "pct_obs_per_ft", sc_min=0.009)
        self.assertEqual(r["n_max_at_sc_min"], 22)
        self.assertFalse(r["passes_n"])  # 25 > 22
        r2 = obscuration_sc(0.2, 20, "pct_ft", sc_min=0.009)
        self.assertTrue(r2["passes_n"])
        # %/m path — same arithmetic, unit label only (caller supplies values in that unit)
        rm = obscuration_sc(3.3, 25, "pct_obs_per_m")
        self.assertEqual(rm["unit"], "pct_obs_per_m")
        self.assertAlmostEqual(rm["sc_max"], 3.3 / 25)

    def test_rejects_bad_inputs_no_invented_defaults(self):
        from formulas import obscuration_sc, CalcError, dispatch
        with self.assertRaises(CalcError):
            obscuration_sc(0.2, 50, unit="furlong")  # unknown unit
        with self.assertRaises(CalcError):
            obscuration_sc(0.2, 0, "pct_obs_per_ft")
        with self.assertRaises(CalcError):
            obscuration_sc(0.2, 2.5, "pct_obs_per_ft")  # non-integer ports
        with self.assertRaises(CalcError):
            obscuration_sc(0, 10, "pct_obs_per_ft")
        # no default Sh — missing unit still fails
        with self.assertRaises(TypeError):
            obscuration_sc(0.2, 50)  # unit required positional/kw
        r = dispatch("sc_sh_n", {"sh": 1.0, "n_ports": 25, "unit": "pct_obs_per_ft", "sc": 0.04})
        self.assertTrue(r["passes_sc"])
        self.assertAlmostEqual(r["sc_max"], 0.04)


class SprinklerGridCoverageTests(unittest.TestCase):
    """`sprinkler_grid_coverage`. Caps are caller inputs (no code defaults).
    Labels: NFPA 13-2019 Table 10.2.4.2.1(b) OH 130 ft2 / 15 ft (held 13-31);
    FM DS 5-32 Jan-2026 §2.4.3.3.1.1(E) 12 ft (held KB 70_ fm-ds-5-32 L57);
    wall distance NFPA 13-2019 §10.2.5 NOT HELD (SO-1 pending) -> any wall cap is [V] UNVERIFIED."""

    FM_NFPA = {"max_spacing_ft": 12, "max_area_ft2": 130}  # FM DS 5-32 Jan-2026 12 ft + NFPA 13-2019 T10.2.4.2.1(b) 130

    def test_neg_reproduces_b38_r38_13ft_and_80_of_100ft_defect(self):
        """-NEG- DI-3: 100x75 ft, branches x=5..75 @10 ft (8), heads @13 ft.
        Hand check: x_last=5+7*10=75; covered x = 75+10/2 = 80 of 100 -> 20 ft strip;
        13 ft > FM 12 ft; area 10*13 = 130 <= 130 passes (why the defect slipped through)."""
        from formulas import sprinkler_grid_coverage as g
        r = g(100, 75, 10, 13, 8, 6, 5, 6, **self.FM_NFPA)
        self.assertEqual(r["n_heads"], 48)
        self.assertAlmostEqual(r["area_per_head_ft2"], 130)
        self.assertTrue(r["area_ok"])
        self.assertAlmostEqual(r["max_directional_spacing_ft"], 13)
        self.assertFalse(r["spacing_ok"])
        self.assertAlmostEqual(r["covered_x_ft"], 80)
        self.assertAlmostEqual(r["uncovered_x_ft"], 20)
        self.assertAlmostEqual(r["coverage_x_pct"], 80)
        self.assertAlmostEqual(r["wall_x1_ft"], 25)
        self.assertFalse(r["coverage_ok"])
        self.assertFalse(r["passes"])
        self.assertIn("NOT CHECKED", r["wall_ok"])
        # NFPA-only OH caps (15 ft / 130 ft2): spacing passes, coverage still fails
        rn = g(100, 75, 10, 13, 8, 6, 5, 6, max_spacing_ft=15, max_area_ft2=130)
        self.assertTrue(rn["spacing_ok"])
        self.assertFalse(rn["passes"])
        # with a caller [V] wall cap of 6 ft the outer reach grows to 6 ft: 81 of 100, still FAIL
        rw = g(100, 75, 10, 13, 8, 6, 5, 6, max_wall_distance_ft=6, **self.FM_NFPA)
        self.assertAlmostEqual(rw["uncovered_x_ft"], 19)
        self.assertFalse(rw["wall_ok"])  # 25 ft > 6 ft
        self.assertFalse(rw["passes"])

    def test_pass_hand_check_10x11_full_coverage(self):
        """Hand check: branches x=5..95 @10 (10), heads y=4.5..70.5 @11 (7) -> 70 heads,
        110 ft2/head, max 11 ft, walls 5/5/4.5/4.5 ft, covered 100 x 75 (100 %)."""
        from formulas import sprinkler_grid_coverage as g
        r = g(100, 75, 10, 11, 10, 7, 5, 4.5, max_wall_distance_ft=6, min_spacing_ft=7, **self.FM_NFPA)
        self.assertEqual(r["n_heads"], 70)
        self.assertAlmostEqual(r["area_per_head_ft2"], 110)
        self.assertAlmostEqual(r["max_directional_spacing_ft"], 11)
        self.assertAlmostEqual(r["wall_x1_ft"], 5)
        self.assertAlmostEqual(r["wall_y1_ft"], 4.5)
        self.assertAlmostEqual(r["uncovered_x_ft"], 0)
        self.assertAlmostEqual(r["uncovered_y_ft"], 0)
        self.assertTrue(r["wall_ok"])
        self.assertTrue(r["min_spacing_ok"])
        self.assertTrue(r["passes"])
        self.assertEqual(r["fail_reasons"], [])

    def test_wall_cap_fail_min_spacing_and_bad_inputs(self):
        from formulas import sprinkler_grid_coverage as g, CalcError, dispatch
        # shifted grid: x0 wall 7 ft > caller [V] cap 6 ft
        r = g(100, 75, 10, 11, 10, 7, 7, 4.5, max_wall_distance_ft=6, **self.FM_NFPA)
        self.assertAlmostEqual(r["wall_x0_ft"], 7)
        self.assertFalse(r["wall_ok"])
        self.assertAlmostEqual(r["uncovered_x_ft"], 1)  # reach 6 -> covers 1..100
        self.assertFalse(r["passes"])
        # min spacing 7 ft (caller) violated by 6 ft heads
        rm = g(60, 30, 10, 6, 6, 5, 5, 3, min_spacing_ft=7, **self.FM_NFPA)
        self.assertFalse(rm["min_spacing_ok"])
        self.assertFalse(rm["passes"])
        with self.assertRaises(CalcError):
            g(100, 75, 10, 11, 11, 7, 5, 4.5, **self.FM_NFPA)  # x_last 105 outside room
        with self.assertRaises(CalcError):
            g(100, 75, 10, 11, 2.5, 7, 5, 4.5, **self.FM_NFPA)  # non-integer branches
        with self.assertRaises(TypeError):
            g(100, 75, 10, 11, 10, 7, 5, 4.5)  # caps required — no hard-coded defaults
        d = dispatch("grid_coverage", {"room_length_ft": 100, "room_width_ft": 75, "branch_spacing_ft": 10,
                                       "head_spacing_ft": 11, "n_branches": 10, "heads_per_branch": 7,
                                       "branch_offset_ft": 5, "head_offset_ft": 4.5, **self.FM_NFPA})
        self.assertTrue(d["passes"])


class ElevationContractTests(unittest.TestCase):
    """`dz_ft` contract for tapered_branch / cross_main_walk (no numeric change).
    Contract: dz_ft = rise in the flow direction = elevation of the downstream (remote) node minus the
    upstream (inlet) node; + increases required upstream pressure (same as bor_demand_pressure).
    Elevation 0.4333 psi/ft (PSI_PER_FT_WATER)."""

    SENT = "rise in the flow direction"

    def test_a_elevation_convention_key_in_both_ops(self):
        from formulas import tapered_branch, cross_main_walk
        t = tapered_branch(8, 10, 100, [{"d_in": 1.38, "length_ft": 1, "dz_ft": 0, "head": False}])
        c = cross_main_walk(100, [{"q_gpm": 100, "p_psi": 20}], [{"d_in": 4.026, "length_ft": 1}])
        for r in (t, c):
            self.assertIn("elevation_convention", r)
            self.assertIn(self.SENT, r["elevation_convention"])
            self.assertIn("downstream", r["elevation_convention"])

    def test_b_remote_node_10ft_above_inlet_adds_4_333(self):
        """Hand check: remote node 10 ft ABOVE the inlet -> dz_ft=+10 -> +10*0.4333 = +4.333 psi."""
        from formulas import tapered_branch, cross_main_walk
        r = tapered_branch(8, 10, 100, [{"d_in": 1.38, "length_ft": 1, "dz_ft": 10, "head": False}])
        pf = r["nodes"][1]["pf_psi"]
        self.assertAlmostEqual(r["p_inlet_psi"] - 10 - pf, 4.333, delta=0.001)
        c = cross_main_walk(100, [{"q_gpm": 100, "p_psi": 20}], [{"d_in": 4.026, "length_ft": 1, "dz_ft": 10}])
        self.assertAlmostEqual(c["segments_detail"][0]["pe_psi"], 4.333, delta=0.001)

    def test_c_remote_node_10ft_below_inlet_subtracts_4_333(self):
        """Hand check: remote node 10 ft BELOW the inlet -> dz_ft=-10 -> -4.333 psi."""
        from formulas import tapered_branch
        r = tapered_branch(8, 10, 100, [{"d_in": 1.38, "length_ft": 1, "dz_ft": -10, "head": False}])
        pf = r["nodes"][1]["pf_psi"]
        self.assertAlmostEqual(r["p_inlet_psi"] - 10 - pf, -4.333, delta=0.001)
        # Repro: dz +10 gives 14.4071 (code convention), dz -10 gives 5.7411
        self.assertAlmostEqual(tapered_branch(8, 10, 100, [{"d_in": 1.38, "length_ft": 1, "dz_ft": 10,
                                                            "head": False}])["p_inlet_psi"], 14.4071, delta=0.0001)
        self.assertAlmostEqual(r["p_inlet_psi"], 5.7411, delta=0.0001)

    def test_d_hand_checked_r13_riser_drop_elevation_term(self):
        """Hand check: 15.25 ft x 0.4333 = 6.6078 psi elevation term on the 6 in Sch 40 drop."""
        from formulas import cross_main_walk
        r = cross_main_walk(c=100, branches=[{"q_gpm": 946.87, "p_psi": 46.211}],
                            segments=[{"d_in": 6.065, "length_ft": 1, "dz_ft": 15.25}])
        self.assertAlmostEqual(r["segments_detail"][0]["pe_psi"], 6.6078, delta=0.0005)
        self.assertIn("dz(+)=downstream higher", r["segments_detail"][0]["dz_sign"])


class GridCoverageEdgeWallTests(unittest.TestCase):
    """sprinkler_grid_coverage: edge-head area counts in PASS (edge_area_rule
    default "include"); wall_compare "le" (default; NFPA 13-2019 §10.2.5.2.1 "shall not exceed one-half",
    held) | "lt" (FM DS 2-0 §2.5.2.3.2 / Fig. 2.5.2.3.2 strict D_W < 50 % S_MAX,
    ASSUMED insurer). Edge S = max(spacing, 2 x wall distance) per axis [V] (NFPA 13-2019 §9.5.2.1 not pulled)."""

    CAPS = {"max_spacing_ft": 12, "max_area_ft2": 130, "max_wall_distance_ft": 6}

    def test_a_12x10_walls6_edge_144_fails_by_default(self):
        """Hand check: 72x62 room, 6 branches @12 off 6 (x_last 66, walls 6/6), 6 heads @10 off 6
        (y_last 56, walls 6/6). Interior 12x10 = 120; edge max(12,12) x max(10,12) = 144 > 130 -> FAIL."""
        from formulas import sprinkler_grid_coverage as g
        r = g(72, 62, 12, 10, 6, 6, 6, 6, **self.CAPS)
        self.assertAlmostEqual(r["area_per_head_ft2"], 120)
        self.assertAlmostEqual(r["edge_area_per_head_ft2_v"], 144)
        self.assertFalse(r["edge_area_ok"])
        self.assertFalse(r["passes"])
        self.assertTrue(any("edge area 144 > 130" in f for f in r["fail_reasons"]))
        self.assertEqual(r["edge_area_rule"], "include")

    def test_b_same_case_info_rule_passes_backward_path(self):
        from formulas import sprinkler_grid_coverage as g
        r = g(72, 62, 12, 10, 6, 6, 6, 6, edge_area_rule="info", **self.CAPS)
        self.assertTrue(r["passes"])
        self.assertEqual(r["fail_reasons"], [])

    def test_c_walls_exactly_6_strict_lt_fails(self):
        """56x50, 5 @11 off 6 (walls 6/6), 5 @10 off 5 (walls 5/5); cap 6; 'lt' -> 6 < 6 false -> FAIL."""
        from formulas import sprinkler_grid_coverage as g
        r = g(56, 50, 11, 10, 5, 5, 6, 5, wall_compare="lt", **self.CAPS)
        self.assertAlmostEqual(r["max_wall_dist_actual_ft"], 6)
        self.assertFalse(r["wall_ok"])
        self.assertFalse(r["passes"])
        self.assertEqual(r["wall_compare"], "lt")

    def test_d_walls_exactly_6_default_le_passes(self):
        from formulas import sprinkler_grid_coverage as g
        r = g(56, 50, 11, 10, 5, 5, 6, 5, **self.CAPS)
        self.assertTrue(r["wall_ok"])
        self.assertEqual(r["wall_compare"], "le")
        self.assertTrue(r["passes"])

    def test_e_hand_checked_r09_grid_passes_strict(self):
        """DI-3: 100x75, 9 @11.25 off 5 (x_last 95, walls 5/5), 7 @11.0 off 4.5 (y_last 70.5,
        walls 4.5/4.5); edge max(11.25,10) x max(11,9) = 123.75 <= 130; walls 5 < 6 -> PASS under 'lt'."""
        from formulas import sprinkler_grid_coverage as g, CalcError
        r = g(100, 75, 11.25, 11.0, 9, 7, 5, 4.5, wall_compare="lt", **self.CAPS)
        self.assertEqual(r["n_heads"], 63)
        self.assertAlmostEqual(r["edge_area_per_head_ft2_v"], 123.75)
        self.assertTrue(r["passes"])
        with self.assertRaises(CalcError):
            g(100, 75, 11.25, 11.0, 9, 7, 5, 4.5, wall_compare="ge", **self.CAPS)
        with self.assertRaises(CalcError):
            g(100, 75, 11.25, 11.0, 9, 7, 5, 4.5, edge_area_rule="skip", **self.CAPS)


class DiTypedDryCapGuardTests(unittest.TestCase):
    """dry_delivery_screen DI-typed-'dry' 750 gal cap guard.
    Held: NFPA 13-2019 s8.3.2.3.1.1 (DI <=500 gal) / s8.3.2.3.2 (QOD does not extend DI size);
    NFPA 13-2019 s8.2.3.4 (dry 750 gal with QOD). Caps and verdicts unchanged; guard + disclosure only."""

    @staticmethod
    def _seg(v_gal):
        import math
        d = 6.065
        gpf = math.pi / 4.0 * (d ** 2) / 144.0 * 7.48  # hand: 1.500706 gal/ft
        return [{"d_in": d, "length_ft": v_gal / gpf}]

    def test_hand_case_53598_di_typed_dry_qod_raises(self):
        # Hand case (-NEG- row): 535.98 gal DI zone typed 'dry' with QOD would get the 750 gal dry cap.
        from formulas import CalcError, dry_delivery_screen, pipe_volume
        seg = self._seg(535.98)
        self.assertAlmostEqual(pipe_volume(seg)["volume_gal"], 535.98, places=6)
        with self.assertRaises(CalcError) as cm:
            dry_delivery_screen(seg, 450, qod=True, system_type="dry", edition=2019,
                                declared_interlock="double")
        msg = str(cm.exception)
        self.assertIn("NFPA 13-2019 s8.3.2.3.1.1", msg)
        self.assertIn("s8.3.2.3.2", msg)
        self.assertIn("13-FP006-2019-8.3.2.3", msg)

    def test_dry_qod_500_750_discloses_basis_cap_unchanged(self):
        from formulas import dry_delivery_screen
        r = dry_delivery_screen(self._seg(535.98), 450, qod=True, system_type="dry", edition=2019)
        self.assertEqual(r["nfpa_size_cap_gal"], 750.0)          # granted cap unchanged
        self.assertTrue(r["nfpa_delivery_time_exempt"])          # verdict unchanged
        self.assertIn("s8.2.3.4 (750 gal w/ QOD)", r["qod_750_cap_basis"])
        self.assertIn("NFPA 13-2019", r["qod_750_cap_basis"])
        self.assertIn("confirm dry-pipe, not DI", r["warning"])
        # explicit declared_interlock='none' is the same dry-pipe path
        r2 = dry_delivery_screen(self._seg(535.98), 450, qod=True, system_type="dry", edition=2019,
                                 declared_interlock="none")
        self.assertEqual(r2["nfpa_size_cap_gal"], 750.0)
        self.assertEqual(r2["declared_interlock"], "none")
        self.assertIn("qod_750_cap_basis", r2)

    def test_no_disclosure_outside_band_and_di_path_unchanged(self):
        from formulas import dry_delivery_screen
        a = dry_delivery_screen(self._seg(400.0), 450, qod=True, system_type="dry", edition=2019)
        self.assertNotIn("qod_750_cap_basis", a); self.assertNotIn("warning", a)
        b = dry_delivery_screen(self._seg(535.98), 450, qod=False, system_type="dry", edition=2019)
        self.assertNotIn("qod_750_cap_basis", b); self.assertFalse(b["nfpa_delivery_time_exempt"])
        c = dry_delivery_screen(self._seg(800.0), 450, qod=True, system_type="dry", edition=2019)
        self.assertNotIn("qod_750_cap_basis", c); self.assertFalse(c["nfpa_delivery_time_exempt"])
        d = dry_delivery_screen(self._seg(535.98), 450, qod=True, system_type="di", edition=2019,
                                declared_interlock="double")
        self.assertEqual(d["nfpa_size_cap_gal"], 500.0)          # DI cap 500 unchanged
        self.assertFalse(d["nfpa_delivery_time_exempt"])
        self.assertEqual(d["declared_interlock"], "double")
        self.assertNotIn("qod_750_cap_basis", d)
        # di_trip_to_water arithmetic / FM 30 s default unchanged
        self.assertEqual(d["limit_s"], 30.0)
        self.assertAlmostEqual(d["t_fill_s"], 60.0 * 535.98 / 450.0, places=6)

    def test_bad_value_and_dispatch_alias(self):
        from formulas import CalcError, dispatch, dry_delivery_screen
        with self.assertRaises(CalcError):
            dry_delivery_screen(self._seg(300.0), 450, system_type="dry", declared_interlock="single")
        with self.assertRaises(CalcError):
            dispatch("dry_delivery_screen", {"segments": self._seg(535.98), "q_fill_gpm": 450, "qod": True,
                                             "system_type": "dry", "edition": 2019, "declared_interlock": "double"})
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import run as _run
        self.assertEqual(_run.ALIASES["dry_delivery_screen"].get("declared_interlock"), "declared_interlock")
        self.assertIn("qod_750_cap_basis", _run.OUTPUT_ORDER["dry_delivery_screen"])

    def test_tapered_branch_docstring_typo_removed(self):
        from formulas import tapered_branch
        self.assertNotIn("),,", tapered_branch.__doc__)


class RemoteAreaRectangleTests(unittest.TestCase):
    """remote_area_rectangle: NFPA 13-2019 §27.2.4.2.1 1.2*sqrt(A) parallel to branches
    (held). Round-up of fractional sprinklers = [V] (2019 §27.2.4.2.2 not pulled;
    2025 §28.2.4.2.2 comparison only)."""

    def test_a_hand_check_3500_s11_25(self):
        """Hand: sqrt(3500)=59.1608; x1.2=70.9930 ft; /11.25=6.3105 -> 7 heads -> 78.75 ft.
        L=10: S*L=112.5; 3500/112.5=31.11 -> 32 heads; 32/7=4.57 -> 5 branches (last 4); width 50."""
        from formulas import remote_area_rectangle as r
        o = r(3500, 11.25, 10)
        self.assertAlmostEqual(o["required_length_parallel_ft"], 70.99296, places=4)
        self.assertEqual(round(o["required_length_parallel_ft"], 2), 70.99)
        self.assertEqual(o["heads_per_branch_v"], 7)
        self.assertAlmostEqual(o["length_provided_parallel_ft_v"], 78.75)
        self.assertEqual(o["n_heads_v"], 32)
        self.assertEqual(o["n_branches_v"], 5)
        self.assertEqual(o["heads_on_last_branch_v"], 4)
        self.assertAlmostEqual(o["width_perp_ft_v"], 50)
        self.assertAlmostEqual(o["heads_area_ft2_v"], 3600)
        self.assertIsNone(o["room_short_parallel"])
        self.assertFalse(o["elects_remote_area"])
        self.assertIn("27.2.4.2.1", o["basis"])

    def test_b_neg_room_shorter_than_1_2_sqrt_a_reported_not_clipped(self):
        """-NEG-: room 60 ft parallel < 70.99 -> room_short True, shortfall 10.99, 5 heads fit;
        required length and 7 heads/branch NOT clipped."""
        from formulas import remote_area_rectangle as r
        o = r(3500, 11.25, 10, room_length_parallel_ft=60, room_width_perp_ft=100)
        self.assertTrue(o["room_short_parallel"])
        self.assertFalse(o["fits_room"])
        self.assertAlmostEqual(o["shortfall_parallel_ft"], 10.99296, places=4)
        self.assertEqual(o["heads_fit_parallel"], 5)
        self.assertEqual(o["heads_per_branch_v"], 7)
        self.assertAlmostEqual(o["required_length_parallel_ft"], 70.99296, places=4)
        self.assertTrue(any("NOT" in w and "clipped" in w for w in o["warnings"]))

    def test_c_exact_multiple_no_spurious_extra_head_and_room_fits(self):
        """A 2500: 1.2*50 = 60.0 = 5 x 12 exactly -> 5 heads (not 6); L 10 -> 120 ft2;
        2500/120 = 20.83 -> 21 heads; 21/5 -> 5 branches (last 1); room 100 x 60 fits."""
        from formulas import remote_area_rectangle as r
        o = r(2500, 12, 10, room_length_parallel_ft=100, room_width_perp_ft=60)
        self.assertEqual(o["heads_per_branch_v"], 5)
        self.assertEqual(o["n_heads_v"], 21)
        self.assertEqual(o["n_branches_v"], 5)
        self.assertEqual(o["heads_on_last_branch_v"], 1)
        self.assertFalse(o["room_short_parallel"])
        self.assertFalse(o["room_narrow_perp"])
        self.assertTrue(o["fits_room"])

    def test_d_bad_inputs_and_dispatch_aliases(self):
        import formulas
        from formulas import remote_area_rectangle as r, CalcError
        for args in ((0, 11.25, 10), (3500, -1, 10), (3500, 11.25, 0)):
            with self.assertRaises(CalcError):
                r(*args)
        with self.assertRaises(CalcError):
            r(3500, 11.25, 10, room_length_parallel_ft=0)
        for alias in ("remote_area_rectangle", "remote-area-rectangle", "remote_area"):
            o = formulas.dispatch(alias, {"area_ft2": 3500, "head_spacing_ft": 11.25, "branch_spacing_ft": 10})
            self.assertEqual(o["heads_per_branch_v"], 7)



class DiCiteAndHeadsFitTests(unittest.TestCase):
    """DI cite wording, DI 60 s cite, heads_fit_parallel.
    NFPA 13-2019 s8.3.2.3.1.1: a DI system of 500 gal or less needs no water-delivery test (a threshold,
    NOT a cap); larger systems use s8.3.2.3.1.2 (60 s) / .1.3 (calc) / .1.4. Held 13-FP006-2019-8.3.2.3."""
    SEG_600 = [{"d_in": 6.065, "length_ft": 400.0}]   # 600.28 gal > 500
    def test_a_di_size_cite_wording_both_editions(self):
        from formulas import dry_delivery_screen as d
        for ed in (2019, 2025):
            o = d(self.SEG_600, 450, system_type="di", edition=ed)
            b = o["nfpa_basis"]
            self.assertIn(f"NFPA 13-{ed} s8.3.2.3.1.1", b)
            self.assertIn("no delivery-time requirement", b)
            self.assertIn("s8.3.2.3.1.2", b)
            self.assertIn("QOD may help", b)
            self.assertNotIn("does not extend size", b)
    def test_b_di_60s_option_cites_8_3_2_3_1_2_not_dry_clause(self):
        from formulas import dry_delivery_screen as d
        o19 = d(self.SEG_600, 450, system_type="di", edition=2019)
        self.assertIn("NFPA 13-2019 s8.3.2.3.1.2", o19["note_60s_option"])
        self.assertNotIn("s8.2.3.2", o19["note_60s_option"])
        o25 = d(self.SEG_600, 450, system_type="di", edition=2025)
        self.assertIn("s8.3.2.3.1.2", o25["note_60s_option"])
        self.assertNotIn("s8.2.4.2", o25["note_60s_option"])
        self.assertIn("not auto-granted", o19["note_60s_option"])
    def test_c_dry_60s_option_unchanged(self):
        from formulas import dry_delivery_screen as d
        o = d(self.SEG_600, 450, system_type="dry", edition=2019)
        self.assertIn("NFPA 13-2019 s8.2.3.2", o["note_60s_option"])
        o = d(self.SEG_600, 450, system_type="dry", edition=2025)
        self.assertIn("NFPA 13-2025 s8.2.4.2", o["note_60s_option"])
    def test_d_heads_fit_hand_check_75ft_wall_4_5_s11_is_7(self):
        """Hand: (75 - 2*4.5)/11 = 6.0 spacings -> 6 + 1 = 7 heads; end-head span 66.0 ft; 7*11 = 77.0 ft."""
        from formulas import remote_area_rectangle as r
        o = r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=4.5)
        self.assertEqual(o["heads_fit_parallel"], 7)
        self.assertEqual(o["spacings_fit_parallel"], 6)
        self.assertAlmostEqual(o["wall_offset_ft"], 4.5)
        self.assertAlmostEqual(o["length_between_end_heads_ft"], 66.0)
        self.assertEqual(o["heads_per_branch_v"], 7)
        self.assertAlmostEqual(o["length_provided_parallel_ft_v"], 77.0)
    def test_e_heads_fit_default_keeps_spacing_value_but_is_labelled(self):
        from formulas import remote_area_rectangle as r
        o = r(3500, 11.25, 10, room_length_parallel_ft=60, room_width_perp_ft=100)
        self.assertEqual(o["heads_fit_parallel"], 5)      # value unchanged (no wall offset given)
        self.assertEqual(o["spacings_fit_parallel"], 5)
        self.assertIn("spacing", o["heads_fit_parallel_basis"])
        self.assertIn("wall_offset_ft", o["heads_fit_parallel_basis"])
    def test_f_heads_fit_edges(self):
        from formulas import remote_area_rectangle as r
        self.assertEqual(r(3600, 11.0, 10, room_length_parallel_ft=74.99, wall_offset_ft=4.5)["heads_fit_parallel"], 6)
        self.assertEqual(r(3600, 11.0, 10, room_length_parallel_ft=8, wall_offset_ft=4.5)["heads_fit_parallel"], 0)
        self.assertEqual(r(3600, 11.0, 10, room_length_parallel_ft=9, wall_offset_ft=4.5)["heads_fit_parallel"], 1)
        with self.assertRaises(CalcError):
            r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=-1)
    def test_g_remote_area_basis_cites_held_27_2_4_2_2_roundup(self):
        from formulas import remote_area_rectangle as r
        b = r(3500, 11.25, 10)["basis"]
        self.assertIn("27.2.4.2.2", b)
        self.assertIn("13-79", b)
        self.assertNotIn("2019 §27.2.4.2.2 not pulled", b)

class PipeVelocityTests(unittest.TestCase):
    """New op pipe_velocity, v[ft/s] = 0.4085*Q[gpm]/d[in]^2.
    Constant derivation: 1 gal = 231 in^3, 1 ft^2 = 144 in^2. Q gpm = Q*231/(12^3*60) ft^3/s
    = Q*231/103680 ft^3/s. A = pi/4*d^2/144 ft^2. v = Q*(231/103680)*(576/pi)/d^2 = Q*231/(180*pi)/d^2
    = 0.40850*Q/d^2. SCREEN ONLY: no pass/fail against any velocity limit (FM DS 2-0 figures 20 vs 30 ft/s
    conflict and are NOT carried). NFPA 13-2019 s27.2.1.4* HELD (13-78); s27.2.1.1-.3 HOLD (13-81) -> [V]."""
    def test_a_hand_check_131_gpm_in_1_380(self):
        from formulas import pipe_velocity as pv
        o = pv(131, id_in=1.380)
        self.assertAlmostEqual(o["v_fps"], 0.4085 * 131 / 1.9044, places=9)
        self.assertAlmostEqual(o["v_fps"], 28.10, places=2)       # hand check: 53.5135 / 1.9044
        self.assertAlmostEqual(pv(100, id_in=2.067)["v_fps"], 9.5612, places=3)
    def test_b_constant_derivation(self):
        import math
        from formulas import pipe_velocity as pv
        k = 231.0 / (180.0 * math.pi)
        self.assertAlmostEqual(k, 0.4085, places=4)
        o = pv(100, id_in=2)
        self.assertAlmostEqual(o["k_const"], 0.4085, places=9)
        self.assertAlmostEqual(o["k_const_derived"], k, places=9)
        self.assertAlmostEqual(o["flow_area_in2"], math.pi / 4 * 4, places=9)
    def test_c_boundary_at_caller_limit_no_pass_fail(self):
        from formulas import pipe_velocity as pv
        o = pv(100, id_in=2, limit_fps=0.4085 * 100 / 4, limit_source="test-only figure, NOT FM")
        self.assertAlmostEqual(o["v_minus_limit_fps"], 0.0, places=9)
        self.assertAlmostEqual(o["v_over_limit"], 1.0, places=9)
        self.assertEqual(o["limit_source"], "test-only figure, NOT FM")
        o2 = pv(100, id_in=2)
        for d in (o, o2):
            for key in d:
                self.assertNotIn("pass", key.lower()); self.assertNotIn("above", key.lower())
                self.assertNotIn("fail", key.lower())
        self.assertNotIn("limit_fps", o2)
        # The old assertions here pinned the defective label (no 20/30 ft/s mention, "HOLD").
        # 30 ft/s is FM DS 2-0's HW -> Darcy-Weisbach method switch, not a cap; there is no 20 ft/s in DS 2-0.
        self.assertIn("method switch", o2["friction_method_note"]); self.assertIn("30 ft/s", o2["friction_method_note"])
        self.assertNotIn("figure HOLD", o2["friction_method_note"])
    def test_d_limit_needs_source_and_positive(self):
        from formulas import pipe_velocity as pv
        with self.assertRaises(CalcError): pv(100, id_in=2, limit_fps=30)
        with self.assertRaises(CalcError): pv(100, id_in=2, limit_fps=30, limit_source="  ")
        with self.assertRaises(CalcError): pv(100, id_in=2, limit_fps=0, limit_source="x")
    def test_e_negative_inputs_raise(self):
        from formulas import pipe_velocity as pv
        for q, d in ((0, 2), (-5, 2), (100, 0), (100, -1.38), (None, 2), (100, None)):
            with self.assertRaises(CalcError, msg=(q, d)): pv(q, id_in=d)
        with self.assertRaises(CalcError): pv(100, nominal="1-1/4", schedule="40")   # no held ID table: ID explicit
    def test_f_nominal_schedule_are_labels_only(self):
        from formulas import pipe_velocity as pv
        o = pv(131, id_in=1.380, nominal="1-1/4", schedule="40")
        self.assertEqual(o["nominal"], "1-1/4"); self.assertEqual(o["schedule"], "40")
        self.assertIn("caller-supplied", o["id_source"])
        self.assertAlmostEqual(o["v_fps"], pv(131, id_in=1.380)["v_fps"], places=12)
    def test_g_cites(self):
        from formulas import pipe_velocity as pv
        o = pv(131, id_in=1.380)
        self.assertIn("27.2.1.4", o["nfpa13_cite"]); self.assertIn("13-78", o["nfpa13_cite"])
        self.assertIn("2019", o["nfpa13_cite"])
        self.assertIn("27.2.1.1", o["nfpa13_cite"]); self.assertIn("[V]", o["nfpa13_cite"])
        self.assertIn("13-81", o["nfpa13_cite"])
    def test_h_dispatch_and_run_py(self):
        import json, subprocess, tempfile, os
        from formulas import dispatch
        self.assertAlmostEqual(dispatch("pipe_velocity", {"q_gpm": 131, "id_in": 1.380})["v_fps"], 28.0998, places=3)
        self.assertAlmostEqual(dispatch("pipe-velocity", {"q_gpm": 131, "id_in": 1.380})["v_fps"], 28.0998, places=3)
        job = {"job": "t", "steps": [{"id": "v", "op": "pipe_velocity", "q": 131, "id_in": 1.380, "nominal": "1-1/4", "schedule": "40"}]}
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "j.json"); open(p, "w").write(json.dumps(job))
            r = subprocess.run([sys.executable, str(_CALC / "run.py"), p], capture_output=True, text=True,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("v_fps", r.stdout); self.assertIn("TRANSCRIPT_OK", r.stdout); self.assertIn("28.09", r.stdout)

class RepairTests(unittest.TestCase):
    """Kernel repair tests (tests first; one kernel pass).
    RL-1: pipe_velocity labels. FM DS 2-0 (Oct 2021, Interim rev Jan 2024) App A pp.157/161: 30 ft/s is the
    Hazen-Williams -> Darcy-Weisbach method switch, NOT a cap; no 20 ft/s in DS 2-0. No numeric change.
    RL-2: di_trip_to_water optional system_type ('di' -> NFPA 13 s8.3.2.3.1.2 60 s option cite); default unchanged.
    RL-3: dry_delivery_screen adds nfpa_size_threshold_gal (= nfpa_size_cap_gal legacy alias; threshold, not a cap)."""
    SEG_600 = [{"d_in": 6.065, "length_ft": 400.0}]
    def test_rl1_docstring_no_conflicting_figures(self):
        from formulas import pipe_velocity as pv
        d = pv.__doc__
        self.assertNotIn("two conflicting", d); self.assertNotIn("20 and 30", d)
        self.assertIn("method switch", d); self.assertIn("not a cap", d)
        self.assertNotIn("(HELD, 13-78)", d)
    def test_rl1_friction_method_note(self):
        from formulas import pipe_velocity as pv
        n = pv(131, id_in=1.380)["friction_method_note"]
        self.assertNotIn("two conflicting", n); self.assertNotIn("figure HOLD", n)
        self.assertIn("method switch", n); self.assertIn("30 ft/s", n); self.assertIn("not a cap", n)
        self.assertIn("DS 2-0", n); self.assertIn("No velocity pass/fail", n)
    def test_rl1_cite_not_labelled_held_verbatim(self):
        from formulas import pipe_velocity as pv
        c = pv(131, id_in=1.380)["nfpa13_cite"]
        self.assertNotIn("HELD verbatim", c)
        self.assertIn("paraphrase", c); self.assertIn("held clause", c)
        for k in ("27.2.1.4", "13-78", "2019", "27.2.1.1", "[V]", "13-81"): self.assertIn(k, c)
    def test_rl1_numbers_unchanged(self):
        from formulas import pipe_velocity as pv
        o = pv(131, id_in=1.380)
        self.assertAlmostEqual(o["v_fps"], 0.4085 * 131 / 1.380 ** 2, places=12)
        self.assertEqual(o["k_const"], 0.4085); self.assertEqual(o["basis"], "SCREEN - verify with engineer of record")
    def test_rl2_di_trip_system_type_di_cites_8_3_2_3_1_2(self):
        from formulas import di_trip_to_water as t
        for ed, dry in ((2019, "s8.2.3.2"), (2025, "s8.2.4.2")):
            base = t(100, 450, 0, 10, 0, edition=ed)
            self.assertIn(dry, base["note_60s_option"])                       # default unchanged (dry cite)
            self.assertNotIn("s8.3.2.3.1.2", base["note_60s_option"])
            for st in ("di", "DI", "double-interlock", "double_interlock"):
                o = t(100, 450, 0, 10, 0, edition=ed, system_type=st)
                # 100 gal DI is <=500 -> s8.3.2.3.1.1 threshold (was .1.2); >500 is covered in the volume-aware tests below
                self.assertIn(f"NFPA 13-{ed} §8.3.2.3.1.1", o["note_60s_option"])
                self.assertNotIn(dry, o["note_60s_option"])
                self.assertIn("no-water-delivery-test threshold", o["note_60s_option"])
                # the default (system_type None) call now also carries the additive key
                # system_type_default_warning; it is excluded here with note_60s_option (numbers/verdicts compared).
                _skip = ("note_60s_option", "system_type_default_warning")
                self.assertEqual({k: v for k, v in o.items() if k not in _skip},
                                 {k: v for k, v in base.items() if k not in _skip})
            # explicit "dry" at <=500 gal now carries the dry <=500 wording (None stays the legacy label)
            self.assertIn("≤500 gal dry-pipe no-water-delivery-test threshold",
                          t(100, 450, 0, 10, 0, edition=ed, system_type="dry")["note_60s_option"])
            self.assertEqual(t(600, 450, 0, 10, 0, edition=ed, system_type="dry")["note_60s_option"],
                             t(600, 450, 0, 10, 0, edition=ed)["note_60s_option"])
            self.assertEqual(t(100, 450, 0, 10, 0, edition=ed, system_type=None), base)
    def test_rl2_bad_system_type_refused(self):
        from formulas import di_trip_to_water as t
        with self.assertRaises(CalcError): t(100, 450, system_type="wet")
    def test_rl2_dispatch_and_run_py_accept_system_type(self):
        import json, subprocess, tempfile, os
        from formulas import dispatch
        self.assertIn("8.3.2.3.1.1", dispatch("di_trip_to_water", {"v_gal": 100, "q_fill_gpm": 450, "system_type": "di", "edition": 2019})["note_60s_option"])
        job = {"job": "t", "steps": [{"id": "d", "op": "di_trip_to_water", "v_gal": 100, "q_fill_gpm": 450, "t_release_s": 10, "edition": 2019, "system_type": "di"}]}
        with tempfile.TemporaryDirectory() as td:
            pth = os.path.join(td, "j.json"); open(pth, "w").write(json.dumps(job))
            r = subprocess.run([sys.executable, str(_CALC / "run.py"), pth], capture_output=True, text=True,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("system_type", r.stdout); self.assertIn("8.3.2.3.1.1", r.stdout)
    def test_rl2_dry_delivery_screen_di_unchanged(self):
        from formulas import dry_delivery_screen as d
        o = d(self.SEG_600, 450, system_type="di", edition=2019)
        self.assertIn("NFPA 13-2019 s8.3.2.3.1.2", o["note_60s_option"]); self.assertNotIn("s8.2.3.2", o["note_60s_option"])
    def test_rl3_threshold_alias_equal(self):
        from formulas import dry_delivery_screen as d
        small = [{"d_in": 4.026, "length_ft": 60}]
        for seg, kw, want in ((small, dict(system_type="dry"), 500.0),
                              (self.SEG_600, dict(system_type="dry", qod=True), 750.0),
                              (self.SEG_600, dict(system_type="di", qod=True), 500.0),
                              (self.SEG_600, dict(system_type="di"), 500.0)):
            o = d(seg, 450, **kw)
            self.assertIn("nfpa_size_threshold_gal", o); self.assertIn("nfpa_size_cap_gal", o)
            self.assertEqual(o["nfpa_size_threshold_gal"], want); self.assertEqual(o["nfpa_size_cap_gal"], want)
    def test_rl3_docstring_threshold_not_cap(self):
        from formulas import dry_delivery_screen as d
        self.assertIn("nfpa_size_threshold_gal", d.__doc__); self.assertIn("not a cap", d.__doc__)
    def test_rl3_run_py_prints_threshold_key(self):
        import json, subprocess, tempfile, os
        job = {"job": "t", "steps": [{"id": "s", "op": "dry_delivery_screen", "segments": self.SEG_600, "q_fill_gpm": 450, "system_type": "di", "edition": 2019}]}
        with tempfile.TemporaryDirectory() as td:
            pth = os.path.join(td, "j.json"); open(pth, "w").write(json.dumps(job))
            r = subprocess.run([sys.executable, str(_CALC / "run.py"), pth], capture_output=True, text=True,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nfpa_size_threshold_gal", r.stdout); self.assertIn("nfpa_size_cap_gal", r.stdout)

class VolumeAwareCiteTests(unittest.TestCase):
    """delivery-time cite chosen by VOLUME, not by path. DI <=500 gal -> s8.3.2.3.1.1 threshold
    (held 13-FP006-2019/2025-8.3.2.3); DI >500 -> elected .1.2/.1.3/.1.4; dry <=500 (no QOD) / <=750 (QOD) ->
    2019 s8.2.3.3/.4, 2025 s8.2.4.2.1/.2 (held 13-FP006-2019-8.2.3, 13-FP006-2025-8.2.4). Numerics unchanged."""
    G_PER_FT = 3.141592653589793 / 4 * 2.469 ** 2 / 144 * 7.48

    def seg(self, v):
        return [{"d_in": 2.469, "length_ft": v / self.G_PER_FT}]

    def di_note(self, v, ed, via="trip"):
        if via == "trip":
            return f.di_trip_to_water(v, 450, 0, 10, 0, edition=ed, system_type="di")["note_60s_option"]
        return f.dry_delivery_screen(self.seg(v), 450, t_release_s=10, system_type="di", edition=ed)["note_60s_option"]

    def check_le500(self, note, ed):
        self.assertIn(f"≤500 gal DI no-water-delivery-test threshold (NFPA 13-{ed} §8.3.2.3.1.1) — FM 30 s governs", note)
        self.assertIn("not a cap", note)
        self.assertNotIn("60 s test-connection OPTION", note)

    def check_gt500(self, note, ed):
        calc, tab = (("s8.2.3.6", "Table 8.2.3.6.1") if ed == 2019 else ("s8.2.4.3", "Table 8.2.4.3.2"))
        for t in (f"NFPA 13-{ed} s8.3.2.3.1.2", "s8.3.2.3.1.3", calc, "s8.3.2.3.1.4", tab, "elected", "s8.3.2.3.2"):
            self.assertIn(t, note)
        self.assertNotIn("no-water-delivery-test threshold", note)

    def test_di_le500_trip_and_screen_both_editions(self):
        for ed in (2019, 2025):
            for v in (90.3675, 103.7279, 500.0):          # 500.0 inclusive boundary (<=)
                self.check_le500(self.di_note(v, ed, "trip"), ed)
                self.check_le500(self.di_note(v, ed, "screen"), ed)

    def test_di_gt500_trip_and_screen_both_editions(self):
        for ed in (2019, 2025):
            for v in (500.1, 623.0):
                self.check_gt500(self.di_note(v, ed, "trip"), ed)
                self.check_gt500(self.di_note(v, ed, "screen"), ed)

    def test_hand_check_numbers_unchanged(self):
        # Hand check: 60*90.3675/450 = 12.049 s fill; +10 s release = 22.049 s (DI-nA)
        r = f.di_trip_to_water(90.3675, 450, 0, 10, 0, edition=2019, system_type="di")
        self.assertAlmostEqual(r["t_fill_s"], 12.049, places=6)
        self.assertAlmostEqual(r["t_total_s"], 22.049, places=6)
        self.assertTrue(r["passes_screen"]); self.assertEqual(r["limit_s"], 30.0)
        s = f.dry_delivery_screen(self.seg(500.0), 450, t_release_s=10, system_type="di")
        self.assertAlmostEqual(s["volume_gal"], 500.0, places=6)
        self.assertTrue(s["nfpa_delivery_time_exempt"]); self.assertEqual(s["nfpa_size_threshold_gal"], 500.0)
        s2 = f.dry_delivery_screen(self.seg(500.1), 450, t_release_s=10, system_type="di")
        self.assertFalse(s2["nfpa_delivery_time_exempt"])

    def test_default_and_dry_gt_threshold_labels_unchanged(self):
        r = f.di_trip_to_water(90.3675, 450, 0, 10, 0)            # system_type None: unchanged dry label
        self.assertEqual(r["note_60s_option"], "NFPA 13-2025 s8.2.4.2 (60 s test-connection OPTION — elected path, "
                         "not auto-granted) — screen does not auto-elect this path")
        for ed, sec in ((2019, "8.2.3.2"), (2025, "8.2.4.2")):
            d = f.dry_delivery_screen(self.seg(500.1), 450, system_type="dry", edition=ed)
            self.assertIn(f"NFPA 13-{ed} s{sec} (60 s test-connection OPTION", d["note_60s_option"])
            self.assertNotIn("no-water-delivery-test threshold", d["note_60s_option"])

    def test_dry_le500_and_qod_750_wording_both_editions(self):
        for ed, s500, s750 in ((2019, "§8.2.3.3", "§8.2.3.4"), (2025, "§8.2.4.2.1", "§8.2.4.2.2")):
            n = f.dry_delivery_screen(self.seg(400.0), 450, system_type="dry", edition=ed)["note_60s_option"]
            self.assertIn(f"≤500 gal dry-pipe no-water-delivery-test threshold (NFPA 13-{ed} {s500}", n)
            self.assertIn("FM 30 s governs", n); self.assertNotIn("8.3.2.3", n)
            n2 = f.dry_delivery_screen(self.seg(600.0), 450, qod=True, system_type="dry", edition=ed)["note_60s_option"]
            self.assertIn(f"≤750 gal dry-pipe with QOD no-water-delivery-test threshold (NFPA 13-{ed} {s750}", n2)
            self.assertIn("not DI", n2)
            n3 = f.dry_delivery_screen(self.seg(600.0), 450, qod=False, system_type="dry", edition=ed)["note_60s_option"]
            self.assertNotIn("no-water-delivery-test threshold", n3)
            n4 = f.di_trip_to_water(400.0, 450, 0, 10, 0, edition=ed, system_type="dry")["note_60s_option"]
            self.assertIn(f"≤500 gal dry-pipe no-water-delivery-test threshold (NFPA 13-{ed} {s500}", n4)


class ObscurationScBoundaryTests(unittest.TestCase):
    """obscuration_sc N_max = floor(Sh/Sc_min) must be exact at exact decimal multiples.
    Old kernel used float `sh // scmin` (0.3 // 0.01 == 29.0 although 0.3/0.01 is 30 to 1e-15)."""

    def test_choomba_exact_case_n_max_30_and_consistent(self):
        # Boundary example: sc == sc_min, N == Sh/sc_min exactly.
        from formulas import obscuration_sc
        r = obscuration_sc(0.3, 30, "pct_obs_per_ft", sc=0.01, sc_min=0.01)
        self.assertTrue(r["passes_sc"])
        self.assertEqual(r["n_max_at_sc_min"], 30)
        self.assertTrue(r["passes_n"])
        self.assertEqual(r["passes_n"], r["passes_sc"])  # same boundary, same verdict
        # one port more is over the listing floor
        r31 = obscuration_sc(0.3, 31, "pct_obs_per_ft", sc=0.01, sc_min=0.01)
        self.assertEqual(r31["n_max_at_sc_min"], 30)
        self.assertFalse(r31["passes_n"])
        self.assertFalse(r31["passes_sc"])

    def test_exact_multiples_plan_boundaries(self):
        from formulas import obscuration_sc
        for sh, scmin, want in [(0.3, 0.1, 3), (0.7, 0.1, 7), (0.6, 0.2, 2 + 1), (1.0, 0.05, 20)]:
            r = obscuration_sc(sh, want, "pct_obs_per_ft", sc_min=scmin)
            self.assertEqual(r["n_max_at_sc_min"], want, (sh, scmin))
            self.assertTrue(r["passes_n"], (sh, scmin))
            self.assertFalse(obscuration_sc(sh, want + 1, "pct_obs_per_ft", sc_min=scmin)["passes_n"])

    def test_non_boundary_values_unchanged_and_hand_check_exact_rational(self):
        from fractions import Fraction
        from formulas import obscuration_sc
        # existing value stays 22 (0.2/0.009 = 22.22...)
        self.assertEqual(obscuration_sc(0.2, 25, "pct_obs_per_ft", sc_min=0.009)["n_max_at_sc_min"], 22)
        # just below / just above an exact multiple (well outside the 1e-9 tolerance)
        self.assertEqual(obscuration_sc(0.2999, 1, "pct_obs_per_ft", sc_min=0.1)["n_max_at_sc_min"], 2)
        self.assertEqual(obscuration_sc(0.3001, 1, "pct_obs_per_ft", sc_min=0.1)["n_max_at_sc_min"], 3)
        # exact-rational hand check: 0.3 / 0.01 = 3/10 / (1/100) = 30 exactly
        self.assertEqual(Fraction("0.3") / Fraction("0.01"), 30)
        self.assertEqual(obscuration_sc(0.3, 1, "pct_obs_per_ft", sc_min=0.01)["n_max_at_sc_min"], 30)

    def test_sweep_matches_exact_decimal_floor(self):
        # 3-decimal grid: kernel N_max must equal the exact-rational floor for every (Sh, Sc_min).
        from fractions import Fraction
        from math import floor
        from formulas import obscuration_sc
        bad = []
        for a in range(1, 400, 7):
            for b in range(1, 120, 3):
                sh, scmin = a / 1000.0, b / 1000.0
                want = floor(Fraction(a, 1000) / Fraction(b, 1000))
                got = obscuration_sc(sh, 1, "pct_obs_per_ft", sc_min=scmin)["n_max_at_sc_min"]
                if got != want:
                    bad.append((sh, scmin, got, want))
        self.assertEqual(bad, [])

class HeadsFitDefaultGuardTests(unittest.TestCase):
    """Additive warning key; wall_offset_ft NOT required. Tests first.
    When wall_offset_ft is omitted, remote_area_rectangle falls back to the SPACING count floor(Rp/S) for
    heads_fit_parallel. It now ALSO emits heads_fit_parallel_warning (default used; a wall-offset head count may
    differ). Every existing key/value is unchanged. Hand check: Rp 75, S 11.00, w 4.5 -> spacing count 6,
    head count floor((75-9)/11)+1 = 7 (end-head span 66.0 ft; 7*11 = 77.0 ft)."""
    KEY = "heads_fit_parallel_warning"
    LEGACY_KEYS = {"sqrt_a_ft", "required_length_parallel_ft", "heads_per_branch_raw", "heads_per_branch_v",
                   "length_provided_parallel_ft_v", "area_per_head_ft2", "n_heads_raw", "n_heads_v", "n_branches_v",
                   "heads_on_last_branch_v", "width_perp_ft_v", "heads_area_ft2_v", "rectangle_area_ft2_v",
                   "both_sides_of_cross_main", "room_length_parallel_ft", "room_width_perp_ft", "spacings_fit_parallel",
                   "heads_fit_parallel", "heads_fit_parallel_basis", "shortfall_parallel_ft", "room_short_parallel",
                   "room_narrow_perp", "fits_room", "warnings", "elects_remote_area", "basis"}
    def test_a_warning_present_when_wall_offset_omitted(self):
        from formulas import remote_area_rectangle as r
        o = r(3600, 11.0, 10, room_length_parallel_ft=75)
        self.assertIn(self.KEY, o)
        w = o[self.KEY]
        self.assertIsInstance(w, str)
        self.assertIn("wall_offset_ft", w)
        self.assertIn("default", w.lower())
        self.assertIn("spacing count", w)
        self.assertIn("may differ", w)
        self.assertIn("floor(75/11)", w)                                # states the Rp and S used
        self.assertIn("= 6", w)                                         # the default value returned
        self.assertIn("7", w)                                           # Example: wall_offset_ft 4.5 gives 7
    def test_b_warning_absent_when_wall_offset_given_or_no_room(self):
        from formulas import remote_area_rectangle as r
        self.assertNotIn(self.KEY, r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=4.5))
        self.assertNotIn(self.KEY, r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=0))
        self.assertNotIn(self.KEY, r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=0.0, room_width_perp_ft=100))
        self.assertNotIn(self.KEY, r(3600, 11.0, 10))                       # no room length: no heads_fit at all
        self.assertNotIn("heads_fit_parallel", r(3600, 11.0, 10))
    def test_c_hand_check_75_s11_default_6_vs_wall_offset_7(self):
        from formulas import remote_area_rectangle as r
        d = r(3600, 11.0, 10, room_length_parallel_ft=75)
        self.assertEqual(d["heads_fit_parallel"], 6)                      # legacy default value unchanged
        self.assertEqual(d["spacings_fit_parallel"], 6)
        self.assertIn(self.KEY, d)
        o = r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=4.5)
        self.assertEqual(o["heads_fit_parallel"], 7)
        self.assertAlmostEqual(o["length_between_end_heads_ft"], 66.0)
        self.assertEqual(o["heads_per_branch_v"] * 11.0, 77.0)
        self.assertNotIn(self.KEY, o)
    def test_d_legacy_keys_and_values_identical(self):
        from formulas import remote_area_rectangle as r
        d = r(3500, 11.25, 10, room_length_parallel_ft=60, room_width_perp_ft=100)
        self.assertEqual(set(d) - {self.KEY}, self.LEGACY_KEYS)
        self.assertEqual(d["heads_fit_parallel"], 5)
        self.assertEqual(d["spacings_fit_parallel"], 5)
        self.assertEqual(len(d["warnings"]), 1)                            # only the legacy room-short warning
        self.assertNotIn("DEFAULT USED", d["warnings"][0])                 # new key does NOT leak into warnings[]
        self.assertIn("spacing count floor(Rp/S), NOT a head count", d["heads_fit_parallel_basis"])
        o = r(3500, 11.25, 10, room_length_parallel_ft=60, room_width_perp_ft=100, wall_offset_ft=4.5)
        self.assertEqual(set(o), self.LEGACY_KEYS | {"wall_offset_ft", "length_between_end_heads_ft"})
        # numerics identical default vs wall-offset call on every key that does not depend on the offset
        for k in ("sqrt_a_ft", "heads_per_branch_v", "n_heads_v", "n_branches_v", "rectangle_area_ft2_v",
                  "shortfall_parallel_ft", "fits_room", "room_short_parallel"):
            self.assertEqual(d[k], o[k], k)
    def test_e_wall_offset_not_required_and_errors_unchanged(self):
        from formulas import remote_area_rectangle as r
        r(3600, 11.0, 10, room_length_parallel_ft=75)                      # must not raise (NOT required)
        with self.assertRaises(CalcError):
            r(3600, 11.0, 10, room_length_parallel_ft=75, wall_offset_ft=-1)
    def test_f_run_py_prints_warning_key(self):
        import run
        order = run.OUTPUT_ORDER["remote_area_rectangle"]
        self.assertIn(self.KEY, order)
        self.assertEqual(order.index(self.KEY), order.index("heads_fit_parallel_basis") + 1)


class L45RL5DefaultSystemTypeWarningTests(unittest.TestCase):
    """Tests first. di_trip_to_water with system_type omitted keeps the
    legacy DRY-pipe note_60s_option byte-identical and ALSO emits the additive key system_type_default_warning
    ('DEFAULT USED'). The key is absent whenever system_type is given. No numeric, verdict or legacy-label change."""
    KEY = "system_type_default_warning"
    TEXT = "DEFAULT USED: no system_type \u2192 dry-pipe cite; pass system_type='di' for DI"
    LEGACY_KEYS = {"formula", "t_fill_s", "t_total_s", "limit_s", "limit_basis", "margin_s", "passes_screen",
                   "v_max_gal_at_limit", "edition", "nfpa_table_cite", "note_60s_option"}
    def test_a_warning_present_when_system_type_omitted(self):
        from formulas import di_trip_to_water as d
        for ed in (2019, 2025):
            o = d(100.0, 40.0, edition=ed)
            self.assertIn(self.KEY, o, ed)
            self.assertEqual(o[self.KEY], self.TEXT)
            self.assertIn("DEFAULT USED", o[self.KEY])
            self.assertIn("system_type='di'", o[self.KEY])
        self.assertIn(self.KEY, d(600.0, 40.0, system_type=None))     # explicit None == omitted
    def test_b_warning_absent_when_system_type_given(self):
        from formulas import di_trip_to_water as d
        for st in ("dry", "di", "DI", "double-interlock", "double_interlock", "di_preaction", "dry_pipe"):
            for v in (100.0, 600.0):
                self.assertNotIn(self.KEY, d(v, 40.0, system_type=st), (st, v))
    def test_c_legacy_note_and_keys_byte_identical_for_default(self):
        from formulas import di_trip_to_water as d, _nfpa13_dry_cites, _parse_nfpa13_dry_edition
        for ed in (2019, 2025):
            for v in (100.0, 600.0):
                o = d(v, 40.0, edition=ed)
                cites = _nfpa13_dry_cites(_parse_nfpa13_dry_edition(ed))
                self.assertEqual(o["note_60s_option"], cites["dry_60s_cite"] + " \u2014 screen does not auto-elect this path")
                self.assertEqual(set(o) - {self.KEY}, self.LEGACY_KEYS)
    def test_d_numerics_identical_to_explicit_dry_and_no_warning_leak(self):
        from formulas import di_trip_to_water as d
        a = d(412.5, 37.0, 2.0, 3.0, 4.0); b = d(412.5, 37.0, 2.0, 3.0, 4.0, system_type="dry")
        for k in ("t_fill_s", "t_total_s", "limit_s", "limit_basis", "margin_s", "passes_screen", "v_max_gal_at_limit",
                  "edition", "nfpa_table_cite"):
            self.assertEqual(a[k], b[k], k)
        self.assertNotIn("DEFAULT USED", a["note_60s_option"])           # warning is its own key, not in the legacy note
        self.assertNotIn("DEFAULT USED", a["nfpa_table_cite"])
    def test_e_dry_delivery_screen_unchanged(self):
        from formulas import dry_delivery_screen as s
        o = s([{"d_in": 4.0, "length_ft": 100.0}], 40.0, system_type="di")
        self.assertNotIn(self.KEY, o)
        o2 = s([{"d_in": 4.0, "length_ft": 100.0}], 40.0)
        self.assertNotIn(self.KEY, o2)                                    # screen always passes system_type through
    def test_f_run_py_prints_warning_key(self):
        import run
        order = run.OUTPUT_ORDER["di_trip_to_water"]
        self.assertIn(self.KEY, order)
        self.assertEqual(order.index(self.KEY), order.index("note_60s_option") + 1)


if __name__ == "__main__":
    unittest.main()
