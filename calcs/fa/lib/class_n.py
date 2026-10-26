"""Class N pathway checker per NFPA 72-2025 12.3.6.
Model: a pathway serves endpoints. It has a primary path and optional redundant path.
Each path is a list of physical segment ids. Flags cover items (3), (4), (6) which topology cannot prove.
Screening tool. Verify with the engineer of record."""

def check_pathway(p):
    """p: dict(name, endpoints:int, primary:[seg], redundant:[seg] or None,
    e2e_verified:bool, loss_trouble:bool, degraded_trouble:bool). Returns list of findings."""
    f = []
    red = p.get("redundant")
    if p["endpoints"] >= 2 and not red:
        f.append("12.3.6(1): 2+ endpoints, no redundant path")
    if red:
        shared = sorted(set(p["primary"]) & set(red))
        if shared:
            f.append("12.3.6(7): shared segment(s) " + ",".join(shared))
    if not p.get("e2e_verified"):
        f.append("12.3.6(3): end-to-end verification not shown")
    if not p.get("loss_trouble"):
        f.append("12.3.6(4): loss of comms trouble not shown")
    if red and not p.get("degraded_trouble"):
        f.append("12.3.6(6): degraded redundancy trouble not shown")
    return f

def check_network(pathways):
    """Adds 12.3.6(5) screen: a segment used by two different pathways means one fault may affect another.
    This is a screen only. Fault isolation hardware can resolve it. Verify with the engineer of record."""
    out = {p["name"]: check_pathway(p) for p in pathways}
    use = {}
    for p in pathways:
        for s in set(p["primary"]) | set(p.get("redundant") or []):
            use.setdefault(s, set()).add(p["name"])
    for s, names in sorted(use.items()):
        if len(names) > 1:
            for n in sorted(names):
                out[n].append("12.3.6(5) screen: segment %s shared with %s" % (s, ",".join(sorted(names - {n}))))
    return out
