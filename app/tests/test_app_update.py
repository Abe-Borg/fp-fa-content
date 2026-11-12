"""App release selection and the Settings action; release responses are fixtures."""
from __future__ import annotations

import http.client
import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fpfa import app_update


def release(version: str, **fields) -> dict:
    return dict(tag_name=f"app-v{version}", draft=False, prerelease=False) | fields


class ReleaseTests(unittest.TestCase):
    def check(self, rows, installed="0.3.1"):
        with patch.object(app_update, "__version__", installed), patch.object(app_update, "_release_page", return_value=rows):
            return app_update.check_for_app_update()

    def test_selects_highest_numeric_app_version_not_first_or_content(self):
        result = self.check([
            release("0.9.0"), release("2026.99.0", tag_name="content-v2026.99.0"),
            release("0.11.0"), release("0.10.0"), release("9.0.0", draft=True),
            release("8.0.0", prerelease=True), release("10.0.0-beta.1"),
            release("banana"), release("7.0.0", draft=None),
        ])
        self.assertEqual((result.status, result.version), ("available", "0.11.0"))
        self.assertEqual(result.download_url, "https://github.com/Abe-Borg/fp-fa-content/releases/tag/app-v0.11.0")
        self.assertIn("0.3.1", result.message)

    def test_equal_and_ahead_versions_never_offer_a_downgrade(self):
        for installed in ("0.3.1", "0.4.0"):
            with self.subTest(installed=installed):
                result = self.check([release("0.3.1")], installed)
                self.assertEqual(result.status, "current")
                self.assertEqual(result.download_url, "")
        self.assertIn("newer", result.message)

    def test_no_stable_app_release_does_not_claim_up_to_date(self):
        for rows in ([], [release("1.0.0", tag_name="content-v1.0.0")], [release("2.0.0", prerelease=True)]):
            with self.subTest(rows=rows):
                self.assertEqual(self.check(rows).status, "unavailable")

    def test_reads_beyond_a_full_page_of_content_releases(self):
        with patch.object(app_update, "PAGE_SIZE", 2), patch.object(app_update, "_release_page", side_effect=[
            [release("1.0.0", tag_name="content-v1.0.0")] * 2, [release("2.0.0")],
        ]) as fetch:
            result = app_update.check_for_app_update()
        self.assertEqual(result.version, "2.0.0")
        self.assertEqual([call.args for call in fetch.call_args_list], [(1,), (2,)])

    def test_truncated_or_failed_history_does_not_claim_up_to_date(self):
        with patch.object(app_update, "MAX_PAGES", 1), patch.object(app_update, "PAGE_SIZE", 1):
            self.assertEqual(self.check([release("0.1.0")]).status, "error")
        with patch.object(app_update, "PAGE_SIZE", 1), patch.object(app_update, "_release_page", side_effect=[
            [release("0.1.0")], urllib.error.URLError("offline"),
        ]):
            self.assertEqual(app_update.check_for_app_update().status, "error")

    def test_http_request_is_bounded_and_contains_no_credentials(self):
        response = io.BytesIO(json.dumps([release("9.0.0")]).encode())
        with patch.object(app_update.urllib.request, "urlopen", return_value=response) as fetch:
            result = app_update.check_for_app_update()
        request = fetch.call_args.args[0]
        self.assertEqual(request.full_url, app_update.RELEASES_API + "?per_page=100&page=1")
        self.assertEqual(set(k.lower() for k in request.headers), {"user-agent", "accept", "x-github-api-version"})
        self.assertEqual(fetch.call_args.kwargs["timeout"], app_update.TIMEOUT_SECONDS)
        self.assertEqual(result.status, "available")

    def test_invalid_and_oversized_responses_are_retryable_errors(self):
        for raw in (b"not json", b'{"error":"failed"}', b'[null]', b'\xff', b'x' * 65):
            with self.subTest(raw=raw), patch.object(app_update, "MAX_RESPONSE_BYTES", 64), patch.object(
                app_update.urllib.request, "urlopen", return_value=io.BytesIO(raw)
            ):
                result = app_update.check_for_app_update()
                self.assertEqual(result.status, "error")
                self.assertEqual(result.download_url, "")

    def test_connection_timeout_and_http_failures_are_retryable(self):
        for error in (urllib.error.URLError("offline"), TimeoutError(), urllib.error.HTTPError("url", 429, "limited", {}, None),
                      urllib.error.HTTPError("url", 404, "missing", {}, None)):
            with self.subTest(error=error), patch.object(app_update.urllib.request, "urlopen", side_effect=error):
                result = app_update.check_for_app_update()
                self.assertEqual(result.status, "error")
                self.assertEqual(result.download_url, "")

    def test_download_address_comes_from_known_repository_not_remote_payload(self):
        result = self.check([release("9.0.0", html_url="https://untrusted.example/update")])
        self.assertTrue(result.download_url.startswith(app_update.PROJECT_URL + "/releases/tag/app-v"))


class SettingsActionTests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory(prefix="fpfa-app-update-"))
        self.enterContext(patch.dict(os.environ, {"FPFA_DATA_DIR": folder, "FPFA_CONTENT_UPDATES": "0"}))
        from fpfa.paths import write_config
        write_config({"key_backend": "file"})
        from fpfa.desk import Desk
        from fpfa.web.server import WindowServer
        self.enterContext(patch("fpfa.desk.load_api_key", return_value=None))
        self.desk = Desk()
        self.server = WindowServer(self.desk).start()
        self.addCleanup(self.desk.close)
        self.addCleanup(self.server.stop)

    def request(self, method, route, token=True):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.port, timeout=3)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Cynosure-Token"] = self.server.token
        connection.request(method, "/api/" + route, body="{}" if method == "POST" else None, headers=headers)
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def wait_result(self):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            state = self.request("GET", "state")[1]
            if state["settings"]["app_update"]["status"] != "checking":
                return state["settings"]["app_update"]
            time.sleep(0.01)
        self.fail("App update worker did not finish")

    def test_action_is_authenticated_nonblocking_deduplicated_and_independent(self):
        self.assertEqual(self.request("POST", "app-check", token=False)[0], 403)
        before = self.request("GET", "state")[1]
        self.assertEqual(before["settings"]["app_update"]["status"], "idle")
        started, finish = threading.Event(), threading.Event()
        expected = app_update.AppUpdateResult("available", "Version 2 is available", "2.0.0", app_update.PROJECT_URL + "/releases/tag/app-v2.0.0")
        def lookup():
            started.set()
            finish.wait(3)
            return expected
        with patch("fpfa.desk.check_for_app_update", side_effect=lookup) as check:
            try:
                self.assertEqual(self.request("POST", "app-check")[0], 200)
                self.assertTrue(started.wait(1))
                self.assertEqual(self.request("POST", "app-check")[0], 200)
                state = self.request("GET", "state")[1]
                self.assertEqual(state["settings"]["app_update"]["status"], "checking")
                self.assertEqual(check.call_count, 1)
                for key in ("content_line", "content_root", "content_version", "key_saved", "feed_url"):
                    self.assertEqual(state["settings"][key], before["settings"][key])
                self.assertEqual(state["thread"], before["thread"])
                self.assertEqual(state["projects"], before["projects"])
            finally:
                finish.set()
            self.assertEqual(self.wait_result()["download_url"], expected.download_url)

    def test_error_can_be_retried_and_previous_download_is_cleared(self):
        outcomes = [app_update.AppUpdateResult("available", "Available", "2.0.0", "https://github.com/example"),
                    RuntimeError("unexpected failure"), app_update.AppUpdateResult("current", "Up to date")]
        with patch("fpfa.desk.check_for_app_update", side_effect=outcomes):
            for status in ("available", "error", "current"):
                self.request("POST", "app-check")
                result = self.wait_result()
                self.assertEqual(result["status"], status)
                if status != "available":
                    self.assertEqual(result["download_url"], "")


if __name__ == "__main__":
    unittest.main()
