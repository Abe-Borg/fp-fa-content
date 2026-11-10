# Releasing panel for double-interlock

Use a fire alarm control unit listed for releasing service, and releasing devices listed for use with that unit (NFPA 72 §23.11.1 and §23.11.2, same duty in 2019, 2022, and 2025). Where FM controls the job, the valve, the solenoid, and the panel are an FM Approved combination. Confirm the category on the submittal. Do not assume a general alarm panel can release water.

Each releasing device is supervised, and the field wiring is supervised per §12.6 (§23.11.3 and §23.11.4). The sequence of operation matches the suppression standard, which for this company is NFPA 13 (§23.11.6). Each protected space has at least one automatic detector on the releasing unit (§23.11.7). One releasing unit monitors the inputs and operates the release, unless a listed multi-unit arrangement meets §23.11.9 (§23.11.8).

The releasing unit is monitored by the building fire alarm for alarm, supervisory, and trouble, and it does not depend on that building system (§23.11.10 and §23.8.5.10). Intervening valves are supervised per Chapter 17. Protect the releasing equipment from the suppression system it controls (§23.11.11).

## Disconnect

A physical disconnect lets the system be tested without tripping suppression (§23.11.5). Operating it causes a supervisory signal. NFPA 72-2019, 2022, and 2025 §23.11.5.2 require a physical switch. A software disable, including a dedicated key on the keypad, does not comply. FM DS 5-40 §2.4.3, September 2007, says the same thing: disconnect the release wiring before a functional test.

## Two detectors, when used

Cross-zoning is permitted for alarm response when the authority allows it, at least two detectors serve the space, alarm verification is not used, and the sequence is in the Chapter 7 documents (NFPA 72 §23.8.5.4.3). The sequence item is new in 2022. 2019 stops at the prior items. For suppression actuation, spacing follows Chapter 17 (§23.8.5.4.4). The 0.7 factor in §23.8.5.4.5 is for two detectors that start public notification. It is not the suppression spacing. Those duties match in 2019, 2022, and 2025 aside from the 2022 sequence item.

On an FM job, do not cross-zone the preaction detection leg. FM DS 5-32 §2.4.3.2.1.3 forbids it. One alarm-level pre-alarm plus P, the pressure drop from sprinkler operation, is the pair. Off an FM job, a cross-zoned first knock may still be the company default. See `di-releasing.md`.

Water releases only when detection and P, the pressure drop from sprinkler operation, are both true. Program the panel so a loss of supervisory pressure alone cannot open the valve. Low air is supervisory only (tag PSL-SUP) and is never a release input. On panels that treat "normal" release as OR logic and "cross-zoned" as AND logic, mapping detection and the P contact as a normal OR zone is a failed program: the panel may raise no trouble, and the P contact alone can trip. A zone type that is supervisory only cannot be the release input. A panel zone printed as a low-air alarm type that serves as the electric/electric P contact is tagged PSL-REL, not PSL-SUP, and is ANDed with detection. A zone on the supervisory low-air signal stays supervisory. Witness the printed zone-to-output map. The riser diagram does not show that setting.

Disabling an output programmed as releasing is a supervisory signal on the panel reviewed for this note, not a trouble. Walk test disables release outputs and can restore them after 30 minutes of inactivity. Walk test is not the impairment control. The physical disconnect is. Confirm whether the programming switch is supervised, and whether it times out, on the submitted panel.

Abort is not a listed function for preaction release under the UL 864 reading used here. Do not add an abort column.

Solenoid current sets the release-circuit wire size. A special-application resistance limit of 1 divided by solenoid current, in ohms, is a panel limit, not an NFPA formula. Count a detection input and a P input per double-interlock zone before choosing a conventional panel, plus the supervisory low-air input. On electric/pneumatic trim the actuator at the valve is P, so the panel sees the solenoid side and the supervisory monitor. Then add waterflow and valve supervision.

Standby duration is `secondary-power.md`. There is no releasing-only hour in NFPA 72. Clean-agent and foam release columns are out of scope. Single-interlock programs are comparison-only.
