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

NFPA 4-2024 says a written plan is not required for a building with limited integrated systems, and that testing is still required when the plan is not. A hall with double-interlock preaction, elevators, smoke control, or energy storage is not a limited system. Expect a written plan.

After a change, NFPA 4-2024 §6.4.3 retests the changed functions plus 10 percent of unaffected inputs, up to 50 devices. FM DS 5-40 §2.2.7, September 2007, uses the same 100 percent of affected devices plus 10 percent, capped at 50, after a software change. Confirm that alarm sheet is still in force.

The record of completion and the 17-item documentation list are `documentation-package.md`. A 5-minute general alarm, or 15 minutes of voice, in Table 14.4.3.2 is a test duration. It is not the battery sizing input.
