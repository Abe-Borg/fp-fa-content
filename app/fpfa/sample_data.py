"""Generic sample inputs. Not a real job."""

EXAMPLE_BASIS = {
    "ahj": "Local fire marshal (sample)",
    "nfpa_13": "2025",
    "nfpa_72": "2025",
    "insurer": "FM",
    "hazard_notes": (
        "Sample data hall. Ordinary-hazard analogue. Double-interlock preaction. "
        "Numbers are for the prototype workflow, not a constructed building."
    ),
}

EXAMPLE_DI = {
    "zone_id": "DH-1",
    "system_type": "di",
    "hazard": "ordinary",
    "supervised": True,
    "density_gpm_ft2": 0.20,
    "base_area_ft2": 1500,
    "area_increase": 0.30,
    "hose_gpm": 250,
    "q_fill_gpm": 600,
    "t_detect_s": 8,
    "t_release_s": 2,
    "t_exhaust_s": 0,
    "qod": False,
    "delivery_basis": "FM",
    "medium": "nitrogen",
    "prime_held_by": "nc_solenoid",
    "failsafe_on_total_power_loss": False,
    "supervisory_psi": 15,
    "manual_station": True,
    "length_basis": "center_to_center",
    "fittings_percent": None,
    "trim_gal": None,
    "supervisory_psig": 40,
    "fill_minutes": 30,
    "segments": [
        {"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 900},
        {"role": "branch", "nps": "2", "schedule": "sch40", "length_ft": 220},
        {"role": "cross", "nps": "4", "schedule": "sch10", "length_ft": 160},
        {"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 48},
    ],
}

# Generic Li-ion off-gas sample for the explosion-control starter.
# Component LFL values are inputs. The mixture LFL is calculated by lfl.py.
# Percents and section cites stay in the skill starter block.
EXAMPLE_BESS_BASIS = {
    "ahj": "Local fire marshal (sample)",
    "nfpa_13": "2025",
    "nfpa_72": "2025",
    "insurer": "FM",
    "hazard_notes": (
        "Sample Li-ion BESS room. Explosion-control starter. "
        "Numbers are for the prototype workflow, not a constructed building."
    ),
}

EXAMPLE_BESS = {
    "room_id": "BESS-1",
    "composition_assumed": True,
    "composition_why": "generic sample mix, not a cell test report",
    "mix": {
        "H2": 58.0,
        "CO": 9.0,
        "CO2": 22.0,
        "CH4": 5.5,
        "C2H4": 2.5,
        "C2H6": 1.2,
        "C3H6": 0.6,
        "EMC": 0.9,
        "DMC": 0.3,
    },
    "lfl": {
        "H2": 4.0,
        "CO": 10.9,
        "CO2": None,
        "CH4": 4.4,
        "C2H4": 2.4,
        "C2H6": 2.4,
        "C3H6": 1.8,
        "EMC": 2.0,
        "DMC": 3.1,
    },
}
