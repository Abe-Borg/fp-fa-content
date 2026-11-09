# FP/FA agent-team prototype: plan of record

This file is the single source of truth for the v0 prototype. Every agent working on this repository reads it before starting and updates the status columns when a phase or a gate changes. Email threads, chat transcripts, and earlier planning notes are history, not the plan.

Updated: 2026-11-09. Phases 1 through 5 complete. Phase 6 in progress: everything that runs without a Windows machine or a key is done; the Windows runs wait for the owner. Implementation of v0 is authorized as of 2026-11-09 along the path in this file.

## 1. Definition of done for v0

A coworker installs `fpfa-setup.exe` on their own Windows machine, saves their own Anthropic API key, opens the sample double-interlock data hall, and asks: "Give me the design basis for zone DH-1."

Within a few minutes they get all four of these:

1. A lead reply with the design-basis summary and the open questions.
2. A team panel showing the FP specialist, the FA specialist, and the checker as separate contributors, with every handoff inspectable: who sent what to whom, when, and what came back.
3. An exported Design Basis and Open Questions document whose numbers came from the calc tools, whose claims passed the independent checker, and whose unresolved items are listed as RFIs for the engineer of record.
4. The cost of that task, measured and shown on the status line and recorded on the job.

The known answer for that task is `docs/known-answer-dh1.md`. The exported document and the lead reply are judged against it.

## 2. Decisions of record

| Date | Decision | Why |
| --- | --- | --- |
| 2026-11-09 | Orchestrate the team on the existing Messages-API tool loop in `app/fpfa/claude_client.py`. Do not adopt the Claude Agent SDK for v0. | The SDK's distinctive promise, direct peer messaging between specialists, is not available in SDK or non-interactive mode per current docs. Its remaining advantages are already built here or must be built here regardless. It would add a subprocess runtime, a packaging problem, and config isolation work with no v0 payoff. See section 9. |
| 2026-11-09 | Peer messaging is lead-routed through the project record in v0. Real-time specialist-to-specialist chat is a v0.2 experiment. | The outcome is inspectable handoffs and distinct contributions. A handoff row with sender, receiver, time, and content gives that whatever the transport. |
| 2026-11-09 | Durable project record is SQLite, one database in the data directory, every row keyed by project id. Agents write to it only through app tools. Documents are exports of it. | Conversation history is not a transaction log. Duplicate prevention, roster restoration, and pending work need a store the app owns. |
| 2026-11-09 | No Managed Agents cloud runtime in v0. The `/heavy` hatch stays dormant and is removed or parked in v0.1. | Agreed in the November 5 planning. Nothing in v0 needs a hosted container. |
| 2026-11-09 | The window stays tkinter. No UI technology change for v0. | The roster, collapsed activity, and inbox already have a home in the current window. |
| 2026-11-09 | Model stays `claude-opus-5-5` for the lead, the specialists, and the checker. Cost is measured before any model split is considered. | Engineering judgment first. A cheaper specialist model is a measured decision, not a default. |
| 2026-11-09 | Numbers come from `calcs/`. The three labels stay: calculated, ASSUMED, use best judgment. Delivery times are an optimistic screen, not a listed water-delivery-time calculation. | Unchanged from the current app. The team does not loosen this. |

## 3. Roadmap and status

Sizes are focused work sessions. No dates are promised.

| Phase | Ships | Gate | Size | Status |
| --- | --- | --- | --- | --- |
| 0. Freeze | This file, `CLAUDE.md`, `docs/known-answer-dh1.md`, README pointer | Owner confirms the known answer | 1 | Documents merged. Known answer awaiting the owner's confirmation |
| 1. Project record | SQLite store with the tables in section 5. App tools that write to it. Calc tools record themselves and return a prior result for identical inputs. Migration of today's JSON jobs. | Store tests green. Existing suite green. | 2 to 3 | Done in `app/fpfa/record.py`, `calc_tools.py`, and the three model paths. Tests in `app/tests/test_record.py` |
| 2. Design-basis export | Word export built from the record. Sections in section 7. | Export from a seeded record matches the known answer by hand. | 1 to 2 | Done in `app/fpfa/design_basis_docx.py`; menu item in the window; `app/tests/test_design_basis.py` locks the section 2 figures of the known answer. The checker gate on this export moves to Phase 3 with the record-fed checker |
| 3. Team | Lead loop with `list_specialists`, `delegate`, `handoff`, `request_check`. FP and FA specialists run in their own contexts from the existing role files with their own skill and tool subsets. Checker runs blind from the record. The lead picks specialists from the request. | Fake-client tests show three distinct contributors and a complete handoff log on the sample. | 3 to 4 | Done in `app/fpfa/team.py`; tests in `app/tests/test_team.py`. The Design Basis export now waits for a current all-Supported record check when findings exist. Awaiting review before Phase 4 |
| 4. Team UI | Roster with states, collapsed activity, expandable handoff cards, blockers and open-questions pane, cancel. Built on the existing Activity list and inbox. | Window tests under Xvfb. | 2 | Done: Team tab in the drawer (`app/fpfa/team_panel.py`), TEAM roster in the sidebar, app-written team summary under lead replies, cooperative cancel through the tool loop, a Run blind check job. Tests in `app/tests/test_team_ui.py` |
| 5. Recovery | Pending handoffs re-queued on launch. Calc idempotency by input hash. In-flight jobs marked interrupted on relaunch. Forced-kill and sleep tests. | Tests C and D protocol written and passed. | 2 | Done: jobs persist as record rows, `Record.recover()` runs once at launch, the lead sees waiting handoffs at the top of its turn, a wake detector in the window. `docs/recovery-protocol.md` is the protocol; its automated part, including a real process kill, is `app/tests/test_recovery.py`. The manual Windows runs wait for the Phase 6 machine |
| 6. Package and measure | Installer from the existing scripts. Clean Windows VM. Run tests A through E. Record versions, cost per task, failures, and limits. | A, B, E pass. C and D at least documented. | 1 to 2 | In progress. Done from Linux: the Windows workflow gained a build-only mode (`publish` off uploads the installer and zip as artifacts, no tag), `__version__` is 0.1.3 for the next release, every model context writes its usage on the record (`turn`, `narration`, `record_check`, `delegation` events), `app/fpfa/usage_report.py` prices a job (`/usage`, the ⋯ menu, `python -m fpfa.usage_report`), `app/fpfa/about.py` records versions (`About and versions`, `--versions`), and `docs/acceptance-tests.md` is the A through E protocol with result tables. Waiting on the owner: the clean Windows machine, a key, and the known-answer confirmation, then the manual runs and the result tables |

## 4. Acceptance tests

| Test | What passes | Status |
| --- | --- | --- |
| A. Clean Windows install | Install on a clean machine, open the sample, load the skills, run the DH-1 tool plan, export. Figures match `docs/known-answer-dh1.md`. Runtime and dependency versions recorded. | Protocol in `docs/acceptance-tests.md`. Figures locked by tests; versions come from About and versions. Manual run: not run |
| B. Specialist collaboration | Distinct FP, FA, and checker contributions on DH-1. Every substantive handoff is a record row with sender, receiver, time, and payload, visible in the window. | Automated half passed (`app/tests/test_team.py`). Manual run with a key per `docs/acceptance-tests.md`: not run |
| C. Continuity | Relaunch the app and the roster, the pending handoffs, and the record are back. A completed specialist can be asked a follow-up with its prior contribution in front of it. | Automated half passed (`app/tests/test_recovery.py`, a second window on the same data directory). Manual Windows run per `docs/recovery-protocol.md`: not run |
| D. Recovery | Forced process kill and sleep/wake, tested separately. No duplicate calc records. No repeated handoff. In-flight jobs are marked interrupted and can be re-run. | Automated half passed: a child process killed between calc records, recovery, re-run with replays only, and the wake detector as a clock gap. Manual Windows runs per `docs/recovery-protocol.md`: not run |
| E. Usability and cost | Activity collapsed by default, handoffs inspectable, cancel works, blockers visible, export reviewable. Cost per DH-1 task measured from the usage totals. | Automated half passed (`app/tests/test_usage.py`, `test_team_ui.py`, `test_prototype.py`); the cost report exists. Manual run and the cost table per `docs/acceptance-tests.md`: not run |

## 5. Project record

One SQLite database at `<data_dir>/fpfa.db`. Every table has `project_id`. The JSON job files stay for the chat thread and the zone form until Phase 1 migrates them; after migration the JSON file keeps the thread and the form, and the record holds everything else.

| Table | Holds | Written by |
| --- | --- | --- |
| `facts` | Basis of design: AHJ, adopted code and editions, insurer, owner standard, assumptions. `kind`, `key`, `value`, `source`, `label` (calculated, ASSUMED, use best judgment, CODE, OWNER, PRACTICE). | `record_fact` tool, the zone form |
| `evidence` | Cites: document, edition, section, short paraphrase, applicability, status (held, NOT PULLED, NEEDS HOLD). | `record_evidence` tool |
| `calc_records` | Tool name, input hash, inputs, outputs, pack version, time, caller. | Every calc tool, automatically |
| `findings` | A specialist's statement with its label and its supporting calc or evidence ids. | `record_finding` tool |
| `questions` | Open questions and RFIs: text, raised by, status, answer. | `open_question` tool, the owner |
| `decisions` | Elections and judgments: text, basis, decided by. | `record_decision` tool |
| `handoffs` | From agent, to agent, brief, payload, status (pending, delivered, returned), result, times. | `handoff` and `delegate` tools |
| `tasks` | Title, owner agent, status. | The lead |
| `agents` | Name, role slug, status, last active. | The app |
| `jobs` | Window jobs: id, kind, title, status (queued, running, done, error, cancelled, interrupted), error, start and update times. Written once per status change; a job never moves back. | The app, from the inbox refresh |
| `events` | Append-only log of everything above plus job starts, finishes, interruptions, and usage totals. | The app |

Rules:

- An agent never opens the database. It calls a tool. The tool validates, writes one transaction, and appends an event.
- A calc tool computes a hash of the tool, its inputs, and the identity of the calc code in the running pack (a hash of the kernel files). If a record with that hash exists for the project, the tool returns the recorded output and marks the call as a replay. This is the duplicate prevention for Phase 5. A pack update that changes a kernel file changes the identity, so old results are never replayed by new code; the old rows stay as history.
- Form-owned basis facts follow the form. A changed value writes a new row and supersedes the old one. Import from a JSON job happens once; the sync runs on every open, save, run, and turn.
- A fact or finding carries exactly one of the three labels from the current app, or a cite class. The tool rejects a row with none.
- Documents are exports. Nothing in a document is typed into the record by hand.
- Recovery marks, it does not run. `Record.recover()` runs once at launch in one transaction: queued or running jobs and working agents become `interrupted`, delivered handoffs go back to `pending` with a re-queued note. The same rows are updated, so nothing is duplicated, and a second pass finds nothing. The designer re-runs; calc replay makes that cheap.
- Implemented in `app/fpfa/record.py`. The database is `fpfa.db` in the data directory. `Record.snapshot(project_id)` is what an export reads. Rows written by a model context carry its agent name: `lead`, `narrator`, `tool-plan`, or a specialist slug.

## 6. The team on the existing loop

- **Lead.** The everyday path, with `roles/everyday/ROLE.md` as the shell and the active mode file, plus four new tools: `list_specialists`, `delegate(specialist, brief, inputs)`, `handoff(to, payload)`, `request_check()`. The lead owns the objective, picks specialists from the request, reconciles their findings, surfaces blockers, and writes the summary. It does not compute.
- **Specialists.** `fp-sprinkler` and `fa-releasing` to start. `delegate` runs `run_tool_loop` with that role's `ROLE.md` as the system text, the skill index, and that role's tool subset. The user message is the brief plus the record slices the lead grants. The specialist returns a structured contribution: findings, calc record ids, questions, and handoffs. The tool writes the contribution and a `returned` handoff row. Each specialist is a fresh context per delegation; a follow-up to a finished specialist re-sends its prior contribution as context.
- **Checker.** `roles/qa-specialist/ROLE.md`, blind. `request_check` builds the claim list from the record's findings and the cites from `evidence` and `calc_records`, and runs the one-call check that exists today in `app/fpfa/claim_check.py`. Verdicts are written to the record. Export waits for Supported, as today.
- **Routing.** A specialist that needs another specialist writes a handoff with `to`. The lead sees pending handoffs on its next round and delivers them when it activates that specialist. No specialist talks to another directly in v0.
- **Activation.** Dynamic. The lead is told which specialists exist and chooses. A fixed sequence is not imposed.
- **Cost.** Every context sums its usage. The lead's status line shows the task total. The total goes on the `events` row that closes the task: a `turn` event per lead turn (lead rounds plus every delegation and check inside it, also written when the turn is cancelled), a `narration` event per narrated zone run or starter, usage on each `record_check` event, and a `delegation` event per specialist, including one marked cancelled for a specialist a cancel interrupted. `app/fpfa/usage_report.py` reads every usage event on the job back and prices them at a dated rate snapshot; `/usage` posts the report into the thread.
- **Cancel.** A cancel flag per job is checked by the tool loop before each model round and by the lead before each team tool. The round or tool in flight finishes. A cancelled specialist is marked interrupted and its handoff cancelled; the job shows `cancelled` in Activity.
- **Relaunch.** The lead's user message starts with the handoffs waiting on the record, re-queued or not, so a delivery that a kill interrupted is in front of the lead on its next turn without a tool call. Interrupted jobs show in Activity under their original ids, the thread gets one app-written note when the job opens, and the Team tab shows the interrupted agents and the re-queued handoffs. A clock gap over 90 s between polls is reported as a resume with a `wake` event; nothing is restarted. The note is owed across launches until the job is opened (`recovered` and `recovery_noted` events). One window per data directory: an OS file lock on `fpfa.lock` (`app/fpfa/instance_lock.py`) refuses a second window, so it cannot recover the first one's live work; a kill releases the lock.

Implemented in `app/fpfa/team.py`. `TeamSession` is the lead's tool executor; `delegate` runs `run_tool_loop` with the specialist's role file as the system text and `SPECIALIST_SCHEMAS` (every tool but the three team tools); `check_record` builds the claim packet from findings and their supports and reuses the QA role's one-call blind turn; `export_gate` is what the Design Basis export asks before writing. Each delegation and each check is an `events` row with its usage.

## 7. Design Basis and Open Questions export

Word document from the record, section order:

1. Basis of design: AHJ, adopted code and editions, delta edition, insurer, owner standard. Each with its label.
2. Elections: system family, trim family, releasing logic, supervisory medium, with status tokens.
3. Calculation records: for each calc, the tool, inputs, outputs, time, and whether it was a replay.
4. Findings by contributor: FP, FA, and any later specialist, each with label and supporting ids.
5. Checker verdicts, with the claim list and the cites.
6. Assumptions: every ASSUMED row.
7. Open questions and RFIs for the engineer of record.
8. Handoff log.

The Section 21 13 19 export stays as it is. This is a second document.

Implemented in `app/fpfa/design_basis_docx.py`. Elections are read from the trim, releasing, and nitrogen calc records and from recorded decisions. Until the record-fed checker lands in Phase 3, section 5 prints a line saying no blind claim check has run, and the export does not wait for one.

## 8. Reuse map

| Exists today | Role in v0 |
| --- | --- |
| `app/fpfa/claude_client.py` tool loop, caching, usage totals | Lead and specialist contexts |
| `app/fpfa/calc_tools.py`, `calcs/fp`, `calcs/fa` | Unchanged math. Gains automatic calc records. |
| `roles/*/ROLE.md` | Lead shell, specialist system texts, checker |
| `app/fpfa/workflow.py` tool plan | Still runs the DH-1 numbers deterministically before any model call |
| `app/fpfa/claim_check.py` | Checker turn, now fed from the record |
| `app/fpfa/spec_docx.py` | Pattern for the new export |
| `app/fpfa/jobs.py` inbox | Runs delegations and checks on workers; roster states come from it |
| `app/fpfa/projects.py` JSON jobs | Thread and form; the record takes the rest |
| `app/packaging/*`, `.github/workflows/windows-app.yml` | Installer for test A |
| `app/fpfa/managed.py` | Dormant. Remove or park in v0.1. |

## 9. Why not the Agent SDK for v0

Checked against the current docs on 2026-11-09.

- Agent Teams, the feature that lets agents message each other, is experimental and does not run in non-interactive mode. In `-p` mode, "including Agent SDK sessions, Claude doesn't spawn teammates, and a subagent that Claude names runs as an ordinary subagent." Subagent-to-subagent messaging inside the SDK is not documented.
- What the SDK does give: isolated subagents with their own prompt, tools, and model; resume of a completed subagent with its history by a second `query(resume=...)`; skills through a plugin root; custom tools through an in-process MCP server; `tools: []` to remove every built-in; automatic caching; `total_cost_usd` and `max_budget_usd`.
- What it costs here: a bundled CLI subprocess per session that a frozen `fpfa.exe` would have to ship and point at with `cli_path` (undocumented for PyInstaller); a 32 KB Windows command-line cap that forces the system text into a file; `setting_sources=[]`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, and `CLAUDE_CONFIG_DIR` to keep a coworker's own Claude Code setup out of the app.

If the SDK is revisited, the spike runs after Phase 1 on a Windows machine with one exit question: does a frozen `fpfa.exe` start the bundled CLI from `cli_path`, run two subagents with the calc tools as an in-process MCP server and `tools: []`, load the pack's skills through `plugins`, and return structured results, with settings isolated? Yes on all five means the SDK can sit behind the same `delegate` interface. Any no means this plan stands.

## 10. Out of v0

Shared hosting. Managed Agents. Real-time peer chat. Wet and dry verticals beyond what the form already does. Factory or batch content automation. Source-runner automation. Canadian standards text. Autonomous issue of engineering deliverables. A model split by role.

## 11. How the agents coordinate

- This file is the plan. A change to scope, a decision, or a status moves here first, in the same pull request as the work.
- The coding agent on this repository owns Phases 1 through 5 and keeps `CLAUDE.md` and the README current.
- The content team keeps the content pack (skills, corpus, specs) and reviews the known answer.
- The reviewing agent reviews each phase pull request against this file and against the acceptance tests.
- One pull request per phase where practical. Each pull request body states the tests run and their counts.
- No release tags from a phase pull request. Content stays on `content-v*` tags and the app on `app-v*` tags.

## 12. Open items for the project owner

1. Confirm or edit `docs/known-answer-dh1.md`, especially the open questions and the judgment items marked OWNER TO CONFIRM.
2. Provide a clean Windows machine or VM for test A at Phase 6, with an API key for tests B and E.
3. Run the manual halves of tests A through E per `docs/acceptance-tests.md` and `docs/recovery-protocol.md`, and fill their result tables.
4. Decide when to publish `app-v0.1.3`: push the tag, or run the Windows app workflow with `publish` on.
