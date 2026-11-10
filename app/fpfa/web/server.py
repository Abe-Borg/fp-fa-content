"""The window's local server: one Desk behind a small HTTP API, the page that drives it, and its event stream.

Standard library only (http.server). It binds 127.0.0.1 on a free port and
refuses every /api request without the launch token, a Host header that is
not this loopback address, or a cross-site Origin. Nothing here decides
anything about a job: every rule lives in fpfa.desk.

GET  /                  the page (app/frontend, built into fpfa/web/static)
GET  /api/state         Desk.snapshot(), the conversation included
GET  /api/events        server-sent events: "state" when the window's state changes,
                        "live" with the new words of a reply that is arriving, "live_end"
GET  /api/text/<name>   about, license, notices: the long texts of Settings
POST /api/<action>      one Desk action, a JSON body in, {"ok": true} out
"""

from __future__ import annotations

import hmac
import json
import mimetypes
import secrets
import threading
import time
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlsplit

from fpfa.about import about_text, license_text, notices_text
from fpfa.claude_client import safe_error
from fpfa.desk import Desk

STATIC = Path(__file__).resolve().parent / "static"
TOKEN_HEADER = "X-Cynosure-Token"
MAX_BODY = 1_000_000
# How often the pump runs the workers' callbacks and takes the streamed words, in seconds.
PUMP_SECONDS = 0.03
# The event stream sends at most this often, so a burst of words becomes one message.
FRAME_SECONDS = 0.03
KEEPALIVE_SECONDS = 15.0
NOT_BUILT = """<!doctype html><meta charset="utf-8"><title>+Cynosure</title>
<body style="font-family:system-ui;margin:3rem;max-width:40rem"><h1>+Cynosure</h1>
<p>The window's page has not been built. From the app folder:</p>
<pre>cd frontend
npm ci
npm run build</pre><p>Then start +Cynosure again.</p></body>"""

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")


def _text(value: Any, limit: int = 20000) -> str:
    return str(value if value is not None else "")[:limit]


def _flag(value: Any) -> bool:
    return value is True or value in (1, "1", "true", "on")


# Each action: the Desk method it calls, from the request body. The page sends nothing else.
ACTIONS: dict[str, Callable[[Desk, dict], Any]] = {
    "send": lambda d, b: d.send_chat(_text(b.get("text"), 200000)),
    "form": lambda d, b: d.patch_form(b.get("values") if isinstance(b.get("values"), dict) else {}),
    "open": lambda d, b: d.select_project(_text(b.get("id"), 200)),
    "new": lambda d, b: d.new_job(),
    "rename": lambda d, b: d.rename_job(_text(b.get("id"), 200) or None, _text(b.get("name"), 500)),
    "delete": lambda d, b: d.delete_job(_text(b.get("id"), 200) or None),
    "save": lambda d, b: d.save_current(),
    "mode": lambda d, b: d.set_mode(_text(b.get("slug"), 80)),
    "narrate": lambda d, b: d.set_narrate(_flag(b.get("on"))),
    "sample-di": lambda d, b: d.start_sample_di(),
    "sample-bess": lambda d, b: d.start_sample_bess(),
    "run": lambda d, b: d.start_zone_run(),
    "export-section": lambda d, b: d.export_docx(),
    "export-basis": lambda d, b: d.export_design_basis(),
    "check-record": lambda d, b: d.start_record_check(),
    "cancel": lambda d, b: d.cancel_running_jobs(),
    "usage": lambda d, b: d.show_usage(),
    "help": lambda d, b: d.show_help(),
    "segment-add": lambda d, b: d.add_segment(
        _text(b.get("role"), 40), _text(b.get("nps"), 40), _text(b.get("schedule"), 40), _text(b.get("length"), 40)
    ),
    "segment-remove": lambda d, b: d.remove_segment(int(b.get("index", -1))),
    "notice-dismiss": lambda d, b: d.dismiss_notice(int(b.get("id", 0))),
    "banner-dismiss": lambda d, b: d.dismiss_banner(),
    "scheme": lambda d, b: d.set_scheme(_text(b.get("id"), 40)),
    "motion": lambda d, b: d.set_reduce_motion(_flag(b.get("reduce"))),
    "key-save": lambda d, b: d.save_key(_text(b.get("key"), 1000)),
    "key-clear": lambda d, b: d.clear_key(),
    "key-check": lambda d, b: d.check_key(_text(b.get("key"), 1000)),
    "content-check": lambda d, b: d.check_content_updates(_text(b.get("feed"), 2000)),
    "content-root": lambda d, b: d.save_content_root(_text(b.get("folder"), 2000)),
}

TEXTS: dict[str, Callable[[], str]] = {
    "about": about_text,
    "license": license_text,
    "notices": notices_text,
}


def new_token() -> str:
    return secrets.token_urlsafe(24)


class WindowServer(ThreadingHTTPServer):
    """The HTTP server and the pump that runs the desk's queue."""

    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, desk: Desk, *, token: str | None = None, port: int = 0, static: Path = STATIC):
        self.desk = desk
        self.token = token or new_token()
        self.static = Path(static)
        self.stopping = threading.Event()
        super().__init__(("127.0.0.1", port), Handler)
        self.port = self.server_address[1]
        self._workers: list[threading.Thread] = []

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def page_url(self, *, theme: str = "") -> str:
        query = f"?token={self.token}"
        if theme:
            query += f"&theme={theme}"
        return self.base_url + "/" + query

    def start(self) -> "WindowServer":
        for target, name in ((self.serve_forever, "fpfa-server"), (self._pump, "fpfa-pump")):
            thread = threading.Thread(target=target, daemon=True, name=name)
            thread.start()
            self._workers.append(thread)
        return self

    def stop(self) -> None:
        self.stopping.set()
        with self.desk.changed:
            self.desk.changed.notify_all()
        try:
            self.shutdown()
        except Exception:
            pass
        self.server_close()

    def _pump(self) -> None:
        desk = self.desk
        while not self.stopping.is_set():
            try:
                desk.pump()
            except Exception:
                traceback.print_exc()
            self.stopping.wait(PUMP_SECONDS)

    def allowed_hosts(self) -> set[str]:
        return {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}


class Handler(BaseHTTPRequestHandler):
    server: WindowServer
    protocol_version = "HTTP/1.1"
    server_version = "Cynosure"
    sys_version = ""

    def log_message(self, format: str, *args) -> None:  # noqa: A002 — the base class's name
        return None

    # Guards -------------------------------------------------------------

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlsplit(self.path).query)

    def _host_ok(self) -> bool:
        return (self.headers.get("Host") or "") in self.server.allowed_hosts()

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin or origin == "null":
            return origin is None
        return origin in {f"http://{host}" for host in self.server.allowed_hosts()}

    def _token_ok(self) -> bool:
        given = self.headers.get(TOKEN_HEADER) or (self._query().get("token") or [""])[0]
        return bool(given) and hmac.compare_digest(given, self.server.token)

    # Replies -------------------------------------------------------------

    def _send(self, status: int, body: bytes, content_type: str, *, cache: str = "no-store") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: Any) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _refuse(self, status: int, message: str) -> None:
        self._json(status, {"ok": False, "error": message})

    # Routes --------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 — http.server's name
        path = urlsplit(self.path).path
        if not self._host_ok():
            self._refuse(HTTPStatus.MISDIRECTED_REQUEST, "This server answers only on its own loopback address.")
            return
        if not path.startswith("/api/"):
            self._static(path)
            return
        if not self._token_ok():
            self._refuse(HTTPStatus.FORBIDDEN, "Missing or wrong launch token.")
            return
        desk = self.server.desk
        if path == "/api/health":
            self._json(HTTPStatus.OK, {"ok": True})
        elif path == "/api/state":
            self._json(HTTPStatus.OK, desk.call(self._full_state))
        elif path == "/api/events":
            self._events()
        elif path.startswith("/api/text/"):
            name = path.rsplit("/", 1)[-1]
            maker = TEXTS.get(name)
            if maker is None:
                self._refuse(HTTPStatus.NOT_FOUND, "No such text.")
                return
            try:
                text = maker()
            except Exception as exc:
                text = "This text could not be read. " + safe_error(exc)
            self._json(HTTPStatus.OK, {"ok": True, "text": text})
        else:
            self._refuse(HTTPStatus.NOT_FOUND, "No such route.")

    do_HEAD = do_GET

    def do_POST(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if not self._host_ok() or not self._origin_ok():
            self._refuse(HTTPStatus.FORBIDDEN, "Cross-site requests are refused.")
            return
        if not self._token_ok():
            self._refuse(HTTPStatus.FORBIDDEN, "Missing or wrong launch token.")
            return
        name = path[len("/api/"):] if path.startswith("/api/") else ""
        action = ACTIONS.get(name)
        if action is None:
            self._refuse(HTTPStatus.NOT_FOUND, "No such action.")
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self._refuse(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body is too large.")
            return
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._refuse(HTTPStatus.BAD_REQUEST, "The request body is not JSON.")
            return
        if not isinstance(body, dict):
            self._refuse(HTTPStatus.BAD_REQUEST, "The request body must be a JSON object.")
            return
        desk = self.server.desk
        try:
            result = desk.call(action, desk, body)
        except (ValueError, TypeError) as exc:
            self._refuse(HTTPStatus.BAD_REQUEST, safe_error(exc))
            return
        except Exception as exc:
            traceback.print_exc()
            self._refuse(HTTPStatus.INTERNAL_SERVER_ERROR, safe_error(exc))
            return
        reply = {"ok": True, "revision": desk.revision}
        if isinstance(result, (bool, str)):
            reply["result"] = result
        self._json(HTTPStatus.OK, reply)

    # The page --------------------------------------------------------------

    def _static(self, path: str) -> None:
        root = self.server.static
        if path in ("", "/"):
            path = "/index.html"
        target = (root / path.lstrip("/")).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            self._refuse(HTTPStatus.NOT_FOUND, "No such file.")
            return
        if not target.is_file():
            if path == "/index.html":
                self._send(HTTPStatus.OK, NOT_BUILT.encode("utf-8"), "text/html; charset=utf-8")
                return
            self._refuse(HTTPStatus.NOT_FOUND, "No such file.")
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in ("application/json",):
            content_type += "; charset=utf-8"
        # Built assets carry a content hash in their names, so they never change under one name.
        cache = "public, max-age=31536000, immutable" if path.startswith("/assets/") else "no-store"
        self._send(HTTPStatus.OK, target.read_bytes(), content_type, cache=cache)

    # State and the event stream -----------------------------------------------

    def _full_state(self) -> dict:
        desk = self.server.desk
        state = desk.snapshot(thread=True)
        state["lives"] = desk.live_items()
        return state

    def _write_event(self, kind: str, payload: Any) -> None:
        data = json.dumps(payload, ensure_ascii=False)
        self.wfile.write(f"event: {kind}\ndata: {data}\n\n".encode("utf-8"))

    def _events(self) -> None:
        server = self.server
        desk = server.desk
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.close_connection = True
        sent_revision = -1
        sent_thread = -1
        sent_live_rev = -1
        sent_project: str | None = None
        sent_lives: dict[str, tuple[int, int]] = {}
        try:
            while not server.stopping.is_set():
                with desk.changed:
                    desk.changed.wait_for(
                        lambda: server.stopping.is_set()
                        or desk.revision != sent_revision
                        or desk.live_rev != sent_live_rev,
                        timeout=KEEPALIVE_SECONDS,
                    )
                if server.stopping.is_set():
                    break
                with desk.lock:
                    state = None
                    if desk.revision != sent_revision:
                        include_thread = desk.thread_rev != sent_thread or (desk.project or {}).get("id") != sent_project
                        state = desk.snapshot(thread=include_thread)
                    live_rev = desk.live_rev
                    lives = desk.live_items()
                    project_id = (desk.project or {}).get("id")
                if state is None and live_rev == sent_live_rev:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    continue
                if state is not None:
                    self._write_event("state", state)
                    sent_revision = state["revision"]
                    if "turns" in state["thread"]:
                        sent_thread = state["thread"]["rev"]
                        sent_project = project_id
                sent_live_rev = live_rev
                live_ids = set()
                for item in lives:
                    job_id = item["job_id"]
                    live_ids.add(job_id)
                    gen, length = sent_lives.get(job_id, (-1, 0))
                    text = item["text"]
                    if gen != item["gen"] or len(text) < length:
                        start = 0
                    else:
                        start = length
                    if start == len(text) and gen == item["gen"]:
                        continue
                    self._write_event("live", {
                        "job_id": job_id, "project_id": project_id, "gen": item["gen"],
                        "start": start, "text": text[start:],
                    })
                    sent_lives[job_id] = (item["gen"], len(text))
                for job_id in [key for key in sent_lives if key not in live_ids]:
                    self._write_event("live_end", {"job_id": job_id})
                    del sent_lives[job_id]
                self.wfile.flush()
                time.sleep(FRAME_SECONDS)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            return
