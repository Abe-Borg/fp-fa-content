# Section 28 31 00 — Fire detection and alarm

Verify with the engineer of record before issue. Wet, dry, and double-interlock only. No foam or clean-agent release.

### 1.1 Summary

Detection, notification, supervision, and releasing. Double-interlock stays here and in Section 21 13 19, not in Section 21 13 16.

Pin NFPA 72 first. An unamended 2024 I-Code floor cites NFPA 72-2022, so NFPA 72-2025 is a delta unless adopted. Preaction low air: 2019 is design practice (dry-pipe heading only); 2022 and 2025 are code (dry pipe and preaction).

### 1.2 Cause and effect

FA-DI-CE: solenoid = (Fire 1 OR the FACU manual station) AND same-zone low air AND not isolated [OWNER FM DS 5-32 §2.4.3.2.1.3]. Action replaces Fire 1. Another zone's low air does not satisfy the AND. Low air alone never releases or moves a door. Dry-pipe low air and high air are supervisory [CODE NFPA 72-2025 §17.19.2.2.2(A)]. §23.8.5.4.3 is alarm verification, not this AND. Low air is not a detector. Pump, fuel, and charger do not release.

§2.4.3.2.1.3.1 actuates on pre-alarm. §2.4.3.2.1.3.2 bars cross-zone, never the FM default. Off FM it is design practice or owner-required. An NFPA 76 alert is supervisory, never the detection leg.

Mag hold release and egress unlock are two outputs, two bases. Lock relay is alarm only: wet waterflow, Fire 1, or the FACU manual station. Not low air, duct smoke, tamper, or delayed to the solenoid. Lock-power loss unlocks [CODE IBC 2021 §1010.2.11; 2024 is one lower]. Mag-power loss releases holds [PRACTICE]. Hold-open on alarm and waterflow as alarm stay [PRACTICE]. Duct smoke, including a pump-house duct, is supervisory [CODE §21.7.4] and stops its own non-engine fan only. Diesel combustion and cooling air stay on, not resolved, pending engineer-of-record confirmation. Dry waterflow door action is not code. Assume it acts. Verify with the engineer of record.

Isolate is supervisory and blocks the solenoid. Supervising station: alarm and release, then supervisory, trouble. Ch. 26 not held. Each waterflow and release is its own point.

### 2.1 Power, points, and wire

Three batteries. Building FACU 24 h + 5 min [CODE §10.6.7.2.1 to §10.6.7.2.2]. EVACS and boosters 24 h + 15 min at max load [CODE §10.6.7.2.3 to §10.6.7.2.4]. NFPA governs over FM DS 5-40 24 h + 5 min [OWNER]. Never put 90 h on EVACS or the building FACU. FM releasing: 90 h + 10 min on maker data, not a teaching Ah [OWNER FM DS 5-40 §2.3.4]. Non-FM releasing is 24 h + 5 min [PARA]. PE-185 / EX-154 20 percent spare or next size: training value [PRACTICE], not [CODE], not an approved live design. Verify with the engineer of record. 100 Ah charger limit unresolved. Split above the listed size.

Speakers: 1.0 dB is [CODE] only in NFPA 72-2025 §18.3.7.2.1(1). 2019/2022: [PRACTICE]. A battery pass does not clear it.

Aging: 1.20 on NFPA 72-2019 (§10.6.7.2.1.1); 1.25 on 2022 or 2025 (§10.6.7.2.14).

Diesel [CODE NFPA 20-2025 §12.4.2.3]: running is separate. Diesel or electric pump running is supervisory [OWNER]; code permits alarm or supervisory [CODE §23.8.5.9.1]. Off or manual: separate supervisory (§12.4.2.3(2), §23.8.5.9.2). Trouble: separate or common (§12.4.2.3(3); §12.4.1.4, §12.4.1.5). Oil, temperature, charger, and fuel may split [PRACTICE] or one pump-house trouble [OWNER FM DS 3-7 §2.2.1.12] until the owner elects. Electric off-normal: supervisory (§23.8.5.9.2, §10.4.7.2). Terminals: Section 21 30 00.

### 3.1 Layout

Spot and very-early warning follow NFPA 72 and the insurer. A raised floor is its own room. No arc-flash vent. With an elevator, Phase I and shunt: lower temperature and RTI, within 24 in, no delay [CODE §21.4], class alarm [PRACTICE], voltage loss supervisory [CODE §21.4.5], not self-resetting where IBC 2021 §3005.5 is adopted, same-space recall smoke, not a release leg. Egress lights stay on. Shed critical load before water, then interlock cooling. No cooling minutes held. Gas trouble is not a gas alarm. Single-interlock is comparison-only.

### 3.2 Pathway, voice, hold

On 2022 and 2025, no relocation or partial evacuation may use Levels 0 to 4 [CODE §24.3.14.4.1]. Level 1 on sprinklered total evacuation is [PRACTICE]. At 2 h, use Level 2 or 3, or §24.3.14.4.6 [CODE §24.3.14.4.3]. At 1 h, Level 4 or §24.3.14.4.6 [PARA §24.3.14.4.4]. Do not cite Level 4 on 2019. Firefighter phones in 2 h construction use Level 2 or 3 [CODE §24.3.14.8]. No Level 0 on relocation or partial evacuation. No Level 1 on those circuits. EX-155 is training. Verify with the engineer of record. Audibility is not intelligibility. A loud room is tone and visual, not voice. A failed speech screen means more speakers, lower taps, then a retest. Corridor visuals are at least 15 cd [CODE §18.5.5.8.2]. Speech targets are not [CODE]. EX-156 is training. Generator and emergency power (EX-157) stay on hold: heat and smoke [PRACTICE]; running and fuel supervisory; fail trouble [OWNER]; no release; not a skill.
