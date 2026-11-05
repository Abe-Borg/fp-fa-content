# Audible, visible, and voice notification

Public mode, NFPA 72-2022 and 2025 §18.4.4.1: at least 15 dB above average ambient, or 5 dB above a maximum that lasts 60 seconds or more, whichever is greater. Measure at 5 ft above the floor. The total, ambient plus appliances, does not exceed 110 dBA at the minimum hearing distance (§18.4.1.2). Those two sections match in 2019.

Ambient above 105 dBA requires visible appliances (§18.4.1.1 in 2022 and 2025). It does not waive the audible appliances. A visual-only design at 105 dBA is not the rule.

Reduced or eliminated audible signaling needs authority approval, and visible signaling per §18.5 still applies (§18.4.4.2, same in 2019, 2022, and 2025).

## Visible

Room spacing uses the wall table and the ceiling table. 2022 and 2025: Tables 18.5.5.7.1(a) and (b). 2019: Tables 18.5.5.5.1(a) and (b). This note does not reprint the candela grids. Use the enforced table.

Synchronization in a room, 2022 and 2025 §18.5.5.7.2 (2019 §18.5.5.5.2): one appliance; or two groups in the same room or in adjacent fields of view that flash together; or more than two appliances or groups that flash in sync.

Corridors, §18.5.5.8 in 2022 and 2025: at least 15 cd, within 15 ft of each end, 100 ft maximum spacing, and synchronization when more than two appliances are in view. A corridor wider than 20 ft uses the room tables. There is no separate corridor candela table. 2019 cites are §18.5.5.6.3, §18.5.5.6.5, and §18.5.5.6.7.

An illumination alternative of 0.0375 lm/ft² at every point may replace table spacing (NFPA 72-2022 and 2025 §18.5.5.9).

Use the manufacturer's current at the candela and at the listed minimum voltage. Count synchronization-module loss in the voltage drop (`nac-and-wire.md`).

## Restricted audible mode

NFPA 72-2025 §18.4.8 is restricted audible mode operation, where a risk analysis, the authority, or another code requires it. Mark the areas. Use it only where trained, awake, mobile staff are present. Audible appliances in the zone follow the synchronization rule, and every visible appliance in the zone synchronizes per §18.5.5.7.2. Sections 18.4.6.3 and 18.4.5 also apply.

2019 and 2022 have no restricted-audible section in Chapters 3, 18, or 24. On those editions the mode is an owner or authority election, not a code chapter.

## Voice and intelligibility

The designer names each acoustically distinguishable space and marks whether intelligibility is required (NFPA 72-2025 §18.4.12.2 and the definition at §3.3.6; 2019 and 2022 §18.4.11). Quantitative measurement is not required (§18.4.12.5). The design designates those spaces in occupiable areas as Chapter 18 requires (§24.4.2.2.2*, 2022 and 2025). Intelligibility is not required in every space unless another law, code, standard, or another part of NFPA 72 requires it (NFPA 72-2025 §18.4.12.3). A data hall is often marked as not requiring intelligibility, with tone plus visible appliances. Marking a space that way does not remove audibility or visible appliances. Document the design sound level for each coverage area for acceptance testing (§18.4.1.5.6). Relays, circuits, or interfaces that stop or reduce ambient noise meet Chapters 10, 12, 21, and 23 (§18.4.4.5.3*). The field pass value is an owner setting. Do not invent it.

A 2010-cycle reading of Annex D uses 0.45 STI at 90 percent of the measurement points and an average of 0.50 STI. Confirm Annex D in the enforced edition before those numbers are a pass criterion. Quantitative STI has been permitted since the 2013 cycle. It is not mandated. Private-mode audibility is a lower margin than public mode. Confirm the section before using 10 dB. Do not elect private mode in a hall.

Speaker circuits: 25 V or 70.7 V. The 1.0 dB electrical-loss limit is NFPA 72-2025 §18.3.7.2.1. On 2019 and 2022 that limit is design practice (`nac-and-wire.md`). A tighter loss target is a choice, not a second code value. When primary power is available, failure of an audio amplifier is a trouble signal (NFPA 72-2025 §10.19.1.1, same duty in 2019 and 2022). On secondary power, amplifier monitoring is required only while an alarm is present (§10.6.7.1.1 Exception).

Voice is not required in a typical single-story hall by the occupancy list that drives emergency voice. If the owner adds voice, Chapter 18 still applies. Survivability of that voice path is `pathway-survivability.md`.

Where the system has a microphone for live voice, post instructions for using it (NFPA 72-2022 and 2025 §24.3.2). The two editions match. The wording of the card is practice.

Public mode stays 15 dB above average ambient. Do not use a 10 dB rule for that target. A teaching screen at 78 dBA average needs 93 dBA. A 1 W tap, from an assumed 94 dB at 1 m on a 2 W datasheet, meets 93 dBA only to about 0.79 m. That spacing is not buildable. Check the tap against the ambient before electing voice. A gallery at a high ambient is tone plus visual. Do not copy the teaching distance onto a live zone. The field intelligibility pass stays an owner election.

FM does not set appliance spacing. It does require the alarm, including pre-alarm where the sheet says so, at a constantly attended location.
