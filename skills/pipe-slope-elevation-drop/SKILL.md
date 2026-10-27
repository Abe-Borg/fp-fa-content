---
name: Pipe slope elevation drop
description: >-
  Use when you have a pipe run length and its slope or pitch and need the
  elevation drop from one end to the other, one segment or a sum of segments.
  Wet, dry, or double-interlock piping, or any pitched line. Not hydraulic
  demand, not volume takeoff, and not a drainage-code pass or fail.
---

# Pipe slope elevation drop

**Intake.** A missing input is ASSUMED (the value and why). Do not present an ASSUMED value as a measured length or a cited code pitch. **Scope lock.** This geometry applies to wet, dry, and double-interlock piping. It does not elect a system. Foam, clean agent, water mist, and single-interlock are out of scope. Show the arithmetic. Never invent a length or a slope in silence. Cite a section and an edition only when a code pitch floor is checked as an optional overlay. Verify a pitch-compliance judgment with the engineer of record. Do not claim a stamp.

Given length and slope, return elevation drop. Do not size pipe, prove drainage, or run hydraulics.

## 1. Inputs

| Input | Required | Notes |
|---|---|---|
| Segment ID (or single) | no | For multi-run tables |
| Length L | yes | Same unit family as the drop report (default ft) |
| Slope or pitch value | yes | See the unit forks |
| Slope unit | yes | One of: in/ft, percent, ft/ft (decimal), 1:n (rise:run), degrees |
| Slope reference | no | Default along-pipe (grade measured on the pipe axis). Alternate: horizontal (rise over horizontal run). If missing, ASSUMED along-pipe, flagged |
| Report units | no | Default: print both inches and feet |

If L or the slope is missing, stop and ask, or use ASSUMED only when the parent task named a value.

## 2. Unit forks to a common slope s (ft drop per ft of the stated reference)

Convert the stated slope into a decimal slope s = rise/run on the stated reference (along-pipe or horizontal).

| Stated unit | Conversion to s (ft/ft) |
|---|---|
| in/ft (pitch) | s = (in per ft) / 12 |
| percent grade | s = percent / 100 |
| ft/ft (decimal) | s = the value as given |
| 1:n (rise:run) | s = 1 / n. If the note says n:1, invert it and flag the inversion |
| degrees from horizontal | s = tan(theta) with theta in radians on the horizontal-reference path. For drop along the pipe, use the sine formula below |

Shop default when the pitch is bare (for example a bare quarter inch): treat it as in/ft. Label that ASSUMED in/ft and flag it.

## 3. Drop formulas

### 3A. Slope given along the pipe (default)

Grade is drop per unit of pipe length.

```
drop_ft = L_ft * s
drop_in = drop_ft * 12
```

Check: 100 ft of pipe at 1/4 in/ft. s = 0.25 / 12 = 0.020833. drop_ft = 2.0833. drop_in = 25.0.

### 3B. Slope given on the horizontal, length is the pipe axis

Pipe length is the hypotenuse.

```
drop_ft = L_ft * s / sqrt(1 + s^2)
drop_in = drop_ft * 12
```

For small pitches (s under about 0.02), the square-root term is about 1 and 3B is within about 0.02 percent of 3A. Still use 3B when the drawing notes pitch as horizontal grade and gives centerline length.

Check: L = 100 ft, s = 0.020833 (1/4 in/ft horizontal). drop_ft = 100 * 0.020833 / sqrt(1 + 0.000434) = 2.0829 (about 24.99 in).

### 3C. Angle from horizontal, length along the pipe

```
drop_ft = L_ft * sin(theta)
drop_in = drop_ft * 12
```

Theta from degrees: theta in radians = degrees * pi / 180.

## 4. Multi-segment runs

For each segment i with its own L_i and s_i:

```
drop_ft_total = sum of drop_ft_i
```

Same slope on a polyline, under 3A: drop_ft_total = s * sum of L_i.

Opposite pitch (up, then down): keep a signed drop (positive down in the flow direction, negative up) if the parent asks for net elevation change. Otherwise report the absolute drop per segment and the net separately. Default sign: positive means elevation loss in the stated flow direction.

## 5. Optional code-pitch overlay

Only when the parent asks whether the pitch meets a drainage floor.

- Name the enforced NFPA 13 edition. The delta baseline is NFPA 13-2025.
- Do not invent the drainage section number. If the adopted section is not in the inputs, report the geometry only and tag pitch compliance as unverified. Verify with the engineer of record.

The primary output is always the geometry drop, not a pass or fail on code pitch.

## 6. Output

| Seg | L (ft) | Slope stated | Unit | Ref (pipe or horizontal) | s (ft/ft) | Drop (in) | Drop (ft) | Flags |
|---|---|---|---|---|---|---|---|---|

Then one line: drop_in_total and drop_ft_total.

Always show the formula used (3A, 3B, or 3C) and the unit conversion once per distinct slope unit in the run.

## 7. Out of scope

| Ask | Hand off |
|---|---|
| Trapped volume, gallons | `sprinkler-system-volume-takeoff` |
| Dry or double-interlock water delivery time | `dry-preaction-water-delivery-screen` |
| Hydraulic friction, or C-factor | hydraulics, and `nitrogen-inerting-and-c-factor-gate` for C only |
| Freeze or heat trace | `freeze-heat-trace-fp-piping` |
| A length or a pitch with no basis | Stop, or ASSUMED with a flag. Never silent |

## 8. Checks

1. 100 ft main, 1/2 in/ft along the pipe. s = 0.5 / 12 = 0.041667. Drop = 4.167 ft = 50.0 in.
2. 40 ft branch, 2 percent grade along the pipe. s = 0.02. Drop = 0.80 ft = 9.6 in.
3. 75 ft, 1:50 horizontal, length along the pipe. s = 0.02. Drop = 75 * 0.02 / sqrt(1.0004) = 1.4997 ft, about 18.0 in.
