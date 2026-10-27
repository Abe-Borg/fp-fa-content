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
returning. A failed delete is logged and returned on the result, and the id
stays registered. Inbox close and process exit delete whatever is still
registered, including a poll that the worker has not finished.
"""

from __future__ import annotations

import atexit
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


def active_session_ids() -> list[str]:
    with _active_lock:
        return list(_active_sessions)


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
        _active_sessions.clear()


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
            with open_url(req, timeout=120) as resp:
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


def delete_session(request: Request, session_id: str) -> dict:
    """DELETE one hosted session and record the outcome.

    A failure is logged and the id is put back so a later close or process
    exit can retry. A session another caller already removed is skipped.
    The error text is scrubbed before it is logged or returned.

    request is the caller's handle. After the id is taken off the registry,
    the stored callable performs the DELETE so a second caller does not
    send another one. request is kept so a caller can show which handle it
    intended, and so the two stay the same object for a registered session.
    """
    if request is None:
        raise ValueError("A session delete needs the request that opened it.")
    with _active_lock:
        stored = _active_sessions.pop(session_id, None)
    if stored is None:
        return {"ok": True, "session_id": session_id, "error": "", "skipped": True}
    failed: BaseException | None = None
    try:
        stored("DELETE", f"/v1/sessions/{session_id}", None)
    except Exception as exc:
        failed = exc
    except BaseException:
        with _active_lock:
            _active_sessions.setdefault(session_id, stored)
        raise
    if failed is not None:
        error = scrub_text(str(failed) or type(failed).__name__)
        with _active_lock:
            _active_sessions.setdefault(session_id, stored)
        _log.error(
            "hosted session delete failed session_id=%s error=%s",
            session_id,
            error or "delete failed",
        )
        return {"ok": False, "session_id": session_id, "error": error or "delete failed"}
    return {"ok": True, "session_id": session_id, "error": ""}


def delete_active_sessions() -> list[dict]:
    """DELETE every hosted session still registered.

    Inbox close and process exit call this. The job's own delete removes
    the id first, so a finished job is not deleted twice.
    """
    with _active_lock:
        pending = list(_active_sessions.items())
    return [delete_session(request, session_id) for session_id, request in pending]


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
    atexit.register(delete_active_sessions)
    from fpfa.jobs import register_inbox_close_hook

    register_inbox_close_hook(delete_active_sessions)


_install_session_cleanup()
