"""Messages API tool loop for Claude Opus 5.5.

Verified against platform.claude.com on 2026-10-23:
- model id is claude-opus-5-5
- tools use name, description, and input_schema
- Opus 5.5 rejects forced tool_choice (type "any" or type "tool"), so this
  loop leaves tool choice on the default (auto) and asks again in a user
  message when a required tool was skipped
- adaptive thinking stays on; this client does not send thinking disabled,
  temperature, top_p, or top_k

A size rejection (HTTP 413, or a 400 for a prompt over the context window)
is raised as RequestTooLarge on the first attempt. The request is not trimmed
and not resent. incomplete_notice labels a reply whose stop_reason says it
did not finish.

Prompt caching. The system text and the tool list are byte-identical on
every round of a turn, and on every turn in the same mode on the same
content pack. AnthropicMessages.create sends the system text as one text
block with a cache breakpoint, so later rounds and later turns read tools
plus system from the cache instead of paying for them again. On a request
that carries tools (the tool loop), it also asks for automatic caching on
the growing message tail, so a skill body or a tool result read on one
round is cached for the rounds after it. Nothing is trimmed, reordered, or
shortened. run_tool_loop sums the usage the API reports on each round so a
caller can show how much was read from the cache.

Streaming. AnthropicMessages.streaming(on_event) returns a callable with the
signature of create() that sends the same request through messages.stream
and reports the reply as it is written: {"type": "text", "text": ...} for
each piece of reply text, {"type": "thinking"} when a thinking block opens,
and {"type": "reset"} when a failed attempt is about to be sent again, so a
listener drops the words of the attempt that failed. The request body, the
cache markers, the retries, and the returned message are the same as
create()'s, so the tool loop does not know which one it was given. Tool
definitions are not marked for eager input streaming: every tool here takes
a few scalars, and the API keeps validating them.

Retries. A rate limit, an overload, a timeout, or a dropped connection is
sent again, up to RETRY_ATTEMPTS attempts in all. The wait is the API's
retry-after when it names one, and otherwise RETRY_WAITS. A retry-after is
waited out whole, since the API says an earlier attempt fails; one longer
than RETRY_AFTER_MAX is not waited at all, and the request stops with how
long the API asked for. The wait is on the job's cancel event when the
client has one, so Stop ends it at once. on_retry, when set, hears each
wait so the window can say why nothing is moving. A long team turn makes
dozens of requests, and one refused request must not lose the turn.

A spend limit is not a rate limit. The usage tier's monthly spend cap is a
429 marked enforced_spend_limit_reached with no retry-after, and it fails
until the next month; a spend limit the owner set on the organization or a
workspace is a 400; a billing problem is a 402. None of them is sent again:
the request stops at once with SpendLimitReached, in plain words, with the
API's own message, which says when access resumes.

Request ids. Every response carries the API's request-id, and the
anthropic-workspace-id of the workspace it was billed to. The client keeps
both for each request it sent, answered or refused (requests), and the
window writes them to the job's record when the job ends.

Effort. FPFA_EFFORT, or the effort argument, adds output_config.effort to
every request this client sends, on both paths alike. It is unset by
default, which leaves the model on its own default (medium on Opus 5.5).
It is there so cost and time can be compared against quality on a live
run; nothing in the app sets it.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any, Callable

MODEL_ID = "claude-opus-5-5"
# Attempts for one request, the first included.
RETRY_ATTEMPTS = 5
# Seconds before the second, third, fourth, and fifth attempt when the API names no wait.
RETRY_WAITS = (2.0, 4.0, 8.0, 16.0)
# The longest retry-after the client waits out by itself. A longer one stops the request with the API's wait in
# the message: the API says an attempt before it fails, so waiting less would only spend an attempt.
RETRY_AFTER_MAX = 120.0
# The tier's monthly spend cap: a 429 that is not a rate limit. error.details.error_code says which it is.
SPEND_CAP_CODE = "enforced_spend_limit_reached"
# A spend limit the owner set: a 400 whose message the API documents as starting with one of these.
_SPEND_LIMIT_PREFIXES = (
    "You have reached your specified API usage limits",
    "You have reached your specified workspace API usage limits",
)
# The most request ids one client keeps. A team turn makes dozens; this bounds a runaway one.
REQUEST_LOG_LIMIT = 500
EFFORTS = ("low", "medium", "high", "xhigh", "max")
EFFORT_ENV = "FPFA_EFFORT"
# One breakpoint on the system block caches tools plus system. The same
# value as a top-level request field asks the API to cache the last block of
# the message list automatically, so each tool round reads the rounds before it.
CACHE_CONTROL = {"type": "ephemeral"}
_USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)
_log = logging.getLogger("fpfa.claude")
_TRANSIENT_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}
_TRANSIENT_TYPES = {"APIConnectionError", "APITimeoutError", "RateLimitError", "InternalServerError"}
# A 400 for a prompt over the context window has no class of its own in the SDK.
_TOO_LARGE_WORDS = ("too long", "too large", "context window", "context limit")
# stop_reason values that mean the reply did not finish. tool_use is listed
# because the loop only ends on it when the tool-round limit ran out.
_INCOMPLETE = {
    "max_tokens": "Claude stopped because the reply hit the output limit (stop_reason max_tokens)",
    "model_context_window_exceeded": (
        "Claude stopped because the request and reply filled the model's context window "
        "(stop_reason model_context_window_exceeded)"
    ),
    "refusal": "Claude declined to finish this reply (stop_reason refusal)",
    "pause_turn": "The API paused the turn before the reply finished (stop_reason pause_turn)",
    "tool_use": (
        "The turn ran out of tool rounds while Claude was still calling tools (stop_reason tool_use)"
    ),
}


class RequestTooLarge(RuntimeError):
    """The API rejected the complete request for its size. Nothing was trimmed or resent."""


class TurnCancelled(RuntimeError):
    """The designer cancelled the job. The loop stopped before its next model round."""


class SpendLimitReached(RuntimeError):
    """The API refused the request because a spend limit or a billing problem stops it. It was not sent again."""

    def __init__(self, message: str, *, status_code: int | None = None, request_id: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id


class RetryWaitTooLong(RuntimeError):
    """The API asked for a longer wait before another attempt than the client waits out by itself."""


def safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(r"sk-ant-[A-Za-z0-9_\-]+", "[key]", text)
    return text[:800]


def request_too_large(exc: BaseException) -> bool:
    """True for HTTP 413, or a 400 that says the prompt is over the context window."""
    status = getattr(exc, "status_code", None)
    if status == 413:
        return True
    if status != 400:
        return False
    text = str(exc).lower()
    return any(word in text for word in _TOO_LARGE_WORDS)


def cached_system(system: Any) -> Any:
    """System text as content blocks, with a cache breakpoint on the last text block.

    A string becomes one text block that holds the whole string. A list is
    copied block by block, and the last text block gets the breakpoint unless
    a block already carries one. The text is not changed. None and an empty
    value pass through unchanged.
    """
    if system is None or system == "" or system == []:
        return system
    if isinstance(system, str):
        return [{"type": "text", "text": system, "cache_control": dict(CACHE_CONTROL)}]
    blocks = [dict(block) if isinstance(block, dict) else block for block in system]
    if any(isinstance(block, dict) and block.get("cache_control") for block in blocks):
        return blocks
    for block in reversed(blocks):
        if isinstance(block, dict) and block.get("type") == "text":
            block["cache_control"] = dict(CACHE_CONTROL)
            break
    return blocks


def empty_usage() -> dict:
    """Running totals for one turn. rounds counts the API calls that were made."""
    totals = {field: 0 for field in _USAGE_FIELDS}
    totals["rounds"] = 0
    return totals


def add_usage(totals: dict, usage: Any) -> dict:
    """Add one response's usage to the totals. A missing block or field counts as 0."""
    totals["rounds"] = int(totals.get("rounds", 0)) + 1
    if usage is None:
        return totals
    for field in _USAGE_FIELDS:
        if isinstance(usage, dict):
            value = usage.get(field)
        else:
            value = getattr(usage, field, None)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        totals[field] = int(totals.get(field, 0)) + int(value)
    return totals


def attach_usage(exc: BaseException, usage: dict | None) -> None:
    """Put the usage known so far on an exception, added to any it already carries.

    A failure does not un-spend the rounds that ran before it. Every layer a
    failure passes through (the tool loop, a consult, a delegation, the lead's
    turn) adds what it knows, so the record can close the task with it.
    """
    known = dict(getattr(exc, "usage", None) or {})
    for key, value in (usage or {}).items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        known[key] = int(known.get(key, 0)) + int(value)
    try:
        exc.usage = known
    except Exception:
        # An exception type that takes no attributes. The usage is lost with it; nothing else can be done.
        pass


def usage_summary(usage: dict | None) -> str:
    """One status-line sentence on token use. Empty when no round was counted.

    Input tokens are the uncached tokens plus the tokens written to the cache
    plus the tokens read from it. The percent is the share read from the cache.
    """
    if not isinstance(usage, dict) or not usage.get("rounds"):
        return ""
    rounds = int(usage["rounds"])
    fresh = int(usage.get("input_tokens") or 0)
    written = int(usage.get("cache_creation_input_tokens") or 0)
    read = int(usage.get("cache_read_input_tokens") or 0)
    output = int(usage.get("output_tokens") or 0)
    total_in = fresh + written + read
    word = "round" if rounds == 1 else "rounds"
    text = f"{rounds} {word}, {total_in:,} input tokens"
    if total_in:
        text += f" ({read * 100 // total_in}% read from cache)"
    return text + f", {output:,} output tokens."


def incomplete_notice(stop_reason: str | None) -> str:
    """A label for a reply the API reported as unfinished. Empty when it finished."""
    reason = _INCOMPLETE.get(stop_reason or "")
    if not reason:
        return ""
    return f"Incomplete reply. {reason}. The text is partial and is not a complete answer."


def retry_wait(exc: BaseException, attempt: int) -> float:
    """Seconds before the next attempt. attempt counts the failures so far, starting at 0.

    The API's retry-after header wins when it gives a number of seconds, whole:
    an attempt before it fails. Without one the wait doubles from RETRY_WAITS.
    The caller decides whether a long one is waited out (RETRY_AFTER_MAX).
    """
    named = _named_wait(exc)
    if named is not None:
        return named
    return RETRY_WAITS[min(max(attempt, 0), len(RETRY_WAITS) - 1)]


def _named_wait(exc: BaseException) -> float | None:
    """The API's retry-after in seconds, or None when the response names none."""
    headers = getattr(getattr(exc, "response", None), "headers", None)
    named = None
    if headers is not None:
        try:
            named = headers.get("retry-after")
        except Exception:
            named = None
    if named in (None, ""):
        return None
    try:
        return max(0.0, float(named))
    except (TypeError, ValueError):
        return None


def _error_code(exc: BaseException) -> str:
    """error.details.error_code from the API's error body: the SDK's own field, or the body it kept."""
    code = getattr(exc, "error_code", None)
    if isinstance(code, str) and code:
        return code
    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, dict) else None
    details = error.get("details") if isinstance(error, dict) else None
    found = details.get("error_code") if isinstance(details, dict) else None
    return found if isinstance(found, str) else ""


def _api_message(exc: BaseException) -> str:
    """error.message from the API's error body, or "" when there is none."""
    message = getattr(exc, "api_message", None)
    if isinstance(message, str) and message:
        return message
    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, dict) else None
    return str(error.get("message") or "") if isinstance(error, dict) else ""


def spend_stop(exc: BaseException) -> str:
    """Why sending this request again cannot help: a spend cap, a spend limit, or a billing problem. Else "".

    The tier's monthly cap is told from a rate limit by its error code, never
    by its wording. A spend limit the owner set is a 400 the API documents by
    the start of its message; a 400 is not sent again in any case, so the
    message only says plainly what happened.
    """
    status = getattr(exc, "status_code", None)
    said = _api_message(exc)
    tail = f" The API said: {said}" if said else ""
    if status == 429 and _error_code(exc) == SPEND_CAP_CODE:
        return ("The organization has reached its usage tier's monthly API spend cap. The API refuses every request "
                "until access resumes, so the application did not send this one again." + tail)
    if status == 400 and said.startswith(_SPEND_LIMIT_PREFIXES):
        return ("A spend limit set on the organization, or on the workspace of this API key, has been reached. The "
                "API refuses requests until the limit is raised or access resumes." + tail)
    if status == 402:
        return "The API reports a billing problem (402). Check the payment details in the Claude Console." + tail
    return ""


def configured_effort(value: str | None = None) -> str:
    """The effort to send, or "" to send none. An unknown word is treated as none."""
    text = (value if value is not None else os.environ.get(EFFORT_ENV, "")).strip().lower()
    return text if text in EFFORTS else ""


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


def _tell(observe: Callable[[dict], Any] | None, event: dict) -> None:
    """Report progress to a listener. A listener that fails never fails the turn."""
    if observe is None:
        return
    try:
        observe(event)
    except Exception:
        _log.exception("progress listener failed")


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
    cancel: Any = None,
    observe: Callable[[dict], Any] | None = None,
) -> dict:
    """Call create() the way Messages.create is called. execute() runs a client tool.

    cancel is an optional threading.Event. When it is set, the loop raises
    TurnCancelled before its next model round. A round already in flight
    finishes; a tool already running finishes.

    observe is an optional listener for the window's working line. It is
    told {"type": "round", "round": n} before each model round and
    {"type": "tool_start" | "tool_end", "name": ..., "input": ...} around
    each tool. It changes nothing the loop sends or returns.
    """
    required = list(required or [])
    messages: list[dict] = [{"role": "user", "content": user_text}]
    called: list[dict] = []
    nudges = 0
    final_text = ""
    stop_reason = ""
    usage = empty_usage()
    for _ in range(max_rounds):
        if cancel is not None and cancel.is_set():
            cancelled = TurnCancelled("Cancelled by the designer before the next model round.")
            # The rounds that ran were billed. The caller can still record them.
            cancelled.usage = dict(usage)
            raise cancelled
        _tell(observe, {"type": "round", "round": int(usage["rounds"]) + 1})
        try:
            response = create(
                model=MODEL_ID,
                max_tokens=max_tokens,
                system=system,
                tools=tools,
                messages=messages,
            )
        except Exception as exc:
            # The rounds before this one were billed. The caller records them with the failure, or with the
            # cancel when the designer stopped the job during a wait to send it again. The request that failed
            # returned no usage: whether any part of it was billed is not known here.
            attach_usage(exc, usage)
            raise
        add_usage(usage, getattr(response, "usage", None))
        _log.info(
            "totals after round %d: input %d, cache write %d, cache read %d, output %d",
            usage["rounds"],
            usage["input_tokens"],
            usage["cache_creation_input_tokens"],
            usage["cache_read_input_tokens"],
            usage["output_tokens"],
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
                _tell(observe, {"type": "tool_start", "name": name, "input": tool_input})
                try:
                    output = execute(name, tool_input)
                    is_error = False
                    payload = json.dumps(output, default=str)
                except TurnCancelled as exc:
                    # A cancel inside a tool (a delegated specialist) ends this turn too.
                    # The caller merged the nested usage; this carries the loop's own.
                    _tell(observe, {"type": "tool_end", "name": name, "is_error": True})
                    cancelled = TurnCancelled(str(exc))
                    cancelled.usage = dict(usage)
                    raise cancelled from exc
                except Exception as exc:
                    is_error = True
                    output = {"error": safe_error(exc)}
                    payload = output["error"]
                _tell(observe, {"type": "tool_end", "name": name, "is_error": is_error})
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
        "usage": usage,
    }


class AnthropicMessages:
    """Thin wrapper so the loop and the UI share one client."""

    def __init__(self, api_key: str, model: str = MODEL_ID, *, effort: str | None = None,
                 on_retry: Callable[[dict], Any] | None = None, cancel: Any = None):
        import anthropic

        self.model = model
        self.effort = configured_effort(effort)
        # Hears {"type": "retry", "attempt", "of", "wait_s", "status"} before each wait.
        self.on_retry = on_retry
        # The job's threading.Event. A wait before another attempt ends at once when it is set.
        self.cancel = cancel
        # Requests sent again after a failure, since this client was made. A failed attempt reports no
        # usage, so nothing here can say what it cost; the count is what can be said.
        self.retries = 0
        # Every request this client sent that the API answered or refused with an id: {"id", "workspace",
        # "status", "at"}. Quoted to the provider's support, and how a bill is matched to a job.
        self.requests: list[dict] = []
        # Retries live in create() so a 429 or 529 is visible and bounded.
        self._client = anthropic.Anthropic(api_key=api_key, timeout=300.0, max_retries=0)

    def _prepare(self, kwargs: dict) -> dict:
        """The request as it is sent. Shared by create() and the streaming path."""
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
        # Cache breakpoint on the system text. Tools render before it, so one
        # marker caches both. The text is sent whole; only its shape changes.
        if kwargs.get("system"):
            kwargs["system"] = cached_system(kwargs["system"])
        # A tool loop resends the growing message list every round. Automatic
        # caching puts a moving breakpoint on its last block. A single call
        # with no tools (the blind claim check) has no later round to read
        # that entry, so it is left off there.
        if kwargs.get("tools"):
            kwargs.setdefault("cache_control", dict(CACHE_CONTROL))
        # Off unless the owner set it. The same field on the streamed path and the plain one.
        if self.effort:
            config = dict(kwargs.get("output_config") or {})
            config.setdefault("effort", self.effort)
            kwargs["output_config"] = config
        return kwargs

    def _note(self, request_id: Any, workspace_id: Any, status: Any) -> None:
        """Keep the API's id for one request. A response with none (a test's stand-in) keeps nothing."""
        if not isinstance(request_id, str) or not request_id or len(self.requests) >= REQUEST_LOG_LIMIT:
            return
        self.requests.append({
            "id": request_id, "workspace": workspace_id if isinstance(workspace_id, str) else "",
            "status": status, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

    def _wait(self, seconds: float) -> None:
        """Wait before another attempt. On the job's cancel event when there is one, so Stop ends the wait."""
        if self.cancel is None:
            time.sleep(seconds)
            return
        if self.cancel.wait(seconds):
            raise TurnCancelled("Cancelled by the designer while waiting to send a refused request again.")

    def _send(self, kwargs: dict, on_event: Callable[[dict], Any] | None = None):
        """Send one request, with the bounded retry. on_event turns the call into a stream."""
        for attempt in range(RETRY_ATTEMPTS):
            try:
                if on_event is None:
                    response = self._client.messages.create(**kwargs)
                    self._note(getattr(response, "_request_id", None), getattr(response, "_workspace_id", None), "ok")
                    return response
                return self._stream(kwargs, on_event)
            except TurnCancelled:
                raise
            except Exception as exc:
                self._note(getattr(exc, "request_id", None), getattr(exc, "workspace_id", None),
                           getattr(exc, "status_code", None) or type(exc).__name__)
                # Checked before the transient retry so a size rejection is never resent.
                if request_too_large(exc):
                    raise RequestTooLarge(
                        "Claude rejected the request as too large for the model's context window "
                        "or the API request size limit. The app did not trim the request or resend "
                        "it with parts missing, and no file on disk was changed. Chat, zone, and "
                        "starter requests carry every specs/*.md file in full. To send less, shorten "
                        "the question or start a new job so fewer earlier turns are included. "
                        "API response: " + safe_error(exc)
                    ) from exc
                stop = spend_stop(exc)
                if stop:
                    # Sending it again cannot help, and the turn should say why in plain words.
                    raise SpendLimitReached(stop, status_code=getattr(exc, "status_code", None),
                                            request_id=getattr(exc, "request_id", None)) from exc
                if attempt == RETRY_ATTEMPTS - 1 or not _transient_api_error(exc):
                    raise
                wait = retry_wait(exc, attempt)
                if wait > RETRY_AFTER_MAX:
                    raise RetryWaitTooLong(
                        f"The API asked for {wait:.0f} s before another attempt, longer than the application waits by "
                        f"itself ({RETRY_AFTER_MAX:.0f} s). Nothing was sent again. Try again after that. "
                        + safe_error(exc)
                    ) from exc
                # The words of the failed attempt are not the reply. The listener drops them.
                _tell(on_event, {"type": "reset"})
                self.retries += 1
                _tell(self.on_retry, {
                    "type": "retry", "attempt": attempt + 2, "of": RETRY_ATTEMPTS, "wait_s": wait,
                    "status": getattr(exc, "status_code", None),
                })
                _log.warning("request failed (%s); attempt %d of %d in %.0f s",
                             type(exc).__name__, attempt + 2, RETRY_ATTEMPTS, wait)
                self._wait(wait)
        raise RuntimeError("Claude request was not sent")

    def _stream(self, kwargs: dict, on_event: Callable[[dict], Any]):
        """One streamed request. Returns the same Message that create() returns."""
        with self._client.messages.stream(**kwargs) as stream:
            for event in stream:
                kind = getattr(event, "type", "")
                if kind == "content_block_start":
                    block = getattr(getattr(event, "content_block", None), "type", "")
                    if block in ("thinking", "redacted_thinking"):
                        _tell(on_event, {"type": "thinking"})
                    elif block == "tool_use":
                        _tell(on_event, {"type": "tool_use", "name": getattr(event.content_block, "name", "")})
                elif kind == "content_block_delta":
                    delta = getattr(event, "delta", None)
                    if getattr(delta, "type", "") == "text_delta":
                        text = getattr(delta, "text", "") or ""
                        if text:
                            _tell(on_event, {"type": "text", "text": text})
            message = stream.get_final_message()
            # The final message of a stream carries no request id of its own; the stream's response does.
            self._note(getattr(stream, "request_id", None), getattr(stream, "workspace_id", None), "ok")
            return message

    def create(self, **kwargs):
        return self._send(self._prepare(kwargs))

    def streaming(self, on_event: Callable[[dict], Any]) -> Callable[..., Any]:
        """A create() that streams and reports the reply as it is written.

        The returned callable takes what create() takes and returns what it
        returns. on_event runs on the calling thread, once per event.
        """
        def create(**kwargs):
            return self._send(self._prepare(kwargs), on_event)

        return create

    def check_model(self) -> str:
        info = self._client.models.retrieve(self.model)
        return getattr(info, "id", self.model)
