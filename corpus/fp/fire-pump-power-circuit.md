# Fire-pump power circuit

The electrical engineer sizes the feeder. This note is the fire-protection side of that coordination. The controller product and the signals are `fire-pump-controller.md` and `fire-pump-alarm-interface.md`. Maintenance of the same path is `pump-power-testing.md`.

Article 695 is its own regime. A competent building design will violate two of its prohibitions unless someone says so at schematic design.

## No ground-fault protection on the pump circuit

Ground-fault protection of equipment is required on solidly grounded 480/277 V wye services of 1,000 A and larger (NEC 230.95). The same threshold reaches building disconnects, branch-circuit disconnects, and feeders (240.13, 210.13, and 215.10). It is prohibited on a fire-pump power circuit (NEC 2017, 2020, and 2023 §695.6(G); NEC 2026 §695.7(G)). FM DS 3-7 §2.4.12.11 says the same thing. Cite the NEC. Do not argue it as an insurer preference.

A large hall service trips 230.95. A fire pump fed downstream of that service disconnect sits on the prohibited protection. The fix is the topology in 695.3(A)(1) (2026: 695.4(A)(1)): a connection ahead of the service disconnect, not a different breaker. On a campus feeder, ask the question at every disconnect in the path.

The exemptions that do not help: a fire pump is not an emergency system, so 700.31 and 701.26 (no ground-fault protection on the alternate source of those systems) are not cover. The exemptions that do help, and that a large campus will not meet, are services under 1,000 A and 208Y/120 V.

## Campus feeder

A feeder source in a multi-building campus is allowed only when the individual sources in 695.3(A) (2026: 695.4(A)) are not practicable, the authority approves the arrangement, and the overcurrent devices are selectively coordinated with the supply-side devices (2017 through 2023 §695.3(C)(3); 2026 §695.4(C)(3)). Write down why a dedicated service is not practicable. Get the approval named. Drawing approval is not that approval.

Selective coordination, in Article 100, runs from overload through the maximum available fault current, for the full range of opening times. A study that stops at the instantaneous pickup has not shown that. The sentence that requires a licensed engineer to select and document the coordination is absent from the 2017 text of 695.3(C)(3) and present in 2020, 2023, and 2026. Cite the adopted NEC.

Coordination and a transfer switch pull apart. Breakers coordinate only up to the upstream instantaneous pickup. Removing that trip so the upstream device waits drops the transfer switch's short-time rating. On one published label the same switch fell from 50 kA with an instantaneous trip to 20 kA on a 0.5 second short-time delay. The mechanism is general. The spread is that product. Confirm the label (`[V]` until the specified switch is in hand). The procurement choices are a fault current the short-time rating still covers, a coordination method that keeps the instantaneous trip, or taking the pump off the campus feeder. An automatic transfer switch in the fire-pump path is already a break in the water (`fire-pump-alarm-interface.md`). This is the electrical reason to keep the count of those switches small.

## Four numbers to get in writing

1. Available fault current at the controller line terminals and at any transfer switch, checked against the marked ratings. State the worst case: transformer impedance at 90 percent of nameplate for the usual ±10 percent tolerance, utility voltage at 110 percent, and motor contribution on the order of four times full-load current. Current-limiting devices in series do not compound. If a generator can parallel the utility, the duty is the combination.
2. Voltage at the controller line terminals during normal starting, at most 15 percent below the controller's rated voltage (NEC 2023 §695.7(A); 2026 §695.8(A)). The limit is at the controller, not at the motor, and the generator has to meet it too. A federal generator criterion uses the same 15 percent dip and also wants the generator loaded, without the fire pump, enough to avoid wet stacking. That document says 35 percent in one place and 30 percent in a later change. Thirty percent is the newer figure and matches the NFPA 110 direction it cites. Thirty-five percent satisfies both. The running limit at the contactor load terminals is 5 percent below the motor rating at 115 percent of full-load current (2023 §695.7(D); 2026 §695.8(D)).
3. Conductor ampacity is the floor (2017 through 2023 §695.6(B); 2026 §695.7(B)). On a long campus run the voltage drop governs. Do not stop at ampacity.
4. The instantaneous pickup of every upstream device. That number tells you whether the coordination study is real.

Do not fuse the fire-pump control circuit. NEC 430.72(C) Exception omits overcurrent protection where opening the control circuit would create a hazard, and it names a fire-pump motor as the example.

Inside a building, the 2023 NEC allows 2 in. of concrete around the fire-pump conductors. The 2026 NEC §695.7 raises that to 5 in., with 2 in. only when a licensed engineer documents a 2 hour rating. Cite the adopted edition. Verify the rating path with the engineer of record.

Field-mark the transfer equipment's short-circuit rating on the enclosure, based on the overcurrent device and its settings (the 2017 and later marking rules in 700.5(E), 701.5(E), 702.5, and 708.24(E)). Photograph the label at closeout.

The insurer sheet agrees with these NEC rules. It does not raise them. You cannot delete them by negotiating with the carrier. Owner standards can still forbid a campus feeder or forbid a transfer switch. Ask that before the gear is bought.
