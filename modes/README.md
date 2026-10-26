# modes

One folder per everyday-path mode: `modes/<slug>/MODE.md`.

Each file starts with YAML frontmatter (`name`, `description`) and then the mode behavior. The desktop everyday path loads the active mode file into the chat turn and lists the other modes. The model reads another mode with the `read_mode` tool, the same way it reads `roles/<slug>/ROLE.md` with `read_role`. Do not paste the mode into the application.

`README.md` is this guide and is not a mode.

Modes in this pack:

- `brainstorm` — explore options; do not lock a draft section
- `calculator` — quote calc-tool figures
- `synthesis` — draft narrative after a tool-plan run, section 21 13 19, including an explosion-control starter after the LFL tool plan
- `mixed` — explore, calculate, and draft in one reply, with the labels kept apart

Three labels stay distinct in every mode. Pipe gallons and t_total are calculated. ASSUMED stays on blank trim and on the screen-limit lookup. A value the designer types is not assumed. A designer judgment the tools did not return is use best judgment. A delivery time from the dry or double-interlock screen is an optimistic screen, not a listed water-delivery-time calculation.

Keep the section string the app already uses for this export. Do not add job names, client names, personal names, raw standards text, or a vendor catalog.
