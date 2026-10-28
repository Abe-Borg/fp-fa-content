---
name: fa-asd-vewfd-data-hall-sampling-layout
description: >-
 Use when you must lay out ASD/VEWFD sampling for a US hyperscale data hall:
 ports per level, return sampling (including a common fan wall, sampled before mixing),
 head count, and transport-time target per
 NFPA 72-2025 §17.7.4.6, NFPA 75-2024 or 75-2020 §9.2.2, FM DS 5-32 s2.4.2.2 when FM
 insures, and NFPA 76-2020/2024 §8.5.3.1 only if elected. Packet optional;
 missing inputs ASSUMED.
---
# FA ASD VEWFD data hall sampling layout

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: wet, dry, or double-interlock (DI) preaction only. No clean agent. No foam. Single- or non-interlock as basis of design: record, Stop, RFI-variance.

- On FM DI jobs carry the standing flag: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job."
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER] (or [OWNER]/insurer). Cite section AND edition. Mark approximations with ~. Never invent code text; gaps get "section not pinned; verify before use.
- Pin the enforced NFPA 72 edition first. A label can change by edition (run `fa-code-edition-delta-check`).
- Three-layer basis (code x insurer x owner); most stringent wins; report delta vs the enforced edition and NFPA 72-2025.
- Run math in a script; show inputs. Short sentences. No em dashes or en dashes (write "to"). Verify judgment calls with the engineer of record. Copy METHOD, not synthetic numbers.

## Inputs (ASSUME and flag any missing)
1. Hall area (ft2), ceiling height, slab or raised floor.
2. Cable tray or obstructions that block smoke (one vs two levels).
3. Containment (hot or cold aisle) and return path (CRAH returns or fan wall), return opening area.
4. Insurer (FM or not). NFPA 76 elected by owner, insurer, or AHJ, and which edition? It is telecom scope, NOT automatic for a hyperscale hall.
5. Listed ASD head: max holes per head, listed design software.
6. Preaction valve areas from the sprinkler zone schedule.

## Basis (held sources only)
- [CODE] NFPA 72-2025 §17.7.4.6.1.1*: each port treated as a spot detector for location and spacing per §17.7.4, absent performance-based criteria.
- [CODE] §17.7.4.6.2.1: transport time from farthest port shall not exceed 120 s (a max, not a floor).
- [CODE] §17.7.4.6.2.2 to .2.4: network by computer-based fluid dynamics calcs incl. pressure, flow, sensitivity at each port; software listed for the equipment. §17.7.4.6.2.7: benchmark end test ports in calcs.
- [CODE] NFPA 72-2025 §17.7.7.3.3.3*: in high air movement areas, air sampling follows the manufacturer's published instructions. Table 17.7.7.3.3.2 does not bind ASD ports.
- [CODE] Edition numbering: 2022 = 2025 numbers above. On a **72-2019** job cite §17.7.3.6 (§17.7.3.6.1.1*, §17.7.3.6.2.1 120 s, §17.7.3.6.2.2 to .2.4, §17.7.3.6.2.7*) and high air movement §17.7.6.3.3.3 / Table 17.7.6.3.3.2; same requirements. Run `fa-code-edition-delta-check` first.
- [CODE] ITM (feeds the ITM plan, not the layout): Table 14.4.3.2 17(7)(d) ASD functional test **Annually**; Table 14.3.1 17(1) filters semiannual, piping/ports at acceptance; sensitivity per §14.4.4.3. 2022/2025: end-port smoke test and airflow check at other ports "In the absence of an automatic, listed airflow supervision feature." **2019**: the row body has the end-port test on each pipe run and airflow at all other ports with no such condition; Table 14.3.1 reference §17.7.3.6. Settled. 17(7)(d) has no footnote and 2019 Ch. 14 has no airflow-supervision text. On 2019 jobs the end-port test is [CODE 2019], even with listed airflow supervision. Ch. 14 has no transport-time test.
- [CODE] NFPA 75-2024 §9.2.2* (when NFPA 75 is in the basis; **75-2020 SAME** per ): detection at (1) ceiling level throughout the ITE area; (2) below a raised floor containing cables; (3)* the exhaust/return air stream where aisle containment is used; (4) the return air stream where the above-ceiling area is a return plenum. §9.2.2.1: return-opening ports cover no more than 4 ft2. On a 2020 job cite 75-2020.
- [OWNER]/insurer FM DS 5-32 (Jan 2026) s2.4.2.2 (s2.4.2.2.1 to .7 .md, run 208; FM, non-): ports in return air, equipment area, below raised floor (s2.4.2.2.1). Return 4 ft2/port (s2.4.2.2.3; spot detectors s2.4.2.3.1). Ceiling single level 200 ft2/port (s2.4.2.2.4); two levels 400 ft2/port (s2.4.2.2.5; two levels where trays block smoke, s2.4.2.2.6). Transport 60 s (s2.4.2.2.7). s2.4.2.1.3 (with .3.1 and .3.2 .md pass 4): at or above 5 ft/s or 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only], slow ventilation on VEWFD pre-alarm.
- [CODE] NFPA 76-2024 §8.5.3.1 (only if elected): one level 200 ft2/port (§8.5.3.1.2.1*); two levels each 400 ft2/port, stagger no more than 200 ft2 (§8.5.3.1.2.2*); returns 4 ft2/port (§8.5.3.1.2.3*); alert 0.2 %/ft, alarm 1.0 %/ft (§8.5.3.1.2.5*); transport max 60 s excl. benchmark ports (§8.5.3.1.2.6). §8.4.2.2.4(1): VEWFD alert (prealarm) is a supervisory signal. §8.4.2.2.9: supervisory signals do not activate building NACs. NFPA 76-2020 has the same values at the same sections (returns §8.5.3.1.2.3(C)).
- [PRACTICE] Maker guidance: balance and port share per listed software.

## Steps
1. Pin basis layers: FM? NFPA 76 elected (which edition)? If neither, governing spacing is §17.7.4.6.1.1, plus NFPA 75 §9.2.2 when 75 is in the basis; say so. In high air movement, port spacing follows the maker's published instructions (§17.7.7.3.3.3*), not Table 17.7.7.3.3.2.
2. Levels: trays blocking smoke means two levels; else one.
3. Ceiling ports: one level area/200; two levels area/400 **per level** (not combined). FM s2.4.2.2.5 reads: "If two levels of detection are used (ceiling and below raised floor level), install an air sampling port or remote sampling point in an area no larger than 400 ft2 (37.2 m2) for both levels" . Verify with the engineer of record. Conservative assumption: 400 ft2 per port at each level, not combined. Stagger: where NFPA 76 is adopted or elected, coverage between high and low levels is no more than 200 ft2 [CODE NFPA 76-2024 §8.5.3.1.2.2(2); 76-2020 same section]; cite the adopted 76 edition. Where 76 is not in the basis: on FM jobs the stagger is FM s2.4.2.2.6, no more than 200 ft2 between each level [OWNER/insurer] ; off FM, use the half-grid offset in `fa-two-level-detection-stagger-and-fm-mapping` as [PRACTICE]. Report per level, total, grid.
4. Return ports: return area/4 ft2 [CODE NFPA 75-2024 or 75-2020 §9.2.2.1 when 75 is in the basis ; NFPA 76-2020 §8.5.3.1.2.3(C) or 76-2024 §8.5.3.1.2.3 when 76 applies; FM s2.4.2.2.3 OWNER/insurer]. On a common fan wall, do not apply that 4 ft2 rule to the mixed face. Use the fan-wall return-plane section below. Ports inside each contained hot aisle [CODE NFPA 75 §9.2.2(3)] and in an above-ceiling return plenum if used [§9.2.2(4)].
5. Equipment-area ports (FM) and below-floor ports (raised floor with cables, NFPA 75 §9.2.2(2)). Layout-dependent; mark TBD if no plan. Do not invent a count.
6. Heads, per valve area, then summed. Partition known ports by preaction valve area. A head serves one valve area only. Inside each area, heads = known ports in that area divided by the listed holes per head, rounded up. The listed cap governs inside that area. Total heads = the sum of those per-area counts. Do not divide the hall total by the head capacity and round once. Two areas of 20 ports with a 40-port head need two heads, not one. If an area's port count is TBD, leave that area's heads TBD. Do not invent the count.
7. Transport: 120 s NFPA 72 max; 60 s governs where FM or NFPA 76 applies (76-2024 8.5.3.1.2.6 is [CODE] where 76 is adopted or owner-required; in an MMR otherwise carry it as [PRACTICE], Design practice. Report value and source. If any port exceeds 60 s, fix the design, never the cap: split into more, shorter branches or add a detector, then rerun the maker calc until every port is at or under 60 s . A shared two-level detector that cannot hold 60 s fails. `calcs/fa/lib/asd_v2.py` is a screen only; the maker calc certifies.
8. Thresholds: if 76 elected, alert 0.2 %/ft and alarm 1.0 %/ft; else [OWNER]. Design practice (design practice item 7, 2026-10-15): on FM jobs the owner VEWFD **Action or Fire 1** level counts as FM pre-alarm. It is an alarm-level signal and is the DI detection leg (leg 1). It opens the preaction valve only together with low air. Confirm on the owner sequence which of Action or Fire 1 is used; full level map in `fa-two-level-detection-stagger-and-fm-mapping`. NFPA 76 **Alert** stays supervisory [CODE NFPA 76-2024 §8.4.2.2.4(1)]: no building NAC [§8.4.2.2.9], never leg 1, never arms a release. Fire 2 is not OK as the leg on FM jobs.
9. Ventilation at or above 5 ft/s or 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only]: add FM slow-down interlock on FM pre-alarm (Action or Fire 1 per item 7) and its acceptance test.
10. Run listed design software (e.g., ASPIRE): worst-port transport, balance, share. Never certify transport from a hand count.
11. FM flags on every FM job: "[OWNER]/insurer conflict: FM DS 5-32 (Jan 2026) s2.4.1.1 ranks DI preaction last. Company decision (design practice): keep DI. Flag to owner and FM on this job." Also flag s2.4.3.2.1.3 no cross-zone: company FM default is single leg (Fire 1 or Action) AND low air, which complies; flag only if the owner forces two-leg cross-zone [OWNER].

## Fan-wall return plane

Use this when the hall has a central fan wall or one common return. Ceiling and below-floor counts above still apply. This section sizes the return layer and the staged ventilation response. It does not elect the sprinkler family and it does not replace the listed pipe-network model.

**Sample before mixing.** Put the primary return layer on the last mechanically discrete return or exhaust-plenum sections on the mechanical schedule, upstream of the common face. If the hall has only one mixed plenum, create engineered sectors from that schedule and sample each sector before the final face. Document against the schedule. Do not treat fan cells, perforated panels, or equal-area rectangles on the mixed face as unit returns. Do not put ports inside the air handler: at high air change, smoke is diluted below a detectable level before the unit.

Show the literal mixed-face count, then reject it:

```
A_face = Q_H / V_face
n_literal = ceil(A_face / 4)
```

Those ports sit after mixing has erased the local concentration. With M equal returns on one face, a local concentration is read as about 1/M at the common face. A 20-unit wall can need about 4.0 %/ft locally to read 0.2 %/ft at the face, which is past the 1.0 %/ft alarm tier. That is why the design count is class coverage at the relocated plane, not `ceil(A_face / 4)`.

**Airflow gate, room volume only.** `ACH = 60 * Q_H / V_H`. `V_H` is the room only. Exclude the subfloor and the ceiling plenum. A plenum-inclusive volume lowers ACH and can hide the gate. Size `Q_H` for maximum outside air or economizer when that mode exists. Recompute ACH. Do not trust a supplied ACH that used a different volume. FM DS 5-32 (Jan 2026) s2.4.2.1.3: below 5 ft/s or below 60 ACH, else interlock ventilation to slow on pre-alarm and acceptance-test that interlock. The 60 ACH figure is owner/insurer (FM DS 5-32). It is not in NFPA 75-2024 Ch. 4 to 13. The sheet's measurement pointer is a velocity test. Compute ACH anyway. Argue the clear on velocity. Do not pass the gate by enlarging the volume. If ACH is over 60 or velocity is at or above 5 ft/s, the interlock is required. Do not desensitize the detector to avoid it.

**Ports per discrete section.** Name the class, then space to it. Do not let a high-air-change "400 ft2" suggestion demote VEWFD to EWFD.

| Class | Area per port | Basis |
|---|---|---|
| VEWFD | 200 ft2 | FM DS 5-32 s2.4.2.2.4; NFPA 76-2024 §8.5.3.1.2.1 when 76 applies |
| EWFD | 400 ft2 | FM two-level s2.4.2.2.5; NFPA 76-2024 §8.5.3.2.1.2 when 76 applies |
| Standard | spot spacing per §17.7.4 | NFPA 72-2025 §17.7.4.6.1.1. No 900 ft2 per port. In high air movement, follow the maker's published instructions (§17.7.7.3.3.3*). |

`n_j = ceil(A_j / A_class)`. `N_ports = sum(n_j)`. The return network protects while airflow is on. The ceiling or void network protects when airflow is off, including during slowdown. Design both. A starved-return flow fault is not a detection outage.

**Opening disclosure, not a metric swap.** If face velocity or return area is known at the discrete section, `ft2_per_port = A_return,j / n_j`. Compare to the 4 ft2 opening rule (FM s2.4.2.2.3 and s2.4.2.3.1; NFPA 75 §9.2.2.1 when 75 applies). If the ratio is over 4, print it and ask for written FM or AHJ acceptance. Do not "fix" it by gridding the merged face. Do not silently switch the count to `ceil(A_return,j / 4)` unless that election is written.

**Chamber, then the listing cap.** Balanced line: panel setting is about `Sh / N`, and effective per-port sensitivity is about `Sc * N`. Design to the body tiers, alert 0.2 %/ft and alarm 1.0 %/ft (FM DS 5-32 s3.3.2.2 and s3.3.2.3). Do not design to an appendix figure of 0.02 %/ft. That figure is about 10 times tighter than the body tier. Worst case is smoke in one hole. A single panel value that ignores hole count is too insensitive by about N.

```
H_sens = floor(0.2 / Sc_min)
H_allow = min(H_listing, H_sens)
N_det = sum over sections of ceil(n_j / H_allow)
```

`H_allow` is per chamber, not per pipe. A four-pipe head still has one chamber. On measured hardware the listed hole cap binds before the chamber floor. Usable VEWFD area is about listed holes times 200 ft2. A datasheet area built on a coarser class is not the VEWFD area. Still run `H_sens`: a coarse family can fail a 25-port line. Also bind listed maximum pipe length. Put the head in conditioned space. Sampled air can be hotter than the head rating. Do not span subfloor, hall, and return plenum on one network.

**Transport screen is not acceptance.** A balanced single-pipe screen, `t_screen ≈ Ap * L * H_N / QT` with `H_N = sum(1/k)` for k = 1 to N, is a plausibility check only. Verify the identity before using it on the project line: 3/4 in tube, Ap about 0.00307 ft2, QT = 80 L/min is about 0.0471 ft3/s as an example only, H_25 about 3.816, so 200 ft is about 49.7 s and 250 ft is about 62 s. Use the caller's QT, N, and a declared L. Do not reuse 80 L/min on a different head. The screen has no multi-branch form. NFPA 72 requires the listed fluid-dynamics model, and acceptance is the commissioned time from the most remote hole. Do not emit hole sizes from this screen. Commission at the worst credible mode, including economizer, fan failure, and the pre-alarm slowdown speed. Balance at or above 70 percent. End cap is the vented last hole. Standoff sampling pipe 2 in to 8 in off the grille. Orient holes 20 degrees to 45 degrees to the airflow, never straight into the flow. Exhaust the aspirator back into the sampled room only with the maker's limit in view: exhaust past the protected length can break the 60 s cap.

**Staged response (intent, not the full releasing matrix).** One detection zone is one discrete return section. Single-detector logic. Do not cross-zone the preaction trip (FM DS 5-32 s2.4.3.2.1.3). Hand the Boolean to `preaction-releasing-c-and-e-soo`. The trip family, when there is one, is wet, dry, or double-interlock from `suppression-technology-selection`.

| Stage | Effective per port | Actions |
|---|---|---|
| L1 Alert | 0.2 %/ft | Annunciate. Start ventilation slowdown when the airflow gate requires it. No release. |
| L2 Action | 0.4 %/ft to 0.6 %/ft band | Localize. Arm power isolation (readiness only). Hold slowdown. Trip that zone's preaction valve when the FM L2 trip applies. |
| L3 Fire 1 | 1.0 %/ft | Fire alarm and fire service. Execute power isolation per `power-isolation-disconnect-control`. |

FM body text gives 0.2 %/ft and 1.0 %/ft. It does not publish the 0.4 to 0.6 band. That band is design practice. Verify with the engineer of record. Conservative assumption: trip at L2 and set Action at 0.4 %/ft, inside the head's listed range. Do not use 0.2 %/ft as the trip (a filter change will trip it) and do not wait for 1.0 %/ft (that gives up the pre-alarm margin). On an FM job, Action or Fire 1 is the DI detection leg per step 8 above. NFPA 76 Alert stays supervisory when 76 applies.

No automatically operated smoke exhaust on detection in the data-processing room (FM s2.4.2.1.7). If a code forces automatic exhaust, interlock it to sprinkler waterflow. Sheet language that also names water-mist waterflow is comparison only. Do not elect mist. Do not add an abort. Do not raise sensitivity to compensate for airflow. Slowdown dwell, thermal limit, and restoration are not in the sheet: label them ASSUMED with the mechanical designer and the owner. Restoration does not reset a latched stage. A cold-aisle high-temperature alarm can truncate slowdown. Detection does not outrank the IT thermal limit. Witness fans on and fans off. The heated-wire script stays in `commissioning-ist-acceptance-packet`.

## Output
Labeled basis table; ports per level, return (discrete section, not the mixed face), equipment (or TBD), below floor; heads per valve area and the summed head count; governing transport and whether it is a screen or the listed model; airflow-gate flag; ASSUMED list; open items; delta vs NFPA 72-2025.
