import sys, os, subprocess, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.ads_grid import points, max_on_axis, must_split, grid
class T(unittest.TestCase):
    def test_quotes_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand_check(self):
        # hand: 120 x 80 ft -> ceil(3) x ceil(2) = 6 points; cap 6//3 = 2
        self.assertEqual(points(120, 80), 6); self.assertEqual(max_on_axis(6), 2)
    def test_small_room(self):
        self.assertEqual(points(15, 20), 1); self.assertEqual(max_on_axis(1), 0)
    def test_edge(self):
        self.assertEqual(points(40, 40), 1); self.assertEqual(points(40.1, 40), 2)
    def test_split(self):
        self.assertTrue(must_split(10, 12.5, "tile", "tile"))   # 25%
        self.assertFalse(must_split(10, 12, "tile", "tile"))    # 20% exactly, not over
        self.assertTrue(must_split(10, 10, "carpet", "tile"))
    def test_grid(self):
        self.assertEqual(grid([dict(name="A", L=120, W=80, on_axis=3)])[0], ("A", 6, 2, False))
if __name__ == "__main__": unittest.main()
