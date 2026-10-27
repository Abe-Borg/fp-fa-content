---
name: Containment ceiling and obstruction coverage
description: >-
 use this, ideally after HC/OH + density×area are pinned (if absent, assume
 and flag ASSUMED), when you must elect the
 3-D sprinkler coverage scheme for hot-aisle containment + overhead bus/tray +
 concealed plenums (drop-out Class 4651 vs protect-beneath vs grate ≤4 ft;
 obstruction offset/≥12 psi; EC concealed-space heads) — against company
 wet|dry|DI only (consume STS; this Skill does not elect family); packet optional;
 STS + fork + density (+ matrix geometry/carrier/obstruction when dual)
 consumed when present, else ASSUMED and flagged — never a stop; SI/NI-as-BOD → Stop RFI-variance (comparison-only;
 SI sized-as-wet ≠ wet feed); foam prohibited; mist PRACTICE REFUSED; status
 register every run — not occupancy, not density×area, not ASD return-sampling,
 not a head-coordinate dump or CAD, not invent hall.
---
# Containment ceiling and obstruction coverage

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. After occupancy-hazard-fork has classified the hall and density-area-dry-increase has pinned `q_spr` / `system_type`, this Skill **elects the 3-D sprinkler coverage scheme** and emits a **path + spacing/obstruction schedule**. The spine is: **containment-ceiling path → deflector datum → overhead obstruction treatment → concealed-space EC map**.

It is a **PATH ELECTION + spacing/obstruction SCHEDULE**. It is **not** occupancy classification. It is **not** a density×area demand. It is **not** an ASD/VEWFD return-sampling plane. It is **not** a head-coordinate dump, a reflected-ceiling CAD, or a hydraulic tree. It does **not** elect the suppression family — it **consumes** STS `wet` | `dry` | `DI` and records geometry consequences (wet-feed gate, Path 2 SOO limb, DI economics on Test A).

**Design practice:** 3-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PARAMETER** → report **directional Δ vs NFPA 13-2025** on obstruction / concealed / drop-out / deflector. Cite **section AND edition**. Enforced ≠ latest. Show-and-verify any arithmetic. Flag invented values `[SYN]` and unpinned assumptions `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet + STS `wet`|`dry`|`DI` + `occupancy-hazard-fork` + `density-area-dry-increase` (+ `most-stringent-basis-matrix` **geometry / carrier / obstruction** rows when dual-carrier — **consume and return here**). Caller-path-only. **NO PLACEHOLDER.** Do not invent section numbers. Owner may **raise, never lower**. Physics / vendor preference ≠ requirement.

**Corpus honesty (training ground — never hall defaults):** the IN containment-coverage outline + worked package are **`[SYN]` method** (Path 2 window, ≤4 ft offset, SP-C(o), schedule tags). Hall **36k ft² / 26 ft / 10 ft lid / 11.4 ft grid** and companion SI label = **`comparison-only`** — never project defaults; never company BOD. Worked-package framing of 130 ft² as “NFPA-13 OH cap” is drift — this Skill’s **DS 2-0 HC-2** attribution wins. Do not invent or copy those numbers as defaults.

Look up shop codebook notes **by title** (not a required filesystem path): *Containment coverage / HAC ceiling path notes (drop-out vs beneath vs grate)* — may alias mined content inside *Data-center sprinkler and preaction design* + *FM occupancy vs installation sheet precedence (DS 5-32 and DS 2-0)*; *FM DS 5-32 insurer design basis*; *FM DS 2-0 installation sheet*; *Sprinkler installation, piping and component basis*; *The Design practice*; *Enforced-vs-latest edition resolver and reference pins*. Do **not** invent a standalone titled containment KB note this run.

**Elects (preserve):** (1) **HAC ceiling path** — Path 1 protect-beneath / Path 2 FM Class **4651** drop-out + ceiling QR / Path 3 grated HAC ≤**4 ft** / **open** — with the fusible-link / auto-release **prohibition** on the same row. (2) **Deflector datum** and, if Path 2, the **panel-elevation window**. (3) **Overhead obstruction schedule** — DS 2-0 under-object test **and** DS 5-32 **≥12 psi or ≤4 ft** offset, kept separate. (4) **Concealed-space coverage map** — EC non-storage at the consumed density/area, or the FM “nothing recommended” terminal. (5) **Spacing/coverage window** (7–12 ft linear, 64–130 ft²/head on FM HC-2). Schedule limits, not a layout.

**Hard fence (CAD / invent):** if the caller asks for CAD, a head-coordinate dump, a hydraulic tree, or a density×area `calcs` → **Stop**. Do not “just put the heads on a 11.4 ft grid.” That number is a **worked-package method check**, not a default. Do not invent fabricated tokens or hall defaults.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (geometry-adapted — consumes STS, does not elect)

This Skill owns **HAC Path 1/2/3 / open election + deflector datum + Test A/B obstruction schedule + EC concealed map + spacing/coverage window**. Controlling company BOD = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI | `suppression-technology-selection` (**consume** — do not elect here) |
| Elect HAC Path 1/2/3 / open; schedule deflector / Test A / Test B / EC / spacing | **This Skill** |
| Dual-carrier per-parameter union (geometry / carrier / obstruction rows) | `most-stringent-basis-matrix` (**consume**, then **return here**) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- IN SI containment-geometry spine (method only)

**This Skill does not elect families.** It **consumes** the STS token `wet` | `dry` | `DI`, the completed the input packet, fork HC/OH, density-area `q_spr`/`system_type`, and — when carrier = `dual` — matrix **geometry / carrier / obstruction** rows. Then it elects the coverage path and emits the schedule.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue geometry as if SI/NI were company-elected BOD.
6. SI/NI (including the IN SI spine) may appear only as **`comparison-only`** evidence — never an ordinary elective family option.
7. Preserve the technical note under company-elected wet/dry/DI (or when SI appears only as sheet/synthetic evidence): **SI sized-as-wet ≠ wet feed** until the valve trips — tag that consequence **`comparison-only`** when SI is the source, or as a geometry consequence of company dry/DI when that is the elected feed.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream via STS | Record geometry consequences (wet-feed gate, Path 2 SOO limb, DI Test A economics) |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance`; keep SI≠wet-feed technical as comparison-only |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD or foam obstruction/coverage family |
| Water mist | **`PRACTICE REFUSED`** | Record sheet language that groups mist with sprinkler airflow/CFD remedies (precedence note / DS 5-32 §3.5.2.3) if cited; do **not** design/accept mist as BOD or as elective obstruction/coverage family |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | Handoff-only | Do not invent clean-agent coverage here |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Sheet language that groups water-mist with sprinkler airflow remedies is **`comparison-only`** — never mist BOD.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| HAC Path 1/2/3 / open + fusible-link prohibition | System-family election (`suppression-technology-selection`) |
| Deflector datum + Path 2 panel window | Occupancy / HC/OH re-class (`occupancy-hazard-fork`) |
| Test A (DS 2-0) + Test B (DS 5-32) separate columns | Density×area `calcs` (`density-area-dry-increase`) |
| EC concealed map + nothing-recommended | ASD/VEWFD return-sampling (`fa-asd-vewfd-data-hall-sampling-layout`) |
| Spacing window 7–12 ft / 64–130 ft² (schedule limits) | Head (x,y,z) / CAD / RCP / hydraulic tree |
| Status register + reciprocal handshakes | Dual-carrier BOD authorship (matrix — consume+return) |
| Consume packet + STS + matrix(when dual) + fork + density | Invent hall 36k/26/10/11.4 defaults; mint AXA Class 4651 |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet / STS / matrix(when dual) / fork / density, **(c)** containment_type / lid, **(d)** path election, **(e)** deflector / Path 2 window, **(f)** Test A, **(g)** Test B, **(h)** wet-feed gate, **(i)** EC map, **(j)** spacing window, **(k)** Δ vs 13-2025, and **(l)** mist/foam if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling path + editions + arithmetic supported by mined sheet / caller geometry already closed |
| `provisional` | Directionally pinned; Ch. 10 / Path 2 SOO dwell / edition hole flagged `[V]` — **never silent `grounded` on copied IN 36k/26/10/11.4 defaults** |
| `unresolved` | STS / matrix(when dual) / fork / density / containment_type / lid / widths / plenums not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, IN SI spine, SI≠wet-feed technical when SI is the source, sheet mist/airflow wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; ASD VEWFD; full C&E; dry delivery; ITM lid; multizone cell; pump/hydrant) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as controlling medium or elective obstruction/coverage family — record and refuse |

**Copied synthetic 36k ft² / 26 ft / 10 ft lid / 11.4 ft grid → never `grounded`.** ≥12 psi unverified → never `grounded` “meets Test B by pressure.”

### 1.5 Look-up-by-title + corpus honesty

The Look-up title *Containment coverage / HAC ceiling path notes (drop-out vs beneath vs grate)* is **not** a standalone mined KB file today — content lives inside *Data-center sprinkler and preaction design* and the DS 5-32 / DS 2-0 precedence note. Treat that title as an **alias**, not a license to invent a new KB note this run.

IN outline + worked package = **`[SYN]` method** only. SI label on that spine = **`comparison-only`** under company fence. Refuse copying **36k · 26 · 10 · 11.4** (or companion K/SIN picks) as project defaults. Worked “NFPA-13 OH 130” is correct: 130 ft² is the NFPA 13 Ordinary Hazard maximum [CODE NFPA 13-2019/2022/2025 Table 10.2.4.2.1(b), Ordinary Hazard, all rows: 130 ft² max protection area, standard pendent/upright spray; pulls ]; FM DS 2-0 HC-2 also uses 130 ft² for the comparison. Cite both; the most stringent governs.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent a hall. Do not treat SI/NI as company BOD.

| Input | Required | Notes / Stop |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| Occupancy-hazard-fork schedule | **yes** | Consume **HC/OH**. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not re-classify. |
| Density-area result | **yes** | Consume `density_gpm_ft2`, `system_type`. Missing `system_type` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not re-run density×area. |
| **Consumed `most-stringent-basis-matrix` geometry / carrier / obstruction rows** | **yes** when dual-carrier (or when those rows exist) | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away as if matrix replaces this Skill. Unresolved controlling geometry/carrier/obstruction row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here** to elect path + schedule. Never silent-swap FM Class 4651 onto an AXA-only job. |
| **`containment_type`** | **yes** | `hot-aisle` \| `cold-aisle` \| `hot-collar` \| `open` \| `undetermined`. Undetermined → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (assume the more demanding containment case). |
| **`lid_construction`** | **yes if not `open`** | `solid` \| `FM-drop-out` \| `grated` \| `curtain/fusible` \| `undetermined`. Curtain/fusible is **illegal as a substitute** — elect Path 1 or 2; do not credit the curtain. |
| **`h_ceiling_ft`** | **yes** | FM DS 5-32 **30 ft (9 m) cap**. **>30 ft on FM with no cited off-table path → Stop.** |
| **`h_lid_ft`** | **yes if Path 2 is a candidate** | If unknown and Path 2 requested → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| Overhead-object schedule | **yes if any overhead layer exists** | Per run: `tag`, `kind`, **`width_ft` (least dimension parallel to the floor)**, `top_ft AFF`. Missing widths on a hall that has overhead distribution → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| Concealed-space flags | **yes** | Below-floor supply and/or above-ceiling return + combustibles/cables yes/no. If plenums exist and contents undeclared → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (assume combustible cables present). |
| Controlling **carrier** | **yes** | `FM` \| `AXA XL` \| `none` \| `dual`. Unpinned insured job → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. **`dual` → consume matrix** geometry/carrier/obstruction rows (see above); this Skill still owns the coverage emit. Class **4651** is an **FM Approval class** — do not invent an AXA/NFPA class number. |
| **Owner posture** | **yes** (may be “none / NDA”) | May **force Path 1**, tighter spacing, extra under-object heads. Raise, never lower. |
| AHJ-enforced NFPA 13 edition | **yes to cite** | Δ baseline = **NFPA 13-2025**. Enforced ≠ latest. |
| Caller **output path** | **yes** | If unnamed, return the schedule in the response and stop. |

**Do not invent** hall area, deck height, lid height, bus/tray widths, K-factor, or a 11.4 ft grid. Worked-package numbers are **METHOD, not defaults**. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token**; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `occupancy-hazard-fork` | HC/OH schedule — consumed when present (else `ASSUMED`, flagged) | Re-classify occupancy here |
| `density-area-dry-increase` | `q_spr` / `system_type` / design area — consumed when present (else `ASSUMED`, flagged) | Re-run density×area `calcs` |
| `most-stringent-basis-matrix` | **Geometry / carrier / obstruction** rows when dual-carrier; company fence | Rebuild dual-carrier BOD; Stop-away forever; silent FM↔AXA Class 4651 swap |
| `fa-asd-vewfd-data-hall-sampling-layout` | Below-floor VEWFD omission / return-sampling plane handoff | Size ASD ports here |
| `preaction-releasing-c-and-e-soo` | Consumes Path 2 drop-out limb SOO from this Skill | Rewrite full C&E here |
| `dry-preaction-water-delivery-screen` | Delivery-clock companion when STS is dry/DI | Prove ≤30 s fill here |
| `itm-design-for-testability` | Path 2 lid fail-to-drop → ITM of panels | Emit ITM interval calendar here |
| `multizone-preaction-zone-alignment` | Consumes containment-**cell** geometry for zoning | Elect Path 1/2/3 there; invent zone count here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or STS `wet`|`dry`|`DI` is missing / `unresolved`, or dual-carrier controlling geometry/carrier/obstruction rows are missing when required, or occupancy-hazard-fork is missing, or density-area is missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Outbound this restamp only.** Zero live peers currently name this Skill by id — do **not** restamp peers from here.

| Peer | They own | This Skill owns |
|---|---|---|
| `occupancy-hazard-fork` | HC/OH space-list (required upstream) | Consume only; do not re-classify |
| `density-area-dry-increase` | `q_spr` / design area / dry increase (required upstream) | Consume `system_type`; do not re-size |
| `most-stringent-basis-matrix` | Per-parameter union / geometry·carrier·obstruction rows | **Consume only** when dual — then elect path + schedule **here** |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume only**; hand family under company fence; mist = `PRACTICE REFUSED`; foam prohibited |
| the input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `fa-asd-vewfd-data-hall-sampling-layout` | Return-sampling plane / 60-ACH interlock sizing | Below-floor VEWFD omission handoff; do not size ports here |
| `preaction-releasing-c-and-e-soo` | Authoritative full preaction C&E / Boolean | Path 2 **drop-out limb SOO only** |
| `dry-preaction-water-delivery-screen` | Delivery clock when STS is dry/DI | Geometry does not prove ≤30 s |
| `itm-design-for-testability` | Lifecycle ITM / Path 2 lid fail-to-drop ITM | Name ITM of panels; do not emit interval calendar |
| `multizone-preaction-zone-alignment` | 1:1 PA↔cell zone alignment from containment-cell geometry | Do **not** elect Path 1/2/3 there; do not invent zone count |
| `pump-envelope` / `hydrant-supply-curve` | Pump listed envelope / hydrant curve | **Not-this** — preserve |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency. Do **not** restamp peers from this Skill.

Example lines:

- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: geometry/carrier/obstruction rows when dual. Consume; return here after.`
- `HAND OFF — the input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — occupancy-hazard-fork: HC/OH. Consume only.`
- `HAND OFF — density-area-dry-increase: q_spr / system_type. Consume only.`
- `HAND OFF — fa-asd-vewfd-data-hall-sampling-layout: return-sampling plane / below-floor VEWFD.`
- `HAND OFF — preaction-releasing-c-and-e-soo: full C&E; this Skill writes Path 2 drop-out limb only.`
- `HAND OFF — dry-preaction-water-delivery-screen: delivery clock when dry/DI.`
- `HAND OFF — itm-design-for-testability: Path 2 lid fail-to-drop ITM.`
- `HAND OFF — multizone-preaction-zone-alignment: cell zoning; Path election stays here.`
- `HAND OFF — pump-envelope / hydrant-supply-curve: Not this Skill.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before edition pins or path election:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`.
2. Check upstream (packet optional): packet if present (optional); STS present; fork present; density present; matrix geometry/carrier/obstruction rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix·fork·density / containment_type·lid / path / deflector·window / Test A / Test B / wet-feed / EC / spacing / Δ 13-2025 (tokens from §1.4). Keep `[SYN]`/`[V]`/`[VERIFY]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER** anywhere in the run.

### 3.1 Pin editions (enforced ≠ latest)

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor | NFPA 13 obstruction / drop-out / concealed / deflector | **NFPA 13-2025** = Δ baseline. Unamended **2024 I-Codes** typically pin **NFPA 13 → 2022**. **Ch. 10 obstruction/position/coverage criteria are not mined** → directional `[V]`; **do not invent a 13-2025 section** except the deflector datum [CODE 2025 §10.2.7.1.1.1 / 2022 §10.2.6.1.1.1, unobstructed construction] and 2025 spacing §10.2.6, and protection area / max spacing by hazard [CODE NFPA 13-2019/2022/2025 Tables 10.2.4.2.1(a) to (d), pulls ]; obstruction rules held: three-times rule (max clear distance 24 in.) [CODE NFPA 13-2022 §10.2.7.3.1.3 / 2025 §10.2.8.3.1.4]; sprinklers under fixed obstructions over 4 ft wide [CODE NFPA 13-2022 §10.2.7.4.2; 2025 §10.2.8.2(6) [CODE NFPA 13-2025 §10.2.8.2(6)]; ≤4 ft wide needs no sprinklers below only where Table 10.2.8.2(a)/(b) and Figure 10.2.8.2(a) are maintained (§10.2.8.2(7)); Tables 10.2.8.2(a) (US) and 10.2.8.2(b) (SI) now held in full, 14 rows each, e.g. (a) "Less than 1 → 0" … "7 or more → 35 or less" [CODE NFPA 13-2025 Table 10.2.8.2(a)/(b)]; Figures 10.2.8.2(a)–(d) are PNG-only, so read the dimensions A/B from the figure and do not transcribe them as text]. |
| Insurer occupancy | HAC paths, tray offset, EC concealed, QR, 12 ft max, 4 in. deflector max, 30 ft cap | **FM DS 5-32, January 2026**. |
| Insurer install | 4 ft least-dimension, supplemental-head wet-feed gate, 7–12 ft / 64–130 ft² window | **FM DS 2-0, October 2021 / Interim Rev January 2024**. DS 2-0 is the **BASE**; DS 5-32 is a **narrow overlay**. Obstruction analysis is **handed back** to DS 2-0 (DS 5-32 §2.4.3.2.1.1.1). |
| Owner | Tighter path / spacing / extra heads | Project-issued. Public posture ≠ BOD. |

Consume the assignment packet (optional), STS token, fork, density-area, and matrix geometry/carrier/obstruction rows when dual (consumed when present, else `ASSUMED` — see §2). Do not rebuild them. If a packet note conflicts with this Skill’s per-parameter union, **Design practice most-stringent wins** and both sources stay visible.

### 3.2 Confirm prerequisites — consume, don’t redo

Occupancy-hazard-fork has **HC or OH** (FM white space = **HC-2**). Density-area has **`system_type`**. STS token is `wet`|`dry`|`DI`. Dual-carrier → **consume** matrix geometry/carrier/obstruction rows; if missing/unresolved → assume the more stringent row (`ASSUMED`, flagged) or `handoff` to complete matrix, then **return here**. HAC Class **4651** is FM-specific — do not mint on AXA/`none`.

### 3.3 Classify the 3-D envelope (open vs contained)

Datum: **AFF**. Record `h_ceiling_ft` (FM cap **30 ft** — DS 5-32 §2.4.3.3.1.1.C / §2.2.5.2); lid; overhead runs; plenums. Typical 5–8 ft joists **fail** DS 2-0’s unobstructed gate → hall is **obstructed construction** under FM. A hard-lid is unobstructed **by inspection**. Flag it; do not turn it into a channel-layout hydraulic.

**Open hall:** skip path election. Still run deflector, overhead obstruction, concealed EC, spacing window.

**Contained hall:** FM DS 5-32 §2.4.3.5 covers **hot-aisle, cold-aisle, and hot-collar**. Same three paths.

### 3.4 Elect the HAC ceiling path (the load-bearing fork)

FM DS 5-32 **§2.4.3.5 (Jan-2026, pp.20–21)** gives **three grounded paths** and **one prohibition**.

| Path | When | Ceiling array | Extra heads | Cite |
|---|---|---|---|---|
| **1 — Protect beneath** | Solid containment ceiling | Ceiling QR still required | **Yes** — automatic protection **inside** the contained aisle | §2.4.3.5; §2.4.3.5.1.2 / .3 |
| **2 — Class 4651 drop-out** | FM-Approved **Class 4651** drop-out + ceiling-level QR | **Single** ceiling QR array | **No in-aisle sprinkler system** | §2.4.3.5.1.1.B: panels **≤15 ft (4.5 m) AFF**; **≤20 ft (6 m) panel-to-sprinkler** |
| **3 — Grated HAC** | Grated hot-aisle ceiling | Ceiling array **plus** grate-interface spacing | **≤4 ft (1.2 m)** at the ventilation-ceiling / plenum interface | §2.4.3.5.3.3 (p.21) + Fig. 3.3.3.4.B |

**Prohibition:** **Never** credit fusible-link panels, thermal-mechanical releases, or auto-releasing containment curtains as a substitute for sprinklers (DS 5-32 §2.4.3.5 / §3.3.3.4). If `lid_construction = curtain/fusible` → force Path 1 or a listed Path 2 panel.

**Class-number honesty:** §2.4.3.5.1.1.B names **Class 4651**; §3.3.3.4 names **Class 6451**. Both tokens stay visible. Specify **FM Class 4651 `[VERIFY 4651-vs-6451]`** against the **FM Approval Guide**. Do **not** pick 6451 as a silent correction.

There is **no FM default** among 1/2/3. Solid lid + Path 2 window fails → **Path 1**. Grated → **Path 3** (do **not** treat as DS 2-0 open-grid). Owner may **force Path 1** (raise).

**Code-layer fence on Path 2 — check the adopted code before electing drop-out .** FM listing does not override a code ban. **Maryland:** drop-out ceilings are **prohibited for new ceiling installations** statewide — State Fire Prevention Code COMAR 29.06.01 .08.ZZ (NFPA 1 §13.3.1.2.1) and .07.X (NFPA 101), naming NFPA 13 §9.3.11 / NFPA 13R §6.15 drop-out ceilings (KB *Ceilings and concealed spaces* ). **Baltimore County** restates it (Bill 14-21: `13:8.15.15.1` "shall not be used with sprinklers", existing grandfathered only if listing-maintained; `101:9.7.1.1.1` new ceilings; ). In a Path-2-banned jurisdiction: Path 2 → **not available**; elect Path 1 (solid lid, protect beneath) or Path 3 (grated). Other states: no ban held in the corpus → `[verify]` the adopted fire code / amendments; do not assume either way.

### 3.5 Pin the deflector, then prove Path 2 geometry

**Deflector datum — three-way conflict; most-stringent wins.**

| Instrument | Measurement | Floor | Ceiling (max below deck) |
|---|---|---|---|
| **FM DS 5-32 Jan-2026 §2.4.3.3.1.1.D** | **DEFLECTOR** | **1.75 in. (44 mm)** | **4 in. (100 mm)** |
| **FM DS 2-0 Oct-2021/Jan-2024** | **centerline of the thermal element** | **≥2 in.** | DS 5-32 overlay **displaces the loose 12 in. habit** |
| **NFPA 13-2025** | deflector | **1 in.** [CODE 2025 §10.2.7.1.1.1 / 2022 §10.2.6.1.1.1, unobstructed construction] | **12 in.** [CODE 2025 §10.2.7.1.1.1 / 2022 §10.2.6.1.1.1, unobstructed construction] |

**Binding number on an FM hall = DS 5-32’s 4 in. MAXIMUM.** Choose a deflector drop inside **1.75–4.0 in.**

```
deflector_ft_AFF = h_ceiling_ft − (deflector_drop_in / 12)
band_ok = (1.75 ≤ deflector_drop_in ≤ 4.0)
```

**Path 2 window:**

```
h_p ≤ 15.0 # DS 5-32 §2.4.3.5.1.1.B
(deflector_ft_AFF − h_p) ≤ 20.0
⇒ window = [max(0, deflector_ft_AFF − 20), 15.0]
```

If `lower_bound > 15.0` the window is **empty** → Path 2 **impossible** → Path 1. The ≤20 ft limb **binds first** as the deck rises.

### 3.6 Overhead obstruction schedule — two independent tests (do not blend)

**Test A — DS 2-0 least-dimension (FM DS 2-0 §2.5.2.5.4, p.89):** any object up to **4 ft (1.2 m)** wide, **LEAST dimension** parallel to the floor, **does not qualify as an obstruction**. Over **4 ft** (individual **or grouped**): **supplemental sprinklers under the object** (NFPA 13 also requires sprinklers under fixed obstructions over 4 ft wide [CODE NFPA 13-2022 §10.2.7.4.2; 2025 §10.2.8.2(6)]). Grouped if closer than **3× width** (§2.5.2.5.3).

**Preaction / wet-feed gate (company fence):** the no-calculation exemption (§2.5.2.5.5.2) requires **WET feed**. Company-elected **dry** or **DI** (and any comparison-only SI evidence) **fails gate (A)**. Technical honesty preserved: **SI is hydraulically sized as wet but the feed is not wet until the valve trips** — under company fence that SI path is **`comparison-only`**; under company dry/DI the same wet-feed fail applies as a geometry consequence. Every **over-4-ft** object becomes a **designed** supplemental system under **§2.5.2.5.5.3**: **at most FOUR** sprinklers, density with the **obstruction’s underside as the “ceiling height,”** **not** balanced with the ceiling. **Do not run that four-head tree here.**

**Checkerboard fence:** DS 2-0 §2.5.2.5.1.1 is **graphic-only**. This Skill **schedules the 4 ft / grouped / supplemental rules**. It does **not** claim a head-by-head checkerboard pass.

Do **not** import DS 2-0 **storage** obstruction **≤2 ft**, or DS 7-112 **3 ft / 10 ft²**, onto a DP hall. Do **not** conflate DS 1-12 melt-out HC-1 wet-only with Class 4651 Path 2.

**Test B — DS 5-32 elevated-tray offset / pressure (additive).** FM DS 5-32 Jan-2026 §2.4.3.3.1.1.F: **≥12 psi OR keep the sprinkler within 4 ft horizontal of the trays** — **and** address obstruction per **DS 2-0**. A 3 ft-wide tray needs **no sprinkler beneath it** (Test A pass) and **still owes** Test B.

**≥12 psi cannot be verified in this Skill.** Default compliance path = **≤4 ft horizontal offset**. Record ≥12 psi as the **unused alternative** unless a hydraulic Skill already proved remote-head pressure.

```
offset_to_centerline_ft ≤ 4.0
half_spacing_ft = S_ft / 2
if half_spacing_ft > 4.0:
 uniform_grid_does_NOT_satisfy_Test_B
 → schedule supplemental / shifted heads SP-C(o) at every tray/bus run
```

If a square-grid method check lands at 11.4 ft, half-spacing **5.70 ft > 4.0 ft** → the uniform grid **alone fails Test B**. That count is **layout-driven** and is **not** inside the density-area head count. Schedule the **rule**; do not invent the count.

### 3.7 Concealed-space EC map

**FM DS 5-32 Jan-2026 §2.4.3.4.1.1:** concealed spaces containing combustibles → **EC non-storage** at the **same 0.2 gpm/ft² over 2,500 ft² wet / 3,500 ft² dry**. Temperature: **nominal 135 °F wet / 165 °F dry** (sheet’s concealed-space **°C conversions are a known typo**). `[VERIFY]` an FM-Approved EC head **listed for dry/preaction** if `system_type` is preaction (company dry/DI).

**Fig. 2.4.3.1.2.1 negative terminal:** **non-combustible concealed space with no cables** → *“No concealed space fire protection recommended.”* Combustible construction **or** cables present → EC.

**DS 5-32 §2.4.3.4.1.1 is more stringent** than a generic HC-1 concealed-space read. Carry **separate schedule rows**; do not add concealed + ceiling flows. Concurrent remote-area is a **hydraulic question — not this Skill**.

Below-floor VEWFD omission (DS 5-32 §2.4.2.1.6) → **fa-asd-vewfd-data-hall-sampling-layout**.

### 3.8 Spacing / coverage window (schedule limits, not a CAD grid)

| Parameter | Value | Who governs | Cite |
|---|---|---|---|
| Max linear spacing | **12 ft (3.6 m)** | DS 5-32 (tighter than DS 2-0’s 15 ft) | DS 5-32 §2.4.3.3.1.1.E |
| Min linear spacing | **7 ft (2.1 m)** SC · **10 ft** EC | DS 2-0 | Table 2.5.2.3.1.1(b) |
| Area per sprinkler | **min 64 ft² (100 ft² EC) / max 130 ft²** | DS 2-0 | same |
| Path 3 grate interface | **≤4 ft (1.2 m)** | DS 5-32 | §2.4.3.5.3.3 |

```
S_max_ft = min(12.0, owner_cap_ft)
S_min_ft = 7.0 # SC; 10.0 if EC
A_max_ft2 = 130.0
A_min_ft2 = 64.0
# square-grid method check (optional, not a required layout):
S_square_ft = sqrt(A_max_ft2) # 11.40 ft; 11.4² = 129.96 ≤ 130
```

**130 ft² is the NFPA 13 Ordinary Hazard maximum** [CODE NFPA 13-2019/2022/2025 Table 10.2.4.2.1(b), Ordinary Hazard, all rows: 130 ft² max protection area, standard pendent/upright spray; pulls ], and FM DS 2-0 HC-2 also uses 130 ft² for the comparison; the most stringent governs. Do **not** multiply whole-hall area ÷ 130 as demand. **K-factor is out of scope** (DS 2-0 floors K5.6 SC / K11.2 EC at 0.2 — note as a floor, **do not pick a SIN**). **Sidewalls** require a flat, smooth, unobstructed ceiling ≤30 ft (DS 2-0 §2.5.3.1.1) — a containment hall with overhead bus/tray is **not** that ceiling.

Do not conflate Path 3 **≤4 ft** at the **HAC grate** with DS 2-0 **open-grid ceiling**. Do not conflate SI **wet demand area** with **wet feed** for the supplemental-head exemption (SI path = comparison-only under company fence).

### 3.9 Wet / preaction geometry interactions (consume STS; do not elect)

This Skill does **not** choose the interlock. Consume STS `wet`|`dry`|`DI` and record geometry consequences:

- Company dry/DI (and comparison-only SI evidence) **fails** DS 2-0 wet-feed supplemental exemption → over-4-ft objects → designed four-head systems (hydraulic tree, not here).
- Cross-zone + HAC + DI = stranded **“triple interlock.”** **Do not** trip the preaction valve on cross-zoned detection (DS 5-32 §2.4.3.2.1.3.2) → **preaction-releasing-c-and-e-soo**.
- Path 2 SOO limb only: S0 lid intact; S2 preaction on **pre-alarm**; S3 panels drop **before** QR fuse `[V]`; S4 ceiling QR discharges. Failures: panel fail-to-drop → open-room heads + ITM of the lid (`itm-design-for-testability`); tray shadow → SP-C(o) ≤4 ft, **not** ≥12 psi.
- Ceiling-plane airflow > **5 ft/s** → ventilation **reduction** on **VEWFD pre-alarm**. **Do not price +30 % into this Skill.** Sheet language grouping water-mist with sprinkler airflow remedies = **`comparison-only`** — never mist BOD (`PRACTICE REFUSED` if presented as BOD).
- Owner-mandated **DI does not change the HAC path**. It **does** change Test A economics and design **area** (other Skills). Split those rows.

### 3.10 Most-stringent union + Δ vs NFPA 13-2025

Union **per parameter**. Binding FM numbers: deflector **max 4 in.** vs NFPA **12 in.** [CODE 2025 §10.2.7.1.1.1 / 2022 §10.2.6.1.1.1, unobstructed construction]; spacing **max 12 ft / 130 ft²**; Test A **4 ft least-dimension**; Test B **12 psi or 4 ft** (FM-only additive); concealed **EC at hall density** when cables present. Drop-out as a concept exists in NFPA 13 — **section unpinned `[V]`**. Do **not** invent a 13-2025 Ch. 10 obstruction section.

If notes conflict, **most-stringent wins** and **both sources stay visible** (4651 vs 6451; DS 2-0 QR-wet-only vs DS 5-32 QR-for-dry in a DP room — occupancy sheet wins inside the hall).

---

## Output

A **containment / obstruction / concealed-space coverage schedule**. Write **only** to the caller-named path.

Minimum: Hard-scope / company-fence / status register; pinned editions; consumed packet + STS `wet`|`dry`|`DI` + matrix(when dual) + HC/OH + `system_type`; geometry statement (caller numbers only); path election + **no-curtain** prohibition; Path 2 window arithmetic if applicable; deflector drop; Test A and Test B on **separate columns**; wet-feed gate result under company fence; concealed-space rows (no summed gpm); spacing window (not coordinates); 3-layer table; Path 2 drop-out limb SOO; status + `[SYN]`/`[V]`/`[VERIFY]` register; checkerboard-graphics limitation stated; reciprocal `HAND OFF` rows.

Suggested tags: **SP-C** ceiling array; **SP-C(o)** supplemental at bus/tray; **SP-A** in-aisle (Path 1 only); **DOP-1** Class **4651 `[VERIFY]`**; **SP-G** grate interface (Path 3); **EC-CS** concealed plenums.

Do not emit pipe sizes, remote-area gpm, pump envelopes, ASD hole schedules, head (x,y,z) lists, CAD, mist BOD, foam BOD, rebuilt packet/matrix, or family election.

---

## Stop

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

1. Missing packet, STS `wet`|`dry`|`DI`, HC/OH, or density-area `system_type` → `unresolved`. 2. Dual-carrier with missing/unresolved matrix geometry/carrier/obstruction rows (complete matrix, then **return here** — do not Stop-away forever). 3. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. 4. `containment_type` or lid undetermined. 5. Ceiling > 30 ft on FM with no off-table path. 6. Path 2 requested but lid/ceiling heights missing. 7. Overhead distribution exists but widths/elevations not supplied. 8. Plenums exist but combustibles/cables not declared. 9. Caller asks for CAD, coordinates, a tree, or density×area `calcs`. 10. Caller asks to re-classify occupancy or re-size `q_spr`. 11. AXA XL / `none_pruner` / / / ARCHIVE. 14. Inventing a hall program from the worked package (36k / 26 / 10 / 11.4).

Also stop: treating ≥12 psi as proven; treating SI “sized as wet” as DS 2-0 **wet feed** (or as company BOD); treating a grated HAC lid as DS 2-0 open-grid; applying DS 7-112’s 3 ft trigger to hall bus duct; conflating DS 1-12 melt-out with Class 4651 Path 2; electing Path 2 drop-out where the adopted code bans drop-out ceilings for new work (e.g. Maryland) → re-elect Path 1 / 3.

---

## Citations (section AND edition)

**FM DS 5-32 January 2026:** §2.4.3.2.1.1.1 obstruction handed back to DS 2-0; §2.4.3.2.1.3.2 no cross-zoned detection; §2.4.3.3.1.1 QR / 0.2 / 2,500 wet / 3,500 dry / 30 ft cap / deflector **1.75–4 in.** / spacing **12 ft**; §2.4.3.3.1.1.F **≥12 psi or ≤4 ft**; §2.4.3.4.1.1 concealed EC; §2.4.3.5 three paths, Class **4651**, ≤15 ft AFF, ≤20 ft to sprinklers, no fusible-link; §2.4.3.5.3.3 grated ≤**4 ft**; §3.3.3.4 Class **6451** token (conflict); Fig. 2.4.3.1.2.1 nothing-recommended terminal. Sheet mist/airflow grouping (§3.5.2.3 lineage) = comparison-only — never mist BOD.

**FM DS 2-0 Oct-2021 / Jan-2024:** Table 2.5.2.3.1.1(b) 7–15 ft / 64–130 ft²; §2.5.2.5.4 **≤4 ft least dimension = not an obstruction**; §2.5.2.5.5.2 no-calc needs **WET feed**; §2.5.2.5.5.3 max FOUR heads, underside = ceiling.

**Maryland drop-out ban:** State FPC COMAR 29.06.01 (2025 code capture) .08.ZZ / NFPA 1 §13.3.1.2.1 and .07.X; Baltimore County Bill 14-21 (NFPA 1-2018 amendments) `13:8.15.15.1`, `101:9.7.1.1.1`.

**NFPA 13-2025:** Δ reference. Deflector [CODE 2025 §10.2.7.1.1.1 / 2022 §10.2.6.1.1.1, unobstructed construction]; 2025 spacing is §10.2.6 ; protection area / max spacing by hazard [CODE NFPA 13-2019/2022/2025 Tables 10.2.4.2.1(a) to (d), pulls ]; obstruction rules held: three-times rule (max clear distance 24 in.) [CODE NFPA 13-2022 §10.2.7.3.1.3 / 2025 §10.2.8.3.1.4]; sprinklers under fixed obstructions over 4 ft wide [CODE NFPA 13-2022 §10.2.7.4.2; 2025 §10.2.8.2(6) [CODE NFPA 13-2025 §10.2.8.2(6)]; ≤4 ft wide needs no sprinklers below only where Table 10.2.8.2(a)/(b) and Figure 10.2.8.2(a) are maintained (§10.2.8.2(7)); Tables 10.2.8.2(a) (US) and 10.2.8.2(b) (SI) now held in full, 14 rows each, e.g. (a) "Less than 1 → 0" … "7 or more → 35 or less" [CODE NFPA 13-2025 Table 10.2.8.2(a)/(b)]; Figures 10.2.8.2(a)–(d) are PNG-only, so read the dimensions A/B from the figure and do not transcribe them as text]. Ch. 10 **directional `[V]`** for the rest. Enforced pin on unamended 2024 I-Codes = **NFPA 13-2022**.

---

## Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance` / comparison-only (preserve SI≠wet-feed technical as comparison-only). Foam prohibited. Mist = `PRACTICE REFUSED`. Status every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist). Upstream (packet optional; gaps → `ASSUMED`): packet + STS + fork + density (+ matrix geometry/carrier/obstruction when dual — consume+return). **NO PLACEHOLDER.**
2. Three-layer, most stringent, PER PARAMETER. Owner may force Path 1, tighten spacing, or require heads under objects FM would exempt. Raise, never lower.
3. Delta vs NFPA 13-2025 on obstruction, concealed, drop-out, and deflector — **not** density numbers. Directional `[V]` where Ch. 10 is unmined.
4. Show-and-verify: deflector elevation, Path 2 window, grouped widths, half-spacing vs 4 ft.
5. Honesty: checkerboard graphics are **not** in this output. ≥12 psi is **not** proven here. 4651 vs 6451 stays visible. Worked-package 36k / 26 ft / 10 ft / 11.4 ft are **method**, not this job — IN SI spine = comparison-only.
6. Reciprocal handshakes with correct peer folder IDs; do not restamp peers. Caller-path-only.

---

## Not this Skill

| Work | Where it lives |
|---|---|
| IBC / OH / HC | `occupancy-hazard-fork` — **consume only** |
| `q_spr`, hose, duration, 2,500→3,500 | `density-area-dry-increase` — **consume only** |
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume only**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier per-parameter authorship (geometry/carrier/obstruction) | `most-stringent-basis-matrix` — **consume**, then return here |
| Assignment packet authorship | the input packet — **consume only** |
| Return-sampling plane / 60-ACH interlock sizing | `fa-asd-vewfd-data-hall-sampling-layout` |
| Releasing C&E / full SOO | `preaction-releasing-c-and-e-soo` (this Skill only writes the **drop-out limb**) |
| Dry/DI delivery clock ≤30 s | `dry-preaction-water-delivery-screen` |
| Path 2 lid fail-to-drop ITM intervals | `itm-design-for-testability` |
| Multi-zone PA↔cell alignment | `multizone-preaction-zone-alignment` (consumes cell geometry; does **not** elect Path 1/2/3) |
| Pump / hydrant | `pump-envelope` / `hydrant-supply-curve` — **Not-this** (preserve) |
| Node-by-node tree, ≥12 psi **proof**, four-head supplemental calcs | hydraulic-tree Skill (not written) |
| Head (x,y,z), CAD, RCP | **Stop** |

---

## Check before you finish

0. **Hard scope + status register first.** STS = wet|dry|DI (consume — do not elect). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Packet (optional) + STS + fork + density present; matrix geometry/carrier/obstruction when dual (consume+return). Emit status skeleton (§1.4). **NO PLACEHOLDER.**
1. Confirm remaining inputs; Stop tests. 2. Pin editions. 3. Consume occupancy-hazard-fork and density-area (already gated). 4. Classify open vs HAC. 5. Elect Path 1 / 2 / 3 / open; no-curtain prohibition; Path 2 → **4651 `[VERIFY]`**. 6. Show-and-verify deflector band and Path 2 window. 7. Schedule Test A and Test B separately; wet-feed gate under company fence. If `S/2 > 4` → SP-C(o) rule. 8. Map EC vs nothing-recommended. 9. Spacing window 7–12 ft / 64–130 ft². No coordinate dump. 10. 3-layer union; directional Δ vs 13-2025. 11. Path 2 drop-out limb SOO only. 12. Close status register; reciprocal `HAND OFF` rows (correct peer IDs). 13. Write **only** to the caller-named path.
