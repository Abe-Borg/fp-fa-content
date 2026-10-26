# Section 28 31 00 — Fire detection and alarm (draft)

Draft language for the fire alarm these sprinkler systems need. Verify with the engineer of record before issue. Do not author foam release or clean-agent release.

## Part 1 — General

### 1.1 Summary

Provide detection, notification, supervision, and releasing for the elected wet, dry, and double-interlock systems. Double-interlock releasing belongs to this section and to sprinkler Section 21 13 19. Do not write that releasing matrix into Section 21 13 16.

Pin the enforced NFPA 72 edition before applying a factor or a spacing rule. An unamended 2024 I-Code floor references NFPA 72-2022. NFPA 72-2025 is a delta unless the adoption says otherwise.

### 1.2 Double-interlock cause and effect

Water opens only when the detection leg and the low-air leg are both true. The matrix is the sequence of operation on the shop drawings, and the record drawings match the program that was loaded.

On an FM job, FM DS 5-32 is the double-interlock flag. The detection leg is an alarm-level signal the engineer of record accepts. An NFPA 76 alert is supervisory and is never that leg. Do not require a cross-zone to trip the valve on an FM job. Off an FM job, a cross-zoned first knock may still be the company default. Say which rule is in force. Do not copy a prior panel program.

Single-interlock programs are comparison-only. Do not use their zone counts as defaults. Do not add a foam column or a clean-agent column. During a test, notify occupants, do not discharge as the test method, secure the valve, confirm the circuit is monitored, and return the system to service.

## Part 2 — Products

### 2.1 Supervision, power, and wire

Supervise preaction valve position, low air, fire-pump signals, and the other points the sprinkler sections name. Map each point to a circuit class. Do not invent a module count. Pump-controller terminals are named in Section 21 30 00.

Secondary power: 24 hours quiescent, then 5 minutes of alarm, unless the voice path requires 15 minutes (NFPA 72 §10.6.7.2). NFPA 72 has no releasing-only duration. Say that when 24 hours plus 5 minutes is used on a releasing panel. Where FM DS 5-40 §2.3.4 (September 2007) is in force, carry 90 hours plus 10 minutes for that panel and confirm the sheet. Do not apply the FM duration to an NFPA-only job. Aging factor: 1.20 on NFPA 72-2019 (§10.6.7.2.1.1); 1.25 on 2022 or 2025 (§10.6.7.2.14). Do not swap them.

If the battery exceeds the largest battery the panel lists, split the load onto a second listed supply. Do not specify an unlisted battery or freeze a panel model number.

Size notification and releasing conductors from the voltage-drop calculation. Cite the adopted NEC wire table. Do not paste the table. A point-to-point circuit sums the segment drops. The end-of-line product is a different method. Name which one was used.

## Part 3 — Execution

### 3.1 Layout and interfaces

Spot spacing, beam rules, and very-early-warning sampling follow the adopted NFPA 72 and the insurer sheet when that sheet applies. Do not interpolate an airflow table. Under a raised floor, count a separate room. Keep detectors out of an arc-flash vent path. A supervisory alert is not the double-interlock detection leg.

Elevator recall and shunt trip are outputs coordinated with the elevator specification. Do not design the elevator sprinkler here. HVAC shutdown, door release, and electric locks are coordinated with the other specifications. Record whether a lock unlocks on alarm, on loss of power, or both.

Where the insurer figure applies, take the critical load off before water, then interlock cooling. Do not kill cooling while the load is still energized. Egress lighting stays on. No minute count for cooling after isolation is held. Mark a missing time unverified. A test mode used in integrated testing is on the matrix. Class each off-site signal as alarm, supervisory, or trouble. A gas trouble is not a gas alarm.
