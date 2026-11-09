"""Look of the desktop window: colour schemes, fonts, the ttk theme, and Windows DPI.

The window is plain tkinter. This module keeps every colour, font, and style
in one place so ui.py only names a style. Nothing here reads the content pack
or the API key.

Colour schemes. The five schemes and their colours are copied from the
practice's other desktop apps (Spec Surgeon's frontend/src/index.css, which
Build-a-Spec carries too) and adapted to tkinter: Warm Clay is the default,
and Blueprint, Graphite & Teal, Carbon & Hi-Vis, and Linen redefine every
token. Settings picks one, and the choice is saved in config.json. A widget
never names a colour of its own. It asks for a token (`colors.bg`) or is
registered with `Theme.paint`, so a scheme change repaints it.

Rounded controls. tkinter draws square corners, so buttons, fields, cards,
tabs, check boxes, and scrollbar thumbs are small pictures from shapes.py,
used as ttk image elements that stretch by nine slices. Changing the scheme
redraws the same pictures in place and every control follows.
"""

from __future__ import annotations

import base64
import sys
import tkinter as tk
import tkinter.font as tkfont
import weakref
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from fpfa import shapes
from fpfa.shapes import mix

TOKENS = (
    "bg", "surface", "raised", "edge",
    "ink", "ink_dim", "ink_faint",
    "accent", "accent_hover", "on_accent",
    "paper", "paper_edge", "paper_ink", "paper_dim", "paper_faint",
    "ok", "warn", "err", "err_tint",
)


@dataclass(frozen=True)
class Scheme:
    """One colour scheme: its id, its name in Settings, and a colour per token."""

    id: str
    name: str
    blurb: str
    dark: bool
    colors: dict


def _scheme(scheme_id: str, name: str, blurb: str, dark: bool, **tokens: str) -> Scheme:
    missing = [token for token in TOKENS if token not in tokens]
    if missing or len(tokens) != len(TOKENS):
        raise ValueError(f"scheme {scheme_id} must define exactly the tokens in TOKENS; missing {missing}")
    return Scheme(scheme_id, name, blurb, dark, dict(tokens))


SCHEMES: dict[str, Scheme] = {
    scheme.id: scheme
    for scheme in (
        _scheme(
            "clay", "Warm Clay", "Warm charcoal, cream paper, terracotta.", True,
            bg="#262624", surface="#2f2f2d", raised="#3a3936", edge="#45443f",
            ink="#eceae4", ink_dim="#a8a49a", ink_faint="#7d7a72",
            accent="#d97757", accent_hover="#e08b6d", on_accent="#ffffff",
            paper="#faf9f5", paper_edge="#e6e2d8", paper_ink="#2c2b27", paper_dim="#8a8578",
            paper_faint="#b5b0a3", ok="#7fa650", warn="#d4a04c", err="#c65b4e", err_tint="#fbeeec",
        ),
        _scheme(
            "blueprint", "Blueprint", "Deep navy, cool white paper, drafting blue.", True,
            bg="#121a26", surface="#18212f", raised="#212c3d", edge="#2f3d53",
            ink="#e3e9f2", ink_dim="#9aa8bc", ink_faint="#6e7d93",
            accent="#2e8aee", accent_hover="#4da0f5", on_accent="#08111d",
            paper="#f8fafc", paper_edge="#dbe2ec", paper_ink="#1b2433", paper_dim="#66748a",
            paper_faint="#a5b0c0", ok="#428a5e", warn="#e2ad4f", err="#dc4739", err_tint="#fcefee",
        ),
        _scheme(
            "graphite", "Graphite & Teal", "Neutral charcoal, white paper, teal.", True,
            bg="#1b1d1f", surface="#222528", raised="#2b2f33", edge="#3a3f45",
            ink="#e7e9eb", ink_dim="#a3a9b0", ink_faint="#767d85",
            accent="#269c9b", accent_hover="#37acaa", on_accent="#061b1b",
            paper="#fbfbfa", paper_edge="#e1e4e6", paper_ink="#1f2326", paper_dim="#6c747c",
            paper_faint="#a8afb5", ok="#5f8f3a", warn="#e0a54a", err="#d94b3c", err_tint="#fcefed",
        ),
        _scheme(
            "carbon", "Carbon & Hi-Vis", "True black, pure white paper, safety orange.", True,
            bg="#0b0b0c", surface="#121214", raised="#1b1b1e", edge="#2c2c31",
            ink="#f4f4f5", ink_dim="#a9a9b0", ink_faint="#7a7a82",
            accent="#f55b00", accent_hover="#ff7d30", on_accent="#140700",
            paper="#ffffff", paper_edge="#e2e2e4", paper_ink="#141416", paper_dim="#66666d",
            paper_faint="#a6a6ad", ok="#318c52", warn="#e8b230", err="#e12c31", err_tint="#fdecec",
        ),
        _scheme(
            "linen", "Linen", "Light and warm: linen, off-white paper, terracotta.", False,
            bg="#f5f1ea", surface="#ece6dc", raised="#fffdf9", edge="#dcd3c5",
            ink="#2a2620", ink_dim="#5f564b", ink_faint="#877e72",
            accent="#a64b29", accent_hover="#8d3f22", on_accent="#ffffff",
            paper="#fffdf9", paper_edge="#e6dfd3", paper_ink="#2a2620", paper_dim="#6c6459",
            paper_faint="#aaa293", ok="#3c7e39", warn="#9d671b", err="#b33d2c", err_tint="#fbeceb",
        ),
    )
}
DEFAULT_SCHEME = "clay"
SCHEME_ORDER = tuple(SCHEMES)
# How many steps a newly revealed word takes from the background to the text colour.
FADE_STEPS = 6


def resolve_scheme(value) -> str:
    """A known scheme id, else the default (a hand-edited config or an older build)."""
    return value if isinstance(value, str) and value in SCHEMES else DEFAULT_SCHEME


def saved_scheme() -> str:
    """The scheme Settings last saved. FPFA_THEME overrides it for one run."""
    import os

    from fpfa.paths import read_config

    override = os.environ.get("FPFA_THEME")
    if override:
        return resolve_scheme(override.strip().lower())
    return resolve_scheme(read_config().get("appearance"))


def remember_scheme(scheme_id: str) -> str:
    from fpfa.paths import write_config

    chosen = resolve_scheme(scheme_id)
    write_config({"appearance": chosen})
    return chosen


class Colors:
    """The colours of the scheme in use. Attributes change in place when the scheme changes."""

    def __init__(self) -> None:
        self.use(DEFAULT_SCHEME)

    def use(self, scheme_id: str) -> str:
        scheme = SCHEMES[resolve_scheme(scheme_id)]
        self.scheme = scheme.id
        self.dark = scheme.dark
        for token in TOKENS:
            setattr(self, token, scheme.colors[token])
        # Colours worked out from the tokens, the way the web apps use color-mix().
        self.accent_soft = mix(self.accent, self.bg, 0.16)
        self.accent_pressed = mix(self.accent, "#000000", 0.86)
        self.accent_disabled = mix(self.accent, self.bg, 0.38)
        self.select = mix(self.accent, self.bg, 0.36)
        self.raised_hover = mix(self.ink, self.raised, 0.07)
        self.raised_pressed = mix(self.ink, self.raised, 0.13)
        self.side_hover = mix(self.ink, self.surface, 0.06)
        self.disabled_ink = mix(self.ink, self.bg, 0.36)
        self.focus_edge = mix(self.accent, self.edge, 0.70)
        self.banner = mix(self.accent, self.surface, 0.14)
        self.banner_edge = mix(self.accent, self.edge, 0.45)
        self.paper_select = mix(self.accent, self.paper, 0.24)
        self.paper_rule = mix(self.paper_ink, self.paper, 0.22)
        self.shimmer = mix(self.ink, self.bg, 0.92)
        return scheme.id

    def fade(self, step: int, *, onto: str | None = None) -> str:
        """Step 0 is nearly the background, the last step nearly the text colour."""
        share = (step + 1) / (FADE_STEPS + 1)
        return mix(self.ink, onto or self.bg, share)


colors = Colors()

UI_FAMILIES = (
    "Segoe UI",
    "Segoe UI Variable Text",
    "Inter",
    "Helvetica Neue",
    "Cantarell",
    "Noto Sans",
    "DejaVu Sans",
)
# The display face of the headings and the wordmark, as in the other apps.
DISPLAY_FAMILIES = (
    "Georgia",
    "Cambria",
    "Charter",
    "Liberation Serif",
    "Noto Serif",
    "DejaVu Serif",
)
MONO_FAMILIES = (
    "Cascadia Code",
    "Cascadia Mono",
    "Consolas",
    "JetBrains Mono",
    "DejaVu Sans Mono",
    "Liberation Mono",
)

# Flat widgets take their background from the surface they sit on. A style
# named "OnSide.Accent.TButton" is "Accent.TButton" drawn on the sidebar colour.
_SURFACES = (("OnSide", "surface"), ("OnCard", "raised"), ("OnPaper", "paper"))
_VARIANT_STYLES = (
    "TFrame", "TLabel", "Dim.TLabel", "Small.TLabel", "Faint.TLabel", "Section.TLabel", "Footer.TLabel",
    "Job.TLabel", "Heading.TLabel", "Title.TLabel", "Link.TLabel", "Wordmark.TLabel", "Plus.TLabel",
    "Chip.TLabel", "Status.TLabel", "Icon.TLabel",
    "TButton", "Accent.TButton", "Ghost.TButton", "Sidebar.TButton", "Danger.TButton",
    "TEntry", "TCombobox", "TCheckbutton", "Toolbar.Toolbutton", "Toolbar.TMenubutton", "Icon.TMenubutton",
    "Vertical.TScrollbar", "Horizontal.TScrollbar", "TSeparator",
    "Card.TFrame", "Panel.TFrame", "Paper.TFrame", "Swatch.TFrame", "Composer.TFrame", "Bubble.TFrame",
    "Banner.TFrame", "Field.TFrame", "TNotebook", "TNotebook.Tab", "Treeview", "Treeview.Heading",
)


class Theme:
    """Fonts, pictures, and the pixel scale for one window, and the scheme it is drawn in."""

    def __init__(self, root: tk.Misc, scale: float, ui_family: str, mono_family: str, display_family: str):
        self.root = root
        self.scale = scale
        self.ui_family = ui_family
        self.mono_family = mono_family
        self.display_family = display_family
        self.fonts: dict = {}
        self.images: dict[str, tk.PhotoImage] = {}
        self.scheme = colors.scheme
        self._painted: list[tuple[weakref.ref, dict]] = []
        self._listeners: list[Callable[[], None]] = []

    def px(self, value: float) -> int:
        """Scale a pixel size for a high-DPI display. Font sizes are in points already."""
        return int(round(value * self.scale))

    def image(self, name: str) -> tk.PhotoImage:
        return self.images[name]

    def paint(self, widget: tk.Misc, **roles) -> tk.Misc:
        """Colour a tk widget by token name, and again whenever the scheme changes.

        paint(label, bg="surface", fg="ink_dim"). A value may also be a
        function of the colours for a colour that is worked out.
        """
        self._painted.append((weakref.ref(widget), dict(roles)))
        _apply_roles(widget, roles)
        return widget

    def on_change(self, callback: Callable[[], None]) -> None:
        """Run callback after every scheme change. For text tags and drawn widgets."""
        self._listeners.append(callback)

    def set_scheme(self, scheme_id: str) -> str:
        """Redraw the window in another scheme. Returns the scheme now in use."""
        chosen = colors.use(scheme_id)
        self.scheme = chosen
        _load_images(self)
        _configure_styles(self)
        alive = []
        for ref, roles in self._painted:
            widget = ref()
            if widget is None:
                continue
            try:
                if not widget.winfo_exists():
                    continue
                _apply_roles(widget, roles)
            except tk.TclError:
                continue
            alive.append((ref, roles))
        self._painted = alive
        for callback in list(self._listeners):
            try:
                callback()
            except tk.TclError:
                continue
        _recolor_popdowns(self.root)
        style_title_bar(self.root)
        return chosen


def _apply_roles(widget: tk.Misc, roles: dict) -> None:
    options = {}
    for option, role in roles.items():
        options[option] = role(colors) if callable(role) else getattr(colors, role)
    widget.configure(**options)


def enable_windows_dpi_awareness() -> bool:
    """Ask Windows for crisp text on a scaled display. Call before tk.Tk().

    Without this, Windows bitmap-stretches the whole window at 125% or 150%
    scaling and the text looks blurry. Returns True when a call succeeded.
    Other platforms return False and nothing changes.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
    except ImportError:
        return False
    try:
        # 1 = system DPI aware. Per-monitor (2) needs WM_DPICHANGED handling Tk does not do.
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return True
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return True
    except Exception:
        return False


def _colorref(value: str) -> int:
    red, green, blue = shapes.parse_color(value)
    return (blue << 16) | (green << 8) | red


def style_title_bar(window: tk.Misc) -> bool:
    """Give a window's Windows title bar the scheme's colours. No effect elsewhere.

    Windows 11 takes a caption and text colour. Windows 10 (build 1809 and
    later) only switches the bar between dark and light. A build that knows
    neither keeps its own title bar. Returns True when Windows accepted a call.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        window.update_idletasks()
        handle = ctypes.windll.user32.GetParent(window.winfo_id())
        if not handle:
            return False
        dwm = ctypes.windll.dwmapi.DwmSetWindowAttribute
        accepted = False
        dark = ctypes.c_int(1 if colors.dark else 0)
        # 20 is DWMWA_USE_IMMERSIVE_DARK_MODE; builds before 19041 used 19.
        for attribute in (20, 19):
            if dwm(handle, attribute, ctypes.byref(dark), ctypes.sizeof(dark)) == 0:
                accepted = True
                break
        # 35 is DWMWA_CAPTION_COLOR and 36 DWMWA_TEXT_COLOR (Windows 11).
        for attribute, value in ((35, colors.bg), (36, colors.ink)):
            ref = ctypes.c_int(_colorref(value))
            if dwm(handle, attribute, ctypes.byref(ref), ctypes.sizeof(ref)) == 0:
                accepted = True
        return accepted
    except Exception:
        return False


def pick_family(root: tk.Misc, candidates: tuple[str, ...], fallback: str) -> str:
    try:
        available = set(tkfont.families(root))
    except tk.TclError:
        return fallback
    for name in candidates:
        if name in available:
            return name
    return fallback


def _scale_for(root: tk.Misc) -> float:
    try:
        dpi = float(root.winfo_fpixels("1i"))
    except (tk.TclError, ValueError):
        return 1.0
    return max(1.0, min(3.0, dpi / 96.0))


# Corner radii of the rounded pictures, in pixels at 100% scale.
RADIUS = 9
RADIUS_MENU = 6
RADIUS_PAPER = 10
RADIUS_CARD = 13
RADIUS_CHIP = 14
RADIUS_COMPOSER = 14
RADIUS_BUBBLE = 16


def _slice(px: Callable[[float], int], radius: float) -> int:
    """How far in from each edge a rounded picture is kept unstretched: its corner and a little more."""
    return px(radius) + px(2)


def _side(px: Callable[[float], int], radius: float) -> int:
    """The size of a rounded picture: two corners and a middle that an element can stretch."""
    return 2 * _slice(px, radius) + px(6)


def _pictures(px: Callable[[float], int]) -> dict[str, bytes]:
    """Every picture the theme uses, drawn in the colours of the scheme in use."""
    c = colors
    line = max(1.0, float(px(1)))
    out: dict[str, bytes] = {"clear": shapes.clear(_side(px, RADIUS), _side(px, RADIUS))}

    def box(name: str, fill, border=None, *, r=RADIUS, width=line, alpha=1.0) -> None:
        size = _side(px, r)
        out[name] = shapes.rounded_rect(size, size, px(r), fill, border=border, border_width=width, fill_alpha=alpha)

    box("btn_accent", c.accent)
    box("btn_accent_hover", c.accent_hover)
    box("btn_accent_pressed", c.accent_pressed)
    box("btn_accent_disabled", c.accent_disabled)
    box("btn_soft", c.raised, c.edge)
    box("btn_soft_hover", c.raised_hover, c.edge)
    box("btn_soft_pressed", c.raised_pressed, c.edge)
    box("btn_soft_disabled", c.surface, c.edge)
    box("btn_ghost_hover", c.raised_hover)
    box("btn_ghost_pressed", c.edge)
    # On a card, a button and a field are wells in the window colour, so they stand off the card.
    box("btn_well", c.surface, c.edge)
    box("btn_well_hover", c.bg, c.ink_faint)
    box("btn_well_pressed", c.bg, c.edge)
    box("field_well", c.bg, c.edge)
    box("field_well_focus", c.bg, c.focus_edge, width=line * 1.5)
    box("btn_danger_hover", mix(c.err, c.raised, 0.22), mix(c.err, c.edge, 0.6))
    box("outline", None, c.edge)
    box("outline_hover", c.raised, c.edge)
    box("pill_hover", c.raised)
    box("pill_selected", c.accent_soft, mix(c.accent, c.edge, 0.45))
    box("field", c.raised, c.edge)
    box("field_focus", c.raised, c.focus_edge, width=line * 1.5)
    box("field_disabled", c.surface, c.edge)
    box("tab_hover", c.raised, alpha=0.55)
    box("tab_selected", c.raised)
    box("row_selected", c.raised)
    box("menu_hover", c.raised, r=RADIUS_MENU)
    box("card", c.raised, c.edge, r=RADIUS_CARD)
    box("panel", c.surface, c.edge, r=RADIUS_CARD)
    box("paper", c.paper, c.paper_edge, r=RADIUS_PAPER)
    box("composer", c.raised, c.edge, r=RADIUS_COMPOSER)
    box("composer_focus", c.raised, c.focus_edge, r=RADIUS_COMPOSER, width=line * 1.5)
    box("swatch", c.raised, c.edge, r=RADIUS_CARD)
    box("swatch_hover", c.raised_hover, c.ink_faint, r=RADIUS_CARD)
    box("swatch_selected", c.raised, c.accent, r=RADIUS_CARD, width=line * 2)
    box("banner", c.banner, c.banner_edge, r=RADIUS_PAPER)
    box("chip", None, c.edge, r=RADIUS_CHIP)
    box("chip_hover", c.raised, c.focus_edge, r=RADIUS_CHIP)
    bubble = _side(px, RADIUS_BUBBLE)
    out["bubble"] = shapes.rounded_rect(
        bubble, bubble, (px(RADIUS_BUBBLE), px(RADIUS_BUBBLE), px(5), px(RADIUS_BUBBLE)), c.raised,
        border=c.edge, border_width=line,
    )

    # Scrollbar thumbs: a slim pill with a clear margin, so the bar reads as thin.
    thumb, gap = px(6), px(3)
    for name, fill in (
        ("thumb", c.edge), ("thumb_hover", c.ink_faint),
        ("thumb_paper", c.paper_edge), ("thumb_paper_hover", c.paper_faint),
    ):
        pill = shapes.rounded_rect(thumb, 4 * thumb, thumb / 2.0, fill)
        out[name + "_v"] = shapes.extend(pill, left=gap, right=gap)
        flat = shapes.rounded_rect(4 * thumb, thumb, thumb / 2.0, fill)
        out[name + "_h"] = shapes.extend(flat, top=gap, bottom=gap)
    out["thumb_clear_v"] = shapes.clear(thumb + 2 * gap, 4 * thumb)
    out["thumb_clear_h"] = shapes.clear(4 * thumb, thumb + 2 * gap)

    # Check boxes, with the gap to their label built in.
    check = px(18)
    tick = shapes.icon("check", check, c.on_accent, width=max(1.6, check / 9.0))

    def check_box(name: str, fill, border, mark: bool) -> None:
        picture = shapes.rounded_rect(check, check, px(5), fill, border=border, border_width=line)
        if mark:
            picture = shapes.overlay(picture, tick)
        out[name] = shapes.extend(picture, right=px(8))

    check_box("check_off", c.raised, c.edge, False)
    check_box("check_off_hover", c.raised_hover, c.ink_faint, False)
    check_box("check_on", c.accent, None, True)
    check_box("check_on_hover", c.accent_hover, None, True)
    check_box("check_disabled", c.surface, c.edge, False)

    # Small line icons.
    icon = px(18)
    for name, drawing, tint in (
        ("icon_more", "more", c.ink_dim),
        ("icon_more_hover", "more", c.ink),
        ("icon_close", "close", c.ink_dim),
        ("icon_close_hover", "close", c.ink),
        ("icon_panel", "panel", c.ink_dim),
        ("icon_panel_on", "panel", c.accent),
        ("icon_plus", "plus", c.on_accent),
        ("icon_send", "arrow_up", c.on_accent),
        ("icon_stop", "stop", c.ink),
        ("icon_check", "check", c.ok),
    ):
        out[name] = shapes.icon(drawing, icon, tint)
    chevron = px(14)
    out["chevron"] = shapes.extend(shapes.icon("chevron_down", chevron, c.ink_dim), left=px(2), right=px(8))
    out["chevron_menu"] = shapes.extend(shapes.icon("chevron_down", chevron, c.ink_dim), left=px(6))

    # The working dots: one disc at five strengths, which the status line cycles through.
    dot = px(7)
    for step, alpha in enumerate((0.25, 0.42, 0.62, 0.82, 1.0)):
        out[f"dot_{step}"] = shapes.disc(dot, c.accent, radius=dot * (0.36 + 0.14 * alpha), alpha=alpha)
    out["dot_ok"] = shapes.disc(dot, c.ok)
    out["dot_warn"] = shapes.disc(dot, c.warn)
    out["dot_err"] = shapes.disc(dot, c.err)
    out["dot_idle"] = shapes.disc(dot, c.ink_faint, radius=dot * 0.32)

    # The mark beside the wordmark and on the welcome.
    out["mark"] = shapes.star_mark(px(20), c.accent)
    out["mark_large"] = shapes.star_mark(px(46), c.accent)
    return out


# The window, taskbar, and installer icon: the star on warm charcoal, the same in every scheme.
ICON_STAR = SCHEMES["clay"].colors["accent"]
ICON_BACKGROUND = "#1d1d1b"
_ICON_CACHE: dict[tuple[int, ...], list[bytes]] = {}


def app_icon_pictures(sizes: tuple[int, ...] = (16, 32, 48, 64)) -> list[bytes]:
    """The window icon as PNG bytes at several sizes, smallest first."""
    found = _ICON_CACHE.get(sizes)
    if found is None:
        found = _ICON_CACHE[sizes] = [shapes.star_mark(size, ICON_STAR, ICON_BACKGROUND) for size in sizes]
    return list(found)


# Pictures already drawn, by scheme and scale. Going back to a scheme is then instant.
_PICTURE_CACHE: dict[tuple[str, float], dict[str, bytes]] = {}


def _load_images(theme: Theme) -> None:
    """Draw every picture in the current colours. Existing pictures are redrawn in place."""
    key = (colors.scheme, round(theme.scale, 3))
    pictures = _PICTURE_CACHE.get(key)
    if pictures is None:
        pictures = _PICTURE_CACHE[key] = _pictures(theme.px)
    for name, data in pictures.items():
        encoded = base64.b64encode(data)
        existing = theme.images.get(name)
        if existing is None:
            theme.images[name] = tk.PhotoImage(master=theme.root, data=encoded)
        else:
            existing.configure(data=encoded)


def _create_elements(theme: Theme, style: ttk.Style) -> None:
    """The rounded elements. Created once per interpreter; their pictures change with the scheme."""
    img = theme.image
    px = theme.px
    edge = _slice(px, RADIUS)
    large = _slice(px, RADIUS_CARD)

    def create(name: str, kind: str, *spec, **options) -> None:
        # An image element pads its children by its slice border unless told otherwise.
        # Every style here sets its own padding, so the element adds none.
        if "border" in options:
            options.setdefault("padding", 0)
        style.element_create(name, kind, *spec, **options)

    def button(element: str) -> list:
        return [(element, {"sticky": "nswe", "children": [
            ("Button.padding", {"sticky": "nswe", "children": [("Button.label", {"sticky": "nswe"})]}),
        ]})]

    def frame(element: str) -> list:
        return [(element, {"sticky": "nswe"})]

    create("Accent.button", "image", img("btn_accent"),
           ("disabled", img("btn_accent_disabled")), ("pressed", img("btn_accent_pressed")),
           ("active", img("btn_accent_hover")), border=edge, sticky="nsew")
    create("Soft.button", "image", img("btn_soft"),
           ("disabled", img("btn_soft_disabled")), ("pressed", img("btn_soft_pressed")),
           ("active", img("btn_soft_hover")), border=edge, sticky="nsew")
    create("Ghost.button", "image", img("clear"),
           ("disabled", img("clear")), ("pressed", img("btn_ghost_pressed")),
           ("active", img("btn_ghost_hover")), border=edge, sticky="nsew")
    create("Danger.button", "image", img("btn_soft"),
           ("disabled", img("btn_soft_disabled")), ("pressed", img("btn_danger_hover")),
           ("active", img("btn_danger_hover")), border=edge, sticky="nsew")
    create("Outline.button", "image", img("outline"),
           ("pressed", img("btn_soft_pressed")), ("active", img("outline_hover")), border=edge, sticky="nsew")
    create("Pill.button", "image", img("clear"),
           ("selected", img("pill_selected")), ("pressed", img("btn_ghost_pressed")),
           ("active", img("pill_hover")), border=edge, sticky="nsew")
    create("Field.field", "image", img("field"),
           ("disabled", img("field_disabled")), ("focus", img("field_focus")), border=edge, sticky="nsew")
    create("Well.button", "image", img("btn_well"),
           ("disabled", img("btn_soft_disabled")), ("pressed", img("btn_well_pressed")),
           ("active", img("btn_well_hover")), border=edge, sticky="nsew")
    create("Well.field", "image", img("field_well"),
           ("disabled", img("field_disabled")), ("focus", img("field_well_focus")), border=edge, sticky="nsew")
    create("Chevron.indicator", "image", img("chevron"), sticky="")
    create("MenuChevron.indicator", "image", img("chevron_menu"), sticky="")
    create("Check.indicator", "image", img("check_off"),
           ("disabled", img("check_disabled")),
           ("selected", "active", img("check_on_hover")), ("selected", img("check_on")),
           ("active", img("check_off_hover")), sticky="w")
    create("Pill.tab", "image", img("clear"),
           ("selected", img("tab_selected")), ("active", img("tab_hover")), border=edge, sticky="nsew")
    create("Round.row", "image", img("clear"), ("selected", img("row_selected")), border=edge, sticky="nsew")
    create("Card.frame", "image", img("card"), border=large, sticky="nsew")
    create("Panel.frame", "image", img("panel"), border=large, sticky="nsew")
    create("Paper.frame", "image", img("paper"), border=_slice(px, RADIUS_PAPER), sticky="nsew")
    create("Banner.frame", "image", img("banner"), border=_slice(px, RADIUS_PAPER), sticky="nsew")
    create("Swatch.frame", "image", img("swatch"),
           ("selected", img("swatch_selected")), ("active", img("swatch_hover")), border=large, sticky="nsew")
    create("Composer.frame", "image", img("composer"), ("focus", img("composer_focus")),
           border=_slice(px, RADIUS_COMPOSER), sticky="nsew")
    create("Bubble.frame", "image", img("bubble"), border=_slice(px, RADIUS_BUBBLE), sticky="nsew")
    create("Chip.frame", "image", img("chip"), ("active", img("chip_hover")),
           border=_slice(px, RADIUS_CHIP), sticky="nsew")
    cap = px(6)
    create("Thin.Vertical.thumb", "image", img("thumb_v"),
           ("disabled", img("thumb_clear_v")), ("pressed", img("thumb_hover_v")), ("active", img("thumb_hover_v")),
           border=(0, cap, 0, cap), padding=0, sticky="ns")
    create("Thin.Horizontal.thumb", "image", img("thumb_h"),
           ("disabled", img("thumb_clear_h")), ("pressed", img("thumb_hover_h")), ("active", img("thumb_hover_h")),
           border=(cap, 0, cap, 0), padding=0, sticky="ew")
    create("Paper.Vertical.thumb", "image", img("thumb_paper_v"),
           ("disabled", img("thumb_clear_v")), ("pressed", img("thumb_paper_hover_v")),
           ("active", img("thumb_paper_hover_v")), border=(0, cap, 0, cap), padding=0, sticky="ns")

    layout = style.layout
    layout("TButton", button("Soft.button"))
    layout("Accent.TButton", button("Accent.button"))
    layout("Ghost.TButton", button("Ghost.button"))
    layout("Sidebar.TButton", button("Ghost.button"))
    layout("Danger.TButton", button("Danger.button"))
    layout("Toolbar.TMenubutton", [("Outline.button", {"sticky": "nswe", "children": [
        ("Menubutton.padding", {"sticky": "nswe", "children": [
            ("MenuChevron.indicator", {"side": "right", "sticky": ""}),
            ("Menubutton.label", {"side": "left", "sticky": ""}),
        ]}),
    ]})])
    layout("Icon.TMenubutton", [("Ghost.button", {"sticky": "nswe", "children": [
        ("Menubutton.padding", {"sticky": "nswe", "children": [("Menubutton.label", {"sticky": ""})]}),
    ]})])
    layout("Toolbar.Toolbutton", [("Pill.button", {"sticky": "nswe", "children": [
        ("Toolbutton.padding", {"sticky": "nswe", "children": [("Toolbutton.label", {"sticky": "nswe"})]}),
    ]})])
    layout("TEntry", [("Field.field", {"sticky": "nswe", "children": [
        ("Entry.padding", {"sticky": "nswe", "children": [("Entry.textarea", {"sticky": "nswe"})]}),
    ]})])
    layout("TCombobox", [("Field.field", {"sticky": "nswe", "children": [
        ("Chevron.indicator", {"side": "right", "sticky": ""}),
        ("Combobox.padding", {"sticky": "nswe", "children": [("Combobox.textarea", {"sticky": "nswe"})]}),
    ]})])
    layout("OnCard.TButton", button("Well.button"))
    layout("OnCard.TEntry", [("Well.field", {"sticky": "nswe", "children": [
        ("Entry.padding", {"sticky": "nswe", "children": [("Entry.textarea", {"sticky": "nswe"})]}),
    ]})])
    layout("OnCard.TCombobox", [("Well.field", {"sticky": "nswe", "children": [
        ("Chevron.indicator", {"side": "right", "sticky": ""}),
        ("Combobox.padding", {"sticky": "nswe", "children": [("Combobox.textarea", {"sticky": "nswe"})]}),
    ]})])
    layout("Field.TFrame", frame("Field.field"))
    layout("TCheckbutton", [("Checkbutton.padding", {"sticky": "nswe", "children": [
        ("Check.indicator", {"side": "left", "sticky": ""}),
        ("Checkbutton.label", {"side": "left", "sticky": "nswe"}),
    ]})])
    layout("TNotebook", [("Notebook.client", {"sticky": "nswe"})])
    layout("TNotebook.Tab", [("Pill.tab", {"sticky": "nswe", "children": [
        ("Notebook.padding", {"sticky": "nswe", "children": [("Notebook.label", {"sticky": ""})]}),
    ]})])
    layout("Treeview", [("Treeview.padding", {"sticky": "nswe", "children": [
        ("Treeview.treearea", {"sticky": "nswe"}),
    ]})])
    layout("Treeview.Heading", [
        ("Treeheading.cell", {"sticky": "nswe"}),
        ("Treeheading.padding", {"sticky": "nswe", "children": [("Treeheading.text", {"sticky": "we"})]}),
    ])
    # The jobs list: a tree with no columns, a rounded highlight on the open job.
    layout("Jobs.Treeview", [("Treeview.padding", {"sticky": "nswe", "children": [
        ("Treeview.treearea", {"sticky": "nswe"}),
    ]})])
    layout("Jobs.Treeview.Row", [("Round.row", {"sticky": "nswe"})])
    layout("Jobs.Treeview.Item", [("Treeitem.padding", {"sticky": "nswe", "children": [
        ("Treeitem.text", {"sticky": "nswe"}),
    ]})])
    layout("Lines.Treeview", [("Treeview.padding", {"sticky": "nswe", "children": [
        ("Treeview.treearea", {"sticky": "nswe"}),
    ]})])
    layout("Lines.Treeview.Item", [("Treeitem.padding", {"sticky": "nswe", "children": [
        ("Treeitem.text", {"sticky": "nswe"}),
    ]})])
    layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
        ("Thin.Vertical.thumb", {"expand": "1", "sticky": "nswe"}),
    ]})])
    layout("Horizontal.TScrollbar", [("Horizontal.Scrollbar.trough", {"sticky": "we", "children": [
        ("Thin.Horizontal.thumb", {"expand": "1", "sticky": "nswe"}),
    ]})])
    layout("OnPaper.Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
        ("Paper.Vertical.thumb", {"expand": "1", "sticky": "nswe"}),
    ]})])
    layout("Card.TFrame", frame("Card.frame"))
    layout("Panel.TFrame", frame("Panel.frame"))
    layout("Paper.TFrame", frame("Paper.frame"))
    layout("Banner.TFrame", frame("Banner.frame"))
    layout("Swatch.TFrame", frame("Swatch.frame"))
    layout("Composer.TFrame", frame("Composer.frame"))
    layout("Bubble.TFrame", frame("Bubble.frame"))
    layout("Chip.TLabel", [("Chip.frame", {"sticky": "nswe", "children": [
        ("Label.padding", {"sticky": "nswe", "children": [("Label.label", {"sticky": "nswe"})]}),
    ]})])


def _configure_styles(theme: Theme) -> None:
    """Colours and fonts of every style, in the scheme in use. Runs again on a scheme change."""
    c = colors
    px = theme.px
    fonts = theme.fonts
    root = theme.root
    style = ttk.Style(root)

    try:
        root.configure(bg=c.bg)
    except tk.TclError:
        pass
    for pattern, value in (
        ("*Menu.background", c.raised),
        ("*Menu.foreground", c.ink),
        ("*Menu.activeBackground", c.accent_soft),
        ("*Menu.activeForeground", c.ink),
        ("*Menu.relief", "flat"),
        ("*Menu.activeBorderWidth", 0),
        ("*Menu.borderWidth", 1),
        ("*TCombobox*Listbox.background", c.raised),
        ("*TCombobox*Listbox.foreground", c.ink),
        ("*TCombobox*Listbox.selectBackground", c.accent_soft),
        ("*TCombobox*Listbox.selectForeground", c.ink),
        ("*TCombobox*Listbox.borderWidth", 0),
        ("*TCombobox*Listbox.relief", "flat"),
    ):
        root.option_add(pattern, value)
    root.option_add("*Menu.font", fonts["list"])
    root.option_add("*TCombobox*Listbox.font", fonts["list"])

    style.configure(
        ".",
        background=c.bg,
        foreground=c.ink,
        bordercolor=c.edge,
        lightcolor=c.bg,
        darkcolor=c.bg,
        troughcolor=c.bg,
        focuscolor=c.accent,
        selectbackground=c.select,
        selectforeground=c.ink,
        fieldbackground=c.raised,
        insertcolor=c.ink,
        font=fonts["ui"],
    )
    style.map(".", foreground=[("disabled", c.disabled_ink)])

    style.configure("TFrame", background=c.bg)
    style.configure("TLabel", background=c.bg, foreground=c.ink, font=fonts["ui"])
    style.configure("Dim.TLabel", foreground=c.ink_dim)
    style.configure("Small.TLabel", foreground=c.ink_dim, font=fonts["small"])
    style.configure("Faint.TLabel", foreground=c.ink_faint, font=fonts["small"])
    style.configure("Footer.TLabel", foreground=c.ink_faint, font=fonts["small"])
    style.configure("Section.TLabel", foreground=c.ink_faint, font=fonts["section"])
    style.configure("Job.TLabel", foreground=c.ink, font=fonts["job"])
    style.configure("Heading.TLabel", foreground=c.ink, font=fonts["heading"])
    style.configure("Title.TLabel", foreground=c.ink, font=fonts["title"])
    style.configure("Wordmark.TLabel", foreground=c.ink, font=fonts["wordmark"])
    style.configure("Plus.TLabel", foreground=c.accent, font=fonts["wordmark"])
    style.configure("Link.TLabel", foreground=c.accent, font=fonts["ui"])
    style.configure("Status.TLabel", foreground=c.ink_dim, font=fonts["small"])
    style.configure("Icon.TLabel", foreground=c.ink_dim)
    style.configure("Chip.TLabel", foreground=c.ink_dim, font=fonts["small"], padding=(px(12), px(5)))
    style.map("Chip.TLabel", foreground=[("active", c.ink)])
    style.configure("Ok.TLabel", foreground=c.ok, font=fonts["small"])
    style.configure("Err.TLabel", foreground=c.err, font=fonts["small"])

    button_pad = (px(14), px(7))
    style.configure("TButton", padding=button_pad, foreground=c.ink, anchor="center", font=fonts["ui"])
    style.map("TButton", foreground=[("disabled", c.disabled_ink)])
    style.configure("Accent.TButton", padding=button_pad, foreground=c.on_accent, font=fonts["ui_bold"])
    style.map("Accent.TButton", foreground=[("disabled", mix(c.on_accent, c.accent_disabled, 0.55))])
    style.configure("Ghost.TButton", padding=(px(10), px(6)), foreground=c.ink_dim)
    style.map("Ghost.TButton", foreground=[("disabled", c.disabled_ink), ("active", c.ink)])
    style.configure("Sidebar.TButton", padding=(px(10), px(7)), foreground=c.ink_dim, anchor="w")
    style.map("Sidebar.TButton", foreground=[("active", c.ink)])
    style.configure("Danger.TButton", padding=button_pad, foreground=c.ink)
    style.map("Danger.TButton", foreground=[("disabled", c.disabled_ink), ("active", c.err)])

    style.configure("Toolbar.TMenubutton", padding=(px(11), px(5), px(4), px(5)), foreground=c.ink_dim,
                    font=fonts["small"])
    style.map("Toolbar.TMenubutton", foreground=[("active", c.ink)])
    style.configure("Icon.TMenubutton", padding=(px(7), px(5)), foreground=c.ink_dim)
    style.configure("Toolbar.Toolbutton", padding=(px(11), px(5)), foreground=c.ink_dim, font=fonts["small"],
                    anchor="center")
    style.map("Toolbar.Toolbutton", foreground=[("selected", c.accent), ("active", c.ink)])

    style.configure("TEntry", padding=(px(9), px(6)), foreground=c.ink, insertcolor=c.ink,
                    selectbackground=c.select, selectforeground=c.ink, font=fonts["ui"])
    style.map("TEntry", foreground=[("disabled", c.disabled_ink)])
    style.configure("TCombobox", padding=(px(9), px(6), px(2), px(6)), foreground=c.ink,
                    selectbackground=c.raised, selectforeground=c.ink, insertcolor=c.ink)
    style.map(
        "TCombobox",
        selectbackground=[("readonly", c.raised), ("disabled", c.surface)],
        selectforeground=[("readonly", c.ink), ("disabled", c.disabled_ink)],
        foreground=[("disabled", c.disabled_ink)],
    )
    style.configure("TCheckbutton", background=c.bg, foreground=c.ink, padding=(0, px(3)), font=fonts["ui"])
    style.map("TCheckbutton", foreground=[("disabled", c.disabled_ink)])

    style.configure("TNotebook", background=c.bg, borderwidth=0, bordercolor=c.bg, lightcolor=c.bg,
                    darkcolor=c.bg, tabmargins=(0, 0, 0, px(8)))
    style.configure("TNotebook.Tab", padding=(px(13), px(6)), foreground=c.ink_dim, font=fonts["small_bold"])
    style.map("TNotebook.Tab", foreground=[("selected", c.ink), ("active", c.ink)])

    linespace = fonts["list"].metrics("linespace")
    style.configure(
        "Treeview",
        rowheight=max(px(26), linespace + px(10)),
        background=c.bg,
        fieldbackground=c.bg,
        foreground=c.ink,
        borderwidth=0,
        font=fonts["list"],
    )
    style.map("Treeview", background=[("selected", c.accent_soft)], foreground=[("selected", c.ink)])
    style.configure("Treeview.Heading", background=c.bg, foreground=c.ink_faint, font=fonts["section"],
                    relief="flat", borderwidth=0, padding=(px(6), px(5)))
    style.map("Treeview.Heading", background=[("active", c.bg)], foreground=[("active", c.ink_dim)])
    style.configure(
        "Jobs.Treeview",
        rowheight=max(px(32), linespace + px(14)),
        background=c.surface,
        fieldbackground=c.surface,
        foreground=c.ink_dim,
        borderwidth=0,
        indent=0,
        font=fonts["list"],
    )
    style.map("Jobs.Treeview", background=[("selected", c.surface)], foreground=[("selected", c.ink)])
    style.configure("Jobs.Treeview.Item", padding=(px(10), 0, px(6), 0))
    style.configure(
        "Lines.Treeview",
        rowheight=max(px(20), fonts["small"].metrics("linespace") + px(5)),
        background=c.surface,
        fieldbackground=c.surface,
        foreground=c.ink_faint,
        borderwidth=0,
        indent=0,
        font=fonts["small"],
    )
    style.map("Lines.Treeview", background=[("selected", c.surface)], foreground=[("selected", c.ink_faint)])
    style.configure("Lines.Treeview.Item", padding=(px(2), 0, px(2), 0))

    for name in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(name, background=c.bg, troughcolor=c.bg, bordercolor=c.bg, lightcolor=c.bg,
                        darkcolor=c.bg, borderwidth=0, relief="flat", arrowsize=px(10))
    style.configure("TSeparator", background=c.edge)
    for name in ("Card.TFrame", "Panel.TFrame", "Paper.TFrame", "Banner.TFrame", "Swatch.TFrame",
                 "Composer.TFrame", "Bubble.TFrame", "Field.TFrame"):
        style.configure(name, background=c.bg)

    # The same styles on the sidebar, on a card, and on paper.
    for prefix, token in _SURFACES:
        tone = getattr(c, token)
        for base in _VARIANT_STYLES:
            style.configure(f"{prefix}.{base}", background=tone)
        for name in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
            style.configure(f"{prefix}.{name}", troughcolor=tone, bordercolor=tone, lightcolor=tone, darkcolor=tone)
        style.configure(f"{prefix}.TNotebook", bordercolor=tone, lightcolor=tone, darkcolor=tone)
        style.configure(f"{prefix}.Treeview", fieldbackground=tone)
        style.map(f"{prefix}.Treeview.Heading", background=[("active", tone)])
    style.configure("OnPaper.TLabel", foreground=c.paper_ink)
    style.configure("OnPaper.Dim.TLabel", foreground=c.paper_dim)
    style.configure("OnPaper.Small.TLabel", foreground=c.paper_dim)
    style.configure("OnPaper.Faint.TLabel", foreground=c.paper_faint)
    style.configure("OnPaper.Section.TLabel", foreground=c.paper_dim)
    style.configure("OnPaper.Heading.TLabel", foreground=c.paper_ink)
    # The tables of the drawer sit on the sidebar colour and mark the picked row.
    style.map("OnSide.Treeview", background=[("selected", c.accent_soft)], foreground=[("selected", c.ink)])
    style.map("OnCard.Treeview", background=[("selected", c.accent_soft)], foreground=[("selected", c.ink)])
    # On a card the well is the window colour, so its selection and readonly text sit on that.
    style.configure("OnCard.TCombobox", selectbackground=c.bg)
    style.map("OnCard.TCombobox", selectbackground=[("readonly", c.bg), ("disabled", c.surface)])
    style.configure("OnBanner.TLabel", background=c.banner, foreground=c.ink, font=fonts["ui"])
    style.configure("OnBanner.Icon.TLabel", background=c.banner)


def _recolor_popdowns(root: tk.Misc) -> None:
    """A combobox keeps its drop-down list once opened. Give the open ones the new colours."""
    c = colors

    def walk(widget: tk.Misc) -> None:
        for child in widget.winfo_children():
            try:
                if child.winfo_class() == "TCombobox":
                    popdown = root.tk.call("ttk::combobox::PopdownWindow", str(child))
                    root.tk.call(
                        f"{popdown}.f.l", "configure",
                        "-background", c.raised, "-foreground", c.ink,
                        "-selectbackground", c.accent_soft, "-selectforeground", c.ink,
                    )
            except tk.TclError:
                pass
            walk(child)

    try:
        walk(root)
    except tk.TclError:
        pass


def apply_theme(root: tk.Tk, scheme: str | None = None) -> Theme:
    """Set fonts and ttk styles on root. Returns the fonts, the pictures, and the pixel scale.

    scheme names one of SCHEMES. None reads the saved choice.
    """
    chosen = scheme if scheme is not None else saved_scheme()
    existing = getattr(root, "_cynosure_theme", None)
    if isinstance(existing, Theme):
        # One theme per window. A second call only changes the scheme.
        existing.set_scheme(chosen)
        return existing
    colors.use(chosen)
    default = tkfont.nametofont("TkDefaultFont", root=root)
    ui = pick_family(root, UI_FAMILIES, default.actual("family"))
    mono = pick_family(
        root,
        MONO_FAMILIES,
        tkfont.nametofont("TkFixedFont", root=root).actual("family"),
    )
    display = pick_family(root, DISPLAY_FAMILIES, ui)
    for name, size, weight in (
        ("TkDefaultFont", 10, "normal"),
        ("TkTextFont", 10, "normal"),
        ("TkMenuFont", 10, "normal"),
        ("TkHeadingFont", 10, "bold"),
        ("TkCaptionFont", 10, "bold"),
        ("TkSmallCaptionFont", 9, "normal"),
        ("TkTooltipFont", 9, "normal"),
    ):
        try:
            tkfont.nametofont(name, root=root).configure(family=ui, size=size, weight=weight)
        except tk.TclError:
            pass
    try:
        tkfont.nametofont("TkFixedFont", root=root).configure(family=mono, size=10)
    except tk.TclError:
        pass

    theme = Theme(root, _scale_for(root), ui, mono, display)
    theme.fonts = {
        "ui": tkfont.Font(root, family=ui, size=10),
        "ui_bold": tkfont.Font(root, family=ui, size=10, weight="bold"),
        "chat": tkfont.Font(root, family=ui, size=11),
        "chat_bold": tkfont.Font(root, family=ui, size=11, weight="bold"),
        "who": tkfont.Font(root, family=ui, size=9, weight="bold"),
        "heading": tkfont.Font(root, family=display, size=13, weight="bold"),
        "title": tkfont.Font(root, family=display, size=24, weight="bold"),
        "subtitle": tkfont.Font(root, family=ui, size=11),
        "job": tkfont.Font(root, family=display, size=14, weight="bold"),
        "wordmark": tkfont.Font(root, family=display, size=15, weight="bold"),
        "section": tkfont.Font(root, family=ui, size=8, weight="bold"),
        "small": tkfont.Font(root, family=ui, size=9),
        "small_bold": tkfont.Font(root, family=ui, size=9, weight="bold"),
        "italic": tkfont.Font(root, family=ui, size=10, slant="italic"),
        "mono": tkfont.Font(root, family=mono, size=10),
        "mono_bold": tkfont.Font(root, family=mono, size=10, weight="bold"),
        "list": tkfont.Font(root, family=ui, size=10),
        "gap": tkfont.Font(root, family=ui, size=5),
    }

    _load_images(theme)
    style = ttk.Style(root)
    if "cynosure" not in style.theme_names():
        style.theme_create("cynosure", parent="clam")
        style.theme_use("cynosure")
        _create_elements(theme, style)
    else:
        style.theme_use("cynosure")
    _configure_styles(theme)
    try:
        icons = [tk.PhotoImage(master=root, data=base64.b64encode(data)) for data in app_icon_pictures()]
        root.iconphoto(True, *reversed(icons))
        theme.images["app_icon"] = icons[-1]
        theme._icons = icons
    except tk.TclError:
        pass
    root._cynosure_theme = theme
    return theme


def theme_of(widget: tk.Misc | None) -> Theme | None:
    """The theme of the window a widget belongs to, or None before apply_theme ran."""
    if widget is None:
        return None
    try:
        root = widget._root()
    except (AttributeError, tk.TclError):
        return None
    found = getattr(root, "_cynosure_theme", None)
    return found if isinstance(found, Theme) else None
