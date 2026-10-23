import unittest, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import asd
class T(unittest.TestCase):
    def test_hand(self):  # 21 mm ID, 30 L/min: A=3.4636e-4 m2, v=0.5/3.4636e-4/... 
        v = (30/1000/60) / (3.141592653589793*0.021**2/4); self.assertAlmostEqual(v, 1.4436, places=3)
        self.assertAlmostEqual(asd.transport_s(50, 21, 30), 50/v, places=6); self.assertAlmostEqual(asd.transport_s(50, 21, 30), 34.64, places=1)
    def test_limits(self):
        r = asd.check(100, 21, 30); self.assertFalse(r["pass"]); self.assertTrue(r["code_pass"])
        self.assertAlmostEqual(asd.max_len_m(60, 21, 30), 86.6, places=0)
    def test_scaling(self):  # double flow halves time
        self.assertAlmostEqual(asd.transport_s(80, 21, 60) * 2, asd.transport_s(80, 21, 30), places=9)
    def test_bad(self):
        with self.assertRaises(ValueError): asd.transport_s(10, 21, 0)
    def test_quotes(self):
        self.skipTest("raw code text is not stored in this repository")
if __name__ == "__main__": unittest.main()
