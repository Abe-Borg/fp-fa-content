# Liquid-cooled halls

Hall density stays `density-area.md` until the coolant's fire data says otherwise. Leak detection, containment, and the intervention matrix are `liquid-cooled-escaped-liquids-leak-detect`. This note is the fork that decides whether the hall is still that density.

Classify the fluid from the current safety data sheet. Record closed-cup flash point and fire point. No flash point, as with many aqueous direct-to-chip fluids, keeps the hall on the ordinary energized-equipment basis. A flash point without a fire point is not treated as a pool-fire density. Evaluate a confined-vapor event instead of switching to an ignitable-liquid ceiling design. A fluid with both a flash point and a fire point, in an open tank that can spill, is an ignitable-liquid problem on top of energized equipment. FM DS 5-32 tells the designer to use a nonignitable liquid in liquid-cooled servers. That choice keeps the hall on `density-area.md`.

Direct-to-chip with a nonignitable fluid does not change the density. It adds leak detection in the system or the room, branch isolation, and a coordinated shutdown of information technology and the cooling that serves it (DS 5-32). Power isolation is `hall-power-isolation.md`. There is no default sensing-cable offset from a wall. Coverage is a layout the designer draws before installation. A vendor clip spacing of 6 ft is an attachment interval, not a detection pitch.

Open immersion with a combustible dielectric uses FM DS 7-32 in addition to the energized-equipment controls. The ceiling package for a flash point under 200 °F is the drainage row in `ignitable-liquid-sprinklers.md`: 0.30 gpm/ft² over 4,000 ft² or 6,000 ft². Sprinklers are required under a tank or obstruction wider than 3 ft or larger than 10 ft². A ceiling-only layout over open tanks does not meet that rule. The all-welded piping exception that would let the surrounding occupancy govern is not available once hoses, valves, and quick disconnects exist. Containment holds at least the largest vessel, including interconnected volume. Dielectric does not go to the sanitary sewer. Foam, water mist, and gaseous agent are out of scope as the basis. The water ceiling design is the company path.

A sealed two-phase fluid with no fire point can stay on the hall density and still fail a supply review because of phasedown and reporting rules. Standardize it only when the owner accepts that supply risk. Integrity monitoring of the sealed boundary is part of the leak layer.

NFPA 75-2024 added immersion requirements. Liquid-to-chip text in the standard is still moving. Cite the edition the authority enforces. NFPA 75-2024 itself points at earlier editions of NFPA 13 and NFPA 72 (`edition-pins.md`).

The method is `liquid-cooled-escaped-liquids-leak-detect`. It consumes the wet, dry, or double-interlock election. It does not change that election.
