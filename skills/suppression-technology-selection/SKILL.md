---
name: Suppression technology selection
description: >-
 use this when selecting, at concept stage, the protection objective and
 permitted wet/dry/double-interlock water-based system family per space on a US
 data-center program, including accepting, amending, deferring, or rejecting a
 vendor suppression concept before occupancy, density-area, pump, or detailed
 special-hazard work; emit a status register per election/row
 (grounded/provisional/unresolved/comparison-only/handoff/RFI-variance).
---
# Suppression technology selection

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection concept-stage recipe.

This Skill owns only:

> protection objective → permitted medium/system family → accept/amend/reject/defer → lifecycle consequence

It does **not** own the three-layer per-parameter reconciliation. Consume the completed `most-stringent-basis-matrix` result and do not rebuild its jurisdiction register, carrier union, owner evidence analysis, or code overrides.

**Design practice:** objective first, then permitted medium/system family. Physics is a lens; code, insurer, owner, and company scope control the selection. Consume `most-stringent-basis-matrix`; do not duplicate it. Select only wet pipe, dry pipe, or double-interlock preaction. SI/NI = `comparison-only`. Foam prohibited. Mist `PRACTICE REFUSED`. Cite **section AND edition**. Show-and-verify preview arithmetic when FM values apply. Mark invented values `[SYN]` / unpinned values `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Write **only** to the path the **caller** names.

The output is a per-space technology-objective selection matrix. It must state:

1. The objective
2. The space taxonomy
3. The vendor or conceptual proposal
4. The physics lens
5. The permitted company system family
6. The selection status
7. The Status-register token (`grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`)
8. The controlling basis pointer
9. The lifecycle consequences
10. The required handoffs
11. `[SYN]`, `[V]`, and unresolved conditions

Write output only to the caller-named path. Do not write to,,, or .

---

## 1. Hard scope gate

### 1.1 Allowed company elections

This Skill may select only:

- Wet-pipe sprinkler
- Dry-pipe sprinkler
- Double-interlock preaction

The selected water-based system must be supported by the consumed `most-stringent-basis-matrix` result.

### 1.2 Comparison-only system evidence

These may appear in a vendor, carrier, or owner proposal, but this Skill must not select them:

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

If the caller requires single-interlock, non-interlock, or another prohibited preaction type as a **company election** / BOD:

1. Record the requested election.
2. **Stop** the system-family decision.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. SI/NI may appear only as a **`comparison-only`** evidence row (never the controlling selection).

FM DS 5-32’s January 2026 preference ranking remains **`comparison-only`** evidence:

> Wet → non-interlock → single-interlock → double-interlock last

This ranking does not authorize a company election outside the hard scope. Status on ranking rows: `comparison-only`.

### 1.3 Prohibited or handoff-only media

This Skill must not elect or design:

- Foam or foam-water
- Water mist
- Clean agent
- Hybrid water/inert gas
- Condensed aerosol
- Oxygen-reduction or hypoxic systems
- Dry chemical
- Water spray
- Carbon dioxide
- Any other special-hazard medium

Treatment:

| Medium | FM/carrier status | Company status | This Skill action |
|---|---|---|---|
| Water sprinkler family | May be applicable | Permitted | Select wet, dry, or double-interlock only |
| Water mist | FM DS 5-32 may permit a branch | `PRACTICE REFUSED` | Record evidence; do not elect/design |
| Clean agent | Often supplementary; may be barred by topology | Record-only | Out of scope |
| Hybrid | May be supplementary or barred | Record-only | Handoff to special-hazard Skills |
| Foam | May apply to a cited ignitable-liquid hazard | Prohibited | Stop and hand off |
| Aerosol | Physics/vendor option only; not a hall default | Record-only | Handoff or stop |
| Hypoxic/oxygen reduction | Physics option only | Record-only | Handoff or stop |
| Water spray | Separate apparatus/special-hazard regime | Record-only | Out of scope |

### 1.4 Mist refusal

FM DS 5-32 January 2026 Fig. 2.4.3.1.1.1 may present FM Approved water mist as an option. FM DS 5-32 §2.4.3.3.2.1 delegates mist design to DS 4-2 and the manufacturer’s DIOM/listing.

That does **not** lift the company practice fence:

> Mist is `PRACTICE REFUSED`.

The presence of mined FM DS 4-2, an FM Approval listing, or a manufacturer DIOM does not authorize this Skill to elect or design mist.

If the caller requests mist:

- Record that FM may permit it in a cited branch.
- Record company refusal.
- Return status `RFI-variance` (company-fence) with companion `prohibited` / `handoff` as applicable.
- Route to the applicable special-hazard process.
- Do not produce nozzle, pressure, spacing, flow, listing, or hydraulic design.

### 1.5 Foam refusal

Foam is not a permitted company selection.

If an occupancy or hazard sheet appears to require foam:

- Do not design or specify foam.
- Record the cited requirement.
- Return an `RFI-variance` / company-fence gate.
- Hand off to the applicable special-hazard and hazard-classification Skills.

 states that foam is not a hyperscale white-space primary and is routed only when a cited occupancy/hazard sheet requires it.

---

## 2. Required inputs

The caller must supply:

| Input | Required | Rule |
|---|---:|---|
| Space list | Yes | One row per space; missing list → `ASSUMED` space list (flagged), not a Stop |
| Owner objective per space | Yes, may be empty | `control`, `suppression`, or `extinguishing` |
| Li-ion topology | Yes where relevant | Missing topology on white-space, UPS, BBU, or ESS row → `ASSUMED` topology (value + why, flagged), not a Stop |
| Consumed basis-matrix result | Yes | Must include jurisdiction status, carrier status, owner evidence, system-family constraints, and unresolved rows |
| Vendor concept matrix | No | If absent, vendor column is `n/a` |
| Caller output path | Yes for file output | If absent, return the matrix and stop |

The consumed `most-stringent-basis-matrix` result must identify:

- Jurisdiction and enforced-edition status
- Applicable insurer or insurers
- Owner evidence status
- Allowed system-family constraints
- Provisional insurer-union rows
- Unresolved code overrides
- Applicable controlling rows and handoffs
- Directional delta references versus NFPA 13-2025

This Skill must not recreate those determinations.

### 2.1 Space-list fields

Each space should include:

- `name`
- Taxonomy: `white`, `grey`, `churn`, `ordinary`, `mmr`, `genset`, or another named special hazard
- `area_ft2`, if available
- `ceiling_height_ft`, if available
- Contents and operational notes
- Li-ion topology where applicable
- Vendor or owner concept, if any

Missing project values are not invented. Mark them `[SYN]` only when the caller explicitly supplies them as synthetic placeholders.

### 2.2 Owner objective

The objective comes from the owner’s business-continuity plan, not from a vendor matrix.

Allowed objective vocabulary:

- `control` — limit growth and spread
- `suppression` — reduce intensity and hold until fire-service response
- `extinguishing` — extinguish with minimal residue or interruption

If the BCP is empty:

- State an objective as a placeholder.
- Mark it `[SYN]`.
- Say that it is not derived from the corpus.
- Do not invent a BCP requirement.

If the selected objective is unavailable under the controlling basis, mark it:

> `FORECLOSED — not traded away`

Do not rewrite a prohibition as a preference.

Example: an extinguishing objective for a distributed-Li-ion data-processing room may be foreclosed by FM DS 5-32 January 2026 §2.4.3.6.4.1. The lifecycle benefit of gaseous protection must still be acknowledged, but it is unavailable under that controlling condition.

---

## 3. Consume the basis-matrix result

Before selecting a technology, read the completed `most-stringent-basis-matrix` result.

### 3.1 Do not duplicate the basis matrix

This Skill must not:

- Rebuild the jurisdiction-instrument register
- Reconcile carrier A and carrier B row by row
- Rank whole layers
- Recreate owner evidence tiers
- Resolve code overrides
- Recalculate the full carrier union
- Replace unresolved basis rows with assumptions

Use the matrix’s controlling result and status.

### 3.2 Basis status handling

| Basis-matrix status | Selection action | Status token |
|---|---|---|
| Grounded controlling system family | May select if within company scope | `grounded` |
| Provisional insurer union | Selection may be conditional; preserve provisional status | `provisional` |
| Unresolved system-family row | Elect an `ASSUMED` company family (wet / dry / DI only, with why), flagged — not a Stop | `unresolved` |
| Unresolved row unrelated to selection | Carry `[V]` and proceed conditionally | `unresolved` (non-blocking) / `[V]` |
| Owner evidence absent | Do not infer owner election | `unresolved` or `RFI-variance` |
| Prohibited system family | Stop with company-fence gate | `RFI-variance` |
| Missing carrier source | `ASSUMED` carrier (flagged) or hand off to `most-stringent-basis-matrix` — not a Stop | `handoff` / `unresolved` |
| SI/NI / other preaction as election | Stop; record comparison evidence only | `RFI-variance` + `comparison-only` row |

Selection output must point to the relevant basis-matrix row or caller-supplied citation rather than duplicating the full matrix.

---

## 4. Space taxonomy

This is a use-and-physics taxonomy, not IBC occupancy, NFPA 13 hazard classification, or FM hazard classification.

The `occupancy-hazard-fork` Skill owns those classifications after this concept selection.

| Token | Meaning | Required split |
|---|---|---|
| `white` | Servers, IT, data processing, high airflow, shielded equipment fires | Treat in-rack Li-ion as an overlay |
| `grey` | Support areas with UPS, BBU, switchgear, or electrical equipment | Split UPS/BBU from MV/LV switchgear |
| `churn` | Corridors, staging, de-crate, receiving, transitional areas | Split staging/storage commodity from cable routes |
| `ordinary` | Offices, NOC, administration, break rooms | Usually life-safety control |
| `mmr` | Telecom meet-me or cross-connect rooms | Route telecom regime separately |
| `genset` | Generator, fuel, and day-tank areas | Separate special hazard; no incipient-stage assumption |
| `other` | Named special hazard | Route to the applicable Skill |

### 4.1 Required taxonomy cautions

- Do not apply a white-space hall rule to a UPS or BBU gallery without confirming the room regime.
- Do not apply an HC category to staging/de-crate storage merely because it is located in a data building.
- Do not treat an MMR as white space without resolving the telecom/private-enterprise regime.
- Do not treat an ESS room as an ordinary grey room.
- Do not treat generator/fuel areas as a sprinkler-only selection question.

---

## 5. Physics screen: lens, not requirement

Use Euralarm §5 p. 9 and related vendor material as a physics lens only.

| Technology | White | Grey | Churn | Ordinary | Physics note |
|---|---|---|---|---|---|
| Sprinkler/control | Less suitable for shielded IT fires | Usually compatible with wetting tolerance | Suitable | Suitable | Heat-actuated; water and power consequences |
| Water mist | May be suitable only under a valid listing | May be physically attractive | May be suitable | May be suitable | Listing-specific; company practice refuses |
| Gaseous | Physically attractive for shielded contents | May be attractive | Usually less suitable | Usually less suitable | Requires enclosure/retention; company handoff only |
| Oxygen reduction | Physics option only | Physics option only | Usually unsuitable | Usually unsuitable | Company handoff/stop |
| Condensed aerosol | Physics option only | Physics option only | Usually unsuitable | Usually unsuitable | Not a company election |

Physics does not control the selection.

The controlling selection comes from:

1. Consumed basis-matrix result
2. Adopted code and AHJ conditions
3. Applicable insurer conditions
4. Owner evidence
5. Company scope gate

### 5.1 Airflow discipline

Do not reject gaseous concepts merely because of airflow.

The FSSA/FIA Phase 2 evidence in the corpus reports acceptable or improved agent homogeneity within its tested envelope of approximately:

- Up to 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; FSSA/FIA test envelope, not code]
- 100% recirculation
- No makeup air

The evidence does not establish behavior outside that envelope, but airflow alone is not a sufficient rejection basis.

If a gaseous concept is rejected, state the actual basis:

- Company scope
- Carrier prohibition
- Code/AHJ requirement
- Owner requirement
- Missing retention feasibility
- Missing listing or enclosure basis
- Supplement-not-substitute rule

Do not use airflow as a substitute for those grounds.

---

## 6. Permitted-versus-favored decision table

Every selection matrix must include this distinction.

| Candidate | FM/carrier status | Company status | Selection result | Required action |
|---|---|---|---|---|
| Wet pipe | May be FM’s highest-preference water-based option under DS 5-32 §2.4.1.1, January 2026 | Permitted | May select if basis matrix supports | Handoff to occupancy and density-area |
| Dry pipe | May be required by climate or cited basis | Permitted | May select only with cited basis | Handoff to density-area and pump-envelope |
| Double-interlock | FM least-preferred; AXA XL penalizes it | Permitted | May select if owner/basis matrix requires | Carry dry-area, delivery, gas, corrosion, and supply consequences |
| Single-interlock | Carrier comparison evidence | Not permitted for election | `comparison-only` | Caller request → `RFI-variance` stop |
| Non-interlock | Carrier comparison evidence | Not permitted for election | `comparison-only` | Caller request → `RFI-variance` stop |
| Water mist | FM may permit a cited branch/listing | `PRACTICE REFUSED` | Refused | Special-hazard handoff |
| Clean agent | Generally adjunct; may be barred by topology | Record-only | Deferred, prohibited, or handoff | Clean-agent Skills |
| Hybrid | May be adjunct or barred | Record-only | Deferred, prohibited, or handoff | Special-hazard Skills |
| Foam | Hazard-sheet-dependent | Prohibited | Prohibited | `RFI-variance` and special-hazard handoff |
| Aerosol/hypoxic | Physics/vendor evidence only | Record-only | Screen-out or handoff | Special-hazard Skills |
| Water spray | Separate apparatus regime | Record-only | Deferred/handoff | out of scope |

The distinction is mandatory:

- **FM-permitted** does not mean company-permitted.
- **Physically favored** does not mean selected.
- **Selected** requires the basis-matrix result and the company scope gate.
- **Refused** must remain refused even if a carrier branch exists.
- **Handoff required** means this Skill must not design the option.

---

## 7. Select the permitted water-based system family

Selection proceeds only among:

- Wet pipe
- Dry pipe
- Double-interlock preaction

Do not create a universal default.

### 7.1 Wet pipe

Select wet pipe when:

- The basis matrix supports it.
- Climate and space conditions permit it.
- Water sensitivity does not require a different allowed family.
- The owner or carrier does not require dry or double-interlock.
- The downstream density, duration, and supply consequences are accepted.

### 7.2 Dry pipe

Select dry pipe only when:

- The basis matrix or cited project source supports it.
- Freeze or space conditions require it.
- The dry design-area, delivery-time, air/nitrogen, corrosion, and supply consequences are carried.
- The applicable dry-pipe source is cited.

Do not derive a dry-pipe basis from a double-interlock source without an explicit cited connection.

### 7.3 Double-interlock preaction

Double-interlock is permitted within company scope but is not the FM default.

If selected:

- Record FM DS 5-32 January 2026 §2.4.1.1 and §2.4.1.2 as carrier comparison evidence.
- Carry the applicable dry-design area.
- Carry the ≤30-second delivery requirement where FM DS 5-32 §2.4.3.2.1.2(D) applies.
- Carry supervisory air/nitrogen.
- Carry corrosion and pipe-material requirements.
- Carry the effect on pump, tank, loop, and zoning work.
- Do not describe double-interlock as prohibited by FM or AXA XL.
- Do not replace it with single-interlock.

### 7.4 Wet-versus-double-interlock preview

When FM DS 5-32 January 2026 quantitative values apply, a concept-stage preview may be shown without running the density-area Skill:

```text
Wet:
0.20 gpm/ft² × 2,500 ft² = 500 gpm
500 gpm + 250 gpm hose = 750 gpm
750 gpm × 60 min = 45,000 gal

Double-interlock dry:
0.20 gpm/ft² × 3,500 ft² = 700 gpm
700 gpm + 250 gpm hose = 950 gpm
950 gpm × 60 min = 57,000 gal

Difference:
950 − 750 = +200 gpm
57,000 − 45,000 = +12,000 gal
200 / 750 = 26.67%
12,000 / 45,000 = 26.67%
```

Label the preview `derived` only when the inputs are grounded and the arithmetic is independently checked.

This preview is not a generic dry-pipe calculation. If the system is ordinary dry pipe rather than double-interlock, use the applicable cited dry basis and hand off to `density-area-dry-increase`.

---

## 8. Li-ion topology gate

Consume Li-ion topology from the caller and the basis-matrix result.

FM DS 5-32 January 2026 §2.3.1.4 and §2.4.3.6 govern only where their topology conditions apply.

### 8.1 Distributed in-rack Li-ion

Where the basis matrix confirms distributed in-rack Li-ion in an applicable DP room:

- Preserve the FM DS 5-32 January 2026 §2.4.3.6.4.1 hard bar against clean-agent and hybrid protection.
- Do not treat the bar as a code prohibition.
- Do not elect mist; company practice remains refused.
- Keep the water-based selection within wet/dry/double-interlock scope.
- Record that water is used for cooling and surrounding/rack protection, not necessarily cell-fire extinguishment.
- Hand off Li-ion-specific criteria to the applicable ESS or Li-ion Skill.

The bar is topology-dependent. If the topology changes, reopen the selection rather than carrying the prohibition permanently.

### 8.2 ESS or Li-ion UPS room

Route to:

- `ess-isolation-venting-and-duration`
- `occupancy-hazard-fork`
- The basis-matrix result
- Any applicable owner, AHJ, or insurer RFI

Do not classify or design the ESS room here.

### 8.3 Stored or staged Li-ion

Route to the applicable storage and commodity classification work. Do not apply the data-hall BBU rule to stored or staged material.

---

## 9. Objective → selection decision

For each space:

1. State the objective.
2. State the vendor or conceptual proposal.
3. State the physics lens.
4. Apply the basis-matrix result.
5. Apply the hard company scope gate.
6. Select wet, dry, or double-interlock, or return `prohibited`, `deferred`, `unresolved`, or `handoff`.
7. Record lifecycle consequences.
8. Record all follow-on handoffs.

### 9.1 Selection statuses

Every space must receive one primary selection status **and** a Status-register token (§12.3 / §15.3):

| Selection status | Meaning | Typical Status-register token |
|---|---|---|
| `selection decision` | Wet, dry, or double-interlock selected within scope | `grounded` or `provisional` |
| `comparison-only` | Carrier/vendor/physics option recorded but not selected (incl. SI/NI ranking) | `comparison-only` |
| `prohibited` | Company, carrier, owner, or code condition bars the option | `RFI-variance` when company-fence; else `handoff` |
| `deferred` | Valid concept, but another Skill owns feasibility or design | `handoff` |
| `unresolved` | Required basis, topology, owner direction, or source is incomplete | `unresolved` |
| `handoff` | Another Skill must decide or design the option | `handoff` |
| `RFI-variance` | Company-fence gate (SI/NI/foam/mist presented as election/BOD) | `RFI-variance` |

### 9.2 Objective foreclosure

If the objective cannot be delivered by the controlling permitted system:

- Mark `FORECLOSED — not traded away`.
- State the controlling prohibition or limitation.
- Preserve the lifecycle benefit the rejected concept would have provided.
- Do not make the result sound like a preference.
- Create the relevant `RFI-variance` gate or `handoff`.

---

## 10. Vendor concept accept/amend/reject

Use the following decision structure.

| Verdict | Use when |
|---|---|
| `Accept` | Vendor concept agrees with the permitted system family and basis-matrix result |
| `Amend` | Medium is within scope but system family, primary/adjunct relationship, space routing, or lifecycle control is wrong or incomplete |
| `Reject` | Vendor concept selects a prohibited company medium/system, conflicts with a hard carrier/code/owner bar, or substitutes a special medium for the required water-based basis |
| `Defer` | Concept may be valid but requires a separate special-hazard, enclosure, listing, owner, or AHJ determination |

### Concepts outside wet, dry, and double-interlock

If a vendor concept leads with gas, clean agent, foam, mist, or any medium other than wet pipe, dry pipe, or double-interlock preaction, record it as rejected or deferred and stop. Do not size that medium. A water-based concept that is only incomplete is an amend, not a reject.

## 11. Lifecycle consequence register

Selection must not be based on discharge effectiveness alone.

Use one row per material/system option:

| Space | Objective | Option | Lifecycle stage/factor | Push | Evidence | Selection effect | Status | Handoff |
|---|---|---|---|---|---|---|---|---|

Preserve the following lifecycle factors:

- Pre-fire operating condition
- Incipient-stage response
- Flaming-stage control
- Power isolation
- Water damage
- Drying and cleanup
- Runoff containment
- Agent hold time
- FRS access
- HDD or equipment acoustics
- Obscuration
- Reinstatement and loss of cover
- Reset, recharge, and service availability

Suggested stage labels:

- `S0` pre-fire
- `S1` incipient
- `S2` flaming
- `S3` deployment
- `S4` FRS intervention
- `S5` immediate aftermath
- `S6` resumption
- `S7` reinstatement

### 11.1 Detection versus medium

Electronics may smolder before flaming. Heat-actuated heads do not provide incipient-stage detection.

Where FM DS 5-32 January 2026 §2.4.2 applies:

- Treat FM-Approved VEWFD as a separate detection requirement.
- Do not claim the medium alone handles the incipient stage.
- Hand off VEWFD layout to the detection Skill.
- Hand off preaction release logic to `preaction-releasing-c-and-e-soo`.

### 11.2 Power isolation

Do not assume gaseous protection eliminates power isolation.

Record the applicable carrier/owner requirement and hand off means to `power-isolation-disconnect-control`.

For water-based protection, do not release water into energized equipment until the isolation sequence and incident procedure are defined.

### 11.3 Reinstatement

For every selected or deferred option, record:

- Loss-of-cover condition
- Reset/recharge requirement
- Insurer notification
- Fire-watch requirement
- IT or operational restart condition
- Handoff to `itm-design-for-testability` or `commissioning-ist-acceptance-packet`

---

## 12. Provenance, Status register, and flags

Use a **Status-register token** on every election/row, plus provenance labels and flags.

### 12.1 Provenance labels (claim quality)

| Label | Meaning |
|---|---|
| `grounded` | Directly supported by a held source with section/page and edition/date |
| `derived` | Arithmetic from grounded inputs, independently checked (e.g. wet-vs-DI preview) |
| `synthetic` | Caller-supplied or invented project placeholder |
| `verify` | Edition, listing, applicability, or source requires verification (`[V]`) |

### 12.2 Flags

- `[SYN]` — synthetic project or owner placeholder
- `[V]` — unverified, unpinned, secondary, or unmined requirement
- `[U]` — unresolved
- `CONFLICT` — source conflict
- `HANDOFF` — another Skill owns the next action

Do not convert a carrier or owner qualitative statement into a numeric selection.

### 12.3 Status register (mandatory every run)

Emit with Outputs. **Every election / matrix row / gate gets a Status-register token.** Vocabulary matches the ITM / campus bar:

| Status | Use on this Skill |
|---|---|
| `grounded` | Company election (wet/dry/DI) pinned to consumed basis-matrix controlling row + company scope + cited sheet/edition |
| `provisional` | Selection conditional on provisional insurer-union or open non-gating RFI; assumptions stated |
| `unresolved` | Blocking hole: missing space list, missing/incomplete basis-matrix system-family row, missing Li-ion topology where the FM bar may apply, empty required input |
| `comparison-only` | SI/NI / other preaction evidence; FM DS 5-32 preference ranking; physics/vendor options recorded but **not** elected |
| `handoff` | Work owned elsewhere: occupancy-hazard-fork; density-area; pump-envelope; out of scope; special-hazard; releasing C&E; water-spray |
| `RFI-variance` | Company-fence gate: SI/NI/foam/mist (or other prohibited medium) presented as election/BOD; prohibited system family stop |

**Rules:**

- SI/NI evidence rows → `comparison-only`. SI/NI as election/BOD → **Stop** with `RFI-variance`.
- Foam as election/design → `RFI-variance` (prohibited). Mist as election/design → `RFI-variance` + `PRACTICE REFUSED`.
- Do **not** emit a final `grounded` selection from an `unresolved` basis-matrix system-family row.
- Preserve `[SYN]` / `[V]` beside the Status-register token; do not collapse them into it.

---

## 13. Directional NFPA 13-2025 delta

Consume the delta from `most-stringent-basis-matrix`.

This Skill may summarize a selection-relevant delta, but must not rebuild the code comparison.

Rules:

- NFPA 13-2025 is the delta baseline, not automatically the enforced code floor.
- The enforced edition and jurisdiction instrument come from the basis-matrix result.
- If the matrix marks the delta `[V]`, preserve `[V]`.
- Do not invent a general NFPA 13-2025 dry/double-interlock section.
- Do not present a carrier uplift as a code requirement.
- For mist, do not create a numeric NFPA 13 delta; mist is a different listing-based design paradigm and is refused here.
- For special hazards, use `n/a` where NFPA 13 is not the governing standard and hand off to the relevant Skill.

---

## 14. Handoffs

| Work | Handoff |
|---|---|
| Three-layer code/carrier/owner matrix | `most-stringent-basis-matrix` |
| IBC, NFPA 13 hazard, FM HC, storage/commodity classification | `occupancy-hazard-fork` |
| Density, remote area, dry-area increase, demand | `density-area-dry-increase` |
| Pump, tank, loop, supply curve, margin | `pump-envelope` |
| Clean-agent enclosure and retention feasibility | the out-of-scope method |
| Clean-agent concentration and quantity | the out-of-scope method |
| Preaction releasing logic and sequence | `preaction-releasing-c-and-e-soo` |
| Power isolation and disconnect controls | `power-isolation-disconnect-control` |
| ITM and design-for-testability | `itm-design-for-testability` |
| Commissioning and acceptance | `commissioning-ist-acceptance-packet` |
| Assignment packet retrieval/adaptation | the input packet |
| Outdoor oil-filled transformer water spray | `power-block-transformer-water-spray` (does not replace wet, dry, or double-interlock for the building) |
| ESS isolation, venting, duration, and Li-ion room basis | `ess-isolation-venting-and-duration` |
| VEWFD layout and detection | Detection/releasing Skill |
| CAD, BIM, delegated design | Outside Skills |

Consume existing packets and matrices. Do not rebuild them.

---

## 15. Output

Write a technology-objective selection matrix only to the caller-named path, or return it in the response if no path was supplied.

### 15.1 Minimum selection matrix

| Space | Taxonomy | Objective | Vendor concept | Physics lens | FM/carrier status | Company-permitted option | Selected medium/system | Selection status | Status-register token | Controlling basis pointer | Lifecycle consequence | Delta pointer | Flags | Handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 15.2 Required companion sections

Include:

1. Consumed basis-matrix status
2. Scope-gate result
3. Objective register
4. Space taxonomy
5. Permitted-versus-physically-favored table
6. Selection matrix
7. Vendor accept/amend/reject/defer record
8. Lifecycle consequence register
9. Wet-versus-double-interlock preview where applicable
10. **Status register** (mandatory — §12.3 / §15.3)
11. `[SYN]`, `[V]`, `[U]`, and handoff register
12. Directional NFPA 13-2025 delta references
13. Final handoff list

### 15.3 Status register (mandatory emit)

Every run must emit a Status register covering **each space election and each comparison/gate row**:

| Space / row | Election or evidence | Status-register token | Controlling basis pointer | Flags | Notes |
|---|---|---|---|---|---|

Tokens allowed: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.

Minimum checks:

- Wet/dry/DI elections that close → `grounded` or `provisional` (never silent `grounded` on provisional union).
- SI/NI / FM ranking / physics-only options → `comparison-only`.
- SI/NI/foam/mist as requested election → `RFI-variance` (and **Stop** per Hard scope).
- Special-hazard / clean-agent / density / pump work → `handoff`.
- Missing required basis or topology → `unresolved`.

### 15.4 Do not emit

Do not emit:

- IBC occupancy classification
- NFPA 13 OH classification
- FM HC classification from scratch
- Storage commodity classification from scratch
- Density-area `calcs`
- Pump or tank sizing
- Hydraulic tree
- Mist nozzle/listing design
- Foam proportioning
- Clean-agent quantity or retention design
- Releasing C&E
- CAD or drawings
- A rebuilt dual-carrier BOD
- A final selection from an unresolved basis-matrix system-family row

---

## 16. Stop conditions

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items; input gaps → stated `ASSUMED`, flagged) when:

1. The space list is missing.
2. The consumed `most-stringent-basis-matrix` result is missing.
3. The matrix does not identify jurisdiction status, carrier status, owner evidence, or system-family constraints.
4. The system-family row is unresolved for the space.
5. The caller requests single-interlock, non-interlock, or another prohibited preaction type as election/BOD → **Stop** with `RFI-variance` (evidence may remain `comparison-only`).
6. The caller requests foam design or specification → **Stop** with `RFI-variance` (prohibited).
7. The caller requests mist design or specification → **Stop** with `RFI-variance` (`PRACTICE REFUSED`).
8. The caller requests clean-agent, hybrid, aerosol, hypoxic, water-spray, or other special-hazard design in this Skill.
9. Li-ion topology is missing where it could trigger the FM bar.
10. The caller asks this Skill to run occupancy, density-area, pump, hydraulic, or detailed special-hazard work.
11. The caller asks for a final code-compliant selection while a required basis-matrix row is unresolved.
12. A source is only an unmined root PDF or pointer.
13. The caller requests writing outside the caller-named output path.

An empty BCP is not itself a stop. Mark the objective `[SYN]` and continue.

---

## 17. Citations

Use section and edition/date for every code, insurer, or standard requirement.

### FM DS 5-32

`FM DS 5-32 January 2026`

- Water-based preference: §§2.4.1.1 and 2.4.1.3
- Interlock ranking and double-interlock warning: §§2.4.1.1 and 2.4.1.2
- Wet/dry preaction fork: §2.4.3.2.1.2
- Water-delivery time: §2.4.3.2.1.2(D)
- VEWFD and airflow: §2.4.2
- Li-ion BBU scope: §2.3.1.4
- Clean-agent/hybrid Li-ion bar: §2.4.3.6.4.1
- Sprinkler density/area: §2.4.3.3.1.1
- Hose and duration: §§2.4.1.5 and 2.4.1.6
- Clean-agent hold/de-energization requirements, where applicable: §2.4.3.2.3
- Mist routing: §2.4.3.3.2.1 and Fig. 2.4.3.1.1.1

### FM DS 4-9

`FM DS 4-9 October 2018 / Interim Revision July 2023`

- Clean-agent supplementary default: §2.2.1.2
- Clean-agent supplementary-versus-sole-protection posture: §3.2.1

### AXA XL

`AXA XL March 2026`

- Ordinary Hazard Group 1 and no density/area method: p. 8
- Single-interlock preference and double-interlock penalty: p. 8
- Li-ion density reinforcement: p. 8
- Power isolation and damper posture: pp. 4 and 9
- Heat-damage onset: pp. 4 and 9

### Other selection sources

- Euralarm selection method: §4.1 p. 5
- Euralarm physics matrix: §5 p. 9
- Euralarm lifecycle factors: §6.2.1–§6.2.7
- FSSA/FIA Phase 2 airflow evidence: cite the held 2023 source and tested envelope; do not generalize beyond it.
- : foam scope and routing
- : listing-specific mist architecture and refusal fence
- : enforced-versus-latest and delta-baseline rules

---

## Design practice

1. Objective first, then permitted medium/system family.
2. Physics is a lens; code, insurer, owner, and company scope control the selection.
3. Consume `most-stringent-basis-matrix`; do not duplicate it.
4. Select only wet pipe, dry pipe, or double-interlock preaction.
5. Single-interlock and non-interlock are `comparison-only` — never company election.
6. Foam is prohibited.
7. Mist is `PRACTICE REFUSED`.
8. Clean agent, hybrid, aerosol, hypoxic, building deluge, and other special media are record-only and routed (`handoff`). Outdoor oil-filled transformer water spray is `power-block-transformer-water-spray`. It does not replace wet, dry, or double-interlock for the building.
9. A barred objective is foreclosed, not traded away.
10. Do not reject gaseous technology solely because of airflow.
11. Preserve the vendor’s valid lifecycle argument even when rejecting the concept.
12. Show and verify wet-versus-double-interlock preview arithmetic when FM values apply.
13. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.
14. Keep `[SYN]`, `[V]`, and Status register visible.
15. Never turn an unresolved basis into a final selection.
16. SI/NI/foam/mist as election/BOD → **Stop** with `RFI-variance`; do not silent-substitute wet/dry/DI.

---

## Check before you finish

1. Confirm the space list and caller-named output path.
2. Consume the `most-stringent-basis-matrix` result.
3. Confirm jurisdiction, carriers, owner evidence, and system-family constraints are present.
4. Apply the wet/dry/double-interlock scope gate.
5. Stop on single-interlock, non-interlock, foam, or mist election/BOD requests with `RFI-variance` (SI/NI evidence may remain `comparison-only`).
6. Record objectives first; mark empty BCP objectives `[SYN]`.
7. Classify spaces using white/grey/churn/ordinary plus separate special-hazard routing.
8. Split UPS/BBU from switchgear and staging/storage from cable routes.
9. Screen physics using Euralarm/Siemens as non-governing evidence.
10. Build the permitted-versus-physically-favored table.
11. Select wet, dry, or double-interlock only.
12. Preview wet-versus-double-interlock consequences where cited FM values apply.
13. Accept, amend, reject, or defer the vendor concept.
14. Record lifecycle consequences and whether they changed the decision.
15. Mark selection status per space (§9.1).
16. **Emit Status register** (mandatory): `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` on every election/row (§12.3 / §15.3).
17. Preserve `[SYN]`, `[V]`, and basis-matrix unresolved flags beside Status-register tokens.
18. Add all required handoffs.
19. Write only to the caller-named path.
