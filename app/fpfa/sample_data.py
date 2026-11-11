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

# A second generic zone, for showing the workflow is not tied to DH-1's numbers or wording. It sits on the
# size-exemption boundary on purpose: the pipe alone is under the 500 gal cap and the zone total is over it.
# Every value differs from DH-1 where a difference changes an answer: cut lengths with a typed fittings
# allowance, a typed trim volume (so nothing in the volume is ASSUMED), a higher fill flow, other detection
# and release times, and no manual release station. The trim family is the same, because the kernel's truth
# table models electric/electric only. docs/known-answer-dh2.md is the expected basis and the pass criteria.
# These inputs were chosen for the test, not taken from a job, and wait for the owner's confirmation.
EXAMPLE_BASIS_2 = {
    "ahj": "Local fire marshal (sample)",
    "nfpa_13": "2025",
    "nfpa_72": "2025",
    "insurer": "FM",
    "hazard_notes": (
        "Second sample data hall. Ordinary-hazard analogue. Double-interlock preaction. "
        "Numbers are for the prototype workflow, not a constructed building."
    ),
}

EXAMPLE_DI_2 = {
    "zone_id": "DH-2",
    "system_type": "di",
    "hazard": "ordinary",
    "supervised": True,
    "density_gpm_ft2": 0.20,
    "base_area_ft2": 1500,
    "area_increase": 0.30,
    "hose_gpm": 250,
    "q_fill_gpm": 900,
    "t_detect_s": 10,
    "t_release_s": 3,
    "t_exhaust_s": 0,
    "qod": False,
    "delivery_basis": "FM",
    "medium": "nitrogen",
    "prime_held_by": "nc_solenoid",
    "failsafe_on_total_power_loss": False,
    "supervisory_psi": 15,
    "manual_station": False,
    "length_basis": "cut",
    "fittings_percent": 5,
    "trim_gal": 6.6,
    "supervisory_psig": 20,
    "fill_minutes": 30,
    "segments": [
        {"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 1500},
        {"role": "branch", "nps": "2", "schedule": "sch40", "length_ft": 403},
        {"role": "cross", "nps": "4", "schedule": "sch10", "length_ft": 300},
        {"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 70},
    ],
}

# The sample zones by the name a command or the evaluation runner gives them.
SAMPLE_ZONES = {
    "dh1": ("Sample data hall DI zone", EXAMPLE_BASIS, EXAMPLE_DI),
    "dh2": ("Second sample DI zone (size-exemption boundary)", EXAMPLE_BASIS_2, EXAMPLE_DI_2),
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
