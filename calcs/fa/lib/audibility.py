"""Audibility margin library for tone notification. Screening use.
Public mode uses +15 dB over average ambient or +5 dB over the 60-second maximum, whichever is higher (NFPA 72-2022 18.4.4.1).
Private mode uses +10 dB over average ambient (NFPA 72-2025 18.4.5.1).
Cap 110 dBA at the minimum hearing distance (NFPA 72-2022 18.4.1.2).
Above 105 dBA average ambient, the screen calls for a visual appliance (NFPA 72-2019/2022 18.4.1.1).
Voice: 72 judges voice by intelligibility, not by these margins. Using tone margins for voice ADS
is [PARA] practice only; where adopted; AHJ to confirm.
"""
CAP_DBA = 110.0
VISUAL_TRIGGER_DBA = 105.0

def required_dba(avg_ambient, lmax60=None, mode="public"):
    add = {"public": 15.0, "private": 10.0}[mode]
    req = avg_ambient + add
    if lmax60 is not None:
        req = max(req, lmax60 + 5.0)
    return req

def check(avg_ambient, lmax60, design_dba, mode="public"):
    req = required_dba(avg_ambient, lmax60, mode)
    return {"required": req, "feasible": req <= CAP_DBA, "meets": design_dba >= req and design_dba <= CAP_DBA,
            "visual_required": avg_ambient > VISUAL_TRIGGER_DBA}
