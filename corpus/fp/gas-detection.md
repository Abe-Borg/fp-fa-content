# Gas and vapor detection

FM DS 5-49 (October 2018) sets power, annunciation, placement, and calibration. It does not set the trip percentage. A later file date is a rebuild, not a new edition.

Provide at least two independent supplies, transfer within 10 seconds with no signal loss, and at least 24 hours of standby with a battery calculation (§2.2.2). Annunciate at the detector and at an attended location outside the process area. Reset manually after the concentration is acceptable (§2.3.1.1 and §2.3.1.2). Power loss and loss of sampling airflow are trouble signals, distinct from a gas alarm (§2.3.1.4).

Place the detector below the leak when the specific gravity is above 1, and above it when the specific gravity is below 1, then adjust for process temperature and pressure (§3.1). Calibrate at the shorter of the manufacturer interval and the occupancy-sheet interval (§2.4.3.1).

Trip percentages come from the occupancy sheet, not from DS 5-49:

- Chemical-plant fuel gas: alarm at 25 percent of the lower explosive limit, shutoff at 50 percent (FM DS 7-14 §2.4.12.1.1).
- Gas-turbine fuel gas: trip below 25 percent, and do not raise the setpoint above 25 percent in a highly ventilated enclosure (FM DS 7-79 §2.4.1.1 and §3.3.1.1).
- Hydrogen equipment rooms without gas cabinets: 25 percent of the lower explosive limit, then 2.5 cfm/ft² and a safety shutoff (FM DS 7-91).
- Lithium-ion energy storage: often 10 percent of the lower explosive limit under FM DS 5-33, and 10 percent on the NFPA 855 explosion-control path. Do not relax that pin to the 25 percent process figure (`../fa/ess-room-detection.md`).

Methane at 5 percent by volume means 2.5 percent by volume is 50 percent of that limit. Those are examples in DS 5-49 §C.1.2. They are not trip setpoints.

A draft of NFPA 72-2025 §17.11 covers acoustic leak detection and warns that a spot ultrasonic detector can miss a liquid-phase release. Verify the final text. Acoustic leak detection is not a white-space smoke initiator.

Hot work stops above 1 percent of the lower explosive limit (FM DS 10-3 §2.5.2.2.5). That is a work permit limit, not a room-detection setpoint.
