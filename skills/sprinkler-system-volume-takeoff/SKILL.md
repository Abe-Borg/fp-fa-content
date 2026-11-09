---
name: Sprinkler system volume takeoff
description: >-
 use this when a dry or double-interlock (DI) preaction zone needs its trapped
 water volume (gal) from a pipe segment list (takeoff or hydraulic-software pipe
 report) — gal per segment, per zone, largest single zone, and connected total
 per riser room / N₂ generator, with NFPA 13 volume-gate flags; feeds
 dry-preaction-water-delivery-screen and nitrogen-inerting-and-c-factor-gate.
 Wet / dry / DI only (wet = informational volume only). NOT delivery-time proof,
 QOD election, N₂ generator selection, C-factor, hydraulics.
---

# Sprinkler system volume takeoff

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. Turns a per-zone pipe segment list into gallons. It **does not** prove delivery time (that is `dry-preaction-water-delivery-screen`) and **does not** pick a generator or compressor (that is `nitrogen-inerting-and-c-factor-gate`). It hands those Skills the two numbers they ask for.

**Design practice:** cite section AND edition; delta vs NFPA 13-2025; show-and-verify math; judgment calls tagged `Verify with the engineer of record` with a conservative default; never invent a length or an ID — `ASSUMED` or `[SYN]` with a flag.

## 1. Scope gate

| System type | Action |
|---|---|
| Dry pipe | In scope — full run + flags |
| Double-interlock preaction (N₂ generator + compressor) | In scope — full run + DI flags |
| Wet | Volume reported **informational only** (no NFPA 13 volume gate); useful for wet+N₂ fill sizing hand-off |
| Single-/non-interlock preaction, deluge, foam, clean agent, mist, water spray | **Out of scope — Stop** (`RFI-variance` if presented as BOD) |

C = 100 is not touched here (hydraulics are not this Skill's).

## 2. Inputs

| Input | Required | Notes |
|---|---|---|
| Zone ID + system type (dry / DI) + riser room + N₂ generator served | yes | Missing → `ASSUMED`, flagged |
| Segment list per zone: nominal size (in.), schedule / pipe type, length (ft) | yes | From a takeoff or the hydraulic software pipe report. Include feed main, cross main, branch, drops/sprigs, riser above the valve clapper. |
| Pipe ID source (manufacturer data sheet per schedule/type) | no | **Governs when given.** Else Table 3 default (§3). |
| Fittings / riser allowance | no | §4.1 — `Verify with the engineer of record` |
| Valve trim volume (gal) above the clapper / seat | no | Manufacturer data sheet. §4.2 |
| Occupancy hazard (for the calculated-delivery table only, passed through) | no | Not used for gallons |

**Shop default (the engineer of record):** mains, cross mains and any pipe **2 in. and larger = Sch 10, grooved fittings**; **branch lines = Sch 40** (threaded). Sizes 1–12 in. If the pipe type column is blank, apply this default and tag `ASSUMED (shop default)`. A 2 in. branch line → Sch 40 under the default (branch rule governs); flag it.

## 3. Method and default ID table

```
gal/ft = 0.0408 × ID² (ID in inches)
segment_gal = L_ft × gal/ft
```

**Constant verify:** volume of 1 ft = (π/4)·ID²·12 in³; 231 in³ = 1 gal → (π/4)(12)/231 = 9.42478/231 = **0.040800** gal/(ft·in²). ✓

**Table 3 — DEFAULT gal/ft (manufacturer ID governs).** IDs = OD − 2×wall per ASME B36.10M dimensions as also used by ASTM A795 / A135 Sch 10 / Sch 40. Cross-check column = NFPA 13-2025 Table A.8.2.4 (held, corpus A1) = NFPA 13-2022 Table A.8.2.3 (held §2; every cell identical, 3/4 in. Sch 10 blank in both).

| NPS (in.) | Sch 10 ID | Sch 10 gal/ft | 13-2025 A.8.2.4 Sch 10 | Sch 40 ID | Sch 40 gal/ft | 13-2025 A.8.2.4 Sch 40 |
|---|---|---|---|---|---|---|
| 1 ¹ | 1.097 | 0.0491 | 0.049 | 1.049 | 0.0449 | 0.045 |
| 1¼ ¹ | 1.442 | 0.0848 | 0.085 | 1.380 | 0.0777 | 0.078 |
| 1½ ¹ | 1.682 | 0.1154 | 0.115 | 1.610 | 0.1058 | 0.106 |
| 2 | 2.157 | 0.1898 | 0.190 | 2.067 | 0.1743 | 0.174 |
| 2½ | 2.635 | 0.2833 | 0.283 | 2.469 | 0.2487 | 0.248 |
| 3 | 3.260 | 0.4336 | 0.433 | 3.068 | 0.3840 | 0.383 |
| 3½ | 3.760 | 0.5768 | 0.576 | 3.548 | 0.5136 | 0.513 |
| 4 | 4.260 | 0.7404 | 0.740 | 4.026 | 0.6613 | 0.660 |
| 5 | 5.295 | 1.1439 | 1.144 | 5.047 | 1.0393 | 1.040 |
| 6 (0.134 wall) | 6.357 | 1.6488 | 1.649 | 6.065 | 1.5008 | 1.501 |
| 8 (Sch 10 0.188 wall) **sourced** ² | 8.249 | 2.7763 | 2.776 | 7.981 | 2.5988 | 2.66 is **Sch 30** — not comparable |
| 10 Sch 10 **sourced** ² / Sch 40 `[SYN]` | 10.374 (0.188 wall) | 4.3909 | not in held table | 10.020 `[SYN]` | 4.0963 `[SYN]` | not in held table |
| 12 `[SYN]` | 12.390 (0.180 wall) | 6.2633 | not in held table | 11.938 | 5.8146 | not in held table |

² Sch 10 8 in. and 10 in. inside diameters are from a manufacturer submittal (8 in. ID 8.249 at 0.188 in. wall; 10 in. ID 10.374 at 0.188 in. wall). The pipe supplier's data sheet governs.

¹ Sch 10 below 2 in. does not apply under the shop default (branches are Sch 40); rows kept for flexibility (e.g., listed thin-wall or a different owner standard).

Notes:
- 1–8 in. rows agree with NFPA 13-2025 Table A.8.2.4 to ≤0.001 gal/ft — the formula reproduces the annex table.
- **10 in. Sch 10 is now sourced (Wheatland, note ²). 12 in. (both schedules) and 10 in. Sch 40 rows remain `[SYN]`** (neither 2022 A.8.2.3 nor 2025 A.8.2.4 goes above 8 in. — confirmed): wall values from ASME B36.10M recalled, not opened in a held source; ASTM A795 Sch 10 walls for 8–12 in. differ from B36.10 Sch 10 (note the NFPA 8 in. Sch 10 = 0.188 wall vs B36.10 0.148). **Use the manufacturer data-sheet ID**; if none, the B36.10 Sch 10 wall is thinner → larger ID → larger gallons, which is the conservative side for volume gates.
- **Manufacturer ID governs** (thin-wall, Sch 10 "light-wall", Sch 7, dynaflow/eddythread etc. differ). Record the data sheet + rev on the output.
- CPVC, copper, other types → manufacturer ID only; no default row → `ASSUMED` with flag.

### 3.1 `calcs` op — `pipe_volume` (2026-10-23; do not edit `calcs`)
- Run **one step per zone**; IDs come from Table 3 or the data sheet (the op holds **no ID table** — it takes `d_in` as the actual ID). So the op does **not** clear the 12 in. `[SYN]` rows.
- Constant: op uses π/4·ID²/144·7.48 = 0.0407999 gal/(ft·in²) ≡ 0.0408 here (diff < 0.001 %).
- Op output is pipe-only (`volume_gal`, `volume_ft3`, `segments_detail`); add fittings % and trim (§4) by hand on the zone summary. Save the JSON + stdout **with the project**, not in `calcs/runs/`.
```
python3 calcs/fp/run.py zone-volumes.calc.json
{"job":"<project> dry/DI zone volumes","steps":[
 {"id":"zoneA_pipe","op":"pipe_volume","segments":[{"d_in":1.049,"length_ft":1400},{"d_in":4.26,"length_ft":260}]},
 {"id":"zoneA_fill","op":"air_fill_scfm","v_gal":543.58,"p_psig":40,"t_min":30}]}
```
- Optional `air_fill_scfm` step on the zone total is a **pass-through to** `nitrogen-inerting-and-c-factor-gate` (that Skill owns the compressor pick).

## 4. Allowances (optional; each `Verify with the engineer of record`)

### 4.1 Fittings / riser allowance
- **Default 0 %** when lengths are measured **center-to-center through fittings** (hydraulic software pipe reports and model takeoffs do this) — fitting bodies are then already in the length. Grooved fittings add no net volume per the corpus worked takeoff (USFA CB-2006-52 example). Equivalent length (friction) **is not volume** — never add fitting equivalent lengths to the gallons.
- **Default +5 %** of pipe gallons when the takeoff is **pipe-cut lengths only** (fittings excluded) or the source is unknown. `Verify with the engineer of record` — conservative engineering allowance, not a code value.
- Riser / feed main / drops: take actual lengths; never an allowance if lengths exist. Missing riser length → `ASSUMED` = floor-to-deck height + 10 ft, flagged.

### 4.2 Valve trim volume
- Use the valve maker's data sheet (gal above clapper/seat incl. trim to the alarm/air side as the sheet states). Record model + sheet rev.
- No sheet → `ASSUMED` **5 gal** per valve, `Verify with the engineer of record` (conservative placeholder; replace with the data-sheet value).

## 5. Outputs

### 5.1 Per-segment table (one per zone)

| Zone | Seg ID | Role (main / cross / branch / riser / drop) | NPS | Sch / type | ID (in.) | ID source | gal/ft | L (ft) | gal |
|---|---|---|---|---|---|---|---|---|---|

### 5.2 Per-zone summary

| Zone | Type (dry/DI) | Riser room | N₂ gen | Pipe gal | Fittings allow. (%, gal) | Trim gal | **Zone total gal** | Flags |
|---|---|---|---|---|---|---|---|---|

Zone total = Σ segment gal × (1 + fittings %) + trim gal.

### 5.3 Aggregation
- **Largest single zone (gal)** — per riser room, per N₂ generator, and campus-wide.
- **Connected Σ gallons** — per riser room and per N₂ generator (all dry/DI zones it serves).

### 5.4 Threshold flags (code floor; mirrors `dry-preaction-water-delivery-screen` Parameter B)

| Type | Zone total | Flag |
|---|---|---|
| Dry | ≤ 500 gal | `VOL≤500` — no QOD, no specific delivery requirement [CODE NFPA 13-2025 §8.2.4.2.1; 13-2022 §8.2.3.3] |
| Dry | 500 < V ≤ 750 | `VOL-QOD` — exemption only **with** a QOD [CODE 13-2025 §8.2.4.2.2; 13-2022 §8.2.3.4] |
| Dry | > 750 | `VOL>750` — must meet 60 s ITC, listed calc (Table 8.2.4.3.2), manifold, or listed alternative time [13-2025 §8.2.4.2, §8.2.4.3, §8.2.4.4, §8.2.4.5; 13-2022 §8.2.3.2, §8.2.3.5–.6, §8.2.3.7] |
| DI | ≤ 500 gal | `DI≤500` [CODE 13-2025 / 13-2022 §8.3.2.3.1.1] |
| DI | > 500 | `DI>500` — **no 750 gal DI path**; 60 s simultaneous, calc, or table time [13-2025 / 13-2022 §8.3.2.3.1.2–.1.4; QOD permitted §8.3.2.3.2] |
| Any dry/DI | any | `FM-30s` reminder when FM DS 5-32 controls — volume exemptions do **not** waive the 30 s gate (owned by the delivery screen) |
| Any dry/DI | any | `PLANS` — total system volume must be on working plans [CODE NFPA 13-2025 §28.1.3(24)(b); 13-2022 §28.1.3(23)(b)] |

Flags are screens; the delivery screen owns the verdict.

### 5.5 Hand-offs (exact field names)
- `HAND OFF — dry-preaction-water-delivery-screen: Largest system volume (gal) = <largest single zone gal> (zone <ID>, <dry|DI>), flags <…>.`
- `HAND OFF — nitrogen-inerting-and-c-factor-gate: largest-system volume (gal) = <…> and connected Σ gallons = <…> per N₂ generator / riser room (two-number check).`

## 6. Code basis and delta

| Item | NFPA 13-2025 (delta) | NFPA 13-2022 (2024 I-Codes floor) | Held |
|---|---|---|---|
| Dry capacity 60 s / 500 gal / 750 gal + QOD | §8.2.4, §8.2.4.2, §8.2.4.2.1, §8.2.4.2.2 | §8.2.3.1–§8.2.3.4 | Yes —, |
| Dry calculated delivery | §8.2.4.3, Table 8.2.4.3.2 | §8.2.3.5–.6, Table 8.2.3.6.1 | Yes (same values) |
| Dry manifold test connection; listed alternative times | §8.2.4.4 (.4.1–.4.3, Table 8.2.4.3.2 times; 4-head = 2+2 on two remote branch lines, 2-head = 2 on remote branch); §8.2.4.5 listed alternative times | §8.2.3.7 | 2025 held — §1 (A.8.2.4.4 annex not pulled) |
| DI size (500 gal / 60 s / calc / table) | §8.3.2.3.1.1–.1.4, §8.3.2.3.2 | same numbers; cross-refs 8.2.3.6 → 8.2.4.3 | Yes — |
| gal/ft table | Table A.8.2.4 | Table A.8.2.3 (A.8.2.3.1: 60 s limit n/a ≤500 gal, or ≤750 gal with QOD) | Both held — the 2025 annex table; 2022 §2. Values identical 3/4–8 in.; table stops at 8 in. |
| Volume on working plans | §28.1.3(24)(b) | §28.1.3(23)(b) — same text, item renumbered | Both held — §3 |

**Delta 2022 → 2025:** dry size clause renumbered §8.2.3 → §8.2.4 and reframed as "Dry Pipe System Water Delivery" with 500/750 gal moved under the single-orifice §8.2.4.2; gallons and times unchanged. DI §8.3.2.3 unchanged except cross-refs. **Note:** in 2025, §8.2.3 is not the dry capacity clause — cite §8.2.4.

## 7. Worked example — `[SYN]` synthetic data, not a project

Riser room RR-1, one N₂ generator G-1. Zone A dry; Zone B DI. Lengths center-to-center from a pipe report → fittings 0 %. Trim per (synthetic) data sheet 1.5 gal each.

| Zone | Seg | NPS / Sch | gal/ft | L | gal |
|---|---|---|---|---|---|
| A | branch | 1 / 40 | 0.0449 | 1,400 | 62.86 |
| A | branch | 1¼ / 40 | 0.0777 | 320 | 24.86 |
| A | branch | 1½ / 40 | 0.1058 | 160 | 16.93 |
| A | cross | 2 / 10 | 0.1898 | 240 | 45.55 |
| A | cross | 2½ / 10 | 0.2833 | 180 | 50.99 |
| A | main | 4 / 10 | 0.7404 | 260 | 192.50 |
| A | main/riser | 6 / 10 | 1.6488 | 90 | 148.39 |
| **A pipe** | | | | | **542.08** |
| B | branch | 1 / 40 | 0.0449 | 900 | 40.41 |
| B | branch | 1¼ / 40 | 0.0777 | 200 | 15.54 |
| B | cross | 2 / 10 | 0.1898 | 160 | 30.37 |
| B | main | 4 / 10 | 0.7404 | 180 | 133.27 |
| B | main/riser | 6 / 10 | 1.6488 | 60 | 98.93 |
| **B pipe** | | | | | **318.52** |

Verify (spot): 0.0408 × 4.260² = 0.0408 × 18.1476 = 0.7404; 260 × 0.7404 = 192.50 ✓. 1,400 × 0.0449 = 62.86 ✓. Σ A = 62.86+24.86+16.93+45.55+50.99+192.50+148.39 = 542.08 ✓.

- Zone A total = 542.08 + 0 + 1.5 = **543.58 gal** (dry) → `VOL-QOD` (needs QOD for the code exemption; else 60 s / calc).
- Zone B total = 318.52 + 0 + 1.5 = **320.02 gal** (DI) → `DI≤500`.
- Largest single zone = **543.58 gal (A)**; connected Σ at G-1 = 543.58 + 320.02 = **863.60 gal**.
- If Zone A were DI instead: 543.58 > 500 → `DI>500` (no 750 path). Cutting ~44 gal (e.g., 60 ft of 6 in. Sch 10 = 98.93 gal) is the zoning lever — delivery screen decides.

Hand-off lines: `dry-preaction-water-delivery-screen: Largest system volume (gal) = 543.58 (Zone A, dry), VOL-QOD`. `nitrogen-inerting-and-c-factor-gate: largest-system volume = 543.58 gal; connected Σ = 863.60 gal at G-1`.

## 8. Status register (every run)
Each zone: `grounded` (all IDs from data sheet or held table, lengths from report) / `provisional` (`ASSUMED` default schedule, allowance, trim, or `[SYN]` 12 in. / 10 in. Sch 40 rows) / `unresolved`.

## 9. Stops
Out-of-scope system type as BOD; segment list absent for every zone (no gallons invented from ft²).

## Verify with the engineer of record
1. Fittings allowance 0 % / +5 % defaults. 2. Trim placeholder 5 gal. 3. Missing riser length = height + 10 ft. 4. 12 in. IDs (and 10 in. Sch 40) `[SYN]` until a manufacturer sheet or ASTM A795 table is held. 5. 2 in. branch line → Sch 40 under the shop default. 6. Corpus core (2026-10-23) cites "13-2025 §8.2.3.3" for the 500 gal dry exemption — wrong clause for 2025 (held: §8.2.4.2.1; 2022 = §8.2.3.3). Use this Skill's §6 cites, not the package's.
