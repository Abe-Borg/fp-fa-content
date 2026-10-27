---
name: Pipe slope elevation drop
description: >-
  Use when a pipe run has a length and a slope or pitch and you need the
  elevation drop, for one segment or a sum of segments, on wet, dry, or
  double-interlock piping or any other pitched line. Not hydraulic demand,
  not a volume takeoff, and not a drainage-code pass or fail.
---

# Pipe slope elevation drop

**Intake.** The input packet is optional. A missing input is not a stop: state the value used and why, and label it ASSUMED. Do not present an ASSUMED value as a cited code or table value, and do not freeze a vendor SKU. **Scope lock.** Wet pipe, dry pipe, and double-interlock preaction only. Foam, clean agent, water mist, and single-interlock or non-interlock preaction are out of scope. If one of those is requested as the basis of design, record it and stop. Do not substitute another system and do not size it here. Cite the section and the edition. Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Verify judgment calls with the engineer of record.

Given length and slope, this method returns elevation drop. It does not size pipe, prove drainage, or run hydraulics. Do not invent a length or a slope. Label a filled-in value ASSUMED. Cite a code section and edition only when a pitch floor is checked as an optional overlay.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Segment id, or "single" | no | For a multi-run table |
| Length L | yes | Same unit family as the drop. Default feet. |
| Slope or pitch value | yes | See the unit forks |
| Slope unit | yes | One of: in/ft, percent, ft/ft, 1:n, degrees |
| Slope reference | no | Default along the pipe (grade on the pipe axis). Alternate: horizontal (rise over horizontal run). Missing: ASSUMED along-pipe. |
| Drop units | no | Print both inches and feet. |

If length or slope is missing and the parent task did not name a value, ask, or use ASSUMED only when the parent named the basis.

## Unit forks

Convert the stated slope to a decimal slope s, in feet of drop per foot of the stated reference.

| Stated unit | s (ft/ft) |
|---|---|
| in/ft | inches per foot, divided by 12 |
| percent | percent, divided by 100 |
| ft/ft | the value as given |
| 1:n | 1 / n. If the note says n:1, invert it and flag the reading. |
| degrees from horizontal | see the angle formula below |

A bare pitch such as "1/4" with no unit is ASSUMED in/ft. Flag it.

## Drop

### Along the pipe (default)

Grade is drop per unit of pipe length.

```
drop_ft = L_ft * s
drop_in = drop_ft * 12
```

Check: 100 ft at 1/4 in/ft. s = 0.25 / 12 = 0.020833. drop_ft = 2.0833. drop_in = 25.0.

### Horizontal grade, length along the pipe

Pipe length is the hypotenuse.

```
drop_ft = L_ft * s / sqrt(1 + s*s)
drop_in = drop_ft * 12
```

For a small fire-protection pitch (s about 0.02 or less), the square-root term is about 1, so the two formulas agree within a few hundredths of a percent. Still use this form when the drawing notes horizontal grade and gives centerline length.

Check: L = 100 ft, s = 0.020833. drop_ft = 100 * 0.020833 / sqrt(1 + 0.000434) = 2.0829, about 24.99 in.

### Angle from horizontal, length along the pipe

```
drop_ft = L_ft * sin(theta)
drop_in = drop_ft * 12
```

theta in radians is degrees times pi / 180.

## Several segments

Sum the segment drops. Same slope on a polyline, along-pipe formula: s times the sum of the lengths.

If pitch reverses, keep a signed drop when the parent asks for net change. Positive means elevation loss in the stated flow direction. Otherwise report the absolute drop per segment and the net separately.

## Optional pitch floor

This method's answer is the geometry drop, not a pass or fail on a code pitch.

Only when the parent asks whether the pitch meets a drainage floor: name the enforced NFPA 13 edition. The delta baseline is NFPA 13-2025. Cite the drainage section and the edition from the opened standard. If that section is not in hand, report the drop and mark pitch compliance unpinned. Verify the comparison with the engineer of record. Do not invent the section number.

## Output

| Seg | L (ft) | Slope stated | Unit | Ref | s (ft/ft) | Drop (in) | Drop (ft) | Flags |
|---|---|---|---|---|---|---|---|---|

Then drop_in_total and drop_ft_total. Show which formula was used, and show the unit conversion once per distinct slope unit.

## Worked checks

1. 100 ft main, 1/2 in/ft along the pipe. s = 0.5 / 12 = 0.041667. Drop = 4.167 ft = 50.0 in.
2. 40 ft branch, 2 percent along the pipe. s = 0.02. Drop = 0.80 ft = 9.6 in.
3. 75 ft, 1:50 horizontal, length along the pipe. s = 0.02. Drop = 75 * 0.02 / sqrt(1.0004) = 1.4997 ft, about 18.0 in.

## Out of scope

Foam, clean agent, water mist, and single-interlock or non-interlock as the sprinkler basis of design. Canada is out of scope. Trapped volume. Water-delivery time. Friction loss. Freeze protection. A survey length or a pitch with no stated basis, unless it is labeled ASSUMED.

## Handoffs

| Ask | Handoff |
|---|---|
| Trapped volume, gallons | `sprinkler-system-volume-takeoff` |
| Dry or double-interlock water delivery | `dry-preaction-water-delivery-screen` |
| C-factor | `nitrogen-inerting-and-c-factor-gate` |
| Freeze or heat trace | `freeze-heat-trace-fp-piping` |
