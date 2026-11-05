# Needed fire flow

Which instrument is asking is `campus-loop-and-fire-flow.md`. This note is the arithmetic behind that election, and the moves that do not change the answer. There is no national fire-flow number.

## Sprinklered buildings

ISO's Guide for Determination of Needed Fire Flow, edition 06-2014, page 2: for a commercial building sprinklered to NFPA 13, the needed fire flow is the demand at the base of the riser plus the inside and outside hose streams. The construction formula does not apply. The number handed to the purveyor is the hydraulic demand. Raising density for an insurer or an owner raises that number. Say so before the service is sized.

The largest demand on the site governs. A storage or staging area can exceed the hall (`storage-design.md`).

Where IFC Appendix B is adopted, a sprinkler reduction can still sit on a minimum flow and duration. A secondary paper reports 1,500 gpm for 2 hours from the 2006 and 2009 editions. That floor can exceed a wet hall's own demand, so the code floor would govern. Confirm it in the adopted IFC (`[V]`). Do not apply Appendix B because the model code prints it.

## Unsprinklered ISO, as a bound only

NFF = C × O × [1 + (X + P)], with C = 18 F √A, rounded. For construction classes 3 through 6, and for any one-story building, C is capped at 6,000 gpm (ISO page 10). The cap is already binding near 166,000 ft² for classes 3 and 4 (F = 0.8) and near 296,000 ft² for classes 5 and 6 (F = 0.6). A larger footprint does not raise C.

Exposure and passageway charges are zero for a sprinklered building, for classes 5 and 6, and for classes 3 and 4 with C-1 or C-2 contents (page 16). Occupancy factor O is the remaining lever: 0.75, 0.85, 1.00, 1.15, and 1.25 for C-1 through C-5. At the cap and O = 0.85 the result is 5,000 gpm, at any larger area. There is no data-hall row. State the analogy. Do not treat this unsprinklered bound as the sprinkler demand, and do not add it on top of the hydraulic demand.

A fire wall that cuts area does nothing to ISO needed fire flow once C is capped. The same wall can still matter under an adopted IFC Appendix B table. Ask which method is in force before anyone buys the wall for fire flow (`[V]` on the current appendix).

ISO's 48 month look-back for a main drain, a dry trip, and a pump test is a rating window. It is not an NFPA 25 frequency. The guide in hand states no duration for a commercial needed fire flow. Do not size a tank on a remembered 2 to 4 hours.

## Methods to reject

Three older formulas ignore construction type and ignore sprinklers, and they fail at hall scale (the comparison is a 2009 secondary paper):

- Volume divided by 100 produces on the order of 100,000 gpm for a 250,000 ft² hall that is 40 ft high.
- Area divided by 3 produces on the order of 80,000 gpm at full involvement. That expression is a fireground estimate.
- The quadratic nonresidential formula peaks near 16,000 ft² and is negative past about 32,000 ft².

Do not use them for a sprinklered hall.

## Hydrant credit

A rating method credits hydrants only inside the hose-lay distance, not the straight-line distance. The 2009 secondary paper reports 1,000 gpm within 300 ft or at a pumper outlet, and zero beyond 1,000 ft. The 2014 guide in hand does not contain that table. Confirm it in the current rating schedule before you count hydrants (`[V]`). Available flow for this purpose is computed at 20 psi residual. Local hydrant spacing is the adopted fire code. Do not paste another city's spacing onto the plans.

## Canada capacity and the connection

On a Canada job, NBC 2023 AE Division B 3.2.5.7.(4) exempts an NFPA 13 sprinklered building from the capacity in sentence (1). That exemption does not omit the fire department connection. NBC 2023 AE 3.2.5.15.(3) places that connection no closer than 3 m and no farther than 15 m from the principal entrance. The sentence is absent from NBC 2025 3.2.5.15 and from BCBC 2024. Do not carry the band onto those codes. Do not promote an assumed municipal curve, including a 750 gpm at 65 psi teaching point, as the final supply. Do not invent CAN/ULC-S524 or CAN/ULC-S561 hours. Hand siting to the Class I standpipe note.
