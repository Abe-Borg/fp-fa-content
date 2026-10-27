---
name: Storage staging sprinkler design
description: >-
  Use when a receiving, de-crate, staging, laydown, or spare-parts area is
  storage rather than white-space hazard, and you must classify the commodity
  and read an FM DS 8-9 N-at-pressure design, the 15 ft mixed-use bleed, and
  Table 14 hose and duration, including at-rest Li-ion under DS 7-112. Not
  white-space density times area, not an installed ESS room, and not a pump
  envelope.
---

# Storage staging sprinkler design

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

This method classifies storage commodity and reads a storage design. It consumes the system family from `suppression-technology-selection` and the storage send from `occupancy-hazard-fork`. It does not elect the family, reclassify the hall, or convert storage to a density-area demand.

**Core rule.** White-space demand (0.20 gpm/ft2 over 2,500 ft2 wet or 3,500 ft2 dry) is not a storage design. Do not reuse it on a storeroom, and do not freeze campus supply on the hall's 750 gpm / 45,000 gal. Storage hose and duration often govern the campus. Hand the priced hose, duration, and sprinkler flow to `hydrant-supply-curve` and `pump-envelope` after this method prices them.

FM DS 8-9 has no data-center chapter. Design pin: March 2010, interim revision April 2026. Re-read Tables 2 through 11 and the hose table from that interim revision before pinning a row. A July 2018 table body is unpinned until that re-read. Every data-center mapping that is not a sheet rule is an inference. Label it. Do not invent a commodity, a height, a K-factor, or an N-at-pressure program. There is no default of "20 heads at 7 psi." If a key is missing, state an ASSUMED value, use the more demanding case, and flag the row.

**Design practice.** Three layers, most stringent per parameter (commodity, height, wet versus dry column, hose, duration, bleed, and the Li-ion state of charge when batteries are stored). Report a directional delta versus NFPA 13-2025 storage chapters, not versus the ordinary-hazard density table. Prefer wet pipe unless freeze or the owner forces dry or double-interlock.

## Editions

| Layer | Pin |
|---|---|
| Code floor | Adopted IFC for high-piled and Li-ion storage. Delta reference NFPA 13-2025. An unamended 2024 I-Code cycle enforces NFPA 13-2022. IFC chapter text and NFPA 13 storage curves that are not opened on the job stay unpinned. |
| Storage design | FM DS 8-1 April 2014 / interim revision October 2024 classifies. FM DS 8-9 March 2010 / interim revision April 2026 protects. FM DS 2-0 October 2021 / interim revision January 2024 §2.5.4 is the layout companion. |
| At-rest Li-ion | FM DS 7-112 October 2024, first publication. |
| Hall next door | FM DS 5-32 January 2026 and FM DS 3-26 April 2025 §2.2.5. Adjacency only. Do not pull 0.20 / 2,500 / 3,500 into the storage row. |

## Battery state

FM splits Li-ion by the state of the battery, not by the building name.

| State | Where it goes |
|---|---|
| At rest, spare, staging, vendor pallet, construction laydown, decommissioned, or damaged | Stay here. DS 7-112 overlay on DS 8-9. |
| Installed dedicated ESS room or yard | `ess-isolation-venting-and-duration` (DS 5-33). Do not design it here. |
| Installed distributed battery at or under 20 kWh per rack | `power-isolation-disconnect-control` (DS 5-32). Do not design it here. |

Do not send stored Li-ion to the ESS method. A spares room is storage with a battery overlay.

## Steps

1. Confirm the family is wet, dry, or double-interlock. Prefer wet. A missing family is ASSUMED, not a silent swap. Foam, clean agent, water mist, single-interlock, and non-interlock as the basis of design: record and stop.
2. Consume `occupancy-hazard-fork`. The space must be storage or mixed, not a hazard class pasted onto a storeroom. "The storeroom is HC-2" is a category error. If the fork is missing, assume storage or mixed, say why, and flag it. Do not walk the hall occupancy chapters again.
3. Trigger, FM DS 8-9 §1.0. The sheet applies when any one is true: Class 1, 2, or 3 stored higher than 10 ft; Class 4 or plastic stored higher than 5 ft; or storage of any height over 200 ft2, with the area bounded by aisles at least 8 ft wide. A four-pallet island can clear 200 ft2. DS 2-0 Appendix A joins the 200 ft2 test to a height test. Until that conflict is checked on the opened sheet, DS 8-9 governs the design and DS 2-0 governs which layout regime applies. IFC high-piled is a different, height-based trigger. Do not use the code height gate to decide that storage does not exist. The portable-rack escape (DS 8-9 §2.2.5.2.4) is only for portable racks: at or under 100 ft2, 8 ft clear on all sides, and a height cap. It is not a general pallet escape. Verify that escape with the engineer of record.
4. At-rest Li-ion, when that state is present (FM DS 7-112 October 2024). Incidental storage needs all five: metal or cardboard boxes, area at or under 200 ft2, height at or under 6 ft, aisles at least 10 ft, and state of charge at or under 60 percent (§2.4.3.1). Miss one and it is full storage. Incidental hose is 500 gpm for 1 hour. Real storage (§2.4.5): packaging selects the DS 8-9 category (cellulosic or unexpanded internals to cartoned unexpanded plastic; expanded internals raise the class; unexpanded plastic external packaging raises it again). Ceiling-only envelope when the sheet allows it: state of charge at or under 60 percent, ceiling at or under 40 ft, storage at or under 15 ft, rack at or under 3 tiers, quick-response only. No storage above the batteries on a ceiling-only design. Keep at least 10 ft from other combustibles. Uncartoned, ceiling over 40 ft, or state of charge over 60 percent withdraws the commodity route. Damaged, returned, or defective (§2.4.6): outdoors preferred, or a cutoff room with direct outside access; one pallet high unless open-frame rack with in-racks; 0.3 gpm/ft2 over the room; 500 gpm hose for 2 hours. Automated storage (§2.4.7): at or under 30 percent state of charge, wet only; 30 to 60 percent only with the sheet's metal-lined and in-rack conditions, wet only; over 60 percent prohibited. Water cools. It does not extinguish enclosed cells. Write the state-of-charge cap into the receiving specification. An unstated state of charge is unpinned. Do not invent 30 percent or 60 percent as a grounded default.
5. Code layer for stored Li-ion, by the adopted IFC edition. IFC 2018 or 2021 does not contain the 2024 Li-ion storage provisions unless a local amendment says so. IFC 2024 includes the operational permit over 15 ft3 (105.5.28), the Group S-1 sprinkler trigger (903.2.9), and the Li-ion storage section. Section text that is not opened on the job stays unpinned. A later IFC chapter for lithium batteries applies only where that edition is adopted. Do not port a later edition onto a 2018 or 2021 authority. Batteries installed in their equipment are not storage.
6. Commodity, FM DS 8-1, three steps. Do not skip the pallet. Material plus internal packaging: more than 5 percent plastic by weight or volume leaves Class 1, 2, and 3. Expanded plastic: more than 40 percent by volume, or more than 20 percent exposed or enveloping. External packaging can raise or lower the protection category. Encapsulation does not change class. Wood, approved, or cardboard pallets do not raise class. A non-approved unexpanded plastic pallet raises one level. Protect to the highest hazard present, or segregate. Do not average. FM Class 4 means cartoned unexpanded plastic. NFPA 13 Class IV is a different class. Do not invent a crosswalk. Data-center receiving is plastics storage until proved otherwise. Treat packaged servers as cartoned unexpanded plastic at minimum and test them against cartoned expanded plastic. Non-PVC cable on wood or metal reels is cartoned unexpanded plastic (DS 8-1 Table 2.3 item 198). PVC on metal is Class 1 (item 194). PVC on wood or paper is Class 3 (item 195). Those cable rows are an inference until the FM field engineer confirms them. Verify with the engineer of record before the water supply is frozen.
7. Arrangement, before any ceiling-only quote. Ceiling-only rack options assume an open frame. Unblocked transverse flues at least every 9 ft through the rack height. A net opening under 3 in is not a flue. Solid shelves only if fixed, at or under 20 ft2, and not blocking a transverse flue. Grating at least 70 percent uniformly open. If the rack fails the open-frame test, treat it as solid shelf. Failed flues that create a solid shelf over 64 ft2 need in-racks at every tier. If the arrangement is unknown, assume the more demanding case and flag it. Do not assume open frame because the drawing says "rack."
8. Column and head family. Consume the elected family. Wet, including antifreeze when wet is elected and freeze is documented: wet columns; quick-response and pendent are allowed (DS 8-9 §2.3.3.2.4 and §2.3.3.2.6). Dry, and double-interlock: design as dry; standard-response upright, 280 F (§2.3.3.2.3). Wet temperature is 160 F, or 212 F when ambient exceeds 100 F, still designed as 160 F (§2.3.3.2.2). Do not import white-space head temperatures from DS 5-32. If the owner forces double-interlock in storage, the column is dry and the heads are standard-response upright 280 F. Record the pushback and still design dry. Dry columns in Tables 2 through 11 stop at 30 ft. The only ceiling-only dry path above 30 ft is §2.3.6.1: Class 1, 2, or 3, ceilings over 30 ft to 55 ft, standard-response upright 280 F. Double-interlock is not on that list. A tall storage building on double-interlock is an RFI before the family is committed.
9. Read N sprinklers at minimum pressure (DS 8-9 §2.3.3.7). Do not interpolate (§2.3.3.7.2). You may use a ceiling-height row equal to or higher than the actual ceiling. Do not convert the row to gpm/ft2 and compare it with NFPA 13. Do not apply the dry-area increase from `density-area-dry-increase`. FM storage tables are already split wet and dry. Keys: commodity, ceiling height, arrangement, wet or dry column, and aisle when the table asks. A missing key makes the number ASSUMED, never grounded. The 768 ft2 minimum design area (§2.3.3.7.2.3) can increase the flowing count. Read Table 14 from the protection-table count, not from the padded count. In-racks are required when no ceiling option exists, the supply cannot support a ceiling option, or a solid-shelf gate fires. Table 12, ordinary balancing at the point of connection: Class 1 to 3, 6 heads at or above 22 gpm on one level, or 10 heads (5 on two levels) at or above 22 gpm; Class 4 and plastics, 8 heads at or above 30 gpm, or 14 heads (7 on two levels) at or above 30 gpm; minimum pressure 7 psi; minimum K 8.0 when design flow exceeds 30 gpm. Do not run the tree here. The DS 7-112 in-rack path excludes ceiling demand. Cite §2.4.2.2 when that overlay applies. Above 20 in-rack heads, a separate control valve and drain is an ITM feature. Hand it to `itm-design-for-testability`. Ceiling storage sprinklers start at K 11.2 (DS 2-0). There is no K 5.6 or K 8.0 storage sprinkler. Layout limits in DS 2-0 §2.5.4 (area spacing, a 2 ft obstruction exemption, a steeper slope penalty, open-grid ceilings prohibited) are buildability flags. This method does not lay out heads.
10. Fifteen-foot bleed (DS 8-9 §2.3.3.5). Extend the storage hydraulic design at least 15 ft past every storage edge, or to a wall, wherever the occupancy is mixed. Where two storage areas are protected differently, extend the higher hazard 15 ft into the lower hazard. A room without walls is not hydraulically self-contained. Apply storage N-at-pressure and Table 14 on that apron. Do not convert the apron to 0.20 gpm/ft2. A rated partition is what lets the hall keep its own density on its side of the wall (DS 5-32 §2.2.4 for data-hall wall ratings; DS 3-26 §2.2.5 greatest hazard when the boundary is open). An undeclared boundary is ASSUMED unrated, so the bleed applies, unless the caller says otherwise.
11. Hose and duration, DS 8-9 Table 14, from the protection-table count. At or under 12 sprinklers: 250 gpm and 60 min. 13 to 19: 500 gpm and 90 min. 20 or more: 500 gpm and 120 min. Most storage designs land at 20 or more, so 500 gpm for 120 min, against a white-space 250 gpm for 60 min. When DS 7-112 asks 500 gpm for 2 hours, use the more stringent. If N is not pinned, state the fork and do not freeze campus hose at 250 gpm. Gallons only when sprinkler flow is pinned from a cited row: demand equals sprinkler flow plus hose, and gallons equal that demand times duration. Do not derive sprinkler flow from an unstated K times square root of pressure. Water delivery: DS 8-9 §2.3.2.5 is 40 s to the most remote 4 sprinklers (2 on 2 lines) unobstructed, and 60 s for a single-sprinkler cutoff. A data hall on DS 5-32 is 30 s to the most remote sprinkler. If one riser feeds both, the hall's 30 s governs the shared system. Do not quote 40 s as the data-center delivery requirement.
12. Code-side family. Do not silently pick ESFR. NFPA 13-2025 splits storage into control-mode density-area, CMSA, and ESFR. Low-piled and miscellaneous storage at or under 12 ft stays on the occupancy density, with the area limits in NFPA 13-2025 §4.3.1.4 through §4.3.1.8 and §20.1.1. That is the usual staging case when the insurer trigger has not fired. ESFR system type is limited by NFPA 13-2022 and 13-2025 §14.2.2: other system types only when the head is specifically listed. CMSA follows the listing (NFPA 13-2025 §13.2.1.3). Conservative assumption: no ESFR on dry pipe or double-interlock unless the listing for that head says so. If no listing is cited, stop and record an RFI. Verify with the engineer of record. NFPA 13 storage curves that are not opened on the job cannot support a numeric code-versus-FM delta. Report the delta as directional: FM is N at a minimum pressure, interpolation forbidden, separate wet and dry tables, and no extra 30 percent area on an FM row.

## Output

Storage memo: family consumed; editions, including the April 2026 DS 8-9 pin; trigger test; commodity or the DS 7-112 packaging route; open-frame result; head family; N at minimum pressure from a cited row, or an explicit ASSUMED flag with no invented row; 15 ft bleed; Table 14 from the table count; Li-ion state when present; ESFR listing gate; show-and-verify; directional delta versus NFPA 13-2025 storage; handoff of priced hose, duration, and sprinkler flow.

Do not emit a hall hazard schedule, a density-area demand, a pump nameplate, an in-rack valve size, or a fabricated table row.

## Out of scope

Foam, clean agent, water mist, deluge, and single-interlock or non-interlock as the sprinkler basis of design. Canada is out of scope. Installed ESS. Distributed batteries at or under 20 kWh per rack. White-space density times area. Head-by-head layout. Interpolating a storage table.

## Handoffs

| Work | Handoff |
|---|---|
| System family | `suppression-technology-selection` |
| Storage versus occupied send | `occupancy-hazard-fork` |
| White-space density, area, hose, duration | `density-area-dry-increase` |
| Campus supply and pump | `hydrant-supply-curve`, `pump-envelope` |
| In-rack valve and drain above 20 heads | `itm-design-for-testability` |
| Installed ESS | `ess-isolation-venting-and-duration` |
| Distributed battery isolation | `power-isolation-disconnect-control` |
| Dual-carrier commodity or hose row | `most-stringent-basis-matrix` |
