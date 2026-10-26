---
name: Occupancy hazard fork
description: >-
 use this when classifying each space in a US data-center program for IBC
 occupancy, the §903.2 sprinkler trigger, NFPA 13 occupancy/hazard, insurer
 hazard category, mixed-occupancy greatest-hazard effects, and ESS/Li-ion
 overlays before density-area or pump work.
---
# Occupancy hazard fork

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center classification recipe.

This Skill walks a program **space by space** and emits a hazard-classification schedule. It owns:

> IBC occupancy group → §903.2 sprinkler trigger → NFPA 13 / insurer hazard route → technology and special-hazard overlays → boundary consequence → downstream handoff

It does **not** own:

- Jurisdiction or edition resolution
- Three-layer carrier/owner reconciliation
- System-family election
- Density×area calculation
- Pump or water-supply sizing
- Storage commodity design
- Special-hazard suppression design
- Allowable-area, egress, or smoke-control design

Consume the completed:

- `most-stringent-basis-matrix`
- `suppression-technology-selection`

Do not rebuild their jurisdiction register, carrier union, owner evidence, or permitted system election.

Write output only to the caller-named path. Do not write to,,, or .

---

## 1. Classification principles

Keep these questions separate:

| Question | Classification | Result |
|---|---|---|
| What does the building or space most nearly resemble? | IBC occupancy group | B, F-1, S-1, H, or another supported group |
| Does the adopted code require sprinklers? | IBC/IFC §903.2 trigger | Trigger section and conclusion |
| What hazard class applies once protection is required? | NFPA 13 occupancy/hazard | OH1, OH2, EH, or another supported class |
| What insurer category applies? | FM HC or AXA OH | HC-1/2/3 or AXA OH Group 1 |
| Is the space actually storage? | FM/NFPA/IFC storage route | Commodity classification and storage handoff |
| Is a special overlay present? | NFPA 75, ESS/Li-ion, telecom, switchgear, transformer, generator | Parallel floor or specialist handoff |

A data hall may correctly be:

> IBC B or F-1 + NFPA 13 OH1 + FM HC-2 + NFPA 75 ITE area

These are different taxonomies. Do not merge them.

### 1.1 Upstream ownership

The completed `most-stringent-basis-matrix` result supplies:

- Enforced IBC/IFC and referenced-standard editions
- Applicable carrier or carriers
- Dual-carrier union, where applicable
- Owner evidence status
- Provisional or unresolved basis rows
- Controlling basis pointers
- Directional deltas versus NFPA 13-2025

The completed `suppression-technology-selection` result supplies:

- Space objective
- Selected or proposed system family
- Company-permitted system status
- Comparison-only system evidence
- Prohibited or deferred technology status

If either result is missing, do not stop: run it or carry a stated `ASSUMED` result (flagged), and mark the classification ASSUMED-based.

### 1.2 Company system-family fence

Only these may appear as selected systems:

- Wet pipe
- Dry pipe
- Double-interlock preaction

These may appear only as comparison evidence:

- Single-interlock preaction
- Non-interlock preaction
- Other preaction types

If an upstream result requests single-interlock or non-interlock:

1. Record the requested system.
2. Mark it `comparison-only`.
3. Return an `RFI/variance` gate.
4. Do not substitute another system.

This Skill does not elect a system family.

---

## 2. Required inputs

The caller must supply:

1. A completed `most-stringent-basis-matrix` result.
2. A completed `suppression-technology-selection` result.
3. A space list with one row per space.
4. Declared mixed-occupancy and mixed-hazard boundaries.
5. The caller-named output path, unless the schedule is to be returned in the response.

### 2.1 Space-list fields

Required:

| Field | Rule |
|---|---|
| `name` | Unique space identifier |
| `area_ft2` | Project value; `[SYN]` if synthetic |
| `contents` | Actual installed, stored, or processed contents |
| `ceiling_height_ft` | Roof deck/ceiling height |
| `occupied_vs_storage` | `occupied`, `storage`, or `mixed` |
| `fire_area_id` | Declared fire-area boundary, if known |
| `boundary_register` | Boundary status for adjacent differing spaces |

Required where applicable:

- Li-ion energy per rack
- Room total energy
- Chemistry
- Installed versus stored/staged state
- State of charge for stored/staged batteries
- Public/private telecom function
- AC-powered versus DC-powered telecom function
- Signal-processing equipment area
- MV voltage
- Oil-filled equipment status
- Grouped cable status
- Concealed-space status
- Selected system family from `suppression-technology-selection`

Do not invent a space list, contents, fire-area boundary, carrier, owner standard, battery topology, or jurisdiction.

### 2.2 Boundary register

Every boundary that could change classification must be listed:

- HC-2 ↔ HC-1
- IBC group change
- Occupied ↔ storage
- Storage ↔ hall
- ESS/UPS room ↔ other space
- MMR/telecom ↔ private IT
- Switchgear ↔ occupied or storage
- Concealed space ↔ occupied space

Allowed values:

- `verified-rated`
- `unrated-open`
- `unresolved`

For `verified-rated`, state the known hourly rating or mark it `[V]`.

An omitted boundary is not treated as harmless. Missing boundary data → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (assume the higher-hazard case).

### 2.3 Basis-status values

Every output row must carry one status:

| Status | Meaning |
|---|---|
| `grounded` | Supported by a held, edition-pinned source |
| `provisional` | Inherited from a provisional basis-matrix result |
| `unresolved` | Required classification or source cannot be closed |
| `comparison-only` | Carrier, vendor, or alternate classification recorded but not controlling |
| `handoff` | Another Skill owns the next determination |

---

## 3. Consume upstream results

### 3.1 Basis-matrix intake

Confirm that the basis result identifies:

- Jurisdiction status
- Enforced IBC/IFC edition
- Enforced NFPA pins where applicable
- Carrier status: FM, AXA XL, dual, or none
- Owner evidence status
- Controlling per-parameter rows
- Provisional insurer-union rows
- Unresolved code, carrier, or owner rows

Do not independently resolve a dual-carrier union. If the result is dual-carrier, preserve:

- FM classification
- AXA classification
- Controlling union result
- Any carrier-specific comparison evidence

Do not stop merely because the carrier is dual.

### 3.2 Technology-selection intake

Confirm that the technology result identifies:

- Objective
- Proposed medium
- Selected or proposed system family
- Company-permitted status
- Comparison-only or prohibited status
- Special-hazard handoffs

Use the selected system family only for a downstream demand-area hint. Do not redesign it here.

### 3.3 Inherited edition pins

Do not use a generic “2024-cycle” edition table as an enforced default.

Use the edition pins inherited from `most-stringent-basis-matrix`. If a required pin is unresolved:

- Preserve the inherited `[V]` or `unresolved` status.
- Do not declare the row final or code-compliant.
- Do not silently substitute the latest edition.

Citations must use:

> `instrument edition §section`

Example:

> `IBC-2024 §302.1`

---

## 4. IBC occupancy and §903.2 trigger

Keep IBC classification separate from NFPA 13 and insurer hazard.

### 4.1 Data-center group

IBC-2024 §202 defines a data center using ITE load and conditioned-floor-area criteria but does not assign a dedicated Chapter 3 occupancy group.

Use IBC-2024 §302.1:

> classify by the use the building or space most nearly resembles

Defensible data-center candidates may include:

- B — Business
- F-1 — /Industrial, moderate hazard
- S-1 — Storage, moderate hazard
- H — High Hazard, only where a supported MAQ/control-area analysis requires it

Use the project’s adopted IBC edition from the basis matrix, not an assumed edition.

### 4.2 §302.1 resemblance record

Record:

- Primary group
- Alternate candidate groups
- Facts supporting the primary
- Facts supporting alternates
- AHJ precedent, if available
- ESS, storage, process, staffing, and operational facts
- `[V]` items requiring AHJ confirmation

Use this directional screen:

| Fact pattern | Candidate effect |
|---|---|
| Human-centered office use, staff density, white space ancillary | Supports B |
| Electronic data processing or unmanned server-hall resemblance | B remains credible |
| Continuously operating process hall, integrated operational power/ESS | Elevates F-1 consideration |
| Dedicated-use ESS building | F-1 under IFC-2024 §1207.7.1 |
| Static, rack-dense, very-low-staff, shell/dark-hall use | Supports S-1 |
| MAQ or hazardous-material exceedance | May require Group H/control-area analysis |

Do not make B, F-1, or S-1 a universal data-center default.

Integrated ESS in a larger building may affect the §302.1 rationale and impose an IFC Ch. 12 overlay, but it is not automatically a Group F-1 assignment.

### 4.3 Group H and MAQ gate

If battery electrolyte, fuel oil, chemicals, or another hazardous material may exceed an adopted maximum allowable quantity:

- Do not bury the issue under B/F-1/S-1.
- Record a `Group H/control-area review`.
- Mark the row `unresolved` or `handoff`.
- Route to the applicable fire-area and hazardous-material process.

**Battery rooms are S-1 / F-1, not H, where the 2024 IBC is adopted** (KB *IBC occupancy and sprinkler trigger fork* ; ICC Li-ion early-release guidance):
- 2024 IBC added §304.1 **B** (Li-ion testing / R&D), §306.2 **F-1** (ESS in dedicated-use buildings; ESS and equipment containing Li-ion; Li-ion batteries), §311.2 **S-1** (Li-ion / Li-metal batteries).
- ICC guidance §4.2.2: completed batteries are **not** summed toward Table 307.1(1) MAQs. Group H is for cases outside the Ch. 43 / §1207 / §903 / §907 framework or raw-material MAQ exceedance — **guidance text, not code**; cite the 2024 IBC sections where adopted.
- A spare-BBU / battery staging room → **S-1** (2024 IBC) → sprinkler trigger follows §903.2.9 (+ 2027 IFC Ch. 43 §4303.3.2 where adopted).
- On **IBC 2018 / 2021** AHJs (e.g. NM IBC 2021; unincorporated DeKalb County IL IBC 2021) the listings are absent → request a **written building-official S-1 determination** (ICC §4.2.2 as rationale) rather than accepting a Group H default.

### 4.4 §903.2 sprinkler triggers

Evaluate every credible IBC group and cite the adopted edition.

For an IBC-2024/IFC-2024 basis, the principal triggers are:

| Candidate or condition | Trigger |
|---|---|
| F-1 | `IBC/IFC-2024 §903.2.4`: single fire area, story count, or aggregate area thresholds; special manufacturing triggers where applicable |
| S-1 | `IBC/IFC-2024 §903.2.9`: single fire area, story count, or aggregate area thresholds; special storage triggers where applicable |
| B | No general business-area trigger; `§903.2.2` concerns ambulatory care, not a general data-center threshold |
| Windowless story | `IBC/IFC-2024 §903.2.11.1` |
| High-rise | `IBC/IFC-2024 §403.3` |
| Underground | `IBC/IFC-2024 §405.3` |
| ESS | `§903.2` references IFC-2024 Ch. 12 where applicable |
| Battery R&D/testing | `IBC/IFC-2024 §903.2.2.2` where applicable |

Do not use the erroneous Group B 5,000 ft² or occupant-load-500 shortcuts.

**State substitutions to check before applying the §903.2 table** (KB ; cite the state instrument):
- **Georgia** (Rule 120-3-3 redline, Nov 2025, effective date not printed): IFC 903.2 is substituted — the new-building sprinkler requirement comes from **NFPA 101 (2024)** occupancy chapters; the IBC still governs sprinklers tied to construction type / area-height increases. Georgia keeps a 903.2.1 **telecommunications-building** omission (supervised fire alarm + 2-h barriers) — it does not say data center; **do not take it as a DC omission** (shop: halls sprinklered wet/dry/DI; FM DS 5-32 would not follow it).
- **New Mexico** (14.7.2 NMAC, eff 2023-07-14, IBC 2021): **deletes the §903.2 exception** (the telecom equipment-space omission `[inference]`) — no building-code omission argument in NM.
- **Maryland** (COMAR 09.12.51, IBC 2021 statewide; 2024 IBC proposed): no MD change to §903.2 triggers.

If the building is a large, windowless hyperscale hall, the schedule may conclude that sprinklers are required throughout under the applicable general trigger. That conclusion does not resolve the IBC group or downstream design.

### 4.5 NFPA 75 parallel floor

Where NFPA 75 is adopted or referenced, evaluate it independently of the IBC area trigger.

The current corpus pins the following to NFPA 75-2024, subject to official-primary verification (§6.1.3.2 and §9.1.1 verified, NFPA 75-2020/2024; §9.1 names no sprinkler system type):

- Building construction (fully sprinklered building per NFPA 13 OR one of the listed construction types): §6.1.1 [CODE NFPA 75-2024 §6.1.1: Type I (442/332) or Type II (222/111), or single-story Type II (000); NFPA 75-2020 §6.1.1: Type I (443/332) or Type II (222/111), or single-story Type II (000); §6.1.1.1 permits modification by Ch. 4 risk assessment;]
- ITE-area separation floor: §6.1.3.2
- Automatic sprinkler protection: §9.1.1
- Listed smoke detection per NFPA 72: §9.2.1

NFPA 75-2024 removed Li-ion protection requirements; route batteries to NFPA 855 and IFC Ch. 12.

Record NFPA 75 as:

- `code-floor`
- `insurer/owner overlay`
- `not adopted`
- `unresolved`

Do not treat NFPA 75 as the complete data-center design basis.

### 4.6 §507.4 consequence

Record §507.4 only as a possible allowable-area handoff:

- One story
- Group B/F/M/S as applicable
- NFPA 13 throughout
- At least 60 ft of public ways/yards on all sides

Do not perform allowable-area calculations here. If the site condition is unknown, mark `[V]` and hand off.

---

## 5. Occupancy, storage, telecom, and special-hazard fork

Classify by actual use, not room name.

| Space condition | Classification route | This Skill result |
|---|---|---|
| Data hall / white space | Occupancy hazard | IBC group + NFPA/insurer class |
| I/O distribution | Occupancy hazard | Usually FM HC-2 where FM Table C-1 applies |
| BOC/process control | Contents-dependent occupancy | HC-2 or HC-1 with rationale |
| NOC/monitoring | Occupancy hazard | Usually FM HC-1 |
| Private enterprise/VOIP MMR | NFPA 75 / DS 5-32 path | Route and classify accordingly |
| Public telecom/DC plant | NFPA 76 / DS 5-14 path | Telecom handoff |
| Receiving/staging/decrating | Storage commodity | Off HC table; storage handoff |
| Installed ESS/Li-ion UPS | ESS overlay | Off ordinary HC table; ESS handoff |
| In-rack Li-ion BBU | Hall occupancy plus BBU overlay | Preserve hall class; apply topology gate |
| Stored/staged Li-ion | Storage plus Li-ion overlay | DS 7-112/storage handoff |
| Non-Li stationary battery | Occupancy plus battery sheet | FM DS 5-28 route |
| MV switchgear | Occupancy plus object gate | DS 5-19 route |
| Transformer/generator/fuel | Special hazard | Off HC table; specialist handoff |

The same physical room may change route during a phased project. Classify the worst supported configuration the room will see, and record the transition trigger.

---

## 6. FM HC classification

Use this section only where FM applies or where the basis matrix identifies FM classification as a comparison row.

### 6.1 Primary FM sources

Use:

- `FM DS 3-26 April 2025` Table 2.2.2
- `FM DS 3-26 April 2025` Appendix C Table C-1
- `FM DS 3-26 April 2025` §2.2.5
- `FM DS 5-32 January 2026`
- `FM DS 2-0 October 2021 / Interim Revision January 2024` for installation routing where DS 5-32 is silent

FM DS 5-32 is an occupancy-specific overlay. DS 2-0 remains the installation base where DS 5-32 does not speak.

### 6.2 FM named-space map

| Space | FM category | Basis |
|---|---|---|
| Data hall / IT Facilities | HC-2 | DS 3-26 Appendix C Table C-1 |
| I/O Distribution Room | HC-2 | DS 3-26 Appendix C Table C-1 |
| Control Rooms | HC-2 | DS 3-26 Appendix C Table C-1 |
| Electrical Rooms | HC-2 | DS 3-26 Appendix C Table C-1 |
| NOC/monitoring/network-operations control room | HC-1 | DS 3-26 Appendix C Table C-1 |
| Telecom room | Usually HC-1 only after telecom regime gate | DS 3-26 Appendix C Table C-1, subject to DS 5-14/DS 5-32 routing |
| Laboratory | HC-1 | DS 3-26 Appendix C Table C-1 |
| Support office | HC-1 | DS 3-26 Appendix C Table C-1 |
| Utility room inside support space | May be HC-2 | Contents and applicable named-space rule |
| AC/DC switchyard building | HC-2 | DS 3-26 Appendix C Table C-1 |
| HVDC station | HC-3 | DS 3-26 Appendix C Table C-1 |

If a space is not named in Table C-1:

1. Classify by predominant contents under Table 2.2.2.
2. Record the reasoning.
3. Mark `[V]`.
4. Request AHJ/FM concurrence where the result affects the basis.

### 6.3 Control-room fork

Do not classify by the word “control.”

- Building-operations, process, or IT-bearing `Control Room` → HC-2 candidate.
- Monitoring-only `NOC` → HC-1 candidate.
- Uncertain contents → hold HC-2 provisionally and mark `[V]`.

### 6.4 Concealed-space overlay

For combustible concealed spaces under raised floors or above ceilings:

- Record the concealed space as a separate schedule row.
- Preserve the generic FM concealed-space route as comparison evidence.
- Apply the more-stringent FM DS 5-32 January 2026 §2.4.3.4.1.1 classification/design-route pointer where applicable.
- Do not calculate flow or concurrency.
- Hand off concurrency and hydraulic remote-area questions.
- Code floor for concealed-space omission: NFPA 13-2025/2022 §9.2.1 (2016 §8.15.1) captured in full, structure identical across editions ; cite the specific omission item by edition.
- **Elevator pit delta:** NFPA 13-2025 §9.2.14.2 "Sprinklers shall not be required in elevator pits" reverses 2022 §9.3.6.1 / 2016 §8.15.5.1; 2025 §9.2.14.3 machine-room/hoistway omission drops the detection condition in 2022 §9.3.6.3 . Use the enforced edition (unamended 2024 I-Codes → 2022, pit heads required); print the 2025 delta. Verify with the engineer of record where the AHJ enforces 2025.

The classification conclusion is:

> concealed-space HC-2 route where DS 5-32 applies; separate system/handoff required

---

## 7. AXA XL and no-carrier routes

### 7.1 AXA XL

Where AXA XL controls, do not import FM HC numbers.

Record:

- AXA XL March 2026 white-paper occupancy: Ordinary Hazard Group 1 per NFPA 13.
- AXA XL’s single-interlock preference as comparison evidence only.
- Double-interlock `+30% design area + nitrogen` as a directional demand-area handoff, not a calculation.
- AXA XL PRC 17.10 partition posture as a carrier overlay.
- Controlling result from `most-stringent-basis-matrix`.

AXA XL does not provide a complete density, K-factor, or hydraulic method in the held white paper. Do not invent one.

### 7.2 No carrier

Where no insurer applies:

- Use the adopted code-floor classification.
- Use the enforced NFPA 13 edition from the basis matrix.
- Keep NFPA 13-2025 as the delta reference unless separately adopted.
- Do not treat the common OH1 white-space assumption as grounded without the primary section.

### 7.3 Dual carrier

For dual FM/AXA work:

- Show the FM HC row.
- Show the AXA OH row.
- Show the owner row if present.
- Show the controlling union result inherited from the basis matrix.
- Preserve carrier-specific differences.
- Do not MAX entire layers or silently select one carrier.

---

## 8. Telecom/MMR regime gate

A dedicated MMR, MDF, cable-entrance, or telecom-power room is not automatically white space and not automatically HC-1.

Use:

### 8.1 Required MMR inputs

- Public telecom/carrier function: yes/no
- Private enterprise IT function: yes/no
- AC-powered/VOIP or DC-powered switching
- Signal-processing equipment area
- MDF/cable-entrance/power/technical-support/standby-engine areas
- Facility-wide SPE area across all floors
- Enclosed-room combinations
- MMR boundary and separation status

### 8.2 Regime result

| Function | Route |
|---|---|
| Private enterprise IT or AC-powered VOIP | NFPA 75 / FM DS 5-32 path |
| Public telecom, TCO/MTSO, or DC-powered switching | NFPA 76 / FM DS 5-14 path |
| Mixed private/public or uncertain | `unresolved`; telecom handoff and RFI |

FM DS 5-14 April 2012 / Interim April 2025 §1.0–§1.1 routes VOIP to DS 5-32 and covers TCO/MTSO/DC-powered switching.

Do not import DS 5-14’s communication-equipment suppression path into a DS 5-32 white-space hall.

### 8.3 Telecom aggregation and room merge

Record:

- SPE area aggregated across the telecommunications facility where applicable.
- Most-restrictive-room effect where MDF, power, HVAC, or technical-support areas share one enclosure.
- Raised-floor/common-airflow condition.
- Detection classification as a handoff.

Detailed NFPA 76 classification and detection design belongs to the telecom/MMR Skill. NFPA 76-2024 VEWFD/EWFD criteria are held [CODE NFPA 76-2024 §8.5.3.1.2, §8.5.3.2.1]; other NFPA 76 committee-record citations remain `[V]`.

---

## 9. MV switchgear object gate

Use:

### 9.1 Required inputs

- Voltage: above or below 1000 V AC
- Metal-clad, vacuum, air, SF₆, minimum-oil, or bulk-oil gear
- Noncombustible room construction
- Other combustibles in the room
- Grouped cable or bus duct
- Transformer or generator apparatus in the same room
- Storage present or absent

### 9.2 Classification and routing

FM DS 3-26 Appendix C Table C-1 may support HC-2 for an Electrical Room. That HC classification does not decide apparatus protection.

| Object condition | Result |
|---|---|
| Standard >1000 V AC metal-clad/vacuum/air/SF₆ in noncombustible room | Retain HC-2 where Table C-1 applies; hand off the room package to **`mv-switchgear-room-package`** |
| Bulk-oil gear or exposed combustibles | Off ordinary room route; special-hazard RFI/handoff |
| Grouped combustible cable | Record cable overlay; hand off to applicable DS 5-31 route |
| Below 1000 V AC | Do not cite DS 5-19 as the primary voltage rule; use the applicable electrical-room basis |
| Storage in switchgear room | Record conflict; storage handoff and RFI |
| Transformer apparatus | Route to out of scope |

FM DS 5-19 October 2020 / Interim January 2024 §2.2.1 and §2.2.3 distinguish room protection from apparatus protection. Do not infer deluge merely from the word “switchgear.”

---

## 10. ESS and Li-ion overlays

Treat batteries by state and topology, not by building name.

### 10.1 Required battery fields

- Installed or stored/staged
- In-rack, dedicated room, or dedicated building
- Energy per rack
- Total room energy
- Chemistry
- State of charge, where stored/staged
- Adjacent spaces and boundary rating
- Carrier position
- Owner topology requirement

### 10.2 Overlay table

| Battery state | Primary route | Schedule result |
|---|---|---|
| In-rack BBU within FM DS 5-32 threshold | FM DS 5-32 | Hall remains occupancy row with BBU overlay |
| In-rack BBU above 20 kWh/rack | DS 5-32/DS 5-33 scope loop | `unresolved`; carrier RFI |
| Dedicated Li-ion ESS/UPS room | FM DS 5-33 + IFC Ch. 12 + NFPA 855 | Off ordinary HC table; ESS handoff |
| Dedicated-use ESS building | IFC-2024 §1207.7.1 | Group F-1 hard result, subject to adopted edition |
| Stored/staged Li-ion | FM DS 7-112 + storage route | Not HC; storage/Li-ion handoff |
| Non-Li stationary battery | FM DS 5-28 April 2021 §2.4.2 | HC-2 plus QR route where FM applies |

### 10.3 In-rack BBU threshold

FM DS 5-32 January 2026 §2.3.1.4 provides the in-rack BBU threshold conditions, including rack energy, shelf grouping, and aisle condition.

If the BBU exceeds the applicable threshold:

- Do not silently classify it as ordinary hall HC-2.
- Record the DS 5-32 → DS 5-33 referral.
- Record the DS 5-33 §1.0(G) return path for in-server-rack BBU.
- Mark the result `[V]` and `unresolved`.
- Require the carrier’s written position before water-supply concept freeze.

Do not resolve the loop by inference.

### 10.4 NFPA 75 boundary

NFPA 75-2024 does not supply the Li-ion protection basis. Apply:

- IFC Ch. 12
- The adopted NFPA 855 edition
- Applicable insurer sheet
- Owner evidence

Do not perform ESS sprinkler, explosion-control, ventilation, duration, or thermal-runaway design here.

Use `ess-isolation-venting-and-duration` and the applicable ESS Skills.

---

## 11. Storage and staging gate

Storage is not HC.

### 11.1 Storage identification

A space is storage or mixed storage when it contains:

- Palletized goods
- Racked stock
- Receiving/decrating inventory
- Spare parts
- Cable or conduit stores
- Filters or construction materials
- In-envelope construction laydown
- Stored, returned, damaged, or decommissioned Li-ion

The same room may be an HC-2 electrical room when occupied by installed equipment and a commodity-classified storage room during staging.

### 11.2 Required storage result

Record only:

- `occupied`
- `storage`
- `mixed`
- Commodity-classification handoff
- IFC Ch. 32 high-piled status
- FM DS 8-9 applicability status
- Aggregation/separation status
- Adjacent-space boundary consequence

Do not calculate DS 8-1 commodity class here.

Hand off to `storage-staging-sprinkler-design`.

### 11.3 IFC Ch. 32 status

The corpus indicates that IFC Ch. 32 high-piled storage is height-driven, with thresholds commonly stated as:

- More than 12 ft for Class I–IV commodities
- More than 6 ft for high-hazard commodities

These thresholds remain `[V]` until verified against the adopted IFC primary.

Do not use IFC Ch. 32 status to decide whether FM storage applies. FM DS 8-9 has its own applicability route, including storage-area conditions that may apply below the IFC high-piled threshold.

### 11.4 Storage aggregation and boundaries

Record:

- Highest-hazard commodity governs unless properly segregated.
- Mixed storage may extend protection consequences into adjacent areas.
- FM DS 8-9 March 2010 / Interim Rev April 2026 §2.3.3.5 (corpus mine Jul-2018 → `[V]`) extends storage design ≥15 ft beyond storage edges or to a wall where applicable.
- Fire barriers, distance, and fire-area boundaries require separate coordination.

Do not translate storage classification into a density or gpm.

### 11.5 Stored Li-ion

Stored/staged Li-ion does not use the installed ESS route.

Route to:

- FM DS 7-112 October 2024
- `storage-staging-sprinkler-design` (DS 7-112 incidental test, SOC cap, and the code layer by adopted IFC edition: IFC 2024 105.5.28 permit > 15 ft³ / §903.2.9; 2027 IFC Ch. 43 §4303 only where adopted)
- ESS/Li-ion specialist Skill where damaged or returned batteries are involved

Record the IBC group for the spares room per §4.3 (S-1 under 2024 IBC; BO determination on 2018/2021). Worked method by title: *Mixed-program IL building — occupancy-boundary resolution incl. storage H and a spare Li-ion cage* (`[SYN]`, method only).

---

## 12. Mixed occupancy and greatest-hazard boundaries

Classification and compartmentation are linked.

### 12.1 IBC mixed occupancy

Use the adopted IBC edition and record:

| Method | Reference | Classification consequence |
|---|---|---|
| Accessory | IBC-2024 §508.2 | Accessory-use treatment only when the adopted conditions are met |
| Nonseparated | IBC-2024 §508.3.2 | Most restrictive provisions of occupancies present |
| Separated | IBC-2024 §508.4 and §508.4.4.1 | Apply the adopted Table 508.4 cell and actual assembly |

If an accessory claim requires an area test, show:

```text
accessory_fraction = accessory_area_ft2 / story_area_ft2
accessory_ok = accessory_fraction ≤ adopted_limit and group is not H
```

Do not claim accessory status when story area or the adopted percentage is unknown.

### 12.2 FM greatest-hazard rule

FM DS 3-26 April 2025 §2.2.5:

- `verified-rated` boundary → retain separate classifications, subject to the actual assembly basis.
- `unrated-open` boundary → shared/boundary area takes the greatest hazard.
- `unresolved` boundary → carry the higher-hazard case as `ASSUMED` (flagged); not a Stop; never assume a lower hazard.

Example:

> HC-1 NOC open to HC-2 hall → boundary consequence is HC-2.

This is a classification consequence, not a density×area calculation.

### 12.3 Boundary register output

For each boundary, record:

| Boundary | Status | Classification consequence | Required handoff |
|---|---|---|---|
| HC-2 ↔ HC-1 | verified-rated | Separate classifications may remain | `fire-area-compartmentation-schedule` |
| HC-2 ↔ HC-1 | unrated-open | Boundary takes HC-2 | Compartmentation/RFI |
| Storage ↔ occupied | unresolved | Storage consequence unresolved | `storage-staging-sprinkler-design` |
| ESS ↔ hall | unrated-open | ESS overlay and greatest-hazard review | ESS/compartmentation |
| MMR ↔ private IT | unresolved | Telecom regime unresolved | Telecom/MMR specialist path |

The actual wall, door, damper, penetration, and firestop design belongs to `fire-area-compartmentation-schedule`.

FM DS 5-32 January 2026 §2.2.4, AXA XL PRC 17.10, and NFPA 75-2024 §6.1.3.2 may be recorded as basis pointers, but this Skill does not design the assembly.

---

## 13. Demand-area handoff only

Classification may provide a demand-area hint, never a density×area calculation.

Use only the selected system family inherited from `suppression-technology-selection`.

| Route | Wet hint | Dry/DI hint |
|---|---:|---:|
| FM HC-2 at or below 30 ft | 2,500 ft² | 3,500 ft² |
| FM HC-1 at or below 30 ft | 1,500 ft² | 1,500 ft² |
| AXA OH Group 1 | NFPA 13 area `[V]` | Directional DI adjustment `[V]` |
| NFPA 13-2025 delta | Matrix-linked | Matrix-linked |

For FM HC-2, the source relationship is:

- `FM DS 3-26 April 2025` Table 2.3.1.10
- `FM DS 5-32 January 2026` §2.4.3.3.1.1
- Wet/dry consequence from `FM DS 5-32 January 2026` §2.4.3.2.1.2

Do not add hose, duration, density, flow, tank volume, or pump margin.

### 13.1 High ceiling

FM DS 5-32 January 2026 applies a 30 ft ceiling cap through its applicable clauses.

If the ceiling exceeds 30 ft:

- Mark the FM route `unresolved` or `off-table`.
- Hand off to `density-area-dry-increase`.
- Consume the NFPA 13-2025 high-ceiling delta from the basis matrix.
- Cite NFPA 13 §19.2.3.2.5 only with its edition: 2025 = ceilings over 30 ft; 2022 = dry/DI +30% .
- Do not invent an HC area or density.

### 13.2 Greatest hazard is not a hydraulic result

The greatest-hazard rule determines the classification or boundary route.

It does not determine:

- Operating sprinklers
- Density
- Flow
- Hose allowance
- Duration
- Pump size
- Tank size
- Concurrent concealed-space demand

Those belong to downstream Skills.

---

## 14. Output schedule

Create one row per space.

### 14.1 Required columns

| Column | Required content |
|---|---|
| Space/tag | Caller input |
| Area | Input; `[SYN]` if synthetic |
| Contents | Actual contents and operational use |
| Occupied/storage status | `occupied`, `storage`, or `mixed` |
| IBC occupancy | Primary and alternate group(s) with §302.1 rationale |
| Sprinkler trigger | Adopted section and conclusion |
| NFPA 13 class | OH/EH/storage/off-table; `[V]` where unpinned |
| Insurer route | FM HC, AXA OH, dual rows, or none |
| Telecom regime | NFPA 75/DS 5-32, NFPA 76/DS 5-14, or unresolved |
| Switchgear route | DS 5-19/object gate where applicable |
| ESS/Li-ion overlay | BBU, ESS room/building, stored, non-Li, or none |
| Storage route | Storage handoff and IFC Ch. 32 status |
| Boundary consequence | Separate, greatest hazard, or unresolved |
| Selected system | Wet, dry, DI, or inherited comparison-only/prohibited status |
| Demand-area hint | Area only; no gpm |
| Basis status | Grounded/provisional/unresolved/comparison-only/handoff |
| Controlling basis pointer | Inherited matrix row or cited source |
| Δ vs NFPA 13-2025 | Directional classification delta only |
| Flags | `[SYN]`, `[V]`, `[U]`, RFI, conflict |
| Handoff | Skill id and required next action |

### 14.2 Off-table rows

Keep off-table rows visible.

Use:

- `OFF TABLE — storage`
- `OFF TABLE — ESS`
- `OFF TABLE — generator/fuel`
- `OFF TABLE — transformer apparatus`
- `OFF TABLE — telecom regime unresolved`
- `OFF TABLE — switchgear object unresolved`

Silence does not mean no protection is required.

### 14.3 Companion sections

Include:

1. Inherited basis-matrix and technology-selection status
2. Edition-pin block
3. IBC group and §903.2 trigger register
4. Space-use fork
5. FM/AXA classification register
6. MMR regime register where applicable
7. Switchgear object register where applicable
8. ESS/Li-ion overlay register where applicable
9. Boundary register
10. Demand-area handoff register
11. `[SYN]`/`[V]`/RFI/status register
12. Handoff list

---

## 15. Show-and-verify

Show arithmetic only for classification gates.

### 15.1 Accessory check

```text
accessory_fraction = accessory_area_ft2 / story_area_ft2
```

Use only with the adopted IBC accessory rule and a declared story area.

### 15.2 Fire-area triggers

```text
f1_or_s1_single_trigger = fire_area_ft2 exceeds the adopted §903.2 threshold
f1_or_s1_aggregate_trigger = aggregate_fire_area_ft2 exceeds the adopted threshold
windowless_trigger = story_without_openings_ft2 exceeds the adopted §903.2.11.1 threshold
```

Use declared fire-area boundaries, not raw room areas.

### 15.3 Demand-area routing

```text
if insurer == FM and class == HC-2 and selected_system == wet:
 area_hint = 2500 ft²

if insurer == FM and class == HC-2 and selected_system in {dry, DI}:
 area_hint = 3500 ft²

if insurer == FM and class == HC-1:
 area_hint = 1500 ft²

if insurer == AXA XL and selected_system == DI:
 area_hint = matrix_linked_directional_adjustment
```

This is a routing hint only. Do not calculate density×area.

---

## 16. Status and flag register

### 16.1 Provenance statuses

| Status | Use |
|---|---|
| `grounded` | Held source with edition and section |
| `derived` | Arithmetic derived from grounded inputs |
| `synthetic` | Caller-supplied exercise value |
| `provisional` | Inherited provisional matrix result |
| `unresolved` | Required classification cannot close |
| `comparison-only` | Alternate carrier/vendor/system evidence |
| `handoff` | Another Skill owns the next action |

### 16.2 Flags

- `[SYN]` — synthetic project value
- `[V]` — unverified edition, applicability, listing, boundary, or primary source
- `[U]` — unresolved classification or basis
- `RFI` — required information
- `CONFLICT` — conflicting source or classification
- `HANDOFF` — downstream Skill owns the next step

Never use `[SYN]` for a code or insurer requirement.

---

## 17. Stop conditions

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items; input gaps → stated `ASSUMED`, flagged) when:

1. The space list is missing.
2. The completed `most-stringent-basis-matrix` result is missing.
3. The completed `suppression-technology-selection` result is missing.
4. The inherited jurisdiction or enforced edition status is unresolved for the decision.
5. A required mixed-occupancy or mixed-hazard boundary is omitted.
6. The caller requests this Skill to elect single-interlock or non-interlock.
7. A dual-carrier result is supplied without the basis-matrix union.
8. MMR public/private function or AC/DC power regime is unresolved.
9. ESS topology is missing where it could change the route.
10. The DS 5-32/DS 5-33 `>20 kWh/rack` loop is present and the caller requests a final class.
11. A switchgear room’s voltage, oil status, or grouped-cable condition is missing.
12. The caller asks for storage HC classification instead of a storage handoff.
13. The caller asks for density, flow, pump, hose, duration, or hydraulic concurrency.
14. The caller asks for foam, mist, clean-agent, hybrid, aerosol, hypoxic, transformer spray, or other special-hazard design.
15. The caller asks for allowable-area, egress, smoke-control, or detailed compartmentation design.
16. The caller asks for a final code-compliant conclusion while a required row is provisional or unresolved.
17. The caller does not name an output path and requests file output.

---

## 18. Handoffs

| Work | Handoff |
|---|---|
| Basis matrix, jurisdiction, carrier union, owner evidence | `most-stringent-basis-matrix` |
| Objective and permitted system family | `suppression-technology-selection` |
| Demand area and dry/DI consequences | `density-area-dry-increase` |
| Storage/staging commodity and protection | `storage-staging-sprinkler-design` |
| Fire-area and compartmentation schedule | `fire-area-compartmentation-schedule` |
| ESS isolation, venting, duration, and Li-ion room basis | `ess-isolation-venting-and-duration` |
| MV switchgear room/object protection | **`mv-switchgear-room-package`** (live Skill; DS 5-19 room package). Note: `mv-switchgear-room-fire-protection` |
| Transformer or power-block spray | out of scope |
| MMR/telecom regime and NFPA 76 work | Telecom/MMR specialist path |
| Pump and water-supply envelope | `pump-envelope` |
| Preaction releasing sequence | `preaction-releasing-c-and-e-soo` |
| Power isolation | `power-isolation-disconnect-control` |
| Detection and VEWFD | Detection/releasing Skill |
| ITM and acceptance | `itm-design-for-testability` and `commissioning-ist-acceptance-packet` |

---

## 19. Directional delta versus NFPA 13-2025

The basis matrix owns the formal delta. This Skill reports only classification consequences.

Permitted directional statements include:

- FM HC-2 is a loss-category classification rather than a bare NFPA 13 occupancy label.
- AXA XL identifies OH Group 1 but does not supply a complete hydraulic method.
- FM’s 30 ft ceiling cap differs from the NFPA 13-2025 high-ceiling mechanism.
- FM and NFPA/IFC storage taxonomies do not map one-to-one.
- NFPA 75 is a parallel ITE-area floor when adopted; it does not replace insurer requirements.
- ESS/Li-ion overlays are separate from ordinary NFPA 13 occupancy classification.

Do not state a numerical OH1 density, area, or high-ceiling increase as grounded unless the basis matrix supplies the verified primary citation.

---

## 20. Citations

### Code floor

- `IBC-2024 §202` — data-center definition and no dedicated Chapter 3 group.
- `IBC-2024 §302.1` — most-nearly-resembles classification.
- `IBC-2024 §304` — Business.
- `IBC-2024 §306` — /Industrial.
- `IBC-2024 §307` — High Hazard.
- `IBC-2024 §311` — Storage.
- `IBC/IFC-2024 §903.2.4` — F-1 sprinkler triggers.
- `IBC/IFC-2024 §903.2.9` — S-1 sprinkler triggers.
- `IBC/IFC-2024 §903.2.11.1` — stories without openings.
- `IBC/IFC-2024 §403.3` — high-rise.
- `IBC/IFC-2024 §405.3` — underground buildings.
- `IBC-2024 §508.2`, §508.3.2, §508.4, §508.4.4.1 — mixed occupancy.
- `IBC-2024 §507.4` — unlimited-area path.
- `IFC-2024 §1207.7.1` — dedicated-use ESS building as F-1.
- `IFC-2024 Ch. 12` — ESS overlay.
- `IFC-2024 Ch. 32` — high-piled storage route.
- `NFPA 75 §6.1.1` building construction (fully sprinklered building per NFPA 13 OR listed construction; 2024: Type I (442/332) or Type II (222/111); 2020: Type I (443/332) or Type II (222/111); either edition: single-story Type II (000); §6.1.1.1 risk-assessment modification;), NFPA 75-2024 §6.1.3.2, §9.1.1, §9.2.1 — ITE-area floor.

### FM and insurer basis

- `FM DS 3-26 April 2025 Table 2.2.2` — general HC classification.
- `FM DS 3-26 April 2025 Appendix C Table C-1` — named data-center spaces.
- `FM DS 3-26 April 2025 §2.2.5` — greatest-hazard mixed/unseparated occupancy.
- `FM DS 3-26 April 2025 Table 2.3.1.10` — demand-area handoff basis.
- `FM DS 5-32 January 2026 §2.3.1.4` — in-rack BBU threshold.
- `FM DS 5-32 January 2026 §2.2.4` — data-processing-room separation pointer.
- `FM DS 5-32 January 2026 §2.4.3.2.1.2` — wet/dry system-family consequence.
- `FM DS 5-32 January 2026 §2.4.3.3.1.1` — HC-2 demand-area pointer.
- `FM DS 5-32 January 2026 §2.4.3.4.1.1` — concealed-space route.
- `FM DS 5-32 January 2026 §2.4.1.1` — carrier system preference comparison.
- `FM DS 2-0 October 2021 / Interim Revision January 2024` — installation-base precedence.
- `FM DS 5-28 April 2021 §2.4.2` — non-Li stationary battery HC-2/QR route.
- `FM DS 5-33 January 2024 §1.0(G)` — in-server-rack BBU scope return.
- `FM DS 5-33 January 2024 §2.4.1` — ESS design handoff; no design performed here.
- `FM DS 7-112 October 2024` — stored/staged Li-ion route.
- `FM DS 8-1 April 2014 / Interim Revision October 2024` — storage classification route.
- `FM DS 8-9 March 2010 / Interim Revision July 2018 §1.0 and §2.3.3.5` — storage applicability and mixed-use extension.
- `FM DS 5-14 April 2012 / Interim Revision April 2025 §1.0–§1.1` — telecom/DC-plant versus VOIP routing.
- `FM DS 5-19 October 2020 / Interim Revision January 2024 §2.2.1 and §2.2.3` — switchgear object gate.
- `FM DS 5-31 January 2020 / Interim Revision October 2025 §2.3.2.2.B` — grouped cable route.

### Canonical corpus notes

Look up by title:

-
-
-
-
-
-
-

---

## Design practice

1. Classify the building and each space separately.
2. Never merge IBC group, NFPA 13 hazard, FM HC, AXA OH, storage class, and ESS regime.
3. Consume the basis matrix and technology-selection result.
4. Do not rebuild jurisdiction, carrier union, owner evidence, or system election.
5. Selected systems are wet, dry, or double-interlock only.
6. Single-interlock and non-interlock remain comparison-only.
7. Storage is not HC.
8. MMR classification begins with function and power type.
9. Switchgear classification begins with voltage, oil, combustibles, and cable.
10. ESS classification begins with battery state and topology.
11. Dedicated-use ESS building is F-1 under the applicable IFC edition; other ESS configurations remain overlays or unresolved where required.
12. Unseparated boundaries take the greatest hazard under FM DS 3-26 §2.2.5.
13. Greatest hazard is not a density or hydraulic calculation.
14. NFPA 13-2025 deltas remain matrix-linked and directional where primary text is absent.
15. A missing or unresolved classification remains visible as `[V]`, provisional, unresolved, RFI, or handoff.
16. No code, carrier, owner, or special-hazard requirement is invented.

---

## Check before you finish

1. Confirm the two upstream results.
2. Confirm inherited edition and jurisdiction status.
3. Confirm the space list and boundary register.
4. Apply the IBC §202/§302.1 group fork.
5. Evaluate every credible §903.2 trigger.
6. Record NFPA 75 as a parallel floor where adopted/referenced.
7. Separate occupied, storage, ESS, telecom, switchgear, generator, and transformer routes.
8. Apply FM Table C-1 and DS 3-26 §2.2.5 where FM governs.
9. Apply AXA OH or dual-carrier rows without importing FM values.
10. Run the MMR function/power/SPE gate.
11. Run the switchgear voltage/oil/cable gate.
12. Run the ESS state/topology gate and preserve the >20 kWh/rack loop.
13. Hand storage to `storage-staging-sprinkler-design`.
14. Resolve verified-rated, unrated-open, and unresolved boundaries.
15. Apply greatest-hazard consequences without calculating density or flow.
16. Add only a wet/dry/DI demand-area handoff hint.
17. Emit required schedule columns and status register.
18. Add directional NFPA 13-2025 delta and all `[SYN]`/`[V]` flags.
19. Write only to the caller-named path.
