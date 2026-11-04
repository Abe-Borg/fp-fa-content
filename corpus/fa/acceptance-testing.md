# Fire alarm acceptance and integrated testing

Inspection, testing, and maintenance frequencies below are NFPA 72 Chapter 14. They are not the 25-year sprinkler calendar. Insurer trip-test levers for nitrogen and valve supervision are `../fp/itm-testability.md`.

## Frequencies that move by edition

Visual inspection of supervisory signal devices and of waterflow devices is quarterly in NFPA 72-2019 Table 14.3.1 items 17(11) and 17(12), and semiannual in 2022 and 2025. Duct-detector visual inspection references §17.7.5.5 in 2019 and §17.7.6.5 in 2022 and 2025. The 2025 row is general condition semiannual and the sampling tube annual.

Sensitivity testing is at 1 year, then every other year, and may extend to 5 years after the listed conditions are met (§14.4.4.3, same schedule in 2019, 2022, and 2025). The 2019 extension basis includes a 4 percent obscuration fallback when a range is not marked (§14.4.4.3.3). 2022 and 2025 use the listed and marked range only.

Air-sampling functional tests in Table 14.4.3.2 are annual: end port and airflow. Visual inspection of filters is semiannual, and the pipe and ports are checked at acceptance (Table 14.3.1). The 2019 reference for that row is §17.7.3.6. Later editions use §17.7.4.6.

Valve-regulated lead-acid batteries: replace a cell or unit below 13.26 V. Load-test or replace at 3 years, replace at or below 80 percent, and replace before the next interval if below 85 percent. The charger setpoint in the table notes is 2.265 V per cell, plus or minus 0.015 V. Those values match across 2019, 2022, and 2025. The location inside the table moved. Semiannual temperature in 2019 is more than 18 °F above ambient. In 2022 and 2025 it is compared with the measured temperature inside the enclosure. Primary dry-cell marking in 2025 uses 60 percent of shelf life plus an installed date, and replacement at 12 months from the installed date. 2019 and 2022 mark the manufacture date and use 12 months.

There is no test row for notification power extenders. Table 14.4.3.2 items 12 and 13 are reserved in 2019, 2022, and 2025. Surge-protective devices are inspected semiannually. The 2019 name is transient suppressors.

Intelligibility testing, where the space requires it, cites §14.4.11 in 2019 and 2022 and §14.4.12 in 2025.

## Releasing test, not a discharge

NFPA 72 Table 14.4.3.2 item 18(6): verify the release solenoid at acceptance and annually. Item 17(1): the electromechanical releasing device, annually. The same items are in 2019, 2022, and 2025. The footnote points at the test plan in §14.2.10. It does not call for an agent discharge. During the test, notify occupants (§14.2.6.2), do not discharge the suppression system as an NFPA 72 requirement (§14.2.6.3), secure the valve (§14.2.6.4), confirm the releasing circuit is monitored and operates (§14.2.6.5), and restore service (§14.2.6.6). Those sentences match in 2019, 2022, and 2025. `di-releasing.md` carries the same test rules.

A cross-zone arrangement, where one is programmed, has an annual test row (Table 14.4.3.2 item 18(4) in the pulls). On an FM job the detection leg is not cross-zoned, so that row is not the operating sequence.

## Integrated systems

NFPA 4 §4.1.3 requires integrated testing of new or existing fire protection and life safety systems where the design documents, the commissioning plan, or a law requires it. The 2021, 2024, and 2027 editions match that trigger in the pulls.

The owner selects the integrated test team (§4.2.2 in the 2024 text). At a minimum the team is the integrated testing agent and the installation, testing, or maintenance personnel for each integrated system (§4.2.3).

NFPA 4-2024 says a written plan is not required for a building with limited integrated systems, and that testing is still required when the plan is not (§4.5.3.1). A hall with double-interlock preaction, elevators, smoke control, or energy storage is not a limited system. Expect a written plan.

A campus wet and double-interlock test still runs when the plan is not required. NFPA 4-2024 §4.5.1(6) requires a functional matrix of inputs and associated outputs. That item stays closed. Do not mark it unheld. Do not invent the other plan-item sentences. Waterflow alarms that building and the supervising station and starts voice in that building. It does not recall an elevator. Double-interlock release does not recall. Lobby smoke does (NFPA 72 §21.3.3.1). Detection alone does not open a double-interlock valve. Low air alone is supervisory and does not release. Detection and low air together release. Generator-room detection shuts down room ventilation and does not close fuel. Loss of a supervising-station path is trouble. An energy-storage gas row is optional and only where that room exists. On the concentration-reduction path, concentration reduction and an alarm start when the measured concentration reaches a start setpoint selected at no more than 10 percent of the lower flammable limit (NFPA 855-2023 §9.6.5.6.7(1) and (5)(b)). A clean-air or zero reading does not satisfy that start. On the exhaust-rate path the code start is when concentration exceeds 25 percent of the lower flammable limit (§9.6.5.1.5.4(1)); an earlier 10 percent start is design practice, not that code section. A detector fault is trouble; a maker delay stays assumed. Do not invent maker times. On a Canada job, CAN/ULC-S1001 is NEEDS HOLD. Do not invent those rows. Do not map NFPA 4 as Canada code.

After a change, NFPA 4-2024 §6.4.3 retests the changed functions plus 10 percent of unaffected inputs, up to 50 devices. FM DS 5-40 §2.2.7, September 2007, uses the same 100 percent of affected devices plus 10 percent, capped at 50, after a software change. Confirm that alarm sheet is still in force.

The record of completion and the 17-item documentation list are `documentation-package.md`. A 5-minute general alarm, or 15 minutes of voice, in Table 14.4.3.2 is a test duration. It is not the battery sizing input.

## Commissioning plan and 2022 notification rows

NFPA 3-2024 §5.2.3.2 requires the commissioning plan to include testing procedures (8), testing of integrated systems where applicable (9), and the frequency established for periodic integrated systems testing where applicable (11). §5.3.3 requires the updated plan to include the sequence of operation for fire protection and life safety systems (2) and an issues log (8). The sequence is wet, dry, and double-interlock only. On a Canada job, CAN/ULC-S1001 is NEEDS HOLD. Do not invent that plan.

NFPA 72-2022 Table 14.4.3.2, and not the 2025 table: item 22(2) verifies that audible information is intelligible and complies with §14.4.11. Items 22(1) and 22(2) verify notification-appliance operation annually. Item 22(3) verifies candela marking against the approved drawings, and verifies annually that each visual appliance flashes. Item 15(5) tests each initiating device circuit, notification appliance circuit, and signaling line circuit for correct indication at the control unit. Item 5(6) operates any five telephone handsets at once and checks voice quality and clarity. The 2025 notification rows in that table are NEEDS HOLD. CAN/ULC-S536 is NEEDS HOLD. The field intelligibility pass stays an owner election. Do not invent it. Alarm verification on a releasing zone is not a code claim. The physical disconnect stays §23.11.
