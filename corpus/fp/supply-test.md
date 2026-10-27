# Supply test and the base-of-riser curve

Compare supply and demand at the same point. A hydrant test is the supply at the test. Demand is at the base of the riser. Relocate the test for friction and elevation before you judge it. The N^1.85 curve and the pump envelope are `pump-and-supply.md`. This note is the test and the deductions.

## How the test is taken

FM DS 3-0 (March 2010) and the usual carrier field procedure agree on the technique. NFPA 291 is the code-side method. Confirm the adopted edition.

- Flow enough water that the test point sits near the demand. Extrapolating a short test is the weak part of the curve.
- Read static with no flow, residual during steady flow, and pitot at the stream. Confirm the orifice to the nearest 1/16 in.
- Open the flowing hydrant fully. A throttled or broken stream is not a reading. Keep pitot at or above 10 psi (DS 3-0). Keep the public-main residual at or above 20 psi during the test.
- Do not read flow and pressure on the same hydrant. If there is no other hydrant, the main residual is about 3 psi higher than the barrel gauge. Say that you used the correction.
- Do not drop the residual so low that the main can collapse. Close hydrants slowly. Restore every valve, and compare the result with the last test.

Pitot flow is Q = 29.8 × c × d² × √p, with Q in gpm, d in inches, and p in psi (DS 3-0 Eq. 1; the constant is 29.83 in the theoretical form and 29.85 on one carrier sheet). Do not mix coefficients. FM DS 3-0 Table 4 uses 0.80 for a smooth hydrant butt, 0.70 for a square butt, and 0.60 for an inset butt. A smooth underwriter nozzle is 0.97. A carrier sheet uses 0.90 for a smooth rounded butt and 0.98 for a playpipe. Pick one set and name it.

Elevation is 0.433 psi per foot. Add it when the reference point is below the gauge.

A pumped supply is three points, not one residual: churn, 100 percent of rated flow, and 150 percent (`pump-and-supply.md`). Do not add a standby pump's curve on top of the supply it draws from.

## What gets deducted

Hose that shares the supply is deducted once, on the supply side. Duration is stored volume divided by sprinkler flow plus the deducted hose flow (DS 3-0 Eq. 30). Both flow and duration have to pass.

Fitting loss on the underground run is usually small. A backflow preventer is not small. The 5 psi figure in DS 3-0 §3.3 is a screen for whether to count the device. It is not the loss to carry. Planning floors and the certified curve are `backflow-preventer.md`.

A carrier grades a supply Good, Fair, or Poor and then adjusts for duration. Excellent, on that sheet, needs two good supplies. A 4 hour duration and a mandatory second supply on the same sheet are for oil and chemical occupancies. They do not transfer to a wet, dry, or double-interlock hall. The design target remains the insurer demand for the required duration, not the letter grade.

Test age is local. One carrier will not use a test older than 5 years and prefers 2 years. DS 3-0 states no maximum (`pump-and-supply.md`). Do not paste another city's 6 month or 12 month rule, and do not invent a company safety factor in psi. Ask the authority and the purveyor what margin they enforce, and record it as their layer.

## Two suction numbers

A single test is a snapshot. Ask the purveyor for the seasonal and daily range. On a tank, the drop during the design duration is part of the design. Check supply against demand at the end-of-duration water level. Check churn against the full-tank static. One suction pressure cannot do both jobs (`variable-speed-pump.md`).

Storage outside the hall can set a larger demand than the hall (`storage-design.md`). The campus supply, the tank, and the pump follow the larger number.
