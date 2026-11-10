"""The streamed Messages path, the tool loop's progress listener, and what the window does with both.

Every model call is a stand-in. The first two classes need no display.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402



class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def _text_event(text: str):
    return SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="text_delta", text=text))


def _start_event(kind: str, **fields):
    return SimpleNamespace(type="content_block_start", content_block=SimpleNamespace(type=kind, **fields))


class _Inner:
    """Stand-in for anthropic.Anthropic with both create() and stream()."""

    def __init__(self, reply, events=(), errors=()):
        self.reply = reply
        self.events = list(events)
        self.errors = list(errors)
        self.created: list[dict] = []
        self.streamed: list[dict] = []
        self.messages = self

    def create(self, **kwargs):
        self.created.append(kwargs)
        return self.reply

    def stream(self, **kwargs):
        inner = self

        class _Stream:
            def __enter__(self):
                inner.streamed.append(kwargs)
                return self

            def __exit__(self, *_exc):
                return False

            def __iter__(self):
                error = inner.errors.pop(0) if inner.errors else None
                for event in inner.events:
                    yield event
                    if error is not None and getattr(event, "type", "") == "content_block_delta":
                        raise error

            def get_final_message(self):
                return inner.reply

        return _Stream()


def _client(inner):
    from fpfa.claude_client import AnthropicMessages

    client = AnthropicMessages("sk-ant-test-not-sent")
    client._client = inner
    return client


def _status_error(status: int, message: str):
    import anthropic

    cls = {413: getattr(anthropic, "ContentTooLargeError", None) or anthropic.RequestTooLargeError,
           529: anthropic.InternalServerError}.get(status, anthropic.BadRequestError)
    body = {"type": "error", "error": {"type": "error", "message": message}}
    response = SimpleNamespace(status_code=status, headers={}, request=None)
    return cls(f"Error code: {status} - {body}", response=response, body=body)


REPLY = SimpleNamespace(stop_reason="end_turn", content=[Block(type="text", text="Zone total is 281.3 gal.")])
EVENTS = [
    _start_event("thinking"),
    _start_event("text"),
    _text_event("Zone total "),
    _text_event("is 281.3 gal."),
    SimpleNamespace(type="message_stop"),
]
TOOLS = [{"name": "zone_trapped_volume", "description": "d", "input_schema": {"type": "object"}}]


class StreamingClientTests(unittest.TestCase):
    def test_a_stream_reports_the_reply_and_returns_the_same_message(self):
        inner = _Inner(REPLY, EVENTS)
        heard = []
        create = _client(inner).streaming(heard.append)
        out = create(max_tokens=100, system="SYSTEM TEXT", tools=TOOLS, messages=[{"role": "user", "content": "q"}])
        self.assertIs(out, REPLY)
        self.assertEqual(heard, [
            {"type": "thinking"},
            {"type": "text", "text": "Zone total "},
            {"type": "text", "text": "is 281.3 gal."},
        ])
        self.assertEqual(inner.created, [])
        self.assertEqual(len(inner.streamed), 1)

    def test_the_streamed_request_is_the_request_create_sends(self):
        """Same model, same cached system block, same cache marker on the tail, same tools: one cache."""
        plain, streamed = _Inner(REPLY), _Inner(REPLY, EVENTS)
        call = {"max_tokens": 16000, "system": "SYSTEM TEXT", "tools": TOOLS,
                "messages": [{"role": "user", "content": "q"}], "temperature": 0.2, "top_p": 0.9, "top_k": 5}
        _client(plain).create(**{**call, "messages": list(call["messages"])})
        _client(streamed).streaming(lambda _event: None)(**{**call, "messages": list(call["messages"])})
        self.assertEqual(streamed.streamed[0], plain.created[0])
        sent = streamed.streamed[0]
        self.assertEqual(sent["model"], "claude-opus-5-5")
        self.assertEqual(sent["system"], [
            {"type": "text", "text": "SYSTEM TEXT", "cache_control": {"type": "ephemeral"}}
        ])
        self.assertEqual(sent["cache_control"], {"type": "ephemeral"})
        for dropped in ("temperature", "top_p", "top_k", "tool_choice", "thinking"):
            self.assertNotIn(dropped, sent)
        # The tools go out as written: no tool is marked for eager input streaming.
        self.assertEqual(sent["tools"], TOOLS)
        self.assertNotIn("eager_input_streaming", str(sent["tools"]))

    def test_the_stream_refuses_what_create_refuses(self):
        create = _client(_Inner(REPLY, EVENTS)).streaming(lambda _event: None)
        with self.assertRaises(ValueError):
            create(max_tokens=10, messages=[], thinking={"type": "disabled"})
        with self.assertRaises(ValueError):
            create(max_tokens=10, messages=[], tool_choice={"type": "any"})

    def test_a_failed_attempt_is_reset_before_it_is_sent_again(self):
        inner = _Inner(REPLY, EVENTS, errors=[_status_error(529, "Overloaded")])
        heard = []
        clock = SimpleNamespace(sleep=Mock())
        with patch("fpfa.claude_client.time", clock):
            out = _client(inner).streaming(heard.append)(max_tokens=10, messages=[{"role": "user", "content": "q"}])
        self.assertIs(out, REPLY)
        self.assertEqual(len(inner.streamed), 2)
        clock.sleep.assert_called_once()
        kinds = [event["type"] for event in heard]
        # First attempt: one piece, then the failure. The listener is told to drop it.
        self.assertEqual(kinds, ["thinking", "text", "reset", "thinking", "text", "text"])
        after = heard[kinds.index("reset") + 1:]
        self.assertEqual("".join(event.get("text", "") for event in after), "Zone total is 281.3 gal.")

    def test_a_request_that_is_too_large_is_raised_once_and_never_resent(self):
        from fpfa.claude_client import RequestTooLarge

        inner = _Inner(REPLY, EVENTS, errors=[_status_error(413, "Request exceeds the maximum allowed number of bytes.")])
        heard = []
        clock = SimpleNamespace(sleep=Mock())
        with patch("fpfa.claude_client.time", clock), self.assertRaises(RequestTooLarge):
            _client(inner).streaming(heard.append)(max_tokens=10, messages=[{"role": "user", "content": "q"}])
        self.assertEqual(len(inner.streamed), 1)
        clock.sleep.assert_not_called()
        self.assertNotIn({"type": "reset"}, heard)

    def test_a_listener_that_fails_does_not_fail_the_turn(self):
        def broken(_event):
            raise RuntimeError("the window went away")

        inner = _Inner(REPLY, EVENTS)
        with self.assertLogs("fpfa.claude", level="ERROR"):
            out = _client(inner).streaming(broken)(max_tokens=10, messages=[{"role": "user", "content": "q"}])
        self.assertIs(out, REPLY)


class ObserveTests(unittest.TestCase):
    def _script(self):
        turns = [
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="t1", name="read_skill", input={"slug": "dry-pipe"}),
            ]),
            SimpleNamespace(stop_reason="end_turn", content=[Block(type="text", text="Done.")]),
        ]
        return lambda **_kwargs: turns.pop(0)

    def test_the_loop_reports_rounds_and_tools_and_returns_what_it_returned_before(self):
        from fpfa.claude_client import run_tool_loop

        heard = []
        args = dict(system="s", user_text="q", tools=[], execute=lambda name, _input: {"ok": name})
        watched = run_tool_loop(self._script(), observe=heard.append, **args)
        plain = run_tool_loop(self._script(), **args)
        self.assertEqual(watched, plain)
        self.assertEqual(heard, [
            {"type": "round", "round": 1},
            {"type": "tool_start", "name": "read_skill", "input": {"slug": "dry-pipe"}},
            {"type": "tool_end", "name": "read_skill", "is_error": False},
            {"type": "round", "round": 2},
        ])

    def test_a_failing_tool_and_a_failing_listener(self):
        from fpfa.claude_client import run_tool_loop

        heard = []

        def execute(_name, _input):
            raise ValueError("density must be a number")

        out = run_tool_loop(self._script(), system="s", user_text="q", tools=[], execute=execute, observe=heard.append)
        self.assertTrue(out["tool_calls"][0]["is_error"])
        self.assertIn({"type": "tool_end", "name": "read_skill", "is_error": True}, heard)

        def broken(_event):
            raise RuntimeError("no window")

        with self.assertLogs("fpfa.claude", level="ERROR"):
            again = run_tool_loop(
                self._script(), system="s", user_text="q", tools=[],
                execute=lambda name, _input: {"ok": name}, observe=broken,
            )
        self.assertEqual(again["text"], "Done.")

    def test_a_specialists_events_carry_its_slug(self):
        from fpfa.record import Record
        from fpfa.team import delegate

        record = Record(Path(tempfile.mkdtemp(prefix="fpfa-stream-")) / "fpfa.db")
        heard = []
        out = delegate(
            REPO, record, "p1", self._script(), specialist="fp-sprinkler",
            brief="Size the zone.", observe=heard.append,
        )
        self.assertEqual(out["summary"], "Done.")
        self.assertTrue(heard)
        self.assertTrue(all(event.get("agent") == "fp-sprinkler" for event in heard))
        self.assertEqual([event["type"] for event in heard], ["round", "tool_start", "tool_end", "round"])

    def test_the_working_line_names_the_tool_and_never_a_result(self):
        from fpfa.desk import describe_activity

        self.assertEqual(describe_activity({"type": "round", "round": 2}), "thinking")
        self.assertEqual(
            describe_activity({"type": "tool_start", "name": "read_skill", "input": {"slug": "dry-pipe-delivery"}}),
            "reading the dry-pipe-delivery skill",
        )
        self.assertEqual(describe_activity({"type": "tool_start", "name": "read_role", "input": {}}), "reading a role")
        self.assertEqual(describe_activity({"type": "tool_start", "name": "search_corpus", "input": {"query": "x"}}),
                         "searching the corpus")
        self.assertEqual(describe_activity({"type": "tool_start", "name": "record_finding", "input": {}}),
                         "writing to the project record")
        self.assertEqual(
            describe_activity({"type": "tool_start", "name": "delegate", "input": {"specialist": "fa-releasing"}}),
            "handing off to fa-releasing",
        )
        self.assertEqual(describe_activity({"type": "tool_start", "name": "request_check", "input": {}}),
                         "running the blind check")
        # A calc tool is named. Its inputs and its figures are not shown.
        line = describe_activity({"type": "tool_start", "name": "zone_trapped_volume",
                                  "input": {"segments": [{"length_ft": 900}]}, "agent": "fp-sprinkler"})
        self.assertEqual(line, "fp-sprinkler: running zone_trapped_volume")
        self.assertNotIn("900", line)
        self.assertEqual(describe_activity({"type": "tool_end", "name": "x", "is_error": False}), "thinking")
        self.assertIsNone(describe_activity({"type": "something-else"}))

    def test_suggestions_follow_the_thread(self):
        from fpfa.desk import suggested_prompts

        empty = suggested_prompts(None, [], key_saved=False)
        self.assertEqual([action for _label, action in empty], ["/sample-di", "/help"])
        with_key = suggested_prompts(None, [], key_saved=True)
        self.assertEqual(len(with_key), 3)
        self.assertEqual(with_key[0][1], "/sample-di")
        project = {"last_run": {"tools": {}}, "di": {"zone_id": "DH-1"}}
        after_run = [{"role": "user", "text": "/sample-di"}, {"role": "assistant", "text": "Sample loaded."}]
        chips = suggested_prompts(project, after_run, key_saved=True)
        self.assertEqual(chips[0], ("Design basis", "Give me the design basis for zone DH-1."))
        self.assertEqual(len(chips), 3)
        # No key: a question could not be answered, so none is offered.
        self.assertEqual(suggested_prompts(project, after_run, key_saved=False), [])
        # A typed question, or a job in flight, clears them.
        asked = after_run + [{"role": "user", "text": "Which trim family?"}]
        self.assertEqual(suggested_prompts(project, asked, key_saved=True), [])
        self.assertEqual(suggested_prompts(project, after_run, key_saved=True, busy=True), [])
        self.assertEqual(suggested_prompts(None, [], key_saved=True, busy=True), [])


def _isolate_data() -> Path:
    path = tempfile.mkdtemp(prefix="fpfa-stream-ui-")
    os.environ["FPFA_DATA_DIR"] = path
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    os.environ.pop("FPFA_CONTENT_ROOT", None)
    os.environ.pop("FPFA_THEME", None)
    os.environ.pop("FPFA_REDUCE_MOTION", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return Path(path)


ANSWER = (
    "## Design basis for zone DH-1\n\n"
    "The zone is a **double-interlock preaction** system.\n\n"
    "| Item | Value |\n| --- | --- |\n| Zone total | 281.3 gal |\n| t_total | 38.1 s |\n\n"
    "- The size exemption applies.\n- `t_total` does not pass the screen.\n\n"
    "1. Confirm the trim volume.\n2. Confirm the AHJ."
)


class StreamingWindowTests(unittest.TestCase):
    def _app(self, *, motion: bool = False, key: bool = True):
        _isolate_data()
        from fpfa.keystore import save_api_key
        
        if key:
            save_api_key("sk-ant-local-test")
        root = Loop()
        self.addCleanup(root.destroy)
        app = root.open_desk()
        root.update()
        return app

    def _pump(self, app, until, timeout: float = 6.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            app.pump()
            if until():
                return
            time.sleep(0.01)
        self.fail("timed out waiting for the window")

    def _thread(self, app) -> str:
        return app.thread_text()

    def test_a_streamed_reply_is_in_the_thread_before_the_turn_ends(self):
        from fpfa.projects import load_project

        app = self._app()
        release = threading.Event()

        class Streaming:
            def __init__(self, _key):
                pass

            def create(self, **_kwargs):
                raise AssertionError("the window streams when the client can")

            def streaming(self, on_event):
                def create(**_kwargs):
                    on_event({"type": "thinking"})
                    for start in range(0, 60, 12):
                        on_event({"type": "text", "text": ANSWER[start:start + 12]})
                    release.wait(5)
                    on_event({"type": "text", "text": ANSWER[60:]})
                    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=ANSWER)])

                return create

        try:
            with patch("fpfa.desk.AnthropicMessages", Streaming):
                app.send_chat("Give me the design basis for zone DH-1.")
                self._pump(app, lambda: "Design basis for zone DH-1" in self._thread(app))
                thread = self._thread(app)
                # The turn is still running: its words, its caption, and the working line are all there.
                self.assertEqual([job.status for job in app.jobs.snapshot()], ["running"])
                # The reply was cut inside a bold span. It is drawn bold already, with no stray asterisks.
                self.assertIn("The zone is a double-interl", thread)
                self.assertNotIn("**", thread)
                self.assertNotIn("Confirm the AHJ", thread)
                self.assertIn("| chat", thread)
                self.assertIn("Working on it…", thread)
                self.assertIn("▍", thread)
                self.assertEqual(app.chat_log[-1]["role"], "user")
                self.assertTrue(app._pending_here())
                release.set()
                self._pump(app, lambda: "Confirm the AHJ" in self._thread(app) and not app._pending_here())
        finally:
            release.set()
        thread = self._thread(app)
        self.assertNotIn("Working on it…", thread)
        self.assertNotIn("▍", thread)
        self.assertEqual(thread.count("Design basis for zone DH-1"), 1)
        self.assertEqual(app._lives, {})
        self.assertFalse(app._pending_here())
        saved = load_project(app.project["id"])
        self.assertTrue(saved["chat"][-1]["text"].endswith(ANSWER))
        self.assertEqual([job.status for job in app.jobs.snapshot()], ["done"])

    def test_a_specialists_words_stay_out_of_the_thread(self):
        app = self._app()
        app.start_sample_di()
        job = app.jobs.snapshot()[-1]
        on_event, observe = app._stream_listener(job.id)
        observe({"type": "round", "round": 1})
        observe({"type": "tool_start", "name": "delegate", "input": {"specialist": "fp-sprinkler"}})
        on_event({"type": "text", "text": "SPECIALIST SUMMARY"})
        on_event({"type": "thinking"})
        observe({"type": "tool_start", "name": "zone_trapped_volume", "input": {}, "agent": "fp-sprinkler"})
        observe({"type": "tool_end", "name": "zone_trapped_volume", "is_error": False, "agent": "fp-sprinkler"})
        observe({"type": "tool_end", "name": "delegate", "is_error": False})
        on_event({"type": "text", "text": "LEAD REPLY"})
        events = []
        while not app._stream_events.empty():
            events.append(app._stream_events.get_nowait()[1])
        texts = [event["text"] for event in events if event["type"] == "text"]
        self.assertEqual(texts, ["LEAD REPLY"])
        activity = [event["text"] for event in events if event["type"] == "activity"]
        self.assertEqual(activity, [
            "thinking",
            "handing off to fp-sprinkler",
            "fp-sprinkler: running zone_trapped_volume",
            "fp-sprinkler: thinking",
            "thinking",
        ])

    def test_text_from_a_later_round_replaces_text_from_an_earlier_one(self):
        """The tool loop keeps the text of the last round that wrote any. The thread shows the same."""
        app = self._app()
        app.start_sample_di()
        job = app.jobs.snapshot()[-1]
        on_event, observe = app._stream_listener(job.id)
        observe({"type": "round", "round": 1})
        on_event({"type": "text", "text": "Let me check the trim first."})
        observe({"type": "tool_start", "name": "elect_di_trim", "input": {}})
        observe({"type": "tool_end", "name": "elect_di_trim", "is_error": False})
        app._drain_stream_events()
        self.assertEqual(app._lives[job.id]["body"], "Let me check the trim first.")
        # A round with no text leaves the earlier text in place.
        observe({"type": "round", "round": 2})
        app._drain_stream_events()
        self.assertEqual(app._lives[job.id]["body"], "Let me check the trim first.")
        on_event({"type": "text", "text": "The trim family is "})
        on_event({"type": "text", "text": "El/El."})
        app._drain_stream_events()
        self.assertEqual(app._lives[job.id]["body"], "The trim family is El/El.")
        # A specialist's round inside a tool is not a round of the lead.
        observe({"type": "tool_start", "name": "delegate", "input": {"specialist": "fp-sprinkler"}})
        observe({"type": "round", "round": 1, "agent": "fp-sprinkler"})
        observe({"type": "tool_end", "name": "delegate", "is_error": False})
        on_event({"type": "text", "text": " Provisional."})
        app._drain_stream_events()
        self.assertEqual(app._lives[job.id]["body"], "The trim family is El/El. Provisional.")
        app._end_stream(job.id, job.project_id)
        self.assertEqual(app._lives, {})

    def test_a_retry_drops_the_words_of_the_failed_attempt(self):
        app = self._app()
        release = threading.Event()

        class Retried:
            def __init__(self, _key):
                pass

            def streaming(self, on_event):
                def create(**_kwargs):
                    on_event({"type": "text", "text": "HALF AN ANSWER THAT FAILED"})
                    on_event({"type": "reset"})
                    on_event({"type": "text", "text": "The second attempt."})
                    release.wait(5)
                    return SimpleNamespace(
                        stop_reason="end_turn", content=[SimpleNamespace(type="text", text="The second attempt.")]
                    )

                return create

        try:
            with patch("fpfa.desk.AnthropicMessages", Retried):
                app.send_chat("Which trim family?")
                self._pump(app, lambda: "The second attempt." in self._thread(app))
                self.assertNotIn("HALF AN ANSWER", self._thread(app))
                release.set()
                self._pump(app, lambda: not app._pending_here())
        finally:
            release.set()
        self.assertNotIn("HALF AN ANSWER", self._thread(app))
        self.assertEqual(self._thread(app).count("The second attempt."), 1)

    def test_a_reply_that_arrives_whole_is_in_the_thread_at_once(self):
        """The desk keeps the whole reply; easing it in is the page's (frontend/tests/reveal.test.ts)."""
        app = self._app(key=False)
        app.send_chat("/help")
        app.pump()
        state = app.snapshot()
        self.assertIn("/sample-di —", state["thread"]["turns"][-1]["text"])
        self.assertIn("/sample-di —", self._thread(app))
        self.assertEqual(app.live_items(), [])

    def test_opening_a_saved_thread_sends_it_whole(self):
        from fpfa.projects import new_project, save_project

        app = self._app(key=False)
        before = app.thread_rev
        project = new_project("Saved job")
        project["chat"] = [{"role": "user", "text": "hello"}, {"role": "assistant", "text": "A saved reply."}]
        save_project(project)
        app.open_project(project["id"])
        self.assertGreater(app.thread_rev, before)
        turns = app.snapshot()["thread"]["turns"]
        self.assertEqual([turn["text"] for turn in turns], ["hello", "A saved reply."])
        self.assertIn("A saved reply.", self._thread(app))
        self.assertIn("hello", self._thread(app))

    def test_reduce_motion_setting_and_environment(self):
        from fpfa.paths import write_config
        from fpfa.desk import reduce_motion

        _isolate_data()
        self.assertFalse(reduce_motion())
        write_config({"reduce_motion": True})
        self.assertTrue(reduce_motion())
        write_config({"reduce_motion": False})
        os.environ["FPFA_REDUCE_MOTION"] = "1"
        try:
            self.assertTrue(reduce_motion())
        finally:
            os.environ.pop("FPFA_REDUCE_MOTION", None)

    def test_chips_send_what_they_say_and_the_footer_drops_the_job_heading(self):
        app = self._app()
        labels = [chip["label"] for chip in app.snapshot()["chips"]]
        self.assertEqual(labels, ["Load the sample zone", "What trips a double-interlock valve?", "Show the commands"])
        app.ask_claude.set(False)
        app._use_chip("/sample-di")
        app.pump()
        self.assertIn("Sample loaded", self._thread(app))
        labels = [chip["label"] for chip in app.snapshot()["chips"]]
        self.assertEqual(labels, ["Design basis", "Explain the screen", "Questions for the engineer"])
        app.status.set("Asking claude-opus-5-5… Job 6b34e02bf8dc | Sample data hall DI zone | chat | Give me the basis")
        self.assertEqual(app.snapshot()["status"], "Asking claude-opus-5-5…")
        app.status.set("Chat updated.")
        self.assertEqual(app.snapshot()["status"], "Chat updated.")


if __name__ == "__main__":
    unittest.main()
