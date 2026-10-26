# calcs

Deterministic fire-protection and fire-alarm math. The desktop app loads `calcs/fp/di_zone.py` from the content pack and calls it as Claude tools. Do not reimplement these formulas in the model prompt.

## `calcs/fp`

| File | Role |
| --- | --- |
| `formulas.py` | Kernel: pipe volume, delivery screen, density/area, hose duration, nitrogen fill, and the other ops behind `dispatch` |
| `run.py` | Small CLI over `dispatch` |
| `pipe_ids.py` | Shop inside diameters and the blank-schedule rule |
| `di_zone.py` | Zone gallons (fittings and trim), trim-family screen, releasing truth table, nitrogen C = 100 |
| `test_formulas.py` | Kernel tests. Run from this folder: `python -m unittest test_formulas` |
| `test_di_zone.py` | Zone-screen tests |

The kernel file in this tree has 79 tests. A curation note described the earlier suite as 71; the file that was moved is the 79-test module, and those tests are the ones that must stay green.

`di_zone.py` loads `formulas.py` and `pipe_ids.py` from its own directory, so a content pack can replace `calcs/fp` without installing a package.

The delivery-time functions are an optimistic screen (trip time plus volume over fill flow). They are not a listed water-delivery-time calculation. On double-interlock the NFPA size cap is 500 gallons, and a quick-opening device does not raise it.

## `calcs/fa`

`lib/` holds the fire-alarm modules (15 in this pack: airflow, audibility, battery, voltage drop, intelligibility, ASD, Class N, separation, and the rest). A curation note described 16 libraries; the non-backup set that was moved is these 15. Tests live in `tests/` and run with:

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
