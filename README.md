# FP/FA Design Assistant

Desktop prototype for hyperscale data-center fire protection and fire alarm designers. The scope is wet pipe, dry pipe, and double-interlock preaction sprinklers, plus the detection and releasing that trip them. Foam, clean agent, water mist, deluge, and single-interlock preaction are out of scope.

The app reads methods from `skills/`, calculations from `calcs/`, and optional draft language from `specs/`. It does not hardcode those methods. Point it at another folder with the same layout (`FPFA_CONTENT_ROOT`, or Settings) when a content pack is downloaded later. `corpus/` is reserved for reference notes the next pass can search.

## Why this stack

Python, because the calc kernel that already exists is Python and the other design apps in this practice are Python. The window is the standard-library `tkinter` toolkit, so the prototype has no backend server and no browser. Numbers are computed in `calcs/` and exposed to Claude as tools.

The model is Claude Opus 5.5, model id `claude-opus-5-5`, called with the Anthropic Messages API and each user's own API key. That id is the one published on the Claude platform models page for Claude Opus 5.5. The client does not send `temperature`, `top_p`, or `top_k`. It does not disable adaptive thinking, and it does not force `tool_choice` (this model rejects a forced tool). Skills are local `SKILL.md` files the model reads through a `read_skill` tool. The Claude Agent SDK was not used: these skills are files in the content pack, not Anthropic-hosted container skills, and that SDK expects a Claude Code runtime.

Deterministic math is never left to the model. The double-interlock screen runs a fixed tool plan on the form. Claude may call the same tools and write the narrative. If that narrative does not quote the tool-plan volume and delivery time, the draft keeps the tool-plan figures. A delivery time from these tools is an optimistic screen. It is not a listed water-delivery-time calculation.

## Run from source (Windows)

Install Python 3.11 or newer (3.12 is what this prototype was exercised with), then:

```bat
cd app
py -m pip install -r requirements.txt
py -m pip install pywin32
py -m fpfa
```

`pywin32` lets the `keyring` package store the API key in Windows Credential Manager. If Credential Manager is unavailable, the app stores the key in a user-only file under `%APPDATA%\fpfa-assistant` and says so in Settings. The key is not written into the project file, the chat log, or the exported document.

On Linux or macOS the same commands work with `python3` in place of `py`. The key is stored in a user-only file under `~/.local/share/fpfa-assistant` (or `$XDG_DATA_HOME`), mode `0600` where the filesystem allows it. Set `FPFA_USE_KEYRING=1` before starting the app to use the system keyring instead. A missing keyring on those desktops can open a blocking password dialog, so the file is the default there.

Projects are JSON files in that data directory. Override it with `FPFA_DATA_DIR` if you want them somewhere else.

## What you can do in this prototype

1. Settings. Paste an Anthropic API key. Check key calls the models endpoint for `claude-opus-5-5` and does not generate text.
2. Projects. Create a job, or load the sample data-hall zone. Record the AHJ, NFPA 13 and NFPA 72 editions, the insurer, and hazard notes.
3. DI zone. Enter pipe segments (nominal size, schedule, length, role). Blank schedule uses the shop default and is flagged. Run the zone.
4. Results. Trapped volume, pipe-only and zone-total delivery screens, trim family, releasing truth table, nitrogen C-factor, density and hose. Export a draft Section 21 13 16 `.docx`.
5. Chat. With a key saved, the same tools and skills are available. Without a key, the zone tool plan still runs.

The sample zone is generic. It is not a constructed building.

## Tests

```bat
cd calcs\fp
py -m unittest test_formulas test_di_zone

cd ..\fa
py -m unittest discover -s tests

cd ..\..\app
py -m unittest discover -s tests
```

`calcs/fp/test_formulas.py` is the seed kernel suite (79 tests in this tree). `calcs/fa` is the fire-alarm library suite. Quote-only tests that needed raw code text are skipped, because that text is not in the repo. The app tests run the sample zone, the Word export, the Claude tool loop against a fake response, and the key-file fallback.

## Layout

| Path | Role |
| --- | --- |
| `app/` | Desktop application |
| `skills/<slug>/SKILL.md` | Design methods the model must read |
| `calcs/fp` | Fire-protection formulas, shop pipe IDs, DI zone screens |
| `calcs/fa` | Fire-alarm calculation libraries |
| `specs/` | Optional master-spec markdown (README is not treated as a spec) |
| `corpus/` | Reserved for later reference notes |

## Not in this prototype

No installer. No second model vendor. No foam, clean agent, mist, deluge, or single-interlock design path (those inputs return an RFI and stop). Wet and dry can be named on the form; the finished vertical workflow is the double-interlock zone.
