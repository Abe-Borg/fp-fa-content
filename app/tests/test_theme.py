"""Colour schemes, generated pictures, and the ttk theme.

The first two classes need no display. The window tests skip without one.
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

    def test_rounded_rect_has_clear_corners_a_border_and_a_solid_middle(self):
        from fpfa import shapes

        data = shapes.rounded_rect(24, 24, 8, "#3a3936", border="#45443f")
        self.assertEqual(self._pixel(data, 0, 0)[3], 0)
        self.assertEqual(self._pixel(data, 23, 23)[3], 0)
        self.assertEqual(self._pixel(data, 12, 12), (0x3A, 0x39, 0x36, 255))
        # The top edge, away from a corner, is the border colour.
        self.assertEqual(self._pixel(data, 12, 0), (0x45, 0x44, 0x3F, 255))
        # A corner pixel on the curve is partly covered: that is the smoothing.
        partial = [self._pixel(data, x, y)[3] for x in range(8) for y in range(8)]
        self.assertTrue(any(0 < alpha < 255 for alpha in partial))
        # Four equal corners: the picture is the same in every quarter.
        for x, y in ((2, 3), (5, 1), (7, 7)):
            self.assertEqual(self._pixel(data, x, y), self._pixel(data, 23 - x, y))
            self.assertEqual(self._pixel(data, x, y), self._pixel(data, x, 23 - y))

    def test_a_corner_can_be_tighter_than_the_others(self):
        from fpfa import shapes

        data = shapes.rounded_rect(40, 40, (16, 16, 4, 16), "#ff0000")
        # Three pixels in from the bottom-right: inside a 4 px corner, outside a 16 px one.
        self.assertEqual(self._pixel(data, 36, 36)[3], 255)
        self.assertEqual(self._pixel(data, 3, 3)[3], 0)
        with self.assertRaises(ValueError):
            shapes.rounded_rect(10, 10, (1, 2, 3), "#000000")

    def test_ring_overlay_extend_and_icons(self):
        from fpfa import shapes

        ring = shapes.rounded_rect(24, 24, 8, None, border="#112233")
        self.assertEqual(self._pixel(ring, 12, 12)[3], 0)
        self.assertEqual(self._pixel(ring, 12, 0), (0x11, 0x22, 0x33, 255))
        box = shapes.rounded_rect(18, 18, 5, "#d97757")
        tick = shapes.icon("check", 18, "#ffffff")
        marked = shapes.overlay(box, tick)
        whites = sum(1 for x in range(18) for y in range(18) if self._pixel(marked, x, y)[:3] == (255, 255, 255))
        self.assertGreater(whites, 6)
        wide = shapes.extend(box, right=8)
        self.assertEqual(shapes.png_size(wide), (26, 18))
        self.assertEqual(self._pixel(wide, 25, 9)[3], 0)
        self.assertEqual(self._pixel(wide, 9, 9), (0xD9, 0x77, 0x57, 255))
        for name in shapes.ICONS:
            self.assertEqual(shapes.png_size(shapes.icon(name, 18, "#eceae4")), (18, 18))

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
    def setUp(self):
        # The schemes live beside the ttk styles, so the module needs tkinter, though no display.
        try:
            import tkinter  # noqa: F401
        except ImportError:
            self.skipTest("tkinter is not installed")

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

    def test_every_picture_is_drawn_and_a_stretched_one_has_a_middle(self):
        from fpfa import shapes, theme

        theme.colors.use("clay")
        pictures = theme._pictures(lambda value: int(round(value)))
        for name in ("btn_accent", "btn_soft", "field", "field_focus", "card", "paper", "composer", "bubble",
                     "chip", "thumb_v", "check_on", "icon_more", "dot_0", "dot_4", "mark", "mark_large"):
            self.assertIn(name, pictures)
        # A nine-slice picture keeps a stretchable middle between its two slices.
        px = lambda value: int(round(value))  # noqa: E731
        for name, radius in (("btn_accent", theme.RADIUS), ("card", theme.RADIUS_CARD),
                             ("composer", theme.RADIUS_COMPOSER), ("bubble", theme.RADIUS_BUBBLE)):
            width, height = shapes.png_size(pictures[name])
            self.assertGreater(width, 2 * theme._slice(px, radius), name)
            self.assertGreater(height, 2 * theme._slice(px, radius), name)
        bigger = theme._pictures(lambda value: int(round(value * 2)))
        self.assertEqual(shapes.png_size(bigger["btn_accent"])[0], 2 * shapes.png_size(pictures["btn_accent"])[0])


class ThemeWindowTests(unittest.TestCase):
    def _root(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        try:
            import tkinter as tk
        except ImportError:
            self.skipTest("tkinter is not installed")
        _isolate_data()
        root = tk.Tk()
        self.addCleanup(root.destroy)
        return root

    def test_apply_theme_builds_the_styles_and_a_scheme_change_repaints(self):
        import tkinter as tk
        from tkinter import ttk

        from fpfa import theme

        root = self._root()
        look = theme.apply_theme(root, "clay")
        self.assertIs(theme.theme_of(root), look)
        self.assertIs(theme.apply_theme(root, "clay"), look)
        style = ttk.Style(root)
        self.assertEqual(style.theme_use(), "cynosure")
        self.assertEqual(style.lookup("TLabel", "foreground"), "#eceae4")
        self.assertEqual(style.lookup("OnSide.TFrame", "background"), "#2f2f2d")
        self.assertEqual(style.lookup("OnPaper.TLabel", "foreground"), "#2c2b27")
        self.assertIn("Accent.button", str(style.layout("Accent.TButton")))
        self.assertIn("Field.field", str(style.layout("TEntry")))
        painted = look.paint(tk.Label(root, text="x"), bg="surface", fg="ink_dim")
        self.assertEqual((str(painted.cget("bg")), str(painted.cget("fg"))), ("#2f2f2d", "#a8a49a"))
        picture = look.image("btn_accent")
        heard = []
        look.on_change(lambda: heard.append(theme.colors.scheme))

        self.assertEqual(look.set_scheme("linen"), "linen")
        self.assertEqual(heard, ["linen"])
        self.assertEqual((str(painted.cget("bg")), str(painted.cget("fg"))), ("#ece6dc", "#5f564b"))
        self.assertEqual(style.lookup("TLabel", "foreground"), "#2a2620")
        self.assertEqual(str(root.cget("bg")), "#f5f1ea")
        # The same picture object, redrawn: every control that uses it follows.
        self.assertIs(look.image("btn_accent"), picture)
        red, green, blue = picture.get(picture.width() // 2, picture.height() // 2)
        self.assertEqual("#%02x%02x%02x" % (red, green, blue), "#a64b29")
        # A destroyed widget is dropped without stopping the repaint.
        painted.destroy()
        self.assertEqual(look.set_scheme("clay"), "clay")
        if sys.platform != "win32":
            # Only Windows has a title bar the app can colour.
            self.assertFalse(theme.style_title_bar(root))

    def test_the_window_opens_in_the_saved_scheme_and_settings_changes_it(self):
        from fpfa import theme
        from fpfa.paths import read_config, write_config
        from fpfa.ui import App

        root = self._root()
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        write_config({"key_backend": "file", "appearance": "graphite"})
        app = App(root)
        root.update()
        self.assertEqual(app.theme.scheme, "graphite")
        self.assertEqual(str(app.chat_view.cget("bg")), "#1b1d1f")
        self.assertEqual(root.title(), "+Cynosure")
        app.open_settings()
        root.update()
        cards = [child for child in _walk(app._settings_window) if child.winfo_class() == "TFrame"
                 and "Swatch" in str(child.cget("style"))]
        self.assertEqual(len(cards), 5)
        selected = [card for card in cards if card.instate(["selected"])]
        self.assertEqual(len(selected), 1)
        # Clicking the Carbon card recolours the window at once and saves the choice.
        cards[theme.SCHEME_ORDER.index("carbon")].event_generate("<Button-1>")
        root.update()
        self.assertEqual(app.theme.scheme, "carbon")
        self.assertEqual(read_config()["appearance"], "carbon")
        self.assertEqual(str(app.chat_view.cget("bg")), "#0b0b0c")
        self.assertEqual(str(app.chat_view.tag_cget("body", "foreground")), "#f4f4f5")
        self.assertEqual(str(app.results.cget("bg")), "#ffffff")
        self.assertTrue(cards[theme.SCHEME_ORDER.index("carbon")].instate(["selected"]))
        self.assertFalse(cards[theme.SCHEME_ORDER.index("graphite")].instate(["selected"]))
        self.assertIn("Carbon & Hi-Vis", app.status.get())


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


if __name__ == "__main__":
    unittest.main()
