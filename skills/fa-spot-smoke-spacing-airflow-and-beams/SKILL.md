---
name: fa-spot-smoke-spacing-airflow-and-beams
description: >-
  Use when you must lay out or check spot-type smoke detector counts in data center support rooms (electrical, UPS, mechanical, office, raised floor) for airflow reduction, beams and joists, under-floor spaces and return-plenum mechanical rooms per NFPA 72 Ch 17 (2019, 2022, 2025). Not ASD/VEWFD hall sampling.
---
# Spot smoke spacing: airflow, beams, raised floor

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job, stop. CAN/ULC-S524 detector spacing is not held. Return NEEDS HOLD. Do not map these NFPA 72 rows as Canada code. Do not state hours or ULC body text. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
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
- [CODE] Smooth spacing 30 ft nominal; every ceiling point within 0.7S (17.7.4.2.3.1) [2019 17.7.3.2.3.1]. Sidewall 12 in max (17.7.4.2.1*). Not in supply airstream (17.7.7.3.2).
- [CODE NFPA 72-2025] Location. A detector protecting a specific hazard may sit closer, where it can intercept the smoke (§17.7.4.1.3). Spot smoke is on the ceiling, or on a sidewall with the top within 12 in. of the ceiling (§17.7.4.2.1*). Under a raised floor, mount only in a listed orientation (§17.7.4.2.2*). In 2025, §17.7.3 is sensitivity. Do not cite §17.7.3 for location. The 2019 location numbers stay with the spacing cites above.
- Containment is not addressed in Ch 17. Hot-aisle work goes to the ASD skills [PRACTICE].

## Inputs (ASSUME and flag any missing)
Room list: size, ceiling height, ACH, beam depth and spacing, girders, raised floor use (supply air or not), plenum use, enforced edition.

## Steps
1. Area per detector by ACH. Pick the smallest table ACH at or above the room ACH, so spacing rounds down. No interpolation [CODE table; row pick PARA].
2. Under-floor: separate room at smooth spacing; never counted as room detection.
3. Return-plenum mech room: no reduction.
4. Beams: below 0.1H use smooth spacing; at or above 0.1H and spacing at or above 0.4H, a detector in each pocket; apply 2025-only rules only on 2025 jobs.
5. Grid check in a script: cell area at or under table area, spacing at or under 30 ft, farthest point within 0.7S. Over 40 ft on 2025: 17.7.4.2.3.3 other spacing [PARA].
6. MV switchgear room: where NFPA 76 is adopted or owner-required, NFPA 76-2024 §6.10.5.1 (same section in 2020) requires an early-warning system in power areas, per Chapter 8 [CODE]. Whether the room is a power area is a scope call. Verify with the engineer of record. That section sets no spot count. A design value of 4 early-warning spots where Chapter 17 spacing gives 2 is [PARA]. Else Chapter 17 spacing is the floor [PRACTICE]. Keep detectors out of arc-flash vent paths and above the gear clear zone. Prefer air sampling with the detector outside the room. Final spots need the arc-flash study [PRACTICE]. Verify with the engineer of record.
7. FM electrical rooms: on an FM job the sheet smoke minimum is photoelectric or combination smoke to a constantly attended location, with or without sprinklers or heat [OWNER FM DS 5-19 §2.2.4]. Space those detectors per FM DS 5-48 §2.2.3.3 (Table 4 by air changes; 900 ft² and 30 ft at or under about 6 air changes). Compare with the Chapter 17 counts from steps 1 to 5. The most stringent wins. Do not add heat from DS 5-19. Where the room is a high-ambient electrical wiring room, add spot fixed-temperature heat in addition to smoke, not instead of smoke [OWNER FM DS 5-48 §2.2.1.5]. The ambient call stays with the engineer of record. Arc-flash detectors are not the basis of design.
8. Print row-pick tests (for example 13 ACH uses the 15 ACH row).

## Output
Room table: ACH row, area per detector, beam rule, grid, count, pass or fail per check, edition labels, delta vs 2025.

## Concealed detectors

A concealed detector has a remote indicator at an accessible location the authority accepts [CODE NFPA 72-2022 and 2025 §17.4.7.2]. The 2019 rule covered a concealed detector more than 10 ft above the floor (§17.4.6). Cite the enforced edition. Confirm any panel-and-drawing exemption in the adopted text before dropping the indicator (§17.4.7.3 in 2022 and 2025).

Solid joists count as beams [CODE NFPA 72-2025 §17.7.4.2.4.1]. A girder whose top is within 4 in. of the ceiling is treated as a beam; more than 4 in. down, it is not a factor [CODE §17.7.4.2.4.2, 2025 only]. At or above 0.4 of the ceiling height between beams, put a detector in each pocket, and apply the 0.1 height depth test in step 4 [CODE §17.7.4.2.4.3]. A gap above the beam over 15 percent of the ceiling height permits smooth spacing [CODE §17.7.4.2.4.3(6), 2025 only]. On 2019 and 2022 jobs those girder and gap rules stay [PRACTICE], as the basis already says. Do not use the gap relief on those editions without an authority acceptance.

The 2025 location labels stay §17.7.4.1.3, §17.7.4.2.1*, and §17.7.4.2.2*. In 2025, §17.7.3 is sensitivity. Do not cite it for location. Stratification beyond these beam rules stays open. Do not invent a second spacing number. On a Canada job, stop. CAN/ULC-S524 spacing is NEEDS HOLD.

## Telecom rooms when NFPA 76 is elected

Where the owner or the authority treats a meet-me room, a main distribution frame, or a cable entrance as a telecommunications facility under NFPA 76, the room-by-room very-early-warning and early-warning rules apply. That applicability is an owner or authority call [PARA]. Verify with the engineer of record. Do not treat a hyperscale hall as that facility. Duct smoke in those rooms is supervisory [CODE NFPA 72-2019, 2022, and 2025 §21.7.4]. The sentence matches. The second-level trip obscuration stays [ASSUMED] (GAP-B33R8-1). Do not encode 0.2 %/ft as [CODE]. Foam and clean agent stay locked. Wet, dry, and double-interlock only.
