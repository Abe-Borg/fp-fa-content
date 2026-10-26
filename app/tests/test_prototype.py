"""App tests. Calc math stays in calcs/; this checks the workflow, export, and guards."""

from __future__ import annotations

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
        self.assertTrue(result["narrative_checks"]["quotes_volume"])
        self.assertTrue(result["narrative_checks"]["quotes_time"])

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
        self.assertIn("Section 21 13 16", text)
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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "section.docx"
            write_docx(path, {"name": "Exemption check", "basis": self.basis}, result)
            doc = Document(path)
            rows = [[cell.text for cell in row.cells] for row in doc.tables[1].rows]
        pipe_row = next(row for row in rows if row[0] == "Pipe only")
        zone_row = next(row for row in rows if row[0] == "Zone total")
        self.assertEqual(pipe_row[-1], "—")
        self.assertEqual(zone_row[-1], "No")


class ChatRequestTests(unittest.TestCase):
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
        client.create(max_tokens=8, messages=[], temperature=0, top_p=1, top_k=5)
        self.assertNotIn("temperature", client._client.messages.kwargs)
        self.assertNotIn("top_p", client._client.messages.kwargs)
        self.assertNotIn("top_k", client._client.messages.kwargs)
        self.assertNotIn("tool_choice", client._client.messages.kwargs)


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
        keystore.clear_api_key()
        self.assertEqual(keystore.load_api_key(), "")

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
        for folder in (REPO / "skills", REPO / "calcs"):
            for path in folder.rglob("*"):
                if path.suffix.lower() not in {".py", ".md"} or "__pycache__" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                if banned.search(text):
                    hits.append(str(path.relative_to(REPO)))
        self.assertEqual(hits, [])


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
            self.assertIn("not a listed water-delivery-time calculation", narrative)
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


if __name__ == "__main__":
    unittest.main()
