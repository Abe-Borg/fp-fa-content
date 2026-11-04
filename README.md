# FP/FA Design Assistant

Desktop prototype for hyperscale data-center fire protection and fire alarm designers. The scope is wet pipe, dry pipe, and double-interlock preaction sprinklers, plus the detection and releasing that trip them, and outdoor oil-filled transformer apparatus water spray (NFPA 15-style) in `skills/power-block-transformer-water-spray/SKILL.md`. Foam, clean agent, water mist, a building deluge system, and single-interlock preaction are out of scope. Canada ships only through a Country gate (US | Canada) on the skill. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Apparatus water spray is not water mist and it is not a building deluge system.

The app reads methods from `skills/`, calculations from `calcs/`, and optional draft language from `specs/`. It does not hardcode those methods. Point it at another folder with the same layout (`FPFA_CONTENT_ROOT`, or Settings). Settings can also check the release feed and install a newer pack. `corpus/` holds edition pins and decision notes. The everyday path searches them with `search_corpus`.

## Why this stack

Python, because the calc kernel that already exists is Python and the other design apps in this practice are Python. The window is the standard-library `tkinter` toolkit, so the prototype has no backend server and no browser. Numbers are computed in `calcs/` and exposed to Claude as tools.

The model is Claude Opus 5.5, model id `claude-opus-5-5`, called with the Anthropic Messages API and each user's own API key. That id is the one published on the Claude platform models page for Claude Opus 5.5. The client does not send `temperature`, `top_p`, or `top_k`. It does not disable adaptive thinking, and it does not force `tool_choice` (this model rejects a forced tool).

The everyday path is how a typed question is answered. It loads the shell from `roles/everyday/ROLE.md` and lists the other specialist roles in `roles/<slug>/ROLE.md`, including the QA specialist. The model reads a specialist with `read_role` and a method with `read_skill` (`skills/<slug>/SKILL.md`). The Mode menu points at `modes/<slug>/MODE.md` the same way: brainstorm, calculator, synthesis, and mixed. The active mode file is the behavior for that reply. The model reads another mode with `read_mode`. Those files stay in the content pack. Calc tools still run in `calcs/` through the same tool loop. `fa_calc` runs `calcs/fa/lib`. `search_corpus` searches `corpus/`. The fixed tool plan in `app/fpfa/workflow.py` still fills the tables and the docx when a narrative disagrees. This path does not add another model vendor, and it does not send the skills to a hosted container runtime.

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

`pywin32` lets the `keyring` package store the API key in Windows Credential Manager. If Credential Manager is unavailable, the app stores the key in a user-only file under `%APPDATA%\fpfa-assistant`. Settings and the status line say which store holds the key. The key is not written into the project file, the chat log, or the exported document.

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

On Linux or macOS, use `python3` in place of `py`. PyInstaller builds for the OS it is running on, so a Windows `.exe` comes from a Windows run (`app\dist\fpfa\fpfa.exe`, or `packaging\build_app.ps1`). A Linux run writes `app/dist/fpfa/fpfa`. The folder includes a seed content pack, and the packaged app checks the release feed on launch. Smoke that Linux binary with `FPFA_CONTENT_UPDATES=0 ./dist/fpfa/fpfa --demo --quit` from `app/`. That runs the seed pack and the sample tool plan. It does not produce `fpfa.exe`. `python3 packaging/build_app.py --seed-only` writes the seed folder and stops before PyInstaller. On Windows, `packaging\build_app.ps1` then `packaging\build_installer.ps1` writes `app\dist\fpfa-setup-<version>.exe` (Inno Setup 6). Upload that setup exe to a GitHub Release. Windows Credential Manager still has to be confirmed on a Windows machine where `pywin32` is installed.

## Conversation-first window

The chat thread is the main pane. You can type a question without filling in the zone form. The form sits in a smaller panel under the thread for pipe segments and basis when you want them. It is not required to start.

- **Sample DI** (the chip under the composer, or `/sample-di`) creates the sample data-hall double-interlock job and runs the existing zone tool plan. That path does not need an API key. The narrative is posted back into the thread, including the ASSUMED trim line and the ASSUMED screen limit. The same figures stay on the results panel for export.
- **Sample BESS** (the chip under the composer, or `/sample-bess`) creates a generic Li-ion BESS room and runs the explosion-control starter in synthesis mode. That path does not need an API key. The method stays in `skills/ess-isolation-venting-and-duration/SKILL.md`. Mixture LFL and setpoints come from the LFL tool. An election or a duration the tool did not return is labeled ASSUMED. The sample room has no sprinkler zone, so the draft does not invent gallons or seconds. If that project already has a zone tool plan, the starter quotes it and those gallons and seconds govern when the narrative disagrees. Export of Section 21 13 19 still needs a zone run.
- `/run` runs whatever is on the optional zone form.
- `/new Job name` opens a job. `/help` lists the composer commands.
- **Settings** and **Export 21 13 19** stay as buttons. Export still needs a finished zone run. Before the file is written, the app runs the blind claim check from `skills/blind-claim-check/SKILL.md`. The QA checker is `roles/qa-specialist/ROLE.md`. That turn receives only the claim list and the short cites. It does not receive the draft, the spec section, or the designer's notes. Claims come from the narrative the export writes, including a figure with no section and a sentence that names a section a tool already named. A tool string may be shown as a package assertion. It is not a passage from the standard, and copying it back as the cite does not support the claim. Export waits until every such claim is Supported. That result does not mean the narrative was compared to the standard. Engineer-of-record review still applies. A cite marked `NOT PULLED` stays open. The check is a `claim` job on the inbox, labeled `Job <id> | <project> | claim | <title>`, and the result is posted into the same project thread. It does not open a hosted container. The draft section stays 21 13 19.
- A normal message, with a key saved, uses the everyday path and includes the earlier turns in that project. The window does not wait on the call. The reply is written into the thread when it arrives. The path can read a specialist role, a mode, and a skill, and it can call the calc tools. The Mode menu (or `/mode`) chooses brainstorm, calculator, synthesis, or mixed. If a tool plan has already run, the request repeats those governing figures. The chat reply does not replace the tables or the export. Ask Claude after the tool plan is the checkbox on `/sample-di`, `/sample-bess`, and `/run`. Numbers in the tables and the export stay on the tool plan either way.
- The inbox beside the project list is the queue of zone runs, chat turns, an explosion-control starter that calls Claude, a blind claim check, and a heavy job. Two workers run the long jobs. The composer stays usable while a job runs, including a second message and a switch to another project. A result that finishes later is labeled with its job id, project name, and kind, and it is written onto the project that started it. A local tool plan with no model call still finishes before `/sample-di`, `/sample-bess`, or `/run` returns, and it is recorded on the same inbox.
- `/heavy task` sends that task through the hosted runtime and posts the reply into the same thread. The turn is text-only reasoning on the zone packet already in the message. It does not call `read_role`, `read_skill`, `read_mode`, or a calc tool, and it does not recompute zone gallons or seconds. It does not open another project. A typed question, `/sample-di`, `/sample-bess`, and `/run` stay on the path they already had.
- Projects are listed beside the thread. New and Delete manage those files. Ctrl+S saves the open job, and closing the window saves it too. A first `/run`, `/help`, or chat message keeps whatever is already on the optional form. The sample zone is generic. It is not a constructed building.

Blank trim (5 gal) and the screen-limit seconds are labeled ASSUMED on the optional form, in the thread after a run, in the results panel, and in the export. Pipe gallons and trip time are calculated. A value the designer types is not assumed. A designer judgment the tools did not return is labeled use best judgment. That label is not ASSUMED and it is not a calculated figure. A delivery time from these tools is an optimistic screen. It is not a listed water-delivery-time calculation.

Check key in Settings calls the models endpoint for `claude-opus-5-5` and does not generate text.

## Tests

```bat
cd calcs\fp
py -m unittest test_formulas test_di_zone

cd ..\fa
py -m unittest discover -s tests

cd ..\..\app
py -m unittest discover -s tests
```

`calcs/fp/test_formulas.py` is the seed kernel suite (79 tests in this tree). `calcs/fa` is the fire-alarm library suite. Quote-only tests that needed raw code text are skipped, because that text is not in the repo. The app tests run the sample zone, the Word export, the blind claim check before that export, the Claude tool loop against a fake response, the key-file fallback, the `/sample-di` starter, the `/sample-bess` explosion-control starter, the inbox queue (workers, composer stays usable, out-of-order results stay on their job), and the `/heavy` hosted hatch (one cloud session, text-only prompt, reply back in the same thread, a failed session delete is visible, close and process exit delete an in-flight session, ordinary paths do not call it). Content-pack tests serve a local manifest and zip. Those tests do not need a display.

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
| `specs/` | Draft CSI sections, one file each. README is not a spec. Double-interlock draft language is 21 13 19 |
| `corpus/` | Paraphrased reference notes (edition pins and decision logs). `search_corpus` searches this folder |

## Not in this prototype

`packaging/build_app.py` builds a distributable folder, and on Windows that folder contains an `.exe` with a seed content pack. `packaging/build_installer.ps1` wraps that folder as `fpfa-setup-<version>.exe` for a GitHub Release. Settings can install a newer pack from the release feed. Publishing a pack from chat is not wired; a `content-v` tag runs the release workflow. Windows Credential Manager still has to be confirmed on a Windows machine. No second model vendor. No foam, clean agent, mist, building-deluge, or single-interlock design path (those inputs return an RFI and stop). Outdoor oil-filled transformer apparatus water spray stays on the desktop path through `power-block-transformer-water-spray`. Wet and dry can be named on the form; the finished vertical workflow is the double-interlock zone. The inbox queues long jobs on workers and labels a result with the job it belongs to. The blind claim check is a `claim` job on the Messages path. `/heavy` is the only hosted container path, and it is text-only on the zone packet already computed on this machine.
