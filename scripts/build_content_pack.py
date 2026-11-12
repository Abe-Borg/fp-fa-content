#!/usr/bin/env python3
"""Build a versioned content zip and manifest.json.

The zip includes skills, calcs, corpus, specs, modes, and roles.
It omits the app, project files, API keys, _sources, and vendor-catalog
paths. A foam or clean-agent path stops the build. A Canada-named path is
packed under its own name: Canada is in scope through a skill's Country gate.

Before packing, this script runs the strip scan (scripts/check_pack_strip.py) and stops with a
message on any finding: a job, client, or place name outside the reviewed baseline, a QA or batch
tag, or a clean-agent or foam name in a path. It then packs a staged copy that leaves out
calcs/fp/draft/, the held and unwired draft, so that folder is not in the zip. The builder in
app/fpfa/content_pack.py also leaves that folder out and refuses the same scope prefixes, so the
app's seed copy and installer follow the same rules.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fpfa.content_pack import ALLOWED_TOP, ContentPackError, build_pack  # noqa: E402
import check_pack_strip  # noqa: E402

# Left out of the zip: held, unwired, and not part of the shipped calculators.
HELD_PATHS = ("calcs/fp/draft",)


def preflight(source: Path) -> None:
    """Stop with a message when the tree breaks a ship rule. Nothing is dropped silently."""
    findings = check_pack_strip.all_findings(source)
    if findings:
        shown = "\n".join(f"  {line}" for line in findings[:40])
        more = f"\n  ... and {len(findings) - 40} more" if len(findings) > 40 else ""
        raise ContentPackError(f"strip scan found {len(findings)} problem(s):\n{shown}{more}")


def stage_source(source: Path, dest: Path) -> list[str]:
    """Copy the packed folders to dest without the held paths. Return the paths left out."""
    held = {source / rel for rel in HELD_PATHS}

    def ignore(folder: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name == "__pycache__" or (Path(folder) / name) in held
        }

    for top in ALLOWED_TOP:
        folder = source / top
        if folder.is_dir():
            shutil.copytree(folder, dest / top, symlinks=True, ignore=ignore)
    return [rel for rel in HELD_PATHS if (source / rel).exists()]


def _notes(changelog: list[str], changelog_file: str) -> list[str]:
    lines: list[str] = []
    if changelog_file:
        path = Path(changelog_file)
        if not path.is_file():
            raise ContentPackError(f"changelog file not found: {path}")
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    lines.extend(changelog)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a content pack zip and manifest.json")
    parser.add_argument("--version", required=True, help="Numbered version, such as 2026.10.1")
    parser.add_argument("--out", required=True, help="Directory for the zip and manifest.json")
    parser.add_argument("--source", default=str(REPO), help="Content checkout to pack")
    parser.add_argument("--changelog", action="append", default=[], help="Changelog line (repeatable)")
    parser.add_argument("--changelog-file", default="", help="Text file of changelog lines")
    parser.add_argument("--created", default="", help="ISO timestamp; default is the current UTC time")
    args = parser.parse_args(argv)
    source = Path(args.source)
    try:
        preflight(source)
        notes = _notes(args.changelog, args.changelog_file)
        with tempfile.TemporaryDirectory() as tmp:
            staged = Path(tmp) / "pack"
            staged.mkdir()
            held = stage_source(source, staged)
            built = build_pack(
                staged,
                Path(args.out),
                args.version,
                changelog=notes,
                created=args.created or None,
            )
    except ContentPackError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1
    for rel in held:
        sys.stderr.write(f"left out {rel} (held, unwired)\n")
    for rel in built.stripped:
        sys.stderr.write(f"stripped {rel}\n")
    sys.stdout.write(f"wrote {built.zip_path}\n")
    sys.stdout.write(f"manifest {built.manifest_path}\n")
    sys.stdout.write(f"sha256 {built.manifest['sha256']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
