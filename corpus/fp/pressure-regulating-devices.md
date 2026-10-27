# Pressure-regulating devices

Design the system so a sprinkler pressure-reducing valve is not required. The common listing plateau is 175 psi (`control-valves.md`). NFPA 13-2022 and 2025 §7.1.2 rate aboveground components for the maximum working pressure, and not less than 175 psi. Section 16.9.7.1 calls for a listed reducing valve only where normal pressure can exceed 175 psi and the components are not listed for that pressure.

Raising the component rating, adding a zone, or limiting pump speed are the earlier moves. Speed control is `variable-speed-pump.md`. A reducing valve is the last move.

## FM fences

FM DS 3-11 (October 2021) is the sheet when a reducing valve is actually in the design:

- Do not use one on a sprinkler system whose static inlet is 175 psi or less (§2.2.2.2).
- Do not put a pilot-operated valve downstream of a dry-pipe or preaction system (§2.2.2.3). That arrangement fights the dry side.
- Do not install automatic breach-containment valves, and remove one if it is already there (§2.2.3). The sheet's loss sample is long undetected leaks, which a closing device does not catch, plus the impairment of closing a sprinkler main.

Pump-house relief valves and suction regulation are FM DS 3-7, not DS 3-11. On an FM job there is no pressure-reducing valve on the fire-pump suction or discharge (§2.3.5.1). A low-suction condition is an alarm, not a throttle. A relief valve does not trim the supply curve (§3.1.10). NFPA 20-2019 through 2025 §4.7.7.2 bars a relief valve as the way to meet the churn rating in §4.7.7.1.

Building deluge reducing valves are out of scope.

## When one is unavoidable

Prefer a direct-acting valve for a zone or a hose outlet. Install it horizontal, stem up, with approved trim relief on a sprinkler valve, and placard the set pressure, the set flow and inlet, and the design demand at the outlet. Size it from the manufacturer's chart at maximum inlet static, maximum outlet static, minimum inlet residual, minimum outlet residual, and the real flow range, including the alternate supply.

On a fire-service main provide a same-size normally closed bypass, meters on the outlet side, and a full-flow test drain. Where a parallel valve covers the low flow, the sheet's band runs from no flow to about twice the minimum or 20 percent of the main valve's maximum (§3.3). If the primary cannot pass the low inspection flow, set the secondary at 125 percent of the primary minimum (§2.3.1.5).

Inspection on Table 2.4.1.2-1 is weekly visual, semiannual partial flow, and annual full flow. Provide a drain that can take the test. A high-rise drain that cannot is an impairment problem (`standpipe-system.md`).

## Hose outlets

NFPA 14-2024 §10.2.4.2 requires a listed regulating device where static pressure at a 2-1/2 in. hose connection exceeds 175 psi, limiting both static and residual to 175 psi. A federal specification that triggers at 125 psi and sets the outlet at 100 psi is that specification. A city's residual band at 250 gpm is that city. Do not paste either onto the next job. Reserve the abbreviation for a reducing valve. Do not use it for a relief valve.
