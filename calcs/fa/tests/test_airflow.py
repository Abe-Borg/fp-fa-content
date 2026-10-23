import sys,unittest,re; import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from lib.airflow import TABLE, spacing_ft2, detectors, minutes_per_change
class T(unittest.TestCase):
    def test_table_matches_held_2022_and_2025(self):
        self.skipTest("raw code text is not stored in this repository")
    def test_hand(self):  # 20000 ft2 x 14 ft = 280000 ft3 / 70000 cfm = 4 min -> 500 ft2 -> 40
        self.assertEqual(detectors(20000,280000,70000),(500,40))
    def test_round_down(self): self.assertEqual(spacing_ft2(4.9),500); self.assertEqual(spacing_ft2(12),900)
    def test_guards(self):
        with self.assertRaises(ValueError): spacing_ft2(0.9)
        with self.assertRaises(ValueError): minutes_per_change(100,0)
if __name__=="__main__": unittest.main()
