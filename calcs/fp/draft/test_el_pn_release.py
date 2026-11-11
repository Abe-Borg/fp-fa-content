#!/usr/bin/env python3
"""Tests for the held El/Pn draft function. DRAFT: held, not wired.

The draft stays held until a separate go-ahead. Nothing imports it.
"""
from __future__ import annotations

import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import el_pn_release as ep  # noqa: E402


class ElPnReleaseDraftTests(unittest.TestCase):
    def test_00_draft_status_marks_the_module_held(self):
        self.assertIn("DRAFT", ep.STATUS)
        self.assertIn("HELD", ep.STATUS)

    def test_01_hand_checked_solenoid_true_valve_shut(self):
        # D=1, manual_in_D=0, isolated=0, PA-REL=0: solenoid=(1 OR 0) AND NOT 0 = 1; valve=1 AND 0 = 0
        for psl in (False, True):
            out = ep.el_pn_outputs(detection=True, manual_in_D=False, isolated=False, pa_rel=False, psl_sup=psl)
            self.assertEqual(out, {"solenoid": True, "valve_release": False})

    def test_02_psl_sup_alone_releases_neither(self):
        out = ep.el_pn_outputs(detection=False, manual_in_D=False, isolated=False, pa_rel=False, psl_sup=True)
        self.assertEqual(out, {"solenoid": False, "valve_release": False})
        out = ep.el_pn_outputs(detection=False, manual_in_D=False, isolated=False, pa_rel=True, psl_sup=True)
        self.assertEqual(out, {"solenoid": False, "valve_release": False})

    def test_03_manual_in_D_substitutes_for_D_only_and_isolation_blocks(self):
        both = ep.el_pn_outputs(False, True, False, True)
        self.assertEqual(both, {"solenoid": True, "valve_release": True})
        no_p = ep.el_pn_outputs(False, True, False, False)
        self.assertEqual(no_p, {"solenoid": True, "valve_release": False})
        iso = ep.el_pn_outputs(True, True, True, True)
        self.assertEqual(iso, {"solenoid": False, "valve_release": False})

    def test_04_footnote_9a_default_manual_in_D_false(self):
        # preaction-releasing-c-and-e-soo footnote 9(a): no panel Manual Release -> manual_in_D := FALSE
        self.assertIs(ep.MANUAL_IN_D_DEFAULT, False)
        self.assertIn("9(a)", ep.FOOTNOTE_9A)
        self.assertEqual(ep.el_pn_outputs(detection=False, isolated=False, pa_rel=True),
                         {"solenoid": False, "valve_release": False})
        t9a = ep.el_pn_truth_table(manual_in_D_values=(ep.MANUAL_IN_D_DEFAULT,))
        self.assertEqual((t9a["row_count"], t9a["solenoid_true_count"], t9a["valve_release_true_count"]), (16, 4, 2))

    def test_05_32_row_table_counts_12_solenoid_6_valve_6_shut(self):
        t = ep.el_pn_truth_table()
        self.assertEqual(t["row_count"], 32)
        self.assertEqual(len({(r["detection"], r["manual_in_D"], r["isolated"], r["pa_rel"], r["psl_sup"])
                              for r in t["rows"]}), 32)
        self.assertEqual(t["solenoid_true_count"], 12)
        self.assertEqual(t["valve_release_true_count"], 6)
        self.assertEqual(t["solenoid_true_valve_shut_count"], 6)
        self.assertIn("DRAFT", t["status"])
        self.assertNotIn("psl_sup", t["boolean_solenoid"])
        self.assertNotIn("psl_sup", t["boolean_valve_release"])
        self.assertIn("pa_rel", t["boolean_valve_release"])

    def test_06_every_row_matches_the_boolean_independently(self):
        for r in ep.el_pn_truth_table()["rows"]:
            sol = (r["detection"] or r["manual_in_D"]) and not r["isolated"]
            self.assertEqual(r["solenoid"], sol)
            self.assertEqual(r["valve_release"], bool(sol and r["pa_rel"]))

    def test_07_psl_sup_is_inert_on_every_row(self):
        for d, m, i, p in itertools.product((False, True), repeat=4):
            self.assertEqual(ep.el_pn_outputs(d, m, i, p, False), ep.el_pn_outputs(d, m, i, p, True))

    def test_09_NEG_el_el_boolean_is_not_this_table(self):
        """NEG: a single-output Boolean that keys the release on the low-air supervisory input.

        That construction collapses solenoid energize with valve admission. It has 6 of 32 true rows,
        the same count as valve_release, but the true rows differ."""
        wrong, valve = set(), set()
        for r in ep.el_pn_truth_table()["rows"]:
            k = (r["detection"], r["manual_in_D"], r["isolated"], r["pa_rel"], r["psl_sup"])
            if (r["detection"] or r["manual_in_D"]) and r["psl_sup"] and not r["isolated"]:
                wrong.add(k)
            if r["valve_release"]:
                valve.add(k)
        self.assertEqual((len(wrong), len(valve)), (6, 6))
        self.assertEqual(len(wrong & valve), 3)
        self.assertNotEqual(wrong, valve)

    def test_10_outputs_reject_non_boolean_inputs(self):
        with self.assertRaises(TypeError):
            ep.el_pn_outputs(detection="yes", manual_in_D=False, isolated=False, pa_rel=False)


if __name__ == "__main__":
    unittest.main()
