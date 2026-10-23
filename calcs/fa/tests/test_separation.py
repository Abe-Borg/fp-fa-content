import sys,os,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","lib"))
from separation import shared_ok, annex_sep_ok
class T(unittest.TestCase):
    def test_hand_entry(self):
        # hand check: 8 ft at enclosure <= 10 ft ok; 20 ft riser fails (EX-59 trap)
        self.assertTrue(shared_ok(8,at_enclosure=True)[0]); self.assertFalse(shared_ok(20,at_enclosure=True)[0])
        self.assertTrue(shared_ok(10,at_enclosure=True)[0])
    def test_room(self):
        self.assertTrue(shared_ok(40,room_ft2=1000)[0]); self.assertFalse(shared_ok(40,room_ft2=1001)[0])
    def test_ecf(self):
        ok,r=shared_ok(40,room_ft2=900,has_ecf=True); self.assertFalse(ok); self.assertIn("ECF",r)
    def test_drop_annex(self):
        self.assertTrue(shared_ok(30,single_drop=True)[0])
        self.assertTrue(annex_sep_ok(48,"horizontal")); self.assertFalse(annex_sep_ok(47,"horizontal")); self.assertTrue(annex_sep_ok(12,"vertical"))
if __name__=="__main__": unittest.main()
