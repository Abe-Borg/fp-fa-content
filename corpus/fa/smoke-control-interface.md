# Smoke control interface

Most single-story data halls have no engineered smoke-control system. The interface shows up in an atrium, a high-rise office, or where the authority requires Chapter 9 smoke control. Check the IBC §909 trigger on the job before laying out a firefighter's smoke-control panel.

Where IBC 2021 or 2024 is adopted:

- Wiring for the smoke-control system, any voltage, is in continuous raceway, and it also meets NFPA 70 (§909.12.2).
- A mechanical system that uses pressurization, airflow, or exhaust is fully automatic (§909.12.3.1).
- Detection that controls smoke control complies with §907 and uses a listed control unit. Verification includes positive confirmation of actuation, a test path, manual override, and power taken downstream of the disconnects (§909.12 and §909.12.1).
- The firefighter's smoke-control panel overrides duct detectors and freeze stats (§909.16.3, item 1). It is also a fire-command-center feature.

Zone the fire-alarm inputs to the smoke-control zones. NFPA 72 annunciation zoning is §10.18.5. Smoke control is a line on the integrated-test matrix (`acceptance-testing.md`).

## Pressure and makeup, when NFPA 92-2024 is adopted

NFPA 1-2024 §2.2 references NFPA 92-2021. The criteria below are from the 2024 edition of NFPA 92. Confirm which edition the authority expects before sealing.

Minimum pressure difference across a barrier, sprinklered, any ceiling height: 0.05 in. of water (NFPA 92-2024 Table 4.4.2.1.1, used under §4.4.2.1.1). Mechanical makeup mass flow is less than the mechanical exhaust (§4.4.4.1.2). Makeup velocity does not exceed 200 ft/min where the makeup can reach the plume, unless an engineering analysis supports a higher velocity (§4.4.4.1.4).

Opposed airflow in §5.10.1 is flow from a communicating space into a large-volume space. It is not a stairwell rule.

NFPA 92-2024 §4.4.5 says smoke-control operation shall not compromise a gaseous-agent system. Gaseous agent is out of scope here. The sentence is a guard, not a design path.

One authority's smoke-control test standard, not IBC text, wants fans, dampers, and automatic doors to reach the commanded state within 60 seconds at the firefighter's panel, including after transfer to secondary power, and samples initiating devices rather than testing every device. Treat the 60 seconds and the sample size as that standard's rules. Confirm them in the adopted instrument before writing them into the matrix.
