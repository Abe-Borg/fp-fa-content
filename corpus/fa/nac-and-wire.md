# NAC voltage drop and conductor resistance

Notification-appliance-circuit calculations are part of the documentation package: NFPA 72 §7.2.1(8) in 2019, 2022, and 2025.

Design by the end-line-loaded method or by point-to-point, NFPA 72 §18.3.7.4. The pack checks NFPA 72-2025 §18.3.7.1 through §18.3.7.6: starting voltage (name whether it is the manufacturer's rated start or a measured start), Class and length basis, 75 °C copper, both conductors.

End-line loading multiplies the total appliance current by the resistance of the full circuit. Point-to-point walks the circuit: each segment carries only the current downstream of it, and the drops add. Those are different numbers. Do not report the end-line product as if it were the point-to-point result. `calcs/fa` `nac_vdrop` implements both. A worked check in that library (two 0.2 A appliances, 100 ft and 1,000 ft, 18 AWG stranded, 20.4 V start) is 14.04 V end-line and 16.902 V point-to-point. Those figures demonstrate the method. They are not a hall design.

The end-line and point-to-point methods, the 75 °C basis, and the instruction to count both conductors are NFPA 72-2025 §18.3.7.1 through §18.3.7.6. NFPA 72-2019 has no §18.3.7. NFPA 72-2022 has §18.3.7.1 and §18.3.7.2 only, and it does not state a speaker loss in decibels. On a 2019 or 2022 job those methods stay design practice. Do not label them as that edition's text.

Speaker circuits are a different limit: 1.0 dB electrical line loss, NFPA 72-2025 §18.3.7.2.1. On a 2019 or 2022 job that 1.0 dB figure is practice, not that edition's text. Module loss comes out of the budget before the cable loss. Amplifier failure is a trouble signal (NFPA 72 §10.19.1, same duty in 2019 and 2022). Compare 25 V and 70.7 V when both are available. `fa-speaker-circuit-loss-check` owns the pass or fail.

## NEC Chapter 9 Table 8

Resistance per foot comes from NEC Chapter 9 Table 8 for the gauge, the stranding, and the temperature. The numeric table is data used by the voltage-drop skill. This note does not reprint it. Confirm the edition of NFPA 70 (the unamended 2024 I-Code reference pin is NEC 2023; resolve the project instrument separately) and confirm the license to rely on the table before issuing the calc. `fa-nec-table-8-wire-sizing` elects the gauge. It does not decide audibility.

Pathway survivability (NFPA 72 Levels 0 through 4, and the 3 ft / 20 ft / Class D choices for an emergency voice system) is `fa-pathway-survivability-election`. It is not a voltage-drop result.
