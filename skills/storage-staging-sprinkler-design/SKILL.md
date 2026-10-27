---
name: Storage staging sprinkler design
description: >-
 use this when a US data-center receiving / de-crate / staging / laydown /
 spare-parts area exceeds the storage trigger (>200 ft², or Class 1–3 >10 ft /
 Class 4–plastics >5 ft) and occupancy-hazard-fork has sent it off the white-space HC
 table (or you assume and flag ASSUMED) — classify commodity then read N@P (FM DS 8-9) including
 15 ft bleed, Table 14 hose/duration, wet vs dry/DI head family, and DS 7-112
 at-rest Li-ion overlay when stored/spares/damaged batteries are present —
 against company-elected wet|dry|DI only (prefer wet; packet optional; STS + matrix
 storage/carrier/commodity/hose-duration when dual-carrier + fork consumed when
 present, else ASSUMED and flagged — never a stop);
 SI/NI-as-BOD → Stop RFI-variance (comparison-only); foam prohibited; mist
 PRACTICE REFUSED; status register every run — not white-space density×area,
 not pump envelope, not installed dedicated ESS (DS 5-33), not ≤20 kWh BBU
 power-isolation, no silent N@P (state ASSUMED + why).
---

# Storage staging sprinkler design

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, deluge, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record. Do not claim a stamp.

Reusable DC fire-protection recipe. **This Skill runs AFTER an assignment packet exists and occupancy-hazard-fork has already forked the space as storage or mixed** (commodity class, **not** HC/OH). It **classifies the commodity** (FM DS 8-1) and **reads a storage design** from **FM DS 8-9**: **N sprinklers @ minimum pressure**, plus the **15 ft mixed-use bleed**, the **Table 14 hose/duration fork**, and the **wet vs dry/DI head family** — only against a company-elected **`wet` | `dry` | `double-interlock`**. When the space holds **at-rest / spare / staging / vendor-pallet / decommissioned / damaged Li-ion**, this Skill **continues here** under a **DS 7-112 overlay** on DS 8-9 / DS 2-0. It does **not** elect the suppression family, reclassify IBC occupancy / NFPA 13 OH / FM HC for the hall, convert storage to density×area, size a pump, design **installed** dedicated ESS (DS 5-33), or design ≤20 kWh distributed BBU power-isolation.

**Core thesis:** Storage is a **different FM regime** from white-space HC density×area. White-space density-area-dry-increase is **0.20 gpm/ft² over 2,500 ft² wet / 3,500 ft² dry → 750 gpm / 45,000 gal (wet)** or **950 gpm / 57,000 gal (DI/dry)** — a **density-method minimum** for HC-2 occupied space. **Do not reuse 0.20×2,500 on storage. Do not freeze campus demand on 750 / 45,000.** Storage hose/duration can **govern campus supply** (typically **500 gpm / 120 min** once the protection-table count is ≥20). Hand the priced hose + duration + (when pinned) N@P sprinkler flow to hydrant-supply-curve / pump-envelope. Those Skills consume campus `qd` **only after** this Skill has priced storage.

**DS 8-9 contains ZERO data-center content.** Held codebook was Mar 2010 / IR **Jul 2018**, 87 pp. **Opened official ungated current: Mar 2010 / IR April 2026**, 103 pp (the licensed data sheet). Re-read Tables 2–11 / hose-duration from the **Apr 2026** copy before pinning a project — do not keep Jul 2018 N@P as current. The held notes still record the Jul-2018 mine → residual `[V]` until the sheet is re-read. Every DC mapping that is not a verbatim sheet rule is **`[inference]`**.

**One worked package exists — method only (rewrite 2026-10-09).** A worked example holds *A synthetic mixed-program building — occupancy-boundary resolution incl. storage H and a spare Li-ion cage* (a synthetic mixed-program example, **`[SYN]`**): greatest-hazard boundary register, a DS 8-9 Table 3 CUP row read from **stated synthetic inputs**, Table 14 hose raised by the DS 7-112 incidental 500 gpm / 1 h rider, and the DS 7-112 five-part incidental test on a spare-module cage with a code fence (IFC 2024 / 2027 IFC Ch. 43, AHJ-conditional). Consume its **method**; its commodity, height, K, N@P and gallons are **not** defaults (and its DS 8-9 row is the Jul-2018 corpus mine → `[V]` vs Apr-2026). Do **not** invent a commodity class, a storage height, a ceiling row, a K-factor, or an N@P program “typical of DC staging.” Do not silently emit a Tables 2–11 row: when commodity / height / arrangement / STS column are not supplied, state each as `ASSUMED` (value + why, choosing the more demanding case) and flag the row ASSUMED-based. There is no shop default of “20 heads @ 7 psi.” A synthetic mixed-program Space H = fork/handoff method only (`[SYN]`); never copy as N@P defaults.

**Design practice (lede):** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union per parameter** (commodity, height, wet vs dry column, hose, duration, bleed, DS 7-112 SOC/damaged when Li-ion — each separately) → report **directional delta vs NFPA 13-2025 storage chapters** (not the OH density table). Cite **section AND edition**. Enforced ≠ latest. Show-and-verify any area / count / gallons math. Flag invented values `[SYN]` and unverified assumptions `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling water medium = **`wet` | `dry` | `double-interlock`** only (prefer **wet**); SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the optional input packet + STS wet|dry|DI + matrix storage/carrier/commodity/hose-duration rows when dual-carrier + **`occupancy-hazard-fork` required**. **DS 7-112 at-rest ownership** lives here — do **not** Stop→ESS for stored Li-ion. Caller-path-only. **NO PLACEHOLDER.**

Cite the section and the edition. Do not invent a section. Do not copy client-secret or training-ground paths into the deliverable.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill designs storage N@P, not system family)

This Skill may emit a **controlling** storage commodity / N@P / bleed / Table 14 / head-family (+ DS 7-112 at-rest overlay when Li-ion stored) package only against an elected company water medium protecting the storage space:

1. **Wet-pipe sprinkler** — **preferred** where freeze / owner do not force dry or DI
2. **Dry-pipe sprinkler** — dry columns; **SR upright 280 °F**
3. **Double-interlock preaction** — **as dry**; **SR upright 280 °F**

Comparison-only (never elected here; never the controlling storage water BOD):

- Single-interlock preaction (DS 8-9 SI wet-or-dry via DS 5-48 = **sheet language only**)
- Non-interlock preaction (sheet: as dry)
- Any other preaction type
- Hall wet/SI 750/45k comparator spines elsewhere — **company-fence conflict**; company hall comparator is **wet** (and separately DI/dry 950/57k)

**This Skill does not elect families.** It **consumes** the election from `suppression-technology-selection`, storage / carrier / commodity / hose-duration rows from `most-stringent-basis-matrix` (when dual-carrier or those rows exist), the optional input packet, and the required **`occupancy-hazard-fork`** storage/`mixed` off-HC send. Controlling BOD = `wet` | `dry` | `double-interlock` only.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling storage mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling storage N@P as if SI/NI were company-elected.
6. Do **not** continue “On SI storage…” as a controlling instruction.
7. SI/NI (including DS 8-9 §2.3.2.4 SI wet-or-dry via DS 5-48) may appear only as **`comparison-only`** evidence — never an ordinary elective Input.

**Owner-forced DI:** if owner forces DI in storage, **column becomes dry** and **heads become SR upright 280 °F**. Record the pushback; still design dry. Prefer wet unless freeze / owner force dry/DI.

**Antifreeze:** when wet is elected and freeze path is documented, antifreeze designs **as wet-pipe** (DS 8-9 §2.3.2.3) — allowed wet column, not a separate STS family.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream (prefer wet) | Emit controlling storage design |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record sheet evidence if cited; do **not** design/accept mist as storage BOD |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only special-hazard tracks | Annotate STS handoff if presented — **never** company storage water BOD |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** Sheet mist language elsewhere does **not** authorize mist as storage BOD.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| DS 8-1 three-step commodity + DS 8-9 N@P | System-family election (STS) |
| 15 ft mixed-use bleed §2.3.3.5 | White-space density×area (`density-area-dry-increase`) |
| Table 14 hose/duration from **table** N | Campus hydrant curve / pump listed envelope (hand off after pricing) |
| Wet vs dry column + QR/pendent wet-only; DI/dry = SR upright 280 °F | Installed dedicated ESS room/yard (`ess-isolation-venting-and-duration` / DS 5-33) |
| Open-frame App. A gate before ceiling-only | ≤20 kWh distributed BBU (`power-isolation-disconnect-control` / DS 5-32) |
| **DS 7-112 at-rest overlay** (SOC, incidental 5-part, packaging→CUP/CEP/UUP/UEP, damaged 0.3/room + 500/2 h, ASRS SOC gates) | Inventing commodity / height / K / N@P / “20 @ 7 psi” |
| Status register + reciprocal handshakes | In-rack valve/drain sizing (`itm-design-for-testability`) |
| Consume packet + STS wet\|dry\|DI + matrix + fork | Rebuilding packet / dual-carrier matrix / hall HC |
| Edition pins + Δ vs 13-2025 **storage** + show-and-verify | Head layout / DS 2-0 §2.5.4 install recipe (flag only) |
| Hydrant/pump hand-off of priced hose/duration/`q_spr` | Citing Jul-2018 N@P as current without Apr-2026 portal check |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** Hard-scope gate, **(b)** commodity class, **(c)** trigger/height, **(d)** arrangement/open-frame, **(e)** system column / head family, **(f)** N@P pin, **(g)** 15 ft bleed, **(h)** Table 14, **(i)** DS 7-112 / SOC when Li-ion present, **(j)** Δ vs 13-2025 storage:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling wet\|dry\|DI + edition + claim supported by **mined** DS 8-9 / DS 8-1 / DS 7-112 (when Li-ion) / caller commodity·height·arrangement already closed |
| `provisional` | Directionally pinned; edition / open-frame / SI comparison / ESFR listing (Verify with engineer of record, §3.10) / Apr-2026 table-body hole flagged `[V]` — **never silent `grounded` on invented N@P or copied hall 750/45k** |
| `unresolved` | STS / matrix / fork / commodity / height / arrangement / boundary / carrier / AHJ edition not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, DS 8-9 SI wet-or-dry via DS 5-48, hall wet/SI spines, sheet mist wording — never controlling BOD |
| `handoff` | Peer owns next action (STS family; matrix authorship then **return here**; density-area white-space; hydrant/pump after pricing; ITM in-rack valve; ESS installed; PI ≤20; fork off-HC) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD; tall DI >30 ft without §2.3.6.1 path |
| `PRACTICE REFUSED` | Mist presented as storage controlling medium — record and refuse; do not continue mist BOD |

**Unearned N@P / commodity → never `grounded`.** Unstated CUP@Xft→N@P or “typical 20@7” → never presented as a cited row; at most a stated `ASSUMED` / `[SYN]` provisional value, flagged. SI evidence → `comparison-only`. Reuse 0.20×2,500 or freeze campus on hall 750/45k → Stop. Jul-2018 cited as current without portal check → `provisional`/`[V]` at best.

### 1.5 DS 7-112 ownership block (CRITICAL — at-rest Li-ion)

**FM splits Li-ion by the STATE OF THE BATTERY, not by the building** (DS 7-112 §1.0; DS 5-32 §2.4.3.10.2; DS 5-33 §1.0(G)):

| Battery state | Sheet / Skill |
|---|---|
| **At-rest / spare / staging / vendor-pallet / construction laydown / decommissioned / damaged** Li-ion | **DS 7-112 overlay on DS 8-9 / DS 2-0 → CONTINUE HERE** |
| Installed dedicated ESS / Li-ion UPS room·yard | **DS 5-33 → `ess-isolation-venting-and-duration`** |
| Installed ≤20 kWh/rack distributed BBU | **DS 5-32 → `power-isolation-disconnect-control`** |

**Do NOT Stop→ESS for stored Li-ion.** The spares/staging room is a **storage occupancy with a battery overlay**, not an ESS room. When Li-ion at-rest is present, emit the **DS 7-112 sub-path** (Step 3.2b) inline: SOC gates, incidental 5-part escape, packaging→CUP/CEP/UUP/UEP route into DS 8-9, damaged **0.3 gpm/ft² over the room** + **500 gpm / 2 h**, ASRS SOC gates. Hand **installed** dedicated ESS to ESS Skill; hand ≤20 kWh BBU to power-isolation. Cut-off room FRR vs DS 5-33 2-hr → emit RFI / curate more-stringent; do not invent.

---

## 2. Required inputs and upstream intake

Caller must supply (or fork / matrix / STS already resolved). Do not invent commodity, height, N@P, or treat SI/NI as company BOD.

| Input | Required | Notes |
|---|---|---|
| the optional input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve a job index. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection`. Prefer wet. Antifreeze as wet column when wet elected / freeze documented. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Foam → **Stop**. |
| **Consumed `most-stringent-basis-matrix` storage / carrier / commodity / hose-duration rows** | **yes** when dual-carrier (or when those rows exist) | **Consume when present** (missing → `ASSUMED`, flagged) — do not Stop-away as if matrix replaces this Skill. Unresolved controlling storage/carrier/commodity/hose row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged (or `handoff` to complete matrix), then **return here** to price N@P/bleed/Table 14. Never silent-swap FM DS 8-9 onto an AXA-only job. |
| **`occupancy-hazard-fork` schedule** | **yes** | Consume `occupied_vs_storage = storage` or `mixed`, contents, area, ceiling height, boundary ratings. **Do not re-do IBC / OH / HC for the hall.** If the fork still assigned **HC-1/2/3** to this space → **Stop**. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| Space identity | **yes** | Receiving / dock / de-crate / staging / laydown / spare-parts / cable / filter store / in-envelope construction laydown. Use, not room name. |
| `area_ft2` of the storage arrangement | **yes** | Footprint of stored commodity. For the DS 8-9 >200 ft² test, area is bounded by **minimum 8 ft (2.4 m) aisles** (DS 8-9 §1.0). |
| Storage **height** (ft) and **ceiling / roof-deck height** (ft) | **yes** | Height of the commodity (top of storage) **and** ceiling. Different gates. Ceiling row in DS 8-9 is ceiling height, not pile height. |
| **Contents + packaging + pallet** | **yes** unless commodity class already pinned on the fork schedule | Material + internal packaging + external packaging + pallet / handling aids. A class without the pallet step is incomplete. |
| Storage **arrangement** | **yes** | `solid-piled` / `palletized` / `shelf` / `bin-box` / `open-frame rack` / `solid-shelf rack` / `portable rack` / `undetermined`. If rack: single / double / multiple-row; flue dimensions; deck type and **uniform open area %** if grated. |
| **Rated partitions** at storage↔occupied (and storage↔storage of different protection) boundaries | **yes** | Each boundary: `rated` / `unrated-open` / `undetermined` / `wall-to-wall enclosure`. Needed for the **15 ft bleed**. If mixed-use boundary **not declared** → **Stop**. |
| Controlling **carrier** | **yes** | `FM` / `AXA XL` / `none` / `dual`. Dual → **consume matrix** storage/carrier rows (see above); this Skill still owns the storage design emit. |
| ESS / Li-ion **state** in the space | **yes** if batteries are present | **At-rest / spare / staging / vendor-pallet / decommissioned / damaged → CONTINUE here under DS 7-112.** Installed dedicated ESS room/yard → **Stop** / hand `ess-isolation-venting-and-duration`. ≤20 kWh distributed BBU → **Stop** / hand `power-isolation-disconnect-control`. |
| Max received/stored **SOC** (when Li-ion at-rest) | **yes** when Li-ion present | Design input (DS 7-112). Unpinned → `[V]` / `unresolved`; do not invent ≤30 / ≤60 defaults as grounded. |
| AHJ-enforced I-Code / NFPA 13 edition | **yes** to cite the code floor | Delta reference = **NFPA 13-2025**. Enforced ≠ latest. Unamended 2024 I-Codes pin **NFPA 13-2022**. |
| Owner-standard posture for storage | **yes** (may be “none / not in hand”) | Interlock mandate in storage; assumed commodity; rated cutoff; pallet policy; max SOC for Li-ion logistics. NDA → structure-only Layer-3 that can only **raise**. |
| Caller **output path** | **yes** | If unnamed, return the design in the response and stop — do not pick a corpus location. |

Optional (do not block; flag `[V]` / `comparison-only`): aisle width; idle-pallet presence (DS 8-24); HVLS / airflow at ceiling; roof slope; open-grid ceiling/mezzanine; Scheme 8-9A segregation intent; FM field-engineer concurrence on class; IFC Ch.32 aggregation distances; SI wet-or-dry DS 5-48 comparison evidence — never controlling.

**Do not invent** a commodity class, a height, a Tables 2–11 row, a K-factor, campus `qd`, PLACEHOLDER text, or SI/NI as storage BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the optional input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve a job index |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token**; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI; treat mist/foam as BOD |
| `most-stringent-basis-matrix` | Storage / carrier / commodity / hose-duration rows when dual-carrier; company wet/dry/DI fence | Rebuild dual-carrier BOD; Stop-away forever; silent FM↔AXA swap |
| `occupancy-hazard-fork` | Storage/`mixed` off-HC send + 15 ft flag — consumed when present (else `ASSUMED`, flagged) | Re-classify white-space HC here; dismiss storage on IFC height alone |
| `density-area-dry-increase` | White-space comparator context when present | Put 0.20×2,500 / hall 750/45k on storage |
| `hydrant-supply-curve` / `pump-envelope` | Hand off **after** this Skill prices hose/duration/`q_spr` | Size pump / freeze campus before storage pricing |
| `itm-design-for-testability` | In-rack valve/drain >20 heads | Size valve/drain tree here |
| `ess-isolation-venting-and-duration` | Installed dedicated ESS reciprocal | Design installed ESS here; Stop→ESS for **stored** Li-ion |
| `power-isolation-disconnect-control` | ≤20 kWh BBU reciprocal | Design ≤20 kWh BBU isolation here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling storage/carrier/commodity/hose rows are missing when required, or occupancy-hazard-fork is missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why. Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.

### 2.2 Reciprocal handshakes (required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `occupancy-hazard-fork` | Off-HC storage/`mixed` send + 15 ft flag; white-space HC | Consume fork row; price N@P + bleed on apron; do not re-classify |
| `suppression-technology-selection` | Family election + fence status | **Consume only** wet\|dry\|DI token |
| `most-stringent-basis-matrix` | Per-parameter union / storage·carrier·commodity·hose rows | **Consume only** — then price storage here |
| the optional input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |
| `density-area-dry-increase` | White-space density×area | Storage N@P / Table 14 only — **Not** white-space |
| `hydrant-supply-curve` / `pump-envelope` | Campus curve / pump envelope | Priced hose/duration/`q_spr` hand-off **after** this Skill |
| `itm-design-for-testability` | In-rack valve/drain >20 | Flag ITM feature; do not size here |
| `ess-isolation-venting-and-duration` | Installed dedicated ESS / DS 5-33 | **DS 7-112 at-rest / spares / damaged** — **Not** installed ESS |
| `power-isolation-disconnect-control` | ≤20 kWh/rack DS 5-32 BBU path | At-rest Li-ion storage only — **Not** ≤20 BBU |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency. Do **not** rewrite peers from this Skill.

Example lines:

- `HAND OFF — occupancy-hazard-fork: storage/mixed off-HC send already required. Missing → run the fork first or proceed with `ASSUMED` (flagged), not a Stop.`
- `HAND OFF — suppression-technology-selection: wet|dry|DI election. Prefer wet. SI/NI → RFI-variance.`
- `HAND OFF — most-stringent-basis-matrix: storage/carrier/commodity/hose rows. Consume; return here after.`
- `HAND OFF — density-area-dry-increase: white-space density×area. Not this Skill.`
- `HAND OFF — hydrant-supply-curve / pump-envelope: consume storage-priced hose/duration/q_spr after this Skill.`
- `HAND OFF — itm-design-for-testability: in-rack valve/drain >20.`
- `HAND OFF — ess-isolation-venting-and-duration: installed dedicated ESS / DS 5-33. Stored Li-ion stays here (DS 7-112).`
- `HAND OFF — power-isolation-disconnect-control: ≤20 kWh BBU. Not this Skill.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before edition pins or commodity:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock` (prefer wet). SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier; occupancy-hazard-fork present. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical). Dual + missing matrix → assume the most-stringent row (flag `ASSUMED`) or hand off to complete matrix, then **return here**.
3. Emit status-register skeleton on Hard-scope / commodity / trigger-height / arrangement / column-head / N@P / bleed / Table 14 / DS 7-112-SOC (when Li-ion) / Δ 13-2025 (tokens from §1.4). Keep `[SYN]`/`[V]`/`[inference]` honesty tags **inside** status rows.
4. If Li-ion present: name battery **state** (§1.5). At-rest → continue DS 7-112 sub-path. Installed ESS → Stop/hand ESS. ≤20 kWh BBU → Stop/hand PI.

### 3.1 Pin editions (cite section AND edition)

Resolve **enforced** vs **latest** before reading any table. Format: `instrument-edition §section`.

| Layer | What to pin | Shop-pinned editions |
|---|---|---|
| Code floor | IFC high-piled (Ch.32); NFPA 13 storage family chapters; Li-ion storage per the **adopted IFC edition** (see Step 3.2c) | **IFC-2024** as adopted. **NFPA 13-2025** = delta reference. Unamended **2024 I-Codes** enforce **NFPA 13-2022**. **NFPA 13 storage chapters, IFC Ch.32, the IFC 2024 Li-ion storage section text, NFPA 855 primary text are not held** → every code-floor storage/Li-ion number is **`[V]` / `[verify vs primary]`**. |
| Insurer (this Skill’s design sheet) | FM DS 8-1 classifies; **FM DS 8-9 protects**; **FM DS 7-112** at-rest overlay when Li-ion | **DS 8-1 Apr-2014 / IR Oct-2024.** **DS 8-9 March 2010 / IR April 2026** (103 pp, official ungated) — portal re-read obligation; corpus still Jul-2018 mined `[V]`. **DS 7-112 October 2024** (first publication). Layout companion **FM DS 2-0 Oct-2021 / IR Jan-2024 §2.5.4**. |
| Insurer (hall adjacency only) | FM DS 5-32 / DS 3-26 | **DS 5-32 January 2026** — white-space comparator and mixed-use wall ratings, **not** the storage design sheet. **DS 3-26 April 2025 §2.2.5** greatest-hazard. Do **not** pull 0.2 / 2,500 / 3,500 / QR pendent into the storage row. |
| Owner | Storage interlock, cutoff, commodity assumption, pallet policy, max SOC | Project-issued. Public posture ≠ basis of design. |

Cite the section and the edition. Do not invent a section.

**Do not invent section numbers.** If a number is not in those notes or the caller’s inputs, omit it or mark `[SYN]`.

### 3.2 Confirm the occupancy-hazard-fork handoff — consume, don’t redo

Match occupancy-hazard-fork’s storage language. Do not walk IBC Ch.3, §903.2, FM Table C-1, or NFPA 13 OH for this room.

Fork already decided (quote it, don’t re-argue):

- Receiving / dock / decrating / staging / spare-parts / cable store / in-envelope laydown → **commodity class, not HC** → FM DS 8-1 → **DS 8-9**. IFC Ch.32 high-piled is a **separate** code-floor question.
- **Do not assign an HC to storage.** “The storeroom is HC-2” is a category error.
- Same room can be HC-2 when it holds **installed** gear and a commodity-classified storeroom when it holds palletized stock. Classify to the **worst configuration the room will ever see**.
- **Stored Li-ion** (spares, vendor pallets, decommissioned, damaged) → **neither** HC nor ordinary commodity alone → **DS 7-112 overlay** — **CONTINUE here** (Step 3.2b). Do **not** Stop→ESS.
- **Installed dedicated ESS** → Stop / hand `ess-isolation-venting-and-duration`. **≤20 kWh BBU** → Stop / hand `power-isolation-disconnect-control`.
- Mixed storage↔occupied: DS 3-26 **§2.2.5** and DS 8-1 **§2.4.1.1** agree — protect for the **greatest hazard**. DS 8-9 design **extends 15 ft beyond the storage edges** into mixed-use neighbors (**DS 8-9 §2.3.3.5**) — occupancy-hazard-fork **flags** that extension and **does not convert it to a density**. **This Skill prices it.**

If `occupied_vs_storage` is `occupied` (white space, electrical, NOC) → **wrong Skill** (density-area-dry-increase). If missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (state whether storage or mixed was assumed and why).

### 3.2b DS 7-112 at-rest sub-path (when Li-ion stored)

When battery state is at-rest / spare / staging / vendor-pallet / decommissioned / damaged, overlay **FM DS 7-112 Oct-2024** on DS 8-9 / DS 2-0. Where DS 7-112 states a parameter it governs; where silent, DS 8-9 / DS 2-0 survive.

1. **Name the state** (§1.5 table). Installed ESS or ≤20 BBU → hand off (do not design here).
2. **Try incidental escape (DS 7-112 §2.4.3.1)** — **ALL five** must hold: metal or cardboard boxes · **≤200 ft²** · **≤6 ft high** · **≥10 ft aisles between areas** · **SOC ≤60 %**. Miss one → full storage design (§2.4.5). Unexpanded-plastic containers with other four holding → low-piled UUP per Table 2.4.3.2 (sheet numbers — cite; do not invent as shop default). Incidental hose/duration: **500 gpm / 1 h** (§2.4.3.4/.5).
3. **Real storage (§2.4.5):** packaging picks DS 8-9 commodity — wood/metal/corrugated cellulosic or unexpanded internals → **CUP**; corrugated + expanded internals → **CEP**; unexpanded plastic external → **UUP**; unexpanded external + >40% expanded inside (or expanded external on rack table) → **UEP**. Envelope for ceiling-only commodity route: **SOC ≤60 %, ceiling ≤40 ft, storage ≤15 ft, rack ≤3 tiers, QR only**. Hard riders: **no storage above the batteries** for ceiling-only (§2.4.5.2); **≥10 ft** from other combustibles (§2.4.5.3); **≥10 ft aisles / ≤15 ft** abutted width (§2.4.5.4). Cliff: uncartoned, ceiling >40 ft, or **SOC >60 %** → commodity route withdrawn; ceiling for surrounding occupancy; in-racks per §2.4.2.2 carry design.
4. **Damaged / returned / defective (§2.4.6):** outdoors preferred, or cut-off room with direct outside access; **one pallet high** (higher ⇒ open-frame + in-racks); **0.3 gpm/ft² over the room footprint**; **500 gpm hose / 2 h**. Outdoors: ≤900 ft², ≤2 pallets high, 10 ft between piles, 10/20 ft to noncomb./comb. walls, hydrant access. Cut-off FRR vs DS 5-33 2-hr → **`[verify]` / RFI**; curate more-stringent; do not invent.
5. **ASRS (DS 7-112 §2.4.7):** SOC ≤30 % wet only; 30–60 % + metal-lined containers + horizontal loading + ceiling AND in-rack, wet only; **>60 % PROHIBITED**.
6. Status: DS 7-112/SOC row must be `grounded` only on cited § + caller SOC; else `provisional`/`unresolved`. Water cools; it does not extinguish enclosed cells (§1.1.3) — design the room to survive the batteries.

Then continue to ordinary DS 8-9 trigger / commodity / arrangement / N@P steps with the overlay commodity and hose/duration riders applied.

### 3.2c Code layer for stored Li-ion — by adopted IFC edition (corpus: ICC 2027 IFC Ch. 43 early release + ICC guidance; KB *Li-ion battery storage and staging on a DC campus* Run-624/626)

| AHJ edition | What applies to spare / staged Li-ion | Status |
|---|---|---|
| **IFC 2018 / 2021** | None of the 2024 Li-ion storage provisions. Ch. 43 arrives only by local amendment / ordinance or FCO conditions. Occupancy: get a **written BO determination (S-1)** — the 2024 IBC battery listings are absent (occupancy-hazard-fork). | FM DS 7-112 stays the quantified layer |
| **IFC 2024** (already in force) | **105.5.28 operational permit > 15 ft³ Li-ion**; **903.2.9** S-1 battery-storage sprinkler trigger; 907.2.10 detection; the IFC 2024 Li-ion storage section (§320 per the corpus reading) | section text not held → `[V]` |
| **2027 IFC Ch. 43** (pre-publication; enforce only where adopted) | **§4303.3.1 limited storage ≤ 15 ft³ per fire area**; beyond that an **indoor storage area (§4303.3.2)**: §104.2.2 technical report, **2-h fire barriers** in mixed-use buildings, sprinklers per §903.3.1.1, **ASD and/or radiant-energy detection**, §911 explosion control if the report says so. **§4303.3.2.6: demonstrated SOC ≤ 30 %** (with approved procedures) removes the report, the 2-h separation and explosion control — sprinklers and detection remain. Containment enclosures listed to **UL 1487** (§4304.10). VRLA / lead-acid / Ni-Cd spares > 15 ft³ → §4306 (≤ 25 % LFL exhaust, spill control, signage). | `provisional` / AHJ-conditional |

- **Write the SOC cap into the owner's receiving spec** — it drives both the DS 7-112 incidental / ASRS gates and the Ch. 43 §4303.3.2.6 relief.
- Batteries **installed in** their equipment are not "storage" (§4303.1); installed in-rack BBU → power-isolation / ESS Skills.
- Report each code row with the edition; never port a 2024/2027 row onto a 2018/2021 AHJ.

### 3.3 Confirm the DS 8-9 trigger (do not use the IFC height gate to dismiss storage)

Apply DS 8-9 when **any one** is true (**DS 8-9 §1.0**):

1. Class 1, 2 or 3 stored **higher than 10 ft (3.0 m)**; **or**
2. **Class 4 or plastic** commodities stored **higher than 5 ft (1.5 m)**; **or**
3. **storage of any height occupying an area >200 ft² (20 m²)**, area bounded by **minimum 8 ft (2.4 m) wide aisles**.

**`[inference]`** Every DC receiving, decrating, staging, spare-parts, cable, and in-envelope construction-laydown area is a DS 8-9 occupancy until proved under 200 ft². A pallet island clears 200 ft² with four pallets. **200 ft² ≈ 14 ft × 14 ft.**

**Two sheets, two shapes of the same trigger — curate to the more stringent.** DS 2-0 App. A defines storage-type occupancy as **200 ft² AND** 5 ft (plastic or worse) / 10 ft (cellulosic or less). DS 8-9 lists **>200 ft² at any height** as an independent third bullet. **`[verify]`** whether DS 8-9’s area bullet is genuinely independent of height. Until then: **DS 8-9 governs DESIGN**; DS 2-0’s conjoined test governs which **layout** regime (§2.5.2 vs §2.5.4) applies.

**IFC-2024 Ch.32 is a different trigger, height not area** (`[verify vs IFC-2024 primary]`): top of storage **> 12 ft** (Class I–IV) or **> 6 ft** (high-hazard). **The insurer fires first.** A 200 ft² pallet of packaged servers stacked 8 ft is invisible to IFC Ch.32 and fully inside DS 8-9. **Do not use the code trigger to decide whether you have a storage problem.**

**Portable-rack escape only (DS 8-9 §2.2.5.2.4):** storage area **≤100 ft² (9.3 m²)**, **min 8 ft clear on ALL sides**, height **≤10 ft** cartoned / **≤5 ft** uncartoned plastics → base the system on the **occupancy surrounding** the portable storage. Written for **portable racks**, not general palletized storage. Raise with the FM field engineer. Flag `[V]`.

If none of the §1.0 bullets fire and the portable-rack escape is not claimed → say DS 8-9 does not apply and hand back to occupancy-hazard-fork / density-area for the surrounding occupancy. Do not invent a storage design.

### 3.4 Classify commodity (DS 8-1) — three steps, never skip the pallet

If occupancy-hazard-fork already emitted a **sheet-attributed** class (and the pallet step was run), consume it. If the class is a habit label (“it’s just electronics”) → re-run the three steps here. **Protect to the highest hazard present, or segregate — never average** (DS 8-1 §2.4.1.1 / §3.2.1; DS 8-9 §2.2.2.2). When DS 7-112 packaging route already pinned CUP/CEP/UUP/UEP, consume that as the DS 8-9 category.

1. **Material + internal packaging** (only these count toward the plastic %). **>5% plastic by weight or volume** leaves Class 1/2/3 (DS 8-1 §2.2.4.1.B / §2.2.5.1.A). Expanded plastic: **>40% by volume**, **or >20% exposed/enveloping** (DS 8-1 §2.2.6.1).
2. **External packaging** can raise or lower (carton → CUP/CEP; plastic container drives protection). Encapsulation does **not** change class — DS 8-9 already accounts for it.
3. **Pallet:** wood / FM Approved / cardboard → no increase. **Non-FM-Approved unexpanded plastic pallet → +1 level (1→2, 2→3, 3→CUP)** (DS 8-1 §2.2.9.2). Idle non-FM-Approved plastic pallets are **UUP** and a different sheet (DS 8-24).

**State which sheet a class came from, every time.** FM deleted Group A/B/C plastics and distinct Class 4 (DS 8-1 Apr-2014). **FM “Class 4” = CUP; NFPA 13 “Class IV” is a distinct class.** Do **not** invent an NFPA↔FM mapping. DS 8-9 protection categories: **Class 1/2/3 · Class 4 + CUP · UUP · CEP · UEP**.

**`[inference, codebook-labelled]`:** treat DC receiving / decrating / staging as **plastics storage until proved otherwise**; packaged servers as **CUP at minimum, test against CEP**. Cable: **“plastic other than PVC” on wood or metal reels = CUP** (DS 8-1 Table 2.3 **item 198**). PVC on metal = Class 1 (item 194); PVC on wood/paper = Class 3 (item 195). Flag `[V]` / raise with the FM field engineer **before water-supply freeze**.

### 3.5 Arrangement gate — open-frame test / rack vs solid-pile (before any ceiling-only quote)

Every ceiling-only rack option in DS 8-9 Tables 7–11 is conditioned on **open-frame**. Run App. A **before** quoting a ceiling-only design. All must hold:

1. Unblocked transverse flues **at least every 9 ft (2.7 m)** horizontally, **throughout rack height**.
2. No blocked transverse flue. Net **< 3 in. (75 mm)** is not a flue (§2.2.3).
3. Solid shelves only if **fixed-in-place**, **≤20 ft² (2.0 m²)**, and **not blocking a transverse flue**.
4. Grating **≥70% uniformly open**; slats fixed-in-place with flues between all pallet loads.
5. Multiple-row with butted storage: extra flue geometry.

**Closing rule, verbatim:** if rack storage does not meet the guidelines, **treat it as if it has solid shelves.** Fail aligned 3 in. flues → **>64 ft² solid-shelf** case → in-racks **at every tier** (§2.2.3.1.4).

**`[inference]`** DC failure modes: welded wire deck below 70% open; butted pallets in a receiving/laydown row; cable reels / irregular spares creating shielded areas. **`[verify]`** deck open area with the rack vendor, in writing.

If arrangement is `undetermined` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; assume the more demanding arrangement, never open-frame merely because the drawing says “rack.”

### 3.6 System column → wet vs dry AND head family (consume STS; comparison-only SI footnote)

**Controlling path — STS `wet` | `dry` | `DI` only:**

| STS election | DS 8-9 design basis | Head family (ceiling storage) |
|---|---|---|
| Wet-pipe | wet columns | QR **and** pendent **allowed** (QR / pendent = **wet/antifreeze only**, §2.3.3.2.4 / §2.3.3.2.6) |
| Wet + antifreeze (freeze documented) | **as wet-pipe** (§2.3.2.3) | same as wet |
| **Double-interlock preaction** | **as DRY** | **SR upright 280 °F** |
| Dry-pipe | dry columns | **SR upright 280 °F** |

**Comparison-only footnote (never ordinary Inputs / never controlling BOD):** DS 8-9 sheet language that **single-interlock** may be wet OR dry by ceiling heat-detector spacing per **DS 5-48** (§2.3.2.4), and that **non-interlock** designs as dry, is **`comparison-only`** under company fence. SI/NI-as-BOD → **Stop** `RFI-variance` (§1.1). Do not silent-swap DI.

**Load-bearing head rule:** DS 8-9 §2.3.3.2.4 QR only on wet/antifreeze; §2.3.3.2.6 pendent only on wet/antifreeze; §2.3.3.2.3 **280 °F upright** on dry / preaction-designed-as-dry. **A double-interlock storage area is SR upright 280 °F.** Mixing QR and SR in the same protected area needs a clear delineation and, in the same-elevation or QR-higher cases, **a draft curtain** (§2.3.3.6.5).

Temperature (wet): **160 °F**; **212 °F when ambient exceeds 100 °F (38 °C)**, designed as 160 °F (§2.3.3.2.2). DS 5-32 white space is **QR pendent, 135 °F wet / 165 °F dry** — **do not import**.

**Dry columns in Tables 2–11 stop at 30 ft** for every commodity band. Ceiling-only dry above 30 ft is **§2.3.6.1 only**: Class **1/2/3**, ceilings **>30 to 55 ft**, SR upright 280 °F — **double-interlock is NOT in that list.** Campus-standard DI cannot use the only over-30-ft ceiling-only dry option. **RFI to FM** before committing a tall logistics building to DI (`RFI-variance`).

Owner mandate: if owner forces DI in storage, **column becomes dry** and **heads become SR upright 280 °F**. Record the pushback; still design dry. Prefer wet.

### 3.7 Read N sprinklers @ min pressure — not density×area. Interpolation forbidden.

**Design form (DS 8-9 §2.3.3.7):** **“N sprinklers @ minimum pressure.”** **“Do not interpolate or make adjustments to the values listed in these tables.”** (§2.3.3.7.2)

- You may use **any table ceiling-height row equal to or higher** than the actual ceiling, and a higher row if it is hydraulically better.
- **Do not** convert an FM row to gpm/ft² and compare it to NFPA 13.
- **Do not** apply density-area-dry-increase’s kernel. FM storage **has no dry-pipe design-area penalty**. Appendix B, January 2008: tables subdivided into wet vs dry, *“it is no longer necessary to make an adjustment due to the presence of a dry-pipe sprinkler system.”*

**No default program.** Required keys to open a row: **commodity category** × **ceiling height** × **arrangement** × **wet vs dry column (from STS)** × aisle if the table asks. If any key is missing → **not a Stop**: state the missing key as `ASSUMED` (value + why, more demanding case) and flag the N@P number ASSUMED-based; you may still emit trigger, class, bleed, head family, and the Table 14 **fork** (as a function of N). Status on N@P = never `grounded` without a cited row.

**Trap — 768 ft² floor with hose carve-out (§2.3.3.7.2.3):** minimum design area **768 ft² (71 m²)** = sprinklers × spacing. Increase the sprinkler count to reach it — **but Table 14 hose and duration are read from the count in the PROTECTION TABLE, not the increased count.**

**In-racks become mandatory** (§2.3.4.2) when ceiling tables offer no option, water supply cannot support any ceiling-only option, or solid-shelf / open-top-container gates fire. Table 12 in-rack numbers: Class 1–3 → **6 @ ≥22 gpm** (1 level) / **10 (5 on 2 levels) @ ≥22 gpm**; Class 4 and plastics → **8 @ ≥30 gpm** / **14 (7 on 2 levels) @ ≥30 gpm**; min pressure **7 psi**; min **K8.0** when design flow exceeds 30 gpm. Ordinary in-rack **balancing**: balance with ceiling demand **at the point of connection** — **not** a sum at the source. **Do not run the tree here.** (DS 7-112 in-rack path is unbalanced suppression-mode — ceiling demand excluded; cite §2.4.2.2 when that overlay applies.)

**In-rack separate control valve and drain** above **20 in-rack heads** is an **ITM / design-for-testability feature**, not this calc. Hand off to **itm-design-for-testability**.

Ceiling storage K-family starts at **K11.2** (DS 2-0 Table 2.5.4.1.1). There is **no K5.6/K8.0 storage sprinkler**. Layout numbers (100 ft² max area spacing, obstruction exemption **2 ft not 4 ft**, slope penalty **+50% not +30%**, open-grid ceilings **prohibited**) are **DS 2-0 §2.5.4** — flag as buildability constraints; do not lay out heads in this Skill.

### 3.8 Fifteen-foot bleed into mixed-use / neighbors (this is the finding that costs money)

**DS 8-9 §2.3.3.5:** extend the storage hydraulic design **≥15 ft (4.5 m) beyond all edges of the storage, or to a wall, whenever there is mixed-use occupancy**. Where two adjacent storage occupancies are protected differently, **extend the higher-hazard design 15 ft into the lower-hazard area.**

A storage room is **not** hydraulically contained by its own walls unless there *are* walls.

**`[inference]`** Wall and door the staging area, or it re-rates a **15-ft apron** of whatever it touches — **including white space**. Occupancy-hazard-fork already flagged this and refused to convert it to a density. **This Skill applies the storage N@P (and Table 14 hose/duration) on that apron**, not HC-2 0.20×2,500.

**Hall adjacency (DS 5-32 is the neighbor’s sheet, not this design sheet):** DS 5-32 **§2.2.4 (Jan-2026):** **1-hr** walls (DP/network/tape/generator); **2-hr** between multiple DP rooms. A **rated** storage↔hall partition is what lets the hall **keep** HC-2 density×area on its side of the wall. Unrated / open → greatest hazard (DS 3-26 §2.2.5) **plus** the 15 ft storage-design extension.

Show the bleed in plan-words: storage footprint + 15 ft or to wall, using **declared** boundary ratings. If a boundary is `undetermined` → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; assume `unrated-open` (the bleed applies) unless told otherwise.

### 3.9 Hose / duration fork (Table 14) — this can govern CAMPUS supply

**DS 8-9 Table 14, standard spacing:**

| Protection-table sprinkler count | Hose | Duration |
|---|---|---|
| **≤12** | **250 gpm** | **60 min** |
| **13–19** | **500 gpm** | **90 min** |
| **≥20** | **500 gpm** | **120 min** |

Most DC-plausible storage designs are **20+ sprinkler** designs → **500 gpm for 120 min**, against DS 5-32 white-space **250 gpm / 60 min**. DS 7-112 damaged / many overlay regimes attach **500 gpm / 2 h** — can exceed Table 14; use the more stringent when overlay applies.

**Read hose/duration from the PROTECTION TABLE count, not the 768 ft² padded count.** If N is not yet pinned, **state the fork** and **do not freeze** campus hose at 250.

**Do not freeze campus demand on hall 750 gpm / 45,000 gal (wet).** Storage can exceed it on **hose alone** (500 vs 250) and on **duration alone** (120 vs 60), before sprinkler N@P is added. Size the storage case in the **campus water-supply concept at schematic design, not at permit.** Hand priced `hose_gpm` + `duration_min` + (when N@P exists) sprinkler flow to **hydrant-supply-curve / pump-envelope**.

Show-and-verify gallons **only** when `q_spr` is pinned from a cited table row:

```
qd = q_spr + hose_gpm # hose at the demand point
gallons = qd × duration_min # hose already inside qd
```

If N@P is unpinned, write the hose/duration fork and carry gallons from a stated `ASSUMED` N@P (value + why), flagged. Do not silently derive `q_spr` from an unstated K√P.

**Water delivery — name the instrument.** DS 8-9 §2.3.2.5: **40 s** to the most remote **4 sprinklers (2 on 2 lines)** unobstructed; **60 s** single-sprinkler cut-off. Hall (DS 5-32) is **≤30 s to the most remote sprinkler**. **`[inference]`** If a single riser feeds hall + storage, the **hall’s 30 s governs the shared system.** Do not quote “40 seconds” as the DC delivery requirement.

### 3.10 Code-side family (ESFR / CMSA / CMDA) — seedling; do not silently pick ESFR

Look up by title: *Storage sprinkler families — ESFR/CMSA/CMDA and in-rack* (**status: seedling**). **NFPA 13-2025 storage primaries now partly held (2026-10-22):** Ch. 21 CMDA / Ch. 22 CMSA / Ch. 23 ESFR (TOC + Table 22.2, 22.4, 23.3.1 titles, pull 13-43); CMDA palletized/solid-piled >12 ft: Table 21.2.2.1.1 densities over **2,000 ft²** (e.g. 12–15 ft ordinary temp: Class I 0.15, II 0.16, III 0.20, IV 0.27) [CODE NFPA 13-2025 §21.2, Table 21.2.2.1.1, pull 13-55]; temperature rules §21.1.6.1–21.1.7, K-11.2+ area reduction 25% not below 2,000 ft² §21.3.3.1(2)(b) [pull 13-53]; ESFR spacing 12 ft (≤25 ft storage / ≤30 ft ceiling) else 10 ft, ≥8 ft, ≥4 in. from wall, temp ordinary/intermediate §14.2.8.1, §14.2.8.3–.4, §14.2.5 [pull 13-14]. **Low-piled / miscellaneous ≤12 ft** stays on occupancy-hazard density, max area 3,000 ft²; miscellaneous ≤10% of building or 4,000 ft² [CODE NFPA 13-2025 §4.3.1.4–4.3.1.8, §20.1.1, pull 13-56] — this is the normal DC staging case. Table cell values beyond the quoted rows and all IFC Ch.32 trigger text stay **`[verify]`**, except ESFR system type [CODE NFPA 13-2022/2025 §14.2.2 (ESFR system-type limit; other system types only if specifically listed), pull 13-10] and CMSA system type [CODE NFPA 13-2025 §13.2.1.3 / 2022 §13.2.2 (CMSA system types, per listing), pull 13-10].

**ESFR vs preaction collision — now code-cited** [CODE NFPA 13-2022/2025 §14.2.2 (ESFR system-type limit; other system types only if specifically listed), pull 13-10]; [CODE NFPA 13-2025 §13.2.1.3 / 2022 §13.2.2 (CMSA system types, per listing), pull 13-10]. A 2023 trade source states **ESFR is listed for use in wet systems only**; **CMSA is permitted on wet, dry OR preaction**. If that holds, **ESFR is unavailable in any preaction envelope** — the normal hyperscale in-building de-crate / staging case. **Verify with engineer of record — ESFR on dry/DI:** conservative assumption = no ESFR behind a dry or DI valve unless a dry/preaction listing for that head is cited (§14.2.2); no cited listing → **Stop + RFI-variance**; CMSA is the default family. The rule is §14.2.2 (Ch. 14), not Ch. 23 (pull 13-10); check the **head’s listing** for any specific listing. FM already constrains the head from the other direction (QR/pendent wet-only; dry = SR upright 280 °F).

**NFPA 13 storage density/area curves are not in the corpus** — cannot compute a numeric code-vs-FM delta. Report **directional** only: FM designs N@P with interpolation forbidden; NFPA 13 storage is a different instrument (family chapters post-2019: CMDA / CMSA / ESFR, not the OH density table).

### 3.11 Design practice 3-layer union — per parameter, not per layer

Do **not** MAX whole layers. Union each row; name the controlling layer.

| Parameter | Code floor | Insurer (FM) | Owner | What this method does |
|---|---|---|---|---|
| **Commodity** | IFC Ch.32 / NFPA 13 Class I–IV + Group A/B/C [CODE NFPA 13-2022/2025 §20.4.1–§20.4.4 (Class I–IV), §20.4.5 (plastics groups), pull 13-10] | DS 8-1 three-step class; highest hazard; FM Class 4 = CUP; DS 7-112 packaging→CUP/CEP/UUP/UEP when Li-ion | May assume a class or force segregation | State the **sheet**. Never average. |
| **Height / trigger** | IFC **>12 ft / >6 ft** high-hazard `[V]` | DS 8-9 **>10 / >5 / >200 ft²**; DS 7-112 incidental ≤6 ft / ≤200 ft² | May restrict pile height / SOC | Insurer fires first. |
| **Wet vs dry** | NFPA 13 dry/DI **+30% area** [CODE NFPA 13 2025 §19.2.3.2.6 / 2022 §19.2.3.2.5 / 2019 §19.3.3.2.5, pull 13-03] — **wrong instrument for FM storage** | DS 8-9 **separate wet/dry tables**; DI = **dry**; QR/pendent **wet-only**; dry = **SR upright 280 °F**; SI wet-or-dry = **comparison-only** | May **force DI → dry column + SR 280 °F** | Consume STS; fork column and head family. Do not add +30% to an FM row. |
| **Hose** | NFPA 13 hose-stream `[V]` | Table 14: **250 / 500 / 500** by table count; DS 7-112 damaged **500 gpm** | May raise | Read from **table** N. Can **govern campus**. |
| **Duration** | Occupancy duration `[V]` | Table 14: **60 / 90 / 120 min**; DS 7-112 often **2 h** | May add tank / minutes | Can **govern campus tank**. Do not freeze 60 min from the hall. |
| **Bleed** | IFC aggregation / 1-hr or 100 ft `[V]` | **§2.3.3.5 ≥15 ft** into mixed-use or into the lower-hazard storage | May require a rated cutoff | Rated wall **or** 15 ft apron of storage design. |
| **Li-ion SOC / damaged** | IFC 2024 105.5.28 / 903.2.9 / Li-ion storage section; 2027 IFC Ch. 43 §4303 where adopted; NFPA 855 `[V]` | DS 7-112 SOC gates; incidental 5-part; damaged **0.3 over room + 500/2 h** | Max received SOC in logistics spec | Own at-rest here; hand installed ESS / ≤20 BBU. |

### 3.12 Show-and-verify

```
# Trigger (DS 8-9 §1.0)
height_gate_class123 = storage_height_ft > 10
height_gate_plastics = storage_height_ft > 5 # Class 4 / plastics
area_gate = storage_area_ft2 > 200 # 8-ft aisle bounding
ds89_applies = height_gate_class123 OR height_gate_plastics OR area_gate

# Bleed (DS 8-9 §2.3.3.5)
# If mixed-use and no wall: hydraulic design extends ≥15 ft beyond all storage edges.

# Table 14 — use PROTECTION TABLE count, not 768 ft² padded count
# ≤12 → 250 gpm / 60 min; 13–19 → 500 / 90; ≥20 → 500 / 120

# DS 7-112 when Li-ion at-rest (cite Oct-2024 §§)
# incidental_5part = metal/cardboard AND area≤200 AND height≤6 AND aisle≥10 AND SOC≤60
# damaged → 0.3 gpm/ft² over room + 500 gpm / 2 h

# Gallons only if q_spr is pinned from a cited N @ min pressure row
# qd = q_spr + hose_gpm
# gallons = qd * duration_min

# Do NOT:
# q_spr = 0.20 * 2500 # hall density×area — forbidden here
# interpolate between table rows
# invent CUP @ X ft → N@P / "20 @ 7 psi"
# Stop→ESS for stored Li-ion
```

### 3.13 Honesty tags (inside status rows)

| Tag | Use |
|---|---|
| **`[SYN]`** | Invented commodity, height, N@P row, K-factor, q_spr from guessed K√P, campus `qd` copied from hall 750/45,000, invented NFPA↔FM class map, synthetic mixed-program Space H copied as N@P default. |
| **`[V]`** | IFC Ch.32 / IFC 2024 Li-ion storage section (§320 per corpus) / 2027 Ch. 43; NFPA 13-2025 storage chapters / ESFR wet-only listing (system type cited §14.2.2, pull 13-10; head listing must be cited, else Stop + RFI-variance, Verify with engineer of record); DS 8-9 Apr-2026 table body vs Jul-2018 corpus; SI wet-vs-dry via DS 5-48 (comparison-only); packaged-server CEP test; wire-deck 70% open; DS 7-112 cut-off FRR vs DS 5-33 2-hr. |
| **`[inference]`** | Every DC consequence of DS 8-1 / DS 8-9 / DS 7-112 (those sheets have **zero** or near-zero DC content). Label it in the output. |
| Grounded FM pins | §1.0 trigger; §2.3.3.5 15 ft; §2.3.3.7.2 no interpolation; Table 14 250/60 · 500/90 · 500/120; QR/pendent wet-only; dry SR 280 °F; open-frame App. A; DS 7-112 Oct-2024 SOC / incidental / damaged. Cite **section AND edition**. |

---

## Output

A **storage sprinkler design memo**. Write **only** to the path the **caller** names. If unnamed, return the memo in the response and stop.

Must contain: Hard-scope / company-fence / status register; pinned editions (DS 8-9 Apr-2026 pin + Jul-2018 corpus-[V]; DS 7-112 Oct-2024 when Li-ion); consumed packet + STS wet|dry|DI + matrix (when dual) + occupancy-hazard-fork fields; trigger test; three-step commodity (or DS 7-112 packaging route); open-frame test; 3-layer table; head family from STS column; N@P from a **cited** row **or explicit Stop** on the number; 15 ft bleed; Table 14 from **table** count; DS 7-112/SOC status when Li-ion; ESFR/preaction Verify with engineer of record (no ESFR on dry/DI without a cited listing → Stop + RFI-variance); show-and-verify; directional Δ vs NFPA 13-2025 **storage**; status + `[SYN]` / `[V]` / `[inference]` register; hand-off to hydrant/pump (storage-priced hose/duration).

Do **not** emit: hall HC/OH schedule, density×area `qd`, pump nameplate, rebuilt dual-carrier matrix, rebuilt assignment packet, in-rack valve sizing, fabricated Tables 2–11 program, SI/NI as controlling BOD, or Stop→ESS for stored Li-ion.

---

## Stop

A missing input is not a stop. Proceed with a stated ASSUMED value (the value and why), flagged in the output and the status register. Company scope locks stay hard stops: single-interlock or non-interlock as the basis of design, foam, water mist, deluge, and clean agent as the basis of design.

1. Occupancy-hazard-fork missing, or `occupied_vs_storage` not `storage`/`mixed`, or fork still assigned **HC** to this space.
2. Assignment packet missing, or STS wet|dry|DI election missing / `unresolved`.
3. Dual-carrier with missing/unresolved matrix storage/carrier/commodity/hose-duration rows (complete matrix, then **return here** — do not Stop-away forever).
4. SI/NI (or other prohibited preaction) presented as **basis of design** → `RFI-variance`. Foam-as-BOD → Stop. Mist-as-BOD → `PRACTICE REFUSED`.
5. Trying to **reclassify IBC / OH / HC** for the hall.
6. Trying to **reuse 0.20×2,500 / 3,500** or freeze campus demand on **750 gpm / 45,000 gal**.
7. Missing commodity inputs and no sheet-attributed class on the fork schedule.
8. Missing storage height, ceiling height, or arrangement.
9. Mixed-use / storage↔occupied boundary **not declared**.
10. Unpinned carrier.
11. **Installed dedicated ESS** presented for design here → hand `ess-isolation-venting-and-duration`. **≤20 kWh distributed BBU** → hand `power-isolation-disconnect-control`. (Stored Li-ion → **do not Stop**; continue DS 7-112.)
12. **Interpolating** table rows, converting N@P to a density, or inventing a commodity/height/N@P default program (including “20 @ 7 psi”).
13. **Selecting ESFR** in a preaction / DI envelope without a cited dry/preaction listing (Verify with engineer of record; Stop + RFI-variance) [CODE NFPA 13-2022/2025 §14.2.2 (ESFR system-type limit; other system types only if specifically listed), pull 13-10].
14. **Ceiling > 30 ft on dry/DI** without a cited §2.3.6.1 path — and DI is **not** on that path.
15. Citing **Jul-2018** N@P as current without Apr-2026 portal check.
16. AXA-XL / `none` job asking for a **numeric NFPA 13 storage density/area** — those curves are **not in corpus**.

---

## Citations (section AND edition)

Cite the section and the edition. Do not invent a section. **FM DS 8-1 Apr-2014 / Interim Rev Oct-2024:** three-step class; >5% plastic; pallet +1 level; Table 2.3 item 198 non-PVC cable = CUP. **FM DS 8-9 March 2010 / Interim Rev April 2026** (design pin; portal re-read): §1.0 trigger; §2.3.3.5 ≥15 ft bleed; §2.3.3.7.2 no interpolation; Table 14 hose/duration; QR/pendent wet-only; dry SR 280 °F; Table 12 in-rack; §2.3.6.1 dry >30–55 ft Class 1–3 only (DI not listed). Corpus mine still **Jul-2018 / 87 pp** → `[V]` until remine. **Zero DC content — DC consequences = `[inference]`.** **FM DS 7-112 October 2024** (first publication): at-rest Li-ion overlay — §1.0 state split; §2.4.3 incidental 5-part; §2.4.5 packaging→CUP/CEP/UUP/UEP + SOC ≤60 % envelope; §2.4.6 damaged 0.3 gpm/ft² over room + 500 gpm / 2 h; §2.4.7 ASRS SOC gates. **FM DS 2-0 Oct-2021 / Jan-2024 §2.5.4:** storage K from K11.2; obstruction 2 ft; slope +50%. **FM DS 5-32 January 2026:** hall adjacency only — do not design storage from this sheet; §2.4.3.10.2 routes stored Li-ion to DS 7-112. **FM DS 5-33:** installed ESS only — Not this Skill. **NFPA 13-2025** storage family chapters: delta reference, **no primary in corpus**. **IFC-2024 Ch.32 / 105.5.28 / 903.2.9 / Li-ion storage section; 2027 IFC Ch. 43 §4303 (ICC early release, pre-publication); NFPA 855:** `[verify vs primary]`.

**Corpus honesty:** one storage/spares worked package (a synthetic example mixed-program, 2026-10-05) = **method only `[SYN]`** (its N@P row rests on stated synthetic inputs and the Jul-2018 DS 8-9 mine); synthetic mixed-program Space H fork method `[SYN]`; refuse invent CUP@Xft→N@P; SI spines elsewhere = comparison-only; company wet|dry|DI fence imported from peer bar (not inside storage KB notes).

---

## Design practice

1. **Company fence.** Controlling BOD = wet | dry | double-interlock only (prefer wet). SI/NI → Stop `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. Do not invent SI/NI as storage BOD.
2. **Status vocabulary every run** on Hard-scope, commodity, trigger/height, arrangement, column/head, N@P, bleed, Table 14, DS 7-112/SOC when Li-ion, Δ 13-2025. Unearned N@P never `grounded`.
3. **Upstream (packet optional; gaps → `ASSUMED`, not a Stop).** Packet + STS wet|dry|DI + matrix storage/carrier/commodity/hose when dual-carrier + occupancy-hazard-fork — **consume**; dual missing matrix → unresolved then **return here**.
4. **Three-layer, most stringent, per parameter.** FM DS 8-9 (and DS 7-112 when at-rest Li-ion) is the design sheet on an FM job. Owner can force DI (dry column, SR 280 °F) or a rated cutoff that **stops** the bleed.
5. **DS 7-112 at-rest ownership.** Stored / spare / staging / damaged Li-ion **continues here**. Installed ESS → ESS Skill. ≤20 kWh BBU → power-isolation. Do **not** Stop→ESS for stored Li-ion.
6. **Delta vs NFPA 13-2025 storage — directional, not the OH density table.** FM: N@P, interpolation forbidden, separate wet/dry tables (no +30% area lever). NFPA 13 storage curves **not in corpus** — **delta UNMEASURED**; say so.
7. **Show-and-verify.** Trigger, 15 ft bleed, Table 14 from **table** N, gallons only from pinned `q_spr + hose`. Apr-2026 portal re-read before pinning Jul-2018 numbers as current.
8. **Honesty — one `[SYN]` worked package (a synthetic example), method only. NO PLACEHOLDER.** Do not invent CUP @ X ft → N@P. `[inference]` every DC mapping. Caller-path-only.
9. **Campus supply.** Hall 750/45,000 (**wet**) is a **white-space minimum**. Storage Table 14 **500 gpm / 120 min** (or DS 7-112 500/2 h) can **govern**. Hand off; do not freeze.

---

## Not this Skill

| Work | Where it lives |
|---|---|
| IBC occupancy / §903.2 / NFPA 13 OH / FM HC for the **hall** | occupancy-hazard-fork |
| White-space density×area (0.20×2,500/3,500, 750/45,000 wet / 950/57,000 DI/dry) | density-area-dry-increase — **do not reuse on storage** |
| System-family election wet\|dry\|DI | suppression-technology-selection — **consume only** |
| Dual-carrier per-parameter authorship | most-stringent-basis-matrix — **consume**, then return here |
| Assignment packet authorship | the optional input packet — **consume only** |
| Campus hydrant curve / pump listed envelope | hydrant-supply-curve / pump-envelope — consume storage-priced hose/duration **after** this Skill |
| In-rack separate valve/drain | itm-design-for-testability |
| **Installed dedicated ESS** room/yard (DS 5-33) | ess-isolation-venting-and-duration — **Not** at-rest storage |
| **≤20 kWh** distributed BBU (DS 5-32) | power-isolation-disconnect-control |
| Head layout, 2 ft obstruction, slope +50% | DS 2-0 §2.5.4 install recipe |
| Pipe tree, K√P balance, C-factor | hydraulic-tree Skill (not written) |

---

## Check sequence

0. **Hard scope + status register first.** STS = wet|dry|DI (prefer wet). SI/NI → Stop `RFI-variance`. Foam → Stop. Mist → `PRACTICE REFUSED`. Packet (optional) + STS + matrix (when dual) + fork present. Emit status skeleton (§1.4).
1. **Li-ion state split.** At-rest / spare / staging / damaged → **CONTINUE** DS 7-112 sub-path here. Installed ESS → hand ESS Skill. ≤20 kWh BBU → hand power-isolation. Do **not** Stop→ESS for stored Li-ion.
2. Confirm occupancy-hazard-fork consumed (`storage`/`mixed`, no HC on this row).
3. Pin editions. DS 8-9 **Mar-2010 / IR April 2026** design pin + Jul-2018 corpus `[V]` / portal re-read. DS 7-112 **Oct-2024** when Li-ion. NFPA 13-2025 = **delta**, not the OH table.
4. Run §1.0 trigger. Report IFC Ch.32 separately `[V]`. Do not dismiss on IFC. Portable-rack escape caution.
5. Three-step commodity (pallet included) or DS 7-112 packaging→CUP/CEP/UUP/UEP. No invented default class.
6. Open-frame test **before** any ceiling-only row.
7. Fork wet vs dry and head family from **STS**. DI/dry → **SR upright 280 °F**. SI sheet language = comparison-only only.
8. Read **N @ min pressure** from a cited row, or carry a stated `ASSUMED` N@P (value + why), flagged — never presented as a cited row. **No interpolation presented as cited. No 0.20×2,500. No silent 20@7.**
9. Apply **§2.3.3.5 15 ft bleed**. Apron = storage design.
10. Table 14 from **protection-table** N (or DS 7-112 500/2 h when overlay governs). **Do not freeze campus on 750 / 45,000 (wet).** Hand off to hydrant/pump.
11. ESFR in preaction/DI: [CODE NFPA 13-2022/2025 §14.2.2 (ESFR system-type limit; other system types only if specifically listed), pull 13-10]; no ESFR without a cited dry/preaction listing → Stop + RFI-variance (Verify with engineer of record).
12. Show-and-verify. Status register + `[SYN]` / `[V]` / `[inference]` listed. Directional Δ vs NFPA 13-2025 **storage**. Write **only** to caller-named path.
