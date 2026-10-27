# Standpipe system beyond the Class I residual

Whether a Class I standpipe is required, the 100 psi residual floor, and supervisory air on a manual-dry pipe are `standpipe-class-i.md`. This note is the demand in gallons, who supplies it, and the test drain. Do not import a high-rise zone, a rooftop gravity tank, or an express riser into a hall. Static head at 0.433 psi per foot does not put a one-story building in that problem.

## Whether, and which class

The trigger is the adopted IFC or IBC §905, not the sprinkler hazard. IFC and IBC 2021 and 2024 §905.3.1 require Class III where the building is four stories or more above or below the grade plane, or the highest occupied floor is more than 30 ft above fire-department access, or the lowest is more than 30 ft below. Exception 1 allows Class I where the building is sprinklered throughout under §903.3.1.1 or §903.3.1.2. A single-story hall often misses the height trigger. A multi-story building or a tall support structure can hit it. Read the adopted section. Do not add a standpipe that no layer requires.

Company practice is Class I, 2-1/2 in. connections, no occupant hose, unless the adopted code or the owner requires hose. Hose may be omitted only where `standpipe-class-i.md` says so.

## Demand

NFPA 14-2024 §10.6: 250 gpm from each of the two most remote 2-1/2 in. outlets on the most remote standpipe (500 gpm), then 250 gpm for each additional standpipe where the floor is at most 80,000 ft². Above that area the second standpipe is 500 gpm and the third is 250 gpm where required. The maximum is 1,000 gpm where the building is sprinklered throughout and 1,250 gpm where it is not. If the adopted edition is 2019, use that edition's hydraulic demand. The class note's held 2019 cite is §7.10. An older commentary limited a 1,000 gpm cap to light hazard. A hall is not light hazard. Read the cap conditions before you stop adding flow.

The company residual at the most remote 2-1/2 in. outlet is 100 psi. A federal specification that uses 65 psi below 150 ft and 100 psi at or above 150 ft is comparison-only (`standpipe-class-i.md`).

A federal specification also splits who carries the flow: below 75 ft the fire department supplies a manual standpipe through the fire-department connection, and an on-site pump in a combination system is sized for the sprinkler demand; at 75 ft and above the pump includes the standpipe demand. That split is the specification, not §905. On an automatic standpipe, feed the simultaneous sprinkler and standpipe demand into `pump-and-supply.md`. On a manual standpipe, do not put the standpipe gallons on the building pump, and still confirm the supply can deliver the minimum standpipe flow. Calculate only the demands that can run together (`hydraulic-method.md`).

Company hydraulics stay on the C-factors in `hydraulic-method.md`. A federal standpipe specification's C = 120 for steel is that specification. Do not use it to raise a dry or double-interlock calculation off C = 100.

## Pressure and the connection

NFPA 14-2024 §10.2.1 limits system pressure to 400 psi. A 350 psi ceiling is an older edition. A 300 psi figure is an author's design signal, not a code limit. Do not cite it. An express main allowed above 400 psi with listed materials, and a ban on hose valves in that pipe, is reported and not pinned (`[V]`).

NFPA 14-2024 §10.2.4.2 requires regulation where static pressure at a 2-1/2 in. connection exceeds 175 psi. A federal trigger at 125 psi, with the outlet set at 100 psi, is that specification (`pressure-regulating-devices.md`).

One committee account says that before the 2024 edition the fire-department connection did not have to supply the full system demand at the required pressure, and that the 2024 edition changed that. The account has no section number. Treat the change as `[V]`. Size the pump and the riser on the rules above. Raise the connection capacity with the engineer of record and the authority. Do not upsize a two-way connection from the account alone, and do not ignore the question.

## Test without impairing the sprinklers

A 5 year flow test of hose-connection regulating valves needs a place for the water. Floor drains sized for a sprinkler main drain are usually too small. On a combination riser, taking the standpipe out of service takes the sprinklers with it. A carrier preference is a drain riser of 4 in. or larger, sized for about 250 to 500 gpm, and an in-place test with a flow meter. That riser is not an NFPA 14 requirement. Draw it when regulating hose valves are in the design, because it cannot be added cheaply later. If valves are removed for a bench test, return each valve to its own outlet. They are not interchangeable across floors.

Acceptance flow on a federal specification is at least 250 gpm for 5 minutes per riser. Hydrostatic acceptance follows the adopted NFPA 14, in the same family as the 200 psi, 2 hour test in `acceptance-tests.md`.
