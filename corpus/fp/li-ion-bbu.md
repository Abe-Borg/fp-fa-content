# In-rack lithium-ion backup in the data hall

Hall density, spacing, and the 20 kWh line already sit in `hall-geometry.md`. This note is the scope fight around that line and the protection objective. The occupancy sheet is FM DS 5-32, January 2026.

Distributed backup stays under DS 5-32 when it is at most 20 kWh per rack, at most two shelves together, and the aisle is at least 4 ft (§2.3.1.4). Above 20 kWh per rack, §2.3.1.4 sends the rack to FM DS 5-33. DS 5-33 (January 2024) §1.0 excludes lithium-ion backup units installed in server racks of data-processing rooms and sends them back to DS 5-32. DS 7-112 excludes both installed backup units and energy-storage systems. Storage of modules that are not in a rack is `li-ion-storage.md`. The circular reference is only the installed rack above 20 kWh. On an FM job with that rack, get the carrier's written position before the water supply is frozen. The stake is a hall at 0.20 gpm/ft² over 2,500 ft² or 3,500 ft² versus a room-area density of 0.30 gpm/ft² (`ess-room-sprinklers.md`).

Rack energy is nameplate ampere-hours times volts, divided by 1,000, then multiplied by cells per module and modules per rack (§3.2.1.1).

Rows that use or may use this backup get a vertical barrier of at least 20-gauge solid sheet steel after every third rack, full height of the rack side, kept to the frame so aisle airflow remains (§2.4.3.6). That line is also in `hall-geometry.md`.

Suppression is quick-response sprinklers on the hall design. The objective is cooling the surroundings. The sheet states that a module fire is not extinguished by sprinklers (§3.3.3.3.2). Gaseous protection of these rows is out of scope. Water mist is out of scope. A mist listing written for a data-processing room that excludes lithium-ion is not a path around that fence.

IFC 2024 §1207.1.3 and Table 1207.1.3 put lithium-ion energy storage above 20 kWh into that chapter. The held text does not say whether many in-rack units under 20 kWh each are aggregated. Record the question for the fire code official. Do not write an exemption or an aggregation as if the code had settled it. Ohio's adoption of that chapter leaves the same question to the local official. NFPA 855-2020 Annex A.1.3 aggregates capacity per fire area. The 2023 and 2026 annex language is a later carve-out discussion. Which edition the fire code adopts is `../fa/ess-room-detection.md`.

The hall method is `density-area-dry-increase`. At-rest modules leave this note for `storage-staging-sprinkler-design`.
