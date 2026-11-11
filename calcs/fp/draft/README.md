# calcs/fp/draft: held, not wired

`el_pn_release.py` is a draft of the El/Pn solenoid and valve-release function. It is **HELD**. Do not import it, and do not wire it into `formulas.py`, `run.py`, `di_zone.py`, the tool plan, or the app. It waits for a separate go-ahead.

- It has two outputs: `solenoid = (D OR manual_in_D) AND NOT isolated`, and `valve_release = solenoid AND PA-REL`. The low-air supervisory input is never in either Boolean.
- It is separate from the El/El table in `di_zone.py`, which stays as it is.
- `calcs/fp/test_draft_held.py` fails if anything under `calcs/` or `app/` references the draft, and it runs `test_el_pn_release.py` in its own process.
- This folder is not a Python package, so `python -m unittest discover -s . -p 'test_*.py'` from `calcs/fp` does not import the draft.
- The app builds its calc identity from `calcs/fp/*.py` only, so a file in this folder does not change it.
- The files here are staged from the kernel source folder by `scripts/fp_kernel_stage.py`. Do not hand-edit them.
