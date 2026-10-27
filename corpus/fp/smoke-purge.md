# Smoke purge and hall airflow

A single-story hall usually has no IBC §909 system (`../fa/smoke-control-interface.md`). Stair pressurization, when a stair exists, is `stair-pressurization.md`. This note is dilution after the fire, and what aisle velocity does to detectors.

Purge time follows outside air and exhaust, not recirculation. A hall at several hundred air changes per hour of fan-wall flow, with a small outside-air fraction, purges at the outside-air rate. The dilution form, after smoke production has stopped, is t = (1 / a) × ln(C₀ / C), with a in air changes per minute. At 6 air changes per hour, a is 0.1 per minute, and the time to 1 percent of the initial concentration is about 46 minutes. That 1 percent figure is an obscuration criterion from the source paper. It is not a toxicity or re-entry limit.

The same source states that there is no demonstrated tenability benefit from using the building air system to dilute smoke inside the fire space. Purge is a recovery tool and an adjacent-space tool. The clock starts when smoke production stops. Starting exhaust on the first alarm, while the fire is still burning, solves a different problem. Gaseous agent is out of scope. Exhaust that would have broken a gaseous hold is not a design path here.

Shutting the fans down does not stop smoke movement driven by stack effect, buoyancy, or wind. Doing nothing lets the air system carry smoke to every zone it serves. Write the fan and damper response even when no smoke-control system is required (`duct-smoke.md`, `dampers.md`).

A zone-dependent smoke mode is not started from a duct detector or a manual station. Those devices do not know the zone. Stair pressurization is the opposite case: any device may start it (`stair-pressurization.md`).

Aisle airflow above the critical velocity for a small fire leaves an upstream detector in clean air until the fire is large. For a 4 ft aisle near 300 ft/min, the upstream null persists until the fire is on the order of 170 kW. That figure is closed-form arithmetic from the aisle geometry. It is not a code threshold. Place detection on the downstream and return path. A cross-zone that needs an upwind detector may never complete. Hall sampling layout is `../fa/detection-layout.md`. Ceiling velocity limits on an FM hall are `hall-geometry.md`.

FM DS 5-32 does not want an automatically operated smoke-exhaust system in a data-processing room. Where the adopted code requires automatic operation, interlock it to the sprinkler alarm (`exhaust-ducts.md`).

The detection method is `fa-asd-vewfd-data-hall-sampling-layout`. The HVAC interface is `fa-hvac-door-and-lock-interfaces`.
