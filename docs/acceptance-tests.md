# Acceptance tests A through E: protocol and results

The app is named +Cynosure. Its installer is `Cynosure-Setup-<version>.exe` and its exe is `Cynosure.exe`.

The plan of record (`docs/prototype-plan.md`, section 4) names five acceptance tests. This file is how to run each one, what passes, and where the results go. Tests C and D have their own protocol in `docs/recovery-protocol.md`; this file points there and keeps their results in one place with the others.

Everything that can run without a Windows machine or an API key has run and is marked below. Everything else needs the project owner on a Windows machine with a saved key, and is marked **Not run** until then.

The team milestone (a plain objective, a real dependency between the specialists, a job that stays coherent as it changes, an output that says how far it can be trusted) has its own path in `docs/live-evaluation.md`. That path is the one to run with the live model. The section "What was tested, what was simulated, and what is unrun" below is the plain account of where it stands. Nothing in this repository has been run against the live model.

**Five statuses, kept apart.** Software hardening: done for the hardening milestone (`docs/milestone-hardening-handback.md`) and for six of the defects the acceptance test of 0.2.0 found (version 0.3.1, `NEXT-STEPS.md`). Offline regression evidence: the four suites pass, every agent scripted. Installed Windows evidence: none. Live-model evidence: none for this version. Engineering validation: none; no standard was opened and no qualified engineer has reviewed the basis (`docs/releasing-basis.md`). A pass in one says nothing about the next.

**One live run exists, on an older version, and it is not ours.** An acceptance test of version 0.2.0 (run CYN020-20261111) called the live model through the released build's source on Linux. It is that tester's reported evidence about 0.2.0. Nothing in it was run here, none of its counts are repeated here as runs made here, and it says nothing about 0.3.0 or 0.3.1, whose role files and checks differ. `NEXT-STEPS.md` reviews each of its findings against the source and lists what still has to be run on Windows and with the live model.

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

1. With separate written permission to use the app, run `Cynosure-Setup-<version>.exe`. Expected: the second page shows the Proprietary License Notice under a short summary, states that acceptance grants no permission to use the app, and Next stays disabled until **I accept the agreement** is selected. Accept it, then accept the defaults. Note the install time and the install folder. Expected in the install folder: `Cynosure.exe`, `LICENSE.txt`, and `THIRD-PARTY-NOTICES.txt`.
2a. Before you run anything, compare identities. ⋯ menu, **About and versions**: note the line that reads `Content fingerprint …, calc code …`. Get the same line from a seed built on Linux from the commit the installer was built from: from `app/`, `python packaging/build_app.py --seed-only --seed <folder> --seed-version <the installer's seed version>`, then `FPFA_CONTENT_ROOT=<folder> python -m fpfa --versions`. (The seed is compared with a seed because it may leave folders out that a source checkout holds.) Expected from 0.3.1: both values are equal, though the installed files have Windows line endings. If either differs, write both lines under failures: a calculation recorded on this install would then read as out of date after a content update that changed nothing. This step has not been run; the identity fix rests on a test made on Linux.
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

1. On a fresh launch, expected: Activity is not shown until a job runs; the job panel is closed; the top bar holds the job-list button, the job panel's three tabs (Inputs, Results, Team), and ⋯; the thread shows the welcome with its three start cards; and the only other buttons are New chat, Settings, and Send. Close the window with the panel open on a tab and the job list hidden, and start it again. Expected: it opens the way it was left.
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
| Manual app-update check: numeric version ordering, content/draft/prerelease filtering, pagination, failure and retry, duplicate-click protection, and authenticated state updates | **Tested**, with fixture release responses; no model involved | `app/tests/test_app_update.py` |
| Settings update control in Clay and Linen at 150% display scale: keyboard activation, checking state, close/reopen during a check, error and current states, download link | **Tested** in Linux Chromium with fixture release results and a stand-in download page | `app/tests/test_app_update_browser.py`; screenshot output via `FPFA_UPDATE_SCREENSHOT_DIR` |
| App-release lookup in this connected environment | **Tested** from Linux on 2026-11-12; the 0.3.1 checkout found stable app release 0.3.2. The repository is private; this does not establish unauthenticated access from an installed copy | `fpfa.app_update.check_for_app_update()` |
| App-update download in the installed Windows WebView2 window and running the newer installer | **Unrun** | Settings → About +Cynosure → Check for updates |
| Calc kernels, the DH-1 figures, the pack lint (no low-air release wording, no standards text) | Tested | `calcs/fp`, `calcs/fa` |
| The releasing truth table row by row: low air alone never releases; release needs the detection leg and P | Tested | `app/tests/test_releasing_basis.py` |
| Inputs on the record with who supplied each; a changed input marks exactly what used it; a re-run clears it | Tested | `test_coherence.py` |
| A basis field stated in chat reaching an empty field on the Inputs tab; a basis field the designer emptied leaving the record, with what rested on it out of date | Tested, with the lead's `set_input` called directly and no model | `test_coherence.py` |
| (Superseded for new jobs by FA Lead's ruling: a new job's basis starts blank. Still true of an older record that holds one.) A new job's NFPA 13 2025, NFPA 72 2025, and insurer FM recorded as starting values not confirmed by the designer, and said so by the lead's status block, a specialist's brief, the record as the team reads it, `/status`, the Team tab, the Design Basis, and the Section 21 13 19 export; typing a value or stating it to the lead confirms it, emptying a field does not; a later change to the starting values does not make an untouched one typed; correcting an older job's source leaves its calcs current; an edition hold and a run's flags never say the job states a starting value | Tested, with the lead's `set_input` called directly and no model. The Team tab's line was looked at in Chromium on Linux (Linen, device scale 2) on a job made in the page. Which edition and insurer a job should start with is not examined by anything here; it is the owner's open decision | `test_coherence.py` (`BasisStartingValueTests`) |
| Whether a live lead or specialist treats a basis starting value as unconfirmed, and whether a zone narration still writes the starting edition as the job's (the narrator is given the basis without the mark) | **Unrun** | live only |
| An input stated in chat on the form while the turn still runs; the card under the reply with Show and Undo; the lead's reason called the designer's words only when found in their messages; the field's mark; Undo putting back the old value and who supplied it (blank stays blank; an accepted hint stays ASSUMED and its edition HOLD stays), with the lead's row kept; typing during the turn kept over a fill; the stale-run note read from the run; Ask me first writing nothing until Apply, and Skip; the next turn told what became of each row | **Simulated**: a scripted lead calls `set_input`; the window's side is the real application | `test_chat_fill.py` |
| The same in the page: the card, Show with the focus in the field, the tag and Escape, Undo on the form, the Inputs tab's mark, the Ask me first setting, and Apply | **Simulated** lead, the page tested in Chromium on Linux | `test_web.py` (`e2e_fill.mjs`) |
| Whether the live lead calls `set_input` for an input the designer mentions in passing, and keeps from filling a field it only infers | **Unrun** | `python -m fpfa.live_eval` is the owner's to run |
| A calc that took a figure from an alternative marked as an alternative, with the tool result saying so; a figure two takeoffs share tied to the one on the project inputs | Tested | `test_coherence.py` |
| A cite looked up in the content pack; a wrong figure beside a matching author's note is caught; an out-of-date finding is not judged; tiers | Tested, with a checker stand-in that says Supported to everything | `test_checker.py` |
| The export gate, the Design Basis layout, the Section 21 13 19 guard against a run the form moved past | Tested | `test_checker.py`, `test_design_basis.py`, `test_desk_team.py` |
| The figures in a reply looked up on the record | Tested on written replies | `test_desk_team.py` |
| Retries with the API's retry-after, the effort field off by default | Tested against a fake transport | `test_desk_team.py`, `test_streaming.py` |
| Kill and relaunch, the instance lock, sleep and wake as a clock gap | Tested, with a real process kill | `test_recovery.py` |
| The window's page: menus, thread, the job panel and its three tabs, the form, the figures of a run, and the Team tab with an answer typed into it; on the Team tab, the sentence of what kind of checking this is read whole with its row closed, from where the other cards' text starts, and the row opened from the keyboard to the kinds of assurance | Tested in Chromium on Linux | `test_web.py` (`e2e.mjs`, `e2e_team.mjs`) |
| The screenshot tool for looking at the window: it shoots the scheme the app serves at the device scale asked for, and stops with nothing written when asked for another scheme | Tested in Chromium on Linux. Its argument checks need only Node.js | `test_web.py`, `ScreenshotToolTests` (`shoot.mjs`) |
| The Results tab's figures held to the tool output and to the narrative, label for label; the window's layout remembered between runs | Tested | `test_results_panel.py`, `frontend/tests/layout.test.ts` |
| A stale, replaced, or basis-free finding cannot keep an old figure current in a reply; a figure is matched with its unit | Tested on written replies | `test_hardening.py` |
| The size exemption on the recorded row, the narrative, the tile, and both documents is the zone-total answer; a pipe-only screen gives none | Tested, including the 475 gal pipe and 505.5 gal zone case | `test_hardening.py`, `test_prototype.py` |
| A calculation made by other calc code is out of date; one on a tool the record does not track says it cannot be reconciled | Tested | `test_hardening.py` |
| A finding that departs from the releasing rule, or holds a figure only as another quantity, is not supported whatever the checker says | Tested, with a checker stand-in that says Supported to everything | `test_hardening.py` |
| A design basis with a calculation no finding speaks for says INCOMPLETE DRAFT at its head; the kinds of assurance name the two never performed | Tested | `test_hardening.py` |
| A failed delegation, consult, turn, or trace check keeps the usage that had finished and is marked failed; retries are counted | Tested with scripted failures | `test_hardening.py`, `test_scenario.py` |
| Which contributor read which skill, before or after its findings, and whether a cite it recorded is one the skill holds | Tested with scripted reads | `test_hardening.py` |
| The pack lint and the app's detector flag the same sentences, including the paraphrases the first lint missed | Tested | `calcs/fp/test_pack_content_lowair.py`, `test_releasing_basis.py` |
| A checker reply that was cut off changes no finding, is logged as not finished with its usage, and is never the latest check; a record over eight claims is checked in batches; a claim a finished reply skips is not a "no" | Tested, with a checker stand-in that returns the cut-off reply the 0.2.0 acceptance run captured | `test_acceptance_report.py` |
| A finding may rest on a decision; a support id on no table is said to the model that wrote it | Tested | `test_acceptance_report.py` |
| The Section 21 13 19 claim check's usage is on the job's record whether the export was blocked or the request failed, and in the cost report | Tested, with a scripted check | `test_acceptance_report.py` |
| The calc-code identity and the content fingerprint are the same for a CRLF copy of the pack; a calculation run on that copy is current on the LF one | Tested on Linux, on a copy made for the test. **Not confirmed on a Windows install** | `test_acceptance_report.py` |
| With a checker that says Supported to everything: a figure in any known unit is held to its class; a statement the application can match nothing in is not in the first group; a fact a specialist wrote is not a project input | Tested | `test_acceptance_report.py` |
| A job that states another edition of a standard than a calculation's cites carries EDITION NOT RECONCILED before a rerun and after one, in the draft, the coverage gaps, the run's flags, `/status`, and the Team tab, and clears when the editions agree | Tested. It compares two labels; whether the rule is the same in both editions is not examined by anything here | `test_acceptance_report.py` |
| A zone total rounded by the caller cannot carry the trip time across its limit; the gas fill replays the one row | Tested | `test_hardening.py` |
| A zone run refuses a density, a base area, a fill flow, a supervisory fill, or a fill time of 0, and a blank area increase, hose, supervisory fill, or fill time, naming each in the form's words; the form keeps a 0 and a blank as typed; a 0 passed to the gas fill reaches the kernel and is refused there; the lead cannot record a 0 density | Tested | `test_acceptance_report_030.py`, `ZoneInputTests` |
| Unit conversion by the definitions alone; the 0.3.0 report's SI case gives 447.983 gpm and 1695.8 L/min with a calculation record for each; the lead records a figure given in another unit and keeps both; the designer's SI figure is refused in a field that takes US units, a specialist's call included; the reply audit reads a figure given in SI; the figure a conversion was given backs only its own unit, in the trace check and the reply audit | Tested; the specialist's calls are **simulated** | `test_acceptance_report_030.py`, `UnitConversionTests` |
| The checker's quoted cite and reason kept apart from the application's, on the Team tab, in the Design Basis, and in the lead's tool result; verdict lines in bold, in capitals, numbered "1)", or behind a list marker are read; Stop is heard between a check's requests | Tested, with checker replies written in the live checker's own form (the 0.3.0 report's diagnostic replay) | `test_acceptance_report_030.py`, `CheckerReasonTests` |
| The monthly spend cap, a spend limit the owner set, and a billing error are not sent again and say so in plain words; a retry-after is waited out whole up to 120 s, or the request stops; Stop ends a wait to send again; every request id and the workspace billed are kept on the job and counted in the cost report; a check run inside a turn is counted once in the time on the model | Tested against a fake transport that raises the errors the API documents. **No real limit was reached** | `test_acceptance_report_030.py`, `ApiClientTests` |
| A damaged record (truncated, its header zeroed, a text file) is named with its path, left byte for byte, and moved aside only on a yes, never deleted; the data directory is let go. A whole record another connection has locked is not called damaged: the launch ends with its path, changes nothing, and offers nothing to move, `--move-damaged-record` or not | Tested in-process, and the three damaged copies launched from the command line on Linux | `test_acceptance_report_030.py`, `DamagedRecordTests` |
| The Team tab follows the record while a job on the open job works, at most every two seconds | Tested with the desk's own progress listener and a finding written mid-job | `test_acceptance_report_030.py`, `LiveTeamTests` |
| Every rule that colours text reads at 4.5:1 on the background, the surface, and a raised card in all five schemes; the faint ink colours no text a reader needs. Text on the accent is left out: Warm Clay's white on terracotta is 3.1:1, an open decision | Tested by reading the stylesheet; the README pictures retaken | `test_acceptance_report_030.py`, `TextContrastTests` |
| The delivery tile prints the tool's fill time alone and its margin beside the verdict; the lead's instructions follow the owner's ruling on missing inputs | Tested | `test_acceptance_report_030.py`, `FillTimeTileTests`, `MissingInputPolicyTests` |
| Every module in the page's bundle is an npm package's, listed in `licenses.json` with its license text, or one of the page's own sources; any other, such as a helper Vite writes in, fails the page's build and is named. The committed page carries no modulepreload polyfill, which is Vite's code, while `licenses.json` lists no vite | Tested, the license plugin on stand-in bundles, and the committed page | `frontend/tests/licenses.test.ts`, `test_web.py` |
| No Mode menu and no `/mode`: a typed question goes out in the mixed mode and a zone narration in synthesis, whatever mode an older job saved; the explosion-control starter stays in synthesis | **Simulated**: the request a scripted client receives | `test_prototype.py` (`test_a_chat_turn_is_written_in_the_mixed_mode`, `test_a_zone_narration_is_written_in_the_synthesis_mode`) |
| A lead that plans, records what the designer said, delegates, reconciles, and checks | **Simulated** | `test_team_protocol.py`, `test_scenario.py` |
| One specialist asking the other, objecting, and the author revising | **Simulated** | `test_team_protocol.py`, `test_scenario.py` |
| A job closed, reopened, changed, interrupted, and exported | **Simulated** | `test_scenario.py` |
| The unattended evaluation runner and its report, including a checker that approves everything being caught by a planted claim | **Simulated** | `test_live_eval.py` |
| Any request to the live model: whether it plans, delegates without being told, asks, objects, revises | **Unrun** | `docs/live-evaluation.md` |
| Time and cost of a real design-basis request | **Unrun** | `/usage` on a live job |
| The lead and specialist role files as prompts: whether the model follows them | **Unrun** | live only |
| Whether the live model writes a reply differently in one mode than in another, and whether a zone narration in synthesis keeps the governing figures as well as the mixed one did | **Unrun** | live only |
| The trace check's own judgment (the checker stand-in never disagrees). The runner's probe step and step 8 of the guide are how to test it | **Unrun** | live only |
| Whether the live checker's reply now finishes on a record of sixteen to twenty-two findings, eight claims to a request with a 64,000-token ceiling (16,000 before 2026-11-12) | **Unrun**. The 0.2.0 acceptance run saw it cut off at 4,000 | live only; keep the reply's stop reason |
| Every request asks for 64,000 output tokens, and a zone narrative, a starter, a trace check, and a claim check stream rather than wait for a whole reply | **Simulated** (a stand-in client records each request) | `test_streaming.py`, `StreamingClientTests`, `StreamingWindowTests` |
| Whether a live reply longer than 16,000 tokens now finishes, and how long it takes | **Unrun** | live only; `/usage` |
| Whether the Section 21 13 19 export can open with the live checker at all. The 0.2.0 acceptance run saw 1 claim of 12 supported; the cite the checker is shown is an unlabeled list of the tool plan's numbers | **Unrun**, and open as a question (`NEXT-STEPS.md`, N-2) | live only |
| Whether a live specialist reads a skill before it records findings, and follows it | **Unrun** | live only |
| The second job with the live model | **Unrun** | `--job dh2` |
| Whether a live specialist converts an SI figure with `convert_units`, and whether the live lead goes on from "that's all I have" with labeled assumptions (the 0.3.0 report's GT-FP-12 and GT-FP-11) | **Unrun** on 0.3.2 | live only |
| Whether the live checker writes its reason in the form the QA role now asks for, and whether the reasons help a specialist revise | **Unrun** on 0.3.2 | live only |
| The spend cap and a long retry-after on the real API; a request id quoted to the provider's support and matched in the Console | **Unrun** | live only, and the cap only by an account that reaches it |
| The damaged-record question in the Windows message box, and moving the file aside on an NTFS volume | **Unrun** | Windows only |
| Any check of the engineering basis against NFPA 13, NFPA 72, FM DS 5-32, or a manufacturer's listing; any qualified engineer's review | **Not done** | `docs/releasing-basis.md`, section 8 |
| The skipped tests: 13 `calcs/fa` code-quote tests (no code text in the repository) and the FP kernel reproduce check (needs the kernel source folder) | **Skipped** in every run here | `calcs/fa`, `calcs/fp/test_kernel_reproduce.py` |
| A blank input stays blank: the form, the tool plan, and the calc tools put no 0, FM, 2025, 40 psig, or 30 min in its place; a blank time basis, choice, or yes/no holds the run naming it (since PR-C a blank detection, releasing, or exhaust time gives the fill time alone instead, below); a blank insurer reaches the kernel blank; a blank edition is a HOLD, "edition not pinned", in the lead's status block, `/status`, the Team tab, and the Design Basis coverage | Tested, no model involved | `app/tests/test_hardening.py`, `BlankInputHoldTests`; `test_acceptance_report.py`, `EditionHoldTests` |
| A new form is blank; a hint shows only with its cite, edition, and VERIFY, and its cite is in the pack file it names; no hint for the fill flow, the supervisory fill, or the low-air setting; base area shows NFPA 13's 1,500 ft² and FM's 3,500 ft²; Use hints records each one ASSUMED and marks it on the form; typing over it makes it GIVEN; an earlier version's unconfirmed starting values leave the job when it opens | Tested through the desk; the Inputs tab looked at in Linux Chromium at device scale 2 (Linen) | `app/tests/test_coherence.py`, `DeskInputTests`; `test_content_provenance.py`, `HintCiteTests` |
| Using a hint clears no HOLD: an ASSUMED edition stays "edition not pinned" in the status block, the edition gaps, a run's flags, and the coverage, and every other ASSUMED input keeps its own ASSUMED line, until the designer types a value | Tested through the desk and the record | `app/tests/test_coherence.py`, `test_an_accepted_edition_hint_never_clears_the_hold`, `test_a_run_names_each_input_taken_from_a_hint` |
| The QA verdict parse reads the QA role's own line, line 18, with its `(<reason>)`, including a reason or a cite that holds a quote or a bracket, a bracket inside a passage the reason quotes, and a reason that is missing, empty, or the role's placeholder | Tested against lines built from the role file and hand-written lines; no live checker reply in those forms has been seen | `test_acceptance_report_030.py`, `test_the_parse_reads_the_qa_roles_own_line_exactly`, `test_a_bracket_inside_a_quoted_reason_and_a_missing_reason` |
| The corrections `docs/content-provenance.md` lists keep their sentences (text guards), and every skill a role names is in the pack | Tested | `app/tests/test_content_provenance.py` |
| PR-C, delivery rows: the system type (required), the declared interlock, the job's pinned NFPA 13 edition, and `v_basis` caller reach the kernel; a wet zone has no delivery, gas-fill, or releasing rows; a double-interlock row cites no dry-pipe path; the threshold is named as one, with its section and edition, never a cap; the kernel's cite is shown as written | Tested on the DH-1 and DH-2 samples and hand-built calls, no model involved | `app/tests/test_pr_c.py`, `DeliveryArgumentTests` |
| PR-C, edition: a blank, ASSUMED, or unlabeled (2022) NFPA 13 edition runs the figures with every NFPA 13 cite withheld and writes no 2025 to the record; 2019 is cited as 2019; a changed edition puts the delivery rows out of date; Section 21 13 19 and the Design Basis wait for a pinned edition | Tested through the tool plan, the record, and both exports | `test_pr_c.py`, `EditionTests`, `ExportGateTests`; `test_acceptance_report.py`, `EditionHoldTests` |
| PR-C, form checks: a blank sub-time gives the fill time and its margin and nothing else; a typed 0 is ASSUMED-ZERO; density, base area, and duration > 0 on the form, the tool, `fp_calc`, and `validate_di`; no demand without a density or area; an ASSUMED density is labeled and not for release; `fp_calc` takes no elevation as 0 unless it is passed; fittings left out of the screen's zone total take the kernel's ASSUMED allowance; a zone total within 1% of the threshold is flagged | Tested, no model involved; the expected figures are the kernel's own on another call or a contract property, not worked out from the code under test | `test_pr_c.py`, `SubTimeTests`, `DemandTests`, `ExemptionTests` |
| PR-C, units and the claim cite: an unmarked kPa or bar is refused on a gas-law field and ASSUMED gauge on another; `k_si` is shown as a display figure; the gas fill names the larger basis; each claim's cite is built from named outputs, and an approve-all checker does not carry a figure no output holds | Tested with an approve-all reply written in the test; no live checker has seen the new cite form | `test_pr_c.py`, `UnitTests`, `ClaimCiteTests` |
| PR-C, FA calls: `charger_ok` holds without the caller's listed cap and on a pack that still takes a maker key; a blank, missing, or non-positive LFL holds; a missing starter block holds naming the skill. The FA content change (`charger_ok`, `spare_ah`) and the NFPA 497 LFL constants are not in this tree, so the app side was tested against a stand-in function only | Tested; the pack side **Unrun** until the content lands | `test_pr_c.py`, `FaCallTests` |
| PR-D, no silent defaults: `fp_calc` `density_area` refuses an omitted or blank area increase or hose; `zone_trapped_volume` refuses a blank or unknown length basis; a direct `dry_delivery_screen` with trim or fittings needs `length_basis` and takes the basis it is given; a blank manual station holds the releasing table; a `zone_gal` of 0 or less, or not finite, is refused | Tested on hand-built calls and the DH-1 and DH-2 samples, no model involved; expected zone totals are the kernel's own takeoff on the same basis | `app/tests/test_pr_d.py`, `DensityAreaThroughFpCalcTests`, `NoLengthBasisDefaultTests`, `ManualStationTests`, `ZoneTotalPositiveTests` |
| PR-D, releasing and display: only a double-interlock zone gets the releasing table and is asked for the manual station and the failsafe answer; every volume line prints the length basis beside the allowance, center-to-center with no allowance adds the friction sentence (its cite read from the pack file) outside the narrative, and the takeoff and the screen each name their basis | Tested through the tool plan, the Results tiles, the Section, and the Design Basis | `test_pr_d.py`, `ReleasingForDoubleInterlockOnlyTests`, `VolumeBasisTests` |
| PR-D, export gates: Section 21 13 19 names and holds on every ASSUMED input (run, job, or record), a blank or ASSUMED insurer, withheld NFPA 13 cites, and a blank NFPA 72 edition, before a billed check; a Design Basis with no pinned NFPA 72 edition is a working draft with its fire-alarm figures, and the findings and claims on them, printed as HOLD | Tested through `section_problem`, the desk's claim check, and the Design Basis writer. Which fire-alarm kernels really read the edition is content and **Unresolved**: the app holds every `fa_calc` row but the LFL screens | `test_pr_d.py`, `SectionGateTests`, `Nfpa72DesignBasisTests` |
| PR-D, FA: `charger_ok` without the listed cap returns one recorded HOLD message, never a pass or a fail and never a maker cap, that stands in the status, `/status`, the coverage, and the Design Basis until it runs on the cap; the `fa_calc` LFL ops hold on a blank, zero, negative, or non-finite LFL as `lfl_setpoints` does; `live_eval` reads `nfpa_size_threshold_gal` | Tested; the installed pack's `charger_ok` still takes a maker key, so every call holds, and the run on a listed cap was tested against a stand-in function only (the pack side **Unrun** until the content lands) | `test_pr_d.py`, `ChargerHoldTests`, `LflBypassTests`, `LiveEvalThresholdTests` |
| Whether a live model passes the job's edition and the system type to the delivery tools, and quotes `note_60s_option` as written | **Unrun** | live only |
| The held electric/pneumatic draft under `calcs/fp/draft/` | **Not run** by these suites, imported by nothing; left out of a built pack and of the seed | held work |
| A numbered seed is not replaced by an older or equal published pack, an older seed still upgrades, and a pack an earlier version downloaded, or an installed pack with no number, does not stand in for a newer seed after an app upgrade; a folder the designer chose stays | Tested, with a stand-in frozen seed and a local feed | `app/tests/test_content_update.py` |
| A foam or clean-agent slug (the two the 0.3.x acceptance found among them) fails the app's pack build with no zip, the seed copy, and the install; a Canada-named path ships under its own name in the build, the seed, and the install; the scan and the builder keep one prefix list | Tested | `app/tests/test_content_update.py`, `calcs/fp/test_pack_strip_guard.py` |
| The content workflow's gate: a tag whose commit is not on main, a tag not named `content-v<version>`, a version not above every published content pack (the release list the workflow hands it; a refused tag sets no floor), a push by someone other than the owner, a check not told the owner, or a release list that cannot be read fails | Tested against a local git repository; the workflow itself has not run on a tag | `app/tests/test_content_update.py` |
| Branch protection on main and a tag rule for `content-v*` | **Not set** from here: repository settings for the owner | the PR-A pull request |
| The test workflow on GitHub (`.github/workflows/tests.yml`) | Ran and passed on the pull request that added it, on Python 3.12. It skips the browser tests, which need Playwright: the runner has none | new in this milestone |
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
