# Acceptance tests A through E: protocol and results

The plan of record (`docs/prototype-plan.md`, section 4) names five acceptance tests. This file is how to run each one, what passes, and where the results go. Tests C and D have their own protocol in `docs/recovery-protocol.md`; this file points there and keeps their results in one place with the others.

Everything that can run without a Windows machine or an API key has run and is marked below. Everything else needs the project owner on a Windows machine with a saved key, and is marked **Not run** until then.

## Before you start

1. **Get the installer.** Two ways:
   - **Build without a release.** On GitHub, Actions, "Windows app", Run workflow, pick the branch, leave `version` empty, turn `publish` off, Run. When it finishes, open the run and download the artifact `fpfa-windows-<version>-<sha>`. It holds `fpfa-setup-<version>.exe` and `fpfa-windows-<version>.zip`. Nothing is tagged or released.
   - **Release.** Push the tag `app-v<version>` where `<version>` equals `__version__` in `app/fpfa/__init__.py`, or run the same workflow with `publish` on. The release carries both files.
2. **A clean Windows machine or VM.** No Python installed, no earlier copy of the app, no saved key. Windows 10 or 11, 64-bit. Note its edition and build (Settings, System, About).
3. **An Anthropic API key** for the owner's account. It is typed into Settings on the machine and nowhere else.
4. **`docs/known-answer-dh1.md` confirmed.** Three items are marked OWNER TO CONFIRM. Test A compares the export against that page, so confirm or edit them first.

## Test A. Clean Windows install

What passes: install on a clean machine, open the sample, load the skills, run the DH-1 tool plan, export. Figures match `docs/known-answer-dh1.md` section 2. Runtime and dependency versions recorded.

1. Run `fpfa-setup-<version>.exe`. Accept the defaults. Note the install time and the install folder.
2. Start the app from the Start menu. Expected: the chat-first window opens, no error, the status line shows the key is not saved.
3. ⋯ menu, **About and versions**. Copy the box's text into the versions table below. It lists the app version and whether it is frozen, the model id, Python, Windows, each dependency's version, the content pack version and folder, the data directory, and the record schema.
4. Type `/sample-di` and press Enter. Expected: a new job named for the sample, the tool plan runs without a key, and the thread shows the zone figures. Open Zone details, Results tab: the tables.
5. Compare the figures with `docs/known-answer-dh1.md` section 2: pipe volume, fittings allowance, trim, zone total, delivery time, screen limit, releasing rows, density and area, hose, duration, nitrogen. Every figure and every label must match.
6. ⋯ menu, **Export draft Section 21 13 19…**. Expected: a .docx is written and opens in Word. Then **Export Design Basis and Open Questions…**. Expected: with no findings yet the export is allowed and section 3 lists the eight calculation records with the same figures.
7. Settings, paste the key, save. Expected: the status line says the key is saved. Note which key store the Settings dialog reports (Credential Manager on Windows).
8. Ask: "Give me the design basis for zone DH-1." Expected: a reply with a **Team** block under it, the Team tab roster showing the lead and at least one specialist, and findings on the record. Compare the reply's content against sections 3 and later of the known answer. Note what differs.
9. ⋯ menu, **Usage and cost**. Copy the job total and the estimated cost into the cost table below.

Pass: steps 2, 4, 5, 6, and 8 as expected, and the versions table filled.

## Test B. Specialist collaboration

What passes: distinct FP, FA, and checker contributions on DH-1. Every substantive handoff is a record row with sender, receiver, time, and payload, visible in the window.

1. On the Test A job, ask: "Have the sprinkler specialist confirm the trim election and the releasing specialist write the cause-and-effect for DH-1, then run the blind check."
2. Expected: the Team block names `fp-sprinkler`, `fa-releasing`, and the checker's count. The Team tab roster shows both specialists `✓ done` and the lead `✓ done`. HANDOFFS shows a row from the lead to each specialist with the time, status `returned`, and the brief; selecting a row shows the payload and the result. Findings written by each specialist carry its slug and a calc record id in supports.
3. If a specialist hands work to the other, expected: a row from the first specialist to the second, `pending` until the lead delegates to the receiver, then `delivered` and `returned`, with the same row id throughout.
4. Export the Design Basis. Expected: section 4 groups findings by contributor, section 5 shows the checker's verdicts, section 8 lists the handoffs.

Pass: steps 2 and 4 as expected.

Automated half, already passed: `app/tests/test_team.py` runs the same shape with stand-in model calls (three distinct contributors, a complete handoff log, the checker's verdicts applied).

## Test C. Continuity

See `docs/recovery-protocol.md`, Test C. Automated half passed (`app/tests/test_recovery.py`). Manual steps not run.

## Test D. Recovery

See `docs/recovery-protocol.md`, Test D: forced kill, a second copy while the first runs, sleep and wake, hibernate. Automated half passed, including a real process kill. Manual steps not run.

## Test E. Usability and cost

What passes: Activity collapsed by default, handoffs inspectable, cancel works, blockers visible, export reviewable. Cost per DH-1 task measured from the usage totals.

1. On a fresh launch, expected: Activity is not shown until a job runs; Zone details starts closed; only New chat, Settings, and Send are plain buttons.
2. After Test B, expected: every handoff row opens its detail on the Team tab; blockers list the open questions and any finding not Supported; the Design Basis export can be read in Word and traced to the record.
3. Cancel: ask a long question with **Ask Claude** on, press **Cancel running job** on the Team tab while Activity shows `running`. Expected: the turn stops at its next round, the thread shows a "Cancelled" line, Activity shows `cancelled`, and **Usage and cost** still lists the cancelled turn with what it spent.
4. Cost: ⋯ menu, **Usage and cost**, or from a source checkout `py -m fpfa.usage_report --db "%APPDATA%\fpfa-assistant\fpfa.db"`. The report lists each model context (lead turns with their delegations and checks inside, narrations, blind checks), the job total, and the estimated dollars at the rates printed on the second line. Fill the cost table below with the Test A question alone and with the full Test B task.

Pass: steps 1, 2, and 3 as expected, and the cost table filled.

Automated half, already passed: `app/tests/test_usage.py` proves the events, the totals, and the report; `app/tests/test_team_ui.py` proves cancel end to end; `app/tests/test_prototype.py` proves the launch layout.

## How the figures are judged

- Numbers come from the calc tools. A figure in a reply that is not a tool-plan figure is a defect, however plausible.
- Labels stay distinct: calculated, ASSUMED, use best judgment. A delivery time is an optimistic screen, not a listed water-delivery-time calculation, and the reply must say so.
- The double-interlock draft section is 21 13 19. A reply or export that says 21 13 16 for the sample zone fails.
- NFPA 13-2025 is the delta baseline. A cite without an edition fails.

## Results

### Where each test stands

| Test | Automated half | Manual half (Windows) | Date | Notes |
| --- | --- | --- | --- | --- |
| A. Clean Windows install | Figures locked by `calcs/fp` and `app/tests/test_prototype.py`; versions by `app/tests/test_usage.py`; packaging config checked | Not run | | Needs the installer and the clean machine |
| B. Specialist collaboration | Passed, `app/tests/test_team.py` | Not run | | Needs a key |
| C. Continuity | Passed, `app/tests/test_recovery.py` | Not run | | Protocol in `docs/recovery-protocol.md` |
| D. Recovery | Passed, including a real process kill | Not run | | Protocol in `docs/recovery-protocol.md` |
| E. Usability and cost | Passed, `app/tests/test_usage.py`, `test_team_ui.py`, `test_prototype.py` | Not run | | Needs a key for the cost figures |

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
| Content pack version | |
| Record schema | |
| Installer file and size | |
| Install time | |

### Cost per task (from Usage and cost)

Rates are the dated snapshot printed by the report. Record the date it prints.

| Task | Model contexts | Input tokens (fresh / cache write / cache read) | Output tokens | Estimated cost | Wall time |
| --- | --- | --- | --- | --- | --- |
| Test A, "Give me the design basis for zone DH-1." | | | | | |
| Test B, specialists plus blind check | | | | | |
| Narrated zone run (`/run` with Ask Claude on) | | | | | |

### Failures and limits found

| Where | What happened | Severity | Follow-up |
| --- | --- | --- | --- |
| | | | |
