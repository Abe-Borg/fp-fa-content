---
name: fa-bess-gas-detection-layout-and-setpoints
description: >-
  Use when an indoor Li-ion battery room uses gas detection to start exhaust
  (IFC 2024 1207.6.1.2, NFPA 855-2023 9.6.5, NFPA 69) and you must pick species
  from cell data, set the 10 percent and 25 percent of LFL thresholds, and
  place sensors for exhaust running and exhaust failed.
---

# BESS gas detection layout and setpoints

## Intake and scope (all FA skills)
- The input packet is optional. Any missing input gets a stated value, labeled **ASSUMED** (value used + why). ASSUMED is never shown as a code value. Keep going.
- Scope locks are hard Stops: suppression interface is wet, dry, or double-interlock preaction only. No clean agent. No foam. No water mist. Single-interlock as basis of design: record, Stop, RFI-variance.
- Canada is out of scope.
- Label every claim [CODE] [HB] [PARA] [PRACTICE] [OWNER]. Cite section AND edition. Never invent or paste licensed code text; paraphrase and cite. Unconfirmed section numbers carry **VERIFY**. Judgment calls: **Verify with the engineer of record**, and state the conservative assumption.
- Pin enforced editions first (IFC, NFPA 72, NFPA 855, NFPA 69, IMC). Run `fa-code-edition-delta-check`. Three-layer basis (code, insurer, owner). Most stringent wins.
- Run mixture math in a script. Show inputs. Short sentences. No em dashes. Do not copy another room's gas mix. No CAD.

## Basis
- [CODE] IFC 2024 1207.6.1.2 (ventilation based on exhaust rate): exhaust at not less than 1 cfm/ft2 of floor area, continuous or started by gas detection. 1207.6.1.2.1 standby power 2 hours on that path. 1207.6.1.2.4: gas detection per Section 916 starts exhaust above 25 percent of the lower flammable limit and holds it until the concentration is below 25 percent. Do not title this section "explosion control." Whether it is the project's explosion-control path is a separate question. Hand that question to `ess-isolation-venting-and-duration`.
- Two NFPA 855-2023 paths. Do not merge them into one setpoint.
  - Exhaust-rate path, 9.6.5.1.5.4(1): detection starts mechanical exhaust above 25 percent of the lower flammable limit of the mixture. 9.6.5.1.5.4(3): at least 2 hours of standby on that detection. This matches IFC 2024 1207.6.1.2.4 at 25 percent [CODE].
  - Explosion-control path, 9.6.5.6.7: only where detection starts a combustible-concentration reduction system based on an NFPA 69 study. Start at no more than 10 percent of the lower flammable limit (item 1). Alarm above 10 percent (item 5). Keep the reduction system from exceeding 25 percent (item 2). Duration on this path is the figure already pinned in `ess-isolation-venting-and-duration` (9.6.5.6.7(4): 24 hours standby and 2 hours alarm). Do not recompute it here.
  - So 10 percent is a code value only on the 9.6.5.6.7 path. On the rate path, 25 percent is the code trigger [CODE].
  - Design practice, no value change: start exhaust and alarm at 10 percent of the lower flammable limit on every battery room, as an owner or practice choice on the rate path. Verify with the engineer of record. Conservative assumption: keep 10 percent. Never call the early start a substitute for a 9.6.5.6.7 design.
  - Record which path the room uses. If unknown, issue an RFI. Do not guess the path and hide the flag.
- [CODE] IFC 2024 916.3: equipment designed for the gases detected and installed per the maker. 916.4 power. 916.5 standby power, or trouble on loss of power. 916.8: flammable-gas alarm above 25 percent of the lower flammable limit, with audible and visible signals distinct from fire alarm and from carbon-monoxide alarm. 916.9 is signage next to the gas devices. It is not the signaling rule.
- [CODE] NFPA 69 combustible-concentration limit is the study the explosion-control path points at. This pack does not pin the NFPA 69 edition year. Label that year ASSUMED unpinned, the same way `ess-isolation-venting-and-duration` does. Do not cite 9.6.5.6.6 for an indoor room. That section is outdoor container equipment.
- [HB] NFPA 855 annex text on detector selection is guidance, not a mandate. A 1 to 3 minute response band is not confirmed in this pack. Treat a response under 1 minute at a plume head as [PRACTICE]. Verify with the engineer of record.
- [HB] NFPA 72 placement factors include gas behavior and response time. NFPA 72 has no battery-room gas spacing rule.
- Cell-level vent-gas reports are not held in this pack. The reading steps below are [PRACTICE].

## Inputs (ASSUME and flag any missing)
1. Cell vent-gas report: composition in volume percent, and the lower flammable limit at vent temperature. Missing: assume hydrogen plus a carbonate vapor, and open an RFI that the report is missing.
2. Module or unit report: vent volume and rate. Missing: assume a single-module event. Verify with the engineer of record.
3. Room geometry, rack layout, vent locations, exhaust and makeup locations and rates.
4. Detector data: gas, range, units (percent of a single gas, parts per million, or percent of the mixture), response time, and cross-sensitivity.

## Steps
1. Species. List flammable gases from the cell report. Hydrogen is the primary percent-of-limit target for common lithium-iron-phosphate and nickel-manganese-cobalt cells [PARA]. Add a carbonate-vapor head as early warning, on top of hydrogen, never instead of it [PRACTICE]. Carbon monoxide is optional as a runaway marker [PARA].
2. Mixture limit. Run the mixture calculation in a script on the flammable fraction. Also show the report value. Use the lower of the two [PRACTICE]. Component limits that were assumed get a verify flag.
3. Setpoints. Pick the path first. Label each setpoint [CODE] or [PRACTICE]. Low alarm at no more than 10 percent of the basis limit. High alarm at or below 25 percent. Convert each to parts per million of each sensed gas by its share of the mixture.
4. Single-gas trap. If the vendor sets percent of the lower explosive limit of hydrogen alone, or of one vapor alone, compute what mixture percent that reading really equals. A single-gas 10 percent setpoint trips late when other flammables are present. Write an RFI: set on the mixture, or justify it with the cell report. Verify with the engineer of record.
5. Technology. Catalytic, thermal-conductivity, or electrochemical for hydrogen. Photoionization or metal-oxide for the vapor. Check cross-sensitivity, including a carbon-monoxide cell that also reads hydrogen, and check poisoning. Response under 1 minute where a plume head is needed [PARA].
6. Time to setpoint. In a script, mixed-room fill time and plume-zone fill time to 10 percent of the limit, from the module vent rate. If the plume time is shorter than the head response, move the head or add heads. Verify with the engineer of record.
7. Count. At least one head per listed gas per room [CODE IFC 916.3, PARA on "per room"]. Add heads per rack row or vent cluster where airflow splits the room [PRACTICE].
8. Heights. No fixed code height. Defaults, each one open until the detection vendor justifies it: hydrogen within about 12 in of the ceiling; a vapor heavier than air within about 12 in of the floor. Justify both with exhaust running and with exhaust failed, from the cell data, vent locations, geometry, and airflow. Avoid dead-air pockets and direct makeup jets [PRACTICE].
9. Exhaust check. Steady mixed concentration is gas inflow divided by exhaust rate. It must stay below 25 percent of the limit for the design event. Size that event from the unit report, not from one module, once the report exists. Hand rates to the mechanical engineer. Do not size the fan.
10. Hand species, setpoints, and head counts to `fa-bess-gas-relay-map-and-cause-effect`. Hand standby duration to `ess-isolation-venting-and-duration` and battery math to `fa-secondary-power-battery-calc`.

## Open items to raise every time
- Cell report missing, or gas data absent.
- Setpoints in percent of one gas, without a mixture justification.
- Heights not justified for exhaust on and exhaust failed.
- Gas detection listed as monitoring only, or as a network point only, while it is the required exhaust start (IFC 2024 1207.6.1.2.4).

## Output
Species table, mixture calculation, setpoint table (mixture percent and parts per million per gas) with the path labeled, technology, time to setpoint, head count and height schedule with justification status, open items, and the delta versus NFPA 72 (silent on battery-room gas placement).
