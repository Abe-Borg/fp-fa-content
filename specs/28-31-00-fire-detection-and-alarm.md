# Section 28 31 00 — Fire detection and alarm (draft)

Draft. Verify with the engineer of record before issue. Wet, dry, and double-interlock only. No foam or clean-agent release.

## Part 1 — General

### 1.1 Summary

Provide detection, notification, supervision, and releasing for the elected systems. Double-interlock releasing belongs here and in Section 21 13 19. Do not write that matrix into Section 21 13 16.

Pin the enforced NFPA 72 edition first. An unamended 2024 I-Code floor references NFPA 72-2022. NFPA 72-2025 is a delta unless adopted. Preaction low air: 2019 is design practice (dry-pipe heading only). 2022 and 2025 are code (dry pipe and preaction).

### 1.2 Cause and effect

FA-DI-CE: solenoid = (Fire 1 OR the FACU manual station) AND same-zone low air AND not isolated [OWNER FM DS 5-32 §2.4.3.2.1.3]. Action takes Fire 1's place when the owner map says so. Another zone's low air does not satisfy the AND. Low air alone never releases and never moves a door. Dry-pipe low air is supervisory only [CODE NFPA 72-2025 §17.19.2.2.2(A)]. High air is supervisory on that cite. Do not cite §23.8.5.4.3 for the AND. It is alarm verification. Low air is not a detector.

§2.4.3.2.1.3.1 actuates on pre-alarm. §2.4.3.2.1.3.2 does not cross-zone. Two-leg cross-zone is never the FM default. Off an FM job it is design practice, or owner-required. An NFPA 76 alert is supervisory and is never the detection leg.

Mag hold release and egress unlock are two outputs with two bases. Both act on wet waterflow, Fire 1, or the FACU manual station. Not on low air, duct smoke, or tamper. Not delayed to the solenoid. Lock-power loss unlocks [CODE IBC 2021 §1010.2.11; 2024 is one number lower]. Mag-power loss releases holds [PRACTICE]. Hold-open on alarm and waterflow as alarm stay [PRACTICE]. Duct smoke is supervisory [CODE §21.7.4]: fan only. Dry waterflow door action is not code. Assume it acts. Verify with the engineer of record.

Isolate is supervisory and blocks the solenoid. Supervising station: alarm and release, then supervisory, then trouble. Ch. 26 not held. Each waterflow and each release has its own point.

## Part 2 — Products

### 2.1 Power, points, and wire

Three batteries. Building FACU: 24 h + 5 min [CODE §10.6.7.2.1 to §10.6.7.2.2]. EVACS: 24 h + 15 min at maximum connected load [CODE §10.6.7.2.3 to §10.6.7.2.4]. NFPA governs over FM DS 5-40 24 h + 5 min [OWNER]. Never put 90 h on EVACS or the building FACU. FM releasing: 90 h + 10 min [OWNER FM DS 5-40 §2.3.4]. Non-FM releasing: 24 h + 5 min [PARA]. Building FACU: 20 percent spare, or the next size [PRACTICE]. A 100 Ah charger limit is unresolved. Split above the listed size.

Speakers: 1.0 dB is [CODE] only in NFPA 72-2025 §18.3.7.2.1(1). 2019/2022: [PRACTICE]. A battery pass does not clear it.

Aging: 1.20 on NFPA 72-2019 (§10.6.7.2.1.1); 1.25 on 2022 or 2025 (§10.6.7.2.14).

Diesel [CODE NFPA 20-2025 §12.4.2.3]: engine running, separate, alarm or supervisory by election [CODE §23.8.5.9.1]; off or manual, separate supervisory (§12.4.2.3(2), §23.8.5.9.2); trouble, separate or common (§12.4.2.3(3); see §12.4.1.4 and §12.4.1.5). Oil, temperature, charger, and fuel may split [PRACTICE], or group as one pump-house trouble under FM DS 3-7 §2.2.1.12 until the owner elects. Electric off-normal signals stay supervisory (§23.8.5.9.2, §10.4.7.2). Terminals: Section 21 30 00.

## Part 3 — Execution

### 3.1 Layout

Spot and very-early warning follow NFPA 72 and insurer. A raised floor is its own room. No arc-flash vent. Elevator Phase I and shunt only where an elevator is present. Placement, lower temperature and RTI, 24 in, no delay: [CODE §21.4]. Class alarm [PRACTICE]. Voltage loss supervisory [CODE §21.4.5]. Not self-resetting where IBC 2021 §3005.5 is adopted. Same-space recall smoke. Not a release leg. Egress lighting stays on. Shed critical load before water, then interlock cooling. No cooling minutes held. A gas trouble is not a gas alarm. Single-interlock is comparison-only.
