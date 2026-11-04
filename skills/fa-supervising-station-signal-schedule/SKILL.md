---
name: fa-supervising-station-signal-schedule
description: >-
  Use when you must decide which signals a data center FA system sends to the
  supervising station and how each is classed (alarm, supervisory, trouble),
  including BESS gas alarm, gas trouble, exhaust supervision and room fire
  detection (IFC 2024 1207.5.4, 1207.6.1.2.3; NFPA 855-2023 4.8.4, 9.6.5.6.7;
  NFPA 72-2022 Ch 26). Country gate: US or Canada.
---
# Supervising station signal schedule

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed section numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill and use the fire-department notify rows below. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
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
| Gas at or above 10% LFL (low) | Alarm, own BESS GAS zone | CODE on the 9.6.5.6.7 path: 855-2023 9.6.5.6.7(5)(b) requires an alarm signal above 10% LFL (Design practice, 2026-10-23). Rate path rooms: alarm as [PRACTICE], same class. Never supervisory. Label PRACTICE |
| Gas at high setpoint | Alarm (gas) | PARA |
| Off-gas VOC early warning (if separate) | Supervisory | PARA, Verify with the engineer of record |
| Gas detection fault or power loss | Trouble | CODE |
| Exhaust fan or airflow loss, makeup air not proven, damper not open, HOA off Auto | Supervisory | CODE for supervision (IFC 2024 1207.6.1.2.3); class Verify with the engineer of record, conservative supervisory |
| Preaction supervisory (low air, valve, N2) | Supervisory | CODE |
| ASD / VEWFD Alert (DI hall) | Supervisory | [OWNER, synthetic] default. Confirm against the owner program on the job |
| Fire 1 or Action (FM DI leg 1), alone | Alarm (also EVACS alert) | [OWNER] FM map; class as fire alarm to the station |
| DI release (Fire 1 or Action AND low air): solenoid, EVACS pre-discharge, release NAC | Alarm | [PRACTICE] row; basis FM DS 5-32 §2.4.3.2.1.3 [OWNER] plus low air 2022/2025 [CODE]; 2019 preaction [PRACTICE]. Not §23.8.5.4.3 |
| Releasing circuit open, EVACS amplifier failure, loss of primary | Trouble | [CODE] releasing circuit open is Table 14.4.3.2 item 18(9); amplifier failure and loss of primary are NFPA 72-2025 §10.19.1.1 to .1.3 where that path applies |

Alarm receipt within 90 s, and supervisory and trouble receipt, follow NFPA 72-2025 Table 14.4.3.2 items 4(1) and 3(4) [CODE]. Feed these rows to `fa-integrated-systems-test-matrix`.
- Classing gas alarm as supervisory only is a flag. Verify with the engineer of record. Conservative: alarm. Confirm with AHJ and station whether gas alarm is dispatched to the fire department.

## Service selection (all DC jobs, from a worked example)
- Pick the service first: central, proprietary or remote station [CODE NFPA 72 Ch 26, enforced edition].
- Owner security SOC as proprietary station: check the definition (NFPA 72-2025 3.3.306.2) and 26.4 location and staffing rules (same text 2019, 2022, 2025). A single operator with security duties may not qualify. Verify with the engineer of record. Conservative: listed central station for all signals; SOC gets a secondary annunciator only.
- Duct smoke detectors initiate a supervisory signal [CODE NFPA 72-2019 §21.7.4]. NFPA 72-2022 and 2025 §21.7.4 are NEEDS HOLD. Do not assume the same sentence. Where IMC 2021 or 2024 §606.4.1 is adopted, that instrument's supervisory limit applies where a supervising station is required.
- VEWFD Alert is supervisory, no building notification [CODE NFPA 76-2020/2024 8.4.2.2.x where adopted]. Action or Fire 1 on FM jobs is alarm [OWNER] (design practice).
- Waterflow and FA alarm to station as alarm; valve tamper, low air or N2 and fire pump as supervisory [CODE IBC 2024 903.4.1, 903.4.2; 2021 903.4, 903.4.1].
- Path supervision by edition. 2019 and 2022: 26.6.3.3 supervises a single path at 60 min or less and annunciates failure at the station within 60 min. 26.6.3.4 supervises each multipath pathway within 6 h and annunciates failure of any path at the station within 6 h (26.6.3.4(2)) [CODE, enforced edition]. 2025: 26.6.3.3.1 permits one pathway unless the AHJ or another code bars it. 26.6.3.3.2 supervises that path end to end at 60 min, with failure annunciated per Section 10.15. 26.6.3.4 supervises each pathway end to end at 6 h. The 2022 rule that annunciates multipath failure at the station within 6 h is not in the 2025 text. 26.6.3.4(3) covers only failure to complete a transmission, per 10.15 [CODE NFPA 72-2025]. Section 10.15 is general trouble (200 s at 10.15.1; locations 10.15.7 and 10.15.8) and sets no path timing. On a 2025 multipath job, keep 6 h station annunciation of path failure as owner practice [PARA; Verify with the engineer of record, conservative: 6 h]. Do not cite that 6 h station annunciation as a 2025 code rule.
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

## Canada supervising-station and fire-department notify gate

When Country is Canada and the adopted code is NBC 2025, or a provincial code that adopts these NBC sentences:

- A waterflow alarm notifies the fire department [CODE NBC 2025 Div. B 3.2.4.7.(2) and (4)].
- A two-stage alert signal notifies the fire department that the alert was initiated [CODE 3.2.4.7.(3) and (4)].
- Supervisory signals required by 3.2.4.9.(3) and (5) transmit to the fire department [CODE 3.2.4.9.(6) through 3.2.4.7.(4)].
- The means of notification is CAN/ULC-S561. NEEDS HOLD: the body, the installation rules, the service rules, and the timing are not held. Do not invent CAN/ULC-S561 hours or retransmission times. Stop those claims until the text is held.
- NFPA 72 Chapter 26 supervising-station practice is not a substitute for the NBC sentences or for CAN/ULC-S561 [PARA].
- Trouble signals to the fire department are not in the held 3.2.4.7 text. Leave that row [OWNER] until CAN/ULC-S561 is held. Do not mark it CODE.

Verify with the engineer of record.

## US and Canada supervising-station crosswalk

Country gate (US | Canada). One skill. Do not port a row across the gate.

On a US job, waterflow is a fire alarm. Except as §26.2.2 and §29.10.9.7 permit, the supervising station retransmits it immediately [CODE NFPA 72-2025 §26.2.1.1 and §26.2.1.2]. Where verification is required, that check is not more than 90 s [CODE §26.2.2(4)]. The section that sends other supervisory signals to the supervising station is not pinned. Leave it NEEDS HOLD. Do not invent it.

On a Canada job, keep the fire-department notify rows above. The 90 s verification has no held NBC equivalent. Do not tag it, or any other NFPA 72 Chapter 26 row, as Canada code. CAN/ULC-S561 stays NEEDS HOLD. Do not invent hours or retransmission times.

Rejected: inventing CAN/ULC-S561 hours, tagging a US Chapter 26 row as Canada code, and treating foam or clean agent as a signal class. Foam and clean agent stay out of scope.

## Campus proprietary account

Country gate first. The rows in this section are US only. Pin the edition with `fa-code-edition-delta-check`.

One proprietary supervising-station account may cover a multi-building campus under one ownership. The property may be contiguous or noncontiguous [CODE NFPA 72-2025 §26.4.2.2]. Keep each building and each system as its own subpoint. Fire retransmission indicates the building or group of buildings [CODE §26.4.6.1.5].

Staffing is two qualified operators at all times, unless retransmission is automatic [CODE §26.4.5.1 and §26.4.5.2].

A single point of failure on one pathway does not fail the other pathways [CODE §26.6.3.4(2)].

Priority across buildings is alarm, then supervisory, then trouble [PRACTICE]. A multi-owner campus, or central-station service, uses one account per building [PRACTICE].

An owner display with no constant attendance is not a supervising station [CODE §26.4.2.1]. That screen fails. Pass only with a listed proprietary station or a central-station account. The display may remain a secondary annunciator. This does not replace the engineer-of-record check in Service selection.

Canada: stop. CAN/ULC-S561 is NEEDS HOLD. Do not invent CAN/ULC-S561 hours or retransmission times. NFPA 72 is never Canada code. The Canada gates above stay in force.

Rejected: inventing CAN/ULC-S561 retransmission hours, tagging a US §26.4 row as Canada code, and foam or clean-agent subpoints. Foam and clean agent stay out of scope.
