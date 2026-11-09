---
name: Most stringent basis matrix
description: >-
  use this when setting or restamping a US data-center fire-protection
  basis-of-design as a per-parameter three-layer most-stringent matrix across
  adopted code, applicable insurer(s), and owner, including
  wet/dry/double-interlock system-family gating and dual-carrier reconciliation,
  before occupancy classification, density-area calculation, or pump-envelope
  work; emit a status register per row/election
  (grounded/provisional/unresolved/comparison-only/handoff/RFI-variance).
---
# Most stringent basis matrix

> **Intake rule (the engineer, 2026-10-07 — overrides any older gate wording below):** The assignment packet is optional and never a gate. Start from exactly what is given. A missing packet, a missing upstream result (STS token, matrix row, occupancy fork, density, C&E, etc.), or a missing input blank is **not** a Stop: run the upstream Skill if practical, otherwise fill the gap with a stated **ASSUMED** value (the value used + why), flag it in the output and the status register, and continue. ASSUMED is not verified. "Never invent" / "refuse invent" rules on project numbers mean do not *silently* invent: label the number ASSUMED; never present an ASSUMED value as a cited code or table value; never freeze a vendor SKU. **Company scope locks stay hard Stops and are not softened by this rule:** wet / dry / double-interlock preaction only; foam prohibited; clean agent not done (hand-away); water mist `PRACTICE REFUSED`; single-interlock / non-interlock / other preaction never the elected system (SI/NI-as-BOD → Stop + `RFI-variance`, comparison-only). Cite section and edition, use `_calc/run.py` for governed math, design to the most-stringent 3-layer basis; the engineer is the engineer of record.

Reusable US data-center fire-protection recipe. This Skill sets or restamps a prototype fire-protection basis-of-design as a **per-parameter reconciliation matrix**:

> adopted code floor × insurer A × insurer B or `n/a` × owner → most-stringent applicable result per parameter

The matrix names the controlling layer for each row, reports the directional delta versus **NFPA 13-2025**, cites section **and edition**, shows and verifies arithmetic owned by this Skill, and preserves `[SYN]`, `[V]`, and unresolved conditions.

Every run must state, for each row and each election/gate:

1. The controlling value and controlling layer
2. The rule (A–D) and any code/owner override
3. The Status-register token (`grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`)
4. Provenance (`grounded` / `derived` / `synthetic` / `verify`) and flags (`[SYN]`, `[V]`, `[U]`, conflict, handoff)
5. Directional delta versus NFPA 13-2025 where applicable
6. Required handoffs

**the engineer Way:** code is the legal floor; insurer sheet(s) and owner may raise it. Most-stringent is resolved **per parameter**, never by ranking or MAX-ing whole layers. Elect only wet pipe, dry pipe, or double-interlock preaction. SI/NI = `comparison-only`. Foam prohibited. Mist `PRACTICE REFUSED`. Cite **section AND edition**. Show-and-verify arithmetic this Skill owns. Mark invented values `[SYN]` / unpinned values `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Write **only** to the path the **caller** names.

This is the engineer Way in detail:

- Code is the legal floor.
- Insurer sheet(s) and owner standard may raise the basis where applicable.
- Most-stringent is resolved **per parameter**, never by ranking or MAX-ing whole layers.
- Enforced edition is not the same as latest edition.
- Silence is not permission.
- A missing or unmined primary source is not evidence.
- Invented project values are `[SYN]`.
- Unverified, unpinned, or unmined requirements are `[V]`.
- A requirement that cannot yet be closed remains unresolved; it is never silently converted into a final code-compliant value.
- Every matrix run emits a **Status register** with tokens `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` on every row and every election/gate.

This Skill is not a space-list classifier, density-area calculator, pump-envelope calculator, hydraulic-tree generator, CAD tool, or assignment-packet rebuild.

Write output only to the path the caller names. Do not write to `KNOWLEDGE_BASE`, `EXERCISES`, `_pruner`, `_surveyor`, `_engineer`, or `ARCHIVE`.

---

### 1.0 Country/edition gate at intake (model A — stop-vocab normalize 2026-11-04, staged)
Pin country + enforced edition per row first (enforced ≠ latest). Missing pin → `ASSUMED` (value + why) + flag, continue. US → §4.2 resolver; Canada (BC/AB/ON) → §4.2b pins + NEG-CA list (no invented ULC/CSA/OBC/BCFC/VBBL text; unheld → `unresolved` + RFI, not a run-Stop). Company scope locks stay hard.

## 1. Hard scope gate

### 1.1 Allowed system-family elections

This Skill may elect only:

1. **Wet-pipe sprinkler**
2. **Dry-pipe sprinkler**
3. **Double-interlock preaction**

The caller must identify which allowed family is being considered or must provide enough evidence for this Skill to resolve it.

### 1.2 Comparison-only system evidence

The following may appear in carrier or owner source columns as comparison evidence, but this Skill must not elect them:

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type
- Any other suppression family outside the allowed wet/dry/double-interlock scope

FM DS 5-32’s ranking remains **`comparison-only`** evidence:

> Wet → non-interlock → single-interlock → double-interlock last

This is a carrier preference ranking, not a company election permission. AXA XL’s single-interlock preference and double-interlock penalty remain comparison evidence only. Status on ranking / preference rows: `comparison-only`.

If the caller requires single-interlock, non-interlock, or another prohibited preaction type as a **company election** / BOD:

1. Record the requested election.
2. **Stop** the system-family resolution.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. SI/NI may appear only as a **`comparison-only`** evidence row (never the controlling election).

### 1.3 Double-interlock treatment

Double-interlock is **carrier-disfavored but owner-electable**. Do not describe it as prohibited by FM or AXA XL.

If double-interlock is elected within the allowed company scope, carry its consequences as separate matrix rows:

- Dry-design area or other cited area lever
- Water-delivery-time proof
- Supervisory air or nitrogen
- Corrosion and pipe-material controls
- Dry/preaction friction-factor basis
- Downstream fire-water demand and supply consequences
- Pump, tank, loop, and zoning handoffs

Do not treat an owner’s double-interlock election as automatically more stringent on every axis. It may increase hydraulic demand while reducing availability or delaying water delivery. Resolve system election, hydraulic area, delivery time, and reliability as separate parameters.

### 1.4 Special-hazard scope fence

This Skill does not elect or design:

- Foam or foam-water systems
- Water mist
- Clean-agent or hybrid systems
- Condensed aerosol
- Oxygen-reduction systems
- Dry chemical
- Other special-hazard media

**Foam is prohibited for this company scope.** If an occupancy or hazard sheet appears to require foam as election/design/BOD:

1. Record the cited requirement.
2. **Stop** foam design here.
3. Return an `RFI-variance` / company-fence gate.
4. Hand off to the applicable special-hazard Skill (`handoff`).

**Mist is `PRACTICE REFUSED`.** FM DS 5-32 may identify FM Approved water mist as a possible terminal in a flowchart, but that does not authorize this Skill to elect or design mist. If the caller requests mist as election/design/BOD:

1. Record that FM may permit a cited branch.
2. Record company refusal.
3. **Stop** mist design here.
4. Return status `RFI-variance` (company-fence) with companion `PRACTICE REFUSED` / `handoff`.
5. Route to the special-hazard and `suppression-technology-selection` Skills.

Clean-agent or other special-hazard questions may be recorded as:

- `not this Skill`
- `prohibited by the applicable carrier or owner`
- `handoff` (Status-register token)
- `out of scope`

Do not perform their quantity, concentration, hold-time, nozzle, enclosure, or acceptance design here. Status on record-only special-hazard rows that are not company elections: `handoff` or `comparison-only` as applicable — never a controlling BOD election in this Skill.

---

## 2. Inputs

The caller must supply:

1. **Parameter list**

   If omitted, do not stop: use the suggested default rows below and flag the list `ASSUMED`.

   Suggested default rows, extend only when a cited source requires them:

   - System family / allowed election
   - Carrier system preference or ranking, as comparison evidence
   - Density / area
   - Hose allowance and duration
   - Water-delivery time
   - Head temperature / response
   - Ceiling height or cap
   - Compartmentation rating
   - Compartmentation extent
   - Door rating
   - Damper trigger and rating
   - Detection or VEWFD
   - Power isolation
   - Leak detection
   - In-rack Li-ion barrier / kWh gate / cooling-not-gas
   - In-rack Li-ion density uplift
   - Supervisory air or nitrogen
   - Pipe material / corrosion controls
   - Fire-water demand consequence, without running the demand calculation
   - Required handoff to density-area or pump-envelope work

   A special-hazard row may be included only as a record-only applicability or prohibition row. It must not become a design election in this Skill.

2. **Jurisdiction-instrument register**

   The caller must supply, or the runner must resolve, the jurisdiction information in §4.

   A generic 2024-cycle table is not an enforced-edition pin.

3. **Carrier A**

   Supply:

   - Carrier identity
   - Sheet title
   - Sheet revision or edition/date
   - Applicable sections or pages
   - Confirmation that the carrier actually controls the job or phase

4. **Carrier B**

   For a dual-carrier or ambiguous job, supply the same information for Carrier B.

   For a single-carrier job, explicitly set Carrier B to `n/a`.

   A missing second carrier sheet on a dual-carrier job is not a Stop: carry the row as `ASSUMED` (state the value used + why), flagged. Do not silently invent a missing value.

5. **Owner layer**

   Supply the owner standard or written project direction if available.

   If the owner standard is NDA or not in hand:

   - Keep the owner column.
   - Use structure only.
   - Do not invent numeric owner requirements.
   - Mark the applicable cell `[V] owner standard not in hand`.
   - Treat the row as conditional or unresolved where the owner could change the election.

6. **Source-type and sheet-routing information**

   Identify whether each source is:

   - Adopted code or local administrative instrument
   - Occupancy-specific insurer sheet
   - General installation sheet
   - Component sheet
   - Hydraulic or calculation-method sheet
   - ITM or acceptance sheet
   - Stand-alone insurer sheet
   - Owner standard
   - Public owner material
   - Secondary summary
   - Unmined root PDF or pointer only

7. **Rule selector**

   The caller may preassign Rule A, B, C, or D. If omitted, assign exactly one matching rule per row and record it.

   Do not invent a fifth resolution rule.

8. **Caller output path**

   Required for file output.

   If no path is named, return the matrix in the response (output-routing rule, not a design Stop). Do not choose a corpus location.

Optional inputs may include:

- Assignment-packet note list
- Existing BOD requirements matrix
- Occupancy-hazard-fork result
- System-family hint limited to `wet`, `dry`, or `double-interlock`
- In-rack Li-ion energy data
- Existing carrier reconciliation matrix
- Existing jurisdiction worksheet

Consume these inputs; do not silently rebuild work owned by another Skill.

---

## 3. Four resolution rules

The resolution logic is not a single numerical MAX. Carriers and layers may constrain different axes.

**Legend:**

- **Rule A** — single quantitative source controls
- **Rule B** — same axis → more-conservative value
- **Rule C** — different axes → union
- **Rule D** — prescriptive requirement satisfies a general requirement

### Rule A — single quantitative source controls

If one carrier supplies a number and the other carrier is silent or qualitative, use the cited number provisionally.

Examples:

- FM supplies density and area; AXA XL supplies only Ordinary Hazard Group 1.
- FM supplies hose allowance and duration; Carrier B is silent.
- FM supplies a delivery-time limit; Carrier B is silent.
- A component sheet supplies architecture but not demand: route demand to the named demand source instead of inventing it.

Carrier silence is not zero and is not permission. Record the silence and the source that supplies the operative value.

### Rule B — same axis → more conservative

If two sources state values on the same axis, select the more stringent applicable value.

Examples:

- Two ratings on the same rating axis
- Two maximum heights
- Two minimum durations
- Two required detection conditions
- Two leak-detection requirements

Do not apply Rule B to values that only appear similar but measure different things.

### Rule C — different axes → union, never blend

If sources constrain different attributes of one parameter, retain both at their applicable levels.

Examples:

- Higher compartmentation rating plus greater full-height extent
- FM QR head requirement plus AXA heat-damage threshold
- Rating, extent, and fire-alarm damper trigger
- Carrier area lever plus carrier nitrogen requirement

Never average different carrier levers.

For double-interlock, for example:

- FM DS 5-32 may redesign the system as dry using `3,500 ft²`.
- AXA XL may apply `+30%` to a different base, producing a different area.

Do not average the two areas, stack them without authority, or treat one as a general replacement for the other.

### Rule D — prescription satisfies general requirement

If one source prescribes a specific means that satisfies another source’s general requirement, the prescription controls that means.

Examples:

- FM-Approved VEWFD satisfies AXA XL’s fixed-photoelectric-or-air-sampling alternative where the carrier scopes are compatible.
- FM App. D power-isolation architecture supplies detailed means for AXA XL’s general hall-and-air-handler de-energization requirement.
- A cited carrier barrier prescription may satisfy a less-specific owner or carrier separation requirement.

A hard prohibition is also a prescription. For example, where FM DS 5-32 §2.4.3.6.4.1 prohibits clean agent or hybrid protection in the applicable distributed-Li-ion room, record the prohibition and route special-hazard design elsewhere.

### Never MAX whole layers

Wrong:

> “FM is stricter, so use FM for every row.”

Correct:

- FM 2-hour DP-to-DP rating
- AXA XL full-height slab-to-deck extent
- AXA XL fire-alarm damper trigger
- FM quantitative density where AXA XL supplies no density
- Owner requirement only where project-issued evidence supports it

The controlling layer must be named separately for every row.

---

## 4. Jurisdiction and edition resolver

Resolve the enforced code before filling code-floor cells.

Use the canonical resolver note:

`enforced-edition-resolver-and-reference-pins.md`

The resolver requires:

1. Permit address
2. Permit filing date and effective-date path
3. State-adopted IBC, IFC, and NEC editions
4. State amendments and effective dates
5. Local ordinance and local amendments
6. Local transition rules or republication
7. Actual adopted integrated code book
8. IFC Chapter 80 / IBC Chapter 35 edition pins
9. Any direct NFPA or NEC adoption outside the I-Codes
10. Separate NEC resolution
11. Administrative overlays:
    - Bulletins
    - Plan-review guides
    - Adopted checklists
    - Emergency rules
    - Appeals or official interpretations
12. Contractual applicability of insurer and owner requirements
13. Delta reporting versus NFPA 13-2025

### 4.1 Mandatory jurisdiction-instrument register

Emit a register before the matrix:

| Field | Required entry |
|---|---|
| Permit address | Exact jurisdiction and incorporated/unincorporated status |
| Permit date | Filing date and applicable transition path |
| Building AHJ | Name and adopted instrument |
| Fire AHJ | Name and adopted instrument |
| Electrical AHJ | Name and adopted instrument |
| State code | Edition, adoption instrument, effective date |
| Local code | Ordinance, amendment, effective date |
| Integrated code | Actual adopted book or official text |
| NFPA pins | Directly adopted or Chapter 80/35 referenced editions |
| NEC pin | Separately resolved edition and instrument |
| Administrative overlays | Bulletins, checklists, interpretations, appeals |
| Carrier applicability | Contractually binding carrier and sheet |
| Owner applicability | Project-issued standard, written direction, or unresolved |
| Reverification cadence | Kickoff, DD, pre-permit, or project-specific |

Do not use an ICC adoption map or generic model-code table as the enforceable text.

### 4.2 Reference pins versus enforced pins

Under an unamended 2024 I-Code adoption, the corpus supports these reference pins:

| Standard | 2024-cycle enforced reference | Latest/delta reference |
|---|---:|---:|
| NFPA 13 | 2022 | 2025 |
| NFPA 72 | 2022 | 2025 |
| NFPA 20 | 2022 | 2025 |
| NFPA 25 | 2023 | 2026 |
| NFPA 70 / NEC | 2023 reference, resolve independently | 2026 |
| NFPA 75 | no direct Chapter 80/35 pin | 2024 |
| NFPA 855 | 2023 best-supported reference | 2026 |
| NFPA 2001 | 2022 | 2025 |

These are reference pins only until the project’s adopted instrument is verified.

Do not cite NFPA 13-2025 as the code minimum unless the AHJ separately adopted it.

The code-floor citation must use the enforced edition and enforcing instrument, for example:

- `IFC-2024 §903.3.1.1 → NFPA 13-2022`
- `Fargo ND FMC §§9-0701 / 9-0704 → IFC-2024`
- `Benton County AR Ord. O-2023-71 → AFPC 2021`
- `FM DS 5-32 Jan-2026 §2.4.3.2.1.2`

Use the exact local instrument where local amendments change the result.

### 4.2b Canada jobs — code-floor pins (restamp 2026-10-29; supersedes 2026-10-09 fence)

Canada is **unlocked** for BC / AB / ON (SK/Saskatoon still parked). The old rule "every Canadian code-floor cell = `unresolved`" is **retired**: fill the Layer-1 code floor from the pins below; a cell stays `unresolved` + RFI **only** where the pin is not held (see GAPs). Do **not** port US pins (IFC/IBC §§, US state amendments, US frost depths, IFC 100 ft FDC) into a Canadian row. Insurer and owner layers apply as written. ULC vs UL listing → `[verify]`. Company scope locks (wet/dry/DI only; foam prohibited; clean agent hand-away; mist refused) do not change at the border. No ULC hours / CSA text invented.

**Referenced-standard pins (Layer 1; Table 1.3.1.2 of each code; quote-checked 32/32 + OBC 4/4):**

| Std | NBC/NFC 2025 model | BC (BCBC 2024) | AB (NBC/NFC 2023 AE) | ON (OBC 2024 Table 1.3.1.2 / OFC 2026) | US delta baseline |
|---|---|---|---|---|---|
| NFPA 13 | 2019 | 2019 | 2019 | 2019 | 2025 |
| NFPA 14 | 2013 | 2013 | 2013 | 2013 (OBC) | 2024 |
| NFPA 20 | **2019** | 2016 | 2016 | 2016 (OBC) | 2025 |
| NFPA 24 | none in table | none in BCBC table — **BCFC GAP** | 2013 (NBC AE) | 2013 (OBC + OFC) | 2025 |
| NFPA 25 | 2020 (NFC) | per BCFC (2020) | 2020 (NFC AE) | **2017** (OFC deemed-to-comply) | 2026 |

Enforced ≠ latest: always cite the pinned edition; report the US-2025 value only as a delta row. NFPA 24-2013 text is not held → use 24-2022/2025 wording labelled **[nearest]**.

**Part 3 overlays (code-floor rows):**
- **3.2.5.9.(2)** (NBC 2025 / BCBC 2024 / AE 2023): a dry standpipe *not connected to a water supply* does not count — this is **not** a ban on NFPA 14 automatic-dry.
- **3.2.5.9.(3)**: total standpipe supply need not exceed **30 L/s** (code minimum; owner may raise).
- **3.2.5.15.(1)/(2)**: standpipe and sprinkler FDC ≤ **45 m** unobstructed to a hydrant (ON: OFC Compendium equivalent).
- **AB only — NBC 2023 AE 3.2.5.15.(3):** FDC **≥ 3 m and ≤ 15 m from the principal entrance**, in addition to ≤45 m to hydrant. Absent from NBC 2025 / BCBC 2024 (OBC [verify e-Laws]) — do not transplant.
- **3.2.5.17.(1)**: freeze protection is performance-only → method from the pinned NFPA 13 edition (see `freeze-heat-trace-fp-piping`).
- **3.2.5.18.(1)**: fire pump per NFPA 20 at that code's Table 1.3.1.2 edition.
- **NFC(AE) 2023 4.3.13.3**: fuel tank static head ≤ 70 kPa (confirmed in AE PDF).

**NEG-CA (explicit stop list — GAP-B29R1-2):**
- NEG-CA-1 inventing ULC assembly fire-resistance hours.
- NEG-CA-2 inventing CSA B139 text.
- NEG-CA-3 inventing OBC 3.2.5.7 / 3.2.5.15.(3) body not held.
- NEG-CA-4 porting US IFC/IBC FDC / frost pins into a Canadian row.
- NEG-CA-5 inventing BCFC NFPA 24 or VBBL pins.

**Still `unresolved` + RFI:** BCFC NFPA 24 pin; NFPA 24-2013 text; Vancouver (VBBL) vs BCBC; OBC 3.2.5.15.(3) existence; AB CE Code edition; ULC assembly hours; CSA B139; municipal servicing standards outside the province (Vancouver/Markham).

### 4.3 NFPA 13-2025 delta discipline

NFPA 13-2025 is the fixed delta baseline, not automatically the enforced code floor.

The following may be reported when applicable:

- Dry-system water-delivery restructuring: NFPA 13-2025 §8.2.4
- VCI systems: NFPA 13-2025 §8.2.11
- Vacuum dry or vacuum preaction: NFPA 13-2025 §8.11
- Ceilings over 30 ft (OH1 area +30%, OH2/EH density): NFPA 13-2025 §19.2.3.2.5 [CODE 2025, pull 13-03]

Dry-pipe / double-interlock +30%: [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03]. §19.2.3.2.5 is a different rule in each edition (2022 = dry-pipe / double-interlock +30%; 2025 = ceilings over 30 ft), so always cite it with its edition.

When the NFPA 13-2025 number or section is not pinned:

- Report a directional delta.
- Mark the row `[V]`.
- Do not fabricate a percentage.
- Do not present a secondary summary as a sealed code citation.

---

## 5. Within-carrier sheet precedence and routing

Apply the source’s own scope and cross-references before comparing Carrier A against Carrier B.

Canonical method:

`fm-occupancy-vs-installation-sheet-precedence-ds-5-32-and-ds-2-0.md`

### 5.1 Occupancy overlay versus installation base

For FM data-center work:

- FM DS 2-0 is the installation base.
- FM DS 5-32 is the data-center occupancy overlay.
- Where DS 5-32 states a parameter, it governs that parameter.
- Where DS 5-32 is silent, the applicable DS 2-0 default survives.
- Silence is not permission or relief.
- DS 5-32 does not replace DS 2-0 wholesale.

Use the explicit example:

- DS 5-32 §2.4.3.2.1.1 routes installation to DS 2-0 plus the recommendations in DS 5-32.
- DS 5-32 §2.4.3.2.1.2 resolves the wet-versus-dry design fork by interlock count where applicable.
- DS 2-0 remains relevant for subjects DS 5-32 does not address, such as applicable installation, obstruction, spacing, component, acceptance, or layout rules.

Do not quote DS 5-32 for a subject it does not mention.

### 5.2 Overlay can tighten or replace a base default

Do not assume that an occupancy sheet merely relaxes the base.

An occupancy sheet may:

- Tighten a base requirement
- Choose a different remedy
- Supply a category rather than a number
- Route a room to another occupancy sheet
- Replace a base default for the parameter it expressly governs

Record the source and exact parameter rather than generalizing from one sheet to another.

### 5.3 Component sheets

A component sheet may prescribe subsystem architecture while expressly disclaiming:

- Demand
- Supply capacity
- ITM
- Electrical wiring
- Hydraulic method
- Acceptance calculations

Read the component sheet’s scope fence first.

For example, FM DS 3-7 may govern pump architecture while routing demand to occupancy and installation sheets, supply reliability to DS 3-29, ITM to DS 2-81, and hydraulic or acceptance math to DS 3-0.

Do not cite a component sheet for a value it expressly excludes.

### 5.4 Stand-alone sheets

A stand-alone insurer sheet may replace a base standard for its recommendations while still:

- Deferring calculations to another standard
- Deferring human-exposure limits
- Deferring enclosure or hold-time math
- Remaining subordinate to an occupancy-specific sheet

Record both the stand-alone status and its outward handoffs.

### 5.5 Routing ledger

For each insurer source, maintain:

| Topic | Source that speaks | Base or overlay | Governing value | Silent source retained? | Handoff |
|---|---|---|---|---|---|
| Occupancy demand | Cited occupancy sheet | Overlay | Value or `[V]` | Yes/no | Density-area |
| Installation | Cited installation sheet | Base | Value or `[V]` | Yes/no | Layout |
| Pump architecture | Component sheet | Component | Architecture | Demand routed elsewhere | Pump-envelope |
| Hydraulics | Hydraulic sheet | Method | Method | N/A | Hydraulic Skill |
| ITM | ITM sheet | Method | Interval/test | N/A | ITM Skill |
| Acceptance | Acceptance sheet | Method | Test | N/A | Assignment packet or QA |

A sheet pointer without the underlying cited source is not a closed requirement.

---

## 6. Carrier posture

### 6.1 Single-carrier job

- Fill Carrier A from the named controlling sheet.
- Set Carrier B to `n/a`.
- Apply Rules A–D across code, Carrier A, and owner.
- Do not let FM values silently govern an AXA job.
- Do not let AXA values silently govern an FM job.

### 6.2 Dual-carrier or ambiguous job

- Fill both carrier columns from cited sheets.
- Reconcile the union per parameter.
- Issue one carrier-agnostic BOD, not two separate BODs.
- When the actual carrier is known, drop the unused carrier column and rerun the code and owner overrides.

### 6.3 Third carrier

A third carrier may be added only if the caller supplies:

- Carrier identity
- Applicable sheet
- Sheet date or revision
- Applicable values
- Sections or pages
- Contractual applicability

A public brochure, marketing page, or generic risk-engineering page is not a numeric third-carrier basis.

If the third carrier is named but its governing sheet or values are missing, do not stop: carry `ASSUMED` values (value + why), flagged.

### 6.4 Current carrier evidence

Where these sheets apply, cite:

FM DS 5-32, January 2026:

- Interlock ranking: §2.4.1.1
- Double-interlock delay and availability warning: §2.4.1.2
- Hose allowance: §2.4.1.5
- Duration: §2.4.1.6
- VEWFD and airflow gate: §2.4.2 / §2.4.2.1.3
- Wet/dry demand fork: §2.4.3.2.1.2
- Delivery time: §2.4.3.2.1.2(D)
- Pre-alarm and no cross-zoning: §2.4.3.2.1.3
- Density, area, QR, temperature, ceiling, and spacing: §2.4.3.3.1.1
- Compartmentation: §2.2.4
- Ceiling cap: §2.2.5.2
- Li-ion BBU gate: §2.3.1.4
- Li-ion barriers and no clean agent/hybrid where applicable: §2.4.3.6 / §2.4.3.6.4.1
- Escaped-liquid loss information: Table 3.6.1-1
- DS 2-0 routing: §2.4.3.2.1.1

AXA XL, March 2026:

- Ordinary Hazard Group 1 and no density/area/K-factor/hydraulic method: p. 8
- Single-interlock preference and double-interlock penalty: p. 8
- Full-height separation and door posture: pp. 4, 9
- Fire-alarm damper activation: p. 9
- Power isolation: pp. 4, 9
- Leak detection: p. 4
- Li-ion density reinforcement: p. 8
- 125°F damage-onset criterion: pp. 4, 9

AXA XL PRC sheets:

- Treat as delta overlays unless the PRC itself states otherwise.
- Acquire and cite the underlying NFPA or sibling PRC source it references.
- Do not fabricate a PRC edition where the PRC does not state one.
- Date the claim, not an invented standard edition.
- If the consequential sibling PRC is absent, mark the row `[V]` or unresolved.

---

## 7. Build the matrix

### 7.1 Required columns

| Column | Required content |
|---|---|
| Parameter | Caller-supplied row |
| Applicability | Allowed system family, room, hazard, or phase |
| Code floor | Enforced instrument, edition, section, or `[V]` |
| Insurer A | Value, sheet, date/edition, section/page |
| Insurer B or `n/a` | Value, sheet, date/edition, section/page |
| Owner | Tier A/B numeric evidence, or structure-only |
| Within-carrier routing | Base, overlay, component, method, or unresolved |
| Rule | A, B, C, or D |
| Provisional insurer union | Union before code/owner closure |
| Code override | Code value if it exceeds the insurer union |
| Owner override | Owner value if valid and stricter |
| Controlling value | Final or conditional result |
| Controlling layer | Layer that set this row |
| Status-register token | `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (mandatory every row) |
| Provenance | `grounded` / `derived` / `synthetic` / `verify` (claim quality; keep beside Status-register token) |
| Delta vs NFPA 13-2025 | Directional or quantified only when pinned |
| Flags | `[SYN]`, `[V]`, `[U]`, conflict, `RFI-variance` companion notes |
| Handoff | Generic Skill purpose or `none` |

### 7.2 Cell rules

**Code-floor cell**

- Use the enforced edition and section.
- Include the enforcing instrument.
- If unpinned, use `[V]` and say why.
- NFPA 13-2025 is the delta baseline, not automatically the floor.

**Insurer cell**

- Include the sheet title, revision/date, section or page.
- Distinguish silence from missing source values.
- Do not convert qualitative language into a number.

**Owner cell**

- Use a number only from Tier A or Tier B evidence.
- Tier C, D, and E material is prior or site evidence, not a fleet BOD.
- Public compliance pages are not project-issued owner standards.

**Controlling value**

- Do not label a row final if a mandatory code override is unresolved.
- If code is missing, label the insurer result **provisional insurer union**.
- If owner evidence could change the row, label the result conditional or unresolved.

### 7.3 Default matrix rows

Use only rows applicable to the caller’s system and scope:

1. System family / allowed election
2. Carrier preference or ranking, comparison-only
3. Density / area
4. Hose and duration
5. Water-delivery time
6. Head temperature / response
7. Ceiling cap
8. Compartmentation rating
9. Compartmentation extent
10. Door rating
11. Damper trigger and rating
12. VEWFD / detection
13. Power isolation
14. Leak detection
15. Li-ion barrier and kWh gate
16. Li-ion density uplift
17. Supervisory air or nitrogen
18. Pipe material and corrosion
19. Downstream demand consequence
20. Required handoff

Do not add a special-hazard design row merely because a source mentions a special-hazard option.

---

## 8. Apply the rules

Apply exactly one Rule A–D to each carrier-union row. A later code override may be appended as `+ code override`.

### 8.1 System-family row

The system-family row must first apply the hard scope gate.

Allowed controlling values:

- Wet pipe
- Dry pipe
- Double-interlock preaction

Comparison-only values:

- Non-interlock
- Single-interlock
- Other preaction types

If a source prefers single-interlock, record:

- Carrier preference (Status-register token: `comparison-only`)
- Company election prohibition
- If the caller wants that election / BOD: **Stop** with `RFI-variance` / company-fence gate
- No substituted controlling system family

If owner evidence mandates double-interlock:

- Record owner election as applicable within scope.
- Keep carrier objections visible.
- Separate system-family election from hydraulic area, delivery time, and supply consequences.
- Do not claim that double-interlock is prohibited by the carriers.

### 8.2 Density and area

If FM DS 5-32 supplies the only quantitative value:

- Apply Rule A.
- Cite FM DS 5-32 §2.4.3.3.1.1 and §2.4.3.2.1.2, January 2026.
- Name the controlling density/area row.
- Hand the calculation to `density-area-dry-increase`.

Do not invent an AXA XL density. AXA XL p. 8 supplies Ordinary Hazard Group 1 but no density, area, K-factor, or hydraulic method.

If double-interlock is elected, do not automatically use the wet area. Carry the cited dry-area consequence and hand off the hydraulic calculation.

### 8.3 Delivery time

For FM DS 5-32, cite §2.4.3.2.1.2(D), January 2026.

Do not infer that a carrier’s silence removes the requirement.

Do not invent a proof method. If the delivery-time verification method is not held, record:

- Requirement: grounded
- Means of verification: `[V]` or unresolved
- Handoff: delivery-time or hydraulic Skill

### 8.4 Compartmentation

Use Rule C when rating and extent differ.

Example:

- FM DS 5-32 §2.2.4, January 2026: 2-hour DP-to-DP rating where applicable.
- AXA XL March 2026 pp. 4 and 9: full-height slab-to-deck extent and fire-alarm-activated dampers.
- Union: higher rating plus greater extent plus required trigger.

If the insurer door value conflicts with the code floor, do not stamp the insurer value. Show the ratio and code override status.

### 8.5 Detection and power isolation

Use Rule D when a specific insurer architecture satisfies another source’s general requirement.

Examples:

- FM-Approved VEWFD versus AXA XL fixed photoelectric or air-sampling.
- FM App. D / Fig. D.1 architecture plus AXA XL hall-and-air-handler de-energization.

Keep detection, releasing, power isolation, and HVAC controls as separate rows or explicit handoffs. Do not silently add cross-zoning to a system where the controlling sheet prohibits it.

### 8.6 Li-ion rows

If energy data are supplied, show the classification arithmetic without inventing inputs:

```text
kWh per cell = Ah × V / 1000
kWh per module = kWh per cell × cells per module
kWh per rack = kWh per module × modules per rack
```

Use FM DS 5-32 §2.3.1.4 and §2.4.3.6, January 2026, where applicable.

If AXA XL requires density reinforcement but supplies no factor or method:

- Record the requirement.
- Record FM’s quantitative value separately.
- Mark the controlling magnitude unresolved `[V]`.
- Do not invent a multiplier.
- Hand off only after a cited magnitude exists.

### 8.7 Clean agent and special hazard rows

Use only as a prohibition or applicability record.

For distributed Li-ion where FM DS 5-32 §2.4.3.6.4.1 applies:

- Record clean agent/hybrid prohibition.
- Do not size gas.
- Route any adjunct question to the clean-agent or special-hazard Skill.

For foam:

- Record **prohibited** for company scope.
- Do not create a foam system.
- If presented as election/design/BOD: **Stop** with `RFI-variance` / company-fence gate.
- Route any occupancy-forced foam requirement to special-hazard review (`handoff`).

For mist:

- Record `PRACTICE REFUSED`.
- Do not treat FM’s flowchart allowance as company authorization.
- If presented as election/design/BOD: **Stop** with `RFI-variance` + `PRACTICE REFUSED`.
- Route to `suppression-technology-selection` and special-hazard review (`handoff`).

---

## 9. Code-floor override

The code floor has priority over the insurer union where the code requirement is higher and applicable.

### 9.1 Override test

For every row:

1. Identify the enforced code requirement.
2. Identify the insurer union.
3. Compare them on the same axis.
4. If the code floor is more stringent, set the code override.
5. If the code floor is absent, mark the row `provisional` / `unresolved` with a stated `ASSUMED` floor (value + why) + RFI and continue — not a Stop.

### 9.2 Door-ratio check

Where both carriers state a ¾-hour door and the insurer union contains a 2-hour barrier:

```text
insurer ratio = 0.75 hr / 2.00 hr = 0.375
```

A ¾-hour door on a 1-hour barrier has:

```text
0.75 hr / 1.00 hr = 0.75
```

A 1½-hour door on a 2-hour barrier has:

```text
1.50 hr / 2.00 hr = 0.75
```

The IBC-716 opening-protective table is not held as a mined primary in the corpus. Therefore:

- The non-conformance signal is detectable.
- The 1½-hour result is `[V]` / `[SYN]` until the adopted code and table are pinned.
- Do not label the insurer-union ¾-hour door AHJ-compliant on a 2-hour barrier.

### 9.3 Missing-code fallback

If the code-floor requirement is absent:

- Carry the insurer union only as a **provisional insurer union**.
- Mark `code override unresolved`.
- Mark status `unresolved`.
- Keep the delta directional `[V]`.
- Do not call the row final.
- Do not call the row code-compliant.
- Create the required procurement or RFI handoff.

This is not a default that the insurer wins. It is an explicit incomplete three-layer result.

### 9.4 Current NFPA 13-2025 delta treatment

The general dry/double-interlock +30% comparison is:

- Cited [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03]
- No invented section
- No fabricated percentage beyond a cited source
- Cite by edition: the 2025 pointer is §19.2.3.2.6 (2025 §19.2.3.2.5 is the ceilings-over-30 ft rule)

If FM DS 5-32 supplies `2,500 ft² wet` and `3,500 ft² dry`, the FM comparison may be shown:

```text
FM dry increase = (3500 − 2500) / 2500 = 0.40 = +40%
```

The NFPA 13 general +30% rule is held: [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03].

---

## 10. Owner-layer override

The owner layer may raise a requirement but may not lower:

- The adopted code floor
- A carrier condition of coverage
- A mandatory local amendment
- A legally required administrative condition

### 10.1 Evidence ladder

| Tier | Evidence | Use |
|---|---|---|
| A | Project-issued owner standard, BOD, or specification | Binding Layer 3 |
| B | Written project answer or accepted deviation | Binding for that project |
| C | One-site filing or installed condition | Site evidence only |
| D/E | Public compliance page, marketing, prior, or inference | Prior only; not BOD |

Do not fill silent owner cells from public material.

If the owner is silent:

- Use `— (not invoked)` where appropriate.
- Add `[V] owner standard not in hand`.
- Do not infer owner numbers.
- Treat any owner-sensitive election as conditional or unresolved.

### 10.2 Owner double-interlock mandate

An owner-issued double-interlock mandate is permitted within this Skill’s allowed system-family scope.

Carry separately:

- Owner system election
- Carrier preference or objection
- Dry-area consequence
- Delivery-time consequence
- Supervisory-gas consequence
- Corrosion/material consequence
- Downstream water-supply consequence

Do not silently replace the owner election with the carrier preference for single-interlock or non-interlock.

---

## 11. Provenance, Status register, and flags

Every matrix row must carry a **Status-register token**, a provenance label, and any applicable flags. Do not collapse provenance into the Status-register token.

### 11.1 Provenance labels (claim quality)

| Label | Meaning |
|---|---|
| `grounded` | Directly supported by a held source with section/page and edition/date |
| `derived` | Arithmetic derived only from grounded inputs; math shown and independently checked |
| `synthetic` | Caller-invented or exercise/project quantity; never a code or insurer fact |
| `verify` | Source, edition, section, applicability, or value requires verification (`[V]`) |

A derived result must not become provenance-`grounded` merely because its arithmetic is correct. The inputs and the result retain their own provenance.

### 11.2 Flags

- `[SYN]` — invented or synthesized project quantity
- `[V]` — unverified, unpinned, secondary, unmined, or source-limited
- `[U]` — unresolved and not eligible for a final controlling claim
- `CONFLICT` — sources conflict on the same axis
- `HANDOFF` — another Skill owns the next action (companion to Status-register `handoff`)

### 11.3 Status register (mandatory every run)

Emit with Outputs. **Every parameter row, election, and gate gets a Status-register token.** Vocabulary matches the ITM / campus / STS bar:

| Status | Use on this Skill |
|---|---|
| `grounded` | Controlling value pinned to held sheet/edition/section (or enforced instrument) + closed three-layer reconciliation within company wet/dry/DI scope |
| `provisional` | Insurer-union result with open non-gating assumptions, or code/owner layer not yet closed but row still usable as provisional insurer union (assumptions stated) |
| `unresolved` | Blocking hole: missing parameter list; missing jurisdiction/permit path; dual-carrier sheet missing; mandatory code override cannot be evaluated for a final claim; owner-sensitive election without evidence |
| `comparison-only` | SI/NI / other preaction evidence; FM DS 5-32 preference ranking; AXA SI preference / DI penalty; carrier ranking rows — **never** the controlling company election |
| `handoff` | Work owned elsewhere: density-area; pump-envelope; occupancy-hazard-fork; STS election; ITM; clean-agent / special-hazard; releasing C&E; jurisdiction research |
| `RFI-variance` | Company-fence gate: SI/NI/foam/mist (or other prohibited family/medium) presented as election/BOD; prohibited system-family stop |

**Rules:**

- SI/NI evidence rows → `comparison-only`. SI/NI as election/BOD → **Stop** with `RFI-variance`.
- Foam as election/design → `RFI-variance` (prohibited). Mist as election/design → `RFI-variance` + `PRACTICE REFUSED`.
- Do **not** emit a final `grounded` controlling value while a mandatory code override is `unresolved`.
- Preserve `[SYN]` / `[V]` / provenance beside the Status-register token; do not collapse them into it.
- Special-hazard record-only rows that are not elections → `handoff` or `comparison-only` as applicable.

---

## 12. Show-and-verify arithmetic

This Skill owns:

- Rule selection
- Ratio checks
- Carrier-lever comparisons
- Simple derived quantities
- Scope and routing checks

This Skill does not own:

- Density-area `_calc`
- Pump sizing
- Supply-curve margin
- Node-by-node hydraulic calculations
- CAD or delegated design

### 12.1 Double-interlock lever comparison

```text
fm_di_area  = 3500 ft²
axa_di_area = 2500 ft² × 1.30
             = 3250 ft²

verification:
0.30 × 2500 = 750 ft²
2500 + 750 = 3250 ft²
```

Do not average `3500` and `3250`.

Do not stack `3500 × 1.30` without a cited requirement.

### 12.2 FM dry increase

```text
fm_increase = (3500 − 2500) / 2500
            = 1000 / 2500
            = 0.40
            = +40%
```

This is an FM comparison, not a substitute citation for the unpinned general NFPA 13-2025 +30% rule.

### 12.3 Demand screen, when values are supplied

The matrix may show the named consequence without running the density-area Skill:

```text
Q_sprinkler = density × design area
Q_total     = Q_sprinkler + hose allowance
V_min       = Q_total × duration
```

Example using grounded FM wet values:

```text
0.2 gpm/ft² × 2500 ft² = 500 gpm
500 gpm + 250 gpm      = 750 gpm
750 gpm × 60 min       = 45,000 gal
```

Label these as derived only when the inputs are grounded and the arithmetic is independently checked. Hand the actual hydraulic design and supply adequacy to `density-area-dry-increase` and `pump-envelope`.

### 12.4 Li-ion arithmetic

```text
kWh per cell   = Ah × V / 1000
kWh per module = kWh per cell × cells per module
kWh per rack   = kWh per module × modules per rack
```

Do not invent `Ah`, voltage, cell count, or module count.

---

## 13. Failure fallbacks

Use these fallbacks in order:

1. Both carriers silent and code floor present:
   - Code floor controls.
2. One carrier quantitative and the other qualitative or silent:
   - Rule A; quantitative source controls provisionally.
3. Carrier conflict on same axis:
   - Select the more stringent applicable value.
   - Preserve both sources.
   - Log `CONFLICT`.
4. Different carrier axes:
   - Rule C; retain the union.
5. All layers absent:
   - Mark `unresolved`.
   - Do not invent.
6. Code floor absent:
   - Carry provisional insurer union.
   - Mark code override unresolved.
   - Do not label final or code-compliant.
7. Owner standard absent:
   - Structure-only owner column.
   - Do not infer a number.
8. Dual-carrier sheet or values missing:
   - Stop.
9. Third carrier named but source missing:
   - Stop.
10. Caller requests prohibited system family (SI/NI/other) as election/BOD:
    - **Stop** with `RFI-variance` / company-fence gate (evidence may remain `comparison-only`).
11. Caller requests foam or mist as election/design/BOD:
    - **Stop** with `RFI-variance` (foam prohibited; mist `PRACTICE REFUSED`); route to special-hazard / STS (`handoff`).
12. Caller asks this Skill to perform occupancy, density-area, pump, or hydraulic-tree work:
    - **Stop** and hand off (`handoff`).

---

## 14. Output

Produce a markdown package containing:

1. Jurisdiction-instrument register
2. Edition-pin block
3. Source and sheet-routing ledger
4. Scope-gate result
5. Per-parameter reconciliation matrix
6. Rule assignments
7. Provisional insurer-union and code-override notes
8. Owner evidence statement
9. Show-and-verify arithmetic
10. **Status register** (mandatory — §11.3 / §14.3)
11. Provenance labels + `[SYN]`, `[V]`, `[U]`, and conflict register
12. Handoffs
13. Dual-carrier collapse note, if applicable

### 14.1 Minimum matrix

| Parameter | Applicability | Code floor | Insurer A | Insurer B or `n/a` | Owner | Routing | Rule | Provisional union | Code override | Owner override | Controlling value | Controlling layer | Status-register token | Provenance | Δ vs NFPA 13-2025 | Flags | Handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 14.2 Required statements

Include:

- Most-stringent is per parameter, not per layer.
- No whole-layer MAX was used.
- System-family election is limited to wet, dry, and double-interlock preaction.
- Single-interlock/non-interlock evidence is `comparison-only` unless separately authorized outside this Skill; as election/BOD → **Stop** with `RFI-variance`.
- Foam is prohibited; as election/design → **Stop** with `RFI-variance`.
- Mist is `PRACTICE REFUSED`; as election/design → **Stop** with `RFI-variance`.
- NFPA 13-2025 is the delta baseline, not automatically the enforced code floor.
- Any unmined or unpinned primary remains `[V]`.
- A provisional insurer union with unresolved code override is not a final code-compliant BOD (Status-register: `provisional` / `unresolved` as applicable).
- Density-area and pump work are handoffs (`handoff`), not calculations performed here.
- A dual-carrier prototype must be rerun against the actual carrier when known.
- Status register emitted every run for every row/election/gate.

### 14.3 Status register (mandatory emit)

Every run must emit a Status register covering **each parameter row and each election/gate**:

| Parameter / row | Election or evidence | Status-register token | Controlling layer / source pointer | Flags | Notes |
|---|---|---|---|---|---|

Tokens allowed: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.

Minimum checks:

- Wet/dry/DI controlling elections that close → `grounded` or `provisional` (never silent `grounded` on provisional insurer union or unresolved code override).
- SI/NI / FM ranking / AXA preference rows → `comparison-only`.
- SI/NI/foam/mist as requested election → `RFI-variance` (and **Stop** per Hard scope).
- Density-area / pump / occupancy / STS / ITM / special-hazard work → `handoff`.
- Missing required jurisdiction, dual-carrier sheet, or mandatory override → `unresolved`.

### 14.4 Do not emit

Do not emit:

- Space-by-space occupancy classification
- A new hazard-classification schedule
- Density-area `_calc` transcript
- Pump rated flow or pressure selection
- Supply-curve adequacy proof
- Node-by-node hydraulic tree
- CAD or drawings
- Assignment-packet rebuild
- Clean-agent, foam, mist, or other special-hazard design
- Invented NFPA, IBC, NEC, insurer, or owner citations
- A final code-compliance claim while a mandatory code override is unresolved

---

## 15. Stop conditions

> **2026-10-07 intake rule:** any item below that is a missing packet, a missing upstream result, or a missing input blank is **not** a Stop — proceed with a stated `ASSUMED` value (value + why), flagged in the output and status register. Only company scope-lock items (SI/NI-as-BOD → `RFI-variance`, foam, water mist `PRACTICE REFUSED`, clean agent as company BOD) and wrong-Skill / out-of-scope routing remain hard Stops.

Return the blocking item (hard **Stop** only for scope-lock / wrong-Skill items; input gaps → stated `ASSUMED`, flagged) when:

1. The parameter list is missing → `unresolved`.
2. The caller requests single-interlock, non-interlock, or another prohibited preaction type as election/BOD → **Stop** with `RFI-variance` (evidence may remain `comparison-only`).
3. The caller requests foam design or specification → **Stop** with `RFI-variance` (prohibited).
4. The caller requests mist design or specification → **Stop** with `RFI-variance` (`PRACTICE REFUSED`).
5. Permit jurisdiction or permit-date path is missing → `unresolved`.
6. State or local adoption instrument is missing → `unresolved`.
7. The adopted integrated code text is unavailable where needed → `unresolved`.
8. The NEC pin is missing for an electrical or power-isolation row → `unresolved`.
9. A dual-carrier job lacks the second carrier’s sheet identity or stated values → `unresolved`.
10. A third carrier is named without cited sheet values → `unresolved`.
11. An NDA owner standard is demanded as a numeric source → `unresolved` / `RFI-variance` as applicable.
12. A public owner page is being used as a binding BOD → `unresolved`.
13. A source is only a root PDF, pointer, or unmined reference → `unresolved`.
14. A required code override cannot be evaluated and the caller asks for a final code-compliant value → `unresolved`.
15. A caller asks this Skill to perform occupancy, density-area, pump-envelope, hydraulic-tree, CAD, or assignment-packet work → **Stop** with `handoff`.
16. The caller asks for output in a corpus or managed write lane rather than the caller-named path.

---

## 16. Generic handoffs

| Work | Handoff |
|---|---|
| Space-list occupancy, IBC/IFC trigger, sprinkler hazard class | `occupancy-hazard-fork` |
| Density, remote area, dry-area increase, demand calculation | `density-area-dry-increase` |
| Pump rated flow, pressure, churn, supply curve, margin | `pump-envelope` |
| Node-by-node sprinkler hydraulics | hydraulic-tree Skill (not yet in shop) |
| Detection and releasing cause-and-effect | `preaction-releasing-c-and-e-soo` |
| Power isolation and electrical coordination | `power-isolation-disconnect-control` |
| Clean agent or other special hazard | `clean-agent-enclosure-integrity` / `clean-agent-concentration-and-quantity` |
| ITM and acceptance | `itm-design-for-testability` / `commissioning-ist-acceptance-packet` |
| Retrieve and adapt an existing assignment packet | `dc-fp-assignment-packet` |
| Jurisdiction adoption and AHJ instrument research | jurisdiction-edition-resolver |
| Owner standard or unresolved owner election | owner RFI |
| CAD, BIM, or delegated design | outside Skills |

Consume another Skill’s output when supplied. Do not duplicate its work.

---

## 17. Citations

Use the shop codebook by title. Every requirement citation must include section and edition/date where the source provides them.

### the engineer Way and method

- `The engineer Way` — three-layer basis, per-parameter most-stringent rule, enforced-versus-latest distinction, and delta reporting
- `enforced-edition-resolver-and-reference-pins.md` — adoption chain, jurisdiction resolver, Chapter 80/35 pins, independent NEC resolution, and NFPA 13-2025 delta discipline
- `hyperscaler-owner-standard-layer.md` — owner evidence ladder, asymmetric raise-only rule, and NDA/public-owner limits
- `fm-occupancy-vs-installation-sheet-precedence-ds-5-32-and-ds-2-0.md` — base/overlay, component, stand-alone, routing, and silence-not-permission rules

### FM DS 5-32

`FM DS 5-32 January 2026`

- Interlock ranking: §2.4.1.1
- Double-interlock availability warning: §2.4.1.2
- Hose allowance: §2.4.1.5
- Duration: §2.4.1.6
- VEWFD and airflow: §2.4.2 / §2.4.2.1.3
- Wet/dry demand fork: §2.4.3.2.1.2
- Delivery time: §2.4.3.2.1.2(D)
- Pre-alarm and no cross-zoning: §2.4.3.2.1.3
- Density, design area, QR, temperature, ceiling, spacing: §2.4.3.3.1.1
- Compartmentation: §2.2.4
- Ceiling cap: §2.2.5.2
- BBU gate: §2.3.1.4
- Li-ion barrier and no-gas condition: §2.4.3.6 / §2.4.3.6.4.1
- DS 2-0 routing: §2.4.3.2.1.1
- Loss table: Table 3.6.1-1

### AXA XL

`AXA XL March 2026`

- Ordinary Hazard Group 1 and no density/area/K-factor/hydraulic method: p. 8
- Single-interlock preference and double-interlock penalty: p. 8
- Full-height separation and doors: pp. 4, 9
- Fire-alarm damper activation: p. 9
- Power isolation: pp. 4, 9
- Leak detection: p. 4
- Li-ion density reinforcement: p. 8
- 125°F damage-onset criterion: pp. 4, 9
- PRC overlay behavior: `AXA XL insurer design basis.md`, “How AXA XL’s PRC library actually works”

### Code and delta

- NFPA 13-2025 §8.2.4 — dry-system water-delivery restructuring, where applicable
- NFPA 13-2025 §8.2.11 — VCI systems, where applicable
- NFPA 13-2025 §8.11 — vacuum dry or vacuum preaction, where applicable
- NFPA 13-2025 §19.2.3.2.5 — ceilings over 30 ft (pull 13-03); in 2022 the same number is the dry-pipe / double-interlock +30% rule, so always cite it with its edition
- NFPA 13 dry/double-interlock +30% — [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03]
- IBC-716 opening-protective table — `[V]` unless the adopted edition and table are held
- IBC-717 damper table — `[V]` unless the adopted edition and table are held
- NFPA 72-2025 releasing provisions — `[V]` unless the enforced and latest primary pins are held
- NEC Article 645 and NFPA 75 — `[V]` unless the independently resolved electrical code path is held

### Scope fences

- `foam-extinguishing-and-foam-water-sfff.md` — foam is not a hyperscale white-space primary; route only when a cited hazard sheet requires it
- `suppression-technology-selection-by-space-and-objective.md` — technology-selection routing and current mist correction
- Water-mist design-basis notes — mist remains `PRACTICE REFUSED` for this company scope

---

## 18. the engineer Way

1. Code is the floor; insurer and owner may raise it.
2. Most-stringent is per parameter, never per layer.
3. The allowed company system family is wet, dry, or double-interlock only.
4. Single-interlock and non-interlock are `comparison-only` — never company election here.
5. Double-interlock is carrier-disfavored but owner-electable; split system election from hydraulic, delivery, gas, corrosion, and supply consequences.
6. Enforced edition is not latest edition.
7. NFPA 13-2025 is the delta baseline, not automatically the enforced minimum.
8. Every governing requirement needs section and edition/date.
9. Silence is not permission.
10. An unmined root PDF is not evidence.
11. Owner evidence is asymmetric: raise, never lower; NDA is structure, not a number.
12. Foam is prohibited.
13. Mist is `PRACTICE REFUSED`.
14. Show and verify simple math; hand off density-area and pump calculations (`handoff`).
15. If uncertain, mark `[V]` / `unresolved` and carry a stated `ASSUMED` value (value + why) rather than silently invent.
16. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.
17. Keep `[SYN]`, `[V]`, provenance, and Status register visible.
18. Never turn an unresolved code override into a final code-compliant BOD.
19. SI/NI/foam/mist as election/BOD → **Stop** with `RFI-variance`; do not silent-substitute wet/dry/DI.

---

## 19. Runner checklist

1. Confirm the parameter list and caller-named output path.
2. Apply the wet/dry/double-interlock Hard scope gate.
3. **Stop** on a requested single-interlock, non-interlock, foam, mist, or other prohibited election/BOD with `RFI-variance` (SI/NI evidence may remain `comparison-only`).
4. Build the jurisdiction-instrument register.
5. Resolve enforced code editions and the separate NEC pin.
6. Record NFPA 13-2025 as the delta baseline only.
7. Confirm Carrier A and Carrier B or explicit `n/a`.
8. Read each source’s scope fence and classify its sheet type.
9. Build the within-carrier routing ledger.
10. Fill one row per parameter.
11. Assign exactly one Rule A–D per row.
12. Resolve the insurer union per parameter.
13. Apply the code override.
14. Apply owner raise-only evidence.
15. Mark provisional insurer unions and unresolved overrides (`provisional` / `unresolved`).
16. Add provenance labels (`grounded` / `derived` / `synthetic` / `verify`).
17. **Emit Status register** (mandatory): `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` on every row/election/gate (§11.3 / §14.3).
18. Show and verify ratio and lever arithmetic.
19. Name the density/area row without running `_calc` (`handoff` to density-area).
20. Add generic handoffs (`handoff` tokens where work is owned elsewhere).
21. Add directional NFPA 13-2025 deltas only where valid.
22. Preserve `[SYN]`, `[V]`, `[U]`, and conflict notes beside Status-register tokens.
23. Add the dual-carrier collapse note where applicable.
24. Write only to the caller-named path, or return the matrix and stop if no path was named.

## Support-space duration pin (E1; E3 CLOSED = E1), 2026-10-27
- Support OH2 wet: **60 min** under NFPA 13-2025 §19.2.3.1.3 (supervised + monitored at a constantly attended location). Show-and-verify [SYN]: 550 gpm × 60 = **33,000 gal**.
- FM layer agrees: FM DS 3-26 (Apr 2019 / IR Apr 2025) §2.3.1.13 → **60 min for all HC**; hose **250 gpm** for HC-1/HC-2 (§2.3.1.12). E3 is closed and equals E1. Delta vs NFPA 13-2025: none on duration.
- E2 (90 min, 49,500 gal) only if AHJ/owner requires the unsupervised branch. Hall demand × duration (e.g. 66,797 gal) still governs supply and storage.


## 2026-11-03 — GAP-B29R1-2 NEG-CA list
Added explicit NEG-CA-1..5 above §4.2b Still-unresolved list (substance already in prose). Unresolved + RFI list kept unchanged.

## 2026-11-04 — stop-vocab normalize (staged)
- Inserted short §1.0 Country/edition gate pointing to existing §4.2/§4.2b + NEG-CA (no new cites).
- `If no path is named, return the matrix in the response and stop. Do no…` → `If no path is named, return the matrix in the response (output-routing rule, not a design …`
- `5. If the code floor is absent, mark the row provisional and unresolve…` → `5. If the code floor is absent, mark the row `provisional` / `unresolved` with a stated `A…`
