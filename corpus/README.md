# corpus

Paraphrased decision logs and edition pins for a later search pass. One topic per file. The desktop app does not read this folder yet.

This folder holds 120 notes: `scope-lock.md`, `design-conventions.md`, 92 files in `fp/`, and 26 files in `fa/`. The first 19 were the seed (the scope lock, 13 fire-protection notes, and 5 fire-alarm notes). The rest are paraphrased from topic notes and stripped of job names, personal names, and source-archive paths. Seventeen of the fire-protection notes are short digests of water-supply and fire-pump material. Thirty-one more are facility-type digests: rooms, yards, envelopes, and the spaces those systems protect. Large sources are summarized with section cites. City checklists, vendor catalogs, and a supply-analysis router that only restated notes already here were not copied. Chemical-plant process sheets, gaseous-agent design, and building water spray were not copied. Outdoor oil-filled transformer apparatus water spray stays in scope.

They are not a reprint of a standard. A numeric screen sits next to its edition and section. Where a licensed primary is not held, the note says `[V]` and does not invent a section.

Out of this folder: raw standards text, vendor catalogs, source-pull archives, job names, client names, and personal names. Foam, clean agent, and water mist are out of scope (the guard is in `scope-lock.md` only). A building deluge system is out of scope. Outdoor oil-filled transformer apparatus water spray (NFPA 15-style) is allowed and is sized in `power-block-transformer-water-spray`. Jurisdictions outside the stated NFPA, IBC, and IFC basis are out of scope. Canada stays out of scope. Single-interlock and non-interlock preaction are comparison-only. They are never the basis of design.

Company systems in these notes: wet pipe, dry pipe, and double-interlock preaction, outdoor oil-filled transformer apparatus water spray, plus pumps, nitrogen, compressors, and the Division 21 and Division 28 fire-alarm work those systems need.

Spec language is not here. When specs are ingested, double-interlock draft language belongs in CSI 21 13 19.

## Folder map

| Path | Count | What the folder holds |
| --- | --- | --- |
| scope-lock | 1 | Wet, dry, and double-interlock fence, plus outdoor transformer water spray |
| design-conventions | 1 | How a number is chosen, cited, and not copied from another hall |
| fp/ | 92 | Water-based suppression, detection that serves it, insurer sheets, facility types, and design practice |
| fa/ | 26 | Fire alarm, releasing, power, pathways, notification, and space detection |

`fp/` groups as: edition and election (`edition-pins.md`, `system-election.md`, `sheet-precedence.md`, `ufc-outside-pin.md`, `ufc-electronic-equipment.md`); hall and pipe (`hall-geometry.md`, `density-area.md`, `pipe-layout.md`, `pipe-volume.md`, `sprinkler-temperature-and-k.md`, `concealed-spaces.md`); dry and preaction (`water-delivery-screen.md`, `preaction-trim-and-sequence.md`, `air-maintenance.md`, `nitrogen-compressor-and-c-factor.md`, `nitrogen-sampling.md`); storage and liquids (`storage-design.md`, `storage-families.md`, `ignitable-liquid-sprinklers.md`, `li-ion-storage.md`); water supply hardware (`pump-and-supply.md`, `supply-test.md`, `water-supply-reliability.md`, `water-tanks.md`, `fire-pump-installation.md`, `fire-pump-controller.md`, `fire-pump-alarm-interface.md`, `fire-pump-power-circuit.md`, `jockey-pump.md`, `variable-speed-pump.md`, `pump-power-testing.md`, `control-valves.md`, `pressure-regulating-devices.md`, `backflow-preventer.md`, `standpipe-class-i.md`, `standpipe-system.md`, `campus-loop-and-fire-flow.md`, `private-fire-mains.md`, `thrust-restraint.md`, `needed-fire-flow.md`, `hydraulic-method.md`); detection and alarm (`duct-smoke.md`, `waterflow-supervision.md`, `fm-detection-install.md`, `fm-alarm-sheet.md`, `vewfd-acceptance.md`, `asd-commissioning.md`, `stratification.md`, `gas-detection.md`, `errcs.md`, `alarm-service-class.md`); installation and upkeep (`seismic-bracing.md`, `post-earthquake-supply.md`, `fuel-seismic-shutoff.md`, `freeze-heat-trace.md`, `cold-climate-freeze.md`, `heat-trace-supervision.md`, `itm-testability.md`, `acceptance-tests.md`, `impairment-and-hot-work.md`, `construction-safeguards.md`, `preincident-environment.md`, `controls-separation.md`); rooms and yards (`transformer-siting.md`, `mv-switchgear-room.md`, `cable-trays.md`, `lightning-and-surge.md`, `generator-plant.md`, `diesel-fuel-handling.md`, `non-lithium-battery-rooms.md`, `battery-room-hydrogen.md`, `hydrogen-equipment-rooms.md`, `ess-room-sprinklers.md`, `ess-explosion-control.md`, `damage-limiting-construction.md`, `li-ion-bbu.md`, `liquid-cooled-halls.md`, `telecom-rooms.md`, `plant-control-room.md`, `hall-power-isolation.md`); envelope and exposure (`compartmentation.md`, `firestops.md`, `dampers.md`, `exhaust-ducts.md`, `mfl-evaluation.md`, `mfl-walls.md`, `campus-exterior-exposure.md`, `smoke-purge.md`, `stair-pressurization.md`, `ground-mounted-pv.md`, `roof-mounted-pv.md`, `incident-mechanisms.md`).

`fa/` groups as: basis and documents (`edition-deltas.md`, `three-layer-basis.md`, `when-a-system-is-required.md`, `documentation-package.md`, `cybersecurity.md`); detection (`detection-layout.md`, `asd-performance.md`, `heat-detector-spacing.md`, `space-detection-matrix.md`, `ess-room-detection.md`, `bess-separation.md`, `generator-room.md`); circuits and notification (`pathway-class.md`, `pathway-survivability.md`, `nac-and-wire.md`, `notification-appliances.md`, `supervising-station.md`); releasing and power (`di-releasing.md`, `releasing-panel.md`, `preaction-supervision.md`, `supervisory-points.md`, `secondary-power.md`, `epo-and-disconnect.md`, `interfaces.md`, `smoke-control-interface.md`, `acceptance-testing.md`).

| File | What it holds | Skill to read for the method |
| --- | --- | --- |
| `scope-lock.md` | Wet / dry / double-interlock fence, plus outdoor transformer water spray | `suppression-technology-selection`, `power-block-transformer-water-spray` |
| `design-conventions.md` | Most-stringent layer, cite edition, do not copy another hall | `most-stringent-basis-matrix` |
| `fp/edition-pins.md` | Unamended 2024 I-Code reference pins | `most-stringent-basis-matrix` |
| `fp/system-election.md` | Wet, dry, and double-interlock election, including the FM rank | `suppression-technology-selection` |
| `fp/sheet-precedence.md` | When DS 5-32 displaces DS 2-0 | `most-stringent-basis-matrix` |
| `fp/ufc-outside-pin.md` | Federal criteria that are not the I-Code pin | `most-stringent-basis-matrix` |
| `fp/hall-geometry.md` | Hall spacing, temperature, deflector, and which area the interlock uses | `density-area-dry-increase` |
| `fp/density-area.md` | Dry/DI area fork, do not stack | `density-area-dry-increase` |
| `fp/pipe-layout.md` | Wall thickness, pitch, hangers, obstructions | `containment-ceiling-and-obstruction-coverage` |
| `fp/pipe-volume.md` | Trapped-volume takeoff | `sprinkler-system-volume-takeoff` |
| `fp/sprinkler-temperature-and-k.md` | Ambient limit, K-factor, 7 psi floor | `occupancy-hazard-fork` |
| `fp/concealed-spaces.md` | Combustible concealed space and cloud ceilings | `containment-ceiling-and-obstruction-coverage` |
| `fp/water-delivery-screen.md` | Volume caps and 60 s / 30 s clocks | `dry-preaction-water-delivery-screen` |
| `fp/preaction-trim-and-sequence.md` | Trim collision and releasing sequence | `preaction-el-el-trim-election`, `preaction-releasing-c-and-e-soo` |
| `fp/air-maintenance.md` | Relief, 5 psi margin, listed compressor | `nitrogen-inerting-and-c-factor-gate` |
| `fp/nitrogen-compressor-and-c-factor.md` | C = 100, two-number fill | `nitrogen-inerting-and-c-factor-gate` |
| `fp/nitrogen-sampling.md` | Remote-end purity, leak test, not a C-factor | `nitrogen-inerting-and-c-factor-gate` |
| `fp/storage-design.md` | FM storage rows, hose steps, dry column | `occupancy-hazard-fork` |
| `fp/storage-families.md` | ESFR wet-only, CMSA, CMDA 30 percent | `occupancy-hazard-fork` |
| `fp/ignitable-liquid-sprinklers.md` | Water density, drainage, containment | `occupancy-hazard-fork` |
| `fp/pump-and-supply.md` | Supply curve and pump envelope | `hydrant-supply-curve`, `pump-envelope` |
| `fp/supply-test.md` | Pitot test, deductions, two suction numbers | `hydrant-supply-curve` |
| `fp/water-supply-reliability.md` | Adequate versus reliable, enhanced ladder | `hydrant-supply-curve` |
| `fp/water-tanks.md` | Suction tank, break tank, 4020 listing | `hydrant-supply-curve` |
| `fp/fire-pump-installation.md` | Pump count, usable curve, suction, diesel tank | `pump-envelope` |
| `fp/fire-pump-controller.md` | Controller signals and refuse list | `fire-pump-controller-configuration-and-supervision` |
| `fp/fire-pump-alarm-interface.md` | Terminals versus the insurer list, transfer outage | `fire-pump-controller-configuration-and-supervision` |
| `fp/fire-pump-power-circuit.md` | No ground-fault protection, campus-feeder coordination | `fire-pump-controller-configuration-and-supervision` |
| `fp/jockey-pump.md` | Leakage pump setpoints and sensing line | `fire-pump-controller-configuration-and-supervision` |
| `fp/variable-speed-pump.md` | Churn ceiling and speed limiting | `pump-envelope` |
| `fp/pump-power-testing.md` | Infrared, transfer switch, fuel, flush flows | `fire-pump-controller-configuration-and-supervision` |
| `fp/control-valves.md` | Suction gate, butterfly friction, 175 psi plateau | `fire-pump-controller-configuration-and-supervision` |
| `fp/pressure-regulating-devices.md` | Avoid a sprinkler reducing valve, dry-side ban | `pump-envelope` |
| `fp/backflow-preventer.md` | Tier, certified loss, full-flow test path | `hydrant-supply-curve` |
| `fp/standpipe-class-i.md` | Class I residual and supervisory air | `standpipe-class-i-election-and-demand` |
| `fp/standpipe-system.md` | Gallon demand, who supplies it, test drain | `standpipe-class-i-election-and-demand` |
| `fp/campus-loop-and-fire-flow.md` | Loop and needed-fire-flow method | `campus-looped-main-sizing`, `needed-fire-flow-method-election` |
| `fp/private-fire-mains.md` | Pipe, hydrants, one-leg-out delta, flush | `campus-looped-main-sizing` |
| `fp/thrust-restraint.md` | Test pressure, restrained length, encasement | `campus-looped-main-sizing` |
| `fp/needed-fire-flow.md` | ISO cap, rejected formulas, hydrant credit | `needed-fire-flow-method-election` |
| `fp/hydraulic-method.md` | Diameter, remote-area length, C reporting | `pump-envelope` |
| `fp/duct-smoke.md` | 2,000 cfm and 15,000 cfm triggers by code | `fa-hvac-door-and-lock-interfaces` |
| `fp/waterflow-supervision.md` | 90 s device limit, 60 s receipt, two-turn valve | `fa-fire-pump-and-preaction-supervisory-points` |
| `fp/fm-detection-install.md` | DS 5-48 spacing, airflow fence, heat default | `fa-spot-smoke-spacing-airflow-and-beams` |
| `fp/fm-alarm-sheet.md` | September 2007 alarm sheet, what to reconcile | `fa-secondary-power-battery-calc` |
| `fp/vewfd-acceptance.md` | Heated-wire test, 120 s, pre-alarm opens the valve | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fp/asd-commissioning.md` | Return openings, hole cap, 70 percent balance | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fp/stratification.md` | High-ceiling screen, annex example, no hand formula | `fa-spot-smoke-spacing-airflow-and-beams` |
| `fp/gas-detection.md` | Power and placement versus occupancy setpoints | `ess-isolation-venting-and-duration` |
| `fp/errcs.md` | Public-safety radio coverage to confirm in the adopted fire code | `fa-pathway-survivability-election` |
| `fp/alarm-service-class.md` | FM Class V and Class VIA, not pathway class | `fa-integrated-systems-test-matrix` |
| `fp/seismic-bracing.md` | Brace spacing ceiling and FM Cp when S_DS is unknown | `fp-seismic-bracing-and-restraint` |
| `fp/post-earthquake-supply.md` | Public-main outage as a second-source driver | `fp-seismic-bracing-and-restraint` |
| `fp/fuel-seismic-shutoff.md` | Fuel-gas brace spacing and shutoff time | `fp-seismic-bracing-and-restraint` |
| `fp/freeze-heat-trace.md` | Freeze screen, listing fence | `freeze-heat-trace-fp-piping` |
| `fp/cold-climate-freeze.md` | 100-year map, 40 °F spaces, diesel room | `freeze-heat-trace-fp-piping` |
| `fp/heat-trace-supervision.md` | Branch-line listing and energized-circuit supervision | `freeze-heat-trace-fp-piping` |
| `fp/itm-testability.md` | CD testability levers | `itm-design-for-testability` |
| `fp/acceptance-tests.md` | Hydrostatic, leak, witnessed 30 s delivery | `commissioning-ist-acceptance-packet` |
| `fp/impairment-and-hot-work.md` | Impairment closeout and hot-work distances | `itm-design-for-testability` |
| `fp/construction-safeguards.md` | Sprinklers in service before combustibles | `itm-design-for-testability` |
| `fp/preincident-environment.md` | Freeze, flood, and snow plan triggers | `freeze-heat-trace-fp-piping` |
| `fp/controls-separation.md` | Fire and gas paths off the business network | `fa-code-edition-delta-check` |
| `fp/transformer-siting.md` | Indoor room, containment datum, roof exposure | `power-block-transformer-water-spray` |
| `fp/mv-switchgear-room.md` | Room package above 1,000 V, no lineup deluge | `mv-switchgear-room-package` |
| `fp/cable-trays.md` | Cable-only 0.2 gpm/ft² over 3,000 ft² | `mv-switchgear-room-package` |
| `fp/lightning-and-surge.md` | Shield angle, 1 ohm ground, 20 percent margin | `mv-switchgear-room-package` |
| `fp/generator-plant.md` | DS 5-23 arrangement, density on DS 7-32 | `combustion-air-and-hall-free-area` |
| `fp/diesel-fuel-handling.md` | Receiving geometry and emergency fuel shutoff | `hydrant-supply-curve` |
| `fp/non-lithium-battery-rooms.md` | Hazard category 2, 1-hour room, hydrogen floor | `occupancy-hazard-fork` |
| `fp/battery-room-hydrogen.md` | Current-based airflow versus 1 cfm/ft² | `most-stringent-basis-matrix` |
| `fp/hydrogen-equipment-rooms.md` | Bulk hydrogen outdoors, equipment-room ventilation | `most-stringent-basis-matrix` |
| `fp/ess-room-sprinklers.md` | 0.30 gpm/ft² over the room, 45 min times racks | `pump-envelope` |
| `fp/ess-explosion-control.md` | 10 percent trip, 2.5 cfm/ft² floor, propane envelope | `ess-isolation-venting-and-duration` |
| `fp/damage-limiting-construction.md` | Group C vent ratio, exterior-wall preference | `ess-isolation-venting-and-duration` |
| `fp/li-ion-bbu.md` | 20 kWh sheet loop and in-rack barriers | `density-area-dry-increase` |
| `fp/li-ion-storage.md` | State-of-charge gates for modules at rest | `storage-staging-sprinkler-design` |
| `fp/liquid-cooled-halls.md` | Coolant fork before the hall density moves | `liquid-cooled-escaped-liquids-leak-detect` |
| `fp/telecom-rooms.md` | NFPA 76 area test, water basis on an FM hall | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fp/plant-control-room.md` | 1-hour control room, hazard category by height | `most-stringent-basis-matrix` |
| `fp/hall-power-isolation.md` | FM isolation before water, test mode | `power-isolation-disconnect-control` |
| `fp/compartmentation.md` | Fire barrier versus fire wall, door for the rating | `fire-area-compartmentation-schedule` |
| `fp/firestops.md` | Listed system number, F versus L rating | `fire-area-compartmentation-schedule` |
| `fp/dampers.md` | Dynamic dampers where fans stay running | `fa-hvac-door-and-lock-interfaces` |
| `fp/exhaust-ducts.md` | When industrial-exhaust rules do not apply | `ess-exhaust-duct-shaft-and-duct-sprinklers` |
| `fp/mfl-evaluation.md` | Impaired-sprinkler loss scenario | `fire-area-compartmentation-schedule` |
| `fp/mfl-walls.md` | 4-hour wall, separation product, 3-hour doors | `fire-area-compartmentation-schedule` |
| `fp/campus-exterior-exposure.md` | Building, yard, and wildland exposure | `campus-looped-main-sizing` |
| `fp/smoke-purge.md` | Outside-air purge rate, upstream detector null | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fp/stair-pressurization.md` | Door force versus the pressure band | `fa-hvac-door-and-lock-interfaces` |
| `fp/ground-mounted-pv.md` | Access, hail, no ballasted ground mount | `most-stringent-basis-matrix` |
| `fp/roof-mounted-pv.md` | Class 1A lost under modules, array geometry | `most-stringent-basis-matrix` |
| `fp/ufc-electronic-equipment.md` | Defense wet-pipe electronic area, comparison only | `most-stringent-basis-matrix` |
| `fp/incident-mechanisms.md` | Smoke loss and undesigned isolation, 1993–2006 | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fa/edition-deltas.md` | I-Code to NFPA 72 pairing and section moves | `fa-code-edition-delta-check` |
| `fa/three-layer-basis.md` | Code, insurer, and owner for fire alarm | `most-stringent-basis-matrix` |
| `fa/when-a-system-is-required.md` | §907, waterflow supervision, duct trigger | `fa-code-edition-delta-check` |
| `fa/documentation-package.md` | Chapter 7 list, sequence, record of completion | `fa-code-edition-delta-check` |
| `fa/cybersecurity.md` | Chapter 11 levels and external connections | `fa-code-edition-delta-check` |
| `fa/detection-layout.md` | Spot smoke, sampling, two levels, containment | `fa-spot-smoke-spacing-airflow-and-beams`, `fa-asd-vewfd-data-hall-sampling-layout` |
| `fa/asd-performance.md` | 120 s, 60 s, and 90 s transport; NFPA 76 areas | `fa-asd-vewfd-data-hall-sampling-layout` |
| `fa/heat-detector-spacing.md` | 0.7S, joists, beams, ceiling-height factor | `fa-spot-smoke-spacing-airflow-and-beams` |
| `fa/space-detection-matrix.md` | Detection and notification by space | `fa-spot-smoke-spacing-airflow-and-beams` |
| `fa/ess-room-detection.md` | Smoke, 10 percent and 25 percent gas, standby hours | `ess-isolation-venting-and-duration` |
| `fa/bess-separation.md` | 2-hour energy-storage room separation | `fire-area-compartmentation-schedule` |
| `fa/generator-room.md` | Heat detection and fuel-tank permission | `fa-secondary-power-battery-calc` |
| `fa/pathway-class.md` | Class A, B, N, and X, 200 s, 10 ft / 1,000 ft² | `fa-pathway-survivability-election` |
| `fa/pathway-survivability.md` | Levels 0 through 4 and NEC Article 760 | `fa-pathway-survivability-election` |
| `fa/nac-and-wire.md` | NAC drop method, 2025-only code text | `fa-nac-voltage-drop-check`, `fa-nec-table-8-wire-sizing` |
| `fa/notification-appliances.md` | 15 dB / 5 dB, 110 dBA, corridor visible rules | `fa-nac-voltage-drop-check` |
| `fa/supervising-station.md` | Service types, 90 s, 60 min and 6 h paths | `fa-integrated-systems-test-matrix` |
| `fa/di-releasing.md` | Double-interlock cause and effect | `fa-double-interlock-releasing-cause-and-effect` |
| `fa/releasing-panel.md` | Listed releasing unit, physical disconnect, program logic | `fa-double-interlock-releasing-cause-and-effect` |
| `fa/preaction-supervision.md` | Manual release, test detector, 1,000-head cap reading | `preaction-releasing-c-and-e-soo` |
| `fa/supervisory-points.md` | Pump and preaction point class | `fa-fire-pump-and-preaction-supervisory-points` |
| `fa/secondary-power.md` | Standby hours, aging factor, door-lock load | `fa-secondary-power-battery-calc` |
| `fa/epo-and-disconnect.md` | Article 645, NFPA 75 disconnect, 3 ft / 20 ft, doors | `power-isolation-disconnect-control` |
| `fa/interfaces.md` | Elevator, HVAC, signals, and power isolation | `fa-elevator-recall-and-shunt-trip`, `power-isolation-disconnect-control` |
| `fa/smoke-control-interface.md` | IBC §909 interface and NFPA 92 pressure | `fa-hvac-door-and-lock-interfaces` |
| `fa/acceptance-testing.md` | Chapter 14 frequencies and NFPA 4 team | `fa-integrated-systems-test-matrix`, `commissioning-ist-acceptance-packet` |
