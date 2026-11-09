"""ADS dBA margin library. Verify with engineer of record. Where adopted; AHJ to confirm.
Formula [PARA physics, annex-backed]: free-field point source, L(d) = L_ref - 20 log10(d / d_ref).
  Free-field point source: halving the distance raises level by 6 dB (NFPA 72 Annex D, informative).
Sum of n sources (incoherent): L = 10 log10(sum 10^(L_i/10)).
Required level and the 110 dBA cap come from lib.audibility [CODE 72-2022 18.4.4.1 and 18.4.1.2].
Free-field ignores room reverberation, which usually adds level. That makes the margin conservative [PARA]."""
import math
from lib import audibility as au

def spl_at(l_ref, d_ft, d_ref_ft=10.0):
    if d_ft <= 0 or d_ref_ft <= 0:
        raise ValueError("distances must be > 0")
    return l_ref - 20.0 * math.log10(d_ft / d_ref_ft)

def combine(levels):
    if not levels:
        raise ValueError("no sources")
    return 10.0 * math.log10(sum(10 ** (l / 10.0) for l in levels))

def margin(avg_ambient, lmax60, sources, mode="public"):
    """sources: list of (l_ref_dba_at_10ft, distance_ft) to the worst listener point.
    Returns dict: predicted, required, margin_db, meets (>=0 and <= cap), feasible, visual_required."""
    pred = combine([spl_at(l, d) for l, d in sources])
    c = au.check(avg_ambient, lmax60, pred, mode)
    return {"predicted": pred, "required": c["required"], "margin_db": pred - c["required"],
            "meets": c["meets"], "feasible": c["feasible"], "visual_required": c["visual_required"],
            "over_cap": pred > au.CAP_DBA}
