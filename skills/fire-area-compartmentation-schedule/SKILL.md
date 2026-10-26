---
name: Fire-area compartmentation schedule
description: >-
  use this when (ideally after occupancy-hazard-fork’s boundary register and
  basis-matrix compartmentation rows exist — if absent, assume the more
  stringent case and flag ASSUMED) a multi-hall US data-center program
  needs the passive DP-to-DP / hall↔support fire-area schedule (FM 2-hr vs AXA
  ≥1-hr most-stringent, door/damper/firestop package) before per-hall
  density-area — not occupancy from scratch, not density×area, not full
  releasing C&E.
---
# Fire-area compartmentation schedule

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe.

**This Skill owns** the building-scale **passive fire-area / compartmentation schedule**: rated separations between DP halls and support spaces, opening-protective / damper correspondence, continuity / firestop / joint FLAGS, and the **passive-layer C&E spine** (door release + damper close).

It does **not** own occupancy classification, §903.2 forks, three-layer BOD rebuild, system-family election, density×area, full releasing C&E, ESS sprinkler/explosion design, MFL wall design, or exterior-exposure envelopes.

**Core thesis:** on a multi-hall FM (or dual-carrier) job the headline reconciliation is often **FM DS 5-32 §2.2.4 2-hr between multiple DP rooms** over **AXA XL ≥1-hr full-height** — **Rule C / most-stringent on the rating axis**, with AXA's **FA-activated dampers** and **slab-to-deck extent** folded in on their own axes. The **code floor** frequently does **not** itself mandate hall-to-hall FRR on a sprinklered same-occupancy Group B path; name the real driver (usually insurer/owner). Then hang the **door / damper / firestop / joint** package off the elected wall rating — and here **code can exceed the carrier** (2-hr barrier ⇒ **1½-hr door**, even if carriers habitually say ¾-hr).

**Design practice:** three-layer basis (code floor × insurer A × insurer B-or-n/a × owner) → **most-stringent union PER PARAMETER** (rating, extent, door, damper trigger/rating, continuity, assembly type). Report **Δ vs IBC-2024 / IFC-2024** (and directional vs NFPA 13-2025 where relevant — **13 does not set DP-to-DP FRR**). Cite **section AND edition**. Show-and-verify ratios. Flag invented values `[SYN]` / unpinned `[V]`. Generic — do not copy a 4-hall / 250,000 ft² prototype onto another job.

**Assembly-type honesty:** prefer **fire barrier (IBC §707)** as the DC default for hall↔hall / hall↔support insurer compartments. Reserve **fire wall (IBC §706)** for the deliberate separate-building effect. If the §706 vs §707 fork is unpinned → flag **`[V]`** and do not silently assume parapets.

Write the schedule **only** to the path the **caller** names. Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

Elected water-based systems elsewhere may be only:

- Wet-pipe sprinkler
- Dry-pipe sprinkler
- Double-interlock preaction

Comparison-only (never elected by company Skills):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**Foam** is prohibited for company scope. **Water mist** is `PRACTICE REFUSED`.

This Skill does **not** elect a system family. If `suppression-technology-selection` is present, **acknowledge** the elected wet/dry/DI status for passive C&E handoff consistency only.

If the caller asks this Skill to **authorize** single-interlock, non-interlock, foam, or mist:

1. Record the request.
2. **Stop**.
3. Return an `RFI/variance` / company-fence gate.
4. Do not substitute or design the prohibited option.

### 1.2 What this Skill designs

| In scope | Out of scope |
|---|---|
| FP-FB compartmentation schedule (rating, assembly type, door, damper, continuity) | Occupancy group / §903.2 / HC from scratch |
| Passive door-release + damper-close C&E spine | Full releasing Boolean / abort / gas adjunct |
| Purpose fork (code job vs insurer/owner job) | Density×area, pump, tank, hydraulics |
| Correspondence ratios + DYNAMIC damper schedule defaults | Damper model selection / UL EMME directory deep dive (handoff) |
| Firestop / joint FLAG rows + ownership posture | Full UL system-number detailing (handoff) |
| ESS / non-Li battery / NFPA 75 / BOC rating **pins** on the schedule | ESS sprinkler, explosion control, off-gas design |

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent hall counts, ratings, door hours, or boundary statuses from habit.

| Input | Required | Rule |
|---|---|---|
| **Building / hall inventory** | **yes** | Named DP halls + support spaces (MMR/network, electrical/MEP, UPS/BBU, generator/fuel-oil, tape/storage, admin, BOC/ICS if present). Missing inventory → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `occupancy-hazard-fork` result** | **yes** | Must include **boundary register** with status per boundary: `verified-rated` / `unrated-open` / `unresolved`. Missing result or omitted register → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `most-stringent-basis-matrix` compartmentation rows** | **yes** | Consume rating / extent / door / damper rows. Do **not** rebuild the matrix. Dual-carrier with a named carrier's compartmentation values missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (assume the more stringent rating). |
| **Carrier posture** | **yes** (usually inherited) | `FM` / `AXA XL` / `dual` / other named / explicit `n/a`. Confirm against basis-matrix. |
| **AHJ-enforced I-Code cycle** | **yes** to cite | Prefer edition pins inherited from basis-matrix. Unamended **2024** model floor is the shop default for rules; local adoption may lag. Unpinned → still emit insurer union; mark code override **`[V]`**. |
| **Owner compartmentation posture** | **yes** (may be `none` / `empty`) | Project-issued or explicit empty. NDA → structure-only; may raise, never lower. |
| **Caller output path** | **yes** for file output | If unnamed, return the schedule in the response and stop. |
| **`suppression-technology-selection` result** | optional | Acknowledge elected wet/dry/DI for C&E consistency. Do not elect systems here. Absent → continue; mark system-family acknowledgment `n/a` or `[V]`. |

Optional (do not block alone; flag `[V]` where used): assignment packet; construction type; §507 unlimited-area election; smoke-control / FCC triggers (usually **not** size alone); generator/fuel special-hazard overlays beyond schedule pins.

**Do not invent** an IBC Table 506.2 cell, a ¾-hr door on a 2-hr barrier as AHJ-ok, a hall-to-hall code mandate that is actually an insurer requirement, or an AXA **PRC 17.10** clause (not in corpus — see §5.2). *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Boundary register intake (mandatory)

For each boundary that will become an FB schedule row, read the occupancy-hazard-fork status:

| Status | Schedule action |
|---|---|
| `verified-rated` | Schedule the assembly package; record known hourly rating or mark rating `[V]` if unpinned |
| `unrated-open` | Do **not** invent a rated wall to fix classification. Record consequence (greatest-hazard already owned upstream). Emit RFI/FLAG if the program still needs a rated separation for insurer/owner reasons |
| `unresolved` | **Not a Stop**: carry any FB row that depends on that boundary on a stated `ASSUMED` rating (the more stringent), flagged. Never assume a lower rating |

An omitted boundary needed for an FB row is not harmless → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (assume the more stringent rating).

### 2.2 Basis-matrix compartmentation intake (mandatory)

Consume, do not rebuild:

- Compartmentation **rating** rows (DP↔DP, DP↔support, special rooms)
- Compartmentation **extent** / continuity
- **Door** rating (carrier habit vs code override posture)
- **Damper** trigger and rating
- Provisional / unresolved / `[V]` statuses on those rows
- Dual-carrier union already performed under Rule C / per-parameter logic

If a required compartmentation row is `unresolved` in the matrix → **not a Stop**: carry the more stringent candidate as `ASSUMED` (flagged) or emit FLAG rows — never silently invent the controlling value.

### 2.3 Look up by title

*Design practice*; *Enforced-vs-latest edition resolver and reference pins*; *FM DS 5-32 insurer design basis*; *AXA XL insurer design basis*; *Fire-resistance-rated compartmentation and assemblies*; *FRR construction compartmentation IBC 2024* (source); *Fire and smoke damper selection and installation*; *Through-penetration firestop system selection and specification*; *NFPA 75 ITE room applicability and requirements*; *Li-ion ESS battery room sprinkler protection*; *UPS and DC battery room protection (non-lithium)* / DS 5-28 content in the FRR note; *MFL limiting factors walls space separation and openings*; *MFL evaluation and campus loss limitation*; *Campus exterior fire exposure separation and wall protection*; *Process control room and ICS/OT fire protection*; *The hyperscaler owner-standard layer*.

---

## 3. Pin editions (enforced ≠ latest)

| Standard | Role | Shop-pinned editions |
|---|---|---|
| **IBC / IFC** | Fire wall §706, fire barrier §707, openings §716, dampers §717, firestop §714, joints §715, fire-area / allowable area Ch.5, mixed occupancy §508 | Model floor **2024**; adopted local edition governs. Table **cells** may be `[V]` if unlicensed |
| **IMC** | Damper companion to IBC §717 | Match I-Code cycle |
| **FM DS 5-32** | Compartmentation ratings / doors / slab continuity | **January 2026 §2.2.4** |
| **FM DS 5-33** | Dedicated Li-ion ESS cutoff-room construction | **January 2024** path — **§2.3.4** min **2-hr** room |
| **FM DS 5-28** | Non-Li battery room rating | **April 2021 §2.2.4** — unconditional **≥1-hr** |
| **FM DS 7-110** | Process control / ICS room separation | **June 2026 §2.2.5–§2.2.8** — min **1-hr** when inventory includes BOC/ICS |
| **FM DS 1-22 / 1-42** | MFL definition / MFL wall (not ordinary hall barrier) | DS 1-22 **Int. Jan-2026**; DS 1-42 **Int. Apr-2025** — route away |
| **FM DS 1-20 / 9-19** | Exterior exposed wall / WUI | DS 1-20 **Apr-2025**; DS 9-19 **Int. Jan-2024** — route away |
| **AXA XL** | ≥1-hr full-height; FA-activated dampers; slab-to-deck | Date the *claim*: whitepaper **Mar-2026 p.4 / p.9**. **PRC 17.10 not in corpus** → `[V]` / procurement |
| **NFPA 75** | ITE-area separation floor when adopted | **2024** — ≥1-hr [CODE NFPA 75-2020/2024 §6.1.3.2, pull 75-05]; doors ≥45 min [CODE NFPA 75-2020/2024 §6.1.3.4: ¾-h doors in 1-h construction, 1½-h in 2-h, pull 75-05] |
| **NFPA 80 / UL 10C / UL 555 / UL 555S** | Door / damper listing bases | Listing, not a substitute for §716/§717 correspondence |

Inherit pins from `most-stringent-basis-matrix` when present. Surface enforced ≠ latest gaps; do not silently upgrade local adoption.

---

## 4. Ask the purpose question first (code job vs insurer/owner job)

```
IF wall is doing a CODE job
   (separated occupancies §508.4 / fire-area strategy §707 / control-area-MAQ /
    ESS IFC Ch.12 / shaft / exit enclosure / NFPA 75 ITE separation when adopted)
   => assembly type + rating follow that code job (then raise to insurer/owner if higher)
ELSE IF halls are same-occupancy on a compliant Ch.5 path (often §507 unlimited-area Group B)
   => code floor may be "no internal hall-to-hall FRR required"
   => 2-hr / 1-hr walls are INSURER or OWNER requirements — name them
```

**Do not invent a code requirement that isn't there.** Attributing FM's 2-hr DP-to-DP wall to the building code misstates the basis and corrupts Δ reporting.

Chase **§507 unlimited-area** before drawing any internal **fire wall** for allowable-area reasons. Large floor area alone does **not** trigger IBC §909 smoke control or §911 fire command center.

Δ reporting: often **+2 hr over none-identified** for B↔B insurer walls on a compliant Ch.5 path. NFPA 13-2025 is **directional only** here — it does not set DP-to-DP FRR.

---

## 5. Three-layer union — compartmentation parameters separately

Do **not** MAX whole sheets. Prefer the consumed basis-matrix controlling values; this table is the shop reconciliation pattern when closing or verifying those rows.

| Parameter | FM DS 5-32 §2.2.4 (Jan-2026) | AXA XL (whitepaper Mar-2026 p.4/p.9) | Union rule |
|---|---|---|---|
| **Rating — DP↔DP** | **2-hr** between multiple DP rooms | ≥1-hr full-height | **C** → **2-hr** |
| **Rating — DP↔support** (network / electrical / MEP) | **1-hr** | ≥1-hr | **B/tie** → **1-hr** (raise if special hazard demands) |
| **Rating — generator / fuel-oil** | **1-hr** FM floor | ≥1-hr | **1-hr floor + FLAG** — NFPA 30/37 / sibling generator sheets may raise; do not invent the higher number |
| **Rating — dedicated Li-ion ESS cutoff** | DS 5-33 §2.3.4 **min 2-hr** room (floors/walls/ceiling) | ≥1-hr (raise) | **C** → **2-hr** grounded pin; IFC Table 1207.7 cells remain `[V]`; further raise = FLAG |
| **Rating — non-Li UPS / lead-acid / NiCd room** | DS 5-28 §2.2.4 **≥1-hr** unconditional (no area/kWh threshold) | ≥1-hr | **≥1-hr** grounded; do not omit small closets |
| **Rating — tape / bulk storage** | keep OUT of DP rooms; 1-hr room | ≥1-hr | **1-hr + out-of-hall rule** |
| **Rating — BOC / process-control / ICS** (when in inventory) | DS 7-110 §2.2.5 min **1-hr**; redundant trains in separate rated areas §2.2.6 | ≥1-hr if AXA applies | **1-hr** insurer job; §707 package |
| **Extent / continuity** | slab-to-slab | full-height slab-to-deck | **C** → **slab → underside of roof deck** (single-story) |
| **Door (carrier habit)** | **¾-hr** | **¾-hr** | **B** then **code override** (§7) |
| **Damper trigger** | close on FA / releasing C&E | **FA-activated dampers** | **C/D** → **FA-activated** (combo F&S when both functions required) |

**In-hall preaction zones are not fire areas.** Do not schedule FB tags between multizone PA-Z1/Z2 of one hall unless architecture truly provides rated separation (unusual). Align with `multizone-preaction-zone-alignment`.

### 5.1 NFPA 75 parallel floor (when adopted / referenced)

Where NFPA 75 applies to the ITE area:

- Prescriptive floor: **≥1-hr** fire-rated separation extending floor → floor above or roof; **doors ≥45 minutes**
- Then **raise** to insurer/owner (FM 2-hr DP↔DP / AXA ≥1-hr / owner)
- Li-ion / BBU / ESS protection is **out of NFPA 75-2024** → route to NFPA 855 + IFC Ch.12 + ESS Skills; do not cite 75 for batteries

If adoption is unknown → record NFPA 75 status `[V]` / `unresolved` and do not invent applicability.

### 5.2 AXA PRC 17.10 honesty

AXA compartmentation numbers in this Skill are pinned to the **Mar-2026 whitepaper p.4 / p.9** (≥1-hr full-height; ¾-hr doors; slab-to-roof-deck; FA-activated dampers).

**AXA XL PRC 17.10 is not in the corpus.** Do **not** invent PRC 17.10 clauses. If a caller or upstream result cites 17.10 as controlling → mark **`[V]` / procurement**, keep whitepaper pins as the held claim basis, and stop only if the matrix itself left the AXA compartmentation row unresolved.

---

## 6. Select assembly type (§706 vs §707) — corpus default

| Purpose | Assembly | Consequence |
|---|---|---|
| Create **separate buildings** for height/area/type-of-construction | **Fire wall §706** | Structural stability; continuity; **≥30-in** roof projection; opening **≤156 ft²** and aggregate width **≤25%** (§706.8) — usually too strong for ordinary hall↔hall |
| Hall↔hall, hall↔MMR, hall↔UPS/ESS/generator, shafts, exit enclosures, insurer compartments, BOC/ICS | **Fire barrier §707** — **DC default** | Continuity §707.5 (slab→underside of deck); **supporting construction rated to match** §707.5.1 |
| Corridor-class | Fire partition §708 | Not the hall-separation tool |
| Smoke compartment only | Smoke barrier §709 | 20-min S-doors — does **not** satisfy insurer *fire* separation |

If the job leaves §706 vs §707 unpinned → schedule the **rating + package**, mark assembly-type **`[V] fire wall vs fire barrier undecided`**, and do not invent parapets.

### 6.1 MFL vs IBC assembly fence (mandatory)

Ordinary insurer / owner hall↔hall **2-hr fire barriers** are **not** FM **MFL fire walls**.

| Construct | Typical rating | Owner Skill / note |
|---|---|---|
| IBC / DS 5-32 hall compartment (this Skill) | 1-hr / 2-hr fire **barrier** §707 | This Skill |
| FM MFL fire wall | Default **4-hour (F240 / EI240)** + separate opening / stability package | `mfl-limiting-factors-walls-space-separation-and-openings` — **FM DS 1-42 Int. Apr-2025** |
| MFL definition / impaired-active assumption | — | `mfl-evaluation-and-campus-loss-limitation` — **FM DS 1-22 Int. Jan-2026** |

**Do not** reuse the 2-hr → 1½-hr door correspondence as proof of MFL compliance. If the caller asks for an MFL wall schedule here → **Stop** and hand off.

### 6.2 Exterior / campus exposure fence (mandatory)

This Skill's interior FRR schedule is **not**:

- Exterior *exposed* wall package — **FM DS 1-20 April 2025**
- Wildland / WUI ember + radiant envelope — **FM DS 9-19 Interim January 2024**

Hand those to `campus-exterior-fire-exposure-separation-and-wall-protection` (or sibling Skill). Do not size yard-facing doors/glazing from the interior 2-hr → 1½-hr ladder alone.

---

## 7. Opening-protective / damper correspondence (code can beat the carrier)

**Memorize — this is where carrier habit fails:**

| Assembly | Door (IBC §716) | Fire damper (IBC §717 / IMC 607) |
|---|---|---|
| **1-hr fire barrier** | **¾-hr** | **1.5-hr** (assembly < 3 hr) |
| **2-hr fire barrier** | **1½-hr** (**not** ¾-hr) | **1.5-hr** (2 hr < 3 hr threshold — do **not** force a 3-hr damper) |
| ≥3-hr assembly | per Tables 716.1(2)/(3) `[V]` cells | **3-hr** damper |
| Corridor / smoke barrier | **20-min** S-door (UL 1784) — separate case | Smoke damper UL 555S |

**Show the ratio on a 2-hr DP-to-DP wall:**

```
insurer_door_ratio = 0.75 / 2.00 = 0.375 # NON-CONFORMING if ¾-hr kept on 2-hr
conforming_ratio ≈ 0.75
door_2hr_ok = 1.50 / 2.00 = 0.75 # 1½-hr — code override
```

**¾-hr on 2-hr is non-conforming.** Do not stamp the insurer-union ¾-hr door as AHJ-ok on a 2-hr barrier. Governing **1½-hr** is code correspondence; if the IBC-716 table is unlicensed as a stamped primary, still apply the ratio and flag **`[V]`/`[SYN]` FLAG** — never present ¾-hr as compliant.

Caller demand to stamp ¾-hr AHJ-ok on a 2-hr barrier → **Stop**.

### 7.1 DYNAMIC dampers — schedule default (elevated)

Rating correspondence alone is not enough.

For **DP-hall air paths where fans do NOT auto-shutdown** on fire (typical hyperscale hall — area-detection exception / availability posture):

1. Schedule **UL 555 DYNAMIC**-rated fire dampers (or **combination fire/smoke** dampers, inherently actuator-driven).
2. **Static**-rated fire dampers are acceptable **only** on systems that truly shut down automatically on fire (verify per AHU against the fan-shutdown matrix — fork is per-system, not per-building).
3. Prefer **combination fire/smoke** where FA-activation (AXA) and fire-barrier penetration (code) both apply; Leakage Class I preferred over Class II floor when available without sole-source risk.
4. **Max UL-listed multi-section damper size** for the chosen DYNAMIC model is a **hard architectural opening cap** (AMCA mullions are static-only — cannot split oversized DYNAMIC openings). Flag oversized openings at DD; do not defer to submittal.
5. **Damper annulus is listing-owned** — typically **1/8 in. per foot** of damper width/height, **min ¼ in., max 1½ in.** (round: opening ≥ OD + ⅞ in.). A damper penetration is **not** an ordinary through-penetration; **do not** pack the annulus with a generic ASTM E814 / UL 1479 detail that defeats the listing.
6. Deep model / sleeve / actuator / velocity selection → hand off to *Fire and smoke damper selection and installation* (and sibling Skill if present). This Skill still **schedules** DYNAMIC vs static + rating + FA trigger.

Cite: IBC §717.3.2 correspondence (<3 hr → 1½-hr damper; ≥3 hr → 3-hr); UL 555 / UL 555S; Greenheck life-safety dampers manual (Decent; written to IBC-2015 — cells `[V]` vs IBC-2024).

**Smoke exhaust:** do **not** auto-operate smoke exhaust in DP rooms (FM releasing posture); dampers **contain**.

---

## 8. Firestop / joints — ownership harden

Through-penetrations of rated assemblies require **listed systems** tested to **ASTM E814 / UL 1479** (F-rating always; T-rating in floors unless excepted). Joints (including head-of-wall) require **IBC §715 / ASTM E1966 / UL 2079**.

**Generic sealant is not a basis.**

Ownership posture on the schedule:

| Party | Owns |
|---|---|
| Architect / drawings | UL **design number** + hourly rating on the drawings |
| FP / system designer | Every penetration mapped + detail callouts matching wall type, penetrant, annulus, packing, movement |
| Contractor | Only what is drawn — no product substitution that breaks the listed system |

**Prefer minimize penetrations** of rated hall barriers. Where practical, **split air systems / reroute ducts** so the rated wall has no duct opening; every avoided damper and firestop is commissioning owned by nobody.

If full UL system-number detailing is out of this call's scope → emit a **FLAG** row pointing to *Through-penetration firestop system selection and specification* — do not invent systems.

Damper penetrations: see §7.1 — listing annulus, not generic E814 pack.

---

## 9. Special rating overlays (schedule pins)

### 9.1 Dedicated Li-ion ESS cutoff room

When inventory includes a **dedicated Li-ion ESS / UPS cutoff room**:

- Schedule **minimum 2-hr** fire-rated **floors, walls, and ceiling** per **FM DS 5-33 §2.3.4** (January 2024 path in corpus; assemblies per DS 1-21 as cited by that sheet).
- Door / damper / firestop package tracks the **2-hr** assembly (1½-hr door; 1.5-hr damper; DYNAMIC rules if air path applies).
- IFC-2024 **§1207.7.4 + Table 1207.7** now held (pulls IFC-36, IFC-IBC-IMC-24-bess2, model text / unamended proxy): ESS rooms get **2 h fire barriers (IBC §707) + 2 h horizontal assemblies (IBC §711)**. The Li-ion MAQ is **600 kWh per fire area** (IFC 2024 §1207.5.2 + Table 1207.5). Confirm the adopted edition and local amendments. The NFPA 855-2023 §9.6.4.1 1 h option is not used, because IFC §1207.7.4 is stricter.
- Sprinkler density, duration, rack separation, explosion control, off-gas → ESS Skills (`ess-isolation-venting-and-duration` and siblings). **FLAG** only; do not design here.
- Do **not** leave ESS at a soft 1-hr FM floor + maybe raise when the dedicated cutoff path applies.

### 9.2 Non-lithium battery rooms (lead-acid / NiCd / VRLA)

**FM DS 5-28 §2.2.4:** locate lead-acid and nickel-cadmium batteries in a **minimum one-hour** fire-rated room — **no area, capacity, or quantity threshold** and no unless sprinklered escape.

- Small switchgear-control battery closets are rated too — this is where the requirement is usually missed.
- Acid-containment floor seals (§2.2.5) are **not** fire-rating rules — call out separately if flooded batteries on upper floors.
- Li-ion rooms do **not** use this pin → §9.1 / ESS Skills.
- Code-floor reconciliation under IFC stationary-storage thresholds is **unreconciled** in corpus → design to FM; report delta; mark code cell `[V]` if needed.

### 9.3 Generator / fuel-oil

FM DS 5-32 §2.2.4 **1-hr** floor + AXA ≥1-hr. Higher ratings from NFPA 30/37 / generator-plant notes → **FLAG**, do not invent.

### 9.4 BOC / process-control / ICS (when in inventory)

**FM DS 7-110 §2.2.5–§2.2.8 (June 2026):**

- Minimum **one-hour** fire-rated separation between process control rooms and adjacent areas (including low-voltage switchgear rooms)
- Redundant process-control trains → each system's controls, equipment, **and cabling** in a **separate** fire-rated area
- Seal openings with listed penetration seals rated **equivalent to** the floor/wall
- Typical assembly: **fire barrier §707** doing an **insurer job**; door/damper follows 1-hr correspondence (¾-hr door; 1.5-hr damper)

If inventory has no BOC/ICS → omit the row.

### 9.5 Tape / bulk storage

Keep tape / bulk storage **out of DP rooms**; schedule **1-hr** room per FM §2.2.4 / AXA ≥1-hr.

---

## 10. Emit the compartmentation schedule (FP-FB)

Minimum columns:

| Col | Content |
|---|---|
| Tag | FB-1… |
| Separation (from → to) | DP↔DP, DP↔MMR, ESS envelope, BOC, etc. |
| Boundary register status | `verified-rated` / `unrated-open` / `unresolved` (consumed) |
| Assembly rating | 2-hr / 1-hr / flagged higher |
| Basis | FM §2.2.4 / DS 5-33 §2.3.4 / DS 5-28 §2.2.4 / DS 7-110 / AXA p.4/p.9 / NFPA 75 / code job / owner |
| Assembly type | fire barrier §707 / fire wall §706 / `[V]` |
| Door opening protective | 1½-hr on 2-hr; ¾-hr on 1-hr; NFPA 75 ≥45-min floor when applicable [CODE NFPA 75-2020/2024 §6.1.3.4: ¾-h doors in 1-h construction, 1½-h in 2-h, pull 75-05]; flags |
| Damper | rating + **DYNAMIC** or static (justified) + FA-activated / combo F&S |
| Continuity | slab→underside of roof deck (single-story); support rated to match |
| Notes / FLAG | ESS, generator, firestop UL design number, parapet, MFL-not-applicable, exterior handoff |

Also emit:

1. Edition-pin block (inherited + local)
2. Consumed upstream status (occupancy boundary register; basis-matrix compartmentation rows; tech-selection acknowledgment if present)
3. Purpose statement (code vs insurer/owner driver) per major separation class
4. Show-and-verify door ratio for every 2-hr line
5. Δ vs identified code floor (and directional vs NFPA 13-2025: n/a for DP-to-DP FRR)
6. Passive C&E spine (§11)
7. `[SYN]` / `[V]` / FLAG / RFI / handoff register
8. Explicit fences: MFL routed away; exterior routed away; PRC 17.10 not invented

---

## 11. Passive-layer C&E spine (not the full releasing matrix)

Platform-agnostic, testable. Hand water-path / power-isolation detail to their Skills. Acknowledge elected wet/dry/DI from tech-selection when present — do not change the election.

1. **On VEWFD L2 Pre-Alarm in an affected fire area:** annunciate; **release magnetic hold-opens** on that fire area's rated doors; **command FA-activated / combo dampers on that boundary to close**; HVAC slow/stop per detection C&E where the airflow gate requires it.
2. **On L3 / waterflow:** confirm doors released/latched and dampers closed; hold the barrier (protects N+1/2N adjacency); signal power-isolation panel — isolate critical loads **before water reaches energized equipment** (Fig D.1 intent; detail → `power-isolation-disconnect-control`).
3. **Fail-safe:** dampers close on loss of power or loss of FA signal; door hold-opens release on loss of power.
4. **Do not auto-operate smoke exhaust in DP rooms.**
5. **Supervision:** damper end-switches / door-release circuits to **Class V or greater** when the FA layer requires it; trouble = impairment until cleared.
6. **Cross-area guardrail:** compartmentation C&E for one fire area shall **not** trip suppression in an adjacent fire area.

Full water Boolean / abort / gas adjunct → `preaction-releasing-c-and-e-soo`.

---

## 12. Flags and status labels

| Flag / status | Use |
|---|---|
| **`[SYN]`** | Door/damper hours derived from ratio when table primary unlicensed; synthetic hall geometry counts |
| **`[V]`** | IBC table cells (506.2 / 508.4 / 707.3.10 / 716.1 / 717), §706 vs §707 fork, IFC 1207.7 cells, PRC 17.10, NFPA 75 adoption, owner NDA, unlicensed Greenheck→IBC-2024 cells |
| **`FLAG`** | Firestop UL design number deferred; generator higher rating; ESS explosion/off-gas; oversized DYNAMIC opening; parapet if §706 undecided |
| **`RFI/variance`** | Caller asks SI/mist/foam authorization; MFL requested here; ¾-hr stamped AHJ-ok on 2-hr |
| **`handoff`** | Work owned by another Skill/note |
| Grounded | FM 2-hr DP-to-DP / 1-hr else / DS 5-33 2-hr ESS cutoff / DS 5-28 1-hr non-Li / DS 7-110 1-hr BOC / ¾-hr carrier habit / slab continuity; AXA ≥1-hr + FA dampers (whitepaper pins). Cite **section AND edition** |

---

## 13. Output

A **fire-area compartmentation schedule** (markdown table + edition pins + upstream consumption block + purpose statement + door-ratio show-and-verify + DYNAMIC damper defaults + passive C&E spine + flags + handoffs).

Write **only** to the caller-named path.

### 13.1 Do not emit

- Occupancy classification from scratch
- Density×area `calcs/fp` or demand numbers
- Per-hall sprinkler criteria re-derivation
- Full releasing C&E
- ESS sprinkler / explosion / off-gas design
- Foam or mist design
- MFL wall schedule
- Exterior exposure / WUI envelope design
- Smoke-control engineering / FCC design
- CAD
- Invented PRC 17.10 text

---

## 14. Stop conditions

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

Return the blocking item (hard Stop only for scope-lock / wrong-Skill items; input gaps → stated `ASSUMED`, flagged) when:

1. Missing building/hall inventory.
2. Missing completed `occupancy-hazard-fork` result or its **boundary register**.
3. A boundary needed for an FB row is `unresolved` or omitted.
4. Missing `most-stringent-basis-matrix` compartmentation rows (rating/extent/door/damper), or dual-carrier with one named carrier's compartmentation values missing, or a required row left `unresolved` without FLAG-only treatment.
5. Caller demands a **¾-hr door stamped AHJ-ok on a 2-hr barrier**.
6. Caller asks this Skill to **authorize** single-interlock, non-interlock, **foam**, or **mist**.
7. Caller asks to classify occupancy from scratch, run density×area, design ESS suppression/explosion, design an **MFL wall**, or treat in-hall multizone PA sections as 2-hr fire areas without rated construction.
8. NDA owner treated as numeric rating without structure-only posture.
9. Caller asks to invent **AXA XL PRC 17.10** clauses as if held in corpus.
10. Caller asks to write outside the caller-named path.

---

## 15. Citations (section **and** edition — do not invent)

**FM DS 5-32 January 2026 §2.2.4:** 1-hr walls (DP/network/tape/generator); **2-hr between multiple DP rooms**; ¾-hr doors (carrier habit); slab-to-slab.

**FM DS 5-33 January 2024 §2.3.4:** dedicated Li-ion ESS cutoff room — **minimum 2-hour** fire-rated floors, walls, and ceiling.

**FM DS 5-28 April 2021 §2.2.4:** lead-acid and nickel-cadmium batteries in a **minimum one-hour** fire-rated room — unconditional.

**FM DS 7-110 June 2026 §2.2.5–§2.2.8:** process control room **≥1-hr** separation; redundant trains in separate rated areas; penetration seals equivalent to assembly.

**FM DS 1-22 Interim January 2026 / FM DS 1-42 Interim April 2025:** MFL construct and **4-hr** MFL wall default — **not** this Skill's ordinary 2-hr barrier.

**FM DS 1-20 April 2025 / FM DS 9-19 Interim January 2024:** exterior exposed wall / WUI — route to campus-exterior note.

**AXA XL whitepaper March 2026 p.4 / p.9:** ≥1-hr full-height; ¾-hr doors; slab-to-roof-deck; FA-activated dampers. **PRC 17.10 not in corpus** — do not invent.

**NFPA 75-2024 (when adopted):** ITE-area **≥1-hr** separation [CODE NFPA 75-2020/2024 §6.1.3.2, pull 75-05]; doors **≥45 min** [CODE NFPA 75-2020/2024 §6.1.3.4: ¾-h doors in 1-h construction, 1½-h in 2-h, pull 75-05]; batteries → NFPA 855 / IFC Ch.12.

**IBC-2024:** §706 fire wall / §707 fire barrier / §716 openings / §717 dampers / §714 firestop / §715 joints / §508 mixed occupancy / Ch.5 area (§507 unlimited-area path).

**Correspondence rules:** 1-hr FB → ¾-hr door; 2-hr FB → **1½-hr door**; assembly <3 hr → **1.5-hr** fire damper; DP-hall air path → **UL 555 DYNAMIC** (or combo F/S) unless that AHU truly auto-shuts down.

**Listing / companion:** UL 555 / UL 555S; NFPA 80 / UL 10C; Greenheck life-safety dampers manual (Decent; IBC-2015 lineage — verify cells); ASTM E814 / UL 1479; ASTM E1966 / UL 2079.

### 15.1 Deliberately `[V]`

| Item | Why |
|---|---|
| IBC Tables 716.1(2)/(3), 717.3.2 numeric cells | Rules edition-stable in corpus; licensed cells may be unheld |
| IBC Tables 506.2, 508.4, 707.3.10 | Allowable-area / separated-occupancy / fire-area cells often unlicensed |
| IFC-2024 Table 1207.7 | ESS chemistry/energy cells — do not invent |
| AXA XL PRC 17.10 | Named in corpus as procurement candidate; **not mined** |
| NFPA 75 adoption + some clause pins | Confirm AHJ reference; several pins secondary/`[75-2024 confirmed]` |
| Greenheck → IBC-2024 damper table cells | Source written to IBC-2015; correspondence confirmed independently, cells `[V]` |
| §706 vs §707 when job-unpinned | Do not invent parapets |
| Generator / fuel higher-than-1-hr envelopes | NFPA 30/37 detail often FLAG, not invented here |

---

## 16. Design practice

1. Three-layer, most stringent, **per parameter**. Insurer/owner usually sets wall **rating**; code sets **door/damper** for that wall — and code can win on the door.
2. Per-parameter, not per-layer. FM 2-hr × AXA full-height extent × FA dampers × DYNAMIC listing = **union of axes**, not take all FM or take all AXA.
3. Consume upstream Skills; do not rebuild occupancy classification or the basis matrix.
4. Owner may raise, never lower. NDA is structure.
5. Enforced ≠ latest. Pin adopted I-Code; report Δ vs 2024 model floor when useful. NFPA 13-2025 is directional and **not** the DP-to-DP FRR driver.
6. Show-and-verify the 0.75/2.00 non-conformance and 1.50/2.00 fix.
7. Honesty. Name insurer/owner when the code floor is silent on hall↔hall FRR. Name MFL and exterior as **different packages**.
8. Company fence: wet/dry/DI only elsewhere; SI comparison-only; no foam; mist refused — this Skill elects none of them.

---

## 17. Not this Skill / handoffs

| Work | Where it lives |
|---|---|
| Occupancy / §903 / HC / boundary register | `occupancy-hazard-fork` (consume) |
| Dual-carrier BOD whole matrix | `most-stringent-basis-matrix` (consume compartmentation rows) |
| System-family election (wet/dry/DI) | `suppression-technology-selection` (acknowledge only) |
| Density × area | `density-area-dry-increase` |
| In-hall multizone PA alignment | `multizone-preaction-zone-alignment` |
| Releasing C&E full matrix | `preaction-releasing-c-and-e-soo` |
| Power isolation architecture | `power-isolation-disconnect-control` |
| ESS sprinkler / explosion / off-gas / duration | `ess-isolation-venting-and-duration` / ESS Skills |
| Damper model / sleeve / velocity / EMME listing deep dive | *Fire and smoke damper selection and installation* (+ sibling Skill if present) |
| Firestop UL system-number selection | *Through-penetration firestop system selection and specification* |
| MFL fire wall / space separation | `mfl-limiting-factors-walls-space-separation-and-openings` / DS 1-42; definition DS 1-22 |
| Exterior exposed wall / WUI | `campus-exterior-fire-exposure-separation-and-wall-protection` / DS 1-20 / DS 9-19 |
| NFPA 75 ITE protection beyond wall rating pin | *NFPA 75 ITE room applicability and requirements* (floor only here) |
| Smoke-control engineering / FCC design | not this Skill |
| Foam / mist design | prohibited / `PRACTICE REFUSED` — stop |

---
