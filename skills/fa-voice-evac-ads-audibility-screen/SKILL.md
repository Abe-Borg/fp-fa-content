---
name: fa-voice-evac-ads-audibility-screen
description: >-
  Use when you must set acoustically distinguishable spaces (ADS), intelligibility calls and an audibility screen for a data center (halls, aisles, office, mechanical, genset rooms), including loud rooms over 105 dBA and the AHJ reduce or eliminate path, per NFPA 72 Ch 18 and IBC 907.5.2.2.
---
# Voice evac ADS and audibility screen

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.
- On FM DI jobs carry the standing flag: [OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision: keep DI. Flag to owner and FM on this job.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed numbers carry **VERIFY**. Judgment calls carry **Verify with the engineer of record** with the conservative assumption stated.
- Pin the enforced editions first; run `fa-code-edition-delta-check`. Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes. Verify with the engineer of record. Do not claim a stamp. No CAD. Copy METHOD, not synthetic numbers.

## Basis (NFPA 72-2025 unless noted; 2019/2022 renumbers via `fa-code-edition-delta-check`)
- [CODE] 3.3.6 ADS definition. 18.4.12.1 to .3 (2019/2022 18.4.11): designer sets ADSs and marks each as needing intelligibility or not.
- [CODE] 18.4.4.1: public mode is the greater of 15 dB over average ambient or 5 dB over the max lasting 60 s or more.
- [CODE] 18.4.1.2: 110 dBA max at minimum hearing distance. 18.4.1.1: over 105 dBA ambient, visual appliances required.
- [CODE] 18.4.4.2: with AHJ approval, audible may be reduced or eliminated when visual meets 18.5.
- [CODE] 18.3.7.2.1: speaker NAC electrical loss 1.0 dB max, include MIA (18.3.7.2.2). Run `fa-speaker-circuit-loss-check`.
- [CODE] 10.19.1: amplifier failure gives trouble.
- [CODE IBC 2021/2024 907.5.2.2]: where EVACS is code required, paging zones per that section. Where voice is owner choice, tag [OWNER].
- Loud room over 110 dBA ambient: no held text resolves it. Verify with the engineer of record ( row 15). Conservative: visual per 18.5, AHJ reduce or eliminate path, owner hearing protection signs.

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

US teaching shape only: six ceiling speakers, 25 ft on center, 0.25 W tap. A modeled average near 0.55 is not acceptance. Field-check intelligibility. Modeled speech stays [ASSUMED] until a field method is chosen. Annex D measurement is required only when the AHJ or the project basis elects it. Quantitative Annex D is permitted, not mandated. Do not copy the teaching taps onto a live corridor. On a Canada job do not treat the US handbook screen as code, and do not invent a Canada intelligibility duration. Verify with the engineer of record.
