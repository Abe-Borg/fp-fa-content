"""Double-interlock zone screens on top of formulas.py.

Volume, delivery time, density, hose, and nitrogen fill rate are the kernel
in formulas.py. This module only adds the allowances, the trim-family screen,
and the releasing truth table. It does not invent a listed water-delivery time.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _sibling(name: str):
    path = Path(__file__).resolve().parent / f"{name}.py"
    mod_name = "calcs_fp_" + name + "_" + path.parent.as_posix().replace("/", "_")
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


formulas = _sibling("formulas")
pipe_ids = _sibling("pipe_ids")

_STOP_TYPES = {
    "single_interlock",
    "single-interlock",
    "si",
    "non_interlock",
    "non-interlock",
    "ni",
    "foam",
    "foam_water",
    "clean_agent",
    "clean-agent",
    "mist",
    "water_mist",
    "deluge",
}


def normalize_system(system_type: str) -> str:
    st = str(system_type).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "double_interlock": "di",
        "di_preaction": "di",
        "preaction": "di",
        "dry_pipe": "dry",
        "wet_pipe": "wet",
    }
    return aliases.get(st, st)


def _segments(raw: Any) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(raw, list) or not raw:
        raise formulas.CalcError("segments must be a non-empty list")
    rows = []
    flags: list[str] = []
    for i, seg in enumerate(raw):
        if not isinstance(seg, dict):
            raise formulas.CalcError(f"segment {i} must be an object")
        length = seg.get("length_ft", seg.get("length", seg.get("l")))
        role = seg.get("role")
        if seg.get("d_in") not in (None, ""):
            d = float(seg["d_in"])
            src = "caller inside diameter"
            nps = seg.get("nps")
            sch = seg.get("schedule")
        else:
            resolved = pipe_ids.resolve(seg.get("nps", seg.get("size")), seg.get("schedule"), role)
            d = resolved["d_in"]
            src = resolved["id_source"]
            nps = resolved["nps"]
            sch = resolved["schedule"]
            flags.extend(f"segment {i + 1}: {item}" for item in resolved["flags"])
        rows.append({
            "d_in": d,
            "length_ft": float(length),
            "role": role,
            "nps": nps,
            "schedule": sch,
            "id_source": src,
        })
    return rows, flags


def zone_trapped_volume(segments: Any, length_basis: str = "center_to_center",
                        fittings_percent: Any = None, trim_gal: Any = None) -> dict[str, Any]:
    """Pipe gallons from formulas.pipe_volume, plus fittings allowance and trim.

    Center-to-center lengths: 0 percent fittings. Cut lengths with the
    allowance omitted: 5 percent. Trim omitted: 5 gal, flagged as assumed.
    """
    rows, flags = _segments(segments)
    pipe = formulas.pipe_volume([{"d_in": r["d_in"], "length_ft": r["length_ft"]} for r in rows])
    basis = str(length_basis or "center_to_center").strip().lower().replace("-", "_").replace(" ", "_")
    if fittings_percent is None or fittings_percent == "":
        if basis in ("cut", "cut_lengths", "pipe_cut"):
            fittings_percent = 5.0
            flags.append("ASSUMED fittings allowance 5% (cut lengths). Verify with the engineer of record.")
        else:
            fittings_percent = 0.0
            flags.append("fittings allowance 0% (center-to-center lengths already include fitting bodies)")
    fittings_percent = formulas._require_non_negative("fittings_percent", fittings_percent)
    trim_assumed = trim_gal is None or trim_gal == ""
    if trim_assumed:
        trim_gal = 5.0
        flags.append("ASSUMED trim volume 5 gal (no valve data sheet). Verify with the engineer of record.")
    trim_gal = formulas._require_non_negative("trim_gal", trim_gal)
    pipe_gal = float(pipe["volume_gal"])
    zone = pipe_gal * (1.0 + fittings_percent / 100.0) + trim_gal
    detailed = []
    for row, detail in zip(rows, pipe["segments_detail"]):
        detailed.append({**row, "detail": detail})
    return {
        "formula": pipe["formula"],
        "length_basis": basis,
        "pipe_gal": pipe_gal,
        "pipe_ft3": float(pipe["volume_ft3"]),
        "fittings_percent": fittings_percent,
        "fittings_gal": pipe_gal * fittings_percent / 100.0,
        "trim_gal": trim_gal,
        "trim_assumed": trim_assumed,
        "zone_gal": zone,
        "segments": detailed,
        "flags": flags,
    }


def nitrogen_gate(v_gal: Any, p_psig: Any = 40.0, t_min: Any = 30.0) -> dict[str, Any]:
    """Design C is 100. Fill rate is formulas.air_fill_scfm on both bases. C=120 is not the design value."""
    fill = formulas.air_fill_scfm(v_gal, p_psig, t_min)
    ratio = (100.0 / 120.0) ** 1.85
    return {
        "design_c": 100,
        "comparison_c": 120,
        "friction_ratio_c100_vs_c120": ratio,
        "note": (
            "Design Hazen-Williams C is 100 on dry and double-interlock pipe. "
            "C=120 is comparison only and is not the emitted design value. "
            f"Using 120 instead of 100 multiplies friction by about {ratio:.3f}."
        ),
        **fill,
    }


def elect_di_trim(system_type: str, prime_held_by: str = "unknown",
                  failsafe_on_total_power_loss: Any = False,
                  supervisory_psi: Any = None, medium: str = "unelected",
                  insurer: str = "") -> dict[str, Any]:
    """Trim-family screen. No catalog number is elected.

    Asks what holds the prime chamber shut. A pneumatic actuator and an
    electric/electric low-air setting are different bands; mixing them is a
    failed election, not a field tweak.
    """
    raw = str(system_type).strip().lower().replace(" ", "_")
    if raw.replace("-", "_") in {item.replace("-", "_") for item in _STOP_TYPES} or raw in _STOP_TYPES:
        return {
            "status": "RFI-variance",
            "family": None,
            "controlling": False,
            "power_loss_behavior": None,
            "flags": [
                f"{system_type} is out of scope. Wet, dry, and double-interlock preaction only. "
                "No foam, clean agent, mist, deluge, or single-interlock basis of design."
            ],
        }
    st = normalize_system(system_type)
    if st in ("wet", "dry"):
        return {
            "status": "N/A",
            "family": None,
            "controlling": False,
            "system_type": st,
            "power_loss_behavior": None,
            "flags": ["Trim-family election applies to double-interlock zones. Wet and dry do not get a DI trim."],
        }
    if st != "di":
        return {
            "status": "RFI-variance",
            "family": None,
            "controlling": False,
            "flags": [f"Unrecognized system type {system_type!r}. Double-interlock is the only trim path."],
        }

    if isinstance(failsafe_on_total_power_loss, str):
        failsafe = failsafe_on_total_power_loss.strip().lower() not in ("", "false", "0", "no")
    else:
        failsafe = bool(failsafe_on_total_power_loss)
    held = str(prime_held_by or "unknown").strip().lower().replace(" ", "_").replace("-", "_")
    flags = [
        "Status is provisional: this screen does not open a listing sheet. "
        "Specify the valve, solenoid, and panel by function and listing. Do not freeze a catalog number."
    ]
    family = None
    behavior = None
    if failsafe:
        family = "named-failsafe"
        behavior = (
            "On loss of primary and standby power the valve must degrade to a dry-pipe path "
            "(water can still reach a fused sprinkler) rather than stay shut with no water path. "
            "That holding path is pneumatic. Do not copy an electric/electric low-air setting onto it."
        )
        flags.append("Failsafe-on-total-power-loss was requested, so the electric/electric convenience path is not elected.")
    elif held in ("pneumatic_actuator", "pneumatic", "el_pn", "el/pn"):
        family = "El/Pn"
        behavior = (
            "A pneumatic actuator holds the prime. Supervisory pressure follows the elected valve's "
            "air-or-nitrogen versus water-pressure graph. A fixed 15 psi electric/electric number is not that graph."
        )
    elif held in ("nc_solenoid", "solenoid", "el_el", "el/el", "electric"):
        family = "El/El"
        behavior = (
            "A normally closed solenoid holds the prime. Supervisory air or nitrogen serves the low-air "
            "switch only. Do not apply a pneumatic-actuator pressure band."
        )
    else:
        flags.append("Unresolved: what holds the prime chamber shut? Do not default the family.")
        return {
            "status": "unresolved",
            "family": None,
            "controlling": False,
            "system_type": "di",
            "power_loss_behavior": None,
            "medium": medium,
            "flags": flags,
        }

    psi = None
    if supervisory_psi not in (None, ""):
        psi = float(supervisory_psi)
        if family == "El/El" and psi >= 25:
            flags.append(
                f"Collision: supervisory {psi:g} psi is in the pneumatic-actuator band. "
                "Do not mix that band with an electric/electric low-air switch."
            )
        if family == "El/Pn" and psi <= 15:
            flags.append(
                f"Supervisory {psi:g} psi matches a common electric/electric nominal, not an actuator graph. "
                "Read the elected sheet before using it on El/Pn."
            )
    med = str(medium or "unelected").strip().lower()
    if med in ("", "unelected", "unknown"):
        flags.append("Supervisory medium is not elected. The nitrogen gate owns air versus nitrogen. Design C stays 100 if nitrogen is used.")
    if str(insurer).strip().upper() == "FM":
        flags.append(
            "FM DS 5-32 ranks double-interlock late. Where the basis of design is still double-interlock, "
            "flag that conflict to the owner and the insurer. Do not cross-zone two smoke detectors to trip the valve."
        )
    return {
        "status": "provisional",
        "family": family,
        "controlling": True,
        "system_type": "di",
        "prime_held_by": held,
        "supervisory_psi": psi,
        "medium": med,
        "power_loss_behavior": behavior,
        "flags": flags,
    }


def releasing_truth_table(manual_station: Any = True, insurer: str = "FM") -> dict[str, Any]:
    """This solenoid truth table is electric/electric trim.

    Solenoid = (detection leg OR manual station) AND p_second_leg AND NOT isolated.
    p_second_leg (P) is the pressure drop from sprinkler operation, sensed by PSL-REL.
    On electric/pneumatic trim the solenoid is D AND not isolated, and the valve actuator PA-REL gates the valve mechanically, which is outside this table.

    Low air is supervisory only (PSL-SUP). It is not a release input and it is
    not in the Boolean. The second leg is the row key ``p_second_leg`` and the
    Boolean is ``boolean_p``; ``boolean`` carries the same text as ``boolean_p``.

    manual_release is a station inside D (still needs P). A panel zone typed Manual Release
    that bypasses the AND is not modeled and is never a default (C&E skill footnote ⁹ election).

    A second smoke zone does not trip the valve and is not required. No abort
    and no pre-discharge delay on the water path.
    """
    manual_ok = bool(manual_station) and str(manual_station).lower() not in ("false", "0", "no")
    rows = []
    for detection in (False, True):
        for manual in (False, True):
            for p_second_leg in (False, True):
                for isolated in (False, True):
                    for second_smoke in (False, True):
                        det_leg = detection or (manual and manual_ok)
                        solenoid = bool(det_leg and p_second_leg and not isolated)
                        rows.append({
                            "detection": detection,
                            "manual": manual,
                            "p_second_leg": p_second_leg,
                            "isolated": isolated,
                            "second_smoke": second_smoke,
                            "solenoid": solenoid,
                        })
    by_key = {}
    for row in rows:
        key = (row["detection"], row["manual"], row["p_second_leg"], row["isolated"], row["second_smoke"])
        by_key[key] = row["solenoid"]
    for detection in (False, True):
        for manual in (False, True):
            for p_second_leg in (False, True):
                for isolated in (False, True):
                    a = by_key[(detection, manual, p_second_leg, isolated, False)]
                    b = by_key[(detection, manual, p_second_leg, isolated, True)]
                    if a != b:
                        raise RuntimeError("second smoke zone changed the solenoid; truth table is wrong")
    fires = [row for row in rows if row["solenoid"]]
    boolean_p = "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated"
    return {
        "boolean_p": boolean_p,
        "second_leg": ("This solenoid truth table is electric/electric trim. "
                       "p_second_leg is P, the pressure drop from sprinkler operation, sensed by PSL-REL. "
                       "On electric/pneumatic trim the solenoid is D AND not isolated, and the valve actuator "
                       "PA-REL gates the valve mechanically, which is outside this table."),
        "boolean": boolean_p,
        "detection_leg": ("one detection zone, or a manual station in place of that zone. "
                          "manual_release is a station inside D (still needs P). A panel zone typed Manual Release that bypasses the AND is not modeled and is never a default (C&E skill footnote ⁹ election)."),
        "second_smoke": "does not trip the valve and is not required",
        "abort": "no abort and no pre-discharge delay on the water path",
        "manual_station": manual_ok,
        "insurer": insurer,
        "fm_no_cross_zone": str(insurer).strip().upper() == "FM",
        "row_count": len(rows),
        "solenoid_true_count": len(fires),
        "rows": rows,
        "rows_without_second_smoke": [row for row in rows if not row["second_smoke"]],
    }
