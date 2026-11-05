---
name: fa-integrated-systems-test-matrix
description: >-
  Use when you must build the NFPA 4 integrated systems test (IST) matrix and releasing ITM rows for a data center hall: one scenario per C&E row across FA, DI preaction release, HVAC, EPO, doors, elevators, gas exhaust and the supervising station, with edition-keyed NFPA 72 Ch 14 test items.
---
# Integrated systems test matrix and releasing ITM

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Pin the enforced editions first; run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis
- [CODE NFPA 4-2021/2024 4.5.1]: IST plan elements (eleven); 4-2021 = 4-2024 on compared text (4-02, 4-03). 4.5.3.1 If vs 2027 "Where" is cosmetic. Scenario run and validate per 4.5.4 to 4.5.6 [PARA, 4-04].
- [HB] NFPA 75-2024 Annex A is guidance only; A.9.2.1 (prefer ASD transport under 90 s) is 2024 only. Code floor stays 120 s [CODE NFPA 72-2025 17.7.4.6.2.1].
- [CODE NFPA 72 14.2.6.4 and 14.2.6.6]: secure suppression before FA test, restore after; 2019, 2022, 2025 (72-30).
- [CODE Table 14.4.3.2 18(8)]: counting-zone test at least four locations, all editions (72-28, 72-38).
- [CODE Table 14.4.3.2 17(7)(d)]: ASD end-port test. 2019: required even with listed airflow supervision. 2022/2025: only where listed airflow supervision is absent (72-29).
- [CODE Table 14.4.3.2 item 8]: secondary power test against the battery calc demand record.
- FM DI release (company default): (Fire 1 or Action OR manual) AND low air AND NOT isolated. Basis: FM DS 5-32 §2.4.3.2.1.3 (Jan 2026) [OWNER/insurer] plus low-air supervisory 2022 §17.17.2.2.2 and 2025 §17.19.2.2.2 [CODE]; 2019 preaction low-air [PRACTICE]. Do not cite §23.8.5.4.3 for this row; low air is not a detector. Two-leg cross-zone rows and Table 14.4.3.2 item 18(4) apply only on non-FM jobs or where the owner requires cross-zone.

## Relation to other skills
- The FP workflow `commissioning-ist-acceptance-packet` owns the acceptance and IST program stack. This skill only builds the FA scenario rows and FA ITM rows that feed it. Do not duplicate the program.
- Power isolation timing is owned by the FP workflow `power-isolation-disconnect-control`; take its trigger election as an input.

## Steps
1. Pull every C&E row from the releasing, HVAC/door, elevator, fire pump, gas relay and station skills.
2. One IST scenario per row: initiating event, expected outputs per system, station class, pass criteria, who witnesses.
3. Script checks: VEWFD Alert sounds nothing and is never a release leg [OWNER]; release only on (leg 1 OR manual) AND low air AND NOT isolated (count release states in the truth table and hand check); hall inputs do not recall elevators; every row has a basis.
4. EPO: FA monitors only by default [PRACTICE]. FA-to-EPO trip is Verify with the engineer of record (owner and insurer decide; see `power-isolation-disconnect-control`).
5. Add edition-keyed ITM rows (secure and restore, counting zone, ASD end-port, item 8 battery).
5a. DI plus EVACS seed rows (one hall, synthetic example; method from NFPA 72-2025 Table 14.4.3.2 [CODE]; signal class tags [PRACTICE] unless noted):
   - Visual inspection, item 1 (see Table 14.3.1).
   - ASD end-port smoke test to Fire 1, item 17(7)(d).
   - Low air trip: supervisory only, no release, item 17(10)(b).
   - Riser valve tamper, item 17(10)(a).
   - Fire 1 AND low air: solenoid energizes, EVACS pre-discharge, release NAC, supervising-station alarm, item 18(6).
   - Open each releasing circuit: trouble, item 18(9).
   - Fire 1 alone: EVACS alert and supervising-station alarm, no release, item 2(1).
   - EVACS amplifier failure: backup amplifier takes over, item 5(1).
   - Voice intelligibility at acceptance, item 22(2).
   - Supervising-station alarm receipt within 90 s, item 4(1); supervisory and trouble receipt, item 3(4).
   - Releasing FACU and EVACS on battery: loss of primary is trouble, item 8, checked against the battery demand record.
   - ECF interface: EVACS pre-discharge relay from the releasing FACU, item 24.
   - Leave item 18(4) cross-zone out on FM single-leg jobs.
   - ASD Alert to the supervising station as supervisory: synthetic owner default [OWNER]. Confirm against the owner program on the job.
6. Who secures the preaction valve (FP or FA) is an open coordination item [PRACTICE].
7. Export the matrix as CSV for the test log.

## Output
IST matrix CSV, ITM row table by edition, judgment-call list, open items.

## Campus wet and double-interlock rows

Integrated testing is still required when a written plan is not required [CODE NFPA 4-2024 §4.5.3.1]. The functional matrix is NFPA 4-2024 §4.5.1 item (6) [CODE]. That item is closed. Do not mark it unheld. Do not invent the other plan-item sentences. Air-sampling and smoke sensitivity test rows stay with the Chapter 14 table already used here. No new rows. Synthetic campus only. Do not copy the rows onto a hall.

- Waterflow, wet building: fire alarm, supervising-station alarm, and voice in that building. No elevator recall. General waterflow is not a Phase I initiator [CODE NFPA 72 §21.3.3.1]. An owner add is [OWNER]. Verify with the engineer of record.
- Double-interlock detection only: pre-alarm or alarm. No valve release.
- Double-interlock low air only: supervisory. No release.
- Double-interlock detection and low air: release, waterflow, voice, and supervising station. No elevator recall. Release is not a Phase I initiator.
- Elevator lobby smoke: Phase I recall [CODE NFPA 72 §21.3.3.1]. A dedicated valved pit line may recall on its own waterflow [CODE §21.3.3.2]. Detail is `fa-elevator-recall-and-shunt-trip`.
- Generator-room detection: room ventilation shuts down [CODE NFPA 37-2024 §11.3.4, where adopted]. Fuel stays open. The interface is `fa-hvac-door-and-lock-interfaces`.
- Supervising-station path loss: trouble at the station.
- Energy-storage gas, optional and only where that room is on the campus. Detail is `fa-bess-gas-relay-map-and-cause-effect`.
  - Concentration-reduction path: when measured concentration reaches a start setpoint selected at no more than 10 percent of LFL, start concentration reduction and send an alarm to the FACU [CODE NFPA 855-2023 §9.6.5.6.7(1) and (5)(b)]. A reading of zero does not start. Exhaust-rate path: that early 10 percent start is [PRACTICE], not [CODE]. The code start on the rate path is the 25 percent row. Do not fail a rate-path test for lacking a code 10 percent start.
  - When measured concentration exceeds 25 percent of LFL, start mechanical exhaust if it is not already running [CODE §9.6.5.1.5.4(1) on the exhaust-rate path].
  - Detector fault or power loss: trouble at the FACU [PRACTICE].
  - Maker response delay: use listed maker data [ASSUMED]. Do not invent a time.
- Release only when both double-interlock conditions are present. Detection alone and low air alone never release.
- Canada: stop. CAN/ULC-S1001 is NEEDS HOLD. Do not map NFPA 4 or NFPA 72 as Canada code. Do not invent Canadian integrated-test rows. Foam, clean agent, and single-interlock stay locked.

## Commissioning plan rows

These rows sit on the matrix header and on each scenario. They do not replace the NFPA 4 functional matrix. NFPA 4-2024 §4.5.1(6) stays closed.

The commissioning plan includes testing procedures [CODE NFPA 3-2024 §5.2.3.2(8)], testing of integrated systems where that testing applies [CODE §5.2.3.2(9)], and the frequency set for periodic integrated systems testing where that testing applies [CODE §5.2.3.2(11)]. Put the frequency on the matrix header. Update the plan with the sequence of operation for fire protection and life safety systems [CODE §5.3.3(2)] and with an issues log [CODE §5.3.3(8)]. Add an issues-log column on each row.

Map the sequence and the wet, dry, and double-interlock cause and effect under §5.3.3(2) [PRACTICE]. Map the integrated-test scenarios under §5.2.3.2(9) and (11). Map acceptance rows under §5.2.3.2(8) [PRACTICE]. Chapter 14 notes in this skill are pointers. The 2025 notification-appliance rows in Table 14.4.3.2 are NEEDS HOLD. Do not invent those frequencies as code. A speech-transmission-index field pass stays [OWNER]. Do not invent it.

On a Canada job, stop. CAN/ULC-S1001 and CAN/ULC-S536 are NEEDS HOLD. Do not map NFPA 3, NFPA 4, or NFPA 72 as Canada code. Foam, clean agent, and single-interlock stay locked.

## Worked double-interlock rows

Synthetic hall only. Do not copy the rows onto a live zone.

- Second-level detection alone: alarm, no release. The trip setpoint stays [ASSUMED]. Verify with the engineer of record. Do not encode 0.2 %/ft as [CODE].
- Low air alone: supervisory, no release. On a double-interlock or preaction job, 2019 preaction low-air supervisory is [PRACTICE]. 2022 §17.17.2.2 is [CODE]. Citing 2025 §17.17.2.2 is NEEDS HOLD. The 2025 number is §17.19.2.2.2.
- Second-level detection and same-zone low air: release [OWNER]/insurer. Releasing-service listing and the §23.11 framework stay [CODE]. That section does not prescribe this Boolean.
- Disconnect active: no release [CODE §23.11.5]. The disconnect is a physical switch [CODE §23.11.5.2]. Operating it is supervisory [CODE §23.11.5.1].
- Every cause-and-effect row has a matrix row [CODE NFPA 4-2024 §4.5.1(6)]. That item stays closed.
- Alarm verification on a releasing circuit stays [PRACTICE]. Do not cite §23.8.5.4.3(3) as a code ban.

Foam, clean agent, and single-interlock stay locked.
