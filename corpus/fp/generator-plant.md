# Standby generator plant and fuel

Detection in the engine room, and the fuel-tank permission that can require it, are `../fa/generator-room.md`. Combustion-air and radiator openings are `combustion-air-and-hall-free-area`. Off-load yards are `diesel-fuel-handling.md`. Ceiling density and drainage for the liquid are `ignitable-liquid-sprinklers.md`. This note is the arrangement of the plant and which sheet owns the density.

FM DS 5-23 (July 2020, interim January 2022) is the arrangement sheet. It does not print a sprinkler density. Section 2.5.1 points at FM DS 7-32 Table 2.4.3. Diesel with a closed-cup flash point under 200 °F is FM Group A, not very-high flash point (`ignitable-liquid-sprinklers.md`, DS 7-32A, April 2026). The control package on that table is 0.30 gpm/ft² over 4,000 ft² or 6,000 ft², with drainage. NFPA 37-2024 §11.4.5.1 states 0.3 gpm/ft² over 2,500 ft². Report both. The more stringent area and hose that actually apply govern. NFPA 13 occupancy densities are not the generator-room design.

A double-wall day tank or bulk tank is not a substitute for containment and emergency drainage (DS 5-23 §2.2.2.1). Leak detection is still required at a diked day tank (§2.5.2). Fuel headers are not used as extra storage (§2.2.11). Each generator on a bulk system gets its own day tank. Combustion-air louvers interlock with generator operation (§2.4.1.2). Closing those louvers, or closing a fuel valve, on engine-room detection fights the need for combustion air. The detection conflict is `../fa/generator-room.md`. Verify with the engineer of record.

NFPA 110 vocabulary is three independent axes. Class is hours at rated load without refueling. Type is seconds to start and transfer. Level is whether failure threatens life. A campus continuity target usually drives Class. Level 1 is the life-safety axis. It is not a synonym for the most important generator. Emergency power within 10 seconds and standby power within 60 seconds, and the fire-alarm generator credit, are `../fa/secondary-power.md`.

A Defense criterion of 7 days of fuel, or 14 days for some secure missions, is mission policy. A commercial duration comes from the owner, often on the order of 24 to 72 hours, and from the tank's fire design. Do not copy the Defense duration onto a commercial job. Biodiesel and liquefied petroleum gas prohibitions in that Defense document are Defense rules.

An electric fire pump's generator starts automatically. A diesel fire pump does not auto-start on loss of normal power unless a trained response is immediate (`fire-pump-installation.md`). They are two engines. Minimum loading of the generator, so it does not wet-stack, is the figure in `fire-pump-power-circuit.md`. Size the set from the fire-pump starting load as well as from the building load.

Gas-turbine and hydrogen-cooled generator protection is a different sheet (FM DS 7-79). Do not apply its height-based densities to a diesel standby room.

The room water path is wet, dry, or double-interlock. Foam and water mist are out of scope. The method for openings is `combustion-air-and-hall-free-area`. The method for the liquid density is `occupancy-hazard-fork`.
