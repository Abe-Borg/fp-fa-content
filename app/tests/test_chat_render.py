"""Thread rendering and job naming. These tests do not need a display."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("FPFA_DATA_DIR", tempfile.mkdtemp(prefix="fpfa-test-"))


class MarkdownSegmentsTests(unittest.TestCase):
    def test_markers_are_drawn_and_words_are_kept(self):
        from fpfa.chat_render import markdown_segments, plain_text

        text = (
            "## What sets the time\n"
            "- **Detection**: the panel confirms (`t_detect_s`).\n"
            "  - nested point\n"
            "1. Keep the trapped volume small.\n"
            "Screen limit 30.0 s — ASSUMED from time basis FM. t_total and zone_gal stay as written.\n"
            "---\n"
            "end"
        )
        shown = plain_text(text)
        self.assertIn("What sets the time", shown)
        self.assertNotIn("##", shown)
        self.assertIn("• Detection: the panel confirms (t_detect_s).", shown)
        self.assertIn("• nested point", shown)
        self.assertIn("1. Keep the trapped volume small.", shown)
        self.assertIn("Screen limit 30.0 s — ASSUMED from time basis FM. t_total and zone_gal stay as written.", shown)
        self.assertNotIn("**", shown)
        self.assertNotIn("`", shown)
        self.assertNotIn("---", shown)
        tags = {tag for _chunk, chunk_tags in markdown_segments(text) for tag in chunk_tags}
        for tag in ("heading", "bullet", "bullet2", "bold", "code"):
            self.assertIn(tag, tags)

    def test_single_asterisks_and_underscores_are_left_alone(self):
        from fpfa.chat_render import plain_text

        self.assertEqual(plain_text("a*b*c and q_fill_gpm"), "a*b*c and q_fill_gpm")

    def test_job_heading_is_a_caption_with_the_job_id(self):
        from fpfa.chat_render import markdown_segments, plain_text

        zone = "Job 4e8ed6163bf9 | Sample data hall DI zone | zone | Zone tool plan\nZone total is 281.3 gal."
        segments = markdown_segments(zone)
        self.assertEqual(segments[0], ("Job 4e8ed6163bf9 | Sample data hall DI zone | zone | Zone tool plan", ("meta",)))
        self.assertIn("Zone total is 281.3 gal.", plain_text(zone))
        chat = "Job 84861fb382ed | Hall 2 | chat | How do I keep a DI zone under the screen?\nAnswer."
        self.assertEqual(markdown_segments(chat)[0], ("Job 84861fb382ed | Hall 2 | chat", ("meta",)))
        claim = "Job 0123456789ab | Hall 2 | claim | Section 21 13 19 claim check\nBlind claim check."
        self.assertIn("| claim |", plain_text(claim))
        self.assertEqual(plain_text("Job is done | not a heading"), "Job is done | not a heading")

    def test_tables_are_aligned_in_mono(self):
        from fpfa.chat_render import markdown_segments, plain_text

        text = (
            "| piece | source |\n"
            "| --- | --- |\n"
            "| zone gallons | `zone_trapped_volume` |\n"
            "| t_total | **di_trip_to_water** |\n"
            "after"
        )
        lines = plain_text(text).split("\n")
        self.assertEqual(lines[0], "piece         source")
        self.assertTrue(set(lines[1]) <= {"─", " "})
        self.assertEqual(lines[2], "zone gallons  zone_trapped_volume")
        self.assertEqual(lines[3], "t_total       di_trip_to_water")
        self.assertEqual(lines[4], "after")
        segments = markdown_segments(text)
        self.assertEqual(segments[0], ("piece         source", ("pre", "pre_head")))
        # The newline after a shaded row is shaded too, so the block is one band.
        self.assertEqual(segments[1], ("\n", ("pre",)))
        self.assertEqual(segments[-2], ("\n", ("pre",)))
        self.assertEqual(segments[-1], ("after", ()))

    def test_table_without_a_rule_row_is_shown_as_written(self):
        from fpfa.chat_render import plain_text

        self.assertEqual(plain_text("| a | b |\n| c | d |"), "| a | b |\n| c | d |")

    def test_fenced_code_keeps_its_text(self):
        from fpfa.chat_render import markdown_segments, plain_text

        text = "Before\n```\nzone_gal = 281.3\n**not bold**\n```\nAfter"
        self.assertEqual(plain_text(text), "Before\nzone_gal = 281.3\n**not bold**\nAfter")
        self.assertIn(("zone_gal = 281.3", ("pre",)), markdown_segments(text))


class ChatTitleTests(unittest.TestCase):
    def setUp(self):
        try:
            import tkinter  # noqa: F401
        except ImportError:
            self.skipTest("tkinter is not installed")

    def test_title_comes_from_the_first_line(self):
        from fpfa.ui import UNTITLED_JOB, chat_title

        self.assertEqual(chat_title("hello there"), "hello there")
        self.assertEqual(chat_title("\n  Trim   family?  \nmore text"), "Trim family?")
        self.assertEqual(
            chat_title("How should I split a 40,000 ft2 data hall into DI zones?"),
            "How should I split a 40,000 ft2 data hall into…",
        )
        self.assertLessEqual(len(chat_title("x" * 200)), 48)
        self.assertEqual(chat_title("   "), UNTITLED_JOB)


if __name__ == "__main__":
    unittest.main()
