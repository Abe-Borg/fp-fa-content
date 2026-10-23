import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from lib import battery as b

class T(unittest.TestCase):
    def test_hand_check_three_editions(self):
        # Hand: 0.50 A x 24 h = 12.000 Ah; 2.00 A x 5/60 h = 0.1667 Ah; base 12.1667.
        # 2019 x1.20 = 14.600; 2022 and 2025 x1.25 = 15.208. Pick 18 Ah in all.
        r19 = b.ah_required(0.5, 2.0, 2019)
        r22 = b.ah_required(0.5, 2.0, 2022)
        r25 = b.ah_required(0.5, 2.0, 2025)
        self.assertAlmostEqual(r19["base_ah"], 12.1667, places=4)
        self.assertAlmostEqual(r19["req_ah"], 14.6, places=4)
        self.assertAlmostEqual(r22["req_ah"], 15.2083, places=4)
        self.assertEqual(r22["req_ah"], r25["req_ah"])
        self.assertEqual(b.pick_battery(r22["req_ah"]), 18)

    def test_evacs_15min(self):
        r = b.ah_required(0.5, 12.0, 2022, evacs=True)
        self.assertAlmostEqual(r["base_ah"], 12.0 + 3.0, places=6)

    def test_generator_4h(self):
        r = b.ah_required(0.5, 2.0, 2025, generator_backed=True)
        self.assertAlmostEqual(r["base_ah"], 2.0 + 2.0 / 12, places=6)

    def test_no_stacking_and_bad_edition(self):
        self.assertEqual(b.factor(2022), 1.25)
        with self.assertRaises(ValueError):
            b.factor(2016)

    def test_pick_and_margin(self):
        self.assertIsNone(b.pick_battery(150))
        self.assertAlmostEqual(b.margin_pct(16.6667, 18), 8.0, places=1)

    def test_code_text_held(self):
        self.skipTest("raw code text is not stored in this repository")


class TestR11Charger(unittest.TestCase):
    def test_r10_19_case_hand(self):
        # hand: (3.4*24 + 18.0*5/60)*1.25 = (81.6+1.5)*1.25 = 103.875
        r = b.ah_required(3.4, 18.0, 2025)
        self.assertAlmostEqual(r["req_ah"], 103.875, places=3)
        self.assertIsNone(b.pick_battery(r["req_ah"]))
        self.assertTrue(b.charger_ok(r["req_ah"], "simplex_es_ps"))
        self.assertTrue(b.charger_ok(r["req_ah"], "notifier_amps24"))
    def test_unknown_maker_partial(self):
        with self.assertRaises(ValueError):
            b.charger_ok(50, "unlisted_maker")
    def test_split_under_100(self):
        n, r = b.split_supplies(3.4, 18.0, 2025, 100)
        self.assertEqual(n, 2)
        self.assertAlmostEqual(r["req_ah"], 51.9375, places=3)

if __name__ == "__main__":
    unittest.main()
