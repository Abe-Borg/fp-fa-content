---
name: fa-bess-gas-detection-layout-and-setpoints
description: >-
  Use when an indoor Li-ion BESS room uses gas detection to start exhaust
  ventilation (IFC 2024 1207.6.1.2, NFPA 855-2023 9.6.5.6, NFPA 69) and you
  must pick gas species from UL 9540A data, compute the mixture LFL, set the
  10 percent LFL alarm and 25 percent LFL design limit, choose sensor
  technology, and set sensor count and heights from airflow with exhaust on
  and with exhaust failed.
---

# BESS gas detection layout and setpoints

**Intake.** A missing input is ASSUMED (the value and why). Do not present an ASSUMED value as a cited code value. **Scope lock.** The suppression interface is wet pipe, dry pipe, or double-interlock preaction only. Foam, clean agent, water mist, and single-interlock as the basis of design are out of scope. Record and stop. Do not size them. Cite the section and the edition. Do not paste the standard. Unconfirmed section numbers carry VERIFY. Verify judgment calls with the engineer of record. Do not claim a stamp. Country gate (US | Canada). On a Canada job keep this skill. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Pin editions first (`fa-code-edition-delta-check`). Three-layer basis (code, insurer, owner). Most stringent wins. Run the mixture math in `calcs/fa/lib/lfl.py` (tool `lfl_setpoints`). Do not compute Le Chatelier in the reply. Copy the method, not a sample room's numbers.

## Basis

- [CODE] IFC 2024 1207.6.1.2 (Ventilation Based on Exhaust Rate): exhaust at not less than 1 cfm/ft2 of floor area, continuous or started by gas detection per 1207.6.1.2.4. Standby power 2 h (1207.6.1.2.1). Supervision (1207.6.1.2.3). 1207.6.1.2.4: gas detection per Section 916 starts exhaust above 25 percent of LFL and keeps it on until below 25 percent of LFL. Do not call this section explosion control by its title. Whether it is the project's explosion-control path is a separate question. Hand that election to `ess-isolation-venting-and-duration`.
- Two NFPA 855-2023 paths. Do not merge them into one setpoint.
  - Exhaust-rate path, 855-2023 9.6.5.1.5.4(1): detection starts mechanical exhaust when gas exceeds 25 percent of the mixture LFL. 9.6.5.1.5.4(3): gas detection gets at least 2 h standby. This matches IFC 2024 1207.6.1.2.4 at 25 percent [CODE].
  - Explosion-control path, 855-2023 9.6.5.6.7: only where detection starts a combustible-concentration-reduction system based on an NFPA 69 study. Start the reduction system at no more than 10 percent of LFL per (1). Send an alarm signal above 10 percent of LFL per (5)(b). That alarm maps to an FACU alarm, not a supervisory signal [CODE].
  - So 10 percent of LFL is a code value only on the 9.6.5.6.7 path. On the rate path, 25 percent is the code trigger [CODE].
  - Design practice, no value change: start exhaust and alarm at 10 percent of LFL on every BESS room, as an owner or practice choice on the rate path. Verify with the engineer of record. Conservative assumption: keep 10 percent. Never call the early start a substitute for a 9.6.5.6.7 design.
  - Record which path each room uses. If unknown, open an RFI. Do not guess the path and label it code.
- [CODE] IFC 2024 916.3: equipment designed for the gases detected and installed per the maker. 916.4 power. 916.5 standby power or trouble on power loss. 916.8: flammable-gas alarm above 25 percent of LFL. Gas audible and visible signals are distinct from fire alarm and carbon-monoxide alarm signals. 916.9 is signage next to gas alarm devices, not the signaling rule.
- [CODE] NFPA 855-2023 9.6.5.6.7(2): the reduction system stays on so gas does not exceed 25 percent of LFL of the mixture or of the components. Study basis is 9.6.5.6.1.1. Do not cite 9.6.5.6.6 for an indoor exhaust design. That section covers outdoor container ESS.
- [CODE] NFPA 69 combustible-concentration limit. The edition year is unpinned in this pack. Label the year ASSUMED. Confirm the adopted edition. NFPA 855 points at NFPA 69 on the exhaust path. The 25 percent screen is an input to `lfl_setpoints`, not a number you calculate. See `ess-isolation-venting-and-duration`.
- [HB] NFPA 855-2023 A.9.6.5.6.6 is annex guidance on detector selection and placement. It is not mandatory. A 1 to 3 minute response range is not confirmed here. Treat a sub-1-minute plume response as design practice. Verify with the engineer of record. Conservative assumption: plume heads with T90 under 1 minute.
- [HB] NFPA 72 placement factors include gas characteristics and response time. NFPA 72 has no BESS gas placement rule. Pin the 72 edition with `fa-code-edition-delta-check`.
- UL 9540A report text is not in this pack. Report-reading steps are design practice.

## Inputs (ASSUME and flag any missing)

1. UL 9540A cell report: vent-gas composition (volume percent) and LFL at vent temperature. If missing: ASSUMED hydrogen plus a carbonate VOC, and an open RFI that the 9540A report is missing.
2. Module and unit reports: vent-gas volume and rate, and propagation. If missing: ASSUMED single-module event. Verify with the engineer of record.
3. Room geometry, rack layout, vent locations, exhaust and makeup locations and rate.
4. Detector data: gas, range, units (percent LEL of one gas versus ppm versus percent LFL of the mixture), T90, and cross-sensitivity. Do not freeze a vendor SKU.

## Steps

1. Species. From the cell report, list flammable gases. Hydrogen is the primary percent-LFL target for LFP and NMC. Add a VOC (DMC or EMC) head as early warning, on top of hydrogen, never instead of it [PRACTICE]. Carbon monoxide is optional as a runaway marker.
2. Mixture LFL. Pass the off-gas mix and the component LFL table to `lfl_setpoints`. Also show the report value. Use the lowest as the basis [PRACTICE, conservative]. Component LFLs that were assumed for carbonates need engineer-of-record verification.
3. Setpoints. Pick the path first (9.6.5.1.5.4 rate, or 9.6.5.6.7 explosion control). Label each setpoint [CODE] or [PRACTICE] by path. Low alarm at no more than 10 percent of the basis LFL. High alarm at or below 25 percent of LFL. Convert each to ppm of each sensed gas by its share of the mixture. Quote the vol% and ppm the tool returns. Do not invent them.
4. Single-gas trap. If the vendor sets "percent LEL of hydrogen" (or of DMC) rather than percent LFL of the mixture, compute what mixture percent that reading really equals. A single-gas 10 percent LEL setpoint trips late when other flammables are present. Flag it and write an RFI: set on the mixture basis, or justify it with 9540A data. Verify with the engineer of record.
5. Technology. Pick per gas: catalytic, thermal-conductivity, or electrochemical for hydrogen. PID or MOS for VOC. Check cross-sensitivity (a carbon-monoxide cell can read hydrogen) and poisoning. Response time under 1 minute where a plume head is needed.
6. Time to setpoint. In a script, mixed-room and plume-zone fill time to 10 percent of LFL from the module vent rate. If plume time is shorter than head response, move heads to the plume or add heads. Verify with the engineer of record.
7. Count. At least one head per listed gas per room [CODE IFC 916.3]. "Per room" is a reading of that section, not a spacing table. Add heads per rack row or vent cluster where airflow splits the room [PRACTICE].
8. Heights. No fixed code height. Defaults, each labeled ASSUMED until justified: hydrogen within about 12 in of the ceiling. DMC (heavier than air) low, about 12 in above the floor. Each height stays open until the detection vendor justifies it from 9540A gas data, vent locations, geometry, and airflow, with exhaust running and with exhaust failed. Avoid dead-air pockets and direct makeup jets [PRACTICE].
9. Exhaust check. Steady mixed concentration is gas inflow divided by exhaust rate. It must stay below 25 percent of LFL for the design event (size from the unit report, not one module). Hand rates to the mechanical engineer. Do not size the fan.
10. Hand results to `fa-bess-gas-relay-map-and-cause-effect` and to `fa-secondary-power-battery-calc`.

## Auto RFIs

- 9540A report missing, or gas data absent.
- Setpoints in percent LEL of a single gas, without a mixture justification.
- Heights not justified for exhaust on and for exhaust failed.
- Gas detection listed as monitoring only, or as an add alternate, while it is the required exhaust start (IFC 2024 1207.6.1.2.4).

## Output

Species table. Mixture LFL from the tool. Setpoint table (mixture percent LFL and ppm per gas), each row tagged [CODE] or [PRACTICE] and tagged with the path. Technology pick. Time to setpoint. Head count and height schedule with justification status. RFI list. Delta versus the pinned NFPA 72 edition, which is silent on gas placement.

## Edition fence for Chapter 1207

The room has smoke detection or radiant-energy detection as the adopted fire code's detection section requires [CODE IFC 2024 §1207.5.4]. Read Table 1207.6 for the technology that fits the room. Do not infer a gas or a setpoint from the table title.

The lead sentence of IFC §1207.5.4 is the same in 2021 and 2024 [CODE]. The 2024 printing adds an exception for a small remote telecommunications structure with lead-acid or nickel-cadmium batteries. That exception is not a hall UPS room. §1207.5.4.1 differs by edition. Do not cite it until the edition row is split. Cite IFC §1207.6 and §1207.7 from the 2024 text only. The 2021 printing of those two sections is NEEDS HOLD. A gas setpoint past 25 percent of LFL is owner or maker, not this code row. The 25 percent alarm itself stays [CODE].

§1207.6.1.2.4 is the 25 percent of LFL exhaust start and the run-until-clear rule already in the basis. It is not a detection-battery section. Exhaust standby stays §1207.6.1.2.1. Detection power-loss trouble stays §916.5. Do not add a code claim that a detector failure is a supervising-station trouble under §1207.6.1.2.4. That class stays [PRACTICE] until the engineer of record closes it. Where NFPA 855 does not set the gas-start class, the class is [PRACTICE]. On the explosion-control path the alarm above 10 percent of LFL stays [CODE NFPA 855-2023 §9.6.5.6.7(5)(b)].

On a Canada job, stop. CAN/ULC-S524 is NEEDS HOLD. Do not map the IFC or NFPA 72 as Canada code. Foam and clean agent stay locked.

## Out of scope

Foam, clean agent, water mist, and single-interlock as the sprinkler basis. Do not size a suppressant mass or a vent from this skill. See the country gate in this skill.
