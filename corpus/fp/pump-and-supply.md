# Hydrant supply and pump envelope

Demand (`qd`) comes from the density-area note. Supply is a separate curve. Do not schedule a rated pump flow and pressure while the supply test, the basis-of-record pressure, or another gating question is still open. A synthetic rated pressure frozen into an equipment schedule is the failure this note exists to prevent. Listed 100, 125, and 150 psi ratings are not a menu of screening heads.

## Supply curve

From a two-point flow test (static pressure, residual pressure, flowing gpm) build the N^1.85 curve and read available pressure at the demand. `calcs/fp` op `hydrant_supply` does that step. One-segment relocation of the test, when used, is an explicit input.

FM DS 3-0 (March 2010) was checked for a maximum water-supply test age. No explicit maximum was found in that sheet, so test age stays `[V]`. A carrier limit of two years, or an NFPA 291 practice, governs only when that document is the one that applies. Section 2.1.1.2 of DS 3-0 lists deterioration among the reasons to test, which supports asking for a fresh test. Table 3 gives underground unlined cast-iron C by age and corrosiveness. Use it when the pipe age is known. Do not invent a C.

Hose stream and duration ride with the demand. They are not added a second time on the supply side.

## Envelope

Screen a listed centrifugal pump at rated flow, at churn, and at 150 percent of rated flow through `calcs/fp` (`pump_envelope`). Pass or fail against the demand and the suction condition. Do not publish `rated gpm at rated psi` as the job's pump until those gates are closed.

Relief: NFPA 20 §4.20. Compare net shutoff plus maximum static suction with the rating. The calc returns whether a relief valve is needed. Do not skip the check because a prior schedule omitted it.

Diesel driver derate, NFPA 20-2025 §11.2.2.4 and §11.2.2.5, is additive: 3 percent per 1,000 ft above 300 ft, plus 1 percent per 10 °F above 77 °F. Altitude and temperature are site inputs. Do not reuse a prior site's horsepower.

The pump-room controller, ambient limits, and supervisory points are `fire-pump-controller.md` and the fire-alarm supervisory note. This note does not size the controller.
