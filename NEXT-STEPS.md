# Next steps after the app-v0.2.0 acceptance report

Written 2026-11-12 against `REPORT.md` (run CYN020-20261111, target `app-v0.2.0`, commit `24cebb48`). This is a plan. No code, test, or content file was changed to produce it.

**Read this first.** The report tested 0.2.0. `main` is 0.3.0, twelve commits later, and the hardening milestone in it landed about three and a half hours before the test run began. Of the ten defects, three are fixed or gone at HEAD (BUG-001, 004, 008), three are partly fixed and still open (BUG-002, 003, 007), and four are unchanged (BUG-005, 006, 009, 010). I found five more things the report did not raise (N-1 to N-5). Everything below is judged against HEAD (`10fdd37`), with what was true at the tested commit stated beside it.

How each finding was checked: I extracted the tested tree next to HEAD and ran the report's reproduction steps against both, with no model. Where an agent takes part it is a script written in advance, so those results show what the application does, not what the live model does. Nothing here was run on Windows, nothing was sent to the live model, and no standard was opened. Section 8 is the full account.

Sizes: **S** is under about 50 lines of application code plus a test, **M** is 50 to 200, **L** is more. Owner is **App** (Claude), **Content** (the Grok team, through the FP/FA App Grok Bot), or **Mixed**, per the ownership rules in `CLAUDE.md`.

---

## 0. Status: items 1 to 6 are done, as version 0.3.1

Added 2026-11-12, after the owner's answer to question 1 ("fix first as 0.3.1, start with items 1 to 6") and with two of the report's evidence files in hand. Everything below this section is the plan as first written; this section says what became of it.

| # | Defect | What was done | Held by |
| --- | --- | --- | --- |
| 1 | BUG-006 | A cut-off checker reply ends the check and changes no finding; it is a `check_incomplete` event with its usage and is never the latest check. The request asks for 16,000 tokens and keeps the stop reason. A record goes eight claims to a request. A claim a finished reply skips is "No verdict" and goes back to not checked. A finding may rest on a decision, and a support id on no table is said in the tool result | `test_acceptance_report.UnfinishedCheckTests` (9) |
| 2 | BUG-005 | A calculation whose cites name another edition than the job states carries EDITION NOT RECONCILED, before a rerun and after one, in the draft, the coverage gaps, the run's flags, `/status`, the lead's block, and the Team tab | `EditionHoldTests` (5) |
| 3 | BUG-003, N-3 | A supported finding is in the first group only when the application matched a figure or the releasing record's expression in it; otherwise it is in a new fifth group. The figure rule reads every known unit by class. A fact a contributor wrote is a RECORDED FACT, not a project input | `TraceGuardTests` (7) |
| 4 | BUG-002 | `di_trip_to_water` and `nitrogen_gate` run on the takeoff's own zone total | `test_hardening`, `test_a_rounded_volume_cannot_carry_the_trip_time_across_its_limit` |
| 5 | N-1 | The calc-code identity and the content fingerprint hash a file with its line endings set aside | `IdentityTests` (3) |
| 6 | BUG-010 | The Section 21 13 19 claim check closes on a `section_check` event with its usage, counted in the cost report, blocked export or failed request alike | `SectionCheckUsageTests` (4) |

**What the two evidence files settled.**

- `truncated-checker-proof.json` is BUG-006 exactly as inferred: `stop_reason` `max_tokens`, 4,000 output tokens of which 4,000 were thinking, and an empty `content` list. It adds one figure the plan did not have: that one check carried 30,046 input tokens for about sixteen findings. That is why the fix splits the record into requests of eight and does not only raise the ceiling. The tests replay this reply.
- `section-export-assessment.json` answers item 7 (N-2). The tester's own reading of the 1-of-12 result is that the cite "flattens tool figures into unlabeled number bag, so checker refuses to infer quantity roles", and that it was not a truncation. That is the cause proposed in section 3, now on the tester's evidence and not only on a reading of `claim_check._package_source`. So item 7 is no longer "find out why": it is application work, to build the Section cites from each record's named outputs the way the trace check does. It is **not** done here; it was not among items 1 to 6.

**Where the work departs from the plan as written, and the defaults taken on questions that were not answered.** Each is one constant or one small function, and each is yours to reverse.

1. *Question 2, an unfinished check and the Design Basis.* The export waits, as it does when no check has run. That is the rule `CLAUDE.md` already had ("a current trace check"), so no gate was changed. The plan's alternative, exporting with the findings marked not checked, would change that rule and is still yours to choose.
2. *A cut-off reply keeps nothing.* The plan's test said "k judged, the rest untouched". Implemented instead: a cut-off reply writes no verdict at all, because a check speaks for the findings it saw or for none, and half of one beside half of an older one would read as a single check. A reply that **finished** and skipped a claim is different: the check is complete and that one claim goes back to not checked.
3. *Question 3, the new group's name.* It is "Trace-consistent with an identified row, on the checker's reading alone" (`checker.TIER_TITLE`). Reword it as you like; the tests hold only that no title reads as verification.
4. *The wrong release statements are kept out of the first group, not rejected.* "Releases on detection alone" with a checker that approves it now lands in the new group with the reason that only the checker's reading stands behind it. A true statement in other words lands there too: the application cannot tell them apart. Rejecting the false one needs new wording rules, which the pack lint carries a copy of. That proposal is written up for the content team in `docs/content-provenance.md`, section 2b-1, with the gallons constant and the 2022 edition body.
5. *Question 9, `.gitattributes`.* Not added. The hash was made insensitive, which closes the defect by itself and does not touch your Windows working tree. Pinning line endings is still open.
6. *The edition hold is a row-level hold.* It does not move a finding to the engineer's group, because most findings on a held calculation (a trip time against the insurer's screen, say) do not turn on the edition. It is not staleness either. And the application still passes no edition to the kernel: whether it should, for 2019, is the mixed question in section 3.
7. *The gas fill is included in item 4*, as planned, and it changed one existing test's fixture: a specialist's gas-fill call with the volume rounded and the plan's own pressure and time is now the plan's row, so that test's exploratory calculation became a what-if on the fill time.

**Limits found while doing it, not fixed.**

- The first group's test is what the application matched, not what is true. A finding that quotes the releasing record's expression and then contradicts it in the same sentence would still be in the first group with an approving checker, as a finding with a correct figure and a wrong conclusion always could.
- "600 gal/hr" is still read as 600 gal: one of the eight original units followed by a slash is taken as that unit. Only a ratio that starts with a unit the application does not know gets a class of its own.
- A number written in words is read only before one of the eight original units, and "one and two minutes" is not read at all.
- A record made on a Windows build under 0.2.0 or 0.3.0 holds the CRLF identity and will read as out of date once under 0.3.1. It would in any case: the kernel changed between those versions.
- The scripted evaluation's probe check is two requests now, since it covers eleven findings.

**Suites at the head of this work**, on Linux, Python 3.13.18: `calcs/fp` 262 pass (1 skipped), `calcs/fa` 88 pass (13 skipped), `app/frontend` 29 pass, `app` 540 tests, 539 pass and the same one environment error as before (`pywebview` does not install in this container). Both browser tests ran. The page was rebuilt and the README's pictures retaken from the scripted scenario.

**Still not done by anyone:** nothing in 0.3.1 has run on Windows or against the live model. Items 7 to 10 of the list below are open. Section 5 is unchanged except that the line-ending step is now a written step in `docs/acceptance-tests.md` (Test A, step 2a).

---

## 0b. Version 0.3.2: the app-v0.3.0 acceptance report

Added 2026-11-12. A second acceptance run (the "+Cynosure app test report", 2026-11-11, by another party) tested 0.3.0 at `04196bd` from source in Chromium on Linux, and found ten defects and a list of known gaps. Its verdict was NO-GO for acceptance under its regimen. `main` was then 0.3.1, which had closed two of the ten. Each finding was checked against 0.3.1 before anything changed, with the report's own evidence files where it had them: the checker diagnostic replay, the SI-unit records and reply, the missing-input reply, the corruption runs, and the contrast measurements. The owner then took the recommendations below as decisions.

| Finding | Report's severity | At 0.3.1 | What 0.3.2 does | Held by |
| --- | --- | --- | --- | --- |
| F-001 a density or area of 0 runs | S1 | Open; the plan and the form also put 40 psig, 30 min, and 0 in place of a blank or a 0 | A zone run refuses a 0 where it means nothing and a blank it needs, naming each by the form's label; the form keeps what was typed; the lead cannot record a 0 density. The kernel still accepts a 0 in `density_area` (a content proposal) | `test_acceptance_report_030.ZoneInputTests` (7) |
| F-002 a cut-off check read as "Not supported" | S1 | **Fixed in 0.3.1** (`a6e94a3`) | Its parser read only "N. Verdict" exactly, and since 0.3.1 a line it misread sends the finding back to not checked. It now reads case, bold, "1)", and list markers. Stop is heard between a check's requests | `CheckerReasonTests` (6); 0.3.1's `UnfinishedCheckTests` |
| F-003 Team tab still during a turn | S2 | Open | Read again at most every two seconds while a job on the open job works | `LiveTeamTests` (1) |
| F-004 damaged record, traceback | S2 | Open; reproduced on all three of the report's damaged copies | Named, left as it was, moved aside only on a yes, never deleted; `--move-damaged-record`. A record another program has locked, or one that cannot be opened or written, is not called damaged and is never offered to be moved (found in review of this change) | `DamagedRecordTests` (6) |
| F-005 secondary text below 4.5:1 | S3 | Open, and wider: error, warning, and link text too | Secondary text is `--ink-dim`; status-coloured text is mixed toward the ink; a test reads every text colour in every scheme | `TextContrastTests` (2) |
| F-006 a claim the screen does not depend on its assumed times | S2, live | The tool returned the fill time alone (28.1 s, inside 30 s) | The delivery tile prints it and the margin beside the verdict. The rule a team should keep is content and is proposed to the content team | `FillTimeTileTests` (1) |
| F-007 the checker's reasons thrown away | S2 | Open | Kept as the checker's reading, apart from the application's, on the Team tab, in the Design Basis, and to the lead; the reply text kept for an audit | `CheckerReasonTests` |
| F-008 SI figures run as US ones | S1, live | Open; nothing could convert | `fpfa.units` and the `convert_units` tool, recorded; `set_input` with a unit keeps both figures; the designer's SI figure is refused in a US field; the reply audit reads SI figures; the figure a conversion was given keeps its unit on the row's inputs too, so it backs only that unit (found in review of this change) | `UnitConversionTests` (9) |
| F-009 paused instead of an assumed screen | S2, live | The lead's rule told it to stop when the system type was unknown | The owner's ruling, in the lead's rule 4: go on with labeled assumptions; stop only for a takeoff with no pipe data | `MissingInputPolicyTests` (1) |
| F-010 export check missing from `/usage` | S1 | **Fixed in 0.3.1** (`007ef80`) | Unchanged | 0.3.1's `SectionCheckUsageTests` |
| LIV-R2 spend cap retried five times | known gap | Open | Never sent again; the API's words say when access resumes | `ApiClientTests` (6) |
| LIV-R5 a wait Stop could not end | known gap | Open | The wait is on the job's cancel event | `ApiClientTests` |
| LIV-U2 request ids not kept | known gap | Open | Every request's id and workspace kept on the job and counted in the report | `ApiClientTests` |
| Time on the model counted twice | observation | Open | A check inside a turn is counted once | `ApiClientTests` |

**Decisions the owner took (2026-11-12).** Each was the recommendation in the review:

1. Missing inputs (F-009): go on with stated, labeled assumptions; the one stop is a takeoff with no pipe data at all.
2. A damaged record (F-004): ask, and move it aside on a yes, never deleted.
3. SI figures (F-008): converted through the chat and the tools now; whether the Inputs form takes SI is a later decision.
4. A blank the run needs (area increase, hose, supervisory fill, fill time): stop and name the field.
5. The faint, error, and link text colours change in all five schemes.
6. The content items go to `docs/content-provenance.md`, section 2b-2, for the content team.
7. Stopping a request in flight (an abort of the lead's stream on Stop) was not done. On reflection it would not have shortened the report's measured 18.5 s stop, which waited on a specialist's request, and those are not streamed. The wait to send a refused request again, the case that could hang for 30 s, is now cancellable.

**Limits found while doing it, not fixed.**

- Warm Clay's white text on its terracotta accent is 3.1:1 (2.6:1 on hover), below 4.5:1 for a button label. It is the brand colour: an open item for the owner (`docs/prototype-plan.md`, section 12, item 4a). The contrast test leaves text on the accent out and says so.
- The SI guard catches the figure the designer gave. A figure the model remembers in SI from elsewhere (FM's 8 mm/min beside 0.2 gpm/ft², say) is not caught by it; the trace check and the reply audit, which now read SI units, are the guard there.
- `convert_units` rows are not tied to the project inputs, as `fp_calc` rows are not, and a status block lists them as ones it cannot reconcile after an input change.
- The Windows message box that asks about a damaged record has not been seen on Windows.

**Content proposals** (`docs/content-provenance.md`, 2b-2): `density_area` to require a density and an area greater than 0; a rule that a claim about what a result depends on rests on a what-if run; one ruling on the NAC thin margin against the regimen; the kernels to return the spare ampere-hours and the hydrant deficit; the blind-claim-check skill's reply line to match the QA role's.

**Still open from section 1 below, and not taken up here:** items 7 (whether the Section 21 13 19 export can open with the live checker: the 0.3.0 run's EXP-02 saw the gate block again), 8 (the evaluation's collaboration checks: the 0.3.0 run's REG-C3 and BLK-C1 reproduced the same gap), 9 (the Design Basis table layout), 10 (the pipe-only "passes"), and 11 (the gallons constant; the 0.3.0 run's own arithmetic used 231 in³ and saw the 0.1 gal differences it predicts).

**Not done by anyone:** nothing in 0.3.2 has run on Windows or against the live model. F-006, F-008, and F-009 are live findings; 0.3.2 gives the application's side of each, and only a live rerun can say whether the model now does what the instructions and the tools allow.

---

## 1. Prioritized fix list

Ordered by what I would do first. Items 1 to 6 should land before a 0.3.x build goes to Windows or to a second live run, because the retest would otherwise find them again.

| # | What | Defect | State at HEAD | Owner | Size |
|---|---|---|---|---|---|
| 1 | A trace check that did not finish must not become verdicts. Keep the stop reason, write nothing for a claim that got no verdict line, log it as incomplete with its usage, raise the 4,000-token ceiling, and split large packets | BUG-006 | Open, reproduced | App | M |
| 2 | Hold applicability when the job's NFPA 13 edition is not the edition the calculation's cites carry. Today a 2022 job prints 2025 cites as "follows the project inputs" | BUG-005 | Open, reproduced | Mixed | M |
| 3 | Close the rest of the trace-check guard: a claim the application matched nothing in cannot earn the top tier on the checker's word; units outside the eight the rule knows; unknown units; a specialist's own fact counted as a project input; release statements that never mention low air | BUG-003, N-3 | Partly fixed: 4 of the report's 6 false claims still pass | Mixed | M to L |
| 4 | Run the trip time on the takeoff's own zone total, as the delivery screen already does | BUG-002 | Open, reproduced | App | S |
| 5 | Make the calc-code identity and the content fingerprint ignore line endings, and pin line endings in the repository. On Windows the same kernel has a different identity, and 0.3.0 marks a calculation out of date when the identity differs | N-1 (new) | Open, strong evidence, needs Windows to confirm | App | S |
| 6 | Put the Section 21 13 19 claim check's usage on the record and in the cost report | BUG-010 | Open, reproduced | App | S |
| 7 | Find out why the live Section 21 13 19 check supported 1 claim of 12, and whether that export can be reached at all with the live model | N-2 (new) | Unknown, needs the report's evidence | App, maybe Mixed | S to investigate |
| 8 | Stop the evaluation's collaboration checks counting length as a reason | BUG-007 | Partly fixed: the report's own fixture still passes 3 of 4 checks | App | S to M |
| 9 | Give the Design Basis tables column widths, repeated headers, and fewer columns | BUG-009 | Open, reproduced by rendering | App | M |
| 10 | Stop printing "passes" for the pipe-only timing beside a zone-total "does not pass" | N-4 (new) | Open | Mixed | S |
| 11 | Decide the gallons constant (7.48 against 1728/231) and, if it changes, release it as content | Section 4 | Not a defect; a content decision | Content | L across the pack |
| 12 | Retest only, no code: BUG-001, BUG-004, BUG-008 | | Fixed or gone at HEAD | | |

Suggested grouping into pull requests, one path each, so each can be retested against this baseline on its own:

1. **The check finishes or says it did not** (items 1 and 6, plus decisions and unknown ids as supports).
2. **Guards** (items 3 and 4).
3. **Edition hold** (item 2, application side only; the kernel's 2022 body is a separate content question).
4. **Identity and line endings** (item 5).
5. **Export layout and wording** (items 9 and 10).
6. **Evaluator** (item 8).

Then build an unpublished 0.3.1 installer (the "Windows app" workflow with `publish` off) and run section 5.

---

## 2. HEAD against the tested commit

| | Tested | HEAD |
|---|---|---|
| Commit | `24cebb48` (tag `app-v0.2.0`) | `10fdd37`, equal to `origin/main` |
| App version | 0.2.0 | 0.3.0, not tagged, no installer built |
| Relation | | The tested commit is an ancestor. 12 commits, 112 files, about 8,600 lines added |
| Calc code identity, LF checkout | `8c633ce8c70be1cb` | `d9cb09ea552f6150` |

The report's test ran 2026-11-11 22:11 to 23:13 UTC. Pull request #79 (the hardening milestone, 0.3.0) merged at 18:40 UTC the same day. The tester pinned the release it was given, which was right, but its conclusions describe a build `main` had already moved past.

What moved, and which findings it touches:

| Commit | What it did | Findings affected |
|---|---|---|
| `54c10dd` | Replaced the window layout: a job list, a thread, and a job panel with three tabs. The "Zone details" drawer is gone | BUG-008 no longer exists as written. UX-01, UX-02, and every screenshot-based observation need a fresh look |
| `b34f2db` | Refreshed the FP kernel from its source | Calc identity changed. Every figure should be re-confirmed, though the DH-1 figures are unchanged |
| `89522fe`, `7db9cbd` | Hardening: the size exemption exists once on the recorded row; figures matched with their unit; failed delegations, consults, turns, and checks keep the usage that had finished; the evaluation's collaboration checks rewritten; tiers renamed; coverage and INCOMPLETE DRAFT; skill reads recorded; a second job defined | BUG-001 and BUG-004 fixed. BUG-002, BUG-003, BUG-007 partly fixed. TRUST-06's "no coverage evaluator" is no longer true |
| `c400f19` | Retired the deprecated `low_air` alias from `di_zone.py` | Calc identity changed again |
| `79ce9e5`, `46f9140` | `CLAUDE.md` trimmed; the ownership rules added | Governs how the fixes below are split between owners |

One consequence the hand-back for 0.3.0 states itself: no request has been sent to the live model on 0.3.0, and nothing has been installed on Windows on any version. The report's live evidence is about 0.2.0's prompts and checks. The role files changed in 0.3.0, so the live behaviour it praised (specialists challenging each other, corrections preserved) has to be seen again, not carried forward.

---

## 3. Per-defect analysis

Classes: **product bug** (the code is wrong on a path a designer reaches), **guard-rail gap** (real, shown only with a scripted model that misbehaves on purpose), **harness artifact**, **intended behaviour**.

| ID | Report | Mine | Class | At 0.2.0 | At HEAD |
|---|---|---|---|---|---|
| BUG-001 | High | High | Product bug | Reproduced | **Fixed** |
| BUG-002 | High | Medium | Guard-rail gap | Reproduced | **Open** for the trip time |
| BUG-003 | High | High for the release statements, Medium for units | Guard-rail gap | Reproduced, 6 of 6 | **Open**, 4 of 6 |
| BUG-004 | High | High | Product bug | Reproduced, to the cent | **Fixed** |
| BUG-005 | Medium | **High** | Product bug | Reproduced | **Open** |
| BUG-006 | High | High | Product bug, seen live | Reproduced | **Open** |
| BUG-007 | Medium | Medium | Guard-rail gap in the evaluator | Verified in source | **Open** against the report's fixture |
| BUG-008 | Medium | Medium | Product bug | Reproduced | **Gone**: the layout was replaced |
| BUG-009 | Medium | Medium | Product bug | Same code | **Open**, slightly worse |
| BUG-010 | Medium | Medium | Product bug, seen live | Reproduced | **Open** |

Where I disagree with the report: BUG-002 is rated too high and BUG-005 too low. Reasons are under each.

### BUG-001. The Design Basis said a 505.5 gal zone was exempt

**Supported by the code, at 0.2.0. Fixed at HEAD.**

- At 0.2.0, `workflow.run_tool_plan` called `dry_delivery_screen` without the zone total, so the recorded row carried the kernel's pipe-only flag (475 gal, true). It then corrected a copy in memory with `govern_nfpa_exemption`. The Results tab and the narrative read the copy. `design_basis_docx.key_figures` read the record and printed "zone-total exemption yes".
- Reproduced on the tested tree with the report's inputs (6 in Sch 10, 288.11123868205976 ft, 6% fittings, 2 gal trim, 1500 gpm): the recorded row is exempt, and the exported row reads "NFPA size cap 500 gal; zone-total exemption yes", standing "follows the project inputs".
- At HEAD the plan hands the screen `zone_gal` (`workflow.py:143-149`), the recorded row carries `exemption_volume_gal` 505.5 and the answer no, and every surface prints `workflow.exemption_answer`. The same export reads "size exemption on the zone total of 505.5 gal: no". Held by `test_hardening.SizeExemptionTests` (6 tests).

Nothing to fix. Retest: the report's 475 / 505.5 case and its three boundary cases on a 0.3.x build, and open a 0.2.0 project in 0.3.x to confirm an old pipe-only row reads "not determined" until the zone is run again.

### BUG-002. A rounded takeoff flips the trip-time screen and both rows stay current

**Supported. Guard-rail gap. Open at HEAD. I rate it Medium, not High.**

- Reproduced on both trees with the report's exact figures: takeoff 500.34253038108415 gal gives 30.013701215243366 s and fails; the same call with `v_gal` 500 gives 30.0 s and passes; two rows, both `current`, neither carrying a note.
- Root cause: `coherence._result_matches` ties a passed figure to a recorded result within `max(0.05, 0.2%)`, which is about 1 gal at 500 gal. That tolerance is right for saying where a figure came from and wrong for deciding a pass. 0.3.0 added `coherence.EXACT_FROM_SOURCE` for exactly this, but it lists only `dry_delivery_screen.zone_gal`. `di_trip_to_water.v_gal` and `nitrogen_gate.v_gal` still run on the caller's rounding. The 0.3.0 hand-back says so (later work, item 5a). `CLAUDE.md` already states the rule the code does not yet keep for the trip time.
- Why Medium: the rounding has to carry the time across the limit, so the trip time must sit within a few hundredths of a second of it, and the screen is an optimistic screen, not a delivery calculation. Why it is still near the top of the list: a live model does pass figures rounded, the fix is two lines, and the rule is already written down.

**Fix (App, S).** Add `"di_trip_to_water": ("v_gal",)` and `"nitrogen_gate": ("v_gal",)` to `EXACT_FROM_SOURCE`. `ToolSession._exact_from_record` is already general: the call then runs and is recorded on the takeoff's own figure, a repeat replays one row, and the result says the passed figure was replaced. The gas fill has no threshold; it is included so one zone total gives one recorded fill, not two.

**Smallest test.** Beside `test_a_rounded_zone_total_cannot_cross_the_cap`: the 300.45 ft fixture, `di_trip_to_water` with `v_gal=500`. Expect `passes_screen` false, the same record id as the exact call, and `figure_taken_from_the_record` in the result. Two existing tests pass 281.3 for a takeoff of 281.346 (`test_coherence.py:450`, `:763`); their expectations need re-reading, not weakening.

### BUG-003. A permissive checker labels contradictions and wrong units as supported by a source

**Supported. Guard-rail gap. Partly fixed at HEAD; the more serious half is open.**

I rebuilt the report's seven cases, added three, and ran them with a stand-in checker that says Supported to everything.

| Case | 0.2.0 | HEAD |
|---|---|---|
| False: the valve releases on detection alone | Supported, top tier | **Supported, top tier** |
| False: releases on either detection or the pressure drop | Supported, top tier | **Supported, top tier** |
| True control: detection leg AND pressure drop, not isolated | Supported | Supported |
| 900 gpm cited to a 900 ft fact | Supported | Not supported: "holds 900 only as another quantity" |
| "nine hundred g.p.m." cited to 900 ft | Supported | **Supported, top tier** |
| 600 gpm cited to 600 L/min | Supported | Not supported |
| 99 Ah cited to 99 ft | Supported | **Supported, top tier** |
| Mine: 600 gpm cited to "600 lpm" | Supported | **Supported, top tier** |
| Mine: 450 gal cited to "450 feet of hose" | Supported | Not supported |
| Mine, true control: 900 ft cited to a 900 ft fact | Supported | Supported |

Root causes at HEAD, each separate:

1. **The top tier needs nothing the application matched.** In `checker.check_record` (`checker.py:460-477`) a claim with no figure passes on the checker's verdict alone, and `assurance` (`:633-635`) gives it "Trace-consistent with a row the application identified". The module's own header says meaning is "the checker's judgment alone". That is honest in the docstring and invisible in the tier.
2. **The figure rule knows eight units.** `quantities._CLAIM_UNITS` is gal, gpm, psi, scfm, s, min, ft2, and percent. A figure in amp-hours, volts, amps, feet, or inches is not read as a figure in a claim, so nothing is held. Battery capacity is squarely in the fire-alarm scope.
3. **An unknown unit is treated as no unit.** "600 lpm" is stored as 600 with class `None`, and `quantities.has` lets a classless number back anything.
4. **Words are not figures.** "nine hundred" and "g.p.m." are not read.
5. **The release rule only reads sentences that name low air.** `releasing.release_wording_hits` skips any sentence without it (`releasing.py:215`), so a single-leg or an either-or statement never reaches a rule.
6. **New, N-3: a specialist's own fact is packaged as a project input.** `_cite_for` (`checker.py:276-288`) marks every fact row "PROJECT INPUT", and the QA role is told that means "a value the designer gave". I had a scripted specialist record an ASSUMED fact, then a finding labelled calculated with the same words citing it. It came back Supported, basis `source`, top tier. The echo rule looks only at evidence notes and findings.

Why High for the release half: the releasing statement is the one sentence in the document with a safety rule behind it, and the label a wrong one earns is the strongest the application gives. Why only Medium for the units: the document says in a table that nothing was verified, and the live model in the report's own challenge rejected every one of these.

**Fix (M to L).**

- *App.* Record, per claim, what the application itself held: the figures it matched. A Supported verdict with nothing matched keeps the verdict and gets its own standing, worded so it cannot be read as the first group, for example "Trace-consistent on the checker's reading alone; no figure for the application to hold". This one change covers the two release statements, the spelled-out flow, and the amp-hour case without a wording list. It needs your decision on the label (question 3).
- *App.* In `quantities.py`: give each non-claim unit its own class instead of one `OTHER`, read those units in claims too, give an unrecognized unit word its own class instead of `None`, normalize dotted unit spellings, and treat a number written in words as a figure the application cannot read.
- *App.* In `_cite_for`: only the zone inputs and the five basis fields are "PROJECT INPUT". Any other fact is shown as a recorded fact with who wrote it and its label, counts as author-only when the finding's author wrote it, and goes through the echo rule.
- *Mixed.* For a finding that cites a `releasing_truth_table` row and speaks about what releases, require the row's own expression (`releasing.releasing_logic(...)["expression"]`) in the text, or it stays on the checker's reading alone. Extending the wording detector to single-leg and either-or statements is the other route. The pack lint carries a copy of those rules and `CLAUDE.md` says to change both together, so that part goes to the Grok team before it is written.

**Smallest test.** One table-driven test in `test_hardening.AssuranceTests` with `yes_to_everything`: the ten rows above. No false row may come back Supported with basis `source`; the two true controls must stay there.

### BUG-004. A failed specialist lost the usage of a response that had finished

**Supported, at 0.2.0. Fixed at HEAD.**

- At 0.2.0 `team.delegate` caught a non-cancel exception and re-raised with no event and no usage, and `run_tool_loop` attached none.
- Reproduced on the tested tree with the report's script (one specialist round of 10,000 input and 1,000 output tokens, then a raised error): one `turn` event, 700 input, 380 output, 18,000 cache-read, $0.014. Those are the report's figures exactly.
- At HEAD the same script writes a `delegation` event marked failed with the 10,000 and 1,000, the turn total includes it ($0.074), and the report prints the Failures line that says the total is a floor. Held by `test_hardening.FailureAccountingTests` (7 tests).

Nothing to fix. Still true by nature, and the application says so: the request that failed reports no usage. BUG-010 is the one accounting hole left.

### BUG-005. An edition change is rerun without resolving the edition mismatch

**Supported. Product bug. Open at HEAD. I rate it High, and it is worse than the report describes.**

- Reproduced on both trees: basis changed to NFPA 13 2022, zone run again. The delivery-screen row still cites NFPA 13-2025, its standing in the export is "follows the project inputs", the run has no warning and no flag, and the document shows 2022 in the inputs table and 2025 in the calculation table with nothing between them.
- Root cause, three parts:
  1. No calculation depends on the edition. `coherence.BINDINGS` ties no tool argument to `basis/nfpa_13`, and `workflow.run_tool_plan` never passes an edition. The kernel defaults to 2025.
  2. The "stale" the tester saw was `inputs.changed_since`, which compares the form with the last run. On the record nothing went out of date: zero rows. So the Design Basis gate (`checker.export_reason`) was already open **before** the rerun. The rerun replayed the same rows and only cleared the form's signal.
  3. `design_basis_docx.standing_of` prints "follows the project inputs" for any tracked row.
- The kernel's own position makes this sharper. `formulas._parse_nfpa13_dry_edition` (`formulas.py:537-551`) accepts 2019 and 2025 and says other editions, 2022 by name, are "rejected, not in this gate". The content team has said it does not hold a 2022 body for this rule. The application prints a 2025 cite on a 2022 job anyway, because it never asks.
- Why High: `CLAUDE.md` states that an unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified. For work across many jurisdictions that is an ordinary job, not an edge case. NFPA 13-2025 stays the baseline the pack is written against; the defect is what happens when a job declares an adopted edition that is not the baseline.

**Fix (Mixed, M). The application side does not invent an engineering answer.**

- *App.* A derived check, beside the others in `coherence.py`: for each current calculation, read the edition its own output states (`di_trip_to_water` returns `edition`; the others name it in their cite strings) and compare it with the job's. Where they differ the row carries a hold: "EDITION NOT RECONCILED. This calculation's cites are NFPA 13-2025. The job states NFPA 13-2022. Whether the rule and the section apply in the adopted edition is unresolved."
- *App.* Print the hold in place of "follows the project inputs", count it as a coverage gap so the document opens INCOMPLETE DRAFT, show it on the Results tile and in the lead's status block, and carry it into the Section 21 13 19 flags.
- *Mixed, to agree with the Grok team first:* whether the plan should pass `edition` to the kernel when the job's edition is one the kernel holds (2019). That changes which cite prints, which is engineering content.
- *Content, routed to the FP/FA App Grok Bot:* whether to hold a 2022 body in the gate. Until then the hold is the honest output.

**Smallest test.** Seed 2025 and run: no hold. Change `nfpa_13` to 2022: the hold is on the screen and trip rows before and after a rerun, the export contains it and does not contain "follows the project inputs" on those rows, and coverage is incomplete. Back to 2025: it clears.

### BUG-006. A truncated trace check becomes negative verdicts

**Supported. Product bug, observed live. Open at HEAD and unchanged since the tag: `claim_check.py` has not been touched.**

Reproduced on both trees with a scripted reply of `stop_reason` `max_tokens`, one thinking block, and no text: both findings were written "Not supported" with an empty reason, the event was logged as an ordinary `record_check` with 4,000 output tokens, and `check_is_current` was true.

Three separate causes:

1. **The ceiling.** `claim_check._ask_usage` (`claim_check.py:317-329`) sends `max_tokens=4000`. Every tool-loop request in the application sends 16,000. On Claude Opus 5.5 thinking cannot be turned off and `max_tokens` caps thinking and reply text together, so a 16 to 22 claim packet can spend the whole 4,000 on thinking. That is what the report's observer saw.
2. **No verdict is read as a no.** `_ask_usage` returns the text and the usage and drops `stop_reason`. `checker.check_record` then does `words.get(n, VERDICT_NOT)` (`checker.py:460`) and overwrites each finding's status. `claim_check._from_model` has the same default (`:237`).
3. **Supports the packet cannot see.** `build_record_packet` (`checker.py:311-319`) indexes calculations, evidence, facts, and findings, not decisions, and `Record.record_finding` accepts any id. A finding that cites a decision reads "not on the record" when the row is there. Confirmed: an invented id is accepted without a word.

The consequence the report does not spell out: because the check counts as current, the Design Basis gate opens and the document files those findings under "Needs further evidence or engineering review" with "The trace check did not support it." The check never judged them. That is a false statement in a deliverable, and it is why this is first on the list. The report calls the result "an explicitly unchecked draft"; by the code it was a draft that said it had been checked and failed.

**Fix (App, M).**

- `_ask_usage` returns the stop reason too, and sends 16,000.
- In `check_record`, a claim with no verdict line is not judged: its finding's status is left alone. When any claim is unjudged, or the stop reason is one `claude_client._INCOMPLETE` names, write a `check_incomplete` event with the usage, the stop reason, and how many were judged; leave the last complete check as the latest, the way `check_failed` already does; add the kind to `usage_report.USAGE_KINDS` and `COUNTED_KINDS`. The status line says the check did not finish and that nothing was changed.
- Send large packets in batches (about eight claims) so one cut-off loses only its own claims. The system text is cached, so the extra requests cost little.
- Index decisions in the packet as the team's own statements (author-only, like a finding). Have `record_finding` and `record_decision` say in their result which support ids are on no table, so the model can correct them in the same turn.
- The same treatment in `claim_check._from_model` for the Section export.

**Smallest tests.** A scripted checker that returns `max_tokens` and a thinking block only: statuses unchanged, one `check_incomplete` event with usage, `check_is_current` false, the status line says it did not finish. A reply with verdict lines for the first k claims: k judged, the rest untouched. The request carries `max_tokens` of at least 16,000. A finding citing a decision shows the decision, not "missing".

One decision is yours before this is written (question 2): when the check cannot finish, does the Design Basis wait, or export with those findings under "Stated by a specialist, not checked" and a line at its head.

### BUG-007. The evaluation counts ceremonial exchanges as collaboration

**Supported at 0.2.0 by the source. Rewritten in 0.3.0. The report's own fixture still passes at HEAD.**

- At 0.2.0 the checks were `PASS if consults or crossed` and `PASS if reviews`.
- At HEAD `live_eval.collaboration` excludes replayed calculations, bare agreements, and unanswered questions. But "a reason" and "an answer of substance" are both `len(text) >= 20`. "I agree. I agree. I agree." is 26 characters. And a consult counts as used when the asker records any finding afterwards, related or not.
- Run at HEAD with the report's fixture (an acknowledgement, two unrelated findings, the triple agreement): asked-and-answered met, a position with a reason met, an exchange had an effect met. Only "rests on the other's work" is correctly not observed.

`CLAUDE.md` already has the rule: before adding a check, name what would fool it. Length fools this one.

**Fix (App, S to M).** A reason has to survive having agreement and courtesy phrases removed and repeated sentences collapsed, and has to point at something on the record: a row id, a figure the reviewed finding rests on, or a term from it. A consult is used when the asker's later finding cites the exchange, a row the answerer wrote, or a figure from the answer. This changes the evaluation report only, not the product.

**Smallest test.** In `EvaluationEvidenceTests`: the report's fixture gives no reasoned agreement and no effect; the scripted scenario's real exchange still passes.

### BUG-008. At the minimum width the panel's close control was off screen

**Supported at 0.2.0. Not present at HEAD.**

Served both trees and measured in Chromium at 1020 by 680. At 0.2.0 the document was 1108 px wide and "Close Zone details" sat at x 1066. (The report measured 1039; a different tab was open. Same defect.) At HEAD the document is 1020 px wide on the Inputs, Results, and Team tabs, and on the Team tab at 1020 by 560, with no control past the edge. The drawer the defect was in was removed by `54c10dd`.

Nothing to fix. Retest on Windows at 125%, 150%, and 175% display scale, where font metrics differ, with a long job name.

### BUG-009. The calculation table in the exported draft is hard to read

**Supported. Open at HEAD, and a little worse.**

`design_basis_docx._table` (`:76-83`) adds a table and sets no widths. Section 3 has seven columns (Tool, By, Recorded, Replays, Figures, Standing, Id). I exported the report's C fixture at HEAD and rendered it in LibreOffice: seven equal columns of 0.86 in on a portrait page with 1.25 in margins, the delivery-screen sentence running the full height of a page in a column two words wide, 10 pages for a record with eight calculations and no findings. The 0.3.0 exemption sentence is longer than the one it replaced, so the column is taller. The findings, exchanges, and evidence tables have seven and eight columns and the same problem.

**Fix (App, M).** `_table` takes column widths, turns autofit off, sets the width on every cell (Word ignores a width set only on the column), repeats the header row, and keeps a row on one page. Section 3 becomes Tool, Figures, Standing, Id, with who ran it, when, and the replay count moved into the per-record list that is already printed below it. The same pass over the three other wide tables.

**Smallest test.** Open the written file: every table has autofit off, widths that sum to no more than the text width, and its prose column the widest. Then look at it in Microsoft Word on Windows; LibreOffice is not the reader's program.

### BUG-010. The Section 21 13 19 claim check is missing from the usage ledger

**Supported. Product bug, observed live. Open at HEAD.**

`Desk.start_claim_check` (`desk.py:2764-2783`) calls `claim_check.judge`, which calls `_ask`, which is `_ask_usage(...)[0]`: the usage is thrown away one line after it is read. Nothing is written to the record, and `usage_report.USAGE_KINDS` has no kind for it. Confirmed on both trees: `judge` returns no usage and adds no event.

**Fix (App, S).** `judge` returns the usage and the stop reason. The worker in `start_claim_check` writes a `section_check` event with the usage, the seconds, and the count supported, and a failed one on an exception with whatever usage the exception carries. Add the kind to `USAGE_KINDS`, `COUNTED_KINDS`, `_label`, and the list `live_eval._spent_in_flight` reads.

**Smallest test.** A scripted check with a usage block: one counted `section_check` row with those tokens, and its line in the report text.

### New findings the report did not raise

**N-1. Line endings change the calc-code identity. (App, S. Likely a product bug on Windows at HEAD; needs Windows to confirm.)**

`calc_tools.calc_identity` and `content_fingerprint` hash raw bytes. The report records calc identity `e774ca6f43cdeb0e`. The tested tree as checked out here gives `8c633ce8c70be1cb`. The same files with CRLF line endings give `e774ca6f43cdeb0e` exactly. So the shipped Windows seed has CRLF endings, which fits the report's note that the seed matches the tag "after line-ending normalization", and fits the build: `windows-app.yml` checks out on a Windows runner and the repository has no `.gitattributes`. The content pack is built on Ubuntu, with LF.

At 0.2.0 the identity was only a replay key, so this was harmless. At 0.3.0 a calculation whose identity differs from the installed pack's is out of date (`coherence.analyze`). On a Windows install, the first content update that replaces the bundled seed would then mark every recorded calculation out of date with "the calc code changed after it ran", and hold the Design Basis export until every zone is run again, when not one line of the kernel changed. It also means the fingerprint and identity in an evaluation report from Windows cannot be compared with the ones from Linux for the same commit, which is the comparison those values exist for.

Fix: hash with line endings normalized, and add `.gitattributes` so the Windows build checks out what Linux does (question 9). An LF tree's identity is unchanged by this, so nothing recorded from a source run moves. Test: copy the calc folders to a temporary root with CRLF endings; both hashes equal the LF tree's. Confirm on Windows by comparing About and versions with the Linux value for the same commit.

**N-2. The Section 21 13 19 export may be unreachable with the live model. (To investigate.)**

The report files the Section export as correctly blocked: the live check supported 1 claim of 12, so no file was written and none was inspected. With a stand-in that approves everything, the same 12 claims all pass and the export opens, which is the only way any test here has ever reached it. Each claim's cite is `claim_check._package_source`: the words "PACKAGE ASSERTION", some cite fragments, and a bare list of every number the tool plan returned. The QA role tells the checker that supported means the record states the figures and the condition in the claim. A list of numbers states no condition, so a careful checker refuses, as it did. The trace check's packet is richer: `checker._calc_text` gives each record's outputs by name. Acceptance Test A, step 6, expects this export to open after the claim check.

I cannot see which claim passed or why the others did not; that is in `section-export-assessment.json`, which I do not have. If the cause is the thin cite, the fix is application work: build the Section cites the way the trace check builds its own. If the gate is meant to stay shut until a standard is pulled, the acceptance test and the README should say the Section export is not expected to open, and Test A should stop expecting it.

**N-3. A specialist's own fact counts as a project input.** Under BUG-003, cause 6.

**N-4. A pipe-only "passes" printed beside a zone-total "does not pass". (Mixed, S.)**

In the C fixture's export at HEAD the delivery-screen row reads "Pipe-only t_total 29.0 s against the 30.0 s FM limit: passes", the size exemption on 505.5 gal reads no, and the next row reads that the zone-total screen does not pass. Each is labelled correctly. In a narrow column a reader sees "passes" first. This is the same kind of hazard BUG-001 was, one step milder. Print the pipe-only time without a verdict, or mark it as not the governing screen. The wording of a calculation's result is partly the content owner's, so agree it with them.

**N-5. More than half the spend is cache writes. (A lead, not a defect.)**

From the report's own ledger totals, at its rates: cache writes are $9.76 of $18.43, 53%. A nine-second smoke turn cost $0.37; I would expect most of that to be the first write of the prefix, but the report does not break it down. By the code, each agent context has its own system text and so writes its own cache entry. The 0.3.0 hand-back already lists moving the status block after the chat history so the history caches. Worth measuring before the next live run, since it sets what a job costs.

---

## 4. The gallons constant

**What I found.** The kernel computes pipe volume as `pi/4 * ID^2 / 144 * 7.48` gallons per foot (`calcs/fp/formulas.py:326`). The report states its check as `pi/4 * ID^2 * length_ft * 12 / 231`. Those are different constants: 1728/231 is 7.480519..., and 7.48 is that value rounded to three figures. Every volume in the report matches 7.48, to all ten decimals it prints:

| | With 7.48 | With 1728/231 | The report prints |
|---|---|---|---|
| DH-1 pipe | 276.3460622119 | 276.3652542434 | 276.3460622119 |
| DH-2 pipe | 416.2611626120 | 416.2900716447 | 416.2611626120 |
| C, 300.45 ft plus 5 gal | 500.3425303811 | 500.3769315569 | 500.3425303811 |

So the report's oracle used the application's constant, whatever its text says. Its arithmetic checks are sound for everything except the constant itself, which it could not have caught. `app/tests/test_prototype.py:334` and `:502` build their expected values with 7.48 too, so the repository's own tests share the blind spot.

**Should the application use the exact constant?** The application should not choose: this is the kernel's formula, and the kernel is the Grok team's. As a recommendation to route to them, yes, for four reasons:

1. One US gallon is 231 cubic inches by definition. The exact form has no rounding to defend.
2. 7.48 understates every volume by 69 parts per million. For a "500 gal or less" threshold and for a trip-time screen, understating volume is the direction that favours a pass.
3. The kernel already uses 231 exactly elsewhere: the velocity constant at `formulas.py:2259-2287` is derived from it. The kernel is not consistent with itself.
4. Anyone checking independently will use 231 and will disagree in the fifth figure, and at the printed tenth of a gallon. The report's stated method would have produced 276.4 where the application prints 276.3. That is a discrepancy a reviewer has to chase for no engineering reason.

Against that, the size of it: 0.035 gal at 500 gal, and 0.0014 s on the trip time at 1500 gpm. An assumed 5 gal of trim is more than a hundred times larger. This is a matter of defensibility and of agreeing with an independent check, not of safety. I would not hold any application fix for it.

**What it would do to the 500 gal boundary tests.**

- *A fixture given as a length keeps its answer.* 300.45 ft plus 5 gal goes from 500.343 to 500.377 gal and still fails. The 475 gal fixture becomes 475.033 gal of pipe and 505.535 gal of zone, still not exempt.
- *A fixture back-solved to a target volume under 7.48 moves up by about 0.034 gal.* If the report's 499.99 / 500.00 / 500.01 cases were built the way its 475 gal case clearly was, they become 500.024 / 500.034 / 500.044. The first two flip from pass to fail on both the exemption and the 30 s screen; the third stays a fail. Each length has to be re-derived, about a quarter of an inch shorter on 6 in Sch 10. I have not seen those fixtures, so this is conditional.
- *There is a band 0.035 gal wide, from 499.965 to 500.000 gal as the application now computes it,* in which the application says the zone is at or under the threshold and exact arithmetic says it is over.
- *A test that passes a volume as a number is not affected.*
- *In this repository:* the hardening test's check that the 300.45 ft takeoff lies between 500.0 and 500.5 still holds. DH-1's known answer moves at printed precision: 276.3 and 281.3 gal become 276.4 and 281.4, and its trip time stays 38.1 s. The repository's DH-2 (475.1 and 505.5 gal, 46.7 s) does not move at one decimal. Twenty-three files pin the DH-1 strings, among them both known-answer pages, the README, and the page's tests, and the screenshots would be retaken. (The tester's own DH-2 would go from 435.7 to 435.8 gal.)
- *The calc identity changes,* so on 0.3.0 every recorded calculation goes out of date until its zone is run again. That is the design working.
- *Tests get better.* With the exact constant, an oracle written from the definition agrees with the kernel to floating-point precision, so boundary fixtures can be built without reading the implementation, which is what the test rule in `CLAUDE.md` asks for.

One caution for the content team: the gas-fill formula (`air_fill_scfm`) also has 7.48 in it, and its docstring calls that a vendor basis. Whether that one should move is a separate question from the pipe volume. And the constant is written into `corpus/fp/pipe-volume.md` and the volume-takeoff skill, so it is a pack-wide change with its own release, not a one-line edit.

---

## 5. What still needs testing

The PARTIAL, BLOCKED, and NOT RUN rows of the report's matrix, with what HEAD adds. Nothing in this section has been run by anyone on 0.3.0.

### Native Windows

Never run, on any version, by anyone. The report's PRE-01, PRE-04, FAIL-05, FAIL-06, UX-01, UX-02, and UX-03 all stop here. `docs/acceptance-tests.md` (Tests A and E) and `docs/recovery-protocol.md` (Tests C and D) already hold the steps. What to add to them:

| Area | What to do | Why now |
|---|---|---|
| Install | The installer on a clean machine: the license page holds Next until accepted, the install folder has the exe and both text files, the Start menu entry works, uninstall leaves the data. Note what SmartScreen says; the installer is not signed | PRE-04 |
| First launch | The page opens in the app's own WebView2 window, not a browser tab. Copy About and versions into the table | PRE-01 |
| **Identity** | Compare the content fingerprint and calc identity in About with the values from a Linux checkout of the same commit. Then apply a content update and look at a job run before it: its calculations must not all read out of date | **N-1** |
| Key store | Save the key, relaunch, it is still there in Credential Manager. Check key. A wrong key gives a clean 401 and does not replace the saved one. Clear it | PRE-04, FAIL-03 |
| Upgrade | Install 0.3.x over 0.2.0 on a **copy** of the data. Old jobs open. A zone run under 0.2.0 shows its exemption as "not determined" until it is run again. The record schema stays 4 | PRE-04, BUG-001 |
| Display scale | 100%, 125%, 150%, 175%, each at the 1020 by 680 minimum, on each of the three tabs, with a long job name, in a light scheme | BUG-008 |
| Native dialogs | Save As: cancel, overwrite, a read-only folder, a path too long, a file Word has open, a Documents folder that OneDrive redirects | FAIL-06, UX-02 |
| Microsoft Word | Open both exports in Word itself. Table widths, the head of the document, page count | BUG-009, UX-03 |
| Closing while busy | Close the window during a live turn; kill it from Task Manager during one; start a second copy; sleep and wake; hibernate; turn the network off mid-turn | FAIL-05, Tests C and D |

### Live model on 0.3.x

| What | Matrix rows | Note |
|---|---|---|
| A plain request on DH-1, then the same in other words | LIVE-01 | The report's live evidence is on 0.2.0's role files |
| The second job as the repository defines it: `/sample-di2`, `docs/known-answer-dh2.md` | LIVE-05 | The tester invented its own DH-2 because 0.2.0 had none. Its inputs differ from the repository's. Use the repository's so the result can be compared with a known answer, once you confirm its inputs |
| The trace check on 16 to 22 findings returns verdict text | BUG-006 | After the fix. Keep the reply's stop reason |
| The four planted wrong claims, step 8 of `docs/live-evaluation.md` | TRUST-01, TRUST-02 | The fourth has no rule behind it and tests the checker itself |
| The Section 21 13 19 export: does it open | UX-03, N-2 | Has never opened with the live model |
| Stop a turn while a specialist is working, then resume | FAIL-01 | Passed on 0.2.0; the failure accounting under it changed |
| A real rate limit, an overload, a timeout | FAIL-03 | Not induced by the report. Deliberate flooding is not needed: a low-tier key or a pulled network cable will do |
| The cost report against the provider's own usage page for the same hour | FAIL-02 | The report had no invoice. This is the only check on the ledger as a whole |
| The unattended runner on both jobs | | `python -m fpfa.live_eval` is billed. You run it, not a test and not me |

### Offline, and can be done before either of the above

- Two quick sends of the same message. The composer stays usable while a job runs and jobs queue, so a double Enter is two paid turns. The report did not test it (UX-02). Worth a scripted test to see what happens, then a decision on whether to guard it.
- Python 3.12. The suites ran here on 3.13.18. CI (`tests.yml`) runs 3.12 and installs no Playwright, so the browser tests do not run there.
- The 13 skipped `calcs/fa` tests and the kernel reproduce check were skipped here too, and the 0.3.0 hand-back says they were skipped in every earlier run. They need material that is not in the repository.

### Not test gaps: features that do not exist

Imported documents (TRUST-04, CHANGE-06, the import half of FAIL-06) and a spending cap in the window (FAIL-04). The first is not in the plan of record. The second is a decision already written down: `--max-usd` is a guard between steps, never a limit, and the hand-back tells you to set a hard limit on the key. If you want either, that is a scope change for `docs/prototype-plan.md`, not a retest.

### Engineering validation

None, as before. No standard was opened by the report, by the hardening milestone, or by me.

---

## 6. Where the report is wrong, overstated, or missing something

**Wrong**

1. *Its stated oracle is not the one it used.* Section 4. The text says `12 / 231`; the numbers are 7.48. The claim of independent arithmetic holds for the sums and the time formula and does not hold for the constant.
2. *BUG-005's mechanism.* It says the edition change "initially marked results stale" and the rerun "cleared that signal". The signal was the form compared with the last run. On the record nothing was ever stale, so the Design Basis gate was open before the rerun as well as after.
3. *BUG-006's workaround.* "The Design Basis remains exportable as an explicitly unchecked draft." By the code, the draft said the trace check had run and had not supported those findings. It was mis-checked, not unchecked.

**Overstated**

4. *BUG-002 as High.* The band in which a rounding flips the screen is a few hundredths of a second wide, on a screen that is advisory. Medium. Still worth fixing at once, because it is two lines.
5. *"Usage/cost transparency and bounded behavior: FAIL"* folds together two real accounting defects (BUG-004, BUG-010) and one design decision (no hard cap). The first two are defects. The third is documented behaviour.
6. *UX-04 "PASS".* The report says itself that this means the assessment was completed. That is a note, not a pass.
7. *Its priority list.* Items 1 and 3 ("restore governing-value consistency", "preserve usage across failures") were mostly done in 0.3.0 before the report was written. Not the tester's fault; the list is stale all the same.

**Understated**

8. *BUG-005 as Medium.* It affects any job on an adopted edition other than 2025, and the kernel itself says it does not hold 2022.
9. *The Section export.* Filed as correctly blocked. A deliverable that could not be produced once in the whole campaign is a finding in its own right (N-2).

**Missing**

10. *The line-ending identity* (N-1). The report had both halves, the identity and the note about normalization, and did not put them together.
11. *A specialist's own fact earning the top tier* (N-3). Same family as BUG-003, not among its cases.
12. *The pipe-only "passes"* (N-4), in the very table it inspected for BUG-001.
13. *Where the money goes* (N-5). It reports the total and not that most of it is cache writes.
14. *That 0.3.0 existed.* Nothing in the report tells a reader its target was one version behind `main` on the day it ran.
15. *What effort the live results are tied to.* It says effort was unset. On Opus 5.5 that is medium. The checker running out of room at 4,000 tokens is partly a product of that; at another effort it moves, it does not go away.

**Confirmed, for balance.** The cost arithmetic is right: I recomputed $18.429381 from its four token totals at its rates, and $0.0694958 for the Section check. Its DH-1 and DH-2 figures are the application's figures. BUG-001, 004, and 008 reproduce on the tested tree exactly as written. Its separation of live behaviour from scripted controls is careful throughout, and the seven defects still open at HEAD are all real.

---

## 7. Open questions for you

Decisions that are yours, in the order they block work.

1. **Target and order.** I propose the fixes go on `main` as 0.3.1, items 1 to 6 first, and the Windows and live retests run on that build, not on 0.3.0. The alternative is to retest 0.3.0 now, which costs a live run to re-find seven things already reproduced offline. Which do you want?
2. **An incomplete trace check and the Design Basis.** `CLAUDE.md` says both exports keep a current trace check as their gate, and also that a Design Basis with work missing is never blocked for that. When the check cannot finish: does the export wait, or does it go out with those findings under "Stated by a specialist, not checked" and a line at its head saying the check was incomplete? I lean to the second, with batching to make it rare.
3. **A label for "supported on the checker's reading alone".** The BUG-003 fix needs a standing between the top group and "its author's own cite only". Is a fifth group acceptable, and do you want to word it? No tier may read as verification.
4. **Editions.** Which editions do your jobs declare today: 2019, 2022, 2025? If 2022 is common, do you want the Grok team asked for a 2022 body in the kernel's gate, or is a standing hold on 2022 jobs acceptable for now?
5. **The wording detector.** Today it reads only a sentence that names the supervisory air signal. Extending it to single-leg and either-or statements means changing the pack lint's copy as well. May I write that up as a proposal for the FP/FA App Grok Bot through Choom, with the structural rule (the finding must carry the record's own expression) going ahead on the application side meanwhile?
6. **The gallons constant.** Do you want it raised with the Grok team as a content change? If yes, I would send them section 4 as written.
7. **The Section 21 13 19 gate.** Is "every claim Supported" meant to be reachable by the live checker when every cite is a tool-package assertion? If it is, I will look at the cite packet. If it is not, Test A should stop expecting the export to open.
8. **Evidence.** Five of the report's files would settle things I could only infer: `truncated-checker-proof.json`, `section-export-assessment.json` with the claim-check file, `content-integrity.json` (for the line endings), `OFFLINE-false-claims/result.json`, and the C `.docx`. Can you share them, or should I proceed without?
9. **`.gitattributes`.** Pinning line endings to LF fixes the identity mismatch at its source. You work on Windows: a checkout would then hold LF files, which editors handle but which is a change to your working tree. Acceptable, or would you rather only the hash be made insensitive?
10. **The second job.** `docs/known-answer-dh2.md` still waits for your confirmation of its inputs. Separately, do you want the tester's own DH-2 fixture (435.7 gal, 450 gpm, 50 s) kept as a third known answer?
11. **A double send.** If two quick sends prove to be two paid turns, do you want a guard?
12. **This file.** You asked for it at the repository root. The plan of record is `docs/prototype-plan.md`. Once you have decided the above, should this move under `docs/` and the plan of record be updated, or is it a working note to delete when the work is done?
13. **A new job's starting edition and insurer.** A new job starts with NFPA 13 2025, NFPA 72 2025, and insurer FM (`app/fpfa/inputs.py`, `BASIS_STARTING`, now the one place the app holds them). Since 2026-11-12 the record and every view mark an untouched one as a starting value not confirmed by the designer, instead of recording it as if the designer had stated it; the values themselves were not changed. `CLAUDE.md` notes that an unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified, so 2025 is not a safe thing to imply. The decisions are yours, with the Grok team on the engineering side: (a) which edition and which insurer a new job starts with, or whether the editions and the insurer start blank; (b) whether an emptied field stays blank instead of going back to its starting value. Today a blank insurer cannot reach a run because the form refills it; if it could, `workflow.run_tool_plan` would hand the releasing truth table FM in its place (`or "FM"`), which is a default in place of a blank and would need an owner and content answer first; (c) whether an edition that is only a starting value should put EDITION NOT RECONCILED on the calculations that cite it and make the Design Basis an incomplete draft until it is confirmed. Today it is compared like a stated one and only labelled; (d) whether the zone narrator, which is given the basis as it stands, should be told which values are starting values. Nothing here changes until you decide.

---

## 8. How this was checked

The five statuses, kept apart as `CLAUDE.md` requires.

| Status | What this plan rests on |
|---|---|
| Software hardening | None done. No file but this one was written |
| Offline regression evidence | The probes and suite runs below, on Linux, Python 3.13.18, Node 22.23.4, Chromium through Playwright, LibreOffice |
| Installed Windows evidence | **None** |
| Live-model evidence | **None of mine.** The report's, on 0.2.0, is quoted where used. No request was sent to a model and nothing was billed |
| Engineering validation | **None.** No standard was opened. Section numbers above are the pack's own pins as the kernel prints them, not text I read |

**Probes, each run against the tested tree and HEAD**, with temporary databases and no model:

| Defect | Probe | Scripted agent |
|---|---|---|
| BUG-001, 005 | The tool plan on the report's C fixture, the record row, and the exported Word text; then the edition changed and the zone run again | No |
| BUG-002 | The takeoff, then the trip time on the exact and the rounded volume | No |
| BUG-003, N-3 | Ten findings through the trace check | Yes: a checker that says Supported to everything |
| BUG-004 | A lead that delegates, a specialist that finishes one round and then raises | Yes |
| BUG-006, 010 | A checker reply cut off with no text; the Section check with a usage block | Yes |
| BUG-007 | The report's ceremonial fixture through `live_eval.collaboration` | No model; rows written directly. HEAD only |
| BUG-008 | Both trees served with `--demo --serve`, measured at 1020 by 680 | No |
| BUG-009 | The HEAD export rendered to PDF and read; column widths read from the file | No |
| N-1 | The identity hash recomputed with LF and with CRLF | No |
| N-2 | The Section check's best case | Yes: a checker that says Supported to everything |

**Suites at HEAD, run here:**

| Suite | Tests | Result |
|---|---|---|
| `calcs/fp` | 262 | pass, 1 skipped (the kernel reproduce check) |
| `calcs/fa` | 88 | pass, 13 skipped (the code-quote tests) |
| `app/frontend` | 29 | pass |
| `app` | 511 | 510 pass, 1 error: `test_this_environment_has_a_license_text_for_every_package_the_app_needs`, because `pywebview` would not install in this container (a dependency failed to build). An environment limit, not a regression. Both browser tests ran |

**Not done.** I did not have the report's evidence files or its `tools/` scripts and did not guess at them; each probe was rebuilt from the report's written steps. I did not run 0.2.0's test suite. I did not check the frontend's source for the composer and double-send behaviour beyond the desk's queue. The Windows line-ending finding rests on a hash match and the build workflow, not on a Windows machine.
