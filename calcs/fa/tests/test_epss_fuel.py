import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import epss_fuel as f

class TestEPSSFuel(unittest.TestCase):
    def test_quotes(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand_check(self):
        # Hand: Class 24 (Class X at 24 h), 140 gph -> low 3360 gal x 1.33 = 4468.8 gal. Class 48 -> 6720 gal x 1.00.
        self.assertAlmostEqual(f.min_tank_gal(24, 140), 4468.8, places=6)
        self.assertAlmostEqual(f.min_tank_gal(48, 140), 6720.0, places=6)
    def test_boundary(self):
        self.assertEqual(f.multiplier(24), 1.33); self.assertEqual(f.multiplier(24.01), 1.00)
    def test_check_and_usable(self):
        r = f.check(5000, 24, 140); self.assertTrue(r["tank_ok"]); self.assertAlmostEqual(r["hours_full_load"], 35.714, places=3)
        self.assertFalse(f.check(5000, 24, 140, usable=0.85)["tank_ok"])   # 4250 usable < 4468.8
    def test_bad_input(self):
        for bad in ((lambda: f.multiplier(0)), (lambda: f.low_fuel_gal(24, 0)), (lambda: f.fuel_hours(100, 10, 1.2))):
            with self.assertRaises(ValueError): bad()

if __name__ == "__main__":
    unittest.main()
