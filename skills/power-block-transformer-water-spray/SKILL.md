---
name: Power-block transformer water spray
description: >-
 use this when an outdoor oil-filled transformer yard (or diesel genset/fuel
 apparatus branch) needs apparatus water-spray demand, separation/barrier, and
 oil containment — against company wet|dry|DI only on room hand-offs (consume
 STS; this Skill does not elect family); packet optional (STS when room +
 matrix special-hazard/dual when dual + occupancy when rooms consumed when
 present, else ASSUMED and flagged — never a stop); SI/NI-as-BOD → Stop RFI-variance (comparison-only); foam prohibited;
 mist PRACTICE REFUSED; water-spray ≠ mist; status register every run — not
 white-space density×area, not DS 7-32 as transformer spray, no silent
 Voil/L×W×H/outline MVA (state ASSUMED + why), not clean-agent or foam/mist BOD, not CAD.
---
# Power-block transformer water spray

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** The building sprinkler basis stays wet pipe, dry pipe, or double-interlock preaction. Apparatus water spray for an outdoor oil-filled transformer is in scope here. Foam, clean agent, water mist, a building deluge system, and single-interlock or non-interlock preaction are out of scope as the basis of design. If one of those is requested as the basis of design, record it and stop. Do not size those systems here. Water spray is not water mist. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record. Do not claim a stamp.

Reusable DC fire-protection recipe. **This Skill sizes OUTDOOR OIL-FILLED TRANSFORMER (and related diesel/fuel apparatus) FIXED WATER-SPRAY demand, separation/barrier geometry, and oil containment.** It runs after the space has already been classified as power-block / outdoor apparatus (not white-space HC). It does **not** elect the hall sprinkler/preaction family — it **consumes** STS `wet` | `dry` | `DI` when room hand-offs occur. It does **not** size white-space density×area. It does **not** redesign DS 7-32 ignitable-liquid operations as a whole. It does **not** CAD. It does **not** design foam, mist, CAF, or clean agent.

**Core thesis:** Classify the **object** first, then pick **apparatus-vs-room**. Outdoor oil-filled transformers are **apparatus-centric** (separation → barriers → water spray). Standard MV/LV switchgear + dry-type transformers are **room-centric** (detection + de-energization + room sprinkler/preaction — **no deluge on the lineup**). Generators are **engine-plus-fuel** under NFPA 37 / FM DS 5-23 arrangement, with density routed to **DS 7-32** — not a “DS 5-23 density.” Water spray is **NFPA 15 / FM DS 5-4 + DS 4-1N method**, not NFPA 13. **Water-spray ≠ mist** — DS 4-1N is not DS 4-1 / DS 4-2.

**Design practice:** three-layer most-stringent per parameter (density, simultaneous demand, standoff/hardware, containment volume, hose/duration, separation vs spray election). Delta vs **NFPA 13-2025** is reported for any **room** protection hand-off; apparatus delta is vs **NFPA 15** (public reproductions `[V]` until licensed primary is in hand). Cite **section AND edition**. Show-and-verify. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD for company **sprinkler/preaction** on room hand-offs = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**; **water-spray ≠ mist**. Upstream (packet optional; gaps → `ASSUMED`): the optional input packet + STS `wet`|`dry`|`DI` **when room hand-off** + `occupancy-hazard-fork` **when rooms** (+ `most-stringent-basis-matrix` **special-hazard / dual-carrier** rows when dual — **consume and return here**). Caller-path-only. **NO PLACEHOLDER.** Clean agent = **hand-away only** (company does not design — company scope). Generic — do not copy outline MVA / gal / L×W×H as defaults. Owner may **raise, never lower**.

**Honesty — worked package is partial.** Outline spine: power-block transformer/generator special-hazard. Matching worked package exists for **transformer water-spray sizing** — consume **method and formulas**, not synthetic 6,000 gal / 25×10×12 ft / 981 gpm envelopes. a synthetic generator yard outline FOAM REFUSED / mist REFUSED spine = company-aligned corroboration — not a license to invent yard defaults. FM DS 5-4 and DS 4-1N are **primaries in the codebook** — cite them, not the deep-research report.

Write the sizing package **only** to the path the **caller** names. Do not write outside the caller-named output. Do not retrieve a job index. Do not run white-space `_calc`. Do not CAD.

Cite the section and the edition. Do not invent a section.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (water-spray-adapted — consumes STS on room hand-offs, does not elect)

This Skill owns **apparatus water-spray demand + DS 5-4 separation/barrier geometry + oil containment** for outdoor oil-filled transformers (and related diesel/fuel apparatus branch). Controlling company BOD for **sprinkler/preaction** families on room hand-offs = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI (room path) | `suppression-technology-selection` (**consume** when room hand-off — do not elect here) |
| Apparatus water-spray + separation/barrier + oil containment | **This Skill** |
| Dual-carrier per-parameter union (special-hazard / dual-carrier rows) | `most-stringent-basis-matrix` (**consume**, then **return here**) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- Synthetic SI room spines that touch transformer / switchgear rooms (method only)

**This Skill does not elect hall families.** It **consumes** the optional input packet, the STS token `wet` | `dry` | `DI` **when a room hand-off** is in scope, occupancy-hazard-fork **when rooms** are in scope, and — when carrier = `dual` — matrix **special-hazard / dual-carrier** rows. Water spray itself stays **apparatus record/handoff** on STS (STS already names this Skill inbound). Then it runs the object fence and emits the water-spray + containment package.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family on a room hand-off / packet:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue spray arithmetic as if SI/NI were company-elected BOD.
6. SI/NI (including synthetic SI room spines) may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler / preaction | Permitted when elected upstream via STS on **room** hand-offs | Record room consequences under that BOD; do not elect |
| Apparatus fixed **water spray** (NFPA 15 / DS 5-4 + DS 4-1N) | **In scope here** | Size demand + geometry + containment |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water / CAF | **Prohibited** | **Stop**; do not accept/design foam BOD — even when DS 5-4 indoor alternatives / indoor `Vcontain` formula / DS 7-32 §2.4.9 / AXA drainage→agent foam path surfaces |
| Water mist | **`PRACTICE REFUSED`** | Record DS 5-4 mist alternative / DS 7-32 §2.4.9 / DS 4-2 language as **sheet evidence** only; do **not** design/accept mist as BOD. **Water-spray ≠ mist.** |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent (company scope); Not-this may hand away — never company BOD here |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** **Water-spray ≠ mist** (DS 4-1N ≠ DS 4-1 / DS 4-2). Fence foam/mist **before** any indoor-alternatives / special-protection reading. Clean agent = hand-away only — never company BOD here. Prefer dry-type / room wet\|dry\|DI when the company path fits.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Object fence apparatus vs room; geometry-first DS 5-4 | System-family election (`suppression-technology-selection`) |
| Apparatus spray 0.30 + wall 0.20 + Aprot / Qws / simultaneous | Occupancy re-class (`occupancy-hazard-fork`) — consume when rooms |
| Hardware + DS 4-1N method floors; hose tiers; outdoor Vcontain | White-space density×area (`density-area-dry-increase`) |
| Campus Qd hand-off; de-energize-before-water C&E interface | Dual-carrier BOD authorship (matrix — consume+return) |
| Status register + reciprocal handshakes | Invent Voil / L×W×H / outline MVA / worked 6,000 gal / 981 gpm; foam / mist / CAF / clean-agent as company BOD; switchgear lineup deluge; DS 7-32 as transformer spray |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet / STS(when room) / matrix(when dual) / occupancy(when rooms), **(c)** object-class fence, **(d)** geometry-first gate, **(e)** Aprot / Qws / +20%, **(f)** simultaneous fork, **(g)** hardware + DS 4-1N floors, **(h)** hose / containment / SPCC, **(i)** campus Qd, **(j)** Δ layers, and **(k)** mist/foam/clean-agent if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling object fence + editions + demand math supported by caller Voil / L×W×H / opened DS 5-4 / 4-1N already closed |
| `provisional` | Directionally pinned; NFPA 15 licensed / simultaneous 0.30-vs-0.20 / SPCC final / DS 4-1N currency hole flagged `[V]` — **never silent `grounded` on invented Voil / L×W×H / outline MVA / worked 981 gpm** |
| `unresolved` | STS(when room) / matrix(when dual) / occupancy(when rooms) / object class / Voil / envelope / Carrier not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, synthetic SI room spines, DS 5-4 foam-water·CAF·mist indoor alternatives, DS 7-32 mist wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; hydrant/pump Qd; room density; commissioning / ITM; power-isolation; clean-agent hand-away) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as controlling medium or elective special-protection family — record and refuse |

**Invented Voil / L×W×H / outline 48 MVA / worked 6,000 gal / 25×10×12 / 981 gpm as defaults → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Outline + worked spray-sizing package = **`[SYN]` method** only (geometry → Aprot → Qws → simultaneous → containment structure). Do **not** copy 6,000 gal / 25×10×12 / Aprot 1,090 / 981 gpm / outline ~48 MVA as project defaults. a synthetic generator yard FOAM REFUSED / mist REFUSED spine = company-aligned corroboration. Licensed NFPA 15 apparatus pins / simultaneous A/B fork / packet short-form `transformer` remain intentional Absent / `[V]` / refuse invent. **NO PLACEHOLDER.**

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent Voil, L×W×H, or outline MVA. Do not treat SI/NI as company BOD. Do not elect foam/mist/CAF/clean-agent.

| Input | Required | Notes / Stop |
|---|---|---|
| the optional input packet (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`special-hazard` / `suppression` / `bod`) — do not invent a new `transformer` / `water-spray` packet token this run; do not rebuild; do not retrieve a job index. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes when room hand-off** | From `suppression-technology-selection`. Required when switchgear / dry-type / Approved-fluid indoor / room path is in scope. Missing when room → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. Pure outdoor apparatus-only run with no room hand-off: record STS water-spray handoff posture; still refuse SI/NI/foam/mist as BOD. |
| **Occupancy-hazard-fork schedule** | **yes when rooms** | Already pinned **or** explicitly deferred with return path when room objects are in scope (occupancy already routes transformers here inbound). Missing when rooms with no deferral → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not re-classify here. |
| **Consumed `most-stringent-basis-matrix` special-hazard / dual-carrier rows** | **yes when dual-carrier** (or when those rows exist) | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever as if matrix replaces this Skill. Unresolved controlling special-hazard row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **Object class** | **yes** | `outdoor oil-filled transformer` / `indoor liquid-filled transformer` / `diesel genset / fuel apparatus` / `switchgear or dry-type room` (fence → hand-off). Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Fluid / Approval status** | **yes** for transformers | Mineral oil gal **or** FM Approved fluid; **FM Approved transformer** (Std **3990**) vs Approved **fluid only** (glossary trap). Unknown → `[V]`, no “no FP needed” claim. |
| **Voil per unit (gal)** | **yes** for liquid-filled | Caller-surveyed or `[SYN]` flagged estimate. Drives spacing tier, hose tier, containment perimeter. |
| **Protected envelope L×W×H (ft)** | **yes** if spray elected | Bounding box of tank + radiators + conservator (excl. bushings). Missing → **not a Stop**: proceed with a stated `ASSUMED` envelope (value + why), flagged; demand math built on it is ASSUMED-based. |
| **Bank arrangement** | **yes** if multi-unit | Row count / adjacency — drives simultaneous origin+adjacent. |
| **Wall / building exposure** | **yes** | Distance to nearest wall type (2-hr / noncombustible / combustible) measured from **inside edge of containment**. |
| **Carrier** | **yes** | FM / AXA / UFC / n/a. Dual → matrix rows above. |
| **AHJ 13 / 15 editions** | **yes** to cite | Room delta baseline **13-2025**. Apparatus code floor **NFPA 15** — licensed text often `[V]`; note **15-2027** exists; NFPA 15-**2027** acceptance held [CODE NFPA 15-2027 §10.2 flushing (≥10 ft/s), §10.3 hydro per NFPA 13, §10.4.2.1 actuation valve operates within 40 s, pull 15-01; the 2027 acceptance text is the held acceptance pin]. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional: owner remote-impounding / leak-monitoring raise; outdoor weather (wind → large-capacity nozzles); campus supply curve already run (consume residual — do not rebuild); detection/releasing panel identity (C&E hand-off).

**Do not invent** Voil, L×W×H, or copy outline ~4,000–8,000 gal / 48 MVA / worked 6,000 gal / 25×10×12 / 981 gpm as defaults. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the optional input packet | Packet context — **optional** (consume when present) (nearest `special-hazard` / `suppression` / `bod`) | Rebuild the packet; invent a `transformer` / `water-spray` component token; retrieve a job index |
| `suppression-technology-selection` | Elected wet/dry/DI **when room hand-off**; water-spray already named inbound as apparatus handoff | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD; redesign water-spray inside STS |
| `occupancy-hazard-fork` | Occupancy / space class — **required when rooms** (already routes transformers here) | Re-classify occupancy here; skip room hand-off when object fence opens |
| `most-stringent-basis-matrix` | **Special-hazard / dual-carrier** rows when dual | Rebuild dual-carrier BOD; Stop-away forever; invent spray numbers |
| `density-area-dry-increase` | Room / DS 7-32 density hand-off receiver (not yard deluge) | Emit yard 0.30 as white-space HC; treat water spray as 13 density×area |
| `hydrant-supply-curve` / `pump-envelope` | Receive campus `Qd` + duration | Freeze pump nameplate / rebuild supply curve here |
| `commissioning-ist-acceptance-packet` | Deluge / NFPA 15 commissioning texture | Invent acceptance criteria as code |
| `itm-design-for-testability` | Water-spray / deluge ITM handoff | Emit ITM interval calendar here |
| `power-isolation-disconnect-control` | De-energize-before-water twin | Rewrite isolation architecture here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS(when room), occupancy(when rooms), or dual-carrier special-hazard rows (when required) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Handoffs.** Do **not** rewrite peers. Note: `suppression-technology-selection` and `occupancy-hazard-fork` **already name this Skill inbound** (Water spray → handoff; Transformer apparatus → route here).

| Peer | They own | This Skill owns |
|---|---|---|
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status; water-spray = apparatus handoff (names this Skill) | **Consume** STS when room; mist = `PRACTICE REFUSED`; foam prohibited; water-spray ≠ mist |
| `occupancy-hazard-fork` | Occupancy / HC/OH pin; transformer apparatus → route here (names this Skill) | Consume when rooms; do not re-classify; switchgear stays room/DS 5-19 |
| `density-area-dry-increase` | Density×area / dry increase; water-spray / transformer / gen-fuel = handoff-only | Hand room / DS 7-32 density off; do **not** emit yard deluge as 13 HC |
| `most-stringent-basis-matrix` | Per-parameter union / special-hazard·dual-carrier rows | **Consume only** when dual — then design spray package **here** |
| the optional input packet | Assignment context (`special-hazard` / `suppression` / `bod`) | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `hydrant-supply-curve` | Campus supply vs demand at BOR | Emit `Qd` + duration; do not rebuild curve |
| `pump-envelope` | Pump rated flow/pressure; ≥2000 gpm one-pump-out texture lives on DS 4-1N cite here | Emit demand into pump Skill; do not freeze nameplate |
| `commissioning-ist-acceptance-packet` | Deluge / NFPA 15 commissioning | Name commissioning texture; refuse invent criteria as code |
| `itm-design-for-testability` | Water-spray / deluge ITM | Name ITM of spray system; do not emit interval calendar |
| `power-isolation-disconnect-control` | De-energize / disconnect architecture | De-energize-before-water twin; coordinate, do not rewrite |
| `combustion-air-and-hall-free-area` | DS 5-23 gen combustion-air neighbor | **Not-this** unless scoped |
| `ess-isolation-venting-and-duration` | ESS isolation / venting | **Not-this** unless scoped |
| `storage-staging-sprinkler-design` | Commodity / storage sprinkler | **Not-this** |
| `preaction-el-el-trim-election` / room preaction peers | Preaction trim / room package | **Not-this** unless room hand-off scoped; company BOD still wet\|dry\|DI |
| out-of-scope clean-agent work | Clean-agent concentration / enclosure | **Hand-away only** — company does not design clean agent |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — suppression-technology-selection: wet|dry|DI election on room path. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited; water-spray ≠ mist. Peer already names this Skill inbound.`
- `HAND OFF — occupancy-hazard-fork: occupancy pin when rooms. Peer already routes transformers here.`
- `HAND OFF — most-stringent-basis-matrix: special-hazard/dual-carrier rows when dual. Consume; return here after.`
- `HAND OFF — the optional input packet: optional (nearest special-hazard/suppression/bod). Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — density-area-dry-increase: room / DS 7-32 density — not yard deluge.`
- `HAND OFF — hydrant-supply-curve / pump-envelope: consume campus Qd + duration from here.`
- `HAND OFF — commissioning-ist-acceptance-packet / itm-design-for-testability: deluge / NFPA 15 commissioning + ITM.`
- `HAND OFF — power-isolation-disconnect-control: de-energize-before-water twin.`
- `HAND OFF — mv-switchgear-room-package: the DS 5-19 switchgear-room package (detection, upstream breaker outside the room, room sprinkler/preaction). This Skill only fences switchgear as room-centric and does not build that package.`
- `HAND OFF — combustion-air / ess / storage / preaction: Not-this unless scoped.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before object class / editions / Aprot arithmetic:

1. Confirm company fence: on room hand-offs STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only. Restate **water-spray ≠ mist**.
2. Check upstream (packet optional): packet if present (optional); STS present when room; occupancy present when rooms; matrix special-hazard/dual rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix·occupancy / object fence / geometry / Aprot·Qws / simultaneous / hardware / hose·containment / campus Qd / Δ (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER.** anywhere in the run.

### 3.1 Pin editions

| Instrument | Role | Shop pin |
|---|---|---|
| **FM DS 5-4** *Transformers* | Apparatus density, wall spray, standoff, simultaneous rule, hose tier, indoor room density fork, spacing/barrier tables | **July 2019 / Interim Rev. October 2020** — **primary** |
| **FM DS 4-1N** *Fixed Water Spray Systems* | Method: nozzle pressure floor, pipe, auto preference, ≥60 min remote xfmr duration, geometry | **May 2010** — **primary**; ⚠ adopts **NFPA 15-2001** — re-pin before sealed use |
| **FM DS 5-19** | Switchgear **room** package — **not** apparatus deluge | **Oct 2020 / IR Jan 2024** |
| **FM DS 5-23** | Generator/fuel **arrangement** (no density on sheet) | **Jul 2020 / IR Jan 2022** |
| **FM DS 7-32** | Gen-room / non-Approved indoor liquid density, containment, drainage | Primary held — cite Table 2.4.3 for diesel gen rooms; **do not** use this Skill as a full 7-32 redesign; fence foam/mist (§2.4.9) before any special-protection reading |
| **FM DS 5-31** | Cable-only room density 0.20/3,000 | **Jan 2020 / IR Oct 2025** |
| **FM DS 2-0** | Water-spray equipment install pointer from DS 5-4 | **Oct 2021 / IR Jan 2024** |
| **NFPA 15** | Code-floor water spray | Now held: transformer **0.25 gpm/ft²** of the rectangular-prism projected area + **0.15** on nonabsorbing ground; complete impingement; supply design flow + **250 gpm hose for 1 h** [CODE NFPA 15-2022 §7.4.4.1, §7.4.4.3.1, §7.4.4.3.6, pull 15-02]; exposure 0.25 gpm/ft², ≤12 ft rundown spacing [CODE NFPA 15-2022 §7.4.2.1–7.4.2.2, pull 15-03]; general range 0.15–0.50 [§7.2.1.3]. NFPA 37-2024 §11.4.5.1 (0.30/2,500, 100 ft²/head, 20 ft of engine/fuel/lube) is engine-enclosure only — not a transformer/yard distance [pulls 15-02, 15-03]. 2024/2027 currency `[V]`. |
| **NFPA 37** | Engine clearances / gen spray secondary | **2024 + TIA 24-1**; secondary vs DS 7-32 demand area |
| **NFPA 30 / NFPA 37** | Fuel tank floor | Separate / bulk tanks: NFPA 30-2024 Ch. 22, §22.10, §22.11 [CODE, pull 30-01]. Engine fuel tanks are outside NFPA 30 scope [CODE NFPA 30-2024 §1.1.2(9), pull 30-03]; their floor is NFPA 37-2024 Ch. 6: construction per NFPA 30 or listed §6.1, ≤660 gal unless in a room by themselves §6.3.2.2 (any size in an engineered engine room, §6.3.2.2.1), containment ≥ largest tank within structures §6.3.2.4 [CODE, pull 37-01]. Verify with engineer of record (owner/insurer layering): conservative assumption = apply NFPA 37 Ch. 6 and, where the owner or insurer invokes them, NFPA 30 Ch. 22 and FM DS 7-32 (tank clauses not pulled `[V]`); take the larger. Property-line distances not pulled; 2027 `[V]` |
| **NFPA 13-2025** | **Room** sprinkler/preaction method only (hand-off) | Delta baseline for rooms — **not** apparatus spray |

Cite the section and the edition. Do not invent a section.

**Do not cite FM DS 1-45** (no current catalog sheet). **Do not confuse** DS 4-1N (water spray) with DS 4-1 / DS 4-2 (mist) / DS 4-0 (umbrella routing). **Water-spray ≠ mist.**

### 3.2 Object fence — apparatus vs room

| Object | This Skill | Hand-off |
|---|---|---|
| Outdoor oil-filled transformer | **In scope** — geometry-first, then spray + containment | Campus Qd → `hydrant-supply-curve` / `pump-envelope` |
| Indoor liquid-filled, **FM Approved fluid** | Indoor sprinkler **0.20 gpm/ft² over entire room** (DS 5-4 §2.2.3) — record; detail room package elsewhere under company wet\|dry\|DI | Room preaction / `density-area-dry-increase` as needed; consume STS |
| Indoor liquid-filled, **non-Approved fluid** | DS 5-4 routes **entire** design + containment + drainage to **DS 7-32** — **Stop** on inventing a 0.30 indoor room density | DS 7-32 path — not white-space HC; fence foam/mist before special-protection |
| Dry-type / gas-insulated indoor | No liquid hazard — noncombustible room + room sprinkler/preaction (company wet\|dry\|DI) | Room Skills; DS 5-4 §2.2.2.1 prefers dry-type |
| **MV/LV switchgear** | **FENCE: room-centric (DS 5-19)** — smoke to constantly attended location; de-energize / upstream breaker outside room; room sprinkler/preaction; **no apparatus deluge on the lineup** | Switchgear room package / `occupancy-hazard-fork` row; consume STS |
| Diesel genset enclosure | Arrangement per DS 5-23; density per **DS 7-32** (typ. 0.30 over 4,000–6,000 ft² for FP<200°F) + NFPA 37 secondary 0.30/2,500 cross-check | Gen/fuel note; campus Qd hand-off; combustion-air neighbor = Not-this unless scoped |
| Bulk fuel yard | NFPA 30 floor + FM DS 7-88 dike/impounding | Fuel note — not this Skill’s core math |

**FM Approved transformer trap:** Approval Std **3990** → fire frequency reduced enough that **FP not necessary** and wall/neighbor separation drops to **3 ft** (DS 5-4 §3.3). An FM Approved **fluid** in a **non**-Approved transformer buys far less (5–50 ft) — glossary: fluid Approval ≠ transformer Approval.

**Indoor alternatives honesty (DS 5-4 / KB / DS 4-1N):** when sheets surface foam-water / mist / CAF / CO₂-gaseous as indoor alternatives, record as **sheet evidence only** → apply company fence → **Stop** / `PRACTICE REFUSED` / clean-agent **hand-away** — do **not** elect or design those agents here. Prefer dry-type / room wet\|dry\|DI when in company practice.

### 3.3 Parameters, separately (three-layer union)

| Parameter | Election | Union |
|---|---|---|
| **A. Separation vs spray** | Meet DS 5-4 spacing/barrier **or** provide automatic spray | Geometry-first; owner/insurer may still demand spray when geometry clears |
| **B. Apparatus density** | gpm/ft² on transformer surfaces (excl. underside) | **max(NFPA 15 floor `[V]`, FM 0.30, owner)** — FM usually wins |
| **C. Wall / exposure density** | gpm/ft² on exposed building wall | FM **0.20** over Table-6 Y×Z coverage when wall-spray alternative elected |
| **D. Simultaneous demand** | Origin + adjacent | FM: size system **and** water supply for fire-origin + adjacent on each side **simultaneously** |
| **E. Hardware / method** | Standoff, no top/vent piping, no bushing spray, nozzle pressure | Union of DS 5-4 hardware + DS 4-1N method floors |
| **F. Containment** | Vcontain outdoor/indoor | FM formulas; SPCC / 40 CFR 112 sized **separately** (often larger); indoor foam-water/CAF/mist terms = **formula evidence only** — not company election |
| **G. Hose + duration** | Tiered by fluid/volume | FM §2.3.2.3 tiers; DS 4-1N remote xfmr ≥**60 min** |

### 3.4 Geometry-first gate (DS 5-4)

Decision sequence (DS 5-4 §2.3.1.1.1 alternatives): plain separation · 2-hr barrier · 3-hr barrier at ≥5 ft · spray on transformer · spray on wall. Canonical spacing Tables 5/6/7/8 + indoor Table 4 live in the **transformer rooms and outdoor transformer siting** note — **do not maintain a second copy here**. Headlines:

- Distances measured from **inside edge of containment** — 5 ft (≤1,000 gal) / 8 ft (>1,000 gal) perimeter **stacks on** tabulated separation.
- FM Approved transformer: **3 ft** to wall/neighbor; FP not necessary.
- Non-Approved liquid: **5–100 ft** to wall, **5–50 ft** to neighbor by volume tier.
- If Table 8 unmet → **2-hr barrier** between transformers extending **1 ft vertically + 2 ft horizontally** beyond fault-pressurizable components.
- Choosing barrier or spray alternatives can trigger **Table 7 roof radiant** check — a building is only “not exposed” at any oil volume when ≥**50 ft** tall (single-story hall fails).
- Spacing tables = **fire-exposure** control, not blast control (§2.3.1 preamble).

If geometry fails **or** carrier/owner demands spray → continue to §3.5.

### 3.5 Apparatus water-spray demand (DS 5-4 §2.3.2 + DS 4-1N method)

**Density pins (primary-confirmed):**

| Target | Density | Cite |
|---|---|---|
| Transformer surfaces (excl. underside) | **0.30 gpm/ft² (12 mm/min)** | DS 5-4 §2.3.2.1.A, Jul-2019/IR Oct-2020 |
| Exposed building wall (wall-spray alternative) | **0.20 gpm/ft² (8 mm/min)** over Table-6 Y×Z | §2.3.2.2.A |
| Code-floor surfaces (public) | **0.25** surfaces + **0.15** nonabsorbing ground | NFPA 15 reproductions — `[V]` |

**Area (exclude underside; exclude bushings):**

```
Arect_ft2 = (L×W) + 2(L×H) + 2(W×H) # per rectangular element
Aprot = Σ Arect over protected elements (tank, radiators, conservator; not bushings)
Qws_unit = 0.30 × Aprot # gpm per origin unit at FM density
```

**Show-and-verify — insurer delta vs 0.25 floor:**

```
delta_pct = (0.30 − 0.25) / 0.25 × 100 = +20%
# Example method only (not a default): Aprot 1,666 ft² → 500 gpm @ 0.30 vs 417 gpm @ 0.25
```

**Simultaneous demand (DS 5-4 §2.3.2.1 — size system AND supply):**

Fire-origin transformer + **adjacent transformers on each side** simultaneously. In a 3-unit row that is origin + two neighbors. If the sheet is silent on whether neighbors take full **0.30** or reduced exposure **0.20**, compute both and carry the **more conservative** for supply sizing; flag the fork `[V]` / `[inference]`.

```
Qws_simul = Qws_origin + Σ Qws_adjacent # controlling reading stated
```

**Hardware rules (DS 5-4 §2.3.2.1.C–F) — all required:**

- Components ≥ **18 in. (45 cm)** off the transformer
- **No** piping over the top / relief vents
- **No** direct bushing spray
- Equipment per **DS 4-1N**; installed per **DS 2-0**
- Two nozzle levels, upper and lower, **same standoff** (DS 5-4 Figs. 7–8; DS 4-1N Figs. FM-2/3)
- Wall spray: direct impingement **or** rundown with max **10 ft** between levels; nozzle spacing per **manufacturer tables**, not FM (§2.3.2.2.C–E)

**DS 4-1N method floors (May 2010) — do not skip after density calc:**

| Rule | Pin |
|---|---|
| Min nozzle pressure ≥**20 psi (1.4 bar)** | §2.2.1.10 |
| Outdoor orifice **<½ in.** → **30 psi (2.2 bar)** | §2.2.1.10 |
| Outdoor ≥½ in. → ≥20 psi | §2.2.1.10 |
| **Do not galvanize** open-nozzle extinguishment mains | §2.2.1.5 |
| Sch. **10** OK for **4/5/6 in.** with weld or Approved joints | §2.2.1.4 |
| Prefer **automatic** (valves locked/supervised open) | §2.2.1.3 |
| Remote transformer supply duration ≥**60 minutes** (aligns DS 5-4) | §2.2.1.9 |
| Systems ≥**2000 gpm**: size for **one pump out of service** | §2.2.1.8 |
| Prefer large-capacity nozzles on large/windy yards | transformer section §2.2.1.12 |
| Indoor oil-filled: weatherproof **or** curb+baffle+separate system per unit; else CO₂/gaseous path on sheet = **evidence only** → clean-agent **hand-away** — not water spray / not company BOD | §2.2.1.12 |

**⚠ Do not use Table FM-2 (open tank) as a transformer or gen-yard density.** Densities live on DS 5-4 / 5-31 / 7-32.

**Open-nozzle hardware gates (check on whatever nozzle is submitted — never freeze a SKU).** Corpus example: Viking Model E spray nozzles VK810–VK817, **F_062104 Rev 20.1 (2020-06-15)** p.4–6 (KB power-block note Run-409):
- **FM Approval can be finish-limited:** Model E FM Approval reads **brass only**; electroless-nickel (corrosion) finish = cULus only → on an FM-insured coastal / outdoor yard, a nickel nozzle is **not FM Approved** `[verify with Viking]`.
- **Small orifice → strainer:** K ≤ 3.2 (orifice < 3/8 in.) needs a pipeline strainer with **≤ 1/8 in. perforations** for FM Approval. Blow-off plugs carry no listing.
- **Vendor minimum ≠ floor:** the sheet's 10 psi (pendent / ≤ 2 ft axial only) defers to the AHJ → the DS 4-1N 20 / 30 psi floors above govern.
- Nozzles **normal to the surface, ≈ 2 ft standoff** (meets DS 5-4 ≥ 18 in.); pattern data are **still-air** → wind allowance outdoors; read max axial distance from the table, don't interpolate.

**Hose-stream allowance — TIERED (DS 5-4 §2.3.2.3)** where transformers expose buildings/equipment:

| Fluid / volume | Hose | Duration |
|---|---|---|
| FM Approved liquids, **or** ≤1,000 gal mineral oil | **250 gpm** | **1 hour** |
| **>1,000 gal** mineral oil in an individual transformer | **500 gpm** | **2 hours** |

Duration is a **water-supply** driver — check against campus supply curve and pump run time, not only containment volume.

### 3.6 Oil containment / drainage

**Outdoor (DS 5-4 §2.2.1.4–.5, §2.3.1.4 → IEEE Std 980 / DS 7-83):**

```
Vcontain_gal ≥ Voil + 60 × (Qhose + ΣQws_simul)
# Qhose per §2.3.2.3 tier (250 or 500)
# assume adjacent sprays on both sides run with origin
```

- Perimeter ≥ **5 ft** (≤1,000 gal) / **8 ft** (>1,000 gal) beyond fluid-containing components **including external coolers**
- Rainwater removal required
- **Separate** containment per transformer — no cross-run to adjacent equipment
- Environmental / **SPCC (40 CFR 112)** sized separately — DS 5-4 explicitly out-of-scopes it; often the larger number

**Indoor (formula evidence + company fence):** DS 5-4 uses `Vcontain ≥ Voil + 20 × Qspecial` where `Qspecial` on the sheet may reference foam-water / CAF / mist discharge rates. Treat that clause as **sheet evidence of formula variables only** — **do not** elect or design foam, CAF, or mist. Company fence: foam **prohibited**; mist **`PRACTICE REFUSED`**; prefer dry-type / room wet\|dry\|DI. Curb ≥ **3 in.** regardless of calc; separate per transformer.

### 3.7 Detection / releasing / de-energize C&E (interface only)

Automatic detection + releasing (**not** manual-only). C&E is as much **operational** as hydraulic: **alarm + de-energize / trip before or with** any water release into energized apparatus. Do **not** author the full matrix here — hand off to releasing C&E / `power-isolation-disconnect-control`; record the requirement and the upstream-breaker-outside-room posture for switchgear rooms.

Generator activation: fuel-stop valves close + ventilation shuts down (NFPA 37 interface). Combustion-air openings = Not-this unless scoped (`combustion-air-and-hall-free-area`).

### 3.8 Hand campus Qd to hydrant / pump Skills

Governing single event = **larger of** simultaneous transformer-spray demand **or** generator-spray demand, each + applicable hose. Carry `Qd` and duration into:

- **`hydrant-supply-curve`** / water-supply analysis — supply vs demand at BOR; hose deducted
- **`pump-envelope`** — rated flow/pressure selection
- Do **not** freeze a pump nameplate inside this Skill

```
Qd_event = max(Qws_simul_xfmr + Qhose_xfmr, Q_gen_spray + Qhose_gen)
Duration_min = per hose tier / DS 4-1N ≥60 / DS 7-32 as applicable
V_stored_needed ≈ Qd_event × Duration_min # campus tank Skill consumes
```

Flag all `[SYN]` if envelopes estimated.

### 3.9 Flags, deltas, honesty

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented Voil, L×W×H, nozzle count envelopes, outline MVA defaults |
| **`[V]`** | Licensed NFPA 15 current section numbers (except NFPA 15-2027 acceptance §10.2 / §10.3 / §10.4.2.1, pull 15-01); NFPA 30 property-line pins (Ch. 22 §22.10/§22.11 held, pull 30-01; NFPA 30-2024 §1.1.2(9) excludes liquids in the fuel tanks of stationary engines (pull 30-03)); NFPA 37 chapter pins; neighbor 0.30 vs 0.20 simultaneous fork; SPCC final volume; DS 4-1N currency vs NFPA 15-2001 |

**Δ vs NFPA 15 (apparatus):** 0.25→**0.30** (+20%); more conservative simultaneous-demand; 18 in. standoff / no bushing / no top piping; tiered hose 250@1 h / 500@2 h.

**Δ vs NFPA 13-2025:** apparatus spray is **not** a 13 density×area problem. Room protection (switchgear, dry-type, Approved-fluid indoor) uses 13 method under company wet\|dry\|DI — report that delta on the **hand-off**, not as if 13 governed the yard deluge. Do **not** take the NFPA 13 electrical-room sprinkler omission on high-availability DC work (UFGS/UFC + owner disallow).

**Pitfalls (do not):** deluge on metal-clad switchgear; quote **0.30** as indoor transformer-room density (indoor Approved fluid = **0.20 over entire room**; surviving 0.30 is **outdoor apparatus**); propose total-flooding clean agent for indoor transformers (FM removed Jul-2012) **or** design clean agent as company BOD (company scope hand-away only); confuse Approved fluid with Approved transformer; flat 500 gpm hose ignoring the 1 h/2 h tier; Table FM-2 as yard density; skip ≥20/30 psi nozzle floor after density calc; release water before electrical isolation; treat double-wall as containment (DS 5-23); elect foam/mist/CAF from indoor `Vcontain` / DS 5-4 alternatives; conflate water-spray with mist (DS 4-1N ↔ DS 4-2).

**Do not** paste outline 6,000 gal / 25×10×12 / 981 gpm as defaults. Worked package = method only.

---

## Output

A **power-block apparatus water-spray + containment package** (markdown).

**Write only to the caller-named path.** If unnamed, return and stop.

**Minimum contents:**

1. Status register (§1.4) + Hard-scope fence result (wet\|dry\|DI consume when room; SI/NI/foam/mist posture; water-spray ≠ mist).
2. Upstream intake: packet + STS(when room) + matrix(when dual) + occupancy(when rooms).
3. Edition-pin block (DS 5-4 Jul-2019/IR Oct-2020; DS 4-1N May-2010; DS 5-19/5-23/7-32 as touched; NFPA 15 `[V]`; 13-2025 room delta).
4. Object-class fence statement (apparatus vs room; switchgear = DS 5-19 room-centric).
5. Geometry-first gate result (spray required / substituted / owner-forced).
6. Aprot show-and-verify + Qws @ 0.30 + Δ vs 0.25 (+20%).
7. Simultaneous origin+adjacent Qws_simul with fork stated.
8. Hardware checklist (18 in.; no top/vents; no bushings; DS 4-1N pressure floors).
9. Hose tier + duration; containment Vcontain math (indoor foam-water/CAF/mist terms = evidence + fence); SPCC separate.
10. Campus Qd hand-off row to hydrant/pump Skills.
11. De-energize-before-water C&E interface note (hand-off, not rewrite).
12. Δ vs NFPA 15 and Δ vs NFPA 13-2025 (rooms only); `[SYN]`/`[V]` register; honesty line; reciprocal HAND OFF lines.

Do **not** emit: white-space density×area transcript, full DS 7-32 plant redesign, CAD, a job index retrieval, switchgear apparatus deluge, foam/mist/CAF/clean-agent BOD, rebuilt packet/matrix/STS, or writes outside the caller-named output.

---

## Stop

A missing input is not a stop. Proceed with a stated ASSUMED value (the value and why), flagged in the output and the status register. Company scope locks stay hard stops: single-interlock or non-interlock as the basis of design, foam, water mist, a building deluge system, and clean agent as the basis of design. Apparatus water spray for an outdoor oil-filled transformer stays in scope.

1. SI/NI (or other prohibited preaction) presented as **basis of design** on room hand-off / packet → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent / foam / mist as company BOD → Stop / hand-away only.
2. Missing the optional input packet → not a Stop (packet optional). Missing STS when room hand-off → `ASSUMED` (flagged), not a Stop. Missing matrix special-hazard/dual rows when dual → `ASSUMED` (flagged), not a Stop / handoff then return. Missing occupancy when rooms → `ASSUMED` (flagged), not a Stop.
3. Object class missing or is **switchgear/dry-type** and caller wants apparatus deluge — **fence**; hand to room package under wet\|dry\|DI.
4. Caller wants **white-space density×area** or treats this as NFPA 13 HC.
5. Caller cites **DS 7-32** as the transformer apparatus density sheet (7-32 is indoor non-Approved / gen / ignitable-liquid path).
6. Caller cites **DS 1-45** or confuses **DS 4-1N** with mist **DS 4-2** (water-spray ≠ mist).
7. Voil or L×W×H missing but sealed demand requested; invent Voil / L×W×H / outline MVA / worked SYN envelopes as defaults.
8. Indoor non-Approved fluid and caller wants an invented DS 5-4 indoor 0.30 — route to DS 7-32; fence foam/mist.
9. Claiming “no FP needed” without FM Approved **transformer** (not merely fluid).
10. writes outside the caller-named output; CAD production asked as this Skill’s deliverable.

---

## Citations (section **and** edition)

| Claim | Pin |
|---|---|
| Apparatus spray **0.30 gpm/ft²** excl. underside | FM DS **5-4** Jul-2019/IR Oct-2020 **§2.3.2.1.A** |
| Wall spray **0.20 gpm/ft²** | §2.3.2.2.A |
| ≥**18 in.** standoff; no top/vent piping; no bushing spray; simultaneous origin+adjacent | §2.3.2.1.C–F |
| Hose 250 gpm/1 h vs 500 gpm/2 h | §2.3.2.3 |
| Indoor Approved fluid **0.20 over entire room** | §2.2.3 |
| Non-Approved indoor → DS 7-32 | §2.2.3.1.B |
| FM Approved transformer / Std 3990 | §3.3; glossary |
| Nozzle ≥20 psi; outdoor <½ in. → 30 psi | DS **4-1N May 2010** §2.2.1.10 |
| No galvanized extinguishment mains; Sch.10 4/5/6; ≥60 min remote; ≥2000 gpm one-pump-out | §2.2.1.4–.5,.8–.9 |
| Switchgear room-centric | DS **5-19** Oct-2020/IR Jan-2024 §2.2 |
| Gen arrangement; density not on sheet | DS **5-23** Jul-2020/IR Jan-2022 §2.2 / §2.5.1 → DS 7-32 |
| Cable-only 0.20/3,000 | DS **5-31** §2.3.2.2.B |

**Absent / `[V]`:** licensed NFPA 15 current apparatus language; NEC Art. 450 Part III reconciliation; full nozzle K selection tables (use manufacturer + 4-1N pressure floors); simultaneous neighbor 0.30 vs 0.20 primary resolution (carry both); packet short-form `transformer` / `water-spray` (consume nearest).

---

## Design practice

1. **Hard-scope + status first.** Company fence on room hand-offs = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. **Water-spray ≠ mist.** Clean agent = hand-away only. Status every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist). Upstream (packet optional; gaps → `ASSUMED`): packet optional + STS when room + occupancy when rooms (+ matrix special-hazard/dual when dual — consume+return). **NO PLACEHOLDER.**
2. Three-layer most-stringent **per parameter** (density, simultaneous, hardware, containment, hose/duration).
3. Apparatus ≠ room ≠ white-space HC. Switchgear stays room-centric — **no lineup deluge**.
4. Geometry first; spray when geometry fails or insurer/owner demands.
5. Cite section **and** edition; DS 5-4 / 4-1N primaries over report readings.
6. Show-and-verify Aprot and +20% delta; flag `[SYN]` envelopes; no silent Voil / L×W×H / outline MVA — state ASSUMED + why when not given.
7. Indoor foam-water/CAF/mist / clean-agent alternatives = sheet evidence + company fence — do not elect/design; prefer dry-type / room wet\|dry\|DI.
8. Hand campus Qd to hydrant/pump Skills — do not freeze the campus supply here.

If notes conflict, **most-stringent wins** and both sources stay visible.

---

## Not this Skill

| Work | Where |
|---|---|
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume** when room; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance`; water-spray ≠ mist; peer already names this Skill |
| Occupancy / HC fork; transformer apparatus route | `occupancy-hazard-fork` — consume when rooms; peer already names this Skill |
| White-space density×area | `density-area-dry-increase` — room / DS 7-32 hand-off only |
| Dual-carrier special-hazard authorship | `most-stringent-basis-matrix` — consume+return when dual |
| Assignment packet authorship | the optional input packet — consume only (nearest special-hazard/suppression/bod) |
| Campus supply curve / pump nameplate | `hydrant-supply-curve` / `pump-envelope` |
| Deluge / NFPA 15 commissioning | `commissioning-ist-acceptance-packet` |
| Water-spray / deluge ITM calendar | `itm-design-for-testability` |
| De-energize / disconnect architecture | `power-isolation-disconnect-control` |
| Switchgear room package | **`mv-switchgear-room-package`** (live Skill) — DS 5-19 room package; this Skill does not duplicate it |
| Full ignitable-liquid plant (DS 7-32) | DS 7-32 note — fence; do not redesign wholesale |
| Gen combustion-air openings | `combustion-air-and-hall-free-area` — **Not-this** unless scoped |
| ESS / Li-ion | `ess-isolation-venting-and-duration` — **Not-this** unless scoped |
| Storage / staging sprinkler | `storage-staging-sprinkler-design` — **Not-this** |
| Preaction trim / room EL-EL | `preaction-el-el-trim-election` — **Not-this** unless room scoped; company BOD still wet\|dry\|DI |
| Clean-agent concentration / enclosure | out-of-scope clean-agent work — **hand-away only** (company scope) |
| Transformer siting table reprint | transformer-rooms-and-outdoor-transformer-siting (canonical geometry) |
| CAD / writes outside the caller-named output | forbidden |

---

## Check sequence

0. **Hard scope + status register first.** On room hand-offs STS = wet|dry|DI (consume — do not elect). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away. Restate **water-spray ≠ mist**. Packet if present (optional); STS when room; occupancy when rooms; matrix special-hazard/dual when dual (consume+return). Emit status skeleton (§1.4). **NO PLACEHOLDER.**
1. Confirm object class. **Fence** switchgear → room package under wet\|dry\|DI. Voil/envelope missing → stated `ASSUMED` values (value + why), flagged; spray math is ASSUMED-based, not sealed.
2. Pin DS 5-4 Jul-2019/IR Oct-2020, DS 4-1N May-2010, related sheets; NFPA 15 `[V]`; 13-2025 for room hand-offs only. DS 4-1N ≠ DS 4-2.
3. Approval status: transformer vs fluid trap (Std 3990).
4. Geometry-first gate against DS 5-4 tables (by title); record spray required / substituted.
5. Compute Aprot; Qws @ 0.30; show +20% vs 0.25; simultaneous Qws_simul with 0.30 vs 0.20 fork honesty.
6. Hardware + DS 4-1N pressure/pipe/duration floors (≥20/30 psi; no galvanize; ≥60 min; ≥2000 gpm one-pump-out).
7. Hose tier; Vcontain (indoor foam-water/CAF/mist terms = evidence + fence only); SPCC separate note.
8. Emit campus Qd hand-off to `hydrant-supply-curve` / `pump-envelope`.
9. De-energize-before-water interface; C&E / `power-isolation-disconnect-control` hand-off.
10. Δ vs NFPA 15 and Δ vs 13-2025 (rooms); status register complete; `[SYN]`/`[V]`; honesty (no outline defaults); reciprocal HAND OFF lines.
11. Write **only** to caller-named path (or return and stop).
