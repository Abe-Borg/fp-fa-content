# Data-hall sprinkler geometry

The density, the area, the hose, and the duration for an HC-2 hall are `density-area.md`. The 30 second and 60 second clocks are `water-delivery-screen.md`. This note is the geometry those demands sit on. FM DS 5-32 below is the January 2026 sheet.

## Heads, spacing, ceiling

Quick-response sprinklers. Nominal 135 °F on wet pipe above the floor, and nominal 165 °F on a designed-dry system (§2.4.3.3.1.1(B)). Maximum spacing 12 ft. Deflector 1.75 in. to 4 in. below the ceiling. Ceiling height 30 ft (§2.4.3.3.1.1).

NFPA 13-2025 §10.2.7.1.1.1 allows 1 in. to 12 in. from the ceiling to the deflector. On an FM hall the 4 in. maximum governs. Where DS 5-32 is silent, the installation sheet still applies: 7 ft to 12 ft and 64 ft² to 130 ft², minimum K5.6 or K11.2 extended coverage (FM DS 2-0, October 2021 / interim January 2024, Tables 2.5.2.1.1(b) and 2.5.2.3.1.1(b)). Design pressure is at least 7 psi unless a K-class table raises it (DS 2-0 §2.5.1.1.2).

A nominal 135 °F wet head needs ceiling ambient at or below 85 °F, because FM DS 2-81 §2.5.1.3.1 treats exposure within 50 °F of the rating as damage. A 165 °F dry head is then capped near 100 °F by the ordinary-temperature ceiling. NFPA 13-2025 Table 7.2.4.1(a) allows a 135 °F glass bulb up to 100 °F ceiling ambient, which is a looser ceiling than the FM damage rule. Use the FM limit on an FM job. Temperature ratings and K-factor threads are `sprinkler-temperature-and-k.md`.

## Which area the interlock uses

Inside a DS 5-32 data-processing room, non-interlock and single-interlock use the wet area. Only double-interlock uses the dry area (§2.4.3.2.1.2). Do not import the DS 3-26 habit that treats non-interlock as dry. Single-interlock and non-interlock are comparison-only. They are never the basis of design. Electing double-interlock is the company practice on an FM hall, and it is the choice that takes the 3,500 ft² area. Flag the rank in §2.4.1.1. See `system-election.md`.

Water at the single most remote sprinkler within 30 seconds applies to every preaction type on this sheet (§2.4.3.2.1.2(D)). That sentence does not authorize another interlock as the basis.

## Air, trays, containment, rooms

Forced cooling air stays under 5 ft/s or under 60 air changes per hour, with a pre-alarm slowdown if either limit is reached (§2.4.2.1.3). The velocity test in §3.5.2.3 is 4 in. to 10 in. below the ceiling. The air-change branch does not state a room volume. Retest the interlock annually after the commissioning test (§2.7.4.4 and §2.4.2.1.3.2).

Ceiling-plane airflow above 5 ft/s in an HC-2 occupancy can also trigger an area remedy on DS 2-0 §2.5.2.1.8.1. Do not stack that increase on an area that is already the dry 3,500 ft².

Cable trays above the equipment need at least 12 psi at the sprinkler, or the head within 4 ft horizontally of the tray (§2.4.3.3.1.1(F)).

Solid aisle containment needs sprinklers below the containment, or FM Approved Class 4651 drop-out panels no more than 15 ft above the floor and 20 ft from the sprinklers (§2.4.3.5). A fusible-link curtain is not the sprinkler.

Room walls are 1 hour. Walls between multiple data-processing rooms are 2 hours. Doors are 3/4 hour, slab to slab (§2.2.4).

Distributed lithium-ion backup stays at or below 20 kWh per rack under this sheet (§2.3.1.4). Above that, use FM DS 5-33. In-scope distributed lithium-ion backup also gets vertical 20-gauge steel barriers every third rack (§2.4.3.6).

A cable-only vault on FM DS 5-31 (January 2020 / interim October 2025) §2.3.2.2(B) is 0.2 gpm/ft² over 3,000 ft² at 165 °F. Do not use 3,000 ft² in the hall.

Provide a sectional valve and a 2 in. test discharge downstream of the preaction valve (DS 5-32 §2.4.3.2.1.2(E)). Also provide the DS 2-0 remote inspector's test and the riser bypass. They are not substitutes for each other.

Storage rooms go to DS 8-9, lithium-ion storage to DS 7-112, and UPS rooms to DS 5-28 (DS 5-32 §2.4.3.9 and §2.4.3.10). Do not copy the hall density into those rooms.
