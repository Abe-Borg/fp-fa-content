"""The colours of the +Cynosure window: five schemes, their tokens, and the Windows title bar.

The window is a web page (fpfa/web). Its stylesheet, app/frontend/src/styles.css,
defines every token below for every scheme as a CSS custom property, and
tests/test_web.py keeps the two equal, so this module stays the list the app
validates a saved choice against and the colours the native title bar and the
window's first paint use.

The five schemes and their colours are the practice's other desktop apps'
(Spec Surgeon's frontend/src/index.css, which Build-a-Spec carries too): Warm
Clay is the default, and Blueprint, Graphite & Teal, Carbon & Hi-Vis, and
Linen redefine every token. Settings picks one, and the choice is saved in
config.json. A page element never names a colour of its own: it reads a token.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

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


def _colorref(value: str) -> int:
    red, green, blue = shapes.parse_color(value)
    return (blue << 16) | (green << 8) | red


def style_title_bar(handle: int, scheme_id: str | None = None) -> bool:
    """Give a Windows title bar the scheme's colours. handle is the window's HWND. No effect elsewhere.

    Windows 11 takes a caption and text colour. Windows 10 (build 1809 and
    later) only switches the bar between dark and light. A build that knows
    neither keeps its own title bar. Returns True when Windows accepted a call.
    """
    if sys.platform != "win32" or not handle:
        return False
    scheme = SCHEMES[resolve_scheme(scheme_id or colors.scheme)]
    try:
        import ctypes

        dwm = ctypes.windll.dwmapi.DwmSetWindowAttribute
        accepted = False
        dark = ctypes.c_int(1 if scheme.dark else 0)
        # 20 is DWMWA_USE_IMMERSIVE_DARK_MODE; builds before 19041 used 19.
        for attribute in (20, 19):
            if dwm(handle, attribute, ctypes.byref(dark), ctypes.sizeof(dark)) == 0:
                accepted = True
                break
        # 35 is DWMWA_CAPTION_COLOR and 36 DWMWA_TEXT_COLOR (Windows 11).
        for attribute, value in ((35, scheme.colors["bg"]), (36, scheme.colors["ink"])):
            ref = ctypes.c_int(_colorref(value))
            if dwm(handle, attribute, ctypes.byref(ref), ctypes.sizeof(ref)) == 0:
                accepted = True
        return accepted
    except Exception:
        return False
