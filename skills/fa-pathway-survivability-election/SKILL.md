---
name: fa-pathway-survivability-election
description: >-
  Use this when electing NFPA 72 pathway survivability Levels (0-4) for EVACS or
  ECF relay location (3 ft / 20 ft / Class D) by edition. Packet optional;
  missing inputs ASSUMED. Companion to fa-code-edition-delta-check. Not Class
  designation design, not NAC/speaker loss, not battery.
---
# FA pathway survivability election

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job, stop. No NBC pathway-survivability rule is held. Return NEEDS HOLD. Do not map these NFPA 72 rows as Canada code. Do not state hours or ULC body text. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get edition text not confirmed.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write the word to). Verify with the engineer of record. Do not claim a stamp. Copy METHOD, not synthetic numbers.

## Not this skill
- Pathway **Class** A/B/C/D/N/X designation design and SLC/IDC/NAC topology: see KB pathway-class page (no dedicated skill yet).
- NAC voltage drop / speaker dB / Table 8 gauge: `fa-nac-voltage-drop-check`, `fa-speaker-circuit-loss-check`, `fa-nec-table-8-wire-sizing`.
- Full edition matrix beyond Levels / EVACS key / ECF location: `fa-code-edition-delta-check`.

## Basis (held)
### Survivability Levels [CODE] §12.4
- **2019** (72-22): Levels **0-3 only**. No Level 4.
  - Level 0: no special protection.
  - Level 1: fully sprinklered (NFPA 13) with metal raceway or metal armored cable.
  - Level 2: 2 h CI/fire-resistive cable, cable system, enclosure, or AHJ alternative.
  - Level 3: fully sprinklered (NFPA 13) plus one or more of the Level 2 options.
- **2022 / 2025** (72-19 / 72-04): Levels **0-4**. Level 4 = 1 h CI/fire-resistive cable, cable system, enclosure, or AHJ alternative. 2022 matches 2025.

### EVACS pathway survivability [CODE] §24.3.14.4
- **2019** (72-23): keyed to **evac strategy / zone separation**, not building rating.
  - Partial / relocation: Level **2 or 3** required (§24.3.14.4.1).
  - Exception .4.1.1 (zones separated by <2 h construction): Level **1, 2, or 3**.
  - Exception .4.1.2 (Class X or N with paths separated >=1/3 max diagonal of the notification zone): Level **1, 2, or 3**.
  - Total evacuation (no relocation / no partial): Level **0, 1, 2, or 3** (§24.3.14.4.2).
  - Never cite Level 4 on a 2019 job.
- **2022 / 2025** (72-20 / 72-05b): keyed to **building fire-resistance rating**.
  - No relocation / no partial: Level **0, 1, 2, 3, or 4** (§24.3.14.4.1).
  - Partial / relocation: >=2 h -> Level 2 or 3 or .4.6; >=1 h and <2 h -> Level **4** or .4.6; <1 h -> .4.6 only.
  - .4.6: Class N or X with Level 1, separated per .4.6.3. Under .4.6, §12.3.8 and §23.6.1 do not apply.
  - Class N shared segments: where two redundant Class N amplifier pathways share a head-end or switch segment, route them on separate segments so one failure cannot drop both. Pin the edition first, then cite that edition's item. Do not mix item numbers across editions.
    - Shared segment: NFPA 72-2022 12.3.6(5) does not permit primary and redundant pathways to share traffic over the same physical segment. NFPA 72-2025 12.3.6(7) requires that primary and redundant paths do not share traffic over the same physical segment. [CODE]
    - Single fault on one pathway that affects another: 2022 12.3.6(3); 2025 12.3.6(5) [CODE]. Where one segment carries two different pathways, cite both items for that edition (strictest defensible reading) [PRACTICE].
    - Item map 2022 to 2025 [PARA]: (1) to (1) and (3); (1) Exception to (2); (2) to (4); (3) to (5); (4) to (6); (5) to (7).
    - Item (1) scope, 2022 vs 2025: Verify with the engineer of record. Default: provide the redundant path in both editions [PRACTICE]. Annex A.12.3.6 is an open gap; annex silence is not a close.
    - Show the separate segments on the riser.
- **Scope delta [PARA] of held [CODE]:** on 2022/2025 the partial-evac rules (.4.3 to .4.6.4) apply, per §24.3.14.4.2, to the communication and control circuit pathways between a room or rated enclosure containing fire alarm equipment and other room(s) or rated enclosure(s) containing fire alarm equipment required for occupant notification (72-20 / 72-05b). On 2019, §24.3.14.4.1 has no such limit; §24.3.14.3 applies the rules to notification and communications circuits and other circuits necessary to ensure the continued operation of the emergency communications system (72-23). State which pathways the election covers.

### ECF relay location [CODE] §21.2.4
- **2019 / 2022** (72-24 / 72-20): within **3 ft** of the controlled component where the control circuit is **not** Class D. **No** 20 ft metal raceway/armored allowance.
- **2025** (72-11): §21.2.4.1: (1) within **3 ft** where conductors are not in metal raceway or metal armored cable, **or** (2) within **20 ft** where they are. §21.2.4.2: Class D need not meet .4.1.

### SAME across held [CODE]
- Class A/N/X separation §12.3.8.1: <=10 ft entry/exit; single room <=1000 ft2 (no ECF).
- Fault / restore indication within **200 s** (§12.6.1 / §12.6.2): **SAME** in **2019** (72-22), **2022** (72-40), and **2025** (72-04). 2022 = 2019 same duties; 2025 differs only in the exceptions cross-ref (12.6.10 vs 12.6.13).
- Restore operational capability within **200 s** from the time the fault is introduced (cites 10.11.1): 2019 **§12.2.3.4**; 2022 / 2025 **§12.2.3.5**. 2022 = 2019 words; 2025 rewords it to operational performance of a pathway class designation. 200 s SAME in all three. Cite the edition's number.
- Not SAME (72-40): the 20 ft control-equipment enclosure integrity exemption is 2022 §12.6.9 "in conduit or equivalently protected" vs 2025 §12.6.7 "in metal raceway or metal armored cable". Do not carry the 2022 wording onto a 2025 job.

## Inputs (ASSUME and flag any missing)
1. Enforced NFPA 72 edition (2019 / 2022 / 2025). Default ASSUMED 2025; always design-check older held eds when relevant.
2. Evacuation strategy: total (no relocation/partial) vs partial/relocation.
3. For 2022/2025 partial: building fire-resistance rating (h). For 2019 partial: whether zone-separation exceptions apply.
4. Sprinklered per NFPA 13? (needed for Level 1 / Level 3 / .4.6 Level 1).
5. Proposed Level election (0-4) and pathway construction (raceway / CI hours).
6. ECF: distance (ft) from interface device to controlled component; metal raceway/armored yes/no; Class D yes/no.
7. Whether Class A separation or 200 s fault timing is in scope for the handoff note.

## Steps
1. Pin enforced edition. Run `fa-code-edition-delta-check` for the Levels / EVACS / ECF rows.
2. List allowed Levels for the evac strategy on that edition (table above). Reject Level 4 on 2019.
3. Elect Level. Prefer owner/practice preference among code-permitted options. Label [PRACTICE] when choosing Level 1 metal raceway on a total-evac hall (Level 0 is also permitted).
4. For partial evacuation on 2022/2025, if building rating is 1-2 h and Level 4 is elected, confirm the edition has Level 4. On 2019 use L2/3 or an exception path instead.
5. ECF: if Class D -> exempt. Else if edition is 2025 and metal raceway/armored and distance <=20 ft -> PASS. Else if distance <=3 ft -> PASS. Else FAIL (relocate, add raceway on 2025, or redesign as Class D).
6. Note §12.3.8.1 SAME across held. Note §12.6.1 / §12.6.2 200 s as SAME 2019 / 2022 / 2025 [CODE]; cite the restore rule as §12.2.3.4 (2019) or §12.2.3.5 (2022 / 2025). If using .4.6, state that §12.3.8 does not apply under that path. For partial evac, state which pathways the election covers (scope delta above).
7. On FM DI VEWFD jobs carry: the s2.4.1.1 DI flag; the s2.4.3.2.1.3 no-cross-zone note (company FM default is single leg AND low air, which complies; flag only if the owner forces two-leg cross-zone [OWNER]); and the item 7 map: owner Action or Fire 1 = FM pre-alarm (alarm-level, arms the DI detection leg); NFPA 76 Alert stays supervisory (no building NAC, never a release leg). Which of Action or Fire 1 is ASSUMED unless the owner sequence says; see `fa-two-level-detection-stagger-and-fm-mapping`.

## Output
Edition pin; allowed Levels table; elected Level with [CODE]/[PRACTICE] labels; ECF PASS/FAIL by edition; SAME-row note; FM DI / VEWFD flags; open the edition text only if a real gap appears (Levels / EVACS / ECF / 200 s older-ed is held; 72-40 closed 2026-10-16).

## Campus EVACS pointer
Set evacuation strategy, then the fire-resistance rating, then the level, one building at a time. Pin the edition first. Do not cite Level 4 on a 2019 job. On 2022 and 2025, total evacuation with no relocation and no partial evacuation may use Level 0, 1, 2, 3, or 4 [CODE §24.3.14.4.1]. Level 1 on a sprinklered total-evacuation building is a [PRACTICE] pick; Level 0 is also permitted. Relocation or partial evacuation at 2 h uses Level 2 or Level 3, or §24.3.14.4.6 [CODE §24.3.14.4.3]. At 1 h and under 2 h, Level 4 or §24.3.14.4.6 [CODE §24.3.14.4.4]. Firefighter telephone circuits in 2 h construction use Level 2 or Level 3 [CODE §24.3.14.8]. Reject Level 0 on a relocation building. Reject Level 1 on those telephone circuits. Do not copy the picks as a live design.

Campus, NFPA 72-2025: a relocation or partial-evacuation building at 2 h elects Level 2 [CODE §24.3.14.4.3]. A building and the connecting link at 1 h and under 2 h elect Level 4, or the §24.3.14.4.6 alternate [CODE §24.3.14.4.4]. Pin 2025 before that election. A modeled speech score stays [ASSUMED]. Field intelligibility verification stays. Annex D quantitative measurement only when the AHJ or the project basis elects it. Campus sync uses the hot-standby master in `fa-nac-voltage-drop-check` [PRACTICE]. Never tag that backup as [CODE]. On a Canada job, stop. Do not invent a Canada pathway or voice rule. Verify with the engineer of record.

## Class N campus paths by edition

Pin NFPA 72 before citing §12.3.6. Do not mix item numbers across editions.

- Shared segment: 2022 §12.3.6(5); 2025 §12.3.6(7) [CODE]. The NFPA 72-2025 §12.3.6 body is held, items (1) through (7). Cite the 2025 items as [CODE]. The earlier delta-note label on that wording is retired. Item (5): a single open, ground, short, or combination of those faults on one pathway does not affect another pathway. Item (7): primary and redundant paths do not share traffic over the same physical segment.
- Single-fault isolation: 2025 §12.3.6(5) [CODE]. The live map also cites 2022 §12.3.6(3). Another reading says 2022 has no single-fault item. Keep the live cite. Do not relabel either edition until both bodies are checked side by side. Verify with the engineer of record.
- Redundant path: 2022 item (1); 2025 items (1) and (3). Single-endpoint exception: 2022 item (1) exception; 2025 item (2). That map is [PARA].
- Two or more remote amplifiers: dual path on separate physical segments. Cite (5) on 2022, and (7) plus (5) on 2025.
- One remote amplifier: item (1) scope differs by edition. That hold stays open. Default: provide the redundant path on both editions [PRACTICE]. Do not close it from annex silence.
- Between buildings, run the primary and redundant paths in separate conduit and on separate switches [ASSUMED].
- Annex A.12.3.6 is not held. Do not quote it and do not paraphrase it.
- Canada: stop. CAN/ULC-S524 is NEEDS HOLD. Do not invent a pathway rule. Foam and clean agent stay locked.

## Shared pathways and integrity exemptions

Chapter 12 shared-pathway performance levels are not the Chapter 24 survivability levels above. Do not mix the two number sets.

- Level 3 pathways use equipment dedicated to the life safety system [CODE NFPA 72 §12.5.4*].
- Level 1 pathways prioritize life-safety data over other data [CODE NFPA 72-2025 §12.5.2.2].
- A Level 3 default on an owner network is [PRACTICE]. Level 2 needs owner sign-off [OWNER]. Do not invent Level 0 or Level 2 requirement text.
- Monitoring for integrity is not required for listed equipment interconnected inside one enclosure [CODE NFPA 72-2025 §12.6.6*].
- It is not required for ground-fault detection conductors where one ground fault does not stop required operation [CODE §12.6.8]. Do not cite §12.6.9 for that exemption. In 2025, §12.6.9 is computer and keyboard cabling.
- The 20 ft enclosure line above stays: 2022 §12.6.9 versus 2025 §12.6.7. That pair is the enclosure exemption, not the ground-fault exemption.
- A modeled speech score stays [OWNER] or [ASSUMED]. It is never a field pass. NEC 2026 Table 8 stays NEEDS HOLD. Do not state ohms. Class N item (1) stays open. On a Canada job, stop. Do not map NFPA 72 as Canada code.
