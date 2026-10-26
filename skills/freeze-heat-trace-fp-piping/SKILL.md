---
name: Freeze program and heat-trace for FP piping
description: >-
  use this when the site may be freeze-prone (100-year DMT / cold-climate map)
  and you must screen freeze exposure, elect heated-enclosure vs heat-trace vs
  dry/DI drain strategy for freeze-exposed FP piping, and structure the OEM FS
  heat-trace + FACP alarm / MasterSpec 210533 package — packet optional; STS
  wet|dry|DI consumed or ASSUMED; heat-trace ≠ heated DI valve house; heat-trace only wet runs
  that must stay wet; never silently invent DMT / cable W/ft / controller setpoints (state ASSUMED + why);
  SI/NI-as-BOD → Stop RFI-variance; foam prohibited; mist PRACTICE REFUSED;
  tank heaters handoff; not standpipe Class election, not N₂ plant, not CAD.
---

# Freeze program and heat-trace for FP piping

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe. **This Skill screens freeze exposure from the 100-year DMT / cold-climate map, elects the freeze strategy (heated envelope / heated valve enclosure vs heat-trace on wet-must-stay-wet vs dry/DI supervisory drain), structures the OEM FS vs non-FS heat-trace path + FACP low-temp / leak / circuit-supervision alarm schedule, and emits a generic MasterSpec §210533 / §210700 edit checklist** — after the assignment packet exists and STS has elected company `wet` | `dry` | `DI`.

It does **not** elect the hall sprinkler/preaction family (consume STS). It does **not** elect Class I standpipe type (consume `standpipe-class-i-election-and-demand`). It does **not** invent site DMT °F, OEM wattage tables, circuit amps, or controller setpoints as universal defaults. It does **not** size closed-top tank heaters (companion / handoff). It does **not** design foam, mist, CAF, or clean agent. It does **not** CAD cable routes.

**Core thesis:** Freeze protection is a **campus program** first (**FM DS 9-18, July 2022** when the site is freeze-prone), not a cable SKU. Step 0 is the **FM Worldwide Freeze Map** 100-year DMT — **never invent zone °F** from App. D overview figures. When **100-year DMT ≤ 20°F (−6.7°C)**, DS 9-18 applies: hold water-filled FP spaces **> 40°F (4°C)**; electric pump rooms **> 40°F**; diesel **> 70°F**; exterior preaction/dry/deluge valves in an **insulated heated enclosure** with temperature to a **constantly attended** location; plan utility loss **≥ 3 days**. Where 40°F cannot be held on a wet portion → dry / preaction / dry pendant / antifreeze **only when the occupancy sheet allows** — and company BOD remains **`wet` | `dry` | `DI` only** (consume STS; do **not** silently elect SI). **Heat-trace ≠ substitute for a heated DI / dry valve house** (DS 9-18 §2.2.6; OEM FS guides). Heat-trace applies only to **freeze-exposed wet runs that must stay wet**; declared dry standpipe / dry DI legs stay drained / empty — do **not** heat-trace them instead of draining. OEM **FS** (UL 515A / FM / c-UL-us VGNJ fire-sprinkler path) vs **non-FS** campus MEP path must be elected honestly — XL-Trace Edge trio (H58489 / H58033 / H55838) is a **held method example**, not a locked campus SKU. **Listing fence (held, H60742 2025 pp. 5/8):** the RAYCHEM 465 FS controller is c-UL-us / UL **VGNJ** listed with **5XLE / 8XLE only** — **12XLE is not on the 465 listed cable list**; a 12XLE FS circuit needs **separate listing evidence** (e.g. with C910-485 / ACS-30), otherwise solve with thicker / lower-k insulation or parallel runs. **Never invent DMT, cable W/ft, or controller defaults** — structure the register and **Stop / `[V]` / RFI** when the primary is unheld.

**Design practice:** three-layer most-stringent **per parameter** (map gate / applicability, ambient floors, valve-house vs heat-trace fork, wet-vs-dry leg strategy, OEM FS listing path, GFEP / backup power, FACP alarm schedule, MasterSpec 210533/210700 hooks, utility-outage / ERP). Delta vs **NFPA 13-2025** freeze / heated-enclosure §§ where held (else `[V]` — vendor often cites **13-2019 §8.3.1.8.2.3**). Cite **section AND edition**. Show-and-verify math. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**; clean agent = **hand-away only**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet (optional) + STS `wet`|`dry`|`DI` (consumed, else `ASSUMED`) (+ `most-stringent-basis-matrix` when dual — **consume and return here**). Consume standpipe type when freeze-exposed standpipe legs exist — do **not** re-elect Class. N₂ plant ≠ freeze program (`nitrogen-inerting-and-c-factor-gate`). Caller-path-only. **NO PLACEHOLDER.** Generic — do not copy Bismarck / Fargo / MN Becker geometry, nVent SKUs, or Thermon TCM2 printed setpoints as universal defaults. Owner may **raise, never lower**.

**Honesty — DMT / wattage / setpoints unheld as defaults.** Corpus holds **FM DS 9-18 (July 2022)** campus floors + App. C tracing preference; OEM FS design paths (RAYCHEM **H58489 / EN-2504 (2025)**, Chromalox **PX143**, Thermon **TEP0165**, Nelson **GA-2499 Rev.0 2015** ★dated); XL-Trace IOM **H58033 / EN-2602 (©2026)**; non-FS **H55838** (defers FS → H58489); MasterSpec wet §211313 §3.4.Q / standpipe §211200 §3.5.M → **210533 / 210700** hooks; worked Bismarck / Fargo packages as **`[SYN]` method**. **Now held (2026-10-05 mining):** H58489 pass-2 grids **Tables 1–7 and 9** (Qb, indoor / k multiples, voltage factors, valve / support adders, max circuit length, transformer A/ft); XL-Trace data sheet **H51349 / EN-2504 (2025)** (8XLE ≈ **8.8 W/ft @ 40 °F** on metal — **graph read**, not printed; min install **0 °F**; 50/65 °F start-up rows = 110 °F maintain only); RAYCHEM **465 IOM H60742 (©2025)** (VGNJ listing scope, seven-condition supervisory relay, OEM defaults). Live site **100-year DMT °F**, Fig. 11 curves as printed numbers, grid rows below **−20 °F** start-up, TraceCalc outputs, and the **NFPA 13-2025** valve-enclosure section number are **not** held / not sealed defaults. Recipe structure is **Ready**; sealed DMT / sealed W/ft / sealed controller setpoints → **Stop / `[V]` / RFI**.

Write the freeze / heat-trace package **only** to the path the **caller** names. Write output only to the caller-named path.

Look up shop codebook notes **by title**: *Freeze prevention / 100-year DMT and cold-climate FP*; *Design practice*; *Enforced-vs-latest edition resolver*; *Standpipe & hose systems (NFPA 14)*; *ITM basis and design for testability*; *Water tanks for fire protection* (tank-heater companion handoff).

---

## 1. Hard scope gate

### 1.1 Company system-family fence (consumes STS — does not elect)

This Skill owns **freeze exposure screen, freeze strategy election (heated envelope / heated valve enclosure / heat-trace / dry-leg drain), OEM FS vs non-FS path structure, FACP freeze/heat-trace alarm schedule structure, and MasterSpec §210533 / §210700 edit checklist**. Controlling company BOD for sprinkler/preaction families = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI (hall / campus BOD) | `suppression-technology-selection` (**consume** — do not elect here) |
| Freeze program / heat-trace strategy / FACP freeze points / 210533 checklist | **This Skill** |
| Dual-carrier per-parameter union | `most-stringent-basis-matrix` (**consume**, then **return here**) |
| Standpipe Class I / type / residual / demand | `standpipe-class-i-election-and-demand` (**consume** type; do not elect) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**This Skill does not elect hall families.** It **consumes** the completed the input packet and the STS token `wet` | `dry` | `DI`, then runs the freeze recipe. Freeze strategy may **force dry/DI legs** on freeze-exposed portions — that is a **posture consequence**, not a silent SI election. If freeze forces a family change vs the packet STS token → **Stop** / handoff to STS reconcile — do **not** silently substitute SI.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family on the packet:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue freeze arithmetic as if SI/NI were company-elected BOD.
6. SI/NI may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler / preaction | Permitted when elected upstream via STS | Record freeze consequences under that BOD; do not elect |
| Heat-trace on freeze-exposed **wet** FP piping (FS listed path) | **In scope here** | Structure OEM path + alarms; refuse invent W/ft |
| Heated valve enclosure for exterior DI/dry/deluge | **In scope here** (mandatory when freeze-exposed exterior valves) | Elect enclosure; heat-trace ≠ substitute |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water / CAF | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do **not** design/accept mist as BOD |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent; Never company BOD here |
| Closed-top suction / gravity **tank heaters** | **Handoff** | Route to tank companion / DS 3-2 — not core of this Skill |
| Antifreeze as white-space BOD | **Stop / RFI** unless listing + AHJ + occupancy sheet force in writing | Prefer dry/DI; do not elect antifreeze by habit |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Clean agent = hand-away only. Tank heaters = companion handoff.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| 100-year DMT map gate structure (refuse invent °F) | Invent site zone °F from App. D overview |
| DS 9-18 campus ambient / pump-room / utility-outage floors | System-family election (`suppression-technology-selection`) |
| Strategy fork: heated envelope vs heat-trace vs dry/DI drain | Standpipe whether / Class / residual / gpm (`standpipe-class-i-election-and-demand`) |
| Heated valve enclosure mandatory fence (trace ≠ substitute) | N₂ purity / C-factor / AMD plant (`nitrogen-inerting-and-c-factor-gate`) |
| OEM FS vs non-FS path election + honesty | Hall DI ≤30 s delivery proof (`dry-preaction-water-delivery-screen`) |
| FACP low-temp / leak / HT circuit supervision **schedule structure** | Invent OEM W/ft / circuit max / TCM2 Maintain 38°C as campus floor |
| MasterSpec §210533 / §210700 edit checklist (generic) | Tank heater Btu / DS 3-2 Tables 6–13 (companion handoff) |
| Utility ≥3-day / freeze ERP handshake flags | Private-main frost depth rebuild (`campus-looped-main-sizing` / DS 3-10 peer) |
| Freeze memo + open RFIs | CAD cable/clip coordinates; foam/mist/clean-agent BOD |
| Optional valve-house free-area note | Combustion-air / hall OA% design (`combustion-air-and-hall-free-area` — optional handshake only) |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet + STS (+ matrix when dual), **(c)** map gate / 100-year DMT, **(d)** campus ambient floors, **(e)** strategy fork (envelope / trace / dry), **(f)** valve-house fence, **(g)** wet-must-stay-wet takeoff scope, **(h)** OEM FS vs non-FS path, **(i)** GFEP / backup power, **(j)** FACP alarm schedule, **(k)** MasterSpec 210533/210700 checklist, **(l)** utility-outage / ERP, **(m)** tank handoff if tank present, and **(n)** mist/foam/clean-agent if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling election + editions supported by opened DS 9-18 / OEM FS guide pins already closed for that parameter |
| `provisional` | Directionally pinned; live map DMT / start-up below −20 °F (TraceCalc) / (NFPA 13-2025 enclosure § now held: §8.3.1.7.2.3, pull 13-01) / Fig. 11 curve values flagged `[V]` — **never silent `grounded` on invented DMT or W/ft** |
| `unresolved` | STS / matrix(when dual) / freeze-exposed geometry / standpipe type(when freeze legs) not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, Nelson 2015 dated path, Chromalox/Thermon peer FACP lists when another OEM is elected, secondary blog |
| `handoff` | Peer owns next action (STS family; matrix then **return here**; standpipe type consume; dry-delivery; N₂ gate; ITM; tank heaters; combustion-air free-area if valve-house interacts) |
| `RFI-variance` | SI/NI/foam/mist presented as BOD; or caller demands sealed DMT/W/ft with primary unheld and refuses RFI |
| `PRACTICE REFUSED` | Mist presented as controlling medium |

**Invented site DMT °F / OEM W/ft / controller setpoints as defaults → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Worked Bismarck XL-Trace trio + Fargo single-OEM FACP packages = **`[SYN]` method** only. Do **not** copy −20°F BOD Ta, 12XLE2 / 8XLE2 SKUs, ACS-30 channel counts, or synthetic pipe lengths as project defaults. MN Becker / Duluth −35°F / Chicago −20°F = **illustration** zones in DS 3-2 / OEM worked cells — **not** this site. Nelson GA-2499 **2015** = dated compare; refuse as primary without current listing letter. Thermon TCM2 printed **Maintain 38°C** ≠ DS 9-18 / H58489 **40°F** campus floor. **NO PLACEHOLDER.**

**Negative case (carry as a lesson, do not retrieve):** a worked example (Bismarck XL-Trace retest, verdict corpus-insufficient, `[SYN]`) — the earlier 2026-09-21 package elected **12XLE2 + ACS-30 on FS pipe**, which sits **outside the held VGNJ listing** (465 + 5XLE/8XLE). The retest re-solved with **5XLE2 + thicker FG insulation** (3 / 2 / 1½ in.) and **3 × 15 A / 30 mA, 3 × 465**, and flagged that Tables 7/9 stop at **−20 °F** start-up (colder Ta → TraceCalc). Lesson: check the listing fence **before** cable selection; do not copy the retest's lengths, Ta, or SKUs.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent DMT °F, OEM wattage, or controller defaults. Do not treat SI/NI as company BOD. Do not elect foam/mist/clean-agent. Do not elect standpipe Class.

| Input | Required | Notes / Stop |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`suppression` / `bod` / climate / water-supply). Do not rebuild; do not retrieve prior job files. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Consumed `most-stringent-basis-matrix` rows** | **yes when dual-carrier** | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever. Unresolved freeze / ambient / valve-house rows → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **Site location for Freeze Map** | **yes** | City / county / lat-long sufficient for live FM Worldwide Freeze Map lookup. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **100-year DMT °F (or explicit map-pending flag)** | **yes** | Caller supplies opened map value **or** accepts `provisional` + `[V]` until map pulled. **Never invent** from App. D. |
| **Freeze-exposed FP geometry screen** | **yes** | Which legs are wet continuous / dry / exterior valves / pump room / FDC / canopy / buried. Survey open → `[V]`. |
| **Consumed standpipe type** | **yes when freeze-exposed standpipe legs** | From `standpipe-class-i-election-and-demand` (Manual/Automatic × Wet/Dry). Missing when freeze legs → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged / `handoff`. Do **not** elect Class here. |
| **Carrier** | **yes** | FM / AXA / UFC / n/a. Dual → matrix rows above. FM → DS 9-18 controlling Layer-2. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional: owner colder design-day / longer fuel autonomy; elected OEM FS brand (or “parameterize trio”); existing TraceCalc / listing letters; tank presence (triggers handoff); valve-house free-area interaction with combustion-air Skill.

**Do not invent** site DMT, −20°F as universal Ta, nVent 12XLE2 as universal cable, ACS-30 / 465 / ITC-FS / TCM2-FX as universal controller, or Thermon Maintain 38°C as campus floor. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `most-stringent-basis-matrix` | Freeze / ambient / dual-carrier rows when dual | Rebuild dual-carrier BOD; invent DMT |
| `standpipe-class-i-election-and-demand` | Consumed standpipe type for wet/dry leg fork | Elect whether / Class / residual / gpm; heat-trace a declared dry standpipe |
| `dry-preaction-water-delivery-screen` | Freeze/dry-leg interface when DI delivery shares plant | Re-run ≤30 s hall DI proof as heat-trace sizing |
| `nitrogen-inerting-and-c-factor-gate` | N₂ plant presence — **N₂ ≠ freeze** | Treat N₂ supervision as heat-trace substitute; invent C-factor here |
| `itm-design-for-testability` | Emit freeze ITM / heated-enclosure / no-heat-tape-substitute flags | Duplicate full ITM interval calendar / AGF matrix |
| Future / tank Skills | Tank present → **handoff** DS 3-2 heater path | Size tank Btu / invent zone for Tables 6–9 here |
| `combustion-air-and-hall-free-area` | **Optional** when valve-house free-area / louver interacts | Redesign genset combustion air or hall OA% |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS, dual-carrier rows (when required), site pin, or standpipe type (when freeze legs) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Outbound this draft.** Do **not** restamp peers in this write.

| Peer | They own | This Skill owns |
|---|---|---|
| the input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume** STS; freeze may force dry/DI legs → handoff reconcile; SI/NI → Stop; mist `PRACTICE REFUSED`; foam prohibited |
| `most-stringent-basis-matrix` | Per-parameter union / dual-carrier rows | **Consume only** when dual — then elect freeze package **here** |
| `standpipe-class-i-election-and-demand` | Class I / type / residual / demand | **Consume** type; emit wet-vs-dry freeze fork consequences; do not re-elect Class |
| `dry-preaction-water-delivery-screen` | Hall DI ≤30 s / volume-cut | Freeze/dry-leg interface only; not heat-trace W/ft |
| `nitrogen-inerting-and-c-factor-gate` | N₂ plant / C=100 / AMD | **N₂ plant ≠ freeze program**; do not conflate |
| `itm-design-for-testability` | ITM features / heated-enclosure verify / no heat-tape substitute | Emit freeze ITM flags; do not duplicate product matrix |
| `combustion-air-and-hall-free-area` | Genset / hall free area | **Optional** handshake only if valve-house free-area interacts |
| Clean-agent Skills | Clean-agent concentration / enclosure | **Hand-away only** |
| Tank companion (future / DS 3-2 path) | Tank water hold / heater Btu | **Handoff** — out of core scope |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — the input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; freeze-forced dry/DI legs → reconcile; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: dual-carrier / freeze-ambient rows when dual. Consume; return here after.`
- `HAND OFF — standpipe-class-i-election-and-demand: consume standpipe type; do not elect Class; dry legs stay dry.`
- `HAND OFF — dry-preaction-water-delivery-screen: freeze/dry-leg interface only; not HT W/ft.`
- `HAND OFF — nitrogen-inerting-and-c-factor-gate: N₂ plant ≠ freeze; do not conflate supervisory gas with heat-trace.`
- `HAND OFF — itm-design-for-testability: freeze ITM / enclosure verify / no heat-tape substitute flags — peer owns checklist layer.`
- `HAND OFF — combustion-air-and-hall-free-area: optional only if valve-house free-area interacts.`
- `HAND OFF — tank companion / DS 3-2: tank heaters out of core — handoff when tank present.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first (Method item 0)

Before map / strategy / OEM / FACP arithmetic:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier; standpipe type when freeze-exposed standpipe legs. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix / map / ambient / strategy / valve-house / wet takeoff / OEM path / GFEP·backup / FACP / 210533 / utility-ERP / tank / Δ (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER.** anywhere in the run.
5. Restate refuse-invent: **no invented site DMT °F**; **no invented OEM W/ft / circuit amps / controller setpoints as sealed defaults**; Bismarck/Fargo/MN worked packages are **method**, not silent defaults.

### 3.1 Pin editions (cite section AND edition)

| Instrument | Role | Shop pin / honesty |
|---|---|---|
| **FM DS 9-18, July 2022** | Campus freeze program (map gate, ambient floors, valve house, ≥3-day, App. C) | **Controlling Layer-2** when freeze-prone / FM-insured. Cite section AND July 2022. |
| **FM Worldwide Freeze Map** | 100-year DMT °F site pin | Live www.fmglobal.com — **refuse invent** from App. D overview |
| **FM DS 3-2** (Oct 2015 / Int. Rev. Jul 2022) | Tank heaters companion | **Handoff** — not core |
| **FM DS 3-7 / 3-10 / 10-1 / 1-24 / 5-23** | Pump-room detail / main frost / ERP / leak / emergency power | Pointers — consume, do not rebuild full sheets here |
| **OEM FS design** (elected brand) | Heat-loss / cable / controller / FACP contacts | Parameterize. Held method example: RAYCHEM **H58489 / EN-2504 (2025)**. Peers: Chromalox **PX143**; Thermon **TEP0165**; Nelson **GA-2499 (2015)** ★dated |
| **OEM FS IOM** | Install / GFEP / megger / IR | Held example: **H58033 / EN-2602 (©2026)** — cite owning OEM IR gate |
| **OEM FS cable data sheet** | Cable output / ratings / circuit table colour | Held example: RAYCHEM **H51349 / EN-2504 (©2025)** — 8XLE output is a **graph read**; min install **0 °F**; approvals defer to H58489 / H55838 |
| **OEM FS controller IOM** | FS listing scope / FACP contacts / defaults | Held example: RAYCHEM **465 IOM H60742 (©2025)** — VGNJ with **5XLE/8XLE only**; indoor TYPE 12, 32–105 °F; branch CB **≤30 A** |
| **OEM non-FS campus** | General water / grease / fuel | Held example: **H55838** — **explicit deferral FS → H58489**; do not size FS from non-FS tables |
| **MasterSpec §210533 / §210700** | Div-21 heat-trace + insulation hook | Hooked from wet §211313 §3.4.Q and standpipe §211200 §3.5.M (Victaulic ARCOM 2013 templates) — edit before CD |
| **NFPA 13-2025** | Freeze / listed tracing / valve-enclosure delta baseline | Valve-enclosure clause (vendor cite **13-2019 §8.3.1.8.2.3**) [CODE NFPA 13-2019 §8.3.1.8.2.3; 2022 §8.3.1.8.2.3; 2025 §8.3.1.7.2.3, pull 13-01] |
| **IEEE 515.1** (edition per OEM) | Monitoring / spray-shadow pattern | Coordination — cite OEM-held edition |
| **UL 515A** (when Chromalox/Thermon path) | FS freeze listing class | Honesty vs RAYCHEM c-UL-us VGNJ / 465 path — do not conflate listing language |

**Do not cite Bismarck Art. 45-18 / Fargo 5 psi / a local dry-standpipe ban as universal.** Ask per jurisdiction.

### 3.2 Parameters, separately (three-layer union)

| Parameter | Code floor (L1) | Insurer (L2) | Owner (L3) | Method action |
|---|---|---|---|---|
| **A. Map / applicability** | Climate / AHJ freeze rules | DS 9-18 ≤20°F 100-yr DMT | May apply warmer voluntarily | Live map; refuse invent °F |
| **B. Ambient floors** | NFPA 13 40°F trigger [CODE NFPA 13-2019/2022 §16.4.1.1, pull 13-01]; 2025 §16.4.1.1 drops the 40°F trigger (subject to freezing, judged by average annual extreme minimum per §16.4.1.1.1) | DS 9-18 >40°F wet spaces; pump >40/70 | May raise | Stamp DS floors when FM; else provisional |
| **C. Valve house** | Listed enclosure / heated room `[V]` vs 13-2025 | DS 9-18 §2.2.6 mandatory exterior | May raise | Trace ≠ substitute — hard fence |
| **D. Strategy fork** | Wet only if heated; else dry/preaction | §2.2.7 system-type fork | DI/N₂ often already elected | Consume STS; force dry/DI legs honestly |
| **E. Heat-trace scope** | Listed electrical tracing allowed | App. C preference; OEM FS listing | Brand preference | Wet-must-stay-wet only |
| **F. OEM path** | UL 515A / Listed | FM Approved where sheet requires | May lock brand | Elect FS vs non-FS; parameterize SKUs |
| **G. Supervision** | FACP supervisory of freeze/HT | DS 9-18 §2.3.1 low-temp + leak | NOC / attended | Alarm schedule structure |
| **H. Utility / ERP** | — | ≥3-day loss + fuel; DS 10-1 ERP | May lengthen | Flags + handoff ITM/ops |
| **I. Tank** | NFPA 22 [CODE NFPA 22-2023 §16.1.2 (coldest water ≥42°F), §16.1.2.2 (low-temp alarm 40°F), pull 22-01; FM's −5°F heat trigger is not the NFPA 22 trigger, which is the lowest one-day mean temperature per §16.1.2.1] | DS 3-2 42°F / −5°F heat trigger | — | **Handoff** companion |

Most-stringent wins **per row**. Name the controlling layer. Owner may raise, never lower.

### 3.3 Step — Map gate (100-year DMT)

1. Record site location (city/county or coordinates).
2. Require **live FM Worldwide Freeze Map** 100-year DMT °F (warm-side zone value). App. D overview figures in the PDF are **not** a site pin.
3. Gate: if **100-year DMT ≤ 20°F (−6.7°C)** → DS 9-18 recommendations **apply** (freeze-prone). If warmer → sheet not mandatory; may still apply voluntarily / by owner — record Layer-3.
4. If map not yet pulled → status `provisional` / `unresolved` on parameter A; **do not invent** °F from climate class narratives (Bismarck / Fargo / MN Becker).
5. Routing sentence form (fill only held values): *Site 100-year DMT per FM Worldwide Freeze Map [ZONE °F]; campus freeze per FM DS 9-18 (July 2022); FS heat-trace per [elected OEM guide + edition]; heated valve enclosure per DS 9-18 §2.2.6 (trace ≠ substitute).*

### 3.4 Step — Campus ambient / program floors (DS 9-18)

Apply when gate yes (or owner adopts). Stampable without inventing zone °F:

| # | Requirement | Cite |
|---|---|---|
| 1 | Water-filled FP spaces (incl. concealed / stair / above ceiling at exterior walls) **> 40°F (4°C)** | §2.2.1 |
| 2 | Prefer **not** wet pipe in exterior walls | §2.2.3 |
| 3 | Electric fire-pump room **> 40°F**; diesel **> 70°F** | §2.2.4 → DS 3-7 |
| 4 | Exterior risers incl. **preaction / dry / deluge** → **insulated heated enclosure** + temp to **constantly attended** location | §2.2.6 |
| 5 | Cannot hold ≥40°F on a portion → dry / preaction / dry pendant / antifreeze **per occupancy sheet** | §2.2.7 |
| 6 | Private-main frost cover → DS 3-10 | §2.2.8 |
| 7 | Low-temp alarms + FM Approved leak detection to attended location | §2.3.1 → DS 1-24 |
| 8 | Utility-outage freeze analysis **≥ 3 days**; emergency fuel **≥ 3 days** | §2.4.1 B / §2.4.5 → DS 5-23 |
| 9 | Freeze ERP + annual exercise | §2.7 → DS 10-1 |
| 10 | Insulation without flow does **not** prevent freeze | §3.3 |
| 11 | Self-reg spiral spacing ≥ **2 in. (50 mm)** when App. C tracing used | App. C.1.2 |

Put freeze-critical heaters (valve house, pump room, HT controllers) on **generator-backed** power aligned to the ≥3-day basis.

### 3.5 Step — Strategy election (envelope vs heat-trace vs dry/DI)

**Decision order (do not skip):**

1. **Can continuous building / space heat hold >40°F** on the water-filled portion? → Prefer heated envelope; minimize wet pipe in exterior walls.
2. **Exterior DI / dry / deluge valves?** → **Heated insulated enclosure** mandatory under DS 9-18 §2.2.6. Heat-trace on wet supply **into** the house is allowed; heat-trace **shall not** replace the house.
3. **Portion cannot hold ≥40°F?** → Convert that portion to **dry / DI / dry pendant** per occupancy — **consume STS**. If STS is wet but freeze forces dry/DI → **not a Stop**: carry that portion as `ASSUMED` dry/DI (flagged) and hand off STS reconcile — **never** elect SI.
4. **Wet runs that must stay wet** in freeze exposure (FDC approach, wet Class I in conditioned path with residual outdoor segment, canopy wet branch, etc.) → **heat-trace + insulation** on the FS listed path.
5. **Declared dry standpipe / dry DI / N₂-filled hall pipe** → **drain / empty / supervisory gas** — **do not heat-trace** instead of draining. MasterSpec standpipe §3.5.M is **wet-type only**.
6. Antifreeze white-space → **Stop / RFI** unless written listing + AHJ + occupancy force.
7. Mist → `PRACTICE REFUSED`. Foam → **Stop**.

**Hard fence (load-bearing):** **Heat-trace ≠ substitute for heated valve enclosure.** Held by DS 9-18 §2.2.6 **and** OEM FS guides (H58489 p.21 vendor cite NFPA 13-2019 §8.3.1.8.2.3; [CODE NFPA 13-2019 §8.3.1.8.2.3; 2022 §8.3.1.8.2.3; 2025 §8.3.1.7.2.3, pull 13-01]).

### 3.6 Step — Wet-must-stay-wet takeoff scope (structure only)

Build a takeoff **register** of freeze-exposed **water-filled** FP pipe only:

| Column | Content |
|---|---|
| Tag | HT-FS-## / VH-## |
| Service | Wet supply / FDC / wet standpipe feed / canopy wet branch / etc. |
| Pipe (IPS / material) | Metal preferred for FS UL paths that ban plastic |
| Location | Outdoor / canopy / buried / into valve house |
| Insulation type/thickness | Parameterize |
| Strategy | Heat-trace **or** heated enclosure (never cable-alone for exterior DI/dry valves) |

**Out of HT scope by default:** DI / dry hall pipe under N₂ or air; dry exterior Class I standpipe legs; plastic FS pipe where elected OEM listing bans it; tank heaters (handoff).

Lengths / IPS from BIM or field measure — label `[V]` / `[SYN]` if synthetic screening only. **No SprinkFDT invent.**

### 3.7 Step — OEM FS vs non-FS path election + honesty

| Path | Owns | Maintain (typical held) | Controller honesty | Cable honesty |
|---|---|---|---|---|
| **FS** sprinkler / wet standpipe / wet supply / branch-with-heads | Elected **FS** design guide | **Tm 40°F (4°C)** water (DS 9-18 / H58489 / PX143) | FS shortlist only (example RAYCHEM: **465 / C910-485 / ACS-30** + FACP) — the shortlist is **not interchangeable for listing**: the 465 VGNJ listing carries **5XLE/8XLE only** (H60742 pp. 5/8); do **not** use non-FS roster as FS | FS-listed path (example: **5XLE / 8XLE** with 465); **12XLE only with separate listing evidence**, else insulation / lower-k / parallel runs; never 3XLE; XL-Trace Edge **NOT UL listed on plastic FS pipe** |
| **Non-FS** campus MEP (domestic/process water, grease, fuel) | Non-FS guide (example **H55838**) | Water/fuel ~40°F; grease often **110°F** (OEM) | Non-FS roster (example ECW-GF / 460 / …) — **fence out of FS LOD** | May allow general-water plastics / 3XLE — **does not** relax FS plastic fence |
| **Install / GFEP / IR / ITM** | Owning OEM IOM (example **H58033**) | — | IOM roster; FS still prefer FS shortlist | Cite **owning OEM** IR gate (example H58033 **>1000 MΩ** vs Thermon **≥20 MΩ** — do not cross) |

**Parameterize brand.** XL-Trace Edge trio is a **held method example**, not a locked every-job SKU. Chromalox PX143 / Thermon TEP0165 = UL 515A peers. Nelson 2015 = dated — refuse primary without current listing letter + occupancy/size fence check (printed OH-only / ≤6 in. may sit outside hyperscale).

**Refuse invent:**

- Qb outside the held Table 1 range (IPS ½–20 in. × insulation 0.5–4 in. × ΔT 20–150 °F; interpolate inside it) or for a non-RAYCHEM OEM → stated `ASSUMED` Qb (value + why) / TraceCalc / `[V]`, flagged — do not paste foreign OEM W/ft as if cited.
- Cross-copy CPR ↔ XLE ↔ FLX ↔ CLT wattage tables.
- Thermon TCM2 Maintain **38°C** as DS 9-18 **40°F** floor.
- H55838 tables to size **FS** circuits (explicit deferral).
- Non-FS controller (e.g. 460 / ECW-GF) as the **FS** controller when FS shortlist exists.
- 12XLE on an FS circuit on the strength of the H58489 p. 3 general-purpose block or the 465 shortlist — **refuse** without separate listing evidence (negative case a worked example).
- A 50 °F or 65 °F start-up row of Table 7 / H51349 for a 40 °F freeze circuit — those rows are **110 °F maintain only** (red in source); overstates allowable length.

**Sizing method spine (when OEM guide held — show-and-verify):** ΔT = Tm − Ta → Qb (table) → insulation/indoor multiples → select cable ≥ Qcorrected → length = pipe + valve/support/sprinkler adders + kits → circuit max vs start-up Ta / GF CB → transformer kW. Use OEM software (e.g. TraceCalc Pro) when grids incomplete. **Ta = live map / project design-day — never silent −20°F default.**

**Grid fences (held 2026-10-05, H58489 Tables 7/9 + H51349 p. 2):**

| Fence | Rule | Pin |
|---|---|---|
| Coldest start-up row | Grids end at **−20 °F** start-up; colder start-up / Ta → **TraceCalc** (or OEM calc), `[V]` until stamped | H58489 Tables 7/9; case-bi |
| 50 / 65 °F start-up rows | **110 °F maintain only** — never used for freeze (40 °F) circuits; freeze rows are −20 / 0 / 20 / 40 °F | H51349 p. 2 colour read |
| Cable ladder at 40 °F (metal, nominal) | 5XLE 5.6 (printed) · 8XLE ≈ **8.8** (graph read) · 12XLE2 12.4 (printed) W/ft, then × Table 4 voltage factor (208 V: 0.90 / 0.94 / 0.88) | H58489 p. 19 / Table 4; H51349 p. 3 |
| Printed example errors | Standpipe Step 2 applies 0.88 to Qb (8.6) — correct is 12.4 × 0.88 = 10.9 ≥ 9.8; branch prints 0.97 where Table 2 gives 0.79 | H58489 pp. 19–21 (a check check) |
| Minimum install temperature | **0 °F (−18 °C)** — a **construction-schedule** constraint for winter installs, not a design-Ta limit | H51349 p. 2 |
| GFEP | Every heating-cable branch circuit; smallest appropriate GF CB | H58489 p. 22 |

Run ΔT / Qcorrected / length / kW arithmetic through `calcs/fp/run.py` only if the op exists; otherwise show the arithmetic inline as a printed pin — **do not invent a kernel op**.

**Shared FS fences (held class — confirm on elected OEM):** GFEP on **each** heating-cable branch circuit; alarm dry contacts → **FACP**; backup power covers freeze loads; buried: jacket class + no buried splices/tees + connections above grade (depth still DS 3-10 for mains); sprinkler insulation **spray-shadow** / head rating coordination (often ≥**155°F / 68°C** peer fence — apply as coordination, not W/ft paste).

**465 controller fences (held, H60742 ©2025 — confirm at submittal on the elected OEM):** indoor only (TYPE 12, ambient **32–105 °F**) within **328 ft** of the sensor point, ambient sensor representative of the sprinkler piping incl. elevation; one 465 per circuit; branch CB **≤30 A**; non-combustible insulation with sealed non-combustible (metal) cover; min sprinkler rating **155 °F**. **Factory defaults are OEM values, not campus floors — schedule as `confirm at submittal`:** setpoint **40 °F** / low-temperature supervisory **35 °F** / GF supervisory 20 mA / **GF trip 30 mA** (latching). **External contactor** → the 465 can no longer monitor load or GF current → a **separate GFEPD is required** (H60742 pp. 10, 16). Carry the relay conflict (IOM DPST vs H58489 Table 14 SPST) — IOM controls; confirm cut sheet.

### 3.8 Step — FACP / supervisory alarm schedule (handshake)

Emit a **schedule structure** — map points to elected controller contacts at submittal (do not invent undocumented ACS/ITC/TCM2 point IDs as sealed):

| Point class | Condition | Type | Notes |
|---|---|---|---|
| HT-AL-GF | Ground-fault trip any HT circuit | Supervisory | Mandatory GFEP class |
| HT-AL-LT | Low pipe / low ambient vs maintain intent (**40°F** Tm) | Supervisory | Protect freeze — not release; 465 OEM default low alarm 35 °F = confirm at submittal |
| HT-AL-HT | High pipe temp | Supervisory | Insulation / SSR / sensor |
| HT-AL-SF | Sensor / RTD / thermistor fail | Supervisory | |
| HT-AL-CF | Controller / relay fail | Supervisory | |
| HT-AL-LC | Loss of continuity | Supervisory | Peer-complete list (PX143 shape); 465 relay carries it (H60742 p. 14) |
| HT-AL-PV | Loss of supply voltage / power | Supervisory | Confirm backup transfer |
| VH-AL-LT | Valve-house low temperature | Supervisory | **Priority** — DI/dry valve freeze |
| VH-AL-HF | Valve-house heater fail | Supervisory | |
| PR-AL-LT | Pump-room low temperature | Supervisory | |
| FP-AL-LEAK | Leak detection (DS 1-24) | Supervisory | Where provided |
| FP-AL-IMP | Freeze impairment / OOS | Supervisory | DS 10-1 procedures |

All HT / freeze points are **supervisory / trouble**, not automatic suppression release. **No cross-zone DI trip from heat-trace alarms.** Coordinate Div 28 / FACP / NOC attended monitoring.

### 3.9 Step — MasterSpec §210533 / §210700 edit checklist (generic)

Emit project-agnostic checklist (not a pasted Bismarck 21 05 33 BOD):

| Template item | Edit posture |
|---|---|
| Scope | Electric HT on **freeze-exposed wet-type** FP piping only + FACP supervisory |
| Dry legs | Declared dry standpipe / dry DI **stay dry** — strip language that traces dry trim to force wet |
| Valve house | Heated enclosure first; **trace ≠ substitute** (DS 9-18 §2.2.6) |
| OEM path | Name elected FS design guide + IOM + edition; parameterize — do not lock every job to one SKU family |
| FS vs non-FS | Fence non-FS campus MEP out of FS LOD / controller shortlist |
| GFEP | Each heating-cable branch; cite OEM / NEC |
| IR / Cx | Owning OEM acceptance (do not cross IR gates) |
| Insulation | §210700 weather/FR as applicable; spray-shadow coordination |
| Backup power | Freeze loads on ≥3-day basis |
| Submittals | Circuit schedule (IPS, length, W/ft from OEM calc, breaker, GFEP); controller cut sheet; IR forms; FACP points |
| Hooks | Keep wet §211313 §3.4.Q / standpipe §211200 §3.5.M → 210533/210700 |
| Foreign local overlays | **Do not import** unless this job’s AHJ |
| Tank heaters | Out of 210533 core — companion section / note |

### 3.10 Step — Utility-outage / ERP / ITM handshake

- ≥3-day utility-loss freeze hazard analysis; on-site fuel ≥3 days for freeze-critical loads.
- Freeze ERP per DS 10-1; annual exercise.
- Idle-facility doctrine: maintain ≥40°F **or** convert wet→dry — **keep sprinklers in service** (do not shut off “to prevent freeze” as first resort).
- OA **< 20°F** after hours without heat → heighten cold-spot monitoring (§2.5.11).
- **HAND OFF** detailed ITM product/interval layer to `itm-design-for-testability` (enclosure verify; no heat-tape substitute flag already aligned).

### 3.11 Step — Tank heaters (handoff — out of core)

If closed-top suction / gravity tank present:

1. Record presence.
2. Emit `handoff` — campus program remains DS 9-18; **tank water hold / heater sizing** = **FM DS 3-2** (≥42°F hold, alarm 40°F, heat suction tanks when zone ≤ −5°F, Tables 6–13); same 42°F hold / 40°F alarm in [CODE NFPA 22-2018/2023 §16.1.2, §16.1.2.2, pull 22-01].
3. Do **not** invent Becker/Duluth/Chicago zone °F or Btu here.
4. Do **not** treat air-bubbler as FP tank method (DS 3-2 forbid).

### 3.12 Step — Δ layers + honesty close

Always print:

- Δ vs **NFPA 13-2025** freeze / heated-enclosure / listed-tracing interface (FM adds formal 100-yr DMT ≤20°F gate, ≥3-day utility planning, heated valve house — carry explicitly). Vendor 13-2019 §8.3.1.8.2.3 [CODE NFPA 13-2019 §8.3.1.8.2.3; 2022 §8.3.1.8.2.3; 2025 §8.3.1.7.2.3, pull 13-01].
- Controlling layer per parameter (A–I).
- `[SYN]` screening takeoffs / provisional Ta vs sealed map DMT / TraceCalc.
- Open RFIs (live DMT, OEM grid cells, 13-2025 enclosure §, listing letters, owner colder design-day).

---

## 4. Outputs / artifacts

Write **only** to the caller-named path (or return in-response and stop). Typical package:

1. **Status register** (§1.4) + Hard-scope fence result (STS consume; SI/NI/foam/mist posture).
2. **Freeze program memo** — map gate · ambient floors · strategy fork · valve-house fence · wet-must-stay-wet scope · OEM FS vs non-FS path · GFEP/backup · utility ≥3-day / ERP flags.
3. **Heat-trace register structure** — tags / service / IPS / strategy; **no invented sealed W/ft**; provisional calcs labeled `[SYN]`/`[V]`.
4. **FACP / supervisory alarm schedule structure** (§3.8).
5. **MasterSpec §210533 / §210700 edit-matrix checklist** (generic).
6. **Tank handoff note** when tank present.
7. **Open RFIs** — each with blocking/non-blocking tag.
8. **Reciprocal HAND OFF lines** to live peers.
9. **Δ vs NFPA 13-2025** + `[SYN]`/`[V]` register.

Do **not** emit: hall density×area transcript, standpipe Class election, N₂ purity calc, DI ≤30 s proof, tank Btu schedule as sealed, CAD coordinates, prior job files retrieval, foam/mist/clean-agent BOD, or KB writes.

---

## 5. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away only.
2. Missing the input packet → not a Stop (packet optional). Missing STS → `ASSUMED` (flagged), not a Stop. Missing matrix rows when dual → assume most-stringent row (`ASSUMED`, flagged) or hand off, then return.
3. Freeze-exposed standpipe legs present but standpipe type unconsumed → `ASSUMED` type (flagged) + `handoff` to `standpipe-class-i-election-and-demand`; not a Stop.
4. Site DMT / OEM W/ft / circuit schedule needed but primary unheld → stated `ASSUMED` value (value + why) + `[V]` + RFI, not a Stop — **never silently invent**; no vendor SKU frozen.
5. Heat-trace proposed as substitute for heated DI/dry valve enclosure → **Stop**; elect enclosure.
6. Heat-trace proposed on declared dry standpipe / dry DI instead of drain → **Stop**.
7. Non-FS guide / non-FS controller used to size or control **FS** circuits → **Stop** / refuse.
8. Cross-OEM wattage / IR-gate paste → **Stop** / refuse.
9. Antifreeze white-space as elective BOD without written force → Stop / RFI.
10. Caller wants tank heater Btu, standpipe gpm, N₂ plant, DI delivery proof, or CAD as this Skill’s deliverable → wrong Skill / handoff.
11. KB / worked examples / ARCHIVE writes; prior job files retrieve.

---

## 6. Citations (section AND edition)

| Claim | Pin | Status |
|---|---|---|
| Freeze-prone applicability | FM DS **9-18, July 2022** §1.0 / §3.1 / App. A — 100-yr DMT ≤ **20°F (−6.7°C)** | `grounded` method |
| Wet-space ambient floor | DS 9-18 §2.2.1 **> 40°F (4°C)** | `grounded` |
| Electric / diesel pump rooms | §2.2.4 **>40°F** / **>70°F** → DS 3-7 | `grounded` |
| Exterior heated valve enclosure | §2.2.6 insulated heated enclosure + attended temp | `grounded` — load-bearing |
| System-type fork | §2.2.7 cannot hold ≥40°F → dry/preaction/… | `grounded` method; consume STS |
| Failure detection | §2.3.1 low-temp + leak → DS 1-24 | `grounded` |
| Utility-loss / fuel | §2.4.1 B / §2.4.5 **≥ 3 days** → DS 5-23 | `grounded` |
| Insulation ≠ freeze protection without flow | §3.3 | `grounded` |
| Self-reg spiral spacing | App. C.1.2 ≥ **2 in. (50 mm)** | `grounded` |
| Trace ≠ heated enclosure (OEM) | H58489 p.21 (vendor NFPA **13-2019 §8.3.1.8.2.3**) | Aligns DS 9-18; [CODE NFPA 13-2019 §8.3.1.8.2.3; 2022 §8.3.1.8.2.3; 2025 §8.3.1.7.2.3, pull 13-01] |
| FS maintain Tm | H58489 p.5 / PX143 **40°F**; DS 9-18 floor | `grounded` numeric class |
| FS controller shortlist (RAYCHEM example) | H58489 p.30 **465 / C910-485 / ACS-30** + FCP | Method example — parameterize brand; **not interchangeable for cable listing** |
| FS listing fence | 465 IOM **H60742 (©2025)** pp. 5/8: c-UL-us / UL **VGNJ** with **5XLE/8XLE (-CR/-CT, 1/2) only** | `grounded` — 12XLE FS needs separate listing evidence |
| Heat-loss / circuit grids | H58489 pass-2 **Tables 1–7, 9** (pp. 15–24) | `grounded` within printed range; start-up < −20 °F → TraceCalc `[V]` |
| 8XLE output | H51349 **EN-2504 (2025)** p. 3 graph — ≈ **8.8 W/ft @ 40 °F** | Graph read (±0.1) — label as read, not printed |
| 50/65 °F start-up rows | H51349 p. 2 colour read — **110 °F maintain only** | `grounded` fence |
| Min install temperature | H51349 p. 2 — **0 °F (−18 °C)** | Construction constraint |
| 465 defaults | H60742 — setpoint 40 °F / low alarm 35 °F / GF trip 30 mA | OEM — confirm at submittal |
| External contactor | H60742 pp. 10, 16 — GF / load monitoring disabled → separate GFEPD | `grounded` |
| Negative case | a worked example — 12XLE2 + ACS-30 on FS pipe outside VGNJ listing | Lesson only |
| Non-FS defers FS | H55838 p.2 → H58489 | `grounded` fence |
| GFEP each branch | H58489 / H58033 / PX143 / peers | `grounded` class |
| IR accept (RAYCHEM IOM example) | H58033 **>1000 MΩ** @ 500/1000/2500 Vdc | Owning-OEM only |
| IR accept (Thermon peer) | TEP0165 ≥**20 MΩ** @ ≥500 Vdc | Do not cross onto RAYCHEM |
| MasterSpec wet HT hook | §211313 §3.4.Q → **210533** / **210700** (Victaulic ARCOM 2013 / base 02/10) | Edit before CD |
| MasterSpec standpipe HT hook | §211200 §3.5.M → **210533** / **210700** (2013 / 06/12) — **wet-type only** | Dry ≠ heat-trace |
| Tank hold / heat trigger (companion) | FM DS **3-2** ≥42°F / alarm 40°F; heat suction when zone ≤ **−5°F**; [CODE NFPA 22-2023 §16.1.2 (coldest water ≥42°F), §16.1.2.2 (low-temp alarm 40°F), pull 22-01; FM's −5°F heat trigger is not the NFPA 22 trigger, which is the lowest one-day mean temperature per §16.1.2.1] | Handoff |

**Absent / `[V]` (refuse invent):** live site **100-year DMT °F**; Fig. 11 curves as printed values (graph only — H51349 read used, labeled); grid rows for start-up below **−20 °F**; TraceCalc Pro stamped outputs; 12XLE FS listing evidence; peer-OEM (Chromalox / Thermon / Nelson) grids; FM Approval letter pair beyond vendor listing claims; owner Tier-A colder design-day numerics.

---

## 7. Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance`. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent = hand-away only. Status every run. Packet optional; STS (+ matrix when dual) consumed when present, else `ASSUMED` (flagged). **NO PLACEHOLDER.** **Never silently invent DMT / W/ft / controller defaults — if not given, state an ASSUMED value + why and flag it.**
2. Three-layer most-stringent **per parameter** (map, ambient, valve house, strategy, HT scope, OEM path, supervision, utility/ERP, tank handoff).
3. Campus program first (DS 9-18) — cable SKU second. Live Freeze Map — refuse App. D invent.
4. Heat-trace ≠ heated valve house. Heat-trace only wet-must-stay-wet. Dry legs stay dry.
5. Cite section **and** edition; enforced ≠ latest; local AHJ pins stay local; OEM paths parameterized.
6. Show-and-verify ΔT / Q / length when grids held; flag `[SYN]` / `[V]`; schedule needed but primary unheld → `ASSUMED` + `[V]` + RFI, not a Stop.
7. FS vs non-FS honesty; FS listing fence before cable pick; no cross-OEM wattage / IR paste; N₂ plant ≠ freeze.
8. Hand standpipe Class, DI delivery, N₂, ITM product, tank Btu, combustion-air to peer Skills — do not absorb their scope.

If notes conflict, **most-stringent wins** and both sources stay visible.

---

## 8. Not this Skill

| Work | Where |
|---|---|
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier BOD authorship | `most-stringent-basis-matrix` — consume+return when dual |
| Assignment packet authorship | the input packet — consume only |
| Standpipe whether / Class I / type / residual / gpm | `standpipe-class-i-election-and-demand` — **consume type**; do not elect |
| Hall DI ≤30 s / volume-cut proof | `dry-preaction-water-delivery-screen` — freeze/dry consume only |
| N₂ plant / C-factor / AMD | `nitrogen-inerting-and-c-factor-gate` — N₂ ≠ freeze |
| ITM interval calendar / AGF product matrix | `itm-design-for-testability` — emit freeze flags only |
| Genset / hall free-area design | `combustion-air-and-hall-free-area` — optional handshake |
| Closed-top tank heater Btu / DS 3-2 Tables | Tank companion / future Skill — **handoff** |
| White-space density×area | `density-area-dry-increase` |
| Clean-agent concentration / enclosure | Clean-agent Skills — **hand-away only** |
| CAD / KB / worked examples / ARCHIVE writes | forbidden |

---
