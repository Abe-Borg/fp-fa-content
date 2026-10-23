import sys, os, subprocess, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.speaker import *
class T(unittest.TestCase):
    def test_quote_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_annex_hand_check(self):  # A.18.3.7.2.1c: 260.338 ohm, 4.76 ohm -> -0.15738
        self.assertAlmostEqual(20*math.log10(260.338/(260.338+4.76)), -0.15738, places=4)
        self.assertAlmostEqual(z_load(70.7, 19.2), 260.338, places=2)
        self.assertAlmostEqual(loss_db(70.7, 19.2, 4.76), -0.15738, places=3)
    def test_k_factor(self):  # annex 59.25 at 0.5 dB; hand: 10^0.025 = 1.05925
        self.assertAlmostEqual(k_factor(0.5), 59.25, places=1); self.assertAlmostEqual(k_factor(1.0), 122.0, places=0)
    def test_max_len_roundtrip(self):  # at max length loss equals target
        L = max_len_ft(25.0, 30.0, 6.28, 1.0); self.assertAlmostEqual(loss_db(25.0, 30.0, 6.28*L/1000), -1.0, places=6)
    def test_amp(self):
        self.assertEqual(amp_check(96, 120), (True, 96.0)); self.assertFalse(amp_check(96.1, 120)[0])
if __name__ == "__main__": unittest.main()
