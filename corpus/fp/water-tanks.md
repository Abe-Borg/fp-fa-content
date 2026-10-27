# Water tanks for fire protection

Pick the tank from the reliability order in `water-supply-reliability.md`, then size it for the demand. FM DS 3-2 (October 2015 / interim July 2022) is the tank sheet. It does not set the occupancy demand. A closed-top suction tank and a fire pump are the usual stored supply for a single-story hall. A gravity tank needs height the hall does not have. A pressure tank is a small primary or a bridge until the pumps are up: the sheet's practice is about two-thirds water, with air falling from about 75 psi to about 15 psi as the water leaves. NFPA 22-2023 Chapter 7 does not state those two figures. Capacity is what the authority approves, and the air has to discharge the water at the required residual. Do not cite the two-thirds or the 75 psi as NFPA 22.

## Duration volume

Size a suction or gravity tank for sprinkler demand plus hose for the design duration (§2.1). Usable volume runs from the overflow down to the anti-vortex plate, not to the steel bottom (NFPA 22-2023 §4.1.4). The plate is at least twice the outlet diameter and at least 6 in. or half a diameter off the bottom (NFPA 22-2023 §14.2.13; DS 3-2 §3.6.5). On a vertical turbine, also subtract the minimum submergence (`fire-pump-installation.md`). Refill within 8 hours (NFPA 22-2023 §4.2.1.4; DS 3-2 §3.6.6 for a gravity fill pump).

A break tank is not that duration. Use one only when the authority prohibits a direct public connection, and only when the public main can still supply 150 percent of rated pump flow (§2.2.2.1). One break tank per pump, for fire protection only. The working band is 150 percent of rated flow for 15 minutes, measured from 2 ft above the anti-vortex plate up to the auto-fill start (§2.2.2.2). At least two automatic fills and one manual fill, each at least 150 percent of rated flow, opening 6 in. below full. Low-level alarm at 9 in. below full. Fill velocity at most 20 ft/s, and the fill outlet at least 15 ft from the suction, preferably on the opposite side. A break tank is less reliable than a full-duration suction tank because the fill can fail and the water aerates (§3.2). If the fill main approaches the cost of a suction tank, build the suction tank.

Do not share the tank with process water unless a dedicated fire-protection volume is trapped and the process pipe is separate. Putting a former public-suction pump onto a new break tank deletes the public residual. Recalculate.

## Listing, earthquake, freeze

Design to FM Approvals Standard 4020, not to an AWWA tank alone. Submit to the current standard. The sheet's appendix is a checklist, not the approval. Minimum welded shell and bottom on that checklist is 0.25 in. Roof vent area is at least 1.5 times the larger of the fill and the suction. Wind design uses at least 90 mph and exposure C. Exposure B is not allowed.

In an FM 50- to 500-year zone, provide freeboard of at least 0.5 × diameter × the convective slosh, or accept the impulsive-mass penalty. Importance is 1.25. Anchored tanks use embedded bolts and chairs. Straps and hooked bolts are rejected. Pipe flexibility is `post-earthquake-supply.md`.

Freeze protection uses the FM 100-year map, not a guessed zone (`cold-climate-freeze.md`). Hold the coldest water between 42 °F and 50 °F. Alarm at 40 °F. Those two temperatures match NFPA 22-2018 and 2023 §16.1.2 and §16.1.2.2. Heat a suction tank when the zone is −5 °F or colder (§2.2.6.5). Size heaters from the map zone through Tables 6 through 9, then the transfer rate, then the surface. Do not interpolate across zones. Prefer a heater dedicated to the tank when plant steam is banked at night. An air bubbler is not a method for a closed fire-protection tank. Do not draw a tank that has an unbroken ice sheet thicker than 2 in. Interior inspection interval on the sheet is 5 years (§2.3.9).

A high-rise refill rule from one city, including a dual fill at 110 percent of pump capacity, does not size a tank for a one-story hall. Do not import it.

Pump suction friction from the tank is at most 6 psi at 150 percent of rated flow (`fire-pump-installation.md`). Place a second yard supply so the two sources are not impaired together (§2.2.1.5).
