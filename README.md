# FP/FA Design Assistant

Desktop prototype for hyperscale data-center fire protection and fire alarm designers. The scope is wet pipe, dry pipe, and double-interlock preaction sprinklers, plus the detection and releasing that trip them, and outdoor oil-filled transformer apparatus water spray (NFPA 15-style) in `skills/power-block-transformer-water-spray/SKILL.md`. Foam, clean agent, water mist, a building deluge system, and single-interlock preaction are out of scope. Canada ships only through a Country gate (US | Canada) on the skill. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Apparatus water spray is not water mist and it is not a building deluge system.

The v0 agent-team prototype plan, its decisions, and its acceptance tests are in `docs/prototype-plan.md`. The known answer for the sample zone is `docs/known-answer-dh1.md`. Coding agents start from `CLAUDE.md`.

The app reads methods from `skills/`, calculations from `calcs/`, and optional draft language from `specs/`. It does not hardcode those methods. Point it at another folder with the same layout (`FPFA_CONTENT_ROOT`, or Settings). Settings can also check the release feed and install a newer pack. `corpus/` holds edition pins and decision notes. The everyday path searches them with `search_corpus`.

## Why this stack

Python, because the calc kernel that already exists is Python and the other design apps in this practice are Python. The window is the standard-library `tkinter` toolkit, so the prototype has no backend server and no browser. Numbers are computed in `calcs/` and exposed to Claude as tools.

The model is Claude Opus 5.5, model id `claude-opus-5-5`, called with the Anthropic Messages API and each user's own API key. That id is the one published on the Claude platform models page for Claude Opus 5.5. The client does not send `temperature`, `top_p`, or `top_k`. It does not disable adaptive thinking, and it does not force `tool_choice` (this model rejects a forced tool). Every request marks the system text as a prompt-cache breakpoint, and a request that carries tools asks for automatic caching on the message tail, so the rounds of one turn and the turns of one session read the shared prefix from the cache instead of paying full price for it each time.

The everyday path is how a typed question is answered. It loads the shell from `roles/everyday/ROLE.md` and lists the other specialist roles in `roles/<slug>/ROLE.md`, including the QA specialist. The model reads a specialist with `read_role` and a method with `read_skill` (`skills/<slug>/SKILL.md`). The Mode menu points at `modes/<slug>/MODE.md` the same way: brainstorm, calculator, synthesis, and mixed. The active mode file is the behavior for that reply. The model reads another mode with `read_mode`. Those files stay in the content pack. Calc tools still run in `calcs/` through the same tool loop. `fa_calc` runs `calcs/fa/lib`. `search_corpus` searches `corpus/`. The fixed tool plan in `app/fpfa/workflow.py` still fills the tables and the docx when a narrative disagrees. This path does not add another model vendor, and it does not send the skills to a hosted container runtime.

Spec files are loaded in full. Every `specs/*.md` file except the README is appended to the system text, sorted by file name, with its complete text. That system text goes on the everyday chat, the zone narrative, and the explosion-control starter. The app sets no file-count cap and no character cap on these files, and it does not summarize, skip, or shorten one. Earlier builds stopped after 12 files and cut each file at 16,000 characters, which dropped the end of Section 28 31 00 (all of §3.8, §3.9, and the closing paragraph). The eight files in this tree total about 50,500 characters, about 9,800 more than the old cap sent.

Loading specs in full increases token use, cost, and context use on every one of those requests. The tool loop sends the same system text on each tool round of a turn (up to 16 rounds). That text goes out as one block with a prompt-cache breakpoint, so the first round of a turn writes the tool list and the system text to the cache at the cache-write rate, and the later rounds, and later turns inside the cache lifetime, read them at the cache-read rate. A request that carries tools also asks for automatic caching on the message tail, so a skill body or a tool result read on one round is cached for the rounds after it. A mode switch or an installed content pack changes the system text and starts a new cache entry. The blind claim check is one call with no tools, so it gets the system marker and no tail marker. A larger `specs/` folder in a content pack still raises the size of every request and the cost of the first round of each turn. The status line after a chat turn, a zone run, or a starter that called Claude shows the rounds, the input tokens, the share read from the cache, and the output tokens, so a cache that stops hitting is visible. The model's context window and the API request size limit still apply to the whole request; loading in full does not make the context unlimited. When the API rejects a request as too large (HTTP 413, or a 400 that says the prompt is too long), the reply or warning says so in plain words and includes the API's message. The app does not trim the request, drop a section, or resend a shorter copy, and the files in `specs/` are not changed. A too-large rejection is not retried. Rate limits and overloads are still retried with the same full request.

`max_tokens` (16000 on these paths) caps what Claude writes in one response. It is an output setting and is not a limit on the spec files. A reply the API reports as unfinished starts with an "Incomplete reply" line in the chat thread that names the `stop_reason` (`max_tokens`, `model_context_window_exceeded`, `refusal`, `pause_turn`, or `tool_use` when the tool-round limit ran out). On a zone run or a starter, the same line is listed under Warnings and Flags. A zone run's flags go into the Section 21 13 19 export, so the line is there too. The tables and figures stay on the tool plan either way. The blind claim check and the `/heavy` hosted path do not receive the spec files.

`/heavy` is the escape hatch for a heavy job. It is the only path that opens a Claude Managed Agents cloud session (a hosted container). That path is text-only reasoning on the already-computed zone packet in the message. The container is not given `skills/`, `roles/`, `modes/`, or `calcs/`, and it has no network to fetch them. The prompt does not tell the model to call `read_role`, `read_skill`, `read_mode`, or a calc tool. Those tools stay on the desktop Messages path. The model id on the session stays `claude-opus-5-5`. The reply is written back into the same project thread and labeled with the job. The hosted session is not a second conversation. Ordinary chat, Sample DI, Sample BESS, and a zone tool plan do not use it. The session is deleted when the job finishes. A failed delete is written to the `fpfa.managed` log and named on the reply. A delete that is still on the network stays tracked until that attempt finishes. Closing the window, and process exit, delete a session that is still polling or still being deleted. That sweep waits about a second so a slow network does not hold the window. The cached agent and cloud environment are reused for later heavy jobs in the same process. They are not deleted with the session.

Deterministic math is never left to the model. The double-interlock screen runs a fixed tool plan on the form. Claude may call the same tools and write the narrative. If that narrative does not quote the tool-plan volume and delivery time, the export keeps the tool-plan narrative and the tables. The rejected model draft is not written beside them. A delivery time from these tools is an optimistic screen. It is not a listed water-delivery-time calculation.

## Run from source (Windows)

Install Python 3.11 or newer (3.12 is what this prototype was exercised with), then:

```bat
cd app
py -m pip install -r requirements.txt
py -m pip install pywin32
py -m fpfa
```

`pywin32` lets the `keyring` package store the API key in Windows Credential Manager. If Credential Manager is unavailable, the app stores the key in a user-only file under `%APPDATA%\fpfa-assistant`. Settings and the status line say which store holds the key. The key is not written into the project file, the chat log, or the exported document. A source run reaches `keyring` through a short-lived child Python process (`py -c ...`), so a keyring that never answers times out instead of hanging the window.

On Linux or macOS the same commands work with `python3` in place of `py`. The key is stored in a user-only file under `~/.local/share/fpfa-assistant` (or `$XDG_DATA_HOME`), mode `0600` where the filesystem allows it. Set `FPFA_USE_KEYRING=1` before starting the app to use the system keyring instead. A missing keyring on those desktops can open a blocking password dialog, so the file is the default there.

Projects are JSON files in that data directory. Override it with `FPFA_DATA_DIR` if you want them somewhere else.

## Content updates

Settings shows the content version, **Check for updates**, and a short changelog. The check reads a manifest, downloads a newer zip, verifies sha256, and then points the saved content folder at the new tree. Until that pointer moves, the app keeps the last good pack. If the saved folder is missing or incomplete, the app uses the bundled seed: this checkout when you run from source, or the seed folder shipped with a packaged app.

The API key and the project files live in the data directory. A content update leaves them there.

The default feed is the `manifest.json` asset on the latest GitHub Release:

`https://github.com/Abe-Borg/fp-fa-content/releases/latest/download/manifest.json`

A static URL that serves the same JSON works for a mirror or a test. The feed can also be the GitHub API document for the latest release (`https://api.github.com/repos/Abe-Borg/fp-fa-content/releases/latest`). The app then downloads the `manifest.json` asset named in that document. The manifest lists `version`, `created`, `sha256`, `filename`, and `changelog`. `min_app_version` is optional.

`FPFA_CONTENT_FEED_URL` overrides the feed for this process. `FPFA_CONTENT_ROOT` pins the content folder, and a check leaves that folder in place. `FPFA_CONTENT_UPDATES=0` skips the launch check. A packaged app checks on launch. A source checkout checks on launch after a feed has been saved, or when the feed override is set. Offline, the window still opens and the last good pack stays in place.

Installed packs live under `content-packs/` in the data directory. The app keeps the current pack and one previous pack. The everyday path searches `corpus/` with `search_corpus`. The pack still carries that folder.

## Release pack

Build the zip and manifest from this checkout:

```bash
python3 scripts/build_content_pack.py --version 2026.10.1 --out dist --changelog "Short note"
```

The zip includes `skills/`, `calcs/`, `corpus/`, `specs/`, `modes/`, and `roles/`, plus `pack.json`. The build omits `app/`, project files, API keys, `__pycache__`, `_sources`, and path names for foam, clean agent, Canada, and vendor catalogs. Scope-lock sentences that name those systems as out of scope stay in the skill files. The manifest sha256 is the zip file.

Pushing a tag `content-v2026.10.1` runs `.github/workflows/content-pack.yml`, which publishes `manifest.json` and the zip as Release assets. The tag message becomes the changelog when it has text. A chat command that opens a curation pull request is not wired.

## Packaging

From `app/` on the machine that should run the app:

```bat
py -m pip install -r requirements.txt pyinstaller
py packaging\build_app.py
```

On Linux or macOS, use `python3` in place of `py`. PyInstaller builds for the OS it is running on, so a Windows `.exe` comes from a Windows run (`app\dist\fpfa\fpfa.exe`, or `packaging\build_app.ps1`). A Linux run writes `app/dist/fpfa/fpfa`. The folder includes a seed content pack, and the packaged app checks the release feed on launch. Smoke that Linux binary with `FPFA_CONTENT_UPDATES=0 ./dist/fpfa/fpfa --demo --quit` from `app/`. That runs the seed pack and the sample tool plan. It does not produce `fpfa.exe`. `python3 packaging/build_app.py --seed-only` writes the seed folder and stops before PyInstaller. On Windows, `packaging\build_app.ps1` then `packaging\build_installer.ps1` writes `app\dist\fpfa-setup-<version>.exe` (Inno Setup 6). Pushing a tag `app-v*` (for example `app-v0.1.1`) runs `.github/workflows/windows-app.yml`, which publishes that setup exe and `fpfa-windows-<version>.zip`. Content packs stay on `content-v*` tags.

The packaged app cannot start a child Python for `keyring`, because there `sys.executable` is `fpfa.exe`. Relaunching it only re-opened the app, which rejected the `-c` argument, so every save fell back to the user-only file. A frozen build therefore calls `keyring` inside its own process on one worker thread with the same timeout (8 s on Windows). That thread runs calls in the order they were made. A call that timed out still runs before any later call, so a slow delete cannot remove a key saved after it. If Credential Manager does not answer, the key still lands in the user-only file and the status line says so. `packaging/build_app.py` copies keyring's package metadata (its backends are found through entry points), collects `keyring.backends`, and on Windows adds `keyring.backends.Windows` and `pywin32-ctypes` (`win32ctypes`), keyring's own Credential Manager dependency. PyInstaller 6 hooks already collect these. The explicit flags guard against a hook change. The packaged app does not need a separate `pywin32` install. Credential Manager storage from the packaged `fpfa.exe` still has to be confirmed on a real Windows machine: save a key in Settings, check that the status line names Windows Credential Manager, and look for `fpfa-assistant` under Control Panel > Credential Manager > Windows Credentials.

## Conversation-first window

The chat thread is where work happens. Open the app, type a question, press Enter. You do not have to fill in a form or run a sample first.

The window has three parts:

- **Sidebar (left).** **+ New chat** at the top, your jobs under it, and **Settings** at the bottom. A new chat takes its name from your first question (for example "How should I split a 40,000 ft2 data hall into…"). Right-click a job (or press F2 / Delete with it selected) to rename or delete it. Deleting the open job clears the thread. **Activity** appears above Settings once a job has run. It lists zone runs, chat turns, claim checks, and heavy jobs with their status.
- **Thread (middle).** Your messages and the replies, in one readable column. Replies are rendered from markdown: headings, bullets, numbered lists, **bold**, `code`, fenced code, and tables aligned in a monospace block. Single asterisks and underscores are left alone, so names such as `t_total` stay intact. Each reply starts with a small caption naming its job (`Job <id> | <project> | <kind> | <title>`; a chat reply's caption stops at the kind, because the question is right above it). "Working on it…" shows under the thread while a job for this project is queued or running. Right-click the thread to copy.
- **Top bar.** The job name, **Mode** (brainstorm, calculator, synthesis, mixed), the **Zone details** toggle, and the **⋯** menu.

The composer is multi-line. Enter sends, Shift+Enter adds a line, and the box grows as you type. Ctrl+S saves the open job, Ctrl+N starts a new chat, and closing the window saves too.

An empty thread shows a short welcome. Two links sit under it. When no API key is saved, one link opens Settings. The other loads the sample double-interlock zone. The sample is optional and never required before a question.

The **⋯** menu holds everything else: Sample DI zone, Sample BESS room, Run zone from Zone details, Export draft Section 21 13 19, Narrate zone runs with Claude (on by default once a key is saved), Rename job, Settings, and Commands. On launch the only plain buttons are New chat, Settings, and Send.

**Zone details** is a drawer on the right, closed until you open it. It has the Basis, Zone, and Results tabs (pipe segments, time basis, trim, and the rest of the zone inputs), plus a **Run zone** button that posts the run into the thread like `/run`. The form scrolls on a short screen. It keeps its values when the drawer is closed.

On Windows the app asks for DPI awareness before it opens the window, so text is sharp at 125% and 150% display scaling instead of being bitmap-stretched. Fonts are Segoe UI and Consolas there, with a fallback on other systems.

- **Sample DI** (the welcome link, ⋯ → Sample DI zone, or `/sample-di`) creates the sample data-hall double-interlock job and runs the existing zone tool plan. It opens its own job. It does not write over the thread you were in. That path does not need an API key. The reply starts with a line that says what was loaded ("Sample loaded: data-hall double-interlock zone DH-1 (4 pipe segments, FM time basis). This is sample data, not a real building…"), then the narrative, including the ASSUMED trim line and the ASSUMED screen limit. The zone inputs are filled in under Zone details, and the same figures stay on the Results tab for export. Follow-up questions in that thread use those figures.
- **Sample BESS** (⋯ → Sample BESS room, or `/sample-bess`) creates a generic Li-ion BESS room and runs the explosion-control starter in synthesis mode. Its reply also starts with a "Sample loaded" line. That path does not need an API key. The method stays in `skills/ess-isolation-venting-and-duration/SKILL.md`. Mixture LFL and setpoints come from the LFL tool. An election or a duration the tool did not return is labeled ASSUMED. The sample room has no sprinkler zone, so the draft does not invent gallons or seconds. If that project already has a zone tool plan, the starter quotes it and those gallons and seconds govern when the narrative disagrees. Export of Section 21 13 19 still needs a zone run.
- `/run` (or **Run zone** in Zone details) runs whatever is on the zone form.
- `/new Job name` starts a named job. `/help` lists the composer commands.
- **Export draft Section 21 13 19** (in the ⋯ menu) still needs a finished zone run. Before the file is written, the app runs the blind claim check from `skills/blind-claim-check/SKILL.md`. The QA checker is `roles/qa-specialist/ROLE.md`. That turn receives only the claim list and the short cites. It does not receive the draft, the spec section, or the designer's notes. Claims come from the narrative the export writes, including a figure with no section and a sentence that names a section a tool already named. A tool string may be shown as a package assertion. It is not a passage from the standard, and copying it back as the cite does not support the claim. Export waits until every such claim is Supported. That result does not mean the narrative was compared to the standard. Engineer-of-record review still applies. A cite marked `NOT PULLED` stays open. The check is a `claim` job on the inbox, labeled `Job <id> | <project> | claim | <title>`, and the result is posted into the same project thread. It does not open a hosted container. The draft section stays 21 13 19.
- A normal message, with a key saved, uses the everyday path and includes the earlier turns in that project. The window does not wait on the call. The question is saved on the job right away, and the reply is written into the thread when it arrives. The path can read a specialist role, a mode, and a skill, and it can call the calc tools. The Mode menu (or `/mode`) chooses brainstorm, calculator, synthesis, or mixed. If a tool plan has already run, the request repeats those governing figures. The chat reply does not replace the tables or the export. **Narrate zone runs with Claude** in the ⋯ menu decides whether `/sample-di`, `/sample-bess`, and `/run` also ask Claude for the narrative. Numbers in the tables and the export stay on the tool plan either way.
- The inbox (Activity, in the sidebar) is the queue of zone runs, chat turns, an explosion-control starter that calls Claude, a blind claim check, and a heavy job. Two workers run the long jobs. The composer stays usable while a job runs, including a second message and a switch to another project. A result that finishes later is labeled with its job id, project name, and kind, and it is written onto the project that started it. A local tool plan with no model call still finishes before `/sample-di`, `/sample-bess`, or `/run` returns, and it is recorded on the same inbox.
- `/heavy task` sends that task through the hosted runtime and posts the reply into the same thread. The turn is text-only reasoning on the zone packet already in the message. It does not call `read_role`, `read_skill`, `read_mode`, or a calc tool, and it does not recompute zone gallons or seconds. It does not open another project. A typed question, `/sample-di`, `/sample-bess`, and `/run` stay on the path they already had.
- Jobs are JSON files in the data directory. A first `/run`, `/help`, or chat message keeps whatever is already on the zone form. The sample zone is generic. It is not a constructed building.

Settings has two sections. **Anthropic API key** has the key field, Save key, Check key, and Clear key, and says which store holds the key. **Content pack** shows the content version, Check for updates, and What's new. The content feed URL and the content pack folder are under **Advanced**.

Blank trim (5 gal) and the screen-limit seconds are labeled ASSUMED on the Zone details form, in the thread after a run, on the Results tab, and in the export. Pipe gallons and trip time are calculated. A value the designer types is not assumed. A designer judgment the tools did not return is labeled use best judgment. That label is not ASSUMED and it is not a calculated figure. A delivery time from these tools is an optimistic screen. It is not a listed water-delivery-time calculation.

Check key in Settings calls the models endpoint for `claude-opus-5-5` and does not generate text.

## Project record

Every job has rows in one SQLite database, `fpfa.db` in the data directory. The record is the durable store the agent-team prototype builds on (`docs/prototype-plan.md`, Phase 1). It holds facts (basis of design and assumptions, each with a label), evidence (cites with edition, section, a short paraphrase, and a status of held, NOT PULLED, NEEDS HOLD, or PACKAGE ASSERTION), calculation records, findings, open questions, decisions, handoffs, tasks, agents, and an append-only event log. Documents are exports of the record. Nothing in the record is edited by hand.

Calc tools record themselves. When a zone run, a starter, or a chat turn calls `zone_trapped_volume`, `dry_delivery_screen`, `di_trip_to_water`, `density_area`, `hose_duration`, `nitrogen_gate`, `elect_di_trim`, `releasing_truth_table`, `resolve_pipe_id`, `lfl_setpoints`, `fp_calc`, or `fa_calc` on a job, the tool, its inputs, its output, the content version, and the caller (`tool-plan`, `narrator`, or `lead`) are written as one calculation record keyed by a hash of the inputs. A second call with the same inputs on the same job returns the recorded output and counts a replay instead of writing a second row. That is the duplicate prevention the recovery phase relies on. A tool session that has no record attached, which is how the calc tests and the form's pipe-ID lookups run, writes nothing and behaves as before.

Five record tools are on the everyday path beside the calc tools: `record_fact`, `record_evidence`, `record_finding`, `open_question`, and `record_decision`. `read_record` shows the job's record with row ids. A fact, finding, or decision carries exactly one label: calculated, ASSUMED, use best judgment, or a cite class (CODE, OWNER, PRACTICE, PARA, HB). A row with no label, or an evidence row with an unknown status, is refused and the model sees the refusal as a tool error. Rows written by the model carry the agent name of the context that wrote them.

Opening a job imports it into the record once: the basis fields become facts (editions as CODE, the insurer as OWNER, the AHJ and hazard notes as use best judgment) and the tool calls in a saved zone run or starter become calculation records. Deleting a job deletes its record rows. The record does not change the chat thread, the zone form, the tables, or the Section 21 13 19 export.

## Design Basis and Open Questions export

**Export Design Basis and Open Questions** in the ⋯ menu writes a second Word document from the job's project record (`app/fpfa/design_basis_docx.py`). Every line is read from the record; nothing is typed by hand and nothing from the chat thread is copied in. The sections are: basis of design, with the cites held on the record; elections, read from the trim, releasing, and nitrogen calc records and from recorded decisions; calculation records, one row per record with the caller, the time, the replay count, the key figures with their labels, and the inputs as passed; findings grouped by contributor with the ids they rest on; checker verdicts, or a line saying no blind claim check has run on this record; assumptions, every ASSUMED row and every ASSUMED flag a calc returned; open questions and RFIs, with answered ones listed after; and the handoff log. The export needs a job with at least one recorded calculation, fact, or finding. It does not wait for the blind claim check in this phase; the checker that reads from the record arrives with the team in Phase 3, and the document says so when no check has run. The Section 21 13 19 export is unchanged and still waits for every claim to be Supported.

## The team

A chat turn on a job is the lead of a team (`app/fpfa/team.py`). The lead is the everyday path with three more tools. `list_specialists` names the specialist roles in the content pack: every `roles/<slug>/ROLE.md` except the everyday shell and the QA checker, so `fa-releasing`, `fp-sprinkler`, and `spec-draft` in this tree. `delegate(specialist, brief, inputs)` runs that specialist in its own context: its `ROLE.md` is the system text, with the skill index and a paragraph that says how to record its work (`spec-draft` also gets the spec files, the others do not). The specialist has the calc tools, the content tools, the record tools, and `handoff`, but not `delegate`, so it cannot delegate in turn. Its user message is the brief, the lead's inputs, its own earlier contribution on the job, any handoffs waiting for it, and the record summary with row ids. Everything it writes carries its slug. The lead gets back a contribution: the specialist's summary and the findings, questions, cites, handoffs, and calc record ids it wrote. The lead's handoff to the specialist is written to the record first and marked returned with the summary; a specialist that fails leaves it cancelled and the agent marked error.

`handoff(to, brief, payload)` writes a pending row for another agent. No specialist talks to another directly in this version. A handoff is delivered when the lead next delegates to the receiver, and it is marked returned when that delegation finishes. That is what makes every substantive exchange a row with a sender, a receiver, times, and content.

`request_check` runs the blind checker over the record's findings. Each finding is one claim. Its cite is built from the rows it names in `supports`: a calc record becomes a package assertion with that tool's figures, an evidence row becomes its document, edition, section, and note, and a finding with no supports, or one that rests on a NOT PULLED or NEEDS HOLD cite, is `NOT PULLED`. The checker is the same QA role and the same one-call blind turn as the Section 21 13 19 check; it sees only the claim list and the cites. A verdict is written onto each finding. A finding that rests on a calc record alone is Supported only if the package figures carry every number in the claim, as before. The outcome is logged on the record, and the Design Basis export now waits for it: a record with findings exports only after a check that is current (no finding added or changed since) supports every one. A record with no findings has nothing a checker could judge, so the tool-plan figures export on their own with the no-check line.

The lead's system text gains one paragraph on the team when a record is open. Usage is summed across the lead and every specialist it ran, and the status line after the turn shows the total. A chat without a record, which is how the tests drive the plain loop, has none of this.

## Tests

```bat
cd calcs\fp
py -m unittest test_formulas test_di_zone

cd ..\fa
py -m unittest discover -s tests

cd ..\..\app
py -m unittest discover -s tests
```

`calcs/fp/test_formulas.py` is the seed kernel suite (79 tests in this tree). `calcs/fa` is the fire-alarm library suite. Quote-only tests that needed raw code text are skipped, because that text is not in the repo. The app tests run the sample zone, the Word export, the blind claim check before that export, the Claude tool loop against a fake response, the key-file fallback, the packaged-app keyring path (`keyring` runs in-process and `fpfa.exe` is not relaunched), the PyInstaller keyring flags, the `/sample-di` starter, the `/sample-bess` explosion-control starter, the inbox queue (workers, composer stays usable, out-of-order results stay on their job), the `/heavy` hosted hatch (one cloud session, text-only prompt, reply back in the same thread, a failed session delete is visible, close and process exit delete an in-flight session, ordinary paths do not call it), and the chat-first window (a first question with a saved key gets a reply without Sample DI, Sample DI seeds its own job when chosen, only New chat, Settings, and Send are plain buttons on launch, Zone details starts closed, the composer keys, rename and delete, and the Working on it line). `tests/test_chat_render.py` checks how replies are drawn (markdown markers, job captions, aligned tables) and how a job is named from its first question. `tests/test_spec_loading.py` checks that spec files load in full: each returned spec equals its source text, more than 12 files all come back in order, a file far past 16,000 characters keeps its middle, its end, its Unicode, and its trailing text, README is skipped in any letter case, and a missing or empty `specs/` folder gives no spec notes. It also checks that the whole current Section 28 31 00, including §3.8, §3.9, and its last paragraph, is in the assembled system text and in every round of a stand-in Messages request, that a too-large rejection is shown once and never resent shorter, and that an unfinished reply is labeled in the chat, the zone run, and the starter. `tests/test_team.py` checks the team: the specialist roster excludes the shell and the checker, a specialist's system text is its role file plus the skill index, delegation runs in the specialist's own context with the specialist tool list and writes rows as that specialist, a pending handoff is delivered with the next delegation and prior work is shown, a non-specialist or an empty brief is refused, a failing specialist leaves its handoff cancelled, a lead turn with a record gets the team tools and sums the team's usage, a turn without a record keeps the plain tools, the record-fed checker builds claims and cites from the findings and applies the blind verdicts with the package rule, and the export gate opens on an all-Supported current check and closes when a finding changes. `tests/test_design_basis.py` checks the Design Basis export: every section comes from the record, the eight tool-plan figures for the sample zone appear with the labels `docs/known-answer-dh1.md` expects, checker rows are shown when a claim check exists, an empty record exports a document that says so, a replayed calc shows its count, and nothing from the thread is copied in. `tests/test_record.py` checks the project record: labels and statuses are enforced, identical calc inputs make one row and a replay count, handoffs move pending to delivered to returned, writes from eight threads all land, a JSON job imports once, a tool session with a record writes calc rows and one without writes nothing, a zone rerun replays all eight calls, narrator and lead calls carry their agent name, and the record tools write rows the model asked for. `tests/test_prompt_caching.py` checks the cache markers: the system text goes out as one block with a breakpoint and the same text on every round, a request with tools asks for automatic caching on the message tail, the caller's message list is not marked or changed, the claim check gets no tail marker, and the usage totals and the status-line summary add up. Content-pack tests serve a local manifest and zip. Those tests do not need a display.

Window tests need a display and the `tkinter` module (`python3-tk` on Debian or Ubuntu). Without that module, importing the window fails and those tests do not run. A run with `DISPLAY` unset skips the window tests and still runs the rest.

## Layout

| Path | Role |
| --- | --- |
| `app/` | Desktop application |
| `skills/<slug>/SKILL.md` | Design methods the model must read |
| `roles/<slug>/ROLE.md` | Specialist role prompts. `everyday` is the chat shell. `qa-specialist` is the blind claim check |
| `modes/<slug>/MODE.md` | Everyday-path modes: brainstorm, calculator, synthesis, mixed |
| `calcs/fp` | Fire-protection formulas, shop pipe IDs, DI zone screens |
| `calcs/fa` | Fire-alarm calculation libraries |
| `specs/` | Draft CSI sections, one file each, sent to the model in full. README is not a spec. Double-interlock draft language is 21 13 19 |
| `corpus/` | Paraphrased reference notes (edition pins and decision logs). `search_corpus` searches this folder |
| `docs/` | Plan of record and known answers for the prototype. Not part of the content pack |

## Not in this prototype

`packaging/build_app.py` builds a distributable folder, and on Windows that folder contains an `.exe` with a seed content pack. `packaging/build_installer.ps1` wraps that folder as `fpfa-setup-<version>.exe` for a GitHub Release. Settings can install a newer pack from the release feed. Publishing a pack from chat is not wired; a `content-v` tag runs the content-pack workflow, and an `app-v` tag runs the Windows app workflow. Windows Credential Manager still has to be confirmed on a Windows machine. No second model vendor. No foam, clean agent, mist, building-deluge, or single-interlock design path (those inputs return an RFI and stop). Outdoor oil-filled transformer apparatus water spray stays on the desktop path through `power-block-transformer-water-spray`. Wet and dry can be named on the form; the finished vertical workflow is the double-interlock zone. The inbox queues long jobs on workers and labels a result with the job it belongs to. The blind claim check is a `claim` job on the Messages path. `/heavy` is the only hosted container path, and it is text-only on the zone packet already computed on this machine.
