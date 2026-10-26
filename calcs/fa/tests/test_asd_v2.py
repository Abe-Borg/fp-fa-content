import sys, os, subprocess, unittest, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib import asd_v2 as v
A = math.pi * 0.021 ** 2 / 4
class T(unittest.TestCase):
    def test_quotes_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand_check(self):
        # hand: header 10 m at 40 L/min; one branch, lead 0, 2 holes 5 m apart, q/hole 20.
        # header v = (40/60000)/A = 1.9248 m/s -> 5.195 s; segment 5 m at 20 L/min v = 0.9624 -> 5.195 s; total 10.390 s
        b = v.branch("B", 21, 0, 2, 5)
        t = v.network(10, 21, [b], 40)["B"][0]
        self.assertAlmostEqual(t, 10 / ((40/60000)/A) + 5 / ((20/60000)/A), places=6)
        self.assertAlmostEqual(t, 10.390, places=2)
    def test_v1_bounds_v2(self):
        b = v.branch("B", 21, 3, 8, 4)
        t2 = v.network(12, 21, [b, v.branch("C", 21, 3, 8, 4)], 64)["B"][0]
        self.assertLess(t2, v.v1_screen(12, b, 64 / 16))
    def test_more_branches_faster_header_share(self):
        b = v.branch("B", 21, 0, 4, 5)
        one = v.network(20, 21, [b], 40)["B"][0]
        two = v.network(20, 21, [b, v.branch("C", 21, 0, 4, 5)], 40)["B"][0]
        self.assertGreater(two, one)  # same fan flow split two ways: slower per branch
    def test_bad_input(self):
        with self.assertRaises(ValueError): v.network(10, 0, [v.branch("B", 21, 0, 2, 5)], 40)
class TestR11PortTimes(unittest.TestCase):
    def test_hand_first_port(self):
        # hand: v = (50/60000)/(pi*0.021^2/4) = 2.4059 m/s; (8+1)/v = 3.741 s
        pt = v.port_times(8, 21, [v.branch("LOW", 21, 1, 5, 6.1)], 50)
        vel = (50/60000.0)/(math.pi*0.021**2/4)
        self.assertAlmostEqual(pt["LOW"][0], 9/vel, places=6)
        self.assertEqual(len(pt["LOW"]), 5)
    def test_far_port_matches_network(self):
        brs = [v.branch("H", 21, 4, 6, 6.1), v.branch("L", 21, 1, 5, 6.1)]
        pt = v.port_times(8, 21, brs, 50); net = v.network(8, 21, brs, 50)
        for k in pt: self.assertAlmostEqual(pt[k][-1], net[k][0], places=9)
    def test_ex100_r11_every_port_60s(self):
        brs = [v.branch("H1",21,4,3,6.1), v.branch("H2",21,4,3,6.1), v.branch("L1",21,1,3,6.1), v.branch("L2",21,1,2,6.1)]
        pt = v.port_times(8, 21, brs, 50)
        self.assertTrue(all(t <= 60.0 for ts in pt.values() for t in ts))
        self.assertTrue(all(ts == sorted(ts) for ts in pt.values()))
if __name__ == "__main__": unittest.main()
