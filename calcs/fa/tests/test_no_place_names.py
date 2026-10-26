"""The calc tree must not carry job, client, or place names."""

import os
import sys
import unittest

_FP = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "fp")
sys.path.insert(0, _FP)
from place_name_scan import assert_no_place_names


class PlaceNameTests(unittest.TestCase):
    def test_calcs_tree_has_no_job_client_or_place_names(self):
        assert_no_place_names()


if __name__ == "__main__":
    unittest.main()
