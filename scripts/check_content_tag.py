#!/usr/bin/env python3
"""Refuse to publish a content-v* tag unless its commit is on main and the repository's owner pushed it.

.github/workflows/content-pack.yml runs this first, before anything is tested, built, or published, after
fetching main into refs/remotes/origin/main. Any finding fails the publish job:

  * the tag is not named like content-v0.6.0;
  * the tag's commit is not on main (an ancestor of main's tip, or the tip itself). A tag pushed on a branch
    that was never merged, or on a commit main no longer holds, publishes nothing;
  * the tag's version is not above every earlier content-v* tag, so the feed never goes back a version;
  * the tag was pushed by someone other than the repository's owner. The owner and the account that pushed
    are both required: a check that is not told who the owner is refuses the tag.

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


def _version(tag: str) -> tuple[int, ...] | None:
    """The numbers of a content tag's version, or None for a tag not named like content-v0.6.0."""
    if not TAG.match(tag or ""):
        return None
    return tuple(int(part) for part in tag[len("content-v"):].split("."))


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def _highest_on_main(where: Path, tag: str, tip: str) -> tuple[tuple[int, ...], str] | None:
    """The highest content-v* tag other than this one whose commit is on main: the latest a pack could be from."""
    best = None
    for name in _git(where, "tag", "-l", "content-v*").stdout.split():
        numbers = _version(name)
        if name == tag or numbers is None:
            continue
        commit = _git(where, "rev-parse", "--verify", "--quiet", f"refs/tags/{name}^{{commit}}")
        if commit.returncode != 0:
            continue
        if _git(where, "merge-base", "--is-ancestor", commit.stdout.strip(), tip).returncode != 0:
            continue  # a tag off main never published, so it sets no floor
        if best is None or numbers > best[0]:
            best = (numbers, name)
    return best


def tag_problems(tag: str, main_ref: str, *, actor: str, owner: str, cwd: Path | None = None) -> list[str]:
    """What stops this tag from publishing. Empty when it may."""
    where = Path(cwd) if cwd is not None else Path.cwd()
    found: list[str] = []
    mine = _version(tag)
    if mine is None:
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
        if mine is not None:
            highest = _highest_on_main(where, tag, tip.stdout.strip())
            if highest is not None and mine <= highest[0]:
                found.append(f"The tag {tag} is not above {highest[1]}, which is already on main. A content pack is "
                             "published only with a version above every earlier one, so the feed never goes back.")
    if not owner:
        found.append("The repository owner is not named, so the check cannot tell who may publish.")
    elif actor != owner:
        found.append(f"The tag was pushed by {actor or 'an unnamed account'}. Only the repository owner, {owner}, publishes content.")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refuse a content-v* tag that is not on main")
    parser.add_argument("--tag", required=True, help="The tag's name, such as content-v0.6.0")
    parser.add_argument("--main-ref", default="refs/remotes/origin/main", help="The ref that holds main's tip")
    parser.add_argument("--actor", required=True, help="The account that pushed the tag")
    parser.add_argument("--owner", required=True, help="The repository owner, the one account that may publish")
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
