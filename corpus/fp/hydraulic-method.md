# Hydraulic method checks

Hazen-Williams loss uses the actual internal diameter to the 4.87 power. Representative Schedule 40 steel inside diameters: 1.610 in. at 1-1/2 in., 2.067 in. at 2 in., 3.068 in. at 3 in., and 4.026 in. at 4 in. Confirm the diameter on the pipe that will be installed. A data-hall minimum wall can be heavier than Schedule 10 and lighter than a remembered Schedule 40. Use the wall in `pipe-layout.md`.

Elevation change is 0.433 psi per foot of fresh water.

The NFPA 13 remote-area length is 1.2 times the square root of the area. Hose is added at the base of the riser, not through the branch lines.

Company reporting: C = 100 for wet, dry, and double-interlock. C = 120 appears only as a labelled comparison value, including the nitrogen column, and nitrogen is not a C credit. Show the friction understatement if someone asks for the credit (`nitrogen-compressor-and-c-factor.md`). Do not size on C = 120.

FM DS 2-0 Appendix A accepts Hazen-Williams at or below 30 ft/s and calls for Darcy-Weisbach above 30 ft/s, and for a non-water system. Water sprinklers stay on Hazen-Williams inside that speed.

Channel sprinklers are counted with the maximum allowable area spacing, not the as-built coverage. Remote flow is density times that maximum area (FM DS 2-0 §2.5.2.4.3(C)).

NFPA 20 limits the churn pressure rise to 1.40 times rated pressure and requires the 150 percent flow point at not less than 65 percent of rated pressure. Do not publish a rated pump flow and pressure until demand and friction are fixed. A single pump is not scheduled past 140 percent of rated flow on the FM DS 3-7 reading, and churn plus maximum static stays inside the 175 psi listing plateau (`sheet-precedence.md`).

A federal wet-pipe template floors backflow loss at 12 psi for a reduced-pressure assembly and 8 psi for a double check, or the manufacturer's loss if greater, and it looks for at least 20 psi residual at the backflow inlet or the pump suction. Those floors are that template. On a commercial job use the manufacturer's loss and the adopted code. Do not import a template density. The specification states density in gpm/ft² and area in square feet. A promise to comply with a guide is not a design.

Calculate only the demands that can run together. A screening example that fails one 30,000 ft² preaction zone on a 30 second fill, and passes the same gallons split into smaller zones, is an illustration. Zone by the whole zone's volume, not by the remote area alone (`pipe-volume.md` and `water-delivery-screen.md`).

Start pressure at the head is in `sprinkler-temperature-and-k.md`.
