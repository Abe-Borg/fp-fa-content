# Energy-storage and UPS room detection

Suppression density for the room is a fire-protection note (`../fp/density-area.md`). This note is detection, gas signals, and standby hours.

Where IFC 2021 or 2024 is adopted, rooms and walk-in units with electrochemical energy storage get smoke detection or radiant-energy detection, and the alarm goes to a supervising station or to a constantly attended location where approved (IFC §1207.5.4). IBC 2024 §907.2.23 points those rooms at that section. IFC 2024 applies the chapter above the Table 1207.1.3 lithium-ion threshold of 20 kWh. The 2021 table number is Table 1207.1.1. A small remote telecommunications structure with lead-acid or nickel-cadmium batteries is the exception. It does not describe a hall UPS room.

IFC 2024 Table 1207.7 marks smoke and automatic fire detection, and the technology-specific protection in §1207.6, as required in both dedicated and nondedicated buildings. A data-center energy-storage room is nondedicated (§1207.7.2). Keep off-site transmission. A dedicated-building waiver of that transmission does not apply.

IFC Table 1207.6 marks exhaust ventilation as not required for lithium-ion. The gas-detection rule that rides on required exhaust (§1207.6.1.2.4) is therefore not triggered by lithium-ion through that table. Explosion control is required (§1207.6.3, pointing at §911) unless an exception is approved. Table 911.1 requires venting or prevention for electrochemical storage where §1207.6.3 applies. It does not require a barricade. NFPA 855-2023 §9.6.5.6.3 allows either NFPA 69 explosion prevention or NFPA 68 deflagration venting. The gas-detection items in §9.6.5.6.7 apply where gas detection activates a concentration-reduction system under an NFPA 69 study. Design practice on a lithium-ion room uses that prevention path and still confirms the hazard-mitigation analysis. Venting remains an allowed alternative. Do not treat the practice path as the only legal path.

## Setpoints and hours

Mechanical exhaust, where the exhaust path applies, starts above 25 percent of the lower flammable limit and stays on until the concentration is below that level (IFC 2024 §1207.6.1.2.4; NFPA 855-2023 §9.6.5.1.5.4). The exhaust-path standby in NFPA 855-2023 §9.6.5.1.5.4(3) is 2 hours.

On the explosion-control path, NFPA 855-2023 §9.6.5.6.7(5) sends a trouble on gas-system failure and an alarm above 10 percent of the lower flammable limit to a supervising station or a constantly attended location. Lithium-ion gas detection on that path is 24 hours standby and 2 hours alarm (§9.6.5.6.7(4)). Smoke and fire detection for lithium-ion storage is also 24 hours standby and 2 hours alarm (§4.8.3). Design practice sizes the gas panel at 24 hours plus 2 hours on both paths and shows both results. `secondary-power.md` states the same pair. IFC 2024 §916.5 requires standby power or a trouble on loss of power and sets no hours, so a trouble-only path does not satisfy §4.8.3.

NFPA 72 does not classify a gas signal. The distinct gas alarm is IFC §916.8, where IFC 2024 is adopted. Gas detection installed on a fire alarm system falls under NFPA 72 Chapters 1, 10, 14, 17, and 23 (2022 §17.10.2.2). Connect gas points to the fire alarm only where approved and where the control unit listing allows it (IFC §916.10).

The 10 percent threshold may be of the mixture or of the individual components (NFPA 855-2023 §9.6.5.6.7(1)). A sensor that reads one species and is set on a pure-gas scale can trip late. Hydrogen, methane, and ethylene lower flammable limits used as pure-gas references are NFPA 497-2024 Table 4.4.2: hydrogen 4 percent, methane 5 percent, ethylene 2.7 percent by volume. If the project basis lists a lower value, use the lower value. Do not relax a 10 percent energy-storage setpoint to a 25 percent process-gas setpoint.

Multiple panels aggregate to a master or annunciator at a location the authority approves (NFPA 855-2023 §4.8.2.2). Alarm signals from the detection system go to a supervising station (§4.8.4). Do not replace the §4.8.3 two-hour alarm period with the five-minute building-alarm period.

## Before the detector layout

Check stored energy against the maximum allowable quantity first. IFC 2024 Table 1207.5 and §1207.5.1 are that check. A room over the quantity can pass every detector spacing check and still be wrong. The annex suggests hydrogen is usually the largest gas, with methane, ethane, propylene, and ethylene also present, and that a single location may not be enough in a large room (NFPA 855-2023 A.9.6.5.6.6). Annex text is not the requirement. Maintenance intervals in that annex run from 1 to 12 months. The requirement is the manufacturer's interval or the occupancy sheet, whichever is shorter when both exist.

NFPA 855-2026 adds thermal-image detection as an option and points secondary power at Section 4.10. IFC 2024 Chapter 80 lists an earlier NFPA 855 edition while §1207 says it is based on the 2023 edition. Which edition binds is an authority question. Do not mix 2026 section numbers into a 2023 job.

FM DS 5-33 is the insurer sheet for the energy-storage occupancy when the room leaves the data-processing sheet. Distributed lithium-ion backup at or below 20 kWh per rack can stay under FM DS 5-32. Above that, use DS 5-33 (`../fp/hall-geometry.md`).
