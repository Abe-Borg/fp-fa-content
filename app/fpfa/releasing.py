"""How the app words the double-interlock releasing logic, everywhere it prints it.

Release is the detection leg AND P. P is the pressure drop from sprinkler
operation. The calc kernel names that second leg p_second_leg and returns
the Boolean as boolean_p. Low air is a supervisory signal. It is never a
release input, and nothing the app writes, shows, or sends to a model says
it is.

The kernel still returns a deprecated string and row key that call the
second leg low_air. They exist for installed apps older than this one,
which read those names. This module is the one place that knows about
them: the narrative, both documents, the Results tab, and every tool
result a model sees go through it, so the deprecated names never reach a
reader. A saved run or a content pack from before the relabel carries only
the deprecated names; the same logic is then printed with the leg named
p_second_leg.

No method lives here. The Boolean, the definition of the second leg, and
the truth-table rows are the kernel's. This module only chooses which of
the kernel's names to print.
"""

from __future__ import annotations

from typing import Any

# What the app prints for the second leg when a saved run or an older pack does not carry
# the kernel's own sentence. The current kernel returns this definition as second_leg.
SECOND_LEG_FALLBACK = "p_second_leg is P, the pressure drop from sprinkler operation."
# The kernel's own words for the supervisory signal (low_air_note, second sentence).
LOW_AIR_SUPERVISORY = "Low air is supervisory only (PSL-SUP) and is never a release input."
TRUTH_TABLE_TOOL = "releasing_truth_table"
_DEPRECATED_LEG = "low_air"
_SECOND_LEG = "p_second_leg"
_ROW_KEYS = ("rows", "rows_without_second_smoke")
# Keys of the kernel output that exist only for older apps.
_DEPRECATED_KEYS = ("boolean", "deprecated", "low_air_note")


def releasing_logic(truth: dict | None) -> dict:
    """The releasing Boolean and its second leg, as the app prints them anywhere.

    Reads boolean_p and second_leg from the kernel output. When only the
    deprecated string is there, the same Boolean is returned with the leg
    named p_second_leg.
    """
    truth = truth if isinstance(truth, dict) else {}
    boolean = str(truth.get("boolean_p") or "").strip()
    if not boolean:
        boolean = str(truth.get("boolean") or "").replace(_DEPRECATED_LEG, _SECOND_LEG).strip()
    second_leg = str(truth.get("second_leg") or "").strip() or SECOND_LEG_FALLBACK
    return {"expression": boolean, "second_leg": second_leg, "supervisory": LOW_AIR_SUPERVISORY}


def second_leg_value(row: dict) -> bool:
    """P on one truth-table row. An older saved row carries it under the deprecated key."""
    if _SECOND_LEG in row:
        return bool(row[_SECOND_LEG])
    return bool(row.get(_DEPRECATED_LEG))


def releasing_sentence(truth: dict | None, family: str | None = None) -> str:
    """One paragraph on the releasing logic for the narrative and the documents.

    The truth table is electric/electric trim. When the trim screen elected
    another family, the paragraph says so first, and the kernel's own
    sentence on the second leg says what gates P on that trim. The table is
    then a reference, not that valve's logic.
    """
    logic = releasing_logic(truth)
    family = (family or "").strip()
    if family and family != "El/El":
        head = (
            f"Releasing: the elected trim family is {family}. The truth table is the "
            f"electric/electric reference, not this valve's logic: {logic['expression']}."
        )
    else:
        head = f"Releasing: {logic['expression']}."
    return " ".join([head, logic["second_leg"], logic["supervisory"]])


def _row_view(row: Any) -> Any:
    if not isinstance(row, dict):
        return row
    shown = {key: value for key, value in row.items() if key != _DEPRECATED_LEG}
    if _SECOND_LEG not in shown and _DEPRECATED_LEG in row:
        # A row from before the relabel: the same value under the leg's name.
        ordered = {}
        for key, value in row.items():
            ordered[_SECOND_LEG if key == _DEPRECATED_LEG else key] = value
        return ordered
    return shown


def reader_view(tool: str, output: Any) -> Any:
    """A calc output as a model or a designer sees it: the deprecated alias is left out.

    Only the releasing truth table changes. Its Boolean is boolean_p, its rows
    carry p_second_leg, and one sentence says what low air is. The stored
    calc record and the saved run keep the kernel's full output.
    """
    if tool != TRUTH_TABLE_TOOL or not isinstance(output, dict):
        return output
    logic = releasing_logic(output)
    shown: dict = {}
    for key, value in output.items():
        if key in _DEPRECATED_KEYS:
            continue
        if key in _ROW_KEYS and isinstance(value, list):
            shown[key] = [_row_view(row) for row in value]
        else:
            shown[key] = value
    shown["boolean_p"] = logic["expression"]
    shown["second_leg"] = logic["second_leg"]
    shown["low_air"] = LOW_AIR_SUPERVISORY
    return shown
