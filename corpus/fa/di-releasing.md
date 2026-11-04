# Double-interlock releasing cause and effect

Write the fire-alarm sequence for a double-interlock zone on a listed releasing panel. NFPA 72-2025 §23.11 is the releasing chapter to check against the enforced edition (`fa-code-edition-delta-check`). The control unit is listed for releasing service, and the releasing devices are listed for use with it (§23.11.1 and §23.11.2). The disconnect is a physical switch, not a software function (§23.11.5.2, same duty in 2019, 2022, and 2025). Operating that disconnect or a disable function is a supervisory signal at the releasing unit (§23.11.5.1). This note does not set trim pressures or delivery time.

The cause-and-effect matrix is the sequence of operation required on the shop drawings (NFPA 72 §7.4.9) and reissued with the record drawings to match the program actually loaded (NFPA 72 §7.5.5.2). The same section numbers are used in 2019, 2022, and 2025.

## Both legs

Water releases only when the detection leg and the low-air leg are both true.

On an FM job, FM DS 5-32 §2.4.1.1 is the double-interlock flag to the owner and the insurer, and §2.4.3.2.1.3 is the no-cross-zone flag. The detection leg is an alarm-level signal (owner Action, or Fire 1, as the engineer of record confirms). NFPA 76 Alert is supervisory: no notification appliances, and it is never leg 1. Fire 2 is not the detection leg. Do not require a cross-zone to trip the valve on an FM job. That insurer rule conflicts with a company habit of cross-zoning the first knock. The conflict is with the habit, not with double-interlock itself. Off an FM job, a cross-zoned first knock may still be the company default; two detectors then follow NFPA 72 §23.8.5.4.4 (2019, 2022, and 2025).

## Test, not discharge

NFPA 72 Table 14.4.3.2 item 18(6): verify the release solenoid at the initial acceptance test and annually. Item 17(1): the electromechanical releasing device, annually. Same items in 2019, 2022, and 2025.

During the test, notify occupants (§14.2.6.2), do not discharge the suppression system as an NFPA 72 requirement (§14.2.6.3), secure the valve (disconnect solenoids or close valves; fire protection coordinates the preaction valve) (§14.2.6.4), confirm the releasing circuit is monitored and operates on alarm (§14.2.6.5), and return the system to service (§14.2.6.6).

Clean-agent discharge and foam discharge are out of scope. Do not add those columns. Single-interlock programs are comparison-only.
