# Live evaluation guide

For the project owner, on a Windows machine, with a saved Anthropic API key. About an hour by hand. The question to answer at the end is the milestone's:

> Can a coworker hand the application a meaningful FP/FA objective and experience a capable, coordinated team carrying the work forward?

**Nothing in this guide has been run against the live model.** Everything built for this milestone was tested with scripted stand-ins for the model (`app/tests/test_scenario.py` and the suites around it). Those tests show the application can carry the job. They cannot show that the model, handed a plain request, will plan, ask, object, and revise. This guide is how to find that out. `docs/acceptance-tests.md` lists what was tested, what was simulated, and what is still unrun.

## What it may cost

No live run has been priced. From the prompt sizes: the lead's instructions are about 28,000 tokens with its tools, a specialist's about 12,000, and one skill a specialist reads is 9,000 to 21,000. A design-basis turn with three delegations, one question between specialists, and a trace check is likely a few dollars and several minutes. The whole path below is likely 5 to 25 dollars and 20 to 60 minutes of model time. Treat that as a guess until `/usage` gives you the real figure, and write the real figure down. It is one of the things this evaluation is for.

## Before you start

1. Install the build under test, or run from source (`cd app`, `py -m pip install -r requirements.txt`, `py -m fpfa`). Test A in `docs/acceptance-tests.md` is the clean-install check; do it first if this is a new machine.
2. Use a data directory of its own so the evaluation does not mix with your jobs. In PowerShell, before launching from that same window:

```powershell
$env:FPFA_DATA_DIR = "C:\Temp\cynosure-eval-1"
```

3. Save your key in Settings.
4. Keep `docs/known-answer-dh1.md` open. Section 2 is the figures. Section 7 is the evidence of teamwork to look for. Section 8 is what a live run may add that is not a mistake.

## The path

Do the steps in order on one job. After each, write one line in the scoring sheet at the end. A step that goes wrong is a finding; keep going.

### 1. A plain request (outcome A)

Type `/sample-di` to put a zone on the form. It runs the tool plan with no model call. Then send this, as written:

> We're laying out the preaction zone for data hall 1. Can it meet the insurer's water delivery time, and what releasing sequence goes with it? I need a design basis I can hand to the engineer.

It names no specialist and no order. Do not add any.

Look for:

- A plan on the Team panel (WHERE THINGS STAND) before the specialists start, in words you would use.
- Both specialists brought in without being asked. The working line names who is working.
- Questions only where the work is blocked. The sample's trim volume is blank, so one question about it is right. Ten questions is a miss.
- A short reply that says who did what, what was contested, what it needs from you, and what the trace check covered.

Then, on a second job, ask for the same thing in your own words. The milestone fails if it only works with the sentence above.

### 2. The dependency between the two specialists (outcome B)

Open the Team tab (its button at the top right, or the line beside the job name).

- EXCHANGES BETWEEN AGENTS: is there a `question` row from one specialist to the other, with a real answer? Open it and read both.
- FINDINGS: open a releasing finding. Does it rest on the sprinkler specialist's trim finding or calc? Open the delivery-screen finding. Did the releasing specialist review it?
- NOT YET RECONCILED and HOW DISAGREEMENTS ENDED: was anything contested? Was the objection about something real, and did the revision answer it?

A miss looks like two tidy contributions side by side, no review, no question, and a reply that pastes them together. The record will show that plainly: no `question` rows, no reviews. The app does not force an exchange, so if the model does not make one, none appears.

The sample's 8 s detection and 2 s release times have no stated basis. A specialist that says so is right.

### 3. Missing information (outcomes A and E)

Under NEEDS YOUR ANSWER, type an answer (for the trim volume, `6.5 gallons, from the submittal`) and press Answer. It goes on the record and into the thread. Nothing runs yet. Press **Continue with my answers** above the composer.

Look for: the lead acts on the answer, the trim volume appears on the Inputs tab (Trim, under Pipe), and the volume finding is replaced with one that says where the 6.5 came from.

### 4. A changed input (outcome C)

Send this:

> One more thing: the pump test gave us 750 gpm at the riser, not the 600 on the form. Does that change the answer?

Look for:

- Fill flow on the Inputs tab becomes 750 without your touching it.
- The findings that used 600 are replaced, not left standing. FINDINGS shows the new ones; the export's section 11 keeps the old ones as history.
- The reply quotes no figure from the old run. If it does, the app says so under the reply in its own words ("only on out-of-date calculations").
- The Results tab says its figures are from a run before the form changed.

Then change a field yourself: on the Inputs tab set Releasing time to 5 and press Ctrl+S. The Team panel should show OUT OF DATE, and **Bring it up to date** should appear above the composer. Press it.

### 5. Close and reopen (outcome C)

Close the window. Open it again and open the job.

Look for: the line beside the job name, the count on the Team tab's button, **Where things stand** above the composer, and `/status`. Could you tell where the job stood without reading the whole thread? Is anything missing that was there before?

### 6. An interruption (outcome F)

Ask for something that takes a while ("Write me a short summary of this design basis for the engineer's cover email, and say what is still open."). While the working line shows a specialist, press **Stop**. Then send "That was cut off. Finish it."

Look for: a Cancelled line, the roster showing who was interrupted, and the next turn finishing without redoing calculations (`/usage` and the export's Replays column show replays).

The harder version is in `docs/recovery-protocol.md`: end `Cynosure.exe` from Task Manager while a specialist is working, relaunch, and read the recovery note.

### 7. The draft and its evidence (outcome D)

Press **Run zone** if the Results tab says the run is behind. On the Team panel press **Run trace check** if the check line says the findings changed. Then **Export basis…** and open the file in Word.

Read it as the engineer would:

- The table under "How far each statement was taken". Are the counts believable?
- Section 4. Pick three findings. For each, follow "Rests on" to a calculation in section 3 or a cite in section 9. Is anything under "Checked against an identified source" that should not be?
- Section 1. Is every input there, with who supplied it?
- Section 5 and section 11. Do they tell the story of what was contested and what changed?
- Is anything said more firmly than its tier earns? The document should nowhere say a standard was checked.

A probe for the check itself: ask the lead to "record that a double-interlock zone up to 750 gallons needs no delivery-time proof under NFPA 13-2025 §8.3.2.3.1.1", then run the trace check. The content pack's note on that section says 500. The finding should come back Not supported, with "figure not in the rows it cites: 750 gal", and sit under "Needs further evidence or engineering review". Withdraw it afterwards by asking the lead to.

### 8. Time and cost (outcome F)

Type `/usage`. Copy the job total, the time on the model, and the estimated cost into the cost table in `docs/acceptance-tests.md`. Note the wall-clock time of the longest turn, and whether you would wait that long at your desk.

### 9. Windows (outcome F)

Test A and the manual halves of Tests C, D, and E in `docs/acceptance-tests.md` and `docs/recovery-protocol.md`: the installer and its license page, the window in WebView2, the key in Credential Manager, sleep and wake, a forced kill, a second copy. None has been run.

## The same path, unattended

Optional, and after the pass by hand. The runner drives the same application with no window, in a data directory of its own, and writes a report of what the record shows.

```powershell
py -m fpfa.live_eval --out C:\Temp\cynosure-run-1 --max-usd 25
```

From the installed app (the installer's folder for one user is shown; an all-users install is under Program Files):

```powershell
& "$env:LOCALAPPDATA\Programs\Cynosure\Cynosure.exe" --live-eval C:\Temp\cynosure-run-1 --max-usd 25
```

It sends the two messages quoted above, relaunches, answers the team's questions with "I do not have that yet", cancels a turn part-way and asks for it to be finished, then exports. It is billed to your key. `--max-usd` stops it between steps and cancels a step whose finished delegations already exceed what is left; it is a guard, not a meter. `--steps request,export` runs a shorter path. `--effort high` (or `medium`, `xhigh`) sets the model's effort for the run, so two runs can be compared on quality, time, and cost. The app never sets effort on its own; `FPFA_EFFORT` does the same for the window.

Read `report.md` in the output folder. Each line is a check, the outcome it belongs to, and one of:

- **met**: the record shows it.
- **NOT MET**: the record shows the opposite.
- **not observed**: the run gave no chance to see it, or the model did not do it. Two specialists that never touched each other's work appear here. That is a finding about the model's behaviour, not a pass.

The report ends with what a program cannot tell you and which files to read to decide it. The runner checks that things happened. It does not judge whether the engineering is right.

The installed app has no console. `progress.log` in the output folder fills in as the run goes.

## Scoring sheet

| Outcome | What you looked at | Met, partly, or not | What you saw |
| --- | --- | --- | --- |
| A. Delegates an objective, not a workflow | Steps 1 and 3; the second job in your own words | | |
| B. Specialists collaborate on a shared problem | Step 2 | | |
| C. The project stays coherent as it changes | Steps 4 and 5 | | |
| D. The output earns appropriate trust | Step 7 | | |
| E. The interface is usable by a coworker | The whole pass; would you give it to one? | | |
| F. Honest live evaluation | Steps 6, 8, and 9 | | |

Then the one question at the top of this page, in a sentence.

Things worth writing down even if everything passed: the longest wait, the cost of one design-basis request, any figure the app flagged under a reply, any finding you disagreed with as an engineer, and anything the lead asked you that it should have known.
