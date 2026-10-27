# Thrust restraint for buried fire mains

Restrain or block every change of direction, every dead end, and every closed valve on the buried fire main. Push-on and mechanical joints are treated as having no longitudinal restraint. Aboveground sway braces are `seismic-bracing.md`. The main itself is `private-fire-mains.md`.

DIPRA's thrust-restraint procedure (7th edition, 2016) is the calculation method. It is not a code. Compliance is NFPA 24. Section 10.6.1 covers thrust blocks and §10.6.1.1.1 bases the thrust on the test pressure. Section 10.6.2 covers restrained joints. Cite the adopted edition.

## Design pressure

Use the highest pressure the buried main will see. That is pump churn on top of maximum static suction, and then the test pressure, because the pipe-soil system is weakest at the new installation. A carrier floor of 50 psi above hydrostatic, and at least 250 psi, is that test-pressure rule stated as a minimum. Take the higher of the calculated test pressure and that floor. FM DS 3-10 Table 2.2.16.5 is built at 225 psi and 2,000 lb/ft². Name which pressure you designed to.

Restrained length is linear in that pressure. In the horizontal-bend equation, pressure is only in the numerator. On DIPRA's own example (30 in. ductile iron, 6 ft of cover, a 90 degree horizontal bend, laying condition 4), 150 psi needs 55.2 ft and 250 psi needs 92.0 ft. The lengths are that example. The ratio is the point: a higher churn pressure buys restrained joints at every fitting. Do not copy the 30 in. lengths onto a campus main.

## Which equation

Thrust at a bend is T = 2 P A sin(θ/2). Thrust at a dead end or a closed valve is T = P A. Area is the outside-diameter area from the pipe table, not the flow area. The safety factor on blocks and on restrained joints is 1.5.

| Focus | Restrained length |
| --- | --- |
| Horizontal bend, or a vertical bend upward | L = 1.5 P A tan(θ/2) / (Ff + Rs/2) |
| Vertical bend downward | L = 1.5 P A tan(θ/2) / Ff |
| Dead end | L = 1.5 P A / Ff, on the full-circumference friction |

Round up to whole pipe lengths, 18 or 20 ft. In the same example, the vertical downward bend was 163.9 ft and the dead end was 125.7 ft, against 55.2 ft for the horizontal bend. Route around obstructions in plan when you can. A hydrant lead, a fire-department connection, a future stub, and a closed sectional valve are all dead ends.

Polyethylene encasement uses Ff = 0.7 times the bare-pipe friction. On a bend that also has sidefill bearing, the example grew about 11 percent. On a friction-only focus (vertical down, dead end, tee branch, reducer) the same factor is about 43 percent. Compute each focus. Do not carry one penalty across the schedule.

Soil strength, friction angle, unit weight, and the laying condition are inputs from a geotechnical report. Laying condition moves the bearing coefficient. Specifying a better bedding can shorten the restrained length. A carrier default of 1,000 lb/ft² is the soft-clay row of the bearing table, one step above muck. It is conservative on better soil and wrong if someone treats it as a generic fact. Undisturbed soil, or fill compacted to at least 90 percent Standard Proctor, is the bearing face for a block. Block height is at least the pipe outside diameter and at most half the cover. Block width is one to two times the height.

Do not split one thrust between a block and restrained joints, each taking a share. They need different movement to develop strength. Design each for the full thrust if you use both.

Restrained pipe inside an ungrouted casing does not count toward the length. Start the count outside the casing, or grout the annulus. In unstable ground, restrain the whole line. Fittings closer than their calculated length share the pipe between them. As a pair of bends approaches 90 degrees, restrain everything between them and treat the outer legs as dead ends.

Joints can deflect up to about 8 degrees, depending on type and size. A deflected joint makes less thrust than a fitting. Prefer it when the alignment allows.

Setscrew retainer glands are a carrier exclusion near buildings, pump houses, and corrosive soil. Use restrained joints, rods, clamps, or blocks.

Write the excavation limit into the turnover. Digging beside a pressurized restrained line removes the soil that is the restraint. On a campus built in phases, depressurize the segment or add blocking before the soil is opened.

FM DS 3-10 prefers blocks, multiplies the area by four in soft clay, and treats rods alone as inadequate above 12 in. Reconcile that with the DIPRA length when both apply. Do not average them.
