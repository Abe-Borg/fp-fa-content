"""Project inputs: what the designer gave the team to work from.

The zone form and the basis fields are the job's inputs. They are the
shared assumptions every agent reasons from, so they live on the project
record as facts (kind "input" for the zone, kind "basis" for the five
basis fields). The form is one way to edit them; telling the lead in chat
is the other (the lead's set_input tool). When a value changes, the old
fact row is superseded, and every calculation that used the old value is
out of date until it is run again (fpfa.coherence).

This module is the one description of those inputs: their names, their
types, the hint a blank field shows, and how a value is checked and
compared. It holds no method. It does not compute or default an
engineering figure; a blank stays blank.

Every field of a new form is blank. A field may show a hint (HINTS): a value
the content pack pins, always shown with its cite and edition and labeled
VERIFY. A hint is never an input until the designer enters a value or accepts
it. An accepted hint is recorded with the label ASSUMED, and its source says
the designer accepted it (SOURCE_ACCEPTED). Accepting a hint clears no HOLD:
an ASSUMED edition is still not pinned, and every other ASSUMED input carries
its own "<name> ASSUMED" line (assumed_lines) until the designer types a value.
Detection, releasing, and exhaust times have no hint: 0 is not a meaningful
detection or release time, and a blank one holds the run.

An input fact's value is JSON text, so a blank (null), a number, a
choice, a flag, and the list of pipe segments are all one column. Its
label is GIVEN when the designer supplied it, typed or in chat, and ASSUMED
when the designer accepted a hint. A job saved by an earlier version can hold
a starting value nobody confirmed; it is taken off the form when the job
opens (unconfirmed_starting_values), so it is never an input either.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any, Iterable, NamedTuple

INPUT_KIND = "input"
BASIS_KIND = "basis"
GIVEN = "GIVEN"
ASSUMED = "ASSUMED"

# Who supplied a value. The fact's source text is built from these.
SOURCE_DESIGNER = "designer"          # typed on the form
SOURCE_CHAT = "chat"                  # stated to the lead in chat, recorded by set_input
SOURCE_DEFAULT = "default"            # a starting value an earlier form put there, not confirmed
SOURCE_SAMPLE = "sample"              # the sample job's data
SOURCE_SAMPLE_UNCONFIRMED = "sample_owner"  # a sample chosen for a test that waits for the owner's confirmation
SOURCE_ACCEPTED = "accepted"          # a hint the designer accepted: recorded ASSUMED
SOURCE_TYPED_HINT = "typed_hint"      # typed by the designer, the same value as a hint the field showed: GIVEN
SOURCE_TEXT = {
    SOURCE_DESIGNER: "zone form",
    SOURCE_TYPED_HINT: "typed from form hint",
    SOURCE_CHAT: "designer, in chat",
    SOURCE_DEFAULT: "zone form (starting value, not confirmed by the designer)",
    SOURCE_SAMPLE: "SAMPLE data",
    SOURCE_SAMPLE_UNCONFIRMED: "SAMPLE data, OWNER TO CONFIRM",
    SOURCE_ACCEPTED: "zone form (starting value the designer accepted; ASSUMED, not a design value)",
}
# A basis field is on the same Inputs tab, but the record has always called its form "job form".
BASIS_SOURCE_TEXT = {
    SOURCE_DESIGNER: "job form",
    SOURCE_TYPED_HINT: "typed from form hint",
    SOURCE_DEFAULT: "job form (starting value, not confirmed by the designer)",
    SOURCE_ACCEPTED: "job form (starting value the designer accepted; ASSUMED, not a design value)",
}
UNCONFIRMED_MARK = "not confirmed by the designer"
# How a reader is told a value is a starting value, beside the value.
UNCONFIRMED_NOTE = "(starting value, not confirmed by the designer)"
ACCEPTED_MARK = "starting value the designer accepted"

SYSTEM_TYPES = ("di", "dry", "wet")
HAZARDS = ("ordinary", "light", "extra")
BASES = ("FM", "NFPA-OH", "NFPA-LH", "NFPA-EH", "NFPA-HP", "NFPA-DU")
MEDIA = ("nitrogen", "air", "unelected")
PRIMES = ("nc_solenoid", "pneumatic_actuator", "unknown")
LENGTH_BASES = ("center_to_center", "cut")
SEGMENT_ROLES = ("branch", "drop", "cross", "main", "feed", "riser")

_TYPED_NUMBER = re.compile(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?:[eE][-+]?\d+)?")

NUMBER = "number"
TEXT = "text"
FLAG = "flag"
CHOICE = "choice"
SEGMENTS = "segments"

# name: (type, choices, the value a new form holds, unit for display). A new form holds nothing.
ZONE_FIELDS: dict[str, tuple] = {
    "zone_id": (TEXT, None, "", ""),
    "system_type": (CHOICE, SYSTEM_TYPES, None, ""),
    "hazard": (CHOICE, HAZARDS, None, ""),
    "supervised": (FLAG, None, None, ""),
    "density_gpm_ft2": (NUMBER, None, None, "gpm/ft2"),
    "base_area_ft2": (NUMBER, None, None, "ft2"),
    "area_increase": (NUMBER, None, None, ""),
    "hose_gpm": (NUMBER, None, None, "gpm"),
    "q_fill_gpm": (NUMBER, None, None, "gpm"),
    "t_detect_s": (NUMBER, None, None, "s"),
    "t_release_s": (NUMBER, None, None, "s"),
    "t_exhaust_s": (NUMBER, None, None, "s"),
    "qod": (FLAG, None, None, ""),
    "delivery_basis": (CHOICE, BASES, None, ""),
    "medium": (CHOICE, MEDIA, None, ""),
    "prime_held_by": (CHOICE, PRIMES, None, ""),
    "failsafe_on_total_power_loss": (FLAG, None, None, ""),
    "supervisory_psi": (NUMBER, None, None, "psi"),
    "manual_station": (FLAG, None, None, ""),
    "length_basis": (CHOICE, LENGTH_BASES, None, ""),
    "fittings_percent": (NUMBER, None, None, "%"),
    "trim_gal": (NUMBER, None, None, "gal"),
    "supervisory_psig": (NUMBER, None, None, "psig"),
    "fill_minutes": (NUMBER, None, None, "min"),
    "segments": (SEGMENTS, None, [], ""),
}
BASIS_FIELDS = ("ahj", "nfpa_13", "nfpa_72", "insurer", "hazard_notes")
# A new job's basis fields start blank too (FA Lead's ruling, 2026-11-12): no edition and no insurer is a
# starting value. The 2025 / 2025 / FM an earlier version put there are in LEGACY_STARTING_VALUES, only to
# recognise them in a job it saved; the editions' hints (HINTS) carry their cites.
INPUT_NAMES = tuple(ZONE_FIELDS) + BASIS_FIELDS
class Hint(NamedTuple):
    """A value the content pack pins for an input, shown beside a blank field. Never an input until accepted.

    cite is the section with its edition, as the pack writes it. source is the
    pack file that holds the pin, and quote a phrase of it that a test finds
    there, so no hint carries a cite the pack does not hold. A hint is always
    shown with its cite and labeled VERIFY.
    """

    value: Any
    note: str
    cite: str
    source: str
    quote: str


_DENSITY = "skills/density-area-dry-increase/SKILL.md"
_DELIVERY = "skills/dry-preaction-water-delivery-screen/SKILL.md"
# The hints, by input. A field with two hints is not filled by Use hints: the designer types the one that applies.
# No hint stands where the pack pins no value with a cite: the fill flow, the supervisory pressures, the
# times, the choices, the yes/no inputs, and the insurer have none.
HINTS: dict[str, tuple[Hint, ...]] = {
    "density_gpm_ft2": (
        Hint(0.20, "ordinary hazard group 2", "NFPA 13-2025 Table 19.2.3.1.1", _DENSITY,
             "OH-2 **0.20 / 1,500** [CODE NFPA 13-2025 Table 19.2.3.1.1"),
    ),
    "base_area_ft2": (
        Hint(1500.0, "ordinary hazard", "NFPA 13-2025 Table 19.2.3.1.1", _DENSITY,
             "OH-1 **0.15 / 1,500**, OH-2 **0.20 / 1,500** [CODE NFPA 13-2025 Table 19.2.3.1.1"),
        Hint(3500.0, "FM, dry or double-interlock", "FM DS 5-32 (January 2026) §2.4.3.3.1.1.A", _DENSITY,
             "| Density 0.2 gpm/ft²; area 2,500 wet / 3,500 dry | §2.4.3.3.1.1.A |"),
    ),
    "area_increase": (
        Hint(0.30, "dry or double-interlock area increase", "NFPA 13-2025 §19.2.3.2.6", _DENSITY,
             "[CODE NFPA 13 2025 §19.2.3.2.6"),
    ),
    "hose_gpm": (
        Hint(250.0, "ordinary hazard hose stream", "NFPA 13-2025 Table 19.2.3.1.2", _DENSITY,
             "[CODE NFPA 13-2025 Table 19.2.3.1.2: OH 250 gpm"),
    ),
    "fill_minutes": (
        Hint(30.0, "time to restore supervisory pressure", "NFPA 13-2025 §8.2.7.3",
             "skills/nitrogen-inerting-and-c-factor-gate/SKILL.md", "Code floor is 30 min [CODE NFPA 13-2025 §8.2.7.3]"),
    ),
    "delivery_basis": (
        Hint("FM", "FM-insured data center, 30 s to the most remote sprinkler", "FM DS 5-32 (January 2026) §2.4.3.2.1.2(D)",
             _DELIVERY, "§2.4.3.2.1.2(D) — 1 most remote, DATA CENTER / every preaction arrangement"),
    ),
    "nfpa_13": (
        Hint("2025", "the pack's delta baseline; an unamended 2024 I-Code adoption enforces 2022", "NFPA 13-2025",
             _DELIVERY, "Delta baseline = **NFPA 13-2025**. Unamended **2024 I-Codes** → **13-2022**."),
    ),
    "nfpa_72": (
        Hint("2025", "the company's design-to edition [PRACTICE]; the enforced edition sets the battery factor",
             "NFPA 72-2025", "skills/fa-code-edition-delta-check/SKILL.md",
             "company practice: design to 72-2025 [PRACTICE]"),
    ),
}
VERIFY = "VERIFY"
# What earlier versions put in a new form, for one purpose only: to recognise that value in a job one of them
# saved, where nobody entered or accepted it (unconfirmed_starting_values). None of these is a hint or an input.
LEGACY_STARTING_VALUES: dict[str, Any] = {
    "system_type": "di", "hazard": "ordinary", "supervised": True, "density_gpm_ft2": 0.20,
    "base_area_ft2": 1500.0, "area_increase": 0.30, "hose_gpm": 250.0, "q_fill_gpm": 600.0, "qod": False,
    "delivery_basis": "FM", "medium": "nitrogen", "prime_held_by": "nc_solenoid",
    "failsafe_on_total_power_loss": False, "supervisory_psi": 15.0, "manual_station": True,
    "length_basis": "center_to_center", "supervisory_psig": 40.0, "fill_minutes": 30.0,
    "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM",
}
# The basis fields whose edition a calculation's cites are held to. Blank, the edition is not pinned.
EDITION_FIELDS = (("nfpa_13", "NFPA 13"), ("nfpa_72", "NFPA 72"))
# Ways a person writes a unit after a number. A number with its own input's unit is that number;
# any other trailing text is refused, so nothing is converted and nothing is guessed.
_UNIT_WORDS = {
    "gpm": ("gpm",),
    "s": ("s", "sec", "secs", "second", "seconds"),
    "psi": ("psi",),
    "psig": ("psig", "psi"),
    "gal": ("gal", "gals", "gallon", "gallons"),
    "min": ("min", "mins", "minute", "minutes"),
    "%": ("%", "percent", "pct"),
    "ft2": ("ft2", "ft²", "sq ft", "sqft", "sf", "square feet"),
    "gpm/ft2": ("gpm/ft2", "gpm/ft²", "gpm/sq ft", "gpm/sf"),
}
# Other words for a choice. A choice is matched without regard to case.
_CHOICE_WORDS = {
    "system_type": {
        "double-interlock": "di", "double interlock": "di", "double-interlock preaction": "di",
        "double interlock preaction": "di", "preaction": "di", "dry pipe": "dry", "dry-pipe": "dry",
        "wet pipe": "wet", "wet-pipe": "wet",
    },
    "medium": {"n2": "nitrogen", "compressed air": "air"},
    "prime_held_by": {
        "solenoid": "nc_solenoid", "nc solenoid": "nc_solenoid", "normally closed solenoid": "nc_solenoid",
        "actuator": "pneumatic_actuator", "pneumatic actuator": "pneumatic_actuator",
    },
    "length_basis": {"center to center": "center_to_center", "c-c": "center_to_center", "cut lengths": "cut"},
}
# What a reader needs to know about an input beyond its name.
_INPUT_NOTES = {
    "area_increase": "a fraction: 0.30 is a 30 percent increase",
    "supervisory_psi": "the low-air supervisory setting",
    "supervisory_psig": "the supervisory gas fill pressure",
    "fill_minutes": "the time allowed to fill to that pressure",
    "t_detect_s": "detection time; owned by the releasing design",
    "t_release_s": "releasing time; owned by the releasing design",
    "segments": "the pipe takeoff, as a list",
}


# The zone form's name for an input and the unit it shows, for a message the designer reads.
FORM_LABELS = {
    "system_type": ("System", ""),
    "hazard": ("Hazard", ""),
    "supervised": ("Supervised waterflow", ""),
    "density_gpm_ft2": ("Density", "gpm/ft²"),
    "base_area_ft2": ("Base area", "ft²"),
    "area_increase": ("Area increase", ""),
    "hose_gpm": ("Hose", "gpm"),
    "q_fill_gpm": ("Fill flow", "gpm"),
    "t_detect_s": ("Detection time", "s"),
    "t_release_s": ("Releasing time", "s"),
    "t_exhaust_s": ("Exhaust time", "s"),
    "qod": ("Quick-opening device", ""),
    "delivery_basis": ("Time basis", ""),
    "failsafe_on_total_power_loss": ("Failsafe on total power loss", ""),
    "manual_station": ("Manual station", ""),
    "length_basis": ("Lengths", ""),
    "supervisory_psig": ("Supervisory fill", "psig"),
    "fill_minutes": ("Fill time", "min"),
}
# What a zone run needs. The kernel refuses a fill flow, a fill pressure, or a fill time of 0. It would
# compute a demand on a density or a base area of 0, but that is not a sprinkler demand, so a run refuses it
# too. Nothing here is an engineering threshold: these are the values that do not describe a zone at all.
POSITIVE = ("q_fill_gpm", "density_gpm_ft2", "base_area_ft2", "supervisory_psig", "fill_minutes")
# These may be 0, which says none on purpose, but not blank: a blank is not an answer, and a run never puts
# a 0 or a starting value in its place.
NOT_BLANK = {
    "area_increase": "Enter it as a fraction (0.30 is a 30 percent increase), or 0 when no increase applies.",
    "hose_gpm": "Enter the hose stream in gpm, or 0 when none is included.",
}
# The detection, releasing, and exhaust times. A blank one is never taken as 0: the delivery rows are then the
# fill time alone and its margin, with no pass or fail. A typed 0 is used and marked ASSUMED-ZERO (optimistic,
# NEEDS PE REVIEW). The times come from the releasing design.
SUB_TIMES = ("t_detect_s", "t_release_s", "t_exhaust_s")
SUBTIMES_MISSING = "sub-times not provided; no pass or fail"
# A choice or a yes/no the run's tools take. Blank, the run holds: no choice is made for the designer. The
# trim medium and the prime holder are not here: blank, they go to the kernel as its own "unelected" and
# "unknown", which say no election was made.
CHOSEN = ("system_type", "hazard", "supervised", "qod", "delivery_basis", "length_basis", "manual_station",
          "failsafe_on_total_power_loss")


class InputError(ValueError):
    """A value an input cannot hold. The message names the input and what it takes."""


def run_problem(name: str, value: Any) -> str:
    """Why a zone run cannot use this value of an input, in the form's words. "" when it can.

    A value that is not a number is said to be one, a blank is named as a
    blank, and nothing is defaulted: the designer decides what goes there.
    """
    label, unit = FORM_LABELS.get(name, (name, unit_of(name) if name in ZONE_FIELDS else ""))
    in_unit = f" {unit}" if unit else ""
    blank = value is None or (isinstance(value, str) and not value.strip())
    if name in CHOSEN:
        if blank:
            return f"{label} is blank. Choose one."
        return ""
    if blank:
        if name in NOT_BLANK:
            return f"{label} is blank. {NOT_BLANK[name]}"
        if name in POSITIVE:
            return f"{label} is blank. Enter it in{in_unit}." if unit else f"{label} is blank."
        return ""
    if isinstance(value, bool):
        return f"{label} must be a number."
    try:
        number = float(str(value).replace(",", "")) if isinstance(value, str) else float(value)
    except (TypeError, ValueError):
        return f"{label} must be a number."
    if not math.isfinite(number):
        return f"{label} must be a finite number."
    if name in POSITIVE and number <= 0:
        return f"{label} must be greater than 0{in_unit}."
    if (name in NOT_BLANK or name in SUB_TIMES) and number < 0:
        return f"{label} cannot be negative."
    return ""


def kind_of(name: str) -> str:
    """The fact kind an input is stored under."""
    if name in BASIS_FIELDS:
        return BASIS_KIND
    if name in ZONE_FIELDS:
        return INPUT_KIND
    raise InputError(f"{name!r} is not a project input. Inputs: " + ", ".join(INPUT_NAMES))


def unit_of(name: str) -> str:
    return ZONE_FIELDS[name][3] if name in ZONE_FIELDS else ""


def describe() -> str:
    """Every input with what it takes, for a tool description: its choices, its unit, and a note where one helps."""
    parts = []
    for name, (kind, choices, _default, unit) in ZONE_FIELDS.items():
        if kind == CHOICE:
            takes = " | ".join(choices)
        elif kind == NUMBER:
            takes = f"number, {unit}" if unit else "number"
        elif kind == FLAG:
            takes = "true | false"
        elif kind == SEGMENTS:
            takes = "list"
        else:
            takes = "text"
        note = _INPUT_NOTES.get(name)
        parts.append(f"{name} ({takes}{'; ' + note if note else ''})")
    parts.extend(f"{name} (text)" for name in BASIS_FIELDS)
    return "; ".join(parts)


def _number(name: str, value: Any) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise InputError(f"{name} takes a number")
    if isinstance(value, str):
        value = _bare_number(name, value)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} takes a number, not {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{name} takes a finite number")
    return number


def _bare_number(name: str, text: str) -> str:
    """A typed number without its thousands commas and without its own unit.

    "1,500 ft2" for an area is 1500. A number followed by anything else, such
    as a percent sign on an input that is a fraction, is refused with what the
    input takes, so the value is never converted here.
    """
    raw = text.strip()
    found = _TYPED_NUMBER.match(raw)
    if not found:
        return raw
    tail = raw[found.end():].strip().lower().rstrip(".")
    unit = unit_of(name)
    if tail and tail not in _UNIT_WORDS.get(unit, ()):
        takes = f"a number in {unit}" if unit else "a bare number"
        note = _INPUT_NOTES.get(name)
        raise InputError(f"{name} takes {takes}{' (' + note + ')' if note else ''}, not {text!r}")
    return found.group(0).replace(",", "")


def _flag(name: str, value: Any) -> bool | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "yes", "on", "1"):
        return True
    if isinstance(value, str) and value.strip().lower() in ("false", "no", "off", "0"):
        return False
    raise InputError(f"{name} takes true or false")


def _segment(index: int, row: Any) -> dict:
    if not isinstance(row, dict):
        raise InputError(f"segment {index} must be an object with a size and a length")
    length = _number(f"segment {index} length_ft", row.get("length_ft", row.get("length")))
    if length is None or length <= 0:
        raise InputError(f"segment {index} needs a length in feet greater than 0")
    out: dict[str, Any] = {
        "role": str(row.get("role") or "").strip(),
        "nps": row.get("nps") if row.get("nps") not in ("", None) else None,
        "schedule": str(row.get("schedule") or "").strip(),
        "length_ft": length,
    }
    if out["role"] and out["role"] not in SEGMENT_ROLES:
        raise InputError(f"segment {index} role must be one of: " + ", ".join(SEGMENT_ROLES))
    diameter = _number(f"segment {index} d_in", row.get("d_in"))
    if diameter is not None:
        out["d_in"] = diameter
    if out["nps"] is None and diameter is None:
        raise InputError(f"segment {index} needs a nominal size or an inside diameter")
    if out["nps"] is not None:
        out["nps"] = str(out["nps"]).strip()
    return out


def coerce(name: str, value: Any) -> Any:
    """Check one input value and return it in the form the job file keeps.

    A blank stays None; nothing is defaulted here. Raises InputError with
    the input's name when the value is not one the input can hold.
    """
    if name in BASIS_FIELDS:
        return "" if value is None else str(value).strip()
    if name not in ZONE_FIELDS:
        raise InputError(f"{name!r} is not a project input. Inputs: " + ", ".join(INPUT_NAMES))
    kind, choices, _default, _unit = ZONE_FIELDS[name]
    if kind == NUMBER:
        number = _number(name, value)
        if number is not None and number < 0:
            raise InputError(f"{name} cannot be negative")
        return number
    if kind == FLAG:
        return _flag(name, value)
    if kind == CHOICE:
        text = "" if value is None else str(value).strip()
        if not text:
            return None
        if text in choices:
            return text
        folded = " ".join(text.lower().split())
        by_case = {choice.lower(): choice for choice in choices}
        found = by_case.get(folded) or _CHOICE_WORDS.get(name, {}).get(folded)
        if found is None:
            raise InputError(f"{name} must be one of: " + ", ".join(choices))
        return found
    if kind == SEGMENTS:
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise InputError("segments takes a list of pipe segments")
        return [_segment(index, row) for index, row in enumerate(value, start=1)]
    return "" if value is None else str(value).strip()


def canonical(name: str, value: Any) -> Any:
    """A value in the one shape used to compare and store it. A bad value is kept as its text."""
    try:
        cooked = coerce(name, value)
    except InputError:
        return None if value is None else str(value)
    if name in ZONE_FIELDS and ZONE_FIELDS[name][0] == SEGMENTS:
        return [_segment_key(row) for row in cooked]
    return cooked


def _segment_key(row: dict) -> dict:
    """A segment as it is stored: its length, its nominal size, and its diameter when one is given.

    The diameter the form resolves from the calc pack is display. It is left
    out of the stored value, so the same pipe before and after the form looks
    its diameter up is one value and not a change. A diameter typed with no
    nominal size is the only description of that pipe, and is kept.
    """
    key: dict[str, Any] = {"length_ft": round(float(row["length_ft"]), 6)}
    if row.get("nps") not in (None, ""):
        key["nps"] = str(row.get("nps"))
        key["schedule"] = str(row.get("schedule") or "")
        key["role"] = str(row.get("role") or "")
    elif row.get("d_in") is not None:
        key["d_in"] = round(float(row["d_in"]), 3)
    return key


def encode(name: str, value: Any) -> str:
    """JSON text for the fact's value column. Never empty: a blank is null."""
    return json.dumps(canonical(name, value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def decode(text: Any) -> Any:
    if not isinstance(text, str):
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def same(left: Any, right: Any) -> bool:
    """Whether two input values are the same value. 600 and "600.0" are; a blank and "" are."""
    if _is_blank(left) and _is_blank(right):
        return True
    if _is_blank(left) or _is_blank(right):
        return False
    if isinstance(left, bool) or isinstance(right, bool):
        return _as_flag(left) is _as_flag(right) and _as_flag(left) is not None
    a, b = _as_number(left), _as_number(right)
    if a is not None and b is not None:
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_segment(x, y) for x, y in zip(left, right))
    return str(left).strip() == str(right).strip()


def same_segment(left: Any, right: Any) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return left == right
    a_len, b_len = _as_number(left.get("length_ft")), _as_number(right.get("length_ft"))
    if a_len is None or b_len is None or not math.isclose(a_len, b_len, rel_tol=1e-9, abs_tol=1e-6):
        return False
    a_d, b_d = _as_number(left.get("d_in")), _as_number(right.get("d_in"))
    if a_d is not None and b_d is not None:
        return math.isclose(a_d, b_d, abs_tol=5e-4)
    return str(left.get("nps") or "") == str(right.get("nps") or "") and \
        str(left.get("schedule") or "") == str(right.get("schedule") or "")


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _as_flag(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    return None


def default_of(name: str) -> Any:
    """The value a new form holds for this input: blank (None), "" for a text field, [] for the segments."""
    if name in ZONE_FIELDS:
        return ZONE_FIELDS[name][2]
    return ""


def hints_of(name: str) -> tuple[Hint, ...]:
    """Every hint a blank field shows. Empty when it has none."""
    return HINTS.get(name, ())


def hint_of(name: str) -> Any:
    """The value Use hints puts in a blank field: its one hint's, or None when it has none or more than one."""
    found = hints_of(name)
    return found[0].value if len(found) == 1 else None


def _hint_figure(name: str, value: Any, unit: str = "") -> str:
    if isinstance(value, float) and name in ("density_gpm_ft2", "area_increase"):
        text = f"{value:.2f}"
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        text = f"{value:,.0f}" if float(value).is_integer() else f"{value:g}"
    else:
        text = str(value)
    return f"{text} {unit}".strip()


def typed_source(name: str, value: Any) -> str:
    """Who supplied a value the designer typed: typed from a form hint when it is one of the field's hint values.

    It is the designer's value either way, and GIVEN: typing a figure clears
    the ASSUMED an accepted hint carries. The source only says where the
    figure came from.
    """
    if _is_blank(value):
        return SOURCE_DESIGNER
    for hint in hints_of(name):
        if same(canonical(name, value), canonical(name, hint.value)):
            return SOURCE_TYPED_HINT
    return SOURCE_DESIGNER


def hint_text(name: str, unit: str | None = None) -> str:
    """Every hint of an input as the form shows it: the value, what it is for, its cite and edition, and VERIFY."""
    unit = unit_of(name) if unit is None else unit
    return " · ".join(f"{_hint_figure(name, hint.value, unit)} ({hint.note}; {hint.cite}) {VERIFY}"
                      for hint in hints_of(name))


def provenance(project: dict | None, name: str, value: Any) -> str:
    """Who supplied this value: the job's own note of it, or what its value implies.

    A job keeps a note per input once the designer types it or accepts its
    hint, the lead sets it, or a sample fills it. With no note, a value that
    is an earlier form's starting value (its hint now) was not supplied by
    anyone; any other value was typed.
    """
    noted = ((project or {}).get("given") or {}).get(name)
    if noted in SOURCE_TEXT:
        return noted
    start = LEGACY_STARTING_VALUES.get(name)
    if start is not None and not _is_blank(value) and same(canonical(name, value), canonical(name, start)):
        return SOURCE_DEFAULT
    return SOURCE_DESIGNER


def unconfirmed_basis(project: dict | None, basis: dict | None = None) -> list[str]:
    """The basis fields that hold a starting value the designer has not confirmed. A blank field is not one.

    basis is the basis to read, the job's own when None (a run reads the
    basis it ran on). Each is judged by provenance, so a value the designer
    typed or stated in chat is theirs even where it equals the starting value.
    """
    if basis is None:
        basis = (project or {}).get("basis") if isinstance((project or {}).get("basis"), dict) else {}
    return [name for name in BASIS_FIELDS
            if str((basis or {}).get(name) or "").strip()
            and provenance(project, name, (basis or {}).get(name)) == SOURCE_DEFAULT]


def label_for(source: str, given: str = GIVEN) -> str:
    """The record's label for an input from this source: ASSUMED for an accepted hint, else the field's own."""
    return ASSUMED if source == SOURCE_ACCEPTED else given


def unconfirmed_starting_values(project: dict | None) -> list[str]:
    """Inputs of a job an earlier version saved that still hold that form's starting value, with no note.

    Nobody entered or accepted them, so they are not the job's inputs. The
    desk takes them off the form when the job opens and shows their hints.
    """
    project = project or {}
    found: list[str] = []
    di = project.get("di") if isinstance(project.get("di"), dict) else {}
    for name in ZONE_FIELDS:
        if name in di and provenance(project, name, di[name]) == SOURCE_DEFAULT:
            found.append(name)
    basis = project.get("basis") if isinstance(project.get("basis"), dict) else {}
    for name in BASIS_FIELDS:
        if name in basis and provenance(project, name, basis[name]) == SOURCE_DEFAULT:
            found.append(name)
    return found


def unpinned_editions(basis: dict | None, assumed: Iterable[str] = ()) -> list[str]:
    """The standards whose edition the job does not pin: blank, missing, not one year, or ASSUMED.

    An edition the designer took from its hint is ASSUMED, not pinned: accepting a hint clears no HOLD.
    """
    basis = basis if isinstance(basis, dict) else {}
    assumed = set(assumed)
    years = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
    found = []
    for field, document in EDITION_FIELDS:
        if field in assumed or len(set(years.findall(str(basis.get(field) or "")))) != 1:
            found.append(document)
    return found


EDITION_NOT_PINNED = "edition not pinned"


def edition_hold_lines(basis: dict | None, assumed: Iterable[str] = (), unconfirmed: Iterable[str] = ()) -> list[str]:
    """The HOLD for each edition the job does not pin. Nothing that depends on it is given until it is.

    assumed names the fields taken from a hint, and unconfirmed the fields an
    older record holds as an earlier form's starting value: neither pins.
    """
    basis = basis if isinstance(basis, dict) else {}
    assumed = set(assumed)
    unconfirmed = set(unconfirmed)
    lines = []
    for field, document in EDITION_FIELDS:
        if document not in unpinned_editions(basis, assumed | unconfirmed):
            continue
        value = str(basis.get(field) or "").strip()
        if field in assumed:
            states = f"{value or 'Its value'} is ASSUMED, a hint the designer used, not an edition the designer stated"
        elif field in unconfirmed and value:
            states = f"{value} is an earlier form's starting value, not confirmed by the designer"
        else:
            states = f"The job states no {document} edition"
        lines.append(
            f"HOLD: {document} {EDITION_NOT_PINNED}. {states}, so a figure or a cite that depends on the edition "
            "(a battery factor, a section number) waits until the designer types one. No edition is taken for it."
        )
    return lines


def accepted_inputs(project: dict | None) -> set[str]:
    """The inputs of a job the designer took from a hint and has not typed over since: recorded ASSUMED."""
    given = (project or {}).get("given") if isinstance((project or {}).get("given"), dict) else {}
    return {name for name, source in given.items() if source == SOURCE_ACCEPTED}


def assumed_lines(names: Iterable[str], values: dict | None = None) -> list[str]:
    """One line for each ASSUMED input that is not an edition (an edition is a HOLD of its own).

    It names the input, its value, and the cite of the hint it came from, and
    it stays until the designer types a value.
    """
    editions = {field for field, _document in EDITION_FIELDS}
    values = values or {}
    lines = []
    for name in sorted(set(names) - editions, key=lambda item: INPUT_NAMES.index(item) if item in INPUT_NAMES else 999):
        cites = "; ".join(hint.cite for hint in hints_of(name)) or "no cite"
        shown = show(name, values[name]) if name in values else "its value"
        lines.append(
            f"{name} ASSUMED: {shown} is a hint the designer used ({cites}, {VERIFY}), not a design value. It stays "
            "ASSUMED until the designer types a value."
        )
    return lines


def changed_since(run: dict | None, di: dict | None, basis: dict | None) -> list[str]:
    """The inputs that differ between a finished zone run and the form as it is now.

    A run keeps the zone and the basis it ran on. Empty when there is no run
    or nothing moved. The tables and the Section export are that run's, so a
    name here means they no longer describe the form.
    """
    if not isinstance(run, dict) or not isinstance(run.get("inputs"), dict):
        return []
    ran_on = run.get("inputs") or {}
    ran_basis = run.get("basis") if isinstance(run.get("basis"), dict) else {}
    now = di or {}
    changed = []
    for name in ZONE_FIELDS:
        before = ran_on.get(name, default_of(name))
        after = now.get(name, default_of(name))
        if not same(canonical(name, before), canonical(name, after)):
            changed.append(name)
    for name in BASIS_FIELDS:
        if str(ran_basis.get(name) or "").strip() != str((basis or {}).get(name) or "").strip():
            changed.append(name)
    return changed


def source_text(source: str, name: str = "") -> str:
    """The fact's source text for who supplied an input. name picks the basis form's words for a basis field."""
    source = source or SOURCE_DESIGNER
    if name in BASIS_FIELDS and source in BASIS_SOURCE_TEXT:
        return BASIS_SOURCE_TEXT[source]
    return SOURCE_TEXT.get(source, source)


def note_given(project: dict, names, source: str) -> None:
    """Record on the job who supplied these inputs."""
    given = project.setdefault("given", {})
    for name in names:
        if name in ZONE_FIELDS or name in BASIS_FIELDS:
            given[name] = source


def zone_values(project: dict | None) -> dict:
    """The zone inputs of a job, by name, in the order the form shows them. Unknown keys are left out."""
    di = (project or {}).get("di") if isinstance((project or {}).get("di"), dict) else {}
    if not di:
        return {}
    return {name: di.get(name, default_of(name)) for name in ZONE_FIELDS}


def show(name: str, value: Any) -> str:
    """One input value as a designer reads it. The value is the decoded one, not the stored JSON text."""
    if name == "segments":
        rows = value if isinstance(value, list) else []
        if not rows:
            return "none"
        return f"{len(rows)} segment{'s' if len(rows) != 1 else ''}: " + "; ".join(show_segment(row) for row in rows)
    if _is_blank(value):
        return "blank"
    if isinstance(value, bool):
        return "yes" if value else "no"
    number = _as_number(value) if name in ZONE_FIELDS and ZONE_FIELDS[name][0] == NUMBER else None
    if number is not None:
        unit = unit_of(name)
        return f"{number:g}{' ' + unit if unit else ''}"
    return str(value)


def show_segment(row: Any) -> str:
    if not isinstance(row, dict):
        return str(row)
    length = _as_number(row.get("length_ft"))
    size = f"{row.get('nps')} in" if row.get("nps") not in (None, "") else ""
    if row.get("d_in") is not None and not size:
        size = f"ID {float(row['d_in']):.3f} in"
    bits = [f"{length:g} ft" if length is not None else "", size, str(row.get("schedule") or ""), str(row.get("role") or "")]
    return " ".join(bit for bit in bits if bit)
