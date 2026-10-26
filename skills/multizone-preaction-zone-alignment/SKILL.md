---
name: Multizone preaction zone alignment
description: >-
  use this when one white-space hall is too large for a single company-elected
  wet|dry|double-interlock system and you must subdivide into aligned
  suppression / VEWFD / power-isolation / impairment zones (packet optional;
  STS + matrix consumed when present, else ASSUMED and flagged); SI/NI-as-BOD → Stop RFI-variance (comparison-only); foam prohibited;
  mist PRACTICE REFUSED; status register every run — not density×area from
  scratch, not ASD port sizing, not El/El trim, not ≤30 s delivery proof, not
  releasing C&E rewrite.
---

# Multizone preaction zone alignment


Roster language, job names, and local source-file paths were removed when this method was copied into the content pack. Section numbers and the calculation method are unchanged. Verify judgment calls with the engineer of record.

**Intake rule (the engineer of record, 2026-10-07 — overrides any older gate wording below):** The assignment packet is optional and never a gate. Start from exactly what is given. A missing packet, a missing upstream result (STS token, matrix row, occupancy fork, density, C&E, etc.), or a missing input blank is **not** a Stop: run the upstream Skill if practical, otherwise fill the gap with a stated **ASSUMED** value (the value used + why), flag it in the output and the status register, and continue. ASSUMED is not verified. "Never invent" / "refuse invent" rules on project numbers mean do not *silently* invent: label the number ASSUMED; never present an ASSUMED value as a cited code or table value; never freeze a vendor SKU. **Company scope locks stay hard Stops and are not softened by this rule:** wet / dry / double-interlock preaction only; foam prohibited; clean agent not done (hand-away); water mist `PRACTICE REFUSED`; single-interlock / non-interlock / other preaction never the elected system (SI/NI-as-BOD → Stop + `RFI-variance`, comparison-only). Cite section and edition, use `_calc/run.py` for governed math, design to the most-stringent 3-layer basis; Verify with the engineer of record.

Reusable DC fire-protection recipe. **This Skill subdivides one oversized white-space hall into independent, cross-system-aligned suppression zones** after `suppression-technology-selection` pinned company-elected `wet` | `dry` | `double-interlock`. It elects **zone count / boundaries / per-zone hardware unit / 1:1 alignment** (suppression ↔ VEWFD ↔ power-isolation ↔ impairment blast-radius), driven by **FM ≤30 s water delivery** (when a dry/DI clock applies) and **impairment continuity**. It does **not** invent an NFPA 13 maximum-system-area section number, re-run density×area, size ASD ports, write El/El trim, **prove** the delivery clock, or rewrite the releasing C&E.

**Core thesis:** at hall scale the binding drivers are usually **insurer delivery time** and **operational blast-radius**, not a code-floor area cap. The basic FM unit is already a **dedicated, sectioned preaction system** (sectional valve + **2-in test line** downstream of the preaction valve). This Skill multiplies that unit until each zone can be proved ≤30 s **and** a single trip/ITM event does not strand the whole hall — then forces **1:1 alignment** so one VEWFD pre-alarm trips one valve and de-energizes one isolation zone.

**Design practice (lede):** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PARAMETER** (delivery gate, blast-radius, alignment, per-zone hardware, concurrency hand-off). Report **Δ vs NFPA 13-2025** (directional on system-area / delivery clocks when the floor is unpinned). Cite **section AND edition**. Show-and-verify arithmetic. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Company fence: controlling BOD = **`wet` | `dry` | `double-interlock`** only; SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Company-typical white-space preaction multizone path = **DI**; wet allowed for **blast-radius-only** zoning (no FM ≤30 s pretension). Upstream (packet optional; gaps → `ASSUMED`): completed `dc-fp-assignment-packet` + STS company election token + matrix water-delivery / interlock / VEWFD / zoning-relevant rows when dual-carrier. **Do not invent NFPA 13 max-system-area section numbers.** Caller-path-only. **NO PLACEHOLDER.** Generic — do **not** copy NE ~4 × 12,500 ft² SI or Arvada ~5 × 9,600 ft² DI halls onto another job.

**Corpus honesty (training ground — never hall defaults):**

| Spine | What it shows | Honesty |
|---|---|---|
| NE hyperscale multizone (`hyperscale-datahall-multizone-preaction-zoning-ne`) | ~50,000 ft² → ~4 × ~12,500 ft²; **SI** primary | **`[SYN]` comparison-only / historical training** — never company BOD; never copy as default N or ft² |
| Arvada whitespace WDT/zoning outline | ~48,000 ft²; **5 DI zones × ~9,600**; WDT ≤30 s volume budget | **`[SYN]` illustrative** company-path shape only — never default N or ft²; delivery **proof** owned by water-delivery |
| FM DS 5-32 / DS 2-0 / VEWFD / power notes | Dedicated unit; ≤30 s; 2-in test; no cross-zone; VEWFD zone count; PI §2.8; DS 2-0 ~10–12k experience | **mined** doctrine — experience band is overlay `[V]`, **not** a code max-area invent |

Write the zone-alignment package **only** to the path the **caller** names. Do not write into KNOWLEDGE_BASE, EXERCISES, `_pruner`, `_surveyor`, `_engineer`, ARCHIVE, or the root PDF queue. Look up shop codebook notes **by title**.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill elects zones, not system family)

This Skill may emit a **controlling** multizone alignment only against an elected company system family:

1. **Wet-pipe sprinkler** — zoning still useful for **impairment / ITM blast-radius**; FM ≤30 s is a **preaction/dry delivery gate** — do **not** pretension a wet-only hall as meeting FM ≤30 s.
2. **Dry-pipe sprinkler** — owes a delivery clock; zone count / volume-cut interacts with water-delivery.
3. **Double-interlock preaction** — **company-typical white-space multizone path**; controlling when STS elected DI.

Comparison-only (never elected here; never the controlling zoning BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**This Skill does not elect wet | dry | DI.** It **consumes** the STS company election token and zoning-relevant rows from `most-stringent-basis-matrix` (plus the completed `dc-fp-assignment-packet`). Controlling BOD = `wet` | `dry` | `double-interlock` only. Do **not** invent DI when STS elected wet. Do **not** silent-swap SI→DI.

If the caller presents SI, NI, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling zone-alignment package as if SI/NI were company-elected.
6. Do **not** copy the NE SI ~4 × 12,500 hall as a reusable default.
7. SI/NI (including FM “no interlock-type qualifier” on ≤30 s, and AXA SI preference / FM wet→NI→SI→DI ranking) may appear only as **`comparison-only`** evidence — never the controlling Drivers A–D path.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Emit controlling zone alignment (wet: blast-radius path; dry/DI: delivery + blast-radius) |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not design foam zoning |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only | Not this Skill |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist does **not** authorize mist election or design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Zone count N / boundaries / per-zone FM hardware unit | System-family election (STS) |
| 1:1 suppression ↔ VEWFD ↔ power-isolation alignment | Density × area `_calc` (consume named demand row) |
| Drivers A–D + honesty fence on code max-area | ≤30 s / 60 s **delivery proof** (water-delivery owns) |
| Tables A+B + own-zone SOO spine | Authoritative releasing C&E / SOO rewrite |
| Status register + `[SYN]`/`[V]` | ASD port count / transport-time math |
| Reciprocal handshakes (water-delivery / C&E / PI / density / ASD / El-El / nitrogen / pump / ITM) | El/El trim catalog / SKU schedule |
| Consume packet + STS wet\|dry\|DI + matrix rows | Nitrogen C-factor / 98 % / generator SKU |
| DS 2-0 ~10–12k ft² experience as **overlay `[V]`** | Inventing NFPA 13 max-area § / concurrent-zone pump gpm |
| | Treating in-hall zones as 2-hr fire areas |
| | Copying NE SI 4×12.5k or Arvada DI 5×~9.6k as defaults |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** each of Drivers A–D, **(c)** the elected N / boundary set, **(d)** each Table A ≤30 s status cell, and **(e)** the concurrency hand-off:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling wet\|dry\|DI + edition + claim supported by **mined** sheet / caller geometry / named peer proof method already closed |
| `provisional` | Directionally pinned; edition or delivery-proof hole flagged `[V]` — **never silent `grounded` on ≤30 s** |
| `unresolved` | STS / matrix / hall area / carrier / AHJ edition / containment geometry not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, NE SI spine, FM ranking / “no interlock qualifier” — never controlling BOD |
| `handoff` | Peer owns next action (water-delivery proves ≤30 s; C&E Boolean; PI Fig D.1; density `_calc`; pump concurrency; ASD ports; El/El trim; N₂ medium/C) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |

**Unearned ≤30 s claim → never `grounded`.** Keep Table A ≤30 s column at `handoff` / `unresolved` / `provisional` until `dry-preaction-water-delivery-screen` names a proved method. SI evidence → `comparison-only`. Invented N / ft² / 4×12,500 → Stop or `[SYN]` — never hall default.

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent a zone count, hall ft², 2×2 grid, or concurrent-zone pump demand. Do not treat SI/NI as company BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

| Input | Required | Notes |
|---|---|---|
| `dc-fp-assignment-packet` (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). |
| **Consumed `most-stringent-basis-matrix` water-delivery / interlock / VEWFD / zoning rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling delivery / interlock / VEWFD row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap FM **30 s** onto an AXA-only job. |
| **Hall white-space floor area** | **yes** | Single hall (or named sub-area). Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do **not** default to 50,000 / 48,000 / 12,500 / 9,600. |
| **System type per hall / zone (controlling)** | **yes** | Already pinned: `wet` / `dry` / `double-interlock`. This Skill does **not** pick the type. Wet with no dry/DI clock → blast-radius zoning only; say so. |
| **Carrier** | **yes** | `FM DS 5-32 controlling` / dual / AXA / other named / explicit `n/a`. Never silent-swap FM **30 s** onto an AXA-only job. |
| **AHJ-enforced NFPA 13 edition** | **yes** to cite | Delta baseline = **NFPA 13-2025**. Unamended **2024 I-Codes** → **13-2022**. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` edition (value + why), flagged; any "code forces N zones" claim on it is ASSUMED-based. |
| **Containment / cell geometry** | **yes** (or explicit `[V]`) | Aisle-containment cell lines or equivalent zone-boundary geometry. Boundaries must not straddle pods. Missing geometry → flag `[V]` / `unresolved` and ask; do not invent a 2×2 grid. |
| **Owner blast-radius / zone-split posture** | **yes** (may be `none`) | Project-issued fraction out-of-service target, **or** explicit `empty`. NDA → structure-only; may raise, never lower. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional (do not block; flag `[V]` / `handoff` / `comparison-only`): ceiling height vs FM **30 ft** cap; hose + duration already named; simultaneous-zone concurrency posture for pump hand-off; number of proposed risers; SI comparison evidence (NE spine / FM ranking) — never controlling; DS 2-0 ~10–12k experience band as overlay.

**Do not invent** an NFPA 13 §number for maximum system area, a pipe-fill model that "proves" 30 s, a zone count from habit, a concurrent-zone pump demand, or PLACEHOLDER text. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `dc-fp-assignment-packet` | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token**; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI |
| `most-stringent-basis-matrix` | Water-delivery / interlock / VEWFD / zoning-relevant rows; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA clock swap |
| `dry-preaction-water-delivery-screen` | Named proof method / proved vs unproved ≤30 s when present | Invent a V/Q 30 s closeout here |
| `preaction-releasing-c-and-e-soo` | Own-zone / no-cross-zone Boolean context | Rewrite full C&E matrix |
| `power-isolation-disconnect-control` | 1:1 PI zone tags / Fig D.1 context when present | Own NEC 645 / Test-Mode architecture here |
| `density-area-dry-increase` | Named demand row (wet 2,500 vs dry 3,500) | Re-run `_calc` |
| `asd-vewfd-return-sampling` | 1:1 VEWFD zone tags when present | Size ASD ports / transport here |
| `preaction-el-el-trim-election` | DI trim family when present | Write trim SKU catalog |
| `nitrogen-inerting-and-c-factor-gate` | Medium (N₂ generator + compressor) / C-factor election (C=100 design; 120 comparison-only) when dry/DI | Own fill clock or C-factor here |
| `pump-envelope` | Concurrency flow when present | Freeze concurrent-zone gpm from habit |
| `itm-design-for-testability` | 2-in test-line testability into CD when present | Own ITM interval tables here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling delivery / interlock / VEWFD rows are missing when required → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

### 2.2 Reciprocal handshakes (required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `dry-preaction-water-delivery-screen` | **Prove** ≤30 s / 60 s; elect QOD vs volume-cut vs extra risers | Elect **provisional N** / boundaries; mark ≤30 s status `handoff` / `unresolved` / `proved (cite method)` |
| `preaction-releasing-c-and-e-soo` | Controlling DI Boolean; **no cross-zone** smoke water trip; full SOO | Zone tags + **own-zone spine** only |
| `power-isolation-disconnect-control` | NEC 645 / Fig D.1 / Test-Mode / auto-manual isolation | **1:1 PI zone tags** on Tables A+B |
| `density-area-dry-increase` | `qd` / dry **3,500** vs wet **2,500** `_calc` | **Name** consumed demand row; no `_calc` |
| `pump-envelope` | Concurrent-zone **supply** flow / tank | Name concurrency assumption `[V]`/`[SYN]`; never freeze gpm |
| `asd-vewfd-return-sampling` | Port count / transport ≤60 s | **1:1 VEWFD zone tags** |
| `preaction-el-el-trim-election` | DI trim family / collision | Hand-off row only |
| `nitrogen-inerting-and-c-factor-gate` | Medium / C / 30-min **fill** | Zone map context only; fill ≠ delivery |
| `itm-design-for-testability` | 2-in test / drain / supervision **testability** into CD | **Schedule** the 2-in line per zone (FM hardware unit) |
| `suppression-technology-selection` / `most-stringent-basis-matrix` / `dc-fp-assignment-packet` | Family + matrix + packet | **Consume only** |
| `fire-area-compartmentation-schedule` | DP-to-DP / hall-to-hall fire barriers | In-hall zones are **not** fire areas |

Emit rows as needed:

- `HAND OFF — dry-preaction-water-delivery-screen: prove ≤30 s / 60 s (QOD vs volume-cut vs extra risers). This Skill elected provisional N / boundaries only; ≤30 s column is handoff/unresolved until proved.`
- `HAND OFF — preaction-releasing-c-and-e-soo: full Boolean / abort / exhaust; own-zone-only spine named here. Do not rewrite the matrix.`
- `HAND OFF — power-isolation-disconnect-control: Fig D.1 / Test-Mode / NEC 645. This Skill only scheduled 1:1 PI tags.`
- `HAND OFF — density-area-dry-increase: consume named demand row (DI → dry 3500; wet → wet row). No _calc here.`
- `HAND OFF — pump-envelope: concurrent-zone supply. Concurrency assumption is [V]/[SYN] provisional only.`
- `HAND OFF — asd-vewfd-return-sampling: ports / transport. 1:1 VEWFD tags only here.`
- `HAND OFF — preaction-el-el-trim-election: DI trim family.`
- `HAND OFF — nitrogen-inerting-and-c-factor-gate: medium / C / fill (fill ≠ delivery).`
- `HAND OFF — itm-design-for-testability: 2-in test-line testability into CD.`
- `HAND OFF — fire-area-compartmentation-schedule: only if architecture claims fire-rated separation between in-hall zones (unusual).`

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest)

Resolve **enforced** vs **latest** before electing a count. Format every citation `instrument-edition §section`.

| Standard | Role | Shop-pinned editions |
|---|---|---|
| **NFPA 13** | Code-floor system-area / dry-volume / delivery clocks | Delta = **13-2025**. Unamended **2024 I-Codes** enforce **13-2022**. **Licensed max-system-area / single-interlock volume treatment not inventable here.** If unpinned in the shop codebook → carry as **`[V]` directional** — **do not invent a section number**. |
| **FM DS 5-32** | DC white-space **≤30 s** to the **single most remote sprinkler**, all preaction arrangements; dedicated sectioned unit | **January 2026**, §2.4.3.2.1.2 / .D; Fig **2.4.3.2.1.2.E** (cite **caption**; body cross-ref typo 2.4.**4** in source — do not invent an alternate Fig) |
| **FM DS 2-0** | Install overlay; practical system-size experience **~10,000–12,000 ft²**; generic delivery ladder | **Oct-2021 / Interim Rev Jan-2024**, §2.2.1.11.3 experience — **overlay `[V]`**, **not** a fabricated code max-area |
| **AXA XL** | DI area+N₂ lever; **no 30 s numeric gate** in the shop AXA note | date the *claim* (e.g. Mar-2026 white paper) |
| **NFPA 72** | One releasing-service control unit per suppression zone (consume; do not rewrite Ch.23) | Enforced vs **72-2025** [CODE NFPA 72-2025 §23.11.1, pull 72-06] |

Look up **by title**: *The Design practice*; *Enforced-vs-latest edition resolver and reference pins*; *Data-center sprinkler and preaction design*; *FM DS 5-32 insurer design basis*; *VEWFD detection & releasing for data centers*; *Power isolation and disconnect control*; *Dry-pipe & double-interlock air supply and water delivery*.

Consume the assignment packet (optional) and any BOD **delivery / interlock / VEWFD** rows. Do not rebuild them. Do not retrieve CASE_INDEX. Do not run `_calc`.

**Overlay traps:** (1) Quoting an invented NFPA 13 max-system-area § (e.g. worked-package memory of §4.4 / §8.2.3) is **forbidden** — Absent stays Absent. (2) AXA’s DI lever is **area + N₂**, not a 30 s clock — do not blend. (3) FM “no interlock-type qualifier” on ≤30 s and FM preference ranking are **`comparison-only`** vs company SI fence — not permission to run SI as BOD. (4) DS 2-0 ~10–12k ft² is **experience**, not a code max you stamp as §X.Y.

### 3.2 Confirm prerequisites — consume, don’t redo

`suppression-technology-selection` already pinned company `wet` | `dry` | `double-interlock` (**company election token** required). If type is missing → `ASSUMED` company family (wet | dry | DI only, with why), flagged — not a Stop. If SI/NI presented as BOD → **Stop** (`RFI-variance`). This Skill does **not** pick SI vs DI. Wet with no dry/DI clock → continue for **blast-radius only**; mark Driver A `N/A` / `comparison-only` as applicable — do not claim FM ≤30 s on wet-only.

**Out of scope — emit a hand-off row, do not continue as that Skill:**

- Density × area / dry +30 % / 2,500→3,500 → **density-area-dry-increase**
- Pump envelope / hydrant curve / simultaneous-zone **flow calc** → **pump-envelope** (this Skill may **name** a concurrency assumption as `[V]` / `[SYN]` and hand off)
- ASD port count / transport ≤60 s math → **asd-vewfd-return-sampling**
- Authoritative C&E matrix / SOO → **preaction-releasing-c-and-e-soo**
- Delivery-time **proof** (listed program, ITC water test, QOD election) → **dry-preaction-water-delivery-screen**
- Power-isolation architecture / NEC 645 / Test-Mode → **power-isolation-disconnect-control**
- El/El trim catalog → **preaction-el-el-trim-election**
- Nitrogen medium / C / fill → **nitrogen-inerting-and-c-factor-gate**
- Fire-rated hall-to-hall walls → **fire-area-compartmentation-schedule** (in-hall zones are **not** fire areas)
- ITM interval / 2-in testability CD features → **itm-design-for-testability** (this Skill schedules the 2-in line; ITM writes testability)

### 3.3 Three grounded drivers (and one honesty fence)

Work the drivers separately. Do **not** invent a fourth "code max area" driver with a fabricated section. Status each driver every run.

| Driver | What it forces | Grounding | Status note |
|---|---|---|---|
| **A. FM ≤30 s delivery** | Smaller downstream pipe volume → faster fill after valve trip; zone area is an **output of delivery arithmetic**, not a habit | FM DS 5-32 **§2.4.3.2.1.2.D** — ≤30 s to the **single most remote sprinkler**, **no interlock-type qualifier** on the sheet. Distinct from NFPA 13's **60 s to ITC** / calculated multi-head tables. Applies when dry/DI (or wet companion with a dry clock) and FM controls. | Wet-only → N/A for this gate. Unearned proof → never `grounded`. SI clock facts → `comparison-only` |
| **B. Impairment / trip blast-radius** | One valve trip, impairment, or ITM event must not strand the whole hall | FM availability doctrine (§2.4.1.1/.2 order of preference — ranking itself is `comparison-only` under company DI BOD). Owner may set a max out-of-service fraction. | Always live for wet\|dry\|DI zoning |
| **C. Cross-system alignment** | Zone boundaries on containment-cell lines; **1:1** suppression ↔ VEWFD ↔ power-isolation; one RCU per suppression zone | VEWFD "number of FP systems/zones"; power isolation "isolate as locally as possible… capability to depower an entire room" (§2.8); releasing: one FACP/RCU per preaction system. | Geometry missing → `[V]` / `unresolved` |
| **D. Code-floor max system area** | May or may not force further split | **Honesty fence:** do **not** invent NFPA 13 section numbers. If the shop codebook has no pinned max-area / single-interlock volume rule, write **`[V] code-floor area rule unpinned`** and treat subdivision as **insurer/owner-driven**. Never stamp "§X.Y permits one 52,000 ft² system" from memory as corpus. | Absent § → omit or `[V]`; never invent |

**Driver A physics (restamp 2026-10-09 — what the zone-volume screen may and may not say):**
- **Delivery = trip time + transit time** (Nam, FM Global, *IAFSS FSS-9* 2008; KB *Dry-pipe and DI air supply and water delivery* Run-652). The **60·V/Q fill screen is not a transit model** — trapped air in closed branches means water reaches the open head long before the zone is full; on Nam's FM cases 60·V/Q over-predicts transit **≈2–5×**. A zone that "fails" 60·V/Q is **unproven, not failed**; one that "passes" is not proven either.
- **Configuration before volume:** center feed < center-end < side-end; short feed main; riser at the zone centroid. Split the zone only after the feed is fixed.
- **Accelerator on DI zones:** on a one-head FM criterion the trip term alone can consume the budget above ~400 gal at 15 psig without an accelerator (Arvada retest `[SYN]` screen). Where Viking EA-1 is used: rate trigger 0.1 psi/s, UL 1486 **≤2,250 gal hard cap**, FM only with VXD / Model F El/El (F_041523 Rev 09 Jun 2025); rotary setting vs zone volume is **not printed** → `[V]` Viking TS. Trim election → `preaction-el-el-trim-election`.
- Arvada retest BOD numbers (target 380–420 gal, ceiling 1,200 gal, setting 4 above) are **layout-steering `[SYN]` limits, not defaults or proof**. A listed delivery-time program per zone + witnessed remote test remain required (`dry-preaction-water-delivery-screen` / commissioning).

**Optional overlay (not Driver D):** FM DS 2-0 §2.2.1.11.3 practical **~10,000–12,000 ft²** system-size experience may inform provisional zone sizing toward the water-delivery volume-cut discussion — label **`[V]` experience overlay**, **not** a code max-area invent, **not** a substitute for Driver A proof.

**Zones ≠ fire areas.** In-hall suppression zones are **operational sections**. FM **2-hr DP-to-DP** ratings apply **between separate DP rooms/halls**, not between zones of one hall. Do not claim passive fire-rated separation between PA-Z1 and PA-Z2 unless architecture actually provides it (then that is the compartmentation Skill).

### 3.4 Elect the per-zone hardware unit (the FM sectioned system)

Every zone is a **dedicated** preaction (or wet sectional) system separate from other sprinkler systems:

1. **One preaction valve / riser** per zone (wet: one sectional / riser path per impairment zone).
2. **Sectional isolation** (supervised OS&Y or butterfly) at the riser.
3. **2-in (50 mm) test discharge line downstream of the preaction valve** (FM DS 5-32 Fig **2.4.3.2.1.2.E** — caption number) — ITM / delivery-test path; hand testability to ITM.
4. **One VEWFD detection zone** mapped 1:1 (no cross-zone water trip).
5. **One power-isolation zone** (cabinet/row → zone → whole-room escalation capability retained).
6. **One releasing-service control unit** per suppression zone (sharing costs battery/supervision; do not chain fragile multi-panel release).
7. **Actuator-removal impairment** — audible + visual at the releasing panel (NFPA 13 eff. 1-Jan-2021 practice; cite edition when pinned).

Hydraulic **demand row** is **consumed, not recalculated**. **Consume the BOD / density-area row already named** — do **not** default to an SI-flavored wet-basis 0.2/2,500 example as if it were company DI. Typical forks when the row exists: **wet** → wet remote-area row; **DI / dry** → dry **3,500** via **density-area-dry-increase**; never invent `qd`. Name the consumed row; **hand `_calc` to density-area-dry-increase**.

### 3.5 Derive zone count (most-stringent of the binding drivers)

```
# Conceptual — show substitutions; do NOT invent fill models as 30 s proofs
N_zones >= ceil(A_hall / A_max_from_delivery_screen) # Driver A — only after dry-preaction-water-delivery-screen
N_zones >= ceil(1 / f_max_out_of_service) # Driver B — owner/insurer blast-radius
N_zones = tile(containment_cells) # Driver C — geometry must tile without straddling
# Optional overlay only — NOT a code max invent:
# N_zones >= ceil(A_hall / A_experience_DS2_0) # ~10–12k [V] experience; never stamp as § max-area
```

**Rules:**

1. **Driver A does not mint a 30 s claim.** If the caller has no named proof method / listed program / measured ITC plan, write the delivery ceiling as **`[V] pending dry-preaction-water-delivery-screen`** with status `handoff` / `unresolved` and elect a **provisional** count from Drivers B+C (and optional DS 2-0 experience overlay) only — never "passes ≤30 s because V/Q ≈ 12 s" as a stamped proof. Synthetic fill screens in worked packages are **illustrative `[SYN]`**, not Skill outputs.
2. **Driver B** — show the out-of-service fraction: `A_zone / A_hall`. Prefer the smallest fraction the owner/insurer will buy. NDA owner → structure-only column.
3. **Driver C** — boundaries on **whole** aisle-containment cells. No pod straddles two preaction systems. Unequal zones are OK if geometry demands it; equal rectangles are not a code requirement.
4. **Take the most stringent (largest N / smallest A_zone)** among drivers that actually apply. Do not average.
5. **Code-floor area** — if unpinned, **omit** fabricated § cites. If a licensed primary later pins a max area, re-test whether code exceeds the insurer/owner union (**code can raise N further**).
6. **Do not default** to NE ~4 × 12,500 or Arvada ~5 × 9,600. Both are `[SYN]` only. Require caller geometry.

**Simultaneous-operating-zone assumption** for pump/tank: sprinkler **density** is still one zone's remote area; **supply** may need a concurrency rule. Corpus often has **no** multi-zone concurrency number → carry **`[V]` / `[SYN] 1-zone concurrent as provisional`** and **hand off to pump-envelope**. Do not freeze 1,500 gpm (or any habit gpm) from memory.

Status the elected N: `provisional` until Driver A proof closes when FM dry/DI applies; `grounded` only when geometry + drivers that apply are pinned and any ≤30 s claim cites a named water-delivery proof method.

### 3.6 Emit the cross-system alignment schedule

Minimum tables:

**Table A — Suppression-zone master schedule**

| Col | Content |
|---|---|
| Tag | PA-Z1…Zn |
| Floor area | ft² (**caller** geometry only) |
| System type | company-elected wet \| dry \| DI |
| Preaction valve / riser | by function (size may be `[SYN]` until hydraulics) |
| Sectional isolation | supervised |
| 2-in test line | downstream of PA valve (wet sectional path: say N/A or alternate ITM path) |
| Aligned VEWFD zone | 1:1 tag |
| Aligned PI zone | 1:1 tag |
| RCU | one per zone |
| Demand row named | consume BOD; hand `_calc` |
| ≤30 s status | `handoff` / `unresolved` / `provisional` / `proved (cite method)` — **never unearned `grounded`** |

**Table B — Cross-system alignment**

| Suppression | VEWFD | Power-isolation | Containment cells | Notes |
|---|---|---|---|---|
| PA-Zn | VEWFD-Zn | PI-Zn | whole pods only | no cross-zone water trip |

**Zoning SOO spine (hand the full matrix):** each event acts **only on its own zone**. L2 pre-alarm trips **that** zone's valve only; other zones stay armed and dry. Impairment: open **that** zone's **physical** release disconnect → other zones remain in service. Full Boolean / abort / exhaust rules → **preaction-releasing-c-and-e-soo**. Full Fig D.1 / Test-Mode → **power-isolation-disconnect-control**.

### 3.7 Show-and-verify (this Skill's math — not delivery proof, not `_calc`)

```
A_hall = sum(A_zone_i)
f_oos = A_zone / A_hall # impairment blast-radius
# Example check ONLY when caller supplies numbers — never as defaults:
# (caller) A_hall / N = A_zone; f_oos = A_zone / A_hall
# demand: consume BOD named row; DI → dry 3500 via density-area; wet → wet row
# NEVER invent 50000/4=12500 or 0.2/2500+250→750 as company defaults
```

Do **not** emit a V_pipe / Q_fill "proof" of ≤30 s. That arithmetic, if used at all, is **`[SYN]` screening** and must be superseded by **dry-preaction-water-delivery-screen**.

### 3.8 Flags and status discipline

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented hall geometry, fill-model inputs, valve size placeholders, concurrent-zone assumptions, NE/Arvada example numbers used illustratively |
| **`[V]`** | Unpinned NFPA 13 max-area / SI volume treatment, AHJ edition, owner blast-radius fraction, delivery proof method, concurrency rule, DS 2-0 experience overlay |
| Status tokens | `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` on gate, drivers, N, ≤30 s column, concurrency |
| Grounded sheet numbers | FM ≤30 s (§2.4.3.2.1.2.D), dedicated sectioned unit + 2-in test line (Fig **2.4.3.2.1.2.E** caption), no cross-zone water trip, wet 2,500 / dry 3,500 demand **names** when already in BOD. Cite **section AND edition**. |

**Do not invent section numbers.** If a max-system-area cite is not in the notes/inputs, omit it or mark `[V]`. **NO PLACEHOLDER.**

---

## 4. Output

A **zone-alignment package**. Write **only** to the caller-named path.

Minimum: Hard-scope gate + status register (gate / Drivers A–D / elected N / Table A ≤30 s / concurrency); edition-pin block (name the max-area Absent hole); inputs echoed including **packet + STS company election token + matrix** rows; Drivers A–D with honesty fence on code area + optional DS 2-0 experience overlay `[V]`; elected N and boundary rules from **caller geometry**; per-zone FM hardware unit; Tables A+B; named demand row + handoffs; provisional concurrency note; reciprocal handshake rows; show-and-verify; `[SYN]`/`[V]` register; directional Δ vs NFPA 13-2025; corpus honesty that NE SI 4×12.5k and Arvada DI 5×~9.6k were **not** copied as defaults.

Do **not** emit: density×area `_calc` transcript, ASD port math, El/El trim catalog, full releasing C&E matrix, delivery-time closeout claiming 30 s without a named proof method, fire-barrier schedule between in-hall zones, pump nameplate, PLACEHOLDER text, or invented NFPA 13 max-area § numbers.

---

## 5. Stop

**2026-10-07 intake rule:** any item below that is a missing packet, a missing upstream result, or a missing input blank is **not** a Stop — proceed with a stated `ASSUMED` value (value + why), flagged in the output and status register. Only company scope-lock items (SI/NI-as-BOD → `RFI-variance`, foam, water mist `PRACTICE REFUSED`, clean agent as company BOD) and wrong-Skill / out-of-scope routing remain hard Stops.

1. Assignment packet missing → not a Stop (packet optional); proceed and flag `ASSUMED`. 2. STS company election token missing / `unresolved`, or system type missing. 3. SI/NI (or other prohibited preaction) presented as **BOD** → `RFI-variance`. 4. Foam BOD. 5. Mist design request (`PRACTICE REFUSED` / `RFI-variance`). 6. Dual-carrier controlling water-delivery / interlock / VEWFD matrix rows missing when required → `unresolved`. 7. Missing hall area or containment geometry treated as inventable. 8. Unpinned carrier. 9. Unpinned AHJ edition when claiming code forces N zones. 10. Caller demands an **invented NFPA 13 max-system-area section**. 11. Caller asks to **prove ≤30 s** inside this Skill without handing to `dry-preaction-water-delivery-screen`, or to mark unearned ≤30 s `grounded`. 12. Caller asks to rewrite the full releasing C&E, size ASD ports, run density×area `_calc`, elect El/El trim, own nitrogen C/fill, freeze concurrent-zone pump gpm, or treat in-hall zones as 2-hr fire areas. 13. Caller asks to copy NE ~4 × 12,500 SI or Arvada ~5 × 9,600 as hall defaults. 14. Silent-swap FM **30 s** onto an AXA-only job. 15. NDA owner treated as a numeric blast-radius fraction without structure-only posture. 16. Write into KNOWLEDGE_BASE / EXERCISES / `_pruner` / `_surveyor` / `_engineer` / ARCHIVE / root PDF queue.

---

## 6. Citations (section AND edition — do not invent)

Shop codebook **by title**.

**FM DS 5-32 January 2026 (mined):** §2.4.3.2.1.2 dedicated preaction + sectional valve + 2-in test line / Fig **2.4.3.2.1.2.E** (caption; body typo 2.4.4 noted — cite caption); **§2.4.3.2.1.2.D** ≤30 s to most remote sprinkler; §2.4.3.2.1.3 / .3.2 trip on VEWFD pre-alarm, **no cross-zoned detection**; §2.4.1.1/.2 interlock order / availability (**ranking = `comparison-only`** under company DI BOD); §2.4.3.3.1.1 demand criteria (consume named row).

**FM DS 2-0 Oct-2021/Jan-2024 (mined):** delivery ladder §2.2.1.11.1; system-size experience **~10,000–12,000 ft²** §2.2.1.11.3 — **overlay `[V]`**, not code max-area.

**Power isolation (mined):** §2.8 local→room capability; Fig D.1 consumed via power-isolation Skill.

**VEWFD (mined):** detection layout driven by number of FP systems/zones (§3.3.2.1 class).

**AXA XL Mar-2026 (shop note):** DI **+30 % area AND nitrogen-fill** — **no 30 s numeric gate**; SI preference = `comparison-only`.

**Corpus — comparison / illustrative `[SYN]` only (never hall defaults):**

- NE outline `hyperscale-datahall-multizone-preaction-zoning-ne` — ~50k / **4 × ~12,500** / **SI** primary → **`comparison-only` / historical**.
- Arvada outline `hyperscale-whitespace-hall-tank-vt-vs-hsc-wdt-zoning-amd-n2-bimlod-arvada-co` — ~48k / **5 DI × ~9,600** → company-path **illustrative `[SYN]`** only; WDT proof → water-delivery. Its 2026-10-05 **retest** (Nam trip + transit, EA-1 decay screen) **withdrew** the earlier 60·V/Q "fail ×5" verdict — cite the retest, not the 2026-09-22 package.
- NE **per-zone SI criteria + NE code-floor fence** package (2026-10-05, `corpus-insufficient`/medium): NE enforces **NFPA 13-2010** (153 NAC 1); the ≤30 s criterion could not be proven for 4 × 12,500 ft² — **SI = `comparison-only`**; use only as negative teaching on zone size.

**Absent / honesty:** licensed NFPA 13-2025 **maximum system area** and **single-interlock volume** treatment as stamped primary section numbers; a layout-independent transit method (Nam trip term is held and validates within ≈8 % on choked cases, under-predicts deep-subsonic cases; transit still needs the listed program / test); multi-zone simultaneous-operating-zone supply rule; company-DI-primary worked package that is not `[SYN]`.

---

## 7. Design practice

1. Three-layer, most stringent, **per parameter**. Code may be silent on forcing subdivision; FM **≤30 s** (when dry/DI + FM) and blast-radius usually bind. Report Δ vs **13-2025** without inventing § cites. Company fence: **wet | dry | DI** only; SI/NI Stop + `RFI-variance` / comparison-only; foam prohibited; mist PRACTICE REFUSED. Company-typical white-space preaction multizone = **DI**; wet = blast-radius-only path.
2. Per-parameter, not per-layer. Delivery gate, impairment fraction, and alignment are separate rows — do not MAX "take all FM geometry." Never silent-swap FM 30 s onto AXA-only.
3. Owner may raise (more zones / smaller blast-radius), never lower the insurer delivery gate.
4. Enforced ≠ latest. Unpinned 13-2025 area rules stay `[V]`. **Do not invent NFPA 13 max-system-area section numbers.**
5. Show-and-verify area fractions and named demand arithmetic. Delivery **proof** is another Skill. Demand row: **consume BOD** (DI → dry 3500 via density-area); never invent SI-flavored defaults.
6. Status register every run on gate + Drivers A–D + elected N + ≤30 s column + concurrency: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Unearned ≤30 s → never `grounded`.
7. Upstream (packet optional; gaps → `ASSUMED`): packet + STS company election token + matrix rows. Caller-path-only. **NO PLACEHOLDER.**
8. Honesty. Synthetic fill screens, NE SI 4×12.5k, and Arvada DI 5×~9.6k stay `[SYN]` / comparison or illustrative only. Do not invent NFPA 13 section numbers. Do not mint V/Q 30 s proofs. DS 2-0 ~10–12k = experience overlay `[V]`, not code max.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Wet / dry / DI election (SI/NI comparison-only) | `suppression-technology-selection` |
| Assignment packet intake | `dc-fp-assignment-packet` |
| Dual-carrier BOD matrix | `most-stringent-basis-matrix` |
| Occupancy / HC / OH | occupancy-hazard-fork |
| Density × area `_calc` | `density-area-dry-increase` |
| ≤30 s / 60 s delivery proof, QOD, volume | `dry-preaction-water-delivery-screen` |
| Releasing C&E + SOO | `preaction-releasing-c-and-e-soo` |
| Power isolation / NEC 645 / Test-Mode | `power-isolation-disconnect-control` |
| ASD port / transport sizing | `asd-vewfd-return-sampling` |
| El/El trim catalog | `preaction-el-el-trim-election` |
| N₂ / C-factor / 30-min fill | `nitrogen-inerting-and-c-factor-gate` |
| DP-to-DP fire barriers | `fire-area-compartmentation-schedule` |
| Pump envelope / concurrency flow | `pump-envelope` |
| 2-in testability / ITM intervals | `itm-design-for-testability` |

---

## 9. Runner checklist

1. Hard-scope gate: wet|dry|DI only; SI/NI-as-BOD → Stop `RFI-variance`; foam/mist Stop; wet/no dry clock → blast-radius only (no FM 30 s pretension). Emit status on gate.
2. Check packet (optional) + STS **company election token** + matrix water-delivery/interlock/VEWFD rows; missing → `ASSUMED` (flagged), not a Stop.
3. Confirm hall area, carrier, AHJ edition, containment geometry, owner blast-radius posture; Stop tests. Refuse NE/Arvada defaults.
4. Pin editions; refuse invented 13 max-area § numbers; note DS 2-0 ~10–12k as overlay `[V]` only.
5. Consume packet/BOD/matrix rows; do not rebuild. Require STS company election — not “type pinned including SI.”
6. Work Drivers A–D; honesty fence on code area; status each driver. Optional DS 2-0 experience overlay — not Driver D invent.
7. Elect per-zone hardware unit (valve + sectional + 2-in Fig **2.4.3.2.1.2.E** caption + 1:1 VEWFD/PI/RCU).
8. Derive N from most-stringent binding drivers; boundaries on containment cells; caller geometry only. Status elected N.
9. Emit Tables A+B; ≤30 s column never unearned `grounded`; hand delivery proof, C&E, PI, density, ASD, El-El, nitrogen, pump, ITM.
10. Name concurrency `[V]`/`[SYN]`; hand pump-envelope — never freeze habit gpm.
11. Show-and-verify area fractions + named demand (consume BOD; DI→dry 3500); Δ vs 13-2025 directional.
12. Reciprocal handshakes named. Corpus honesty: NE SI / Arvada DI both `[SYN]` only.
13. No PLACEHOLDER; no invent § / 30 s proof / zone count / SI-as-BOD.
14. Write **only** to the caller-named path.
