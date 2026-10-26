---
name: ESS isolation venting and duration
description: >-
  NFPA 69 explosion control for a generic Li-ion BESS room. Mixture LFL and
  percent setpoints come from lfl_setpoints. An election or a duration the
  tool does not return is ASSUMED. Not a sprinkler basis of design.
---

# ESS isolation, venting, and duration

The desktop starter reads the starter block in this file and does not copy it into the application.

**Intake.** A missing input is ASSUMED (the value and why). Do not present an ASSUMED value as a calculated figure or as a cited code value. **Scope lock.** The sprinkler basis of design stays wet pipe, dry pipe, or double-interlock preaction. This skill does not elect foam, clean agent, water mist, deluge, or single-interlock. An explosion-control starter is not that election.

Cite the section and the edition. Where this pack does not pin an edition year, say the year is unpinned and label it ASSUMED. Do not invent a section. Do not paste the standard. Generic room only. No job name, client name, personal name, or vendor catalog.

## What the tool owns

`lfl_setpoints` owns the mixture LFL and each setpoint vol% and ppm. Pass the off-gas mix, the component LFL table, and each percent in the starter block. Do not compute Le Chatelier in the reply. The tool does not choose a code percent, an election, or a duration. `calcs/fa/lib/lfl.py` is the arithmetic. Do not add a code threshold there.

Pipe gallons and t_total stay on the zone tool plan. Do not recompute them here. A delivery time from `dry_delivery_screen` or `di_trip_to_water` is an optimistic screen, not a listed water-delivery-time calculation.

## Starter block

The desktop reads this block after the tool plan. Keep the field names. The prose below is the method. The block is the cite list the starter prints. A percent here is an input to the tool. The tool returns vol% and ppm.

```starter
screen: n69-ccr
pct: 25
basis: diluted
section: NFPA 69 8.3.1
edition: unpinned
path: combustible concentration reduction

screen: n855-exhaust
pct: 25
basis: diluted
section: NFPA 855-2023 9.6.5.1.5.4
edition: 2023
path: normal-operation exhaust

screen: n855-ccr
pct: 10
basis: diluted
section: NFPA 855-2023 9.6.5.6.7(1)
edition: 2023
path: explosion-control gas detection

election: combustible concentration reduction
election_section: NFPA 69 8.3.1

duration: 24 h standby and 2 h alarm
duration_section: NFPA 855-2023 9.6.5.6.7(4)

note: NFPA 855-2023 9.6.5.1.5.4(3) is 2 h standby on the exhaust path only. That duration is not this election and it is not calculated.
note: IFC 2024 1207.6.1.2.4 names the same 25 percent exhaust start. It is not a second setpoint.
note: Sprinkler basis of design stays wet pipe, dry pipe, or double-interlock preaction. This starter does not elect foam, clean agent, water mist, deluge, or single-interlock.
```

## Method

1. Read this skill before drafting. Draft in synthesis mode, after the tool plan.
2. The room is a generic Li-ion BESS room. Do not copy another room's mix, stored energy, or fan rate.
3. Off-gas composition. If the designer did not supply a cell off-gas report, keep the sample mix and label the composition ASSUMED. Component LFL values shipped with that mix are sample inputs. The mixture LFL is calculated.
4. Call `lfl_setpoints` with the three screens. Quote each mixture LFL and each setpoint the tool returns. Those figures are calculated. Do not invent vol% or ppm.
5. NFPA 69 8.3.1 is the combustible-concentration-reduction screen at 25 percent of LFL. This pack does not pin the NFPA 69 edition year. Label that year ASSUMED unpinned. Do not treat 25 percent as a number you calculated. Confirm the adopted edition before issue.
6. NFPA 855-2023 9.6.5.6.7(1) is the explosion-control gas path at 10 percent of LFL. NFPA 855-2023 9.6.5.1.5.4 is the normal-operation exhaust path at 25 percent of LFL. Pass both. Do not collapse them into one alarm. IFC 2024 1207.6.1.2.4 names the same 25 percent exhaust start. It is not a second setpoint.
7. Use the diluted (whole-gas) basis for a room detector. The fuel-only mixture LFL is the Le Chatelier result. The tool returns both. Setpoints in the starter block use the diluted basis.
8. Election. No tool returns one. This starter uses combustible concentration reduction and labels it ASSUMED. Deflagration venting is not sized here. Isolation hardware is not sized here. Explosion suppression is not a clean-agent basis of design. Do not size it.
9. Duration. No tool returns one. On the explosion-control path, label ASSUMED the NFPA 855-2023 9.6.5.6.7(4) gas-detection screen: 24 h standby and 2 h alarm. NFPA 855-2023 9.6.5.1.5.4(3) asks 2 h standby only, and only on the exhaust path. Show that difference. Do not call either duration calculated. Hand the battery math to `fa-secondary-power-battery-calc`. Smoke and fire detection on the same room is NFPA 855-2023 4.8.3 (24 h standby and 2 h alarm). That row is not a gas-panel duration.
10. Signals. Hand off to `fa-supervising-station-signal-schedule` (IFC 2024 1207.5.4 and 1207.6.1.2.3, NFPA 855-2023 4.8.4 and 9.6.5.6.7). A gas alarm is not a supervisory signal on the explosion-control path.
11. Power isolation. `power-isolation-disconnect-control` hands a room above its in-rack line to this skill. Do not rebuild that package here. Do not invent a disconnect count.
12. Sprinklers. Hand density, hose, and water duration to `density-area-dry-increase`. Installed Li-ion ESS is not the ordinary-hazard white-space table. Do not recompute zone gallons or t_total. If the request names a zone total and a t_total, quote them. Those gallons and seconds govern when the narrative disagrees. The double-interlock draft section stays 21 13 19.
13. A sentence that is designer judgment, and that no tool returned, is use best judgment. Keep that label off calculated figures and off ASSUMED figures.
14. The narrative is a draft for the engineer of record. Do not claim a stamp.

## Out of scope

Foam, clean agent, water mist, deluge, and single-interlock as the sprinkler basis of design. Do not size a vent, a suppressant mass, or a vendor panel from this starter. A jurisdiction outside the stated NFPA, IBC, and IFC basis is out of scope. Canada is out of scope.

## Handoffs

| Work | Handoff |
|---|---|
| Sprinkler density, area, hose, water duration | `density-area-dry-increase` |
| Gas-detection battery | `fa-secondary-power-battery-calc` |
| Supervising-station class | `fa-supervising-station-signal-schedule` |
| Power isolation and disconnect | `power-isolation-disconnect-control` |
| Compartment rating | `fire-area-compartmentation-schedule` |
| System family election | `suppression-technology-selection` |
| Zone gallons and trip time | the zone tool plan |
