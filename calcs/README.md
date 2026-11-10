# calcs

Deterministic fire-protection and fire-alarm math. The desktop app loads `calcs/fp/di_zone.py` from the content pack and calls it as Claude tools. Do not reimplement these formulas in the model prompt.

## `calcs/fp`

| File | Role |
| --- | --- |
| `formulas.py` | Kernel: pipe volume, delivery screen, density/area, hose duration, nitrogen fill, and the other ops behind `dispatch` |
| `run.py` | Small CLI over `dispatch` |
| `pipe_ids.py` | Shop inside diameters and the blank-schedule rule |
| `di_zone.py` | Zone gallons (fittings and trim), trim-family screen, releasing truth table (second leg is `p_second_leg`, the pressure drop from sprinkler operation; `low_air` is a deprecated alias and low air is supervisory only), nitrogen C = 100 |
| `test_formulas.py` | Kernel tests. Run from this folder: `python -m unittest test_formulas` |
| `test_di_zone.py` | Zone-screen tests, including the second-leg label tests (`p_second_leg`, deprecated `low_air` alias) |
| `test_pack_local.py` | Finite-number guard and fill-basis label tests |
| `test_pack_content_lowair.py` | Scans `corpus/` and `specs/` for wording that makes low air a release input; release is detection and P |

### Where the kernel files come from

`formulas.py`, `run.py` and `test_formulas.py` are the kernel source files (md5 prefixes `2b33548e`, `68d93bd9` and `e590c54c`), stripped of comments and docstrings that carry internal tags, with a few generic label edits, plus 3 pack-local behaviours that the kernel source does not have yet:

1. **Finite-number guard.** `_as_float` rejects `inf` and `nan`, so an overflowing input such as `1e309` cannot become an infinite fill flow.
2. **Two-basis fill label.** `fill_bases_text` states the gauge-basis and the absolute-basis air-fill rates side by side. It does not elect one.
3. **`fill_bases` result key.** `air_fill_scfm` and `compressor_n2_sizing` return that label next to their numbers, and the air-fill docstring says the label does not pick a basis.

The kernel source has 215 tests, and they pass on the pack copy of `test_formulas.py`. `test_pack_local.py` adds 3 more for the 3 pack-local behaviours.

### Reproduce the kernel files

One command stages the three files from a kernel source folder and byte-compares them with `calcs/fp/`. Run it from the repository root, with the folder that holds the kernel's `formulas.py`, `run.py` and `test_formulas.py`:

```bash
python3 scripts/check_fp_kernel_reproduce.py --kernel-dir <kernel-dir>
```

It exits 0 when all three files are identical. It exits 1 with a short diff summary when one differs, and 2 when the kernel folder cannot be staged. `scripts/fp_kernel_stage.py` holds the staging rules and can write the staged files to a folder with `--out`. `calcs/fp/test_kernel_reproduce.py` runs the same check, and is skipped unless `FP_KERNEL_DIR` is set to the kernel folder.

`di_zone.py` loads `formulas.py` and `pipe_ids.py` from its own directory, so a content pack can replace `calcs/fp` without installing a package.

The delivery-time functions are an optimistic screen (trip time plus volume over fill flow). They are not a listed water-delivery-time calculation. On double-interlock the 500 gallon size threshold is not raised by a quick-opening device. Above it, a 60 second test-connection option or a listed calculation is the path; the screen does not pick one. `di_trip_to_water` takes an optional `v_basis` (pipe-only, v_allow, or caller) that labels which volume the threshold test used; omitting it changes no existing key or value. The cite note follows the volume: at or under 500 gallons it is a no-delivery-test threshold; above 500 gallons one of the alternative paths has to be elected.

## `calcs/fa`

`lib/` holds the fire-alarm modules (15 in this pack: airflow, audibility, battery, voltage drop, intelligibility, ASD, Class N, separation, and the rest). A curation note described 16 libraries; the non-backup set that was moved is these 15. `lib/lfl.py` computes a mixture LFL and a setpoint at a caller-supplied percent. `setpoints_for` does not choose a code threshold and does not return an election or a duration. `trigger_paths` still applies the two NFPA 855 percents already in that file. Do not add an NFPA 69 threshold there. Tests live in `tests/` and run with:

```bash
python -m unittest discover -s tests
```

Run that from `calcs/fa`. Tests that only asserted raw code text are skipped. The math tests remain. Charger fixture keys in the battery module stay, because the tests lock those keys; the catalog quotations were removed.

Fixture and test names in this tree are generic. Hand checks are named for the quantity they lock (density, supply, pump, relief valve, high altitude), not for a job, a client, or a city. Both suites include a name scan that fails if one of those names is introduced:

```bash
# from calcs/fp
python -m unittest discover -s . -p 'test_*.py'
# from calcs/fa
python -m unittest discover -s tests
```

Do not add job names, client names, personal names, raw NFPA text, or vendor catalogs under this tree.
