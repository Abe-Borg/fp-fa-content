---
name: fa-nac-voltage-drop-check
description: >-
  Use when you must check a DC notification appliance circuit for voltage at the
  last appliance per NFPA 72-2025 §18.3.7.1 to .6 (CUSTV or CMSTV, MVA, ELL or
  PTP, 75°C, both conductors) with NEC Ch. 9 Table 8 resistance (held 2023/2020;
  2026 NEEDS HOLD): gauge pass or fail and max length. Packet optional; missing
  inputs ASSUMED. Not AC or audio line-loss, SLC, or battery sizing.
---
# FA NAC voltage drop check

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). Canada in scope (the engineer 2026-10-29). NBC 2025 Div. B 3.2.4 held (fold26). CAN/ULC-S524, S536, S537, S1001, and CEC Sec. 32 are NEEDS HOLD. Foam and clean agent still locked. On a Canada job, stop any claim that needs S524/S536/S537/S1001/CEC 32 until held. Do not invent S524 battery hours.
- If country = Canada: STOP. Return NEEDS HOLD (CAN/ULC-S524 NAC install). Do not map NFPA 72 rows as CA CODE. Do not state hours or ULC body text. (fixture-166 / fold 29)
- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (the engineer, standing): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "needs LiNK: <id>".
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`). Pin the enforced **NEC** edition for Table 8 separately (not the same as 72). Prefer `fa-nec-table-8-wire-sizing` for the shared R / gauge layer when that skill has already elected ohm/kft.
- NEC Table 8 edition gate (Chunk 19 companion / LOCAL-13 GAP3 close): held ohms below are **NEC 2023** (70-03). **NEC 2026 Ch. 9 Table 8 body is NEEDS HOLD** (not pulled). On a NEC 2026 job (example: TX state min / the site plan-review per held notes site-dallas-nec-2026-local-status-2026-11-04.md` [PARA]): STOP inventing 2026 ohms. Do not tag 2023 Table 8 values as [CODE 2026]. Either hold for LiNK Table 8 2026, or if the job must proceed, use 2023 held ohms only as **ASSUMED / VERIFY** and report the NEC 2026 gap. Never invent numbers.
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). the engineer is engineer of record; no stamp claim. Copy METHOD, not synthetic numbers.

## Basis
- Edition gate (72-16, 72-17): §18.3.7.1 to .6 exist only in NFPA 72-2025. 72-2022 §18.3.7 ends at .2; 72-2019 has no §18.3.7. On a 2019 or 2022 job the CUSTV/CMSTV, MVA, ELL/PTP, and 75°C method is **[PRACTICE]**, not [CODE].
- [CODE] NFPA 72-2025 §18.3.7.1: DC-power-sourced NACs designed and installed per §18.3.7.1 and §18.3.7.3 to .6.
- [CODE] §18.3.7.1.1: starting voltage includes (1) the control unit start terminal voltage (CUSTV) of the power source and the current at the minimum input voltage rating of the appliances, for circuits integrated in the control unit; (2) the control module start terminal voltage (CMSTV) of the control module (CM) at the appliance minimum input voltage rating, for circuits on a CM.
- [CODE] §18.3.7.1.2*: CMs not integrated with the control unit are included in circuit designs. §18.3.7.1.2.1*: where used, module voltage adjustment (MVA) is factored into each circuit.
- [CODE] §18.3.7.1.3*: Class B length from circuit start to the last appliance. §18.3.7.1.4*: Class A length from circuit start to the last appliance on the longest side of the circuit.
- [CODE] §18.3.7.3: length follows the intended path, including right angles and vertical changes; lengths in calcs include the total length of both conductors; the calc form states whether the displayed length is doubled in the calc or already out and back; wire resistance values are not doubled for length and reflect NEC Table 8 or the maker data sheet (include the data sheet if product-specific).
- [CODE] §18.3.7.4*: design by end-line-loaded (ELL) or point-to-point (PTP).
- [CODE] §18.3.7.5: wiring designed for a minimum of 167°F (75°C), or the expected operating temperature if higher. §18.3.7.6: wire size and material meet Ch. 18 and Ch. 14 performance.
- [CODE NEC 2023] NFPA 70-2023 Ch. 9 Table 8, DC resistance at 75°C, uncoated copper, stranded (7), ohm/kft: 18 AWG 7.95; 16 AWG 4.99; 14 AWG 3.14; 12 AWG 1.98; 10 AWG 1.24. (Solid, same table: 18 7.77, 16 4.89, 14 3.07, 12 1.93, 10 1.21.) Table note 2: R2 = R1 [1 + 0.00323 (T2 - 75)] for copper above 75°C. Use the coated column if strands are coated. Cite these ohms as [CODE] only when the enforced NEC is 2023 (or 2020 for 18 to 10 AWG uncoated copper match per 70-08). **NEC 2026 Table 8: NEEDS HOLD.** Do not invent 2026 ohms. Do not cite these as [CODE 2026].
- Annex A, explanatory not requirement [HB]: A.18.3.7 regulated 24 VDC appliances operate from 16 to 33 VDC; use listed current "X mA @ 16 VDC". A.18.3.7.4: ELL is the most conservative and recommended method; PTP needs exact wire distances between every appliance. A.18.3.7.3: count drops and junction-box loops in length.
- [CODE] NFPA 72-2025 §7.2.1(8) (72-13); same item in 2022 (72-20) and 2019 (72-26): NAC voltage drop calculations are part of the documentation package.
- [PRACTICE / maker data] End-of-discharge start value (commonly 20.4 V for 24 V) only where the maker gives no CUSTV. NFPA 72-2025 §18.3.7.1.1 requires CUSTV / CMSTV as the start voltage; 2022 has this only in annex A.18.3.7.1 (72-49).

## Inputs (ASSUME and flag any missing)
1. Appliance count, type, candela. Listed current per appliance at its minimum input voltage (maker UL table).
2. Circuit path length, start to last appliance (Class B) or to the last appliance on the longest side (Class A), including drops and vertical runs.
3. Source: panel (CUSTV) or CM (CMSTV, MVA). Booster supplies use their published start terminal voltage.
4. Appliance listed minimum input voltage (16 V typical for regulated 24 V; confirm).
5. Conductor gauge, stranded or solid, coated or not, expected operating temperature.
6. Class A or B.

## Steps
1. Start voltage: CUSTV (panel circuit) or CMSTV (CM circuit) from the maker [CODE §18.3.7.1.1]. For a CM circuit, apply MVA [§18.3.7.1.2.1]. If no published value, ASSUME end-of-discharge (20.4 V for 24 V) [PRACTICE / maker data] and flag it.
2. Minimum at last appliance = listed minimum input voltage (16 V typical [HB], Annex A.18.3.7, explanatory); confirm on the listing.
3. Keep each listed appliance current at the specified candela and minimum voltage. I_total is the sum. Add maker inrush and sync module effects. The sum is the ELL load. PTP still needs each appliance current.
4. Length: follow the routed path [§18.3.7.3(1)]. Class B: start to last appliance. Class A: start to last appliance on the longest side [§18.3.7.1.4]. Maker guides saying a Class A run can be up to twice as long are a layout hint only [PRACTICE]; covering the return leg back to the panel is also [PRACTICE]. State on the form whether the length shown is one-way and doubled in the calc, or already out and back [§18.3.7.3(3)]. For PTP, record the one-way feet from the previous point to each appliance. The previous point is the source, then the last appliance.
5. Resistance: held Table 8 value at 75°C for the gauge and stranding, not doubled [§18.3.7.3(4)], only when the enforced NEC edition is held (2023 / 2020 match). On NEC 2026: NEEDS HOLD or ASSUMED/VERIFY 2023 ohms with gap (never [CODE 2026]). Correct above 75°C with note 2. Both-conductor ohms for a one-way length L_ft = 2 x L_ft x (ohm/kft) / 1000. For ELL, R_circuit uses the full one-way length. For PTP, use that formula on each segment length, not on the whole run.
6. Method: ELL by default [§18.3.7.4(1)]. PTP only when every segment length in step 4 is known [§18.3.7.4(2)]. State which. Do not check a PTP circuit with the ELL product.
7. Script the method you selected. Use `calcs/fa/lib/nac_vdrop.py`: `ell` or `ptp`.
   - ELL. Lump I_total at the far end. Vdrop = I_total x R_circuit. V_eol = start voltage - MVA - Vdrop. Pass if V_eol is at or above the listed minimum. Report margin, percent drop, and the ELL max one-way length at I_total.
   - PTP. Order appliances from the source outward. Each segment is (one-way feet from the previous point, appliance current at the end of the segment). Current on a segment is the sum of the appliance currents at that point and every point farther from the source. Segment drop = that downstream current x the both-conductor resistance of that segment only. Add the segment drops. Voltage at an appliance = start voltage - MVA - the drops up to that appliance. The reported end voltage is the lowest of those voltages. Pass if that voltage is at or above the listed minimum. Report each segment drop and the worst voltage. Do not multiply I_total by the full-circuit resistance. That product is ELL. It reads low when the appliances are spaced along the run, and it is not a PTP result.
8. Thin margin rule: a small margin with synthetic currents or uncounted MVA/sync loss is reported FAILING until listed data is in.
9. If ELL fails: split the NAC, move the booster, upsize the wire, or rerun as PTP with the measured spacing and the segment sum in step 7. Recheck when candela changes.

## Output
Input table with labels and ASSUMED flags; start voltage basis (CUSTV, CMSTV, MVA); Class and length basis; method (ELL or PTP); Table 8 values used (NEC edition cited; 2026 NEEDS HOLD); per-gauge Vdrop and end voltage (ELL end voltage, or the lowest PTP appliance voltage, with the segment drops); percent drop; pass or fail; ELL max length when that screen was run; fixes. File it as the NAC voltage drop calculation required in documentation [CODE NFPA 72 §7.2.1(8), 2019 / 2022 / 2025 (72-26, 72-20, 72-13)].

## Sources
KB: 60_power-battery-and-voltage-drop/nac-voltage-drop-calculations.md. Worked: EXERCISES/worked/fixture-02-nac-voltage-drop.md, _calc/ex02_nac_vdrop.py (method only; its solid-wire values and "draft ~18.3.7.1" wording are stale). Filed LiNK sources: held notes/held-nfpa-link-72-14-nac-voltage-drop-2025-2026-10-15.md, held notes/held-nfpa-link-70-03-nec-ch9-table8-2023-2026-10-15.md; 70-08 (2020 Table 8). Adoption [PARA]: held notes/the site-dallas-nec-2026-local-status-2026-11-04.md (Chunk 19). Companion: fa-nec-table-8-wire-sizing. _sources 72-08, 72-13, manufacturer-public-guidance-PRACTICE.md. (Paths under held training corpus unless absolute.) fold28: fixture-165, _calc/ex165_campus_nac_sync.py, SKILLS-HANDOFF-2026-11-02-fold28.

## fold 23 restamp (2026-10-29)
- Worked: fixture-151 (`_calc/ex151_nac_evacs_secondary.py`, test `_calc/tests/test_ex151.py`). SHIP-NAC2 14 x 0.20 A, 600 ft, 14 AWG: Veol 9.85 V FAIL vs 16.0 V. Fix: split 2 x 7 on 12 AWG, 1.40 A, Veol 17.07 V PASS [PRACTICE fix].
- Horn/strobe NAC on wet buildings and EVACS speakers in halls are separate checks. Run `fa-speaker-circuit-loss-check` for the speaker side.

## fold 24 restamp (2026-10-29)
- Worked pointer: fixture-151 (NAC vdrop + EVACS booster secondary). Speaker line loss limit 1.0 dB [CODE] NFPA 72-2025 §18.3.7.2 (held). EVACS 24 h + 15 min [CODE] governs over FM 24 h + 5 [OWNER]. Battery spare follow-on: fixture-154 (training / PRACTICE only; PE-185 Verify with engineer of record; not CODE; not approved live design).

## fold 28: campus strobe sync / multi-building negative (fixture-165)
- Voltage drop and sync are related but separate checks. After a NAC pass, still screen visual sync across buildings when a view spans them.
- Room sync [CODE NFPA 72 18.5.5.7.2, 2022=2025]: includes visuals run by separate systems (item 2). Corridor: more than two in view flash in sync [CODE; Lead optional fold29 clause pin on exact 18.5.5.x wording].
- Negative rejected (fixture-165): skip sync across buildings where the view spans them. REJECTED. 18.5.5.7.2(2) covers separate systems.
- Fix patterns [PRACTICE]: one campus sync master (follower power supplies follow the master), or keep each building its own master and close the link with a door so no view spans buildings.
- Sync-module / master loss: strobes may keep flashing unsynced; report trouble [PRACTICE]. Single point of failure on one campus master is [OWNER] (flag; redundant master or a boundary door).
- Foam or clean agent: REJECTED (locked).
- Worked: EXERCISES/worked/fixture-165-campus-nac-sync-multibuilding-strobe.md, _calc/ex165_campus_nac_sync.py. Training value. Verify with the engineer of record. Do not copy synthetic numbers.

## fold 29: campus sync-master redundancy (fixture-167)
- One campus sync master is a SPOF [OWNER]. fixture-165 base left all groups on A-PS1.
- Offer hot-standby sync master (separate enclosure and circuit, auto takeover + trouble) [PRACTICE]. Never tag backup dual-master as CODE. No held NFPA 72 text requires a backup sync master.
- Offer view-break door at the link corridor as [OWNER] architectural option (splits FOV so loss of A master unsyncs A side only).
- Residual: cut of the common sync bus between buildings [OWNER]. Strobes may keep flashing unsynced; report trouble [PRACTICE]. Field sync test at acceptance.
- Held sync CODE stays fixture-165 / 18.5.5.7.2 only. Negatives: dual-master as CODE REJECTED; foam/clean REJECTED.
- Worked: EXERCISES/worked/fixture-167-campus-sync-master-redundancy.md, _calc/ex167_campus_sync_master_redundancy.py. Training value. Verify with the engineer of record.

## fold 29: Canada explicit STOP (fixture-166)
- Intake CA STOP added after Country gate. Worked: EXERCISES/worked/fixture-166-canada-skill-gate-negative-stops.md, _calc/test_ex166_168_b29.py T166. Training value. Verify with the engineer of record.

## Campus NAC voltage drop

Method only. Do not copy the runs as a job result. Ohms are NEC 2023 Chapter 9 Table 8. On a NEC 2026 job those ohms are an [ASSUMED] screen and Table 8 is NEEDS HOLD. Where NEC 2026 is adopted, the non-power-limited fire alarm branch circuit is not a multiwire branch circuit [CODE §760.41(B)]. The end-of-line floor used below is 16.0 V [ASSUMED].

- 14 AWG, 250 ft, 1.6 A: 2.512 V drop, 17.89 V at the end, PASS.
- 12 AWG, 420 ft, 2.1 A: 3.493 V drop, 16.91 V at the end, PASS.
- 12 AWG, 600 ft, 2.4 A: 5.702 V drop, 14.70 V at the end, FAIL. The recorded rerun is 10 AWG on that same length and load, 16.83 V at the end, PASS. Do not guess a gauge change that has not been rerun.
- On a Canada job, stop. CAN/ULC-S524 and CEC Section 32 are NEEDS HOLD. Foam and clean agent stay locked.
