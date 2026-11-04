# Generator and fuel-room detection

No model-code line in the held pulls requires fire detection in a generator room by itself. IFC 2024 §1203 and IBC 2024 §2702 cover power, not detection.

NFPA 37-2024 §6.3.2.2.1 allows a fuel tank of any size in the engine room only when the room has fire detection, fire suppression, and containment that keep a fire from leaving the room. Without that package, tanks outside their own room are limited to 660 gallons (§6.3.2.2) and 1,320 gallons aggregate (§6.3.2.3). The section does not name the detector type. Design practice uses heat detectors spaced under NFPA 72 §17.6.3, including the ceiling-height reductions in Table 17.6.3.5.1. Spot smoke next to a running engine is a poor default.

NFPA 37-2021 §11.3.1, where that edition is adopted, sends detection to NFPA 72. Automatic fuel stop valves required elsewhere in NFPA 37 close on detection in the engine zone (§11.3.3). Mechanical ventilation of the enclosure, where provided, shuts down on that detection. NFPA 37-2024 §11.3.4 states that duty where the 2024 edition is adopted. The 2021 section states the same shutdown. Combustion air and radiator air are not that output. Verify with the engineer of record before stopping them. Do not close the fuel valve to a life-safety generator on engine-room detection unless the engineer of record accepts that trip. The §11.3.4.1 exception is not used by default. Engine-room detection can still alarm. Where §11.3.3 requires a valve for a different reason, the engineer of record decides. Cite the edition in force.

Sprinkler density in NFPA 37-2024 §11.4.5.1, 0.3 gpm/ft² over 2,500 ft², is a fire-protection number. It is not a detector spacing.

## Generator as fire-alarm secondary power

NFPA 72 §10.6.7.3.1(2) allows an automatic generator plus 4 hours of dedicated batteries. The generator has to meet §10.6.11.3.1.1: NFPA 110 Type 10, Class 24, Level 1, with the circuit arranged under NEC Article 700, and equal survivability where pathway survivability is required. The branch circuit is dedicated (§10.6.5.1.2). `secondary-power.md` covers the Class 24 gap in the NFPA 110 table and the decision to size 24 hours when the generator does not qualify.

Emergency power is within 10 seconds. Standby power is within 60 seconds. The IFC 2024 minimum duration in §1203.1.4 and §1203.1.5 is 2 hours, which is not the fire-alarm battery duration. Voice and alarm standby follow NFPA 72 (§1203.2.4).

The fire command center, where one exists, gets generator supervision, manual start, and transfer (IBC 2021 and 2024 §911.1.6, item 15). NFPA 110-2022 Level 1 equipment gets local annunciation and a remote common audible alarm (§5.6.6), including the conditions in Table 5.6.5.4 such as low fuel in the main tank. Routing those points to the fire alarm is practice, not a held NFPA 72 requirement. Label them supervisory.

FM DS 5-23 text for the generator occupancy was not in the pull. Do not invent an FM detector type from the data-hall sheet.
