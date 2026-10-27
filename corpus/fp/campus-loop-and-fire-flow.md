# Campus loop and needed fire flow

Size the private fire main after density-area has a company-scoped wet, dry, or double-interlock demand and the hydrant curve has a supply verdict. If either is missing, label the substitute ASSUMED and say why.

The loop carries the full demand with one leg out of service. Pick diameter from the actual inside diameter, not a nominal size. Place sectional valves so one impairment does not take the campus out. NFPA 24 is the code floor for private mains. The pack's delta baseline is NFPA 24-2025. An unamended 2024 I-Code adoption typically enforces NFPA 24-2022. Pipe, valves, hydrants, and the section cites are `private-fire-mains.md`. Hydraulic calculations are Chapter 11 and main size is §5.2. Underground restraint and flushing are Chapter 10. An older map that put sizing in Chapter 13 is not the map to use.

Hazen-Williams friction on the leg uses the same relation as the rest of the pack: pressure loss per foot is 4.52 × Q^1.85 / (C^1.85 × d^4.87), with Q in gpm and d in inches. `calcs/fp` op `hazen_williams` evaluates it. Campus-loop design locks C at 100 for every underground material. The material-and-age C table is comparison-only on this note. Do not size the leg on a higher tabulated C. The hydrant-supply method uses that material-and-age lookup for a different purpose: a one-segment relocation of the supply test when the pipe age is known (`pump-and-supply.md`). That lookup does not set the loop's design C.

## Which fire-flow method binds

Needed fire flow is a method election, not a single published gallon figure.

- ISO's sprinklered method, when the purveyor or the authority uses it.
- IFC Appendix B, only where that appendix is adopted. Do not apply it because the model code prints it.
- UFC 3-600-01 §9-2. Appendix C of that UFC is not in the codebook. A Department of Defense flow that depends on Appendix C is ASSUMED and `[V]`.
- The purveyor's maximum available flow, when that is the contract limit.

Unsprinklered ISO results are a different question from the sprinkler demand. Do not add them on top of `qd` unless the adopted method says to. An occupancy that is not listed by name in the ISO tables is an analogy. Say so on the memo.

Reject research curves that were not built for a sprinklered data hall (the pack cites the FEMA/USFA 2009 discussion of older laboratory methods for that rejection). The ISO arithmetic, the area cap, and those rejected formulas are `needed-fire-flow.md`. State the method, the geometry credit, and who adopted it. The loop, the tank, and the pump envelope may all be governed by that memo. They are not governed by a guessed gpm.
