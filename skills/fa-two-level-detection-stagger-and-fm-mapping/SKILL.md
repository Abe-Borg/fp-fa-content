---
name: fa-two-level-detection-stagger-and-fm-mapping
description: >-
 Use when a data hall needs two-level (high and low) VEWFD/ASD sampling and you
 must decide which stagger rule applies (NFPA 76-2020/2024 only when adopted or
 elected) and map owner VEWFD levels to FM signals (Alert supervisory; Action
 or Fire 1 = FM pre-alarm per design practice item 7); packet optional, missing
 inputs ASSUMED.
---
# FA two-level detection stagger and FM mapping

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.

- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "section not pinned; verify before use.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). Verify judgment calls with the engineer of record. Copy METHOD, not synthetic numbers.

## Relationship to other skills
Full port, return and head layout: `fa-asd-vewfd-data-hall-sampling-layout`. Release logic: `fa-double-interlock-releasing-cause-and-effect`. This skill owns only the two-level stagger decision and the level-to-signal map, and hands both to those skills.

## Basis
- [CODE] NFPA 72-2025 (and 2022, ; 2019 §17.7.3.6) §17.7.4.6.1.1*: each port treated as a spot detector, absent performance criteria. §17.7.7.3.3.3* (2019 §17.7.6.3.3.3): air sampling in high air movement per maker instructions. No two-level stagger rule in NFPA 72; any stagger on a 72-only job is [PRACTICE] (: not in 2025 Ch. 17 body; : not in 2019 / 2022 Ch. 17 body or Annex A Ch. 17, and 2025 A.17.7.1.11 adds video image smoke detector text; annex A.17.7.1.11 [HB/annex] says where stratification is possible, consider mounting a portion of the detectors below the ceiling, and in high-ceiling areas consider projected beam or air sampling detectors at different levels; no spacing value).
- [CODE] : 2022 Annex A Ch. 23 and Ch. 17 have **no** two-detector, cross-zone, or counting-zone guidance (A.23.11.7 lists system types only; A.17.14 lists initiating devices only). INSIGHTS boxes were not checked. The §23.8.5.4.3 to .5 two-detector rules are [CODE] in 2019, 2022 and 2025 body text. 2022 and 2025 add §23.8.5.4.3(4); 2019 ends at item (3).
- [CODE] NFPA 76-2024 §8.5.3.1.2.2* (only when 76 is adopted or elected): each level no more than 400 ft2 per port; coverage between high and low levels no more than 200 ft2, staggered. §8.5.3.1.2.1*: one level 200 ft2.
- [CODE] NFPA 76-2020 (same section numbers;, and 8.5.3.1.2.txt; is a summary only): §8.5.3.1.2.2* two levels, each level no more than 400 ft2 per port, between levels no more than 200 ft2, staggered. §8.5.3.1.2.3(C): each return air port covers no more than 4 ft2. §8.4.2.2.4(1), §8.4.2.2.9: VEWFD alert is supervisory, no building NACs. Values match 2024. Cite the 76 edition the job adopts.
- [OWNER]/insurer FM DS 5-32 s2.4.2.2 (pointer note): two levels 400 ft2 per port where trays block smoke. FM s2.4.2.2.6 : two levels where cable trays impede smoke; stagger no more than 200 ft2 between each level [OWNER/insurer]. Verify with the engineer of record (insurer criteria, not code). Conservative assumption: on FM jobs use two levels where cable trays impede smoke, with the stagger no more than 200 ft2 between levels.
- [CODE] NFPA 76-2024 §8.4.1.3*, §8.4.2.2.4(1), §8.4.2.2.7, §8.4.2.2.9: VEWFD alert (prealarm) is a supervisory signal, distinguishable, and does not activate building NACs. NFPA 76 is telecom scope, not automatic for a hyperscale hall [PRACTICE].
- [OWNER]/insurer FM DS 5-32 §2.4.3.2.1.3: actuate preaction on pre-alarm (§2.4.3.2.1.3.1); no cross-zone (§2.4.3.2.1.3.2). Confirm the edition with the insurer.
- design practice item 7 : on FM jobs the owner VEWFD Action or Fire 1 counts as FM pre-alarm. It is alarm-level and arms the DI detection leg (valve opens only with low air). NFPA 76 Alert stays supervisory: no building NAC, never a release leg. Confirm which of Action or Fire 1 on the owner sequence.

## Inputs (ASSUME and flag any missing)
1. NFPA 76 adopted or elected (owner, insurer, AHJ), and which edition? Default ASSUMED not elected for a hyperscale hall.
2. Insurer (FM or not).
3. Obstructions that block smoke (trays, containment tops); hall area; return opening area.
4. Owner VEWFD level names and thresholds (e.g. Alert, Action, Fire 1, Fire 2) and which of Action or Fire 1 is the FM pre-alarm map. If missing, ASSUME Fire 1 and flag it.

## Steps
1. Level gate: two levels when obstructions block smoke; else one level and stop the stagger part.
2. Stagger rule:
 - 76 adopted or elected: [CODE] 76 §8.5.3.1.2.2 (2020 or 2024), 400 ft2 per port per level, stagger so high-to-low coverage is no more than 200 ft2.
 - 76 not in basis: ports per level at 400 ft2 [OWNER]/insurer FM. Stagger method [PRACTICE]: offset the low grid half a grid in both directions from the high grid, so each high-to-low cell is about 200 ft2 (mirrors 76). On FM jobs the stagger is FM s2.4.2.2.6, no more than 200 ft2 between each level [OWNER/insurer] . Verify with the engineer of record. Conservative assumption: apply the FM 200 ft2 stagger on FM jobs. Check shown: high grid S x S at 400 ft2 per level gives S = 20 ft. The low grid shifts S/2 = 10 ft in both directions, so each low port sits at the center of a high cell. Combined, the two levels place 2 ports per 400 ft2, or 1 port per 200 ft2 in plan, and no plan point is more than 10 ft x 10 ft (100 ft2 quadrant) from a port at the other level. This meets 200 ft2 only under the reading 'no more than 200 ft2 of plan area per port across both levels'. That reading is ASSUMED (FM DS 5-32 Jan 2026 s2.4.2.2.6 B text, the January 2026 data sheet does not settle that reading does not settle it). Do not cite a QA finding as authority.
 - Return openings: 4 ft2 per port [CODE 76-2020 §8.5.3.1.2.3(C) or 76-2024 §8.5.3.1.2.3 when 76 applies; NFPA 75-2024 or 75-2020 §9.2.2.1 when 75 is in the basis ; FM s2.4.2.2.3 OWNER/insurer]. Hand the count to the ASD layout skill.
3. Ports per level = area / 400, per level, not combined. Script it. Hand to the ASD layout skill.
4. Signal map table, one row per owner level: signal class, building NAC, release leg, SOC notify, vent slow-down.
 - Alert: supervisory, no NAC, not a leg [CODE 76-2020/2024 §8.4.2.2.4(1), .9 where 76 applies]. Where 76 is not in the basis, no held code makes Alert supervisory: label it [OWNER] per item 7 (Design practice), not [CODE].
 - Mapped level (Action or Fire 1): alarm-level, building NAC yes, leg 1, FM ventilation slow-down at or above 5 ft/s or 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only] [design-practice item 7; OWNER/insurer].
 - Action when Fire 1 is the map: not a leg, no NAC, pre-alarm display at FACU/SOC [OWNER].
 - Fire 1 when Action is the map: alarm-level, building NAC yes, SOC notify, not a separate leg (leg 1 is already set by Action in a rising sequence) [OWNER]. If the owner wants Fire 1 OR'd into leg 1 as a backup, label it [OWNER] and show it in the truth table. Vent slow-down already started on Action.
 - Fire 2: alarm, not the leg on FM jobs [OWNER].
5. Check: no row lets a supervisory signal sound NACs or arm a release. Fix before handoff.
6. FM flags: s2.4.1.1 (standing DI flag, above). s2.4.3.2.1.3 no cross-zone: company FM default is single leg (Fire 1 or Action) AND low air, which complies. Flag only where the owner standard forces two-leg cross-zone [OWNER]. Two-leg is [PRACTICE] on non-FM jobs only.
7. Non-FM jobs: map is [OWNER]; the Alert-is-supervisory rule still holds where 76 is in the basis.

## Output
Stagger decision with label; ports per level; return ports; signal map table; ASSUMED list (76 status, mapped level); FM flags; handoffs to the ASD and DI skills.

## L2 trip obscuration, open

On an FM double-interlock job, where the mapped Action or Fire 1 level is the detection leg, hold the trip obscuration at 0.2 %/ft per port. Label it ASSUMED. It is not settled code and it is not a closed insurer pin. FM DS 5-32 January 2026 body §2.4.3.2.1.3.1 actuates the valve on the pre-alarm. §2.4.3.2.1.3.2 bars cross-zoned detection. Those body sentences outrank §3.3.2 rationale text that says an L3 alarm initiates suppression. §3.3.2 still states the 0.2 %/ft pre-alarm figure [OWNER]/insurer. Do not hand 0.2 %/ft as [CODE]. Do not invent a trip from 0.4 to 0.6 %/ft, and do not use 1.0 %/ft as the detection-leg trip, unless the engineer of record closes the hold. Carry the same flag on `preaction-releasing-c-and-e-soo` and on `fa-double-interlock-releasing-cause-and-effect`. NFPA 72 and NFPA 13 set no obscuration trip. Where FM is not in the basis, owner thresholds stay [OWNER]. On a Canada job the FM sheet is the same when that insurer is on the job. Do not assert an NBC or NFC detection overlay. CAN/ULC-S524 stays NEEDS HOLD. Do not map NFPA 72 as Canada code. Wet, dry, and double-interlock only. Foam and clean agent stay locked. Verify with the engineer of record.

## Sensitivity vocabulary does not elect the trip

Each air-sampling port is a spot detector for location and spacing [CODE NFPA 72-2025 §17.7.4.6.1.1; 2019 §17.7.3.6.1.1]. In 2025, §17.7.3 is sensitivity. It names the vocabulary. It does not elect Alert, Action, or Fire 1, and it does not set 0.2 %/ft. The L2 trip above stays ASSUMED (GAP-B33R8-1). Do not relabel it [CODE]. On a Canada job, CAN/ULC-S524 stays NEEDS HOLD. Do not map NFPA 72 as Canada code.
