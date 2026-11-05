---
name: fa-speaker-circuit-loss-check
description: >-
  Use when you must check a voice/alarm loudspeaker circuit for electrical line
  loss against the 1.0 dB limit ([CODE] NFPA 72-2025 §18.3.7.2.1, [PRACTICE] on
  a 72-2019 or 2022 job), with module loss (MIA) netted from the budget, compare
  25 V vs 70.7 V, and solve max length; packet optional, missing inputs ASSUMED.
---
# FA speaker circuit loss check

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get edition text not confirmed.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write the word to). Verify with the engineer of record. Do not claim a stamp. Copy METHOD, not synthetic numbers.

## Not this skill
DC NAC voltage drop: `fa-nac-voltage-drop-check`. Amplifier battery: `fa-secondary-power-battery-calc`. ADS and intelligibility decisions are owner/AHJ inputs here, not outputs.

## Basis
- [CODE] NFPA 72-2025 §18.3.7.2.1: AC-power-sourced NACs designed for a maximum of 1.0 dB electrical loss, considering all adjustments (loss or gain) from the primary audio source, through wiring, control unit and control module circuitry, to the last loudspeaker. Also per §18.3.7.2 to .6.
- [CODE] 72-2025 §18.3.7.2.2: CMs not integrated in the CU include module insertion adjustment (MIA) in the design.
- [CODE] 72-2025 §18.3.7.2.3 / .2.4: Class B length start to last loudspeaker; Class A or X start to last loudspeaker on the longest side.
- [CODE] 72-2025 §18.3.7.3 to .5: path length with both conductors; resistance not doubled, per NEC Table 8 or maker sheet; ELL or PTP; 75°C wiring.
- [CODE] NFPA 70-2023 Ch. 9 Table 8, 75°C uncoated stranded copper, ohm/kft: 18 AWG 7.95; 16 AWG 4.99; 14 AWG 3.14; 12 AWG 1.98; 10 AWG 1.24.
- [CODE] 72-2025 §10.19.1.1 to .1.3: amplifier failure (on primary, or on secondary with alarm present) and tone generator failure give trouble. Same numbers and text in 2019 and 2022 (72-56). §10.6.7.1.1 exception (2019 / 2022 same text, 72-65): on secondary, amplifier monitoring only when alarm present.
- NFPA 72-2022: §18.3.7 ends at .2 (Ch. 12 and wire performance). No 1.0 dB limit, no MIA, no ELL/PTP, no 75°C rule (72-16). On a 2022 job all of the above from §18.3.7.2.1 on is **[PRACTICE]**.
- NFPA 72-2019: §18.3 ends at §18.3.6; no §18.3.7 and no speaker dB limit (72-17). On a 2019 job the 1.0 dB limit and the MIA rule are **[PRACTICE]**.
- [HB] NFPA 72-2025 A.18.3.7.2.1 equations (72-21): loss dB = 20 log10(Z / (Z + R)) (a); Z = V^2 / W (b); 0.5 dB max length = 59.25 x V^2 / (R x W) (g), R per 1000 ft pair; 25.2 VRMS uses 635 and 70.7 VRMS uses 4998 for V^2 (h, i). Typical design 1.0 or 0.5 dB. Annex is guidance, usable as [HB] method on any edition.
- [HB] Regression check (72-21): 70.7 V, 19.2 W, R = 4.76 ohm gives Z = 260.338 ohm and -0.157 dB. Scripts reproduce this before use.
- Edition rows:

| Edition | 1.0 dB limit | MIA | Label |
|---|---|---|---|
| 2025 | §18.3.7.2.1(1) | §18.3.7.2.2 | [CODE] |
| 2022 | not in §18.3.7 (ends at .2) | none | [PRACTICE] (72-16) |
| 2019 | no §18.3.7 | none | [PRACTICE] (72-17) |

## Inputs (ASSUME and flag any missing)
1. Enforced NFPA 72 edition (drives labels).
2. Line voltage: 25 V or 70.7 V (25.2 V per annex).
3. Total tap wattage on the circuit and number of speakers.
4. Circuit length on the routed path, Class A/B/X, longest side for Class A or X.
5. Gauge, stranding, temperature (correct above 75°C per Table 8 note 2).
6. CM in the path: published MIA in dB. Amplifier output tolerance if given. Owner loss target if tighter than 1.0 dB (for example 0.5 dB) [OWNER].

## Steps
1. Edition gate: label the 1.0 dB limit [CODE] for 72-2025, [PRACTICE] for 72-2022 and 72-2019. Run the 72-21 regression check in the script first.
2. Length per §18.3.7.2.3 / .2.4 and §18.3.7.3. State one-way vs out-and-back on the form.
3. Script: Z = V^2 / W, R_line = both-conductor length x ohm/kft / 1000, wire loss = 20 log10((Z + R_line) / Z) as a positive dB number, per gauge and voltage.
3a. Module loss: total = wire loss + MIA of every CM in the path + any CU adjustment (a gain reduces it) [CODE 2025 §18.3.7.2.1(2), §18.3.7.2.2; PRACTICE on older editions]. MIA not published: ASSUMED. Get the maker value; until then carry a stated ASSUMED dB and mark the result provisional. Never treat an unpublished MIA as zero.
4. Budget = 1.0 dB, or the owner target if tighter (for example 0.5 dB [OWNER]; the annex calls 0.5 dB typical [HB]). Pass if total loss is within the budget.
5. Define R first: R = loop ohms per 1000 ft of route = 2 x per-conductor ohm/kft (Table 8). This is how this skill reads annex eq g R per 1000 ft pair [HB 72-21]; with it, eq g and this step agree at 0.5 dB with no MIA (`calcs/fp/fa_sk4_check.out`: 742 ft at 70.7 V, 94 ft at 25.2 V, 40 W, 16 AWG). Solve L_max on the wire budget net of module loss: L_max one-way = Z (10^((budget - MIA_total)/20) - 1) / (2 x ohm/kft / 1000). If MIA_total is at or above the budget, the circuit fails at any length. For a 0.5 dB budget with no MIA this matches annex eq g [HB].
6. 25 V vs 70.7 V: at the same wattage, Z at 25 V is about 8 times lower, so loss is much higher [PRACTICE, from the formula]. Prefer 70.7 V for long hall runs unless the owner or AHJ requires 25 V. Report both.
7. If it fails: split the circuit, raise gauge, move to 70.7 V, or relocate the amplifier.
8. Note amplifier supervision (§10.19.1) and battery handoff to `fa-secondary-power-battery-calc` (24 h + 15 min at max load, §10.6.7.2.3 to .2.4).

## Worked screen
Method only. Do not copy it as a job result. A 70.7 V circuit at 60 W and 1,900 ft on 14 AWG is about 1.163 dB of loss (signed form about -1.163 dB) and fails the 1.0 dB budget. The same run on 12 AWG is about 0.751 dB (about -0.751 dB) and passes. A battery calc that passes, for example 15.90 Ah against an 18 Ah pick at 24 h + 15 min, does not clear the failing circuit. Fix the wire, then rerun the loss. The battery-spare follow-on is training only [PRACTICE]. It is not [CODE] and it is not an approved live design. Verify with the engineer of record. The 1.0 dB limit stays [CODE] on NFPA 72-2025. EVACS duration stays 24 h + 15 min [CODE] and governs over FM 24 h + 5 min [OWNER].

## Campus speaker feeders

Method only. Do not copy the runs as a job result. Ohms come from NEC 2023 Chapter 9 Table 8 through `fa-nec-table-8-wire-sizing`. On a NEC 2026 job those ohms are an [ASSUMED] screen. NEC 2026 Table 8 is NEEDS HOLD. Do not invent 2026 ohms and do not tag the 2023 ohms as [CODE] for 2026.

Limit remains 1.0 dB [CODE NFPA 72-2025 §18.3.7.2.1(1)]; [PRACTICE] on 2019 and 2022.

- 70.7 V, 14 AWG, 500 ft one way, 60 W: 0.321 dB, PASS.
- 70.7 V, 12 AWG, 900 ft one way, 120 W: 0.713 dB, PASS. The same run on 16 AWG is 1.696 dB and FAILS.
- On a Canada job, stop. CAN/ULC-S524 and CEC Section 32 are NEEDS HOLD. Do not map NFPA 72 as Canada code. Foam and clean agent stay locked.

## Distributed taps

A lumped load at about half the route length is a fair hand check when equal taps are spread evenly. It is not the record when the loss is close to 1.0 dB. The record walks the circuit backward: each tap is a constant impedance of nominal voltage squared divided by tap watts, and the loop resistance counts both conductors. Ohms stay NEC Chapter 9 Table 8. NEC 2023 and 2020 are held. NEC 2026 Table 8 is NEEDS HOLD. The pass limit stays 1.0 dB [CODE NFPA 72-2025 §18.3.7.2.1(1)]; [PRACTICE] on 2019 and 2022. This pack does not add a ladder solver. When the hand check is within a few tenths of 1.0 dB, leave the result open and verify with the engineer of record. Do not invent ohms.

On a Canada job, stop. CAN/ULC-S524 and CEC Section 32 stay NEEDS HOLD. GAP-B33R8-1 stays open. Foam, clean agent, and single-interlock stay locked.

## Output
Edition and label; input table with ASSUMED flags; per-gauge, per-voltage loss and PASS/FAIL; L_max; MIA used; fixes; open items.
