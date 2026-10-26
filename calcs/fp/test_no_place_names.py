"""The calc tree must not carry job, client, or place names."""

from __future__ import annotations

import unittest

from place_name_scan import assert_no_place_names


class PlaceNameTests(unittest.TestCase):
    def test_calcs_tree_has_no_job_client_or_place_names(self):
        assert_no_place_names()


if __name__ == "__main__":
    unittest.main()
