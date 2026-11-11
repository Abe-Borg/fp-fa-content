# Acceptance tests A through E: protocol and results

The app is named +Cynosure. Its installer is `Cynosure-Setup-<version>.exe` and its exe is `Cynosure.exe`.

The plan of record (`docs/prototype-plan.md`, section 4) names five acceptance tests. This file is how to run each one, what passes, and where the results go. Tests C and D have their own protocol in `docs/recovery-protocol.md`; this file points there and keeps their results in one place with the others.

Everything that can run without a Windows machine or an API key has run and is marked below. Everything else needs the project owner on a Windows machine with a saved key, and is marked **Not run** until then.

The team milestone (a plain objective, a real dependency between the specialists, a job that stays coherent as it changes, an output that says how far it can be trusted) has its own path in `docs/live-evaluation.md`. That path is the one to run with the live model. The section "What was tested, what was simulated, and what is unrun" below is the plain account of where it stands. Nothing in this repository has been run against the live model.

**Five statuses, kept apart.** Software hardening: done for the hardening milestone (`docs/milestone-hardening-handback.md`). Offline regression evidence: the four suites pass, every agent scripted. Installed Windows evidence: none. Live-model evidence: none. Engineering validation: none; no standard was opened and no qualified engineer has reviewed the basis (`docs/releasing-basis.md`). A pass in one says nothing about the next.

**Blocked, not failed.** Test A compares the export with `docs/known-answer-dh1.md`, which still has three items marked OWNER TO CONFIRM. Until the owner confirms or edits them, Test A cannot be passed or failed; it is blocked. The second job (`docs/known-answer-dh2.md`) is blocked for acceptance the same way: its inputs were chosen for the test and wait for the owner. Both can be run; neither run is an acceptance result until then.

## Before you start

1. **Get the installer.** Two ways:
   - **Build without a release.** On GitHub, Actions, "Windows app", Run workflow, pick the branch, leave `version` empty, turn `publish` off, Run. When it finishes, open the run and download the artifact `Cynosure-windows-<version>-<sha>`. It holds `Cynosure-Setup-<version>.exe` and `Cynosure-windows-<version>.zip`. Nothing is tagged or released.
   - **Release.** Push the tag `app-v<version>` where `<version>` equals `__version__` in `app/fpfa/__init__.py`, or run the same workflow with `publish` on. The release carries both files.
2. **A clean Windows machine or VM.** No Python installed, no earlier copy of the app, no saved key. Windows 10 or 11, 64-bit. Note its edition and build (Settings, System, About).
3. **An Anthropic API key** for the owner's account. It is typed into Settings on the machine and nowhere else.
4. **`docs/known-answer-dh1.md` confirmed.** Three items are marked OWNER TO CONFIRM. Test A compares the export against that page, so confirm or edit them first. Until then Test A is blocked. The coding agent did not choose them for you.

## Test A. Clean Windows install

What passes: install on a clean machine, open the sample, load the skills, run the DH-1 tool plan, export. Figures match `docs/known-answer-dh1.md` section 2. Runtime and dependency versions recorded.

1. Run `Cynosure-Setup-<version>.exe`. Expected: the second page shows the license (PolyForm Shield License 1.0.0) under a short summary, and Next stays disabled until **I accept the agreement** is selected. Accept it, then accept the defaults. Note the install time and the install folder. Expected in the install folder: `Cynosure.exe`, `LICENSE.txt`, and `THIRD-PARTY-NOTICES.txt`.
2. Start +Cynosure from the Start menu. Expected: the chat-first window opens maximized in the Warm Clay colour scheme with a dark title bar, no error, and the status line shows the key is not saved. The window is drawn by Microsoft Edge WebView2, which Windows 10 and 11 carry. If the page opens in a browser tab instead of the app's own window, WebView2 is missing or broken on that machine: note it under failures, and the app still works in the tab.
3. ⋯ menu, **About and versions**. Copy the version lines into the versions table below (the Copy button takes the whole box). The box opens with the name, the copyright line, and the license in brief, then lists the app version and whether it is frozen, the model id, Python, Windows, each dependency's version, the content pack version and folder, the data directory, and the record schema. A packaged app reports `anthropic`, `python-docx`, `keyring`, `pywin32-ctypes`, `pywebview`, and `pythonnet` by version; `pyinstaller` reads "not installed" there, because the build tool is not bundled. The last line, `Window`, names the Edge engine version WebView2 is running.
4. Type `/sample-di` and press Enter. Expected: a new job named for the sample, the tool plan runs without a key, the thread shows the zone figures, and the job panel opens on the Results tab: the figures as tiles, each with its label, and the tool transcript under them.
5. Compare the figures with `docs/known-answer-dh1.md` section 2: pipe volume, fittings allowance, trim, zone total, delivery time, screen limit, releasing rows, density and area, hose, duration, nitrogen. Every figure and every label must match.
6. ⋯ menu, **Export draft Section 21 13 19…**. Expected: after the claim check, the Windows Save dialog asks where; a .docx is written there and opens in Word. Then **Export Design Basis and Open Questions…**. Expected: with no findings yet the export is allowed and section 3 lists the eight calculation records with the same figures.
7. Settings, paste the key, save. Expected: the status line says the key is saved. Note which key store the Settings dialog reports (Credential Manager on Windows).
8. Ask for a design basis in a plain sentence that names no specialist and no order. `docs/live-evaluation.md`, step 1, has one to use as written; then ask again in your own words on a second job. Expected: three pulsing dots and a line that says what the app is doing while it works, then the reply arriving in the thread as it is written, with a **Team** block under it written by the app, a line on the team beside the job name, and on the Team tab a plan, both specialists, and findings on the record. Compare the reply's content against sections 3 and later of the known answer, and the Team panel against section 7. Note what differs.
9. ⋯ menu, **Usage and cost**. Copy the job total, the time on the model, and the estimated cost into the cost table below.

Pass: steps 2, 4, 5, 6, and 8 as expected, and the versions table filled.

## Test B. Specialist collaboration

What passes: distinct FP, FA, and checker contributions on DH-1, **and evidence that the two specialists worked on a shared problem**. Every substantive exchange is a record row with sender, receiver, time, and content, visible in the window.

The request does not name a specialist, an order, or the check. An earlier version of this test told the lead which specialist to use for what and when to run the check. A pass on that showed only that the lead follows instructions.

1. On the Test A job, or a new one with a zone on the form, send the plain request in `docs/live-evaluation.md`, step 1.
2. Expected, on the Team panel:
   - WHERE THINGS STAND: an objective and steps the lead set, both specialists listed with what each did.
   - EXCHANGES BETWEEN AGENTS: a `brief` row from the lead to each specialist with what came back, and at least one row or finding that carries a fact from one specialist to the other: a `question` row with a real answer, or a finding by one that rests on the other's **finding** (open the finding and read "Rests on"). A finding that cites a calculation the other specialist ran first does not count when the citing specialist ran the same calculation itself: the record replays the first row, so it carries the other's name with nothing having passed between them.
   - FINDINGS: each finding names its author and the rows it rests on. At least one finding has a review by the specialist who did not write it, with a reason (open it and read "Reviewed by"). An agreement with no reason beside it does not count.
   - METHODS READ: each specialist that recorded findings read a skill before it did.
   - NOT YET RECONCILED is empty, or the lead's reply says what is open and why. HOW DISAGREEMENTS ENDED lists any objection with how it ended.
   - The check line says a trace check ran, and how many findings were consistent with a calculation record, a content-pack note, or a project input, and how many only with their author's own cite.
3. Export the Design Basis. Expected: "What this document covers" at the head, saying INCOMPLETE DRAFT with the list when work is missing; the table "How far each statement was taken" with the kinds of assurance, the last two marked NOT PERFORMED; section 4 with findings under the tier each earned; section 5 with the reviews and how each objection ended; section 8 with the exchanges by kind; section 10 with the trace check claim by claim; section 12 with the content fingerprint and the skills each contributor read.

Pass: step 2's first three bullets and step 3. A run with two contributions and no row that connects them does not pass, however good each contribution is. Neither does a run whose only connection is a replayed calculation or a bare agreement. Write down which it was.

Automated half, already passed with stand-in model calls: `app/tests/test_team.py`, `test_team_protocol.py` (what each agent is told and what its tools do), and `test_scenario.py` (the whole job, scripted). These show the application's side. They do not show what the live model chooses to do.

## Test C. Continuity

See `docs/recovery-protocol.md`, Test C. Automated half passed (`app/tests/test_recovery.py`). Manual steps not run.

## Test D. Recovery

See `docs/recovery-protocol.md`, Test D: forced kill, a second copy while the first runs, sleep and wake, hibernate. Automated half passed, including a real process kill. Manual steps not run.

## Test E. Usability and cost

What passes: Activity collapsed by default, handoffs inspectable, cancel works, blockers visible, export reviewable. Cost per DH-1 task measured from the usage totals.

1. On a fresh launch, expected: Activity is not shown until a job runs; the job panel is closed; the top bar holds the job-list button, the job panel's three tabs (Inputs, Results, Team), and ⋯; the thread shows the welcome with its three start cards; and the only other buttons are New chat, Settings, Mode, and Send. Close the window with the panel open on a tab and the job list hidden, and start it again. Expected: it opens the way it was left.
2. Responsiveness, the reason the window moved to WebView2. With the Test A job open and a long reply in the thread: drag the window's edge to resize it, open and close the job panel, drag the panel's edge, give the panel the thread's place and bring the thread back, switch to another job and back, scroll the thread with the wheel while a reply is arriving, and change the colour scheme in Settings. Expected: each responds without a visible pause, the thread stays where you scrolled it while words arrive, and Latest brings it back to the end. Note anything that stutters under failures, with the machine's display scale.
3. After Test B, expected: every exchange row opens its detail on the Team panel; a question for the designer can be answered in place; every finding opens to what it rests on and how far the check took it; the Design Basis export can be read in Word and traced to the record. With the keyboard alone: Tab reaches the line beside the job name, the Team tab's button, each group of findings, each finding, each exchange row, and the answer box; Enter or Space opens them.
4. Cancel: ask a long question, press **Stop** beside Send (or **Cancel running job** on the Team tab) while Activity shows `running`. Expected: the turn stops at its next round, the thread shows a "Cancelled" line, Activity shows `cancelled`, and **Usage and cost** still lists the cancelled turn with what it spent.
5. Cost and time: ⋯ menu, **Usage and cost**, or from a source checkout `py -m fpfa.usage_report --db "%APPDATA%\fpfa-assistant\fpfa.db"`. The report lists each model context (lead turns with their delegations and the questions between specialists inside, narrations, trace checks) with how long each took, the job total, the time on the model, and the estimated dollars at the rates printed on the second line. Fill the cost table below with one plain design-basis request and with the full path in `docs/live-evaluation.md`.

Pass: steps 1 through 4 as expected, and the cost table filled.

Automated half, already passed: `app/tests/test_usage.py` proves the events, the totals, and the report; `app/tests/test_team_ui.py` proves cancel end to end; `app/tests/test_prototype.py` proves the launch layout.

## How the figures are judged

- Numbers come from the calc tools. A figure in a reply that is not on a calculation record is a defect, however plausible. The app looks every figure in the lead's reply up, by number and kind of unit, and names under the reply any it cannot find, or finds only on an out-of-date row: a calculation an input changed under, the value an input had before it changed, a finding that is out of date or was replaced. A finding that still repeats an old number does not make it current. A reply with that note under it fails this line.
- The check is a trace check. It says whether a finding is consistent with the rows it cites. It does not open a standard, and a reply or an export that says a standard was checked or verified fails. No tier is a verification, and the export names verification against the primary standard and a qualified engineering review as not performed.
- The size exemption is judged on the zone total. A reply, a finding, a tile, or an export that states it from the pipe alone fails.
- A design basis with work missing says so at its head. One that reads complete while a calculation has no specialist's finding fails.
- Release is the detection leg AND P, the pressure drop from sprinkler operation. Low air is supervisory only and is never a release input; a reply or an export that says otherwise fails (`docs/releasing-basis.md`).
- Labels stay distinct: calculated, ASSUMED, use best judgment. A delivery time is an optimistic screen, not a listed water-delivery-time calculation, and the reply must say so.
- The double-interlock draft section is 21 13 19. A reply or export that says 21 13 16 for the sample zone fails.
- NFPA 13-2025 is the delta baseline. A cite without an edition fails.

## Results

### Where each test stands

| Test | Automated half | Manual half (Windows) | Date | Notes |
| --- | --- | --- | --- | --- |
| A. Clean Windows install | Figures locked by `calcs/fp` and `app/tests/test_prototype.py`; versions by `app/tests/test_usage.py`; packaging config checked | **Blocked**, and not run | | Blocked on the three OWNER TO CONFIRM items in the known answer. Needs the installer and the clean machine |
| B. Specialist collaboration | Passed with stand-in model calls: `app/tests/test_team.py`, `test_team_protocol.py`, `test_scenario.py`; what counts as collaboration and what does not, `test_hardening.py` | Not run | | Needs a key. The plain request, not the old one that named the specialists |
| C. Continuity | Passed, `app/tests/test_recovery.py` | Not run | | Protocol in `docs/recovery-protocol.md` |
| D. Recovery | Passed, including a real process kill | Not run | | Protocol in `docs/recovery-protocol.md` |
| E. Usability and cost | Passed, `app/tests/test_usage.py`, `test_team_ui.py`, `test_desk_team.py`, `test_prototype.py`; the Team panel in Chromium, `test_web.py` | Not run | | Needs a key for the cost figures |
| Team milestone path (`docs/live-evaluation.md`) | Simulated end to end, `app/tests/test_scenario.py`; the unattended runner with a scripted model, `test_live_eval.py` | Not run | | The live model has not been called once |
| The second job (`docs/known-answer-dh2.md`) | Its figures locked by `test_hardening.py`; `/sample-di2` loads it | **Blocked** for acceptance, and not run | | Its inputs wait for the owner's confirmation. The runner takes `--job dh2` |

### What was tested, what was simulated, and what is unrun

**Tested** means the real code ran and the result was checked, with no model involved. **Simulated** means the real application ran with every model call replaced by a script written in advance. **Unrun** means nobody has done it.

| What | Standing | Where |
| --- | --- | --- |
| Calc kernels, the DH-1 figures, the pack lint (no low-air release wording, no standards text) | Tested | `calcs/fp`, `calcs/fa` |
| The releasing truth table row by row: low air alone never releases; release needs the detection leg and P | Tested | `app/tests/test_releasing_basis.py` |
| Inputs on the record with who supplied each; a changed input marks exactly what used it; a re-run clears it | Tested | `test_coherence.py` |
| A basis field stated in chat reaching an empty field on the Inputs tab; a basis field the designer emptied leaving the record, with what rested on it out of date | Tested, with the lead's `set_input` called directly and no model | `test_coherence.py` |
| A calc that took a figure from an alternative marked as an alternative, with the tool result saying so; a figure two takeoffs share tied to the one on the project inputs | Tested | `test_coherence.py` |
| A cite looked up in the content pack; a wrong figure beside a matching author's note is caught; an out-of-date finding is not judged; tiers | Tested, with a checker stand-in that says Supported to everything | `test_checker.py` |
| The export gate, the Design Basis layout, the Section 21 13 19 guard against a run the form moved past | Tested | `test_checker.py`, `test_design_basis.py`, `test_desk_team.py` |
| The figures in a reply looked up on the record | Tested on written replies | `test_desk_team.py` |
| Retries with the API's retry-after, the effort field off by default | Tested against a fake transport | `test_desk_team.py`, `test_streaming.py` |
| Kill and relaunch, the instance lock, sleep and wake as a clock gap | Tested, with a real process kill | `test_recovery.py` |
| The window's page: menus, thread, the job panel and its three tabs, the form, the figures of a run, and the Team tab with an answer typed into it | Tested in Chromium on Linux | `test_web.py` (`e2e.mjs`, `e2e_team.mjs`) |
| The Results tab's figures held to the tool output and to the narrative, label for label; the window's layout remembered between runs | Tested | `test_results_panel.py`, `frontend/tests/layout.test.ts` |
| A stale, replaced, or basis-free finding cannot keep an old figure current in a reply; a figure is matched with its unit | Tested on written replies | `test_hardening.py` |
| The size exemption on the recorded row, the narrative, the tile, and both documents is the zone-total answer; a pipe-only screen gives none | Tested, including the 475 gal pipe and 505.5 gal zone case | `test_hardening.py`, `test_prototype.py` |
| A calculation made by other calc code is out of date; one on a tool the record does not track says it cannot be reconciled | Tested | `test_hardening.py` |
| A finding that departs from the releasing rule, or holds a figure only as another quantity, is not supported whatever the checker says | Tested, with a checker stand-in that says Supported to everything | `test_hardening.py` |
| A design basis with a calculation no finding speaks for says INCOMPLETE DRAFT at its head; the kinds of assurance name the two never performed | Tested | `test_hardening.py` |
| A failed delegation, consult, turn, or trace check keeps the usage that had finished and is marked failed; retries are counted | Tested with scripted failures | `test_hardening.py`, `test_scenario.py` |
| Which contributor read which skill, before or after its findings, and whether a cite it recorded is one the skill holds | Tested with scripted reads | `test_hardening.py` |
| The pack lint and the app's detector flag the same sentences, including the paraphrases the first lint missed | Tested | `calcs/fp/test_pack_content_lowair.py`, `test_releasing_basis.py` |
| A lead that plans, records what the designer said, delegates, reconciles, and checks | **Simulated** | `test_team_protocol.py`, `test_scenario.py` |
| One specialist asking the other, objecting, and the author revising | **Simulated** | `test_team_protocol.py`, `test_scenario.py` |
| A job closed, reopened, changed, interrupted, and exported | **Simulated** | `test_scenario.py` |
| The unattended evaluation runner and its report, including a checker that approves everything being caught by a planted claim | **Simulated** | `test_live_eval.py` |
| Any request to the live model: whether it plans, delegates without being told, asks, objects, revises | **Unrun** | `docs/live-evaluation.md` |
| Time and cost of a real design-basis request | **Unrun** | `/usage` on a live job |
| The lead and specialist role files as prompts: whether the model follows them | **Unrun** | live only |
| The trace check's own judgment (the checker stand-in never disagrees). The runner's probe step and step 8 of the guide are how to test it | **Unrun** | live only |
| Whether a live specialist reads a skill before it records findings, and follows it | **Unrun** | live only |
| The second job with the live model | **Unrun** | `--job dh2` |
| Any check of the engineering basis against NFPA 13, NFPA 72, FM DS 5-32, or a manufacturer's listing; any qualified engineer's review | **Not done** | `docs/releasing-basis.md`, section 8 |
| The skipped tests: 13 `calcs/fa` code-quote tests (no code text in the repository) and the FP kernel reproduce check (needs the kernel source folder) | **Skipped** in every run here | `calcs/fa`, `calcs/fp/test_kernel_reproduce.py` |
| The held electric/pneumatic draft under `calcs/fp/draft/` | **Not run** by these suites, imported by nothing | held work |
| The test workflow on GitHub (`.github/workflows/tests.yml`) | **Unrun** until the pull request that adds it | new in this milestone |
| The Windows installer, WebView2 window, Credential Manager, sleep and hibernate on real hardware | **Unrun** | Tests A, C, D, E above |
| The pictures in the README | Taken from the simulated scenario | `docs/screenshots/` |

### Versions (from About and versions on the test machine)

| Item | Value |
| --- | --- |
| App version and build (frozen or source) | |
| Windows edition and build | |
| Python | |
| anthropic | |
| python-docx | |
| keyring | |
| pywin32-ctypes | |
| pywebview | |
| pythonnet | |
| Window (WebView2 engine) | |
| Content pack version | |
| Record schema | |
| Installer file and size | |
| Install time | |

### Cost per task (from Usage and cost)

Rates are the dated snapshot printed by the report. Record the date it prints. If the report has a Failures line, copy it: the cost is then a floor, because a failed request reports no usage.

| Task | Model contexts | Input tokens (fresh / cache write / cache read) | Output tokens | Estimated cost | Wall time |
| --- | --- | --- | --- | --- | --- |
| One plain design-basis request (`docs/live-evaluation.md`, step 1) | | | | | |
| The whole path in `docs/live-evaluation.md` | | | | | |
| The second job's request (`docs/live-evaluation.md`, step 10) | | | | | |
| Narrated zone run (`/run` with Ask Claude on) | | | | | |

### Failures and limits found

| Where | What happened | Severity | Follow-up |
| --- | --- | --- | --- |
| | | | |
