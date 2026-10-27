---
name: Liquid-cooled escaped liquids leak detect
description: >-
  Use when a direct-to-chip or CDU hall puts pressurized coolant at the racks
  and you must classify the coolant, then lay out below-equipment leak
  detection, containment, and the BMS or FACP intervention. Not sprinkler
  density times area, and not ASD pipe sizing.
---

# Liquid-cooled escaped liquids leak detect

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

This method classifies the coolant, then designs leak detection, containment posture, and intervention for a hall that already distributes pressurized coolant to every rack. It consumes the sprinkler family from `suppression-technology-selection`. It does not elect that family, resize density times area, or size an air-sampling network.

**Core rule.** Classification of the coolant governs. Nonignitable treated water or a propylene-glycol mix is a leak-detection problem on the white-space sprinkler basis. An ignitable heat-transfer fluid with an exposable pool is an ignitable-liquid problem. Do not invent a containment percent, a flash point, a differential-pressure trip, or a cable SKU.

## Editions

| Instrument | Role | Pin |
|---|---|---|
| FM DS 5-32 | Nonignitable liquid-cooled servers preferred. Leak detection in the cooling system or the room. White-space sprinklers stay unless the fork flips. | January 2026 |
| FM DS 7-32 | Only after flash point, fire point, and an exposable pool. Density and drainage are a handoff. | April 2020 / interim revision April 2026 |
| NFPA 30 | Ignitable-liquid classification when the fork opens. | 2024 unless the authority pins another year |
| NFPA 75 | ITE liquid-cooling text. Still maturing. Do not invent a containment percent from it. | 2024 |
| NFPA 13-2025 | Density delta lives on the density method, not here, unless the ignitable-liquid fork opens. | 2025 |
| OCP ACS Cold Plate, leak detection and intervention | Direct-to-chip taxonomy: indirect and direct sensing, voting, intervention ladder. No containment percent. | Rev 1.0, 2021 |
| OCP immersion requirements | At least 100 percent of the largest vessel. Immersion only. | Rev 2.10, 2023 |

A second carrier's escaped-liquid or below-equipment leak rule, when that carrier is in the basis, is corroboration. Cite the opened document. If the section is not opened, mark it unpinned. Do not import an FM number onto a job that carrier does not control.

## Coolant fork

Use the actual safety data sheet. Do not invent flash point or fire point.

| Result | Path |
|---|---|
| No measurable closed-cup flash point (aqueous direct-to-chip, treated water, propylene-glycol mix) | White-space sprinkler basis stays. This method is the leak layer. |
| Sealed two-phase dielectric, no exposable pool | White-space sprinklers stay. Add loss-of-fluid and integrity monitoring. |
| Flash point, no fire point | White space, plus a confined-release review. Mark unpinned. Verify with the engineer of record. |
| Flash point, fire point, and an exposable pool (open immersion hydrocarbon, ester, or similar) | Ignitable-liquid basis. Stop density here. Hand density and occupancy to `density-area-dry-increase` and `occupancy-hazard-fork` under NFPA 30 and FM DS 7-32. Keep leak and containment concepts. Do not emit a DS 7-32 density from this method. |

FM preference on an insured job: use a nonignitable liquid. Designing the coolant out of the fire problem is the cheapest lever. Foam, clean agent, and water mist stay out of scope on the ignitable-liquid branch. Do not read a special-protection option on DS 7-32 as permission to design those agents.

## Sensor architecture

Refuse a single-layer design. Direct rope or point sensors need coolant that touches the sensor and is electrically conductive.

| Coolant | Direct conductive rope or point |
|---|---|
| Propylene-glycol mix or other aqueous coolant | Valid |
| Dielectric, including many two-phase fluids | Not valid as the only direct layer. Lead with indirect, optical, level, and tray sensors. |

1. Indirect, non-contact. Differential pressure across the cooling pumps is the flagship. Also buffer or reservoir level, turbidity or optical buildup, and abnormal flow or temperature. The cold-plate document treats pump differential pressure as something that should be required. It gives no trip value. Do not invent psi. A large branch is blind to a slow drip, so the direct layer is not optional.
2. Level and make-up. Buffer-tank level catches the slow loss that differential pressure misses. Automatic make-up that silently refills defeats level detection. Lock out or alarm make-up runtime unless the owner standard says otherwise.
3. Direct. Point sensors at drip-pan low points, CDU internals, and quick-disconnect drip paths. Cable along pipes, under a raised floor, and under racks where the leak path is not a single point. Two-wire is yes or no. Four-wire locating maps to a tile or a zone. Specify flame resistance, chemical resistance, and bend radius by listing. Specify the function. Do not freeze a SKU.

Draw a leak-detection layout plan before installation. Hold-down clips at or under 6 ft, and a clip at every change of direction, are an attachment rule from a common locating-cable install guide. They are not a coverage pitch. A rule that the cable must sit within 3 ft of walls is not in that guide. Do not use it.

Voting, from the cold-plate document: with a tray point and a manifold cable, either sensor alarms the operator, and both are required before automatic intervention. No single sensor shuts the row down. Fix thresholds at commissioning.

## Intervention

Record the ladder. The owner elects the tier. Do not invent a shutdown.

| Tier | Action |
|---|---|
| 1 Manual | Notify and dispatch. Minimum everywhere. |
| 2 Automatic electrical | De-energize information technology in the zone. Stops power into a wet board. Does not stop the fluid. |
| 3 Automatic electrical and fluid | De-energize and shut the coolant branch or the CDU. State fail position and swing time. A row CDU can take many racks. Soft-shutdown before that drop. Enable the cold-plate thermal throttle. |

Reaction authority: node to the board controller, rack to the rack manager or rack CDU, row to the row CDU and the building management system. Cooling-loop leaks get an escalated alarm. Blind automatic shutoff of cooling can be the larger hazard. Define the response per leak type. Coordinate the branch shutoff with `power-isolation-disconnect-control`. Do not rewrite that method. Leak detection is usually management-system primary, with fire-alarm points as supervisory or alarm as the carrier and owner elect. Do not invent a sprinkler-releasing tie unless the sequence already pins one.

## Containment

1. If the owner standard pins a volume or a percent, use it and cite it.
2. Open immersion, when the immersion document applies: at least 100 percent of the largest single system or container, including interconnected volume. Reconcile drainage with FM DS 7-32 on the density handoff. Do not emit the density table here.
3. Direct-to-chip with no owner pin: do not invent 100 percent. The cold-plate document does not set one. Emit drip pans at high-risk fittings and the curbs or trenches coordinated with mechanical. A high-flow manifold break may not be containable for the whole event. Mark the volume unpinned.
4. Do not present a worked-example gallon value as a code default.

Refrigerant or pumped two-phase: ASHRAE 34 space volume per refrigerant mass is life safety, not sprinkler density. A consortium figure sometimes cited is at least 1,000 ft3 per 13 lb. Verify it against the adopted edition. Do not treat it as a sprinkler number.

## Output

Coolant class with the safety-data-sheet pins; white-space versus ignitable-liquid result; a sentence that this is a detection delta, not a density delta, or the density handoff if the fork flipped; three sensor layers and whether conductive sensing is valid; voting; intervention tier; containment pinned or unpinned; the struck 3 ft rule; open items.

## Out of scope

Foam, clean agent, water mist, and single-interlock or non-interlock as the sprinkler basis of design. Canada is out of scope. Density times area. Air-sampling ports and transport time. Invented containment percent, flash point, trip psi, or cable SKU. A cooling plant that does not put pressurized coolant at the racks.

## Handoffs

| Work | Handoff |
|---|---|
| Sprinkler family | `suppression-technology-selection` |
| Ignitable-liquid density and occupancy | `density-area-dry-increase`, `occupancy-hazard-fork` |
| Air sampling | `fa-asd-vewfd-data-hall-sampling-layout` (liquid cooling often lowers residual airflow; do not size ports here) |
| Power isolation | `power-isolation-disconnect-control` |
| Commissioning of layout and trip thresholds | `commissioning-ist-acceptance-packet` |
| Sensor inspection and test | `itm-design-for-testability` |
| Releasing sequence, if one is already pinned | `preaction-releasing-c-and-e-soo` |
