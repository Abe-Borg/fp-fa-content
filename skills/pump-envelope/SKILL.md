---
name: Pump envelope
description: >-
  use this ideally after hydrant-supply-curve has returned a pump-needed
  verdict (or the parent cites already-closed supply proof), density-area has
  produced company-scoped wet/dry/DI `qd_gpm`, and matrix pump rows are closed
  (any absent input is assumed and flagged ASSUMED, not a stop), and you
  must screen a listed centrifugal envelope (rated / churn / 150%) through
  `_calc` without freezing `FP-1 = Q @ P` while gating RFIs or BOR pressure are
  open, plus the driver block as cited pins (diesel fuel-tank hours, NEC 695
  OCPD, jockey sizing/setpoints, seal, VS relief, VT vs HSC) — SI/NI/foam/mist
  refused as BOD; not occupancy, density×area, hydrant curve rebuild,
  dual-carrier BOD, looped-main, VSPLC sizing, combustion-air louvers, or CAD.
---
# Pump envelope

> **Intake rule (the engineer, 2026-10-07 — overrides any older gate wording below):** The assignment packet is optional and never a gate. Start from exactly what is given. A missing packet, a missing upstream result (STS token, matrix row, occupancy fork, density, C&E, etc.), or a missing input blank is **not** a Stop: run the upstream Skill if practical, otherwise fill the gap with a stated **ASSUMED** value (the value used + why), flag it in the output and the status register, and continue. ASSUMED is not verified. "Never invent" / "refuse invent" rules on project numbers mean do not *silently* invent: label the number ASSUMED; never present an ASSUMED value as a cited code or table value; never freeze a vendor SKU. **Company scope locks stay hard Stops and are not softened by this rule:** wet / dry / double-interlock preaction only; foam prohibited; clean agent not done (hand-away); water mist `PRACTICE REFUSED`; single-interlock / non-interlock / other preaction never the elected system (SI/NI-as-BOD → Stop + `RFI-variance`, comparison-only). Cite section and edition, use `calcs/fp/run.py` for governed math, design to the most-stringent 3-layer basis; the engineer is the engineer of record.

Reusable US data-center fire-protection recipe.

**This Skill owns** the **listed centrifugal envelope screen** (rated / churn / 150%) against a company-scoped demand, through the shop `_calc` `pump_envelope` op. It screens a candidate (`qr_gpm`, `pr_psi` as **inputs**) and reports whether that candidate sits inside the controlling flow-cap / churn / 150% / ceiling envelope. It also emits the **driver block** (§7A): diesel fuel-tank sizing basis, electric OCPD / GFPE / acceptance-amp pins, jockey capacity + setpoint window, seal election, VS relief, and VT vs HSC — as **cited pins**, not kernel outputs and not a nameplate.

It sits **after `hydrant-supply-curve`**. Density-area owns demand (`q_spr` + hose + duration gallons). Hydrant owns the **supply curve** and the **pump need / no-need verdict**. This Skill owns the **listed envelope** **only after** hydrant (or a parent-cited closed supply proof) has said a pump is needed — it is explicitly **not** a supply curve and **not** a nameplate mint.

**Downstream water-supply order:** `density-area-dry-increase` → `hydrant-supply-curve` → **`pump-envelope`** (when a pump is indicated). Do **not** skip hydrant by jumping density-area → this Skill unless the parent explicitly sequences otherwise **and** cites already-closed supply proof.

The shop arithmetic kernel is the source of truth, not a hand spreadsheet and **not a manufacturer shop curve**.

**the engineer Way:** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PUMP PARAMETER** (listed flow / flow-cap, churn, 150% pressure floor, component ceiling, N+1, driver — each separately). Report the **delta vs NFPA 13-2025** (demand context) **and vs NFPA 20-2025** (pump floor). Cite **section AND edition**. Show-and-verify math. Mark invented values `[SYN]` / unpinned values `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Consume upstream Skills; do not rebuild them. Generic — do not copy a prototype hall onto another job.

**Process guardrail (load-bearing):** `pr_psi` is an **envelope input, not a scheduled rating.** Do **not** write `FP-1 = Q @ P` while BOR demand is open or gating RFIs are open. Recipe: run the envelope, paste stdout, keep `pr_psi` as an input, print `provisional [RFI-…]`. Honest prose does not save a frozen schedule.

**Negative teaching:** (1) The MS campus fire-pump-selection worked package (`corpus-insufficient`) froze a **synthetic rated pressure (100 psi)** into the equipment schedule — failure mode this Skill exists to prevent. (2) the campus Mesa FP-1 first-pass QA (`needs-rework`) scheduled **750 gpm @ 40 psi net** while gating RFIs were open. Shop codebook process note (by title): *Do not schedule rated pump gpm/psi on open gating RFIs*.

Write output **only** to the path the **caller** names. Do not write into `KNOWLEDGE_BASE`, `EXERCISES`, `_pruner`, `_surveyor`, `_engineer`, or `ARCHIVE`. Look up shop codebook notes **by title**.

---

### 1.0 Country/edition gate at intake (model A — stop-vocab normalize 2026-11-04, staged)
Pin country + enforced edition first (enforced ≠ latest). Missing pin → `ASSUMED` (value + why) + flag, continue per intake rule; scope locks (§1.1 family fence, foam prohibited, clean agent hand-away, mist `PRACTICE REFUSED`, SI/NI comparison-only) stay hard.
- **US** → AHJ-adopted IFC/IBC + NFPA editions as used in this Skill; NFPA 13-2025 (and NFPA 20-2025 / 14-2024 where used) only as delta when not enforced.
- **Canada (BC/AB/ON)** → pin via `most-stringent-basis-matrix` §4.2b; NFPA 20 per that code's Table 1.3.1.2 (2016 BC/AB/ON-OBC; 2019 NBC 2025 model) — see Canada diesel section. Never cite US IFC/IBC §§ or US NFPA editions as the Canadian code floor.
- **NEG-CA (stop-class mis-cites):** never invent ULC hours, CSA B139 text, OBC/NBC/BCFC bodies, or unheld Canadian pins. Unheld → `NEEDS HOLD` / `unresolved` + RFI (do not invent; do not Stop the whole run).

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may screen a **controlling** listed envelope only against demand produced for an elected company system family:

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

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** demand to screen:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling envelope screen sized as if SI/NI were company-elected.

SI/NI may appear in a **comparison / delta** column only (e.g., “if SI were allowed, density-area would have sized wet 2,500 → `qd` 750”). Comparison rows are never the controlling envelope demand.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Screen listed envelope vs consumed `qd` |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; do not control the screen |
| Foam / foam-water | **Prohibited** | Stop; do not design or screen a foam BOD pump |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design/screen |
| Clean agent | Handoff-only | Not this Skill |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |

**Foam is prohibited for company scope.** **Mist is `PRACTICE REFUSED`.** Do **not** screen a foam or mist BOD pump envelope here. FM flowchart branches that mention mist do not authorize design here.

### 1.3 What this Skill calculates

| In scope | Out of scope |
|---|---|
| Listed centrifugal envelope (churn / 100% / 150%) via `_calc` | Occupancy / HC / OH classification |
| Candidate `qr` / `pr` **screening** (inputs, not nameplate) | System-family election |
| Flow-cap / churn / ceiling boolean harvest | Density × area re-calc |
| 3-layer union **per pump parameter** | Hydrant / municipal supply curve / Adequacy verdict |
| Show-and-verify + `[SYN]`/`[V]`/status register | Dual-carrier BOD rebuild |
| Consume `qd` + suction/static from hydrant handoff | Looped-main / NFF / App-B fire-flow |
| N+1 / driver **flags** (not kernel keys) | Node-by-node pipe tree / Ch.28 schedule |
| **Driver block (§7A):** diesel fuel-tank hours, NEC 695 OCPD rule, jockey capacity / setpoints, seal, VS relief, VT vs HSC — pins, not kernel | Breaker coordination study / feeder voltage drop / GFPE-service collision memo (*Fire-pump circuit power integrity* note) |
| | VSPLC sizing / combustion-air louvers / CAD / shop curve |

**FM DS 3-7 scope fence:** §1.0 explicitly **excludes** water-supply capacity and pressure requirements. DS 3-7 sizes the **installation** (count, driver mix, usable fraction of the curve, room). Occupancy demand is **DS 5-32 / DS 3-26 / DS 8-9 + DS 2-0**. Do not ask this Skill (or DS 3-7) “how many gpm at what psi?” as a scheduled nameplate.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent `qd_gpm`. Do **not** invent `pr_psi` from a shop curve or from the AXA XL “standard pressure” list. Do **not** invent a nameplate. Do **not** invent a system-family election. Do **not** invent suction/static when hydrant has not handed them off.

| Input | Required | Rule |
|---|---|---|
| **Completed `hydrant-supply-curve` result** | **yes** (or parent-cited closed supply proof) | Must show **pump needed** (Inadequate on pressure, or equivalent parent-cited closed proof). Consume `qd_gpm` and **suction/static from that hydrant result only**. Verdict **Adequate / no-pump** → **Stop** for code/insurer envelope (§4). Missing need verdict and no closed proof → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Density-area alone is **not** permission to size a pump. |
| **Completed `density-area-dry-increase` result** | **yes** (usually inherited via hydrant) | Consume `qd_gpm` (and `q_spr` / hose / duration context). Label `qd` a **density-method minimum**. Balanced tree demand is **higher**. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `most-stringent-basis-matrix` result** | **yes** (or closed pins inherited) | Consume **pump-parameter** rows (flow cap, listed flow, churn preference, 150% floor, ceiling, N+1, driver), provisional/`[V]` flags, company wet/dry/DI fence, and NFPA 13-2025 / NFPA 20-2025 delta rows that touch those parameters. Dual-carrier with **unresolved** pump rows → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged). Do **not** rebuild the matrix. |
| **Company-elected `system_type`** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from STS / matrix / density / hydrant. SI/NI as BOD → **Stop** (§1.1). |
| Assignment packet | preferred | Consume; do not rebuild. |
| `qd_gpm` | **yes** | Sprinkler + hose at the **BOR**. Prefer hydrant-consumed value (same number density-area produced). Canonical FM HC-2 white-space minima when so consumed: **wet 750 gpm**, **dry/DI 950 gpm**. Do **not** treat “wet/SI 750” as a company election — SI is comparison-only. |
| `qr_gpm` | **yes** | Candidate **rated flow** being screened (not yet a scheduled nameplate). |
| `pr_psi` | **yes** | Candidate **rated net** being screened. **Envelope input, not a listed rating.** Stays an input until BOR demand is closed. |
| `suction_static_psi` | **yes** | Max static suction for **system churn** = churn net + suction. **Prefer hydrant handoff** (relocated BOR suction / static from that curve). Not a substitute for re-running the hydrant op. |
| `churn_frac` | no | Default **1.20** (preferred shutoff). Override from matrix / controlling sheet. |
| `churn_frac_max` | no | Default **1.40** (code-floor max shutoff). |
| `fm_flow_cap` | no | Kernel default **1.40** (FM **single** 100%-Qmax centrifugal). Override from the 3-layer union (AXA **1.20**; FM **multiple 1.10**). |
| `nfpa_flow_cap` | no | Kernel default **1.50**. |
| `p150_frac` | no | Kernel default **0.65** (150% flow at ≥65% rated net). |
| `ceiling_psi` | no | Default **175** (typical sprinkler-component working-pressure class). |
| Gating-RFI status | **yes** | `open` (list ids) or `closed`. **Open → print envelope + `provisional [RFI-…]`; do not write `FP-1 = Q @ P`.** |
| Controlling **carrier** | yes | `FM` \| `AXA XL` \| other named sheet. Prefer matrix pin. Dual-carrier with differing pump parameters and no closed union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to most-stringent-basis-matrix. |
| Owner N+1 / driver-mix posture | yes (may be “none”) | **Flags only — not kernel outputs.** |
| AHJ-enforced NFPA 20 / NFPA 13 editions | yes to cite | Delta baselines: **NFPA 20-2025**, **NFPA 13-2025**. Enforced ≠ latest. Prefer matrix pins. |
| Caller **output path** | **yes** for file output | Typically `<name>.calc.json` + short markdown verification. If unnamed, return results in the response and stop (do not invent a path). |

**Driver-block inputs (each missing → stated `ASSUMED`, flagged; not a Stop):** driver type (electric / diesel / both); diesel engine hp **and published fuel consumption rate** (gal/hr); motor nameplate LRC + Table 430.250 FLC of the fire pump, jockey and accessories; AHJ-adopted **NEC** and **NFPA 20** editions (drive the OCPD sum and tank rule); suction regime (flooded positive vs water surface below the pump); underground joint / valve / hydrant counts (jockey leakage); max static suction; component rating.

Optional (do not invent; flag `[V]` / `unresolved`): standpipe add-on if IFC/IBC §905 actually triggered (usually N/A on a single-story hall — hose ≠ standpipe); owner-standard numeric raise already named on the matrix.

**Do not invent** `qd_gpm`, hydrant need verdict, suction/static, `pr_psi` from 100/125/150, a shop-curve head, a system-family election, or `FP-1 = Q @ P`. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `hydrant-supply-curve` | **Pump-needed** verdict; `qd_gpm`; suction/static (or relocated BOR supply points) from **that** curve only | Re-run hydrant / Adequacy; invent suction; skip to envelope from density alone |
| `density-area-dry-increase` | `qd_gpm` (density-method minimum); hose / duration context; elected wet/dry/DI context | Re-run density × area |
| `most-stringent-basis-matrix` | Pump-parameter rows (flow cap, churn, 150% floor, ceiling, N+1, driver); provisional/`[V]`; company wet/dry/DI fence; NFPA deltas | Rebuild dual-carrier union or jurisdiction register; blend FM 140% with AXA 120% |
| `suppression-technology-selection` | Elected wet/dry/DI (handshake); comparison-only / prohibited status | Elect a system family |
| `occupancy-hazard-fork` | Only if hall HC/OH context is still needed and missing from density/hydrant | Re-classify occupancy |
| `fire-area-compartmentation-schedule` | Hall / fire-area id when multi-hall identity is required | Design ratings, doors, dampers |
| `dc-fp-assignment-packet` | Packet context when present | Rebuild the packet |

If an upstream result presents SI/NI/foam/mist as BOD → **Stop** (company scope lock — stays hard). If a required upstream result is missing, or marks a controlling pump / system row `unresolved` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (more stringent candidate; or run the upstream Skill first).

### 2.2 Look up by title

*The engineer Way*; *Do not schedule rated pump gpm/psi on open gating RFIs*; *Fire-pump selection & installation (NFPA 20 + insurer overlay)*; *Water-supply analysis & the supply-vs-demand curve*; *Variable-speed pressure-limiting pumps and the zone pressure envelope*; *Enforced-vs-latest edition resolver and reference pins*; shop `_calc` README / `formulas.pump_envelope`.

---

## 3. Pin editions (cite section AND edition)

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor (pump) | NFPA 20 (stationary pumps) | **NFPA 20-2025** (approved Sept 2024) for the pump delta baseline. AHJ-enforced edition often a cycle behind (unamended 2024 I-Codes typically pin **NFPA 20-2022**). Surface both. **Licensed NFPA 20-2025 primary is not in the shop codebook → every NFPA 20 § below is `[verify vs licensed NFPA 20-2025]`.** |
| Code floor (demand context) | NFPA 13 (density/area that produced `qd`) | **NFPA 13-2025** delta baseline. Consumed from density-area / hydrant; do not re-derive. |
| Insurer | Controlling pump **installation** sheet | **FM DS 3-7, Fire Protection Pumps**, base **April 2012 / Interim Rev. October 2021** in the codebook (catalog current **IR April 2025** — re-pin `[V]` before project use). **AXA XL PRC.14.2.1** Copyright **2021** (AXA jobs; legacy “NFPA 20-1999” metadata — reconcile to 20-2025). Demand still comes from occupancy sheets (**FM DS 5-32 January 2026** / DS 3-26 April 2025), not from DS 3-7. |
| Owner | N+1 / diesel mandate / VSPLC | Project-issued standard. Public posture ≠ BOD. NDA → structure only. |

Inherit pins from `most-stringent-basis-matrix` when present. Always cite **section AND edition**; enforced ≠ latest.

**FM DS 3-7 scope fence (do not miss):** §1.0 explicitly **excludes** water-supply capacity and pressure requirements. DS 3-7 sizes the **installation**. Do not ask this Skill “how many gpm at what psi?” as a scheduled rating.

---

## 4. Confirm prerequisites, then consume, don’t redo

1. Assignment packet exists when preferred — do not rebuild.
2. **`hydrant-supply-curve` completed with pump-needed** (or parent cites already-closed supply proof). Consume `qd` + suction/static from **that** handoff only. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged.
3. **Hydrant Adequate / no-pump** for code/insurer demand → **Stop**. Do **not** run the envelope to mint a pump the supply proof said is not required. Owner N+1 / diesel remains Layer-3 / `handoff` unless a cited sheet already required it.
4. **`density-area-dry-increase` completed** — consume `qd_gpm`; label **density-method minimum**. Canonical FM HC-2 white-space minima when so consumed: **wet 750 gpm**, **dry/DI 950 gpm**. Balanced tree demand is higher (LA-style hall: density 750 → balanced ~980 `[V]`).
5. **`most-stringent-basis-matrix` pins closed** for pump parameters (direct or inherited). Unresolved → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged.
6. Elected system is **wet \| dry \| double-interlock**. SI/NI-as-BOD → **Stop** (§1.1). Foam/mist BOD → **Stop** (§1.2).
7. If occupancy or density is missing and required to interpret `qd` → run that Skill first or carry a stated `ASSUMED` `qd` (flagged); not a Stop.
8. If two carriers both apply **and pump parameters differ** (flow cap, churn preference, N+1, driver mix) without a closed matrix union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to **most-stringent-basis-matrix**. Do not blend FM 140%/110% with AXA 120% here.
9. If the caller asks to **skip** hydrant and freeze a pump nameplate from density-area alone → **Stop** (process guardrail, not a missing-input stop): order is density → **hydrant** → pump. A merely *missing* hydrant result is not this case — carry `ASSUMED` per item 2.
10. If the caller has not named an output path → return the screen in the response and stop; do not pick a codebook location.

---

## 5. Kernel formula (do not hand-roll; use `_calc`; listed envelope, not a shop curve)

```
min_qr_fm      = qd / fm_flow_cap
min_qr_nfpa    = qd / nfpa_flow_cap
qd_over_qr     = qd / qr
churn_net_pref = churn_frac * pr
churn_net_max  = churn_frac_max * pr
p150_min       = p150_frac * pr
q150           = 1.5 * qr
churn_system_pref = churn_net_pref + suction_static_psi
churn_system_max  = churn_net_max + suction_static_psi
```

Linear interpolate **net at `qd` between 100% (`pr`) and 150% (`p150_min`) only if** `qr <= qd <= 1.5*qr`:

```
p_net_qd = pr + (p150_min - pr) * (qd - qr) / (0.5 * qr)
```

Quoted from kernel source (`formulas.pump_envelope`). Labeled **envelope interpolation**. Do **not** treat it as a manufacturer curve. If `qd` is outside the 100–150% band, the kernel prints no `p_net_qd` and the note *“qd outside 100%–150% listed envelope; no interpolation (do not invent a shop curve)”*.

Defaults in the kernel: `churn_frac = 1.20`, `churn_frac_max = 1.40`, `nfpa_flow_cap = 1.50`, `fm_flow_cap = 1.40`, `p150_frac = 0.65`, `ceiling_psi = 175`.

---

## 6. Gating-RFI gate **BEFORE** scheduling (always; this is the Skill’s process step)

Rated flow and rated net are **nameplate cells**. They stay `provisional [RFI-…]` / `TBD [RFI-…]` until the RFIs that *gate* them close, or the engineer accepts the under-design risk **in the rating itself**.

Typical gating holes (any one is enough to refuse a freeze):

- BOR **pressure** still `[SYN]` / `[V]` (no node-by-node / no layout).
- Occupancy demand or hose path (through-pump vs supply-side deduction) unclosed.
- Controlling insurer pump sheet unread / dual-carrier pump rows not unioned.
- Flow test not current / not relocated to suction (hydrant proof incomplete).
- Hydrant need verdict missing or parent closed-proof citation absent.

**What to print instead of a nameplate:**

- Hold table: `Qr_min` from the **stated** demand floor vs FM 140% / NFPA 150% (and AXA 120% / FM-multiple 110% if those layers apply).
- Cap: `Prated_max` implied by churn + max static ≤ component ceiling (usually 175 psi). **That cap is not a selected head.**
- Nameplate: type (electric HSC / diesel), constant-speed vs VSPLC decision, **flow `provisional [RFI]`**, **net `TBD [RFI]`**.
- Verdict: `insufficient-input` is a legal product. `buildable-with-minor-fixes` is not, if the schedule already picked Q @ P.

**Open gating RFIs + caller asks to freeze `FP-1 = Q @ P` → STOP.** Still **run the envelope** if `qd`/`qr`/`pr`/`suction_static` are supplied as screening inputs **and** the hydrant need gate passed; paste stdout; keep `pr_psi` labeled **input**.

Arithmetic matching is not coordination. Byte-identical `_calc` stdout can still be `needs-rework` if the schedule froze the rating.

---

## 7. the engineer Way 3-layer on **pump parameters separately** (then set kernel caps)

Do **not** MAX whole layers. Union each row; name the controlling layer; override kernel caps to match. Kernel defaults are **not** the most-stringent union. Prefer closed matrix pins; do not rebuild the matrix here.

| Parameter | Code floor (NFPA 20-2025) | Insurer | Owner | What the runner does |
|---|---|---|---|---|
| **Flow cap** (`qd/qr` max) | Listed centrifugal guaranteed to **150%** → `nfpa_flow_cap = 1.50`. Sizing screen `Qr ≥ Qd / 1.5` [CODE NFPA 20-2019/2022/2025 §6.2.1, pull 20-08]. | **FM DS 3-7 §2.4.6.4 (p.14):** single 100%-Qmax centrifugal **140%**. **§2.4.6.5:** **multiple** centrifugal **110%** (most stringent number in the codebook). **AXA XL PRC.14.2.1 p.4:** demand **≤ 120%** of rated; never accept > 150%. UFC 3-600-01 §9-5: ≤ **140%** (federal comparison, not commercial control). | May tighten. | Set `fm_flow_cap` / `nfpa_flow_cap` to the **controlling** cap. AXA job → **1.20**, not the kernel 1.40 default. FM two-or-more pumps → **1.10**. |
| **Listed flow** (`qr`) | Round **up** to a listed rating after `min_qr_*`. | AXA XL p.4 standard ratings **500 / 1000 / 1250 / 1500 / 2000 / 2500 gpm**. Rounding `min_qr_fm` up is an **interpretation**, not a kernel output. Process note names **FM DS 3-7 Table 2.3.4.3-1** as the listed-flow round-up table; the install note indexes that table as **piping data** — `[V]` the listed-flow set vs the licensed sheet before treating **750 gpm** (or any non-AXA rating) as listed. | May force a larger spare. | Screen the **candidate** `qr` the caller named. Rounding up is post-kernel. |
| **Rated net** (`pr_psi`) | `Pnet,req(Qd) = Pdischarge,demand − Psuction + Psafety` `[verify §]`. | AXA XL p.4 “standard” pressures **100 / 125 / 150 psi** are **not a menu of screening heads**. Do **not** invent 40 or 100 psi from that list. | May raise component class. | **Keep as INPUT.** Do not invert the envelope to “find” a nameplate. |
| **Churn** | Shutoff head **≤ 140%** rated. **§4.7.7.1:** net churn + max static suction, elevation-adjusted, ≤ component rating [CODE NFPA 20-2019/2022/2025 §4.7.7.1; pull 20-06]. | AXA XL p.3,7: **prefer ≤ 120%**, allow 140%. FM DS 3-7 §2.3.4.2: main relief only when churn + max static can exceed the component rating (**usually 175 psi**). Both carriers: **do not design a system that needs a relief valve to survive churn.** Diesel: FM takes pressure to **121%** of net rated shutoff (governor may permit 110% speed; pressure ∝ speed²). | May force VSPLC / flatter curve. | Leave kernel `churn_frac=1.20` / `churn_frac_max=1.40` unless the controlling sheet / matrix states otherwise. Read `churn_system_*_le_ceiling`. |
| **150% pressure floor** | Pump must still deliver **≥ 150% rated flow**. | FM DS 3-7 §2.4 preamble (p.13): still **≥150% rated flow at ≥65% rated pressure**. AXA XL: pumps that hold demand out to **120–150%** of rated. | — | Kernel `p150_frac = 0.65`. Do not swap in a shop-curve 150% point and call it the envelope. |
| **Component ceiling** | — | AXA XL p.6 and FM DS 3-7: design **≤ 175 psi** where practical (most sprinkler components not listed above 175). AXA XL BOR design-pressure ceiling **≤ 125 psi** is a **supply-analysis** overlay, not a kernel input — report it; do not silently replace `ceiling_psi`. | May specify 175 / 250 / 300 class. | Default `ceiling_psi = 175`. |
| **Component rating (code floor, 2026-10-22)** | — | Components rated for the max working pressure and not less than 175 psi aboveground / 150 psi underground [CODE NFPA 13-2022/2025 §7.1.2, pull 13-30]. Where normal (non-fire) pressure can exceed 175 psi and components are not listed for it, a listed PRV is required, with inlet/outlet gauges, a ≥½ in. relief downstream and a test connection [CODE NFPA 13-2022/2025 §16.9.7.1–16.9.7.5, pull 13-30]. The FM/AXA 175 psi target sits on top of this floor. |
| **N+1 / count** | NFPA 20 sizes *a* pump. | **FM DS 3-7 §2.4.6.2:** standard water supply is **1×100% Qmax**, **or 3×50%**, **or (nonstorage only) 2× equally sized mixed-driver each ≥75% Qmax**. **§2.4.6.3:** if none of those can deliver, N pumps to meet Qmax **and N+1 installed, preferably half electric / half diesel**. AXA XL p.4: demand **> 2000 gpm ⇒ multiple + ≥1 diesel**. | Hyperscalers often mandate N+1 even below 2000 gpm. | **Owner/insurer flags, not kernel outputs.** On an FM job, stop presenting N+1 as an owner nicety. On an AXA job below 2000 gpm, N+1 is Layer-3 unless the owner/sheet says otherwise. |
| **Driver mix** | Alternate power for electric when normal is unreliable or high-rise [CODE 2025 §9.3.1; 2019 §9.3.1 (high-rise) + §9.3.2 (unreliable), pull 20-09 (ORD-FP-012)]. Electric ATS is electric-only — a diesel uses **no** fire-pump ATS. | FM §2.4.12.2: electric **unreliable** = disruptions **>8 h, 3 or more times in 12 months**. AXA: diesel where the pump is the sole supply or power is shaky. UFC: diesel must **not** auto-start on loss of normal power (FM is conditional; on an unattended DC campus the conditional collapses to do-not-auto-start). | Diesel mandate common. | **Flags only.** All-electric on an FM N+1 farm is a **documented departure** from §2.4.6.3 — written variance, not a silent choice. |

**If notes conflict, most-stringent wins and both sources stay visible.** Do not blend FM 140% with AXA 120% into 130%. Do not average FM-multiple 110% with NFPA 150%.

**Key deltas to always print:**

- **Demand (NFPA 13-2025 context, from the consumed `qd`):** FM absolute dry area **2,500 → 3,500 ≈ +40%** vs NFPA 13-2025 dry/DI **+30%** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03]. This Skill does not re-run that math; it **states** that `qd` is the density-method minimum from that union.
- **Pump (NFPA 20-2025):** FM usable curve **140% single / 110% multiple** vs NFPA listed **150%** vs AXA **120%**. FM N+1 + mixed drivers vs NFPA’s single-pump floor. NFPA 20 numeric floor unpinned in codebook → Δ **directional `[V]`** except where FM/AXA numbers are primary.

---

## 7A. Driver block — cited pins (not kernel keys; not a nameplate)

`calcs/fp/run.py` has **no** fuel-tank, OCPD or jockey op — **do not invent one**. Print each rule below as a pin with section **and** edition, show the arithmetic inline, and keep OEM values (engine consumption, motor LRC, jockey curve, seal type) as **`confirm at submittal`**. Most-stringent wins **per row**; enforced ≠ latest.

### 7A.1 Diesel fuel tank

| Layer | Rule | Pin |
|---|---|---|
| NFPA 20-**2022** + **TIA 20-22-1** | Tank(s) ≥ **12 h** of engine run time at the engine's **published fuel consumption rate** + **5 %** expansion + **5 %** sump (§11.4.1.3.1) [CODE NFPA 20-2022 §11.4.1.3.1, pull 20-07] | TIA issued Dec 8 2021, effective Dec 28 2021 |
| NFPA 20-2022 + **TIA 20-22-2** | Fallback **only when consumption is not known:** ≥ **1 gal/hp (5.07 L/kW)** + 5 % + 5 % (§11.4.1.3.1.1 [CODE NFPA 20-2022/2025, pull 20-07]; 2022/2025 only; not in 2019, where 1 gal/hp is §11.4.1.3.1 itself [CODE 2019 §11.4.1.3.1, pull 20-09 (ORD-FP-012)]) | same dates |
| NFPA 20-**2025** | Committee accepted both TIAs as written (PI 107/108) → same 12 h / 1 gal/hp reading | First Draft record Jan 2023; final book [CODE NFPA 20-2025 §11.4.1.3.1, §11.4.1.3.1.1, pull 20-07] |
| NFPA 20-**2019** (AHJs still on it) | ≥ **1 gal/hp** + 5 % + 5 %; no run-time basis | [CODE NFPA 20-2019 §11.4.1.3.1, pull 20-07] |
| **FM DS 3-7** (Apr 2012 / IR Oct 2021) | ≥ **8 h** of engine run time + 5 % expansion + 5 % sump, reserved for the fire-pump engine; **separate tanks and fuel lines per engine**; double-walled steel or vault tank inside the pump room; containment = entire contents + 2 in.; **no biodiesel** | §2.4.21 (p.20); IR Apr 2025 re-pin `[V]` |

- **Governing rule:** compute every applicable layer and take the **larger** tank. At equal consumption, NFPA 20-2022+TIA (12 h) exceeds FM (8 h, the lower insurer floor); on an NFPA 20-2019 AHJ, compare 1 gal/hp against FM 8 h × consumption. **Never cite an 8-hour NFPA 20 rule** (rejected at the 2022 First Draft). Verify with the engineer of record (UFGS invoked): conservative assumption = add UFGS 1 gal/hp + 10 % as an owner layer and take the max of the enforced NFPA 20 edition, FM 8 h and UFGS (no UFGS pull on file).
- **Arithmetic pin:** `run volume = t_h × q_published (gal/hr)`, then add 5 % expansion + 5 % sump as printed. Corpus example (not a default): 290 hp engine at 13.5 gal/hr → 12 h = **162 gal** run volume vs ≈ **290 gal** by the 1 gal/hp fallback — obtaining the published consumption roughly halves the tank. Use **consumption**, not the engine's fuel-**supply** rate.
- Diesel pump room + tank sprinklered EH2 [CODE NFPA 20-2019/2022 §4.14.1.3; 20-2025 §4.14.1.3.2; pull 20-06]; day tanks not approved (committee record, not book text). Edition wording: 2019 §4.14.1.3 says "diesel engine pump drivers and day tanks"; 2022 §4.14.1.3 says "diesel engine pump drivers and fuel tanks"; 2025 §4.14.1.3.2 says "diesel engine pump drivers or fuel tanks serving diesel engine pump drivers" [CODE NFPA 20-2019/2022 §4.14.1.3; 20-2025 §4.14.1.3.2; pull 20-06].

### 7A.2 Electric drive — NEC 695 / NFPA 20 power pins

| Item | Rule | Pin |
|---|---|---|
| Utility (normal) source OCPD | Carry **LRC of the largest fire-pump motor + FLC of all other pump motors (incl. jockey) and accessories, indefinitely**; if not a standard size → **next standard size** per **Table 240.6(A)**. Use the **nameplate LRC**, not a 600 % FLA rule of thumb. Trip not field-adjustable. Listed fire-pump assembly alternative: no trip within 2 min at 600 % FLC, none at 24× FLC restart transient, none within 10 min at 300 % FLC | NEC **2020/2023 §695.4(B)(2)**; NEC 2026 draft **§695.5(B)(2)**; NFPA 20 §9.2.3.4 — working drafts held, adopted book `[V]` |
| Jockey in the sum — edition fork | **NEC 2017:** jockey counted at **LRC**. **NEC 2020+:** jockey (other pump motors) at **FLC**. Pick by the AHJ-adopted NEC year; a stricter local sheet (e.g. Rowlett TX, LRC) governs where it is current | NEC 2020 CMP-13 FD track changes (reconstructed 2017 wording) |
| Generator-side OCPD | Instantaneous pickup of the full pump-room load; **not larger than the 430.62 value** = largest motor's Table 430.52 maximum (inverse-time **250 %** of Table 430.250 FLC, Design B) + Σ FLC of the other motors | NEC 2026 draft 695 + **§430.62(A)** + Table 430.52(C)(1); FLC from **Table 430.250**, not the nameplate (§430.6(A)(1)) |
| GFPE | **Not allowed** anywhere in the fire-pump power circuit; NEC **2020 §240.13**: the ≥1000 A building-main GFPE rule **does not apply** to fire-pump disconnects | [CODE NEC 2017/2020/2023 §695.6(G); 2026 §695.7(G), pull 70-01]; FM DS 3-7 §2.4.12.11 |
| Acceptance-test amps | By enforced edition: **2025** nameplate service-factor amps (or manufacturer documentation), FLA × SF only where SF amps are not provided [CODE 2025 §14.2.6.7.1 / §14.2.6.7.1.1]; **2019/2022** FLA × nameplate SF [CODE 2019 §14.2.6.6.4; 2022 §14.2.6.7.1]; pull 20-12. Verify with the engineer of record: where SF amps are listed, conservative assumption = check both figures on any edition and the lower governs; Table 430.250 FLC still sizes OCPDs only | NFPA 20-2025 SR-23/SR-24; [CODE 2025 §14.2.6.7.1 (SF amps; §14.2.6.7.1.1 FLA × SF where SF amps not provided), pull 20-09 (ORD-FP-012); pull 20-12: 2022 §14.2.6.7.1 and 2019 §14.2.6.6.4 require FLA × SF] |
| Jockey supply | Not through the fire-pump controller / transfer switch (no junction-box use) | [CODE NEC 2017/2020/2023 §695.6(I)(6); 2026 §695.7(I)(8), pull 70-01]; FM DS 3-7 §2.4.14 |

Breaker coordination, voltage drop (≤15 % start), feeder routing, and the 230.95 GFPE collision → **HAND OFF** to *Fire-pump circuit power integrity and selective coordination*. No breaker is "sized" here without nameplate LRC and the AHJ NEC year.

### 7A.3 Jockey (pressure-maintenance) pump

1. **Capacity ≥ normal leakage** ([CODE NFPA 20-2019/2022/2025 §4.27.3; pull 20-06; §4.27.1 is the means-to-maintain-pressure clause, pull 20-09 (ORD-FP-012)]; the fire pump is never the jockey — [CODE NFPA 20-2019/2022/2025 §4.27.7, pull 20-06]; FM DS 3-7 §2.4.7.4). Lower bound from **FM DS 3-10 (Jan 2022 IR) §2.3.1.6** allowable leakage: **2 qt/hr per 100 joints** + 1 fl oz/in. valve dia/hr per metal-seated valve + 5 oz/min per dry-barrel hydrant if tested open.
2. **Upper bound (derivation, `case-2026-10-05-bf`):** keep jockey capacity **below one sprinkler's flow at its minimum pressure** (e.g. K5.6 @ 7 psi = 5.6 × √7 = 14.8 gpm; 7 psi = minimum operating pressure of any sprinkler [CODE NFPA 13-2022/2025 §28.2.4.11.1, pull 13-07]) so a single open head is not masked.
3. **Setpoints — FM DS 3-7 §2.4.11.6:** jockey start = churn + max static suction + **5 psi**; jockey stop = start + **10 psi**; fire-pump start = jockey start − **5 to 10 psi**; **10 psi** decrements per additional pump. NFPA 20 committee example: 155 psi jockey stop / 145 psi pump start.
4. **Window inside the component rating:** the jockey stop (and jockey churn + max suction) must stay ≤ the system component rating (usually **175 psi**) **and** ≤ the jockey pump's OEM flange MAWP (confirm at submittal). If the FM cascade breaks the rating, elect a window inside it and record the trade-off — `case-2026-10-05-bf`: FM start = 120 + 52 + 5 = **177 > 175** → elected jockey stop/start **155/140**, FP-1 start 130, FP-2 120; max system 120 + 52 = 172 ≤ 175 (fire-pump start sits below churn — documented). Each controller gets its **own sensing line** (§2.4.11.1).
5. Jockey pump itself need not be listed; its **controller** must be. A packaged VFD booster is not a listed jockey controller.

### 7A.4 Seal election

| Layer | Rule | Pin |
|---|---|---|
| NFPA 20-**2025** | **Packing only** for centrifugal (new §6.1.1.5) and vertical-shaft pumps — mechanical seals excluded (UL dropped them for new listings in 2021) | SR-8 / SR-9; [CODE 2025 §6.1.1.5 "sealing type for centrifugal pumps shall be packing", pull 20-09 (ORD-FP-012)]; not in 2019 |
| NFPA 20-**2022** | Mechanical seals only with public-main / clean closed-top tank / maker-spec water [CODE NFPA 20-2022/2025 §4.6.2.1.1]; clean-water flush for the seals at positive pressure [CODE NFPA 20-2022/2025 §4.6.2.1.2]; 'positive inlet pressure' = [UNSOURCED / committee record SR-6], not code | 2025 via pull 20-09 stage capture; 2022 [CODE NFPA 20-2022 §4.6.2.1.1, §4.6.2.1.2, pull 20-21]; 2022/2025 only; not in 2019 |
| **FM DS 3-7** (Apr 2012 / IR Oct 2021) | Mechanical seal only on an FM Approved-for-seal pump and only where **all**: clean suction (never open water), suction positive at all flows, **spare split seal set on site**, **weekly** testing | §2.4.5 (p.14); §3.1.8 |

Annex support (advisory, not a requirement): NFPA 20-2022 A.4.6.2.1.1 says mechanical seals "should be restricted to those applications where only clean water is pumped" and the pump "should operate with positive pressure conditions at the pump inlet at all times" (pull 20-25). This backs the packing default where the suction is an open tank, pond or river, or can go negative.

Default = **packing** (most stringent). A mechanical seal on a pre-2025 AHJ needs every FM §2.4.5 condition in writing.

### 7A.5 Variable-speed / pressure-limiting relief

**Diesel derate op (batch10 R3, 2026-10-23).** `_calc` `diesel_derate` (`pump_bhp`, `altitude_ft`, `ambient_f`, `nameplate_hp?`, `stepwise?`, `gear_loss_hp?`): deduct 3 %/1,000 ft above 300 ft [CODE NFPA 20-2025 §11.2.2.4; 2022 identical] and 1 %/10 °F above 77 °F [CODE NFPA 20-2025 §11.2.2.5]; gear loss is a caller input [§11.2.2.6]; derated rating ≥ pump BHP [§11.2.2.7] via `engine_ok` / `deficit_hp`. **Additive combination is a Design practice (batch9 F2), not code text — Verify with the engineer of record** (conservative: additive gives the larger deduction). Prefer the engine OEM's published derate when it is larger. Worked (batch10 R21, the site): 17.64 % → 186.98 hp required; 175 hp fails, 200 hp OK. Use the job's altitude and design ambient; never a demo value.

**Diesel main relief (2026-10-23b).** Where a diesel pump is installed and **1.21 × net rated shutoff (churn) + max static suction, elevation-adjusted > component rating**, a main relief valve is required [CODE NFPA 20-2019/2022/2025 §4.20.1.2; 2025 says "main relief valve", 2019/2022 "pressure relief valve"]. This metric uses the **net shutoff**, not `churn_frac`. `_calc` op `relief_check` (`net_shutoff_psi`, `max_static_suction_psi`, `component_rating_psi`=175 default, signed `elevation_adj_psi`) returns `relief_check_psi`. The 175 psi default is the NFPA 13 §7.1.2 aboveground floor (pull 13-30); use the actual lowest component rating. Unknown max static: Design practice C1 = min static + 10 psi, `ASSUMED`, **Verify with the engineer of record**; get the purveyor value on a real job.

NFPA 20-**2019 §4.20.1.3** [CODE NFPA 20-2019/2022/2025 §4.20.1.3, §4.20.1.3.1; pull 20-06]: VS or diesel pressure-limiting drive → **relief valve required where shutoff head at rated speed exceeds the component rating**, set **≥ 10 psi above** the pressure-limiting set pressure. FM DS 3-7 §3.1.11: VS "best avoided if possible". Do not design a constant-speed system that needs a relief valve to survive churn (§7 churn row). VSPLC sizing → **handoff**.

### 7A.6 Pump type — VT vs HSC (election row)

| Suction regime | Machine class | Pin |
|---|---|---|
| Water surface **below** the pump / static suction lift (tank, wet pit, reservoir) | **Vertical turbine** | FM DS 3-7 §2.4.1.1 (no split-case / end-suction / in-line on static lift); §2.4.2 (VT where water level is below the discharge flange) |
| Permanently **flooded positive suction** | HSC / end-suction / in-line permitted | NFPA 20 positive-suction doctrine; OEM IOMs |

VT fences: bowls at OEM minimum submergence at **minimum** water depth (§2.4.2.2); **exclude water below minimum submergence from duration** (§2.4.2.3); right-angle gear max power and thrust ≤ nameplate (§2.4.2.4); diesel VT → mass-elastic torsional analysis (§2.4.2.5). Method: a prior site worked package (synthetic; not in CASE_INDEX) — refuse HSC on a below-grade tank. Elect the family; never freeze an OEM SKU.

---

## 8. Run `calcs/fp/run.py` — kernel is source of truth

Stdlib kernel. Agents **set inputs and interpret**. Paste **stdout**. QA re-runs the **same JSON**. Exit **2** on bad inputs. Transcript ends with `TRANSCRIPT_OK`. Rounding: **4 decimal places** unless the value is an integer. Booleans `true` / `false`.

**Preferred: JSON batch** (write the JSON at the **caller-named** path, next to the deliverable):

```
python3 calcs/fp/run.py path/to/name.calc.json
```

JSON shape (ops `pump_envelope` / `pump-envelope`):

```json
{
  "job": "<caller job id>",
  "notes": "pump envelope screen; pr_psi is an INPUT not a scheduled rating; hydrant need verdict + gating RFIs listed in markdown",
  "steps": [
    {
      "id": "envelope",
      "op": "pump_envelope",
      "qr": 750,
      "pr": 40,
      "qd": 900,
      "suction_static": 70,
      "churn_frac": 1.20,
      "churn_frac_max": 1.40,
      "nfpa_flow_cap": 1.50,
      "fm_flow_cap": 1.40,
      "p150_frac": 0.65,
      "ceiling": 175
    }
  ]
}
```

**Always include the optional keys in JSON** so the transcript prints them (omitted keys still take formula defaults but disappear from `inputs`). Use the **caller job id**, never a training-job slug. Contract-demo numbers (750 / 40 / 900 / 70) are **not** job defaults — do not copy them into another job.

**Ad-hoc** (one op, no JSON; still paste stdout; prefer JSON for QA):

```
python3 calcs/fp/run.py pump-envelope --qr 750 --pr 40 --qd 900 --suction-static 70 --churn-frac 1.20 --ceiling 175
```

CLI flags (from `run.py`): `--qr` `--pr` `--qd` required; `--suction-static` required; `--churn-frac` default 1.20; `--churn-frac-max` default 1.40; `--qd-nfpa-cap` → `nfpa_flow_cap` default 1.50; `--fm-flow-cap` default 1.40; `--p150-frac` default 0.65; `--ceiling` default 175.

**JSON / CLI aliases → formula kwargs**

| You may write | Kernel kwarg |
|---|---|
| `qr` / `qr_gpm` / `--qr` | `qr_gpm` |
| `pr` / `pr_psi` / `--pr` | `pr_psi` |
| `qd` / `qd_gpm` / `--qd` | `qd_gpm` |
| `churn_frac` / `--churn-frac` | `churn_frac` |
| `churn_frac_max` / `--churn-frac-max` | `churn_frac_max` |
| `nfpa_flow_cap` / `--qd-nfpa-cap` | `nfpa_flow_cap` |
| `fm_flow_cap` / `--fm-flow-cap` | `fm_flow_cap` |
| `p150_frac` / `--p150-frac` | `p150_frac` |
| `suction_static` / `suction_static_psi` / `--suction-static` | `suction_static_psi` |
| `ceiling` / `ceiling_psi` / `--ceiling` | `ceiling_psi` |

**Stdout keys to harvest:** `min_qr_fm_gpm`, `min_qr_nfpa_gpm`, `qd_over_qr`, `churn_net_pref_psi`, `churn_net_max_psi`, `p150_min_psi`, `q150_gpm`, `churn_system_pref_psi`, `churn_system_max_psi`, `ceiling_psi`, `p_net_qd_psi` (only if interpolation applied), `qd_le_fm_cap`, `qd_le_nfpa_cap`, `churn_system_pref_le_ceiling`, `churn_system_max_le_ceiling`, `interpolation_applied`, `interpolation`.

**Kernel README / live transcript** (canonical example numbers from the kernel README — **contract demo only, not job defaults**):

```
CALC KERNEL TRANSCRIPT
job: (adhoc)
steps: 1

--- step pump_envelope  op=pump_envelope  formula=pump rated/churn/150% envelope ---
inputs
  qr_gpm: 750 gpm
  pr_psi: 40 psi
  qd_gpm: 900 gpm
  churn_frac: 1.2000
  churn_frac_max: 1.4000
  nfpa_flow_cap: 1.5000
  fm_flow_cap: 1.4000
  p150_frac: 0.6500
  suction_static_psi: 70 psi
  ceiling_psi: 175 psi
outputs
  min_qr_fm_gpm: 642.8571 gpm
  min_qr_nfpa_gpm: 600 gpm
  qd_over_qr: 1.2000
  churn_net_pref_psi: 48 psi
  churn_net_max_psi: 56 psi
  p150_min_psi: 26 psi
  q150_gpm: 1125 gpm
  churn_system_pref_psi: 118 psi
  churn_system_max_psi: 126 psi
  ceiling_psi: 175 psi
  p_net_qd_psi: 34.4000 psi
  qd_le_fm_cap: true
  qd_le_nfpa_cap: true
  churn_system_pref_le_ceiling: true
  churn_system_max_le_ceiling: true
  interpolation_applied: true
  interpolation: envelope interpolation (linear in flow between 100% rated net and 150% flow at p150_frac of rated net). Not a shop curve.

TRANSCRIPT_OK
```

If stdout disagrees with a hand product, **the kernel wins**. Re-check inputs (especially `fm_flow_cap` left at 1.40 on an AXA or FM-multiple job).

**Do not run** `hydrant`, `density-area`, `hw`, or `louver` inside this Skill. Hydrant/supply-curve already ran (or parent closed proof cited). Density-area already ran. Single-segment HW is not this recipe.

---

## 9. Show-and-verify (independent of stdout)

Write the arithmetic in the markdown verification so a reviewer can recompute without the kernel. Substitutions for the contract-demo numbers above:

```
min_qr_fm   = 900 / 1.40 = 642.8571 gpm     VERIFY: 1.40 × 642.8571 = 900
min_qr_nfpa = 900 / 1.50 = 600 gpm          VERIFY: 1.50 × 600 = 900
qd_over_qr  = 900 / 750 = 1.20              → ≤ 1.40 FM single? true; ≤ 1.50 NFPA? true
churn_net_pref = 1.20 × 40 = 48 psi
churn_net_max  = 1.40 × 40 = 56 psi
p150_min       = 0.65 × 40 = 26 psi
q150           = 1.5 × 750 = 1125 gpm
churn_system_pref = 48 + 70 = 118 psi ≤ 175? true
churn_system_max  = 56 + 70 = 126 psi ≤ 175? true
in_band: 750 ≤ 900 ≤ 1125 → interpolate
p_net_qd = 40 + (26 − 40) × (900 − 750) / (0.5 × 750)
         = 40 + (−14) × 150 / 375
         = 40 − 5.6
         = 34.4 psi
```

**Ceiling-fail check** (same flows, `pr_psi = 100` — the **synthetic-pressure anti-pattern**, not a nameplate):

```
churn_system_pref = 1.20 × 100 + 70 = 190 psi  →  le_ceiling false
churn_system_max  = 1.40 × 100 + 70 = 210 psi  →  le_ceiling false
```

That is the envelope telling you a 100 psi **input** overruns 175 psi at this suction — **not** a license to schedule 100 psi anyway. The MS worked package scheduled 100 psi synthetic from the AXA standard-pressure list while BOR pressure was unclosed. **Do not copy that freeze.**

Post-kernel interpretation (not kernel output): round `min_qr_*` **up** to a listed rating; keep that pick `provisional` until gating RFIs close. AXA 120% screen: `qd ≤ 1.20 × qr`. FM-multiple screen: `qd_share ≤ 1.10 × qr_each`.

---

## 10. Status vocabulary and flags

| Status | Meaning |
|---|---|
| `grounded` | Value pinned to cited section **and** edition (or kernel stdout matching show-and-verify) |
| `provisional` | Usable for screening / hold table; gating RFI or BOR still open — **not** a schedule freeze |
| `unresolved` | Blocking gap (missing hydrant need verdict, unread pump sheet, unclosed matrix pump row) |
| `comparison-only` | SI/NI evidence, AXA 75–100 design band, carrier preference rankings, UFC federal overlay — not BOD |
| `handoff` | Work owned by another Skill (esp. VSPLC, looped-main, hydraulic-tree, back to hydrant) |
| `RFI-variance` | Caller asks SI/NI/foam/mist as BOD; company-fence gate; or asks to freeze nameplate on open RFIs |

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented `pr_psi`, invented suction static, invented hydrant pair, invented shop-curve head, invented 750-gpm “standard” rating if the licensed listed-flow table is unpinned, any nameplate Q @ P. Never present `[SYN]` as a scheduled rating. |
| **`[V]`** | NFPA 20-2025 section pins; listed-flow set vs FM DS 3-7 Table 2.3.4.3-1 vs AXA p.4; balanced BOR demand; AHJ-enforced edition; owner NDA numbers; AXA BOR ≤125 psi vs 175 psi component class (different axes — report both); FM DS 3-7 IR Apr-2025 re-pin; NFPA 20-2025 final book text for the tank / seal / acceptance-amp rows; NEC adopted-book wording and subsection letters for 695 / 240.6 / 430.62; engine consumption, motor LRC, jockey curve and flange MAWP (OEM, confirm at submittal). |
| **`provisional [RFI-…]`** | Nameplate flow and/or net while gating RFIs are open. **Required.** |

**Grounded envelope fractions** (1.20 / 1.40 churn; 1.40 / 1.50 / 1.10 flow caps; 0.65; 175 psi): cite sheet **and** edition. Do not `[SYN]` the kernel defaults themselves.

**Driver mix / N+1** print as **owner/insurer flags** next to the transcript. They are not stdout keys. Status: often `grounded` on FM §2.4.6.3 / AXA >2000 gpm; Layer-3 / `provisional` when owner-only below trigger.

---

## 11. Hand-offs (do not continue here)

**Water-supply order:** density-area → hydrant-supply-curve → **this Skill** (if pump needed).

- Hydrant need verdict missing / skip attempt → **`hydrant-supply-curve`** (do not invent suction).
- Hydrant **Adequate / no-pump** → stop code/insurer pump path; owner N+1 = Layer-3 / `handoff` if owner mandates.
- `qd` not yet produced → **`density-area-dry-increase`**.
- Dual-carrier pump rows still disagree / unresolved → **`most-stringent-basis-matrix`**.
- Occupancy / HC / OH missing → **`occupancy-hazard-fork`**.
- System-family election missing / SI/NI-as-BOD / foam / mist → **`suppression-technology-selection`** + `RFI-variance` (do not elect here).
- Packet missing → **`dc-fp-assignment-packet`**.
- Multi-hall identity missing → **`fire-area-compartmentation-schedule`**.
- Looped-main / one-leg-out diameter → looped-main recipe (`_calc` `hw` is a **single segment**, not a network).
- Churn vs 175 psi fails and the job needs modulation → *Variable-speed pressure-limiting pumps and the zone pressure envelope* (VSPLC). FM DS 3-7 §3.1.11 posture is “best avoided if possible”; NFPA 20 has barred a PRV from controlling churn since 2003. **This Skill does not size VSPLC.**
- Combustion-air / louver free-area → `_calc` `louver` / **`combustion-air-and-hall-free-area`**. Diesel ventilation numbers live on FM DS 3-7 §§2.4.17–2.4.25 — not here.
- Breaker coordination / voltage drop / feeder routing / 230.95 GFPE collision → *Fire-pump circuit power integrity and selective coordination* (this Skill prints only the §7A.2 OCPD rule).
- Node-by-node BOR psi, pipe schedule → hydraulic-tree Skill.
- Certified **shop curve** / field 3-point (or FM App. C 6-point) acceptance → submittal / commissioning, not this screen.
- CAD / pump-room layout / suction 10D spool / test header → other recipes / **`itm-design-for-testability`** as applicable.
- Fire-pump controller configuration (refuse list: Lockout / Load Shed / auto-stop), remote-signal terminal map, pump-room ambient floor + max, ATS outage budget, valve supervision schedule, acceptance-start union → **`fire-pump-controller-configuration-and-supervision`**.

---

## 12. Output

Write **only** to the path the **caller names** (typically a `.calc.json` transcript plus a short markdown verification beside it). Do **not** write into `KNOWLEDGE_BASE`, `EXERCISES`, `_pruner`, `_surveyor`, `_engineer`, `ARCHIVE`, or any shop codebook tree.

**`.calc.json`** — the JSON actually run (QA re-runs this file). Keep a `.calc.stdout.txt` (or paste stdout into the markdown). Transcript must end with `TRANSCRIPT_OK`.

**Markdown verification** (short) must contain:

1. Pinned editions (NFPA 20-2025 + AHJ pin; FM DS 3-7 Apr-2012/Oct-2021 and/or AXA XL PRC.14.2.1 2021; NFPA 13-2025 demand context; owner posture).
2. Upstream intake: hydrant **pump-needed** (or parent closed proof); density-area `qd` consume; matrix pump-parameter pins; elected wet/dry/DI confirmed; company-fence handshake.
3. Consumed `qd_gpm` labeled **density-method minimum** (balanced is higher); suction/static source named (hydrant handoff).
4. Gating-RFI status. If open: **no `FP-1 = Q @ P`**; nameplate cells `provisional [RFI-…]` / `TBD [RFI-…]`.
5. 3-layer table for **flow cap, listed flow, rated net (input), churn, 150% floor, ceiling, N+1, driver** separately; controlling values; kernel overrides (`fm_flow_cap` etc.).
6. Kernel command + **full stdout**.
6a. **Driver block (§7A)** as pins: fuel-tank rule by enforced NFPA 20 edition vs FM 8 h (larger governs); NEC-year OCPD sum (jockey LRC vs FLC) + 240.6 step + 430.62 generator cap + no GFPE; jockey leakage bracket + setpoint window ≤ component rating; seal; VS relief; VT vs HSC. OEM values `confirm at submittal`; missing inputs `ASSUMED`.
7. Show-and-verify of `min_qr_*`, `qd_over_qr` vs caps, churn vs 175, and the interpolation formula when in-band.
8. Delta vs NFPA 20-2025 (flow cap / N+1 / churn 120 vs 140) and vs NFPA 13-2025 (demand context only).
9. Statement that this is the **listed envelope (churn / 100% / 150%)**, not a shop curve.
10. Status register: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` + `[SYN]` / `[V]` / `provisional [RFI-…]` list.
11. Explicit hand-off (density → hydrant → pump order stated; matrix / hydraulics / VSPLC / looped-main / louver as still open).

Do **not** emit: occupancy schedule, density×area re-calc, hydrant Adequacy rebuild, dual-carrier BOD rebuild, looped-main diameter, combustion-air CFM, CAD, or a scheduled `FP-1 = Q @ P` while BOR or gating RFIs are open.

---

## 13. Stop

> **2026-10-07 intake rule:** any item below that is a missing packet, a missing upstream result, or a missing input blank is **not** a Stop — proceed with a stated `ASSUMED` value (value + why), flagged in the output and status register. Only company scope-lock items (SI/NI-as-BOD → `RFI-variance`, foam, water mist `PRACTICE REFUSED`, clean agent as company BOD) and wrong-Skill / out-of-scope routing remain hard Stops.

Return the blocker (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess.

1. Missing **`hydrant-supply-curve` pump-needed** verdict (and no parent-cited closed supply proof). Caller jumps density → pump.
2. Hydrant verdict is **Adequate / no-pump** for code/insurer demand (owner N+1 is Layer-3 / `handoff`, not this screen).
3. Missing **`qd_gpm`** (density-area-dry-increase has not run, or caller did not pass it).
4. Missing / **unresolved** matrix pump-parameter pins (flow cap / churn / N+1 / driver) when dual-carrier or controlling sheet unread.
5. Elected system missing, or SI/NI / other prohibited preaction presented as **BOD** → `RFI-variance`.
6. Caller asks to elect/design/screen **foam** (prohibited) or **mist** (`PRACTICE REFUSED`).
7. Caller asks to **freeze a nameplate** (`FP-1 = Q @ P`) while **gating RFIs are open** or **BOR demand is unclosed**.
8. **Inventing `pr_psi`** from a shop curve, from AXA XL 100/125/150 “standard” pressures, or by inverting the envelope.
9. Writing **`FP-1 = Q @ P`** while BOR is open (even with a matching transcript).
10. **Inventing suction/static** instead of consuming hydrant handoff (or a cited closed proof).
11. Unpinned **carrier** (cannot choose FM 140/110 vs AXA 120 vs NFPA 150).
12. Trying to **re-classify occupancy**, **re-run density×area**, **re-run hydrant**, **size a looped main**, **size combustion-air louvers**, or **draw CAD** here.
13. Trying to **replace the listed envelope with a shop curve** (or invent points outside 100–150%).
14. Caller asks to write into `KNOWLEDGE_BASE` / `EXERCISES` / `_pruner` / `_surveyor` / `_engineer` / `ARCHIVE`.

Missing `pr_psi` as a screening input is **not a Stop**: the kernel requires it, so use a stated `ASSUMED` screening pressure (value + why) labeled **`ASSUMED` / `[SYN]` input**. It is not a rated-point selection — if it came from the standard-pressure list, say so. Do not schedule or freeze it.

---

## 14. Citations

Shop codebook **by title** (not a required filesystem path). Prefer these section+edition pins; omit or `[V]` anything not here. **Do not invent section numbers.**

**the engineer Way / process**

- *The engineer Way* — 3-layer most-stringent; cite section **and** edition; enforced ≠ latest; show-and-verify; `[SYN]`/`[V]`; status vocabulary. Pump delta vs **NFPA 20-2025**; demand-context delta vs **NFPA 13-2025**.
- *Do not schedule rated pump gpm/psi on open gating RFIs* (seedling) — `pr_psi` is an input; rounding `min_qr` up is interpretation; honest prose does not save a frozen schedule; listed 100/125/150 psi are not a screening-head menu. Negative teaching: MS campus pump worked package froze **100 psi synthetic** (`corpus-insufficient`); the campus Mesa FP-1 scheduled **750 @ 40** on open RFIs (`needs-rework`).

**NFPA 20-2025** (*Fire-pump selection & installation*) — rows carry their pull; any row still marked `[verify §]` is not yet pinned

| Claim | Pin |
|---|---|
| `Qr ≥ Qd / 1.5`; hard rule: greatest single system demand ≤ 150% of rated flow | [CODE NFPA 20-2025 §4.10.1, pull 20-23, raw text checked: "greatest single demand for any fire protection system connected to the pump is less than or equal to 150 percent of the rated capacity (flow)"]; 2019/2022 numbering not pulled `[V]` |
| Shutoff (churn) ≤ **140%** rated | [CODE NFPA 20-2019/2022/2025 §6.2.2, pull 20-08] |
| Net churn + max static suction ≤ component rating | [CODE NFPA 20-2019/2022/2025 §4.7.7.1; pull 20-06] |
| Suction ≥0 psi at the suction flange with all pumps at 150% (required, not a preference); **−3 psi** at 150% suction-tank exception | [CODE NFPA 20-2019/2022/2025 §4.16.3.1 (identical); §4.16.3.2 tank tied to water level after full demand at or above pump centerline (2022/2025) vs tank base at or above pump (2019); pull 20-13] |
| Jockey required; fire pump is not the jockey | [CODE NFPA 20-2019/2022/2025 §4.27.7; pull 20-06] |
| Alternate power for electric when unreliable / high-rise; start voltage drop ≤15% | [CODE 2025 §9.3.1; 2019 §9.3.1 (high-rise) + §9.3.2 (unreliable); 15% drop 2019/2025 §9.4.1, pull 20-09 (ORD-FP-012)] |
| 2025 exemption: no alternate power for the primary pump where a backup engine-, steam- or electric-driven pump with an independent source meeting §9.2.2 is installed; 2022 wording same as 2019 | [CODE NFPA 20-2025 §9.3.2; NFPA 20-2019/2022 §9.3.1–9.3.2, pull 20-20] |
| Suction control valve: listed OS&Y; no other control valve within 50 ft of the suction flange except §4.29.3 devices; closure ≥5 s; automated valves need position indication + supervisory switch (no butterfly in that zone) | [CODE NFPA 20-2025 §4.16.5.1–4.16.5.4, pull 20-15] |
| Break / suction tank: net capacity = overflow inlet to vortex plate; break tank ≥15 min at 150% rated, auto-fill ≥40 °F and ≤4 in. below overflow, manual fill bypass | [CODE NFPA 22-2023 §4.1.4, §14.5.1–14.5.1.4, pull 22-02] |
| Suction flush: Table 14.1.1.1 rate; if not available, ≥150% rated; if not, greater of 100% rated or max system demand (conditional, not unconditional 150%) | [CODE NFPA 20-2022 §14.1.1.3–14.1.1.3.2; NFPA 24-2022 §10.10.2.1.3.2, pull 20-24] |
| Acceptance 3-point curve churn / 100% / 150% | Load test at minimum, rated and peak loads [CODE NFPA 20-2019/2022/2025 §14.2.6.3]; match to certified shop curve [CODE NFPA 20-2019/2022/2025 §14.2.4.2], pull 20-10; 'churn' point wording [practice/annex] (not in Ch. 14 body text) (common ground with FM DS 3-0) |

**FM DS 3-7 (April 2012 / Interim Rev. October 2021 codebook; catalog IR April 2025 `[V]` re-pin)** — *Fire-pump selection & installation*

| Claim | Section |
|---|---|
| Sheet disclaims capacity/pressure (occupancy sheets size gpm/psi) | §1.0 (p.4) |
| 1×100% **or** 3×50% **or** (nonstorage) 2× mixed-driver ≥75% | §2.4.6.2 |
| N+1, preferably half electric / half diesel | §2.4.6.3 |
| Single centrifugal usable **140%** of rated | §2.4.6.4 (p.14) |
| Multiple centrifugal usable **110%** of rated | §2.4.6.5 (p.14) |
| Still deliver ≥150% rated flow at ≥65% rated pressure | §2.4 preamble (p.13) |
| Relief only if churn + max static can exceed component rating (usually **175 psi**) | §2.3.4.2 |
| No series pumps (3% FTS → 97%→91% for three) | §2.2.2.2 / §3.1.2 |
| Electric “unreliable” = >8 h, 3× in 12 months | §2.4.12.2 |
| VSPLC “best avoided if possible” | §3.1.11 |
| Field acceptance 6 flow points, 6+6 starts, ≥1 h run | App. C |

**AXA XL PRC.14.2.1 (Copyright 2021)** — same install note

| Claim | Pin |
|---|---|
| Standard rated flows 500 / 1000 / 1250 / 1500 / 2000 / 2500 gpm | p.4 |
| Standard rated pressures 100 / 125 / 150 psi (**not a screening menu**) | p.4 |
| Demand ≤ **120%** of rated; never accept > 150% | p.4 / water-supply note p.3 |
| > **2000 gpm** ⇒ multiple pumps + ≥1 diesel | p.4 |
| Prefer churn ≤ **120%**; allow 140% | p.3, 7 |
| System **≤ 175 psi** unless heavy-duty components | p.6 |
| BOR design-pressure ceiling **≤ 125 psi**; design FP systems to **75–100 psi** | water-supply analysis note (PRC 14-1-2-0 p.5–6) — report; different axis from 175 psi class |

**Driver block (§7A) — corpus pins**

| Claim | Pin |
|---|---|
| Diesel tank 12 h at published consumption + 5 % + 5 % | NFPA 20-2022 §11.4.1.3.1 per **TIA 20-22-1** (Dec 2021) [CODE NFPA 20-2022/2025 §11.4.1.3.1, pull 20-07] |
| 1 gal/hp fallback when consumption unknown | NFPA 20-2022 §11.4.1.3.1.1 per **TIA 20-22-2** (Dec 2021) [CODE NFPA 20-2022/2025, pull 20-07]; 2022/2025 only; not in 2019 (2019 §11.4.1.3.1, pull 20-09 (ORD-FP-012)) |
| 2025 accepts both TIAs | NFPA 20-2025 First Draft PI 107/108 (Jan 2023); final text [CODE NFPA 20-2025 §11.4.1.3.1, §11.4.1.3.1.1, pull 20-07; same text in 2022] |
| 2019 tank = 1 gal/hp + 5 % + 5 % | [CODE NFPA 20-2019 §11.4.1.3.1, pull 20-07] |
| FM tank 8 h + 5 % + 5 %; separate tanks/lines; no biodiesel | FM DS 3-7 Apr 2012 / IR Oct 2021 §2.4.21 |
| Utility OCPD LRC + FLC others, next standard size | [CODE NEC 2020/2023 §695.4(B)(2); 2026 §695.5(B)(2), pull 70-01] · Table 240.6(A) |
| Jockey LRC (2017) vs FLC (2020+) | NEC 2020 CMP-13 First Draft track changes |
| Generator-side cap | NEC §430.62(A) + Table 430.52(C)(1) + Table 430.250 |
| No GFPE in fire-pump circuit; 240.13 exemption | [CODE NEC 2017/2020/2023 §695.6(G); 2026 §695.7(G), pull 70-01]; NEC 2020 §240.13; FM DS 3-7 §2.4.12.11 |
| Acceptance amps by edition (2025 SF amps; 2019/2022 FLA × SF; lower governs = Verify with the engineer of record) | NFPA 20-2025 SR-23/24; [CODE 2025 §14.2.6.7.1, fallback FLA × SF §14.2.6.7.1.1, pull 20-12]; 2022 §14.2.6.7.1 and 2019 §14.2.6.6.4 require FLA × SF (edition fork applied) |
| Jockey capacity ≥ leakage; FM leakage | [CODE NFPA 20-2019/2022/2025 §4.27.3; pull 20-06]; FM DS 3-10 Jan 2022 §2.3.1.6 |
| Jockey cascade | FM DS 3-7 §2.4.11.6 (start = churn + max static + 5; stop +10; FP start −5 to −10) |
| Packing only (2025) vs FM conditional seal | NFPA 20-2025 SR-8/9; NFPA 20-2022 SR-6; FM DS 3-7 §2.4.5 |
| VS relief ≥10 psi above set where shutoff > component rating | [CODE NFPA 20-2019/2022/2025 §4.20.1.3, §4.20.1.3.1; pull 20-06] |
| VT on static lift; exclude water below submergence | FM DS 3-7 §2.4.1.1, §2.4.2, §2.4.2.3 |
| Worked method | `case-2026-10-05-bf` (jockey 155/140 inside 175 psi); a prior site worked package; electric-fire-pump-breaker packages (NEC 2017 vs 2020 jockey LRC; 430.62 cap) |

**Demand / supply consumed (do not re-cite as this Skill’s work):** FM DS 5-32 **January 2026** §2.4.3.3.1.1.A (0.2 gpm/ft²; 2,500 wet / 3,500 dry); hose 250 gpm §2.4.1.5; 60 min §2.4.1.6 — **density-area-dry-increase**. Hydrant Adequacy / pump need / suction points — **hydrant-supply-curve**.

**Kernel** — `_calc` README / `run.py` / `formulas.pump_envelope`: formula block in §5; interpolation only in the 100–150% band; **not a shop curve**.

**Negative teaching (exercise, not a codebook number):** worked package *hyperscale campus fire-water supply — fire-pump selection* (MS / AXA XL / diesel N+1), verdict **`corpus-insufficient`**, froze **100 psi synthetic** rated pressure while BOR array friction was unclosed. the campus Mesa FP-1 scheduled **750 gpm @ 40 psi** on open gating RFIs. Do not copy either freeze. The arrangement/SOO half of the MS package is not this Skill’s output.

**Company fence (consume, do not re-elect):** STS / matrix / density / hydrant wet/dry/DI handshake; FM DS 5-32 §2.4.1.1 ranking = comparison evidence only.

---

## 15. the engineer Way

1. **Three-layer, most stringent, on pump parameters separately.** Code (NFPA 20-2025) is the *floor* (150% listed curve, 140% churn max, §4.7.7.1 overpressure [CODE NFPA 20-2019/2022/2025 §4.7.7.1; pull 20-06]). The **insurer sheet** usually sets the real basis: FM DS 3-7 usable **140% / 110%**, count, driver mix, N+1; AXA XL **120%** demand cap and **120%** preferred churn. The **owner standard** can raise N+1 / diesel again. Cite the sheet. Do not assert N+1 or diesel from habit — on FM it is Layer-2; on AXA below 2000 gpm it is often Layer-3.
2. **Delta vs NFPA 20-2025 every time** (pump), **and vs NFPA 13-2025** (consumed demand). If the numeric NFPA 20 floor isn’t in the licensed primary, say **directional `[V]`**. Do not invent a 20-2025 section number.
3. **Show-and-verify.** Kernel stdout + independent `min_qr`, cap, churn+suction vs 175, interpolation. Kernel wins on arithmetic.
4. **Current editions; enforced ≠ latest.** Default NFPA 20-**2025** / 13-**2025** for delta baselines; report the AHJ-referenced editions when they differ.
5. **Honesty on the nameplate.** The envelope **screens** a candidate (`qr`, `pr` as **inputs**). It does not mint `FP-1 = Q @ P`. Density `qd` is a **minimum**. Open gating RFIs → `provisional [RFI-…]`. The MS synthetic-100-psi freeze and the campus 750@40 freeze are the anti-patterns.
6. **Company fence + upstream order.** Wet/dry/DI only. Density → hydrant → pump. Consume; do not rebuild.
7. **Driver block = pins, most-stringent per row.** Fuel tank: larger of enforced NFPA 20 edition (12 h + TIA / 1 gal/hp) and FM 8 h. OCPD sum by the AHJ NEC year. Jockey window inside the component rating. Packing by default. VT on static lift. No invented kernel op; no frozen SKU.

---

## 16. Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH classification | `occupancy-hazard-fork` |
| System-family election (wet/dry/DI) | `suppression-technology-selection` |
| Density × area `qd` / gallons | `density-area-dry-increase` (**consume** `qd_gpm`; label density-method **minimum**) |
| Dual-carrier per-parameter BOD / controlling pump rows | `most-stringent-basis-matrix` (**consume** controlling pump rows; do not blend caps here) |
| Assignment packet | `dc-fp-assignment-packet` |
| Hydrant / municipal supply curve / pump need verdict | `hydrant-supply-curve` (**mandatory** need verdict + suction handoff) |
| Looped-main / one-leg-out diameter | looped-main recipe (`hw` = one segment) |
| Node-by-node BOR psi, pipe schedule | hydraulic-tree Skill |
| VSPLC / zone pressure envelope | *Variable-speed pressure-limiting pumps and the zone pressure envelope* |
| Combustion air / louver | `combustion-air-and-hall-free-area` / `_calc` `louver` |
| Shop curve, CAD, pump-room architecture, test-header (→ `itm-design-for-testability`), fuel-tank construction details / containment drawings | other recipes / specs / ITM as applicable (fuel-tank **sizing rule** is §7A.1 here) |
| Writing into `KNOWLEDGE_BASE`, `EXERCISES`, `_pruner`, `_surveyor`, `_engineer`, `ARCHIVE` | forbidden |

---

## 17. Runner checklist

- [ ] Hydrant **pump-needed** consumed (or parent closed proof cited). Density alone not used as pump permission. Suction/static from hydrant handoff.
- [ ] Packet consumed (not rebuilt). Occupancy not reclassified. Density×area not rerun; `qd_gpm` consumed and labeled **density-method minimum**. Wet **750** / dry/DI **950** when those FM HC-2 minima apply — **not** “wet/SI 750”.
- [ ] Company fence: elected wet/dry/DI only. SI/NI-as-BOD / foam / mist → stopped with `RFI-variance`.
- [ ] Matrix pump-parameter pins closed (or inherited). Dual-carrier conflict → stopped / handed to matrix.
- [ ] Editions pinned: NFPA 20-2025 (delta) + AHJ pin; NFPA 13-2025 demand context; FM DS 3-7 Apr-2012/Oct-2021 (IR Apr-2025 `[V]` re-pin) and/or AXA XL PRC.14.2.1 2021; owner posture.
- [ ] Gating-RFI gate done **before** any schedule sentence. Open → envelope + `provisional [RFI-…]`; **no `FP-1 = Q @ P`**.
- [ ] `pr_psi` treated as **input**. Not invented from 100/125/150 or a shop curve. Not frozen while BOR is open.
- [ ] 3-layer union **per parameter** (flow cap, listed flow, rated net, churn, 150% floor, ceiling, N+1, driver). Kernel `fm_flow_cap` / `nfpa_flow_cap` **overridden** to the controlling cap (AXA 1.20; FM-multiple 1.10; FM-single 1.40; NFPA 1.50). Not left at defaults out of habit.
- [ ] JSON written at **caller path**; `python3 calcs/fp/run.py <that.json>` run; **full stdout pasted**; `TRANSCRIPT_OK`; exit 0. QA can re-run the same file.
- [ ] Independent verify: `min_qr_fm = qd/fm_cap`, `min_qr_nfpa = qd/1.5`, `qd_over_qr` vs caps, `churn_net_* = frac × pr`, `churn_system_* = net + suction` vs 175, interpolation formula **only** in 100–150% band. Kernel wins.
- [ ] Output labeled **listed envelope (churn / 100% / 150%)**, not a shop curve. Interpolation note pasted.
- [ ] N+1 / driver mix printed as **flags**, not as kernel keys.
- [ ] Driver block (§7A) printed as pins: fuel tank (enforced NFPA 20 edition vs FM 8 h, larger governs; consumption not supply rate); NEC-year OCPD sum + 240.6 + 430.62 cap + no GFPE; acceptance SF amps; jockey leakage bracket + FM §2.4.11.6 cascade checked against 175 psi; seal (packing default); VS relief; VT vs HSC. OEM values confirm at submittal.
- [ ] Deltas printed vs NFPA 20-2025 (pump) and NFPA 13-2025 (demand context).
- [ ] Status register present: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` + `[SYN]` / `[V]` / `provisional [RFI-…]`.
- [ ] Negative teaching remembered: do **not** copy the MS synthetic-100-psi freeze or the campus 750@40 freeze.
- [ ] No codebook / EXERCISES / agent-worktree writes. No CAD / louver / looped-main / occupancy / hydrant rebuild.

---

## 18. 2026-09-01 sheet addendum

- **FM DS 3-7** catalog current **April 2012 / IR April 2025** (codebook was IR Oct 2021). Official ungated `.../03-water-supply/fmds0307.pdf`. Pump-power *installation* + transfer switches live here. Re-pin `[V]` churn/150% section numbers against the Apr 2025 copy before project use.
- **AXA XL PRC.14.2.1.1** *Centrifugal Fire Pump Acceptance Tests* **2020-01-31**, 9 pp: acceptance (200%/20 psi sibling). This Skill still **does not freeze a nameplate**. Consume the PRC for the acceptance-test overlay when AXA controls; do not treat it as a shop curve.
- **DS 5-20** *Electrical Testing* IR Oct 2025 is the 2-81 **ATS test** target — ITM Skill, not envelope sizing.
- **DS 5-23** is facility gensets, not the listed fire-pump envelope.

## Duty-not-SKU pin — Lead18 B16-R3, 2026-10-27
- Write rated duty + NFPA 20-2025 envelope (§4.8.1; churn §4.7.7.1). Never freeze a maker/model; contractor picks the listed unit.
- Teaching duty **KEEP 1,000 gpm @ 40 psi** (city+pump 96.67 vs 47.92, +48.75 on the capped design curve). Motor ≥ 40 hp class ASSUMED, per listed curve.
- Optional alternate **C 1,250 @ 40** (city+pump 100.72, PASS) = alternate duty criteria note only; no auto restamp. If a live job elects it: re-check NFPA 20 / NEC 695 feeder and test header. Option with 8.6 psi churn margin to 175 psi = least preferred. Verify with the engineer of record.

## 2026-10-28 update — prior fold Lead24: diesel derate + §4.20.1.2 relief + B22R2-NEG-1 (worked-only, SYNTHETIC)
Source: EXERCISES/worked/batch22-r2__diesel-fp-derate-relief-screen.md (_calc exit 0). Synthetic 4,500 ft / 104 °F, 1,500 gpm diesel, max BHP 140.
- **Derate:** NFPA 20-2022/2025 §11.2.2.4 (3 %/1,000 ft above 300 ft) + §11.2.2.5 (1 %/10 °F above 77 °F; A.11.2.2.5 include room temp rise). 3×4.2 = 12.6 % + 1×2.7 = 2.7 % → 15.3 %, factor 0.847 → engine ≥ **165.3 hp** 4-h (140/0.847 = 165.29). 150 hp FAIL (127.05); 175 hp PASS (148.2). Additive combination = Lead practice, code silent → Verify with the engineer of record; continuous vs stepwise (162.8 hp). Verify with the engineer of record. §11.2.2.2 10 % listing margin is not a designer derate — don't stack. Schedule: "≥ 165.3 hp after §11.2.2.4/.5 derate", no SKU.
- **Diesel relief NFPA 20-2025 §4.20.1.2:** 121 % × churn + max static vs 175 psi (NFPA 13 §7.1.2 rating). Option A 1.21×125+40 = **191.25 > 175 → MRV required** (size per §4.20.2.1). Option B 1.21×110+40 = 173.1 PASS only if max static ≤ **41.9 psi** (50 psi → 183.1 FAIL). Purveyor max-static letter needed.
- **B22R2-NEG-1:** using electric §4.7.7.1 (125+40 = 165 ≤ 175 "OK") falsely clears diesel — misses ~110 % overspeed (pressure ∝ speed² ≈ 1.21).
- Not restamped into the site (electric). C = 1,250@40 alt note and 1,000@40 duty unchanged.

## 2026-10-29 PDT — prior fold Lead25: B23R2-NEG-1 (electric relief rule falsely clears diesel)
Source: `EXERCISES/worked/batch23-r2__diesel-fp-controller-config-supervision.md` (`_calc` exit 0). Synthetic 1,000 gpm / 110 psi net diesel, shutoff 130.
- Derate: 110 hp nameplate × 0.977 → 107.47 hp ≥ 95 bhp → PASS (NFPA 20-2025 §11.2.2.4/.5/.7).
- Diesel relief screen is NFPA 20-2025 §4.20.1.2 (121 % overspeed shutoff basis): static 55 → 212.3 psi; static 40 → 197.3 psi; both > 175 → **MRV required**.
- **B23R2-NEG-1:** at static 40 the electric §4.7.7.1 churn screen gives 170 ≤ 175 and looks "compliant". That is a false clear for diesel, because the electric rule leaves out the 121 % overspeed term. Always screen diesel on §4.20.1.2. (Extends B22R2-NEG-1.) Static suction = purveyor letter (ASSUMED until held).

## Canada diesel pump house (AB/BC/ON) — B26-R2 / Lead28 fold, 2026-10-29

Canada unlocked; pin NFPA 20 per that code's Table 1.3.1.2 (**2016** BC/AB/ON-OBC; **2019** NBC 2025 model) — never cite 2019/2025 §§ on an AB/BC job. Teaching case is SYNTHETIC (the province DI campus; 1,000 gpm @ 100 psi diesel; suction 60 psi, 125 hp ASSUMED).

- **Fuel:** NFPA 20-2016 §11.4.1.3.1 (1 gal/hp + 5% + 5%) → 125 × 1.05 × 1.05 ≈ 137.8 gal ≈ **522 L** (ASSUMED hp; mfr curve governs).
- **NFC Part 4 room fork:** NFC(AE) 2023 4.3.13.1.(1)(b) allows indoor fire-pump fuel; 4.3.13.4.(1) routes to a **4.3.14 room** except per 4.2.8. **Branch F2 (industrial):** 4.2.8.2.(1)(b) incidental ≤5 000 L Class IB–IIIA **per fire compartment, summing all tanks** (generator day tanks too). **Branch Group D:** 4.2.8 N/A → dedicated 4.3.14 room: ≥2 h separation, contain ≥100% largest tank, liquid-tight joint, no other use. Room cannot close until AHJ/architect pins F2 vs D. Static head ≤**70 kPa** (NFC(AE) 2023 4.3.13.3 — confirmed). Heat ≥40 °F (NFPA 20-2016 §4.13.3.1; FM DS 3-7); winter-grade diesel, no biodiesel (FM DS 3-7 §2.4.21).
- **Churn NEG (B26R2-NEG-3, STANDS):** 60 psi ASSUMED suction + 120 psi net churn = **180 > 175 psi** ceiling → FAIL. Fix path: lower Pr / flatter curve / NFPA 20-2016 pressure control (section pin [verify]); do not freeze Pr or relief; replace ASSUMED suction with the province flow test.
- Other NEGs: **NEG-1** Group D with tank in pump room (4.2.8 is industrial-only) → 4.3.14 room; **NEG-2** F2 count of only the FP tank → sum compartment; **NEG-4** summer diesel/biodiesel.
- **NEG-CA (prior fold Lead31, GAP-B29R1-2 — supersedes the prior "Open (no invent)" line):** NEG-CA-1 inventing a ULC 2 h assembly number; NEG-CA-2 inventing CSA B139 piping text; NEG-CA-3 inventing an NFPA 20-2016 pressure-control § number not pinned; NEG-CA-4 citing NFPA 20-2019/2025 §§ on an AB/BC 2016 pin. Each → NEEDS HOLD. Still open: ASSUMED suction/hp.


## 2026-11-03 — prior fold Lead31: GAP-B29R1-2 NEG-CA list
Canada diesel pump-house "Open (no invent)" upgraded to NEG-CA-1..4. B26R2-NEG-3 churn and NEG-1/2/4 unchanged.

## 2026-11-04 — stop-vocab normalize (staged)
- Inserted §1.0 Country/edition gate (model A) + NEG-CA before §1.
- `9. If the caller asks to **skip** hydrant and freeze a pump nameplate …` → `9. If the caller asks to **skip** hydrant and freeze a pump nameplate from density-area al…`
- Kept hard (method guardrails, not blank-gates): hydrant Adequate/no-pump → Stop; open gating RFIs + freeze FP-1 = Q@P → Stop (envelope still runs).

## NFPA cap and FM cap on the governing demand

When the demand is a combined standpipe and sprinkler greater-of (`standpipe-class-i-election-and-demand`), screen both caps on that governing flow.

- NFPA: rated flow at least demand divided by 1.5 (NFPA 20-2025 §4.10.1).
- FM, when that sheet applies: rated flow at least demand divided by 1.4. FM DS 3-7 §2.4.6.4, April 2012 with the April 2025 interim revision, limits a single 100 percent centrifugal pump to 140 percent of rated flow for combined system demand plus hose. Multiple pumps use 110 percent (§2.4.6.5). The kernel factor 1.40 sits on that cite.

An NFPA pass with an FM fail is not a closed selection. Carry the next listed size as ASSUMED. Verify with the engineer of record. Do not resize silently and do not freeze a model number. Upsizing still leaves driver horsepower, suction size, the test header, 150 percent source capacity, and fuel open.

Teaching point [SYN], envelope only, not a shop curve. Governing greater-of demand 1,055.9 gpm:

- FM minimum rated flow = 1,055.9 / 1.40 = 754.21 gpm. Check: 1.40 × 754.21 = 1,055.9.
- NFPA minimum rated flow = 1,055.9 / 1.50 = 703.93 gpm. Check: 1.50 × 703.93 = 1,055.9.
- A 750 gpm candidate is 1,055.9 / 750 = 1.408. That is an NFPA pass and an FM fail, short about 4.2 gpm.
- A 1,000 gpm candidate is 1,055.9 / 1,000 = 1.056. Both caps pass. 1,000 gpm is the ASSUMED next listed size. Availability of an 800 gpm or 850 gpm rating was not verified. It is not a scheduled pump.
- Churn system maximum stays 173 psi on both sizes. It tracks rated pressure, not rated flow, and it is 2 psi under 175. That margin is thin.

Where FM is the carrier, the FM cap governs. Options to verify with the engineer of record: the 1,000 gpm size, a carrier-accepted cut of demand to 1,050 gpm or less, or a written carrier variance. Failures: treating the NFPA 150 percent pass as enough under FM; sizing on standpipe flow when the greater-of is larger; assuming churn grows with rated flow; reading envelope net pressure as a shop curve; promoting 1,000 gpm onto a live job without that verification; applying the screen as a Canada basis. GAP-B31R1-2 stays open. No calc operation is added for it.

## Rated-pressure floor from a net demand point

When a net demand pressure is known and one or more candidate rated flows are in hand, screen the rated-pressure floor by hand. Show the arithmetic. `calcs/fp` screens a given rated flow and rated pressure. It does not select the rated pressure. Do not invent a catalog of listed pressures. Use only ratings the caller supplies.

The envelope is the line from shutoff (zero flow, churn fraction times rated pressure) through rated flow at rated pressure to 150 percent of rated flow at the 150 percent fraction times rated pressure. NFPA 20-2025 §6.2.1 requires at least 150 percent of rated capacity at not less than 65 percent of rated head. §6.2.2 limits shutoff to 140 percent of rated head. Over-pressure stays the separate §4.7.7.1 check.

The rated-pressure floor equals net demand pressure divided by the envelope factor at that flow. Above 150 percent of rated flow the point is infeasible. Pick the smallest listed candidate at or above the floor. A round trip through the envelope must meet the demand. Do not report the floor as a nameplate. Do not read or invent annex figure axis values. The screen uses none.

Teaching point [SYN]: demand 1,200 gpm at 95 psi net, candidate rated flows 1,000 gpm and 1,500 gpm, churn fraction 1.0, 150 percent fraction 0.65, listed pressures 100, 110, and 125 psi. At 1,000 gpm the demand is 120 percent of rated flow. The factor is 1 + (0.65 - 1) x (200 / 500) = 0.860. The floor is 95 / 0.860 = 110.47 psi, so the listed pressure is 125 psi. At 1,500 gpm the demand is 80 percent of rated flow. The factor is 1.000. The floor is 95 psi, so the listed pressure is 100 psi. That is the lower selection.

The result is a screen. Verify with the engineer of record. The listed shop curve governs. Do not freeze a model number. Run the FM flow cap beside this screen. An NFPA envelope pass does not close the FM cap. GAP-B31R1-2 stays open. Do not skip the FM cap because the NFPA envelope passed. This screen does not take a Hazen-Williams coefficient. Do not reopen that lock here.

## Diesel relief on an NFPA 20-2016 pin, and hose-source verdicts

On an NFPA 20-2016 basis the diesel or variable-speed relief section is §4.19.1.2. It is not §4.18. Do not copy that 2016 number onto a 2019, 2022, or 2025 job. Those editions keep §4.20.1.2, already in §7A. The arithmetic is the same on both cites: 121 percent of net shutoff, not the churn fraction, plus maximum static suction, plus a signed elevation adjustment, compared with the component rating. The default rating is 175 psi until the job's lowest listed component is pinned. `calcs/fp` `relief_check` returns that metric and labels the basis NFPA 20-2025 §4.20.1.2. It does not take an edition argument. On a 2016 pin, cite §4.19.1.2 for the same screen. Do not invent an edition switch the kernel does not have.

Annex A.4.19 body is held. Figure A.4.19.2.1 is cite-only. Do not transcribe an orifice size or a listed setpoint from the figure. Size and setpoint stay open until a vendor shop curve is in hand. The §4.27 table is not held (GAP-B37R38-1). GAP-B35R8-2 stays open on that size and setpoint.

Teaching check, inputs [ASSUMED], not a nameplate and not a municipal pressure. Maximum static suction 75 psi. Net shutoff 91 psi at a rated pressure of 65 psi: 1.21 × 91 + 75 = 185.11 psi, above 175 psi, so relief is required. Net shutoff 105 psi at a rated pressure of 75 psi: 1.21 × 105 + 75 = 202.05 psi, also required. Relief is already required at 65 psi on that maximum-churn basis. It is not only required at 75 psi and above. When the inputs are assumed, the requirement stays with the engineer of record. Do not freeze an orifice or a model number. Do not invent a municipal curve. GAP-B35R8-1 stays open.

Hose-source topologies are the fence in `hydrant-supply-curve` §21. Under the conservative assumed T2 path, 750 gpm at 65 psi fails. Net pressure needed is about 74.7 psi. Only T1a passes, and the margin is about 0.96 psi. That margin stays with the engineer of record. The 1,000 gpm alternate stays in play if hose is taken through the pump. Do not promote 750 gpm at 65 psi as the final supply under T2.

Driver derate cites on a 2016 pin stay §11.2.2.4 and §11.2.2.5. Whether those two adjustments add stays with the engineer of record. Do not invent a municipal curve. GAP-B33R8-1 stays open. This is a fence, not a design. Synthetic teaching only. Foam and clean agent stay locked.
