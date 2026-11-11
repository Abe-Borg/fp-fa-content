#!/usr/bin/env python3
"""Pure stdlib calc kernel for DC FP arithmetic.

Agents set inputs. This module does the arithmetic. No numpy, no network, no
SprinkFDT / water-delivery-time, no shop-curve invention.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union
from decimal import Decimal, ROUND_FLOOR

# US fire-protection Hazen-Williams (NFPA 13 / handbook form).
HW_COEFF = 4.52
HW_FLOW_EXP = 1.85
HW_DIAM_EXP = 4.87

# psi per foot of water. Stated constant — do not silently swap 0.433.
PSI_PER_FT_WATER = 0.4333

# Hydrant / supply-curve exponent (same 1.85 as HW).
SUPPLY_EXP = 1.85

# Pump envelope defaults (NFPA 20 / FM DS 3-7 screening). CHURN_FRAC_MAX 1.40 = NFPA 20-2019/2022/2025 §6.2.2; P150_FRAC 0.65 = §6.2.1. CHURN_FRAC_PREF 1.20 is practice, not code.
CHURN_FRAC_PREF = 1.20
CHURN_FRAC_MAX = 1.40
NFPA_FLOW_CAP = 1.50
FM_FLOW_CAP = 1.40
P150_FRAC = 0.65
CEILING_PSI_DEFAULT = 175.0


class CalcError(ValueError):
    """Bad inputs. CLI maps this to exit 2."""


Number = Union[int, float]


def _as_float(name: str, value: Any) -> float:
    """Parse a real number. Reject bools, non-numbers, inf, and nan.

    ``float("1e309")`` is inf on IEEE-754. A later ``<= 0`` check does not
    catch it, and dividing by that fill flow collapses the trip time.
    """
    import math

    if isinstance(value, bool) or value is None:
        raise CalcError(f"{name} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CalcError(f"{name} must be a number") from exc
    if not math.isfinite(number):
        raise CalcError(f"{name} must be a finite number")
    return number


def _require_positive(name: str, value: Number) -> float:
    x = _as_float(name, value)
    if x <= 0:
        raise CalcError(f"{name} must be > 0")
    return x


def _require_non_negative(name: str, value: Number) -> float:
    x = _as_float(name, value)
    if x < 0:
        raise CalcError(f"{name} must be >= 0")
    return x


def hazen_williams(
    q_gpm: Number,
    c: Number,
    d_in: Number,
    length_ft: Number,
) -> dict[str, Any]:
    """US fire-protection Hazen-Williams head loss.

    p_psi = 4.52 * L_ft * Q_gpm**1.85 / (C**1.85 * d_in**4.87)
    hf_ft = p_psi / 0.4333
    """
    q = _require_non_negative("q_gpm", q_gpm)
    c_fac = _require_positive("c", c)
    d = _require_positive("d_in", d_in)
    length = _require_non_negative("length_ft", length_ft)

    denom = (c_fac ** HW_FLOW_EXP) * (d ** HW_DIAM_EXP)
    p_psi = HW_COEFF * length * (q ** HW_FLOW_EXP) / denom
    hf_ft = p_psi / PSI_PER_FT_WATER
    return {
        "formula": "Hazen-Williams head loss (US fire protection)",
        "p_psi": p_psi,
        "hf_ft": hf_ft,
        "psi_per_ft_water": PSI_PER_FT_WATER,
    }


def density_area(
    density_gpm_ft2: Number,
    base_area_ft2: Number,
    area_increase: Number = 0,
    hose_gpm: Number = 0,
    duration_min: Optional[Number] = None,
) -> dict[str, Any]:
    """density/area demand + hose (+ optional duration gallons).

    design_area = base_area_ft2 * (1 + area_increase)   # NFPA 13 dry/DI +30%: 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5 / 2010 §11.2.3.2.5 (pulls 13-03, 13-08)
    q_spr = density_gpm_ft2 * design_area
    qd = q_spr + hose_gpm
    gallons = qd * duration_min   # hose already inside qd; labeled
    """
    density = _require_non_negative("density_gpm_ft2", density_gpm_ft2)
    base_area = _require_non_negative("base_area_ft2", base_area_ft2)
    increase = _require_non_negative("area_increase", area_increase)
    hose = _require_non_negative("hose_gpm", hose_gpm)

    design_area = base_area * (1.0 + increase)
    q_spr = density * design_area
    qd = q_spr + hose
    out: dict[str, Any] = {
        "formula": "density/area demand",
        "design_area_ft2": design_area,
        "q_spr_gpm": q_spr,
        "hose_gpm": hose,
        "qd_gpm": qd,
    }
    if duration_min is not None:
        dur = _require_non_negative("duration_min", duration_min)
        out["duration_min"] = dur
        out["gallons"] = qd * dur
        out["gallons_note"] = "hose already inside qd"
    return out


def _one_hydrant_p(ps: float, ph: float, qf: float, q: float) -> float:
    return ps - (ps - ph) * ((q / qf) ** SUPPLY_EXP)


def hydrant_supply(
    ps_psi: Number,
    ph_psi: Number,
    qf_gpm: Number,
    q_gpm: Union[Number, Sequence[Number]],
    derate: Optional[Number] = None,
) -> dict[str, Any]:
    """Two-point hydrant / municipal supply curve.

    P(Q) = Ps - (Ps - Ph) * (Q / Qf)**1.85
    Optional derate is a uniform multiplier on P(Q) (e.g. 0.9 * P).
    """
    ps = _as_float("ps_psi", ps_psi)
    ph = _as_float("ph_psi", ph_psi)
    qf = _require_positive("qf_gpm", qf_gpm)

    if isinstance(q_gpm, (str, bytes)):
        raise CalcError("q_gpm must be a number or a list of numbers")

    if isinstance(q_gpm, Sequence) and not isinstance(q_gpm, (str, bytes)):
        qs = [_require_non_negative("q_gpm", q) for q in q_gpm]
        is_table = True
    else:
        qs = [_require_non_negative("q_gpm", q_gpm)]
        is_table = False

    derate_val: Optional[float] = None
    if derate is not None:
        derate_val = _as_float("derate", derate)
        if derate_val < 0:
            raise CalcError("derate must be >= 0")

    rows = []
    for q in qs:
        p_raw = _one_hydrant_p(ps, ph, qf, q)
        row: dict[str, Any] = {
            "q_gpm": q,
            "p_raw_psi": p_raw,
        }
        if derate_val is not None:
            row["p_derated_psi"] = derate_val * p_raw
        rows.append(row)

    out: dict[str, Any] = {
        "formula": "hydrant/supply curve (2-point)",
        "ps_psi": ps,
        "ph_psi": ph,
        "qf_gpm": qf,
        "derate": derate_val,
        "table": is_table or len(rows) > 1,
        "rows": rows,
    }
    if len(rows) == 1:
        out["q_gpm"] = rows[0]["q_gpm"]
        out["p_raw_psi"] = rows[0]["p_raw_psi"]
        if derate_val is not None:
            out["p_derated_psi"] = rows[0]["p_derated_psi"]
    return out


def pump_envelope(
    qr_gpm: Number,
    pr_psi: Number,
    qd_gpm: Number,
    suction_static_psi: Number,
    churn_frac: Number = CHURN_FRAC_PREF,
    churn_frac_max: Number = CHURN_FRAC_MAX,
    nfpa_flow_cap: Number = NFPA_FLOW_CAP,
    fm_flow_cap: Number = FM_FLOW_CAP,
    p150_frac: Number = P150_FRAC,
    ceiling_psi: Number = CEILING_PSI_DEFAULT,
) -> dict[str, Any]:
    """Listed centrifugal envelope vs a demand pair. Not a shop curve.

    Linear interpolate net at qd between 100% (pr) and 150% (p150_min)
    only when qr <= qd <= 1.5*qr:
        p_net_qd = pr + (p150_min - pr) * (qd - qr) / (0.5 * qr)
    """
    qr = _require_positive("qr_gpm", qr_gpm)
    pr = _require_non_negative("pr_psi", pr_psi)
    qd = _require_non_negative("qd_gpm", qd_gpm)
    suction = _as_float("suction_static_psi", suction_static_psi)
    churn = _require_positive("churn_frac", churn_frac)
    churn_max = _require_positive("churn_frac_max", churn_frac_max)
    nfpa_cap = _require_positive("nfpa_flow_cap", nfpa_flow_cap)
    fm_cap = _require_positive("fm_flow_cap", fm_flow_cap)
    p150f = _require_positive("p150_frac", p150_frac)
    ceiling = _as_float("ceiling_psi", ceiling_psi)

    min_qr_fm = qd / fm_cap
    min_qr_nfpa = qd / nfpa_cap
    qd_over_qr = qd / qr
    churn_net_pref = churn * pr
    churn_net_max = churn_max * pr
    p150_min = p150f * pr
    q150 = 1.5 * qr
    churn_system_pref = churn_net_pref + suction
    churn_system_max = churn_net_max + suction

    qd_le_fm = qd_over_qr <= fm_cap + 1e-12
    qd_le_nfpa = qd_over_qr <= nfpa_cap + 1e-12
    churn_pref_ok = churn_system_pref <= ceiling + 1e-12
    churn_max_ok = churn_system_max <= ceiling + 1e-12

    in_band = (qr <= qd <= q150)
    p_net_qd: Optional[float] = None
    interp_note = (
        "qd outside 100%–150% listed envelope; no interpolation "
        "(do not invent a shop curve)"
    )
    if in_band:
        p_net_qd = pr + (p150_min - pr) * (qd - qr) / (0.5 * qr)
        interp_note = (
            "envelope interpolation (linear in flow between 100% rated net "
            "and 150% flow at p150_frac of rated net). Not a shop curve."
        )

    out: dict[str, Any] = {
        "formula": "pump rated/churn/150% envelope",
        "min_qr_fm_gpm": min_qr_fm,
        "min_qr_nfpa_gpm": min_qr_nfpa,
        "qd_over_qr": qd_over_qr,
        "churn_net_pref_psi": churn_net_pref,
        "churn_net_max_psi": churn_net_max,
        "p150_min_psi": p150_min,
        "q150_gpm": q150,
        "churn_system_pref_psi": churn_system_pref,
        "churn_system_max_psi": churn_system_max,
        "ceiling_psi": ceiling,
        "qd_le_fm_cap": qd_le_fm,
        "qd_le_nfpa_cap": qd_le_nfpa,
        "churn_system_pref_le_ceiling": churn_pref_ok,
        "churn_system_max_le_ceiling": churn_max_ok,
        "interpolation": interp_note,
        "interpolation_applied": in_band,
    }
    if p_net_qd is not None:
        out["p_net_qd_psi"] = p_net_qd
    return out


def louver_free_area(
    cfm: Number,
    face_fpm: Number,
    free_area_pct: Number,
) -> dict[str, Any]:
    """Louver free-area from combustion-air CFM and face velocity.

    free_area_ft2 = cfm / face_fpm
    gross_area_ft2 = free_area_ft2 / (free_area_pct / 100)
    """
    q = _require_positive("cfm", cfm)
    face = _require_positive("face_fpm", face_fpm)
    pct = _as_float("free_area_pct", free_area_pct)
    if pct <= 0:
        raise CalcError("free_area_pct must be > 0")
    if pct > 100:
        raise CalcError("free_area_pct must be <= 100")

    free_area = q / face
    gross_area = free_area / (pct / 100.0)
    return {
        "formula": "louver free-area",
        "free_area_ft2": free_area,
        "gross_area_ft2": gross_area,
        "free_area_pct": pct,
    }


def pipe_volume(segments: Any) -> dict[str, Any]:
    """Water/air volume of a pipe network.

    gal_per_ft = pi/4 * ID^2 / 144 * 7.48 (ID in inches); total = sum(gal_per_ft * L).
    segments: list of {"d_in": ID, "length_ft": L} (aliases id/d, length/l).
    """
    if not isinstance(segments, list) or not segments:
        raise CalcError("segments must be a non-empty list")
    import math
    rows = []
    total = 0.0
    for i, s in enumerate(segments):
        if not isinstance(s, dict):
            raise CalcError(f"segment {i} must be an object")
        d = _require_positive("d_in", s.get("d_in", s.get("id", s.get("d"))))
        L = _require_positive("length_ft", s.get("length_ft", s.get("length", s.get("l"))))
        gpf = math.pi / 4.0 * d * d / 144.0 * 7.48
        v = gpf * L
        total += v
        rows.append(f"{d:g} in x {L:g} ft -> {gpf:.4f} gal/ft, {v:.1f} gal")
    return {"formula": "pipe volume (pi/4*ID^2/144*7.48 gal/ft)", "segments_detail": rows,
            "volume_gal": total, "volume_ft3": total / 7.48}


def fill_bases_text(gauge: float, absolute: float, subject: str = "") -> str:
    """Label both fill rates. This does not elect gauge or absolute."""
    if subject:
        return (
            f"{subject} gauge-basis fill rate is {gauge:.2f} scfm. "
            f"{subject} absolute-basis fill rate is {absolute:.2f} scfm."
        )
    return (
        f"Gauge-basis fill rate is {gauge:.2f} scfm. "
        f"Absolute-basis fill rate is {absolute:.2f} scfm."
    )


def air_fill_scfm(v_gal: Number, p_psig: Number, t_min: Number = 30.0) -> dict[str, Any]:
    """Compressor / N2 fill rate to restore system pressure in t_min.

    KB / Viking basis (gauge): scfm = V*P/(7.48*14.7*T)  (0.012*gal at 40 psig, 30 min).
    Also reports the absolute-pressure (conservative) variant V*(P+14.7)/(7.48*14.7*T).
    Restore rule: NFPA 13-2025 8.2.7.3 (30 min) -- cite in the package, not here.
    ``fill_bases`` states both rates. It does not pick one.
    """
    v = _require_positive("v_gal", v_gal)
    p = _require_positive("p_psig", p_psig)
    t = _require_positive("t_min", t_min)
    gauge = v * p / (7.48 * 14.7 * t)
    absolute = v * (p + 14.7) / (7.48 * 14.7 * t)
    return {"formula": "air/N2 fill scfm = V*P/(7.48*14.7*T)",
            "scfm_gauge_basis": gauge,
            "scfm_abs_basis": absolute,
            "free_air_scf_gauge": v * p / (7.48 * 14.7),
            "fill_bases": fill_bases_text(gauge, absolute)}



def compressor_n2_sizing(systems: Any, t_min: Number = 30.0) -> dict[str, Any]:
    """Dry/DI air-compressor and N2-generator sizing.

    Compressor: sized on the LARGEST single system to restore its supervisory pressure in
    t_min (NFPA 13-2025 s8.2.7.3: 30 min).
    N2 generator: sized on the CAMPUS CONNECTED TOTAL of all systems over the same t_min
    (design practice, not code; verify with engineer of record).
    Each system: {"id", "v_gal", "p_psig"}. Uses air_fill_scfm (gauge + absolute bases).
    """
    if not isinstance(systems, (list, tuple)) or not systems:
        raise ValueError("systems must be a non-empty list of {id, v_gal, p_psig}")
    t = _require_positive("t_min", t_min)
    rows = []
    for i, sy in enumerate(systems):
        r = air_fill_scfm(sy["v_gal"], sy["p_psig"], t)
        rows.append({"id": sy.get("id", f"sys{i+1}"), "v_gal": float(sy["v_gal"]),
                     "p_psig": float(sy["p_psig"]), "scfm_gauge": r["scfm_gauge_basis"],
                     "scfm_abs": r["scfm_abs_basis"]})
    big = max(rows, key=lambda x: x["scfm_abs"])
    campus_gauge = sum(x["scfm_gauge"] for x in rows)
    campus_abs = sum(x["scfm_abs"] for x in rows)
    return {"systems": rows, "largest_system_id": big["id"],
            "compressor_scfm_gauge": big["scfm_gauge"], "compressor_scfm_abs": big["scfm_abs"],
            "n2_campus_scfm_gauge": campus_gauge,
            "n2_campus_scfm_abs": campus_abs,
            "connected_v_gal": sum(x["v_gal"] for x in rows),
            "fill_bases": " ".join((
                fill_bases_text(big["scfm_gauge"], big["scfm_abs"], "Compressor"),
                fill_bases_text(campus_gauge, campus_abs, "N2 campus"),
            )),
            "basis": "compressor: NFPA 13-2025 s8.2.7.3 30-min fill on largest system; "
                     "N2: campus connected total (design practice, not code; verify with engineer of record)"}

def k_factor(k: Number, p_psi: Any = None, q_gpm: Any = None, density: Any = None,
             area_ft2: Any = None, min_p_psi: Any = None) -> dict[str, Any]:
    """Sprinkler/nozzle discharge q = K*sqrt(P) (NFPA 13-2025 K-factor definition; hydraulic calc ch.).

    Modes (exactly one): p_psi -> Q; q_gpm -> P; density (gpm/ft2) + area_ft2 (head coverage)
    -> q_req = density*area, P_req = (q_req/K)^2 floored at min_p_psi.
    Floor: 7 psi = FM DS 2-0 (Oct 2021 / Interim Rev Jan 2024) s2.5.1.1.2 minimum sprinkler design
    pressure; US listings carry the same 7 psi minimum (NFPA 13 pin pending, verify with engineer of record).
    The floor is applied only when min_p_psi is given. When the floor governs, Q is recomputed.
    k_si = 14.4 * K (L/min/bar^0.5; NFPA 13 K-factor table SI column convention).
    """
    import math
    k = _require_positive("k", k)
    modes = [p_psi is not None, q_gpm is not None, density is not None or area_ft2 is not None]
    if sum(modes) != 1:
        raise CalcError("give exactly one of p_psi, q_gpm, or density+area_ft2")
    out: dict[str, Any] = {"k_si": 14.4 * k}
    if p_psi is not None:
        p = _require_positive("p_psi", p_psi)
        out.update({"formula": "q = K*sqrt(P)", "q_gpm": k * math.sqrt(p), "p_psi": p})
    elif q_gpm is not None:
        q = _require_positive("q_gpm", q_gpm)
        out.update({"formula": "P = (Q/K)^2", "q_gpm": q, "p_psi": (q / k) ** 2})
    else:
        d = _require_positive("density", density); a = _require_positive("area_ft2", area_ft2)
        q = d * a
        out.update({"formula": "q_req = density*area; P = (q_req/K)^2", "q_req_gpm": q,
                    "q_gpm": q, "p_psi": (q / k) ** 2})
    if min_p_psi is not None:
        pm = _require_positive("min_p_psi", min_p_psi)
        out["min_p_psi"] = pm
        out["floor_governs"] = out["p_psi"] < pm
        if out["floor_governs"]:
            out["p_psi"] = pm; out["q_gpm"] = k * math.sqrt(pm)
    return out


ELEVATION_CONVENTION = ("dz_ft = rise in the flow direction = elevation of the downstream (remote) node minus "
                        "the upstream (inlet) node; + increases required upstream pressure (0.4333 psi/ft); "
                        "same convention as bor_demand_pressure")
DZ_SIGN_TEXT = "dz(+)=downstream higher"


def tapered_branch(k: Number, p_end_psi: Number, c: Number, segments: Any,
                   min_head_psi: Number = 7.0) -> dict[str, Any]:
    """Multi-node branch line, end-head-first.

    Sources: Hazen-Williams per-foot loss p = 4.52 Q^1.85 / (C^1.85 d^4.87) (NFPA 13-2025 hydraulic
    calc chapter; same constant as hazen_williams op), head flow q = K*sqrt(P) (NFPA 13-2025 K-factor
    definition), elevation 0.4333 psi/ft. 7 psi default minimum head pressure (NFPA 13; section
    re-pin pending). C is an input (lock: C = 100 for dry/DI).

    segments[i] = pipe from node i to node i+1 toward the inlet:
      {"d_in", "length_ft", "eq_ft" (fitting equivalent length, default 0), "dz_ft" (default 0) = rise in the flow
       direction = elevation of the downstream (remote) node i minus the upstream (inlet-side) node i+1;
       + increases the required upstream pressure by 0.4333*dz. Note: the earlier text
       "+ = inlet higher than the downstream node" was wrong; arithmetic unchanged), "head" (head at the upstream node, default True),
       "k" (optional K override for that head)}.
    Node 0 is the most remote head at p_end_psi. Each node's head flows at its own pressure
    (no velocity-pressure correction, no flow balancing at a tee - single-line walk only).
    """
    import math
    k = _require_positive("k", k); p = _require_positive("p_end_psi", p_end_psi)
    c = _require_positive("c", c); pmin = _require_positive("min_head_psi", min_head_psi)
    if not isinstance(segments, list) or not segments:
        raise CalcError("segments must be a non-empty list")
    q = k * math.sqrt(p); nodes = [{"node": 0, "p_psi": p, "q_head_gpm": q, "q_cum_gpm": q}]
    rows = [f"node0 head: p={p:.2f} psi q={q:.2f} gpm"]
    for i, s in enumerate(segments, 1):
        if not isinstance(s, dict):
            raise CalcError(f"segment {i} must be an object")
        d = _require_positive("d_in", s.get("d_in")); L = _require_positive("length_ft", s.get("length_ft"))
        eq = _require_non_negative("eq_ft", s.get("eq_ft", 0.0)); dz = _as_float("dz_ft", s.get("dz_ft", 0.0))
        pf = HW_COEFF * q ** HW_FLOW_EXP / (c ** HW_FLOW_EXP * d ** HW_DIAM_EXP) * (L + eq)
        pe = PSI_PER_FT_WATER * dz
        p = p + pf + pe
        line = f"seg{i} {d:g}in x ({L:g}+{eq:g})ft: Q={q:.2f} pf={pf:.2f} pe={pe:.2f} -> node{i} p={p:.2f}"
        qh = 0.0
        if s.get("head", True):
            kh = _require_positive("k", s.get("k", k)); qh = kh * math.sqrt(p); q += qh
            line += f"; head K{kh:g} q={qh:.2f} -> Q={q:.2f}"
        nodes.append({"node": i, "p_psi": p, "pf_psi": pf, "pe_psi": pe, "dz_ft": dz, "dz_sign": DZ_SIGN_TEXT,
                      "q_head_gpm": qh, "q_cum_gpm": q})
        rows.append(line)
    return {"formula": "tapered branch node walk (HW 4.52, q=K*sqrt(P), 0.4333 psi/ft)", "nodes_detail": rows,
            "nodes": nodes, "q_inlet_gpm": q, "p_inlet_psi": p, "k_equiv_inlet": q / math.sqrt(p),
            "end_head_ok": p_end_psi >= pmin, "min_head_psi": pmin,
            "elevation_convention": ELEVATION_CONVENTION}



def pump_net_at_q(qr_gpm: Number, pr_psi: Number, q_gpm: Any, churn_frac: Number = CHURN_FRAC_PREF,
                  p150_frac: Number = P150_FRAC) -> dict[str, Any]:
    """Net pump pressure at arbitrary flow from the rated point. LISTED ENVELOPE, not a shop curve.

    Basis: NFPA 20-2025 s6.2.1/s6.2.2 (centrifugal pump: shutoff <= 140% of rated pressure; >= 65% of rated
    pressure at 150% of rated flow). Piecewise-linear envelope through three points:
      (0, churn_frac*pr) -> (qr, pr) -> (1.5*qr, p150_frac*pr).
    0 <= Q <= qr:      p = churn*pr + (pr - churn*pr) * Q/qr
    qr < Q <= 1.5*qr:  p = pr + (p150*pr - pr) * (Q - qr)/(0.5*qr)   (same law as pump_envelope)
    Q > 1.5*qr: no value (beyond the NFPA 20-2025 s6.2.1 150% point; flagged, p_net_psi = null).
    Defaults churn 1.20 (preferred) and 0.65 are the conservative envelope; a listed shop curve governs.
    """
    qr = _require_positive("qr_gpm", qr_gpm); pr = _require_positive("pr_psi", pr_psi)
    ch = _require_positive("churn_frac", churn_frac); pf = _require_positive("p150_frac", p150_frac)
    if ch > 1.40 + 1e-12:
        raise CalcError("churn_frac > 1.40 exceeds NFPA 20-2025 s6.2.2 shutoff limit")
    qs = q_gpm if isinstance(q_gpm, list) else [q_gpm]
    if not qs:
        raise CalcError("q_gpm must be a number or non-empty list")
    rows = []; table = []
    for qv in qs:
        q = _require_non_negative("q_gpm", qv)
        if q <= qr:
            p = ch * pr + (pr - ch * pr) * q / qr; seg = "churn-rated"
        elif q <= 1.5 * qr + 1e-9:
            p = pr + (pf * pr - pr) * (q - qr) / (0.5 * qr); seg = "rated-150"
        else:
            p = None; seg = "beyond-150 (NFPA 20-2025 s6.2.1)"
        rows.append({"q_gpm": q, "pct_rated": 100.0 * q / qr, "p_net_psi": p, "segment": seg})
        table.append(f"Q={q:.2f} ({100*q/qr:.1f}%) p_net={'n/a' if p is None else f'{p:.4f}'} psi [{seg}]")
    out = {"formula": "piecewise-linear listed envelope (0,churn*pr)-(qr,pr)-(1.5qr,p150*pr)",
           "churn_net_psi": ch * pr, "p150_net_psi": pf * pr, "q150_gpm": 1.5 * qr, "rows": table,
           "points": rows, "all_within_150": all(r["p_net_psi"] is not None for r in rows),
           "basis": "NFPA 20-2025 s6.2.1/s6.2.2 envelope (Fig A.6.2 RENDER GAP; A.6.2 body not held); not a shop curve (verify with engineer of record vs listed curve)"}
    if len(rows) == 1:
        out["p_net_psi"] = rows[0]["p_net_psi"]
    return out


DI_LIMITS_S = {"FM": 30.0, "NFPA-LH": 60.0, "NFPA-OH": 50.0, "NFPA-EH": 45.0, "NFPA-HP": 40.0, "NFPA-DU": 15.0}
# Dry-pipe water-delivery table times: identical NFPA 13-2019 Table 8.2.3.6.1 ↔ 13-2025 Table 8.2.4.3.2
# (B-DRYED 13-FP006-2019-8.2.3 / 13-FP006-2025-8.2.4). "NFPA" alias = NFPA-OH (data hall analogue).
# edition param only changes citation labels; numerics unchanged.


def _parse_nfpa13_dry_edition(edition: Any) -> int:
    """NFPA 13 dry/DI water-delivery edition gate.

    Held body: 2019 §8.2.3 + Table 8.2.3.6.1 (B-DRYED 13-FP006-2019-8.2.3) and
    2025 §8.2.4 + Table 8.2.4.3.2 (13-FP006-2025-8.2.4). Default 2025 preserves
    prior unlabeled behavior. Other editions (incl. 2022) rejected — not in this gate.
    """
    try:
        ed = int(str(edition).strip())
    except (TypeError, ValueError) as exc:
        raise CalcError("edition must be 2019 or 2025 (NFPA 13 dry/DI delivery; other editions not held)") from exc
    if ed not in (2019, 2025):
        raise CalcError("edition must be 2019 or 2025 (NFPA 13 dry/DI delivery; other editions not held)")
    return ed


def _nfpa13_dry_cites(edition: int) -> dict[str, str]:
    """Edition-correct section/table labels from held B-DRYED bodies. Numerics identical."""
    if edition == 2019:
        return {
            "dry_size_cite": "NFPA 13-2019 s8.2.3.3 (500 gal) / s8.2.3.4 (750 gal w/ QOD)",
            "dry_60s_cite": "NFPA 13-2019 s8.2.3.2 (60 s test-connection OPTION — elected path, not auto-granted)",
            "dry_table_cite": "NFPA 13-2019 Table 8.2.3.6.1",
            "dry_du_cite": "NFPA 13-2019 s8.2.3.1.1 / s8.2.3.6.3 (15 s DU; not a Table 8.2.3.6.1 row)",
            "di_size_cite": "NFPA 13-2019 s8.3.2.3.1.1 (DI <=500 gal: no delivery-time requirement; >500 gal via s8.3.2.3.1.2-.4; QOD may help, s8.3.2.3.2)",
            "di_60s_cite": "NFPA 13-2019 s8.3.2.3.1.2 (DI 60 s test-connection OPTION — elected path, not auto-granted)",
            "di_calc_ptr": "NFPA 13-2019 s8.3.2.3.1.3 → s8.2.3.6 / Table 8.2.3.6.1",
            # Volume-aware cite sections (held)
            "di_calc_sec": "s8.2.3.6", "di_table_sec": "Table 8.2.3.6.1",
            "dry_le500_sec": "§8.2.3.3", "dry_le750_sec": "§8.2.3.4",
        }
    return {
        "dry_size_cite": "NFPA 13-2025 s8.2.4.2.1 (500 gal) / s8.2.4.2.2 (750 gal w/ QOD)",
        "dry_60s_cite": "NFPA 13-2025 s8.2.4.2 (60 s test-connection OPTION — elected path, not auto-granted)",
        "dry_table_cite": "NFPA 13-2025 Table 8.2.4.3.2",
        "dry_du_cite": "NFPA 13-2025 Table 8.2.4.3.2 dwelling-unit row (15 s)",
        "di_size_cite": "NFPA 13-2025 s8.3.2.3.1.1 (DI <=500 gal: no delivery-time requirement; >500 gal via s8.3.2.3.1.2-.4; QOD may help, s8.3.2.3.2)",
        "di_60s_cite": "NFPA 13-2025 s8.3.2.3.1.2 (DI 60 s test-connection OPTION — elected path, not auto-granted)",
        "di_calc_ptr": "NFPA 13-2025 s8.3.2.3.1.3 → s8.2.4.3 / Table 8.2.4.3.2",
        # DI numbering in 2025 is s8.3.2.3.1.x (held); s8.2.4.3 / Table 8.2.4.3.2 are
        # the calc/table homes that .1.3/.1.4 point to; dry <=500/<=750 = s8.2.4.2.1/.2 (held)
        "di_calc_sec": "s8.2.4.3", "di_table_sec": "Table 8.2.4.3.2",
        "dry_le500_sec": "§8.2.4.2.1", "dry_le750_sec": "§8.2.4.2.2",
    }



_V_BASIS_ALIASES = {
    "pipe_only": "pipe-only",
    "pipeonly": "pipe-only",
    "v_allow": "v_allow",
    "vallow": "v_allow",
    "caller": "caller",
    "caller_supplied": "caller",
    "callersupplied": "caller",
}


def _normalize_v_basis(v_basis: Any) -> Any:
    """None stays omitted. Else 'pipe-only' / 'v_allow' / 'caller' (aliases accepted)."""
    if v_basis is None:
        return None
    raw = str(v_basis).strip().lower().replace("-", "_").replace(" ", "_")
    if raw not in _V_BASIS_ALIASES:
        raise CalcError("v_basis must be None, 'pipe-only', 'v_allow' or 'caller'")
    return _V_BASIS_ALIASES[raw]


def _v_basis_clause(v_basis: Any) -> str:
    """Which V the <=500 / <=750 test used. None and pipe-only share one clause.

    The clause no longer says pipe-only V is "tested" as the
    statutory comparison. The <=500 gal DI exemption uses system size (zone_gal), NFPA 13-2019/2025
    s8.3.2.3.1.1. Pipe-only is the reported lower-bound screen. Label only."""
    if v_basis in (None, "pipe-only"):
        return ("V passed is pipe-only trapped volume, a lower-bound screen (not V_allow = pipe × 1.05 + 5 gal, "
                "ASSUMED; verify with engineer of record); the statutory size test uses full system size (zone_gal), "
                "not pipe-only volume")
    if v_basis == "v_allow":
        return ("V tested is V_allow (= pipe × 1.05 + 5 gal, ASSUMED; verify with engineer of record), "
                "not pipe-only trapped volume")
    if v_basis == "caller":
        return ("V tested is caller-supplied v_gal (v_basis=caller), "
                "not labelled pipe-only")
    raise CalcError("v_basis must be None, 'pipe-only', 'v_allow' or 'caller'")


def _delivery_cite_note(st: str, v: float, cites: dict, ed: int, qod: bool = False,
                        basis: str = "FM", v_basis: Any = None) -> tuple[Any, bool]:
    """Volume-aware, basis-aware delivery-time cite.
    Returns (note_body, is_threshold); (None, False) = keep legacy label.

    DI: V <= 500 gal -> NFPA 13 s8.3.2.3.1.1 (no water-delivery test; a threshold, not a cap);
    V > 500 -> one of s8.3.2.3.1.2 / .1.3 / .1.4 must be elected (s8.3.2.3.1 = four alternatives, not tiers).
    Dry (held 2019 s8.2.3.3/.4, 2025 s8.2.4.2.1/.2): V <= 500 no test; <= 750 with QOD no test; else legacy label.
    Claim "FM 30 s governs" only when basis is FM (the backward-compatible default). NFPA-* and
    explicit limit_s (limit_basis "explicit") cite the held NFPA 13 path only — they do not claim FM 30 s.
    The caller-supplied V in di_trip_to_water and dry_delivery_screen is typically pipe-only trapped volume,
    a lower-bound screen, not V_allow (= pipe x 1.05 + 5 gal, ASSUMED; verify with engineer of record). The
    statutory <=500 gal DI comparison uses full system size (zone_gal), NFPA 13-2019/2025 s8.3.2.3.1.1; the note says so and does not call pipe-only V the statutory test.
    Label only: no numeric output depends on this. FM-basis threshold notes stay byte-identical.
    Optional v_basis (None / pipe-only / v_allow / caller) selects the V-tested clause.
    None and pipe-only keep the wording. v_allow and caller must not claim pipe-only.
    FM-basis threshold notes stay byte-identical when v_basis is omitted or pipe-only (no V
    clause); an explicit v_allow / caller appends the clause so the note does not imply pipe-only."""
    thr = 500.0 + 1e-9
    key = str(basis).upper()
    key = "NFPA-OH" if key == "NFPA" else key
    claim_fm = key == "FM"
    vb = _normalize_v_basis(v_basis) if v_basis is not None else None
    v_clause = _v_basis_clause(vb)
    # Append the non-pipe-only clause onto FM notes (which otherwise never mention V)
    # so an explicit v_allow / caller cannot be read as pipe-only. Omitted / pipe-only
    # FM notes stay byte-identical (no V clause).
    attach_fm = vb in ("v_allow", "caller")
    if st == "di":
        if v <= thr:
            if claim_fm:
                _fm = (f"≤500 gal DI no-water-delivery-test threshold (NFPA 13-{ed} §8.3.2.3.1.1) — FM 30 s governs "
                       "(a threshold, not a cap; §8.3.2.3.1.2–.1.4 apply only if elected)")
                return ((_fm + f"; {v_clause}") if attach_fm else _fm), True
            return (f"≤500 gal DI no-water-delivery-test threshold (NFPA 13-{ed} §8.3.2.3.1.1) — "
                    f"a threshold, not a cap; §8.3.2.3.1.2–.1.4 apply only if elected; {v_clause}"), True
        return (f"NFPA 13-{ed} s8.3.2.3.1.2 (60 s) / s8.3.2.3.1.3 (calc, {cites['di_calc_sec']}) / s8.3.2.3.1.4 "
                f"({cites['di_table_sec']}) — one path must be elected (s8.3.2.3.1 = four alternatives, not tiers); "
                "QOD s8.3.2.3.2 may help"), False
    if v <= thr:
        if claim_fm:
            _fm = (f"≤500 gal dry-pipe no-water-delivery-test threshold (NFPA 13-{ed} {cites['dry_le500_sec']}, no QOD) — "
                   "FM 30 s governs (a threshold, not a cap)")
            return ((_fm + f"; {v_clause}") if attach_fm else _fm), True
        return (f"≤500 gal dry-pipe no-water-delivery-test threshold (NFPA 13-{ed} {cites['dry_le500_sec']}, no QOD) — "
                f"a threshold, not a cap; {v_clause}"), True
    if qod and v <= 750.0 + 1e-9:
        if claim_fm:
            _fm = (f"≤750 gal dry-pipe with QOD no-water-delivery-test threshold (NFPA 13-{ed} {cites['dry_le750_sec']}) — "
                   "FM 30 s governs (a threshold, not a cap; confirm dry-pipe, not DI)")
            return ((_fm + f"; {v_clause}") if attach_fm else _fm), True
        return (f"≤750 gal dry-pipe with QOD no-water-delivery-test threshold (NFPA 13-{ed} {cites['dry_le750_sec']}) — "
                f"a threshold, not a cap; confirm dry-pipe, not DI; {v_clause}"), True
    return None, False


def di_trip_to_water(v_gal: Number, q_fill_gpm: Number, t_detect_s: Number = 0.0,
                     t_release_s: Number = 0.0, t_exhaust_s: Number = 0.0,
                     limit_s: Any = None, basis: str = "FM",
                     edition: Any = 2025, system_type: Any = None,
                     v_basis: Any = None) -> dict[str, Any]:
    """SCREEN ONLY - not a listed water-delivery calc.

    t_total = t_detect + t_release + t_exhaust + 60 * V / Q_fill.
    V = trapped pipe volume to the test/remote outlet (gal); Q_fill = average fill flow (gpm) at low
    back-pressure from the supply curve. Sub-times are vendor/test inputs. This ignores air
    compression and transit slowdown, so it is OPTIMISTIC; a pass is necessary, not sufficient.
    Limits (design practice ruling, 2026-10-23): basis "FM" = 30 s (FM DS 5-32, provisional default,
    labeled FM); basis "NFPA-xx" = held dry-pipe water-delivery table times (LH 60 / OH 50 / EH 45 /
    HP 40 / DU 15); "NFPA" = NFPA-OH. Table numerics identical 2019 Table 8.2.3.6.1 ↔ 2025
    Table 8.2.4.3.2 (B-DRYED); edition only changes the cite label (and DU row location note).
    note_60s_option claims "FM 30 s governs" only when limit_basis is FM; NFPA-* /
    explicit limit_s cite the held NFPA 13 path only. The V passed is typically pipe-only trapped V (a
    lower-bound screen, not V_allow = pipe x 1.05 + 5 gal, ASSUMED; verify with engineer of record); the statutory <=500 gal DI
    comparison uses system size (zone_gal), NFPA 13-2019/2025 s8.3.2.3.1.1. Label only;
    FM-default notes byte-identical.
    Do NOT treat the 60 s single-orifice test-connection OPTION (2019 s8.2.3.2 / 2025 s8.2.4.2)
    as automatically granted — it is one of several conditional sizing paths. limit_s overrides
    basis. edition default 2025 (backward compatible); 2019|2025 only.
    system_type: None (default, unchanged: note_60s_option carries the DRY-pipe 60 s cite,
    2019 s8.2.3.2 / 2025 s8.2.4.2) | "dry" (same) | "di" (aliases double-interlock / double_interlock /
    di_preaction): note_60s_option cites the DI 60 s option, NFPA 13 s8.3.2.3.1.2. Label only: no numeric
    output depends on system_type. Any other value raises CalcError.
    with system_type "di" the note is VOLUME-aware (V <= 500 gal: s8.3.2.3.1.1 no-delivery-test
    threshold, not a cap; V > 500: s8.3.2.3.1.2/.1.3/.1.4, one path elected); explicit "dry" with V <= 500 gal gets
    the dry <=500 wording (2019 s8.2.3.3 / 2025 s8.2.4.2.1). system_type None stays byte-identical (legacy dry label).
    with system_type None the output ALSO carries the additive key system_type_default_warning
    ("DEFAULT USED: no system_type -> dry-pipe cite; pass system_type='di' for DI"); absent when system_type is given;
    note_60s_option, the dry default label and every number/verdict unchanged.
        Optional v_basis (None / 'pipe-only' / 'v_allow' / 'caller'; aliases accepted).
    When omitted, every existing key/value stays byte-identical and the v_basis output key is
    absent (the non-FM threshold note carries the lower-bound / zone_gal clause). When
    given, the additive output key reports the label and is threaded through _delivery_cite_note.
    The cite note must not claim "pipe-only" for v_allow or caller. Label only: no numeric or
    verdict output depends on v_basis.
    """
    ed = _parse_nfpa13_dry_edition(edition)
    cites = _nfpa13_dry_cites(ed)
    _st_cite = None
    if system_type is None:
        di_note = False
    else:
        _st = str(system_type).strip().lower().replace("-", "_").replace(" ", "_")
        _st = {"double_interlock": "di", "di_preaction": "di", "dry_pipe": "dry"}.get(_st, _st)
        if _st not in ("dry", "di"):
            raise CalcError("system_type must be None, 'dry' or 'di' (wet/dry/DI locks)")
        di_note = _st == "di"
        _st_cite = _st
    v = _require_positive("v_gal", v_gal); qf = _require_positive("q_fill_gpm", q_fill_gpm)
    td = _require_non_negative("t_detect_s", t_detect_s); tr = _require_non_negative("t_release_s", t_release_s)
    te = _require_non_negative("t_exhaust_s", t_exhaust_s)
    if limit_s is None:
        key = str(basis).upper()
        key = "NFPA-OH" if key == "NFPA" else key
        if key not in DI_LIMITS_S:
            raise CalcError("basis must be FM, NFPA or NFPA-LH/OH/EH/HP/DU (or give limit_s)")
        lim = DI_LIMITS_S[key]; src = key
    else:
        lim = _require_positive("limit_s", limit_s); src = "explicit"
    tf = 60.0 * v / qf; t = td + tr + te + tf
    v_max = (lim - td - tr - te) * qf / 60.0
    if src.startswith("NFPA"):
        table_cite = cites["dry_du_cite"] if src == "NFPA-DU" else cites["dry_table_cite"]
    else:
        table_cite = "FM DS 5-32 provisional 30 s (design practice)" if src == "FM" else "explicit limit_s"
    _vb = _normalize_v_basis(v_basis)
    _nb, _thr = _delivery_cite_note(_st_cite, v, cites, ed, basis=src, v_basis=_vb) if _st_cite else (None, False)
    if _nb is not None:
        _note = _nb if _thr else _nb + " — screen does not auto-elect this path"
    else:
        _note = cites["di_60s_cite" if di_note else "dry_60s_cite"] + " — screen does not auto-elect this path"
    out = {"formula": "t = t_det + t_rel + t_exh + 60*V/Q_fill (screen, optimistic)", "t_fill_s": tf,
           "t_total_s": t, "limit_s": lim, "limit_basis": src, "margin_s": lim - t,
           "passes_screen": t <= lim + 1e-9, "v_max_gal_at_limit": max(v_max, 0.0),
           "edition": ed, "nfpa_table_cite": table_cite,
           "note_60s_option": _note}
    if system_type is None:
        # additive key only; legacy note_60s_option / dry-pipe default label stay byte-identical.
        out["system_type_default_warning"] = "DEFAULT USED: no system_type \u2192 dry-pipe cite; pass system_type='di' for DI"
    if _vb is not None:
        # Additive key only; omitted callers keep every existing key/value byte-identical.
        out["v_basis"] = _vb
    return out


def seismic_fp(sds: Number, ip: Number, wp: Number, z_over_h: Number = 1.0,
               r_mu: Number = 1.3, car: Number = 1.0, rpo: Number = 1.5,
               ta_s: Any = None, at_grade: Any = False) -> dict[str, Any]:
    """ASCE 7-22 Eq. 13.3-1: Fp = 0.4*SDS*Ip*Wp*(Hf/Rmu)*(CAR/Rpo), bounded
    0.3*SDS*Ip*Wp <= Fp <= 1.6*SDS*Ip*Wp. Hf: Ta unknown -> 1 + 2.5(z/h);
    Ta known -> 1 + a1(z/h) + a2(z/h)^10, a1 = min(1/Ta, 2.5), a2 = max(1-(0.4/Ta)^2, 0).
    CAR/Rpo from ASCE 7-22 Table 13.6-1 (held/paid) -> caller input. Rmu >= 1.3.
    """
    sds = _require_positive("sds", sds); ip = _require_positive("ip", ip); wp = _require_positive("wp", wp)
    zh = _require_non_negative("z_over_h", z_over_h)
    if zh > 1: raise CalcError("z_over_h must be <= 1")
    rmu = max(_require_positive("r_mu", r_mu), 1.3)
    car = _require_positive("car", car); rpo = _require_positive("rpo", rpo)
    if at_grade in (True, "true", "True", 1):
        # 13.3.1.1 / 13.3.1.2 (FEMA P-2082-1 2020 text, ASCE 7-22 basis): at/below grade Hf = 1.0, Rmu = 1.0
        hf = 1.0; rmu = 1.0
    elif ta_s is None:
        hf = 1 + 2.5 * zh
    else:
        ta = _require_positive("ta_s", ta_s); a1 = min(1 / ta, 2.5); a2 = max(1 - (0.4 / ta) ** 2, 0.0)
        hf = 1 + a1 * zh + a2 * zh ** 10
    raw = 0.4 * sds * ip * wp * (hf / rmu) * (car / rpo)
    lo = 0.3 * sds * ip * wp; hi = 1.6 * sds * ip * wp
    return {"formula": "ASCE 7-22 13.3-1 Fp (bounded)", "hf": hf, "r_mu_used": rmu,
            "fp_raw": raw, "fp_min": lo, "fp_max": hi, "fp": min(max(raw, lo), hi),
            "fp_over_wp": min(max(raw, lo), hi) / wp}


# NFPA 13-2025 Tables 18.5.5.2 (held rows): max Fpw (lb) by lateral
# brace spacing <=20 / 20-25 / 25-30 / 30-35 / 35-40 ft. Only these rows are held; no others are invented.
BRACE_PIPE_FPW_MAX = {
    "sch40-2": (316, 253, 207, 177, 149),
    "sch40-4": (1807, 1446, 1185, 1016, 850),
    "sch40-6": (4784, 3827, 3136, 2688, 2251),
    "sch10-4": (991, 793, 650, 557, 467),
}


def brace_load(cp: Number, segments: Any, pipe: Any = None, spacing_ft: Any = None,
               listed_capacity_lb: Any = None, angle_deg: Any = None,
               capacity_is_horizontal: Any = False) -> dict[str, Any]:
    """NFPA 13 style lateral brace load: Wp = 1.15 * sum(water-filled lb/ft * ZOI length);
    Fpw = Cp * Wp (NFPA 13-2025 s18.5.9.2 1.15 factor; s18.5.9.3 Fpw = Cp*Wp).
    Cp is a caller input. NFPA 13-2025 has NO Cp table: Cp = 0.754*S_DS (s18.5.9.3), so use
    cp_from_sds(). Older editions (2022 and earlier) used a Cp table vs Ss (docstring fixed;
    prior text "Cp from NFPA 13 seismic coefficient table (held)" was stale for 2025).
    segments: [{"lb_per_ft": w, "length_ft": L}].
    Optional: pipe + spacing_ft -> Tables 18.5.5.2 max Fpw check (pipe_ok);
    listed_capacity_lb + angle_deg -> capacity / Table 18.5.2.3 angle divisor (brace_ok).
    Divisor reading of Table 18.5.2.3 = corpus interpretation, verify with engineer of record.
    Fix (design practice): capacity_is_horizontal=True for FM
    horizontal ASD listings (e.g. Anvil Fig. 770 FM column, already resolved to horizontal and /1.5)
    -> angle divisor NOT applied (FM factor applied once). Default False keeps the UL/axial path.
    """
    cp = _require_positive("cp", cp)
    if not isinstance(segments, list) or not segments:
        raise CalcError("segments must be a non-empty list")
    w = 0.0; rows = []
    for i, s in enumerate(segments):
        lb = _require_positive("lb_per_ft", s.get("lb_per_ft")); L = _require_positive("length_ft", s.get("length_ft"))
        w += lb * L; rows.append(f"{lb:g} lb/ft x {L:g} ft = {lb*L:.1f} lb")
    wp = 1.15 * w
    out = {"formula": "Fpw = Cp*Wp, Wp = 1.15*water-filled ZOI weight", "segments_detail": rows,
           "w_pipe_lb": w, "wp_lb": wp, "fpw_lb": cp * wp}
    # optional pipe-capacity and brace-angle checks.
    if pipe is not None or spacing_ft is not None:
        if pipe not in BRACE_PIPE_FPW_MAX or spacing_ft is None:
            raise CalcError(f"pipe must be one of {sorted(BRACE_PIPE_FPW_MAX)} with spacing_ft")
        sp = _require_positive("spacing_ft", spacing_ft)
        if sp > 40:
            raise CalcError("lateral spacing > 40 ft exceeds NFPA 13-2025 Tables 18.5.5.2 range")
        col = 0 if sp <= 20 else 1 if sp <= 25 else 2 if sp <= 30 else 3 if sp <= 35 else 4
        cap = BRACE_PIPE_FPW_MAX[pipe][col]
        out.update({"pipe_fpw_max_lb": cap, "pipe_ok": cp * wp <= cap})
    if listed_capacity_lb is not None:
        cap = _require_positive("listed_capacity_lb", listed_capacity_lb)
        ang = _require_positive("angle_deg", angle_deg if angle_deg is not None else 90)
        if ang < 30 or ang > 90:
            raise CalcError("angle_deg must be 30-90 (NFPA 13-2025 Table 18.5.2.3 range)")
        horiz = bool(capacity_is_horizontal) and str(capacity_is_horizontal).lower() not in ("false", "0", "no")
        div = 1.0 if horiz else (2.0 if ang < 45 else 1.414 if ang < 60 else 1.155 if ang < 90 else 1.0)
        out.update({"capacity_is_horizontal": horiz, "angle_divisor": div, "brace_cap_lb": cap / div,
                    "brace_ok": cp * wp <= cap / div})
    return out


def brace_spacing_max(cp: Number, pipe: Any, main_lb_per_ft: Number,
                      branch_lb_per_main_ft: Number = 0.0, listed_capacity_lb: Any = None,
                      angle_deg: Any = None, capacity_is_horizontal: Any = False) -> dict[str, Any]:
    """Max lateral brace spacing, chained to cp_from_sds.
    For each held NFPA 13-2025 Tables 18.5.5.2 column upper bound (20/25/30/35/40 ft):
    ZOI weight = (main_lb_per_ft + branch_lb_per_main_ft) * S; Wp = 1.15*ZOI (s18.5.9.2);
    Fpw = Cp*Wp (s18.5.9.3); pass if Fpw <= table max for pipe (and <= listed/angle divisor
    if given). Returns the largest passing S. branch_lb_per_main_ft = tributary branch-line
    water-filled weight per ft of main (caller's ZOI reading; verify with engineer of record).
    """
    cp = _require_positive("cp", cp)
    if pipe not in BRACE_PIPE_FPW_MAX:
        raise CalcError(f"pipe must be one of {sorted(BRACE_PIPE_FPW_MAX)}")
    wm = _require_positive("main_lb_per_ft", main_lb_per_ft)
    wb = float(branch_lb_per_main_ft or 0.0)
    if wb < 0:
        raise CalcError("branch_lb_per_main_ft must be >= 0")
    bcap = None
    if listed_capacity_lb is not None:
        r = brace_load(cp, [{"lb_per_ft": 1.0, "length_ft": 1.0}], listed_capacity_lb=listed_capacity_lb,
                       angle_deg=angle_deg, capacity_is_horizontal=capacity_is_horizontal)
        bcap = r["brace_cap_lb"]
    rows = []; best = None
    for col, S in enumerate((20, 25, 30, 35, 40)):
        fpw = cp * 1.15 * (wm + wb) * S
        tcap = BRACE_PIPE_FPW_MAX[pipe][col]
        ok = fpw <= tcap and (bcap is None or fpw <= bcap)
        rows.append(f"S={S} ft: Fpw={fpw:.1f} lb vs table {tcap}" + (f" / brace {bcap:.1f}" if bcap else "") + (" OK" if ok else " FAIL"))
        if ok:
            best = S
    return {"formula": "max S in {20..40} with Cp*1.15*(w_main+w_branch)*S <= Table 18.5.5.2 max",
            "rows": rows, "max_spacing_ft": best if best is not None else 0,
            "brace_cap_lb": bcap, "any_pass": best is not None}


def diesel_derate(pump_bhp: Number, altitude_ft: Number = 0.0, ambient_f: Number = 77.0,
                  nameplate_hp: Any = None, stepwise: Any = False, gear_loss_hp: Number = 0.0) -> dict[str, Any]:
    """Diesel engine derate, ADDITIVE.
    NFPA 20-2025 s11.2.2.4: deduct 3 % per 1,000 ft above 300 ft; s11.2.2.5: deduct 1 % per 10 F
    above 77 F (2022 text identical). The code gives no combination rule; ADDITIVE
    (1 - (a+t)/100) is the design practice ruling (larger deduction), verify with engineer of record.
    s11.2.2.6 gear-drive loss is a caller input (added to pump BHP). s11.2.2.7: derated engine
    rating >= pump BHP. Default prorates continuously; stepwise=True counts whole 1,000 ft / 10 F steps.
    """
    bhp = _require_positive("pump_bhp", pump_bhp) + _require_non_negative("gear_loss_hp", gear_loss_hp)
    alt = _as_float("altitude_ft", altitude_ft); amb = _as_float("ambient_f", ambient_f)
    step = bool(stepwise) and str(stepwise).lower() not in ("false", "0", "no")
    da = max(0.0, alt - 300.0) / 1000.0; dt = max(0.0, amb - 77.0) / 10.0
    if step:
        da = float(int(da)); dt = float(int(dt))
    a_pct = 3.0 * da; t_pct = 1.0 * dt
    factor = 1.0 - (a_pct + t_pct) / 100.0
    if factor <= 0:
        raise CalcError("derate >= 100 %; inputs out of range")
    req = bhp / factor
    out = {"formula": "required_hp = (BHP + gear) / (1 - (3*(alt-300)/1000 + 1*(T-77)/10)/100)",
           "alt_deduction_pct": a_pct, "temp_deduction_pct": t_pct, "total_deduction_pct": a_pct + t_pct,
           "derate_factor": factor, "required_engine_hp": req,
           "basis": "NFPA 20-2025 s11.2.2.4/.5 (additive per design practice), s11.2.2.7"}
    if nameplate_hp is not None:
        np_ = _require_positive("nameplate_hp", nameplate_hp)
        out.update({"nameplate_hp": np_, "derated_hp": np_ * factor, "engine_ok": np_ * factor >= bhp - 1e-9,
                    "deficit_hp": max(0.0, req - np_)})
    return out


def electric_overpressure(net_shutoff_psi: Number, max_static_suction_psi: Number,
                          component_rating_psi: Number = 175.0, elevation_ft: Number = 0.0,
                          vs_set_psi: Any = None, vs_variance_psi: Number = 0.0,
                          relief_credited: Any = False) -> dict[str, Any]:
    """Electric (constant- or variable-speed) pump maximum-pressure check.
    NFPA 20-2025 s4.7.7.1: net churn + max static suction, adjusted for elevation, <= component rating.
    Electric constant speed: no overspeed factor (contrast relief_check diesel 1.21).
    elevation_ft = height of the governing component ABOVE the pump discharge (negative = below);
    adjustment = -0.4333 psi/ft * elevation_ft (lowest component governs -> pass a negative value).
    NFPA 20-2025 s4.7.7.2: relief valves / PRVs shall NOT be the means to meet s4.7.7.1 ->
    relief_credited=True never changes the verdict. s4.7.7.3.1: a variable speed pump is acceptable to
    limit system pressure; s4.7.7.3.2: set + max variance, adjusted for elevation, <= rating of any
    component. s4.20 main relief [verify NFPA 20-2025 s4.20].
    """
    sh = _require_non_negative("net_shutoff_psi", net_shutoff_psi)
    st = _require_non_negative("max_static_suction_psi", max_static_suction_psi)
    rating = _require_positive("component_rating_psi", component_rating_psi)
    elev_adj = -PSI_PER_FT_WATER * _as_float("elevation_ft", elevation_ft)
    churn_max = sh + st + elev_adj
    ok_churn = churn_max <= rating + 1e-9
    out = {"formula": "P_max = net_churn + static_suction - 0.4333*elev_ft <= rating (s4.7.7.1); VSP: set + variance - 0.4333*elev_ft <= rating (s4.7.7.3.2)",
           "elevation_adj_psi": elev_adj, "churn_max_psi": churn_max, "component_rating_psi": rating,
           "churn_ok_4771": ok_churn, "churn_margin_psi": rating - churn_max,
           "relief_credited": bool(relief_credited) and str(relief_credited).lower() not in ("false", "0", "no"),
           "relief_note": "NFPA 20-2025 s4.7.7.2: relief/PRV not a means to meet s4.7.7.1; s4.20 [verify]"}
    vs_ok = None
    if vs_set_psi is not None:
        vsp = _require_positive("vs_set_psi", vs_set_psi) + _require_non_negative("vs_variance_psi", vs_variance_psi) + elev_adj
        vs_ok = vsp <= rating + 1e-9
        out.update({"vs_max_psi": vsp, "vs_ok_47732": vs_ok, "vs_margin_psi": rating - vsp})
    if ok_churn:
        path = "constant-speed OK (s4.7.7.1)"
    elif vs_ok:
        path = "variable speed limits pressure (s4.7.7.3.1/.3.2)"
    else:
        path = "FAIL: raise component ratings or use VSP; relief/PRV not permitted (s4.7.7.2)"
    out.update({"compliant": bool(ok_churn or vs_ok), "compliance_path": path,
                "basis": "NFPA 20-2025 s4.7.7.1, s4.7.7.2, s4.7.7.3.1, s4.7.7.3.2; s4.20 [verify]"})
    return out


# --- dispatch helpers for run.py ---

def cp_from_sds(sds: Any = None, attach_height_ratio: Any = None,
                apply_height_factor: bool = False) -> dict[str, Any]:
    """Seismic coefficient Cp.

    NFPA 13-2025 s18.5.9.3 (OCR L25385-25387): Fpw = Cp*Wp, Cp = 0.754*S_DS.
    s18.5.9.5 (L25412-25413): where data for Cp are not available, Cp = 0.5.
    Permitted reductions (only if apply_height_factor): s18.5.9.3.3 attachment at 51-75 %
    of average roof height -> x0.875; s18.5.9.3.4 below 50 % -> x0.75. The 50-51 % band and
    ratios > 0.75 get no factor (the text is silent / not permitted). S_DS comes from the AHJ
    or the ASCE 7 Hazard Tool (s18.5.9.3.1); default site class unless AHJ (s18.5.9.3.2).
    """
    if sds is None:
        cp_base = 0.5
        basis = "NFPA 13-2025 s18.5.9.5 default Cp=0.5 (no S_DS data)"
    else:
        sds_v = _require_positive("sds", sds)
        cp_base = 0.754 * sds_v
        basis = "NFPA 13-2025 s18.5.9.3 Cp=0.754*S_DS"
    factor = 1.0
    if apply_height_factor:
        if attach_height_ratio is None:
            raise CalcError("attach_height_ratio required when apply_height_factor is true")
        r = float(attach_height_ratio)
        if r <= 0 or r > 1.5:
            raise CalcError("attach_height_ratio must be in (0, 1.5]")
        if 0.51 <= r <= 0.75:
            factor = 0.875
            basis += "; x0.875 s18.5.9.3.3"
        elif r < 0.50:
            factor = 0.75
            basis += "; x0.75 s18.5.9.3.4"
    return {"cp_base": round(cp_base, 4), "height_factor": factor,
            "cp": round(cp_base * factor, 4), "basis": basis}


def relief_check(net_shutoff_psi: Number, max_static_suction_psi: Number,
                 component_rating_psi: Number = 175.0, elevation_adj_psi: Number = 0.0,
                 edition: Any = 2025) -> dict[str, Any]:
    """Diesel main relief valve test.

    edition=2025 (default, unchanged) -> NFPA 20-2025 s4.20.1.2. edition=2016 -> NFPA 20-2016
    s4.19.1.2:
    same 121% rule (121% of the net rated shutoff (churn) pressure plus the maximum static
    suction pressure, adjusted for elevation). Factor 1.21 is quoted in both editions; only the
    section/edition cite changes. Other editions raise CalcError (not held). SCREEN; verify with engineer of record.

    NFPA 20-2025 s4.20.1.2 (paraphrase): where a diesel engine fire pump is installed and 121% of
    the net rated shutoff (churn) pressure plus the maximum static suction pressure, adjusted for
    elevation, exceeds the pressure rating of the system components, a main relief valve is required.
    relief_check_psi = 1.21*net_shutoff + max_static_suction + elevation_adj (elevation_adj is
    signed: negative for components above the pump). Uses the NET SHUTOFF, not the rated net;
    kernel pump_envelope churn_frac is a different quantity.
    """
    sh = _require_positive("net_shutoff_psi", net_shutoff_psi)
    st = float(max_static_suction_psi)
    if st < 0:
        raise CalcError("max_static_suction_psi must be >= 0")
    rt = _require_positive("component_rating_psi", component_rating_psi)
    try:
        ed = int(edition)
    except (TypeError, ValueError):
        raise CalcError("edition must be 2016 or 2025")
    if ed == 2025:
        basis = "NFPA 20-2025 s4.20.1.2 (diesel)"
    elif ed == 2016:
        basis = ("NFPA 20-2016 s4.19.1.2 (diesel 121% rule; Canada/AE pin) - SCREEN, verify with engineer of record")
    else:
        raise CalcError("edition must be 2016 or 2025 (other editions not held)")
    metric = 1.21 * sh + st + float(elevation_adj_psi or 0.0)
    return {"relief_check_psi": round(metric, 2), "component_rating_psi": rt,
            "relief_valve_required": metric > rt, "margin_psi": round(rt - metric, 2),
            "edition": ed, "basis": basis}


def junction_balance(q_low_gpm: Number, p_low_psi: Number, p_high_psi: Number,
                     q_high_gpm: Number = 0.0, tol_psi: Number = 0.5) -> dict[str, Any]:
    """Two-path hydraulic junction balance.

    NFPA 13-2025 s28.2.2.4.1: pressures at hydraulic junction points shall balance within
    0.5 psi; s28.2.2.4.2: carry the highest pressure and the adjusted total flow forward.
    Adjustment uses Q = K*sqrt(P) (same law as k_factor): the low-pressure path is treated as
    an equivalent K = q_low/sqrt(p_low) and its flow is raised to p_high:
    q_adj = q_low*sqrt(p_high/p_low). If |p_high - p_low| <= tol_psi, the code allows the
    junction as balanced (flows simply add); q_adj is still reported.
    """
    import math
    ql = _require_positive("q_low_gpm", q_low_gpm)
    pl = _require_positive("p_low_psi", p_low_psi)
    ph = _require_positive("p_high_psi", p_high_psi)
    if ph < pl:
        raise CalcError("p_high_psi must be >= p_low_psi")
    qh = float(q_high_gpm or 0.0)
    if qh < 0:
        raise CalcError("q_high_gpm must be >= 0")
    k_eq = ql / math.sqrt(pl)
    q_adj = k_eq * math.sqrt(ph)
    dp = ph - pl
    return {"k_equiv": round(k_eq, 4), "q_low_adjusted_gpm": round(q_adj, 2),
            "q_total_gpm": round(qh + q_adj, 2), "p_carried_psi": ph,
            "delta_p_psi": round(dp, 3), "within_tolerance": dp <= float(tol_psi),
            "basis": "NFPA 13-2025 s28.2.2.4.1-.2; Q=K*sqrt(P)"}


def dry_delivery_screen(segments: Any, q_fill_gpm: Number, qod: Any = False,
                        t_detect_s: Number = 0.0, t_release_s: Number = 0.0,
                        t_exhaust_s: Number = 0.0, limit_s: Any = None,
                        basis: str = "FM", system_type: Any = None,
                        edition: Any = 2025, declared_interlock: Any = None) -> dict[str, Any]:
    """Chained op:
    pipe_volume(segments) -> NFPA 13 dry/DI size-exemption check -> di_trip_to_water screen.
    SCREEN ONLY, optimistic (see di_trip_to_water).

    500 gal is a THRESHOLD, not a cap. NFPA 13-2019 s8.3.2.3.1.1: a DI system
    of <=500 gal needs no water-delivery test; larger DI uses s8.3.2.3.1.2 (60 s) / .1.3 (calc) / .1.4. The 750 gal
    QOD size is dry-pipe only (2019 s8.2.3.4). FM 30 s still governs. Output key nfpa_size_cap_gal is a legacy
    name kept for compatibility (it is this threshold).
    nfpa_size_threshold_gal = the same value (the correct name): threshold (DI 500) /
    dry-pipe QOD size (750, 2019 s8.2.3.4, dry only); not a cap. nfpa_size_cap_gal stays as a legacy alias. DI note_60s_option now cites s8.3.2.3.1.2.
    Size caps identical in held 2019/2025 bodies: dry <=500 gal no QOD / <=750 with QOD
    (2019 s8.2.3.3/.4; 2025 s8.2.4.2.1/.2); DI <=500 gal (s8.3.2.3.1.1 both editions) — QOD
    does not extend DI size (s8.3.2.3.2). The 60 s test-connection OPTION is NOT auto-granted
    when volume exceeds the size exemption (caller must elect that path separately).
    FM DS 5-32 provisional 30 s default still applies when basis=FM (design practice).
    "FM 30 s governs" is claimed only when basis/limit_basis is FM; NFPA-* / explicit
    limit_s cite the held NFPA 13 path only (DI s8.3.2.3.1.1 / dry 2019 s8.2.3.3/.4 = 2025 s8.2.4.2.1/.2).
    V here is pipe-only trapped V from pipe_volume, a lower-bound screen, not V_allow
    (= pipe x 1.05 + 5 gal, ASSUMED; verify with engineer of record). `nfpa_delivery_time_exempt` is that pipe-only
    lower-bound screen and does not by itself claim the exemption; the statutory <=500 gal DI comparison uses
    full system size (zone_gal), NFPA 13-2019/2025 s8.3.2.3.1.1. Key name kept (rename deferred).
    Label only; FM-default notes byte-identical.
    note_60s_option is VOLUME-aware (DI <=500 gal s8.3.2.3.1.1 threshold; DI >500 elected
    .1.2/.1.3/.1.4; dry <=500 / <=750 with QOD -> 2019 s8.2.3.3/.4, 2025 s8.2.4.2.1/.2; dry above that keeps the
    path-specific s8.2.3.2 / s8.2.4.2 label). Label only; all numerics and verdicts unchanged.
    edition default 2025 (backward compatible); 2019|2025 only.
    declared_interlock: None (default, unchanged) | "none" |
    "double". "double" with system_type="dry" -> CalcError (a DI zone typed 'dry' would get the dry-pipe
    750 gal QOD cap; NFPA 13-2019 s8.3.2.3.1.1 / s8.3.2.3.2, held 13-FP006-2019-8.3.2.3). When
    system_type="dry", QOD on and 500 < V <= 750 gal, outputs add qod_750_cap_basis + warning
    "confirm dry-pipe, not DI". Granted caps, verdicts and di_trip_to_water arithmetic unchanged.
    system_type default is None (omitted). Output system_type stays "dry" and every
    existing key/value stays byte-identical; an additive key system_type_default_warning reports
    "DEFAULT USED: no system_type -> dry-pipe path; pass system_type='di' for DI". The key is
    absent when system_type is given (including explicit "dry"). Same pattern as the key
    on di_trip_to_water. nfpa_size_cap_gal is a legacy alias of nfpa_size_threshold_gal (a threshold,
    not a cap); both keys stay equal and both remain readable. Alias-safe; no numeric change.
    """
    ed = _parse_nfpa13_dry_edition(edition)
    cites = _nfpa13_dry_cites(ed)
    pv = pipe_volume(segments)
    v = float(pv["volume_gal"])
    q = bool(qod) and str(qod).lower() not in ("false", "0", "no")
    _system_type_defaulted = system_type is None
    if _system_type_defaulted:
        st = "dry"
    else:
        st = str(system_type).strip().lower().replace("-", "_").replace(" ", "_")
        st = {"double_interlock": "di", "di_preaction": "di", "dry_pipe": "dry"}.get(st, st)
        if st not in ("dry", "di"):
            raise CalcError("system_type must be 'dry' or 'di' (wet/dry/DI locks; single-interlock not supported)")
    di_decl = None if declared_interlock is None else str(declared_interlock).strip().lower().replace("-", "_")
    di_decl = {"double_interlock": "double"}.get(di_decl, di_decl)
    if di_decl not in (None, "none", "double"):
        raise CalcError("declared_interlock must be None, 'none' or 'double' (wet/dry/DI locks)")
    if di_decl == "double" and st == "dry":
        raise CalcError("declared_interlock='double' with system_type='dry' (DI zone typed dry): "
                        + cites["di_size_cite"] + " — the dry-pipe QOD 750 gal cap ("
                        + cites["dry_size_cite"] + ") is not available to DI (held 13-FP006-2019-8.3.2.3); "
                        "re-run with system_type='di'")
    # DI gets NO 750 gal QOD size exemption (held 2019+2025 s8.3.2.3.1.1 / .2).
    cap = 750.0 if (q and st == "dry") else 500.0
    exempt = v <= cap + 1e-9
    trip = di_trip_to_water(v, q_fill_gpm, t_detect_s, t_release_s, t_exhaust_s, limit_s, basis, edition=ed,
                            system_type=st)
    nb = cites["di_size_cite"] if st == "di" else cites["dry_size_cite"]
    _vb, _vthr = _delivery_cite_note(st, v, cites, ed, q, basis=trip["limit_basis"])  # basis-aware
    if _vb is not None:
        _n60 = _vb if _vthr else _vb + " — not auto-granted by size-exemption screen"
    else:
        _n60 = cites["di_60s_cite" if st == "di" else "dry_60s_cite"] + " — not auto-granted by size-exemption screen"
    out = {"volume_gal": v, "system_type": st, "qod": q, "nfpa_size_cap_gal": cap,
           "nfpa_size_threshold_gal": cap, "nfpa_delivery_time_exempt": exempt, "nfpa_basis": nb, "edition": ed,
           "note_60s_option": _n60}
    out.update({k: trip[k] for k in ("t_fill_s", "t_total_s", "limit_s", "limit_basis",
                                      "margin_s", "passes_screen", "v_max_gal_at_limit",
                                      "nfpa_table_cite")})
    out["formula"] = "V=sum(pi/4*ID^2/144*7.48*L); t = t_det + t_rel + t_exh + 60*V/Q_fill"
    if di_decl is not None:
        out["declared_interlock"] = di_decl
    if st == "dry" and q and 500.0 < v <= 750.0 + 1e-9:
        out["qod_750_cap_basis"] = (cites["dry_size_cite"] + " — 750 gal cap is dry-pipe + QOD only; DI stays 500 gal ("
                                    + cites["di_size_cite"] + ")")
        out["warning"] = ("dry+QOD 500-750 gal: 750 gal cap granted — confirm dry-pipe, not DI "
                          "(a DI zone must use system_type='di' / declared_interlock='double')")
    if _system_type_defaulted:
        # additive key only; system_type stays "dry"; every existing key/value byte-identical.
        out["system_type_default_warning"] = "DEFAULT USED: no system_type → dry-pipe path; pass system_type='di' for DI"
    return out
def cross_main_walk(c: Number, branches: Any, segments: Any, tol_psi: Number = 0.5) -> dict[str, Any]:
    """Cross-main walk with a junction balance at every branch tee.

    branches[0] is the most remote branch line; each item is either {"q_gpm", "p_psi"} (inlet
    already known) or {"tapered": {k, p_end_psi, c, segments, min_head_psi}} (computed by
    tapered_branch). segments[i] = cross-main pipe from branch i's tee to branch i+1's tee
    {"d_in", "length_ft", "eq_ft"=0, "dz_ft"=0}; dz_ft = rise in the flow direction = elevation of
    the downstream (remote-side) tee minus the upstream (riser-side) tee; + increases the required
    upstream pressure by 0.4333*dz (same as bor_demand_pressure). An optional extra last segment carries the total
    to the riser/feed point. HW 4.52 Q^1.85/(C^1.85 d^4.87) (NFPA 13-2025 hydraulic calc chapter),
    0.4333 psi/ft elevation. At each tee: NFPA 13-2025 s28.2.2.4.1-.2 via junction_balance -
    the lower-pressure side is raised to the higher pressure by Q=K*sqrt(P) and the higher
    pressure is carried. C is an input (company lock: C=100 for wet, dry and DI; no nitrogen
    C-credit). No velocity pressure. SCREEN - verify with engineer of record for submittal use.
    """
    c = _require_positive("c", c)
    if not isinstance(branches, list) or not branches:
        raise CalcError("branches must be a non-empty list")
    if not isinstance(segments, list) or len(segments) not in (len(branches) - 1, len(branches)):
        raise CalcError("segments must have len(branches)-1 items (+1 optional tail to riser)")

    def _branch(i, b):
        if not isinstance(b, dict):
            raise CalcError(f"branch {i} must be an object")
        if "tapered" in b:
            t = b["tapered"]
            r = tapered_branch(t.get("k"), t.get("p_end_psi"), t.get("c", c), t.get("segments"),
                               t.get("min_head_psi", 7.0))
            return r["q_inlet_gpm"], r["p_inlet_psi"]
        return _require_positive("q_gpm", b.get("q_gpm")), _require_positive("p_psi", b.get("p_psi"))

    q, p = _branch(0, branches[0])
    rows = [f"branch0 inlet: Q={q:.2f} gpm P={p:.2f} psi"]
    tees = []; seg_detail = []
    for i, s in enumerate(segments, 1):
        if not isinstance(s, dict):
            raise CalcError(f"segment {i} must be an object")
        d = _require_positive("d_in", s.get("d_in")); L = _require_positive("length_ft", s.get("length_ft"))
        eq = _require_non_negative("eq_ft", s.get("eq_ft", 0.0)); dz = _as_float("dz_ft", s.get("dz_ft", 0.0))
        pf = HW_COEFF * q ** HW_FLOW_EXP / (c ** HW_FLOW_EXP * d ** HW_DIAM_EXP) * (L + eq)
        pe = PSI_PER_FT_WATER * dz
        p = p + pf + pe
        seg_detail.append({"segment": i, "q_gpm": q, "pf_psi": pf, "dz_ft": dz, "pe_psi": pe,
                           "dz_sign": DZ_SIGN_TEXT, "p_after_psi": p})
        line = f"cm{i} {d:g}in x ({L:g}+{eq:g})ft: Q={q:.2f} pf={pf:.3f} pe={pe:.3f} -> P={p:.2f}"
        if i < len(branches):
            qb, pb = _branch(i, branches[i])
            if p >= pb:
                jb = junction_balance(qb, pb, p, q, tol_psi); side = "branch raised"
            else:
                jb = junction_balance(q, p, pb, qb, tol_psi); side = "cross main raised"
            q = float(jb["q_total_gpm"]); p = float(jb["p_carried_psi"])
            tees.append({"tee": i, "branch_q_gpm": qb, "branch_p_psi": pb, "adjusted": side,
                         "delta_p_psi": jb["delta_p_psi"], "within_tolerance": jb["within_tolerance"],
                         "q_total_gpm": q, "p_psi": p})
            line += f"; tee{i} branch {qb:.2f}@{pb:.2f} ({side}, dP={jb['delta_p_psi']}) -> Q={q:.2f} P={p:.2f}"
        else:
            line += " (tail to riser)"
        rows.append(line)
    return {"formula": "cross main walk: HW per segment + junction_balance at each tee", "rows": rows,
            "tees": tees, "q_total_gpm": round(q, 2), "p_inlet_psi": round(p, 3),
            "all_tees_within_tolerance": all(t["within_tolerance"] for t in tees),
            "segments_detail": seg_detail, "elevation_convention": ELEVATION_CONVENTION,
            "basis": "NFPA 13-2025 s28.2.2.4.1-.2; HW 4.52/1.85/4.87; verify with engineer of record"}


def battery_standby(loads: Any, standby_h: Number = 24.0, alarm_min: Number = 5.0,
                    aging_factor: Number = 1.25, vendor_derate: Any = None,
                    battery_ah: Any = None) -> dict[str, Any]:
    """FA / releasing secondary-power battery capacity.

    AH_req = (sum(I_stby_A) * standby_h + sum(I_alarm_A) * alarm_min/60) * aging_factor
    NFPA 72-2025 s10.6.7.2.1 (24 h quiescent), s10.6.7.2.2 (5 min alarm), s10.6.7.2.13 (all loads
    not auto-disconnected), s10.6.7.2.14 (>= 1.25 aging correction). Optional vendor_derate (e.g.
    0.80 per Potter IOM) reported as a separate, more conservative line (AH_req / derate).
    loads: list of {"id", "qty", "standby_ma", "alarm_ma"} (per-unit mA).
    """
    if not isinstance(loads, list) or not loads:
        raise CalcError("loads must be a non-empty list")
    h = _require_positive("standby_h", standby_h); m = _require_positive("alarm_min", alarm_min)
    af = _require_positive("aging_factor", aging_factor)
    rows = []; s_ma = 0.0; a_ma = 0.0
    for i, ld in enumerate(loads):
        if not isinstance(ld, dict):
            raise CalcError(f"load {i} must be an object")
        q = _require_non_negative("qty", ld.get("qty", 1))
        sm = _require_non_negative("standby_ma", ld.get("standby_ma", 0))
        am = _require_non_negative("alarm_ma", ld.get("alarm_ma", 0))
        s_ma += q * sm; a_ma += q * am
        rows.append(f"{ld.get('id', f'load{i+1}')}: {q:g} x {sm:g}/{am:g} mA -> {q*sm:g}/{q*am:g} mA")
    s_ah = s_ma / 1000.0 * h; a_ah = a_ma / 1000.0 * m / 60.0
    req = (s_ah + a_ah) * af
    out = {"formula": "AH = (I_stby*h + I_alarm*min/60) * aging", "rows": rows,
           "standby_ma_total": s_ma, "alarm_ma_total": a_ma, "standby_ah": s_ah, "alarm_ah": a_ah,
           "aging_factor": af, "ah_required": req,
           "basis": "NFPA 72-2025 s10.6.7.2.1/.2.2/.2.13/.2.14"}
    if vendor_derate is not None:
        d = _require_positive("vendor_derate", vendor_derate)
        if d > 1:
            raise CalcError("vendor_derate must be <= 1")
        out["ah_required_vendor_derated"] = req / d
    if battery_ah is not None:
        b = _require_positive("battery_ah", battery_ah)
        gov = out.get("ah_required_vendor_derated", req)
        out["battery_ah"] = b; out["battery_ok"] = b + 1e-9 >= gov; out["margin_ah"] = b - gov
    return out


def bor_demand_pressure(q_gpm: Number, p_bor_psi: Number, c: Number = 100.0, segments: Any = None,
                        dz_ft: Number = 0.0, friction_allow_psi: Number = 0.0, system: str = "dry",
                        suction_residual_psi: Number = 0.0, qr_gpm: Any = None,
                        churn_frac: Number = 1.0, p150_frac: Number = P150_FRAC) -> dict[str, Any]:
    """BOR -> pump discharge flange demand-pressure walk + rated-pressure floor screen.

    FIRST SLICE toward node-by-node BOR calc; single flow path, NOT a looped/network (EPANET) solver.
    q_gpm / p_bor_psi = demand at the base of riser (e.g. from cross_main_walk + hose as caller adds).
    segments (BOR -> pump discharge, all carrying q_gpm): {"d_in","length_ft","eq_ft"=0,"dz_ft"=0};
      pf = 4.52 Q^1.85/(C^1.85 d^4.87) * (L+eq)  (NFPA 13-2025 Ch.28 hydraulic calc, HW; fittings/valves
      as equivalent length per NFPA 13-2025 s28.2.3 / Table 28.2.3.1.1 with Table 28.2.3.2.1 C multiplier,
      caller-supplied; included per s28.2.4.8.1(1)). Segment dz_ft = rise in flow direction toward the BOR.
    dz_ft = extra elevation of BOR above pump discharge not carried in segments; +0.4333 psi/ft.
    friction_allow_psi = lump allowance (flagged; replace with segments for submittal).
    C lock (company): C=100 for wet, dry and DI; no nitrogen C-credit. Code enforces C=100 for dry / di;
    wet C is caller-supplied and must be passed as 100 under the lock.
    p_discharge_req = p_bor + sum(pf) + 0.4333*sum(dz) + allowance;
    p_net_req = p_discharge_req - suction_residual_psi (net pump pressure at q, NFPA 20-2025 s6.2.1/s6.2.2 sense).
    Rated-pressure floor (only if qr_gpm given), using the NFPA 20-2025 s6.2.1/s6.2.2 envelope of pump_net_at_q:
      q <= qr: pr >= p_net_req / (churn + (1-churn) q/qr)   [default churn 1.0 = flat, conservative]
      qr < q <= 1.5qr: pr >= p_net_req / (1 + (p150-1)(q-qr)/(0.5qr));  q > 1.5qr: no floor (flag).
    Churn/over-pressure must still be checked with electric_overpressure / relief_check.
    pump_envelope FM cap semantics untouched. SCREEN - verify with engineer of record; listed shop curve governs.
    """
    q = _require_positive("q_gpm", q_gpm); p0 = _require_positive("p_bor_psi", p_bor_psi)
    c = _require_positive("c", c)
    sysk = str(system).strip().lower().replace("-", "").replace(" ", "")
    sysk = {"doubleinterlock": "di", "preaction": "di", "dip": "di"}.get(sysk, sysk)
    if sysk not in ("wet", "dry", "di"):
        raise CalcError("system must be wet, dry or di (foam/clean locked out)")
    if sysk in ("dry", "di") and abs(c - 100.0) > 1e-9:
        raise CalcError("C=100 lock for dry/DI paths")
    segs = segments or []
    if not isinstance(segs, list):
        raise CalcError("segments must be a list")
    allow = _require_non_negative("friction_allow_psi", friction_allow_psi)
    dz0 = _as_float("dz_ft", dz_ft); ps = _as_float("suction_residual_psi", suction_residual_psi)
    p = p0; pf_tot = 0.0; dz_tot = dz0; rows = [f"BOR: Q={q:.2f} gpm P={p0:.3f} psi"]
    for i, s in enumerate(segs, 1):
        if not isinstance(s, dict):
            raise CalcError(f"segment {i} must be an object")
        d = _require_positive("d_in", s.get("d_in")); L = _require_positive("length_ft", s.get("length_ft"))
        eq = _require_non_negative("eq_ft", s.get("eq_ft", 0.0)); dz = _as_float("dz_ft", s.get("dz_ft", 0.0))
        pf = HW_COEFF * q ** HW_FLOW_EXP / (c ** HW_FLOW_EXP * d ** HW_DIAM_EXP) * (L + eq)
        pe = PSI_PER_FT_WATER * dz; pf_tot += pf; dz_tot += dz; p += pf + pe
        rows.append(f"s{i} {d:g}in x ({L:g}+{eq:g})ft dz={dz:g}: pf={pf:.4f} pe={pe:.4f} -> P={p:.3f}")
    pe0 = PSI_PER_FT_WATER * dz0; p += pe0 + allow
    rows.append(f"datum dz={dz0:g}ft pe={pe0:.4f}; allowance={allow:g} -> P_discharge_req={p:.3f}")
    p_net = p - ps
    out = {"formula": "P_dis = P_bor + sum HW pf + 0.4333*dz + allowance; P_net = P_dis - P_suction",
           "rows": rows, "system": sysk, "c": c, "friction_psi": pf_tot, "elevation_psi": PSI_PER_FT_WATER * dz_tot,
           "allowance_psi": allow, "p_discharge_required_psi": p, "p_net_required_psi": p_net,
           "lump_allowance_flag": allow > 0,
           "basis": "NFPA 13-2025 Ch.28 (s28.2.3, s28.2.4.8.1) HW walk; NFPA 20-2025 s6.2.1/s6.2.2 envelope floor; "
                    "single path, not network solver; verify with engineer of record"}
    if qr_gpm is not None:
        qr = _require_positive("qr_gpm", qr_gpm); ch = _require_positive("churn_frac", churn_frac)
        pfr = _require_positive("p150_frac", p150_frac)
        if ch > 1.40 + 1e-12:
            raise CalcError("churn_frac > 1.40 exceeds NFPA 20-2025 s6.2.2 shutoff limit")
        if q <= qr:
            fac = ch + (1 - ch) * q / qr; seg = "churn-rated"
        elif q <= 1.5 * qr + 1e-9:
            fac = 1 + (pfr - 1) * (q - qr) / (0.5 * qr); seg = "rated-150"
        else:
            fac = None; seg = "beyond-150 (NFPA 20-2025 s6.2.1)"
        out.update({"qr_gpm": qr, "pct_rated": 100 * q / qr, "envelope_segment": seg,
                    "envelope_factor": fac,
                    "rated_pressure_floor_psi": (p_net / fac) if fac else None})
    return out


def rated_pressure_select(q_demand_gpm: Number, p_net_demand_psi: Number, qr_gpm: Any,
                          churn_frac: Number = 1.0, p150_frac: Number = P150_FRAC,
                          pr_candidates_psi: Any = None) -> dict[str, Any]:
    """Fire-pump rated-pressure SELECTION from a net demand point. SCREEN - verify with engineer of record.

    Consumes bor_demand_pressure["p_net_required_psi"] (net pump pressure needed at q_demand_gpm).
    Basis (held NFPA 20 text only, paraphrased): NFPA 20-2025 s6.2.1 (not less than 150% of rated capacity at
    not less than 65% of total rated head); NFPA 20-2025 s6.2.2 (shutoff head not to exceed 140%
    of rated head). Envelope = pump_net_at_q (0,churn*pr)-(qr,pr)-(1.5qr,p150*pr); Fig A.6.2 is a
    RENDER GAP - no Fig A.6.2 values used.
    Per qr candidate: factor f(q) = envelope p/pr at q (churn 1.0 default = flat, conservative);
      floor pr_min = p_net_demand / f;  q > 1.5qr -> infeasible (beyond s6.2.1 150% point).
    Optional pr_candidates_psi (caller's listed ratings): pick smallest >= floor. Checks: roundtrip via
    pump_net_at_q at the selected pr; churn_frac <= 1.40 (s6.2.2); p150_frac >= 0.65 (s6.2.1).
    Over-pressure (s4.7.7.1) still via electric_overpressure / relief_check. FM qd_le_fm_cap untouched.
    """
    q = _require_positive("q_demand_gpm", q_demand_gpm); pn = _require_positive("p_net_demand_psi", p_net_demand_psi)
    ch = _require_positive("churn_frac", churn_frac); pf = _require_positive("p150_frac", p150_frac)
    if ch > 1.40 + 1e-12:
        raise CalcError("churn_frac > 1.40 exceeds NFPA 20-2025 s6.2.2 shutoff limit")
    if ch < 1.0 - 1e-12:
        raise CalcError("churn_frac < 1.0 not a rising-to-shutoff centrifugal envelope")
    if pf < 0.65 - 1e-12 or pf > 1.0 + 1e-12:
        raise CalcError("p150_frac must be within 0.65..1.0 (NFPA 20-2025 s6.2.1)")
    qrs = qr_gpm if isinstance(qr_gpm, list) else [qr_gpm]
    if not qrs:
        raise CalcError("qr_gpm must be a number or non-empty list")
    cands = None
    if pr_candidates_psi is not None:
        cl = pr_candidates_psi if isinstance(pr_candidates_psi, list) else [pr_candidates_psi]
        if not cl:
            raise CalcError("pr_candidates_psi must be non-empty")
        cands = sorted(_require_positive("pr_candidates_psi", v) for v in cl)
    rows = []; table = []
    for qv in qrs:
        qr = _require_positive("qr_gpm", qv)
        if q <= qr:
            f = ch + (1.0 - ch) * q / qr; seg = "churn-rated"
        elif q <= 1.5 * qr + 1e-9:
            f = 1.0 + (pf - 1.0) * (q - qr) / (0.5 * qr); seg = "rated-150"
        else:
            f = None; seg = "beyond-150 (NFPA 20-2025 s6.2.1)"
        floor = pn / f if f else None
        sel = None
        if floor is not None and cands is not None:
            sel = next((c for c in cands if c >= floor - 1e-9), None)
        pr_use = sel if sel is not None else floor
        back = pump_net_at_q(qr, pr_use, q, ch, pf)["p_net_psi"] if pr_use is not None else None
        row = {"qr_gpm": qr, "pct_rated": 100.0 * q / qr, "segment": seg, "envelope_factor": f,
               "rated_pressure_floor_psi": floor, "selected_pr_psi": sel,
               "feasible": floor is not None and (cands is None or sel is not None),
               "p_net_at_q_check_psi": back,
               "meets_demand": back is not None and back >= pn - 1e-9,
               "churn_psi": ch * pr_use if pr_use else None, "churn_le_140_ok_622": ch <= 1.40 + 1e-12,
               "p150_psi": pf * pr_use if pr_use else None}
        rows.append(row)
        table.append(f"qr={qr:.1f} ({row['pct_rated']:.1f}%) f={'n/a' if f is None else f'{f:.4f}'} "
                     f"floor={'n/a' if floor is None else f'{floor:.3f}'} sel={sel} [{seg}]")
    feas = [r for r in rows if r["feasible"]]
    best = min(feas, key=lambda r: (r["selected_pr_psi"] or r["rated_pressure_floor_psi"])) if feas else None
    out = {"formula": "pr_min = p_net_demand / f(q/qr); f from pump_net_at_q envelope (NFPA 20-2025 s6.2.1/s6.2.2)",
           "q_demand_gpm": q, "p_net_demand_psi": pn, "churn_frac": ch, "p150_frac": pf,
           "candidates": rows, "rows": table, "any_feasible": bool(feas), "best": best,
           "basis": "NFPA 20-2025 s6.2.1 (150% cap @ >=65% head), s6.2.2 (shutoff <=140%) per the held NFPA 20 text; "
                    "Fig A.6.2 RENDER GAP not used; s4.7.7.1 over-pressure separate; SCREEN - verify with engineer of record, listed shop curve governs"}
    if len(rows) == 1:
        out.update({k: rows[0][k] for k in ("rated_pressure_floor_psi", "selected_pr_psi", "envelope_factor", "feasible", "meets_demand")})
    return out


def air_setpoint_stack(system_air_psig: Number, trip_psig: Number, low_air_switch_psig: Number,
                       high_air_switch_psig: Any = None, release_psig: Any = None, trip_tol_psi: Number = 0.0,
                       margin_low_psi: Number = 5.0, margin_high_psi: Number = 5.0,
                       table_a_min_psig: Any = None, max_pneumatic_psig: Any = None,
                       pmd_cut_in_psig: Any = None, pmd_cut_out_psig: Any = None,
                       held: Any = None) -> dict[str, Any]:
    """Dry / DI supervisory air setpoint stack + compressor/PMD margin screen.
    SCREEN ONLY - verify with engineer of record wherever a code band fails.

    Bands (worked package):
      T_worst = max(trip + trip_tol, release)                          [maker Tbl B, e.g. Reliable 505, +/-2]
      L - T_worst >= margin_low (default 5)  NFPA 13-2025 s8.2.6.4 (owner dial; T_worst+5 reading)
      P > L ; P >= Table A min (maker, e.g. Reliable 505/747)          [maker]
      H - P >= margin_high (default 5)       NFPA 13-2025 s8.2.6.5
      H, P <= max_pneumatic (Reliable 505 caution caps / note 6 30 psi abs) [maker]
      compressor cut-in (upstream of PMD) > P ; cut-in >= Table A min (505 n.4 / 747 n.3); cut-out > cut-in
    AMD/PMD requirement itself: NFPA 13-2025 s8.2.8.1/.2. No maker setpoint is defaulted here: every
    pressure is caller-supplied; `held` = names of inputs the caller asserts are HELD maker/code values,
    all others are tagged ASSUMED in the output.
    """
    def num(name, v, req=True):
        if v is None:
            if req:
                raise CalcError(f"{name} required")
            return None
        try:
            x = float(v)
        except (TypeError, ValueError):
            raise CalcError(f"{name} must be a number, got {v!r}")
        if x != x or x < 0 or x > 300:
            raise CalcError(f"{name} out of range 0-300 psig: {v!r}")
        return x
    P = num("system_air_psig", system_air_psig); T = num("trip_psig", trip_psig)
    L = num("low_air_switch_psig", low_air_switch_psig)
    H = num("high_air_switch_psig", high_air_switch_psig, False); R = num("release_psig", release_psig, False)
    tol = num("trip_tol_psi", trip_tol_psi); ml = num("margin_low_psi", margin_low_psi)
    mh = num("margin_high_psi", margin_high_psi); M = num("table_a_min_psig", table_a_min_psig, False)
    cap = num("max_pneumatic_psig", max_pneumatic_psig, False)
    ci = num("pmd_cut_in_psig", pmd_cut_in_psig, False); co = num("pmd_cut_out_psig", pmd_cut_out_psig, False)
    if P <= 0 or T <= 0 or L <= 0:
        raise CalcError("system_air, trip and low_air must be > 0 psig")
    if T >= P:
        raise CalcError(f"trip {T} >= system air {P}: valve would be tripped at maintain pressure")
    if (ci is None) != (co is None):
        raise CalcError("give both pmd_cut_in_psig and pmd_cut_out_psig, or neither")
    if ci is not None and co <= ci:
        raise CalcError(f"cut-out {co} must exceed cut-in {ci}")
    if cap is not None and M is not None and M > cap:
        raise CalcError(f"Table A min {M} > max pneumatic cap {cap}: check row")
    held_set = set(held or [])
    t_worst = max(T + tol, R if R is not None else 0.0)
    bands, code_fail, maker_fail = [], False, False
    def band(name, value, floor, basis, kind, ok=None):
        nonlocal code_fail, maker_fail
        passed = (value >= floor) if ok is None else ok
        if not passed:
            if kind == "code": code_fail = True
            else: maker_fail = True
        bands.append({"band": name, "value_psi": round(value, 3), "floor_psi": floor, "pass": passed,
                      "kind": kind, "basis": basis})
    band("low_air - T_worst", L - t_worst, ml, "NFPA 13-2025 s8.2.6.4", "code")
    band("system - low_air", P - L, 0.0, "P > L (no alarm at maintain)", "physics", ok=P - L > 0)
    if H is not None:
        band("high_air - system", H - P, mh, "NFPA 13-2025 s8.2.6.5", "code")
    if M is not None:
        band("system - Table A min", P - M, 0.0, "maker Table A min supervisory", "maker")
    if cap is not None:
        band("cap - system", cap - P, 0.0, "maker max pneumatic cap", "maker")
        if H is not None:
            band("cap - high_air", cap - H, 0.0, "maker max pneumatic cap", "maker")
    if ci is not None:
        band("cut_in - system", ci - P, 0.0, "compressor cut-in > PMD set (no starve)", "physics", ok=ci - P > 0)
        if M is not None:
            band("cut_in - Table A min", ci - M, 0.0, "Reliable 505 n.4 / 747 n.3 compressor-on >= Table A min", "maker")
    inputs = {"system_air_psig": P, "trip_psig": T, "low_air_switch_psig": L, "high_air_switch_psig": H,
              "release_psig": R, "trip_tol_psi": tol, "table_a_min_psig": M, "max_pneumatic_psig": cap,
              "pmd_cut_in_psig": ci, "pmd_cut_out_psig": co}
    tags = {k: ("HELD" if k in held_set else "ASSUMED") for k, v in inputs.items() if v is not None}
    notes = []
    if code_fail and not maker_fail:
        notes.append("NFPA 13-2025 s8.2.6.4/.5 5 psi margin not met inside maker band -> NEEDS PE / maker confirmation (do not settle here)")
    if ci is not None and cap is not None and co > cap:
        notes.append(f"upstream cut-out {co} > cap {cap}: OK only if PMD downstream holds P; verify PMD inlet rating (PE/maker)")
    if any(v == "ASSUMED" for v in tags.values()):
        notes.append("ASSUMED inputs present; result is teaching/screen only")
    return {"t_worst_psi": round(t_worst, 3), "bands": bands, "code_pass": not code_fail,
            "maker_pass": not maker_fail, "all_pass": all(b["pass"] for b in bands),
            "needs_pe": code_fail or any(v == "ASSUMED" for v in tags.values()),
            "tags": tags, "notes": notes,
            "basis": "NFPA 13-2025 s8.2.6.4/.5 (5 psi defaults), s8.2.8.1/.2; maker bands caller-supplied (Reliable 505/747 Tbl A/B, Bulletin 251 PMD). SCREEN - verify with engineer of record"}


def loop_two_path(q_total_gpm: Number, d1_in: Number, l1_ft: Number, d2_in: Number = None,
                  l2_ft: Number = None, c: Number = 100, c2: Number = None,
                  split_frac: Number = None) -> dict[str, Any]:
    """Looped private main, two parallel legs source->demand node.

    Rationale: NFPA 13-2025 Ch.28 (hydraulic calcs; loops/grids balanced so pressure loss
    is equal along every path to a common node, HW per s28.2.2.1) and NFPA 24-2025 private
    fire service mains (looped supply). DSSP looped private main use-case.
    Balanced split (default): hf1 = hf2, Q1+Q2 = Q, HW exponent 1.85 ->
        Q_i  proportional to  C_i * (d_i**4.87 / L_i)**(1/1.85)
    If split_frac given, Q1 = split_frac*Q (forced split, governing = higher leg loss).
    Equal-split shortcut (Q/2 each leg) also reported (governing = higher leg loss).
    C=100 company lock default. Not an EPANET solver; single loop, two legs, no elevation.
    SCREEN - verify with engineer of record.
    """
    q = _require_non_negative("q_total_gpm", q_total_gpm)
    d1 = _require_positive("d1_in", d1_in); L1 = _require_positive("l1_ft", l1_ft)
    d2 = d1 if d2_in is None else _require_positive("d2_in", d2_in)
    L2 = L1 if l2_ft is None else _require_positive("l2_ft", l2_ft)
    c1 = _require_positive("c", c); cc2 = c1 if c2 is None else _require_positive("c2", c2)
    w1 = c1 * (d1 ** HW_DIAM_EXP / L1) ** (1 / HW_FLOW_EXP)
    w2 = cc2 * (d2 ** HW_DIAM_EXP / L2) ** (1 / HW_FLOW_EXP)
    if split_frac is None:
        f1 = w1 / (w1 + w2); mode = "balanced (hf1=hf2)"
    else:
        f1 = float(split_frac)
        if not 0 <= f1 <= 1:
            raise CalcError("split_frac must be 0..1")
        mode = "forced split_frac"
    q1, q2 = q * f1, q * (1 - f1)
    p1 = hazen_williams(q1, c1, d1, L1)["p_psi"]; p2 = hazen_williams(q2, cc2, d2, L2)["p_psi"]
    e1 = hazen_williams(q / 2, c1, d1, L1)["p_psi"]; e2 = hazen_williams(q / 2, cc2, d2, L2)["p_psi"]
    return {"formula": "two-path loop HW split", "mode": mode, "q1_gpm": q1, "q2_gpm": q2,
            "p1_psi": p1, "p2_psi": p2, "p_governing_psi": max(p1, p2),
            "equal_split_p1_psi": e1, "equal_split_p2_psi": e2,
            "equal_split_governing_psi": max(e1, e2),
            "basis": "NFPA 13-2025 Ch.28 HW (s28.2.2.1) loop balance; NFPA 24-2025 looped private main; C=100 lock. SCREEN - verify with engineer of record"}



# FUS 1999 Required Duration of Fire Flow (p.16; 3,000→1.25 h IMAGE-VERIFIED).
# Keys are tabulated fire-flow L/min. Gaps (e.g. 7k/9k/11k) use next-higher key.
_FUS1999_DURATION_H = {
    2000: 1.0,
    3000: 1.25,
    4000: 1.50,
    5000: 1.75,
    6000: 2.0,
    8000: 2.0,
    10000: 2.0,
    12000: 2.5,
    14000: 3.0,
    16000: 3.5,
    18000: 4.0,
    20000: 4.5,
    22000: 5.0,
    24000: 5.5,
    26000: 6.0,
    28000: 6.5,
    30000: 7.0,
    32000: 7.5,
    34000: 8.0,
    36000: 8.5,
    38000: 9.0,
    40000: 9.5,
}


def _round_nearest_1000_lpm(x: float) -> int:
    """Nearest 1,000 L/min; half-up for positive values (FUS customary)."""
    if x < 0:
        raise CalcError("cannot round negative fire flow")
    return int(x / 1000.0 + 0.5) * 1000


def _fus1999_duration_h(rff_lpm: int) -> tuple[float, str]:
    """Lookup Required Duration (h) from FUS 1999 p.16 table.

    Exact tabulated keys used as held. Values below 2,000 → 1.0 h ('2,000 or less').
    Values ≥40,000 → 9.5 h. Non-tabulated intermediate rounded RFF (7k/9k/11k, …)
    use the next-higher tabulated key (conservative for storage volume).
    THIS IS A SCREEN ENGINEERING ASSUMPTION — not a FUS code/clause; source does
    not state an interpolation rule for gaps. Do not upgrade to a code claim.
    """
    if rff_lpm <= 2000:
        return 1.0, "FUS 1999 p.16: 2,000 or less → 1.0 h"
    if rff_lpm >= 40000:
        return 9.5, "FUS 1999 p.16: 40,000 and over → 9.5 h"
    keys = sorted(_FUS1999_DURATION_H.keys())
    if rff_lpm in _FUS1999_DURATION_H:
        return _FUS1999_DURATION_H[rff_lpm], f"FUS 1999 p.16 exact key {rff_lpm}"
    for k in keys:
        if k > rff_lpm:
            return _FUS1999_DURATION_H[k], (
                f"SCREEN engineering assumption (not a FUS code/clause): "
                f"RFF {rff_lpm} not tabulated on FUS 1999 p.16; "
                f"next-higher key {k} (conservative; no held interpolation rule)"
            )
    return 9.5, "FUS 1999 p.16 fallback ≥40,000 → 9.5 h"


# --- FUS 2020 - ONLY cells held in the knowledge base ---
#   L32 Table 1 duration + "interpolate intermediates"; L55–56 formula/rounding;
#   L58–71 construction C table (NBC types); L79 occupancy −25…+25 %; L83–88
#   sprinkler ≤50 % core (+25 % community ITM NOT auto-applied); L91 exposure ≤75 %;
#   L99–101 clamp: 2020 universal 2,000/45,000 clamp NOT established (PE-VERIFY).
_FUS2020_C_BY_TYPE = {
    "V": 1.5,      # Type V Wood Frame
    "IV-D": 1.5,   # Un-Rated Mass Timber
    "IV-C": 1.0,   # Ordinary / Partially Rated Mass Timber
    "IV-B": 0.9,   # Rated Mass Timber
    "IV-A": 0.8,   # Encapsulated Mass Timber
    "III": 1.0,    # Ordinary (joisted masonry)
    "II": 0.8,     # Noncombustible
    "I": 0.6,      # Fire Resistive
}
_FUS2020_DURATION_H = dict(_FUS1999_DURATION_H)  # FUS 2020 Table 1 printed p.5: identical ladder (source note L32)


def _fus2020_construction(c_construction: Any) -> tuple[float, list[str]]:
    """Map an FUS 2020 NBC type label or held numeric C. No interpolation (not held for 2020)."""
    if isinstance(c_construction, str):
        lab = c_construction.strip().upper().replace("TYPE", "").strip().replace(" ", "")
        if lab in _FUS2020_C_BY_TYPE:
            return _FUS2020_C_BY_TYPE[lab], [lab]
        try:
            c_construction = float(lab)
        except ValueError:
            raise CalcError(
                f"FUS 2020 construction type {c_construction!r} not held; "
                f"use one of {sorted(_FUS2020_C_BY_TYPE)} (FUS 2020 printed pp.20–21)"
            ) from None
    c = _as_float("c_construction", c_construction)
    types = [t for t, v in _FUS2020_C_BY_TYPE.items() if abs(v - c) < 1e-9]
    if not types:
        raise CalcError(
            f"c_construction={c} is not a held FUS 2020 coefficient "
            "(held: 0.6, 0.8, 0.9, 1.0, 1.5; FUS 2020 printed pp.20–21). "
            "No 2020 interpolation rule held — not defaulted"
        )
    return c, types


def _fus2020_duration_h(rff_lpm: int) -> tuple[float, str]:
    """FUS 2020 Table 1 (printed p.5): exact keys; intermediates linearly interpolated
    per the table footnote '* Interpolate for intermediate figures' (held, source note L32)."""
    if rff_lpm <= 2000:
        return 1.0, "FUS 2020 Table 1 p.5: 2,000 or less → 1.0 h"
    if rff_lpm >= 40000:
        return 9.5, "FUS 2020 Table 1 p.5: 40,000 and over → 9.5 h"
    if rff_lpm in _FUS2020_DURATION_H:
        return _FUS2020_DURATION_H[rff_lpm], f"FUS 2020 Table 1 p.5 exact key {rff_lpm}"
    keys = sorted(_FUS2020_DURATION_H)
    for lo, hi in zip(keys, keys[1:]):
        if lo < rff_lpm < hi:
            d_lo, d_hi = _FUS2020_DURATION_H[lo], _FUS2020_DURATION_H[hi]
            d = d_lo + (d_hi - d_lo) * (rff_lpm - lo) / (hi - lo)
            return d, (
                f"FUS 2020 Table 1 p.5 linear interpolation {lo}→{hi} "
                "(footnote: 'Interpolate for intermediate figures')"
            )
    raise CalcError(f"FUS 2020 duration lookup failed for {rff_lpm}")


def _fus_rff_2020(a_m2: Any, c_construction: Any, occupancy_factor: Any,
                  sprinkler_credit: Any, exposure_factor: Any) -> dict[str, Any]:
    """FUS 2020 RFF, Part 2 steps A–G — held cells only; unheld cells raise CalcError."""
    import math

    a = _require_positive("a_m2", a_m2)
    c, types = _fus2020_construction(c_construction)
    occ = _as_float("occupancy_factor", occupancy_factor)
    if occ < -0.25 or occ > 0.25:
        raise CalcError("occupancy_factor must be in [-0.25, +0.25] (FUS 2020 printed p.24)")
    spr = _as_float("sprinkler_credit", sprinkler_credit)
    if spr < 0:
        raise CalcError("sprinkler_credit must be ≥ 0")
    if spr > 0.50:
        raise CalcError(
            "sprinkler_credit > 0.50 not supported: FUS 2020 community-ITM-oversight "
            "additional ≤25% (printed pp.27–29) is underwriter judgment — NOT auto-applied; "
            "foam/clean LOCKED"
        )
    exp = _as_float("exposure_factor", exposure_factor)
    if exp < 0 or exp > 0.75:
        raise CalcError("exposure_factor must be in [0, 0.75] (FUS 2020 printed p.30)")

    f0_raw = 220.0 * c * math.sqrt(a)
    f0_rounded = _round_nearest_1000_lpm(f0_raw)
    e_occ = f0_rounded * (1.0 + occ)
    if e_occ < 2000.0:
        raise CalcError(
            f"FUS 2020: post-occupancy flow {e_occ:.1f} L/min < 2,000 — the 1999 2,000 floor is "
            "NOT established as a universal FUS 2020 Part 2 rule (source note L99–101; PE-VERIFY). "
            "Not defaulted"
        )
    spr_reduction = e_occ * spr
    exp_addition = e_occ * exp
    h_raw = e_occ - spr_reduction + exp_addition
    if h_raw < 2000.0 or h_raw > 45000.0:
        raise CalcError(
            f"FUS 2020: H={h_raw:.1f} L/min outside [2,000, 45,000] — FUS 2020 universal "
            "clamp NOT established (45,000 ceiling sentence absent; source note L99–101; "
            "PE-VERIFY). Not defaulted to 1999 clamp"
        )
    rff = _round_nearest_1000_lpm(h_raw)
    dur_h, dur_note = _fus2020_duration_h(rff)
    volume_m3 = rff * dur_h * 60.0 / 1000.0
    rff_gpm = rff / 3.785411784
    return {
        "edition": 2020,
        "a_m2": a,
        "c_construction": c,
        "construction_type_2020": "/".join(types),
        "occupancy_factor": occ,
        "sprinkler_credit": spr,
        "exposure_factor": exp,
        "f0_raw_lpm": f0_raw,
        "f0_rounded_lpm": f0_rounded,
        "e_occupancy_lpm": e_occ,
        "e_floor_applied": False,
        "sprinkler_reduction_lpm": spr_reduction,
        "exposure_addition_lpm": exp_addition,
        "h_raw_lpm": h_raw,
        "h_clamped_lpm": h_raw,
        "rff_lpm": rff,
        "rff_gpm_us": rff_gpm,
        "duration_h": dur_h,
        "duration_note": dur_note,
        "volume_m3": volume_m3,
        "clamp_min_lpm": None,
        "clamp_max_lpm": None,
        "clamp_status": "NOT ESTABLISHED in FUS 2020 — H outside [2,000, 45,000] raises (PE-VERIFY)",
        "basis": (
            "FUS 2020 (Water Supply for Public Fire Protection in Canada) Part 2 steps A–G: "
            "RFF=220·C·√A (L/min, m²; IMAGE-VERIFIED p.19); round step C and G to 1,000 only; "
            "C from NBC-type table pp.20–21 (held values only, no interpolation); "
            "occupancy ±25% p.24; sprinkler ≤50% core Table 4 (community-ITM +25% NOT applied); "
            "exposure ≤75% p.30; duration Table 1 p.5 (interpolate intermediates). "
            "No 2020 clamp/floor established — out-of-band raises. "
            "COMPARISON/edition-delta only where AHJ cites 1999 (municipal water regulation 2018). "
            "FUS C ≠ Hazen–Williams C (company HW C=100). Not Ps/Ph/Qf; GAP-B35R8-1 untouched. "
            "SCREEN — verify with engineer of record"
        ),
    }


def fus_rff(
    a_m2: Number,
    c_construction: Number,
    occupancy_factor: Number = 0.0,
    sprinkler_credit: Number = 0.0,
    exposure_factor: Number = 0.0,
    edition: Any = 1999,
) -> dict[str, Any]:
    """FUS 1999 Required Fire Flow (RFF) — Part II (pp.17–20).

    Formula (IMAGE-VERIFIED): F0 = 220 · C · √A   with F in L/min, A in m².
    C = construction coefficient (wood 1.5 / ordinary 1.0 / non-combustible 0.8 /
    fire-resistive 0.6); interpolation allowed; not outside [0.6, 1.5].
    Outline A→H (p.20): round formula to nearest 1,000; apply occupancy ± without
    intermediate rounding (floor 2,000 after occupancy); sprinkler decrease and
    exposure increase both applied to post-occupancy value; H = E − F + G; clamp
    [2,000, 45,000]; round final to nearest 1,000; look up duration (p.16).

    Sprinkler credit path (p.18): ≤30% NFPA 13 + ≤10% supply + ≤10% supervision
    → theoretical max 50%. Caller supplies the elected total fraction (0..0.50);
    do not invent other suppression-agent credits (LOCKED). Exposure total ≤75% (p.18–19).

    FUS C is NOT Hazen–Williams C (company HW C=100 still governs sprinkler calcs).
    Not a hydrant curve / Ps/Ph/Qf; does not close GAP-B35R8-1. Edition locked to
    1999 by default — no silent 2020 substitution. edition=2020 routes
    to _fus_rff_2020 (held cells only; unheld cells raise).
    SCREEN — verify with engineer of record. Not full-network / design certification.
    """
    import math

    ed_raw = edition
    try:
        ed = int(str(ed_raw).strip())
    except (TypeError, ValueError) as exc:
        raise CalcError("edition must be 1999 or 2020 (FUS)") from exc
    if ed == 2020:
        # separate held-cells-only path; 1999 path below unchanged.
        return _fus_rff_2020(a_m2, c_construction, occupancy_factor,
                             sprinkler_credit, exposure_factor)
    if ed != 1999:
        raise CalcError(
            "fus_rff supports FUS 1999 | 2020 only "
            f"(got edition={ed_raw!r})"
        )

    a = _require_positive("a_m2", a_m2)
    c = _as_float("c_construction", c_construction)
    if c < 0.6 or c > 1.5:
        raise CalcError("c_construction must be in [0.6, 1.5] (FUS 1999 p.17)")
    occ = _as_float("occupancy_factor", occupancy_factor)
    if occ < -0.25 or occ > 0.25:
        raise CalcError("occupancy_factor must be in [-0.25, +0.25] (FUS 1999 p.18)")
    spr = _as_float("sprinkler_credit", sprinkler_credit)
    if spr < 0 or spr > 0.50:
        raise CalcError("sprinkler_credit must be in [0, 0.50] (FUS 1999 p.18; foam/clean LOCKED)")
    exp = _as_float("exposure_factor", exposure_factor)
    if exp < 0 or exp > 0.75:
        raise CalcError("exposure_factor must be in [0, 0.75] (FUS 1999 pp.18–19)")

    f0_raw = 220.0 * c * math.sqrt(a)
    f0_rounded = _round_nearest_1000_lpm(f0_raw)
    e_occ = f0_rounded * (1.0 + occ)
    if e_occ < 2000.0:
        e_occ = 2000.0
        e_floor_applied = True
    else:
        e_floor_applied = False
    spr_reduction = e_occ * spr
    exp_addition = e_occ * exp
    h_raw = e_occ - spr_reduction + exp_addition
    h_clamped = min(45000.0, max(2000.0, h_raw))
    rff = _round_nearest_1000_lpm(h_clamped)
    # Re-clamp after rounding (e.g. theoretical edge)
    if rff < 2000:
        rff = 2000
    if rff > 45000:
        rff = 45000
    dur_h, dur_note = _fus1999_duration_h(rff)
    volume_m3 = rff * dur_h * 60.0 / 1000.0  # L/min × h × 60 → L; /1000 → m³
    # US gpm convenience only (not FUS primary unit); 1 US gal = 3.785411784 L
    rff_gpm = rff / 3.785411784

    return {
        "edition": 1999,
        "a_m2": a,
        "c_construction": c,
        "occupancy_factor": occ,
        "sprinkler_credit": spr,
        "exposure_factor": exp,
        "f0_raw_lpm": f0_raw,
        "f0_rounded_lpm": f0_rounded,
        "e_occupancy_lpm": e_occ,
        "e_floor_applied": e_floor_applied,
        "sprinkler_reduction_lpm": spr_reduction,
        "exposure_addition_lpm": exp_addition,
        "h_raw_lpm": h_raw,
        "h_clamped_lpm": h_clamped,
        "rff_lpm": rff,
        "rff_gpm_us": rff_gpm,
        "duration_h": dur_h,
        "duration_note": dur_note,
        "volume_m3": volume_m3,
        "clamp_min_lpm": 2000,
        "clamp_max_lpm": 45000,
        "basis": (
            "FUS 1999 Part II pp.17–20: F=220·C·√A (L/min, m²); "
            "round formula ±1,000; occupancy ± no mid-round (floor 2,000); "
            "sprinkler ≤50% + exposure ≤75% on post-occupancy; H=E−F+G; "
            "clamp [2,000,45,000]; final ±1,000; duration p.16. "
            "FUS C ≠ Hazen–Williams C (company HW C=100). "
            "Not Ps/Ph/Qf; GAP-B35R8-1 untouched. "
            "1999 only — no FUS 2020 claim. SCREEN — verify with engineer of record"
        ),
    }



def _decimal_floor_quotient(numer: Number, denom: Number) -> int:
    """Floor of numer/denom using the shortest-round-trip decimal of each float
    (documents the typed-input vs computed-residue edge).

    Each side is Decimal(str(float(x))), then ROUND_FLOOR. Typed decimal inputs
    that survive str(float(...)) as their exact short decimal (0.3/0.01 → 30,
    0.7/0.1 → 7, 0.3/0.1 → 3, 0.6/0.2 → 3, 1.0/0.05 → 20, and the 0.2/0.009
    leftover → 22) are exact.

    Computed residue is different. A binary intermediate such as 0.7 - 0.4
    equals 0.29999999999999993, not 0.3; str(float(0.7-0.4)) is
    '0.29999999999999993', so (0.7-0.4)/0.1 floors to 2. The retired
    float-eps residual would have returned 3. This helper does not add
    a tolerance to restore that promotion. Callers that need an exact decimal
    should pass a typed decimal (or a value that round-trips through str(float)),
    not a binary difference. obscuration_sc corpus inputs are typed, so this
    edge does not change stored jobs.
    """
    q = Decimal(str(float(numer))) / Decimal(str(float(denom)))
    return int(q.to_integral_value(rounding=ROUND_FLOOR))


def obscuration_sc(
    sh: Number,
    n_ports: Number,
    unit: str,
    sc: Any = None,
    sc_min: Any = None,
) -> dict[str, Any]:
    """ASD chamber sensitivity from per-port target — Sc ≤ Sh/N.

    Balanced airflow-fraction form (ri ≈ 1/N): Sc,req ≤ Sh,target / N; also Sh,eff ≈ Sc·N and
    listing-floor N_max = ⌊Sh / Sc,min⌋. Held: FM DS 5-32 Jan-2026 §3.3.2 chamber-vs-port
    dilution examples + KB asd-return-sampling-sizing-for-fan-wall-halls (pp.4–6 / TL;DR).
    Layer label: insurer/engineering method (FM body §3.3.2 rationale tables + airflow-fraction
    derivation) — NOT an NFPA 13/72 code-prescribed trip setpoint (those standards set none).

    unit is REQUIRED for clarity: "pct_obs_per_ft" (% obs/ft) or "pct_obs_per_m" (% obs/m).
    Caller supplies Sh (and optional Sc / Sc,min) already in that unit — no silent unit conversion
    and no default 0.2/1.0 thresholds invented here.
    n_ports must be a positive integer. Does NOT elect port layout (FA owns sampling layout) and
    does NOT elect trip tier — GAP-B33R8-1 remains HOLD / untouched.
    SCREEN — verify with engineer of record.
    """
    u_raw = str(unit).strip().lower().replace(" ", "_").replace("-", "_").replace("%", "pct")
    u_map = {
        "pct_obs_per_ft": "pct_obs_per_ft",
        "pct_obs_ft": "pct_obs_per_ft",
        "pct_per_ft": "pct_obs_per_ft",
        "pct_ft": "pct_obs_per_ft",
        "obs_per_ft": "pct_obs_per_ft",
        "per_ft": "pct_obs_per_ft",
        "ft": "pct_obs_per_ft",
        "pct_obs_per_m": "pct_obs_per_m",
        "pct_obs_m": "pct_obs_per_m",
        "pct_per_m": "pct_obs_per_m",
        "pct_m": "pct_obs_per_m",
        "obs_per_m": "pct_obs_per_m",
        "per_m": "pct_obs_per_m",
        "m": "pct_obs_per_m",
    }
    if u_raw not in u_map:
        raise CalcError(
            'unit required: "pct_obs_per_ft" (% obs/ft) or "pct_obs_per_m" (% obs/m); '
            "no silent conversion between ft and m"
        )
    u = u_map[u_raw]
    sh_v = _require_positive("sh", sh)
    # n_ports: positive integer only (no fractional ports)
    n_f = _as_float("n_ports", n_ports)
    if n_f != int(n_f) or int(n_f) < 1:
        raise CalcError("n_ports must be a positive integer (>= 1)")
    n = int(n_f)
    sc_max = sh_v / n
    out: dict[str, Any] = {
        "formula": "Sc_req <= Sh_target / N (balanced ri=1/N); Sh_eff ~= Sc * N",
        "sh": sh_v,
        "n_ports": n,
        "unit": u,
        "sc_max": sc_max,
        "sc_req_max": sc_max,  # alias
        "gap_b33r8_1": "GAP-B33R8-1 HOLD untouched — op does not elect trip tier / Sh setpoint",
        "port_layout": "FA owns sampling layout — op does not elect ports",
        "basis": (
            "FM DS 5-32 Jan-2026 s3.3.2 chamber-vs-port dilution (balanced) + "
            "KB asd-return-sampling-sizing-for-fan-wall-halls (Sc<=Sh/N). "
            "Insurer/engineering method — not NFPA 13/72 code trip setpoint. "
            "GAP-B33R8-1 HOLD untouched. SCREEN — verify with engineer of record"
        ),
    }
    if sc is not None:
        sc_v = _require_positive("sc", sc)
        sh_eff = sc_v * n
        passes = sc_v <= sc_max + 1e-15
        out.update({"sc": sc_v, "sh_eff": sh_eff, "passes_sc": passes})
    if sc_min is not None:
        scmin = _require_positive("sc_min", sc_min)
        # float `sh_v // scmin` is NOT the exact floor at decimal multiples
        # (0.3 // 0.01 == 29.0 though 0.3/0.01 is 30 to ~1e-15; 0.3/0.1 -> 2.9999999999999996).
        # Replace the floor(Sh/Sc_min + 1e-9) residual with an exact Decimal
        # quotient (shortest-round-trip decimal of each float, then floor). Exact decimal
        # multiples (0.3/0.01, 0.3/0.1, 0.7/0.1, 0.6/0.2, 1.0/0.05, earlier cases) are exact;
        # non-boundary values unchanged. GAP-B33R8-1 HOLD untouched. passes_n stays consistent
        # with passes_sc at the Sc == Sc_min exact-decimal boundary.
        n_max = _decimal_floor_quotient(sh_v, scmin)
        out.update({
            "sc_min": scmin,
            "n_max_at_sc_min": n_max,
            "passes_n": n <= n_max,
        })
    return out


def sprinkler_grid_coverage(
    room_length_ft: Number,
    room_width_ft: Number,
    branch_spacing_ft: Number,
    head_spacing_ft: Number,
    n_branches: Number,
    heads_per_branch: Number,
    branch_offset_ft: Number,
    head_offset_ft: Number,
    max_spacing_ft: Number,
    max_area_ft2: Number,
    max_wall_distance_ft: Any = None,
    min_spacing_ft: Any = None,
    edge_area_rule: str = "include",
    wall_compare: str = "le",
) -> dict[str, Any]:
    """Rectangular sprinkler grid spacing / area / wall-distance / coverage check (edge-head area in PASS + selectable wall comparison).

    Geometry (caller states the layout; the op does NOT elect a grid):
      x axis = room_length (cross-main axis): branches at x_i = branch_offset + i*branch_spacing
      y axis = room_width (branch axis): heads at y_j = head_offset + j*head_spacing
    Outputs: head count, interior S x L, max directional spacing, the four wall distances,
    covered extent / uncovered strip per axis, PASS/FAIL against CALLER-SUPPLIED caps.

    Coverage reach of an outer line toward its wall = half that axis's spacing (pure bay
    geometry), or max(half spacing, max_wall_distance_ft) when the caller supplies a wall cap.
    Uncovered strip = room dimension - covered extent (clipped to the room).

    No hard-coded code values. Caller caps, typical sources (labels only, not defaults):
      max_area_ft2 / max_spacing_ft: NFPA 13-2019 Table 10.2.4.2.1(b) OH 130 ft2 / 15 ft
        (held);
        FM DS 5-32 Jan-2026 §2.4.3.3.1.1(E) 12 ft max spacing (held).
      max_wall_distance_ft: NFPA 13-2019 §10.2.5.2.1 (wall distance not to exceed one-half of the allowable
        distance between sprinklers; held); FM DS 2-0
        §2.5.2.3.2 / Fig. 2.5.2.3.2 (4 in < D_W < 50 % S_MAX).
        If omitted the wall check is reported NOT CHECKED and does not count toward PASS.
    wall_compare: "le" (default) = NFPA 13-2019 §10.2.5.2.1 "shall not exceed" (wall <= cap);
                  "lt" = FM DS 2-0 Fig. 2.5.2.3.2 strict "<" reading (ASSUMED insurer) (wall < cap).
    edge_area_rule: "include" (default) = PASS also needs the edge-head area
        S x L <= max_area_ft2, with S = max(spacing, 2 x wall distance) per axis [V] (NFPA 13-2019
        §9.5.2.1 not pulled; rule per 13-74 §10.2.4.1.1 pointer "determined in accordance with 9.5.2.1"
        + comparison); "info" = report only (pre-CALC-2 backward path).
    SCREEN — verify with engineer of record. Locks: wet/dry/DI only; no hydraulics here.
    """
    L = _require_positive("room_length_ft", room_length_ft)
    W = _require_positive("room_width_ft", room_width_ft)
    sb = _require_positive("branch_spacing_ft", branch_spacing_ft)
    sh = _require_positive("head_spacing_ft", head_spacing_ft)
    nb_f = _as_float("n_branches", n_branches)
    nh_f = _as_float("heads_per_branch", heads_per_branch)
    if nb_f != int(nb_f) or int(nb_f) < 1:
        raise CalcError("n_branches must be a positive integer (>= 1)")
    if nh_f != int(nh_f) or int(nh_f) < 1:
        raise CalcError("heads_per_branch must be a positive integer (>= 1)")
    nb, nh = int(nb_f), int(nh_f)
    xb = _require_non_negative("branch_offset_ft", branch_offset_ft)
    yh = _require_non_negative("head_offset_ft", head_offset_ft)
    smax = _require_positive("max_spacing_ft", max_spacing_ft)
    amax = _require_positive("max_area_ft2", max_area_ft2)
    wcap = None if max_wall_distance_ft is None else _require_positive("max_wall_distance_ft", max_wall_distance_ft)
    smin = None if min_spacing_ft is None else _require_positive("min_spacing_ft", min_spacing_ft)
    ear = str(edge_area_rule).strip().lower()
    if ear not in ("include", "info"):
        raise CalcError("edge_area_rule must be 'include' or 'info'")
    wcmp = str(wall_compare).strip().lower()
    if wcmp not in ("le", "lt"):
        raise CalcError("wall_compare must be 'le' (NFPA 13-2019 §10.2.5.2.1) or 'lt' (FM DS 2-0 strict, ASSUMED)")
    x_last = xb + (nb - 1) * sb
    y_last = yh + (nh - 1) * sh
    eps = 1e-9
    if x_last > L + eps:
        raise CalcError(f"last branch x={x_last} ft lies outside room_length_ft={L}")
    if y_last > W + eps:
        raise CalcError(f"last head y={y_last} ft lies outside room_width_ft={W}")
    wx0, wx1 = xb, L - x_last
    wy0, wy1 = yh, W - y_last
    # directional spacings actually present (a single line has no spacing in that axis)
    sp_x = sb if nb > 1 else None
    sp_y = sh if nh > 1 else None
    present = [v for v in (sp_x, sp_y) if v is not None]
    max_dir = max(present) if present else 0.0
    reach_x = max(sb / 2.0, wcap) if wcap is not None else sb / 2.0
    reach_y = max(sh / 2.0, wcap) if wcap is not None else sh / 2.0
    cov_x = min(L, x_last + reach_x) - max(0.0, xb - reach_x)
    cov_y = min(W, y_last + reach_y) - max(0.0, yh - reach_y)
    unc_x = max(0.0, L - cov_x)
    unc_y = max(0.0, W - cov_y)
    area_int = sb * sh
    edge_area = max(sb, 2 * max(wx0, wx1)) * max(sh, 2 * max(wy0, wy1))
    spacing_ok = max_dir <= smax + eps
    area_ok = area_int <= amax + eps
    coverage_ok = unc_x <= eps and unc_y <= eps
    max_wall = max(wx0, wx1, wy0, wy1)
    if wcap is None:
        wall_ok = None
    elif wcmp == "lt":
        wall_ok = max_wall < wcap - eps
    else:
        wall_ok = max_wall <= wcap + eps
    min_ok = None if smin is None else all(v >= smin - eps for v in present)
    edge_ok = edge_area <= amax + eps
    checks = [spacing_ok, area_ok, coverage_ok] + [c for c in (wall_ok, min_ok) if c is not None]
    if ear == "include":
        checks.append(edge_ok)
    fails = []
    if not spacing_ok:
        fails.append(f"max directional spacing {max_dir} ft > cap {smax} ft")
    if not area_ok:
        fails.append(f"area/head {area_int} ft2 > cap {amax} ft2")
    if unc_x > eps:
        fails.append(f"uncovered strip x {unc_x} ft of {L} ft")
    if unc_y > eps:
        fails.append(f"uncovered strip y {unc_y} ft of {W} ft")
    if ear == "include" and not edge_ok:
        fails.append(f"edge area {edge_area:g} > {amax:g} ft2 (S=max(spacing, 2 x wall) per axis) [V]")
    if wall_ok is False:
        if wcmp == "lt":
            fails.append(f"wall distance {max_wall} ft not < cap {wcap} ft (wall_compare=lt, FM DS 2-0 strict, ASSUMED)")
        else:
            fails.append(f"wall distance {max_wall} ft > cap {wcap} ft (wall_compare=le, NFPA 13-2019 §10.2.5.2.1)")
    if min_ok is False:
        fails.append(f"spacing below min {smin} ft")
    return {
        "formula": "x_i=xb+i*Sb; y_j=yh+j*Sh; A=Sb*Sh; cover=lines +/- reach (S/2 or wall cap); uncovered=dim-cover",
        "room_length_ft": L, "room_width_ft": W,
        "n_heads": nb * nh,
        "area_per_head_ft2": area_int,
        "edge_area_per_head_ft2_v": edge_area,
        "edge_area_ok": edge_ok, "edge_area_rule": ear, "wall_compare": wcmp,
        "max_directional_spacing_ft": max_dir,
        "x_last_branch_ft": x_last, "y_last_head_ft": y_last,
        "wall_x0_ft": wx0, "wall_x1_ft": wx1, "wall_y0_ft": wy0, "wall_y1_ft": wy1,
        "max_wall_dist_actual_ft": max_wall,
        "covered_x_ft": cov_x, "covered_y_ft": cov_y,
        "uncovered_x_ft": unc_x, "uncovered_y_ft": unc_y,
        "coverage_x_pct": 100.0 * cov_x / L, "coverage_y_pct": 100.0 * cov_y / W,
        "spacing_ok": spacing_ok, "area_ok": area_ok, "coverage_ok": coverage_ok,
        "wall_ok": "NOT CHECKED (no caller wall cap)" if wall_ok is None else wall_ok,
        "min_spacing_ok": "NOT CHECKED" if min_ok is None else min_ok,
        "passes": all(checks),
        "fail_reasons": fails,
        "basis": ("caller-supplied caps; typical: NFPA 13-2019 Table 10.2.4.2.1(b) OH 130 ft2/15 ft; "
                  "FM DS 5-32 Jan-2026 §2.4.3.3.1.1(E) 12 ft; wall_compare=" + wcmp +
                  (" (FM DS 2-0 Fig. 2.5.2.3.2 strict <, ASSUMED)" if wcmp == "lt" else
                   " (NFPA 13-2019 §10.2.5.2.1 not to exceed, held)") +
                  "; edge_area_rule=" + ear + " (edge S=max(spacing, 2 x wall) per axis [V], "
                  "NFPA 13-2019 §9.5.2.1 not pulled; §10.2.4.1.1 pointer); SCREEN — verify with engineer of record"),
    }



REMOTE_AREA_FACTOR_2019 = 1.2  # NFPA 13-2019 §27.2.4.2.1 (held)
REMOTE_AREA_2019_TEXT = (
    "NFPA 13-2019 §27.2.4.2.1 (paraphrase): for the density/area method the design area is a rectangle "
    "with the dimension parallel to the branch lines at least 1.2 times sqrt(A), large enough to include "
    "sprinklers on both sides of the cross main."
)


def remote_area_rectangle(
    area_ft2: Number,
    head_spacing_ft: Number,
    branch_spacing_ft: Number,
    room_length_parallel_ft: Any = None,
    room_width_perp_ft: Any = None,
    wall_offset_ft: Any = None,
) -> dict[str, Any]:
    """Density/area remote-area rectangle shape.

    Source (2019, enforced AB floor): NFPA 13-2019 §27.2.4.2.1 verbatim (held 13-75 L10):
      dimension parallel to the branch lines >= 1.2 * sqrt(A); the rectangle "shall permit the
      inclusion of sprinklers on both sides of the cross main".
    Comparison only (NOT 2019 evidence): NFPA 13-2025 §28.2.4.2.1 same 1.2 sqrt(A) text
      (raw 13-FPF3-2025-ch28-full L685-686); §28.2.4.2.2 "Any fractional sprinkler shall be carried
      to the next higher whole sprinkler" (L688-690); §28.2.4.2.3 adjacent-branch extension.
    [V] UNVERIFIED for 2019: fractional-sprinkler round-up (heads per branch, total heads) and the
      branch-count / adjacent-branch carry-over — 2019 §27.2.4.2.2+ NOT pulled (13-75 GAPS). The op
      applies round-up as the 2025-comparison rule and labels every rounded output _v.

    Inputs: A = area of sprinkler operation (ft2, caller's design area incl. any increases already
      applied); S = head spacing along the branch (ft); L = spacing between branches (ft);
      optional room dimension parallel to branches / perpendicular (ft).
    NEG behaviour: a room shorter than 1.2 sqrt(A) parallel to the branches is REPORTED
      (room_short_parallel, shortfall, heads that fit) — the required length is NOT clipped.
    heads_fit_parallel was floor(Rp/S) = a SPACING count (6 for 75 ft at 11.00 ft). It
      keeps that value when wall_offset_ft is not given (also reported as spacings_fit_parallel, labelled in
      heads_fit_parallel_basis). With wall_offset_ft = w (end-head distance to each wall, caller input, NOT a code
      value) heads_fit_parallel = floor((Rp - 2w)/S + eps) + 1 = HEAD count (75, w 4.5, S 11.00 -> 7; end-head span
      66.0 ft); 0 if Rp < 2w. Round-up of fractional sprinklers: NFPA 13-2019 s27.2.4.2.2 HELD verbatim (13-79).
    Does NOT elect a remote area, locate the cross main, or do hydraulics. SCREEN — verify with engineer of record.
    """
    import math
    A = _require_positive("area_ft2", area_ft2)
    S = _require_positive("head_spacing_ft", head_spacing_ft)
    Lb = _require_positive("branch_spacing_ft", branch_spacing_ft)
    eps = 1e-9
    sqrt_a = math.sqrt(A)
    req_len = REMOTE_AREA_FACTOR_2019 * sqrt_a
    hpb_raw = req_len / S
    hpb = max(1, math.ceil(hpb_raw - eps))
    len_prov = hpb * S
    a_head = S * Lb
    n_raw = A / a_head
    n_tot = max(1, math.ceil(n_raw - eps))
    n_br_raw = n_tot / hpb
    n_br = max(1, math.ceil(n_br_raw - eps))
    last_br = n_tot - (n_br - 1) * hpb
    width = n_br * Lb
    warnings: list[str] = []
    out: dict[str, Any] = {
        "sqrt_a_ft": sqrt_a,
        "required_length_parallel_ft": req_len,
        "heads_per_branch_raw": hpb_raw,
        "heads_per_branch_v": hpb,
        "length_provided_parallel_ft_v": len_prov,
        "area_per_head_ft2": a_head,
        "n_heads_raw": n_raw,
        "n_heads_v": n_tot,
        "n_branches_v": n_br,
        "heads_on_last_branch_v": last_br,
        "width_perp_ft_v": width,
        "heads_area_ft2_v": n_tot * a_head,
        "rectangle_area_ft2_v": len_prov * width,
        "both_sides_of_cross_main": ("CHECK - 2019 §27.2.4.2.1: rectangle shall permit sprinklers on both sides "
                                     "of the cross main; op does not locate the cross main (caller/PE)"),
    }
    room_short = None
    if room_length_parallel_ft is not None:
        Rp = _require_positive("room_length_parallel_ft", room_length_parallel_ft)
        room_short = Rp + eps < req_len
        out["room_length_parallel_ft"] = Rp
        spacings = int(math.floor(Rp / S + eps))
        out["spacings_fit_parallel"] = spacings
        if wall_offset_ft is None:
            out["heads_fit_parallel"] = spacings
            out["heads_fit_parallel_basis"] = ("spacing count floor(Rp/S), NOT a head count; pass wall_offset_ft "
                                               "for heads = floor((Rp-2w)/S)+1")
            # explicit guard; wall_offset_ft stays OPTIONAL.
            out["heads_fit_parallel_warning"] = (
                f"DEFAULT USED: wall_offset_ft omitted -> heads_fit_parallel = spacing count floor(Rp/S) = "
                f"floor({Rp:g}/{S:g}) = {spacings}, NOT a head count; a wall-offset head count "
                "floor((Rp-2w)/S)+1 may differ (example: Rp 75 ft, S 11.00 ft, wall_offset_ft 4.5 gives 7, "
                "spacing count 6) - pass wall_offset_ft (caller input, not a code value)")
        else:
            w = _require_non_negative("wall_offset_ft", wall_offset_ft)
            avail = Rp - 2.0 * w
            heads_fit = int(math.floor(avail / S + eps)) + 1 if avail >= -eps else 0
            out["wall_offset_ft"] = w
            out["heads_fit_parallel"] = heads_fit
            out["length_between_end_heads_ft"] = max(0.0, (heads_fit - 1) * S)
            out["heads_fit_parallel_basis"] = ("head count floor((Rp-2w)/S)+1 with end-head wall offset w = "
                                               "wall_offset_ft (caller input)")
        out["shortfall_parallel_ft"] = max(0.0, req_len - Rp)
        if room_short:
            warnings.append(
                f"room {Rp:g} ft parallel to branches < 1.2*sqrt(A) = {req_len:.4f} ft; required length NOT "
                "clipped; adjacent-branch extension rule (2025 §28.2.4.2.3 comparison) NOT HELD for 2019 [V] - PE")
    out["room_short_parallel"] = room_short
    room_narrow = None
    if room_width_perp_ft is not None:
        Rw = _require_positive("room_width_perp_ft", room_width_perp_ft)
        room_narrow = Rw + eps < width
        out["room_width_perp_ft"] = Rw
        if room_narrow:
            warnings.append(f"room {Rw:g} ft perpendicular < rectangle width {width:g} ft (n_branches_v x L); reported, not clipped")
    out["room_narrow_perp"] = room_narrow
    out["fits_room"] = None if (room_short is None and room_narrow is None) else not (bool(room_short) or bool(room_narrow))
    out["warnings"] = warnings
    out["elects_remote_area"] = False
    out["basis"] = (REMOTE_AREA_2019_TEXT + " | 2025 §28.2.4.2.1 comparison only | round-up of fractional "
                    "sprinklers = NFPA 13-2019 §27.2.4.2.2 verbatim HELD (13-79; 2025 §28.2.4.2.2 comparison only); "
                    "adjacent-branch carry-over [V] | SCREEN - verify with engineer of record")
    return out


def pipe_velocity(q_gpm: Number, id_in: Any = None, nominal: Any = None, schedule: Any = None,
                  limit_fps: Any = None, limit_source: Any = None) -> dict[str, Any]:
    """Water velocity in a pipe, SCREEN ONLY: v[ft/s] = 0.4085*Q[gpm]/d[in]^2.

    Constant derivation: 1 gal = 231 in^3 and 1 ft^2 = 144 in^2, so Q gpm = Q*231/(12^3*60) ft^3/s
    = Q*231/103680 ft^3/s; A = (pi/4)*d^2/144 ft^2; v = Q/A = Q*(231/103680)*(576/pi)/d^2
    = Q*231/(180*pi)/d^2 = 0.40850*Q/d^2 (`k_const` 0.4085 is used; `k_const_derived` is reported).
    ID: explicit `id_in` (inches, internal). No Sch 40 nominal->ID table is held in _calc, so `nominal` and
    `schedule` are LABELS only (election: Sch 40; the caller's ID must match the pipe); nominal
    without `id_in` raises CalcError.
    NO pass/fail is emitted against any velocity limit. FM DS 2-0 (Oct 2021, Interim rev Jan 2024) App A
    pp.157/161: 30 ft/s is the Hazen-Williams -> Darcy-Weisbach method switch, not a cap; there is no 20 ft/s
    in DS 2-0 (the 20 ft/s figures are FM DS 3-10 private-main connections / DS 3-2 fill pipes). A caller may
    pass `limit_fps` WITH a non-empty `limit_source`; the op then reports only v - limit and v / limit
    (arithmetic, not a verdict).
    NFPA 13-2019 s27.2.1.4* (held clause, paraphrased
    here): velocity of water flow shall not be limited when using Hazen-Williams or Darcy Weisbach unless
    required by other NFPA standards. s27.2.1.1-.3 formula text is HOLD (13-81) -> [V].
    SCREEN - verify with engineer of record.
    """
    import math
    q = _require_positive("q_gpm", q_gpm)
    if id_in is None:
        if nominal is not None:
            raise CalcError("id_in is required: no held nominal-size/schedule ID table in _calc "
                            "(nominal and schedule are labels only; Sch 40 elected)")
        raise CalcError("id_in must be a number")
    d = _require_positive("id_in", id_in)
    k_const = 0.4085
    v = k_const * q / (d * d)
    out: dict[str, Any] = {
        "formula": "pipe velocity v[ft/s] = 0.4085*Q[gpm]/d[in]^2 (SCREEN)",
        "q_gpm": q, "id_in": d, "k_const": k_const, "k_const_derived": 231.0 / (180.0 * math.pi),
        "flow_area_in2": math.pi / 4.0 * d * d, "v_fps": v,
        "id_source": "caller-supplied internal diameter (no held nominal/schedule ID table in _calc)",
    }
    if nominal is not None:
        out["nominal"] = str(nominal)
    if schedule is not None:
        out["schedule"] = str(schedule)
    if limit_fps is not None:
        lim = _require_positive("limit_fps", limit_fps)
        if not isinstance(limit_source, str) or not limit_source.strip():
            raise CalcError("limit_source is required with limit_fps (the limit is a caller-supplied input with provenance)")
        out["limit_fps"] = lim
        out["limit_source"] = limit_source.strip()
        out["v_minus_limit_fps"] = v - lim
        out["v_over_limit"] = v / lim
    out["nfpa13_cite"] = ("NFPA 13-2019 s27.2.1.4* (paraphrase of the held clause 13-78): "
                          "velocity of water flow shall not be limited "
                          "under Hazen-Williams or Darcy Weisbach unless other NFPA standards require; "
                          "s27.2.1.1-.3 formula text HOLD (13-81) -> [V]")
    out["friction_method_note"] = ("No velocity pass/fail emitted. FM DS 2-0 (Oct 2021, Interim rev Jan 2024) App A pp.157/161: "
                                   "30 ft/s is the Hazen-Williams -> Darcy-Weisbach method switch, not a cap; no 20 ft/s in "
                                   "DS 2-0 (the 20 ft/s figures are FM DS 3-10 private-main connections / DS 3-2 fill pipes). "
                                   "Supply any limit as limit_fps + limit_source")
    out["basis"] = "SCREEN - verify with engineer of record"
    return out


OPS = {
    "pipe_velocity": "pipe_velocity", "pipe-velocity": "pipe_velocity", "velocity": "pipe_velocity",
    "remote_area_rectangle": "remote_area_rectangle", "remote-area-rectangle": "remote_area_rectangle", "remote_area": "remote_area_rectangle",
    "sprinkler_grid_coverage": "sprinkler_grid_coverage", "sprinkler-grid-coverage": "sprinkler_grid_coverage", "grid_coverage": "sprinkler_grid_coverage",
    "obscuration_sc": "obscuration_sc", "obscuration-sc": "obscuration_sc", "sc_sh_n": "obscuration_sc", "chamber_sensitivity": "obscuration_sc",
    "fus_rff": "fus_rff", "fus-rff": "fus_rff", "fus_required_fire_flow": "fus_rff",
    "air_setpoint_stack": "air_setpoint_stack", "air-setpoint-stack": "air_setpoint_stack", "pmd_margin_stack": "air_setpoint_stack",
    "battery_standby": "battery_standby", "battery-standby": "battery_standby",
    "diesel_derate": "diesel_derate", "diesel-derate": "diesel_derate",
    "electric_overpressure": "electric_overpressure", "electric-overpressure": "electric_overpressure",
    "compressor_n2_sizing": "compressor_n2_sizing", "compressor-n2-sizing": "compressor_n2_sizing",
    "brace_spacing_max": "brace_spacing_max", "brace-spacing-max": "brace_spacing_max",
    "hw": "hazen_williams",
    "hazen_williams": "hazen_williams",
    "hazen-williams": "hazen_williams",
    "density_area": "density_area",
    "density-area": "density_area",
    "hydrant": "hydrant_supply",
    "hydrant_supply": "hydrant_supply",
    "pump_envelope": "pump_envelope",
    "pump-envelope": "pump_envelope",
    "louver": "louver_free_area",
    "louver_free_area": "louver_free_area",
    "pipe_volume": "pipe_volume",
    "air_fill_scfm": "air_fill_scfm",
    "air_fill": "air_fill_scfm",
    "k_factor": "k_factor",
    "tapered_branch": "tapered_branch",
    "di_trip_to_water": "di_trip_to_water",
    "seismic_fp": "seismic_fp",
    "brace_load": "brace_load",
    "junction_balance": "junction_balance",
    "loop_two_path": "loop_two_path", "loop-two-path": "loop_two_path", "looped_main": "loop_two_path",
    "relief_check": "relief_check",
    "hose_duration": "hose_duration",
    "cp_from_sds": "cp_from_sds",
    "dry_delivery_screen": "dry_delivery_screen",
    "dry-delivery-screen": "dry_delivery_screen",
    "pump_net_at_q": "pump_net_at_q", "pump-net-at-q": "pump_net_at_q",
    "cross_main_walk": "cross_main_walk", "cross-main-walk": "cross_main_walk",
    "bor_demand_pressure": "bor_demand_pressure", "bor-demand-pressure": "bor_demand_pressure",
    "rated_pressure_screen": "bor_demand_pressure",
    "rated_pressure_select": "rated_pressure_select", "rated-pressure-select": "rated_pressure_select",
    "pump_rated_pressure": "rated_pressure_select",
}


_HOSE_DUR = {  # NFPA 13-2025 Table 19.2.3.1.2 (inside hose gpm, total inside+outside gpm, duration min range)
    "light": (0, 100, 30, 30),
    "ordinary": (0, 250, 60, 90),
    "extra": (0, 500, 90, 120),
}


def hose_duration(hazard: str, supervised: Any = False) -> dict[str, Any]:
    """Hose stream allowance and duration lookup.

    NFPA 13-2025 Table 19.2.3.1.2 (values: inside hose 0, 50 or 100 gpm; total combined
    inside+outside LH 100 / OH 250 / EH 500 gpm; duration LH 30, OH 60-90, EH 90-120 min).
    s19.2.3.1.3 (OCR L34899): the LOWER duration is permitted only where waterflow and
    supervisory devices are electrically supervised and monitored at an approved, constantly
    attended location; otherwise the upper value is used here (conservative).
    Storage, special-occupancy and ESS durations are NOT covered (chapters 20+, NFPA 855).
    """
    h = str(hazard).strip().lower().split()[0].replace("-", "")
    h = {"lh": "light", "oh": "ordinary", "oh1": "ordinary", "oh2": "ordinary",
         "eh": "extra", "eh1": "extra", "eh2": "extra"}.get(h, h)
    if h not in _HOSE_DUR:
        raise CalcError("hazard must be light, ordinary or extra (NFPA 13-2025 Table 19.2.3.1.2)")
    sup = bool(supervised) and str(supervised).lower() not in ("false", "0", "no")
    inside, total, lo, hi = _HOSE_DUR[h]
    dur = lo if sup else hi
    return {"hazard": h, "inside_hose_gpm_options": [0, 50, 100], "hose_total_gpm": total,
            "duration_min": dur, "duration_range_min": [lo, hi], "supervised": sup,
            "basis": "NFPA 13-2025 Table 19.2.3.1.2 / s19.2.3.1.3"}


def dispatch(op: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run one named op. `inputs` is a dict of formula kwargs (already aliased)."""
    key = (op or "").strip().lower().replace(" ", "_")
    if key not in OPS:
        raise CalcError(
            f"unknown op {op!r}; want one of: hw, density_area, hydrant, "
            "pump_envelope, louver, pipe_volume, air_fill_scfm"
        )
    name = OPS[key]
    fn = {
        "hazen_williams": hazen_williams,
        "density_area": density_area,
        "hydrant_supply": hydrant_supply,
        "pump_envelope": pump_envelope,
        "louver_free_area": louver_free_area,
        "pipe_volume": pipe_volume,
        "air_fill_scfm": air_fill_scfm,
        "compressor_n2_sizing": compressor_n2_sizing,
        "diesel_derate": diesel_derate,
        "electric_overpressure": electric_overpressure,
        "brace_spacing_max": brace_spacing_max,
        "k_factor": k_factor, "tapered_branch": tapered_branch,
        "di_trip_to_water": di_trip_to_water, "seismic_fp": seismic_fp, "brace_load": brace_load,
        "junction_balance": junction_balance,
        "loop_two_path": loop_two_path,
        "relief_check": relief_check,
        "hose_duration": hose_duration,
        "cp_from_sds": cp_from_sds,
        "dry_delivery_screen": dry_delivery_screen,
        "pump_net_at_q": pump_net_at_q,
        "cross_main_walk": cross_main_walk,
        "battery_standby": battery_standby,
        "bor_demand_pressure": bor_demand_pressure,
        "rated_pressure_select": rated_pressure_select,
        "air_setpoint_stack": air_setpoint_stack,
        "fus_rff": fus_rff,
        "obscuration_sc": obscuration_sc,
        "sprinkler_grid_coverage": sprinkler_grid_coverage,
        "remote_area_rectangle": remote_area_rectangle,
        "pipe_velocity": pipe_velocity,
    }[name]
    return fn(**inputs)
