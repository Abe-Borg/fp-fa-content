"""The README's pictures, taken again:  python tests/docs_pictures.py [folder]

SIMULATED. No model is called. The job in the pictures is the first turn of
tests/team_scenario.py: every agent's moves are a script written in advance,
played through the real application, which builds the messages, runs the
calc kernels, writes the record, and draws the window. A second, empty data
directory gives the opening screen and Settings. The pictures show what the
window does with such a job. They do not show what a live model writes.

Needs Node.js with Playwright (frontend/tools/shoot_docs.mjs). The default
folder is docs/screenshots. Nothing here touches the owner's jobs: each
window runs in a data directory of its own that is made for it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
TOOL = APP_DIR / "frontend" / "tools" / "shoot_docs.mjs"
for folder in (APP_DIR, Path(__file__).resolve().parent):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))


def _fresh_data_dir(name: str) -> None:
    os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix=f"fpfa-pictures-{name}-")
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    for variable in ("FPFA_CONTENT_ROOT", "FPFA_THEME", "FPFA_REDUCE_MOTION"):
        os.environ.pop(variable, None)
    from fpfa.keystore import save_api_key
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    # A stand-in key, so the window draws as it does for a designer who has saved one. It is never sent.
    save_api_key("sk-ant-local-test")


def _settle(desk, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        desk.pump()
        if not desk._pending_here():
            desk.pump()
            return
        time.sleep(0.02)
    raise RuntimeError("the scripted turn did not finish")


def _shoot(desk, out: Path, which: str) -> None:
    from fpfa.web.server import WindowServer

    server = WindowServer(desk).start()
    try:
        subprocess.run([shutil.which("node"), str(TOOL), server.page_url(), str(out), which], check=True, timeout=240)
    finally:
        server.stop()
        desk.close()


def main(argv: list[str]) -> int:
    out = Path(argv[0]).resolve() if argv else REPO / "docs" / "screenshots"
    if shutil.which("node") is None:
        sys.stderr.write("The pictures need Node.js with Playwright.\n")
        return 2
    from fpfa.desk import Desk

    _fresh_data_dir("welcome")
    _shoot(Desk(), out, "welcome")

    _fresh_data_dir("job")
    from team_scenario import REQUEST_ONE, client_for, turn_one

    desk = Desk()
    with desk.lock:
        # The designer has the sample zone on the form and its tool plan run; then one plain request.
        desk.ask_claude.set(False)
        desk.start_sample_di()
        desk.pump()
        players = turn_one(desk.record, desk.project["id"])
        with patch("fpfa.desk.AnthropicMessages", client_for(players)):
            desk.send_chat(REQUEST_ONE)
            _settle(desk)
    _shoot(desk, out, "job")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
