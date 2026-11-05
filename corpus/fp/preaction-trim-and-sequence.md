# Double-interlock trim and releasing sequence

Double-interlock means two events: detection, and loss of sprinkler-system pressure. NFPA 13 defines that pair. Minimum supervisory air or nitrogen held in the pack: 7 psi (NFPA 13-2025 and 2022 §8.3.2.5.2; 2019 §8.3.2.4.4; 2016 §7.3.2.4.4). A manufacturer band can be higher. The code minimum is not a setpoint.

## What holds the prime chamber shut

"Failsafe" is not one trim. Ask what holds the prime chamber shut before picking a pressure.

- An electric/electric trim uses a normally closed solenoid. Supervisory air then serves the low-air switch (and an accelerator, if listed with that valve). The manufacturer may allow a lower setting.
- An electric/pneumatic trim uses a pneumatic actuator. That actuator has its own band. A common actuator band in the opened sheets is about 30 psi (about 50 psi when water pressure is high).
- A listed failsafe package that opens pneumatically on loss of power is a third family. It is listed as a unit with a named panel. Do not invent a bill of materials for one that is not on the current approval.

Stacking a pneumatic-actuator band near 30 psi on an electric/electric low-air switch near 7 to 15 psi is a failed election, not a field adjustment. Pick one opened sheet and use that sheet's band. Graph or table values that scale with water pressure are read from the printed graph, not from a remembered approximation.

On a Reliable DDX-LP valve, low air is at least the low-pressure trip plus 2 psi plus 5 psi on a US NFPA 13-2025 job (§8.2.6.4), and high air stays at or below 30 psi. Calculate that margin on each Bulletin 505 row. At 20 psi maximum water the minimum supervisory pressure is 8 psi and the cap is 10 psi: nominal trip 5 psi plus 2 psi plus 5 psi is 12 psi, which is above the cap, so the margin does not fit. At 30 psi water the minimum is 10 psi and the cap is 14 psi: the same stack is 12 psi, under the cap. At 50 psi water the minimum is 12 psi and the cap is 16 psi: nominal trip 7 psi plus 2 psi plus 5 psi is 14 psi, under the cap. Only the 20 psi row fails that arithmetic. A margin pass on the 30 or 50 psi row is not a failure. Factory low air of 18 psi is a separate manufacturer setting. On the 20, 30, and 50 psi rows it is above every cap, so it still has to be lowered in the field. Bulletin 505 also prints 225 psi water at a 21 psi minimum and 275 psi water at a 23 psi minimum, both with a nominal trip of 14 psi. At those two rows factory 18 psi sits between the trip plus 2 psi and the Table A minimum, so do not field-lower it, and do not call the 5 psi margin a pass (16 psi plus 5 psi is 21 psi). Do not interpolate between rows. Bulletin 747 matches the Table A minima and does not print caps or trip; keep those on Bulletin 505. The switch tolerance stays unheld. A margin that fits does not close that hold, so low air stays assumed where it is open. Verify with the engineer of record. The Potter PS25 pairing on the PrePaK is named in Reliable Bulletin 747 (November 2022). Do not cite the 2025 section numbers on a Canada pin. The 2019 section numbers for the 5 psi margins are NEEDS HOLD.

A manufacturer accelerator setting versus zone volume is not printed as a rule. A prior screen that used a low setting only under about 1,200 gallons is `[V]`. Confirm with the manufacturer's technical support. Do not copy it.

Quick-opening-device trip time is still not water-delivery time. Hand the proof to `water-delivery-screen.md`.

## Sequence

The water path on double-interlock is detection (or the owner's pre-alarm level that the engineer of record has accepted) and low air. Both are required. Write that as the cause-and-effect matrix the panel is programmed from (`preaction-releasing-c-and-e-soo` and `fa/di-releasing.md`).

Wet pipe, when it is the elected system, is thermal operation of the sprinkler. Do not attach a double-interlock releasing program to a wet valve.

Clean-agent release is out of scope. Do not add an agent-discharge column to this matrix.

Single-interlock cause-and-effect packages are comparison-only. Do not use their zone counts or program numbers as defaults.

## Compressor on an NFPA 13-2019 Canada pin

On a Canada pin the floor is NFPA 13-2019 §8.2.6.3.2: a dedicated compressor delivers at least 3.5 scfm absolute and restores the largest system in not more than 30 minutes. Annex A.8.2.6.3.2 is the 2019 annex. The 2025 annex restore text is not retrieved. NFPA 13-2025 §8.2.7.3 is a reconcile lane only when the job elects it. A heated valve room uses 30 minutes, not the below 5 °F allowance of 60 minutes. A teaching volume of 211 gal at 40 psig needs about 3.50 scfm absolute. Do not freeze a model number. Fill one system at a time.

Relief is at least system air plus 10 psi (NFPA 13-2019 §8.2.6.5; NFPA 13-2025 §8.2.9.4). At 40 psig assumed, that is at least 50 psig. A factory plus 5 psi setting is short. High-air supervision is at least 5 psi above system air, so at least 45 psig at that assumed maintain. Cite the 2019 family at §8.2.6.7.2 and §8.2.6.7.2.2 on a Canada pin, and the 2025 §8.2.6.4 and §8.2.6.5 margins only when that edition is elected. Do not invent a ULC body. The maker trip setpoint stays open.
