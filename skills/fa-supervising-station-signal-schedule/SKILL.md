---
name: fa-supervising-station-signal-schedule
description: >-
  Use when you must decide which signals a data center FA system sends to the
  supervising station and how each is classed (alarm, supervisory, trouble),
  including BESS gas alarm, gas trouble, exhaust supervision and room fire
  detection (IFC 2024 1207.5.4, 1207.6.1.2.3; NFPA 855-2023 4.8.4, 9.6.5.6.7;
  NFPA 72-2022 Ch 26).
---
# Supervising station signal schedule

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed section numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Canada is out of scope.
- Pin enforced editions first (IFC, NFPA 72, NFPA 855, NFPA 69, IMC); run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis
- [CODE] IFC 2024 1207.5.4: ESS room fire detection signals to a central, proprietary or remote station, or approved constantly attended location.
- [CODE] NFPA 855-2023 4.8.4: detection alarm signals to a supervising station per NFPA 72.
- [CODE] NFPA 855-2023 9.6.5.6.7(5) (the edition text VERIFY-01): annunciation of gas detection trouble and of alarm above 10% LFL. 855-2023 4.8.4: supervising station per NFPA 72.
- [CODE] IFC 2024 1207.6.1.2.3 (Supervision): required exhaust supervised by a central, proprietary or remote station per NFPA 72, or audible and visible signal at a constantly attended on-site location. 1207.6.1.2.4 sets the gas start (25% LFL) only; it does not set a trouble signal. Gas detection power-loss trouble is IFC 2024 916.5 (FA-SKILLS-verify-01) plus NFPA 855-2023 9.6.5.6.7(5).
- [CODE] NFPA 72-2022 26.3.8.3 (Disposition of Signals): what the station does with each signal once received. It does not classify signals (the edition text VERIFY-01). Use it only for disposition.
- Signal class (alarm vs supervisory vs trouble) for gas and exhaust points: no held code text classes them. NFPA 72-2022 17.10.2.2 gives no signal type (the edition text VERIFY-01). Class is Verify with the engineer of record with the conservative default in the table below (gas alarm as alarm, faults as trouble, exhaust loss as supervisory). Confirm with AHJ and station.
- [HB] NFPA 72-2022 A.23.8.4.7 example priority table has no gas row. NFPA 72 does not class gas signals. Gas alarm as Life Safety priority by analogy to hazmat and CO is [PARA].

## Default schedule (conservative)
| Event | Class | Tag |
|---|---|---|
| Smoke or heat in BESS room | Fire alarm | CODE |
| Waterflow | Fire alarm | PARA |
| Gas at or above 10% LFL (low) | Alarm, own BESS GAS zone | CODE on the 9.6.5.6.7 path: 855-2023 9.6.5.6.7(5)(b) requires an alarm signal above 10% LFL (, DC FA Design practice 2026-10-23). Rate path rooms: alarm as [PRACTICE], same class. Never supervisory. Label PRACTICE |
| Gas at high setpoint | Alarm (gas) | PARA |
| Off-gas VOC early warning (if separate) | Supervisory | PARA, Verify with the engineer of record |
| Gas detection fault or power loss | Trouble | CODE |
| Exhaust fan or airflow loss, makeup air not proven, damper not open, HOA off Auto | Supervisory | CODE for supervision (IFC 2024 1207.6.1.2.3); class Verify with the engineer of record, conservative supervisory |
| Preaction supervisory (low air, valve, N2) | Supervisory | CODE |
- Classing gas alarm as supervisory only is a flag. Verify with the engineer of record. Conservative: alarm. Confirm with AHJ and station whether gas alarm is dispatched to the fire department.

## Service selection (all DC jobs, from a worked example)
- Pick the service first: central, proprietary or remote station [CODE NFPA 72 Ch 26, enforced edition].
- Owner security SOC as proprietary station: check the definition (NFPA 72-2025 3.3.306.2) and 26.4 location and staffing rules (same text 2019, 2022, 2025, 72-54). A single operator with security duties may not qualify. Verify with the engineer of record. Conservative: listed central station for all signals; SOC gets a secondary annunciator only ( row 5).
- Duct smoke detectors report supervisory only where a supervising station is required [CODE NFPA 72 21.7.4; IMC 2021/2024 606.4.1 where adopted].
- VEWFD Alert is supervisory, no building notification [CODE NFPA 76-2020/2024 8.4.2.2.x where adopted]. Action or Fire 1 on FM jobs is alarm [OWNER] (design practice).
- Waterflow and FA alarm to station as alarm; valve tamper, low air or N2 and fire pump as supervisory [CODE IBC 2024 903.4.1, 903.4.2; 2021 903.4, 903.4.1].
- Path supervision by edition (72-77, a worked example). 2019 and 2022 26.6.3.3: a single path is supervised at 60 min or less and its failure reaches the station within 60 min; 26.6.3.4 multipath: each path within 6 h. 2025 26.6.3.3.1 permits one pathway unless the AHJ or another code bars it; 26.6.3.3.2 keeps the 60 min end-to-end integrity check [CODE, enforced edition]. 2025 failure annunciation points to another section whose text is not held; do not cite it until pulled. On 2025 multipath jobs keep 6 h station annunciation as the design value (Design practice design practice) [PARA; Verify with the engineer of record, conservative: 6 h]. Do not carry the 2022 station annunciation wording onto a 2025 job.
- Default: two paths even on a 2025 job, each supervised at 60 min or less [OWNER; PRACTICE; Verify with the engineer of record, conservative: two paths].
- Record the pathway pair (for example cellular plus IP) and a signal time budget from vendor data, ASSUMED until confirmed.

## Steps
1. List every off-normal event from the C&E.
2. Class each per the table. Note where code is silent.
3. Confirm each is a distinct zone or point at the station, not a combined common trouble.
4. Confirm the transmission path is hardwired to the FACP and its communicator, not BMS.
5. Record station disposition per NFPA 72-2022 26.3.8.3 and owner notification lists. Do not cite 26.3.8.3 for the class.

## Output
Signal schedule with class, basis, station action, zone label, open items, delta vs NFPA 72-2022.
