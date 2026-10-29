---
name: fa-nec-table-8-wire-sizing
description: >-
  Use this when you must pick FA conductor gauge or max length from NEC Ch. 9
  Table 8 ohms (NAC or speaker feeder math shared layer), before or beside
  fa-nac-voltage-drop-check / fa-speaker-circuit-loss-check. Packet optional;
  missing inputs ASSUMED. Supplies R and gauge election only; not voltage-drop
  or speaker dB pass/fail.
---
# FA NEC Table 8 wire sizing

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get edition text not confirmed.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`). Table 8 itself is NEC 2023, not 72; pin 72 when length or drop/dB rules are in play.
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write the word to). Verify with the engineer of record. Do not claim a stamp. Copy METHOD, not synthetic numbers.

## Not this skill
- DC NAC voltage-drop pass/fail and V_eol: `fa-nac-voltage-drop-check`.
- Speaker / AC NAC 1.0 dB electrical loss pass/fail and L_max under a dB budget: `fa-speaker-circuit-loss-check`.
- This skill supplies **R (ohm/kft)**, temperature correction, and a **gauge / max-length election table** only. Hand those numbers to the NAC or speaker skill for the pass/fail step.

## Basis
- [CODE] NFPA 70-2023 Ch. 9 Table 8, DC resistance at 75°C (167°F), uncoated copper, ohm/kft (held 70-03):

| AWG | Solid ohm/kft | Stranded (7) ohm/kft |
|---|---|---|
| 18 | 7.77 | 7.95 |
| 16 | 4.89 | 4.99 |
| 14 | 3.07 | 3.14 |
| 12 | 1.93 | 1.98 |
| 10 | 1.21 | 1.24 |

- Use the coated column if strands are coated (coated values not held here; needs product sheet or further the edition text). Aluminum also in Table 8; FA NAC/speaker feeders are copper unless the sheet says otherwise.
- [CODE] Table 8 Note 2 temperature correction for copper: R2 = R1 [1 + 0.00323 (T2 - 75)], with T2 in °C and R1 the 75°C table value. (Aluminum alpha 0.00330 is in the held note; not used for copper FA runs.)
- [CODE] NFPA 72-2025 §18.3.7.3: length follows the intended path, including right angles and vertical changes; lengths in calcs include the total length of both conductors; the calc form states whether the displayed length is doubled in the calc or already out and back; wire resistance values are **not doubled** for length and reflect NEC Table 8 or the maker data sheet. Label [CODE 2025]. On a 72-2019 or 72-2022 job the both-conductor / Table 8 method is **[PRACTICE]** (72-16, 72-17; run `fa-code-edition-delta-check`).
- [CODE] §18.3.7.5: wiring designed for a minimum of 167°F (75°C), or the expected operating temperature if higher.
- Edition of Table 8: held pull is **NEC 2023 only** (70-03). NEC 2020 Table 8 is held (70-08): uncoated copper 75°C values for 18 to 10 AWG match 2023. Cite NEC 2020 Table 8 [CODE] on a 2020 job.

## Inputs (ASSUME and flag any missing)
1. Circuit kind: DC NAC, or speaker / AC NAC feeder (for how the budget is stated later).
2. Conductor: solid or stranded (7); coated or uncoated. Default ASSUMED: uncoated stranded copper (typical FA).
3. Expected operating temperature (°C). Default ASSUMED 75°C (no correction).
4. One-way path length (ft), Class A/B/X as applicable, and whether the form shows one-way or already out-and-back.
5. For a NAC length election: current I (A) and allowable voltage drop V_allow (V) = start voltage minus listed minimum (those values come from the NAC skill / maker; here they are inputs only).
6. For a speaker length election: allowable wire resistance R_budget (ohm) from the speaker skill (from Z and dB budget net of MIA), or state I/V style is N/A and only report ohm/kft.
7. Gauges to screen (default 18/16/14/12/10).

## Steps
1. Pick column: stranded (7) vs solid; uncoated vs coated. State ASSUMED if the product sheet is missing. Typical FA: uncoated stranded.
2. Read R1 from the held Table 8 row at 75°C [CODE 70-03].
3. If T2 > 75°C, correct: R2 = R1 [1 + 0.00323 (T2 - 75)]. If T2 = 75, R = R1. Below 75°C without a sheet: stay at R1 and note the conservative side for copper (lower T lowers R).
4. Length rule pointer: both-conductor length for circuit R [CODE 2025 §18.3.7.3; PRACTICE on 2019/2022]. Do **not** double ohm/kft. R_circuit = (length of both conductors, ft) x (ohm/kft) / 1000.
5. Build a small gauge table in a script. For each gauge report:
   - ohm/kft (after temp correction);
   - R_circuit at the stated length (both conductors);
   - for NAC: max one-way length at stated I and V_allow: L_one_max = V_allow / I / (2 x ohm/kft / 1000);
   - for speaker: max one-way length at stated R_budget: L_one_max = R_budget / (2 x ohm/kft / 1000);
   - or, if only screening gauges for a fixed length, list R_circuit and leave pass/fail to the handoff skill.
6. Elect the smallest (or owner-preferred) gauge that meets the length/budget screen. Flag ASSUMED loads.
7. Hand off: NAC V_eol / percent drop / PASS-FAIL to `fa-nac-voltage-drop-check`; speaker dB loss / PASS-FAIL to `fa-speaker-circuit-loss-check`. Do not restate those pass rules here.

## Output
Input table with ASSUMED flags; stranding/coating/temp basis; Table 8 R1 and R2 used; per-gauge ohm/kft and max-length (or R_circuit) table; elected gauge; handoff note to NAC or speaker skill; NEC edition cited (2020 held 70-08; 2023 held 70-03).
