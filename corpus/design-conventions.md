# Design conventions

These are the defaults for every note in this folder. A project document overrides them when it is stricter. They are not a code, an insurer sheet, or an owner standard.

## Three layers

Design each parameter to the most stringent of the code floor, the insurer sheet, and the owner standard. The code floor is the adopted IBC or IFC and the NFPA edition that instrument references. The latest NFPA edition is the delta reference. It is not the enforced minimum until the authority adopts it. Pins are in `fp/edition-pins.md`.

Cite the section and the edition together. A nearby section number in another edition is often a different rule. The dry-pipe area increase and the ceiling-height increase are the example in `fp/edition-pins.md`.

Report the delta against the code floor when the insurer or the owner governs. Do not assert a habit as if it were the code.

## Company systems

The basis of design is wet pipe, dry pipe, or double-interlock preaction, plus the pumps, the nitrogen or air supply, and the fire-alarm work those systems need. Foam, clean agent, water mist, and a building deluge system are out of scope. Outdoor oil-filled transformer apparatus water spray is the exception in `scope-lock.md`. It does not elect the building sprinkler family. Single-interlock and non-interlock preaction are comparison-only. The fence is `scope-lock.md`. The election is `fp/system-election.md`.

On an FM hall, company practice keeps double-interlock and flags the sheet that ranks it last. The detection leg is one alarm-level pre-alarm, not a cross-zone, and not an early-warning alert. Those two flags are `fa/di-releasing.md`.

## Numbers

A numeric screen sits next to its edition and section. Where the licensed text was not confirmed, the note says `[V]` and does not invent a section. A value the tools did not return, and that the designer is judging, is not a cited code value. Verify it with the engineer of record.

Do not copy another hall's gallons, rated pump pressure, zone count, panel program, or pressure setpoints. Do not print a pump rating until demand and friction are fixed.

Dry and double-interlock hydraulics use C = 100. Nitrogen is for corrosion and for the pendent-head permission. It is not a C-factor credit (`fp/nitrogen-compressor-and-c-factor.md`).

Calculations run in `calcs/`. Show the inputs. A delivery time from the screen is not a listed water-delivery calculation (`fp/water-delivery-screen.md`).

Low-air and high-air separation of at least 5 psi is design practice when the adopted NFPA 13 paragraphs support it (`fp/air-maintenance.md`). The valve's published sheet still governs. If the sheet cannot meet the separation, the election fails.

## How a note is written

One topic per file. Short sentences. Name the controlling layer. A jurisdiction outside the stated NFPA, IBC, and IFC basis is not a place to port these pins (`fp/ufc-outside-pin.md`). Local amendments change hydrant spacing, flow-test age, and safety factors. Confirm them. Do not paste another city's checklist.
