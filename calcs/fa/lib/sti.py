"""STI acceptance evaluator per ADS.
Source: NFPA 72-2022 and 72-2025 Annex D (informative; binding only where adopted).
Annex D.2.4.1 screen: at least 90 percent of locations at or above the floor, and the average at or above the average minimum.
floor/avg: STI 0.45/0.50, CIS 0.65/0.70. Single location: value must be >= avg_min.
r05 = nearest 0.05, ties down (screening choice; verify with the engineer of record).
Location values are compared raw (never rounded up to the floor)."""
from decimal import Decimal, ROUND_HALF_DOWN
from statistics import mean
LIMITS = {"STI": (0.45, 0.50), "CIS": (0.65, 0.70)}

def r05(x):
    return float((Decimal(str(round(x, 3))) / Decimal("0.05")).quantize(Decimal(1), rounding=ROUND_HALF_DOWN) * Decimal("0.05"))

def evaluate(locs, scale="STI", frac=0.90):
    """locs: list of per-location reading tuples. Returns dict."""
    floor, amin = LIMITS[scale]
    per = [round(mean(r), 3) for r in locs]
    if len(per) == 1:
        return {"per": per, "frac": 1.0 if per[0] >= floor else 0.0, "avg": per[0], "avg_rep": per[0],
                "pass": per[0] >= amin, "basis": "single location, D.2.4 single-point text"}
    n_ok = sum(v >= floor for v in per); f = n_ok / len(per); a = mean(per); ar = r05(a)
    return {"per": per, "frac": f, "avg": a, "avg_rep": ar, "pass": f >= frac and ar >= amin,
            "basis": "D.2.4.1 90% floor + D.2.4.12 rounded average"}
