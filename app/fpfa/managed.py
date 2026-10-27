"""Claude Managed Agents escape hatch for one heavy job.

Ordinary chat, Sample DI, Sample BESS, and a zone tool plan do not call this
module. A heavy job is the only caller. It opens one cloud session (an
Anthropic-hosted container), waits for that session to finish, and returns
the reply text. The caller posts that text into the desktop thread that
started the job. This module does not open a second conversation.

The model id stays claude-opus-5-5. Requests do not send temperature, top_p,
top_k, tool_choice, or a thinking field. The role and the mode stay in the
content pack; the caller passes the system text it loaded.
"""

from __future__ import annotations

import json
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

# File tools inside the container. Web search and web fetch stay off, and the
# sandbox network allows no hosts, so this job cannot pull a page.
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


def scrub_text(text: str) -> str:
    return _KEY_RE.sub("[key]", text or "")[:800]


def session_system(pack_system: str) -> str:
    """Pack text the caller loaded, plus the hatch note. No role is stored here."""
    pack = (pack_system or "").strip()
    if not pack:
        return HEAVY_NOTE
    return pack + "\n\n" + HEAVY_NOTE


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
            "system": HEAVY_NOTE,
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


def _delete_session(request: Request, session_id: str) -> None:
    try:
        request("DELETE", f"/v1/sessions/{session_id}", None)
    except Exception:
        return


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
    system: str,
    user_text: str,
    resources: dict | None = None,
    sleep: Callable[[float], None] | None = None,
    max_polls: int = 150,
    poll_seconds: float = 2.0,
) -> dict:
    """Run one heavy job and return its reply text.

    resources caches the agent and the cloud environment for later heavy jobs
    in this process. The session is deleted before this function returns, so
    the hosted run is not left as a second conversation.
    """
    task = (user_text or "").strip()
    if not task:
        raise ValueError("A heavy job needs a task.")
    if resources is None:
        resources = {}
    pause = sleep or time.sleep
    session_id = ""
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
                    "system": session_system(system),
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
        text, stop = _wait_for_reply(
            request,
            session_id,
            sleep=pause,
            max_polls=max_polls,
            poll_seconds=poll_seconds,
        )
        return {
            "text": text,
            "model": MODEL_ID,
            "runtime": RUNTIME,
            "stop_reason": stop,
        }
    except Exception as exc:
        message = scrub_text(str(exc) or type(exc).__name__)
        raise RuntimeError(message or "The hosted run failed.") from None
    finally:
        if session_id:
            _delete_session(request, session_id)
