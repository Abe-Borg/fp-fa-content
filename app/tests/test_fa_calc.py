"""fa_calc, search_corpus, and the spec-note cap."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))


def _session_root(root: Path) -> Path:
    pack = root / "calcs" / "fp"
    pack.mkdir(parents=True, exist_ok=True)
    di = pack / "di_zone.py"
    if not di.is_file():
        di.write_text("formulas = None\n", encoding="utf-8")
    return root


def _session(root: Path):
    from fpfa.calc_tools import ToolSession

    return ToolSession(_session_root(root))


class FaCalcTests(unittest.TestCase):
    def test_nac_ell_returns_pass_and_veol(self):
        from fpfa.calc_tools import ToolSession

        # Same hand check as calcs/fa/tests/test_nac_vdrop.py: 12 AWG passes.
        result = ToolSession(REPO).execute("fa_calc", {
            "module": "nac_vdrop",
            "op": "ell",
            "inputs": {
                "currents_a": [0.2] * 12,
                "length_one_way_ft": 450,
                "awg": "12",
            },
        })
        self.assertTrue(result["pass"])
        self.assertAlmostEqual(result["Veol"], 16.1232, places=3)

    def test_unknown_module_or_op_raises(self):
        from fpfa.calc_tools import ToolSession

        session = ToolSession(REPO)
        with self.assertRaises((KeyError, ValueError)):
            session.execute("fa_calc", {"module": "no_such_module", "op": "ell", "inputs": {}})
        with self.assertRaises((KeyError, ValueError)):
            session.execute("fa_calc", {"module": "nac_vdrop", "op": "no_such_op", "inputs": {}})
        with self.assertRaises((KeyError, ValueError)):
            session.execute("fa_calc", {"module": "../fp/formulas", "op": "dispatch", "inputs": {}})
        with self.assertRaises((KeyError, ValueError)):
            session.execute("fa_calc", {"module": "nac_vdrop", "op": "_private", "inputs": {}})

    def test_list_ops_matches_public_functions(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.fa_calc import FA_OPS

        listed = ToolSession(REPO).execute("fa_calc", {"list_ops": True})
        self.assertEqual(listed["ops"], {name: list(ops) for name, ops in FA_OPS.items()})

    def test_bare_number_and_tuple_are_wrapped(self):
        from fpfa.calc_tools import ToolSession

        session = ToolSession(REPO)
        factor = session.execute("fa_calc", {
            "module": "battery",
            "op": "factor",
            "inputs": {"edition": 2025},
        })
        self.assertEqual(factor, {"value": 1.25})
        setpoint = session.execute("fa_calc", {
            "module": "lfl",
            "op": "setpoint",
            "inputs": {"lfl_vol_pct": 4.0, "pct": 25},
        })
        self.assertEqual(setpoint["value"][0], 1.0)
        self.assertEqual(setpoint["value"][1], 10000.0)

    def test_modules_that_import_lib_still_run(self):
        from fpfa.calc_tools import ToolSession

        session = ToolSession(REPO)
        branch = session.execute("fa_calc", {
            "module": "asd_v2",
            "op": "branch",
            "inputs": {"name": "A", "id_mm": 21, "lead_m": 1, "holes": 2, "spacing_m": 3},
        })
        self.assertEqual(branch["name"], "A")
        network = session.execute("fa_calc", {
            "module": "asd_v2",
            "op": "network",
            "inputs": {
                "header_m": 2,
                "header_id_mm": 25,
                "branches": [branch],
                "total_lpm": 60,
            },
        })
        self.assertIsInstance(network["A"], list)
        self.assertEqual(len(network["A"]), 3)
        level = session.execute("fa_calc", {
            "module": "ads_margin",
            "op": "spl_at",
            "inputs": {"l_ref": 90, "d_ft": 20, "d_ref_ft": 10},
        })
        self.assertAlmostEqual(level["value"], 90 - 20 * math.log10(2), places=5)

    def test_a_second_content_root_uses_its_own_lib(self):
        from fpfa.calc_tools import ToolSession

        def pack(marker: float) -> Path:
            root = Path(tempfile.mkdtemp(prefix="fpfa-fa-root-"))
            lib = root / "calcs" / "fa" / "lib"
            lib.mkdir(parents=True)
            (lib / "__init__.py").write_text("", encoding="utf-8")
            (lib / "asd.py").write_text(
                f"def transport_s(length_m, id_mm, flow_lpm):\n    return {marker}\n",
                encoding="utf-8",
            )
            (lib / "asd_v2.py").write_text(
                "from lib import asd\n"
                "def branch(name, id_mm, lead_m, holes, spacing_m):\n"
                "    return {'name': name, 'marker': asd.transport_s(0, 1, 1)}\n",
                encoding="utf-8",
            )
            return root

        first = ToolSession(_session_root(pack(1.0))).execute("fa_calc", {
            "module": "asd_v2",
            "op": "branch",
            "inputs": {"name": "A", "id_mm": 1, "lead_m": 1, "holes": 1, "spacing_m": 1},
        })
        second = ToolSession(_session_root(pack(2.0))).execute("fa_calc", {
            "module": "asd_v2",
            "op": "branch",
            "inputs": {"name": "B", "id_mm": 1, "lead_m": 1, "holes": 1, "spacing_m": 1},
        })
        self.assertEqual(first["marker"], 1.0)
        self.assertEqual(second["marker"], 2.0)

    def test_schemas_keep_lfl_and_add_the_new_tools(self):
        from fpfa.calc_tools import SCHEMAS

        names = [item["name"] for item in SCHEMAS]
        self.assertIn("lfl_setpoints", names)
        self.assertIn("fa_calc", names)
        self.assertIn("search_corpus", names)
        fa = next(item for item in SCHEMAS if item["name"] == "fa_calc")
        self.assertIn("list_ops", fa["description"])
        self.assertIn("Do not compute the formula yourself.", fa["description"])
        search = next(item for item in SCHEMAS if item["name"] == "search_corpus")
        self.assertIn("corpus/", search["description"])
        self.assertIn("NFPA edition", search["description"])


class SearchCorpusTests(unittest.TestCase):
    def test_finds_a_pin_and_skips_non_markdown(self):
        root = Path(tempfile.mkdtemp(prefix="fpfa-corpus-"))
        corpus = root / "corpus" / "fa"
        corpus.mkdir(parents=True)
        (corpus / "pin.md").write_text(
            "# Notification pin\n\nThe adopted edition is NFPA 72-2025 for this note.\n"
            "A second line also says nfpa 72-2025 so both lines return.\n",
            encoding="utf-8",
        )
        (corpus / "plain.md").write_text(
            "No heading here but PlainToken is the pin.\n",
            encoding="utf-8",
        )
        long = "A" * 180 + " UniquePinToken " + "B" * 180
        (corpus / "long.md").write_text("# Wide\n\n" + long + "\n", encoding="utf-8")
        (corpus / "skip.txt").write_text("NFPA 72-2025 should not come from text.\n", encoding="utf-8")
        (corpus / "skip.bin").write_bytes(b"NFPA 72-2025\x00binary")
        session = _session(root)

        found = session.execute("search_corpus", {"query": "nfpa 72-2025"})
        self.assertEqual(len(found["hits"]), 1)
        hit = found["hits"][0]
        self.assertEqual(hit["path"], "corpus/fa/pin.md")
        self.assertEqual(hit["heading"], "Notification pin")
        self.assertEqual(len(hit["lines"]), 2)
        self.assertTrue(all(len(line) <= 200 for line in hit["lines"]))
        self.assertIn("NFPA 72-2025", hit["lines"][0])

        with self.assertRaises(ValueError):
            session.execute("search_corpus", {"query": "  "})
        plain = session.execute("search_corpus", {"query": "plaintoken"})
        self.assertEqual(plain["hits"][0]["path"], "corpus/fa/plain.md")
        self.assertNotIn("heading", plain["hits"][0])

        clipped = session.execute("search_corpus", {"query": "uniquepintoken"})
        self.assertEqual(len(clipped["hits"]), 1)
        self.assertLessEqual(len(clipped["hits"][0]["lines"][0]), 200)
        self.assertIn("UniquePinToken", clipped["hits"][0]["lines"][0])

    def test_default_limit_and_response_cap(self):
        root = Path(tempfile.mkdtemp(prefix="fpfa-corpus-cap-"))
        folder = root / "corpus" / "n"
        folder.mkdir(parents=True)
        for index in range(10):
            (folder / f"p{index:02d}.md").write_text(
                f"# H\n\nPinToken lives in file {index}.\n",
                encoding="utf-8",
            )
        session = _session(root)
        found = session.execute("search_corpus", {"query": "PinToken"})
        self.assertEqual(len(found["hits"]), 8)

        wide = "W" * 200
        for index in range(120):
            (folder / f"w{index:03d}.md").write_text(
                f"# H\n\n{wide} WideToken {wide}\n{wide} WideToken again {wide}\n",
                encoding="utf-8",
            )
        capped = session.execute("search_corpus", {"query": "WideToken", "limit": 500})
        self.assertLess(len(capped["hits"]), 120)
        self.assertGreater(len(capped["hits"]), 8)
        self.assertLessEqual(len(json.dumps(capped)), 40_000)
        for hit in capped["hits"]:
            self.assertLessEqual(len(hit["lines"]), 2)
            self.assertTrue(all(len(line) <= 200 for line in hit["lines"]))


class SpecNotesCapTests(unittest.TestCase):
    def test_default_chars_keeps_a_long_pin(self):
        import inspect

        from fpfa.skills_loader import spec_notes

        default = inspect.signature(spec_notes).parameters["chars"].default
        self.assertGreaterEqual(default, 16000)
        root = Path(tempfile.mkdtemp(prefix="fpfa-specs-"))
        folder = root / "specs"
        folder.mkdir()
        (folder / "README.md").write_text("folder guide\n", encoding="utf-8")
        (folder / "21-30-00-fire-pumps.md").write_text("y" * 9000, encoding="utf-8")
        (folder / "28-31-00-fire-detection-and-alarm.md").write_text("x" * 12000, encoding="utf-8")
        notes = spec_notes(root)
        self.assertEqual(
            [note["name"] for note in notes],
            ["21-30-00-fire-pumps.md", "28-31-00-fire-detection-and-alarm.md"],
        )
        self.assertEqual(len(notes[0]["text"]), 9000)
        self.assertEqual(len(notes[1]["text"]), 12000)
        clipped = spec_notes(root, chars=100)
        self.assertEqual(len(clipped[1]["text"]), 100)


if __name__ == "__main__":
    unittest.main()
