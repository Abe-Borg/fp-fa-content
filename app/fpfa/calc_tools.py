"""Claude tool schemas. Every number comes from calcs/fp, loaded from the content pack."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from fpfa.modes_loader import list_modes, read_mode
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, read_skill

_MODULES: dict[str, object] = {}


def _load(path: Path):
    key = str(path.resolve())
    if key in _MODULES:
        return _MODULES[key]
    mod_name = "contentpack_" + key.replace("\\", "_").replace("/", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    _MODULES[key] = module
    return module


def _obj(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required}


SCHEMAS = [
    {
        "name": "list_skills",
        "description": "List design methods in the content pack (skills/<slug>/SKILL.md). Read a skill before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_skill",
        "description": "Return the full SKILL.md for one slug. Use this instead of inventing a method.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "list_roles",
        "description": "List specialist roles in the content pack (roles/<slug>/ROLE.md). Read a role before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_role",
        "description": "Return the full ROLE.md for one specialist slug. Use this instead of inventing a role.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "list_modes",
        "description": "List everyday-path modes in the content pack (modes/<slug>/MODE.md). Read a mode before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_mode",
        "description": "Return the full MODE.md for one mode slug. Use this instead of inventing a mode.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "resolve_pipe_id",
        "description": "Shop-default inside diameter for a nominal pipe size. Do not invent an ID. A blank schedule uses the shop default and is flagged.",
        "input_schema": _obj(
            {
                "nps": {"type": "number", "description": "Nominal size in inches"},
                "schedule": {"type": "string", "description": "sch10 or sch40. Omit for the shop default."},
                "role": {"type": "string", "description": "branch, drop, cross, main, feed, or riser"},
            },
            ["nps"],
        ),
    },
    {
        "name": "zone_trapped_volume",
        "description": "Trapped gallons for one zone. Pipe volume is formulas.pipe_volume. Fittings and trim are added here, not in your head.",
        "input_schema": _obj(
            {
                "segments": {"type": "array", "description": "Each item has length_ft and either d_in or nps plus optional schedule and role."},
                "length_basis": {"type": "string", "description": "center_to_center or cut"},
                "fittings_percent": {"type": "number"},
                "trim_gal": {"type": "number"},
            },
            ["segments"],
        ),
    },
    {
        "name": "dry_delivery_screen",
        "description": (
            "Pipe timing, NFPA size cap, and optimistic trip-to-water screen from formulas.dry_delivery_screen. "
            "Not a listed water-delivery calculation. Timing stays on pipe volume. "
            "Pass trim_gal and fittings_percent when the zone has them. "
            "nfpa_delivery_time_exempt then uses the zone total (pipe + fittings + trim) "
            "through the same rule as /run. Omitted fittings_percent counts as 0 when trim_gal is passed. "
            "Double-interlock has a 500 gal cap; a quick-opening device does not raise it."
        ),
        "input_schema": _obj(
            {
                "segments": {"type": "array"},
                "q_fill_gpm": {"type": "number"},
                "qod": {"type": "boolean"},
                "t_detect_s": {"type": "number"},
                "t_release_s": {"type": "number"},
                "t_exhaust_s": {"type": "number"},
                "basis": {"type": "string", "description": "FM or NFPA-OH"},
                "system_type": {"type": "string", "description": "dry or di"},
                "trim_gal": {"type": "number", "description": "Trim gallons to include in the size exemption. Omit for a pipe-only screen."},
                "fittings_percent": {"type": "number", "description": "Fittings allowance percent. Used with trim_gal for the zone-total exemption."},
            },
            ["segments", "q_fill_gpm", "system_type"],
        ),
    },
    {
        "name": "di_trip_to_water",
        "description": "Optimistic t = t_detect + t_release + t_exhaust + 60*V/Q from formulas.di_trip_to_water. Pass the zone total gallons, including trim. Not a listed delivery-time proof.",
        "input_schema": _obj(
            {
                "v_gal": {"type": "number"},
                "q_fill_gpm": {"type": "number"},
                "t_detect_s": {"type": "number"},
                "t_release_s": {"type": "number"},
                "t_exhaust_s": {"type": "number"},
                "basis": {"type": "string"},
            },
            ["v_gal", "q_fill_gpm"],
        ),
    },
    {
        "name": "density_area",
        "description": "Sprinkler demand from formulas.density_area. design area = base * (1 + increase); demand adds hose.",
        "input_schema": _obj(
            {
                "density_gpm_ft2": {"type": "number"},
                "base_area_ft2": {"type": "number"},
                "area_increase": {"type": "number"},
                "hose_gpm": {"type": "number"},
                "duration_min": {"type": "number"},
            },
            ["density_gpm_ft2", "base_area_ft2"],
        ),
    },
    {
        "name": "hose_duration",
        "description": "Hose stream and duration from formulas.hose_duration (NFPA 13-2025 Table 19.2.3.1.2 screen).",
        "input_schema": _obj(
            {"hazard": {"type": "string"}, "supervised": {"type": "boolean"}},
            ["hazard"],
        ),
    },
    {
        "name": "nitrogen_gate",
        "description": (
            "Design C is 100. Fill scfm is formulas.air_fill_scfm. "
            "The result states the gauge-basis rate and the absolute-basis rate. Quote both. "
            "Do not emit C=120 as the design value."
        ),
        "input_schema": _obj(
            {"v_gal": {"type": "number"}, "p_psig": {"type": "number"}, "t_min": {"type": "number"}},
            ["v_gal"],
        ),
    },
    {
        "name": "elect_di_trim",
        "description": "Double-interlock trim-family screen. Elect El/El, El/Pn, or named-failsafe from what holds the prime. Do not invent a catalog number. Out-of-scope systems return RFI-variance.",
        "input_schema": _obj(
            {
                "system_type": {"type": "string"},
                "prime_held_by": {"type": "string", "description": "nc_solenoid, pneumatic_actuator, or unknown"},
                "failsafe_on_total_power_loss": {"type": "boolean"},
                "supervisory_psi": {"type": "number"},
                "medium": {"type": "string"},
                "insurer": {"type": "string"},
            },
            ["system_type"],
        ),
    },
    {
        "name": "releasing_truth_table",
        "description": "Build the double-interlock solenoid truth table in code. solenoid = (detection OR manual) AND low air AND NOT isolated. A second smoke zone must not change the result.",
        "input_schema": _obj(
            {"manual_station": {"type": "boolean"}, "insurer": {"type": "string"}},
            [],
        ),
    },
    {
        "name": "lfl_setpoints",
        "description": (
            "Mixture LFL and setpoints from calcs/fa/lib/lfl.py. "
            "Pass each percent. This tool does not choose a code threshold, an election, or a duration."
        ),
        "input_schema": _obj(
            {
                "mix": {"type": "object", "description": "Gas name to volume percent or fraction."},
                "lfl": {"type": "object", "description": "Gas name to component LFL vol%. Use null for an inert."},
                "screens": {
                    "type": "array",
                    "description": "Each item has name, pct, and basis (fuel or diluted). pct is the caller's percent.",
                },
            },
            ["mix", "lfl"],
        ),
    },
    {
        "name": "fp_calc",
        "description": "Run any other op in calcs/fp/formulas.py by name (hazen_williams, pump_envelope, k_factor, and the rest). Pass op and inputs. Do not compute the formula yourself.",
        "input_schema": _obj(
            {"op": {"type": "string"}, "inputs": {"type": "object"}},
            ["op", "inputs"],
        ),
    },
]

# The DI workflow refuses a narrative until these have run on the form.
REQUIRED_DI_TOOLS = [
    "zone_trapped_volume",
    "dry_delivery_screen",
    "di_trip_to_water",
    "elect_di_trim",
    "releasing_truth_table",
]


class ToolSession:
    def __init__(self, content_root: Path):
        self.root = Path(content_root)
        di_path = self.root / "calcs" / "fp" / "di_zone.py"
        if not di_path.is_file():
            raise FileNotFoundError(di_path)
        self.di = _load(di_path)
        self.formulas = self.di.formulas

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name == "list_skills":
            return {"skills": list_skills(self.root)}
        if name == "read_skill":
            text = read_skill(self.root, str(args.get("slug", "")))
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "list_roles":
            return {"roles": list_roles(self.root)}
        if name == "read_role":
            text = read_role(self.root, str(args.get("slug", "")))
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "list_modes":
            return {"modes": list_modes(self.root)}
        if name == "read_mode":
            text = read_mode(self.root, str(args.get("slug", "")))
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "resolve_pipe_id":
            return self.di.pipe_ids.resolve(args.get("nps"), args.get("schedule"), args.get("role"))
        if name == "zone_trapped_volume":
            return self.di.zone_trapped_volume(
                args.get("segments"),
                args.get("length_basis") or "center_to_center",
                args.get("fittings_percent"),
                args.get("trim_gal"),
            )
        if name == "dry_delivery_screen":
            screen = self.formulas.dry_delivery_screen(
                args.get("segments"),
                args.get("q_fill_gpm"),
                qod=args.get("qod", False),
                t_detect_s=args.get("t_detect_s", 0),
                t_release_s=args.get("t_release_s", 0),
                t_exhaust_s=args.get("t_exhaust_s", 0),
                basis=args.get("basis") or "FM",
                system_type=args.get("system_type") or "di",
            )
            return _govern_delivery_exemption(self.formulas, screen, args)
        if name == "di_trip_to_water":
            return self.formulas.di_trip_to_water(
                args.get("v_gal"),
                args.get("q_fill_gpm"),
                t_detect_s=args.get("t_detect_s", 0),
                t_release_s=args.get("t_release_s", 0),
                t_exhaust_s=args.get("t_exhaust_s", 0),
                basis=args.get("basis") or "FM",
            )
        if name == "density_area":
            return self.formulas.density_area(
                args.get("density_gpm_ft2"),
                args.get("base_area_ft2"),
                area_increase=args.get("area_increase") or 0,
                hose_gpm=args.get("hose_gpm") or 0,
                duration_min=args.get("duration_min"),
            )
        if name == "hose_duration":
            return self.formulas.hose_duration(args.get("hazard") or "ordinary", args.get("supervised", False))
        if name == "nitrogen_gate":
            return self.di.nitrogen_gate(args.get("v_gal"), args.get("p_psig") or 40, args.get("t_min") or 30)
        if name == "elect_di_trim":
            return self.di.elect_di_trim(
                args.get("system_type") or "",
                prime_held_by=args.get("prime_held_by") or "unknown",
                failsafe_on_total_power_loss=args.get("failsafe_on_total_power_loss", False),
                supervisory_psi=args.get("supervisory_psi"),
                medium=args.get("medium") or "unelected",
                insurer=args.get("insurer") or "",
            )
        if name == "releasing_truth_table":
            return self.di.releasing_truth_table(
                manual_station=args.get("manual_station", True),
                insurer=args.get("insurer") or "FM",
            )
        if name == "lfl_setpoints":
            return _lfl_setpoints(self.root, args)
        if name == "fp_calc":
            return self.formulas.dispatch(str(args.get("op") or ""), dict(args.get("inputs") or {}))
        raise KeyError(f"unknown tool {name}")


def _lfl_setpoints(content_root: Path, args: dict) -> dict:
    """Run lfl.setpoints_for. Percents stay whatever the caller passed."""
    path = Path(content_root) / "calcs" / "fa" / "lib" / "lfl.py"
    if not path.is_file():
        raise FileNotFoundError(path)
    module = _load(path)
    mix = args.get("mix") or {}
    table = args.get("lfl") or {}
    screens = args.get("screens") or []
    if not isinstance(mix, dict) or not isinstance(table, dict):
        raise ValueError("mix and lfl must be objects")
    if not isinstance(screens, list):
        raise ValueError("screens must be a list")
    clean_lfl = {}
    for key, value in table.items():
        if value is None or value == "":
            clean_lfl[str(key)] = None
        else:
            clean_lfl[str(key)] = float(value)
    clean_mix = {str(key): float(value) for key, value in mix.items()}
    clean_screens = []
    for screen in screens:
        if not isinstance(screen, dict):
            raise ValueError("each screen must be an object")
        if "pct" not in screen:
            raise ValueError("each screen needs a pct")
        clean_screens.append({
            "name": str(screen.get("name") or screen.get("id") or ""),
            "pct": float(screen["pct"]),
            "basis": str(screen.get("basis") or ""),
        })
    return module.setpoints_for(clean_mix, clean_lfl, clean_screens)


def dumps(payload) -> str:
    return json.dumps(payload, indent=2, default=str)


def _number_was_passed(args: dict, key: str) -> bool:
    if key not in args:
        return False
    value = args[key]
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _govern_delivery_exemption(formulas, screen: dict, args: dict) -> dict:
    """Size exemption follows the zone total when trim or fittings were passed.

    Timing on the pipe-only screen stays. ``govern_nfpa_exemption`` is the same
    helper ``/run`` uses. A call with neither trim nor fittings stays pipe-only.
    """
    trim_passed = _number_was_passed(args, "trim_gal")
    fittings_passed = _number_was_passed(args, "fittings_percent")
    if not trim_passed and not fittings_passed:
        return screen
    trim = formulas._require_non_negative("trim_gal", args["trim_gal"]) if trim_passed else 0.0
    fittings = (
        formulas._require_non_negative("fittings_percent", args["fittings_percent"])
        if fittings_passed else 0.0
    )
    pipe = float(screen["volume_gal"])
    zone_gal = pipe * (1.0 + fittings / 100.0) + trim
    # Local import: workflow imports this module at load time.
    from fpfa.workflow import govern_nfpa_exemption

    return govern_nfpa_exemption(screen, zone_gal)
