# Battery-room hydrogen ventilation

Suppression and the 1-hour room are `non-lithium-battery-rooms.md`. Lithium-ion off-gas is a different gas and a different trip (`ess-explosion-control.md`). Process hydrogen is `hydrogen-equipment-rooms.md`. This note is the airflow for flooded, valve-regulated, and nickel-cadmium charging.

FM DS 5-28 §2.3.1.3 (April 2021) offers 1 cfm per square foot of floor, continuous, or a design to IEEE 1635, holding hydrogen below 1 percent of room volume during simultaneous boost charge of all batteries. Those are not equivalent alternatives. The area rate is a floor. The charging current sets the generation. Air changes per hour are an output after the flow is known.

The published dilution form is generation H = N × I × k cubic feet per hour, with k = 0.0158 ft³ per ampere-hour per cell at 20 °C, and airflow Q = H / (0.01 × 60). Collapsed, Q = 0.0263 × N × I cfm at a 1 percent limit. N × I is the sum of cells times charging amperes. The constant is the Faraday-derived factor used in the battery-room literature. It is not an NFPA section. Re-derive any worked example that is handed over. A circulated example that prints a result two orders of magnitude too low is a known failure of that arithmetic.

The area rate and this calculation cross when N × I per square foot of floor is about 38. Below that, 1 cfm/ft² is conservative. Above it, the area rate under-ventilates and the calculation governs. A customary 1.25 multiplier covers temperature, charger failure, net volume, and deterioration. It does not cover mixing. OSHA's dilution method uses a mixing factor from 2 to 5, with 2 as the optimum, and the factor multiplies the flow. State the factor. A calculation that omits it has asserted perfect mixing.

Hydrogen is buoyant. Exhaust at the true high point, make-up low, and do not leave ceiling pockets. Where the room also exhausts acid vapor, the low extract does little for hydrogen. Size the hydrogen flow on the high-level portion.

Alarm below 1 percent, which is 25 percent of the 4 percent lower explosive limit (DS 5-28 §2.3.1.4). A 2 percent setpoint is 50 percent of that limit. Reject it. Provide two fans, each alarmed, with automatic changeover. The sheet accepts a ventilation-failure monitor in place of a gas detector. On a campus, provide both. What feeds the fans is not stated. A room ventilated only on normal power loses hydrogen control during the outage that produces the heaviest recharge. Put the fans on the backup source and record the transfer. Mark the power source `[V]` until the one-line shows it.

The 1 cfm/ft² figure traces to a legacy fire-code article that also offered a calculated 0.8 percent limit. That parent code is not the adopted IFC. Cite DS 5-28 for the insurer number. Confirm NEC Article 480 and the adopted fire-code battery chapter on the job. The code floor is `[V]` until that check is written down.

The three-layer method is `most-stringent-basis-matrix`. The energy-storage gas layout is `fa-bess-gas-detection-layout-and-setpoints`. This room's setpoint stays below 1 percent hydrogen. Do not move it to the energy-storage 10 percent lower-flammable-limit trip.
