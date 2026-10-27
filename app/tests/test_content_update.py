"""Content pack build and the updater. The feed is a local fixture, not GitHub."""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))


def isolate() -> Path:
    path = Path(tempfile.mkdtemp(prefix="fpfa-test-"))
    os.environ["FPFA_DATA_DIR"] = str(path)
    os.environ.pop("FPFA_CONTENT_ROOT", None)
    os.environ.pop("FPFA_CONTENT_FEED_URL", None)
    os.environ.pop("FPFA_CONTENT_UPDATES", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return path


def write_tree(root: Path, extra: dict[str, str] | None = None) -> None:
    files = {
        "skills/example/SKILL.md": "Wet, dry, and double-interlock.\n",
        "calcs/fp/formulas.py": "def screen():\n    return 1\n",
        "corpus/scope-lock.md": "Scope lock.\n",
        "specs/21-13-19-double-interlock-preaction.md": "Section 21 13 19.\n",
        "modes/mixed/MODE.md": "Mixed.\n",
        "roles/everyday/ROLE.md": "Everyday.\n",
    }
    if extra:
        files.update(extra)
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def zip_bytes(members: dict[str, bytes], symlinks: dict[str, bytes] | None = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
        for name, payload in (symlinks or {}).items():
            info = zipfile.ZipInfo(name)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, payload)
    return buffer.getvalue()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


def serve(handler) -> ThreadingHTTPServer:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def stop(httpd: ThreadingHTTPServer) -> None:
    httpd.shutdown()
    httpd.server_close()


def feed_url(httpd: ThreadingHTTPServer, path: str = "/manifest.json") -> str:
    port = httpd.server_address[1]
    return f"http://127.0.0.1:{port}{path}"


def directory_handler(directory: Path):
    class Handler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    return Handler


class ContentPackBuildTests(unittest.TestCase):
    def test_fixture_pack_strips_scope_paths_and_keeps_scope_lock_text(self):
        from fpfa.content_pack import build_pack

        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source, {
            "skills/foam/SKILL.md": "omit this file\n",
            "skills/_sources/raw.md": "omit raw\n",
            "corpus/canada/note.md": "omit this note\n",
            "skills/clean-agent/SKILL.md": "omit this file\n",
            "skills/catalog/vendor.md": "omit this file\n",
        })
        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        built = build_pack(source, out, "2026.10.1", changelog=["Shorter screen note"], created="2026-10-27T00:00:00Z")
        self.assertEqual(built.manifest["version"], "2026.10.1")
        self.assertEqual(built.manifest["created"], "2026-10-27T00:00:00Z")
        self.assertEqual(built.manifest["changelog"], ["Shorter screen note"])
        self.assertEqual(built.manifest["filename"], "fp-fa-content-v2026.10.1.zip")
        self.assertEqual(built.manifest["min_app_version"], "0.1.0")
        digest = hashlib.sha256(built.zip_path.read_bytes()).hexdigest()
        self.assertEqual(digest, built.manifest["sha256"])
        with zipfile.ZipFile(built.zip_path) as archive:
            names = archive.namelist()
            example = archive.read("skills/example/SKILL.md").decode("utf-8")
        self.assertIn("double-interlock", example)
        self.assertIn("calcs/fp/formulas.py", names)
        self.assertIn("pack.json", names)
        self.assertNotIn("app/fpfa/keystore.py", names)
        for name in names:
            parts = Path(name).parts
            self.assertNotIn("_sources", parts)
            self.assertNotIn("foam", [part.casefold() for part in parts])
            self.assertNotIn("canada", [part.casefold() for part in parts])
            self.assertNotIn("clean-agent", [part.casefold() for part in parts])
            self.assertFalse(name.startswith("app/"))
        stripped = set(built.stripped)
        self.assertIn("skills/foam/SKILL.md", stripped)
        self.assertIn("skills/_sources/raw.md", stripped)
        self.assertIn("corpus/canada/note.md", stripped)
        self.assertIn("skills/clean-agent/SKILL.md", stripped)

    def test_builder_refuses_an_api_key(self):
        from fpfa.content_pack import ContentPackError, build_pack

        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source, {"skills/example/SKILL.md": "sk-ant-" + "abcdefghij-secret\n"})
        with self.assertRaises(ContentPackError) as caught:
            build_pack(source, Path(tempfile.mkdtemp()), "2026.10.1")
        self.assertIn("API key", str(caught.exception))
        self.assertNotIn("abcdefghij", str(caught.exception))

    def test_builder_refuses_a_key_file_name(self):
        from fpfa.content_pack import ContentPackError, build_pack

        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source, {"skills/anthropic-api-key": "local secret\n"})
        with self.assertRaises(ContentPackError):
            build_pack(source, Path(tempfile.mkdtemp()), "2026.10.1")

    def test_script_packs_this_checkout(self):
        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        script = REPO / "scripts" / "build_content_pack.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--version",
                "2026.10.27",
                "--out",
                str(out),
                "--changelog",
                "Dry run fixture",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "2026.10.27")
        self.assertEqual(manifest["changelog"], ["Dry run fixture"])
        self.assertIn("created", manifest)
        blob = (out / manifest["filename"]).read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), manifest["sha256"])
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            names = archive.namelist()
            skill = archive.read("skills/preaction-el-el-trim-election/SKILL.md").decode("utf-8")
            canada_note = archive.read("skills/fa-integrated-systems-test-matrix/SKILL.md").decode("utf-8")
            marker = json.loads(archive.read("pack.json").decode("utf-8"))
        self.assertEqual(marker["version"], "2026.10.27")
        self.assertIn("foam", skill.lower())
        self.assertIn("Canada", canada_note)
        for top in ("skills/", "calcs/", "corpus/", "specs/", "modes/", "roles/"):
            self.assertTrue(any(name.startswith(top) for name in names), top)
        self.assertIn("calcs/fp/formulas.py", names)
        for name in names:
            parts = [part.casefold() for part in Path(name).parts]
            self.assertNotIn("_sources", parts)
            self.assertNotIn("foam", parts)
            self.assertNotIn("canada", parts)
            self.assertNotIn("clean-agent", parts)
            self.assertFalse(name.startswith("app/"))
            self.assertNotEqual(Path(name).name, "anthropic-api-key")
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            for name in names:
                if Path(name).suffix.lower() in {".md", ".py", ".json", ".txt"}:
                    self.assertNotIn("sk-ant-", archive.read(name).decode("utf-8", errors="replace"), name)

    def test_script_rejects_a_bad_version(self):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "build_content_pack.py"), "--version", "beta", "--out", tempfile.mkdtemp()],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("2026.10.1", proc.stderr)

    def test_seed_copy_omits_the_app_and_pack_marker(self):
        dest = Path(tempfile.mkdtemp(prefix="fpfa-seed-"))
        proc = subprocess.run(
            [sys.executable, str(APP_DIR / "packaging" / "build_app.py"), "--seed-only", "--seed", str(dest)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((dest / "skills").is_dir())
        self.assertTrue((dest / "calcs" / "fp" / "formulas.py").is_file())
        self.assertTrue((dest / "corpus").is_dir())
        self.assertFalse((dest / "app").exists())
        self.assertFalse((dest / "pack.json").exists())
        self.assertFalse((dest / "anthropic-api-key").exists())
        self.assertFalse(any("_sources" in path.parts for path in dest.rglob("*")))

    def test_workflow_publishes_on_a_content_tag(self):
        text = (REPO / ".github" / "workflows" / "content-pack.yml").read_text(encoding="utf-8")
        self.assertIn("content-v*", text)
        self.assertIn("scripts/build_content_pack.py", text)
        self.assertIn("manifest.json", text)
        self.assertIn("contents: write", text)


class ContentUpdateTests(unittest.TestCase):
    def setUp(self):
        self.data = isolate()

    def tearDown(self):
        os.environ.pop("FPFA_CONTENT_ROOT", None)
        os.environ.pop("FPFA_CONTENT_FEED_URL", None)
        os.environ.pop("FPFA_CONTENT_UPDATES", None)
        os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-test-")

    def _serve_pack(self, version: str = "2026.10.1", changelog: list[str] | None = None):
        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source, {"skills/example/SKILL.md": f"Installed {version}.\n"})
        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        from fpfa.content_pack import build_pack

        built = build_pack(source, out, version, changelog=changelog or [f"Notes for {version}"])
        httpd = serve(directory_handler(out))
        self.addCleanup(stop, httpd)
        return httpd, built

    def test_install_verifies_hash_and_keeps_the_key_outside_the_pack(self):
        from fpfa.content_update import check_for_content_update, content_version_text
        from fpfa.paths import content_root, read_config

        key = self.data / "anthropic-api-key"
        key.write_text("sk-ant-local-test-value", encoding="utf-8")
        httpd, built = self._serve_pack("2026.10.1", ["Shorter screen note"])
        result = check_for_content_update(feed_url(httpd))
        self.assertEqual(result.status, "updated", result.message)
        self.assertEqual(result.version, "2026.10.1")
        self.assertEqual(result.changelog, ["Shorter screen note"])
        root = content_root()
        self.assertEqual(root, Path(result.root))
        self.assertIn("Installed 2026.10.1.", (root / "skills" / "example" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(content_version_text(), "2026.10.1")
        cfg = read_config()
        self.assertEqual(cfg["content_version"], "2026.10.1")
        self.assertEqual(cfg["content_sha256"], built.manifest["sha256"])
        self.assertEqual(cfg["content_changelog"], ["Shorter screen note"])
        self.assertFalse((root / "anthropic-api-key").exists())
        self.assertFalse((root / "config.json").exists())
        self.assertEqual(key.read_text(encoding="utf-8"), "sk-ant-local-test-value")
        packed = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in root.rglob("*")
            if path.is_file()
        )
        self.assertNotIn("sk-ant-local-test-value", packed)

        again = check_for_content_update(feed_url(httpd))
        self.assertEqual(again.status, "current")
        self.assertEqual(content_root(), root)

    def test_bad_hash_offline_and_downgrade_keep_the_installed_pack(self):
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root, read_config

        httpd, built = self._serve_pack("2026.10.2")
        first = check_for_content_update(feed_url(httpd))
        self.assertEqual(first.status, "updated")
        installed = content_root()

        manifest = json.loads(built.manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = "2026.10.3"
        manifest["sha256"] = "0" * 64
        built.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        rejected = check_for_content_update(feed_url(httpd))
        self.assertEqual(rejected.status, "rejected")
        self.assertIn("sha256", rejected.message)
        self.assertIn("last good pack", rejected.message)
        self.assertEqual(content_root(), installed)
        self.assertEqual(read_config()["content_version"], "2026.10.2")

        offline = check_for_content_update("http://127.0.0.1:9/manifest.json")
        self.assertEqual(offline.status, "offline")
        self.assertIn("last good pack", offline.message)
        self.assertEqual(content_root(), installed)

        older = dict(manifest)
        older["version"] = "2026.10.1"
        older["sha256"] = built.manifest["sha256"]
        older["filename"] = built.manifest["filename"]
        built.manifest_path.write_text(json.dumps(older), encoding="utf-8")
        stay = check_for_content_update(feed_url(httpd))
        self.assertEqual(stay.status, "current")
        self.assertEqual(content_root(), installed)
        self.assertEqual(read_config()["content_version"], "2026.10.2")

    def test_min_app_version_blocks_the_swap(self):
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root

        httpd, built = self._serve_pack("2026.10.4")
        manifest = json.loads(built.manifest_path.read_text(encoding="utf-8"))
        manifest["min_app_version"] = "9.0.0"
        built.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = check_for_content_update(feed_url(httpd))
        self.assertEqual(result.status, "needs_app")
        self.assertIn("last good pack", result.message)
        from fpfa.content_update import content_version_text

        self.assertEqual(content_version_text(), "source checkout")
        self.assertEqual(content_root(), REPO.resolve())

    def test_three_installs_keep_one_previous_pack(self):
        from fpfa.content_pack import build_pack
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root, data_dir

        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        httpd = serve(directory_handler(out))
        self.addCleanup(stop, httpd)
        for version in ("2026.10.1", "2026.10.2", "2026.10.3"):
            source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
            write_tree(source, {"skills/example/SKILL.md": version + "\n"})
            build_pack(source, out, version, changelog=[version])
            result = check_for_content_update(feed_url(httpd))
            self.assertEqual(result.status, "updated", result.message)
        root = content_root()
        self.assertEqual(root.name, "2026.10.3")
        parent = data_dir() / "content-packs"
        names = sorted(path.name for path in parent.iterdir() if path.is_dir() and not path.name.startswith("."))
        self.assertIn("2026.10.3", names)
        self.assertIn("2026.10.2", names)
        self.assertNotIn("2026.10.1", names)

    def test_env_pin_does_not_swap(self):
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root, read_config

        os.environ["FPFA_CONTENT_ROOT"] = str(REPO)
        httpd, _built = self._serve_pack("2026.10.5")
        result = check_for_content_update(feed_url(httpd))
        self.assertEqual(result.status, "pinned")
        self.assertIn("FPFA_CONTENT_ROOT", result.message)
        self.assertEqual(content_root(), REPO.resolve())
        self.assertNotIn("content_version", read_config())

    def test_check_without_apply_leaves_the_seed(self):
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root

        httpd, _built = self._serve_pack("2026.10.6")
        result = check_for_content_update(feed_url(httpd), apply=False)
        self.assertEqual(result.status, "available")
        self.assertEqual(content_root(), REPO.resolve())

    def test_unsafe_stripped_and_foreign_members_are_rejected(self):
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root, data_dir

        httpd, built = self._serve_pack("2026.10.1")
        installed = check_for_content_update(feed_url(httpd))
        self.assertEqual(installed.status, "updated")
        good = content_root()
        out = built.zip_path.parent

        def publish(members, version, symlinks=None):
            blob = zip_bytes(members, symlinks)
            filename = f"fp-fa-content-v{version}.zip"
            (out / filename).write_bytes(blob)
            manifest = {
                "version": version,
                "created": "2026-10-27T00:00:00Z",
                "sha256": hashlib.sha256(blob).hexdigest(),
                "filename": filename,
                "changelog": ["nope"],
            }
            (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        valid = {
            "skills/example/SKILL.md": b"ok\n",
            "calcs/fp/formulas.py": b"# fixture\n",
        }
        publish({**valid, "../sentinel-fpfa-test.txt": b"escape\n"}, "2026.10.7")
        slipped = check_for_content_update(feed_url(httpd))
        self.assertEqual(slipped.status, "rejected")
        self.assertIn("unsafe", slipped.message)
        self.assertEqual(list(data_dir().rglob("sentinel-fpfa-test.txt")), [])
        self.assertEqual(content_root(), good)

        publish({**valid, "skills/_sources/raw.md": b"raw\n"}, "2026.10.8")
        stripped = check_for_content_update(feed_url(httpd))
        self.assertEqual(stripped.status, "rejected")
        self.assertIn("stripped", stripped.message)
        self.assertEqual(content_root(), good)

        publish({**valid, "app/fpfa/keystore.py": b"key\n"}, "2026.10.9")
        foreign = check_for_content_update(feed_url(httpd))
        self.assertEqual(foreign.status, "rejected")
        self.assertIn("content folders", foreign.message)
        self.assertEqual(content_root(), good)

        publish(valid, "2026.10.10", symlinks={"skills/link.md": b"/tmp/outside"})
        linked = check_for_content_update(feed_url(httpd))
        self.assertEqual(linked.status, "rejected")
        self.assertIn("symlink", linked.message)
        self.assertEqual(content_root(), good)

    def test_redirect_uses_the_requested_feed_url(self):
        from fpfa.content_pack import build_pack
        from fpfa.content_update import check_for_content_update
        from fpfa.paths import content_root

        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source, {"skills/example/SKILL.md": "From the feed host.\n"})
        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        built = build_pack(source, out, "2026.10.11", changelog=["Redirected manifest"])
        routes = {
            "/cdn/manifest.json": built.manifest_path.read_bytes(),
            "/feed/" + built.manifest["filename"]: built.zip_path.read_bytes(),
        }

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urllib.parse.urlparse(self.path).path
                if path == "/feed/manifest.json":
                    port = self.server.server_address[1]
                    self.send_response(302)
                    self.send_header("Location", f"http://127.0.0.1:{port}/cdn/manifest.json")
                    self.end_headers()
                    return
                if path == "/cdn/" + built.manifest["filename"]:
                    self.send_error(404)
                    return
                payload = routes.get(path)
                if payload is None:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format, *args):
                return

        httpd = serve(Handler)
        self.addCleanup(stop, httpd)
        result = check_for_content_update(feed_url(httpd, "/feed/manifest.json"))
        self.assertEqual(result.status, "updated", result.message)
        self.assertIn("From the feed host.", (content_root() / "skills" / "example" / "SKILL.md").read_text())

    def test_github_release_document_points_at_the_manifest_asset(self):
        from fpfa.content_pack import build_pack
        from fpfa.content_update import check_for_content_update

        source = Path(tempfile.mkdtemp(prefix="fpfa-src-"))
        write_tree(source)
        out = Path(tempfile.mkdtemp(prefix="fpfa-out-"))
        built = build_pack(source, out, "2026.10.12", changelog=["From the release document"])
        filename = built.manifest["filename"]

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urllib.parse.urlparse(self.path).path
                port = self.server.server_address[1]
                if path == "/repos/releases/latest":
                    body = json.dumps({
                        "tag_name": "content-v2026.10.12",
                        "assets": [
                            {
                                "name": "manifest.json",
                                "browser_download_url": f"http://127.0.0.1:{port}/download/manifest.json",
                            },
                            {
                                "name": filename,
                                "browser_download_url": f"http://127.0.0.1:{port}/download/{filename}",
                            },
                        ],
                    }).encode("utf-8")
                elif path == "/download/manifest.json":
                    body = built.manifest_path.read_bytes()
                elif path == "/download/" + filename:
                    body = built.zip_path.read_bytes()
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                return

        httpd = serve(Handler)
        self.addCleanup(stop, httpd)
        result = check_for_content_update(feed_url(httpd, "/repos/releases/latest"))
        self.assertEqual(result.status, "updated", result.message)
        self.assertEqual(result.changelog, ["From the release document"])

    def test_missing_saved_root_falls_back_to_the_seed(self):
        from fpfa.paths import content_root, write_config

        write_config({"content_root": str(Path(tempfile.mkdtemp()) / "missing")})
        self.assertEqual(content_root(), REPO.resolve())

    def test_frozen_app_prefers_the_bundled_seed(self):
        import sys
        from unittest.mock import patch

        import fpfa.paths as paths

        parent = Path(tempfile.mkdtemp(prefix="fpfa-frozen-"))
        seed = parent / "seed"
        write_tree(seed, {"skills/example/SKILL.md": "Bundled seed.\n"})
        with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", str(parent), create=True):
            self.assertEqual(paths.content_root(), seed.resolve())
            from fpfa.content_update import content_version_text

            self.assertEqual(content_version_text(), "bundled seed")

    def test_pack_url_stays_on_the_requested_feed(self):
        from fpfa.content_update import ContentUpdateError, resolve_pack_url

        manifest = {"filename": "fp-fa-content-v2026.10.1.zip", "url": ""}
        requested = "https://github.com/Abe-Borg/fp-fa-content/releases/latest/download/manifest.json"
        self.assertEqual(
            resolve_pack_url(manifest, requested),
            "https://github.com/Abe-Borg/fp-fa-content/releases/latest/download/fp-fa-content-v2026.10.1.zip",
        )
        tagged = "https://github.com/Abe-Borg/fp-fa-content/releases/download/content-v2026.10.1/manifest.json"
        self.assertEqual(
            resolve_pack_url(manifest, tagged),
            "https://github.com/Abe-Borg/fp-fa-content/releases/download/content-v2026.10.1/fp-fa-content-v2026.10.1.zip",
        )
        with self.assertRaises(ContentUpdateError):
            resolve_pack_url({"filename": "x.zip", "url": "file:///tmp/x.zip"}, requested)

    def test_feed_request_omits_the_api_key(self):
        from fpfa.content_update import DEFAULT_FEED_URL, request_headers, resolved_feed_url, updates_on_launch
        from fpfa.paths import write_config

        headers = request_headers()
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("X-Api-Key", headers)
        self.assertNotIn("sk-ant-", " ".join(headers.values()))
        self.assertEqual(resolved_feed_url(), DEFAULT_FEED_URL)
        self.assertTrue(DEFAULT_FEED_URL.endswith("/manifest.json"))
        self.assertFalse(updates_on_launch())
        os.environ["FPFA_CONTENT_FEED_URL"] = "http://127.0.0.1:9/manifest.json"
        self.assertTrue(updates_on_launch())
        self.assertEqual(resolved_feed_url(), "http://127.0.0.1:9/manifest.json")
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        self.assertFalse(updates_on_launch())
        os.environ.pop("FPFA_CONTENT_UPDATES", None)
        os.environ.pop("FPFA_CONTENT_FEED_URL", None)
        write_config({
            "content_root": str(REPO),
            "content_version": "custom",
            "content_feed_url": "http://127.0.0.1:9/manifest.json",
        })
        self.assertFalse(updates_on_launch())
        os.environ["FPFA_CONTENT_UPDATES"] = "1"
        self.assertTrue(updates_on_launch())


class ContentUpdateUiTests(unittest.TestCase):
    def setUp(self):
        isolate()
        os.environ["FPFA_CONTENT_UPDATES"] = "0"

    def tearDown(self):
        os.environ.pop("FPFA_CONTENT_UPDATES", None)
        os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-test-")

    def _root(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        try:
            import tkinter as tk

            return tk.Tk()
        except Exception as exc:
            self.skipTest(f"tkinter display is not available ({exc})")

    def test_settings_shows_the_version_and_check_button(self):
        from fpfa.content_update import UpdateResult
        from fpfa.ui import App

        root = self._root()
        try:
            app = App(root)
            root.update_idletasks()
            root.update()
            self.assertIn("source checkout", app.content_status.get())
            app.open_settings()
            root.update_idletasks()
            root.update()
            labels = _button_labels(root)
            self.assertIn("Check for updates", labels)
            self.assertIn("Settings", labels)
            result = UpdateResult(
                status="updated",
                message="Content pack 2026.10.1 is installed.",
                version="2026.10.1",
                changelog=["Shorter screen note"],
            )
            app._finish_content_check(result, manual=True, status_var=None)
            root.update()
            self.assertIn("2026.10.1", app.content_banner.get())
            self.assertIn("Shorter screen note", app.content_banner.get())
            self.assertIn("source checkout", app._settings_version.get())
            self.assertIn("Shorter screen note", app._changelog_view.get("1.0", "end"))
        finally:
            root.destroy()


def _button_labels(widget) -> list[str]:
    found = []
    for child in widget.winfo_children():
        if child.winfo_class() in ("TButton", "Button"):
            found.append(child.cget("text"))
        found.extend(_button_labels(child))
    return found


if __name__ == "__main__":
    unittest.main()
