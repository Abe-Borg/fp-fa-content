# roles

One folder per specialist role: `roles/<slug>/ROLE.md`.

Each file starts with YAML frontmatter (`name`, `description`) and then the role prompt. Do not paste a role into the application.

How the application uses them:

- A chat turn on a job is the lead of a team. `roles/lead/ROLE.md` is its system text. It delegates to the specialists and does not answer in their place. A pack without that file falls back to `roles/everyday/ROLE.md` with a short team paragraph the application adds.
- A specialist's `ROLE.md` is the system text of its own context when the lead delegates to it, or when another specialist asks it something with `consult`. The section "Working with the team" in a specialist's file says what it owns, what it needs from the other discipline, and which of the other's findings it reviews. Keep that section when you edit the file: it is what makes two specialists one design basis.
- A chat with no project record (the plain tool loop) loads `roles/everyday/ROLE.md` as the shell and lists the other roles. The model reads one with the `read_role` tool, the same way it reads `skills/<slug>/SKILL.md` with `read_skill`.

`README.md` is this guide and is not a role.

Roles in this pack:

- `lead` — the designer's one point of contact: owns the objective, delegates, makes the specialists reconcile, runs the trace check, answers
- `everyday` — shell for a typed question when no team is running
- `fp-sprinkler` — wet, dry, and double-interlock sprinkler screens, plus the outdoor transformer water-spray exception in `power-block-transformer-water-spray`
- `fa-releasing` — detection and releasing that trip those systems
- `spec-draft` — narrative after a tool-plan run, including section 21 13 19
- `qa-specialist` — blind claim check before that section is exported

Mode behavior lives next to this folder in `modes/<slug>/MODE.md` (brainstorm, calculator, synthesis, mixed). These role files do not switch modes. Keep section numbers that the app already uses. Do not add job names, client names, personal names, raw standards text, or a vendor catalog.
