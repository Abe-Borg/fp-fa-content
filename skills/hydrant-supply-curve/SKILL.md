---
name: Hydrant supply curve
description: >-
  use this ideally after density-area-dry-increase has produced company-scoped
  wet/dry/DI demand (if absent, assume and flag ASSUMED) (`q_spr` / `qd_gpm` + hose + duration gallons) and you must prove (country gate US or Canada; Canada adds SI units, the NBC 2023 Alberta Edition 3.2.5.7 cross-check, and municipal DSSP rows)
  municipal/hydrant supply vs demand at the BOR from a 2-point flow test (Ps,
  Ph, Qf → N^1.85 curve, optional one-segment relocate, hose + duration) and
  return a pump need/no-need verdict — with matrix pins for
  hose/duration/currency consumed (if missing/unresolved, assume most-stringent
  and flag ASSUMED — not a stop; missing flow-test data likewise ASSUMED), SI/NI/foam/mist
  refused as BOD; not occupancy, density×area, dual-carrier BOD rebuild, listed
  pump envelope (churn/100%/150%), ITM, assignment packet, looped-main sizing,
  NFF/App-B fire-flow, or a pipe tree.
---
# Hydrant supply curve

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable data-center fire-protection recipe. **Country gate (US | Canada).** US pins below stay on a US job. On a Canada job read section 1.0. Do not port a US pin into a Canada row or a Canada pin into a US row.

**This Skill owns** proving **municipal / hydrant supply vs demand at the Base of Riser (BOR)** from a **2-point flow test** (Ps, Ph, Qf → N^1.85 curve), optional one-segment relocate, hose-aware adequacy, duration, and the **pump need / no-need verdict** that falls out of that proof.

It sits **between `density-area-dry-increase` and `pump-envelope`**. Density-area owns demand (`q_spr` + hose + duration gallons). This Skill owns the **supply curve at a common reference point** and the **yes/no pump call**. Pump-envelope owns the **listed centrifugal screen** (churn / 100% / 150%) **only after** this Skill has said a pump is needed — it is explicitly **not** a supply curve.

**Downstream water-supply order:** `density-area-dry-increase` → **`hydrant-supply-curve`** → **`pump-envelope`** (when a pump is indicated). Do not skip this Skill by jumping straight to pump selection unless the parent explicitly sequences otherwise **and** supply proof is already closed.

The shop arithmetic kernel `calcs/fp` **`hydrant`** op is the source of truth for `P(Q)`, not a hand spreadsheet. Optional `calcs/fp` **`hw`** is a **one-segment** Hazen-Williams relocate only. Do **not** expand `hw` into a pipe tree. Do **not** size looped mains. Do **not** run `pump-envelope` ops inside this Skill.

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER SUPPLY PARAMETER** (test currency, reference point, hose, duration, derate — each separately). Report the **delta vs NFPA 13-2025**. Cite **section AND edition**. Show-and-verify math. Mark invented values `[SYN]` / unpinned values `[V]`. Status vocabulary: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Consume upstream Skills; do not rebuild them. Generic — do not copy a prototype hall onto another job.

**Process guardrail (load-bearing):** pump need/no-need is a **verdict**, not a nameplate. Do **not** write `FP-1 = Q @ P`. If Inadequate on pressure → **hand off** to `pump-envelope` with this Skill’s BOR suction/supply points as inputs. If Adequate → **no pump** for the code/insurer demand (owner N+1 is Layer-3 unless a cited sheet already required it).

**Negative teaching:** (1) Do not treat AXA XL’s “design FP systems to 75–100 psi” band as the sprinkler **demand** — that envelope can flip a light HC-2 hall to “add a pump” while the computed demand still sits well under the relocated supply. Judge adequacy against **computed demand**; flag the envelope as the convention that can flip the call. (2) If the underground is schematic / N.T.S. / RFI-open, **omit `hw`** — do not invent pipe lengths. (3) A 2-point static+residual pair describes a **municipal** supply, not a pumped one.

Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.0 Country gate (US | Canada)

Required at intake: country is US or Canada. On a Canada job, name the province and the municipality, and name the adopted code (NBC 2023 Alberta Edition, BCBC 2024, or OBC 2024). An unresolved country is ASSUMED. It is not a blanket stop. Verify judgment calls with the engineer of record. On a US job the sections below are unchanged.

Run the supply calc in gpm and psi, and also report L/min and kPa. 1 gpm = 3.785 L/min. 1 psi = 6.895 kPa. The Alberta Edition floor of 3,800 L/min is about 1,004 gpm. 140 kPa is about 20.3 psi. 550 kPa is about 79.8 psi. On a municipal DSSP job the flow test comes from the servicing-standard fire-flow letter (municipal DSSP §4.2). If that letter is missing, label the test ASSUMED.

| Row | Rule (paraphrase) | Design response | Hold |
|---|---|---|---|
| NBC 2023 Alberta Edition Div. B 3.2.5.7.(1)(a) | 3,800 L/min at 140 kPa from the municipal supply | Read the supply curve at 1,004 gpm. Pass when residual is at least 20.3 psi. Where sentence (4) exempts an NFPA 13 building, still show the row | held |
| BCBC 2024 3.2.5.7.(2) | A sprinklered building, or a building with a standpipe, is deemed to comply | Do not apply the Alberta Edition numbers. Use NFPA 13 demand plus the insurer demand | held |
| OBC 2024 3.2.5.7 | Performance language only. The body is not held | Verify before use | NEEDS HOLD. Do not quote the body |
| Municipal DSSP §5.9(a) | A private-hydrant service is at least 150 mm. A leg longer than 180 m to a hydrant is looped | Loop the main. Flag a dead leg longer than 180 m | held |
| Municipal DSSP §5.9(d) | Static pressure above 550 kPa requires a pressure-reducing valve on the service | If static is above 79.8 psi, flag it. Whether that valve rule applies to the fire service is open. Verify with the municipality | text held; applicability open |
| Municipal DSSP §5.11(d) | Private hydrants are not on a separate service. They are on a service that has a constant draw | This conflicts with a dedicated fire service. Flag it to the owner and the municipality | text held; municipal confirmation open |
| Municipal DSSP §5.11(e), (f), and (l) | A hydrant is within 45 m of the fire-department connection. Public hydrants are not on private lines. A dead end does not carry two hydrants | Loop the main. Keep the standpipe arrangement consistent with these limits | held |
| Municipal DSSP §5.11(j) | The servicing standard cites "ABC 1997 §3.2.5.5" | That citation is stale. Read it as NBC 2023 Alberta Edition. Confirm it with the authority having jurisdiction | held, and flagged |
| Private hydrants, NFPA 24 | NBC 2023 Alberta Edition 3.2.5.7.(2)(b) pins NFPA 24-2013 | NFPA 24-2013 is not held. Cite NFPA 24-2022 or NFPA 24-2025 and label it the nearest edition. A BCFC pin to NFPA 24 is also not held | NEEDS HOLD |

Synthetic teaching, not a job: demand 900 gpm (0.20 gpm/ft² over 2,500 ft², plus 30 percent, plus 250 gpm hose) against a supply derated by 0.9. Residual is 63.3 psi at 900 gpm and 61.3 psi at 1,004 gpm, which is above 20.3 psi, so the cross-check is a provisional pass. That row has no system-side calculation. A pump verdict goes to `pump-envelope`. Duration is NFPA 13 plus the insurer. Do not cite ULC hours. On a Canada pin, cite NFPA 13-2019 for the demand (`density-area-dry-increase` section 1.0).

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may prove a **controlling** supply-vs-demand verdict only against demand produced for an elected company system family:

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

**This Skill does not elect families.** It handshakes with `suppression-technology-selection`, `most-stringent-basis-matrix`, and `density-area-dry-increase`. Consume their elected `wet` \| `dry` \| `double-interlock` result.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** demand to prove:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling Adequate/Inadequate / pump verdict sized as if SI/NI were company-elected.

SI/NI may appear in a **comparison / delta** column only (e.g., “if SI were allowed, density-area would have sized wet 2,500 → `qd` 750”). Comparison rows are never the controlling supply proof.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Prove supply vs consumed `qd` |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; do not control the verdict |
| Foam / foam-water | **Prohibited** | Stop; do not design or prove a foam BOD supply |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design/prove |
| Clean agent | Handoff-only | Not this Skill |
| Hybrid water/inert | Handoff-only | Not this Skill |
| Oxygen-reduction / hypoxic | Handoff-only | Not this Skill |
| Condensed aerosol / dry chemical / CO₂ | Handoff-only | Not this Skill |
| Water spray (apparatus) | Handoff-only | Route to specialist Skills |

**Foam is prohibited for company scope.** **Mist is `PRACTICE REFUSED`.** Do **not** prove a foam or mist BOD supply curve here. FM flowchart branches that mention mist do not authorize design here.

### 1.3 What this Skill calculates

| In scope | Out of scope |
|---|---|
| 2-point municipal/hydrant `P(Q)` at Effective Point → BOR | Occupancy / HC / OH classification |
| Optional one-segment `hw` relocate (known L, C, actual ID) | System-family election |
| Hose-aware adequacy at `qd`; duration check | Density × area re-calc |
| Pump **need / no-need** verdict | Dual-carrier BOD rebuild |
| Show-and-verify + `[SYN]`/`[V]`/status register | Listed churn / 100% / 150% envelope |
| Consume `qd` from density-area | Looped-main / NFF / App-B fire-flow |
| | Node-by-node pipe tree / Ch.28 schedule |

**FM DS 3-0 checked 2026-10-23d (March 2010, pull `_shared/fm-ds-3-0-hydraulics.md`):** no explicit maximum water-supply **test age** found in the sheet, so test age stays `[V]` (AXA ≤2 yr / NFPA 291 rows govern). Citable adds: §2.1.1.2 lists Water supply deterioration can be detected among test purposes (supports RFI-ing a fresh test); §3.2 / Table 3 (p.51) gives **underground** unlined cast-iron C by age and corrosiveness (e.g. 20 yr: 95 / 65 / 55 mild/moderate/severe; new 120; cement-lined 140) — use Table 3 for a lead-in `hw` C when the pipe age is known instead of inventing one.

**FM DS 3-0 scope fence:** the sheet **analyzes and rates** a supply (Adequate / Inadequate). It does **not** size the fire pump (NFPA 20), the tank (NFPA 22), or the private main (NFPA 24). Do not ask this Skill for a nameplate.

---

## 2. Required inputs and upstream intake

Caller must supply. Do **not** invent the flow test. Do **not** invent `qd_gpm`. Do **not** invent relocate geometry. Do **not** invent a system-family election.

| Input | Required | Rule |
|---|---|---|
| **Completed `density-area-dry-increase` result** | **yes** | Consume `q_spr_gpm`, `qd_gpm`, `hose_gpm`, `duration_min`, and `gallons` (when tank/break-tank). Label `qd` a **density-method minimum**. Balanced tree demand is **higher**. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Completed `most-stringent-basis-matrix` result** | **yes** (or closed pins inherited) | Consume hose / duration / test-currency / derate rows, provisional/`[V]` flags, company wet/dry/DI fence, and NFPA 13-2025 delta rows that touch those supply parameters. May inherit **closed** pins already carried on the density-area result. Dual-carrier with **unresolved** hose/duration/currency rows → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged). Do **not** rebuild the matrix. |
| **Company-elected `system_type`** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from STS / matrix / density-area. SI/NI as BOD → **Stop** (§1.1). |
| Assignment packet | preferred | Consume; do not rebuild. |
| `q_spr_gpm` | **yes** | From density-area. |
| `qd_gpm` | **yes** | Sprinkler + hose at the **BOR** (`q_spr + hose`). Canonical FM HC-2 white-space minima when so consumed: **wet 750 gpm**, **dry/DI 950 gpm**. Do **not** treat “wet/SI 750” as a company election — SI is comparison-only. |
| `hose_gpm` | **yes** | Prefer matrix-pinned or density-area value. DC white space **250 gpm** (FM) when consumed. Deducted by evaluating the curve at `qd`, not by a kernel flag. |
| `duration_min` | **yes** | Prefer matrix-pinned or density-area value. FM DC **60 min**. Do **not** import AXA XL oil/chemical **4 h**. |
| Stored volume (gal) | if tank / break-tank | Prefer density-area `gallons` (`qd × duration`; hose already inside `qd`). Continuous municipal main meets duration inherently. |
| Flow-test **Ps** (`ps_psi`) | **yes** | Static, no flow. Not given → stated `ASSUMED` value (value + why), flagged; verdict is ASSUMED-based, not verified. |
| Flow-test **Ph** (`ph_psi`) | **yes** | Residual at measured flow **Qf**. Not given → stated `ASSUMED` value (value + why), flagged. |
| Flow-test **Qf** (`qf_gpm`) | **yes** | Measured test flow. Kernel does **not** convert Pitot → Q. Not given → stated `ASSUMED` value (value + why), flagged. |
| **q table** | **yes** | At least **`[0, q_spr, qd]`**. `Q=0` must reproduce Ps. `Q=Qf` must reproduce Ph. |
| `derate` | no | Uniform multiplier on `P(Q)` (e.g. **0.9**). Owner/reliability snapshot — **not** an NFPA 13 required factor. Prefer matrix/owner pin. |
| Test **age** | **yes** | AXA XL: **≤ 2 yr** to use as current; **never use > 5 yr**. Unknown age → `[V]` / `unresolved`; run as ASSUMED-based, do not treat as verified current; NFPA 291-2025 §4.15.1 recommends (should) a 5-year hydrant test interval and sets no maximum test age (pull 291-01). |
| Test location vs **BOR** | **yes** | Same hydrant as demand / at BOR, **or** a stated hydrant→BOR run. |
| Optional relocate `length_ft`, `c`, `d_in` | **only if known** | One underground segment hydrant→BOR. **Omit if schematic / N.T.S. / RFI-open.** `d_in` = **actual internal** diameter, not nominal. |
| Optional elevation Δh (ft) | only if known | Signed. Flat / unknown → 0 and say so. |
| Optional inline device loss | only if cited | Backflow **≥ 5 psi is a screening trigger, not a value to carry.** Use a certified curve at design flow, or flag `[V]` / `[SYN]`. Never carry 5 psi as the RPZ loss. |
| BOR demand **pressure** | no | Node-by-node / layout result. If missing, report **available P at `qd`** and the bound “no-pump **if** demand ≤ P_supply(`qd`)”. Do not invent Ch.28 psi. Status: `unresolved` / `[V]` on demand pressure. |
| Controlling **carrier** | yes | `FM` \| `AXA XL` \| other named sheet. Prefer matrix pin. Dual-carrier with differing hose/duration/currency and no closed union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to most-stringent-basis-matrix. |
| **`fire-area-compartmentation-schedule` result** | **yes when** multi-hall and hall identity is needed to know **which** `qd` is being proven | Consume fire-area / hall id only. Do not design FRR. Absent on a true single-fire-area job → continue; mark fire-area intake `n/a`. Required but missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| AHJ-enforced NFPA 13 / 291 editions | yes to cite | Delta baseline **NFPA 13-2025**. Flow-test RP **NFPA 291-2025** [2025 §4.4.6 drop ≥10% (total demand §4.4.7); §4.12.1.2 flow formula, pull 291-01/291-04; 2019 §4.3.6: ≥25% drop or flow the total fire-fighting demand, pull 291-04]. Enforced ≠ latest. Prefer matrix pins. |
| Caller **output path** | **yes** for file output | Typically `<name>.calc.json` + short markdown verification. If unnamed, return results in the response and stop (do not invent a path). |

**Do not invent** a flow test, relocate L/C/ID, BFP psi, BOR demand pressure, derate presented as code, or `FP-1 = Q @ P`. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| `density-area-dry-increase` | `q_spr`, `qd_gpm`, hose, duration, gallons; density-method minimum label; elected wet/dry/DI context | Re-run density × area |
| `most-stringent-basis-matrix` | Hose / duration / test-currency / derate rows; provisional/`[V]`; company wet/dry/DI fence; NFPA 13-2025 deltas | Rebuild dual-carrier union or jurisdiction register |
| `suppression-technology-selection` | Elected wet/dry/DI (handshake); comparison-only / prohibited status | Elect a system family |
| `occupancy-hazard-fork` | Only if hall HC/OH context is still needed and missing from density-area | Re-classify occupancy |
| `fire-area-compartmentation-schedule` | Hall / fire-area id when multi-hall identity is required | Design ratings, doors, dampers |
| the input packet | Packet context when present | Rebuild the packet |

If an upstream result presents SI/NI/foam/mist as BOD → **Stop** (company scope lock — stays hard). If a required upstream result is missing, or marks a controlling hose/duration/currency/system row `unresolved` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (more stringent candidate; or run the upstream Skill first).

### 2.2 Look up by title

*Design practice*; *Water-supply analysis & the supply-vs-demand curve*; *Fire-protection hydraulics methods*; *Fire-pump selection & installation*; *Backflow preventers on fire service — selection and pressure loss*; *Needed fire-flow determination methods*; *Enforced-vs-latest edition resolver and reference pins*; shop `calcs/fp` README / `hydrant` and `hw` formulas.

---

## 3. Pin editions (cite section AND edition)

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor (hydraulics) | NFPA 13 supply + calc method | **NFPA 13-2025** delta baseline. Unamended 2024 I-Codes typically pin **NFPA 13-2022**. Licensed NFPA 13-2025 Ch.5 / Ch.28 primary is **not** in the shop codebook → `[verify vs licensed NFPA 13-2025]` / `[V]`. Method (Hazen-Williams / N^1.85 / common reference) is edition-stable. |
| Code floor (flow test) | NFPA 291 recommended practice | **NFPA 291-2025**. Section pins: Ch. 4 procedure §4.3/§4.7, drop ≥10% §4.4.6, formula §4.12.1.2 [NFPA 291-2025, pull 291-01/291-04; §4.12 Calculation Results in full, pull 291-05]; NFPA 291-2019: procedure §4.2/§4.5, 2019 §4.3.6: ≥25% drop or flow the total fire-fighting demand, pull 291-04; recommended practice (should). |
| Insurer (analysis method) | Controlling supply-analysis sheet | **FM DS 3-0**, **March 2010** (held edition — verify current → `[V]` on currency beyond Mar-2010). **AXA XL Analyzing Water Supplies (PRC.14.1.2.0)** Copyright **2020**; **Conducting Water Supply Tests (PRC.14.1.2.1)** Copyright **2020**. |
| Insurer (demand consumed) | Occupancy sheet that produced `qd` | **FM DS 5-32, January 2026** (hose 250 gpm §2.4.1.5; duration 60 min §2.4.1.6). Do not re-derive density×area here. |
| Owner | Derate / extra duration / N+1 even when Adequate | Project-issued standard. NDA → structure only. |

Inherit pins from `most-stringent-basis-matrix` when present. Always cite **section AND edition**; enforced ≠ latest.

---

## 4. Confirm prerequisites, then consume, don’t redo

1. Assignment packet exists when preferred — do not rebuild.
2. **`density-area-dry-increase` completed** — consume `q_spr` / `qd_gpm` / hose / duration / gallons; label **density-method minimum**.
3. **`most-stringent-basis-matrix` pins closed** for hose / duration / test-currency / derate (direct or inherited from density-area). Unresolved → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged.
4. Elected system is **wet \| dry \| double-interlock**. SI/NI-as-BOD → **Stop** (§1.1). Foam/mist BOD → **Stop** (§1.2).
5. Multi-hall job needing hall identity → fire-area result present; else mark `n/a`.
6. If `qd` / `q_spr` missing → run density-area first or carry a stated `ASSUMED` demand (flagged); not a Stop.
7. If occupancy classification is still missing and required to interpret the demand → run occupancy-hazard-fork or carry a stated `ASSUMED` class (flagged); not a Stop.
8. If two carriers both apply **and** hose / duration / test-currency rules differ without a closed matrix union → **not a Stop**: take the more stringent value per parameter as `ASSUMED` (flagged) or hand off to **most-stringent-basis-matrix**. Do not blend FM 60 min with AXA 4 h (oil/chemical — **does not transfer to a DC**).
9. If the caller has not named an output path → return the screen in the response and stop.
10. If the supply is already a **fire pump** (needs churn / 100% / 150%) → **Stop**. That is **`pump-envelope`**, and only **after** a need verdict from this Skill (or an already-closed supply proof the parent cites).
11. If the caller asks to **skip** this Skill and freeze a pump nameplate from density-area alone → **Stop**; order is density → **hydrant** → pump.

---

## 5. Gate the flow test **before** plotting (always)

| Gate | Rule | Cite | Status |
|---|---|---|---|
| Age | AXA XL: use **≤ 2 yr**; tests **> 5 yr must not be used**. | PRC.14.1.2.0 p.3; NFPA 291-2025 §4.15.1 recommends (should) a 5-year hydrant test interval and sets no maximum test age (pull 291-01) | `grounded` method |
| Location | **As close to the demand as possible.** General “area tests” are not a substitute. | PRC.14.1.2.0 p.3; PRC.14.1.2.1 p.1 | `grounded` |
| Same hydrant | **Do not read flow and pressure off the same hydrant.** If unavoidable, main residual ≈ **+3 psi** vs gauge — flag `[V]`. | PRC.14.1.2.1 p.3 | correction `[V]` |
| Public-main floor | Do not drop residual below **~20 psi** during the test. | DS 3-0 p.5; PRC.14.1.2.1 p.3 | `grounded` |
| Multi-source | Individual, then combined, all sources on-line. **Never** add a booster’s discharge to the municipal supply it draws from. | PRC.14.1.2.1 p.4 | `grounded` |
| Pitot → Qf | Kernel takes **Qf as an input**. Convert **outside** this Skill with **one** coefficient set: FM DS 3-0 Eq 1 `a = 29.8`, hydrant-butt **c = 0.80**; AXA PRC.14.1.2.1 `Q = 29.85·Cd·D²·√P`; NFPA 291-2025 Eq. 4.9.3a `Q = 29.84·c·d²·√p` [CODE, pull 291-03, image-read]; difference 0.03 %, below rounding; on an NFPA 291-basis report use 29.84, smooth-rounded **Cd = 0.90**. **Do not mix 0.80 and 0.90**. | DS 3-0 §2.1.1.5 p.8; PRC.14.1.2.1 pp.5–6 | `grounded` |

**Unknown test age, or age > 2 yr on an AXA job, or age > 5 yr → not a Stop:** run the curve as an `ASSUMED`-based verdict (state the test data used + why), flagged and not verified; RFI a current flow test. Status: `unresolved` until a current test is in hand.

Lead-in ≈ BOR is reasonable **unless** lead-in **> 50 ft (15 m)**, there is an elevation difference, or significant friction (e.g. **4 in.** lead-in); typical lead-in loss **< 5 psi** (PRC.14.1.2.0 p.3). If any of those fire, you owe a relocate — or you omit `hw` and flag `[V]` / `provisional`. You do **not** invent L.

### 5.1 Layer-1 AHJ supply overlays — safety factor, flow-test currency, curve adjustment (restamp 2026-10-09)

Many AHJs add a **margin** between demand and supply and a **test-age** rule on top of FM / AXA. The margin is a **pass/fail term in §10(b)**, not a demand change. Each AHJ words it differently — **pin the instrument, apply its own math, never merge neighbors' numbers, and never invent one from silence.** Corpus examples (KB *Water supply analysis and supply curve* Run-363–397, 431, 617; resolver Run-640s) — **illustrations, not defaults**:

| Form of the rule | Examples held (instrument + edition) |
|---|---|
| **Flat psi between demand and supply** | one city 10 psi (IFC-2021 one city-amended §903.3.5, guidelines Mar 2024); Arlington TX 10 psi (Construction Guide, Jun 2025); Danville VA / Prince William Co. VA 5 psi (FMO manuals 2025 / 2024); Arkansas 5 psi (AFPC 2021 §903.3.1); Minnesota ≥5 psi (Minn. R. 7511 amendment, 903.3.9) |
| **Psi at the test hydrant** | Raleigh 10 psi at the test hydrant (RFD General Information, rev 2/21/2023) |
| **Occupancy-tiered psi + low-HGL adjusted curve** | Fairfax County OFM CRP (V2 Feb 2024): A/B/F/M/S 15 psi no pump / 20 psi with pump; shift the whole curve to the low HGL |
| **Percent formula** | Anne Arundel Co. MD 15 % = (1 − P_demand/P_supply) × 100 (Bill 13-26 §13.3.1.2.2); Seattle 10 % of system design pressure at the lead-in, not on hose (AR 9.03.25, eff 2025-09-25, supersedes 9.03.20) |
| **Three-part derate** | NC State Construction Office (2020): −10 psi static, −10 psi residual, −10 % residual flow (state property) |
| **Seasonal / low-pressure shift** | Charlotte CFD 48-hour low parallel shift |
| **AHJ-conditional** | New Mexico 10 psi as mandated by the AHJ (10.25.5 NMAC §903.3.8.5, placed under limited-area sprinklers) — not shop-wide |
| **Silent (do not invent)** | Maryland State FPC, Baltimore Co., Howard Co., Gwinnett, Des Moines, San Antonio, OCFA, SFFD, Idaho, Dallas, NYC (beyond its 65 psi standpipe residual) |

**Flow-test currency also varies** (take the strictest of AHJ and carrier): Chesapeake ≤6 mo; OCFA water availability ≤6 mo; Arkansas ≤6 mo of calc submittal; Richmond DPU / Arlington / one city / Danville / PWC / one city / NYC DEP / SFFD / Anne Arundel ≤12 mo (one city high-pile ≤90 days); Raleigh ≤1 yr new / ≤3 yr existing; Minnesota ≤36 mo; Seattle SPU hydraulic-model report or same-zone flow test <5 yr. AXA ≤2 yr / never >5 yr still applies on AXA jobs.

**Method bans:** Baltimore County (Bill 14-21, NFPA 13-2016 §22.4.4.9.1 as amended) — total pressure + nominal K only; **velocity-pressure method prohibited**.

**Rule:** record `AHJ margin = <form, value, instrument, edition>` or `AHJ margin = silent (instrument checked)` in the status register. Unknown AHJ → `ASSUMED` (state which margin you assumed and why), flagged — never silently zero.

---

## 6. Design practice 3-layer on **supply parameters separately**

Do **not** MAX whole layers. Union each row; name the controlling layer.

| Parameter | Code floor | Insurer | Owner | What this method does |
|---|---|---|---|---|
| **Reference point** | Everything to a common reference (NFPA 13 hydraulic practice). | FM DS 3-0: Effective Point → **BOR** (§2.1.1.6.2). | May specify a campus node. | Compare supply and demand **at the BOR**. |
| **Curve form** | NFPA 291-2025 `P(Q)=Ps−(Ps−Ph)(Q/Qf)^1.85` [NFPA 291-2025 Eq. 4.12.1.2 is Q_R = Q_F × (h_r/h_f)^0.54 [pull 291-02; equation read from page image]; the N^1.85 form is its algebraic equivalent (0.54 = 1/1.85), not quoted text]. | Same N^1.85 as DS 3-0 Eq 25. | May require a seasonal derate on P. | Run `calcs/fp hydrant`. Two points only. |
| **Hose** | NFPA 13 hose-stream allowance `[V]` vs 13-2025 tables. | FM DS 5-32 **§2.4.1.5 (Jan-2026): 250 gpm** white space. Storage DS 8-9 can be **500 gpm** — not this Skill’s default. | May raise. | Evaluate P at **`qd = q_spr + hose`** (consumed). |
| **Duration** | Occupancy duration `[V]` vs 13-2025. | FM **60 min** (DS 5-32 §2.4.1.6). AXA **4 h / mandatory 2nd supply = oil/chemical — do not import**. | May add tank / extra minutes. | `duration = Volume / (Q_AS + Q_DEDUCT)` (DS 3-0 Eq 30). |
| **Test currency** | — | AXA **≤ 2 yr / never > 5 yr**. | May require annual. | Gate in §5. |
| **Derate** | Not a code factor. | Not FM DS 3-0. | e.g. **0.9** on P(Q). | Pass `derate` **once** (see §8). |
| **Adequacy** | Supply covers demand at the reference point. | FM: **Adequate / Inadequate** on flow **and** pressure **and** duration (§2.1.2.4.5). AXA: Good/Fair/Poor; single supply **caps at Good**. | May require N+1 even when Adequate. | Design to **insurer demand + 60 min**. Report AXA grade as **risk margin**. |
| **Pump call** | NFPA 20 sizes a pump **if** one is needed. | Add pump only if relocated supply fails demand. AXA demand **≤ 120% rated, never > 150%** is **`pump-envelope`**, after this verdict. | N+1 / diesel mandate. | **Verdict only.** No nameplate. |

**Key deltas to always print:**

- **Demand (from consumed `qd`):** FM absolute dry area **2,500 → 3,500 ≈ +40%** vs NFPA 13-2025 dry/DI **+30%** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03]. This Skill **states** that `qd` is the density-method minimum from that union.
- **Supply method:** Hazen-Williams / N^1.85 is **edition-stable** vs NFPA 13. AXA Good/Fair/Poor + 2-yr currency + 75–100 psi design band are **carrier overlay**.
- **Duration:** FM **60 min** vs NFPA occupancy duration `[V]`. Do not cite AXA 4 h as a DC requirement.

---

## 7. Run `calcs/fp/run.py` — `hydrant` is source of truth

**Kernel formula (do not hand-roll `hydrant`; use `calcs/fp`):**

```
P(Q) = Ps - (Ps - Ph) * (Q / Qf)**1.85
```

Optional `derate` is a uniform multiplier on `P(Q)`. Raw and derated are both reported. Rejects `Qf <= 0` and `Q < 0`. Exponent **1.85** is the same N^1.85 basis as FM DS 3-0 Eq 25 / NFPA 291-2025 closed form (NFPA 291-2025 Eq. 4.12.1.2 is Q_R = Q_F × (h_r/h_f)^0.54 [pull 291-02; equation read from page image]; the N^1.85 form is its algebraic equivalent (0.54 = 1/1.85), not quoted text).

Stdlib kernel. Agents **set inputs and interpret**. Paste **stdout**. QA re-runs the **same JSON**. Exit **2** on bad inputs. Transcript ends with `TRANSCRIPT_OK`. Rounding: **4 decimal places** unless the value is an integer.

FM DS 3-0 reporting convention (p.4) rounds supply **flow → 10 gpm**, **pressure → 1 psi**. Keep **kernel precision** in the transcript; apply DS rounding only on the schedule line, and say so.

**Preferred: JSON batch** (write the JSON at the **caller-named** path):

```
python3 calcs/fp/run.py path/to/name.calc.json
```

JSON shape (op `hydrant` → `hydrant_supply`):

```json
{
  "job": "<caller job id>",
  "notes": "2-point hydrant supply curve; q table 0 / q_spr / qd; derate once; not a pump envelope",
  "steps": [
    {
      "id": "supply",
      "op": "hydrant",
      "ps": 70,
      "ph": 55,
      "qf": 1600,
      "q": [0, 750, 900],
      "derate": 0.9
    }
  ]
}
```

Use the **caller job id**, never a training-job slug. Include `derate` in JSON only when the caller asked for it. The numbers 70 / 55 / 1600 / 0.9 / 750 / 900 above are **kernel README contract-demo values, not job defaults — do not copy them into another job**.

**Ad-hoc:**

```
python3 calcs/fp/run.py hydrant --ps 70 --ph 55 --qf 1600 --q 0 750 900 --derate 0.9
```

`--q` accepts one flow or a list. `--derate` optional.

**JSON / CLI aliases → formula kwargs:** `ps`/`ps_psi`/`--ps` → `ps_psi`; `ph`/`ph_psi`/`--ph` → `ph_psi`; `qf`/`qf_gpm`/`--qf` → `qf_gpm`; `q`/`q_gpm`/`--q` → `q_gpm`; `derate`/`--derate` → `derate`.

**Stdout keys:** single-q → `p_raw_psi`, `p_derated_psi`. Table → rows `q_gpm`, `p_raw_psi`, `p_derated_psi`, plus `derate`. Formula label: `hydrant/supply curve (2-point)`.

**Kernel live transcript** (contract demo only — live run of the command above):

```
CALC KERNEL TRANSCRIPT
job: (adhoc)
steps: 1

--- step hydrant op=hydrant_supply formula=hydrant/supply curve (2-point) ---
inputs
  ps_psi: 70 psi
  ph_psi: 55 psi
  qf_gpm: 1600 gpm
  q_gpm: [0, 750, 900] gpm
  derate: 0.9000
outputs
  table
    q_gpm p_raw_psi p_derated_psi
    0 70 psi 63 psi
    750 66.3074 psi 59.6767 psi
    900 64.8261 psi 58.3435 psi
  derate: 0.9000

TRANSCRIPT_OK
```

If stdout disagrees with a hand product, **the kernel wins**. Re-check inputs (especially `q` missing hose, or derate applied twice).

**Do not run** `pump-envelope`, `density-area`, or `louver` inside this Skill. `hw` is allowed **only** as §8.

---

## 8. Optional one-segment relocate (`hw`) — omit if schematic / N.T.S.

**Optional one-segment HW (relocate only):**

```
p_psi = 4.52 * L_ft * Q_gpm**1.85 / (C**1.85 * d_in**4.87)
hf_ft = p_psi / 0.4333
```

Constant **0.4333 psi/ft** is the kernel’s conversion of head loss to feet — **do not silently swap 0.433**. Elevation adjustment of the **supply** uses FM DS 3-0 Eq 2 **0.433 psi/ft** (different constant, different job).

Frame every comparison at the **BOR**. Relocate **only** when L, C, and actual ID are **known**.

```
P_BOR(Q) = P_hydrant_raw(Q) - p_hw(Q) - PE_signed - P_device[V]
PE_signed = 0.433 psi/ft × Δh # DS 3-0 Eq 2
```

**Omit `hw` when:** layout is schematic / N.T.S.; length is RFI-open; ID/material unknown. Report P at the Effective Point, flag `[V]` / `provisional` “not relocated,” and **do not invent 400 ft / 8 in / C=120**.

**Derate vs relocate:** preferred: run hydrant **raw** (no `--derate`) when relocating; subtract `hw` + PE; **then** multiply `P_BOR` by derate **once**. Never pass `--derate` **and** multiply after relocate.

C from FM DS 3-0 Appendix C **Table 3 (p.51)** by **actual** material/age. Unknown → omit `hw`. `d_in` is **actual internal** diameter. Nominal 8.0 in is `[SYN]` if used for screening.

**Ad-hoc HW** (contract demo — kernel README numbers, **not** a job main):

```
python3 calcs/fp/run.py hw --q 900 --c 100 --id 6.065 --length 200
```

Live stdout:

```
CALC KERNEL TRANSCRIPT
job: (adhoc)
steps: 1

--- step hw op=hazen_williams formula=Hazen-Williams head loss (US fire protection) ---
inputs
  q_gpm: 900 gpm
  c: 100
  d_in: 6.0650 in
  length_ft: 200 ft
outputs
  p_psi: 8.1121 psi
  hf_ft: 18.7216 ft
  psi_per_ft_water: 0.4333 psi/ft

TRANSCRIPT_OK
```

**Backflow:** DS 3-0 §3.3 “BFP ≥ 5 psi (0.34 bar)” means **count the device if it drops about that much** — it is **not** 5 psi of loss. If no certified curve → `[V]`; do not silently eat the margin with 5 psi.

---

## 9. Show-and-verify (independent of stdout)

Write the arithmetic so a reviewer can recompute without the kernel. Substitutions for the **contract-demo** numbers above:

```
P(Q) = Ps − (Ps − Ph) · (Q / Qf)^1.85

Back-check test anchors (must hold):
  P(0) = 70 − 15 · (0)^1.85 = 70 psi
  P(1600) = 70 − 15 · (1)^1.85 = 55 psi

At Q = 900 gpm (contract qd):
  900/1600 = 0.5625
  0.5625^1.85 = 0.34492659
  15 × 0.34492659 = 5.1739
  P_raw = 70 − 5.1739 = 64.8261 psi
  P_derated (0.9) = 0.9 × 64.8261 = 58.3435 psi

At Q = 750 gpm (contract q_spr):
  750/1600 = 0.46875
  0.46875^1.85 = 0.24617354
  15 × 0.24617354 = 3.6926
  P_raw = 70 − 3.6926 = 66.3074 psi
  P_derated = 0.9 × 66.3074 = 59.6767 psi
```

VERIFY: kernel table matches those five displayed pressures. If not, **kernel wins**.

Optional NFPA 291 residual-correction (no residual-correction clause found in NFPA 291-2025; §4.14 is a peak-demand caution only, pull 291-01):

```
QR = Qf · [(Ps − Pr) / (Ps − Ph)]^0.54 # exponent 0.54 ≈ 1/1.85; NFPA 291-2025 Eq. 4.12.1.2 (pull 291-02)
Q20 = 1600 · [(70 − 20) / (70 − 55)]^0.54
    = 1600 · (50/15)^0.54
    ≈ 3065 gpm
```

Hydrant “rated at 20 psi” is a **291 rating**, not the sprinkler demand point. Do not substitute Q20 for `qd`. Method is grounded; the 20 psi rating basis is NFPA 291-2025 §4.2.1 (should, advisory; pull 291-03/291-05). Edition fork: NFPA 291-2019 §4.2.1 is a different clause (tests should be made during a period of ordinary demand, pull 291-04); do not cite 2019 §4.2.1 for the 20 psi basis.

Optional one-segment HW at the same 900 gpm (contract demo):

```
p_psi = 4.52 · 200 · 900^1.85 / (100^1.85 · 6.065^4.87) = 8.1121 psi
hf_ft = 8.1121 / 0.4333 = 18.7216 ft
```

If relocating that demo: `P_BOR_raw(900) = 64.8261 − 8.1121 − PE`. Then derate once if requested. **Do not copy 8.11 psi onto a campus 8-in main.**

---

## 10. Adequacy + duration + pump need/no-need (verdict, not a nameplate)

Hose is already inside `qd`. Read the (relocated, once-derated) supply at **`qd`**, not at `q_spr`.

**(a) FLOW.** Can the supply pass `qd` above the **20 psi** public-main floor? If P(`qd`) < 20 at the main → **Inadequate** on flow.

**(b) PRESSURE.**

```
ΔP(qd) = P_supply_BOR(qd) − P_demand_BOR(qd)
ΔP > 0 → pass ΔP ≤ 0 → fail
# with a Layer-1 AHJ margin (§5.1): pass only if ΔP ≥ margin in that AHJ's own form
# flat psi: ΔP ≥ M_psi percent: (1 − P_demand/P_supply)·100 ≥ M_pct
# derate / low-HGL / seasonal shift: shift the supply curve FIRST, then test ΔP > 0
```

- If the caller **did not** supply BOR demand pressure: print `P_supply_BOR(qd)` and the bound **“no pump required for any true BOR demand ≤ P_supply(qd)”**. Mark demand pressure `[V]` / `unresolved`. Do **not** invent array friction.
- **Do not** substitute AXA XL **75–100 psi** (PRC.14.1.2.0 p.6) or the **≤ 125 psi** BOR ceiling (p.5) for `P_demand`. Those are **design-band / ceiling overlays**. Judge on **computed demand**; **flag the envelope** (`comparison-only` overlay vs design target).

**(c) DURATION** (DS 3-0 Eq 30, p.40):

```
duration_min = Volume / (Q_AS + Q_DEDUCT)
```

Required DC duration = **60 min** when consumed from FM. **Continuous municipal main** that holds `qd` above 20 psi meets 60 min inherently — **no tank required for duration**. Fail duration → **Inadequate** even if flow/pressure pass.

**(d) Carrier grade (optional overlay, not the design target).** AXA XL PRC.14.1.2.0: Good / Fair / Poor; **a single supply caps at Good**. Report the letter; **design to insurer demand + 60 min**. Status: `comparison-only` / risk margin.

**(e) Pump need/no-need — falls out of (a)–(c).**

| Verdict | What to print | What not to print | Status |
|---|---|---|---|
| **Adequate** on flow, pressure, and duration | **No fire pump required** to meet the code/insurer demand. Owner N+1 / tank = Layer-3 unless a cited sheet already required it. | No `FP-1 = Q @ P`. | `grounded` verdict when inputs grounded |
| **Inadequate** on **pressure**, duration OK | **Pump needed** (pressure, not duration). **Hand off to `pump-envelope`** with `qd_gpm` and suction/static from **this** curve only. | Do not pick `qr` / `pr`. Do not run churn/100%/150% here. | `handoff` to pump-envelope |
| **Inadequate** on pressure **and** reliability / duration | Pump **and** 2nd source or storage — still a **verdict**. | Do not size NFPA 22 / NFPA 24 here. | `handoff` |
| Inadequate on flow (cannot make `qd` above 20 psi) | Improve the **supply** (main / second source), not a booster that starves the city main. | Do not combine booster discharge with the municipal suction source. | `handoff` / supply improvement |

**Action ladder (preserve):** pressure fail → pump handoff; flow fail → improve supply (not a booster that double-counts the city main); duration fail → storage / 2nd source verdict — still not a nameplate.

AXA multiple-pump trigger **demand > 2000 gpm ⇒ multiple + ≥1 diesel** is a **flag** if `qd` exceeds 2000 — still not a nameplate (`comparison-only` / carrier overlay).

---

## 11. Status vocabulary and flags

### 11.1 Status register (required on every run)

| Status | Meaning |
|---|---|
| `grounded` | Value pinned to cited section **and** edition (or kernel stdout matching show-and-verify) |
| `provisional` | Usable only with the same caveat visible (e.g., not relocated; inherited provisional matrix row) |
| `unresolved` | Blocking open item (unknown test age treated as current; missing BOR demand psi when ΔP is forced; unresolved matrix currency row) |
| `comparison-only` | SI/NI evidence, AXA Good/Fair/Poor grade, AXA 75–100 design band, carrier preference rankings — not BOD |
| `handoff` | Work owned by another Skill (esp. `pump-envelope` after need verdict) |
| `RFI-variance` | Caller asks SI/NI/foam/mist as BOD; company-fence gate |

### 11.2 `[SYN]` / `[V]`

| Flag | Use |
|---|---|
| **`[SYN]`** | Invented flow test, invented L/C/ID, invented BFP psi, invented BOR demand pressure, invented derate presented as code, any `FP-1 = Q @ P`. |
| **`[V]`** | NFPA 13-2025 section pins (NFPA 291 pins held, pull 291-01); AHJ-enforced edition; test age unknown; same-hydrant +3 psi; lead-in > 50 ft not relocated; BFP certified curve; Ch.28 demand psi; AXA 75–100 vs computed demand; DS 3-0 March 2010 currency beyond held edition. |
| Grounded method numbers | Exponent 1.85, 0.433 psi/ft Eq 2, 20 psi floor, 250 gpm / 60 min when consumed from FM, 2-yr / 5-yr currency. Cite sheet **and** edition. |

**Fluctuation:** a single flow test is a snapshot. Ask the purveyor for seasonal/diurnal range.

---

## 12. Hand-offs (do not continue here)

**Water-supply order:** density-area → **this Skill** → `pump-envelope` (if needed).

- `qd` not yet produced → **`density-area-dry-increase`**.
- Occupancy / HC / OH missing → **`occupancy-hazard-fork`**.
- Packet missing → **the input packet** / assignment-packet.
- Dual-carrier hose/duration/currency conflict or unresolved matrix rows → **`most-stringent-basis-matrix`**.
- System-family election missing / SI/NI-as-BOD / foam / mist → **`suppression-technology-selection`** + `RFI-variance` (do not elect here).
- Multi-hall identity missing → **`fire-area-compartmentation-schedule`**.
- Verdict **pump needed** → **`pump-envelope`** (`qd_gpm` + suction/static from **this** curve only; **no nameplate here**; **no churn/100%/150% ops here**).
- Verdict **no pump** (Adequate) → stop pump path for code/insurer; owner N+1 remains Layer-3 / `handoff` if owner mandates.
- Looped-main / one-leg-out diameter → looped-main recipe (`hw` = **one** segment only here).
- Node-by-node BOR demand psi → hydraulic-tree Skill.
- Backflow assembly selection + certified curve → *Backflow preventers on fire service*.
- IFC Appendix B fire flow / hydrant spacing / NFF method election → other / AHJ (`needed-fire-flow-determination-methods`).
- Storage / receiving / staging demand (DS 8-9) → occupancy + density-area for **that** space.
- ITM / test header / drain → **`itm-design-for-testability`**.

---

## 13. Output

Write **only** to the path the **caller names** (typically a `.calc.json` transcript plus a short markdown verification). If no path is named, return results in the response and stop.

**Markdown verification** must contain:

1. Pinned editions (section **and** edition).
2. Upstream intake: density-area consume; matrix hose/duration/currency pins (or inherited closed); elected wet/dry/DI confirmed; company-fence handshake.
3. Consumed `q_spr` / `qd_gpm` / hose / duration, labeled **density-method minimum**.
4. Flow-test gate (age, location vs BOR, not same-hydrant).
5. 3-layer table for supply parameters separately.
6. Kernel command + **full stdout**.
7. Show-and-verify of `P(Q)`, including **P(0)=Ps** and **P(Qf)=Ph**.
8. Hose read at `qd`; duration; ΔP or the “no-pump if demand ≤ P_supply” bound.
9. **Pump need/no-need verdict** — not a nameplate. Envelope 75–100 psi flagged if it would flip the call.
10. Delta vs NFPA 13-2025.
11. Status register: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` + `[SYN]` / `[V]` list.
12. Explicit hand-off (density → hydrant → pump order stated).

Do **not** emit occupancy schedule, density×area re-calc, dual-carrier BOD rebuild, looped-main diameter, a pipe tree, listed churn/100%/150% envelope, or `FP-1 = Q @ P`.

---

## 14. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

Return the blocker (hard Stop only for scope-lock / wrong-Skill items). For a missing input, use a stated `ASSUMED` value (flagged) — stated, not a silent guess.

1. Missing **`qd_gpm` / `q_spr`** from density-area. Missing **Ps, Ph, Qf**.
2. Missing / **unresolved** matrix pins for hose / duration / test-currency (and not closed on the density-area inherit).
3. Elected system missing, or SI/NI / other prohibited preaction presented as **BOD** → `RFI-variance`.
4. Caller asks to elect/design/prove **foam** (prohibited) or **mist** (`PRACTICE REFUSED`).
5. Multi-hall job needing hall identity and fire-area result missing.
6. **Test > 5 yr**. **Test > 2 yr** on an AXA job presented as current. Unknown age treated as current.
7. **Inventing relocate L / C / ID** on a schematic / N.T.S. underground.
8. **Expanding `hw` into a pipe tree** or **sizing a looped main**.
9. **Describing a pumped supply with one static/residual pair**.
10. **Freezing a nameplate** (`FP-1 = Q @ P`) or running **`pump-envelope`** ops inside this Skill.
11. Skipping this Skill to jump density-area → pump without a supply verdict (unless parent cites already-closed proof).
12. **Inventing BOR demand pressure** to force ΔP.
13. **Mixing hydrant Cd 0.80 (FM) with 0.90 (AXA/291)** on a Pitot conversion.
14. **Dual-carrier** job where hose / duration / currency **differ by carrier**, without **most-stringent-basis-matrix**.
15. Combining a **booster discharge** with the **municipal supply it draws from**.
16. Caller asks to write outside the caller-named path.

---

## 15. Citations (section **and** edition)

Shop codebook **by title**.

**Grounded — FM DS 3-0 March 2010:** §2.1.1 reference point = BOR; p.4 round flow → 10 gpm, pressure → 1 psi; p.5 public-main residual ≥ **20 psi**; Eq 1 Pitot `a = 29.8`; Eq 2 elevation `0.433 psi/ft`; §2.1.1.6.1 municipal = static + residual (pump = churn/100%/150% is **not** this Skill); §2.1.1.6.2 relocate; Eq 25 N^1.85; §2.1.2.4.5 Adequate only if flow/pressure **and** duration; Eq 30 duration; Appendix C Table 3 C-factors; §3.3 BFP ≥ 5 psi = **screening trigger**.

**Grounded — AXA XL PRC.14.1.2.0 Copyright 2020:** p.3 test ≤ **2 yr** / never > **5 yr**; pp.5–6 BOR ceiling ≤ 125 psi, design FP **75–100 psi** — **overlay, not HC-2 demand**.

**Grounded — AXA XL PRC.14.1.2.1 Copyright 2020:** same-hydrant +3 psi; Cd 0.90.

**Grounded — demand consumed:** FM DS 5-32 **January 2026** hose 250 gpm §2.4.1.5; 60 min §2.4.1.6 (when consumed from density-area / matrix — not re-derived here).

**Deliberately `[V]` / `[verify §]`:**
- NFPA 291-2025 closed form = Equation 4.12.1.2 (pull 291-01; §4.12 in full pull 291-05; equation body render gap, image read in 291-03); no residual-correction clause in 291-2025.
- NFPA 13-2025 Ch.5 / Ch.28 demand-pressure floors. (Hose/duration table now held: [CODE NFPA 13-2025 Table 19.2.3.1.2, OH 250 gpm / 60 or 90 min, EH 500 / 90 or 120; lower value only with supervised waterflow + supervisory devices monitored at a constantly attended location, §19.2.3.1.3; 2019 Table 19.3.3.1.2 ranges 60–90 / 90–120; pull 13-52].)
- **Flow-test age:** test ≤12 months before working-plan submittal unless the AHJ approves otherwise [CODE NFPA 13-2016 §23.2.1.1, pull 13-17; A.23.2.1.1 drought note, pull 13-33]. 2022/2025 numbering `[V]` (pull needed). A 36-month figure is not NFPA base text; treat as a local amendment only when cited.
- Held FM DS 3-0 currency **beyond March 2010**.
- Same-hydrant +3 psi when applied as a numeric correction on an unavoidable same-hydrant test.
- BFP certified loss curve when not provided.
- Q20 hydrant rating substituted for sprinkler `qd` (never do this; if someone cites it, mark misuse).

**Absent:** licensed NFPA 13-2025 Ch.28 demand pressure; NFPA 291-2025 Equation 4.12.1.2 body (render gap, pull 291-01); current FM DS 3-0 beyond March 2010.

---

## 16. Design practice

1. Three-layer, most stringent, on **supply parameters separately**. Do not import AXA 4 h into a DC. Do not assert a fire pump from habit.
2. Delta vs NFPA 13-2025 every time. Demand context from consumed `qd`. Supply **method** is edition-stable. If the numeric 13-2025 / 291-2025 floor isn’t in the licensed primary, say **directional `[V]`**.
3. Show-and-verify. Kernel stdout + independent `(Q/Qf)^1.85` algebra, including anchors P(0)=Ps and P(Qf)=Ph. Kernel wins on arithmetic.
4. Current editions; enforced ≠ latest. Held FM DS 3-0 is **March 2010** — say so.
5. Honesty on the pump call. This Skill **proves** supply vs demand and returns **need / no-need**. It does not mint `FP-1 = Q @ P`. Schematic underground → no invented `hw`. Computed demand governs; the AXA envelope is flagged, not silently used as demand.
6. **Company fence.** Wet / dry / DI only for controlling demand. SI/NI = `comparison-only`. Foam prohibited. Mist `PRACTICE REFUSED`. Handshake — do not elect families here.
7. **Consume upstream; don’t rebuild.** Density-area + matrix pins are inputs. Status register complete every run.
8. **Order:** density → hydrant → pump. Never skip the hydrant verdict to freeze a nameplate.
9. **Cap-and-slope versus actual suction (§18).** When an adopted IFC-style §903.3.5.5 caps static above 90 psi, the sprinkler design curve is **80/45** at the test flow. Pump need, pressure-reducing valves, hangers, and suction stay on the actual test. Do not restate suction against the 45 psi design residual.

---

## 17. Not this Skill

| Work | Where it lives |
|---|---|
| Occupancy / HC / OH | `occupancy-hazard-fork` |
| Density × area `qd` / gallons | `density-area-dry-increase` |
| Dual-carrier BOD / matrix | `most-stringent-basis-matrix` |
| System-family election | `suppression-technology-selection` |
| Fire-area / FRR schedule | `fire-area-compartmentation-schedule` |
| Assignment packet | the input packet |
| Listed pump envelope (churn / 100% / 150%) | **`pump-envelope`** (next Skill **if** pump needed) |
| ITM / test header / drain | `itm-design-for-testability` |
| Looped-main / one-leg-out diameter | looped-main recipe (`hw` = **one** segment here) |
| Node-by-node BOR demand psi | hydraulic-tree Skill |
| IFC Appendix B / NFF / hydrant spacing | other / AHJ |
| Foam / mist design | prohibited / `PRACTICE REFUSED` |

---

## 18. Local cap-and-slope (IFC-style §903.3.5.5) — 80/45 versus actual suction

Teach both sentences. They feed different checks. This is a local-amendment pattern on the IFC sprinkler-supply section. Do not attach it to a city or a project name. Where the adopted instrument does not use this pattern, do not apply it.

1. **Sprinkler design curve.** Actual static above 90 psi: set design static to 80 psi and keep the original test slope. `residual_design = 80 − (Ps_actual − Pr_actual)` at the test flow. Worked `[SYN]`: test 95/60 at 1,500 gpm becomes **80/45** at 1,500 gpm. Shifting static to 80 psi and keeping the 60 psi residual (80/60) drops the design point by about 8.64 psi and is unconservative. Actual static below 90 psi: use the actual curve, with demand including hose, plus a 10 psi safety factor. Static of exactly 90.0 psi is not addressed by the two sentences: use the safety-factor branch and flag the AHJ. Verify with the engineer of record.
2. **Actual residual, including actual suction.** Actual flow-test pressures determine whether a fire pump, a pressure-reducing valve, or added hangers are required. Pump-need, pressure-reducing-valve, hanger, and suction rows use the **actual** curve. Do not restate suction against the 45 psi design residual of the **80/45** curve.
   - Show-and-verify `[SYN]`: suction at 1,500 gpm = 60 − 2.19 = **57.81 psi**. Suction at 1,113.28 gpm = actual 74.84 psi (hydrant exponent 1.85) minus 1.26 psi Hazen-Williams (8 in. Schedule 40, 80 ft, C = 100) = **73.58 psi**, which is at least 20 psi, so the suction check is ACCEPT.
3. Churn, overpressure, and component ratings use actual static, and maximum seasonal static, never the 80 psi cap (NFPA 20-2025 §4.7.7.1).
4. Worked demand check `[SYN]`: design curve at 1,113.28 gpm = 59.84 psi. Municipal supply plus a **1000@40** pump envelope (36.83 psi net) = 96.67 psi against a 47.92 psi demand, margin +48.75 psi, PASS. The rated duty itself is owned by `pump-envelope`. This skill does not freeze a maker or a model.
5. Demand times duration (1,113.28 gpm × 60 min = 66,797 gal, FM DS 5-32 §2.4.1.6) is a duration statement, not a tank size and not a local on-site storage clause. Show the product (1,113.28 × 60 = 66,796.8, reported as 66,797). Tank or storage sizing is a separate step, with its own basis. Verify with the engineer of record. List numbering under §903.3.5.5 is `[V]` until a plain-text reading of the adopted instrument confirms it.

## 19. Wet campus rollup (one fire, not a sum)

Synthetic teaching only. Do not attach it to a city or a job. Wet only. The dry and double-interlock area increase does not apply here.

Campus demand is one most-demanding remote area plus its hose (one fire), not a sum of halls. Governing flow is 750 gpm: FM DS 5-32 wet 0.20 gpm/ft² × 2,500 ft² = 500 gpm, plus 250 gpm hose. When the concealed-space trigger does not fire, governing volume is 45,000 gal (FM, 60 min, supervised) or 49,500 gal (NFPA 13-2025 ordinary-hazard group 2, 550 gpm × 90 min unsupervised, §19.2.3.1.3). State the election on the basis of design. The supply must deliver at least 750 gpm at the required pressure and at least the elected volume. Verify the supervised election with the engineer of record. When §19.2.3.1.5 also fires, use §20. The unsupervised triggered volume is 68,400 gal.

Do not sum two halls. 0.20 × 5,000 ft² + 500 gpm hose = 1,500 gpm and 90,000 gal doubles the demand. The halls are separate fire areas. Using the NFPA 1,500 ft² area when FM controls (550 gpm, below 750 gpm) is unconservative. The 3,000 ft² concealed-space trigger is owned by `density-area-dry-increase` §19 and restated as a supply target in §20. Do not copy the teaching gallons onto another site.

## 20. Supply target when the 3,000 ft² trigger or the duration election changes

Consume the demand from `density-area-dry-increase`. Do not rebuild it here. Synthetic wet campus only. Do not attach it to a city or a job. The dry and double-interlock area increase does not apply.

Read the trigger and the supervision basis together. Do not pair the 760 gpm flow with the 45,600 gal volume unless both the trigger has fired and §19.2.3.1.3 supervision is documented. Do not use 49,500 gal once the trigger has fired.

| Concealed-space trigger | §19.2.3.1.3 supervision on the basis of design | Supply |
|---|---|---|
| Does not fire | Documented | **750 gpm** and **45,000 gal** (60 min) |
| Does not fire | Not documented | **49,500 gal** (ordinary-hazard group 2, 550 gpm × 90 min). FM 750 gpm still governs flow when FM controls. This row is only the non-trigger case |
| Fires | Documented | **760 gpm** and **45,600 gal** (760 × 60). Column 2 is 0.17 gpm/ft² over 3,000 ft² plus 250 gpm hose. This flow beats the 750 gpm insurer figure |
| Fires | Not documented | **760 gpm** and **68,400 gal** (760 × 90) |

Do not take 60 min without the supervision basis on the basis of design. The code floor can beat the insurer on both flow and volume.

These gallons are a duration statement. They are not a tank size and not a local on-site storage clause. Do not sum halls. Hand the governing flow and volume through this curve. Verify the supervision election with the engineer of record.
