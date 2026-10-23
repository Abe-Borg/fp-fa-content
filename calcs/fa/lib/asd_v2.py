"""ASD transport time v2: multi-branch pipe network, segment by segment plug flow.
Limits reuse lib.asd (120 s code limit; 60 s early warning is maker practice).
Model [PARA physics, not code text]: equal flow per hole. Segment flow = holes downstream x flow per hole.
t to a hole = sum(L_seg / v_seg) along its path. Listed maker software governs. Screening tool. Verify with the engineer of record."""
import math
from lib import asd
LIMITS = asd.LIMITS

def branch(name, id_mm, lead_m, holes, spacing_m):
    """Straight branch: lead pipe from the tee, then `holes` holes at `spacing_m`, last hole at end cap."""
    return dict(name=name, id_mm=id_mm, lead_m=lead_m, holes=holes, spacing_m=spacing_m)

def branch_time(b, q_hole_lpm):
    """Time from the farthest hole of branch b to its tee. Flow drops after each hole."""
    t = asd.transport_s(b["lead_m"], b["id_mm"], b["holes"] * q_hole_lpm) if b["lead_m"] > 0 else 0.0
    for k in range(b["holes"] - 1):           # segment between hole k and k+1 carries holes-(k+1) holes of flow
        t += asd.transport_s(b["spacing_m"], b["id_mm"], (b["holes"] - k - 1) * q_hole_lpm)
    return t

def network(header_m, header_id_mm, branches, total_lpm):
    """Header from detector to tee carries total flow. Returns dict branch -> (t_s, pass_ew, pass_code)."""
    n = sum(b["holes"] for b in branches); q = total_lpm / n
    th = asd.transport_s(header_m, header_id_mm, total_lpm) if header_m > 0 else 0.0
    out = {}
    for b in branches:
        t = th + branch_time(b, q)
        out[b["name"]] = (t, t <= LIMITS["early_warning"], t <= LIMITS["code"])
    return out

def v1_screen(header_m, b, endcap_lpm):
    """Old v1 screen: whole path at end-cap flow (one hole). Conservative upper bound."""
    L = header_m + b["lead_m"] + b["spacing_m"] * (b["holes"] - 1)
    return asd.transport_s(L, b["id_mm"], endcap_lpm)

def port_times(header_m, header_id_mm, branches, total_lpm):
    """r11: transport time from EVERY port to the detector. Returns {branch: [t_port1 (nearest), ..., t_far]}.
    Port k (1-based from tee) path: header + lead + (k-1) spacings; segment j carries holes-j holes of flow."""
    n = sum(b["holes"] for b in branches); q = total_lpm / n
    th = asd.transport_s(header_m, header_id_mm, total_lpm) if header_m > 0 else 0.0
    out = {}
    for b in branches:
        t = th + (asd.transport_s(b["lead_m"], b["id_mm"], b["holes"] * q) if b["lead_m"] > 0 else 0.0)
        ts = [t]
        for j in range(1, b["holes"]):
            t += asd.transport_s(b["spacing_m"], b["id_mm"], (b["holes"] - j) * q); ts.append(t)
        out[b["name"]] = ts
    return out
