"""Exact unit conversion: the convert_units tool, and an input the designer gave in other units.

Every calc tool takes the US units its field names state (gpm, ft2, gpm/ft2,
psi, gal, ft, in, s, min). A designer on a metric job gives SI figures, and
the model never converts in its head (the math rule). So the application
converts, here, by the definitions and nothing else:

- 1 ft = 0.3048 m and 1 in = 0.0254 m (the international foot and inch).
- 1 US gallon = 231 in3 = 3.785411784 L.
- 1 lbf = 4.4482216152605 N, so 1 psi = 6.894757293168361 kPa. 1 bar = 100 kPa.
- A sprinkler density in mm/min is a flow in L/min over each m2 of area.

Each of those is exact by definition (the 1959 yard and pound agreement and
the US gallon of 231 cubic inches), so no factor here is an engineering
choice and none is rounded.

A conversion changes the unit of a figure and nothing else. A figure that
was ASSUMED is still ASSUMED. A gauge pressure stays a gauge pressure:
gauge and absolute are never converted into each other, because that takes
an atmospheric pressure, which is an assumption. Cubic feet are left out on
purpose. The kernel's pipe volume uses 7.48 gal per cubic foot, whether to
use the exact figure is a content decision still open (NEXT-STEPS.md,
section 4), and the application does not put a second figure beside it.

foreign_figures() reads the SI figures in what the designer wrote, so a
calc tool can refuse one passed into a field that takes US units
(calc_tools.ToolSession). That is matching on text: it catches the number
the designer gave, not a figure the model remembered from elsewhere.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from fpfa import quantities


class UnitError(ValueError):
    """A unit the application cannot convert, or two units that measure different things."""


@dataclass(frozen=True)
class Unit:
    key: str
    dimension: str
    # How many of the dimension's base unit one of this unit is.
    factor: float
    # The unit as a result prints it.
    display: str
    si: bool


_IN = 0.0254
_FT = 0.3048
_GAL_L = 3.785411784
_FT2_M2 = _FT * _FT
_PSI_KPA = 4.4482216152605 / (_IN * _IN) / 1000.0

# key: (dimension, factor to the base unit, display, SI). Bases: m, m2, L, L/min, kPa, mm/min, s.
_TABLE: dict[str, tuple[str, float, str, bool]] = {
    "m": ("length", 1.0, "m", True),
    "mm": ("length", 0.001, "mm", True),
    "cm": ("length", 0.01, "cm", True),
    "ft": ("length", _FT, "ft", False),
    "in": ("length", _IN, "in", False),
    "m2": ("area", 1.0, "m²", True),
    "ft2": ("area", _FT2_M2, "ft²", False),
    "L": ("volume", 1.0, "L", True),
    "m3": ("volume", 1000.0, "m³", True),
    "gal": ("volume", _GAL_L, "gal", False),
    "L/min": ("flow", 1.0, "L/min", True),
    "L/s": ("flow", 60.0, "L/s", True),
    "m3/h": ("flow", 1000.0 / 60.0, "m³/h", True),
    "gpm": ("flow", _GAL_L, "gpm", False),
    "kPa": ("pressure", 1.0, "kPa", True),
    "Pa": ("pressure", 0.001, "Pa", True),
    "MPa": ("pressure", 1000.0, "MPa", True),
    "bar": ("pressure", 100.0, "bar", True),
    "psi": ("pressure", _PSI_KPA, "psi", False),
    "mm/min": ("density", 1.0, "mm/min", True),
    "gpm/ft2": ("density", _GAL_L / _FT2_M2, "gpm/ft²", False),
    "s": ("time", 1.0, "s", True),
    "min": ("time", 60.0, "min", True),
    "hr": ("time", 3600.0, "hr", True),
}
UNITS: dict[str, Unit] = {key: Unit(key, *row) for key, row in _TABLE.items()}

# Spellings, as _normal() leaves them, to the unit they name.
_SPELLINGS: dict[str, str] = {}
for _key, _words in {
    "m": ("m", "metre", "meter", "metres", "meters"),
    "mm": ("mm", "millimetre", "millimeter", "millimetres", "millimeters"),
    "cm": ("cm", "centimetre", "centimeter", "centimetres", "centimeters"),
    "ft": ("ft", "foot", "feet"),
    "in": ("in", "in.", "inch", "inches"),
    "m2": ("m2", "sqm", "sq.m", "squaremetre", "squaremeter", "squaremetres", "squaremeters"),
    "ft2": ("ft2", "sqft", "sq.ft", "sf", "squarefoot", "squarefeet"),
    "L": ("l", "litre", "liter", "litres", "liters"),
    "m3": ("m3", "cubicmetre", "cubicmeter", "cubicmetres", "cubicmeters"),
    "gal": ("gal", "gals", "gallon", "gallons", "usgal"),
    "L/min": ("l/min", "lpm", "litre/min", "liter/min", "litres/min", "liters/min", "l/minute",
              "litres/minute", "liters/minute"),
    "L/s": ("l/s", "lps", "l/sec", "litres/s", "liters/s", "litres/second", "liters/second"),
    "m3/h": ("m3/h", "m3/hr", "m3/hour"),
    "gpm": ("gpm", "gal/min", "gallons/minute", "gallon/minute", "usgpm"),
    "kPa": ("kpa", "kpag", "kpa(g)"),
    "Pa": ("pa",),
    "MPa": ("mpa", "mpag"),
    "bar": ("bar", "barg", "bar(g)"),
    "psi": ("psi", "psig"),
    "mm/min": ("mm/min", "l/min/m2", "lpm/m2", "l/m2/min", "mm/minute"),
    "gpm/ft2": ("gpm/ft2", "gpm/sqft", "gpm/sf", "gal/min/ft2"),
    "s": ("s", "sec", "secs", "second", "seconds"),
    "min": ("min", "mins", "minute", "minutes"),
    "hr": ("h", "hr", "hrs", "hour", "hours"),
}.items():
    for _word in _words:
        _SPELLINGS[_word] = _key
# A pressure said to be absolute. It is not converted: from gauge it would need an atmospheric pressure.
_ABSOLUTE = re.compile(r"(psia|bara|kpaa|\(a\)|abs)$")

_BASIS = {
    "length": "1 ft = 0.3048 m and 1 in = 0.0254 m, exact by definition.",
    "area": "1 ft² = 0.09290304 m², exact by definition (0.3048 m squared).",
    "volume": "1 US gallon = 231 in³ = 3.785411784 L, exact by definition.",
    "flow": "1 gpm = 3.785411784 L/min (the US gallon), exact by definition.",
    "pressure": ("1 psi = 6.894757293168361 kPa (1 lbf = 4.4482216152605 N over 1 in²) and 1 bar = 100 kPa, exact "
                 "by definition. Gauge stays gauge: a gauge pressure converts to a gauge pressure."),
    "density": ("A density in mm/min is a flow in L/min over each m² of area, so 1 gpm/ft² = 3.785411784 L/min over "
                "0.09290304 m² = 40.74583 mm/min, exact by definition."),
    "time": "1 min = 60 s and 1 hr = 3600 s.",
}
_DIMENSION_WORD = {
    "length": "length", "area": "area", "volume": "volume", "flow": "flow", "pressure": "pressure",
    "density": "sprinkler design density", "time": "time",
}
NOTE = ("A unit conversion. It changes the unit and nothing else: a figure that was ASSUMED is still ASSUMED, and "
        "one that was the designer's is still theirs.")


def _normal(text: str) -> str:
    """A unit as written, in the one spelling the table looks up: lower case, no spaces, no superscripts."""
    out = str(text or "").strip().lower()
    out = out.replace("²", "2").replace("³", "3").replace("·", "/").replace("⋅", "/")
    out = re.sub(r"\s+per\s+", "/", out)
    if "(g)" not in out:
        # L/(min·m²) is L/min/m²; kPa(g) keeps its mark, which the table spells.
        out = out.replace("(", "").replace(")", "")
    out = re.sub(r"\s+", "", out)
    return out if out in ("in.", "sq.m", "sq.ft") else out.rstrip(".")


def unit(text: Any) -> Unit:
    """The unit a spelling names. Raises UnitError with what the application converts."""
    raw = str(text or "").strip()
    if not raw:
        raise UnitError("A unit is needed. " + known())
    word = _normal(raw)
    if _ABSOLUTE.search(word):
        raise UnitError(
            f"{raw!r} is an absolute pressure. The application converts gauge pressures only, because a change "
            "between gauge and absolute needs an atmospheric pressure, which is an assumption."
        )
    key = _SPELLINGS.get(word)
    if key is None:
        raise UnitError(f"The application does not convert {raw!r}. " + known())
    return UNITS[key]


def known() -> str:
    """What the application converts, by kind of quantity, for an error message or a tool description."""
    groups: dict[str, list[str]] = {}
    for item in UNITS.values():
        groups.setdefault(item.dimension, []).append(item.display)
    return "It converts " + "; ".join(f"{_DIMENSION_WORD[dim]}: {', '.join(names)}" for dim, names in groups.items()) + "."


def kind(dimension: str) -> str:
    """A kind of quantity with its article, for a sentence: a length, an area."""
    word = _DIMENSION_WORD.get(dimension, dimension)
    return ("an " if word[:1] in "aeiou" else "a ") + word


def _number(value: Any) -> float:
    if isinstance(value, bool):
        raise UnitError("value takes a number")
    try:
        number = float(str(value).replace(",", "")) if isinstance(value, str) else float(value)
    except (TypeError, ValueError) as exc:
        raise UnitError(f"value takes a number, not {value!r}") from exc
    if not math.isfinite(number):
        raise UnitError("value takes a finite number")
    return number


def convert(value: Any, from_unit: Any, to_unit: Any) -> dict:
    """value in from_unit, given in to_unit, by the exact definitions. The convert_units tool's result."""
    number = _number(value)
    source, target = unit(from_unit), unit(to_unit)
    if source.dimension != target.dimension:
        raise UnitError(
            f"{source.display} is {kind(source.dimension)} and {target.display} is {kind(target.dimension)}. "
            "They do not convert into each other."
        )
    factor = source.factor / target.factor
    result = number * factor
    return {
        "formula": "result = value × factor, by the exact unit definitions",
        "given": {"value": number, "unit": source.display},
        "result": {"value": result, "unit": target.display},
        "factor": factor,
        "quantity": _DIMENSION_WORD[source.dimension],
        "basis": _BASIS[source.dimension],
        "note": NOTE,
    }


def split(text: Any) -> tuple[float, str] | None:
    """A typed figure as (number, the unit as written), or None when text is not a number and a unit."""
    if not isinstance(text, str):
        return None
    found = re.match(r"\s*([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*(.*?)\s*$", text)
    if not found or not found.group(1) or not found.group(2):
        return None
    try:
        number = float(found.group(1).replace(",", ""))
    except ValueError:
        return None
    return number, found.group(2)


# A field name's unit, by its last parts, for the guard on an SI figure passed to a US field.
_FIELD_UNITS = (
    (("gpm", "ft2"), "gpm/ft2"),
    (("gpm",), "gpm"),
    (("ft2",), "ft2"),
    (("gal",), "gal"),
    (("psig",), "psi"),
    (("psi",), "psi"),
    (("ft",), "ft"),
    (("in",), "in"),
)


def field_unit(name: Any) -> Unit | None:
    """The US unit a calc tool's field name states (density_gpm_ft2, q_fill_gpm, v_gal, length_ft). Else None."""
    parts = [part for part in re.split(r"[^a-z0-9]+", str(name or "").lower()) if part]
    for tail, key in _FIELD_UNITS:
        if len(parts) > len(tail) and tuple(parts[-len(tail):]) == tail:
            return UNITS[key]
    return None


_FIGURE_IN_TEXT = re.compile(
    r"(?<![\w.§-])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(mm/min|L/min/m²|L/min/m2|lpm/m2|L/min|l/min|lpm|L/s|l/s|m³/h|m3/h|m³/hr|m3/hr|kPa|MPa|bar|m²|m2|m³|m3|"
    r"mm|cm|m|L|gpm/ft²|gpm/ft2|gpm/sq\s?ft|gpm|ft²|ft2|sq\s?ft|gal|psig|psi|ft|in\.)"
    r"(?![\w²³/])",
    re.IGNORECASE,
)


def figures_in_text(text: Any) -> list[tuple[str, Unit]]:
    """Every figure in prose with a unit this module converts: (the number as the record compares it, the unit)."""
    out: list[tuple[str, Unit]] = []
    for match in _FIGURE_IN_TEXT.finditer(str(text or "")):
        try:
            found = unit(match.group(2))
        except UnitError:
            continue
        out.append((quantities.normal(match.group(1)), found))
    return out


def foreign_figures(text: Any) -> tuple[tuple[str, str, str], ...]:
    """The SI figures in the designer's words that they did not also give in a US unit of the same kind.

    Each is (the number as the record compares it, its dimension, the unit as it prints). A designer who
    wrote "139 m² (1,496 ft²)" gave both, and 139 is not refused as a number of square feet on that account.
    """
    found = figures_in_text(text)
    native = {(number, item.dimension) for number, item in found if not item.si}
    out: list[tuple[str, str, str]] = []
    for number, item in found:
        if item.si and item.dimension in ("length", "area", "volume", "flow", "pressure", "density") \
                and (number, item.dimension) not in native and (number, item.dimension, item.display) not in out:
            out.append((number, item.dimension, item.display))
    return tuple(out)
