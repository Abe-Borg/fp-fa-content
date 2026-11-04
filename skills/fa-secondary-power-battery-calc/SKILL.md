---
name: fa-secondary-power-battery-calc
description: >-
 Use when you must size standby batteries for a fire alarm or releasing service
 control unit, booster, or ASD power supply per NFPA 72 §10.6.7: 24 h plus
 alarm time, edition-keyed factor (2019 20% margin; 2022/2025 1.25 aging),
 voice 24 h plus 15 min, generator plus 4 h option. Packet optional; missing
 loads ASSUMED. Also covers Li-ion BESS rooms: FACP serving BESS detection and
 the gas detection panel at 24 h standby plus 2 h alarm (NFPA 855-2023 4.8.3
 for smoke and fire detection; 9.6.5.6.7(4) for Li-ion gas detection). Not NAC drop, UPS, or sizing the ESS itself.
---
# FA secondary power battery calc

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.
- Country gate (US | Canada). On a US job use the NFPA, IBC, and IFC pins in this skill. On a Canada job keep this skill. NBC 2025 Division B 3.2.4 is the held alarm overlay where this skill cites it. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Do not port a US pin into a Canada row or a Canada pin into a US row. Foam and clean agent stay locked.

- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "section not pinned; verify before use.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). Verify judgment calls with the engineer of record. Copy METHOD, not synthetic numbers.

- [CODE] §10.6.7.2.1: quiescent load minimum 24 h.
- [CODE] §10.6.7.2.2: then all evacuation/aid notification appliances 5 min, unless §10.6.7.2.4 applies.
- [CODE] §10.6.7.2.3 to .2.4: voice/alarm: 24 h quiescent, then 15 min at maximum connected load.
  - EVACS amplifier example (synthetic, loads ASSUMED, NFPA 72-2025, F = 1.25 at §10.6.7.2.14): Is = 1.15 A, Ia = 13.65 A. Base = 1.15 x 24 + 13.65 x 15/60 = 31.01 Ah. Times 1.25 = 38.77 Ah. Pick 55 Ah. Margin 41.9% [CODE durations and F; loads ASSUMED].
  - Margin screen: the 20% spare over required Ah is a training value [PRACTICE]. It is not [CODE] and it is not an approved live design. Do not cite it as a code minimum. Verify with the engineer of record before a live job uses it. Under 20% is THIN: step up to the next listed stock size, or mark THIN and verify with the engineer of record. Example: a voice panel pick that fails the 20% screen steps up (55 Ah to 65 Ah). The edition factor F is separate and stays [CODE].
  - Charger and stock size: verify before use that the panel's own listed charger range covers the elected Ah, and that the Ah is a listed compatible size (next listed size up is acceptable) [PRACTICE]. Any maker range used in an example is an example only. Keep the unit maker-neutral.
  - FM on EVACS amplifiers (DS 5-40 §2.3.4, September 2007): other FA signaling is 24 h + 5 min [OWNER]. Held text has no separate EVACS or voice line and no FM 90 h voice figure. Elect NFPA 72 §10.6.7.2.3 to .2.4 at 24 h + 15 min [CODE] (most stringent). The 90 h + 10 min figure is for preaction releasing panels only (the sheet also names deluge panels; deluge is out of scope). Do not carry 90 h onto EVACS amplifiers. DS 5-23 is not an FA duration source.
- Duration pins (identical in `fa-secondary-power-battery-calc` and `fa-releasing-panel-standby-and-power-split`): building FACU 24 h + 5 min [CODE NFPA 72-2025 §10.6.7.2.1 to .2.2]; EVACS 24 h + 15 min at maximum connected load [CODE §10.6.7.2.3 to .2.4], and NFPA governs over FM DS 5-40 24 h + 5 min [OWNER]; releasing (DI preaction) panel on FM jobs 90 h + 10 min [OWNER FM DS 5-40 s2.3.4]. Never apply 90 h to EVACS or the building FACU. Non-FM releasing: 24 h + 5 min [PARA].
- Speaker circuit: a battery pass does not clear the speaker circuit. Check speaker line loss at 1.0 dB as well. Run `fa-speaker-circuit-loss-check`. That 1.0 dB limit is [CODE] on NFPA 72-2025 §18.3.7.2.1(1) and [PRACTICE] on 2019 and 2022.
- Worked screens, loads ASSUMED, not a job. On 2022 or 2025 use F = 1.25 (§10.6.7.2.14). Use F = 1.20 only as the NFPA 72-2019 factor (§10.6.7.2.1.1). Never apply 1.20 on a 2022 or 2025 basis. EVACS booster at 24 h + 15 min: (0.50 A × 24 + 5.00 A × 0.25) = 13.25 Ah. Times 1.25 = 16.56 Ah against an 18 Ah pick. The duration passes. The same base times 1.20 is 15.90 Ah and is the 2019 factor only. The same loads at 90 h + 10 min use the wrong duration. 90 h + 10 min is releasing only, and it is 10 min, not 5 min. Building FACU at 24 h + 5 min with 0.60 A standby and 4.40 A alarm, 2019 factor: (0.60 × 24 + 4.40 × 5/60) × 1.20 = 17.72 Ah against 18 Ah. The duration passes and the spare screen fails. Twenty percent spare on that 2019 building screen is 21.26 Ah. Twenty percent spare on the 1.25 EVACS result is 19.88 Ah. The training screen picks 26 Ah for both. Those catalog sizes are ASSUMED and synthetic. Do not lock 18 Ah or 26 Ah on a live job. A double-interlock releasing screen on maker data, F = 1.25: base 15.20 Ah becomes 19.0 Ah, pick 26 Ah; the FM owner case, base 56.45 Ah at 90 h + 10 min, becomes 70.6 Ah, pick 100 Ah. Do not copy a 1.20 product of those bases (18.24 Ah or 67.34 Ah) or a 90 h + 5 min base (56.12 Ah). The 20 percent spare, or the next size, is a training value [PRACTICE], not [CODE], and not an approved live design. Verify with the engineer of record. Duration pins are unchanged.
- [CODE] §10.6.7.2.13: include all loads not automatically disconnected on transfer.
- **Edition-keyed battery factor (never hardcode):**
 - NFPA 72-2019 §10.6.7.2.1.1*: "Battery calculations shall include a minimum 20 percent safety margin above the calculated amp-hour capacity required." Use F = 1.20 [CODE 2019].
 - NFPA 72-2022 and 2025 §10.6.7.2.14*: "a correction factor of 1.25 for aging." Use F = 1.25 [CODE 2022/2025].
 - Edition unknown: run `fa-code-edition-delta-check`; if still unknown, ASSUME the higher factor (1.25) and flag it [PRACTICE]. Never apply both.
- [CODE] §10.6.7.3.1(2): automatic generator plus dedicated batteries with 4 hours of capacity (same text 2019 / 2022). The text does not say whether alarm minutes ride on top. Generator credit needs a generator per 10.6.11.3.1.1 (2022 and 2025): NFPA 110 Type 10, Class 24, Level 1. NFPA 110-2022 and 2025 Table 4.1(a) have no Class 24. Default: specify NFPA 110 Class X set to 24 h fuel, Type 10, Level 1 [CODE pointer; Design practice; Verify with the engineer of record]. If the generator does not meet that, no 4 h credit: size 24 h battery only.
- Generator fuel: where the Class X (24 h) generator is the credit, NFPA 110-2025 5.5.3.1 sets the main tank at no less than 133 percent of the 5.5.2 low-fuel quantity for classes of 24 h or less; 5.5.3.2 sets 100 percent above 24 h (`calcs/fa/lib/epss_fuel.py`). Hand the 1.33 multiplier to the generator engineer; FA does not size the tank [CODE NFPA 110-2025].
- Battery size cap: if the 24 h battery-only case exceeds the largest listed battery for the panel or supply (100 Ah in the corpus standard list, VERIFY against the panel and charger listing), first choice is to split the load onto a second listed supply and keep 24 h battery only. Example: two 55 Ah listed supplies, each under its own listing, each sized for 24 h plus alarm time with the edition factor. Design practice is to split the load before using one battery larger than the listing. A single larger battery is allowed only where the maker lists one supply at the needed size. Rechargeable batteries must be listed or recognized per NFPA 72-2022/2025 §10.6.10.1.3 (new in 2022). Generator plus 4 h is allowed only where the generator meets the item above. Verify with the engineer of record. The 4 h case (4 h quiescent plus the alarm period) is [PARA]; confirm it with the AHJ.
- [CODE] NFPA 72-2025 §7.2.1(7); same item in 2022 and 2019: documentation includes battery capacity and safety margin calculations where batteries are provided. Ch. 14 annual secondary-power test confirms capacity plus margin.
- [CODE] Table 14.4.3.2 item 8, Initial X and Annually, same words in 2019, 2022, 2025 : disconnect primary, verify the trouble signal, verify battery rated capacity exceeds standby and alarm demand "including the safety margin" from manufacturer's data, run general alarm 5 min (voice 15 min). Reading "safety margin" as this skill's F is [PARA]. The 5 / 15 min are test run times, not sizing inputs. 2025 fn c: a listed charger/power supply that verifies demand may be approved as equivalent.
- Releasing panels: NFPA 72-2025 has NO releasing-specific duration. Applying 24 h + 5 min to a releasing panel is a **[PARA]** reading of §10.6.7.2.2, never [CODE]. Longer alarm time (e.g., 10 min) is insurer, owner, or practice; label it. FM DS 5-40 §2.3.4 (September 2007) [OWNER DS 5-40] gives 90 h plus 10 min for preaction release panels. Verify with the engineer of record: September 2007 is the held edition; confirm it is current with the insurer. Conservative assumption: FM jobs carry 90 h + 10 min; NFPA-only jobs 24 h + alarm per 72. Do not apply 90 h to EVACS. DS 5-23 is not an FA duration source.

## BESS add-on (Li-ion ESS rooms, NFPA 855-2023, IFC 2024)
- [CODE] NFPA 855-2023 4.8.3: Li-ion ESS smoke and fire detection must carry 24 h standby and 2 h alarm. 4.8.3 covers smoke and fire detection, not gas. The FACP serving BESS room detection is sized 24 h + 2 h, not 24 h + 5 min. Alarm signals from that detection go to a supervising station [CODE §4.8.4]. Confirm adoption of 855-2023 with the AHJ. Running the whole FACP at 2 h alarm is an UPPER BOUND; split out the ESS detection load where the panel serves more (Verify with the engineer of record). No new battery arithmetic. The 1.25 factor on 2022 and 2025, the 1.20 factor on 2019 only, and the FM releasing case of 90 h + 10 min [OWNER] stay as written above. On a Canada job, stop. CAN/ULC-S524 hours stay NEEDS HOLD. Do not map NFPA 72 as Canada code.
- [CODE] NFPA 855-2023 9.6.5.6.7(4) : Li-ion gas detection gets at least 24 h standby and 2 h alarm, or more if the HMA requires. Item (3) asks only 2 h; the Li-ion item governs [PARA]. 9.6.5.6.7 applies only on the explosion control path. On the exhaust rate path, 855-2023 9.6.5.1.5.4(3) asks 2 h standby only. Default kept, no value change: size the gas panel at 24 h + 2 h on both paths [PRACTICE; Verify with the engineer of record, conservative]. Show both results, for example 2 h basis vs 24 h + 2 h basis. IFC 2024 1207.6.1.2.4 sets no detection battery hours (it points to Section 916).
- [CODE] IFC 2024 916.5 (Emergency and Standby Power): standby power or trouble on power loss (FA-SKILLS-verify-01). 916.4 covers power connections. 916.5 sets no hours, so the trouble-only path does not meet 855 for Li-ion.
- [CODE] IFC 2024 1207.6.1.2.1 (Standby Power): exhaust on standby power for at least 2 h per 1203.2.5 (FA-SKILLS-verify-01). Fan power is not on the FA battery; record it as a mechanical/electrical item.
- Gas panel calc: controller, all gas heads, gas horn/strobes on the gas panel. Gas heads draw near alarm current in standby on many products; use data sheet values.
- Factor: apply the enforced NFPA 72 edition factor to the gas panel 24 h + 2 h calc, same as the FACP: F = 1.20 on 72-2019 (10.6.7.2.1.1, 20 percent safety margin) or F = 1.25 on 72-2022/2025 (10.6.7.2.14, aging). Never both ( 2019 and 2022). Edition unknown: use 1.25 and flag [PRACTICE]. 855-2023 4.8.3 points to NFPA 72 secondary power (upheld 2026-10-23) [CODE pointer]; also 72-2022 17.10.2.2 where it interfaces the FA system. Then add owner margin if any (ASSUMED 20% on top only if owner requires; never double count without saying so). Derate for battery temperature where the room runs warm, per manufacturer data [PRACTICE].
- Traps: a 72-only 24 h + 5 min FACP calc that passes but fails the 855 2 h alarm; a gas panel sized for 2 h only.
- Steps: run the FACP case at 24 h + 5 min and at 24 h + 2 h; carry the larger. Run the gas panel at 24 h + 2 h. Report each pick and margin. Open item if HMA asks for more.

## Inputs (ASSUME and flag any missing)
1. Load list: item, qty, standby A, alarm A from listed data sheets (ASD heads, solenoids, modules, NACs).
2. Which loads ride this panel vs separate supplies (each gets its own calc).
3. Service type: protected premises, voice/alarm, releasing.
4. Generator credit taken or not.
5. Panel charger max Ah, available battery sizes.
6. Enforced NFPA 72 edition (drives F).
7. BESS present? Enforced NFPA 855 edition, HMA duration if any, gas panel load list.

## Steps
1. Build the load table in a script. Sum Is and Ia.
2. Durations: use the duration pins above. Standby 24 h (or 4 h quiescent plus alarm period with generator credit, [PARA], AHJ to confirm); alarm 5 min, or 15 min at max load for voice. For releasing, show 5 min [PARA] and the FM 90 h + 10 min case side by side when FM insures. Keep the building FACU, EVACS, and the releasing FACU as separate batteries. If the supply feeds speakers, a passing battery calc still leaves the 1.0 dB speaker-loss check open.
3. Required Ah = (Is x standby h + Ia x alarm h) x F, with F from the edition-keyed factor above. Print the edition and F in the script output. Pick the next standard size up. Report safety margin = picked Ah minus required Ah (and as a percent).
3a. Thin screen: spare under 20% of required Ah is THIN. That 20% spare is a training value [PRACTICE], not [CODE], and not an approved live design. Do not cite it as a code minimum. Verify with the engineer of record. The edition factor F is separate and stays [CODE]. Conservative: step up one standard size. Flag, do not change elected values silently.
4. Check against panel charger limit; if over, call for separate charger or battery cabinet.
5. Note what dominates (often ASD heads on aux power); show sensitivity if moved to separate supplies.
6. On FM DI jobs add: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job."

## Output
Load table (ASSUMED flags), Is, Ia, labeled durations, edition and factor F with its section (2019 §10.6.7.2.1.1 at 1.20; 2022/2025 §10.6.7.2.14 at 1.25), required Ah per case, pick, safety margin [CODE §7.2.1(7) documentation item], charger check, open items, delta vs NFPA 72-2025. The load table, F and pick are the demand record for the item 8 acceptance test; hand them to the ITM plan.


## Canada secondary power

On a Canada job the US durations above are a comparison floor only. Do not cite them as CAN/ULC-S524. S524 standby and alarm duration are NEEDS HOLD. Do not invent S524 hours. Where FM is carried, 90 h + 10 min stays the FM owner figure for the releasing panel only, and the Canada duration for that panel is also NEEDS HOLD. Do not invent a Canada speaker-circuit loss value.
