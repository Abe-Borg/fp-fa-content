"""Colour schemes, the stylesheet that carries them, and the app icon.

The schemes are listed in fpfa/theme.py and defined for the page in
app/frontend/src/styles.css; the two must agree token for token. None of
this needs a display.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

# The chrome, paper, and accent of each scheme, as the practice's other apps define them
# (Spec Surgeon's frontend/src/lib/theme.ts, which Build-a-Spec carries too).
SWATCHES = {
    "clay": ("Warm Clay", "#262624", "#faf9f5", "#d97757"),
    "blueprint": ("Blueprint", "#121a26", "#f8fafc", "#2e8aee"),
    "graphite": ("Graphite & Teal", "#1b1d1f", "#fbfbfa", "#269c9b"),
    "carbon": ("Carbon & Hi-Vis", "#0b0b0c", "#ffffff", "#f55b00"),
    "linen": ("Linen", "#f5f1ea", "#fffdf9", "#a64b29"),
}


def _isolate_data() -> None:
    os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-theme-")
    os.environ.pop("FPFA_THEME", None)


class ShapeTests(unittest.TestCase):
    def test_png_round_trip(self):
        from fpfa import shapes

        pixels = bytes([10, 20, 30, 255, 40, 50, 60, 128] * 6)
        data = shapes.encode_png(4, 3, pixels)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(shapes.png_size(data), (4, 3))
        self.assertEqual(shapes.decode_png(data), (4, 3, pixels))
        with self.assertRaises(ValueError):
            shapes.encode_png(4, 3, pixels[:-4])

    def _pixel(self, data: bytes, x: int, y: int) -> tuple:
        from fpfa import shapes

        width, _height, pixels = shapes.decode_png(data)
        offset = (y * width + x) * 4
        return tuple(pixels[offset:offset + 4])

    def test_star_mark_and_icon_file(self):
        from fpfa import shapes

        star = shapes.star_mark(32, "#d97757", "#1d1d1b")
        self.assertEqual(self._pixel(star, 16, 16), (0xD9, 0x77, 0x57, 255))
        # Along an arm of the star, and in a quarter between two arms.
        self.assertEqual(self._pixel(star, 12, 16), (0xD9, 0x77, 0x57, 255))
        self.assertEqual(self._pixel(star, 16, 12), (0xD9, 0x77, 0x57, 255))
        self.assertEqual(self._pixel(star, 6, 6), (0x1D, 0x1D, 0x1B, 255))
        self.assertEqual(self._pixel(star, 0, 0)[3], 0)
        ico = shapes.encode_ico([shapes.star_mark(size, "#d97757", "#1d1d1b") for size in (16, 32)])
        self.assertEqual(ico[:6], b"\x00\x00\x01\x00\x02\x00")
        self.assertEqual((ico[6], ico[7], ico[22], ico[23]), (16, 16, 32, 32))

    def test_mix_and_contrast(self):
        from fpfa import shapes

        self.assertEqual(shapes.mix("#ffffff", "#000000", 0.5), "#808080")
        self.assertEqual(shapes.mix("#d97757", "#262624", 1.0), "#d97757")
        self.assertEqual(shapes.mix("#d97757", "#262624", 0.0), "#262624")
        self.assertAlmostEqual(shapes.contrast("#ffffff", "#000000"), 21.0, places=1)
        self.assertAlmostEqual(shapes.contrast("#777777", "#777777"), 1.0, places=3)


class SchemeTests(unittest.TestCase):
    def test_the_five_schemes_carry_the_sibling_apps_colours(self):
        from fpfa import theme

        self.assertEqual(theme.SCHEME_ORDER, tuple(SWATCHES))
        self.assertEqual(theme.DEFAULT_SCHEME, "clay")
        for scheme_id, (name, bg, paper, accent) in SWATCHES.items():
            scheme = theme.SCHEMES[scheme_id]
            self.assertEqual(scheme.name, name)
            self.assertEqual((scheme.colors["bg"], scheme.colors["paper"], scheme.colors["accent"]), (bg, paper, accent))
            self.assertEqual(set(scheme.colors), set(theme.TOKENS))
            self.assertTrue(scheme.blurb)
        self.assertEqual([s.dark for s in theme.SCHEMES.values()], [True, True, True, True, False])

    def test_text_reads_on_every_surface_in_every_scheme(self):
        from fpfa import theme
        from fpfa.shapes import contrast

        for scheme in theme.SCHEMES.values():
            c = scheme.colors
            for surface in ("bg", "surface", "raised"):
                self.assertGreaterEqual(contrast(c["ink"], c[surface]), 7.0, (scheme.id, surface))
                self.assertGreaterEqual(contrast(c["ink_dim"], c[surface]), 4.5, (scheme.id, surface))
            for surface in ("bg", "surface"):
                self.assertGreaterEqual(contrast(c["ink_faint"], c[surface]), 3.0, (scheme.id, surface))
                self.assertGreaterEqual(contrast(c["accent"], c[surface]), 3.0, (scheme.id, surface))
            self.assertGreaterEqual(contrast(c["on_accent"], c["accent"]), 3.0, scheme.id)
            self.assertGreaterEqual(contrast(c["paper_ink"], c["paper"]), 7.0, scheme.id)

    def test_the_keyboard_ring_shows_on_every_fill_it_is_drawn_on(self):
        from fpfa import theme
        from fpfa.shapes import contrast

        try:
            for scheme_id in theme.SCHEME_ORDER:
                theme.colors.use(scheme_id)
                c = theme.colors
                # The page's ring (:focus-visible) on a button, a well on a card, a selected toolbar pill.
                for fill in (c.raised_hover, c.bg, c.accent_soft):
                    self.assertGreaterEqual(contrast(c.accent, fill), 3.0, (scheme_id, fill))
                # On the accent itself the ring is the colour of the text on it.
                self.assertGreaterEqual(contrast(c.on_accent, c.accent), 3.0, scheme_id)
                # A scheme card: the focused one in the ink, the one in use in the accent.
                self.assertGreaterEqual(contrast(c.ink, c.raised), 7.0, scheme_id)
                self.assertGreaterEqual(contrast(c.accent, c.raised), 3.0, scheme_id)
        finally:
            theme.colors.use(theme.DEFAULT_SCHEME)

    def test_a_scheme_must_define_every_token_and_no_other(self):
        from fpfa import theme

        tokens = dict(theme.SCHEMES["clay"].colors)
        tokens.pop("ok")
        with self.assertRaises(ValueError):
            theme._scheme("broken", "Broken", "missing a token", True, **tokens)
        with self.assertRaises(ValueError):
            theme._scheme("extra", "Extra", "one too many", True, **theme.SCHEMES["clay"].colors, shadow="#000000")

    def test_colours_change_in_place_and_fade_runs_from_background_to_text(self):
        from fpfa import theme
        from fpfa.shapes import contrast

        colors = theme.Colors()
        self.assertEqual((colors.scheme, colors.bg, colors.dark), ("clay", "#262624", True))
        self.assertEqual(colors.use("linen"), "linen")
        self.assertEqual((colors.bg, colors.accent, colors.dark), ("#f5f1ea", "#a64b29", False))
        self.assertEqual(colors.use("no-such-scheme"), "clay")
        steps = [contrast(colors.fade(step), colors.bg) for step in range(theme.FADE_STEPS)]
        self.assertEqual(steps, sorted(steps))
        self.assertLess(steps[0], 2.0)
        self.assertGreater(steps[-1], 7.0)

    def test_the_choice_is_saved_and_one_run_can_override_it(self):
        _isolate_data()
        from fpfa import theme
        from fpfa.paths import read_config, write_config

        self.assertEqual(theme.saved_scheme(), "clay")
        self.assertEqual(theme.remember_scheme("blueprint"), "blueprint")
        self.assertEqual(read_config()["appearance"], "blueprint")
        self.assertEqual(theme.saved_scheme(), "blueprint")
        self.assertEqual(theme.remember_scheme("mauve"), "clay")
        write_config({"appearance": 7})
        self.assertEqual(theme.saved_scheme(), "clay")
        write_config({"appearance": "carbon"})
        os.environ["FPFA_THEME"] = "Linen"
        try:
            self.assertEqual(theme.saved_scheme(), "linen")
        finally:
            os.environ.pop("FPFA_THEME", None)
        self.assertEqual(theme.saved_scheme(), "carbon")

STYLES = APP_DIR / "frontend" / "src" / "styles.css"


def _css_schemes() -> dict[str, dict[str, str]]:
    """Each scheme's tokens as styles.css defines them, by scheme id."""
    text = STYLES.read_text(encoding="utf-8")
    found: dict[str, dict[str, str]] = {}
    for selectors, body in __import__("re").findall(r"([^{}]+)\{([^{}]*)\}", text):
        ids = __import__("re").findall(r'data-theme="([a-z]+)"', selectors)
        if not ids:
            continue
        tokens = dict(__import__("re").findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;", body))
        for scheme_id in ids:
            found.setdefault(scheme_id, {}).update({name.replace("-", "_"): value.lower() for name, value in tokens.items()})
    return found


class StylesheetTests(unittest.TestCase):
    def test_the_stylesheet_defines_every_scheme_token_for_token(self):
        from fpfa import theme

        css = _css_schemes()
        self.assertEqual(sorted(css), sorted(theme.SCHEME_ORDER))
        for scheme_id, scheme in theme.SCHEMES.items():
            self.assertEqual(css[scheme_id], {token: value.lower() for token, value in scheme.colors.items()}, scheme_id)

    def test_warm_clay_is_also_the_default_of_root(self):
        text = STYLES.read_text(encoding="utf-8")
        self.assertIn(':root,\n:root[data-theme="clay"] {', text)

    def test_a_rule_names_no_colour_of_its_own(self):
        """Outside the scheme blocks, every colour is a token or a mix of tokens."""
        import re

        text = STYLES.read_text(encoding="utf-8")
        outside = re.sub(r':root(?:\[data-theme="[a-z]+"\])?(?:,\s*:root\[data-theme="[a-z]+"\])?\s*\{[^{}]*?--bg:[^{}]*\}', "", text)
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b", outside), [])
        self.assertEqual(re.findall(r"\brgba?\(|\bhsla?\(", outside), [])
        for word in ("black", "white", "gray", "grey"):
            self.assertNotRegex(outside, rf":\s*[^;]*\b{word}\b")


class DeskSchemeTests(unittest.TestCase):
    def test_settings_saves_the_scheme_and_the_page_reads_it(self):
        _isolate_data()
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        from fpfa.desk import Desk
        from fpfa.paths import read_config, write_config

        write_config({"key_backend": "file", "appearance": "graphite"})
        desk = Desk()
        self.addCleanup(desk.close)
        state = desk.snapshot()
        self.assertEqual(state["settings"]["scheme"], "graphite")
        self.assertEqual([item["id"] for item in state["settings"]["schemes"]], list(SWATCHES))
        self.assertEqual(state["settings"]["schemes"][0]["colors"]["accent"], "#d97757")
        shell_calls = []
        desk.shell.scheme_changed = shell_calls.append
        self.assertEqual(desk.set_scheme("carbon"), "carbon")
        self.assertEqual(read_config()["appearance"], "carbon")
        self.assertEqual(desk.snapshot()["settings"]["scheme"], "carbon")
        self.assertEqual(shell_calls, ["carbon"])
        self.assertIn("Carbon & Hi-Vis", desk.status.get())
        # An unknown id falls back to the default rather than saving nonsense.
        self.assertEqual(desk.set_scheme("mauve"), "clay")

    def test_the_title_bar_call_is_harmless_off_windows(self):
        from fpfa import theme

        if sys.platform == "win32":
            self.skipTest("Windows takes the call")
        self.assertFalse(theme.style_title_bar(1234, "linen"))
        self.assertFalse(theme.style_title_bar(0, "linen"))


if __name__ == "__main__":
    unittest.main()
