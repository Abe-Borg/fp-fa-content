#!/usr/bin/env python3
"""Pure stdlib fire-protection arithmetic.

Callers set inputs. This module does the arithmetic. No numpy, no network, no
listed water-delivery-time model, and no shop-curve invention.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union

# US fire-protection Hazen-Williams (NFPA 13 / handbook form).
HW_COEFF = 4.52
HW_FLOW_EXP = 1.85
HW_DIAM_EXP = 4.87

# psi per foot of water. Stated constant — do not silently swap 0.433.
PSI_PER_FT_WATER = 0.4333

# Hydrant / supply-curve exponent (same 1.85 as HW).
SUPPLY_EXP = 1.85

# Pump envelope defaults (NFPA 20 / FM DS 3-7 screening). CHURN_FRAC_MAX 1.40 = NFPA 20-2019/2022/2025 s6.2.2; P150_FRAC 0.65 = s6.2.1. CHURN_FRAC_PREF 1.20 is practice, not code.
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
    """Dry/DI air-compressor and N2-generator sizing (batch9 R5).

    Compressor: sized on the LARGEST single system to restore its supervisory pressure in
    t_min (NFPA 13-2025 s8.2.7.3: 30 min).
    N2 generator: sized on the connected total of all systems over the same t_min
    (design practice, not code; verify with the engineer of record).
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
                     "N2: connected total of the systems on this run (design practice, not code; verify with the engineer of record)"}

def k_factor(k: Number, p_psi: Any = None, q_gpm: Any = None, density: Any = None,
             area_ft2: Any = None, min_p_psi: Any = None) -> dict[str, Any]:
    """Sprinkler/nozzle discharge q = K*sqrt(P) (NFPA 13-2025 K-factor definition; hydraulic calc ch.).

    Modes (exactly one): p_psi -> Q; q_gpm -> P; density (gpm/ft2) + area_ft2 (head coverage)
    -> q_req = density*area, P_req = (q_req/K)^2 floored at min_p_psi (batch7 R5).
    Floor: 7 psi = FM DS 2-0 (Oct 2021 / Interim Rev Jan 2024) s2.5.1.1.2 minimum sprinkler design
    pressure; US listings carry the same 7 psi minimum (NFPA 13 section pin still open; verify with the engineer of record).
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


def tapered_branch(k: Number, p_end_psi: Number, c: Number, segments: Any,
                   min_head_psi: Number = 7.0) -> dict[str, Any]:
    """Multi-node branch line, end-head-first (rebuilt batch6 R2).

    Sources: Hazen-Williams per-foot loss p = 4.52 Q^1.85 / (C^1.85 d^4.87) (NFPA 13-2025 hydraulic
    calc chapter; same constant as hazen_williams op), head flow q = K*sqrt(P) (NFPA 13-2025 K-factor
    definition), elevation 0.4333 psi/ft. 7 psi default minimum head pressure (NFPA 13; section
    re-pin pending). C is an input (lock: C = 100 for dry/DI).

    segments[i] = pipe from node i to node i+1 toward the inlet:
      {"d_in", "length_ft", "eq_ft" (fitting equivalent length, default 0), "dz_ft" (+ = inlet higher
       than the downstream node, default 0), "head" (head at the upstream node, default True),
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
        nodes.append({"node": i, "p_psi": p, "pf_psi": pf, "pe_psi": pe, "q_head_gpm": qh, "q_cum_gpm": q})
        rows.append(line)
    return {"formula": "tapered branch node walk (HW 4.52, q=K*sqrt(P), 0.4333 psi/ft)", "nodes_detail": rows,
            "nodes": nodes, "q_inlet_gpm": q, "p_inlet_psi": p, "k_equiv_inlet": q / math.sqrt(p),
            "end_head_ok": p_end_psi >= pmin, "min_head_psi": pmin}


DI_LIMITS_S = {"FM": 30.0, "NFPA-LH": 60.0, "NFPA-OH": 50.0, "NFPA-EH": 45.0, "NFPA-HP": 40.0, "NFPA-DU": 15.0}
# NFPA 13-2025 Table 8.2.4.3.2. "NFPA" alias = NFPA-OH (data hall analogue).


def di_trip_to_water(v_gal: Number, q_fill_gpm: Number, t_detect_s: Number = 0.0,
                     t_release_s: Number = 0.0, t_exhaust_s: Number = 0.0,
                     limit_s: Any = None, basis: str = "FM") -> dict[str, Any]:
    """SCREEN ONLY - not a listed water-delivery calc (rebuilt batch6 R3).

    t_total = t_detect + t_release + t_exhaust + 60 * V / Q_fill.
    V = trapped pipe volume to the test/remote outlet (gal); Q_fill = average fill flow (gpm) at low
    back-pressure from the supply curve. Sub-times are vendor/test inputs. This ignores air
    compression and transit slowdown, so it is OPTIMISTIC; a pass is necessary, not sufficient.
    Limits: basis "FM" = 30 s (FM DS 5-32, provisional default, labeled FM); basis "NFPA-xx" = NFPA 13-2025 Table 8.2.4.3.2 (2022 Table 8.2.3.6.1): LH 60 s (1 head),
    OH 50 s (2 heads), EH 45 s (4), HP 40 s (4), DU 15 s (1); "NFPA" = NFPA-OH. Per 2025 §8.2.4.3.3 the
    clock starts when the most remote head(s) open, so t_detect/t_release are a conservative add-on.
    limit_s overrides basis.
    """
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
    return {"formula": "t = t_det + t_rel + t_exh + 60*V/Q_fill (screen, optimistic)", "t_fill_s": tf,
            "t_total_s": t, "limit_s": lim, "limit_basis": src, "margin_s": lim - t,
            "passes_screen": t <= lim + 1e-9, "v_max_gal_at_limit": max(v_max, 0.0)}


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


# NFPA 13-2025 Tables 18.5.5.2 (rows held in this table): max Fpw (lb) by lateral
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
    cp_from_sds(). Older editions (2022 and earlier) used a Cp table vs Ss (docstring fixed batch8 R5;
    prior text "Cp from NFPA 13 seismic coefficient table (held)" was stale for 2025).
    segments: [{"lb_per_ft": w, "length_ft": L}].
    Optional (batch7 R6): pipe + spacing_ft -> Tables 18.5.5.2 max Fpw check (pipe_ok);
    listed_capacity_lb + angle_deg -> capacity / Table 18.5.2.3 angle divisor (brace_ok).
    Divisor reading of Table 18.5.2.3 is an interpretation. Verify with the engineer of record.
    capacity_is_horizontal=True for FM
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
    # batch7 R6: optional pipe-capacity and brace-angle checks.
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
    """Max lateral brace spacing (batch9 R13), chained to cp_from_sds.
    For each held NFPA 13-2025 Tables 18.5.5.2 column upper bound (20/25/30/35/40 ft):
    ZOI weight = (main_lb_per_ft + branch_lb_per_main_ft) * S; Wp = 1.15*ZOI (s18.5.9.2);
    Fpw = Cp*Wp (s18.5.9.3); pass if Fpw <= table max for pipe (and <= listed/angle divisor
    if given). Returns the largest passing S. branch_lb_per_main_ft = tributary branch-line
    water-filled weight per ft of main (caller supplies the weight; verify with the engineer of record).
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
    """Diesel engine derate, ADDITIVE (batch10 R3).
    NFPA 20-2025 s11.2.2.4: deduct 3 % per 1,000 ft above 300 ft; s11.2.2.5: deduct 1 % per 10 F
    above 77 F (2022 text matches). The code gives no combination rule. ADDITIVE
    (1 - (a+t)/100) is the design practice (the larger deduction). Verify with the engineer of record.
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
           "basis": "NFPA 20-2025 s11.2.2.4/.5 (additive combination is design practice), s11.2.2.7"}
    if nameplate_hp is not None:
        np_ = _require_positive("nameplate_hp", nameplate_hp)
        out.update({"nameplate_hp": np_, "derated_hp": np_ * factor, "engine_ok": np_ * factor >= bhp - 1e-9,
                    "deficit_hp": max(0.0, req - np_)})
    return out


# --- dispatch helpers for run.py ---

def cp_from_sds(sds: Any = None, attach_height_ratio: Any = None,
                apply_height_factor: bool = False) -> dict[str, Any]:
    """Seismic coefficient Cp (batch8 R5).

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
                 component_rating_psi: Number = 175.0, elevation_adj_psi: Number = 0.0) -> dict[str, Any]:
    """Diesel main relief valve screen.

    NFPA 20-2025 s4.20.1.2: a diesel fire pump needs a main relief valve when 121 percent
    of the net rated shutoff (churn) pressure plus the maximum static suction pressure,
    adjusted for elevation, exceeds the component rating.
    relief_check_psi = 1.21*net_shutoff + max_static_suction + elevation_adj (elevation_adj is
    signed: negative for components above the pump). Uses the net shutoff, not the rated net.
    pump_envelope churn_frac is a different quantity.
    """
    sh = _require_positive("net_shutoff_psi", net_shutoff_psi)
    st = float(max_static_suction_psi)
    if st < 0:
        raise CalcError("max_static_suction_psi must be >= 0")
    rt = _require_positive("component_rating_psi", component_rating_psi)
    metric = 1.21 * sh + st + float(elevation_adj_psi or 0.0)
    return {"relief_check_psi": round(metric, 2), "component_rating_psi": rt,
            "relief_valve_required": metric > rt, "margin_psi": round(rt - metric, 2),
            "basis": "NFPA 20-2025 s4.20.1.2 (diesel)"}


def junction_balance(q_low_gpm: Number, p_low_psi: Number, p_high_psi: Number,
                     q_high_gpm: Number = 0.0, tol_psi: Number = 0.5) -> dict[str, Any]:
    """Two-path hydraulic junction balance (batch7 R19).

    NFPA 13-2025 s28.2.2.4.1: pressures at hydraulic junction points balance within
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
                        basis: str = "FM", system_type: str = "dry") -> dict[str, Any]:
    """Chained op (batch8 R26): pipe_volume(segments) -> NFPA 13-2025 s8.2.4.2.1/.2 size
    exemption check -> di_trip_to_water screen. SCREEN ONLY, optimistic (see di_trip_to_water).

    NFPA 13-2025 s8.2.4.2.1: <= 500 gal without QOD, s8.2.4.2.2: <= 750 gal with QOD -> no
    specific water-delivery time required. FM DS 5-32 (Jan 2026)
    s2.4.3.2.1.2 D 30 s still applies to data-center preaction regardless (provisional).
    """
    pv = pipe_volume(segments)
    v = float(pv["volume_gal"])
    q = bool(qod) and str(qod).lower() not in ("false", "0", "no")
    st = str(system_type).strip().lower().replace("-", "_").replace(" ", "_")
    st = {"double_interlock": "di", "di_preaction": "di", "dry_pipe": "dry"}.get(st, st)
    if st not in ("dry", "di"):
        raise CalcError("system_type must be 'dry' or 'di' (wet/dry/DI locks; single-interlock not supported)")
    # batch10 R1 fix: DI gets NO 750 gal QOD size exemption. NFPA 13-2025 s8.3.2.3.1.1: DI <= 500 gal
    # exempt; a QOD only "helps meet" the delivery-time options (s8.3.2.3.2), it does not raise the cap.
    # The 750 gal QOD cap is a dry-pipe rule only (s8.2.4.2.2).
    cap = 750.0 if (q and st == "dry") else 500.0
    exempt = v <= cap + 1e-9
    trip = di_trip_to_water(v, q_fill_gpm, t_detect_s, t_release_s, t_exhaust_s, limit_s, basis)
    nb = ("NFPA 13-2025 s8.3.2.3.1.1 (DI 500 gal; QOD does not extend, s8.3.2.3.2)" if st == "di" else
          "NFPA 13-2025 s8.2.4.2.1 (500 gal) / s8.2.4.2.2 (750 gal w/ QOD)")
    out = {"volume_gal": v, "system_type": st, "qod": q, "nfpa_size_cap_gal": cap,
           "nfpa_delivery_time_exempt": exempt, "nfpa_basis": nb}
    out.update({k: trip[k] for k in ("t_fill_s", "t_total_s", "limit_s", "limit_basis",
                                      "margin_s", "passes_screen", "v_max_gal_at_limit")})
    out["formula"] = "V=sum(pi/4*ID^2/144*7.48*L); t = t_det + t_rel + t_exh + 60*V/Q_fill"
    return out


OPS = {
    "diesel_derate": "diesel_derate", "diesel-derate": "diesel_derate",
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
    "relief_check": "relief_check",
    "hose_duration": "hose_duration",
    "cp_from_sds": "cp_from_sds",
    "dry_delivery_screen": "dry_delivery_screen",
    "dry-delivery-screen": "dry_delivery_screen",
}


_HOSE_DUR = {  # NFPA 13-2025 Table 19.2.3.1.2 (inside hose gpm, total inside+outside gpm, duration min range)
    "light": (0, 100, 30, 30),
    "ordinary": (0, 250, 60, 90),
    "extra": (0, 500, 90, 120),
}


def hose_duration(hazard: str, supervised: Any = False) -> dict[str, Any]:
    """Hose stream allowance and duration lookup (batch8 R17).

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
        "brace_spacing_max": brace_spacing_max,
        "k_factor": k_factor, "tapered_branch": tapered_branch,
        "di_trip_to_water": di_trip_to_water, "seismic_fp": seismic_fp, "brace_load": brace_load,
        "junction_balance": junction_balance,
        "relief_check": relief_check,
        "hose_duration": hose_duration,
        "cp_from_sds": cp_from_sds,
        "dry_delivery_screen": dry_delivery_screen,
    }[name]
    return fn(**inputs)
