"""Battery sizing library. Screening use. Not for construction.

Edition factors (NFPA 72 10.6.7; confirm the adopted edition):
- 2019: 20 percent margin, factor 1.20 (10.6.7.2.1.1).
- 2022 and 2025: aging factor 1.25 (10.6.7.2.14).
- Durations: 24 h quiescent then 5 min alarm [CODE 2019 10.6.7.2.1; 2022/2025 10.6.7.2.1 and 10.6.7.2.2]. EVACS 15 min at max load [CODE 2019 10.6.7.2.1.2; 2025 10.6.7.2.4]. With a generator, 4 h batteries [CODE 10.6.7.3.1(2), all three].
- Apply ONE factor only. Do not stack 1.25 on a maker aging factor [PRACTICE].
- Where adopted; AHJ to confirm the edition. Battery pick is next standard size up [PRACTICE].
Formula: Ah_base = I_standby x H_standby + I_alarm x (min_alarm / 60). Ah_req = Ah_base x factor.
"""

EDITION_FACTOR = {2019: 1.20, 2022: 1.25, 2025: 1.25}
STD_SIZES_AH = (7, 12, 18, 26, 33, 40, 55, 65, 100)  # [PRACTICE] common VRLA sizes, EXAMPLE


def factor(edition):
    if edition not in EDITION_FACTOR:
        raise ValueError("edition must be 2019, 2022 or 2025")
    return EDITION_FACTOR[edition]


def alarm_minutes(evacs=False):
    return 15.0 if evacs else 5.0


def standby_hours(generator_backed=False):
    return 4.0 if generator_backed else 24.0


def ah_required(i_standby_a, i_alarm_a, edition, evacs=False, generator_backed=False):
    if i_standby_a < 0 or i_alarm_a < 0:
        raise ValueError("currents must be >= 0")
    base = i_standby_a * standby_hours(generator_backed) + i_alarm_a * alarm_minutes(evacs) / 60.0
    return {"edition": edition, "base_ah": base, "factor": factor(edition),
            "req_ah": base * factor(edition)}


def pick_battery(req_ah, sizes=STD_SIZES_AH):
    for s in sizes:
        if s >= req_ah:
            return s
    return None


def margin_pct(req_ah, picked_ah):
    return (picked_ah / req_ah - 1.0) * 100.0


# Charger caps below are listing limits used by the unit tests, not a catalog.
# The 100 Ah top of STD_SIZES_AH is a list max, not a listing cap.
# notifier_amps24: 200 Ah. simplex_es_ps: 110 Ah.
MAKER_CHARGER_MAX_AH = {"notifier_amps24": 200, "simplex_es_ps": 110}


def charger_ok(req_ah, maker_key):
    """True if the required Ah is within the named maker charger listing."""
    if maker_key not in MAKER_CHARGER_MAX_AH:
        raise ValueError("no listing held for %s; result is PARTIAL, do not invent a cap" % maker_key)
    return req_ah <= MAKER_CHARGER_MAX_AH[maker_key]


def split_supplies(i_standby_a, i_alarm_a, edition, cap_ah, evacs=False):
    """Ruling 5 helper: fewest equal listed supplies so each req_ah <= cap_ah, 24 h battery-only."""
    n = 1
    while True:
        r = ah_required(i_standby_a / n, i_alarm_a / n, edition, evacs)
        if r["req_ah"] <= cap_ah:
            return n, r
        n += 1
