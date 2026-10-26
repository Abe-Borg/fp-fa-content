"""Shop-default sprinkler pipe inside diameters.

IDs are outside diameter minus twice the wall, using ASME B36.10M dimensions
also used for ASTM A795 / A135 schedule 10 and schedule 40.

NFPA 13-2025 Table A.8.2.4 matches the 1 through 8 inch rows within about
0.001 gal/ft. 10 inch schedule 40 and both 12 inch rows are not in that annex
table; they are marked approximate. A manufacturer data sheet governs when
the project has one.

Shop default when the schedule cell is blank: branch lines, drops, and any
pipe under 2 inch are schedule 40. Mains and cross mains 2 inch and larger
are schedule 10. A 2 inch branch stays schedule 40.
"""

from __future__ import annotations

APPROXIMATE = {("10", "sch40"), ("12", "sch10"), ("12", "sch40")}

# nps string -> schedule -> inside diameter, inches
IDS: dict[str, dict[str, float]] = {
    "1": {"sch10": 1.097, "sch40": 1.049},
    "1.25": {"sch10": 1.442, "sch40": 1.380},
    "1.5": {"sch10": 1.682, "sch40": 1.610},
    "2": {"sch10": 2.157, "sch40": 2.067},
    "2.5": {"sch10": 2.635, "sch40": 2.469},
    "3": {"sch10": 3.260, "sch40": 3.068},
    "3.5": {"sch10": 3.760, "sch40": 3.548},
    "4": {"sch10": 4.260, "sch40": 4.026},
    "5": {"sch10": 5.295, "sch40": 5.047},
    "6": {"sch10": 6.357, "sch40": 6.065},
    "8": {"sch10": 8.249, "sch40": 7.981},
    "10": {"sch10": 10.374, "sch40": 10.020},
    "12": {"sch10": 12.390, "sch40": 11.938},
}


def nps_key(nps) -> str:
    x = float(nps)
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    text = f"{x:.2f}".rstrip("0").rstrip(".")
    return text


def schedule_key(schedule: str) -> str:
    s = str(schedule).strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    s = s.replace("schedule", "sch")
    if s in ("10", "40"):
        s = "sch" + s
    if s not in ("sch10", "sch40"):
        raise ValueError("schedule must be sch10 or sch40")
    return s


def default_schedule(nps, role: str | None) -> tuple[str, bool]:
    """Return (schedule, assumed). Branch, drop, sprig, or under 2 inch -> sch40."""
    role_l = (role or "").strip().lower()
    if role_l in ("branch", "drop", "sprig") or float(nps) < 2:
        return "sch40", True
    return "sch10", True


def resolve(nps, schedule: str | None = None, role: str | None = None) -> dict:
    key = nps_key(nps)
    if key not in IDS:
        raise ValueError(f"no shop ID for NPS {nps}; enter a data-sheet inside diameter")
    assumed = False
    if schedule is None or str(schedule).strip() == "":
        schedule, assumed = default_schedule(key, role)
    sch = schedule_key(schedule)
    d = IDS[key][sch]
    flags = []
    if assumed:
        flags.append(f"ASSUMED schedule {sch} for {key} in. {role or 'pipe'} (shop default)")
    if (key, sch) in APPROXIMATE:
        flags.append(
            f"{key} in. {sch} ID {d} is approximate and is not in NFPA 13-2025 Table A.8.2.4; "
            "use the pipe data sheet"
        )
    return {
        "nps": key,
        "schedule": sch,
        "role": role,
        "d_in": d,
        "schedule_assumed": assumed,
        "approximate": (key, sch) in APPROXIMATE,
        "flags": flags,
        "id_source": "shop table (data sheet governs)" if not assumed else "shop default",
    }
