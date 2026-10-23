"""ITM scheduler. NFPA 72-2022 Table 14.4.3.2 frequencies and 14.4.4.3 sensitivity cycle.
Sensitivity: within 1 year after installation (14.4.4.3.1), then every other year (14.4.4.3.2),
unless the interval is extended to at most 5 years under 14.4.4.3.3.
Where adopted; AHJ to confirm."""
PER_YEAR={"Semiannually":2,"Semiannual":2,"Annually":1}
def visits(rows):
    """rows: (name, qty, per_year). Two visits (Jan, Jul). Returns (jan, jul, year)."""
    for r in rows:
        if r[2] not in (1,2): raise ValueError("per_year must be 1 or 2: %r"%(r,))
    jul=sum(q for _,q,f in rows if f==2); jan=sum(q for _,q,f in rows)
    return jan, jul, sum(q*f for _,q,f in rows)
def sensitivity_years(horizon, extend=False, max_gap=5, nuisance_up=()):
    if not 1<=max_gap<=5: raise ValueError("max gap is 5 years")
    out=[1]; y=1
    while True:
        y += max_gap if (extend and len(out)>=2) else 2
        if y>horizon: break
        out.append(y)
    return sorted(set(out)|{n for n in nuisance_up if 1<=n<=horizon})
