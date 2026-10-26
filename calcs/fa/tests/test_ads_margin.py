import math, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import ads_margin as m

class TestADSMargin(unittest.TestCase):
    def test_source_quote(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_halving_is_6db(self):
        self.assertAlmostEqual(m.spl_at(90, 5) - m.spl_at(90, 10), 20 * math.log10(2), places=9)
        self.assertAlmostEqual(m.spl_at(90, 5) - 90, 6.02, places=2)
    def test_hand_check(self):
        # Hand: two 88 dBA@10 ft horns at 20 ft each -> 81.98 each; sum = 81.98 + 3.01 = 84.99 dBA.
        # Ambient 65 avg, Lmax60 72 -> required max(80, 77) = 80. Margin 4.99 dB.
        r = m.margin(65, 72, [(88, 20), (88, 20)])
        self.assertAlmostEqual(r["predicted"], 84.99, places=2)
        self.assertEqual(r["required"], 80)
        self.assertAlmostEqual(r["margin_db"], 4.99, places=2)
        self.assertTrue(r["meets"])
    def test_fail_and_cap(self):
        self.assertFalse(m.margin(80, None, [(84, 20)])["meets"])
        self.assertTrue(m.margin(100, None, [(120, 10)])["over_cap"])
        self.assertTrue(m.margin(106, None, [(110, 10)])["visual_required"])
    def test_bad_input(self):
        with self.assertRaises(ValueError): m.spl_at(90, 0)
        with self.assertRaises(ValueError): m.combine([])

if __name__ == "__main__":
    unittest.main()
