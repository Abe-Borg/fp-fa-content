---
name: Dry/preaction water-delivery screen
description: >-
 use this when dry or double-interlock volume must prove water-delivery time
 (NFPA 13 ≤60 s / FM often 30 s gate) after company-elected wet|dry|DI
 (STS + matrix consumed when present, else ASSUMED; packet optional), and you elect QOD/accelerator vs volume
 cut vs extra risers; SI/NI as BOD → Stop RFI-variance (comparison-only
 evidence only); foam prohibited; mist PRACTICE REFUSED; status register
 every run; NOT occupancy, density×area, pump envelope, trim catalog, C&E,
 nitrogen C-factor, SprinkFDT tree.
---

# Dry/preaction water-delivery screen

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **This Skill is the WATER-DELIVERY TIME SCREEN** that runs after **suppression-technology-selection has already pinned** company-elected `dry` / `double-interlock` (or wet with an explicit dry-clock companion that still owes a delivery proof). It elects **QOD / accelerator vs volume-cut vs extra risers**, pins the **60 s vs 30 s fork**, states whether the chosen QOD is **listed for air vs nitrogen**, and emits a **status register** on the gate, Parameters A–E, and the proof claim. It does **not** pick occupancy, density×area, pump envelope, El/El trim, C&E, C-factor, or a SprinkFDT tree.

**Core thesis:** accelerator **trip time is not water-delivery time.** Every opened QOD sheet that speaks to delivery says so in words. A listed QOD can **waive or shorten the valve-open half** of the clock; it does **not** prove water at the remote head. **Do not invent a 30 s (or 60 s) proof** unless the **caller names the listed calculation software** (or a test-manifold / as-built ITC procedure that actually measures water). If software is unnamed → **Stop** on any claim that the hall “meets 30 s.” Unproved 30 s → status `unresolved` or `handoff` — **never** `grounded` “meets 30 s.”

**Design practice:** three-layer basis (code floor × insurer sheet × owner standard), **most-stringent union PER PARAMETER**, applied separately to **delivery-time gate**, **volume gates**, **proof method**, **QOD vs split**, and **air vs N₂ compatibility of the chosen QOD**. Delta vs **NFPA 13-2025** (and other floors where cited). Cite **section AND edition**. Show-and-verify math. Flag invented values `[SYN]` / unpinned `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Company fence: controlling BOD = `wet` | `dry` | `double-interlock` only; SI/NI → Stop + `RFI-variance` / comparison-only (never the controlling clock path); **Foam prohibited**; **Mist = PRACTICE REFUSED**. If notes conflict, **most-stringent wins and both sources stay visible**. Generic — do not copy a hall volume or a vendor SKU onto another job. Caller-path-only. **NO PLACEHOLDER** anywhere.

**Honesty.** Do not invent gallons, trip seconds, a 30-second closeout, or a listed-program name. A vendor graph of accelerator operating time versus volume is not a water-delivery proof. A prior layout's volume budget is steering only. Do not copy its gallons onto another hall.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (handshake — this Skill elects nothing)

This Skill may emit a **controlling** dry/preaction water-delivery screen only against an elected company system family that **owes a dry/DI delivery clock**:

1. **Dry-pipe sprinkler**
2. **Double-interlock preaction**
3. **Wet-pipe** — only when an explicit companion dry/DI zone still owes a delivery proof; **wet with no dry/preaction clock → N/A (not this screen)**

Comparison-only (never elected; never the controlling BOD / controlling clock path):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

FM DS 5-32 January 2026 §2.4.1.1 preference ranking and §2.4.3.2.1.2(D)’s **“no interlock-type qualifier”** on the ≤30 s gate remain **`comparison-only` evidence**. That sheet fact is **not** permission to run a controlling screen on SI/NI BOD, and **not** company election permission.

**This Skill does not elect families.** It **consumes** the election from `suppression-technology-selection` and delivery-time / DI-penalty rows from `most-stringent-basis-matrix` (plus the completed the input packet). Controlling BOD = `wet` | `dry` | `double-interlock` only.

If the caller presents single-interlock, non-interlock, or another prohibited preaction type as the **basis of design** / controlling mix:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute wet, dry, or double-interlock.
5. Do **not** emit a controlling water-delivery screen as if SI/NI were company-elected.
6. Do **not** treat “FM still owes ≤30 s on every preaction arrangement” as authorization for an SI/NI controlling clock path.
7. SI/NI may appear only as a **`comparison-only`** evidence row (never the controlling Parameter A path).

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Dry / double-interlock water sprinkler (and wet companion with a dry clock) | Permitted when elected upstream | Emit controlling water-delivery screen |
| Wet with **no** dry/preaction clock | N/A | Mark N/A; do not invent a dry clock |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not design foam delivery |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only | Not this Skill |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist does **not** authorize mist election or design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Parameter A–E water-delivery screen + status register | System-family election (STS) |
| 60 s vs 30 s fork; volume vs FM overlay; proof method | Occupancy / HC / OH classification |
| QOD vs volume-cut vs extra risers; trip ≠ delivery | Density × area `calcs` |
| Opened QOD × air/N₂ from sheets | Dual-carrier BOD rebuild |
| Reciprocal handshake: prove or mark unproved | C&E matrix / SOO (names clocks only) |
| Consume packet + STS + matrix delivery/DI-penalty rows | El/El trim catalog / SKU schedule |
| | Nitrogen fill / C-factor / purity |
| | SprinkFDT / `calcs` / inventing a 30 s closeout |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** each of Parameters A–E, and **(c)** the proof claim:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling election + edition + proof method named; claim supported by opened sheet or named listed program / measured test |
| `provisional` | Directionally pinned; edition or sheet hole flagged `[V]` but not blocking |
| `unresolved` | STS / matrix / volume / carrier / AHJ edition / proof method not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, FM ranking, or FM “no interlock qualifier” used as evidence only — never controlling BOD |
| `handoff` | Proof or hardware owned by peer (IST witness, trim SKU, N₂ fill, named listed program outside this Skill) |
| `RFI-variance` | SI/NI/foam/mist (or other fence breach) presented as BOD |

**Unproved 30 s (or calculated-table) claim → `unresolved` or `handoff`. Never `grounded` “meets 30 s.”**

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent a 30 s proof. Do not treat SI/NI as company BOD. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `wet` \| `dry` \| `double-interlock` from `suppression-technology-selection`. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). Wet with no dry clock → **N/A**. |
| **Consumed `most-stringent-basis-matrix` delivery-time / DI-penalty rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling delivery / DI-penalty row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap FM **30 s** onto an AXA-only job. |
| **System type per hall / zone (controlling)** | **yes** | Already pinned: `dry` / `double-interlock` (this Skill’s primary clock). Wet companion only if a dry clock still applies. This Skill does **not** pick SI vs DI. |
| **Largest system volume (gal)** | **yes** | **Single largest** dry/DI zone, not campus aggregate. Missing → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. Do not invent gallons from ft². |
| ↳ volume source | no | Hand-off line (2026-10-22c): take **Largest system volume (gal)** from `sprinkler-system-volume-takeoff` (Σ L × 0.0408·ID², NFPA 13-2025 Table A.8.2.4 default IDs) when a segment list exists. |
| **Listed QOD / accelerator trip time** (if a QOD is already elected) | **yes** (may be `unelected`) | Vendor **valve-open / accelerator** time, **not** water-delivery. Missing listing → treat as unelected. |
| **Supervisory medium** | **yes** | `air` / `nitrogen` / `unelected`. Compatibility is **per QOD listing**, not assumed. |
| **QOD listing identity** | **yes** (may be `none`) | Named model + listing (UL/FM) **or** explicit `none`. Do not silently swap Viking numbers onto a Tyco riser. |
| **Carrier** | **yes** | `FM DS 5-32 / DS 2-0 controlling` **or** `AXA XL overlay` **or** named other **or** explicit `n/a`. |
| **Owner delivery / zone-split posture** | **yes** (may be `none`) | Project-issued, **or explicit `empty`**. NDA → structure-only; may raise, never lower. |
| **AHJ-enforced NFPA 13 edition** | **yes** to cite | Delta baseline = **NFPA 13-2025**. Unamended **2024 I-Codes** → **13-2022**. Unpinned AHJ → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Proof method** | **yes** | `unelected` / `ITC water-delivery test` / `test manifold (named K, named orifice count)` / **`listed calculation program named by caller`**. **Unnamed software cannot carry a 30 s (or calculated-table) claim.** |
| **Caller output path** | **yes** | If unnamed, return the screen in the response and stop. |

Optional (do not block; flag `[V]` / `handoff`): K-factor of remote heads; ITC size vs branch-line; tree vs loop; residual at BOR; anti-column device y/n; number of proposed extra risers; IST companion status.

**Do not invent** a system volume, a 30 s proof, a listed-program name, a QOD SKU, or N₂ compatibility that the opened sheet does not state. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

### 2.1 Upstream consumption (do not rebuild; consume when present, else `ASSUMED`)

| Upstream Skill | Consume | Do not |
|---|---|---|
| the input packet | Packet context — **optional** (consume when present) | Rebuild the packet; retrieve `CASE_INDEX` |
| `suppression-technology-selection` | Elected wet/dry/DI; comparison-only / prohibited / `PRACTICE REFUSED` status | Elect a system family; silent-substitute SI→DI |
| `most-stringent-basis-matrix` | Delivery-time / DI-penalty rows; company wet/dry/DI fence; provisional/`[V]` | Rebuild dual-carrier BOD; silent FM↔AXA clock swap |
| `preaction-releasing-c-and-e-soo` | Named 30/60 clocks (peer **names**, does **not** prove) | Rewrite C&E; invent simultaneous DI words into Boolean |
| `itm-design-for-testability` | 30 s + remote-end criterion written into CD spec | Run fill / IST here |
| `commissioning-ist-acceptance-packet` | Witnessed test-script companion when present | Own the witness script here |
| `nitrogen-inerting-and-c-factor-gate` | Medium / fill / C-factor context | Own fill clock or C=120 here |
| `preaction-el-el-trim-election` | Valve family + QOD model as function | Write trim SKU catalog here |

If SI/NI/foam/mist is presented as BOD → **Stop** (company scope lock — stays hard). If the assignment packet is missing, or elected `system_type` is missing / `unresolved`, or dual-carrier controlling delivery / DI-penalty rows are missing when required → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged; for a missing STS token assume a company family (wet | dry | DI only) and say why.

---

## 3. Steps

### 3.1 Pin editions (enforced ≠ latest)

| Standard | Role | Shop-pinned editions |
|---|---|---|
| **NFPA 13** | Code floor: volume gates, ITC 60 s general, **hazard-graded calculated table**, DI **simultaneous** test words, QOD permission | Delta = **13-2025**. Unamended **2024 I-Codes** enforce **13-2022**. Shop codebook: **13-2007 via Viking 2010** for Table 7.2.3.6.1 / §7.2.3 / DI §7.3.2.3.1 trio; **13-2025 dry-delivery consolidated/reframed §8.2.4** (enforced-edition resolver). **Licensed 13-2025 table / 500–750 gal clause not in codebook → `[V]`. Do not invent a 13-2025 section number beyond the resolver pin.** |
| **NFPA 25** | In-service delivery comparison / QOD ITM | Latest **2026**; 2024 I-Codes typically **25-2023**. **Licensed NFPA 25 not in codebook.** Do not emit the interval table here (ITM Skill owns). |
| **FM DS 5-32** | **DC white-space 30 s** to the **single most remote sprinkler**, all preaction arrangements | **January 2026 / Interim Rev. July 2026** (verified vs raw FMDS0532.txt line 909), §2.4.3.2.1.2(D) p.16; verify as-built vs calc §3.3.3.2.4. Endpoint = **design pressure at the most remote sprinkler**, not first water at the ITC. “No interlock-type qualifier” = **`comparison-only`** vs company SI fence. |
| **FM DS 2-0** (**mirror copy**, a non-FM mirror; FM-hosted copy not pulled) | Generic delivery ladder (60/50/40/40 s) — applies only "when a maximum water delivery time is not specified" by the occupancy sheet [§2.2.1.11.1]; DS 5-32 specifies 30 s, so **under most-stringent, 30 s governs wherever FM governs** + practical ~10,000–12,000 ft² system-size experience + 30-minute **air** fill (air fill is **not** this Skill’s clock) | **October 2021 / Interim Rev. January 2024**. Ladder §2.2.1.11.1; system-size experience §2.2.1.11.3 |
| **AXA XL** DC white paper | DI penalty = **+30 % area AND nitrogen-fill**. **No 30 s numeric gate** in the shop AXA note | **March 2026** |
| **QOD listings (opened)** | Accelerator trip / listed volume / medium | See Step 3.6 primary table + 3.6.1 corpus pointers. Pins are the **opened PDF rev dates**, not “current web.” |

Look up **by title**: *The Design practice*; *Enforced-vs-latest edition resolver*; *Dry-pipe & double-interlock air supply and water delivery*; *Data-center sprinkler and preaction design*; *FM DS 5-32 insurer design basis*; *AXA XL insurer design basis*; *Nitrogen inerting and internal corrosion control*.

Consume the assignment packet if present (optional). Do not rebuild it. Do not run `calcs` except: gallons come from `sprinkler-system-volume-takeoff` (`calcs` op `pipe_volume`, 2026-10-23) — consume its zone total, do not recompute. No `calcs` op exists for trip+transit delivery time (`calcs` README: "Not SprinkFDT / water-delivery-time"). Do not run SprinkFDT.

**Overlay traps:** (1) Quoting “NFPA 13 = 60 s” for a data hall is **three errors**: 60 s is the **general ITC / one-sprinkler sizing** route; the **calculated** OH analogue is **50 s / two most remote** (13-2007 Table 7.2.3.6.1 via Viking; same value held [CODE NFPA 13-2025 Table 8.2.4.3.2 (Ordinary Group 1/2: 2 sprinklers, 50 s); 2019 Table 8.2.3.6.1; 2013 Table 7.2.3.6.1;, ; 2007 wording `[V]`]); the **FM DC** number is **30 s / one most remote**. (2) AXA’s DI lever is **area + N₂**, not a 30 s clock — do not blend. (3) Vendor **quarterly** DI tests that run **detection first, then ITC** are **not** the NFPA DI water-delivery test (*simultaneous*).

**Screens, not a listed closeout.**

- An inspection checkbox such as "water delivery time, dry systems over 750 gallons only" is an inspection trigger. It is not an FM design waiver, and it is not universal.
- A calculated pass at an NFPA one-sprinkler time can still fail an FM 30 s criterion. A quick-opening-device trip time is not a delivery proof.
- The endpoint is design pressure at the most remote sprinkler, not first water at the inspector's test connection (FM DS 5-32 §2.4.3.2.1.2(D) and FM DS 2-0).
- Double-interlock does not inherit the dry-pipe 750 gal quick-opening exemption. NFPA 13 §8.3.2.3 (2019, 2022, and 2025): at most 500 gal, or 60 s, or a listed calculation. There is no 750 gal path in that section.
- The screen `t = t_det + t_rel + t_exh + 60·V/Q_fill` in `calcs` is optimistic. A pass is necessary and not sufficient, and it is never a 30 s closeout. Pass `system_type:"di"` for double-interlock. The double-interlock exemption cap is 500 gal regardless of a quick-opening device (NFPA 13-2019/2022/2025 §8.3.2.3.1.1). The 750 gal quick-opening path is dry pipe only (NFPA 13-2025 §8.2.4.2.2; 2022 §8.2.3.4).
- Where FM DS 5-32 applies, the data-center target is at most 500 gal and at most 30 s to the most remote sprinkler. Thirty seconds is the insurer criterion, not the NFPA code floor. A zone over 500 gal does not take the dry-pipe 750 gal exemption.
- Exhaust time moves the result. Verify the allowance with the engineer of record. Splitting a large zone is a layout lever. This screen does not prove the split.
- A local 60 s checklist, a 4 s accelerator trip, and a vendor slide are not a delivery time and not a project gallon figure. Gallons come from the pipe takeoff.

**Trip and transit.** The 2008 IAFSS dry-pipe paper splits trip (blow-down) from transit (unsteady flow with trapped air). `60·V/Q` is not a transit model. It can over-predict transit several times, and a no-accelerator model can miss a deep-subsonic case. A zone that fails `60·V/Q` is unproven, not failed. One that passes is not proved. On a one-head FM criterion, an accelerator is required once the trip term alone can use up the 30 s budget, on the order of 400 gal at 15 psig in the published screens. The UL 1486 cap cited for that accelerator family is 2,250 gal. Any "meets 30 s" claim still needs a listed delivery program or a witnessed remote test. Do not copy another layout's gallon target.

### 3.2 Confirm prerequisites — consume, don’t redo

`suppression-technology-selection` already pinned `wet` | `dry` | `double-interlock`. If type is missing → `ASSUMED` company family (wet | dry | DI only, with why), flagged — not a Stop. If still **wet** with no dry clock → **N/A**. If SI/NI presented as BOD → **Stop** (`RFI-variance`). This Skill does **not** pick SI vs DI.

**Out of scope — emit a hand-off row, do not continue:**

- Occupancy / HC / OH → occupancy-hazard-fork
- Density × area / dry +30 % / 2,500→3,500 → density-area-dry-increase
- Pump envelope / hydrant curve → pump-envelope / hydrant-supply-curve
- Node-by-node tree / SprinkFDT → hydraulic-tree / **not this Skill**
- C=120 / 98 % / generator vs cylinders → **nitrogen-inerting-and-c-factor-gate**
- Low-air / LOW AIR ALARM / SI vs DI Boolean → **preaction-releasing-c-and-e-soo**
- Valve-room El/El trim catalog / SKU schedule → **HAND OFF — preaction-el-el-trim-election.** Do not write a trim catalog here.
- ITM interval tables / CD features checklist → **itm-design-for-testability** (writes 30 s + remote-end into spec; does not run fill)
- Witnessed acceptance / IST script → **commissioning-ist-acceptance-packet**

Air-supply **30-minute fill**, AMD-per-system, and compressor CFM live in *Dry-pipe & double-interlock air supply and water delivery* and are consumed, not rebuilt. They are **not** the water-delivery clock.

### 3.3 Three-layer union — five parameters, separately

Do **not** MAX whole sheets.

| Parameter | What you elect | Union rule | Status note |
|---|---|---|---|
| **A. Delivery-time gate** | seconds **and** how many heads / where measured | Shortest time **and** most severe venting (fewer heads, more remote) among layers that actually apply. FM DS 5-32 **30 s / 1 most remote** beats NFPA OH **50 s / 2** **and** NFPA general **60 s / ITC**. AXA with **no 30 s number** does **not** donate a clock; it donates the DI **area + N₂** lever (other Skills). | SI/NI clock facts → `comparison-only` only |
| **B. Volume gates** | 500 gal / 750 gal / listed-QOD waiver vs calculated proof | Code volume exemptions are **code-floor only**. They do **not** waive an FM **30 s** DC gate. Owner may force smaller zones. the local inspection checklist >750 = inspection trigger ≠ waiver. | DI cap [CODE 2019/2022/2025 §8.3.2.3]: 500 gal / 60 s / calculated |
| **C. Proof method** | ITC water test / test manifold / **listed program named by caller** | A 30 s (or calculated-table) **claim** requires a **named** listed program **or** a measured water test. Unnamed software → **no claim** → `unresolved`/`handoff`. | Never invent grounded 30 s |
| **D. QOD vs volume-cut vs extra risers** | hardware vs split the largest volume | First-order term is **volume**. QOD is a **valve-open** lever. Extra risers **are** volume-cut. Pick the combination that can actually be **proved** under Parameter A. | SprinkFDT Pass ≠ FM 30 s |
| **E. Air vs N₂ × this QOD** | medium compatibility of the **elected** device | Listing text of the **opened** sheet. Silent sheet ≠ listed for N₂. Hand C-factor / purity to the nitrogen Skill. | QRS-2 N₂ silence stays visible |

**Do not MAX whole layers.** An AXA-only job does **not** inherit FM 30 s by silent swap. An FM hall that elects air still owes the **30 s** clock even if N₂ is unelected. Company SI fence is not lifted by FM’s “every preaction arrangement” wording.

### 3.4 Parameter A — 60 s vs 30 s fork (cite edition)

**NFPA 13-2007 via Viking Dry System Technical Manual (2010) — `[V]` vs 13-2025:**

| Time | NFPA 13-2007 Table 7.2.3.6.1 (sprinklers open) | FM DS 2-0 §2.2.1.11.1 | FM DS 5-32 Jan-2026 |
|---|---|---|---|
| **60 s** | **Light — 1** | **Option A — 1 most remote** | — |
| **50 s** | **Ordinary I & II — 2** | **Option B — 2 on most remote branch, NONSTORAGE** | — |
| **40 s** | High piled — 4 | Options C/D storage | — |
| **30 s** | — | — | **§2.4.3.2.1.2(D) — 1 most remote, DATA CENTER / every preaction arrangement** |

**Volume / ITC gates (13-2007 §7.2.3, echoed by Reliable Bulletin 323 July 2023 p.3; 2007 wording not retrieved, `[V]` (re-checked 2026-10-22: code edition holds 2007 §7.2.3 as page images p36–37 only, with no text layer, so it stays `[V]`); same 500 / 750 gal gates held [CODE NFPA 13-2013 §7.2.3.3, §7.2.3.4, A2 ; 13-2019 §8.2.3.3, §8.2.3.4; 13-2025 §8.2.4.2.1, §8.2.4.2.2; ]):**

- **≤ 500 gal (1,893 L)** — permitted **without** a QOD; **no** specific delivery requirement to the ITC (code floor).
- **> 500 and ≤ 750 gal (2,839 L)** — same exemption **with** a listed QOD (60 s to ITC **may be waived**).
- **> 750 gal** — must meet **60 s to the ITC**, **or** be calculated with a **listed** program (trip + transit + compression), **or** be verified on a **test manifold** simulating the required number of orifices at the **same K-factor**.

**Double-interlock trio (13-2007 §7.3.2.3.1.1/.1.2/.1.3; current [CODE 2019/2022/2025 §8.3.2.3.1.1–.1.4]):** distinguishing words are *with the detection system activated **and** the inspector's test connection opened **simultaneously**.* A DI trip test that fires detection first and then opens the ITC **is not the code water-delivery test** and will read short. Write **simultaneously** into the acceptance procedure.

**13-2025 delta (resolver, not licensed primary):** dry-system water-delivery **consolidated/reframed into §8.2.4** [CODE NFPA 13-2025 §8.2.4, §8.2.4.1 to §8.2.4.5, Table 8.2.4.3.2; 2019 equivalent §8.2.3, Table 8.2.3.6.1; ]. Report the delta; **do not invent** the 2025 table rows.

**How to read a DC hall:**

- **FM-insured white space:** Parameter A = **30 s to the single most remote sprinkler** (DS 5-32). Endpoint is **design pressure at the most remote sprinkler, not first water at the ITC**.
- **Code-only, no FM 5-32:** do **not** call it a flat 60 s. State the **ITC 60 s** route **and** the **calculated hazard table** (`[V]` vs 13-2025). OH analogue = **50 s / 2 heads**.
- **AXA-only:** no 30 s numeric in the shop AXA note. Do **not** invent 30 s. DI still pays **+30 % area AND nitrogen-fill** (other Skills).
- **Dual-carrier FM + AXA:** 30 s (FM) **and** N₂ on DI (AXA) — **both**, separately. Not a blend into one number.
- **SI/NI sheet facts (including FM “no interlock qualifier”):** `comparison-only` evidence only — **never** controlling Parameter A on company BOD.

**Delta line to always print:** DS 5-32’s **30 s / 1 head** is a **~40 %** cut on the NFPA 13 Ordinary-Hazard **calculated** criterion (**50 s / 2 heads**, held [CODE NFPA 13-2025 Table 8.2.4.3.2 (Ordinary Group 1/2: 2 sprinklers, 50 s); 2019 Table 8.2.3.6.1; 2013 Table 7.2.3.6.1;, ; 2007 wording `[V]`]), **and** a **50 %** cut on the **60 s ITC** slogan.

### 3.5 Parameter D — accelerator vs volume-cut vs extra risers

**First-order term is volume.** More, smaller preaction zones beats one large one. FM DS 2-0 §2.2.1.11.3 experience limits a system to **~10,000–12,000 ft²** to hit **FM’s own (lenient vs 30 s) ladder**. Extra risers **are** the volume-cut.

**QOD / accelerator** speeds **valve operation** (destroys dry-valve differential, or electrically signals the releasing panel). It does **not** move water through 800 ft of pipe. Use it when:

- code **750 gal** waiver is the only clock (not an FM 30 s hall), **or**
- listed program / test still shows the **valve-open** slice is the binding delay, **and**
- the device is **listed with this valve family and this medium**.

**Do not** treat QOD as a substitute for splitting a hall that cannot make **30 s**. SprinkFDT “Pass” vs NFPA does **not** prove FM ≤30 s.

**Other drawing levers** (consume from *Dry-pipe & double-interlock air supply and water delivery*; do not redesign occupancy heads here): do not shrink ITC below branch-line size; prefer **K ≥ 8.0** when the 30 s clock is live (collision with reflexive K5.6 QR — flag, hand head schedule to the head-selection Skill); **center-feed tree, not loop** (FM **permits** loops in nonstorage — permitted ≠ advisable at 30 s); keep residual up; listed **anti-column** device (delivery-time protection on a 30 s hall, not the low-pressure “column defeats the valve” folklore).

**2/3 rule — schematic sanity check, not a 30 s proof** (Viking Appendix A via the air-supply note):

```
Q_min,gpm >= (2/3) * V_gal # supply capable of 2/3 of system volume per minute
t_fill,s ~ 60 * V / Q # seconds to displace volume at Q; NOT trip+transit+compression

example (do not copy onto a job):
 V = 1200 gal → Q_min = 800 gpm
 if residual Q at the riser is only 400 gpm, 60*1200/400 = 180 s → volume-cut or more risers; a QOD cannot invent 400 gpm
```

Show this arithmetic in the BOD when a zone is oversized relative to its riser. **It is not listed-program delivery.** Compression, tree geometry, and K-orifice venting are missing.

### 3.6 Parameter E — N₂ vs air compatibility of each opened QOD

**Trip time ≠ delivery time.** Quote the vendor’s own fence, then stop.

| Device | Opened pin | Listed with | Medium in **this** sheet | Listed volume / other cap | Listed trip / operate (valve, not water) | Valve families on **this** sheet |
|---|---|---|---|---|---|---|
| **Viking Model EA-1** Electronic Accelerator | **F_041523 Rev 09 June 2025**; P/N **27327** | **FM Approved** max wwp **250 PSI (17 bar)**; **cULus / UL 1486** | **air/nitrogen** throughout (samples air/N₂ **twice per second**) | UL 1486 **maximum system capacity 2,250 gal (8,517 L)** | **“operates the preaction or dry pipe system within four seconds”**; activate on **> 0.1 PSI/s (0.007 bar/s)** after **three consecutive** samples | DI Electric/Pneu-Lectric: VXD 4–8" (10" loose trim), Model F 4–8"; dry: VXR 4" & 6", Model F 4" & 6". Panel: **VFR-500** (up to **two** DI or **four** dry). Max rated air/N₂ **70 PSI (4.8 bar)** |
| **Viking Model D-2** Accelerator | **F_010898 Rev 01 December 2025**; P/N **09881** | **UL Listed: VJPZ**; **FM Approved** accelerators with built-in anti-flood | **“clean, dry, oil-free air (or nitrogen)”** | **“Refer to NFPA-13 for maximum system size”** — **no gallon figure on this sheet** | Mechanical differential; **no numeric trip seconds** on this sheet | Differential **dry pipe** (Model F all sizes trim kit 09730; VXR trim kit 24112-1). **Not** a DI electronic accelerator on this sheet. **Never exceed 60 psi (4.1 bar)** system air |
| **Tyco Model QRS-2** Electronic Accelerator | **TFP1122 JANUARY 2026**; QRS-2 P/N **100300**; Potter **4410G3** | **UL 864 / ULC S527**; **FM Approved**; **CSFM 7165-0595:113** | Sheet language is **system air pressure** only. **The word nitrogen does not appear in TFP1122 as opened.** → **N₂ compatibility `[V]` / not established by this sheet. Do not invent it.** | **No gallon cap on this sheet** | **No numeric trip seconds.** Design criteria: **quick operation does not ensure** AHJ water-delivery time. Test: compare trip to **previous tests**, not to 30 s | Dry: **DPV-1 2½–6 in.** (TFP1020). DI El/El: **DV-5A 1½–8 in.** (TFP1466). Panel: Potter **4410G3**, Program **#14** dry / **#13** DI. Up to **four** QRS-2 on dry; **one** on DI |
| **Reliable Model B1** Accelerator + Accelo-Check | **Bulletin 323 July 2023** ( — **no in **) | **UL**; **ULC up to 1,500 gal (5,678 L)**; **FM**; **LPC** | **“pressurized air or nitrogen in the piping”** (product description) | **UL Listed to 1,500 gal; “this capability is also approved by FM.”** Min pneumatic **15 psi** to operate | **3–4 psi (21–28 kPa)** top-vs-middle ΔP to open. Figure 2 = **accelerator operating time vs system size, one sprinkler**, 25–50 psi — **graph not a water-delivery table; not digitized.** p.3: water delivery **significantly exceeds** accelerator time | Reliable **only** (not listed for other makers): D, EX, DDX-LP, DDX Type F / Type PL DI, FX |

**EA-1 / QRS-2 common fence (quote, then obey):** water delivery is determined by **piping configuration and volume**, **air/N₂ pressure at accelerator trip**, **number and orifice of open sprinklers**, **water-supply characteristics**. DI water delivery **also** assumes electric detection **before** the first sprinkler **on the vendor’s listing narrative** — that is a **listing assumption**, not a substitute for NFPA’s **simultaneous** DI test. **Keep both visible.**

**QRS-2 quarterly DI procedure (TFP1122 Testing §2.b):** *first operate the detection system and then open the ITC.* **Do not file that as the NFPA DI water-delivery proof.**

**Potter panel `QRS` Program #14** (air-supply note run-130) is an **electrically initiated** dry-system trip from **manual stations**. It is **not** this Tyco QRS-2, **not** a listed QOD credit, and **gets no delivery-time credit** from this Skill.

#### 3.6.1 Also opened / corpus-mined QOD pointers (catalog not exhaustive)

Thin pointers from *Dry-pipe & double-interlock air supply and water delivery* ( 311, 324). **Still trip ≠ delivery.** Do **not** invent N₂/trip numbers beyond what the dry-pipe note already pins. Unelected / other OEM → open the sheet or **hand off** to `preaction-el-el-trim-election`. **This catalog is not exhaustive.**

| Device | Corpus pin | Thin fence (do not invent beyond note) |
|---|---|---|
| **Victaulic Series 746 / 746-LPA** | I-746/746-LPA 4603 REV D 03/2012 — Run **324** | Actuator-exhaust QOD; **746 ≠ 30 s**; **746-LPA only < 20 psi** (else 746); **757P banned** with 746 unless tank+regulator; FireLock NXT air **13–18**. Do not paste Tyco/Viking trip numbers onto Victaulic trim. |
| **Tyco VIZOR EDPA** | TFP1105 AUGUST 2025 — Run **309** | Electronic QOD for DPV-1 **4 & 6**; NOTICE: quick VIZOR ≠ AHJ / FM ≤30 s delivery. |
| **Tyco ACC-1** | TFP1112 APRIL 2026 — Run **308** | Mechanical QOD for DPV-1 **2½–6**; NOTICE: quick accelerator ≠ water-delivery compliance. |
| **Viking Model E-1** | F_071692 Rev 21.1 April 11 2022 — Run **311** | Atmosphere-vent QOD (≠ D-2 intermediate-chamber); air **or nitrogen** on sheet; **DO NOT exceed 60 psi** on F path; does **not** waive FM ≤30 s. |

### 3.7 Parameter C — forbid inventing a 30 s proof

**★★ STOP. Do not write “meets 30 s” (or “meets 50 s / 60 s calculated”) without one of:**

1. **Listed calculation software named by the caller** (program + version as they named it), run on **this** tree and **this** volume, predicting **trip + transit + compression**, **or**
2. A **measured** water-delivery test (remote ITC or DS 5-32 2 in. test line / test manifold at the **required K and orifice count**).

**Unnamed SprinkCAD / HydraCAD / “the usual listed program” is not a name.** If the caller did not name the program → emit **“30 s unproved”** with status `unresolved` or `handoff`, and elect volume-cut / extra risers / QOD as **candidates**, not as a passed gate. Do **not** mark the claim `grounded`.

This Skill **does not run SprinkFDT** and **does not invent nodes**. SprinkFDT TFP2017028 Pass rows are **comparison arithmetic**, not Parameter C proof.

Vendor **4 s** (EA-1) or a Figure-2 accelerator curve is **Parameter D hardware**, not Parameter C proof.

### 3.8 Show-and-verify (independent arithmetic; no `calcs` in this Skill)

Print whenever volume or the 30 s slogan is argued:

```
# code-floor volume gates (13-2007 via Viking/Reliable; [V] vs 13-2025)
if V <= 500: code ITC clock may be N/A (no QOD required)
if 500 < V <= 750: code 60 s ITC may be waived IF listed QOD is installed
if V > 750: code 60 s ITC OR listed program OR test manifold

# FM DC overlay (DS 5-32 Jan-2026 §2.4.3.2.1.2(D)) — does not inherit the 500/750 waiver
t_req_FM = 30 s to 1 most remote sprinkler at DESIGN PRESSURE # if FM 5-32 controls

# delta vs NFPA OH calculated (13-2007 Table 7.2.3.6.1 [V]; OH 2 heads / 50 s held: 13-2013 Table 7.2.3.6.1, 13-2019 Table 8.2.3.6.1, 13-2025 Table 8.2.4.3.2; )
(50 - 30) / 50 = 0.40 # 40 % shorter
# vs ITC slogan
(60 - 30) / 60 = 0.50 # 50 % shorter

# 2/3 schematic (Viking) — NOT a listed delivery calc
Q_2_3 = (2/3) * V_gal # gpm
```

**VERIFY:** gallons on the line are the **caller’s largest zone**, not a demo 1,200 gal. If FM controls, a 600 gal zone with a QOD is **not** “done” — it still owes **30 s** proof. the local inspection checklist >750 inspection checkbox does **not** clear FM.

### 3.9 Handshakes (reciprocal — required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `preaction-releasing-c-and-e-soo` | **Names** 30/60 clocks; DI simultaneous vs sequential words in SOO; does **not** prove fill | **Proves** delivery or marks `unresolved`/`handoff` unproved |
| `itm-design-for-testability` | Writes **30 s + remote-end** into CD spec / features; does **not** run fill | Supplies the prove-side criterion status |
| `commissioning-ist-acceptance-packet` | **Owns witnessed** test script / IST baseline | Names measured-test method when elected; does not witness |
| `nitrogen-inerting-and-c-factor-gate` | Medium air vs N₂, generator vs cylinders, C=100 vs earned 120, **30-minute FILL** | Only whether the elected QOD is listed for that medium |
| `preaction-el-el-trim-election` | Valve-room **trim SKU** / El/El hardware | Pass: valve family + QOD model + need for anti-flood / Accelo-Check / solenoid / CoilKeeper as a **function**, not a part table |

Emit rows:

- `HAND OFF — nitrogen-inerting-and-c-factor-gate: medium air vs N₂, generator vs cylinders, C=100 vs earned 120, 30-minute FILL (compressor half). This Skill only asked whether the elected QOD is listed for that medium.`
- `HAND OFF — preaction-el-el-trim-election. Do not write a trim schedule or SKU list here.`
- `HAND OFF — preaction-releasing-c-and-e-soo: DI simultaneous vs sequential; low-air is alarm-only on SI (comparison) and a trip input on DI. Peer named clocks; this Skill proves or marks unproved. Do not rewrite the matrix.`
- `HAND OFF — itm-design-for-testability: 30 s + remote design-pressure criterion into CD; this Skill does not write the interval table.`
- `HAND OFF — commissioning-ist-acceptance-packet: witnessed ITC / manifold / as-built delivery test script.`
- Extra risers / zone count that changes hydraulic demand → density-area-dry-increase consumes the new zone map; this Skill does not re-run `qd`.
- Tree friction / remote-head pressure → hydraulic-tree / listed delivery program **named by caller**.

---

## 4. Output

A **dry/preaction water-delivery screen**. Write **only** to the caller-named path.

Minimum: Hard-scope gate + status register (gate / A–E / proof claim); edition-pin block (name the holes: 13-2025 §8.2.4 table and 500/750 mapping now held (2007 wording still `[V]`), NFPA 25, ANRACI DI 500/750); inputs echoed including packet + STS + matrix; Parameter A 60-vs-30 fork with **section AND edition** + design-pressure endpoint; Parameter B volume vs FM overlay (a local inspection checkbox inspection ≠ waiver); Parameter C proof method (**named software or unproved** — never grounded without it); Parameter D QOD vs volume-cut vs extra risers + 2/3 show-and-verify; Parameter E QOD × air/N₂ from **opened** sheets + thin corpus pointers; vendor fence that trip ≠ delivery; reciprocal C&E / ITM / IST / trim / nitrogen hand-off rows; Δ vs 13-2025; `[SYN]`/`[V]` register.

Do **not** emit occupancy schedule, density×area `calcs`, pump nameplate, El/El trim catalog, C&E matrix, C-factor / 98 % purity, or a SprinkFDT tree. Do **not** emit PLACEHOLDER text.

---

## 5. Stop

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

1. Assignment packet missing → not a Stop (packet optional); proceed and flag `ASSUMED`. 2. STS election missing / `unresolved`, or system type missing / still **wet** with no dry clock (N/A vs Stop as applicable). 3. SI/NI (or other prohibited preaction) presented as **BOD** → `RFI-variance`. 4. Foam BOD. 5. Mist design request (`PRACTICE REFUSED` / `RFI-variance`). 6. Dual-carrier controlling delivery-time / DI-penalty matrix rows missing when required → `unresolved`. 7. Largest volume (gal) unpinned. 8. Unpinned carrier. 9. Unpinned AHJ NFPA 13 edition. 10. Caller asks to **invent a 30 s (or 60 s calculated) proof** without **naming** listed calc software (or a measured water test), or to mark that unproved claim grounded.

QOD = `none` is **not** a Stop — it is a lever **not taken**; volume-cut / extra risers / listed-program proof remain.

---

## 6. Citations (section AND edition)

**NFPA 13-2007 via Viking Dry System Technical Manual 2010** (`dry-pipe-and-double-interlock-air-supply-and-water-delivery`): Table **7.2.3.6.1** 15/60/50/45/40 s; §**7.2.3** 500 / 750 gal; DI §**7.3.2.3.1** simultaneous; Appendix A levers + **2/3 rule**; 60 psi dry-valve air ceiling. **2007 wording `[V]` (not retrieved). The 15/60/50/45/40 s table and 500 / 750 gal gates are held [CODE NFPA 13-2013 §7.2.3, Table 7.2.3.6.1, A2 ; 13-2019 §8.2.3, Table 8.2.3.6.1; 13-2025 §8.2.4, Table 8.2.4.3.2, ]; the other items here stay `[V]` vs NFPA 13-2025.**

**NFPA 13-2025** (enforced-edition resolver, not licensed primary): dry water-delivery **§8.2.4** consolidation [CODE NFPA 13-2025 §8.2.4, Table 8.2.4.3.2, ]. Unamended 2024 I-Codes floor = **13-2022**.

**FM DS 5-32 January 2026:** §**2.4.3.2.1.2(D)** p.16 **≤30 s** to single most remote sprinkler at **design pressure**; §**2.4.3.2.1.2(B)/(C)** SI=wet demand, DI=dry demand (other Skill / comparison context); §**3.3.3.2.4** verify as-built vs calc. “No interlock-type qualifier” = **`comparison-only`** vs company SI fence.

**FM DS 2-0 Oct-2021 / Jan-2024:** §**2.2.1.11.1** 60/50/40/40 s ladder; §**2.2.1.11.3** ~10,000–12,000 ft² experience.

**AXA XL Mar-2026:** DI **+30 % area AND nitrogen-fill** — **no 30 s gate** in the shop note.

**Viking EA-1 F_041523 Rev 09 June 2025:** 4 s operate; 0.1 PSI/s × 3 samples; UL 1486 **2,250 gal**; FM 250 psi wwp; air/**nitrogen**; VFR-500.

**Viking D-2 F_010898 Rev 01 December 2025:** UL VJPZ; FM anti-flood accelerator; air **(or nitrogen)**; NFPA-13 for max size; 60 psi ceiling.

**Tyco QRS-2 TFP1122 January 2026:** UL 864/ULC S527 + FM; trip ≠ delivery; DPV-1 / DV-5A; **N₂ not in sheet**.

**Reliable Bulletin 323 July 2023:** 3–4 psi ΔP; UL/FM **1,500 gal**; ULC 1,500 gal; air **or nitrogen**; NFPA 500/750 restatement; trip ≠ ITC water.

**Corpus-mined QOD pointers (dry-pipe note):** Victaulic I-746/746-LPA Run **324**; Tyco ACC-1 TFP1112 Run **308**; Tyco VIZOR TFP1105 Run **309**; Viking E-1 F_071692 Run **311** — still trip ≠ delivery.

**Trip and transit method:** IAFSS 9th Symposium (2008), dry-pipe trip and transit. Method source, not a criterion source. Equations 1–3 are the trip. Equations 4–13 are the transit. Table 2 is 40 freezer cases. Do not copy a layout's gallons from that paper onto a hall.

**Absent:** a licensed NFPA 13-2025 delivery table in this pack; NFPA 25 intervals (the ITM method owns those); a QRS-2 nitrogen listing; a digitized accelerator operating-time graph; a named listed delivery program unless the caller supplies it. Nothing here closes a 30 s proof by itself.

---

## 7. Design practice

1. Three-layer, most stringent, on **five parameters separately**: delivery-time gate, volume gates, proof method, QOD vs split, medium × this QOD. Owner may raise, never lower. Company fence: wet | dry | DI only; SI/NI Stop + `RFI-variance` / comparison-only; foam prohibited; mist PRACTICE REFUSED.
2. Per-parameter, not per-layer. Never MAX whole sheets. Never blend AXA N₂ into an FM 30 s clock or vice versa. Never reopen SI as BOD from FM’s “every preaction arrangement” wording.
3. **Accelerator time is not water-delivery time.** 30 s is a design output you **prove**, not a QOD advertisement. Unproved → `unresolved`/`handoff`, never grounded.
4. Current editions; enforced ≠ latest. Do not invent 13-2025 table rows.
5. Show-and-verify: `(50−30)/50 = 40 %`; `(60−30)/60 = 50 %`; `Q_2/3 = (2/3)·V`. No `calcs` in this Skill.
6. Status register every run on gate + A–E + proof claim: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`.
7. Upstream (packet optional; gaps → `ASSUMED`): packet + STS (`wet`|`dry`|`DI`) + matrix delivery/DI-penalty rows. Caller-path-only. **NO PLACEHOLDER.**
8. Honesty. Worked delivery packages exist (§3.1) — use them as method, never as another job's gallons, and none of them is a listed-program closeout. Do not invent gallons, software names, or a 30 s closeout. QRS-2 N₂: **sheet is silent — both the silence and the other makers’ “air or nitrogen” stay visible.** QOD catalog not exhaustive.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Wet / dry / DI election (SI/NI comparison-only) | suppression-technology-selection |
| Occupancy / HC / OH | occupancy-hazard-fork |
| Density × area / dry +30 % / 2,500→3,500 | density-area-dry-increase |
| Dual-carrier BOD | most-stringent-basis-matrix |
| Pump envelope / hydrant curve | pump-envelope / hydrant-supply-curve |
| Node-by-node tree / SprinkFDT | hydraulic-tree / **not this Skill** |
| C=120 / 98 % / generator vs cylinders / 30-min **fill** | **nitrogen-inerting-and-c-factor-gate** |
| Low-air / C&E / SI vs DI Boolean (names 30/60; does not prove) | **preaction-releasing-c-and-e-soo** |
| El/El / valve-room trim catalog | **preaction-el-el-trim-election** |
| Head K / QR listing schedule | sprinkler-head-selection (flag K vs 30 s; do not pick heads here) |
| ITM interval tables / CD features (writes 30 s criterion) | itm-design-for-testability |
| Witnessed IST / acceptance script | commissioning-ist-acceptance-packet |

---

## Check before you finish

1. Hard-scope gate: wet|dry|DI only; SI/NI-as-BOD → Stop `RFI-variance`; foam/mist Stop; wet/no dry clock → N/A. Emit status on gate. 2. Check packet (optional) + STS + matrix delivery/DI-penalty rows; missing → `ASSUMED` (flagged), not a Stop. 3. Confirm other inputs; Stop tests. 4. Pin editions; name the 13-2025 / ANRACI / NFPA 25 holes. 5. Union five parameters separately; status on each. 6. Print 60 s vs 30 s fork with **section AND edition** + **design-pressure endpoint**; do not flatten NFPA to 60 s; SI clock facts = `comparison-only`. 7. Volume gates vs FM overlay (500/750 and the local inspection checklist >750 inspection do not waive 30 s). 8. Elect QOD vs volume-cut vs extra risers; 2/3 sanity; SprinkFDT Pass ≠ FM 30 s. 9. QOD × air/N₂ from **opened** sheets + thin corpus pointers; catalog not exhaustive. 10. Proof method: **named listed software or unproved** — never invent / never grounded 30 s without it; status on proof claim. 11. Reciprocal hand-offs: C&E (names) / ITM (criterion) / IST (witness) / N₂ (fill) / El-El (trim). 12. Δ vs 13-2025. 13. Honesty: trip ≠ delivery; no PLACEHOLDER; cite the worked packages (§3.1) as method only — do not copy their gallons and do not invent a listed-program closeout. 14. Count the valve stub in system volume (§9). An FM margin **<5 s** is a hold-point, not a pass. 15. Write **only** to the caller-named path.

---

## 9. Valve stub and the FM margin hold-point

Count the riser and valve stub downstream of the double-interlock valve in system volume V. A zone total that stops at the branch main and omits that stub is short.

Worked `[SYN]`: zone 219.12 gal and 28.53 s, plus an 11 ft 6 in. Schedule 10 valve stub at 18.14 gal, gives **237.25 gal / 29.98 s** against the FM DS 5-32 30 s gate (margin +0.02 s). The same volume at a fill flow of 650 gpm is 32.90 s and fails.

NFPA 13-2025 §8.3.2.3.1.1 (double-interlock at or under 500 gal may be exempt from the code delivery clock) does not waive the FM 30 s gate.

**Rule.** FM margin **<5 s**, or volume above 0.9 times the maximum volume that still meets 30 s, is a mandatory **hold-point** before issue:

1. A listed delivery program run on the design curve, including the pump where one is in the supply, or
2. A witnessed trip test at or under 30 s.
3. A manifold test under NFPA 13-2025 §8.2.4.4.1 through §8.2.4.4.3 is an acceptable proof path.

If the screen fails, the levers are: move the valve closer to the remote heads, shorten the branch run, split the zone, or add an accelerator. Verify with the engineer of record until that evidence is in hand. This screen still does not issue a pass by itself.

A maker's installation instructions are a procedure example only for how the trip and water-delivery test is run. The specification stays generic: per the maker's instructions. Do not freeze a catalog number or a document number. Those instructions give no seconds value, so the numeric hold-point stays mandatory until a witnessed trip test or a listed calculation supplies the seconds. The teaching rerun (237.25 gal / 29.98 s against the FM 30 s gate, margin about 0.02 s, under 5 s) does not close the hold-point. Paths 1 and 2 above still apply. Do not attach the teaching volume to a city or a job.
