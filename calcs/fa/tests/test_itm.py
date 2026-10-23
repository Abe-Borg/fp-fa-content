import sys,unittest; import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from lib.itm import visits, sensitivity_years
class T(unittest.TestCase):
    def test_hand_visits(self):  # 3 semi + 5 annual: jan 8, jul 3, year 11
        self.assertEqual(visits([("a",3,2),("b",5,1)]),(8,3,11))
    def test_strict_cycle(self): self.assertEqual(sensitivity_years(10),[1,3,5,7,9])
    def test_extended_and_nuisance(self):
        self.assertEqual(sensitivity_years(10,True),[1,3,8]); self.assertEqual(sensitivity_years(10,True,nuisance_up=(6,)),[1,3,6,8])
    def test_guards(self):
        with self.assertRaises(ValueError): sensitivity_years(10,True,max_gap=6)
        with self.assertRaises(ValueError): visits([("x",1,4)])
if __name__=="__main__": unittest.main()
