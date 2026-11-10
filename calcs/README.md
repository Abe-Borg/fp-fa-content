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

The kernel file in this tree has 215 tests. `test_pack_local.py` adds 3 more for the finite-number guard and the two-basis fill labels, which this pack keeps on top of the kernel.

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
