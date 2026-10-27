# Storage and staging sprinklers

Do not convert a storage row into the hall density, and do not add the NFPA 30 percent dry increase on top of an FM table row. FM states the wet column and the dry column separately.

FM DS 8-9 (March 2010 / interim July 2018) §1.0 applies above 10 ft for Class 1 through 3, above 5 ft for Class 4 or plastic, or above 200 ft² at any height when the pile is bounded by 8 ft aisles. That can start before the IFC high-piled trigger. Use the stricter of the two (`storage-families.md`).

Extend the storage design at least 15 ft past the storage, or to a wall, and 15 ft into an adjacent lower-hazard storage design (§2.3.3.5).

Double-interlock storage uses the dry column: standard-response upright, nominal 280 °F. Quick-response and pendent storage heads on this sheet are wet or antifreeze only (§2.3.3.2). Antifreeze is not a company default. Do not invent an antifreeze design here.

Hose follows the table's sprinkler count, not a count padded to a minimum area. Twelve sprinklers or fewer: 250 gpm for 60 minutes. Thirteen through 19: 500 gpm for 90 minutes. Twenty or more: 500 gpm for 120 minutes (Table 14, §2.3.3.7.2.3). Do not interpolate rows. Since the January 2008 revision, wet and dry are separate tables. There is no extra dry-area percentage to add (Appendix B).

Ceiling-only dry pipe from above 30 ft to 55 ft is Class 1 through 3 only, upright standard-response 280 °F, tree piping, on the order of 12,000 ft², and ambient at least 16 °F (§2.3.6.1). Double-interlock is not listed on that ceiling-only path. Sample dry rows with 500 gpm hose, from Tables 14a and 14b: 35 ft is 20 sprinklers at 7 psi (K25.2); 40 ft is 12 at 50 psi (K25.2); 55 ft is 16 at 50 psi (K33.6). Confirm the row in the sheet before sealing. These are not hall heads.

Balance both demands at the connection. Class 1 through 3: 6 sprinklers at 22 gpm, or 10 on two levels. Class 4 and plastics: 8 or 14 at 30 gpm, 7 psi minimum, K8.0 when the flow is above 30 gpm (Table 12, §2.3.4.8.1.2). Add in-rack flow at the point of connection. Adjusted flow equals the lower flow times the square root of the higher pressure over the lower pressure.

Open-frame racks need unblocked transverse flues at least every 9 ft. Solid shelves only if they are fixed and 20 ft² or less. Grating is at least 70 percent open (Appendix A). Otherwise treat the rack as solid shelf.

Storage layout on FM DS 2-0 §2.5.4: the obstruction exemption is 2 ft (Table 2.5.4.5.4.1), maximum area 100 ft², and maximum spacing 10 ft when the ceiling is above 30 ft. Slopes of 2 in 12 through 4 in 12 add 50 percent area on the peak-head options. Above 4 in 12, the remaining options are a false ceiling or wet in-rack sprinklers. Open-grid ceilings are prohibited (§2.5.4.5.6.1).

FM storage K-factors start at K11.2. There is no K5.6 or K8.0 storage sprinkler on that table (Table 2.5.4.1.1). K19.6 through K28.0 use 1 in. outlets. K33.6 uses 1-1/4 in.

Scheme 8-9A isolates the worst commodity at 60 gpm from the most remote 6 or 8 sprinklers, with 250 gpm hose for at least 60 minutes, and that demand is not simultaneous with the ceiling (§2.3.4.9).

Several applications in §2.3.6.3 through §2.3.6.8 are wet pipe only. A double-interlock storage room does not get those wet-only routes.

Stored lithium-ion above 60 percent state of charge, or uncartoned, or under a ceiling above 40 ft, leaves the commodity table and is protected by in-rack sprinklers (FM DS 7-112, October 2024, §2.4.2.2). That is not the room density in `density-area.md`.
