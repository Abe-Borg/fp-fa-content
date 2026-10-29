# Company scope lock

Controlling basis of design in this pack is one of three water-sprinkler families, plus one apparatus exception:

1. Wet pipe.
2. Dry pipe.
3. Double-interlock preaction.
4. Outdoor oil-filled transformer apparatus water spray (NFPA 15-style). Size it in `power-block-transformer-water-spray`. It does not elect the building sprinkler family.

The sprinkler election is made in `suppression-technology-selection` and consumed by the other methods. A missing election is labeled ASSUMED. It is not a silent swap to another family.

## Out of scope

Foam, clean agent, water mist, and a building deluge system are out of scope. Record the request and stop. Do not size them here. Apparatus water spray for an outdoor oil-filled transformer is the exception above. It is not water mist and it is not a building deluge system.

Single-interlock and non-interlock preaction are comparison-only. If either is offered as the basis of design, record it, stop, and return an RFI. Do not substitute double-interlock.

A jurisdiction outside the stated NFPA, IBC, and IFC basis, and outside a country-gated Canada job, is out of scope. On a Canada job the code floor comes from the adopted NBC family and the edition pins in `most-stringent-basis-matrix`. Do not port US pins into that row or Canada pins into a US row. CAN/ULC-S524, S536, S537, S1001, and CEC Section 32 stay NEEDS HOLD. Do not invent those clause texts or battery hours. Insurer and owner layers still apply as written.

## How a number is carried

Decide each parameter by the most stringent of the code floor, the insurer sheet, and the owner standard. Cite the section and the edition. A value the tools did not return, and that the designer is judging, is not a cited code value. Verify judgment calls with the engineer of record.

Do not copy another hall's gallons, rated pump pressure, zone count, or panel program onto a new job.
