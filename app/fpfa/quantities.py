"""A figure as a number and the kind of unit it carries, and where one may be found.

The trace check and the reply audit both ask the same question of a figure
in a sentence: do the rows it should have come from hold that number? Asked
of the number alone, 900 gpm is found whenever a 900 ft pipe is on the
record. This module asks it of the pair.

A quantity is (number, unit class). The class comes from the unit written
after the number in prose, or from the name of the field a calc record or a
project input keeps the number in (zone_gal, t_total_s, q_fill_gpm,
length_ft). A number with no unit the module knows has the class None.

Two sets of units:

- The eight a reply or a claim has always carried: gal, gpm, psi, scfm, s,
  min, ft2, pct (FIGURE). The reply audit reads these.
- Every other unit the module knows, each with a class of its own: feet,
  inches, amp-hours, volts, amps, litres per minute, hours, a count of rows
  or zones, and so on (_FAMILIES). A source has always been read for these.
  The trace check now reads them in a claim too (claim_figures), so a
  99 Ah claim is not backed by a 99 ft fact. Before, they all shared one
  class and a claim's figure in one of them was not read at all.

A unit written as a ratio that the module does not know (gal/hr, psi/ft)
gets a class of its own from its spelling. It is not "no unit": 600 of
something per hour does not back 600 gpm.

A figure stored as {"value": ..., "unit": ...}, the way a unit conversion
records its given and its result, has the class of that unit. The reply
audit reads the eight units and the SI flow, area, volume, pressure, and
density units (reply_figures), so a figure a reply gives in L/min has to be
on the record in L/min.

The rule, in holds(): a figure with a class is found where the same number
is held with the same class, or with no class at all. It is not found where
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
# Every other unit the module knows, by class, as it is spelled. Case counts: A is amps and a is a word.
# "in." needs its full stop, because "in" is a word too.
_FAMILIES: dict[str, tuple[str, ...]] = {
    "ft": ("ft", "feet", "foot"),
    "in": ("in.", "inch", "inches"),
    "mm": ("mm",), "cm": ("cm",), "m": ("m",),
    "v": ("V", "VAC", "VDC"), "kv": ("kV",),
    "a": ("A",), "ma": ("mA",), "ah": ("Ah",),
    "kw": ("kW",), "mw": ("MW",), "kva": ("kVA",),
    "hz": ("Hz",), "db": ("dB", "dBA"), "degf": ("°F",), "degc": ("°C",),
    "l": ("L",), "lpm": ("lpm", "LPM", "L/min", "l/min"),
    # The SI units a metric job gives its figures in (fpfa.units converts them). Each is its own class, so
    # 139 m² is not backed by 139 ft², and 12.2 mm/min is a density, not a length.
    "m2": ("m2", "m²", "sq m"), "m3": ("m3", "m³"), "m3h": ("m3/h", "m³/h", "m3/hr", "m³/hr"),
    "lps": ("L/s", "l/s"), "mmmin": ("mm/min", "L/min/m2", "L/min/m²", "lpm/m2", "lpm/m²"),
    "kpa": ("kPa",), "bar": ("bar",), "cfm": ("cfm", "CFM"),
    "h": ("hours", "hour", "hr"), "d": ("days", "day"), "y": ("years", "year"),
    "count": ("rows", "row", "zones", "zone", "sprinklers", "sprinkler", "heads", "head", "detectors", "detector"),
    "ohm": ("ohms", "ohm"), "awg": ("AWG",), "cd": ("cd",),
}
_FAMILY_OF = {spelling: cls for cls, spellings in _FAMILIES.items() for spelling in spellings}
_NUMBER = r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
_CORE_UNITS = r"(gallons?|gal|gpm|psig|psi|scfm|seconds?|sec|s|minutes?|min|ft2|ft²|sq\s*ft|percent|%)"
FIGURE = re.compile(r"(?<![\w.§-])" + _NUMBER + r"\s*" + _CORE_UNITS + r"(?![\w²])", re.IGNORECASE)
# The longest spelling first, so L/min is not read as L.
_FAMILY = re.compile(
    r"(?<![\w.§-])" + _NUMBER + r"\s*(" + "|".join(re.escape(item) for item in sorted(_FAMILY_OF, key=len, reverse=True))
    + r")(?![\w²])"
)
# A ratio of two unit-like words after a number that no table above knows: gal/hr, psi/ft, m3/h.
_RATIO = re.compile(r"(?<![\w.§-])" + _NUMBER + r"\s*([A-Za-zµ°][A-Za-z]{0,5}\d?/[A-Za-z]{1,6}\d?)(?![\w²])")
_ANY_NUMBER = re.compile(r"(?<![\w.])" + _NUMBER + r"(?![\d])")
# Spellings a sentence may use for a unit the tables hold under another one.
_RESPELL = (
    (re.compile(r"(?i)\bg\.\s?p\.\s?m\.?(?![\w])"), "gpm"),
    (re.compile(r"(?i)\bs\.\s?c\.\s?f\.\s?m\.?(?![\w])"), "scfm"),
    (re.compile(r"(?i)\bp\.\s?s\.\s?i\.\s?g\.?(?![\w])"), "psig"),
    (re.compile(r"(?i)\bp\.\s?s\.\s?i\.?(?![\w])"), "psi"),
    (re.compile(r"(?i)\bgal(?:lons?)?\s?/\s?min(?:ute)?\b"), "gpm"),
    (re.compile(r"(?i)\bgal(?:lons?)?\s+per\s+min(?:ute)?\b"), "gpm"),
    (re.compile(r"(?i)\blit(?:er|re)s?\s?(?:/|per)\s?min(?:ute)?\b"), "L/min"),
)
# A field name's unit, read from its parts: zone_gal, t_total_s, v_max_gal_at_limit, scfm_gauge_basis.
# Only parts the kernels really use as a unit: a trailing _v there is a value, not volts, and _m is "per m".
_NAME_UNITS = {
    "gal": "gal", "gallons": "gal", "gpm": "gpm", "psi": "psi", "psig": "psi", "scfm": "scfm",
    "s": "s", "sec": "s", "seconds": "s", "min": "min", "minutes": "min", "ft2": "ft2",
    "percent": "pct", "pct": "pct",
    # nps is a nominal size in inches: a sentence writes "the 6 in. main" for a segment the record holds as nps 6.
    "ft": "ft", "in": "in", "nps": "in", "ft3": "ft3", "count": "count", "rows": "count", "c": "c",
    "ah": "ah", "lpm": "lpm", "db": "db", "hours": "h",
}
Quantity = tuple[str, "str | None"]

# Numbers written out, for a claim that says "nine hundred gpm". Read only where a unit follows.
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000}
_WORD = "|".join(sorted([*_ONES, *_TENS, *_SCALES], key=len, reverse=True))
# Only before one of the eight claim units. "The two zones" and "one day" are ordinary prose, not figures.
_WORDED = re.compile(
    r"(?<![\w-])((?:" + _WORD + r")(?:(?:[\s-]+|\s+and\s+)(?:" + _WORD + r"))*)\s+" + _CORE_UNITS + r"(?![\w²])",
    re.IGNORECASE,
)


def normal(number: str) -> str:
    """A number as text, so 38,400 and 38400.0 and 38400 compare equal."""
    text = str(number).replace(",", "")
    try:
        value = float(text)
    except ValueError:
        return text
    return f"{value:.10g}"


def respell(text: str | None) -> str:
    """A sentence with the dotted and long spellings of a unit written the way the tables hold it."""
    out = str(text or "")
    for pattern, unit in _RESPELL:
        out = pattern.sub(unit, out)
    return out


def unit_class(unit: str | None) -> str | None:
    """The class of a unit as a sentence writes it. None for a unit this module does not know."""
    text = re.sub(r"\s+", "", str(unit or ""))
    return _CLAIM_UNITS.get(text.lower()) or _FAMILY_OF.get(text)


def name_class(name: str | None) -> str | None:
    """The class a field name gives its number, or None when the name does not say.

    A name with two units in it (density_gpm_ft2) is a compound and says nothing.
    """
    found = {_NAME_UNITS[part] for part in re.split(r"[^a-z0-9]+", str(name or "").lower()) if part in _NAME_UNITS}
    return next(iter(found)) if len(found) == 1 else None


def _classed(text: str) -> list[tuple[int, str, str, str]]:
    """Every number in text that carries a unit: (position, number, the unit as written, its class).

    The eight claim units first, then the other units by family, then a
    ratio no table knows, which is classed by its own spelling. A number is
    read once, by the first of those that takes it.
    """
    found: list[tuple[int, str, str, str]] = []
    taken: set[int] = set()
    for match in FIGURE.finditer(text):
        found.append((match.start(1), normal(match.group(1)), match.group(2), unit_class(match.group(2)) or ""))
        taken.add(match.start(1))
    for match in _FAMILY.finditer(text):
        if match.start(1) not in taken:
            found.append((match.start(1), normal(match.group(1)), match.group(2), _FAMILY_OF[match.group(2)]))
            taken.add(match.start(1))
    for match in _RATIO.finditer(text):
        if match.start(1) not in taken:
            found.append((match.start(1), normal(match.group(1)), match.group(2), "?" + match.group(2).lower()))
            taken.add(match.start(1))
    return sorted(found)


def in_text(text: str | None) -> set[Quantity]:
    """Every number in prose with the class of the unit written after it, None where there is none."""
    text = respell(text)
    found: set[Quantity] = set()
    classed: set[int] = set()
    for position, number, _unit, cls in _classed(text):
        found.add((number, cls))
        classed.add(position)
    for match in _ANY_NUMBER.finditer(text):
        if match.start(1) not in classed:
            found.add((normal(match.group(1)), None))
    return found


def _worded_value(words: str) -> float | None:
    """nine hundred, twenty-five, one thousand two hundred and fifty. None for a run that is not one number.

    "One and two" and "five six" are two numbers, not one, and are not read.
    """
    total, current, last = 0, 0, ""
    for word in re.split(r"[\s-]+", words.lower()):
        if not word:
            continue
        if word == "and":
            if last not in ("hundred", "thousand"):
                return None
            last = "and"
        elif word in _ONES:
            if last == "ones" or (last == "tens" and _ONES[word] >= 10):
                return None
            current += _ONES[word]
            last = "ones"
        elif word in _TENS:
            if last in ("ones", "tens"):
                return None
            current += _TENS[word]
            last = "tens"
        elif word == "hundred":
            if last in ("hundred", "and") or current >= 100:
                return None
            current = (current or 1) * 100
            last = "hundred"
        elif word == "thousand":
            if last in ("thousand", "and"):
                return None
            total += (current or 1) * 1000
            current = 0
            last = "thousand"
        else:
            return None
    return float(total + current) if last and last != "and" else None


def claim_figures(text: str | None) -> list[tuple[str, str, str]]:
    """The figures a claim states, for the trace check: (number, the unit as written, its class), in order.

    Wider than FIGURE. A figure in any unit the module knows is read, in a
    ratio it does not know, and written out in words where a unit follows
    ("nine hundred gpm"). Each then has to be held by the rows the claim
    cites, as that kind of quantity.
    """
    text = respell(text)
    found = [(position, number, unit, cls) for position, number, unit, cls in _classed(text)]
    for match in _WORDED.finditer(text):
        value = _worded_value(match.group(1))
        if value is not None:
            found.append((match.start(1), normal(str(value)), match.group(2), unit_class(match.group(2)) or ""))
    return [(number, unit, cls) for _position, number, unit, cls in sorted(found)]


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
            if _unit_pair(item):
                # A figure stored with its unit beside it ({"value": 1695.8, "unit": "L/min"}, as a unit
                # conversion records it) has the class of that unit. A unit this module does not class, such
                # as gpm/ft², leaves it with none, the way a compound field name does.
                found.update((form, unit_class(item["unit"])) for form in _forms(float(item["value"]), loose))
                for inner, child in item.items():
                    if inner not in ("value", "unit"):
                        walk(child, str(inner))
                return
            for inner, child in item.items():
                # A list of rows keeps the class of the field each number is in; a bare list keeps its own name's.
                walk(child, str(inner))
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child, key)

    walk(value, name)
    return found


def _unit_pair(item: dict) -> bool:
    """A dict that is one figure and the unit it is in: a numeric "value" and a "unit" string."""
    value = item.get("value")
    return (isinstance(item.get("unit"), str) and isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


# The SI units the reply audit reads besides the eight: flow, area, volume, pressure, and a sprinkler density.
# A metric job's reply carries them, and a figure in one of them is as much a computed figure as one in gpm.
_REPLY_SI = ("lpm", "lps", "m3h", "m2", "l", "m3", "kpa", "bar", "mmmin")
_REPLY_SI_FIGURE = re.compile(
    r"(?<![\w.§-])" + _NUMBER + r"\s*("
    + "|".join(re.escape(item) for item in sorted(
        (spelling for cls in _REPLY_SI for spelling in _FAMILIES[cls]), key=len, reverse=True))
    + r")(?![\w²³/])"
)


def reply_figures(text: str | None) -> list[tuple[str, str]]:
    """The figures the reply audit looks up: (number, the unit as written), in the order they stand.

    The eight units of FIGURE, and the SI units of _REPLY_SI. A length, an
    inch, an hour, or a count in a reply is narrative ("a 6 in. main", "two
    zones") and is not read, as before.
    """
    found: list[tuple[int, str, str]] = []
    taken: set[int] = set()
    for match in FIGURE.finditer(text or ""):
        found.append((match.start(1), normal(match.group(1)), match.group(2).lower()))
        taken.add(match.start(1))
    for match in _REPLY_SI_FIGURE.finditer(text or ""):
        if match.start(1) not in taken:
            found.append((match.start(1), normal(match.group(1)), match.group(2)))
    return [(number, unit) for _position, number, unit in sorted(found)]


def holds(number: str, cls: str | None, have: set[Quantity]) -> bool:
    """Whether a figure of a class is held: the same number with that class, or with no class at all."""
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


def has(number: str, unit: str | None, have: set[Quantity]) -> bool:
    """holds(), for a figure given with its unit as written."""
    return holds(number, unit_class(unit), have)


def numbers(have: set[Quantity]) -> list[str]:
    """The numbers alone, sorted, for a row that is printed."""
    return sorted({number for number, _cls in have}, key=lambda item: (len(item), item))
