"""The native window around the page, and the app's entry point.

The page is shown in Microsoft's WebView2 control through pywebview, the way
Spec Surgeon shows its page: a native Windows window, the page drawn by the
same engine as Edge, and nothing leaving the machine but the model calls the
designer asks for. WebView2 ships with Windows 10 and 11. When pywebview or
its backend is missing (a source run on Linux, say), the page opens in the
default browser instead and the server runs until Ctrl+C.

run: python -m fpfa
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from fpfa import theme as palette
from fpfa.about import APP_NAME, APP_TAGLINE, version_text
from fpfa.desk import ANOTHER_WINDOW_TEXT, Desk, InstanceLockError, Shell
from fpfa.paths import data_dir, write_config
from fpfa.web.server import WindowServer

WINDOW_SIZE = (1280, 800)
MIN_SIZE = (1020, 680)
DOCX_TYPES = ("Word document (*.docx)",)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def native_backend_problem() -> str | None:
    """None when pywebview can open a native window here; else one line why not."""
    try:
        from webview.guilib import initialize
    except ImportError as exc:
        return f"pywebview is not installed ({exc})"
    try:
        initialize()
    except Exception as exc:  # a backend's own ImportError or load failure
        return f"pywebview has no native window backend on this computer ({exc})"
    return None


def exports_dir() -> Path:
    """Where an export goes when there is no native save dialog (the browser fallback)."""
    documents = Path.home() / "Documents"
    folder = (documents if documents.is_dir() else data_dir()) / "Cynosure exports"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _free_name(folder: Path, filename: str) -> Path:
    target = folder / filename
    stem, suffix = target.stem, target.suffix
    count = 2
    while target.exists():
        target = folder / f"{stem} ({count}){suffix}"
        count += 1
    return target


class BrowserShell(Shell):
    """The page in the default browser: no native dialog, so exports go to one folder."""

    def ask_save_path(self, title: str, filename: str) -> Path | None:
        return _free_name(exports_dir(), filename)


class WebviewShell(Shell):
    """pywebview's window: the native save dialog and the title bar's colours."""

    def __init__(self) -> None:
        self.window = None

    def ask_save_path(self, title: str, filename: str) -> Path | None:
        if self.window is None:
            return None
        import webview

        dialog = getattr(getattr(webview, "FileDialog", None), "SAVE", None)
        if dialog is None:
            dialog = webview.SAVE_DIALOG
        result = self.window.create_file_dialog(dialog, save_filename=filename, file_types=DOCX_TYPES)
        if not result:
            return None
        chosen = result[0] if isinstance(result, (list, tuple)) else result
        path = Path(str(chosen))
        return path if path.suffix.lower() == ".docx" else path.with_suffix(".docx")

    def handle(self) -> int:
        try:
            return int(self.window.native.Handle.ToInt64())
        except Exception:
            return 0

    def scheme_changed(self, scheme_id: str) -> None:
        palette.style_title_bar(self.handle(), scheme_id)


def _stop_on_signals() -> None:
    """The browser fallback waits for Ctrl+C. A termination request stops the wait the same way."""

    def stop(signum, frame):
        raise KeyboardInterrupt

    for name in ("SIGTERM", "SIGINT"):
        sig = getattr(signal, name, None)
        if sig is None:
            continue
        if name == "SIGINT" and signal.getsignal(sig) is not signal.SIG_IGN:
            continue
        try:
            signal.signal(sig, stop)
        except (ValueError, OSError):
            pass


def _show_error(text: str) -> None:
    """A message before any window exists: a Windows message box, else standard error."""
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, text, APP_NAME, 0x10)
            return
        except Exception:
            pass
    sys.stderr.write(text + "\n")


def take_screenshots(url: str, folder: Path) -> list[Path]:
    """The demo's pictures: the thread and the Zone details drawer, through the frontend's Playwright tool."""
    tool = FRONTEND / "tools" / "shoot.mjs"
    node = shutil.which("node")
    if node is None or not tool.is_file():
        sys.stderr.write("Screenshots need Node.js and app/frontend/tools/shoot.mjs (a source checkout).\n")
        return []
    folder.mkdir(parents=True, exist_ok=True)
    subprocess.run([node, str(tool), url, str(folder)], check=False, timeout=120)
    return sorted(folder.glob("*.png"))


def run_window(desk: Desk, server: WindowServer, shell: Shell, *, browser: bool = False) -> int:
    """Open the page and block until the window closes. Saving the open job comes first."""
    url = server.page_url(theme=desk.scheme)
    problem = None if not browser else "the browser was asked for"
    if problem is None:
        problem = native_backend_problem()
    if problem is None and isinstance(shell, WebviewShell):
        import webview

        background = palette.SCHEMES[palette.resolve_scheme(desk.scheme)].colors["bg"]
        window = webview.create_window(
            APP_NAME, url, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], min_size=MIN_SIZE,
            background_color=background, text_select=True, maximized=True,
        )
        shell.window = window

        def closing() -> bool:
            desk.call(desk.close)
            return True

        window.events.closing += closing
        window.events.shown += lambda: shell.scheme_changed(desk.scheme)
        webview.start(private_mode=True)
        return 0
    if not isinstance(shell, BrowserShell):
        desk.shell = BrowserShell()
    sys.stderr.write(f"{APP_NAME}: {problem}; opening the page in the default browser.\n")
    sys.stderr.write(f"{APP_NAME} is open at {server.base_url}/ — press Ctrl+C here to close it.\n")
    _stop_on_signals()
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    desk.call(desk.close)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="fpfa", description=f"{APP_NAME}: {APP_TAGLINE.lower()}.")
    parser.add_argument("--demo", action="store_true", help="Load the sample DI zone and run the tool plan")
    parser.add_argument("--quit", action="store_true", help="With --demo, exit after the run (and the screenshots)")
    parser.add_argument("--screenshot-dir", default="", help="With --demo, write PNGs of the window here")
    parser.add_argument("--export", default="", help="With --demo, write the draft .docx here")
    parser.add_argument("--versions", action="store_true", help="Print app, runtime, dependency, and content versions and exit")
    parser.add_argument(
        "--theme", default="", choices=("",) + palette.SCHEME_ORDER,
        help="Colour scheme for this run. Settings saves the lasting choice.",
    )
    parser.add_argument("--browser", action="store_true", help="Open the page in the default browser, not a window")
    parser.add_argument("--serve", action="store_true", help="Serve the page and print its address; open nothing")
    parser.add_argument("--port", type=int, default=0, help="With --serve or --browser, the port to listen on")
    parser.add_argument(
        "--live-eval", default="", metavar="FOLDER",
        help="Run the live evaluation path with no window and write a report into FOLDER. "
             "Calls the model with the saved key and is billed. See docs/live-evaluation.md",
    )
    parser.add_argument("--max-usd", type=float, default=25.0, help="With --live-eval, stop at about this spend. Default 25")
    parser.add_argument("--effort", default="", help="With --live-eval, the model's effort for the run. Default: the model's own")
    parser.add_argument("--eval-steps", default="", help="With --live-eval, the steps to run, comma-separated. Default: all")
    args = parser.parse_args(argv)
    if args.theme:
        os.environ["FPFA_THEME"] = args.theme
    if args.versions:
        sys.stdout.write(version_text() + "\n")
        return
    if args.live_eval:
        # Asked for by name, with a cap. A windowed build has no console to ask again on.
        from fpfa import live_eval

        options = ["--out", args.live_eval, "--max-usd", str(args.max_usd), "--yes"]
        if args.effort:
            options += ["--effort", args.effort]
        if args.eval_steps:
            options += ["--steps", args.eval_steps]
        sys.exit(live_eval.main(options))
    if args.demo:
        # Skip the OS keyring probe. The demo never calls Claude.
        write_config({"key_backend": "file"})

    wants_window = not args.serve and not (args.demo and args.quit and not args.screenshot_dir)
    shell: Shell
    if args.browser or args.serve or not wants_window:
        shell = BrowserShell()
    else:
        shell = WebviewShell() if native_backend_problem() is None else BrowserShell()
    try:
        desk = Desk(shell=shell)
    except InstanceLockError:
        _show_error(ANOTHER_WINDOW_TEXT)
        sys.exit(1)

    if args.demo and args.quit and not args.screenshot_dir:
        # The packaged smoke test: the sample and its tool plan, no window.
        try:
            desk.call(desk.load_demo)
            desk.pump()
            if args.export:
                try:
                    desk.call(desk.export_to, Path(args.export))
                except RuntimeError as exc:
                    sys.stderr.write(str(exc) + "\n")
            sys.stdout.write(desk.snapshot()["status"] + "\n")
        finally:
            desk.call(desk.close)
        return

    server = WindowServer(desk, port=args.port).start()
    try:
        desk.call(desk.start)
        if args.demo:
            desk.call(desk.load_demo)
            desk.pump()
            if args.export:
                try:
                    desk.call(desk.export_to, Path(args.export))
                except RuntimeError as exc:
                    sys.stderr.write(str(exc) + "\n")
        if args.screenshot_dir:
            for path in take_screenshots(server.page_url(theme=desk.scheme), Path(args.screenshot_dir)):
                sys.stdout.write(f"wrote {path}\n")
            if args.quit:
                return
        if args.serve:
            sys.stdout.write(f"{APP_NAME} is serving {server.page_url(theme=desk.scheme)}\n")
            sys.stdout.flush()
            _stop_on_signals()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            return
        run_window(desk, server, shell, browser=args.browser)
    finally:
        try:
            desk.call(desk.close)
        finally:
            server.stop()


if __name__ == "__main__":
    main()
