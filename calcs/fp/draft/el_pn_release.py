#!/usr/bin/env python3
"""El/Pn solenoid and valve-release function. DRAFT: held, not wired, do not import.

This file is a held draft. No pack module, tool plan, or app code imports it, and
``calcs/fp/test_draft_held.py`` checks that. It stays held until a separate go-ahead.
It is separate from the El/El table in ``di_zone.py``, which stays as it is.

Two outputs, not one:
    solenoid      = (D OR manual_in_D) AND NOT isolated
    valve_release = solenoid AND PA-REL          (P = PA-REL, the listed actuator at the valve)
psl_sup (the low-air supervisory input) is never in either Boolean. It is an inert proof
column, accepted only so a test can show that it changes nothing. Solenoid energized is not
valve release: with D present and PA-REL not tripped the solenoid is true and the valve
stays shut.

manual_in_D: a manual station typed as detection, inside D, still needs P. With no panel
Manual Release station (preaction-releasing-c-and-e-soo footnote 9(a)) manual_in_D is FALSE,
which is the default here. A zone typed Manual Release is an owner and fire-marshal election
(footnote 9(c)), never the company default. Setpoints stay open and no numbers appear here.
"""
from __future__ import annotations

import itertools
from typing import Any

STATUS = "DRAFT, HELD, NOT WIRED"
BOOLEAN_SOLENOID = "solenoid = (detection OR manual_in_D) AND NOT isolated"
BOOLEAN_VALVE_RELEASE = "valve_release = solenoid AND pa_rel"
BOOLEAN_NOTE = "psl_sup is an inert proof column — NOT a release input; it is never in either Boolean; P = PA-REL only"
MANUAL_IN_D_DEFAULT = False
FOOTNOTE_9A = ("preaction-releasing-c-and-e-soo footnote 9(a): no panel Manual Release station "
               "-> manual_in_D := FALSE")
NOT_TABLE = "App di_zone.releasing_truth_table (El/El, 6/32)"


def _b(name: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool, got {type(value).__name__}")
    return value


def el_pn_outputs(detection: bool, manual_in_D: bool = MANUAL_IN_D_DEFAULT, isolated: bool = False,
                  pa_rel: bool = False, psl_sup: bool = False) -> dict[str, bool]:
    """DRAFT, held. Returns {"solenoid", "valve_release"}. psl_sup is an inert proof column, not a release input."""
    d = _b("detection", detection)
    m = _b("manual_in_D", manual_in_D)
    iso = _b("isolated", isolated)
    p = _b("pa_rel", pa_rel)
    _b("psl_sup", psl_sup)  # validated, then ignored: it appears in neither Boolean
    solenoid = (d or m) and not iso
    return {"solenoid": solenoid, "valve_release": solenoid and p}


def el_pn_truth_table(manual_in_D_values: tuple = (False, True)) -> dict[str, Any]:
    """Enumerate the DRAFT table (D, manual_in_D, isolated, PA-REL, PSL-SUP); default 2^5 = 32 rows.

    Pass manual_in_D_values=(MANUAL_IN_D_DEFAULT,) for the footnote 9(a) view (16 rows).
    Separate from the El/El 6/32 table."""
    rows = []
    for d, m, iso, p, s in itertools.product((False, True), tuple(manual_in_D_values),
                                             (False, True), (False, True), (False, True)):
        out = el_pn_outputs(d, m, iso, p, s)
        rows.append({"detection": d, "manual_in_D": m, "isolated": iso, "pa_rel": p, "psl_sup": s, **out})
    return {
        "status": STATUS,
        "boolean_solenoid": BOOLEAN_SOLENOID,
        "boolean_valve_release": BOOLEAN_VALVE_RELEASE,
        "boolean_note": BOOLEAN_NOTE,
        "footnote_9a": FOOTNOTE_9A,
        "row_count": len(rows),
        "solenoid_true_count": sum(r["solenoid"] for r in rows),
        "valve_release_true_count": sum(r["valve_release"] for r in rows),
        "solenoid_true_valve_shut_count": sum(r["solenoid"] and not r["valve_release"] for r in rows),
        "rows": rows,
        "not": NOT_TABLE,
    }


if __name__ == "__main__":
    t = el_pn_truth_table()
    print(t["status"], t["row_count"], t["solenoid_true_count"], t["valve_release_true_count"])
