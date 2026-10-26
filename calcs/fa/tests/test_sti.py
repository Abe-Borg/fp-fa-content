import sys, os, subprocess, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.sti import evaluate, r05
class T(unittest.TestCase):
    def test_quotes_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand_check_pass(self):
        # hand: 10 locs, 9 at 0.50 and 1 at 0.44 -> 90% >= 0.45; avg (4.50+0.44)/10 = 0.494 -> 0.50 -> PASS
        r = evaluate([(0.50,)] * 9 + [(0.44,)])
        self.assertAlmostEqual(r["avg"], 0.494, places=3); self.assertEqual(r["avg_rep"], 0.50); self.assertTrue(r["pass"])
    def test_fail_on_fraction(self):
        r = evaluate([(0.60,)] * 8 + [(0.44,), (0.40,)])  # 80%
        self.assertEqual(r["frac"], 0.8); self.assertFalse(r["pass"])
    def test_fail_on_average(self):
        r = evaluate([(0.46,)] * 10)  # avg 0.46 -> 0.45 < 0.50
        self.assertEqual(r["avg_rep"], 0.45); self.assertFalse(r["pass"])
    def test_single_point(self):
        self.assertFalse(evaluate([(0.47,)])["pass"]); self.assertTrue(evaluate([(0.50,)])["pass"])
    def test_cis_and_ties(self):
        self.assertTrue(evaluate([(0.72,)] * 10, scale="CIS")["pass"])
        self.assertEqual(r05(0.525), 0.50); self.assertEqual(r05(0.476), 0.50)
if __name__ == "__main__": unittest.main()
