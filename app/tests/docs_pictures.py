"""The README's pictures, taken again:  python tests/docs_pictures.py [folder] [welcome] [job] [fill]

SIMULATED. No model is called. The job in the pictures is the first turn of
tests/team_scenario.py: every agent's moves are a script written in advance,
played through the real application, which builds the messages, runs the
calc kernels, writes the record, and draws the window. A second, empty data
directory gives the opening screen and Settings. The pictures show what the
window does with such a job. They do not show what a live model writes.

The fill picture is a third window: a scripted lead records the AHJ, the
insurer, and the zone name a designer states in a message, and the card
under its reply and the marked fields on the Inputs tab are drawn.

Needs Node.js with Playwright (frontend/tools/shoot_docs.mjs). The default
folder is docs/screenshots, and with no names every picture is taken.
Nothing here touches the owner's jobs: each window runs in a data directory
of its own that is made for it.
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


FILL_REQUEST = (
    "New job. The AHJ is the City of Irvine, and the insurer is FM Global. "
    "First zone is DH-1. What do you still need from me before you can run the water delivery screen?"
)
FILL_REPLY = (
    "I put what you gave me on the Inputs tab: the AHJ, the insurer, and the zone name.\n\n"
    "I did not touch the NFPA 13 and NFPA 72 editions. Which edition the City of Irvine enforces is an adoption "
    "question, and I won't answer it from the city's name. Tell me the edition on the permit set and I'll record it.\n\n"
    "Before I can run the water delivery screen on DH-1 I still need:\n\n"
    "1. The pipe takeoff: sizes, schedules, and lengths by role.\n"
    "2. The fill flow at the riser, from the flow test or the hydraulic calc.\n"
    "3. The trim volume from the elected valve's data sheet. Without it the trim is carried as ASSUMED.\n"
    "4. The detection and releasing times from the releasing design."
)


def _fill_desk():
    """A new chat in which the lead fills in three fields the designer stated. The lead is a script."""
    from fpfa.desk import Desk
    from team_scenario import Players, call, client_for, say, use

    class Lead(Players):
        def kind(self, kwargs):
            return "lead"

    players = Lead({"lead": [
        call(
            use("set_input", name="ahj", value="City of Irvine", why="“The AHJ is the City of Irvine.”"),
            use("set_input", name="insurer", value="FM Global", why="“the insurer is FM Global”"),
            use("set_input", name="zone_id", value="DH-1", why="“First zone is DH-1.”"),
        ),
        say(FILL_REPLY),
    ]})
    desk = Desk()
    with desk.lock:
        desk.ask_claude.set(False)
        with patch("fpfa.desk.AnthropicMessages", client_for(players)):
            desk.send_chat(FILL_REQUEST)
            _settle(desk)
    return desk


def main(argv: list[str]) -> int:
    out = Path(argv[0]).resolve() if argv else REPO / "docs" / "screenshots"
    wanted = set(argv[1:]) or {"welcome", "job", "fill"}
    if shutil.which("node") is None:
        sys.stderr.write("The pictures need Node.js with Playwright.\n")
        return 2
    from fpfa.desk import Desk

    if "welcome" in wanted:
        _fresh_data_dir("welcome")
        _shoot(Desk(), out, "welcome")

    if "job" in wanted:
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

    if "fill" in wanted:
        _fresh_data_dir("fill")
        _shoot(_fill_desk(), out, "fill")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
