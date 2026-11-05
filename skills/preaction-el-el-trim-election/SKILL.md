---
name: Preaction El/El trim election
description: >-
 use this when company-elected double-interlock is pinned (STS + matrix +
 releasing C&E Boolean consumed when present, else ASSUMED and flagged;
 packet optional) and you must elect the
 DI trim family (El/El vs El/Pn vs named SureFire failsafe), including the
 "what holds the prime chamber shut" air-band rule and the actuator vs
 low-air-switch collision; SI/NI-as-BOD → Stop
 RFI-variance (comparison-only); foam prohibited; mist PRACTICE REFUSED;
 status register every run — not occupancy, density, pump, C&E rewrite,
 nitrogen C-factor, QOD sizing, or CAD.
---

# Preaction El/El trim election

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Reusable DC fire-protection recipe. **This Skill ELECTS the double-interlock trim family** after `suppression-technology-selection` pinned company `double-interlock` and `preaction-releasing-c-and-e-soo` already wrote the controlling releasing Boolean. It does **not** rewrite C&E. It does **not** size QOD/accelerators (hand off to `dry-preaction-water-delivery-screen`). It does **not** elect nitrogen vs air / C-factor (hand off to `nitrogen-inerting-and-c-factor-gate`). It does **not** elect wet/dry/DI (STS owns that).

**Core thesis:** “Failsafe” is not one trim. Three families exist and they collide on **supervisory pressure** and **what happens on loss of releasing power**. **Ask what holds the prime chamber shut** — a pneumatic actuator (El/Pn, and SureFire's power-loss path) needs the actuator band; an NC solenoid (El/El) lets the air serve only the low-air switch / accelerator, so the OEM may allow a lower setting. Mixing a pneumatic-actuator band with a lower El/El low-air switch setting is a **failed election**, not a field adjustment.

**Design practice (lede):** three-layer basis (code floor × insurer × owner), most-stringent **per parameter** (actuation pair, supervisory pressure, failsafe-on-power-loss, listed solenoid/panel pair). Delta vs **NFPA 13-2025**. Cite **section AND edition**. Show-and-verify. Flag `[SYN]` / `[V]`. Status vocabulary every run: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. Company fence: this Skill’s controlling election is **DI trim only**; SI/NI → Stop + `RFI-variance` / comparison-only; **Foam prohibited**; **Mist = PRACTICE REFUSED**. Caller-path-only. **NO PLACEHOLDER.** Generic — do not copy a hall’s valve SKU or psi onto another job.

---

## 1. Hard scope gate

### 1.1 Company system-family fence (this Skill elects trim, not system family)

This Skill may emit a **controlling** DI trim-family election only when upstream already elected **double-interlock** for the zone(s) under trim:

1. **Double-interlock preaction** — controlling path for this Skill’s trim election.

Comparison-only (never elected here; never the controlling trim BOD):

- Single-interlock preaction
- Non-interlock preaction
- Any other preaction type

**Wet / dry without a DI trim need → N/A** (not this Skill). Do not invent a DI trim schedule for a wet-only or dry-pipe-only BOD.

**This Skill does not elect wet | dry | DI.** It **consumes** the STS election and listing/trim/DI rows from `most-stringent-basis-matrix` (plus the completed the input packet). Controlling company BOD for trim = **DI only**.

If the caller presents SI, NI, wet-as-trim-BOD, or dry-as-trim-BOD (with no DI zone) as the basis for this Skill’s election:

1. Record the requested election.
2. **Stop**.
3. Return an `RFI-variance` / company-fence gate.
4. Do **not** silently substitute DI.
5. Do **not** emit a controlling trim election as if SI/NI were company-elected.
6. SI sheets (e.g. Tyco **TFP1421**) may appear only as **`comparison-only`** air-band evidence — **never** a controlling family row.

### 1.2 Prohibited or handoff-only media

| Medium | Company status | This Skill action |
|---|---|---|
| Double-interlock water sprinkler (trim election) | Permitted when DI elected upstream | Emit controlling trim-family election |
| Wet / dry with **no** DI zone | N/A | Mark N/A; do not invent DI trim |
| Single-interlock / non-interlock / other preaction | Comparison-only | Record; SI/NI-as-BOD → **Stop** `RFI-variance` |
| Foam / foam-water | **Prohibited** | **Stop**; do not design foam trim |
| Water mist | **`PRACTICE REFUSED`** | Record evidence if cited; do not elect/design |
| Clean agent / hybrid / hypoxic / aerosol / CO₂ / water spray / deluge | Handoff-only | Not this Skill |

**Foam is prohibited.** **Mist is `PRACTICE REFUSED`.** FM sheet language that mentions mist does **not** authorize mist election or design here.

### 1.3 What this Skill produces

| In scope | Out of scope |
|---|---|
| Parameters A–D trim-family election + status register | System-family election (STS) |
| Collision check (~30 psi actuator vs 7–15 psi El/El) | Occupancy / HC / OH classification |
| Listed valve + solenoid + panel **by function + listing** | Density × area `calcs` |
| Supervisory / low-air setpoints from **elected** opened sheet | Dual-carrier BOD rebuild (consume matrix) |
| Reciprocal handshakes (C&E / QOD / N₂ / STS / ITM) | Rewriting `preaction_trip` Boolean |
| Consume packet + STS DI + matrix + C&E Boolean | QOD / accelerator **sizing** / 30 s proof |
| | Nitrogen C-factor / 98 % / generator SKU |
| | CAD / trim isometric |
| | Inventing psi / SKU / battery hours as hall defaults |

### 1.4 Status register (mandatory every run)

Emit a status token on **(a)** the Hard-scope gate, **(b)** each of Parameters A–D, **(c)** the collision check, and **(d)** the listing pair:

| Token | Meaning on this Skill |
|---|---|
| `grounded` | Controlling DI + edition + elected family supported by **mined** / opened WHOLE sheet |
| `provisional` | Directionally pinned; PDF-held sheet or edition hole flagged `[V]` — **never silent `grounded`** |
| `unresolved` | STS / matrix / C&E Boolean / carrier / AHJ edition / failsafe posture not given — carried as `ASSUMED` (value + why) and flagged; not a Stop (the packet itself is optional) |
| `comparison-only` | SI/NI, TFP1421 air band, FM preference ranking — never controlling trim BOD |
| `handoff` | Peer owns next action (C&E Boolean restamp on Family 3; QOD size; N₂ medium/C; ITM features) |
| `RFI-variance` | SI/NI/foam/mist (or wet/dry-as-trim-BOD with no DI zone) presented as BOD |

**PDF-held Reliable Bulletin 750 / Viking SureFire F_051704 / FireFlex TOTALPAC N2 SUREFIRE → status ≤ `provisional` + `[V]` until source review WHOLE mine into .** Unopened OEM for elected valve → `provisional`/`[V]`; pressure carried as a stated `ASSUMED` value (value + why), flagged.

---

## 2. Required inputs and upstream intake

Caller must supply. Do not invent a valve model, psi default, or failsafe posture. *(2026-10-07: this means do not **silently** invent. When a needed project value is not given, use a stated `ASSUMED` value (value + why), flagged — never presented as a cited, listed, or field-verified value; never a frozen vendor SKU.)*

| Input | Required | Notes |
|---|---|---|
| the input packet (optional) | no | Packet is **optional, never a gate**. Consume; do not rebuild; do not retrieve `CASE_INDEX`. Missing → proceed from the inputs given; label filled-in values `ASSUMED` (value + why). |
| **Company-elected `system_type` from STS** | **yes** (inherited) | Must be `double-interlock` (or named DI zone list) from `suppression-technology-selection`. Missing → **not a Stop**: proceed with `ASSUMED` `double-interlock` (with why), flagged. SI/NI as BOD → **Stop** (`RFI-variance`). Wet/dry with no DI zone → **N/A**. |
| **Consumed `most-stringent-basis-matrix` listing / trim / DI rows** | **yes** when dual-carrier (or when those rows exist) | Consume; do not rebuild. Unresolved controlling listing/trim/DI row → **not a Stop**: carry the more stringent candidate value as `ASSUMED` (value + why), flagged. Never silent-swap carrier. |
| **Releasing C&E already written** | **yes** | Consume the Boolean from `preaction-releasing-c-and-e-soo`. Do **not** rewrite `preaction_trip`. If C&E still asks the failsafe question → **this Skill answers it**. |
| **Carrier** | **yes** | FM / AXA / UFC / n/a named. Dual-carrier: consume matrix rows. |
| **AHJ NFPA 13 edition** | **yes** | Delta baseline **13-2025**. Unamended 2024 I-Codes → **13-2022**. Unpinned → **not a Stop**: proceed with a stated `ASSUMED` value (value + why), flagged. |
| **Supervisory medium** | **yes** | `air` / `nitrogen` / `unelected`. Medium election lives in the nitrogen Skill; this Skill only needs it for actuator / AMD compatibility. |
| **Failsafe posture** | **yes** (may be `unelected`) | `El/El` / `El/Pn` / `SureFire-or-named-failsafe` / `unelected`. If unelected, elect here — do **not** default silently to Viking 2010 TM or any hall SKU. Status the posture. |
| **Caller output path** | **yes** | Else return the election in the response and stop. |

Optional (do not block; flag `[V]` / `handoff` / `comparison-only`): existing valve-room drawing (check for 30 psi actuator + El/El stack); SI TFP1421 air band as comparison evidence only; ITM DRAW/SPEC feature asks.

Do not invent a valve model as a hall default. Specify **by function + listing**. Owner NDA specs: structure only; may raise, never lower.

---

## 3. Steps

**Trim code pins (added 2026-10-22, pulls ):** gauges above and below the water control valve and on the air supply [CODE NFPA 13-2025 §8.3.1.5.1(1),(3); 2022 §8.3.1.3(1),(2)]; hydraulic/pneumatic/mechanical manual operation independent of detection and sprinklers [CODE 2025 §8.3.1.4 / 2022 §8.3.1.2]; test devices per detection zone in 2025 [§8.10.6.1] vs per circuit in 2022 [§8.3.1.7.1] — print the delta; detection per NFPA 72 [CODE 2025 §8.10.2]; dry-pilot air independent of system air [CODE 2025 §8.10.3.11]; aux drains where direction changes trap water, ≥1 in. valve at ≥50 gal trapped [CODE NFPA 13-2022/2025 §16.10.5.1, §16.10.5.2.1]; low-point drain sign at the valve [§16.10.5.3.7]; gauge connections with shutoff + drain [§16.13.2].

### 3.1 Pin editions

| Instrument | Role | Shop pin | Provenance |
|---|---|---|---|
| **NFPA 13** | DI definition (detection **and** sprinkler-system pressure loss). Supervisory air/N₂. | Delta **13-2025**. Enforced often **13-2022**. Licensed C-table `[V]` if unpinned. | DI cap [CODE 2019/2022/2025 §8.3.2.3]; min supervisory 7 psi [CODE 2025/2022 §8.3.2.5.2; 2019 §8.3.2.4.4; 2016 §7.3.2.4.4] |
| **NFPA 72** | Releasing-service control unit | Delta **72-2025** | [CODE NFPA 72-2025 §23.11.1]; do not invent other subsections |
| **FM DS 2-0** | FM Approved valve + solenoid + panel combination | **Oct 2021 / IR Jan 2024** §2.2.1.12.1.1 | peer-pinned |
| **FM DS 5-32** | Functional C&E on an FM DC (consume, don’t rewrite) | **Jan 2026** | peer-pinned; preference ranking = `comparison-only` |
| **Tyco TFP1466** | Current **El/El** DV-5A DI | **TFP1466 · JUNE 2026** | **mined** |
| **Tyco TFP1461** | DV-5A DI **El/Pn** peer | **TFP1461 · JUNE 2026** | **mined** |
| **Victaulic I-769N** | FireLock NXT DI **El/Pn** peer | **9452 REV C 11/2023** | **mined** |
| **Viking F_052020** | Model VXD DI **El/Pn** | **Form No. F_052020 Rev 04 December 2025** | **mined** |
| **Viking F_070889** | DI **El/Pn** peer (optional Family 2) | **Form No. F_070889 Rev 01 June 2025** | **mined** (optional) |
| **Reliable Bulletin 750** | DDX **Type D** El/El | **Feb 2024** (opened) | **PDF-held** `provisional`/`[V]` |
| **Viking F_051704** | TRIMPAC SureFire D-2/D-2B failsafe on loss of primary+secondary power | **Rev 01 May 2025** (supersedes the 2013-09-16 copy) | **mined** WHOLE (KB DI air-supply note ): listed as a unit (cULus VLTR/VLTR7; FM Approved Preaction); holding air **not printed** |
| **Viking F_052220** | Model VXD DI **Electric/Pneu-Lectric (El/El)** | **Form No. F_052220 Rev 01 November 2022** | **mined** — §6.1 Table 2 |
| **Viking F_041523** | Model EA-1 electronic accelerator (El/El rate-trigger 2nd interlock) | **Form No. F_041523 Rev 09 June 2025** | **mined** |
| **FireFlex TOTALPAC N2 SUREFIRE** | Packaged Viking-based failsafe + N₂ skid IOM | **©2023** | **PDF-held** `provisional`/`[V]` (related HP Dry FM-076E-0-13B is mined — **different doc**) |
| **Tyco FSV-1 / TFP1386** | Latch-open after trip | **Aug 2022** | fence only — **not** El/El power-fail |

**Do not** treat Viking Preaction TM **F_010808 (19 Feb 2010)** as the current El/El sheet (**mined** historical fence).

**Deleted / forbidden identifiers:** `F_052220_06` (stays forbidden). **Correction :** Viking sells the VXD in **both** forms — **F_052020 = VXD El/Pn** and **F_052220 Rev 01 Nov 2022 = VXD Electric/Pneu-Lectric (El/El)**. "VXD" alone does not name a family; identify by **form number + what holds the prime chamber**.

### 3.2 Confirm prerequisites

System type is DI. Packet (optional) + STS + matrix (when required) present. C&E Skill already wrote trip logic. If C&E still asks the “failsafe question” as a hand-off, **this Skill answers it**. Nitrogen Skill may still be unelected — record medium as input; the C-factor election (shop **C=100** design; 120 comparison-only, never a goal) belongs to `nitrogen-inerting-and-c-factor-gate`. Emit Hard-scope gate status.

### 3.3 Three-layer union — four parameters, separately

| Parameter | What you elect | Union rule | Status |
|---|---|---|---|
| **A. Actuation pair** | El/El vs El/Pn vs named failsafe | Owner/AHJ/insurer that **requires** failsafe-on-total-power-loss wins over convenience. Code **permits** several DI constructions. | mandatory |
| **B. Supervisory pressure** | Setpoint + low-air switch | **Most-stringent compatible envelope** of the **chosen** listed trim. Do not mix families. | mandatory |
| **C. Failsafe-on-power-loss** | Valve stays shut vs opens vs latch | Name the behavior. “Failsafe” without a sentence is not an election. | mandatory |
| **D. Listed pair** | Valve + solenoid + releasing panel | FM: **FM Approved combination** (DS 2-0 §2.2.1.12.1.1). Specify function, not SKU. | mandatory |

### 3.4 Vocabulary fence (El/El vs El/Pn; CROSS-ZONE)

| Label | Meaning on this Skill | Second gate |
|---|---|---|
| **El/El** = **Electric/Electric** | Switch-based DI; **both gates inside the panel** (detection circuit **and** low-air / system-pressure switch) | **No** pneumatic actuator |
| **El/Pn** = **Electric/Pneumatic** | Detection/solenoid **and** a **pneumatic actuator** held by supervisory air/N₂ | Pneumatic actuator (AMD band per OEM) |

**Viking vocabulary:** Viking "Electric/**Pneu-Lectric**" = this Skill's **El/El** (low-air switch or EA-1 = the panel's second input; Potter calls it "Electric/Electric"). Viking "Electric/**Pneumatic**" = **El/Pn**. Both forms exist on the VXD: **F_052020 Rev 04 Dec 2025 = El/Pn**; **F_052220 Rev 01 Nov 2022 = El/El**. Tyco **TFP1461** / Victaulic **I-769N** are **El/Pn**. Never label a valve by model name alone — cite the form.

**CROSS-ZONE CONFLICT:** Vendor “CROSS-ZONE DELUGE” / “DOUBLE KNOCK/CROSS ZONE” panel labels (TFP1466 Figure 4; Victaulic I-769N sample program) are **not** two smoke detection zones for water trip. On El/El, Zone 2 = **low-air / sprinkler leg**. On El/Pn, the second interlock = **pneumatic / sprinkler actuator leg**. Do **not** import Z1∧Z2 detection coincidence into company DI C&E (FM DS 5-32 §2.4.3.2.1.3.2 — do not use cross-zoned detection to activate the preaction valve — remains binding doctrine; consume, do not rewrite C&E here).

### 3.5 Family catalog (opened OEM + provenance)

**Family 1 — Electric/Electric (no pneumatic actuator).** Detection circuit **and** low-air / system-pressure switch both required.

- **Tyco TFP1466 DV-5A El/El (JUNE 2026)** — **mined:** two independent events (Zone 1 detection/pull ∧ Zone 2 low-air). Nominal supervisory **~15 psi (1.0 bar)** air or nitrogen, **irrespective of water**. Low-pressure switch **~12 psi (0.8 bar) on decreasing** from 15 (install: 3 psi below system air). Relief typically cracks **~20 psi**. Compatible with optional **Model QRS-2** electronic accelerator (TFP1120/TFP1122 host = **DV-5A El/El** — do **not** invent a VXD+QRS-2 listing). AMD-1 / AMD-3 listed; **no AMD-2** on this El/El sheet. Solenoid separately ordered (TFP2180). **MRA-1** = ~10 min anti-reset latch after trip — **not** dry-pipe-on-dead-panel. Inadequate batteries may **fail to operate the solenoid during a power failure** — that is **not** SureFire failsafe; it is a **closed-valve-on-dead-panel** risk unless the listed panel/battery calc is done. Status path: `grounded` when sheet in hand.
- **Reliable Bulletin 750 Type D (Feb 2024)** — **PDF-held provisional `[V]`:** Electric/Electric. source review-opened teaching numbers (min supervisory **≥7 psi**; high/low switch **5–6 psi decreasing**; Potter **PFC-4410G3**; **90 h** standby called on that sheet — `[V]` vs current NFPA 72 battery chapter). **Do not mark `grounded` until WHOLE mine.** Numbers stay for collision teaching only with explicit provenance.

- **Viking Model VXD Electric/Pneu-Lectric F_052220 Rev 01 Nov 2022** — **mined:** NC solenoid holds the prime; air feeds the low-air switch only. §6.1 Table 2: **recommended 30 psi (water ≤175) / 50 psi (175–250)**; low-air switch **25 / 45**; compressor 30-on/40-off (50/60). Table 2 rows printed "(release system)" — read as sprinkler-piping supervisory air.
 - **With EA-1 (F_041523 Rev 09 Jun 2025):** "minimum recommended pressure setting is **10 PSI**" → rotary **setting 1 (10/15/20)**; Table 2's 30 psi = setting 4 (25/30/35) (§8.1 VXD, §8.2 Model F, §5.2). Second interlock = **>0.1 psi/s decay rate**, "within four seconds". **EA-1 is FM Approved only with VXD 4/6/8 in. (10 in. loose) and Model F 4/6/8 El/El; UL 1486 ≤2,250 gal; not approved with SureFire or El/Pn.** EA-1 activation ≠ delivery time — hand the proof to the water-delivery Skill.
 - Setting vs zone volume is **not printed** by Viking; corpus screens (AR / a prior layout `[SYN]`) suggest setting 1 only for zones ≲1,200 gal and setting 3–4 above — `[V]` confirm with Viking TS.

**Family 2 — Electric/Pneumatic (El/Pn).** Low-air / pneumatic actuator **plus** solenoid. **Not El/El. Not named FAILSAFE** unless a separate SureFire/Family 3 package is elected.

- **Tyco TFP1461 DV-5A El/Pn (JUNE 2026)** — **mined:** Graph B air **scales with water** (~15→~24 psi approximate read — **always size from printed Graph B**, not these approximations). AMD-1/2/3. Low-air supervisory ≈ **6 psi below** Graph B min. Peer contrast: do **not** copy Graph B onto TFP1466 El/El.
- **Victaulic I-769N (9452 REV C 11/2023)** — **mined:** Series **767** Electric/Pneumatic Actuator. Maintain air **13–18 psi**. Sample CROSS-ZONE / DOUBLE KNOCK program = **vendor habit** — fence per §3.4.
- **Viking Model VXD F_052020 Rev 04 December 2025** — **mined:** Electric/Pneumatic. Table 2 AMD **30 psi** (water ≤175) / **50 psi** (175–250); supervisory switch **25 / 45 psi**. Compressor ON/OFF **30/40** and **50/60** respectively. **Not El/El.**
- **Optional peer:** Viking **F_070889 Rev 01 June 2025** — **mined:** same AMD **30/50** and supervisory **25/45** family; do not mix cut-in tables across forms.

**Family 3 — Named failsafe (SureFire).** Failsafe **on loss of primary and secondary power** (degrade toward pneumatic dry-pipe behavior).

- **Viking TRIMPAC SureFire F_051704 Rev 01 May 2025** — **mined WHOLE:** factory failsafe DI trim for the Model F valve + VFR-500 panel, **listed as a unit** (cULus VLTR/VLTR7; FM Approved Preaction). Normal power: low air with no detection → NO block solenoid **powered closed**, valve stays shut. Input fault or **loss of AC + battery** → a fusing sprinkler trips the valve **pneumatically** (degrades to sprinkler-only release). Hydro **300 psi or +50 over working, ≤2 h**; air test **≤40 psi**; never air-pressurize the priming chamber. **Holding air not printed** → by mechanism (actuator on the power-loss path) use the actuator family **30/50 psi** — **inference, `[V]` Viking TS**. EA-1 is not approved with SureFire.
 - **Panel binding:** the trim needs a releasing program with **two solenoid outputs (NC release + N/O block)** and the NO solenoid **de-energized in normal standby** (battery: a normally-energized NO pattern can exceed the panel battery circuit at the FM 90 h / 10 min basis). Viking documents a SureFire program on the VFR-500 (F_072523 Rev 04); a one-release-output El/El program cannot drive it. Name the program by brand + number + drawing on the submittal; never freeze it as a shop SKU.
- **FireFlex TOTALPAC N2 SUREFIRE IOM ©2023** — **PDF-held provisional `[V]`:** packaged Viking-based failsafe + N₂ skid. source review-opened Table 2 teaching (El/pneu-lectric vs SUREFIRE bands) stays provisional. Related mined **HP Dry** FM-076E-0-13B is a **different document** — do not swap.

**Not a family:** Tyco **FSV-1** latch-open-after-trip. Do not file it under El/El failsafe.

**Not a controlling family row:** Tyco **SI TFP1421** (fixed **10±2** air) — **`comparison-only`** fence evidence only.

**Honesty — Absent stampable failsafe BOM:** corpus depth-gap notes no stampable DV-5A El/El+QRS-2+#13 failsafe BOM. Do **not** invent one. Ask for current FM-Approved failsafe datasheet when Family 3 is required.

### 3.6 Opened-sheet pressure table (do not mix rows)

| Family | Opened sheet | Provenance | Supervisory / AMD | Low-air / trip | Failsafe-on-total-power-loss |
|---|---|---|---|---|---|
| **El/El Tyco DV-5A** | TFP1466 **JUNE 2026** | **mined** | Air **nominally ~15 psi** irrespective of water; relief ~20 psi | Switch **~12 psi decreasing** | **No.** NC de-energized solenoid; MRA-1 is **~10 min anti-reset**, not dry-pipe-on-dead-panel. Inadequate batteries → solenoid may not open. |
| **El/El Reliable Type D** | Bulletin 750 **Feb 2024** | **PDF-held `[V]`** | **≥7 psi** min supervisory (opened) | Switch **5–6 psi decreasing** (opened) | **No.** No mechanical backup on that sheet narrative. |
| **El/Pn Tyco DV-5A** | TFP1461 **JUNE 2026** | **mined** | **Graph B** water-dependent (~15→~24 approx.) | ≈6 psi below Graph B min | **No.** Pneumatic actuator second gate. |
| **El/Pn Victaulic 769N** | I-769N **REV C 11/2023** | **mined** | **13–18 psi** | Series 767 actuator band | **No** (unless redundant-solenoid package separately elected — still not SureFire). |
| **El/Pn Viking VXD** | F_052020 **Rev 04 Dec 2025** | **mined** | AMD **30/50 psi**; supervisory **25/45** | Not El/El | **No.** NC solenoid + pneumatic actuator in SET. |
| **El/Pn Viking (peer)** | F_070889 **Rev 01 June 2025** | **mined** optional | AMD **30/50**; supervisory **25/45** | Not El/El | **No.** |
| **El/El Viking VXD** | F_052220 **Rev 01 Nov 2022** | **mined** | **Recommended 30/50**; with EA-1 **min 10** (set 1 = 10/15/20) | Switch **25/45** (no EA-1) or EA-1 rate trigger | **No.** Both gates in the panel → no release on total power loss. |
| **SureFire DI (Viking TRIMPAC)** | F_051704 **Rev 01 May 2025** | **mined** | Air test **≤40 psi**; holding air not printed → **30/50 by mechanism `[V]`** | NO block solenoid + pneumatic actuator | **Yes:** loss of AC + battery → sprinkler-only pneumatic release (listed as a unit). |
| **FireFlex TOTALPAC N2 SUREFIRE** | IOM © **2023** | **PDF-held `[V]`** | source review-opened Table 2 bands | Fail-safe via packaged SureFire + N₂ | **Yes (concept, provisional).** |

**Collision (show-and-verify from those rows):** the Viking actuator band (El/Pn F_070889/F_052020, and SureFire's power-loss path) is **~30 psi** (or **50 psi** on high-pressure water). Tyco / Reliable El/El low-air lives at **~7–15 psi** (Reliable **≥7**; Tyco nominal **~15**, trip **~12**). `30/15 = 2`; `30 − 7 = 23 psi` of incompatible setpoint. **Viking VXD El/El (F_052220) is not in the low band by default** — Viking recommends 30/50 and allows 10 only as the EA-1 minimum. The 2010 TM **~10 psi** survives as that **floor**, not a default. Victaulic **13–18** and Tyco Graph B are **El/Pn** — do not stack them onto Family 1. Pick **one row**. Do not stack a 30 psi pneumatic actuator on TFP1466 / Type D El/El.

**N₂ / AMD stack squeeze (check every elected row):** generator cut-in must sit a few psi below the AMD set **and** a few psi above the low-air alarm. On VXD El/El Table 2 (low-air 25 / AMD 30) a 3 psi margin each way leaves **no window** (AR retest `[SYN]`); EA-1 setting 1 at nominal 15 also leaves none unless the AMD may sit above nominal (`[V]` Viking TS). Hand the band to `nitrogen-inerting-and-c-factor-gate` (ECS generator + compressor is the shop standard — not Potter) and record the squeeze as a submittal question.

**Three-way Viking trade (AR retest, `[SYN]` method):** El/Pn = mechanical second gate, 30 psi, no auto release on dead panel; El/El + EA-1 = lowest air / best delivery margin, **no power-loss release path** (needs written owner + insurer acceptance); SureFire = failsafe on power loss, actuator band 30/50 (slower delivery), no EA-1. Name the trade in the BOD.

FSV-1 TFP1386 **Aug 2022**: anti-reset after DV-5 trip — **not** El/El power-fail failsafe.

### 3.7 The ~10–15 psi vs ~30 psi collision (show-and-verify)

Pneumatic actuators on dry/DI valves are commonly **set in the 25–40 psi band** (Viking AMD **30/50**). El/El **low-air switches** on opened current El/El sheets live at **~7–15 psi**.

```
If actuator_setpoint ≈ 30 psi and El/El_low_air_switch ≈ 10–12 psi:
 the pneumatic actuator never sees its set pressure on an El/El trim,
 OR the El/El switch is sitting above the actuator and nuisance-trips.
 → failed election. Pick ONE family. Do not stack.
```

**Show in the BOD:** chosen family, listed supervisory setpoint, listed low-air switch, actuator type (`none` on El/El). If the caller’s existing valve-room drawing shows a 30 psi dry-pipe actuator **and** an El/El solenoid, **Stop** and name the collision. Status the collision check (`grounded` when both bands from opened/mined sheets; `provisional` if one side is PDF-held).

**Failsafe that adds a pneumatic actuator pulls the assembly into the actuator band** — do not “keep 10 psi and add SureFire.” Show that collision explicitly ([SYN] valve-room worked package teaches this — METHOD only; do not copy hall defaults).

Do not invent a 10 / 15 / 30 / 7 psi number as a project default. Use the **listed** setpoint of the elected family. If the OEM sheet for the elected valve is not in hand → `[V]` and a stated `ASSUMED` setpoint (value + why), flagged — not a Stop; never freeze a vendor SKU.

### 3.8 Package on the drawing

Mark each `DRAW` / `SPEC` / `C&E` / `N/A` / `[V]`.

1. Name the **family** in the BOD (one sentence of power-loss behavior).
2. Valve + solenoid + panel **by listing**, not SKU.
3. Supervisory setpoint + low-air switch settings **from that listing**.
4. AMD / nitrogen maintenance device compatible with the elected pressure (nitrogen Skill owns generator vs cylinders).
5. Hand-off row: `HAND OFF — dry-preaction-water-delivery-screen` if DI volume needs QOD (TFP1466 names QRS-2 as compatible on **DV-5A El/El**; do not size it here; do not invent VXD+QRS-2).
6. Hand-off row: `HAND OFF — nitrogen-inerting-and-c-factor-gate` for medium (ECS N₂ generator + compressor), purity / originally-installed N₂, and the C-factor election (shop C=100; 120 comparison-only).
7. Do **not** rewrite the C&E matrix. If Family 3 failsafe changes trip-on-dead-panel, emit status **`handoff`** and **tell** the C&E Skill to **restamp that one Boolean** — do not silently edit it here.

### 3.9 Handshakes (reciprocal — required rows)

| Peer | They own | This Skill owns |
|---|---|---|
| `preaction-releasing-c-and-e-soo` | Controlling `preaction_trip` Boolean; asks El/El **failsafe QUESTION** | **Answers** failsafe / elects trim family; may **hand back** one Boolean restamp request on Family 3 (`handoff`) — never silent rewrite |
| `dry-preaction-water-delivery-screen` | Proves ≤30/60 s or marks unproved; sizes QOD vs volume-cut | Passes valve family + QOD **function** need (e.g. QRS-2 compatible on TFP1466); no SKU catalog / no delivery proof |
| `nitrogen-inerting-and-c-factor-gate` | Medium (N₂ generator + compressor), C-factor election (C=100 design; 120 comparison-only), fill | Only actuator / AMD / medium **compatibility** with elected pressure band |
| `suppression-technology-selection` | Company wet \| dry \| DI election | Consumes DI; does not re-elect |
| `most-stringent-basis-matrix` | Dual-carrier listing / trim / DI rows | Consumes; never silent-swap |
| `itm-design-for-testability` | ITM intervals / CD features | Optional DRAW/SPEC features from elected trim (anti-reset, monitored solenoid, etc.) — does not write interval tables |
| the input packet | Packet intake (optional) | Consume when present |

Emit rows as needed:

- `HAND OFF — preaction-releasing-c-and-e-soo: Family 3 failsafe elected → restamp dead-panel Boolean only. Do not rewrite full matrix here.`
- `HAND OFF — dry-preaction-water-delivery-screen: QOD/accelerator sizing + 30/60 proof.`
- `HAND OFF — nitrogen-inerting-and-c-factor-gate: medium / C / purity / fill.`
- `HAND OFF — itm-design-for-testability: trim-driven test features into CD.`

---

## 4. Output

A **trim-family election**. Write **only** to the caller-named path.

Minimum: Hard-scope gate + status register (gate / A–D / collision / listing); edition-pin block; inputs echoed including packet + STS + matrix + C&E Boolean; Parameters A–D with status; family chosen with OEM sheet + date + provenance (`mined` / `PDF-held` / `[V]` / `[SYN]`); supervisory/low-air numbers from **that** sheet; collision check; listing pair; QRS-2 / QOD and nitrogen hand-offs; Family 3 → C&E Boolean restamp `handoff` when needed; Δ vs 13-2025; `[V]` / `[SYN]` register.

Do **not** emit occupancy schedule, density×area `calcs`, pump nameplate, rewritten C&E matrix, C-factor / 98 % purity, QOD gallon proof, or CAD. Do **not** emit PLACEHOLDER text. Do **not** invent psi / SKU / battery hours.

---

## 5. Stop

Missing inputs stay ASSUMED and flagged. The scope lock above still stops.

1. Assignment packet missing → not a Stop (packet optional); proceed and flag `ASSUMED`. 2. STS DI election missing / `unresolved`. 3. Matrix listing/trim/DI rows unresolved when dual-carrier requires them → `unresolved`. 4. C&E Boolean not yet written. 5. SI/NI (or wet/dry with no DI zone) presented as **trim BOD** → `RFI-variance` (or N/A as applicable). 6. Foam BOD. 7. Mist design request (`PRACTICE REFUSED` / `RFI-variance`). 8. Unpinned carrier or AHJ 13 edition. 9. Caller wants a valve SKU or psi as hall default / invent. 10. Mixing ~30 psi pneumatic actuator with El/El ~7–15 psi switch. 11. Naming a Viking VXD family without its form number (F_052020 El/Pn vs F_052220 El/El), or citing `F_052220_06`. 12. Using 2010 Viking TM as current El/El. 13. Treating FSV-1 as power-fail failsafe. 14. Grounding PDF-held Bulletin 750 / FireFlex as `grounded` without `[V]`, or grounding the SureFire 30/50 holding air (inference) without `[V]`. 15. Inventing VXD+QRS-2 listing. 16. Treating vendor CROSS-ZONE as two smoke zones for water trip. 17. Silent C&E Boolean edit (Family 3 must `handoff_pruner` / / / ARCHIVE / root PDF queue.

---

## 6. Citations (section AND edition)

- Tyco **TFP1466 JUNE 2026** (**mined**): El/El two independent events; nominal **~15 psi**; low-air **~12 psi decreasing**; relief ~20; MRA-1; QRS-2 compatible on DV-5A; AMD-1/3 (no AMD-2); CROSS-ZONE panel label ≠ two smoke zones; solenoid/panel battery risk on power failure.
- Tyco **TFP1461 JUNE 2026** (**mined**): El/Pn; Graph B water-dependent air; AMD-1/2/3.
- Victaulic **I-769N 9452 REV C 11/2023** (**mined**): El/Pn; air **13–18**; Series 767; sample CROSS-ZONE ≠ DC water trip.
- Viking **F_052020 Rev 04 December 2025** (**mined**): VXD El/Pn; AMD **30/50**; supervisory **25/45**.
- Viking **F_052220 Rev 01 November 2022** (**mined**): VXD Electric/Pneu-Lectric (El/El); §6.1 Table 2 recommended **30/50**, low-air switch **25/45**.
- Viking **F_041523 Rev 09 June 2025** (**mined**): EA-1; min recommended **10 psi** (setting 1 = 10/15/20); 0.1 psi/s rate trigger; FM with VXD / Model F El/El only; UL 1486 ≤2,250 gal; not SureFire / El/Pn.
- Viking **F_070889 Rev 01 June 2025** (**mined**, optional Family 2 peer): AMD **30/50**; supervisory **25/45**.
- Reliable **Bulletin 750 Feb 2024** (**PDF-held `[V]`**): Type D El/El opened ≥7 / 5–6 / PFC-4410G3 / 90 h — provisional until mine.
- Viking **F_051704 Rev 01 May 2025** (**mined**): SureFire listed as a unit; NO solenoid powered closed in normal power; loss of AC + battery → sprinkler-only pneumatic release; hydro 300 / +50 ≤2 h; air test ≤40; holding air not printed (30/50 by mechanism `[V]`).
- FireFlex **TOTALPAC N2 SUREFIRE IOM ©2023** (**PDF-held `[V]`**): packaged SureFire + N₂ — provisional; do not swap with mined HP Dry FM-076E-0-13B.
- Viking Preaction TM **F_010808 2010** (**mined** historical): ~10 psi teaching — **not** current El/El.
- Tyco **FSV-1 / TFP1386 Aug 2022**: anti-reset fence — not power-fail failsafe.
- Tyco **QRS-2** (TFP1120 / TFP1122): DI El/El host = **DV-5A**; Program #13 panel pair belongs in Parameter D; sizing → water-delivery Skill. **No invented VXD+QRS-2 listing.**
- FM **DS 2-0 Oct-2021 / IR Jan-2024** §2.2.1.12.1.1 listed combination.
- FM **DS 5-32 Jan-2026**: consume C&E; §2.4.3.2.1.3.2 no cross-zoned detection for preaction valve; preference ranking = `comparison-only`.

**Absent / `[V]`:** now held: DI size [CODE 2019/2022/2025 §8.3.2.3]; 7 psi minimum for preaction types 8.3.2.1(2) and (3), i.e. noninterlock and DI [CODE 2025/2022 §8.3.2.5.2; 2019 §8.3.2.4.4; 2016 §7.3.2.4.4] — the earlier "SI attribution" is wrong as to scope; SureFire holding air (not printed); EA-1 setting vs zone volume (not printed); stampable DV-5A El/El+QRS-2+#13 failsafe BOM; WHOLE mines for Bulletin 750 / FireFlex SureFire IOM.

**[SYN] teaching only (do not copy hall defaults):** valve-room worked collision package (outline elects ~10; execution forces ~30 when actuator present); warm-DI El/El primary TFP1466 ~15/12 + QRS-2 + Program #13 with VXD 30/50 alternate refusing QRS-2.

---

## 7. Design practice

1. Three-layer, most stringent, on **four parameters separately**: actuation pair, supervisory pressure, failsafe-on-power-loss, listed valve+solenoid+panel. Owner may raise, never lower. Company fence: **DI trim only** after STS DI; SI/NI Stop + `RFI-variance` / comparison-only; foam prohibited; mist PRACTICE REFUSED.
2. Per-parameter, not per-layer. Never MAX whole sheets. Never stack Family 1 El/El switches on Family 2/3 actuator bands.
3. **Failsafe ≠ one trim.** Name power-loss behavior in one sentence. MRA-1 / FSV-1 ≠ SureFire.
4. Current editions; enforced ≠ latest. Cite **section AND edition**. Do not invent 13-2025 DI section numbers.
5. Show-and-verify collision: `30/15 = 2`; `30 − 7 = 23`. Pick **one** family row.
6. Status register every run on gate + A–D + collision + listing: `grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance`. PDF-held ≤ `provisional` + `[V]`.
7. Upstream (packet optional; gaps → `ASSUMED`): packet + STS DI + matrix (when dual-carrier) + C&E Boolean already written. Caller-path-only. **NO PLACEHOLDER.**
8. Honesty. Provenance labels on every family row (`mined` / `PDF-held` / `[V]` / `[SYN]`). Do not invent psi/SKU/battery hours. Do not rewrite C&E here — Family 3 → `handoff` restamp request. QRS-2 hosts DV-5A El/El only on opened sheets.

---

## 8. Not this Skill

| Work | Where it lives |
|---|---|
| Wet / dry / DI election (SI/NI comparison-only) | `suppression-technology-selection` |
| Dual-carrier BOD / listing rows | `most-stringent-basis-matrix` |
| Trip Boolean / SOO (failsafe is a **question** there) | `preaction-releasing-c-and-e-soo` |
| Medium (N₂ generator + compressor), C-factor election (C=100; 120 comparison-only), purity, fill | `nitrogen-inerting-and-c-factor-gate` |
| ≤30 s / QOD **sizing** / delivery proof | `dry-preaction-water-delivery-screen` |
| Assignment packet intake | the input packet |
| ITM interval tables / CD feature writing | `itm-design-for-testability` |
| Occupancy / density×area / pump | occupancy / density-area / pump Skills |
| CAD / trim isometric | not a Skill |

---

## Check before you finish

1. Hard-scope gate: DI-only trim election; SI/NI-as-BOD → Stop `RFI-variance`; wet/dry no DI → N/A; foam/mist Stop. Emit status on gate.
2. Check packet (optional) + STS DI + matrix listing/trim/DI rows + C&E Boolean written; missing → `ASSUMED` (flagged), not a Stop.
3. Confirm other inputs (carrier, 13 edition, medium, failsafe posture); Stop tests.
4. Pin editions; forbid `F_052220_06`; name VXD by form (F_052020 El/Pn vs F_052220 El/El); name PDF-held vs mined.
5. Vocabulary fence: El/El vs El/Pn; CROSS-ZONE ≠ two smoke zones.
6. Union Parameters A–D separately; status on each.
7. Elect **one** family from catalog with provenance; Family 1 Tyco TFP1466 or Viking VXD F_052220 (± EA-1); Family 2 peers TFP1461 + I-769N + VXD F_052020 (+ optional F_070889); Family 3 SureFire F_051704 Rev 01 (mined; holding air `[V]`). Name the Viking three-way trade and the N₂ stack squeeze.
8. Print pressure table row for elected family only; run collision check; status collision + listing.
9. Package DRAW/SPEC/C&E/N/A/[V]; QRS-2 function hand-off (DV-5A El/El only); nitrogen hand-off; Family 3 → C&E Boolean restamp `handoff`.
10. Reciprocal handshakes named.
11. Δ vs 13-2025; Absent/`[V]` honesty.
12. No PLACEHOLDER; no invent psi/SKU; no silent C&E rewrite; no SI controlling family row.
13. Write **only** to the caller-named path.
14. On a Reliable DDX-LP double-interlock valve, run the supervisory stack below before freezing low air, maintain, and high air. Factory low air of 18 psi is the held Potter PS25 switch default (document 5401564) only where that row's cap allows it. At 225 psi and 275 psi water it sits between the trip-plus-tolerance and the Table A minimum, so do not field-lower it there, and do not call the 5 psi margin a pass. At 50 psi water or less it is above every cap and must be field-lowered. Any other numeric low-air value stays ASSUMED while the GAP-B28R1-1 tolerance residual is open. Verify with the engineer of record.

## Reliable DDX-LP supervisory stack

Country gate (US | Canada). On a US job use the NFPA 13-2025 margins below, and pin the enforced edition. On a Canada job the NFPA 13 pin follows `most-stringent-basis-matrix` §4.2b (2019 unless a later edition is adopted). The 2019 section numbers for the 5 psi low-air and high-air margins are NEEDS HOLD. Do not cite the 2025 numbers as Canada code. Do not invent a ULC or NBC cite for them. Reliable tables are maker data. Canada listing stays [verify].

Synthetic teaching only. Re-derive every psi on the job. Do not copy a hall.

Maker data, Reliable Bulletin 505 (October 2026) Tables A and B, and Bulletin 760 (October 2026):

- Table A minimum supervisory pressure by maximum water pressure, psi: 20 to 8, 30 to 10, 50 to 12, 75 to 13, 100 to 15, 125 to 16, 150 to 17, 175 to 18, 200 to 19, 225 to 21, 250 to 22, 275 to 23, 300 to 24. Do not interpolate. Use the next-higher water row when the job pressure is between printed rows.
- Table B low-pressure nominal trip, plus or minus 2 psi: 20 to 5, 30 to 5, 50 to 7, 75 to 9, 100 to 10, 125 to 11, 150 to 12, 175 to 13, 200 to 13, 225 to 14, 250 to 14, 275 to 14, 300 to 14.
- Absolute cap 30 psi (Bulletin 505 and Technical Bulletin 751 note 6). Type D electric double-interlock minimum supervisory pressure 15 psi (Bulletin 760). A tankless compressor starts at or above the Table A minimum.

Hand math only. Do not invent a calc operation for this stack.

- Worst-case trip equals the Table B nominal plus 2 psi.
- Low air is at least that trip plus 5 psi [CODE NFPA 13-2025 §8.2.6.4 on a US job].
- Maintain pressure is at least the Table A minimum and above low air.
- High air is at least maintain plus 5 psi [CODE NFPA 13-2025 §8.2.6.5 on a US job] and at or below 30 psi.
- Compressor cut-in, upstream of the pressure-maintenance device, is above maintain pressure.

Teaching point at 125 psi water [SYN]: trip 11/13, low air 18 held as the Potter PS25 factory default on decrease (document 5401564) where that row's cap allows it, Table A minimum 16, a fixed maintenance device at 23, high air 28, cap 30. At 225 psi and 275 psi water, do not field-lower factory 18 psi, and do not call the 5 psi margin a pass. At 50 psi water or less, field-lower it. The same document states factory high 28 psi on increase and a field range of 10 to 60 psi. That range is not a per-water-pressure setpoint table and it is not a tolerance. A raised compressor preset of 26/32 passes that point. The margin thins above 150 psi water. At 300 psi water a 23 psi maintain sits below the Table A minimum of 24 and fails.

The earlier band that put low air between trip-plus-2 and the Table A minimum is retired. It cannot meet the 5 psi rule on every row. Low air sits above the Table A minimum. Table A governs maintain pressure, not the switch.

Wrong settings:

- A tankless compressor left at cut-in 20 psi and cut-out 26 psi, with low air also at 20 psi. Cut-in equals the alarm, so the alarm chatters. That failure is not the nitrogen 40 psi cap flag. Hand the cap flag to `nitrogen-inerting-and-c-factor-gate`.
- An adjustable maintenance device left at the factory 29/35 psi pair. The plus 2 psi tolerance can reach 37 psi, above the 30 psi cap.
- A 10 psi fixed device on a low-pressure double-interlock valve whose minimum is higher.
- A 23 psi maintain on a 300 psi water row, below Table A.

Open:

- GAP-B28R1-1 residual is the Potter setpoint tolerance, and whether Bulletin 761 supersedes Bulletin 747. The Potter PS25 factory pair (document 5401564) is held: low 18 psi on decrease and high 28 psi on increase. Reliable Bulletin 747 (November 2022) names that switch on the PrePaK, so the valve-to-switch pairing is held. The per-water-pressure minimums are the Bulletin 505 Table A rows, including 225 psi to 21 psi and 275 psi to 23 psi. Bulletin 747 Table A matches those minima and does not print the caps or the trip. Keep caps and trip sourced to Bulletin 505. Do not cite them to Bulletin 747. Do not invent a tolerance. At 150 psi water the stack requires low air of at least 19 psi (Table B nominal 12, plus 2, plus 5). At 50 psi water or less, factory 18 psi is above every cap in the low-pressure rows below and must be field-lowered. At 225 psi and 275 psi water, trip plus tolerance is 16 psi, factory 18 psi sits under the Table A minimum (21 psi and 23 psi), and the §8.2.6.4 stack is 21 psi, which is above factory 18 psi. Do not field-lower factory 18 psi on those two rows, and do not call that margin a pass. Verify with the engineer of record. That factory setting is separate from the per-row 5 psi margin.
- A low-pressure row whose maintain sits below factory 18 leaves the switch in alarm. Re-derive low air so it stays below maintain and at least trip plus 5 psi. Do not invent a field floor or a tolerance.
- A maintain of 25 psi puts high air on the 30 psi cap with no headroom. The switch tolerance is not held. Prefer the teaching maintain of 23 psi.
- The held pairing is Reliable Bulletin 747 (November 2022). Do not cite an unopened bulletin as that proof.
- The delivery time at a 23 psi maintain stays open. Do not invent seconds. Verify with the engineer of record.

Hand off to `fa-fire-pump-and-preaction-supervisory-points`: per zone, low-air and high-air supervisory points use this stack. Where factory 18 psi meets that row's cap and the 5 psi margin, low air may cite the held Potter factory pair. Elsewhere label the number ASSUMED. The pairing is held. Bulletin 505 Table A, including 225 psi and 275 psi, is held. The switch tolerance is not. Do not claim the gap fully closed. On Type F, loss of air without detection is supervisory only and does not open water (Bulletin 760). This skill does not edit the fire-alarm point list. The Canada gate above stays. Do not cite a 2025 section number on a Canada pin.

Bulletin 505 (October 2026) low-pressure rows. Do not interpolate rows that are not in the table. Calculate the low-air margin on each row. Worst-case trip is the nominal trip plus 2 psi. On a US NFPA 13-2025 job, low air is at least that trip plus 5 psi (§8.2.6.4). Compare that number with that row's cap.

- 20 psi water: minimum supervisory 8 psi, cap 10 psi, nominal trip 5 psi. Worst-case trip 7 psi. Trip plus 5 psi is 12 psi, above the cap. The margin does not fit. Do not call this row a pass.
- 30 psi water: minimum supervisory 10 psi, cap 14 psi, nominal trip 5 psi. Worst-case trip 7 psi. Trip plus 5 psi is 12 psi, under the cap of 14 psi. The margin fits.
- 50 psi water: minimum supervisory 12 psi, cap 16 psi, nominal trip 7 psi. Worst-case trip 9 psi. Trip plus 5 psi is 14 psi, under the cap of 16 psi. The margin fits.

A margin that fits on the 30 psi or 50 psi row is not a failure. Only the 20 psi row fails that arithmetic.

Factory 18 psi is a separate manufacturer setting. It is above every cap (10, 14, and 16 psi), so it has to be lowered in the field on all three rows. Citing factory 18 psi at 50 psi water or less is a failure of that setting, not of the margin. The switch tolerance is still not held. Do not invent it. A margin that fits the cap does not close the tolerance or the listing. Low air stays ASSUMED where either hold is open. Verify with the engineer of record and the maker.

Stop if low air is placed inside the retired band, if high air exceeds 30 psi on a DDX-LP valve, if factory 18 psi is field-lowered at 225 psi or 275 psi water, if the §8.2.6.4 margin is called a pass at 225 psi water with factory 18 psi, if caps or trip points are cited to Bulletin 747, if factory 18 psi is left on water at 50 psi or less, if a low-air number other than that factory pair is presented as a maker value while the tolerance is open, or if a 2025 section number is cited on a Canada pin. Nitrogen stays on its own gate. Do not reopen it here. Foam, clean agent, and single-interlock stay locked.

## Code margin inside the maker band

Hand math only. This pack does not add a calc operation for the stack. A screen is not design approval. Do not fill a missing maker band from memory. Tag every unheld input ASSUMED. Maker bands are inputs. They are never defaults.

On the Bulletin 505 row at 50 psi water (nominal trip 7 psi, tolerance 2 psi, so worst-case trip 9 psi; Table A minimum 12 psi; cap 16 psi), a stack of low air 12 psi, maintain 15 psi, and high air 16 psi gives a low-air margin of 3 psi and a high-air margin of 1 psi. Both sit inside the maker band and both fail the 5 psi code margins [CODE NFPA 13-2025 §8.2.6.4 and §8.2.6.5 on a US job]. Do not shave the 5 psi margin to force a pass. Do not move outside the maker cap to force a pass. Verify with the engineer of record and the maker.

Hand-check pass [SYN], separate from that row: worst-case trip 13 psi, low air 18 psi, maintain 23 psi, high air 28 psi, Table A minimum 16 psi, cap 30 psi, compressor cut-in 26 psi and cut-out 32 psi. Margins are 5 psi and 5 psi. Headroom under the cap is 2 psi. Cut-in is 3 psi above maintain. Cut-out above the cap is upstream of the pressure-maintenance device only. Verify the device inlet with the engineer of record.

Do not cite an unopened bulletin as the pairing basis. The pairing stays Bulletin 747. Caps and trip stay Bulletin 505. The Potter tolerance residual in GAP-B28R1-1 stays open. Do not reopen the nitrogen gate. On a Canada job, do not cite the 2025 margin sections as Canada code.

Failures: calling the screen an approval; inventing a maker setpoint; lowering the low-air margin below 5 psi to clear the 50 psi water row.

## Compressor floor on an NFPA 13-2019 Canada pin

Performance only. Do not freeze a model number. On a Canada pin the code floor is NFPA 13-2019. A dedicated compressor delivers at least 3.5 scfm absolute and restores the largest system to normal pressure in not more than 30 minutes [CODE NFPA 13-2019 §8.2.6.3.2 and Annex A.8.2.6.3.2]. The reconcile lane, only when the job elects it, is NFPA 13-2025 §8.2.7.3. A heated valve room uses the 30 minute clock. Do not apply the below 5 °F allowance of 60 minutes to that room. Do not invent a ULC body.

Teaching point [ASSUMED], not a nameplate: 211 gal at 40 psig needs about 3.50 scfm absolute (about 2.56 scfm gauge). Size at least 3.5 scfm absolute, or an OEM listing at or above that delivery at cut-out. Fill one system at a time through the air-maintenance bypass.

Air-supply relief is at least system air plus 10 psi. At 40 psig assumed, relief is at least 50 psig [CODE NFPA 13-2019 §8.2.6.5; NFPA 13-2025 §8.2.9.4]. A factory setting of plus 5 psi is short. Do not leave it as-left on an NFPA 13-2019 or later job.

High-air supervisory is at least system air plus 5 psi, so at least 45 psig at the assumed 40 psig maintain. Cite both lanes: the 5 psi practice with NFPA 13-2025 §8.2.6.4 and §8.2.6.5, and the 2019 family at §8.2.6.7.2 and §8.2.6.7.2.2. Do not mix a 3 psi shop default into this work. On a Canada pin cite the 2019 floor. Later 2025 numbers are a reconcile lane unless the job elects them.

The 2025 annex restore text is not retrieved (GAP-B37R49-1). Carry the 2019 annex and mark it for verification. The double-interlock trip and low-air maker setpoint stay open (GAP-B37R49-2). GAP-B33R8-1 stays open. This pack does not add a setpoint calc. The screen above stays hand math. Verify with the engineer of record. Foam, clean agent, and single-interlock stay locked.
