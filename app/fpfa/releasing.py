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

It also holds the one detector for the wording this rule forbids
(release_wording_hits): a sentence that departs from that rule. The trace
check runs it on every finding, the reply audit on every lead reply, and
the evaluation on the reply and the exported draft. The pack's
own lint (calcs/fp/test_pack_content_lowair.py) carries the same rules so it
can travel with a bare pack; tests/test_releasing_basis.py holds the two to
the same sentences. It is a guard against a known wrong statement, not a
proof that a sentence is right: a paraphrase nobody thought of passes.
"""

from __future__ import annotations

import re
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


# -- the wording the releasing rule forbids -------------------------------------------------

_LA = r"(?:low[-_ ]air|low[- ]supervisory[- ](?:air|pressure)|loss of supervisory (?:air|pressure))"
_LOW_AIR = re.compile(_LA, re.I)
# The plain spelling, for the widest rule: a sentence that names low air beside a release word.
_LOW_AIR_PLAIN = re.compile(r"low[- ]air", re.I)
_RELEASE_WORD = re.compile(r"\b(releas\w*|opens? the (preaction )?valve)\b", re.I)
_NEGATION = re.compile(
    r"\b(not|never|no|cannot|can't|without|alone|only supervisory|supervisory only|"
    r"is supervisory|stays supervisory|keeps the low-air switch supervisory)\b"
    # The supervisory point named as such: "low-air supervisory row", "supervisory low air".
    r"|low[- ]air supervisory|supervisory low[- ]air",
    re.I,
)
_ACT = r"(?:releas\w*|trips?|tripped|opens?|opened|admit\w*|energi[sz]\w*|discharg\w*)"
# A release, or the release AND written as an operator.
_ACTION = re.compile(r"\b" + _ACT + r"\b|\bAND(?:s|ed)?\b")
# What may stand between a joining word and low air: "and the low-air switch", "plus a low-air signal".
_NEAR = r"\s+(?:(?:a|an|the|its|same-zone|with|on)\s+){0,2}"
# Phrases that state or imply low air as a release leg, whatever else the sentence says.
_BANNED = (
    re.compile(r"low[- ]air release input", re.I),
    re.compile(r"panel low[- ]air interlock", re.I),
    re.compile(r"\band (same-zone )?low air\b.{0,40}\b(releas|not isolated)", re.I),
    re.compile(r"detection and low air together", re.I),
    re.compile(r"needs loss of supervisory pressure before the solenoid", re.I),
    re.compile(r"electric/electric trim uses an electric low[- ]air input", re.I),
    # Low air written as an operand of the release Boolean. The operator is upper case there.
    re.compile(r"\bAND\s+(?:same-zone\s+)?low[-_ ]air\b"),
    # Low air named as the second interlock, gate, or leg, in either order.
    re.compile(r"low[- ]air\b[^.;]{0,30}\bis the (second|2nd)\b[^.;]{0,30}\b(interlock|gate|leg)", re.I),
    re.compile(r"=\s*\**low[- ]air\b[^.;]{0,30}\b(sprinkler leg|second gate|second interlock)", re.I),
    re.compile(r"\b(second|2nd)\s+(leg|interlock|gate|event|input|condition)\b[^.;]{0,50}\b(is|are|=|being)\b"
               r"[^.;]{0,25}" + _LA, re.I),
    # A release that waits for low air.
    re.compile(r"\b(together with|only with|still needs)\s+(same-zone\s+)?low[- ]air\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\b(is|as) (a|the) (trip|release) input\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\balso the\b[^.;]{0,40}\breleas", re.I),
)
# Detection joined to low air. Read as the release AND only in a sentence about releasing (_ACTION).
_JOINED = (
    re.compile(r"\b(detect\w*|smoke|alarm\w*|fire 1)\b[^.;]{0,50}(\band\b|\bplus\b|\+|&|\btogether with\b|"
               r"\bcombined with\b|\bwith\b|\bAND(?:s|ed)?\b)" + _NEAR.replace(r"\s+", r"\s*", 1) + _LA, re.I),
    re.compile(_LA + r"\b[^.;]{0,30}(\band\b|\bplus\b|\+|&|\btogether with\b)[^.;]{0,30}\b(detect\w*|smoke)\b", re.I),
)
# Shapes that read as low air in the release AND unless the same sentence denies it.
_UNLESS_DENIED = (
    # Low air said to finish, confirm, or stand for the release or the second leg.
    re.compile(_LA + r"\b[^.;]{0,60}\b(completes?|confirms?|satisf\w+|provides?|supplies|carries|serves as|acts as)\b"
               r"[^.;]{0,40}\b(releas\w*|interlock|second leg|sprinkler operation|sprinkler leg)\b", re.I),
    # Low air mapped, wired, or used as P.
    re.compile(r"\b(map|wire|use|program|assign|treat)\w*\b[^.;]{0,40}" + _LA + r"\b[^.;]{0,40}\bas\b[^.;]{0,25}"
               r"(\bP\b|\bthe release\b|\ba release\b|\bthe second\b|\bthe interlock\b)", re.I),
    # A release that needs, or happens on, low air.
    re.compile(r"\b" + _ACT + r"\b[^.;]{0,40}\b(needs?|requires?|on|when|upon|after|once)\b[^.;]{0,60}" + _LA, re.I),
    re.compile(r"\b(both|needs?|needed|requires?|required)\b[^.;]{0,80}" + _LA + r"\b[^.;]{0,60}\b" + _ACT + r"\b", re.I),
    re.compile(_LA + r"\b[^.;]{0,20}(->|→|=>)[^.;]{0,15}\breleas", re.I),
)
# The sentence itself says low air is not a release input, or is supervisory only.
_DENIAL = re.compile(r"\b(never|not)\b[^.;]{0,20}\b(a |the )?(trip|release) input\b", re.I)
_DENIES = re.compile(
    r"\b(never|not|no)\b[^.;]{0,25}\b(a |the )?(trip|release)\b|supervisory[- ]only|only supervisory|"
    r"\b(is|are|stays|remains) (a )?supervisory\b|"
    + _LA + r"\b[^.;]{0,45}\b(does not|do not|doesn't|never|cannot|can't|is not|isn't|alone|must not|shall not)\b|"
    r"\b(does not|do not|never|cannot|must not|shall not|not)\b[^.;]{0,60}" + _LA + r"|"
    r"\b(neither|nor)\b|\bwithout\b[^.;]{0,30}" + _LA,
    re.I,
)


def _sentences(text: str):
    for line_no, line in enumerate(str(text or "").splitlines(), 1):
        for part in re.split(r"(?<=[.;])\s+", line):
            if part.strip():
                yield line_no, part.strip()


def release_wording_hits(text: str) -> list[tuple[int, str]]:
    """Sentences in text that depart from the releasing rule: (line number, sentence).

    Empty for text that says nothing of the kind. A sentence that names the
    wording in order to deny it ("low air is never a release input") is not
    a hit.
    """
    hits: list[tuple[int, str]] = []
    for line_no, sentence in _sentences(text):
        if not _LOW_AIR.search(sentence):
            continue
        banned = [pattern for pattern in _BANNED if pattern.search(sentence)]
        if banned:
            # "low air is never a release input" names the phrase in order to deny it.
            only_input_phrase = all("input" in pattern.pattern and "also" not in pattern.pattern
                                    and "second" not in pattern.pattern for pattern in banned)
            if only_input_phrase and _DENIAL.search(sentence):
                continue
            hits.append((line_no, sentence))
        elif _DENIES.search(sentence):
            continue
        elif any(pattern.search(sentence) for pattern in _UNLESS_DENIED):
            hits.append((line_no, sentence))
        elif _ACTION.search(sentence) and any(pattern.search(sentence) for pattern in _JOINED):
            hits.append((line_no, sentence))
        elif _LOW_AIR_PLAIN.search(sentence) and _RELEASE_WORD.search(sentence) and not _NEGATION.search(sentence):
            hits.append((line_no, sentence))
    return hits
