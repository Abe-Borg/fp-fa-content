#!/usr/bin/env python3
"""Third-party license notices for the packaged app.

Adapted from Build-a-Spec's packaging/windows/third_party_notices.py (the
practice's copy-and-adapt reuse): the same strict posture, sized for this
app. The window is a web page shown in Microsoft's WebView2 through
pywebview, so the page's JavaScript and the WebView2 SDK that pywebview
carries are listed too. tkinter is not bundled (build_app.py excludes it).

Why this exists. The PyInstaller build bundles the Python interpreter, every
Python package the app imports with its dependencies, and the built page.
Their licenses (PSF, MIT, BSD, Apache-2.0, and others) ask that their
copyright and license text travel with a binary. This module
writes one THIRD-PARTY-NOTICES.txt holding all of them. build_app.py puts it
in the app folder beside the exe, so the installer and the portable zip both
carry it. +Cynosure's own license ships beside it as LICENSE.txt.

What is listed.

* The packages named in app/requirements.txt and everything they require, as
  installed in the environment that runs the build. A requirement marked for
  another platform or for an optional extra is left out. This is the set
  PyInstaller draws from, so the list can name a package PyInstaller left
  out: a license listed for code that did not ship costs nothing, and one
  missing for code that did is a violation.
* PyInstaller, because its bootloader is the exe.
* The interpreter, from the LICENSE.txt in its install directory. On the
  python.org Windows build that file also carries the terms of the libraries
  the build ships (OpenSSL, bzip2, libffi).
* The Microsoft WebView2 SDK DLLs inside pywebview (webview/lib), at the
  version those DLLs report, from third_party_licenses/Microsoft.Web.WebView2-
  <version>.txt (the LICENSE.txt and NOTICE.txt of that NuGet package). The
  WebView2 runtime itself is part of Windows and is not bundled.
* The npm packages whose code is in the page, from fpfa/web/static/licenses.json,
  which the page's build (app/frontend/vite.config.ts) writes from node_modules.

It is strict. A listed package with no license text, an interpreter without
its license file, a WebView2 SDK without its text, or a page bundle whose
license list is missing or incomplete raises NoticesError
naming every gap at once, and no file is written. An installer that leaves a
license out must not ship. When a package really ships no license text, the
remedy is its text from that project's source at exactly that version, saved
as third_party_licenses/<name>-<version>.txt next to this file. The version
in the name makes an upgrade fail again until someone checks the new text.

Run it directly to check an environment before the long build:

    python packaging/third_party_notices.py --check
    python packaging/third_party_notices.py --out dist/THIRD-PARTY-NOTICES.txt
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import re
import sys
import sysconfig
from dataclasses import dataclass
from importlib import metadata
from typing import Iterable, Sequence

NOTICES_FILENAME = "THIRD-PARTY-NOTICES.txt"
APP_NAME = "+Cynosure"
# Listed whatever the requirements say: PyInstaller's bootloader is the exe.
ALWAYS_BUNDLED = ("pyinstaller",)

_PACKAGING_DIR = pathlib.Path(__file__).resolve().parent
_APP_DIR = _PACKAGING_DIR.parent
REQUIREMENTS = _APP_DIR / "requirements.txt"
# License texts for listed packages that ship none: <canonical name>-<version>.txt.
LICENSE_OVERRIDES_DIR = _PACKAGING_DIR / "third_party_licenses"

# Heading every CPython license file carries, so another LICENSE.txt is never passed off as Python's.
PSF_LICENSE_MARKER = "PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2"
# The page's bundled npm packages, written by its build.
PAGE_LICENSES = _APP_DIR / "fpfa" / "web" / "static" / "licenses.json"
# The WebView2 SDK's main DLL inside pywebview; its version names the license file.
WEBVIEW2_DLL = "webview/lib/Microsoft.Web.WebView2.Core.dll"

_LICENSE_NAME_RE = re.compile(r"^(licen[cs]e|copying|notice|copyright|authors)", re.IGNORECASE)
# A module named license.py is code, not a license text.
_NOT_TEXT_SUFFIXES = frozenset({".py", ".pyc", ".pyo", ".pyi", ".pyd", ".so", ".dll", ".dylib", ".exe"})
_REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
_RULE = "=" * 78


class NoticesError(RuntimeError):
    """One or more license texts could not be found. problems lists every gap."""

    def __init__(self, problems: Sequence[str]):
        self.problems = list(problems)
        super().__init__(
            "third-party notices cannot be written:\n" + "\n".join(f"  - {item}" for item in self.problems)
        )


@dataclass(frozen=True)
class LicenseText:
    source: str
    text: str


@dataclass(frozen=True)
class Component:
    name: str
    version: str
    license: str
    texts: tuple[LicenseText, ...]
    kind: str = "python"
    note: str = ""

    @property
    def title(self) -> str:
        return f"{self.name} {self.version}".strip()


def canonical_name(name: str) -> str:
    """PEP 503 normalization: Jaraco.Classes and jaraco_classes match."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _read_text(path: str | os.PathLike[str]) -> str | None:
    """File text with LF line endings; None when blank or unreadable."""
    try:
        data = pathlib.Path(path).read_bytes()
    except OSError:
        return None
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\n").rstrip()
    return text or None



def requirement_names(path: str | os.PathLike[str] = REQUIREMENTS) -> list[tuple[str, bool]]:
    """(package name, whether it must be installed) for each line of a requirements file.

    A line with an environment marker, such as one for Windows only, is left
    out where the marker does not hold. Where the marker cannot be evaluated
    the package is kept but not required.
    """
    names = []
    for raw in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        requirement, _, marker = line.partition(";")
        applies = _marker_applies(marker) if marker.strip() else True
        if applies is False:
            continue
        match = _REQUIREMENT_NAME_RE.match(requirement)
        if match:
            names.append((match.group(1), applies is True))
    return names


def _marker_class():
    """The Marker class of the packaging library, from wherever this environment has it."""
    for module in ("packaging.markers", "pip._vendor.packaging.markers"):
        try:
            return __import__(module, fromlist=["Marker"]).Marker
        except ImportError:
            continue
    return None


def _marker_applies(marker: str) -> bool | None:
    """Whether an environment marker holds here. None when it cannot be evaluated.

    A marker that names an optional extra never holds: the app installs none.
    """
    if re.search(r"\bextra\s*==", marker):
        return False
    marker_class = _marker_class()
    if marker_class is None:
        return None
    try:
        return bool(marker_class(marker.strip()).evaluate())
    except Exception:
        return None


def bundled_distributions(
    roots: Iterable[str] | None = None,
    *,
    lookup=metadata.distribution,
) -> list[metadata.Distribution]:
    """The requirements and everything they require, each once, sorted by name.

    A root that is not installed is a problem, because the build needs it. A
    dependency that is not installed is skipped: its marker put it on another
    platform or behind an extra this app does not use.
    """
    wanted = requirement_names() if roots is None else [(name, True) for name in roots]
    found: dict[str, metadata.Distribution] = {}
    problems: list[str] = []
    queue = list(wanted) + [(name, False) for name in ALWAYS_BUNDLED]
    while queue:
        name, required = queue.pop(0)
        key = canonical_name(name)
        if key in found:
            continue
        try:
            dist = lookup(name)
        except metadata.PackageNotFoundError:
            if required:
                problems.append(f"{name} is in requirements.txt but is not installed in this environment")
            continue
        found[key] = dist
        for line in dist.requires or ():
            requirement, _, marker = line.partition(";")
            if marker.strip() and _marker_applies(marker) is False:
                continue
            match = _REQUIREMENT_NAME_RE.match(requirement)
            if match:
                queue.append((match.group(1), False))
    if problems:
        raise NoticesError(problems)
    return [found[key] for key in sorted(found)]


def license_identifier(dist: metadata.Distribution) -> str:
    """The license a distribution declares: expression, short field, or classifiers."""
    meta = dist.metadata
    expression = (meta.get("License-Expression") or "").strip()
    if expression:
        return expression
    field = (meta.get("License") or "").strip()
    if field and "\n" not in field and len(field) <= 200 and field.upper() != "UNKNOWN":
        return field
    classifiers = [
        item.split("::")[-1].strip()
        for item in meta.get_all("Classifier") or ()
        if item.startswith("License ::")
    ]
    if classifiers:
        return "; ".join(classifiers)
    first = field.splitlines()[0].strip() if field else ""
    if first and len(first) <= 80 and first.upper() != "UNKNOWN":
        return first
    return "not declared in its package metadata (see the text below)"


def _is_license_file(file: metadata.PackagePath) -> bool:
    name = file.parts[-1] if file.parts else ""
    if "__pycache__" in file.parts:
        return False
    return bool(_LICENSE_NAME_RE.match(name)) and os.path.splitext(name)[1].lower() not in _NOT_TEXT_SUFFIXES


def distribution_license_texts(
    dist: metadata.Distribution,
    *,
    overrides_dir: str | os.PathLike[str] | None = LICENSE_OVERRIDES_DIR,
) -> tuple[LicenseText, ...]:
    """Every license text dist ships, in order; empty when it ships none.

    The files its metadata declares come first, then other license-named
    files in its .dist-info, then license-named files elsewhere in its RECORD
    (code vendored inside the package). With none of those, a multi-line
    License field, and after that an override file.
    """
    files = list(dist.files or ())
    by_path = {file.as_posix(): file for file in files}
    meta_dir = next(
        ("/".join(file.parts[:-1]) for file in files
         if len(file.parts) >= 2 and file.parts[-1] == "METADATA" and file.parts[-2].endswith(".dist-info")),
        None,
    )
    chosen: list[metadata.PackagePath] = []
    if meta_dir is not None:
        for declared in dist.metadata.get_all("License-File") or ():
            for candidate in (f"{meta_dir}/licenses/{declared}", f"{meta_dir}/{declared}"):
                file = by_path.get(candidate)
                if file is not None:
                    if file not in chosen:
                        chosen.append(file)
                    break
    own, vendored = [], []
    for file in sorted(files, key=lambda item: item.as_posix()):
        if file in chosen or not _is_license_file(file):
            continue
        inside = meta_dir is not None and file.as_posix().startswith(meta_dir + "/")
        (own if inside else vendored).append(file)
    texts = []
    for file in [*chosen, *own, *vendored]:
        text = _read_text(dist.locate_file(file))
        if text:
            texts.append(LicenseText(file.as_posix(), text))
    if texts:
        return tuple(texts)
    field = (dist.metadata.get("License") or "").strip()
    if len([line for line in field.splitlines() if line.strip()]) >= 3:
        return (LicenseText("the License field of its package metadata", field),)
    if overrides_dir is not None:
        name = canonical_name(dist.metadata.get("Name") or "")
        override = pathlib.Path(overrides_dir) / f"{name}-{dist.version}.txt"
        text = _read_text(override)
        if text:
            return (LicenseText(
                f"packaging/third_party_licenses/{override.name} "
                f"(supplied with {APP_NAME}; the package ships no license file)",
                text,
            ),)
    return ()


def distribution_components(
    dists: Iterable[metadata.Distribution],
    *,
    overrides_dir: str | os.PathLike[str] | None = LICENSE_OVERRIDES_DIR,
) -> list[Component]:
    components, problems = [], []
    for dist in dists:
        name = dist.metadata.get("Name") or "unknown"
        texts = distribution_license_texts(dist, overrides_dir=overrides_dir)
        if not texts:
            problems.append(
                f"{name} {dist.version} ships no license text. Save its license, from that project's "
                f"source at exactly this version, as packaging/third_party_licenses/"
                f"{canonical_name(name)}-{dist.version}.txt"
            )
            continue
        note = "its bootloader is the app's exe" if canonical_name(name) == "pyinstaller" else ""
        components.append(Component(name, dist.version, license_identifier(dist), texts, note=note))
    if problems:
        raise NoticesError(problems)
    return components


def interpreter_license_path(
    base_prefix: str | os.PathLike[str] | None = None,
    stdlib_dir: str | os.PathLike[str] | None = None,
) -> pathlib.Path:
    """The license file of the interpreter being bundled.

    LICENSE.txt in sys.base_prefix is where python.org's Windows install
    keeps it. The standard-library directory is where POSIX builds keep it.
    """
    base = pathlib.Path(sys.base_prefix if base_prefix is None else base_prefix)
    stdlib = pathlib.Path(sysconfig.get_path("stdlib") if stdlib_dir is None else stdlib_dir)
    candidates = [base / "LICENSE.txt", base / "LICENSE", stdlib / "LICENSE.txt"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise NoticesError([
        "the interpreter's license file was not found (looked for "
        + ", ".join(str(item) for item in candidates) + ")"
    ])


def base_components(
    *,
    interpreter_license: str | os.PathLike[str] | None = None,
    python_version: str | None = None,
) -> list[Component]:
    """The interpreter. Raises naming the gap."""
    problems: list[str] = []
    interpreter_text = None
    try:
        path = interpreter_license_path() if interpreter_license is None else pathlib.Path(interpreter_license)
    except NoticesError as exc:
        problems += exc.problems
    else:
        interpreter_text = _read_text(path)
        if not interpreter_text:
            problems.append(f"the interpreter's license file {path} is empty or unreadable")
            interpreter_text = None
        elif PSF_LICENSE_MARKER not in interpreter_text:
            problems.append(f"{path} is not the Python license (it lacks {PSF_LICENSE_MARKER!r})")
            interpreter_text = None
    if problems:
        raise NoticesError(problems)
    return [Component(
        "Python", python_version or platform.python_version(), "PSF-2.0",
        (LicenseText("LICENSE.txt from the interpreter's install directory", interpreter_text),),
        kind="runtime", note="the bundled interpreter",
    )]


def dll_file_version(path: str | os.PathLike[str]) -> str:
    """The FileVersion a Windows DLL records in its version resource, read from its bytes. "" when absent."""
    try:
        data = pathlib.Path(path).read_bytes()
    except OSError:
        return ""
    key = "FileVersion".encode("utf-16-le")
    at = data.find(key)
    if at < 0:
        return ""
    # The value follows the key's terminator and padding, as UTF-16 digits and dots.
    tail = data[at + len(key): at + len(key) + 96].decode("utf-16-le", "ignore")
    match = re.search(r"(\d+(?:\.\d+){1,3})", tail)
    return match.group(1) if match else ""


def webview2_components(
    dists: Iterable[metadata.Distribution],
    *,
    overrides_dir: str | os.PathLike[str] | None = LICENSE_OVERRIDES_DIR,
) -> list[Component]:
    """The WebView2 SDK inside pywebview, when pywebview is bundled. Raises when its text is missing."""
    for dist in dists:
        if canonical_name(dist.metadata.get("Name") or "") != "pywebview":
            continue
        dll = next((file for file in dist.files or () if file.as_posix() == WEBVIEW2_DLL), None)
        if dll is None:
            return []
        version = dll_file_version(dist.locate_file(dll))
        name = f"Microsoft.Web.WebView2-{version}.txt"
        text = _read_text(pathlib.Path(overrides_dir) / name) if overrides_dir is not None and version else None
        if not text:
            raise NoticesError([
                f"pywebview {dist.version} carries the Microsoft WebView2 SDK {version or '(version unread)'}. "
                f"Save the LICENSE.txt and NOTICE.txt of the Microsoft.Web.WebView2 {version} NuGet package as "
                f"packaging/third_party_licenses/{name}"
            ])
        return [Component(
            "Microsoft Edge WebView2 SDK", version, "BSD-3-Clause (Microsoft)",
            (LicenseText(f"packaging/third_party_licenses/{name}", text),),
            kind="runtime",
            note=f"the WebView2 DLLs inside pywebview {dist.version}; the WebView2 runtime is part of Windows",
        )]
    return []


def page_components(licenses: str | os.PathLike[str] = PAGE_LICENSES) -> list[Component]:
    """The npm packages whose code is in the window's page. Raises when the list or a text is missing."""
    path = pathlib.Path(licenses)
    try:
        packages = json.loads(path.read_text(encoding="utf-8"))["packages"]
    except (OSError, ValueError, KeyError, TypeError):
        raise NoticesError([
            f"{path} is missing or unreadable. Build the page (app/frontend: npm ci, npm run build) and commit it."
        ]) from None
    components, problems = [], []
    for item in packages:
        name, version = str(item.get("name") or ""), str(item.get("version") or "")
        text = str(item.get("text") or "").replace("\r\n", "\n").strip()
        if not text:
            problems.append(f"the page bundles {name} {version}, and its package ships no license text")
            continue
        components.append(Component(
            name, version, str(item.get("license") or "not declared"),
            (LicenseText(f"node_modules/{name}, bundled into the page", text),), kind="javascript",
        ))
    if not components and not problems:
        problems.append(f"{path} lists no packages; the page cannot have been built from app/frontend")
    if problems:
        raise NoticesError(problems)
    return components


_GROUPS = (("runtime", "Runtime"), ("python", "Python packages"), ("javascript", "The window's page (JavaScript)"))


def render_notices(components: Sequence[Component]) -> str:
    """The notices document, with LF line endings."""
    lines = [
        "THIRD-PARTY NOTICES",
        "",
        f"{APP_NAME} for Windows is built with PyInstaller and bundles the components",
        "listed below: the Python interpreter, Python packages, the WebView2 SDK that",
        "shows the window, and the JavaScript packages in the window's page. Each",
        "remains under its own license, and its full text is reproduced in this file",
        f"as the component distributes it. {APP_NAME}'s own license is in LICENSE.txt,",
        "in this folder. The Microsoft Edge WebView2 runtime that draws the window is",
        "part of Windows and is not bundled.",
    ]
    for kind, heading in _GROUPS:
        members = [item for item in components if item.kind == kind]
        if not members:
            continue
        lines += ["", heading, "-" * len(heading)]
        lines += [f"  {item.title} - {item.license}" for item in members]
    for kind, _heading in _GROUPS:
        for component in (item for item in components if item.kind == kind):
            heading = component.title + (f" ({component.note})" if component.note else "")
            lines += ["", "", _RULE, heading, f"License: {component.license}"]
            for text in component.texts:
                lines += ["", f"--- {text.source} ---", "", text.text]
    return "\n".join(lines) + "\n"


def build_notices(
    *,
    roots: Iterable[str] | None = None,
    interpreter_license: str | os.PathLike[str] | None = None,
    overrides_dir: str | os.PathLike[str] | None = LICENSE_OVERRIDES_DIR,
    page_licenses: str | os.PathLike[str] = PAGE_LICENSES,
) -> tuple[str, list[Component]]:
    """Render the notices for this environment. Raises naming every missing text."""
    problems: list[str] = []
    components: list[Component] = []
    try:
        components += base_components(interpreter_license=interpreter_license)
    except NoticesError as exc:
        problems += exc.problems
    dists: list[metadata.Distribution] = []
    try:
        dists = bundled_distributions(roots)
        components += distribution_components(dists, overrides_dir=overrides_dir)
    except NoticesError as exc:
        problems += exc.problems
    for gather in (lambda: webview2_components(dists, overrides_dir=overrides_dir), lambda: page_components(page_licenses)):
        try:
            components += gather()
        except NoticesError as exc:
            problems += exc.problems
    if problems:
        raise NoticesError(problems)
    return render_notices(components), components


def write_notices(destination: str | os.PathLike[str], **options) -> list[Component]:
    """Write the notices file. Nothing is written when a text is missing."""
    text, components = build_notices(**options)
    path = pathlib.Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\r\n" if os.name == "nt" else "\n")
    return components


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Write or check {APP_NAME}'s third-party notices")
    parser.add_argument("--out", default="", help="Write the notices here (default: do not write)")
    parser.add_argument("--check", action="store_true", help="Only check that every license text is found")
    args = parser.parse_args(argv)
    try:
        if args.out and not args.check:
            components = write_notices(args.out)
            sys.stdout.write(f"wrote {args.out} ({len(components)} components)\n")
        else:
            _text, components = build_notices()
            sys.stdout.write(f"every license text was found ({len(components)} components)\n")
    except NoticesError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1
    for component in components:
        sys.stdout.write(f"  {component.title} - {component.license}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
