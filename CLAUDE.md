# CLAUDE.md

Guidance for coding agents working in this repository. Read `docs/prototype-plan.md` first. It is the plan of record and it says what is in and out of v0.

## What this is

A Windows desktop assistant for hyperscale data-center fire sprinkler and fire-alarm design. `app/` is a tkinter program. Everything else is a content pack the app loads at runtime: `skills/`, `roles/`, `modes/`, `calcs/`, `corpus/`, `specs/`. Claude writes narrative and reads methods. Every number comes from `calcs/`. The README has the full description.

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
- The inbox is in memory; the record is all that survives a relaunch. Window jobs are `jobs` rows there, and `Record.recover()` runs once at launch and only marks: in-flight jobs and agents become `interrupted`, delivered handoffs go back to `pending`. Nothing is re-run on its own. One window per data directory: `App` takes the OS file lock on `fpfa.lock` first and a second window is refused. `docs/recovery-protocol.md` is the Test C and D protocol.

## Layout

| Path | Role |
| --- | --- |
| `app/fpfa/` | Desktop app. `ui.py` window, `claude_client.py` tool loop, `calc_tools.py` tool schemas and the tool session, `record.py` project record (SQLite), `workflow.py` DI tool plan, `claim_check.py` blind checker, `spec_docx.py` Section 21 13 19 export, `design_basis_docx.py` Design Basis and Open Questions export, `team.py` lead, specialists, handoffs, and the record-fed checker, `team_panel.py` the Team tab, `jobs.py` inbox, `instance_lock.py` one window per data directory, `usage_report.py` tokens and cost from the record, `about.py` versions, `content_update.py` pack updater |
| `app/tests/` | App suite. Window tests need a display |
| `calcs/fp`, `calcs/fa` | Deterministic kernels and their tests |
| `skills/<slug>/SKILL.md`, `roles/<slug>/ROLE.md`, `modes/<slug>/MODE.md` | Content with `name` and `description` frontmatter |
| `specs/*.md` | Draft CSI sections, all sent to the model in full |
| `corpus/` | Paraphrased pins and notes, searched by `search_corpus` |
| `docs/` | Plan of record and known answers. Not part of the content pack |

## Working here

- Python 3.11 or newer; 3.12 is what the suites are run with. Install `app/requirements.txt`. On Linux add `python3-tk` and run window tests under `xvfb-run`.
- Tests, from the folders named: `calcs/fp`: `python -m unittest discover -s . -p 'test_*.py'`. `calcs/fa`: `python -m unittest discover -s tests`. `app`: `python -m unittest discover -s tests`. Run all three before a push and put the counts in the pull request body.
- Run the app from `app/` with `python -m fpfa`. `--demo --quit --screenshot-dir <dir>` runs the sample and writes two PNGs under a display.
- `FPFA_DATA_DIR` moves the data directory. `FPFA_CONTENT_UPDATES=0` skips the launch feed check. `FPFA_CONTENT_ROOT` pins the pack.
- Model prices live only in `usage_report.py` as a dated snapshot (`RATES_PER_MILLION`, `RATES_DATE`). Change both together; never spread a price elsewhere.
- When behavior changes, update `README.md` in the same change. Do not shorten it to make room; add what is necessary. When dependencies change, update `app/requirements.txt`. When a phase, gate, or decision changes, update `docs/prototype-plan.md`. Keep this file current.
- One pull request per phase where practical. No release tags from a pull request. Content releases are `content-v*` tags; app releases are `app-v*` tags and need `app/fpfa/__init__.py` to carry the same version.
- The model id is `claude-opus-5-5`. Prompt caching is on the system block and, with tools present, on the message tail. Keep the system text byte-identical across rounds; put anything that varies per turn in the user message.
- The target machine is Windows. Keyring goes through Credential Manager there; other desktops use a user-only file. Do not break the frozen-app path in `keystore.py`.

## Content pack rules

- A skill, role, or mode is one folder with one markdown file and frontmatter. The pack build (`scripts/build_content_pack.py`) strips paths named foam, clean-agent, canada, catalog, and `_sources`, and refuses any file that holds an API key.
- Keep section numbers, edition years, and numeric screens. Paraphrase; do not quote a standard at length.
- Do not add a code threshold to `calcs/fa/lib/lfl.py`. Percents are inputs.
