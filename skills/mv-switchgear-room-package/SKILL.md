---
name: MV switchgear room package
description: >-
 use this when a space is / may be an MV (>1000 V AC) switchgear / circuit-breaker
 room and you must elect the DS 5-19 room package (object class, smoke+attended,
 upstream high-side breaker outside room, room wet|dry|DI water path, cable DS 5-31
 fork, oil-filled §2.2.3 fork, no lineup deluge) packet optional, STS consumed or
 ASSUMED; never present an assumed density as DS 5-19 density; never treat as NEC 645 ITE EPO; SI/NI-as-BOD Stop;
 foam prohibited; mist PRACTICE REFUSED; clean-agent hand-away; not transformer
 apparatus spray, not hall isolation.
---

# MV switchgear room package

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, deluge, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record. Do not claim a stamp.

Reusable US data-center fire-protection recipe. **This Skill owns the FM DS 5-19 MV switchgear / circuit-breaker ROOM package**: object-class fence (room vs apparatus), voltage fence (>1000 V AC), oil / non-oil fork, base room package (noncombustible · smoke to constantly attended · de-energize/diagnose · room sprinkler/preaction · no storage · positive-pressure filtered air · pre-incident plan · upstream high-side breaker outside the room), grouped-cable DS 5-31 fork, and water-path consumption under company `wet` | `dry` | `DI` — after the assignment packet exists and STS has elected company family.

It does **not** elect the hall sprinkler/preaction family (consume STS). It does **not** invent a “DS 5-19 density.” It does **not** deluge the metal-clad lineup. It does **not** treat switchgear-room isolation as NEC 645 / NFPA 75 / DS 5-32 ITE hall EPO (`power-isolation-disconnect-control`). It does **not** size outdoor oil-transformer apparatus spray (`power-block-transformer-water-spray`). It does **not** design foam, mist, CAF, or clean agent.

**Core thesis:** Classify the **object** first. Standard modern MV **metal-clad / vacuum / air / SF₆** switchgear in a **noncombustible room with no other combustibles** is a **ROOM** problem — **do not deluge the lineup** *(FM DS 5-19 §2.2.1, October 2020 / Interim Revision January 2024)*. Voltage fence: sheet applies **above 1000 V AC**; below → DS 5-20 / other room FP — do **not** cite §2.2 as primary for a 480 V switchboard room without naming the fence *(§1.0)*. Base room package: noncombustible · **photoelectric or photo+ionization** smoke alarming at a **constantly attended** location · response that reaches people who can **de-energize or diagnose** · room sprinkler or preaction per STS/owner/DS 5-32 · **no storage** · slight **positive pressure** filtered air · pre-incident plan · strongly prefer **upstream (high-side) breaker OUTSIDE the room** *(§2.2.4–2.2.5, §2.1.5)*. **Smoke does not buy sprinkler omission** — sheet language is explicit *(§2.2.4)*. **No sprinkler density lives in DS 5-19** for the standard non-oil room — density from NFPA 13 / occupancy / **DS 5-31** cable-only when applicable. Never invent “DS 5-19 density.” Grouped combustible cable → DS 5-31; cable-only **0.2 gpm/ft² over 3,000 ft²**, **165°F**, **130 ft²** spacing when corpus holds DS 5-31 §2.3.2.2.B *(January 2020 / Interim October 2025)* — cite + `[V]` if edition unconfirmed in the run. Oil-filled bulk-oil / exposed combustibles → §2.2.3 fork (sprinkler **OR** FM Approved inert gas **OR** FM Approved water mist listed for enclosures-with-machinery → DS 4-1) — but company: **mist = `PRACTICE REFUSED`**, **clean agent = hand-away only**, **foam prohibited**. Structure the fork; **Stop / RFI-variance / PRACTICE REFUSED / hand-away** when mist/inert/foam presented as BOD; prefer non-oil technology + room water path under wet|dry|DI. Minimum-oil treated as non-oil when room clean *(§2.2.1; App. C.1.4.1.1)*. Forced-air-cooled bus duct drawing from a fire-risk area → fan interlock with bus CB + remote detection *(§2.2.3.2)*. Arc-resistant / redundancy / preferably **five** horizontal sections = electrical design bind note *(§2.3.5)*, not FP density invent. OH-fed surge → DS 5-11 pointer / lightning surge handoff — not room FP substitute. Calc runs / a synthetic room example project = **`[SYN]` method only** — refuse invent room ft² / demand gpm as sealed defaults.

**Design practice:** three-layer most-stringent **per parameter** (object class, voltage fence, oil fork, room package elements, cable density fork, isolation architecture, water-path family consume, detection, C&E interface). Report **Δ vs NFPA 13-2025** on the room water path; apparatus delta is N/A when room-centric. Cite **section AND edition** — **FM DS 5-19, October 2020, Interim Revision January 2024**. Show-and-verify when density×area is consumed from peers. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**; clean agent = **hand-away only** (company does not design clean agent). Upstream (packet optional; gaps → `ASSUMED`): the optional input packet + STS `wet`|`dry`|`DI` (consumed, else `ASSUMED`) (+ `most-stringent-basis-matrix` when dual — **consume and return here**) (+ `occupancy-hazard-fork` when occupancy/HC row feeds the room). Caller-path-only. **NO PLACEHOLDER.** Generic — do **not** copy a synthetic room example ~2,000 ft² / calc 500–700–600 gpm envelopes / a synthetic example dual-object SI spines as project defaults. Owner may **raise, never lower**.

**Honesty — density / room area unheld as DS 5-19 defaults.** Corpus holds **FM DS 5-19 (Oct-2020 / IR Jan-2024)** room posture with **no** standard-room sprinkler density; **FM DS 5-31 (Jan-2020 / IR Oct-2025)** cable-only **0.2/3,000** when cable-only; worked a synthetic room / a synthetic adjacency example / a synthetic example packages and worked examples as **`[SYN]` method**. Live room area, elected occupancy density, and sealed demand gpm are **not** sealed defaults from this sheet. Recipe structure is **Ready**; sealed “DS 5-19 density” / sealed room ft² / sealed gpm → **Stop / `[V]` / RFI**.

Write the package **only** to the path the **caller** names. Do not write outside the caller-named output. Do not retrieve a job index. Do not CAD.

Cite the section and the edition. Do not invent a section.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (consumes STS — does not elect)

This Skill owns the **DS 5-19 MV switchgear ROOM package** (object/voltage/oil fences, room package elements, cable fork, isolation architecture note, water-path consumption). Controlling company BOD for sprinkler/preaction families = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI (hall / campus / room BOD) | `suppression-technology-selection` (**consume** — do not elect here) |
| MV switchgear **room** package (DS 5-19) | **This Skill** |
| Dual-carrier per-parameter union | `most-stringent-basis-matrix` (**consume**, then **return here**) |
| Occupancy / HC pin when rooms | `occupancy-hazard-fork` (**consume** when gated; peer §9 already routes here) |
| Room density×area arithmetic when elected | `density-area-dry-increase` (**consume** / hand demand — do not invent DS 5-19 density) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- Synthetic SI MV-room spines (a synthetic room / MD / a synthetic example) as company BOD

**This Skill does not elect hall families.** It **consumes** the optional input packet and the STS token `wet` | `dry` | `DI`, then runs the room package. Electrical-room **DI** as owner preference is **consume if elected upstream** — do **not** invent DI as universal electrical-room default. If caller presents SI/NI as BOD:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue room arithmetic as if SI/NI were company-elected BOD.
6. SI/NI (including a synthetic room worked SI Route A / a synthetic electrical-room SI) may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler / preaction | Permitted when elected upstream via STS | Record room water path under that BOD; do not elect |
| Room smoke (photo or photo+ion) + constantly attended + de-energize/diagnose | **In scope here** | Elect package elements per §2.2.4–2.2.5 |
| Upstream high-side breaker outside room | **In scope here** (architecture note) | Prefer / record; do not invent EPO counts |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water / CAF | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist (incl. DS 5-19 §2.2.3.1 / DS 4-1 enclosure listing) | **`PRACTICE REFUSED`** | Structure §2.2.3 fork; record sheet evidence; do **not** design/accept mist as BOD |
| Clean agent / inert gas / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent; Never company BOD here — even when §2.2.3.1 names inert gas |
| Apparatus water spray / lineup deluge | **Out — fence** | Hand to `power-block-transformer-water-spray` only for transformers; **refuse** lineup deluge |
| NEC 645 / NFPA 75 / DS 5-32 ITE hall EPO | **Handoff** | `power-isolation-disconnect-control` — different object |
| OH-fed surge / lightning arresters | **Handoff pointer** | DS 5-11 / lightning-surge corpus — not room FP substitute |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Clean agent / inert gas = hand-away only. Prefer non-oil tech + room wet|dry|DI when the company path fits.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Object-class fence: room vs apparatus; no lineup deluge | System-family election (`suppression-technology-selection`) |
| Voltage fence >1000 V AC; <1000 V → DS 5-20 / other | NEC 645 / NFPA 75 / App. D ITE EPO (`power-isolation-disconnect-control`) |
| Oil / bulk-oil / minimum-oil / non-oil fork + company Stop on mist/inert/foam BOD | Transformer apparatus spray 0.30 / wall 0.20 (`power-block-transformer-water-spray`) |
| Base room package checklist (§2.2.4–2.2.5, §2.1.5) | Invent “DS 5-19 density” or sealed room ft²/gpm from a synthetic room/calc |
| Cable-only DS 5-31 fork (0.2/3,000 when held) | White-space hall density×area ownership (`density-area-dry-increase`) |
| Upstream breaker-outside-room architecture note + C&E interface flags | Full releasing C&E / SOO rewrite (`preaction-releasing-c-and-e-soo`) |
| Forced-air bus-duct interlock flag (§2.2.3.2) | Arc-resistant / 5-section gap as FP density invent (§2.3.5 = electrical bind) |
| Status register + reciprocal HAND OFFs | OH surge design (DS 5-11 pointer only); foam/mist/clean-agent BOD; CAD |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet + STS (+ matrix when dual; occupancy when gated), **(c)** object class, **(d)** voltage fence, **(e)** oil / non-oil fork, **(f)** base room package completeness, **(g)** smoke vs sprinkler (no omission credit), **(h)** cable DS 5-31 fork, **(i)** isolation architecture (upstream breaker), **(j)** water-path consume STS, **(k)** detection / DS 5-48 spacing honesty, **(l)** C&E handoff, **(m)** Δ layers, and **(n)** mist/foam/clean-agent if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling object fence + editions + package elements supported by opened DS 5-19 / DS 5-31 (when cable) / caller voltage·oil·room facts already closed |
| `provisional` | Directionally pinned; live room area / occupancy density / DS 5-48 spacing / owner DI preference flagged `[V]` — **never silent `grounded` on invented DS 5-19 density or a synthetic room ft²/gpm** |
| `unresolved` | STS / matrix(when dual) / occupancy(when gated) / voltage / oil class / Carrier not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, a synthetic route SI, a synthetic single-interlock electrical-room spine, a synthetic example dual-object SI, sheet mist/inert wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix then **return here**; density-area; power-isolation; transformer spray; releasing C&E; occupancy; lightning surge; clean-agent hand-away) |
| `RFI-variance` | SI/NI/foam/mist (or inert/clean-agent as company BOD) presented as BOD; or caller demands sealed DS 5-19 density with primary silent |
| `PRACTICE REFUSED` | Mist presented as controlling medium |

**Invented “DS 5-19 density” / a synthetic room ~2,000 ft² / calc 500–700–600 gpm as defaults → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Worked a synthetic room example MV room package, a synthetic adjacency example adjacency (no lineup deluge), a synthetic example dual-object, and worked examples batch = **`[SYN]` method only**. Do **not** copy room area, Route-A SI wet 0.2/2,500, dry/DI reservation 0.2/3,500, or cable-priced 0.2/3,000 demand envelopes as project defaults. SI spines = **comparison-only** under company fence. DS 5-48 smoke spacing remains **unheld** → `[V]`. **NO PLACEHOLDER.**

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent DS 5-19 density, room ft², demand gpm, 645 EPO counts, or lineup deluge. Do not treat SI/NI as company BOD. Do not elect foam/mist/clean-agent.

| Input | Required | Notes / Stop |
|---|---|---|
| the optional input packet (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`suppression` / `bod` / special-hazard / electrical). Do not rebuild; do not retrieve a job index. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. Electrical-room DI = consume if elected — do not invent. |
| **Consumed `most-stringent-basis-matrix` rows** | **yes when dual-carrier** | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever. Unresolved switchgear / electrical-room / dual-carrier rows → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **Consumed occupancy / HC pin** | **yes when rooms / HC feeds density** | From `occupancy-hazard-fork` (peer §9 MV gate). Missing when density path needs HC → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged / `handoff`. |
| **Voltage class** | **yes** | `>1000 V AC` (DS 5-19) / `≤1000 V AC` (fence → DS 5-20 / other). Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Breaker / insulation technology** | **yes** | vacuum / air / SF₆ / metal-clad / minimum-oil / bulk-oil / unknown. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged or structure-only `[V]`. |
| **Room construction + combustibles screen** | **yes** | Noncombustible? Storage? Other combustibles? Grouped cable? Bus duct from fire-risk area? Survey open → `[V]`. |
| **Carrier** | **yes** | FM / AXA / UFC / dual / n/a. Dual → matrix rows above. FM → DS 5-19 controlling Layer-2 for room package. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional: owner electrical-room DI preference (consume if STS-aligned); arc-resistant gear / redundancy note from EE; OH exposure for surge pointer; adjacent transformer yard (bus-duct interlock); cable tray takeoff for DS 5-31.

**Do not invent** DS 5-19 density, a synthetic room room ft², calc gpm envelopes, 645 EPO counts, or transformer deluge on the lineup. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the optional input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve a job index |
| `suppression-technology-selection` | Elected wet/dry/DI | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `most-stringent-basis-matrix` | Switchgear / electrical-room / dual-carrier rows when dual | Rebuild dual-carrier BOD; invent density |
| `occupancy-hazard-fork` | Occupancy / HC pin; peer §9 already routes MV here | Re-class occupancy; invent HC-2 as DS 5-19 density |
| `density-area-dry-increase` | Room / cable density×area when water path elected | Invent “DS 5-19 density”; paste hall numbers blindly |
| `power-isolation-disconnect-control` | Reciprocal fence — hall ITE EPO stays there | Treat DS 5-19 upstream breaker as 645 EPO |
| `power-block-transformer-water-spray` | Reciprocal fence — apparatus spray stays there | Deluge the switchgear lineup |
| `preaction-releasing-c-and-e-soo` | C&E when DI/releasing cells live | Author full water Boolean matrix here |
| `combustion-air-and-hall-free-area` | **Optional** when room vent / free-area interacts | Redesign genset combustion air |
| Freeze / lightning peers | Freeze-exposed piping / OH surge when present | Absorb freeze program or station-arrester design |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS, dual-carrier rows (when required), voltage, or oil class are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal HAND OFF lines (emit every run as applicable)

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency. Do **not** rewrite peers from this Skill.

- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — occupancy-hazard-fork: occupancy/HC pin; peer §9 MV gate routes here for room package.`
- `HAND OFF — most-stringent-basis-matrix: dual-carrier / electrical-room rows when dual. Consume; return here after.`
- `HAND OFF — the optional input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — density-area-dry-increase: room / DS 5-31 cable density×area — never invent DS 5-19 density.`
- `HAND OFF — power-isolation-disconnect-control: ITE/645/App. D hall EPO. This Skill owns DS 5-19 upstream-breaker-outside-room only — different object.`
- `HAND OFF — power-block-transformer-water-spray: apparatus spray / outdoor oil xfmr. This Skill fences switchgear = room-centric; no lineup deluge.`
- `HAND OFF — preaction-releasing-c-and-e-soo: full water Boolean / abort / cross-zone when DI releasing live.`
- `HAND OFF — out-of-scope clean-agent work: hand-away only; company does not design clean agent / inert as BOD.`
- `HAND OFF — lightning / surge corpus (DS 5-11): OH-fed gear station/junction arresters — not room FP substitute.`
- `HAND OFF — freeze-heat-trace-fp-piping: when freeze-exposed room FP piping / exterior valves.`
- `HAND OFF — combustion-air-and-hall-free-area: optional when room vent / free-area interacts.`

---

## 3. Decision tree / Steps

### 3.0 Step 0 — Hard scope + status register first

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent / inert as company BOD → Stop / hand-away.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier; occupancy when density gated. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status skeleton (§1.4). Restate **refuse invent DS 5-19 density / a synthetic room ft² / calc gpm defaults**. **NO PLACEHOLDER.**
4. Restate object thesis: **room problem → no lineup deluge**.

### 3.1 Step — Object class fence

| Object | This Skill action |
|---|---|
| Standard metal-clad / vacuum / air / SF₆ in noncombustible room, no other combustibles | **ROOM package** — continue |
| Minimum-oil CB, room noncombustible, no other combustibles | Treat as **non-oil** *(§2.2.1; App. C.1.4.1.1 ~10% of bulk)* — ROOM package |
| Bulk-oil CB / oil-insulated apparatus / switchgear exposed to other combustibles | Open **§2.2.3 fork** (§3.3) — still **not** transformer yard deluge |
| Outdoor oil-filled **transformer** | **Fence** → `power-block-transformer-water-spray` |
| ITE / data-hall EPO / NEC 645 | **Fence** → `power-isolation-disconnect-control` |
| Caller wants apparatus deluge on metal-clad lineup | **Stop** / refuse — wrong object class *(§2.2.1)* |

### 3.2 Step — Voltage fence

| Voltage | Action |
|---|---|
| **>1000 V AC** | DS 5-19 applies — continue *(§1.0)* |
| **≤1000 V AC** (e.g. 480 V switchboard) | Do **not** cite §2.2 as primary; route to DS 5-20 / owner / DS 5-32 / NFPA 13 room FP — record fence; status `handoff` / `comparison-only` if analogy used |
| Unknown | `ASSUMED` voltage class (value + why), flagged `[V]` — not a Stop |

### 3.3 Step — Oil / bulk-oil / company-media fork (§2.2.3)

**§2.2.3.1 Indoor bulk oil / ignitable-liquid apparatus** sheet options:

- **A.** Automatic sprinklers **OR** FM Approved **inert gaseous** extinguishing **OR** FM Approved **water mist** listed for **enclosures with machinery** (→ **DS 4-1**)
- **B.** Vent flammable vapor **to the exterior**
- **C.** Prefer **air / SF₆ / vacuum** over oil on new work

**Company overlay (mandatory):**

| Sheet option | Company action |
|---|---|
| Automatic sprinkler / preaction under wet\|dry\|DI | **Permitted path** — consume STS; prefer this for company BOD |
| FM Approved inert gas | **Hand-away only** — structure fork; do **not** design as company BOD |
| FM Approved water mist (DS 4-1) | **`PRACTICE REFUSED`** — record sheet evidence; do not design/accept mist BOD |
| Foam / foam-water | **Prohibited** — **Stop** even if other sheets surface foam |
| Prefer non-oil tech | **Recommend** — aligns sheet §2.2.3.1.C + hyperscale practice |

If mist/inert/foam presented as **BOD** → Stop / `PRACTICE REFUSED` / hand-away / `RFI-variance` as applicable. Do **not** invent a DS 5-19 oil-path density.

**§2.2.3.2 Forced-air-cooled bus ducts:** if cooling air is drawn from a potential fire location (e.g. outdoor oil-transformer yard) → **interlock** cooling fan with bus-duct CB **and** remote-area fire detection.

**§2.2.3.4 Portable extinguishers:** Class **A and C** *(note: sheet numbering jumps 2.2.3.2 → 2.2.3.4 — no 2.2.3.3 in held edition)*.

### 3.4 Step — Base room package (non-oil / minimum-oil clean room)

Elect / record each element *(§2.2.4–2.2.5, §2.1.5)*:

| Element | Election | Cite |
|---|---|---|
| Construction | Noncombustible room; gear separate from controlled / hazardous equipment | §2.2.1; §2.1.5.1 |
| Smoke type | **Photoelectric** or **photo + ionization** combo | §2.2.4 |
| Smoke destination | Alarm at **constantly attended** location; response includes personnel who can **de-energize or diagnose** | §2.2.4 |
| Smoke vs sprinklers | Smoke **does not** change need for sprinklers — **no omission credit** | §2.2.4 |
| Smoke spacing | per **DS 5-48** | §2.2.4 — **DS 5-48 unheld** → `[V]` |
| Room water | Sprinkler or preaction per **STS** / owner / DS 5-32 / NFPA 13 — **consume STS** | No density in DS 5-19 |
| Upstream isolation | Prefer **high-side breaker OUTSIDE** the electrical room, accessible in emergency | §2.2.5 |
| Pre-incident plan | Electrical + firefighting respond **together**; de-energize so FF is not delayed | §2.2.5 |
| Storage | **No** tools/supplies/materials in switch rooms or enclosures | §2.1.5.4 |
| Air | Slight **positive pressure** from **filtered** air source | §2.1.5.3 |
| Arc hygiene | Arc-resistant vents must not expose combustibles; room venting against overpressure | §2.1.5.2 |
| Critical arrangement (EE bind) | Arc-resistant **or** redundant **or** physical separation at tie; else preferably **≥5 horizontal sections** between primary-selective breakers | §2.3.5 — **not** FP density |
| Portable extinguishers | Class A and C | §2.2.3.4 |

**Do not conflate** upstream-breaker-outside-room with NEC 645 ITE hall EPO — emit HAND OFF to `power-isolation-disconnect-control`.

### 3.5 Step — Grouped-cable DS 5-31 fork

Per DS 5-19 §2.2.2 → protect grouped combustible insulated wires/cables per **DS 5-31**.

| Condition | Action |
|---|---|
| Significant combustible = grouped cable only (vault/tray/room) | Cable-only ceiling: **0.2 gpm/ft² over 3,000 ft²**, **165°F**, **130 ft²** spacing *(DS 5-31 §2.3.2.2.B, Jan-2020 / Int. Oct-2025)* — cite held primary; `[V]` if edition unconfirmed in run |
| Other combustibles share the protected area (oil CBs, storage, transformers) | Do **not** use cable-only density alone *(DS 5-31 §2.3.2.2.C)* — occupancy/equipment sheet |
| High trays obstruct ceiling | Sprinklers in **every aisle/walkway** *(DS 5-31 §2.3.2.2.1)* — detail via cable note / density peer |
| Gaseous / clean-agent alternative for cable | Sheet may open gaseous gates — company = **hand-away only**; mist not offered on DS 5-31 → refuse mist |

Hand density arithmetic to `density-area-dry-increase` when sealed demand is needed. Do **not** paste 0.2/3,000 into a data hall without DS 5-32 / occupancy check.

### 3.6 Step — Isolation architecture (switchgear room, not ITE)

1. Record **upstream (high-side) breaker outside the room** as preferred / load-bearing on hyperscale jobs where de-energize-before-fight is required *(§2.2.5 — sheet “may be needed”)*.
2. Pre-incident plan: electrical personnel respond **with** firefighting; de-energize so FF is not delayed.
3. Emit C&E interface flags: alarm + de-energize/diagnose capability **before or with** water release into energized gear.
4. **Do not** author full releasing matrix — HAND OFF to `preaction-releasing-c-and-e-soo` when DI/releasing live.
5. **Do not** invent EPO button counts, AFF heights, or 645 applicability — HAND OFF hall isolation to `power-isolation-disconnect-control`.

### 3.7 Step — Water path consume STS (no DS 5-19 density)

1. Consume STS `wet` | `dry` | `DI`. Electrical-room DI common owner preference = **consume if elected**, do not invent.
2. Density source honesty:
 - Standard non-oil room → **NFPA 13 / occupancy / DS 5-32 / owner** stack — **not** DS 5-19.
 - Cable-only → DS 5-31 **0.2/3,000** when applicable.
 - HC-2 Electrical Room from DS 3-26 App. C Table C-1 (via occupancy peer) does **not** invent a DS 5-19 density.
3. Hand sealed density×area / dry-increase math to `density-area-dry-increase`.
4. Do **not** take NFPA 13 electrical-room sprinkler **omission** on high-availability DC work (UFGS/UFC / owner often disallow) — record as practice fence, not invented section.
5. Calc / a synthetic room method examples (`*mv-ds519*` wet Route A / dry-DI reservation / cable) = **`[SYN]`** — refuse as sealed project defaults.
6. SI Route A in worked packages = **`comparison-only`** under company fence — never company BOD.

### 3.8 Step — Detection honesty

- Smoke type + constantly attended + de-energize/diagnose per §2.2.4 — **mandatory regardless of sprinklers/heat**.
- Spacing → DS 5-48 — **unheld** in corpus → `[V]` / submittal; do not invent spacing ft.
- Smoke ≠ sprinkler credit — restate every run.
- Optional VEWFD for business-critical cable rooms → detection peer / cable note — not a substitute for room water.

### 3.9 Step — Surge OH-fed pointer (not room FP)

If metal-clad gear is fed from exposed overhead circuits:

- Severe lightning + direct OH through roof bushings or noncontinuous metallic sheath → **station-type arresters** *(FM DS 5-11 §2.1.2.7.1 — April 2012 / Interim October 2025 when held)*.
- Continuous metallic-sheath cable to OH → arresters at **cable junction** (may also need at switchgear) *(§2.1.2.7.2)*.
- Ground electrode path ≤**1 ohm**; short leads *(§2.1.2.2)*.

**HAND OFF** detail to lightning-and-surge corpus / future Skill. Surge ≠ room FP substitute. Mist REFUSED unchanged.

### 3.10 Step — Δ layers + honesty close

Always print:

- **Δ vs NFPA 13-2025:** room water method / electrical-room omission practice; FM adds room-centric package, upstream-breaker architecture, smoke≠sprinkler-credit, oil fork — carry explicitly.
- Controlling layer per parameter (object, voltage, oil, room package, cable, isolation, water path, detection).
- `[SYN]` a synthetic room / calc / a synthetic example method vs sealed live room area / demand.
- Open RFIs (voltage confirm, oil class, room area, STS DI vs wet, DS 5-48 spacing, cable takeoff, OH surge exposure).

Edition cite form: **FM DS 5-19, October 2020, Interim Revision January 2024** (section **AND** edition). Filename “(2024)” = interim year only.

### 3.11 Step — Worked / calc honesty register (method only)

When citing training-ground spines, label each row:

| Spine | What it shows | Honesty |
|---|---|---|
| a synthetic room example Clearwater MV room (`…mv-switchgear-mn__mv-switchgear-room-fp`) | Room-centric package; upstream breaker; no lineup deluge; density from occupancy not DS 5-19 | **`[SYN]` method** — refuse ~2,000 ft² / SI Route A as defaults; SI = `comparison-only` under company fence |
| a synthetic adjacency example genyard adjacency (`…mv-switchgear-room-ds519-adjacency-no-lineup-deluge`) | Dual-object: transformer spray ≠ switchgear room | **`[SYN]`** — object fence method |
| a synthetic example MV DS 5-19 + adjacent DI white-space | Dual-object company-path illustration | **`[SYN]` illustrative** — never hall/room defaults |
| worked examples (room-demand-batch / wet-route-a / dry-di-reservation / cable) | Density×area **method** under HC-2 / cable-only stacks | **`[SYN]`** — 0.2/2500→500+250; 0.2/3500 dry-DI; 0.2/3000 cable — **not** sealed project Qd |

Do **not** promote any row to `grounded` project defaults. Company BOD remains STS wet|dry|DI only.

### 3.12 Step — Pitfalls (refuse these)

- **Deluging a metal-clad vacuum lineup** as if it were an oil transformer — wrong object *(§2.2.1)*.
- **Citing DS 5-19 for a 480 V switchboard room** without the >1000 V fence *(§1.0)*.
- **Taking smoke detection as permission to omit sprinklers** — sheet forbids *(§2.2.4)*.
- **Assuming minimum-oil needs the bulk-oil package** — FM treats minimum-oil as non-oil when room clean *(§2.2.1)*.
- **Conflating switchgear-room isolation with ITE EPO / NEC 645** — related physics, different articles/objects.
- **Inventing a DS 5-19 sprinkler density** — there is none for the standard room.
- **Using 0.2/3,000 when oil CBs, transformers, or storage share the room** — DS 5-31 §2.3.2.2.C blocks cable-only.
- **Electing mist / inert / foam as company BOD** from §2.2.3.1 sheet options — structure fork, then Stop / PRACTICE REFUSED / hand-away / prohibit.
- **Ignoring arc-resistant vent discharge** into cable/combustibles or skipping room overpressure vent *(§2.1.5.2)*.
- **Storage in the switch room** — explicitly prohibited *(§2.1.5.4)*.
- **Forced-air bus duct from transformer yard** without fan interlock *(§2.2.3.2)*.
- **Treating arc-resistant / 5-section gap as an FP density** — EE bind *(§2.3.5)*, not water design.
- **Using OH surge arresters as a substitute for room FP** — DS 5-11 pointer only.
- **Silent-substituting SI→DI** or inventing electrical-room DI without STS election.
- **Copying a synthetic room/calc gpm envelopes** as sealed campus demand.

---

## 4. Outputs / artifacts

Write **only** to the caller-named path (or return in-response and stop). Typical package:

1. **Status register** (§1.4) + Hard-scope fence result (STS consume; SI/NI/foam/mist/inert posture).
2. **Object / voltage / oil fence statement** — room-centric; no lineup deluge; >1000 V named.
3. **Base room package checklist** (§3.4) with cites.
4. **Cable DS 5-31 fork** result (apply / N/A / other-combustibles block) — density cited only when held.
5. **Isolation architecture note** — upstream breaker outside room + pre-incident plan; HAND OFF hall EPO.
6. **Water-path consume record** — STS token; density source honesty (not DS 5-19); handoff to density-area when sealed math needed.
7. **Oil-fork company overlay** when bulk-oil / exposed combustibles — Stop / PRACTICE REFUSED / hand-away as applicable.
8. **Open RFIs** — each with blocking/non-blocking tag.
9. **Reciprocal HAND OFF lines** to live peers.
10. **Δ vs NFPA 13-2025** + `[SYN]`/`[V]` register + edition pins.

Do **not** emit: invented DS 5-19 density, sealed a synthetic room/calc gpm as defaults, lineup deluge design, full water-path C&E rewrite, 645 EPO counts, transformer apparatus spray transcript, foam/mist/clean-agent BOD, a job index retrieval, CAD, or writes outside the caller-named output.

---

## 5. Stop

A missing input is not a stop. Proceed with a stated ASSUMED value (the value and why), flagged in the output and the status register. Company scope locks stay hard stops: single-interlock or non-interlock as the basis of design, foam, water mist, deluge, and clean agent as the basis of design.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent / inert as company BOD → Stop / hand-away only.
2. Missing the optional input packet → not a Stop (packet optional). Missing STS → `ASSUMED` (flagged), not a Stop. Missing matrix rows when dual → assume most-stringent row (`ASSUMED`, flagged) or hand off, then return.
3. Voltage or oil/technology class missing → stated `ASSUMED` class (flagged) / `[V]`, not a Stop; package is ASSUMED-based.
4. Caller demands sealed **“DS 5-19 density”** or sealed room ft²/gpm from a synthetic room/calc as universal → **Stop** / refuse invent.
5. Caller wants **apparatus deluge on metal-clad / vacuum lineup** → **Stop** / wrong object *(§2.2.1)*.
6. Caller treats DS 5-19 package as **NEC 645 ITE EPO** → **Stop** / handoff to `power-isolation-disconnect-control`.
7. Caller cites §2.2 as primary for **≤1000 V** room without naming voltage fence → **Stop** / correct fence.
8. Smoke presented as permission to **omit sprinklers** → **Stop** / sheet forbids *(§2.2.4)*.
9. Storage proposed in switch room as acceptable → record conflict; RFI — sheet prohibits *(§2.1.5.4)*.
10. Caller wants transformer yard spray, hall density×area ownership, full C&E rewrite, or CAD as this Skill’s deliverable → wrong Skill / handoff.
11. writes outside the caller-named output; a job index retrieve.

---

## 6. Citations (section AND edition)

| Claim | Pin | Status |
|---|---|---|
| Sheet voltage scope >1000 V AC; else DS 5-20 | FM DS **5-19, October 2020, Interim Revision January 2024** §1.0 p.3 | `grounded` |
| Noncombustible room; minimum-oil = non-oil; no FP if clean | §2.2.1 p.13; App. C.1.4.1.1 p.26 (~10% of bulk) | `grounded` |
| Grouped cable → DS 5-31 | §2.2.2 p.13 | `grounded` method |
| Cable-only 0.2 gpm/ft² / 3,000 ft² / 165°F / 130 ft² | FM DS **5-31** §2.3.2.2.B, **January 2020, Interim Revision October 2025** | `grounded` when primary held; else `[V]` |
| Oil path: sprinkler OR inert OR mist (DS 4-1 enclosure); vent exterior; prefer non-oil | §2.2.3.1 p.14 | Sheet `grounded`; mist/inert as BOD → company Stop / refuse / hand-away |
| Forced-air bus duct fan interlock + remote detection | §2.2.3.2 p.14 | `grounded` |
| Portable extinguishers Class A and C | §2.2.3.4 p.14 | `grounded` |
| Photo or photo+ion smoke; constantly attended; de-energize/diagnose; smoke ≠ sprinkler credit; spacing DS 5-48 | §2.2.4 p.14 | `grounded` method; DS 5-48 spacing `[V]` unheld |
| Pre-incident plan; upstream high-side breaker outside room | §2.2.5 p.14 | `grounded` |
| Positive pressure filtered air; no storage; arc-vent hygiene | §2.1.5.3 /.4 /.2 p.13 | `grounded` |
| Critical: arc-resistant / redundant / separation; preferably 5 horizontal sections | §2.3.5 p.14 | `grounded` EE bind — not density |
| No sprinkler density in DS 5-19 for standard non-oil room | Synthesis + source note Key numbers | `grounded` honesty |
| OH-fed surge station/junction arresters | FM DS **5-11** §2.1.2.7, April 2012 / Interim October 2025 (when held) | Pointer / handoff |
| Company fence wet\|dry\|DI; SI/NI Stop; foam prohibited; mist PRACTICE REFUSED; clean-agent hand-away | Shop locks / live peers | Hard scope §1 |

**Absent / `[V]` (refuse invent):** live room area ft²; sealed occupancy density as “DS 5-19”; DS 5-48 detector spacing tables; NFPA 13-2025 electrical-room omission section number as sealed cite without primary; owner Tier-A DI numeric standard; a synthetic room/calc gpm envelopes as universal defaults.

---

## 7. Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance`. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent / inert = hand-away only. Status every run. Packet optional; STS (+ matrix when dual) consumed when present, else `ASSUMED` (flagged). **NO PLACEHOLDER.** **Never present an assumed density / a synthetic room ft² / calc gpm as a DS 5-19 value — label ASSUMED + why.**
2. Three-layer most-stringent **per parameter** (object, voltage, oil, room package, cable, isolation, water path, detection).
3. **Object class first** — room vs apparatus. Do not deluge the lineup.
4. Voltage fence named every time §2.2 is cited. Smoke ≠ sprinkler credit restated.
5. Cite section **and** edition (DS 5-19 Oct-2020 / IR Jan-2024; DS 5-31 Jan-2020 / IR Oct-2025 when cable).
6. Show-and-verify density×area only via held peer / caller area — flag `[SYN]` / `[V]`; density source unheld → stated `ASSUMED` + `[V]`, not a Stop; never labeled “DS 5-19 density”.
7. Structure §2.2.3 oil fork honestly; company media fence before electing mist/inert/foam.
8. Hand ITE EPO, transformer spray, density arithmetic, releasing C&E, occupancy authorship, surge detail to peer Skills — do not absorb their scope.
9. Calc / a synthetic room / a synthetic example spines = `[SYN]` method — never campus defaults; SI spines = `comparison-only`.
10. Electrical-room DI common owner preference = consume if STS-elected — never invent as universal.

If notes conflict, **most-stringent wins** and both sources stay visible.

---

## 8. Not this Skill

| Work | Where |
|---|---|
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier BOD authorship | `most-stringent-basis-matrix` — consume+return when dual |
| Assignment packet authorship | the optional input packet — consume only |
| Occupancy / HC classification authorship | `occupancy-hazard-fork` — consume; peer §9 routes MV **here** |
| Room / cable density×area sealed math | `density-area-dry-increase` — handoff; never invent DS 5-19 density |
| NEC 645 / NFPA 75 / DS 5-32 App. D ITE hall EPO | `power-isolation-disconnect-control` — **reciprocal fence** |
| Outdoor oil-transformer apparatus spray / containment | `power-block-transformer-water-spray` — **reciprocal fence**; no lineup deluge |
| Full releasing C&E / SOO / water Boolean | `preaction-releasing-c-and-e-soo` |
| Hall DI ≤30 s delivery proof | `dry-preaction-water-delivery-screen` |
| Freeze program / heat-trace | `freeze-heat-trace-fp-piping` |
| Genset / hall free-area design | `combustion-air-and-hall-free-area` — optional handshake |
| Clean-agent concentration / enclosure / inert design | out-of-scope clean-agent work — **hand-away only** |
| OH surge / station arresters detail | Lightning-and-surge corpus (DS 5-11) — pointer only here |
| CAD / writes outside the caller-named output | forbidden |

---

## 9. Check sequence

0. **Hard scope + status register first.** STS = wet|dry|DI (consume — do not elect). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Clean-agent/inert as company BOD → Stop / hand-away. Packet if present (optional); matrix when dual (consume+return); occupancy when density gated. Emit status skeleton (§1.4). Restate **refuse invent DS 5-19 density / a synthetic room ft² / calc gpm**; **room problem → no lineup deluge**. **NO PLACEHOLDER.**
1. Pin DS 5-19 Oct-2020/IR Jan-2024; DS 5-31 Jan-2020/IR Oct-2025 when cable; DS 5-48 spacing `[V]`; DS 5-11 surge pointer when OH-fed; NFPA 13-2025 room delta posture.
2. Object-class fence — metal-clad/vacuum/air/SF₆ room vs bulk-oil fork vs transformer spray vs ITE EPO.
3. Voltage fence >1000 V AC; ≤1000 V → do not cite §2.2 as primary.
4. Oil fork §2.2.3 — structure sheet options; company Stop / PRACTICE REFUSED / hand-away on mist/inert/foam BOD; prefer non-oil + room water; bus-duct interlock if yard air.
5. Base room package checklist (§3.4) — smoke+attended, no sprinkler omission credit, no storage, positive pressure, pre-incident plan, upstream breaker outside room.
6. Cable DS 5-31 fork — 0.2/3,000 when cable-only and held; else occupancy sheet; hand density-area for sealed math.
7. Isolation architecture note + C&E interface flags; HAND OFF hall EPO and full releasing matrix.
8. Water path consume STS; density-source honesty; `[SYN]` calc/a synthetic room method only.
9. Detection honesty (DS 5-48 `[V]`); optional surge OH pointer; Δ vs NFPA 13-2025; status register complete; `[SYN]`/`[V]`; open RFIs; reciprocal HAND OFF lines.
10. Close every §1.4 row with a token + honesty tags. Refuse silent `grounded` on: invented DS 5-19 density, copied a synthetic room ft²/gpm, SI evidence as BOD, mist/inert sheet wording as company election, 645 EPO conflation, or lineup deluge.
11. Confirm write path = caller-named only. Do not write outside that path.

### method item-0 reminder (print verbatim when gated)

```
Hard scope: STS wet|dry|DI consumed — not elected here.
SI/NI-as-BOD → Stop RFI-variance (comparison-only only).
Foam prohibited. Mist = PRACTICE REFUSED. Clean-agent/inert = hand-away only.
Object: MV switchgear ROOM (DS 5-19) — no lineup deluge.
Voltage: >1000 V AC required to cite §2.2 as primary.
Refuse invent: DS 5-19 density; a synthetic room/calc room ft²/gpm defaults; 645 EPO counts.
Packet optional; STS consumed or `ASSUMED`; matrix when dual (consume+return).
```
