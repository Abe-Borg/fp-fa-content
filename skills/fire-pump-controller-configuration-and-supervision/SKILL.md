---
name: fire-pump-controller-configuration-and-supervision
description: >-
  use this when a company-elected wet / dry / double-interlock job has a fire
  pump (electric with or without transfer switch, or diesel) and you must issue
  the FP-side controller and pump-room supervision package: the required remote
  signal set mapped to named terminals on named strips, the configuration
  refuse list (Lockout, Load Shed, series zone, auto-stop), the pump-room
  ambient floor AND maximum, the transfer outage budget for the C&E narrative,
  valve supervision method per pump valve, and the acceptance-test union. Packet
  optional; missing inputs ASSUMED and flagged. FP side of the interface only:
  hands the contact list to fa-fire-pump-and-preaction-supervisory-points; not
  pump sizing, driver/OCPD sizing, or FA panel design.
---

# Fire-pump controller configuration and pump-room supervision (FP side)

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

## 0. What this Skill is

A reusable FP-side recipe for the **controller and pump-room supervision interface**. It answers: *what must the FP drawings and spec require of the fire-pump controller, transfer switch, and pump room so that every required signal actually exists as a wireable contact, nothing in the controller can prevent or delay a start, and the room stays inside the controller's rated envelope?*

It produces:
1. A **required-signal matrix** (code x insurer x owner x local amendment, most stringent per signal).
2. A **terminal map**: each required signal → named strip → named terminal (or not discrete + mitigation), per the submitted OEM.
3. A **configuration refuse / specify list** for the spec and the commissioning record.
4. A **pump-room environmental schedule** with a floor AND a maximum.
5. A **transfer outage budget** for the C&E narrative.
6. A **valve supervision schedule** (method per pump valve).
7. An **acceptance-test union** (start counts and alarm-contact verification).
8. The **contact-list hand-off** to the FA side.

**Core findings it carries (corpus-grounded, multi-OEM):**
- The insurer alarm list does **not** map one-to-one onto controller terminals. On the OEMs mined, at least one required signal is a composite, one may be screen-only, and connected to alternate source lives on the **transfer-switch strip in a second enclosure**. Landing only the controller strip silently omits an insurer-required signal.
- Controllers ship field-wireable functions that can **prevent or stop** the pump (Lockout input, Shutdown-on-Lockout, Load Shed, series-zone interlocks, automatic stop). FM DS 3-7 §2.2.1.3 (fault may start the pump, never prevent it) makes these a **refuse-by-name** list.
- Every layer states a pump-room temperature **floor**; none states a **maximum**. The product listing (fourth layer) does: ~104 °F (40 °C) on two OEMs.
- An ATS on a fire pump is a **break, not a bridge**: the running motor is stopped for transfer and restarts through the full starter sequence.

**Design practice:** three-layer basis (code floor x insurer data sheet x owner standard) plus the **product-listing fourth layer**; most stringent wins **per signal and per setting**. Report delta vs the enforced NFPA 20 edition **and** NFPA 20-2025. Cite section AND edition. Verify with the engineer of record. Do not claim a stamp. Copy METHOD from worked packages, never their numbers.

## 1. Hard scope gate

| Check | Result |
|---|---|
| System family elected wet / dry / DI | proceed |
| Family missing | ASSUME per `suppression-technology-selection` default for the hall (state it), flag, proceed |
| SI or NI preaction as BOD | record, **Stop + `RFI-variance`**; SI/NI may appear only as a comparison row |
| Foam / clean agent / mist requested | foam: Stop (prohibited); clean agent: hand-away; mist: `PRACTICE REFUSED` |
| No fire pump on the job (hydrant verdict Adequate, no owner N+1) | Stop this Skill: nothing to configure; report `handoff` to `hydrant-supply-curve` verdict |
| Canada | Out of scope |

This Skill **elects nothing** about the suppression system or the pump rating.

## 2. Inputs (parameterized; ASSUME and flag any missing)

| # | Input | If missing → ASSUMED |
|---|---|---|
| I1 | Enforced NFPA 20 edition (AHJ-adopted) and NEC edition | NFPA 20-2022 code floor + report 2025 delta; flag `[V]` adoption |
| I2 | Insurer (FM / AXA XL / other / none) and its data sheet revisions | FM (most stringent of the held insurer layers); DS 3-7 + DS 2-81 rev as held, `[V]` current rev |
| I3 | Owner standard and any local amendment (e.g. state fire-code amendment supervisory list) | none; flag local amendment not checked |
| I4 | Pump count, driver per pump (electric / diesel), series or parallel | from `pump-envelope` output; else 1 electric, parallel |
| I5 | Power arrangement: utility only / utility + on-site generator via ATS / two utilities / feeder from generator only | utility + generator via integral ATS (hyperscale default), flag |
| I6 | Starter type (across-the-line / reduced voltage) | reduced voltage where ≥100 hp or on a generator (corpus rule); flag |
| I7 | Controller OEM and IOM revision on the submittal | OEM TBD: produce the matrix with terminal column = `submittal confirm` |
| I8 | Pump-room location (indoor room / pump house / exterior skid) and adjacent heat sources | indoor room adjacent to mechanical plant; flag max-temperature check |
| I9 | Water source monitoring wanted (suction pressure, tank level, flow) | suction pressure + tank level both wanted; flag analog-input contention check |
| I10 | Valves on the pump train (suction, discharge, bypass, backflow isolation, test header, hose header, automated water control valve) and supervision method per valve | all present except automated valve; electrical tamper per §4.18.1 method (1) or (2); flag |
| I11 | Jockey pump present and its controller | present; separate jockey controller; flag |
| I12 | Variable speed / pressure-limiting driver | none: company default constant speed (VSPLC best avoided, FM DS 3-7 §3.1.11 ~); flag |
| I13 | Point of constant attendance / supervising station type | proprietary or central station; flag |

## 3. Pin editions and layers

Record for the job, one line each:
- **Code floor:** NFPA 20 (enforced year) §10.4.6 to §10.4.8 electric signals; §12.4.1 to §12.4.3 diesel; §4.8.8 / §4.8.9; §4.16.5.3.2; §4.18; §4.27.6.7; Ch. 14 acceptance; NEC Art. 695 (enforced year). Verbatim NFPA 20 text is held **only** for the pulls 20-01 to 20-05 (Step A list). Those rows are [CODE] with edition and pull id. Everything else in NFPA 20 (Ch. 9, Ch. 14, §4.27 jockey sizing, 2019 / 2022 §12.4.1.3 / §12.4.1.4) stays `[V]`; see the paywalled gap list, NFPA 20 block.
- **Insurer:** FM DS 3-7 §2.2.1.12 (separate alarms to constant attendance), §2.2.1.3 (fail-to-safe wiring), §2.2.1.6 (room > 40 °F); FM DS 2-81 §2.9.6 (adds loss of phase and phase reversal, local AND at FACP/remote), §2.9.4.1, Table 7 item 5 (manual stop only, annual). Our DS 3-7 is the 2021 revision; current is ~Apr 2025 `[V]`.
- **Owner / federal overlay:** UFGS 21 30 00 acceptance starts where the owner adopts it; owner BMS/EPMS requirements.
- **Local amendment:** any state or city supervisory list (example pattern: a state amendment requiring room temperature, phase loss, phase reversal, and pump-in-manual as distinct FA supervisory points). Treat as Layer 1 for that jurisdiction only.
- **Fourth layer (product listing):** controller IOM of the **submitted** revision. Never use a mined IOM's defaults as the job's values.

## 4. Step A: required-signal matrix (most stringent per signal)

Build one row per signal per pump. Columns: point #, point, pump, signal, source, governing layer, status. **Point numbers and names match the FP point list issued to FA, rev 3 (rows 1 to 12, 12a to 12g, 20 to 25, 26a, 26, 27)**; keep them so the FA schedule and this package cross-reference one to one.

NFPA 20 text below is cited from same duties the edition text pulls: **20-01** (2025 §10.4.6 to §10.4.8, §12.4.1 to §12.4.3), **20-02** (2025 Ch. 4; 2022 / 2019 §10.4.7, §10.4.8, §12.4.2, §12.4.3), **20-03** (2022 / 2019 §4.18, jockey note), **20-04** (2019 / 2022 §4.8, §4.16, §4.18), **20-05** (2025 §4.8.8 to §4.8.9.1). Anything outside those pulls stays `[V]`.

**Signal class is a [CODE] constraint, not an FA choice** [CODE NFPA 72-2019/2022/2025 §23.8.5.9.1, §23.8.5.9.2; pull 72-41]: a pump running signal is permitted to be a supervisory **or** alarm signal; signals other than pump running shall be supervisory signals. So rows 2 to 12, 20, and the valve rows 21–26a and 26 are **Supervisory**; row 1 is Supervisory or Alarm (the only election). Trouble applies only to faults on the FA monitoring circuit itself, never as the class of an NFPA 20 signal.

**A1. Electric controller → FACP (signals per §10.4.7.2, contacts per §10.4.8)**

| # | Point | Source |
|---|---|---|
| 1 | Pump or motor running | [CODE NFPA 20-2019/2022/2025 §10.4.7.2.1, §10.4.8; 20-01, 20-02] |
| 2 | Loss of phase (all phases, running or at rest) | [CODE 2019/2022/2025 §10.4.7.2.2; 20-01, 20-02]. Often **not discrete** on the OEM; see Step B |
| 3 | Phase reversal | [CODE 2019/2022/2025 §10.4.7.2.3; 20-01, 20-02]. Upstream monitoring permission §10.4.7.2.3.2 is 2022/2025 only; not in 2019 (2019 equivalent §10.4.6.2.2, local indicator, pull 20-09 (ORD-FP-012)) |
| 4 | Controller connected to alternate source (two sources per 2025 §9.3.1 / 2019 §9.3.2, pull 20-09 (ORD-FP-012)) | [CODE 2019/2022/2025 §10.4.7.2.4; 20-01, 20-02]. **ATS strip** |
| 5 | Alternate-source isolating switch or circuit breaker open or tripped | [CODE 2019/2022/2025 §10.4.7.2.5; 20-01, 20-02]. ATS strip |
| 6 | **Controller or system trouble (single common point)** | [CODE 2019/2022/2025 §10.4.7.2.6, §10.4.8; 20-01, 20-02]. Condition list by edition below |
| 7 | Loss of power / power available | **Not an NFPA 20 remote signal.** §10.4.6.1 (Power Available Visible Indicator) is a local indicator [CODE 2019/2025 §10.4.6.1; 20-01, pull 20-09 (ORD-FP-012)]; the clause itself does not say not remote. FM signal (FM DS 3-7 §2.2.1.12, separate). Land on FM jobs |
| 8 | Controller not in auto / manual mode | Not in §10.4.7.2 [20-01, 20-02]. Required by a state amendment where adopted (AR AFPC §913.6 pattern); otherwise [SYN] optional |
| 9 | Pump room temperature low (both drivers) | Not in captured NFPA 20 Ch. 10 or 12. State amendment where adopted; FM floor in Step D; otherwise [SYN] |

**Row 6 condition list by edition** (one contact):
- **2019** (20-02): one sentence: ground fault (where provided), pressure-sensing device, variable-speed trouble, fail-to-start = 4.
- **2022** (20-02): As a minimum list of the same 4.
- **2025** (20-01): As a minimum list of 9: ground fault where provided; pressure-sensing device; variable-speed trouble; fail-to-start; motor overload (§10.4.6.4); single phase; pressures exceeding rated components; low reservoir level; lowest permissible suction pressure.
- **Fail-to-start is inside row 6, not a separate code point.** FM DS 3-7 §2.2.1.12 asks for it **separately**: on FM jobs either get a discrete OEM contact or record `unresolved` + insurer concurrence.
- Local motor overload indicator: visual + silenceable audible at > 120 % FLA in any phase for 12 s [CODE 2025 §10.4.6.4; 20-01]; not in 2019 (pull 20-09 (ORD-FP-012)). Annunciation only; see C6.
- §10.4.7.1 [CODE 2025; 20-01; 2019 / 2022 in 20-02]: where the room is not constantly attended, audible or visible signals at a point of constant attendance, powered by a separate reliable supervised source not exceeding 125 V.

**A2. Diesel controller → FACP (remote panel §12.4.2.3, remote circuits §12.4.2.2, contacts §12.4.3)**

| # | Point | Source |
|---|---|---|
| 10 | Engine running (separate signal) | [CODE 2019/2022/2025 §12.4.2.3(1); 20-01, 20-02] |
| 11 | Controller main switch in off or manual (separate signal) | [CODE 2019/2022/2025 §12.4.2.3(2); 20-01, 20-02] |
| 12 | **Diesel controller or engine trouble: ONE common point (company default)**. Supervisory [CODE NFPA 72 §23.8.5.9.2; 72-41] | [CODE 2019/2022/2025 §12.4.2.3(3) separate or common signals; 20-01, 20-02]. Sub-conditions 12a to 12g are **not FA points** by default |
| 12a | Failure of engine to start automatically (sub-condition of 12) | [CODE 2019/2025 §12.4.1.3(3); 20-01, pull 20-09 (ORD-FP-012)]. 2022 `[V]` |
| 12b | Shutdown from overspeed; critically low oil pressure; high engine temperature; high cooling water temperature (sub-condition of 12) | [CODE 2019/2025 §12.4.1.3(1),(2),(4),(5); 20-01, pull 20-09 (ORD-FP-012)]. 2022 `[V]` |
| 12c | ECM failure (§12.4.1.3(6)); ECM selector in alternate, fuel injection malfunction, ECM warning (§12.4.1.4(5),(6),(11)); ECM engines only (sub-condition of 12) | [CODE 2025; 20-01]. 2019 has only ECM selector (5) and fuel injection (6) [CODE 2019 §12.4.1.4(5),(6), pull 20-09 (ORD-FP-012)]; ECM failure §12.4.1.3(6) and ECM warning §12.4.1.4(11) not in 2019. 2022 `[V]` |
| 12d | Battery failure or missing battery: (a) separate visible indicator for each battery; (b) initiates at no lower than two-thirds of battery nominal voltage rating (8.0 V dc on a 12 V dc system); (c) also initiates when the battery is missing, with or without the charger energized; (d) sensing delayed to prevent nuisance signals. Battery charger failure (separate indicator; audible not required) (sub-condition of 12) | [CODE 2025 §12.4.1.4(1)(a) to (d), (2); 20-01]. 2019 / 2022 `[V]` |
| 12e | Low fuel level signal at two-thirds tank capacity (sub-condition of 12) | [CODE 2025 §12.4.1.4(7); 20-01]. 2019 / 2022 `[V]` |
| 12f | Low engine temperature; low cooling water flow; interstitial-space liquid intrusion; fuel maintenance needed (if provided); low air / hydraulic start pressure (if used); pressures exceeding rated components; low reservoir; lowest permissible suction (sub-condition of 12) | [CODE 2025 §12.4.1.4(3),(8),(9),(10),(12) to (15); 20-01]. 2019: low air/hydraulic (3), low air pressure (8), low engine temp (9), interstitial (10), fuel maintenance (11) [CODE 2019 §12.4.1.4, pull 20-09 (ORD-FP-012)]; low cooling water flow and items (13)–(15) not in 2019 list. 2022 `[V]` |
| 12g | System overpressure at 115 % of set (VS pressure-limiting engines only; sub-condition of 12) | [CODE 2025 §12.4.1.4(4); 20-01] |
| 20 | Loss of power (controller AC) | Not in §12.4.2.3 [20-01, 20-02]. FM DS 3-7 §2.2.1.12 signal; land on FM jobs, otherwise [SYN] |

- **Path to the remote panel:** §12.4.2.3(3) itself cross-references only §12.4.1.4 and §12.4.1.5 (§12.4.1.5 is the signal-silencing switch, not a trouble list; 2019/2025, pull 20-09 (ORD-FP-012)). The §12.4.1.3 conditions (oil pressure, engine temperature, fail-to-start, overspeed, cooling water, ECM failure: 12a, 12b, ECM failure in 12c) reach remote indication only through §12.4.2.2, which requires circuits for the conditions in §12.4.1.3, §12.4.1.4, and §12.4.2.3 [CODE 2019/2022/2025 §12.4.2.2; 20-01, 20-02].
- Grouping default [SYN election under the §12.4.2.3(3) common option]: one common diesel trouble point (row 12); 12a to 12g as discrete FACP points only on owner, FM, or AHJ request. FM also accepts a single pump house trouble signal per corpus (DS 3-7, our 2021 rev) `[V]` current rev.
- §12.4.2.1 [CODE 2025; 20-01; 2019 / 2022 in 20-02]: remote signals powered by a source other than the engine starting batteries, not exceeding 125 V, where the room is not constantly attended.

**A3. Rules**
- Most stringent per signal: if FM or a local amendment requires a signal **separately**, the row 6 / row 12 composite does not satisfy it. Record `unresolved` until a discrete path or written insurer concurrence exists.
- Variable speed (only if a job elects it; company default is constant speed): §4.8.8 design-curve mismatch and the ten §4.8.9 conditions report to the **controller** with remote contacts per §4.8.9.1 [CODE 2019/2022 §4.8.8 to §4.8.9.1, 20-04; 2025 §4.8.8 to §4.8.9.1, 20-05 (20-02's 2025 capture of §4.8.9 is truncated at item 7)]. **Mapping these to row 6 is [SYN/PARA]**, not CODE: §10.4.7.2.6(3) (2025 numbered list; 2019 §10.4.7.2.6 has no list and names a variable speed trouble signal inline, pull 20-09 (ORD-FP-012)) cross-references the controller VFD clauses (§10.10.8.1, §10.10.8.2, §10.10.3), not the §4.8.9 unit. Assumed path: unit → controller → row 6; confirm with OEM `[V]`. A VS diesel adds 12g.
- Class constraint (hand-off, not an FA choice): rows 2 to 12, 20, 21–26a and 26 Supervisory; row 1 Supervisory or Alarm [CODE NFPA 72-2019/2022/2025 §23.8.5.9.1/.2; 72-41]. FA owns labels, modules, and the row 1 election only.

## 5. Step B: terminal map (per submitted OEM)

For each Step A row, fill: **strip** (controller / ATS / remote panel), **terminal**, **contact type** (Form C, fail-safe de-energize-on-trouble or not), **composite membership**, **delay**, **verdict**.

| Verdict | Meaning | Action |
|---|---|---|
| discrete | one terminal, one condition | land |
| composite | one terminal, several conditions | land; label by class (e.g. Motor trouble / fail-to-start class); C&E must not claim a discrete or faster signal |
| not discrete | screen alarm only | prefer an OEM option with a discrete contact; else common alarm + documented limitation + written insurer concurrence; status `unresolved` until one exists |
| second enclosure | on the ATS strip | **mandatory on the riser diagram**; say so in a drawing note |
| trouble-named contact | OEM label such as Motor Trouble or Controller Trouble | the label is a **name, not a class**: it lands as Supervisory [NFPA 72 §23.8.5.9.2; 72-41] |
| name collision | terminal name misleads (e.g. Pump Room Alarm = overvoltage + undervoltage + phase unbalance) | relabel on the hand-off as Controller electrical alarm; true room temperature comes from a separate device |

**Patterns found across the four electric OEMs mined (method, not values):**
- Power Available fail-safe relay can double as dead-controller indication; confirm in writing on the submittal whether it is inside the controller-trouble composite.
- Fail-to-start is commonly inside a motor-trouble composite with a ~20 s factory delay.
- At least one OEM ships phase loss as screen-only; another ships a discrete Form C Phase Failure. Pick per job; do not copy terminal letters across OEMs.
- ATS normal dropout (~85 %) precedes the undervoltage alarm (~80 %) on one OEM, so a transfer can occur with **no** undervoltage alarm. The ATS-alternate contact is the only annunciation: second reason to land the ATS strip.

Output the map as a table and validate in a script (Step I).

## 6. Step C: configuration refuse / specify list (spec + commissioning record)

Each item is a spec clause **and** a witnessed line on the acceptance record.

| # | Item | Position | Basis |
|---|---|---|---|
| C1 | Lockout / inhibit input | **Not assigned, not wired.** Shutdown-on-Lockout disabled. A BMS/EPMS request for a pump-inhibit contact is a finding: escalate, do not wire | FM DS 3-7 §2.2.1.3 |
| C2 | Lockout vs emergency handle | Assume worst case (lockout may defeat the electronic assist on emergency start) until the OEM confirms in writing that the mechanical path survives | OEM IOM ambiguity `[V]` |
| C3 | Load shedding / motor-run delay on alternate source | **Not supplied**; if present, disabled and verified. If the generator cannot carry the pump start, fix the generator | NEC Art. 695 ~; UFC 3-540-01 |
| C4 | Automatic stop | **Manual stop only**; acceptance form run-period line reads No. If a run-period is ever enabled, the insurer note is about 10 min after cut-out. That note is not the code minimum-run, and it is not overspeed lockout. See §19 | FM DS 2-81 Table 7 item 5; NFPA 20 §12.7 |
| C5 | Series / higher-zone / lower-zone functions | Disabled on FM jobs (FM permits no series pumps); submittal states so | FM DS 3-7 ~; corpus finding |
| C6 | Running overload trip | None configurable; overload is annunciation only (local visual + silenceable audible > 120 % FLA for 12 s [CODE 2025 §10.4.6.4; 20-01]; also a row 6 member in 2025). Confirm no trip on the submittal | NFPA 20-2025 §10.4.6.4 (20-01); no-trip rule NEC 695 ~ `[V]` |
| C7 | Remote start / BMS write access | Read-only monitoring; any remote interface can start, never stop or inhibit. NFPA 20-2025 adds cybersecurity reference to NEC 110.3(A)(8) ~ `[V]` | FM DS 3-7 §2.2.1.3; NFPA 20-2025 SR-21 |
| C8 | Pressure sensing | ½ in. sensing line on every controller incl. jockey (FM DS 3-7 §2.4.11.2 ~); dual discharge transducers where the pump is the only delivery path (controller uses the lower reading) | FM; OEM |
| C9 | Analog-input contention | Where suction pressure and tank level (or flow and spare temperature) share one input, record the choice; the un-chosen signal goes to a separate monitored device | OEM fourth layer |
| C10 | Weekly automatic test | Enabled; start/stop times recorded; stuck-test-solenoid diagnostic enabled where offered | OEM; NFPA 20-2025 SR-21 `[V]` |
| C11 | Enclosure | NEMA 2 is indoor only; exterior skid or weather-exposed room needs an outdoor NEMA type specified at order | NFPA 20-2025 SR-16/22 `[V]`; OEM |
| C12 | Jockey supply | Not through the fire-pump controller or its transfer switch | [CODE NEC 2017/2020/2023 §695.6(I)(6); 2026 §695.7(I)(8), pull 70-01]; FM DS 3-7 §2.4.14 |

## 7. Step D: pump-room environmental schedule (floor AND maximum)

| Room | Parameter | Floor | Maximum | Governs |
|---|---|---|---|---|
| Electric pump room | dry-bulb ambient | > 40 °F (FM DS 3-7 §2.2.1.6; DS 2-81 §2.9.4.1) | ≤ submitted controller listing max (~104 °F / 40 °C on two OEMs; two OEMs silent → **demand datasheet value**, do not invent) | most stringent of insurer floor and product envelope |
| Diesel pump room | ambient | insurer floor for engine starting (FM DS 3-7 ~ `[V]`) | controller + engine listing max | as above; ventilation numbers → `combustion-air-and-hall-free-area` |

- Controller ambient alarms on held OEMs sit at or near the limit (low ~41 °F, high ~104 °F). Treat them as **limit annunciation**, not early warning. Put a warning band with a stated margin on a separate room temperature device (FA supervisory and/or BMS).
- FA low-temperature point (row 9): NFPA 72-2025 §17.19.5 (40 °F, per FA Skill pull 72-07) is the FA side; FP states the requirement and setpoint basis. Not an NFPA 20 signal in the captured chapters.
- Freeze-exposed pump houses: route heat trace and enclosure heat to `freeze-heat-trace-fp-piping`.

## 8. Step E: valve supervision schedule (rows 21 to 25, 26a, 26, 27)

§4.18 wording is the same in 2019, 2022 and 2025 [CODE; 2025 20-02; 2022 / 2019 20-03, 20-04]. Where provided: only valves actually installed.

| # | Valve | Duty | Source |
|---|---|---|---|
| 21 | Suction valve | supervised open | [CODE 2019/2022/2025 §4.18.1; 20-02, 20-03] |
| 22 | Discharge valve | supervised open | same |
| 23 | Bypass valves | supervised open | same |
| 24 | Backflow preventer isolation valves | supervised open | same; A.4.18: isolation and control valves identical with a backflow assembly [CODE annex 2019/2022; 20-04] |
| 25 | Control valves in the pipeline to the hose valve (test) header | supervised **closed** | [CODE 2019/2022/2025 §4.18.2; 20-02, 20-03, 20-14] |
| 26a | Automated water control valve assembly (**where provided**): reliable position indication; valve supervisory switch connected to a remote supervisory station; manual and automatic operation | Supervisory | [CODE 2019/2022/2025 §4.16.5.3.2(1) to (3); 20-02, 20-04] |
| 26 | Private main / loop control valves 2½ in. and up | supervised | Not NFPA 20; insurer (2½ in. threshold) / [CODE NFPA 24-2022/2025 §6.7.2 (supervision methods); §6.7.3 roadway-box gate valves exempt, pull 24-02; NFPA 24 sets no 2½ in. threshold] |
| 27 | Jockey pump isolation valves | supervision **not required**; no jockey FACP point required | [CODE 2019/2022/2025 §4.27.6.7; 20-02, 20-03] (pressure maintenance pump in 2019 / 2022). Optional jockey run / trouble [SYN] |

- Methods §4.18.1 [CODE 2019/2022/2025; 20-02, 20-03]: (1) central station, proprietary, or remote station signaling; (2) local signaling with audible signal at a constantly attended point; (3) locking open; (4) sealing + approved weekly recorded inspection inside owner-controlled fenced enclosures. Only (1) and (2) give an electrical point.
- **Company election [SYN]:** method (1) or (2), an electrical tamper switch to the FACP on every valve in rows 21 to 25 and 26a.
- FM enhanced-security valve supervision is an ITM lever; it lives in `itm-design-for-testability`.

## 9. Step F: transfer outage budget (for the C&E narrative)

Compute and show (script; inputs listed):
`t_restart = t_dropout_delay + t_gen_start + t_alt_accept + t_post_transfer + t_starter_ramp`
- Held OEM example values (method only, re-pin per submittal): ~3 s + ~15 s generator + ~3 s + ~2 s, then 5 to 8 s reduced-voltage ramp → **≥ ~23 s to restart command**, before the ramp.
- Write the C&E narrative around a pump that is **off** for that window. Never write the ATS bridges the outage.
- Hand the number to `dry-preaction-water-delivery-screen` and `multizone-preaction-zone-alignment` only as a narrative note; it does not change the 60 s / 30 s delivery requirements, and this Skill does not re-run delivery time.

## 10. Step G: acceptance-test union

- Start counts: take the **union** of the OEM field acceptance form and any owner/federal overlay. Held example: 10 manual + 10 automatic (UFGS 21 30 00) + 6 emergency-handle + 1 remote per source (OEM form) = 27 per source, 54 on a two-source machine. NFPA 20 own count: no fewer than six automatic and six manual operations [CODE 2019/2025 §14.2.7.2, pull 20-09 (ORD-FP-012)] (§14.2.6 is the general field-acceptance procedure; the union is correct either way). NFPA 20-2019/2025 §14.2.7.2: 6 automatic + 6 manual starts (code floor); 10+10 per UFGS (governs, most stringent).
- Every Step A signal is **witnessed at the FACP / supervising station**, including ATS-alternate and phase loss. The OEM form verifies only some contacts; it is a pre-test checklist, never the acceptance record.
- Record: controller vs motor nameplate FLC and LRC side by side; rotation and phase reversal on **both** sources; cut-in, cut-out, run-period, sequential-start timer, weekly test times; three-party (controller / motor / pump vendor) hold point before first start; signed NFPA 20 → NFPA 25 hand-off (NFPA 20 §14.4 hands off to NFPA 25; acceptance records are §14.3 [CODE 2019/2025 titles, pull 20-09 (ORD-FP-012)]).
- Acceptance amps: By enforced edition: **2025** nameplate service-factor amps (or manufacturer documentation), FLA × SF only where SF amps are not provided [CODE 2025 §14.2.6.7.1 / §14.2.6.7.1.1]; **2019/2022** FLA × nameplate SF [CODE 2019 §14.2.6.6.4; 2022 §14.2.6.7.1]; pull 20-12. Verify with the engineer of record: where SF amps are listed, conservative assumption = check both figures on any edition and the lower governs (NFPA 20-2025 SR-23/24).
- Commissioning package → `commissioning-ist-acceptance-packet`.

## 11. Step H: hand-off contact list to the FA side

Deliver to `fa-fire-pump-and-preaction-supervisory-points` (FA owns classes, labels, modules, pathways, C&E rows):
- the Step B map keyed to point rows 1 to 12, 12a to 12g, 20 to 25, 26a, 26, 27 (strip, terminal, contact type, composite, delay, verdict);
- which valves have electrical supervision (Step E);
- room temperature device(s) and setpoints basis (Step D);
- the refuse list items the FA designer must **not** wire (C1, C3, C7);
- open `submittal confirm` items.
Signal class is fixed by NFPA 72 §23.8.5.9.2 [CODE 2019/2022/2025; 72-41]: everything except pump running is Supervisory. Only row 1 (Supervisory or Alarm) is an FA / AHJ / insurer election.

## 12. Step I: show-and-verify (script, with negative tests)

Validate:
1. Every Step A / Step E row (1 to 12, 20 to 25, 26a, 26, 27 as applicable; 12a to 12g only if discrete points were requested) has a Step B terminal or a non-discrete verdict with mitigation.
2. If two sources exist, rows 4 and 5 (ATS strip) are present (§10.4.8 requires their contacts when a transfer switch is fitted).
2b. No row other than row 1 carries a class other than Supervisory; no NFPA 20 signal mapped to FA trouble.
2a. Row 6 condition list matches the enforced edition (4 for 2019 / 2022, 9 for 2025).
3. No row maps a lockout, inhibit, or load-shed function to a field input.
4. Every separately-required FM signal has a separate terminal or is `unresolved`.
5. Room schedule has both a floor and a maximum; the maximum cites a product document, not ASSUMED-as-listing.
6. Outage budget arithmetic reproduces from listed inputs.
7. Start-count union ≥ each source list, per source.
Negative tests: drop the ATS strip → must fail check 2; wire Lockout → fail 3; delete room max → fail 5.

## 13. Status vocabulary

`grounded` / `provisional` / `unresolved` / `comparison-only` / `handoff` / `RFI-variance` / `submittal confirm`. Every ASSUMED value appears in the status register with reason.

## 14. Hand-offs (reciprocal)

- Pump rating, churn, driver block (diesel tank, NEC 695 OCPD, jockey sizing and setpoints) → **`pump-envelope`** (§7A). This Skill consumes its pump count, driver, and jockey setpoints.
- Feeder, breaker coordination, voltage drop, GFPE collision → *fire-pump circuit power integrity and selective coordination* (sibling recipe).
- FA monitor points, classes, labels, modules → **`fa-fire-pump-and-preaction-supervisory-points`** (DC FA side).
- Releasing C&E rows, DI sequence → **`preaction-releasing-c-and-e-soo`**.
- Disconnect / power isolation logic in the building → **`power-isolation-disconnect-control`**; pump circuits are never in a shunt or EPO path.
- Pump room in or near MV switchgear → **`mv-switchgear-room-package`**.
- Test header, valve supervision interval levers, alarm isolation → **`itm-design-for-testability`**.
- Commissioning record → **`commissioning-ist-acceptance-packet`**.
- Diesel room ventilation → **`combustion-air-and-hall-free-area`**. Freeze → **`freeze-heat-trace-fp-piping`**.
- Edition conflicts across layers → **`most-stringent-basis-matrix`**.
- System family missing or SI/NI → **`suppression-technology-selection`**.
- Packet → **the input packet** (optional).

## 15. Stop list

Stop (and say why) when:
- SI/NI preaction is the BOD → Stop + `RFI-variance`.
- Foam elected → Stop. Clean agent → hand-away. Mist → `PRACTICE REFUSED`.
- Anyone requires a wired Lockout, inhibit, load-shed, or BMS stop on the fire pump and will not withdraw it → Stop + RFI to owner and insurer; do not issue the configuration.
- Canada is out of scope.
- You would need to present an ASSUMED terminal, delay, or temperature limit as an OEM listing value → do not; keep it ASSUMED / `submittal confirm`.
- You would need to quote NFPA 20 text outside pulls 20-01 to 20-05 as adopted → cite with `[V]` and "needs portal lookup"; never invent wording. Pins inside pulls 20-01 to 20-05 are [CODE] with edition and pull id.
Missing inputs are **not** a Stop.

## 16. Not this Skill

Pump sizing or curve; driver OCPD or feeder sizing; FA panel design, signal classes, or NAC; preaction air/N2 supervision setpoints (FP trim and `nitrogen-inerting-and-c-factor-gate`); water delivery time; ITM intervals.

## 17. Output

1. Basis line (editions, insurer, owner, local amendment, OEM + IOM rev).
2. Step A matrix. 3. Step B terminal map. 4. Step C spec clauses (copy-ready) + commissioning lines. 5. Step D room schedule. 6. Step E valve schedule. 7. Step F outage budget with inputs. 8. Step G acceptance union. 9. Step H FA hand-off. 10. Status register (ASSUMED, `[V]`, `submittal confirm`). 11. Delta vs NFPA 20-2025.

## 18. Jockey and fire-pump start ladder

Order, top to bottom: jockey stop, then jockey start, then fire-pump start **below** jockey start, then each extra pump about 10 psi lower. The fire pump is not the jockey [CODE NFPA 20-2025 §4.27.7].

Insurer sheet, where that sheet controls [OWNER/insurer]: FM DS 3-7 §2.4.11.6 sets jockey start at churn plus maximum static plus 5 psi, jockey stop at start plus 10 psi, and fire-pump start at 5 to 10 psi below jockey start. §2.4.11.5 keeps fire-pump start as close to churn as practical. Where AXA XL PRC.14.2.1 controls, the jockey differential is at least 15 psi and fire-pump start is about 10 psi below jockey start. The controlling carrier governs. Do not blend the two sheets.

Worked insurer arithmetic only (1,000 gpm, 80 psi rated, 95 psi churn, 60 psi static): jockey start 95 + 60 + 5 = 160 psi; jockey stop 170 psi; fire-pump start 150 to 155 psi; a second pump 140 to 145 psi. Absolute setpoints stay with the engineer of record. Do not copy this arithmetic onto another pump.

Wrong pattern: fire-pump start about 5 psi above jockey stop (170 + 5 = 175 psi on the worked case). The fire pump then starts before the jockey on every leak. That violates NFPA 20-2025 §4.27.7 and the annex intent that the fire pump is not the pressure-maintenance pump. Do not use it.

Annex A.14.2.6(4) is advisory. In NFPA 20-2019, NFPA 20-2022, and NFPA 20-2025, jockey stop is churn plus the minimum static supply, and jockey start is at least 10 psi below that stop. Fire-pump start is 5 psi below jockey start in NFPA 20-2019 and NFPA 20-2022, and 10 psi below jockey start in NFPA 20-2025. Each extra pump steps another 10 psi lower. When the pressure-switch differential will not meet that example, set the absolute points from the test gauges and verify them with the engineer of record. Figure A.4.27.6.5 stays optional PARK and is not asserted.

Where an insurer sheet and NFPA both apply, take the controlling carrier and state which edition of A.14.2.6(4) was used for the NFPA layer.

## 19. Diesel stop, overspeed, and minimum run

The substance of NFPA 20 §12.7.5 and §12.7.6 is the same in the 2019, 2022, and 2025 editions.

- Stop the engine by hand from inside the controller. An outside stop is permitted only after every starting cause has returned to normal and the controller is back in automatic.
- Do not shut the engine down automatically while a starting or running cause is still present. Automatic shutdown is limited to automatic testing, overspeed lockout, and a case the authority having jurisdiction has approved.
- Overspeed lockout is one of those permitted automatic shutdowns. It stops the engine and holds it out. It is not the minimum-run timer, and it is not permission to omit that timer when some other automatic stop is proposed.
- Where automatic shutdown after an automatic start is allowed, the minimum-run timer is at least 30 minutes. That timer is the code floor for the approved case. It is not the insurer run-period in C4.
- C4 stays the insurer layer: manual stop, and about 10 minutes after cut-out if a run-period is ever turned on. Where automatic shutdown has been approved, 30 minutes is more stringent than that 10-minute note. Where the insurer or the authority having jurisdiction forbids automatic stop, manual stop wins. Name the rule you took.
- §12.7.6: the emergency control bypasses the automatic circuits so the engine can be started and kept running by hand.
- The annex prefers manual shutdown. That sentence is advisory. Design practice is manual stop. Do not enable automatic shutdown after an automatic start without approval and the 30-minute timer.

An alarm silence on the diesel controller re-sounds within 4 hours. A trouble silence re-sounds within 24 hours [CODE NFPA 20-2025 §12.4.1.5, §12.4.1.6]. Remote diesel signals are not powered from the engine starting batteries (§12.4.2.1, already in A2).

Do not paste the electric signal list onto a diesel controller. Loss of power, phase reversal, loss of phase, alternate source, and the transfer-switch isolating switch live in §10.4.7. They are not diesel points. A diesel still needs the separate main-switch-off-or-manual point (row 11), low fuel at two-thirds tank (row 12e), and each battery failure (row 12d). Copying the electric list leaves dead power and phase points and drops those diesel points.

Phase loss on an electric controller is often a screen alarm only. Land a discrete contact or a documented composite, and verify that landing with the engineer of record. A local fire code may also require pump-room valve tampers as supervisory points in addition to NFPA 72 §23.8.5.9. Apply that addition only where the amendment is adopted. Optional annex notes under A.12.4.1 are not asserted. Delta versus NFPA 13: none. NFPA 20 controls this section.
