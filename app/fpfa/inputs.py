"""Project inputs: what the designer gave the team to work from.

The zone form and the basis fields are the job's inputs. They are the
shared assumptions every agent reasons from, so they live on the project
record as facts (kind "input" for the zone, kind "basis" for the five
basis fields). The form is one way to edit them; telling the lead in chat
is the other (the lead's set_input tool). When a value changes, the old
fact row is superseded, and every calculation that used the old value is
out of date until it is run again (fpfa.coherence).

This module is the one description of those inputs: their names, their
types, the value a blank form starts with, and how a value is checked and
compared. It holds no method. It does not compute or default an
engineering figure; a blank stays blank.

An input fact's value is JSON text, so a blank (null), a number, a
choice, a flag, and the list of pipe segments are all one column. Its
label is GIVEN: the designer supplied it. It is not calculated, not
ASSUMED, and not a judgment the tools did not return. Where the value is
only the form's starting value and the designer has not confirmed it, the
fact's source says so; the label does not change.
"""

from __future__ import annotations

import json
import math
from typing import Any

INPUT_KIND = "input"
BASIS_KIND = "basis"
GIVEN = "GIVEN"

# Who supplied a value. The fact's source text is built from these.
SOURCE_DESIGNER = "designer"          # typed on the form
SOURCE_CHAT = "chat"                  # stated to the lead in chat, recorded by set_input
SOURCE_DEFAULT = "default"            # the form's starting value, not confirmed
SOURCE_SAMPLE = "sample"              # the sample job's data
SOURCE_TEXT = {
    SOURCE_DESIGNER: "zone form",
    SOURCE_CHAT: "designer, in chat",
    SOURCE_DEFAULT: "zone form (starting value, not confirmed by the designer)",
    SOURCE_SAMPLE: "sample data",
}
UNCONFIRMED_MARK = "not confirmed by the designer"

SYSTEM_TYPES = ("di", "dry", "wet")
HAZARDS = ("ordinary", "light", "extra")
BASES = ("FM", "NFPA-OH", "NFPA-LH", "NFPA-EH", "NFPA-HP", "NFPA-DU")
MEDIA = ("nitrogen", "air", "unelected")
PRIMES = ("nc_solenoid", "pneumatic_actuator", "unknown")
LENGTH_BASES = ("center_to_center", "cut")
SEGMENT_ROLES = ("branch", "drop", "cross", "main", "feed", "riser")

NUMBER = "number"
TEXT = "text"
FLAG = "flag"
CHOICE = "choice"
SEGMENTS = "segments"

# name: (type, choices, the value a blank form holds, unit for display)
ZONE_FIELDS: dict[str, tuple] = {
    "zone_id": (TEXT, None, "", ""),
    "system_type": (CHOICE, SYSTEM_TYPES, "di", ""),
    "hazard": (CHOICE, HAZARDS, "ordinary", ""),
    "supervised": (FLAG, None, True, ""),
    "density_gpm_ft2": (NUMBER, None, 0.20, "gpm/ft2"),
    "base_area_ft2": (NUMBER, None, 1500.0, "ft2"),
    "area_increase": (NUMBER, None, 0.30, ""),
    "hose_gpm": (NUMBER, None, 250.0, "gpm"),
    "q_fill_gpm": (NUMBER, None, 600.0, "gpm"),
    "t_detect_s": (NUMBER, None, 0.0, "s"),
    "t_release_s": (NUMBER, None, 0.0, "s"),
    "t_exhaust_s": (NUMBER, None, 0.0, "s"),
    "qod": (FLAG, None, False, ""),
    "delivery_basis": (CHOICE, BASES, "FM", ""),
    "medium": (CHOICE, MEDIA, "nitrogen", ""),
    "prime_held_by": (CHOICE, PRIMES, "nc_solenoid", ""),
    "failsafe_on_total_power_loss": (FLAG, None, False, ""),
    "supervisory_psi": (NUMBER, None, 15.0, "psi"),
    "manual_station": (FLAG, None, True, ""),
    "length_basis": (CHOICE, LENGTH_BASES, "center_to_center", ""),
    "fittings_percent": (NUMBER, None, None, "%"),
    "trim_gal": (NUMBER, None, None, "gal"),
    "supervisory_psig": (NUMBER, None, 40.0, "psig"),
    "fill_minutes": (NUMBER, None, 30.0, "min"),
    "segments": (SEGMENTS, None, [], ""),
}
BASIS_FIELDS = ("ahj", "nfpa_13", "nfpa_72", "insurer", "hazard_notes")
INPUT_NAMES = tuple(ZONE_FIELDS) + BASIS_FIELDS


class InputError(ValueError):
    """A value an input cannot hold. The message names the input and what it takes."""


def kind_of(name: str) -> str:
    """The fact kind an input is stored under."""
    if name in BASIS_FIELDS:
        return BASIS_KIND
    if name in ZONE_FIELDS:
        return INPUT_KIND
    raise InputError(f"{name!r} is not a project input. Inputs: " + ", ".join(INPUT_NAMES))


def unit_of(name: str) -> str:
    return ZONE_FIELDS[name][3] if name in ZONE_FIELDS else ""


def _number(name: str, value: Any) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise InputError(f"{name} takes a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} takes a number, not {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{name} takes a finite number")
    return number


def _flag(name: str, value: Any) -> bool:
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
        if text not in choices:
            raise InputError(f"{name} must be one of: " + ", ".join(choices))
        return text
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
    """The value a blank form holds for this input."""
    if name in ZONE_FIELDS:
        return ZONE_FIELDS[name][2]
    return {"nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM"}.get(name, "")


def provenance(project: dict | None, name: str, value: Any) -> str:
    """Who supplied this value: the job's own note of it, or what its value implies.

    A job keeps a note per input once the designer types it, the lead sets it,
    or a sample fills it. With no note, a value that is still the form's
    starting value was not supplied by anyone; any other value was typed.
    """
    noted = ((project or {}).get("given") or {}).get(name)
    if noted in SOURCE_TEXT:
        return noted
    if same(canonical(name, value), canonical(name, default_of(name))):
        return SOURCE_DEFAULT
    return SOURCE_DESIGNER


def source_text(source: str) -> str:
    return SOURCE_TEXT.get(source, source or SOURCE_TEXT[SOURCE_DESIGNER])


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
