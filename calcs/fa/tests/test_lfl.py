import os, sys, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from lib import lfl as L
class T(unittest.TestCase):
    def test_bulletin_627_example_hand(self):
        # Hand: 100/(80/5.0 + 15/3.0 + 5/2.1) = 100/23.381 = 4.277 -> Bulletin prints 4.3
        v = L.lfl_mix({"CH4": 80, "C2H6": 15, "C3H8": 5}, {"CH4": 5.0, "C2H6": 3.0, "C3H8": 2.1})
        self.assertAlmostEqual(v, 4.277, places=3); self.assertEqual(round(v, 1), 4.3)
    def test_source_text_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_natural_gas_bulletin_503_example(self):
        # USBM Bulletin 503 worked example: 80/15/4/1 at 5.3/3.22/2.37/1.86 -> 4.55
        v = L.lfl_mix({"a": 80, "b": 15, "c": 4, "d": 1}, {"a": 5.3, "b": 3.22, "c": 2.37, "d": 1.86})
        self.assertAlmostEqual(v, 4.55, places=2)
    def test_inert_dropped_and_diluent(self):
        mix = {"H2": 50, "CO2": 50}; l = {"H2": 4.0, "CO2": None}
        self.assertAlmostEqual(L.lfl_mix(mix, l), 4.0)
        self.assertAlmostEqual(L.lfl_with_diluent(mix, l), 8.0)
    def test_ex41_regression(self):
        mix = {"H2":58.0,"CO":9.0,"CO2":22.0,"CH4":5.5,"C2H4":2.5,"C2H6":1.2,"C3H6":0.6,"EMC":0.9,"DMC":0.3}
        l = {"H2":4.0,"CO":10.9,"CO2":None,"CH4":4.4,"C2H4":2.4,"C2H6":2.4,"C3H6":1.8,"EMC":2.0,"DMC":3.1}
        self.assertAlmostEqual(L.lfl_mix(mix, l), 4.11, places=2)
        self.assertAlmostEqual(L.lfl_with_diluent(mix, l), 5.26, places=2)
    def test_setpoints(self):
        v, ppm = L.setpoint(4.0, 25); self.assertAlmostEqual(v, 1.0); self.assertAlmostEqual(ppm, 10000)
        self.assertAlmostEqual(L.pct_of_lfl(0.4, 4.0), 10.0)
    def test_no_fuel_raises(self):
        with self.assertRaises(ValueError): L.lfl_mix({"N2": 100}, {"N2": None})
    def test_r9_trigger_paths_ex93_hand(self):
        # Hand: LFL 5.336 vol% = 53360 ppm. 25% = 13340 ppm. 10% = 5336 ppm. Governing 5336, not 53360 (100%).
        out, gov = L.trigger_paths(5.336)
        self.assertAlmostEqual(out["9.6.5.1.5.4 exhaust"][2], 13340, places=3)
        self.assertAlmostEqual(gov[2], 5336, places=3); self.assertLess(gov[2], 5.336*1e4)
    def test_setpoints_for_uses_the_caller_percent(self):
        mix = {"H2":58.0,"CO":9.0,"CO2":22.0,"CH4":5.5,"C2H4":2.5,"C2H6":1.2,"C3H6":0.6,"EMC":0.9,"DMC":0.3}
        table = {"H2":4.0,"CO":10.9,"CO2":None,"CH4":4.4,"C2H4":2.4,"C2H6":2.4,"C3H6":1.8,"EMC":2.0,"DMC":3.1}
        fuel = L.lfl_mix(mix, table)
        diluted = L.lfl_with_diluent(mix, table)
        vol, ppm = L.setpoint(diluted, 25)
        out = L.setpoints_for(mix, table, [{"name": "screen", "pct": 25, "basis": "diluted"}])
        self.assertAlmostEqual(out["lfl_fuel_vol_pct"], fuel)
        self.assertAlmostEqual(out["lfl_diluted_vol_pct"], diluted)
        self.assertAlmostEqual(out["setpoints"][0]["vol_pct"], vol)
        self.assertAlmostEqual(out["setpoints"][0]["ppm"], ppm)
        self.assertIsNone(out["election"])
        self.assertIsNone(out["duration"])
        self.assertEqual(L.setpoints_for(mix, table, [])["setpoints"], [])
        self.assertEqual(
            set(L.PATH_PCT),
            {"9.6.5.1.5.4 exhaust", "9.6.5.6.7 CCR and alarm"},
        )
        with self.assertRaises(ValueError):
            L.setpoints_for(mix, table, [{"name": "x", "pct": 10, "basis": "room"}])
if __name__ == "__main__": unittest.main()
