---
name: Commissioning IST acceptance packet
description: >-
  use this, ideally after STS wet|dry|DI + matrix acceptance/carrier rows +
  releasing C&E exist (packet optional; anything absent is assumed and
  flagged ASSUMED, never a stop), when you must emit the construction-
  completion acceptance / IST program stack (individual acceptance + NFPA 4 IST
  + FM DS 5-32 App. C/D + FM85A/999C); SI/NI-as-BOD → Stop RFI-variance
  (comparison-only); foam prohibited; mist PRACTICE REFUSED; status register
  every run — not ITM interval tables, not C&E rewrite, not density×area, not
  ≤30 s design-stage volume screen.
---

# Commissioning IST acceptance packet

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **This Skill is the CONSTRUCTION-COMPLETION ACCEPTANCE / IST PROGRAM STACK**, not an ITM interval table and not a C&E rewrite. After a completed **the input packet**, a company-elected **`wet` | `dry` | `double-interlock`** from **`suppression-technology-selection`**, consumed **`most-stringent-basis-matrix`** acceptance/carrier/system-family rows (when dual-carrier or those rows exist), and a **releasing C&E / SOO** already exist, it asks: *what must be witnessed, recorded, and signed so the as-built detection → releasing → preaction → power-isolation chain is proven before the hall is energized?* It produces a **five-pillar acceptance packet** with FM↔AHJ dual-acceptance hold points, DS 5-32 App. C / App. D scripts, FM85A / FM999C form lines, a **status register**, and a **≤30 s water-delivery proof hand-off** to the dry/preaction water-delivery screen.

**Core thesis:** Turnover is a **STACK**, not one test. Individual acceptance proves each subsystem against its own install standard; **NFPA 4 IST proves the interactions**. On an FM-insured campus there are **two AHJs** (local building/fire + FM Field Engineering) — two plan reviews, two acceptance acts, one building. FM DS 5-32 overlays the DC numeric proofs the code floor does not supply (heated-wire, ASD transport, ≤30 s remote water, App. D Test Mode). **NFPA 25 ≠ acceptance.**

**Design practice (lede):** three-layer basis (code floor × insurer sheet × owner standard), **most-stringent union PER PARAMETER** (acceptance act, witness scope, numeric pass/fail, form set, baseline capture). Delta vs **NFPA 13-2025** (install acceptance) **and** vs the code IST/FA suite where pinned. Cite **section AND edition**. Show-and-verify. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock`** only; SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): packet + STS wet\|dry\|DI + matrix acceptance/carrier/system-family rows when dual-carrier + releasing C&E. Caller-path-only. **NO PLACEHOLDER.** Generic — do not copy a synthetic hall program, jurisdiction, or witness name as defaults.

**Honesty — worked package is partial.** Outline spine: commissioning/IST-led hall (a prior site SI preaction — **`[SYN]` comparison-only / structure only**; never company BOD / hall defaults). Matching worked package exists for the **≤30 s delivery verification protocol only** — do **not** copy synthetic hall ft² / MW / head counts as defaults. Do not invent a full NFPA 4 IST script from habit. Consume ≤30 s worked package **method only**.

Write the packet **only** to the path the **caller** names. Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill elects acceptance acts, not system family)

This Skill may emit a **controlling** construction-completion acceptance / IST packet only against an elected company system family:

1. **Wet-pipe sprinkler**
2. **Dry-pipe sprinkler**
3. **Double-interlock preaction**

Comparison-only (never elected here; never the controlling acceptance BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

FM DS 5-32 January 2026 §2.4.1.1 preference ranking (Wet → NI → SI → DI last) and §2.4.3.2.1.2(D)’s **“no interlock-type qualifier”** on the ≤30 s gate remain **`comparison-only` evidence**. That sheet fact is **not** permission to run a controlling acceptance packet on SI/NI BOD, and **not** company election permission.

**This Skill does not elect families.** It **consumes** the election from `suppression-technology-selection`, acceptance / carrier / system-family rows from `most-stringent-basis-matrix` (when dual-carrier or those rows exist), the completed the input packet, and the releasing C&E / SOO from `preaction-releasing-c-and-e-soo`. Controlling BOD = `wet` | `dry` | `double-interlock` only.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling IST / acceptance packet as if SI/NI were company-elected.
6. Do **not** continue “On SI halls…” as a controlling ITP instruction.
7. SI/NI (including a prior single-interlock outline spine, SI measurement-gap prose from DS 2-0, FM ranking / “no interlock qualifier”) may appear only as **`comparison-only`** evidence — never the controlling five-pillar / App. C/D / ≤30 s path.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Emit controlling acceptance / IST packet |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do **not** elect/accept mist as controlling BOD; mist remote-pressure baseline → refused / `handoff` only |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only special-hazard tracks | May flag PRC.13.0.5 / DS 4-9 / NFPA 15 `[V]` companion rows; do not port agent rules onto water-based company BOD |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist does **not** authorize mist election or acceptance here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Five-pillar acceptance / IST stack + status register | System-family election (STS) |
| Dual-AHJ hold points; App. C/D scripts (gated) | Occupancy / HC / OH classification |
| FM85A / FM999C checklist; baseline register | Density × area `calcs/fp` |
| ≤30 s **witnessed** live proof plan + hand-off | Design-stage ≤30 s volume / QOD screen (water-delivery owns) |
| Reciprocal handshakes (water / ITM / C&E / PI / multizone / STS / matrix / nitrogen) | Rewriting releasing C&E / SOO |
| Consume packet + STS wet\|dry\|DI + matrix + C&E | ITM interval tables / design-for-testability levers |
| Edition pins + Δ vs 13-2025 + code IST/FA floor | Inventing full NFPA 4 IST scripts without C&E |
| | Inventing MDP/UPS disconnect lists (power-isolation owns means) |
| | Copying a prior single-interlock ~28k ft² / ~14 MW as defaults |
| | Treating NFPA 25 as acceptance |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** each of the five pillars, **(c)** App. C heated-wire / ASD ≤60 s (or N/A), **(d)** App. D Test Mode (or N/A), **(e)** the ≤30 s proof claim, **(f)** FM85A/999C form readiness, and **(g)** each baseline-register item:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling wet\|dry\|DI + edition + claim supported by **mined** sheet / caller-witnessed live act already closed |
| `provisional` | Directionally pinned; edition / form / calc corroboration hole flagged `[V]` — **calc-only ≤30 s ≤ `provisional`**, never silent `grounded` |
| `unresolved` | STS / matrix / C&E / carrier / AHJ edition / detection / power-isolation pin not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, a prior single-interlock spine, FM ranking / “no interlock qualifier”, SI measurement-gap prose — never controlling BOD |
| `handoff` | Peer owns next action (water-delivery design screen; ITM intervals; C&E authorship; PI Fig D.1 means; multizone N; N₂ originally-installed flag) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as acceptance path — record and refuse; do not continue mist BOD |

**Unearned live ≤30 s → never `grounded`.** Live witnessed remote-point timing may reach `grounded`. Calc corroboration alone → ≤ `provisional`. Design-stage water-delivery screen → `handoff` (does not substitute for acceptance proof on a new hall). SI evidence → `comparison-only`. Invented NFPA 4 script / hall defaults → Stop.

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent a campus, C&E matrix, IST script, or hall program. Do not treat SI/NI as company BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve prior job files. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). |
| **Consumed `most-stringent-basis-matrix` acceptance / carrier / system-family rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling acceptance / carrier / system-family row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap FM App. C onto an AXA-only job or drop AHJ certificates on an FM job. |
| **Releasing C&E / SOO** | **yes** | Named inputs→outputs matrix (detection → trip → HVAC/dampers → power isolation → notification → restoration). Missing or “TBD” → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged — this Skill does not **silently** invent C&E / NFPA 4 scenarios; any assumed C&E basis is labeled `ASSUMED`. |
| **System mix per hall / zone (controlling)** | **yes** | Already pinned: `wet` / `dry` / `double-interlock` **only**. Drives which individual-acceptance pillars run. SI/NI may appear only as `comparison-only` annotations — never controlling mix elections. |
| **Carrier** | **yes** | `FM DS 5-32 / DS 2-0 controlling` **or** `AXA XL overlay` **or** dual **or** explicit `n/a`. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **AHJ-enforced I-Code / NFPA suite** | **yes** | Enforced editions for 13 / 72 / 20 / 24 / 4 / 3. Delta baselines = latest shop pins below. Unpinned AHJ → **not a Stop**: proceed with a stated `ASSUMED` edition (value + why), flagged; do not label the packet sealed while the edition is ASSUMED. |
| **Detection type** | **yes** | VEWFD/ASD y/n; spot smoke; linear heat; other. App. C heated-wire applies only where VEWFD is the FM detection basis. |
| **Power-isolation present** | **yes** | `y` / `n`. `y` → App. D Test Mode is a mandatory script line. Do **not** invent MDP/UPS tag lists — consume from C&E / packet; means detail → `power-isolation-disconnect-control` (handshake only this run). |
| **Special-hazard / agent systems** | **yes** | List or `none`. Agent systems pull PRC.13.0.5 / DS 4-9 tracks — do not port agent rules onto water-based. Foam → Stop. Mist → `PRACTICE REFUSED`. |
| **Caller output path** | **yes** | If unnamed, return the packet in the response and stop. |

Optional (do not block; flag `[V]` / `handoff` / `comparison-only`): owner witness role name; FM field-office witness scope already settled; pump count/rating (consumed for pump acceptance pillar, not sized here); underground / standpipe presence; smoke-control §909 trigger; nitrogen originally installed y/n (baseline / ITM eligibility flag only — nitrogen Skill owns medium/C); SI comparison evidence (a prior site spine / DS 2-0 SI gap) — never controlling.

**Do not invent** a C&E matrix, a hall program, a jurisdiction, an IST baseline, PLACEHOLDER text, or MDP/UPS disconnect lists. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token**; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI |
| `most-stringent-basis-matrix` | Acceptance / carrier / system-family rows; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA swap |
| `preaction-releasing-c-and-e-soo` | Named C&E / SOO — consumed when present (else `ASSUMED`, flagged) | Rewrite C&E; invent NFPA 4 scenarios without matrix |
| `dry-preaction-water-delivery-screen` | Named design-stage proof method / QOD election when present | Own design-stage volume/QOD screen here |
| `itm-design-for-testability` | 30 s + remote-end written into CD / ITM levers when present | Emit ITM interval tables here |
| `power-isolation-disconnect-control` | Means / Fig D.1 context when present (handshake only) | Invent MDP/UPS tag lists or own Test-Mode architecture here |
| `multizone-preaction-zone-alignment` | Zone count / 1:1 alignment tags when present | Elect N / boundaries here |
| `nitrogen-inerting-and-c-factor-gate` | Originally-installed N₂ flag for baseline / ITM eligibility | Own fill clock or the C-factor election (shop C=100; 120 comparison-only) here |
| `occupancy-hazard-fork` / density / pump | Named occupancy / demand / pump pins when present | Re-classify, `calcs/fp`, or size pump |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling acceptance / carrier / system-family rows are missing when required, or releasing C&E is missing / “TBD” → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

### 2.2 Reciprocal handshakes (required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `dry-preaction-water-delivery-screen` | Design-stage volume / QOD / zone-split **election**; named proof method | **Witnessed** ≤30 s live remote-point script + baseline capture; endpoint = design pressure |
| `itm-design-for-testability` | ITM **intervals** / CD testability levers (≠ acceptance) | Acceptance **baseline register** capture list (DS 2-81 consumer input) |
| `preaction-releasing-c-and-e-soo` | Authoritative C&E / SOO authorship; names 30/60 clocks | **Consume** C&E for NFPA 4 IST scenarios; refuse invent |
| `power-isolation-disconnect-control` | Disconnect **means** / Fig D.1 detail (sibling unrestamped — handshake only) | App. D **Test Mode witness** line when power-isolation = `y` |
| `multizone-preaction-zone-alignment` | Zone count N / 1:1 alignment | Per-zone acceptance acts when zones exist |
| `suppression-technology-selection` / `most-stringent-basis-matrix` / the input packet | Family + matrix + packet | **Consume only** |
| `nitrogen-inerting-and-c-factor-gate` | Medium / C / fill; ITM 3→10 eligibility lever | Baseline “originally installed with nitrogen” y/n capture only |
| `asd-vewfd-return-sampling` | ASD port / transport design math | App. C heated-wire + ASD ≤60 s **witness** when VEWFD |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency. Do **not** restamp `power-isolation-disconnect-control` from this Skill.

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest)

Resolve **enforced** vs **latest** before filling any row. Format every citation `instrument-edition §section` (or App./form + page when that is what the sheet uses).

| Standard | Role in this Skill | Shop-pinned editions |
|---|---|---|
| **NFPA 3** | Commissioning *process* (OPR → BOD → SOO → prefunctional → acceptance → IST → closeout); Cx plan contents [CODE NFPA 3-2024 §5.2.3.2 items (1) to (11); §5.2.3.3 the plan forms the commissioning record; pull 3-01; §5.3.3 later-phase update (9 items incl. sequence of operation, schedule, qualified specialists) [CODE NFPA 3-2024 §5.3.3, pull 3-02]; A.5.2.3.2 suggested structure [annex, advisory 'should', pull 3-02]] | **2024** |
| **NFPA 4** | Integrated systems testing (cross-system C&E) | **2024**. Modification retest §6.4.3: changed functions + **10% of unaffected inputs, max 50**. |
| **NFPA 13** | Aboveground sprinkler/preaction install acceptance + contractor certificate | Delta = **13-2025 Ch.29**. Unamended **2024 I-Codes** often enforce **13-2022**. Hydrostatic test: **200 psi for 2 h** without loss; where portions are normally subjected to **system working pressure over 150 psi**, test those at **50 psi above system working pressure** for 2 h [CODE NFPA 13-2025/2022 §29.2.1.1, §29.2.1.3; 2019 §28.2.1.1, §28.2.1.3; pull 13-04]. Basis is system working pressure, not static. |
| **NFPA 24** | Underground / private fire-service-main acceptance | **2025**. Flush clear; ≥**10 ft/s** where available; hydro before backfill. |
| **NFPA 20** | Fire-pump field acceptance | **2025 Ch.14**; performance §6.2 (≥150% capacity @ ≥65% head; churn ≤140% rated head). |
| **NFPA 72** | FA + releasing acceptance / ROC | **2025**. Ch.23 releasing service — [CODE NFPA 72-2025 §23.11.1–§23.11.11, pull 72-06]. |
| **NFPA 25** | **Post-turnover ITM only** — **not** an acceptance basis | Latest **2026**. Do **not** cite as acceptance. Do **not** import one city/ITM intervals into this packet. |
| **IFC/IBC** | §901.5 acceptance; §901.6.2 integrated testing index; §907.7 FA per 72 | **2024** model; AHJ amendments control. |
| **FM DS 5-32** | **DC acceptance overlay** — App. C heated-wire, ASD ≤60 s, ≤30 s water, App. D Test Mode | **January 2026** |
| **FM DS 2-0** | FM plan-review + acceptance protocol; **FM85A / FM999C** (App. C forms) | **October 2021 / Interim Rev. January 2024**. FM as AHJ: App. A. |
| **FM DS 2-81** | Differential ITM baseline **consumer** of this packet’s records — not the acceptance protocol | **April 2019 / IR October 2021** |
| **AXA XL PRC.13.0.5** | Carrier acceptance for **special extinguishing** systems only | **2020**. Scope fence: **not** water-based company BOD. |
| **FM DS 4-9** | Clean-agent acceptance (door fan mandatory on FM) | **Oct-2018 / IR Jul-2023** |

Look up **by title** (not a required filesystem path): *Design practice*; *Acceptance, commissioning and integrated systems testing*; *ITM basis and design for testability*; *Preaction releasing cause-and-effect and sequence of operations*; *Enforced-vs-latest edition resolver and reference pins*; *FM DS 5-32 insurer design basis*; *AHJ special inspection and third-party commissioning*.

**Corpus pins (short — honesty):**

- **Mined (primary):** acceptance-commissioning-and-integrated-systems-testing note (five-pillar; dual AHJ; App. C/D; ≤30 s; NFPA 25 ≠ acceptance; FM85A/999C; baseline = DS 2-81 differential); monograph ; FM DS 5-32 / DS 2-0 sheets; AHJ special-inspection note (§909 third authority).
- **`[SYN]` comparison-only:** a prior site outline a worked example (SI primary_system; ~28k ft² / ~14 MW — **structure spine only**); ≤30 s worked package (method only, `verdict: corpus-insufficient`); VEWFD heated-wire worked companion (Table C.2 method; do not invent amperage → `[V]`).
- **Do not blur:** one city ITM-led outline (IST in name, ITM spine) → ITM Skill owns; never import intervals as acceptance acts.
- **Absent / `[V]`:** licensed NFPA 13-2025 Ch.29 subsection text; full reusable NFPA 4 IST script library independent of C&E (test-plan minimum content held: [CODE NFPA 4-2024/2027 §4.5.1, pull 4-04]; IST trigger [CODE NFPA 4-2021/2024 §4.1.3, pulls 4-03, 4-02]); (NFPA 72-2025 §23.11.x now held [CODE, pull 72-06]); newer FM85A/999C portal revs; FM85B body; company wet\|dry\|DI fence inside the acceptance KB note itself (fence lives in restamped Skills / STS).

Consume packet + STS + matrix + C&E if present. Do not rebuild them. Do not retrieve prior job files.

### 3.2 Confirm prerequisites — upstream missing → ASSUMED, not a Stop

| Gate | Pass | Fail |
|---|---|---|
| Hard-scope company fence | Controlling mix = wet \| dry \| DI | SI/NI/foam/mist-as-BOD → **Stop** (`RFI-variance` / `PRACTICE REFUSED`) |
| Assignment packet present | Consume space list, system mix, carrier, AHJ pins | Optional — proceed without it; label filled-in values `ASSUMED` |
| STS company election token | `wet` \| `dry` \| `DI` pinned | Missing → `ASSUMED` company family (flagged) / `handoff` — not a Stop |
| Matrix acceptance/carrier/system-family rows | Consumed when dual-carrier / when rows exist | Unresolved controlling rows → `ASSUMED` (more stringent), flagged — not a Stop |
| Releasing C&E / SOO present | Named initiation → releasing → HVAC/dampers → power isolation → notification → restoration, with priorities and failure fallbacks | Missing → `ASSUMED` C&E basis (flagged) and hand off to preaction-releasing C&E Skill; do **not** silently invent matrix rows |
| Carrier pinned | FM / AXA / dual / n/a named | Missing → `ASSUMED` carrier (flagged) — not a Stop |
| AHJ editions pinned | Enforced 13/72/20/24/4/3 (or explicit `[V]` with no seal claim) | Missing → `ASSUMED` edition (flagged); not labeled sealed while ASSUMED |

**Out of scope — emit a hand-off row, do not continue:**

- ITM interval tables / design-for-testability levers → **itm-design-for-testability**
- C&E rewrite / SOO authorship → **preaction-releasing-c-and-e-soo**
- Density × area / dry +30% → **density-area-dry-increase**
- Occupancy / HC → **occupancy-hazard-fork**
- Design-stage ≤30 s volume screen / QOD election → **dry-preaction-water-delivery-screen** (this Skill **consumes** the proof method and **witnesses** the field timing)
- Pump nameplate selection → **pump-envelope**
- Disconnect means / Fig D.1 architecture → **power-isolation-disconnect-control** (handshake; do not invent MDP/UPS lists)
- Zone count / 1:1 alignment → **multizone-preaction-zone-alignment**

### 3.3 Five-pillar stack (emit every pillar or mark N/A with reason)

Union = **most stringent per acceptance act**. Code forms stay even on an FM site; FM DC proofs stay even where code is satisfied. Owner may add witnesses/scenarios; owner may not delete an insurer-required proof. Status each pillar.

| Pillar | What it is | Controlling instruments |
|---|---|---|
| **1. Commissioning record** | Process: OPR → BOD → SOO → prefunctional → acceptance → IST → issues closure → systems manual → training → final Cx report | **NFPA 3-2024** |
| **2. Individual acceptance records** | Each subsystem meets its own install standard | NFPA **13-2025** Ch.29 (aboveground); **24-2025** (underground); **20-2025** Ch.14 (pump); **72-2025** ROC (FA/releasing); special-hazard per PRC.13.0.5 / DS 4-9 / NFPA 15/`[V]` as applicable (handoff-only; foam Stop; mist PRACTICE REFUSED) |
| **3. Integrated test plan + report** | Cross-system interactions per the **existing** C&E | **NFPA 4-2024** + owner; IFC **§901.6.2** index |
| **4. Insurer acceptance evidence** | FM plan-review hold + field proofs + **FM85A / FM999C**; or AXA witness for agent systems | **FM DS 2-0** §2.6/§2.7 + App. C forms; **FM DS 5-32** App. C/D; AXA **PRC.13.0.5** for agent only |
| **5. Owner turnover records** | Training, O&M, baseline register, software copy, password change, physical release disconnect | Owner standard (may raise); FM85A instruction-materials line; DS 2-81 differential baseline consumer |

**Dual-acceptance statement (required on FM jobs):** App. A of DS 2-0 defines the FM AHJ as the appointed Field Engineering representative. Schedule **two** submittal reviews and **two** acceptance acts. FM §2.6.1.2/.1.3: drawings/calcs/specs to FM **before installation starts**, and again on every revision; §2.7.2.1/.2.2: FM acceptance of that package is a **precondition** of the acceptance test. Local FM office (§2.6.6) decides what FM witnesses — settle on building 1 of a phased campus.

Where IBC §909 engineered smoke control exists, a **third** authority (owner-retained independent special inspector) may gate the permit and sit upstream of NFPA 4 IST — flag `[V]` / AHJ; normally **not** a single-story data hall, but negative-test / supervise-the-outcome / blast-radius rules transfer regardless.

### 3.4 Parameter union — acceptance acts separately

Do **not** MAX whole sheets.

| Parameter | Election | Union rule |
|---|---|---|
| **A. Plan-review hold** | Who must accept drawings/calcs before install | Any layer that requires it (FM §2.6; agent DS 4-9 §2.4; AHJ permit). Dual = both tracks. |
| **B. Individual acceptance suite** | Which subsystem certificates | Code floor forms **plus** insurer supplements. Never drop AHJ certificates on an FM job. |
| **C. DC numeric proofs** | Heated-wire / ASD / ≤30 s / App. D | **FM DS 5-32** controls where FM-insured. Code has FA acceptance but **not** the DC heated-wire method. SI/NI clock facts → `comparison-only`. |
| **D. IST scenarios** | End-to-end C&E scenarios | NFPA 4 + owner; FM complements (throttled per-circuit re-trip DS 2-0 §2.7.3.3.6) — does not replace NFPA 4. **Consume C&E** — never invent a canned hall IST. |
| **E. Forms / certificates** | FM85A, FM999C, NFPA 13/24 certificates, NFPA 72 ROC | Most complete set among applicable layers. |
| **F. Baseline capture list** | What IST must record for lifetime differential ITM | Union of DS 2-81 differential consumers + owner CMMS. |

### 3.5 FM DS 5-32 App. C — heated-wire (VEWFD)

Emit only when detection = VEWFD/ASD on an FM (or dual) job. Status the script line.

**Pass criterion (FM DS 5-32 Jan-2026 App. C, Table C.2):** Alert **or** Pre-Alarm within **120 s** of the **end** of the heated-wire period.

**Script lines (minimum):**

1. Normal programmed sensitivity; **verification / time-delay disabled during test**, then **re-enabled before leaving**.
2. Run **fans ON and fans OFF**.
3. ≥**3×** per HVAC condition (or owner-raised count).
4. Record wire option used (shop notes carry Mod. BS 6266 and North American variants — cite the project’s specified apparatus; do not invent amperage if unspecified → `[V]`).
5. **Does not replace** NFPA 72-2025 functional / ASD transport-time acceptance — **run both**.

**ASD transport:** ≤**60 s** from most remote port to detector (FM DS 5-32 §2.4.2.2.7).

### 3.6 ≤30 s water-delivery proof — hand-off, don’t re-screen

**Criterion (FM DS 5-32 Jan-2026 §2.4.3.2.1.2(D) / §3.3.3.2.4):** ≤**30 s** to the **single most remote sprinkler** / test point. Recommend a **2 in.** test discharge line above the preaction valve. Applies on company **dry / DI** (and wet companion with a dry clock) when FM controls. Wet-only with no dry clock → N/A for this gate (say so).

| This Skill does | This Skill does **not** |
|---|---|
| Name the **endpoint** (design pressure at remote sprinkler, not first water) | Run the design-stage volume / QOD / zone-split screen |
| Require a **witnessed live** remote-point timing test for a **new** hall | Accept a hydraulic calc alone as the new-hall proof (calc = corroboration; FM accepts calc only where as-built piping matches the model — §3.3.3.2.4) |
| Capture trip time + trip-point air + remote pressure ramp on the baseline register | Invent gallons, transient allowance, or a listed-program name |

**Status rule:** live witness → may `grounded`; calc-only → ≤ `provisional` / never substitute on new hall; design screen → `handoff` to water-delivery.

**Hand-off:** design-stage volume/QOD election → **dry-preaction-water-delivery-screen**. ITM lifetime remote-area check → **itm-design-for-testability** (writes 30 s + remote-end into the ITM spec).

**FM85A QOD rule:** record time to minimum sprinkler pressure **WITH** and **WITHOUT** the QOD as separate entries — plan **two** measurements (or an explicit FM waiver). Endpoint language (DS 2-0 App. A): pressure at most remote sprinkler **reaches or surpasses design pressure**.

**Show-and-verify (screen corroboration only — not a substitute for live timing):**

```
V_total_gal = Σ[π · (D_i_in² / 4) · L_i_ft] · (12/231) # actual ID, every pipe valve→remote
t_fill_s = 60 · V_total_gal / Q_remote_gpm
accept if t_fill_s + valve_transient_s ≤ 30
```

Flag `V_total`, `Q_remote`, and transient `[SYN]` / `[V]` unless caller-supplied. Prefer witnessed live test. **This fill screen is not a transit model** — delivery = trip + transit (Nam / FM Global 2008; KB dry-pipe note Run-652) and 60·V/Q over-predicts transit ≈2–5× on well-configured systems. Use it only as a conservative corroboration; a 60·V/Q fail is not a witnessed fail.

**Per-zone witness record (DI with an electronic accelerator — method from the Arvada retest `[SYN]`):** operate detection **and** open the remote test connection together; record (a) accelerator activation time, (b) valve-open time, (c) water-at-RTC time; RTC orifice = the **smallest sprinkler orifice in the zone**. Keep (a) as the accelerator trend baseline for ITM. Accelerator fault = zone impaired for the FM criterion.

**SI measurement gap — `comparison-only` corpus fact (not a controlling path):** DS 2-0 §2.7.3.3.4(B) names non-interlock and double-interlock in the trip-pressure/ramp-time sentence; §2.6.5.4 still requires delivery-time documentation at plan review for **any** preaction. Under company fence, controlling halls are wet/dry/DI — write DI/dry measurement into the ITP per sheet. If the caller forces SI-as-BOD → **Stop `RFI-variance`** (do **not** continue “On SI halls…” as controlling instruction). SI gap prose and FM “no interlock-type qualifier” stay **`comparison-only` evidence only**.

### 3.7 FM DS 5-32 App. D — Test Mode (power isolation)

When power-isolation = `y`:

1. Put the disconnect-control panel in **Test Mode** — prove triggers and FP signaling **register without firing** power-off outputs.
2. Then run **ONE** controlled live outage scenario in an **approved** window (Fig. D.1 sequence posture).
3. Re-incorporate + re-test after any later power / HVAC / FA / FP change.
4. Prove power-isolation does **NOT** fire on Alert (or Pre-Alarm) unless **programmed** for that threshold.

Do not invent MDP/UPS tag lists — consume from C&E / assignment packet. Means / architecture detail → handshake to **power-isolation-disconnect-control**.

**Latched no-auto-restart (ESS / where the C&E carries it):** prove each isolation trigger latches, that utility return or a BMS self-clear does **not** re-close, and that exhaust + sprinkler supply stay in service (NM ESS NAR package `[SYN]` method). For ESS rooms, **no water shutoff and no restart until a cooling / removal plan exists**; fire watch until damaged ESS is removed (FM RW000029 pp. 56, 62, 79).

### 3.7b Releasing-panel program verification (witness lines — consume the C&E; do not rewrite it)

Before the DI functional test, photograph / print the **as-loaded** program and check (KB *Releasing control unit* Run-415/420/421; WY DI El/El program-verification package `[SYN]` 26-item checklist = method):
1. **Brand + program # + drawing #** match the C&E — Viking VFR-500 numbering ≠ Potter G3 numbering; Program #n alone is not acceptable (Program 0 edits can change any template).
2. **Manual Release zone:** none, or retyped **DETECTION** — on G3-family El/El / SureFire programs a Manual Release zone overrides the interlock by default. Witness: pull station with pipe pressurized → **must not release** (unless a written owner + FM decision accepts the override).
3. **No abort on water:** no IDC typed abort; **SUP 1 retyped Supervisory** (printed "SUP 1 defaults to abort" on some G3 water templates) — witness SUP 1 → supervisory only.
4. **Soak = CONTINUOUS; pre-discharge = 0 s.**
5. **Low Air Alarm alone → supervisory**, never general alarm.
6. Monitored solenoid: coil removed → supervisory/impairment on its own IDC.
7. Failsafe trims: NO block solenoid **de-energized in normal standby**; total power loss (AC + battery) → the trim degrades to sprinkler-only pneumatic release — witness per the OEM sheet.

### 3.8 FM DS 2-0 field protocol highlights + FM85A / FM999C

**Hold points to schedule:**

| Hold | Cite |
|---|---|
| FM plan review before install + on every revision | DS 2-0 §2.6.1.2/.1.3 |
| Delivery-time documentation at plan review (dry/preaction/deluge) | §2.6.5.4 |
| C&E / interlock method of actuation as plan-review specs | §2.6.4.10/.11 |
| FM acceptance of package before acceptance test | §2.7.2.1/.2.2 |
| Local FM witness scope settled | §2.6.6 |

**Acceptance numbers (DS 2-0 §2.7 / FM85A):**

| Test | FM criterion |
|---|---|
| Hydrostatic | ≥**200 psi (13.8 bar) / 2 h, no loss**; or working+50 psi if working >200 psi; gauge at **low point** |
| Pneumatic (dry/preaction) | **40 psi / ≥24 h**, loss ≤**1½ psi (0.1 bar)** collective; lowest nominal space temp if can go below 32 °F |
| Waterflow alarm | Alarm ≤**60 s** after initiating flow through ITC |
| Trip conditions | All supplies incl. fire pumps **in service**; all control valves fully open; witnessed by **owner’s representative** |
| Per-circuit re-trips | After successful full-flow trip: each detection circuit + each manual station with control valve **throttled** (§2.7.3.3.6) — proves C&E without flooding the hall |
| Coupon rule | Written confirmation all quick-connect cutouts removed — else full flush + visual |

**FM85A / FM999C (DS 2-0 App. C, mandatory per §2.6.5 / §2.7.2):**

- Default witness on FM85A = **owner’s representative, not FM** — name the role contractually; separately confirm whether FM attends.
- Impairment closure is a certificate line: *system left in service; date left in service with all control valves open*.
- Releasing questions on the form: detection type; single/double/non-interlock; air-pressure supervision; manual operation of auto-release valve; if electric — circuitry supervised per **DS 5-40**; panel + solenoid make/model. Under company fence, controlling BOD answers are wet / dry / **DI**; SI/NI form options are comparison annotations only if AHJ/FM form still asks — never company election.
- **FM999C** certifies **Protection Available … after hose deduction** (flow/pressure/density or pressure over demand area + **duration available**) — design-verification twin of the supply curve. White-space ceiling-only skips in-rack blocks; storage/staging buildings do not.
- Forms inside the sheet carry **©2010** markings — `[V]` portal for newer standalone FM85A/FM999C before live issue.
- Underground flush certificate **FM85B** is named on FM85A and is **not** in DS 2-0 → procurement line `[V]`.

**AXA agent track (only if special-hazard listed as handoff):** PRC.13.0.5 — carrier witnesses; compares as-built to **its** reviewed drawings; total-system test; GC (or purchaser’s contracting officer) owns the orderly sequence + pre-test briefing. **Abort switches expected on gaseous, prohibited on white-space preaction** — prove abort affects only the agent system when one panel serves both. Foam → Stop. Mist → PRACTICE REFUSED.

### 3.9 Recommended sequence (new FM-insured **company** wet \| dry \| DI hall)

Tailor to the STS-elected mix. SI a prior site sequence title in the acceptance KB note = **`comparison-only` / historical pointer** — never the controlling sequence title.

1. CD closeout — OPR/BOD/SOO/Cx plan [CODE NFPA 3-2024 §5.2.3.2, pull 3-01]/integrated matrix/shop drawings/software ownership/witness plan aligned (company wet\|dry\|DI BOD).
2. Underground (NFPA 24) — flush + hydro → UG certificate / FM85B track.
3. Aboveground (NFPA 13 Ch.29) — hydro + operational + supervisory + waterflow → aboveground certificate.
4. Fire pump (NFPA 20 Ch.14) — three-point (churn / 100% / 150%-or-max) vs certified curve; ATS peak-load transfer.
5. Fire alarm (NFPA 72) — point-to-point, notifications, supervisory/trouble, interface logic → ROC + software copy.
6. FM App. C heated-wire (if VEWFD).
7. ASD transport ≤60 s.
8. App. D Test Mode, then one controlled live isolation scenario (if power-isolation = y).
9. Live ≤30 s water-delivery proof (remote instrumented endpoint) when dry/DI clock applies.
10. NFPA 4 integrated scenarios (**consume** C&E; include restoration) — never invent a canned script.
11. FM85A + FM999C complete; throttled per-circuit re-trips; as-built vs accepted drawings.
12. Commissioning closeout — issues log, training, manuals, baseline register, password change, physical release disconnect.

Insert readiness gates (pre-FAT distinct from FAT) for major equipment — aborting a witnessed test for a pre-checkable condition burns a witness slot.

### 3.10 Baseline register (FM ITM is differential)

Specify capture **now**; ITM Skill consumes later. Minimum per system (status each item; fail if would be `unspecified`):

- Full-flow trip **time** and trip-point **air pressure**
- Measured air-leakage rate (FM criterion **≤1½ psi / 24 h from 40 psi**)
- Three-point pump curve with rpm + amperage vs nameplate FLC at 150%
- Base-of-riser **and** hydraulically remote pressures for every company wet/dry/DI deluge/spray system that applies; **mist-system remote pressures → `PRACTICE REFUSED` / `handoff` only** — do **not** imply mist is company-accepted
- Detection response times (ASD transport; heated-wire results)
- Turns full-open → full-shut for **every** control valve
- Maintained hydraulic-demand register (gpm @ psi at BOR)
- Door-fan result for every clean-agent enclosure (handoff adjunct when present)
- As-programmed zone→output map (printed/photographed from panel), NORMAL vs CROSS ZONED, must-not-release negatives; brand + program # + drawing # + firmware; manual-release / SUP 1 / soak settings as witnessed (§3.7b)
- Four-contact point list proven **at the receiving end** (alarm / supervisory / trouble / waterflow)
- Remote-end ≤30 s delivery time — **without this, DS 5-32 can never again be proven** (when dry/DI + FM)
- Nitrogen originally-installed y/n (baseline / ITM eligibility flag only)

If baseline status would be `unspecified`, the packet **fails this item** and says so.

### 3.11 Flags, deltas, honesty

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented project quantities (hall ft², transient seconds, witness names you assumed). a prior site ~28k / ~14 MW defaults are forbidden — if cited, mark `[SYN]` comparison-only structure. |
| **`[V]`** | Unpinned primary: licensed NFPA 13-2025 Ch.29 subsection numbers (hydro / air / trip now held: [CODE NFPA 13-2025/2022 §29.2.1, §29.2.2.1, §29.2.3.2; 2019 §28.2; pull 13-04]); NFPA 72 Ch.23 releasing §§; NFPA 25 (not used as acceptance); FM85B form; newer FM85A/999C portal revs; §909 applicability; owner standard. |
| **Status tokens** | `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` / `PRACTICE REFUSED` as defined in §1.4. |

**Δ vs NFPA 13-2025:** FM adds plan-review hold, throttled per-circuit re-trip, coupon rule, QOD-without timing, design-pressure endpoint, FM85A/999C. Hydrostatic/pneumatic **numbers** look familiar (200 psi/2 h; 40 psi/24 h/1½ psi) — procedural deltas dominate; numbers held [CODE NFPA 13-2025/2022 §29.2.1.1 (200 psi / 2 h), §29.2.2.1 (40 psi / 24 h / 1½ psi); 2019 §28.2.1.1, §28.2.2.1; pull 13-04].

**Δ vs code IST/FA floor:** code gets installed + individually accepted + documented + integrated-tested. **FM DS 5-32 adds** 120 s heated-wire, 60 s ASD, 30 s remote water, App. D Test Mode.

**Do not** paste outline ~28,000 ft² / ~14 MW / a prior site as defaults. Worked package for ≤30 s exists — consume **method**, not synthetic numbers. Do **not** invent full NFPA 4 IST scripts. Do **not** treat NFPA 25 / one city ITM intervals as acceptance acts.

---

## 4. Output

A **construction-completion acceptance / IST program packet** (markdown).

**Write it only to the path the caller names.** If unnamed, return it in the response and stop.

**Minimum contents:**

1. **Hard-scope gate + status register** — company wet\|dry\|DI fence; SI/foam/mist disposition; tokens on gate / five pillars / App. C/D / ≤30 s / forms / baseline items.
2. **Edition-pin block** — enforced vs latest for 3/4/13/20/24/72; FM DS 5-32 Jan-2026; FM DS 2-0 Oct-2021/IR Jan-2024; carrier; owner posture.
3. **Inputs echoed** — packet + STS election token + matrix rows + C&E present, controlling system mix (`wet`/`dry`/`DI` only), carrier, detection, power-isolation, special-hazard list. No invented campus.
4. **Five-pillar stack** with N/A reasons where gated off; status per pillar.
5. **Dual-acceptance / hold-point schedule** (FM + AHJ; §909 third authority if triggered).
6. **App. C heated-wire script** (or N/A) + ASD ≤60 s.
7. **≤30 s proof plan** + explicit hand-off to dry-preaction-water-delivery-screen; endpoint = design pressure at remote sprinkler; QOD with/without; status rule (live may grounded; calc ≤ provisional).
8. **App. D Test Mode script** (or N/A); no invented MDP/UPS lists.
9. **FM85A / FM999C checklist lines** + owner-rep witness naming.
10. **Baseline register** capture list + pass/fail if unspecified; mist remote pressures refused/handoff.
11. **Recommended sequence** tailored to company wet\|dry\|DI (SI a prior site sequence = comparison/historical only).
12. **Reciprocal handshake rows** + open `HAND OFF` lines.
13. **Δ vs NFPA 13-2025** and **Δ vs code IST/FA floor**.
14. **`[SYN]` / `[V]` / status register.** Honesty: outline spine only; worked ≤30 s package is method-only — no synthetic hall defaults; NO PLACEHOLDER.

Do **not** emit: ITM interval tables, C&E rewrite, density×area `calcs/fp`, pump nameplate selection, CAD, prior job files retrieval, KB writes, invented NFPA 4 scripts, or PLACEHOLDER text.

---

## 5. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess:

1. Assignment packet missing → **not a Stop** (packet optional); proceed and flag `ASSUMED`.
2. **Missing STS company election token** (`wet`\|`dry`\|`DI`) or election `unresolved` → `unresolved` / `handoff`.
3. **Missing matrix** acceptance/carrier/system-family rows when dual-carrier / when required → `unresolved`.
4. **Missing releasing C&E / SOO** (or “TBD”) → `unresolved`.
5. **SI/NI** (or other prohibited preaction) presented as **BOD** → `RFI-variance`. Do not silent-swap DI.
6. **Foam** as BOD → Stop. **Mist** as acceptance/design path → `PRACTICE REFUSED` / `RFI-variance`.
7. **Unpinned carrier.**
8. **Unpinned AHJ editions** when a sealed packet is requested.
9. Caller asks to **rewrite C&E**, emit **ITM interval tables**, run **density×area**, or **size a pump**.
10. No C&E to consume → build the **NFPA 4** script against a stated `ASSUMED` C&E basis (flagged) — never a canned hall IST presented as project C&E.
11. Caller asks to treat **NFPA 25** (or one city/ITM intervals) as acceptance.
12. Caller asks to paste **a prior site** ~28k ft² / ~14 MW / SI hall defaults, or to invent MDP/UPS lists from unrestamped power-isolation.
13. Caller asks to mark **calc-only** ≤30 s as `grounded` live acceptance proof, or to skip the water-delivery hand-off on a new hall.
14. Dual-carrier with **no** controlling acceptance rows and missing insurer values — do not silent-swap FM App. C onto an AXA-only job or drop AHJ certificates on an FM job.
15. Caller asks to write outside the caller-named path.
16. **PLACEHOLDER** invent anywhere in the packet.

---

## 6. Citations (section **and** edition — do not invent)

Shop codebook **by title**.

**Design practice / method**

- *Design practice* — 3-layer, most-stringent, Δ vs NFPA 13-2025; cite section **and** edition.
- *Enforced-vs-latest edition resolver and reference pins*.
- *Acceptance, commissioning and integrated systems testing* — five-pillar stack; FM dual AHJ; App. C/D; FM85A/999C; baseline = lifetime differential (**mined**).

**Sheets / standards**

| Claim | Pin |
|---|---|
| Five-pillar stack + sequence | Acceptance note TL;DR; NFPA **3-2024**, **4-2024** (**mined**) |
| ≤30 s to most remote sprinkler | FM DS **5-32 Jan-2026** §2.4.3.2.1.2(D), §3.3.3.2.4 (**mined**) |
| Heated-wire ≤120 s; fans on+off | DS **5-32** App. C / Table C.2 (**mined**) |
| ASD transport ≤60 s | DS **5-32** §2.4.2.2.7 (**mined**) |
| App. D Test Mode | DS **5-32** App. D (**mined**) |
| FM plan-review hold; acceptance preconditions | DS **2-0** Oct-2021/IR Jan-2024 §2.6 / §2.7.2 (**mined**) |
| Throttled per-circuit re-trip | DS **2-0** §2.7.3.3.6 (**mined**) |
| SI measurement gap (comparison-only under company fence) | DS **2-0** §2.7.3.3.4(B) + §2.6.5.4 (**mined**; status `comparison-only`) |
| Hydro 200 psi/2 h; pneumatic 40 psi/24 h/1½ psi | DS **2-0** §2.7.3.2; FM85A p.175 criteria (**mined**) |
| FM as AHJ | DS **2-0** App. A (**mined**) |
| FM85A / FM999C mandatory | DS **2-0** §2.6.5 / §2.7.2; App. C forms (**mined**) |
| QOD-without as separate entry; design-pressure endpoint | FM85A dry/auto-release block; App. A water-delivery-time definition (**mined**) |
| Differential ITM vs acceptance record | DS **2-81** Apr-2019/IR Oct-2021 Table 2c items 13–14; §3.1.6.1 F (**mined**) |
| NFPA 4 modification retest 10%/max 50 | NFPA **4-2024** §6.4.3 |
| Agent carrier acceptance | AXA XL **PRC.13.0.5 2020** (special extinguishing only; handoff) |
| FM clean-agent door fan mandatory | DS **4-9** Oct-2018/IR Jul-2023 §2.5.1.2.1 (handoff) |
| §909 third-authority special inspector | AHJ special-inspection note / acceptance run-113 addendum (**mined**) |
| Company wet\|dry\|DI fence; SI Stop | Peer Hard-scope bar (STS / matrix / multizone / nitrogen / water / C&E / ITM) |
| a prior single-interlock Cx/IST spine | worked examples outline a worked example — **`[SYN]` comparison-only** structure |
| ≤30 s verification method | worked examples worked `...-or__preaction-30s-delivery-verification` — **`[SYN]` method only** |

**Absent (name the hole):** licensed NFPA 13-2025 Ch.29 subsection text; NFPA 72-2025 §23.11.x exact numbering; FM85B form body; newer standalone FM85A/999C if portal-updated; stand-alone NFPA 4 IST script library independent of C&E; company wet\|dry\|DI fence inside the acceptance KB note itself.

---

## 7. Design practice

1. **Three-layer, most stringent, per acceptance act.** Code floor forms + IST process; insurer DC proofs and FM dual-AHJ hold points; owner may raise witnesses/scenarios. Report **Δ vs NFPA 13-2025** and the code IST/FA floor.
2. **Per-parameter, not per-layer.** Never let FM substitute for AHJ certificates or vice versa.
3. **Company fence.** Controlling BOD = **wet | dry | DI** only. SI/NI → Stop + `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. Never silent-swap SI→DI.
4. **Upstream (packet optional; gaps → `ASSUMED`, not a Stop).** Packet + STS wet\|dry\|DI + matrix acceptance/carrier/system-family rows (when dual-carrier) + releasing C&E — missing any → proceed with `ASSUMED` (flagged), not a Stop. This Skill elects acceptance acts / scripts / forms / baseline, **not** system family.
5. **C&E is an input.** Missing C&E is **not a Stop**: state an `ASSUMED` C&E basis (flagged) or run `preaction-releasing-c-and-e-soo` first. Do not silently invent NFPA 4 scripts from habit.
6. **Acceptance ≠ ITM.** NFPA 25 keeps the accepted system reliable after turnover — never an acceptance basis; do not import one city/ITM intervals.
7. **Show-and-verify + status register.** Live ≤30 s timing preferred (`grounded` only when witnessed); volume screen math only as corroboration ≤ `provisional` with `[SYN]`/`[V]` flagged. Status every run on gate / pillars / App. C/D / ≤30 s / forms / baseline.
8. **Honesty + NO PLACEHOLDER.** No synthetic hall defaults (a prior single-interlock spine = comparison-only structure). Worked ≤30 s package = method only. Caller-path-only writes. No PLACEHOLDER invent.
9. If notes conflict, **most-stringent wins** and both sources stay visible.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Fire-pump controller acceptance: start-count union per source, every remote signal witnessed at the FACP (incl. ATS-alternate, phase loss), refuse-list settings verified | `fire-pump-controller-configuration-and-supervision` (feeds this packet) |
| Assignment packet / prior job files | the input packet (prior) — consume only |
| System-family election wet\|dry\|DI | `suppression-technology-selection` — consume only |
| Dual-carrier acceptance/carrier BOD rebuild | `most-stringent-basis-matrix` — consume only |
| Releasing C&E / SOO authorship | `preaction-releasing-c-and-e-soo` |
| Design-stage ≤30 s volume / QOD / zone split | `dry-preaction-water-delivery-screen` |
| ITM intervals / design-for-testability levers | `itm-design-for-testability` |
| Disconnect means / Fig D.1 architecture | `power-isolation-disconnect-control` (handshake only this run; sibling unrestamped) |
| Zone count / 1:1 alignment | `multizone-preaction-zone-alignment` |
| Nitrogen medium / C / fill | `nitrogen-inerting-and-c-factor-gate` (baseline N₂ flag only here) |
| Density × area | `density-area-dry-increase` |
| Pump rated selection | `pump-envelope` |
| Occupancy / HC | `occupancy-hazard-fork` |
| CAD / drawings production | not this Skill |
| Writing into KB / worked examples / ARCHIVE / agent private trees | forbidden |

---
