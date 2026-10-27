---
name: ESS exhaust duct, shaft and duct sprinklers
description: >-
  Use when a Li-ion ESS or UPS battery room has an explosion-control or gas
  exhaust duct and you must decide the duct path (IMC 509 hazardous exhaust or
  not), its dampers, shaft and penetration ratings, and whether duct sprinklers
  are needed, then add their demand to the room wet, dry, or double-interlock
  demand. Not exhaust cfm sizing, not room density, not gas-detection cause
  and effect.
---

# ESS exhaust duct, shaft and duct sprinklers

**Intake.** A missing input is ASSUMED (the value and why). Do not present an ASSUMED value as a cited code value. **Scope lock.** Wet pipe, dry pipe, or double-interlock preaction only. Dry and double-interlock systems use a nitrogen generator and compressor and C = 100. Foam, clean agent, water mist, and single-interlock are out of scope. Record and stop. Do not size them here. Cite the section and the edition. Three-layer basis (code, insurer, owner). Most stringent wins per parameter. Report the delta versus NFPA 13-2025. Show the arithmetic. Verify judgment calls with the engineer of record. Do not claim a stamp. Generic room only.

## 1. Code path fork (run first)

Why the exhaust exists:

- IFC 2024 Table 1207.6 does not require §1207.6.1 exhaust ventilation for Li-ion.
- It does require §1207.6.3 explosion control. The exhaust is usually the NFPA 69 path: detection at 10 percent of LFL starts the exhaust, which holds the room at or below 25 percent of LFL.

Record which basis drives the exhaust: §1207.6.3 and NFPA 69, FM DS 5-33 §2.5.5, the listing, or a local amendment. Verify with the engineer of record: exhaust may also be required elsewhere in the code (§1207.6.1). Do not delete exhaust on the Table 1207.6 "No" alone.

IMC 509 applicability:

- IMC 2024 §509.2 triggers where hazardous materials under normal operating conditions exceed 25 percent of LFL. A textual reading says Li-ion does not trigger it.
- Apply §509 anyway. That is the conservative choice. Verify with the engineer of record and the AHJ.

## 2. Schedule (IMC 2024, when §509 is applied)

| Item | Rule | Cite |
|---|---|---|
| Fire and smoke dampers | None. Prohibited | IMC 2024 §509.6.1 |
| Balancing dampers | None. Balance by duct sizing. Verify with the engineer of record | IMC 2024 §509.5.1 |
| Wall penetration | Enclose from the penetration to the outlet. Rating at least the highest wall penetrated, unless the duct interior is sprinklered | IMC 2024 §509.6.3 |
| Floor or roof penetration | Rated shaft, matching the room (2 h when the room is 2 h) | IMC 2024 §509.6.2; IBC 2024 §713.4 |
| Common shaft | Not allowed. Dedicated shaft | IMC 2024 §509.4 |
| Makeup air | About equal to exhaust, interlocked | IMC 2024 §509.5.5 |
| Discharge | Directly outdoors | IMC 2024 §509.5.7 |
| Duct material | Per Table 509.8 (for example, 9 in to 18 in nonabrasive = 0.034 in G90) | IMC 2024 §509.8 |
| Duct sprinklers | Required unless the largest cross-section is under 10 in (a 10 in duct is still required) | IMC 2024 §509.7 Exception 3 |

Trade-off: if you omit duct sprinklers (under 10 in), §509.6.3 makes the rated enclosure run the full length. If the duct is sprinklered, the wall enclosure may be dropped, but not the floor shaft. Conservative choice: keep both. Verify with the engineer of record.

## 3. Duct sprinkler layout and demand (NFPA 13-2025)

- Horizontal runs: heads on 10 ft centers, first head at most 5 ft from the entrance (§9.3.9.1.3).
- Vertical risers: one head at the top of each riser and one at the midpoint of each offset (§9.3.9.1.1). Exterior-riser exemption: no sprinkler in a vertical riser outside the building if it does not expose combustible material, or the interior of the building and the horizontal distance between the hood outlet and the riser is at least 25 ft [CODE NFPA 13-2025 §9.3.9.1.2]. The wording is cooking-hood based. Applying it to a Li-ion exhaust riser needs engineer-of-record verification. Noncombustible or limited-combustible nonaccessible vertical shafts need no sprinklers [§9.3.3.1.1].
- Listed line strainer ahead of duct heads smaller than K-2.8 [CODE NFPA 13-2025 duct-sprinkler text]. The subsection number is unpinned. Mark it and verify before use. K-factor 1.4 to 5.6 and extra-high temperature (§8.9.6.1 and §8.9.6.3) are commercial-cooking rules. Use them for Li-ion exhaust only as a judgment call. Verify with the engineer of record.
- Demand: minimum 7 psi at each head, all heads flowing (§19.2.3.4.3). Use K 1.4 to 5.6.
- Show the arithmetic: q = K times the square root of P. Example: K 5.6 times the square root of 7 is 14.82 gpm per head, so 4 heads is 59.3 gpm.
- Add the duct flow to the room demand from `density-area-dry-increase`.
- ITM: provide access to the heads.
- Freeze: check any roof or exterior run, and hand off to `freeze-heat-trace-fp-piping`.
- Supply: feed the duct heads from a wet branch even when the room is double-interlock. This is a judgment call. Verify with the engineer of record. Exclude the duct heads from the double-interlock trapped volume.

## 4. Handoffs

- Exhaust cfm and fans go to the mechanical designer and the NFPA 69 study. Do not size the fan here.
- Room density goes to `density-area-dry-increase`.
- Isolation, election, and gas-detection duration go to `ess-isolation-venting-and-duration`.
- Gas-detection relays and cause and effect go to `fa-bess-gas-relay-map-and-cause-effect`.
- Setpoints and head layout go to `fa-bess-gas-detection-layout-and-setpoints`.
- Double-interlock nitrogen and the compressor go to `nitrogen-inerting-and-c-factor-gate`.

Do not copy a worked room's cfm, head count, or gallons as a default.
