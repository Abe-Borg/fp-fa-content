# Fire-pump alarm interface and transfer

Configuration that must stay off, and the signal list to name, are `fire-pump-controller.md`. This note is the gap between that list and the box, and the fact that a transfer stops the pump.

## The listing has a ceiling

Codes and insurer sheets state a pump-room minimum. They do not state a maximum. The controller listing does. One indoor controller examined for this pack was rated 39 °F to 104 °F, with alarms at 41 °F and 104 °F. Those alarms announce the limit. They are not an early warning. Publish the minimum and the maximum from the listing actually purchased. The FM floor of 40 °F (DS 3-7 §2.2.1.6) is stricter than a 39 °F product floor. A room next to heat-rejection equipment can miss the maximum while it satisfies the freeze floor.

Indoor NEMA 2 construction is a common listing. An outdoor skid needs the enclosure specified at order. Seismic certificates on a controller are void until the structural engineer issues anchorage. A preapproval pinned to an older building code does not travel by itself.

## Map signals to terminals

FM DS 3-7 §2.2.1.12, for an electric pump, wants running, loss of power, controller on the alternate source, and failure to start, at a constantly attended location. FM DS 2-81 §2.9.6 adds loss of phase and phase reversal, locally and at the fire-alarm panel or the supervising station.

On the controllers examined, that list does not land on one strip:

- Running and phase reversal are often discrete.
- Failure to start is often inside a composite trouble point, and one product delays it 20 seconds. Do not write a cause-and-effect time that ignores the delay.
- "Connected to the alternate source" is often on the transfer-switch enclosure, not the controller strip. Landing only the controller strip drops an insurer point.
- A point named for the pump room can be an electrical composite (overvoltage, undervoltage, phase unbalance). Read the definition.
- A fail-safe "power available" contact may be a long trouble summary. Ask for the membership list before the matrix is written (`[V]` until that submittal).

Do not copy terminal letters from one manufacturer onto another.

Overcurrent thresholds on these controllers annunciate. They do not trip. That matches the decision to let the pump run. Ask the submittal to confirm that no trip can be turned on.

Reduced-voltage starting changes the conductor count. Across-the-line, autotransformer, and solid-state starters are three conductors plus ground at 125 percent of full-load current. Part-winding and wye-delta starters are six conductors plus ground, sized at 125 percent of about half and about 58 percent of full-load current. The 100 hp and generator cases that require reduced voltage are `fire-pump-controller.md`. Decide the conduit at the one-line.

Shared analog inputs are a product limit. Suction pressure and tank level can occupy one input, and flow and a spare temperature another. Choose at the submittal. Put the signal you did not land on another supervised device. An automatic pump-curve feature that needs flow plus both pressures can foreclose tank level on that controller.

## The transfer is an outage

Every transfer stops a running motor so it is not thrown across the line while it is still turning. It restarts on the normal sequence after the switch has finished, plus the manufacturer's restart delay, plus any reduced-voltage ramp. One product's chain, from dropout below 85 percent of nominal through a roughly 15 second generator start and a 3 second accept, was at least 23 seconds before the restart command, and about 28 to 31 seconds to full voltage on a wye-delta ramp. That chain is that product. Order the times from the submittal and mark the hold `[V]` until then (`fire-pump-controller.md`). Narrate a pump that is off for the window. Do not narrate a bridge.

Retransfer while the motor is running is inhibited on that product, so the pump takes the outage once during a fire. Phase order of the two sources has to match at rough-in. A mismatch looks like a phase reversal and can start a transfer.

The transfer can move before the undervoltage alarm. Dropout at 85 percent and an alarm at 80 percent leaves a band where the only annunciation is the alternate-position contact. That is a second reason to land the transfer-switch strip.

## Acceptance is the stricter list

NFPA 20-2019, 2022, and 2025 §14.2.7.2 require at least six automatic and six manual starts. A federal specification asks for ten and ten, and it is that specification. A manufacturer's form can also ask for emergency-handle starts and one remote start, and then repeat the block on the alternate source. Take the union of the instruments that apply. Do not submit the manufacturer's form as the acceptance record. Keep the lines it does well: nameplate full-load and locked-rotor current for the controller and the motor, rotation on both sources, and the recorded cut-in, cut-out, and timers.

Where the controller offers a no-flow weekly test, enable it and record the window. A test that looks for a pressure drop of about 5 psi is checking the solenoid. It is not the annual flow test (`acceptance-tests.md`).
