"""Annex D ADS and STI measurement grid counter. NFPA 72-2022/2025 Annex D.3.7.4, D.3.7.5 and A.24.4.2.2.2 (72-96 pull).
Annex is advisory. Grid rule ceil(L/40) x ceil(W/40), min 1, is a screening choice. Verify with the engineer of record."""
import math
SPACING_FT = 40.0

def points(L, W, spacing=SPACING_FT):
    return max(1, math.ceil(L / spacing)) * max(1, math.ceil(W / spacing))

def max_on_axis(n):
    return n // 3

def must_split(h1, h2, finish1, finish2):
    """True if two zones should be separate ADSs: ceiling height change over 20 percent or finish change."""
    return abs(h1 - h2) / min(h1, h2) > 0.20 or finish1 != finish2

def grid(zones):
    """zones: list of dict(name, L, W, on_axis). Returns rows (name, n, cap, ok)."""
    out = []
    for z in zones:
        n = points(z["L"], z["W"]); cap = max_on_axis(n)
        out.append((z["name"], n, cap, z.get("on_axis", 0) <= cap))
    return out
