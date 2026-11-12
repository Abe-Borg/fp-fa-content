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

from desk_loop import Loop  # noqa: E402

os.environ.setdefault("FPFA_DATA_DIR", tempfile.mkdtemp(prefix="fpfa-test-"))



def _bullet_slugs(text: str, start: str, end: str) -> list[str]:
    chunk = text.split(start, 1)[1].split(end, 1)[0]
    return re.findall(r"(?m)^- `([a-z0-9-]+)`", chunk)


def _isolate_data():
    path = tempfile.mkdtemp(prefix="fpfa-test-")
    os.environ["FPFA_DATA_DIR"] = path
    os.environ.pop("FPFA_CONTENT_ROOT", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return Path(path)


def _support_every_claim():
    """Messages.create stand-in that marks every numbered claim Supported.

    This stand-in is not proof the narrative was checked. The production gate
    still treats NOT PULLED as open, rejects a cite that only repeats the
    claim, and rejects Supported when a figure in the claim is absent from
    the cite.
    """
    from fpfa.claim_check import numbered_bodies, split_checker_request

    seen = []

    def create(**kwargs):
        seen.append(kwargs)
        claims, sources = split_checker_request(kwargs["messages"][0]["content"])
        source_map = numbered_bodies(sources)
        lines = []
        for number in numbered_bodies(claims):
            cite = source_map.get(number, "")
            lines.append(f'{number}. Supported. Cite: "{cite}"')
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text="\n".join(lines))],
        )

    create.seen = seen
    return create


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
        self.assertIn("Trim: ASSUMED (the kernel's assumption)", blank)
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
        self.assertIn(total, rejected["narrative"])
        self.assertNotIn("40 gallons", rejected["narrative"])
        self.assertNotIn("Model draft (tables govern", rejected["narrative"])
        self.assertTrue(any("tool-plan" in item for item in rejected["warnings"]))

        def boom(_system, _user, _tools, _execute):
            raise RuntimeError("network down sk-ant-secretvalue")

        failed = self.run(self.root, self.di, self.basis, narrator=boom)
        self.assertEqual(failed["source"], "tool-plan")
        self.assertIn(volume, failed["narrative"])
        self.assertNotIn("sk-ant-secretvalue", " ".join(failed["warnings"]))

    def test_rejected_model_draft_is_absent_from_the_docx(self):
        from docx import Document

        from fpfa.spec_docx import write_docx

        first = self.run(self.root, self.di, self.basis)
        volume = self.fmt1(first["tools"]["zone_trapped_volume"]["zone_gal"])
        total = self.fmt1(first["tools"]["di_trip_to_water"]["t_total_s"])
        marker = "REJECTED-PROSE about 750 gal and 12 seconds."

        def bad(_system, _user, _tools, _execute):
            return {"text": marker, "tool_calls": []}

        rejected = self.run(self.root, self.di, self.basis, narrator=bad)
        self.assertEqual(rejected["source"], "tool-plan")
        self.assertNotIn(marker, rejected["narrative"])
        self.assertIn(volume, rejected["narrative"])
        self.assertIn(total, rejected["narrative"])

        def doc_text(result) -> str:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "section.docx"
                write_docx(path, {"name": "Sample data hall DI zone", "basis": self.basis}, result)
                doc = Document(path)
                text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
                for table in doc.tables:
                    for row in table.rows:
                        text += "\n" + " | ".join(cell.text for cell in row.cells)
                return text

        text = doc_text(rejected)
        self.assertNotIn(marker, text)
        self.assertNotIn("Model draft (tables govern", text)
        self.assertIn(volume, text)
        self.assertIn(total, text)
        self.assertIn("Section 21 13 19", text)

        legacy = dict(rejected)
        legacy["narrative"] = (
            rejected["narrative"]
            + "\n\nModel draft (tables govern if the figures differ):\n"
            + marker
        )
        legacy_text = doc_text(legacy)
        self.assertNotIn(marker, legacy_text)
        self.assertNotIn("Model draft (tables govern", legacy_text)
        self.assertIn(volume, legacy_text)
        self.assertIn(total, legacy_text)

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
        self.assertEqual(screen["nfpa_size_threshold_gal"], 500)
        self.assertIn("exemption threshold (NFPA 13-2025 §8.3.2.3.1.1): no", result["narrative"])
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

    def test_fill_flow_rejects_non_finite(self):
        import math

        from fpfa.calc_tools import ToolSession
        from fpfa.sample_data import EXAMPLE_DI
        from fpfa.workflow import validate_di

        formulas = ToolSession(self.root).formulas
        for bad in ("1e309", "inf", "nan", math.inf, math.nan):
            di = json.loads(json.dumps(EXAMPLE_DI))
            di["q_fill_gpm"] = bad
            with self.assertRaises(ValueError) as caught:
                validate_di(di)
            self.assertIn("finite", str(caught.exception).lower())
            with self.assertRaises(ValueError):
                self.run(self.root, di, self.basis)
            with self.assertRaises(formulas.CalcError):
                formulas._as_float("q_fill_gpm", bad)
            with self.assertRaises(formulas.CalcError):
                formulas._require_positive("q_fill_gpm", bad)
            with self.assertRaises(formulas.CalcError):
                formulas.di_trip_to_water(100, bad)
            with self.assertRaises(formulas.CalcError):
                formulas.air_fill_scfm(100, bad, 30)

        for bad in (0, -5, "0"):
            di = json.loads(json.dumps(EXAMPLE_DI))
            di["q_fill_gpm"] = bad
            with self.assertRaises(ValueError) as caught:
                validate_di(di)
            self.assertIn("greater than 0", str(caught.exception))

        di = json.loads(json.dumps(EXAMPLE_DI))
        di["trim_gal"] = "1e309"
        with self.assertRaises(ValueError) as caught:
            self.run(self.root, di, self.basis)
        self.assertIn("finite", str(caught.exception).lower())

        session = ToolSession(self.root)
        with self.assertRaises(formulas.CalcError):
            session.execute("zone_trapped_volume", {
                "segments": [{"d_in": 4.026, "length_ft": 10}],
                "trim_gal": "1e309",
                "fittings_percent": 0,
            })
        with self.assertRaises(formulas.CalcError):
            session.execute("dry_delivery_screen", {
                "segments": [{"d_in": 4.026, "length_ft": 10}],
                "q_fill_gpm": "1e309",
                "system_type": "di",
                "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM",
            })
        with self.assertRaises(formulas.CalcError):
            formulas._require_positive("q_fill_gpm", 0)

    def test_compressor_n2_reports_gauge_and_absolute(self):
        from docx import Document

        from fpfa.calc_tools import ToolSession
        from fpfa.spec_docx import write_docx

        result = self.run(self.root, self.di, self.basis)
        nitrogen = result["tools"]["nitrogen_gate"]
        gauge = f"{nitrogen['scfm_gauge_basis']:.2f}"
        absolute = f"{nitrogen['scfm_abs_basis']:.2f}"
        self.assertNotEqual(gauge, absolute)
        self.assertGreater(nitrogen["scfm_abs_basis"], nitrogen["scfm_gauge_basis"])
        self.assertIn(f"Gauge-basis fill rate is {gauge} scfm", nitrogen["fill_bases"])
        self.assertIn(f"Absolute-basis fill rate is {absolute} scfm", nitrogen["fill_bases"])
        self.assertIn(f"Gauge-basis fill rate is {gauge} scfm", result["narrative"])
        self.assertIn(f"Absolute-basis fill rate is {absolute} scfm", result["narrative"])

        session = ToolSession(self.root)
        chat = session.execute("nitrogen_gate", {
            "v_gal": result["tools"]["zone_trapped_volume"]["zone_gal"],
            "p_psig": 40,
            "t_min": 30,
        })
        self.assertIn(f"Gauge-basis fill rate is {gauge} scfm", chat["fill_bases"])
        self.assertIn(f"Absolute-basis fill rate is {absolute} scfm", chat["fill_bases"])

        sized = session.execute("fp_calc", {
            "op": "compressor_n2_sizing",
            "inputs": {
                "systems": [
                    {"id": "A", "v_gal": 750, "p_psig": 40},
                    {"id": "B", "v_gal": 500, "p_psig": 40},
                ],
                "t_min": 30,
            },
        })
        self.assertGreater(sized["compressor_scfm_abs"], sized["compressor_scfm_gauge"])
        self.assertGreater(sized["n2_campus_scfm_abs"], sized["n2_campus_scfm_gauge"])
        self.assertIn(
            f"Compressor gauge-basis fill rate is {sized['compressor_scfm_gauge']:.2f} scfm",
            sized["fill_bases"],
        )
        self.assertIn(
            f"Compressor absolute-basis fill rate is {sized['compressor_scfm_abs']:.2f} scfm",
            sized["fill_bases"],
        )
        self.assertIn(
            f"N2 campus gauge-basis fill rate is {sized['n2_campus_scfm_gauge']:.2f} scfm",
            sized["fill_bases"],
        )
        self.assertIn(
            f"N2 campus absolute-basis fill rate is {sized['n2_campus_scfm_abs']:.2f} scfm",
            sized["fill_bases"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "section.docx"
            write_docx(path, {"name": "Sample data hall DI zone", "basis": self.basis}, result)
            doc = Document(path)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            fill_rows = None
            for table in doc.tables:
                rows = [[cell.text for cell in row.cells] for row in table.rows]
                text += "\n" + "\n".join(" | ".join(row) for row in rows)
                if rows and rows[0][:2] == ["Fill basis", "scfm"]:
                    fill_rows = rows
        self.assertEqual(fill_rows, [
            ["Fill basis", "scfm"],
            ["Gauge", gauge],
            ["Absolute", absolute],
        ])
        self.assertIn(f"Gauge-basis fill rate is {gauge} scfm", text)
        self.assertIn(f"Absolute-basis fill rate is {absolute} scfm", text)

    def test_chat_exemption_uses_zone_total_when_trim_is_present(self):
        import math

        from fpfa.calc_tools import ToolSession
        from fpfa.workflow import govern_nfpa_exemption

        diameter = 6.065
        gallons_per_foot = math.pi / 4.0 * diameter * diameter / 144.0 * 7.48
        segments = [{"d_in": diameter, "length_ft": 495.0 / gallons_per_foot}]
        session = ToolSession(self.root)
        volume = session.execute("zone_trapped_volume", {
            "segments": segments,
            "fittings_percent": 0,
            "trim_gal": 10,
        })
        self.assertAlmostEqual(volume["pipe_gal"], 495, delta=0.05)
        self.assertAlmostEqual(volume["zone_gal"], 505, delta=0.05)

        # The times and the basis are the caller's: the tool takes none for granted.
        times = {"t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM"}
        pipe_only = session.execute("dry_delivery_screen", {
            "segments": segments,
            "q_fill_gpm": 500,
            "system_type": "di",
            "qod": True,
            **times,
        })
        # A pipe-only screen never says the exemption is met: 495 gal of pipe is under the cap and the zone
        # total is not. The kernel's own flag is kept under its true name.
        self.assertIsNone(pipe_only["nfpa_delivery_time_exempt"])
        self.assertTrue(pipe_only["pipe_only_nfpa_delivery_time_exempt"])
        self.assertEqual(pipe_only["exemption_status"], "not determined")
        self.assertIn("pipe-only screen", pipe_only["exemption_note"])
        self.assertNotIn("exemption_volume_gal", pipe_only)
        # Handed the takeoff's zone total, the same screen answers, and the answer is no.
        on_zone = session.execute("dry_delivery_screen", {
            "segments": segments, "q_fill_gpm": 500, "system_type": "di", "qod": True, "zone_gal": volume["zone_gal"],
            **times,
        })
        self.assertIs(on_zone["nfpa_delivery_time_exempt"], False)
        self.assertAlmostEqual(on_zone["exemption_volume_gal"], volume["zone_gal"], places=6)

        chat = session.execute("dry_delivery_screen", {
            "segments": segments,
            "q_fill_gpm": 500,
            "system_type": "di",
            "qod": True,
            "trim_gal": 10,
            "fittings_percent": 0,
            **times,
        })
        governed = govern_nfpa_exemption(pipe_only, volume["zone_gal"])
        self.assertFalse(chat["nfpa_delivery_time_exempt"])
        self.assertTrue(chat["pipe_only_nfpa_delivery_time_exempt"])
        self.assertEqual(chat["nfpa_size_cap_gal"], 500)
        self.assertEqual(chat["nfpa_delivery_time_exempt"], governed["nfpa_delivery_time_exempt"])
        self.assertAlmostEqual(chat["exemption_volume_gal"], governed["exemption_volume_gal"], places=6)
        self.assertAlmostEqual(chat["exemption_volume_gal"], 505, delta=0.05)
        self.assertAlmostEqual(chat["t_total_s"], pipe_only["t_total_s"], places=6)


class ChatRequestTests(unittest.TestCase):
    def test_slash_commands_and_sample_di_aliases(self):
        from fpfa.spec_docx import DRAFT_SECTION
        from fpfa.desk import chat_run_summary, parse_slash_command, slash_help_text, unknown_slash_text

        self.assertEqual(parse_slash_command("/sample-di"), ("sample-di", ""))
        self.assertEqual(parse_slash_command("  /SAMPLE_DI  "), ("sample-di", ""))
        self.assertEqual(parse_slash_command("/sampledi"), ("sample-di", ""))
        self.assertEqual(parse_slash_command("/sample-bess"), ("sample-bess", ""))
        self.assertEqual(parse_slash_command("/sample_bess"), ("sample-bess", ""))
        self.assertEqual(parse_slash_command("/SAMPLEBESS"), ("sample-bess", ""))
        self.assertEqual(parse_slash_command("/run now"), ("run", "now"))
        self.assertEqual(parse_slash_command("/new Hall zone"), ("new", "Hall zone"))
        self.assertEqual(parse_slash_command("/help"), ("help", ""))
        self.assertEqual(parse_slash_command("/heavy check the room"), ("heavy", "check the room"))
        self.assertIsNone(parse_slash_command("explain the trim"))
        self.assertIsNone(parse_slash_command(""))
        self.assertIsNone(parse_slash_command("/"))
        help_text = slash_help_text()
        self.assertIn("/sample-di", help_text)
        self.assertIn("/sample-bess", help_text)
        self.assertIn("/heavy", help_text)
        self.assertIn("text-only", help_text)
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
        from fpfa.desk import format_chat_request

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
        self.assertIn("Use tools for any gallons", text)
        from fpfa.desk import chat_request_text

        hosted = chat_request_text([], {"insurer": "FM"}, {"zone_id": "DH-1"}, "review", hosted=True)
        everyday = chat_request_text([], {"insurer": "FM"}, {"zone_id": "DH-1"}, "review")
        self.assertIn("already-computed zone packet", hosted)
        self.assertIn("Do not call read_role, read_skill, read_mode", hosted)
        self.assertNotIn("Use tools for any gallons", hosted)
        self.assertIn("Use tools for any gallons", everyday)
        self.assertNotIn("already-computed zone packet", everyday)


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

    def test_frozen_app_calls_keyring_in_process(self):
        """A PyInstaller build must not relaunch sys.executable (Cynosure.exe) to reach keyring."""
        import importlib.util
        import threading
        from unittest.mock import patch

        _isolate_data()
        # Earlier tests here swap fpfa.keystore._keyring_call for fakes and leave them in
        # place. Load a private copy so this test sees the real dispatcher.
        spec = importlib.util.spec_from_file_location(
            "fpfa_keystore_frozen_probe", APP_DIR / "fpfa" / "keystore.py"
        )
        keystore = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(keystore)

        store = {}
        release = threading.Event()

        def delete_password(service, account):
            del store[(service, account)]

        fake_keyring = SimpleNamespace(
            set_password=lambda service, account, value: store.__setitem__((service, account), value),
            get_password=lambda service, account: store.get((service, account)),
            delete_password=delete_password,
        )
        launched = []

        def no_launch(*args, **kwargs):
            launched.append(args)
            raise AssertionError("the frozen app relaunched sys.executable")

        frozen_exe = str(Path(tempfile.gettempdir()) / "Cynosure" / "Cynosure.exe")
        with patch.object(sys, "frozen", True, create=True), \
                patch.object(sys, "executable", frozen_exe), \
                patch.dict(sys.modules, {"keyring": fake_keyring}), \
                patch.object(subprocess, "run", no_launch), \
                patch.object(subprocess, "Popen", no_launch):
            self.assertEqual(keystore._keyring_call("set", "sk-ant-frozen-test", timeout=2), "ok")
            self.assertEqual(keystore._keyring_call("get", timeout=2), "sk-ant-frozen-test")
            self.assertEqual(keystore._keyring_call("delete", timeout=2), "ok")
            self.assertEqual(keystore._keyring_call("get", timeout=2), "")
            self.assertEqual(keystore._keyring_call("delete", timeout=2), "ok")

            os.environ["FPFA_USE_KEYRING"] = "1"
            try:
                self.assertEqual(keystore.save_api_key("sk-ant-frozen-test"), "keyring")
                self.assertEqual(keystore.load_api_key(), "sk-ant-frozen-test")
                self.assertFalse((keystore.data_dir() / "anthropic-api-key").exists())
                keystore.clear_api_key()
                self.assertNotIn((keystore.SERVICE, keystore.ACCOUNT), store)
            finally:
                os.environ.pop("FPFA_USE_KEYRING", None)

            def hang(service, account):
                release.wait(10)
                return None

            fake_keyring.get_password = hang
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    keystore._keyring_call("get", timeout=0.2)
            finally:
                release.set()

            # A delete that timed out must not land after a later save and remove it.
            fake_keyring.get_password = lambda service, account: store.get((service, account))
            slow_delete = threading.Event()

            def delayed_delete(service, account):
                slow_delete.wait(10)
                store.pop((service, account), None)

            fake_keyring.delete_password = delayed_delete
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    keystore._keyring_call("delete", timeout=0.2)
                try:
                    keystore._keyring_call("set", "sk-ant-replacement", timeout=0.2)
                except subprocess.TimeoutExpired:
                    pass
            finally:
                slow_delete.set()
            self.assertEqual(keystore._keyring_call("get", timeout=2), "sk-ant-replacement")
            fake_keyring.delete_password = delete_password
            self.assertEqual(keystore._keyring_call("delete", timeout=2), "ok")

            def no_backend(service, account):
                raise RuntimeError("No recommended backend was available.")

            fake_keyring.get_password = no_backend
            with self.assertRaises(RuntimeError) as caught:
                keystore._keyring_call("get", timeout=2)
            self.assertIn("No recommended backend", str(caught.exception))

            _isolate_data()
            self.assertEqual(keystore.save_api_key("sk-ant-frozen-test"), "file")
            with patch.object(keystore.sys, "platform", "win32"):
                text = keystore.key_status()
            self.assertIn("user-only file", text)
            self.assertIn("Credential Manager", text)
            self.assertIn("packaged app", text)
            self.assertNotIn("pywin32", text)
            keystore.clear_api_key()
        self.assertEqual(launched, [])

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

    def test_apparatus_water_spray_is_an_allowed_exception(self):
        everyday = (REPO / "roles" / "everyday" / "ROLE.md").read_text(encoding="utf-8")
        lock = (REPO / "corpus" / "scope-lock.md").read_text(encoding="utf-8")
        for text in (everyday, lock):
            lowered = text.lower()
            self.assertIn("outdoor oil-filled transformer apparatus water spray", lowered)
            self.assertIn("power-block-transformer-water-spray", text)
            self.assertIn("foam", lowered)
            self.assertIn("clean agent", lowered)
            self.assertIn("single-interlock", lowered)
            self.assertRegex(text, r"Canada|Canadian")
        self.assertNotIn("water spray are out of scope", lock)
        self.assertIn("not a building deluge system", everyday)

    def test_pack_has_no_roster_or_client_names(self):
        banned = re.compile(
            r"\bAbe\b|DC FP Lead|stay dark|Hyperion|Abraham|\bNovva\b|NEEDS PE REVIEW|/workspace/"
        )
        hits = []
        for folder in (REPO / "skills", REPO / "corpus", REPO / "calcs", REPO / "roles", REPO / "modes"):
            for path in folder.rglob("*"):
                if path.suffix.lower() not in {".py", ".md"} or "__pycache__" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                if banned.search(text):
                    hits.append(str(path.relative_to(REPO)))
        self.assertEqual(hits, [])

    def test_pack_has_no_qa_status_or_round_tags(self):
        """Strip rules 2026-11-09: no claim-check/QA status lines, round tags, or PE-approval lines ship."""
        banned = re.compile(
            r"(?i)claimcheck(?!\.md)"  # the <section>-claimcheck.md verdict file name is functional
            r"|(?i:\bqa-?\d+\b)"
            r"|PASS \d+/\d+|\b\d+/\d+ Supported\b"
            r"|(?i:\bPE[- ]approved\b)|\bNot PE\b"
            r"|Synthetic training (?:use|tool)|_scout/"
            r"|\bLead\d+\b|\bfold ?\d+\b|\b[Bb]\d+-R\d+\b|\bbatch\d+ R\d+\b"
        )
        hits = []
        for folder in (REPO / "skills", REPO / "corpus", REPO / "calcs", REPO / "roles", REPO / "modes", REPO / "specs"):
            for path in folder.rglob("*"):
                if path.suffix.lower() not in {".py", ".md"} or "__pycache__" in path.parts or ".bak" in path.name:
                    continue
                for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if banned.search(line):
                        hits.append(f"{path.relative_to(REPO)}:{number}")
        self.assertEqual(hits, [])

    def test_content_pack_inventory_matches_the_indexes(self):
        """Saturday step 6: the in-repo pack is the index. Corpus search is search_corpus."""
        skills_readme = (REPO / "skills" / "README.md").read_text(encoding="utf-8")
        tier_a = _bullet_slugs(skills_readme, "Tier A methods", "Tier B methods")
        tier_b = _bullet_slugs(skills_readme, "Tier B methods", "Pilot method")
        pilot = _bullet_slugs(skills_readme, "Pilot method", "Tier C methods")
        tier_c = _bullet_slugs(skills_readme, "Tier C methods", "Specialist role prompts")
        self.assertEqual(len(tier_a), 18)
        self.assertEqual(len(tier_b), 24)
        self.assertEqual(pilot, ["ess-isolation-venting-and-duration"])
        self.assertEqual(
            tier_c,
            [
                "storage-staging-sprinkler-design",
                "liquid-cooled-escaped-liquids-leak-detect",
                "mv-switchgear-room-package",
                "power-block-transformer-water-spray",
                "ess-exhaust-duct-shaft-and-duct-sprinklers",
                "fa-bess-gas-detection-layout-and-setpoints",
                "fa-bess-gas-relay-map-and-cause-effect",
                "pipe-slope-elevation-drop",
            ],
        )
        self.assertEqual(len(set(tier_a + tier_b)), 42)
        self.assertNotIn(pilot[0], tier_a + tier_b + tier_c)
        disk = sorted(
            path.name
            for path in (REPO / "skills").iterdir()
            if (path / "SKILL.md").is_file()
        )
        self.assertEqual(disk, sorted(tier_a + tier_b + pilot + tier_c))

        corpus_indexed = re.findall(
            r"(?m)^\| `([^`]+\.md)`",
            (REPO / "corpus" / "README.md").read_text(encoding="utf-8"),
        )
        corpus_disk = sorted(
            path.relative_to(REPO / "corpus").as_posix()
            for path in (REPO / "corpus").rglob("*.md")
            if path.name.lower() != "readme.md"
        )
        self.assertEqual(sorted(corpus_indexed), corpus_disk)
        self.assertEqual(len(corpus_disk), 120)
        self.assertIn("scope-lock.md", corpus_disk)

        spec_indexed = re.findall(
            r"(?m)^\| `([^`]+\.md)`",
            (REPO / "specs" / "README.md").read_text(encoding="utf-8"),
        )
        spec_disk = sorted(
            path.name
            for path in (REPO / "specs").glob("*.md")
            if path.name.lower() != "readme.md"
        )
        self.assertEqual(sorted(spec_indexed), spec_disk)
        self.assertEqual(len(spec_disk), 8)
        self.assertIn("21-13-19-double-interlock-preaction.md", spec_disk)
        self.assertNotIn("README.md", spec_disk)

        secret = re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}")
        leaks = []
        for folder in (REPO / "skills", REPO / "corpus", REPO / "specs"):
            for path in folder.rglob("*.md"):
                if secret.search(path.read_text(encoding="utf-8", errors="replace")):
                    leaks.append(str(path.relative_to(REPO)))
        self.assertEqual(leaks, [])

        wired = []
        # search_corpus is the only reader. The pack builder still only names the folder.
        search_wired = {
            "app/fpfa/calc_tools.py",
            "app/fpfa/corpus_search.py",
            "app/fpfa/fa_calc.py",
        }
        for path in (REPO / "app" / "fpfa").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(REPO))
            if path.name == "content_pack.py":
                self.assertNotIn("spec_notes", text)
                self.assertNotIn("list_skills", text)
                self.assertNotIn("read_skill", text)
                continue
            mentions = bool(re.search(r"""['\"]corpus['\"]""", text)) or (
                "corpus/" in text and path.name != "paths.py"
            )
            if mentions and rel not in search_wired:
                wired.append(rel)
        self.assertEqual(wired, [])

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
            self.assertEqual(note["text"], (folder / note["name"]).read_text(encoding="utf-8"))

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
            r"|NFPA 2001"
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
        fa_spec = (folder / "28-31-00-fire-detection-and-alarm.md").read_text(encoding="utf-8")
        self.assertIn("Country gate (US | Canada)", fa_spec)
        self.assertIn("3.2.4.9.(5)", fa_spec)
        self.assertIn("3.2.4.9.(6)", fa_spec)
        self.assertIn("NEEDS HOLD", fa_spec)
        self.assertIn("CAN/ULC-S524", fa_spec)
        self.assertEqual(hits, [])


class EverydayPathTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root

        self.root = content_root()

    def test_roles_load_like_skills(self):
        from fpfa.roles_loader import list_roles, read_role

        slugs = [item["slug"] for item in list_roles(self.root)]
        self.assertEqual(
            slugs,
            ["everyday", "fa-releasing", "fp-sprinkler", "lead", "qa-specialist", "spec-draft"],
        )
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
        self.assertIn("- qa-specialist:", system)
        self.assertIn("Blind claim check before export of section 21 13 19.", system)
        qa_body = "Judge each numbered claim from the cites file alone."
        self.assertIn(qa_body, (REPO / "roles" / "qa-specialist" / "ROLE.md").read_text(encoding="utf-8"))
        self.assertNotIn(qa_body, system)
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
            self.assertNotIn(qa_body, text, path.name)
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
        from fpfa.desk import chat_request_text
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
        self.assertNotIn("qa-specialist", payload["roles_to_read"])
        self.assertIn("- qa-specialist:", seen["system"])
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
            self.assertNotIn(
                "An explosion-control starter quotes the LFL tool plan and does not recompute it.",
                text,
                path.name,
            )

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
        from fpfa.desk import chat_request_text
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
        _isolate_data()

        
        root = Loop()
        try:
            app = root.open_desk()
            app.load_demo()
            root.update()
            self.assertEqual(len(app.segments), 4)
            narrative = app.results_text
            self.assertIn("Zone total is", narrative)
            self.assertIn("5.0 gal trim ASSUMED", narrative)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", narrative)
            self.assertIn("not a listed water-delivery-time calculation", narrative)
            self.assertIn("Trim: ASSUMED (the kernel's assumption)", app.assumption_text.get())
            self.assertIn("30.0 s ASSUMED", app.assumption_text.get())
            self.assertIsNotNone(app.project["last_run"])
            with tempfile.TemporaryDirectory() as tmp:
                blocked = Path(tmp) / "blocked.docx"
                with self.assertRaises(RuntimeError):
                    app.export_to(blocked)
                self.assertFalse(blocked.exists())
                written = app.export_to(Path(tmp) / "draft.docx", create=_support_every_claim())
                self.assertTrue(written.is_file())
                self.assertGreater(written.stat().st_size, 1000)
                self.assertIn("| claim |", app.thread_text())
        finally:
            root.destroy()

    def test_async_results_stay_on_the_project_that_started_them(self):
        _isolate_data()

        from fpfa.projects import load_project, new_project, save_project
        
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
        root = Loop()
        try:
            app = root.open_desk()
            origin = new_project("Origin job")
            other = new_project("Other job")
            app.open_project(other["id"])
            app._finish_run(origin["id"], result, None)
            self.assertEqual(load_project(origin["id"])["last_run"]["narrative"], "ORIGIN-RESULT")
            self.assertIsNone(load_project(other["id"]).get("last_run"))
            self.assertNotIn("ORIGIN-RESULT", app.results_text)

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
            self.assertNotIn("solenoid", app.thread_text())
        finally:
            root.destroy()

    def test_poll_continues_after_a_callback_raises(self):
        _isolate_data()

        from fpfa.projects import new_project
        
        root = Loop()
        try:
            app = root.open_desk()
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
            seen.clear()
            app.queue.put(lambda: app._finish_run(origin["id"], result, None))
            app.queue.put(lambda: seen.append("after-run"))
            app._poll()
            self.assertEqual(seen, ["after-run"])
            self.assertEqual(app.project["last_run"]["narrative"], "KEPT")
            self.assertIn("KEPT", app.results_text)
        finally:
            root.destroy()

    def test_chat_is_the_primary_pane(self):
        """The window opens on the thread. What the page draws comes from this state.

        The buttons, the menus, and the job panel are the page's; tests/test_web.py
        drives them in a browser.
        """
        _isolate_data()

        from fpfa.desk import THREAD_HINT

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            state = app.snapshot()
            welcome = app.thread_text()
            self.assertIn(THREAD_HINT.splitlines()[0], welcome)
            self.assertEqual(state["welcome"]["title"], THREAD_HINT.splitlines()[0])
            links = [link["action"] for link in state["welcome"]["links"]]
            self.assertEqual(links, ["settings", "sample-di"])
            self.assertIn("/sample-di", " ".join(link["text"] for link in state["welcome"]["links"]))
            self.assertIn("Add your Anthropic API key", state["welcome"]["links"][0]["text"])
            # The app picks the mode for each path; the window offers no choice of one.
            self.assertNotIn("mode", state)
            self.assertEqual(state["title"], "New chat")
            self.assertEqual(state["activity"], [])
            self.assertEqual(state["turns"] if "turns" in state else state["thread"]["turns"], [])
            # The starters: the sample, and the commands. A question chip needs a key.
            self.assertEqual([chip["action"] for chip in state["chips"]], ["/sample-di", "/help"])
        finally:
            root.destroy()

    def test_first_chat_turn_needs_no_sample(self):
        """With a key saved, open the app and ask. Sample DI never runs."""
        _isolate_data()
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import list_projects, load_project
        from fpfa.desk import THREAD_HINT, WELCOME_KEY_LINK

        save_api_key("sk-ant-local-test")
        seen = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(
                        type="text",
                        text="## Short answer\n- **Trim** is ASSUMED until a valve sheet is in hand.",
                    )],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            welcome = app.thread_text()
            self.assertIn(THREAD_HINT.splitlines()[0], welcome)
            self.assertNotIn(WELCOME_KEY_LINK, welcome)
            self.assertIsNone(app.project)
            self.assertEqual(list_projects(), [])
            with patch("fpfa.desk.AnthropicMessages", Fast):
                app.send_chat("How should I split a 40,000 ft2 data hall into DI zones?")
                self._wait_for(app, "Short answer")
            thread = app.thread_text()
            self.assertNotIn(THREAD_HINT.splitlines()[0], thread)
            self.assertIn("How should I split", thread)
            self.assertIn("• Trim is ASSUMED", thread)
            self.assertNotIn("**", thread)
            self.assertEqual(len(seen), 1)
            self.assertIn("How should I split", seen[0]["messages"][0]["content"])
            projects = list_projects()
            self.assertEqual(len(projects), 1)
            self.assertNotIn("Sample", projects[0]["name"])
            self.assertEqual(app.project["name"], "How should I split a 40,000 ft2 data hall into…")
            self.assertEqual(app.snapshot()["title"], app.project["name"])
            saved = load_project(app.project["id"])
            self.assertIsNone(saved.get("last_run"))
            self.assertIsNone(saved.get("bess_run"))
            self.assertEqual([turn["role"] for turn in saved["chat"]], ["user", "assistant"])
            kinds = [job.kind for job in app.jobs.snapshot()]
            self.assertEqual(kinds, ["chat"])
            self.assertTrue(bool(app.activity_rows))
        finally:
            root.destroy()

    def test_pending_line_shows_while_a_reply_is_out(self):
        _isolate_data()
        import threading
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")
        release = threading.Event()

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **_kwargs):
                release.wait(3)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="pending reply")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                app.send_chat("Which trim family?")
                self.assertIn("Working on it…", app.thread_text())
                release.set()
                self._wait_for(app, "pending reply")
                import time

                deadline = time.time() + 2
                while time.time() < deadline and "Working on it…" in app.thread_text():
                    app._poll()
                    time.sleep(0.02)
            self.assertNotIn("Working on it…", app.thread_text())
        finally:
            release.set()
            root.destroy()

    def test_composer_sends_slash_commands_and_questions(self):
        """What the composer sends. Enter, Shift+Enter, and the growing box are the page's (tests/test_web.py)."""
        _isolate_data()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("   ")
            self.assertIsNone(app.project)
            app.send_chat("/help")
            root.update()
            self.assertIn("/sample-di —", app.thread_text())
            self.assertNotIn("## Commands", app.thread_text())
            # /help is a slash command, so the job keeps its default name.
            self.assertEqual(app.project["name"], "Untitled job")
            # A chip sends exactly the message it stands for.
            app._use_chip("/help")
            self.assertEqual([turn["text"] for turn in app.chat_log if turn["role"] == "user"], ["/help", "/help"])
        finally:
            root.destroy()

    def test_new_chat_rename_and_delete(self):
        _isolate_data()
        from unittest.mock import patch

        from fpfa.projects import list_projects, load_project
        from fpfa.desk import THREAD_HINT

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.new_job()
            first = app.project["id"]
            self.assertEqual(app.project["name"], "Untitled job")
            # A second New chat on an untouched job does not pile up empty jobs.
            app.new_job()
            self.assertEqual(app.project["id"], first)
            self.assertEqual(len(list_projects()), 1)
            app.send_chat("hello there")
            self.assertEqual(app.project["name"], "hello there")
            app.rename_job(None, "  Hall 2  zoning ")
            self.assertEqual(load_project(first)["name"], "Hall 2 zoning")
            self.assertEqual(app.snapshot()["title"], "Hall 2 zoning")
            self.assertIn("Hall 2 zoning", [row["name"] for row in app.project_rows])
            app.new_job()
            self.assertNotEqual(app.project["id"], first)
            self.assertIn(THREAD_HINT.splitlines()[0], app.thread_text())
            app.open_project(first)
            self.assertIn("hello there", app.thread_text())
            # The page asks the designer first; the desk deletes what it is told to.
            app.delete_job(first)
            self.assertIsNone(app.project)
            self.assertEqual(app.chat_log, [])
            self.assertNotIn("hello there", app.thread_text())
            self.assertIn(THREAD_HINT.splitlines()[0], app.thread_text())
            self.assertNotIn(first, [row["id"] for row in list_projects()])
        finally:
            root.destroy()

    def test_a_chat_turn_is_written_in_the_mixed_mode(self):
        """There is no Mode menu. A typed question gets the mixed mode, whatever an older job saved."""
        _isolate_data()
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import new_project, save_project

        save_api_key("sk-ant-local-test")
        seen = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="Mixed reply.")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            self.assertNotIn("mode", app.snapshot())
            # A job saved while the menu existed still carries the mode it was left in. Nothing reads it.
            job = new_project("Older job")
            job["mode"] = "brainstorm"
            save_project(job)
            app.open_project(job["id"])
            app.send_chat("/mode calculator")
            self.assertIn("/mode is not a command.", app.thread_text())
            with patch("fpfa.desk.AnthropicMessages", Fast):
                app.send_chat("draft the zone")
                self._wait_for(app, "Mixed reply.")
            self.assertIn("Active mode: mixed.", seen[0]["messages"][0]["content"])
            self.assertIn(
                "This mode may explore an option, quote a calc tool, and draft in the same reply.",
                seen[0]["system"],
            )
            self.assertNotIn("This mode explores options.", seen[0]["system"])
            self.assertNotIn("This mode answers with tool figures.", seen[0]["system"])
        finally:
            root.destroy()

    def test_a_zone_narration_is_written_in_the_synthesis_mode(self):
        """Run zone's narrator gets the mode written for a draft after a tool plan."""
        _isolate_data()
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key

        save_api_key("sk-ant-local-test")
        seen = []

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="zone narrative without the governing figures")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(True)
            with patch("fpfa.desk.AnthropicMessages", Fast):
                app.send_chat("/sample-di")
                self._wait_for(app, "5.0 gal trim ASSUMED")
            self.assertTrue(seen)
            self.assertIn("This mode writes the draft narrative after a zone tool plan.", seen[0]["system"])
            self.assertNotIn("This mode may explore an option", seen[0]["system"])
            self.assertIn("Active mode: synthesis.", seen[0]["messages"][0]["content"])
            self.assertEqual(app.project["last_run"]["mode"], "synthesis")
        finally:
            root.destroy()

    def test_chat_persists_when_optional_form_number_is_invalid(self):
        """A bad optional-form number must not discard the chat."""
        _isolate_data()
        from fpfa.projects import load_project, new_project, save_project

        def select_project(app, project_id: str) -> None:
            app.refresh_projects()
            app.select_project(project_id)

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            job = new_project("Form job")
            job["chat"] = [{"role": "user", "text": "keep this thread"}]
            save_project(job)
            other = new_project("Other job")
            save_project(other)
            app.open_project(job["id"])
            app.density.set("not-a-number")

            app.send_chat("/help")
            chat = app.thread_text()
            self.assertIn("keep this thread", chat)
            self.assertIn("/help", chat)
            saved = load_project(job["id"])
            saved_text = [turn.get("text") for turn in saved["chat"]]
            self.assertIn("keep this thread", saved_text)
            self.assertIn("/help", saved_text)
            self.assertNotIn("not-a-number", json.dumps(saved.get("di")))

            select_project(app, other["id"])
            self.assertEqual(app.project["id"], other["id"])
            select_project(app, job["id"])
            self.assertIn("keep this thread", app.thread_text())

            app.density.set("not-a-number")
            app.notices.clear()
            app.save_current()
            # The page shows the notice in a dialog of its own.
            self.assertEqual([notice["title"] for notice in app.notices], ["Save"])
            saved = load_project(job["id"])
            self.assertIn("keep this thread", [turn.get("text") for turn in saved["chat"]])
            self.assertNotIn("not-a-number", json.dumps(saved.get("di")))

            app.hose.set("bad-gpm")
            select_project(app, other["id"])
            self.assertEqual(app.project["id"], other["id"])
            select_project(app, job["id"])
            reopened = load_project(job["id"])
            self.assertIn("keep this thread", [turn.get("text") for turn in reopened["chat"]])
            self.assertIn("/help", [turn.get("text") for turn in reopened["chat"]])
            self.assertIn("keep this thread", app.thread_text())
        finally:
            root.destroy()

    def test_sample_di_slash_loads_and_runs_the_zone(self):
        _isolate_data()

        from fpfa.spec_docx import DRAFT_SECTION
        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/sample-di")
            chat = app.thread_text()
            results = app.results_text
            self.assertEqual(len(app.segments), 4)
            self.assertIn("/sample-di", chat)
            self.assertIn("5.0 gal trim ASSUMED", chat)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", chat)
            self.assertIn(DRAFT_SECTION, chat)
            self.assertIn("5.0 gal trim ASSUMED", results)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", results)
            self.assertIn("not a listed water-delivery-time calculation", results)
            self.assertIn("Trim: ASSUMED (the kernel's assumption)", app.assumption_text.get())
            self.assertIn("30.0 s ASSUMED", app.assumption_text.get())
            self.assertEqual(app.project["last_run"]["source"], "tool-plan")
            self.assertEqual(app.chat_log[0]["role"], "user")
            self.assertEqual(app.chat_log[0]["text"], "/sample-di")
            self.assertEqual(app.chat_log[1]["role"], "assistant")
        finally:
            root.destroy()

    def test_sample_di_menu_runs_the_same_path(self):
        _isolate_data()

        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            # The menu row and the welcome link post the same action as /sample-di.
            app.start_sample_di()
            chat = app.thread_text()
            self.assertIn("/sample-di", chat)
            self.assertIn("5.0 gal trim ASSUMED", chat)
            self.assertEqual(len(app.segments), 4)
            self.assertIsNotNone(app.project["last_run"])
            self.assertIn("Zone total is", app.results_text)
        finally:
            root.destroy()

    def test_sample_di_seeds_its_own_thread_when_chosen(self):
        """Sample DI is optional. When chosen it opens its own job and says what it loaded."""
        _isolate_data()

        from fpfa.projects import load_project
        from fpfa.desk import sample_di_seed

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/help")
            first = app.project["id"]
            app.new_job()
            self.assertNotEqual(app.project["id"], first)
            root.update()
            # The welcome link runs the same starter as /sample-di.
            self.assertIn("sample-di", [link["action"] for link in app.snapshot()["welcome"]["links"]])
            app.start_sample_di()
            root.update()
            self.assertNotEqual(app.project["id"], first)
            self.assertEqual(app.project["name"], "Sample data hall DI zone")
            self.assertEqual(app.snapshot()["title"], "Sample data hall DI zone")
            reply = app.chat_log[1]["text"]
            self.assertTrue(reply.splitlines()[1].startswith("Sample loaded: data-hall double-interlock zone DH-1"))
            self.assertIn(sample_di_seed(), reply)
            self.assertIn("4 pipe segments", reply)
            self.assertIn("not a real building", reply)
            self.assertIn("Zone total is", reply)
            self.assertIn("5.0 gal trim ASSUMED", reply)
            self.assertEqual(app.zone_id.get(), "DH-1")
            self.assertEqual(app._seed_notes, {})
            # The earlier job keeps its own thread.
            self.assertEqual(
                [turn["text"] for turn in load_project(first)["chat"] if turn["role"] == "user"],
                ["/help"],
            )
            # A second run of the same zone is not labeled as a fresh sample.
            app.send_chat("/run")
            self.assertNotIn("Sample loaded", app.chat_log[-1]["text"])
            self.assertIn("Zone total is", app.chat_log[-1]["text"])
        finally:
            root.destroy()

    def test_chat_does_not_require_a_filled_zone_form(self):
        _isolate_data()

        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("hello")
            chat = app.thread_text()
            self.assertIn("hello", chat)
            self.assertIn("API key", chat)
            self.assertIn("/sample-di", chat)
            self.assertEqual(app.segments, [])
            self.assertIsNone(app.project.get("last_run"))
            app.send_chat("/help")
            self.assertIn("/sample-di —", app.thread_text())
            app.send_chat("/not-a-tool")
            self.assertIn("/not-a-tool is not a command", app.thread_text())
            app.send_chat("/run")
            self.assertIn("Add at least one pipe segment.", app.thread_text())
        finally:
            root.destroy()

    def test_ask_claude_returns_before_the_reply(self):
        _isolate_data()
        import threading
        import time
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
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

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                app.send_chat("Which trim family?")
                self.assertTrue(started.wait(2))
                self.assertNotIn("threaded reply", app.thread_text())
                self.assertIn("Asking", app.status.get())
                release.set()
                deadline = time.time() + 2
                while time.time() < deadline:
                    app._poll()
                    if "threaded reply" in app.thread_text():
                        break
                    time.sleep(0.02)
                self.assertIn("threaded reply", app.thread_text())
                self.assertIn("Which trim family?", app.thread_text())
        finally:
            root.destroy()

    def test_follow_up_send_includes_earlier_turns(self):
        _isolate_data()
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
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

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.AnthropicMessages", Fast):
                app.send_chat("Which trim family?")
                self._wait_for(app, "El/El holds the prime.")
                app.send_chat("explain that recommendation")
                self._wait_for(app, "That follows the first answer.")
            self.assertGreaterEqual(len(seen), 2)
            self.assertIn("Which trim family?", seen[1])
            self.assertIn("El/El holds the prime.", seen[1])
            self.assertIn("explain that recommendation", seen[1])
            self.assertIn("Earlier turns:", seen[1])
            # A job with a record is a team turn: the system text is the pack's lead role, the
            # specialists by slug, and the team paragraph. The lead does not wear a specialist's role.
            system = seen_meta[0]["system"]
            self.assertIn("# Team lead", system)
            self.assertIn("Specialists on this team.", system)
            self.assertIn("- fp-sprinkler:", system)
            self.assertNotIn("Call list_roles and read_role before you answer as that specialist.", system)
            self.assertEqual(seen_meta[1]["system"], system)
            self.assertEqual(seen_meta[0]["model"], "claude-opus-5-5")
            self.assertNotIn("tool_choice", seen_meta[0])
            self.assertNotIn("temperature", seen_meta[0])
            self.assertNotIn("top_p", seen_meta[0])
            self.assertNotIn("top_k", seen_meta[0])
            self.assertNotIn("thinking", seen_meta[0])
            names = [tool["name"] for tool in seen_meta[0]["tools"]]
            for name in (
                "read_skill",
                "read_mode",
                "list_modes",
                "zone_trapped_volume",
                "dry_delivery_screen",
                "di_trip_to_water",
                "elect_di_trim",
                "releasing_truth_table",
                "delegate",
                "set_input",
                "request_check",
            ):
                self.assertIn(name, names)
            self.assertNotIn("read_role", names, "the lead delegates to a specialist; it does not wear its role")
            self.assertIn("Active mode: mixed.", seen[0])
            self.assertIn("This mode may explore an option, quote a calc tool, and draft in the same reply.", seen_meta[0]["system"])
        finally:
            root.destroy()

    def test_implicit_project_keeps_the_optional_form(self):
        _isolate_data()

        from fpfa.projects import load_project
        
        root = Loop()
        try:
            app = root.open_desk()
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
            # Nothing on a new form is an input until the designer gives it. What has no hint is typed; the
            # hints are used (recorded ASSUMED).
            app.patch_form({
                "t_detect": "8", "t_release": "2", "t_exhaust": "0", "q_fill": "600", "base_area": "1500",
                "supervisory_psig": "40", "system_label": "Double-interlock", "hazard": "ordinary",
                "supervised": "yes", "qod": "no", "manual_station": "yes", "failsafe": "no",
                "length_label": "Center to center",
            })
            app.accept_hints()
            app.send_chat("/run")
            chat = app.thread_text()
            self.assertEqual(app.zone_id.get(), "KEEP-1")
            self.assertEqual(app.ahj.get(), "Kept AHJ")
            self.assertEqual(len(app.segments), 1)
            self.assertNotIn("Add at least one pipe segment.", chat)
            self.assertEqual(app.project["di"]["zone_id"], "KEEP-1")
            self.assertEqual(app.project["basis"]["ahj"], "Kept AHJ")
            self.assertEqual(len(app.project["di"]["segments"]), 1)
            self.assertIsNotNone(app.project.get("last_run"))
            self.assertIn("Trim: ASSUMED (the kernel's assumption)", app.assumption_text.get())
            saved = load_project(app.project["id"])
            self.assertEqual(saved["di"]["zone_id"], "KEEP-1")
            self.assertEqual(saved["basis"]["ahj"], "Kept AHJ")
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.zone_id.set("HELP-9")
            app.send_chat("/help")
            self.assertEqual(app.zone_id.get(), "HELP-9")
            self.assertEqual(app.project["di"]["zone_id"], "HELP-9")
            self.assertIn("/sample-di", app.thread_text())
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.zone_id.set("CHAT-1")
            app.send_chat("hello there")
            self.assertEqual(app.zone_id.get(), "CHAT-1")
            self.assertEqual(load_project(app.project["id"])["di"]["zone_id"], "CHAT-1")
            self.assertIn("hello there", app.thread_text())
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.zone_id.set("NAMED-1")
            app._slash_new("/new Hall zone", "Hall zone")
            self.assertEqual(app.project["name"], "Hall zone")
            self.assertEqual(app.zone_id.get(), "NAMED-1")
            self.assertEqual(app.project["di"]["zone_id"], "NAMED-1")
        finally:
            root.destroy()

    def test_close_and_ctrl_s_save_form_edits(self):
        _isolate_data()

        from fpfa.projects import list_projects, load_project, new_project
        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app._on_close()
            self.assertEqual(list_projects(), [])
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            origin = new_project("Close job")
            app.open_project(origin["id"])
            app.refresh_projects(origin["id"])
            app.zone_id.set("CLOSED-2")
            app.ahj.set("Close AHJ")
            # Choosing the open job again changes nothing.
            app.select_project(origin["id"])
            root.update()
            self.assertEqual(app.zone_id.get(), "CLOSED-2")
            app._on_close()
            saved = load_project(origin["id"])
            self.assertEqual(saved["di"]["zone_id"], "CLOSED-2")
            self.assertEqual(saved["basis"]["ahj"], "Close AHJ")
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.zone_id.set("KEY-3")
            # Ctrl+S in the page posts save.
            app.save_current()
            root.update()
            self.assertIsNotNone(app.project)
            self.assertEqual(app.zone_id.get(), "KEY-3")
            self.assertEqual(load_project(app.project["id"])["di"]["zone_id"], "KEY-3")
            self.assertIn("Saved", app.status.get())
        finally:
            root.destroy()

    def test_chat_does_not_replace_the_tool_plan(self):
        _isolate_data()
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        root = Loop()
        seen = []
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/sample-di")
            root.update()
            zone_gal = app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"]
            self.assertIn("281.3", app.results_text)
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

            with patch("fpfa.desk.AnthropicMessages", Fast):
                app.send_chat("revise the volume")
                self._wait_for(app, "I estimate about 40 gallons and 12 seconds.")
            self.assertEqual(app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"], zone_gal)
            self.assertIn("281.3", app.results_text)
            self.assertIn("5.0 gal trim ASSUMED", app.results_text)
            self.assertIn("Governing zone total text: 281.3.", seen[0])
            self.assertIn("38.1", seen[0])
            self.assertIn("5.0 gal trim ASSUMED", seen[0])
            self.assertIn("Earlier turns:", seen[0])
            self.assertIn("tool plan", app.status.get())
        finally:
            root.destroy()

    def test_local_zone_is_labeled_on_the_inbox(self):
        _isolate_data()
        from docx import Document

        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/sample-di")
            run = app.project["last_run"]
            job_id = run["job_id"]
            reply = app.chat_log[1]["text"]
            self.assertEqual(app.chat_log[1]["job_id"], job_id)
            self.assertIn(job_id, reply)
            self.assertIn("Sample data hall DI zone", reply)
            self.assertIn("| zone |", reply)
            self.assertIn("5.0 gal trim ASSUMED", reply)
            self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM", reply)
            self.assertTrue(run["narrative"].startswith("Zone "))
            self.assertNotIn(job_id, run["narrative"])
            self.assertEqual(run["source"], "tool-plan")
            inbox = "\n".join(app.inbox_lines)
            self.assertIn(job_id, inbox)
            self.assertIn("done", inbox)
            self.assertIn("zone", inbox)
            with tempfile.TemporaryDirectory() as tmp:
                written = app.export_to(Path(tmp) / "draft.docx", create=_support_every_claim())
                doc = Document(written)
                text = "\n".join(p.text for p in doc.paragraphs)
                self.assertIn("Section 21 13 19", text)
                self.assertNotIn(job_id, text)
                self.assertIn("| claim |", app.thread_text())
        finally:
            root.destroy()

    def test_failed_zone_stays_labeled_on_its_job(self):
        _isolate_data()

        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/run")
            reply = app.chat_log[-1]["text"]
            job_id = app.chat_log[-1]["job_id"]
            self.assertIn("Add at least one pipe segment.", reply)
            self.assertIn(job_id, reply)
            self.assertIn("| zone |", reply)
            self.assertIn("Untitled job", reply)
            inbox = "\n".join(app.inbox_lines)
            self.assertIn("error", inbox)
            self.assertIn(job_id, inbox)
        finally:
            root.destroy()

    def test_job_result_cannot_land_on_a_different_project(self):
        _isolate_data()

        from fpfa.projects import load_project, new_project
        
        result = {
            "source": "tool-plan",
            "narrative": "ORIGIN-RESULT",
            "warnings": [],
            "flags": [],
            "tools": {
                "zone_trapped_volume": {"zone_gal": 281.3, "trim_gal": 5, "trim_assumed": True},
                "di_trip_to_water": {
                    "t_total_s": 38.1,
                    "passes_screen": False,
                    "limit_s": 30,
                    "limit_basis": "FM",
                },
                "elect_di_trim": {"family": "El/El"},
            },
        }
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            origin = new_project("Origin job")
            other = new_project("Other job")
            app.open_project(other["id"])
            zone_job = app.jobs.record(
                project_id=origin["id"],
                project_name="Origin job",
                kind="zone",
                title="Zone tool plan",
                status="done",
            )
            chat_job = app.jobs.record(
                project_id=origin["id"],
                project_name="Origin job",
                kind="chat",
                title="Which trim?",
                status="done",
            )
            app._finish_run(other["id"], result, None, job_id=zone_job.id)
            app._finish_chat(other["id"], "ORIGIN-CHAT", job_id=chat_job.id)
            saved = load_project(origin["id"])
            self.assertEqual(saved["last_run"]["narrative"], "ORIGIN-RESULT")
            self.assertEqual(saved["last_run"]["job_id"], zone_job.id)
            self.assertIn(zone_job.id, saved["last_run"]["job_heading"])
            self.assertIn("Origin job", saved["last_run"]["job_heading"])
            texts = [turn["text"] for turn in saved["chat"]]
            self.assertTrue(any("ORIGIN-CHAT" in text and chat_job.id in text for text in texts))
            self.assertTrue(any(turn.get("job_id") == chat_job.id for turn in saved["chat"]))
            self.assertIsNone(load_project(other["id"]).get("last_run"))
            self.assertEqual(load_project(other["id"]).get("chat") or [], [])
            visible = app.thread_text()
            self.assertNotIn("ORIGIN-CHAT", visible)
            self.assertNotIn("ORIGIN-RESULT", app.results_text)
        finally:
            root.destroy()

    def test_composer_stays_usable_while_a_zone_job_runs(self):
        _isolate_data()
        import threading
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")
        zone_started = threading.Event()
        zone_release = threading.Event()
        zone_calls = {"n": 0}

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                content = kwargs["messages"][0]["content"]
                if "CHAT-WHILE-ZONE" in content:
                    return SimpleNamespace(
                        stop_reason="end_turn",
                        content=[SimpleNamespace(type="text", text="CHAT-WHILE-REPLY")],
                    )
                zone_calls["n"] += 1
                if zone_calls["n"] == 1:
                    zone_started.set()
                    zone_release.wait(5)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="zone narrative without the governing figures")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(True)
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                app.send_chat("/sample-di")
                self.assertTrue(zone_started.wait(3))
                self.assertNotIn("5.0 gal trim ASSUMED", app.thread_text())
                app.send_chat("CHAT-WHILE-ZONE")
                self._wait_for(app, "CHAT-WHILE-REPLY", timeout=3)
                mid = app.thread_text()
                self.assertIn("CHAT-WHILE-REPLY", mid)
                self.assertIn("| chat\n", mid)
                self.assertNotIn("5.0 gal trim ASSUMED", mid)
                zone_release.set()
                self._wait_for(app, "5.0 gal trim ASSUMED", timeout=3)
            thread = app.thread_text()
            self.assertIn("| zone |", thread)
            self.assertIn("| chat\n", thread)
            self.assertIn("CHAT-WHILE-REPLY", thread)
            self.assertIn("5.0 gal trim ASSUMED", thread)
            self.assertEqual(app.project["last_run"]["source"], "tool-plan")
            self.assertIn("281.3", f"{app.project['last_run']['tools']['zone_trapped_volume']['zone_gal']:.1f}")
            self.assertNotIn(app.project["last_run"]["job_id"], app.project["last_run"]["narrative"])
            inbox = "\n".join(app.inbox_lines)
            self.assertIn("zone", inbox)
            self.assertIn("chat", inbox)
            self.assertIn("Sample data hall DI zone", inbox)
        finally:
            zone_release.set()
            root.destroy()

    def test_out_of_order_replies_are_labeled_on_their_projects(self):
        _isolate_data()
        import threading
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import load_project
        
        save_api_key("sk-ant-local-test")
        slow_release = threading.Event()
        fast_release = threading.Event()
        slow_started = threading.Event()
        fast_started = threading.Event()

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                content = kwargs["messages"][0]["content"]
                if "FAST-QUESTION" in content:
                    fast_started.set()
                    if not fast_release.wait(5):
                        text = "FAST-TIMEOUT"
                    else:
                        text = "FAST-REPLY"
                elif "SLOW-QUESTION" in content:
                    slow_started.set()
                    if not slow_release.wait(5):
                        text = "SLOW-TIMEOUT"
                    else:
                        text = "SLOW-REPLY"
                else:
                    text = "OTHER-REPLY"
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text=text)],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                app._start_named_job("Alpha hall")
                alpha_id = app.project["id"]
                app.send_chat("SLOW-QUESTION")
                self.assertTrue(slow_started.wait(3))
                app.send_chat("FAST-QUESTION")
                self.assertTrue(fast_started.wait(3))
                fast_release.set()
                self._wait_for(app, "FAST-REPLY", timeout=3)
                early = app.thread_text()
                self.assertIn("FAST-REPLY", early)
                self.assertIn("| chat\n", early)
                self.assertNotIn("SLOW-REPLY", early)
                turns = [turn for turn in app.chat_log if turn.get("role") == "assistant"]
                self.assertEqual(len(turns), 1)
                self.assertIn("FAST-QUESTION", turns[0]["text"])
                self.assertIn(turns[0]["job_id"], turns[0]["text"])
                slow_release.set()
                self._wait_for(app, "SLOW-REPLY", timeout=3)
            visible = app.thread_text()
            self.assertIn("FAST-REPLY", visible)
            self.assertIn("SLOW-REPLY", visible)
            saved = load_project(alpha_id)
            assistant = [turn for turn in saved["chat"] if turn.get("role") == "assistant"]
            self.assertEqual(len(assistant), 2)
            self.assertIn("FAST-REPLY", assistant[0]["text"])
            self.assertIn("SLOW-REPLY", assistant[1]["text"])
            self.assertNotEqual(assistant[0]["job_id"], assistant[1]["job_id"])
            self.assertIn(assistant[0]["job_id"], assistant[0]["text"])
            self.assertIn("Alpha hall", assistant[0]["text"])
            self.assertIn("Alpha hall", assistant[1]["text"])
            self.assertIsNone(saved.get("last_run"))
        finally:
            slow_release.set()
            fast_release.set()
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                slow_release.clear()
                fast_release.clear()
                slow_started.clear()
                fast_started.clear()
                app._start_named_job("Alpha hall")
                alpha_id = app.project["id"]
                app.send_chat("SLOW-QUESTION")
                self.assertTrue(slow_started.wait(3))
                app._start_named_job("Beta hall")
                beta_id = app.project["id"]
                self.assertNotEqual(alpha_id, beta_id)
                app.send_chat("FAST-QUESTION")
                self.assertTrue(fast_started.wait(3))
                fast_release.set()
                self._wait_for(app, "FAST-REPLY", timeout=3)
                on_beta = app.thread_text()
                self.assertIn("FAST-REPLY", on_beta)
                self.assertIn("Beta hall", on_beta)
                self.assertNotIn("SLOW-REPLY", on_beta)
                self.assertNotIn("Alpha hall", on_beta)
                alpha_saved = load_project(alpha_id)
                alpha_text = "\n".join(turn.get("text") or "" for turn in alpha_saved["chat"])
                self.assertIn("SLOW-QUESTION", alpha_text)
                self.assertNotIn("FAST-REPLY", alpha_text)
                slow_release.set()
                deadline_hit = False
                import time
                deadline = time.time() + 3
                while time.time() < deadline:
                    app._poll()
                    alpha_saved = load_project(alpha_id)
                    blob = "\n".join(turn.get("text") or "" for turn in alpha_saved.get("chat") or [])
                    if "SLOW-REPLY" in blob:
                        deadline_hit = True
                        break
                    time.sleep(0.02)
                self.assertTrue(deadline_hit)
            alpha_saved = load_project(alpha_id)
            beta_saved = load_project(beta_id)
            alpha_text = "\n".join(turn.get("text") or "" for turn in alpha_saved["chat"])
            beta_text = "\n".join(turn.get("text") or "" for turn in beta_saved["chat"])
            self.assertIn("SLOW-REPLY", alpha_text)
            self.assertIn("Alpha hall", alpha_text)
            self.assertNotIn("FAST-REPLY", alpha_text)
            self.assertIn("FAST-REPLY", beta_text)
            self.assertIn("Beta hall", beta_text)
            self.assertNotIn("SLOW-REPLY", beta_text)
            self.assertNotIn("SLOW-REPLY", app.thread_text())
            self.assertNotIn("Alpha hall", app.thread_text())
        finally:
            slow_release.set()
            fast_release.set()
            root.destroy()

    def _zone_result(self, narrative: str) -> dict:
        return {
            "source": "tool-plan",
            "narrative": narrative,
            "warnings": [],
            "flags": [],
            "tools": {
                "zone_trapped_volume": {"zone_gal": 12.0, "trim_gal": 5, "trim_assumed": True},
                "di_trip_to_water": {
                    "t_total_s": 10.0,
                    "passes_screen": True,
                    "limit_s": 60,
                    "limit_basis": "FM",
                },
                "elect_di_trim": {"family": "El/El"},
            },
        }

    def _prepare_zone_form(self, app, name: str) -> str:
        app._start_named_job(name)
        app._insert_segment({
            "role": "branch",
            "nps": "1",
            "schedule": "sch40",
            "length_ft": 10,
            "d_in": 1.049,
        })
        app.ask_claude.set(True)
        return app.project["id"]

    def _hold_overlapping_runs(self, app, on_second):
        """Prepare two /run jobs that block inside the zone call.

        Call the returned start function after the patch is active. The first
        job returns a labeled result. on_second() supplies the second outcome
        and may return a result or raise.
        """
        import threading
        from unittest.mock import patch

        entered = [threading.Event(), threading.Event()]
        release = [threading.Event(), threading.Event()]
        state = {"n": 0}
        lock = threading.Lock()

        def fake_zone(_pack, _di, _basis, narrator=None, mode=None, **_kwargs):
            # The window also passes record= and project_id=. This stand-in ignores them.
            with lock:
                index = state["n"]
                state["n"] += 1
            if index > 1:
                raise AssertionError("unexpected extra zone run")
            entered[index].set()
            if not release[index].wait(5):
                raise TimeoutError("zone run was not released")
            if index == 0:
                return self._zone_result("FIRST-ZONE-RESULT")
            return on_second()

        def start():
            app.send_chat("/run")
            self.assertTrue(entered[0].wait(3), "first zone run did not start")
            app.send_chat("/run")
            self.assertTrue(entered[1].wait(3), "second zone run did not start")
            jobs = [job for job in app.jobs.snapshot() if job.kind == "zone"]
            self.assertEqual(len(jobs), 2)
            self.assertEqual(app.jobs.get(jobs[1].id).status, "running")
            return jobs

        return patch("fpfa.desk.run_di_zone", fake_zone), entered, release, start

    def test_overlapping_zone_runs_each_post_a_labeled_result(self):
        """Two /run jobs on one project each add their own labeled result."""
        _isolate_data()

        from fpfa.keystore import save_api_key
        from fpfa.projects import load_project
        
        save_api_key("sk-ant-local-test")
        root = Loop()
        patcher = None
        patch_started = False
        release = [None, None]
        try:
            app = root.open_desk()
            root.update()
            origin_id = self._prepare_zone_form(app, "Overlap hall")
            patcher, _entered, release, start = self._hold_overlapping_runs(
                app, lambda: self._zone_result("SECOND-ZONE-RESULT")
            )
            patcher.start()
            patch_started = True
            jobs = start()
            release[0].set()
            self._wait_for(app, "FIRST-ZONE-RESULT", timeout=3)
            mid = app.thread_text()
            self.assertIn("FIRST-ZONE-RESULT", mid)
            self.assertIn(jobs[0].id, mid)
            self.assertNotIn("SECOND-ZONE-RESULT", mid)
            self.assertNotIn(jobs[1].id, mid)
            release[1].set()
            self._wait_for(app, "SECOND-ZONE-RESULT", timeout=3)
            saved = load_project(origin_id)
            assistant = [turn for turn in saved["chat"] if turn.get("role") == "assistant"]
            self.assertEqual(len(assistant), 2)
            self.assertEqual(assistant[0]["job_id"], jobs[0].id)
            self.assertEqual(assistant[1]["job_id"], jobs[1].id)
            self.assertNotEqual(assistant[0]["job_id"], assistant[1]["job_id"])
            self.assertIn("FIRST-ZONE-RESULT", assistant[0]["text"])
            self.assertIn(jobs[0].id, assistant[0]["text"])
            self.assertIn("Overlap hall", assistant[0]["text"])
            self.assertIn("| zone |", assistant[0]["text"])
            self.assertNotIn(jobs[1].id, assistant[0]["text"])
            self.assertIn("SECOND-ZONE-RESULT", assistant[1]["text"])
            self.assertIn(jobs[1].id, assistant[1]["text"])
            self.assertIn("Overlap hall", assistant[1]["text"])
            self.assertIn("| zone |", assistant[1]["text"])
            self.assertNotIn(jobs[0].id, assistant[1]["text"])
            visible = app.thread_text()
            self.assertIn("FIRST-ZONE-RESULT", visible)
            self.assertIn("SECOND-ZONE-RESULT", visible)
        finally:
            for event in release:
                if event is not None:
                    event.set()
            if patch_started:
                patcher.stop()
            root.destroy()

    def test_zone_error_after_project_switch_is_saved_on_that_project(self):
        """A second overlapping /run that fails after a switch still lands on its project."""
        _isolate_data()
        import time
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import load_project
        
        save_api_key("sk-ant-local-test")
        root = Loop()
        patcher = None
        patch_started = False
        release = [None, None]
        try:
            app = root.open_desk()
            root.update()
            origin_id = self._prepare_zone_form(app, "Overlap hall")

            def fail_second():
                raise RuntimeError("SECOND-ZONE-FAILED")

            patcher, _entered, release, start = self._hold_overlapping_runs(app, fail_second)
            app.notices.clear()
            if True:
                patcher.start()
                patch_started = True
                jobs = start()
                release[0].set()
                self._wait_for(app, "FIRST-ZONE-RESULT", timeout=3)
                self.assertNotIn("SECOND-ZONE-FAILED", app.thread_text())
                app._start_named_job("Other hall")
                other_id = app.project["id"]
                self.assertNotEqual(other_id, origin_id)
                self.assertNotIn("FIRST-ZONE-RESULT", app.thread_text())
                release[1].set()
                deadline = time.time() + 3
                saved_text = ""
                while time.time() < deadline:
                    app._poll()
                    saved = load_project(origin_id)
                    saved_text = "\n".join(turn.get("text") or "" for turn in saved.get("chat") or [])
                    if "SECOND-ZONE-FAILED" in saved_text:
                        break
                    time.sleep(0.02)
                self.assertIn("SECOND-ZONE-FAILED", saved_text)
                # No dialog: the error went to the thread of the job that started the run.
                self.assertEqual(app.notices, [])
            saved = load_project(origin_id)
            assistant = [turn for turn in saved["chat"] if turn.get("role") == "assistant"]
            self.assertEqual(len(assistant), 2)
            self.assertEqual(assistant[0]["job_id"], jobs[0].id)
            self.assertIn("FIRST-ZONE-RESULT", assistant[0]["text"])
            self.assertIn(jobs[0].id, assistant[0]["text"])
            self.assertEqual(assistant[1]["job_id"], jobs[1].id)
            self.assertIn("SECOND-ZONE-FAILED", assistant[1]["text"])
            self.assertIn("RuntimeError", assistant[1]["text"])
            self.assertIn(jobs[1].id, assistant[1]["text"])
            self.assertIn("Overlap hall", assistant[1]["text"])
            self.assertIn("| zone |", assistant[1]["text"])
            self.assertNotIn(jobs[0].id, assistant[1]["text"])
            self.assertNotIn("Other hall", assistant[1]["text"])
            other = load_project(other_id)
            other_text = "\n".join(turn.get("text") or "" for turn in other.get("chat") or [])
            self.assertNotIn("SECOND-ZONE-FAILED", other_text)
            self.assertNotIn("FIRST-ZONE-RESULT", other_text)
            self.assertNotIn("SECOND-ZONE-FAILED", app.thread_text())
            app.open_project(origin_id)
            reopened = app.thread_text()
            self.assertIn("FIRST-ZONE-RESULT", reopened)
            self.assertIn("SECOND-ZONE-FAILED", reopened)
            self.assertIn(jobs[1].id, reopened)
            self.assertEqual(app.jobs.get(jobs[1].id).status, "error")
        finally:
            for event in release:
                if event is not None:
                    event.set()
            if patch_started:
                patcher.stop()
            root.destroy()

    def _wait_for(self, app, needle: str, timeout: float = 2.0) -> None:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.thread_text():
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")


class JobInboxTests(unittest.TestCase):
    def test_submit_returns_while_a_worker_is_busy(self):
        import threading
        import time

        from fpfa.jobs import JobInbox, label_result

        inbox = JobInbox(worker_count=1)
        started = threading.Event()
        release = threading.Event()
        second_ran = threading.Event()
        seen = {}

        def slow(_job_id):
            seen["thread"] = threading.current_thread().name
            started.set()
            release.wait(3)

        def later(_job_id):
            second_ran.set()

        try:
            first = inbox.submit(
                project_id="p-slow",
                project_name="Slow job",
                kind="zone",
                title="Zone tool plan",
                work=slow,
            )
            self.assertTrue(started.wait(2))
            began = time.perf_counter()
            second = inbox.submit(
                project_id="p-fast",
                project_name="Fast job",
                kind="chat",
                title="a follow up",
                work=later,
            )
            self.assertLess(time.perf_counter() - began, 0.4)
            self.assertEqual(inbox.get(second.id).status, "queued")
            self.assertEqual(inbox.get(first.id).status, "running")
            self.assertFalse(second_ran.is_set())
            self.assertTrue(seen["thread"].startswith("fpfa-worker-"))
            self.assertNotEqual(seen["thread"], threading.current_thread().name)
            release.set()
            self.assertTrue(second_ran.wait(2))
            deadline = time.time() + 2
            while time.time() < deadline and inbox.get(second.id).status != "done":
                time.sleep(0.01)
            self.assertEqual(inbox.get(first.id).status, "done")
            self.assertEqual(inbox.get(second.id).status, "done")
            slow_label = label_result(inbox.get(first.id).heading(), "SLOW-BODY")
            fast_label = label_result(inbox.get(second.id).heading(), "FAST-BODY")
            self.assertIn(first.id, slow_label)
            self.assertIn("Slow job", slow_label)
            self.assertIn("| zone |", slow_label)
            self.assertNotIn("Fast job", slow_label)
            self.assertNotIn(second.id, slow_label)
            self.assertIn(second.id, fast_label)
            self.assertIn("Fast job", fast_label)
            self.assertIn("| chat |", fast_label)
            self.assertNotIn("Slow job", fast_label)
            lines = [job.inbox_line() for job in inbox.snapshot()]
            self.assertEqual(len(lines), 2)
            self.assertIn(first.id, lines[0])
            self.assertIn(second.id, lines[1])
        finally:
            release.set()
            inbox.close()

    def test_worker_error_scrubs_an_api_key(self):
        import time

        from fpfa.jobs import JobInbox

        inbox = JobInbox(worker_count=1)

        def boom(_job_id):
            raise RuntimeError("network down sk-ant-secretvalue")

        try:
            job = inbox.submit(
                project_id="p1",
                project_name="Key job",
                kind="chat",
                title="ask",
                work=boom,
            )
            deadline = time.time() + 2
            while time.time() < deadline and inbox.get(job.id).status != "error":
                time.sleep(0.01)
            saved = inbox.get(job.id)
            self.assertEqual(saved.status, "error")
            self.assertNotIn("sk-ant-secretvalue", saved.error)
            self.assertIn("[key]", saved.error)
        finally:
            inbox.close()

    def test_closed_inbox_rejects_new_work(self):
        from fpfa.jobs import JobInbox

        inbox = JobInbox(worker_count=1)
        inbox.close()
        with self.assertRaises(RuntimeError):
            inbox.submit(
                project_id="p1",
                project_name="Late",
                kind="chat",
                title="late",
                work=lambda _job_id: None,
            )


class BessStarterTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root

        self.root = content_root()

    def test_starter_quotes_the_lfl_tool_and_labels_the_open_points(self):
        from fpfa.bess import BESS_SKILL, run_bess_plan
        from fpfa.sample_data import EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.skills_loader import read_starter_cites
        from fpfa.workflow import run_di_zone

        cites = read_starter_cites(self.root, BESS_SKILL)
        self.assertEqual([screen["pct"] for screen in cites["screens"]], [25.0, 25.0, 10.0])
        result = run_bess_plan(self.root, EXAMPLE_BESS, EXAMPLE_BESS_BASIS)
        tool = result["tools"]["lfl_setpoints"]
        self.assertIsNone(tool["election"])
        self.assertIsNone(tool["duration"])
        self.assertAlmostEqual(tool["lfl_fuel_vol_pct"], 4.11, places=2)
        self.assertAlmostEqual(tool["lfl_diluted_vol_pct"], 5.26, places=2)
        self.assertEqual(result["source"], "tool-plan")
        self.assertEqual(result["mode"], "synthesis")
        self.assertTrue(result["narrative_checks"]["quotes_all"])
        narrative = result["narrative"]
        self.assertIn("Mixture LFL 4.11 vol% is calculated (fuel-only).", narrative)
        self.assertIn("Mixture LFL with diluent 5.26 vol% is calculated.", narrative)
        self.assertIn("Edition year ASSUMED unpinned for NFPA 69 8.3.1.", narrative)
        self.assertIn("NFPA 855-2023 9.6.5.6.7(1)", narrative)
        self.assertIn("NFPA 855-2023 9.6.5.6.7(4)", narrative)
        self.assertIn("Explosion-control election ASSUMED:", narrative)
        self.assertIn("No tool returned an election.", narrative)
        self.assertIn("Duration ASSUMED: 24 h standby and 2 h alarm", narrative)
        self.assertIn("No tool returned a duration.", narrative)
        self.assertIn("does not elect foam", narrative)
        self.assertIn("use best judgment", narrative)
        self.assertIn("did not invent gallons or seconds", narrative)
        self.assertNotIn("21 13 16", narrative)
        self.assertNotIn("election is calculated", narrative.lower())
        self.assertNotIn("duration is calculated", narrative.lower())
        zone = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS)
        self.assertIn("281.3", zone["narrative"])
        self.assertIn("38.1", zone["narrative"])
        before = zone["tools"]["zone_trapped_volume"]["zone_gal"]
        joined = run_bess_plan(
            self.root, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, zone_result=zone
        )
        self.assertIn(
            "Zone total 281.3 gal and t_total 38.1 s stay on the zone tool plan.",
            joined["narrative"],
        )
        self.assertNotIn("did not invent gallons", joined["narrative"])
        self.assertEqual(zone["tools"]["zone_trapped_volume"]["zone_gal"], before)
        self.assertAlmostEqual(before, 281.3, places=1)
        from fpfa.desk import chat_request_text

        follow = chat_request_text([], {}, {}, "revise the setpoint", zone, "synthesis", joined)
        self.assertIn("Mixture LFL 4.11 vol% is calculated (fuel-only).", follow)
        self.assertIn("Governing zone total text: 281.3.", follow)
        self.assertIn("An explosion-control tool plan already ran.", follow)
        self.assertIn("No tool returned an election.", follow)

    def test_model_draft_is_kept_only_when_it_quotes_the_tool_plan(self):
        from fpfa.bess import run_bess_plan
        from fpfa.everyday import assemble_system
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_BESS, EXAMPLE_BESS_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        zone = run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS)
        seen = {}

        def agree(system, user, _tools, _execute):
            seen["system"] = system
            seen["user"] = user
            return {"text": user, "tool_calls": []}

        kept = run_bess_plan(
            self.root,
            EXAMPLE_BESS,
            EXAMPLE_BESS_BASIS,
            zone_result=zone,
            narrator=agree,
            mode="synthesis",
        )
        self.assertEqual(kept["source"], "claude")
        self.assertIn("281.3", kept["narrative"])
        self.assertIn("38.1", kept["narrative"])
        self.assertIn("Active mode: synthesis.", seen["user"])
        self.assertNotIn("The desktop starter reads the starter block", seen["user"])
        self.assertIn(
            "An explosion-control starter quotes the LFL tool plan and does not recompute it.",
            seen["system"],
        )
        self.assertEqual(seen["system"], assemble_system(self.root, "synthesis"))
        self.assertNotIn("8.3.1", seen["system"])

        def disagree(_system, _user, _tools, _execute):
            return {
                "text": "Mixture LFL is 9.99 vol%. Zone total 999.0 gal. t_total 1.0 s.",
                "tool_calls": [],
            }

        rejected = run_bess_plan(
            self.root,
            EXAMPLE_BESS,
            EXAMPLE_BESS_BASIS,
            zone_result=zone,
            narrator=disagree,
        )
        self.assertEqual(rejected["source"], "tool-plan")
        head, _, tail = rejected["narrative"].partition("Model draft")
        self.assertIn("4.11", head)
        self.assertIn("281.3", head)
        self.assertIn("38.1", head)
        self.assertNotIn("999.0", head)
        self.assertIn("9.99", tail)
        self.assertTrue(any("did not quote the LFL tool plan" in item for item in rejected["warnings"]))

    def test_method_stays_in_the_skill_file(self):
        from fpfa.skills_loader import read_starter_cites

        body = (REPO / "skills" / "ess-isolation-venting-and-duration" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("The desktop starter reads the starter block in this file", body)
        cites = read_starter_cites(self.root, "ess-isolation-venting-and-duration")
        self.assertEqual(cites["election"]["value"], "combustible concentration reduction")
        self.assertIn("24 h standby", cites["duration"]["value"])
        banned = ("8.3.1", "9.6.5.6.7", "NFPA 69", "The desktop starter reads the starter block", "does not elect foam")
        for path in (REPO / "app" / "fpfa").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in banned:
                self.assertNotIn(token, text, path.name)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "skills" / "ess-isolation-venting-and-duration"
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n\nno block\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_starter_cites(root, "ess-isolation-venting-and-duration")
            (folder / "SKILL.md").write_text(
                "---\nname: x\ndescription: y\n---\n\n```starter\n"
                "screen: only\nbasis: diluted\nsection: somewhere\n"
                "election: a method\nduration: some hours\n```\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                read_starter_cites(root, "ess-isolation-venting-and-duration")

    def test_sample_bess_slash_and_chip_run_the_starter(self):

        from fpfa.projects import load_project
        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/help")
            app.density.set("not-a-number")
            old_id = app.project["id"]
            app.send_chat("/sample-bess")
            chat = app.thread_text()
            self.assertIn("/sample-bess", chat)
            self.assertIn("Mixture LFL 4.11 vol% is calculated (fuel-only).", chat)
            self.assertIn("Explosion-control election ASSUMED:", chat)
            self.assertIn("Duration ASSUMED:", chat)
            self.assertIn("Edition year ASSUMED unpinned", chat)
            self.assertIn("| bess |", chat)
            self.assertEqual(app.project["bess_run"]["mode"], "synthesis")
            self.assertNotIn("mode", app.project)
            self.assertEqual(app.project["name"], "Sample Li-ion BESS room")
            self.assertIsNone(app.project.get("last_run"))
            self.assertEqual(app.project["bess_run"]["source"], "tool-plan")
            self.assertEqual(app.project["bess_run"]["kind"], "bess")
            self.assertEqual(app.segments, [])
            self.assertIn("NFPA 69 8.3.1", app.results_text)
            saved_old = load_project(old_id)
            self.assertNotIn("not-a-number", json.dumps(saved_old.get("di")))
            kinds = [job.kind for job in app.jobs.snapshot()]
            self.assertIn("bess", kinds)
        finally:
            root.destroy()

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            # The menu row posts the same action as /sample-bess.
            app.start_sample_bess()
            chat = app.thread_text()
            self.assertIn("/sample-bess", chat)
            self.assertIn("4.11", chat)
            self.assertEqual(app.project["bess_run"]["mode"], "synthesis")
            self.assertIsNone(app.project.get("last_run"))
        finally:
            root.destroy()

    def test_bess_job_that_calls_claude_stays_off_the_ui_thread(self):
        import threading
        import time
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")
        started = threading.Event()
        release = threading.Event()
        seen = []

        class Blocking:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen.append(kwargs)
                started.set()
                release.wait(3)
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="short draft without the tool figures")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(True)
            with patch("fpfa.desk.AnthropicMessages", Blocking):
                app.send_chat("/sample-bess")
                self.assertTrue(started.wait(2))
                self.assertNotIn("4.11", app.thread_text())
                self.assertEqual(seen[0]["model"], "claude-opus-5-5")
                self.assertNotIn("tool_choice", seen[0])
                self.assertNotIn("temperature", seen[0])
                self.assertNotIn("top_p", seen[0])
                self.assertNotIn("top_k", seen[0])
                self.assertNotIn("thinking", seen[0])
                release.set()
                deadline = time.time() + 2
                while time.time() < deadline:
                    app._poll()
                    if "4.11" in app.thread_text():
                        break
                    time.sleep(0.02)
            chat = app.thread_text()
            self.assertIn("4.11", chat)
            self.assertIn("| bess |", chat)
            self.assertIn("did not quote the LFL tool plan", app.results_text)
            self.assertIsNone(app.project.get("last_run"))
            self.assertEqual(app.project["bess_run"]["source"], "tool-plan")
        finally:
            release.set()
            root.destroy()


class ManagedAgentTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()

    def tearDown(self):
        from fpfa.managed import release_active_sessions

        release_active_sessions()

    def _request(self, events, session_status="running"):
        calls = []

        def request(method, path, body):
            calls.append((method, path, body))
            if method == "POST" and path == "/v1/environments":
                return {"id": "env_test"}
            if method == "POST" and path == "/v1/agents":
                return {"id": "agent_test"}
            if method == "POST" and path == "/v1/sessions":
                return {"id": "sess_test", "status": "running"}
            if method == "GET" and "/events" in path:
                return {"data": events, "next_page": None}
            if method == "GET" and path == "/v1/sessions/sess_test":
                return {"id": "sess_test", "status": session_status}
            if method == "DELETE" and path == "/v1/sessions/sess_test":
                return {}
            raise AssertionError((method, path))

        return calls, request

    def test_heavy_job_uses_one_cloud_session_and_returns_its_text(self):
        from fpfa.claude_client import MODEL_ID
        from fpfa.managed import (
            HEAVY_NOTE,
            HEAVY_TEXT_ONLY,
            MODEL_ID as managed_model,
            run_heavy_job,
            session_system,
        )

        self.assertEqual(managed_model, "claude-opus-5-5")
        prompt = session_system()
        self.assertIn(HEAVY_TEXT_ONLY, prompt)
        # Canada is in scope through a skill's Country gate, not refused as a path; this session cannot read one.
        self.assertNotIn("Canadian path", HEAVY_TEXT_ONLY)
        self.assertIn("only through a skill's Country gate", HEAVY_TEXT_ONLY)
        self.assertIn("NEEDS HOLD", HEAVY_TEXT_ONLY)
        self.assertIn(HEAVY_NOTE, prompt)
        self.assertNotIn("Call read_role", prompt)
        self.assertNotIn("Call read_skill", prompt)
        self.assertNotIn("Call read_mode", prompt)
        events = [
            {
                "type": "agent.message",
                "processed_at": "2026-10-27T00:00:02Z",
                "content": [{"type": "text", "text": "SECOND"}],
            },
            {
                "type": "agent.message",
                "processed_at": "2026-10-27T00:00:01Z",
                "content": [{"type": "text", "text": "FIRST"}],
            },
            {
                "type": "session.status_idle",
                "processed_at": "2026-10-27T00:00:03Z",
                "stop_reason": {"type": "end_turn"},
            },
        ]
        calls, request = self._request(events)
        resources = {}
        out = run_heavy_job(
            request,
            system=prompt,
            user_text="check the room",
            resources=resources,
        )
        self.assertEqual(out["text"], "FIRST\nSECOND")
        self.assertEqual(out["model"], MODEL_ID)
        self.assertEqual(out["runtime"], "managed-agents")
        self.assertNotIn("sess_test", out["text"])
        self.assertTrue(out["session_delete"]["ok"])
        self.assertEqual(out["session_delete"]["session_id"], "sess_test")
        self.assertEqual(out["session_delete"]["error"], "")
        posts = [call for call in calls if call[0] == "POST" and call[1] == "/v1/sessions"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(sum(1 for call in calls if call[0] == "DELETE"), 1)
        self.assertFalse(any(call[1].startswith("/v1/messages") for call in calls))
        session = posts[0][2]
        self.assertEqual(set(session), {"agent", "environment_id", "initial_events"})
        self.assertEqual(session["agent"]["model"], {"id": "claude-opus-5-5"})
        self.assertEqual(session["agent"]["type"], "agent_with_overrides")
        self.assertEqual(session["agent"]["system"], prompt)
        self.assertIn("text-only reasoning on the already-computed zone packet", session["agent"]["system"])
        self.assertIn(HEAVY_NOTE, session["agent"]["system"])
        self.assertNotIn("Call read_role", session["agent"]["system"])
        self.assertNotIn("Call read_skill", session["agent"]["system"])
        self.assertNotIn("Call read_mode", session["agent"]["system"])
        self.assertNotIn("You are the design assistant", session["agent"]["system"])
        self.assertEqual(len(session["initial_events"]), 1)
        self.assertEqual(session["initial_events"][0]["type"], "user.message")
        self.assertNotIn("multiagent", session)
        env = next(call[2] for call in calls if call[1] == "/v1/environments")
        self.assertEqual(env["config"]["type"], "cloud")
        self.assertEqual(env["config"]["networking"]["type"], "limited")
        self.assertNotIn("unrestricted", json.dumps(env))
        agent = next(call[2] for call in calls if call[1] == "/v1/agents")
        self.assertEqual(agent["model"], "claude-opus-5-5")
        self.assertEqual(agent["system"], prompt)
        self.assertEqual(set(agent), {"name", "model", "system", "tools"})
        toolset = agent["tools"][0]
        self.assertEqual(toolset["default_config"]["enabled"], False)
        enabled = {item["name"] for item in toolset["configs"] if item.get("enabled")}
        self.assertNotIn("web_search", enabled)
        self.assertNotIn("web_fetch", enabled)
        wire = json.dumps([call[2] for call in calls if call[2] is not None])
        for banned in ("temperature", "top_p", "top_k", "tool_choice", "thinking"):
            self.assertNotIn(f'"{banned}"', wire)
        calls.clear()
        again = run_heavy_job(
            request,
            system=prompt,
            user_text="next check",
            resources=resources,
        )
        self.assertEqual(again["text"], "FIRST\nSECOND")
        self.assertFalse(any(call[1] == "/v1/agents" for call in calls))
        self.assertFalse(any(call[1] == "/v1/environments" for call in calls))
        self.assertEqual(sum(1 for call in calls if call[0] == "POST" and call[1] == "/v1/sessions"), 1)

    def test_paused_hosted_run_is_not_continued_as_another_conversation(self):
        from fpfa.managed import run_heavy_job

        events = [
            {
                "type": "agent.message",
                "content": [{"type": "text", "text": "partial"}],
            },
            {
                "type": "session.status_idle",
                "stop_reason": {"type": "requires_action"},
            },
        ]
        calls, request = self._request(events)
        with self.assertRaises(RuntimeError) as caught:
            run_heavy_job(request, user_text="check the room")
        self.assertIn("no second conversation", str(caught.exception))
        self.assertNotIn("partial", str(caught.exception))
        self.assertEqual(sum(1 for call in calls if call[0] == "POST" and call[1] == "/v1/sessions"), 1)
        self.assertEqual(sum(1 for call in calls if call[0] == "DELETE"), 1)
        self.assertFalse(any(call[0] == "POST" and call[1].endswith("/events") for call in calls))

    def test_timeout_deletes_the_session(self):
        from fpfa.managed import run_heavy_job

        calls, request = self._request([])
        sleeps = []
        with self.assertRaises(RuntimeError) as caught:
            run_heavy_job(
                request,
                user_text="check the room",
                sleep=lambda seconds: sleeps.append(seconds),
                max_polls=2,
                poll_seconds=5,
            )
        self.assertIn("did not finish", str(caught.exception))
        self.assertEqual(sleeps, [5])
        self.assertEqual(sum(1 for call in calls if call[0] == "DELETE"), 1)
        self.assertEqual(sum(1 for call in calls if call[0] == "POST" and call[1] == "/v1/sessions"), 1)

    def test_hosted_error_scrubs_an_api_key(self):
        from fpfa.managed import anthropic_request, run_heavy_job

        secret = "sk-ant-" + "abc123secret"

        def request(method, path, body):
            raise RuntimeError(f"upstream {secret}")

        with self.assertRaises(RuntimeError) as caught:
            run_heavy_job(request, user_text="check the room")
        self.assertNotIn(secret, str(caught.exception))
        self.assertIn("[key]", str(caught.exception))

        import io
        import urllib.error

        seen = {}

        def opener(req, timeout=120):
            seen["beta"] = req.get_header("Anthropic-beta")
            seen["version"] = req.get_header("Anthropic-version")
            seen["key"] = req.get_header("X-api-key")
            seen["timeout"] = timeout
            raise urllib.error.HTTPError(
                req.full_url,
                400,
                "bad",
                hdrs=None,
                fp=io.BytesIO(f'{{"error":"{secret}"}}'.encode("utf-8")),
            )

        client = anthropic_request("sk-ant-local-test", opener=opener)
        with self.assertRaises(RuntimeError) as http_caught:
            client("POST", "/v1/sessions", {"agent": "agent_test"})
        self.assertEqual(seen["beta"], "managed-agents-2026-04-01")
        self.assertEqual(seen["version"], "2023-06-01")
        self.assertEqual(seen["key"], "sk-ant-local-test")
        self.assertEqual(seen["timeout"], 120)
        self.assertNotIn(secret, str(http_caught.exception))
        self.assertIn("[key]", str(http_caught.exception))

        def refuse(req, timeout=120):
            raise AssertionError("network")

        blocked = anthropic_request("sk-ant-local-test", opener=refuse)
        with self.assertRaises(ValueError):
            blocked("POST", "/v1/agents", {"temperature": 0, "tool_choice": {"type": "any"}, "thinking": {"type": "disabled"}})
        with self.assertRaises(RuntimeError) as messages:
            blocked("POST", "/v1/messages", None)
        self.assertIn("Messages API", str(messages.exception))

    def test_everyday_system_text_is_not_sent_on_the_hosted_path(self):
        from fpfa.everyday import assemble_system
        from fpfa.managed import run_heavy_job
        from fpfa.paths import content_root

        calls = []

        def request(method, path, body):
            calls.append(path)
            raise AssertionError((method, path))

        with self.assertRaises(ValueError) as caught:
            run_heavy_job(
                request,
                system=assemble_system(content_root(), "mixed"),
                user_text="check the room",
            )
        self.assertIn("text-only", str(caught.exception))
        self.assertEqual(calls, [])

    def test_failed_session_delete_is_visible_and_can_be_retried(self):
        from fpfa.managed import (
            DELETE_FAILURE_NOTE,
            active_session_ids,
            delete_active_sessions,
            reply_with_delete_status,
            run_heavy_job,
        )

        events = [
            {
                "type": "agent.message",
                "content": [{"type": "text", "text": "HEAVY-REPLY"}],
            },
            {
                "type": "session.status_idle",
                "stop_reason": {"type": "end_turn"},
            },
        ]
        secret = "sk-ant-" + "abc123secret"
        deletes = {"n": 0}

        def request(method, path, body):
            if method == "POST" and path == "/v1/environments":
                return {"id": "env_test"}
            if method == "POST" and path == "/v1/agents":
                return {"id": "agent_test"}
            if method == "POST" and path == "/v1/sessions":
                return {"id": "sess_leak", "status": "running"}
            if method == "GET" and "/events" in path:
                return {"data": events, "next_page": None}
            if method == "GET" and path == "/v1/sessions/sess_leak":
                return {"id": "sess_leak", "status": "idle"}
            if method == "DELETE" and path == "/v1/sessions/sess_leak":
                deletes["n"] += 1
                if deletes["n"] == 1:
                    raise RuntimeError(f"network down {secret}")
                return {}
            raise AssertionError((method, path))

        with self.assertLogs("fpfa.managed", level="ERROR") as captured:
            out = run_heavy_job(request, user_text="check the room", sleep=lambda _seconds: None)
        self.assertEqual(out["text"], "HEAVY-REPLY")
        self.assertFalse(out["session_delete"]["ok"])
        self.assertEqual(out["session_delete"]["session_id"], "sess_leak")
        self.assertIn("network down", out["session_delete"]["error"])
        self.assertNotIn(secret, out["session_delete"]["error"])
        self.assertIn("[key]", out["session_delete"]["error"])
        self.assertIn("sess_leak", active_session_ids())
        logged = "\n".join(captured.output)
        self.assertIn("hosted session delete failed", logged)
        self.assertIn("sess_leak", logged)
        self.assertIn("network down", logged)
        self.assertNotIn(secret, logged)
        reply = reply_with_delete_status(out)
        self.assertIn("HEAVY-REPLY", reply)
        self.assertIn(DELETE_FAILURE_NOTE, reply)
        retried = delete_active_sessions()
        self.assertEqual(deletes["n"], 2)
        self.assertEqual(retried[-1]["ok"], True)
        self.assertNotIn("sess_leak", active_session_ids())

    def test_failed_delete_on_a_failed_job_is_visible(self):
        from fpfa.managed import active_session_ids, run_heavy_job

        def request(method, path, body):
            if method == "POST" and path == "/v1/environments":
                return {"id": "env_test"}
            if method == "POST" and path == "/v1/agents":
                return {"id": "agent_test"}
            if method == "POST" and path == "/v1/sessions":
                return {"id": "sess_fail", "status": "running"}
            if method == "GET":
                return {"data": []}
            if method == "DELETE":
                raise RuntimeError("network down")
            raise AssertionError((method, path))

        with self.assertLogs("fpfa.managed", level="ERROR") as captured:
            with self.assertRaises(RuntimeError) as caught:
                run_heavy_job(
                    request,
                    user_text="check the room",
                    sleep=lambda _seconds: None,
                    max_polls=1,
                )
        message = str(caught.exception)
        self.assertIn("did not finish", message)
        self.assertIn("The hosted session was not deleted", message)
        self.assertIn("network down", message)
        self.assertIn("sess_fail", active_session_ids())
        self.assertTrue(any("network down" in line for line in captured.output))

    def test_close_deletes_an_in_flight_heavy_session(self):
        import threading

        from fpfa.jobs import JobInbox
        from fpfa.managed import run_heavy_job

        deleted = []
        in_poll = threading.Event()
        release = threading.Event()

        def request(method, path, body):
            if method == "POST" and path == "/v1/environments":
                return {"id": "env_test"}
            if method == "POST" and path == "/v1/agents":
                return {"id": "agent_test"}
            if method == "POST" and path == "/v1/sessions":
                return {"id": "sess_inflight", "status": "running"}
            if method == "DELETE":
                deleted.append(path)
                return {}
            if method == "GET" and "/events" in path:
                in_poll.set()
                release.wait(5)
                return {"data": []}
            if method == "GET":
                return {"id": "sess_inflight", "status": "running"}
            raise AssertionError((method, path))

        inbox = JobInbox(worker_count=1)
        try:
            inbox.submit(
                project_id="p",
                project_name="Zone",
                kind="heavy",
                title="check",
                work=lambda _job_id: run_heavy_job(
                    request,
                    user_text="check the room",
                    sleep=lambda _seconds: None,
                    max_polls=3,
                ),
            )
            self.assertTrue(in_poll.wait(2))
            self.assertEqual(deleted, [])
            inbox.close()
            self.assertEqual(deleted, ["/v1/sessions/sess_inflight"])
            self.assertTrue(any(thread.is_alive() for thread in inbox._threads))
        finally:
            release.set()
            for thread in inbox._threads:
                thread.join(timeout=2)
            self.assertFalse(any(thread.is_alive() for thread in inbox._threads))

    def test_delete_in_progress_stays_visible_to_shutdown(self):
        import threading
        import time

        from fpfa.managed import (
            active_session_ids,
            delete_active_sessions,
            delete_session,
            register_active_session,
        )

        started = threading.Event()
        release = threading.Event()

        def request(method, path, body):
            if method == "DELETE":
                started.set()
                release.wait(5)
                raise RuntimeError("network down")
            raise AssertionError((method, path))

        register_active_session("sess_busy", request)
        holder: dict = {}

        def run() -> None:
            holder["status"] = delete_session(request, "sess_busy")

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        try:
            self.assertTrue(started.wait(2))
            self.assertIn("sess_busy", active_session_ids())
            began = time.monotonic()
            with self.assertLogs("fpfa.managed", level="ERROR") as captured:
                statuses = delete_active_sessions(deadline=0.3)
                self.assertLess(time.monotonic() - began, 1.0)
                release.set()
                worker.join(2)
            self.assertIn("sess_busy", active_session_ids())
            self.assertTrue(statuses)
            self.assertTrue(all(not item.get("ok") for item in statuses))
            self.assertFalse(any(item.get("skipped") for item in statuses))
            self.assertTrue(any(item.get("pending") for item in statuses))
            logged = "\n".join(captured.output)
            self.assertIn("still in progress", logged)
            self.assertIn("sess_busy", logged)
            self.assertIn("network down", logged)
        finally:
            release.set()
            worker.join(2)
        self.assertFalse(holder["status"]["ok"])
        self.assertIn("network down", holder["status"]["error"])
        self.assertIn("sess_busy", active_session_ids())

    def test_shutdown_observes_an_inflight_delete_that_succeeds(self):
        import threading
        import time

        from fpfa.managed import active_session_ids, delete_active_sessions, delete_session, register_active_session

        started = threading.Event()
        release = threading.Event()
        calls = []

        def request(method, path, body):
            if method == "DELETE":
                calls.append(path)
                started.set()
                release.wait(5)
                return {}
            raise AssertionError((method, path))

        register_active_session("sess_done", request)
        worker = threading.Thread(target=lambda: delete_session(request, "sess_done"), daemon=True)
        worker.start()
        self.assertTrue(started.wait(2))
        threading.Thread(target=lambda: (time.sleep(0.1), release.set()), daemon=True).start()
        statuses = delete_active_sessions(deadline=2.0)
        worker.join(2)
        self.assertEqual(calls, ["/v1/sessions/sess_done"])
        self.assertTrue(any(item.get("ok") for item in statuses))
        self.assertFalse(any(item.get("skipped") for item in statuses))
        self.assertNotIn("sess_done", active_session_ids())

    def test_close_bounds_a_slow_session_delete(self):
        import threading
        import time

        from fpfa.jobs import JobInbox
        from fpfa.managed import active_session_ids, register_active_session

        started = threading.Event()
        release = threading.Event()

        def request(method, path, body):
            if method == "DELETE":
                started.set()
                release.wait(30)
                return {}
            raise AssertionError((method, path))

        register_active_session("sess_slow", request)
        inbox = JobInbox(worker_count=1)
        try:
            began = time.monotonic()
            with self.assertLogs("fpfa.managed", level="ERROR") as captured:
                inbox.close()
            elapsed = time.monotonic() - began
            self.assertLess(elapsed, 2.5)
            self.assertGreater(elapsed, 0.4)
            self.assertTrue(started.wait(1))
            self.assertIn("sess_slow", active_session_ids())
            self.assertTrue(any("still in progress" in line and "sess_slow" in line for line in captured.output))
        finally:
            release.set()
            deadline = time.time() + 2
            while time.time() < deadline and "sess_slow" in active_session_ids():
                time.sleep(0.01)

    def test_process_exit_deletes_an_in_flight_hosted_session(self):
        import subprocess
        import textwrap

        log_path = Path(tempfile.mkdtemp(prefix="fpfa-del-")) / "del.log"
        script = textwrap.dedent(
            f"""
            import sys
            import time
            sys.path.insert(0, {str(APP_DIR)!r})
            from fpfa.jobs import JobInbox
            from fpfa.managed import active_session_ids, run_heavy_job

            log_path = {str(log_path)!r}

            def request(method, path, body):
                if method == "POST" and path == "/v1/environments":
                    return {{"id": "env"}}
                if method == "POST" and path == "/v1/agents":
                    return {{"id": "ag"}}
                if method == "POST" and path == "/v1/sessions":
                    return {{"id": "sess_exit"}}
                if method == "DELETE":
                    with open(log_path, "a", encoding="utf-8") as handle:
                        handle.write("DELETE " + path + "\\n")
                    return {{}}
                return {{"data": []}}

            inbox = JobInbox(worker_count=1)
            inbox.submit(
                project_id="p",
                project_name="Zone",
                kind="heavy",
                title="check",
                work=lambda job_id: run_heavy_job(
                    request,
                    user_text="check",
                    sleep=time.sleep,
                    poll_seconds=30,
                    max_polls=5,
                ),
            )
            for _ in range(100):
                if active_session_ids():
                    break
                time.sleep(0.02)
            else:
                raise SystemExit(2)
            """
        )
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertTrue(log_path.is_file(), proc.stderr)
        self.assertIn("DELETE /v1/sessions/sess_exit", log_path.read_text(encoding="utf-8"))

    def test_hatch_does_not_paste_a_role_or_send_ordinary_modules(self):
        from fpfa.managed import HEAVY_NOTE

        client = (REPO / "app" / "fpfa" / "managed.py").read_text(encoding="utf-8")
        self.assertNotIn("You are the design assistant", client)
        self.assertNotIn("NFPA 69", client)
        self.assertIn(HEAVY_NOTE.split(".")[0], client)
        for name in ("everyday.py", "workflow.py", "bess.py", "claude_client.py", "claim_check.py"):
            text = (REPO / "app" / "fpfa" / name).read_text(encoding="utf-8")
            self.assertNotIn("managed-agents", text, name)
            self.assertNotIn("run_heavy_job", text, name)
        ui = (REPO / "app" / "fpfa" / "desk.py").read_text(encoding="utf-8")
        for name in (
            "_send_chat_message",
            "run_zone",
            "_enqueue_zone",
            "_run_zone_here",
            "run_bess",
            "_enqueue_bess",
            "_run_bess_here",
            "export_docx",
            "export_to",
            "start_claim_check",
            "_finish_claim",
            "_claim_outcome",
        ):
            body = ui.split(f"def {name}(", 1)[1].split("\n    def ", 1)[0]
            self.assertNotIn("run_heavy_job", body, name)
        heavy = ui.split("def start_heavy(", 1)[1].split("\n    def ", 1)[0]
        self.assertIn("run_heavy_job", heavy)
        self.assertIn("session_system()", heavy)
        self.assertIn("reply_with_delete_status", heavy)
        self.assertNotIn("assemble_system", heavy)

    def _wait_for(self, app, needle: str, timeout: float = 2.0) -> None:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            app._poll()
            if needle in app.thread_text():
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {needle!r}")

    def test_heavy_reply_lands_in_the_same_thread(self):
        import threading
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import list_projects
        
        save_api_key("sk-ant-local-test")
        seen = {}

        def fake_ok(request, *, system, user_text, resources=None, **kwargs):
            seen["thread"] = threading.current_thread().name
            seen["system"] = system
            seen["user_text"] = user_text
            return {
                "text": "HEAVY-REPLY",
                "model": "claude-opus-5-5",
                "runtime": "managed-agents",
            }

        class Boom:
            def __init__(self, *_args, **_kwargs):
                raise AssertionError("ordinary Messages client")

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            project_id = None
            app.send_chat("/new Hall zone")
            project_id = app.project["id"]
            before = [row["id"] for row in list_projects()]
            with patch("fpfa.desk.run_heavy_job", fake_ok), patch("fpfa.desk.AnthropicMessages", Boom):
                app.send_chat("/heavy check the room")
                self._wait_for(app, "HEAVY-REPLY")
            self.assertEqual(app.project["id"], project_id)
            self.assertEqual([row["id"] for row in list_projects()], before)
            self.assertTrue(seen["thread"].startswith("fpfa-worker-"))
            from fpfa.managed import session_system

            self.assertEqual(seen["system"], session_system())
            self.assertNotIn("You are the design assistant", seen["system"])
            self.assertNotIn("Call read_role", seen["system"])
            self.assertNotIn("Call read_skill", seen["system"])
            self.assertNotIn("Call read_mode", seen["system"])
            self.assertIn("check the room", seen["user_text"])
            self.assertIn("already-computed zone packet", seen["user_text"])
            self.assertNotIn("Use tools for any gallons", seen["user_text"])
            self.assertNotIn("sk-ant", seen["user_text"])
            reply = app.chat_log[-1]["text"]
            job_id = app.chat_log[-1]["job_id"]
            self.assertIn("HEAVY-REPLY", reply)
            self.assertIn("| heavy |", reply)
            self.assertIn(job_id, reply)
            self.assertIn("Hall zone", reply)
            self.assertIn("check the room", reply)
            self.assertTrue(reply.startswith(f"Job {job_id} |"))
            self.assertIsNone(app.project.get("last_run"))
            self.assertIsNone(app.project.get("bess_run"))
            inbox = "\n".join(app.inbox_lines)
            self.assertIn("heavy", inbox)
            self.assertIn("back in this thread", app.status.get())
        finally:
            root.destroy()

    def test_ordinary_paths_do_not_call_the_hosted_runtime(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")

        def explode(*_args, **_kwargs):
            raise AssertionError("hosted runtime")

        class Fast:
            def __init__(self, _key):
                pass

            def create(self, **_kwargs):
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="CHAT-REPLY")],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(False)
            with patch("fpfa.desk.run_heavy_job", explode):
                app.send_chat("/sample-di")
                self.assertIn("281.3", app.thread_text())
                app.ask_claude.set(False)
                app.send_chat("/sample-bess")
                self.assertIn("4.11", app.thread_text())
                with patch("fpfa.desk.AnthropicMessages", Fast):
                    app.send_chat("which trim")
                    self._wait_for(app, "CHAT-REPLY")
            kinds = {job.kind for job in app.jobs.snapshot()}
            self.assertIn("zone", kinds)
            self.assertIn("bess", kinds)
            self.assertIn("chat", kinds)
            self.assertNotIn("heavy", kinds)
        finally:
            root.destroy()

    def test_heavy_keeps_the_tool_plan_and_the_chat_mode(self):
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        
        save_api_key("sk-ant-local-test")
        seen = {}

        def fake_ok(request, *, system, user_text, resources=None, **kwargs):
            seen["user_text"] = user_text
            seen["system"] = system
            return {"text": "HEAVY-REPLY", "model": "claude-opus-5-5", "runtime": "managed-agents"}

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(False)
            app.send_chat("/sample-di")
            zone_gal = app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"]
            app.density.set("not-a-number")
            with patch("fpfa.desk.run_heavy_job", fake_ok):
                app.send_chat("/heavy review the zone")
                self._wait_for(app, "HEAVY-REPLY")
            self.assertEqual(app.project["last_run"]["tools"]["zone_trapped_volume"]["zone_gal"], zone_gal)
            self.assertIn("281.3", app.results_text)
            self.assertIn("Governing zone total text: 281.3.", seen["user_text"])
            self.assertIn("38.1", seen["user_text"])
            self.assertIn("Active mode: mixed.", seen["user_text"])
            self.assertIn("already-computed zone packet", seen["user_text"])
            self.assertNotIn("Use tools for any gallons", seen["user_text"])
            from fpfa.managed import session_system

            self.assertEqual(seen["system"], session_system())
            self.assertNotIn("Call the calc tool", seen["system"])
            self.assertIn("| heavy |", app.thread_text())
            saved = json.dumps(app.project.get("di"))
            self.assertNotIn("not-a-number", saved)
        finally:
            root.destroy()

    def test_heavy_without_a_key_stays_local(self):
        from unittest.mock import patch

        from fpfa.keystore import clear_api_key
        
        clear_api_key()

        def explode(*_args, **_kwargs):
            raise AssertionError("hosted runtime")

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            with patch("fpfa.desk.run_heavy_job", explode):
                app.send_chat("/heavy check the room")
            self.assertIn("Settings", app.thread_text())
            self.assertNotIn("heavy", [job.kind for job in app.jobs.snapshot()])
            self.assertEqual(len(list_projects_ids(app)), 1)
        finally:
            root.destroy()

    def test_heavy_reply_stays_on_the_project_that_started_it(self):
        import threading
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import load_project
        
        save_api_key("sk-ant-local-test")
        started = threading.Event()
        release = threading.Event()

        def blocking(request, *, system, user_text, resources=None, **kwargs):
            started.set()
            release.wait(3)
            return {"text": "HEAVY-REPLY", "model": "claude-opus-5-5", "runtime": "managed-agents"}

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/new Origin hall")
            origin_id = app.project["id"]
            with patch("fpfa.desk.run_heavy_job", blocking):
                app.send_chat("/heavy check the room")
                self.assertTrue(started.wait(2))
                app.send_chat("/new Other hall")
                other_id = app.project["id"]
                self.assertNotEqual(other_id, origin_id)
                release.set()
                deadline_text = "HEAVY-REPLY"
                import time
                deadline = time.time() + 2
                saved = ""
                while time.time() < deadline:
                    app._poll()
                    saved = json.dumps(load_project(origin_id).get("chat") or [])
                    if deadline_text in saved:
                        break
                    time.sleep(0.02)
            self.assertIn("HEAVY-REPLY", saved)
            self.assertIn("| heavy |", saved)
            self.assertNotIn("HEAVY-REPLY", app.thread_text())
            self.assertEqual(load_project(other_id).get("last_run"), None)
            other_chat = json.dumps(load_project(other_id).get("chat") or [])
            self.assertNotIn("HEAVY-REPLY", other_chat)
        finally:
            release.set()
            root.destroy()


class BlindClaimCheckTests(unittest.TestCase):
    def setUp(self):
        _isolate_data()
        from fpfa.paths import content_root

        self.root = content_root()

    def _sample(self):
        from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
        from fpfa.workflow import run_di_zone

        return run_di_zone(self.root, EXAMPLE_DI, EXAMPLE_BASIS)

    def test_sample_claims_come_from_the_exported_narrative(self):
        from fpfa.claim_check import (
            BLIND_CLAIM_SKILL,
            build_packet,
            checker_request,
            checker_system,
            claims_filename,
            judge,
            sources_filename,
            verdict_filename,
        )
        from fpfa.roles_loader import read_role
        from fpfa.skills_loader import read_skill

        result = self._sample()
        packet = build_packet(result)
        self.assertEqual(packet["section"], "21 13 19")
        # PR-C added the ASSUMED-ZERO line (a typed 0 s exhaust time) and the gas fill's sizing basis to the narrative.
        self.assertEqual(packet["claim_count"], 14)
        self.assertIn("Zone total is 281.3 gal", packet["claims"])
        self.assertIn("t_total 38.1 s is calculated", packet["claims"])
        self.assertIn("281.3", packet["claims"])
        self.assertIn("38.1", packet["claims"])
        self.assertNotIn("NOT PULLED", packet["sources"])
        self.assertIn("PACKAGE ASSERTION (not a retrieved standard passage)", packet["sources"])
        # The double-interlock 500 gal rule, as the kernel cites it: a size threshold under
        # NFPA 13-2025 s8.3.2.3.1.1, not a cap. The sources carry that wording with the
        # section tokens taken out; the claims never state it as a requirement.
        basis = result["tools"]["dry_delivery_screen"]["nfpa_basis"]
        self.assertTrue(basis.startswith("NFPA 13-2025 s8.3.2.3.1.1 ("), basis)
        for phrase in ("DI <=500 gal: no delivery-time requirement", "QOD may help"):
            self.assertIn(phrase, basis)
            self.assertIn(phrase, packet["sources"])
            self.assertNotIn(phrase, packet["claims"])
        self.assertNotIn("QOD does not extend", packet["sources"])
        self.assertNotIn("requires NFPA 13-2025 Table", packet["claims"])
        self.assertNotIn("Draft for the engineer of record", packet["claims"])
        self.assertNotIn("ranks double-interlock", packet["claims"])
        for claim_line, source_line in zip(
            packet["claims"].splitlines(), packet["sources"].splitlines(), strict=True
        ):
            requirement = claim_line.split(" requires ", 1)[1]
            self.assertNotIn(requirement, source_line)
        skill = read_skill(self.root, BLIND_CLAIM_SKILL)
        self.assertIn("A checker who reads the draft tends to agree with its mistakes.", skill)
        self.assertIn("<section>-claims.md", skill)
        self.assertIn("<section>-sources.md", skill)
        self.assertIn("<section>-claimcheck.md", skill)
        self.assertIn("Supported", skill)
        self.assertIn("Not supported", skill)
        self.assertIn("Source not found", skill)
        self.assertEqual(claims_filename(), "21-13-19-claims.md")
        self.assertEqual(sources_filename(), "21-13-19-sources.md")
        self.assertEqual(verdict_filename(), "21-13-19-claimcheck.md")
        request = checker_request(packet["claims"], packet["sources"])
        self.assertTrue(request.startswith("21-13-19-claims.md\n"))
        self.assertIn("\n\n21-13-19-sources.md\n", request)
        self.assertNotIn("Draft for the engineer of record", request)
        self.assertNotIn("Part 1 — General", request)
        self.assertEqual(checker_system(self.root), read_role(self.root, "qa-specialist").strip())
        self.assertNotIn("Part 1 — General", checker_system(self.root))
        self.assertNotIn(
            "A checker who reads the draft tends to agree with its mistakes.",
            checker_system(self.root),
        )
        create = _support_every_claim()
        outcome = judge(self.root, packet, create)
        self.assertTrue(outcome["all_supported"])
        self.assertFalse(outcome["checked_against_standard"])
        self.assertIn("did not compare the narrative to the standard", outcome["thread"])
        self.assertIn("Engineer-of-record review still applies", outcome["thread"])
        self.assertNotIn("Every claim is Supported.", outcome["thread"])
        self.assertIn("1. Supported.", outcome["verdict"])
        self.assertEqual(create.seen[0]["model"], "claude-opus-5-5")
        self.assertNotIn("temperature", create.seen[0])
        self.assertNotIn("top_p", create.seen[0])
        self.assertNotIn("top_k", create.seen[0])
        self.assertNotIn("tool_choice", create.seen[0])
        self.assertNotIn("thinking", create.seen[0])
        self.assertNotIn("tools", create.seen[0])
        self.assertEqual(create.seen[0]["messages"][0]["content"], request)
        self.assertEqual(create.seen[0]["system"], checker_system(self.root))
        module = (REPO / "app" / "fpfa" / "claim_check.py").read_text(encoding="utf-8")
        self.assertNotIn("A checker who reads the draft tends to agree with its mistakes.", module)
        self.assertNotIn("NFPA 69", module)
        self.assertNotIn("8.3.2.3.1.1", module)
        dry = "21 13 " + "16"
        self.assertNotIn(dry, module)
        self.assertNotIn(dry, packet["claims"])
        self.assertNotIn(dry, outcome["verdict"])
        self.assertNotIn(dry, (REPO / "roles" / "qa-specialist" / "ROLE.md").read_text(encoding="utf-8"))

    def test_unretrieved_cite_stays_open_even_when_the_model_says_supported(self):
        from fpfa.claim_check import build_packet, checker_request, judge

        result = self._sample()
        result["narrative"] += (
            "\nNFPA 13-2025 §29.2.1.1 requires a 200 psi test for two hours."
        )
        result["basis"]["hazard_notes"] = "HAZARD-NOTE-MARKER stays with the designer."
        packet = build_packet(result)
        request = checker_request(packet["claims"], packet["sources"])
        open_lines = [line for line in packet["sources"].splitlines() if "NOT PULLED" in line]
        self.assertEqual(open_lines, ["15. NOT PULLED"])
        self.assertIn("§29.2.1.1", packet["claims"])
        self.assertIn("281.3", packet["claims"])
        self.assertIn("NOT PULLED", request)
        self.assertNotIn("HAZARD-NOTE-MARKER", request)
        self.assertNotIn("Draft for the engineer of record", request)
        self.assertNotIn("HAZARD-NOTE-MARKER", checker_request(packet["claims"], packet["sources"]))
        outcome = judge(self.root, packet, _support_every_claim())
        self.assertFalse(outcome["all_supported"])
        self.assertFalse(outcome["checked_against_standard"])
        open_line = next(line for line in outcome["verdict"].splitlines() if line.startswith("15. "))
        self.assertTrue(open_line.startswith("15. Source not found."))
        self.assertNotIn("Supported", open_line)
        self.assertIn("Open claims: 15", outcome["block_reason"])
        self.assertTrue(any(line.startswith("1. Supported.") for line in outcome["verdict"].splitlines()))

    def test_missing_checker_does_not_export(self):
        from fpfa.claim_check import build_packet, unanswered

        packet = build_packet(self._sample())
        outcome = unanswered(packet)
        self.assertFalse(outcome["all_supported"])
        self.assertEqual(outcome["checker"], "absent")
        self.assertEqual(outcome["verdict"], "")
        self.assertIn("did not run", outcome["thread"])
        self.assertNotIn("Supported.", outcome["thread"])

    def test_shared_section_and_uncited_figure_stay_in_the_packet(self):
        from fpfa.claim_check import _from_model, build_packet

        result = self._sample()
        before = build_packet(result)
        result["narrative"] += (
            "\nPer NFPA 13-2025 §8.3.2.3.1.1 a double-interlock zone may hold 750 gal with a QOD."
            "\nZone total is 999.9 gal."
        )
        packet = build_packet(result)
        self.assertNotEqual(packet["claims"], before["claims"])
        self.assertIn("750", packet["claims"])
        self.assertIn("999.9", packet["claims"])
        self.assertIn("§8.3.2.3.1.1", packet["claims"])
        for claim_line, source_line in zip(
            packet["claims"].splitlines(), packet["sources"].splitlines(), strict=True
        ):
            if "750" in claim_line:
                self.assertIn("PACKAGE ASSERTION", source_line)
                self.assertNotIn("NOT PULLED", source_line)
                self.assertNotIn("750", source_line)
                self.assertNotIn(claim_line.split(" requires ", 1)[1], source_line)
            if "999.9" in claim_line:
                self.assertIn("PACKAGE ASSERTION", source_line)
                self.assertNotIn("999.9", source_line)
        lied = "\n".join(
            f'{number}. Supported. Cite: "x"' for number in range(1, packet["claim_count"] + 1)
        )
        outcome = _from_model(packet, lied)
        self.assertFalse(outcome["all_supported"])
        self.assertFalse(outcome["checked_against_standard"])
        self.assertIn("Not supported.", outcome["verdict"])

    def test_echoed_tool_cite_is_not_supported(self):
        from fpfa.claim_check import _from_model

        packet = {
            "section": "21 13 19",
            "claims": "1. NFPA 13-2025 §8.3.2.3.1.1 requires DI 500 gal; QOD does not extend.",
            "sources": "1. NFPA 13-2025 §8.3.2.3.1.1. DI 500 gal; QOD does not extend.",
            "claim_count": 1,
            "draft_token": "echo",
        }
        outcome = _from_model(packet, '1. Supported. Cite: "same string"')
        self.assertFalse(outcome["all_supported"])
        self.assertFalse(outcome["checked_against_standard"])
        self.assertTrue(outcome["verdict"].startswith("1. Not supported."))

    def test_export_writes_sidecars_only_after_support(self):
        from unittest.mock import patch

        from docx import Document

        from fpfa.claim_check import claim_dir, claims_filename, verdict_filename
        from fpfa.projects import list_projects
        
        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.send_chat("/sample-di")
            origin_id = app.project["id"]
            before = [row["id"] for row in list_projects()]

            def explode(*_args, **_kwargs):
                raise AssertionError("hosted runtime")

            with tempfile.TemporaryDirectory() as tmp, patch("fpfa.desk.run_heavy_job", explode):
                blocked = Path(tmp) / "blocked.docx"
                with self.assertRaises(RuntimeError) as caught:
                    app.export_to(blocked)
                self.assertIn("did not run", str(caught.exception))
                self.assertFalse(blocked.exists())
                held = claim_dir(origin_id)
                self.assertTrue((held / claims_filename()).is_file())
                self.assertFalse((held / verdict_filename()).is_file())
                create = _support_every_claim()
                written = app.export_to(Path(tmp) / "draft.docx", create=create)
                doc = Document(written)
                text = "\n".join(p.text for p in doc.paragraphs)
                dry = "21 13 " + "16"
                self.assertIn("Section 21 13 19", text)
                self.assertNotIn(dry, text)
                self.assertTrue((written.parent / verdict_filename()).is_file())
                verdict = (written.parent / verdict_filename()).read_text(encoding="utf-8")
                self.assertIn("Supported.", verdict)
                self.assertNotIn(dry, verdict)
                self.assertNotIn("Draft for the engineer of record", verdict)
                user = create.seen[0]["messages"][0]["content"]
                self.assertNotIn("Draft for the engineer of record", user)
                self.assertNotIn("tools", create.seen[0])
            chat = app.thread_text()
            self.assertIn("| claim |", chat)
            self.assertIn("did not compare the narrative to the standard", chat)
            self.assertIn("Engineer-of-record review still applies", chat)
            self.assertNotIn("Every claim is Supported.", chat)
            self.assertEqual(app.project["id"], origin_id)
            self.assertEqual([row["id"] for row in list_projects()], before)
            self.assertTrue(app.project["claim_check"]["all_supported"])
            self.assertFalse(app.project["claim_check"]["checked_against_standard"])
            kinds = {job.kind for job in app.jobs.snapshot()}
            self.assertIn("zone", kinds)
            self.assertIn("claim", kinds)
            self.assertNotIn("heavy", kinds)
        finally:
            root.destroy()

    def test_claim_job_stays_on_the_project_that_started_it(self):
        import threading
        import time
        from unittest.mock import patch

        from fpfa.keystore import save_api_key
        from fpfa.projects import list_projects, load_project
        
        started = threading.Event()
        release = threading.Event()
        seen = {}

        class Hold:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                seen["user"] = kwargs["messages"][0]["content"]
                seen["system"] = kwargs["system"]
                seen["keys"] = set(kwargs)
                seen["thread"] = threading.current_thread().name
                started.set()
                release.wait(3)
                from fpfa.claim_check import numbered_bodies, split_checker_request

                claims, sources = split_checker_request(kwargs["messages"][0]["content"])
                numbered = numbered_bodies
                source_map = numbered(sources)
                lines = [
                    f'{number}. Supported. Cite: "{source_map.get(number, "")}"'
                    for number in numbered(claims)
                ]
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="\n".join(lines))],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(False)
            app.send_chat("/sample-di")
            origin_id = app.project["id"]
            save_api_key("sk-ant-local-test")

            def explode(*_args, **_kwargs):
                raise AssertionError("hosted runtime")

            dialogs = []

            def no_dialog(*_args, **_kwargs):
                dialogs.append("dialog")
                return ""

            # The save dialog is the window's (pywebview's). It must not open for a check
            # that finished on a job no longer open.
            with patch("fpfa.desk.run_heavy_job", explode), patch("fpfa.desk.AnthropicMessages", Hold), patch.object(
                app.shell, "ask_save_path", no_dialog
            ):
                app.export_docx()
                self.assertTrue(started.wait(2))
                self.assertTrue(seen["thread"].startswith("fpfa-worker-"))
                app.send_chat("/new Other hall")
                other_id = app.project["id"]
                self.assertNotEqual(other_id, origin_id)
                before = [row["id"] for row in list_projects()]
                release.set()
                deadline = time.time() + 2
                saved = ""
                while time.time() < deadline:
                    app._poll()
                    saved = json.dumps(load_project(origin_id).get("chat") or [])
                    if "| claim |" in saved:
                        break
                    time.sleep(0.02)
            self.assertIn("| claim |", saved)
            self.assertIn("did not compare the narrative to the standard", saved)
            self.assertIn("Engineer-of-record review still applies", saved)
            self.assertNotIn("Every claim is Supported.", saved)
            self.assertNotIn("| claim |", app.thread_text())
            self.assertEqual(load_project(origin_id)["claim_check"]["all_supported"], True)
            self.assertEqual(load_project(origin_id)["claim_check"]["checked_against_standard"], False)
            self.assertIsNone(load_project(other_id).get("claim_check"))
            self.assertEqual({row["id"] for row in list_projects()}, set(before))
            self.assertEqual(dialogs, [])
            self.assertNotIn("Draft for the engineer of record", seen["user"])
            self.assertNotIn("Part 1 — General", seen["user"])
            self.assertNotIn("Part 1 — General", seen["system"])
            self.assertIn("Judge each numbered claim from the cites file alone.", seen["system"])
            for banned in ("temperature", "top_p", "top_k", "tool_choice", "thinking", "tools"):
                self.assertNotIn(banned, seen["keys"])
            self.assertIn("claim", {job.kind for job in app.jobs.snapshot()})
            self.assertNotIn("heavy", {job.kind for job in app.jobs.snapshot()})
        finally:
            release.set()
            root.destroy()

    def test_export_keeps_the_draft_that_was_checked(self):
        import threading
        import time
        from unittest.mock import patch

        from docx import Document

        from fpfa.claim_check import numbered_bodies, split_checker_request
        from fpfa.keystore import save_api_key
        
        started = threading.Event()
        release = threading.Event()

        class Hold:
            def __init__(self, _key):
                pass

            def create(self, **kwargs):
                started.set()
                release.wait(3)
                claims, sources = split_checker_request(kwargs["messages"][0]["content"])
                source_map = numbered_bodies(sources)
                lines = [
                    f'{number}. Supported. Cite: "{source_map.get(number, "")}"'
                    for number in numbered_bodies(claims)
                ]
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[SimpleNamespace(type="text", text="\n".join(lines))],
                )

        root = Loop()
        try:
            app = root.open_desk()
            root.update()
            app.ask_claude.set(False)
            app.send_chat("/sample-di")
            save_api_key("sk-ant-local-test")
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "draft.docx"

                def save_as(*_args, **_kwargs):
                    return str(target)

                with patch("fpfa.desk.AnthropicMessages", Hold), patch.object(app.shell, "ask_save_path", save_as):
                    app.export_docx()
                    self.assertTrue(started.wait(2))
                    app.project["last_run"]["narrative"] = "MUTATED-NARRATIVE"
                    release.set()
                    deadline = time.time() + 2
                    while time.time() < deadline and not target.is_file():
                        app._poll()
                        time.sleep(0.02)
                    app._poll()
                self.assertTrue(target.is_file())
                text = "\n".join(p.text for p in Document(target).paragraphs)
                self.assertIn("Draft for the engineer of record", text)
                self.assertIn("281.3", text)
                self.assertNotIn("MUTATED-NARRATIVE", text)
        finally:
            release.set()
            root.destroy()


def list_projects_ids(app):
    return list(app._ids)


if __name__ == "__main__":
    unittest.main()
