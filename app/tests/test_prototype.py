"""App tests. Calc math stays in calcs/; this checks the workflow, export, and guards."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("FPFA_DATA_DIR", tempfile.mkdtemp(prefix="fpfa-test-"))


def _isolate_data():
    path = tempfile.mkdtemp(prefix="fpfa-test-")
    os.environ["FPFA_DATA_DIR"] = path
    os.environ.pop("FPFA_CONTENT_ROOT", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return Path(path)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import fmt1, run_di_zone

        self.root = content_root()
        self.basis = dict(EXAMPLE_BASIS)
        self.di = EXAMPLE_DI
        self.run = run_di_zone
        self.fmt1 = fmt1

    def test_sample_zone_tool_plan(self):
        result = self.run(self.root, self.di, self.basis)
        tools = result["tools"]
        volume = tools["zone_trapped_volume"]["zone_gal"]
        trip = tools["di_trip_to_water"]
        self.assertLess(volume, 500)
        self.assertGreater(volume, 200)
        self.assertTrue(tools["dry_delivery_screen"]["nfpa_delivery_time_exempt"])
        self.assertEqual(tools["dry_delivery_screen"]["nfpa_size_cap_gal"], 500)
        self.assertFalse(trip["passes_screen"])
        self.assertGreater(trip["t_total_s"], 30)
        self.assertEqual(tools["elect_di_trim"]["family"], "El/El")
        self.assertEqual(tools["elect_di_trim"]["status"], "provisional")
        self.assertEqual(tools["nitrogen_gate"]["design_c"], 100)
        self.assertEqual(tools["releasing_truth_table"]["solenoid_true_count"], 6)
        self.assertEqual(result["source"], "tool-plan")
        self.assertIn(self.fmt1(volume), result["narrative"])
        self.assertIn(self.fmt1(trip["t_total_s"]), result["narrative"])
        self.assertIn("not a listed water-delivery-time calculation", result["narrative"])
        self.assertIn("5.0 gal trim ASSUMED", result["narrative"])
        self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", result["narrative"])
        self.assertTrue(any("ASSUMED from time basis FM" in flag for flag in result["flags"]))
        self.assertTrue(result["narrative_checks"]["quotes_volume"])
        self.assertTrue(result["narrative_checks"]["quotes_time"])

    def test_claude_request_carries_the_tool_plan_figures(self):
        from fpfa.workflow import form_assumption_lines

        seen = {}

        def grab(system, user, _tools, _execute):
            seen["system"] = system
            seen["user"] = user
            return {"text": "", "tool_calls": [], "stop_reason": "max_tokens"}

        result = self.run(self.root, self.di, self.basis, narrator=grab)
        volume = self.fmt1(result["tools"]["zone_trapped_volume"]["zone_gal"])
        total = self.fmt1(result["tools"]["di_trip_to_water"]["t_total_s"])
        self.assertIn(volume, seen["user"])
        self.assertIn(total, seen["user"])
        self.assertIn("5.0 gal trim ASSUMED", seen["user"])
        self.assertIn("tool_plan_inputs", seen["user"])
        self.assertIn("ASSUMED", seen["system"])
        self.assertTrue(any("output limit" in item for item in result["warnings"]))
        blank = "\n".join(form_assumption_lines("", "FM", self.root))
        self.assertIn("Trim: ASSUMED 5 gal", blank)
        self.assertIn("30.0 s ASSUMED from time basis FM", blank)
        entered = "\n".join(form_assumption_lines("10", "NFPA-OH", self.root))
        self.assertIn("10 gal entered on the form. Not assumed.", entered)
        self.assertIn("50.0 s ASSUMED from time basis NFPA-OH", entered)
        self.assertNotIn("Trim: ASSUMED", entered)

    def test_advertised_tool_inputs_replay_the_governing_plan(self):
        from fpfa.calc_tools import ToolSession

        seen = {}

        def grab(_system, user, _tools, _execute):
            seen["user"] = user
            return {"text": "", "tool_calls": []}

        result = self.run(self.root, self.di, self.basis, narrator=grab)
        payload = json.loads(seen["user"].split("\n\n", 1)[1])
        advertised = payload["tool_plan_inputs"]
        recorded = {
            call["name"]: call["input"]
            for call in result["transcript"]
            if call.get("by") == "tool-plan"
        }
        self.assertEqual(advertised, recorded)
        for name in ("dry_delivery_screen", "di_trip_to_water"):
            self.assertEqual(advertised[name]["t_detect_s"], 8)
            self.assertEqual(advertised[name]["t_release_s"], 2)
            self.assertEqual(advertised[name]["t_exhaust_s"], 0)
        trim_in = advertised["elect_di_trim"]
        self.assertFalse(trim_in["failsafe_on_total_power_loss"])
        self.assertEqual(trim_in["supervisory_psi"], 15.0)
        self.assertEqual(trim_in["medium"], "nitrogen")

        session = ToolSession(self.root)
        replayed = session.execute("di_trip_to_water", advertised["di_trip_to_water"])
        governing = result["tools"]["di_trip_to_water"]
        self.assertAlmostEqual(replayed["t_total_s"], governing["t_total_s"])
        self.assertFalse(replayed["passes_screen"])
        self.assertGreater(replayed["t_total_s"], 30)
        self.assertEqual(self.fmt1(replayed["t_total_s"]), "38.1")

        failsafe = dict(self.di)
        failsafe["failsafe_on_total_power_loss"] = True
        held = self.run(self.root, failsafe, self.basis)
        held_trim = next(
            call["input"] for call in held["transcript"] if call["name"] == "elect_di_trim"
        )
        self.assertTrue(held_trim["failsafe_on_total_power_loss"])
        replay_trim = session.execute("elect_di_trim", held_trim)
        self.assertEqual(replay_trim["family"], "named-failsafe")
        self.assertEqual(held["tools"]["elect_di_trim"]["family"], "named-failsafe")

    def test_model_text_is_kept_only_when_it_quotes_the_tool_plan(self):
        first = self.run(self.root, self.di, self.basis)
        volume = self.fmt1(first["tools"]["zone_trapped_volume"]["zone_gal"])
        total = self.fmt1(first["tools"]["di_trip_to_water"]["t_total_s"])

        def good(_system, _user, _tools, _execute):
            return {"text": f"The zone is {volume} gal and t_total is {total} s.", "tool_calls": []}

        kept = self.run(self.root, self.di, self.basis, narrator=good)
        self.assertEqual(kept["source"], "claude")
        self.assertIn(volume, kept["narrative"])
        self.assertEqual(kept["tools"]["zone_trapped_volume"]["zone_gal"], first["tools"]["zone_trapped_volume"]["zone_gal"])

        def bad(_system, _user, _tools, _execute):
            return {"text": "I estimate about 40 gallons and 12 seconds.", "tool_calls": []}

        rejected = self.run(self.root, self.di, self.basis, narrator=bad)
        self.assertEqual(rejected["source"], "tool-plan")
        self.assertIn(volume, rejected["narrative"])
        self.assertTrue(any("tool-plan" in item for item in rejected["warnings"]))

        def boom(_system, _user, _tools, _execute):
            raise RuntimeError("network down sk-ant-secretvalue")

        failed = self.run(self.root, self.di, self.basis, narrator=boom)
        self.assertEqual(failed["source"], "tool-plan")
        self.assertIn(volume, failed["narrative"])
        self.assertNotIn("sk-ant-secretvalue", " ".join(failed["warnings"]))

    def test_docx_uses_tool_numbers(self):
        from docx import Document

        from fpfa.spec_docx import write_docx

        result = self.run(self.root, self.di, self.basis)
        volume = self.fmt1(result["tools"]["zone_trapped_volume"]["zone_gal"])
        total = self.fmt1(result["tools"]["di_trip_to_water"]["t_total_s"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "section.docx"
            write_docx(path, {"name": "Sample data hall DI zone", "basis": self.basis}, result)
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
            for table in doc.tables:
                for row in table.rows:
                    text += "\n" + " | ".join(cell.text for cell in row.cells)
        self.assertIn("Section 21 13 19", text)
        self.assertEqual(doc.core_properties.title, "Section 21 13 19 — Double-interlock preaction (draft)")
        self.assertNotIn("21 13 " + "16", text)
        self.assertIn("5.0 gal trim ASSUMED", text)
        self.assertIn("30.0 ASSUMED", text)
        self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", text)
        self.assertIn("not a listed water-delivery-time calculation", text)
        self.assertIn(volume, text)
        self.assertIn(total, text)
        self.assertIn("El/El", text)
        self.assertIn("Design Hazen-Williams C is 100", text)
        self.assertNotIn("sk-ant-", text)

    def test_docx_uses_the_basis_stored_on_the_run(self):
        from docx import Document

        from fpfa.spec_docx import write_docx

        result = self.run(self.root, self.di, self.basis)
        result["basis"] = {
            "ahj": "Authority on the run",
            "nfpa_13": "2025",
            "nfpa_72": "2025",
            "insurer": "FM",
            "hazard_notes": "Notes from the run.",
        }
        project = {
            "name": "Sample data hall DI zone",
            "basis": {
                "ahj": "Authority edited later",
                "nfpa_13": "2019",
                "nfpa_72": "2019",
                "insurer": "Later insurer",
                "hazard_notes": "Notes edited after the run.",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "section.docx"
            write_docx(path, project, result)
            doc = Document(path)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        self.assertIn("Authority on the run", text)
        self.assertIn("Insurer: FM", text)
        self.assertIn("Notes from the run.", text)
        self.assertNotIn("Authority edited later", text)
        self.assertNotIn("Later insurer", text)
        self.assertNotIn("Notes edited after the run.", text)

    def test_nfpa_exemption_uses_zone_total_not_pipe_only(self):
        import math

        from docx import Document

        from fpfa.sample_data import EXAMPLE_DI
        from fpfa.spec_docx import write_docx

        diameter = 6.065
        gallons_per_foot = math.pi / 4.0 * diameter * diameter / 144.0 * 7.48
        di = dict(EXAMPLE_DI)
        di["segments"] = [{"role": "main", "d_in": diameter, "length_ft": 495.0 / gallons_per_foot}]
        di["trim_gal"] = 10
        di["fittings_percent"] = 0
        di["qod"] = True
        result = self.run(self.root, di, self.basis)
        volume = result["tools"]["zone_trapped_volume"]
        screen = result["tools"]["dry_delivery_screen"]
        self.assertAlmostEqual(volume["pipe_gal"], 495, delta=0.05)
        self.assertAlmostEqual(volume["zone_gal"], 505, delta=0.05)
        self.assertTrue(screen["pipe_only_nfpa_delivery_time_exempt"])
        self.assertFalse(screen["nfpa_delivery_time_exempt"])
        self.assertEqual(screen["nfpa_size_cap_gal"], 500)
        self.assertIn("cap: no", result["narrative"])
        self.assertIn("not assumed", result["narrative"])
        self.assertNotIn("trim ASSUMED", result["narrative"])
        self.assertIn("ASSUMED from time basis", result["narrative"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "section.docx"
            write_docx(path, {"name": "Exemption check", "basis": self.basis}, result)
            doc = Document(path)
            rows = [[cell.text for cell in row.cells] for row in doc.tables[1].rows]
        pipe_row = next(row for row in rows if row[0] == "Pipe only")
        zone_row = next(row for row in rows if row[0] == "Zone total")
        self.assertEqual(pipe_row[-1], "—")
        self.assertEqual(zone_row[-1], "No")
        self.assertIn("ASSUMED", pipe_row[3])
        self.assertIn("ASSUMED", zone_row[3])
        body = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        self.assertIn("not assumed", body)
        self.assertNotIn("trim ASSUMED", body)


class ChatRequestTests(unittest.TestCase):
    def test_slash_commands_and_sample_di_aliases(self):
        from fpfa.spec_docx import DRAFT_SECTION
        from fpfa.ui import chat_run_summary, parse_slash_command, slash_help_text, unknown_slash_text

        self.assertEqual(parse_slash_command("/sample-di"), ("sample-di", ""))
        self.assertEqual(parse_slash_command("  /SAMPLE_DI  "), ("sample-di", ""))
        self.assertEqual(parse_slash_command("/sampledi"), ("sample-di", ""))
        self.assertEqual(parse_slash_command("/run now"), ("run", "now"))
        self.assertEqual(parse_slash_command("/new Hall zone"), ("new", "Hall zone"))
        self.assertEqual(parse_slash_command("/help"), ("help", ""))
        self.assertIsNone(parse_slash_command("explain the trim"))
        self.assertIsNone(parse_slash_command(""))
        self.assertIsNone(parse_slash_command("/"))
        help_text = slash_help_text()
        self.assertIn("/sample-di", help_text)
        self.assertIn(DRAFT_SECTION, help_text)
        self.assertIn("ASSUMED", help_text)
        self.assertIn("Ctrl+S", help_text)
        self.assertIn("not a command", unknown_slash_text("inbox"))
        summary = chat_run_summary({
            "narrative": "Zone total is 281.3 gal.",
            "tools": {
                "zone_trapped_volume": {"trim_gal": 5, "trim_assumed": True},
                "di_trip_to_water": {"limit_s": 30, "t_total_s": 38.1, "limit_basis": "FM"},
            },
        })
        self.assertIn("Zone total is 281.3 gal.", summary)
        self.assertIn("5.0 gal trim ASSUMED", summary)
        self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", summary)
        self.assertIn("t_total 38.1 s is calculated.", summary)
        self.assertIn(DRAFT_SECTION, summary)
        self.assertNotIn("21 13 " + "16", summary)

    def test_follow_up_includes_prior_turns(self):
        from fpfa.ui import format_chat_request

        text = format_chat_request(
            [
                {"role": "user", "text": "Which trim family?"},
                {"role": "assistant", "text": "El/El holds the prime with the solenoid."},
            ],
            {"insurer": "FM"},
            {"zone_id": "DH-1"},
            "explain that recommendation",
        )
        self.assertIn("Which trim family?", text)
        self.assertIn("El/El holds the prime with the solenoid.", text)
        self.assertIn("explain that recommendation", text)
        self.assertIn("Earlier turns:", text)


class ClaudeLoopTests(unittest.TestCase):
    def test_loop_nudges_and_does_not_force_tools(self):
        from fpfa.claude_client import run_tool_loop

        class Block:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

            def model_dump(self, exclude_none=True):
                return {key: value for key, value in self.__dict__.items() if value is not None}

        script = [
            SimpleNamespace(content=[
                Block(type="thinking", thinking="check the tool", signature="sig-keep"),
                Block(type="text", text="I will guess the volume."),
            ]),
            SimpleNamespace(content=[
                Block(type="tool_use", id="toolu_1", name="zone_trapped_volume", input={"segments": [{"d_in": 1, "length_ft": 1}]}),
            ]),
            SimpleNamespace(content=[
                Block(type="text", text="Quoted from the tool."),
            ]),
        ]
        seen = []

        def create(**kwargs):
            self.assertNotIn("tool_choice", kwargs)
            self.assertNotIn("temperature", kwargs)
            seen.append(kwargs)
            return script[len(seen) - 1]

        def execute(name, arguments):
            self.assertEqual(name, "zone_trapped_volume")
            return {"zone_gal": 12.5}

        out = run_tool_loop(
            create,
            system="sys",
            user_text="go",
            tools=[{"name": "zone_trapped_volume"}],
            execute=execute,
            required=["zone_trapped_volume"],
        )
        self.assertEqual(len(seen), 3)
        self.assertEqual(out["nudges"], 1)
        self.assertEqual(out["tool_calls"][0]["output"]["zone_gal"], 12.5)
        assistant = seen[1]["messages"][1]["content"]
        self.assertEqual(assistant[0]["signature"], "sig-keep")
        self.assertIn("zone_trapped_volume", seen[1]["messages"][2]["content"])

    def test_wrapper_rejects_forced_tool_choice_and_sampling_params(self):
        from fpfa.claude_client import AnthropicMessages

        client = AnthropicMessages("sk-ant-test-not-sent")

        class Messages:
            def __init__(self):
                self.kwargs = None

            def create(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(content=[])

        class Inner:
            def __init__(self):
                self.messages = Messages()

        client._client = Inner()
        with self.assertRaises(ValueError):
            client.create(max_tokens=8, messages=[], tool_choice={"type": "any"})
        with self.assertRaises(ValueError):
            client.create(max_tokens=8, messages=[], thinking={"type": "disabled"})
        client.create(max_tokens=8, messages=[], temperature=0, top_p=1, top_k=5, tool_choice={"type": "auto"})
        self.assertNotIn("temperature", client._client.messages.kwargs)
        self.assertNotIn("top_p", client._client.messages.kwargs)
        self.assertNotIn("top_k", client._client.messages.kwargs)
        self.assertNotIn("tool_choice", client._client.messages.kwargs)
        self.assertNotIn("thinking", client._client.messages.kwargs)

    def test_wrapper_retries_a_transient_overload(self):
        from unittest.mock import patch

        from fpfa.claude_client import AnthropicMessages

        client = AnthropicMessages("sk-ant-test-not-sent")

        class Overloaded(Exception):
            status_code = 529

        class Messages:
            def __init__(self):
                self.calls = 0
                self.kwargs = None

            def create(self, **kwargs):
                self.calls += 1
                self.kwargs = kwargs
                if self.calls == 1:
                    raise Overloaded("overloaded")
                return SimpleNamespace(content=[])

        class Inner:
            def __init__(self):
                self.messages = Messages()

        client._client = Inner()
        with patch("fpfa.claude_client.time.sleep"):
            client.create(max_tokens=8, messages=[])
        self.assertEqual(client._client.messages.calls, 2)

    def test_truncated_tool_call_is_not_executed(self):
        from fpfa.claude_client import run_tool_loop

        class Block:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

            def model_dump(self, exclude_none=True):
                return {key: value for key, value in self.__dict__.items() if value is not None}

        def create(**_kwargs):
            return SimpleNamespace(
                stop_reason="max_tokens",
                content=[Block(type="tool_use", id="toolu_cut", name="zone_trapped_volume", input={})],
            )

        def execute(_name, _arguments):
            raise AssertionError("a truncated tool call must not run")

        out = run_tool_loop(
            create,
            system="sys",
            user_text="go",
            tools=[],
            execute=execute,
            required=["zone_trapped_volume"],
            max_rounds=4,
        )
        self.assertEqual(out["tool_calls"], [])
        self.assertEqual(out["stop_reason"], "max_tokens")
        self.assertEqual(out["nudges"], 0)


class KeyAndSkillTests(unittest.TestCase):
    def test_key_file_fallback_never_touches_a_hanging_keyring(self):
        data = _isolate_data()
        import fpfa.keystore as keystore

        def boom(*_args, **_kwargs):
            raise subprocess.TimeoutExpired(cmd="keyring", timeout=1)

        keystore._keyring_call = boom
        where = keystore.save_api_key("sk-ant-local-test")
        self.assertEqual(where, "file")
        self.assertEqual(keystore.load_api_key(), "sk-ant-local-test")
        mode = (data / "anthropic-api-key").stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)
        from fpfa.projects import new_project

        project = new_project("Key isolation")
        blob = (data / "projects" / f"{project['id']}.json").read_text(encoding="utf-8")
        self.assertNotIn("sk-ant-local-test", blob)
        self.assertIn("user-only file", keystore.key_status())
        keystore.clear_api_key()
        self.assertEqual(keystore.load_api_key(), "")
        self.assertIn("Credential Manager", keystore.key_storage_help())
        self.assertIn("pywin32", keystore.key_storage_help())
        self.assertIn("FPFA_USE_KEYRING=1", keystore.key_storage_help())

    def test_windows_status_names_credential_manager_or_the_file(self):
        from unittest.mock import patch

        _isolate_data()
        import fpfa.keystore as keystore

        calls = []

        def fake(action, secret=None, timeout=2.0):
            calls.append(action)
            if action == "set":
                fake.saved = secret
                return "ok"
            if action == "get":
                return getattr(fake, "saved", "")
            return "ok"

        keystore._keyring_call = fake
        os.environ["FPFA_USE_KEYRING"] = "0"
        try:
            with patch.object(keystore.sys, "platform", "win32"):
                self.assertEqual(keystore.save_api_key("sk-ant-local-test"), "file")
                text = keystore.key_status()
            self.assertNotIn("set", calls)
            self.assertIn("user-only file", text)
            self.assertIn("Credential Manager", text)
            self.assertIn("pywin32", text)
        finally:
            os.environ.pop("FPFA_USE_KEYRING", None)
            keystore.clear_api_key()

        os.environ["FPFA_USE_KEYRING"] = "1"
        try:
            self.assertEqual(keystore.save_api_key("sk-ant-local-test"), "keyring")
            with patch.object(keystore.sys, "platform", "win32"):
                windows = keystore.key_status()
            with patch.object(keystore.sys, "platform", "linux"):
                other = keystore.key_status()
            self.assertIn("Windows Credential Manager", windows)
            self.assertIn("system keyring", other)
        finally:
            os.environ.pop("FPFA_USE_KEYRING", None)
            keystore.clear_api_key()

    def test_skills_come_from_the_pack(self):
        from fpfa.paths import content_root
        from fpfa.skills_loader import list_skills, read_skill

        root = content_root()
        slugs = [item["slug"] for item in list_skills(root)]
        self.assertIn("sprinkler-system-volume-takeoff", slugs)
        self.assertGreaterEqual(len(slugs), 8)
        text = read_skill(root, "preaction-el-el-trim-election")
        self.assertIn("El/El", text)
        with self.assertRaises(ValueError):
            read_skill(root, "../calcs/fp/formulas.py")

    def test_pack_has_no_roster_or_client_names(self):
        banned = re.compile(
            r"\bAbe\b|DC FP Lead|stay dark|Hyperion|Abraham|\bNovva\b|NEEDS PE REVIEW|/workspace/"
        )
        hits = []
        for folder in (REPO / "skills", REPO / "calcs", REPO / "roles", REPO / "modes"):
            for path in folder.rglob("*"):
                if path.suffix.lower() not in {".py", ".md"} or "__pycache__" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                if banned.search(text):
                    hits.append(str(path.relative_to(REPO)))
        self.assertEqual(hits, [])

    def test_di_draft_does_not_use_the_dry_pipe_section_number(self):
        banned = "21 13 " + "16"
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(banned, readme)
        self.assertIn("21 13 19", readme)
        for path in (REPO / "app" / "fpfa").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(banned, text, path.name)
            if path.name == "spec_docx.py":
                self.assertIn("21 13 19", text)
        for folder in (REPO / "roles", REPO / "modes"):
            for path in folder.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(banned, text, path.name)

    def test_spec_builders_keep_double_interlock_on_21_13_19(self):
        import importlib.util

        from fpfa.skills_loader import spec_notes

        folder = REPO / "specs"
        files = sorted(
            path for path in folder.glob("*.md") if path.name.lower() != "readme.md"
        )
        names = [path.name for path in files]
        self.assertEqual(
            names,
            [
                "21-05-00-common-work.md",
                "21-11-00-fire-service-mains.md",
                "21-12-00-standpipes.md",
                "21-13-13-wet-pipe.md",
                "21-13-16-dry-pipe.md",
                "21-13-19-double-interlock-preaction.md",
                "21-30-00-fire-pumps.md",
                "28-31-00-fire-detection-and-alarm.md",
            ],
        )
        notes = spec_notes(REPO)
        self.assertEqual([note["name"] for note in notes], names)
        for note in notes:
            self.assertLessEqual(len(note["text"]), 4000)
            self.assertEqual(
                len(note["text"]),
                len((folder / note["name"]).read_text(encoding="utf-8")),
            )

        di = (folder / "21-13-19-double-interlock-preaction.md").read_text(encoding="utf-8")
        dry = (folder / "21-13-16-dry-pipe.md").read_text(encoding="utf-8")
        self.assertIn("CSI 21 13 19", di)
        self.assertIn("Do not write double-interlock requirements into Section 21 13 16.", di)
        self.assertIn("CSI 21 13 16", dry)
        self.assertIn("Section 21 13 19", dry)
        self.assertNotIn("Single- or double-interlock", di)

        mislabel = re.compile(
            r"(?i)(double-interlock|preaction).{0,80}21 13 16"
            r"|21 13 16.{0,80}(double-interlock|preaction)"
        )
        fence = re.compile(r"(?i)\b(not|dry pipe|dry-pipe)\b")
        for path in folder.glob("*.md"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if mislabel.search(line):
                    self.assertRegex(line, fence, f"{path.name}:{number}")

        roster = re.compile(
            r"\bAbe\b|DC FP Lead|stay dark|Hyperion|Abraham|\bNovva\b|NEEDS PE REVIEW|/workspace/"
            r"|Canada|Canadian|\bCSA\b|NFPA 2001"
        )
        authored = re.compile(r"(?i)provide (a |an )?(foam|clean agent|water mist|deluge)")
        scan_path = REPO / "calcs" / "fp" / "place_name_scan.py"
        spec = importlib.util.spec_from_file_location("place_name_scan", scan_path)
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        places = scanner.banned_pattern()
        hits = []
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if roster.search(text) or places.search(text) or authored.search(text):
                hits.append(path.name)
            self.assertNotIn("_sources", text)
            lowered = path.name.lower()
            self.assertNotIn("foam", lowered)
            self.assertNotIn("clean", lowered)
            self.assertNotIn("canada", lowered)
        self.assertEqual(hits, [])


class EverydayPathTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root

        self.root = content_root()

    def test_roles_load_like_skills(self):
        from fpfa.roles_loader import list_roles, read_role

        slugs = [item["slug"] for item in list_roles(self.root)]
        self.assertEqual(slugs, ["everyday", "fa-releasing", "fp-sprinkler", "spec-draft"])
        text = read_role(self.root, "fp-sprinkler")
        self.assertIn("Pipe-only volume is not the exemption volume.", text)
        self.assertIn("ASSUMED", text)
        with self.assertRaises(ValueError):
            read_role(self.root, "../skills/occupancy-hazard-fork/SKILL.md")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "roles" / "fp-sprinkler"
            folder.mkdir(parents=True)
            (folder / "ROLE.md").write_text(
                "---\nname: FP\ndescription: sprinkler specialist\n---\n\nBODY-MARKER\n",
                encoding="utf-8",
            )
            (root / "roles" / "README.md").write_text("guide, not a role\n", encoding="utf-8")
            found = list_roles(root)
            self.assertEqual([item["slug"] for item in found], ["fp-sprinkler"])
            self.assertEqual(found[0]["description"], "sprinkler specialist")
            self.assertIn("BODY-MARKER", read_role(root, "fp-sprinkler"))

    def test_system_prompt_points_at_role_files(self):
        from fpfa.everyday import assemble_system
        from fpfa.workflow import system_prompt

        marker = "Call list_roles and read_role before you answer as that specialist."
        body_only = "Pipe-only volume is not the exemption volume."
        releasing = "Do not invent a releasing row the truth-table tool did not return."
        everyday = (REPO / "roles" / "everyday" / "ROLE.md").read_text(encoding="utf-8")
        self.assertIn(marker, everyday)
        system = system_prompt(self.root)
        self.assertEqual(system, assemble_system(self.root))
        self.assertIn(marker, system)
        self.assertIn("ASSUMED", system)
        self.assertIn("- fp-sprinkler:", system)
        self.assertIn("- fa-releasing:", system)
        self.assertIn("- spec-draft:", system)
        self.assertIn("sprinkler-system-volume-takeoff", system)
        self.assertNotIn(body_only, system)
        self.assertNotIn(releasing, system)
        mode_rule = "Call list_modes and read_mode before you apply a different mode."
        mixed_body = "This mode may explore an option, quote a calc tool, and draft in the same reply."
        calculator_body = "This mode answers with tool figures."
        self.assertIn(mode_rule, everyday)
        self.assertIn(mode_rule, system)
        self.assertIn(mixed_body, system)
        self.assertIn("- calculator:", system)
        self.assertNotIn(calculator_body, system)
        self.assertIn("use best judgment", system)
        for path in (REPO / "app" / "fpfa").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(marker, text, path.name)
            self.assertNotIn(mode_rule, text, path.name)
            self.assertNotIn(body_only, text, path.name)
            self.assertNotIn(releasing, text, path.name)
            self.assertNotIn(mixed_body, text, path.name)
            self.assertNotIn(calculator_body, text, path.name)
        self.assertNotIn("SYSTEM_PROMPT", (REPO / "app" / "fpfa" / "claude_client.py").read_text(encoding="utf-8"))

    def test_changed_role_file_is_what_the_prompt_uses(self):
        from fpfa.everyday import assemble_system
        from fpfa.roles_loader import read_role

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            everyday = root / "roles" / "everyday"
            everyday.mkdir(parents=True)
            (everyday / "ROLE.md").write_text(
                "---\nname: Everyday\ndescription: shell\n---\n\nSHELL-SENTENCE about ASSUMED trim.\n",
                encoding="utf-8",
            )
            specialist = root / "roles" / "fp-sprinkler"
            specialist.mkdir()
            (specialist / "ROLE.md").write_text(
                "---\nname: FP\ndescription: sprinkler specialist for wet dry and DI\n---\n\n"
                "SPECIALIST-BODY-NOT-INLINED\n",
                encoding="utf-8",
            )
            mixed = root / "modes" / "mixed"
            mixed.mkdir(parents=True)
            (mixed / "MODE.md").write_text(
                "---\nname: Mixed\ndescription: everyday mix\n---\n\nMODE-SENTENCE from the pack.\n",
                encoding="utf-8",
            )
            brainstorm = root / "modes" / "brainstorm"
            brainstorm.mkdir()
            (brainstorm / "MODE.md").write_text(
                "---\nname: Brainstorm\ndescription: explore options\n---\n\n"
                "BRAINSTORM-BODY-NOT-INLINED\n",
                encoding="utf-8",
            )
            (root / "modes" / "README.md").write_text("guide, not a mode\n", encoding="utf-8")
            system = assemble_system(root)
            self.assertIn("SHELL-SENTENCE about ASSUMED trim.", system)
            self.assertIn("MODE-SENTENCE from the pack.", system)
            self.assertIn("fp-sprinkler", system)
            self.assertIn("sprinkler specialist for wet dry and DI", system)
            self.assertIn("- brainstorm:", system)
            self.assertIn("explore options", system)
            self.assertNotIn("SPECIALIST-BODY-NOT-INLINED", system)
            self.assertNotIn("BRAINSTORM-BODY-NOT-INLINED", system)
            self.assertIn("SPECIALIST-BODY-NOT-INLINED", read_role(root, "fp-sprinkler"))
            (root / "roles" / "everyday" / "ROLE.md").unlink()
            with self.assertRaises(FileNotFoundError):
                assemble_system(root)

    def test_everyday_loop_calls_calcs_and_read_role(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.claude_client import MODEL_ID
        from fpfa.everyday import run_everyday

        class Block:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

            def model_dump(self, exclude_none=True):
                return {key: value for key, value in self.__dict__.items() if value is not None}

        args = {"segments": [{"d_in": 1.049, "length_ft": 10}]}
        direct = ToolSession(self.root).execute("zone_trapped_volume", args)
        script = [
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="toolu_role", name="read_role", input={"slug": "fp-sprinkler"}),
            ]),
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="toolu_vol", name="zone_trapped_volume", input=args),
            ]),
            SimpleNamespace(stop_reason="end_turn", content=[
                Block(type="text", text=f"Zone total is {direct['zone_gal']:.1f} gal from the tool."),
            ]),
        ]
        seen = []

        def create(**kwargs):
            seen.append(kwargs)
            return script[len(seen) - 1]

        out = run_everyday(self.root, create, "What is the trapped volume of one 10 ft branch?")
        self.assertEqual(seen[0]["model"], MODEL_ID)
        self.assertNotIn("tool_choice", seen[0])
        self.assertNotIn("temperature", seen[0])
        self.assertNotIn("top_p", seen[0])
        self.assertNotIn("top_k", seen[0])
        self.assertNotIn("thinking", seen[0])
        self.assertEqual([call["name"] for call in out["tool_calls"]], ["read_role", "zone_trapped_volume"])
        self.assertIn("Pipe-only volume is not the exemption volume.", out["tool_calls"][0]["output"]["text"])
        self.assertEqual(out["tool_calls"][1]["output"]["zone_gal"], direct["zone_gal"])
        self.assertTrue(out["tool_calls"][1]["output"]["trim_assumed"])
        self.assertEqual(out["tool_calls"][1]["output"]["trim_gal"], 5.0)
        self.assertIn("optimistic screen", (REPO / "roles" / "fp-sprinkler" / "ROLE.md").read_text(encoding="utf-8"))
        self.assertIn("21 13 19", (REPO / "roles" / "spec-draft" / "ROLE.md").read_text(encoding="utf-8"))

    def test_tool_plan_still_governs_and_chat_repeats_it(self):
        from unittest.mock import patch

        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.ui import chat_request_text
        from fpfa.workflow import govern_note, run_di_zone

        result = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS)
        note = govern_note(result)
        self.assertIn("281.3", note)
        self.assertIn("38.1", note)
        self.assertIn("5.0 gal trim ASSUMED", note)
        self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", note)
        self.assertIn("when a narrative disagrees", note)
        self.assertIn("not a listed water-delivery-time calculation", note)
        request = chat_request_text(
            [{"role": "user", "text": "Which trim family?"}, {"role": "assistant", "text": "El/El."}],
            {"insurer": "FM"},
            {"zone_id": "DH-1"},
            "revise the volume",
            result,
        )
        self.assertIn("Earlier turns:", request)
        self.assertIn("Which trim family?", request)
        self.assertIn("Governing zone total text: 281.3.", request)
        self.assertNotIn("Governing", chat_request_text([], {}, {}, "hello"))
        self.assertFalse(any("missing roles" in item for item in result["warnings"]))
        seen = {}

        def grab(system, user, _tools, _execute):
            seen["system"] = system
            seen["user"] = user
            return {"text": "", "tool_calls": []}

        run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS, narrator=grab)
        self.assertIn("roles_to_read", seen["user"])
        self.assertIn("fp-sprinkler", seen["user"])
        self.assertIn("spec-draft", seen["user"])
        payload = json.loads(seen["user"].split("\n\n", 1)[1])
        self.assertEqual(payload["roles_to_read"], ["fp-sprinkler", "fa-releasing", "spec-draft"])
        with patch("fpfa.workflow.list_roles", return_value=[]):
            flagged = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS)
        self.assertTrue(any("missing roles" in item for item in flagged["warnings"]))
        self.assertEqual(flagged["source"], "tool-plan")
        self.assertIn("281.3", flagged["narrative"])


class ModeBehaviorTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root

        self.root = content_root()

    def test_modes_load_like_roles(self):
        from fpfa.modes_loader import list_modes, read_mode

        slugs = [item["slug"] for item in list_modes(self.root)]
        self.assertEqual(slugs, ["brainstorm", "calculator", "mixed", "synthesis"])
        text = read_mode(self.root, "Calculator")
        self.assertIn("This mode answers with tool figures.", text)
        self.assertIn("use best judgment", text)
        self.assertIn("ASSUMED", text)
        with self.assertRaises(ValueError):
            read_mode(self.root, "../roles/everyday/ROLE.md")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "modes" / "calculator"
            folder.mkdir(parents=True)
            (folder / "MODE.md").write_text(
                "---\nname: Calculator\ndescription: quote the tools\n---\n\nBODY-MARKER\n",
                encoding="utf-8",
            )
            (root / "modes" / "README.md").write_text("guide, not a mode\n", encoding="utf-8")
            found = list_modes(root)
            self.assertEqual([item["slug"] for item in found], ["calculator"])
            self.assertEqual(found[0]["description"], "quote the tools")
            self.assertIn("BODY-MARKER", read_mode(root, "calculator"))

    def test_active_mode_file_is_what_the_prompt_uses(self):
        from fpfa.everyday import assemble_system, run_everyday
        from fpfa.modes_loader import read_mode

        calculator = assemble_system(self.root, "calculator")
        brainstorm = assemble_system(self.root, "brainstorm")
        self.assertIn("This mode answers with tool figures.", calculator)
        self.assertNotIn("This mode explores options.", calculator)
        self.assertIn("This mode explores options.", brainstorm)
        self.assertNotIn("This mode answers with tool figures.", brainstorm)
        self.assertIn("- mixed:", calculator)
        self.assertEqual(calculator, assemble_system(self.root, "CALCULATOR"))
        self.assertIn(read_mode(self.root, "synthesis"), assemble_system(self.root, "synthesis"))
        for path in (REPO / "app" / "fpfa").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("This mode explores options.", text, path.name)
            self.assertNotIn("This mode writes the draft narrative after a zone tool plan.", text, path.name)

    def test_everyday_loop_can_read_a_mode(self):
        from fpfa.claude_client import MODEL_ID
        from fpfa.everyday import run_everyday

        class Block:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

            def model_dump(self, exclude_none=True):
                return {key: value for key, value in self.__dict__.items() if value is not None}

        script = [
            SimpleNamespace(stop_reason="tool_use", content=[
                Block(type="tool_use", id="toolu_mode", name="read_mode", input={"slug": "brainstorm"}),
            ]),
            SimpleNamespace(stop_reason="end_turn", content=[
                Block(type="text", text="Two options. The open point is use best judgment."),
            ]),
        ]
        seen = []

        def create(**kwargs):
            seen.append(kwargs)
            return script[len(seen) - 1]

        out = run_everyday(self.root, create, "Talk through the trim choice.", mode="brainstorm")
        self.assertEqual(seen[0]["model"], MODEL_ID)
        self.assertNotIn("tool_choice", seen[0])
        self.assertNotIn("temperature", seen[0])
        self.assertNotIn("top_p", seen[0])
        self.assertNotIn("top_k", seen[0])
        self.assertNotIn("thinking", seen[0])
        self.assertIn("This mode explores options.", seen[0]["system"])
        self.assertNotIn("This mode answers with tool figures.", seen[0]["system"])
        names = [tool["name"] for tool in seen[0]["tools"]]
        self.assertIn("read_mode", names)
        self.assertIn("read_role", names)
        self.assertIn("zone_trapped_volume", names)
        self.assertEqual(out["tool_calls"][0]["name"], "read_mode")
        self.assertIn("This mode explores options.", out["tool_calls"][0]["output"]["text"])

    def test_labels_stay_distinct(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.ui import chat_request_text, describe_modes
        from fpfa.workflow import (
            form_assumption_lines,
            judgment_label_line,
            label_glossary,
            run_di_zone,
            trim_assumption_text,
        )

        glossary = label_glossary()
        judgment = judgment_label_line()
        self.assertIn("calculated", glossary)
        self.assertIn("ASSUMED", glossary)
        self.assertIn("use best judgment", glossary)
        self.assertIn("use best judgment", judgment)
        self.assertNotIn("ASSUMED", judgment)
        blank = trim_assumption_text({"trim_gal": 5, "trim_assumed": True})
        typed = trim_assumption_text({"trim_gal": 10, "trim_assumed": False})
        self.assertIn("ASSUMED", blank)
        self.assertNotIn("use best judgment", blank)
        self.assertIn("not assumed", typed)
        self.assertNotIn("ASSUMED", typed)
        self.assertNotIn("use best judgment", typed)
        lines = form_assumption_lines("12", "FM", self.root)
        joined = "\n".join(lines)
        self.assertIn("12 gal entered on the form. Not assumed.", joined)
        self.assertIn("30.0 s ASSUMED from time basis FM", joined)
        self.assertIn(judgment, joined)
        screen = next(line for line in lines if line.startswith("Screen limit"))
        trim = next(line for line in lines if line.startswith("Trim:"))
        self.assertNotIn("use best judgment", screen)
        self.assertNotIn("use best judgment", trim)
        result = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS, mode="calculator")
        self.assertEqual(result["mode"], "calculator")
        self.assertIn("gal of pipe (calculated)", result["narrative"])
        self.assertIn("t_total 38.1 s is calculated.", result["narrative"])
        self.assertIn("5.0 gal trim ASSUMED", result["narrative"])
        self.assertIn("use best judgment", result["narrative"])
        self.assertIn(judgment, result["flags"])
        self.assertFalse(any("missing modes" in item for item in result["warnings"]))
        request = chat_request_text([], {"insurer": "FM"}, {"zone_id": "DH-1"}, "hello", result, "synthesis")
        self.assertIn("Active mode: synthesis.", request)
        self.assertIn("Governing zone total text: 281.3.", request)
        self.assertIn(judgment, request)
        described = describe_modes(self.root, "mixed")
        self.assertIn("Active mode: mixed.", described)
        self.assertIn("brainstorm", described)
        self.assertIn("(active)", described)
        self.assertNotIn("This mode may explore an option", described)

    def test_missing_mode_does_not_replace_the_tool_plan(self):
        from unittest.mock import patch

        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        with patch("fpfa.workflow.list_modes", return_value=[]):
            result = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS, mode="calculator")
        self.assertEqual(result["source"], "tool-plan")
        self.assertIn("281.3", result["narrative"])
        self.assertTrue(any("missing modes" in item for item in result["warnings"]))


class UiSmokeTests(unittest.TestCase):
    def test_demo_run_and_export(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            app.load_demo()
            root.update()
            self.assertEqual(len(app.pipes.get_children()), 4)
            narrative = app.results.get("1.0", "end")
            self.assertIn("Zone total is", narrative)
            self.assertIn("5.0 gal trim ASSUMED", narrative)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", narrative)
            self.assertIn("not a listed water-delivery-time calculation", narrative)
            self.assertIn("Trim: ASSUMED 5 gal", app.assumption_text.get())
            self.assertIn("30.0 s ASSUMED", app.assumption_text.get())
            self.assertIsNotNone(app.project["last_run"])
            with tempfile.TemporaryDirectory() as tmp:
                written = app.export_to(Path(tmp) / "draft.docx")
                self.assertTrue(written.is_file())
                self.assertGreater(written.stat().st_size, 1000)
        finally:
            root.destroy()

    def test_async_results_stay_on_the_project_that_started_them(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.projects import load_project, new_project, save_project
        from fpfa.ui import App

        result = {
            "source": "tool-plan",
            "narrative": "ORIGIN-RESULT",
            "warnings": [],
            "flags": [],
            "tools": {
                "zone_trapped_volume": {"zone_gal": 505.0},
                "di_trip_to_water": {"t_total_s": 40.0, "passes_screen": False},
                "elect_di_trim": {"family": "El/El"},
            },
        }
        root = tk.Tk()
        try:
            app = App(root)
            origin = new_project("Origin job")
            other = new_project("Other job")
            app.open_project(other["id"])
            app._finish_run(origin["id"], result, None)
            self.assertEqual(load_project(origin["id"])["last_run"]["narrative"], "ORIGIN-RESULT")
            self.assertIsNone(load_project(other["id"]).get("last_run"))
            self.assertNotIn("ORIGIN-RESULT", app.results.get("1.0", "end"))

            app.open_project(origin["id"])
            app.chat_log = [{"role": "user", "text": "Which trim family?"}]
            app._write_form(app.project)
            save_project(app.project)
            app.open_project(other["id"])
            app.chat_log = [{"role": "user", "text": "unrelated"}]
            app._render_chat()
            app._finish_chat(origin["id"], "El/El holds the prime with the solenoid.")
            saved = load_project(origin["id"])["chat"]
            self.assertEqual(saved[0]["text"], "Which trim family?")
            self.assertEqual(saved[-1]["text"], "El/El holds the prime with the solenoid.")
            self.assertEqual(app.chat_log[-1]["text"], "unrelated")
            self.assertNotIn("solenoid", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

    def test_poll_continues_after_a_callback_raises(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.projects import new_project
        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            for after_id in list(root.tk.call("after", "info")):
                root.after_cancel(after_id)
            seen = []

            def bad():
                seen.append("bad")
                raise ValueError("density must be a number")

            def good():
                seen.append("good")

            app.queue.put(bad)
            app.queue.put(good)
            app._poll()
            self.assertEqual(seen, ["bad", "good"])
            self.assertIn("ValueError", app.status.get())
            self.assertTrue(root.tk.call("after", "info"))

            origin = new_project("Poll job")
            app.open_project(origin["id"])
            app.density.set("-")
            result = {
                "source": "tool-plan",
                "narrative": "KEPT",
                "warnings": [],
                "flags": [],
                "basis": {"ahj": "Kept AHJ", "insurer": "FM", "nfpa_13": "2025", "nfpa_72": "2025"},
                "tools": {
                    "zone_trapped_volume": {"zone_gal": 10.0},
                    "di_trip_to_water": {"t_total_s": 12.0, "passes_screen": True},
                    "elect_di_trim": {"family": "El/El"},
                },
            }
            for after_id in list(root.tk.call("after", "info")):
                root.after_cancel(after_id)
            seen.clear()
            app.queue.put(lambda: app._finish_run(origin["id"], result, None))
            app.queue.put(lambda: seen.append("after-run"))
            app._poll()
            self.assertEqual(seen, ["after-run"])
            self.assertTrue(root.tk.call("after", "info"))
            self.assertEqual(app.project["last_run"]["narrative"], "KEPT")
            self.assertIn("KEPT", app.results.get("1.0", "end"))
        finally:
            root.destroy()

    def _button_labels(self, root) -> list[str]:
        labels = []

        def walk(widget):
            for child in widget.winfo_children():
                if child.winfo_class() in ("TButton", "Button"):
                    labels.append(str(child.cget("text")))
                walk(child)

        walk(root)
        return labels

    def test_chat_is_the_primary_pane(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.spec_docx import DRAFT_SECTION
        from fpfa.ui import THREAD_HINT, App

        root = tk.Tk()
        try:
            app = App(root)
            root.update_idletasks()
            root.update()
            app._prefer_chat()
            root.update_idletasks()
            root.update()
            self.assertGreater(app.chat_view.winfo_height(), app.tabs.winfo_height())
            self.assertIn("/sample-di", app.chat_view.get("1.0", "end"))
            self.assertIn(THREAD_HINT.splitlines()[0], app.chat_view.get("1.0", "end"))
            labels = self._button_labels(root)
            self.assertIn("Settings", labels)
            self.assertIn(f"Export {DRAFT_SECTION}", labels)
            self.assertIn("Sample DI", labels)
            self.assertEqual(app.mode_slug.get(), "mixed")
            self.assertIn("calculator", app.mode_box["values"])
            self.assertIn("brainstorm", app.mode_box["values"])
            self.assertIn("synthesis", app.mode_box["values"])
            self.assertNotIn("Run DI zone", labels)
            self.assertNotIn("Sample DI job", labels)
            self.assertEqual(app.chat_entry.focus_get(), app.chat_entry)
        finally:
            root.destroy()

    def test_mode_menu_is_saved_and_shapes_the_request(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import load_project, new_project, save_project
        from fpfa.ui import App

        save_api_key("sk-ant-local-test")
        seen = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="Calculator quote only.")],
                )

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.chat_entry.insert(0, "/mode calculator")
            app.send_chat()
            self.assertEqual(app.mode_slug.get(), "calculator")
            self.assertIn("Active mode: calculator.", app.chat_view.get("1.0", "end"))
            self.assertNotIn("This mode answers with tool figures.", app.chat_view.get("1.0", "end"))
            self.assertEqual(app.project["mode"], "calculator")
            self.assertEqual(load_project(app.project["id"])["mode"], "calculator")
            other = new_project("Other mode job")
            other["mode"] = "brainstorm"
            save_project(other)
            app.open_project(other["id"])
            self.assertEqual(app.mode_slug.get(), "brainstorm")
            app.open_project(load_project(app.project["id"])["id"])
            with patch("fpfa.ui.AnthropicMessages", Fast):
                app.mode_slug.set("synthesis")
                app.chat_entry.insert(0, "draft the zone")
                app.send_chat()
                self._wait_for(app, "Calculator quote only.")
            self.assertIn("Active mode: synthesis.", seen[0]["messages"][0]["content"])
            self.assertIn(
                "This mode writes the draft narrative after a zone tool plan.",
                seen[0]["system"],
            )
            self.assertNotIn("This mode explores options.", seen[0]["system"])
            self.assertEqual(app.project["mode"], "synthesis")
        finally:
            root.destroy()

    def test_mode_persists_when_optional_form_number_is_invalid(self):
        """A bad optional-form number must not discard a mode change or the chat."""
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk
        from unittest.mock import patch

        from fpfa.projects import load_project, new_project, save_project
        from fpfa.ui import App

        def select_project(app, project_id: str) -> None:
            app.refresh_projects()
            index = app._ids.index(project_id)
            app.project_list.selection_clear(0, "end")
            app.project_list.selection_set(index)
            app.project_list.event_generate("<<ListboxSelect>>")

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            job = new_project("Mode job")
            job["mode"] = "mixed"
            job["chat"] = [{"role": "user", "text": "keep this thread"}]
            save_project(job)
            other = new_project("Other mode job")
            other["mode"] = "mixed"
            save_project(other)
            app.open_project(job["id"])
            app.density.set("not-a-number")

            app.chat_entry.insert(0, "/mode calculator")
            app.send_chat()
            chat = app.chat_view.get("1.0", "end")
            self.assertEqual(app.mode_slug.get(), "calculator")
            self.assertIn("Active mode: calculator.", chat)
            self.assertIn("keep this thread", chat)
            self.assertIn("/mode calculator", chat)
            saved = load_project(job["id"])
            self.assertEqual(saved["mode"], "calculator")
            saved_text = [turn.get("text") for turn in saved["chat"]]
            self.assertIn("keep this thread", saved_text)
            self.assertIn("/mode calculator", saved_text)
            self.assertNotIn("not-a-number", json.dumps(saved.get("di")))

            select_project(app, other["id"])
            self.assertEqual(app.project["id"], other["id"])
            self.assertEqual(app.mode_slug.get(), "mixed")
            select_project(app, job["id"])
            self.assertEqual(app.mode_slug.get(), "calculator")
            self.assertEqual(load_project(job["id"])["mode"], "calculator")
            self.assertIn("keep this thread", app.chat_view.get("1.0", "end"))

            app.density.set("not-a-number")
            app.mode_slug.set("synthesis")
            with patch("fpfa.ui.messagebox.showerror") as shown:
                app.save_current()
            self.assertTrue(shown.called)
            saved = load_project(job["id"])
            self.assertEqual(saved["mode"], "synthesis")
            self.assertIn("keep this thread", [turn.get("text") for turn in saved["chat"]])
            self.assertNotIn("not-a-number", json.dumps(saved.get("di")))

            app.hose.set("bad-gpm")
            app.mode_slug.set("brainstorm")
            select_project(app, other["id"])
            self.assertEqual(app.project["id"], other["id"])
            self.assertEqual(load_project(job["id"])["mode"], "brainstorm")
            select_project(app, job["id"])
            self.assertEqual(app.mode_slug.get(), "brainstorm")
            reopened = load_project(job["id"])
            self.assertEqual(reopened["mode"], "brainstorm")
            self.assertIn("keep this thread", [turn.get("text") for turn in reopened["chat"]])
            self.assertIn("/mode calculator", [turn.get("text") for turn in reopened["chat"]])
            self.assertIn("keep this thread", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

    def test_sample_di_slash_loads_and_runs_the_zone(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.spec_docx import DRAFT_SECTION
        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.chat_entry.insert(0, "/sample-di")
            app.send_chat()
            chat = app.chat_view.get("1.0", "end")
            results = app.results.get("1.0", "end")
            self.assertEqual(len(app.pipes.get_children()), 4)
            self.assertIn("/sample-di", chat)
            self.assertIn("5.0 gal trim ASSUMED", chat)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", chat)
            self.assertIn(DRAFT_SECTION, chat)
            self.assertIn("5.0 gal trim ASSUMED", results)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", results)
            self.assertIn("not a listed water-delivery-time calculation", results)
            self.assertIn("Trim: ASSUMED 5 gal", app.assumption_text.get())
            self.assertIn("30.0 s ASSUMED", app.assumption_text.get())
            self.assertEqual(app.project["last_run"]["source"], "tool-plan")
            self.assertEqual(app.chat_log[0]["role"], "user")
            self.assertEqual(app.chat_log[0]["text"], "/sample-di")
            self.assertEqual(app.chat_log[1]["role"], "assistant")
        finally:
            root.destroy()

    def test_sample_di_chip_runs_the_same_path(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.sample_di_button.invoke()
            chat = app.chat_view.get("1.0", "end")
            self.assertIn("/sample-di", chat)
            self.assertIn("5.0 gal trim ASSUMED", chat)
            self.assertEqual(len(app.pipes.get_children()), 4)
            self.assertIsNotNone(app.project["last_run"])
            self.assertIn("Zone total is", app.results.get("1.0", "end"))
        finally:
            root.destroy()

    def test_chat_does_not_require_a_filled_zone_form(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.chat_entry.insert(0, "hello")
            app.send_chat()
            chat = app.chat_view.get("1.0", "end")
            self.assertIn("hello", chat)
            self.assertIn("API key", chat)
            self.assertIn("/sample-di", chat)
            self.assertEqual(app.pipes.get_children(), ())
            self.assertIsNone(app.project.get("last_run"))
            app.chat_entry.insert(0, "/help")
            app.send_chat()
            self.assertIn("/sample-di —", app.chat_view.get("1.0", "end"))
            app.chat_entry.insert(0, "/not-a-tool")
            app.send_chat()
            self.assertIn("/not-a-tool is not a command", app.chat_view.get("1.0", "end"))
            app.chat_entry.insert(0, "/run")
            app.send_chat()
            self.assertIn("Add at least one pipe segment.", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

    def test_ask_claude_returns_before_the_reply(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import threading
        import time
        import tkinter as tk
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.ui import App

        save_api_key("sk-ant-local-test")
        started = threading.Event()
        release = threading.Event()

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **_kwargs):
                started.set()
                release.wait(3)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="threaded reply")],
                )

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.chat_entry.insert(0, "Which trim family?")
            with patch("fpfa.ui.AnthropicMessages", Blocking):
                app.send_chat()
                self.assertTrue(started.wait(2))
                self.assertNotIn("threaded reply", app.chat_view.get("1.0", "end"))
                self.assertIn("Asking", app.status.get())
                app.chat_entry.insert(0, "still typing")
                self.assertEqual(app.chat_entry.get(), "still typing")
                app.chat_entry.delete(0, "end")
                release.set()
                deadline = time.time() + 2
                while time.time() < deadline:
                    app._poll()
                    if "threaded reply" in app.chat_view.get("1.0", "end"):
                        break
                    time.sleep(0.02)
                self.assertIn("threaded reply", app.chat_view.get("1.0", "end"))
                self.assertIn("Which trim family?", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

    def test_follow_up_send_includes_earlier_turns(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.ui import App

        save_api_key("sk-ant-local-test")
        seen = []
        seen_meta = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs["messages"][0]["content"])
                seen_meta.append(kwargs)
                text = "El/El holds the prime." if len(seen) == 1 else "That follows the first answer."
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text=text)],
                )

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            with patch("fpfa.ui.AnthropicMessages", Fast):
                app.chat_entry.insert(0, "Which trim family?")
                app.send_chat()
                self._wait_for(app, "El/El holds the prime.")
                app.chat_entry.insert(0, "explain that recommendation")
                app.send_chat()
                self._wait_for(app, "That follows the first answer.")
            self.assertGreaterEqual(len(seen), 2)
            self.assertIn("Which trim family?", seen[1])
            self.assertIn("El/El holds the prime.", seen[1])
            self.assertIn("explain that recommendation", seen[1])
            self.assertIn("Earlier turns:", seen[1])
            marker = "Call list_roles and read_role before you answer as that specialist."
            self.assertIn(marker, seen_meta[0]["system"])
            self.assertEqual(seen_meta[0]["model"], "claude-opus-5-5")
            self.assertNotIn("tool_choice", seen_meta[0])
            self.assertNotIn("temperature", seen_meta[0])
            self.assertNotIn("top_p", seen_meta[0])
            self.assertNotIn("top_k", seen_meta[0])
            self.assertNotIn("thinking", seen_meta[0])
            names = [tool["name"] for tool in seen_meta[0]["tools"]]
            for name in (
                "read_role",
                "read_skill",
                "read_mode",
                "list_modes",
                "zone_trapped_volume",
                "dry_delivery_screen",
                "di_trip_to_water",
                "elect_di_trim",
                "releasing_truth_table",
            ):
                self.assertIn(name, names)
            self.assertIn("Active mode: mixed.", seen[0])
            self.assertIn("This mode may explore an option, quote a calc tool, and draft in the same reply.", seen_meta[0]["system"])
        finally:
            root.destroy()

    def test_implicit_project_keeps_the_optional_form(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.projects import load_project
        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.zone_id.set("KEEP-1")
            app.ahj.set("Kept AHJ")
            app._insert_segment({
                "role": "branch",
                "nps": "1",
                "schedule": "sch40",
                "length_ft": 10,
                "d_in": 1.049,
            })
            app.chat_entry.insert(0, "/run")
            app.send_chat()
            chat = app.chat_view.get("1.0", "end")
            self.assertEqual(app.zone_id.get(), "KEEP-1")
            self.assertEqual(app.ahj.get(), "Kept AHJ")
            self.assertEqual(len(app.pipes.get_children()), 1)
            self.assertNotIn("Add at least one pipe segment.", chat)
            self.assertEqual(app.project["di"]["zone_id"], "KEEP-1")
            self.assertEqual(app.project["basis"]["ahj"], "Kept AHJ")
            self.assertEqual(len(app.project["di"]["segments"]), 1)
            self.assertIsNotNone(app.project.get("last_run"))
            self.assertIn("Trim: ASSUMED 5 gal", app.assumption_text.get())
            saved = load_project(app.project["id"])
            self.assertEqual(saved["di"]["zone_id"], "KEEP-1")
            self.assertEqual(saved["basis"]["ahj"], "Kept AHJ")
        finally:
            root.destroy()

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.zone_id.set("HELP-9")
            app.chat_entry.insert(0, "/help")
            app.send_chat()
            self.assertEqual(app.zone_id.get(), "HELP-9")
            self.assertEqual(app.project["di"]["zone_id"], "HELP-9")
            self.assertIn("/sample-di", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.zone_id.set("CHAT-1")
            app.chat_entry.insert(0, "hello there")
            app.send_chat()
            self.assertEqual(app.zone_id.get(), "CHAT-1")
            self.assertEqual(load_project(app.project["id"])["di"]["zone_id"], "CHAT-1")
            self.assertIn("hello there", app.chat_view.get("1.0", "end"))
        finally:
            root.destroy()

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.zone_id.set("NAMED-1")
            app._slash_new("/new Hall zone", "Hall zone")
            self.assertEqual(app.project["name"], "Hall zone")
            self.assertEqual(app.zone_id.get(), "NAMED-1")
            self.assertEqual(app.project["di"]["zone_id"], "NAMED-1")
        finally:
            root.destroy()

    def test_close_and_ctrl_s_save_form_edits(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk

        from fpfa.projects import list_projects, load_project, new_project
        from fpfa.ui import App

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app._on_close()
            self.assertEqual(list_projects(), [])
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            origin = new_project("Close job")
            app.open_project(origin["id"])
            app.refresh_projects(origin["id"])
            app.zone_id.set("CLOSED-2")
            app.ahj.set("Close AHJ")
            app.project_list.event_generate("<<ListboxSelect>>")
            root.update()
            self.assertEqual(app.zone_id.get(), "CLOSED-2")
            app._on_close()
            saved = load_project(origin["id"])
            self.assertEqual(saved["di"]["zone_id"], "CLOSED-2")
            self.assertEqual(saved["basis"]["ahj"], "Close AHJ")
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass

        root = tk.Tk()
        try:
            app = App(root)
            root.update()
            app.zone_id.set("KEY-3")
            app.chat_entry.focus_set()
            app.chat_entry.event_generate("<Control-s>")
            root.update()
            self.assertIsNotNone(app.project)
            self.assertEqual(app.zone_id.get(), "KEY-3")
            self.assertEqual(load_project(app.project["id"])["di"]["zone_id"], "KEY-3")
            self.assertIn("Saved", app.status.get())
        finally:
            root.destroy()

    def test_chat_does_not_replace_the_tool_plan(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        _isolate_data()
        import tkinter as tk
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.ui import App

        root = tk.Tk()
        seen = []
        try:
            app = App(root)
            root.update()
            app.chat_entry.insert(0, "/sample-di")
            app.send_chat()
            root.update()
            zone_gal = app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"]
            self.assertIn("281.3", app.results.get("1.0", "end"))
            save_api_key("sk-ant-local-test")

            class Fast:
                def __init__(self, _key):
                    pass

                def create(self, **kwargs):
                    seen.append(kwargs["messages"][0]["content"])
                    return SimpleNamespace(
                        stop_reason="end_turn",
                        content=[SimpleNamespace(type="text", text="I estimate about 40 gallons and 12 seconds.")],
                    )

            with patch("fpfa.ui.AnthropicMessages", Fast):
                app.chat_entry.insert(0, "revise the volume")
                app.send_chat()
                self._wait_for(app, "I estimate about 40 gallons and 12 seconds.")
            self.assertEqual(app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"], zone_gal)
            self.assertIn("281.3", app.results.get("1.0", "end"))
            self.assertIn("5.0 gal trim ASSUMED", app.results.get("1.0", "end"))
            self.assertIn("Governing zone total text: 281.3.", seen[0])
            self.assertIn("38.1", seen[0])
            self.assertIn("5.0 gal trim ASSUMED", seen[0])
            self.assertIn("Earlier turns:", seen[0])
            self.assertIn("tool plan", app.status.get())
        finally:
            root.destroy()

    def _wait_for(self, app, needle: str, timeout: float = 2.0) -> None:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.chat_view.get("1.0", "end"):
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")


if __name__ == "__main__":
    unittest.main()
