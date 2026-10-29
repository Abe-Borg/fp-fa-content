---
name: fa-spot-smoke-spacing-airflow-and-beams
description: >-
  Use when you must lay out or check spot-type smoke detector counts in data center support rooms (electrical, UPS, mechanical, office, raised floor) for airflow reduction, beams and joists, under-floor spaces and return-plenum mechanical rooms per NFPA 72 Ch 17 (2019, 2022, 2025). Not ASD/VEWFD hall sampling.
---
# Spot smoke spacing: airflow, beams, raised floor

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Pin the enforced editions first; run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis (NFPA 72, held 72-03, 72-45, 72-55; 2025/2022 numbers, 2019 in brackets)
- [CODE] Airflow reduction: Table 17.7.7.3.3.2 by ACH [2019 Table 17.7.6.3.3.2, same values]. 7.5 ACH or less: no reduction (17.7.7.3.3.1).
- [CODE] Table not for under-floor or above-ceiling spaces (table title, all editions).
- [CODE] Under-floor is a separate room (17.7.4.5.1) and does not replace room detection (17.7.4.5.2) [2019 17.7.3.5]. 2025: if environmental air, also 17.7.5.1 and 17.7.5.2 via 17.7.4.5.3(2).
- [CODE] HVAC mechanical room used as return plenum: no ACH reduction (17.7.7.3.4) [2019 17.7.6.3.4].
- [CODE] Beams: solid joists count as beams; depth vs 0.1H, spacing vs 0.4H (2025 17.7.4.2.4.3; 2022 17.7.4.2.4.2; 2019 17.7.3.2.4.2).
- [CODE 2025 only] 40 ft ceiling scope on 17.7.4.2.3.1; girder within 4 in of ceiling is a beam (17.7.4.2.4.2); gap above beam over 0.15H permits smooth spacing (17.7.4.2.4.3(6)). On 2019/2022 jobs these are [PRACTICE].
- [CODE] Smooth spacing 30 ft nominal; every ceiling point within 0.7S (17.7.4.2.3.1) [2019 17.7.3.2.3.1]. Sidewall 12 in max (17.7.4.2.1). Not in supply airstream (17.7.7.3.2).
- Containment is not addressed in Ch 17. Hot-aisle work goes to the ASD skills [PRACTICE].

## Inputs (ASSUME and flag any missing)
Room list: size, ceiling height, ACH, beam depth and spacing, girders, raised floor use (supply air or not), plenum use, enforced edition.

## Steps
1. Area per detector by ACH. Pick the smallest table ACH at or above the room ACH, so spacing rounds down. No interpolation [CODE table; row pick PARA].
2. Under-floor: separate room at smooth spacing; never counted as room detection.
3. Return-plenum mech room: no reduction.
4. Beams: below 0.1H use smooth spacing; at or above 0.1H and spacing at or above 0.4H, a detector in each pocket; apply 2025-only rules only on 2025 jobs.
5. Grid check in a script: cell area at or under table area, spacing at or under 30 ft, farthest point within 0.7S. Over 40 ft on 2025: 17.7.4.2.3.3 other spacing [PARA].
6. MV switchgear room: where NFPA 76 is adopted or owner-required, apply the 76 power area reading (example: 4 EWFD spots in a room where 72 spacing gives 2) [PARA; Verify with the engineer of record, provisional until 76-2024 6.1.3, 8.8.2, 8.8.3(1) are pulled]. Else 72 spacing is the floor [PRACTICE]. Keep detectors out of arc-flash vent paths and above the gear clear zone; prefer ASD with the detector outside the room; final spots need the arc-flash study [PRACTICE; Verify with the engineer of record] (Design practice design practice, , ).
7. Print row-pick tests (for example 13 ACH uses the 15 ACH row).

## Output
Room table: ACH row, area per detector, beam rule, grid, count, pass or fail per check, edition labels, delta vs 2025.
