# Space-by-space detection for a hyperscale building

Confirm the owner standard before treating this matrix as the basis. Company suppression under the heads is wet, dry, or double-interlock only. Foam, clean agent, and water mist are out of scope.

| Space | Detection | Notification |
| --- | --- | --- |
| Data hall | Air sampling at the ceiling and at the return. On an FM job the pre-alarm level is the double-interlock detection leg. No cross-zone on that leg. | Public-mode audible and visible, or visible-heavy where the authority allows reduced audible. Intelligibility is usually not required. |
| Aisle containment | Exhaust or return sampling where NFPA 75 §9.2.2(3) applies, plus ports in the aisle as practice. | Not a separate notification zone by default. |
| Raised floor with cable | A separate detection plane (NFPA 75 §9.2.2(2); NFPA 72 treats it as its own room). FM may allow omission for plenum-rated cable or where return sampling already covers the underfloor. | None by default. |
| Electrical, switchgear, UPS | Spot smoke or sampling. On an FM job, spot photoelectric or combination smoke to a constantly attended location (FM DS 5-19 §2.2.4). Spacing follows FM DS 5-48 where that sheet is in force. Heat is added in a high-ambient electrical room (FM DS 5-48 §2.2.1.5). Keep detectors out of arc-flash vent paths. | Public mode. |
| Medium-voltage room where NFPA 76 is adopted | Early-warning fire detection per NFPA 76 §6.10.5.1, same in 2020 and 2024. A count at 400 ft² per detector is a spacing estimate, not that section. Where NFPA 76 is not adopted, NFPA 72 spacing is the floor. | Public mode. |
| Lithium-ion energy storage | Smoke, plus gas on the explosion-control path. See `ess-room-detection.md`. | Public mode. Gas alarm distinct from the fire alarm where IFC §916.8 applies. |
| Generator | Heat. Fuel-tank permission may require detection. See `generator-room.md`. | Public mode. Run, fail, and low fuel are supervisory if the owner routes them. |
| Meet-me or signal-processing room | Very early warning when NFPA 76 applies and the signal-processing area exceeds 2,500 ft² (NFPA 76-2024 §6.11.6.1). At or below 2,500 ft² the 76 tier is early warning, not very early. NFPA 76 is not automatic for the hall. | Public mode. Alert stays supervisory. |
| Office | Spot smoke and manual stations as the occupancy chapter requires. | Public mode, or voice if the occupancy requires it. |
| Loading and storage | Heat, or the storage sheet. Do not use the hall's early-warning layout as the storage design. | Public mode. |
| Fire pump room | Pump running, elected alarm or supervisory. Every other pump signal supervisory. Valve tamper. Low temperature at 40 °F if a device is provided. See `supervisory-points.md`. | Public mode as practice. |

On an FM hall, slow ventilation on pre-alarm when air is at or above 5 ft/s or 60 air changes per hour. Ports, transport time, and the two-level areas are `detection-layout.md`.
