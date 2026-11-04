"""Allowlisted dispatcher for calcs/fa/lib.

The model names a module and a function. This module loads that file from the
content pack and calls the function. It does not evaluate a formula itself.
"""

from __future__ import annotations

import inspect
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
    module = _fa_module(content_root, module_name)
    if op_name not in FA_OPS[module_name] or not _is_public_function(module, op_name):
        raise KeyError(f"unknown op {op_name!r} for module {module_name!r}")
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
