"""ASD transport time screening. Plug-flow estimate only; listed maker software governs.
Limit: 120 s (NFPA 72-2025 17.7.4.6.2.1; where adopted; AHJ to confirm).
Early warning target under 60 s is maker practice for very-early warning, not the 120 s code ceiling.
Formula [PARA physics, not code text]: v = Q / A, A = pi d^2 / 4, t = L / v. One pipe, constant flow (end-cap flow is the worst case
because flow drops as holes take air; using the end-cap flow gives the longest time, so this is the conservative screen)."""
import math
LIMITS = {"code": 120.0, "early_warning": 60.0}

def area_m2(id_mm): return math.pi * (id_mm / 1000.0) ** 2 / 4.0
def velocity_ms(flow_lpm, id_mm): return (flow_lpm / 1000.0 / 60.0) / area_m2(id_mm)
def transport_s(length_m, id_mm, flow_lpm):
    if length_m < 0 or id_mm <= 0 or flow_lpm <= 0: raise ValueError("bad input")
    return length_m / velocity_ms(flow_lpm, id_mm)
def max_len_m(limit_s, id_mm, flow_lpm): return limit_s * velocity_ms(flow_lpm, id_mm)
def check(length_m, id_mm, flow_lpm, target="early_warning"):
    t = transport_s(length_m, id_mm, flow_lpm)
    return {"t_s": t, "limit_s": LIMITS[target], "pass": t <= LIMITS[target], "code_pass": t <= LIMITS["code"]}
