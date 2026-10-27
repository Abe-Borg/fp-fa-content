---
name: ESS exhaust duct shaft and duct sprinklers
description: >-
  Use when a Li-ion energy-storage or battery room has an exhaust duct and you
  must choose the duct code path, dampers, shaft rating, and whether duct
  sprinklers are required, then add their flow to the room demand. Not fan
  airflow, not room density, and not the gas-detection sequence.
---

# ESS exhaust duct, shaft, and duct sprinklers

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

This method decides the exhaust duct's code path, its dampers, the shaft and penetration ratings, and the duct sprinklers, then adds that flow to the room's wet, dry, or double-interlock demand. It does not size exhaust airflow. It does not set room density. It does not write the gas-detection sequence.

## Code path

Record which basis drives the exhaust: IFC explosion control, NFPA 69, an insurer sheet, the listing, or a local amendment.

IFC 2024 Table 1207.6 does not, by that table alone, require §1207.6.1 exhaust ventilation for lithium-ion. It does require §1207.6.3 explosion control. The exhaust is often the NFPA 69 path: detection starts the exhaust and holds the room at or below 25 percent of the lower flammable limit. Verify with the engineer of record whether exhaust is also required elsewhere in the code. Do not delete the exhaust because the table says no.

IMC 2024 §509.2 applies where hazardous materials exceed 25 percent of the lower flammable limit under normal operating conditions. A reading of that sentence says a lithium-ion room does not trigger it, because off-gas is not normal operation. Design practice is to apply §509 anyway. That is the conservative choice. Verify with the engineer of record and the authority having jurisdiction.

## Schedule when §509 is applied

IMC 2024 unless noted.

| Item | Rule | Cite |
|---|---|---|
| Fire and smoke dampers | None. Prohibited. | §509.6.1 |
| Balancing dampers | None. Balance by duct size. | §509.5.1 is the basis. Verify with the engineer of record. |
| Wall penetration | Enclose from the penetration to the outlet. Rating at least the highest wall penetrated, unless the duct interior is sprinklered. | §509.6.3 |
| Floor or roof penetration | Rated shaft, matching the room (2 hours when the room is 2 hours). | §509.6.2 and IBC 2024 §713.4 |
| Common shaft | Not allowed. Dedicated shaft. | §509.4 |
| Makeup air | About equal to exhaust, and interlocked. | §509.5.5 |
| Discharge | Directly outdoors. | §509.5.7 |
| Duct material | Per Table 509.8. Example: 9 to 18 in, nonabrasive, 0.034 in G90. Read the opened table for other sizes. | §509.8 |
| Duct sprinklers | Required unless the largest cross-section is under 10 in. A 10 in duct is still required. | §509.7 exception 3 |

If the duct sprinklers are omitted because the duct is under 10 in, §509.6.3 keeps the rated enclosure for the full length. If the duct is sprinklered, the wall enclosure may be omitted. The floor shaft stays. Conservative assumption: keep both the sprinklers and the enclosure. Verify with the engineer of record.

## Duct sprinklers

NFPA 13-2025.

- Horizontal runs: heads on 10 ft centers. The first head is within 5 ft of the entrance (§9.3.9.1.3).
- Vertical risers: one head at the top of each riser and one at the midpoint of each offset (§9.3.9.1.1).
- An exterior-riser exemption exists for a cooking hood when the riser does not expose combustible material, or the interior, and the horizontal distance from the hood outlet to the riser is at least 25 ft (§9.3.9.1.2). That wording is a cooking-hood rule. Applying it to a lithium-ion exhaust riser is a judgment call. Verify with the engineer of record. A noncombustible, limited-combustible, nonaccessible vertical shaft may not need sprinklers (§9.3.3.1.1).
- Provide a listed line strainer ahead of duct heads smaller than K 2.8. The subsection for that strainer is not pinned in this pack. Mark it unpinned until the opened section is cited.
- K-factor 1.4 to 5.6 and extra-high temperature (§8.9.6.1 and §8.9.6.3) are commercial-cooking rules. Use them on a lithium-ion exhaust only as a judgment. Verify with the engineer of record.
- Demand: minimum 7 psi at every head, with all duct heads flowing (§19.2.3.4.3).
- Flow per head is K times the square root of pressure. Check: K 5.6 at 7 psi is about 14.8 gpm. Four heads are about 59 gpm. Use the heads actually specified.
- Add the duct flow to the room demand from `density-area-dry-increase`.
- Provide access for inspection and test.
- Any roof or exterior run goes to `freeze-heat-trace-fp-piping`.
- Feed the duct heads from a wet branch even when the room is double-interlock. That is a judgment. Verify with the engineer of record. Keep the duct heads out of the double-interlock trapped volume.

## Output

Which basis drives the exhaust; whether §509 is applied and why; damper, shaft, and sprinkler schedule; head count and added flow; wet-branch note; open items for the authority and the engineer of record.

## Out of scope

Foam, clean agent, water mist, and single-interlock or non-interlock as the sprinkler basis of design. Canada is out of scope. Exhaust cubic feet per minute and fan selection. Room density. Gas-detection relays. Nitrogen generator sizing.

## Handoffs

| Work | Handoff |
|---|---|
| Exhaust rate and fans | Mechanical designer, with `ess-isolation-venting-and-duration` for the code floor |
| Room density, hose, and duration | `density-area-dry-increase` |
| Gas detection layout and setpoints | `fa-bess-gas-detection-layout-and-setpoints` |
| Gas relays and sequence | `fa-bess-gas-relay-map-and-cause-effect` |
| Nitrogen and C-factor on a double-interlock room | `nitrogen-inerting-and-c-factor-gate` |
| Freeze | `freeze-heat-trace-fp-piping` |
