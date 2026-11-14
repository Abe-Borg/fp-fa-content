"""The app's name, its license, and the installer that shows the license.

The name and the license are stated in several places: fpfa/about.py, the
window, the LICENSE file, the installer script, the build scripts, the
release workflow, and the README. These tests keep them saying one thing.
None needs a display or a Windows machine: the installer script is read as
text.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
from importlib import metadata
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

PACKAGING = APP_DIR / "packaging"
ISS = PACKAGING / "installer.iss"
LICENSE = REPO / "LICENSE"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _iss_value(key: str) -> list[str]:
    """Every value of a [Setup]-style key in installer.iss, comments left out."""
    values = []
    for line in ISS.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith(";"):
            continue
        match = re.match(rf"^{re.escape(key)}=(.*)$", line)
        if match:
            values.append(match.group(1).strip())
    return values


def _iss_define(name: str) -> str:
    match = re.search(rf'^#define {name} "([^"]*)"', ISS.read_text(encoding="utf-8"), flags=re.M)
    assert match, f"installer.iss does not define {name}"
    return match.group(1)


def _iss_section(name: str) -> list[str]:
    lines, inside = [], False
    for line in ISS.read_text(encoding="utf-8").splitlines():
        if line.startswith("["):
            inside = line.strip() == f"[{name}]"
            continue
        if inside and line.strip() and not line.lstrip().startswith(";"):
            lines.append(line.strip())
    return lines


class NameTests(unittest.TestCase):
    def test_the_app_is_named_cynosure_everywhere_a_designer_sees_it(self):
        from fpfa import __version__, about
        from fpfa.instance_lock import ANOTHER_WINDOW_TEXT

        self.assertEqual(about.APP_NAME, "+Cynosure")
        self.assertEqual(about.APP_FILE_NAME, "Cynosure")
        self.assertTrue(about.version_lines(REPO, Path("/data"))[0].startswith(f"+Cynosure {__version__} ("))
        self.assertTrue(ANOTHER_WINDOW_TEXT.startswith("+Cynosure is already open"))
        self.assertEqual(_iss_define("MyAppName"), about.APP_NAME)
        self.assertEqual(_iss_define("MyAppExeName"), "Cynosure.exe")
        self.assertEqual(_iss_value("OutputBaseFilename"), ["Cynosure-Setup-{#MyAppVersion}"])
        self.assertEqual(_iss_value("DefaultDirName"), ["{autopf}\\{#MyAppFileName}"])
        self.assertTrue((REPO / "README.md").read_text(encoding="utf-8").startswith("# +Cynosure\n"))

    def test_the_old_name_is_gone_from_the_app_and_its_packaging(self):
        old = re.compile(r"FP/FA Design Assistant|FP/FA App|FPFA App|fpfa-setup|fpfa-windows|fpfa\.exe")
        allowed = {
            # The installer names the old exe and shortcuts once, to remove them on an upgrade.
            ISS: {"fpfa.exe", "FPFA App", "FP/FA App", "fpfa-setup"},
        }
        files = [*sorted((APP_DIR / "fpfa").glob("*.py")), *sorted(PACKAGING.glob("*.*")),
                 REPO / ".github" / "workflows" / "windows-app.yml"]
        for path in files:
            if path.suffix in (".ico", ".pyc"):
                continue
            found = set(old.findall(path.read_text(encoding="utf-8")))
            self.assertLessEqual(found, allowed.get(path, set()), f"{path.name} still names the old app: {found}")

    def test_an_install_under_the_old_name_is_upgraded_in_place(self):
        # The id of the published fpfa-setup-0.1.0.exe. Changing it would install a second copy.
        self.assertEqual(_iss_value("AppId"), ["{{A8F1C3E2-9B47-4D6A-8E21-0FPFA0100000}"])
        removed = "\n".join(_iss_section("InstallDelete"))
        self.assertIn('Name: "{app}\\fpfa.exe"', removed)
        self.assertIn('Name: "{autoprograms}\\FPFA App"', removed)
        self.assertIn('Name: "{autodesktop}\\FPFA App.lnk"', removed)
        icons = "\n".join(_iss_section("Icons"))
        self.assertIn('Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"', icons)
        # What a designer's data is filed under does not change, so jobs and the key carry over.
        from fpfa import keystore, paths

        self.assertIn("fpfa-assistant", Path(paths.__file__).read_text(encoding="utf-8"))
        self.assertIn("fpfa-assistant", Path(keystore.__file__).read_text(encoding="utf-8"))

    def test_the_build_names_the_exe_and_gives_it_the_icon(self):
        build_app = _load("fpfa_build_app_branding", PACKAGING / "build_app.py")
        work = Path(tempfile.mkdtemp(prefix="fpfa-brand-"))
        windows = build_app.pyinstaller_command(work / "seed", work / "dist", work / "w", windowed=True, windows=True)
        self.assertEqual(windows[windows.index("--name") + 1], "Cynosure")
        self.assertEqual(Path(windows[windows.index("--icon") + 1]), PACKAGING / "assets" / "Cynosure.ico")
        other = build_app.pyinstaller_command(work / "seed", work / "dist", work / "w", windowed=False, windows=False)
        self.assertNotIn("--icon", other)
        # The About box of a packaged app reads these versions from the bundle.
        for name in ("anthropic", "python-docx", "keyring", "pywebview", "pythonnet"):
            self.assertIn(name, [windows[i + 1] for i, flag in enumerate(windows) if flag == "--copy-metadata"])
        # The window: the built page goes in as data, pywebview's Windows backend whole, and no tkinter.
        data = [windows[i + 1] for i, flag in enumerate(windows) if flag == "--add-data"]
        self.assertTrue(any(item.endswith("fpfa/web/static") and "static" in item.split(os.pathsep)[0] for item in data))
        collected = [windows[i + 1] for i, flag in enumerate(windows) if flag == "--collect-all"]
        self.assertEqual(collected, ["webview", "clr_loader", "pythonnet"])
        self.assertIn("clr", [windows[i + 1] for i, flag in enumerate(windows) if flag == "--hidden-import"])
        self.assertIn("tkinter", [windows[i + 1] for i, flag in enumerate(windows) if flag == "--exclude-module"])
        self.assertNotIn("clr_loader", [other[i + 1] for i, flag in enumerate(other) if flag == "--collect-all"])
        self.assertEqual(_iss_value("SetupIconFile"), ["assets\\Cynosure.ico"])

    def test_the_icon_file_is_the_star_the_window_draws(self):
        from fpfa import shapes, theme

        make_icon = _load("fpfa_make_icon", PACKAGING / "make_icon.py")
        self.assertEqual((make_icon.STAR, make_icon.BACKGROUND), (theme.ICON_STAR, theme.ICON_BACKGROUND))
        committed = make_icon.ICON_PATH.read_bytes()
        self.assertEqual(committed[:4], b"\x00\x00\x01\x00")
        self.assertEqual(int.from_bytes(committed[4:6], "little"), len(make_icon.SIZES))
        # The small sizes are quick to redraw. They must be the bytes in the committed file.
        small = shapes.encode_ico([shapes.star_mark(size, make_icon.STAR, make_icon.BACKGROUND) for size in (16, 20)])
        first_entry = int.from_bytes(committed[6 + 8:6 + 12], "little")
        first_offset = int.from_bytes(committed[6 + 12:6 + 16], "little")
        small_size = int.from_bytes(small[6 + 8:6 + 12], "little")
        small_offset = int.from_bytes(small[6 + 12:6 + 16], "little")
        self.assertEqual(committed[first_offset:first_offset + first_entry], small[small_offset:small_offset + small_size])
        self.assertEqual([size for size in make_icon.SIZES if size >= 256], [256])


class LicenseTests(unittest.TestCase):
    def test_the_license_reserves_original_rights_and_preserves_third_party_and_existing_rights(self):
        raw = LICENSE.read_bytes()
        # Inno Setup shows a text license as ANSI or UTF-8. Plain ASCII reads the same either way.
        self.assertTrue(raw.isascii(), "LICENSE holds a non-ASCII character; an older Inno Setup would garble it")
        self.assertFalse(raw.lstrip().startswith(b"{\\rtf"))
        text = raw.decode("ascii")
        lines = text.splitlines()
        self.assertEqual(lines[0], "# +Cynosure Proprietary License Notice")
        self.assertIn("Copyright (c) 2026 Abraham Borg. All rights reserved.", lines)
        for heading in ("## Scope", "## No License Granted", "## Third-Party Materials",
                        "## Existing Rights and Separate Agreements", "## No Warranty",
                        "## Limitation of Liability", "## Engineering Use"):
            self.assertIn(heading, lines)
        prose = " ".join(text.split())
        self.assertIn("No license or permission to use, run, copy, modify", prose)
        self.assertIn("require separate written permission from Abraham Borg", prose)
        self.assertIn("does not replace those licenses", prose)
        self.assertIn("does not revoke rights already granted", prose)
        self.assertIn("WITHOUT WARRANTY", prose)
        self.assertIn("APPLICABLE LAW PROHIBITS", prose)

    def test_every_surface_states_the_same_license(self):
        from fpfa import about

        self.assertEqual(about.LICENSE_NAME, "Proprietary License Notice")
        self.assertEqual(about.LICENSE_URL, f"{about.PROJECT_URL}/blob/main/LICENSE")
        self.assertEqual(about.COPYRIGHT, "Copyright (c) 2026 Abraham Borg")
        self.assertEqual(about.license_text(), LICENSE.read_text(encoding="ascii"))
        self.assertIn(about.LICENSE_NAME, about.LICENSE_SUMMARY)
        self.assertIn("All rights reserved", about.LICENSE_SUMMARY)
        self.assertIn("require separate written permission", about.LICENSE_SUMMARY)
        self.assertIn("draft for the engineer of record", about.USE_NOTICE)
        shown = about.about_text(REPO, Path("/data"))
        for part in (about.COPYRIGHT, about.LICENSE_SUMMARY, about.USE_NOTICE, "Record schema"):
            self.assertIn(part, shown)
        self.assertEqual(_iss_define("MyAppCopyright"), about.COPYRIGHT)
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("## License", readme)
        self.assertIn("[Proprietary License Notice](LICENSE)", readme)
        self.assertIn(about.COPYRIGHT.replace("Copyright (c) ", ""), readme)
        workflow = (REPO / ".github" / "workflows" / "windows-app.yml").read_text(encoding="utf-8")
        self.assertIn("Proprietary License Notice", workflow)

    def test_the_installer_names_the_author_as_publisher(self):
        # The app is its author's own. The publisher Windows shows under Apps is the name on
        # the license, and no file outside the content pack names anyone else.
        from fpfa import about

        script = (APP_DIR / "packaging" / "installer.iss").read_text(encoding="utf-8")
        self.assertIn(f'#define MyAppPublisher "{about.APP_AUTHOR}"', script)
        self.assertIn(about.APP_AUTHOR, about.COPYRIGHT)
        root = APP_DIR.parent
        for path in [root / "README.md", root / "CLAUDE.md", root / "LICENSE",
                     *sorted((root / "docs").glob("*.md")),
                     *sorted((APP_DIR / "packaging").glob("*.*")),
                     *sorted((APP_DIR / "fpfa").glob("*.py")),
                     *sorted((root / ".github" / "workflows").glob("*.yml"))]:
            if path.suffix in (".ico", ".png"):
                continue
            self.assertNotIn("ehvert", path.read_text(encoding="utf-8", errors="replace").lower(), path.name)

    def test_the_installer_shows_the_license_and_waits_for_acceptance(self):
        values = _iss_value("LicenseFile")
        self.assertEqual(len(values), 1, "installer.iss needs one LicenseFile, or Setup shows no license page")
        target = (PACKAGING / values[0].replace("\\", "/")).resolve()
        self.assertEqual(target, LICENSE.resolve(), "the license page must show the root LICENSE, not a copy")
        # Nothing in the script skips the page or pre-selects acceptance.
        script = ISS.read_text(encoding="utf-8")
        self.assertNotIn("wpLicense", script)
        self.assertNotIn("LicenseAcceptedRadio", script)
        self.assertEqual(_iss_section("Code"), [])
        label = _iss_value("LicenseLabel3")
        self.assertEqual(len(label), 1)
        self.assertTrue(label[0].isascii())
        self.assertIn("Proprietary License Notice", label[0])
        self.assertIn("require separate written permission", label[0])
        self.assertIn("Accepting this notice does not grant permission", label[0])
        self.assertIn("without warranty", label[0])
        self.assertIn("draft for the engineer of record", label[0])
        self.assertIn("the agreement below governs", label[0])
        self.assertIn("You must accept the agreement before continuing", label[0])

    def test_the_installer_puts_the_terms_beside_the_exe(self):
        files = _iss_section("Files")
        license_lines = [line for line in files if 'Source: "..\\..\\LICENSE"' in line]
        self.assertEqual(len(license_lines), 1)
        self.assertIn('DestDir: "{app}"', license_lines[0])
        self.assertIn('DestName: "LICENSE.txt"', license_lines[0])
        notices = [line for line in files if "THIRD-PARTY-NOTICES.txt" in line]
        self.assertEqual(len(notices), 1)
        self.assertIn('DestDir: "{app}"', notices[0])
        for line in (*license_lines, *notices):
            # A missing file must stop the compile, not be passed over.
            self.assertNotIn("skipifsourcedoesntexist", line)
        script = (PACKAGING / "build_installer.ps1").read_text(encoding="utf-8")
        self.assertIn('"LICENSE.txt", "THIRD-PARTY-NOTICES.txt"', script)
        workflow = (REPO / ".github" / "workflows" / "windows-app.yml").read_text(encoding="utf-8")
        self.assertIn("third_party_notices.py --check", workflow)
        self.assertIn('"Cynosure.exe", "LICENSE.txt", "THIRD-PARTY-NOTICES.txt"', workflow)

    def test_the_built_folder_carries_the_license(self):
        build_app = _load("fpfa_build_app_license", PACKAGING / "build_app.py")
        folder = Path(tempfile.mkdtemp(prefix="fpfa-bundle-")) / "Cynosure"
        written = build_app.finish_bundle(folder, notices=False)
        self.assertEqual(written, ["LICENSE.txt"])
        self.assertEqual((folder / "LICENSE.txt").read_bytes(), LICENSE.read_bytes())


class NoticesTests(unittest.TestCase):
    def setUp(self):
        self.notices = _load("fpfa_third_party_notices", PACKAGING / "third_party_notices.py")
        self.work = Path(tempfile.mkdtemp(prefix="fpfa-notices-"))

    def _interpreter_license(self) -> Path:
        text = "A. HISTORY\n\nPYTHON SOFTWARE FOUNDATION LICENSE VERSION 2\n\n1. This LICENSE AGREEMENT...\n"
        path = self.work / "LICENSE.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def _dist(self, name: str, version: str = "1.0", *, license_text: str | None = "MIT License\n\nPermission...",
              requires: list[str] | None = None) -> None:
        folder = self.work / "site" / f"{name.replace('-', '_')}-{version}.dist-info"
        folder.mkdir(parents=True, exist_ok=True)
        meta = ["Metadata-Version: 2.1", f"Name: {name}", f"Version: {version}", "License-Expression: MIT"]
        meta += [f"Requires-Dist: {item}" for item in requires or []]
        record = [f"{folder.name}/METADATA,,"]
        if license_text is not None:
            (folder / "licenses").mkdir(exist_ok=True)
            (folder / "licenses" / "LICENSE").write_text(license_text, encoding="utf-8")
            meta.append("License-File: LICENSE")
            record.append(f"{folder.name}/licenses/LICENSE,,")
        (folder / "METADATA").write_text("\n".join(meta) + "\n", encoding="utf-8")
        (folder / "RECORD").write_text("\n".join(record) + "\n", encoding="utf-8")

    def _lookup(self, name: str):
        found = list(metadata.distributions(name=name, path=[str(self.work / "site")]))
        if not found:
            raise metadata.PackageNotFoundError(name)
        return found[0]

    def test_requirements_are_read_with_their_platform_markers(self):
        path = self.work / "requirements.txt"
        path.write_text(
            "anthropic>=2.2.0\n# a comment\npython-docx>=1.1.0\n"
            'only-elsewhere>=1; sys_platform == "no-such-platform"\n'
            'everywhere>=1; python_version >= "3.0"\n',
            encoding="utf-8",
        )
        names = dict(self.notices.requirement_names(path))
        self.assertEqual(names["anthropic"], True)
        self.assertEqual(names["python-docx"], True)
        if self.notices._marker_class() is not None:
            self.assertNotIn("only-elsewhere", names)
            self.assertEqual(names["everywhere"], True)
        real = dict(self.notices.requirement_names())
        for name in ("anthropic", "python-docx", "keyring"):
            self.assertIn(name, real)

    def test_the_closure_follows_requirements_and_skips_extras(self):
        self._dist("root-pkg", requires=["dep-one>=1", 'only-extra ; extra == "bedrock"', "not-installed>=2"])
        self._dist("dep-one", requires=["dep-two"])
        self._dist("dep-two")
        self._dist("only-extra")
        dists = self.notices.bundled_distributions(["root-pkg"], lookup=self._lookup)
        self.assertEqual([dist.metadata["Name"] for dist in dists], ["dep-one", "dep-two", "root-pkg"])
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.bundled_distributions(["root-pkg", "missing-root"], lookup=self._lookup)
        self.assertIn("missing-root", str(raised.exception))

    def test_a_package_without_a_license_text_stops_the_build_until_one_is_supplied(self):
        self._dist("has-text")
        self._dist("no-text", "2.5", license_text=None)
        dists = [self._lookup("has-text"), self._lookup("no-text")]
        overrides = self.work / "third_party_licenses"
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.distribution_components(dists, overrides_dir=overrides)
        self.assertEqual(len(raised.exception.problems), 1)
        self.assertIn("no-text 2.5 ships no license text", raised.exception.problems[0])
        self.assertIn("third_party_licenses/no-text-2.5.txt", raised.exception.problems[0])
        # The text for another version does not count: an upgrade must be checked again.
        overrides.mkdir()
        (overrides / "no-text-2.4.txt").write_text("BSD License\n", encoding="utf-8")
        with self.assertRaises(self.notices.NoticesError):
            self.notices.distribution_components(dists, overrides_dir=overrides)
        (overrides / "no-text-2.5.txt").write_text("BSD License\n\nRedistribution...", encoding="utf-8")
        components = self.notices.distribution_components(dists, overrides_dir=overrides)
        self.assertEqual([item.title for item in components], ["has-text 1.0", "no-text 2.5"])
        self.assertIn("supplied with +Cynosure", components[1].texts[0].source)

    def test_the_interpreter_is_always_listed_and_no_window_toolkit_is(self):
        license_path = self._interpreter_license()
        components = self.notices.base_components(interpreter_license=license_path, python_version="3.12.0")
        self.assertEqual([item.title for item in components], ["Python 3.12.0"])
        self.assertFalse(hasattr(self.notices, "tcl_tk_directories"), "the window is WebView2; no Tcl or Tk ships")
        not_python = self.work / "other.txt"
        not_python.write_text("Some other license.", encoding="utf-8")
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.base_components(interpreter_license=not_python)
        self.assertTrue(any("is not the Python license" in item for item in raised.exception.problems))

    def _webview_dist(self, version: str = "1.0.3856.49"):
        folder = self.work / "site" / "pywebview-6.2.1.dist-info"
        folder.mkdir(parents=True, exist_ok=True)
        lib = self.work / "site" / "webview" / "lib"
        lib.mkdir(parents=True, exist_ok=True)
        # A version resource as Windows writes it: the key, its padding, then the value, in UTF-16.
        (lib / "Microsoft.Web.WebView2.Core.dll").write_bytes(
            b"MZ\x90\x00" + "FileVersion".encode("utf-16-le") + b"\x00\x00\x00\x00" + version.encode("utf-16-le")
            + b"\x00\x00" + "InternalName".encode("utf-16-le")
        )
        (folder / "METADATA").write_text("Metadata-Version: 2.1\nName: pywebview\nVersion: 6.2.1\n", encoding="utf-8")
        (folder / "RECORD").write_text(
            f"{folder.name}/METADATA,,\nwebview/lib/Microsoft.Web.WebView2.Core.dll,,\n", encoding="utf-8"
        )
        return self._lookup("pywebview")

    def test_the_webview2_sdk_inside_pywebview_needs_its_text_at_its_own_version(self):
        dist = self._webview_dist()
        self.assertEqual(self.notices.dll_file_version(dist.locate_file("webview/lib/Microsoft.Web.WebView2.Core.dll")),
                         "1.0.3856.49")
        overrides = self.work / "third_party_licenses"
        overrides.mkdir()
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.webview2_components([dist], overrides_dir=overrides)
        self.assertIn("Microsoft.Web.WebView2-1.0.3856.49.txt", raised.exception.problems[0])
        (overrides / "Microsoft.Web.WebView2-1.0.3856.49.txt").write_text("Copyright (C) Microsoft...", encoding="utf-8")
        [component] = self.notices.webview2_components([dist], overrides_dir=overrides)
        self.assertEqual(component.title, "Microsoft Edge WebView2 SDK 1.0.3856.49")
        self.assertIn("part of Windows", component.note)
        self.assertEqual(self.notices.webview2_components([], overrides_dir=overrides), [])
        # The text committed with the app is the package's own.
        shipped = (PACKAGING / "third_party_licenses" / "Microsoft.Web.WebView2-1.0.3856.49.txt").read_text(encoding="utf-8")
        self.assertIn("Copyright (C) Microsoft Corporation. All rights reserved.", shipped)
        self.assertIn("NOTICES AND INFORMATION", shipped)

    def test_the_pages_packages_are_listed_from_its_build(self):
        components = self.notices.page_components()
        names = [item.name for item in components]
        self.assertTrue({"react", "react-dom", "scheduler"} <= set(names), names)
        self.assertTrue(all(item.kind == "javascript" and "Permission is hereby granted" in item.texts[0].text
                            for item in components))
        broken = self.work / "licenses.json"
        broken.write_text(json.dumps({"packages": [{"name": "left-pad", "version": "1.3.0", "license": "WTFPL", "text": ""}]}),
                          encoding="utf-8")
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.page_components(broken)
        self.assertIn("left-pad 1.3.0", raised.exception.problems[0])
        with self.assertRaises(self.notices.NoticesError):
            self.notices.page_components(self.work / "missing.json")

    def test_the_document_lists_every_component_with_its_text_and_nothing_is_written_on_a_gap(self):
        components = [
            self.notices.Component("Python", "3.12.0", "PSF-2.0",
                                   (self.notices.LicenseText("LICENSE.txt", "PSF TEXT"),), kind="runtime"),
            self.notices.Component("anthropic", "2.7.0", "Apache-2.0",
                                   (self.notices.LicenseText("licenses/LICENSE", "APACHE TEXT"),)),
        ]
        text = self.notices.render_notices(components)
        self.assertTrue(text.startswith("THIRD-PARTY NOTICES\n"))
        self.assertIn("+Cynosure's own license is in LICENSE.txt", text)
        self.assertIn("  Python 3.12.0 - PSF-2.0", text)
        self.assertIn("  anthropic 2.7.0 - Apache-2.0", text)
        self.assertLess(text.index("PSF TEXT"), text.index("APACHE TEXT"))
        destination = self.work / "out" / "THIRD-PARTY-NOTICES.txt"
        with self.assertRaises(self.notices.NoticesError):
            self.notices.write_notices(destination, roots=["no-such-package-anywhere"],
                                       interpreter_license=self._interpreter_license())
        self.assertFalse(destination.exists())

    def test_this_environment_has_a_license_text_for_every_package_the_app_needs(self):
        """The packages in requirements.txt and all they require, as installed here."""
        dists = self.notices.bundled_distributions()
        names = {self.notices.canonical_name(dist.metadata["Name"]) for dist in dists}
        for name in ("anthropic", "python-docx", "keyring"):
            self.assertIn(name, names)
        components = self.notices.distribution_components(dists)
        self.assertEqual(len(components), len(dists))
        components += self.notices.webview2_components(dists) + self.notices.page_components()
        for component in components:
            self.assertTrue(component.texts and all(text.text.strip() for text in component.texts), component.title)
        if "pywebview" in names:
            self.assertIn("Microsoft Edge WebView2 SDK", [item.name for item in components])


if __name__ == "__main__":
    unittest.main()
