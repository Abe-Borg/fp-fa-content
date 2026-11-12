"""Read stable app releases without installing anything or changing the content pack."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from fpfa import __version__
from fpfa.about import APP_NAME, PROJECT_URL

RELEASES_API = "https://api.github.com/repos/Abe-Borg/fp-fa-content/releases"
PAGE_SIZE = 100
MAX_PAGES = 10
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 10
_VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+", re.ASCII)


@dataclass(frozen=True)
class AppUpdateResult:
    status: str
    message: str
    version: str = ""
    download_url: str = ""


def _numbers(version: str) -> tuple[int, ...]:
    if not _VERSION.fullmatch(version):
        raise ValueError("Invalid app version")
    return tuple(int(part) for part in version.split("."))


def _release_page(page: int) -> list[dict]:
    request = urllib.request.Request(
        f"{RELEASES_API}?per_page={PAGE_SIZE}&page={page}",
        headers={
            "User-Agent": "Cynosure-app-update",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    # This request carries no API key, project data, or saved content-feed settings.
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Release response too large")
    releases = json.loads(raw)
    if not isinstance(releases, list) or any(not isinstance(item, dict) for item in releases):
        raise ValueError("Invalid release response")
    return releases


def check_for_app_update() -> AppUpdateResult:
    """Compare numeric app versions across pages, ignoring content and preview releases."""
    try:
        local = _numbers(__version__)
        latest: tuple[tuple[int, ...], str] | None = None
        for page in range(1, MAX_PAGES + 1):
            releases = _release_page(page)
            for release in releases:
                tag = release.get("tag_name")
                if not isinstance(tag, str) or not tag.startswith("app-v"):
                    continue
                published_flags = dict(draft=False, prerelease=False)
                if any(release.get(flag) is not expected for flag, expected in published_flags.items()):
                    continue
                version = tag.removeprefix("app-v")
                if not _VERSION.fullmatch(version):
                    continue
                numbers = _numbers(version)
                if latest is None or numbers > latest[0]:
                    latest = (numbers, version)
            if len(releases) < PAGE_SIZE:
                break
        else:
            # A truncated history cannot establish which app version is newest.
            return AppUpdateResult("error", "Couldn’t finish checking app releases. Try again later.")
        if latest is None:
            return AppUpdateResult("unavailable", "No stable app release is available yet.")
        numbers, version = latest
        if numbers > local:
            return AppUpdateResult(
                "available",
                f"{APP_NAME} {version} is available. You have {__version__}.",
                version,
                f"{PROJECT_URL}/releases/tag/app-v{version}",
            )
        if numbers == local:
            message = f"You’re up to date. {APP_NAME} {__version__} is the latest version."
        else:
            message = f"Your version ({__version__}) is newer than the latest release ({version})."
        return AppUpdateResult("current", message, version)
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 429}:
            message = "The release service is limiting requests. Try again later."
        elif exc.code == 404:
            message = "Couldn’t access app releases. The repository may be private or unavailable."
        else:
            message = "Couldn’t read app releases. Try again later."
    except (urllib.error.URLError, TimeoutError, OSError):
        message = "Couldn’t check for updates. Check your connection and try again."
    except (ValueError, TypeError):
        message = "Couldn’t read the app release information. Try again later."
    return AppUpdateResult("error", message)
