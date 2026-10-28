---
name: Density area dry increase
description: >-
 use this when elected wet/dry/double-interlock, HC/OH (or a pinned carrier
 density), and completed most-stringent-basis-matrix + occupancy-hazard-fork
 results (plus fire-area-compartmentation-schedule on multi-hall jobs) ideally
 exist — if absent, assume and flag ASSUMED (never a stop) — and you must
 produce density×area demand (q_spr + hose + duration
 gallons), including the FM dry-area 2,500→3,500 (≈+40%) vs NFPA 13-2025
 +30% fork (NFPA 13-2025 §19.2.3.2.6) — not for occupancy classification, system-family
 election, SI/NI election, hydrant curve, pump envelope, or node-by-node
 hydraulics.
---
# Density area dry increase

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe.

**This Skill owns** the **density×area demand calculation**: pin density and design area under a three-layer most-stringent union (separately), apply the FM dry/DI absolute-area fork (2,500 → 3,500 ≈ +40%) versus the NFPA 13 +30% delta [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5], add hose and duration, and produce `q_spr` / `qd` / gallons through the shop `calcs` kernel.

It does **not** own occupancy classification, system-family election, fire-area rating design, hydrant supply curves, pump envelopes, or node-by-node hydraulic trees.

**Core thesis:** on an FM HC-2 white-space hall the controlling density-method demand is usually **0.2 gpm/ft²** over **2,500 ft² wet** or **3,500 ft² dry/DI**, plus **250 gpm** hose and **60 min** duration — **750 gpm / 45,000 gal** wet, **950 gpm / 57,000 gal** dry/DI. FM fixes absolute areas; NFPA 13 applies a relative dry/DI +30% on a different base. Always print the delta. Never stack FM 3,500 with NFPA +30%.

**Design practice:** three-layer basis (code floor × insurer × owner) → **most-stringent union PER PARAMETER** (density separate from area). Report **Δ vs NFPA 13-2025**. Cite **section AND edition**. Show-and-verify math. Mark invented values `[SYN]` / unpinned `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Consume upstream Skills; do not rebuild them. Generic — do not copy a prototype hall onto another job.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (elect / size only)

This Skill may produce a **controlling** density×area demand only for an elected company system family:

1. **Wet-pipe sprinkler**
2. **Dry-pipe sprinkler**
3. **Double-interlock preaction**

Comparison-only (never elected; never the controlling BOD path):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

FM DS 5-32 January 2026 §2.4.1.1 preference ranking remains **comparison evidence**:

> Wet → non-interlock → single-interlock → double-interlock last

That ranking is **not** company election permission. AXA XL’s single-interlock preference and double-interlock penalty remain comparison evidence only.

If the caller requires single-interlock, non-interlock, or another prohibited preaction type as the **basis of design**:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling `qd` sized as if SI/NI were company-elected.

SI/NI may appear in a **comparison / delta** column only (e.g., “if SI were allowed, FM DS 5-32 would size wet 2,500”). Comparison rows are never the controlling demand.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Size density×area |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; do not elect or control `qd` |
| Foam / foam-water | **Prohibited** | Stop; do not design |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent | Handoff-only | Not this Skill |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |

**Foam is prohibited for company scope.** **Mist is `PRACTICE REFUSED`.** FM flowchart branches that mention mist do not authorize design here.

### 1.3 What this Skill calculates

| In scope | Out of scope |
|---|---|
| Density pin + design-area pin under 3-layer union | Occupancy / HC / OH classification |
| FM absolute wet 2,500 / dry-DI 3,500 fork | System-family election |
| NFPA 13-2025 dry/DI +30% **delta** column [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5] | Fire-area / FRR schedule |
| Hose + duration → `qd` + gallons via `calcs` | Hydrant supply curve |
| Owner DI → area 3,500 consequence | Pump rated flow/pressure / churn / 150% |
| Show-and-verify + `[SYN]`/`[V]`/status register | Node-by-node tree, K√P, pipe schedule |
| Consume demand-area HINT from occupancy-hazard-fork | Storage / ESS / commodity density design |

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent HC/OH, density, system family, carrier, or area from habit.

| Input | Required | Rule |
|---|---|---|
| **Completed `most-stringent-basis-matrix` result** | **yes** | Consume jurisdiction/editions, carrier union, owner posture, provisional/`[V]` rows, wet/dry/DI fences, and NFPA 13-2025 delta rows that touch density, area, hose, or duration. Do **not** rebuild the matrix. Dual-carrier with unresolved density/area rows → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged). |
| **Completed `suppression-technology-selection` result** | **yes** | Must show **elected** `wet` \| `dry` \| `double-interlock` within company scope. Comparison-only SI/NI status is not an election. Missing or prohibited election → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `occupancy-hazard-fork` result** | **yes** | Consume HC/OH (or AXA OH), ceiling height, demand-area **HINT**, off-table flags, and system-family inheritance. **Do not re-classify occupancy.** Missing HC/OH (and density not already pinned) → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `fire-area-compartmentation-schedule` result** | **yes when** multi-hall / fire-area schedule already exists for the program | Consume fire-area identity / boundary context for which hall’s demand is being sized. Do not design FRR here. Absent on a true single-fire-area job → continue; mark fire-area intake `n/a`. Required but missing on a multi-hall job → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (state which hall's demand is assumed). |
| **Elected `system_type`** | **yes** | `wet` \| `dry` \| `double-interlock` only. SI/NI as BOD → **Stop** (§1.1). |
| **`hazard` or pinned `density_gpm_ft2`** | **yes** | FM **HC-1 / HC-2 / HC-3**, or NFPA 13 **OH-1 / OH-2**, or density already resolved from matrix/occupancy. White-space hall on FM = **HC-2**. |
| **`ceiling_height_ft`** | **yes** | FM DS 5-32 **30 ft (9 m) cap**. ≤30 ft → table values. **>30 ft on FM without cited off-table path → Stop.** |
| **Demand-area HINT** | **yes** (from occupancy-hazard-fork) | Starting `base_area_ft2`. Do not invent past the hint without a cited sheet. |
| **`hose_gpm` / `duration_min`** | **yes** | Prefer matrix-pinned or FM sheet values. FM HC-1/HC-2 default **250 gpm / 60 min**. |
| (NFPA 13-2025 delta for hose/duration) | — | [CODE NFPA 13-2025 Table 19.2.3.1.2: OH 250 gpm / 60 or 90 min; EH 500 / 90 or 120; lower value only per §19.2.3.1.3 (supervised + monitored at a constantly attended location)]. Print vs FM 250/60. |
| **Controlling carrier** | **yes** (usually inherited) | `FM` \| `AXA XL` \| other named. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Dual-carrier without matrix union → **not a Stop**: take the more stringent carrier value per parameter (flag `ASSUMED`) or hand back to `most-stringent-basis-matrix`. |
| **Owner interlock / area mandate** | **yes** (may be `none`) | Owner may force DI → dry area 3,500. NDA → posture-only. |
| **AHJ-enforced NFPA 13 edition** | **yes** to cite | Delta baseline = **NFPA 13-2025**. Enforced ≠ latest. Prefer matrix pins. |
| **Caller output path** | **yes** for file output | Typically `<name>.calc.json` + short markdown verification. If unnamed, return results in the response and stop. |
| Optional K, spacing, coverage/head | no | Not needed for density×area demand. If invented → **`[SYN]`**. |

**Do not invent** an FM density, an AXA density method, an NFPA 13 section number for general dry/DI +30% other than [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5], a stacked `3500 × 1.30`, or a storage/ESS demand disguised as HC-2. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `most-stringent-basis-matrix` | Editions; carrier union; density/area/hose/duration rows; provisional/`[V]`; NFPA 13-2025 deltas; company wet/dry/DI fence | Rebuild jurisdiction register or dual-carrier union |
| `suppression-technology-selection` | Elected wet/dry/DI; comparison-only / prohibited status | Elect a system family |
| `occupancy-hazard-fork` | HC/OH; demand-area HINT; ceiling; off-table / storage / ESS flags | Re-classify occupancy; convert greatest-hazard into gpm |
| `fire-area-compartmentation-schedule` | Fire-area id / hall boundary context when present | Design ratings, doors, dampers |

If a required upstream result is missing or marks a controlling density/area/system row `unresolved` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first); the demand is ASSUMED-based.

### 2.2 Demand-area HINT intake (mandatory)

Consume the occupancy-hazard-fork hint; do not recalculate classification:

| Route | Wet hint | Dry / DI hint |
|---|---:|---:|
| FM HC-2 @ ≤30 ft | 2,500 ft² | 3,500 ft² |
| FM HC-1 @ ≤30 ft | 1,500 ft² | 1,500 ft² |
| AXA OH Group 1 | NFPA 13 area `[V]` | Directional DI adjustment `[V]` |
| NFPA 13-2025 delta | Matrix-linked | Matrix-linked |

Hints are **area only**. Do not add hose, duration, density, flow, tank volume, or pump margin at the hint step — that arithmetic is this Skill’s job after pins are confirmed.

**Off-table / handoff:** storage, ESS/Li-ion, generator/fuel, transformer apparatus, unresolved telecom/switchgear object routes → **Stop** or `handoff`; do not size as ordinary HC-2 0.2 / 2,500. Greatest-hazard boundary consequences are **classification**, not density calcs.

### 2.3 Look up by title

*The Design practice*; *Enforced-vs-latest edition resolver and reference pins*; *FM DS 5-32 insurer design basis*; *FM hazard category for data-center spaces*; *Data-center sprinkler and preaction design*; *AXA XL insurer design basis*; *FM occupancy vs installation sheet precedence DS 5-32 and DS 2-0*; *Dry-pipe and double-interlock air supply and water delivery*; *The hyperscaler owner-standard layer*; shop `calcs` README / `density_area` formula.

---

## 3. Pin editions (enforced ≠ latest)

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor | NFPA 13 density/area; dry/DI +30% delta | **NFPA 13-2025** for the delta baseline. AHJ-enforced edition often a cycle behind — surface both. **General dry/DI +30%:** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5]. |
| Insurer | Controlling sheet | **FM DS 5-32, January 2026** (DC occupancy). Demand backbone **FM DS 3-26, April 2025** (Table 2.3.1.10, §2.3.1.7, §2.3.1.11–13). Install sheet **FM DS 2-0, October 2021 / Interim Rev. January 2024** (do not silently restack its airflow +30%). **AXA XL** DC white paper **March 2026** (OH-1; DI +30% area + nitrogen; **no density/area tables**). |
| Owner | Interlock posture / any numeric raise | Project-issued standard. Public posture ≠ basis of design. |

Inherit pins from `most-stringent-basis-matrix` when present. FM DS 5-32 (Jan-2026) can cite lagged standards internally — always cite **section AND edition**; do not let the sheet’s reference list silently stand in for the enforced code.

---

## 4. Confirm prerequisites, then consume

1. Assignment packet exists (other Skill) — do not rebuild.
2. `most-stringent-basis-matrix` completed — consume density/area/hose/duration / delta rows.
3. `suppression-technology-selection` completed — elected system is wet, dry, or double-interlock.
4. `occupancy-hazard-fork` completed — HC/OH + demand-area HINT + ceiling; no re-classification.
5. `fire-area-compartmentation-schedule` present when the program is multi-hall / fire-area scoped.
6. If HC/OH missing and density not already pinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (state the hazard assumed and why).
7. If elected system_type is SI/NI → **Stop** (§1.1; company scope lock). If missing → `ASSUMED` company family (wet | dry | DI only, with why), flagged — not a Stop.
8. If two carriers both apply and matrix union is missing/unresolved → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand back to `most-stringent-basis-matrix`. Do not blend levers here.

---

## 5. Resolve DENSITY (3-layer, separately from area)

Do **not** invent a density.

| Source | Density | Cite | Status |
|---|---|---|---|
| Code floor | OH-1 **0.15 / 1,500**, OH-2 **0.20 / 1,500** [CODE NFPA 13-2025 Table 19.2.3.1.1; 2022 Table 19.2.3.1.1 (new systems; Figure 19.2.3.1.1 curves for existing)]. | Hydraulic-calculation-method note | held |
| FM HC-2 white space, ≤30 ft | **0.2 gpm/ft² (8 mm/min)** | FM DS 5-32 **§2.4.3.3.1.1.A (Jan-2026)**; identical root FM DS 3-26 **Table 2.3.1.10 (April 2025)** | `grounded` |
| FM HC-1 (NOC/telecom), ≤30 ft | **0.1 gpm/ft²** over 1,500 ft² wet & dry | FM DS 3-26 **Table 2.3.1.10 (April 2025)** — only if occupancy-hazard-fork classified HC-1 | `grounded` when so classified |
| AXA XL | **No density.** Occupancy = **Ordinary Hazard Group 1** per NFPA 13 | AXA XL white paper **p.8 (Mar-2026)** | incomplete basis |
| Owner | May raise; may be NDA | Project standard | capture if numeric |

**Union:** most stringent numeric density that is actually pinned. On an FM-insured HC-2 hall, **0.2 gpm/ft²** controls. On an AXA-XL-only job, occupancy-hazard-fork or matrix (or NFPA 13-2025 once pinned) must supply density. **AXA XL alone is not a complete sprinkler basis**. If density is still unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; never presented as a cited AXA/NFPA value.

Metric check (show it): `0.2 gpm/ft² × 40.746 ≈ 8.15 mm/min` → FM’s stated **8 mm/min** is the rounded value.

Prefer density rows already closed in `most-stringent-basis-matrix`. Do not silently override a matrix `provisional` / `[V]` without flagging the same status.

---

## 5A. ESS / Li-ion room override (added 2026-10-22, fpskills-2026-10-22)

This section applies only when `ess-isolation-venting-and-duration` hands over an installed Li-ion ESS room. That room is not on the HC-2 white-space table.

- **Density and area (≤ 50 kWh groups):** 0.30 gpm/ft² over the room area or 2,500 ft², whichever is smaller [CODE IFC 2024 §1207.5.5 item 1, pull IBC-IFC-24-bess]. Union with FM DS 5-33 §2.4.1 (0.30 over the ROOM) and take the most stringent.
- **Groups over 50 kWh:** no density without a UL 9540A installation-level test basis [CODE IFC 2024 §1207.5.5 item 2]. Report the density as `unresolved` and do not run the calc.
- **Dry / DI:** apply the +30 % increase to the §1207.5.5 area [CODE NFPA 13 2025 §19.2.3.2.6]. Verify the math: 2,500 × 1.30 = 3,250 ft², and 0.30 × 3,250 = 975 gpm (wet is 0.30 × 2,500 = 750 gpm).
 - When 3,250 ft² is larger than the room, carry the full 3,250 ft². This is the conservative case. NFPA 13-2025 has no text on a design area larger than the room (only §19.2.3.1.4 / §19.2.3.3.4 for rooms smaller than the area); multiple adjustments compound from the Table 19.2.3.1.1 area (§19.2.3.2.8.1) . **Verify with the engineer of record** before capping the area at the room size.
- NFPA 855-2023 §4.9.2.1 matches IFC 0.30 / room-or-2,500; §4.9.2.2 >50 kWh from §9.1.5 testing; A.4.9.2.2 points to UL 9540A installation-level Method 1 — no longer `[V]`.
 - Do not stack the FM 3,500 ft² area with the +30 %.
- **Hose and duration:** NFPA 13-2025 Table 19.2.3.1.2 extra-hazard row gives 500 gpm hose and 90 or 120 min (90 only with supervised, monitored waterflow/supervisory per §19.2.3.1.3) [CODE NFPA 13-2025 Table 19.2.3.1.2]. Applying the EH row to an ESS room is still **Verify with the engineer of record**. Neither is cited for ESS: IFC §1207.5.5 gives density only, and the 500 gpm is the NFPA 13 extra-hazard hose value carried over. Union with FM DS 5-33 §2.4.1 (250 gpm hose) and take the most stringent.
- **Exhaust-duct sprinklers:** when they are fed from this system, add their flow to the demand (see `ess-exhaust-duct-shaft-and-duct-sprinklers`).

## 6. Resolve design AREA — controlling company path

### 6.1 Controlling elections only (wet / dry / DI)

**Company controlling path — use absolute FM areas; `area_increase = 0` on the controlling run:**

| Elected `system_type` | FM area (DC hall / HC-2) | Kernel `base_area_ft2` | Kernel `area_increase` |
|---|---|---|---|
| `wet` | 2,500 wet | **2500** | **0** |
| `double-interlock` | 3,500 dry | **3500** | **0** |
| `dry` (dry-pipe) | 3,500 dry | **3500** | **0** |

FM DS 5-32 **§2.4.3.3.1.1.A (Jan-2026)** pins absolute areas: **2,500 ft² (230 m²) wet / 3,500 ft² (330 m²) dry**. Relative equivalent of the dry bump: **(3,500 − 2,500) / 2,500 = 0.40 = ≈+40%**.

FM DS 5-32 **§2.4.3.2.1.2 (Jan-2026)** (comparison context for carrier preference):

- **(B)** non-interlock or single-interlock → wet demand → 2,500 ft² — **comparison-only for company Skills**
- **(C)** double-interlock → dry demand → 3,500 ft² — **aligns with permitted DI election**

**Never stack:** do not run controlling demand as `area = 3500` **and** `area_increase = 0.30`. FM dry/DI controlling step is absolute **3500 / 0**.

### 6.2 Owner double-interlock mandate

If the owner forces double-interlock, **AREA becomes 3,500** even though FM’s preference order ranks DI last (**§2.4.1.1, Jan-2026**). That is Layer-3 on **AREA**, not a density change. Record FM/AXA pushback; still size dry when DI is the elected company system. Do not treat owner DI as automatically more stringent on every axis (delivery time, reliability).

### 6.3 Comparison-only: SI / NI evidence (not controlling)

Keep these as **comparison / teaching** rows only. They do **not** authorize company election or controlling `qd`.

| Comparison system | FM DS 5-32 (Jan-2026) evidence | FM DS 3-26 (April 2025) evidence | Company action |
|---|---|---|---|
| Single-interlock | §2.4.3.2.1.2(B) → wet 2,500; **never** dry +30% / 3,500 | §2.3.1.7 → SI may be wet or dry | Comparison-only; BOD request → **Stop / RFI-variance** |
| Non-interlock | §2.4.3.2.1.2(B) → wet 2,500 on DS 5-32 occupancy | §2.3.1.7 → NI treated as DRY → 3,500 | Flag sheet conflict; comparison-only; BOD request → **Stop** |

For a **DS 5-32 occupancy (DP / IT hall)**, the occupancy sheet wins over DS 3-26 where they differ — as **carrier evidence**, not as permission to elect NI/SI. If both sheets are claimed without an occupancy-sheet override, Design practice most-stringent **comparison** on AREA would show dry 3,500 for non-interlock. **Flag the conflict and controlling citation**; do not average; do not elect NI.

### 6.4 AXA XL DI lever (do not blend with FM)

AXA XL **(Mar-2026, p.8):** prefers single-interlock (comparison-only for company); **double-interlock penalty = +30% design area AND nitrogen-fill**. Different lever, different base (OH-1 per NFPA 13, not FM’s 2,500). **Apply the controlling carrier’s lever, not a blend.**

- FM job, elected DI/dry → FM absolute **3,500** + ≤30 s delivery consequence (delivery proof is another Skill).
- AXA XL job, elected DI → +30% on the *AXA/NFPA* base + nitrogen; density must still be pinned elsewhere or carried as a stated `ASSUMED` value (flagged).
- Dual-carrier → `most-stringent-basis-matrix` owns the union; this Skill consumes the controlling row only.

### 6.5 NFPA 13-2025 +30% (delta column only)

NFPA 13 applies a **+30% design-area increase to dry-pipe and double-interlock-preaction** systems. [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5].

**Cite the dry/DI +30% rule by edition:** 2025 §19.2.3.2.6 · 2022 §19.2.3.2.5 · 2019 §19.3.3.2.5 . Always give the edition with §19.2.3.2.5, because the number means a different rule in 2025 (ceilings over 30 ft).

Wet does **not** take the general dry/DI +30%. SI would not either — but SI is not a company election.

Do **not** feed NFPA +30% into the controlling FM run. Run it as a **delta step** (§9). Consume matrix delta rows when present.

---

## 7. High-ceiling fork

- **FM DS 5-32 §2.4.3.3.1.1.C and §2.2.5.2 (Jan-2026):** max ceiling **30 ft (9 m)**. Table / DS 5-32 numbers are **HC-2 @ ≤30 ft**. **Ceiling > 30 ft on FM without a cited off-table occupancy path → Stop.** Do not invent a high-ceiling density. Status: `unresolved` / `handoff`.
- **NFPA 13 high-ceiling mechanisms:** consume from `most-stringent-basis-matrix`. OH1 “+30% area for ceilings > 30 ft” [CODE 2025 §19.2.3.2.5.2(A)]. Cite by edition: the ceilings-over-30 ft rule is 2025 §19.2.3.2.5 [CODE 2025]; in 2022 that same number is the dry/DI +30% rule.
- **Do not conflate** high-ceiling +30% with **FM DS 2-0 §2.5.2.1.8.1** (Oct-2021 / Jan-2024) airflow option 2 (ceiling-plane > **5 ft/s (1.5 m/s)** and hazard **> HC-1** → one option is +30% design area, stacking with dry area **`[V]`**). That is an install-sheet gate, not this Skill. Raise it; do not silently price it into `area_increase`.

---

## 8. Most-stringent union (DENSITY × AREA separately)

Build two 3-layer rows, then take the union:

| | Code floor | Insurer | Owner | Controlling |
|---|---|---|---|---|
| **Density** | OH `[V]` | FM **0.2** (HC-2) or AXA XL *none* | may raise | max pinned |
| **Area** | wet OH `[V]` · dry/DI **×1.30** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5] | FM **2,500 wet / 3,500 dry (≈+40%)** · AXA XL DI **+30% + N₂** | may **force DI → 3,500** | most stringent *applicable* area after elected-system fork |

**Key delta to always print:** FM absolute **2,500 → 3,500 ≈ +40%** vs NFPA 13-2025 **+30%** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5]. On a 2,500 wet base, NFPA +30% → **3,250 ft²**; FM dry is **250 ft² larger**. Wet jobs **avoid both** bumps. DI/dry jobs take FM 3,500 when FM controls.

Canonical shop minima (FM HC-2, hose 250, 60 min), density-method, **not** balanced hydraulics:

| Elected system | Area | q_spr | qd | gallons | Status |
|---|---|---|---|---|---|
| Wet | 2,500 | 500 gpm | **750 gpm** | **45,000 gal** | `grounded` FM path |
| Double-interlock / dry | 3,500 | 700 gpm | **950 gpm** | **57,000 gal** | `grounded` FM path |
| NFPA +30% on 2,500 (delta only; 2025 §19.2.3.2.6) | 3,250 | 650 gpm | 900 gpm | 54,000 gal | `comparison-only` |
| SI wet 2,500 (if proposed) | 2,500 | 500 | 750 | 45,000 | **`comparison-only`** — not BOD |

Owner-mandated DI vs wet: **+200 gpm / +12,000 gal** from area alone (+26.7% on the 750 gpm wet total).

These are **MINIMA**. Inner-head over-discharge (typically ~1.1–1.3×) is a node-by-node hydraulic Skill, not this one.

---

## 9. Run `calcs/fp/run.py` — kernel is source of truth

Stdlib kernel. Agents **set inputs and interpret**. Paste **stdout**. QA re-runs the **same JSON**. Exit **2** on bad inputs. Transcript ends with `TRANSCRIPT_OK`. Rounding: **4 decimal places** unless the value is an integer.

**Kernel formula (do not hand-roll):**

```
design_area = base_area_ft2 * (1 + area_increase)
q_spr = density_gpm_ft2 * design_area
qd = q_spr + hose_gpm
gallons = qd * duration_min # hose already inside qd
```

**Preferred: JSON batch** (write JSON at the **caller-named** path, next to the deliverable):

```
python3 calcs/fp/run.py path/to/name.calc.json
```

JSON shape (ops `density_area` / `density-area`):

```json
{
 "job": "<caller job id>",
 "notes": "density-area demand; controlling vs NFPA +30% delta; elected wet|dry|DI only",
 "steps": [
 {
 "id": "qd_controlling",
 "op": "density_area",
 "density": 0.20,
 "area": 2500,
 "area_increase": 0,
 "hose": 250,
 "duration_min": 60
 },
 {
 "id": "qd_nfpa_delta",
 "op": "density_area",
 "density": 0.20,
 "area": 2500,
 "area_increase": 0.30,
 "hose": 250,
 "duration_min": 60
 }
 ]
}
```

For FM **dry / DI**, the controlling step is **absolute area**, not a stacked increase:

```json
{ "id": "qd_controlling", "op": "density_area", "density": 0.20, "area": 3500, "area_increase": 0, "hose": 250, "duration_min": 60 }
```

Equivalent relative check (optional third step; must **not** replace the absolute 3,500 run): `"area": 2500, "area_increase": 0.40` → same 3,500 / 700 / 950 / 57,000.

**Ad-hoc** (one op, no JSON; still paste stdout; prefer JSON for QA):

```
python3 calcs/fp/run.py density-area --density 0.20 --area 2500 --area-increase 0 --hose 250 --duration 60
python3 calcs/fp/run.py density-area --density 0.20 --area 3500 --area-increase 0 --hose 250 --duration 60
python3 calcs/fp/run.py density-area --density 0.20 --area 2500 --area-increase 0.30 --hose 250 --duration 60
```

CLI flags: `--density` `--area` `--area-increase` (default 0) `--hose` (default 0) `--duration` (optional; enables gallons).

**JSON / CLI aliases → formula kwargs**

| You may write | Kernel kwarg |
|---|---|
| `density` / `density_gpm_ft2` / `--density` | `density_gpm_ft2` |
| `area` / `base_area` / `base_area_ft2` / `--area` | `base_area_ft2` |
| `area_increase` / `--area-increase` | `area_increase` |
| `hose` / `hose_gpm` / `--hose` | `hose_gpm` |
| `duration` / `duration_min` / `--duration` | `duration_min` |

**Stdout keys to harvest:** `design_area_ft2`, `q_spr_gpm`, `hose_gpm`, `qd_gpm`, `duration_min`, `gallons`, `gallons_note` (`hose already inside qd`).

**Expected transcripts (FM HC-2, 0.20 density, 250 hose, 60 min):**

Wet (`area 2500`, `area_increase 0`):

```
CALC KERNEL TRANSCRIPT
job: (adhoc)
steps: 1

--- step density_area op=density_area formula=density/area demand ---
inputs
 density_gpm_ft2: 0.2000 gpm/ft2
 base_area_ft2: 2500 ft2
 area_increase: 0
 hose_gpm: 250 gpm
 duration_min: 60 min
outputs
 design_area_ft2: 2500 ft2
 q_spr_gpm: 500 gpm
 hose_gpm: 250 gpm
 qd_gpm: 750 gpm
 duration_min: 60 min
 gallons: 45000 gal
 gallons_note: hose already inside qd

TRANSCRIPT_OK
```

DI / dry (`area 3500`, `area_increase 0`): `design_area_ft2: 3500` · `q_spr_gpm: 700` · `qd_gpm: 950` · `gallons: 57000`.

NFPA +30% delta (`area 2500`, `area_increase 0.30`) [2025 §19.2.3.2.6]: `design_area_ft2: 3250` · `q_spr_gpm: 650` · `qd_gpm: 900` · `gallons: 54000`.

If stdout disagrees with a hand product, **the kernel wins**. Re-check inputs (especially stacked `area_increase` on an already-dry `base_area`).

---

## 10. Show-and-verify (independent of stdout)

Write the arithmetic in the markdown verification so a reviewer can recompute without the kernel:

```
design_area = 2500 × (1 + 0) = 2500 ft²
q_spr = 0.20 × 2500 = 500 gpm VERIFY: 0.2×2000=400; 0.2×500=100; 400+100=500
qd = 500 + 250 = 750 gpm
gallons = 750 × 60 = 45,000 gal VERIFY: 750×6=4,500; ×10=45,000
```

Dry / DI:

```
design_area = 3500 × (1 + 0) = 3500 ft²
q_spr = 0.20 × 3500 = 700 gpm
qd = 700 + 250 = 950 gpm
gallons = 950 × 60 = 57,000 gal
FM bump = (3500−2500)/2500 = 0.40 = +40% VERIFY: 0.40×2500=1000
NFPA +30%[CODE]= 2500 × 1.30 = 3250 ft²
FM − NFPA = 3500 − 3250 = 250 ft² (FM more stringent on area)
```

**Do not** multiply whole-hall area × density for demand. Demand is over the **remote design area**, independent of hall size. Whole-hall area is a head-count input to layout, not this Skill.

---

## 11. Status flags and honesty marks

| Flag / status | Use |
|---|---|
| `grounded` | Value pinned to cited section **and** edition in corpus (e.g., FM 0.2 / 2,500 / 3,500 / 250 / 60 / 30 ft) |
| `provisional` | Inherited provisional matrix/occupancy row; usable only with the same caveat visible |
| `unresolved` | Controlling pin missing; cannot close `qd` |
| `comparison-only` | SI/NI evidence, NFPA +30% delta column, carrier preference rankings — not BOD |
| `handoff` | Work owned by another Skill |
| `RFI-variance` | Caller asks SI/NI/foam/mist as BOD; company-fence gate |
| **`[SYN]`** | Invented K-factor, spacing, coverage/head, pipe schedule, supervisory pressure, or any number not on a cited sheet |
| **`[V]`** | Unpinned / unmined / directional — see §16 |

Grounded FM numbers (0.2 / 2,500 / 3,500 / 250 / 60 / 30 ft) do **not** need `[SYN]`.

K and spacing are **out of scope** for demand. If the caller asked for them anyway, mark `[SYN]` and do not let them alter `qd`.

---

## 12. Output

Write **only** to the path the **caller** names (typically a `.calc.json` transcript plus a short markdown verification beside it). Do **not** write into,,, or any shop codebook tree.

**`.calc.json`** — the JSON actually run (QA re-runs this file). Keep a `.calc.stdout.txt` (or paste stdout into the markdown). Transcript must end with `TRANSCRIPT_OK`.

**Markdown verification** (short) must contain:

1. Pinned editions (code / insurer / owner), inherited from matrix where possible.
2. Upstream consumption block: matrix + suppression-technology-selection + occupancy-hazard-fork (+ fire-area schedule when required) — fields consumed, not rebuilt.
3. Elected system_type = wet \| dry \| DI only; any SI/NI shown as `comparison-only`.
4. Consumed demand-area HINT (HC/OH, wet vs dry/DI hint); off-table rows not sized here.
5. 3-layer table for **density** and **area** separately; controlling values; owner interlock effect on area.
6. Controlling area fork: wet = 2,500 / `area_increase=0`; dry or DI = 3,500 / `area_increase=0`.
7. Kernel command + **full stdout**.
8. Show-and-verify `q = density × area`, `Q = q + hose`, `V = Q × duration`.
9. Directional delta vs NFPA 13-2025: FM **≈+40%** vs NFPA **+30%** cited by edition (2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5).
10. Statement that `qd` is a **density-method minimum**, not balanced demand.
11. Status / `[SYN]` / `[V]` / `RFI-variance` / `handoff` register.
12. Explicit hand-off: **`hydrant-supply-curve`** → **`pump-envelope`** (and matrix if dual-carrier still open; hydraulic tree when node-by-node work begins).

---

## 13. Stop conditions

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

Return the blocker (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess.

1. Missing required upstream result: `most-stringent-basis-matrix`, `suppression-technology-selection`, or `occupancy-hazard-fork`.
2. Multi-hall / fire-area program missing required `fire-area-compartmentation-schedule`.
3. Missing **HC/OH** (and density not already resolved) or missing **elected** system type.
4. Caller asks to size **single-interlock**, **non-interlock**, or other non-allowed preaction as BOD → `RFI-variance`.
5. Caller asks to elect/design **foam** or **mist** → prohibited / `PRACTICE REFUSED`.
6. **Unpinned carrier** (cannot choose FM absolute areas vs AXA XL +30%+N₂ vs code-floor `[V]`).
7. **Dual-carrier** job without a completed matrix union: hand back to `most-stringent-basis-matrix`; do not blend FM 3,500 with AXA XL +30%+N₂.
8. **Ceiling > 30 ft on FM** with no cited off-table occupancy path.
9. Storage / ESS / commodity / generator-fuel / transformer **off-table** route presented as ordinary HC density×area.
10. Trying to **size pipe, K-factor, remote-head pressure, C-factor, or a node-by-node tree** here.
11. Trying to **re-classify occupancy** or convert greatest-hazard into gpm (wrong Skill).
12. Trying to **select a fire pump**, run a **hydrant supply curve**, or overlay supply here.
13. AXA-XL-only job with **density still unpinned** (white paper has no density/area tables).
14. Liquid-cooled hall whose coolant classification would displace this basis (open ignitable-liquid immersion → other occupancy sheet, not HC-2 0.2/2,500). Occupancy-hazard-fork should have gated this; if it didn’t, **Stop**.
15. Attempt to stack `area=3500` with `area_increase=0.30` on the controlling run.
16. Caller asks to write into / / agent worktrees / .

---

## 14. Not this Skill / handoffs

| Work | Where it lives |
|---|---|
| Jurisdiction / carrier / owner matrix | `most-stringent-basis-matrix` |
| System-family election | `suppression-technology-selection` |
| Occupancy / HC / OH classification; demand-area HINT | `occupancy-hazard-fork` (this Skill *consumes* that schedule) |
| Fire-area / FRR / door / damper schedule | `fire-area-compartmentation-schedule` |
| Dual-carrier reconciliation | `most-stringent-basis-matrix` (not a separate dual-carrier Skill) |
| Hydrant / municipal supply curve vs `qd` | **`hydrant-supply-curve`** (next after this Skill) |
| Pump rated flow/pressure, churn, 150% envelope | **`pump-envelope`** (after hydrant verdict says pump needed, or as sequenced by parent) |
| Node-by-node hydraulic tree, BOR psi, pipe schedule, K√P | hydraulic-calc Skill (`calcs` `hw` is a *single segment*, not a tree) |
| Water-delivery-time / SprinkFDT | not in `calcs`; vendor-listed |
| VEWFD, releasing SOO, Li-ion barriers, ESS sprinkler | other recipes |
| Foam / mist / clean-agent / hybrid / ORS design | prohibited / refused / specialist Skills |

**Downstream order for water supply:** this Skill’s `qd_gpm` + `duration_min` + gallons → **`hydrant-supply-curve`** → then **`pump-envelope`** when a pump is indicated. Do not skip the hydrant curve by jumping straight to pump selection unless the parent explicitly sequences otherwise **and** supply proof is already closed.

---

## 15. Design practice

1. **Three-layer, most stringent, on DENSITY and AREA separately.** Code is the floor (IFC/IBC → adopted NFPA 13 edition). Insurer sheet usually sets the real basis (FM DS 5-32 Jan-2026 on FM jobs). Owner standard can raise AREA by forcing double-interlock (dry 3,500) even when FM ranks DI last. Cite the sheet. Do not assert interlock from habit. Company elections remain wet / dry / DI only.
2. **Delta vs NFPA 13-2025 every time.** FM **fixes** absolute wet/dry areas (**2,500 → 3,500, ≈+40%**) and **0.2 gpm/ft²**, plus QR, 30 ft cap, ≤30 s preaction delivery, mandatory VEWFD. NFPA 13 sets occupancy (commonly OH-1/OH-2 `[V]`) and a **+30% dry/DI area increase** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5]. Net: FM is more prescriptive and generally more stringent on a white-space hall. If the numeric floor isn’t pinned, say **directional `[V]`**. Do not invent a 13-2025 section number. Do not misuse §19.2.3.2.5 as the general dry/DI +30%.
3. **Show-and-verify.** Kernel stdout + independent `density × area` / `+ hose` / `× duration`. Hose is added at the demand point, already inside `qd` / gallons.
4. **Current editions; enforced ≠ latest.** Default NFPA 13-**2025** for the delta baseline; report the AHJ-referenced edition when it differs.
5. **Honesty on minima.** Density×area is the **lower bound**. Balanced demand is higher. Do not size the campus pump from 500 gpm when the tree will run ~1.2×.
6. **Consume upstream; fence media.** Matrix / STS / occupancy / fire-area results are inputs. Foam prohibited; mist `PRACTICE REFUSED`; SI/NI comparison-only.

---

## 16. Citations

Shop codebook **by title** (not a required filesystem path). Prefer these section+edition pins; omit or `[V]` anything not here.

### 16.1 Grounded — FM DS 5-32 (January 2026)

*FM DS 5-32 insurer design basis*; *Data-center sprinkler & preaction design*

| Claim | Section |
|---|---|
| Interlock preference order Wet → NI → SI → DI last (comparison evidence) | §2.4.1.1 |
| Hose 250 gpm | §2.4.1.5 |
| Duration 60 min | §2.4.1.6 |
| NI/SI → wet demand; DI → dry demand (carrier evidence) | §2.4.3.2.1.2 (B)/(C) |
| Preaction ≤30 s to most remote sprinkler | §2.4.3.2.1.2.D |
| Density 0.2 gpm/ft²; area 2,500 wet / 3,500 dry | §2.4.3.3.1.1.A |
| QR; 135 °F wet / 165 °F dry; 30 ft cap; spacing 12 ft | §2.4.3.3.1.1 / .B / .C / .E |
| Concealed-space EC at same 0.2 / 2,500 wet / 3,500 dry | §2.4.3.4.1.1 |

### 16.2 Grounded — FM DS 3-26 (April 2025)

*FM hazard category for data-center spaces*

| Claim | Section |
|---|---|
| IT Facilities / white space = HC-2 | Appendix C Table C-1 |
| HC-2 @ ≤30 ft = 0.2 / 2,500 wet / 3,500 dry | Table 2.3.1.10 |
| HC-1 @ ≤30 ft = 0.1 / 1,500 wet & dry | Table 2.3.1.10 |
| SI = wet or dry; NI and DI = treat as DRY (conflict with DS 5-32 (B); occupancy sheet wins on a DP hall — comparison evidence) | §2.3.1.7 |
| Hose 250 (HC-1/2) / 500 (HC-3); 60 min; min 7 psi remote | §2.3.1.11–13 (7 psi is a **hydraulics input**, not this Skill’s output) |

### 16.3 Grounded — AXA XL (March 2026)

*AXA XL insurer design basis*: OH Group 1 (p.8); single-interlock preferred (**comparison-only** for company); DI **+30% design area + nitrogen fill** (p.8); **no** density/area/K tables.

### 16.4 Deliberately `[V]` — do not fake pins

| Claim | Why `[V]` |
|---|---|
| NFPA 13 **general** dry-pipe / double-interlock **+30% area** section number | Held: [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5] |
| Citing **§19.2.3.2.5** without an edition | **Forbidden** — it is the dry/DI +30% rule in 2022 but the ceilings-over-30 ft rule in 2025 |
| OH-1 / OH-2 numeric density/area as quoted 13-2025 code | Held: [CODE NFPA 13-2025/2022 Table 19.2.3.1.1] |
| High-ceiling +30% as a universal code-floor lever | Unpinned / matrix-linked; do not invent |
| 130 ft²/head OH cap [CODE NFPA 13-2019/2025 Table 10.2.4.2.1(b) Ordinary Hazard, all construction rows: 130 ft² max protection area, standard pendent/upright spray;]; NFPA 13-2025 min pressure if used | Not pinned for this Skill’s demand output |
| DS 2-0 airflow +30% stacking with dry area | Install-sheet gate; stacking unverified → `[V]`; raise, don’t silently price |
| AXA XL “NFPA 13” with no edition | White paper silent on edition |
| Potter/Viking preaction § numbers from older editions | Reconcile to 2025; do not treat 2019/2007 § as 2025 |

### 16.5 Kernel

`calcs` README / `run.py` / `formulas.density_area`: `design_area = base_area_ft2 * (1 + area_increase)`; `q_spr = density * design_area`; `qd = q_spr + hose`; optional `gallons = qd * duration_min`.

---

## Check before you finish

- `most-stringent-basis-matrix` consumed (editions, carrier union, density/area/hose/duration, deltas). Not rebuilt.
- `suppression-technology-selection` consumed; elected system is **wet | dry | double-interlock** only.
- `occupancy-hazard-fork` consumed (HC/OH + demand-area HINT + ceiling). Classification not redone. Off-table not sized as HC-2 default.
- `fire-area-compartmentation-schedule` consumed when multi-hall / required; else marked `n/a`.
- Company fence enforced: SI/NI = `comparison-only`; SI/NI-as-BOD → stopped / `RFI-variance`. Foam prohibited; mist `PRACTICE REFUSED`.
- Editions pinned: NFPA 13-2025 (delta) + AHJ edition; FM DS 5-32 Jan-2026 and/or AXA XL Mar-2026; DS 3-26 April 2025 if HC-rooted; owner posture.
- Density taken from a cited sheet or matrix row (FM 0.2 HC-2, FM 0.1 HC-1, or fork-resolved). Not invented. AXA-XL-only without density → stopped.
- Controlling area: **wet → 2,500 / `area_increase=0`**; **dry or DI → 3,500 / `area_increase=0`**. No `3500×0.30` stack.
- Owner DI mandate applied to **AREA** (3,500) when DI is elected.
- Dual-carrier not blended; unresolved dual-carrier → handed back to matrix.
- Ceiling ≤30 ft on FM, or stopped / handed off.
- JSON written at **caller path**; `python3 calcs/fp/run.py <that.json>` run; stdout pasted; `TRANSCRIPT_OK`; exit 0.
- Independent verify: q = density × area, Q = q + hose, V = Q × duration. Hose labeled inside `qd`.
- Delta printed: FM 2,500→3,500 **≈+40%** vs NFPA **+30%** cited by edition (2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5). Wet: both bumps **avoided**.
- Result labeled **density-method minimum**; handoff **`hydrant-supply-curve` then `pump-envelope`**.
- Status register complete: grounded / provisional / unresolved / comparison-only / handoff / RFI-variance + `[SYN]` / `[V]`.
- Support ordinary-hazard wet duration recorded per §17. Supervised and monitored: **60 min**. FM DS 3-26 §2.3.1.13 is **60 min for all HC**. **E3=E1**. The 90 min branch only when the AHJ or the owner requires the unsupervised case.

---

## 17. Support-space duration — E3=E1, 60 min for all HC

Support ordinary-hazard group 2, wet:

- **E1.** **60 min** under NFPA 13-2025 §19.2.3.1.3 when the waterflow and supervisory devices are supervised and monitored at a constantly attended location. Show-and-verify `[SYN]`: 550 gpm × 60 min = **33,000 gal**.
- **E3.** Closed. **E3=E1**. FM DS 3-26 (April 2019, interim revision April 2025) §2.3.1.13 is **60 min for all HC**. Hose is **250 gpm** for HC-1 and HC-2 (§2.3.1.12). Delta versus NFPA 13-2025 on this duration: none.
- **E2.** 90 min and 49,500 gal only when the AHJ or the owner requires the unsupervised branch of §19.2.3.1.3.

A hall demand times its own duration (teaching figure 66,797 gal) still governs supply and storage when it is larger. Do not shorten the hall to the support-space volume. Density, area, and the dry-area increase in the sections above are unchanged. This section does not elect foam, a clean agent, or single-interlock.
