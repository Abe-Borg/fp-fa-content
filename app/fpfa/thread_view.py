"""The conversation, drawn in a tk.Text.

The Text widget is the reading column itself: the window centres it, so a
tag's margin colour can pad a block. A designer's message is a rounded
bubble on the right, as in the practice's other apps. A reply is plain text
on the window colour with its job caption above it. Code and tables sit on a
paper-coloured block. While a job works, the last line is three pulsing dots
and what the app is doing.

A reply that is still arriving, or one that has just landed, is the live
region at the end of the thread. Only its last paragraph is redrawn each
frame, with the newest words fading in and a caret after them, so a long
reply stays cheap to draw and a reader who has scrolled up is left alone.

The text a designer typed is also in the Text widget as hidden characters
beside the bubble, so "select all" and copy take the whole conversation and
the widget's text is the conversation.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from fpfa import theme
from fpfa.chat_render import Segment, markdown_segments
from fpfa.reveal import settle_inline, stable_boundary
from fpfa.theme import FADE_STEPS, colors
from fpfa.widgets import StatusDots, wheel_steps

CARET = "▍"
COLUMN_WIDTH = 780
BUBBLE_SHARE = 0.82


def split_lines(segments: list[Segment]) -> list[tuple[list[Segment], tuple | None]]:
    """Runs grouped into lines: (the runs of a line, the tags of its newline or None at the end)."""
    lines: list[tuple[list[Segment], tuple | None]] = []
    current: list[Segment] = []
    for chunk, tags in segments:
        if chunk == "\n":
            lines.append((current, tags))
            current = []
        else:
            current.append((chunk, tags))
    lines.append((current, None))
    return lines


def line_is_block(chunks: list[Segment], newline_tags: tuple | None) -> bool:
    """True for a line of a code or table block."""
    if newline_tags is not None:
        return "pre" in newline_tags
    return bool(chunks) and all("pre" in tags for _chunk, tags in chunks)


class ThreadView:
    """Draws turns, the welcome, the live reply, and the working line in one Text widget."""

    def __init__(
        self,
        view: tk.Text,
        look: "theme.Theme",
        *,
        links: dict[str, Callable[[], object]] | None = None,
        on_copy: Callable[[str], None] | None = None,
        animate: bool = False,
    ):
        self.view = view
        self.look = look
        self.animate = animate
        self._links = dict(links or {})
        self._on_copy = on_copy
        self._embedded: list[tk.Widget] = []
        self._bubble_labels: list[ttk.Label] = []
        self._dots: StatusDots | None = None
        self._pending_label = ""
        self._shimmer_after: str | None = None
        self._shimmer_at = 0
        self._column = look.px(COLUMN_WIDTH)
        self._live_key: object = None
        self._live_stable = 0
        self._live_drawn = ""
        self._caret_on = True
        # True while the reader is at the end of the thread. New words keep the end in
        # view only then, so a reader who scrolled up to read is left where they are.
        self.follow = True
        self.configure_tags()
        look.on_change(self.configure_tags)
        view.bind("<Destroy>", lambda _event: self._stop_shimmer(), add="+")
        for sequence in (
            "<MouseWheel>", "<Button-4>", "<Button-5>", "<B1-Motion>", "<ButtonRelease-1>",
            "<KeyRelease-Prior>", "<KeyRelease-Next>", "<KeyRelease-Up>", "<KeyRelease-Down>",
            "<KeyRelease-Home>", "<KeyRelease-End>",
        ):
            view.bind(sequence, self.user_moved, add="+")

    # Tags -----------------------------------------------------------------

    def configure_tags(self) -> None:
        """Fonts, colours, and margins of every tag. Runs again when the scheme changes."""
        view = self.view
        look = self.look
        fonts = look.fonts
        px = look.px
        c = colors
        # The Text widget's own padding is the column's margin, so a block lines up with the words.
        side = 0
        try:
            view.configure(
                bg=c.bg, fg=c.ink, selectbackground=c.select, selectforeground=c.ink,
                inactiveselectbackground=c.select,
            )
        except tk.TclError:
            return
        # Creation order sets priority: later tags win. A fade sits above the
        # plain text colour and below the tags that set a colour of their own.
        view.tag_configure(
            "body", font=fonts["chat"], foreground=c.ink,
            lmargin1=side, lmargin2=side, rmargin=side, spacing1=px(3), spacing2=px(3),
        )
        for step in range(FADE_STEPS):
            view.tag_configure(f"fade{step}", foreground=c.fade(step))
        view.tag_configure("gap", font=fonts["gap"], spacing1=0, spacing3=0)
        view.tag_configure("turn_gap", font=fonts["gap"], spacing1=px(12))
        view.tag_configure("meta", font=fonts["small"], foreground=c.ink_faint, spacing3=px(7))
        view.tag_configure("heading", font=fonts["heading"], foreground=c.ink, spacing1=px(10), spacing3=px(3))
        view.tag_configure("bullet", lmargin1=side + px(8), lmargin2=side + px(24))
        view.tag_configure("bullet2", lmargin1=side + px(28), lmargin2=side + px(44))
        view.tag_configure(
            "pre", font=fonts["mono"], background=c.paper, foreground=c.paper_ink,
            lmargin1=side + px(14), lmargin2=side + px(14), rmargin=side + px(14),
            lmargincolor=c.paper, rmargincolor=c.paper, spacing2=px(1),
            selectbackground=c.paper_select, selectforeground=c.paper_ink,
        )
        view.tag_configure("pre_first", spacing1=px(11))
        view.tag_configure("pre_last", spacing3=px(11))
        view.tag_configure("pre_head", font=fonts["mono_bold"])
        view.tag_configure("rule", foreground=c.paper_faint)
        view.tag_configure("bold", font=fonts["chat_bold"])
        view.tag_configure("code", font=fonts["mono"], background=c.raised)
        view.tag_configure("pending", font=fonts["small"], foreground=c.ink_dim, spacing1=px(16), spacing3=px(4))
        view.tag_configure("pending_detail", foreground=c.ink_faint)
        view.tag_configure("shimmer", foreground=c.shimmer)
        view.tag_configure("caret", foreground=c.accent if self._caret_on else c.bg)
        view.tag_configure("user_hidden", elide=True)
        view.tag_configure("bubble_line", justify="right", rmargin=side, spacing1=px(18), spacing3=px(2))
        view.tag_configure("welcome_mark", justify="center", spacing1=px(84), spacing3=px(14))
        view.tag_configure("welcome_title", font=fonts["title"], foreground=c.ink, justify="center", spacing3=px(10))
        view.tag_configure(
            "welcome_sub", font=fonts["subtitle"], foreground=c.ink_dim, justify="center",
            spacing3=px(2), lmargin1=px(40), lmargin2=px(40), rmargin=px(40),
        )
        view.tag_configure("welcome_link", font=fonts["chat"], foreground=c.accent, justify="center", spacing1=px(20))
        view.tag_configure(
            "welcome_hint", font=fonts["small"], foreground=c.ink_faint, justify="center",
            spacing1=px(16), spacing3=px(2),
        )
        for tag in self._links:
            view.tag_configure(tag, underline=True)
            view.tag_bind(tag, "<Button-1>", lambda _event, name=tag: self._follow(name))
            view.tag_bind(tag, "<Enter>", lambda _event: view.configure(cursor="hand2"))
            view.tag_bind(tag, "<Leave>", lambda _event: view.configure(cursor="arrow"))
        view.tag_raise("sel")

    def _follow(self, tag: str) -> str:
        action = self._links.get(tag)
        if action is not None:
            # The link's own text is redrawn by the action, so run it after this click.
            self.view.after_idle(action)
        return "break"

    def set_column(self, width: int) -> None:
        """The reading column changed width. Bubbles wrap to their share of it."""
        if width == self._column or width <= 0:
            return
        self._column = width
        wrap = self._bubble_wrap()
        for label in list(self._bubble_labels):
            try:
                label.configure(wraplength=wrap)
            except tk.TclError:
                self._bubble_labels.remove(label)

    def _bubble_wrap(self) -> int:
        return max(self.look.px(160), int(self._column * BUBBLE_SHARE) - self.look.px(40))

    # Whole thread ---------------------------------------------------------

    def render(
        self,
        turns: list[dict],
        *,
        welcome: dict | None = None,
        live: list[dict] | None = None,
        pending: dict | None = None,
    ) -> None:
        """Redraw everything and scroll to the end.

        live is the replies still coming onto the screen, each
        {"key", "text", "caret", "fades", "settled"}. pending is None, or
        {"label", "detail"} for the working line.
        """
        view = self.view
        view.configure(state="normal")
        self._clear()
        if welcome is not None and not turns and not live:
            self._welcome(welcome)
        for turn in turns:
            text = turn.get("text") or ""
            if turn.get("role") == "user":
                self._user(text)
            else:
                self._assistant(text)
        for name, gravity in (("tail", "left"), ("live_tail", "left"), ("pending", "right")):
            view.mark_set(name, "end-1c")
            view.mark_gravity(name, gravity)
        self._live_key = None
        self._live_stable = 0
        self._live_drawn = ""
        self._draw_live(live or [])
        self._draw_pending(pending)
        view.configure(state="disabled")
        self.follow = True
        view.see("end")

    def _clear(self) -> None:
        self._stop_shimmer()
        for widget in self._embedded:
            try:
                widget.destroy()
            except tk.TclError:
                pass
        self._embedded = []
        self._bubble_labels = []
        self._dots = None
        self._pending_label = ""
        self.view.delete("1.0", "end")

    def _welcome(self, spec: dict) -> None:
        view = self.view
        try:
            view.image_create("end", image=self.look.image("mark_large"))
            view.insert("end", "\n", ("welcome_mark",))
            view.tag_add("welcome_mark", "end-2l linestart", "end-1c")
        except tk.TclError:
            pass
        view.insert("end", spec.get("title", "") + "\n", ("welcome_title",))
        for line in spec.get("lines", []):
            view.insert("end", line + "\n", ("welcome_sub",))
        for text, tag in spec.get("links", []):
            view.insert("end", text + "\n", ("welcome_link", tag))
        footnote = spec.get("footnote")
        if footnote:
            view.insert("end", footnote + "\n", ("welcome_hint",))

    def _user(self, text: str) -> None:
        view = self.view
        px = self.look.px
        bubble = ttk.Frame(view, style="Bubble.TFrame", padding=(px(15), px(9), px(15), px(10)))
        label = ttk.Label(
            bubble, text=text, style="OnCard.TLabel", font=self.look.fonts["chat"],
            wraplength=self._bubble_wrap(), justify="left",
        )
        label.pack()
        for widget in (bubble, label):
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(sequence, self._wheel, add="+")
            widget.bind("<Button-3>", lambda event, body=text: self._copy_menu(event, body), add="+")
        self._embedded.append(bubble)
        self._bubble_labels.append(label)
        view.window_create("end", window=bubble, align="top")
        view.insert("end", "\n", ("bubble_line",))
        view.tag_add("bubble_line", "end-2l linestart", "end-1c")
        # The same words as text, hidden, so copy and get() hold the whole conversation.
        view.insert("end", "You\n" + text + "\n", ("user_hidden",))

    def _copy_menu(self, event, text: str) -> None:
        if self._on_copy is not None:
            self._on_copy(text)

    def _wheel(self, event) -> str:
        self.view.yview_scroll(wheel_steps(event) * 3, "units")
        return "break"

    def _assistant(self, text: str) -> None:
        view = self.view
        view.insert("end", "\n", ("turn_gap",))
        self._insert_segments("end", markdown_segments(text), close=True)

    def _insert_segments(self, index: str, segments: list[Segment], *, close: bool) -> bool:
        """Insert runs at index. close ends the last line, with the block colour when it is one.

        Returns True when the last line belongs to a code or table block, so a
        caller that ends the line itself can give its newline the block colour.
        """
        view = self.view
        lines = split_lines(segments)
        block = [line_is_block(chunks, newline) for chunks, newline in lines]
        last = len(lines) - 1
        for position, (chunks, newline) in enumerate(lines):
            extra: tuple = ()
            if block[position]:
                if position == 0 or not block[position - 1]:
                    extra += ("pre_first",)
                if position == last or not block[position + 1]:
                    extra += ("pre_last",)
            for chunk, tags in chunks:
                view.insert(index, chunk, ("body",) + tags + extra)
            if newline is None:
                if close:
                    view.insert(index, "\n", ("body", "pre") + extra if block[position] else ("body",))
                continue
            if block[position]:
                view.insert(index, "\n", ("body",) + newline + extra)
            elif not chunks:
                # A blank line between paragraphs is a short gap, not a full line.
                view.insert(index, "\n", ("body", "gap"))
            else:
                view.insert(index, "\n", ("body",) + newline)
        return bool(block and block[-1])

    # Live region ----------------------------------------------------------

    def at_bottom(self) -> bool:
        try:
            return self.view.yview()[1] >= 0.995
        except tk.TclError:
            return True

    def user_moved(self, _event=None) -> None:
        """The reader scrolled. Decide after Tk has moved the view whether they are still at the end."""
        try:
            self.view.after_idle(self._note_position)
        except tk.TclError:
            pass

    def _note_position(self) -> None:
        self.follow = self.at_bottom()

    def render_live(self, live: list[dict]) -> None:
        """Redraw the replies that are still arriving. The rest of the thread is untouched."""
        view = self.view
        view.configure(state="normal")
        self._draw_live(live)
        view.configure(state="disabled")
        if self.follow:
            view.see("end")

    def _draw_live(self, live: list[dict]) -> None:
        view = self.view
        if not live:
            if view.compare("tail", "<", "pending"):
                view.delete("tail", "pending")
            self._live_key = None
            self._live_stable = 0
            self._live_drawn = ""
            return
        key = tuple(item.get("key") for item in live)
        last = live[-1]
        text = last.get("text") or ""
        # Earlier live replies, when two jobs answer at once, are drawn whole each time.
        simple = len(live) == 1
        fresh = (
            key != self._live_key
            or not simple
            or not text.startswith(self._live_drawn[:self._live_stable])
        )
        if fresh:
            view.delete("tail", "pending")
            for item in live[:-1]:
                view.insert("pending", "\n", ("turn_gap",))
                self._insert_segments("pending", markdown_segments(item.get("text") or ""), close=True)
            view.insert("pending", "\n", ("turn_gap",))
            view.mark_set("live_tail", "pending")
            view.mark_gravity("live_tail", "left")
            self._live_key = key
            self._live_stable = 0
        settled = last.get("settled")
        boundary = stable_boundary(text, len(text) if settled is None else settled)
        view.delete("live_tail", "pending")
        if boundary > self._live_stable:
            piece = text[self._live_stable:boundary]
            self._insert_segments(
                "pending", markdown_segments(piece, caption=self._live_stable == 0), close=False
            )
            view.mark_set("live_tail", "pending")
            view.mark_gravity("live_tail", "left")
            self._live_stable = boundary
        tail = text[self._live_stable:]
        if last.get("caret"):
            # Still flowing: a half-written bold or code span is drawn as it will end up.
            tail = settle_inline(tail)
        in_block = False
        if tail:
            in_block = self._insert_segments(
                "pending", markdown_segments(tail, caption=self._live_stable == 0), close=False
            )
        nearer = 0
        for distance, step in last.get("fades") or []:
            start = view.index(f"pending - {int(distance)}c")
            if view.compare(start, "<", "live_tail"):
                start = view.index("live_tail")
            stop = view.index(f"pending - {int(nearer)}c")
            if view.compare(start, "<", stop):
                view.tag_add(f"fade{step}", start, stop)
            nearer = distance
        closing = ("body", "pre", "pre_last") if in_block else ("body",)
        if last.get("caret"):
            view.insert("pending", CARET, closing + ("caret",))
        view.insert("pending", "\n", closing)
        self._live_drawn = text

    def commit_live(self) -> None:
        """The live reply is finished and drawn whole. It stays as part of the thread."""
        view = self.view
        try:
            view.mark_set("tail", "pending")
            view.mark_set("live_tail", "pending")
            view.mark_gravity("tail", "left")
            view.mark_gravity("live_tail", "left")
        except tk.TclError:
            pass
        self._live_key = None
        self._live_stable = 0
        self._live_drawn = ""

    def blink(self, on: bool) -> None:
        """Show or hide the caret after the live reply."""
        if on == self._caret_on:
            return
        self._caret_on = on
        try:
            self.view.tag_configure("caret", foreground=colors.accent if on else colors.bg)
        except tk.TclError:
            pass

    # Working line ---------------------------------------------------------

    def render_pending(self, pending: dict | None) -> None:
        view = self.view
        view.configure(state="normal")
        self._draw_pending(pending)
        view.configure(state="disabled")
        if self.follow:
            view.see("end")

    def _draw_pending(self, pending: dict | None) -> None:
        view = self.view
        if pending is None:
            self._stop_shimmer()
            if view.compare("pending", "<", "end-1c"):
                view.delete("pending", "end-1c")
            if self._dots is not None:
                try:
                    self._dots.destroy()
                except tk.TclError:
                    pass
                if self._dots in self._embedded:
                    self._embedded.remove(self._dots)
                self._dots = None
            self._pending_label = ""
            return
        label = pending.get("label") or ""
        detail = pending.get("detail") or ""
        if self._dots is None or not view.compare("pending", "<", "end-1c"):
            if view.compare("pending", "<", "end-1c"):
                view.delete("pending", "end-1c")
            # Left gravity while the line is written, so the mark stays at its start.
            view.mark_gravity("pending", "left")
            self._dots = StatusDots(view, self.look, animate=self.animate)
            self._embedded.append(self._dots)
            view.window_create("end-1c", window=self._dots, align="center", padx=self.look.px(2))
            view.insert("end-1c", " ", ("pending",))
            view.mark_set("pending_text", "end-1c")
            view.mark_gravity("pending_text", "left")
            view.insert("end-1c", "\n", ("pending",))
            view.tag_add("pending", "pending", "end-1c")
            view.mark_gravity("pending", "right")
            self._pending_label = ""
        shown = label + (" " + detail if detail else "")
        if shown != self._pending_label:
            view.delete("pending_text", "pending_text lineend")
            view.insert("pending_text", label, ("pending",))
            if detail:
                view.insert("pending_text lineend", " " + detail, ("pending", "pending_detail"))
            self._pending_label = shown
            self._shimmer_at = 0
        if self.animate:
            self._start_shimmer()

    def _start_shimmer(self) -> None:
        if self._shimmer_after is None:
            try:
                self._shimmer_after = self.view.after(70, self._shimmer)
            except tk.TclError:
                self._shimmer_after = None

    def _stop_shimmer(self) -> None:
        if self._shimmer_after is not None:
            try:
                self.view.after_cancel(self._shimmer_after)
            except tk.TclError:
                pass
            self._shimmer_after = None

    def _shimmer(self) -> None:
        """A brighter band sweeps along the working line, the sign that the app is not frozen."""
        self._shimmer_after = None
        view = self.view
        try:
            if not view.winfo_exists() or self._dots is None:
                return
            length = len(self._pending_label)
            view.tag_remove("shimmer", "pending_text", "pending_text lineend")
            if length:
                span = 6
                at = self._shimmer_at % (length + span + 10)
                view.tag_add("shimmer", f"pending_text + {max(0, at - span)}c", f"pending_text + {min(at, length)}c")
                self._shimmer_at += 1
        except tk.TclError:
            return
        self._start_shimmer()
