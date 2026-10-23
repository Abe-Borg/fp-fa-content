"""Class A, N, X pathway separation check. NFPA 72 12.3.8 and 12.3.8.1 (2019, 2022, 2025).
Basis [CODE NFPA 72-2022 12.3.8.1, held 72-19]:
 (1) shared run "not to exceed 10 ft (3.0 m)" at an enclosure entry or exit
 (2) "Single drops installed in the raceway to individual devices or appliances"
 (3) single room "not exceeding 1000 ft2 (93 m2)", drop with no emergency control function devices
 (2025 item (3) reads "emergency control function interface devices"; same test.)
Annex A.12.3.8 advisory spacing: 12 in. vertical, 48 in. horizontal [PARA annex, not mandatory].
Synthetic training tool. RESOLVED (training value, strictest defensible; not PE-approved): a shared
segment must fit one item fully; items are not added together.
"""
ENTRY_MAX_FT = 10.0
ROOM_MAX_FT2 = 1000.0
ANNEX_SEP_IN = {"vertical": 12, "horizontal": 48}

def shared_ok(shared_ft=0.0, at_enclosure=False, single_drop=False, room_ft2=None, has_ecf=False):
    """Return (ok, reason) for one segment where outgoing and return share a raceway."""
    if shared_ft <= 0:
        return True, "not shared"
    if at_enclosure and shared_ft <= ENTRY_MAX_FT:
        return True, "12.3.8.1(1) within 10 ft of enclosure"
    if single_drop:
        return True, "12.3.8.1(2) single drop"
    if room_ft2 is not None and room_ft2 <= ROOM_MAX_FT2 and not has_ecf:
        return True, "12.3.8.1(3) single room drop, no ECF"
    if room_ft2 is not None and has_ecf:
        return False, "12.3.8.1(3) excludes ECF devices"
    return False, "shared run outside 12.3.8.1"

def annex_sep_ok(sep_in, orientation):
    """Advisory only [PARA A.12.3.8]."""
    return sep_in >= ANNEX_SEP_IN[orientation]
