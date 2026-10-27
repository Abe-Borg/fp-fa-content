# Air-sampling layout limits and commissioning

A listed pipe-network model sizes the holes, the balance, and the predicted transport. Hand math is only a screen. NFPA 72 requires the listed program. The paragraph is the air-sampling section in `../fa/asd-performance.md`.

## Return openings

FM DS 5-32 (January 2026) §2.4.2.2.3 applies 4 ft² per port to each discrete return opening, not to the whole face of a common fan wall. A fan wall of well over a million cubic feet per minute can be thousands of square feet. A literal 4 ft² count on that face is not the layout. Size room and underfloor ports by the class area, and keep the 4 ft² rule on the opening. Sample at the return opening or in the return plenum, upstream of mixing inside the air handler. There is no fan-wall exception on the January 2026 sheet.

Prove the layout at maximum outside air. Recirculation with little filtration makes detection easier and is not the design case. Studies at about 30 to 150 air changes found high-sensitivity ceiling and ceiling-plenum detection workable, while a detector inside the air handler saw smoke only after it had mixed with the whole room. Changing ceiling height from about 10 ft to 20 ft barely changed that spacing, because equipment heat is a weak buoyancy source and transport is momentum-driven. Those study spacings (about 20 ft flaming, 10 ft to 15 ft smoldering) are research. They are not a code table.

Hot-aisle containment sends a cabinet plume into the plenum. Room-ceiling detection misses it. A detector in the hot aisle has to sit over the cabinet. One plume was about 5 ft wide at low flow.

Do not use a spot detector above 300 ft/min unless it is recognized for that airflow. At very high air-change rates the ceiling plane can sit near that speed (FM DS 5-48 §2.2.3.1.3).

## Head location and hole cap

Usable early-warning area is the listed hole count times at most 200 ft² per hole. A 100-hole head is about 20,000 ft² at that density. A published area near 70,000 ft² on a 100-hole head is about 700 ft² per hole. That claim is fenced by local rules. Do not use it on an FM hall. A 40-point head is 8,000 ft² at 200 ft² per point. Confirm whether the model sheet is UL, FM, both, or neither. Marks differ inside one family.

Put the detector body in conditioned space. Sampled-air ratings near 140 °F do not automatically apply to the body, which often stops near 100 °F. Do not copy a 140 °F sampled-air rating onto a head whose sheet stops lower. One head in a comparison was listed for a hazardous location. The others were not. Read the mark.

A European hole cap (class A, B, and C counts) can bind before a chamber-sensitivity floor. The listing cap governs. A UL open-area listing can limit design-tool transport to 45 seconds up to 300 ft/min and 40 seconds from 300 ft/min to 4,000 ft/min, with a minimum balance of 50 percent. The design aim remains at least 70 percent. A companion listing in the same table allows 49 seconds and 47 seconds. Use the table on the submitted model.

For a U.S. four-pipe network, one 2023 product guide limits total branched length to 1,542 ft and each straight pipe to 230 ft. Do not substitute a metric datasheet total from another market. Aspirator speed can change standby current by about a factor of two. Size power from the speed the pipe model uses.

If detector exhaust pressure exceeds room pressure, pipe the exhaust back into the sampled room or the transport time grows.

## Commissioning

Commission from the most remote hole. Design practice, from a code-of-practice target rather than from NFPA 72, is balance of at least 70 percent between the nearest and farthest holes, ideally near 100 percent. A pipe-integrity test should move the flow indication clearly above the recorded baseline. Record flow percent and transport time, and recheck at least annually.

Design both a return-path network, which works while the fans run, and a ceiling network, which works when the fans are off.

In-duct inlet placement of 6 to 10 duct widths, holes at least 2 in. off the wall, and a return pipe stood 2 in. to 8 in. off the grille and aimed 20 to 45 degrees to the airflow rather than straight into it, are practice. Tuning order: fans off, power the detector, wait about 5 minutes, run the highest velocity, rotate the pipe in small steps, mark the angle, and recheck with the fans off. Check integrity at operating temperature.

A British cap of about 21,500 ft² lost to one detector fault is not the U.S. zone limit. Set the zone from the fire area.

Nominal pipe near 21 mm inside diameter, supports at 1.5 m, and a 24 V supply are hardware practice. Confirm them on the listing. The end cap is a vented last hole, the same size as the other holes or slightly larger.
