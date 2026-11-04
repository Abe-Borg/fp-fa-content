---
name: Standpipe Class I election and demand
description: >-
  use this when IFC/IBC §905 (or UFC §9-10 / owner) may require a standpipe and
  you must elect Class I type (manual wet/dry vs automatic), residual target,
  FDC role, and whether standpipe gpm rides the fire pump or stays FD-via-FDC —
  packet optional; STS wet|dry|DI consumed or ASSUMED; SI/NI-as-BOD → Stop RFI-variance;
  foam prohibited; mist PRACTICE REFUSED; not hall density×area, not hydrant
  P(Q), not listed pump envelope, not ITM drain checklist alone, not CAD.
---

# Standpipe Class I election and demand

> **Intake rule (the engineer, 2026-10-07 — overrides any older gate wording below):** The assignment packet is optional and never a gate. Start from exactly what is given. A missing packet, a missing upstream result (STS token, matrix row, occupancy fork, density, C&E, etc.), or a missing input blank is **not** a Stop: run the upstream Skill if practical, otherwise fill the gap with a stated **ASSUMED** value (the value used + why), flag it in the output and the status register, and continue. ASSUMED is not verified. "Never invent" / "refuse invent" rules on project numbers mean do not *silently* invent: label the number ASSUMED; never present an ASSUMED value as a cited code or table value; never freeze a vendor SKU. **Company scope locks stay hard Stops and are not softened by this rule:** wet / dry / double-interlock preaction only; foam prohibited; clean agent not done (hand-away); water mist `PRACTICE REFUSED`; single-interlock / non-interlock / other preaction never the elected system (SI/NI-as-BOD → Stop + `RFI-variance`, comparison-only). Cite section and edition, use `_calc/run.py` for governed math, design to the most-stringent 3-layer basis; the engineer is the engineer of record.

Reusable US data-center fire-protection recipe. **This Skill decides WHETHER a standpipe is required, elects Class I type (manual wet / manual dry / automatic wet / automatic dry), pins residual pressure at the remotest outlet, structures the demand register, and resolves pump-vs-FDC additivity** — after the assignment packet exists and STS has elected company `wet` | `dry` | `DI`.

It does **not** elect the hall sprinkler/preaction family (consume STS). It does **not** invent NFPA 14 gpm tables. It does **not** rebuild the hydrant P(Q) curve, listed pump envelope, campus loop diameter, or ITM product matrix. It does **not** CAD hose-valve coordinates. It does **not** design foam, mist, CAF, or clean agent.

**Core thesis:** A standpipe is a **firefighter-access subsystem (NFPA 14)**, not white-space suppression. The *whether* question is answered against the adopted **IFC/IBC Ch.9 §905** (or UFC §9-10 / owner mandate) — **not** against NFPA 13 hazard class. Class I (2½-in FD connections, no occupant hose) is the hyperscale default. Manual vs automatic follows a **height-tier engineering schedule** (UFGS 21 12 00 template) reconciled to the adopted NFPA 14 edition. Under the **manual <75 ft** combination-system rule, the on-site pump sizes for **sprinkler demand only**; the fire department makes standpipe flow/pressure via the **FDC**. Automatic (≥75 ft) pumps **include** standpipe demand once gpm is sealably held. **Never invent NFPA 14 gpm defaults** — structure the demand register and carry a stated `ASSUMED` value (value + why) + `[V]` + RFI, flagged `provisional` — not a Stop (the engineer intake rule) when the primary is unheld.

**the engineer Way:** three-layer most-stringent **per parameter** (whether-trigger, class/hose, type/manual-vs-automatic, residual, gpm demand, pump-vs-FDC additivity, FDC geometry flags, multi-zone/pressure envelope, test-drain feature). Delta vs **NFPA 13-2025** where the standpipe interfaces a combination sprinkler riser / hose allowance. Cite **section AND edition**. Show-and-verify math. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**; clean agent = **hand-away only**. Upstream (packet optional; gaps → `ASSUMED`): completed `dc-fp-assignment-packet` (optional) + STS `wet`|`dry`|`DI` (consumed, else `ASSUMED`) (+ `most-stringent-basis-matrix` when dual — **consume and return here**). Freeze strategy **consumed**, not invented. Caller-path-only. **NO PLACEHOLDER.** Generic — do not copy the site CE-1353, Bismarck/Fargo geometry, or UFGS federal apparatus as universal AHJ. Owner may **raise, never lower**.

**Honesty — gpm primary now held via pull 14-01** (flow [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01]; pick the row by enforced edition). Corpus holds UFGS 21 12 00 height-tier / residual / combination pump rule, MasterSpec §211200 type dial, AXA XL ≥4 in. test-drain design rule, the site CE-1353 as **local** §905.3.1 / dry-ban / 1000–1250 gpm-cap example, and secondary 500/250 recall (Clarke / NFSA blog) — **none of those seal NFPA 14-2024 demand tables** (the code text itself is now held: [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01]). Model IFC/IBC-2024 §905 trigger text is **not** held as primary. Recipe structure is **Ready**; sealed gpm / simultaneous-demand / residual-mechanism section pins → stated `ASSUMED` value (value + why) + `[V]` + RFI, flagged `provisional` — not a Stop (the engineer intake rule); never `grounded`.

Write the election package **only** to the path the **caller** names. Do not write into KNOWLEDGE_BASE, EXERCISES, `_pruner`, `_surveyor`, `_engineer`, or ARCHIVE. Do not retrieve CASE_INDEX. Do not CAD.

Look up shop codebook notes **by title**: *Standpipe & hose systems (NFPA 14)*; *The engineer Way*; *Enforced-vs-latest edition resolver*; *Freeze prevention / 100-year DMT and cold-climate FP*; *ITM basis and design for testability*; *Variable-speed pressure-limiting pumps and the zone pressure envelope*.

---

### 1.0 Country/edition gate at intake (model A — stop-vocab normalize 2026-11-04, staged)
Pin country + enforced edition first (enforced ≠ latest). Missing pin → `ASSUMED` (value + why) + flag, continue per intake rule; scope locks (§1.1 family fence, foam prohibited, clean agent hand-away, mist `PRACTICE REFUSED`, SI/NI comparison-only) stay hard.
- **US** → AHJ-adopted IFC/IBC + NFPA editions as used in this Skill; NFPA 13-2025 (and NFPA 20-2025 / 14-2024 where used) only as delta when not enforced.
- **Canada (BC/AB/ON)** → pin via `most-stringent-basis-matrix` §4.2b; whether trigger = NBC/BCBC/NBC-AE/OBC 3.2.5.8, NFPA 14-2013 (see Canada section). Never cite US IFC/IBC §§ or US NFPA editions as the Canadian code floor.
- **NEG-CA (stop-class mis-cites):** never invent ULC hours, CSA B139 text, OBC/NBC/BCFC bodies, or unheld Canadian pins. Unheld → `NEEDS HOLD` / `unresolved` + RFI (do not invent; do not Stop the whole run).

## 1. Hard scope gate

### 1.1 Company system-family fence (consumes STS — does not elect)

This Skill owns **standpipe whether / Class I type / residual / demand-register structure / pump-vs-FDC additivity / FDC handshake flags / MasterSpec §211200 edit checklist**. Controlling company BOD for sprinkler/preaction families = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI (hall / combination-riser context) | `suppression-technology-selection` (**consume** — do not elect here) |
| Standpipe whether / Class I / type / residual / demand register / pump↔FDC | **This Skill** |
| Dual-carrier per-parameter union | `most-stringent-basis-matrix` (**consume**, then **return here**) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**This Skill does not elect hall families.** It **consumes** the completed `dc-fp-assignment-packet` and the STS token `wet` | `dry` | `DI`, then runs the §905 / Class I / type / demand recipe.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family on the packet or combination-riser context:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue standpipe arithmetic as if SI/NI were company-elected BOD.
6. SI/NI may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler / preaction | Permitted when elected upstream via STS | Record combination-riser consequences under that BOD; do not elect |
| Class I standpipe (manual/automatic × wet/dry) | **In scope here** | Elect whether / type / residual / demand register / pump↔FDC |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water / CAF | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do **not** design/accept mist as BOD |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent; Never company BOD here |
| Class II / Class III standpipe (occupant hose) | **Stop / RFI** unless AHJ/owner forces in writing | Default refuse; strip from MasterSpec template |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Clean agent = hand-away only. Prefer Class I no-hose when company practice fits.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| §905 / UFC §9-10 / owner *whether* screen (parameterized AHJ edition) | System-family election (`suppression-technology-selection`) |
| Class I election; Class II/III → Stop/RFI | Occupancy re-class; white-space density×area |
| Type dial: Manual Wet / Manual Dry / Automatic Wet / Automatic Dry | Invent heat-trace OEM / wattage (consume freeze strategy) |
| Residual target at remotest 2½-in outlet (held pin or `ASSUMED` + `[V]`) | Hydrant P(Q) rebuild (`hydrant-supply-curve`) |
| Demand-register **structure** + `ASSUMED` + `[V]` + RFI when NFPA 14 gpm unheld | Listed churn/100%/150% envelope (`pump-envelope`) |
| Pump vs FDC additivity under height-tier rule | Campus loop diameter (`campus-looped-main-sizing`) |
| FDC location/type **flags** (handshake, not CAD) | ≥4 in. test-drain **product** matrix (`itm-design-for-testability`) |
| Multi-zone / 300-psi **pointer** (AHJ/design pin, not invent) | Node-by-node standpipe tree / SprinkFDT invent |
| MasterSpec §211200 edit-matrix checklist (generic) | the site CE-1353 / ND Art. 45-18 as universal AHJ |
| Election memo + demand register + open RFIs | CAD hose-valve coordinates; foam/mist/clean-agent BOD |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet + STS (+ matrix when dual), **(c)** AHJ edition / §905 whether, **(d)** Class / hose, **(e)** height-tier type, **(f)** wet/dry leg freeze fork, **(g)** residual target, **(h)** gpm demand register, **(i)** pump↔FDC additivity, **(j)** FDC flags, **(k)** multi-zone/pressure envelope, **(l)** ITM ≥4 in. drain handoff, and **(m)** mist/foam/clean-agent if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling election + editions supported by opened AHJ text / UFGS or MasterSpec pin already closed for that parameter |
| `provisional` | Directionally pinned; NFPA 14-2024 primary / model IFC §905 trigger text / residual mechanism hole flagged `[V]` — **never silent `grounded` on invented gpm** |
| `unresolved` | STS / matrix(when dual) / AHJ edition / building height datum / freeze strategy not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, Class II/III, secondary 500/250 recall, NFSA 300-psi advocacy — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; hydrant/pump Qd; campus loop; freeze; dry-delivery; ITM drain; commissioning) |
| `RFI-variance` | SI/NI/foam/mist (or Class II/III without written force) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as controlling medium |

**Invented NFPA 14 gpm / simultaneous-demand / model §905 height thresholds as defaults → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Worked Bismarck / Fargo Class I Manual Wet/Dry + MasterSpec §211200 packages = **`[SYN]` method** only. Do **not** copy ~42–45 ft / 950 gpm DI floor / 500–750 gpm screening flows as project defaults. the site CE-1353 = **local** Layer-1 example (2021 the site-amended IFC/IBC) — **not** model IFC-2024 and **not** universal. UFGS 21 12 00 = federal **engineering template**, not commercial AHJ. NFPA 14-2024 primary **absent** → refuse invent. **NO PLACEHOLDER.**

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent §905 trigger thresholds, NFPA 14 gpm, or freeze OEM. Do not treat SI/NI as company BOD. Do not elect foam/mist/clean-agent.

| Input | Required | Notes / Stop |
|---|---|---|
| `dc-fp-assignment-packet` (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`suppression` / `bod` / water-supply). Do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Consumed `most-stringent-basis-matrix` rows** | **yes when dual-carrier** | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever. Unresolved controlling standpipe / hose / residual rows → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **AHJ fire/building code + edition** | **yes** | IFC/IBC edition (or UFC / owner). Parameterize — do not default to the site 2021 or IFC-2024 unheld text. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Building geometry for §905 screen** | **yes** | Highest/lowest occupied floor vs FD vehicle access (ft); stories above/below grade; floor area / travel distance if known. Mark `[V]` when survey open. |
| **Freeze / ambient strategy** | **yes when freeze-exposed legs** | Consume freeze program (heated envelope vs dry leg vs heat-trace on wet-must-stay-wet). Do **not** invent heat-trace OEM/wattage. Missing when freeze-exposed → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged / `handoff`. |
| **Combination riser? (y/n)** | **yes** | Drives pump-vs-FDC additivity under UFGS height-tier. |
| **Sprinkler / DI demand context** | **yes when combination + manual** | Consume density-area / hall BOD `qd` so pump floor stays sprinkler-only under manual rule. Do not rebuild density×area. |
| **Carrier** | **yes** | FM / AXA / UFC / n/a. Dual → matrix rows above. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional: owner Class I mandate even when §905 silent; written AHJ hose-omit approval (§905.1.1 style; §905.1.1 does not exist in model IFC 2024 [pull IFC-01]; §905.1.1 is an ND amendment [LOCAL ND Admin. Code §45-18-01-04(2)(f), amending IFC 2021, effective Jan 1, 2024: hose may be omitted when approved by the fire code official, approved hose valves and connections still provided; a rule moving ND to IFC 2024 effective July 1, 2026 is proposed (RU-26-919), final adoption unconfirmed; pull LOCAL-06-ND-web.md (ndlegis.gov web source; not UpCodes LOCAL-06 Arkansas/Seattle)]); FDC inlet preference; existing hydrant curve / campus loop residual (consume — do not rebuild).

**Do not invent** NFPA 14 gpm, model §905 numeric triggers from memory, the site dry-ban as universal, or 500/250/1000 as sealed demand. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `dc-fp-assignment-packet` | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected wet/dry/DI | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `most-stringent-basis-matrix` | Standpipe / hose / residual / dual-carrier rows when dual | Rebuild dual-carrier BOD; invent gpm |
| `hydrant-supply-curve` | Receive standpipe-flow verification handoff (campus can deliver minimum standpipe flow once gpm sealed) | Rebuild P(Q); invent flow test |
| `pump-envelope` | Receive pump-include / pump-exclude standpipe Q flag | Freeze nameplate; add invented standpipe gpm to rated flow |
| `campus-looped-main-sizing` | Loop capacity vs standpipe + sprinkler concurrent once gpm sealed | Resize loop from standpipe screening placeholders |
| `itm-design-for-testability` | ≥4 in. / 250–500 gpm test-drain **feature** handoff | Duplicate AGF product matrix / interval calendar |
| `dry-preaction-water-delivery-screen` | Freeze/dry-leg delivery consequences **only as consume** when dry standpipe shares plant/timing concerns | Re-run ≤30 s hall DI proof as standpipe demand |
| Freeze program (peer / future Skill) | Heated vs dry vs heat-trace posture | Invent XL-Trace / Nelson wattage; heat-trace a declared dry leg |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS, dual-carrier rows (when required), AHJ edition, or freeze strategy (when freeze-exposed) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Outbound this draft.** Do **not** restamp peers in this write.

| Peer | They own | This Skill owns |
|---|---|---|
| `dc-fp-assignment-packet` | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume** STS; mist = `PRACTICE REFUSED`; foam prohibited; SI/NI → Stop |
| `most-stringent-basis-matrix` | Per-parameter union / dual-carrier rows | **Consume only** when dual — then elect standpipe package **here** |
| `hydrant-supply-curve` | Campus supply vs demand at BOR | Emit standpipe-flow verification need once gpm sealed; do not rebuild curve |
| `pump-envelope` | Listed churn/100%/150% screen | Emit pump-include vs pump-exclude standpipe Q; do not freeze nameplate |
| `campus-looped-main-sizing` | Loop diameter / one-leg-out | Emit concurrent standpipe+sprinkler flow once sealed |
| `itm-design-for-testability` | ≥4 in. test drain / PRV in-place test features | Name drain feature; do **not** duplicate AGF matrix |
| `dry-preaction-water-delivery-screen` | Hall DI ≤30 s / volume-cut | Consume freeze/dry-leg interface only; do not treat standpipe as DI delivery proof |
| Clean-agent Skills | Clean-agent concentration / enclosure | **Hand-away only** |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — dc-fp-assignment-packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: dual-carrier / standpipe-hose-residual rows when dual. Consume; return here after.`
- `HAND OFF — hydrant-supply-curve: verify campus can deliver sealed standpipe minimum flow; do not rebuild P(Q) here.`
- `HAND OFF — pump-envelope: pump-include vs pump-exclude standpipe Q under height-tier rule; no nameplate here.`
- `HAND OFF — campus-looped-main-sizing: concurrent standpipe + sprinkler once gpm sealed.`
- `HAND OFF — itm-design-for-testability: ≥4 in. / 250–500 gpm standpipe test-drain feature — peer owns checklist/product layer.`
- `HAND OFF — dry-preaction-water-delivery-screen: freeze/dry-leg interface only; not standpipe gpm.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first (Runner item 0)

Before §905 / Class / type / residual / gpm arithmetic:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix / whether / Class / type / freeze fork / residual / gpm / pump↔FDC / FDC flags / multi-zone / ITM drain / Δ (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER.** anywhere in the run.
5. Restate refuse-invent: **no invented NFPA 14 gpm**; **no invented model §905 thresholds**; the site CE-1353 / UFGS / secondary recall are **pins or templates**, not silent defaults.

### 3.1 Pin editions (cite section AND edition)

| Instrument | Role | Shop pin / honesty |
|---|---|---|
| **Adopted IFC/IBC Ch.9 §905** (or UFC §9-10) | *Whether* trigger | **Parameterize AHJ edition**. Model IFC/IBC-2024 §905 commercial trigger text **held**: IFC/IBC-2024 §905.3.1 (Class III where 4 or more stories are above or below grade plane, or the highest story is >30 ft above / lowest story >30 ft below fire department vehicle access; Exc. 1 allows Class I where sprinklered throughout per §903.3.1.1 or §903.3.1.2) and §905.4 body [CODE; UpCodes pulls IFC-01 (IFC-2024 via Colorado DFPC, unamended), IBC-07 (IBC-2024 via Wyoming, unamended); IFC 2021 §905.3.1 identical, IFC-10] → screen structure + stated `ASSUMED` + `[V]` (adopted AHJ edition/amendments) + RFI for yes/no (not a Stop). the site CE-1353 prints **the site-amended 2021** §905.3.1 — **local example only**. |
| **NFPA 14** | Installation / demand / residual / FDC | UFGS 21 12 00 cites **NFPA 14-2024** as federal template. Held via pull 14-01 (2024/2019/2016/2013): flow [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01]; max pressure [CODE 2024 §10.2 / 2019·2016·2013 §7.2, pull 14-01]; residual [CODE 2024 §10.2.6.1 / 2019·2016·2013 §7.8.1, pull 14-01]; FDC sizing [CODE 2024 §10.7 / 2019·2016·2013 §7.12, pull 14-01]; automatic-dry 3 min [CODE 2024 §8.3.2 / 2019·2016·2013 §5.2.1, pull 14-01]. Enforced ≠ latest (IFC Ch.80 map may lag). |
| **UFGS 21 12 00** | Height-tier / residual / combination pump / acceptance engineering defaults | Held federal template (edition-current refs NFPA 14-2024). Not commercial AHJ. |
| **MasterSpec §211200** (Victaulic ARCOM 2013 / base 06/12) | Type dial / PE delegated / N₂ Coordination Drawings / heat-trace → 210533 | Commercial issue vehicle — **edit before CD**; strip Class II/III; dated. |
| **AXA XL PRC.12.0.2** | ≥4 in. / 250–500 gpm test-drain design rule | Copyright **2020**; insurer-driven feature — hand off product/ITM detail to `itm-design-for-testability`. |
| **NFSA multi-zone pressure note (2026)** | 400-psi reported ceiling; 300-psi = advocacy not code; FDC 2024 delta rumor | **Secondary**; all section pins `[V]`. |
| **Clarke / CSE secondary (2006)** | 500/250 recall; 100-psi residual with AHJ-may-lower-to-65 framing | **Secondary / dated** — corroborates shape; does **not** seal NFPA 14-2024. |
| **NFPA 13-2025** | Combination-riser / hose-allowance interface delta | Delta baseline where sprinkler interface matters — **not** standpipe demand primary. |
| **FM DS 5-32** | Hose allowance interaction with supply duration | Insurer Layer-2 — reconcile simultaneous demand into supply; do not invent standpipe gpm from DS 5-32. |

**Do not cite the site CE-1353 dry-ban / dual two-way FDC / 100 psi topmost as universal.** Ask per jurisdiction.

### 3.2 Parameters, separately (three-layer union)

| Parameter | Code floor (L1) | Insurer (L2) | Owner (L3) | Runner action |
|---|---|---|---|---|
| **A. Whether** | Adopted IFC/IBC §905 / UFC §9-10 | Rarely adds standpipe *requirement* | May mandate Class I even if code silent | Parameterize edition; provisional if trigger text unheld |
| **B. Class / hose** | Class I / II / III per code | — | Hyperscale → Class I no-hose | Default Class I; Class II/III → Stop/RFI unless written force |
| **C. Type (manual/auto × wet/dry)** | NFPA 14 types + AHJ dry bans | Freeze / ITM overlays | Climate + ops | UFGS height-tier × freeze fork × MasterSpec dial |
| **D. Residual** | NFPA 14 residual [CODE 2024 §10.2.6.1 / 2019·2016·2013 §7.8.1, pull 14-01] | May raise | May raise | NFPA 14 100 psi at the 2½ in. outlet is the floor; UFGS 65 / 100 height-tier = comparison-only; reconcile AHJ letter |
| **D2. Pressure limits / PRDs** | Max 400 psi anywhere; PRD where 1½ in. residual >100 psi or any hose-connection static >175 psi (limit to 175); PRD inlet ≤ its rating; series PRDs for redundancy + NFPA 72 high-pressure supervision on master PRDs; parallel low-flow PRD where needed [CODE NFPA 14-2024 §10.1.1–10.1.1.1, §10.2.1, §10.2.4.1–10.2.4.3, §10.2.5(3)/(9), pulls 14-07, 14-13; 2019 §7.2 = pipe, limits in §7.8, pull 14-11] | — | — | Each FDC must supply system demand [CODE 2024 §10.4.1 / 2019 §7.7.1, pull 14-10] |
| **E. Demand gpm** | NFPA 14 flow [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01] | Simultaneous with hose allowance | May raise | **Structure register; `ASSUMED` + `[V]` + RFI — never silently invent** |
| **F. Pump↔FDC** | Combination rules per NFPA 14 / UFGS height-tier | Supply duration interaction | N+1 | Manual <75 ft → pump = sprinkler only; auto ≥75 ft → pump includes standpipe once gpm held |
| **G. FDC flags** | NFPA 14 / AHJ geometry | FDC sized on standpipe system demand [CODE 2024 §10.7 / 2019·2016·2013 §7.12, pull 14-01]; same sizing text 2013–2024, no 2024 change seen | Inlet preference | Handshake flags only — not CAD |
| **H. Test drain** | Not NFPA 14 mandate | AXA ≥4 in. preferred | Hyperscale impairment intolerance | Hand off feature to ITM Skill |

Most-stringent wins **per row**. Name the controlling layer. Owner may raise, never lower.

### 3.3 Step — Whether (§905 / UFC / owner)

1. Record adopted **fire/building code + edition** (caller pin). Enforced ≠ latest.
2. Collect geometry: highest occupied floor above lowest FD vehicle access; stories above/below grade plane; floor area; hose-travel if known. Survey open → `[V]`.
3. Screen against **opened** §905 / UFC §9-10 text for **this AHJ**. If model trigger text is unheld → status `provisional` / `unresolved` on Layer-1 whether; **do not invent** numeric thresholds from memory.
4. **Local pin example (not default):** the site CE-1353 / the site-amended 2021 IFC §905.3.1 — Class III throughout where four or more stories, or highest story >30 ft above/below FD access; exceptions allow Class I in fully sprinklered / named cases; **dry standpipes prohibited** (the site IFC 905.8). Use only on the site jobs.
5. If code silent but owner/EPC mandates firefighter access → record as **Layer-3 provision**; still open AHJ confirmation.
6. If AHJ confirms **not required** → delete system rather than leave orphan risers. Emit election memo with negative finding and stop further type/demand work (or mark N/A).

**Directional corpus TL;DR (not a sealed finding):** single-story hall alone often does not trip height triggers; multi-story / elevated support structures force an honest determination.

### 3.4 Step — Class election

| Election | When | Status |
|---|---|---|
| **Class I** (2½-in FD connections, **no occupant hose**) | Default hyperscale / UFGS / MasterSpec Class I dial | `grounded` method |
| Hose omit | Where adopted §905.1.1 (or equivalent; §905.1.1 does not exist in model IFC 2024 [pull IFC-01]; §905.1.1 is an ND amendment [LOCAL ND Admin. Code §45-18-01-04(2)(f), amending IFC 2021, effective Jan 1, 2024: hose may be omitted when approved by the fire code official, approved hose valves and connections still provided; a rule moving ND to IFC 2024 effective July 1, 2026 is proposed (RU-26-919), final adoption unconfirmed; pull LOCAL-06-ND-web.md (ndlegis.gov web source; not UpCodes LOCAL-06 Arkansas/Seattle)]) allows omit with fire-code-official approval | Request **written** AHJ approval; valves/connections remain |
| Class II / III | Only when AHJ/owner **forces in writing** | **Stop** / `RFI-variance` if presented as elective BOD without written force; strip from §211200 template |

Do not hang occupant hose in ITE buildings by habit.

### 3.5 Step — Type election (Manual/Automatic × Wet/Dry)

**Height-tier engineering schedule (UFGS 21 12 00 — federal template, reconcile to AHJ/NFPA 14):**

| Building height (highest floor / UFGS framing) | Type | Residual @ most remote 2½-in | Combination pump rule |
|---|---|---|---|
| **< 75 ft** | **Manual** (wet or dry) | **≥ 100 psi** at the most remote 2½ in. outlet [CODE NFPA 14-2024 §10.2.6.1 / §10.2.6.1.2; 2019 §7.8.1 / §7.8.1.2, pull 14-01]; UFGS 65 psi = comparison-only (lower value only with a written AHJ variance → RFI-variance) | Booster sized for **SPRINKLER demand only**; FD makes standpipe via **FDC** |
| **75–150 ft** | **Automatic** | ≥ 100 psi (same cite; UFGS 65 comparison-only) | Pump **includes** standpipe demand per NFPA 14 (once gpm held) |
| **≥ 150 ft** | **Automatic** | ≥ **100 psi** | Pump includes standpipe demand |

**MasterSpec §211200 type dial (reconcile to height-tier — do not overshoot):**

| Dial option | Typical use |
|---|---|
| Manual Wet Class I | Heated continuous >40 °F legs; small supply keeps pipe wet; FD via FDC |
| Manual Dry Class I | Freeze-exposed exterior / dock; **no permanent water**; drain + supervisory air; FD via FDC. Supervisory-air band and packaged-compressor pointers: §3.5.1 |
| Automatic Wet / Automatic Dry | ≥75 ft tier or AHJ/owner force permanent residual |
| Semiautomatic Dry | Deluge + detection — rare on DC; needs releasing coordination; not a white-space preaction substitute |

**Freeze fork (consume strategy — do not invent heat-trace):**

- Prefer **wet** only where ambient **>40 °F** continuous and supervised (FM DS 9-18 posture — cite sheet/edition when opened).
- Where 40 °F cannot be held → **dry** standpipe leg — not “wet + hope.”
- Heat-trace applies to **freeze-exposed wet runs that must stay wet** (MasterSpec §3.5.M → 210533 / 210700). **Heat-trace ≠ substitute** for a heated DI valve house. **Do not** heat-trace a declared dry standpipe instead of draining it.
- Honor **local dry bans** when they exist (e.g. the site IFC 905.8) — local pin only.
- Mist **REFUSED**. Antifreeze standpipe **not elected** unless caller cites listing + AHJ path (`[V]`).

#### 3.5.1 Manual-dry supervisory air (national floor by edition, then local pins)

A manual-dry Class I standpipe must carry supervisory air [CODE NFPA 14-2024 §8.3.2.1.1 (all such standpipe piping supervised with supervisory air), §8.3.2.1.2 minimum 7 psi (lower permitted per manufacturer, §8.3.2.1.2.1), §8.3.2.1.3 maximum 20 psi (only automatic and semiautomatic systems may exceed it, §8.3.2.1.3.1); raw 14-FP002-2024-8.3.2; NFPA 14-2019 §6.1.1 'monitored in accordance with NFPA 72 with supervisory air pressure', raw 14-FP002-2019-6.1.1; NFPA 14-2019 sets no psi band, so a 7 to 20 psi band is not required under 2019 (pull 14-12; 2019 Ch. 5, 6, 7, 9, 10, 11 searched)] and owes an air band, monitoring, and a compressor sized to the **held dry volume**. Pins below are opened corpus text. Do not export them past their stated scope, and do not freeze a compressor SKU.

| Pin | What it says | Scope fence |
|---|---|---|
| **Seattle FD AR 9.03.25** (effective **2025-09-25**; supersedes AR 9.03.20 effective 2020-03-01 — cite **9.03.25** on a current Seattle job) | **§3.1** Class I may be **manual dry** in a **non-high-rise** (wet required in underground transportation tunnels). **§3.10** dry standpipes that require supervisory air hold **10–20 psi**, monitored by the building fire alarm. **§3.4** FDC inlets **2½-in. swivel female, national standard thread**; **§3.7** hydrant **within 100 ft** of the FDC, extendable to **400 ft** where sprinklered throughout (SFC §507.5.1.1). **§5.1** hydro **≥200 psi / 2 h** at the topmost outlet **or 50 psi above design**, whichever greater. **§5.2** standpipe flow test **not required** (PRV flow test is). | **City of Seattle only.** 9.03.20 states the same numbers (Run-371) but is superseded. |
| **UFS STANDPIPE-PAC XL, data sheet UFS-213 Rev 1.01 (Dec 2021)** | Packaged dry-standpipe supervisory (air) system: low switch signals **below 7 psig**, high switch **above 23 psig** (the features list says “over 25 PSIG” — cite the **23 psig** specification and confirm on the control-unit manual). Desiccant versions **15 SCFM @ 100 psig**. Written to NYC (LL64 / BC 3303.8.1) and Boston (TCM3-51725) construction/demolition rules. | **NYC/Boston construction-site law ≠ a permanent-building national rule.** NFPA 14 + the local AHJ govern permanent manual-dry standpipes. |
| **Band conflict (keep both visible)** | Seattle's **10–20 psi** and the UFS factory **7 / 23 psig** switches sit **outside each other at both ends**. On a Seattle-style job specify the switch setpoints at the AHJ band; the sheet does not say the setpoints are adjustable → confirm on the control-unit manual. | Do not accept factory NYC/Boston points on a job whose AHJ prints its own band. |

**Fill-time check (derivation in the standpipe note, Run-673 — not printed on the UFS sheet):** t ≈ (V_gal / 7.48) × (p_psig / 14.7) / Q_scfm. Example held in the note: 1,000 gal to 20 psig at 15 SCFM ≈ **12.1 min**. Ignore dryer drop and leakage; compare against the AHJ's impairment limit where one exists (NYC 2 h / Boston 4 h on that sheet only).

**Negative package — `case-2026-10-05-bh`** (`EXERCISES/worked/hyperscale-whitespace-hall-wet-class-i-standpipe-seattle-wa__class-i-manual-dry-standpipe-fdc-supervisory-air-compressor.md`, verdict **corpus-insufficient**). A synthetic one-story Seattle hall, wet-pipe with a Class I manual-dry standpipe, FD-supplied. It shows the *shape* of the package and **fails** for stated reasons — do not copy its numbers:

- Coverage screen: worst point **162.5 ft ≤ 200 ft** with 4 hose valves (model IFC-2024 §905.4 item 6 lets the fire code official require added connections beyond 150 ft unsprinklered or 200 ft sprinklered [CODE; pull IFC-01]; model IFC 2021 §905.4 item 6 is the same [CODE; pull IFC-17]; Seattle 2021 [S] §905.4 keeps it and adds 'or roof' to the 200 ft sprinklered limit, allows connections at the main floor or intermediate landing, and requires roof connections at least 10 ft from the roof edge or openings unless guarded [LOCAL Seattle Fire Code 2021 §905.4, pull LOCAL-06], so on a Seattle job the 200 ft screen applies to floors and roof).
- Hydraulics at **C = 100** (shop lock; the UFGS C = 120 steel figure was deliberately not taken): 6 in. feed → **80.9 psi at the FDC @ 500 gpm**; 4 in. → **144.2 psi, rejected**. The 500 gpm matches the 2019/2016/2013 rule [CODE 2019·2016·2013 §7.10, pull 14-01; 2024 §10.6 reads 250 gpm through each of two connections]. Clarifier: 500 gpm = 250 gpm through each of the 2 most remote 2½ in. connections [CODE NFPA 14-2024 §10.6.1.1.1; 2019 §7.10.1.1.1 / §7.10.1.2.1, pull 14-01] — the package's own failure.
- Dry volume **≈1,145 gal**; compressor **1,145 × 20 / (7.48 × 14.7 × 30) = 6.94 cfm** to 20 psig in 30 min (Viking VXR formula; the 30 min basis is borrowed from the NFPA 13 dry-pipe convention [UNSOURCED / company practice] — no edition of NFPA 14 gives a manual-dry fill time; 2024 §8.3.2.3 Manual Dry is "(Reserved)", pull 14-01). The LP compressor ladder tops out at **990 gal** and fails; the package picks a larger unit.
- Hydro = max(200 psi / 2 h, system working pressure + 50) = **200 psi / 2 h** [CODE NFPA 14-2024 §12.4.1 / 2019 §11.4.1: ≥200 psi or 50 psi over working pressure, whichever is greater, 2 h, pull 14-02].
- **Why it is corpus-insufficient (do not repeat these):** the Seattle §905 *whether* trigger is not held (a one-story hall does not trip a height trigger); the hose-valve location rule is analogue-only; and the NFPA 14 demand (now held: [CODE 2019 §7.10, pull 14-01]), horizontal-standpipe split, and 65-vs-100 psi residual (100 psi now held: [CODE 2019 §7.8.1, pull 14-01]) were unheld when the package was written. Those three gaps are why this Skill still refuses to seal gpm.

**Residual honesty (standing P1):** three competing attachments appear in corpus — (1) UFGS **height-tier 65/100**, (2) MasterSpec **outlet-size** brackets (65 psig @ 1½ / 100 psig @ 2½), (3) Clarke **100 with AHJ discretion to 65**. NFPA 14 residual is now held [CODE NFPA 14-2024 §10.2.6.1 / §10.2.6.1.2; 2019 §7.8.1 / §7.8.1.2, pull 14-01]: 100 psi at the most remote 2½ in. outlet (65 psi applies to 1½ in. outlets only). Carry 100 psi as the floor, UFGS 65 comparison-only, flag competitors, and **ask AHJ in writing** for any lower value. Do not silently merge.

**Static head check (show-and-verify):** `0.433 psi/ft × height_ft`. Low/wide DC halls typically sit far below high-rise multi-zone bands — fence rooftop gravity tanks / express-riser zoning unless the project genuinely is a tall multi-story DC.

### 3.6 Step — Demand register (refuse invent)

Build the register structure. **Do not fill sealed gpm from memory.**

| Register row | What to record | Honesty |
|---|---|---|
| Enforced NFPA 14 edition | From IFC/IBC Ch.80 / AHJ map / UFC | Often **no Ch.80 NFPA 14 row** in corpus → `[V]` / RFI |
| Most-remote standpipe flow | Per NFPA 14 adopted tables | [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01] by enforced edition; enforced edition unknown → stated `ASSUMED` + RFI |
| Additional standpipe increments | Per NFPA 14 | Same |
| System cap (sprinklered / non-sprinklered) | Per NFPA 14 | the site CE-1353 prints **1000 / 1250 gpm** citing NFPA 14 7.10.1.1.5 — **local checklist corroboration only**; Clarke attaches **1000 gpm cap to fully sprinklered AND light hazard** → **DC hall is not light hazard — do not assume the 1000 cap** |
| Simultaneous standpipe ↔ sprinkler / FM hose allowance | Absorb / substitute / add fork | Standing open — do not resolve by invention |
| Screening hydraulics (optional) | HW friction on assumed flow for memo only | Label **`[SYN]` screening — not sealed NFPA 14 demand** |

**Secondary recall (comparison-only — never controlling; code text now held: [CODE 2024 §10.6 / 2019·2016·2013 §7.10, pull 14-01]):** ~500 gpm first Class I/III + 250 gpm each additional, cap ~1,000–1,250 gpm — UFGS-deferred / Clarke / blog shape. Status: `comparison-only`. **Never paste onto a sealed schedule as “NFPA 14 demand.”**

If demand is needed for pump/loop and primary remains unheld → **not a Stop**: carry a stated `ASSUMED` demand (value + why), flagged, with RFI: obtain licensed NFPA 14 edition text (section + edition) or AHJ-accepted demand letter.

### 3.7 Step — Pump vs FDC additivity

| Height-tier / type | On-site fire pump carries standpipe Q? | FDC role |
|---|---|---|
| Manual <75 ft (combination) | **No** — size pump for **sprinkler / DI demand only** (consume hall `qd`) | FD supplies / boosts standpipe demand via FDC |
| Automatic ≥75 ft | **Yes** — once NFPA 14 gpm is sealably held | FDC still required; 2024 full-demand capability: FDC sizing is "based on the standpipe system demand" [CODE 2024 §10.7 / 2019·2016·2013 §7.12, pull 14-01], same text in 2019, so the blog's "2024 change" is not seen in the pull — raise with FPE/AHJ; do not silently upsize or ignore |
| Standpipe-only (no combination) | Follow automatic/manual rule for that building | Same |

Still required under manual rule: verify **campus loop + hydrants** can deliver the **minimum standpipe flow** once gpm is sealed → hand off to `hydrant-supply-curve` / `campus-looped-main-sizing`. Do not add invented standpipe gpm to pump rated flow.

Hose allowance inside sprinkler `qd` (e.g. FM 250 gpm) is **not** automatically the standpipe demand — do not conflate.

### 3.8 Step — FDC location / type flags (handshake, not CAD)

Emit flags for coordination — do **not** place CAD:

- Inlet count / type (two-way default in UFGS; the site local: **two, two-way FDCs if ≥3 risers** — local only).
- Approx. height above grade (~3 ft UFGS default) — confirm AHJ.
- Facing apparatus access / street side; max hose-lay to hydrant (often ≤100 ft in AHJ flyers — pin local).
- Separate standpipe FDC vs sprinkler FDC labeling when combination architecture splits them.
- NFPA 14-2024 FDC-full-demand capability question → FDC sizing [CODE 2024 §10.7 / 2019·2016·2013 §7.12, pull 14-01]; any AHJ reading beyond that stays an open RFI.

### 3.9 Step — Multi-zone / 300-psi redundancy pointer

- **300 psi is NOT an NFPA 14 limit.** NFSA 2026 author proposes it as a redundancy **design signal**; reported NFPA 14 ceiling **400 psi** [CODE 2024 §10.2 / 2019 §7.2, pull 14-01]; 2016/2013 §7.2 read **350 psi** [CODE, pull 14-01] (the Clarke figure).
- Multi-zone / express-riser / rooftop gravity-tank architecture is **form-fenced** for typical low/wide hyperscale halls (static head too small). Re-open only for genuinely tall multi-story DCs.
- PRV ladder honesty: code trigger vs federal tighten vs outlet set — UFGS provide PRV where Class I outlet could exceed **125 psi**, default set **100 psi**; Clarke notes **175 psi** code-side trigger. Reconcile to adopted NFPA 14 (`[V]`). Some AHJs prohibit master PRVs — ask.
- Point to NFSA / zone-pressure-envelope note as **AHJ/design pin**, not invented universal rule.

### 3.10 Step — ITM handshake (≥4 in. test drain)

AXA XL PRC.12.0.2: new standpipes preferred with a **drain riser ≥4 in.** sized for typically **250–500 gpm** so 5-year hose-connection PRV flow tests can run **in place** without impairing the combination riser / white-space suppression.

- Emit feature flag + rationale.
- **HAND OFF** detail checklist / optional AGF product lines / interval levers to `itm-design-for-testability`.
- Do **not** duplicate the AGF TESTanDRAIN / RemoteTEST matrix here.

### 3.11 Step — MasterSpec §211200 edit-matrix checklist (generic)

Emit a project-agnostic edit checklist (not a pasted 2013 Victaulic BOD):

| Template item | Edit posture |
|---|---|
| Class I / II / III dial | **Class I only**; strip II/III unless written force |
| Automatic / Semiauto / Manual | Match height-tier + freeze fork (typically Manual Wet + Manual Dry on <75 ft freeze campuses) |
| Residual brackets | Carry engineering residual + **AHJ confirmation letter**; do not silently adopt a foreign AHJ’s 100 psi |
| Product BOD pins (alarm/dry/deluge series) | Editable — strip vendor-only language unless project elects OEM |
| Coordination Drawings ★ Nitrogen | Keep when Manual/Automatic Dry shares N₂ plant with DI — pressure regimes must reconcile |
| Heat-trace §3.5.M → 210533 / 210700 | Wet-type freeze-exposed only; dry legs stay dry |
| PE Delegated-Design Submittal | Keep; raise to QFPE/engineer-of-record stamp on hyperscale Layer-3 |
| Local foreign AHJ overlays | **Do not import** (e.g. the site dry-ban / dual-FDC) unless this job’s AHJ |

### 3.12 Step — Δ layers + honesty close

Always print:

- Δ vs **NFPA 13-2025** on combination-riser / hose-allowance interface (standpipe ≠ 13 density×area).
- Δ vs adopted **NFPA 14** once edition pinned; list unheld section pins explicitly.
- Controlling layer per parameter (A–H).
- `[SYN]` screening flows (if any) vs sealed demand (if any).
- Open RFIs list (whether trigger text, NFPA 14 gpm, residual mechanism, FDC-full-demand, local amendments, hose-omit letter).

---

## 4. Outputs / artifacts

Write **only** to the caller-named path (or return in-response and stop). Typical package:

1. **Status register** (§1.4) + Hard-scope fence result (STS consume; SI/NI/foam/mist posture).
2. **Election memo** — whether (L1/L2/L3) · Class/hose · height-tier type · wet/dry legs · residual target · pump↔FDC rule · FDC flags · multi-zone fence · ITM drain flag.
3. **Demand register** — structure + held/unheld pins; **no invented gpm**; screening flows labeled `[SYN]` if used.
4. **MasterSpec §211200 edit-matrix checklist** (generic).
5. **Open RFIs** — each with blocking/non-blocking tag.
6. **Reciprocal HAND OFF lines** to live peers.
7. **Δ vs NFPA 13-2025** (interface) + Δ vs NFPA 14 (once pinned) + `[SYN]`/`[V]` register.

Do **not** emit: hall density×area transcript, hydrant P(Q) rebuild, pump nameplate, campus loop resize, AGF product SKU matrix, CAD coordinates, CASE_INDEX retrieval, foam/mist/clean-agent BOD, or KB writes.

---

## 5. Stop

> **2026-10-07 intake rule:** any item below that is a missing packet, a missing upstream result, or a missing input blank is **not** a Stop — proceed with a stated `ASSUMED` value (value + why), flagged in the output and status register. Only company scope-lock items (SI/NI-as-BOD → `RFI-variance`, foam, water mist `PRACTICE REFUSED`, clean agent as company BOD) and wrong-Skill / out-of-scope routing remain hard Stops.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away only.
2. Missing `dc-fp-assignment-packet` → not a Stop (packet optional). Missing STS → `ASSUMED` (flagged), not a Stop. Missing matrix rows when dual → assume most-stringent row (`ASSUMED`, flagged) or hand off, then return.
3. NFPA 14 gpm / simultaneous-demand needed but primary unheld → stated `ASSUMED` + `[V]` + RFI, not a Stop — **never silently invent or present as cited**.
4. Model / adopted §905 trigger text unheld → stated `ASSUMED` whether-answer + `[V]` + RFI, not a Stop — do not present thresholds as cited.
5. Class II/III or occupant hose presented as elective BOD without written AHJ/owner force → Stop / RFI.
6. Heat-trace invented as substitute for dry leg or heated valve house → Stop; consume freeze strategy.
7. the site CE-1353 / Fargo 5 psi / other foreign local overlays imported as universal → Stop / refuse import.
8. Caller wants hydrant P(Q), pump nameplate, loop diameter, ITM interval calendar, or CAD as this Skill’s deliverable → wrong Skill / handoff.
9. KB / EXERCISES / ARCHIVE writes; CASE_INDEX retrieve.

---

## 6. Citations (section AND edition)

| Claim | Pin | Status |
|---|---|---|
| Standpipe *whether* is code (§905), not NFPA 13 hazard | IFC/IBC Ch.9 **§905** adopted edition; UFC **§9-10** when federal | Model 2024 text unheld → `[V]` |
| the site height triggers / dry ban / 1000–1250 caps | the site FMO CE-1353 (rev. Jun 2024) citing the site-amended **2021** IFC/IBC §905.3.1 / 905.8; NFPA 14 7.10.1.1.5 as checklist pointer | **Local example only** |
| Manual <75 ft / auto 75–150 / auto ≥150; residual 65/100; combination pump rule | UFGS **21 12 00** §1.4 / §1.4.1 | Federal template; its 65 psi residual is comparison-only below the NFPA 14 100 psi floor (pull 14-01) |
| Class I default; PRV where outlet could exceed 125 psi; set 100 psi | UFGS §1.4 / §2.1.3.1 | Federal template |
| Type dial Manual/Automatic × Wet/Dry; heat-trace → 210533 | MasterSpec **§211200** (2013 / 06/12) | Edit before CD |
| ≥4 in. / 250–500 gpm test drain | AXA XL **PRC.12.0.2** (2020) p.19 | Insurer feature → ITM handoff |
| 500/250 demand shape; 1000 gpm light-hazard fully-sprinklered cap | Clarke/Schirmer 2006 secondary | `comparison-only` — DC ≠ light hazard |
| 400 psi ceiling; 300 psi advocacy; FDC 2024 full-demand rumor | NFSA Hopkins 2026 secondary; code: 400 psi [CODE 2024 §10.2 / 2019 §7.2, pull 14-01], FDC [CODE 2024 §10.7, pull 14-01] | 300 psi advocacy stays secondary |
| Hazen-Williams C for standpipe steel | UFGS §1.4.2 → **C = 120** steel (distinct from shop dry/DI **C = 100**) | Label both; do not conflate |
| Acceptance hydro ≥200 psi / 2 h; flush ≥10 min; flow ≥250 gpm / 5 min per riser | UFGS §3.7 / §3.8 | Template; reconcile to adopted NFPA 14 acceptance: 2024 Ch. 12 (hydro §12.4.1, flow §12.6) / 2019 Ch. 11 (hydro §11.4.1, flow §11.5), pull 14-02 |
| Seattle manual-dry permission, 10–20 psi supervisory air, FDC/hydrant geometry, hydro, no flow test | Seattle FD **AR 9.03.25** (eff. 2025-09-25) §3.1 / §3.4 / §3.7 / §3.10 / §5.1 / §5.2; AR 9.03.20 (eff. 2020-03-01) superseded | **Seattle only** |
| Packaged supervisory air: low < 7 psig / high > 23 psig; 15 SCFM @ 100 psig | UFS **STANDPIPE-PAC XL**, data sheet **UFS-213 Rev 1.01** (Dec 2021) | NYC/Boston construction & demolition — not a national or permanent-building rule |
| Manual-dry Class I package shape, and where it fails | EXERCISES worked package, case `case-2026-10-05-bh` (verdict corpus-insufficient) | Synthetic; negative example — §3.5.1 |

**Absent / `[V]` (refuse invent):** NFPA 14 annex text (pull 14-01 held body text only: flow, residual, 400/350 psi, FDC sizing, auto-dry 3 min; pull 14-02 adds acceptance: 250 gpm at the most remote hose connection within 3 min of opening the valve, 2024 §12.6.7.2 for all auto/semiauto systems, 2019 §11.5.7.2 only where system capacity exceeds 750 gal); manual-dry fill time (none in any edition — [UNSOURCED / company practice]); **model IFC/IBC-2024 §905** commercial trigger text; IFC Ch.80 **NFPA 14 row** on many statewide adoptions.

---

## 7. the engineer Way

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance`. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent = hand-away only. Status every run. Packet optional; STS (+ matrix when dual) consumed when present, else `ASSUMED` (flagged). **NO PLACEHOLDER.** **Never silently invent NFPA 14 gpm — ASSUMED + [V] when unheld.**
2. Three-layer most-stringent **per parameter** (whether, class, type, residual, gpm, pump↔FDC, FDC flags, test drain).
3. Standpipe ≠ white-space suppression. *Whether* = §905 / UFC / owner — not NFPA 13 HC.
4. Height-tier × freeze fork × MasterSpec dial — consume freeze; do not invent heat-trace.
5. Cite section **and** edition; enforced ≠ latest; local AHJ pins stay local.
6. Show-and-verify static head and any screening HW; flag `[SYN]` / `[V]`; demand needed but primary unheld → `ASSUMED` + `[V]` + RFI, not a Stop.
7. Manual <75 ft → pump excludes standpipe Q; still verify campus can deliver standpipe flow once sealed.
8. Hand FDC/drain/pump/loop detail to peer Skills — do not absorb their scope.

If notes conflict, **most-stringent wins** and both sources stay visible.

---

## 8. Not this Skill

| Work | Where |
|---|---|
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier BOD authorship | `most-stringent-basis-matrix` — consume+return when dual |
| Assignment packet authorship | `dc-fp-assignment-packet` — consume only |
| Hydrant P(Q) / pump need verdict | `hydrant-supply-curve` |
| Listed churn / 100% / 150% envelope | `pump-envelope` — receives pump-include/exclude flag |
| Campus loop diameter / one-leg-out | `campus-looped-main-sizing` |
| ≥4 in. drain checklist / AGF product / ITM intervals | `itm-design-for-testability` |
| Hall DI ≤30 s / volume-cut proof | `dry-preaction-water-delivery-screen` — freeze/dry consume only |
| White-space density×area | `density-area-dry-increase` |
| Freeze OEM heat-trace package | Freeze program Skill / note — consume posture only |
| Clean-agent concentration / enclosure | Clean-agent Skills — **hand-away only** |
| CAD / KB / EXERCISES / ARCHIVE writes | forbidden |

---

## 9. Runner checklist (execute in order)

0. **Hard scope + status register first.** STS = wet|dry|DI (consume — do not elect). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away. Packet if present (optional); matrix when dual (consume+return). Emit status skeleton (§1.4). Restate **no silent NFPA 14 gpm — ASSUMED + [V] when unheld**. **NO PLACEHOLDER.**
1. Pin AHJ edition + NFPA 14 posture + UFGS/MasterSpec/AXA/NFSA pins; mark unheld primaries `[V]`.
2. §905 / UFC / owner **whether** screen — provisional if trigger text unheld; no invented thresholds.
3. Class I + hose-omit path; Class II/III → Stop/RFI without written force.
4. Height-tier type (manual/auto) × freeze fork (wet/dry legs); consume freeze; residual honesty (65/100 competitors). On a manual-dry leg, pin the supervisory-air band to the AHJ (§3.5.1: national floor NFPA 14-2024 7 psi min / 20 psi max [§8.3.2.1.2, §8.3.2.1.3]; NFPA 14-2019 requires supervisory air [§6.1.1] with no psi band (not required under 2019, pull 14-12); Seattle 10–20 psi where adopted, most stringent per parameter; UFS 7/23 psig is a NYC/Boston factory setting. Verify with the engineer of record: the UFS 23 psig high switch sits above the 14-2024 20 psi maximum; conservative assumption = set the high-pressure supervisory switch at or below 20 psi) and size air to the held volume.
5. Demand register structure — stated `ASSUMED` + `[V]` + RFI if gpm needed and primary unheld (not a Stop); screening as `[SYN]` / `ASSUMED`.
6. Pump↔FDC additivity; emit pump-include/exclude; hand campus flow verify to hydrant/loop peers.
7. FDC flags (handshake); multi-zone/300-psi pointer (not invent); ITM ≥4 in. drain handoff.
8. MasterSpec §211200 edit-matrix checklist (generic); strip foreign AHJ overlays.
9. Δ vs NFPA 13-2025 interface + Δ vs NFPA 14; status register complete; `[SYN]`/`[V]`; open RFIs; reciprocal HAND OFF lines.
10. Write **only** to caller-named path (or return and stop).

## 2026-10-29 PDT — prior fold Lead25: B23-R3 wet Class I demand teaching case + NEGs
Source: `EXERCISES/worked/batch23-r3__wet-class-i-standpipe-demand.md` (`_calc` exit 0). Synthetic 5-story 75 ft colo, 3 stairs, sprinklered throughout, C=100.
- Edition: model NFPA 14-**2024** (Ch.10 numbering); the site default NFPA 14-2019 (provisional; [V] edition). Trigger IFC/IBC 2024 §905.3.1.
- Flow: 500 gpm most-remote standpipe (§10.6.1.1.1) + 250 × 2 additional (§10.6.1.1.4) = **1,000 gpm**, cap 1,000 sprinklered (§10.6.1.1.6). Combined: greater of sprinkler or standpipe (§10.6.1.3.1); sprinkler hose not added (§10.6.4). DI sprinkler 390 + 250 = 640 < 1,000 → standpipe governs.
- Pressure at base: 100 residual (§10.2.6.1) + 28.17 elev + 0.96 riser + 3.88 common + 3.0 hose valve (SYNTHETIC) = **136.0 psi @ 1,000 gpm**.
- Pump 1,000 gpm @ **80 psi**: 57.34 + 80 = 137.34 ≥ 136.01 → **PASS, 1.33 psi margin (thin — Verify with the engineer of record using the real hose-valve loss)**; churn 175 max sits at equality (flag). Pump @ **100 psi**: churn 183/203 > 175 → **FAIL** (NFPA 20-2025 §4.7.7.1).
- the site IFC 2021 §913.6 (20 psi @ 150 %): 51.02 → PASS. ≥3 standpipes → ≥2 two-way FDC inlets (the site §905.2.1).
- **B23R3-NEG-1:** stacking 1,000 + 390 + 250 = 1,640 gpm, which ignores §10.6.1.3.1/§10.6.4. **B23R3-NEG-2:** a 4th stair taken to 1,250 gpm overruns the 1,000 cap (1,250 applies only when not sprinklered).
- OPEN/GAP: FDC/check losses (dims GAP); PRD at max churn ≈172.8 borderline → shop curve.

## 2026-10-29 PDT — prior fold Lead26: R5 errata feed (core-r13 + the site §905.8)
Source: errata note on the NFPA 14 section renumber and the local §905.8 amendment.
- When citing NFPA 14-**2024**, use **§10.x** (demand §10.6; PRD >175 static §10.2.4.2; residual §10.2.6.1). §7.8/§7.10 is 2013–2019 numbering, so check the edition label before citing.
- UFGS 125 psi PRD trigger is agency/owner practice, not code (owner layer only).
- **the site §905.8:** dry standpipes are not installed **except where subject to freezing, per NFPA 14**. Do not teach a blanket "dry prohibited in the site" (CE-1353 printing drops the exception).
- [V]: the site NFPA 14 edition (2019 provisional), NFPA 14-2019↔2024 crosswalk; hose-valve 3.0 psi ASSUMED / 1.33 psi margin; Verify with the engineer of record.

## Canada (BC / AB / ON) — B26-R3 / Lead28 fold, 2026-10-29

Canada unlocked (SK parked). On a Canadian site the *whether* trigger is **NBC/BCBC/NBC-AE/OBC 3.2.5.8**, not IFC/IBC §905. Pin NFPA 14 = **2013** and NFPA 24 = **2013** (AB/ON; BC NFPA 24 = BCFC GAP) per `most-stringent-basis-matrix` §4.2b.

- **Whether:** 3.2.5.8.(1) — standpipe if >3 storeys, or >14 m to top-storey ceiling, or ≤14 m but over the Table 3.2.5.8 area *unless sprinklered throughout*. A 1-storey ≤14 m fully sprinklered hall → **no code standpipe** in BC/AB/ON (PASS). Watch "throughout": any unsprinklered space (raised-floor omission, MMR) can lose the waiver — re-check Table area (ON F2 1 500 m²).
- **If elected (owner/FD):** design to NFPA 14-2013; 3.2.5.9.(2) bars only a dry standpipe *not connected to a supply* → automatic-dry or wet OK; 3.2.5.9.(3) supply cap **30 L/s (475.5 gpm)** as code minimum (NFPA 14-2013 500 gpm first standpipe = owner choice, § [verify]); OBC 3.2.5.9.(4) 690 kPa residual unless sprinklered/no pump/FDC full demand; hose connections **in exits** (3.2.5.10); 64 mm outlets, no 38 mm in sprinklered buildings (3.2.5.11).
- **FDC (3.2.5.15):** ≤45 m unobstructed to hydrant (all); **AB only 3.2.5.15.(3): 3–15 m from principal entrance** (absent NBC 2025/BCBC 2024; OBC [verify]). Site the FDC early with civil — the principal entrance is often the admin block.
- **Private main:** install/test per NFPA 24-2013 pin, text **[nearest]** 24-2022/2025 until re-verified. the province DSSP 2018: ≥150 mm, any leg ≤180 m to hydrant or looped; check-valve loop at ≥2 private hydrants. AE 3.2.5.7.(4): NFPA 13-sprinklered → supply = NFPA 13-2019 demand + hose. Teaching `_calc` (C=100, 150 mm, 590.6 ft): 475.5 gpm → 7.36 psi; 500 → 8.08; ASSUMED 750+475.5 = 1,225.5 → **42.41 psi** → CONDITIONAL PASS; elect loop or 200 mm for hyperscale; prove on `hydrant-supply-curve`.
- **B26R3-NEG-1 (FAIL):** US IFC 100 ft FDC-to-hydrant cited on a Canadian set — mis-cite and drops the AB 3–15 m entrance band. Cite 3.2.5.15; a tighter distance only as a labelled owner rule.
- **B26R3-NEG-2 (FAIL):** NFPA 14-2024 dry-standpipe air band put on a 14-2013 pin — 14-2013 has no numeric band (supervisory air §6.1.1; 20 psi over trip §5.2.1.4.10). Latest ≠ enforced.
- **Stop — CAN/ULC-S561 (prior fold Lead31, GAP-B29R1-2):** any CAN/ULC-S561 supervising-station or reduced-duration claim → **NEEDS HOLD (GAP-B27R2-3)**; do not invent hours/durations.
- **Stop — CSA B139 (prior fold Lead31, GAP-B29R1-2):** fuel/oil piping at a diesel FP / standpipe pump-house interface → **NEEDS HOLD**; do not invent CSA B139 body text.
- Open [V]: NFPA 14-2013 Class I 500 gpm section; NFPA 24-2013 text; OBC 3.2.5.15.(3); Vancouver/Markham servicing standard; VBBL inside Vancouver.

## prior fold / Lead27 fold (2026-10-29) — hose-valve maker-loss sensitivity (B25-R4, US teaching case)
Source: EXERCISES/worked/batch25-r4__standpipe-hose-valve-maker-loss-sensitivity.md; _calc run 2026-10-29-batch25-r4 (exit 0). Synthetic 5-story colo.
- Fixed required (100 residual + 28.17 elev + 0.96 riser + 3.88 common) = 133.01 psi. Available at 1,000 gpm = 137.34 psi. **Margin = 4.33 − hose-valve loss**, so every psi of valve loss is a psi of margin. The 3.0 psi ASSUMED teaching loss gives **+1.33 (thin PASS, Verify with the engineer of record)**. Break-even is 4.33 psi, about 14.3 ft EL at 0.3018 psi/ft for a 2½ in outlet at 250 gpm, C=100.
- **B25R4-NEG-1:** a 5.0 psi valve loss gives −0.67, FAIL. The thin margin is smaller than the plausible valve-loss uncertainty. Fix with listed valve data (NFPA 14-2024 §10.2.6.1.1), a larger pump, or a bigger main. **B25R4-NEG-2:** the FM DS 3-0 **4 in** angle-valve EL applied to a 2½ in outlet gives 7.55 psi FAIL. That is the wrong method, because EL rows are size-specific and FM DS 3-0 is not the NFPA 14 basis.
- **GAP:** no maker-published 2½ in hose/angle/PRV-valve loss sheet in corpus, so none is invented. the site NFPA 14 edition is unpinned (14-2019 ASSUMED). No the site restamp.

## prior fold / Lead30 fold (2026-11-02) — Class I 2½ in hose-valve loss 4.0 psi envelope; PRV break; NFPA 14 2019↔2024 pin
Sources: B28-R2 pipeline synthesis `KNOWLEDGE_BASE/30_water-based-suppression/class-i-2-5in-hose-valve-loss-maker-data-synthesis.md` (Lead30 ACCEPT FULL); B28-R3 crosswalk `KNOWLEDGE_BASE/70_codes-standards-insurer-basis/nfpa-14-2019-2024-section-crosswalk.md` (ACCEPT FULL); R5 the site `04_…/class-i-hose-valve-loss-bod-note-batch28-r5.md`. `[SYN]` US teaching case; Canada gates above kept unchanged.
- **Hose-valve loss @ 250 gpm, C=100 (maker data):** Elkhart angle ≈ **3.1 psi** (graph ±0.2) — clears the 4.33 break-even; Giacomini full-open Cv 125 → **4.00 psi** — clears by 0.33 (thin); **pressure-restricting setting Cv 73.32 → 11.6 psi — breaks** (B25-R4 margin goes negative). A PRV / restricting hose valve must be carried with its own listed loss at its set position, never the full-open number.
- **Design envelope elected: 4.0 psi** hose-valve loss — this is a **data bound**, not a listing value (Lead30 dated note); Class III valve listing caveat applies (Class I election only; do not import Class III-listed data without [verify]). Supersedes the 3.0 ASSUMED teaching loss for new runs; B25-R4 margin on 4.0 = +0.33 (thin PASS, Verify with the engineer of record).
- **Residual pin:** 100 psi at the most remote 2½ in outlet = **NFPA 14-2024 §10.2.6.1 = NFPA 14-2019 §7.8.1**; maker hose-valve loss basis via **2024 §10.2.6.1.1** (2019 equivalent per crosswalk). Other held pairs: 2019 §7.2 → 2024 §10.2; §7.10 → §10.6. Check edition label before citing; crosswalk has 11 rows missing LiNK — treat those as [verify].
- **Canada pin:** NFPA 14-**2013** (AB/ON per §4.2b) — use 2013 numbering (§7.8.1 family); this fold adds no Canadian cite.
- Open: Potter-Roemer 4085 / Elkhart current cut sheet [verify]; 11 crosswalk LiNK rows.


## 2026-11-03 — prior fold Lead31: GAP-B29R1-2 narrow Canada stops
Added S561 (→ GAP-B27R2-3) and CSA B139 NEEDS HOLD stop lines to the Canada section. NFPA 14-2013 pin, OBC 3.2.5.8, B26R3-NEG-1/2 unchanged. No ULC/CSA/OBC body invented.

## 2026-11-04 — prior fold Lead32: B30R4 Class I demand close (hose-valve 4.0 + thin margin)

Sources: `EXERCISES/worked/batch30-r4__class-i-standpipe-demand-close.md`; `_factory/STATUS-2026-11-04-batch30-lead32.md`; `_factory/REPORT-2026-11-04-batch30.md`; prior fold CLOSE. `[SYN]` the site 2-story DI hall teaching case. Canada NEG-CA / S561 / CSA B139 stops from Lead31 stand — **do not invent OBC/S561/CSA body**. Foam/clean locked. Do **not** reopen GAP-B28N2-1 (nitrogen P≤25 CLOSED).

### Controlling stack (B30R4-1)
| Line | psi |
|---|---|
| Residual at most remote 2½ in outlet | 100.00 — NFPA 14-2019 §7.8.1 = NFPA 14-2024 §10.2.6.1 |
| Hose valve @250 gpm, full-open | **4.00** — current maker envelope (Giacomini F.O.); **not** Table 11.3.1.3 fallback when current maker data is held (§10.2.6.1.1) |
| Elevation 22 ft | 9.53 |
| Riser 6 in Sch 40 ID **6.065** @500 (`_calc` hw) | 0.62 |
| Feed 8 in Sch 40 ID **7.981** @750 (`_calc` hw) | 3.04 |
| DCDA / check / alarm | **8.00 ASSUMED** → **Verify with the engineer of record**; do not promote without maker device losses |
| **Required @ pump** | **125.19** |
| Available | 125.60 |
| Margin | **+0.41** thin PASS / Verify with the engineer of record |

Churn 82 + 91 = 173 ≤ 175 → no PRD trigger at 2½ in outlets (14-2019 §7.2.3.2 / 14-2024 static >175 path). 6 in feed (ID 6.065 @750, 400 ft) = 11.58 → **−8.13 FAIL**; 8 in feed decision stands.

### Pins to apply on every US Class I demand run
1. **Hose-valve loss:** use the **current maker envelope 4.0 psi @250 gpm** (prior fold/Lead30 elected; prior fold R3 AFS hygiene leaves 4.0 unchanged). Do **not** fall back to NFPA 14 Table 11.3.1.3 when current maker data is held. Class III listing caveat on Giacomini stands — confirm Class I before submittal.
2. **ASSUMED device-stack** (DCDA / check / alarm / similar): label **ASSUMED** and **Verify with the engineer of record**. Thin margins under an ASSUMED stack are not live-job PASS without maker losses. Verify with the engineer of record (GAP-B30R4-1).
3. **Greater-of, not sum:** combined system demand = greater of sprinkler(+hose) **or** standpipe — **not** the sum. Cite the edition in force. NFPA 14-2019 §7.10.1.3.1.1 and NFPA 14-2024 §10.6.1.3.1 state the same greater-of sentence (GAP-B31R1-1 closed). NFPA 14-2019 §7.10.1.3.1.2 stays on the 2019 pin. Do not drop the edition label. If sprinkler(+hose) > standpipe flow, re-run feed/riser loss at that flow. The greater-of re-check itself is closed. Summing the two demands stays a failure (B30R4-NEG-5).
4. **NEG — AFS indicative as design (B30R4-NEG-4):** AFS NYC graph ≈2.5 psi @250 is **indicative only** (graph-read, not tabulated). Using 2.5 as design inflates margin falsely. Keep 4.0 envelope.
5. **NEG — PRV / restricting at remote when static <175 + thin margin (B30R4-NEG-3):** remote 2½ in outlet must be full-open / non-restricting when static ≤175 and margin is thin; a PRV/restricting setting adds loss beyond 4.0 and fails 100 psi residual. Carry listed set-position loss only when a PRV is actually required.
6. **Sch 40 IDs via `_calc`:** use Schedule 40 IDs (6 in → **6.065**, 8 in → **7.981**) through `_calc/run.py` `hw`. Do **not** hand Sch-10 IDs (e.g. 6.357) on standpipe riser/feed takeoffs for this teaching stack (B30R4-NEG-1 root cause with omitted valve loss).

### NEG teaching ids (keep full prefixes)
- **B30R4-NEG-1** — omitting hose-valve loss and/or hand H-W not through `_calc` (DT root cause).
- **B30R4-NEG-2** — 6 in feed FAIL (−8.13).
- **B30R4-NEG-3** — PRV/restricting at remote under thin margin / static <175.
- **B30R4-NEG-4** — AFS ≈2.5 as design.
- **B30R4-NEG-5** — summing standpipe + sprinkler demand.
- **B30R4-NEG-CA** — Canada invent wall (OBC / CSA B139 / ULC S524–S561); model A gate — US NFPA 14 numbers above are US basis only.

### Open GAPs (do not invent close)
GAP-B30R4-1 device-stack maker at 750 gpm stays open. GAP-B30R4-2 greater-of re-check is closed. GAP-B30R4-3 is closed: hand Hazen-Williams matches the kernel to four decimal places, and the +0.41 psi result stays a thin pass. Verify with the engineer of record. GAP-B31R1-1 is closed. The FM rated-cap check stays open (GAP-B31R1-2). Potter-Roemer 4085 curve still procurement.

Supersedes B23/B25 **3.0 ASSUMED** teaching loss for **new** US runs (prior fold 4.0 envelope already elected); B23/B25 historical margins stay as dated sensitivity only.

## 2026-11-04 — stop-vocab normalize (staged)
- `structure the demand register and **Stop / `[V]` / RFI** when the prim…` → `structure the demand register and carry a stated `ASSUMED` value (value + why) + `[V]` + R…`
- `sealed gpm / simultaneous-demand / residual-mechanism section pins → *…` → `sealed gpm / simultaneous-demand / residual-mechanism section pins → stated `ASSUMED` valu…`
- Inserted §1.0 Country/edition gate (model A) + NEG-CA before §1 (Canada section unchanged).
- Kept hard: Class II/III → Stop/RFI unless written force (company/owner fence, not a missing-input stop); 'output path unnamed → return in response' (not a design stop).

## Greater-of demand and FM rated cap

Synthetic teaching only. Re-derive every gpm and psi on the job. Do not copy a hall. Do not apply these NFPA 14 numbers as a Canada basis. Do not invent OBC, CAN/ULC-S561, or CSA body text.

1. **Greater-of, not sum.** Combined demand is the greater of sprinkler demand (including hose) or standpipe demand. NFPA 14-2019 §7.10.1.3.1.1 and NFPA 14-2024 §10.6.1.3.1 state the same greater-of sentence. On a 2019 pin also cite §7.10.1.3.1.2. Keep the edition label on the cite.
2. **Supply at the governing flow.** When sprinkler demand (including hose) is larger, re-run feed, riser, and supply loss at that flow. Show the arithmetic.
3. **Remote outlet at its own flow.** The most remote 2-1/2 in. outlet still has to make its residual at the standpipe flow. A pass at the sprinkler point does not waive that check.
4. **FM rated cap, when that sheet applies.** Single pump: rated flow at least demand divided by 1.4 (FM DS 3-7 §2.4.6.4). Multiple pumps: the 1.10 factor in §2.4.6.5. An NFPA 150 percent pass with an FM fail stays open. Carry the next listed size as ASSUMED. Verify with the engineer of record. Do not resize silently. Hand the envelope to `pump-envelope`.

Teaching point [SYN], a two-story double-interlock hall on an NFPA 14-2019 pin: sprinkler plus hose at 1,055.9 gpm governs over a 750 gpm standpipe. The sprinkler point passes. The remote standpipe check at 750 gpm is a thin pass on an ASSUMED 8.0 psi device stack. Verify with the engineer of record. A graph-read near 3.2 psi is indicative only. Do not use it as the design loss to widen that margin. Where FM applies, 750 gpm rated needs at least 754.2 gpm (1,055.9 / 1.4) and fails. Next listed size 1,000 gpm is ASSUMED if FM governs. Do not freeze a model number.

Failures: summing sprinkler and standpipe demand; checking supply only at the standpipe flow when sprinkler demand governs; dropping the remote-outlet check because the sprinkler point passed; calling a pass on the NFPA cap alone when FM applies and rated flow is under demand / 1.4; promoting the graph-read stack to design.

Open: the FM rated-cap size; the device-stack maker loss at the governing flow. Foam and clean agent stay locked.

## Alarm-check length and backflow maker spread

Synthetic teaching only. Re-derive on the job. Do not copy a hall. Do not apply these numbers as a Canada basis.

- An 8 in. alarm check valve is 29 ft equivalent length at C = 120, Schedule 40 (Reliable Bulletin 400, April 2025, Table D, and Reliable Bulletin 412, January 2021). Convert that length to C = 100 with the kernel's NFPA 13 multiplier. Do not guess the conversion by hand. A 37 ft figure for Bulletin 412 is not held. Do not cite it.
- A standalone 8 in. check at Cv 1800 is (750 / 1800) squared = 0.174 psi at 750 gpm (Victaulic 717, publication 10.08 Rev Y). Equivalent length for that check still needs the engineer of record. Do not promote the 0.174 psi figure to the design stack.
- Eight-inch backflow loss at 750 gpm, read from graphs and not from a table: one make is about 3.0 psi and another is about 6.5 psi (band 6.3 to 6.8). The spread is about 3.5 psi. Those reads are indicative. The design stack stays the ASSUMED 8.0 psi until the basis of design names the make and the engineer of record accepts the sheet (GAP-B30R4-1).
- Failures: using the lower graph-read to widen the +0.41 psi margin without that make on the basis of design; citing 37 ft as a held Bulletin 412 length; treating a graph-read as tabulated design data.
