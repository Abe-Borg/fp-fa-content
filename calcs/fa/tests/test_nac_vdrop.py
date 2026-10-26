import os, sys, subprocess, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from lib import nac_vdrop as n

class T(unittest.TestCase):
    def test_hand_ell_ex02(self):
        # Hand check: 12 x 0.200 A = 2.40 A; 450 ft one way -> 900 ft; 14 AWG str 3.14 -> 2.826 ohm;
        # Vd = 6.782 V; Veol = 20.4 - 6.782 = 13.618 V -> FAIL. 12 AWG: 1.782 ohm, 4.277 V, 16.123 V PASS.
        r = n.ell([0.2] * 12, 450, "14")
        self.assertAlmostEqual(r["R"], 2.826, places=3)
        self.assertAlmostEqual(r["Veol"], 13.618, places=3)
        self.assertFalse(r["pass"])
        r12 = n.ell([0.2] * 12, 450, "12")
        self.assertAlmostEqual(r12["Veol"], 16.1232, places=3)
        self.assertTrue(r12["pass"])

    def test_ex66_16awg(self):
        # QA-EX33-77 F-3: 16 AWG 4.99 gives drop 2.74 V, end 17.66 V. Inputs: 1.0 A? solve: L_both*4.99e-3*I = 2.74.
        # Use I=1.10 A, one way 249.5 ft -> R=2.49 ohm, Vd=2.739 V, Veol=17.661 V.
        r = n.ell([1.10], 249.5, "16")
        self.assertAlmostEqual(r["Vd"], 2.739, places=2)
        self.assertAlmostEqual(r["Veol"], 17.66, places=2)

    def test_ptp_less_than_ell(self):
        segs = [(100, 0.2)] * 5
        p = n.ptp(segs, "14")
        e = n.ell([0.2] * 5, 500, "14")
        # Hand: PTP drop = 0.628 ohm/segment x (1.0+0.8+0.6+0.4+0.2) A = 1.884 V; ELL = 1.0 x 3.14 = 3.14 V
        self.assertAlmostEqual(p["Vd"], 1.884, places=3)
        self.assertAlmostEqual(e["Vd"], 3.14, places=3)
        self.assertLess(p["Vd"], e["Vd"])

    def test_mva_and_maxlen(self):
        L = n.max_one_way_ft(2.4, "14")
        self.assertAlmostEqual(L, 4.4 / 2.4 / 0.00314 / 2, places=3)
        self.assertLess(n.max_one_way_ft(2.4, "14", mva=0.7), L)
        self.assertEqual(n.max_one_way_ft(1.0, "14", v_start=16.0), 0.0)

    def test_smallest_awg(self):
        self.assertEqual(n.smallest_passing_awg([0.2] * 12, 450), "12")

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            n.loop_resistance(-1, "14")
        with self.assertRaises(KeyError):
            n.ohm_per_kft("8")

    def test_table_values_held(self):
        self.skipTest("raw code text is not stored in this repository")

if __name__ == "__main__":
    unittest.main()
