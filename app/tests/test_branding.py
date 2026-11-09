"""The app's name, its license, and the installer that shows the license.

The name and the license are stated in several places: fpfa/about.py, the
window, the LICENSE file, the installer script, the build scripts, the
release workflow, and the README. These tests keep them saying one thing.
None needs a display or a Windows machine: the installer script is read as
text.
"""

from __future__ import annotations

import importlib.util
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
        for name in ("anthropic", "python-docx", "keyring"):
            self.assertIn(name, [windows[i + 1] for i, flag in enumerate(windows) if flag == "--copy-metadata"])
        self.assertEqual(_iss_value("SetupIconFile"), ["assets\\Cynosure.ico"])

    def test_the_icon_file_is_the_star_the_window_draws(self):
        try:
            import tkinter  # noqa: F401
        except ImportError:
            self.skipTest("tkinter is not installed")
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
    def test_the_license_file_is_polyform_shield_naming_the_app(self):
        raw = LICENSE.read_bytes()
        # Inno Setup shows a text license as ANSI or UTF-8. Plain ASCII reads the same either way.
        self.assertTrue(raw.isascii(), "LICENSE holds a non-ASCII character; an older Inno Setup would garble it")
        self.assertFalse(raw.lstrip().startswith(b"{\\rtf"))
        text = raw.decode("ascii")
        lines = text.splitlines()
        self.assertEqual(lines[0], "# PolyForm Shield License 1.0.0")
        self.assertIn("<https://polyformproject.org/licenses/shield/1.0.0>", lines)
        self.assertIn(
            "Required Notice: Copyright (c) 2026 Abraham Borg (https://github.com/Abe-Borg/fp-fa-content)", lines
        )
        business = next(line for line in lines if line.startswith("Licensor Line of Business:"))
        self.assertIn("+Cynosure", business)
        for heading in ("## Acceptance", "## Copyright License", "## Distribution License", "## Notices",
                        "## Noncompete", "## No Liability", "## Definitions"):
            self.assertIn(heading, lines)
        self.assertIn("the software comes as is, without any warranty or condition", text)

    def test_every_surface_states_the_same_license(self):
        from fpfa import about

        self.assertEqual(about.LICENSE_NAME, "PolyForm Shield License 1.0.0")
        self.assertEqual(about.LICENSE_URL, "https://polyformproject.org/licenses/shield/1.0.0")
        self.assertEqual(about.COPYRIGHT, "Copyright (c) 2026 Abraham Borg")
        self.assertEqual(about.license_text(), LICENSE.read_text(encoding="ascii"))
        self.assertIn(about.LICENSE_NAME, about.LICENSE_SUMMARY)
        self.assertIn("except to provide a product that competes with +Cynosure", about.LICENSE_SUMMARY)
        self.assertIn("draft for the engineer of record", about.USE_NOTICE)
        shown = about.about_text(REPO, Path("/data"))
        for part in (about.COPYRIGHT, about.LICENSE_SUMMARY, about.USE_NOTICE, "Record schema"):
            self.assertIn(part, shown)
        self.assertEqual(_iss_define("MyAppCopyright"), about.COPYRIGHT)
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("## License", readme)
        self.assertIn("[PolyForm Shield License 1.0.0](LICENSE)", readme)
        self.assertIn(about.COPYRIGHT.replace("Copyright (c) ", ""), readme)
        workflow = (REPO / ".github" / "workflows" / "windows-app.yml").read_text(encoding="utf-8")
        self.assertIn("PolyForm Shield License 1.0.0", workflow)

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
        self.assertIn("PolyForm Shield License 1.0.0", label[0])
        self.assertIn("except to provide a product that competes with {#MyAppName}", label[0])
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

    def _interpreter_license(self, *, with_tcl: bool = True) -> Path:
        text = "A. HISTORY\n\nPYTHON SOFTWARE FOUNDATION LICENSE VERSION 2\n\n1. This LICENSE AGREEMENT...\n"
        if with_tcl:
            text += (
                "\nTCL\n" + self.notices.TCL_TERMS_OPENING.replace(" ", "\r\n", 3)
                + " The following terms apply to all files. ... " + self.notices.TCL_TK_TERMS_CLOSING + "\n"
                "\nTK\n" + self.notices.TK_TERMS_OPENING + " The following terms apply. ... "
                + self.notices.TCL_TK_TERMS_CLOSING + "\n"
            )
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

    def test_the_interpreter_and_the_window_toolkit_are_always_listed(self):
        license_path = self._interpreter_license()
        components = self.notices.base_components(
            interpreter_license=license_path, tcl_dir=self.work / "tcl8.6", tk_dir=self.work / "tk8.6",
            python_version="3.12.0",
        )
        self.assertEqual([item.title for item in components], ["Python 3.12.0", "Tcl 8.6", "Tk 8.6"])
        self.assertIn("Apple Inc.", components[2].texts[0].text)
        self.assertNotIn("Apple Inc.", components[1].texts[0].text)
        # A license.terms file in the library directory is preferred over the block in Python's file.
        (self.work / "tcl8.6").mkdir()
        (self.work / "tcl8.6" / "license.terms").write_text("Tcl terms from the library directory.", encoding="utf-8")
        again = self.notices.base_components(
            interpreter_license=license_path, tcl_dir=self.work / "tcl8.6", tk_dir=self.work / "tk8.6",
        )
        self.assertEqual(again[1].texts[0].text, "Tcl terms from the library directory.")
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.base_components(
                interpreter_license=self._interpreter_license(with_tcl=False),
                tcl_dir=self.work / "nowhere" / "tcl8.6", tk_dir=self.work / "nowhere" / "tk8.6",
                system_docs=None,
            )
        self.assertEqual(len(raised.exception.problems), 2)
        # A Linux distribution keeps the terms with its own Tcl and Tk packages.
        docs = self.work / "doc"
        for package in ("libtcl8.6", "tk8.6"):
            (docs / package).mkdir(parents=True)
            (docs / package / "copyright").write_text(f"Terms of the system {package} package.", encoding="utf-8")
        packaged = self.notices.base_components(
            interpreter_license=self._interpreter_license(with_tcl=False),
            tcl_dir=self.work / "nowhere" / "tcl8.6", tk_dir=self.work / "nowhere" / "tk8.6", system_docs=docs,
        )
        self.assertEqual([item.texts[0].text for item in packaged[1:]],
                         ["Terms of the system libtcl8.6 package.", "Terms of the system tk8.6 package."])
        not_python = self.work / "other.txt"
        not_python.write_text("Some other license.", encoding="utf-8")
        with self.assertRaises(self.notices.NoticesError) as raised:
            self.notices.base_components(interpreter_license=not_python, tcl_dir=self.work / "tcl8.6",
                                         tk_dir=self.work / "tk8.6", system_docs=None)
        self.assertTrue(any("is not the Python license" in item for item in raised.exception.problems))

    def test_the_document_lists_every_component_with_its_text_and_nothing_is_written_on_a_gap(self):
        components = [
            self.notices.Component("Python", "3.12.0", "PSF-2.0",
                                   (self.notices.LicenseText("LICENSE.txt", "PSF TEXT"),), kind="runtime"),
            self.notices.Component("anthropic", "2.7.0", "Apache-2.0",
                                   (self.notices.LicenseText("licenses/LICENSE", "APACHE TEXT"),)),
        ]
        text = self.notices.render_notices(components)
        self.assertTrue(text.startswith("THIRD-PARTY NOTICES\n"))
        self.assertIn("+Cynosure's own\nlicense is in LICENSE.txt", text)
        self.assertIn("  Python 3.12.0 - PSF-2.0", text)
        self.assertIn("  anthropic 2.7.0 - Apache-2.0", text)
        self.assertLess(text.index("PSF TEXT"), text.index("APACHE TEXT"))
        destination = self.work / "out" / "THIRD-PARTY-NOTICES.txt"
        with self.assertRaises(self.notices.NoticesError):
            self.notices.write_notices(destination, roots=["no-such-package-anywhere"],
                                       interpreter_license=self._interpreter_license(),
                                       tcl_dir=self.work / "tcl8.6", tk_dir=self.work / "tk8.6")
        self.assertFalse(destination.exists())

    def test_this_environment_has_a_license_text_for_every_package_the_app_needs(self):
        """The packages in requirements.txt and all they require, as installed here."""
        dists = self.notices.bundled_distributions()
        names = {self.notices.canonical_name(dist.metadata["Name"]) for dist in dists}
        for name in ("anthropic", "python-docx", "keyring"):
            self.assertIn(name, names)
        components = self.notices.distribution_components(dists)
        self.assertEqual(len(components), len(dists))
        for component in components:
            self.assertTrue(component.texts and all(text.text.strip() for text in component.texts), component.title)


if __name__ == "__main__":
    unittest.main()
