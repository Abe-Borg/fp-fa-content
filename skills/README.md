# skills

One folder per design method: `skills/<slug>/SKILL.md`.

Each file starts with YAML frontmatter (`name`, `description`) and then the method. The desktop app lists these files from the content pack and gives Claude a `read_skill` tool. Do not paste the method into the application.

Keep section numbers, edition years, and the numeric screens. Do not add roster or orchestration language, job names, client names, or personal names. Do not commit raw NFPA text or a vendor catalog. A downloaded content pack can replace this folder as long as the `skills/<slug>/SKILL.md` layout stays.

The double-interlock workflow asks for these slugs when they are present:

- `sprinkler-system-volume-takeoff`
- `dry-preaction-water-delivery-screen`
- `preaction-el-el-trim-election`
- `preaction-releasing-c-and-e-soo`
- `fa-double-interlock-releasing-cause-and-effect`
- `nitrogen-inerting-and-c-factor-gate`
- `density-area-dry-increase`
- `multizone-preaction-zone-alignment` (loaded for the model; the one-zone screen does not walk it)
