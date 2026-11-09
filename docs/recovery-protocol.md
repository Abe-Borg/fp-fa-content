# Recovery protocol: Tests C and D

The plan of record (`docs/prototype-plan.md`, section 4) names two acceptance tests that a relaunch has to pass. This file is the protocol for both: what the app does, what the automated tests already prove, and the manual steps on a Windows machine with the expected result of each. Run the manual steps on the Phase 6 machine alongside Test A and write the results into the table at the end.

## What the app does on a relaunch

- The inbox is in memory. The record is the only thing that survives the process ending.
- Every job the window runs is also a `jobs` row in the record, written from the inbox refresh once per status change. A job never moves back there: a late `queued` after `running` is ignored and a finished job stays finished.
- On launch, before the window takes any work, `Record.recover()` runs once over the whole database in one transaction:
  - a job still `queued` or `running` is marked `interrupted`;
  - an agent still `working` is marked `interrupted`;
  - a handoff still `delivered`, which means its receiver was mid-turn, goes back to `pending` with the note "Re-queued after a relaunch."
  - The same rows are updated. Nothing is copied, so no handoff is repeated and no calc record is duplicated. Finished rows are not touched. A second pass finds nothing.
- The designer sees it three ways: the status line counts what was recovered; Activity lists each interrupted job under its original id with the status `interrupted`; opening the job posts one app-written note into its thread, and the Team tab shows the interrupted agents with `!` and the re-queued handoffs and interrupted jobs under blockers.
- The note is owed until it is read. The recovery pass writes what it touched onto a `recovered` event; until a `recovery_noted` event follows it on that job, every later launch shows the same status line and Activity rows and posts the note when the job is first opened. Closing the app without opening the job loses nothing.
- One window per data directory. The first window takes an operating-system file lock on `fpfa.lock` before it reads the record and holds it until it closes. A second window on the same directory is refused with a message and exits, so it cannot treat the first window's live work as interrupted. The lock belongs to the process: a kill releases it, so a crash never blocks the next launch.
- Nothing is re-run on its own. The designer sends the question again or runs the zone again. Identical calc inputs replay from the record, which the Design Basis export shows as a replay count. The lead's next turn starts with the handoffs waiting on the record, so it delivers each by delegating to its receiver; the same row moves to `delivered` and `returned`.
- Sleep and wake: the window keeps the wall-clock time of its last poll. A gap longer than 90 seconds is treated as a sleep or a freeze. On the first poll after it, a `wake` event is written on the open job and the status line says the app resumed and what to expect of a job that was running. Nothing is restarted.

## What the automated tests cover

`app/tests/test_recovery.py`, run with the app suite under Xvfb.

| Test | Covers |
| --- | --- |
| `test_jobs_persist_once_per_status_and_never_move_back` | The `jobs` rows, one event per status, the no-move-back rule, delete with the project. |
| `test_recover_marks_in_flight_rows_interrupted_and_requeues_delivered_handoffs` | The launch pass on a seeded record: interrupted jobs and agents, re-queued delivered handoff, pending and returned rows untouched, no row copied, one `recovered` event per project, idempotent. |
| `test_recovery_notices_wait_until_the_note_is_posted` | The owed note survives a launch that never opened the job, clears when the note is posted, and a later kill owes only its own work. |
| `test_one_holder_per_file_in_one_process` | The instance lock admits one holder per file, a second file is a separate lock, and release lets the next holder in. |
| `test_the_lock_follows_the_process_that_holds_it` | A child process holds the lock and the parent is refused; the child is killed and the parent acquires it, so a crash never leaves a stale lock. |
| `test_a_requeued_handoff_is_delivered_once_by_the_next_delegation` | Test D, "no repeated handoff": the re-queued row is delivered with the next delegation to its receiver and ends `returned`; the handoff count grows only by the delegation's own row. |
| `test_the_lead_sees_pending_handoffs_at_the_top_of_its_turn` | The lead's user message starts with the waiting handoffs, marked re-queued where recovery put them back, and carries nothing when none wait. |
| `test_recovery_text_names_what_was_in_flight` | The thread note and the Team tab blockers name the interrupted jobs, agents, and re-queued handoffs and leave finished work out. |
| `test_a_killed_run_leaves_no_duplicate_calcs_and_recovery_marks_the_job` | Test D, the kill half, with a real process: a child records the DH-1 calcs one by one and is killed after the third commit. Recovery marks its job and agents interrupted and re-queues its handoff. A full re-run adds only the calcs the kill prevented, every surviving calc replays once, the figures equal the plain run, and a second pass finds nothing. |
| `test_window_jobs_are_written_to_the_record` | The sample zone run leaves a `zone` job row marked `done`. |
| `test_a_relaunch_shows_the_roster_the_requeued_handoff_and_the_interrupted_job` | Test C and the window half of Test D: a relaunch on the same data directory shows the recovery status line, the interrupted job in Activity under its id, the note once in the thread when the job opens even though a launch in between never opened it, the roster states, the blockers, both handoffs pending, and the eight calcs back. Opening the job again posts nothing new, and a launch after the note was read owes nothing and lists nothing. |
| `test_a_second_window_on_the_same_data_directory_is_refused_and_recovers_nothing` | While another holder has the directory, the window refuses to start and the live job and agent rows are untouched; once the holder lets go, the next launch owns the directory, recovers, and releases it when it closes. |
| `test_a_long_gap_between_polls_is_reported_as_a_resume` | Sleep and wake as a clock gap: the status line, the `wake` event with the gap and the running job ids, and the wording with and without a running job. |

The automated tests prove the record behavior and the window behavior in one process. They do not prove what Windows does to a frozen `Cynosure.exe`, a sleeping network connection, or a database on a drive that was asleep. The manual steps do.

## Manual protocol on Windows

Run on the Phase 6 machine with the installed app and a saved key. Use the sample data hall. Write the result of each step in the table at the end. Where a step says "note", write the number down.

### Test C. Continuity

1. Start the app. Type `/sample-di`. Turn **Ask Claude** on and ask: "Give me the design basis for zone DH-1." Wait for the reply and the **Team** block under it.
2. Open the Team tab. Note the roster lines, the number of handoff rows, and the blockers. Note the number of calculation records in the Design Basis export (export it; section 3 lists them).
3. Close the app from the window's close button. Relaunch it.
4. Expected: the job is in the sidebar. Open it. The thread is as it was. The Team tab shows the same roster lines with the same states, the same handoff rows with their briefs and results on select, and the same blockers. The status line does not say "Recovered", because nothing was in flight. Export the Design Basis again: the same number of calculation records, with no new rows.
5. Follow-up to a finished specialist: ask the lead, "Have the sprinkler specialist restate the trim election with its calc record id." Expected: the Team block names the sprinkler specialist again; on the Team tab the new handoff row's detail shows the lead's brief, and the specialist's result refers to its earlier figures by the same calc record ids rather than new ones. The export's calculation records show replays, not new rows.

Pass: steps 4 and 5 as expected.

### Test D. Recovery, forced kill

1. Start the app and open the sample job from Test C. Turn **Ask Claude** on and ask a question that delegates: "Give me the design basis for zone DH-1 and have the releasing specialist write the cause and effect."
2. While Activity shows the chat job as `running` and the Team tab shows a specialist as `● working`, end the process: Task Manager, select the app, **End task**. From a source checkout, `taskkill /F /PID <pid>` on the Python process, or close its console window.
3. Relaunch. Before that, try starting a second copy while the first is still running: expected, a message that the assistant is already open on this data directory, and the second copy exits without changing anything in the first.
4. Expected at launch: the status line reads "Recovered after a relaunch: 1 job interrupted, N handoffs re-queued, across 1 job in the sidebar." Activity lists `interrupted chat <job name> <id>` with the id the thread's job heading carries. Close and relaunch once more without opening the job: the same status line and Activity rows come back, because the note is owed until the job is opened.
5. Open the job. Expected: one note in the thread, "Recovered after a relaunch.", naming the chat job, the Lead and the specialist that were interrupted, and each re-queued handoff with its sender and receiver. The Team tab roster shows those agents with `!` and `interrupted`; blockers list the re-queued handoff and the interrupted job. The handoff row's status is `… pending` and its detail ends with the re-queued note.
6. Note the number of calculation records in the export now.
7. Send the same question again. Expected: the turn runs; the Team block names the specialists; on the Team tab the re-queued handoff's row, with the same id, is now `returned`, and there is no second row with the same brief from the same sender at the earlier time. The roster shows the agents `✓ done`.
8. Export the Design Basis. Expected: the number of calculation records equals the note from step 6 plus only the calcs the first turn never reached; records from before the kill show a replay count of at least 1; no two records share a tool and inputs.

Pass: steps 4, 5, 7, and 8 as expected. Record the counts from steps 6 and 8.

### Test D. Recovery, sleep and wake

1. Start the app and open the sample job. Turn **Ask Claude** on and ask a question that takes a while: "Give me the design basis for zone DH-1 and have both specialists contribute."
2. While Activity shows the job `running`, put the machine to sleep (Start, Power, Sleep). Leave it for at least two minutes. Wake it and sign in.
3. Expected within a few seconds of wake: the status line reads "Resumed after about N min. 1 job still running; one that lost its connection reports an error in its thread, or cancel it from the Team tab."
4. Expected within the model timeout: either the reply arrives as usual, or the job ends `error` with the connection error in its thread. Either way Activity shows one job, not two. If it neither finishes nor fails after ten minutes, press **Cancel running job** on the Team tab: the job ends `cancelled` at its next round.
5. Export the Design Basis. Expected: no calculation record is duplicated; a replayed record shows its count.
6. With no job running, sleep the machine again for at least two minutes and wake it. Expected: "Resumed after about N min. No job was running." Nothing else changes.
7. Hibernate instead of sleep in step 2 is the same test with a longer gap; the expected results do not change.

Pass: steps 3, 4, 5, and 6 as expected.

## Known limits

- A kill during a model round loses that round. Nothing from it was written, so nothing is recovered from it; the job is re-run.
- A job cannot resume mid-turn. Recovery marks; the designer re-runs. Calc replay makes the re-run cheap, and the handoff log stays single-rowed.
- The inbox refresh writes job status to the record on the window thread within one poll of the change, about 100 ms. A kill inside that window may leave a job that never reached the record. It is then simply not listed; there is nothing to recover.
- A kill inside a SQLite transaction leaves a rollback journal that the next open rolls back. The kill test exercises this by killing between commits with timing it does not control.
- The instance lock is per data directory, not per machine. Two data directories (`FPFA_DATA_DIR`) can each have a window. That is two records, so neither recovers the other's work.
- The wake detector reads the wall clock. A clock set forward by more than 90 seconds while the app runs is reported as a resume. That is a status line and an event, not a change to any job.

## Results

| Test | Where | Result | Date | Notes |
| --- | --- | --- | --- | --- |
| Automated (`app/tests/test_recovery.py`, 13 tests) | Linux, Python 3.12, Xvfb | Passed | 2026-11-09 | Runs with the app suite |
| C. Continuity, manual | Windows, installed app | Not run | | Phase 6 machine |
| D. Forced kill, manual | Windows, installed app | Not run | | Phase 6 machine; record the counts from steps 6 and 8 |
| D. Sleep and wake, manual | Windows, installed app | Not run | | Phase 6 machine |
