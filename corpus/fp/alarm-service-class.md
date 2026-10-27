# FM alarm service class and watch

FM DS 5-32 requires fire-alarm supervision at FM DS 9-1 Class V or greater. FM service classes are not NFPA 72 pathway classes. Specify both (`../fa/pathway-class.md` and `../fa/supervising-station.md`).

FM DS 9-1 (April 2017 / interim January 2021) §2.3.6.3 sets Class V as the minimum when the site is not occupied around the clock and has no recorded tours.

Appendix C, Class V: waterflow is supervised to an FM Approved central station, a constantly attended proprietary station, or a constantly attended public fire desk. Class V does not require valve, tank, or pump supervision.

Class VIA adds supervision of valves larger than 1 in. or serving more than 5 sprinklers, plus dry-pipe pressure, pumps, and tank level. The Class VIA line that prints 38 mm as the metric of 1 in. does not match. Do not hard-code 38 mm. Use 1 in. and confirm the sheet.

An FM Approval Standard 3011 placard is required for the central-station path the class describes. Without it, an otherwise central-station path is Class IV on that appendix.

Tours of unoccupied areas are hourly. Occupied business hours are twice hourly, starting within a half hour after the area empties (§3.1.5). Tours may drop to one per shift where video and electronic surveillance exist (§3.1.5). Video does not replace a required recorded tour. Retain video at least 90 days (§2.3.7.2). A dead-bolt throw of at least 1 in. is §2.3.2.1. That hardware line is premises security, not a sprinkler calculation.

Waterflow on Class V, and the extra points on Class VIA, line up with the device rules in `waterflow-supervision.md`.
