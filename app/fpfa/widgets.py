"""Small tkinter widgets the window uses.

Composer is the multi-line message box. It keeps the few Entry calls the
window already makes (get(), insert(0, text), delete(0, "end")) so code that
used a one-line entry still works. ScrollFrame holds a form that can be
taller than the window.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from fpfa import theme


def _count_lines(widget: tk.Text) -> int:
    try:
        found = widget.count("1.0", "end", "displaylines")
    except tk.TclError:
        return 1
    if isinstance(found, tuple):
        found = found[0] if found else 1
    try:
        return max(1, int(found or 1))
    except (TypeError, ValueError):
        return 1


class Composer(tk.Text):
    """Message box. Enter sends, Shift+Enter adds a line.

    get() with no arguments returns the whole message. Index 0 means the
    start of the box, the way it does on an Entry.
    """

    def __init__(
        self,
        master,
        *,
        on_submit: Callable[[], object] | None = None,
        placeholder: str = "",
        placeholder_font=None,
        min_lines: int = 2,
        max_lines: int = 8,
        **kwargs,
    ):
        kwargs.setdefault("height", min_lines)
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("undo", True)
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self._on_submit = on_submit
        self._min_lines = max(1, min_lines)
        self._max_lines = max(self._min_lines, max_lines)
        background = kwargs.get("bg") or kwargs.get("background") or theme.BG
        self._placeholder = tk.Label(
            self,
            text=placeholder,
            fg=theme.MUTED,
            bg=background,
            font=placeholder_font or kwargs.get("font"),
            anchor="w",
            cursor="xterm",
            borderwidth=0,
            padx=0,
            pady=0,
        )
        self._placeholder.bind("<Button-1>", lambda _event: self.focus_set())
        self.bind("<Return>", self._submit)
        self.bind("<KP_Enter>", self._submit)
        self.bind("<Control-Return>", self._submit)
        self.bind("<Shift-Return>", self._newline)
        self.bind("<Shift-KP_Enter>", self._newline)
        for sequence in ("<KeyRelease>", "<<Paste>>", "<<Cut>>", "<FocusIn>", "<FocusOut>", "<Configure>"):
            self.bind(sequence, lambda _event: self.after_idle(self._sync), add="+")
        self._sync()

    @staticmethod
    def _index(index):
        if index in (0, "0"):
            return "1.0"
        return index

    def get(self, index1=None, index2=None):  # noqa: D401 - Entry-compatible
        if index1 is None:
            return super().get("1.0", "end-1c")
        first = self._index(index1)
        if index2 is None:
            return super().get(first)
        last = "end-1c" if index2 == "end" else self._index(index2)
        return super().get(first, last)

    def insert(self, index, chars, *args):
        super().insert(self._index(index), chars, *args)
        self._sync()

    def delete(self, index1, index2=None):
        super().delete(self._index(index1), None if index2 is None else self._index(index2))
        self._sync()

    def _submit(self, _event=None):
        if self._on_submit is not None:
            self._on_submit()
        return "break"

    def _newline(self, _event=None):
        super().insert("insert", "\n")
        self.see("insert")
        self._sync()
        return "break"

    def _sync(self) -> None:
        """Show the placeholder only when empty, and grow with the message."""
        try:
            empty = super().get("1.0", "end-1c") == ""
            if empty:
                # Child windows of a Text are placed inside its padding already.
                self._placeholder.place(x=0, y=0)
            else:
                self._placeholder.place_forget()
            wanted = min(self._max_lines, max(self._min_lines, _count_lines(self)))
            if int(self.cget("height")) != wanted:
                self.configure(height=wanted)
        except tk.TclError:
            return


class ScrollFrame(ttk.Frame):
    """A frame whose inner area scrolls vertically. Put children in .inner."""

    def __init__(self, master, *, background: str = theme.BG, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background=background)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self._on_wheel, add="+")

    def _on_inner(self, _event=None) -> None:
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass

    def _on_canvas(self, event) -> None:
        try:
            self.canvas.itemconfigure(self._window, width=event.width)
        except tk.TclError:
            pass

    def _on_wheel(self, event):
        try:
            if not self.winfo_exists() or not self.winfo_ismapped():
                return None
            widget = self.winfo_containing(event.x_root, event.y_root)
        except (tk.TclError, KeyError):
            return None
        if widget is None or not str(widget).startswith(str(self)):
            return None
        if widget.winfo_class() in ("Treeview", "Text", "Listbox", "TCombobox"):
            return None
        first, last = self.canvas.yview()
        if first <= 0.0 and last >= 1.0:
            return None
        if getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            delta = getattr(event, "delta", 0) or 0
            step = -1 if delta > 0 else 1
            if abs(delta) >= 120:
                step *= max(1, abs(delta) // 120)
        self.canvas.yview_scroll(step * 3, "units")
        return None
