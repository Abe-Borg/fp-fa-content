# Seismic bracing for sprinkler pipe

Scope is wet, dry, or double-interlock sprinkler piping. Gas and fuel piping restraint is a different sheet. Structural attachment design belongs to the structural engineer. This note prints the delta against NFPA 13-2025 Chapter 18.

## Spacing ceilings (not the design spacing)

- Lateral braces at most 40 ft on center (NFPA 13-2025 §18.5.5.2.2). Forty feet is the ceiling. The load tables can force a shorter spacing. A calculated 30 ft or 35 ft on one example is that example's result, not a code maximum.
- Longitudinal braces on feed and cross mains at most 80 ft on center (§18.5.6.1). Branch lines are also 80 ft unless §18.5.9.6 is met (§18.5.6.2).
- The last brace is at most 40 ft from the end of the pipe or a change of direction (§18.5.6.4).

## Load

NFPA path held in the pack: Fpw = Cp × Wp, with Cp = 0.754 × S_DS and Wp = 1.15 × water-filled weight (NFPA 13-2025 §18.5.9.2 and §18.5.9.3). The published equation text in the pull was flattened. Confirm Cp against the page (`[V]`). If S_DS is unknown, Cp = 0.5 (§18.5.9.5).

FM DS 2-8 uses water-filled weight tributary to the brace with no 1.15 factor. Take the larger of the NFPA load and the FM load. They differ by design. That is not a conflict to average.

Height reductions (×0.875 and ×0.75 in §18.5.9.3.3 and §18.5.9.3.4) are not applied by default. Using them is a judgment. Verify with the engineer of record.

`calcs/fp` ops `cp_from_sds`, `brace_spacing_max`, and `brace_load` screen the spacing. For an FM horizontal listing that is already a horizontal allowable, pass the flag that keeps the FM factor from being applied twice. The NFPA angle divisor stays on axial listings.

## Riser

FM DS 2-8 (October 2017 / interim April 2025): a 4-way brace within 2 ft of the top of each riser (§2.2.1.1.2.1); avoid one brace serving more than two risers; intermediate 4-way braces at most 25 ft (§2.2.1.1.2.3); in a multistory building, within 2 ft of each floor (§2.2.1.1.2.2). The NFPA 13-2025 riser section number is not pulled. That cite stays `[V]`.
