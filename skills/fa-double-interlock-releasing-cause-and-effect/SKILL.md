---
name: fa-double-interlock-releasing-cause-and-effect
description: >-
  Use when you must write the FA-side cause-and-effect matrix, truth table, and
  sequence notes for a double-interlock preaction zone on a listed releasing
  panel per NFPA 72-2025 §23.11, with the FM DS 5-32 s2.4.1.1 DI flag and
  s2.4.3.2.1.3 no-cross-zone flag on FM jobs. Packet optional; missing inputs
  ASSUMED. Not trim, air setpoints, or delivery time.
---
# FA double-interlock releasing cause and effect


Roster language, job names, and local source-file paths were removed when this method was copied into the content pack. Section numbers and the calculation method are unchanged. Verify judgment calls with the engineer of record.

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- US jobs only. Canada FA standards are on hold (design-practice-notes item 1): a Canadian job Stops with a note to the engineer of record.
- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (the engineer of record, standing): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "needs code edition: <id>".
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). the engineer of record is engineer of record; no stamp claim. Copy METHOD, not synthetic numbers.

## Scope
FA side only. Valve, trim, air/N2, water delivery belong to FP (skills preaction-releasing-c-and-e-soo, preaction-el-el-trim-election). Matrix is co-signed with the coordinating designer. SI/NI appear only as FM quotes, comparison only.

## Basis (NFPA 72-2025, _sources 72-06, 72-07; 2019 / 2022 Ch. 23: 72-52; Ch. 17: 72-47)
- [CODE] §23.11.1: releasing FACU listed for releasing service. §23.11.2: releasing devices listed for use with it. §23.11.3 to .11.4: device and wiring monitored for integrity.
- [CODE] §23.11.5: disconnect switch to test without actuating. §23.11.5.1: operating it causes a supervisory signal. §23.11.5.2 to .5.3: physical switch; software disconnects not permitted.
- [CODE] §23.11.6: sequence consistent with applicable suppression standards. Reading this as NFPA 13 for DI is [PARA].
- [CODE] §23.11.7*: automatic detectors per Ch. 17. §23.11.8: single releasing FACU (§23.11.9 exception). §23.11.10 to .10.2 (2025; 2019 / 2022 single §23.11.10, 72-52): monitored by, not dependent on, building FA. §23.11.11: protected from discharge damage.
- [CODE] §23.8.5.10.1 to .10.2: releasing FACU connected to building FACU; alarm and supervisory annunciated there.
- [CODE] §23.8.5.4.3(3) (2019, 2022, 2025; 72-52) bars alarm verification where two detectors initiate the alarm response. Keeping verification off the release leg is [PRACTICE] (QA-1 M-3).
- [CODE] §17.19.2.2.2 (2025; 2019 / 2022 §17.17.2.2.2, 72-47): high and low air supervisory signals, by edition. 2025: off-normal per NFPA 13 unless the valve maker's published instructions permit otherwise. 2022 §17.17.2.2.2(B): off-normal at a 10 psi (70 kPa) increase or decrease, for dry pipe and preaction systems, unless the maker's published instructions permit otherwise. 2019 §17.17.2.2.2(B): 10 psi (70 kPa) applies to dry pipe valves; (C) low air dry pipe valves follow the maker's instructions. Setpoints come from the FP corpus. The pressure tank 10 psi rule is §17.19.2.2.1 (2019 / 2022 §17.17.2.2.1).
- No manual-release section and no abort rules found in Ch. 23 (72-06 Not found). No abort and no discharge delay on the water path is [PRACTICE]/[OWNER], not held code text.
- [CODE] NFPA 72 §7.4.9* (shop drawings: narrative or input/output matrix describing the sequence of operation) and §7.5.5.2* (SOO with record drawings "to reflect actual programming at the time of completion"): same words and numbers in 2019, 2022, 2025 (72-13, 72-27). The C&E matrix is that SOO; reissue it as-programmed at closeout.
- [CODE] ITM handoff: Table 14.4.3.2 18(6) release solenoid circuit, Initial X and **Annually**, "Verify operation of solenoid."; 17(1) electromechanical releasing device Annually. Same in 2019, 2022, 2025 (72-12 raw, 72-27). ~~Releasing ITM body numbers are §14.2.6.1 to .6 in all three editions (72-27, 72-28); 2019/2022 text is held for §14.2.6.5 only; 2025 §14.2.6.4 secure and §14.2.6.6 restore.~~ **[CLOSED 72-30, 72-31]** Releasing ITM body is §14.2.6.1 to .6 in all three editions, text held for all three (72-27, 72-28, 72-30): 2019 = 2022 word for word; 2025 same except .1 reworded. [CODE] on every edition: §14.2.6.2 occupant notification while releasing service is tested; §14.2.6.3 no discharge test required by NFPA 72; §14.2.6.4 secure the suppression system for the FA test (disconnect solenoids or close valves; FP coordinates the preaction valve); §14.2.6.5 releasing circuits "electrically monitored for integrity and operate as intended on alarm"; §14.2.6.6 return it to service. The 18(6) footnote cite §14.2.10 is the Test Plan (.1 and .2, same words in all three; 72-31). Also Annually where used: 18(4) cross-zone (one detector per zone, first zone then second) and 18(8) counting zone (minimum of four locations [CODE] in 2019, 2022, and 2025; 72-28, 72-38); 18(9) open-circuit supervision on every releasing circuit (72-28). Abort rows 18(1) to (3) do not apply (no abort on the water path).
- [CODE] NFPA 76-2024 §8.4.1.3*, §8.4.2.2.4(1), §8.4.2.2.9: VEWFD alert (prealarm) is a supervisory signal and does not activate building NACs.
- the engineer of record decision (design-practice-notes item 7, 2026-10-15): on FM jobs the owner VEWFD **Action or Fire 1** level counts as FM pre-alarm. It is an alarm-level signal and is the DI detection leg (leg 1). It opens the preaction valve only together with low air. Confirm on the owner sequence which of Action or Fire 1 is used. NFPA 76 **Alert** stays supervisory [CODE NFPA 76-2024 §8.4.2.2.4(1)]: no building NAC [§8.4.2.2.9], never leg 1, never arms a release.

## Inputs (ASSUME and flag any missing)
1. Insurer; owner detection levels (e.g., Alert, Action, Fire 1, Fire 2). On FM jobs, which of Action or Fire 1 is leg 1 (item 7) [OWNER]. If missing, ASSUME the one the owner sequence calls first alarm-level and flag it.
2. Detection type per zone; zone to valve area map from the coordinating designer.
3. Manual release stations; valve listing rule on manual replacing the detection leg only.
4. Supervisory points: low air, high air, tamper, N2/compressor power, waterflow.
5. Ventilation airflow (FM slow-down at or above 5 ft/s or 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13, pull 75-07; owner/insurer FM DS 5-32 only]).

## Steps
1. Scope gate: confirm DI preaction. SI/NI as basis of design: record, Stop, RFI-variance.
2. Boolean: Solenoid = (detection leg OR manual release) AND low air AND NOT isolated. Manual substitutes for detection leg only (confirm on valve listing).
3. Detection leg: on FM jobs, leg 1 = owner Action or Fire 1 (the engineer of record item 7; confirm which on the owner sequence). It is an alarm-level signal. NFPA 76 Alert is supervisory: no NAC, never leg 1. No cross-zone (s2.4.3.2.1.3). Fire 2 not OK as the leg. Off FM, company cross-zoned first-knock default may apply; two detectors follow §23.8.5.4.4 spacing (2019, 2022, 2025; 72-52).
4. Generate the full truth table in a script; verify solenoid fires only per the Boolean.
5. C&E matrix. Columns: alarm NAC, supervisory, trouble, release solenoid, vent slow-down, notify attended location. Rows: Alert (supervisory, notify attended location, no NAC, no release [CODE NFPA 76 §8.4.2.2.4(1), §8.4.2.2.9 where 76 applies; else OWNER per item 7]); Action, Fire 1, Fire 2 keyed to the map (same as `fa-two-level-detection-stagger-and-fm-mapping` step 4): if Fire 1 is the map, Fire 1 = alarm, NAC yes, leg 1, and Action = pre-alarm display, no NAC, not a leg; if Action is the map, Action = alarm, NAC yes, leg 1, and Fire 1 = alarm, NAC yes, not a separate leg (OR into leg 1 only if the owner asks, [OWNER]); Fire 2 = alarm, NAC yes, never the leg on FM jobs. Then low air, leg 1 AND leg 2, waterflow, high air / tamper / N2 power, ASD fault, solenoid circuit open, isolate switch, manual station. Label every cell [OWNER], [OWNER]/insurer, or [CODE].
6. Isolate switch row: supervisory [CODE §23.11.5.1], blocks solenoid [CODE §23.11.5], physical only [CODE §23.11.5.2].
7. Building FA tie-in: releasing FACU monitored for alarm, supervisory, and trouble [CODE §23.11.10.1; 2019 / 2022 §23.11.10]; annunciate alarm and supervisory at building FACU [CODE §23.8.5.10.2]; releasing FACU not dependent on or affected by the building FA system [CODE §23.11.10.2; 2019 / 2022 §23.11.10].
8. FM flags on every FM job, both, separately:
   - "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (the engineer of record, standing): keep DI. Flag to owner and FM on this job."
   - "FM DS 5-32 s2.4.3.2.1.3.2 (verbatim in FP corpus fm-ds-5-32.md) no cross-zone to actuate conflicts with the company cross-zoned first-knock default (not with DI itself)."
   - FM: no automatic smoke exhaust in DP rooms; if code forces it, tie to waterflow, not detection.
9. Hand off to FP: air setpoints, trim variant (El/Pn, Pn/Pn, El/El failsafe), delivery time.

## Output
Boolean, truth table, labeled C&E matrix (as the §7.4.9 / §7.5.5.2 SOO), releasing ITM rows for the ITM plan (18(4)/(8) where used, 18(6), 18(9); §14.2.6.4 secure and §14.2.6.6 restore [CODE] in 2019, 2022 and 2025; ~~[CODE 2025]; on 2019/2022 jobs these are [PRACTICE] until pulled, needs code edition 72-30~~ [CLOSED 72-30]), FM flag block, ASSUMED list, FP handoff rows, delta vs NFPA 72-2025.

## Sources
KB: 50_releasing-epo-and-interlocks/releasing-service-and-double-interlock-preaction-tie-in.md, 70_codes-standards-insurer-basis/three-layer-basis-for-fire-alarm.md, KNOWLEDGE_BASE/design-practice-notes.md items 6 and 7. Worked: EXERCISES/worked/EX-04-double-interlock-preaction-cause-and-effect.md, EX-12, _calc/ex04_di_ce.py. _sources 72-06, 72-07, 72-12, 72-13, 72-27 (design-practice-notes-link-72-27-ch7-soo-ch14-vrla-releasing-2019-2022-2026-10-15.md), 72-28 (design-practice-notes-link-72-28-ch14-rows-2019-2022-and-14-2-6-2025-2026-10-15.md), 72-29 to 72-31 (design-practice-notes-link-72-29-30-31-ch14-asd-releasing-testplan-2019-2022-2026-10-15.md), 72-38 (design-practice-notes-link-72-38-table-14-4-3-2-selected-2025-2026-10-15.md), 76-01, fm-ds-5-32-and-5-48-detection-POINTERS.md. (Under (path omitted) FA AGENT TRAINING.)
