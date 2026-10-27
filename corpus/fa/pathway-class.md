# Pathway class: SLC, IDC, and NAC

NFPA 72-2025 §12.3 names the classes. Class A survives a single open. Class B has no redundant path. Class C is verified end to end. Class D fails safe. Class E is not monitored. Class N is an IP-style path and is redundant when two or more endpoint devices depend on it. Class X survives an open and a short. Style 4, 6, 7, Y, and Z are retired names. Do not put them on a drawing.

## Separation

Outgoing and return conductors of Class A, Class N, and Class X stay apart (NFPA 72 §12.3.8 and §12.3.8.1). The same cable, enclosure, or raceway is allowed only for 10 ft or less at an enclosure entry, for a single drop to one device, or for a drop to several devices in one room of 1,000 ft² or less that contains no emergency-control interface. The 10 ft and 1,000 ft² limits match in 2019, 2022, and 2025. The 2025 text says "emergency control function interface devices." The 2019 and 2022 text says "emergency control function devices." The limit is the same.

## Fault timing

A single open or ground, and the restoration, indicates within 200 seconds (§12.6.1 and §12.6.2). That 200 seconds is the same in 2019, 2022, and 2025. The restore cite is §12.2.3.4 in 2019 and §12.2.3.5 in 2022 and 2025.

Integrity exemptions changed. In 2022, a shunt, a notification circuit in the same room, and a pneumatic rate-of-rise are exempt, and a 20 ft enclosure interconnection may be in conduit or equivalent protection. In 2025 those three exemptions are dropped, and the 20 ft interconnection needs metal raceway or metal armored cable. Cite the edition.

## Class N redundancy

NFPA 72-2022 §12.3.6(1) describes Class N as two or more pathways, with a one-device exception that allows a single pathway. NFPA 72-2025 §12.3.6(1) ties the redundant path to two or more endpoint devices, and §12.3.6(2) allows a single path when only one endpoint is connected. Whether a lone remote amplifier needs the redundant path on 2022 and not on 2025 is not settled. The annex was not compared. Design practice provides the redundant path on both editions until the engineer of record rules otherwise.

The shared-segment item number also moved: 2022 §12.3.6(5), 2025 §12.3.6(7).

No numeric device cap on one signaling-line fault was in the Chapter 12 pull. Isolators remain a design-practice layout.

## Defaults

Design practice on a hyperscale hall: signaling line circuit Class X or Class A; notification circuits Class B, with Class A risers where the owner requires them; initiating device circuits only for air sampling and conventional relay inputs. On an FM job, FM DS 5-48 wants preaction detection to survive a single fault, which supports Class A or Class X on the releasing panel. Water-valve circuits on the September 2007 FM DS 5-40 reading are Class A, with no cross-zone and no alarm verification. Confirm that sheet is still the one in force (`../fp/fm-alarm-sheet.md`).

Emergency-control wiring distance is `epo-and-disconnect.md`. Survivability level is `pathway-survivability.md`.
