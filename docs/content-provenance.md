# Content provenance: the packaged content, the team's live content, and what must survive a sync

Written 2026-11-11 for the project owner. It needs a decision from you (section 4). Nothing in this repository was changed to settle that decision either way.

## 1. The conflict

The application reads its methods from the content pack in this repository: `skills/`, `roles/`, `modes/`, `corpus/`, `specs/`, `calcs/`. The content team keeps its own working copies of the same material, referred to in the reviews as the live skills.

The 2026-11-11 team review reported that the two have drifted apart:

- None of the 51 packaged skills is in the team's current nine-section form; 28 of the live skills are.
- On the long skills the reviewers compared, only 5 to 12 percent of lines match.
- Corrections made here on 2026-11-10 (pull request #75, commit `bc14eae`) were made to the packaged copies during a pause in the team's skill publication, and were not carried back to the live skills.
- The next skills sync from the team's side would overwrite those corrections.

**What this session could and could not see.** The packaged content is in this repository and was read. The live skills are not in this repository and were not seen, so the drift figures above are the reviewers' report, not a measurement made here. What was measured here: 51 skills are in the pack, and 34 of them are not named in any role file (the same count the reviewers gave).

Neither side is the master. Which one should be is your decision, and this page does not make it.

## 2. Corrections in the packaged content that a sync must not lose

Each of these is a correction to a packaged copy. If the live copy does not have it, a sync from live would undo it. The last column names the test that fails if it is lost; those tests are now run on every pull request (section 5).

### 2a. From pull request #75 (`bc14eae`, 2026-11-10): the second release leg is P

The second leg of the double-interlock release was written as low air in these files and now reads P, the pressure drop from sprinkler operation, with low air named as supervisory only.

| File | Guard |
| --- | --- |
| `skills/dry-preaction-water-delivery-screen/SKILL.md` | `calcs/fp/test_pack_content_lowair.py` scans every sentence |
| `skills/fa-asd-vewfd-data-hall-sampling-layout/SKILL.md` | the same |
| `skills/fa-double-interlock-releasing-cause-and-effect/SKILL.md` | the same, plus `test_the_releasing_skills_name_p_as_the_second_leg` |
| `skills/fa-fire-pump-and-preaction-supervisory-points/SKILL.md` | the scan |
| `skills/fa-hvac-door-and-lock-interfaces/SKILL.md` | the scan |
| `skills/fa-integrated-systems-test-matrix/SKILL.md` | the scan |
| `skills/fa-pathway-survivability-election/SKILL.md` | the scan |
| `skills/fa-supervising-station-signal-schedule/SKILL.md` | the scan |
| `skills/fa-two-level-detection-stagger-and-fm-mapping/SKILL.md` | the scan |
| `skills/nitrogen-inerting-and-c-factor-gate/SKILL.md` | the scan |
| `skills/preaction-el-el-trim-election/SKILL.md` | the scan |
| `skills/preaction-releasing-c-and-e-soo/SKILL.md` | the scan, plus `test_the_releasing_skills_name_p_as_the_second_leg` |
| `roles/fa-releasing/ROLE.md`, `roles/fp-sprinkler/ROLE.md` | the scan |

### 2b. From this milestone (2026-11-11)

| File | What changed | Why | Guard |
| --- | --- | --- | --- |
| `skills/preaction-releasing-c-and-e-soo/SKILL.md` | The controlling Boolean reads `(VEWFD_prealarm OR manual_release_station) AND P` in all six places it is written, with a sentence on what the manual station is and that the footnote 9 bypass is an election | The packaged copy left the manual station out of the detection leg while the kernel, the FA skill, and the corpus carry it. The reviewers reported the live skill and the team's ruling carry it too | `test_the_c_and_e_skill_keeps_the_manual_station_in_the_detection_leg` |
| The same skill, `roles/fa-releasing/ROLE.md`, `corpus/fa/di-releasing.md` | The electric/pneumatic sentence says the solenoid follows the detection leg only while the zone is not isolated | The kernel's own note and the FA skill carry the qualifier; three sentences had dropped it | `test_the_electric_pneumatic_sentence_keeps_the_isolation_qualifier` |
| `roles/fp-sprinkler/ROLE.md` | The specialist passes the takeoff's `zone_gal` to the delivery screen and never states the size exemption from a pipe-only screen | The role told the specialist to quote a flag that was the pipe-only answer when trim and fittings were left out | `app/tests/test_hardening.py`, `test_the_sprinkler_role_tells_the_specialist_to_pass_the_zone_total` |
| `roles/lead/ROLE.md` | A step on saying what a design basis does not cover; what a failed specialist leaves; calculations the app cannot reconcile | So the lead does not present a partial basis as complete | `test_the_lead_is_told_what_is_not_covered_and_the_role_says_what_to_do_about_it` |
| `roles/qa-specialist/ROLE.md` | A figure has to be in the cite as the same kind of quantity | The application now holds a figure to its unit; the checker is told the same | none; it is one sentence of guidance |
| `calcs/fp/test_pack_content_lowair.py` | The detector's rules were widened and two tests added | A reviewer's probe showed the first version missed most paraphrases | it is the guard |

Roles are part of the pack. The reviewers did not report on whether the team keeps live copies of the roles; if it does, the role rows above are at the same risk as the skills.

### 2b-1. From the 0.3.1 fixes that followed the app-v0.2.0 acceptance report (2026-11-12)

One packaged file changed, and only in the part that is the application's contract with the checker: the list of marks the application puts on a cite. No discipline rule, skill, corpus note, specification, or calculation was changed.

| File | What changed | Why | Guard |
| --- | --- | --- | --- |
| `roles/qa-specialist/ROLE.md` | Two marks added to "Kinds of cite on a project record": RECORDED FACT (a fact a contributor wrote, not a value the designer gave) and DECISION (an election the team recorded) | The application used to package every fact as PROJECT INPUT, which the role says is "a value the designer gave", so a specialist's own assumption read to the checker as the designer's. And a finding that rests on a decision now reaches the checker as one | `app/tests/test_acceptance_report.py`, `test_the_checker_is_told_what_the_two_new_marks_mean` |

Three things the acceptance report raised are engineering content and were **not** changed here. They are proposals for the content team, routed through the FP/FA App Grok Bot:

- **The gallons constant.** The FP kernel computes pipe volume with 7.48 gal per cubic foot; the exact value is 1728/231. `NEXT-STEPS.md`, section 4, has the figures and what a change would move.
- **A 2022 body in the kernel's edition gate.** `formulas._parse_nfpa13_dry_edition` holds 2019 and 2025. The application now holds applicability on a job that states another edition; it does not pass an edition to the kernel.
- **The release wording rules.** `releasing.release_wording_hits` and the pack lint's copy read only a sentence that names the supervisory air signal. A statement that the valve releases on one leg alone, or on either leg, reaches no rule. The application now keeps such a statement out of the first group of findings when nothing in it can be matched to the releasing record, but it does not reject it. Rejecting it needs new wording rules, and the two copies change together.

### 2b-2. From the 0.3.2 fixes that followed the app-v0.3.0 acceptance report (2026-11-12)

Four packaged role files changed, each only in a part that is the application's contract with the model: which tool converts a unit, the form of the checker's reply line, and the lead's rule for when to stop and ask, which follows the owner's ruling. No discipline rule, skill, corpus note, specification, or calculation was changed.

| File | What changed | Why | Guard |
| --- | --- | --- | --- |
| `roles/lead/ROLE.md` | Step 3: a figure the designer gave in other units goes in with `set_input` with its unit. The math rule: a change of unit comes from `convert_units`. Step 4: stop only when nothing assumed can stand in for what is missing (no pipe data at all for a volume, a delivery screen, or a gas fill); everything else goes on with stated, labeled assumptions, a request the designer says to answer from what they gave included | F-008: the live specialist ran SI figures as US ones. F-009: the owner ruled on 2026-11-12 that "that's all I have" is answered with a labeled, preliminary screen | `app/tests/test_acceptance_report_030.py`, `MissingInputPolicyTests`; the tools under it, `UnitConversionTests` |
| `roles/fp-sprinkler/ROLE.md` | `convert_units` in the list of tools that own the numbers | F-008 | `UnitConversionTests.test_a_specialist_in_the_turn_is_held_to_the_same_rule`: the application refuses the designer's SI figure in a US field whatever a role says |
| `roles/fa-releasing/ROLE.md` | One sentence: an op takes the units its arguments name; an SI length or pressure goes through `convert_units` first | F-008 | none; one sentence of guidance |
| `roles/qa-specialist/ROLE.md` | The verdict line ends with the checker's reason in brackets, one clause | F-007: the live checker already wrote one, and the application threw it away. The application now keeps it as the checker's reading, apart from its own | `CheckerReasonTests` |

What the report raised that is engineering content, and was **not** changed here. Each is a proposal for the content team, routed through the FP/FA App Grok Bot:

- **A density or a design area of 0 in `density_area`.** The kernel checks both with `_require_non_negative` (`calcs/fp/formulas.py`, lines 114 and 115), so 0 gpm/ft² is a demand of the hose alone. Its own `k_factor` op requires both to be greater than 0 in head-coverage mode (line 425). The application now refuses a 0 on the form, in the lead's `set_input`, and before a zone run; a direct call to the tool still reaches the kernel. Proposal: `_require_positive` for both.
- **A claim about what a result depends on (F-006).** The live team twice said the failing screen did not depend on its assumed detection and release times, when the tool's own `t_fill_s` (28.1 s) was inside the 30 s limit. The application now prints `t_fill_s` and `margin_s` beside the delivery verdict. Proposal: a discipline rule in the specialist roles that a statement that a result does, or does not, depend on an assumed input rests on a recorded what-if run with that input changed.
- **The NAC voltage-drop expectation (GT-FA-01).** At 12 AWG the computed end voltage is 16.98 V against a 16 V minimum, and the pack's method holds that thin margin as failing pending listed data; the acceptance regimen expected a pass. The method and the regimen need one ruling.
- **Figures the kernels do not return (GT-FA-02, and the hydrant case).** The battery calculation returns the required ampere-hours and the margin as a percent, not the spare in ampere-hours; the hydrant curve returns the available pressure, not the deficit. Since a model may not subtract, the team could not state them. Proposal: the kernels return those figures, with their meaning, rather than the application adding a general subtraction tool.
- **The `blind-claim-check` skill's reply line.** It still shows the line without the reason. The QA role, which is what the checker reads, now asks for one; the skill should match it.
- **Units in the content.** The application converts by the definitions alone (`app/fpfa/units.py`). It does not convert cubic feet while the gallons constant is open, a K-factor (the kernel's `k_si` uses its own 14.4 convention), or a gauge pressure to an absolute one. Where a skill or a kernel states a conversion factor of its own, the content team should say whether it agrees with the definitions.

### 2c. Not changed, and why

- **`calcs/fp/di_zone.py`** is pack-only. It is not in the kernel reproduce set, so no kernel sync overwrites it. It no longer returns a `low_air` row key, a `low_air_note` or a `deprecated` block, and its `boolean` string equals `boolean_p`. See `docs/releasing-basis.md`, section 6.
- **`calcs/fp/draft/`** (the held electric/pneumatic release draft and its test) ships in a built pack and is imported by nothing. It is held work and was left as it is.
- **The 34 skills no role names.** They are reachable only if a model finds them in the skill index. Giving each an owner is content work for the team and is not needed by the bounded workflow.

## 3. Identifying the content a result came from

A version label says what somebody called a pack. It does not say what is in it. So the application now computes two values from the files themselves:

- **Content fingerprint**: a hash of every file under `skills`, `roles`, `modes`, `corpus`, `specs`, and `calcs`. Two installs with the same fingerprint are working from the same content.
- **Calc code**: a hash of the kernel files alone. A calculation record keeps the calc code that produced it; when the installed calc code differs, the record marks that calculation out of date.

Both are printed by **About and versions** (`python -m fpfa --versions`), in section 12 of every Design Basis, on every trace check, and at the top of every evaluation report. Section 12 also lists which contributor read which skill, with a hash of the exact text it was given, so a finding can be traced to the method text that was in front of its author. A trace check made against one fingerprint has to be run again when the fingerprint changes.

The fingerprint of this tree at the commit that added this page is recorded in `docs/milestone-hardening-handback.md`. A built pack strips some paths and so has a fingerprint of its own, and a source checkout that converts line endings hashes differently from one that does not. So compare fingerprints between like installs. The one that matters for an evaluation is the one its report prints.

## 4. The decision, and a recommendation

**Decide which copy is authoritative for the content the application ships**, and how changes move between the two. Three workable options:

| Option | What it means | Cost | Risk |
| --- | --- | --- | --- |
| A. The team's live content is the source; the pack is built from it | Every correction in section 2 is first made in the live copy, then exported | The team re-applies about twenty small edits and re-exports 51 skills in the nine-section form | The export replaces every packaged skill at once. The bounded workflow's content changes under the evaluation |
| B. The repository is the source; the team works in it | The team edits skills here, by pull request, and the live copies are retired or regenerated from here | The team changes how it works | Low for the application. High if the team's tooling depends on its own copies |
| C. Per-file ownership with a sync that is checked | A manifest names the owner of each file. A sync from live only replaces files live owns, and the pull-request checks in section 5 must pass | A manifest to write and keep | A file with the wrong owner in the manifest drifts quietly |

**Recommendation: A, done as a controlled reconciliation, after the live evaluation and not before it.**

1. Freeze the packaged content at the fingerprint the evaluation runs on. Do the live evaluation against that. A content change mid-evaluation makes its results incomparable.
2. Have the team carry the section 2 corrections into the live copies, file by file, and confirm each against the guard named beside it.
3. Export the live skills into a branch here. The pull-request checks (the three suites and the pack lint) run on that branch; a correction that was lost fails a named test.
4. Compare the branch's fingerprint and the diff, re-run the offline suites, then re-run the unattended evaluation once on the new content before it replaces the old.

The reason for A over B is that the reviewers describe the live skills as the team's current, restructured form, and the team is where the engineering knowledge is maintained. The reason for the freeze is that the evaluation needs one identifiable body of content. If you would rather the repository be the source, option B needs no export step and the guards already protect it.

Until you decide, nothing syncs. The packaged content stays as it is at the recorded fingerprint, and both sides keep what they have.

## 5. What now stops a silent overwrite

Before this milestone a content release ran no tests: a `content-v*` tag built and published a pack whatever was in it, and no workflow ran the suites on a pull request.

`.github/workflows/tests.yml` now runs on every pull request and every push to `main`: the two calc suites (which include the pack lint and the two guards above), the app suite, and the page's tests. `.github/workflows/content-pack.yml` runs the calc suites and the pack lint before it builds, so a tag on content that lost a correction does not publish.

This is a guard on the corrections that have a test. It does not compare the pack with the live skills, and it cannot notice a correction that was lost if nobody wrote a test for it.
