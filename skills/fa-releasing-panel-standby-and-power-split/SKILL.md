---
name: fa-releasing-panel-standby-and-power-split
description: >-
 Use when you must size a DI preaction releasing panel's secondary power and
 decide whether ASD heads ride the releasing panel aux, one separate listed
 supply, or several supplies, with a thin-margin check and the extended-standby
 source question; packet optional, missing loads ASSUMED.
---
# FA releasing panel standby and power split

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.

- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "section not pinned; verify before use.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). Verify judgment calls with the engineer of record. Copy METHOD, not synthetic numbers.

## Relationship to other skills
Battery arithmetic and the general §10.6.7 basis live in `fa-secondary-power-battery-calc`; run it for each supply. This skill adds the releasing-specific decisions: what loads ride the releasing FACU, the alarm-time labels, and the extended-standby question. C&E logic: `fa-double-interlock-releasing-cause-and-effect`.

## Basis
- [CODE] NFPA 72-2025 and 2022 §10.6.7.2.1 to .2.2: 24 h quiescent, then 5 min alarm for evacuation/aid notification. §10.6.7.2.13: all loads not automatically disconnected count. Battery factor F is edition-keyed, per `fa-secondary-power-battery-calc`: 2019 20% safety margin §10.6.7.2.1.1 (F = 1.20); 2022/2025 aging factor 1.25 §10.6.7.2.14. It is a code value, never trimmed. Durations are the same in 2019; 2019 numbers: 24 h + 5 min §10.6.7.2.1, all loads §10.6.7.2.2.
- [CODE] §10.6.7.3.1(2): generator plus dedicated batteries with 4 hours of capacity (same text 2019 / 2022). How alarm time stacks on that is [PARA]; AHJ to confirm. The generator must meet 10.6.11.3.1.1 (2022/2025); NFPA 110 has no Class 24, so specify Class X at 24 h fuel, Type 10, Level 1 (Design practice; Verify with the engineer of record]. See `fa-secondary-power-battery-calc` for the size cap and split-load rule.
- No releasing-specific duration in NFPA 72-2025 or 2022. 24 h + 5 min for a releasing panel is a **[PARA]** reading of §10.6.7.2.2.
- EVACS amplifiers serving the same hall are a separate supply. Size them at 24 h + 15 min at maximum connected load [CODE NFPA 72-2025 §10.6.7.2.3 to .2.4] in `fa-secondary-power-battery-calc`. Do not fold amplifier load into the releasing FACU calc unless the amplifier really rides that supply. FM 90 h + 10 min (DS 5-40 2007 §2.3.4) applies to the releasing panel only. FM duration for EVACS amplifiers: verify before use.
- Aux on the FACU versus split [PRACTICE]: where ASD rides separate listed supplies (split path), that is the elected path and the releasing FACU load is small. An aux-on-FACU pick is screening only. If the design keeps heads on aux, re-pick to the next common size with at least 20% margin, or mark THIN with a written waiver from the engineer of record. Verify with the engineer of record.
- [CODE] §23.11.1 to .11.2: releasing FACU and releasing devices listed together. §23.11.8: one releasing FACU controls the system (§23.11.9 listed multi-unit exception). §23.11.10.1 to .10.2 (2019 / 2022 single §23.11.10): monitored by, not dependent on, the building FA.
- [CODE] §10.6.7.3.2: secondary circuits feeding the CU and not integral to it are protected against physical damage.
- [CODE] §7.2.1(7) (2022 ; 2019 ): battery capacity and safety margin calcs in documentation.
- [CODE] Table 14.4.3.2 item 8 secondary power test, Initial X and Annually, same in 2019, 2022, 2025: primary off, trouble verified, rated capacity vs demand including the safety margin. Test each supply against its own calc (releasing FACU and every ASD supply) [PARA for separate supplies]. The 5 min test run is not the sizing alarm time; the 10 min [OWNER] case still sizes.
- Extended standby (anything beyond 24 h): FM DS 5-40 (September 2007) §2.3.4 [OWNER/insurer]: automatic preaction release panels need 90 hours of secondary power, then 10 minutes of release and alarm. Confirm the edition is current [OWNER/insurer]. removed an unsourced 90 h; it is now sourced on FM jobs only. The releasing panel and solenoid listing stays "needs source" until pinned. Verify with the engineer of record: Sep 2007 is the held edition; confirm it is current with the insurer. Conservative assumption: FM jobs carry 90 h + 10 min. NFPA-only jobs: 24 h + alarm per 72. On FM jobs, until the engineer of record confirms, the more stringent standby governs.

## Inputs (ASSUME and flag any missing)
1. Enforced edition; insurer; AHJ.
2. Releasing FACU load list (board, SLC, modules, solenoids per valve, NACs on panel) from listed data sheets.
3. ASD head count per releasing panel (from `fa-asd-vewfd-data-hall-sampling-layout`), standby and alarm current per head.
4. Panel charger max Ah and battery cabinet options.
5. Separate listed power supply option for ASD heads: its own load list and charger limit.
6. Generator credit; any owner or insurer extended standby demand and its written source. On an FM job this includes the 90 h + 10 min case. The governing standby is an input to the split, not a note added after it.

## Steps
1. Pin standby hours before any charger check or supply split. One required case per applicable basis:
   - NFPA case: standby_h = 24, alarm = 5 min. 24 h + 5 min on a releasing panel is a [PARA] reading of §10.6.7.2.2.
   - FM case, when FM insures: standby_h = 90, alarm = 10 min [OWNER/insurer FM DS 5-40 §2.3.4]. Confirm the edition is current. Verify with the engineer of record. Also compute the 24 h / 5 min case beside it. The governing case is 90 h + 10 min until the engineer of record confirms a shorter written allowance.
   - Any other written owner or insurer duration: its own standby_h and alarm time, labeled [OWNER] or [OWNER]/insurer.
   Ask the owner, FM, and the AHJ in writing whether any duration beyond 24 h applies, and ask for the clause. Record "needs source: panel/solenoid listing". On an NFPA-only job the governing case is 24 h plus that case's alarm time. Do not select a split on 24 h and apply 90 h afterward.
2. For each supply and each case, Required Ah = (Is x standby_h + Ia x alarm_h) x F. F is edition-keyed. Print standby_h, alarm_h, edition, and F. Report the pick and the margin in Ah and percent for every case. Charger checks, the thin-margin screen, and scenario selection use the governing case only.
3. Thin-margin rule [PRACTICE], on the governing required Ah: if the pick's margin over required Ah is small while any load current is synthetic or ASSUMED, or the margin falls under the shop screen of 20 % (ASSUMED threshold, not code; Verify with the engineer of record; conservative assumption: any margin under 20 % is THIN and steps up one size), report the pick as THIN. Step up one size or confirm listed currents before issue. No code margin applies beyond F.
4. Check each governing pick against the charger limit and the largest listed battery. A supply that fits at 24 h and exceeds the charger or the listed battery at the governing standby fails. ASD heads usually dominate standby, so scenario A often exceeds the panel charger [PRACTICE].
5. Build scenarios from the governing capacity, in a script. (A) ASD heads on the releasing panel aux. (B) ASD heads on one separate listed supply. (C) ASD heads split across N listed supplies when one supply exceeds its charger at the governing standby. For C, raise N until every supply's governing pick fits its charger. Report per-supply loads (print every supply, not one as typical), head assignment, and that each supply's trouble and AC-fail report to the releasing FACU. Each supply gets its own calc via `fa-secondary-power-battery-calc`, using that supply's governing standby_h. Pick the split from the governing case: default to B when A exceeds the charger, and to C when B's single supply exceeds its charger [PRACTICE]. Keep head-to-supply assignment aligned with valve areas, so one supply loss takes out leg 1 for as few valve areas as possible [PRACTICE]. For B and C, confirm each ASD supply is listed, its trouble and AC-fail report to the releasing FACU, and an ASD power loss shows as trouble in the C&E. A dead ASD head removes leg 1 for its valve area. Print the non-governing case beside the governing result. It does not choose the split.
6. Keep the solenoid and releasing circuits on the releasing FACU (§23.11.8). Do not move releasing devices to a separate supply unless listed for it (§23.11.2).
7. Head count sanity: if the head count in the calc differs from the layout, flag it and show both.

## Output
Scenario table (A, B, C) per supply and per case, with the governing case marked: standby_h, alarm time, Is, Ia, required Ah, pick, margin, THIN flag, charger check. Recommended split and why, taken from the governing case. Trouble and supervision rows for C&E. Extended-standby status. ASSUMED list. Items for the fire-protection method (solenoid listing, valve area per head).
