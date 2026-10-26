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
- Canada is out of scope.
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
3. I = sum of listed appliance currents at the specified candela at minimum voltage. Add maker inrush and sync module effects.
4. Length: follow the routed path [§18.3.7.3(1)]. Class B: start to last appliance. Class A: start to last appliance on the longest side [§18.3.7.1.4]. Maker guides saying a Class A run can be up to twice as long are a layout hint only [PRACTICE]; covering the return leg back to the panel is also [PRACTICE]. State on the form whether the length shown is one-way and doubled in the calc, or already out and back [§18.3.7.3(3)].
5. Resistance: Table 8 value at 75°C for the gauge and stranding, not doubled [§18.3.7.3(4)]. Correct above 75°C with note 2. R_circuit = (length of both conductors, ft) x (ohm/kft) / 1000.
6. Method: ELL by default [§18.3.7.4(1)]; PTP only with exact appliance spacing [§18.3.7.4(2)]. State which.
7. Script it: Vdrop = I x R_circuit; V_eol = start voltage - Vdrop. Pass if V_eol >= listed minimum. Report margin, percent drop, and max one-way length at the load.
8. Thin margin rule: a small margin with synthetic currents or uncounted MVA/sync loss is reported FAILING until listed data is in.
9. If it fails: split the NAC, move the booster, upsize wire, or run PTP. Recheck when candela changes.

## Output
Input table with labels and ASSUMED flags; start voltage basis (CUSTV, CMSTV, MVA); Class and length basis; Table 8 values used; per-gauge Vdrop, V_eol, percent drop, pass or fail; max length; fixes. File it as the NAC voltage drop calculation required in documentation [CODE NFPA 72 §7.2.1(8), 2019 / 2022 / 2025 (72-26, 72-20, 72-13)].
