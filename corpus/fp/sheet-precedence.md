# Which FM sheet governs the hall

FM DS 5-32 (January 2026) §2.4.3.2.1.1 installs sprinklers to FM DS 2-0 plus the occupancy section. Where the occupancy sheet is silent, DS 2-0 still applies. Where the occupancy sheet speaks, it displaces the installation-sheet default.

Use these displacements on a data hall:

- Deflector distance is measured by DS 5-32. The binding maximum is 4 in. NFPA 13-2025 §10.2.7.1.1.1 allows up to 12 in. The 4 in. limit governs on the FM job (`hall-geometry.md`).
- Delivery-time defaults of 60, 50, and 40 seconds in DS 2-0 §2.2.1.11.1 apply only when the occupancy sheet sets no maximum. DS 5-32 sets 30 seconds to the most remote sprinkler. Thirty seconds governs (`water-delivery-screen.md`).
- DS 2-0 §2.2.1.11.3 still limits a dry or preaction system to about 10,000 ft² to 12,000 ft² if those longer delivery times are the goal. A hall zone is also held to the 500 gallon double-interlock cap in `water-delivery-screen.md`. The area guide does not raise the gallon cap.
- DS 5-32 states no K-factor of its own, so the 7 psi floor in DS 2-0 §2.5.1.1.2 still applies unless a K-class table raises it.
- A flat hall uses shape factor 1.2. FM DS 3-0 sets 1.2 at a ceiling slope of 5 degrees or less and 1.4 above 5 degrees (equations 11 and 12).

Storage entry is stricter on DS 8-9 §1.0, which includes over 200 ft² at any height for the commodities it names, than a DS 2-0 plastics threshold of 200 ft² and 5 ft. Use the stricter reading, then leave the hall sheet. See `storage-design.md`.

FM DS 2-81 (April 2019 / interim October 2021) Table 2c item 14 states a 60 second delivery default unless the occupancy sheet says otherwise. On a DS 5-32 hall the occupancy sheet says 30 seconds, and that 30 seconds is also the in-service pass-fail at the remote area. Do not grade the lifetime test to 60 seconds.

Provide both the DS 5-32 2 in. sectional test and the DS 2-0 remote inspector's test with a riser bypass.

FM DS 3-7 (April 2012) §2.4.6 sizes nonstorage pumps as one pump at 100 percent, three at 50 percent, or two mixed drivers at 75 percent, and states an N+1 expectation. Use of a single pump stops at 140 percent of rated flow. When more than one pump runs, the cap in that section is 110 percent. Do not print a rated flow and pressure until the demand and the friction are fixed. Series pumps stay off on FM work (`fire-pump-controller.md`).

A nominal temperature rating on DS 2-0 Appendix A is plus or minus about 4 percent. Do not treat 135 °F and 155 °F as interchangeable labels.
