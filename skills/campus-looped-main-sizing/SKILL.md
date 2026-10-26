---
name: Campus looped main sizing
description: >-
  use this ideally after density-area-dry-increase has produced company-scoped
  wet/dry/DI `qd_gpm` (if absent, assume and flag ASSUMED) (density-method minimum) and hydrant-supply-curve has
  returned the BOR supply verdict / `P(Q)` (and matrix
  underground/isolation/C/one-leg-out pins are closed when dual-carrier, else
  most-stringent ASSUMED), and
  you must size a dedicated FP campus loop for full demand with one leg out,
  pick diameter/material/actual ID, and place sectional isolation —
  SI/NI/foam/mist refused as BOD; not a sprinkler tree, not hydrant P(Q), not
  listed pump envelope, not occupancy or density×area.
---
# Campus looped-main sizing

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable US data-center fire-protection recipe.

**This Skill owns** sizing a **dedicated fire-protection campus loop** so the loop can **deliver the full demand with one leg out of service**, picking **diameter / material / actual internal diameter**, and placing **sectional isolation**.

It is the **private-main sibling of `hydrant-supply-curve`**. Density-area owns demand (`qd_gpm`). Hydrant-supply-curve owns the **municipal/hydrant 2-point curve** and the pump **need/no-need** verdict. This Skill owns the **loop that delivers `qd` under the worst single valved-segment outage**. Pump-envelope owns the **listed centrifugal screen** (churn / 100% / 150%) **after** hydrant-supply-curve has said a pump is needed — it is not a supply curve and not a loop.

**Downstream water-supply order:** `density-area-dry-increase` → `hydrant-supply-curve` → **`campus-looped-main-sizing`** (when a dedicated campus loop must be sized) → `pump-envelope` (when a pump is indicated). Do not skip hydrant by jumping density → loop friction unless the parent explicitly sequences otherwise **and** supply proof is already closed.

The shop arithmetic kernel `calcs/fp` op **`hw` / `hazen_williams`** is the sanctioned **ONE-SEGMENT** kernel. One-leg-out = **one segment representing the remaining path**, not a network solve. Do **not** expand `hw` into a pipe tree. Do **not** size a sprinkler array. Do **not** run SprinkFDT.

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER LOOP PARAMETER** (pipe C, actual ID, isolation count, one-leg-out demand, test-currency if inherited — each separately). Report the **delta vs NFPA 13-2025** (positional: 13 does not size private mains) **and** the open delta vs **NFPA 24-2025 `[V]`**, plus the **FM DS 3-10 vs AXA one-leg-out delta** when FM controls. Cite **section AND edition**. Show-and-verify math. Mark invented values `[SYN]` / unpinned values `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Consume upstream Skills; do not rebuild them. Enforced ≠ latest. Write **only** to the path the **caller** names.

**Process guardrail:** the governing hydraulic case is **full demand with ONE LEG OUT (N+1 topology)**. Intact-loop split is not the sizing driver and is **not** a `calcs/fp` job. Do **not** freeze `FP-1 = Q @ P`. Do **not** invent `L` on an N.T.S. / schematic site. Do **not** copy a worked package’s synthetic rectangle, lengths, or 12-in / 8-in tags as defaults — copy **METHOD** only. Do **not** silently downsize legs to FM’s no-impairment split on a non-deluge DC campus.

**Negative teaching:** (1) Sizing on steady-state two-path friction and forgetting the single-break remaining path. (2) Treating HDPE as hydraulically equal to the same **nominal** DI — `(6.28/5.42)^4.87 ≈ 2.05×`. (3) Combining fire and domestic/process underground to “save a trench.” (4) Expanding `hw` into a looped-main network model. (5) Silently picking FM §3.1.4.1(4) no-impairment split over AXA full one-leg-out without reporting the delta. (6) A prior campus looped-main worked package is **synthetic**; its ring and tags are **job geometry, not Skill defaults**.

Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may size a **controlling** dedicated FP campus loop only against demand produced for an elected company system family:

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

**This Skill does not elect families.** It handshakes with `suppression-technology-selection`, `most-stringent-basis-matrix`, `density-area-dry-increase`, and `hydrant-supply-curve`. Consume their elected `wet` \| `dry` \| `double-interlock` result.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** demand to size the loop for:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling one-leg-out diameter sized as if SI/NI were company-elected.

SI/NI may appear in a **comparison / delta** column only (e.g., “if SI were allowed, density-area would have sized wet 2,500 → `qd` 750”). Comparison rows are never the controlling loop demand.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Size dedicated loop for consumed `qd` |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; do not control the loop size |
| Foam / foam-water | **Prohibited** | Stop; do not design a foam BOD loop |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design/size |
| Clean agent | Handoff-only | Not this Skill |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |

**Foam is prohibited for company scope.** **Mist is `PRACTICE REFUSED`.** Do **not** size a foam or mist BOD campus loop here. FM flowchart branches that mention mist do not authorize design here.

### 1.3 What this Skill calculates

| In scope | Out of scope |
|---|---|
| Dedicated FP campus loop; one-leg-out remaining-path friction via `calcs/fp` `hw` | Occupancy / HC / OH classification |
| Diameter ladder → nominal + **actual ID** + material/DR + C | System-family election |
| Sectional isolation ≤ controlling unit bite | Density × area re-calc |
| 3-layer union **per loop parameter** (C, ID, isolation, one-leg-out demand) | Hydrant / municipal `P(Q)` / Adequacy verdict |
| Show-and-verify + `[SYN]`/`[V]`/status register | Dual-carrier BOD rebuild |
| Consume `qd` + hydrant BOR verdict / `P(Q)` | Listed churn / 100% / 150% envelope |
| Transparency vs consumed supply cushion | Node-by-node pipe tree / SprinkFDT / network split |
| Name thrust companion; performance thrust pins | Full DIPRA restrained-length catalog |
| | NFF / IFC App-B fire-flow (unless AHJ-pinned as second `hw` Q) |

**FM DS 3-0 scope fence:** analyzes a supply and supplies H-W / Table 3 C. It does **not** size the private main (NFPA 24), the fire pump (NFPA 20), or the tank (NFPA 22).

**FM DS 3-10 scope fence:** installation / arrangement / restraint / hydro / flush / freeze / ITM of private fire service mains. Hydraulics / H-W C → DS 3-0. This Skill consumes DS 3-10 **install/isolation/size pins** and the **loop-leg sizing delta**; it does not dump the full ITM catalog.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent `qd_gpm`, the flow test, one-leg-out length on an N.T.S. drawing, actual ID from a nominal stamp, or a system-family election.

| Input | Required | Rule |
|---|---|---|
| **Completed `density-area-dry-increase` result** | **yes** | Consume `qd_gpm` (and `q_spr` / hose / duration context). Label `qd` a **density-method minimum**. Balanced tree demand is **higher**. Storage / receiving / staging can be the **larger** campus `qd` — consume **storage-staging-sprinkler-design** if that space governs. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `hydrant-supply-curve` result** | **yes** (when asked to close supply vs loop friction) | Consume BOR verdict (Adequate / Inadequate) and `P_supply_BOR(qd)` / `P(Q)` if relocated. **Do not re-plot.** Missing when transparency is required → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `most-stringent-basis-matrix` result** | **yes** (or closed pins inherited) | Consume underground / isolation / C / one-leg-out / test-currency rows, provisional/`[V]` flags, company wet/dry/DI fence, and NFPA 13-2025 / NFPA 24-2025 `[V]` delta rows that touch those parameters. Dual-carrier with **unresolved** underground/isolation/C/one-leg-out rows → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged). Do **not** rebuild the matrix. |
| **Company-elected `system_type`** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from STS / matrix / density / hydrant. SI/NI as BOD → **Stop** (§1.1). |
| Assignment packet | preferred | Consume; do not rebuild. |
| `qd_gpm` | **yes** | Sprinkler + hose at the **BOR**. Prefer density-area (or hydrant-consumed same number). Canonical FM HC-2 white-space minima when so consumed: **wet 750 gpm**, **dry/DI 950 gpm**. Do **not** treat “wet/SI 750” as a company election — SI is comparison-only. |
| **One-leg-out path `length_ft`** | **yes, and known** | Length of the **remaining path** with the largest single valved segment out. If schematic / N.T.S. / RFI-open → **not a Stop**: use a stated `ASSUMED` length (value + why, conservative), flagged; size is ASSUMED-based and not scheduled until confirmed. Status: `unresolved` / `RFI-variance`. |
| Material + joint / class or DR | **yes** | DI (cement-lined + poly wrap default) · PVC AWWA C900 · HDPE AWWA C906 · other named. |
| **Actual internal diameter `d_in`** | **yes** | **Never nominal.** Unknown ID → stated `ASSUMED` actual ID (value + why) / `[SYN]` screening, flagged — never presented as the verified scheduled size. |
| Hazen-Williams **C** | **yes** | **Design C = 100 (shop lock, all underground materials — design-practice setting Use C=100; C = 100 unchanged).** Table 3 C by **material / age** is the **comparison-only** column (FM DS 3-0 Appendix C **Table 3 (p.51)** and friction tables in **FM DS 2-89** *Pipe Friction Loss Tables* **May 1973 / Revised April 2026**, 127 pp (official `.../02-sprinklers/fmds0289.pdf`). DS 2-89 is **not** folded into 3-0 (3-0 Mar 2010 still cites 2-89). Steel C=100 vs C=120 tables live here. Unknown C → 100, never a guessed 120/140. Sprinkler-pipe C from nitrogen Skill is **not** underground C. HDPE C **not** in the Table 3 excerpt → `[V]`; do not invent 150. |
| Unit inventory | **yes** | Count of **FP units** the isolation rule will see: risers, hydrants, FDCs / laterals. |
| Loop vs dead-end geometry | yes | Dead-end would exceed **1500–2000 ft (457–610 m)** → loop (AXA PRC.14.5.0.1 p.2). |
| Controlling **carrier** | yes | Prefer matrix pin. Dual-carrier with differing isolation / one-leg-out / C rows and no closed union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to most-stringent-basis-matrix. On an **FM-insured** campus, **FM DS 3-10 + NFPA 24** govern install/isolation/size pins — still **report** the AXA one-leg-out delta (§6). |
| AHJ-enforced NFPA **24** / **13** editions | yes to cite | Delta baselines **NFPA 24-2025** and **NFPA 13-2025** (positional). Unamended 2024 I-Codes typically pin **24-2022** / **13-2022**. Prefer matrix pins. |
| Future-phase / yard-hydrant Q | no | Only if **pinned**. Do **not** invent 2,000–3,500 gpm. |
| Elevation Δh (ft) | only if known | Flat / unknown → 0. Elevation uses FM DS 3-0 Eq 2 **0.433 psi/ft** — **not** the kernel’s 0.4333. |
| Inline device loss | only if cited | Backflow **≥ 5 psi is a screening trigger, not a value to carry.** Consume **AXA XL PRC.14.5.0.2** *Backflow Prevention For Fire Service Mains* (**2020-01-31**, 10 pp) when AXA controls BFP. |
| Caller **output path** | **yes** for file output | Typically `<name>.calc.json` + short markdown verification. If unnamed, return results in the response and stop (do not invent a path). |

**Kernel formula (do not hand-roll `hw`; ONE SEGMENT):**

```
p_psi = 4.52 * L_ft * Q_gpm**1.85 / (C**1.85 * d_in**4.87)
hf_ft = p_psi / 0.4333
```

Constant **0.4333 psi/ft of water** converts head loss to feet — **do not silently swap 0.433**. `d_in` is **actual internal** diameter.

**Do not run** `hydrant`, `density-area`, `pump-envelope`, or `louver` inside this Skill.

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `density-area-dry-increase` | `qd_gpm` (density-method minimum); hose / duration context; elected wet/dry/DI context | Re-run density × area |
| `hydrant-supply-curve` | BOR verdict / `P(Q)`; supply cushion at `qd` | Re-plot hydrant curve; invent Adequacy |
| `most-stringent-basis-matrix` | Underground / isolation / C / one-leg-out / test-currency rows; provisional/`[V]`; company wet/dry/DI fence; NFPA deltas | Rebuild dual-carrier union; blend AXA full one-leg-out with FM no-impairment split into a silent average |
| `suppression-technology-selection` | Elected wet/dry/DI (handshake); comparison-only / prohibited status | Elect a system family |
| `occupancy-hazard-fork` | Only if hall HC/OH context is still needed and missing from density/hydrant | Re-classify occupancy |
| `fire-area-compartmentation-schedule` | Hall / fire-area id when multi-hall identity is required | Design ratings, doors, dampers |
| `storage-staging-sprinkler-design` | When storage/receiving/staging governs campus `qd` | Invent a larger campus Q |
| the input packet | Packet context when present | Rebuild the packet |
| `pump-envelope` | — | Run listed envelope here; freeze `FP-1 = Q @ P` |

If an upstream result presents SI/NI/foam/mist as BOD → **Stop** (company scope lock — stays hard). If a required upstream result is missing, or marks a controlling underground / isolation / C / one-leg-out / system row `unresolved` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (more stringent candidate; or run the upstream Skill first).

### 2.2 Look up by title

*Private fire service mains, underground & the campus loop*; *Thrust restraint and buried pipe anchorage*; *Water-supply analysis & the supply-vs-demand curve*; *Fire-protection hydraulics methods*; *Design practice*; *Enforced-vs-latest edition resolver*; *Backflow preventers on fire service — selection and pressure loss*; shop `calcs/fp` README / `hw` formulas.

---

## 3. Pin editions (cite section AND edition)

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor (private mains) | NFPA 24 | **NFPA 24-2025** current. **Licensed primary is not in the shop codebook** → every 24 §-pin is **`[verify vs licensed NFPA 24-2025]` / `[V]`**. Unamended **2024 I-Codes** typically enforce **NFPA 24-2022**. Monograph map: underground **Ch.10**; sizing **Ch.13**. |
| Code floor (sprinkler method) | NFPA 13 does **not** size the private main | **NFPA 13-2025** is the **positional** delta baseline. H-W / actual ID / common reference are edition-stable. |
| Insurer (underground overlay) | Controlling private-main sheet | **AXA XL PRC.14.5.0.1** (fully mined, Copyright 2020). **FM DS 3-10, January 2022 (interim revision)** — **mined whole** (59 pp); controlling FM Layer-2 for install / arrangement / isolation / size / restraint / hydro / flush / freeze / ITM. On an FM-insured campus, **FM DS 3-10 + NFPA 24 govern** install pins — still **report** the AXA one-leg-out delta (§6). AXA remains the comparison carrier when FM controls. |
| Insurer (C and H-W) | Underground C + friction | **FM DS 3-0, March 2010**: Eq 15; Appendix C **Table 3 (p.51)**. Currency beyond Mar-2010 → `[V]`. |
| Insurer (demand consumed) | Occupancy sheet that produced `qd` | **FM DS 5-32, January 2026** when that is what density-area used. Do not re-derive. |
| Federal **reference** (not commercial default) | UFC 3-600-01 Change 6 (2021) **§9-3 / §9-4** | Loop ≥50% fire flow on a single break; sectional isolation same duties at §9-3 Valves, PDF p.123. **DoD-project criteria**. |
| Restraint method | DIPRA 7th Ed., May 2016 | **Calculation basis**, never the compliance layer. Companion note by title. |

Inherit pins from `most-stringent-basis-matrix` when present. Always cite **section AND edition**; enforced ≠ latest.

**FM DS 3-0 scope fence:** analyzes a supply and supplies H-W / Table 3 C. It does **not** size the private main (NFPA 24), the fire pump (NFPA 20), or the tank (NFPA 22).

**FM DS 3-10 pins to carry (mined — do not treat as a hole):**

| Pin | Value | Cite |
|---|---|---|
| Min recommended main | **≥ 6 in.**; <6 only if no hydrants + hydraulic proof + main ≥ riser | §2.2.10 |
| Supply-connection velocity | **< 20 ft/s (6.1 m/s)** | §2.2.10.1 |
| Hydrant branch | **min 6 in.** | §2.2.10.3 |
| Divisional-valve isolation | ≈ **6 risers** / valve | §2.2.11.3 |
| Private hydrant pumper outlet | **Do not install** | §2.2.8.1 |
| PE encasement film | **≥ 0.008 in. (0.20 mm)** per AWWA C105/A21.5 | §2.2.14.2 |
| Hydro test (performance / ITM pointer) | **≥ 200 psi × 2 hr**, or **static+50** when static >150 (include pump churn); do not use the fire pump as the test pump | §2.3.1.2 |
| Flush (performance / ITM pointer) | **≥ 10 ft/s** — Table 2.3.2.1: 6″ 880 · 8″ 1560 · 10″ 2440 · 12″ **3500** gpm | Table 2.3.2.1 |

Hydro / flush are **performance / ITM / acceptance pointers** on this Skill — name them; do not dump a full ITM schedule unless the caller asked. Route detailed ITM to `itm-design-for-testability` / commissioning Skills.

---

## 4. Confirm prerequisites, then consume, don’t redo

1. Assignment packet exists when preferred — do not rebuild.
2. **`density-area-dry-increase` completed** — consume `qd_gpm`; label **density-method minimum**. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged.
3. **`hydrant-supply-curve` completed** when transparency vs supply is required — consume BOR verdict / `P(Q)`. Do not re-run `hydrant`.
4. **`most-stringent-basis-matrix` pins closed** for underground / isolation / C / one-leg-out (direct or inherited). Unresolved → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged.
5. Elected system is **wet \| dry \| double-interlock**. SI/NI-as-BOD → **Stop** (§1.1). Foam/mist BOD → **Stop** (§1.2).
6. Dual-carrier isolation / one-leg-out / C conflict without closed matrix union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to most-stringent-basis-matrix.
7. Caller wants a **node-by-node tree**, **SprinkFDT**, or a **looped-main network model** → **Stop**.
8. `L` schematic / N.T.S. / RFI-open → **not a Stop**: stated `ASSUMED` length (value + why), flagged; do not silently invent length. Status: `unresolved` / `RFI-variance`.
9. Unknown **actual ID** presented as the scheduled size → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or explicit `[SYN]` screen that is **not** scheduled).
10. If the caller asks to **freeze `FP-1 = Q @ P`** or run **pump-envelope** inside this Skill → **Stop**.
11. If the caller has not named an output path → return the screen in the response and stop; do not pick a codebook location.

---

## 5. Design practice 3-layer on loop parameters separately

Do **not** MAX whole layers. Union each row; name the controlling layer.

| Parameter | Code floor | Insurer | Owner | What this method does |
|---|---|---|---|---|
| **One-leg-out demand** | UFC §9-3 **reference**: ≥50% fire flow on a single break | **AXA XL PRC.14.5.0.1 p.2: full demand with one leg out** — stricter than UFC 50%. **FM DS 3-10 §3.1.4.1(4):** legs need be sized only for the **portion of flow under no-impairment conditions**; sizing legs for **total** flow is mainly advised when a **deluge** system is present. | May require N+1 / future-phase Q now | **Non-deluge DC default: size for full `qd` with one remaining path.** `Q` in `hw` = consumed `qd_gpm`. On an **FM** job: **report the delta** to the FM engineer — **do not silently downsize** to the no-impairment split. **Deluge / special-hazard yards:** FM total-flow-legs posture applies. |
| **Loop vs tree** | NFPA 24 dead-end / looping: **no body rule** [UNSOURCED in NFPA 24 (practice / AXA / FM)] | AXA: loop when a dead-end would exceed **1500–2000 ft**. FM: looped mains with **divisional valves** (§2.2.11.2). | Campus prototype | Full dedicated FP loop. Combined fire+domestic/process is a **carrier reject** (AXA; still prefer dedicated on FM even though combined-service is in FM scope). |
| **Diameter / actual ID** | NFPA 24 [CODE NFPA 24-2022/2025 §5.2.1.2 (≥6 in. for mains supplying hydrants); 2019 via §5.2.2;  AXA: **4 in. if hydraulically proven, else 6 in.** (p.11). FM: recommend **≥ 6 in.**; velocity **< 20 ft/s**; hydrant laterals **min 6 in.** (§2.2.10). | Ladder (AXA p.2): **6 → 8 → 10 → 12 in.+** then **verify friction on actual ID** | May upsize for phases | Pick from the ladder, then **run `hw` on actual ID**. HDPE: never size on nominal. Take the **stricter** min-size floor when layers differ. |
| **C** | NFPA 13 C-table is **sprinkler pipe**, not this underground row; NFPA 24 has **no C-value table** (Ch. 11 names H-W only) [UNSOURCED in NFPA 24 (FM DS 3-0 / practice)] | **FM DS 3-0 App. C Table 3:** new unlined CI **120**; cement-lined **140**; **PVC 150**; FRP **160**; unlined CI ages. PRC Table 1 uses aged **C = 100** as a **conservative bound** | **Shop lock C = 100** (design-practice setting); may specify C-test at commissioning | **Design `hw` at C = 100** for every material (most stringent; also the aged-main bound). Print the Table 3 C for the actual material as a **comparison-only** run and the delta. HDPE C **not** in the Table 3 excerpt → `[V]`; **do not invent 150** — HDPE runs at 100 like everything else. A higher design C needs a written exception. |
| **Isolation count** | UFC §9-3 p.123: a single break takes **not more than five hydrants or laterals to not more than three buildings**. (M03-010’s “five hydrants AND sprinkler systems” is a **mis-transcription**.) | **AXA XL: ≤ 5 FP units** (riser, hydrant, etc.) between sectional valves (pp.5–6). **FM DS 3-10 §2.2.11.3:** ≈ **6 risers** per divisional valve. | May require per-lateral / per-hall isolation | **Commercial / hyperscale default: AXA ≤5 FP units** (tighter than FM ≈6). Federal job → UFC hydrants/buildings. Take the **tighter** bite for phased live-campus work. |
| **Valve type / setback** | PIV or wall-indicator per AHJ; supervision [CODE NFPA 24-2022/2025 §6.7.2 (supervision methods); §6.7.3 roadway-box gate valves exempt, pull 24-02; NFPA 24 sets no 2½ in. threshold] | AXA: **PIV preferred**; **40 ft (12 m)** from building wall; electronic supervision of **all control valves ≥ 2½ in.** + **weekly** visual; keep valves **out of pits**. FM: PIV or gate+indicator post; non-indicating curb-box limited to hydrant/lead-in; new valves open **counterclockwise** (§2.2.7). | May require OS&Y at sources | Take **PIV + 40 ft** on an AXA/hyperscale overlay. Intervals → **itm-design-for-testability**. |
| **Hydrant type / spacing** (layout / unit count — **not** `P(Q)`) | UFC: two 2½-in + one **4½-in**; ≤1,250 gpm from any single hydrant | AXA: **dry-barrel**; **~250 ft (76 m)**; **2–3 × 2½ in.**; **no pumper/steamer outlet** on **yard** hydrants. FM §2.2.8.1: **do not install** pumper connections on **private** hydrants. | Fleet standard | Use spacing to **count units between sectional valves**. Do **not** run hydrant `P(Q)` here. |
| **Restraint / anchorage** | NFPA 24 [CODE NFPA 24-2019/2022/2025 §10.6 (thrust blocks §10.6.1, restrained joints §10.6.2) | AXA: thrust = **50 psi above hydrostatic, min 250 psi**; soil bearing **1,000 lb/ft²** (DIPRA Soft Clay default); no **setscrew retainer glands** near buildings. FM: thrust blocks preferred; Table 2.2.16.5 @ **225 psi / 2000 lb/ft²**; PE film **≥ 0.008 in.** | May require restrained joints campus-wide | **Name** *Thrust restraint and buried pipe anchorage*. Performance spec only — do not dump DIPRA. |

**★★ Loop-leg sizing delta (always print when FM is in play):**

| Layer | One-leg-out / single-break posture |
|---|---|
| **AXA XL PRC.14.5.0.1** | Size loop to meet **full demand** with one leg out |
| **UFC 3-600-01 §9-3** | Loop for **≥ 50%** of required Fire Flow on a single break |
| **FM DS 3-10 §3.1.4.1(4)** | Legs sized for **no-impairment split**; total-flow legs mainly for **deluge** |

**⇒ Design practice for hyperscale DC (non-deluge halls):** keep the **AXA one-leg-out full-demand** rule as the design driver. On an FM-insured job, **surface the delta to the FM engineer** — do not silently downsize legs to the no-impairment split. Deluge / special-hazard yards: FM itself pushes toward total-flow legs.

**Key deltas vs code:** vs NFPA **13-2025** is **positional** (13 does not size private mains; **24 is the floor**). vs NFPA **24-2025 `[V]`**: licensed primary absent — directional until the book is in hand. Isolation: AXA **≤5 FP units** (tighter) vs FM ≈**6 risers** vs UFC hydrants-or-buildings.

---

## 6. Topology — loop, dedicated, one remaining path

1. **Loop, not a tree.** Water to any BOR from two directions.
2. **Dedicated FP underground.** Do not combine with domestic/process/cooling water.
3. **Governing outage case:** largest single **valved segment** out. A two-path loop with one break **converts a parallel-flow problem into a longer one-path problem**. That remaining path is the `hw` segment.
4. **Size for future phases now** if the caller has a pinned ultimate Q. Do not invent the ultimate Q.

**Intact-loop split is not this Skill’s kernel.** Hydraulics-methods Eq 21 and AXA PRC.14.1.2.3 common-point balancing require a **network**. Caller asks for that → **Stop**. Status: `handoff` / `unresolved` (network not in `calcs/fp hw`).

---

## 7. Diameter ladder, then actual ID (including the HDPE trap)

Start from the AXA ladder (6→8→10→12 in.), honor FM **≥ 6 in.** / velocity **< 20 ft/s** when FM controls, then **prove friction on actual ID** at **one-leg-out `qd`**.

**PRC Table 1 friction (method-check anchors, not job losses):** 1500 gpm, 1000 ft, **C=100 iron** — 6 in. **110 psi** · 8 in. **27 psi** · 10 in. **9.5 psi** · 12 in. **3.8 psi** · 14 in. **1.8 psi**. METHOD: first reproduce Table 1 with `hw` using Table 1’s diameter convention (nominal) to prove the kernel matches the sheet, then **abandon nominal** for the design run.

**HDPE ID trap — show-and-verify from the loop note. Do not invent IDs.** HDPE is **OD-controlled**; wall grows inward.

| 6-in. pipe | Wall | ID | Friction vs DI, `(d_DI/d)^4.87` |
|---|---|---|---|
| DI, cement-lined | 0.25 in. + lining | **≈ 6.28 in.** | **1.00 ×** |
| **HDPE DR11** (PE4710, 160 psi @ 73 °F) | 0.602 in. | **5.42 in.** | **≈ 2.05 ×** |
| HDPE ≈ DR7 | 0.946 in. | **4.73 in.** | **≈ 3.96 ×** |

```
(6.28 / 5.42)^4.87 ≈ 2.05
```

**Ductile-iron cement-lined actual IDs (U.S. Pipe *Inside Diameter Charts* UNL/CL/DCL, Rev 08/2022 — ; lightest class).** Use the CL ID of the **specified class** for `hw` friction **and** for fill / flush / leakage-test gallons; submittal IDs govern.

| Nominal | CL ID (in.) | gal/ft = 0.0408·ID² |
|---|---|---|
| 4 in. | 4.18 | — |
| 6 in. | 6.28 | 1.609 |
| 8 in. | 8.43 | 2.899 |
| 10 in. | 10.46 | 4.464 |
| 12 in. (Class 350) | 12.52 | 6.395 |
| 14 in. | 14.55 | — |
| 16 in. (Class 250) | 16.61 | 11.256 |
| 24 in. (Class 200) | 24.95 | — |

Heavier special class called (e.g. Class 52 → 12 in. CL **12.34**) → take that row. A nominal-bore takeoff (12 in. → 5.875 gal/ft) **understates volume ~9%** (3,000 ft 12 in. CL loop = 19,186 gal, not 17,626); 12 in. CL vs nominal friction factor **0.813** at fixed C.

**Bury depth (frost) — state + local layer, deepest governs; name it, do not size it here.** Fire mains below frost and **≥ 6 in. deeper than municipal mains** (FM DS 3-10; the 6 in. below municipal mains rule is [UNSOURCED in NFPA 24, FM only]; NFPA 24 floor is 12 in. below frost [CODE NFPA 24-2019/2022/2025 §10.4.2.1.1]. Example, Minnesota: take the deepest of the state footing-frost depth plus 6 in. (Minn. R. 1303.1600; Zone II at 3.5 ft means at least 4.0 ft), the local utility main bury plus 6 in. (not held), and any local service-pipe rule (one city requires 7 ft on the city-connected service segment). Do not port a 42 in. frost depth from another state into Minnesota. Unknown local rule → `ASSUMED`, flagged.

**Design rule:** never size HDPE on its nominal designation. Upsize ≥ one nominal size **or** run `hw` on actual ID from the specified DR. HDPE **deletes thrust blocks** (butt-fusion fully restrained) and **pays in diameter**.

**PVC C900** is the opposite joint trap: push-on, **not** restrained unless blocks/kits. FM: **do not use PVC** where aromatic hydrocarbons may spill; plastic must be **FM Approved** when FM controls.

**Transition:** plastic → metal **before the building footprint**.

---

## 8. Run `calcs/fp/run.py` — `hw` is source of truth (one segment)

Paste **stdout**. QA re-runs the **same JSON**. Transcript ends with `TRANSCRIPT_OK`.

```
python3 calcs/fp/run.py path/to/name.calc.json
```

```json
{
  "job": "<caller job id>",
  "notes": "one-leg-out remaining path; one hw segment; actual ID; not a tree; not hydrant P(Q); not pump envelope",
  "steps": [
    {
      "id": "one_leg_out",
      "op": "hw",
      "q": "<consumed qd_gpm>",
      "c": "100 (shop lock; Table 3 C = comparison run only)",
      "id": "<actual internal in.>",
      "length": "<remaining-path ft>"
    }
  ]
}
```

The README contract-demo numbers **`q=900, c=100, id=6.065, length=200`** are **kernel contract-demo values, not job defaults**. `6.065 in.` is Sch. 40 **steel**, not a campus main.

**Ad-hoc:** `python3 calcs/fp/run.py hw --q 900 --c 100 --id 6.065 --length 200`

Stdout keys: `p_psi`, `hf_ft`, `psi_per_ft_water`. If stdout disagrees with a hand product, **the kernel wins**. Re-check **nominal vs actual ID**, C from the wrong table, Q missing hose, L = intact perimeter instead of remaining path.

A diameter **ladder** is multiple **one-segment** steps, not a network. Optional extra steps: PRC Table 1 method-check; HDPE vs DI at 6.28 vs 5.42; a **lateral** from loop tap to one BOR if that length and actual ID are known. **Omit** any step whose L/ID is unknown.

---

## 9. Show-and-verify

Use **job** Q, L, C, actual ID — not the README 900 / 200 / 6.065 as if they were the campus.

```
p_psi = 4.52 · L_ft · Q_gpm^1.85 / (C^1.85 · d_in^4.87)
hf_ft = p_psi / 0.4333
```

**HDPE trap:** `(6.28 / 5.42)^4.87 ≈ 2.05`. At equal Q, L, and C, `hw` on 5.42 in. vs 6.28 in. must show ~2.05× `p_psi`.

**Standing exponent rule:** pressure is a terrible way to buy pipe size (`D ∝ f^(−1/4.87)`; doubling friction allowance only **−13.3%** on D). When one-leg-out `p_psi` eats the consumed BOR supply, **the first move is a pipe size (or actual ID / material), not a bigger pump.**

Monograph illustration (**not defaults**): two 12-in. DI legs ≈1,500 ft; one valved segment out → ≈3,000 ft one-path; Q=950 gpm; the monograph's C (comparison-only, not the shop C) gives `pf ≈ 3.5 psi` — at shop **C = 100** that is ×(120/100)^1.852 ≈ 1.40 → **≈ 4.9 psi** (nominal bore; re-run on the CL ID). That is **why** a DC campus loop often lands at 12-in.+. **Not a job L, Q, or diameter.**

---

## 10. Sectional isolation — take the tighter bite

Place **sectional control valves** so that a single break or a phased tie-in drops **≤ the controlling unit count** and **never the whole campus**.

**Pin (commercial / AXA / hyperscale default):** **≤ 5 FP units** between sectional valves; valves **both sides of every supply connection** and at **every major loop intersection** (PRC.14.5.0.1 pp.5–6). **Tighter than FM ≈6 risers** — default here.

**Pin (FM, when FM controls install):** divisional valves on loops; ≈ **6 risers** per divisional valve (DS 3-10 §2.2.11.3). Still **report** AXA ≤5 and take the tighter bite for phased live-campus work unless the closed matrix / FM engineer accepts ≈6.

**Pin (federal, if UFC is the basis):** UFC 3-600-01 Change 6 **§9-3 Valves, PDF p.123**, same duties: *“not more than a combined total of five hydrants or the Service Laterals to not more than three separate buildings are out of service due to a single break.”*

Also: PIV setback **40 ft**; electronic supervision of **all control valves ≥ 2½ in.** + **weekly** visual; keep valves **out of pits**; **FDC** single whole-system (or several whole-system at public-water connections on a large campus); **never** multiple part-system FDCs; FM/AXA **no pumper/steamer on private/yard hydrants**.

**Every sectional valve is a latent dead end** when closed — a **thrust** fact. Point at the companion note.

---

## 11. Thrust / anchorage — name the companion; do not dump the catalog

Companion: *Thrust restraint and buried pipe anchorage*.

Performance spec on this Skill: restrain or block every direction change and every dead end; thrust **design pressure** = **hydrostatic test**, not working pressure (AXA *50 psi above hydrostatic, min 250 psi*; FM Table 2.2.16.5 basis **225 psi / 2000 lb/ft²** when FM controls — report which layer); default buried material **DI + PE encasement per ANSI/AWWA C105/A21.5** (FM film **≥ 0.008 in.**) unless DIPRA 10-point soil score **< 10**; **no setscrew retainer glands** near buildings / pump houses or in corrosive soil; **HDPE fusion deletes the thrust calculation** and pays in ID; **PVC C900 does not**; AXA soil bearing **1,000 lb/ft²** = DIPRA Soft Clay — **buy the soil test**.

Do **not** emit a full restrained-length schedule unless the caller asked for restraint calcs. **Linearity warning:** restrained length is **linear in design pressure**; pump oversizing buys trench joints. Do not pick `pr_psi` here.

---

## 12. Loop transparency vs the consumed BOR supply

```
P_far_BOR_one_leg_out(qd) ≈ P_near − p_hw_remaining_path(qd) − PE_signed − P_device[V]
PE_signed = 0.433 psi/ft × Δh # DS 3-0 Eq 2
```

If one-leg-out `p_hw` **eats** the consumed supply cushion → **upsize** (actual ID / ladder / material), or hand back to hydrant-supply-curve / pump-envelope with a **stated remaining-path loss**. Status: `handoff`. Do not silently freeze a pump nameplate to buy the friction.

If the hydrant verdict was **Inadequate on flow**, AXA’s “sometimes just larger undersized underground” is **this** Skill — still one-segment `hw`. If **pump needed (pressure)** → pump-envelope next; this Skill still reports the **UG remaining-path `p_psi`** as an input, not a rated `pr`.

**Needed fire flow / IFC Appendix B / ISO hydrant credit:** not this Skill. If the AHJ has **pinned** a fire-flow number, it may be a second `hw` Q. If unpinned, do not invent 2,000–3,500 gpm.

---

## 13. Status register and flags

| Status | Use |
|---|---|
| `grounded` | Method pinned to mined sheet + edition (AXA one-leg-out; FM DS 3-10 install pins; H-W 4.52/1.85/4.87; HDPE 2.05×; ≤5 FP units). |
| `provisional` | Screening with stated assumptions (e.g. `[SYN]` ID screen that is **not** scheduled; open non-gating RFI). |
| `unresolved` | Blocking hole: missing `L`, missing actual ID, missing `qd`, missing hydrant verdict when required, unresolved matrix underground row. |
| `comparison-only` | SI/NI density path, FM preference ranking, UFC 50% vs AXA full demand shown as delta — never controlling BOD size. |
| `handoff` | Work owned elsewhere: pump-envelope after need; hydrant re-proof; thrust catalog; network balance; ITM detail; storage-staging if that `qd` governs. |
| `RFI-variance` | Company-fence gate (SI/NI/foam/mist as BOD); schematic/N.T.S. geometry; dual-carrier unresolved without matrix. |

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented `qd`, invented L, invented actual ID / DR, invented NFF, copied worked-package ring as if site-measured, invented HDPE C, any `FP-1 = Q @ P`, any network split presented as kernel output. |
| **`[V]`** | NFPA 24 items outside pulls 24-01/24-04 (Ch.10 beyond §10.4.2/§10.6/§10.8/§10.10.2.1; hydro/leakage still KB-only). Flushing now held: underground flushed completely before connecting downstream; min rate per Table 10.10.2.1.3 (10 ft/s; e.g. 12 in. = 3,520 gpm) [CODE NFPA 24-2019/2022/2025 §10.10.2.1.1, §10.10.2.1.3, pull 24-04]; pump suction flushing per NFPA 20 (pull 20-24); FM DS 3-0 March 2010 currency; HDPE C vs Table 3; AXA PRC.14.1.2.3 primary; AXA vs UFC hydrant outlets. |

**Grounded method numbers (cite sheet AND edition):** H-W 4.52 / 1.85 / 4.87; kernel 0.4333 vs Eq 2 0.433; AXA one-leg-out **full demand**; FM §3.1.4.1(4) no-impairment split (delta); ladder 6→12; Table 1 110/27/9.5/3.8; ≤5 FP units (AXA) / ≈6 risers (FM); PIV 40 ft; HDPE `(6.28/5.42)^4.87 ≈ 2.05`; FM velocity <20 ft/s; FM no private pumper; PE ≥0.008 in.

---

## 14. Output

Write **only** to the caller-named path (typically `.calc.json` + markdown verification).

Must contain: pinned editions (incl. **FM DS 3-10 Jan 2022 interim** when FM/AXA in play); consumed `qd_gpm` labeled density-method minimum + hydrant BOR verdict; inherited `system_type` wet|dry|DI; 3-layer table for **C, actual ID, isolation count, one-leg-out demand, test-currency**; **loop-leg delta** (AXA full / UFC 50% / FM no-impairment) printed; topology (dedicated loop; remaining-path L from a **scaled** source); diameter ladder → scheduled **nominal + actual ID + material/DR + C**; HDPE trap if HDPE is in play; kernel command + **full stdout**; independent H-W algebra; sectional-valve placement vs **controlling** isolation bite (default AXA ≤5); thrust companion named; transparency vs consumed `P_supply(qd)`; Δ vs 13-2025 (positional) **and** 24-2025 `[V]`; status register + `[SYN]`/`[V]` list; hand-offs.

Do **not** emit occupancy schedule, density×area re-calc, hydrant `P(Q)` table, listed pump envelope, `FP-1 = Q @ P`, a pipe tree, a network split, SprinkFDT, or a full DIPRA catalog.

---

## 15. Hand-offs (do not continue here)

- Occupancy / HC / OH → `occupancy-hazard-fork`
- System-family election → `suppression-technology-selection`
- Dual-carrier BOD / unresolved underground rows → `most-stringent-basis-matrix`
- Density × area `qd` → `density-area-dry-increase` (already consumed)
- Storage N@P / Table 14 hose that may govern campus `qd` → `storage-staging-sprinkler-design`
- Hydrant / municipal `P(Q)`, pump need/no-need → `hydrant-supply-curve` (already consumed for verdict)
- Listed pump envelope after **pump needed** → `pump-envelope` (hand remaining-path `p_psi` as UG loss input — not a rated `pr`)
- Node-by-node tree / SprinkFDT → hydraulic-tree Skill (not written) — **STOP**
- Looped-main **network** model / PRC.14.1.2.3 common-point balance → **STOP** — not `calcs/fp hw`
- Thrust-block / restrained-length catalog → *Thrust restraint and buried pipe anchorage*
- Hydro / flush / valve-exercise ITM detail → `itm-design-for-testability` / commissioning Skills
- NFF / IFC App-B → needed-fire-flow note (not this Skill) unless AHJ-pinned

---

## 16. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

- Missing **`qd_gpm`**. Missing hydrant **BOR verdict** when asked to close supply vs loop friction.
- **SI/NI as BOD**, **foam** BOD, or **mist** design request (§1).
- Unresolved matrix underground / isolation / C / one-leg-out rows (dual-carrier).
- **Inventing `L`** on schematic / N.T.S. Inventing **actual ID** from a nominal stamp (except an explicit `[SYN]` screen that is **not** scheduled).
- **Expanding `hw` into a pipe tree**, **sizing a sprinkler array**, **SprinkFDT**, or a **looped-main network model**.
- **Freezing `FP-1 = Q @ P`** or running **pump-envelope** inside this Skill.
- Copying worked-package **synthetic** ring/tags as Skill defaults.
- Filling **licensed NFPA 24-2025** holes with invented §§. (FM DS 3-10 is **mined** — cite it; do not invent beyond mined pins.)
- Silently **downsizing** to FM no-impairment split on a non-deluge DC without reporting the AXA delta.
- Combining fire + domestic/process underground as if that were an equivalent loop.
- Caller asks to write outside the caller-named path.

---

## 17. Citations (section AND edition)

**Private fire service mains, underground & the campus loop:** AXA XL **PRC.14.5.0.1** (Copyright 2020) — one-leg-out **p.2**; dead-end **1500–2000 ft p.2**; diameter ladder **p.2**; Table 1 **p.3**; PIV 40 ft / sectional **≤5 FP units** / supervision ≥2½ in. **pp.5–6**; dry-barrel ~250 ft, **no yard steamer** **pp.6–7**; thrust 50 psi above hydrostatic **min 250 psi**, soil **1,000 lb/ft² p.10**; min main **4 in. if proven else 6 in. p.11**. **FM DS 3-10, January 2022 (interim)** — §2.2.8.1 no private pumper; §2.2.10 min ≥6 in. / velocity <20 ft/s / hydrant branch min 6 in.; §2.2.11.2–3 divisional valves / ≈6 risers; §2.2.14.2 PE ≥0.008 in.; §3.1.4.1(4) loop-leg no-impairment split; §2.3.1.2 hydro; Table 2.3.2.1 flush. NFPA **24-2025** named; §§ **`[verify vs licensed NFPA 24-2025]`**; map **Ch.10**; main size [CODE NFPA 24-2022/2025 §5.2.1.2; 2019 via §5.2.2;  HDPE IDs **6.28 / 5.42 / 4.73** and `(6.28/5.42)^4.87 ≈ 2.05`. UFC **3-600-01 Change 6 (2021) §9-3 / §9-4**; isolation same duties **§9-3 Valves, PDF p.123**.

**Thrust restraint and buried pipe anchorage:** DIPRA 7th Ed., May 2016; FM DS 3-10 thrust Table 2.2.16.5 / PE film when FM controls. **Delta vs NFPA 13-2025: none — 13 does not reach the private fire main.**

**Water-supply analysis:** FM DS 3-0 March 2010 Eq 15 / Eq 2 **0.433 psi/ft** / App. C **Table 3 p.51**.

**Fire-protection hydraulics methods:** DS 3-0 Eq 15; **d = actual internal**; Eq 21 loop split (**do not run as this Skill’s kernel**).

**Ductile-iron IDs:** U.S. Pipe *Inside Diameter Charts* UNL/CL/DCL **Rev 08/2022** . **Frost bury (MN):** Minn. R. 1303.1600 (2019 rules); City of Becker Code §51.04 .

**Absent / holes to name, not fill:** licensed **NFPA 24-2025** primary; local utility main-bury standards (MN); AXA **PRC.14.1.2.3** primary (common-point balancing); HDPE C in Table 3; FM DS 3-0 currency beyond March 2010.

---

## 18. Design practice

1. Three-layer, most stringent, on **pipe C, actual ID, isolation count, one-leg-out demand, and inherited test-currency separately**. Non-deluge DC: **full demand with one remaining path** — not UFC 50%, not silent FM no-impairment split — unless the closed matrix / FM engineer / federal basis says otherwise and the delta is printed.
2. Delta vs **NFPA 13-2025 is positional** (13 does not size private mains; 24 is the floor) plus the **open `[V]` delta vs NFPA 24-2025**, plus the **AXA vs FM vs UFC one-leg-out delta**. Do not fabricate 24 section numbers.
3. Show-and-verify. Kernel stdout + independent H-W algebra + HDPE `(6.28/5.42)^4.87 ≈ 2.05`. Kernel wins on arithmetic.
4. Honesty on geometry and nameplates. No invented L. No copied synthetic ring. No `FP-1 = Q @ P`. One segment, not a network.
5. Company fence: wet/dry/DI only; SI/NI comparison-only; foam prohibited; mist `PRACTICE REFUSED`. Status vocabulary complete.
6. Write only to the **caller-named** path.

---

## 19. Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH | occupancy-hazard-fork |
| System-family election | suppression-technology-selection |
| Density × area `qd` / gallons | density-area-dry-increase |
| Storage N@P / Table 14 hose that may govern campus `qd` | storage-staging-sprinkler-design |
| Dual-carrier BOD | most-stringent-basis-matrix |
| Hydrant / municipal `P(Q)`, pump need/no-need | hydrant-supply-curve |
| Listed pump envelope | pump-envelope |
| Node-by-node tree / SprinkFDT | hydraulic-tree Skill (not written) |
| Looped-main **network** model | **STOP** — not `calcs/fp hw` |
| Thrust-block / restrained-length catalog | *Thrust restraint and buried pipe anchorage* |
| Hydro / flush / valve ITM schedule | itm-design-for-testability / commissioning |

---
