# Basis of the releasing statement for a double-interlock zone

**Status: UNRESOLVED as engineering. Internally consistent as software.** The app, the content pack, and the tests state one releasing rule and state it the same way everywhere. That rule has not been checked against the text of any standard, insurer data sheet, or manufacturer listing by anyone working in this repository, and no qualified engineer has reviewed it. Nothing on this page is a stamped engineering determination, and the app does not present it as one.

This page says what the app states, the arrangement and assumptions under which the bounded example supports it, where each part comes from and how far that source was actually inspected, what is not settled, and what would settle it.

## 1. The statement the app makes

Water is admitted only when the detection leg and P are both true and the zone is not isolated.

- **The detection leg (D)** is one detection zone at alarm level, or a manual station on the releasing panel standing in for it. A manual station still needs P.
- **P** is the pressure drop from sprinkler operation. It is the second interlock.
  - On **electric/electric** trim, P is a separate pressure contact, tag **PSL-REL**, that the releasing panel ANDs with the detection leg before it energizes the solenoid.
  - On **electric/pneumatic** trim, the panel solenoid follows the detection leg alone while the zone is not isolated, and the listed pneumatic actuator at the valve, tag **PA-REL**, supplies P mechanically.
- **Low air** is a supervisory signal, tag **PSL-SUP**. It is never a release input, and the panel must not map it as one. A slow nitrogen leak or a compressor fault gives a supervisory signal, never a release.

The calc kernel's truth table (`calcs/fp/di_zone.py`, `releasing_truth_table`) is the electric/electric case: `solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated`. Six of its 32 rows are true with a manual station, four without one. A second smoke zone changes none of them.

## 2. What the bounded example supports, and under which assumptions

The milestone's example is one electric/electric double-interlock zone on an FM job (`docs/known-answer-dh1.md`), and a second zone of the same trim (`docs/known-answer-dh2.md`). For those, and only those, the repository supports this much:

| Claim | Support in this repository | What it assumes |
| --- | --- | --- |
| Release needs two events, and the second is sprinkler operation | The pack's reviewed notes state it; the kernel computes it; tests evaluate every row | That the pack's paraphrase of the double-interlock definition is right for the adopted edition |
| Detection alone, a pressure drop alone, and an isolated zone never release | Tested row by row on the kernel's table (`app/tests/test_releasing_basis.py`) | Nothing beyond the Boolean above. This is a test of the app's logic, not of a panel |
| On electric/electric trim the release contact and the low-air supervisory contact are separate devices | The pack's reviewed notes say so | **That the elected valve's trim provides two contacts.** Only the opened trim sheet for the elected valve shows whether the manufacturer provides one pressure switch or two, what each is listed for, and the setpoints |
| A panel manual station stands in for the detection leg and still needs P | The kernel models it; the FA skill and the corpus state it | **That the panel is programmed that way.** The C&E skill's footnote 9 records that some panels let a zone typed Manual Release bypass the AND by default. That bypass is an election needing the owner and the insurer; it is not modelled and is never a default here |
| Low air is supervisory | The pack's notes, with NFPA 72 section numbers by edition | See section 4 on what "low air" means in this sentence |

Outside that arrangement the app makes no computed claim. Electric/pneumatic trim is described in words; no truth table is computed for it, and the held draft under `calcs/fp/draft/` is not imported by anything.

## 3. Sources, and how far each was actually taken

Three different things are kept apart here: what a file in this repository says, what a reviewer reported in correspondence, and what somebody opened and read in the standard itself.

### 3a. Inspected in this repository

| Source | What it supports | Where | How far it was taken |
| --- | --- | --- | --- |
| The content pack's reviewed notes | The device split PSL-REL / PA-REL / PSL-SUP, and that low air is not a release input | `corpus/fa/di-releasing.md`, `corpus/fa/supervisory-points.md`, `corpus/fa/preaction-supervision.md`, `corpus/fp/preaction-trim-and-sequence.md`, `specs/21-13-19-double-interlock-preaction.md` §3.1, `specs/28-31-00-fire-detection-and-alarm.md` §1.2 | Read. They are the content team's paraphrases, merged through pull requests #72 and #73. No standard's text is in the repository |
| NFPA 13: the double-interlock type admits water on operation of both the detection devices and the automatic sprinklers | Two events, the second being sprinkler operation | `corpus/fp/preaction-trim-and-sequence.md` attributes the pair to NFPA 13 without a section number | Held as a paraphrase. **The section number is NOT PULLED** in this repository |
| NFPA 72-2025 §17.19.2.2.2 (2019 and 2022: §17.17.2.2.2): high and low pressure supervisory signals | Low air is a supervisory signal class | `corpus/fa/supervisory-points.md`, `corpus/fa/preaction-supervision.md`, `specs/28-31-00-fire-detection-and-alarm.md` | Held as a paraphrase, by edition |
| NFPA 72-2025 §23.11.6: the sequence of operation matches the suppression standard | The releasing unit's sequence follows NFPA 13 | `corpus/fa/releasing-panel.md` | Held as a paraphrase |
| FM DS 5-32 (January 2026) definition, Table 2.4.1.2 Note 2, §2.4.3.2.1.3.2 | The insurer's AND, and the bar on cross-zoned detection | `specs/28-31-00-fire-detection-and-alarm.md` §1.2, the two releasing skills | Cited by the reviewed spec as OWNER. The insurer's text is not in the pack |
| The calc kernel | The truth table and its row count | `calcs/fp/di_zone.py`, `calcs/fp/test_di_zone.py` | Tested: the Boolean is evaluated row by row |

### 3b. Reported by reviewers, not inspected here

The 2026-11-11 team review reported the following. They are leads for whoever does the verification. Nothing in this repository shows the text, and this page does not treat them as read.

| Lead | Reported by | What was reported | Caveat reported with it |
| --- | --- | --- | --- |
| A joint FP/FA ruling held by the content team, referred to as 8cb97c21 | FP Lead, FA Lead, FA Factory, QA | That it is the team's ruling behind this rule | Not in this repository. One reviewer reported the ruling's wording as low air "not by itself", against this page's "never a release input"; see section 4 |
| NFPA 13-2025 §8.3.2.1(3) | FA Lead | That the team holds it and it supports the two-event definition | This repository does not hold the pin. The section number is unverified here |
| NFPA 13-2025 §8.2.6.3 | FA Lead | That it supports the rule | Reported as dry-pipe wording extended to double-interlock **by inference** |
| NFPA 72-2025 §17.19.2.2.2(A), §23.11.6 | FA Lead | That the team holds them | The pack paraphrases both (section 3a). The text was not opened here |
| The PSL-REL / PA-REL split, the footnote 9 bypass, FM DS 5-32 | FA Lead | Reported as **unverified** by the team itself | No source for the device split other than the pack's own notes is known to this repository |

### 3c. Opened and read in the primary text

**None.** No standard, data sheet, or manufacturer document was opened to write this page or the code behind it.

## 4. What "low air" means in the app's sentence

The second leg and the supervisory signal both sense the pressure of the same supervisory air or nitrogen. Manufacturer literature for electric/electric trims often gives the panel's second contact a low-pressure name, and some panels type that zone as an alarm of the same name. So a reader can fairly ask what the rule means when the contact that carries P is itself a pressure switch on the same gas.

In every sentence the app writes, **low air means the supervisory signal, tag PSL-SUP**: the contact set above the trip point that reports a leak or a compressor fault. The statement is that this supervisory point is not wired or programmed as the release leg. It is not a statement that the release contact senses something other than loss of system pressure. P does: it is the pressure drop from sprinkler operation, sensed at a lower setting by a contact with a different duty.

That reading depends on the assumption in section 2 that the two contacts are separate devices. Where a manufacturer lists one switch for both duties, the sentence does not describe that trim, and the opened trim sheet governs. Whether the team's own ruling says "never" or "not by itself" is a wording question this repository cannot settle; the ruling is not here.

## 5. What was changed, and what kind of change it was

On 2026-11-10 the app's exports, a tool description, a test, two role files, twelve skills, and the sample's known answer were changed to say what the pack's reviewed corpus and specs already said: the second leg is P, the pressure drop from sprinkler operation. The calc kernel's logic did not change; it computed the same rows before and after.

**That was a reconciliation for internal consistency.** Documents and strings were edited to agree with the pack's own reviewed notes. It was not a reconciliation from primary evidence, because no primary source was opened. An earlier hand-back said "No document was edited to match another"; that sentence was wrong and has been corrected where it stood. The reviewers who read the result agreed the rule is right in substance and disagreed about what to call the change. This page calls it what it was.

Changed on 2026-11-11, in the same spirit and with the same limit:

- The packaged C&E skill's controlling Boolean left the manual station out of the detection leg, while the kernel, the FA skill, and the corpus all carry it. It now reads `(VEWFD_prealarm OR manual_release_station) AND P`, with the footnote 9 bypass named as an election.
- The electric/pneumatic sentence in the releasing role, the C&E skill, and one corpus note said the solenoid follows the detection leg and left out that an isolated zone blocks it. Each now carries the qualifier the kernel's own note has.
- A finding or a lead reply that departs from this rule is now caught at run time, not only in the pack's prose (`fpfa.releasing.release_wording_hits`). The trace check will not call such a finding supported whatever it cites.

These are corrections to the packaged copies of the content. The content team's own copies may differ, and a later sync could overwrite them. `docs/content-provenance.md` lists each one so it can be carried across.

## 6. The kernel's deprecated names

`releasing_truth_table` still returns a `boolean` string and a `low_air` row key that spell the second leg the old way, beside `boolean_p` and `p_second_leg`. Only `app/fpfa/releasing.py` reads them, and nothing a model or a designer sees carries them; tests hold that.

The reason once given for keeping them, that installed apps older than 0.2.0 read those names, no longer holds: a pack built from this tree asks for this app version or newer, so no older app will load it. They are kept for a different reason. `di_zone.py` has a copy on the content team's side, and removing the names here without removing them there would be undone by the next kernel sync or would split the two. Retiring them is a one-line change to make in both places together. It is listed for the owner in `docs/milestone-hardening-handback.md`.

## 7. How the statement is kept from drifting

- `calcs/fp/test_pack_content_lowair.py` scans every prose folder a model reads (`corpus/`, `specs/`, `skills/`, `roles/`, `modes/`) and fails on the old phrasings and on the paraphrases a reviewer's probe showed the first version missed. It also holds the C&E skill to the manual station in the detection leg.
- `app/tests/test_releasing_basis.py` scans `docs/`, the README, and the app's own source with the same rules, checks what the app writes, and tests the logic row by row.
- `app/tests/test_hardening.py` plants a finding that departs from the rule and checks that it is not supported and does not earn a tier.

The detector is a guard against known wrong wording. A paraphrase nobody thought of passes it. It is not evidence that the rule is right.

## 8. The acceptance gate

The releasing basis is **not accepted** until all of these are recorded on this page, each with who did it and when:

1. **The NFPA 13 double-interlock definition** read in the adopted edition, with its section number. NFPA 13-2025 is the delta baseline; an unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified.
2. **The NFPA 72 supervisory and releasing sections** read in the adopted edition.
3. **The elected valve's trim sheet** opened: one pressure switch or two, what each is listed for, and the setpoints. This decides whether section 4's assumption holds on the job.
4. **The panel's handling of a manual release zone** confirmed on the as-loaded program, against footnote 9.
5. **The team's ruling** added here, or its wording reconciled with this page's.
6. **A qualified engineer's review** of sections 1, 2, and 4.

Until then the app's own documents say what kind of checking each statement had. The Design Basis lists the kinds of assurance and names verification against the primary standard and a qualified engineering review as not performed. The evaluation runner prints this gate in every report.

What is not held up by this gate: the software hardening, the offline tests, and the live evaluation of whether the team behaves like a team. A run that agrees with this page shows consistency with the content pack, and nothing more.
