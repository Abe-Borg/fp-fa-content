# Very-early-warning acceptance test

Port areas, the 60 second transport, and the pre-alarm map are `../fa/detection-layout.md`. This note is the heated-wire test and two hall rules that sit next to it.

FM DS 5-32 (January 2026) Appendix C: the heated-wire test produces Alert or Pre-Alarm within 120 seconds after energization ends, with fans on and with fans off, at least three times in each airflow state. The North American wire in Table C.2 is 22 AWG copper with 1.1 mm PVC, energized 30 seconds at a constant 28 A. The modified option uses 1 m wires in parallel, energized 60 seconds at a constant 6.0 V dc, with current drifting from 0 A to 30 A. Disable alarm verification for that short release and restore it before leaving. Run the test at the operational sensitivity.

If a location fails, fix the airflow or the pre-alarm ventilation interlock (§2.4.2.1.3). Do not desensitize the detector to make the test pass.

Provide at least two spot detectors in each protected space or zone where §2.4.2.3.2 applies and spot detectors are the method. Fire-alarm service is Class V or greater (§2.4.2.1.10). Below-floor detection may be omitted for FM Approved plenum or Group 1 cable, or where early-warning sampling is already at the below-floor return (§2.4.2.1.6).

Hot-aisle air can exceed 100 °F. Verify the FM Approval temperature for that location before a head or a port is placed there (§3.3.2.3).

NFPA 75 still requires ceiling detection throughout the information-technology area, detection below a raised floor that contains combustible cable, and damper closure from detection in the air path. Pin the section to the adopted NFPA 75 (`../fa/detection-layout.md`).

The valve opens on the pre-alarm level, not on the later alarm stage (FM DS 5-32 §2.4.3.2.1.3.1), together with low pressure. Fire 2 is not that level.
