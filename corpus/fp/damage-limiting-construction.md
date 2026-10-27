# Damage-limiting construction

This is the envelope behind an FM energy-storage explosion-control requirement. Detection, exhaust rate, and the 10 percent lower-flammable-limit trip are `ess-explosion-control.md`. Sprinklers are `ess-room-sprinklers.md`. The sheet is FM DS 1-44, September 2000, interim October 2024. A registered structural or civil engineer designs it (§3.1.1). The fire-protection note records the targets. It does not size the wall.

FM DS 5-33 sends a lithium-ion energy-storage room through this sheet using propane as the representative gas (§2.3.3.3.1 and §2.3.4.5.1). Propane is Fuel Reactivity Group C (DS 1-44 Table 2.1.1). Group C allows a maximum surface-to-vent ratio of 12 and a vent panel of at most 4 lb/ft² (Table 2.1.2). Hydrogen is Group E. Table 2.1.2 gives no guidance for Group E. An energy-storage room stays on the propane path the occupancy sheet names.

Prefer a static release pressure of 20 psf. The sheet cap is 40 psf (§2.1.4.3.2). Resistant-wall pressure is at least the release pressure plus 50 psf, and the low-strength tables stop at 216 psf (§3.1.6). Surface area is 2(LW) + 2(LH) + 2(WH). Vent area is not subtracted from that surface. Doors in a venting wall do not count as vent area (§2.1.4.5.1).

Worked Group C anchors in Table 2.1.2.1-3: release pressure 20 psf and a ratio of 5 gives a resistant pressure of 100 psf; the same release pressure at a ratio of 12 gives 215 psf.

Location preference, best first: detached with the sheet's separation, detached closer than that, lean-to, then an in-building room on an exterior wall (Fig. 3.1.1). A lean-to resistant wall extends 10 ft beyond and above the hazard. An interior or basement room is the arrangement the sheet treats as undesirable. When a detached building is unavailable, the campus default is the exterior-wall cutoff room.

Fasteners are FM Approved explosion fasteners, factor of safety 1.0, within 10 percent of the release pressure, and not torqued (§2.1.4.1). Keep at least 50 ft clear opposite the vents where the site allows it (§3.1.3). Sprinkler risers sit behind resistant walls. Shutoffs are at least 50 ft away (§2.2).

NFPA 68 is a different method. DS 1-44 §4.2 says the NFPA 68 approach is more conservative and accounts for obstacles. Meeting this sheet does not by itself meet NFPA 68. The code-edition fence for explosion control is `ess-explosion-control.md` and `../fa/ess-room-detection.md`.

The method is `ess-isolation-venting-and-duration` for the prevention path. This note is the envelope that path still owes on an FM job.
