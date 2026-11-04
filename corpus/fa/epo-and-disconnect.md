# Power disconnect, HVAC, doors, and elevator interfaces

NFPA 72 Chapter 21 has no data-hall power-isolation section. The information-technology disconnect is NFPA 75 plus NEC Article 645, where those apply, plus the owner and FM sequence in `interfaces.md`.

## Article 645 is optional

NEC Article 645 wiring methods apply only when every condition in 645.4 is met, including a disconnect under 645.10. Most hyperscale halls do not elect Article 645. Do not assume it from the words data hall. `interfaces.md` states the same fence.

Where 645 is elected, the disconnect is remote (645.10(A)) or the critical-operations path (645.10(B)). Underfloor cable permissions are 645.5(E), not 645.5(D). In both NEC 2020 and 2023, 645.5(D) is physical protection and 645.5(E) is under raised floors. NFPA 75-2020 and 2024 §11.4.5.4.2(5) print the older 645.5(D) letters. Quote 75 as printed, and apply the NEC (E) rule.

A UPS inside the information-technology room follows 645.10, and the disconnect also opens the battery from its load (NEC 645.11). The exception for Article 685 is the whole article in NEC 2020 and in NFPA 75-2020 §11.5.1(1). NEC 2023 and NFPA 75-2024 §11.5.1(1) limit that exception to Parts I and II of Article 685. A second exception covers sources of 750 VA or less. A hall UPS is rarely an Article 685 installation and is well over 750 VA, so neither exception usually applies.

## NFPA 75 disconnect

NFPA 75 §11.4.5 (2020 and 2024, same duty) requires an approved means to disconnect information-technology equipment power and the HVAC that serves it. The approved means disconnects power to all electronic equipment in the room or in designated zones (NFPA 75-2024 §11.4.5.1). Activation of the HVAC disconnect closes all required fire and smoke dampers (§11.4.5.3). The UPS in that room complies with §11.4.5, and the disconnect opens the battery from its load (§11.5.1 and §11.5.1.1). Power to the interlocks, the shutdown devices, and that disconnect is supervised by the fire alarm control unit (§9.2.6 and §9.2.7, both editions). Dampers also operate on smoke detection (§11.1.3 in the 2024 pull). Automatic power-off on detection is co-owned with the isolation method. This note does not set that sequence. Do not map NFPA 75 as Canada code.

The annex, not the requirement, discusses sequential shutdown, keeping cooling airflow, and avoiding a single detector that kills HVAC while the load is still energized. There is no held minute count for how long cooling continues. Mark a hold time `[V]`. FM prefers automatic isolation, with critical loads off before water. See `interfaces.md`.

## Emergency-control wiring

NFPA 72-2025 §21.2.4.1: the interface is within 3 ft without metal raceway or armored cable, or within 20 ft with metal raceway or armored cable. Class D is exempt (§21.2.4.2). The circuit is monitored (§21.2.8, pointing at §12.6). The function is automatic unless the governing document permits manual (§21.2.1).

2019 and 2022 §21.2.4 allow 3 ft where the circuit is not Class D. They have no 20 ft raceway allowance. On those editions use 3 ft or Class D.

Duct detectors initiate a supervisory signal [CODE NFPA 72-2019 §21.7.4]. An alarm is permitted in that edition only where there is no constantly attended location and no supervising station, or where another code requires an alarm (§21.7.4.1 and §21.7.4.2). NFPA 72-2022 and 2025 §21.7.4 are NEEDS HOLD. Do not assume the same sentence. Fire-alarm wiring to an emergency-control function is monitored for integrity under §12.6 [CODE NFPA 72-2019 §21.2.8]. Cite the enforced edition before using §21.2.8 on 2022 or 2025.

## Doors

Door-release monitoring is §21.9. Fail-safe holders that close on loss of power need no secondary power. Electrically locked egress doors unlock where other codes require it (§21.10). If fire-alarm secondary power holds those doors locked, they unlock within 10 minutes of primary-power loss (§21.10.3), and the lock load is in the battery calculation. Supplies that unlock on loss of power are exempt (§21.10.4). Design practice uses those supplies, so the lock load stays out of the fire-alarm battery. Confirm with the security design.

Unlocking occurs at or before public-mode notification in the area served (§21.10.5) and latches until manual reset (§21.10.6). The 2019, 2022, and 2025 door sections match. Which doors unlock is the building code and NFPA 101, not a fire-alarm election. Smoke-activated doors that IBC §716.2.6.6 covers start to close within 10 seconds, where IBC 2021 or 2024 is adopted.

## Elevator

Use this only where the building has an elevator. §21.3 is Phase I recall. Only lobby, hoistway, and machine-room detectors initiate it, unless the authority adds devices (§21.3.3.1). Three outputs go to the elevator: designated level, alternate level, and the machine-room indication (§21.3.14). A lobby detector is within 21 ft of the centerline of each elevator door it serves (§21.3.5.1). The 2022 text says on the ceiling. The 2025 text adds "in accordance with Chapter 17."

With authority approval, those detectors may initiate supervisory instead of alarm (§21.3.13). Record the approval.

Shunt trip, §21.4: heat detectors with a lower temperature rating and a lower response-time index than the sprinklers, within 24 in. of each sprinkler (§21.4.1 and §21.4.2). A waterflow or pressure switch used to shunt trip has no time delay (§21.4.3). A switch set to zero delay does not meet that intent on the annex reading. Loss of shunt-trip control voltage is a supervisory signal (§21.4.4 and §21.4.5).

NFPA 72-2019 §21.3.3.2 adds that a pit waterflow switch used for recall has no time delay, and the pit sprinkler is on its own valve. 2022 and 2025 do not carry that clause the same way. ASME A17.1 is not restated here.

These elevator points are not the double-interlock detection leg, and they are not the information-technology disconnect.
