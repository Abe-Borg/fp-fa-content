"""Spot smoke spacing vs air movement. NFPA 72-2022 and 2025 Table 17.7.7.3.3.2 (same numeric rows).
NFPA 72-2022 17.7.7.3.3.1 reduces spacing when airflow is faster than 8 minutes per air change.
Between rows: round minutes DOWN to the tighter row (screening choice; verify with the engineer of record).
Under 1 minute per change: no table value, raise. Not for under-floor or above-ceiling spaces."""
import math
TABLE=[(1,60,125),(2,30,250),(3,20,375),(4,15,500),(5,12,625),(6,10,750),(7,8.6,875),(8,7.5,900),(9,6.7,900),(10,6,900)]
def minutes_per_change(volume_ft3, cfm):
    if cfm<=0 or volume_ft3<=0: raise ValueError("volume and cfm must be > 0")
    return volume_ft3/cfm
def spacing_ft2(mpc):
    if mpc<1: raise ValueError("under 1 min per air change: no held table value, PE review")
    return max((r for r in TABLE if r[0]<=mpc), key=lambda r:r[0])[2]
def detectors(area_ft2, volume_ft3, cfm):
    sp=spacing_ft2(minutes_per_change(volume_ft3,cfm)); return sp, math.ceil(area_ft2/sp)
