# roles

One folder per specialist role: `roles/<slug>/ROLE.md`.

Each file starts with YAML frontmatter (`name`, `description`) and then the role prompt. The desktop everyday path loads `roles/everyday/ROLE.md` as the chat shell and lists the other roles. The model reads a specialist with the `read_role` tool, the same way it reads `skills/<slug>/SKILL.md` with `read_skill`. Do not paste the role into the application.

`README.md` is this guide and is not a role.

Roles in this pack:

- `everyday` — shell for a typed question
- `fp-sprinkler` — wet, dry, and double-interlock sprinkler screens, plus the outdoor transformer water-spray exception in `power-block-transformer-water-spray`
- `fa-releasing` — detection and releasing that trip those systems
- `spec-draft` — narrative after a tool-plan run, including section 21 13 19
- `qa-specialist` — blind claim check before that section is exported

Mode behavior lives next to this folder in `modes/<slug>/MODE.md` (brainstorm, calculator, synthesis, mixed). These role files do not switch modes. Keep section numbers that the app already uses. Do not add job names, client names, personal names, raw standards text, or a vendor catalog.
