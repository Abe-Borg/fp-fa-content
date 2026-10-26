"""Messages API tool loop for Claude Opus 5.5.

Verified against platform.claude.com on 2026-10-23:
- model id is claude-opus-5-5
- tools use name, description, and input_schema
- Opus 5.5 rejects forced tool_choice (type "any" or type "tool"), so this
  loop leaves tool choice on the default (auto) and asks again in a user
  message when a required tool was skipped
- adaptive thinking stays on; this client does not send thinking disabled,
  temperature, top_p, or top_k
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Callable

MODEL_ID = "claude-opus-5-5"
_TRANSIENT_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}
_TRANSIENT_TYPES = {"APIConnectionError", "APITimeoutError", "RateLimitError", "InternalServerError"}


def safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(r"sk-ant-[A-Za-z0-9_\-]+", "[key]", text)
    return text[:800]


def _transient_api_error(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    if status in _TRANSIENT_STATUS:
        return True
    return type(exc).__name__ in _TRANSIENT_TYPES


def _wire_block(block: Any) -> dict:
    """Keep thinking and redacted-thinking blocks intact for the next request."""
    if isinstance(block, dict):
        return dict(block)
    if hasattr(block, "model_dump"):
        return block.model_dump(exclude_none=True)
    data = {"type": getattr(block, "type", None)}
    for key in ("text", "id", "name", "input", "thinking", "signature", "data"):
        if not hasattr(block, key):
            continue
        value = getattr(block, key)
        if value is not None:
            data[key] = value
    return data


def run_tool_loop(
    create: Callable[..., Any],
    *,
    system: str,
    user_text: str,
    tools: list[dict],
    execute: Callable[[str, dict], Any],
    required: list[str] | None = None,
    max_rounds: int = 8,
    max_nudges: int = 3,
    max_tokens: int = 8192,
) -> dict:
    """Call create() the way Messages.create is called. execute() runs a client tool."""
    required = list(required or [])
    messages: list[dict] = [{"role": "user", "content": user_text}]
    called: list[dict] = []
    nudges = 0
    final_text = ""
    stop_reason = ""
    for _ in range(max_rounds):
        response = create(
            model=MODEL_ID,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        stop_reason = getattr(response, "stop_reason", None) or ""
        wire = [_wire_block(block) for block in response.content]
        uses = [block for block in wire if block.get("type") == "tool_use"]
        texts = [block.get("text", "") for block in wire if block.get("type") == "text" and block.get("text")]
        if texts:
            final_text = "\n".join(texts).strip()
        # A max_tokens cut can leave a tool_use the API will reject on the next turn.
        if stop_reason == "max_tokens" and uses:
            break
        messages.append({"role": "assistant", "content": wire})
        if uses:
            results = []
            for use in uses:
                name = use.get("name") or ""
                tool_input = use.get("input") or {}
                if not isinstance(tool_input, dict):
                    tool_input = {}
                try:
                    output = execute(name, tool_input)
                    is_error = False
                    payload = json.dumps(output, default=str)
                except Exception as exc:
                    is_error = True
                    output = {"error": safe_error(exc)}
                    payload = output["error"]
                called.append({
                    "name": name,
                    "input": tool_input,
                    "output": output,
                    "is_error": is_error,
                })
                results.append({
                    "type": "tool_result",
                    "tool_use_id": use.get("id"),
                    "content": payload,
                    "is_error": is_error,
                })
            messages.append({"role": "user", "content": results})
            continue
        have = {item["name"] for item in called if not item["is_error"]}
        missing = [name for name in required if name not in have]
        if missing and nudges < max_nudges:
            nudges += 1
            messages.append({
                "role": "user",
                "content": (
                    "You still need to call these tools before writing numbers: "
                    + ", ".join(missing)
                    + ". Do not calculate gallons, seconds, gpm, scfm, or the releasing truth table yourself."
                ),
            })
            continue
        break
    return {
        "text": final_text,
        "tool_calls": called,
        "nudges": nudges,
        "stop_reason": stop_reason,
    }


class AnthropicMessages:
    """Thin wrapper so the loop and the UI share one client."""

    def __init__(self, api_key: str, model: str = MODEL_ID):
        import anthropic

        self.model = model
        # Retries live in create() so a 429 or 529 is visible and bounded.
        self._client = anthropic.Anthropic(api_key=api_key, timeout=300.0, max_retries=0)

    def create(self, **kwargs):
        kwargs.pop("temperature", None)
        kwargs.pop("top_p", None)
        kwargs.pop("top_k", None)
        thinking = kwargs.get("thinking")
        if isinstance(thinking, dict) and thinking.get("type") == "disabled":
            raise ValueError("claude-opus-5-5 does not accept thinking disabled")
        # Forced tool use errors on this model. Leave the choice unset (auto).
        choice = kwargs.pop("tool_choice", None)
        if isinstance(choice, dict) and choice.get("type") in ("any", "tool"):
            raise ValueError("claude-opus-5-5 rejects forced tool_choice; leave it on auto")
        kwargs.setdefault("model", self.model)
        delay = 1.0
        for attempt in range(3):
            try:
                return self._client.messages.create(**kwargs)
            except Exception as exc:
                if attempt == 2 or not _transient_api_error(exc):
                    raise
                time.sleep(delay)
                delay *= 2
        raise RuntimeError("Claude request was not sent")

    def check_model(self) -> str:
        info = self._client.models.retrieve(self.model)
        return getattr(info, "id", self.model)
