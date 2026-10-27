# Medium-voltage switchgear rooms

The sheet applies above 1,000 V AC (FM DS 5-19 §1.0, October 2020, interim January 2024). A 480 V switchboard room does not take §2.2 as its primary. Outdoor oil-filled transformer spray is `transformer-siting.md` and `power-block-transformer-water-spray`. Information-technology isolation is `hall-power-isolation.md`. Those are different objects.

Standard metal-clad gear with vacuum, air, or SF₆ interrupters, in a noncombustible room with no other combustibles, is a room problem. Do not deluge the lineup (§2.2.1). Minimum-oil breakers are treated as non-oil when the room is noncombustible and free of other combustibles.

The room package is noncombustible construction, photoelectric or combination smoke detection to a constantly attended location, a response that can de-energize or diagnose, room sprinklers on wet pipe, dry pipe, or double-interlock preaction, no storage, slight positive-pressure filtered air, and a pre-incident plan that brings electrical staff and the fire service together (§2.2.4, §2.2.5, and §2.1.5). Strongly prefer the upstream high-side breaker outside the room (§2.2.5). Smoke detection does not change the need for sprinklers (§2.2.4). Spacing is DS 5-48 (`fm-detection-install.md`). The sheet prints no density for this room. Use the occupancy stack. Company basis is wet, dry, or double-interlock.

Grouped combustible cable is the significant combustible when DS 5-31 applies (`cable-trays.md`). A cable-only area there is 0.2 gpm/ft² over 3,000 ft² (§2.2.2 of this sheet, pointing at DS 5-31 §2.3.2.2.B).

Oil-filled bulk-oil gear, or gear exposed to other combustibles, is the §2.2.3 fork: sprinklers, or a listed gaseous system, or listed water mist. Gaseous agent and water mist are out of scope. Prefer non-oil gear and the room water path. Vent oil vapors outdoors.

Arc-resistant gear, redundancy, or physical separation at the tie is the electrical preference. Otherwise the sheet wants at least five horizontal sections between primary-selective breakers that feed the same critical load (§2.3.5). Arc vents must not discharge onto combustibles, and the room itself is vented for the pressure (§2.1.5.2).

A forced-air bus duct that draws from a fire-risk area, such as an outdoor oil-transformer yard, interlocks the fan with the bus breaker and with remote fire detection (§2.2.3.2).

Overhead-fed gear still needs surge protection. That package is `lightning-and-surge.md`. It does not replace this room.

The method is `mv-switchgear-room-package`.
