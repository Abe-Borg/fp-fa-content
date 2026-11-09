"""Prompt caching on the Messages path.

The system text and the tool list are byte-identical on every round of a
turn, so AnthropicMessages.create sends the system text as one text block
with a cache breakpoint and, when the request carries tools, asks for
automatic caching on the message tail. run_tool_loop sums the usage the
API reports. Every client here is a stand-in. Nothing is sent to the API.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

FA_SPEC = "28-31-00-fire-detection-and-alarm.md"
EPHEMERAL = {"type": "ephemeral"}


class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


class _Inner:
    """Stands in for anthropic.Anthropic. Records each create() call."""

    def __init__(self, reply=None):
        self.calls: list[dict] = []
        self.message_counts: list[int] = []
        self._reply = reply or SimpleNamespace(content=[], stop_reason="end_turn")
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        self.message_counts.append(len(kwargs.get("messages") or []))
        return self._reply(len(self.calls)) if callable(self._reply) else self._reply


def _client(inner: _Inner):
    from fpfa.claude_client import AnthropicMessages

    client = AnthropicMessages("sk-ant-test-not-sent")
    client._client = inner
    return client


def _system_text(call: dict) -> str:
    system = call["system"]
    if isinstance(system, str):
        return system
    return "".join(block["text"] for block in system if block.get("type") == "text")


class WrapperCacheTests(unittest.TestCase):
    def test_string_system_becomes_one_cached_block_with_the_same_text(self):
        inner = _Inner()
        text = "Shell text ±5 °F — “quoted” — 全文"
        _client(inner).create(
            max_tokens=8,
            system=text,
            tools=[{"name": "zone_trapped_volume"}],
            messages=[{"role": "user", "content": "q"}],
        )
        call = inner.calls[0]
        self.assertEqual(call["system"], [{"type": "text", "text": text, "cache_control": EPHEMERAL}])
        self.assertEqual(call["cache_control"], EPHEMERAL)
        self.assertEqual(call["tools"], [{"name": "zone_trapped_volume"}])
        self.assertEqual(call["messages"], [{"role": "user", "content": "q"}])
        self.assertEqual(call["model"], "claude-opus-5-5")

    def test_messages_are_passed_through_without_markers_or_mutation(self):
        messages = [
            {"role": "user", "content": "q"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "t", "signature": "sig"},
                {"type": "tool_use", "id": "toolu_1", "name": "read_skill", "input": {"slug": "x"}},
            ]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "{}"}]},
        ]
        before = copy.deepcopy(messages)
        inner = _Inner()
        _client(inner).create(max_tokens=8, system="s", tools=[{"name": "read_skill"}], messages=messages)
        self.assertIs(inner.calls[0]["messages"], messages)
        self.assertEqual(messages, before)
        self.assertNotIn("cache_control", json.dumps(messages))

    def test_list_system_marks_only_its_last_text_block_and_leaves_the_caller_list_alone(self):
        system = [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]
        inner = _Inner()
        _client(inner).create(max_tokens=8, system=system, tools=[{"name": "t"}], messages=[{"role": "user", "content": "q"}])
        sent = inner.calls[0]["system"]
        self.assertEqual(sent[0], {"type": "text", "text": "a"})
        self.assertEqual(sent[1], {"type": "text", "text": "b", "cache_control": EPHEMERAL})
        self.assertEqual(system, [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}])

    def test_an_existing_breakpoint_is_kept_and_not_doubled(self):
        system = [
            {"type": "text", "text": "a", "cache_control": {"type": "ephemeral", "ttl": "1h"}},
            {"type": "text", "text": "b"},
        ]
        inner = _Inner()
        _client(inner).create(max_tokens=8, system=system, tools=[{"name": "t"}], messages=[{"role": "user", "content": "q"}])
        self.assertEqual(inner.calls[0]["system"], system)

    def test_a_call_without_tools_marks_the_system_but_asks_for_no_tail_cache(self):
        # The blind claim check is one call with no tools. There is no later
        # round to read a cached message tail, so that marker is left off.
        inner = _Inner()
        _client(inner).create(max_tokens=8, system="QA role text", messages=[{"role": "user", "content": "claims"}])
        call = inner.calls[0]
        self.assertNotIn("cache_control", call)
        self.assertEqual(call["system"], [{"type": "text", "text": "QA role text", "cache_control": EPHEMERAL}])

    def test_no_system_and_an_empty_system_pass_through(self):
        inner = _Inner()
        _client(inner).create(max_tokens=8, messages=[{"role": "user", "content": "q"}])
        self.assertNotIn("system", inner.calls[0])
        _client(inner).create(max_tokens=8, system="", messages=[{"role": "user", "content": "q"}])
        self.assertEqual(inner.calls[1]["system"], "")

    def test_sampling_fields_are_still_dropped_with_caching_on(self):
        inner = _Inner()
        _client(inner).create(
            max_tokens=8, system="s", tools=[{"name": "t"}], messages=[{"role": "user", "content": "q"}],
            temperature=0, top_p=1, top_k=4, tool_choice={"type": "auto"},
        )
        call = inner.calls[0]
        for key in ("temperature", "top_p", "top_k", "tool_choice", "thinking"):
            self.assertNotIn(key, call)
        self.assertEqual(call["cache_control"], EPHEMERAL)

    def test_the_claim_check_sends_its_role_as_a_cached_block_and_no_tools(self):
        from fpfa.claim_check import checker_system, judge

        packet = {
            "claim_count": 1,
            "claims": "1. Exported narrative (no code section) requires zone total 281.3 gal.",
            "sources": "1. PACKAGE ASSERTION (not a retrieved standard passage). Tool-plan figures: 281.3",
            "draft_token": "abc",
        }
        inner = _Inner(reply=SimpleNamespace(content=[Block(type="text", text='1. Supported. Cite: "281.3"')]))
        judge(REPO, packet, _client(inner).create)
        call = inner.calls[0]
        self.assertNotIn("tools", call)
        self.assertNotIn("cache_control", call)
        self.assertEqual(call["system"], [{"type": "text", "text": checker_system(REPO), "cache_control": EPHEMERAL}])


class TurnCacheTests(unittest.TestCase):
    """One everyday turn through the wrapper: three rounds, one system block each time."""

    def _script(self, n: int):
        rounds = [
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="toolu_skill", name="read_skill", input={"slug": "sprinkler-system-volume-takeoff"}),
            ], usage=SimpleNamespace(input_tokens=400, output_tokens=40, cache_creation_input_tokens=21000, cache_read_input_tokens=0)),
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="toolu_vol", name="zone_trapped_volume", input={"segments": [{"d_in": 1.049, "length_ft": 100}]}),
            ], usage=SimpleNamespace(input_tokens=30, output_tokens=60, cache_creation_input_tokens=5000, cache_read_input_tokens=21400)),
            SimpleNamespace(stop_reason="end_turn", content=[
                Block(type="text", text="Quoted from the tool."),
            ], usage=SimpleNamespace(input_tokens=20, output_tokens=200, cache_creation_input_tokens=300, cache_read_input_tokens=26400)),
        ]
        return rounds[n - 1]

    def test_every_round_sends_the_identical_full_system_block_and_tool_list(self):
        from fpfa.calc_tools import SCHEMAS
        from fpfa.everyday import assemble_system, run_everyday

        expected = assemble_system(REPO)
        fa = (REPO / "specs" / FA_SPEC).read_text(encoding="utf-8")
        inner = _Inner(reply=self._script)
        out = run_everyday(REPO, _client(inner).create, "How many gallons are trapped?")
        self.assertEqual(len(inner.calls), 3)
        for call in inner.calls:
            self.assertEqual(call["system"], [{"type": "text", "text": expected, "cache_control": EPHEMERAL}])
            self.assertEqual(call["cache_control"], EPHEMERAL)
            self.assertIs(call["tools"], SCHEMAS)
            self.assertIn(fa, _system_text(call))
            self.assertIn("### 3.9", _system_text(call))
        # The message list grows by an assistant turn and a tool-result turn each round.
        self.assertEqual(inner.message_counts, [1, 3, 5])
        self.assertEqual(out["text"], "Quoted from the tool.")
        self.assertEqual([call["name"] for call in out["tool_calls"]], ["read_skill", "zone_trapped_volume"])
        self.assertEqual(out["usage"], {
            "rounds": 3,
            "input_tokens": 450,
            "output_tokens": 300,
            "cache_creation_input_tokens": 26300,
            "cache_read_input_tokens": 47800,
        })

    def test_the_system_text_is_deterministic_per_mode(self):
        from fpfa.everyday import assemble_system

        self.assertEqual(assemble_system(REPO, "mixed"), assemble_system(REPO, "mixed"))
        self.assertEqual(assemble_system(REPO), assemble_system(REPO, "mixed"))
        self.assertNotEqual(assemble_system(REPO, "mixed"), assemble_system(REPO, "calculator"))


class UsageTests(unittest.TestCase):
    def test_loop_sums_usage_and_tolerates_a_missing_block(self):
        from fpfa.claude_client import run_tool_loop

        rounds = [
            SimpleNamespace(stop_reason="tool_use", content=[Block(type="tool_use", id="t1", name="noop", input={})],
                            usage=SimpleNamespace(input_tokens=1000, output_tokens=50, cache_creation_input_tokens=20000, cache_read_input_tokens=0)),
            SimpleNamespace(stop_reason="tool_use", content=[Block(type="tool_use", id="t2", name="noop", input={})],
                            usage={"input_tokens": 500, "output_tokens": 300, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 21000}),
            SimpleNamespace(stop_reason="end_turn", content=[Block(type="text", text="done")]),
        ]
        seen = []

        def create(**kwargs):
            seen.append(kwargs)
            return rounds[len(seen) - 1]

        out = run_tool_loop(create, system="s", user_text="go", tools=[{"name": "noop"}], execute=lambda _n, _a: {})
        self.assertEqual(out["usage"], {
            "rounds": 3,
            "input_tokens": 1500,
            "output_tokens": 350,
            "cache_creation_input_tokens": 20000,
            "cache_read_input_tokens": 21000,
        })

    def test_add_usage_skips_values_that_are_not_numbers(self):
        from fpfa.claude_client import add_usage, empty_usage

        totals = add_usage(empty_usage(), {"input_tokens": 5, "cache_read_input_tokens": None, "output_tokens": "x", "cache_creation_input_tokens": True})
        self.assertEqual(totals, {"rounds": 1, "input_tokens": 5, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0})
        add_usage(totals, None)
        self.assertEqual(totals["rounds"], 2)

    def test_usage_summary_wording(self):
        from fpfa.claude_client import empty_usage, usage_summary

        self.assertEqual(usage_summary(None), "")
        self.assertEqual(usage_summary({}), "")
        self.assertEqual(usage_summary(empty_usage()), "")
        self.assertEqual(
            usage_summary({"rounds": 3, "input_tokens": 1500, "output_tokens": 350,
                           "cache_creation_input_tokens": 20000, "cache_read_input_tokens": 21000}),
            "3 rounds, 42,500 input tokens (49% read from cache), 350 output tokens.",
        )
        self.assertEqual(
            usage_summary({"rounds": 1, "input_tokens": 10, "output_tokens": 2,
                           "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}),
            "1 round, 10 input tokens (0% read from cache), 2 output tokens.",
        )
        self.assertEqual(usage_summary({"rounds": 1}), "1 round, 0 input tokens, 0 output tokens.")

    def test_zone_run_and_starter_carry_the_narrator_usage(self):
        from fpfa.bess import run_bess_plan
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        usage = {"rounds": 2, "input_tokens": 100, "output_tokens": 50, "cache_creation_input_tokens": 21000, "cache_read_input_tokens": 21000}

        def narrator(_system, _user, _tools, _execute):
            return {"text": "", "tool_calls": [], "stop_reason": "end_turn", "usage": usage}

        self.assertIsNone(run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)["usage"])
        self.assertEqual(run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator)["usage"], usage)
        self.assertIsNone(run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS)["usage"])
        self.assertEqual(run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, narrator=narrator)["usage"], usage)


class StatusLineWindowTests(unittest.TestCase):
    """The status bar shows the token line after a chat reply. Needs a display."""

    def _wait_for(self, app, needle: str, timeout: float = 5.0) -> None:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.chat_view.get("1.0", "end"):
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")

    def _app(self):
        import os
        import tempfile

        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        data = Path(tempfile.mkdtemp(prefix="fpfa-cache-test-"))
        os.environ["FPFA_DATA_DIR"] = str(data)
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        import tkinter as tk

        from fpfa.keystore import save_api_key
        from fpfa.paths import write_config
        from fpfa.ui import App

        write_config({"key_backend": "file"})
        save_api_key("sk-ant-local-test")
        root = tk.Tk()
        self.addCleanup(root.destroy)
        app = App(root)
        root.update()
        return app

    def test_chat_status_line_reports_rounds_and_cache_share(self):
        from unittest.mock import patch

        app = self._app()
        seen = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[Block(type="text", text="Cached reply text")],
                    usage=SimpleNamespace(input_tokens=400, output_tokens=120,
                                          cache_creation_input_tokens=0, cache_read_input_tokens=21200),
                )

        with patch("fpfa.ui.AnthropicMessages", Fast):
            app.chat_entry.insert(0, "What limits the zone size?")
            app.send_chat()
            self._wait_for(app, "Cached reply text")
        self.assertEqual(len(seen), 1)
        status = app.status.get()
        self.assertIn("Chat updated.", status)
        self.assertIn("1 round, 21,600 input tokens (98% read from cache), 120 output tokens.", status)
        # The stand-in replaced the wrapper, so the thread text is unchanged either way.
        self.assertNotIn("read from cache", app.chat_view.get("1.0", "end"))


if __name__ == "__main__":
    unittest.main()
