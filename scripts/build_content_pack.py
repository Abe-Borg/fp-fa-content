#!/usr/bin/env python3
"""Build a versioned content zip and manifest.json.

The zip includes skills, calcs, corpus, specs, modes, and roles.
It omits the app, project files, API keys, _sources, and foam,
clean-agent, Canada, and vendor-catalog paths.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "app"))

from fpfa.content_pack import ContentPackError, build_pack  # noqa: E402


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
    try:
        built = build_pack(
            Path(args.source),
            Path(args.out),
            args.version,
            changelog=_notes(args.changelog, args.changelog_file),
            created=args.created or None,
        )
    except ContentPackError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1
    for rel in built.stripped:
        sys.stderr.write(f"stripped {rel}\n")
    sys.stdout.write(f"wrote {built.zip_path}\n")
    sys.stdout.write(f"manifest {built.manifest_path}\n")
    sys.stdout.write(f"sha256 {built.manifest['sha256']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
