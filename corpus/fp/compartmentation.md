# Compartmentation and rated assemblies

Energy-storage room hours are `../fa/bess-separation.md`. A loss-limiting wall that assumes sprinklers are impaired is `mfl-walls.md`. This note is the ordinary interior assembly: what the building code requires, what the insurer adds, and which door and damper follow the wall that was chosen. The method is `fire-area-compartmentation-schedule`.

On a sprinklered, low-rise, same-occupancy Group B hall, IBC 2024 often requires no hall-to-hall fire-resistance rating for allowable area. Unlimited-area buildings under §507, where the yard conditions are met, remove the usual reason to add a fire wall for area. A rated wall still appears when the code has a separate job: separated occupancies (§508.4), a fire-area strategy (§707), a control area, an energy-storage room, or a shaft or exit enclosure. Name the driver. A 2-hour line between data halls on an FM job is FM DS 5-32 §2.2.4 (`hall-geometry.md`), not a silent code floor.

Choose the assembly by purpose. A fire wall (§706) is only for the separate-building effect, with structural stability, a roof projection of at least 30 in, and the opening caps in §706.8. A fire barrier (§707) is the default for hall-to-hall, hall-to-support, shafts, and insurer compartments. It runs from the floor or foundation to the underside of the deck, and the construction that supports it carries the same rating (§707.5 and §707.5.1). A fire partition is a corridor tool. A smoke barrier is a smoke compartment, not a substitute for a fire rating.

Opening correspondence, once the wall rating is chosen:

- A 2-hour fire barrier takes a 1½-hour door. A blanket ¾-hour door does not meet IBC §716 for that wall. The code exceeds a carrier habit of ¾-hour doors on this parameter.
- Other 1-hour fire barriers take a ¾-hour door. A 1-hour shaft or exit enclosure takes a 1-hour (60-minute) door (IBC Table 716.1(2)).
- A corridor or smoke-barrier door is a 20-minute smoke-and-draft door, a separate case.
- A duct in a fire barrier takes a listed fire damper: 1½ hour when the assembly is under 3 hours, and 3 hours when the assembly is 3 hours or more. Damper type and the static rating fence are `dampers.md`.
- Through-penetrations are a listed system to ASTM E814 or UL 1479 (`firestops.md`). Joints are ASTM E1966 or UL 2079.

Reconciled ratings used on an FM campus, taking the stricter parameter: 2 hours between data halls, with a 1½-hour door; 1 hour between a hall and a meet-me room or a generator room unless fuel or energy-storage rules raise it. Energy-storage separation of 2 hours, where the fire code governs, is `../fa/bess-separation.md`. Non-lithium battery rooms are 1 hour with no capacity threshold (`non-lithium-battery-rooms.md`).

A large floor area alone does not trigger IBC §909 smoke control or a fire command center. Those follow an atrium, an underground building, or a high-rise. Many halls have fire alarm and HVAC shutdown with no engineered smoke-control system (`../fa/smoke-control-interface.md`).

Minimize ducts through the rated line. A damper that is never required is commissioning that is never owed.
