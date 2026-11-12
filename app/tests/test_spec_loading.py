"""Every specs/*.md file reaches the model request in full.

The loader has no file-count cap and no character cap. A request that is too
large is reported, never trimmed or resent with parts missing. A reply the API
reports as unfinished is labeled. Stand-ins replace Messages.create. These
tests do not call the API.
"""

from __future__ import annotations

import hashlib
import inspect
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402

os.environ.setdefault("FPFA_DATA_DIR", tempfile.mkdtemp(prefix="fpfa-test-"))

FA_SPEC = "28-31-00-fire-detection-and-alarm.md"
# The caps this change removed. Fixtures go past both.
OLD_CHAR_CAP = 16000
OLD_FILE_CAP = 12



def _isolate_data() -> Path:
    path = tempfile.mkdtemp(prefix="fpfa-test-")
    os.environ["FPFA_DATA_DIR"] = path
    os.environ.pop("FPFA_CONTENT_ROOT", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return Path(path)


def _write(path: Path, text: str) -> None:
    """Exact UTF-8 bytes, so the source text is the same on Windows and Linux."""
    path.write_bytes(text.encode("utf-8"))


def _repo_specs() -> list[Path]:
    folder = REPO / "specs"
    return sorted(path for path in folder.glob("*.md") if path.name.lower() != "readme.md")


def _digests(paths: list[Path]) -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def _long_spec() -> str:
    head = "# Section 99 99 99 — Long test section\n\nSTART-MARKER §1.1 ±5 °F ≥ 0.2 µm\n"
    first = "".join(f"1.{n} Filler line {n} — “quoted” ≤ value.\n" for n in range(900))
    middle = "\nMIDDLE-MARKER §3.8 Ω résumé 中文 🔥 non-BMP\n"
    second = "".join(f"3.{n} Later line {n} — ‘single’ ≈ value.\n" for n in range(900))
    end = "\nEND-MARKER §3.9 last requirement.\n"
    trailing = "Trailing paragraph after the end marker ✓.\n\n   \n"
    return head + first + middle + second + end + trailing


class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def _status_error(status: int, message: str):
    """The SDK's own typed error for a status, as the client would raise it."""
    import anthropic

    if status == 413:
        cls = getattr(anthropic, "ContentTooLargeError", None) or anthropic.RequestTooLargeError
        kind = "request_too_large"
    else:
        cls = anthropic.BadRequestError
        kind = "invalid_request_error"
    body = {"type": "error", "error": {"type": kind, "message": message}}
    response = SimpleNamespace(status_code=status, headers={}, request=None)
    return cls(f"Error code: {status} - {body}", response=response, body=body)


class _Inner:
    """Stand-in for anthropic.Anthropic. Records every request it is sent."""

    def __init__(self, reply=None, error: BaseException | None = None):
        self.calls: list[dict] = []
        self._reply = reply
        self._error = error
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._reply(len(self.calls)) if callable(self._reply) else self._reply

    def stream(self, **kwargs):
        """The window's chat turn streams. The stand-in answers a stream as it answers create().

        The SDK sends the request when the stream is entered, so that is where
        the call is recorded and a scripted error is raised.
        """
        inner = self

        class _Stream:
            def __enter__(self):
                self.reply = inner.create(**kwargs)
                return self

            def __exit__(self, *_exc):
                return False

            def __iter__(self):
                return iter(())

            def get_final_message(self):
                return self.reply

        return _Stream()


def _no_sleep():
    """Stands in for the time module inside claude_client only. A retry would call sleep."""
    from unittest.mock import Mock

    return SimpleNamespace(sleep=Mock())


def _client(inner: _Inner):
    from fpfa.claude_client import AnthropicMessages

    client = AnthropicMessages("sk-ant-test-not-sent")
    client._client = inner
    return client


def _system_text(call: dict) -> str:
    """The system text the wrapper sent. It goes out as one cached text block."""
    system = call["system"]
    if isinstance(system, str):
        return system
    return "".join(block["text"] for block in system if block.get("type") == "text")


class SpecNotesFullTextTests(unittest.TestCase):
    def test_loader_takes_no_cap_parameters(self):
        from fpfa.skills_loader import spec_notes

        self.assertEqual(list(inspect.signature(spec_notes).parameters), ["content_root"])
        with self.assertRaises(TypeError):
            spec_notes(REPO, chars=100)
        with self.assertRaises(TypeError):
            spec_notes(REPO, limit=1)

    def test_more_than_twelve_files_all_return_in_order_with_exact_text(self):
        from fpfa.skills_loader import spec_notes

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "specs"
            folder.mkdir()
            expected = {}
            # Written in reverse so the result order comes from the sort.
            for n in range(OLD_FILE_CAP + 8, 0, -1):
                name = f"{n:02d}-00-00-section-{n}.md"
                text = f"# Section {n:02d} 00 00\n\nBody {n} only. ±{n} °F — “{name}”.\n" + "z" * n
                expected[name] = text
                _write(folder / name, text)
            _write(folder / "README.md", "folder guide, not a spec\n")
            notes = spec_notes(root)
        self.assertEqual(len(notes), OLD_FILE_CAP + 8)
        self.assertGreater(len(notes), OLD_FILE_CAP)
        self.assertEqual([note["name"] for note in notes], sorted(expected))
        for note in notes:
            self.assertEqual(set(note), {"name", "text"})
            self.assertEqual(note["text"], expected[note["name"]])

    def test_long_spec_keeps_middle_end_unicode_and_trailing_text(self):
        from fpfa.skills_loader import spec_notes

        text = _long_spec()
        self.assertGreater(len(text), OLD_CHAR_CAP * 4)
        self.assertGreater(text.index("MIDDLE-MARKER"), OLD_CHAR_CAP)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "specs"
            folder.mkdir()
            _write(folder / "99-99-99-long.md", text)
            _write(folder / "21-05-00-short.md", "Short section.\n")
            source = (folder / "99-99-99-long.md").read_bytes()
            notes = spec_notes(root)
        self.assertEqual([note["name"] for note in notes], ["21-05-00-short.md", "99-99-99-long.md"])
        self.assertEqual(notes[0]["text"], "Short section.\n")
        loaded = notes[1]["text"]
        self.assertEqual(loaded, text)
        self.assertEqual(loaded.encode("utf-8"), source)
        for marker in (
            "START-MARKER §1.1 ±5 °F ≥ 0.2 µm",
            "MIDDLE-MARKER §3.8 Ω résumé 中文 🔥 non-BMP",
            "3.899 Later line 899 — ‘single’ ≈ value.",
            "END-MARKER §3.9 last requirement.",
            "Trailing paragraph after the end marker ✓.",
        ):
            self.assertIn(marker, loaded)
        self.assertTrue(loaded.endswith("✓.\n\n   \n"))

    def test_readme_is_excluded_in_any_letter_case(self):
        from fpfa.skills_loader import spec_notes

        # One folder per spelling: a Windows folder cannot hold two of them.
        for readme in ("README.md", "readme.md", "ReadMe.md", "Readme.md"):
            with self.subTest(readme=readme), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp) / "specs"
                folder.mkdir()
                _write(folder / readme, "folder guide, not a spec\n")
                _write(folder / "21-13-19-di.md", "Section 21 13 19.\n")
                _write(folder / "readme-draft.md", "A spec whose name starts with readme.\n")
                self.assertEqual(
                    spec_notes(Path(tmp)),
                    [
                        {"name": "21-13-19-di.md", "text": "Section 21 13 19.\n"},
                        {"name": "readme-draft.md", "text": "A spec whose name starts with readme.\n"},
                    ],
                )

    def test_missing_or_empty_folder_returns_an_empty_list(self):
        from fpfa.everyday import assemble_system
        from fpfa.skills_loader import spec_notes

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / "roles", root / "roles")
            shutil.copytree(REPO / "modes", root / "modes")
            self.assertEqual(spec_notes(root), [])
            self.assertNotIn("Spec notes from the content pack", assemble_system(root))
            folder = root / "specs"
            folder.mkdir()
            self.assertEqual(spec_notes(root), [])
            _write(folder / "README.md", "folder guide\n")
            _write(folder / "notes.txt", "not markdown\n")
            self.assertEqual(spec_notes(root), [])
            self.assertNotIn("Spec notes from the content pack", assemble_system(root))

    def test_current_specs_load_exactly(self):
        from fpfa.skills_loader import spec_notes

        paths = _repo_specs()
        notes = spec_notes(REPO)
        self.assertEqual([note["name"] for note in notes], [path.name for path in paths])
        for path, note in zip(paths, notes):
            self.assertEqual(note["text"], path.read_text(encoding="utf-8"))
        fa = next(note["text"] for note in notes if note["name"] == FA_SPEC)
        # The old character cap cut this file. The test means nothing if it shrinks below it.
        self.assertGreater(len(fa), OLD_CHAR_CAP)


class FullSpecRequestTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        self.fa = (REPO / "specs" / FA_SPEC).read_text(encoding="utf-8")

    def assert_every_spec_in_full(self, system: str) -> None:
        position = -1
        for path in _repo_specs():
            block = f"## {path.name}\n{path.read_text(encoding='utf-8')}"
            self.assertIn(block, system, path.name)
            self.assertGreater(system.index(block), position, f"{path.name} is out of order")
            position = system.index(block)

    def test_assembled_prompt_carries_the_current_fa_spec_in_full(self):
        from fpfa.everyday import assemble_system
        from fpfa.workflow import system_prompt

        self.assertGreater(len(self.fa), OLD_CHAR_CAP)
        sections = (
            "### 3.8 Telecom suite, duct editions, and 2021 energy storage",
            "### 3.9 Integrated-test frequency, signal schedule, and microphone instructions",
        )
        ending = "No foam. No clean agent. No single-interlock release.\n"
        for needle in sections:
            self.assertGreater(self.fa.index(needle), OLD_CHAR_CAP)
        self.assertTrue(self.fa.endswith(ending))
        # Chat uses assemble_system. The zone and starter paths use system_prompt.
        for system in (assemble_system(REPO), system_prompt(REPO, "synthesis")):
            self.assertIn(f"## {FA_SPEC}\n{self.fa}", system)
            self.assertIn(self.fa[OLD_CHAR_CAP:], system)
            for needle in sections:
                self.assertIn(needle, system)
            self.assertIn(self.fa[-1500:], system)
            self.assert_every_spec_in_full(system)

    def test_model_request_receives_every_spec_in_full_on_every_round(self):
        from fpfa.everyday import assemble_system, run_everyday

        def reply(call: int):
            if call == 1:
                return SimpleNamespace(stop_reason="tool_use", content=[
                    Block(type="tool_use", id="toolu_role", name="read_role", input={"slug": "fa-releasing"}),
                ])
            return SimpleNamespace(stop_reason="end_turn", content=[
                Block(type="text", text="Section 3.9 is in the request."),
            ])

        inner = _Inner(reply=reply)
        out = run_everyday(REPO, _client(inner).create, "What does 3.9 say about the microphone?")
        self.assertEqual(out["text"], "Section 3.9 is in the request.")
        self.assertEqual(len(inner.calls), 2)
        expected = assemble_system(REPO)
        for call in inner.calls:
            # Exactly what the SDK client was handed, round after round.
            # The wrapper sends the text as one cached block. The text itself is unchanged.
            self.assertEqual(_system_text(call), expected)
            self.assertEqual(call["system"], [{"type": "text", "text": expected, "cache_control": {"type": "ephemeral"}}])
            self.assertIn(self.fa, _system_text(call))
            self.assert_every_spec_in_full(_system_text(call))
            # The output setting is separate from spec loading. It is the owner's ceiling for every request.
            self.assertEqual(call["max_tokens"], 64000)

    def test_request_too_large_is_reported_and_never_resent_shorter(self):
        from fpfa.claude_client import RequestTooLarge, safe_error
        from fpfa.everyday import run_everyday

        cases = (
            _status_error(413, "Request exceeds the maximum allowed number of bytes."),
            _status_error(400, "prompt is too long: 1204512 tokens > 1000000 maximum"),
        )
        before = _digests(_repo_specs())
        for error in cases:
            with self.subTest(status=error.status_code):
                inner = _Inner(error=error)
                clock = _no_sleep()
                with patch("fpfa.claude_client.time", clock):
                    with self.assertRaises(RequestTooLarge) as caught:
                        run_everyday(REPO, _client(inner).create, "Summarize 28 31 00.")
                self.assertEqual(len(inner.calls), 1)
                clock.sleep.assert_not_called()
                self.assertIn(self.fa, _system_text(inner.calls[0]))
                self.assertIs(caught.exception.__cause__, error)
                shown = safe_error(caught.exception)
                self.assertTrue(shown.startswith(
                    "RequestTooLarge: Claude rejected the request as too large"
                ))
                self.assertIn("did not trim the request or resend it with parts missing", shown)
                self.assertIn("API response:", shown)
                self.assertIn(str(error.status_code), shown)
        self.assertEqual(_digests(_repo_specs()), before)

    def test_other_bad_request_is_not_relabeled_or_retried(self):
        from fpfa.claude_client import RequestTooLarge

        error = _status_error(400, 'messages: roles must alternate between "user" and "assistant"')
        inner = _Inner(error=error)
        clock = _no_sleep()
        with patch("fpfa.claude_client.time", clock):
            with self.assertRaises(type(error)) as caught:
                _client(inner).create(max_tokens=8, messages=[])
        clock.sleep.assert_not_called()
        self.assertNotIsInstance(caught.exception, RequestTooLarge)
        self.assertEqual(len(inner.calls), 1)


class IncompleteReplyTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()

    def _turn(self, stop_reason: str, text: str = "Partial answer about 3.8") -> dict:
        from fpfa.everyday import run_everyday

        def create(**_kwargs):
            return SimpleNamespace(stop_reason=stop_reason, content=[Block(type="text", text=text)])

        return run_everyday(REPO, create, "question")

    def test_provider_reported_incomplete_reply_is_labeled(self):
        from fpfa.everyday import everyday_reply

        for reason in ("max_tokens", "model_context_window_exceeded", "refusal", "pause_turn"):
            with self.subTest(stop_reason=reason):
                out = self._turn(reason)
                self.assertEqual(out["stop_reason"], reason)
                reply = everyday_reply(out)
                self.assertTrue(reply.startswith("Incomplete reply."))
                self.assertIn(f"stop_reason {reason}", reply)
                self.assertIn("not a complete answer", reply)
                self.assertTrue(reply.endswith("\n\nPartial answer about 3.8"))
        self.assertIn("output limit", everyday_reply(self._turn("max_tokens")))

    def test_finished_reply_is_not_labeled(self):
        from fpfa.everyday import everyday_reply

        self.assertEqual(everyday_reply(self._turn("end_turn", "Done.")), "Done.")
        self.assertEqual(everyday_reply({"text": "Done.", "stop_reason": ""}), "Done.")
        self.assertEqual(everyday_reply({"text": "", "stop_reason": "end_turn"}), "(Claude returned no text.)")

    def test_tool_round_limit_is_labeled_and_still_enforced(self):
        from fpfa.everyday import everyday_reply, run_everyday

        def create(**_kwargs):
            return SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="text", text="Reading the role first."),
                Block(type="tool_use", id="toolu_role", name="read_role", input={"slug": "fp-sprinkler"}),
            ])

        out = run_everyday(REPO, create, "question", max_rounds=2)
        self.assertEqual(len(out["tool_calls"]), 2)
        self.assertEqual(out["stop_reason"], "tool_use")
        reply = everyday_reply(out)
        self.assertTrue(reply.startswith("Incomplete reply."))
        self.assertIn("ran out of tool rounds", reply)

    def test_zone_and_starter_warn_on_any_incomplete_stop_reason(self):
        from fpfa.bess import run_bess_plan
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        def narrator_for(reason: str):
            def narrator(_system, _user, _tools, _execute):
                return {"text": "", "tool_calls": [], "stop_reason": reason}

            return narrator

        plain_zone = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS)
        zone = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator_for("refusal"))
        unfinished = [item for item in zone["warnings"] if item.startswith("Incomplete reply.")]
        self.assertEqual(len(unfinished), 1)
        self.assertIn("stop_reason refusal", unfinished[0])
        self.assertTrue(unfinished[0].endswith("Tables stay on the tool plan."))
        # Warnings are flags, and flags go to the Results tab and the export.
        self.assertIn(unfinished[0], zone["flags"])
        self.assertEqual(zone["tools"], plain_zone["tools"])
        self.assertEqual(zone["source"], "tool-plan")

        plain_bess = run_bess_plan(REPO, EXAMPLE_BESS, EXAMPLE_BESS_BASIS)
        bess = run_bess_plan(
            REPO,
            EXAMPLE_BESS,
            EXAMPLE_BESS_BASIS,
            narrator=narrator_for("model_context_window_exceeded"),
        )
        unfinished = [item for item in bess["warnings"] if item.startswith("Incomplete reply.")]
        self.assertEqual(len(unfinished), 1)
        self.assertIn("context window", unfinished[0])
        self.assertTrue(unfinished[0].endswith("The starter stays on the tool plan."))
        self.assertEqual(bess["tools"], plain_bess["tools"])

        finished = run_di_zone(REPO, EXAMPLE_DI, EXAMPLE_BASIS, narrator=narrator_for("end_turn"))
        self.assertFalse(any(item.startswith("Incomplete reply.") for item in finished["warnings"]))


class ChatWindowTests(unittest.TestCase):
    """The window shows the label and the size error. Needs a display."""

    def _wait_for(self, app, needle: str, timeout: float = 5.0) -> None:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.thread_text():
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")

    def _app(self):
        _isolate_data()

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")
        root = Loop()
        self.addCleanup(root.destroy)
        app = root.open_desk()
        root.update()
        return app

    def test_incomplete_chat_reply_is_labeled_in_the_thread(self):
        from fpfa.projects import load_project

        app = self._app()
        seen = []

        class Cut:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="max_tokens",
                    content=[SimpleNamespace(type="text", text="Partial answer about the microphone")],
                )

        with patch("fpfa.desk.AnthropicMessages", Cut):
            app.send_chat("What does 3.9 say about the microphone?")
            self._wait_for(app, "Partial answer about the microphone")
        thread = app.thread_text()
        self.assertIn("Incomplete reply.", thread)
        self.assertIn("stop_reason max_tokens", thread)
        self.assertLess(thread.index("Incomplete reply."), thread.index("Partial answer about"))
        self.assertEqual(len(seen), 1)
        self.assertIn((REPO / "specs" / FA_SPEC).read_text(encoding="utf-8"), seen[0]["system"])
        saved = load_project(app.project["id"])
        self.assertIn("Incomplete reply.", saved["chat"][-1]["text"])

    def test_request_too_large_shows_a_clear_error_and_keeps_the_question(self):
        from fpfa.claude_client import AnthropicMessages
        from fpfa.projects import load_project

        app = self._app()
        inner = _Inner(error=_status_error(413, "Request exceeds the maximum allowed number of bytes."))

        class TooLarge(AnthropicMessages):
            def __init__(self, key):
                super().__init__(key)
                self._client = inner

        clock = _no_sleep()
        with patch("fpfa.desk.AnthropicMessages", TooLarge), patch("fpfa.claude_client.time", clock):
            app.send_chat("Summarize 28 31 00 in full.")
            self._wait_for(app, "Claude rejected the request as too large")
        clock.sleep.assert_not_called()
        self.assertEqual(len(inner.calls), 1)
        self.assertIn((REPO / "specs" / FA_SPEC).read_text(encoding="utf-8"), _system_text(inner.calls[0]))
        thread = app.thread_text()
        self.assertIn("did not trim the request or resend it with parts missing", thread)
        self.assertEqual([job.status for job in app.jobs.snapshot()], ["error"])
        saved = load_project(app.project["id"])
        self.assertEqual(saved["chat"][0]["role"], "user")
        self.assertIn("Summarize 28 31 00 in full.", saved["chat"][0]["text"])


if __name__ == "__main__":
    unittest.main()
