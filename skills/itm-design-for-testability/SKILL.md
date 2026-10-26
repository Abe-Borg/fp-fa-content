---
name: ITM design for testability
description: >-
  use this when company-scoped wet/dry/double-interlock is elected (packet
  optional; a missing election or input is assumed and flagged ASSUMED), and you must emit a CD-stage ITM
  design-for-testability drawing/spec checklist plus interval-lever schedule
  (nitrogen, enhanced-security valve supervision, test header, ≥4 in. drain,
  BFP path, zoning, alarm isolation; optional gated AGF TESTanDRAIN/RemoteTEST)
  as a 3-layer most-stringent union on INTERVALS and FEATURES separately;
  SI/NI comparison-only, foam prohibited, mist PRACTICE REFUSED as BOD; not
  occupancy, density×area, pump envelope, dual-carrier BOD, or an O&M manual.
---

# ITM design for testability

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe. **This Skill is a CD-stage design-for-testability CHECKLIST**, not a calc dump and not an O&M manual. After an assignment packet exists and the company has elected a permitted system family, it asks: *what must be on the drawings and in the spec so the owner can test and maintain the building for its life without impairing it?* It produces (1) a **physical-features checklist** (test header, ≥4 in. standpipe test drain, impairment-bounded zoning, surge control, BFP full-flow path, lockable alarm-isolation switch, optional gated AGF TESTanDRAIN / RemoteTEST lines) and (2) a **CD-stage interval-lever schedule** (what features change which NFPA 25 / FM / AXA intervals).

**Core thesis:** ITM is a **design input**, not an O&M afterthought. Frequency is a **CD output**. Two specifications made at CD each buy a large, permanent reduction in FM’s own mandated cadence: **nitrogen in the preaction/dry systems takes the full-flow trip test from every 3 years to every 10** (FM DS 2-81 Table 2c item 14; NFPA 25 full-open trip stays every 3 yr [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]), and **FM Approved *enhanced-security* valve supervision takes the control-valve visual inspection from WEEKLY to SEMIANNUALLY — a 26× reduction across every zone valve** (Table 1 items 1a/1c). Neither can be bought later. Per-parameter most-stringent is the cleanest demonstration in the shop codebook (control-valve ladder **52×**). **Both levers exist only when FM grants them on a company-elected wet / dry / double-interlock BOD** — never on SI-as-BOD, and never on a code-direct NFPA 25 job without naming the granting layer.

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard), **most-stringent union PER PARAMETER**, applied **separately to INTERVALS and to FEATURES**. Delta vs **NFPA 25** (ITM code floor) **and** vs **NFPA 13-2025** (sprinkler-install delta where the ITM regime reaches back into design). Cite **section AND edition**. Show-and-verify math where any arithmetic exists. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.

**Honesty.** This is a checklist recipe, not a full ITM-led design project. Worked examples exist for the checklist and for an inspector's-test valve set. Look them up by title. Do not invent filesystem paths as required inputs. There is still no full ITM-led design set (no complete hall program, pump rating, and jurisdiction delivered together). Implement the checklist. Copy the method. Do not copy geometry or SKUs as defaults.

Write the checklist + lever schedule **only** to the path the **caller** names. Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may emit a **controlling** CD ITM design-for-testability checklist only against an elected company system family:

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

**This Skill does not elect families.** It handshakes with `suppression-technology-selection` and `most-stringent-basis-matrix` (and consumes their elected result when density / hydrant / pump Skills already closed upstream). Consume elected `wet` | `dry` | `double-interlock`.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** mix this checklist is written for:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling ITM checklist + lever schedule as if SI/NI were company-elected.
6. Do **not** promise FM nitrogen **3→10** or enhanced-security **weekly→semiannual** levers on an SI-as-BOD path.

SI/NI may appear in a **comparison / delta** column only (e.g., “if SI were allowed, ITM rows would still union FEATURES/INTERVALS, but company fence refuses SI as BOD”). Comparison rows are never the controlling checklist.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Emit CD ITM checklist + interval levers |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; do not control the checklist |
| Foam / foam-water | **Prohibited** | Stop; do not design a foam BOD ITM package |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent | Handoff-only | Not this Skill (door-fan capture list only if already present) |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |

**Foam is prohibited for company scope.** **Mist is `PRACTICE REFUSED`.** Do **not** write a foam or mist BOD ITM checklist here. FM flowchart branches that mention mist do not authorize design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| CD drawing/spec **features** checklist (testability hardware) | Occupancy / HC / OH classification |
| CD **interval-lever** schedule (N₂, enhanced-security, tank alarm, …) | System-family election |
| 3-layer union **separately** on INTERVALS and FEATURES | Density × area `calcs/fp` |
| Show-and-verify + `[SYN]`/`[V]`/status register | Dual-carrier BOD rebuild |
| Consume elected wet/dry/DI + assignment packet | Pump rated nameplate / envelope screen |
| Optional gated AGF TESTanDRAIN / RemoteTEST DRAW/SPEC | Node-by-node hydraulic tree / SprinkFDT |
| Acceptance-baseline capture list (names points; does not run IST) | Full O&M manual / NFPA 25 task calendar |
| | prior job files retrieve; inventing a campus |

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent a system mix, a controlling carrier, a pump rating, an IST baseline, or a campus geometry. Do **not** treat `wet/SI/DI` as a company mix — SI is comparison-only.

| Input | Required | Rule |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve prior job files. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type`** | **yes** (inherited) | Must be `wet` | `dry` | `double-interlock` from STS / matrix (or closed upstream that already consumed those). SI/NI as BOD → **Stop** (§1.1). Status `unresolved` on the election → `ASSUMED` company family (wet | dry | DI only, with why), flagged — not a Stop. |
| **System mix per hall / zone** | **yes** | Per hall / zone: `wet` / `dry` / `double-interlock` **only**. Missing mix → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI may appear only as a comparison column. |
| **Nitrogen from day one** | **yes** (per dry/DI hall) | `y` / `n`. FM’s 3→10 yr lever exists **only** for systems *originally installed with nitrogen* **and** only when FM grants on company-elected dry/DI. A later O&M conversion does not buy it. |
| **Carrier** | **yes** | `FM DS 2-81 controlling` **or** `AXA XL PRC.12.0.2 overlay` (plus explicit `n/a` for the other). Unpinned carrier → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Dual-carrier: **consume controlling ITM rows** from most-stringent-basis-matrix if present; still union INTERVALS and FEATURES separately here. Do not rebuild the dual-carrier BOD. |
| **Completed `most-stringent-basis-matrix` ITM rows** | **yes** when dual-carrier (or closed pins inherited) | Consume ITM / valve-supervision / impairment-related rows, provisional/`[V]` flags, company wet/dry/DI fence. Dual-carrier with **unresolved** controlling ITM rows → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged). |
| **Pump count / rating + test-water discharge path** | **yes** if pumps exist | Rated gpm per pump, driver mix, and a named discharge/stormwater path (or explicit `path TBD [V]`). Needed to size test-header **outlets** at 175% of rated. Do not size the pump. |
| **Standpipe class** | **yes** | Class I / II / III / none. Drives the ≥4 in. test-drain item. `none` → mark the drain item N/A and say why. |
| **BFP on lead-in** | **yes** | `y` / `n` (RPZ / DCDA / other named). `y` → permanent full-flow test path is a drawing decision. |
| **Valve-supervision spec** | **yes** | `ordinary` (tamper / locked / sealed) vs **`FM Approved enhanced-security`** (FM Approval Standard **3135**). This is a CD hardware line, not an O&M preference. Lever only when FM grants on company-elected wet/dry/DI. |
| **Climate (freeze)** | **yes** | Freezing y/n; winter design if known. Attaches hydrant cadence, valve-enclosure heat (≥40 °F), and “no heat-tape substitute.” |
| **Seismic (brace-inspection cadence)** | **yes** | SDC / seismic y/n, or `undetermined [V]`. Attaches AXA brace spot-check + after-event inspection, and FM tank-freeboard flag. Do not size braces (other note). |
| **Acceptance-record / IST baseline status** | **yes** | `specified` / `unspecified` / `IST complete with named points`. FM ITM is **differential** — an unrecorded IST permanently destroys the lifetime baseline. |
| **Caller output path** | **yes** for file output | If unnamed, return the checklist in the response and stop — do not pick a corpus location. Typical CD home (not a worked example): section **`11_qa-coordination`**. |

Optional (do not invent; flag `[V]` / `handoff`): owner CMMS / vendor-qualification posture (structure only if NDA); tank presence + cathodic-protection y/n; concealed-head use; containment / hot-aisle geometry; **AGF TESTanDRAIN / RemoteTEST gate** (caller asks for product-layer DRAW/SPEC — see Step 3.8).

**Do not invent** a system mix, a controlling carrier, a pump rating, an IST baseline, AGF SKUs, or a campus. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI; comparison-only / prohibited status | Elect a system family |
| `most-stringent-basis-matrix` | Controlling ITM rows when dual-carrier; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA swap |
| `pump-envelope` / hydrant / density | Pump count/rating only if already frozen upstream and pumps exist | Re-run envelope, hydrant, or density×area |
| `nitrogen-inerting-and-c-factor-gate` | Day-one N₂ election / C-factor context when dry/DI | Re-derive nitrogen purity or C |
| `commissioning-ist-acceptance-packet` | IST / baseline capture companion when present | Run acceptance tests here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

### 2.2 Look up by title (not required filesystem paths)

*Design practice*; *ITM basis and design for testability*; *Acceptance, commissioning and integrated systems testing*; *Fire protection impairment management*; *Valve type selection, listing and supervision basis*; *Hot-work management during campus construction*; *Nitrogen inerting and internal corrosion control*; *Enforced-vs-latest edition resolver and reference pins*; worked examples outline **a worked example**; a worked inspector's-test set **a worked example** (+ four worked packages under that title); AGF brochure source title *AGF Manufacturing TESTanDRAIN System Test Valves Brochure BR-TND_V004 (2023)*.

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest) — ITM floor is NFPA 25

Resolve **enforced** vs **latest** before filling any row. Format every citation `instrument-edition §section` (or table/item + page when that is what the sheet uses).

| Standard | Role in this Skill | Shop-pinned editions |
|---|---|---|
| **NFPA 25** | **ITM code floor** (frequencies + methods). Self-described as a *minimum*. | **Latest 2026.** Unamended **2024 I-Codes** typically enforce **NFPA 25-2023**. **Licensed NFPA 25 is still ABSENT from the shop codebook** — every NFPA 25 frequency below is the *insurer source’s characterization*, **`[V]`**, unmeasured as a numeric delta. Surface both editions. **Do not invent a 25-2026 section number.** |
| **NFPA 13-2025** | **Sprinkler-install delta** where ITM reaches back into design (spares, temperature rating, QOD / 60 s ITC sizing). | Delta reference = **13-2025**. Code-floor *citation* stays at the AHJ pin (often **13-2022** on a 2024 cycle). |
| **NFPA 20-2025** | Test-header outlet count / hose vs pump rating; pumps-in-service during tests. | Delta baseline **20-2025**; AHJ pin often **20-2022**. `[V]` sections. |
| **NFPA 14** | Standpipe 5-year flow test that the ≥4 in. drain serves. | `[V]` edition/section. UFGS standpipe acceptance cites **NFPA 14-2024**. |
| **NFPA 72-2025** | Detection / releasing ITM (not NFPA 25). | Pair with **FM DS 5-48** and **FM DS 5-40** (below). Do not invent ASD port lifecycle frequencies. |
| **FM DS 2-81** | **FM ITM basis — self-contained** (Tables 1–10). On an FM-insured campus this *is* the ITM basis; NFPA 25 is only the floor you must also not fall below. | **Codebook controlling: April 2019 / IR October 2021.** Catalog current **IR April 2026** (routing inspect; not copied into the held sheet file) — flag catalog Δ **`[V]`** until a check restamps. Cite codebook tables. Scope fence §1.0: ITM of agent-discharging systems only; **no** design/install/acceptance; **no** stand-alone detection ITM (that is 5-48 / 5-40). **Table 2.9.1.1 item 10:** inspect/test/maintain primary and **ATS** supplying electric fire pumps **per DS 5-20**; §2.9.2.1.2 emergency generators supplying fire pumps **per DS 5-20**. |
| **AXA XL PRC.12.0.2** | **Delta overlay** — amends NFPA 25 clause-by-clause and **does not repeat it**. Must be read *with* NFPA 25. | **2020** (legacy GAP.12.0.2). **Cites no edition for any standard.** Date the *claim*, not a fabricated PRC edition. **Appendix A contradicts its own narrative in ≥3 places — narrative controls; never build a schedule from the summary table.** |
| **AXA XL PRC.1.1.0** | Impairment handling (sectional valves, hidden impairment, restoration-is-a-test). | **2020**. Pair with **FM DS 10-7** (opened). **48-hour notice / “one impairment at a time” remain AXA’s, not FM’s.** |
| **FM DS 10-7** | Fire Protection Impairment Management. | **Opened Apr 2019 / IR Oct 2025** (11 pp). **Remove from Absent.** Cite for impairment-program structure; do **not** attribute AXA’s 48 h / one-at-a-time to FM. |
| **FM DS 3-7** | Test-header geometry / closed-loop prohibition; pump-power *installation*. | *Fire Protection Pumps*, codebook **Apr 2012 / IR Oct 2021**; catalog **IR April 2025** (48 pp). Pump-power arrangement + transfer switches live here. **ATS *testing*** is **DS 5-20**, not DS 5-23. DS 5-23 is facility emergency/standby **generators**. |
| **FM DS 5-20** | Electrical Testing — ATS / emergency-generator ITM target of DS 2-81. | PDF **held** the held sheet file `FMDS0520.pdf` — **Oct 2016 / IR Oct 2025**, **21 pp**. Read the sheet for the pins below — cite the pins below; do not invent beyond them. **No “fire pump” string in 5-20** — path is DS 2-81 Table 2.9.1.1 item 10 / §2.9.2.1.2 → 5-20; installation stays DS 3-7. Pins: **§2.1.3.5** ATS functional every **3–5 yr** (Table **2.1.3.5.1**); **§2.1.3.9** generators — monthly start; diesel ≥**30 min** at ≥**30% nameplate** or mfr min (more severe); auto + ATS functional every **3–5 yr** (§2.1.3.9.2); Table **2.1.3.9.3**. |
| **FM DS 10-4** | Contractor Management — who may hang the Red Tag. | **January 2024** (mined whole, ). §2.2.4.5: only a **responsible employee** (owner / local management) impairs site FP under DS 10-7 Red Tag procedures; a contractor may impair only with all three §2.2.4.5.1 controls live (prior notice of planned impairments · responsible-employee supervision during · confirmation rectified after). §2.2.1.6: the written contractor-management policy **shall** address DS 10-7 impairment procedures. ITM vendors are contractors under this gate (`[inference]`, KB). |
| **State ITM floor (example — Kentucky)** | Fire-side ITM by state regulation. | **815 KAR 10:060 §7(2)** (filed 2023-08-08; effective date `[verify LRC]`): all suppression + FA systems inspected and tested **annually** minimum by a **department-authorized / certified** person; reports on NFPA 25 / NFPA 72 forms; copy to the local fire chief **≤ 10 working days**. Local only — check each state's fire-side ITM rule; do not port. |
| **FM DS 5-48** | Automatic Fire Detection ITM. | **Opened Jan 2011 / IR Apr 2025** (32 pp). **Remove from Absent.** Detection Tables **5–7**. Still do not invent ASD port lifecycle frequencies beyond the sheet. |
| **FM DS 5-40** | Fire Alarm Systems. | **Held Sep 2007** (26 pp). **Edition-stale flag** vs **NFPA 72-2025** — cite with stale warning; do not present 2007 as current FACU ITM without the delta. |
| **FM DS 5-32** | Occupancy overlay that **overrides** DS 2-81’s 60 s ITM default → **≤30 s to the most remote sprinkler**. | **January 2026**. |
| **FM DS 2-1** | Corrosion / internal condition (companion to nitrogen / obstruction story). | **Mined Oct 2016 / IR Jul 2022**. **Remove from Absent.** Do not re-run the nitrogen Skill here. |
| Owner | CMMS, vendor qualification, change-control — may raise, never lower. | **No Tier-A owner ITM standard is in the codebook — still Absent.** Structure only if NDA. |

**⚠ Two overlay traps (honor both):**

1. **AXA XL PRC.12.0.2 cannot be used alone.** It states same duties that it *must be read with a copy of NFPA 25* and that *the provisions of the NFPA document are not repeated*. An agent handed only the overlay has **deltas and a lossy summary table**, not a schedule.
2. **FM DS 2-81 Appendix C** (FM↔NFPA-25 comparison) is **stale on both columns** (FM column labelled **2019**, never re-issued for the Jul/Oct-2021 interim revisions; NFPA column is **NFPA 25-2017**, three cycles behind **25-2026**) and **drifts from its own Table 1**. Use it only to **locate where layers differ**; then cite **Tables 1–10 for FM** and **NFPA 25-2026 for the code**. Never quote Appendix C as either party’s requirement.

**Federal RCM fence (CED/Guyer M03-037, ©2015, UFC-adapted):** use for **mechanisms only** (supervision-buys-interval; corrosion-control-buys-interval; >10%/>20% main-drain ladder; shared-generator most-stringent; third rejection of closed-loop meters). **Never import its intervals** onto a permitted, AHJ-inspected, carrier-insured commercial building. It runs **below the code floor by design** and says so.

---

### 3.2 Confirm carrier posture — FM is self-contained; AXA is a delta

| Posture | What you fill | What you do not do |
|---|---|---|
| **FM DS 2-81 controlling** | FM Tables 1–10 are the ITM basis. NFPA 25 is the floor you must also not fall below. AXA column = overlay-read / `n/a` unless the caller also invoked it. | Do not treat AXA Appendix A as FM. Do not promise the nitrogen **10-year** lever on a non-FM or AHJ-enforced-NFPA-25-direct job — **the NFPA 25 floor is 3 years** (FM’s own Appendix C characterization, `[V]` vs 25-2026). **Name the layer before promising it.** Levers only on company-elected wet/dry/DI. |
| **AXA XL PRC.12.0.2 overlay** | Fill AXA *narrative* deltas (~15 frequencies + method requirements). Code-floor cells stay `[V]` until NFPA 25 is pinned. FM column = `n/a` unless dual. | Do not build the schedule from Appendix A. Do not treat PRC.12.0.2 as a standalone standard. Do not import FM 3→10 / 26× onto an AXA-only job without naming FM as the granting layer. |
| **Dual / matrix already run** | **Consume controlling ITM rows** from most-stringent-basis-matrix. Re-union INTERVALS and FEATURES here if those rows are missing. | Do not rebuild occupancy, density, or pump BOD. Do not silent-swap FM numbers onto an AXA job. |

FM order of preference and occupancy densities are **other Skills**. This Skill takes the company-elected system mix as an input.

---

### 3.3 Three-layer union — INTERVALS and FEATURES separately

**Most stringent is per-parameter, not per-layer.** You cannot rank “FM vs AXA vs NFPA 25” as whole sheets. An insurer can hold **both** the most stringent *and* the second-least stringent row of the same task, depending on what got specified at CD.

Run two unions:

**A. FEATURES (is this on the drawings / in the spec?)**

Union = **any layer that requires the feature**. A physical test path required by one insurer and silent in the code is still drawn. Owner may add features; owner may not delete an insurer-required feature.

**B. INTERVALS (how often?)**

Union = **most frequent applicable interval that the named layer actually grants**, after CD levers are applied. Do not take FM’s *un-levered* weekly and AXA’s monthly and call “weekly” without recording whether enhanced-security supervision was specified. Do not import federal RCM annual.

**Canonical demonstration — control-valve position verification (four-layer ladder, 52× end to end):**

| Layer | Instrument | Frequency | Per year |
|---|---|---|---|
| Insurer (FM) — baseline | FM DS 2-81 Table 1 items 1a/1c (Apr-2019 / Oct-2021) | **Weekly** visual | **52** |
| Insurer (AXA XL) | PRC.12.0.2 (2020) — electrically supervised | **Monthly** | 12 |
| **Code floor** | NFPA 25 — codebook belief, **`[V]`, not in corpus** | Quarterly (source characterization) | 4 |
| Insurer (FM) — **with FM Approved *enhanced-security* supervision** | FM DS 2-81 §9.1 lever / Table 1 item 1c | **Semiannual** | **2** |
| Federal owner (DoD RCM) | UFC / CED-Guyer M03-037 — **FENCE: do not import** | Annual | 1 |

The ordering is **not by layer type**. An **insurer** holds both 52/yr *and* 2/yr depending on the CD spec; a **federal owner** standard sits **below the code floor**. That is *most stringent is per-PARAMETER* demonstrated cleanly. **If an owner’s O&M group cites a federal/military frequency to argue an FM campus is over-inspected: FM’s biggest available discount (semiannual, 2/yr) is still 2× more frequent than federal RCM annual.**

**Show-and-verify — weekly → semiannual (26×):**

```
inspections_per_year_weekly = 52
inspections_per_year_semiannual = 2
reduction = 52 / 2 = 26×
```

Applies to **every zone valve**, because DS 2-81’s glossary states *“A zone valve is also considered a control valve”* (p.50). **Only when FM grants enhanced-security on company-elected wet/dry/DI.**

**⚠ Do not over-read the supervision lever.** Enhanced security relaxes only the **visual** inspection (item 1a→1c). Unchanged: **semiannual tamper-switch test** (item 3) and **annual full-travel exercise** with turns-to-close / turns-to-reopen recorded (item 4). The **monthly physical test** (item 2) is scoped by **valve type**, not by supervision — it names PIV, WPIV, **non-FM Approved IBV**, NRS, curb-box/roadway, and non-indicating butterfly. **Specifying FM Approved indicating butterfly valves is a third, smaller lever** (moves a valve out of the monthly-physical population). That is a pressure-vs-ITM trade (other note: *Valve type selection*); record the election, do not re-calc equivalent length here.

**Second argument for the same spec (do not merge into one claim):** AXA XL PRC.1.1.0 calls the **hidden impairment** *“the most serious type”* — nobody knows, duration unbounded. Supervision is the engineering control. **The 26× relaxation is FM’s; PRC.1.1.0 states no frequency.**

---

### 3.4 Physical design-for-testability checklist (CD drawing / spec lines)

Each item is a **line on a drawing** (or a spec/C&E deliverable). None can be added cheaply later. Mark each `DRAW` / `SPEC` / `C&E` / `N/A (input)` / `[V]`.

#### Core (always run — these are the named engineerable components)

**1. Fire-pump test header + discharge path (hose-stream method)**

Closed-loop recirculation to suction is **rejected by three independent publishers** — settled; do not re-litigate:

- AXA XL PRC.12.0.2 p.8: *avoid the closed-loop test method as it does not evaluate the suction supply*.
- FM DS 3-7 **§2.3.3.6** (p.11): *do not install a flow meter in a closed loop piped back to the pump suction* — a near-shut suction valve would not be detected.
- Federal RCM (CED-Guyer folio 33): recirculation to suction *is not permitted* — a closed loop **heats the water and falsifies the curve**.

FM permits a meter **to a tank or reservoir** (real discharge); it prohibits only the **closed loop back to suction**. Where a federal spec also bars hydrants from pump testing, the intersection is a **dedicated test header**.

**Sizing (show-and-verify against the caller’s rated gpm):**

```
Q_means ≥ 1.50 × Q_rated # FM DS 3-7 §2.3.3.4 — test MEANS
Q_outlets ≥ 1.75 × Q_rated # same section — test OUTLETS, hose valves, drainage path
```

Discharge path absorbs a **rising ramp** through **6 flow points** (churn · 50 · 75 · 100 · 125 · 150%) for **≥1 hour**, started low (opening all hoses at once cavitates). Coordinate receiving surface/basin with civil + stormwater at DD. Confirm 2½ in. outlet count against **NFPA 20** Table 4.28(a) minimums and the pump rating [CODE NFPA 20-2019/2022/2025 Table 4.28(a) (values unchanged); header outside pump room §4.22.1.5; header-line control valve supervised closed §4.18.2, pull 20-14].

**2. Standpipe test drain riser ≥ 4 in. (100 mm)**

AXA XL PRC.12.0.2 p.19, same duties: *Provide new standpipe systems with a drain riser large enough to handle the flow rates required for testing. This would typically be a 250 gpm – 500 gpm (950 L/min – 1900 L/min) flow and would require a 4 in. (100 mm) or larger drain riser.*

Recurring justification: FM DS 2-81 **Table 3 item 8** — standpipe flow test achieving **design flow AND hose-valve pressure every 5 years**. NFPA 25-2026 code floor: 5-yr flow test on automatic standpipes [§6.3.1.1] and 5-yr hydrostatic test on manual and semiautomatic standpipes at 200 psi for 2 h (or 50 psi over max where max >150 psi), a drop of ≤5 psi not a failure [§6.3.2.1, §6.3.2.2.2; CODE NFPA 25-2026, pull 14-02]. Without the drain, the test forces bench-testing valves (impairing 50% of a riser’s connections), using an adjacent standpipe as a drain (impairing a combination riser), or running hose to the exterior. **Not a code requirement — an insurer-driven design choice.** If standpipe class = `none`, mark N/A.

**3. Impairment-bounded zoning (sectional / riser)**

Two independent AXA XL documents converge:

- PRC.1.1.0 p.4: *Using sectional valves where possible, rather than main valves, to reduce the number of shut-off sprinklers to a minimum and to take all possible advantage of multiple water supplies.*
- PRC.12.0.2 p.19: *Test only 50% of the connections on any riser at one time … Impair only one standpipe at a time.*

**Design rule:** the largest area any single ITM activity can impair is **one bounded, agreed unit** (a white-space suppression zone — never a hall, never a building). Looped-main sectional valving must let one supply keep feeding zones not being worked on. Pair with on-site spares so a discovered defect does not extend the impairment.

**Who hangs the tag:** the owner's responsible employee — not the ITM vendor — per **FM DS 10-4 §2.2.4.5 (January 2024)**; a vendor impairs only under the three §2.2.4.5.1 controls. Write that into the O&M / ITM contract.

Duration / program structure: cite **FM DS 10-7 (Apr 2019 / IR Oct 2025)** for impairment-management framework and the **NFPA 25 impairment chapter** [CODE NFPA 25-2026 Ch. 15, §15.5.2 impairment-coordinator procedures, pull 25-07]. **NFPA 25-2026 §15.5.2(4): a system out of service more than 10 h in a 24 h period → the impairment coordinator arranges one of: evacuation of the affected area, an approved fire watch, a temporary water supply, or an approved ignition-source / fuel-limit program** [CODE NFPA 25-2026 §15.5.2(4), pull 25-07]; same text in 2020 and 2023 [CODE NFPA 25-2020/2023 §15.5.2(4), pull 25-09]. Do not invent any other hour cap. **⚠ 48-hour notice and one-at-a-time remain AXA XL’s (PRC.1.1.0); do not attribute them to FM DS 10-7.**

Hot-work coupling (do not ignore): FM DS 10-3 **§2.5.1.1.C** requires hot-work and impairment permits **cross-communicated and co-posted**; **§2.5.2.1.3** forbids an active *or planned* impairment near the hot-work area throughout the **post-work fire watch and fire monitoring** (tail **1–5 hours**). The window to bound is **work + watch + monitor**. PRC.1.1.0: *Schedule only one impairment at a time!* and no hot work during an impairment.

**4. Surge / water-hammer control, because testing happens with the pumps running**

AXA XL states three times (pp.5, 7, 13): fire pumps **remain in full service** during system testing; pumps are **not isolated** from the underground; main drain tests run **with all fire pumps left on**. Isolating the pump defeats the test. **The water-hammer risk operations would manage by isolating the pump must be handled in design:** controlled valve-closure rates, restrained/thrust-blocked underground, pressure-relief where NFPA 20 requires it, hydrant/drain procedures specifying **slow closure**. Fully **open** dry-barrel hydrants when testing (throttling leaves the base drain partly open and can undermine the hydrant).

**5. BFP full-flow test path (if BFP on lead-in = y)**

FM DS 2-81 **Table 5 p.14**: annual **full-flow test in excess of the greatest sprinkler demand**, flow measured and recorded; internals every 5 years. Acceptable means: **bypass line, hydrant, or another downstream outlet**, or **reversing the check valve in the FDC piping and discharging out of the FDC**. On a campus with an RPZ or double-check on the lead-in this is a **drawing decision** — retrofitting means cutting the lead-in. UFGS wet-pipe acceptance corroborates a forward-flow test at full system demand incl. hose. Greatest-sprinkler-demand gpm is **consumed** from density-area / hydraulics — do not recompute it here. If demand is unpinned, size the path as a **feature** and flag the gpm `[V]`.

**6. Lockable alarm-isolation switch — FM prohibits jumpering**

FM DS 2-81 **§§2.3.3–2.3.4 p.4**: *Prohibit the use of jumpers or forces to temporarily bypass an alarm device that initiates a fire or supervisory alarm to facilitate testing.* Preferred alternative: **(A) a lockable switch with exterior position indication (open/closed) installed in the alarm circuit and located near the alarm device**, so the switch’s condition can itself be inspected. In a live data hall you cannot take the outage → **(A) is effectively mandatory** and is an **electrical / FA design deliverable**: supervised, position-indicating, lockable isolation switch at each interlocking device, shown on the riser diagram and in the C&E matrix. Related: waterflow→building/process interlock test is **ANNUAL** and must verify desired actions are *initiated **and** achieved* (Table 2a item 3) — end-to-end, not a contact closure.

Switch listing / supervision-circuit design is **partially supported** in the codebook (requirement same duties; product selection not). Flag `[V]` on the SKU; do not invent a model.

**7. Interval-lever schedule** — Step 3.5 (this is an engineerable component; emit as a table, not prose-only).

**8. Acceptance-baseline / differential-ITM register** — Step 3.6.

**9. Pump-power / ATS / generator ITM pointers (when pumps / emergency power exist)** — via DS 2-81 → **DS 5-20** pins above. Installation arrangement stays **DS 3-7**. Do not invent “fire pump” clauses inside 5-20.

#### Extended (gate on inputs — still CD features, not O&M)

Apply when the input exists. Do not skip in silence.

| Gate | Feature | Pin |
|---|---|---|
| Pumps exist | Pump-room **churn path**: electric ≥**10 min monthly** · diesel ≥**30 min weekly** (DS 2-81 §2.9.2.1.2 A / §2.9.3.1.2 A / Table 7 item 2). Floor drain accepts the weekly 30-min discharge. Controllers **manual-stop-only** (Table 7 item 5 — FM does not present this as optional). Diesel tank sized to **¾ full or 8 hours at 100% load** (§2.9.3.1.3 C) — size to the 8-hour criterion at CD. Room **>40 °F**; diesel block heater **≥90 °F or room ≥70 °F**. | DS 2-81 §9.7 |
| (code floor for the pump no-flow run) | NFPA 25 no-flow test started automatically; electric ≥10 min, diesel ≥30 min; attendance unless automated testing per §8.3.2.10 (response ≤4 h) [CODE NFPA 25-2020/2023/2026 §8.3.2.2–8.3.2.4, §8.3.2.7, §8.3.2.10.4, pull 25-05]. Frequency is set elsewhere — do not infer it from this row. | | |
| Pumps exist | Shared-generator rule: generators serving **both** FP and other demands conform to the **most stringent** guidance (federal RCM §2.11). A campus standby plant that also backs the electric fire pump **imports FP ITM onto a plant FP does not control**. Name the trade (dedicated FP generator / diesel pump vs shared). `[V]` vs NFPA 20-2025 / NFPA 110. **Mechanism only — do not import federal intervals.** Pair monthly / 3–5 yr auto+ATS checks with **DS 5-20 §2.1.3.9**. | CED-Guyer folio 31; DS 5-20 |
| Yard mains / lead-ins | Flushing outlets for **≥10 ft/s (3 m/s)** scour. Table 11: **6 in. → 880 gpm · 8 in. → 1,560 · 10 in. → 2,440 · 12 in. → 3,520**. Riser-lead-in: a 2 in. drain may reach velocity but a globe valve will not pass stones — need ~**750 gpm** outlet. Flush yard mains **before** connecting sprinkler systems. Strainers flushed until clear **after every significant flow** (incl. hydrant tests and every preaction/deluge trip). | DS 2-81 §3.1.3.3 + Table 11 p.41 |
| Nitrogen = y on company dry/DI | Nitrogen generator **+** conventional compressor (generator cannot meet 30-minute fill). Gas supply on **standby power or UPS**. Sampling ports at ends of **most remote branch lines**; purge valve **remote from the riser**. Never accept a purity reading at the purge valve. FM air-tightness to specify and accept against: **40 psi, ≤1½ psi loss / 24 h** (§3.1.6.1 F). Leakage rate used to identify systems prone to **false trip on loss of compressed air**; loss of air shall not trip for **design duration of the water supply or 2 hours, whichever is greater**. | DS 2-81 §9.6; *Nitrogen inerting…*; DS 2-1 mined |
| Tanks exist | Supervised level alarm, annually tested: tank level **weekly → monthly** (4×) — Tables 8a/8b. Cathodic protection: federal RCM prices internal inspection **3 yr → 5 yr** — **use the mechanism, not the interval**, on a commercial job. Combustible storage/vegetation **≥50 ft** from the tank. Seismic freeboard in FM 50-to-500-year earthquake zones `[V]` DS 2-81 §2.10.1.2. | DS 2-81 §9.8; federal §10.1 row 4 |
| Battery room / UPS | Spare-bank connection point, cable route, floor space (FM DS 5-28 §2.5.2.4(A)); DC disconnect for offline testing (§2.3.4.1); IR-visible terminals. Outage window **~1 day run + 2–3 days recharge = 3–4 days**. Capacity-test cadences are O&M numbers — record them in the turnover index, do not turn this Skill into a battery O&M manual. | DS 5-28; ITM note battery track |
| Dry / DI halls (company-elected) | Two inspector’s test connections per preaction riser (install-sheet item). Write **≤30 s** and the **remote-end measurement point** into the ITM spec (Step 3.7). | DS 2-81 Table 2c item 14; DS 5-32 |
| Containment / hot-aisle | Temperature rating so ambient at sprinkler elevation stays **≥50 °F below rating** (DS 2-81 §2.5.1.3.1 E). Under FM, **wet** hall at nominal **135 °F** (DS 5-32 §2.4.3.3.1.1(B)) ⇒ ceiling ambient **≤85 °F**; dry/preaction at nominal 165 °F is governed by NFPA 13 ordinary-class **100 °F** `[V]` vs 13-2025 table. **Specify glass-bulb** in containment-served / hot-aisle-adjacent areas — cold-flow is a **solder-link** phenomenon (§3.1.4 p.44). QR white space ⇒ first field sample at **year 20**, then 10 (not year 50). | DS 2-81 §9.5; ITM note §4.3 |
| Concealed heads | Annual per-room labour: physically inspect **≥10% per room** + visually inspect the rest, rotating until all done; **one deficient ⇒ inspect every sprinkler in that room** (cover gasket adhering). Choosing concealed heads is choosing that labour — not an architectural default. | DS 2-81 Table 2a item 13 |
| Any sprinkler system | Spare stock sized to the **hydraulically designed area**, not the NFPA 13 cabinet tier (tops out at **24** [CODE NFPA 13-2022/2025 §16.2.7.5, pull 13-02]). Corpus arithmetic (assumptions stated): wet 2,500 ft² → **≈20 @ 130 ft²/head or ≈25 @ 100**; DI 3,500 ft² → **≈27–35**. DI exceeds the 24-head tier. Plus post-fire: replace all non-operated heads within **20 ft (6 m)** of any operated sprinkler (Table 2a item 12). Remote campus → larger on-site stock *to avoid prolonged impairments*. | PRC.12.0.2 p.5; DS 5-32 remote areas |
| Freeze = y | Hydrants **semi-annual** (before cold weather + after snow/ice) — AXA p.6. Valve enclosure **above 40 °F (4 °C)**; *heat tape and steam tracing are not satisfactory substitutes for a heated room* (DS 2-81 §3.1.6.2 A.3). Schedule waterflow-involving ITM around cold snaps. FM “extreme cold” = **20 °F (11 °C) below normal lows for more than a week**. | AXA p.6; DS 2-81 §2.12 |
| Seismic = y | AXA: piping / hangers / **seismic braces** = annual visual **+ monthly spot check + after any seismic event** (p.3). Do not size braces here. | PRC.12.0.2 p.3 |
| Detection / FACU present | Cite **DS 5-48** Tables 5–7 for detection ITM; cite **DS 5-40** only with **edition-stale** flag vs NFPA 72-2025. Do not invent ASD port lifecycle. | DS 5-48; DS 5-40; NFPA 72-2025 |

**Spare-head show-and-verify (coverage is an assumption — flag it):**

```
n_spares ≈ remote_area_ft2 / coverage_ft2_per_head
# coverage_ft2_per_head is NOT in the ITM source — state 100 or 130 and mark [SYN]
# Example (not a default campus): 3500 / 130 ≈ 26.9 → 27; 3500 / 100 = 35
```

---

### 3.5 Interval-lever schedule (CD output)

Emit one row per lever. **None can be bought later.** Name the layer that **grants** it. If the layer does not apply, the lever **does not exist**. **N₂ 3→10 and enhanced-security levers only when FM grants on company-elected wet/dry/DI** — never on SI-as-BOD, and never on code-direct NFPA 25 jobs without naming the granting layer.

| Lever (specified at CD) | ITM consequence | Magnitude (show the arithmetic) | Layer granting it | Also does **not** relax |
|---|---|---|---|---|
| **Nitrogen**, originally installed, on each company-elected dry/DI hall | Full-flow trip / videoscope / ULGW: **3 yr → 10 yr** (Table 2c item 14 p.11). Systems originally installed with nitrogen are **exempt from the black-steel obstruction investigation** at 10 / 20 / every-5-thereafter (item 15). | `(1/3) / (1/10) = 10/3 ≈ 3.3×` fewer full trips + obstruction regime deleted | **FM** on company dry/DI. ⚠ NFPA 25 floor is **3 years** [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]. On a code-enforced or non-FM project, or where the AHJ enforces NFPA 25 directly, **this lever DOES NOT EXIST.** | Annual partial-flow trip still compares to the last full-flow (Table 2c item 13). Weekly air/water pressures, annual leakage rate still apply. |
| **FM Approved *enhanced-security* valve supervision** (Approval Std **3135**) on every control valve (zone valve = control valve, glossary p.50) | Control-valve **visual**: **weekly → semiannual** (Table 1 items 1a vs 1c p.5) | `52 / 2 = 26×` on every zone valve | **FM** on company wet/dry/DI | Semiannual tamper test (item 3); annual full-travel + turns record (item 4) |
| **FM Approved indicating butterfly valves** (where a valve would otherwise sit in item 2) | Leaves the **monthly physical full-open test** population | Third, smaller lever | **FM** | Visual / tamper / annual exercise still apply. Pressure tax is a **hydraulics** item — do not ignore it; do not re-calc it here. |
| **Supervised tank level alarm**, annually tested | Tank level **weekly → monthly** | `52 / 12 ≈ 4×` (weekly→monthly) | **FM** Tables 8a/8b | Interior inspection cadence unchanged by this lever |
| **Cathodic protection** on stored-water tanks | Federal RCM: internal inspection **3 yr → 5 yr** | 1.67× on the most disruptive event (drain + confined-space) | **Federal RCM — FENCE.** Use the *mechanism* (corrosion control buys interval). **Do not write “5 years” as the commercial ITM interval.** | — |

**Generalize the rule (method-independent — FM loss-experience *and* DoD RCM 0.99 reliability model, two incompatible derivations, same conclusion):** any design measure that **removes a degradation mechanism**, or that **reports on it continuously**, is convertible into ITM interval. Supervision and corrosion control (nitrogen, cathodic protection) are two instances of one principle. Quote (CED-Guyer §2.1.1, folios 3–4): *Supervision of components increases the likelihood that conditions or faults will be detected without an inspection activity. … the tables reflect the improved fault or condition detection by specifying LESS FREQUENT INSPECTIONS.*

**AXA XL frequency deltas above NFPA 25** (all PRC.12.0.2 2020; NFPA 25 values = the source’s own characterization — **`[V]` vs NFPA 25-2026**; **do not invent 25-2026 sections**). Fill these on an AXA (or dual) job; on FM-controlling, they are the overlay-read, not the schedule:

| Item | NFPA 25 (per source, `[V]`) | AXA XL | p. |
|---|---|---|---|
| ITM record retention | 1 yr | **≥ 5 yr** (+ overhaul records for system life) | 2 |
| Electrically supervised valves | quarterly | **monthly** | 16–17 |
| Sealed control valves | — | **weekly**; locked/supervised **monthly** | 16 |
| Piping / hangers / seismic braces | annual visual | **+ monthly spot check + after any seismic event** | 3 |
| Hydrants (freezing areas) | annual | **semi-annual**, before cold weather + after snow/ice | 6 |
| Waterflow devices | vane/pressure semi-annual | **semi-annual for all**, + **central-station receipt confirmed** | 13 |
| Deluge/preaction wet trip | dry trip permitted | **wet trip ≥ every 3 yr when possible** | 12 |
| Dry-pipe full-flow trip | — | **≥ triennial, control valve fully open** | 17–18 |
| Fire-main loop / flow test | — | **every 3 yr** + after install / major change / valve-closing / municipal work | 6 |
| Water tank exterior | quarterly | **weekly** | 11 |

**Appendix A trap (repeat):** storage-tank exterior is **weekly** in the text (p.11) and **quarterly** in the table (p.25); hydrant maintenance **semi-annual in freezing areas** in the text (p.6) vs **annual** in the table (p.24). **Narrative controls.**

**Main drain will not detect a partly closed valve:** an **8 in. gate could be more than ¾ shut and only increase friction 3–5 psi** (PRC.12.0.2 p.13). Supervision + the loop/flow test do that job.

**Federal >10% / >20% main-drain ladder** (mechanism; adopt on top of the governing calendar — seven occurrences in the source). Measure against **previous test OR original acceptance readings**:

| Rung | Trigger | Response |
|---|---|---|
| CAUTION | static **or** residual varies **>10%** | Immediate evaluation |
| WARNING | varies **>20%** | *Emergency situation* — immediate distribution-system flow testing **and main-drain tests on ALL ADJACENT sprinkler systems** |

A 20% drop at one riser is evidence of a shared-underground problem. On a campus loop, write the lateral response into the turnover procedure **regardless of which ITM layer governs**. Same ladder re-pointed at hydrant flow tests — the rule is about the **water supply**, not the instrument.

---

### 3.6 Acceptance-baseline register (FM ITM is differential)

Nearly every recurring FM test is scored **against the acceptance record**, not an absolute. Three traditions state it (FM DS 2-81, AXA XL, federal *previous test or original acceptance readings*). Treat as settled.

| Recurring test | Scored against | Cite |
|---|---|---|
| Annual **partial-flow** trip of dry/preaction valves | *trip point (and trip time when possible) in agreement with the **last full-flow trip test results*** | Table 2c item 13 p.10; NFPA 25 partial-open trip in non-full years: preaction §13.4.3.2.3 / dry §13.4.5.2.2.3 (pull 25-04) |
| Annual fire-pump performance | manufacturer’s curve **and/or previous test results**, rpm-adjusted | §2.9.5.1.2 A p.18 |
| Deluge / fixed-spray after every trip | base-of-riser **and** remote pressures vs **design and/or acceptance** | Table 2c item 24 p.12 |
| Annual dry-valve trip | previous: static water, air, trip-point air, trip time | §3.1.6.2 D.1 p.46 |
| Control valves | **number of turns** full-open → full-shut | §3.1.2.1 p.36 |
| Air leakage (dry/preaction) | acceptance leakage rate (criterion **≤1½ psi / 24 h from 40 psi**) | §3.1.6.1 F p.45 |

**Specify the register** (IST / O&M turnover — this Skill names the capture list; the acceptance Skill runs the tests). Minimum:

- full-flow trip **time AND trip-point air pressure**, per system valve
- measured **air-leakage rate** at 40 psi
- **three-point** pump curve with rpm and amperage vs nameplate FLC at 150%
- base-of-riser **AND** hydraulically-remote pressures for every deluge/spray system
- detection response times (ASD transport / VEWFD — **acceptance** numbers live in FM DS 5-32; lifecycle ITM → **DS 5-48** Tables 5–7; FACU companion **DS 5-40** with edition-stale flag)
- turns full-open → full-shut for **every** control valve
- **maintained hydraulic-demand register** — every system’s design demand (gpm @ psi at BOR), kept current, so the annual pump test can be evaluated against **system demand**, not curve-vs-curve only (PRC.12.0.2 p.11)
- door-fan result for every clean-agent enclosure (if any)

If IST baseline status = `unspecified`, the checklist **fails this item** and says so. A hall whose remote-end delivery time was never recorded at acceptance **can never again be proven to meet DS 5-32**.

**Restoration inherits the same duty.** PRC.1.1.0: *Verify by appropriate test that all fire protection systems have been restored*; reopen **and seal** all valves. After any impairment that alters or isolates piping, record the restoration test **in the same format and against the same points**, including remote-end delivery time. Pair with **FM DS 10-7** impairment-program structure; do not invent FM hour-caps. `[inference]` where the codebook does not number a clause — do not present inference as a numbered FM section.

NFPA 25 **≠ acceptance**. Acceptance (13/24/20 + IST) proves install; NFPA 25 keeps the accepted system reliable after turnover. Do not cite NFPA 25 as an acceptance basis.

---

### 3.7 Water-delivery attribution — write the FM criterion into the ITM spec

Three different 30-or-60-second numbers. **Not the same test. Not interchangeable.**

| # | Number | Endpoint | Clock | What it is | Source |
|---|---|---|---|---|---|
| 1 | ≤ **60 s** | inspector’s test connection | valve trip | **NFPA 13 SIZING** — max system size / QOD at design | NFPA 13-2007 §7.2.3.6 via Viking 2010; 60 s to the ITC held [CODE NFPA 13-2025 §8.2.4.2 / 2019 §8.2.3.2 / 2013 §7.2.3.2; , ] |
| 2 | ≤ **60 s** | inspector’s test connection | *from the time the inspector’s test valve is fully open* | **AXA XL ITM pass/fail in service**; fail ⇒ QOD or supplemental chamber | PRC.12.0.2 p.18 |
| 3 | ≤ **30 s** | **the most remote sprinkler** | detection/trip | **FM DS 5-32 DC white-space DESIGN** — controlling in an FM hall | DS 5-32 §2.4.3.2.1.2(D) / §3.3.3.2.4 |

**Pitfall:** the annual trip-test report demonstrates **#2** (different endpoint, doubled clock). **Passing it is not evidence of FM compliance.**

**FM ITM side is resolved on FM’s own authority.** DS 2-81 **Table 2c item 14 p.11**: *Verify systems can deliver water to **hydraulically remote areas** within the specified time. The maximum water delivery time is **60 seconds unless stated otherwise in an FM Global data sheet specifically for the occupancy or hazard being protected**.* For white space the occupancy sheet is DS 5-32 → **30 s is both the design criterion AND the FM ITM pass/fail for the life of the building.** NFPA 25 counterpart: a 25% delivery-time increase over acceptance triggers an obstruction investigation [CODE NFPA 25-2023/2026 §14.3.1(15), dry and DI preaction; 2020 §14.3.1(15) is 50% and dry only, pull 25-04].

**Cite Table 2c item 14, not §3.1.6.1 E** (support text says “remote test connection”; §3.0 is explanatory; Section 2 controls).

**Action:** write **30 s** and the **remote-end measurement point** into the ITM specification and the O&M turnover so year-10 testing still measures the thing the design promised. Do **not** run the 30 s fill calc here (acceptance / hydraulics Skill).

---

### 3.8 Optional gated AGF TESTanDRAIN / RemoteTEST (DRAW / SPEC)

**Gate:** caller explicitly asks for the AGF product-layer lines, **or** the assignment packet / CD set already elected that hardware track. Otherwise mark `N/A (not gated)` and move on — do not sole-source AGF by habit.

When gated, emit DRAW/SPEC lines from the one city corpus **by title** (a worked example + worked packages), or return an explicit **`handoff`** to look those titles up. **Do not invent SKUs.**

Minimum product-layer rules when emitting lines:

| Line | Rule | Status |
|---|---|---|
| Inspector’s-test / express-drain orifice | **Wet:** alarm-test orifice flow ≤ one sprinkler of the smallest K installed on that system [CODE NFPA 13-2022/2025 §16.14.1.1, pull 13-02]. **Dry / DI:** trip-test flow = one sprinkler of a type installed on that system [CODE 2022/2025 §16.14.2.1, §16.14.3.3, pull 13-02]; 2025 two-/four-sprinkler arrangement where delivery was set by §8.2.4.3/§8.2.4.4 [CODE 2025 §16.14.2.2/.3, pull 13-02]. Verify with the engineer of record (mixed K on dry/DI): conservative assumption = use the smallest-K type installed (reject folklore 5/32–7/32; reject RemoteTEST default K5.6 as a universal) | `grounded` method; SKU `[V]` until Approval Guide pin |
| Combined test/drain family | Cite one city corpus / AGF brochure **by title** for family options; do not invent model numbers | Listing **`[V]`** |
| Wet PRV + hydro-lockout trim | Only when wet BOD and corpus supports; reconcile PRV section to **NFPA 13-2025 / enforced** | PRV [CODE NFPA 13-2022/2025 §16.9.7, pull 13-30 (was mis-cited to 13-02)] |
| RemoteTEST / multi-riser campus lever | FACP/BMS C&E + impairment SOO; AHJ remote-actuation acceptance | Listing / AHJ **`[V]`**; else `handoff` |
| DRAINanTEST / sight-glass InspectorsTEST | Only if AHJ or packet wants visual flow | Optional |

If the corpus titles are not available in-session → status `handoff` / `unresolved` on the product lines; still complete the non-AGF core checklist. **Honesty:** a worked inspector's-test outline + four worked packages **exist**; they are **not** a full ITM-led CD project and are **not** Skill defaults for every campus.

---

### 3.9 Status register (mandatory every run)

Emit near the end of Steps / with Outputs. Every controlling claim gets a status.

| Status | Use |
|---|---|
| `grounded` | Method pinned to mined / held sheet + edition (DS 2-81 Tables 1–10 Apr-2019/Oct-2021; DS 3-7 closed-loop ban; DS 5-20 §2.1.3.5 / §2.1.3.9 held PDF; DS 10-7 opened; DS 5-48 Tables 5–7; 52× ladder; 26× / 3.3× arithmetic) |
| `provisional` | Screening with stated assumptions (e.g. spare coverage `[SYN]`; open non-gating RFI; DS 5-40 Sep-2007 cited with stale flag) |
| `unresolved` | Open hole (carried as `ASSUMED`, flagged — not a Stop; packet optional): missing/unresolved elected `system_type`; missing system mix; unpinned carrier; dual-carrier ITM rows unresolved |
| `comparison-only` | SI/NI ITM path, FM preference ranking, App. C directional map — never controlling BOD checklist |
| `handoff` | Work owned elsewhere: pump-envelope; density-area; STS election; IST execution; AGF corpus lookup by title; brace sizing |
| `RFI-variance` | Company-fence gate (SI/NI/foam/mist as BOD); caller asks for O&M manual / invented CD set |

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented project quantities (coverage ft²/head for spare math, a hall program you were not given, a pump gpm you assumed, invented AGF SKUs). Never present `[SYN]` as a code/insurer number. |
| **`[V]`** | Unpinned primary: **every NFPA 25 frequency** except those pinned by pulls 25-01/25-02/25-03: pump no-flow §8.3.1, pump annual §8.3.3.1, valve Table 13.1.1.2, internal-pipe assessment §14.2.1.1, 13-2025 spare-tier / ambient table / 60 s ITC section, 20-2025 test-header outlet count (now Table 4.28(a), pull 20-14), DS 2-81 catalog IR Apr-2026 Δ vs codebook Apr-2019/Oct-2021, DS 5-20 `` unmined beyond held-PDF pins, DS 5-40 stale vs 72-2025, AGF listing numbers, owner standard, AHJ pin. |

**Grounded sheet numbers (cite table/item AND edition):** FM 3→10 yr, 26×, 175% outlets, 4 in. drain (AXA p.19), 40 psi / 1½ psi / 24 h, Table 11 flushing flows, jumper prohibition, DS 5-20 ATS 3–5 yr / generator monthly + auto+ATS 3–5 yr. **Do not invent section numbers.**

**Delta vs NFPA 25 (required, even though unmeasured):** state **UNMEASURED** wherever the code-floor cell is `[V]`. Do **not** fabricate a percentage. Directional only from FM Appendix C *as a map of where layers differ*, never as authority. Known directional collisions to surface:

- Nitrogen **10-year** full-flow is an **FM relaxation**; NFPA 25 floor is **3 years** [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]. Lever may vanish under AHJ-enforced NFPA 25.
- FM is **more frequent** than NFPA 25-2017 on most App. C rows (valve visual weekly vs monthly; physical valve test monthly vs annually; air leakage annually vs every 3 years [CODE NFPA 25 air/gas leakage every 3 yr, 40 psi / 2 h / ≤3 psi (or 4 h source-off): preaction 2020–2026 §13.4.3.2.6 (2017 §13.4.3.2.5); dry 2017–2026 §13.4.5.2.9, pull 25-04]) and **less frequent** on a handful (dry-pendent sample 15 vs 10 years; obstruction “when suspected” vs calendar 5 years [NFPA 25-2023/2026 §14.2.1.1: internal-pipe assessment at least every 5 yr, or per approved risk analysis §14.2.1.2, pull 25-03]). **Re-pin to 25-2026 before promising either direction.**

**Delta vs NFPA 13-2025 (sprinkler-install):** spare quantity (functional remote-area vs cabinet tier), temperature rating / glass-bulb election, QOD implied by 60 s ITC. None of these are NFPA 25 requirements — they are design consequences of the ITM regime. Directional `[V]` where 13-2025 tables are unpinned.

---

### 3.10 Emit output (caller-path only)

An **ITM design-for-testability checklist + interval-lever schedule** (markdown).

**Write it only to the path the caller names.** If the caller did not name a path, return it in the response and stop. If the caller is assembling a CD set, the process home is section **`11_qa-coordination`** — a **home for this output**, not a worked ITM package to copy.

**Minimum contents:**

1. **Edition-pin block** — NFPA 25-2026 latest vs enforced (often 25-2023 on 2024 I-Codes); NFPA 13-2025 as sprinkler-install delta; FM DS 2-81 **Apr-2019/Oct-2021** controlling (+ catalog IR Apr-2026 Δ `[V]`) and/or AXA XL PRC.12.0.2 2020; DS 5-20 / 10-7 / 5-48 / 5-40 / 2-1 pins as applicable; owner posture; statement that **licensed NFPA 25 is not in the codebook**.
2. **Inputs echoed** — assignment packet if present (optional); elected `system_type` wet|dry|DI; system mix per hall; nitrogen y/n; carrier; pump rating + discharge path; standpipe class; BFP y/n; valve-supervision spec; freeze; seismic; IST baseline status. No invented campus. No SI-as-BOD.
3. **Statement:** ITM is a design input; frequency is a CD output; most-stringent is per parameter, **INTERVALS and FEATURES separately**; no whole-layer MAX.
4. **Features checklist** — core items plus gated extended items (+ optional AGF if gated), each `DRAW`/`SPEC`/`C&E`/`N/A`/`[V]`, with the controlling layer named.
5. **Interval-lever schedule** — table from Step 3.5, layer named on each row, show-and-verify arithmetic (`52/2 = 26×`, `10/3 ≈ 3.3×`), do-not-over-read caveats, nitrogen / enhanced-security **existence check** (FM + company wet/dry/DI only).
6. **Control-valve ladder** (52×) as the per-parameter demonstration.
7. **Acceptance-baseline register** capture list + IST status pass/fail.
8. **Water-delivery attribution** (30 vs 60, remote area vs ITC) written into the spec language.
9. **Δ vs NFPA 25** (unmeasured / directional `[V]`) **and** **Δ vs NFPA 13-2025** (spares / temp / QOD).
10. **Status register** + **`[SYN]` / `[V]` register.** Honesty line: outline + a worked inspector's-test worked set **exist by title**; **no full ITM-led CD project**; this is a checklist recipe.

Do **not** emit: occupancy schedule, density×area `calcs/fp` transcript, pump rated nameplate selection, node-by-node hydraulic tree, CAD, prior job files retrieval, assignment-packet rebuild, invented AGF SKUs, or a fake O&M manual / 25-year task calendar built from Appendix A or Appendix C.

---

## 4. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess:

1. Assignment packet missing → **not a Stop** (packet optional); proceed and flag `ASSUMED`.
2. **Missing / `unresolved` company-elected `system_type`**, or mix not in `wet` / `dry` / `double-interlock`.
3. **SI / NI / other preaction / foam presented as BOD** → `RFI-variance` / company-fence. Mist → `PRACTICE REFUSED`.
4. **Unpinned carrier** (not `FM DS 2-81 controlling` and not `AXA XL PRC.12.0.2 overlay`).
5. **Caller asks to write an O&M manual** or a full NFPA 25 task calendar instead of CD features + levers.
6. **Caller asks to invent a worked CD set** (hall program, pump rating, jurisdiction) as if one existed. Outline + a worked inspector's-test set exist **by title**; they are not a full ITM-led CD project. Checklist against *supplied* inputs only.
7. Dual-carrier with **ITM rows missing** from the matrix Skill **and** one carrier’s ITM values missing here — do not invent AXA frequencies beyond the narrative table above, and do not invent NFPA 25-2026 sections.
8. NDA owner treated as numeric.
9. Caller asks this Skill to **classify occupancy**, **run density×area `calcs/fp`**, **size a pump envelope**, **retrieve prior job files**, or **rebuild the assignment packet**.
10. Caller asks to write outside the caller-named path.
11. Caller asks to invent AGF SKUs / listing numbers not present in the one city corpus titles.

Nitrogen = `n` on a company DI hall is **not** a Stop — it is a lever **not taken**; record that the 3→10 yr reduction and the black-steel obstruction exemption **were declined**, and that FM full-flow stays at 3 years (same as the NFPA 25 floor [CODE NFPA 25-2017–2026, full-open trip every 3 yr: preaction §13.4.3.2.2 (partial-open in other years §13.4.3.2.3); dry §13.4.5.2.2.2 (annual trip §13.4.5.2.2), pull 25-04]).

---

## 5. Citations (section **and** edition — do not invent)

Shop codebook **by title** (not a required filesystem path).

**Design practice / method**

- *Design practice* — non-negotiable #1 (3-layer, most-stringent, Δ vs NFPA 13-2025); #2 enforced ≠ latest, cite section **and** edition. This Skill also reports **Δ vs NFPA 25**. Status vocabulary as above.
- *Enforced-vs-latest edition resolver and reference pins* — 2024 I-Code pins (NFPA 25-**2023** enforced / **2026** latest).

**ITM / testability (primary)**

- *ITM basis and design for testability* — the whole recipe. Especially: three-layer ITM picture; physical obligations; water-delivery attribution; AXA frequency table; FM DS 2-81 (levers, remote-area 60 s default, differential ITM, pump track, flushing Table 11, Appendix C fence); federal RCM (supervision-buys-interval, 52× ladder, >10%/>20% lateral main-drain, shared-generator, fence).
- *Acceptance, commissioning and integrated systems testing* — IST as the lifetime baseline; jumper prohibition from first energization; NFPA 25 ≠ acceptance.
- *Fire protection impairment management* — sectional valves, hidden impairment, restoration-is-a-test; **48 h / one-at-a-time as AXA XL not FM**; DS 10-7 **opened** (structure, not AXA attribution).
- *Valve type selection, listing and supervision basis* — monthly-physical population by valve **type**; FM Approved IBV as the third lever; butterfly pressure tax (do not re-calc here).
- *Hot-work management during campus construction* — DS 10-3 §2.5.1.1.C / §2.5.2.1.3 (work + watch + monitor).
- *Nitrogen inerting and internal corrosion control* — originally-installed condition precedent; sample at branch-line ends; generator + compressor; C = 100 until 98% earned; DS 2-1 mined companion.

**Sheets as the codebook / holdings state them (do not invent sections)**

| Claim | Pin |
|---|---|
| FM DS 2-81 self-contained Tables 1–10; scope fence | §1.0 p.3; codebook **Apr-2019 / Interim Rev. Oct-2021**; catalog IR Apr-2026 Δ `[V]` |
| Nitrogen full-flow 3 yr → 10 yr; obstruction exemption | Table 2c items 14 & 15 p.11 |
| Enhanced-security visual weekly → semiannual | Table 1 items 1a vs 1c p.5; Approval Std **3135**; glossary p.50 zone valve = control valve |
| ITM endpoint = hydraulically **remote area**; 60 s default overridden by occupancy sheet | Table 2c item 14 p.11 — **not** §3.1.6.1 E |
| BFP annual full-flow > greatest sprinkler demand | Table 5 p.14 |
| Jumper prohibition; lockable position-indicating isolation switch | §§2.3.3–2.3.4 p.4 |
| Air tightness 40 psi / 1½ psi / 24 h | §3.1.6.1 F p.45 |
| Flushing ≥10 ft/s; Table 11 flows | §3.1.3.3 + Table 11 p.41 |
| Standpipe 5-yr flow test at design flow and hose-valve pressure | Table 3 item 8 p.13 |
| Sprinkler damage indicator *rating − 50 °F* | §2.5.1.3.1 E p.8 |
| Appendix C stale (FM 2019 / NFPA 25-2017); do not cite as authority | App. C Table 12 pp.54–60 |
| Closed-loop meter prohibited | FM DS 3-7 **§2.3.3.6** p.11; AXA XL PRC.12.0.2 p.8; CED-Guyer folio 33 |
| Test means ≥150% rated; **outlets ≥175% rated** | FM DS 3-7 **§2.3.3.4** p.11 |
| ≥4 in. standpipe test drain, 250–500 gpm | AXA XL PRC.12.0.2 **p.19** |
| Sectional valves rather than main valves | AXA XL PRC.1.1.0 **p.4** |
| Hidden impairment = most serious type | PRC.1.1.0 **p.2** |
| ≤30 s to most remote sprinkler (design **and** FM ITM) | FM DS 5-32 **Jan-2026** §2.4.3.2.1.2(D) |
| QR / 135 °F wet-hall head | DS 5-32 §2.4.3.3.1.1(B) |
| PRC.12.0.2 Appendix A contradicts narrative | tank exterior p.11 vs p.25; hydrants p.6 vs p.24 |
| ATS / generator ITM path | DS 2-81 Table 2.9.1.1 item 10 / §2.9.2.1.2 → **DS 5-20** Oct-2016/IR Oct-2025 held PDF: §2.1.3.5 + Table 2.1.3.5.1; §2.1.3.9 + Table 2.1.3.9.3 |
| Impairment management sheet | FM DS 10-7 **Apr-2019 / IR Oct-2025** (opened) |
| Contractor authority (Red Tag) | FM DS 10-4 **January 2024** §2.2.1.6, §2.2.4.5 / .5.1 |
| State fire-side ITM (KY example) | 815 KAR 10:060 §7(2) (NFPA 1-2018 basis; 2023 filing) |
| Detection ITM | FM DS 5-48 **Jan-2011 / IR Apr-2025** Tables 5–7 (opened) |
| FACU companion (stale) | FM DS 5-40 **Sep-2007** — edition-stale vs NFPA 72-2025 |
| Corrosion companion | FM DS 2-1 **Oct-2016 / IR Jul-2022** (mined) |

**Absent (name the hole; do not fill it):**

- **NFPA 25-2026 (and 25-2023) licensed text** — still ABSENT; `[V]`; do not invent section numbers. Exception: pinned by pulls 25-01/25-02/25-03: pump no-flow §8.3.1, pump annual §8.3.3.1, valve Table 13.1.1.2, internal-pipe assessment §14.2.1.1.
- **Tier-A owner ITM standard** — still Absent; structure only under NDA.
- **Removed from Absent (do not re-list as holes):** FM DS 10-7 (opened); FM DS 5-48 (opened); FM DS 2-1 (mined); FM DS 5-20 (mined, run 393); FM DS 10-4 (mined, run 394). DS 5-40 is **held** but **edition-stale** — not Absent, not current.

**Exercises honesty (by title, not required paths):** a worked example; a worked example + four worked packages. **Exist.** Still **no full ITM-led CD project.**

---

## 6. Negative teaching

1. Treating SI/NI (or “wet/SI/DI”) as a company BOD mix and writing the controlling checklist for it.
2. Promising FM nitrogen **10-year** or enhanced-security **26×** on a non-FM job, on SI-as-BOD, or without naming the granting layer.
3. Building an ITM schedule from AXA PRC.12.0.2 **Appendix A** or FM DS 2-81 **Appendix C**.
4. Quoting NFPA 25 frequencies as if licensed text were in the codebook (inventing 25-2026 section numbers).
5. Attributing AXA **48-hour notice / one-at-a-time** to FM DS 10-7.
6. Claiming DS 5-20 “fire pump” clauses — there is no such string; path is 2-81 → 5-20; install stays 3-7.
7. Leaving DS 10-7 / 5-48 / 2-1 in the Absent list after they were opened/mined; treating DS 5-40 Sep-2007 as current vs NFPA 72-2025.
8. Inventing AGF SKUs / listing numbers; sole-sourcing RemoteTEST without Approval Guide / AHJ pins.
9. Copying one city outline geometry or a four-hall mix as Skill defaults; claiming a full ITM-led CD project exists.
10. Emitting an O&M manual / 25-year calendar; running `calcs/fp`; retrieving prior job files; writing to caller-unnamed corpus paths.
11. Merging INTERVALS and FEATURES into one whole-layer MAX; importing federal RCM intervals.

---

## 7. What this Skill does not own

Hand these off; do not perform them here:

| Work | Where it lives |
|---|---|
| Fire-pump controller configuration, remote-signal terminal map, pump-room valve supervision method per valve, controller weekly-test settings | `fire-pump-controller-configuration-and-supervision` |
| Space-list IBC occupancy / §903.2 / FM HC / AXA OH | `occupancy-hazard-fork` |
| System-family election | `suppression-technology-selection` |
| Density × area `calcs/fp` | `density-area-dry-increase` |
| Pump rated flow/pressure, churn, supply curve | `pump-envelope` (this Skill **consumes** count/rating to size the **test header**, and does not freeze a nameplate) |
| Dual-carrier per-parameter BOD | `most-stringent-basis-matrix` (consume **controlling ITM rows** if present) |
| Assignment packet (retrieve-adapt / prior job files) | the input packet — consume; do not rebuild; **do not retrieve prior job files** |
| Node-by-node hydraulic tree, BOR psi, C-factor | hydraulic-tree / other |
| 30 s fill-volume calc / witnessed trip test script | `commissioning-ist-acceptance-packet` / acceptance notes |
| CAD / drawings production | not this Skill |
| Brace sizing (ZOI, `Fp`, member) | *Seismic bracing and restraint of sprinkler piping* — this Skill only attaches **inspection cadence** |
| Detection/ASD lifecycle detail beyond DS 5-48 Tables 5–7 | DS 5-48 / NFPA 72-2025 Ch. 14 — do not invent |
| Full O&M manual / NFPA 25 task calendar | **Stop** — wrong deliverable |
| Reconstructing an NDA owner standard from public pages | forbidden |
| Writing outside the caller-named path | forbidden |

---

## 8. Design practice (ITM restatement)

1. **Three-layer, most stringent, on INTERVALS and FEATURES separately.** Code (NFPA 25) is the *floor*. The **insurer sheet** usually sets the real basis: on FM, **DS 2-81 is self-contained**; on AXA XL, **PRC.12.0.2 is a delta overlay unusable without NFPA 25**. The **owner standard** can raise again (CMMS, vendor qualification) and cannot lower. Design to the **most stringent applicable layer PER PARAMETER**. Report **Δ vs NFPA 25** (ITM) **and Δ vs NFPA 13-2025** (install consequences). Cite the sheet — don’t assert nitrogen interval or valve cadence from habit.
2. **Per-parameter, not per-layer.** The control-valve ladder is 52× with an insurer at both ends. Never MAX whole sheets. Never import federal RCM intervals because a reliability model looked friendlier.
3. **ITM frequency is a design output.** Nitrogen and enhanced-security supervision are CD specifications. The 10-year lever does not exist where NFPA 25 is enforced directly, or where company fence refused the BOD family. Name the layer before promising it.
4. **Company fence first.** Wet / dry / double-interlock only. SI/NI = comparison-only. Foam prohibited. Mist `PRACTICE REFUSED`.
5. **Current editions; enforced ≠ latest.** Default NFPA 25-**2026** / 13-**2025** for delta baselines; the code-floor *citation* stays at the AHJ pin. AXA PRC cites **no editions** — date the claim. DS 2-81 codebook Apr-2019/IR Oct-2021 controlling; catalog IR Apr-2026 flagged Δ `[V]`.
6. **Show-and-verify.** `52/2 = 26×`, `10/3 ≈ 3.3×`, `Q_outlets = 1.75 × Q_rated`, spare `n ≈ area/coverage` with coverage flagged `[SYN]`. No `calcs/fp` in this Skill.
7. **Honesty.** NFPA 25 numeric delta is **unmeasured**. Outline + a worked inspector's-test set exist by title. No full ITM-led CD project. Do not invent a CD set. Status register every run. `[SYN]` / `[V]` in the open.

If notes conflict, **most-stringent wins** and both sources stay visible. Narrative of PRC.12.0.2 beats its Appendix A. DS 2-81 Tables 1–10 beat its Appendix C. Occupancy sheet (DS 5-32) overlays the ITM sheet’s 60 s default because Table 2c item 14 writes that deference into its own text.

---
