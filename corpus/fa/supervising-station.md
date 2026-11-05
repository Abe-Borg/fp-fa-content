# Supervising station service and signal time

NFPA 72 Chapter 26 recognizes central station, proprietary, and remote supervising station service. The 2019, 2022, and 2025 definitions match. Only the definition numbers move (3.3.290, 3.3.301, and 3.3.306 across those editions).

A proprietary station is under the same ownership as the protected premises and is attended at all times. Staffing is at least two qualified operators, or one operator where retransmission to the communications center is automatic (§26.4.5.1 and §26.4.5.2, all three editions). Whether a site operations center qualifies is an authority and engineer-of-record decision. The code text does not decide it.

## Disposition

Fire alarm signals received at the station are retransmitted immediately to the communications center, except as §26.2.2 and §29.10.9.7 allow (NFPA 72-2022 and 2025 §26.2.1.2). The annex reads "immediately" as without unreasonable delay, and routine handling as a maximum of 90 seconds from receipt. That annex sentence is not the retransmission requirement.

Verification, where it is allowed, does not exceed 90 seconds from receipt at the station until retransmission of the verified alarm starts (2022 and 2025 §26.2.2(4)).

End-to-end time from initiation to display and recording at the station is 90 seconds maximum (2025 §26.6.3.8). Do not describe that 90 seconds as a path-failure timer.

Central station, all three editions: a backup path is operational within 90 seconds after a subsidiary station or channel failure; fire alarms are retransmitted; a supervisory signal gets a dispatched response within 2 hours unless a scheduled procedure clears it; a trouble not restored within 15 minutes gets a call to the subscriber's designees; an impairment restoration plan is in place within 4 hours. Operators do not put another activity ahead of that work (2025 §26.3.7.2.2, same duty where the edition matches).

Remote station signals may terminate at a communications center that meets NFPA 1221 in the 2022 text (§26.5.3.1.1) and NFPA 1225 in the 2025 text. Cite the edition.

## Path supervision

A single communications path is supervised at not more than 60 minutes, and failure annunciates within 60 minutes (§26.6.3.3). Each path of a multipath arrangement is supervised within 6 hours. In 2022, failure of any multipath leg annunciates at the station within 6 hours (§26.6.3.4(2)). The 2025 text drops that 6 hour station-annunciation item. Design practice keeps the 6 hour multipath indication until the engineer of record accepts the deletion. Intervals otherwise stay 60 minutes and 6 hours. The 2025 book renames "path" to "pathway" and points failure annunciation at §10.15.

NFPA 72-2025 §10.15.1 is general trouble indication within 200 seconds. It is not the supervising-station path timer. Do not cite §10.15 for a 60 minute or 6 hour path. The 2025 multipath annunciation sentence is not claimed. An owner may set dual-path failure annunciation to not more than 60 minutes. That election is stricter than the 2022 6-hour multipath floor. It is not code. A schedule row that tags the 60-minute dual-path time as code is not the source.

Where fire pumps are monitored and a building fire alarm system is installed, pump running may be supervisory or alarm (NFPA 72-2025 §23.8.5.9.1). The owner election in this pack transmits it as supervisory. Other pump signals stay supervisory (§23.8.5.9.2). Air-sampling alert and action stay local and are not transmitted. Air-sampling Fire 1 is transmitted as supervisory. Those three are owner elections. An off-gas point is owner or practice. It is not code.

Model codes send alarm, supervisory, and trouble signals to an approved supervising station, or to a constantly attended location where the fire code official approves (IBC 2021 §903.4.1; IBC 2024 §903.4.2). Duct detectors are supervisory where a supervising station is required.

NFPA 76 Alert stays supervisory and does not sound building notification. See `di-releasing.md`.

On an FM job the occupancy sheet wants alarm annunciation at a constantly attended location and service at Class V or better. Class letters are FM DS 9-1. They are not Chapter 12 pathway classes (`../fp/alarm-service-class.md`).

Gas signals are not classified by NFPA 72. Where NFPA 855-2023 §9.6.5.6.7(5) applies, failure of the gas system is trouble, and a concentration above 10 percent of the lower flammable limit is an alarm, at a supervising station or a constantly attended location. Off-gas early warning and fan-proof points are supervisory unless that alarm threshold is crossed. See `ess-room-detection.md`.
