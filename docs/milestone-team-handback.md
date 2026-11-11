# Team milestone: what was found, what changed, and what is not yet known

> This is the hand-back for version 0.2.0. It is kept as written, with one dated correction in section 2D and this note. Two independent reviews of that version found defects it did not report; `docs/milestone-hardening-handback.md` reconciles each finding and says what version 0.3.0 changed. Where the two disagree, the later one is current.

Version 0.2.0. Written 2026-11-11 for the project owner, against the brief "take this application to its next meaningful version": a coherent, bounded agent-team workflow that a coworker can start with an ordinary project request, continue across sessions, and use to produce an inspectable engineering draft.

The short version. The application now has the machinery for that workflow, and every part of it is tested with scripted stand-ins for the model. **No request has been sent to the live model.** Whether the model, handed a plain objective, behaves like a coordinated team is the question this milestone was for, and it is still open. `docs/live-evaluation.md` is the hour it takes to answer it.

## 1. Where the application stood

Read from the repository at the start of this work, not from the correspondence about it.

What was solid:

- Numbers came from deterministic calc kernels with their own tests, and the three labels (calculated, ASSUMED, use best judgment) were kept apart everywhere.
- A project record in SQLite, written only through tools, with calc results replayed by input hash, and a recovery pass tested with a real process kill.
- A working window, prompt caching, usage totals, a cost report, and an installer script.

What stood between that and the brief:

| Outcome in the brief | What the code did |
| --- | --- |
| A. Delegate an objective, not a workflow | The lead was the everyday chat shell plus one paragraph about three team tools. It had `read_role`, so it could read a specialist's role and answer in its place. The acceptance test for collaboration told it which specialist to use for what and when to run the check. |
| B. Specialists collaborate on a shared problem | They never met. A handoff written by one was delivered when the lead next delegated to the other. Nothing let one take a position on the other's finding, and nothing recorded a disagreement or its end. The lead received two contributions and pasted them together. |
| C. The project stays coherent as it changes | The inputs lived on the form. Each turn got a copy of them in its message. Changing a value left every calc record, finding, and export as it was, and the next chat request still told the lead that the old run's figures "govern". Nothing said where a job stood except the thread itself. |
| D. The output earns appropriate trust | The check judged each finding against the note its own author wrote beside the cite. It was called a blind check, and the export waited until every finding was "Supported", which read as more than it was. Separately, the releasing expression was wrong on every surface downstream of the kernel: the tool's description, what the model was shown, the thread, the Results tab, both exports, two role files, and twelve skills. The kernel had been corrected to P as the second leg, with low air supervisory only and never a release input; nothing downstream had followed. |
| E. Usable by a coworker | Chat-first already. The Team tab was a roster, a list of blockers as text, and a handoff table. A specialist's findings and what they rested on were not shown. |
| F. Ready for honest live evaluation | Nothing had been run against the live model. Tests with a scripted model had been reported as collaboration demonstrated. A request was retried three times, two seconds apart. |

One thing was right and is kept: the decision to run the team on the existing Messages loop and not to adopt an agent framework. Nothing found here argues against it.

## 2. What was done, by outcome

### A. The designer delegates an objective

- The lead has its own role, `roles/lead/ROLE.md`, in the content pack. It says how to run a turn: read where the job stands, decide what the request needs, put what the designer said on the record, ask only what blocks the work, state a plan, delegate in dependency order, reconcile, check, answer. It no longer has `read_role`.
- New tools for the lead: `set_plan`, `set_input` (record a value the designer stated in chat), `answer_question`, `resolve_disagreement`.
- Each lead turn opens with a status block the application reads from the record, so the lead does not depend on its memory of earlier turns.
- A question for the designer is a different thing from an RFI for the engineer of record. The designer answers the first on the Team panel, in place.
- Acceptance Test B now asks for a design basis in a plain sentence.

### B. Specialists collaborate

- `consult`: one specialist asks another a question and gets the answer inside its own turn. The exchange is a record row.
- `review_finding`: agree, or object with a note that says what would settle it. An objection ends when the author revises or withdraws the finding, the objector changes its position, or the lead settles it with a recorded decision or escalates it as a question.
- Each specialist's brief lists what on the record needs it: its own findings whose basis changed, objections to its findings, and the other contributor's findings it has not reviewed.
- Each specialist role says what it owns, what it needs from the other, and what it reviews. The delivery screen's detection and release times belong to the releasing specialist; the trim family and pressures belong to the sprinkler specialist.
- The application sees one kind of inconsistency by itself: a calc run on a value other than the project input is marked as an alternative, and a finding resting on it is put in front of the lead. A calc that took a figure from an alternative is marked the same way.
- Nothing forces an exchange. If the model does not ask or review, the record shows two contributions with nothing between them.

### C. The project stays coherent

- The project inputs are record facts, each with who supplied it. A starting value the designer never confirmed is marked as one.
- Every calc records which inputs it used and which calc it took a figure from. When an input changes, what used it is out of date, with the reason, until it is run again, replaced, or withdrawn. Old rows are kept as history.
- A run of the tool plan on inputs that have since changed governs nothing. The lead is told it is out of date, the Results tab says so, and Section 21 13 19 is not written from it.
- `/status`, the line under the top bar, and the Team panel say where a job stands with no model call. Suggestions above the composer follow what is waiting.
- A second window on the same data shows the same state. Tested.

### D. The output earns appropriate trust

- The releasing statement is corrected end to end: release is the detection leg AND P; low air is supervisory only. `docs/releasing-basis.md` gives the basis and what in it still needs a qualified engineer. The fix is to the statement, held by tests that read the truth table row by row and the prose sentence by sentence. *Corrected 2026-11-11: this line used to end "No document was edited to match another." That was wrong. The exports, the roles, twelve skills, and the known answer were edited to agree with the pack's reviewed corpus and specs, and no primary source was opened. `docs/releasing-basis.md`, section 5, says what kind of change it was.*
- The check is a trace check and is called one. A cite to a standard is read in the content pack's own reviewed note on that section when the pack holds one, not in the author's note. A figure with a unit in a claim has to be in the rows it cites. An out-of-date finding is not judged.
- Each finding earns one of four tiers, derived by the application: checked against an identified source; reviewed against its author's own cite; produced by a specialist and not reviewed; needs further evidence or engineering review. The Design Basis opens with the counts and lists every finding under its tier with what it rests on.
- The Design Basis waits for a current check and for nothing out of date. It no longer waits for every finding to be supported, because that rule pushes a team to drop exactly the findings an engineer most needs to see.
- The application looks up every figure in the lead's reply and names under the reply any it cannot find, or finds only on an out-of-date calculation.
- Nothing says a standard was checked. Every check result carries `checked_against_standard: false`.

### E. The interface

- The Team panel is rebuilt in the order a returning designer asks: where things stand, what needs your answer, what is out of date, what is not reconciled, findings by tier with their evidence, how disagreements ended, exchanges by kind.
- Under a lead reply the application writes what passed between the specialists.
- Everything on the panel works from the keyboard. Colour is never the only signal.

### F. Honest live evaluation

- `docs/live-evaluation.md`: the path by hand, step by step, with what a miss looks like and a scoring sheet.
- `python -m fpfa.live_eval`: the same path unattended, in its own data directory, with a spend cap, writing a report of what the record shows.
- `docs/acceptance-tests.md` has a table of tested, simulated, and unrun.
- A transient API failure is retried up to five attempts and honours the API's `retry-after`. Time is recorded beside cost.

## 3. The architectural changes, and the problem each solves

| Change | The user problem |
| --- | --- |
| The lead's behaviour moved from Python into a role file in the content pack | A designer should not have to name specialists or set an order. How a team is run is method, and method is content that can be revised without a build. |
| Inputs moved from the form into the record, and calcs record what they followed | "Earlier calculations and design statements must not silently remain authoritative after their basis has changed." That needs the application to know what each statement rests on. |
| One specialist can ask another directly, and positions on findings are rows | A dependency between two specialists cannot be worked through a mailbox emptied at the next delegation. And reconciliation that is not on the record cannot be inspected. |
| The check reads the content pack, and tiers replace a single pass or fail | A reader has to tell apart what was checked against something, what was only reviewed, what was only stated, and what is open. One word for all four was the trust problem. |
| The export gate changed from "all supported" to "current and nothing stale" | The old gate blocked the document unless unsupported findings were removed. The new one prints them where the engineer will look. |
| A status digest derived from the record, shared by the lead, the specialists, the window, and the gate | Coming back to a job, the designer and the lead should read the same account, and neither should need the thread to reconstruct it. |

What did not change: the Messages loop, one model, one vendor, the calc kernels, the window's stack, the record as SQLite, the Section 21 13 19 export and its gate.

## 4. What is in 0.2.0

New modules: `inputs.py`, `coherence.py`, `status.py`, `checker.py`, `reply_audit.py`, `releasing.py`, `live_eval.py`. Rewritten: `team.py`, `design_basis_docx.py`, `team_panel.py`. New content: `roles/lead`; "Working with the team" in the two specialist roles; the cite kinds in the QA role; twelve skills corrected. New in the page: the Team panel, the line under the top bar, the Results warning. New documents: this one, `live-evaluation.md`, `releasing-basis.md`. The record is schema 4; an older database is migrated when opened. A content pack built from this tree asks for app 0.2.0 or newer.

## 5. Evidence, limits, and what is unrun

### What was run

All four suites pass on Linux with Python 3.12 and Node 22: `calcs/fp` 251 tests (1 skipped: the kernel reproduce check needs a kernel source folder), `calcs/fa` 88 (13 skipped, as before), `app` 449, and the page's 22. The app suite includes two runs of the built page in Chromium, each with more than thirty checks.

What those tests establish, in the words of `docs/acceptance-tests.md`:

- **Tested** (real code, no model involved): the kernels and the DH-1 figures; the releasing truth table and every surface that prints it; inputs, dependencies, and staleness; the trace check's own rules, including a planted wrong figure with a matching author's note; the tiers; both export gates; the reply audit on written replies; retries; recovery with a real kill; the page in a browser.
- **Simulated** (the real application, every model call scripted): a lead that plans and delegates; a question between specialists; an objection and a revision; a job closed, reopened, changed, interrupted, and exported (`app/tests/test_scenario.py`); the unattended runner.

### Known limits

- The role files are prompts nobody has watched a model follow. If the lead does not delegate, or the specialists do not review, the application will show that plainly and do nothing about it.
- The trace check's own judgment is untested: in every test the checker stand-in says Supported to everything, so only the application's rules are exercised. A live checker may be stricter or looser.
- The pack lookup is by document, edition, and section number in `corpus/` and `specs/`. It is conservative: a section written without its document nearby is not found, and the cite then counts as resting on its author. Skills are not searched.
- The figure rule and the reply audit match numbers, not quantities. 900 gpm passes if a 900 ft pipe is on the record. They catch a figure that matches nothing.
- The check is a second pass by the same model on a blind packet. It is not an independent reviewer and it does not open a standard. The document says so; that does not make it less true.
- The releasing statement was corrected from the content pack's own reviewed notes. `docs/releasing-basis.md` lists what was held as a paraphrase and what was not pulled. A qualified engineer has not reviewed it.
- The truth table is for electric/electric trim. An electric/pneumatic sequence is described in words.
- The lead's instructions with the spec files are about 28,000 tokens on every request. Cached after the first round, but it is the largest fixed cost.
- A long team turn has no progress bar, only the working line. A design-basis request may take several minutes.
- The sample's 40 psig fill pressure beside a 15 psi low-air supervisory setting, and its 8 s and 2 s times, are loose inputs. A live specialist may object to them, and would be right. `docs/known-answer-dh1.md`, section 8.
- Three items in the known answer are still marked OWNER TO CONFIRM.

### Unrun

1. Any request to the live model from this version.
2. Whether a plain request, in words other than the two in the guide, gets a plan, both specialists, and only the questions that block.
3. Whether the specialists ask, review, object, and revise without being told to.
4. Whether the lead reconciles or pastes.
5. The time and the cost of one design-basis request, and of the whole evaluation path. The figures in the guide are estimates from prompt sizes.
6. The trace check on live findings.
7. The unattended runner against the live API. Its plumbing ran with a scripted model.
8. Effort levels compared.
9. Everything on Windows: the installer, the WebView2 window, Credential Manager, sleep and hibernate, a forced kill of the packaged exe. The page was checked in Chromium on Linux.
10. A database from 0.1.4 opened by 0.2.0 on a real install. The migration is tested on a synthetic older database.

## 6. The live evaluation

`docs/live-evaluation.md`. About an hour by hand: a plain request, the dependency, a missing value, a changed input, close and reopen, an interruption, the draft, time and cost, Windows. Do it by hand first; the unattended runner is for repeating it and for comparing effort levels.

The single most informative ten minutes: send the plain request in step 1, then open the Team panel and look for one row that connects the two specialists. If there is none, the role files need work before anything else matters.

## 7. Recommendations for the next iteration

Separate from this milestone. None of these is started.

1. **Run the live evaluation, then fix what it shows in the role files.** Expect the first live run to need prompt changes. They are content, not code.
2. **Measure cost before changing the model.** If a design-basis request costs more than it should, the levers in order are: stop sending every spec file to the lead (it delegates; it rarely needs them), then effort per role, then a smaller model for the checker's single call. Each is a measured decision.
3. **Ask the API for a fallback when the model refuses.** The lead and the specialists have none today; a refusal ends the turn with a notice.
4. **Give the electric/pneumatic sequence a truth table of its own**, and retire the kernel's deprecated low-air aliases once no installed app older than 0.2.0 reads them.
5. **Let the trace check read skills as well as corpus notes**, so a method's own numbered screens count as a source.
6. **Division 28 exports.** The releasing specialist's work has no document of its own yet.
7. **A cancel that interrupts a request in flight**, not only between rounds.
8. **Unit-aware figure matching** in the reply audit and the trace check.
9. **A second vertical** (dry pipe or wet) through the same team, once the first survives live use.
