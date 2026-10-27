---
name: Power-block transformer water spray
description: >-
  Use when an outdoor oil-filled transformer needs separation or barrier
  decisions and, when spray is required, apparatus water-spray demand,
  standoff, hose, duration, and oil containment. Not white-space density times
  area, not a metal-clad switchgear lineup, and not a genset-room density.
---

# Power-block transformer water spray

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** The building sprinkler basis of design stays wet pipe, dry pipe, or double-interlock preaction. This method sizes outdoor oil-filled transformer water spray. It does not replace the building system. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Classify the object first. Outdoor oil-filled transformers are a separation, barrier, and water-spray problem (FM DS 5-4 and the water-spray method in FM DS 4-1N). Indoor dry-type gear and metal-clad switchgear are a room problem. Diesel generator rooms are an arrangement problem on another sheet. Do not copy transformer surface density onto a generator, and do not copy white-space density onto a transformer.

Do not invent oil gallons or a protected area. Do not freeze a nozzle SKU. Do not draw nozzle coordinates.

## Editions

| Instrument | Role | Pin |
|---|---|---|
| FM DS 5-4 | Transformer densities, geometry, hose, containment volume | July 2019 / interim revision October 2020 |
| FM DS 4-1N | Water-spray method, nozzles, pressure, duration alignment | May 2010. Does not replace DS 5-4 densities. |
| FM DS 2-0 | Installation of the spray piping | Companion. Cite the edition opened on the job. |
| FM DS 5-19 | Switchgear room. Not this spray. | October 2020 / interim revision January 2024 |
| FM DS 5-23 | Generator arrangement | July 2020 / interim revision January 2022. Density often from DS 7-32. Hand that density off. |
| FM DS 7-32 | Ignitable-liquid operations. Generator-room density table only. Not transformer spray. | April 2020 / interim revision April 2026 |
| IEEE Std 980 and FM DS 7-83 | Oil containment and drainage references | Cite the edition opened on the job. |
| NFPA 15 | Code-floor surface density. Section numbers that are not opened stay unpinned. | Adopted edition. Delta versus the public 0.25 gpm/ft2 surface figure is directional until the section is opened. |
| NFPA 13-2025 | Room protection only. Not the yard spray. | 2025 |

## Object fence

| Object | This method | Not this method |
|---|---|---|
| Outdoor oil-filled transformer | 0.30 gpm/ft2 on surfaces, 0.20 gpm/ft2 on an exposed wall when wall spray is elected, simultaneous units, containment | White-space 0.20 gpm/ft2 over 2,500 ft2 |
| Indoor transformer with an FM Approved fluid | Whole-room sprinkler 0.20 gpm/ft2 (DS 5-4 §2.2.3), under wet, dry, or double-interlock. Hand the demand to `density-area-dry-increase`. | Outdoor 0.30 gpm/ft2 used indoors |
| Indoor fluid that is not FM Approved | No density from DS 5-4. Mark unpinned. Do not invent 0.30 gpm/ft2. | A guessed indoor density |
| Dry-type or metal-clad switchgear | Room package | Water spray on the lineup |
| Diesel generator room | Arrangement on DS 5-23. Density via DS 7-32 when that sheet controls. Hand the density off. | Transformer 0.30 gpm/ft2 copied onto the generator |

An FM Approved transformer (approval standard 3990) can drop protection and separation to about 3 ft (DS 5-4 §3.3). An FM Approved fluid in a transformer that is not itself approved does not buy that relief. Fluid approval is not transformer approval.

Indoor sheet options that name foam, water mist, or a gaseous agent are out of scope. Prefer dry-type equipment or a room wet, dry, or double-interlock system.

## Geometry first

DS 5-4 §2.3.1 offers plain separation, a 2-hour barrier, a 3-hour barrier, spray on the transformer, or spray on the wall. Do not paste a second copy of Tables 5 through 8 here. Open those tables on the job. Headlines:

- Measure distance from the inside edge of containment. A 5 ft perimeter at or under 1,000 gal, or 8 ft over 1,000 gal, stacks on the tabulated separation.
- Approved transformer: about 3 ft to a wall or a neighbor, and fixed protection may not be required.
- Liquid that is not approved: on the order of 5 to 100 ft to a wall and 5 to 50 ft to a neighbor, by volume tier. Read the opened table. Do not freeze those bounds as a substitute for the table.
- If the transformer-to-transformer table is missed, a 2-hour barrier between transformers extends 1 ft vertically and 2 ft horizontally beyond fault-pressurizable components.
- A barrier or spray alternative can pull in a roof-radiation check. A building is "not exposed" at any oil volume only when it is at least about 50 ft tall. A single-story hall fails that test.
- Spacing tables control fire exposure. They are not blast control.

If geometry fails, or the carrier or owner still requires spray, continue.

## Spray demand

FM DS 5-4 §2.3.2, July 2019 / interim revision October 2020:

| Target | Density |
|---|---|
| Transformer surfaces, except the underside | 0.30 gpm/ft2 (12 mm/min), §2.3.2.1.A |
| Exposed building wall, when wall spray is the alternative | 0.20 gpm/ft2 (8 mm/min) over the wall area the sheet's table defines, §2.3.2.2.A |
| Code-floor surfaces, when NFPA 15 is the comparison | 0.25 gpm/ft2 on surfaces is the public comparison figure. Ground coverage at 0.15 gpm/ft2 stays unpinned until the adopted section is opened. |

Protected area is the projected surface of tank, radiators, and conservator. Exclude the underside. Exclude bushings.

```
Arect = (L*W) + 2*(L*H) + 2*(W*H)
Aprot = sum of Arect over protected elements
Qunit = 0.30 * Aprot
```

Insurer delta versus a 0.25 gpm/ft2 floor: (0.30 - 0.25) / 0.25 = 20 percent. Example only, not a default: 1,666 ft2 at 0.30 gpm/ft2 is 500 gpm, and the same area at 0.25 gpm/ft2 is 417 gpm.

Simultaneous demand (DS 5-4 §2.3.2.1): size the system and the supply for the transformer of origin plus the adjacent transformer on each side at the same time. In a three-unit row that is origin plus two neighbors. If the sheet is silent on whether a neighbor takes 0.30 or 0.20 gpm/ft2, compute both and carry the larger for supply. Mark that fork as an inference. Verify with the engineer of record.

Hardware, all required (DS 5-4 §2.3.2.1):

- Piping and nozzles at least 18 in (45 cm) off the transformer.
- No piping over the top or the relief vents.
- No direct spray on bushings.
- Equipment per DS 4-1N. Install per DS 2-0.
- Two nozzle levels, upper and lower, same standoff.
- Wall spray: direct impingement, or rundown with at most 10 ft between levels. Nozzle spacing from the manufacturer's tables.

DS 4-1N, May 2010, after the density math:

| Rule | Pin |
|---|---|
| Minimum nozzle pressure | 20 psi (1.4 bar) |
| Outdoor orifice under 1/2 in | 30 psi (2.2 bar) |
| Outdoor orifice at or over 1/2 in | at least 20 psi |
| Open-nozzle extinguishment mains | Do not galvanize |
| Remote transformer duration | at least 60 minutes |
| Systems at or over 2,000 gpm | size for one pump out of service |
| Large or windy yards | prefer large-capacity nozzles |

A vendor minimum near 10 psi does not replace the 20 psi or 30 psi floor. Pattern data are still-air data. Add a wind allowance outdoors. Do not interpolate a pattern table past its printed axial distance. Small orifices need a listed strainer. Finish can limit approval: a corrosion-resistant plating may be listed to one laboratory and not approved by the insurer. Check the submittal. Do not freeze a model number.

Do not use an open-tank spray table as a transformer or generator-yard density.

Hose, where transformers expose buildings or equipment (DS 5-4 §2.3.2.3):

| Fluid and volume | Hose | Duration |
|---|---|---|
| FM Approved liquid, or mineral oil at or under 1,000 gal | 250 gpm | 1 hour |
| Mineral oil over 1,000 gal in one transformer | 500 gpm | 2 hours |

Duration drives the water supply, not only the containment volume.

## Containment

Outdoor (DS 5-4 §2.2.1.4, §2.2.1.5, and §2.3.1.4, with IEEE 980):

```
Vcontain >= Voil + 60 * (Qhose + sum of simultaneous spray flows)
```

Use the hose tier above. Assume adjacent sprays run with the origin. Perimeter at least 5 ft at or under 1,000 gal, or 8 ft over 1,000 gal, beyond fluid-containing parts, including external coolers. Provide rainwater removal. Separate containment per transformer. Environmental spill rules, including a federal spill plan, are outside DS 5-4 and are often the larger volume. Size the fire-protection volume here and flag the environmental volume separately.

Indoor: a curb at least 3 in, separate per transformer. A containment term that depends on a special-protection discharge rate is out of scope. Do not design that agent. Prefer dry-type equipment or a room wet, dry, or double-interlock system. A double wall is not containment credit on the generator sheet (DS 5-23). Do not treat it as containment here either.

## Campus demand

The governing event is the larger of simultaneous transformer spray plus its hose, or generator spray plus its hose, when both exist. Duration follows the hose tier, and is at least 60 minutes on a remote transformer. Hand demand and duration to `hydrant-supply-curve` and `pump-envelope`. Do not freeze a pump nameplate here. Do not freeze campus demand on a white-space 750 gpm.

Alarm, trip, and de-energize before or with any water on energized apparatus. Do not write the full matrix here. Hand it to `preaction-releasing-c-and-e-soo` and `power-isolation-disconnect-control`. Generator fuel stop and ventilation shutdown are an NFPA 37 interface. Combustion-air openings go to `combustion-air-and-hall-free-area`.

## Output

Object class; edition pins; geometry result (spray required, replaced by separation or barrier, or owner-required); protected area and flow at 0.30 gpm/ft2 with the 20 percent delta; simultaneous flow and which neighbor density was carried; hardware checklist; hose tier and duration; containment gallons; campus handoff; delta versus NFPA 15 and, for rooms only, versus NFPA 13-2025; ASSUMED and unpinned list.

## Out of scope

Foam, clean agent, water mist, and single-interlock or non-interlock as the building sprinkler basis of design. Canada is out of scope. Water spray on a metal-clad switchgear lineup. Using DS 7-32 as transformer spray. Using indoor 0.20 gpm/ft2 as outdoor 0.30 gpm/ft2, or the reverse. Invented oil volume or protected area. Nozzle coordinate drawings. A gaseous agent for an indoor transformer.

## Handoffs

| Work | Handoff |
|---|---|
| Switchgear room | `mv-switchgear-room-package` |
| Indoor room density | `density-area-dry-increase` |
| Generator free area | `combustion-air-and-hall-free-area` |
| Campus supply and pump | `hydrant-supply-curve`, `pump-envelope` |
| De-energize and releasing | `power-isolation-disconnect-control`, `preaction-releasing-c-and-e-soo` |
| Sprinkler family for rooms | `suppression-technology-selection` |
