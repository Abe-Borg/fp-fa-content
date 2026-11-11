# Hardening milestone: what the reviews found, what changed, and what is still not known

Version 0.3.0. Written 2026-11-11 for the project owner, against the handoff "From implemented team machinery to a trustworthy evaluation build". The target was a trustworthy, observable, bounded FP/FA team workflow that is ready for your live evaluation, with no false claims about what has been proved.

**The short version.** Two independent reviews of version 0.2.0 found that several of its checks could give a reassuring answer when the work underneath was wrong, out of date, incomplete, or not collaborative. Each finding was reproduced or inspected against the code before anything was changed. The ones that were software defects are corrected and held by tests. The ones that are not software's to settle are stated as open, in the application's own output and here.

Five statuses, kept apart throughout:

| Status | Where it stands |
| --- | --- |
| Software hardening | Done for this milestone |
| Offline regression evidence | Done: four suites pass, every agent a script |
| Installed Windows evidence | **None.** Nothing was installed or run on Windows |
| Live-model evidence | **None.** No request was sent to the live model. No paid call was made |
| Engineering validation | **None.** No standard was opened. No qualified engineer has reviewed the basis |

A passing scripted test is a passing scripted test. Nothing below is a claim about what the live model does.

## 1. Revision, and the reconciliation of each finding

**Starting revision:** `760e37ec56976f4cdafebb28417c882f589985ae`, `main` after pull request #77. Both reviews assessed `b34f2db`; #77 (the job list, thread, and job panel layout) came after and neither covered it. This work was done on top of #77. Its own tests and both browser tests pass; its changes were not otherwise reviewed here.

**Final revision:** the head of the pull request that carries this file, on branch `claude/upbeat-euler-olxp85`.

How to read the table. *Reproduced* means a probe written for this work showed the defect on `760e37e` before any change. *Verified in source* means the code was read and the defect is plainly there, without a separate run. *Not reproduced as stated* means part of the report did not match what the repository shows. The evidence column names the test that now holds the behaviour.

| # | Finding | Reported by | At `760e37e` | Now | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | After a flow changes from 600 to 750 gpm, the old finding's text lets a reply that repeats 600 gpm escape the stale-number note | Choom (reproduced by Choom) | **Reproduced.** The audit returned no stale and no unfound figure | **Corrected.** A stale, replaced, or withdrawn finding counts as an out-of-date row. So does the value an input had before it changed. A finding with no basis, an earlier message, an earlier reply, and the record said back by a tool cannot make such a figure current | `test_hardening.StaleFiguresInAReplyTests` (6 tests) |
| 2 | Figure matching is by number, not quantity and unit | Choom, and the 0.2.0 hand-back | **Verified in source** | **Corrected in part.** A figure is matched as a number and a kind of unit, in the reply audit and the trace check. It still does not convert units or judge applicability, and a number with no unit beside it backs anything | `QuantityTests`, `test_a_figure_the_cited_row_holds_as_another_quantity_is_not_supported` |
| 3 | 475 gal of pipe, 505.4 gal zone: the narrative says not exempt, the recorded row and the Design Basis say exempt | FP Factory | **Reproduced.** The tool plan recorded the pipe-only screen and governed a copy in memory | **Corrected.** The plan hands the screen the takeoff's zone total; the recorded row carries that answer and every surface prints that row | `SizeExemptionTests` (5 tests) |
| 3a | The model-facing screen returns an unlabeled pipe-only exemption, and the sprinkler role tells the model to quote it | FP Factory | **Reproduced.** The result said exempt, with nothing marking it pipe-only | **Corrected.** A screen with no zone total gives no answer, or "no" when the pipe alone is over. The role tells the specialist to pass the zone total | `test_a_pipe_only_screen_never_says_the_exemption_is_met` |
| 3b | The same key means pipe-only in the kernel and zone total in the app | FP/FA App | **Verified in source** | **Corrected at the app's edge.** Nothing recorded or shown carries the pipe-only meaning under that key; the kernel's flag is kept under `pipe_only_nfpa_delivery_time_exempt`. The kernel file is unchanged | the same tests |
| 4 | A finding that states the release wrongly, against the releasing rule, earns the source tier with the stand-in checker | QA | **Reproduced.** Tier source, verdict Supported | **Corrected** for that statement: the detector runs on every finding and no verdict stands against it. The general case, a wrong claim with no figure and no known wording, still depends on the checker's judgment, which is untested live. The evaluation now plants one such claim to test it | `AssuranceTests`, `test_a_checker_that_approves_everything_is_caught_by_the_planted_claims` |
| 5 | The source tier's title reads stronger than the check | FP Lead, QA | **Verified** | **Corrected.** Tiers renamed; none reads as verification. The export lists six kinds of assurance and marks the last two NOT PERFORMED | `test_no_tier_is_named_as_verification`, `CoverageTests` |
| 6 | A Design Basis exports with no releasing finding | QA | **Reproduced.** The gate returned ready | **Corrected without blocking.** The export opens with what it does not cover and says INCOMPLETE DRAFT | `CoverageTests` (3 tests) |
| 7 | The collaboration check reports met with no exchange, because a replayed calculation counts as the other's work | FP/FA App | **Verified in source and reproduced in a test.** A repeated calculation replays the first row, which keeps the first caller's name | **Corrected.** Replays are read from the record and never counted. A bare agreement and an unanswered question are not counted either | `EvaluationEvidenceTests` (5 tests), `test_live_eval` |
| 8 | The low-air wording check misses most paraphrases | QA (2 of 11), FA Lead (3 of 5) | **Reproduced** with a set written here: the runner's pattern caught 1 of 11; the pack lint 8 of 16 | **Corrected** for the paraphrases anyone has thought of: 16 of 16 here, none of 17 correct sentences flagged, the pack's prose clean. A paraphrase nobody thought of still passes. The reviewers' own probe sets were not available and were not rerun | `calcs/fp/test_pack_content_lowair.py`, `test_the_two_detectors_agree_sentence_for_sentence` |
| 9 | A live run cannot show which specialist read which skill | FA Skills, FP Skills | **Verified in source** | **Corrected.** Each read is recorded with who, which skill, and a hash of the text. The Team tab, the export, and the runner show it, with whether it came before the findings and whether a recorded cite is one the skill holds | `SkillUseTests` (3 tests) |
| 10 | The guide's second job has no inputs, no expected answer, and no pass criteria | FP/FA App | **Verified** | **Corrected, pending you.** DH-2 is defined with inputs, an expected basis, wrong answers, and ten pass criteria. Its inputs wait for your confirmation | `SecondJobTests`, `docs/known-answer-dh2.md` |
| 11 | The releasing role tells the specialist to object to the 8 s and 2 s times | FP/FA App | **Not reproduced as stated.** The role names no figure. It says to object to a time with no stated basis, which is a general rule | **Left as it is.** The role does not hold the sample's answer | `roles/fa-releasing/ROLE.md` |
| 12 | Three OWNER TO CONFIRM items in the known answer block Test A | FP/FA App, and both hand-backs | **Verified** | **Open, yours.** Test A is marked blocked, not failed. Nothing was chosen for you | `docs/acceptance-tests.md` |
| 13 | The releasing basis is not cited or reviewed | FP Lead, FA Lead, FA Factory, QA, Choomba | **Verified** | **Open by its nature.** The basis page is rewritten to say what is supported, under which arrangement and assumptions, what was inspected, what was only reported, and what is unresolved, with an acceptance gate. The reviewers' cited sections are recorded as leads, not as read | `docs/releasing-basis.md` |
| 14 | "No document was edited to match another" is false | QA | **Verified** | **Corrected** where it stood, with the date, and the basis page says what kind of change it was | `docs/milestone-team-handback.md`, `docs/releasing-basis.md` §5 |
| 15 | The packaged C&E skill's Boolean drops the manual station; it came in with `bc14eae` | FP Skills | **Verified that it is absent. Not reproduced that `bc14eae` introduced it:** the line had no manual station before that commit either | **Corrected** in the packaged copy, in all six places, to match the kernel, the FA skill, and the corpus | `test_the_c_and_e_skill_keeps_the_manual_station_in_the_detection_leg` |
| 16 | Three electric/pneumatic sentences omit "and not isolated" | FA Factory | **Verified** in the role, the C&E skill, and one corpus note | **Corrected** | `test_the_electric_pneumatic_sentence_keeps_the_isolation_qualifier` |
| 17 | The kernel still emits the deprecated `boolean` string and `low_air` row key, which spell the second leg the old way | FP Lead, Choomba | **Verified.** Only `releasing.py` reads them; nothing shown carries them | **Left, with the reason corrected.** The stated reason (older apps) no longer holds. The file has a copy on the team's side, so removing the names here alone would be undone or split the two. It is a decision for you (section 6) | `docs/releasing-basis.md` §6 |
| 18 | "Never a release input" overstates the ruling's "not by itself" | FP Factory | **Cannot be reconciled here.** The ruling is not in this repository | **Stated, not settled.** The basis page says what "low air" means in the app's sentence and under which assumption | `docs/releasing-basis.md` §4 |
| 19 | The wired truth table has no supervisory input, so "fire plus low air must not release" is not asserted | FA Factory | **Verified, and not a defect:** the table has no such input, so there is no row to test | **Left.** The tests hold that a pressure drop alone, detection alone, and an isolated zone never release | `test_releasing_basis.TruthTableLogicTests` |
| 20 | A failed delegation, consult, or check logs no usage, so the display and the budget guard undercount exactly when things fail | Claude Developer SME | **Reproduced.** No event, no usage on the exception. An existing test asserted "the failed attempt wrote no usage row" | **Corrected.** Each writes its event, marked failed, with what had finished. A failed turn does too. A failed request's own usage is unknown and the report says so | `FailureAccountingTests` (7 tests), `test_scenario.test_8` |
| 21 | The guide understates time | Claude Developer SME | **Verified** that the guide gave lower figures | **Corrected** by printing both estimates as modelled, with who made each and from what. Neither is a measurement | `docs/live-evaluation.md` |
| 22 | The unrun list omits the skipped tests, the kernel reproduce check, the Playwright tests, and the held draft | QA | **Verified** | **Corrected.** Listed in the acceptance table and in section 3 below. The Playwright tests were run here | `docs/acceptance-tests.md` |
| 23 | No planted wrong low-air probe | QA | **Verified** | **Corrected.** The runner plants four wrong claims; the guide asks you to plant the same four by hand | `live_eval.step_probe`, guide step 8 |
| 24 | FA calcs are not tracked for staleness | Several | **Verified** | **Stated, not supported.** The bounded workflow does not need them. An untracked calculation now says so everywhere, and is listed as unreconciled when an input changed after it ran | `test_a_calculation_on_a_tool_the_record_does_not_track_says_so` |
| 25 | A kernel change does not stale earlier rows | FP Factory, Choomba | **Verified** | **Corrected.** A calculation made by other calc code is out of date | `test_a_calculation_made_by_other_calc_code_is_out_of_date` |
| 26 | The packaged skills diverge from the live skills; corrections here could be overwritten | FP Skills, Choomba | **Cannot be measured here:** the live skills are not in this repository. The count of 34 of 51 skills that no role names was measured and matches | **Not resolved, by instruction.** Both sides are preserved, the corrections at risk are listed with the test that guards each, and a reconciliation is recommended for your approval | `docs/content-provenance.md` |
| 27 | CI only builds; a content release runs no tests | FP/FA App, Choomba | **Verified** | **Corrected.** A workflow runs the four suites on every pull request, and a content release runs the calc suites first. The workflow itself has not run until this pull request | `.github/workflows/tests.yml` |
| 28 | `releasing_truth_table` takes only the manual station and the insurer; no electric/pneumatic function | FP Lead, FA Lead | **Verified** | **Left.** The reviewers classed it as later work, and an electric/pneumatic implementation needs your approval | section 6 |
| 29 | Canada is stripped from v0 | Claude Developer SME | **Verified** | **Untouched.** Your decision | section 6 |

Two defects were found during this work that no review reported:

- `dry_delivery_screen` refused a takeoff written by nominal size, which is how `zone_trapped_volume` takes it. A specialist that passed the form's segments got an error. It now resolves the nominal sizes through the kernel's own table.
- The reply audit accepted a figure because a record or team tool had returned it that turn, including `set_input`'s "was 600 gpm". Those results no longer make an old figure current.

## 2. The plan, and what was done, by outcome

The approach in each case was the same: find the place where one fact was held twice, or where a check asked a question something cheap could answer, and remove the second copy or ask a harder question. No architecture changed. The Messages loop, one model, the record, and the window are as they were.

### 1. The record and the answer agree with the actual project

- **A figure in a reply is ranked by where it could have come from.** Current calculations and inputs make it current. A row the record knows is out of date makes it out of date, whatever the team still says. You see a note under the reply when the lead quotes an old number.
- **The size exemption exists once.** The recorded calculation is what the thread, the Results tile, and both documents print. With trim or fittings missing there is no answer, not a yes. When the zone total includes an assumed trim, a yes says it holds only while the measured values keep the total under the cap.
- **The limits of change propagation are stated.** The eight tools of the zone workflow are reconciled automatically. Any other calculation says, in its result and in the export, that it is not tied to the inputs. A calculation made by a different version of the calc code is out of date until run again.
- Nothing invents a value or makes an engineering decision to clear a stale marker.

### 2. Assurance labels say what was checked

- The tiers are renamed so none reads as verification, and each note says the check is a second pass by the same AI model.
- The export lists six kinds of assurance and marks verification against the primary standard and qualified engineering review as not performed, on every document.
- Three rules stand whatever the checker says: figures with their units, the releasing wording, and a note that only repeats its claim. When a rule overrules the checker, the record keeps that it did.
- A draft with work missing is still exported and opens by saying so.

### 3. The releasing basis, without manufactured certainty

- `docs/releasing-basis.md` is rewritten. It separates what a file here says, what a reviewer reported, and what was read in a standard (nothing). It names the arrangement the example covers and the assumption the rule rests on, and ends with an acceptance gate.
- The packaged C&E skill, the releasing role, and one corpus note were aligned to the basis the pack already states. The kernel file was not touched.
- The earlier hand-back's inaccurate sentence is corrected.

### 4. An evaluation that can fail for the right reasons

- Every check was rewritten against the thing that would fool it. A replayed calculation is not collaboration. A bare agreement is not a position. A row marked out of date is not reconciled. An export with work missing is reported incomplete.
- A probe step plants four wrong claims. Three test the application's rules. The fourth has no rule behind it and tests the checker itself. With a checker that approves everything, the scripted run reports that check NOT MET.
- A second job is defined, with a request in other words.
- Scenarios waiting on you are reported as blocked.

### 5. Content across future updates

- Skill reads are recorded and shown.
- A content fingerprint identifies exactly what a result was produced from.
- `docs/content-provenance.md` lists the corrections a sync must not lose and recommends a reconciliation. Neither copy was declared the master.
- The suites now run on every pull request and before a content release.

### 6. Failures and costs are visible

- A failed delegation, consult, turn, or check keeps the usage that had finished and is marked failed. Retries are counted.
- The usage report says a failed request reports no usage and that the total is then a floor.
- `/status` and the Team tab name who was cut off, what each had recorded, that it is partial, and what asking again repeats.
- The spend cap is described as a guard everywhere, never as a limit.

## 3. Evidence ledger

Everything here was run in this session, on Linux, in a cloud container. Nothing is a count someone else reported.

**Environment.** Linux, Python 3.13.18 (the repository's suites are usually run on 3.12; they were not run on 3.12 here), Node 22.23.4, Chromium through Playwright. No Windows machine. No API key. No network call to a model.

**Baseline, before any change, at `760e37e`:** `calcs/fp` 259 tests, 1 skipped. `calcs/fa` 88 tests, 13 skipped. `app` 465 tests, all passing.

**Final, at the head of the pull request:**

| Suite | Tests | Result | Skipped |
| --- | --- | --- | --- |
| `calcs/fp` | 261 | pass | 1: the kernel reproduce check, which needs the kernel source folder |
| `calcs/fa` | 88 | pass | 13: code-quote tests, because no code text is in the repository |
| `app` | 511 | pass | none. Both browser tests ran, in Chromium on Linux |
| `app/frontend` | 29 | pass | none |

**On GitHub.** The new test workflow ran on the pull request's first commit, on Python 3.12.16, and passed. Its app step ran the 508 tests that commit held, with 2 skipped: the two browser tests, because the runner has no Playwright. So the suites have now run on Python 3.12, there. The browser tests have run only in this session.

The page was rebuilt (`npm run build`) and the build committed. The README's screenshots were regenerated from the scripted scenario.

**Probes written for this work**, run before and after: the six reproductions in the table above (findings 1, 3, 3a, 4, 6, 20) and the wording set for finding 8. Before: all six defects present. After: all six gone.

**Meaningful failures along the way, and what they were.**

- After the first round of changes 14 of 465 app tests failed. All 14 were expectations that had encoded the old behaviour, including one that asserted a failed attempt writes no usage row. Each was read and updated; none was a regression.
- The new wording detector at first flagged 8 legitimate sentences in the pack and the docs. It was tuned until both were clean and all 16 wrong paraphrases were still caught.
- The detector flagged four sentences in this milestone's own documents that described the wrong wording. They were reworded. One sentence in the guide is the claim you are asked to plant, and is allowed by name in the test.
- The scripted run's coverage check reports NOT MET. That is correct and is left: the scripted team never states the size exemption, the demand, or the gas fill.

**Scripted, not live.** Every test in which an agent takes part plays a script: `test_scenario.py`, `test_live_eval.py`, `test_team*.py`, and the agent parts of `test_hardening.py`. The checker in those tests is a stand-in. They show what the application does when a model makes those moves. They show nothing about whether a model will.

**Not run, by anyone, on this version:**

1. Any request to the live model. So: whether the lead plans and delegates unprompted, whether the specialists ask, review, and revise, whether they read skills and follow them, what the checker does with a wrong claim, and what a request costs and how long it takes.
2. Anything on Windows: the installer, launch, WebView2, Credential Manager, a migration from an older install, sleep, a forced kill of the packaged app.
3. The two browser tests anywhere but this session. The GitHub runner skips them.
4. The 13 skipped `calcs/fa` tests and the kernel reproduce check.
5. The held electric/pneumatic draft under `calcs/fp/draft/`.
6. Any comparison with the content team's live skills.
7. Any reading of NFPA 13, NFPA 72, FM DS 5-32, or a manufacturer's document.

### After the pull request was opened: an automated review

An automated code review of the first commit reported three defects in code this milestone added. Each was reproduced before it was changed, and each is corrected with a test.

| Reported | Reproduced | Now | Evidence |
| --- | --- | --- | --- |
| An untracked calculation run again after an input changed stays listed as unreconciled, because the comparison used when it was first recorded | Yes. A rerun replays the row and left the note standing; a rerun with other arguments left the old row as a gap for good | The comparison uses when the calculation last ran, so a rerun clears it. An unreconciled row nothing current rests on is history: still marked where it is listed, no longer a gap | `test_running_an_untracked_calculation_again_reconciles_it` |
| A handoff one specialist left for another, never delivered, does not stop the Design Basis from calling itself covered | Yes | A handoff waiting for a specialist is a gap. A note addressed to the lead is not: nothing delivers one, so it would never clear | `test_a_handoff_no_specialist_has_picked_up_is_a_gap` |
| A zone total rounded by the caller can cross the 500 gal cap: a 500.3 gal takeoff passed as 500 was matched to the takeoff within tolerance and judged exempt | Yes. Exempt, marked current, no warning | The screen runs on the matched takeoff's own figure, the record holds that figure, and the result says the passed one was replaced | `test_a_rounded_zone_total_cannot_cross_the_cap` |

The third has a sibling this change did not touch. `di_trip_to_water` and `nitrogen_gate` also take the zone total as passed, within the same tolerance, as they did before this milestone. A rounded volume there moves a time or a flow slightly and could in principle move a result across the screen limit. It is listed under later work.

## 4. A short guide for you

`docs/live-evaluation.md` is the guide, written to be used without knowing how the application is built. In brief:

1. **Start** with `/sample-di`. Copy the content fingerprint from About and versions.
2. **Ask in ordinary words.** The guide has one request to send as written, and asks you to repeat it in your own words later.
3. **Look at the Team tab,** not only the reply: a plan, both specialists, a real question between them, a position taken with a reason, which methods they read, and what a design basis would still be missing.
4. **Change a fact** in chat, then ask a follow-up that does not mention the old number. If the reply uses the old number, the application should say so under it.
5. **Break it.** Stop a turn part-way; turn the network off mid-turn. The application should say who was cut off, what was kept, that it is partial, and what asking again repeats.
6. **Plant the four wrong claims** in step 8 and run the trace check. The fourth tells you whether the checker can be trusted.
7. **Export** and read the top of the document first.
8. **Run the second job** with `/sample-di2`. The right answer is that the exemption does not apply.

**Warning signs:** a reply with figures and no specialist on the Team tab; a reply that reads complete while the Team tab lists what is missing; an old number in a reply with no note under it; a wrong claim that comes back trace-consistent; a figure from the first job in the second.

**Known limits:** the trace check is the same model twice; the wording detector knows only the wordings someone thought of; figure matching does not convert units; only the eight zone tools are reconciled automatically; the truth table is electric/electric only; a long turn has no progress bar, only the working line.

## 5. Engineering and content status

**The basis used.** The content pack's own reviewed notes and the calc kernel. NFPA 13-2025 is the delta baseline throughout, with NFPA 13-2022 enforced under an unamended 2024 I-Code adoption until the adoption is verified. Section numbers in the application's output are the pack's paraphrased pins.

**Sources actually inspected.** Files in this repository only: the corpus notes, the specs, the skills, the roles, the kernel, and its tests. They are listed in `docs/releasing-basis.md`, section 3a.

**Sources not inspected.** Every standard, data sheet, and manufacturer document. The sections the reviewers cited (NFPA 13-2025 §8.3.2.1(3) and §8.2.6.3; NFPA 72-2025 §17.19.2.2.2(A) and §23.11.6), the team's ruling, and its held excerpts are recorded as leads. None was read here, and none is presented as read.

**Unresolved applicability questions.**

1. The section number of the double-interlock definition in the adopted edition.
2. Whether the elected valve provides one pressure switch or two. The rule assumes two.
3. Whether the size exemption's 500 gal is judged on pipe plus fittings plus trim. The application follows the kernel's note and the team's reported ruling that it is the zone total, which is the conservative reading. Nobody here read the section.
4. Which delivery path applies to a zone over the threshold. No tool elects one.
5. How the panel treats a manual release zone.
6. "Never a release input" against the ruling's reported "not by itself".

**Qualified review.** None recorded. The acceptance gate is in `docs/releasing-basis.md`, section 8.

**Content provenance.** Content fingerprint `784fb6c7ccfcb0bb`, calc code `fb2dabb140405a17`, for this tree as a source checkout. About and versions prints both on any install; a built pack strips some paths and has its own fingerprint. The packaged content was changed in the ways listed in `docs/content-provenance.md`, section 2. Its relation to the team's live content is unmeasured from here.

## 6. Your decisions, and later work

### What stands between this milestone and acceptance

| Decision | Why it is yours | Recommendation |
| --- | --- | --- |
| Run the live evaluation, and name a budget | It spends your money on your key, on your machine | Do the pass by hand first, on a separate data directory. Then the unattended runner on both jobs. Set a hard limit on the key if the amount matters; the runner's cap is a guard |
| Confirm or edit `docs/known-answer-dh1.md` (three items) and `docs/known-answer-dh2.md` (its inputs) | They are the yardsticks | Confirm the DH-2 inputs as they are unless one is unrepresentative; they were chosen to sit on the exemption boundary |
| Which copy of the skills is authoritative | Governance of the team's content | The team's live content as the source, reconciled in a controlled way after the live evaluation, with the content frozen at one fingerprint until then (`docs/content-provenance.md`, section 4) |
| A qualified engineer's review of the releasing basis, and access to the standards | Only a qualified person can give it | Hand the reviewer `docs/releasing-basis.md`. Sections 2, 4, and 8 are written for that reader |
| Install and migration on your Windows machine | Your machine and your data | Follow the guide's migration steps, which work on a copy and never open your real data |

None of these blocked the software work, and none was decided on your behalf.

### Later work, not started

Each is a real improvement. None is needed for the live evaluation to produce reliable evidence.

1. **Retire the kernel's deprecated names** in `di_zone.py`, here and on the team's side together.
2. **An electric/pneumatic truth table**, and passing the trim family and pressures into the releasing calculation. Needs your approval first.
3. **Track the fire-alarm calculations** for staleness, by typing their inputs.
4. **Re-run stale calculations on request** instead of only flagging them.
5. **Unit conversion and same-quantity matching** in the figure rules.
5a. **Run the trip time and the gas fill on the takeoff's own zone total** when a caller passes it rounded, as the delivery screen now does. Today they use the figure as passed, within the match's tolerance.
5b. **A way to close a handoff addressed to the lead.** Nothing marks one delivered, so it stays pending on the record. It is not counted as a coverage gap for that reason.
6. **Call the 500 gal figure a threshold, not a cap,** in every string. The kernel already says it is a threshold. It was left to keep this change small.
7. **Owners for the 34 skills no role names.**
8. **The Claude Developer SME's items:** move the status block after the chat history so the history caches; do not retry a monthly spend-cap refusal; a model per role; cap the `anthropic` package version; move data to `%LOCALAPPDATA%`; sign the installer.
9. **Division 28 exports.**
10. **A progress indication** for a long turn.
11. **Canada.**

## 7. What is in 0.3.0

New modules: `quantities.py`, `content_use.py`. New tests: `test_hardening.py` (44 tests). Changed: `reply_audit.py`, `checker.py`, `coherence.py`, `calc_tools.py`, `workflow.py`, `team.py`, `everyday.py`, `claude_client.py`, `usage_report.py`, `status.py`, `team_panel.py`, `design_basis_docx.py`, `results_panel.py`, `spec_docx.py`, `releasing.py`, `live_eval.py`, `record.py`, `desk.py`, `about.py`, `sample_data.py`, and the Team tab of the page. Content: one skill, four roles, one corpus note, the pack lint. New documents: this one, `known-answer-dh2.md`, `content-provenance.md`. Rewritten: `releasing-basis.md`, `live-evaluation.md`. New workflow: `tests.yml`.

The record's schema is unchanged at 4. An existing database opens without conversion. A zone run made by an older version keeps its pipe-only screen record, which now prints as not determined until the zone is run again. A content pack built from this tree asks for app 0.3.0 or newer.
