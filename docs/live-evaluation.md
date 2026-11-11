# Live evaluation guide

For the project owner, on a Windows machine, with a saved Anthropic API key. About an hour and a half by hand. You do not need to know how the application is built to follow it. The question to answer at the end is the milestone's:

> Can a coworker hand the application a meaningful FP/FA objective and experience a capable, coordinated team carrying the work forward?

## Where things stand before you start

Five different things can be called "done". They are not the same thing and none of them implies the next.

| What | Standing on 2026-11-11 | What it shows |
| --- | --- | --- |
| Software hardening | Done for this milestone (`docs/milestone-hardening-handback.md`) | The defects two reviews found are corrected or stated as open |
| Offline regression evidence | Done: four suites pass on Linux, every model call scripted | The application does what its tests say. Nothing about the live model |
| Installed Windows evidence | **Not run.** No one has installed, launched, or migrated this version on Windows | Nothing yet |
| Live-model evidence | **Not run.** No request from this version has reached the live model | Nothing yet. This guide is how to get it |
| Engineering validation | **Not done.** No standard was opened and no qualified engineer has reviewed the basis (`docs/releasing-basis.md`) | Nothing yet. A live run cannot supply it |

A passing scripted test is a passing scripted test. It is not a passing live-team evaluation.

Three things stand between any run of this guide and calling the milestone accepted, whatever the run shows:

1. `docs/known-answer-dh1.md` still has items marked OWNER TO CONFIRM.
2. The second job's inputs (`docs/known-answer-dh2.md`) were chosen for the test and wait for your confirmation.
3. The releasing basis has no primary-source check and no qualified review.

## What it may cost, and how sure that is

**Nobody has measured this.** Two estimates exist, both modelled from the code and neither observed:

| Estimate | One design-basis request | The whole path | Who, and from what |
| --- | --- | --- | --- |
| Earlier guide | "a few dollars", "several minutes" | 5 to 25 dollars, 20 to 60 minutes of model time | The previous coding session, from prompt sizes: about 28,000 tokens of lead instructions, 12,000 per specialist, 9,000 to 21,000 per skill read |
| Team review, 2026-11-11 | about 3 dollars (range 1 to 7), 12 to 25 minutes | about 11 dollars (range 6 to 25), 50 to 90 minutes | The team's Claude Developer SME, modelled from the code; reported that the earlier time figures were too low |

This version adds a probe step and a second job, which neither estimate includes: allow for two more trace checks on the first job and a second full request. Plan on the longer times. Write down what `/usage` shows; it is one of the things this evaluation is for.

What `/usage` shows is the usage the API reported. A request that fails reports none, so after a failure the figure is a floor on what was spent, not a ceiling. `/usage` says so when it applies.

## Before you start

1. **Do not touch your real jobs.** Use a data directory of its own. In PowerShell, before launching from that same window:

```powershell
$env:FPFA_DATA_DIR = "C:\Temp\cynosure-eval-1"
```

   Your existing data is in `%APPDATA%\fpfa-assistant` and is not read or changed while that variable is set. Nothing in this guide asks you to delete it.
2. Install the build under test, or run from source (`cd app`, `py -m pip install -r requirements.txt`, `py -m fpfa`). The section "Windows, step by step" below is the install check; do it first on a new machine.
3. Save your key in Settings.
4. Open **About and versions** (the ⋯ menu) and copy the lines **Content pack** and **Content fingerprint**. Every result you write down belongs to that fingerprint. If it changes during the evaluation, the content changed and earlier results are about other content.
5. Keep `docs/known-answer-dh1.md` and `docs/known-answer-dh2.md` open. Each has the figures, the expected statements, and what a live run may add that is not a mistake.

## The path

Do the steps in order. After each, write one line in the scoring sheet at the end. A step that goes wrong is a finding; keep going.

### 1. A plain request

Type `/sample-di` to put a zone on the form. It runs the tool plan with no model call. Then send this, as written:

> We're laying out the preaction zone for data hall 1. Can it meet the insurer's water delivery time, and what releasing sequence goes with it? I need a design basis I can hand to the engineer.

It names no specialist and no order. Do not add any.

Look for:

- A plan on the Team tab (WHERE THINGS STAND) before the specialists start, in words you would use.
- Both specialists brought in without being asked. The working line names who is working.
- Questions only where the work is blocked. The sample's trim volume is blank, so one question about it is right. Ten questions is a miss.
- A short reply that says who did what, what was contested, what it needs from you, what the design basis does not yet cover, and what the trace check covered.

Warning signs: the lead answers with figures and the Team tab shows no specialist; one specialist only; a reply that reads complete while the Team tab shows A DESIGN BASIS WOULD BE INCOMPLETE.

### 2. Whether the two specialists worked together

Open the Team tab.

- EXCHANGES BETWEEN AGENTS: is there a `question` row from one specialist to the other, with a real answer? Open it and read both.
- FINDINGS: open a releasing finding. Does it rest on the sprinkler specialist's trim **finding**? Open the delivery-screen finding. Did the releasing specialist review it, and did it give a reason?
- NOT YET RECONCILED and HOW DISAGREEMENTS ENDED: was anything contested? Was the objection about something real, and did the revision answer it?

What does **not** count, however it looks: a finding that cites a calculation the other specialist ran first, when the citing specialist ran the same calculation itself. The record replays the first one's row, so the row carries the other's name whether or not anyone read anyone's work. An agreement with no reason beside it does not count either.

A miss looks like two tidy contributions side by side, no question, no reasoned position, and a reply that pastes them together. The application does not force an exchange, so if the model does not make one, none appears.

The sample's 8 s detection and 2 s release times have no stated basis. A specialist that says so is right.

### 3. Which methods they read

On the Team tab, METHODS READ lists which contributor read which skill, and whether it read it before or after it recorded findings.

- A specialist with findings and nothing under METHODS READ worked from its role file alone.
- A read shows the method was in front of the specialist. It does not show the method was followed. Open one finding and one cite and ask whether the work looks like the method. That judgment is yours; the application does not make it.

### 4. Missing information

Under NEEDS YOUR ANSWER, type an answer (for the trim volume, `6.5 gallons, from the submittal`) and press Answer. It goes on the record and into the thread. Nothing runs yet. Press **Continue with my answers** above the composer.

Look for: the lead acts on the answer, the trim volume appears on the Inputs tab, and the volume finding is replaced with one that says where the 6.5 came from.

### 5. A changed input

Send this:

> One more thing: the pump test gave us 750 gpm at the riser, not the 600 on the form. Does that change the answer?

Look for:

- Fill flow on the Inputs tab becomes 750 without your touching it.
- The findings that used 600 are **replaced**, not left standing. FINDINGS shows the new ones; the export's section 11 keeps the old ones as history. Being marked out of date is noticing the change. Being replaced is reconciling it.
- The reply says what was recalculated and what is still open.
- The Results tab says its figures are from a run before the form changed.

Then send a follow-up that does not mention the old number, such as "So what is the fill flow we are designing to?" The reply should say 750. **If it says 600, or quotes the old 38.1 s, the application says so under the reply** in its own words: "figures in this reply that the record now holds only on out-of-date rows". That note is the thing to look for; a wrong figure with no note under it is a defect to write down.

Then change a field yourself: on the Inputs tab set Releasing time to 5 and press Ctrl+S. The Team tab should show OUT OF DATE, and **Bring it up to date** should appear above the composer. Press it.

### 6. Close and reopen

Close the window. Open it again and open the job.

Look for: the line beside the job name, the count on the Team tab's button, **Where things stand** above the composer, and `/status`. Could you tell where the job stood without reading the whole thread? Is anything missing that was there before?

### 7. An interruption, and a failure

**Interruption.** Ask for something that takes a while ("Write me a short summary of this design basis for the engineer's cover email, and say what is still open."). While the working line shows a specialist, press **Stop**. Then send "That was cut off. Finish it."

Look for: a Cancelled line; on the Team tab and in `/status`, who was cut off, what it had recorded, and that the work is partial; a sentence saying what asking again repeats (the model's work is done and billed again; recorded calculations replay). The next turn should finish without duplicating findings.

**Failure.** Turn the network off (airplane mode) while the working line shows a specialist, wait for the turn to end, and turn it back on. Look for: a reply that says the request failed and what was kept; `/usage` listing the failed work marked FAILED with the usage it had before the failure, and the line saying a failed request reports no usage. Then ask again.

The harder version is in `docs/recovery-protocol.md`: end `Cynosure.exe` from Task Manager while a specialist is working, relaunch, and read the recovery note.

### 8. Testing the check with claims you know are wrong

The trace check is a second pass by the same model. A check that approves everything looks exactly like a check that works, until something wrong is put in front of it. Ask the lead to record each of these, one at a time, then press **Run trace check** on the Team tab and read where each landed.

| Ask the lead to record that... | What should happen | What it tests |
| --- | --- | --- |
| "a double-interlock zone up to 765 gallons needs no delivery-time proof, citing the delivery screen calculation" | Not supported: "figure not in the rows it cites: 765 gal". Under "Needs further evidence or engineering review" | The application's own rule on figures |
| "the trip-to-water time is 281.3 seconds, citing the volume calculation" (use your job's zone total) | Not supported: the rows hold that number only as another quantity | The rule on units |
| "the valve releases on detection and low air, citing the releasing truth table" | Not supported, with the releasing rule quoted | The rule on the releasing wording |
| "the trim screen elects the electric/pneumatic family for this zone, citing the trim calculation" | Not supported. **No rule of the application covers this one.** Only the checker's own judgment can reject it | The checker itself |

The fourth is the one that tells you something about the checker. If it comes back as trace-consistent, the checker approved a claim that contradicts the row it cites, and every trace-consistent finding on the job is unproven. Write that down in those words.

Withdraw all four afterwards by asking the lead to. They stay in the export's history section and nowhere else.

### 9. The draft and its evidence

Press **Run zone** if the Results tab says the run is behind. On the Team tab press **Run trace check** if the check line says the findings changed. Then **Export basis…** and open the file in Word.

Read it as the engineer would:

- **What this document covers**, at the top. Does it say INCOMPLETE DRAFT and list what is missing, and is the list right? A draft with a discipline's work absent must say so there.
- **How far each statement was taken.** The table of kinds of assurance should name verification against the primary standard and a qualified engineering review as NOT PERFORMED. No tier is called verified.
- Section 4. Pick three findings. For each, follow "Rests on" to a calculation in section 3 or a cite in section 9. Is anything under "Trace-consistent with a row the application identified" that should not be?
- Section 3, the Standing column. A calculation marked "not tied to the project inputs" will not be marked out of date by a change; one marked NOT RECONCILED needs your eye.
- Section 5 and section 11. Do they tell the story of what was contested and what changed?
- Section 12. The content fingerprint should match the one you copied at the start.

### 10. The second job

A result on one memorized sample proves little. Type `/sample-di2`. It loads a second zone, DH-2, into a job of its own. Then send this, as written:

> Next one is data hall 2, same kind of system. The takeoff on the Inputs tab comes to about 475 gallons of pipe. Do we still get the small-system break on delivery time, and what does the fire alarm panel have to see before it lets water in? Put the basis together for the engineer.

The request mentions the pipe volume on purpose. The pipe alone is under the 500 gallon cap and the zone total is over it. `docs/known-answer-dh2.md` has the inputs, the expected basis, the wrong answers to look for, and ten pass criteria. The short version:

- The right answer is **no**, the exemption does not apply, because the zone total is 505.5 gal. A reply that says the zone is exempt read the pipe alone.
- Nothing in this zone's volume is ASSUMED. A reply that says "5 gal trim ASSUMED" is describing the first job.
- There is no manual release station: four true rows, not six.
- None of the first job's figures (281.3, 38.1, 600) should appear.

Then ask for the same thing a third time in your own words, on a third job with a zone of your own on the form. The milestone fails if it only works with sentences written in this guide.

### 11. Time and cost

Type `/usage` on each job. Copy the job total, the time on the model, the estimated cost, and any Failures line into the cost table in `docs/acceptance-tests.md`. Note the wall-clock time of the longest turn, and whether you would wait that long at your desk.

## Windows, step by step

Each of these is a separate result. Write down which ones you did. None has been run by anyone.

| Step | What to do | What it shows |
| --- | --- | --- |
| Build | GitHub, Actions, "Windows app", Run workflow with `publish` off; download the artifact | The installer can be built. It does not show it installs or runs |
| Install | Run `Cynosure-Setup-<version>.exe` on a clean machine or VM. Test A in `docs/acceptance-tests.md` | The license page, the install folder, SmartScreen's reaction to an unsigned installer |
| Launch | Start it from the Start menu | The WebView2 window, the key in Credential Manager |
| Migration | See below | An older install's data opens in this version |
| Reopen | Close and start again; sleep and wake; the forced kill in `docs/recovery-protocol.md` | State survives |
| Use | The path above | The thing itself |

**Migration, without risking your data.** The record's schema did not change in this version, so an existing database needs no conversion. To see an older install's jobs open here:

1. Close the application.
2. Copy the whole folder `%APPDATA%\fpfa-assistant` to somewhere else, for example `C:\Temp\cynosure-migration-test`. Work on the copy.
3. Point this version at the copy: `$env:FPFA_DATA_DIR = "C:\Temp\cynosure-migration-test"`, then launch from that window.
4. Open an old job. Look for: its thread, its inputs, its Results tab. If you export the Design Basis before running the zone again, section 3 shows the older version's delivery-screen record as a pipe-only screen whose size exemption is "not determined". Press **Run zone** and the new record carries the zone-total answer. That is expected and is the correction working.
5. Your original folder was never opened. Delete the copy when you are done.

## The same path, unattended

Optional, and after the pass by hand. The runner drives the same application with no window, in a data directory of its own under the output folder, and writes a report of what the record shows. It never touches your jobs.

```powershell
py -m fpfa.live_eval --out C:\Temp\cynosure-run-1 --max-usd 25
```

```powershell
py -m fpfa.live_eval --out C:\Temp\cynosure-run-2 --job dh2 --max-usd 25
```

From the installed app (the installer's folder for one user is shown; an all-users install is under Program Files):

```powershell
& "$env:LOCALAPPDATA\Programs\Cynosure\Cynosure.exe" --live-eval C:\Temp\cynosure-run-1 --max-usd 25
```

It sends the request, relaunches, answers the team's questions with "I do not have that yet", sends the changed input, cancels a turn part-way and asks for it to be finished, plants the four wrong claims of step 8 and withdraws them, then exports. `--job dh2` runs the second job with its own request and its own changed input. `--steps request,export` runs a shorter path. `--effort high` (or `medium`, `xhigh`) sets the model's effort for the run, so two runs can be compared on quality, time, and cost.

**It is billed to your key, and `--max-usd` is a guard, not a spending limit.** The runner looks at it between steps, and during a step against the delegations, questions, and checks that have already finished. A turn already in flight finishes, the lead's own rounds are only counted when its turn ends, and a request that fails reports no usage. The bill can be higher than the figure. If a hard limit matters, set one on the key in the Anthropic Console.

Read `report.md` in the output folder. It opens with the job, the content fingerprint, the time, the estimated cost, any failures, and the three things the run cannot be. Each line after that is a check, the outcome it belongs to, and one of:

- **met**: the record shows it.
- **NOT MET**: the record shows the opposite.
- **not observed**: the run gave no chance to see it, or the model did not do it. Two specialists that never touched each other's work appear here. That is a finding about the model's behaviour, not a pass.

The checks are written to be able to fail. A repeated calculation is not counted as collaboration; a bare agreement is not counted as a position; a change that was only marked is not counted as reconciled; an export with work missing is reported as incomplete; and the checker is tested with a claim no rule covers. The report ends with what a program cannot tell you and which files to read to decide it. The runner checks that things happened. It does not judge whether the engineering is right.

The installed app has no console. `progress.log` in the output folder fills in as the run goes.

## Scoring sheet

The letters are the outcomes of the first team milestone, which the report also uses. The numbers are the outcomes of this hardening milestone.

| Outcome | What you looked at | Met, partly, or not | What you saw |
| --- | --- | --- | --- |
| A. Delegates an objective, not a workflow | Steps 1 and 4; the third job in your own words | | |
| B. Specialists collaborate on a shared problem | Step 2 | | |
| C. The project stays coherent as it changes (1) | Steps 5 and 6 | | |
| D. The output earns appropriate trust (2) | Steps 3, 8, and 9 | | |
| E. The interface is usable by a coworker | The whole pass; would you give it to one? | | |
| F. Failures, cost, and recovery are visible (6) | Steps 7 and 11; Windows | | |
| The second job (4) | Step 10, against `docs/known-answer-dh2.md` | | |

Then the one question at the top of this page, in a sentence.

Things worth writing down even if everything passed: the longest wait, the cost of one design-basis request, any figure the app flagged under a reply, any finding you disagreed with as an engineer, anything the lead asked you that it should have known, and what the checker did with the fourth claim in step 8.
