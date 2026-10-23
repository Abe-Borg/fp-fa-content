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
from typing import Any, Callable

MODEL_ID = "claude-opus-5-5"


def safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(r"sk-ant-[A-Za-z0-9_\-]+", "[key]", text)
    return text[:800]


def _wire_block(block: Any) -> dict:
    if isinstance(block, dict):
        return block
    if hasattr(block, "model_dump"):
        return block.model_dump(exclude_none=True)
    kind = getattr(block, "type", None)
    data = {"type": kind}
    if kind == "text":
        data["text"] = getattr(block, "text", "")
    elif kind == "tool_use":
        data["id"] = getattr(block, "id", "")
        data["name"] = getattr(block, "name", "")
        data["input"] = getattr(block, "input", {}) or {}
    elif kind == "thinking":
        data["thinking"] = getattr(block, "thinking", "")
        data["signature"] = getattr(block, "signature", "")
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
    for _ in range(max_rounds):
        response = create(
            model=MODEL_ID,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        wire = [_wire_block(block) for block in response.content]
        messages.append({"role": "assistant", "content": wire})
        uses = [block for block in wire if block.get("type") == "tool_use"]
        texts = [block.get("text", "") for block in wire if block.get("type") == "text" and block.get("text")]
        if texts:
            final_text = "\n".join(texts).strip()
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
    return {"text": final_text, "tool_calls": called, "nudges": nudges}


class AnthropicMessages:
    """Thin wrapper so the loop and the UI share one client."""

    def __init__(self, api_key: str, model: str = MODEL_ID):
        import anthropic

        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def create(self, **kwargs):
        kwargs.pop("temperature", None)
        kwargs.pop("top_p", None)
        kwargs.pop("top_k", None)
        thinking = kwargs.get("thinking")
        if isinstance(thinking, dict) and thinking.get("type") == "disabled":
            raise ValueError("claude-opus-5-5 does not accept thinking disabled")
        # Forced tool use errors on this model. Refuse it here too.
        choice = kwargs.get("tool_choice")
        if isinstance(choice, dict) and choice.get("type") in ("any", "tool"):
            raise ValueError("claude-opus-5-5 rejects forced tool_choice; leave it on auto")
        kwargs.setdefault("model", self.model)
        return self._client.messages.create(**kwargs)

    def check_model(self) -> str:
        info = self._client.models.retrieve(self.model)
        return getattr(info, "id", self.model)


SYSTEM_PROMPT = """You are the design assistant inside a desktop application for hyperscale data-center fire protection.

Scope you may help design: wet pipe, dry pipe, and double-interlock preaction sprinklers, and the fire-alarm detection and releasing that trip them.
Refuse, in a short paragraph, anything else: foam, foam-water, clean agent, water mist, deluge, single-interlock preaction, and non-interlock preaction. Do not design those systems.

Math rule: gallons, seconds, gpm, psi, scfm, density demand, and the releasing truth table come from tool results. Do not compute them yourself. If a tool returns an error, say so. Quote the tool figures in your draft.

Method rule: design methods are files in the content pack. Call list_skills and read_skill for the method you apply. Do not invent a method when a skill is in the pack.

The application's tables are built from the tool plan on the designer's form. Your prose is the draft narrative. It has to match those tool figures. A water-delivery result from these tools is an optimistic screen, not a listed water-delivery calculation. Judgment calls are for the engineer of record to verify.

Do not name a valve, solenoid, or panel catalog number as if it were elected. Elect by function and listing.
"""
