---
name: fa-voice-evac-ads-audibility-screen
description: >-
  Use when you must set acoustically distinguishable spaces (ADS), intelligibility calls and an audibility screen for a data center (halls, aisles, office, mechanical, genset rooms), including loud rooms over 105 dBA and the AHJ reduce or eliminate path, per NFPA 72 Ch 18 and IBC 907.5.2.2.
---
# Voice evac ADS and audibility screen

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job, stop. CAN/ULC-S524 voice is not held. Return NEEDS HOLD. Do not map these NFPA 72 rows as Canada code. Do not state hours or invent a Canada intelligibility duration. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Pin the enforced editions first; run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis (NFPA 72-2025 unless noted; 2019/2022 renumbers via `fa-code-edition-delta-check`)
- [CODE] 3.3.6 ADS definition. 18.4.12.1 to .3 (2019/2022 18.4.11): designer sets ADSs and marks each as needing intelligibility or not.
- [CODE] 18.4.4.1: public mode is the greater of 15 dB over average ambient or 5 dB over the max lasting 60 s or more.
- [CODE] 18.4.1.2: 110 dBA max at minimum hearing distance. 18.4.1.1: over 105 dBA ambient, visual appliances required.
- [CODE] 18.4.4.2: with AHJ approval, audible may be reduced or eliminated when visual meets 18.5.
- [CODE] 18.4.1.5.6: document the design sound level for each coverage area for acceptance testing.
- [CODE] 18.4.4.5.3*: relays, circuits, or interfaces that stop or reduce ambient noise meet Chapters 10, 12, 21, and 23.
- [CODE] 18.4.12.2: each acoustically distinguishable space is marked as requiring intelligibility or not. 18.4.12.5: quantitative measurement is not required. 24.4.2.2.2* (2022 and 2025): the design designates those spaces in occupiable areas as Chapter 18 requires. The field pass value stays [OWNER]. Do not invent it. A modeled speech score is never a field pass.
- [CODE] 18.3.7.2.1: speaker NAC electrical loss 1.0 dB max, include MIA (18.3.7.2.2). Run `fa-speaker-circuit-loss-check`.
- [CODE] 10.19.1: amplifier failure gives trouble.
- [CODE IBC 2021/2024 907.5.2.2]: where EVACS is code required, paging zones per that section. Where voice is owner choice, tag [OWNER].
- Loud room over 110 dBA ambient: no held text resolves it. Verify with the engineer of record. Conservative: visual per 18.5, AHJ reduce or eliminate path, owner hearing protection signs.

## Inputs (ASSUME and flag any missing)
Spaces with average and 60 s max ambient (measure on real jobs), speaker data sheet output at 1 W and 10 ft, taps, ceiling heights, occupancy, evac strategy, owner voice standard.

## Steps
1. ADS list. Mark intelligibility per space with the reason. Halls and mech rooms are often not required; office and egress per owner.
2. Required level per ADS from 18.4.4.1.
3. Script: inverse-square drop, no room gain [PRACTICE]; minimum hearing distance ASSUMED 3 ft [PRACTICE]. Solve the tap and max listener distance that meets need with the near-speaker total at or under 110 dBA. Count one speaker; flag overlap recheck.
4. Verdict per ADS: PASS, MARGINAL, or does not close. Does not close goes to the 18.4.4.2 AHJ path with visual per 18.5.
5. Over 105 dBA ambient: visual required. Over 110 dBA: Verify with the engineer of record item.
6. Hand line loss and wire to `fa-speaker-circuit-loss-check` and `fa-nec-table-8-wire-sizing`; strobes to `fa-nac-voltage-drop-check`; loads to `fa-secondary-power-battery-calc` (voice 24 h + 15 min).

## Output
ADS table with intelligibility call and reason, level table, tap and spacing solve, AHJ path items, open items, delta vs the enforced edition.

## Campus ADS and corridor speech-transmission screen

A loud room, 85 dBA ambient or more, is its own acoustically distinguishable space: tone plus visual, not voice [HB]. Do not skip that space. An audibility pass is not an intelligibility pass. Where the speech-transmission screen fails, redesign with more speakers, lower taps, and a shorter throw, then retest. Do not log that failure as a pass. Speech-transmission targets are handbook or paraphrase, not [CODE].

Handbook screen [HB NFPA 72-2025 D.2.4.1]: at least 90 percent of points at or above 0.45, and an average at or above 0.50. An average of 0.45 is not a pass.

Corridor visual appliances are rated not less than 15 cd [CODE NFPA 72-2025 §18.5.5.8.2], within 15 ft of each end, and not more than 100 ft apart [CODE §18.5.5.8.4]. More than two in one view flash in sync [CODE §18.5.5.7.2(3)]. A further corridor-only sync sentence is not pinned.

US teaching shape only: six ceiling speakers, 25 ft on center, 0.25 W tap. A modeled average near 0.55 is not acceptance. Do not copy the teaching taps onto a live corridor. Modeled STI is never a field pass. Tag a modeled result [ASSUMED].

Annex D is handbook guidance, not [CODE]. The intelligibility requirement stays in Chapter 18 and Chapter 24. Quantitative Annex D measurement is used only when the AHJ or the project basis elects it. Quantitative Annex D is permitted, not mandated. When that field test is elected, follow this protocol [HB/PRACTICE]:

1. Define each acoustically distinguishable space.
2. Flag a space at 85 dBA or more for other means.
3. Use the STI or STIPA method.
4. Use the microphone path when the system has a microphone. That checks the path end to end. Otherwise use direct injection.
5. Calibrate the talkbox.
6. Measure the grid points and record each space.
7. The pass value is set by the owner [OWNER]. Do not invent a pass value. On a fail, correct and retest [PRACTICE].

Do not invent a test duration. No held text states one. On a Canada job, stop this screen. Do not map these Annex D rows as Canada code, and do not invent a Canada intelligibility duration. CAN/ULC-S524 voice stays NEEDS HOLD. Verify with the engineer of record.

## Tap against ambient before the voice zone

Where the system has a microphone for live voice, post instructions for using it [CODE NFPA 72-2022 and 2025 §24.3.2]. The two editions match. The wording of the card is [PRACTICE].

Public mode is 15 dB above average ambient [CODE NFPA 72 §18.4.4]. Do not use a 10 dB rule for that public-mode target.

Teaching point [PRACTICE], not a job layout. Average ambient 78 dBA. The public-mode target is 78 + 15 = 93 dBA. A speaker at 94 dB SPL at 1 m on a 2 W tap is [ASSUMED] datasheet data. A 1 W tap meets 93 dBA only out to about 0.79 m. That distance is not a buildable spacing. A 1 W tap does not give intelligible public-mode voice in that white space. Check the tap against the ambient before electing voice. Galleries at a high ambient are tone plus visual. Voice stays in aisles and support spaces that can meet the target. Do not copy the 0.79 m figure onto a live zone.

The speech-transmission-index field pass stays [OWNER]. Do not invent the number. Modeled STI is never a field pass. GAP-B33R8-1 stays open. 0.2 %/ft is not [CODE]. Foam, clean agent, and single-interlock stay locked. On a Canada job, stop. CAN/ULC-S524 voice stays NEEDS HOLD.
