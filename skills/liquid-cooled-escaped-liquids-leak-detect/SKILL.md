---
name: Liquid-cooled escaped-liquids leak detect
description: >-
 use this when a direct-to-chip / CDU hall has pressurized coolant at every
 rack and you must run the coolant-classification fork then design
 below-equipment leak detection plus containment and BMS/FACP intervention —
 against company wet|dry|DI only (consume STS; this Skill does not elect
 family); packet optional; STS + occupancy-hazard-fork (+ matrix
 leak-detection / escaped-liquid rows when dual) consumed when present, else
 ASSUMED and flagged — never a stop;
 SI/NI-as-BOD → Stop RFI-variance (comparison-only); foam prohibited; mist
 PRACTICE REFUSED; status register every run — not sprinkler density×area, not
 ASD pipe sizing, not silently invent containment % / SDS flash·fire / ΔP
 setpoint (state ASSUMED + why), never a default TraceTek SKU, not clean-agent or foam/mist BOD.
---
# Liquid-cooled escaped liquids leak detect

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, deluge, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record. Do not claim a stamp.

Reusable DC fire-protection recipe. **This Skill runs the coolant-classification fork, then designs the below-equipment escaped-liquids leak-detection + containment + BMS/FACP intervention layer** for a hall that already distributes **pressurized coolant to every rack** (direct-to-chip / cold-plate TCS with in-row or end-of-row CDUs). It answers: *is the coolant on the white-space side or the ignitable-liquid side, and how do you detect / contain / intervene on a leak?*

It does **not** elect the suppression family — it **consumes** STS `wet` | `dry` | `DI` and records leak / containment / intervention consequences under that BOD. It does **not** re-size sprinkler density×area. It does **not** size ASD / VEWFD networks. It does **not** invent containment %, SDS flash/fire points, ΔP trip setpoints, or a default TraceTek SKU.

| Branch | Question this Skill answers | What it does **not** do |
|---|---|---|
| **Coolant fork** | Flash point? Fire point + exposable pool? → white-space vs ignitable-liquid basis | Does **not** re-size sprinkler density×area (hand off if ignitable-liquid branch opens) |
| **Leak detect + intervene** | Sensor architecture, zoning, containment posture, BMS/FACP C&E | Does **not** size ASD / VEWFD networks (`fa-asd-vewfd-data-hall-sampling-layout`) |
| **Containment** | What volume / tray / curb basis is **pinned** vs **unpinned** | Does **not invent a containment %** when the opened source does not set one |

**Core identity:**

```
# 1) CLASSIFY THE COOLANT FIRST (per fluid, per architecture)
Q1 measurable closed-cup FLASH POINT?
Q2 FIRE POINT? and can it form an exposed spill/pool?

no flash point (aqueous DTC / PG-25 / treated water;
 sealed two-phase fluoroketone) → WHITE-SPACE basis + THIS Skill's leak layer
flash but no fire point → white space + evaluate confined explosion [V]
flash AND fire point AND exposable pool
 (open immersion hydrocarbon/ester/PAO) → IGNITABLE-LIQUID basis
 (NFPA 30 + FM DS 7-32) — hand off density;
 keep leak/containment concepts

# 2) Direct-to-chip delta is DETECTION, not density (nonignitable branch)
# 3) Three sensor layers: indirect telemetry + direct point/rope + locating cable
# 4) Intervention ladder: alarm → electrical isolate → electrical + fluid shutoff
# 5) Containment %: print only if PINNED; otherwise [V] / refuse to invent
```

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PARAMETER** (coolant class, leak-detection requirement, sensor layer, voting, intervention tier, containment volume if pinned, BMS/FACP reporting). Report **Δ vs NFPA 13-2025** (density stays on the white-space Skill unless the ignitable-liquid fork opens — print **detection delta, not density delta** on nonignitable DTC). Cite **section AND edition**. Show-and-verify any arithmetic. Flag invented values **`[SYN]`** / unpinned **`[V]`**. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the optional input packet + STS `wet`|`dry`|`DI` + `occupancy-hazard-fork` (+ `most-stringent-basis-matrix` **leak-detection / escaped-liquid** rows when dual-carrier — **consume and return here**). Caller-path-only. **NO PLACEHOLDER.** Clean agent = **hand-away only** (company does not design — company scope). Generic — specify by **function + listing + opened SDS / OCP / vendor install**, not by a default TraceTek SKU. Owner may **raise, never lower**.

**Honesty (load-bearing):**

- **Direct-to-chip (ACS Cold Plate) sets no containment volume %** in the pinned OCP white paper. **OCP Immersion Rev 2.10 ≥100 % of largest single system/container** is an **immersion** floor. **Do not silently copy 100 % onto a DTC hall** as if it were a cold-plate requirement — if used, mark **`[SYN]`-by-extension** and say so, or prefer **owner-pinned** containment.
- **nVent “cable ≤3 ft from walls” is STRUCK** — absent from both the TraceTek white paper (©2018) and install primary **H55357**. Coverage geometry is the **designer’s drawn layout plan** (vendor precondition of install). Only linear vendor number: **hold-down clips ≤6 ft (2 m) + clip at every direction change** (attachment ≠ coverage).
- **LIT-138** (double-containment pipe cable install — the CDU/TCS loop case) is **not in corpus** → piping-cable install details stay **`[V]` / procure**.
- Coolant **SDS flash / fire point** must be the **actual fluid** on the job. Do not invent PG-25 properties or dielectric flash points from memory.
- Outline / worked package (`hyperscale-liquidcooled-aihall-directtochip-leakdetect-wi`) = **`[SYN]` method** only — do **not** copy 260 gal / 100 % / ΔP examples as defaults; SI alternative on that spine = **`comparison-only`** under company fence.

Write **only** to the path the **caller** names. Do not write outside the caller-named output.

Cite the section and the edition. Do not invent a section.

Outline / worked context (consume structure, do not copy synthetic numbers as defaults): *hyperscale-liquidcooled-aihall-directtochip-leakdetect-wi*.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (leak-detect-adapted — consumes STS, does not elect)

This Skill owns **coolant-classification fork + below-equipment escaped-liquids leak detection + containment posture + BMS/FACP intervention**. Controlling company BOD = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI | `suppression-technology-selection` (**consume** — do not elect here) |
| Coolant fork + leak/containment/intervention package | **This Skill** |
| Dual-carrier per-parameter union (leak-detection / escaped-liquid rows) | `most-stringent-basis-matrix` (**consume**, then **return here**) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- Synthetic SI hall spines that touch leak-detect / DTC packages (method only)

**This Skill does not elect families.** It **consumes** the STS token `wet` | `dry` | `DI`, the optional input packet, occupancy-hazard-fork (pinned or explicitly deferred), and — when carrier = `dual` — matrix **leak-detection / escaped-liquid** rows. Then it runs the coolant fork and emits the leak / containment / intervention package.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue leak/containment arithmetic as if SI/NI were company-elected BOD.
6. SI/NI (including synthetic SI hall spines that mention leak-detect) may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream via STS | Record leak / containment / intervention consequences under that BOD |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD — especially when IL fork / DS 7-32 §2.4.9 special protection / AXA containment-in-place foam path surfaces |
| Water mist | **`PRACTICE REFUSED`** | Record DS 7-32 §2.4.9 mist-via-DS-4-2 optional language as evidence if cited; do **not** design/accept mist as BOD or elective special-protection family |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent (company scope); Not-this may hand away to out-of-scope clean-agent work — never company BOD here |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Fence foam/mist **before** any IL special-protection reading. Clean agent = hand-away only — never company BOD here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Coolant fork Q1/Q2 → white-space vs ignitable-liquid | System-family election (`suppression-technology-selection`) |
| Three-layer sensor architecture + conductive validity | Occupancy re-class (`occupancy-hazard-fork`) — consume / defer only |
| Intervention ladder + 2-of-2 voting + BMS/FACP C&E | Density×area `_calc` (`density-area-dry-increase`) — hand off on IL fork |
| Containment: pinned value or explicit unpinned | ASD pipe / ports / transport (`fa-asd-vewfd-data-hall-sampling-layout`) |
| Status register + reciprocal handshakes | Dual-carrier BOD authorship (matrix — consume+return) |
| Consume packet + STS + matrix(when dual) + occupancy | Invent containment % / SDS / ΔP / ≤3 ft / default TraceTek SKU; clean-agent / foam / mist as company BOD |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet / STS / matrix(when dual) / occupancy, **(c)** coolant-fork result, **(d)** sensor layers + conductive validity, **(e)** voting, **(f)** intervention tier, **(g)** containment pinned/unpinned, **(h)** Δ vs 13-2025, and **(i)** mist/foam if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling fork + editions + sensor/intervention architecture supported by opened SDS / OCP / vendor install / caller pins already closed |
| `provisional` | Directionally pinned; LIT-138 / ΔP setpoint / IMC/edition hole flagged `[V]` — **never silent `grounded` on invented containment % / SDS / default SKU / worked 260 gal** |
| `unresolved` | STS / matrix(when dual) / occupancy / fluid+SDS / pressurized-at-rack / carrier not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, synthetic SI hall leak spines, DS 7-32 mist/foam special-protection wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; density+occupancy on IL fork; ASD VEWFD; power-isolation; commissioning / ITM; clean-agent hand-away) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as controlling medium or elective special-protection family — record and refuse |

**Invented containment % / silent TraceTek SKU / revived ≤3 ft wall rule / invented ΔP trip / copied worked 260 gal → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Outline + worked leak-detect package = **`[SYN]` method** only (fork → three layers → voting → C&E structure). Do **not** copy 260 gal / 100 % borrowed immersion floor / ΔP resolution math as project defaults. SI alternative on the outline = **`comparison-only`** under company fence. LIT-138 / DTC containment % in ACS Cold Plate / ΔP trip setpoints / packet short-form `leak-detect` remain intentional Absent / `[V]` / refuse invent. **NO PLACEHOLDER.**

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent flash point, containment %, ΔP setpoints, or a default SKU. Do not treat SI/NI as company BOD.

| Input | Required | Notes / Stop |
|---|---|---|
| the optional input packet (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`detection` / `special-hazard` / `bod`) — do not invent a new packet token this run; do not rebuild; do not retrieve a job index. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Occupancy-hazard-fork schedule** | **yes** (pinned or explicitly deferred) | Already pinned **or** explicitly deferred with a return path. Missing with no deferral → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not re-classify here. IL fork → occupancy re-pin expected via hand-off. |
| **Consumed `most-stringent-basis-matrix` leak-detection / escaped-liquid rows** | **yes** when dual-carrier (or when those rows exist) | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever as if matrix replaces this Skill. Unresolved controlling leak/escaped-liquid row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **Cooling architecture** | **yes** | `direct-to-chip / cold-plate + CDU` / `sealed two-phase` / `open single-phase immersion` / named. Open immersion flips the fork. |
| **Working fluid identity + SDS** | **yes** | Named fluid (e.g. **PG-25**, treated water, named dielectric). **Flash point, fire point, autoignition** from **current SDS**. Missing SDS → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged or mark class `[V]` and refuse to freeze the fork. |
| **Pressurized coolant at every rack?** | **yes** | This Skill’s trigger texture. If coolant is only in a remote plant → wrong Skill. |
| **Carrier** | **yes** | `FM DS 5-32 controlling` expected; AXA XL escaped-liquids / leak-below-equipment corroboration when invoked. `dual` → matrix rows above. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Leak-detection layout plan status** | **yes** | Vendor install requires a **plan before work**. If none → emit “plan required” deliverable; do not invent a coverage pitch. |
| **Intervention posture** | **yes** | Owner election: alarm-only / auto electrical / auto electrical+fluid — may be `unelected` → ask, flag `[V]`, do not invent a shutdown. |
| **Containment basis** | **yes to freeze volume** | `owner-pinned volume or %` / `immersion OCP 100% applicable` / `unpinned — do not invent`. DTC without owner pin → **performance containment + sensor**, not a fake %. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

**Do not invent** flash point, fire point, containment %, clip spacing-as-coverage, ΔP setpoints, or a default SKU. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the optional input packet | Packet context — **optional** (consume when present) (nearest `detection` / `special-hazard` / `bod`) | Rebuild the packet; invent a `leak-detect` component token; retrieve a job index |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token** | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `occupancy-hazard-fork` | Occupancy / space class — consumed when present (pinned or deferred) (else `ASSUMED`, flagged) | Re-classify occupancy here on nonignitable branch; skip IL hand-off when fork flips |
| `most-stringent-basis-matrix` | **Leak-detection / escaped-liquid** rows when dual-carrier | Rebuild dual-carrier BOD; Stop-away forever; invent leak numbers |
| `density-area-dry-increase` | Receives density hand-off when IL fork opens | Emit 0.30/4000 (or any DS 7-32 Table 2.4.3 density) as **this** Skill’s product |
| `fa-asd-vewfd-data-hall-sampling-layout` | Note only: liquid cooling often lowers residual airflow (helps VEWFD gates) | Size ASD ports / transport here |
| `power-isolation-disconnect-control` | Cooling-side twin of DS 5-32 IT+HVAC disconnect | Rewrite power-isolation architecture here |
| `commissioning-ist-acceptance-packet` | Wet-test / layout-plan / ΔP-threshold commissioning | Invent ΔP trip setpoints as code |
| `itm-design-for-testability` | Locating-module / sensor ITM handoff | Emit ITM interval calendar here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS `wet`|`dry`|`DI`, occupancy (pinned or deferred), or dual-carrier leak/escaped-liquid rows (when required) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Handoffs.** Do **not** rewrite peers. Note: **zero** live peers currently name this Skill by full id inbound.

| Peer | They own | This Skill owns |
|---|---|---|
| `occupancy-hazard-fork` | Occupancy / HC/OH pin (required upstream; re-pin on IL fork) | Consume / defer only; do not re-classify on nonignitable branch |
| `density-area-dry-increase` | Density×area / dry increase; IL density hand-off receiver | Hand off when flash+fire+pool; do **not** emit Table 2.4.3 density here |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume only**; mist = `PRACTICE REFUSED`; foam prohibited |
| `most-stringent-basis-matrix` | Per-parameter union / leak-detection·escaped-liquid rows | **Consume only** when dual — then design leak package **here** |
| the optional input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `fa-asd-vewfd-data-hall-sampling-layout` | ASD ports / chamber / transport / SOO | Note low residual airflow helps VEWFD — do not size ASD here |
| `power-isolation-disconnect-control` | IT+HVAC disconnect architecture | Branch TCS shutoff = cooling-side twin; coordinate, do not rewrite |
| `commissioning-ist-acceptance-packet` | Wet-test / layout-plan / ΔP-threshold commissioning | Name commissioning thresholds; refuse invent setpoints as code |
| `itm-design-for-testability` | Lifecycle ITM / locating-module testability | Name ITM of sensors/modules; do not emit interval calendar |
| `ess-isolation-venting-and-duration` | ESS isolation / venting | **Not-this** unless ESS in same scope |
| `storage-staging-sprinkler-design` | Commodity / storage sprinkler | **Not-this** |
| `preaction-el-el-trim-election` | Preaction trim family | **Not-this** (wet vs SI election stays on STS / preaction peers) |
| out-of-scope clean-agent work | Clean-agent concentration / enclosure | **Hand-away only** — company does not design clean agent |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: leak-detection/escaped-liquid rows when dual. Consume; return here after.`
- `HAND OFF — the optional input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — occupancy-hazard-fork: occupancy pin (or deferred). Consume; IL fork → re-pin hand-off.`
- `HAND OFF — density-area-dry-increase: density×area when IL fork opens. Do not emit 0.30/4000 here.`
- `HAND OFF — fa-asd-vewfd-data-hall-sampling-layout: ASD ports/transport (peer does not yet name this Skill inbound).`
- `HAND OFF — power-isolation-disconnect-control: IT+HVAC disconnect; TCS shutoff is cooling twin.`
- `HAND OFF — commissioning-ist-acceptance-packet: layout-plan / ΔP-threshold commissioning.`
- `HAND OFF — itm-design-for-testability: locating-module / sensor ITM.`
- `HAND OFF — ess-isolation / storage-staging / preaction-el-el: Not-this unless scoped.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before edition pins or fork arithmetic:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only.
2. Check upstream (packet optional): packet if present (optional); STS present; occupancy pinned or deferred; matrix leak-detection/escaped-liquid rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix·occupancy / fork / sensors·conductive / voting / intervention / containment / Δ 13 (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER** anywhere in the run.

### 3.1 Pin editions (enforced ≠ latest)

| Layer | Instrument | Role in this Skill | Shop-pinned edition |
|---|---|---|---|
| Insurer — white space | **FM DS 5-32** | Nonignitable liquid-cooled servers preferred; leak detection in system/room; white-space sprinkler basis stays unless fork flips | **January 2026** |
| Insurer — ignitable liquid (fork) | **FM DS 7-32** | Only if flash+fire+exposable pool — ceiling / under-tank / drainage / special protection | **April 2020 / Interim Revision April 2026** (full mine in corpus). Density / drainage design → **hand off**; do **not** emit Table 2.4.3 (e.g. 0.30/4000) as this Skill’s product. Fence foam/mist (§2.4.9) before any special-protection reading. DS 7-32A classification peer when fork opens. |
| Code floor — liquids | **NFPA 30** | Ignitible-liquid classification when fork opens | **2024** latest: classes [CODE NFPA 30-2024 §4.2.2 (Class II), §4.2.3 (IIIA/IIIB), pull 30-01]; AHJ pin may differ |
| Code floor — ITE | **NFPA 75** | Immersion / liquid-cooling text still maturing | **2024**; liquid-to-chip guidance still in committee per shop note |
| Code floor — sprinkler delta | **NFPA 13-2025** | Density×area stays on the **other** Skill unless ignitable-liquid branch opens | **2025** delta |
| Carrier corroboration | **AXA XL** (escaped liquids / leak detection below liquid-cooled equipment) | Requirement corroboration — not a sensor method | Cite opened PRC edition on the job |
| Owner / consortium | **OCP ACS Cold Plate** Leak Detection & Intervention | DTC taxonomy: indirect/direct, voting, intervention ladder | **Rev 1.0, 2021** |
| Owner / consortium | **OCP Immersion Requirements** | Containment **≥100 %** largest vessel — **immersion** | **Rev 2.10, 2023** |
| Vendor — taxonomy | **nVent RAYCHEM TraceTek** white paper | Point vs cable; action-tier nuance; dielectric defeats conductive rope | **©2018** (H60516 / 18/10) |
| Vendor — install | **nVent TraceTek H55357** | Layout plan precondition; clips ≤6 ft; **no** ≤3 ft wall rule | **rev. EN-1805, ©2018** |

**Δ vs NFPA 13-2025:** on the **nonignitable DTC** branch, this Skill does **not** change density×area — print **“detection delta, not density delta.”** If the ignitable-liquid fork opens, density becomes a **hand-off** to `density-area-dry-increase` + `occupancy-hazard-fork` (DS 7-32 Apr-2020 / IR Apr-2026 mined — do **not** invent or emit 0.30/4000 here).

### 3.2 Run the coolant-classification fork (hard gate)

```
CLASSIFY (SDS in hand):
 no flash point
 aqueous DTC (PG-25 / treated water) → WHITE-SPACE + leak layer (THIS Skill continues)
 sealed two-phase fluoroketone → WHITE-SPACE + integrity / loss-of-fluid monitoring
 flash but no fire point → white space + confined-explosion eval [V]
 flash AND fire point AND exposable pool
 open immersion dielectric → IGNITABLE-LIQUID — Stop density here;
 hand off DS 7-32 / NFPA 30 + density + occupancy;
 keep leak + containment concepts;
 fence foam/mist BEFORE special-protection readings
```

**PG-25 / treated water (typical DTC):** no measurable closed-cup flash point → **non-flammable / nonignitable** white-space branch. Suppression basis remains FM DS 5-32 white space; **this Skill is the delta.**

**FM preference:** use **nonignitable** liquid in liquid-cooled servers — designing the coolant out of the fire problem is the cheapest lever.

**Stop / hand-off if open combustible immersion** is the architecture: do not pretend DTC leak-rope recipes close a pool-fire problem. On IL fork: (1) fence foam prohibited / mist `PRACTICE REFUSED` before reading DS 7-32 §2.4.9 or AXA containment-in-place foam language; (2) **hand off** density + occupancy; (3) keep leak/containment concepts in this Skill; (4) do **not** emit 0.30/4000 (or any Table 2.4.3 row) as this Skill’s density product.

### 3.3 Confirm prerequisites and wrong-Skill fences

- Pressurized coolant at racks / CDUs / manifolds — yes.
- Caller asks **sprinkler density×area** as the deliverable → **Stop** (`density-area-dry-increase`). Record only that the nonignitable branch **keeps** the existing white-space basis.
- Caller asks **ASD pipe / ports / transport** → **Stop** (`fa-asd-vewfd-data-hall-sampling-layout`). Note only: liquid cooling often **lowers** residual airflow, which **helps** VEWFD gates — do not size ASD here.
- Caller asks to invent **containment = 100 %** on a DTC hall without owner pin or immersion applicability → **refuse**; mark unpinned.
- Caller presents SI/NI / foam / mist as company BOD → **Stop** per §1.1–1.2.

### 3.4 Requirement basis (why this Skill exists)

| Source | What it grounds | What it does **not** ground |
|---|---|---|
| **FM DS 5-32** | Leak detection in the liquid-cooling **system or room**; prefer nonignitable coolant; white-space sprinklers stay | Sensor type / zone pitch / containment % |
| **FM loss texture** (shop note) | Escaped liquids as a real loss driver; under-floor coupling cascade narrative | Design method |
| **AXA XL** (when invoked) | **Leak detection below liquid-cooled / cooling equipment** | Method; foam containment-in-place as company BOD |
| **OCP ACS Cold Plate Rev 1.0** | Indirect vs direct definitions; ΔP-across-pumps “should be considered a requirement”; 2-of-2 voting; intervention ladder | Containment volume % |
| **OCP Immersion Rev 2.10** | ≥100 % largest system containment; leak detection mandatory-minimum | **Not** a DTC containment default |
| **nVent white paper + H55357** | Point vs cable; layout plan required; clip ≤6 ft; conductive-fluid physics | ≤3 ft wall spacing (struck); LIT-138 piping case |
| **FM DS 7-32 Apr-2020 / IR Apr-2026** (IL fork only) | Table 2.4.3 / drainage / §2.4.9 special protection exist in corpus | Density product of **this** Skill; foam/mist as company BOD |

### 3.5 Sensor architecture (three layers — refuse single-layer designs)

**Precondition:** direct rope/point needs coolant that **physically touches** the sensor **and** is **electrically conductive** (OCP-CP; nVent corroboration).

| Coolant | Direct conductive rope/point? |
|---|---|
| **PG-25 / aqueous** | **Valid** — conductive |
| **Dielectric / many two-phase** | **Invalid as sole direct layer** — lead with **indirect + optical/level + tray sensors** |

**(a) Indirect (non-contact)** — differential pressure across TCS pumps (flagship); buffer / reservoir level; turbidity / optical build-up; abnormal flow / temperature deviation. Corpus: ΔP across pumps “should be considered a requirement.” **Corpus gives no setpoint** — do not invent trip psi; require commissioning thresholds. Note arithmetic consequence (for caller-supplied flows): ΔP on a large branch is **blind to slow drips** → layer (b)/(c) are not optional.

**(b) Indirect — level / make-up lockout.** Buffer-tank level catches slow loss ΔP misses. **Design rule (flag if not in SDS/owner std):** auto make-up that silently refills **defeats** level detection — lock out / alarm make-up runtime.

**(c) Direct — point + rope/cable.** Point sensors at **drip-pan low points** / CDU internals / QD drip paths. **Cable** along pipes, under raised floors, under racks, where the leak path is ill-defined. **2-wire** = yes/no; **4-wire locating** = map to DC coordinates / tile. Specify flame resistance + chemical resistance + bend radius by listing — **generic function**, not a default SKU.

**Placement honesty:** draw a **leak-detection layout plan** (H55357 precondition). Clips at **≤6 ft (2 m)** and every direction change = **attachment**. **Do not** cite ≤3 ft from walls.

**Nuisance / voting (OCP-CP):** with tray point **and** manifold rope — **either → operator alarm; both → automatic intervention.** Twin of immersion **SR 7.6-8** (no single sensor may trigger shutdown). Fix thresholds at commissioning.

### 3.6 Intervention ladder + BMS/FACP C&E

OCP ACS Cold Plate ladder (record tiers; elect per owner redundancy):

| Tier | Action | Notes |
|---|---|---|
| **1 Manual** | Notify / dispatch | Minimum everywhere |
| **2 Auto electrical** | De-energize ITE in the zone | Protects wetted-but-powered hardware; **does not stop fluid loss** |
| **3 Auto electrical + fluid** | De-energize **and** shut coolant (branch MOV/solenoid / CDU) | Specify fail-last/open/closed; swing time vs water hammer; **panic soft-shutdown before** dropping a row CDU that can take **10+ racks**; enable cold-plate thermal throttle |

**Reaction authority:** node → BMC; rack → Rack Manager / rack CDU; row → row CDU → **BMS**.

**nVent action-tier nuance:** lavatory-style water can auto-solenoid; **cooling loops and sprinklers get escalated alarm priority** — blind auto-shut of cooling “may not be possible or provide other dangers.” Define response **per leak type**. Route locating alarms to **BMS/FACP** with which-tile / which-zone display.

**Pair with power isolation:** branch TCS shutoff is the cooling-side twin of FM DS 5-32 integrated IT+HVAC disconnect. Coordinate via `power-isolation-disconnect-control`; do not rewrite that Skill here.

**FACP vs BMS:** leak detection is typically **BMS/DCIM-primary** with **FACP supervisory or supervisory+alarm** points as the carrier/owner elects. Do not invent a releasing-service tie to sprinklers unless the caller’s C&E already pins it.

Minimum C&E table to emit:

| Event | Minimum | Preferred hyperscale (if elected) |
|---|---|---|
| Telemetry anomaly (ΔP / level) | Supervisory to BMS/DCIM + dispatch | Trend → suspect CDU branch |
| Spot sensor (drip pan / CDU) | Alarm + local response | Alarm + **auto-close branch isolation** + staged soft shutdown |
| Cable leak under rack / pipe | Alarm + manual | Alarm + **de-energize IT zone** + **close CDU/manifold liquid shutoff** (2-of-2 if voted) |

### 3.7 Containment — pinned vs unpinned

**Rules:**

1. If **owner standard** pins a volume or % → use it; cite it.
2. If architecture is **open immersion** and OCP Immersion **SR 3.2-10 / CR 3.3-4** applies → **≥100 % of largest single system/container (including interconnected volume)** is an owner-layer floor; reconcile with FM DS 7-32 drainage when that sheet is open (hand-off density/drainage design — do not emit Table 2.4.3 here).
3. If architecture is **direct-to-chip / ACS Cold Plate** and **no owner pin** → **do not invent 100 %**. Emit: drip pans at high-risk fittings, curbs / trenches as coordinated with mechanical, acknowledgment that high-flow manifold / FWS breaks may **not** be containable for duration (OCP-CP tray caveat). Mark containment volume **`[V]`**.
4. Never present a synthetic worked-example 260 gal / 100 % cell as a code default.

### 3.8 Fluorinated / refrigerant side notes (do not expand into primary design unless called)

- Sealed two-phase fluoroketone: keep white-space sprinklers; add **loss-of-fluid / integrity** monitoring; run 10–20-year AIM/PFAS/supply gate before standardizing.
- Refrigerant / pumped two-phase: **ASHRAE 34** space-volume per refrigerant mass (OCP-CP cites ≥1,000 ft³ per 13 lb — verify against adopted edition) — life-safety, not sprinkler density.

---

## Output

A **coolant-fork + escaped-liquids leak-detection package** written **only** to the caller-named path.

Minimum:

1. Hard-scope / company-fence / status register (§1.4 tokens).
2. Edition-pin block (incl. DS 7-32 Apr-2020 / IR Apr-2026 when IL fork opens — hand-off density, do not emit 0.30/4000 here).
3. Inputs echoed (packet + STS + matrix(when dual) + occupancy; fluid + SDS pins; architecture; carrier).
4. **Coolant-classification fork** result (white-space vs ignitable-liquid) with flash/fire-point citations.
5. Statement: **detection delta, not density delta** (or hand-off if ignitable-liquid).
6. Three-layer sensor architecture + conductive-fluid validity.
7. Leak-detection **layout plan** requirement; clip ≤6 ft as attachment only; ≤3 ft wall rule **struck**.
8. Zone / sensor schedule structure (CDU, manifold, QD drip, below-floor low points, tray low points) — generic functions.
9. Intervention ladder + BMS/FACP C&E table; voting rule; power-isolation hand-off.
10. Containment block: **pinned value** or explicit **unpinned — not invented**.
11. Δ vs NFPA 13-2025; `[SYN]`/`[V]` register inside status rows; LIT-138 gap if piping-cable install claimed.
12. Reciprocal `HAND OFF` rows (correct peer IDs).
13. Honesty line: **do not invent containment %; OCP 100 % is immersion unless owner extends it.**

Do **not** emit: density×area `_calc`, ASD pipe sizing, pump nameplate, clean-agent quantity, foam/mist BOD, CAD shop drawings, codebook writes, rebuilt packet/matrix/STS, or a default TraceTek part number as the basis.

---

## Stop

A missing input is not a stop. Proceed with a stated ASSUMED value (the value and why), flagged in the output and the status register. Company scope locks stay hard stops: single-interlock or non-interlock as the basis of design, foam, water mist, deluge, and clean agent as the basis of design.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent / foam / mist as company BOD → Stop / hand-away only (clean agent) or refuse (foam/mist).
2. Missing packet, STS `wet`|`dry`|`DI`, occupancy (pinned or deferred), or dual-carrier matrix leak-detection/escaped-liquid rows (when required) → `unresolved`. Dual + missing matrix → complete matrix, then **return here** (do not Stop-away forever).
3. Missing fluid identity / SDS when freezing the fork. No pressurized-at-rack coolant texture (wrong Skill). Unpinned carrier.
4. Inventing containment % on an unpinned DTC job; inventing SDS flash/fire; inventing ΔP trip setpoints as code; citing nVent ≤3 ft wall spacing; default TraceTek SKU as basis.
5. Flash+fire+exposable-pool (open combustible immersion) asked to use DTC-only rope recipes as the fire basis **without** density + occupancy hand-off.
6. Caller demands density×area or ASD sizing as this Skill’s product. Emitting DS 7-32 Table 2.4.3 density (e.g. 0.30/4000) here.
7. Single-sensor auto-shutdown as the only architecture when owner/OCP voting applies and is unelected.
8. Write outside the caller-named output. Invent fabricated tokens (**NO PLACEHOLDER.**). NDA owner treated as numeric containment.

Unelected intervention tier is **not** a Stop if alarm-only minimum is issued and auto tiers are flagged `[V]`. Unpinned containment % is **not** a Stop if the package **refuses to invent** and issues a performance/coordination spec instead.

---

## Citations (section **and** edition)

**FM DS 5-32 Jan-2026:** white-space protection; nonignitable liquid-cooled servers preference; leak detection in system/room; water-based primary.

**FM DS 7-32 April 2020 / Interim Revision April 2026:** Table 2.4.3 protection; drainage Table 2.2.2.1; §2.4.9 special protection (foam-water / mist-via-DS-4-2 — company fence: foam prohibited; mist `PRACTICE REFUSED`). Density/drainage → hand off to density + occupancy; do **not** emit 0.30/4000 as this Skill’s product. DS 7-32A classification peer when fork opens.

**OCP ACS Cold Plate Leak Detection & Intervention Rev 1.0 (2021):** indirect vs direct (pp.9, 23–26); ΔP across TCS pumps; rope 2-wire/4-wire; redundant voting (p.37); intervention ladder / authority (pp.8, 37, 40–44); tray containment caveat (p.33); ASHRAE 34 refrigerant volume note (p.22).

**OCP Immersion Requirements Rev 2.10 (2023):** SR 4.2-1 flash-point floor; SR 3.2-10 / CR 3.3-4 ≥100 % containment (**immersion**); SR 5.1-1 leak detection mandatory-minimum; SR 7.6-8 no single-sensor shutdown; OR 5.3-1 high-safety auto responses.

**nVent RAYCHEM TraceTek white paper ©2018:** point vs cable; locating modules → BMS; action-tier “don’t blindly shut cooling/sprinklers”; conductive-fluid physics; FM 7745 fast-fuel probe (generator leg — fence).

**nVent TraceTek H55357 rev. EN-1805 ©2018:** layout plan before install; clips ≤6 ft + every direction change; bend/service-loop rules; TT5000 replacement-on-fuel; **LIT-138 / H55313 deferrals**; ≤3 ft wall figure **absent**.

**AXA XL** (when invoked): leak detection below liquid-cooled / cooling equipment — requirement corroboration, not method.

**Absent (name the hole; do not fill it):** DTC containment volume % in ACS Cold Plate; LIT-138 piping-cable primary; invented PG-25 cp/ρ tables; nVent ≤3 ft wall rule; ΔP trip setpoints as code; packet short-form `leak-detect` token.

---

## Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent = hand-away only. Status every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist). Upstream (packet optional; gaps → `ASSUMED`): packet + STS + occupancy (+ matrix leak-detection/escaped-liquid when dual — consume+return). **NO PLACEHOLDER.**
2. **Fork first.** Coolant flash/fire/exposability decides whether this is a detection add-on or an ignitable-liquid redesign. On IL fork: fence foam/mist, then hand off density + occupancy; keep leak/containment concepts.
3. **Detection delta, not density delta** on nonignitable DTC. Do not re-litigate 0.20/2500 here. Do not emit DS 7-32 0.30/4000 here.
4. **Three layers + voting.** Indirect alone misses drips; direct alone misses dielectrics / evaporated glycol residue; single-sensor shutdown is a nuisance/availability failure mode.
5. **Do not invent containment %.** Immersion 100 % ≠ DTC default. Owner pin or `[V]`. No silent worked 260 gal.
6. **Generic.** Function + listing + opened SDS/OCP/vendor. No default SKU. Coverage is a **drawn plan**. ≤3 ft struck; clips ≤6 ft = attachment; LIT-138 `[V]`.
7. Reciprocal handshakes with correct peer folder IDs; do not rewrite peers. Caller-path-only. Cite section AND edition. Show-and-verify only on caller-supplied volumes/flows; mark synthetic worked-example numbers `[SYN]` if referenced for shape.

---

## Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH | `occupancy-hazard-fork` — **consume** (or defer); IL fork → re-pin hand-off |
| Sprinkler density × area / wet vs SI vs DI election | `density-area-dry-increase` / `suppression-technology-selection` — **consume** STS; density hand-off on IL; SI/NI-as-BOD → `RFI-variance` |
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume only**; mist BOD = `PRACTICE REFUSED`; foam prohibited |
| Dual-carrier per-parameter authorship (leak/escaped-liquid) | `most-stringent-basis-matrix` — **consume**, then return here |
| Assignment packet authorship | the optional input packet — **consume only** |
| ASD / VEWFD pipe, ports, transport, App. C | `fa-asd-vewfd-data-hall-sampling-layout` (peer does not yet name this Skill inbound) |
| Power-isolation architecture | `power-isolation-disconnect-control` — TCS shutoff is cooling twin |
| Commissioning / IST / wet-test thresholds | `commissioning-ist-acceptance-packet` |
| Locating-module / sensor ITM calendar | `itm-design-for-testability` |
| ESS isolation / venting | `ess-isolation-venting-and-duration` — **Not-this** unless scoped |
| Commodity / storage sprinkler | `storage-staging-sprinkler-design` — **Not-this** |
| Preaction trim election | `preaction-el-el-trim-election` — **Not-this** |
| Clean-agent concentration / quantity / enclosure | Hand-away only — company does **not** design clean agent |
| Open immersion pool-fire ceiling / under-tank sprinklers / DS 7-32 density | Hand off to density + occupancy + ignitable-liquid notes (keep leak/containment here) |
| Generator diesel leak / FM 7745 fuel probe | flammable-liquids / generator-plant notes |
| Foam / mist as company BOD | **Prohibited** / `PRACTICE REFUSED` — never design here |
| Writing outside the caller-named output | forbidden |

---

## Check sequence

0. **Hard scope + status register first.** STS = wet|dry|DI (consume — do not elect). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away. Packet (optional) + STS + occupancy (pinned or deferred) present; matrix leak-detection/escaped-liquid when dual (consume+return). Emit status skeleton (§1.4). **NO PLACEHOLDER.**
1. Confirm remaining inputs; Stop tests. Fluid + SDS in hand. Pressurized-at-rack yes. Architecture named.
2. Pin editions: DS 5-32 Jan-2026; OCP-CP 2021; OCP Immersion 2.10 only if applicable; nVent ©2018 / H55357; AXA XL when invoked; DS 7-32 Apr-2020 / IR Apr-2026 when IL fork (hand off density — do not emit 0.30/4000 here); Δ vs 13-2025 = detection-not-density (nonignitable).
3. Fork closed (PG-25/aqueous DTC → white-space + leak layer, or immersion IL hand-off with foam/mist fence first).
4. Three-layer sensors; conductive validity checked; layout plan required; clips ≤6 ft ≠ coverage; ≤3 ft struck; no default SKU; LIT-138 `[V]` if piping-cable claimed.
5. Intervention ladder + BMS/FACP C&E; voting (2-of-2 / SR 7.6-8); no silent single-sensor shutdown; power-isolation hand-off.
6. Containment: pinned or explicitly unpinned — **not invented**. No silent 100 % on DTC. No silent worked 260 gal.
7. Close status register; reciprocal `HAND OFF` rows (correct peer IDs — occupancy, density, STS, matrix, packet, asd-vewfd, power-isolation, commissioning-ist, itm; ess/storage/preaction Not-this unless scoped; clean-agent hand-away).
8. No density×area, no ASD sizing, no foam/mist/clean-agent BOD, no codebook writes. Output only at **caller path**.
