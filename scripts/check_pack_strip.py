#!/usr/bin/env python3
"""Strip scan over every folder a content pack ships.

The scan reads skills, calcs, corpus, specs, modes, and roles and reports:

  * job, client, and place names. The banned list is the one in calcs/fp/place_name_scan.py, whose
    spellings are assembled at runtime. Every relative path component is checked, directories and
    file names alike, and a hit there is always reported. A name inside a file may stay only where
    scripts/strip_scan_baseline.json records the exact count for that file. The baseline covers
    in-file counts only. A new hit, a missing baseline entry, or a count that has shrunk is
    reported, so the baseline cannot drift quietly;
  * QA ids in any spelling, including those with letters between the dash and the digits, and batch
    or round-standard tags, in file text and in every path component;
  * a path component that names clean-agent or foam content, and a path component named canada or
    canadian, which the pack builder would otherwise drop without a message.

This is a phrase and name guard. It is not an engineering review and it does not read meaning.
Exit status is 0 when nothing is reported and 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[1]
SHIPPED_TOPS = ("skills", "calcs", "corpus", "specs", "modes", "roles")
BASELINE_PATH = Path(__file__).resolve().parent / "strip_scan_baseline.json"
_TEXT_SUFFIXES = {".py", ".md", ".json", ".txt", ".yml", ".yaml", ".csv", ".toml"}

sys.path.insert(0, str(REPO / "calcs" / "fp"))
from place_name_scan import banned_pattern  # noqa: E402

# Baseline classes. A name is identified by the first six hex digits of the sha1 of its lowercase
# spelling, so this file does not spell the names it tolerates. A class that is not listed here is
# never tolerated.
_CLASS_BY_ID = {
    "290572": "insurer-name",
    "368bd8": "province-name",
    "cc9139": "province-name",
}

_TAG_PATTERNS = (
    ("QA tag", re.compile(r"(?<![A-Za-z0-9])qa-?(?:ex-?)?\d+", re.IGNORECASE)),
    ("batch or round tag", re.compile(r"\bbatch ?\d+\b|ROUND-STANDARD|BATCH-PROCESS", re.IGNORECASE)),
)
_SCOPE_PREFIXES = ("clean-agent", "clean_agent", "cleanagent", "foam")
_CANADA_NAMES = frozenset({"canada", "canadian"})


def name_class(word: str) -> str | None:
    """Baseline class for a banned spelling, or None when it may never be tolerated."""
    return _CLASS_BY_ID.get(hashlib.sha1(word.lower().encode("utf-8")).hexdigest()[:6])


def load_baseline(path: Path = BASELINE_PATH) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {rel: dict(classes) for rel, classes in data["counts"].items()}


def _pack_files(root: Path):
    for top in SHIPPED_TOPS:
        folder = root / top
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if "__pycache__" in path.parts or path.is_symlink() or not path.is_file():
                continue
            yield path, path.relative_to(root).as_posix()


def path_findings(root: Path) -> list[str]:
    """Path components the builder or installer would drop, or that name out-of-scope content."""
    found: list[str] = []
    root = Path(root)
    for top in SHIPPED_TOPS:
        folder = root / top
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            rel = path.relative_to(root)
            for index, part in enumerate(rel.parts):
                lowered = part.casefold()
                stem = lowered.rsplit(".", 1)[0] if "." in lowered else lowered
                shown = "/".join(rel.parts[: index + 1])
                if lowered.startswith(_SCOPE_PREFIXES):
                    found.append(f"{shown} (clean-agent or foam name; out of scope)")
                    break
                if lowered in _CANADA_NAMES or stem in _CANADA_NAMES:
                    found.append(f"{shown} (the builder drops a canada-named path; gate Canada text inside a skill)")
                    break
    return found


def _component_findings(rel: str, banned: re.Pattern[str]) -> list[str]:
    """Banned names and tags in each component of a pack-relative path.

    A hit names the path through that component and the kind of hit. These are not in-file
    counts, so the baseline never covers them.
    """
    found: list[str] = []
    parts = PurePosixPath(rel).parts
    last = len(parts) - 1
    for index, part in enumerate(parts):
        shown = "/".join(parts[: index + 1])
        where = "file name" if index == last else "directory name"
        if banned.search(part):
            found.append(f"{shown} ({where} carries a banned name)")
        for label, pattern in _TAG_PATTERNS:
            if pattern.search(part):
                found.append(f"{shown} ({where} carries a {label})")
    return found


def strip_findings(root: Path, baseline: dict | None = None) -> list[str]:
    """Findings for the tree under root. baseline maps a file to {class: exact in-file count}."""
    root = Path(root)
    expected = load_baseline() if baseline is None else baseline
    banned = banned_pattern()
    found: list[str] = []
    noted: set[str] = set()
    seen: dict[str, dict[str, int]] = {}
    for path, rel in _pack_files(root):
        # Path hits go straight to the report. The baseline counts text inside a file only.
        for line in _component_findings(rel, banned):
            if line not in noted:
                noted.add(line)
                found.append(line)
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for match in banned.finditer(line):
                cls = name_class(match.group(0))
                if cls is None:
                    found.append(f"{rel}:{number} (job, client, or place name)")
                else:
                    counts = seen.setdefault(rel, {})
                    counts[cls] = counts.get(cls, 0) + 1
            for label, pattern in _TAG_PATTERNS:
                if pattern.search(line):
                    found.append(f"{rel}:{number} ({label})")
    for rel, counts in sorted(seen.items()):
        for cls, count in sorted(counts.items()):
            allowed = expected.get(rel, {}).get(cls)
            if allowed is None:
                found.append(f"{rel} ({count} {cls} hits, none in the baseline)")
            elif allowed != count:
                found.append(f"{rel} ({count} {cls} hits, baseline says {allowed}; review, then update the baseline)")
    for rel, classes in sorted(expected.items()):
        if not (root / rel).is_file():
            continue  # a file that is not in this tree cannot hide a hit
        for cls, allowed in sorted(classes.items()):
            if seen.get(rel, {}).get(cls, 0) == 0 and allowed:
                found.append(f"{rel} (baseline lists {allowed} {cls} hits, found 0; update the baseline)")
    return found


def all_findings(root: Path, baseline: dict | None = None) -> list[str]:
    return path_findings(root) + strip_findings(root, baseline)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strip scan over the folders a content pack ships")
    parser.add_argument("--root", default=str(REPO), help="Content checkout to scan")
    parser.add_argument("--baseline", default=str(BASELINE_PATH), help="Reviewed baseline of tolerated name counts")
    args = parser.parse_args(argv)
    findings = all_findings(Path(args.root), load_baseline(Path(args.baseline)))
    for line in findings:
        sys.stdout.write(line + "\n")
    if findings:
        sys.stderr.write(f"strip scan: {len(findings)} finding(s)\n")
        return 1
    sys.stdout.write("strip scan: clean\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
