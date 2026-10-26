# skills

One folder per design method: `skills/<slug>/SKILL.md`.

Each file starts with YAML frontmatter (`name`, `description`) and then the method. The desktop app lists these files from the content pack and gives Claude a `read_skill` tool. Do not paste the method into the application.

Keep section numbers, edition years, and the numeric screens. Do not add roster or orchestration language, job names, client names, or personal names. Do not commit raw NFPA text or a vendor catalog. A downloaded content pack can replace this folder as long as the `skills/<slug>/SKILL.md` layout stays.

Tier A methods in this folder:

- `suppression-technology-selection`
- `occupancy-hazard-fork`
- `most-stringent-basis-matrix`
- `density-area-dry-increase`
- `sprinkler-system-volume-takeoff`
- `dry-preaction-water-delivery-screen`
- `nitrogen-inerting-and-c-factor-gate`
- `preaction-releasing-c-and-e-soo`
- `preaction-el-el-trim-election`
- `multizone-preaction-zone-alignment`
- `fa-double-interlock-releasing-cause-and-effect`
- `fa-releasing-panel-standby-and-power-split`
- `fa-secondary-power-battery-calc`
- `fa-asd-vewfd-data-hall-sampling-layout`
- `fa-two-level-detection-stagger-and-fm-mapping`
- `fa-fire-pump-and-preaction-supervisory-points`
- `containment-ceiling-and-obstruction-coverage`
- `blind-claim-check`

Tier B methods in this folder (v1, after Tier A). Tier C is not in this pack:

- `hydrant-supply-curve`
- `pump-envelope`
- `fire-pump-controller-configuration-and-supervision`
- `fp-seismic-bracing-and-restraint`
- `campus-looped-main-sizing`
- `needed-fire-flow-method-election`
- `standpipe-class-i-election-and-demand`
- `freeze-heat-trace-fp-piping`
- `itm-design-for-testability`
- `commissioning-ist-acceptance-packet`
- `fa-integrated-systems-test-matrix`
- `fa-nac-voltage-drop-check`
- `fa-speaker-circuit-loss-check`
- `fa-nec-table-8-wire-sizing`
- `fa-pathway-survivability-election`
- `fa-code-edition-delta-check`
- `fa-spot-smoke-spacing-airflow-and-beams`
- `fa-supervising-station-signal-schedule`
- `fa-voice-evac-ads-audibility-screen`
- `fa-hvac-door-and-lock-interfaces`
- `fa-elevator-recall-and-shunt-trip`
- `power-isolation-disconnect-control`
- `fire-area-compartmentation-schedule`
- `combustion-air-and-hall-free-area`

The double-interlock zone screen asks for these slugs when they are present:

- `sprinkler-system-volume-takeoff`
- `dry-preaction-water-delivery-screen`
- `preaction-el-el-trim-election`
- `preaction-releasing-c-and-e-soo`
- `fa-double-interlock-releasing-cause-and-effect`
- `nitrogen-inerting-and-c-factor-gate`
- `density-area-dry-increase`
- `multizone-preaction-zone-alignment` (listed for the model; the one-zone screen does not walk it)
