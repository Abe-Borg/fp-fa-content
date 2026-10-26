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
6. Generator credit; any owner or insurer extended standby demand and its written source.

## Steps
1. Build scenarios in a script: (A) ASD heads on releasing panel aux; (B) ASD heads on one separate listed supply; (C) multi-supply: ASD heads split across N listed supplies when one supply exceeds its charger. For C, raise N until every supply's pick fits its charger; report per-supply loads (print every supply, not one as typical), head assignment, and that each supply's trouble and AC-fail report to the releasing FACU. Each supply gets its own calc via `fa-secondary-power-battery-calc`.
2. Alarm time: 5 min [PARA] and any insurer/owner case (for example 10 min, labeled [OWNER]) side by side.
3. Required Ah = (Is x 24 + Ia x alarm h) x F per supply (F edition-keyed). Report pick and margin in Ah and percent.
3a. Thin-margin rule [PRACTICE]: if the pick's margin over required Ah is small while any load current is synthetic or ASSUMED, or the margin falls under the shop screen of 20 % (ASSUMED threshold, not code; one value shared with Calcs ; Verify with the engineer of record; conservative assumption: any margin under 20 % is THIN and steps up one size), report the pick as THIN. Step up one size or confirm listed currents before issue. No code margin applies beyond F.
4. Check each pick against the charger limit. ASD heads usually dominate standby, so scenario A often exceeds the panel charger [PRACTICE].
5. Pick the split. Default to B when A exceeds the charger, and to C when B's single supply exceeds its charger [PRACTICE]. Keep head-to-supply assignment aligned with valve areas, so one supply loss takes out leg 1 for as few valve areas as possible [PRACTICE]. For B and C, confirm: each ASD supply is listed, its trouble and AC-fail report to the releasing FACU, and an ASD power loss shows as trouble in the C&E. A dead ASD head removes leg 1 for its valve area.
6. Keep the solenoid and releasing circuits on the releasing FACU (§23.11.8). Do not move releasing devices to a separate supply unless listed for it (§23.11.2).
7. Extended-standby question: ask owner, FM and AHJ in writing whether any duration beyond 24 h applies to releasing service, and ask for the clause. Record "needs source: panel/solenoid listing" and size to 24 h on NFPA-only jobs. On FM jobs flag Verify with the engineer of record and show the FM DS 5-40 s2.3.4 case (90 h + 10 min, per FM DS 5-40 §2.3.4; confirm the edition is current) beside the 24 h case; the more stringent governs until the engineer of record confirms.
8. Head count sanity: if the head count in the calc differs from the layout, flag it and show both ( lesson).

## Output
Scenario table (A, B, C) per supply, with THIN flags: Is, Ia, alarm-time label, required Ah, pick, margin, charger check; recommended split and why; trouble/supervision rows for C&E; extended-standby status; ASSUMED list; FP items (solenoid listing, valve area per head).
