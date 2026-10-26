# Double-interlock trim and releasing sequence

Double-interlock means two events: detection, and loss of sprinkler-system pressure. NFPA 13 defines that pair. Minimum supervisory air or nitrogen held in the pack: 7 psi (NFPA 13-2025 and 2022 §8.3.2.5.2; 2019 §8.3.2.4.4; 2016 §7.3.2.4.4). A manufacturer band can be higher. The code minimum is not a setpoint.

## What holds the prime chamber shut

"Failsafe" is not one trim. Ask what holds the prime chamber shut before picking a pressure.

- An electric/electric trim uses a normally closed solenoid. Supervisory air then serves the low-air switch (and an accelerator, if listed with that valve). The manufacturer may allow a lower setting.
- An electric/pneumatic trim uses a pneumatic actuator. That actuator has its own band. A common actuator band in the opened sheets is about 30 psi (about 50 psi when water pressure is high).
- A listed failsafe package that opens pneumatically on loss of power is a third family. It is listed as a unit with a named panel. Do not invent a bill of materials for one that is not on the current approval.

Stacking a pneumatic-actuator band near 30 psi on an electric/electric low-air switch near 7 to 15 psi is a failed election, not a field adjustment. Pick one opened sheet and use that sheet's band. Graph or table values that scale with water pressure are read from the printed graph, not from a remembered approximation.

A manufacturer accelerator setting versus zone volume is not printed as a rule. A prior screen that used a low setting only under about 1,200 gallons is `[V]`. Confirm with the manufacturer's technical support. Do not copy it.

Quick-opening-device trip time is still not water-delivery time. Hand the proof to `water-delivery-screen.md`.

## Sequence

The water path on double-interlock is detection (or the owner's pre-alarm level that the engineer of record has accepted) and low air. Both are required. Write that as the cause-and-effect matrix the panel is programmed from (`preaction-releasing-c-and-e-soo` and `fa/di-releasing.md`).

Wet pipe, when it is the elected system, is thermal operation of the sprinkler. Do not attach a double-interlock releasing program to a wet valve.

Clean-agent release is out of scope. Do not add an agent-discharge column to this matrix.

Single-interlock cause-and-effect packages are comparison-only. Do not use their zone counts or program numbers as defaults.
