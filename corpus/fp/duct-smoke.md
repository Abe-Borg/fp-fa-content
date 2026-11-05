# Duct smoke and fan shutdown

Two triggers, and they are not the same side of the unit.

NFPA 90A, 2024 numbering: a supply over 2,000 cfm is detected downstream of the filters, and a return over 15,000 cfm serving more than one story is detected at each story (§11.4.2.1). The 2021 numbering of the same split is §6.4.2.1. The 2027 numbering in one pull matches the 2024 section. Cite the edition.

IMC 2024 §606.2.1 requires a detector in a return over 2,000 cfm, upstream of the filters, unless area smoke detection covers every space that unit serves. §606.2.3 requires a detector at each story on return risers over 15,000 cfm. Where both NFPA 90A and the IMC apply, meet both. One instrument trips the supply at 2,000 cfm. The other trips the return at 2,000 cfm. The area-detection waiver covers the return side. It does not by itself waive a supply-side trigger, and it fails if the unit also serves a space without area detection.

FM DS 5-48 §2.2.3.3.12 and §2.2.3.3.12.1 (January 2011 / interim April 2025) repeat the 2,000 cfm fan interlock, the 15,000 cfm multi-floor return, and the complete-coverage return waiver.

The signal is supervisory in NFPA 72-2019, 2022, and 2025 §21.7.4. The sentence matches. An alarm is permitted only where there is no constantly attended location and no supervising station, or where another code requires an alarm (§21.7.4.1 and §21.7.4.2). Those alarm-permitted cases match across the same three editions. Annex A.21.7.4 is not held. A local amendment can also say the duct detector does not replace open-area detection. Confirm the amendment. Do not let a duct detector stand in for the hall sampling layout.

An older NFPA 90A exemption for a fan whose only job is to exhaust outdoors must be confirmed in the current section before you omit a detector on a battery-room or generator exhaust fan. Gas exhaust for an energy-storage room is not shut down by a general HVAC shutdown (`../fa/bess-separation.md`).

NFPA 72-2019 §17.4.6 required a remote indicator for a concealed detector more than 10 ft up. NFPA 72-2022 and 2025 §17.4.7 cover any concealed detector, and §17.4.7.3 exempts a point that is shown at the panel and on the drawings.

Accept the detector by the manufacturer's differential between the inlet and outlet tubes. A smoke test can pass while the unit is outside its listed pressure range. Place the sampling run downstream of a disturbance. Six duct widths is the FM DS 5-48 §2.2.3.3.10 figure. Ten duct diameters is a stricter applications-guide figure. Use the stricter one when the guide is the submittal basis, and name which figure you used. Stay at least 10 ft downstream of a humidifier. Support the tube when the duct is wider than 3 ft.

Duct detectors are listed for in-duct use. A detector listed only for open area is not installed inside a duct. A published envelope of about 42 °F to 180 °F, static pressure from +5 in. to −2 in. of water, and about 200 fpm to 4,500 fpm is a guide, not a code range. Confirm it on the listing.

Four equal return branches dilute smoke about fourfold. The common duct reaches 0.2 percent per foot only after a branch is near 0.8 percent per foot. That ratio is mixing math, not a setpoint.

NFPA 92A and NFPA 92B are no longer separate standards. Smoke-control activation is NFPA 92 (`../fa/smoke-control-interface.md`).

A tested equipment room reached its allowable inlet temperature on the order of 30 to 90 seconds after the fans stopped. Treat that as research. Decide fan shutdown in the sequence. Do not invent a cooling-hold minute (`../fa/interfaces.md`).
