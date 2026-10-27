# Jockey pump setpoints

The jockey pump makes up leakage. It is not a fire pump, and the fire pump is not the jockey. NFPA 20-2019, 2022, and 2025 §4.27.3 set the capacity at least at the normal leakage rate. Section 4.27.7 bars using the fire pump for pressure maintenance except as Chapter 8 allows. Pump selection and the room are `fire-pump-installation.md`. Controller refuse items are `fire-pump-controller.md`.

## Setpoints

The annex separation is advisory. Fire-pump start sits 5 psi below jockey start in the 2016, 2019, and 2022 annexes, and 10 psi below in the 2025 annex (A.14.2.6). Cite the edition the authority enforces.

Take the controlling carrier when the sheets disagree:

| Setting | FM DS 3-7 §2.4.11.6 | A carrier sheet that asks for a wider band |
| --- | --- | --- |
| Jockey start | Churn plus maximum static suction plus 5 psi | — |
| Jockey stop | Jockey start plus 10 psi | At least 15 psi above jockey start |
| Fire-pump start | 5 to 10 psi below jockey start | About 10 psi below jockey start |
| Each added pump | 10 psi lower | 10 psi steps |

Do not copy another pump's cut-in and cut-out. A federal specification's 110 psi and 125 psi placeholders are that specification.

Each controller, including the jockey, gets its own 1/2 in. sensing line between the discharge check and the discharge control valve (FM DS 3-7 §2.4.11.2). No shutoff valve on that line. Two check valves at least 5 ft apart, each clapper drilled 3/32 in., are the surge dampers on that reading.

A minimum-run timer is allowed only when jockey shutoff plus maximum static suction stays inside the system working pressure (NFPA 20-2019 and later §4.27.5.2; the 2016 number is §4.26.5.2). Setting a fire-pump run timer to zero is not an acceptable way to get manual stop (FM DS 3-7 §2.4.10.1).

## Size

The annex sizes the jockey to make up allowable leakage in 10 minutes, or 1 gpm, whichever is larger (NFPA 20-2019 and 2022 A.4.27.2.1; 2025 A.4.27.2.2). On an aboveground system the flow stays below one sprinkler. A rule of 1 percent of the fire-pump rating is not in NFPA 20, and it can hide an open head.

On a dry or double-interlock system the jockey holds the wet side up to the valve. Air or nitrogen on the dry side is `air-maintenance.md`. Frequent jockey starts mean leakage, a dry-side problem, or thermal expansion. Find the cause. Do not widen the band to hide it.

Feed the jockey from the emergency or standby panel, not from the fire-pump controller (NEC 2017 through 2023 §695.6(I); 2026 §695.7(I)). It is still part of the fire-pump source sizing. Check the jockey controller's short-circuit rating against the available fault current. Do not copy one catalog's ampere table onto another controller.

Acceptance starts in NFPA 20 §14.2.7.2 (six automatic and six manual) apply to the fire pump. Jockey acceptance follows the controller listing and the specification.
