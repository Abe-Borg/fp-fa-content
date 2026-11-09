# CLAUDE.md

Guidance for coding agents working in this repository. Read `docs/prototype-plan.md` first. It is the plan of record and it says what is in and out of v0.

## What this is

+Cynosure: a Windows desktop assistant for hyperscale data-center fire sprinkler and fire-alarm design. It was FP/FA Design Assistant until 2026-11-09; the package, the data directory, and the environment variables keep the `fpfa` name. `app/` is a tkinter program. Everything else is a content pack the app loads at runtime: `skills/`, `roles/`, `modes/`, `calcs/`, `corpus/`, `specs/`. Claude writes narrative and reads methods. Every number comes from `calcs/`. The README has the full description.

## Rules that do not bend

- Numbers come from the calc tools. The model never computes gallons, seconds, gpm, psi, scfm, or the releasing table.
- Three labels stay distinct: calculated, ASSUMED, use best judgment. A delivery time is an optimistic screen, not a listed water-delivery-time calculation.
- Scope is wet pipe, dry pipe, double-interlock preaction, the detection and releasing that trip them, and outdoor oil-filled transformer apparatus water spray. Foam, clean agent, water mist, building deluge, single-interlock, and non-interlock are refused. Canada only through a skill's Country gate; CAN/ULC and CEC Section 32 bodies stay NEEDS HOLD.
- NFPA 13-2025 is the delta baseline. An unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified. Cite the section and the edition together.
- No raw standards text, no vendor catalog numbers, no job, client, or personal names anywhere in the pack. Tests scan for them and fail the build.
- The double-interlock draft section is 21 13 19. Dry pipe is 21 13 16. Never cross them.
- The Messages client sends no `temperature`, `top_p`, `top_k`, or forced `tool_choice`, and never disables thinking. The system text goes out as one cached block. Do not add a second model vendor.
- The content pack is replaceable. Nothing in `app/` hardcodes a method, a role, or a mode. Loaders read them from disk.
- Agents never open the project record directly. A calc tool records itself; a model writes facts, findings, questions, and decisions through the record tools. A `ToolSession` without a record writes nothing, and tests rely on that.
- The window stays tkinter (plan of record). Its look is built inside tkinter and matches the practice's other apps; do not add a web view, a widget toolkit, or an image library for it.
- A widget never names a colour. It reads a token from `theme.colors`, uses a ttk style, or is registered with `Theme.paint`, so all five schemes recolour it. A new scheme defines every token in `theme.TOKENS`; a new token goes into every scheme.
- A streamed request is the request `create()` sends, byte for byte: same system block, same cache markers, same tools. Do not mark a tool for eager input streaming and do not add a field to one path only. Only the lead's reply is drawn in the thread; a specialist's and the checker's words never are.
- The working line names a tool or a file. It never shows a tool's inputs or its result.
- What the pointer can work, the keyboard can. A control that opens a `PopupMenu` is wired with `App._menu_button`, which binds the click and the keys together; a new clickable card or label takes the focus and answers Space and Enter. The keyboard's ring is the ttk state `theme.KEYBOARD_FOCUS`, set by `watch_keyboard_focus` on Tab and Shift+Tab only: an element with a hover picture has a ring picture, and no style draws a ring from ttk's own `focus` state, which a click sets too.
- The thread follows its end only while `ThreadView.follow` is true. Every way the reader moves the thread calls `user_moved` when the move happens (the press, not the release), and a widget placed inside the thread binds the wheel itself and does the same: its events never reach the Text.
- The license is PolyForm Shield 1.0.0. It is stated in `LICENSE`, `app/fpfa/about.py`, `app/packaging/installer.iss`, the Windows workflow's release notes, and the README; `app/tests/test_branding.py` keeps them in step. The installer's license page reads the root `LICENSE`, never a copy, and nothing may skip it or pre-select acceptance. A bundled package with no license text fails the build: supply `app/packaging/third_party_licenses/<name>-<version>.txt`, never silence the check.
- The inbox is in memory; the record is all that survives a relaunch. Window jobs are `jobs` rows there, and `Record.recover()` runs once at launch and only marks: in-flight jobs and agents become `interrupted`, delivered handoffs go back to `pending`. Nothing is re-run on its own. One window per data directory: `App` takes the OS file lock on `fpfa.lock` first and a second window is refused. `docs/recovery-protocol.md` is the Test C and D protocol.

## Layout

| Path | Role |
| --- | --- |
| `app/fpfa/` | Desktop app. `ui.py` window, `theme.py` colour schemes, fonts, and ttk styles, `shapes.py` the rounded pictures and the icon drawn in pure Python, `widgets.py` composer, list, drop-down menu, chips, `dialogs.py` themed dialogs under the stock modules' names, `thread_view.py` the thread (bubbles, paper blocks, working line, live reply), `reveal.py` how a reply's words arrive, `claude_client.py` tool loop and the streamed call, `calc_tools.py` tool schemas and the tool session, `record.py` project record (SQLite), `workflow.py` DI tool plan, `claim_check.py` blind checker, `spec_docx.py` Section 21 13 19 export, `design_basis_docx.py` Design Basis and Open Questions export, `team.py` lead, specialists, handoffs, and the record-fed checker, `team_panel.py` the Team tab, `jobs.py` inbox, `instance_lock.py` one window per data directory, `usage_report.py` tokens and cost from the record, `about.py` the name, the license facts, and versions, `content_update.py` pack updater |
| `app/packaging/` | `build_app.py` PyInstaller build that also writes LICENSE.txt and the notices into the folder, `installer.iss` Inno Setup script with the license page, `third_party_notices.py`, `make_icon.py` and `assets/Cynosure.ico` |
| `LICENSE` | PolyForm Shield License 1.0.0. Plain ASCII; the installer shows this file |
| `app/tests/` | App suite. Window tests need a display |
| `calcs/fp`, `calcs/fa` | Deterministic kernels and their tests |
| `skills/<slug>/SKILL.md`, `roles/<slug>/ROLE.md`, `modes/<slug>/MODE.md` | Content with `name` and `description` frontmatter |
| `specs/*.md` | Draft CSI sections, all sent to the model in full |
| `corpus/` | Paraphrased pins and notes, searched by `search_corpus` |
| `docs/` | Plan of record and known answers. Not part of the content pack |

## Working here

- Python 3.11 or newer; 3.12 is what the suites are run with. Install `app/requirements.txt`. On Linux add `python3-tk` and run window tests under `xvfb-run`.
- Tests, from the folders named: `calcs/fp`: `python -m unittest discover -s . -p 'test_*.py'`. `calcs/fa`: `python -m unittest discover -s tests`. `app`: `python -m unittest discover -s tests`. Run all three before a push and put the counts in the pull request body.
- Run the app from `app/` with `python -m fpfa`. `--demo --quit --screenshot-dir <dir>` runs the sample and writes two PNGs under a display. `--theme <id>` picks a colour scheme for one run.
- `FPFA_DATA_DIR` moves the data directory. `FPFA_CONTENT_UPDATES=0` skips the launch feed check. `FPFA_CONTENT_ROOT` pins the pack. `FPFA_THEME` picks a scheme and `FPFA_REDUCE_MOTION=1` turns the easing off for one run.
- `App(root)` draws every reply at once, which is what the tests rely on. `main()` passes `motion=True` unless Reduce motion is set. A test of the easing builds `App(root, motion=True)` and pumps frames.
- Look at the window after a change to it. Under a display, drive `App` through its states and capture PNGs; check a light scheme (`linen`) and a display scale above 100% (`xvfb-run -s "-screen 0 2200x1400x24 -dpi 144"`).
- A themed dialog waits for its window to close. A test that reaches one must patch it (`fpfa.ui.messagebox.askyesno`, `fpfa.ui.dialogs.showtext`, and so on) or the suite hangs.
- `ui.py` calls dialogs through the names `messagebox` and `simpledialog`, which are `fpfa/dialogs.py`. Keep those names: tests patch them.
- A ttk image element pads its children by its slice border unless `padding=0` is given, and a nine-slice picture needs a middle wider than zero between its two slices (`theme._side`). Both mistakes draw corners only.
- Tk sends a key to the widget that holds the focus, whatever widget `event_generate` names. A key test calls `focus_force()` first and skips when the display gives no focus. Tk moves the focus on Tab from the `all` bindings (`<<NextWindow>>`, `<<PrevWindow>>`); never bind `<Tab>` on `all`, which would hide them.
- A widget embedded in a Text has no height until it is on screen. Ask where the thread ends only after the window has been pumped (`root.update()` a few times), and test "the end is in view" with `dlineinfo("end-1c")`, not the scroll fraction alone.
- Model prices live only in `usage_report.py` as a dated snapshot (`RATES_PER_MILLION`, `RATES_DATE`). Change both together; never spread a price elsewhere.
- When behavior changes, update `README.md` in the same change. Do not shorten it to make room; add what is necessary. When dependencies change, update `app/requirements.txt`. When a phase, gate, or decision changes, update `docs/prototype-plan.md`. Keep this file current.
- One pull request per phase where practical. No release tags from a pull request. Content releases are `content-v*` tags; app releases are `app-v*` tags and need `app/fpfa/__init__.py` to carry the same version.
- The installer's AppId, the `fpfa` package name, the `FPFA_*` variables, the data directory name, and the keyring service name are not renamed. An existing install and its data depend on them.
- After a change to the star or its colours, run `python packaging/make_icon.py` from `app/` and commit `packaging/assets/Cynosure.ico`.
- The model id is `claude-opus-5-5`. A chat turn streams (`AnthropicMessages.streaming`); everything else calls `create()`. Prompt caching is on the system block and, with tools present, on the message tail. Keep the system text byte-identical across rounds; put anything that varies per turn in the user message.
- The target machine is Windows. Keyring goes through Credential Manager there; other desktops use a user-only file. Do not break the frozen-app path in `keystore.py`.

## Content pack rules

- A skill, role, or mode is one folder with one markdown file and frontmatter. The pack build (`scripts/build_content_pack.py`) strips paths named foam, clean-agent, canada, catalog, and `_sources`, and refuses any file that holds an API key.
- Keep section numbers, edition years, and numeric screens. Paraphrase; do not quote a standard at length.
- Do not add a code threshold to `calcs/fa/lib/lfl.py`. Percents are inputs.
