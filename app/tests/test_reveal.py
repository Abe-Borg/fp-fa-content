"""How a reply's words come onto the screen. No display is needed: the rules are pure."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))


class PaceTests(unittest.TestCase):
    def test_a_burst_drains_in_about_a_second_and_the_end_never_trickles(self):
        from fpfa.reveal import REVEAL_MIN_RATE, reveal_step

        self.assertEqual(reveal_step(0, 0.016), 0.0)
        self.assertEqual(reveal_step(-5, 0.016), 0.0)
        # A long frame cannot reveal more than is waiting.
        self.assertEqual(reveal_step(10, 5.0), 10.0)
        # A big backlog drains by its share; a small one keeps the floor pace.
        self.assertAlmostEqual(reveal_step(3000, 0.1), 3000 * (1 - 2.718281828 ** (-0.1 / 0.3)), delta=1.0)
        self.assertAlmostEqual(reveal_step(40, 0.1), REVEAL_MIN_RATE * 0.1, places=6)
        backlog, clock = 800.0, 0.0
        while backlog > 0.5:
            backlog -= reveal_step(int(backlog) + 1, 1 / 60)
            clock += 1 / 60
        self.assertGreater(clock, 0.6)
        self.assertLess(clock, 1.6)

    def test_the_pace_does_not_depend_on_the_frame_rate(self):
        from fpfa.reveal import Reveal

        text = "word " * 400

        def shown_after(seconds: float, frame: float) -> int:
            reveal = Reveal(text, shown=0)
            clock = 0.0
            while clock < seconds:
                reveal.advance(clock)
                clock += frame
            return reveal.shown

        fast, slow = shown_after(0.5, 1 / 120), shown_after(0.5, 1 / 30)
        self.assertLess(abs(fast - slow), len(text) * 0.12)
        self.assertGreater(fast, len(text) * 0.5)


class AlignTests(unittest.TestCase):
    def test_a_longer_text_carries_on_from_the_words_shown(self):
        from fpfa.reveal import align_shown

        self.assertEqual(align_shown("Zone total", "Zone total is 281.3 gal."), (10, True))
        self.assertEqual(align_shown("", "anything"), (0, True))
        # The finished reply can join its parts with other spacing.
        at, whole = align_shown("Trim is ASSUMED.\nPipe is", "Trim is ASSUMED.\n\nPipe is calculated.")
        self.assertTrue(whole)
        self.assertEqual("Trim is ASSUMED.\n\nPipe is calculated."[:at], "Trim is ASSUMED.\n\nPipe is")
        # Words that are no longer there stop the match where they diverge.
        at, whole = align_shown("Zone total is 300", "Zone total is 281.3 gal.")
        self.assertFalse(whole)
        self.assertEqual("Zone total is 281.3 gal."[:at], "Zone total is")


class BoundaryTests(unittest.TestCase):
    def test_the_settled_part_ends_after_the_last_blank_line(self):
        from fpfa.reveal import stable_boundary

        text = "First paragraph.\n\nSecond paragraph.\n\nThird, still growing"
        self.assertEqual(text[stable_boundary(text):], "Third, still growing")
        self.assertEqual(stable_boundary("No break yet"), 0)
        self.assertEqual(stable_boundary(""), 0)
        # Nothing past the limit is settled: text still fading stays in the growing part.
        limit = text.index("Second") + 3
        self.assertEqual(text[stable_boundary(text, limit):limit], "Sec")
        self.assertEqual(stable_boundary(text, 5), 0)

    def test_a_fenced_block_is_never_cut(self):
        from fpfa.reveal import stable_boundary

        text = "Intro.\n\n```\nzone_gal = 281.3\n\nt_total = 38.1\n```\n\nAfter"
        self.assertEqual(text[stable_boundary(text):], "After")
        open_fence = "Intro.\n\n```\nzone_gal = 281.3\n\nt_total"
        self.assertEqual(open_fence[stable_boundary(open_fence):], "```\nzone_gal = 281.3\n\nt_total")

    def test_drawing_the_two_parts_gives_the_same_text_as_drawing_the_whole(self):
        from fpfa.chat_render import markdown_segments
        from fpfa.reveal import stable_boundary

        reply = (
            "Job 6b34e02bf8dc | Sample | chat\n"
            "## Design basis\n\nThe zone is **double-interlock**.\n\n"
            "| Item | Value |\n| --- | --- |\n| Pipe | 276.3 gal |\n| Trim | 5.0 gal |\n\n"
            "- First point with `t_total`\n- Second point\n\n```\nzone_gal = 281.3\n\nmore\n```\n\n"
            "1. Confirm the trim.\n2. Confirm the AHJ."
        )

        def text_of(segments) -> str:
            return "".join(chunk for chunk, _tags in segments)

        fence_only = 0
        for end in range(len(reply) + 1):
            shown = reply[:end]
            cut = stable_boundary(shown)
            settled = markdown_segments(shown[:cut]) if cut else []
            growing = markdown_segments(shown[cut:], caption=cut == 0) if shown[cut:] else []
            together = text_of(settled) + text_of(growing)
            whole = text_of(markdown_segments(shown))
            if shown[cut:] and not growing:
                # The growing part is only an opening code fence, which draws nothing until
                # its first line arrives. For that moment the two differ by one line break.
                fence_only += 1
                self.assertEqual(together.rstrip("\n"), whole.rstrip("\n"), f"prefix of {end} characters")
            else:
                self.assertEqual(together, whole, f"prefix of {end} characters")
        self.assertLessEqual(fence_only, 4)


class InlineTests(unittest.TestCase):
    def test_a_half_written_span_is_drawn_as_it_will_end_up(self):
        from fpfa.chat_render import markdown_segments
        from fpfa.reveal import settle_inline

        self.assertEqual(settle_inline("The zone is a **double-interl"), "The zone is a **double-interl**")
        self.assertEqual(settle_inline("and `t_tot"), "and `t_tot`")
        # A marker with nothing after it yet is held back.
        self.assertEqual(settle_inline("The zone is a **"), "The zone is a ")
        self.assertEqual(settle_inline("The zone is a *"), "The zone is a ")
        self.assertEqual(settle_inline("and `"), "and ")
        # The first half of the closing pair: the span is closed, the stray asterisk held back.
        self.assertEqual(settle_inline("a **bold*"), "a **bold**")
        # Finished spans, earlier lines, and plain text are left as written.
        for text in ("", "plain words", "a **bold** word and `code`", "**open on an earlier line\nnext line",
                     "names such as t_total and zone_gal"):
            self.assertEqual(settle_inline(text), text)
        # Inside an open code fence nothing is a marker.
        fenced = "Intro\n```\nvalue = a ** b"
        self.assertEqual(settle_inline(fenced), fenced)
        closed = "```\ncode\n```\nthen **bol"
        self.assertEqual(settle_inline(closed), "```\ncode\n```\nthen **bol**")
        drawn = "".join(chunk for chunk, _tags in markdown_segments(settle_inline("The zone is a **double-interl")))
        self.assertEqual(drawn, "The zone is a double-interl")
        self.assertIn(("double-interl", ("bold",)), markdown_segments(settle_inline("The zone is a **double-interl")))


class RevealTests(unittest.TestCase):
    def test_words_arrive_fade_and_settle(self):
        from fpfa.reveal import FADE_MS, Reveal

        reveal = Reveal("", shown=0)
        self.assertFalse(reveal.flowing)
        self.assertFalse(reveal.advance(0.0))
        reveal.feed("Trapped volume is 276.3 gal of pipe (calculated).")
        self.assertTrue(reveal.flowing)
        self.assertEqual(reveal.text, "")
        clock = 0.0
        while reveal.flowing:
            reveal.advance(clock)
            clock += 1 / 60
        self.assertEqual(reveal.text, reveal.target)
        self.assertTrue(reveal.fading(clock))
        fades = reveal.fades(clock, 6)
        self.assertTrue(fades)
        # Newest first: distances grow, and an older piece is further along its fade.
        distances = [distance for distance, _step in fades]
        steps = [step for _distance, step in fades]
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(steps, sorted(steps))
        self.assertLessEqual(distances[-1], len(reveal.target))
        self.assertLess(reveal.settled(clock), len(reveal.target))
        later = clock + FADE_MS / 1000.0 + 0.05
        self.assertFalse(reveal.fading(later))
        self.assertEqual(reveal.fades(later, 6), [])
        self.assertEqual(reveal.settled(later), len(reveal.target))
        self.assertFalse(reveal.active(later))

    def test_a_text_the_reveal_starts_with_is_shown_at_once(self):
        from fpfa.reveal import Reveal

        reveal = Reveal("A reply from the saved thread.")
        self.assertEqual(reveal.text, "A reply from the saved thread.")
        self.assertFalse(reveal.flowing)
        self.assertFalse(reveal.advance(1.0))

    def test_a_finished_reply_carries_on_and_a_changed_one_backs_up(self):
        from fpfa.reveal import Reveal

        streamed = "Job 1a2b3c4d | Hall | chat\nThe zone total is 281.3 gal."
        reveal = Reveal(streamed, shown=0)
        clock = 0.0
        while reveal.shown < 40:
            reveal.advance(clock)
            clock += 1 / 60
        shown = reveal.text
        # The saved turn adds a team summary after the same words.
        final = streamed + "\n\n**Team**\n- fp-sprinkler recorded 2 findings."
        reveal.feed(final)
        self.assertEqual(reveal.text, shown)
        self.assertTrue(reveal.flowing)
        # A retry starts the reply over: nothing of the failed attempt stays.
        reveal.feed("Job 1a2b3c4d | Hall | chat\nA different answer.")
        self.assertTrue(reveal.target.startswith(reveal.text))
        self.assertLessEqual(reveal.shown, len("Job 1a2b3c4d | Hall | chat\n") + 2)
        reveal.finish()
        self.assertEqual(reveal.text, reveal.target)
        self.assertFalse(reveal.fading(clock))

    def test_a_stalled_window_does_not_dump_its_backlog_in_one_frame(self):
        from fpfa.reveal import MAX_FRAME_SECONDS, Reveal, reveal_step

        text = "x" * 4000
        reveal = Reveal(text, shown=0)
        reveal.advance(0.0)
        first = reveal.shown
        reveal.advance(30.0)
        self.assertLessEqual(reveal.shown - first, int(reveal_step(len(text) - first, MAX_FRAME_SECONDS)) + 1)
        self.assertLess(reveal.shown, len(text))


if __name__ == "__main__":
    unittest.main()
