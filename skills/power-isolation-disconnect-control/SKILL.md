---
name: Power isolation disconnect control
description: >-
  use this when hall or electrical-room FP needs NEC Art. 645 applicability,
  auto-vs-manual isolation, FM DS 5-32 Fig D.1 sequencing, Test Mode, and
  timing vs company-elected wet|dry|DI suppression (packet optional; STS + matrix;
  C&E when P1 live; commissioning IST when Test Mode / App. D witness /
  dual-AHJ applies — consumed when present, else ASSUMED and flagged); SI/NI-as-BOD → Stop RFI-variance (comparison-only);
  foam prohibited; mist PRACTICE REFUSED; status register every run — not a
  full water-path C&E rewrite, not ESS sprinkler overlay, not DS 5-19 as ITE
  EPO, not App. D witness ownership.
---

# Power isolation disconnect control

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **This Skill engineers the power-isolation / emergency-disconnect architecture** that ties detection and suppression to the electrical system: **NEC Article 645 applicability fork**, **NFPA 75 disconnect floor**, **FM DS 5-32 §2.5.3 / App. D / Fig D.1** sequencing, **Test Mode capability (means)**, and the **isolate-before-suppression** timing budget — only against a company-elected **`wet` | `dry` | `double-interlock`**. It does **not** elect the suppression family, rewrite the water-path releasing C&E matrix, size ESS sprinklers, invent an owner EPO philosophy from marketing pages, or own the App. D **Test Mode witness** line (that is **`commissioning-ist-acceptance-packet`**).

**Core thesis:** a data-center fire involving energized equipment cannot be fully extinguished until power is removed. Overcurrent devices miss real fault types (series arc, high-resistance parallel arc, loose connections, breaker failure/welded contacts, bad grounding). **Decide the Article 645 fork first** — many hyperscale halls take the **non-645** path on purpose and therefore have **no NEC-mandated room-wide EPO**. Then layer **NFPA 75** (often regardless of 645 election) and the **FM performance goal**: achieve isolation **before the suppression agent's effective duration ends** / isolate critical loads **before sprinkler water reaches them**. Prefer **automatic + controlled soft power-down**; every UPS needs a **direct** shutdown (battery off load), not feed-cut only.

**20 kWh/rack scope line:** when in-rack / distributed Li-ion BBU is in scope, classify rack energy with FM's method and compare to **≤20 kWh/rack** (DS 5-32 §2.3.1.4). At or under the line → stay on DS 5-32 isolation architecture. **Above → ESS hand-off** (DS 5-33 / NFPA 855) — do **not** invent ESS sprinkler/explosion design here (**`ess-isolation-venting-and-duration`**).

**Code-layer threshold fork (restamp 2026-10-09; KB *Li-ion BBU protection in data halls* Run-614/615/619/622/624/627):** IFC 2024 §1207.1.3 / Table 1207.1.3 sets the Li-ion ESS threshold at **20 kWh (nameplate)** with **no aggregate, fire area or per unit wording**; §1207.5.2 MAQ (600 kWh Li-ion) is per fire area but binds only ESS already inside §1207; §1207.3.1 exempts only **lead-acid UL 1778** UPS — **no Li-ion UPS / ITE / in-rack BBU exception**. So a hall of ≤20 kWh in-rack BBUs is outside §1207 on a per-unit reading and far over the MAQ on an aggregate reading. **Write IFC §1207 applicability — AHJ determination required on the code-floor sheet**; never write BBU exempt from IFC or BBU = ESS as settled. Ohio (OAC 1301:7-7-12, IFC 2024 Ch.12 unmodified; NFPA 855-2020 pinned) gives no state answer → local FCO. 2027 IFC is expected to move the threshold to **NFPA 855 Table 1.3** (F169-24, committee action stands by inference; 855 not held → `[V]`) — re-run the check per AHJ edition. Spare BBU modules in storage are not this Skill (→ `storage-staging-sprinkler-design`).

**Design practice (lede):** three-layer basis (code floor × insurer sheet × owner standard) → **most-stringent union PER PARAMETER** (645 election, omission path, auto vs manual, trigger level, hardware type, HVAC order, Test Mode means, selective coordination). Report **Δ vs NEC / NFPA 75 / NFPA 72** and **Δ vs NFPA 13-2025** where water-path params (delivery clock / preaction family) are consumed. Cite **section AND edition**. Show-and-verify kWh and timing inequalities. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist is presented). Company fence: controlling BOD = **`wet` | `dry` | `double-interlock`** only; SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = `PRACTICE REFUSED`**. Upstream (packet optional; gaps → `ASSUMED`): completed the input packet + STS wet\|dry\|DI + matrix power-isolation / releasing / VEWFD / carrier rows when dual-carrier (+ `preaction-releasing-c-and-e-soo` when P1 / releasing cells live; + `commissioning-ist-acceptance-packet` handshake when Test Mode / App. D witness / dual-AHJ applies). Caller-path-only. **NO PLACEHOLDER.** Generic — do **not** copy synthetic hall EPO counts, AFF heights, or kWh defaults.

**Handoff (load-bearing):** P1 / power-isolation **cells** in the authoritative releasing matrix → fill intent here, but **do not duplicate the whole C&E matrix** — that lives in **`preaction-releasing-c-and-e-soo`**. Water Boolean, no-cross-zone, no-abort-on-water, exhaust-follows-water stay there. Reciprocal with commissioning IST: **this Skill owns disconnect means / Fig D.1 architecture / Test Mode capability**; **commissioning owns the App. D Test Mode witness line**.

**Corpus honesty (training ground — never hall defaults):**

| Spine | What it shows | Honesty |
|---|---|---|
| Prior hall Li-ion isolation (worked example) | ~32k ft² / ~15 MW / **19.2 kWh/rack** wet + App. D | **`[SYN]` method only** — Fig D.1 / Test Mode / kWh math usable; refuse hall defaults; wet path is company-aligned family |
| Prior electrical room, single-interlock | Single-interlock primary; electrical room is not an ITE room under Article 645 by adjacency | **`[SYN]` comparison-only** — structure / App. D only; never company basis of design |
| Switchgear room plus adjacent double-interlock hall | Dual-object (switchgear analog + double-interlock hall) | **`[SYN]` illustrative** company-path dual-object only — never defaults |
| Prior-site commissioning IST (single-interlock) | App. D Test Mode commissioning act | **`[SYN]` comparison-only** — method for witness handoff; single-interlock hall is not company basis of design |
| Prior hall, non-interlock preaction | Detection / VEWFD structure | **`[SYN]` comparison-only** under company fence |
| Prior site, BBU classification and barrier layout | FM kWh classification (19.2 kWh/rack at or under 20; a sixth module at 23.04 hands off to DS 5-33), 20-gauge barrier every third rack | **`[SYN]` method only** — IFC §1207 aggregation for distributed BBU is an AHJ determination |
| Prior site, ESS isolation / no-auto-restart | Isolation trigger ladder, latched **no-auto-restart** (no utility-return or BMS self-clear re-close), exhaust and sprinkler kept in service, no water shutoff or restart until a cooling or removal plan | **`[SYN]` method only** — the ESS room itself is out of this skill; borrow only the latch and restoration logic |

Write the isolation package **only** to the path the **caller** names. Write output only to the caller-named path.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill elects isolation architecture, not system family)

This Skill may emit a **controlling** power-isolation / disconnect-control package only against an elected company system family:

1. **Wet-pipe sprinkler**
2. **Dry-pipe sprinkler**
3. **Double-interlock preaction**

Comparison-only (never elected here; never the controlling isolation BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

FM DS 5-32 January 2026 §2.4.1.1 preference ranking (Wet → NI → SI → DI last) and sheet trigger language that names undifferentiated preaction / water-mist remain **`comparison-only` evidence**. That sheet fact is **not** permission to run a controlling isolation package on SI/NI BOD, and **not** company election permission.

**This Skill does not elect families.** It **consumes** the election from `suppression-technology-selection`, power-isolation / releasing / VEWFD / carrier rows from `most-stringent-basis-matrix` (when dual-carrier or those rows exist), the completed the input packet, and — when gated — releasing C&E from `preaction-releasing-c-and-e-soo` and the commissioning IST handshake from `commissioning-ist-acceptance-packet`. Controlling BOD = `wet` | `dry` | `double-interlock` only.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling isolation package as if SI/NI were company-elected.
6. Do **not** continue “On SI halls…” / “On NI halls…” as a controlling isolation instruction.
7. SI/NI (including MD electrical-room SI spine, NV NI AI-hall spine, FM ranking) may appear only as **`comparison-only`** evidence — never the controlling 645 / App. D / timing path.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Wet / dry / double-interlock water sprinkler | Permitted when elected upstream | Emit controlling isolation package; wet/dry/DI drive initiation / isolate-before-water clock |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not accept/design foam BOD |
| Water mist | **`PRACTICE REFUSED`** | Record sheet evidence if cited; do **not** design/accept mist as controlling BOD or isolation timing family |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only special-hazard tracks | May annotate clean-agent ≤10 min soft-shutdown clock / DS 4-9 Class A vs C when adjunct in scope — **never** as company water BOD |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist (including §2.5.3.1 trigger wording) does **not** authorize mist election or an isolation timing family here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| NEC Art. 645 fork + omission + 645.27 trap | System-family election (STS) |
| NFPA 75 disconnect floor checklist | Full releasing C&E / SOO rewrite (hand P1 intent only) |
| FM §2.5.3 auto vs manual + trigger by company wet/dry/DI | App. D **Test Mode witness** (commissioning IST owns) |
| App. D / Fig D.1 **means** + Test Mode **capability** | ESS sprinkler / venting / duration (>20 kWh hand-off) |
| ≤20 kWh/rack show-and-verify + ESS hand-off | ASD port / transport math |
| Timing inequality (isolate-before-water / clean-agent ≤10 min adjunct) | Design-stage ≤30 s volume / QOD screen (water-delivery owns) |
| Compact P1 I/O + SOO hand-off row | DS 5-19 MV switchgear package as if ITE EPO |
| Status register + reciprocal handshakes | Inventing EPO count / AFF height / hall kWh defaults |
| Consume packet + STS wet\|dry\|DI + matrix (+ C&E / IST as gated) | Treating bare `preaction` or mist as controlling family |
| Edition pins + Δ vs NEC/75/72 **and** Δ vs 13-2025 where water-path params consumed | Copying OH 32k/15 MW/19.2 kWh or SI/NI spines as defaults |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** the 645 election / omission path, **(c)** the auto vs manual gate, **(d)** the initiation level, **(e)** the kWh / ESS gate (or N/A), **(f)** Fig D.1 completeness, **(g)** the Test Mode means claim, and **(h)** the timing inequality claim:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling wet\|dry\|DI + edition + claim supported by **mined** sheet / caller Ah·V·counts / named peer proof already closed |
| `provisional` | Directionally pinned; edition / initiation / device-time hole flagged `[V]` — **never silent `grounded` on copied kWh or unearned timing** |
| `unresolved` | STS / matrix / space type / carrier / AHJ edition / Li-ion energy inputs not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, MD SI electrical-room spine, NV NI AI-hall, FM ranking / sheet mist wording — never controlling BOD |
| `handoff` | Peer owns next action (C&E matrix authorship; commissioning App. D witness; ESS >20 kWh; ASD ports; water-delivery ≤30 s design screen; multizone PI-Zn tags; STS/matrix/packet) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |
| `PRACTICE REFUSED` | Mist presented as isolation timing / controlling family — record and refuse; do not continue mist BOD |

**Unearned kWh / timing → never `grounded`.** Copied OH 19.2 kWh without caller Ah/V → stated `ASSUMED` / `[SYN]` provisional only, flagged — never `grounded`. Clean-agent ≤10 min misapplied as wet-hall clock → category-error (reclassify; do not `grounded`). SI evidence → `comparison-only`. Invented EPO / initiation-as-FM-pin → Stop.

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent EPO count, AFF height, kWh from habit, or a synthetic 15 MW / 19.2 kWh hall. Do not treat SI/NI as company BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve prior job files. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). Mist → `PRACTICE REFUSED`. Clean-agent/hybrid → handoff annotation only (may drive adjunct ≤10 min clock — never company water BOD). |
| **Consumed `most-stringent-basis-matrix` power-isolation / releasing / VEWFD / carrier rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling PI / releasing / VEWFD / carrier row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap FM App. D onto an AXA-only job. |
| **`preaction-releasing-c-and-e-soo` when releasing cells / P1 live** | **yes when gated** | Required when P1 / releasing path is in scope. Missing when gated → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. This Skill fills P1 **intent** only — does not invent water Boolean. |
| **`commissioning-ist-acceptance-packet` handshake** | **yes when gated** | When Test Mode / App. D witness / dual-AHJ applies: handshake witness ownership; do not invent MDP/UPS witness scripts here. |
| **Space type** | **yes** | `white-space / ITE hall` / `electrical room` / `UPS room` / `process-control / ICS` / other named. Support spaces are **not** ITE rooms merely by adjacency — Article 645 does not automatically attach. |
| **Article 645 election** | **yes** (or explicit `[V] ask`) | `645` / `non-645` / `unelected`. If unelected → run the six-condition gate and **ask**; do not assume room-wide EPO. |
| **Staffing / ops posture** | **yes** | Lights-out vs 24/7 qualified responders — binds the auto vs manual gate. |
| **Carrier** | **yes** | `FM DS 5-32 controlling` / dual / other / `n/a`. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Power-isolation initiation level** | **yes** (or explicit `[V]`) | `L2` / `L3` / `waterflow` / `L2-soft then L3/waterflow-full` / owner-named. FM §2.5.3.1.1 permits *any smoke detection or the water-flow alarm* and **does not pin L1/L2/L3**. Unpinned → **flag `[V]` and ask — do not invent as an FM section pin**. |
| **In-rack / distributed Li-ion?** | **yes** | `none` / `yes` with Ah, V, cells/module, modules/rack **or** a stated kWh/rack. Missing numbers on a Li-ion job → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged or structure-only with `[V]` / `unresolved`. |
| **Owner EPO posture** | **yes** (may be `none`) | Project-issued. NDA → structure-only (often *discourage room-wide EPO*); may raise localization, never silently delete FM isolation. |
| **AHJ-enforced NEC / NFPA 75 editions** | **yes** to cite | Enforced ≠ latest. NEC **2026** latest; many AHJs still on **2023/2020/2017**. NFPA 75-**2024** references older 70/72 cycles. |
| **Caller output path** | **yes** | If unnamed, return the package in the response and stop. |

Optional (do not block; flag `[V]` / `handoff` / `comparison-only`): A/B UPS topology; zone alignment tags from multizone Skill; clean-agent hold time (for ≤10 min / hold÷2 clocks when adjunct); coordination study availability for 645.27; SI/NI comparison evidence — never controlling.

**Do not invent** a room-wide EPO count, an AFF mounting height as code, a kWh from habit, ESS sprinkler density, PLACEHOLDER text, or initiation L2/L3 as an FM section pin. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve prior job files |
| `suppression-technology-selection` | Elected wet/dry/DI **company election token**; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI; treat mist as BOD |
| `most-stringent-basis-matrix` | Power-isolation / releasing / VEWFD / carrier rows when dual-carrier; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA swap |
| `preaction-releasing-c-and-e-soo` | P1 cell context — **required when releasing cells / P1 live** | Rewrite water Boolean / abort / cross-zone / exhaust |
| `commissioning-ist-acceptance-packet` | App. D **witness** handshake when Test Mode / dual-AHJ applies | Own witness scripts / invent MDP-UPS tag lists for IST |
| `multizone-preaction-zone-alignment` | PI-Zn 1:1 tags when present | Elect N / boundaries here |
| `ess-isolation-venting-and-duration` | >20 kWh/rack hand-off target when crossed | Invent ESS sprinkler/vent design here |
| `fa-asd-vewfd-data-hall-sampling-layout` | Initiation / VEWFD peer context when present | Size ASD ports / transport here |
| `dry-preaction-water-delivery-screen` | Named water-arrival inequality input when present | Own design-stage ≤30 s volume/QOD screen; invent fake code ≤30 s fill |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling PI / releasing / VEWFD / carrier rows are missing when required, or P1/releasing C&E is missing when gated → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

### 2.2 Reciprocal handshakes (required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `preaction-releasing-c-and-e-soo` | Authoritative C&E / SOO authorship; water Boolean; no-cross-zone; abort; exhaust | Compact **P1 intent** / isolation I/O schedule + SOO hand-off row only |
| `commissioning-ist-acceptance-packet` | App. D **Test Mode witness** line; dual-AHJ acceptance acts | Disconnect **means** / Fig D.1 architecture / Test Mode **capability** |
| `multizone-preaction-zone-alignment` | Zone count N / 1:1 PA↔VEWFD↔PI alignment | Consume **PI-Zn tags**; retain whole-room escalation |
| `ess-isolation-venting-and-duration` | >20 kWh/rack ESS sprinkler / vent / duration | ≤20 kWh show-and-verify; hand-off above the line |
| `fa-asd-vewfd-data-hall-sampling-layout` | ASD port / transport design math | Initiation / VEWFD trigger peer only |
| `dry-preaction-water-delivery-screen` | Design-stage ≤30 s volume / QOD screen | Consume water-arrival inequality; isolate-before-water ordering only |
| `suppression-technology-selection` | Family election + fence status | **Consume only** wet\|dry\|DI token |
| `most-stringent-basis-matrix` | Per-parameter union / carrier rows | **Consume only** |
| the input packet | Assignment context | **Consume only** — optional; absent → proceed, flag `ASSUMED` |

Emit one `HAND OFF — <peer>: <what they own>` line per open peer dependency. Do **not** restamp peers from this Skill.

Example lines:

- `HAND OFF — preaction-releasing-c-and-e-soo: full water Boolean / abort / cross-zone / exhaust. This Skill filled P1 intent + compact isolation I/O only.`
- `HAND OFF — commissioning-ist-acceptance-packet: App. D Test Mode witness / dual-AHJ. This Skill owns means / Fig D.1 / Test Mode capability.`
- `HAND OFF — multizone-preaction-zone-alignment: PI-Zn 1:1 tags / N. This Skill consumes tags; retains whole-room escalation.`
- `HAND OFF — ess-isolation-venting-and-duration: >20 kWh/rack ESS path. This Skill showed ≤20 kWh math or handed off.`
- `HAND OFF — fa-asd-vewfd-data-hall-sampling-layout: ports / transport. Initiation peer only here.`
- `HAND OFF — dry-preaction-water-delivery-screen: design-stage ≤30 s proof. This Skill only orders isolate-before-water.`

---

## 3. Steps

### 3.0 Hard scope + status register first

Before edition pins or the 645 fork:

1. Confirm company fence: STS token = `wet` | `dry` | `double-interlock`. SI/NI-as-BOD → **Stop** `RFI-variance`. Foam → **Stop**. Mist → `PRACTICE REFUSED`.
2. Check upstream (packet optional): packet if present (optional); STS present; matrix rows when dual-carrier; C&E when P1 gated; commissioning handshake when Test Mode / dual-AHJ gated. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (or run the upstream Skill first if practical).
3. Emit status-register skeleton on Hard-scope / 645 / auto-manual / initiation / kWh / Fig D.1 / Test Mode / timing (tokens from §1.4). Keep `[SYN]`/`[V]` honesty tags **inside** status rows.

### 3.1 Pin editions (enforced ≠ latest)

| Standard | Role | Shop-pinned editions |
|---|---|---|
| **NEC (NFPA 70)** | Art. **645** ITE rooms — optional/permissive; 645.10 disconnect [CODE NEC 2020/2023 §645.10, pulls 70-05, 70-760-645-2023; NEC 2026 §645.10, 645.10(A) or (B), pull 70-13]; 645.4 gate [CODE NEC 2020/2023 §645.4, same pulls] (**645.5** in 2026 [CODE NEC 2026 §645.5, pull 70-11]; old 645.5 supply circuits = 2026 §645.6, pull 70-11); 645.27 selective coordination for CODS [CODE NEC 2020 §645.27, pull 70-05; NEC 2023 §645.27, pull 70-10; NEC 2026 §645.27(A) General, (B) Replacements, (C) Modifications, pull 70-10] | Latest **2026**; AHJ often older. Cite **section AND edition**. |
| **NFPA 75** | ITE-area disconnect floor; HVAC/damper; UPS battery-from-load; FACP supervision | **2024** (confirm adoption) |
| **NFPA 72** | Signaling / emergency-control / releasing interfaces | Enforced vs **2025** `[V]` numbering |
| **NFPA 13** | Water-path / preaction family context when delivery clock or DI params are consumed | Delta baseline **13-2025**; do not invent max-area § here |
| **FM DS 5-32** | §2.5.3 isolation; §3.4.2.2 HVAC; §3.5.2.2.2 fault rationale; **App. D / Fig D.1**; Test Mode | **January 2026** |
| **FM DS 5-19** | Switchgear-room **analog** (upstream high-side breaker outside room) — **different object** | Do **not** treat 645/75 as governing MV switchgear, or DS 5-19 as governing the ITE hall |
| **FM DS 4-9** | Clean-agent **Class A vs Class C** concentration fork on de-energize vs not | When gas adjunct/primary is in scope (handoff annotation) |
| **FM DS 7-110** | Process-control / ICS rider — auto power-down delay **≤ hold_time ÷ 2** | Plant ICS rooms, not a rewrite of ITE EPO |

Look up **by title**: *Design practice*; *Power isolation and disconnect control*; *IT-room power isolation emergency disconnect code floor*; *FM DS 5-32 insurer design basis*; *VEWFD detection & releasing for data centers*; *Li-ion BBU protection in data halls*; *Enforced-vs-latest edition resolver and reference pins*.

### 3.2 Article 645 applicability fork — decide first

```
IF alternative IT-room (645) wiring methods are NOT needed
    => default NON-645 => NO NEC 645.10 remote disconnect / EPO required
ELSE test six 645.4 conditions (2017 numbering; [CODE NEC 2020/2023 §645.4, pulls 70-05, 70-760-645-2023]; 2026 landing [CODE NEC 2026 §645.5, same six conditions, pull 70-11]):
    C1 645.10-compliant disconnecting means provided
    C2 HVAC dedicated OR shared-with-boundary fire/smoke dampers on smoke / 645.10
    C3 IT & communications equipment listed
    C4 room occupied/accessible only by personnel needed to run IT equipment
    C5 fire-rated separation from other occupancies; openings protected
    C6 only electrical equipment/wiring associated with the IT room installed
    IF any Cn = false => NON-645
    ELSE => Article 645 design permitted (accept 645.10 regime)
```

**Trade:** 645 buys wiring flexibility (underfloor / IT cord allowances) and costs the 645.10 disconnect + HVAC/damper coordination. Non-645 avoids the EPO regime but binds default Ch.1–4 wiring.

**If under 645, test omission path 645.10(B) / NFPA 75 11.4.5.4.2** (five conditions: approved shutdown procedure for power **and** air; continuously available qualified personnel; smoke detection; approved suppression; compliant underfloor cabling). Article **685** route is a separate exemption. AHJ rejection → provide grouped, marked controls at approved locations.

**Trap:** sources that state **645.27** selective coordination **unconditionally** are wrong — 645 is elective **and** critical operations data system is a defined subset. First question when someone cites 645.27: **are we electing Article 645 at all?**

**NFPA 70-2026 gate and owner election.** The Article 645 gate in NFPA 70-2026 is **§645.5** (it was §645.4 in 2023). Fix an older cite before it is copied onto a 2026 job. The six conditions in the fork above are the same conditions; only the section number moved.

Owner election stays ASSUMED until the owner signs it. Verify with the engineer of record.

- **A.** Do not apply Article 645. General NEC applies. No ITE remote disconnect.
- **B.** Apply Article 645 with §645.10(A): a remote disconnect at the principal exits.
- **C.** Apply Article 645 under §645.10(B) for a critical operations data system (staff qualified and available at all times, smoke detection, and an approved suppression system). **Recommend C** for a double-interlock hall that already has very early warning fire detection.

Under A, B, or C: do not tie automatic double-interlock release to an EPO or a shunt trip.

The per-fire-area chemistry gate (**70/20 kWh**: lead-acid 70 kWh, Li-ion 20 kWh) is owned by `occupancy-hazard-fork` and `ess-isolation-venting-and-duration`. The ≤20 kWh/rack line in this skill remains the FM DS 5-32 distributed-BBU handoff.

**Electrical / UPS / switchgear rooms:** not ITE rooms by adjacency. Their disconnect rules come from the articles/sheets governing that equipment (e.g. DS 5-19 for MV switchgear). Status the 645 election row (`grounded` / `provisional` / `unresolved` / `[V]` ask).

### 3.3 NFPA 75 floor (often regardless of 645 election)

When adopted / applied:

- Approved means to disconnect **all electronic equipment** in the room/zone **+ all dedicated HVAC**.
- HVAC disconnect **closes required fire/smoke dampers**.
- **In-room UPS disconnect also disconnects the battery from its load** (except Art. 685 / ≤750 VA).
- Supervise interlock/shutdown-device power **and** disconnect-operating power at the **FACP**; annunciate at a **constantly attended location**.

Pins: NFPA 75-2024 **11.4.5.1–.3**, **11.5.1 / .1.1**, **9.2.6–.8**. NEC/NFPA do **not** mandate shunt-trip vs contactor hardware type (approved means). **Shunt-trip MDPs + direct UPS shutdown + Test-Mode panel** are the **FM prescription** (and a common 645.10 compliance path) — name the layer.

### 3.4 Auto vs manual (FM §2.5.3.1) — miss one → automatic

**Default: automatic + controlled soft power-down.**

Manual isolation only if **ALL** FM §2.5.3.1.3 conditions hold, including:

- VEWFD in equipment rooms; alarms to constantly attended location + immediate notification
- **Qualified responders on site 24/7**, able to respond within **max 10 min** before FP activation
- Noncombustible construction; strong human-element programs
- Plan agreed by senior management, drilled annually, shared with fire service
- **Measured ≤10 min** completion at each annual drill

**Lights-out / minimally staffed → automatic.** Do not waive on hope. Status the auto/manual gate.

**Trigger by company suppression family (FM §2.5.3.1 — company fence applied):**

| Suppression (controlling) | Initiation (FM) | Timing goal | Status note |
|---|---|---|---|
| **Wet / dry / double-interlock** only | **any smoke detection or waterflow** | isolate **before agent/water duration ends**; critical loads **before water reaches them** | Controlling company water path |
| Clean-agent / inert / hybrid (adjunct / handoff) | **discharge alarm** | soft shutdown **≤10 min**, maintain design concentration | `handoff` / adjunct — **never** company water BOD |

**Sheet-language footnote (`comparison-only`):** FM §2.5.3.1 text that groups wet / preaction / water-mist is **sheet wording only**. Undifferentiated `preaction` covering SI/NI is **not** an ordinary controlling Input — SI/NI-as-BOD → Stop `RFI-variance`. Mist named in the sheet → `PRACTICE REFUSED` / `comparison-only`; do **not** design/accept mist as the isolation timing family.

**Initiation level `[V]` if unpinned.** Defensible pattern (still ask): L1 supervisory / start timer; **L2 begin localized soft-down**; **L3 / waterflow complete** room isolation. **Do not stamp L2 or L3 as an FM section pin.** Status the initiation row.

### 3.5 20 kWh/rack scope line (when Li-ion is in scope)

```
kWh/cell = (Ah × V) / 1000
kWh/module = kWh/cell × cells_per_module
kWh/rack = kWh/module × modules_per_rack
# ≤20 kWh/rack → DS 5-32 distributed-BBU overlay
# >20 kWh/rack → [V] ESS hand-off (DS 5-33 / NFPA 855) — not this Skill's sprinkler design
```

Show substitutions. Do not invent Ah/V. Also respect companion scope conditions when the Li-ion note states them (e.g. shelf stacking / aisle spacing) — consume, don't re-litigate barriers here. OH worked **19.2 kWh/rack** is **`[SYN]` method only** — never a hall default; status never `grounded` on copied kWh without caller Ah/V.

**Design consequence:** stored energy behind UPS/BBU means **feed-cut is insufficient** — schedule **UPS-direct-shutdown** (and rack-string isolation where applicable) as a device class distinct from MDP shunt-trip. Above the line → `handoff` to `ess-isolation-venting-and-duration`.

### 3.6 Engineer App. D architecture + Fig D.1 sequence (means)

Account for **all critical spaces, power sources, distribution, backup, and cooling**.

**Inputs (typical):** manual disconnects / EPO at egress (if provided); FA calls; FP manual release; VEWFD L2/L3; waterflow; (gas adjunct) discharge alarm.

**Outputs (Fig D.1 order — critical loads before water):**

| Seq | Output | Device class | Notes |
|---|---|---|---|
| O1 | Critical-load feeds (rPDU/RPP) | **Shunt-trip** | Local cabinet/row first when possible |
| O2/O3 | UPS A/B (+ BBU strings) | **Direct UPS shutdown** | Remove **battery** power |
| O4 | Impacted MDPs | **Shunt-trip** | |
| O5/O6 | ATS/genset / utility | Interlock / shunt-trip | Inhibit re-energize into isolated zone |
| O7 | HVAC / dampers | Interlock **after** O1–O4 | Do not kill cooling while load still energized |
| — | **Lighting** | **Not isolated** | Egress / §2.5.3.1 exception |

**Locality (§2.8):** isolate as locally as possible (cabinet/row) with capability to depower the whole room / zone, and to take down **both A and B** UPS. Multizone halls: align PI zones 1:1 with suppression/VEWFD (**`multizone-preaction-zone-alignment`**); retain whole-room escalation.

**HVAC (§3.4.2.2):** preferred single integrated disconnect that de-energizes **and** interlocks DP equipment + HVAC. Sequence **M2/O7 after P1**. No corpus method for exact cooling-continuation minutes → order the outputs; do not invent a hold time `[V]`.

**Clean-agent overlay (when adjunct in scope):** delayed disconnect ≈ not de-energized for DS 4-9 Class A vs C concentration — put that priced trade in front of the owner; status `handoff`. ICS rooms under DS 7-110: delay **≤ hold_time ÷ 2** when that sheet applies.

**Witness split:** this step builds **means / capability**. Live App. D Test Mode **witness** during acceptance → handshake `commissioning-ist-acceptance-packet`.

### 3.7 Timing budget (commissioning acceptance — not a fake 30 s code number)

```
# Water-based hall (ordering / inequality — device times from project data)
t_isolate = t_detect + t_panel_logic + t_interface + t_shunt_trip
          + t_UPS_orderly_shutdown + t_downstream_decay
# Must satisfy:
t_isolate < t_headfuse + t_fill_to_wet_equipment # isolate before water contact
# Clean-agent clock (different — adjunct / handoff only):
t_soft_shutdown ≤ 10 min # FM §2.5.3.1.2 — NOT the wet-hall clock
# Do NOT hard-code "≤30 s fill" as a NEC/NFPA 75 number — that is a suppression
# delivery input (FM DS 5-32) consumed from dry-preaction-water-delivery-screen.
```

Read clearing/opening terms from the project's **coordination study + TCC curves** when 645.27 / selective coordination applies — not generic assumptions. Mark synthetic device times `[SYN]`. Report **Δ vs NFPA 13-2025** when water-path delivery / preaction-family params are consumed.

**Category-error guard:** FM **≤10 min** soft-shutdown is the **clean-agent** window. Applying it as the wet-hall deadline is a misread. Wet/dry/DI clock = **isolate-before-water**, usually won by **early smoke initiation**, not by agent hold. Status the timing claim; unearned → never `grounded`.

### 3.8 Test Mode + change control (means)

Control panel **must** support **Test Mode**: register triggers + FP signaling **without** firing power-off outputs — so detection/input testing can run without dropping a live room.

Commissioning hooks (means side; witness owned by commissioning IST when gated):

1. Test Mode exercise of every input (EPO, L2, L3, waterflow, FACP, FP release).
2. Live output testing in a maintenance window (each shunt-trip, each UPS direct shutdown, ATS lockout, HVAC-after-power interlock).
3. Fail-safe check (loss of panel signal → fail toward isolation where specified).
4. **Re-incorporate + re-test** after any added power/distribution/backup/cooling or FA/FP change — standing electrical ITM.

**Walktest / software GUI disable is not an impairment control** for releasing or isolation — prefer **physical, tagged** disconnects where the releasing/isolation basis requires them. Status the Test Mode means claim; witness act → `handoff` to commissioning IST.

### 3.9 Hand C&E cells — do not rewrite the water matrix

Emit a **compact isolation I/O schedule + SOO** and a **hand-off row** into the releasing matrix:

| Matrix cell | This Skill's intent | Owner of full matrix |
|---|---|---|
| **P1** power isolation | Level per pinned `[V]` election; direct UPS; Fig D.1 order | **`preaction-releasing-c-and-e-soo`** |
| W1 / abort / cross-zone / exhaust | **Do not rewrite** | same |
| Multizone alignment tags | Consume PA-Zn / VEWFD-Zn / PI-Zn | **`multizone-preaction-zone-alignment`** |

When P1 / releasing cells are live and C&E is missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged (state an `ASSUMED` releasing-cell basis; do not silently invent the matrix).

### 3.10 Status register close-out

Close every §1.4 row with a token + `[SYN]`/`[V]` honesty tags inside the row. Refuse silent `grounded` on: copied OH kWh, unearned isolate-before-water inequality, initiation stamped as FM pin, SI/NI evidence, mist sheet wording, or DS 5-19 treated as ITE EPO.

---

## 4. Output

A **power-isolation disconnect-control package**:

1. Hard-scope gate + status register (gate / 645 / auto-manual / initiation / kWh / Fig D.1 / Test Mode / timing).
2. Edition-pin block (NEC/75/72/13/FM; enforced ≠ latest).
3. Echoed inputs including **packet + STS wet\|dry\|DI + matrix** (+ C&E / IST when gated).
4. 645 fork result (+ omission / Art. 685 / 645.27 trap as applicable).
5. NFPA 75 floor checklist.
6. Auto vs manual gate table; company wet/dry/DI trigger table (mist = footnote only).
7. kWh scope line (if Li-ion) with show-and-verify; ESS hand-off if over.
8. I/O schedules; Fig D.1 sequence SOO (means); HVAC-after-power; lighting exception.
9. Timing inequality + category-error guard; Δ vs NEC/75/72 and Δ vs 13-2025 where water-path params consumed.
10. Test Mode means + change-control; witness handoff row when gated.
11. Compact P1 hand-off to releasing C&E; reciprocal handshake / `HAND OFF` rows.
12. `[SYN]`/`[V]` / status register; corpus honesty (no OH / SI / NI / Raleigh defaults copied).

Write **only** to the caller-named path.

Do **not** emit: full water-path C&E rewrite, ASD port math, density×area, ESS sprinkler/explosion design, MV switchgear DS 5-19 package as if it were ITE EPO, App. D witness scripts owned by commissioning, mist/foam BOD, or CAD.

---

## 5. Stop

> A missing input is ASSUMED (state the value and why). It is not a stop. Scope locks stay hard stops.

1. Caller asks to write outside the caller-named path.

---

## 6. Citations (section **and** edition)

**NEC Art. 645** — optional gate **645.4** [CODE NEC 2020/2023, pulls 70-05, 70-760-645-2023] (**645.5** in 2026 [CODE NEC 2026 §645.5, pull 70-11]); disconnect **645.10** / omission **645.10(B)** [CODE NEC 2020/2023, same pulls; NEC 2026 §645.10 and §645.10(B) (CODS remote-control omission when all conditions met), pull 70-13]; selective coordination **645.27** [CODE NEC 2020, pull 70-05; NEC 2023/2026 §645.27, pull 70-10; 2026 splits into (A) General, (B) Replacements, (C) Modifications] (CODS; elective article); Art. **685** exemption route. **NFPA 75-2024** — **11.4.5.x** [CODE NFPA 75-2020/2024 §11.4.5, pull 75-08] / **11.5.1.x** disconnect + UPS battery-from-load; **9.2.6–.8** supervision/annunciation. **NFPA 72** — emergency-control / releasing interfaces (enforced vs **2025** `[V]`). **NFPA 13-2025** — water-path / preaction-family Δ when delivery or DI params are consumed (do not invent max-area § here). **FM DS 5-32 Jan-2026** — §2.5.3 / .1.1 / .1.2 / .1.3; §2.8 locality; §3.4.2.2 HVAC; §3.5.2.2.2 faults; **App. D / Fig D.1** Test Mode; **§2.3.1.4** ≤20 kWh/rack distributed BBU scope. **FM DS 4-9** — de-energize → Class A vs not → Class C (adjunct). **FM DS 7-110** — ICS hold÷2 rider. **FM DS 5-19** — switchgear analog only (different object).

---

## 7. Design practice

1. Three-layer, most stringent, **per parameter**. Code sets 645/75 existence and UPS-battery rules; FM usually sets timing, Test Mode means, and shunt-trip/direct-UPS architecture; owner sets EPO philosophy (often anti-room-wide).
2. Per-parameter, not per-layer. Non-645 (no code EPO) still takes FM App. D isolation.
3. **Company fence.** Controlling BOD = **wet | dry | DI** only. SI/NI → Stop + `RFI-variance` / comparison-only. Foam prohibited. Mist = `PRACTICE REFUSED`. Never silent-swap SI→DI. Sheet mist / undifferentiated preaction wording = language only.
4. **Status register every run** on Hard-scope / 645 / auto-manual / initiation / kWh / Fig D.1 / Test Mode / timing: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` (+ `PRACTICE REFUSED` when mist). Unearned kWh/timing → never `grounded`.
5. **Upstream (packet optional; gaps → `ASSUMED`, not a Stop).** Packet + STS wet\|dry\|DI + matrix PI/releasing/VEWFD/carrier when dual-carrier; C&E when P1 live; commissioning IST handshake when Test Mode / App. D witness / dual-AHJ applies. Missing → proceed with `ASSUMED` (flagged), not a Stop.
6. Owner may raise localization / soft-down discipline, never delete the isolate-before-water goal on an FM job.
7. Enforced ≠ latest. Surface NEC edition lag inside FM bibliographies. Report **Δ vs NEC / NFPA 75 / NFPA 72** and **Δ vs NFPA 13-2025** where water-path params are consumed.
8. Show-and-verify kWh gate and timing inequalities; no fake code ≤30 s fill; ≤10 min ≠ wet clock.
9. Honesty. Initiation level unpinned — **ask**. >20 kWh → ESS hand-off, don't bluff. Reciprocal: means here / witness at commissioning IST.
10. **NO PLACEHOLDER.** Caller-path-only. Do not invent hall numbers, EPO counts, AFF heights, or Ah/V. Generic — specify by **function + listing**, never by a default panel SKU.
11. On a NFPA 70-2026 job, cite the Article 645 gate at **§645.5**, not §645.4. Record owner option A, B, or C. **Recommend C** for double-interlock plus very early warning. Do not tie automatic double-interlock release to an EPO or a shunt trip.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Full releasing C&E + SOO (water path) | **`preaction-releasing-c-and-e-soo`** (hand P1 cells only) |
| App. D Test Mode **witness** / dual-AHJ acceptance stack | **`commissioning-ist-acceptance-packet`** (this Skill = means) |
| Multizone PA/VEWFD/PI alignment | **`multizone-preaction-zone-alignment`** |
| ASD port / transport sizing | **`fa-asd-vewfd-data-hall-sampling-layout`** |
| Density × area / design-stage ≤30 s delivery proof | **`density-area-dry-increase`** / **`dry-preaction-water-delivery-screen`** |
| ESS sprinkler / venting / duration | **`ess-isolation-venting-and-duration`** |
| MV switchgear room FP | **`mv-switchgear-room-package`** — DS 5-19 room package; **not** 645 ITE EPO and not built here |
| Clean-agent quantity / hold-time sizing | clean-agent Skills (adjunct timing annotation only here) |
| System-family election / dual-carrier matrix authorship | **`suppression-technology-selection`** / **`most-stringent-basis-matrix`** |
| Assignment packet authorship | **the input packet** |
| Li-ion vertical barrier layout | Li-ion / occupancy overlay Skills |
| Compartmentation FRR schedule | **`fire-area-compartmentation-schedule`** |

---
