---
name: Combustion air and hall free area
description: >-
  use this when a genset room needs combustion-air or radiator-air openings, or
  a data hall return/containment needs raised-floor panel free-area (OA%) for
  ASD return or makeup, after occupancy is pinned — against company wet|dry|DI
  only (consume STS; this Skill does not elect family); packet optional;
  STS + occupancy-hazard-fork (+ matrix opening/OA%/genset-air when dual)
  consumed when present, else ASSUMED and flagged — never a stop; SI/NI-as-BOD → Stop RFI-variance (comparison-only);
  foam prohibited; mist PRACTICE REFUSED; status register every run — not pump
  nameplate, not ASD pipe sizing, not louver CAD, not invent OEM Q, not
  clean-agent BOD.
---
# Combustion air and hall free area

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **Two branches, one Skill:** (1) **genset-room combustion / radiator air openings**; (2) **raised-floor panel free area (OA%)** for hall return or makeup. Occupancy is already pinned. This Skill does **not** freeze a pump nameplate (`pump-envelope`). It does **not** size ASD pipe (`asd-vewfd-return-sampling` **consumes** OA% / CFM). It does **not** CAD louvers. It does **not** elect the suppression family — it **consumes** STS `wet` | `dry` | `DI` and records free-area / opening consequences.

**Core thesis:** Free area is **OA% × panel area × count**, not a louver guess. Genset combustion air is **OEM scfm**, not a 1 in²/kW folklore number unless the cited mechanical code actually says that **and** is open. **DS 5-20 is electrical testing** (including ATS *tests*) — not this Skill. **DS 5-23** is facility emergency/standby **generators**. Pump-room ventilation lives in **DS 3-7** — hand off, do not rewrite `pump-envelope`. Separate `Q_comb` / `Q_rad` when OEM or UFC C-4 F says so. Declare **face vs free-area** `v` before `n_panels`.

**Design practice:** three-layer most-stringent per parameter (OA% or opening area, velocity basis, OEM air rate, interlock). **Δ vs NFPA 13-2025 = N/A** to this apparatus — also flag **IMC / NFPA 37 / NFPA 110** as `[V]` if unlicensed. Cite section AND edition. Show-and-verify. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet + STS `wet`|`dry`|`DI` + `occupancy-hazard-fork` (+ `most-stringent-basis-matrix` **opening / OA% / genset-air** rows when dual-carrier — **consume and return here**). Caller-path-only. **NO PLACEHOLDER.** Clean agent = **hand-away only** (company does not design). Generic. Do not invent section numbers. Owner may **raise, never lower**.

Write **only** to the path the **caller** names. Write output only to the caller-named path.

Look up shop codebook notes **by title** (not a required filesystem path): *Standby / prime generator plant and diesel fuel system*; *Data-hall airflow field and the 5 ft/s threshold*; *Fire-pump selection & installation*; *Design practice*; *Enforced-vs-latest edition resolver and reference pins*; *ASD/VEWFD return-sampling sizing for hyperscale fan-wall halls*.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (free-area-adapted — consumes STS, does not elect)

This Skill owns **genset combustion/radiator free-area openings + hall raised-floor panel OA% / panel count**. Controlling company BOD = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI | `suppression-technology-selection` (**consume** — do not elect here) |
| Size genset `A_free` / hall `n_panels` + OA% | **This Skill** |
| Dual-carrier per-parameter union (opening / OA% / genset-air rows) | `most-stringent-basis-matrix` (**consume**, then **return here**) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- Synthetic SI hall spines that touch OA%/CFM (method only)

**This Skill does not elect families.** It **consumes** the STS token `wet` | `dry` | `DI`, the completed the input packet, occupancy-hazard-fork, and — when carrier = `dual` — matrix **opening / OA% / genset-air** rows. Then it sizes free area / openings and emits the verification.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue free-area arithmetic as if SI/NI were company-elected BOD.
6. SI/NI (including synthetic SI hall spines that mention OA%/CFM) may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream via STS | Record free-area / opening consequences under that BOD |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record and refuse; do **not** design/accept mist as BOD |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent ; do not invent clean-agent free area as company BOD |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Clean agent = hand-away only — never company BOD here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Branch A: OEM `Q_comb` / `Q_rad` → `A_free` / louver gross | System-family election (`suppression-technology-selection`) |
| Branch B: OA% × panel area × count → `n_panels` / `A_return` | Occupancy re-class (`occupancy-hazard-fork`) |
| Face vs free-area `v` honesty; UFC C-4 F separate streams | ASD pipe / ports / transport (`asd-vewfd-return-sampling` **consumes** OA%/CFM) |
| DS 5-23 manufacturer + interlock; Tate datasheet pins | Pump nameplate / DS 3-7 pump-room recipe (`pump-envelope`) |
| Status register + reciprocal handshakes | Dual-carrier BOD authorship (matrix — consume+return) |
| Consume packet + STS + matrix(when dual) + occupancy | Louver CAD; invent OEM Q; clean-agent relief vents as company BOD |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet / STS / matrix(when dual) / occupancy, **(c)** branch, **(d)** OEM `Q` / hall `Q`, **(e)** OA% / panel / SP / `v` basis, **(f)** interlock, **(g)** Δ vs 13-2025 / IMC/37/110, and **(h)** mist/foam if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling openings + editions + arithmetic supported by OEM sheet / opened datasheet / caller Q already closed |
| `provisional` | Directionally pinned; IMC/37/110 / SP / `v` hole flagged `[V]` — **never silent `grounded` on invented Q or unread GrateAire rows** |
| `unresolved` | STS / matrix(when dual) / occupancy / OEM Q / hall Q / OA% / `v` basis not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, synthetic SI hall OA%/CFM spines, UFC commercially advisory, sheet mist wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; ASD VEWFD; pump-envelope; ITM / DS 5-20; clean-agent hand-away) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as controlling medium — record and refuse |

**Invented OEM scfm / silent 0.10 SP / brochure 2100 as datasheet / 740 rumor → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

A held draft = **read-only method source** for elevation (face vs free-area; `Q_rad`; UFC C-4; fuller Tate tables) — **not** a live copy and **not** a license to invent fabricated tokens. **NO PLACEHOLDER.** Airflow-field note’s web **740 cfm @ 0.10** → replace with datasheet **700** when PERF-1250 ECN 16500 is used. Tile free-area `v` ≠ FM DS 5-32 5 ft/s compliance plane. No dedicated genset-combustion / Tate-OA% EXERCISE spine — refuse inventing hall/genset defaults. Worked examples (e.g. 4200 scfm / 500 fpm; 20,000 cfm panel counts) = **example only**, never job defaults.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent OEM scfm, OA%, or `v`. Do not treat SI/NI as company BOD.

| Input | Required | Notes / Stop |
|---|---|---|
| **Completed the input packet** | **yes** | Packet is **optional** (component token `combustion-air`). Consume; do not rebuild; do not retrieve prior job files. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Occupancy-hazard-fork schedule** | **yes** | Already pinned. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not re-classify. |
| **Consumed `most-stringent-basis-matrix` opening / OA% / genset-air rows** | **yes** when dual-carrier (or when those rows exist) | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever as if matrix replaces this Skill. Unresolved controlling opening/OA%/genset-air row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **Branch** | **yes** | `genset` / `hall-panel` / `both` |
| **Genset: OEM `Q_comb` (+ `Q_rad` if radiator-in-room)** | **yes** if genset | Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not invent 1 in²/kW. Altitude / inlet T if OEM derates. |
| **Hall: required return/makeup CFM or ASD sampling-plane CFM** | **yes** if hall | Consume from mechanical / ASD path; do not re-size ports. |
| **Panel type / OA%** | **yes** if hall | `PERF-1250 25%` / `GrateAire 56%` / `HD GrateAire 56%` / other named OEM with OA% in hand |
| **`v` basis (face vs free-area)** | **yes** if using `A_free = Q/v` | Mixing without saying so → **Stop**. |
| **Underfloor ΔP** | **yes** if using CFM tables | in. w.c. If unknown, elect a design SP and flag `[V]` — do **not** pick 0.10 in. silently as a fact. |
| **Carrier / AHJ** | **yes** | For genset: IMC/NFPA 37/110 edition pins or `[V]`. `dual` → matrix rows above. |
| **Caller output path** | **yes** | If unnamed, return the screen in the response and stop. |

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token** | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `occupancy-hazard-fork` | Occupancy / space class — consumed when present (else `ASSUMED`, flagged) | Re-classify occupancy here |
| `most-stringent-basis-matrix` | **Opening / OA% / genset-air** rows when dual-carrier | Rebuild dual-carrier BOD; Stop-away forever; invent opening numbers |
| `asd-vewfd-return-sampling` | Hands OA%/CFM **to** ASD (ASD does **not** currently name this Skill by id) | Size ASD ports / transport here |
| `pump-envelope` | Pump-room diesel air / DS 3-7 | Import 0.75 in²/hp onto facility genset |
| `itm-design-for-testability` | DS 5-20 / ATS ITM confusion | Treat DS 5-20 as opening sizing |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS `wet`|`dry`|`DI`, occupancy, or dual-carrier opening/OA%/genset-air rows (when required) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Outbound this restamp only.** Do **not** restamp peers. Note: `asd-vewfd-return-sampling` consumes OA%/CFM conceptually but **does not currently name this Skill by id** inbound.

| Peer | They own | This Skill owns |
|---|---|---|
| `pump-envelope` | Pump listed envelope; DS 3-7 §§2.4.17–2.4.25 pump-room air; `calcs/fp` `louver` identity | Facility genset openings (OEM + DS 5-23); refuse DS 3-7 import onto genset |
| `asd-vewfd-return-sampling` | ASD ports / chamber / transport / SOO | Supply OA% / CFM@SP / `n_panels` / `A_return` — do not size ports here |
| `itm-design-for-testability` | Lifecycle ITM; DS 5-20 / ATS tests | Hand DS 5-20 confusion here → ITM; DS 5-20 ≠ openings |
| the input packet | Assignment context (component `combustion-air`) | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `occupancy-hazard-fork` | Occupancy / HC/OH pin | Consume only; do not re-classify |
| `most-stringent-basis-matrix` | Per-parameter union / opening·OA%·genset-air rows | **Consume only** when dual — then size **here** |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume only**; mist = `PRACTICE REFUSED`; foam prohibited |
| `density-area-dry-increase` / `hydrant-supply-curve` | Density×area / hydrant curve | **Not-this** — preserve |
| Clean-agent enclosure-integrity (peer) | Clean-agent relief-vent free area | **Hand-away only** — company does not design clean agent |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: opening/OA%/genset-air rows when dual. Consume; return here after.`
- `HAND OFF — the input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — occupancy-hazard-fork: occupancy pin. Consume only.`
- `HAND OFF — asd-vewfd-return-sampling: consume OA%/CFM from here (peer does not yet name this Skill inbound).`
- `HAND OFF — pump-envelope: DS 3-7 pump-room air / nameplate. Not facility genset.`
- `HAND OFF — itm-design-for-testability: DS 5-20 / ATS ITM. Not openings.`
- `HAND OFF — density-area-dry-increase / hydrant-supply-curve: Not this Skill.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before edition pins or branch arithmetic:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only.
2. Check upstream (packet optional): packet if present (optional); STS present; occupancy present; matrix opening/OA%/genset-air rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix·occupancy / branch / OEM·hall Q / OA%·panel·SP·`v` / interlock / Δ 13·IMC/37/110 (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER.** anywhere in the run.

### 3.1 Pin editions / OEM sheets

| Instrument | Role | Shop pin |
|---|---|---|
| Tate **PERF 1250** 24 in HPL | Perforated panel | **25% OA** without damper. ECN **16500 12/17/25**. 700 CFM @ 0.10 in. w.o. damper; 490 damper-open; 60 damper-closed |
| Tate **GrateAire** 24 in | Grate (non-HD) | **56% OA** without damper. ECN **16549 Rev 7/2026**. OCR-clean w/o-damper rows only (below); do **not** invent unread 0.06–0.10 |
| Tate **HD GrateAire** 24 in | Grate | **56% OA** without damper. ECN **16502 10/30/25**. 2340 CFM @ 0.10 in. w.o. damper |
| Tate directional PERF 1250 | Older | **32% OA** (2013 drawing) — do not mix with 25% HPL |
| **FM DS 5-23** | Emergency/standby **facility** generators | **Jul 2020 / IR Jan 2022**. **§2.4.1** ventilation **and** combustion air; **§2.4.1.1 manufacturer**; **§2.4.1.2** louver/fan **interlock**; §2.4.2 40 °F / 70 °F water; §2.6.1 ITM → DS 5-20. §3.5 is fire scenarios, **not** an airflow table. |
| **FM DS 3-7** | **Diesel fire-pump** room air (not this genset branch) | **Apr 2012 / IR Apr 2025**. Fence: §2.4.22.2 **0.75 in²/hp** intake; discharge **1.5×** radiator outlet; intake **2×**; no thermostat, opposite walls; −3%/1000 ft above 300 ft. **Do not import onto a standby genset.** Hand pump-room air to `pump-envelope`. |
| **FM DS 5-20** | Electrical *testing* (ATS tests for 2-81) | **Oct 2016 / IR Oct 2025** (held PDF via ITM peer; `` unmined). **Not** opening sizing |
| **UFC 3-540-01 App. C-4** | Combustion air **separate from cooling** (DoD-mandatory; commercially advisory) | Change **4, 16 Jan 2026**. C-4 opening line: evaluate for **NFPA 30, 37, and 110**. Comparison for commercial jobs |
| **IMC / NFPA 37 / NFPA 110** | Genset air openings | IMC / NFPA 110 **`[V]`** if unlicensed; NFPA 37 [CODE NFPA 37-2021/2024 §4.1.1.2: air supply for combustion, cooling and ventilation, no opening sizes, pull 37-02] — do not invent 1 in²/kW |

**Δ vs NFPA 13-2025:** **N/A** to this apparatus. **Δ vs IMC / 37 / 110:** `[V]` until licensed.

### 3.2 Three-layer union per parameter (not a whole-layer MAX)

| Parameter | Code floor | Insurer | Owner | Controlling typical |
|---|---|---|---|---|
| **Combustion Q** | NFPA 37 [CODE NFPA 37-2021/2024 §4.1.1.2: air supply for combustion, cooling and ventilation, no opening sizes, pull 37-02]; NFPA 110 / IMC **`[V]`** — do not invent | **DS 5-23 §2.4.1 / §2.4.1.1:** ventilation **and** air for combustion; **design to manufacturer** | may add winter-min / summer-max room T | **OEM `Q_comb`** |
| **Cooling / radiator Q** | UFC 3-540-01 App. **C-4 F**: combustion air **separate from cooling** (commercially advisory) | DS 5-23 does not publish a radiator multiple. **DS 3-7** multiples = **pump rooms only** | may force separate combustion stack / radiator plenum | **OEM `Q_rad`**, separate opening when required |
| **Interlock** | `[V]` | **DS 5-23 §2.4.1.2:** interlock louvers/fans with **generator**. Pump DS 3-7: interlock with **engine**; **no thermostat**; opposite walls | may add fire/smoke damper overlay (other Skill) | Interlock **on**; no thermostat control of the combustion path |
| **Hall OA% / panel count** | none in 13 | DS 5-32 return-opening disclosure is the ASD Skill; this Skill produces `A_free` / `n_panels` / OA% | may mandate grate vs 25% perf | Named panel table |
| **Velocity basis** | none in 13 | 5 ft/s / 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13, pull 75-07; owner/insurer FM DS 5-32 only] is a **detection gate**, not a tile-orifice limit | may cap face velocity | Caller-named `v`; declare free-area vs face |

If notes conflict, **most-stringent wins** and both sources stay visible. Do not average OEM scfm with an invented IMC table.

### 3.3 Branch A — genset

1. Take **OEM** `Q_comb` and, if radiator-cooled in room, **OEM** `Q_rad` (separate stream per UFC C-4 F / OEM). Sum only if the OEM says they are simultaneous / share the same openings. Missing either when required → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged.
2. Opening area from OEM or from the cited mechanical code — **do not invent**.
3. Show-and-verify:

```
A_free_ft2 = Q_scfm / (v_fpm) # v from OEM or cited code, not invented
A_gross = A_free / (FA%/100) # only if louver FA% is named
```

If `v` unpinned → stated `ASSUMED` velocity basis (value + why), `[V]`, flagged; area is ASSUMED-based. Optional `calcs/fp` `louver` identity check does **not** invent Q.
4. Louvers: use **manufacturer free-area %**, not nominal wall opening. Insect screens cut free area — apply the listed factor or `[V]`.
5. Interlock per **DS 5-23 §2.4.1.2**. Combustion-air path is **not** the pump-room ventilation path (DS 3-7). Separate rooms, separate Skills.
6. Altitude: apply **OEM** derate if the OEM sheet says so. Do **not** apply DS 3-7 §2.4.18 (−3%/1000 ft) to a facility genset.

**Pump-room fence (print, do not execute as genset rules):**

| DS 3-7 Apr-2012 / IR Apr-2025 | Number | Use |
|---|---|---|
| §2.4.22.2 | Heat-exchanger-cooled openings **≥ 0.75 in²/hp (6.5 cm²/kW)** | Pump house **only** |
| §2.4.22.3 / §2.4.25.2.3 | Radiator **discharge** louvers **≥ 1.5 ×** radiator outlet | Pump house |
| §2.4.22.4 | Interlock; **no thermostat**; opposite walls | Same idea as DS 5-23 §2.4.1.2; pump-specific |
| §2.4.25.2.2 | Radiator **intake** louvers **≥ 2 ×** radiator outlet | Pump house |

### 3.4 Branch B — hall panels

Panel area 24×24 in = **4.00 ft²** gross.

**Velocity honesty first:** if `v` is **free-area** (through perforations), `A_free = Q/v` is perforation area and `n_panels = A_free / (OA_frac × A_panel)` is correct. If `v` is **face** velocity on the 24 in module, `A_needed = Q / v_face` is **gross** panel area and `n_panels = A_needed / A_panel` — **do not also divide by OA%**. Mixing face + free-area without saying so → **Stop**.

```
A_open_one = OA% × 4.00 ft2
# PERF-1250: 0.25 × 4.00 = 1.00 ft2
# GrateAire / HD: 0.56 × 4.00 = 2.24 ft2
n_panels = Q_cfm / CFM_one(SP) # catalogue check at stated SP — not a silent substitute for mechanical Q
```

Use the **OEM CFM vs SP table** at the **stated** underfloor SP, with damper **open** vs **none** called out.

**Tate PERF-1250 25% HPL** (ECN 16500 12/17/25) — opened, no damper:

| SP in. w.c. | CFM | damper open | damper closed |
|---|---|---|---|
| 0.02 | 370 | 260 | 10 |
| 0.04 | 440 | 300 | 20 |
| 0.05 | 480 | 340 | 40 |
| 0.06 | 515 | 350 | 50 |
| 0.08 | 575 | 375 | 55 |
| 0.10 | **700** | 490 | 60 |

**Tate GrateAire 24 in** (ECN 16549 Rev 7/2026) — OCR-clean w/o-damper rows only:

| SP in. w.c. | w/o damper | slide open | OBD open |
|---|---|---|---|
| 0.02 | **1050** | 610 | 880 |
| 0.04 | **1505** | 685 | 1275 |
| 0.05 | **1700** | 750 | 1400 |

Do **not** invent 0.06 / 0.08 / 0.10 for non-HD GrateAire. Brochure **2100 CFM @ 0.10** = **marketing** — use HD table when that panel is specified.

**Tate HD GrateAire 24 in** (ECN 16502 10/30/25) — opened, no damper:

| SP in. w.c. | w/o damper | OBD open | OBD closed |
|---|---|---|---|
| 0.02 | 1055 | 890 | 90 |
| 0.04 | 1500 | 1290 | 100 |
| 0.05 | 1685 | 1450 | 120 |
| 0.06 | 1875 | 1565 | 145 |
| 0.08 | 2115 | 1760 | 155 |
| 0.10 | **2340** | 2075 | 170 |

Identity check: PERF-1250 `0.25 × 4.00 ft² = 1.00 ft²` at 700 cfm ⇒ **700 fpm** through free area (codebook **740** cfm rumor is **not** on this sheet). HD GrateAire `0.56 × 4.00 = 2.24 ft²` at 2340 cfm ⇒ **~1045 fpm**. Do not treat 56% as verified from a brochure photo — HD GrateAire datasheet **states 56% OA**.

If Q is `[SYN]`, `n_panels` is `[SYN]`. ASD Skill **consumes** `n_panels` / CFM; this Skill does not place sampling ports. Do not mix 25% PERF with 56% grate in one count without saying so.

### 3.5 Hand-offs

- `HAND OFF — asd-vewfd-return-sampling` with panel OA% + CFM@SP / `n_panels` / `A_return`.
- `HAND OFF — pump-envelope` / DS 3-7 if the room is a **pump** room, not a genset room.
- `HAND OFF — itm-design-for-testability` if ATS testing (DS 5-20 / 2-81) was confused with this opening calc.
- Clean-agent relief free area → hand-away only (company does not design).

---

## Output

Hard-scope / company-fence / status register; Branch A and/or B: OEM air rates or Q_cfm; OA% + sheet date; SP; `v` basis (face vs free-area); `n_panels` or `A_free`; show-and-verify (reproduce PERF 700/1.00 and HD 2340/2.24 identities when those panels are used); interlock callout; `[V]` on IMC/37/110 and on DS 5-23 § if unopened; Δ vs 13-2025 = N/A; reciprocal `HAND OFF` rows.

Do not emit: occupancy reclass, density×area, pump nameplate, ASD hole schedule, louver CAD, DS 3-7 opening schedule on a facility genset, combustion CFM minted from kW, clean-agent BOD, mist/foam BOD, or rebuilt packet/matrix/STS.

---

## Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away only.
2. Missing packet, STS `wet`|`dry`|`DI`, occupancy, or dual-carrier matrix opening/OA%/genset-air rows (when required) → `unresolved`. Dual + missing matrix → complete matrix, then **return here** (do not Stop-away forever).
3. Genset branch without OEM `Q_comb` (or without `Q_rad` when radiator-in-room and combined opening requested). Inventing 1 in²/kW or inventing OEM Q.
4. Importing DS 3-7 0.75 in²/hp / 1.5× / 2× onto a facility genset. Treating DS 5-20 as opening sizing.
5. Mixing face + free-area `v` without saying so. Mixing 25% PERF with 56% grate in one count without saying so. Printing `n_panels` without SP when using catalogue CFM. Using brochure 2100 or unread GrateAire rows as datasheet fact. Silent 0.10 SP as fact.
6. Sizing ASD pipes/ports. Freezing a pump nameplate. Louver CAD.
7. Caller asks to write outside the caller-named path.

---

## Citations (section AND edition)

- Tate PERF 1250 ECN **16500 12/17/25**: **25% OA**, CFM table (**700 @ 0.10** undamped).
- Tate GrateAire ECN **16549 Rev 7/2026**: **56% OA**, OCR-clean low-SP rows; brochure 2100 = marketing.
- Tate HD GrateAire ECN **16502 10/30/25**: **56% OA**, CFM table (**2340 @ 0.10** undamped).
- Tate directional PERF **32% OA** — do not mix with 25% HPL.
- FM DS **5-23 Jul 2020 / IR Jan 2022** §2.4.1 / §2.4.1.1 / §2.4.1.2 / §2.4.2 / §2.6.1→5-20 / §3.5 ≠ airflow.
- FM DS **3-7 Apr 2012 / IR Apr 2025** (pump room fence — hand-off); §§2.4.22 / 2.4.25.
- FM DS **5-20 Oct 2016 / IR Oct 2025** = testing, not this Skill (held PDF; `` unmined).
- UFC **3-540-01 Change 4, 16 Jan 2026** App. **C-4 F** — combustion separate from cooling; commercially advisory.
- IMC / NFPA 110 — `[V]` if unlicensed; NFPA 37 [CODE NFPA 37-2021/2024 §4.1.1.2: air supply for combustion, cooling and ventilation, no opening sizes, pull 37-02] (§4.4 is hazardous-materials engines, not combustion air). Δ vs NFPA 13-2025 = **N/A**.

---

## Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent = hand-away only. Status every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist). Upstream (packet optional; gaps → `ASSUMED`): packet + STS + occupancy (+ matrix opening/OA%/genset-air when dual — consume+return). **NO PLACEHOLDER.**
2. Three-layer, most stringent, PER PARAMETER. OEM scfm beats folklore. Datasheet **700** beats codebook **740**. DS 5-23 manufacturer rule beats copying pump-room 0.75 in²/hp onto a genset. Owner may separate combustion vs radiator and may raise OA%.
3. **Δ vs NFPA 13-2025 = N/A.** Also print **Δ vs IMC/37/110 `[V]`**. Cite section AND edition.
4. Show-and-verify: `A_free = Q/v`; declare face vs free-area; separate `Q_comb`/`Q_rad`; reproduce PERF 700 fpm / HD ~1045 fpm identities.
5. Reciprocal handshakes with correct peer folder IDs; do not restamp peers. Caller-path-only. Refuse invent Q / silent SP / mix panels / unread GrateAire / clean-agent as company BOD.

---

## Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH | `occupancy-hazard-fork` — **consume only** |
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume only**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier per-parameter authorship (opening/OA%/genset-air) | `most-stringent-basis-matrix` — **consume**, then return here |
| Assignment packet authorship | the input packet — **consume only** |
| Pump envelope / combustion air of **diesel fire pump** | `pump-envelope` + DS 3-7 |
| ASD ports / transport time | `asd-vewfd-return-sampling` (this Skill **supplies OA%**; peer does not yet name this Skill inbound) |
| ATS ITM / electrical testing | `itm-design-for-testability` (DS 5-20 / 2-81) |
| Density × area / hydrant curve | `density-area-dry-increase` / `hydrant-supply-curve` — **Not-this** |
| Clean-agent relief-vent free area | Hand-away only — company does **not** design clean agent |
| Louver CAD / damper shop drawings | **Stop** |
| Writing outside the caller-named path | forbidden |

---
