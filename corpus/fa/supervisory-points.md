# Fire pump and preaction supervisory points

The fire-protection design owns the pump, the driver, the controller, the compressor, and the setpoints. This note owns the monitor point, the signal class, and the label on the fire alarm.

NFPA 72 §23.8.5.9 is the same text in 2019, 2022, and 2025. Where pumps are monitored and a building fire alarm exists, the pump-running signal may be alarm or supervisory (§23.8.5.9.1). Every other pump signal is supervisory (§23.8.5.9.2). If the owner, the insurer, and the authority do not elect alarm for pump running, label it supervisory and say the label is assumed. A churn test would otherwise sound the building alarm. Waterflow is already the fire alarm.

A controller contact named trouble is still an NFPA 72 supervisory signal. Do not map it to a fire-alarm trouble point.

## Electric controller

NFPA 20-2025 §10.4.7.2 remote signals, each supervisory except running:

1. Pump or motor running (§10.4.7.2.1).
2. Loss of phase (§10.4.7.2.2).
3. Phase reversal (§10.4.7.2.3).
4. Connected to the alternate source, when a transfer switch is provided (§10.4.7.2.4).
5. Alternate-source isolating switch or breaker open, when a transfer switch is provided (§10.4.7.2.5).
6. Controller or system trouble (§10.4.7.2.6).

Contacts for items 1, 2, 3, and 6 are required (§10.4.8). Items 4 and 5 are required when the controller has a transfer switch. The 2019 and 2022 lists match except the trouble content. 2019 and 2022 §10.4.7.2.6 name four conditions: ground fault where provided, the pressure sensor, variable-speed trouble, and failure to start. 2025 adds motor overload, single phase, pressure above the rated components, low reservoir, and low suction pressure, nine items in all. On a 2019 or 2022 job the four conditions are the code minimum. Carry the extra five only as practice or as the submitted controller provides them.

2022 adds §10.4.7.2.3.2, which permits monitoring of a phase reversal upstream of multiple sources. 2019 is one paragraph.

## Diesel controller

NFPA 20 §12.4.2.3 is the same in 2019, 2022, and 2025. Engine running is a separate signal and follows the same alarm-or-supervisory election. The main switch in the off or manual position is a separate supervisory signal. Controller or engine trouble may be separate signals or one common supervisory signal. "Three contacts" is a reading of that grouping, not a code count. Confirm the grouping on the submittal. Failure to start and loss of battery or charger power sit inside the trouble group unless the owner asks for discrete points.

## Valves, room, and jockey

Suction, discharge, bypass, and backflow isolation valves are supervised open where provided (NFPA 20 §4.18.1, same in 2019, 2022, and 2025). Electrical supervision or a local signal at a constantly attended point creates a fire-alarm point. Locking, or sealing with a weekly inspection, does not. A hose-valve header control valve is supervised closed (§4.18.2). Jockey-pump isolation valves are not required to be supervised (§4.27.6.7). The 2025 text says jockey pump. The 2019 and 2022 text says pressure-maintenance pump. The duty matches.

Valve off-normal is within the first two revolutions of the handwheel or one-fifth of the travel (NFPA 72-2025 §17.19.1.2; 2019 and 2022 §17.17.1).

Room-temperature supervision, where a device is provided, signals at 40 °F (NFPA 72-2025 §17.19.5; 2019 and 2022 §17.17.5). Whether the device is required is a fire-protection and insurer call.

A jockey running or trouble point is not named in §23.8.5.9. Add it only if the owner asks, and label it supervisory and assumed.

## Preaction riser

Per double-interlock valve:

- Low air and high air, each supervisory (NFPA 72-2025 §17.19.2.2.2). The setpoint is the valve listing and NFPA 13, not this note.
- Control-valve tamper, supervisory.
- Waterflow, alarm, within 90 seconds (§17.15.2 in 2025; §17.13.2 in 2019 and 2022).
- The low-air release input is logic, not a second supervisory label. Electric/pneumatic trim keeps the low-air switch supervisory and trips on the pneumatic actuator. Electric/electric trim uses an electric low-air input. Assume the trim the fire-protection design elected.

No NFPA 72 section was found that names a compressor or a nitrogen generator. Monitor their trouble and power-loss contacts as supervisory, label the class as practice, and do not cite §17.19 for them. §17.19.2.2.4 leaves other pressure sources to the authority.

Waterflow and valve points on the riser land on the releasing panel, and alarm and supervisory repeat at the building panel (NFPA 72 §23.8.5.10.2). The releasing panel does not depend on the building panel (§23.11.10.2). Pump points land on the building panel. One monitor module per contact is the counting default. A dual-input module needs a listing and an owner acceptance.

Remote signal power is at most 125 V and is supervised (NFPA 20 §10.4.7.1 and §12.4.2.1). It is not taken from the engine starting batteries on a diesel controller.
