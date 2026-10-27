# Air maintenance device, relief, and the 5 psi margin

Use this after dry pipe or double-interlock is elected. Provide a dedicated listed air-maintenance device and a check or backflow device on every such system (NFPA 13-2025 §8.2.8.1; NFPA 13-2019 and 2022 §8.2.6.6.3.1). Do not put a controller air-maintenance device and a second air-maintenance device ahead of the valve on the same system.

Set the relief valve at least 10 psi above system air pressure. A published trim sheet that sets relief only 5 psi above the air setting fails that minimum. Raise the relief. The section number for the 10 psi relief was not pinned in the source note. Confirm it in the adopted NFPA 13 before the submittal cites it.

Minimum supervisory pressure for the preaction system remains 7 psi (NFPA 13-2025 and 2022 §8.3.2.5.2). That minimum is not the setpoint (`preaction-trim-and-sequence.md`).

Design practice keeps the low-air signal at least 5 psi above the trip pressure, and the high-air signal at least 5 psi above normal supervisory pressure, read from NFPA 13-2025 §8.2.6.4 and §8.2.6.5. Confirm those paragraphs in the adopted edition before sealing. A 2019 job paired with NFPA 72-2019 used a 10 psi band on dry pipe. That band is a different rule (`../fa/preaction-supervision.md`). FM DS 2-81 §3.1.6.1 discusses supervisory air about 20 psi above trip and never above system water pressure. Where that sheet is in force, print it next to the 5 psi code floor and keep the more stringent setting the valve listing allows.

An accelerator has fixed steps. It may not be able to meet a 5 psi high-air separation and the generator's turn-on window at the same time. If the opened sheet cannot, the election fails. Do not average the two bands. Do not copy a prior hall's pressure list. Pick the sheet, show the stack, and verify it with the engineer of record.

A compressor of at least 5.5 ft³/min, or one that feeds more than one system, needs an air receiver and an air-maintenance device (NFPA 13-2019 §8.2.6.6.2; NFPA 13-2025 §8.2.7.5.3 and §8.2.8.2). A compressor dedicated to the sprinkler system is listed on an NFPA 13-2025 job (§8.2.7.5.2).

A sizing screen, not an NFPA formula, is compressor cubic feet per minute equals system gallons times pressure, divided by 7.48 times 14.7 times 30. At 40 psi the shortcut is about 0.012 times the gallons. Size on the absolute basis from `calcs/fp`, which is higher than a gauge-only rate. A listed compressor table governs when it is in hand.

Use a second compressor when one outage would leave more than one double-interlock zone unable to restore in 30 minutes. The 30 minute clock is NFPA 13-2025 §8.2.7.3. The largest zone, not the campus total, is what that clock sizes (`nitrogen-compressor-and-c-factor.md`).

FM DS 2-81 Table 2c item 10 expects that loss of air does not trip the valve for the water-supply duration or 2 hours, whichever is greater. That is an insurer test, not the fill-time calculation.
