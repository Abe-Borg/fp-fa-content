# Variable-speed pressure limiting

Use this note when churn plus the highest static suction exceeds the lowest-rated component, and a single pump stage has to reach the remote demand. The envelope check and the relief-valve screen are `pump-and-supply.md`. Series pumps are not used (`fire-pump-installation.md`). A sprinkler pressure-reducing valve is the last resort (`pressure-regulating-devices.md`).

The high-rise chapter, which is about floors beyond the fire department's pumping reach, does not apply to a hall. Do not import its zone counts. The part that does apply is a high starting pressure at the end of a long main, on a supply whose residual moves.

## The four moves

Name the ceiling first. It is the lowest-rated component in the path. The usual plateau is 175 psi. NFPA 13-2022 and 2025 §7.1.2 are the component-rating cite. Heads listed only to 175 psi set the ceiling even when the pipe is stronger. Whether FM lists sprinklers at 250 psi has to be checked in the current Approval Guide (`[V]`). Do not pick a pressure class the heads cannot meet.

Churn is net shutoff plus maximum static suction. NFPA 20-2019 through 2025 §6.2.2 limit shutoff head to 140 percent of rated head. A carrier preference is 120 percent. Check churn at the highest suction, not at the design flow.

| Move | What blocks it |
| --- | --- |
| Rate the components higher | Head listings. On an FM job, confirm a listed head exists before you leave 175 psi |
| Add a series pump | FM DS 3-7 §2.2.2.2. About 3 percent failure to start per electric unit compounds in series |
| Reduce pressure with a valve | NFPA 20 §4.7.7.2 forbids a relief valve as the way to meet the churn rating. FM DS 3-7 §3.1.10 rejects trimming the curve with a relief valve. Some jurisdictions allow reducing valves only at individual hose outlets. Confirm locally |
| Limit speed | FM DS 3-7 §3.1.11 says variable speed is best avoided, and then allows it for a wide suction swing, for replacing high-rise reducing valves, or for tall-building suppression. Frame a hall request as the suction-swing case, in writing |

## What speed control costs

Affinity: flow follows speed, head follows speed squared, power follows speed cubed. A published comparison, on one supply and one building height, needed about 1.5 to 2.5 times the horsepower to buy the extra pressure at the same rated flow. Those horsepower figures are that paper's. Price the generator, the transfer switch, and the Article 695 feeder (`fire-pump-power-circuit.md`). The saving, where it exists, is a zone you do not build. It is not a smaller motor. On a campus that already wants a diesel driver, the diesel is the variable-speed candidate. The electric variable-speed controller is the expensive one.

If the control fails, the pump returns to rated speed and can exceed the component rating. NFPA 20-2019 through 2025 §4.20.1.3 require a relief valve where the maximum discharge head at shutoff and rated speed, adjusted for elevation, exceeds the component rating. An older claim that every variable-speed pump needs a relief valve is broader than that section. Set the relief at least 10 psi above the limiting setpoint (§4.20.1.3.1). From the discharge flange to the indicating control valve, the components are rated for the highest potential pressure. Do not let that spool be substituted down. Discharge the relief where the operator can see it, never back to the suction, with no shutoff in the relief piping (`fire-pump-installation.md`).

FM rules when variable speed is used: relief consideration above 232 psi uncontrolled, controller-to-motor cable at most 100 ft, an inverter-duty motor sized on nameplate power with no service factor, a dedicated pressure sensor per pump, churn held within 5 percent of the target, output frequency never above line frequency, and manual stop only (§3.1.11).

Do not spend a wider usable flow (a paper's 140 to 150 percent) on an FM job. The 140 percent single-pump and 110 percent multiple-pump caps are about the curve (`fire-pump-installation.md`). Speed control does not raise them.

## Tank suction

On stored water, size the pump on the lowest suction at the end of the duration, and check churn on the highest suction with a full tank. Speed control flattens the top of that range. It does not make water at the bottom. A later phase that pulls the same main down is a foreseeable drop. Absorb it in the driver selection at the start, or re-pump a finished building later.
