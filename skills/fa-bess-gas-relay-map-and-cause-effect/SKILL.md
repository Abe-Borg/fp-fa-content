---
name: fa-bess-gas-relay-map-and-cause-effect
description: >-
  Use when you must write or check the gas-detection relay map, fire-alarm
  points, and cause-and-effect for an indoor Li-ion battery room whose gas
  detection starts exhaust (IFC 2024 1207.6.1.2 and 916, NFPA 855-2023 9.6.5,
  NFPA 72, IMC 2024 509), including distinct gas notification and the
  monitoring-only trap.
---

# BESS gas relay map and cause and effect

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Canada is out of scope.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed section numbers carry **VERIFY**. Judgment calls: **Verify with the engineer of record**, and state the conservative assumption.
- Pin enforced editions first (IFC, NFPA 72, NFPA 855, NFPA 69, IMC). Run `fa-code-edition-delta-check`. Three-layer basis (code, insurer, owner). Most stringent wins.
- Short sentences. No em dashes. No CAD. Copy the method, not another room's point list.

## Basis
- [CODE] IFC 2024 1207.6.1.2.4: continuous gas detection per Section 916 starts the exhaust above 25 percent of the lower flammable limit. Exhaust stays on until the concentration is below 25 percent. Trouble on detection power loss is 916.5 and NFPA 855, not 1207.6.1.2.4. The section title is ventilation based on exhaust rate.
- [CODE] IFC 2024 1207.6.1.2.3: required exhaust is supervised by a central, proprietary, or remote station per NFPA 72, or by an audible and visible signal at a constantly attended on-site location.
- [CODE] IFC 2024 916.8: gas audible and visible signals distinct from fire alarm and from carbon-monoxide alarm. 916.9: signs next to gas alarm devices. 916.4 power connections. 916.5 standby power, or trouble on loss of power.
- [CODE] NFPA 855-2023 9.6.5.1.5.4(1) and (3): on the exhaust-rate path, detection starts exhaust above 25 percent of the lower flammable limit of the mixture, with 2 hours of detection standby. 9.6.5.6.7 applies only on the explosion-control path (an NFPA 69 study). On that path, start at no more than 10 percent, alarm above 10 percent, and do not exceed 25 percent. Duration is the figure in `ess-isolation-venting-and-duration`. Do not recompute standby hours here.
- [CODE] NFPA 72: gas detection that is part of the fire-alarm system follows the chapters that govern gas detection on a protected-premises system. The section does not assign alarm versus supervisory. Class the signals in `fa-supervising-station-signal-schedule`. Temporal-3 is fire. Temporal-4 is carbon monoxide. Neither is the gas tone.
- [CODE] IMC 2024 509.6.1: fire and smoke dampers are prohibited in a hazardous-exhaust duct. Applying the no-balancing-damper rule to battery-room gas exhaust is [PARA]. Verify with the engineer of record. Conservative assumption: no balancing dampers. Rated enclosure at rated walls and floors is 509.6.3 and 509.6.2. Hand duct construction and duct sprinklers to `ess-exhaust-duct-shaft-and-duct-sprinklers`.

## Hard fails (check these first)
1. Gas detection called monitoring only, an alternate, or a network or building-management point only, while it is the required exhaust start (IFC 2024 1207.6.1.2.4). The life-safety start and the fire-alarm signals are hardwired supervised contacts. A network point may duplicate them. It does not replace them.
2. Relay landing points not shown.
3. Gas horns or strobes on fire-alarm notification circuits, or using temporal-3 or temporal-4.
4. Any fire-alarm or HVAC sequence that stops the gas exhaust or its makeup air.
5. Fire, smoke, backdraft, or balancing dampers on the gas exhaust duct.
6. No high-gas signal and no trouble signal at the fire-alarm panel.

## Relay map

ASSUMED until the vendor riser confirms the names. Rename to the vendor relays. Do not invent extra relays to fill a drawing.

| Relay | Trips at | Lands at | Function |
|---|---|---|---|
| Low-start | Low, either gas | Exhaust starter or drive, and makeup-air unit or damper | Start and open. Latched. Manual reset only after the gas clears. |
| Low-alarm | Low, either gas | Fire-alarm monitor module | Gas alarm, own zone label. Alarm class on the explosion-control path, not supervisory [CODE NFPA 855-2023 9.6.5.6.7]. |
| High-notify | High, either gas, at or below 25 percent of the limit | Gas horn and strobes on the gas panel, or their own circuit | Distinct gas notification. Also sounding at the low threshold is a judgment. Verify with the engineer of record. Conservative assumption: yes. |
| High-panel | High | Fire-alarm monitor module | High gas to the fire-alarm panel. If the gas panel has no relay, add a listed expansion module. |
| Fault | Panel fault or power loss | Fire-alarm monitor module | Trouble to the panel and the station. Fail-safe: de-energize on fault. |

- On the explosion-control path, 10 percent does two jobs. One contact starts the reduction system. A separate contact is the alarm. Write both rows. One does not replace the other [CODE NFPA 855-2023 9.6.5.6.7].
- Low-start at 10 percent is [CODE] only on that path. On the rate path the code trigger is 25 percent. The 10 percent start is design practice. Verify with the engineer of record. Conservative assumption: keep 10 percent. Tag the row by path.
- Either gas at a level trips that level. Repeat the row per room.
- Shared relays across rooms: flag them. Per-room fans or dampers need per-room relays or expansion modules.

## Fire-alarm points
- Exhaust-fan proof (current switch and duct airflow switch), makeup air proven open, any motorized damper proven open, and the hand switch not left out of auto. Loss of proof after a command delay is supervisory [PRACTICE]. The delay is set at commissioning. ASSUMED 30 to 60 seconds until commissioning sets it.
- If the gas panel has fewer inputs than proof points, land the proofs on addressable monitor modules.
- Any motorized damper in the exhaust or makeup path fails open.

## Cause and effect

Minimum rows: gas low; gas high; gas below the low setpoint (exhaust stays on until manual reset); gas-detection fault or power loss (trouble; starting exhaust on fault is a judgment, conservative assumption is to start, verify with the engineer of record); makeup air not proven; exhaust loss of flow; room smoke or heat (fire alarm, exhaust keeps running if it is latched); waterflow; general HVAC duct smoke (shut recirculating HVAC only, never the gas exhaust); door holders release on room smoke, on a fire alarm, and on any gas alarm (gas release is a judgment, conservative assumption is yes, verify with the engineer of record).

Columns: exhaust, makeup air, gas notification, fire notification, fire-alarm signal class, supervising station, doors.

Where a row touches preaction release, hand that row to `preaction-releasing-c-and-e-soo` and `fa-double-interlock-releasing-cause-and-effect`. Do not rebuild the sprinkler matrix here.

## Notification
- Gas: amber strobe and a tone that is not temporal-3 or temporal-4, or a voice message. Sign next to each gas device [CODE IFC 2024 916.9]. Distinct-signal duty is 916.8. Tone choice: verify with the engineer of record and the authority having jurisdiction.
- Fire: temporal-3 and a clear strobe, on fire-alarm notification circuits.

## Steps
1. Take species and setpoints from `fa-bess-gas-detection-layout-and-setpoints`.
2. Run the hard-fail list against the drawings and the control sheets. Each fail is an RFI.
3. Fill the relay map with landing points. Mark ASSUMED where the vendor riser is silent.
4. Build the fire-alarm point list and the input-count check.
5. Write the matrix and the sequence notes.
6. Send signal classes to `fa-supervising-station-signal-schedule` and loads to `fa-secondary-power-battery-calc`.
7. Add an integrated-test line: gas, exhaust, makeup air, fire-alarm panel, and station. Hand the script to `fa-integrated-systems-test-matrix`.

Barrier hour rating and door hardware come from `fire-area-compartmentation-schedule`. Do not invent a 2-hour versus 3-hour election here.

## Output
Hard-fail table, relay map with landings, fire-alarm point list, cause-and-effect matrix, sequence notes, notification schedule, and the RFI list.
