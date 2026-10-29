# Section 28 31 00 — Fire detection and alarm (draft)

Draft. Verify with the engineer of record before issue. Wet, dry, and double-interlock only. No foam or clean-agent release.

## Part 1 — General

### 1.1 Summary

Provide detection, notification, supervision, and releasing for the elected systems. Double-interlock releasing belongs here and in Section 21 13 19. Do not write that matrix into Section 21 13 16.

Pin the enforced NFPA 72 edition first. An unamended 2024 I-Code floor references NFPA 72-2022. NFPA 72-2025 is a delta unless adopted. Preaction low air: 2019 is design practice (dry-pipe heading only). 2022 and 2025 are code (dry pipe and preaction).

### 1.2 Cause and effect

FA-DI-CE: solenoid = (Fire 1 OR the FACU manual station) AND same-zone low air AND not isolated [OWNER FM DS 5-32 §2.4.3.2.1.3]. Action takes the Fire 1 place when the owner map says so. Another zone's low air does not satisfy the AND. Low air alone never releases and never unlocks a door. Dry-pipe low air is supervisory only [CODE NFPA 72-2025 §17.19.2.2.2(A)]. High air is supervisory on that cite. Do not cite §23.8.5.4.3 for the AND. It is alarm verification. Low air is not a detector.

§2.4.3.2.1.3.1 actuates on pre-alarm. §2.4.3.2.1.3.2 does not cross-zone. Two-leg cross-zone is never the FM default. Off an FM job it is design practice, or owner-required. Say which. An NFPA 76 alert is supervisory and is never the detection leg.

Doors unlock on wet waterflow, Fire 1, or the FACU manual station. Not on low air. Not delayed to the solenoid. Loss of power unlocks (IBC 2021 §1010.2.11; the 2024 number is one lower). Sensor release and panic hardware: Section 21 05 00, IFC 2024 §1010.2.11 and §1010.2.8. Duct smoke is supervisory [CODE §21.7.4]: fan shutdown only. Dry waterflow door action is not code. Assume it unlocks, and verify with the engineer of record.

Isolate is supervisory and blocks the solenoid. Supervising station: alarm and release, then supervisory, then trouble. Chapter 26 is not held. Each waterflow and each release has its own point. AC failure is trouble.

## Part 2 — Products

### 2.1 Power, points, and wire

Three batteries. Building FACU: 24 h + 5 min [CODE §10.6.7.2.1 to §10.6.7.2.2]. EVACS: 24 h + 15 min at maximum connected load [CODE §10.6.7.2.3 to §10.6.7.2.4]. NFPA governs over FM DS 5-40 24 h + 5 min [OWNER]. Never put 90 h on EVACS or the building FACU. FM releasing: 90 h + 10 min [OWNER FM DS 5-40 §2.3.4]. Non-FM releasing: 24 h + 5 min is a paraphrase, not a releasing-only duration. A 100 Ah charger limit is unresolved. Split the load if the battery exceeds the listed size. Do not freeze a model.

Speakers: 1.0 dB maximum line loss [CODE §18.3.7.2.1(1)]. A passing battery calc does not clear the speaker circuit.

Aging: 1.20 on NFPA 72-2019 (§10.6.7.2.1.1); 1.25 on 2022 or 2025 (§10.6.7.2.14).

Diesel [CODE NFPA 20-2025 §12.4.2.3]: engine running, separate, alarm or supervisory by election [CODE §23.8.5.9.1]; off or manual, separate supervisory (§12.4.2.3(2), §23.8.5.9.2); trouble, separate or common (§12.4.2.3(3); see §12.4.1.4 and §12.4.1.5). Low oil, high temperature, charger failure, and low fuel may be split as design practice. FM DS 3-7 §2.2.1.12 may group extras as one pump-house trouble. Keep the splits until the owner elects the group. Other electric signals are supervisory (§23.8.5.9.2): phase loss, phase reversal, alternate source, alternate isolating switch open (§10.4.7.2). Terminals are in Section 21 30 00. Do not invent a module count.

Size wire from the voltage-drop calculation. Cite the NEC table. Do not paste it.

## Part 3 — Execution

### 3.1 Layout

Spot spacing and very-early warning follow adopted NFPA 72 and the insurer sheet. A raised floor is its own room. No arc-flash vent. Coordinate elevator recall. Egress lighting stays on. Remove critical load before water, then interlock cooling. No cooling minutes are held. A gas trouble is not a gas alarm. Single-interlock is comparison-only.
