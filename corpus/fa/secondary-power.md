# Secondary power for fire alarm and releasing

Pin the enforced NFPA 72 edition before applying a factor. The label changes.

## Hours

NFPA 72 §10.6.7.2.1: quiescent load, 24 hours minimum.

Then alarm: §10.6.7.2.2, evacuation or occupant-notification appliances for 5 minutes, unless the voice exception applies. Voice or alarm communications: §10.6.7.2.3 through §10.6.7.2.4, 24 hours quiescent and then 15 minutes at maximum connected load.

NFPA 72 has no releasing-only duration. Using 24 hours plus 5 minutes on a releasing panel is a reading of §10.6.7.2.2, not a dedicated releasing rule. Say so. A longer alarm (for example 10 minutes) is insurer, owner, or practice, and it needs a label. On FM work, FM DS 5-40 §2.3.4 (September 2007) states 90 hours plus 10 minutes for preaction release panels. Confirm that sheet is still the one in force. Conservative practice in this pack: FM jobs carry 90 hours plus 10 minutes; NFPA-only jobs carry 24 hours plus the alarm period above.

## Factor

- NFPA 72-2019 §10.6.7.2.1.1: include at least a 20 percent margin. Factor 1.20.
- NFPA 72-2022 and 2025 §10.6.7.2.14: a correction factor of 1.25 for aging. Factor 1.25.

Do not apply 1.20 on a 2022 or 2025 job, or 1.25 on a 2019 job. Do not label the FM releasing case as 90 hours plus 5 minutes. A teaching screen at 1.25, not a job result: a 15.20 ampere-hour base becomes 19.0 ampere-hours (26 ampere-hour pick), and a 56.45 ampere-hour base at 90 hours plus 10 minutes becomes 70.6 ampere-hours (100 ampere-hour pick). Do not copy a 1.20 product of those bases. The annex describes that factor as the aging allowance. Do not stack a second manufacturer aging factor on it for the same effect. Use the larger of the two, and say which one governed.

If fire-alarm secondary power holds egress doors locked, those doors unlock within 10 minutes of primary-power loss (NFPA 72 §21.10.3, same duty in 2019, 2022, and 2025), and the lock load is part of this calculation. Supplies that unlock on loss of power are outside that load (§21.10.4). Design practice uses those supplies. See `epo-and-disconnect.md`.

A facility UPS is not automatically the fire-alarm supply. Listing, supervision, and the transfer rules still apply. A stored-energy system under NFPA 111 is sometimes described as able to serve both primary and secondary with 24 hours of capacity. That reading was not confirmed against an edition in this pack. Do not size on it until the edition is in hand. Transfer to secondary power is within 10 seconds whenever primary voltage is not enough for required operation (NFPA 72 §10.6.6.1 in the 2019, 2022, and 2025 pulls). Confirm the paragraph before citing it on a submittal.

No held code section names in-rack backup power. It is information-technology power, not fire-alarm secondary power. Fire-alarm secondary power stays a dedicated fire-alarm battery, or a generator plus that battery. Trouble or thermal contacts from that equipment may be monitor points. The signal class is an owner election. Those points do not release. Rack-row smoke stays on the hall sampling layout unless the owner adds a detector. Whether an aggregate of that equipment is energy storage under IFC 2024 Chapter 1207 is an authority call. Do not label any of those rows as code. Size each fire-alarm supply alone. A synthetic 2025 screen, factor 1.25, is 15.21 ampere-hours for a building control unit at 24 hours plus 5 minutes, 25.88 ampere-hours for voice at 24 hours plus 15 minutes, and 9.16 ampere-hours for a double-interlock releasing supply at 24 hours plus 5 minutes. Do not copy those ampere-hours onto a job. Releasing at 24 hours plus 5 minutes stays a reading, not a dedicated releasing rule. The FM 90 hour comparison stays an owner election.

## Generator credit

§10.6.7.3.1(2) allows an automatic generator plus dedicated batteries with 4 hours of capacity (same text in 2019 and 2022). The text does not say whether the alarm minutes sit on top of the 4 hours. The generator itself has to meet NFPA 72 §10.6.11.3.1.1 (2022 and 2025): NFPA 110 Type 10, Class 24, Level 1. NFPA 110-2022 and 2025 Table 4.1(a) have no Class 24 row. Design practice: specify NFPA 110 Class X with 24 hours of fuel, Type 10, Level 1, and verify with the engineer of record. If the generator does not meet that, there is no 4-hour credit. Size the 24-hour battery.

NFPA 110-2025 §5.5.3.1 sets the main tank at not less than 133 percent of the low-fuel quantity for classes of 24 hours or less. Hand that multiplier to the generator engineer. Fire alarm does not size the tank. `calcs/fa` `epss_fuel` holds the 1.33 factor.

## Listing cap and energy storage

If the 24-hour battery exceeds the largest battery the panel lists (a 100 ampere-hour figure appears in the pack's standard list; verify it against the panel and the charger listing), split the load onto a second listed supply before using one battery larger than the listing. Rechargeable batteries must be listed or recognized (NFPA 72-2022 and 2025 §10.6.10.1.3, new in 2022).

Li-ion energy-storage smoke and fire detection: NFPA 855-2023 §4.8.3, 24 hours standby and 2 hours alarm. Those alarm signals go to a supervising station (§4.8.4). Do not size that detection battery as 24 hours plus 5 minutes. Gas detection on the explosion-control path: §9.6.5.6.7(4), at least 24 hours standby and 2 hours alarm. The exhaust-rate path at §9.6.5.1.5.4(3) asks 2 hours of standby only. Design practice sizes the gas panel at 24 hours plus 2 hours on both paths and shows both results. Confirm that NFPA 855-2023 is adopted. IFC 2024 §916.5 requires standby power or a trouble signal on power loss and sets no hours, so a trouble-only path does not satisfy §4.8.3.

On an IFC 2021 job, gas detection has at least 2 hours of standby power (IFC 2021 §1207.6.1.2.4). Do not copy that hour claim onto the 2024 section. The 2019 margin, the 2019 durations, and the generator-plus-4-hour battery are held. Do not apply the 2019 20 percent margin on a 2025 job.

Documentation of the capacity and the margin is NFPA 72 §7.2.1(7) (2019, 2022, and 2025). The annual test in Table 14.4.3.2 item 8 runs a general alarm for 5 minutes (voice 15 minutes). Those are test durations, not the sizing inputs.
