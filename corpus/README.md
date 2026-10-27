# corpus

Paraphrased decision logs and edition pins for a later search pass. One topic per file. The desktop app does not read this folder yet.

This folder holds 72 notes: `scope-lock.md`, `design-conventions.md`, 44 files in `fp/`, and 26 files in `fa/`. The first 19 were the seed (the scope lock, 13 fire-protection notes, and 5 fire-alarm notes). The rest are paraphrased from topic notes and stripped of job names, personal names, and source-archive paths.

They are not a reprint of a standard. A numeric screen sits next to its edition and section. Where a licensed primary is not held, the note says `[V]` and does not invent a section.

Out of this folder: raw standards text, vendor catalogs, source-pull archives, job names, client names, and personal names. Foam, clean agent, and water mist are out of scope (the guard is in `scope-lock.md` only). A building deluge system is out of scope. Outdoor oil-filled transformer apparatus water spray (NFPA 15-style) is allowed and is sized in `power-block-transformer-water-spray`. Jurisdictions outside the stated NFPA, IBC, and IFC basis are out of scope. Canada stays out of scope. Single-interlock and non-interlock preaction are comparison-only. They are never the basis of design.

Company systems in these notes: wet pipe, dry pipe, and double-interlock preaction, outdoor oil-filled transformer apparatus water spray, plus pumps, nitrogen, compressors, and the Division 21 and Division 28 fire-alarm work those systems need.

Spec language is not here. When specs are ingested, double-interlock draft language belongs in CSI 21 13 19.

## Folder map

| Path | Count | What the folder holds |
| --- | --- | --- |
| scope-lock | 1 | Wet, dry, and double-interlock fence, plus outdoor transformer water spray |
| design-conventions | 1 | How a number is chosen, cited, and not copied from another hall |
| fp/ | 44 | Water-based suppression, detection that serves it, insurer sheets, and design practice |
| fa/ | 26 | Fire alarm, releasing, power, pathways, notification, and space detection |

`fp/` groups as: edition and election (`edition-pins.md`, `system-election.md`, `sheet-precedence.md`, `ufc-outside-pin.md`); hall and pipe (`hall-geometry.md`, `density-area.md`, `pipe-layout.md`, `pipe-volume.md`, `sprinkler-temperature-and-k.md`, `concealed-spaces.md`); dry and preaction (`water-delivery-screen.md`, `preaction-trim-and-sequence.md`, `air-maintenance.md`, `nitrogen-compressor-and-c-factor.md`, `nitrogen-sampling.md`); storage and liquids (`storage-design.md`, `storage-families.md`, `ignitable-liquid-sprinklers.md`); water supply hardware (`pump-and-supply.md`, `fire-pump-controller.md`, `pump-power-testing.md`, `control-valves.md`, `standpipe-class-i.md`, `campus-loop-and-fire-flow.md`, `hydraulic-method.md`); detection and alarm (`duct-smoke.md`, `waterflow-supervision.md`, `fm-detection-install.md`, `fm-alarm-sheet.md`, `vewfd-acceptance.md`, `asd-commissioning.md`, `stratification.md`, `gas-detection.md`, `errcs.md`, `alarm-service-class.md`); installation and upkeep (`seismic-bracing.md`, `fuel-seismic-shutoff.md`, `freeze-heat-trace.md`, `itm-testability.md`, `acceptance-tests.md`, `impairment-and-hot-work.md`, `construction-safeguards.md`, `preincident-environment.md`, `controls-separation.md`).

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
| `fp/fire-pump-controller.md` | Controller signals and refuse list | `fire-pump-controller-configuration-and-supervision` |
| `fp/pump-power-testing.md` | Infrared, transfer switch, fuel, flush flows | `fire-pump-controller-configuration-and-supervision` |
| `fp/control-valves.md` | Suction gate, butterfly friction, 175 psi plateau | `fire-pump-controller-configuration-and-supervision` |
| `fp/standpipe-class-i.md` | Class I residual and supervisory air | `standpipe-class-i-election-and-demand` |
| `fp/campus-loop-and-fire-flow.md` | Loop and needed-fire-flow method | `campus-looped-main-sizing`, `needed-fire-flow-method-election` |
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
| `fp/fuel-seismic-shutoff.md` | Fuel-gas brace spacing and shutoff time | `fp-seismic-bracing-and-restraint` |
| `fp/freeze-heat-trace.md` | Freeze screen, listing fence | `freeze-heat-trace-fp-piping` |
| `fp/itm-testability.md` | CD testability levers | `itm-design-for-testability` |
| `fp/acceptance-tests.md` | Hydrostatic, leak, witnessed 30 s delivery | `commissioning-ist-acceptance-packet` |
| `fp/impairment-and-hot-work.md` | Impairment closeout and hot-work distances | `itm-design-for-testability` |
| `fp/construction-safeguards.md` | Sprinklers in service before combustibles | `itm-design-for-testability` |
| `fp/preincident-environment.md` | Freeze, flood, and snow plan triggers | `freeze-heat-trace-fp-piping` |
| `fp/controls-separation.md` | Fire and gas paths off the business network | `fa-code-edition-delta-check` |
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
