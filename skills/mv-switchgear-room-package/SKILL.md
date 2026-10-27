---
name: MV switchgear room package
description: >-
  Use when a room holds medium-voltage switchgear or circuit breakers above
  1000 V AC and you must apply the FM DS 5-19 room package: smoke to a
  constantly attended location, no storage, upstream high-side breaker outside
  the room, and a wet, dry, or double-interlock water path. Not outdoor
  transformer water spray, and not an information-technology emergency
  power-off.
---

# MV switchgear room package

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

This method owns the FM DS 5-19 room package for medium-voltage switchgear and circuit breakers. It consumes the sprinkler family from `suppression-technology-selection`. It does not elect that family. It does not invent a "DS 5-19 density." It does not put apparatus water spray on a metal-clad lineup. It does not treat room isolation as an information-technology emergency power-off.

**Core rule.** Classify the object first. Modern metal-clad switchgear with vacuum, air, or gas insulation, in a noncombustible room with no other combustibles, is a room problem (FM DS 5-19 §2.2.1, October 2020, interim revision January 2024). Do not spray the lineup. The sheet applies above 1000 V AC (§1.0). At or below 1000 V AC, do not cite §2.2 as the primary rule. Route that room to the low-voltage sheet or to ordinary room protection, and say so.

DS 5-19 does not publish a sprinkler density for the standard non-oil room. Density comes from NFPA 13, the occupancy, or FM DS 5-31 when grouped cable is the only combustible. Do not copy another room's area or demand onto this one.

## Editions

| Instrument | Pin |
|---|---|
| FM DS 5-19, switchgear and circuit breakers | October 2020, interim revision January 2024 |
| FM DS 5-31, grouped cable, when the cable fork opens | January 2020, interim revision October 2025. If that edition is not confirmed on the job, mark the cable density unpinned. |
| FM DS 5-48, smoke spacing | Not pinned in this pack. Mark spacing unpinned. Do not invent a foot spacing. |
| FM DS 5-4 | Outdoor oil-filled transformers. Not this room. Hand off. |
| NFPA 13-2025 | Room water-path delta. Not an apparatus-spray delta. |

## Object and voltage

| Object | Action |
|---|---|
| Metal-clad, vacuum, air, or gas-insulated gear in a noncombustible room with no other combustibles | Room package |
| Minimum-oil breaker, room noncombustible, no other combustibles | Treat as non-oil (DS 5-19 §2.2.1). Room package. |
| Bulk-oil breaker, or switchgear exposed to other combustibles | Open the oil fork below. Still not a transformer-yard spray. |
| Outdoor oil-filled transformer | `power-block-transformer-water-spray` |
| Information-technology hall shutdown | `power-isolation-disconnect-control` |
| Caller wants water spray on the metal-clad lineup | Stop. Wrong object (DS 5-19 §2.2.1). |

Unknown voltage is ASSUMED. State the value and why.

## Oil fork

FM DS 5-19 §2.2.3.1 lists, for indoor bulk oil or ignitable-liquid apparatus, automatic sprinklers, an approved gaseous agent, or water mist listed for enclosures with machinery, plus venting flammable vapor to the exterior, and a preference for air, gas, or vacuum insulation on new work.

Company path: the automatic sprinkler or preaction under wet, dry, or double-interlock is the permitted option. Gaseous suppression, water mist, and foam are out of scope. Recommend non-oil equipment. Do not invent an oil-path density. If gaseous suppression, water mist, or foam is offered as the basis of design, record it and stop.

Forced-air-cooled bus ducts (DS 5-19 §2.2.3.2): if cooling air is drawn from a fire-risk area, such as an outdoor oil-transformer yard, interlock the fan with the bus-duct breaker and with remote-area fire detection.

Portable extinguishers: Class A and Class C (DS 5-19 §2.2.3.4). The held edition skips §2.2.3.3. Do not invent that section.

## Room package

Record each item. Cites are FM DS 5-19, October 2020, interim revision January 2024.

| Element | Rule | Section |
|---|---|---|
| Construction | Noncombustible room. Gear separate from other hazardous equipment. | §2.2.1, §2.1.5.1 |
| Smoke | Photoelectric, or photoelectric plus ionization. | §2.2.4 |
| Destination | Alarm at a constantly attended location. Response includes people who can de-energize or diagnose. | §2.2.4 |
| Smoke versus sprinklers | Smoke does not remove the sprinklers. No omission credit. | §2.2.4 |
| Smoke spacing | DS 5-48. Unpinned in this pack. | §2.2.4 |
| Water | Sprinkler or preaction from the consumed family, the owner, DS 5-32, or NFPA 13. No density in DS 5-19. | none on this sheet |
| Isolation | Prefer the high-side breaker outside the room, accessible in an emergency. | §2.2.5 |
| Pre-incident plan | Electrical and firefighting respond together. De-energize so firefighting is not delayed. | §2.2.5 |
| Storage | No tools, supplies, or materials in the switch room or the enclosures. | §2.1.5.4 |
| Air | Slight positive pressure from filtered air. | §2.1.5.3 |
| Arc vents | Arc-resistant vents must not expose combustibles. Room venting against overpressure. | §2.1.5.2 |
| Section count | Arc-resistant, redundant, or physically separated tie. Otherwise preferably at least five horizontal sections between primary-selective breakers. This is an electrical bind, not a water density. | §2.3.5 |

Do not treat the upstream breaker as an information-technology emergency power-off. Do not invent button counts.

Electrical-room double-interlock is allowed only when `suppression-technology-selection` elected it. Do not invent double-interlock as the universal electrical-room default.

## Grouped cable

DS 5-19 §2.2.2 sends grouped combustible cable to FM DS 5-31.

| Condition | Action |
|---|---|
| Grouped cable is the only significant combustible | Cable-only ceiling: 0.2 gpm/ft2 over 3,000 ft2, 165 F, 130 ft2 spacing (DS 5-31 §2.3.2.2.B, January 2020 / interim revision October 2025). Cite it. If the edition is not confirmed, mark the row unpinned. |
| Oil breakers, storage, or transformers share the area | Do not use the cable-only density alone (DS 5-31 §2.3.2.2.C). |
| High trays obstruct the ceiling | Sprinklers in every aisle or walkway (DS 5-31 §2.3.2.2.1). Hand the layout to the density method. |
| A gaseous alternative for cable | Out of scope. Do not design it. |

Hand sealed density math to `density-area-dry-increase`. Do not paste 0.2 gpm/ft2 over 3,000 ft2 into a data hall without an occupancy check. A hazard classification from the occupancy method does not create a DS 5-19 density.

Do not take an NFPA 13 electrical-room omission on a high-availability room. Record that as design practice. Do not invent a section number for it.

## Surge pointer

If the gear is fed from exposed overhead circuits, station arresters or junction arresters may apply (FM DS 5-11, when that sheet is in the basis). A ground-electrode path at or under 1 ohm and short leads are the usual sheet limits. Surge protection is not a substitute for the room package. Do not size the arresters here.

## Output

Object, voltage, and oil result; room checklist with cites; cable fork or not applicable; isolation note; consumed sprinkler family and the density source (not DS 5-19); delta versus NFPA 13-2025 on the room water path; open items. Always restate that smoke is not permission to omit sprinklers.

## Out of scope

Foam, clean agent, water mist, and single-interlock or non-interlock as the sprinkler basis of design. Canada is out of scope. Lineup water spray. Outdoor transformer water spray. Information-technology emergency power-off. Invented DS 5-19 density, room area, or demand. Full releasing matrix.

## Handoffs

| Work | Handoff |
|---|---|
| Sprinkler family | `suppression-technology-selection` |
| Occupancy and hazard | `occupancy-hazard-fork` |
| Density, area, hose, duration | `density-area-dry-increase` |
| Hall shutdown and disconnect | `power-isolation-disconnect-control` |
| Outdoor transformer water spray | `power-block-transformer-water-spray` |
| Double-interlock releasing sequence | `preaction-releasing-c-and-e-soo` |
| Freeze-exposed piping | `freeze-heat-trace-fp-piping` |
| Room ventilation free area, when it is in scope | `combustion-air-and-hall-free-area` |
