# Fire-pump installation

Rated flow and pressure come from the demand and the supply curve. Do not publish them while either is open (`pump-and-supply.md`). This note is how many pumps, how they are installed, and which layer shrinks the usable curve. Controller configuration is `fire-pump-controller.md`. Reliability of the source is `water-supply-reliability.md`.

## How many, and how much of the curve

FM DS 3-7 (April 2012 / interim October 2021) sets the architecture and disclaims the size (§1.0). On a pump-and-tank supply the standard arrangements in §2.4.6.2 are one pump at 100 percent of maximum demand, or three pumps at 50 percent each. For a nonstorage occupancy the sheet also allows two pumps of different driver types, each at least 75 percent. If none of those can make the demand, install N pumps that meet it plus one spare, preferably half electric and half diesel (§2.4.6.3). On an FM job that spare is the insurer's arrangement. An all-electric plant is a written variance, not a silent choice.

The usable fraction of rated flow is tighter than the 150 percent acceptance point (§2.4.6.4 and §2.4.6.5):

| Arrangement | System demand plus hose, as a fraction of rated flow |
| --- | --- |
| One centrifugal pump at 100 percent of demand | 140 percent |
| Multiple centrifugal pumps | 110 percent |

A federal criterion also caps demand at 140 percent of rated, which matches the single-pump row. A carrier sheet caps demand at 120 percent. The FM multiple-pump row is the strictest of the three. The moment the design uses two or three pumps, each pump is rated for its share divided by 1.10, not by 1.50. Do that before the room is drawn. The pump must still make at least 65 percent of rated pressure at 150 percent of rated flow (NFPA 20-2019 through 2025 §6.2.1; the same limit is in DS 3-7).

Series pumps are not used. NFPA 20's high-rise chapter has allowed up to three in one room. FM DS 3-7 §2.2.2.2 does not. The sheet's arithmetic is about 3 percent failure to start per electric unit, so three in series fall from about 97 percent to about 91 percent (§3.1.2). Parallel pumps start in sequence, and one failure must not block the others (§2.4.8.1). Do not import the rest of the high-rise chapter into a hall.

## Suction and the room

Suction pressure stays positive over the whole flow range (DS 3-7 §2.3.2.1). NFPA 20-2019 through 2025 §4.16.3.1 sizes the suction to at least 0 psi at 150 percent flow. Section 4.16.3.2 allows −3 psi only for a qualifying suction tank. Prefer 0 psi. A vertical turbine is the pump that draws from below. Do not use a split-case, end-suction, or in-line pump on a static lift (DS 3-7 §2.4.1.1).

From a suction tank, friction loss to the pump inlet is at most 6 psi at 150 percent flow (§2.3.2.2). Suction velocity is at most 15 ft/s at 150 percent (§2.3.2.5). On a common suction, assume every pump is flowing. The sheet's examples at 15 ft/s are 2,340 gpm in 8 in., 3,660 gpm in 10 in., and 5,280 gpm in 12 in. No butterfly valve in the suction piping (DS 3-7 §3.1.3.1). The gate-only zone within 50 ft is `control-valves.md`. Keep an elbow or tee whose plane is parallel to a horizontal split case at least 10 pipe diameters away (§2.3.2.4).

Churn plus maximum static suction stays inside the component rating (NFPA 20 §4.7.7.1). A relief valve is for the case where that sum exceeds the rating, not for a design that undersizes the pipe (DS 3-7 §2.3.4.2 and §3.1.10). Install it between the pump and the discharge check, discharge visible, never piped back to the suction, with no shutoff in the relief line. For a diesel, take pressure to 121 percent of net rated shutoff because the governor may allow 110 percent speed and pressure follows the square (§2.3.4). Variable-speed relief is `variable-speed-pump.md`.

Provide a way to test at 150 percent of rated flow, and size the test outlets for 175 percent (DS 3-7 §2.3.3.4). Do not install a flow meter in a closed loop back to the suction (§2.3.3.6). A closed loop cannot see a nearly shut suction valve. A carrier sheet rejects the same loop because it never evaluates the suction supply. Discharge the test to atmosphere, with drainage for 150 percent for the whole test. Decide that at design. Where the pump feeds a dry or double-interlock system, start it from the releasing panel when the valve trips, ahead of the pressure switch (§3.1.12). The reason on the sheet is water hammer.

The preferred house is a detached noncombustible building at least 50 ft from the protected buildings (§2.2.1.2). A room, when a detached house is not feasible, is 2 hour separation, reducible to 1 hour when the room and the adjacent spaces are sprinklered, with a door on an exterior wall, and never inside an unprotected building. IBC 2024 §913.2.1 is the code-floor separation, including its 1 hour exception in a sprinklered building that is not a high-rise. Keep the insurer's ladder when it is stricter, and name the delta. The floor is at or above grade and above the 500-year flood plus 1 to 2 in. (§2.2.1.8). Heat is above 40 °F (§2.2.1.6). A diesel room on the FM freeze sheet is above 70 °F (`cold-climate-freeze.md`). Sprinklers over an engine-driven pump (§2.2.1.5). No storage. Drainage pitched away from the controller, sized for packing leakage and the flow test. Wiring that leaves the room may be able to start the pump. It must not be able to prevent a start (§2.2.1.3).

Limited-service controllers are not used on a pump that supplies the building sprinklers (DS 3-7 §2.4.14).

## Driver

Electric power is unreliable when outages last longer than 8 hours three or more times in a year, or when short outages are frequent (§2.4.12.2). A federal definition is different: forced downtime at most 8 hours in one incident and 24 hours over 3 years. Run both against the utility history. A reliable feed is not shared with ordinary plant loads and is not disconnected by plant staff or the fire department during a fire (§3.1.13.1).

Conductors are at least 125 percent of motor rated current (§2.4.12.8). Voltage drop is 15 percent at the controller during start and 5 percent at the motor at 115 percent of full-load current (§2.4.12.9). The circuit rules are `fire-pump-power-circuit.md`. No ground-fault protection on the pump circuit (§2.4.12.11). A transfer switch is at least 115 percent of full-load current and able to carry locked rotor (§2.4.15). An alternate-source overcurrent device carries locked rotor plus the other pump-room loads without a time limit.

Diesel fuel on FM DS 3-7 §2.4.21.6 is at least 8 hours of run time plus 5 percent expansion plus 5 percent sump, in a double-wall steel tank or a concrete vault, inside the pump room, with its own tank and lines per engine (§2.4.21.8). Do not specify biodiesel (§2.4.21.14). NFPA 20-2022 and 2025 §11.4.1.3.1 size the tank for 12 hours at the published consumption, plus 5 percent expansion and 5 percent sump. The 1 gal per horsepower rule in §11.4.1.3.1.1 applies only when consumption is unknown. The 2019 edition uses 1 gal per horsepower plus the two 5 percent allowances as the rule. Take the larger of the adopted NFPA 20 tank and the FM 8 hour tank. NFPA 37-2024 §6.3.2.2 limits a tank to 660 gallons unless it is in a room by itself. A qualifying engine room may hold a larger tank (§6.3.2.2.1). Containment is at least the largest tank (§6.3.2.4).

Each diesel battery set carries a 3 minute cranking cycle at 40 °F, and the sheet asks for 90 hours of starting ability after a power failure (§2.4.21). Ventilation for a heat-exchanger engine is 0.75 in² per horsepower, with radiator supply louvers at least twice the outlet area and discharge louvers at least 1.5 times, interlocked to engine run with no thermostat (§2.4.17). Cooling water comes off the pump discharge ahead of the check valve. The FM temperature derate is a single 3 percent step at 105 °F, with a 120 °F maximum ambient. The NFPA per-degree method is `pump-and-supply.md`. Use the larger derate. Verify the step against the sheet in hand.

Do not auto-start a diesel on loss of normal power unless a trained response is immediate (§2.4.20.1). On an unattended campus that condition fails. A federal criterion bars that auto-start outright. Hold the room and the coolant with heaters on generator-backed power. The standby generator that feeds an electric pump is the opposite rule: it does start automatically. Two engines.

## Acceptance and duration

Field acceptance on the FM appendix is churn, 50, 75, 100, 125, and 150 percent, instruments calibrated within 12 months, then at least 1 hour of running. Diesel holds 150 percent until the temperature is stable and then runs 15 minutes more. Net head for a horizontal pump is discharge minus suction. For a vertical turbine it is discharge plus the elevation from the water surface to the discharge centerline, at 0.433 psi per foot. Correct speed with the affinity laws before you compare the curve. Starts are six manual and six automatic (§14.2.7.2). A federal specification's ten and ten is that specification (`acceptance-tests.md`). Above 200 hp, no more than two starts in 10 to 12 hours.

Do not count water below a vertical turbine's minimum submergence as duration (DS 3-7 §2.4.2.3). Submergence has to hold at the lowest water level (§2.4.2.2). A mass-elastic analysis with no critical speed within 25 percent of operating speed is a diesel vertical-turbine submittal (§2.4.2.5).

Jockey setpoints are `jockey-pump.md`. Do not copy a catalog envelope in place of the certified curve.
