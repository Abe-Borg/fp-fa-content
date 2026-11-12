"""Settings update states in Chromium. Release results are fixtures; no model is called."""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@unittest.skipUnless(importlib.util.find_spec("playwright"), "Python Playwright is not installed")
class AppUpdateBrowserTests(unittest.TestCase):
    def test_settings_update_states_and_download_link_in_both_schemes(self):
        from playwright.sync_api import sync_playwright, expect
        from fpfa import __version__
        from fpfa.app_update import AppUpdateResult
        from fpfa.desk import Desk
        from fpfa.paths import write_config
        from fpfa.web.server import WindowServer

        with tempfile.TemporaryDirectory(prefix="fpfa-update-browser-") as folder, patch.dict(os.environ, {
            "FPFA_DATA_DIR": folder, "FPFA_CONTENT_UPDATES": "0", "FPFA_REDUCE_MOTION": "1",
        }), patch("fpfa.desk.load_api_key", return_value=None):
            write_config({"key_backend": "file"})
            desk = Desk()
            server = WindowServer(desk).start()
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=shutil.which("chromium") or None, headless=True, args=["--no-sandbox"])
                    try:
                        for scheme in ("clay", "linen"):
                            with self.subTest(scheme=scheme):
                                context = browser.new_context(viewport={"width": 1280, "height": 960}, device_scale_factor=1.5)
                                try:
                                    # The download target is observed without contacting GitHub in this fixture test.
                                    context.route("https://github.com/**", lambda route: route.fulfill(body="Release page fixture"))
                                    page = context.new_page()
                                    page.goto(server.page_url())
                                    page.wait_for_selector(".topbar")
                                    page.evaluate("""async scheme => {
                                        const token = new URLSearchParams(location.search).get('token');
                                        await fetch('/api/scheme', {method:'POST', headers:{'X-Cynosure-Token':token,'Content-Type':'application/json'}, body:JSON.stringify({id:scheme})});
                                    }""", scheme)
                                    expect(page.locator("html")).to_have_attribute("data-theme", scheme)
                                    errors = []
                                    page.on("pageerror", lambda error: errors.append(str(error)))
                                    page.get_by_role("button", name="Settings", exact=False).first.click()
                                    expect(page.locator(".settings")).to_be_visible()
                                    expect(page.get_by_role("button", name="Check for content updates", exact=True)).to_have_count(1)
                                    check = page.locator(".app-update-check")
                                    check.scroll_into_view_if_needed()
                                    started, finish = threading.Event(), threading.Event()
                                    url = "https://github.com/Abe-Borg/fp-fa-content/releases/tag/app-v9.0.0"
                                    def lookup():
                                        started.set()
                                        finish.wait(5)
                                        return AppUpdateResult("available", f"+Cynosure 9.0.0 is available. You have {__version__}.", "9.0.0", url)
                                    with patch("fpfa.desk.check_for_app_update", side_effect=lookup) as fetch:
                                        try:
                                            check.focus()
                                            page.keyboard.press("Enter")
                                            self.assertTrue(started.wait(2))
                                            expect(check).to_be_disabled()
                                            expect(check).to_have_text("Checking…")
                                            # Closing and reopening Settings keeps the same background check.
                                            page.get_by_role("button", name="Close", exact=True).click()
                                            page.get_by_role("button", name="Settings", exact=False).first.click()
                                            check.scroll_into_view_if_needed()
                                            expect(check).to_be_disabled()
                                            self.assertEqual(fetch.call_count, 1)
                                        finally:
                                            finish.set()
                                        download = page.get_by_role("link", name="Download update")
                                        expect(download).to_be_visible()
                                        expect(check).to_be_enabled()
                                        expect(download).to_have_attribute("href", url)
                                    page.locator(".settings").evaluate("node => node.scrollTop = node.scrollHeight")
                                    screenshots = os.environ.get("FPFA_UPDATE_SCREENSHOT_DIR")
                                    if screenshots:
                                        path = Path(screenshots)
                                        path.mkdir(parents=True, exist_ok=True)
                                        page.screenshot(path=str(path / f"settings-app-update-{scheme}.png"))
                                    with page.expect_popup() as popup_info:
                                        download.click()
                                    popup = popup_info.value
                                    popup.wait_for_load_state()
                                    self.assertEqual(popup.url, url)
                                    popup.close()
                                    with patch("fpfa.desk.check_for_app_update", return_value=AppUpdateResult("error", "Couldn’t check for updates. Check your connection and try again.")):
                                        check.click()
                                        expect(page.locator(".app-update-status")).to_contain_text("Couldn’t check")
                                        expect(download).to_have_count(0)
                                        expect(check).to_be_enabled()
                                    with patch("fpfa.desk.check_for_app_update", return_value=AppUpdateResult("current", f"You’re up to date. +Cynosure {__version__} is the latest version.")):
                                        check.click()
                                        expect(page.locator(".app-update-status")).to_contain_text("You’re up to date")
                                        expect(download).to_have_count(0)
                                    self.assertEqual(errors, [])
                                finally:
                                    context.close()
                    finally:
                        browser.close()
            finally:
                server.stop()
                desk.close()


if __name__ == "__main__":
    unittest.main()
