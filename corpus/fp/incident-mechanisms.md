# What investigated hall fires actually damaged

NIST Technical Note 1622 (2009) reprints FM investigations of telecommunications and colocation fires from 1993 through 2006, plus practitioner interviews. The record is three investigated cases and a set of recollections. It is pre-hyperscale, before in-rack lithium-ion backup and before liquid cooling. Use it for mechanism. It is not a frequency and it is not a code section.

The burned fuel in the investigated cases was a short run of cable insulation, a small area of plastic and a handful of drive cases, and a single voltage regulator. The outcomes ranged from replacing the machines in the room to no hardware loss. Non-thermal smoke contamination did the damage. Early detection, early isolation, and a planned smoke path are aimed at that loss. A purge design is `smoke-purge.md`.

Time to find the fire dominated one case. Visibility was reported under 3 ft, about 20 minutes passed between fire-department arrival and extinguishment, and the fire was out about two minutes after power was disconnected. A locating detection system is a loss-control device on that record.

De-energization is what changed the outcome, and in these cases it was a person walking to a switch, the fire department pulling a disconnect, or the room's own electrical protection. None of those was a designed fire-protection interlock. The interlock to design is `hall-power-isolation.md`. Prove it.

Opening doors to vent pushed smoke into an adjacent network room in one case. An exhaust path that started on its own is credited, in another case, with limiting contamination. An unplanned vent path is a second incident. Gaseous agent is out of scope. The useful remnant is the written recovery sequence and a bypass for the failed component. One case with a working automatic system returned to production in under three hours. That duration is that event. It is not a design input to copy.

Contractor and maintenance work sat next to live equipment in two of the three cases. The impairment that mattered was taken because of that work. Phased campus construction is the same condition (`impairment-and-hot-work.md`).

One investigated ignition source was never found. Design the detection and the isolation so the next event does not depend on a named cause.

The detection method is `fa-asd-vewfd-data-hall-sampling-layout`. The isolation method is `power-isolation-disconnect-control`.
