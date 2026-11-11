"""A figure as a number and the kind of unit it carries, and where one may be found.

The trace check and the reply audit both ask the same question of a figure
in a sentence: do the rows it should have come from hold that number? Asked
of the number alone, 900 gpm is found whenever a 900 ft pipe is on the
record. This module asks it of the pair.

A quantity is (number, unit class). The class comes from the unit written
after the number in prose (gal, gpm, psi, scfm, s, min, ft2, pct), or from
the name of the field a calc record or a project input keeps the number in
(zone_gal, t_total_s, q_fill_gpm, length_ft). A number with no unit the
module knows has the class None.

The rule, in has(): a figure with a unit is found where the same number is
held with the same class, or with no class at all. It is not found where
the number is held only with a different class. So a length never backs a
flow, and a number in a sentence that names no unit still backs anything,
because nothing says what it is.

This is still matching, not engineering. It does not convert units, it does
not know that two figures describe the same thing, and it says nothing
about whether the figure applies to the claim around it. It narrows what
"found" means; it does not make "found" mean verified.
"""

from __future__ import annotations

import math
import re
from typing import Any

# Units a claim or a reply may carry. The trace check and the reply audit look these up.
_CLAIM_UNITS = {
    "gallons": "gal", "gallon": "gal", "gal": "gal",
    "gpm": "gpm",
    "psig": "psi", "psi": "psi",
    "scfm": "scfm",
    "seconds": "s", "second": "s", "sec": "s", "s": "s",
    "minutes": "min", "minute": "min", "min": "min",
    "ft2": "ft2", "ft²": "ft2", "sqft": "ft2",
    "percent": "pct", "%": "pct",
}
# Units that mark a number as something else. A claim never carries these; a source may.
_OTHER_UNITS = (
    r"ft|feet|foot|in\.|inch(?:es)?|V|kV|VAC|VDC|A|mA|Ah|kW|MW|kVA|Hz|dB|dBA|°F|°C|mm|cm|m|L|"
    r"hours?|hr|days?|years?|rows?|zones?|sprinklers?|heads?|detectors?|ohms?|AWG|cd"
)
FIGURE = re.compile(
    r"(?<![\w.§-])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(gallons?|gal|gpm|psig|psi|scfm|seconds?|sec|s|minutes?|min|ft2|ft²|sq\s*ft|percent|%)(?![\w²])",
    re.IGNORECASE,
)
_OTHER = re.compile(
    r"(?<![\w.§-])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:" + _OTHER_UNITS + r")(?![\w²])"
)
_ANY_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])")
OTHER = "other"
# A field name's unit, read from its parts: zone_gal, t_total_s, v_max_gal_at_limit, scfm_gauge_basis.
_NAME_UNITS = {
    "gal": "gal", "gallons": "gal", "gpm": "gpm", "psi": "psi", "psig": "psi", "scfm": "scfm",
    "s": "s", "sec": "s", "seconds": "s", "min": "min", "minutes": "min", "ft2": "ft2",
    "percent": "pct", "pct": "pct",
    "ft": OTHER, "in": OTHER, "ft3": OTHER, "nps": OTHER, "count": OTHER, "rows": OTHER, "c": OTHER,
}
Quantity = tuple[str, "str | None"]


def normal(number: str) -> str:
    """A number as text, so 38,400 and 38400.0 and 38400 compare equal."""
    text = str(number).replace(",", "")
    try:
        value = float(text)
    except ValueError:
        return text
    return f"{value:.10g}"


def unit_class(unit: str | None) -> str | None:
    """The class of a unit as a claim writes it. None for a unit this module does not know."""
    return _CLAIM_UNITS.get(re.sub(r"\s+", "", str(unit or "")).lower())


def name_class(name: str | None) -> str | None:
    """The class a field name gives its number, or None when the name does not say.

    A name with two units in it (density_gpm_ft2) is a compound and says nothing.
    """
    found = {_NAME_UNITS[part] for part in re.split(r"[^a-z0-9]+", str(name or "").lower()) if part in _NAME_UNITS}
    return next(iter(found)) if len(found) == 1 else None


def in_text(text: str | None) -> set[Quantity]:
    """Every number in prose with the class of the unit written after it, None where there is none."""
    text = str(text or "")
    found: set[Quantity] = set()
    classed: set[int] = set()
    for match in FIGURE.finditer(text):
        found.add((normal(match.group(1)), unit_class(match.group(2))))
        classed.add(match.start(1))
    for match in _OTHER.finditer(text):
        if match.start(1) not in classed:
            found.add((normal(match.group(1)), OTHER))
            classed.add(match.start(1))
    for match in _ANY_NUMBER.finditer(text):
        if match.start(1) not in classed:
            found.add((normal(match.group(1)), None))
    return found


def _forms(value: float, loose: bool) -> set[str]:
    """A stored number as a sentence would print it.

    Strict, for a claim held to the rows it cites: one decimal, the short
    form, a whole number only when it is one, and two decimals for a small
    rate. Loose, for a reply read against everything the lead could have
    read: also rounded to a whole number and to two decimals.
    """
    if not math.isfinite(float(value)):
        return set()
    magnitude = abs(float(value))
    forms = {f"{magnitude:.1f}", f"{magnitude:g}"}
    if magnitude.is_integer():
        forms.add(str(int(magnitude)))
    elif magnitude < 20:
        forms.add(f"{magnitude:.2f}")
    if loose:
        forms |= {repr(magnitude), f"{magnitude:.0f}", f"{magnitude:.2f}"}
    return {normal(form) for form in forms}


def _plain_number(text: str) -> float | None:
    try:
        return float(text.strip().replace(",", ""))
    except ValueError:
        return None


def in_value(value: Any, name: str | None = None, *, prose: Any = None, strings: bool = True,
             loose: bool = False) -> set[Quantity]:
    """Every number in a stored value, each with the class of the field it sits in.

    A string inside the value is prose and is read as prose, unless strings
    is False (a calc record's notes and formulas are not its figures). A
    string that is only a number is that number. prose, when given, cleans a
    string first (the caller's own cite stripping).
    """
    found: set[Quantity] = set()

    def walk(item: Any, key: str | None) -> None:
        if isinstance(item, bool) or item is None:
            return
        if isinstance(item, (int, float)):
            cls = name_class(key)
            found.update((form, cls) for form in _forms(item, loose))
        elif isinstance(item, str):
            number = _plain_number(item)
            if number is not None:
                cls = name_class(key)
                found.update((form, cls) for form in _forms(number, loose))
            elif strings:
                found.update(in_text(prose(item) if prose is not None else item))
        elif isinstance(item, dict):
            for inner, child in item.items():
                # A list of rows keeps the class of the field each number is in; a bare list keeps its own name's.
                walk(child, str(inner))
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child, key)

    walk(value, name)
    return found


def has(number: str, unit: str | None, have: set[Quantity]) -> bool:
    """Whether a figure is held: the same number with the same class, or with no class at all."""
    cls = unit_class(unit)
    number = normal(number)
    if (number, cls) in have or (number, None) in have:
        return True
    if cls == "pct":
        # A row may hold the same share as a fraction: 30 percent is 0.3.
        try:
            share = normal(str(float(number) / 100.0))
        except ValueError:
            return False
        return (share, "pct") in have or (share, None) in have
    return False


def numbers(have: set[Quantity]) -> list[str]:
    """The numbers alone, sorted, for a row that is printed."""
    return sorted({number for number, _cls in have}, key=lambda item: (len(item), item))
