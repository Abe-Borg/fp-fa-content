---
name: Preaction releasing C and E SOO
description: >-
 use this when occupancy, VEWFD architecture, and a company-elected
 wet/dry/double-interlock system family are pinned (STS + matrix consumed
 when present, else ASSUMED and flagged; packet optional), and you must emit the authoritative releasing cause-and-effect matrix plus
 written sequence of operations the panel is programmed from — controlling
 DI water path (VEWFD_prealarm AND low_air), wet thermal-only, clean agent is out of scope; SI/NI comparison-only Stop if BOD;
 foam prohibited; mist PRACTICE REFUSED; not occupancy, density×area, pump,
 ITM, assignment packet, suppression-tech-selection, or ASD sizing.
---
# Preaction releasing C and E SOO

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe. **This Skill EMITS the authoritative releasing cause-and-effect (C&E) matrix plus the written sequence of operations (SOO) the panel is programmed from.** It runs **after** occupancy, VEWFD architecture, and a **company-elected** system family (`wet` | `dry` | `double-interlock`) are pinned by upstream Skills. It binds already-chosen detection stages and the **company-elected** suppression type into **panel logic**.

**One Skill, two system-family branches (company fence):**

| Branch | Typical space | What this Skill engineers (controlling) |
|---|---|---|
| **Water — company BOD** | Energized data hall / white space | **Controlling DI:** `preaction_trip := VEWFD_prealarm AND low_air`; **wet:** thermal-only / **no W1 trip**; **NO abort**, **NO pre-discharge delay on water**; smoke exhaust follows **water**, not smoke. Dry-pipe (if elected) is thermal / dry-valve regime — no VEWFD releasing trip unless the elected packet says otherwise. |
| **Out of scope** | Clean agent, foam, mist, single-interlock | Record and stop. Do not write a gas sequence. |

Clean agent, foam, and water mist are out of scope beside this water-path sequence. Do not add a gas branch.

**Company-controlling water Boolean (DI BOD):**

```
preaction_trip := VEWFD_prealarm AND low_air
 AND NOT release_disconnect AND NOT panel_trouble
```

**Wet BOD:** no releasing trip — heads control discharge (`wet_pipe := thermal_operation_only`).

**Comparison evidence only (never company default / never controlling BOD):**

```
# FM / AXA SI white-space trip-on-pre-alarm — comparison / historical training
preaction_trip_SI_comparison := VEWFD_prealarm
 AND NOT release_disconnect AND NOT panel_trouble
```

Sprinkler heads still control discharge on preaction; the valve charges the pipe early. A fused head is **not** required to open a **single-interlock** valve — that SI fact remains **comparison evidence**, not permission to elect SI as BOD.

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PARAMETER** → report **Δ vs NFPA 13-2025** (preaction family / abort / delivery clock) **and Δ vs NFPA 72-2025** (releasing-service control unit). Cite **section AND edition**. Enforced ≠ latest. Show-and-verify any arithmetic. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. **Do not invent sections** (especially invented NFPA 72-2025 subsections). Caller-path-only.

**El/El failsafe is a QUESTION this Skill asks, not a trim catalog.** Double-interlock variant-election (El/Pn · Pn/Pn · El/El + failsafe) is a **hand-off row** to `preaction-el-el-trim-election`. Do not write a valve/trim schedule here.

**Honesty.** Copy the method, not another hall's numbers, zone map, program numbers, or battery size. A single-interlock trip on pre-alarm is comparison only, never the controlling basis.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may emit a **controlling** releasing C&E + SOO only against an elected company system family:

1. **Wet-pipe sprinkler**
2. **Dry-pipe sprinkler**
3. **Double-interlock preaction**

Comparison-only (never elected; never the controlling BOD path):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

FM DS 5-32 January 2026 §2.4.1.1 preference ranking remains **comparison evidence**:

> Wet → non-interlock → single-interlock → double-interlock last

That ranking is **not** company election permission. AXA XL’s single-interlock preference and double-interlock penalty remain comparison evidence only. Label every use of that ranking `comparison-only`.

**This Skill does not elect families.** It **consumes** the election from `suppression-technology-selection` and the releasing / system-family rows from `most-stringent-basis-matrix` (plus the completed the input packet). Controlling BOD = `wet` | `dry` | `double-interlock` only.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling C&E / SOO as if SI/NI were company-elected.
6. SI/NI may appear only as a **`comparison-only`** matrix / column (never the controlling schedule).

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Emit controlling C&E + SOO |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not design foam releasing |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent | Adjunct / handoff | May encode adjunct abort-mode branch when `adjunct = y`; enclosure / quantity owned elsewhere |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |
| Deluge / open-sprinkler | Different releasing regime | **Stop** the white-space / company DI default |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM DS 5-32 sheet language that mentions *"water-mist"* (e.g. exhaust interlock wording) is **sheet language only** — it does **not** authorize mist election or design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Controlling DI (and wet) C&E matrix + written SOO | System-family election (STS) |
| Explicit SI/NI **comparison** matrix / column | Occupancy / HC / OH classification |
| Clean-agent adjunct abort-mode branch (if elected) | Density × area `calcs` |
| RCU parameter schedule by function + listing | Dual-carrier BOD rebuild |
| DI El/El failsafe **question** + trim hand-off row | Valve/trim catalog / El/El hardware election |
| Status register + `[SYN]`/`[V]` | Pump envelope; ASD port math |
| Consume STS election + packet + matrix releasing rows | Agent weight `W`, door-fan hold-time |
| Name (do not prove) 30/60 delivery clocks | Copying a synthetic DI/wet corpus package (another hall's) as project defaults |

---

## 2. Required inputs and upstream intake

Caller must supply. Do not copy a synthetic hall or MMR as defaults. Do **not** invent a release program. Do **not** treat SI/NI as company BOD.

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection` (and matrix). Missing STS election → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). |
| **Consumed `most-stringent-basis-matrix` releasing / VEWFD / power-isolation / clean-agent rows** | **yes** when dual-carrier or when those rows exist | Consume; do not rebuild. Unresolved controlling system-family / releasing row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. |
| **VEWFD stages + zone list** | **yes** | L1 Alert / L2 Pre-Alarm-Action / L3 Alarm-Fire, with the **zone list** that can initiate. Thresholds may be consumed from the VEWFD/ASD package; **do not re-size ports**. Missing stages or zone list → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Power-isolation initiation level** | **yes** (or explicit `[V]`) | `L2` / `L3` / `waterflow` / `L2-soft then L3/waterflow-full`. FM DS 5-32 **§2.5.3.1.1 (Jan-2026)** says initiate on *"any smoke detection or the water-flow alarm"* and **does not pin the VEWFD level**. If the caller has not elected a level, **flag `[V]` and ask — do not invent**. Handshake `power-isolation-disconnect-control`. |
| **HVAC / damper / smoke-exhaust policy** | **yes** | Airflow regime (`velocity ft/s` and/or ACH with **declared volume basis**), whether the **<5 ft/s or 60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only]** gate is blown, damper-close trigger, and smoke-exhaust posture (`none` / `code-forced → waterflow only` / other named). Missing policy → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Clean-agent branch** (if adjunct = `y`) | **yes** | Abort mode `IRI` / `ULI` / `NYC` / `AHJ` (or explicit `AHJ to pin [V]`); non-recycling discharge delay **≤30 s**; **physical** disconnect present; coincidence (2-detector) confirmation. Adjunct = `y` without abort-mode election **and** without `[V] AHJ to pin` → **Stop**. |
| **Supervision class** | **yes** | Fire-alarm survivability **Class V or greater** (FM DS 5-32 §2.4.2.1.10; DS 9-1) unless a cited owner/AHJ overlay raises it. |
| **Releasing-panel listing pair** | **yes** | Control unit **listed for releasing service** (NFPA 72 §23.11.1) **and** releasing devices listed for use with it (§23.11.2). On an FM job: **FM Approved valve + solenoid + panel combination** (DS 2-0 §2.2.1.12.1.1). Specify **by function + listing**, never by model. |
| **Caller output path** | **yes** for file output | If unnamed, return the C&E/SOO in the response and stop. |

Optional (do not block; flag `[V]` / `handoff`): occupancy-hazard-fork schedule (consume class, do not re-classify); VEWFD/ASD layout (consume L1/L2/L3 settings and zone tags; **do not re-size**); owner EPO posture (structure only if NDA); double-interlock **variant** already elected (`El/Pn` / `Pn/Pn` / `El/El`) — if unelected on a DI job, **ask the failsafe question** and **hand off** the trim row to `preaction-el-el-trim-election`; nitrogen day-one election (handshake `nitrogen-inerting-and-c-factor-gate`); water-delivery screen companion (`dry-preaction-water-delivery-screen` — **name** 30/60 clocks, do not prove); commissioning / IST companion (`commissioning-ist-acceptance-packet`).

**Do not invent** a system type, a VEWFD stage split, an abort mode, or a power-isolation level. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected wet/dry/DI; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI |
| `most-stringent-basis-matrix` | Releasing / VEWFD / power-isolation / clean-agent rows; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD |
| `asd-vewfd-return-sampling` / detection package | L1/L2/L3 settings + zone tags | Re-size ports / transport time |
| `power-isolation-disconnect-control` | Initiation-level election / EPO structure | Invent L2 or L3 as an FM section pin |
| `preaction-el-el-trim-election` | DI variant + failsafe answer when present | Write trim catalog here |
| `nitrogen-inerting-and-c-factor-gate` | Day-one N₂ context on dry/DI | Re-derive purity / C |
| `dry-preaction-water-delivery-screen` | Named 30/60 clock attribution | Prove fill calc / hydraulics here |
| `commissioning-ist-acceptance-packet` | Commissioning hooks companion | Run acceptance tests here |
| Clean-agent enclosure / the out-of-scope methods | Adjunct feasibility when present | Size `W` or door-fan here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, STS election is missing / `unresolved`, or the matrix controlling releasing/system-family row is unresolved → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

### 2.2 Look up by title (not required filesystem paths)

*The Design practice*; *White-space preaction releasing — cause-and-effect, architecture & SOO*; *VEWFD detection & releasing for data centers*; *Releasing control unit — hardware, standby power & program verification*; *Enforced-vs-latest edition resolver and reference pins*; *FM DS 5-32 insurer design basis*; *Power isolation and disconnect control*; *Gaseous agents in high-airflow environments*.

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest) — two delta references

Resolve **enforced** vs **latest** before filling any cell. Format every citation `instrument-edition §section`.

This Skill reports **Δ vs NFPA 13-2025** (sprinkler/preaction family, abort recognition, delivery clock) **and Δ vs NFPA 72-2025** (releasing-service control unit). The *code-floor citation* stays at the **AHJ pin**.

Under an **unamended 2024 I-Code** adoption (shop codebook: *Enforced-vs-latest edition resolver and reference pins*):

| Standard | Role | 2024-cycle **enforced** pin | Latest (delta) |
|---|---|---|---|
| **NFPA 13** | Preaction family; abort **not recognized** on water (no abort/cancel clause in any edition 2016–2025); DI sizing [CODE §8.3.2.3] | **2022** | **2025** |
| **NFPA 72** | Ch. 23 releasing service | **2022** | **2025** |
| **Out of scope** | Clean agent, foam, mist, deluge, single-interlock design | — | Do not size them here |
| **NFPA 75** | ITE-area detection / damper-close (when adopted) | no direct Ch.80/35 pin | **2024** |
| **NFPA 70 / NEC** | Art. 645 disconnect-on-alarm / HVAC | **2023** | **2026** — resolve independently |
| **FM DS 5-32** | Controlling functional C&E on an FM DC | **January 2026** | — |
| **FM DS 2-0** | Releasing-installation overlay | **Oct-2021 / Interim Rev Jan-2024** | — |
| **FM DS 5-48** | Automatic Fire Detection ITM (companion; not this Skill’s schedule) | **Opened Jan-2011 / IR Apr-2025** | — |
| **FM DS 5-40** | Fire Alarm Systems companion | **Held Sep-2007** — **edition-stale** vs NFPA 72-2025 | — |
| **AXA XL PRC 17.10** | SI + de-energize before waterflow; smoke venting held through soak | date the *claim* | — |
| **UL 864** | Abort **not permitted** on preaction/deluge | listing, not a code cycle | — |

**Honesty on NFPA 72 numbering.** Reconcile releasing-service cites to the enforced edition and to NFPA 72-2025. Do not invent a 72-2025 subsection. Held now: NFPA 72-2025 §23.11.1 through §23.11.11. Numbering outside those stays unverified.

**FM DS 2-0 §2.2.1.12.3.1(A):** do **not** use smoke detection to activate a preaction / deluge system **unless the occupancy sheet grants it**. **DS 5-32 grants it and names the threshold** — cite both: DS 2-0 gate **and** DS 5-32 **§2.4.3.2.1.3 / §2.4.3.2.1.3.1 (Jan-2026)**. On company DI BOD the **controlling** trip still requires the **AND** with low-air; the sheet’s trip-on-pre-alarm language remains **comparison evidence** when used to justify SI-as-BOD (which this Skill refuses).

Consume the assignment packet (optional), STS election, and any BOD-matrix **releasing rows** if present. Do not rebuild them.

---

### 3.2 Confirm the system-family branch (do not re-select the system)

This Skill **does not** choose wet vs preaction vs gas. It **encodes** the type STS already pinned.

```
# Company-controlling encodings
valve_trip := detection_alarm AND sprinkler_operation # double-interlock (company BOD)
wet_pipe := thermal_operation_only # wet — no releasing trip
# dry_pipe := dry-valve / thermal regime per elected packet

# Comparison-only encodings (never controlling BOD)
valve_trip_SI_comparison := detection_alarm # single-interlock — comparison-only
valve_trip_NI_comparison := detection_alarm OR sprinkler_operation # non-interlock — comparison-only
```

**FM DS 5-32 Jan-2026 §2.4.1.1 order of preference** (Wet → Non-interlock → Single-interlock → **Double-interlock last**) is **`comparison-only` evidence**, not election permission. A company-elected DI is a **restrictive election** already priced on the density/area row; this Skill **honors** it and writes the **AND**.

Clean agent, foam, water mist, deluge, and single-interlock preaction are out of scope. Record the request and stop. Do not write a gas sequence or a deluge matrix.

---

### 3.3 Encode water-path trip logic (company-controlling DI / wet)

On a company-elected **double-interlock** energized data hall:

1. **Controlling Boolean:** `preaction_trip := VEWFD_prealarm AND low_air` (plus NOT disconnect / NOT panel_trouble). First detection cause is the **second** VEWFD stage (L2), **and** the sprinkler / low-air interlock. **Not** alarm-stage alone, **not** a second smoke zone.
2. **Do not use cross-zoned detection (two smoke zones) to trip the preaction valve** — FM DS 5-32 **§2.4.3.2.1.3.2 (p.17)** is a **prohibition** on that configuration. Circuit 2 = low-air is the legitimate DI second gate (see table below).
3. **No abort switch and no pre-discharge delay on the water path.** NFPA 13 does not recognize them on preaction (citation note: NFPA 13 2016–2025 contains no abort or cancel clause in the preaction text; the bar comes from UL 864 and company rule, not an NFPA 13 prohibition). **UL 864 does not permit “Abort on Pre-action or Deluge Systems.”** Abort with pre-discharge = 0 s cannot act.
4. **Smoke exhaust follows WATER, never SMOKE.** DS 5-32 **§2.4.2.1.7 / .7.1 / .7.2**: do not install automatically operated smoke-exhaust in DP equipment rooms; where local code compels it, interlock to the **sprinkler / water-mist alarm**, **not** detection. The sheet’s *"water-mist"* wording is **sheet language only** — mist remains `PRACTICE REFUSED` for company election.

On a company-elected **wet** path: **no W1 releasing trip**. Thermal operation only. Abort / disconnect / delay still do not apply to the sprinkler.

**FM / AXA trip-on-pre-alarm (`preaction_trip := VEWFD_prealarm`)** — FM DS 5-32 **§2.4.3.2.1.3** + **§2.4.3.2.1.3.1** *“Arrange the preaction valve to actuate upon the pre-alarm condition”* — remains **comparison evidence** (and the logic copied into SI training packages). It is **not** the company-controlling default and does **not** authorize SI-as-BOD.

**“Cross-zoned” is an ambiguous panel term — ask what is on circuit 2 before you reject it.**

| What is wired to initiating circuit **2**? | Verdict |
|---|---|
| **Low-air / air supervisory switch on the sprinkler piping** | ✔ This **is** the second interlock (the sprinkler). Correct **double-interlock**. Exactly ONE detection AND. |
| **A second smoke or heat detector / a second detection zone** | ✘ **Triple interlock.** Reject — FM’s warned configuration. |

On a **single-interlock** system (comparison-only) there is **no legitimate second circuit**. **Best-practice spec text: delete the word “cross-zoned” and write the interlock explicitly.** Do not emit SI as controlling BOD.

**Silent-OR trap:** `NORMAL` = Boolean **OR** over mapped zones; `CROSS ZONED` = Boolean **AND**. A `NORMAL` release output with detection **and** low-air both mapped releases on **either** input — **air loss alone opens the valve**. The closeout deliverable is the **as-programmed zone→output map, witnessed**.

**High-airflow AND can be physically unsatisfiable.** Full-scale tests (FM Global P14042) recorded **no response** against the direction of airflow. Pair along the flow (room + return), never across it.

**One releasing-service control unit per suppression zone.** FM DS 2-0 §2.2.1.12.1.2: one FACP per preaction system; sharing costs **90 hours of battery PER SYSTEM** (§2.2.1.12.1.3). Each protected space contains **≥1 real automatic detector** (NFPA 72 §23.11.7).

---

### 3.4 Build the reusable C&E matrices (authoritative schedule + comparison)

Rows = initiating events; columns = outputs; cells = action + timing.

| Code | Output |
|---|---|
| **A1** | Alert annunciation (constantly attended) |
| **A2** | Action / alarm annunciation |
| **W1** | Trip preaction valve / admit water |
| **M1** | HVAC reduce (to **<5 ft/s**) |
| **M2** | HVAC shutdown / damper close |
| **P1** | Power isolation |
| **N1** | Notify / graphics / fire service |
| **G1** | Gas release (adjunct path only) |
| **T1** | Supervisory / trouble |
| **L1** | Log |

Legend for **basis** cells: **C** code-floor · **I** insurer · **O** owner · **RV** re-verify in licensed current standard.

#### 3.4.1 Controlling company matrix — double-interlock (and wet adaptation)

**Controlling water-path matrix** for company-elected **DI**. For **wet**: W1 column stays **–** on detection rows (thermal-only; no releasing trip). Adapt notes below.

| Initiating event | A1 | A2 | W1 | M1 | M2 | P1 | N1 | G1 | T1 | L1 | Basis | Status |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|---|
| VEWFD **alert** (L1) | Y | – | – | – | – | – | Y | – | – | Y | I/O | `grounded` method |
| VEWFD **pre-alarm / action** (L2) | – | Y | **AND⁵** | Y¹ | – | O² | Y | – | – | Y | **I/O** — company DI AND | `grounded` / `provisional` |
| Second / **cross-zone** smoke satisfied | – | Y | **No³** | – | – | O | – | Y⁴ | – | Y | I (no cross-zone smoke for water) | `grounded` |
| Manual release (preaction) | – | Y | O⁹ | – | – | O | – | – | – | Y | O/RV — FM DS 2-0 §2.2.1.12.1.4 | `[V]` / owner |
| **Sprinkler operation** / low-air at head | – | Y | Y⁵ | – | – | O | – | – | – | Y | C/I — DI second gate | `grounded` |
| **Waterflow** switch | – | Y | – | O | O | **Y⁶** | Y | – | – | Y | I/O — de-energize ≤ waterflow (AXA) | `grounded` / owner |
| Low / high air (or N₂) | – | – | **AND⁵** | – | – | – | – | – | Y | Y | C — DI: low-air is interlock, not SI stay-closed alone [CODE NFPA 72-2025 §17.19.2.1 (two separate and distinct signals: off-normal and restoration), §17.19.2.2.2(A) both high- and low-pressure conditions, (B) off-normal per NFPA 13 unless the valve manufacturer's instructions permit otherwise; 2019/2022 §17.17.2.1 same two-signal rule; off-normal at a 10 psi increase or decrease [CODE NFPA 72-2022 §17.17.2.2.2(B) (dry pipe and preaction, unless the manufacturer's published instructions permit otherwise); 2019 §17.17.2.2.2(B) (dry pipe valves only);]; **low-pressure DI caveat:** NFPA 72-2022 A.17.17.2.2.2 (annex) says a ±10 psi window "is not appropriate" for dry/preaction systems run at 8–15 psi and "could result in dry pipe valve actuation prior to transmission of a low air pressure supervisory signal". On a low-pressure N₂/air DI system, set the low-air supervisory point per the valve maker's published instructions, above the valve's trip point with margin, and show both values. Verify with the engineer of record on the setpoint margin; conservative assumption: the low-air signal is at least 5 psi above the maker's trip point (`[SYN]` margin)] | `grounded` |
| Valve tamper / wrong position | – | – | – | – | – | – | – | – | Y | Y | C/I | `grounded` |
| **Release disconnect OPEN** | – | – | **inhibited** | – | – | – | – | **inhibited** | Y | Y | C — physical switch | `grounded` |
| Loss of detection power / panel trouble | – | – | **inhibited** | – | – | – | – | **inhibited** | Y | Y | C | `grounded` |
| Gas, abort, or other out-of-scope release | – | – | – | – | – | – | – | – | – | – | Out of scope. Do not program it on the water path. | stop |

¹ M1 only if airflow **≥5 ft/s or ≥60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only]**. Argue on **velocity**; declare the ACH denominator (**room-only**) if ACH is used.
² P1 at L2 is **owner/insurer-tunable** — `[V]` if FM §2.5.3 level unpinned; handshake power-isolation Skill.
³ **No for company DI / wet water path** — second smoke zone is not a trip gate.
⁴ G1 enable needs **two independent VEWFD**.
⁵ **DI controlling:** W1 fires only when **L2 AND low_air** (zone type `LOW AIR ALARM`, not `LOW AIR`). Wet: W1 = – (no releasing trip).
⁶ Usually room-level at waterflow.
⁹ **Manual release vs the DI AND (panel default).** On G3-family panels (Potter PFC-4410G3 *Standard Program Templates* 5403798 Rev C 11/24 p. 2; Viking VFR-500 manual 5403789 Rev A 10/23 p. 1-2 — the VFR-500 is the Viking-branded G3) a zone typed **Manual Release overrides cross-zoning and abort by default**. On **El/El (Pneu-Lectric) and SureFire** programs the panel *is* the interlock, so a pull station would release onto a still-pressurized pipe — **single-interlock behavior**. Elect and write one: (a) **no Manual Release zone** (the code/FM manual means is the mechanical emergency release at the trim); (b) station typed **DETECTION** (≤30 s pre-discharge per the manuals); (c) a **written owner + FM decision** to accept the override (row stays `[V]`/owner). On **El/Pn** the pneumatic leg is at the valve, so the panel manual release does not defeat the interlock. Confirm on the as-loaded program printout.

**Explicit non-outputs:** automatic smoke exhaust on **detection** — **PROHIBITED** in the DP room. Abort row on a water-only job — **omit the row**. Pre-trip / pre-release time-delay cell on W1 — **W1 fires on L2 AND low_air (DI)** with **0 s** pre-discharge; wet has no W1 trip.

#### 3.4.2 Comparison-only matrix / column — SI / NI (never controlling)

Emit **only** as `comparison-only` evidence (carrier ranking, historical training, delta vs company DI). **Never** as the controlling schedule. If the caller wants this matrix as BOD → **Stop** `RFI-variance`.

| Initiating event | W1 on SI (comparison) | W1 on NI (comparison) | Notes | Status |
|---|---|---|---|---|
| VEWFD L2 pre-alarm | **Y** (trip-on-pre-alarm) | Y (OR path) | FM §2.4.3.2.1.3 / .3.1 language — **comparison evidence**, not company election | `comparison-only` |
| Low-air alone | **No** (SI: valve stays closed) | Y (OR opens) | Silent-OR trap if NORMAL maps both | `comparison-only` |
| L2 AND low-air | N/A (no 2nd circuit on SI) | N/A | Company DI controlling path lives in §3.4.1 | `comparison-only` vs DI |
| Cross-zone second smoke | **No³** | **No³** | Prohibition still applies to water trip | `comparison-only` |

Do **not** title any controlling schedule “Default … single-interlock white space.”

**Minimal software truth table (company-controlling DI):**

```
O_supervisory := low_air OR high_air OR valve_tamper OR release_disconnect OR panel_trouble
O_preaction_trip := prealarm AND low_air_alarm
 AND NOT release_disconnect AND NOT panel_trouble
 # zone type LOW AIR ALARM, not LOW AIR
 # wet BOD: O_preaction_trip := FALSE (thermal only)
O_HVAC_reduce := prealarm AND airflow_high # velocity>=5 fps OR ACH>=60
O_room_power_isolation := waterflow OR (prealarm AND OWNER_power_isolation_on_prealarm)
O_alarm := prealarm OR waterflow

# Comparison-only (do not program as company default):
# O_preaction_trip_SI_comparison := prealarm AND NOT release_disconnect AND NOT panel_trouble
```

**Waterflow-alarm timing:** FM DS 2-0 **§2.3.3.2** — waterflow alarm device initiates a signal **no more than 60 seconds** after sprinkler activation, measured by opening the most remote ITC downstream of the device. Distinct from water-delivery time.

---

### Out of scope media

Clean agent, foam, water mist, and single-interlock preaction are out of scope. Record the request and stop. Do not write a gas sequence, an abort mode, a concentration, or a hold time. The water-path sequence in this method is the only releasing logic it produces.

### 3.6 Power isolation, HVAC, dampers — ask the unpinned level

**Handshake:** `power-isolation-disconnect-control`. Structure only here; do not invent the level.

**Hinge (FM DS 5-32 §2.5.3 / App. D Fig D.1, Jan-2026):** isolate **before sprinkler water reaches energized equipment** / before the agent’s effective duration ends.

**Direct-UPS-shutdown rationale:**

```
UPS ride-through (gensets starting) = 10–15 min # FM DS 5-32 §3.5.2
Suppression hold / soft-down window = 10 min # §2.5.3.1.2
15 min ride-through > 10 min hold -> TRUE
```

Cutting only the upstream feed leaves the **UPS battery energizing the ignition source** past the hold. **Every UPS needs a DIRECT shut-down.**

**Initiation level — `[V]` if unpinned.** §2.5.3.1.1 permits *“any smoke detection or the water-flow alarm”* and **does not name L1/L2/L3**. This Skill **asks**. A defensible (still `[V]`) pattern: **localized soft-down begins at L2** → **full room isolation at L3 / waterflow**. **Do not stamp L2 or L3 as an FM section pin.**

**HVAC ordering (FM §3.4.2.2):** de-energize equipment **before** final cooling shutdown. Sequence **M2 after P1**. No method to compute how long cooling must continue → order the outputs, do not invent a time `[V]`.

**M1 ventilation interlock:** if the hall runs **≥5 ft/s (1.5 m/s) or ≥60 ACH [60 ACH not in NFPA 75-2024 Ch. 4 to 13; owner/insurer FM DS 5-32 only]**, command airflow to **<5 ft/s** on pre-alarm (DS 5-32 **§2.4.2.1.3**). **Design and argue on VELOCITY.**

---

### 3.7 Releasing control unit — listing, disconnect, supervision, program = the SOO

Specify the RCU **by function and listing**, never by model.

| Requirement | Pin | Layer |
|---|---|---|
| Listed releasing-service FACU | NFPA 72 **§23.11.1** (2019 capture → reconcile **72-2025**) | C [CODE NFPA 72-2025 §23.11.1] |
| Releasing devices listed for use with it | **§23.11.2** | C |
| **Physical**, supervised disconnect; software disable **prohibited** | NFPA 72 **§23.11.5 / .5.1 / .5.2–.3** | C |
| SOO consistency with the installed program | **§23.11.6** | C |
| ≥1 real automatic detector per protected space | **§23.11.7** | C |
| Two distinct supervisory signals | NFPA 72-2019/2022 **§17.17.2.1** [CODE NFPA 72-2019/2022 §17.17.2.1] → 2025 **§17.19.2.1** [CODE 2025; pressure clause 2025 §17.19.2.2] | C |
| Anti-defeat: actuator removal → audible and visual impairment | NFPA 13, effective 1 Jan 2021 (preaction) | C |
| FM Approved **valve + solenoid + panel combination** | FM DS 2-0 **§2.2.1.12.1.1** | I |
| Manual means to operate the valve during a fire | DS 2-0 **§2.2.1.12.1.4** | I |
| Class V or greater survivability | DS 5-32 **§2.4.2.1.10**; DS 9-1 | I |
| Secondary power on FM releasing service | **90 h standby + 10 min alarm** vs NFPA 72 **24 h + 5 min** ([CODE NFPA 72-2025 §10.6.7.2.1 (24 h), §10.6.7.2.2 (5 min)]) | I vs C |
| Release output time (water) | **CONTINUOUS**; pre-discharge **= 0 s** | listing / I |

**Walktest is not an impairment control** — it disables releasing outputs then **silently re-arms after 30 minutes of inactivity**. The control is the **physical, tagged** disconnect.

**Program-verification hooks:** (1) as-programmed **zone→output map**; (2) **NORMAL vs CROSS ZONED** read off the panel; (3) air-supervisory zone type `LOW AIR ALARM` vs `LOW AIR`; (4) CONTINUOUS / 0 s pre-discharge / no abort on water; (5) physical disconnect present and supervised; (6) **three must-not-release tests on DI**; (7) `MANUAL RELEASE` mapped to a cross-zoned water output **silently defeats the AND** (footnote ⁹); (8) BMS point list: **alarm + supervisory + trouble + waterflow**; (9) **state brand + program # + drawing #** on the C&E and submittal — **Viking VFR-500 program numbers ≠ Potter G3 template numbers** (Viking F_072523 Rev 04 vs Potter 5403798 Rev C); never map one onto the other, and never accept "Program #n" alone (Program 0 edits can change any template — verify the as-loaded program); (10) **Low Air Alarm alone = supervisory**, never general alarm — the SOO must not say "low air → alarm"; (11) **"SUP 1 defaults to abort"** is printed on some G3 water templates (Potter #30/#32/#35) and abort is **not a UL-listed water-based function** (VFR-500 p. 5-36) → confirm no IDC is typed abort, SUP 1 retyped Supervisory, and witness it; (12) **monitored solenoid = a second supervisory IDC** (e.g. Viking F_031225 Rev 01 Apr 2025 surveillance switch) — count it in the IDC map; (13) panel program must match the trim's output count (a SureFire-type trim needs a program with an **N/O-solenoid output**; a one-release-output El/El program cannot drive it) — **identify by function, never freeze the SKU**.

**Failsafe standby-power consequence.** Hand the amp-hour math to the battery method. A failsafe normally-open block solenoid is de-energized in normal standby and powered only on the pipe-damage or low-air leg. A normally energized pattern can exceed the panel battery at the FM 90 h / 10 min basis. Flag the standby state as a submittal question. Do not copy another panel's amp-hour total.

Name the 90 h vs 24 h delta; **do not** run the AH calc here.

---

### 3.8 Double-interlock only — El/El failsafe is a QUESTION; variant-election is a HAND-OFF ROW

**Handshake:** `preaction-el-el-trim-election` (trim catalog lives there). **Ask on every DI (and any El/El) submittal:**

> *What happens on total loss of releasing-panel primary and secondary power — does this system degrade to dry-pipe, or to nothing?*

| Variant | 1st interlock | 2nd interlock | Panel dependence | Fail-dead? |
|---|---|---|---|---|
| **Electric/Pneumatic (El/Pn)** | electric → solenoid | **mechanical** pneumatic actuator | detection only | mechanical 2nd gate survives |
| **Pneumatic/Pneumatic (Pn/Pn)** | pneumatic release line | **mechanical** 2nd actuator | **none** | independent of electricity |
| **Electric/Pneu-Lectric (El/El)** | electric → panel circuit 1 | **electrical** air switch → circuit 2 | **both gates inside the panel** | **no automatic release path unless a failsafe trim is specified** |

Failsafe answer: a **normally-open solenoid plus a pneumatic actuator** so that on complete loss of AC **and** standby the system **degrades to dry-pipe rather than to nothing**.

**Emit one hand-off row, then stop the trim work.** Do not write gauges, drains, dehydrator, 30/50 psi actuator prime, or closet heater here.

**Two delivery clocks — name; do not prove** (handshake `dry-preaction-water-delivery-screen` / hydraulics / IST):

| | NFPA 13 (code floor) | FM DS 5-32 (controlling for a DC) |
|---|---|---|
| Time | **60 s** | **30 s** |
| Measured to | the **system test connection** (ITC) | the **single most remote sprinkler** |
| FM definition | — | **trip time + water travel time**, endpoint = **design pressure at the remote sprinkler** |

A passing 60-s-to-test-connection result does **not** satisfy FM. DI company BOD inherits the **60 s ITC** code-floor clock **and** the **30 s remote** FM clock — **never substitute**. This Skill **names** both; it does **not** run the fill calc.

**Nitrogen handshake:** day-one N₂ on company dry/DI is consumed from `nitrogen-inerting-and-c-factor-gate` / packet — do not re-derive purity or C here; do not invent supervisory-gas defaults.

---

### 3.9 Write the sequence of operations

Platform-agnostic. This SOO **supersedes** any simplified sketches in prior detection or suppression packages.

**Water — company DI (controlling):**

1. **S0 Normal / Standby.** Valve closed; piping dry, supervised (air or N₂); disconnects enabled.
2. **Alert (L1).** A1 + N1 + L1. **No release. No mechanical action.**
3. **Action / pre-alarm (L2).** A2 + N1 + L1. M1 if gate blown. P1 **only if** the pinned initiation level is L2. **W1 does not fire on L2 alone.**
4. **L2 AND low_air (sprinkler operation / low-air alarm).** **W1** (detection **AND** low-air; **no cross-zone smoke; no abort; no pre-trip delay**) → pipe fills; **≤30 s** to most remote sprinkler (FM) — **named, not proved**. Code-floor **60 s to ITC** remains the other named clock.
5. **Waterflow.** Thermal discharge continues. P1 complete at wetted equipment **before water arrives** (intent; timing method may be `[V]`).
6. **L3 Alarm / Fire** (and/or waterflow). Complete P1 (direct UPS shutdown + shunt-trip). M2 **after** P1. **Do not** auto-operate smoke exhaust.
7. **Supervisory / maintenance.** High air-or-N₂, valve tamper, disconnect, panel fault → T1. Low-air alone on DI is an interlock input **and** supervisory — it does **not** trip W1 without prealarm.

**HVAC thermal clock — rows the SOO must carry when M1 / M2 exist (method; numbers are `[SYN]` screens, not defaults):**
- **M2 (HVAC shutdown) := P1_complete OR waterflow** — never on pre-alarm alone, never on a timer alone (a prior layout package truth table; FM DS 5-32 Jan-2026 §3.4.2.2 keep cooling until equipment is de-energized).
- **Ventilation slowdown at FM DS 5-32 §2.4.2.1.3 is time-limited.** At full information-technology load, inlet temperature can reach the head rating in well under a minute, and at high density the slowdown alone can fuse heads. Provide a thermal override at head elevation, and bound the dwell from the fastest expected head operation times 0.75. An unbounded dwell on a wet hall is unresolved. Where slowdown and cooling continuation collide, record the owner and insurer decision. Do not copy another hall's watt density or timer.
- **Federal reference only (TSFPEWG G 3-600-01.01-18, Change 1):** cooling loss → IT power disconnect (2-8.1.4); cooling **not** shut on waterflow (2-5.3.5 / 4-5.7). Cite as comparison; the FM / owner layer governs a commercial hall.

**Water — company wet (controlling):** S0 → Alert/Action annunciation as pinned → thermal head operation → waterflow → P1/M2 per policy. **No W1 releasing trip. No abort / disconnect / delay on the sprinkler.**

**Comparison-only SI SOO fragment** (do not program as company default): L2 → **W1 immediately** (detection alone). Label every such fragment `comparison-only`.

**Clean-agent adjunct (parallel path, if present):** Alert → general alarm (1st detector, 60 bpm, countdown does not start) → pre-discharge (2nd detector, 120 bpm, ≤30 s delay, abort per pinned mode, **manual overrides abort**) → release (hold ≥10 min or until de-energized). Path B (wet/DI primary) remains fully automatic.

**Failure fallbacks:** Disconnect open → W1 and G1 **inhibited**, T1. Panel trouble → release **inhibited**. DI inoperative RCU: name the degraded state (dry-pipe vs nothing).

**Commissioning hooks (name; handshake `commissioning-ist-acceptance-packet`; do not run other Skills’ tests):** heated-wire VEWFD (Alert/Pre-Alarm within **120 s**; fans ON and OFF; ≥3×/condition — DS 5-32 App. C / Table C.2); ASD transport **≤60 s** (consume from ASD Skill); functional test — company DI trips only on **pre-alarm AND low_air** with **no cross-zone smoke dependency**; as-programmed map + three must-not-release tests (DI). Detection ITM companion sheets: **FM DS 5-48** (opened) Tables 5–7; **FM DS 5-40** held Sep-2007 with **edition-stale** flag vs NFPA 72-2025 — cite, do not invent ASD lifecycle frequencies.

---

### 3.10 Show-and-verify (timing-budget and Boolean checks — not `calcs`, not ASD sizing)

```
ACH = Q_cfm × 60 / V_ft3
# Gate blown if velocity >= 5 ft/s OR ACH >= 60 (declare V = room-only)

ride_through_min = 10 to 15 # §3.5.2
hold_min = 10 # §2.5.3.1.2
direct_ups_required = (ride_through_min >= hold_min) # TRUE -> do not feed-cut only

t_evac = travel_ft / walk_ft_per_s + reaction_s
# delay_s must satisfy t_evac <= delay_s <= 30
# 30 s is a CAP. Do not pad to 30 by default.

nfpa13_clock = 60 s to ITC
fm_clock = 30 s to most remote sprinkler at DESIGN PRESSURE
# Name both; do not prove fill here.

# Company DI Boolean check
assert O_preaction_trip == (prealarm AND low_air_alarm
 AND NOT release_disconnect AND NOT panel_trouble)
```

---

### 3.11 Status register and flags (mandatory every run)

Emit with Outputs. **Every controlling claim / matrix row / gate gets a Status-register token.** Vocabulary matches STS / ITM / campus bar:

| Status | Use on this Skill |
|---|---|
| `grounded` | Controlling DI/wet C&E cell pinned to mined/held sheet + edition + company-elected BOD |
| `provisional` | Conditional on provisional insurer-union, open non-gating RFI, or unpinned power-isolation pattern with assumptions stated |
| `unresolved` | Open hole (carried as `ASSUMED`, flagged — not a Stop; packet optional): missing STS election, missing VEWFD stages/zones, missing abort mode on adjunct=y |
| `comparison-only` | SI/NI matrix/column; FM Wet→NI→SI→DI ranking; SI trip-on-pre-alarm training Boolean; AXA SI preference |
| `handoff` | El/El trim; nitrogen; water-delivery prove; commissioning-IST; power-isolation means; out of scope |
| `RFI-variance` | Company-fence gate: SI/NI/foam/mist (or other prohibited medium) presented as election/BOD |

| Flag | Use |
|---|---|
| **`[SYN]`** | Project quantities invented (egress travel, a hall ACH you were not given). |
| **`[V]`** | NFPA 72-2025 section numbering outside §23.11, power-isolation level, NEC 645 text for the enforced edition, owner emergency-power-off choice, airflow volume basis. |

**Rules:**

- SI/NI evidence rows → `comparison-only`. SI/NI as election/BOD → **Stop** with `RFI-variance`.
- Foam as election/design → `RFI-variance` (prohibited). Mist as election/design → `RFI-variance` + `PRACTICE REFUSED`.
- Do **not** label a C&E built on an `ASSUMED` / `unresolved` STS election `grounded`; emit it as ASSUMED-based. (A missing packet does not block.)
- Preserve `[SYN]` / `[V]` beside the Status-register token; do not collapse them into it.

**L1 vs L2 split:** FM grounds **two** effective per-port values — **0.2 %/ft** alert/pre-alarm and **1.0 %/ft** alarm (DS 5-32 §3.3.2.2/.3). The L1/L2 split *within* 0.2 %/ft is **configured ASD staging**, not a third grounded number.

---

## 4. Output

An **authoritative releasing C&E matrix + written SOO** written **only** to the caller-named path.

**Minimum contents:**

1. Edition-pin block (13-2025 and 72-2025 deltas; FM DS 5-32 Jan-2026; DS 2-0 Oct-2021/Jan-2024; DS 5-48 opened / DS 5-40 stale flags as applicable).
2. Inputs echoed — packet if present (optional); STS-elected `system_type` wet|dry|DI; VEWFD stages/zones; adjunct y/n; power-isolation posture. **No SI-as-BOD.**
3. Branch banner with **company-controlling** Boolean: `preaction_trip := VEWFD_prealarm AND low_air` (DI) or wet thermal-only; SI trip-on-pre-alarm labeled `comparison-only` if shown.
4. **Controlling** C&E matrix (DI / wet) with explicit **non-outputs** + **comparison-only** SI/NI matrix/column.
5. Software truth table (company DI).
6. Written SOO (DI or wet controlling; adjunct if present).
7. RCU parameter schedule; DI El/El failsafe question + trim hand-off row (if DI).
8. Explicit handshakes named: water-delivery (30/60); El/El trim; nitrogen; commissioning-ist; power-isolation.
9. Show-and-verify; Δ vs 13-2025 and 72-2025.
10. **Status register** (mandatory) + `[SYN]`/`[V]` register.
11. Honesty line: SI corpus packages = comparison-only; another hall's DI/wet packages = `[SYN]` METHOD only — no package numbers, zone landings or program numbers as defaults.

Do **not** emit occupancy schedule, density×area `calcs`, pump envelope, ASD port math, valve/trim catalog, ITM interval calendar, assignment-packet rebuild, CAD, foam/mist design, or a controlling C&E as if SI were company-elected.

---

## 5. Stop

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess:

1. Occupancy, VEWFD architecture, or **company-elected** system type not pinned.
2. **Missing STS election** / missing assignment packet / missing matrix controlling releasing or system-family row (`unresolved`).
3. **SI / NI / other preaction presented as BOD** → `RFI-variance` / company-fence. Do not emit controlling C&E as if SI were elected.
4. **Foam** as election/design → `RFI-variance` (prohibited). **Mist** as election/design → `RFI-variance` (`PRACTICE REFUSED`).
5. Missing VEWFD stages or zone list.
6. Clean agent, foam, mist, or deluge requested as the releasing basis → stop.
7. Power-isolation level demanded as an FM pin when §2.5.3.1.1 is ambiguous — flag `[V]`, ask, do not invent.
8. Caller asks to put abort or pre-discharge delay on the water path, or to cross-zone a water trip with a **second smoke zone**, or to auto-operate smoke exhaust off detection.
9. A second hazard outside wet, dry, or double-interlock is on the same panel → stop. Do not add abort or discharge delay to the water path.
10. Caller asks to classify occupancy, run density×area, size a pump, **select** suppression technology, size ASD, write a trim catalog, or invent NFPA **72-2025 subsection numbers**.
11. Caller asks to copy another hall's numbers, zone map, or program as the default, or to write a single-interlock trip on pre-alarm as the controlling Boolean.
12. An owner note is treated as a numeric initiation level without a cited standard.

Deluge type → Stop the company DI / wet default.

---

## 6. Citations (section **and** edition)

Shop codebook **by title**. **FM DS 5-32 Jan-2026:** §2.4.1.1 ranking (**comparison-only**); §2.4.3.2.1.3 / .3.1 L2 trip language (**comparison evidence** vs company DI AND); **§2.4.3.2.1.3.2** no cross-zone smoke; §2.4.3.2.1.3.3 two independent VEWFD; §2.4.2.1.7 exhaust (sheet may say *"water-mist"* — language only); §2.4.2.1.3 airflow gate; §2.4.2.1.10 Class V+; §2.4.3.2.1.2.D ≤30 s to remote sprinkler; §2.5.3.1.1 power isolation level **unpinned**. **FM DS 2-0 Oct-2021/Jan-2024:** §2.2.1.12.3.1(A) occupancy-sheet gate; §2.2.1.12.1.1 FM Approved combination; §2.3.3.2 waterflow ≤60 s. **NFPA 72 §23.11.1–.7** (2019 capture → **`[V]` vs 72-2025**). **UL 864** abort-on-water prohibition. **FM DS 5-48** Jan-2011 / IR Apr-2025 (opened) — detection ITM companion. **FM DS 5-40** Sep-2007 held — **edition-stale** vs NFPA 72-2025; cite with stale warning.

**Absent (name the hole; do not fill it):**

- Licensed NFPA 72-2025 and NFPA 13-2025 full text are not in this pack. Numbering outside NFPA 72-2025 §23.11.1 through §23.11.11 stays unverified. Do not invent 72-2025 subsections.
- IFC-2024 §909 overlay.
- Tier-A owner releasing standard — still Absent; structure only under NDA.

**Removed from Absent / do not re-list as holes:** FM DS 5-48 (**opened**). DS 5-40 is **held** but **edition-stale** — not Absent, not current.

---

## 7. Design practice

1. Three-layer, most stringent, per parameter. Code is the floor (NFPA 13 family permission + NFPA 72 Ch. 23 RCU). Insurer sheets supply sequence evidence; **company fence controls the BOD**: wet / dry / **DI** only. Report Δ vs **13-2025** and **72-2025**. Cite **section AND edition**.
2. Per-parameter, not per-layer. A second smoke zone is prohibited as a trip gate on the water path. Low air is the second double-interlock gate.
3. Owner may raise, never lower. NDA is structure, not an L2/L3 pin.
4. Current editions; enforced is not the same as latest. Do not invent subsections.
5. Show the airflow gate, the 30 s versus 60 s clocks (named, not proved), and the double-interlock AND Boolean.
6. Honesty. Power-isolation **level** is unpinned — **ask**. El/El failsafe is a **question**, not a catalog. Corpus DI/wet packages are `[SYN]` METHOD only; SI packages comparison-only.
7. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.
8. Caller-path-only. Keep `[SYN]` / `[V]` visible.

**Directional Δ vs NFPA 13-2025:** NFPA 13 **permits** the whole preaction family and **does not prohibit** cross-zoned detection; **does not recognize abort** on preaction (no abort clause in any edition 2016–2025). FM **imposes** ≤30 s to the remote sprinkler (vs 13’s **60 s to the ITC**) and warns on DI / triple-interlock configurations. **Company fence** removes SI/NI as election even where FM/AXA prefer them — ranking stays `comparison-only`.

**Directional Δ vs NFPA 72-2025:** Ch. 23 **is** the RCU floor. FM **adds** Class V+, **90 h / 10 min** vs 72’s **24 h / 5 min** ([CODE NFPA 72-2025 §10.6.7.2.1/§10.6.7.2.2]). UL 864 abort-on-water is a **listing** overlay.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH | `occupancy-hazard-fork` |
| Density × area `calcs` | `density-area-dry-increase` |
| Dual-carrier BOD | `most-stringent-basis-matrix` |
| Pump envelope | `pump-envelope` |
| ITM intervals / design-for-testability | `itm-design-for-testability` |
| Assignment packet | the input packet |
| Wet vs SI vs DI vs gas **selection** | `suppression-technology-selection` |
| ASD port count / transport-time sizing | `asd-vewfd-return-sampling` |
| Valve/trim catalog, El/El **hardware election** | `preaction-el-el-trim-election` (hand-off row only here) |
| Nitrogen purity / C-factor | `nitrogen-inerting-and-c-factor-gate` |
| Prove 30/60 water-delivery fill | `dry-preaction-water-delivery-screen` / hydraulics / IST |
| Commissioning / IST execution | `commissioning-ist-acceptance-packet` |
| Power isolation means / EPO design | `power-isolation-disconnect-control` |
| Agent weight `W`, door-fan hold-time | the out-of-scope method / the out-of-scope method |

---

## Check before you finish

1. **Hard scope gate:** company wet/dry/DI only; SI/NI comparison-only; foam prohibited; mist `PRACTICE REFUSED`. Stop on BOD violations / SI-as-BOD.
2. Confirm **assignment packet** + **STS election** + matrix releasing rows. Missing / unresolved → proceed with `ASSUMED` (flagged), not a Stop.
3. Confirm remaining inputs (detection stages, zones, HVAC policy, listing pair). Leave NFPA 72-2025 numbering outside §23.11 unverified.
4. Pin editions; cite DS 2-0 gate **and** DS 5-32 grant together when smoke activates preaction.
5. Confirm branch; do **not** re-select the system. Deluge → Stop company default.
6. Encode **company-controlling** water Boolean: DI `preaction_trip := VEWFD_prealarm AND low_air`; wet = thermal-only / no W1. SI `:= VEWFD_prealarm` only as `comparison-only`. NO abort / delay on W1. Exhaust follows water. Sheet *"water-mist"* = language only.
7. Ask circuit 2; ask El/El failsafe on DI; hand off trim. Name 30/60 clocks; do not prove. Handshake nitrogen / IST / power-isolation.
8. Fill **controlling** C&E + truth table; emit SI/NI **comparison** matrix/column separately. Delete any “default SI white space” controlling title.
9. If gas: coincidence, abort mode, delay ≤30 s as a cap, prove abort cannot reach W1, physical disconnect.
10. Power isolation: ask the level; direct UPS shutdown.
11. RCU parameter schedule. Write the SOO. Show-and-verify. Δ vs 13-2025 and 72-2025.
12. **Status register** mandatory: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` + `[SYN]`/`[V]`.
13. Single-interlock examples stay comparison-only. Do not copy another hall's numbers. Check the manual-release override, and check that cooling shutdown follows power isolation or waterflow.
14. Write **only** to the caller-named path.
