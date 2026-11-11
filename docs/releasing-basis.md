# Basis of the releasing statement for a double-interlock zone

This page records what the app says about how a double-interlock preaction valve releases, where that statement comes from, what was checked in this repository, and what still needs a qualified engineer. It exists because the sample's known answer, the exports, a tool description, a test, and several skills carried an older wording that disagreed with the reviewed corpus and specs. The disagreement was resolved on 2026-11-10 in favour of the reviewed content. Nothing on this page is a stamped engineering determination.

## The statement

Water is admitted only when the detection leg and P are both true and the zone is not isolated.

- **The detection leg (D)** is one detection zone at alarm level, or a manual release station on the panel standing in for it. A manual station still needs P.
- **P** is the pressure drop from sprinkler operation. It is the second interlock.
  - On **electric/electric** trim, P is a separate pressure contact, tag **PSL-REL**, that the releasing panel ANDs with the detection leg before it energizes the solenoid.
  - On **electric/pneumatic** trim, the panel solenoid follows the detection leg alone, and the listed pneumatic actuator at the valve, tag **PA-REL**, supplies P mechanically.
- **Low air** is a supervisory signal, tag **PSL-SUP**. It is never a release input, and the panel must not map it as one. A slow nitrogen leak or a compressor fault gives a supervisory signal, never a release.

The calc kernel's truth table (`calcs/fp/di_zone.py`, `releasing_truth_table`) is the electric/electric case: `solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated`. Six of its 32 rows are true. A second smoke zone changes none of them.

## Why the older wording was a defect, and what kind

The logic never changed. The kernel computed the same 6 of 32 rows before and after. What changed is the name of the second leg and, with it, which device the reader is told to wire.

Manufacturer literature for electric/electric trims often calls the panel's second input a low-air or low-pressure switch. The older pack wording followed that habit and wrote the second leg as low air. Read literally by a designer or a model, that tells the panel programmer to use the low-air supervisory point as the release leg. That is wrong on two counts the reviewed content names:

1. On electric/electric trim, the release contact and the supervisory low-air contact are separate devices with separate duties and setpoints. The supervisory signal has to arrive before the valve can trip, which is why the trim skill sets it above the trip point with margin.
2. On electric/pneumatic trim, the panel has no pressure input in the release AND at all. A Boolean that puts a pressure leg in the panel logic describes a different trim.

So this was a label defect with a real consequence, not an arithmetic defect. The figures of the sample zone are unaffected.

## Where the statement comes from

| Source | What it supports | Held where | Status |
| --- | --- | --- | --- |
| NFPA 13, definition of the double-interlock preaction type: water is admitted on operation of both the detection devices and the automatic sprinklers | Two events are required, and the second is sprinkler operation, not a supervisory condition | `corpus/fp/preaction-trim-and-sequence.md` states the pair and attributes it to NFPA 13. The pack does not pin the section number of the definition | The duty is held as a paraphrase. The section number is NOT PULLED. Confirm it in the adopted edition; NFPA 13-2025 is the delta baseline |
| NFPA 72-2025 §17.19.2.2.2 (2019 and 2022 §17.17.2.2.2): high and low pressure supervisory signals on dry pipe and preaction | Low air is a supervisory signal class | `corpus/fa/supervisory-points.md`, `corpus/fa/preaction-supervision.md` | Held as paraphrase, by edition |
| FM DS 5-32 (January 2026) definition and Table 2.4.1.2 Note 2, and §2.4.3.2.1.3.2 on cross-zoning | The insurer's definition of the AND and the bar on cross-zoned detection | `specs/28-31-00-fire-detection-and-alarm.md` §1.2 | Cited by the reviewed spec as OWNER. The insurer text itself is not in the pack |
| The content pack's reviewed notes | The device split PSL-REL / PA-REL / PSL-SUP and the sentence that low air is never a release input | `corpus/fa/di-releasing.md`, `corpus/fa/supervisory-points.md`, `corpus/fp/preaction-trim-and-sequence.md`, `specs/21-13-19-double-interlock-preaction.md` §3.1, `specs/28-31-00-fire-detection-and-alarm.md` §1.2 | Reviewed and merged by the content team (pull requests #72 and #73) |
| The calc kernel | The truth table and its row count | `calcs/fp/di_zone.py`, `calcs/fp/test_di_zone.py` | Tested: the Boolean is evaluated row by row |

No standard was opened to write this page. The repository holds paraphrased pins, not standards text. The table says which statements rest on a held paraphrase and which rest only on the content team's reviewed notes.

## What was changed to match it

- The app reads the kernel's `boolean_p` and `p_second_leg` everywhere it prints the releasing logic: the zone narrative, the Results tab, the Section 21 13 19 export (the truth-table column is now "P (second leg)"), and the Design Basis export. `app/fpfa/releasing.py` is the one place that knows the kernel also returns a deprecated alias.
- A model never sees the deprecated alias. The tool result it reads carries `boolean_p`, rows keyed `p_second_leg`, and one sentence on what low air is. The tool's description says the same.
- When the trim screen elects a family other than electric/electric, the narrative and the documents say that the truth table is the electric/electric reference and not that valve's logic.
- `roles/fa-releasing/ROLE.md` and `roles/fp-sprinkler/ROLE.md` state the rule. Twelve skills that wrote the second leg as low air were corrected sentence by sentence to the wording of the reviewed corpus and specs.
- `docs/known-answer-dh1.md` sections 1, 2, 3, and 7 were aligned.
- The form field that feeds the trim screen is labelled "Low-air supervisory psi".

The kernel still returns the deprecated string and row key. Installed apps older than this one read those names, and a content update must not break them. They can be removed from the kernel once no supported app reads them.

## How it is kept from coming back

- `calcs/fp/test_pack_content_lowair.py` scans every prose folder a model reads (`corpus/`, `specs/`, `skills/`, `roles/`, `modes/`) and fails on the old phrasings. It ran over two of those folders before.
- `app/tests/test_releasing_basis.py` scans `docs/`, the README, and the app's own source strings with the same detector, checks what the app writes (narrative, both documents, the model-facing tool result and description), and tests the logic row by row: detection alone does not release, P alone does not release, a manual station still needs P, an isolated zone never releases, and a second smoke zone changes nothing.

## What still needs a qualified engineer

These are not settled by this repository and are not presented as settled by the app.

1. **The NFPA 13 section number of the double-interlock definition** in the adopted edition. The pack holds the duty and not the pin.
2. **Which device is which on the elected valve.** The opened trim sheet decides whether the manufacturer provides one pressure switch or two, what each is listed for, and the setpoints. The pack's rule is that PSL-REL and PSL-SUP are separate contacts.
3. **The electric/pneumatic case.** The kernel's truth table does not model it. The app says so in words; it does not compute a table for that trim.
4. **A panel zone typed for manual release that bypasses the AND.** The kernel does not model it and never defaults to it. The C&E skill treats it as an election that needs the owner and the insurer.
5. **The sample's known answer** (`docs/known-answer-dh1.md`) still has three items marked OWNER TO CONFIRM, and the releasing statement in it now rests on this page. The owner's confirmation of that page covers this one.
