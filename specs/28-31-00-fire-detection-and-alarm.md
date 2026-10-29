# Section 28 31 00 — Fire detection and alarm

Verify with the engineer of record. Wet, dry, and double-interlock only. No foam or clean-agent release.

### 1.1 Summary

Double-interlock stays here and in Section 21 13 19, not in Section 21 13 16.

Pin NFPA 72 first. An unamended 2024 I-Code cites NFPA 72-2022. NFPA 72-2025 is a delta unless adopted. Preaction low air is practice on 2019 (dry-pipe heading only) and code on 2022 and 2025.

### 1.2 Cause and effect

FA-DI-CE: solenoid = (Fire 1 OR the FACU manual station) AND same-zone low air AND not isolated [OWNER FM DS 5-32 §2.4.3.2.1.3]. Action replaces Fire 1. Another zone's low air does not satisfy the AND. Low air alone never releases. Dry-pipe low air and high air are supervisory [CODE NFPA 72-2025 §17.19.2.2.2(A)]. §23.8.5.4.3 is not this AND. Pump, fuel, and charger do not release.

§2.4.3.2.1.3.1 actuates on pre-alarm. §2.4.3.2.1.3.2 bars cross-zone. Off FM that bar is practice or owner-required. An NFPA 76 alert is supervisory, never the detection leg.

Mag holds and egress unlock are two outputs. The lock relay is alarm only: wet waterflow, Fire 1, or the FACU manual station. Not low air, duct smoke, tamper, or delayed to the solenoid. Lock-power loss unlocks [CODE IBC 2021 §1010.2.11; 2024 is one lower]. Mag-power loss releases holds [PRACTICE]. Hold-open on alarm, and waterflow as alarm, stay [PRACTICE]. Duct smoke, including a pump-house duct, is supervisory [CODE §21.7.4] and stops its own non-engine fan only. Diesel combustion and cooling air stay on, pending engineer-of-record confirmation.

Isolate is supervisory and blocks the solenoid. Station order: alarm and release, then supervisory, then trouble. Ch. 26 is not held.

### 2.1 Power, points, and wire

Building FACU 24 h + 5 min [CODE §10.6.7.2.1 to §10.6.7.2.2]. EVACS 24 h + 15 min at max load [CODE §10.6.7.2.3 to §10.6.7.2.4]. NFPA governs over FM DS 5-40 24 h + 5 min [OWNER]. Never put 90 h on EVACS or the building FACU. FM releasing: 90 h + 10 min [OWNER FM DS 5-40 §2.3.4], not a teaching Ah. Non-FM releasing is 24 h + 5 min [PARA]. EX-154 / PE-185 20 percent spare or next size is a training value [PRACTICE], not [CODE], not an approved live design. 100 Ah charger limit is unresolved. Split above the listed size.

1.0 dB is [CODE] only in NFPA 72-2025 §18.3.7.2.1(1). On 2019/2022 it is [PRACTICE]. A battery pass does not clear it.

Aging: 1.20 on NFPA 72-2019 (§10.6.7.2.1.1); 1.25 on 2022 or 2025 (§10.6.7.2.14).

Diesel running is separate [CODE NFPA 20-2025 §12.4.2.3]. Running is supervisory [OWNER]; code also permits alarm [CODE §23.8.5.9.1]. Off or manual is separate supervisory (§12.4.2.3(2), §23.8.5.9.2). Trouble is separate or common (§12.4.2.3(3); §12.4.1.4, §12.4.1.5). Oil, temperature, charger, and fuel may split [PRACTICE] or one pump-house trouble [OWNER FM DS 3-7 §2.2.1.12]. Electric off-normal is supervisory (§23.8.5.9.2, §10.4.7.2). Terminals: Section 21 30 00.

### 3.1 Layout

A raised floor is its own room. Elevator Phase I and shunt: lower temperature and RTI, within 24 in, no delay [CODE §21.4], alarm [PRACTICE], voltage loss supervisory [CODE §21.4.5], not self-resetting where IBC 2021 §3005.5 is adopted, not a release leg. No cooling minutes held. Gas trouble is not a gas alarm. Single-interlock is comparison-only.

### 3.2 Pathway, voice, hold

2022/2025 total evacuation, no relocation or partial: Levels 0 to 4 [CODE §24.3.14.4.1]. Level 1 if sprinklered is [PRACTICE]. 2 h: Level 2 or 3, or §24.3.14.4.6 [CODE §24.3.14.4.3]. 1 h: Level 4 or §24.3.14.4.6 [PARA §24.3.14.4.4]. No Level 4 on 2019. Firefighter phones in 2 h construction: Level 2 or 3 [CODE §24.3.14.8]. No Level 0 or 1 on relocation or partial (EX-155). Audibility is not intelligibility. Corridor visuals at least 15 cd [CODE §18.5.5.8.2] (EX-156). EX-157: heat and smoke [PRACTICE]; running and fuel supervisory; fail trouble [OWNER]; no release.

### 3.3 Country gate (US | Canada)

On a Canada job do not port the US pins above. NBC 2025 3.2.4 is the overlay. Fire alarm required [CODE 3.2.4.1.(1)]. Two-stage only if the AHJ requires it: unacknowledged alert becomes alarm at 5 min [CODE 3.2.4.4.(2)]. Annunciator near a street or fire-department entrance [CODE 3.2.4.8.(1)]. One storey per zone, within the NFPA 13 area [CODE 3.2.4.8.(2)(b)]. Supervise valves, excess pressure, dry-pipe air loss, automatic pump power loss, NFPA 20 pump signals, and freezing at a dry-pipe valve enclosure or water storage [CODE 3.2.4.9.(3) and (4)]. Heat-trace power loss is supervisory and never releases [CODE 3.2.4.9.(5)]. Supervisory signals transmit to the fire department [CODE 3.2.4.9.(6)]. Double-interlock low air is the owner AND, not the dry-pipe sentence. ULC listing is [PARA]. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 are NEEDS HOLD. Conductor type, FT rating, and circuit integrity stay in that hold. No clause text and no Canada battery hours. US 24 h + 5 min and 24 h + 15 min are a comparison floor only.
