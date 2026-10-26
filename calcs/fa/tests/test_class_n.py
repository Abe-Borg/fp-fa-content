import sys, os, subprocess, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.class_n import check_pathway, check_network
OK = dict(e2e_verified=True, loss_trouble=True, degraded_trouble=True)
class T(unittest.TestCase):
    def test_quotes_held(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand_check(self):
        # hand: 3 endpoints, primary S1,S2,S3, redundant S4,S2 -> S2 shared -> one finding (7)
        f = check_pathway(dict(name="A", endpoints=3, primary=["S1","S2","S3"], redundant=["S4","S2"], **OK))
        self.assertEqual(f, ["12.3.6(7): shared segment(s) S2"])
    def test_single_endpoint_single_path(self):
        self.assertEqual(check_pathway(dict(name="B", endpoints=1, primary=["S9"], redundant=None, **OK)), [])
    def test_two_endpoints_no_redundant(self):
        f = check_pathway(dict(name="C", endpoints=2, primary=["S1"], redundant=None, **OK))
        self.assertIn("12.3.6(1): 2+ endpoints, no redundant path", f)
    def test_flags(self):
        f = check_pathway(dict(name="D", endpoints=2, primary=["a"], redundant=["b"]))
        self.assertEqual(len(f), 3)
    def test_network_shared(self):
        o = check_network([dict(name="X", endpoints=1, primary=["T1"], **OK), dict(name="Y", endpoints=1, primary=["T1"], **OK)])
        self.assertEqual(len(o["X"]), 1); self.assertIn("T1", o["Y"][0])
if __name__ == "__main__": unittest.main()
