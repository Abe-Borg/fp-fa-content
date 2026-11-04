"""Look of the desktop window: palette, fonts, ttk styles, and Windows DPI.

The window is plain tkinter. This module keeps the colors and font choices in
one place so ui.py only names a style. Nothing here reads the content pack or
the API key.
"""

from __future__ import annotations

import sys
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass, field
from tkinter import ttk

BG = "#ffffff"
SURFACE = "#f5f6f8"
SURFACE_HOVER = "#eaedf1"
SURFACE_PRESSED = "#dfe3e8"
BORDER = "#e3e6ea"
BORDER_STRONG = "#cfd5dc"
TEXT = "#1f2328"
MUTED = "#667085"
ACCENT = "#1f3b4d"
ACCENT_HOVER = "#2b5470"
ACCENT_SOFT = "#e3ecf2"
LINK = "#1d6fb8"
CODE_BG = "#f1f3f5"
BANNER_BG = "#e7f0f5"
DISABLED = "#9aa8b3"

UI_FAMILIES = (
    "Segoe UI",
    "Segoe UI Variable Text",
    "Inter",
    "Helvetica Neue",
    "Cantarell",
    "Noto Sans",
    "DejaVu Sans",
)
MONO_FAMILIES = (
    "Cascadia Mono",
    "Consolas",
    "JetBrains Mono",
    "DejaVu Sans Mono",
    "Liberation Mono",
)


@dataclass
class Theme:
    """Fonts and the pixel scale for one window."""

    scale: float = 1.0
    ui_family: str = "TkDefaultFont"
    mono_family: str = "TkFixedFont"
    fonts: dict = field(default_factory=dict)

    def px(self, value: float) -> int:
        """Scale a pixel size for a high-DPI display. Font sizes are in points already."""
        return int(round(value * self.scale))


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


def apply_theme(root: tk.Tk) -> Theme:
    """Set fonts and ttk styles on root. Returns the fonts and the pixel scale."""
    default = tkfont.nametofont("TkDefaultFont", root=root)
    ui = pick_family(root, UI_FAMILIES, default.actual("family"))
    mono = pick_family(
        root,
        MONO_FAMILIES,
        tkfont.nametofont("TkFixedFont", root=root).actual("family"),
    )
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

    fonts = {
        "chat": tkfont.Font(root, family=ui, size=11),
        "chat_bold": tkfont.Font(root, family=ui, size=11, weight="bold"),
        "who": tkfont.Font(root, family=ui, size=10, weight="bold"),
        "heading": tkfont.Font(root, family=ui, size=12, weight="bold"),
        "title": tkfont.Font(root, family=ui, size=20, weight="bold"),
        "subtitle": tkfont.Font(root, family=ui, size=11),
        "job": tkfont.Font(root, family=ui, size=12, weight="bold"),
        "section": tkfont.Font(root, family=ui, size=9, weight="bold"),
        "small": tkfont.Font(root, family=ui, size=9),
        "italic": tkfont.Font(root, family=ui, size=10, slant="italic"),
        "mono": tkfont.Font(root, family=mono, size=10),
        "mono_bold": tkfont.Font(root, family=mono, size=10, weight="bold"),
        "list": tkfont.Font(root, family=ui, size=10),
        "icon": tkfont.Font(root, family=ui, size=13, weight="bold"),
    }
    theme = Theme(scale=_scale_for(root), ui_family=ui, mono_family=mono, fonts=fonts)
    px = theme.px

    try:
        root.configure(bg=BG)
    except tk.TclError:
        pass
    for pattern, value in (
        ("*Menu.background", BG),
        ("*Menu.foreground", TEXT),
        ("*Menu.activeBackground", ACCENT_SOFT),
        ("*Menu.activeForeground", TEXT),
        ("*Menu.relief", "flat"),
        ("*Menu.activeBorderWidth", 0),
        ("*Menu.borderWidth", 1),
        ("*TCombobox*Listbox.background", BG),
        ("*TCombobox*Listbox.selectBackground", ACCENT_SOFT),
        ("*TCombobox*Listbox.selectForeground", TEXT),
    ):
        root.option_add(pattern, value)
    root.option_add("*Menu.font", fonts["list"])
    root.option_add("*TCombobox*Listbox.font", fonts["list"])

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        ".",
        background=BG,
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=BG,
        darkcolor=BG,
        troughcolor=BG,
        focuscolor=ACCENT,
        selectbackground=ACCENT_SOFT,
        selectforeground=TEXT,
        fieldbackground=BG,
        insertcolor=TEXT,
    )
    style.configure("TFrame", background=BG)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("Small.TLabel", background=BG, foreground=MUTED, font=fonts["small"])
    style.configure("Footer.TLabel", background=BG, foreground=MUTED, font=fonts["small"])
    style.configure("Job.TLabel", background=BG, foreground=TEXT, font=fonts["job"])
    style.configure("Section.TLabel", background=SURFACE, foreground=MUTED, font=fonts["section"])
    style.configure("Surface.TLabel", background=SURFACE, foreground=MUTED, font=fonts["small"])

    button_pad = (px(14), px(6))
    style.configure(
        "TButton",
        padding=button_pad,
        background=SURFACE,
        foreground=TEXT,
        bordercolor=BORDER_STRONG,
        lightcolor=SURFACE,
        darkcolor=SURFACE,
        relief="flat",
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        lightcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        darkcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        foreground=[("disabled", DISABLED)],
    )
    style.configure(
        "Accent.TButton",
        padding=button_pad,
        background=ACCENT,
        foreground="#ffffff",
        bordercolor=ACCENT,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", DISABLED), ("pressed", ACCENT), ("active", ACCENT_HOVER)],
        lightcolor=[("disabled", DISABLED), ("pressed", ACCENT), ("active", ACCENT_HOVER)],
        darkcolor=[("disabled", DISABLED), ("pressed", ACCENT), ("active", ACCENT_HOVER)],
        bordercolor=[("disabled", DISABLED), ("active", ACCENT_HOVER)],
        foreground=[("disabled", "#f2f4f6")],
    )
    style.configure(
        "Sidebar.TButton",
        padding=(px(10), px(6)),
        anchor="w",
        background=SURFACE,
        foreground=TEXT,
        bordercolor=SURFACE,
        lightcolor=SURFACE,
        darkcolor=SURFACE,
    )
    style.map(
        "Sidebar.TButton",
        background=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        lightcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        darkcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        bordercolor=[("active", SURFACE_HOVER)],
    )

    # Top-bar menubuttons. Icon.TMenubutton drops the arrow for the ⋯ menu.
    for name in ("Toolbar.TMenubutton", "Icon.TMenubutton"):
        style.configure(
            name,
            padding=(px(10), px(5)),
            background=BG,
            foreground=TEXT,
            bordercolor=BG,
            lightcolor=BG,
            darkcolor=BG,
            arrowcolor=MUTED,
            relief="flat",
        )
        style.map(
            name,
            background=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
            lightcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
            darkcolor=[("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
            bordercolor=[("active", SURFACE_HOVER)],
        )
    style.configure("Icon.TMenubutton", font=fonts["icon"], padding=(px(10), px(1)))
    style.layout(
        "Icon.TMenubutton",
        [(
            "Menubutton.border",
            {"sticky": "nswe", "children": [(
                "Menubutton.padding",
                {"sticky": "nswe", "children": [("Menubutton.label", {"sticky": "nswe"})]},
            )]},
        )],
    )
    style.configure(
        "Toolbar.Toolbutton",
        padding=(px(10), px(5)),
        background=BG,
        foreground=TEXT,
        bordercolor=BG,
        lightcolor=BG,
        darkcolor=BG,
        relief="flat",
    )
    style.map(
        "Toolbar.Toolbutton",
        background=[("selected", ACCENT_SOFT), ("pressed", SURFACE_PRESSED), ("active", SURFACE_HOVER)],
        lightcolor=[("selected", ACCENT_SOFT), ("active", SURFACE_HOVER)],
        darkcolor=[("selected", ACCENT_SOFT), ("active", SURFACE_HOVER)],
        bordercolor=[("selected", ACCENT_SOFT), ("active", SURFACE_HOVER)],
        foreground=[("selected", ACCENT)],
    )

    style.configure(
        "TEntry",
        padding=(px(6), px(4)),
        fieldbackground=BG,
        bordercolor=BORDER_STRONG,
        lightcolor=BG,
        darkcolor=BG,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", BG)])
    style.configure(
        "TCombobox",
        padding=(px(6), px(3)),
        fieldbackground=BG,
        background=BG,
        bordercolor=BORDER_STRONG,
        lightcolor=BG,
        darkcolor=BG,
        arrowcolor=MUTED,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", BG)],
        selectbackground=[("readonly", BG)],
        selectforeground=[("readonly", TEXT)],
        bordercolor=[("focus", ACCENT)],
        background=[("active", SURFACE_HOVER)],
    )
    style.configure("TCheckbutton", background=BG, foreground=TEXT, indicatorcolor=BG)
    style.map("TCheckbutton", indicatorcolor=[("selected", ACCENT)], background=[("active", BG)])
    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure(
        "TNotebook.Tab",
        padding=(px(14), px(6)),
        background=SURFACE,
        foreground=MUTED,
        bordercolor=BORDER,
        lightcolor=SURFACE,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG), ("active", SURFACE_HOVER)],
        foreground=[("selected", ACCENT)],
        lightcolor=[("selected", BG)],
    )
    linespace = fonts["list"].metrics("linespace")
    style.configure(
        "Treeview",
        rowheight=max(px(24), linespace + px(8)),
        background=BG,
        fieldbackground=BG,
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=BG,
        darkcolor=BG,
    )
    style.map("Treeview", background=[("selected", ACCENT_SOFT)], foreground=[("selected", TEXT)])
    style.configure(
        "Treeview.Heading",
        background=SURFACE,
        foreground=MUTED,
        font=fonts["section"],
        relief="flat",
        bordercolor=BORDER,
        lightcolor=SURFACE,
        darkcolor=SURFACE,
    )
    style.map("Treeview.Heading", background=[("active", SURFACE_HOVER)])
    style.configure("TLabelframe", background=BG, bordercolor=BORDER, lightcolor=BG, darkcolor=BG)
    style.configure("TLabelframe.Label", background=BG, foreground=MUTED, font=fonts["section"])
    style.configure("TSeparator", background=BORDER)
    style.configure(
        "TScrollbar",
        background="#d5dae0",
        troughcolor=BG,
        bordercolor=BG,
        lightcolor="#d5dae0",
        darkcolor="#d5dae0",
        arrowcolor=MUTED,
        gripcount=0,
        arrowsize=px(12),
    )
    style.map(
        "TScrollbar",
        background=[("active", "#b9c0c8")],
        lightcolor=[("active", "#b9c0c8")],
        darkcolor=[("active", "#b9c0c8")],
    )
    return theme
