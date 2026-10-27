# Exhaust and ventilation ducts

FM DS 7-78, October 2021, is an industrial-exhaust sheet for process fumes and particulates. Most data-center ducts are outside it. Run the questions in order and stop at the first exit.

An occupancy sheet that speaks to the duct governs instead (§1.0). Data-hall smoke exhaust is FM DS 5-32: do not install an automatically operated smoke-exhaust system in a data-processing room, and where the code forces automatic operation, interlock it to the sprinkler alarm rather than to the detection system. Energy-storage exhaust is `ess-explosion-control.md`. Non-lithium battery dilution is `battery-room-hydrogen.md`. Transformer-room smoke exhaust is `transformer-siting.md`. A generator stack is a chimney (DS 1-13), not this sheet.

A commercial kitchen hood leaves this sheet except the quarterly inspection in §2.4.1.2. The design basis is NFPA 96 and the mechanical code. Those texts are not held here. Mark a kitchen claim `[V]`.

If the duct carries conditioned air, dilution air, or smoke rather than process fumes, it is not this sheet. Ordinary air-conditioning ductwork is FM DS 1-45, which is not held. Mark an insurer claim about ordinary hall ductwork `[V]` until that sheet is in hand. The code floor for duct interiors is NFPA 91 and the mechanical code, also not held here.

In-duct sprinklers apply when the duct is combustible or holds combustible deposits (§2.2.1.1), and then only when the section is at least 80 in² or 10 in in diameter and the deposits exceed 1/16 in, or the duct itself is combustible (§2.2.2.2). A clean metal duct carrying dilute hydrogen from a battery room fails that trigger. It does not get in-duct sprinklers.

Rules that still bind a campus duct:

- Avoid fire barriers. Where a crossing remains, provide a damper of the barrier's rating (§2.1.2.2). Where the code prohibits a damper in hazardous exhaust, reroute. The last resort is a shaft of the same rating extending 25 ft each way from the barrier, with firestops at each end and no inlets inside the shaft. That shaft is not acceptable at a loss-limiting wall (`mfl-walls.md`).
- Discharge more than 6 ft from combustible construction, including the wall the duct leaves, and more than 25 ft from unprotected openings in nearby noncombustible walls (§2.3.1.6).
- Extended-coverage sprinklers are not used to protect ducts (§2.2.2.8).

When the duct is genuinely in scope, in-duct protection is 20 gpm per sprinkler, eight sprinklers, 165 °F quick-response, K at least 5.6 (§2.2.2.5), placed within 3 ft of intakes, equipment, building entries, and turns of 90 degrees or more, then 12 ft on center horizontally and 24 ft on center vertically (§2.2.2.3). A combustible duct with no deposits may instead use 0.50 gpm/ft² over the projected area for 100 linear feet (§2.2.2.6). Hose is at least 250 gpm (§2.2.5.3). Each system gets its own control valve and waterflow alarm (§2.2.1.5).

The energy-storage duct path, once the room has one, is `ess-exhaust-duct-shaft-and-duct-sprinklers`. This note decides whether DS 7-78 applies at all.
