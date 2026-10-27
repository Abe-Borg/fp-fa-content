# corpus

Paraphrased decision logs and edition pins for a later search pass. One topic per file. The desktop app does not read this folder yet.

The training-tree knowledge base was not in this checkout. These notes are the in-scope decision logs distilled from the v1 skills already in the pack, not a copy of a source archive. They are not a reprint of a standard. A numeric screen sits next to its edition and section. Where a licensed primary is not held, the note says `[V]` and does not invent a section.

Out of this folder: raw standards text, vendor catalogs, source-pull archives, job names, client names, and personal names. Foam, clean agent, and water mist are out of scope (the guard is in `scope-lock.md` only). A building deluge system is out of scope. Outdoor oil-filled transformer apparatus water spray (NFPA 15-style) is allowed and is sized in `power-block-transformer-water-spray`. Jurisdictions outside the stated NFPA, IBC, and IFC basis are out of scope. Canada stays out of scope. Single-interlock and non-interlock preaction are comparison-only. They are never the basis of design.

Company systems in these notes: wet pipe, dry pipe, and double-interlock preaction, outdoor oil-filled transformer apparatus water spray, plus pumps, nitrogen, compressors, and the Division 21 and Division 28 fire-alarm work those systems need.

Spec language is not here. When specs are ingested, double-interlock draft language belongs in CSI 21 13 19.

| File | What it holds | Skill to read for the method |
| --- | --- | --- |
| `scope-lock.md` | Wet / dry / double-interlock fence, plus outdoor transformer water spray | `suppression-technology-selection`, `power-block-transformer-water-spray` |
| `fp/edition-pins.md` | Unamended 2024 I-Code reference pins | `most-stringent-basis-matrix` |
| `fp/water-delivery-screen.md` | Volume caps and 60 s / 30 s clocks | `dry-preaction-water-delivery-screen` |
| `fp/nitrogen-compressor-and-c-factor.md` | C = 100, two-number fill | `nitrogen-inerting-and-c-factor-gate` |
| `fp/pipe-volume.md` | Trapped-volume takeoff | `sprinkler-system-volume-takeoff` |
| `fp/density-area.md` | Dry/DI area fork, do not stack | `density-area-dry-increase` |
| `fp/pump-and-supply.md` | Supply curve and pump envelope | `hydrant-supply-curve`, `pump-envelope` |
| `fp/fire-pump-controller.md` | Controller signals and refuse list | `fire-pump-controller-configuration-and-supervision` |
| `fp/preaction-trim-and-sequence.md` | Trim collision and releasing sequence | `preaction-el-el-trim-election`, `preaction-releasing-c-and-e-soo` |
| `fp/standpipe-class-i.md` | Class I residual and supervisory air | `standpipe-class-i-election-and-demand` |
| `fp/itm-testability.md` | CD testability levers | `itm-design-for-testability` |
| `fp/freeze-heat-trace.md` | Freeze screen, listing fence | `freeze-heat-trace-fp-piping` |
| `fp/seismic-bracing.md` | Brace spacing ceiling | `fp-seismic-bracing-and-restraint` |
| `fp/campus-loop-and-fire-flow.md` | Loop and needed-fire-flow method | `campus-looped-main-sizing`, `needed-fire-flow-method-election` |
| `fa/di-releasing.md` | Double-interlock cause and effect | `fa-double-interlock-releasing-cause-and-effect` |
| `fa/secondary-power.md` | Standby hours and aging factor | `fa-secondary-power-battery-calc` |
| `fa/nac-and-wire.md` | NAC drop method, Table 8 cite | `fa-nac-voltage-drop-check`, `fa-nec-table-8-wire-sizing` |
| `fa/detection-layout.md` | Spot smoke, ASD sampling, two levels | `fa-spot-smoke-spacing-airflow-and-beams`, `fa-asd-vewfd-data-hall-sampling-layout` |
| `fa/interfaces.md` | Elevator, HVAC, power isolation, signals | `fa-elevator-recall-and-shunt-trip`, `power-isolation-disconnect-control` |
