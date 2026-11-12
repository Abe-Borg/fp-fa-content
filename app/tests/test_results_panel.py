"""The Results tab's view, the window's remembered layout, and the start cards of the empty thread.

The view prints what the calc tools returned and computes nothing: each figure here is checked against
the tool output it came from and against the narrative, so the tiles, the thread, and the exports
cannot disagree. No model is involved in any test in this file.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from desk_loop import Loop  # noqa: E402


def _isolate() -> Path:
    path = Path(tempfile.mkdtemp(prefix="fpfa-results-"))
    os.environ["FPFA_DATA_DIR"] = str(path)
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    for name in ("FPFA_CONTENT_ROOT", "FPFA_THEME", "FPFA_REDUCE_MOTION"):
        os.environ.pop(name, None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})
    return path


def _sample_run(**changes):
    from fpfa.sample_data import EXAMPLE_BASIS, EXAMPLE_DI
    from fpfa.workflow import run_di_zone

    return run_di_zone(REPO, dict(EXAMPLE_DI, **changes), EXAMPLE_BASIS)


def _low_air_hits(text: str) -> list:
    """The pack's own detector for a sentence that names low air as a release input."""
    path = REPO / "calcs" / "fp" / "test_pack_content_lowair.py"
    spec = importlib.util.spec_from_file_location("pack_lowair_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.low_air_release_hits(text)


class ZoneViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fpfa.results_panel import results_view

        cls.result = _sample_run()
        cls.view = results_view(cls.result)
        cls.figures = {figure["key"]: figure for figure in cls.view["figures"]}

    def test_no_run_is_a_title_and_what_to_do_next(self):
        from fpfa.results_panel import NO_RUN_TITLE, results_view

        for nothing in (None, {}, {"tools": None}, "text"):
            view = results_view(nothing)
            self.assertEqual((view["kind"], view["run"], view["title"]), ("", "", NO_RUN_TITLE))
            self.assertIn("Inputs tab", " ".join(view["lines"]))
            self.assertNotIn("figures", view)

    def test_each_figure_is_the_tool_output_printed_the_way_the_narrative_prints_it(self):
        from fpfa.workflow import fmt1

        tools = self.result["tools"]
        narrative = self.result["narrative"]
        zone = self.figures["zone_total"]
        self.assertEqual((zone["value"], zone["unit"]), (fmt1(tools["zone_trapped_volume"]["zone_gal"]), "gal"))
        self.assertEqual(zone["value"], "281.3")
        self.assertIn(f"Zone total is {zone['value']} gal.", narrative)
        trip = self.figures["t_total"]
        self.assertEqual((trip["value"], trip["unit"]), (fmt1(tools["di_trip_to_water"]["t_total_s"]), "s"))
        self.assertEqual(trip["value"], "38.1")
        self.assertIn(f"t_total {trip['value']} s is calculated.", narrative)
        demand = self.figures["demand"]
        self.assertEqual(demand["value"], fmt1(tools["density_area"]["qd_gpm"]))
        self.assertIn(f"total {demand['value']} gpm", narrative)
        self.assertEqual(self.figures["trim"]["value"], tools["elect_di_trim"]["family"])
        self.assertEqual(self.figures["trim"]["label"], tools["elect_di_trim"]["status"])
        # Every sentence under a figure is one the narrative or the run already says. The friction sentence beside a
        # center-to-center volume (PR-D) is in the run's flags, not the narrative: a section number in the narrative
        # would be read back as a claim of its own by the Section's trace check.
        said = narrative + "\n" + "\n".join(self.result["flags"])
        for line in zone["lines"] + self.figures["size_exemption"]["lines"][1:] + self.figures["gas_fill"]["lines"]:
            self.assertIn(line.rstrip("."), said, line)

    def test_the_three_labels_stay_distinct_on_the_tiles(self):
        zone = self.figures["zone_total"]
        self.assertEqual(zone["label"], "calculated, trim ASSUMED")
        self.assertIn("5.0 gal trim ASSUMED (blank trim; the kernel's assumption, no valve data sheet; not calculated)", zone["lines"])
        self.assertIn("276.3 gal of pipe (calculated)", zone["lines"])
        trip = self.figures["t_total"]
        self.assertEqual(trip["label"], "calculated")
        self.assertTrue(any("ASSUMED from time basis FM" in line and "lookup, not calculated" in line for line in trip["lines"]))
        self.assertIn("Delivery times are an optimistic screen, not a listed water-delivery-time calculation.", trip["lines"])
        self.assertIn("Designer judgment the tools did not return: use best judgment. Not a calculated figure.", self.view["notes"])
        # A figure the tools returned on two bases has no one headline number.
        self.assertEqual(self.figures["gas_fill"]["value"], "")
        self.assertIn("Gauge-basis fill rate is 3.41 scfm. Absolute-basis fill rate is 4.67 scfm.", self.figures["gas_fill"]["lines"])

    def test_the_screen_verdict_is_the_tools_and_is_said_in_words(self):
        trip = self.figures["t_total"]
        self.assertFalse(self.result["tools"]["di_trip_to_water"]["passes_screen"])
        self.assertEqual((trip["tone"], trip["verdict"]), ("warn", "The zone-total screen does not pass."))
        self.assertEqual(self.figures["size_exemption"]["value"], "yes")
        self.assertIn("Zone total of 281.3 gal against the 500 gal exemption threshold (NFPA 13-2025 §8.3.2.3.1.1).", self.figures["size_exemption"]["lines"])
        # A faster fill passes the same screen: the tile follows the tool, not a number of its own.
        from fpfa.results_panel import results_view

        fast = {figure["key"]: figure for figure in results_view(_sample_run(q_fill_gpm=2000.0))["figures"]}
        self.assertEqual((fast["t_total"]["tone"], fast["t_total"]["verdict"]), ("ok", "The zone-total screen passes."))

    def test_a_typed_trim_is_not_called_assumed(self):
        from fpfa.results_panel import results_view

        typed = {figure["key"]: figure for figure in results_view(_sample_run(trim_gal=6.5))["figures"]}
        self.assertEqual(typed["zone_total"]["label"], "calculated")
        self.assertIn("6.5 gal trim (entered on the form, not assumed)", typed["zone_total"]["lines"])
        self.assertFalse(any("ASSUMED" in line for line in typed["zone_total"]["lines"]))

    def test_the_releasing_tile_names_p_and_never_low_air_as_a_release_input(self):
        releasing = self.figures["releasing"]
        self.assertEqual(releasing["code"], "solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated")
        text = "\n".join([releasing["code"], *releasing["lines"]])
        self.assertIn("Low air is supervisory only (PSL-SUP) and is never a release input.", text)
        self.assertNotIn("low_air", text)
        self.assertEqual(_low_air_hits(text), [])
        # The whole view, as the page receives it, leaves the kernel's deprecated names out.
        whole = "\n".join(str(value) for value in self.view.values())
        self.assertNotIn("AND low" + "_air", whole)
        self.assertNotIn("'low" + "_air': ", whole.replace('"', "'"))

    def test_another_trim_family_is_told_the_table_is_a_reference(self):
        from fpfa.results_panel import zone_figures

        tools = dict(self.result["tools"])
        tools["elect_di_trim"] = dict(tools["elect_di_trim"], family="El/Pn")
        releasing = next(figure for figure in zone_figures(tools) if figure["key"] == "releasing")
        self.assertIn("The elected trim family is El/Pn. The truth table is the electric/electric reference, "
                      "not this valve's logic.", releasing["lines"])

    def test_flags_narrative_and_transcript_travel_whole(self):
        self.assertEqual(self.view["kind"], "zone")
        self.assertEqual(self.view["flags"], self.result["flags"])
        self.assertEqual(self.view["narrative"], self.result["narrative"])
        self.assertEqual(self.view["source"], "Narrative from the tool plan.")
        self.assertIn("1. zone_trapped_volume  (tool-plan)", self.view["transcript"])

    def test_a_run_missing_a_tool_draws_what_it_has(self):
        from fpfa.results_panel import results_view

        view = results_view({"tools": {"zone_trapped_volume": {"zone_gal": 12.0}}, "narrative": "n"})
        self.assertEqual([figure["key"] for figure in view["figures"]], ["zone_total"])
        self.assertEqual(view["figures"][0]["lines"], ["Trim was not on this result."])

    def test_the_bess_starter_shows_its_governing_texts_and_no_tiles(self):
        from fpfa.results_panel import results_view

        view = results_view({"kind": "bess", "tools": {"lfl_setpoints": {}}, "narrative": "Starter.",
                             "governing": {"texts": ["Mixture LFL is 5.9 vol%."]}, "flags": ["Duration ASSUMED: 2 h."]})
        self.assertEqual((view["kind"], view["figures"]), ("bess", []))
        self.assertEqual(view["governing"], ["Mixture LFL is 5.9 vol%."])
        self.assertEqual(view["source"], "Narrative from the LFL tool plan.")
        self.assertIn("An election or a duration the tool did not return is ASSUMED.", view["notes"])


class DeskStateTests(unittest.TestCase):
    def setUp(self):
        _isolate()
        self.root = Loop()
        self.addCleanup(self.root.destroy)

    def test_the_page_gets_the_view_beside_the_text_and_is_told_when_a_run_lands(self):
        from fpfa.results_panel import NO_RUN_TITLE

        app = self.root.open_desk()
        self.root.update()
        before = app.snapshot()
        self.assertEqual(before["results_view"]["title"], NO_RUN_TITLE)
        self.assertEqual(before["run_rev"], 0)
        app.ask_claude.set(False)
        app.start_sample_di()
        self.root.update()
        state = app.snapshot()
        self.assertEqual(state["run_rev"], 1)
        view = state["results_view"]
        self.assertEqual(view["kind"], "zone")
        self.assertEqual(view["run"], app.project["last_run"]["job_id"])
        # The plain text is still there for the clipboard, and the two agree.
        self.assertIn("Zone 281.3 gal", state["results"])
        self.assertEqual(next(figure for figure in view["figures"] if figure["key"] == "zone_total")["value"], "281.3")
        # Opening the job again shows the same run and is not a run landing.
        project_id = app.project["id"]
        app.new_job()
        self.assertEqual(app.snapshot()["results_view"]["kind"], "")
        app.select_project(project_id)
        again = app.snapshot()
        self.assertEqual((again["results_view"]["kind"], again["run_rev"]), ("zone", 1))

    def test_the_welcome_offers_three_ways_to_start(self):
        app = self.root.open_desk()
        self.root.update()
        welcome = app.snapshot()["welcome"]
        self.assertEqual([card["action"] for card in welcome["cards"]], ["ask", "inputs", "sample-di"])
        self.assertEqual([card["title"] for card in welcome["cards"]], ["Ask a question", "Size a zone", "Try the sample"])
        # The server runs every card action that is not the page's own.
        from fpfa.web.server import ACTIONS

        for card in welcome["cards"]:
            if card["action"] not in ("ask", "inputs"):
                self.assertIn(card["action"], ACTIONS)
        # The older links are still sent: the key link has no card.
        self.assertEqual([link["action"] for link in welcome["links"]], ["settings", "sample-di"])

    def test_the_layout_is_remembered_between_runs_and_nonsense_is_not(self):
        from fpfa.desk import LAYOUT_DEFAULT, clean_layout
        from fpfa.paths import read_config

        app = self.root.open_desk()
        self.root.update()
        self.assertEqual(app.snapshot()["settings"]["layout"], LAYOUT_DEFAULT)
        revision = app.revision
        self.assertEqual(app.set_layout({"panel": "team", "panel_width": "612.4", "sidebar": 0}),
                         {"sidebar": False, "panel": "team", "panel_width": 612})
        self.assertGreater(app.revision, revision)
        self.assertEqual(read_config()["layout"], {"sidebar": False, "panel": "team", "panel_width": 612})
        # A patch changes only what it names. A tab that does not exist closes the panel.
        self.assertEqual(app.set_layout({"panel": "drawer"}), {"sidebar": False, "panel": "", "panel_width": 612})
        self.assertEqual(app.set_layout({"panel_width": 99999})["panel_width"], 2400)
        self.assertEqual(app.set_layout({"panel_width": 10})["panel_width"], 320)
        self.assertEqual(app.set_layout({"panel_width": "wide"})["panel_width"], 0)
        self.assertEqual(clean_layout("nonsense"), LAYOUT_DEFAULT)
        self.assertEqual(clean_layout({"sidebar": False, "other": 1}), dict(LAYOUT_DEFAULT, sidebar=False))
        # Nothing about a job moved, and the same layout again writes nothing.
        revision = app.revision
        app.set_layout({"panel_width": 0})
        self.assertEqual(app.revision, revision)
        # The next window on this data directory opens the way this one was left.
        app.set_layout({"panel": "results", "sidebar": True})
        self.root.destroy()
        again = self.root.open_desk()
        self.assertEqual(again.snapshot()["settings"]["layout"], {"sidebar": True, "panel": "results", "panel_width": 0})

    def test_a_saved_layout_that_is_not_one_is_ignored(self):
        from fpfa.desk import LAYOUT_DEFAULT
        from fpfa.paths import write_config

        write_config({"layout": ["team"]})
        app = self.root.open_desk()
        self.assertEqual(app.snapshot()["settings"]["layout"], LAYOUT_DEFAULT)


if __name__ == "__main__":
    unittest.main()
