---
name: fa-nac-voltage-drop-check
description: >-
  Use when you must check a DC notification appliance circuit for voltage at the
  last appliance per NFPA 72-2025 §18.3.7.1 to .6 (CUSTV or CMSTV, MVA, ELL or
  PTP, 75°C, both conductors) with NEC 2023 Ch. 9 Table 8 resistance: gauge pass
  or fail and max length. Packet optional; missing inputs ASSUMED. Not AC or
  audio line-loss, SLC, or battery sizing.
---
# FA NAC voltage drop check

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get edition text not confirmed.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write the word to). Verify with the engineer of record. Do not claim a stamp. Copy METHOD, not synthetic numbers.

## Basis
- Edition gate (72-16, 72-17): §18.3.7.1 to .6 exist only in NFPA 72-2025. 72-2022 §18.3.7 ends at .2; 72-2019 has no §18.3.7. On a 2019 or 2022 job the CUSTV/CMSTV, MVA, ELL/PTP, and 75°C method is **[PRACTICE]**, not [CODE].
- [CODE] NFPA 72-2025 §18.3.7.1: DC-power-sourced NACs designed and installed per §18.3.7.1 and §18.3.7.3 to .6.
- [CODE] §18.3.7.1.1: starting voltage includes (1) the control unit start terminal voltage (CUSTV) of the power source and the current at the minimum input voltage rating of the appliances, for circuits integrated in the control unit; (2) the control module start terminal voltage (CMSTV) of the control module (CM) at the appliance minimum input voltage rating, for circuits on a CM.
- [CODE] §18.3.7.1.2*: CMs not integrated with the control unit are included in circuit designs. §18.3.7.1.2.1*: where used, module voltage adjustment (MVA) is factored into each circuit.
- [CODE] §18.3.7.1.3*: Class B length from circuit start to the last appliance. §18.3.7.1.4*: Class A length from circuit start to the last appliance on the longest side of the circuit.
- [CODE] §18.3.7.3: length follows the intended path, including right angles and vertical changes; lengths in calcs include the total length of both conductors; the calc form states whether the displayed length is doubled in the calc or already out and back; wire resistance values are not doubled for length and reflect NEC Table 8 or the maker data sheet (include the data sheet if product-specific).
- [CODE] §18.3.7.4*: design by end-line-loaded (ELL) or point-to-point (PTP).
- [CODE] §18.3.7.5: wiring designed for a minimum of 167°F (75°C), or the expected operating temperature if higher. §18.3.7.6: wire size and material meet Ch. 18 and Ch. 14 performance.
- [CODE] NFPA 70-2023 Ch. 9 Table 8, DC resistance at 75°C, uncoated copper, stranded (7), ohm/kft: 18 AWG 7.95; 16 AWG 4.99; 14 AWG 3.14; 12 AWG 1.98; 10 AWG 1.24. (Solid, same table: 18 7.77, 16 4.89, 14 3.07, 12 1.93, 10 1.21.) Table note 2: R2 = R1 [1 + 0.00323 (T2 - 75)] for copper above 75°C. Use the coated column if strands are coated.
- Annex A, explanatory not requirement [HB]: A.18.3.7 regulated 24 VDC appliances operate from 16 to 33 VDC; use listed current X mA @ 16 VDC. A.18.3.7.4: ELL is the most conservative and recommended method; PTP needs exact wire distances between every appliance. A.18.3.7.3: count drops and junction-box loops in length.
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
5. Resistance: Table 8 value at 75°C for the gauge and stranding, not doubled [§18.3.7.3(4)]. Correct above 75°C with note 2. Both-conductor ohms for a one-way length L_ft = 2 x L_ft x (ohm/kft) / 1000. For ELL, R_circuit uses the full one-way length. For PTP, use that formula on each segment length, not on the whole run.
6. Method: ELL by default [§18.3.7.4(1)]. PTP only when every segment length in step 4 is known [§18.3.7.4(2)]. State which. Do not check a PTP circuit with the ELL product.
7. Script the method you selected. Use `calcs/fa/lib/nac_vdrop.py`: `ell` or `ptp`.
   - ELL. Lump I_total at the far end. Vdrop = I_total x R_circuit. V_eol = start voltage - MVA - Vdrop. Pass if V_eol is at or above the listed minimum. Report margin, percent drop, and the ELL max one-way length at I_total.
   - PTP. Order appliances from the source outward. Each segment is (one-way feet from the previous point, appliance current at the end of the segment). Current on a segment is the sum of the appliance currents at that point and every point farther from the source. Segment drop = that downstream current x the both-conductor resistance of that segment only. Add the segment drops. Voltage at an appliance = start voltage - MVA - the drops up to that appliance. The reported end voltage is the lowest of those voltages. Pass if that voltage is at or above the listed minimum. Report each segment drop and the worst voltage. Do not multiply I_total by the full-circuit resistance. That product is ELL. It reads low when the appliances are spaced along the run, and it is not a PTP result.
8. Thin margin rule: a small margin with synthetic currents or uncounted MVA/sync loss is reported FAILING until listed data is in.
9. If ELL fails: split the NAC, move the booster, upsize the wire, or rerun as PTP with the measured spacing and the segment sum in step 7. Recheck when candela changes.

## Worked screen
Method only. Do not copy it as a job result. Start voltage 20.4 V [PRACTICE, no published CUSTV], minimum 16 V, ELL, no MVA. Fourteen appliances at 0.20 A (2.80 A), 600 ft one-way, 14 AWG stranded: end voltage about 9.85 V, fail. Split into two circuits of seven on 12 AWG (1.40 A each): end voltage about 17.07 V, pass [PRACTICE fix]. A horn or strobe NAC and an EVACS speaker circuit are separate checks. Run `fa-speaker-circuit-loss-check` on the speaker side. A passing battery does not clear a failing NAC. The battery-spare follow-on is training only [PRACTICE]. It is not [CODE] and it is not an approved live design. Verify with the engineer of record. EVACS secondary power stays 24 h + 15 min [CODE] and governs over an FM 24 h + 5 min duration [OWNER]. Speaker line loss stays a separate 1.0 dB check.

## Output
Input table with labels and ASSUMED flags; start voltage basis (CUSTV, CMSTV, MVA); Class and length basis; method (ELL or PTP); Table 8 values used; per-gauge Vdrop and end voltage (ELL end voltage, or the lowest PTP appliance voltage, with the segment drops); percent drop; pass or fail; ELL max length when that screen was run; fixes. File it as the NAC voltage drop calculation required in documentation [CODE NFPA 72 §7.2.1(8), 2019 / 2022 / 2025 (72-26, 72-20, 72-13)].

## Campus strobe sync

Voltage drop and sync are separate checks. A NAC that passes voltage can still fail sync where one view spans buildings.

Visual appliances in a room, including appliances run by separate systems, flash in sync [CODE NFPA 72-2025 §18.5.5.7.2(2); same duty in 2022]. More than two corridor visuals in one view flash in sync [CODE §18.5.5.7.2(3)]. Skipping sync across buildings when the view spans them is rejected.

Practice fixes: one campus sync master, with the other supplies following it, or a master in each building and a door that breaks the view. If the master or a sync module is lost, the strobes may keep flashing out of sync. Report trouble [PRACTICE]. One campus master is a single point of failure [OWNER]. A second master, or a boundary door, is the owner election. Foam and clean agent stay out of scope. Verify with the engineer of record.
