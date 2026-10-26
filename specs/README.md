# specs

Master specification language as markdown, one section per file.

The desktop app appends `specs/*.md` to the model prompt (up to three files, and only the first portion of each) so a content pack can steer draft wording. `README.md` is this guide and is not treated as a spec.

Anything the model writes from these notes is still a draft. The engineer of record verifies it before it is issued. Do not put an API key, a job name, or a vendor catalog in this folder. Numeric design values in an issued section come from `calcs/`, not from prose stored here.
