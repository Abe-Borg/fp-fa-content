# Emergency responder radio coverage

In-building public-safety radio is a separate system from the fire alarm. Its troubles are supervisory. Its power disconnect is not the information-technology-room disconnect.

Coverage figures used in two fire-code-cycle guidelines are 95 percent of each floor and 99 percent of critical areas. Critical areas in the stricter list include exit stairs, the fire command center, the fire alarm panel, smoke-control panels, fire-pump and valve rooms, main electrical rooms, standby-power rooms, and elevator cars. Confirm IFC §510 in the adopted edition before those percentages are sealed. The guidelines cite NFPA 1221-2019. That standard may have been consolidated into NFPA 1225. Do not cite 1221 as current until the consolidation is confirmed for the job. NFPA 72-2025 remote-station text already points at NFPA 1225 (`../fa/supervising-station.md`).

Downlink signal in those guidelines is at least −95 dBm. Delivered audio quality is at least 3.4 in both directions in two of the guidelines. IFC 2021 §510.4.1.1 is understood to accept 3.0. Confirm IFC 2024 before fixing the antenna count. Signal quality at acceptance is a signal-to-interference ratio of at least 20 dB and a bit-error rate of 2 percent or less on a Project 25 bitstream, in the guideline reading. One model text also states a 17 dB policy figure. Use 20 dB until the adopted code says otherwise.

Propagation delay is 15 microseconds or less. If it is longer, the booster is at least 16 dB above the macro signal at the radio. Uplink gain is 65 dB or less unless approved. Donor-to-indoor isolation is at least 20 dB above system gain.

Standby duration is not settled across the guidelines. One sizes 12 hours at full load, or a 2-hour battery plus a generator carrying full load for 12 hours. Another uses a 24-hour battery, or a generator for 24 hours plus a 12-hour battery. Confirm the adopted duration before sizing cabinets or fuel. Low-battery supervision at a 70 percent reduction of operating capacity, and generator-fuel supervision at 70 percent, are the stricter model's figures. Mark them as that model until the code section is confirmed.

Boosters, annunciators, and chargers are listed to UL 2524. Installation follows 47 CFR 90.219. Backbone survivability matches the building fire rating. One model also requires at least 2 hours. Donor antennas use a discharge unit listed to UL 497C on each donor coax, grounded per the NEC article the adopted code names for that coax.

Test after construction, fire doors closed, on a grid of 20 points per floor, by a party who is not the installer. A link budget is submitted. It is not the pass criterion.

Area triggers differ by guideline: above 20,000 ft² or three stories, versus 10,000 ft², two stories, or any basement. A data-center shell meets either trigger. Antenna spacing of 50 ft in occupied areas and 80 ft in open areas is model guidance for the radio designer. It is not a fire-alarm spacing rule.
