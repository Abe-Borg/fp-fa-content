# Non-lithium UPS and battery rooms

Lithium-ion leaves this sheet. FM DS 5-28 §2.4 sends lithium-ion fire protection and its gas detection to DS 5-33 (`ess-room-sprinklers.md`, `ess-explosion-control.md`). Flooded lead-acid, valve-regulated lead-acid, and nickel-cadmium stay here. The sheet is FM DS 5-28, April 2021. Stored batteries that are not in service are DS 7-112 (`li-ion-storage.md` for lithium-ion storage). The hydrogen calculation is `battery-room-hydrogen.md`.

Sprinklers are automatic, quick-response, hazard category 2, per DS 3-26, installed to DS 2-0 (§2.4.2). The area pair used for that category on a data-center occupancy is `density-area.md`. Designing the room to hazard category 1 understates both density and the airflow rules on DS 2-0. Gaseous protection is out of scope. The sheet allows it only as a supplement. Water remains the basis.

The room is at least a 1-hour enclosure for lead-acid and nickel-cadmium, with no area or capacity exception (§2.2.4). Raise that wall at schematic design. Doors, dampers, and firestops follow `compartmentation.md` and `firestops.md`. Redundant lithium-ion systems, when they appear beside this room, each get their own cutoff room (§2.3.3.3). That is a siting rule. The suppression numbers are still the lithium-ion notes.

Ventilation is at least 1 cfm per square foot of floor, continuous, or a design to IEEE 1635, holding hydrogen below 1 percent of room volume during simultaneous boost charge of all batteries (§2.3.1.3). Alarm below 1 percent, by a hydrogen detector or a ventilation-failure monitor, to a constantly attended location (§2.3.1.4). The two paths are not equivalent. Run the screening test in `battery-room-hydrogen.md` before accepting the area rate. Valve-regulated cells still vent. A sealed label does not omit the ventilation.

The room's air system is separate from the equipment areas (§2.3.1.1). One reason is contamination of other equipment if a battery event occurs. Target room temperature as close to 77 °F as the plant allows (§2.3.1.1). Lead-acid life is described as halving for each 15 °F above that (§3.3.2). Cell-to-cell difference above 3 °C on lead-acid, or 5 °C on nickel-cadmium, is the uneven-aging flag.

Floor penetrations within 10 ft of a flooded-battery rack on an upper floor are sealed against acid (§2.2.5). Flood elevation follows DS 1-40: above the 500-year flood, plus 1 ft to 2 ft (§2.2.3).

The sheet cites IEEE battery-maintenance standards and does not print an NFPA or I-Code section for the room rating. The code floor under the 1-hour wall and the ventilation rate is `[V]` until the adopted fire code and NEC Article 480 are checked on the job. The insurer numbers above still govern an FM room.

Detection in the room, as a fire-alarm layout, is `../fa/space-detection-matrix.md`. The hazard method for the ceiling density is `occupancy-hazard-fork`.
