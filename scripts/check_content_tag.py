#!/usr/bin/env python3
"""Refuse to publish a content-v* tag unless its commit is on main and the repository's owner pushed it.

.github/workflows/content-pack.yml runs this first, before anything is tested, built, or published, after
fetching main into refs/remotes/origin/main. Any finding fails the publish job:

  * the tag is not named like content-v0.6.0;
  * the tag's commit is not on main (an ancestor of main's tip, or the tip itself). A tag pushed on a branch
    that was never merged, or on a commit main no longer holds, publishes nothing;
  * the tag was pushed by someone other than the repository's owner, when both names are given.

It reads git and nothing else. It does not decide what a pack holds; the strip scan and the builder do that.
Exit status is 0 when the tag may publish and 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TAG = re.compile(r"^content-v\d+(?:\.\d+)+$")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def tag_problems(tag: str, main_ref: str, *, actor: str = "", owner: str = "", cwd: Path | None = None) -> list[str]:
    """What stops this tag from publishing. Empty when it may."""
    where = Path(cwd) if cwd is not None else Path.cwd()
    found: list[str] = []
    if not TAG.match(tag or ""):
        found.append(f"{tag!r} is not a content tag. A content tag looks like content-v0.6.0.")
    commit = _git(where, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
    tip = _git(where, "rev-parse", "--verify", "--quiet", f"{main_ref}^{{commit}}")
    if commit.returncode != 0:
        found.append(f"The tag {tag} is not in this checkout.")
    elif tip.returncode != 0:
        found.append(f"{main_ref} is not in this checkout. Fetch main before this check.")
    else:
        sha = commit.stdout.strip()
        ancestor = _git(where, "merge-base", "--is-ancestor", sha, tip.stdout.strip())
        if ancestor.returncode == 1:
            found.append(f"The tag {tag} points at {sha}, which is not on main. A content pack is published only from main.")
        elif ancestor.returncode != 0:
            found.append(f"git could not compare {sha} with main: {ancestor.stderr.strip()[:200]}")
    if owner and actor != owner:
        found.append(f"The tag was pushed by {actor or 'an unnamed account'}. Only the repository owner, {owner}, publishes content.")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refuse a content-v* tag that is not on main")
    parser.add_argument("--tag", required=True, help="The tag's name, such as content-v0.6.0")
    parser.add_argument("--main-ref", default="refs/remotes/origin/main", help="The ref that holds main's tip")
    parser.add_argument("--actor", default="", help="The account that pushed the tag")
    parser.add_argument("--owner", default="", help="The repository owner. When given, only that account may publish")
    args = parser.parse_args(argv)
    problems = tag_problems(args.tag, args.main_ref, actor=args.actor, owner=args.owner)
    for line in problems:
        sys.stdout.write(f"::error::{line}\n")
    if problems:
        return 1
    sys.stdout.write(f"{args.tag} is on main. It may publish.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
