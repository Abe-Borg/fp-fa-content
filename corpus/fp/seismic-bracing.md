# Seismic bracing for sprinkler pipe

Scope is wet, dry, or double-interlock sprinkler piping. Gas and fuel piping restraint is a different sheet. Structural attachment design belongs to the structural engineer. This note prints the delta against NFPA 13-2025 Chapter 18.

## Spacing ceilings (not the design spacing)

- Lateral braces at most 40 ft on center (NFPA 13-2025 §18.5.5.2.2). Forty feet is the ceiling. The load tables can force a shorter spacing. A calculated 30 ft or 35 ft on one example is that example's result, not a code maximum.
- Longitudinal braces on feed and cross mains at most 80 ft on center (§18.5.6.1). Branch lines are also 80 ft unless §18.5.9.6 is met (§18.5.6.2).
- The last brace is at most 40 ft from the end of the pipe or a change of direction (§18.5.6.4).

## Load

NFPA path held in the pack: Fpw = Cp × Wp, with Cp = 0.754 × S_DS and Wp = 1.15 × water-filled weight (NFPA 13-2025 §18.5.9.2 and §18.5.9.3). The published equation text in the pull was flattened. Confirm Cp against the page (`[V]`). If S_DS is unknown, Cp = 0.5 (NFPA 13-2025 §18.5.9.5). FM DS 2-8 (October 2017 / interim April 2025) §2.3.1.1 does not use 0.5 for a missing Cp. It uses 0.9, 0.65, and 0.4 for the 50-year, 100-year, and 250-to-500-year zones. FM DS 1-2 (April 2018 / interim January 2024) §2.2.2.1.2, when site S_DS is unavailable, uses 1.3 g, 0.9 g, and 0.55 g for those same zones, which the sheet converts to sprinkler G of 1.0, 0.7, and 0.4. On an FM job print the NFPA Cp and the FM Cp and keep the load that governs. Do not average them.

FM DS 2-8 uses water-filled weight tributary to the brace with no 1.15 factor. Take the larger of the NFPA load and the FM load. They differ by design. That is not a conflict to average.

Height reductions (×0.875 and ×0.75 in §18.5.9.3.3 and §18.5.9.3.4) are not applied by default. Using them is a judgment. Verify with the engineer of record.

`calcs/fp` ops `cp_from_sds`, `brace_spacing_max`, and `brace_load` screen the spacing. For an FM horizontal listing that is already a horizontal allowable, pass the flag that keeps the FM factor from being applied twice. The NFPA angle divisor stays on axial listings.

FM DS 2-8 also limits brace angle to at least 30 degrees from vertical, preferably at least 45 degrees, and limits the difference between two diagonals to 15 degrees (§2.2.1.3.5.2). Slenderness is 200 when the brace takes compression and 300 when it is tension only. Cable bracing does not qualify (§2.2.1.3.5). Powder-driven fasteners and C-clamps, even with straps, are not sway-brace attachments (§2.2.1.3.6). The end lateral brace is within 6 ft of the end of a main (§2.2.1.1.4.2). Sleeves give 2 in. of extra clearance through 3-1/2 in. pipe and 4 in. extra at 4 in. and larger, and 2 in. of end and parallel clearance (§2.2.1.5). Copper lateral and four-way spacing is 25 ft, and aboveground CPVC is not used in earthquake zones on this sheet (§2.2.1.9). Suspended-ceiling force is 0.503 times S_DS times weight at importance 1.0, and ceilings over 1,000 ft² are braced at 12 ft on center (§3.1.11). Drops between independent structures are assumed to move 1.5 percent of height each, and they may move in opposite directions (§2.2.1.4.6.5). A worked 1-1/4 in. Schedule 40 brace at a slenderness of 200 is 9 ft long on Table 3.1.8. Confirm the allowable on the table before using a remembered pound figure. Fuel-gas bracing uses a different sheet (`fuel-seismic-shutoff.md`).

## Riser

FM DS 2-8 (October 2017 / interim April 2025): a 4-way brace within 2 ft of the top of each riser (§2.2.1.1.2.1); avoid one brace serving more than two risers; intermediate 4-way braces at most 25 ft (§2.2.1.1.2.3); in a multistory building, within 2 ft of each floor (§2.2.1.1.2.2). The NFPA 13-2025 riser section number is not pulled. That cite stays `[V]`.
