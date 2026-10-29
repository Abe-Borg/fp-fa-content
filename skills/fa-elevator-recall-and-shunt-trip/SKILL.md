---
name: fa-elevator-recall-and-shunt-trip
description: >-
  Use when a job has elevators and you must lay out NFPA 72 §21.3 Phase I recall
  detection, the three recall outputs and their trigger map, and the §21.4 shunt
  trip heat detector, switch and supervision rows (2019 / 2022 / 2025
  held). Packet optional; missing inputs ASSUMED. Not the elevator
  controller, ASME A17.1 logic, or sprinkler design.
---
# FA elevator recall and shunt trip

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get edition text not confirmed.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write the word to). Verify with the engineer of record. Do not claim a stamp. Copy METHOD, not synthetic numbers.

## Scope
FA side only. The elevator contractor owns the controller and the ASME A17.1 response. FP owns the sprinklers in the machine room, hoistway and pit (rating, RTI, location, any pit-only valved line). FA owns the recall detectors, the three relay outputs, the shunt trip heat detectors and monitor points, annunciation and C&E rows. No elevator point is a DI release leg [PRACTICE]. Shunt trip is not ITE EPO (EPO stays NFPA 75 §11.4.5, held 2020 / 2024 in 75-08, / NEC 645) [PRACTICE]. Apply only where the job has an elevator; most data halls are single story [PRACTICE]. A space with no elevator, including a diesel pump house, gets no elevator points.

## Basis (held sources by ask id)
- [CODE] NFPA 72-2025 and 72-2022 §21.3* to §21.3.14.2* and §21.4 to §21.4.6, same duties (72-44). Same duties in both editions.
- [CODE] NFPA 72-2019 §21.3* to §21.3.14.2* and §21.4 to §21.4.6, same duties (72-46). = 2022 except §21.3.3.2 (no time-delay clause), §21.3.6 (one paragraph), §21.3.8 (wording), §21.4.5 (printed spacing).
- [CODE] §21.3.1: recall devices connect to the required building FA system. No required system: nonrequired system or a dedicated function FACU marked elevator recall control and supervisory control unit (2025 §21.3.2.1 / §21.3.2.2; 2022 §21.3.2*, one paragraph, same duty).
- [CODE] §21.3.3.1: only lobby, hoistway, machine room, machinery space, control space and control room smoke detectors initiate recall (other automatic detection only where ambient prohibits smoke, §21.3.10*), unless the AHJ requires otherwise. §21.3.3.2: pit waterflow only on a separately valved, pit-only sprinkler line. 2019 also requires that the waterflow switch is provided without time-delay capability (72-46); 2022 / 2025 do not say this. §21.3.4: each device still initiates recall with all others on the same circuit in alarm.
- [CODE] §21.3.5.1 lobby detector, 21 ft (6.4 m) from the centerline of each door in the bank. 2019 and 2022: located on the ceiling within 21 ft. 2025: a maximum of 21 ft ... in accordance with Chapter 17. §21.3.5.2: ceilings over 15 ft or not flat and smooth per Chapter 17.
- [CODE] §21.3.6.1 to .6.3 unsprinklered hoistway: no detector unless ASME A17.1 or smoke relief needs it. 2019 §21.3.6 is one paragraph: detectors only where ASME A17.1/CSA B44 requires them for actuation of the elevator hoistway smoke relief equipment and/or to initiate recall for the two listed spaces (72-46). §21.3.7*: serviceable from outside the hoistway. §21.3.8*: sprinklered hoistway, detector at the top where sprinklers are at the top, in the pit where sprinklers are in the pit (2022 lead-in plus 4 items; 2025 5 items reordered; same duties [PARA]). §21.3.9*: listed for the environment.
- [CODE] §21.3.11 annunciate every recall device. §21.3.12 separate and distinct visible annunciation for hoistway and machine room type devices. §21.3.13 supervisory in lieu of alarm only where the AHJ approves.
- [CODE] §21.3.14 three outputs: (1) designated level, (2) alternate level, (3) machine room / machinery space / control space / control room. §21.3.14.1*: designated output from lobbies other than the designated lobby, machine room type spaces not at the designated level, and sprinklered hoistway devices unless §21.3.14.2(3) applies. §21.3.14.2*: alternate output from the designated lobby, machine room type spaces at the designated level, and hoistway devices at or below the lowest recall level where alternate is above designated.
- [CODE] §21.4.1*: shunt trip heat detector has both a lower temperature rating and a lower RTI than the sprinkler. §21.4.2*: within 24 in. (610 mm) of each sprinkler, per Chapter 17. §21.4.2.1: Annex B methods permitted. §21.4.3*: no time delay on pressure or waterflow switches used for shunt trip. §21.4.4*: control circuit monitored for operating voltage. §21.4.5: loss is a supervisory signal (2025 specified in 21.3.1 or in 21.3.2; 2022 prints specified in or in 21.3.2, same duty [PARA]). §21.4.6: devices monitored for integrity.
- [CODE 2025] Table 14.4.3.2 item 17 fn (h): recall devices that send supervisory are tested annually, same as alarm (72-38).
- [CODE] ECF relay location and monitoring per §21.2.4 / §21.2.8, by edition (72-11, 72-20, 72-24). 2019 and 2022: relay within 3 ft of the controlled component. 2025 (§21.2.4.1): within 3 ft, or within 20 ft where the wiring is in metal raceway or armored cable. Class D exempt. Cite the enforced edition; see `fa-code-edition-delta-check`.
- 2019 (72-46): held. Same duties as 2022 except §21.3.3.2 (pit recall waterflow switch without time-delay capability) and §21.3.6 (unsprinklered hoistways: detectors only where ASME A17.1 requires them for smoke relief and/or recall; 2022/2025 also allow smoke relief detectors required by other codes). Cite the 2019 text as [CODE 2019].
- A17.1 edition pointer [CODE]: IBC 2021 Ch 35 references ASME A17.1-2019/CSA B44-19; IBC 2024 references A17.1-2022/CSA B44-22 (a code viewer IBC-18, FA-16). State amendments not checked. Shunt trip and recall output lines keep Verify with the engineer of record until A17.1 text is held.
- Not held: ASME A17.1/CSA B44 Section 2.8 and 2.27 (edition text not confirmed A17.1 2.8 / 2.27, elevator consultant); Annex B §B.3 heat detection body held as [HB/annex] (72-63, 2019 / 2022 / 2025; equations not rendered as text); rest of Annex B TOC only (72-60). A.21.3 and A.21.4.1 to .4.4 are held as [HB/annex] (72-60, 2019 / 2022 / 2025). No numbers from these.

## Inputs (ASSUME and flag any missing)
1. Enforced NFPA 72 edition; insurer (FM or not); AHJ.
2. Elevators and banks; designated and alternate recall levels; lowest recall level.
3. Lobby door centerlines and ceiling height / type per lobby.
4. Machine room, machinery space, control space, control room: locations and levels.
5. Hoistway sprinklered? Sprinklers at top, pit, both (FP). Pit sprinkler on a separately valved pit-only line? (FP)
6. Shunt trip required? (elevator code / AHJ; A17.1 2.8 not held, ASSUME per elevator consultant). Which sprinklers drive it (machine room only, or hoistway too)? If missing, ASSUME machine room only and flag (QA-20 e20-3).
7. Sprinkler temperature rating and RTI at each shunt trip location (FP). Waterflow or pressure switch used for shunt trip?
8. Required building FA system present? Signal class election: alarm, or supervisory with AHJ approval [OWNER].

## Steps
1. Scope gate per the intake block. Pin the edition. On 2019, cite the 2019 text [CODE 2019] (72-46).
2. Place lobby detectors within 21 ft of each door centerline [§21.3.5.1]; use the edition wording (2019 / 2022 "on the ceiling within"; 2025 "a maximum of ... per Chapter 17"). High or non-flat ceilings per Chapter 17 [§21.3.5.2].
3. Place machine room type detectors. Place hoistway detectors only where sprinklered (top / pit to match sprinklers) or where A17.1 needs them [§21.3.6, §21.3.8]. Serviceable from outside and listed for the environment [§21.3.7, §21.3.9].
4. Pit waterflow as a recall trigger only on a pit-only valved line [§21.3.3.2]; else no. On 2019, the switch has no time-delay capability [2019 §21.3.3.2].
5. Build the trigger map in a script: each device to designated, alternate, and/or machine room output per §21.3.14.1 / §21.3.14.2. Whether hoistway devices also drive output (3) is A17.1 2.27: edition text not confirmed, list as a gap (QA-20 e20-5).
6. Circuit rule: each device still recalls with all others on its circuit in alarm [§21.3.4]. Add a test step.
7. Annunciation: each device at the FACU; distinct visible for non-lobby devices [§21.3.11, §21.3.12]. Class alarm, or supervisory only with AHJ approval recorded [§21.3.13] [OWNER].
8. Shunt trip: heat detector within 24 in. of each driving sprinkler; check rating AND RTI both lower in the script, with a negative test [§21.4.1*, §21.4.2*]. Tag the rating and placement rows [CODE]; tag the detector's signal class [PRACTICE] (§21.4 does not set it; QA-20 e20-1).
9. Switches used for shunt trip: no time delay [§21.4.3*]. Shunt control voltage monitor point, loss = SUPV [§21.4.4*, §21.4.5]. Integrity monitoring of detectors and switches [§21.4.6].
9a. A space with a shunt heat detector also has a recall smoke detector in that space [CODE §21.3]. Shunt trip is not self-resetting where IBC 2021 §3005.5 is adopted [CODE]. Placement, temperature rating, RTI, the 24 in limit, and no time delay stay [CODE §21.4.1 to §21.4.3]. The shunt heat detector's signal class is alarm [PRACTICE]. Do not upgrade that tag. Control-voltage loss stays supervisory [CODE §21.4.5].
9b. Worked fixture, method only. Do not copy it as a job device list. Place the recall detectors, map the three outputs, and keep each shunt-trip heat detector within 24 in. of its sprinkler with no time delay. A space with no elevator, including a diesel pump house, gets no elevator points.
10. Relays: three outputs as ECF interfaces, located and monitored per §21.2.4 / §21.2.8 [CODE by edition: 3 ft on 2019 / 2022; 3 ft or 20 ft in raceway on 2025].
11. FM / DI flags: none of these points is a DI leg. On FM DI jobs carry the intake flag and s2.4.3.2.1.3. VEWFD map per Design practice item 7 is unchanged.
12. Hand off: FP (sprinkler rating, RTI, locations, pit line), elevator consultant and AHJ (A17.1 2.8 / 2.27).

## Output
Device schedule (device, location, level, cite, basis label); trigger map to the three outputs; shunt trip check table (sprinkler rating / RTI vs detector, distance, PASS / FAIL); monitor points (voltage loss SUPV, integrity); C&E rows; annunciation list; ASSUMED list; FP and elevator handoff rows; open the edition text ids; edition note (2022 vs 2025 wording at §21.3.2, §21.3.5.1, §21.3.8, §21.4.5; 2019 vs 2022 at §21.3.3.2, §21.3.6, §21.3.8, 72-46).
