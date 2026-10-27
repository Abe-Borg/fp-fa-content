# Water-supply reliability

Adequacy is gallons, pressure, and duration. Reliability is whether that supply is still there when a valve, a pump, or a main is out. FM DS 3-29 (October 2017 / interim April 2021) owns the arrangement. It does not own the demand. Demand stays on the occupancy sheet and on `pump-and-supply.md`.

The sheet's baseline is one supply that is both adequate and reliable. Section 3.1 attributes most sprinkler failures to valve supervision, impairment, and inspection, not to the absence of a second source. A campus can still need a second source. Appendix C is the conversation: size, value, continuity, and rebuild time. Write down which factors drove the choice. Do not absorb an enhanced supply into the code floor.

## Preference order

FM DS 3-29 §2.1.1.2, best first:

1. A direct connection to a reliable public or industrial supply.
2. An on-site gravity tank.
3. A fire pump taking suction from a closed-top tank.
4. A fire pump on a reliable public or industrial supply.
5. A fire pump on an open reservoir.
6. A fire pump on a break tank.

A single-story hall usually lands on 1, 3, or 4. Gravity tanks are uncommon where the building cannot make pressure by height. Tank hardware is `water-tanks.md`.

A supply is not reliable while it has demand-shorting fluctuations, neglected equipment, a poor pump arrangement, a bad installation, recurring impairments, a slow impairment response, or an unmitigated natural hazard (§2.1.1.3).

## Enhanced ladder

Enhanced means the minimum reliable supply plus a secondary source (§2.1.2).

| Rank | Arrangement | What it is |
| --- | --- | --- |
| A | Two or more sources, physically separate, each adequate, no shared impairment | Separate public taps, or a public main plus independent on-site storage with its own suction |
| B | Two adequate sources that share an impairment | Electric and diesel pumps on one tank |
| C | One source with internal redundancy | An electric pump on municipal power plus a generator |
| D | A secondary source that is reliable and not fully adequate | A partial backup |

Electric plus diesel on a common tank is rank B. It is not rank A. NFPA 13, 20, and 24 require a reliable supply. They do not publish this order or this ladder. Report the extra source, the stored volume, the loop sectionalizing, or the generator-backed pump power as insurer or owner above the code floor.

Power is unreliable, on the FM pump sheet, when disruptions last longer than 8 hours three or more times in 12 months, and when short outages are frequent (FM DS 3-7 §2.4.12.2). Use that test when rank C is in play. The installation consequences are `fire-pump-installation.md`.

Wildland exposure without a well-gridded public supply is an Appendix C driver, not a new ladder (FM DS 9-19 §2.6, interim January 2024). Earthquake impairment is the same kind of driver (FM DS 1-11 §1.1, July 2016 / interim April 2025). The hardware for keeping the private system standing is `post-earthquake-supply.md` and `seismic-bracing.md`.

Do not cite DS 3-29 for a gallon demand or a pump count.
