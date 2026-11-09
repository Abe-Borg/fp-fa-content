"""NAC voltage drop library. Not for construction. Verify with engineer of record.

Basis and tags:
- Starting voltage is CUSTV or CMSTV at the appliance minimum input voltage [CODE NFPA 72-2025 18.3.7.1.1, 72-14].
- MVA is factored into each circuit where used [CODE NFPA 72-2025 18.3.7.1.2.1, 72-14].
- Length includes both conductors [CODE NFPA 72-2025 18.3.7.3(2), 72-14]. So ohm/kft is NOT doubled again.
- Methods: ELL or PTP [CODE NFPA 72-2025 18.3.7.4, 72-14]. ELL is the most conservative per annex [HB A.18.3.7.4, 72-14].
- 75 C wire basis [CODE NFPA 72-2025 18.3.7.5, 72-14]. Not in 2019 or 2022 (72-57).
- Resistance: NEC 2023 Ch 9 Table 8, uncoated copper, ohm/kft at 75 C [CODE 70-03]. Where adopted; AHJ to confirm.
- Regulated 24 VDC appliances 16 to 33 VDC [HB A.18.3.7, 72-14]. Use the listing value on a real job.
- Default start voltage 20.4 V is end of discharge practice only [PRACTICE]. Verify with the engineer of record on a real job.
Formula: Vd = I x R, R = L_both_ft x ohm_per_kft / 1000. Veol = Vstart - MVA - Vd.
"""

# NEC 2023 Ch 9 Table 8, uncoated copper, ohm/kft at 75 C (70-03). Verified by grep in tests.
TABLE8_UNCOATED_OHM_PER_KFT = {
    ("18", "solid"): 7.77, ("18", "stranded"): 7.95,
    ("16", "solid"): 4.89, ("16", "stranded"): 4.99,
    ("14", "solid"): 3.07, ("14", "stranded"): 3.14,
    ("12", "solid"): 1.93, ("12", "stranded"): 1.98,
    ("10", "solid"): 1.21, ("10", "stranded"): 1.24,
}

DEFAULT_V_START = 20.4  # [PRACTICE] end of discharge start. Maker CUSTV governs.
DEFAULT_V_MIN = 16.0    # [HB A.18.3.7] regulated 24 VDC low limit. Listing governs.


def ohm_per_kft(awg, strand="stranded"):
    return TABLE8_UNCOATED_OHM_PER_KFT[(str(awg), strand)]


def loop_resistance(length_both_ft, awg, strand="stranded"):
    if length_both_ft < 0:
        raise ValueError("length must be >= 0")
    return length_both_ft * ohm_per_kft(awg, strand) / 1000.0


def ell(currents_a, length_one_way_ft, awg, strand="stranded", v_start=DEFAULT_V_START,
        v_min=DEFAULT_V_MIN, mva=0.0):
    """End-line-loaded. All load lumped at the far end. Returns dict."""
    i = sum(currents_a)
    r = loop_resistance(2.0 * length_one_way_ft, awg, strand)
    vd = i * r
    veol = v_start - mva - vd
    return {"method": "ELL", "I": i, "R": r, "Vd": vd, "Veol": veol, "pass": veol >= v_min}


def ptp(segments, awg, strand="stranded", v_start=DEFAULT_V_START, v_min=DEFAULT_V_MIN, mva=0.0):
    """Point-to-point. segments = [(one_way_ft_from_previous_point, appliance_current_a), ...]
    from the panel outward. Each segment carries all current downstream of it."""
    v = v_start - mva
    worst = v
    downstream = [sum(c for _, c in segments[k:]) for k in range(len(segments))]
    vd_total = 0.0
    for (ft, _), i_seg in zip(segments, downstream):
        dv = i_seg * loop_resistance(2.0 * ft, awg, strand)
        vd_total += dv
        v -= dv
        worst = min(worst, v)
    return {"method": "PTP", "I": downstream[0] if segments else 0.0, "Vd": vd_total,
            "Veol": worst, "pass": worst >= v_min}


def max_one_way_ft(total_current_a, awg, strand="stranded", v_start=DEFAULT_V_START,
                   v_min=DEFAULT_V_MIN, mva=0.0):
    if total_current_a <= 0:
        raise ValueError("current must be > 0")
    v_allow = v_start - mva - v_min
    if v_allow <= 0:
        return 0.0
    return v_allow / total_current_a / (ohm_per_kft(awg, strand) / 1000.0) / 2.0


def smallest_passing_awg(currents_a, length_one_way_ft, strand="stranded", **kw):
    for awg in ("18", "16", "14", "12", "10"):
        if ell(currents_a, length_one_way_ft, awg, strand, **kw)["pass"]:
            return awg
    return None
