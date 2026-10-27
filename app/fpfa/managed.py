"""Claude Managed Agents escape hatch for one heavy job.

Ordinary chat, Sample DI, Sample BESS, and a zone tool plan do not call this
module. A heavy job is the only caller. It opens one cloud session (an
Anthropic-hosted container), waits for that session to finish, and returns
the reply text. The caller posts that text into the desktop thread that
started the job. This module does not open a second conversation.

The hosted turn is text-only reasoning on the zone packet already in the
user message. The container is not given skills/, roles/, modes/, or calcs/,
and it has no network to fetch them. This module does not tell the model to
call read_role, read_skill, read_mode, or a calc tool. Those tools exist
only on the desktop Messages path.

The model id stays claude-opus-5-5. Requests do not send temperature, top_p,
top_k, tool_choice, or a thinking field. The cached agent id and cloud
environment id are reused for later heavy jobs in this process. They are
not sessions, and session cleanup does not delete them.

A session id is registered while the poll runs. The job deletes it before
returning. A delete that is still on the network stays tracked until that
attempt finishes; an empty registry is not treated as a successful delete.
A failed delete is logged and returned on the result, and the id stays
registered. Inbox close and process exit delete whatever is still registered
or still in flight. Those shutdown sweeps wait a short time so a slow
network does not hold the window open.
"""

from __future__ import annotations

import atexit
import contextvars
import json
import logging
import re
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Callable

from fpfa.claude_client import MODEL_ID

MANAGED_BETA = "managed-agents-2026-04-01"
ANTHROPIC_VERSION = "2023-06-01"
API_ROOT = "https://api.anthropic.com"
RUNTIME = "managed-agents"

# Same fields the Messages client refuses. A heavy job does not send them either.
_FORBIDDEN = {"temperature", "top_p", "top_k", "tool_choice", "thinking"}
_KEY_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")
_GUARD = threading.Lock()

# Operational note for the hatch. It is not a role, a mode, or a method.
HEAVY_NOTE = (
    "This turn is a heavy job on the hosted runtime. "
    "Write one reply. The desktop posts that reply into the same project thread. "
    "Do not start another conversation. "
    "Do not recompute zone gallons or seconds. "
    "When the message quotes a tool plan, those figures govern. "
    "A delivery time from the screen is an optimistic screen. "
    "Designer judgment the tools did not return is use best judgment. "
    "Do not quote raw standard text."
)

# The container cannot see the content pack. Say so, and do not send the
# everyday system text, which tells the model to call desktop tools.
HEAVY_TEXT_ONLY = (
    "This hosted path is text-only reasoning on the already-computed zone packet "
    "in the user message. "
    "skills/, roles/, modes/, and calcs/ are not mounted here, and this container "
    "has no network to fetch them. "
    "Do not call read_role, read_skill, read_mode, list_roles, list_skills, list_modes, "
    "or a calc tool. Those tools exist only on the desktop Messages path. "
    "The container file tools cannot see the content pack. "
    "Do not use them to recompute a zone. "
    "Figures already in the user message govern. "
    "Scope stays wet pipe, dry pipe, and double-interlock preaction. "
    "Do not design foam, clean agent, water mist, deluge, single-interlock, or a Canadian path."
)

DELETE_FAILURE_NOTE = (
    "The hosted session was not deleted. "
    "The failure is in the fpfa.managed log. "
    "Closing the app retries the delete."
)

# Sandbox file tools only. Web search and web fetch stay off, and the sandbox
# network allows no hosts. Nothing here mounts the content pack or adds a
# custom tool for read_role, read_skill, read_mode, or calcs.
HEAVY_TOOLS = [
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},
        "configs": [
            {"name": "bash", "enabled": True, "permission_policy": "always_allow"},
            {"name": "read", "enabled": True, "permission_policy": "always_allow"},
            {"name": "write", "enabled": True, "permission_policy": "always_allow"},
            {"name": "edit", "enabled": True, "permission_policy": "always_allow"},
            {"name": "glob", "enabled": True, "permission_policy": "always_allow"},
            {"name": "grep", "enabled": True, "permission_policy": "always_allow"},
        ],
    }
]

Request = Callable[[str, str, dict | None], Any]

_log = logging.getLogger("fpfa.managed")
_active_lock = threading.Lock()
_active_sessions: dict[str, Request] = {}
# DELETE has been sent and has not finished. Distinct from _active_sessions so
# a pop at the start of DELETE is not mistaken for "already deleted".
_inflight_deletes: dict[str, "_DeleteAttempt"] = {}
# Normal heavy-job HTTP budget. Shutdown sets a much shorter value.
_HTTP_TIMEOUT: contextvars.ContextVar[float] = contextvars.ContextVar(
    "fpfa_http_timeout",
    default=120.0,
)
# Total time a close or process-exit sweep will wait for session deletes.
SHUTDOWN_DELETE_DEADLINE = 1.0


def scrub_text(text: str) -> str:
    return _KEY_RE.sub("[key]", text or "")[:800]


def session_system() -> str:
    """Text-only hatch prompt plus HEAVY_NOTE.

    The everyday role, the mode file, and the skill list are not included.
    They tell the model to call tools this container does not have.
    """
    return HEAVY_TEXT_ONLY + "\n\n" + HEAVY_NOTE


def delete_failure_note(status: dict | None) -> str:
    """Designer-facing line when a hosted session is still up. Empty when the delete worked."""
    if not isinstance(status, dict) or status.get("ok", True):
        return ""
    return DELETE_FAILURE_NOTE


def reply_with_delete_status(result: dict) -> str:
    """Reply text, plus a line when the session delete failed."""
    reply = (result.get("text") or "").strip() or "(The hosted run returned no text.)"
    note = delete_failure_note(result.get("session_delete"))
    if not note:
        return reply
    return reply + "\n\n" + note


class _DeleteAttempt:
    """One DELETE that has started and has not yet been confirmed."""

    def __init__(self, request: Request):
        self.request = request
        self.done = threading.Event()
        self.ok = False
        self.error = ""
        self.finished = False

    def status(self, session_id: str) -> dict:
        if not self.finished:
            return _pending_delete_status(session_id)
        return {"ok": self.ok, "session_id": session_id, "error": self.error}


def _pending_delete_status(session_id: str) -> dict:
    return {
        "ok": False,
        "session_id": session_id,
        "error": "shutdown deadline",
        "pending": True,
    }


def _log_unconfirmed_delete(session_id: str) -> None:
    _log.error(
        "hosted session delete still in progress at shutdown session_id=%s",
        session_id,
    )


def active_session_ids() -> list[str]:
    """Sessions not confirmed deleted, including a DELETE still on the network."""
    with _active_lock:
        ids = list(_active_sessions)
        for session_id in _inflight_deletes:
            if session_id not in ids:
                ids.append(session_id)
        return ids


def register_active_session(session_id: str, request: Request) -> None:
    if not session_id:
        return
    with _active_lock:
        _active_sessions[session_id] = request


def release_active_sessions() -> None:
    """Drop registered session ids without DELETE.

    Tests call this so a fake request is not invoked again at process exit.
    Closing the app and process exit call delete_active_sessions instead.
    """
    with _active_lock:
        attempts = list(_inflight_deletes.values())
        _inflight_deletes.clear()
        _active_sessions.clear()
    for attempt in attempts:
        attempt.ok = False
        attempt.error = "released"
        attempt.finished = True
        attempt.done.set()


def _reject_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _FORBIDDEN:
                raise ValueError(f"claude-opus-5-5 heavy job does not send {key}")
            _reject_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden(item)


def _model_id(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("id") or "")
    return ""


def anthropic_request(api_key: str, *, opener=None) -> Request:
    """POST/GET/DELETE against the Managed Agents beta. The key stays on this call."""
    open_url = opener or urllib.request.urlopen

    def request(method: str, path: str, body: dict | None = None) -> dict:
        _reject_forbidden(body)
        if "/v1/messages" in path:
            raise RuntimeError("A heavy job does not use the Messages API.")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "anthropic-beta": MANAGED_BETA,
        }
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["content-type"] = "application/json"
        req = urllib.request.Request(API_ROOT + path, data=data, headers=headers, method=method)
        try:
            with open_url(req, timeout=_HTTP_TIMEOUT.get()) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(scrub_text(f"HTTP {exc.code}: {detail}")) from None
        except Exception as exc:
            raise RuntimeError(scrub_text(f"{type(exc).__name__}: {exc}")) from None
        if not raw or not raw.strip():
            return {}
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"data": parsed}
        return {}

    return request


def _resource_lock(resources: dict) -> threading.Lock:
    with _GUARD:
        lock = resources.get("_lock")
        if lock is None or not hasattr(lock, "acquire"):
            lock = threading.Lock()
            resources["_lock"] = lock
        return lock


def _send(request: Request, method: str, path: str, body: dict | None) -> dict:
    _reject_forbidden(body)
    if "/v1/messages" in path:
        raise RuntimeError("A heavy job does not use the Messages API.")
    if isinstance(body, dict):
        if "model" in body and _model_id(body.get("model")) not in ("", MODEL_ID):
            raise ValueError(f"Heavy job model must stay {MODEL_ID}")
        agent = body.get("agent")
        if isinstance(agent, dict) and _model_id(agent.get("model")) not in ("", MODEL_ID):
            raise ValueError(f"Heavy job model must stay {MODEL_ID}")
    payload = request(method, path, body)
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        return {"data": payload}
    return {}


def _ensure_environment(request: Request, resources: dict) -> str:
    """Return the cached cloud environment id.

    Later heavy jobs in this process reuse it on purpose. It is not a
    session, and session cleanup does not delete it.
    """
    existing = resources.get("environment_id")
    if existing:
        return str(existing)
    created = _send(
        request,
        "POST",
        "/v1/environments",
        {
            "name": "fpfa-heavy",
            "config": {
                "type": "cloud",
                "networking": {"type": "limited"},
            },
        },
    )
    environment_id = str(created.get("id") or "")
    if not environment_id:
        raise RuntimeError("The hosted environment did not start.")
    resources["environment_id"] = environment_id
    return environment_id


def _ensure_agent(request: Request, resources: dict) -> str:
    """Return the cached agent id.

    Later heavy jobs in this process reuse it on purpose. It is not a
    session, and session cleanup does not delete it. The stored system
    text is the text-only hatch prompt. Each session sends that same prompt.
    """
    existing = resources.get("agent_id")
    if existing:
        return str(existing)
    created = _send(
        request,
        "POST",
        "/v1/agents",
        {
            "name": "FPFA heavy job",
            "model": MODEL_ID,
            "system": session_system(),
            "tools": HEAVY_TOOLS,
        },
    )
    agent_id = str(created.get("id") or "")
    if not agent_id:
        raise RuntimeError("The hosted agent did not start.")
    resources["agent_id"] = agent_id
    return agent_id


def _list_events(request: Request, session_id: str) -> list[dict]:
    events: list[dict] = []
    page = ""
    for _ in range(20):
        path = f"/v1/sessions/{session_id}/events?limit=100&order=asc"
        if page:
            path += "&page=" + page
        payload = _send(request, "GET", path, None)
        batch = payload.get("data") or payload.get("events") or []
        if not isinstance(batch, list):
            break
        events.extend(item for item in batch if isinstance(item, dict))
        page = str(payload.get("next_page") or "")
        if not page:
            break
    return _ordered(events)


def _ordered(events: list[dict]) -> list[dict]:
    decorated = []
    for index, event in enumerate(events):
        stamp = str(event.get("processed_at") or "")
        decorated.append((stamp, index, event))
    decorated.sort()
    return [event for _, _, event in decorated]


def _assistant_text(events: list[dict]) -> str:
    parts: list[str] = []
    for event in events:
        if event.get("type") != "agent.message":
            continue
        content = event.get("content") or []
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                parts.append(str(block["text"]))
    return "\n".join(parts).strip()


def _idle_event(events: list[dict]) -> dict | None:
    for event in reversed(events):
        if event.get("type") == "session.status_idle":
            return event
    return None


def _stop_type(idle: dict | None) -> str:
    if not isinstance(idle, dict):
        return ""
    reason = idle.get("stop_reason")
    if isinstance(reason, dict):
        return str(reason.get("type") or "")
    if isinstance(reason, str):
        return reason
    return ""


def _terminated(events: list[dict]) -> bool:
    return any(event.get("type") == "session.status_terminated" for event in events)


def _error_message(events: list[dict]) -> str:
    for event in reversed(events):
        if event.get("type") != "session.error":
            continue
        err = event.get("error")
        if isinstance(err, dict) and err.get("message"):
            return str(err["message"])
        if isinstance(err, str) and err:
            return err
    return "The hosted run ended before a reply."


def _finish_attempt(
    session_id: str,
    attempt: _DeleteAttempt,
    *,
    ok: bool,
    error: str,
) -> None:
    """Record the outcome. A failure puts the id back for a later sweep."""
    with _active_lock:
        current = _inflight_deletes.get(session_id)
        if current is attempt:
            _inflight_deletes.pop(session_id, None)
            if not ok:
                _active_sessions.setdefault(session_id, attempt.request)
        attempt.ok = ok
        attempt.error = error
        attempt.finished = True
        attempt.done.set()


def delete_session(request: Request, session_id: str) -> dict:
    """DELETE one hosted session and record the outcome.

    The id stays in the in-flight map until this attempt finishes. Callers
    that look during the network call still see it. A failure is logged and
    the id is put back so a later close or process exit can retry. An id that
    is not registered and not in flight was already confirmed gone.

    A second caller for the same id waits for the attempt already running
    instead of treating the missing active entry as a successful delete.
    """
    if request is None:
        raise ValueError("A session delete needs the request that opened it.")
    with _active_lock:
        attempt = _inflight_deletes.get(session_id)
        owner = attempt is None
        if owner:
            stored = _active_sessions.pop(session_id, None)
            if stored is None:
                return {"ok": True, "session_id": session_id, "error": "", "skipped": True}
            attempt = _DeleteAttempt(stored)
            _inflight_deletes[session_id] = attempt
    if not owner:
        assert attempt is not None
        attempt.done.wait()
        return attempt.status(session_id)
    assert attempt is not None
    failed: BaseException | None = None
    try:
        attempt.request("DELETE", f"/v1/sessions/{session_id}", None)
    except Exception as exc:
        failed = exc
    except BaseException:
        _finish_attempt(session_id, attempt, ok=False, error="interrupted")
        raise
    if failed is not None:
        error = scrub_text(str(failed) or type(failed).__name__) or "delete failed"
        _log.error(
            "hosted session delete failed session_id=%s error=%s",
            session_id,
            error,
        )
        _finish_attempt(session_id, attempt, ok=False, error=error)
        return attempt.status(session_id)
    _finish_attempt(session_id, attempt, ok=True, error="")
    return attempt.status(session_id)


def _delete_within(request: Request, session_id: str, timeout: float) -> dict:
    """Run delete_session on a daemon thread and wait at most timeout seconds."""
    box: dict[str, dict] = {}

    def target() -> None:
        token = _HTTP_TIMEOUT.set(max(0.05, timeout))
        try:
            box["status"] = delete_session(request, session_id)
        finally:
            _HTTP_TIMEOUT.reset(token)

    thread = threading.Thread(target=target, name="fpfa-session-delete", daemon=True)
    thread.start()
    thread.join(timeout)
    status = box.get("status")
    if status is None:
        _log_unconfirmed_delete(session_id)
        return _pending_delete_status(session_id)
    return status


def delete_active_sessions(deadline: float | None = None) -> list[dict]:
    """DELETE every hosted session that is not confirmed gone.

    deadline is the total seconds to wait. None waits until each attempt
    this call starts has finished. Shutdown passes SHUTDOWN_DELETE_DEADLINE.

    An attempt already on the network is waited on, not treated as deleted.
    If it is still running when the deadline hits, the id stays tracked and
    the status is not ok. A confirmed success is not deleted again.
    """
    started = time.monotonic()

    def remaining() -> float | None:
        if deadline is None:
            return None
        return max(0.0, deadline - (time.monotonic() - started))

    with _active_lock:
        active = [
            (session_id, request)
            for session_id, request in _active_sessions.items()
            if session_id not in _inflight_deletes
        ]
        inflight = list(_inflight_deletes.items())

    results: list[dict] = []
    for session_id, attempt in inflight:
        left = remaining()
        if left is None:
            attempt.done.wait()
        elif left <= 0 or not attempt.done.wait(left):
            _log_unconfirmed_delete(session_id)
            results.append(_pending_delete_status(session_id))
            continue
        results.append(attempt.status(session_id))

    for session_id, request in active:
        left = remaining()
        if deadline is not None and (left is None or left <= 0):
            _log_unconfirmed_delete(session_id)
            results.append(_pending_delete_status(session_id))
            continue
        if deadline is None:
            results.append(delete_session(request, session_id))
            continue
        results.append(_delete_within(request, session_id, left))
    return results


def shutdown_delete_sessions() -> None:
    """Bounded sweep used by inbox close and process exit."""
    token = _HTTP_TIMEOUT.set(SHUTDOWN_DELETE_DEADLINE)
    try:
        delete_active_sessions(deadline=SHUTDOWN_DELETE_DEADLINE)
    finally:
        _HTTP_TIMEOUT.reset(token)


def _wait_for_reply(
    request: Request,
    session_id: str,
    *,
    sleep: Callable[[float], None],
    max_polls: int,
    poll_seconds: float,
) -> tuple[str, str]:
    """Poll one session until it is idle. Do not send a follow-up turn."""
    last_events: list[dict] = []
    for attempt in range(max_polls):
        last_events = _list_events(request, session_id)
        if _terminated(last_events):
            raise RuntimeError(_error_message(last_events))
        idle = _idle_event(last_events)
        status = ""
        if idle is None:
            info = _send(request, "GET", f"/v1/sessions/{session_id}", None)
            status = str(info.get("status") or "")
            if status in ("idle", "terminated"):
                last_events = _list_events(request, session_id)
                idle = _idle_event(last_events)
                if status == "terminated" or _terminated(last_events):
                    raise RuntimeError(_error_message(last_events))
        if idle is not None or status == "idle":
            stop = _stop_type(idle)
            text = _assistant_text(last_events)
            if stop == "requires_action":
                raise RuntimeError(
                    "The hosted run paused for a confirmation. "
                    "It was not continued, and no second conversation was opened."
                )
            if stop == "budget_reached":
                raise RuntimeError("The hosted run stopped because it reached its budget.")
            if stop == "end_turn" and text:
                return text, stop
            # An idle mark can land before the reply text is listed. Look again.
            if attempt == max_polls - 1 and (stop == "end_turn" or (status == "idle" and text)):
                return text, stop or "end_turn"
            if stop and stop != "end_turn":
                raise RuntimeError("The hosted run stopped before a reply.")
        if attempt < max_polls - 1:
            sleep(poll_seconds)
    raise RuntimeError("The hosted run did not finish.")


def run_heavy_job(
    request: Request,
    *,
    user_text: str,
    system: str | None = None,
    resources: dict | None = None,
    sleep: Callable[[float], None] | None = None,
    max_polls: int = 150,
    poll_seconds: float = 2.0,
) -> dict:
    """Run one heavy job and return its reply text.

    resources caches the agent id and the cloud environment id for later
    heavy jobs in this process. Those ids are reused on purpose. This
    function does not delete them.

    system, when passed, must be session_system(). Everyday role, mode, and
    skill text is refused so it cannot land on the wire. The session prompt
    is always the text-only hatch prompt.

    The session is registered for the poll and deleted before this function
    returns. A failed delete stays on session_delete and in the log, and the
    id stays registered for inbox close and process exit.
    """
    task = (user_text or "").strip()
    if not task:
        raise ValueError("A heavy job needs a task.")
    prompt = session_system()
    if system is not None and system != prompt:
        raise ValueError(
            "A heavy job sends the text-only hatch prompt. "
            "It does not send everyday role, mode, or skill instructions."
        )
    if resources is None:
        resources = {}
    pause = sleep or time.sleep
    session_id = ""
    result: dict | None = None
    failure: RuntimeError | None = None
    try:
        with _resource_lock(resources):
            environment_id = _ensure_environment(request, resources)
            agent_id = _ensure_agent(request, resources)
        created = _send(
            request,
            "POST",
            "/v1/sessions",
            {
                "agent": {
                    "type": "agent_with_overrides",
                    "id": agent_id,
                    "model": {"id": MODEL_ID},
                    "system": prompt,
                },
                "environment_id": environment_id,
                "initial_events": [
                    {
                        "type": "user.message",
                        "content": [{"type": "text", "text": task}],
                    }
                ],
            },
        )
        session_id = str(created.get("id") or "")
        if not session_id:
            raise RuntimeError("The hosted run did not start.")
        register_active_session(session_id, request)
        text, stop = _wait_for_reply(
            request,
            session_id,
            sleep=pause,
            max_polls=max_polls,
            poll_seconds=poll_seconds,
        )
        result = {
            "text": text,
            "model": MODEL_ID,
            "runtime": RUNTIME,
            "stop_reason": stop,
        }
    except Exception as exc:
        message = scrub_text(str(exc) or type(exc).__name__)
        failure = RuntimeError(message or "The hosted run failed.")
    delete_status = None
    if session_id:
        delete_status = delete_session(request, session_id)
    if failure is not None:
        if delete_status and not delete_status.get("ok", True):
            extra = delete_status.get("error") or "delete failed"
            raise RuntimeError(
                f"{failure} The hosted session was not deleted: {extra}"
            ) from None
        raise failure from None
    if result is None:
        raise RuntimeError("The hosted run failed.")
    if delete_status is not None:
        result["session_delete"] = {
            "ok": bool(delete_status.get("ok")),
            "session_id": str(delete_status.get("session_id") or ""),
            "error": str(delete_status.get("error") or ""),
        }
    return result


def _install_session_cleanup() -> None:
    atexit.register(shutdown_delete_sessions)
    from fpfa.jobs import register_inbox_close_hook

    register_inbox_close_hook(shutdown_delete_sessions)


_install_session_cleanup()
