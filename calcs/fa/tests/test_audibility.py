import os, sys, unittest, subprocess
H = os.path.dirname(__file__); sys.path.insert(0, os.path.join(H, "..", "lib"))
from audibility import required_dba, check
class T(unittest.TestCase):
    def test_hand_public(self):
        # hand: avg 60, Lmax60 72 -> max(75, 77) = 77
        self.assertEqual(required_dba(60, 72), 77.0)
        self.assertEqual(required_dba(60, 65), 75.0)
    def test_private(self):
        self.assertEqual(required_dba(60, 60, "private"), 70.0)
    def test_ex14_genset(self):
        r = check(108, 112, 110)   # EX-14 inputs
        self.assertEqual(r["required"], 123.0); self.assertFalse(r["feasible"]); self.assertTrue(r["visual_required"])
    def test_held_text(self):
        self.skipTest("raw code text is not stored in this repository")
if __name__ == "__main__": unittest.main()
