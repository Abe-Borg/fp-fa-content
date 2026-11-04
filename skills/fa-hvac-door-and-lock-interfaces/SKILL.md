---
name: fa-hvac-door-and-lock-interfaces
description: >-
  Use when you must write the FA side of HVAC, damper, duct detector, door hold-open and electrically locked door interfaces for a data center per NFPA 72 Ch 21 (2019, 2022, 2025), IMC 606, NFPA 90A, NFPA 75, NFPA 101 and IBC 716/1010, including relay distance, signal class and unlock timing.
---
# HVAC, damper, door and lock interfaces

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Pin the enforced editions first; run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis
- [CODE NFPA 72-2025 21.2.4.1]: interface relay within 3 ft, or within 20 ft in metal raceway or armored cable; Class D exempt (21.2.4.2). 2019 and 2022: 3 ft only, no 20 ft option (72-20, 72-24). 21.2.8: monitored per 12.6.
- [CODE NFPA 72 21.7.2]: detection devices that run HVAC, dampers, fans or doors are monitored for integrity when on the FA system.
- [CODE NFPA 72 21.7.4]: duct smoke detectors initiate supervisory; alarm only per 21.7.4.1 or .2. Same 2019, 2022, 2025. IMC 2021/2024 606.4.1 where adopted: supervisory only where a supervising station is required.
- [CODE IMC 2021/2024 606.2.1, 606.2.3, 606.4 where adopted; NFPA 90A 6.4.2.1]: return over 2,000 cfm, common returns over 15,000 cfm, fan shutdown on activation. Return cfm is project data; if missing ASSUME return = supply, Verify with the engineer of record.
- [OWNER]/insurer FM DS 5-48 and 5-32: duct detectors with fan interlock; with complete room coverage, return detectors may drop. No automatic smoke exhaust in DP rooms; if code forces it, start from waterflow.
- [CODE NFPA 75-2024 §11.4.5.1, where NFPA 75 is adopted or the owner elects it]: an approved means disconnects power to electronic equipment in the information-technology room or in designated zones. [CODE §11.4.5.3]: activating that HVAC disconnect closes all required fire and smoke dampers. §9.2.5 smoke detection runs dampers in plenum spaces. Automatic power-off on detection is co-owned with `power-isolation-disconnect-control`. This skill does not set that sequence. Do not map NFPA 75 as Canada code.
- [CODE NFPA 72 21.9, 21.10, same 2019/2022/2025, 72-43, 72-46]: 21.9.2 and 21.9.3 monitoring; 21.9.4 fail-close holders need no secondary power; 21.10.2 and 21.10.3 locks on FACU secondary unlock within 10 min of primary loss; 21.10.4 independent fail-safe supply exempt; 21.10.5 unlock before or with public-mode notification; 21.10.6 stay unlocked until manual reset.
- Which doors unlock or release comes from IBC 2021/2024 716.2.6.6 and 1010.2.x, NFPA 101 7.2.1.6 and 7.2.1.8.2, NFPA 80 [CODE pointers where adopted].
- Gas exhaust: never shut down by FA or HVAC sequences (see `fa-bess-gas-relay-map-and-cause-effect`).

## Company pins
- FA-DI-CE = (Fire 1 OR the FACU manual station) AND same-zone low air. No cross-zone. Never cite §23.8.5.4.3 for that AND.
- Dry and double-interlock low air: supervisory only [CODE NFPA 72 §17.19.2.2.2(A)]. Low air alone never unlocks a door and never releases a hold.
- A duct detector is supervisory [CODE NFPA 72-2025 §21.7.4, same in 2019 and 2022]. It stops its own fan only. It never unlocks a door and never releases a hold.
- Pump house (EX-153): the duct detector is supervisory and stops its own non-engine fan only. It does not release a hold and it does not unlock. Do not stop diesel combustion air or engine cooling air on a fire-alarm signal. That stop is not resolved. It stays pending engineer-of-record confirmation. Non-engine HVAC fan stop on alarm stays [OWNER]/[PRACTICE] until that confirmation. IBC 716 hold-open release stays [PRACTICE].
- Doors unlock and holds release on wet waterflow, double-interlock Fire 1, or the FACU manual station. Not on low air, valve tamper, or a duct detector.
- Hold-open release and egress unlock are two outputs. They may share a trigger. They do not share a code basis.
- Do not delay door unlock or hold release to the double-interlock solenoid. Doors follow the first alarm (Fire 1). Release still needs low air, and that may never come.
- Secondary power: building FACU 24 h + 5 min [CODE]; EVACS 24 h + 15 min [CODE]; releasing FACU 90 h + 10 min [OWNER FM DS 5-40]. Never put 90 h on EVACS or the building FACU.
- Wet, dry, and double-interlock only. No foam. No clean agent. See the country gate in this skill.

## Two outputs, two bases
- Egress unlock on loss of lock power: [CODE IBC 2021 §1010.2.11, where adopted; the authority having jurisdiction confirms. The 2024 number is one lower]. Loss of power to the electric lock unlocks the door.
- Egress unlock on fire alarm for a general locked egress door: [PRACTICE]/[OWNER]. Fire-alarm unlock on that path is for sensor release and for 2024 elevator lobby doors.
- Hold-open release on alarm: [PRACTICE]/[OWNER]. IBC 716 hold-open text is not held. Leave the tag [PRACTICE].
- Fail-safe magnet release on loss of magnet power: [PRACTICE].
- Waterflow as alarm: [PRACTICE] until the text is held. Do not upgrade the tag.

## Door and HVAC cause and effect
| Input | Class | Hold release | Egress unlock | Fan |
|---|---|---|---|---|
| Wet waterflow | Alarm [PRACTICE] | Yes | Yes | Per HVAC cause and effect |
| Double-interlock Fire 1 | Alarm [OWNER FM DS 5-32] | Yes, at Fire 1 | Yes, at Fire 1 | Per HVAC cause and effect |
| Double-interlock FACU manual | Alarm | Yes | Yes | Per HVAC cause and effect |
| Double-interlock solenoid | Release | Already released | Already unlocked | n/a |
| Lock power loss | Power | No | Yes [CODE IBC 2021 §1010.2.11] | n/a |
| Magnet power loss | Power | Yes [PRACTICE] | No | n/a |
| Duct detector | Supervisory [CODE §21.7.4] | No | No | Own unit off [PRACTICE where IMC is adopted] |
| Dry or double-interlock low air | Supervisory | No | No | No |
| Valve tamper | Supervisory | No | No | No |

## Negatives
The script rejects each of these.
1. Low air unlocks egress. Pipe supervisory was treated as half a fire signal, or mapped to the common alarm relay.
2. A duct detector unlocks or releases holds. Supervisory was wired into the alarm output group. The duct relay drives the fan only.
3. Unlock or hold release waits for the double-interlock solenoid. The door relay was hung on the release output. Map it to Fire 1 or the manual station.
4. One relay serves both hold release and unlock under one cited basis. Those are two outputs. Give each its own tag.

## Steps
1. Unit list: each AHU, fan wall, DOAS, CRAH with supply and return cfm. Run the duct detector triggers per basis; each detector supervisory.
2. Fan stop per IMC where adopted; fan wall shutdown on hall waterflow is Verify with the engineer of record (conservative stop; owner weighs cooling loss).
3. Relay distance check per edition (3 ft or 20 ft rule).
4. Door list from architect: hold-opens (release, monitoring, power), locks (power source, unlock time, latch).
5. Script checks: unlock delay at or under 10 min on FACU power, no auto-relock on alarm clear, unlock at or before NAC, VEWFD Alert unlocks nothing [OWNER] (design practice).
6. Lock loads not automatically disconnected go into the battery calc [PARA, 10.6.7.2.13]. Default [PRACTICE]: independent fail-safe lock supplies.
7. BESS rooms: hold-opens release on FA; release on gas alarm is Verify with the engineer of record, conservative yes. 2 h vs 3 h barrier election from the fire-protection designer sets door and damper ratings.
8. Build two door output groups: hold release and egress unlock. Map each to wet waterflow, double-interlock Fire 1, and the FACU manual station. Map neither to low air, tamper, or duct smoke. Run the cause-and-effect table, including the four negatives. Each row must pass.
9. Dry waterflow door action is not code. Assume it unlocks and releases holds, and verify with the engineer of record.
10. Diesel pump house (EX-153): the duct detector stops its own non-engine fan only and does not release holds. Leave engine combustion air and cooling air running. Stopping them on alarm is not resolved. It stays pending engineer-of-record confirmation. Campus integrated-test rows stay with the cause-and-effect skill (EX-152).

## Output
Duct detector schedule with basis per detector, fan stop matrix, relay distance check, door and lock table with pass or fail, C&E rows, open items, delta vs edition.

## Generator-room ventilation

This is the engine enclosure, not the diesel pump house. The pump-house rule above stays: a duct detector stops its own non-engine fan only.

- Where mechanical ventilation of the engine enclosure is provided, it shuts down when fire detection in that enclosure activates [CODE NFPA 37-2024 §11.3.4, where that edition is adopted]. The 2021 section states the same shutdown.
- Combustion air is not that output [ASSUMED]. Verify with the engineer of record.
- Radiator air is not that output [ASSUMED]. Verify with the engineer of record.
- Fuel stop on a life-safety generator is a separate output. Do not close fuel on detection. That fuel-stop decision stays open.
- The §11.3.4.1 exception is not used by default [OWNER]. Verify with the engineer of record.
- Do not treat fuel stop and ventilation shutdown as one point.
- Campus integrated-test rows for this shutdown live in `fa-integrated-systems-test-matrix`.
- Canada: stop. Do not invent a Canadian generator-room rule. Foam and clean agent stay locked.
