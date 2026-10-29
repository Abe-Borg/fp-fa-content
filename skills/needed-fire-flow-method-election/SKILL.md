---
name: Needed fire flow method election
description: >-
  use this when the AHJ, purveyor, or owner asks how much fire flow the campus
  needs and which method binds (country gate US or Canada; Canada uses
  NBC 2023 Alberta Edition, BCBC 2024, or OBC 2024 at 3.2.5.7) (ISO Note-1 sprinklered path vs IFC Appendix B
  where adopted vs UFC §9-2 / App. C vs purveyor max-available / other named
  method) — packet optional; STS wet|dry|DI consumed or ASSUMED; produce a parameterized
  NFF / hydrant-credit geometry memo that can govern loop, tank, and pump
  envelopes; SI/NI-as-BOD → Stop RFI-variance; foam prohibited; mist PRACTICE
  REFUSED; never silently invent IFC App B or ISO NFF table values (ASSUMED + [V]); not hydrant 2-pt P(Q), not
  hall density×area, not listed pump envelope, not CAD.
---

# Needed fire flow method election

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable data-center fire-protection recipe. **Country gate (US | Canada).** US pins below stay on a US job. On a Canada job read section 1.0. Do not port a US pin into a Canada row or a Canada pin into a US row. **This Skill decides WHICH fire-flow method binds for this AHJ / purveyor / owner, structures the NFF / required-fire-flow register, distinguishes AHJ fire-flow from sprinkler `qd` at the BOR, and emits hydrant-credit / overlapping-coverage geometry flags at handshake level** — after the assignment packet exists and STS has elected company `wet` | `dry` | `DI`.

It does **not** elect the hall sprinkler/preaction family (consume STS). It does **not** rebuild the hydrant 2-point `P(Q)` curve (`hydrant-supply-curve` owns that — and that Skill **explicitly fences out NFF / App B**). It does **not** invent IFC Appendix B table values, ISO FSRS hydrant-credit gallons, or commercial NFF duration gallons when the primary is unheld. It does **not** CAD hydrant coordinates. It does **not** design foam, mist, CAF, or clean agent.

**Core thesis:** There is **no national fire-flow rule**. Step 0 is always **which instrument is asking** — code (IFC Appendix B *only if adopted*), purveyor contract / max-available policy, UFC §9-2 / Appendix C (federal), insurance-*rating* ISO/Verisk NFF (no permit force by itself), property-carrier demand via ISO Note (1), or owner standard. For a commercial building sprinklered per NFPA 13, **ISO Note (1) (Guide EDITION 06-2014 p. 2)** switches off the entire `18F√A` apparatus: **NFF = demand at the base of the automatic sprinkler riser + inside/outside hose-stream demand.** Fire flow is then an **OUTPUT of the FP design**, not an input from a footprint formula — and the three-layer basis propagates into the public main / campus loop. Where IFC Appendix B is adopted, a **code floor** (FEMA/USFA 2009 reporting IFC 2006/2009: up to 75 % sprinkler reduction, floor **1,500 gpm / ≥ 2 h** — `[V]` vs **IFC-2024**) can exceed a wet hall's own `qd` and **govern**. **Never invent App B / ISO table values** — structure the register and **Stop / `[V]` / RFI** when the primary is unheld. Charlotte / Mecklenburg outline material is a **method spine and local overlay example**, not universal AHJ defaults.

**Design practice:** three-layer most-stringent **per parameter** (method election, sprinklered-path NFF definition, unsprinklered bound, App B floor where adopted, hydrant-credit geometry, duration / concurrent campus demands, purveyor max-available). Delta vs **NFPA 13-2025** where the sprinkler interface / hose-duration matters (under ISO Note (1), NFF *is* the 13 demand + hose — delta lives one layer up when FM / owner raise density, or the other way when an App B floor exceeds `qd`). Cite **section AND edition**. Show-and-verify math. `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock` only** (consume STS — do **not** elect); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**; clean agent = **hand-away only**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet (optional) + STS `wet`|`dry`|`DI` (consumed, else `ASSUMED`) (+ `most-stringent-basis-matrix` when dual — **consume and return here**). Consume density-area / hall `qd` when the sprinklered path binds — do **not** rebuild density×area. Caller-path-only. **NO PLACEHOLDER.** Generic — do not copy Charlotte CFD, Raleigh RFD, NC SCO, one city, or UFC federal apparatus as universal AHJ. Owner may **raise, never lower**.

**Honesty — tables and duration unheld.** Corpus holds ISO Guide **EDITION 06-2014** Note (1) + `18F√A` caps / C-2 unsprinklered bound (show-and-verify), FEMA/USFA EFOP **2009** side-by-side method comparison (secondary; IFC App B adoption rule + reported 1,500 gpm / 2 h floor + hydrant-distance paraphrase), Charlotte / Raleigh / NC SCO **local** overlays, and UFC 3-600-01 §9-2 pointer + **Appendix C unheld**. **Licensed IFC-2024 Appendix B tables absent. ISO FSRS hydrant-credit / commercial-duration tables absent.** Recipe structure is **Ready**; sealed App B gpm / duration gallons / FSRS credit gallons → **Stop / `[V]` / RFI**. Do not size tank volume on an unverified duration.

Write the method-election package **only** to the path the **caller** names. Write output only to the caller-named path.

Look up shop codebook notes **by title**: *Needed / required fire flow determination methods*; *Water-supply analysis & the supply-vs-demand curve*; *Private fire service mains and campus loop*; *Design practice*; *Enforced-vs-latest edition resolver*; *Fire-pump selection & installation*.

---

## 1. Hard scope gate

### 1.0 Country gate (US | Canada)

Required at intake: country is US or Canada. On a Canada job, name the adopted code: NBC 2023 Alberta Edition, BCBC 2024, or OBC 2024. Another province is ASSUMED until the adopted code is named. An unresolved country is ASSUMED. It is not a blanket stop. Verify judgment calls with the engineer of record. On a US job, sections 3.1 through 3.12 are unchanged.

| Adopted edition | Rule (paraphrase) | Sprinklered data-center outcome | Hold |
|---|---|---|---|
| NBC 2023 Alberta Edition, Div. B 3.2.5.7.(1) | (a) a piped municipal supply of at least 3,800 L/min at a residual of at least 140 kPa, or (b) a private supply of at least formula-Q from Table 3.2.5.7 | Applies only when sentences (3) and (4) do not exempt the building | Sentence (1) is held. The formula-Q figure is not quote-held. Do not compute it. Label it ASSUMED and verify |
| NBC 2023 Alberta Edition 3.2.5.7.(2) | A private supply of 2,700 L/min below 75,000 L, or 3,800 L/min at 75,000 L or more, with a dry hydrant (NFPA 1142 Chapter 8) or a pressurized hydrant (NFPA 24) | Private hydrants follow the NFPA 24 pin named by the Alberta Edition. That pin is the 2013 edition, which is not held. Cite NFPA 24-2022 or NFPA 24-2025 and label it the nearest edition | Sentence (2) is held. NFPA 24-2013 and NFPA 1142 are NEEDS HOLD |
| NBC 2023 Alberta Edition 3.2.5.7.(3) and (4) | The capacity requirements of sentence (1) do not apply to a building with an NFPA 14 standpipe (3) or with NFPA 13 sprinklers (4) | The capacity floor is exempt. Still show the sentence (1)(a) cross-check: 3,800 L/min is about 1,004 gpm at 140 kPa (about 20.3 psi). Sentence (4) is not a waiver of hydrant rules. Municipal DSSP and NFPA 24 rows still bind. Hand those to `hydrant-supply-curve` | held |
| BCBC 2024 Div. B 3.2.5.7.(1) and (2) | (1) an adequate firefighting water supply; (2) a building sprinklered throughout, or provided with a standpipe, is deemed to comply, except the case the code names | Deemed to comply. Supply is the NFPA 13 demand, plus hose, plus the insurer duration. Do not carry the Alberta Edition numbers onto a BCBC job | held |
| OBC 2024 3.2.5.7 | Performance language only. The body is not held | Treat the supply as a performance requirement and verify it before use | NEEDS HOLD. Do not quote the body |
| NBC 2025 3.2.5.7 | Performance. Deeming to NFPA 13 or NFPA 14 appears in a note only | Practice is similar to BCBC, but the deeming sentence is not code text | note only |

A note to 3.2.5.7 says FUS and NFPA 1142 should be consulted. That note is advisory.

Duration on a Canada job: Alberta Edition 3.2.5.7 capacity does not govern a sprinklered building, so duration is NFPA 13 plus the insurer sheet (FM DS 3-26 or FM DS 5-32). Do not invent CAN/ULC-S524, CAN/ULC-S561, or other ULC hours.

On a Canada job, do not:

- Use IFC Appendix B or an ISO needed-fire-flow number as the Alberta Edition code floor. Sentence 3.2.5.7 is its own rule.
- Cite an NFPA 24-2025 clause as the Alberta Edition pin unless it is labeled the nearest edition.
- Apply 3,800 L/min at 140 kPa, or formula-Q, to a BCBC job.
- Read sentence (4) as "no hydrant rules."
- Treat a municipal DSSP citation of "ABC 1997" as the enforced edition. Read it as NBC 2023 Alberta Edition 3.2.5.5 or 3.2.5.7 and confirm it with the authority having jurisdiction.
- Quote OBC 3.2.5.7 body text.

On the Canada path, the ISO, IFC, and UFC method election in sections 3.3 through 3.7 is replaced by this table. Section 3.8 (needed fire flow is not sprinkler demand at the base of the riser), section 3.9 (hydrant handshake), and section 3.10 (concurrent demands) still run.

### 1.1 Company system-family fence (consumes STS — does not elect)

This Skill owns **NFF / required-fire-flow method election, register structure, NFF-vs-`qd` distinction, hydrant-credit geometry handshake flags, and duration/concurrent structure**. Controlling company BOD for sprinkler/preaction families = **`wet` | `dry` | `double-interlock` only**.

| Role | Owner |
|---|---|
| Elect wet \| dry \| DI (hall / campus BOD context) | `suppression-technology-selection` (**consume** — do not elect here) |
| NFF method election / register / hydrant-credit flags / duration structure | **This Skill** |
| Dual-carrier per-parameter union | `most-stringent-basis-matrix` (**consume**, then **return here**) |
| 2-point municipal/hydrant `P(Q)` + pump need/no-need | `hydrant-supply-curve` (**peer** — fences NFF/App B out) |

Comparison-only (never elected here; never the controlling BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**This Skill does not elect hall families.** It **consumes** the completed the input packet and the STS token `wet` | `dry` | `DI`, then runs the method-election recipe.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling family on the packet:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** continue NFF arithmetic as if SI/NI were company-elected BOD.
6. SI/NI may appear only as **`comparison-only`** evidence — never an ordinary elective family option.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler / preaction | Permitted when elected upstream via STS | Consume hall/`qd` context under that BOD; do not elect |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water / CAF | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do **not** design/accept mist as BOD |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ | **Hand-away only** | Company does **not** design clean agent; Never company BOD here |
| ISU / IITRI / NFA fireground formulas as design NFF | **Reject** | Show arithmetic invalidity at DC scale; do not seal |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Clean agent = hand-away only.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Step-0 method election (which instrument binds) | System-family election (`suppression-technology-selection`) |
| Sprinklered ISO Note (1) path → NFF from consumed `qd` + hose | Density×area rebuild (`density-area-dry-increase`) |
| Unsprinklered ISO bound structure + show-and-verify caps | Hydrant 2-pt `P(Q)` / pump need verdict (`hydrant-supply-curve`) |
| IFC App B **path structure** where adopted — **no invented table gpm** | Listed churn/100%/150% (`pump-envelope`) |
| Hydrant-credit / overlapping-coverage **handshake flags** (not CAD) | Campus loop diameter (`campus-looped-main-sizing`) |
| Duration / concurrent-demand **register structure**; tables unheld → `ASSUMED` + `[V]` + RFI, not a Stop | Tank usable volume / NFPA 22 sizing (future / tank Skills) |
| Purveyor max-available / other named-method capture | Invent App B B105 / ISO FSRS / UFC App C table values |
| Method-election memo + open RFIs | Charlotte / Raleigh / SCO pins as universal defaults |
| Reject ISU / IITRI / NFA with arithmetic | CAD hydrant coordinates; foam/mist/clean-agent BOD |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** packet + STS (+ matrix when dual), **(c)** method election / which instrument binds, **(d)** sprinklered Note (1) vs unsprinklered path, **(e)** App B adoption + floor, **(f)** NFF vs `qd` distinction, **(g)** hydrant-credit geometry flags, **(h)** duration / concurrent register, **(i)** purveyor max-available, **(j)** legacy-method rejection, and **(k)** mist/foam/clean-agent if presented:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling election + editions supported by opened AHJ / ISO 06-2014 Note (1) / held cap arithmetic already closed for that parameter |
| `provisional` | Directionally pinned; IFC-2024 App B tables / ISO FSRS credit-duration / UFC App C flagged `[V]` — **never silent `grounded` on invented table gpm** |
| `unresolved` | STS / matrix(when dual) / AHJ adoption pin / governing `qd` not given when Note (1) binds — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, ISO rating-only PPC conversation, ISU/IITRI/NFA (rejected), Charlotte 13R 50% credit on a non-13R job, secondary FEMA paraphrase pending FSRS primary |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; hydrant `P(Q)`; campus loop; pump envelope; tank/duration storage; standpipe concurrent) |
| `RFI-variance` | SI/NI/foam/mist presented as BOD; or caller demands sealed App B / FSRS gallons with primary unheld and refuses RFI |
| `PRACTICE REFUSED` | Mist presented as controlling medium |

**Invented IFC App B / ISO FSRS / UFC App C table values as defaults → never `grounded`.**

### 1.5 Look-up-by-title + corpus honesty

Charlotte CFD Plan Review Guidelines / Raleigh RFD §6.17 / NC SCO §L.4 = **local Layer-1 overlays**, not model IFC-2024 and not universal. ISO Guide **06-2014** = insurance-*rating* instrument (PPC / BFF) with **Note (1)** load-bearing for sprinklered commercial — **no permit force by itself**. FEMA/USFA EFOP **2009** = secondary comparison (cites IFC 2006/2009, ISO 2008, retired NFPA UFC). UFC 3-600-01 **Appendix C** = **unheld** (re-mine pointer). Worked campus packages that mention NFF / App B as sensitivity = **`[SYN]` method** only — consume method, not synthetic gpm. **NO PLACEHOLDER.**

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent App B table gpm, FSRS credit gallons, commercial NFF duration, or AHJ adoption. Do not treat SI/NI as company BOD. Do not elect foam/mist/clean-agent.

| Input | Required | Notes / Stop |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume nearest components (`suppression` / `bod` / water-supply / AHJ). Do not rebuild; do not retrieve prior job files. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **STS token `wet` \| `dry` \| `DI`** | **yes** | From `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI-as-BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Consumed `most-stringent-basis-matrix` rows** | **yes when dual-carrier** | **Consume when present** (missing → `ASSUMED`, flagged) — do **not** Stop-away forever. Unresolved controlling hose / duration / fire-flow rows → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here**. |
| **AHJ fire-code + edition + Appendix B adoption Y/N** | **yes** | Parameterize. Appendices are **not** code unless the adopting ordinance names them (FEMA/USFA 2009 p. 16). Missing adoption pin → **not a Stop**: carry adoption as a stated `ASSUMED` (which, and why — prefer the more stringent result), flagged + RFI; never present App B as adopted code without the ordinance. |
| **Purveyor / utility fire-flow policy** | **yes when municipal supply** | Max-available / demonstrate-to / contractual. May be the binding instrument when App B unadopted. |
| **Governing sprinkler / DI demand context** | **yes when Note (1) / sprinklered path binds** | Consume `density-area-dry-increase` `q_spr` / `qd_gpm` / hose / duration — **largest campus BOR demand** (often staging/decant / DS 8-9, not white space). Do not rebuild density×area. Missing when path binds → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged / `handoff`. |
| **Building / campus geometry for credit screen** | **yes for hydrant-credit flags** | Hose-lay routes, setbacks, hydrant count/outlets if known. Survey open → `[V]`. Do not CAD. |
| **Carrier** | **yes** | FM / AXA / UFC / ISO-rating-only / n/a. Dual → matrix rows above. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional: owner fire-flow mandate above code; written AHJ method letter; existing hydrant curve / loop residual (consume — do not rebuild); standpipe concurrent demand flag once sealed (handshake only).

**Do not invent** App B B105 values, ISO FSRS credit/duration tables, UFC App C procedure results, Charlotte 13R 50% credit on an NFPA 13 hall, or 2,000–3,500 gpm “typical” NFF as sealed. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `most-stringent-basis-matrix` | Hose / duration / fire-flow / dual-carrier rows when dual | Rebuild dual-carrier BOD; invent App B gpm |
| `density-area-dry-increase` | `q_spr` / `qd_gpm` / hose / duration when Note (1) binds | Re-run density × area |
| `hydrant-supply-curve` | Receive NFF as a **separate** demonstration demand if AHJ requires it alongside BOR `qd` proof | Rebuild `P(Q)`; invent flow test; treat Q20 as NFF |
| `campus-looped-main-sizing` | Emit NFF / concurrent flow once method + sealed number held | Resize loop from invented NFF placeholders |
| `pump-envelope` | Emit whether NFF (vs `qd`) drives pump envelope once sealed | Freeze nameplate; invent NFF into rated flow |
| `standpipe-class-i-election-and-demand` | May consume sealed NFF for concurrent campus — **handshake only** | Rebuild standpipe whether/type/gpm |
| Future / tank Skills | Duration × flow → storage volume once duration held | Invent duration gallons here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If packet, STS, dual-carrier rows (when required), AHJ adoption pin, or governing `qd` (when Note (1) binds) are missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

**Outbound this draft.** Do **not** restamp peers in this write.

| Peer | They own | This Skill owns |
|---|---|---|
| the input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `suppression-technology-selection` | Family election wet\|dry\|DI + fence status | **Consume** STS; mist = `PRACTICE REFUSED`; foam prohibited; SI/NI → Stop |
| `most-stringent-basis-matrix` | Per-parameter union / dual-carrier rows | **Consume only** when dual — then elect NFF method package **here** |
| `density-area-dry-increase` | `q_spr` / `qd` / hose / duration gallons | Consume for Note (1) path; do not rebuild |
| `hydrant-supply-curve` | 2-pt `P(Q)` + pump need/no-need; **explicitly fences out NFF/App B** | Own NFF method; emit demonstration-flow need; do not rebuild curve |
| `campus-looped-main-sizing` | Loop diameter / one-leg-out | Emit governing NFF / concurrent Q once sealed; do not invent NFF as loop Q |
| `pump-envelope` | Listed churn/100%/150% screen | Emit whether sealed NFF (vs `qd`) enters envelope; no nameplate |
| `standpipe-class-i-election-and-demand` | Standpipe whether/type/demand register | Handshake only for concurrent campus once both sealed |
| Future / tank Skills | Usable storage / duration volume | Structure duration register; **handoff** — never invent gallons |
| Clean-agent Skills | Clean-agent concentration / enclosure | **Hand-away only** |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency.

Example lines:

- `HAND OFF — the input packet: optional. Missing → proceed from given inputs; flag `ASSUMED`.`
- `HAND OFF — suppression-technology-selection: wet|dry|DI election. This Skill consumes; SI/NI → Stop RFI-variance; mist PRACTICE REFUSED; foam prohibited.`
- `HAND OFF — most-stringent-basis-matrix: dual-carrier / hose-duration-fire-flow rows when dual. Consume; return here after.`
- `HAND OFF — density-area-dry-increase: consume governing qd for ISO Note (1) path; do not rebuild density×area.`
- `HAND OFF — hydrant-supply-curve: owns 2-pt P(Q); fences NFF/App B. This Skill owns method; emit demonstration-flow need once sealed.`
- `HAND OFF — campus-looped-main-sizing: governing NFF / concurrent Q once sealed; do not invent NFF placeholders.`
- `HAND OFF — pump-envelope: whether sealed NFF enters pump envelope vs qd; no nameplate here.`
- HAND OFF — standpipe-class-i-election-and-demand: concurrent campus handshake only once both demands sealed.`
- `HAND OFF — tank / duration storage Skills: duration × flow → usable volume once duration primary held; never invent gallons here.`
- `HAND OFF — clean-agent: hand-away only; company does not design clean agent.`

---

## 3. Steps

### 3.0 Hard scope + status register first (Method item 0)

Before method election / NFF / hydrant-credit / duration arithmetic:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`. Clean-agent as company BOD → **Stop** / hand-away only.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / packet·STS·matrix / method / Note (1) path / App B / NFF-vs-`qd` / hydrant-credit / duration / purveyor / legacy reject / Δ (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.
4. **NO PLACEHOLDER.** anywhere in the run.
5. Restate refuse-invent: **no invented IFC App B table gpm**; **no invented ISO FSRS credit/duration gallons**; **no invented UFC App C results**; Charlotte / Raleigh / SCO / FEMA secondary floors are **pins or reported values**, not silent national defaults.

### 3.1 Pin editions (cite section AND edition)

| Instrument | Role | Shop pin / honesty |
|---|---|---|
| **ISO / Verisk Guide for Determination of Needed Fire Flow** | Rating NFF; Note (1) sprinklered path | **EDITION 06-2014** held. Note (1) p. 2; formula pp. 1, 3; C caps p. 10; O p. 11; X+P p. 16; rounding/caps p. 26. **Rating only — no permit force.** |
| **Adopted IFC / state fire code + Appendix B** | Code fire-flow *quantity* where adopted | **Parameterize AHJ edition + adoption Y/N.** Licensed **IFC-2024 App B tables unheld** → structure + stated `ASSUMED` value + `[V]` + RFI (not a Stop; never presented as the cited table value). FEMA/USFA 2009 reports IFC 2006/2009 75 % reduction / **1,500 gpm / 2 h** floor — secondary `[V]`. |
| **UFC 3-600-01 §9-2 / Appendix C** | Federal fire-flow procedure | §9-2 pointer held in secondary; **Appendix C NOT in corpus** → stated `ASSUMED` + `[V]` + re-mine / RFI for DoD NFF (not a Stop; not a sealed value). Scope word: often **unsprinklered**. |
| **Purveyor / utility policy** | Contractual max-available / demonstrate-to | Project-issued; often inverse of NFF. |
| **NFPA 13-2025** | Sprinkler demand / hose / duration interface | Delta baseline where Note (1) equates NFF to demand + hose. Enforced ≠ latest. |
| **FM DS 5-32 / DS 8-9 / DS 3-0** | Property-carrier demand that becomes Note (1) NFF; supply analysis | Consume density-area / hydrant peers — do not rebuild. DS 5-32 **January 2026** hose/duration when so consumed. |
| **Charlotte CFD Plan Review Guidelines** | Local ISO NFF / 13R overlay | a note 2026-09-17; body cites **NCIFC 2018**. **Local only.** |
| **Raleigh RFD General Information (2023)** | Local App B **or** ISO permit gate §6.17 | **Local only** — contrast Charlotte (no 13R 50% pin). |
| **NC SCO Water Based FP Guidelines (2020)** | State-property hydrant coverage §L.4 | **State-property AHJ only** — do not merge with municipal. |
| **Gwinnett Co. GA Code Ch.42 (2012 capture)** §42-29 | Hydrant capability floors | **Local only.** Multifamily hydrants ≥ 1,000 gpm @ 20 psi; commercial off-roadway hydrants ≥ 1,250 gpm; verify per NFPA 291. Not an NFF equation. |
| **Des Moines FD Site Plans class (2024-03-13)** | IFC App B pointer | **Local only.** Tables B105.1(1)/(2), B105.2 reduction, then **B105.3 greater-of** (sprinkler + hose vs fire flow). Table values not reprinted → pull adopted App B. |
| **one city FD EPM Fire Flow policy (PFC 2024)** | PFC App B @ 20 psi | **Local only.** Private on-site hydrants may be modeled at **1,000 gpm per hydrant** for App C demonstration — not a sprinkler-density substitute. |
| **OCFA Guideline B-01 (eff. 2026-01-01; 2025 CFC/CBC)** Att.3 / Att.4 / §5.1–5.2 | Municipal fire flow + duration @ 20 psi | **Local only.** §5.1.3: 50 % sprinkler reduction in **flow, not duration**; Att.4 S column often **floors at 1,500 gpm** (≠ blind 50 % of NS) → **use the Att.4 cell**, flag both. Fire-flow area per CFC App B B104 (IA/IB → three largest successive floors). |
| **FEMA/USFA EFOP 2009** | Side-by-side method comparison | Secondary throughout; every cited edition superseded. |

**Do not cite Charlotte 13R 50% credit, Raleigh §6.17, or NC SCO 400/600 ft as universal.** Ask per jurisdiction.

### 3.2 Parameters, separately (three-layer union)

| Parameter | Code floor (L1) | Insurer / rating (L2) | Owner (L3) | Method action |
|---|---|---|---|---|
| **A. Method election** | Adopted App B Y/N; UFC if federal; else AHJ practice | ISO NFF = rating; property carrier via Note (1) demand | May name a method or raise flow | Step 0 first — name the binding instrument |
| **B. Sprinklered NFF definition** | NFPA 13 demand + hose (interface) | ISO Note (1) = BOR demand + hose; FM/AXA raise density → raise NFF | May raise | Consume governing `qd`; do not run `18F√A` |
| **C. Unsprinklered bound** | — | ISO `C·O·[1+(X+P)]` with caps | Rarely | Show-and-verify bound only; not design NFF for sprinklered DC |
| **D. App B floor** | Table + sprinkler reduction where adopted `[V]` | — | May raise | Structure; tables unheld → `ASSUMED` + `[V]`; compare to `qd` |
| **E. Hydrant credit geometry** | AHJ spacing / coverage | ISO/FSRS distance-outlet caps `[V]` (FEMA paraphrase) | Site standards | Handshake flags; not CAD; Stop inventing credit gallons |
| **F. Duration / storage** | App B duration where adopted `[V]`; NFPA 13 occupancy duration `[V]` | FM DC **60 min** when consumed; ISO commercial duration **unheld** (FSRS) | May add tank minutes | Structure register; **never invent gallons**; handoff tank Skills |
| **G. Concurrent campus** | AHJ multi-fire increase (reported up to 2× — `[V]`) | Largest BOR demand + hose/standpipe once sealed | Phasing / N+1 | Register largest-of; handshake standpipe/loop/pump |
| **H. Purveyor max-available** | — | — | Contract | Capture inverse question; design-to when it binds |

Most-stringent wins **per row**. Name the controlling layer. Owner may raise, never lower.

### 3.3 Step 0 — Which method binds (load-bearing)

Sort the asker first. Fire flow does **not** sit cleanly in a single layer:

| Asker | Instrument | Force | What it wants |
|---|---|---|---|
| Fire marshal / AHJ | **IFC Appendix B** *(only if specifically adopted)* | Code — on adoption only | Table by area + construction; sprinkler reduction |
| Water purveyor | Own hydraulic model / max-available policy | Contractual / service | Often *here is the maximum we can deliver; design to it* |
| ISO / Verisk (PPC) | FSRS **Needed Fire Flow** | **None on your permit** — community rating | NFF at selected properties; need/availability ratio |
| Property insurer (FM / AXA / Zurich) | Sheet demand + hose → Note (1) | Real design basis for a DC | See density-area + supply curve |
| Federal (DoD) | UFC 3-600-01 §9-2 / **Appendix C** | Federal projects | Procedure for (often) **unsprinklered** facilities — App C unheld |
| Owner standard | Hyperscaler spec | Can raise any of the above | Parameterize |

**Method actions:**

1. Record AHJ fire-code **edition** + **Appendix B (or state equivalent) adoption Y/N** from packet / ordinance / written AHJ letter. Unknown → **not a Stop**: carry adoption as a stated `ASSUMED` (which, and why — prefer the more stringent result), flagged + RFI; never present App B as adopted code without the ordinance.
2. Record purveyor policy (max-available / demonstrate-NFF / both).
3. Record whether the job is federal UFC, municipal, or owner-self-supplied campus.
4. Name the **binding instrument(s)** for this run. ISO alone never seals a permit number.
5. Local overlay examples (**not defaults**): Charlotte CFD → ISO NFF language for non-sprinkled / 13D / 13R (+ 13R 50% credit) — hyperscale halls are typically **NFPA 13**, so Note (1) / hydraulic path applies; **do not apply 13R 50% credit to a 13 OH/EH hall**. Raleigh RFD §6.17 → fire-flow analysis by **NCFPC App B or ISO**, sealed by design professional. NC SCO §L.4 → State-property hydrant coverage bands — separate instrument. Gwinnett §42-29 → hydrant gpm floors (1,000 @ 20 psi / 1,250). Des Moines → App B + B105.3 greater-of. one city → PFC App B @ 20 psi with 1,000 gpm/hydrant private modeling credit. OCFA B-01 → Att.4 cell @ 20 psi (50 % reduction applies to flow, not duration; S column floors at 1,500 gpm). **Each stays inside its own fence.**

### 3.4 Step — Sprinklered path (ISO Note (1) — almost always for a DC)

ISO Guide **EDITION 06-2014 p. 2** Note (1), load-bearing: for commercial occupancies sprinklered per the general criteria of NFPA 13, NFF **is the demand at the base of the automatic sprinkler riser and inside/outside hose stream demand.** FEMA/USFA 2009 corroborates independently (pp. 14, 26).

**Method actions:**

1. Confirm building(s) are NFPA 13–criteria sprinklered (company wet|dry|DI). If not → §3.5 unsprinklered bound / App B / UFC path.
2. Consume governing `qd_gpm` = `q_spr + hose` from `density-area-dry-increase` (and matrix pins). Label **density-method minimum**.
3. **Campus rule:** NFF under Note (1) = **largest sprinkler demand on the site**, not necessarily the white-space hall — staging / receiving / decant / spare-parts (FM DS 8-9 territory) often governs. Say so in DD before civil sizes the service.
4. Do **not** run `18F√A` for the sprinklered design NFF. Optional unsprinklered bound may still be carried as §3.5 sanity case.
5. Print Δ vs NFPA 13-2025: under Note (1), NFF *is* the 13 demand + hose; FM/owner density raises both demand and the fire flow the campus must demonstrate.

Canonical consumed white-space minima when so produced upstream (illustration — **not** invented here): wet ≈ **750 gpm**, dry/DI ≈ **950 gpm** (FM DS 5-32 Jan-2026 hose 250 gpm context). Always prefer the consumed packet numbers.

### 3.5 Step — Unsprinklered ISO bound (sanity / bounding case only)

**NFF = C · O · [1.0 + (X + P)]**, with **C = 18F√A** rounded to nearest 250 gpm (ISO 06-2014 pp. 1, 3).

Held collapses for a typical hyperscale DC envelope:

- **X + P = 0** for sprinklered buildings, Class 5/6, and Class 3/4 with C-1/C-2 contents (p. 16) — a sprinklered DC satisfies these; use the bound only when the unsprinklered path is actually in play or as a civil day-one ceiling.
- **C capped** at **6,000 gpm** for Construction Classes 3–6 and for 1-story any class (p. 10). Cap onset ≈ **166,453 ft²** (Class 3/4) / **295,916 ft²** (Class 5/6) — matches ISO App. A.
- **O** live lever (p. 11): C-2 **0.85** is the defensible DC analogue class; C-1 generally not defensible; staging/decant area % can move the whole building (10% / 20% / 25% thresholds — cite p. 12–13).
- Rounding (p. 26): nearest 250 if < 2,500; nearest 500 if > 2,500. Stated max 12,000 / min 500 — arithmetic product of sub-caps; DC at C-2 caps far lower.

**Show-and-verify (Class 3/4, O = 0.85, X+P = 0, above cap):**

```
C = 6,000 gpm (capped)
NFF = 6,000 × 0.85 × 1.0 = 5,100 → round per p. 26 → 5,000 gpm
```

Held corpus bound: unsprinklered ISO NFF for a hyperscale DC ≈ **4,500–5,000 gpm**, **≤ 5,000 gpm at C-2 any footprint**. Status: `grounded` method arithmetic on held guide; occupancy-class mapping remains an **analogy argument** (no “data center” row in ISO lists) — state the analogy on the memo.

**Firewall / division-wall note:** ISO area-reduction is **inert above the C cap** at hyperscale. IFC App B may behave **oppositely** (firewall with no openings as area-reduction lever — FEMA p. 16) — another reason Step 0 comes first. Do not advise buying a wall for ISO NFF reduction without knowing which method binds.

### 3.6 Step — IFC Appendix B path (structure only — refuse invent)

1. Confirm **adoption**. If not adopted → record and skip table path (purveyor + AHJ practice + Note (1) remain).
2. If adopted: structure the register — fire-flow calculation area; construction type; table lookup; sprinkler reduction; floor comparison to Note (1) `qd`.
3. **Reported secondary floor (not sealed):** up to **75 %** reduction; reduced flow **not less than 1,500 gpm for ≥ 2 hours** (FEMA/USFA 2009 pp. 16–17 citing IFC 2006/2009). Status: `provisional` / `[V]` until licensed **IFC-2024** (or AHJ-enforced edition) Table B105 / B105.1 (or state equivalent) is opened.
4. If App B gpm is needed and primary remains unheld → **not a Stop**: stated `ASSUMED` value (value + why) + `[V]` + RFI; never presented as the cited table value (the engineer of record confirms). Optional screening flows only as `[SYN]` and never as sealed demand.
5. AHJ may increase where multiple/large fires possible (reported up to **2×** — FEMA p. 17) — flag `[V]`; do not invent the multiplier.

**Governing rule when both exist:** compare sealed App B result (once held) to Note (1) `qd`; **most stringent per the AHJ's written rule** — often the **floor governs** when wet-hall `qd` < floor.

### 3.7 Step — UFC / federal path

- Point to **UFC 3-600-01 §9-2** and **Appendix C** (unsprinklered procedure per CED/Guyer restatement). **Appendix C text unheld** → stated `ASSUMED` + `[V]` + re-mine / RFI for federal NFF (not a Stop).
- Factor list worth anticipating even without App C (response time, access, separation, stories, construction, area, occupancy) — rural/volunteer sites may hear this logic from a marshal even without a UFC cite.
- POL / bulk-fuel **exposure-cooling** tables in secondary federal restatement (240 min duration) are **planning-order only** [not code; owner/insurer only]: NFPA 30-2024 has no exposure-cooling rule, and §22.8.1 requires NFPA 11/15 protection only for a ≥50,000 gal vertical atmospheric Class I fixed-roof tank with unusual exposure, so not diesel (pull 30-02). NFPA 30-2024 §1.1.2(9) excludes liquids in the fuel tanks of stationary engines (pull 30-03); bulk POL storage is not covered by that exclusion. Verify UFC 3-460-01 before design basis; may govern **stored volume** not pump flow. Hand off storage to tank Skills; do not seal from secondary tables.

### 3.8 Step — Distinguish NFF from sprinkler `qd` at BOR

| Quantity | Meaning | Owner Skill |
|---|---|---|
| **`qd` at BOR** | Sprinkler + hose demand for supply-vs-demand proof | `density-area-dry-increase` → `hydrant-supply-curve` |
| **NFF / required fire flow** | AHJ / purveyor / rating fire-flow demonstration number | **This Skill** elects method; number from Note (1) `qd`, sealed App B, UFC, or purveyor |
| **Q20 hydrant rating** | NFPA 291 residual-at-20-psi rating | Not NFF; not `qd` — never substitute |

Under ISO Note (1) they **coincide numerically** with governing `qd`. Under App B floor or purveyor policy they may **diverge** — print both and name which governs loop / tank / pump envelopes.

`hydrant-supply-curve` proves municipal supply vs **`qd`**. It does **not** elect NFF method. If AHJ requires a separate fire-flow demonstration, emit a handoff: same curve may be read at NFF, but method ownership stays here.

### 3.9 Step — Hydrant credit / overlapping coverage (handshake, not CAD)

Emit flags for civil / site coordination — **do not place CAD**:

- Credit measured **along approved hose-lay route**, not crow-flies (FEMA/USFA 2009 p. 19 paraphrase of ISO).
- Reported bands (secondary / `[V]` vs current FSRS — **06-2014 guide does not contain the hydrant-distance table**): **> 1,000 ft → 0 credit**; within **~300 ft** or with **pumper outlet → max 1,000 gpm** per hydrant; ISO takes **lower of distance limit and outlet limit**.
- Implication: a 5,000 gpm unsprinklered-bound NFF wants **≥ five creditable hydrants** inside the hose-lay envelope — often binds before pipe size on deep-setback campuses.
- Local spacing overlays (examples only): Charlotte NCIFC 2018 §507.5.1 non-sprinkled **400 ft** / sprinkled **600 ft**; NC SCO §L.4 **400 / 600 ft** + **150 ft** apparatus access — **do not merge** municipal vs State-property instruments.
- Yard hydrant product flags (consume private-main note): dry-barrel campus hydrants; steamer/pumper on yard hydrants often refused by carrier yard rules — pin project standard, do not invent.
- Overlapping coverage: structure the question (which hydrants credit which building / fire area) — hand geometry detail to campus-loop / civil; this Skill only flags the **credit envelope**.

**Never silently invent FSRS credit gallons.** If credit proof is needed and FSRS unheld → stated `ASSUMED` (value + why) + `[V]` + RFI, not a Stop.

### 3.10 Step — Duration / concurrent campus demands (structure; `ASSUMED` + `[V]` if unheld)

| Row | Honesty |
|---|---|
| ISO commercial NFF duration | **Not in Guide 06-2014 held**; lives in **FSRS** — unheld → `[V]` / RFI. FEMA reports 2–4 h secondhand — do **not** size tanks on that alone. |
| IFC App B duration | Tied to table / floor where adopted — `[V]` until primary opened (reported 2 h at 1,500 gpm floor). |
| FM DC sprinkler duration | **60 min** when consumed from DS 5-32 / density-area — this is **supply duration for `qd`**, not automatically ISO commercial NFF duration. |
| Concurrent | Largest hall + hose + sealed standpipe (if any) + App B floor honesty + future phases — register structure; handshake standpipe / loop / pump. |
| Self-supplied campus | Tanks + pumps may answer “availability,” but AHJ still asks fire-flow / hydrant credit — do not claim NFF question vanishes. |

**Duration × flow = tank volume.** If storage volume is needed and duration primary unheld → stated `ASSUMED` duration (value + why), flagged, + handoff to future tank Skills with open RFI — **never silently invent gallons**.

### 3.11 Step — Reject legacy methods with arithmetic

| Method | At ~250,000 ft² × 40 ft hall | Verdict |
|---|---|---|
| **ISU / Iowa State** `FF = V ÷ 100` | ~**100,000 gpm** | Absurd — ignores construction & sprinklers |
| **NFA fireground** `(A ÷ 3) × F` | ~**83,000 gpm** | Fireground estimator — never design |
| **IITRI non-residential** quadratic | **Negative** beyond ~32,300 ft² (vertex ~16,154 ft² / peak ~3,392 gpm) | Domain-invalid at DC scale |

If an AHJ proposes one, return the one-line arithmetic politely and offer Note (1) / adopted App B / purveyor path instead. Status: `comparison-only` / rejected.

### 3.12 Step — Δ layers + honesty close

Always print:

- Binding instrument(s) from Step 0.
- NFF (or register structure) vs consumed `qd` — which governs loop / tank / pump.
- Δ vs **NFPA 13-2025** on hose / duration / demand interface.
- Δ vs adopted IFC App B once tables held; list unheld section pins explicitly.
- Controlling layer per parameter (A–H).
- `[SYN]` screening flows (if any) vs sealed numbers (if any).
- Open RFIs (adoption Y/N, App B tables, FSRS credit/duration, UFC App C, purveyor letter, local amendments).

---

## 4. Outputs / artifacts

Write **only** to the caller-named path (or return in-response and stop). Typical package:

1. **Status register** (§1.4) + Hard-scope fence result (STS consume; SI/NI/foam/mist posture).
2. **Method-election memo** — Step 0 binding instrument(s) · Note (1) vs App B vs UFC vs purveyor · NFF-vs-`qd` · hydrant-credit flags · duration/concurrent structure · legacy reject.
3. **NFF / hydrant-credit geometry register** — structure + held/unheld pins; **no invented App B / FSRS / UFC table gpm**; screening labeled `[SYN]` if used.
4. **Show-and-verify** — Note (1) consume path and/or unsprinklered cap arithmetic when carried.
5. **Open RFIs** — each with blocking/non-blocking tag.
6. **Reciprocal HAND OFF lines** to live peers (incl. future tank / duration storage).
7. **Δ vs NFPA 13-2025** (interface) + `[SYN]`/`[V]` register.

Do **not** emit: hall density×area transcript, hydrant `P(Q)` rebuild, pump nameplate, campus loop resize, CAD coordinates, prior job files retrieval, foam/mist/clean-agent BOD, invented App B/ISO tables, or KB writes.

---

## 5. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

1. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`. Clean-agent as company BOD → Stop / hand-away only.
2. Missing the input packet → not a Stop (packet optional). Missing STS → `ASSUMED` (flagged), not a Stop. Missing matrix rows when dual → assume most-stringent row (`ASSUMED`, flagged) or hand off, then return.
3. Appendix B adoption unknown → **not a Stop**: carry adoption as `ASSUMED` (state which, and why — prefer the more stringent result), flagged + RFI.
4. Sealed App B / ISO FSRS credit / commercial duration / UFC App C result needed but primary unheld → stated `ASSUMED` + `[V]` + RFI, not a Stop — **never silently invent or present as cited**.
5. Note (1) path binds but governing `qd` / density-area result missing → run `density-area-dry-increase` or carry a stated `ASSUMED` `qd` (flagged); not a Stop.
6. Charlotte 13R 50% credit (or other foreign local overlay) applied to NFPA 13 OH/EH hall or imported as universal → Stop / refuse import.
7. ISU / IITRI / NFA proposed as sealed design NFF without rejection arithmetic → Stop / reject with show-and-verify.
8. Caller wants hydrant `P(Q)`, pump nameplate, loop diameter, tank gallons from invented duration, or CAD as this Skill’s deliverable → wrong Skill / handoff.
9. KB / worked examples / ARCHIVE writes; prior job files retrieve.

---

## 6. Citations (section AND edition)

| Claim | Pin | Status |
|---|---|---|
| Sprinklered commercial NFF = BOR demand + hose | ISO Guide **EDITION 06-2014** Note (1) **p. 2** | `grounded` |
| NFF = C·O·[1+(X+P)]; C = 18F√A | ISO 06-2014 pp. **1, 3** | `grounded` |
| C caps 6,000 (Class 3–6 / 1-story); O factors; X+P = 0 sprinklered | ISO pp. **10, 11, 16** | `grounded` |
| Rounding / max 12,000 / min 500 | ISO p. **26** | `grounded` |
| C-cap onset areas match App. A | ISO App. A p. **30** + corpus recompute | `grounded` method |
| Appendices not code unless adopted | FEMA/USFA EFOP **2009** p. **16** | `grounded` rule; secondary paper |
| App B 75% / 1,500 gpm / 2 h floor | FEMA/USFA 2009 pp. **16–17** citing IFC **2006/2009** | `[V]` vs IFC-2024 primary |
| Hydrant credit distance / 1,000 gpm | FEMA/USFA 2009 p. **19** (ISO 2008 paraphrase) | `[V]` vs current FSRS; not in Guide 06-2014 |
| Reject ISU / IITRI / NFA at DC scale | FEMA/USFA 2009 pp. **11–12, 25, 30–32** + corpus closed form | `grounded` rejection arithmetic |
| Charlotte ISO NFF / 13R 50% credit | Charlotte CFD Plan Review Guidelines (capture **2026-09-17**); NCIFC **2018** cites | **Local only** |
| Raleigh App B or ISO permit gate | Raleigh RFD General Information **2023** §**6.17** | **Local only** |
| NC SCO hydrant coverage | NC SCO Water Based FP Guidelines **2020** §**L.4** | State-property only |
| Gwinnett hydrant floors | Gwinnett Co. GA Code Ch.42 §**42-29** (2012 capture; ) | Local only |
| Des Moines App B pointer | DMFD *Site Plans — Fire Code Requirements* class **2024-03-13** pp.56–60 | Local only |
| one city App B @ 20 psi | one city FD EPM Fire Flow policy, **PFC 2024** | Local only |
| OCFA Att.4 / 50 % flow reduction | OCFA Guideline **B-01 (2026-01-01)** §5.1.3, Att.3 p.28, Att.4 p.29 | Local only |
| UFC fire-flow procedure location | UFC **3-600-01** §**9-2** / **Appendix C** (App C unheld) | Pointer `grounded`; procedure `[V]` |
| FM hose / duration when consumed | FM DS **5-32 January 2026** §2.4.1.5 / §2.4.1.6 | Via density-area consume |
| Residual floor 20 psi (available flow context) | FEMA/USFA 2009 pp. **19–20**; FM DS 3-0 practice | Supply-curve peer |

**Absent / `[V]` (refuse invent):** licensed **IFC-2024 Appendix B** tables and floor text; **ISO FSRS** hydrant-credit and commercial-duration tables; **UFC 3-600-01 Appendix C** procedure text; model IFC §507 quantity pins beyond secondary report.

---

## 7. Design practice

1. **Hard-scope + status first.** Company fence = wet | dry | DI only (consume STS — do not elect). SI/NI → Stop + `RFI-variance`. Foam prohibited. Mist = `PRACTICE REFUSED`. Clean agent = hand-away only. Status every run. Packet optional; STS (+ matrix when dual) consumed when present, else `ASSUMED` (flagged). **NO PLACEHOLDER.** **Never silently invent App B / ISO FSRS / UFC App C table values — a stated ASSUMED value is labeled, never presented as cited.**
2. Three-layer most-stringent **per parameter** (method, Note (1) NFF, unsprinklered bound, App B floor, hydrant credit, duration/concurrent, purveyor).
3. **Step 0 before arithmetic.** Which instrument binds — code adoption, purveyor, rating, federal, owner.
4. Sprinklered DC → Note (1) → consume governing `qd`; fire flow is an output of FP design. Check App B floor before assuming calc governs.
5. Cite section **and** edition; enforced ≠ latest; local AHJ pins stay local (Charlotte ≠ Raleigh ≠ SCO ≠ universal).
6. Show-and-verify Note (1) consume path and unsprinklered cap arithmetic; flag `[SYN]` / `[V]`; tables needed but primary unheld → `ASSUMED` + `[V]` + RFI, not a Stop.
7. Distinguish NFF from BOR `qd` from Q20. Hydrant Skill owns `P(Q)` and fences NFF out — respect the fence.
8. Hand duration-storage, loop Q, pump envelope, and standpipe concurrent to peers — do not absorb their scope.

If notes conflict, **most-stringent wins** and both sources stay visible.

---

## 8. Not this Skill

| Work | Where |
|---|---|
| System-family election wet\|dry\|DI; mist/foam fence | `suppression-technology-selection` — **consume**; mist BOD = `PRACTICE REFUSED`; foam prohibited; SI/NI-as-BOD → `RFI-variance` |
| Dual-carrier BOD authorship | `most-stringent-basis-matrix` — consume+return when dual |
| Assignment packet authorship | the input packet — consume only |
| Density×area `qd` / gallons | `density-area-dry-increase` — consume for Note (1) |
| Hydrant 2-pt `P(Q)` / pump need verdict | `hydrant-supply-curve` — peer fences NFF/App B **out** |
| Listed churn / 100% / 150% envelope | `pump-envelope` |
| Campus loop diameter / one-leg-out | `campus-looped-main-sizing` |
| Standpipe whether / Class I / gpm register | `standpipe-class-i-election-and-demand` — concurrent handshake only |
| Tank usable volume from duration | Future / tank Skills — **handoff**; never invent gallons here |
| Clean-agent concentration / enclosure | Clean-agent Skills — **hand-away only** |
| CAD / KB / worked examples / ARCHIVE writes | forbidden |

---
