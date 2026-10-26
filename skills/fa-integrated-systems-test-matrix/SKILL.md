---
name: fa-integrated-systems-test-matrix
description: >-
  Use when you must build the NFPA 4 integrated systems test (IST) matrix and releasing ITM rows for a data center hall: one scenario per C&E row across FA, DI preaction release, HVAC, EPO, doors, elevators, gas exhaust and the supervising station, with edition-keyed NFPA 72 Ch 14 test items.
---
# Integrated systems test matrix and releasing ITM

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Canada is out of scope.
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
- Release only from both DI legs [CODE NFPA 72 23.8.5.4.3; 2019 items (1) to (3), 2022/2025 adds (4)].

## Relation to other skills
- The FP workflow `commissioning-ist-acceptance-packet` owns the acceptance and IST program stack. This skill only builds the FA scenario rows and FA ITM rows that feed it. Do not duplicate the program.
- Power isolation timing is owned by the FP workflow `power-isolation-disconnect-control`; take its trigger election as an input.

## Steps
1. Pull every C&E row from the releasing, HVAC/door, elevator, fire pump, gas relay and station skills.
2. One IST scenario per row: initiating event, expected outputs per system, station class, pass criteria, who witnesses.
3. Script checks: VEWFD Alert sounds nothing and is never a release leg [OWNER]; release only on leg 1 AND leg 2; hall inputs do not recall elevators; every row has a basis.
4. EPO: FA monitors only by default [PRACTICE]. FA-to-EPO trip is Verify with the engineer of record (owner and insurer decide; see `power-isolation-disconnect-control`).
5. Add edition-keyed ITM rows (secure and restore, counting zone, ASD end-port, item 8 battery).
6. Who secures the preaction valve (FP or FA) is an open coordination item [PRACTICE].
7. Export the matrix as CSV for the test log.

## Output
IST matrix CSV, ITM row table by edition, judgment-call list, open items.
