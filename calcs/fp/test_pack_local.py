"""Pack-local checks that sit on top of the repaired kernel in formulas.py.

They cover the finite-number guard and the two-basis fill labels.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from formulas import (CalcError, _as_float, _require_positive, air_fill_scfm,
                      compressor_n2_sizing, di_trip_to_water)


class PackLocalTests(unittest.TestCase):
    SYS = [{"id": "DI-1", "v_gal": 750, "p_psig": 40}, {"id": "DI-2", "v_gal": 500, "p_psig": 40},
           {"id": "DRY-3", "v_gal": 300, "p_psig": 30}]

    def test_air_fill_states_both_bases(self):
        r = air_fill_scfm(1000, 40, 30)
        self.assertIn(f"Gauge-basis fill rate is {r['scfm_gauge_basis']:.2f} scfm", r["fill_bases"])
        self.assertIn(f"Absolute-basis fill rate is {r['scfm_abs_basis']:.2f} scfm", r["fill_bases"])

    def test_compressor_n2_states_both_bases(self):
        r = compressor_n2_sizing(self.SYS, 30)
        self.assertIn(f"Compressor gauge-basis fill rate is {r['compressor_scfm_gauge']:.2f} scfm", r["fill_bases"])
        self.assertIn(f"Compressor absolute-basis fill rate is {r['compressor_scfm_abs']:.2f} scfm", r["fill_bases"])
        self.assertIn(f"N2 campus gauge-basis fill rate is {r['n2_campus_scfm_gauge']:.2f} scfm", r["fill_bases"])

    def test_positive_inputs_reject_non_finite(self):
        for bad in ("1e309", math.inf, math.nan, "-inf"):
            with self.assertRaises(CalcError):
                _as_float("q_fill_gpm", bad)
            with self.assertRaises(CalcError):
                _require_positive("q_fill_gpm", bad)
            with self.assertRaises(CalcError):
                di_trip_to_water(100, bad)
            with self.assertRaises(CalcError):
                air_fill_scfm(100, bad, 30)
        with self.assertRaises(CalcError):
            _require_positive("q_fill_gpm", 0)
        with self.assertRaises(CalcError):
            _require_positive("q_fill_gpm", -1)


if __name__ == "__main__":
    unittest.main()
