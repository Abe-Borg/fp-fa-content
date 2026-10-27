# Hall power isolation

The Article 645 fork, the NFPA 75 disconnect, and the fire-alarm supervision of that disconnect are `../fa/epo-and-disconnect.md`. Switchgear-room isolation is a different object (`mv-switchgear-room.md`). This note is the FM DS 5-32 overlay, January 2026, §2.5.3 and Appendix D.

The performance goal is isolation before the suppression water's effective duration ends (§2.5.3.1). The prescriptive architecture is shunt-trip breakers on the affected panels, a direct shutdown of each UPS that removes battery power rather than only the feed, and a control panel with a test mode that registers triggers without opening the outputs (Appendix D). The code text requires an approved means. The shunt-trip and direct-UPS arrangement is the insurer prescription.

Automatic controlled shutdown is the default. For wet pipe, dry pipe, and double-interlock preaction, the trigger is any smoke detection or the waterflow alarm (§2.5.3.1). Manual isolation is acceptable only when every condition in §2.5.3.1.3 holds: very-early-warning detection, alarms at a constantly attended location, qualified responders on site at all times who can finish within 10 minutes, noncombustible construction, a plan the fire service has, and a measured drill at least annually. Miss one condition and the isolation is automatic.

Trip as locally as the event allows, and retain the ability to take the whole room (§2.8). Separate A and B UPS rooms may have separate disconnect systems. The control panel still has to be able to take both.

Cooling may continue only while equipment power is still on and the room must stay below a damage threshold (§3.4.2.2). There is no held minute count for that hold. Mark a duration `[V]`. A single disconnect that takes both the equipment and the dedicated HVAC is the sheet's preference. Damper and door behavior on that disconnect is `../fa/epo-and-disconnect.md`.

Gaseous-only shutdown timing on the sheet is out of scope. Company suppression is water-based.

Test mode is part of commissioning and of later inspection. Re-test after any added power, cooling, or fire-alarm change. Fuel emergency shutoff at a receiving yard is a third device, with its own location rule (`diesel-fuel-handling.md`). Label the three so a single red station is not ambiguous.

The method is `power-isolation-disconnect-control`.
