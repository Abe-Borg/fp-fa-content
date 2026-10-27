# Stair pressurization

Most single-story halls have no pressurized stair. The trigger is a smokeproof enclosure, a high-rise, or an underground condition, not the words "data center." Engineered smoke control at an atrium is `../fa/smoke-control-interface.md`. Post-fire dilution in the hall is `smoke-purge.md`.

Two pressure rules are in circulation and they are not the same scope. NFPA 92-2024 Table 4.4.2.1.1 sets 0.05 in of water across a sprinklered barrier at any ceiling height (`../fa/smoke-control-interface.md`). The IBC smokeproof-enclosure alternative is a band of 0.10 in to 0.35 in of water across the stair door. Confirm the section in the adopted IBC before using the band. Sizing the fan to the top of that band when only the 0.05 in table applies oversizes the fan by about the square root of 0.35 / 0.05.

The door-force limit binds first. The adopted building code limits the force to set a side-swinging egress door in motion, commonly 30 lbf (IBC 2021 §1010.1.3; confirm the adopted edition). At 0.35 in of water, a 36 in by 7 ft door with a 10 lbf closer is already near or over a 30 lbf motion limit. A 48 in door has almost no closer force left. Compute the force. The pressure ceiling does not guarantee it. The moment form used for that check is force at the knob equals closer force plus K times width times area times pressure difference, divided by twice the distance from the hinge side to the knob, with K about 5.2 when pressure is in inches of water and width is in feet. Verify the arithmetic on the door that is specified.

Leakage used to size the fan has the orifice form Q = 2610 × A × √ΔP, with Q in cubic feet per minute, A in square feet, and pressure in inches of water. The implied discharge coefficient is about 0.65. Confirm the coefficient in the adopted NFPA 92 edition before sealing. The same form is the door-fan arithmetic. An effective leakage area measured for one purpose is usable in the other if the pressure is stated.

Design velocity through an open stair door is often 200 ft/min, which is also the NFPA 92 cap on makeup velocity toward a plume (§4.4.4.1.4 in the 2024 edition, unless an analysis supports more). A design that sits on 200 ft/min has no margin against that cap. A data-hall aisle that already moves air faster than that is `smoke-purge.md`. It is a different velocity problem.

Any initiating device in the building may start stair pressurization, because the stair does the same thing regardless of which floor is involved. That permission does not extend to a zone-dependent smoke mode (`smoke-purge.md`).

A fixed-speed fan with no relief swings from too much pressure with the doors shut to too little with the doors open. Use relief or modulation except on a small stair with little traffic. Provide two outdoor intakes, facing different directions, each sized for the full flow, each with its own detector and damper.

Gaseous-agent door-fan work is out of scope. The orifice form above is kept because the stair uses it.

The interface method is `fa-hvac-door-and-lock-interfaces`. The barrier schedule is `fire-area-compartmentation-schedule`.
