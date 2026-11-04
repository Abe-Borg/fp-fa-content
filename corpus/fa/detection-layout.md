# Detection layout: spot smoke, sampling, two levels

## Spot-type smoke

Support rooms (electrical, UPS, mechanical, office, raised floor) use NFPA 72 Chapter 17. Smooth-ceiling spacing is 30 ft nominal, and every ceiling point lies within 0.7 times the spacing (NFPA 72-2025 §17.7.4.2.3.1; 2019 §17.7.3.2.3.1). Sidewall detectors are within 12 in. of the ceiling (§17.7.4.2.1*). Do not place the detector in the supply airstream (§17.7.7.3.2). Where the intent is to protect a specific hazard, the detector may sit closer, in a position that can intercept the smoke (§17.7.4.1.3). Under a raised floor, mount the detector only in an orientation for which it is listed (§17.7.4.2.2*). In 2025, §17.7.3 is sensitivity. Do not cite §17.7.3 for location. The 2019 spacing numbers above are a different cite.

Area per detector follows the airflow table. Pick the smallest table row whose air changes are at or above the room. Do not interpolate. The held endpoints match in 2019, 2022, and 2025: 60 air changes per hour is 125 ft², and 7.5 air changes and below is 900 ft² (NFPA 72-2025 Table 17.7.7.3.3.2; 2022 the same table; 2019 Table 17.7.6.3.3.2). The table applies above 7.5 air changes (2025 §17.7.7.3.3.1). Above 60 air changes the table stops. See `asd-performance.md`. FM DS 5-48 Table 4 places the 900 ft² row at 6 air changes or fewer, which is stricter between 6 and 7.5.

Beams: solid joists count as beams. Compare depth to 0.1 of the ceiling height and spacing to 0.4 of the ceiling height (2025 §17.7.4.2.4.3; 2022 §17.7.4.2.4.2; 2019 §17.7.3.2.4.2). Below 0.1 of the height, use smooth spacing. At or above 0.1 of the height and at or above 0.4 of the height between beams, put a detector in each pocket.

2025-only, and practice on earlier editions: the 40 ft ceiling scope on §17.7.4.2.3.1; a girder within 4 in. of the ceiling is a beam (§17.7.4.2.4.2); a gap above the beam over 0.15 of the height permits smooth spacing (§17.7.4.2.4.3(6)).

Under a raised floor, count a separate room at smooth spacing. Those detectors are not the room detection (NFPA 72-2025 §17.7.4.5; 2022 the same section; 2019 §17.7.3.5). Where NFPA 75-2020 or 2024 §9.2.2 applies, also cover the ceiling throughout the information-technology area, the underfloor when it contains cable, the exhaust or return stream where aisle containment is used (§9.2.2(3)), and the return stream if the space above the ceiling is a return plenum. Return openings are at most 4 ft² (§9.2.2.1). NFPA 72 Chapter 17 has no containment rule. Where NFPA 76 is adopted, a power area uses the early-warning tier in §6.10.5.1, not a medium-voltage section from an older pointer. Keep detectors out of arc-flash vent paths.

## Data-hall sampling

Very early warning sampling for a data hall follows NFPA 72-2025 §17.7.4.6 and NFPA 75 §9.2.2 (2024 or 2020, as adopted). Where FM insures, FM DS 5-32 §2.4.2.2 (January 2026 reading in the pack): ports in the return air, in the equipment area, and below the raised floor (§2.4.2.2.1); return at 4 ft² per port (§2.4.2.2.3); ceiling single level 200 ft² per port (§2.4.2.2.4); two levels 400 ft² per port (§2.4.2.2.5), and two levels where trays block smoke (§2.4.2.2.6); transport time 60 seconds (§2.4.2.2.7). At or above 5 ft/s, or 60 air changes per hour, slow the ventilation on a pre-alarm (§2.4.2.1.3). The 60 air-change figure is the FM sheet. It is not in NFPA 75-2024 Chapters 4 through 13.

NFPA 76 §8.5.3.1 (2020 or 2024) applies only when that standard is adopted or elected. The stagger between high and low sampling ports is an NFPA 76 rule on that same condition. It is not an NFPA 72 default.

Map owner sampling levels to FM signals with the engineer of record: Alert is supervisory and is not the double-interlock detection leg; Action or Fire 1 is the pre-alarm the company uses as leg 1. See `di-releasing.md`.

Each sampling port is a spot detector for location and spacing (NFPA 72-2025 §17.7.4.6.1.1; 2019 §17.7.3.6.1.1). The detector signals trouble when airflow is outside the manufacturer's specified range (NFPA 72-2025 §17.7.4.6.1.2). Do not invent that range. A 0.2 percent per foot trip at the second level is not an NFPA 72 requirement. It stays assumed. In 2025, §17.7.3 is sensitivity. It does not elect the trip.

A concealed spot detector has a remote indicator at an accessible location the authority accepts (NFPA 72-2022 and 2025 §17.4.7.2). The 2019 rule covered a concealed detector more than 10 ft above the floor (§17.4.6). Cite the enforced edition. Solid joists count as beams (NFPA 72-2025 §17.7.4.2.4.1). A girder whose top is within 4 in. of the ceiling is a beam; more than 4 in. down, it is not a factor (§17.7.4.2.4.2, 2025). Those 2025 girder and gap rules are practice on earlier editions, as the beam paragraph above already says. On a Canada job, CAN/ULC-S524 spacing is NEEDS HOLD.
