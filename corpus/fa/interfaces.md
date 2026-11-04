# Elevator, HVAC, signals, and power isolation

## Elevator

NFPA 72 §21.3 is Phase I recall detection. Unless §21.3.3.2 or the authority having jurisdiction says otherwise, only elevator lobby, hoistway, machine room, machinery space, control room, and control space smoke detectors, or other automatic detection §21.3.10 permits, initiate Phase I (§21.3.3.1). A waterflow switch may initiate Phase I only for a pit sprinkler on a separately valved line dedicated to the pit (§21.3.3.2). Ordinary wet waterflow and double-interlock release do not. Provide the three recall outputs and the trigger map for the enforced edition (2019, 2022, and 2025 are all held as the same duty in the skill; confirm the labels with `fa-code-edition-delta-check`). CSA B44 and NBC 3.2.6 are NEEDS HOLD. Do not map these rows as Canada code. The lobby detector is within 21 ft of the door centerline (§21.3.5.1). Section 21.4 is the shunt-trip heat detector, the shunt switch, and the supervision of that circuit. Heat detectors used for shunt trip have a lower temperature rating and a lower response-time index than the sprinklers, and they sit within 24 in. of each sprinkler. A flow or pressure switch used to shunt trip has no time delay. The elevator controller and the ASME A17.1 sequence are not this note. Sprinkler design at the elevator is not this note. Detail is in `epo-and-disconnect.md`.

## HVAC, doors, and locks

NFPA 72 Chapter 21 (2019, 2022, and 2025) covers the fire-alarm side of HVAC shutdown, dampers, duct detectors, door hold-opens, and electrically locked doors. Duct-detector supervisory is NFPA 72-2019 §21.7.4 only. The 2022 and 2025 section stays NEEDS HOLD. Detail is in `epo-and-disconnect.md`. The interface wiring allowance of 20 ft in metal raceway is NFPA 72-2025 §21.2.4.1. The 2019 and 2022 text is 3 ft unless the circuit is Class D. There is no 20 ft allowance in those editions. Coordinate IMC §606, NFPA 90A, NFPA 75, NFPA 101, and IBC §716 and §1010 for the opening rating and the lock. If fire-alarm secondary power holds egress doors locked, they unlock within 10 minutes of primary-power loss (§21.10.3). Record relay distance, signal class, and whether the lock unlocks on alarm, on loss of power, or both. Do not invent a cooling-continuation time after the data-hall equipment is isolated. If a minute count is required and no note holds it, mark it `[V]`.

## Supervising station

Class each off-site signal as alarm, supervisory, or trouble. For a lithium-ion energy-storage room, IFC 2024 §1207.5.4 and §1207.6.1.2.3 and NFPA 855-2023 §4.8.4 and §9.6.5.6.7 decide which gas and fire signals leave the building. NFPA 72 Chapter 26 is the supervising-station chapter (2022 pin in the skill). A gas trouble is not a gas alarm.

## Power isolation

NEC Article 645 applies only when the room is actually an information-technology equipment room under that article. Do not assume it from the word "data hall."

On an FM job, FM DS 5-32 Figure D.1 is the sequence reference: automatic versus manual isolation, a test mode, and the order relative to wet, dry, or double-interlock release. The figure's order takes critical loads off before water. Shunt-trip the critical-load feeds, shut the UPS down including its battery, then the affected distribution, and inhibit re-energizing into the isolated zone. Interlock HVAC after that electrical isolation. Do not kill cooling while the load is still energized. Egress lighting stays on. The preferred disconnect both de-energizes the equipment and interlocks the HVAC. There is no held minute count for how long cooling continues after that point. Mark the hold time `[V]`. A test mode witnessed during integrated-system testing has to appear in the cause-and-effect matrix. A missing time is ASSUMED and flagged. It is not a code minute.

Single-interlock as the basis of design stops this note. Foam and water mist are out of scope.
