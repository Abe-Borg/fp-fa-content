"""EPSS fuel-hour check library (r11 R22). Synthetic training use. Not PE-approved. Where adopted; AHJ to confirm.
NFPA 110-2025 fuel screen:
- 5.5.2: the low-fuel switch marks the class fuel quantity.
- 5.5.3.1: class at or under 24 h uses a 133 percent tank factor on that quantity.
- 5.5.3.2: class over 24 h uses a 100 percent factor.
Model [PARA]: low-fuel quantity = class hours x full-load burn rate. Usable fraction of tank is a design input
(default 1.0); the maker or tank vendor sets the real unusable volume."""

def multiplier(class_h):
    if class_h <= 0:
        raise ValueError("class hours must be > 0")
    return 1.33 if class_h <= 24 else 1.00

def low_fuel_gal(class_h, burn_gph):
    if burn_gph <= 0:
        raise ValueError("burn rate must be > 0")
    return class_h * burn_gph

def min_tank_gal(class_h, burn_gph):
    return low_fuel_gal(class_h, burn_gph) * multiplier(class_h)

def fuel_hours(tank_gal, burn_gph, usable=1.0):
    if not 0 < usable <= 1:
        raise ValueError("usable fraction must be in (0, 1]")
    return tank_gal * usable / burn_gph

def check(tank_gal, class_h, burn_gph, usable=1.0):
    req = min_tank_gal(class_h, burn_gph)
    return {"min_tank_gal": req, "tank_ok": tank_gal * usable >= req,
            "hours_full_load": fuel_hours(tank_gal, burn_gph, usable), "multiplier": multiplier(class_h)}
