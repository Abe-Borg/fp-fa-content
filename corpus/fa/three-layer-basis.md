# Three-layer basis for fire alarm

Design each fire-alarm parameter to the most stringent of three layers, and print the delta against the NFPA 72 edition that is actually enforced.

1. Code floor: the adopted IBC or IFC §907, NFPA 72, and NEC Article 760. NFPA 75 applies to information-technology equipment rooms. NFPA 76 applies to telecommunications. Do not apply NFPA 76 to a hyperscale hall unless the room is telecommunications or the owner, the insurer, or the authority adopts it.
2. Insurer: FM DS 5-32 for the data-processing occupancy, FM DS 5-48 for detection installation, and FM DS 5-40 for the alarm system. DS 5-40 is the September 2007 sheet. Reconcile it before you use a figure. See `../fp/fm-alarm-sheet.md`.
3. Owner: the project standard. It can raise a value. It cannot drop the code floor or an insurer condition.

## Deltas to report on an FM hall

These are insurer or owner deltas, not NFPA 72 defaults.

- Very early warning in the data-processing room, with the port areas and the 60 second transport in `detection-layout.md`. NFPA 72 air sampling allows 120 seconds. The tighter clock governs when FM or NFPA 76 applies.
- One pre-alarm level trips the preaction detection leg. Cross-zoning that leg conflicts with FM DS 5-32 §2.4.3.2.1.3. See `di-releasing.md`.
- FM DS 5-32 §2.4.1.1 ranks double-interlock last. Company practice keeps double-interlock and flags that rank to the owner and the insurer.
- Ventilation slows on pre-alarm at or above 5 ft/s or 60 air changes per hour.
- Supervising-station service at FM Class V or better. Class letters are an FM sheet. They are not NFPA 72 pathway classes.

NFPA 75-2024 detection for information-technology areas is §9.2, including the containment exhaust or return at §9.2.2(3). Disconnect of information-technology power is §11.4.5. A UPS in the equipment room follows §11.5.1 and §11.5.1.1. The 2020 edition matches those section duties except the Article 685 wording in §11.5.1(1). See `epo-and-disconnect.md`.
