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
