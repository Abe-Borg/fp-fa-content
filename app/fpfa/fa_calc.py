"""Allowlisted dispatcher for calcs/fa/lib.

The model names a module and a function. This module loads that file from the
content pack and calls the function. It does not evaluate a formula itself.
"""

from __future__ import annotations

import inspect
import math
import sys
from pathlib import Path

# Public design ops. A name that is not a public function in the file is omitted.
# Private helpers (leading underscore) are never called.
FA_OPS: dict[str, tuple[str, ...]] = {
    "nac_vdrop": (
        "ohm_per_kft",
        "loop_resistance",
        "ell",
        "ptp",
        "max_one_way_ft",
        "smallest_passing_awg",
    ),
    "battery": (
        "factor",
        "alarm_minutes",
        "standby_hours",
        "ah_required",
        "pick_battery",
        "margin_pct",
        "charger_ok",
        "split_supplies",
    ),
    "speaker": (
        "z_load",
        "loss_db",
        "k_factor",
        "max_len_ft",
        "amp_check",
    ),
    "sti": (
        "r05",
        "evaluate",
    ),
    "audibility": (
        "required_dba",
        "check",
    ),
    "asd": (
        "area_m2",
        "velocity_ms",
        "transport_s",
        "max_len_m",
        "check",
    ),
    "asd_v2": (
        "branch",
        "branch_time",
        "network",
        "v1_screen",
        "port_times",
    ),
    "airflow": (
        "minutes_per_change",
        "spacing_ft2",
        "detectors",
    ),
    "ads_grid": (
        "points",
        "max_on_axis",
        "must_split",
        "grid",
    ),
    "ads_margin": (
        "spl_at",
        "combine",
        "margin",
    ),
    "class_n": (
        "check_pathway",
        "check_network",
    ),
    "epss_fuel": (
        "multiplier",
        "low_fuel_gal",
        "min_tank_gal",
        "fuel_hours",
        "check",
    ),
    "itm": (
        "visits",
        "sensitivity_years",
    ),
    "separation": (
        "shared_ok",
        "annex_sep_ok",
    ),
    "lfl": (
        "lfl_mix",
        "lfl_with_diluent",
        "pct_of_lfl",
        "setpoint",
        "trigger_paths",
        "setpoints_for",
    ),
}


def run_fa_calc(content_root: Path, args: dict | None) -> dict:
    """Run one allowlisted op, or return the allowlist when list_ops is true."""
    payload = dict(args or {})
    if payload.get("list_ops") is True:
        return {"ops": present_ops(content_root)}
    module_name = _module_name(payload.get("module"))
    op_name = _op_name(payload.get("op"))
    if "inputs" in payload and payload.get("inputs") is not None:
        inputs = payload.get("inputs")
    else:
        inputs = {}
    if not isinstance(inputs, dict):
        raise ValueError("inputs must be an object")
    # A copy: what the caller passed is what the record keeps, and the checks below may clean a value for the kernel.
    inputs = dict(inputs)
    module = _fa_module(content_root, module_name)
    if op_name not in FA_OPS[module_name] or not _is_public_function(module, op_name):
        raise KeyError(f"unknown op {op_name!r} for module {module_name!r}")
    if module_name == "battery" and op_name == "split_supplies":
        _require_split_capacity(inputs)
    if module_name == "battery" and op_name == "charger_ok":
        held = charger_hold(module, inputs)
        if held is not None:
            # Returned, not raised, so the call is recorded and the HOLD stands on the job until a charger_ok
            # runs on the listed cap. The kernel is not called: no maker key and no remembered cap stands in.
            return held
    if module_name == "lfl":
        _require_lfl(op_name, inputs)
    return _as_dict(getattr(module, op_name)(**inputs))


def present_ops(content_root: Path) -> dict[str, list[str]]:
    """Declared ops that exist as public functions. Missing names are left out."""
    found: dict[str, list[str]] = {}
    for module_name in FA_OPS:
        try:
            module = _fa_module(content_root, module_name)
        except KeyError:
            continue
        ops = [name for name in FA_OPS[module_name] if _is_public_function(module, name)]
        if ops:
            found[module_name] = ops
    return found


def _module_name(value) -> str:
    text = str(value or "").strip()
    if text.endswith(".py"):
        text = text[:-3]
    if not text or "/" in text or "\\" in text or ".." in text or text not in FA_OPS:
        raise KeyError(f"unknown fa module {value!r}")
    return text


def _require_split_capacity(inputs: dict) -> None:
    """Reject a cap that split_supplies can never reach.

    The library loops while required amp-hours stay above cap_ah. Positive
    loads approach 0 and never land on a nonpositive cap, so the call hangs.
    Negative currents already raise inside ah_required and do not hang.
    """
    cap = inputs.get("cap_ah")
    if isinstance(cap, bool) or not isinstance(cap, (int, float)) or not math.isfinite(cap) or cap <= 0:
        raise ValueError("cap_ah must be > 0")


CHARGER_CAP = "listed_charger_max_ah"
# The one message a charger check holds on, whatever the cause. It is never a PASS or a FAIL.
CHARGER_HOLD = "HOLD: listed_charger_max_ah required from the listed charger datasheet"
HOLD_STATUS = "HOLD"


def charger_hold(module, inputs: dict) -> dict | None:
    """The HOLD result for a charger_ok call that cannot run on the caller's listed cap, or None when it can.

    charger_ok takes the charger's listed maximum Ah from the caller, and
    nothing else. A maker key, a missing, non-numeric, non-finite, or
    non-positive cap, and a pack whose charger_ok does not take the caller's
    cap all hold, with one message (CHARGER_HOLD). No maker table or remembered
    cap stands in, and the result carries no pass or fail.
    """
    cap = inputs.get(CHARGER_CAP)
    usable = not isinstance(cap, bool) and isinstance(cap, (int, float)) and math.isfinite(cap) and cap > 0
    try:
        takes = CHARGER_CAP in inspect.signature(getattr(module, "charger_ok")).parameters
    except (TypeError, ValueError, AttributeError):
        takes = False
    if "maker_key" not in inputs and usable and takes:
        return None
    return {"module": "battery", "op": "charger_ok", "status": HOLD_STATUS, "message": CHARGER_HOLD,
            "charger_ok": None}


def standing_holds(calcs: list[dict] | None, stale: set[str] | None = None) -> list[str]:
    """The HOLD lines that stand on a job's record: a charger check whose latest current row is a HOLD.

    A charger_ok that later ran on the listed cap ends it. A row out of date
    (stale) does not count either way.
    """
    stale = stale or set()
    latest = None
    for row in calcs or []:
        inp = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
        if row.get("tool") != "fa_calc" or row.get("id") in stale:
            continue
        if _module_name_or_blank(inp.get("module")) == "battery" and str(inp.get("op") or "").strip() == "charger_ok":
            latest = row
    out = (latest or {}).get("outputs")
    if isinstance(out, dict) and out.get("status") == HOLD_STATUS:
        return [CHARGER_HOLD]
    return []


def _module_name_or_blank(value) -> str:
    text = str(value or "").strip()
    return text[:-3] if text.endswith(".py") else text


# The LFL ops and the arguments each reads an LFL from: a table of component LFLs, or one LFL figure.
_LFL_TABLE_OPS = {"lfl_mix", "lfl_with_diluent", "setpoints_for"}
_LFL_FIGURE_OPS = {"pct_of_lfl": "lfl_vol_pct", "setpoint": "lfl_vol_pct", "trigger_paths": "lfl_vol_pct"}
INERT = "inert"


def clean_lfl_table(tool: str, mix, table) -> dict:
    """The component LFL table a mix runs on, or a HOLD naming every gas without a usable LFL.

    Every gas in the mix has an LFL greater than 0 that the caller gave, or is
    written "inert" (passed on as None, which the kernel reads as inert). A
    blank, missing, zero, negative, or non-finite LFL holds the call: the
    kernel would read a gas with no LFL as inert, and the application picks no
    LFL for it.
    """
    if not isinstance(mix, dict) or not isinstance(table, dict):
        raise ValueError(f"HOLD: {tool} needs mix and lfl as objects: gas name to percent, and gas name to its "
                         "component LFL vol% or \"inert\".")
    clean: dict[str, float | None] = {}
    holds = []
    for key, value in table.items():
        if isinstance(value, str) and value.strip().lower() == INERT:
            clean[str(key)] = None
            continue
        number = _finite_number(value)
        if number is None or number <= 0:
            holds.append(f"{key} (LFL {value!r})")
            continue
        clean[str(key)] = number
    holds.extend(f"{key} (no LFL given)" for key in mix if str(key) not in clean
                 and not any(item.startswith(f"{key} (LFL") for item in holds))
    if holds:
        raise ValueError(
            f"HOLD: {tool} needs a component LFL vol% greater than 0 for every gas in mix, or \"inert\": "
            + ", ".join(holds) + ". The application picks no LFL and no percent."
        )
    return clean


def _require_lfl(op: str, inputs: dict) -> None:
    """The LFL ops reached through fa_calc hold on an LFL as lfl_setpoints does. The table is cleaned in place."""
    if op in _LFL_TABLE_OPS:
        inputs["lfl"] = clean_lfl_table(f"fa_calc lfl.{op}", inputs.get("mix"), inputs.get("lfl"))
        return
    key = _LFL_FIGURE_OPS.get(op)
    if key is None:
        return
    value = inputs.get(key)
    number = _finite_number(value)
    if number is None or number <= 0:
        raise ValueError(f"HOLD: fa_calc lfl.{op} needs {key}, an LFL vol% greater than 0 (got {value!r}). "
                         "The application picks no LFL.")


def _finite_number(value) -> float | None:
    if isinstance(value, bool) or value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _op_name(value) -> str:
    text = str(value or "").strip()
    if not text or text.startswith("_") or not text.isidentifier():
        raise KeyError(f"unknown op {value!r}")
    return text


_FA_PATHS: list[str] = []


def _fa_module(content_root: Path, module_name: str):
    """Load calcs/fa/lib/<module>.py through the content-pack loader.

    asd_v2 and ads_margin import `lib` the same way the fa unit tests do,
    which puts calcs/fa on sys.path. A later content root replaces that
    entry so the import follows the pack that is running. The allowlist
    is the only module name accepted.
    """
    if module_name not in FA_OPS:
        raise KeyError(f"unknown fa module {module_name!r}")
    fa_root = (Path(content_root) / "calcs" / "fa").resolve()
    path = fa_root / "lib" / f"{module_name}.py"
    if not path.is_file():
        raise KeyError(f"unknown fa module {module_name!r}")
    _use_fa_root(fa_root)
    from fpfa.calc_tools import _load

    return _load(path)


def _use_fa_root(fa_root: Path) -> None:
    entry = str(fa_root)
    for old in list(_FA_PATHS):
        while old in sys.path:
            sys.path.remove(old)
    _FA_PATHS.clear()
    sys.path.insert(0, entry)
    _FA_PATHS.append(entry)
    loaded = sys.modules.get("lib")
    loaded_file = getattr(loaded, "__file__", None) if loaded is not None else None
    if loaded_file is None:
        return
    if Path(loaded_file).resolve().parent == fa_root / "lib":
        return
    for key in list(sys.modules):
        if key == "lib" or key.startswith("lib."):
            del sys.modules[key]


def _is_public_function(module, name: str) -> bool:
    if not name.isidentifier() or name.startswith("_"):
        return False
    fn = getattr(module, name, None)
    if not inspect.isfunction(fn):
        return False
    return getattr(fn, "__module__", None) == module.__name__


def _as_dict(value):
    """Tool results are dicts. Bare numbers, bools, and other values are wrapped."""
    cleaned = _to_jsonable(value)
    if isinstance(cleaned, dict):
        return cleaned
    return {"value": cleaned}


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"op returned {type(value).__name__}, which is not JSON")
