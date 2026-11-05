# Air-sampling performance floors

Layout areas already in `detection-layout.md` are not repeated here. This note is transport time, sensitivity, and when NFPA 76 applies.

## Transport

NFPA 72 maximum air-sample transport, from the farthest port to the detector, is 120 seconds. The cite is §17.7.3.6.2.1 in 2019 and §17.7.4.6.2.1 in 2022 and 2025. The words match. Sixty seconds is not an NFPA 72 limit.

Each port is a spot detector for location and spacing (§17.7.4.6.1.1 in 2025; §17.7.3.6.1.1 in 2019). Airflow outside the manufacturer's specified range is a trouble signal (NFPA 72-2025 §17.7.4.6.1.2). The annex production-sensitivity benchmark is not the selection basis. A 0.2 percent per foot trip at the second detection level is assumed. It is not an NFPA 72 code value. NFPA 76 alert and alarm numbers below apply only when that standard is adopted or elected.

NFPA 76-2024 §8.5.3.1.2.6 limits very-early-warning transport to 60 seconds from the most remote port, excluding test ports, to the detector. The 2020 edition uses the same number. Early-warning transport is 90 seconds (§8.5.3.2.1.4 in 2024). The 2020 early-warning sentence was not compared. When FM DS 5-32 or NFPA 76 governs, 60 seconds is the design limit. The 120 second code floor is the comparison.

A UL open-area listing can cap the design-tool transport at 40 to 45 seconds, depending on air speed, which is tighter than both clocks. That cap is the listing. It is not a code amendment. A ULC open-area maximum of 120 seconds on the same family is a different mark. Use the mark on the submitted model.

## Sensitivity and area, when NFPA 76 applies

Very early warning, NFPA 76-2024 §8.5.3.1, same values in 2020:

- One level: 200 ft² per port (§8.5.3.1.2.1).
- Two levels: each level 400 ft² or less per port, staggered so the offset between levels is at most 200 ft² (§8.5.3.1.2.2).
- Return openings: 4 ft² per port.
- Alert 0.2 percent per foot, alarm 1.0 percent per foot.
- Alert is supervisory (§8.4.2.2.4(1) in the 2020 pull). No building notification, and it is not the double-interlock detection leg.

Early warning: 400 ft² per port, alarm at 1.5 percent per foot, transport 90 seconds (§8.5.3.2.1).

NFPA 76 requires very early warning in signal-processing and main-distribution areas of a facility with more than 2,500 ft² of signal-processing area (§6.8.6.1 and §6.11.6.1). At or below 2,500 ft² the tier is early warning. One very-early-warning level is at most 200 ft² per port, and transport from the farthest port is at most 60 seconds. Power areas get early warning under §6.10.5.1, same in 2020 and 2024. Cable entrance areas get early warning (§6.9.5.1.1). Rooms with stationary battery storage systems get early warning (§6.10.8.2.8.1). A raised floor with combustibles below, and without common airflow above and below, gets early warning below the floor (§6.8.6.1.1). Early warning is at most 400 ft² per port and 90 seconds of transport. Whether those underfloor combustibles are present is a project input. Whether a meet-me room is a telecommunications facility is an owner or authority call. Verify with the engineer of record. Older pointers that cite §6.1.3 or §8.8 for a power room are the wrong sections. §6.1.3 is area sizing. Chapter 8.8 in that pull is cabling.

Do not apply NFPA 76 as the code floor of a hyperscale hall. Apply it when the room is telecommunications or when the owner, the insurer, or the authority adopts the performance.

NFPA 75-2024 Annex A.9.2.1 prefers air-sampling transport under 90 seconds and ports in the airflow path. That annex sentence is absent in the 2020 edition. It is annex, not a requirement. The code containment locations are §9.2.2, in `detection-layout.md`.

## Above the airflow table

NFPA 72-2025 Table 17.7.7.3.3.2, and the same values in 2022 and in 2019 Table 17.7.6.3.3.2, ends at 60 air changes and 125 ft². The table applies above 7.5 air changes (§17.7.7.3.3.1). Air sampling and projected beam in that high-air section follow the manufacturer's instructions (2025 §17.7.7.3.3.3).

Halls measured near 78 to 265 air changes are past the last row. Do not interpolate, and do not treat 125 ft² as a conservative code value above 60 air changes. That condition is a performance layout. NFPA 72 Annex B.4.5, in the 2019, 2022, and 2025 readings, states there is no quantitative method for smoke dilution or for airflow effects on location. A listed pipe model and a witnessed test are the evidence. Holding 125 ft² above 60 air changes is design practice only, and it is not a substitute for that evidence.

FM DS 5-48 Table 4 places 900 ft² at 6 air changes or fewer, which is stricter than the NFPA row between 6 and 7.5. The FM sheet also stops at 125 ft² and 60 air changes. Do not invent a denser FM row.

Set the chamber threshold at or below the per-port target divided by the number of openings. Fifty openings at a 0.2 percent-per-foot alert need 0.004 percent per foot at the chamber. Twenty-five openings need 0.008 percent per foot. An alarm leg at 1.0 percent per foot on those 25 openings needs 0.04 percent per foot. A glossary line that prints an alert below 0.02 percent per foot is an order of magnitude under the 0.2 percent design tier. Design to the tier. Treat 0.02 as a figure to confirm, not as the setpoint.

Commissioning balance, hole caps, and the heated-wire test are `../fp/asd-commissioning.md` and `../fp/vewfd-acceptance.md`.
