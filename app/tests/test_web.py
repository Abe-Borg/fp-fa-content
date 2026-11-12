"""The window: the local server (fpfa/web/server.py), its event stream, the built page, and the page in a browser.

The server tests talk HTTP to a real server on 127.0.0.1 and need no display.
The browser tests drive the page in Chromium with Playwright (frontend/tools/e2e.mjs,
e2e_team.mjs, and the screenshot tool, shoot.mjs) and are skipped where Node.js or
Playwright is not installed.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

FRONTEND = APP_DIR / "frontend"
STATIC = APP_DIR / "fpfa" / "web" / "static"

ANSWER = (
    "## Design basis for zone DH-1\n\n"
    "The zone is a **double-interlock preaction** system with `t_total` of 38.1 s. 🧯 𝐂 = 100.\n\n"
    "| Item | Value |\n| --- | --- |\n| Zone total | 281.3 gal |\n| t_total | 38.1 s |\n\n"
    + "\n\n".join(f"Paragraph {n}: the releasing panel waits for the detection leg and P, the pressure drop from sprinkler operation." for n in range(1, 25))
    + "\n\n1. Confirm the trim volume.\n2. Confirm the AHJ."
)


def _isolate() -> Path:
    path = Path(tempfile.mkdtemp(prefix="fpfa-web-"))
    os.environ["FPFA_DATA_DIR"] = str(path)
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    for name in ("FPFA_CONTENT_ROOT", "FPFA_THEME", "FPFA_REDUCE_MOTION"):
        os.environ.pop(name, None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return path


class Streaming:
    """A Claude that writes ANSWER a few characters at a time, slowly enough to watch."""

    delay = 0.03

    def __init__(self, _key):
        pass

    def create(self, **_kwargs):
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=ANSWER)])

    def streaming(self, on_event):
        from fpfa.claude_client import unheard

        if on_event is unheard:
            # A narration or a check streams with nobody drawing it. Only the chat reply is paced to be watched.
            return self.create

        def create(**_kwargs):
            on_event({"type": "thinking"})
            time.sleep(0.4)
            for start in range(0, len(ANSWER), 12):
                on_event({"type": "text", "text": ANSWER[start:start + 12]})
                time.sleep(self.delay)
            return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=ANSWER)])

        return create


class ServerCase(unittest.TestCase):
    key = False

    def setUp(self):
        _isolate()
        if self.key:
            from fpfa.keystore import save_api_key

            save_api_key("sk-ant-local-test")
        from fpfa.desk import Desk
        from fpfa.web.server import WindowServer

        self.desk = Desk()
        self.server = WindowServer(self.desk).start()
        self.addCleanup(self._stop)

    def _stop(self):
        self.server.stop()
        self.desk.close()

    def request(self, method: str, path: str, body=None, *, token: bool = True, headers: dict | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.port, timeout=10)
        sent = {"Content-Type": "application/json"}
        if token:
            sent["X-Cynosure-Token"] = self.server.token
        sent.update(headers or {})
        payload = json.dumps(body).encode("utf-8") if isinstance(body, (dict, list)) else body
        connection.request(method, path, body=payload, headers=sent)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        kind = response.getheader("Content-Type") or ""
        return response.status, (json.loads(data) if "json" in kind and data else data)

    def wait(self, until, timeout: float = 8.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.desk.lock:
                if until():
                    return
            time.sleep(0.02)
        self.fail("timed out")


class GuardTests(ServerCase):
    def test_every_api_request_needs_the_launch_token(self):
        status, body = self.request("GET", "/api/state", token=False)
        self.assertEqual(status, 403)
        self.assertFalse(body["ok"])
        status, _ = self.request("GET", "/api/state", token=False, headers={"X-Cynosure-Token": "wrong"})
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/api/new", {}, token=False)
        self.assertEqual(status, 403)
        status, body = self.request("GET", f"/api/health?token={self.server.token}", token=False)
        self.assertEqual((status, body["ok"]), (200, True))

    def test_another_host_or_another_site_is_refused(self):
        status, _ = self.request("GET", "/api/state", headers={"Host": f"evil.example:{self.server.port}"})
        self.assertEqual(status, 421)
        status, _ = self.request("POST", "/api/new", {}, headers={"Origin": "http://evil.example"})
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/api/new", {}, headers={"Origin": "null"})
        self.assertEqual(status, 403)
        status, body = self.request("POST", "/api/new", {}, headers={"Origin": f"http://127.0.0.1:{self.server.port}"})
        self.assertEqual((status, body["ok"]), (200, True))

    def test_a_bad_request_is_answered_and_changes_nothing(self):
        self.assertEqual(self.request("POST", "/api/no-such-action", {})[0], 404)
        self.assertEqual(self.request("POST", "/api/send", b"{not json")[0], 400)
        self.assertEqual(self.request("POST", "/api/send", [1, 2])[0], 400)
        self.assertEqual(self.request("GET", "/api/no-such-route")[0], 404)
        self.assertEqual(self.request("GET", "/api/text/secrets")[0], 404)
        # A body over the limit is refused from its declared length, before it is read.
        status, _ = self.request("POST", "/api/send", b"{}", headers={"Content-Length": "1100000"})
        self.assertEqual(status, 413)
        self.assertIsNone(self.desk.project)

    def test_the_page_is_served_and_nothing_outside_it(self):
        status, body = self.request("GET", "/", token=False)
        self.assertEqual(status, 200)
        self.assertIn(b'<div id="root">', body)
        for path in ("/../desk.py", "/%2e%2e/desk.py", "/../../requirements.txt"):
            self.assertEqual(self.request("GET", path, token=False)[0], 404, path)


class ActionTests(ServerCase):
    def test_the_sample_runs_and_the_state_carries_the_thread(self):
        status, body = self.request("POST", "/api/sample-di", {})
        self.assertEqual((status, body["ok"]), (200, True))
        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(state["title"], "Sample data hall DI zone")
        turns = state["thread"]["turns"]
        self.assertEqual(turns[0], {"role": "user", "text": "/sample-di"})
        self.assertIn("5.0 gal trim ASSUMED", turns[1]["text"])
        self.assertIn("281.3", state["results"])
        self.assertEqual(len(state["form"]["segments"]), 4)
        self.assertEqual(state["activity"][0]["kind"], "zone")
        self.assertEqual(state["lives"], [])

    def test_form_fields_travel_without_reloading_the_page_form(self):
        self.request("POST", "/api/sample-di", {})
        rev = self.desk.form_rev
        self.request("POST", "/api/form", {"values": {"zone_id": "DH-7", "qod": True, "hazard": "no-such-hazard", "nope": 1}})
        self.assertEqual(self.desk.zone_id.get(), "DH-7")
        self.assertTrue(self.desk.qod.get())
        self.assertEqual(self.desk.hazard.get(), "ordinary", "a choice the form does not offer is ignored")
        self.assertEqual(self.desk.form_rev, rev, "the page's own typing does not send the form back to it")
        self.request("POST", "/api/form", {"values": {"trim_gal": "10"}})
        self.assertIn("10 gal entered on the form. Not assumed.", self.desk.snapshot()["form"]["assumptions"])
        # A segment the app resolves changes the form under the page, so the page reloads it.
        status, body = self.request("POST", "/api/segment-add", {"role": "main", "nps": "4", "schedule": "", "length": "40"})
        self.assertEqual((status, body["result"]), (200, True))
        self.assertGreater(self.desk.form_rev, rev)
        self.assertEqual(self.desk.segments[-1]["d_in"], "4.260")
        status, body = self.request("POST", "/api/segment-add", {"role": "main", "nps": "", "length": "40"})
        self.assertFalse(body["result"])
        self.assertEqual(self.desk.notices[-1]["title"], "Segment")
        count = len(self.desk.segments)
        self.request("POST", "/api/segment-remove", {"index": count - 1})
        self.assertEqual(len(self.desk.segments), count - 1)

    def test_rename_delete_and_a_notice_round_trip(self):
        self.request("POST", "/api/sample-di", {})
        project_id = self.desk.project["id"]
        self.request("POST", "/api/rename", {"id": project_id, "name": "  Hall 2   zoning "})
        self.assertEqual(self.desk.snapshot()["projects"], [{"id": project_id, "name": "Hall 2 zoning"}])
        self.request("POST", "/api/delete", {"id": project_id})
        state = self.desk.snapshot()
        self.assertEqual((state["projects"], state["open"]), ([], None))
        self.request("POST", "/api/export-section", {})
        notice = self.desk.snapshot()["notices"][-1]
        self.assertEqual(notice["title"], "Export")
        self.request("POST", "/api/notice-dismiss", {"id": notice["id"]})
        self.assertEqual(self.desk.snapshot()["notices"], [])

    def test_the_long_texts_of_settings(self):
        from fpfa.about import LICENSE_NAME

        status, body = self.request("GET", "/api/text/license")
        self.assertEqual(status, 200)
        self.assertIn("PolyForm Shield", body["text"])
        self.assertIn(LICENSE_NAME.split()[0], body["text"])
        status, body = self.request("GET", "/api/text/about")
        self.assertIn("Record schema", body["text"])
        status, body = self.request("GET", "/api/text/notices")
        self.assertEqual(status, 200)
        self.assertTrue(body["text"])

    def test_settings_change_through_the_api(self):
        from fpfa.paths import read_config

        self.request("POST", "/api/scheme", {"id": "linen"})
        self.assertEqual(read_config()["appearance"], "linen")
        self.request("POST", "/api/motion", {"reduce": True})
        self.assertTrue(self.desk.snapshot()["settings"]["reduce_motion"])
        self.request("POST", "/api/key-save", {"key": ""})
        self.assertIn("Paste a key", self.desk.snapshot()["settings"]["key_message"])
        self.request("POST", "/api/key-save", {"key": "sk-ant-local-test"})
        settings = self.desk.snapshot()["settings"]
        self.assertTrue(settings["key_saved"])
        self.assertTrue(self.desk.snapshot()["narrate"])
        self.request("POST", "/api/key-clear", {})
        self.assertFalse(self.desk.snapshot()["settings"]["key_saved"])
        # The key never travels in the state.
        self.request("POST", "/api/key-save", {"key": "sk-ant-local-test"})
        self.assertNotIn("sk-ant-local-test", json.dumps(self.request("GET", "/api/state")[1]))

    def test_the_page_tells_the_app_how_the_window_was_left(self):
        from fpfa.paths import read_config

        status, state = self.request("GET", "/api/state")
        self.assertEqual(state["settings"]["layout"], {"sidebar": True, "panel": "", "panel_width": 0})
        status, _reply = self.request("POST", "/api/layout", {"values": {"panel": "results", "panel_width": 640, "sidebar": False}})
        self.assertEqual(status, 200)
        self.assertEqual(read_config()["layout"], {"sidebar": False, "panel": "results", "panel_width": 640})
        self.assertEqual(self.request("GET", "/api/state")[1]["settings"]["layout"]["panel"], "results")
        # Anything that is not a layout changes nothing.
        for body in ({"values": "team"}, {"values": {"panel": "drawer"}}, {}):
            self.request("POST", "/api/layout", body)
        self.assertEqual(read_config()["layout"]["panel_width"], 640)
        self.assertEqual(read_config()["layout"]["panel"], "")

    def test_the_state_carries_the_run_as_figures(self):
        self.request("POST", "/api/narrate", {"on": False})
        self.request("POST", "/api/sample-di", {})
        self.wait(lambda: self.desk.run_rev == 1)
        state = self.request("GET", "/api/state")[1]
        self.assertEqual(state["run_rev"], 1)
        figures = {figure["key"]: figure for figure in state["results_view"]["figures"]}
        self.assertEqual((figures["zone_total"]["value"], figures["zone_total"]["unit"]), ("281.3", "gal"))
        self.assertEqual(figures["t_total"]["verdict"], "The zone-total screen does not pass.")
        self.assertNotIn("low" + "_air", json.dumps(state["results_view"]))


def read_events(port: int, token: str, stop, out: list, *, deadline: float = 30.0) -> None:
    """Read the event stream into out as (event, data) until stop() says so or the deadline passes."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=deadline)
    connection.request("GET", f"/api/events?token={token}")
    response = connection.getresponse()
    kind, data = None, []
    end = time.time() + deadline
    while time.time() < end and not stop():
        line = response.fp.readline()
        if not line:
            break
        line = line.decode("utf-8").rstrip("\n")
        if line.startswith("event: "):
            kind = line[7:]
        elif line.startswith("data: "):
            data.append(line[6:])
        elif line == "" and kind:
            out.append((kind, json.loads("\n".join(data))))
            kind, data = None, []
    connection.close()


class EventStreamTests(ServerCase):
    key = True

    def test_a_streamed_reply_arrives_word_by_word_and_ends_as_a_turn(self):
        events: list = []
        finished = threading.Event()
        reader = threading.Thread(
            target=read_events, args=(self.server.port, self.server.token, finished.is_set, events), daemon=True
        )
        reader.start()
        self.wait(lambda: len(events) >= 0)
        time.sleep(0.3)
        self.assertEqual(events[0][0], "state", "a new connection starts with the whole state")
        self.assertEqual(events[0][1]["thread"]["turns"], [])
        with patch("fpfa.desk.AnthropicMessages", Streaming):
            status, _ = self.request("POST", "/api/send", {"text": "Give me the design basis for zone DH-1."})
            self.assertEqual(status, 200)
            self.wait(lambda: self.desk.chat_log and self.desk.chat_log[-1]["role"] == "assistant", timeout=30)
        time.sleep(0.5)
        finished.set()
        reader.join(5)
        lives = [data for kind, data in events if kind == "live"]
        self.assertGreater(len(lives), 3, "the words come in several messages")
        # Each message carries on exactly where the last one ended, counted as the page counts:
        # in UTF-16 units, so the emoji and the mathematical C (two units each) do not throw it off.
        from fpfa.web.server import utf16_length

        self.assertEqual(utf16_length("🧯𝐂a"), 5)
        text = ""
        for data in lives:
            if data["start"] == 0:
                text = data["text"]
            else:
                self.assertEqual(data["start"], utf16_length(text))
                text += data["text"]
        self.assertIn("🧯 𝐂 = 100.", text)
        self.assertTrue(text.startswith("Job "))
        self.assertIn("| chat", text.splitlines()[0])
        self.assertTrue(ANSWER.startswith(text.split("\n", 1)[1][: len(ANSWER)]))
        self.assertIn(("live_end", {"job_id": lives[0]["job_id"]}), events)
        states = [data for kind, data in events if kind == "state"]
        working = [state["pending"] for state in states if state["pending"]]
        self.assertTrue(any(item["detail"] == "writing the reply" for item in working))
        self.assertTrue(all("{" not in item["detail"] for item in working), "the working line names, never shows inputs")
        last = [state for state in states if "turns" in state["thread"]][-1]
        self.assertIn(ANSWER, last["thread"]["turns"][-1]["text"])
        self.assertEqual(last["thread"]["turns"][-1]["job_id"], lives[0]["job_id"])
        # A state that did not change the thread does not send it again.
        self.assertTrue(any("turns" not in state["thread"] for state in states))

    def test_a_job_on_another_project_streams_nothing_into_the_open_one(self):
        events: list = []
        finished = threading.Event()
        threading.Thread(target=read_events, args=(self.server.port, self.server.token, finished.is_set, events),
                         daemon=True).start()
        with patch("fpfa.desk.AnthropicMessages", Streaming):
            self.request("POST", "/api/send", {"text": "Which trim family?"})
            origin = self.desk.project["id"]
            self.request("POST", "/api/send", {"text": "/new Other hall"})
            self.wait(lambda: not self.desk._project_running(origin), timeout=30)
        time.sleep(0.3)
        finished.set()
        live_after_switch = []
        switched = False
        for kind, data in events:
            if kind == "state" and data["open"] and data["open"]["name"] == "Other hall":
                switched = True
            elif kind == "live" and switched:
                live_after_switch.append(data)
        self.assertEqual(live_after_switch, [])
        from fpfa.projects import load_project

        self.assertIn(ANSWER, load_project(origin)["chat"][-1]["text"])


def _source_hash() -> str:
    """The hash vite.config.ts writes into build.json, worked out the same way."""
    names: list[str] = []
    for item in ("index.html", "package.json", "package-lock.json", "vite.config.ts", "tsconfig.json", "src"):
        path = FRONTEND / item
        if path.is_dir():
            names.extend(str(child.relative_to(FRONTEND)).replace("\\", "/") for child in path.rglob("*") if child.is_file())
        else:
            names.append(item)
    digest = hashlib.sha256()
    for name in sorted(names):
        text = (FRONTEND / name).read_text(encoding="utf-8").replace("\r\n", "\n")
        digest.update((name + "\0" + text + "\0").encode("utf-8"))
    return digest.hexdigest()


class BuiltPageTests(unittest.TestCase):
    def test_the_committed_page_is_built_from_the_source_in_this_tree(self):
        stamp = json.loads((STATIC / "build.json").read_text(encoding="utf-8"))
        self.assertEqual(stamp["sources"], _source_hash(), "run `npm run build` in app/frontend and commit fpfa/web/static")

    def test_the_page_names_only_files_it_ships(self):
        index = (STATIC / "index.html").read_text(encoding="utf-8")
        assets = re.findall(r'(?:src|href)="/(assets/[^"]+)"', index)
        self.assertTrue(any(name.endswith(".js") for name in assets))
        self.assertTrue(any(name.endswith(".css") for name in assets))
        for name in assets:
            self.assertTrue((STATIC / name).is_file(), name)
        shipped = {path.name for path in (STATIC / "assets").iterdir()}
        self.assertEqual(shipped, {Path(name).name for name in assets}, "an old build's files are left in static/")
        # Nothing is fetched from the network: the window works offline.
        bundle = "".join((STATIC / name).read_text(encoding="utf-8") for name in assets)
        self.assertNotRegex(index, r"https?://(?!www\.w3\.org)")
        self.assertNotIn("fonts.googleapis", bundle)

    def test_every_bundled_package_has_its_license_text(self):
        licenses = json.loads((STATIC / "licenses.json").read_text(encoding="utf-8"))["packages"]
        names = {item["name"] for item in licenses}
        self.assertTrue({"react", "react-dom", "scheduler"} <= names, names)
        for item in licenses:
            self.assertTrue(item["version"], item["name"])
            self.assertTrue(item["license"], item["name"])
            self.assertGreater(len(item["text"]), 200, item["name"])
            self.assertIn("Permission is hereby granted", item["text"], item["name"])

    def test_vites_modulepreload_polyfill_is_not_in_the_page_while_licenses_json_lists_no_vite(self):
        """The polyfill is Vite's own code (MIT), and the page's build turns it off (build.modulePreload).

        It is what reads a link's relList; nothing else in the page does. The build itself fails on any
        module it cannot attribute (app/frontend/tests/licenses.test.ts); this reads the page that ships.
        """
        index = (STATIC / "index.html").read_text(encoding="utf-8")
        bundle = "".join((STATIC / name).read_text(encoding="utf-8")
                         for name in re.findall(r'src="/(assets/[^"]+\.js)"', index))
        names = {item["name"] for item in json.loads((STATIC / "licenses.json").read_text(encoding="utf-8"))["packages"]}
        if "vite" not in names:
            self.assertNotIn("relList", bundle, "Vite's modulepreload polyfill is in the page, and licenses.json lists no vite")

    def test_the_menus_are_in_the_page(self):
        index = (STATIC / "index.html").read_text(encoding="utf-8")
        bundle = "".join((STATIC / name).read_text(encoding="utf-8")
                         for name in re.findall(r'src="/(assets/[^"]+\.js)"', index))
        for label in ("Sample DI zone", "Sample BESS room", "Run zone", "Team panel",
                      "Usage and cost", "Narrate zone runs with Claude", "Rename job…", "Settings…", "Commands",
                      "About and versions", "Cancel running job", "Run trace check", "Export basis…",
                      "Where this job stands", "Status to thread", "NEEDS YOUR ANSWER", "NOT YET RECONCILED"):
            self.assertIn(label, bundle)


class KeyStoreTests(unittest.TestCase):
    def test_drawing_the_state_never_asks_the_key_store(self):
        """On a Windows source run each ask is a child Python that can wait 8 s, and the state is drawn often."""
        _isolate()
        from fpfa.desk import Desk

        desk = Desk()
        self.addCleanup(desk.close)
        with patch("fpfa.desk.load_api_key", side_effect=AssertionError("asked the key store")) as asked:
            for _ in range(3):
                state = desk.snapshot()
            desk.send_chat("/help")
            desk.pump()
            desk.snapshot()
        asked.assert_not_called()
        self.assertFalse(state["settings"]["key_saved"])
        self.assertEqual([chip["action"] for chip in state["chips"]], ["/sample-di", "/help"])
        # A question, which needs a key, does ask, so a key saved since is found.
        from fpfa.keystore import save_api_key

        save_api_key("sk-ant-local-test")
        with patch("fpfa.desk.AnthropicMessages", Streaming):
            desk.send_chat("Which trim family?")
        self.assertTrue(desk.snapshot()["settings"]["key_saved"])


class EntryPointTests(unittest.TestCase):
    def test_demo_and_quit_runs_the_sample_without_a_window(self):
        import io
        from contextlib import redirect_stdout

        _isolate()
        from fpfa.web.shell import main

        out = io.StringIO()
        with patch("fpfa.web.shell.WindowServer") as server, patch("fpfa.web.shell.run_window") as window, \
                redirect_stdout(out):
            main(["--demo", "--quit"])
        server.assert_not_called()
        window.assert_not_called()
        self.assertIn("Tool plan only.", out.getvalue())
        from fpfa.projects import list_projects

        self.assertEqual([row["name"] for row in list_projects()], ["Sample data hall DI zone"])

    def test_a_second_window_on_the_same_data_directory_is_refused(self):
        _isolate()
        from fpfa.desk import Desk, InstanceLockError

        first = Desk()
        try:
            with self.assertRaises(InstanceLockError):
                Desk()
        finally:
            first.close()
        Desk().close()

    def test_the_browser_fallback_saves_exports_in_one_folder_without_overwriting(self):
        _isolate()
        from fpfa.web.shell import BrowserShell

        home = Path(tempfile.mkdtemp(prefix="fpfa-home-"))
        with patch("fpfa.web.shell.Path.home", return_value=home):
            shell = BrowserShell()
            first = shell.ask_save_path("Export", "Hall.docx")
            first.write_bytes(b"x")
            second = shell.ask_save_path("Export", "Hall.docx")
        self.assertEqual(first.name, "Hall.docx")
        self.assertEqual(second.name, "Hall (2).docx")
        self.assertEqual(first.parent, second.parent)


def _playwright_problem() -> str | None:
    node = shutil.which("node")
    if node is None:
        return "Node.js is not installed"
    probe = subprocess.run([node, "-e", "require('playwright')"], capture_output=True, text=True, timeout=30)
    if probe.returncode != 0:
        return "Playwright is not installed for Node.js"
    return None


class BrowserTests(unittest.TestCase):
    def test_the_page_in_a_browser(self):
        problem = _playwright_problem()
        if problem:
            self.skipTest(problem)
        _isolate()
        from fpfa.keystore import save_api_key

        save_api_key("sk-ant-local-test")
        from fpfa.desk import Desk
        from fpfa.web.server import WindowServer

        with patch("fpfa.desk.AnthropicMessages", Streaming):
            desk = Desk()
            server = WindowServer(desk).start()
            try:
                run = subprocess.run(
                    [shutil.which("node"), str(FRONTEND / "tools" / "e2e.mjs"), server.page_url()],
                    capture_output=True, text=True, timeout=240,
                )
            finally:
                server.stop()
                desk.close()
        lines = [line for line in run.stdout.splitlines() if line.startswith("{")]
        self.assertTrue(lines, run.stdout + run.stderr)
        report = json.loads(lines[-1])
        self.assertTrue(report["ok"], json.dumps(report, indent=2))
        self.assertGreater(report["checks"], 30)

    def test_the_team_panel_in_a_browser(self):
        """A job with a team's work on its record: the strip, the panel, an answer, and a run left behind."""
        problem = _playwright_problem()
        if problem:
            self.skipTest(problem)
        _isolate()
        from fpfa.desk import Desk
        from fpfa.keystore import save_api_key
        from fpfa.web.server import WindowServer
        from team_fixture import seed_team_state

        save_api_key("sk-ant-local-test")
        desk = Desk()
        with desk.lock:
            desk.ask_claude.set(False)
            desk.start_sample_di()
            desk.pump()
            seeded = seed_team_state(desk)
            desk.pump()
        server = WindowServer(desk).start()
        try:
            run = subprocess.run(
                [shutil.which("node"), str(FRONTEND / "tools" / "e2e_team.mjs"), server.page_url()],
                capture_output=True, text=True, timeout=240,
            )
            lines = [line for line in run.stdout.splitlines() if line.startswith("{")]
            self.assertTrue(lines, run.stdout + run.stderr)
            report = json.loads(lines[-1])
            self.assertTrue(report["ok"], json.dumps(report, indent=2))
            self.assertGreater(report["checks"], 30)
            # What the page did is on the record: the answer, under the designer's name, and the saved field.
            with desk.lock:
                row = next(item for item in desk.record.questions(seeded["project"]) if item["id"] == seeded["ask"])
                given = desk.record.givens(seeded["project"])["q_fill_gpm"]
            self.assertEqual((row["status"], row["answer"], row["answered_by"]),
                             ("answered", "6.5 gallons, from the submittal.", "designer"))
            self.assertEqual(given["value"], "750.0")
        finally:
            server.stop()
            desk.close()

    def test_the_chat_filling_the_inputs_in_a_browser(self):
        """A scripted lead fills two basis fields, then (ask first) proposes a third: the card, Show, Undo, Apply."""
        problem = _playwright_problem()
        if problem:
            self.skipTest(problem)
        _isolate()
        from fpfa.desk import Desk
        from fpfa.keystore import save_api_key
        from fpfa.web.server import WindowServer
        from test_team_protocol import Play, call, say, use

        save_api_key("sk-ant-local-test")
        play = Play({"lead": [
            call(use("set_input", name="ahj", value="City of Irvine", why="“The AHJ is the City of Irvine”"),
                 use("set_input", name="insurer", value="FM Global", why="“the insurer is FM Global”")),
            say("I put the AHJ and the insurer on the Inputs tab."),
            call(use("set_input", name="hazard_notes", value="Single-story hall, hot-aisle containment.",
                     why="“single-story hall, hot-aisle containment”")),
            say("The hazard notes wait for your OK."),
        ]})

        class Client:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                return play(**kwargs)

        with patch("fpfa.desk.AnthropicMessages", Client):
            desk = Desk()
            server = WindowServer(desk).start()
            try:
                run = subprocess.run(
                    [shutil.which("node"), str(FRONTEND / "tools" / "e2e_fill.mjs"), server.page_url()],
                    capture_output=True, text=True, timeout=240,
                )
                lines = [line for line in run.stdout.splitlines() if line.startswith("{")]
                self.assertTrue(lines, run.stdout + run.stderr)
                report = json.loads(lines[-1])
                self.assertTrue(report["ok"], json.dumps(report, indent=2))
                self.assertGreaterEqual(report["checks"], 20)
                self.assertEqual({kind: steps for kind, steps in play.scripts.items() if steps}, {}, "the lead's script was played to its end")
                with desk.lock:
                    given = desk.record.givens(desk.project["id"])
                self.assertEqual((given["hazard_notes"]["value"], given["hazard_notes"]["agent"]),
                                 ("Single-story hall, hot-aisle containment.", "designer"))
                self.assertEqual(given["insurer"]["value"], "FM")
            finally:
                server.stop()
                desk.close()


class ScreenshotToolTests(unittest.TestCase):
    """frontend/tools/shoot.mjs, the pictures CLAUDE.md asks for after a change to the window.

    The page draws the scheme the app serves, whatever its address says. A picture is never named for a
    scheme or a device scale it was not drawn in: asked for another scheme, the tool stops and writes nothing.
    """

    TOOL = FRONTEND / "tools" / "shoot.mjs"

    def _shoot(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [shutil.which("node"), str(self.TOOL), *arguments], capture_output=True, text=True, timeout=120,
        )

    @contextmanager
    def _serving(self, theme: str = "", panel: str = ""):
        """The sample zone, served the way python -m fpfa --demo --serve [--theme <id>] serves it, with the window
        left on the tab named. Yields the address that command prints."""
        _isolate()
        # --theme sets FPFA_THEME for its run. Nothing here saves a scheme.
        with patch.dict(os.environ, {"FPFA_THEME": theme} if theme else {}):
            from fpfa.desk import Desk
            from fpfa.web.server import WindowServer

            desk = Desk()
            server = WindowServer(desk).start()
            try:
                desk.call(desk.load_demo)
                desk.pump()
                if panel:
                    desk.call(desk.set_layout, {"panel": panel})
                yield server.page_url(theme=desk.scheme)
            finally:
                server.stop()
                desk.close()

    @staticmethod
    def _pictures(folder: Path) -> dict[str, tuple[int, int]]:
        """Each PNG in the folder, with its width and height in pixels from its header."""
        return {path.name: struct.unpack(">II", path.read_bytes()[16:24]) for path in sorted(folder.glob("*.png"))}

    def test_an_argument_it_cannot_use_stops_it_before_a_browser_opens(self):
        if shutil.which("node") is None:
            self.skipTest("Node.js is not installed")
        folder = Path(tempfile.mkdtemp(prefix="fpfa-shoot-")) / "pictures"
        # Nothing listens at this address. Each refusal comes before a browser would ask it, and before
        # Playwright is loaded, so this runs where Playwright is not installed.
        address = "http://127.0.0.1:9/?token=unused"
        cases = {
            (): "usage:",
            # Windows states its display scale in percent.
            (address, str(folder), "linen", "150"): "1.5 for a display at 150%",
            (address, str(folder), "linen", "0.5"): "from 1 to 5",
            (address, str(folder), "linen", "2x"): "from 1 to 5",
            (address, str(folder), "Linen"): '"Linen" is not a scheme id',
            # A scale in the scheme's place.
            (address, str(folder), "2"): "linen 2",
        }
        for arguments, said in cases.items():
            with self.subTest(arguments=arguments):
                run = self._shoot(*arguments)
                self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                self.assertIn(said, run.stderr)
        self.assertFalse(folder.exists())

    def test_asked_for_another_scheme_than_the_app_serves_it_stops_and_writes_nothing(self):
        problem = _playwright_problem()
        if problem:
            self.skipTest(problem)
        folder = Path(tempfile.mkdtemp(prefix="fpfa-shoot-")) / "pictures"
        with self._serving() as address:
            self.assertIn("theme=clay", address)
            # The address can name linen. The page still draws the app's scheme once the app's state arrives.
            run = self._shoot(address.replace("theme=clay", "theme=linen"), str(folder), "linen")
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("asked for linen, but the page is drawn in clay", run.stderr)
        self.assertIn("--theme linen", run.stderr)
        self.assertIn("Nothing was written.", run.stderr)
        self.assertFalse(folder.exists())

    def test_the_scheme_the_app_serves_is_shot_at_the_scale_asked_for(self):
        problem = _playwright_problem()
        if problem:
            self.skipTest(problem)
        root = Path(tempfile.mkdtemp(prefix="fpfa-shoot-"))
        # The check CLAUDE.md asks for: Linen, served with --theme linen, at a device scale above 1. The window
        # was left on the Inputs tab, whose button closes that tab when it is pressed again.
        with self._serving("linen", panel="inputs") as address:
            run = self._shoot(address, str(root / "linen"), "linen", "2")
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            # Named for no scheme or scale: the names --demo --screenshot-dir has always written, at 1440 by 900.
            plain = self._shoot(address, str(root / "plain"))
            self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertEqual(self._pictures(root / "linen"), {
            "di_zone_inputs-linen@2x.png": (2880, 1800),
            "di_zone_results-linen@2x.png": (2880, 1800),
            "thread-linen@2x.png": (2880, 1800),
        })
        self.assertEqual(self._pictures(root / "plain"), {
            "di_zone_inputs.png": (1440, 900),
            "di_zone_results.png": (1440, 900),
            "thread.png": (1440, 900),
        })


if __name__ == "__main__":
    unittest.main()
