# Waterflow and valve supervision

Waterflow is an alarm. It is within 90 seconds of a flow equal to the smallest sprinkler orifice (NFPA 72-2025 §17.15.2; 2019 and 2022 §17.13.2). That 90 seconds is the device limit. It is not the water-delivery clock and it is not the FM 60 second alarm-receipt test.

FM DS 2-0 (October 2021 / interim January 2024) §2.3.3.2: the waterflow alarm starts within 60 seconds after sprinkler operation, measured at the most remote inspector's test connection downstream of the device. Local notification is required for a system of at least 2,000 ft² (§2.3.3.2 in the same family of rules; confirm the subsection). FM DS 5-40 Table 1, September 2007, also uses 60 seconds as an acceptance time for waterflow receipt. That clock is separate from a 90 second retard and from the 30 second delivery test (`water-delivery-screen.md`).

Do not use a vane switch on dry or preaction pipe. The opening rush can damage the vane. Use a pressure switch. On preaction there is no supply surge at the switch until the valve has opened, so a retard only adds delay. Do not put the wet-system retard on a preaction switch.

Typical retard bands printed in old device manuals (tens of seconds, under the 90 second cap) are not code settings. Set the retard from the listing and the surge the wet system actually sees.

A normally open valve signals when it is closed by no more than two turns or one-fifth of the travel. A normally closed valve signals on the same opening movement (NFPA 72-2025 §17.19.1.2; 2019 and 2022 §17.17.1). A buried non-rising-stem valve uses a listed supervisory switch. Confirm the turns on that device's instructions.

NFPA 72-2025 §17.19.2.2.2 requires both high and low pressure signals on dry and preaction systems. The off-normal point follows NFPA 13 unless the valve instructions allow otherwise. Draft commentary that a system running near 8 psi to 15 psi should not use a 10 psi band is maker commentary, not the code sentence. The 5 psi design-practice margin is `air-maintenance.md`.

NFPA 13-2025 §16.9.3.3.1 allows valve supervision by a station signal, a constantly attended local signal, locking, or fencing and sealing with a weekly inspection. High-rise floor control valves may use only the station signal or the constantly attended local signal (§16.9.3.3.2). Roadway-box underground gate valves are exempt (§16.9.3.3.3). A listed backflow assembly counts as a control valve (§16.9.3.3.5). Electrical supervision is the company default when the fire alarm exists (`../fa/supervisory-points.md`). Locking does not create a fire-alarm point.

Room-temperature supervision, where provided, is 40 °F (NFPA 72-2025 §17.19.5). Tank level and temperature points are supervisory.

On a dry or preaction riser, waterflow confirms that water moved past the switch. It is late. It is not the valve-trip signal. The trip is detection plus low pressure.

A bypass test connection operates the waterflow alarm without sending water past the system valve. The inspector's test connection may need more than one outlet, with a smooth-bore orifice no larger than the smallest sprinkler, chosen from the delivery-time design (FM DS 2-0 Appendix A). Confirm the outlet count on the sheet in hand.

FM DS 9-1 Appendix C, interim January 2021: Class V supervises waterflow. Class VIA also covers valves over 1 in. or serving more than five sprinklers, plus dry-pipe pressure, pumps, tanks, and detection. See `alarm-service-class.md`.
