# App/content hand-back for the content team: interfaces, versioning, risks, and the content changes app milestones made

Written 2026-11-12 for the Grok team, by way of the FP/FA App Grok Bot, with Choom coordinating and the owner (Abe) deciding. It is a read-only review of `2f87462`: `main` at the merge of pull request #84, app 0.3.2, and the `app-v0.3.2` tag. No application code, engineering content, or calculation was changed to write it. This page is under `docs/`, which is not part of the content pack, so adding it does not move the content fingerprint.

It answers four questions. What does the application need from a content pack, and how does it load and version one? What app-side defects and compatibility risks are there? Which content and engineering changes did the app milestones make, so the team can review them? Which issues are mixed, and so need both owners?

**How it was produced.** The repository history was read commit by commit. Behaviour was reproduced with small probes: a tool session with no record (which writes nothing), and a desk on a scratch data directory. Parts of sections 3 and 4 came from two read-only sweeps of the code, and the claims this page relies on were spot-checked against the code. Anything not reproduced is marked *inferred*. Nothing here is engineering validation, a check against a standard, or code compliance. The releasing basis stays unresolved (`docs/releasing-basis.md`).

## 1. The snapshot to review against

Both hashes come from the application's own `calc_tools.calc_identity` and `calc_tools.content_fingerprint`, run on line-feed checkouts. They identify content; they do not show it is correct.

| Point | Commit | Calc code | Content fingerprint |
|---|---|---|---|
| **The tree this page reviews, 0.3.2** | `2f87462` | `d9cb09ea552f6150` | `f5f7a87e6d4fa718` |
| 0.3.1 | `3ae0758` | `d9cb09ea552f6150` | `405014962b492f2e` |
| The tree the 0.3.0 acceptance run tested | `04196bd` | `d9cb09ea552f6150` | `fb8d842e6c6d3ca5` |
| 0.3.0, as recorded in `docs/milestone-hardening-handback.md` | `89522fe` | `fb2dabb140405a17` | `784fb6c7ccfcb0bb` |
| 0.2.0, and `content-v0.5.0`, the latest published pack | `bc447f7`, `24cebb4` | `8c633ce8c70be1cb` | `56d052d97de67072` |

- **The freeze is not holding.** The fingerprint has moved three times since the 0.3.0 hand-back recommended freezing it: once from the pack's own pull request #80, and twice from app milestones editing role files.
- **No published pack has any post-0.2.0 correction.** No content pack has been published since `content-v0.5.0`, and its content is identical to 0.2.0's.

## 2. Manifest: content and engineering changes made in app milestones

All of these are preserved; none was reverted. "Guard" is the test that fails if the change is lost. A *text guard* is a test that reads the file itself; a test of behaviour alone does not notice a lost sentence.

### 2a. Content-pack files changed by app milestones

| Milestone | Commit | File | Change | Reason | Guard |
|---|---|---|---|---|---|
| 0.2.0, PR #75 | `bc14eae` | 12 skills¹ | The second leg of the double-interlock release was written as low air in these files and now reads P, the pressure drop from sprinkler operation, with low air named as supervisory only. The trim-election skill gains a vocabulary note on what vendor sheets call the P contact. | Read literally, the old text put the supervisory point where P belongs. The kernel's `boolean_p` and the reviewed corpus and specs carry P. Labels only; no figure changed. | The pack lint (`calcs/fp/test_pack_content_lowair.py`) scans every sentence; plus `test_the_releasing_skills_name_p_as_the_second_leg` |
| | `bc14eae` | `roles/fa-releasing/ROLE.md`, `roles/fp-sprinkler/ROLE.md` | State the P rule | Same | The scan |
| | `bc14eae` | `calcs/fp/test_pack_content_lowair.py`, `calcs/README.md` | The scan extended to skills, roles, and modes | It is the guard | — |
| | `3f6e07b` | `roles/lead/ROLE.md` (new, 76 lines) | The lead's role: plan, `set_input`, delegate, reconcile, `request_check`, answer | Team milestone | A phrase test (`test_the_lead_role_is_content_and_says_how_the_team_is_run`); the `# Team lead` heading is used by the scripted test harnesses |
| | `3f6e07b` | `roles/fp-sprinkler/ROLE.md`, `roles/fa-releasing/ROLE.md` | New `## Working with the team` sections. They split ownership (the sprinkler specialist owns trim, pressures, and gallons; the releasing specialist owns detection and releasing). Detection and release times are inputs the releasing specialist confirms. "Do not assume electric/electric." An unsupported time is ASSUMED | Team milestone | Heading and keywords only (`test_list_specialists_says_what_each_owns_needs_and_reviews`) |
| | `3f6e07b` | `roles/qa-specialist/ROLE.md` | The "Kinds of cite on a project record" block, and the rule that a figure must be in the cite | Trace check | The heading only (`app/tests/test_checker.py:356`) |
| | `3f6e07b` | `roles/README.md` | How the application uses the roles | — | None |
| 0.3.0, PR #79 | `89522fe` | `skills/preaction-releasing-c-and-e-soo/SKILL.md` | The Boolean becomes `(VEWFD_prealarm OR manual_release_station) AND P` in all six places. A new paragraph: the manual station stands in for detection and still needs P; the footnote-9 Manual Release bypass is an election. The electric/pneumatic sentence gains "while the release disconnect is not operated" | The pack copy left out the manual station while the kernel, the FA skill, and the corpus carry it. The reviewers reported the live skill carries it too | `test_the_c_and_e_skill_keeps_the_manual_station_in_the_detection_leg`, `test_the_electric_pneumatic_sentence_keeps_the_isolation_qualifier` |
| | `89522fe` | `corpus/fa/di-releasing.md`, `roles/fa-releasing/ROLE.md` | The isolation qualifier on the electric/pneumatic sentence | The kernel's note and the FA skill carry it | The isolation test |
| | `89522fe` | `roles/fp-sprinkler/ROLE.md` | Pass `zone_gal` to the delivery screen; never state the exemption from a pipe-only screen; `fp_calc` results are not tied to the inputs | The role told the specialist to quote the pipe-only flag | `test_the_sprinkler_role_tells_the_specialist_to_pass_the_zone_total` |
| | `89522fe` | `roles/fa-releasing/ROLE.md` | `fa_calc` and `lfl_setpoints` results are not tied to the inputs | The limits of reconciliation | None |
| | `89522fe` | `roles/lead/ROLE.md` | Step 9, "Not yet covered"; what a failed specialist leaves; calculations the application cannot reconcile | A partial basis was presented as complete | `test_the_lead_is_told_what_is_not_covered_and_the_role_says_what_to_do_about_it` |
| | `89522fe` | `roles/qa-specialist/ROLE.md` | A figure must be in the cite "as the same kind of quantity" | The application now matches number and unit | None |
| | `89522fe` | `calcs/fp/test_pack_content_lowair.py` | Rules widened, two tests added | A reviewer's probe showed it missed paraphrases | It is the guard |
| 0.3.1, PR #83 | `e3ffb6c` | `roles/qa-specialist/ROLE.md` | Two cite marks: RECORDED FACT and DECISION | Facts were packaged as PROJECT INPUT | `test_the_checker_is_told_what_the_two_new_marks_mean` |
| 0.3.2, PR #84 | `6021015` | `roles/lead/ROLE.md` (step 3 and the math rule), `roles/fp-sprinkler/ROLE.md`, `roles/fa-releasing/ROLE.md` | A figure in other units goes in with its unit; a change of unit comes only from `convert_units` | F-008: SI figures were run as US ones | Behaviour only (`UnitConversionTests`). **The sentences themselves have no text guard** |
| | `9b8a7ad` | `roles/qa-specialist/ROLE.md` | The verdict line ends `(<reason>)` | F-007: the checker's reasons were thrown away | `docs/content-provenance.md` names `CheckerReasonTests`, but that class never reads the role. **No text guard** |
| | `71f5c5e` | `roles/lead/ROLE.md` (step 4) | The owner's ruling of 2026-11-12: proceed on stated, labelled assumptions, including "a density and a design area", the hazard, the hose, the trim, the fittings, and the times. Stop only when there is no pipe data at all | F-009: the lead paused instead of screening | `MissingInputPolicyTests` |

¹ The 12 skills: `dry-preaction-water-delivery-screen`, `fa-asd-vewfd-data-hall-sampling-layout`, `fa-double-interlock-releasing-cause-and-effect`, `fa-fire-pump-and-preaction-supervisory-points`, `fa-hvac-door-and-lock-interfaces`, `fa-integrated-systems-test-matrix`, `fa-pathway-survivability-election`, `fa-supervising-station-signal-schedule`, `fa-two-level-detection-stagger-and-fm-mapping`, `nitrogen-inerting-and-c-factor-gate`, `preaction-el-el-trim-election`, `preaction-releasing-c-and-e-soo`.

What else changed, or did not:

- **An earlier change.** `6472127` (2026-11-05) edited one sentence of the `specs/README.md` folder guide: specs load in full.
- **Kernels.** No app milestone changed a kernel file.
- **0.3.x scope.** No 0.3.x commit changed a skill, corpus, spec, or calculation body other than the hardening rows above.
- **Pack publications in the same window that were not app milestones**, listed for reconciliation only: pull requests #72, #73, #74, #78, and #80 (`c400f19`, which retired `di_zone`'s `low_air` alias and restripped its docstrings).

### 2b. App code that carries engineering substance, changed in these milestones

These files are not in the pack, but each encodes an engineering decision the team should review.

| Commit | Where | What it decides |
|---|---|---|
| `bc14eae` | `app/fpfa/releasing.py`, both exports, the form label | The one reader of the truth table. It still accepts the retired `low_air` names when it opens an older run. The export column reads "P (second leg)"; the form label reads "Low-air supervisory psi" |
| `bc14eae` | `app/tests/test_releasing_basis.py` | The truth table asserted row by row. Its oracle, `docs/releasing-basis.md`, is itself still unresolved |
| `89522fe` | `calc_tools._govern_delivery_exemption`, `workflow.govern_nfpa_exemption` | The application overwrites the kernel's `nfpa_delivery_time_exempt` with its own `zone_gal <= cap` comparison. A pipe-only screen now gives null. An assumed trim qualifies a yes. The helper first came in the owner's commit `01ba1c8` |
| `89522fe` | `app/fpfa/checker.py` | A finding that breaks the releasing rule is not supported, whatever the checker says |
| `89522fe` | `sample_data.EXAMPLE_DI_2`, `docs/known-answer-dh2.md` | The DH-2 inputs were chosen by the coding agent and are still marked OWNER TO CONFIRM |
| `3949c43` | `coherence.EXACT_FROM_SOURCE` | The trip time and the gas fill run on the recorded takeoff figure (500.3425 gal, not a rounded 500) |
| `5ab297e` | `coherence.edition_gaps` | EDITION NOT RECONCILED where a calculation's cited edition differs from the job's |
| `cb47859` | `calc_tools._identity_bytes` | The identity hashes set CRLF line endings aside |
| `6021015` | `inputs.POSITIVE`, `inputs.NOT_BLANK` | A zone run is refused when the fill flow, density, base area, supervisory psig, or fill minutes is 0 or less. The area increase and the hose may be 0 but not blank |
| `6021015` | `app/fpfa/units.py` | Conversion by the definitions only. It refuses gauge to absolute, cubic feet (while the 7.48 gallons constant is open), and the K-factor |
| `71f5c5e` | `app/fpfa/results_panel.py` | The delivery tile prints `t_fill_s` and `margin_s` beside the verdict |

## 3. App/content interfaces: the contract a pack must keep

### Layout and acceptance

- **The load-time check.** It is only that `skills/` and `calcs/fp/formulas.py` exist (`app/fpfa/paths.py:55-60`).
- **Expected at runtime.** A missing item fails or degrades then, not at load:
  - `calcs/fp/di_zone.py` and `pipe_ids.py`, beside `formulas.py` (`di_zone` loads its siblings by path)
  - the roles `everyday`, `lead`, and `qa-specialist`
  - the modes `mixed` and `synthesis`
  - `calcs/fa/lib/lfl.py` and every module in `fa_calc.FA_OPS`
  - the skill `ess-isolation-venting-and-duration` with its `starter` block
- **Zip rules.** A pack zip may hold only the six top folders plus `pack.json`, laid out flat. Any other top-level folder rejects the whole pack, as does a path part named foam, clean-agent, canada, catalog, or `_sources` (`content_pack._FORBIDDEN`).

### Markdown contracts

- **Frontmatter.** The file must start with `---`, and only `name` and `description` are read. The `description` must be a plain value or `>`, `>-`, or `|`. A `|-` or `>+` comes back as the literal text "|-" (`app/fpfa/skills_loader.py:161-173`). This description is the index text every model sees.
- **`## Working with the team`.** `app/fpfa/team.py:67` and `:276-285` slice this heading out of each specialist's role. Where it is missing, the notes are silently empty; `spec-draft` already has none.
- **The QA verdict line.** The checker's system text is the QA role alone, not the `blind-claim-check` skill (`claim_check.checker_system`). The role's line format is what the application parses at runtime (`claim_check._VERDICT_LINE`). The QA role is also the only place the application's cite marks are explained.
- **Agents identified by text.** The scripted test harnesses identify agents by the headings `# Team lead`, `# Sprinkler specialist`, `# Releasing specialist`, and `# Draft narrative`, and by the QA sentence "Judge each numbered claim from the cites file alone" (`app/tests/team_scenario.py:51-52`). Renaming any of them breaks most of the team tests.

### Hard-coded identifiers

- The role slugs `everyday`, `lead`, `qa-specialist`, `spec-draft`, `fp-sprinkler`, and `fa-releasing`. Any other folder under `roles/` becomes a specialist the lead can delegate to.
- The mode slugs, and seven DI skill slugs (`workflow.py:26-34`; a missing one gives a warning only).
- The BESS skill and its starter-block keys (a hard failure).
- `21 13 19` is the application's own constant (`spec_docx.DRAFT_SECTION`).

### The calculation interface

- **Private kernel names the application calls:** `di._segments`, `formulas._require_non_negative`, and `formulas.DI_LIMITS_S`. The keys of `DI_LIMITS_S` must equal `inputs.BASES`, and the keys of `formulas._HOSE_DUR` must equal `inputs.HAZARDS`.
- **Kernel parameters the application never passes:**
  - `system_type` to `di_trip_to_water` (see section 5, item 3)
  - `declared_interlock` and `limit_s` to `dry_delivery_screen`
  - an `edition` to either, deliberately (CLAUDE.md)
- **Output keys the application reads:**
  - `zone_gal`, `trim_assumed`, `flags`, and the flag prefix `"ASSUMED fittings"`
  - `nfpa_size_cap_gal` and `nfpa_delivery_time_exempt`. The kernel calls `nfpa_size_cap_gal` a legacy alias of `nfpa_size_threshold_gal`, which the application never reads.
  - `t_total_s`, `t_fill_s`, `margin_s`, `limit_s`, and `limit_basis` (with `"explicit"` treated specially)
  - `family == "El/El"`
  - `boolean_p`, and truth-table rows carrying `p_second_leg`
- **String formats:**
  - The edition hold scans for `NFPA\s*13[-\s](\d{4})` (`coherence.py`), so a format such as "NFPA 13 (2025)" would silently remove the holds.
  - A figure's unit is read from its output name's suffix (`_s`, `_gal`, `_gpm`, and so on; `quantities._NAME_UNITS`). Renaming `t_total_s` to `t_total` would stop "38.1 s" from matching that field.
  - *Inferred:* `fa_calc` accepts a function only when it is defined in its own module, so a function moved into a shared helper and re-exported would be refused as an unknown op.

### Identity

- **The calc code** hashes every non-test `.py` file directly in `calcs/fp/` and `calcs/fa/lib/`. That includes `run.py` and `place_name_scan.py`, but not `draft/`. Any byte change marks every recorded calculation out of date and blocks export until the zone is run again.
- **The fingerprint** hashes every file in the six folders. Any change makes the last trace check not current.

### Tests that pin content

- **Inventory.** Exactly 120 corpus `.md` files and 8 named specs. Skill tiers of 18, 24, 1, and 8, parsed from labels in `skills/README.md`.
- **Phrases.** Phrase assertions on roles, modes, skills, and specs.
- **Figures.**
  - DH-1: 281.3 gal, 38.1 s, 28.1 s
  - DH-2: 505.5 gal, 46.7 s
  - the BESS lower flammable limit (LFL) values
  - the exact `boolean_p` string
- **These figures are regression locks, not independent answers.** They are produced by the tool plan and then locked. `NEXT-STEPS.md`, section 4, notes that `app/tests/test_prototype.py:334` and `:502` build their expected values with 7.48.

## 4. Pack loading and versioning, as implemented

- **Build.** `scripts/build_content_pack.py` writes a flat `fp-fa-content-v<ver>.zip` and a `manifest.json` with `version`, `created`, `sha256`, `filename`, `changelog`, and `min_app_version`. The `pack.json` inside holds only `version` and `created`. A version needs at least two dotted integers. A file that holds an API key, or is named like a key or settings file, is refused. The current tree strips nothing.
- **`min_app_version`.** It is always the building checkout's own app version, not a computed floor. It is checked only when a downloaded pack is installed (`content_update.py:257`).
- **The feed.** The default is `releases/latest/download/manifest.json` on this repository, fetched with no credentials.
  - On 2026-11-12 the repository was private, and that URL returned 404 without credentials.
  - `releases/latest` is `content-v0.5.0`, because app releases publish with `--latest=false` (`.github/workflows/windows-app.yml:227,230`).
- **"Newer."** A strict numeric comparison. The seed carries no `pack.json`, so its label ("bundled seed") counts as older than any numbered pack.
- **Integrity.** Only a sha256 taken from the same manifest. Nothing is signed, and `http` is accepted.
- **Install and lookup.**
  - Packs install to `<data>/content-packs/<ver>/`, keeping one previous pack, with no control to roll back to it.
  - The lookup order is `FPFA_CONTENT_ROOT`, then the saved folder, then the seed. So after an app upgrade, a saved folder wins over the newer seed.
- **The record.**
  - Calculation rows keep a version label and `calc_identity`, but no fingerprint and no app version.
  - Design Basis section 12, "Content the team worked from", prints whatever is installed at export time. The record keeps that context in memory only, and an in-session content update does not refresh it.
- **CI.** A `content-v*` tag runs the calc suites and the pack lint, but not the app suite. The kernel reproduce check never runs in CI, because `FP_KERNEL_DIR` is not set there.

## 5. App-side defects and compatibility risks

Each was reproduced or read in the code at `2f87462` unless marked *inferred*.

1. **Content updates do not work for installed apps, and if they did, they would downgrade.**
   - The feed returns 404, so installed apps never update.
   - If the feed became reachable (the repository made public, or a feed configured), an installed 0.3.2 app would replace its own content with `content-v0.5.0`, which is the 0.2.0 content. Its `min_app_version` is 0.2.0, so the application accepts it.
   - That would silently drop the hardening corrections (the C&E manual station and the isolation qualifier), the kernel refresh of pull request #78, the alias retirement of #80, and every 0.3.x role change.
   - It would also mark every recorded calculation out of date.
2. **Blank inputs are still defaulted**, which CLAUDE.md rules out. A probe on a real desk confirmed it.
   - `desk.collect_di` sends `t_detect_s`, `t_release_s`, and `t_exhaust_s` as `or 0`, and `delivery_basis` as `or "FM"` (`app/fpfa/desk.py:1076-1080`).
   - `collect_basis` turns a blank NFPA 13 or NFPA 72 edition into "2025" and a blank insurer into "FM" (`desk.py:1039-1041`). `workflow.run_tool_plan` repeats the time and basis fallbacks.
   - The 0.3.2 commit message says the form keeps a blank as blank. That holds for five fields, not for these.
   - The edition case matters most: a designer who clears the edition because the adoption is unverified gets 2025 silently.
3. **A double-interlock zone gets the dry-pipe cite.**
   - The application never passes `system_type="di"` to `di_trip_to_water`.
   - On the DH-1 sample, the recorded row carries "DEFAULT USED: no system_type → dry-pipe cite", and its `note_60s_option` cites NFPA 13-2025 s8.2.4.2.
   - The model reads that row, and the trace check uses its outputs as a package assertion. The kernel's docstring says no figure depends on `system_type`.
4. **The application duplicates kernel arithmetic, outside the calc-code hash.**
   - When the model calls the delivery screen directly with only a trim, the application computes `pipe × (1 + fittings/100) + trim` and then `≤ cap` itself. It counts an omitted fittings allowance as 0.
   - The kernel's takeoff instead assumes 5 percent for cut lengths. So the same pipe can get two different zone totals.
   - The fixed tool plan's path uses the kernel's own `zone_gal`, so it is unaffected.
5. **Kernel figures are restated as literal application text** and would go stale silently if the kernel changed:
   - the 500 gal cap (`calc_tools.py:180`, `spec_docx.py:159`)
   - the 5 gal assumed trim (`desk.py:1023`, `workflow.py:327,365`)
   - "NFPA 13-2025 Table 19.2.3.1.2" (`calc_tools.py:230`)
   - the form's starting values (`inputs.py:65-91`): 0.20 gpm/ft², 1,500 ft², 0.30, 250 gpm, 600 gpm, 40 psig, 30 min, 15 psi, FM, 2025
6. **The calc-code identity is all or nothing.**
   - `c400f19` changed only docstrings, and that alone marked every recorded calculation out of date.
   - *Inferred:* rows written by 0.3.0 or 0.3.1 on Windows with CRLF line endings will read out of date after upgrading to 0.3.2.
7. **`docs/content-provenance.md` has gaps.**
   - The `3f6e07b` role additions are not listed at all.
   - Its guard for the QA reason line is overstated.
   - Several sentences in section 2a have no text guard.
   - No test checks that every skill a role names exists (all of them resolve today).
   - The fingerprint recorded in `docs/milestone-hardening-handback.md` is out of date.
8. **Smaller items.**
   - A pack's load-time validation is weak.
   - *Inferred:* reinstalling the same version could keep stale caches until a restart.
   - The README's `2026.x` version examples, if ever published, would block every `0.x` pack.

## 6. Mixed issues: reported, not decided

Each needs the application's owner (Claude) and the content team (Grok), with the owner's decisions through Choom.

1. **The trip cite (section 5, item 3).** The application would pass `system_type` and `declared_interlock`. The Grok team confirms the DI cite text and that passing them is wanted.
2. **The exemption (section 5, item 4).** Proposal: the kernel returns the zone-total exemption itself, and the application stops computing it.
3. **Defaults in application code (section 5, items 2 and 5).** Stopping the silent defaulting is application work. Which starting values to show, and whether there is a default edition, is engineering.
4. **The `POSITIVE` set.** Which zeros are meaningless was classed as application work; the team should confirm. It sits beside the open proposal that `density_area` require values greater than 0.
5. **Unit scope.** Cubic feet, the K-factor (the kernel's `k_si` uses a 14.4 convention), and gauge against absolute pressure.
6. **The lead's missing-input rule.** It now lists the density and the design area among what the team may assume (the owner's ruling). The team should review what that means for the discipline.
7. **Known answers.** DH-1 and DH-2 need independent values; DH-2's inputs still need the owner's confirmation.
8. **The Section 21 13 19 export.** Whether it can open with the live checker (`NEXT-STEPS.md`, N-2), and the pipe-only "passes" wording (N-4).
9. **Already in `docs/content-provenance.md`, section 2b, unchanged:**
   - the 7.48 gallons constant against 1728/231
   - a 2022 body in the kernel's edition gate
   - extended release-wording rules (the two copies change together; on 2026-11-12 they were identical)
   - a rule that a statement about what a result depends on rests on a what-if run
   - the NAC 16.98 V margin against the regimen
   - kernels that return the spare ampere-hours and the hydrant deficit
   - the `blind-claim-check` reply line
10. **Which copy is authoritative** (`docs/content-provenance.md`, section 4) is still the owner's decision. Until then, nothing syncs.

## 7. Tests run, and what is not claimed

Run on 2026-11-12 at `2f87462`, on Linux with Python 3.13.18. CLAUDE.md names 3.12 for the suites.

- **`calcs/fp`:** 262 tests, OK (1 skipped).
- **`calcs/fa`:** 88 tests, OK (13 skipped).
- **`app`:** 579 tests, 578 pass, 1 error. The error is `test_branding.NoticesTests.test_this_environment_has_a_license_text_for_every_package_the_app_needs`. It fails because `pywebview` could not be installed in that environment (its `proxy_tools` dependency would not build on Python 3.13.18), so it is an environment problem, not a code result. With `pywebview` installed without that dependency, the suite was run again with this page added: 579 tests, all pass.
- **The page's tests (`npm test`):** 29 tests, all pass (run with this page added).
- **Probes**, all in a scratch directory:
  - the blank-field probe
  - the DH-1 trip row
  - the identity at ten commits
  - comparing the two copies of the wording rules
  - the role-to-skill references
- **Not run:** the live model, Windows, the installer, or an authenticated feed. All agent behaviour in the suites is scripted. None of this is engineering validation, a check against a standard, or code compliance, and the releasing basis remains unresolved.

## 8. Decisions for the owner

Each of these is application work, to be done in a follow-up once approved:

- **Close the downgrade path** before the feed becomes reachable: publish a current content pack, or make sure `content-v0.5.0` cannot be installed over a newer seed.
- **Stop defaulting blank inputs** (section 5, item 2), which CLAUDE.md already rules out.
- **Correct the gaps in `docs/content-provenance.md`** (section 5, item 7).
