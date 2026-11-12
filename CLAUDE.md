# CLAUDE.md

Guidance for coding agents working in this repository. `docs/prototype-plan.md` is the plan of record: it says what is in and out of v0, so read it before a change of scope. The README describes everything here at full length; this file is the rules and the commands.

## What this is

+Cynosure: a Windows desktop assistant for hyperscale data-center fire sprinkler and fire-alarm design. `app/` is a Python program whose window is a web page in Microsoft Edge WebView2 (a local server, a React page, pywebview). Everything else is a content pack the app loads at runtime: `skills/`, `roles/`, `modes/`, `calcs/`, `corpus/`, `specs/`. Claude writes narrative and reads methods. Every number comes from `calcs/`.

The product was FP/FA Design Assistant. The `fpfa` package name, the `FPFA_*` variables, the data directory name, the keyring service name, and the installer's AppId are not renamed: an existing install and its data depend on them.

## Ownership and division of responsibilities

**Owner direction, November 11, 2026.** These rules govern future work. Existing differences between the repository and the Grok team's working materials remain unreconciled; do not assume either entire collection is authoritative or overwrite either one wholesale.

### Product and content ownership

- **Abe owns product priorities and consequential decisions.** Choom coordinates independent review, consolidates feedback, and prepares handoffs for Abe. Review comments and another agent's suggestions are not permission to expand a task.
- **Claude coding agents own the application implementation:** desktop UI, orchestration, project records, API integration, content loading and updating, export mechanisms, recovery, application checks, and application tests.
- **The Grok Bot team owns the engineering substance:** skills, specialist engineering guidance, reference corpus, specification content, engineering assumptions, formulas, and calculation implementations. Its research and "training" develop this material; that does not itself establish engineering validity or imply model-weight training.
- **The FP/FA App Grok Bot is the primary content integration coordinator.** It coordinates publication of the team's reviewed material into the repository's content pack, involving the relevant specialists and factories as needed. This is a responsibility assignment, not unrestricted permission to publish or change repositories.
- The Grok team can review application behavior and recommend app changes. Claude can identify content defects and propose corrections. Neither role silently takes ownership of the other's work.

### Classify by purpose, not file extension

The content pack includes executable engineering calculation code, not only Markdown. Engineering content may also appear inside Python, tests, schemas, prompts, or templates. Application logic and engineering substance can coexist in one file.

Claude may change how the app invokes a calculation, preserves precision, records dependencies, displays results, or reports failures within the assigned task. Claude must not independently change the calculation's engineering formula, assumptions, thresholds, interpretation, or authoritative expected values.

Likewise, orchestration prompts are application work, but embedded discipline rules are engineering content. Export layout is application work; engineering specification language is content. When a change crosses this boundary, separate the concerns and coordinate both owners rather than treating the whole file as app-owned.

### Required behavior when content is implicated

1. Preserve the evidence: affected file/version, reproducible behavior, expected versus observed result, and whether the issue is application behavior, engineering content, or both.
2. Route the engineering question and any proposed content correction to the FP/FA App Grok Bot and appropriate specialist through the established handoff process. Do not silently patch production skills, engineering role instructions, corpus, specifications, or calculation substance.
3. For a mixed change, agree on the interface, inputs, units, precision, outputs, error behavior, provenance, and compatibility expectations. Claude implements the app side; the Grok team supplies and validates the engineering side.
4. If source validity or ownership is unresolved, flag the limitation and continue independent app work. Do not invent an engineering answer to unblock coding. Escalate material scope, ownership, or engineering decisions to Abe through Choom.
5. A content correction must return to its authoritative editable source and controlled publication path, once those are established. An isolated repository patch must not become a hidden competing version.

### Tests and fixtures

Claude may create clearly labeled synthetic fixtures, mock skills, and deliberately incorrect inputs in isolated test locations. They must not be promoted into the production content pack or represented as validated engineering.

Application tests may verify loading, precision preservation, recording, failure handling, and consistency against a documented contract. Expected engineering answers must have an independent basis or be explicitly labeled provisional/synthetic. Do not derive an oracle solely from the implementation under test or weaken a test merely to make it pass.

Claude may propose a content schema migration and supply migration tooling. Do not apply semantic changes or publish migrated engineering content without the content owner's review and the applicable task authorization.

### Versioning and handback

Treat app releases and content-pack releases as distinct, compatible artifacts. Record the app revision and the content/calculation identities used by tests and delivered builds. Hashes establish identity and integrity, not engineering correctness.

Do not perform blind bidirectional syncs. Do not silently choose the repository or Grok working collection as the master. Until reconciliation establishes authoritative sources and a publication process, preserve both and identify which frozen snapshot each run uses. `docs/content-provenance.md` records where the two stand: a correction that was made to a packaged file is listed in that page's table with the test that guards it, so that it is not a hidden competing version.

Every handback must distinguish app changes, content dependencies or proposed changes, tests actually run, untested behavior, and unresolved engineering validation. No software test result constitutes code compliance, manufacturer approval, or qualified engineering sign-off.

## Engineering rules

These hold in everything the app writes, shows, and exports. Changing one is an engineering decision, not an application change (see Ownership).

- Numbers come from the calc tools. The model never computes gallons, seconds, gpm, psi, scfm, or the releasing table.
- Three labels stay distinct: calculated, ASSUMED, use best judgment. A delivery time is an optimistic screen, not a listed water-delivery-time calculation.
- Scope is wet pipe, dry pipe, double-interlock preaction, the detection and releasing that trip them, and outdoor oil-filled transformer apparatus water spray. Foam, clean agent, water mist, building deluge, single-interlock, and non-interlock are refused. Canada only through a skill's Country gate; CAN/ULC and CEC Section 32 bodies stay NEEDS HOLD.
- NFPA 13-2025 is the delta baseline. An unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified. Cite the section and the edition together.
- The double-interlock draft section is 21 13 19. Dry pipe is 21 13 16. Never cross them.
- Release is the detection leg AND P, the pressure drop from sprinkler operation. Low air is supervisory only and is never a release input. `docs/releasing-basis.md` is the basis, and it is unresolved as engineering: no standard was opened and no qualified engineer has reviewed it. Do not write that it was verified, and do not turn a section number a reviewer reported into one that was read.
- The wording detector is `releasing.release_wording_hits`; tests run it over the pack, `docs/`, the README, and this file. The pack lint (`calcs/fp/test_pack_content_lowair.py`) carries a copy of its rules: change both together. `releasing.py` is the one reader of the kernel's releasing output. It still accepts the names the relabel retired when it opens a run saved before it; keep that, and never show those names to a model.
- The size exemption is judged on the zone total and exists once: the recorded `dry_delivery_screen` row is what the narrative, the tile, and both documents print (`workflow.exemption_answer`). Never govern a copy in memory. A screen with no zone total never says the exemption is met.
- A figure that decides a yes or no at a threshold is run on the record it came from, not on the caller's rounding of it (`coherence.EXACT_FROM_SOURCE`).
- A zone run takes the form's values as typed. Never put a default or a 0 in place of a blank or a typed 0 (no `or 40`): `workflow.validate_di` names what a run cannot use (`inputs.POSITIVE`, `inputs.NOT_BLANK`, `inputs.run_problem`). Which values are meaningless is not an engineering threshold; a minimum density would be, and is content.
- A change of unit is a calculation, and only `fpfa.units` makes one, by the definitions alone: the `convert_units` tool and `set_input` given a figure with its unit, each recorded. No cubic feet while the gallons constant is open, no K-factor, and never gauge to absolute. During a turn a calc tool refuses the designer's own SI figure in a field that takes US units (`calc_tools.si_figure_problem`, set by `designer_words`).
- No raw standards text, no vendor catalog numbers, no job, client, or personal names anywhere in the pack. Tests scan for them and fail the build. Paraphrase; keep section numbers, edition years, and numeric screens.
- Do not add a code threshold to `calcs/fa/lib/lfl.py`. Percents are inputs.

## What may be claimed

- Five statuses are never merged: software hardening, offline regression evidence, installed Windows evidence, live-model evidence, and engineering validation. Only the first two exist for this tree. The acceptance test of 0.2.0 (`NEXT-STEPS.md`) is another party's live run on an older version: quote it as theirs, and never as live evidence for this one. A document, a report, or a commit message that lets one stand for another is wrong. Do not present someone else's reported test counts as runs you made.
- The record check is a trace check. It says whether a finding is consistent with the rows it cites. Nothing in the app, the docs, or an export may call it verification or say a standard was checked; `checked_against_standard` stays `False`, and no tier title may read as verification. Every export names verification against the primary standard and a qualified engineering review as not performed (`checker.LADDER`).
- What the checker did not say is never a verdict. A reply that was cut off ends the check: no finding is changed and the run is a `check_incomplete` event, never the latest check. A claim a finished reply skips is "No verdict" and goes back to not checked. Do not default a missing verdict line to anything.
- What the checker said beyond its verdict, the passage it quoted and its reason, is kept as its reading (`checker_cite`, `checker_reason`), apart from the application's own reason, and shown as "The checker's reason (the same AI model, a second pass)". It is never a verdict and never a source. `claim_check.verdict_rows` reads a verdict in any case, markup, or common numbering; never let it read a line that names no verdict. A check stops between its requests on the job's cancel.
- A supported finding is in the first tier only when the application itself matched something in it to the rows it cites: a figure with its unit, or the releasing record's own expression (`checker._held_by_app`). Otherwise it is `checker`, the checker's reading alone. Do not add a path that gives `source` on the checker's word. In a cite, only a zone input, a basis field, or a GIVEN fact is a PROJECT INPUT; any other fact is a RECORDED FACT and the team's own statement.
- A Design Basis with work missing is exported and says INCOMPLETE DRAFT: never block it for that, and never let it look whole. Both exports keep their gates: a current trace check and nothing out of date (`checker.export_reason`), and for Section 21 13 19 every claim Supported.
- A test that involves an agent plays a scripted model. Say so where it is written and where it is reported: a scripted pass shows what the application does, never what the live model does. `docs/acceptance-tests.md` keeps the table of tested, simulated, and unrun.
- `python -m fpfa.live_eval` runs against the live model and is billed. Never run it from a test or a build, and never to see whether a change works: the owner runs it. Its tests inject a scripted client through `Runner(client_factory=...)`.
- An evaluation check has to be able to fail. Before adding one to `live_eval.py`, name what would fool it: a replayed calc row is not collaboration, a bare agreement is not a position, a checker that approves everything is not a check. A scenario blocked on an owner's confirmation is reported as blocked, not chosen for them.
- A failure does not un-spend what ran before it: an event that ends on an error is written `failed` with the usage that had finished (`claude_client.attach_usage`). A failed request reports no usage; say that, never guess a figure, and never call `--max-usd` or any other guard a spending limit.

## How the app is built

The record and the team:

- The content pack is replaceable. Nothing in `app/` hardcodes a method, a role, or a mode. Loaders read them from disk.
- Agents never open the project record directly. A calc tool records itself; a model writes facts, findings, questions, and decisions through the record tools. A `ToolSession` without a record writes nothing, and tests rely on that.
- The project inputs are record facts (`inputs.py`). The form and the lead's `set_input` write them; a specialist never does. Every basis field goes through `Record.sync_form`, an empty one too: never leave a blank field out of the sync.
- A finding or a decision is never edited: it is replaced (`replaces`) or withdrawn, and the old row stays as history. A calc that took a figure from an alternative is an alternative.
- What the app derives, no model types: what is out of date and why, and where a calculation's cites name another edition than the job states (`coherence.py`), the tier a finding earned and what a design basis is missing (`checker.py`), the status block and `/status` (`status.py`), the Team block under a reply (`team.py`), the figures the reply audit could not find (`reply_audit.py`), who read which skill (`content_use.py`), and the Results tab's tiles (`results_panel.py`).
- The record reconciles a change only for the tools in `coherence.BINDINGS` and `DERIVED`. A tool with no entry is not tracked, and every view says so; do not let an untracked path imply it was reconciled. A calc row whose `calc_identity` differs from the installed pack's is out of date. The identity and the content fingerprint hash a file with its line endings set aside (`calc_tools._identity_bytes`): never hash a pack file's raw bytes for an identity.
- The edition hold (`coherence.edition_gaps`) compares two labels: the edition a calculation's own cites name and the edition the job states. It never says a rule applies, or does not, in another edition. Do not pass an edition to the kernel and do not clear the hold on a rerun; whether the kernel holds another edition is content (see Ownership).
- A figure is a number and a kind of unit (`quantities.py`); the trace check and the reply audit match on the pair. The trace check reads a claim's figure in every unit the module knows (`claim_figures`); the reply audit reads the eight in `FIGURE` and the SI flow, area, volume, pressure, and density units of `_REPLY_SI` (`reply_figures`). A stored `{"value", "unit"}` pair has the class of its unit, and so does a conversion's `{"value", "from_unit"}` request, its unit read as `fpfa.units` reads it: never hold a figure whose unit is beside it as a number with none. A new unit gets a class of its own in `_FAMILIES`, and a field-name part goes in `_NAME_UNITS` only when the kernels use it as a unit. A figure on an out-of-date row is out of date whatever a finding or an earlier reply says.
- A Results tile is a calc tool's output and nothing else: `results_panel.py` prints a field of the tool result with the narrative's rounding and words, computes nothing, and the page formats nothing.
- How the team is run is content: `roles/lead/ROLE.md` and the "Working with the team" section of each specialist's role. `team.py` holds the tools and the plumbing. A `consult`, a review, or an objection exists only when a model made it. Do not add code that manufactures one. Those orchestration prompts are application work; the discipline rules in the same role files are engineering content (see Ownership).
- The inbox is in memory; the record is all that survives a relaunch. `Record.recover()` runs once at launch and only marks: nothing is re-run on its own. One window per data directory (`instance_lock.py`).
- A record SQLite cannot read, or whose quick check fails, raises `RecordDamaged` and is never written. It is moved aside (`record.move_aside`) only on the designer's yes or `--move-damaged-record`, and never deleted. Only SQLite's corrupt and not-a-database codes, or the quick check, make a record damaged (`record._says_damaged`); a lock, a file or folder that cannot be opened or written, or a full disk is `RecordUnavailable`, which ends the launch and is never offered to be moved aside.

The model client:

- The model id is `claude-opus-5-5`. The Messages client sends no `temperature`, `top_p`, `top_k`, or forced `tool_choice`, and never disables thinking. Do not add a second model vendor.
- The system text goes out as one cached block and stays byte-identical across rounds. Anything that varies per turn goes in the user message, which is where the lead's status block goes.
- A streamed request is the request `create()` sends, byte for byte. Do not add a field to one path only. Every request a job sends streams: a chat turn with its listener, everything else through `claude_client.streamed_create` with none. At the output ceiling a request that is not streamed outlasts the HTTP timeout; never hand a job `client.create` directly. Only the lead's reply is drawn in the thread.
- `max_tokens` caps the model's thinking and its reply together, and thinking cannot be turned off. Every request asks for `claude_client.MAX_OUTPUT_TOKENS` (64,000, the owner's figure); the checker's `claim_check.CHECK_MAX_TOKENS` is the same constant. A record goes eight claims to a request (`checker.CLAIMS_PER_REQUEST`). Do not lower any of them to save output, do not write a literal `max_tokens` at a call site, and keep the reply's `stop_reason`.
- Model prices live only in `usage_report.py` as a dated snapshot (`RATES_PER_MILLION`, `RATES_DATE`). Change both together. Every billed request closes on a record event the cost report counts (`usage_report.USAGE_KINDS`): a new request path adds its kind there. A trace check run inside a turn is `within_turn`: its tokens count, its time is already the turn's.
- A spend cap, a spend limit, or a billing error is never sent again (`claude_client.spend_stop`, `SpendLimitReached`); the tier's cap is told from a rate limit by its error code, never by its wording. A `retry-after` is waited out whole up to `RETRY_AFTER_MAX`, or the request stops. Every wait is on the job's cancel (`AnthropicMessages.cancel`): never sleep where Stop cannot end it. The desk builds a client with its key alone and sets the cancel on it (`desk._model_client`), as stand-ins are built.
- Every request's id and workspace are kept (`AnthropicMessages.requests`, a stream's from the stream) and written to the job on an `api_requests` event when the job ends (`Desk._note_client`). Keep them out of the usage dicts, which hold numbers only.
- The key is read once at launch and kept (`Desk._api_key`). Do not call `load_api_key()` on a click path: on a Windows source run it starts a child Python. Do not break the frozen-app path in `keystore.py`.

The window:

- The window is a web page. `desk.py` holds every rule the window follows and needs no toolkit; `web/server.py` serves the page and the API; `web/shell.py` shows it. The page draws the state and posts actions; it decides nothing about a job. Do not add a second UI stack, bring tkinter back, or move a rule into the page.
- The window is a job list, a thread, and a job panel whose tabs are Inputs, Results, and Team. There is no "Zone details" and no drawer, so no string the app writes may send a designer to one. What is in the panel lays itself out by the panel's width (`@container panel`), never the window's.
- The designer does not choose a mode: there is no Mode menu and no `/mode`. The app picks one per path, `modes_loader.CHAT_MODE` for a typed question and `NARRATION_MODE` for a zone narration and the explosion-control starter. A job's saved `mode` from before is not read.
- The server stays standard library, bound to 127.0.0.1. Every `/api` request carries the launch token; a foreign Host or Origin is refused. A new action is one entry in `server.ACTIONS` that calls one `Desk` method. Nothing in the page fetches from the network.
- `Desk` state changes only on the desk's thread: an action under `Desk.call`, or a callback a worker put on `Desk.queue`. A worker never touches a `Var`, `chat_log`, or a counter. A change bumps `revision` through `_touch()`; a change to the conversation goes through `_render_chat()`; a form change the page did not make goes through `_form_loaded()`. A native dialog never runs with `Desk.lock` held.
- The working line names a tool or a file. It never shows a tool's inputs or its result.
- A CSS rule never names a colour: it reads a token from `styles.css`. A scheme defines every token in `theme.TOKENS`, in `theme.py` and `styles.css` alike.
- Every rule that colours text reads at 4.5:1 on the background, the surface, and a raised card in every scheme (`test_acceptance_report_030.TextContrastTests`). Secondary text is `--ink-dim`; text in a status colour is mixed toward `--ink`. `--ink-faint` is for what is not text.
- While a job works on the open job, a finished tool marks the Team tab due and `pump()` reads it again at most every `TEAM_REFRESH_SECONDS`. Never read the record on every event.
- What the pointer can work, the keyboard can. A control that opens a menu is a `MenuButton`; a clickable row or card is a button. The keyboard's ring is `:focus-visible`, never `:focus`.
- The license is PolyForm Shield 1.0.0; `test_branding.py` keeps every place that states it in step. The installer's license page reads the root `LICENSE` and nothing may skip it. A bundled package with no license text fails the build: supply `app/packaging/third_party_licenses/<name>-<version>.txt`, never silence the check. The page's build fails on a module in its bundle that is neither an npm package's nor one of the page's sources, such as a helper Vite writes in: turn off what writes it, as the modulepreload polyfill is, or attribute it to its package in `vite.config.ts`. Never let one through unlisted.

## Layout

| Path | Role |
| --- | --- |
| `app/fpfa/` | The app. Beyond the modules named above: `claude_client.py` the tool loop, the streamed call, and the retries; `calc_tools.py` the tool schemas and the tool session; `record.py` the project record (SQLite); `workflow.py` the DI tool plan; `claim_check.py` the blind checker for the Section export; `spec_docx.py` and `design_basis_docx.py` the exports; `jobs.py` the inbox |
| `app/frontend/` | The page: React and TypeScript, built by Vite into `app/fpfa/web/static` (committed) |
| `app/packaging/` | PyInstaller build, Inno Setup script, third-party notices, icon |
| `app/tests/` | App suite. `team_scenario.py` is one job scripted end to end; `test_hardening.py` holds one class per defect two reviews found, `test_acceptance_report.py` one per defect the acceptance test of 0.2.0 found, and `test_acceptance_report_030.py` one per finding the acceptance test of 0.3.0 found |
| `calcs/fp`, `calcs/fa` | Deterministic kernels and their tests. Engineering content (see Ownership). In `calcs/fp`, `formulas.py`, `run.py`, and `test_formulas.py` are staged from the kernel source (`scripts/check_fp_kernel_reproduce.py`); `di_zone.py` is pack-only |
| `skills/`, `roles/`, `modes/` | One folder per item with one markdown file (`SKILL.md`, `ROLE.md`, `MODE.md`) and `name` and `description` frontmatter. Skills and the specialists' discipline rules are engineering content. `roles/lead` runs the team; `fp-sprinkler`, `fa-releasing`, and `spec-draft` are the specialists; `qa-specialist` is the checker; `everyday` is the shell for a turn with no record |
| `specs/`, `corpus/` | Engineering content. Draft CSI sections, sent to the model in full; paraphrased pins and notes, searched by `search_corpus` |
| `docs/` | Plan of record, known answers, acceptance and recovery protocols, live evaluation, releasing basis, content provenance, milestone hand-backs, the app/content hand-back for the content team. Not part of the content pack |
| `NEXT-STEPS.md` | The reviews of the 0.2.0 and 0.3.0 acceptance reports against the source: what 0.3.1 and 0.3.2 fixed (section 0b for 0.3.2), what is still open, and the owner's decisions and open questions. Not part of the content pack |
| `scripts/` | `build_content_pack.py` runs the strip scan (`check_pack_strip.py`), leaves out `_sources`, catalog, and the held draft, stops on a foam or clean-agent path, and refuses any file that holds an API key. `check_content_tag.py` is the content workflow's gate: a `content-v*` tag publishes only from main |

## Working here

- Python 3.11 or newer; 3.12 is what the suites are run with. Install `app/requirements.txt`. Node.js 22 builds and tests the page. The target machine is Windows.
- Tests, from the folders named. Run all four before a push and put the counts in the pull request body, which is a handback (see Ownership); `.github/workflows/tests.yml` runs them on every pull request.
  - `calcs/fp`: `python -m unittest discover -s . -p 'test_*.py'`
  - `calcs/fa`: `python -m unittest discover -s tests`
  - `app`: `python -m unittest discover -s tests`
  - `app/frontend`: `npm test`
- After a change under `app/frontend`, run `npm run build` there and commit `app/fpfa/web/static` with it: `test_web.py` fails on a stale page. `npm ci` installs the exact dependencies; a new npm dependency must ship its license text. Node's type stripping runs the page's tests: no TypeScript parameter properties or enums in `src/` modules the tests import.
- Run the app from `app/` with `python -m fpfa`. `--browser` opens the page in the default browser, `--serve --port <n>` serves it and opens nothing, `--demo --quit` runs the sample with no window, `--theme <id>` picks a colour scheme for one run, `--move-damaged-record` moves a record SQLite cannot read aside without asking.
- `FPFA_DATA_DIR` moves the data directory. `FPFA_CONTENT_ROOT` pins the pack. `FPFA_CONTENT_UPDATES=0` skips the launch feed check. `FPFA_THEME`, `FPFA_REDUCE_MOTION=1`, and `FPFA_EFFORT` set the scheme, the easing, and the model's effort for one run; nothing in the app sets `FPFA_EFFORT`.
- No test needs a display. A scripted agent is a list of moves as in `tests/team_scenario.py` (`call(use("tool", arg=...))`, `say("text")`): one script per agent, and a move left over fails the test. A window test opens a desk through `Loop()` (`tests/desk_loop.py`), calls its actions, runs the workers' callbacks with `update()`, and reads `Desk.snapshot()` and `Desk.thread_text()`; a dialog message is a `Desk.notices` entry, and a save dialog is `Desk.shell.ask_save_path`, which a test patches.
- Look at the window after a change to it: serve the scheme to check, `python -m fpfa --demo --serve --theme linen`, then `node frontend/tools/shoot.mjs "<url>" <dir> linen 2` (`<url> <dir> [scheme] [scale]`), or drive it with Playwright. Check a light scheme (`linen`) and a device scale above 1. The page draws the scheme the app serves, never the one its address names; the tool stops when they differ.
- Regenerate what a change shows: `python tests/docs_pictures.py` from `app/` for `docs/screenshots` (taken from the scripted scenario, and the README says so), and `python packaging/make_icon.py` for the icon.
- When behavior changes, update `README.md` in the same change. Do not shorten it to make room; add what is necessary. When dependencies change, update `app/requirements.txt`. When a phase, gate, or decision changes, update `docs/prototype-plan.md`. When what was tested, simulated, or unrun changes, update the table in `docs/acceptance-tests.md`. Keep this file current, and keep it to rules and commands: a description belongs in the README, and the reason for one line of code belongs beside that line.
- The pack builder (`content_pack.collect_pack_files`), the seed copy, the installer, and the strip scan follow one set of path rules: a component starting with a `SCOPE_PREFIXES` name fails the build and the install, `_sources` and catalogs and the held draft are left out and reported, and a Canada-named path ships under its own name. Never drop a path without a message. `content_pack.SCOPE_PREFIXES` and `check_pack_strip._SCOPE_PREFIXES` change together.
- The bundled seed carries a numbered `pack.json` (`content_pack.seed_marker`), written into the seed only: never add a `pack.json` to the checkout's pack folders. Its number is the one line of `app/packaging/seed_content_version.txt` or `--seed-version`; the owner confirms it, and no code supplies one. The updater replaces only with a strictly newer numbered pack (`content_update._is_newer`).
- One pull request per phase where practical. No release tags from a pull request. Content releases are `content-v*` tags; app releases are `app-v*` tags. The app version is in `app/fpfa/__init__.py`, `app/packaging/installer.iss`, `app/frontend/package.json`, and `package-lock.json`; move them together and rebuild the page. A pack built from this tree asks for this app version or newer (`min_app_version`).
