"""Le Chatelier mixture LFL and %LFL helpers.

Formula [PARA source]: USBM Bulletin 627 (Zabetakis 1965), eq. 46/47:
  L_mix = 100 / sum(C_i / L_i), C_i = vol% of combustible i on a fuel-only basis (sum C_i = 100).
  Bulletin text (grep -F): "calculated by Le Chatelier's law (40, 129, 235) :"
  Worked example in the Bulletin: 80/15/5 methane/ethane/propane at LFL 5.0/3.0/2.1 -> "=4.3 vol pct."
Limits [PRACTICE]: rule is reliable for paraffins; check with test data for other mixes. Use the lower of
calc and test-report LFL. Verify with the engineer of record for any design setpoint.
Code thresholds are not set here. NFPA 69 8.3.1 25 percent LFL and NFPA 855 10 percent LFL are held in pulls.
"""

def lfl_mix(mix, lfl):
    """mix: {gas: vol% or fraction}; lfl: {gas: LFL vol%}. Gases with LFL None are inert, dropped.
    Returns mixture LFL in vol% on a fuel-only basis."""
    fuel = {k: v for k, v in mix.items() if lfl.get(k)}
    if not fuel:
        raise ValueError("no combustible component")
    tot = sum(fuel.values())
    return 100.0 / sum((v / tot * 100.0) / lfl[k] for k, v in fuel.items())

def lfl_with_diluent(mix, lfl):
    """Simple whole-gas LFL treating inert parts as diluent (EX-41 method): L_fuel * total / fuel. [PRACTICE]"""
    tot = sum(mix.values())
    fuel = sum(v for k, v in mix.items() if lfl.get(k))
    return lfl_mix(mix, lfl) * tot / fuel

def pct_of_lfl(conc_vol_pct, lfl_vol_pct):
    return 100.0 * conc_vol_pct / lfl_vol_pct

def setpoint(lfl_vol_pct, pct):
    """Concentration at pct% of LFL. Returns (vol%, ppm)."""
    v = lfl_vol_pct * pct / 100.0
    return v, v * 1e4

# two NFPA 855-2023 gas detection paths, both held in 855-08 [CODE].
# 9.6.5.1.5.4 normal-operation exhaust: activate exhaust when gas "exceeds 25 percent of the LFL".
# 9.6.5.6.7(1) explosion control (CCR): activate "at no more than 10 percent of the LFL".
PATH_PCT = {"9.6.5.1.5.4 exhaust": 25.0, "9.6.5.6.7 CCR and alarm": 10.0}

def trigger_paths(lfl_vol_pct):
    """Return {path: (pct, vol%, ppm)} and the governing (lowest) ppm. Asserts pct < 100 to catch the 100% LFL error."""
    out = {k: (p,) + setpoint(lfl_vol_pct, p) for k, p in PATH_PCT.items()}
    for k, (p, v, ppm) in out.items():
        assert 0 < p < 100 and v < lfl_vol_pct
    gov = min(out.values(), key=lambda t: t[2])
    return out, gov


def setpoints_for(mix, lfl, screens):
    """Mixture LFL plus one setpoint per caller-supplied percent.

    screens: list of {name, pct, basis} with basis "fuel" or "diluted".
    An empty list returns the mixture only. This function does not choose pct.
    It does not return an election or a duration.
    """
    fuel = lfl_mix(mix, lfl)
    diluted = lfl_with_diluent(mix, lfl)
    rows = []
    for screen in screens or []:
        basis = screen.get("basis")
        if basis == "fuel":
            base = fuel
        elif basis == "diluted":
            base = diluted
        else:
            raise ValueError("basis must be fuel or diluted")
        pct = float(screen["pct"])
        vol, ppm = setpoint(base, pct)
        rows.append({
            "name": screen.get("name") or screen.get("id") or "",
            "pct": pct,
            "basis": basis,
            "lfl_vol_pct": base,
            "vol_pct": vol,
            "ppm": ppm,
        })
    return {
        "lfl_fuel_vol_pct": fuel,
        "lfl_diluted_vol_pct": diluted,
        "setpoints": rows,
        "election": None,
        "duration": None,
    }
