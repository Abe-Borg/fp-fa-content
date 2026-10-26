---
name: Nitrogen inerting and C-factor gate
description: >-
 use this when company-elected dry or double-interlock is pinned (STS dry|DI +
 matrix nitrogen/C rows consumed when present, else ASSUMED and flagged;
 packet optional) and you must elect
 inert vs air, generator vs cylinders (ECS default family; two-number
 fill/maintenance check), remote-branch purity sampling, and emit calc C=100
 always (C=120 comparison-only); SI/NI-as-BOD → Stop RFI-variance
 (comparison-only); foam prohibited; mist PRACTICE REFUSED; status register
 every run — not ITM interval tables, not El/El trim catalog, not SprinkFDT,
 not occupancy or density×area, not QOD/30 s delivery proof.
---
# Nitrogen inerting and C-factor gate

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **This Skill is the HARDWARE + C-FACTOR GATE** that makes nitrogen real on a dry or double-interlock system that **suppression-technology-selection has already pinned** as company `dry` | `double-interlock`. It elects **inert vs air**, **generator vs cylinders** (liquid is forbidden; **ECS** is the default generator family — design-practice setting), **remote-branch purity sampling**, and **emits calc C=100 — always** (design-practice setting: use C=100, do not chase C=120; C=120 appears only as a `comparison-only` line). It then **hands the 3 yr → 10 yr trip-test INTERVAL LEVER** to **itm-design-for-testability**. It does **not** own that lever’s schedule. It does **not** elect wet/dry/DI. It does **not** prove ≤30 s / ≤60 s water delivery (fill ≠ delivery).

**Core thesis:** **Calc C = 100 — always** on the company dry / DI sprinkler pipe this gate covers (**design-practice setting: use C=100; don't chase C=120**). Nitrogen is a **corrosion and reliability decision, not a hydraulic credit.** The C=120 allowance exists in other layers (FM DS 2-0 Table 2.2.1.3.3 "dry/preaction black steel + inert gas 120"; NFPA 13-2022 per Hopkins; UFC 3-600-01 §9-6/§9-7), but this Skill prints it only as a **`comparison-only`** line with the **≈29 % friction understatement** shown (FM DS 3-0 Eq 15: `(100/120)^1.85 ≈ 0.714`). The evidence backs the dial: independent 8-week testing failed 98 % system-wide under every purge method sold (best **97.3 %**; branches in the **80s–low 90s**) while purge-valve ports read 98 %+. Remote purge + branch-end sampling stay mandatory because they decide whether the pipe is actually inerted against **corrosion** — not to earn C. **Default generator family = ECS** (AdvancedIQ; design-practice setting — ECS, not Potter), specified by **duty + listed function** with OEM values `confirm at submittal`; Potter IntelliGen and UFS NITROGEN-PAC are cited examples / alternates, never a frozen hall SKU. Size any family on **two numbers** (maintenance volume ≥ Σ connected gallons; 30-min compressor / bypass fill ≥ largest single system). FM DS 2-81 rewards systems **originally installed with nitrogen** (full-flow **3 yr → 10 yr**; black-steel obstruction exemption) — a **CD decision**, not a later O&M conversion — and only when FM grants on company-elected **dry/DI**.

**Design practice (lede):** three-layer basis (code floor × insurer sheet × owner standard), **most-stringent union PER PARAMETER**, applied separately to **medium**, **source**, **sample locations**, **C-factor**, and **ITM-lever eligibility**. Delta vs **NFPA 13-2025** (C-factor / dry-pipe air vs N₂ / corrosion — directional `[V]` where unpinned). Cite **section AND edition**. Show-and-verify math. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Company fence: controlling BOD for this gate = **`dry` | `double-interlock`** only (wet → N/A); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet + STS `dry`|`double-interlock` + matrix nitrogen/C/inert-medium rows when dual-carrier. Caller-path-only. **NO PLACEHOLDER.** If notes conflict, **most-stringent wins and both sources stay visible**.

**Honesty — worked packages now exist (method only, `[SYN]`).** Held 2026-10-05 Engineer packages: **a prior layout** DI hall two-number check (``: largest zone 549.4 gal / riser-room Σ 1,442.2 gal; ECS AG-2000 800 @ 40 psig / 2,000 total passes; UFS NGM-5 + CTA-30 1,350 / 3,000 passes as FM-certificate alternate; fill 549.4 × 40 / (7.48 × 14.7 × 30) = 6.66 SCFM; C = 100); **a prior layout (West Des Moines IA) dock** dry-pipe generator election (``: 244.6 gal; FM DS 2-1 §2.2.1.12 fork → N₂ for life + black steel; ECS AG-675 235 gal @ 40 psi **fails** fill by 9.6 gal — a smaller ECS unit is not automatically adequate; C = 100); **C-Aire / N2Blast** feed-air packages (`worked-ac-caire-quickfill-231`, `worked-ad-caire-mid-232`, `worked-ae-beecher-cs-233`: **tank gallons ≠ system gallons**; Quick-Fill 635 is quick-fill only, not supervisory maintenance). Two preaction CD sets emit a `05_detection-releasing` supervisory-air / corrosion-control sheet — the **home for this output**. **Do not copy any package's zone gallons, SKUs, purity %, scfm, or supervisory-floor numbers onto a new hall** — re-derive (Adapt). **Do not invent a 98 % acceptance or a 14-day closeout as achieved.**

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill elects medium/C, not system family)

This Skill may emit a **controlling** nitrogen / C-factor gate only against an elected company system family that **owes a dry/DI inerting + C decision**:

1. **Dry-pipe sprinkler**
2. **Double-interlock preaction**

**Wet-pipe → N/A** (not this gate). Do not invent a dry/DI nitrogen package for a wet-only BOD. Wet+N₂ appears in FM DS 2-1 as a named pointer only — not a hall default and not a controlling path here.

Comparison-only (never elected here; never the controlling N₂/C BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**This Skill does not elect wet | dry | DI.** It **consumes** the STS election and nitrogen / C / inert-medium rows from `most-stringent-basis-matrix` (plus the completed the input packet). Controlling company BOD for this gate = **`dry` | `double-interlock`** only.

If the caller presents SI, NI, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute DI (or dry).
5. Do **not** emit a controlling N₂/C gate as if SI/NI were company-elected.
6. Do **not** promise FM nitrogen **3→10** (or any C=120 credit — C=100 always) on an SI-as-BOD path.
7. SI/NI (and AXA SI preference / FM wet→NI→SI→DI ranking) may appear only as **`comparison-only`** evidence — never the controlling Parameter A–E path.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Dry / double-interlock water sprinkler (N₂ + C gate) | Permitted when elected upstream | Emit controlling N₂ / C-factor gate |
| Wet with **no** dry/DI companion | N/A | Mark N/A; do not invent a dry/DI N₂ package |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not design foam inerting / C |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only | Not this Skill |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist does **not** authorize mist election or design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Parameters A–E gate + status register | System-family election (STS) |
| Inert vs air; generator vs cylinders (liquid Stop); ECS default family; two-number fill/maintenance check | Occupancy / HC / OH classification |
| Remote-branch (+ dead-end) purity sampling doctrine | Density × area `calcs` (consumes emitted C) |
| Emitted calc C = **100 always** (120 = comparison-only line + 29 %) | Dual-carrier BOD rebuild (consume matrix) |
| Package checklist (compressor + generator; remote purge; branch samples) | Rewriting `preaction_trip` Boolean (C&E) |
| ITM **eligibility** (`originally installed with nitrogen` y/n) hand-off | ITM **interval** calendar / 3→10 schedule |
| Reciprocal handshakes (ITM / water-delivery / El-El / STS / matrix / C&E) | QOD sizing / ≤30 s / ≤60 s **delivery** proof |
| Consume packet + STS dry\|DI + matrix N₂/C rows | El/El trim catalog / SKU schedule |
| Thin OEM **sampling-location** pointer (not SKU BOD) | SprinkFDT / `calcs` / inventing purity % / scfm / SKU |
| | Pump envelope / hydrant / node-by-node tree |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** each of Parameters A–E, **(c)** the emitted C claim, and **(d)** the ITM eligibility row:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling dry/DI + edition + claim supported by **mined** / opened WHOLE evidence (or measured remote-branch + dead-end ≥98 %) |
| `provisional` | Directionally pinned; PDF-held sheet or edition hole flagged `[V]` — **never silent `grounded`** |
| `unresolved` | STS / matrix N₂·C row / carrier / AHJ edition / pipe material / purity-verification status not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, AXA SI preference, FM ranking — never controlling N₂/C BOD |
| `handoff` | Peer owns next action (ITM 3→10 schedule; QOD×N₂ listing / 30 s proof; El/El medium compat; C&E low-air Boolean; density-area consumes C) |
| `RFI-variance` | SI/NI/foam/mist (or wet-as-N₂-BOD with no dry/DI) presented as BOD |

**Emitted C = 100 on every run** (`grounded` on the 100 emit when inputs are pinned). **C=120 is never emitted and never `grounded`** — it appears only as a `comparison-only` line with the 29 % show-and-verify, even when remote-branch purity is measured ≥98 %. Purge-valve, generator SP, AutoPurge/Quick-Check, INS-PV on-valve, TAV-D/TSV-D riser, cabinet PSV-D readings are **not** evidence the pipe is inerted (corrosion acceptance). SI evidence → `comparison-only`. FM 1035: approvals under **FM 1035 (September 2024)** are certificate-held (UFS PR470042 / PR470065); the **standard text is unheld** → claims about what 1035 tests stay ≤ `provisional` + `[V]`.

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent a nitrogen plant, purity %, scfm, SKU, or 14-day closeout. Do not treat SI/NI as company BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as cited/listed; never a frozen vendor SKU. C=120 is never ASSUMED or emitted — C=100 always (design-practice setting).)*

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `dry` \| `double-interlock` from `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). Wet with no dry/DI → **N/A**. |
| **Consumed `most-stringent-basis-matrix` nitrogen / C / inert-medium rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling N₂ or C row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap FM numbers onto an AXA job. |
| **System type per hall / zone (controlling)** | **yes** | Already pinned: `dry` / `double-interlock`. This Skill does **not** pick SI vs DI. |
| **Pipe material (system-side)** | **yes** | `black steel` / `internally galvanized` / `polymer-enhanced` / other named. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Carrier** | **yes** | `FM DS 2-0 / DS 2-81 controlling` **or** `AXA XL overlay` **or** `UFC 3-600-01 controlling` (plus explicit `n/a` for the others). Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Owner nitrogen / C posture** | **yes** (may be `none`) | Project-issued, **or explicit `empty`**. NDA → structure-only; may raise, never lower. Do not reconstruct a hyperscaler spec from public pages. |
| **AHJ-enforced NFPA 13 edition** | **yes** to cite | Delta baseline = **NFPA 13-2025**. Unamended 2024 I-Codes → **13-2022**. Unpinned AHJ → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Inert vs air election (if already made)** | **yes** (may be `unelected`) | If already `air` on an FM hall with **>20 sprinklers and no regenerative dryer**, that election **fails FM DS 2-0 §2.2.1.10.3**. Status the election. |
| **Nitrogen source preference** | **yes** (may be `unelected`) | `membrane generator` / `cylinders` / `liquid` / `unelected`. **`liquid` → Stop**. |
| **Purity-verification status** | **yes** | `not yet designed` / `specified (branch-end ports + elapsed time + acceptance value)` / `measured at named remote-branch (+ dead-end) ports` / `purge-valve-only (reject)` / `generator-or-vent-port-only (reject)`. A purge-valve, generator, AutoPurge, or riser-vent reading is **not** evidence the system is inerted (corrosion acceptance). Status the verification claim. Purity never changes the emitted C (100). |
| **Calc C currently assumed** | **yes** | **C=100 always** on company dry/DI sprinkler pipe (design-practice setting). If software / owner / insurer has already assumed **120**, **say so in the BOD, correct the design run to 100**, and print 120 only as a `comparison-only` line with the 29 % show-and-verify. |
| **Caller output path** | **yes** | If unnamed, return the gate in the response and stop. Typical CD home: section **`05_detection-releasing`** / supervisory-air / corrosion-control. |

Optional (do not block; flag `[V]` / `handoff` / `comparison-only`; missing → `ASSUMED`): connected Σ gallons and largest-system volume in **gallons** (both needed for the two-number check; 30-minute fill sized on the **compressor** half, **single largest riser**); freeze y/n; number of preaction zones (each still owes its **own AMD** and **own check/backflow**); SI comparison evidence (AXA preference / FM ranking) — never controlling.

Hand-off line (2026-10-22c): largest-system volume (gal) and connected Σ gallons per N₂ generator / riser room come from `sprinkler-system-volume-takeoff` when a segment list exists.

**Do not invent** a system type, a generator scfm, a purity %, a 14-day closeout, an IST purity log, or a hall-default SKU. **Never emit C=120.** *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as cited/listed; never a frozen vendor SKU. C=120 is never ASSUMED or emitted — C=100 always (design-practice setting).)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected dry/DI; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI |
| `most-stringent-basis-matrix` | Nitrogen / C / inert-medium rows; company dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA C swap |
| `preaction-releasing-c-and-e-soo` | Low-air Boolean context; SI line is **comparison-only** | Rewrite C&E; invent SI supervisory defaults |
| `dry-preaction-water-delivery-screen` | Delivery-clock companion when present | Own ≤30/60 s proof or QOD×N₂ listing here |
| `preaction-el-el-trim-election` | Medium-compat / AMD pressure band when present | Write trim SKU catalog here |
| `itm-design-for-testability` | Receives eligibility hand-off | Emit interval table here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling nitrogen / C rows are missing when required → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume `dry` or `double-interlock` (this Skill's scope; never SI/NI) and say why.

### 2.2 Reciprocal handshakes (required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `itm-design-for-testability` | **Interval** schedule (3→10 full-flow; obstruction exemption) when FM grants | **Eligibility** only: `originally installed with nitrogen` y/n on each company dry/DI hall |
| `dry-preaction-water-delivery-screen` | ≤30 s / ≤60 s **delivery** proof; QOD×air/N₂ **listing** compatibility | **30-minute FILL** (compressor half); medium air vs N₂; C emit — **fill ≠ delivery** |
| `preaction-el-el-trim-election` | Valve-room trim family / supervisory pressure band | Medium / AMD / generator-vs-cylinders **compatibility** only |
| `preaction-releasing-c-and-e-soo` | Controlling `preaction_trip` / low-air Boolean; SI line **comparison-only** | Day-one N₂ / medium context; do not rewrite matrix |
| `suppression-technology-selection` | Company wet \| dry \| DI election | Consumes dry/DI; does not re-elect |
| `most-stringent-basis-matrix` | Dual-carrier nitrogen / C / inert rows | Consumes; never silent-swap |
| the input packet | Packet intake (optional) | Consume when present |
| `density-area-dry-increase` (and pump / hydrant / hydraulic-tree) | Consume emitted C; AXA DI +30 % area **AND** N₂ penalty stays density / matrix | Emit C; do not re-run `qd` |

Emit rows as needed:

- `HAND OFF — itm-design-for-testability: nitrogen originally installed = y/n on each dry/DI hall. Hardware + C-factor gate is closed here. Interval-lever schedule is THAT Skill’s.`
- `HAND OFF — dry-preaction-water-delivery-screen: 30/60 delivery proof + QOD×N₂ listing. This Skill owns 30-minute FILL only (compressor half). Fill ≠ delivery.`
- `HAND OFF — preaction-el-el-trim-election: medium / AMD / pressure-band compatibility. Do not write a trim schedule here.`
- `HAND OFF — preaction-releasing-c-and-e-soo: low-air Boolean; SI alarm-only line is comparison-only; DI air is a trip input. Do not rewrite the matrix.`
- Extra: density-area / pump-envelope / hydrant-supply-curve / hydraulic-tree **consume** the C this Skill emits (underground C ≠ sprinkler C).

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest)

| Standard | Role | Shop-pinned editions |
|---|---|---|
| **NFPA 13** | Code floor: air **or** nitrogen permitted; C=120 at 98 % is the **Hopkins 13-2022** characterization | Delta = **13-2025**. Unamended **2024 I-Codes** enforce **13-2022**. NFPA 13 nitrogen C=120 allowance [CODE NFPA 13-2025 §28.2.4.8.1(14) + Table 28.2.4.8.1 (new systems, nitrogen per §8.2.10); NFPA 13-2022 §28.2.4.8.1(13) + Table 28.2.4.8.1 (nitrogen per §8.2.6.9);]. The 98 % figure is not in that clause (Hopkins / §8.2.x, `[V]`). TIA effect on the clause unconfirmed (code edition shows only a general TIA notice) → `[V]`. Company emit stays 100 (design-practice setting). **Do not invent a 13-2025 C-table section.** |
| **NFPA 13 air/N₂ supply trim (2026-10-22)** | Check valve in the pneumatic supply connection, listed shutoff (renewable-disc or ball) on its supply side, approved relief valve between supply and shutoff set ≥10 psi above system pressure and within the maker's limit | [CODE NFPA 13-2025 §8.2.9.2–8.2.9.4, pulls, ; 2022 §8.2.6.4.2 check, §8.2.6.5 relief, §8.2.6.6.4 check per system]. Do not cite 8.2.6.6.4 for 2025 (does not exist). |
| **NFPA 25-2026 C-value upkeep** | Only matters if C=120 is claimed (shop does not): corrosion-mitigation ITM; if not maintained, re-calc at the lower C | [CODE NFPA 25-2026 §4.1.5.1–4.1.5.2, pull 25-08]. Shop C=100 on dry/DI sidesteps this; keep it that way. |
| **NFPA 25** | ITM floor under the lever this Skill **hands off**. FM’s 10-year full-flow is an **FM relaxation**; NFPA 25 floor is **3 years** [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04] | Latest **2026**; 2024 I-Codes typically **25-2023**. **Licensed NFPA 25 not in codebook.** Do not emit the interval table here. NFPA 25 N₂ items apply only where N₂ is used for an increased C value: semiannual ≥98% check [CODE 2023 preaction §13.4.3.2.14 / 2026 §13.4.3.2.15; dry 2023/2026 §13.4.5.2.10] and §14.3.1(16) N₂-loss obstruction trigger (2023+), pull 25-04; at the emitted C of 100 neither is triggered by this Skill. |
| **FM DS 2-0** | C-table, inert-medium default, 30-minute fill, FM Approved generator, pendent-on-preaction galvanized-**or**-nitrogen | **October 2021 / Interim Rev. January 2024** |
| **FM DS 2-81** | Full-flow 3→10 yr; originally-installed obstruction exemption; air tightness 40 psi / 1½ psi / 24 h | Codebook pin **April 2019 / IR October 2021**. Catalog current **IR April 2026** (routing inspect; not copied). Cite codebook until source review restamps; flag Δ `[V]`. Scope fence §1.0: ITM only. |
| **FM DS 3-0** | Hazen-Williams physics for the 29 % swing | Held copy **March 2010** (verify current). Eq 15 is edition-independent physics. |
| **AXA XL** DC white paper | Controlling AXA path that **mandates** N₂ = **DI** (+30 % area **AND** nitrogen-fill). SI preferred = **`comparison-only`** under company fence — may discuss N₂ for corrosion, **cannot** be controlling BOD | **March 2026**, p.8 |
| **DoD UFC 3-600-01** | Controlling **only** on a DoD job: **mandatory** N₂, **≥98 % throughout piping within 14 days**, C=120 permitted (here `comparison-only` — emit 100), **no stand-alone bottles**; continuous venting not permitted | Change **6, 2021**, §9-6 / §9-7. **14-day = spec obligation**, not a Hopkins-supported achievement. |
| **FM Approval Standard 1035** | Defines "FM Approved nitrogen generator" | **Certificate-held:** FM Approvals certificates cite **FM 1035 (September 2024)** — UFS **PR470042** (NGM-5 / 10 / 20 / 30 / 60, granted 15 Sep 2025, UFS-356 Rev 1.00) and **PR470065** (NITROGEN-PAC SC-1L, granted 25 Oct 2024, UFS-612A Rev 1.00). **Standard text unheld** (Sep 2022 copy opened, PDF-held only). ECS / Potter "FM 1035 Approved" = **listing claims** in OEM sheets. Verify any listing at approvalguide.com (surveillance-dependent). |
| **FM DS 2-1** *Corrosion in Automatic Sprinkler Systems* | Corrosion mechanism + N₂ in dry/preaction **and** wet; coupon rates; **does not grant C=120** | **Oct 2016 / IR July 2022**, 21 pp. Official ungated FMDS0201. |

Look up **by title**: *The Design practice*; *Enforced-vs-latest edition resolver*; *Nitrogen inerting and internal corrosion control*; *Dry-pipe & double-interlock air supply and water delivery*; *Fire-protection hydraulics methods*; *ITM basis and design for testability*; *AXA XL insurer design basis*; *DoD UFC 3-600-01 water-based suppression design basis*; Hopkins / Sprinkler Age *Nitrogen Generators for Dry Pipe Systems* (May/June 2024); Potter *Corrosion Inhibition… Using Nitrogen Gas* (corrosion data); ECS *Managing Safety in Nitrogen Inerting Fire Sprinkler Systems* (May 2014); ECS AdvancedIQ IOM **M-1428 Rev 1.12** (AG-675/950/2000/3500) + AG-2000/3500 spec **Rev 6.00**; UFS NGM data sheet **UFS-354 Rev 1.02 (Sep 2025)** + CTA **UFS-352 Rev 1.01 (Jun 2025)**.

**Design-practice settings (live in the design practice charter; not yet written into the corpus codebook):** **C = 100 always** (don't chase 120); **ECS** is the default N₂ generator family (not Potter). Owner / insurer may raise, never lower.

Consume the assignment packet if present (optional). Do not rebuild it. Do not retrieve CASE_INDEX. Do not run `calcs` except `hw` at C=100 when a pipe-friction number is needed, `pipe_volume` (via `sprinkler-system-volume-takeoff`) and `air_fill_scfm` for the 30-minute fill (JSON saved beside the deliverable).

**Combined op (2026-10-23b):** `compressor_n2_sizing` (`systems:[{id,v_gal,p_psig}]`, `t_min`=30). It returns the compressor on the largest single system [CODE NFPA 13-2025 §8.2.7.3] and the N2 generator on the campus connected total [PRACTICE]. It matches the two-number rule. Report both the gauge and abs scfm.

**Owner restore target shorter than 30 min (open item G4).** Code floor is 30 min [CODE NFPA 13-2025 §8.2.7.3]. An owner standard of e.g. 20 min is **more stringent** → size the compressor for the owner time (rerun with `t_min:20`); never relax below 30 min unless code permits. Practice case: 20 min needs 5.45 scfm, so a 5 scfm compressor that passes 30 min fails the owner target. Owner value is an owner ruling, not code; if the owner target is unconfirmed, keep 30 min and flag Verify with the engineer of record / RFI.

**30-minute fill op (2026-10-23, `calcs` ):** step `{"op":"air_fill_scfm","v_gal":<largest single system gal>,"p_psig":<supervisory psig>,"t_min":30}` [restore rule CODE NFPA 13-2025 §8.2.7.3; 2019/2022 §8.2.6.3.2]. Outputs `scfm_gauge_basis` = V·P/(7.48·14.7·T) and `scfm_abs_basis` = V·(P+14.7)/(7.48·14.7·T). **Size on `scfm_abs_basis`** (≈37 % higher at 40 psig) — `Verify with the engineer of record` (conservative; KB/Viking basis is gauge; listed compressor/CTA fill table governs when held). Run it on the **largest single system** only; Σ gallons stays the **generator maintenance** check — do **not** follow corpus core-r4c2's "generator sized on the single largest system" wording; the two-number rule here governs. Do not run SprinkFDT.

**Overlay traps:** (1) NFPA 13 C=120 is pinned at 13-2025 §28.2.4.8.1(14) / 13-2022 §28.2.4.8.1(13) and Table 28.2.4.8.1 ; the 98 % link stays `[V]`; TIA effect unconfirmed, `[V]`. (2) Galvanized dry/preaction C=120 is a **live dispute** (FM Table 2.2.1.3.3 = 120; Potter citing NFPA 13-2013 = 100). **Both sources stay visible. Emitted C = 100 regardless** (design-practice setting). (3) **FM DS 2-1 corrosion success ≠ C=120 grant** — coupon 20×/14× and 98 % chemistry are corrosion results; they do not move the emitted C.

### 3.2 Confirm prerequisites — consume, don’t redo

STS already pinned company `dry` | `double-interlock` (wet → N/A; SI/NI-as-BOD → Stop `RFI-variance`). If type is missing → `ASSUMED` `dry` or `double-interlock` (with why), flagged — not a Stop. `preaction-releasing-c-and-e-soo` owns low-air / LOW AIR ALARM — consume, **do not rewrite**; SI line remains **comparison-only**. `itm-design-for-testability` owns the interval lever — this Skill records **eligibility** (`originally installed with nitrogen` y/n) and hands it over. El/El trim is **preaction-el-el-trim-election** — emit a hand-off row, do not elect family here. Water-delivery owns QOD×N₂ listing and 30/60 proof — this Skill owns **fill**, not delivery.

### 3.3 Three-layer union — five parameters, separately

| Parameter | What you elect | Union rule |
|---|---|---|
| **A. Medium** | inert N₂ vs compressed air | Any layer that **requires** inert wins. FM default **is** inert. UFC **mandates** N₂. AXA **mandates** N₂ **if DI** (controlling). Code **permits** either. AXA SI N₂ discussion = `comparison-only`. |
| **B. Source** | membrane generator vs cylinders; liquid forbidden | Safety ranking + reliability + UFC bottle ban. Liquid is never in the union. |
| **C. Sample locations** | purge valve **remote**; sample ports at **ends of most remote branch lines** (plus at least one dead-end), **not** at the vent or the generator | The 2024 Hopkins test is the evidence. Silent layers still get this, because inerting (corrosion acceptance) is otherwise unverifiable. |
| **D. C-factor** | calc C | **C = 100 always** (design-practice setting = owner-layer floor; the most-stringent numeric). FM / UFC / NFPA 13-2022 C=120 rows = `comparison-only` with 29 %. Galvanized dispute → 100. Status the emit. |
| **E. ITM-lever eligibility** | originally-installed N₂ y/n, **then hand to ITM** | FM grants 3→10 yr **only** where DS 2-81 controls **and** the system was **originally installed with nitrogen** on company-elected **dry/DI**. NFPA 25 floor remains 3 years [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]. Never promise on SI-as-BOD. |

**Do not MAX whole sheets.** An AXA **comparison** SI case may discuss N₂ for corrosion without AXA having mandated it and **without** becoming company BOD. An FM hall that elects air without a regenerative dryer fails parameter A even if the owner is silent.

### 3.4 Parameter A — elect inert vs air

**FM DS 2-0 §2.2.1.10.2:** default is inert. **§2.2.1.10.3:** air is acceptable ONLY when (A) a regenerative air dryer is provided, OR (B) the system feeds a maximum of 20 sprinklers. A data-hall preaction zone is far more than 20 heads → **plain air is off the table unless a regenerative dryer is installed.**

**Three-layer reading:** every layer either **permits, defaults to, rewards, or mandates** nitrogen on the controlling dry/DI path. **The decision to inert is easy and belongs in the BOD.** The C contest is closed by the design-practice setting (**C=100 always**); the live item is **whether 98 % is actually reached at remote branches** — a corrosion / inerting acceptance spec, not a C credit.

If the caller elects air on **FM** with >20 sprinklers: require an **FM Approved air-supply package** **or** a **regenerative dryer** to a pressure dew point **20 °F (11 °C) below** nominal ambient (DS 2-0 App. A, p.158). Record that the **3→10 yr lever was declined**. Calc C is **100** either way. On **UFC** or **AXA DI**, air **fails** → **Stop** unless the caller withdraws that layer. Status Parameter A.

**AXA Mar-2026 p.8 (comparison vs controlling):** SI preferred language and the DI rule (“design area increased by 30%” **AND** “filled with nitrogen”) stay visible. Under company fence, **SI preference = `comparison-only`**. The controlling AXA path that **mandates** N₂ is **DI**. Do not run a controlling N₂/C gate as if SI were company-elected.

**Nitrogen still wins on corrosion.** Potter 12-month coupon study Table 2 (cited as **corrosion data** — Potter is not the generator default): metal-loss reduction **45.4 % / 91.8 % / 78.6 % / 61.6 %**. Cite **Table 2, not the conclusion**. **Galvanized is not the cheap corrosion answer** — black steel lost **less** metal than galvanized in every Potter condition. **FM DS 2-0 §2.2.4.3.2:** pendent heads on preaction **only if** piping is galvanized **OR** nitrogen-inerted. **Take the nitrogen route.**

**FM DS 2-1 (Oct 2016 / IR Jul 2022) — use it; do not confuse it with C=120:**

- Oxygen is the cathodic driver (§3.1).
- **§2.2.1.12.1** dry/preaction **using nitrogen:** pressurize with an **FM Approved nitrogen generator**; black steel acceptable **if nitrogen will be used throughout the life of the system**, else galvanized or polymer-enhanced.
- **§2.2.1.12.2** not using nitrogen: galvanized or polymer-enhanced (black steel only with FM Approved vacuum).
- **§2.2.1.4 / §2.2.1.13.B:** do **not** install internally galvanized steel in a **wet** system (including wet+N₂). IR 2022 added wet-pipe nitrogen (§2.2.1.13, §3.3) and polymer-enhanced pipe — **named pointer only**; this Skill remains **dry/DI**.
- **Coupon rates (mined):** dry/preaction supervisory — carbon steel with **air corrodes 20× faster** than with nitrogen (§3.2 p.8); wet N₂ purge — carbon steel with air corrodes **up to 14× faster** than N₂-purged (§3.3 p.8). Sheet’s own work used **98 % N₂**; **<98 % (e.g. 95 %) tracks toward air rates** (§3.3 p.10).
- **★★ DS 2-1 does NOT grant Hazen-Williams C=120.** Corrosion mitigation at ≥98 % is a corrosion result. Practice is **C=100 always**.

### 3.5 Parameter B — elect generator vs cylinders (liquid forbidden)

The riser room is an occupied indoor space. **OSHA: below 19.5 % O₂ is oxygen-deficient (29 CFR 1910.134(b)).**

| Source | ECS rating | This Skill |
|---|---|---|
| **Liquid nitrogen dewar** | **Very High — “should NEVER be used”** | **Forbidden. Stop.** 2 gal LN₂ depletes a 250 ft² × 10 ft room. Cryogenic contact embrittles sprinkler steel. |
| **High-pressure cylinder** | **Moderate** | Permitted only if **unavoidable** (temporary / small remote) **and** UFC does not control. 1 Type A cylinder (250 scf) depletes the same room. |
| **Nitrogen generator (membrane)** | **Lowest** | **The DC answer.** Separates ambient air; no imported-N₂ storage vessel. Same conclusion FM reaches from reliability (DS 2-0 §2.2.1.10.5). |

**Scale check:** **1 gal LN₂ → 93 ft³ of gas**; a **60-gal dewar → >5,500 ft³**.

**UFC overlay:** **no stand-alone N₂ bottles**. Specify the generator **by duty + listed function** (FM 1035 where claimed / certified; membrane; integral or separate compressor with bypass for the NFPA 13 30-minute fill [CODE NFPA 13-2025 §8.2.7.3; 2019/2022 §8.2.6.3.2; 2007 §7.2.6.2.2; design-practice-notes-link--air-n2-supply-2007-2025 ]; maintenance capacity ≥ Σ connected gallons; supervisory alarms to FACP/BMS), never by a hall-default model. OEM capacities are **`confirm at submittal`**.

**Generator family election (design-practice setting — ECS, not Potter):**

| Family | Role | Held evidence (OEM values = listing-specific; confirm at submittal) |
|---|---|---|
| **ECS AdvancedIQ** (wall-mount AG-675 / 950 / 2000 / 3500) | **Default family** | IOM **M-1428 Rev 1.12** pp. 8–9: largest single zone **235 / 235 / 800 / 800 gal @ 40 psig** (470 / 470 / 1,600 @ 20 psig); accumulative **675 / 950 / 2,000 / 3,500 gal**; "largest system capacities … based on FM Global testing"; "FM Approved: Standard 1035" = listing claim; AMD one per system (AG-675/950 single-system may omit). Spec sheet **Rev 6.00**: integral compressor + bypass meets the 30-min fill; inert "within 14 days" = **listing timeline, not measured**. Above the AG listing single-zone fill → separate compressor / larger ECS configuration `[V]` with ECS. |
| **UFS NITROGEN-PAC M-Series NGM-5…60 + CTA** | **Alternate — FM-certificate grade** | Certificate **PR470042** (FM 1035 Sep 2024). UFS-354 Table 1 **maximum sprinkler pipe volume:** NGM-5 **3,000** · NGM-10 **5,000** · NGM-20 **10,000** · NGM-30 **20,000** · NGM-60 **31,100 gal** (basis pressure / leak / riser count not printed). 30-min fill rides the **CTA** via the NGM membrane bypass — UFS-352 Table 1 bypass: CTA-30 **2,700 @ 20 / 1,350 @ 40 psi**; CTA-50 4,000 / 2,000; CTA-75 7,700(?) / 3,350 (20-psi value breaks the 2:1 pattern — confirm with UFS); CTA-100 10,700 / 5,350. Current-generation manual 30-NPMICM-0G2 unheld — do not mix with 2019 NGM-S/M/L codes. |
| **UFS NITROGEN-PAC SC-1L** | Alternate — certificate only | Certificate **PR470065** (FM 1035 Sep 2024). **No held capacity gate** (SC Series ICM Rev 4.00 Table 3 lists SC-1S/1M/2M/2L only) — do not borrow SC-1S/1M numbers; `[V]`. |
| **Potter IntelliGen** INS-500/1000 (#5403645 Rev J 02/25) / INS-1500/2000 (#5403646) | **Cited example only** | FM 1035 = IOM claim; bypass / total gallons are vendor figures for those SKUs — not campus defaults. Stale INS-100/250 #5403644-P **Absent in **. |
| South-Tek N2-BLAST / GAP NGP / Tyco NG-2 | Cited examples | Function + listing pointers only (Tyco NG-2 = ECS family). |

**Two-number pairing rule (any family):** (1) generator **maintenance / max-pipe-volume** capacity ≥ **Σ gallons** of all dry/DI systems it serves; **and** (2) compressor / CTA / bypass **30-minute fill** ≥ the **largest single system** at its fill pressure (30 min body rule [CODE NFPA 13-2025 §8.2.7.3; 2019/2022 §8.2.6.3.2]; 'single largest system' is annex text, A.8.2.6.3.2 in 2019/2022 and A.8.2.7.3 in 2025 [annex]). The two tables are independent (e.g. NGM-10 = 5,000 gal maintenance, but with CTA-30 it fills only a **1,350 gal** single system at 40 psi). Fill CFM pin (labeled derivation): `V × P / (7.48 × 14.7 × 30)`. **Do not size a compressor from "CFM @ max pressure" with the Viking F_011607 factor (gal × 0.01213 free-air CFM for 40 psi in 30 min)** — on the UFS CTA it **under-credits the unit 1.40–1.89×**; use the printed bypass gallons. **Tank gallons ≠ system gallons**; a quick-fill compressor is not the supervisory maintenance device (C-Aire packages). This is not a `calcs` kernel op — print the arithmetic as a pin.

Do **not** copy Hopkins test-rig scfm / gallon figures onto a campus.

Honest correction: a membrane generator **cannot create an oxygen-deficient atmosphere in its own room** (product N₂ leaves into the piping; waste is oxygen-rich). Safety conclusion is unaffected.

### 3.6 The nitrogen package on the drawing

Mark each `DRAW` / `SPEC` / `C&E` / `N/A` / `[V]`.

1. **Draw the compressor AND the generator.** The 30-minute fill is met by the **COMPRESSOR** half; the generator is the maintenance/replenish half. Show the **two-number check** (Σ gal vs maintenance capacity; largest single system vs fill) per riser room. Hand CFM arithmetic to *Dry-pipe & double-interlock air supply and water delivery* / water-delivery peer as needed. **Do not invent scfm.** **Compressor ≠ generator.**
2. **30-minute clock = SINGLE LARGEST system, not the aggregate.** NFPA (via Viking) **and** FM DS 2-0 §2.2.1.10.5 agree. This is **FILL**, not water-delivery.
3. **Per-system obligations survive a shared generator.** Each dry/DI system still owes **its own air maintenance device** and **its own check / backflow device** (NFPA 13-2007 §7.2.6.5.3 via Viking — `[V]` vs 13-2025). Eight zones = eight AMDs.
4. **Purge valve REMOTE, not at the riser.** Nitrogen follows the path of least resistance from fill to purge (Fick). Riser-purge was the **worst** 8-week performer.
5. **Sampling ports at the ends of the most remote BRANCH LINES**, and at least one dead-end — **not at the purge valve, not at the generator, not at a riser/cabinet vent.** Each purge valve: **levered float** that closes if the dry/preaction valve trips with the purge open, **and** a **sampling port**.
6. **Essential electrical load.** If the air/N₂ supply relies on electrical power: **secondary supply independent of the facility primary, or an emergency generator** (DS 2-0 App. A p.165). Match ITM: gas supply on **standby power or UPS**.
7. **FM air-tightness** (DS 2-81 §3.1.6.1): **40 psi**, should not lose more than **1½ psi over 24 hours**. **Do not raise air pressure to mask a leak.**
8. Low-point drains, back-pitch, trapped volume are corrosion controls. Hand drain sizing / heated valve room to air-supply / ITM Skills.
9. **El/El trim — hand-off.** `HAND OFF — preaction-el-el-trim-election`. Do not write a trim schedule here.
10. **C&E hand-off row.** On **SI** (`comparison-only`): low air is a leak/break alarm; **the valve stays closed**. On **DI** (controlling): air is one of two trip conditions — **do not silently import the SI line onto DI**. **preaction-releasing-c-and-e-soo writes the matrix.**

### 3.7 Parameter C — remote-branch purity sampling (+ thin OEM pointer)

**STOP: never accept a purity reading taken at the purge valve, at the generator, at an AutoPurge/Quick-Check, at a riser vent, or at a cabinet vent as evidence the system is inerted (≥98 % throughout).** It never changes the emitted C=100 either way.

Independent 8-week testing (Hopkins / Summit / TERPconsulting, Sprinkler Age May/June 2024) — article **published** in ; **raw per-port workbook Absent**. Supply gas **deliberately set to 99.2–99.5 %**. **This is not a bad-generator artefact.**

| Purge method | Purge valve | **2 weeks** (system avg) | **8 weeks** (system avg) | vs 98 % gate |
|---|---|---|---|---|
| **Standard** (remote orifice bleed) | **Remote** | **93.5 %** | **97.3 %** | **fails at 14 days; still fails at 8 weeks** |
| **Breathable** (3–5 psi swing) | **At riser** | **82.8 %** | **89.4 %** | **fails badly, both** |
| **Continuous** | **Remote** | **86.3 %** | **97.3 %** | **fails at 14 days; still fails at 8 weeks** |

**Best system-wide at 8 weeks: 97.3 %.** Branch lines *“in the 80s and low 90s.”* **All three methods hit 98 %+ at the purge-valve port** while the system averaged **82.8–93.5 %**. A contractor closeout showing “98.6 % at the nitrogen test port” is fully consistent with an **82.8 % system**.

**Specify elapsed time honestly.** UFC requires **≥98 % throughout within 14 days**; two of three manufacturers claim 14 days. **Nothing in the tested data supports 14 days.** C is **100** regardless. Without measured remote-branch (+ dead-end) ports, the 98 % line stays a **specified verification**, not a claimed achievement. Status ≤ `provisional`/`unresolved`. **Do not quote the GAP advertisement** bound into the same PDF.

Conflict-of-interest travels with the finding (testing hosted at GAP R&D). Investigators (Summit + TERP) are independent; mechanism is ordinary Fickian diffusion. **Treat the data as credible and the framing as interested. Verify on the job.**

#### Thin OEM sampling-location pointer (not a SKU BOD catalog)

Provenance: **mined** unless marked PDF-held. **Still refuse invent scfm/SKU as hall defaults.** **C=100 always.**

| Device / geometry (mined) | What it samples | Inerting-evidence class (C stays 100) |
|---|---|---|
| **Potter INS-PV** IntelliPurge (#5401532 Rev E 6/19) | Remote **end-of-system / branch-line** install OK; 98 % at **on-valve sensor / Purge Exhaust Port** | Location OK for purge; reading still **purge-port class** — not branch-end evidence |
| **Potter IntelliGen** INS-500/1000 (#5403645) / INS-1500/2000 (#5403646) | **Cabinet Nitrogen Sample Port (SP)** + end-of-system Potter purge (INS-PV / NGP-SPV) | Generator/purge-port class — cited example (not default family) |
| **Tyco TAV-D** (TFP1262 Aug 2022) / **TSV-D** (TFP1263 Jul 2025) | Default install **on the riser**, system side of main control valve; THGA/TSGA / gas sample port | **Hopkins worst** (riser / breathable geometry) — vent-port ≠ remote branch |
| **FireFlex TOTALPAC N2 HP Dry** PSV-D (FM-076E-0-13B 2023) | **Cabinet-mounted** SMART vent | Cabinet/riser-class; HP dry ≠ DI host default — comparison / handoff |
| **South-Tek Quick-Check** (10/13/2020) + AutoPurge | Purity via tubing at **AutoPurge** devices | Purge-device class — not remote-branch dead-end |
| **ECS AdvancedIQ / Tyco NG-2** (TFP1277) wall-mount | Cabinet / adjacent **vent** sample (SGA/PHGA); vents drawn **on the riser** | Generator/vent class — **default family**; size on **two volumes** by listing; vents drawn on the riser collide with remote-purge doctrine → move purge remote; **do not invent scfm** |
| **UFS NITROGEN-PAC** (PVA-2/PVA-4 + TAP / Multi-TAP) / **GAP NGP-1000D** | PVA drawn near the inspector's test connection; purity read at the vent | Vent class unless the ITC is at the remote branch end — alternate; no hall-default SKU |

### 3.8 Parameter D — C-factor: emit C = 100 (always)

**★★ design-practice setting: calc C = 100 on company dry / DI sprinkler pipe — always. Do not chase C=120.** This holds even when FM / UFC / NFPA 13-2022 would permit 120 and even when branch-end purity is measured ≥98 %. Emitting 100 is the most-stringent numeric (owner layer raises; nobody lowers).

| Situation | Emitted calc C | C=120 line | Status |
|---|---|---|---|
| Any company dry / DI black-steel system, air or N₂, purity measured or not | **C = 100** | `comparison-only` + 29 % | `grounded` on the 100 emit when inputs pinned |
| Internally galvanized dry / preaction (FM row 120 vs Potter / 13-2013 = 100) | **C = 100** | both sources stay visible, `comparison-only` | `grounded` on 100 |
| Polymer-enhanced (FM row 140) | **C = 100** | 140 = `comparison-only` (`[V]` if listing unopened) | `grounded` on 100 |
| UFC job (permits 120 at ≥98 % / 14 days) | **C = 100** | UFC 120 = `comparison-only`; the 98 % / 14-day obligation still goes in the spec | `grounded` on 100 |
| Software / owner / insurer already ran 120 | **Correct to C = 100** | Print the delta | name it in the BOD |

**Comparison line (print whenever anyone shows 120) — FM DS 3-0 Eq 15, edition-independent physics:**

```
p_f = 4.52 · (Q / C)^1.85 / d^4.87 # psi/ft; d actual ID
p_f ∝ 1 / C^1.85
(120/100)^1.85 = 1.2^1.85 ≈ 1.401
p_f(C=120) / p_f(C=100) = (100/120)^1.85 ≈ 0.714
friction understated by a C=120 calc ≈ 0.286 ≈ 29 %
```

Where a pipe-segment friction number is needed, run it through `calcs/fp/run.py` `hw` at **C=100** (optionally a second step at C=120 labeled `comparison-only`) with the JSON saved beside the deliverable.

This Skill **emits C=100** for density-area / pump-envelope / hydrant-supply-curve / the hydraulic tree to **consume**. Do not silently mix **sprinkler-pipe C** with **underground C**.

VPCI / chemical inhibitor is **not** a drop-in equivalent to the inert-medium row. 13-2025 adds **VCI systems §8.2.11** — **directional `[V]`**, not floor under 13-2022.

#### Appendix D-1 — C=120 comparison reference (`comparison-only`; never the design path)

**FM DS 2-0 Table 2.2.1.3.3 (p.13):** wet black steel **120**; dry/preaction black steel **100**; dry/preaction black steel **+ inert gas 120**; internally galvanized dry/preaction **120**; polymer-enhanced **140**. UFC 3-600-01 Change 6 §9-6/§9-7: C=120 with ≥98 % throughout in 14 days. NFPA 13-2022 (Hopkins characterization) C=120 at 98 % — Table 28.2.4.8.1 now held: 2025 item (14) citing §8.2.10, 2022 item (13) citing §8.2.6.9, new systems only ; 98 % link and TIA effect `[V]`. Hopkins 8-week data (§3.7): no purge method reached 98 % system-wide. Record these so reviewers see what was declined and why.

### 3.9 Parameter E — ITM-lever eligibility, then hand off

Match **itm-design-for-testability** nitrogen language. **Do not emit the interval-lever schedule here.**

**FM DS 2-81 Table 2c items 14 & 15 p.11:** full-flow **every 3 years — or EVERY 10 YEARS for systems with nitrogen**; black-steel obstruction check **excludes systems originally installed with nitrogen**.

```
(1/3) / (1/10) = 10/3 ≈ 3.3× fewer full-flow trips
```

**Condition precedent:** *“originally installed with nitrogen.”* A later O&M conversion **does not buy it**. Nitrogen = `n` is **not a Stop** — it is a lever **not taken**.

**⚠ NFPA 25 floor is 3 years** [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]. On a code-enforced or non-FM project, **this lever DOES NOT EXIST.**

**⚠ Company fence:** promise **3→10 only** when FM DS 2-81 controls **and** originally-installed N₂ on company-elected **dry/DI**. Never on SI-as-BOD.

**Required hand-off row:** `HAND OFF — itm-design-for-testability: nitrogen originally installed = y/n on each dry/DI hall. Hardware + C-factor gate is closed here. Interval-lever schedule is THAT Skill’s.` Status the eligibility row (`grounded` / `provisional` / `handoff`).

---

## 4. Output

A **nitrogen-inerting + C-factor gate**. Write **only** to the caller-named path.

Minimum: Hard-scope gate + status register (gate / A–E / emitted C / ITM eligibility); edition-pin block (name remaining holes: 13 C-table, FM 1035 standard text (Sep 2024 edition certificate-cited, text unheld), NFPA 25, Hopkins raw per-port workbook); inputs echoed including **packet + STS dry|DI + matrix N₂/C rows**; statement **C=100 always** (design-practice setting) with the C=120 `comparison-only` line + 29 %; generator family (ECS default; alternates) + two-number check; Parameters A–E with status; package checklist (`DRAW`/`SPEC`/`C&E`/`N/A`/`[V]`); 8-week sampling table; thin OEM sampling-location pointer; emitted C=100 + 29 % comparison line; ITM-lever eligibility hand-off; reciprocal C&E / water-delivery / El/El hand-off rows; Δ vs 13-2025 and vs NFPA 25; `[SYN]`/`[V]` register. **NO PLACEHOLDER.**

Do **not** emit occupancy schedule, density×area `calcs`, pump nameplate, node-by-node tree, SprinkFDT, ITM task calendar, El/El trim schedule, QOD/30 s delivery proof, a fake 98 % closeout, or CASE_INDEX retrieval.

---

## 5. Stop

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

1. Assignment packet missing → not a Stop (packet optional); proceed and flag `ASSUMED`. 2. STS election missing / `unresolved`, or system type missing / still **wet** with no dry/DI (N/A vs Stop as applicable). 3. SI/NI (or other prohibited preaction) presented as **BOD** → `RFI-variance`. 4. Foam BOD. 5. Mist design request (`PRACTICE REFUSED` / `RFI-variance`). 6. Dual-carrier controlling nitrogen / C / inert-medium matrix rows missing when required → `unresolved`. 7. Pipe material unpinned. 8. Unpinned carrier. 9. Unpinned AHJ NFPA 13 edition. 10. Caller asks to emit **C=120 as the design C** (desk assumption or "earned" by purity data) → refuse; emit **C=100** (design-practice setting) and print 120 as `comparison-only_pruner` / / / ARCHIVE / root PDF queue.

Nitrogen = `n` on a dry/DI hall is **not** a Stop — it is a lever **not taken** and a C-credit **not taken**. Record both.

---

## 6. Citations (section AND edition)

**FM DS 2-1 Oct-2016 / IR Jul-2022 (mined):** §3.1 oxygen cathodic driver; §2.2.1.12.1 N₂ + FM Approved generator, black steel if N₂ for life; §2.2.1.4 / §2.2.1.13.B no internally galvanized wet; IR 2022 wet-pipe N₂ + polymer-enhanced; §3.2 **20×** dry CS air vs N₂; §3.3 **≤14×** wet; <98 % (e.g. 95 %) tracks toward air; **does not grant C=120**.

**FM 1035 (September 2024) — certificate-held, standard text unheld:** UFS **PR470042** NGM-5 / 10 / 20 / 30 / 60 (granted 15 Sep 2025; UFS-356 Rev 1.00 Sep 2025); UFS **PR470065** NITROGEN-PAC SC-1L (granted 25 Oct 2024; UFS-612A Rev 1.00 Mar 2025). Sep 2022 standard copy opened (PDF-held): §1.2 scope; §3.5 / §4.2 bypass; §4.3 generation capacity — `[V]` vs Sep 2024.

**UFS NGM data sheet UFS-354 Rev 1.02 (Sep 2025):** Table 1 max sprinkler pipe volume 3,000 / 5,000 / 10,000 / 20,000 / 31,100 gal (NGM-5…60). **UFS CTA UFS-352 Rev 1.01 (Jun 2025):** Table 1 bypass 30-min fill 2,700/1,350 · 4,000/2,000 · 7,700(?)/3,350 · 10,700/5,350 gal @ 20/40 psi; Viking 0.01213 cross-check under-credits 1.40–1.89×. Pairing rule = KB synthesis .

**ECS AdvancedIQ IOM M-1428 Rev 1.12 (©2025) pp. 8–9 + AG-2000/3500 spec Rev 6.00 (mined):** zone / accumulative gallons per SKU; FM 1035 listing claim; integral compressor + bypass for 30-min fill; 14-day = listing timeline; riser vents (PAV-D/PSV-D) collide with remote-purge doctrine.

**Worked packages (`[SYN]` method):** `` (a prior layout two-number check); `` (a prior layout IA dock generator election); `worked-ac-caire-quickfill-231` / `worked-ad-caire-mid-232` / `worked-ae-beecher-cs-233` (C-Aire / N2Blast feed air). All C = 100.

**FM DS 2-0 Oct-2021 / Jan-2024 (mined):** Table 2.2.1.3.3 p.13 C-rows; §2.2.1.10.2 inert default; §2.2.1.10.3 air only if dryer or ≤20 heads; §2.2.1.10.5 FM Approved generator + 30-minute fill; §2.2.4.3.2 pendent galvanized-or-N₂; App. A pp.158, 165 regenerative dryer / reliable supply.

**FM DS 2-81 Apr-2019 / Oct-2021 (mined):** Table 2c item 14 p.11 full-flow 3→10 yr; item 15 originally-installed obstruction exemption; §3.1.6.1 40 psi / 1½ psi / 24 h.

**FM DS 3-0 March 2010:** Eq 15 `p_f = 4.52·(Q/C)^1.85 / d^4.87`; Eq 17 / Table 13 `(C/120)^1.85`.

**Hopkins / Sprinkler Age May/June 2024 (mined Exceptional article; raw per-port workbook Absent):** 8-week averages 93.5→97.3 / 82.8→89.4 / 86.3→97.3; purge-valve 98 %+; branches 80s–low 90s; generator does not replace compressor; NFPA 13-2022 C=120 at 98 % `[V]` vs 13-2025.

**Potter ~2013 Table 2 (mined; corrosion data):** 45.4 / 91.8 / 78.6 / 61.6 %; galvanized lost more than black steel. Cite **table not conclusion**.

**ECS May 2014 (mined):** liquid N₂ never; 2 gal LN₂ / 1 Type A cylinder; OSHA 19.5 %.

**UFC 3-600-01 Change 6 (2021) §9-6 / §9-7 (mined):** mandatory N₂, 98 % / 14 days, C=120, no bottles; continuous venting not permitted.

**AXA XL Mar-2026 p.8 (mined):** DI nitrogen-fill +30 % area (controlling AXA N₂ mandate). SI preferred = **`comparison-only`** under company fence.

**OEM sampling (mined):** Potter INS-PV #5401532; IntelliGen #5403645 / #5403646; Tyco TAV-D TFP1262 / TSV-D TFP1263; South-Tek Quick-Check 10/13/2020; ECS AdvancedIQ / Tyco TFP1277; FireFlex TOTALPAC PSV-D; UFS / GAP function+listing pointers.

**Absent / still `[V]` / PDF-held:** NFPA 13-2025 C-value table and TIA status; NFPA 25-2026; **FM 1035 standard text** (Sep 2024 edition named on certificates; Sep 2022 opened, PDF-held); UFS current-generation manual 30-NPMICM-0G2; SC-1L capacity gate; NGM basis pressure / leak rate behind the volume ceiling; Hopkins **raw** per-port workbook (article mined); a Tier-A owner nitrogen standard; Potter INS-100/250 #5403644-P (Absent in ).

---

## 7. Design practice

1. Three-layer, most stringent, on **five parameters separately**: medium, source, sample locations, C-factor, ITM-lever eligibility. Owner may raise, never lower.
2. Per-parameter, not per-layer. Never MAX whole sheets.
3. **C = 100 always** (design-practice setting — don't chase 120); C=120 is a `comparison-only` line with the 29 % shown. **ECS** is the default generator family; specify duty + listed function, OEM values confirm at submittal. Originally-installed nitrogen is a CD specification. The 10-year lever does not exist where NFPA 25 is enforced directly, and does not exist on SI-as-BOD.
4. Current editions; enforced ≠ latest. Do not invent 13-2025 C-table section numbers.
5. Show-and-verify: `(120/100)^1.85 ≈ 1.401` → **≈29 %**; `10/3 ≈ 3.3×` ITM trips (hand-off arithmetic); two-number check and fill CFM printed as pins. Pipe friction, if needed, via `calcs/fp/run.py hw` at C=100.
6. Honesty. Worked packages (a prior layout, a prior layout dock, C-Aire/N2Blast) are **method** — Adapt, don't copy. Do not invent purity % or generator scfm or SKU. Galvanized dispute: **C=100 and both sources stay visible.** DS 2-1 20×/14× ≠ C=120 grant. UFC 14-day = obligation ≠ Hopkins achievement.
7. Status vocabulary every run. Company fence dry|DI. Foam prohibited. Mist `PRACTICE REFUSED`. Packet optional; STS + matrix consumed or `ASSUMED`. **NO PLACEHOLDER.** Caller-path-only.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Wet / dry / double-interlock election | suppression-technology-selection |
| Nitrogen as **3 yr → 10 yr** interval lever | **itm-design-for-testability** |
| Low-air / LOW AIR ALARM / SI vs DI trip Boolean | **preaction-releasing-c-and-e-soo** (SI line comparison-only) |
| Density × area `calcs` | density-area-dry-increase (consumes C; AXA DI+N₂ area penalty) |
| Pump envelope / hydrant curve | pump-envelope / hydrant-supply-curve (underground C is **not** sprinkler C) |
| Node-by-node tree | hydraulic-tree Skill (consumes the C this Skill emits) |
| 30 s / 60 s water-delivery / QOD listing | **dry-preaction-water-delivery-screen**. Compressor 30-minute **fill** stays in this package and is **not** that clock. Fill ≠ delivery. |
| El/El / valve-room trim catalog | **preaction-el-el-trim-election** |
| Occupancy / HC / OH | occupancy-hazard-fork |
| Dual-carrier BOD | most-stringent-basis-matrix |
| SprinkFDT | **not this Skill** |

---

## Check before you finish

1. Hard-scope gate: dry|DI only; wet → N/A; SI/NI-as-BOD → Stop `RFI-variance`; foam/mist Stop. Emit status on gate. 2. Check packet (optional) + STS `dry`|`double-interlock` + matrix nitrogen/C/inert rows; missing → `ASSUMED` (flagged), not a Stop. 3. Confirm other inputs; Stop tests. 4. Pin editions; name the holes (13 C-table, 1035 WHOLE/2024, NFPA 25, Hopkins raw per-port). 5. Union five parameters separately; status on each. 6. Elect inert vs air (AXA SI = comparison-only; AXA DI mandates N₂). 7. Elect generator vs cylinders. Liquid = Stop. Specify by duty + listed function (FM 1035 where claimed / certified); **ECS = default family**, UFS NGM+CTA = FM-certificate alternate, Potter IntelliGen = cited example; OEM values confirm at submittal. Two-number check (Σ gal vs maintenance; largest single vs 30-min fill); no Viking 0.01213 sizing from CFM @ max pressure. Draw compressor + generator. 8. Remote purge. Branch-end (+ dead-end) sample ports. Reject purge-valve / generator / AutoPurge / riser-vent / cabinet-SP readings as inerting evidence. Print the 8-week table + thin OEM sampling pointer. 9. Emit **C=100 always** (design-practice setting). C=120 = `comparison-only` line with ≈29 % shown. DS 2-1 does not grant 120. 10. ITM-lever eligibility; hand off to itm-design-for-testability (dry/DI + FM only). 11. Reciprocal hand-offs: water-delivery (fill ≠ delivery) / El-El / C&E / STS / matrix / density consumers. 12. Δ vs 13-2025 and vs NFPA 25. 13. Honesty: worked packages are method (Adapt, don't copy); no PLACEHOLDER; no invent purity/scfm/SKU/14-day. 14. Write **only** to the caller-named path.
