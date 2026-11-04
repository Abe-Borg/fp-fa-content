---
name: fa-bess-gas-relay-map-and-cause-effect
description: >-
  Use when you must write or check the gas-detection relay map, FACP interface
  points, cause-and-effect matrix, and sequence for an indoor Li-ion BESS room
  where gas detection starts the exhaust (IFC 2024 1207.6.1.2 and 916,
  NFPA 855-2023 9.6.5, NFPA 72, IMC 2024 509), including distinct gas
  notification, proof points, and the monitoring-only or network-only trap.
---

# BESS gas relay map and cause and effect

**Intake.** A missing input is ASSUMED (the value and why). Do not present an ASSUMED value as a cited code value. **Scope lock.** The suppression interface is wet pipe, dry pipe, or double-interlock preaction only. Foam, clean agent, water mist, and single-interlock as the basis of design are out of scope. Record and stop. Do not size them. Cite the section and the edition. Do not paste the standard. Unconfirmed section numbers carry VERIFY. Verify judgment calls with the engineer of record. Do not claim a stamp. Country gate (US | Canada). On a Canada job keep this skill. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Pin editions first (`fa-code-edition-delta-check`). Three-layer basis (code, insurer, owner). Most stringent wins. Copy the method, not a sample room's relay names.

## Basis

- [CODE] IFC 2024 1207.6.1.2.4: continuous gas detection per Section 916 starts the exhaust above 25 percent of LFL. Exhaust stays on until below 25 percent of LFL. Trouble on detection power loss comes from 916.5 and from NFPA 855, not from 1207.6.1.2.4. The section title is Ventilation Based on Exhaust Rate.
- [CODE] IFC 2024 1207.6.1.2.3: required exhaust is supervised by a central, proprietary, or remote station per NFPA 72.
- [CODE] IFC 2024 916.8: gas audible and visible signals are distinct from fire alarm and carbon-monoxide alarm. 916.9 is signage next to gas alarm devices. 916.4 is power. 916.5 is standby power or trouble on power loss.
- [CODE] NFPA 855-2023 9.6.5.1.5.4(1) and (3): on the exhaust-rate path, detection starts the exhaust above 25 percent of the mixture LFL, with 2 h detection standby. 9.6.5.6.7 below applies only on the explosion-control path (an NFPA 69 study).
- [CODE] NFPA 855-2023 9.6.5.6.7: (1) start at no more than 10 percent of LFL. (2) stay on so gas stays at or below 25 percent of LFL. (3) 2 h standby. (4) 24 h standby plus 2 h alarm for Li-ion, or as the AHJ requires. (5) annunciation, including an alarm above 10 percent of LFL. Confirm (3) and (4) against the adopted printing before issue. The duration handoff is `ess-isolation-venting-and-duration` and `fa-secondary-power-battery-calc`.
- [CODE] NFPA 72 gas detection that is on a fire alarm system follows the chapters that govern initiating devices, fundamentals, inspection, and protected-premises systems. Pin the edition. NFPA 72 does not set the gas signal class. Set that class in `fa-supervising-station-signal-schedule`. Temporal-3 is fire. Temporal-4 is carbon monoxide.
- [CODE] IMC 2024 509.6.1: fire and smoke dampers are prohibited in hazardous exhaust ducts. 509.5.1: explosive-material systems are prebalanced by duct sizing. Other systems may use fixed-minimum balancing dampers. Applying the no-balancing-damper rule to BESS gas exhaust is a reading (treat vent gas as explosive). Verify with the engineer of record. Conservative assumption: no balancing dampers. Rated shaft enclosure where the duct penetrates a rated wall is 509.6.3. Rated floor and ceiling assemblies are 509.6.2. Ducts that penetrate rated shafts follow 509.6.1.1 to IBC 714.4.1 or 714.4.1.2. Duct layout and demand stay in `ess-exhaust-duct-shaft-and-duct-sprinklers`.

## Hard fails (check these first)

1. Gas detection called monitoring only, an add alternate, or a building-network or BACnet point only, while it is the required exhaust start (IFC 2024 1207.6.1.2.4). Life-safety start and FACP signals are hardwired, supervised contacts. Network points may duplicate. They never replace.
2. Relay landing points not shown (where each contact terminates).
3. Gas horns or strobes on fire-alarm notification circuits, or using temporal-3 or temporal-4.
4. Any fire-alarm or HVAC shutdown sequence that stops the gas exhaust or its makeup air.
5. Fire, smoke, backdraft, or balancing dampers on the gas exhaust duct.
6. No high-gas signal and no trouble signal reaching the FACP.

## Relay map (ASSUMED until the vendor confirms)

Rename the rows to the vendor's relay labels. Do not treat these names as a catalog.

| Relay | Trips at | Lands at | Function |
|---|---|---|---|
| Low-start | Either gas, rising through a setpoint selected at no more than 10 percent of LFL | Exhaust fan starter or VFD, and makeup-air unit or damper | Start and open. Latched. Manual reset only after gas clears |
| Low-alarm | Low (either gas) | FACP monitor module | Gas alarm to the FACP, own zone label. Alarm class, never supervisory: NFPA 855-2023 9.6.5.6.7(5)(b) |
| High-notify | High (either gas, at or below 25 percent of LFL) | Gas horn and strobes on the gas panel, or their own circuit | Distinct gas notification. Also on low: verify with the engineer of record. Conservative assumption: yes |
| High-facp | High | FACP monitor module | High gas to the FACP. If the panel lacks a contact, add an expansion module |
| Fault | Panel fault or power loss | FACP monitor module | Trouble to the FACP and the station. Fail-safe (de-energize on fault) |

- On the 9.6.5.6.7 path, 10 percent of LFL does two jobs. (1) sets the reduction-system start (Low-start). (5)(b) sets an alarm above 10 percent of LFL (Low-alarm). Write both rows. One does not replace the other [CODE NFPA 855-2023].
- Low-start at 10 percent of LFL is [CODE] only on the 9.6.5.6.7 path. The relay trips when measured concentration rises through a setpoint selected at no more than 10 percent of LFL. A clean-air or zero reading does not trip it. On the rate path the code trigger is 25 percent of LFL. The 10 percent start is design practice. Verify with the engineer of record. Conservative assumption: keep 10 percent. Tag each cause-and-effect row with its path.
- Either gas (hydrogen or VOC) at a level trips that level. Repeat the rows per room.
- Shared relays across several rooms: flag them. Per-room fans or dampers need per-room relays or expansion modules.

## FACP monitor points

- Exhaust-fan proof (current switch and duct airflow switch), makeup air proven open, any motorized damper proven open, and hand-off-auto not in Auto. Loss of proof after a command delay (set at commissioning, ASSUMED 30 s to 60 s) is supervisory [PRACTICE].
- Input-count check: if the gas panel has fewer inputs than proof points, move proofs to FACP addressable monitor modules.
- Any motorized damper in the exhaust or makeup path fails open.

## Cause and effect rows (minimum)

Gas low. Gas high. Gas below the low setpoint (exhaust stays on until manual reset). Gas-detection fault or power loss (trouble; starting exhaust on fault needs engineer-of-record verification; conservative assumption: start). Makeup air not proven. Exhaust loss of flow. Room smoke or heat (fire alarm; exhaust keeps running if latched). Waterflow. General HVAC duct smoke (shut recirculating HVAC only, never the gas exhaust). Door hold-opens release on room smoke, fire alarm, and any gas alarm (gas release of the hold-open needs engineer-of-record verification).

Columns: exhaust, makeup air, gas notification, fire-alarm notification, FACP signal class, supervising station, doors.

## Notification

- Gas: amber strobe plus a tone that is not temporal-3 or temporal-4, or a voice message. Sign next to each gas device per IFC 2024 916.9. Distinct-signal duty is 916.8. Tone choice needs engineer-of-record and AHJ verification.
- Fire: temporal-3, clear strobe, on fire-alarm notification circuits.

## Separation interface

The 2 h versus 3 h fire-barrier election sets door ratings and damper ratings on non-hazardous ducts. Hold-opens release on fire alarm. Put the election and the door hardware in the RFI register. Do not invent the rating here. Hand compartment rating to `fire-area-compartmentation-schedule`.

## Steps

1. Get species and setpoints from `fa-bess-gas-detection-layout-and-setpoints`.
2. Run the hard-fail list against the drawings and the controls sheets. Each fail becomes an RFI.
3. Fill the relay map with landing points. Mark ASSUMED where the vendor riser is silent.
4. Build the FACP point list and the input-count check.
5. Write the cause-and-effect matrix and the sequence. Where it touches preaction release, coordinate with `fa-double-interlock-releasing-cause-and-effect` and `preaction-releasing-c-and-e-soo`. Do not rebuild that matrix here.
6. Send signal classes to `fa-supervising-station-signal-schedule` and loads to `fa-secondary-power-battery-calc`.
7. Add an integrated-system test line: gas, exhaust, makeup air, FACP, and station. The test matrix is `fa-integrated-systems-test-matrix`.

## Output

Hard-fail table. Relay map with landings. FACP point list. Cause-and-effect matrix. Sequence notes. Notification schedule. RFI list.

## Integrated-test setpoints

Optional, and only where an energy-storage room is on the campus. The parts-per-million figures in a worked mixture are examples. Use the job mixture LFL. Do not invent maker times. The test rows live in `fa-integrated-systems-test-matrix`.

- Name the path on the row. Concentration-reduction path (an NFPA 69 study): when measured concentration reaches a start setpoint selected at no more than 10 percent of LFL, start concentration reduction and send an alarm to the FACU [CODE NFPA 855-2023 §9.6.5.6.7(1) and (5)(b)]. A reading of zero does not start. That is the low-start relay and the low-alarm relay above. Exhaust-rate path: the code start is when concentration exceeds 25 percent of LFL [CODE §9.6.5.1.5.4(1)]. An earlier start, at a setpoint selected at no more than 10 percent of LFL, is [PRACTICE]. Verify with the engineer of record. Do not call that practice start a substitute for a §9.6.5.6.7 design, and do not fail a rate-path test for lacking a code 10 percent start.
- When measured concentration exceeds 25 percent of LFL, start mechanical exhaust if it is not already running. On the exhaust-rate path that start is [CODE §9.6.5.1.5.4(1)].
- A gas-detector fault or loss of power sends trouble to the FACU [PRACTICE].
- Maker response delay follows listed maker data [ASSUMED].
- On a Canada job, stop. CAN/ULC-S1001 and CAN/ULC-S524 are NEEDS HOLD. Do not map NFPA 4 or NFPA 855 as Canada code.

## Out of scope

Foam, clean agent, water mist, and single-interlock as the sprinkler basis. Do not size the exhaust fan or the duct sprinklers here. See the country gate in this skill.
