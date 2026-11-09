"""Small tkinter widgets the window uses.

Composer is the multi-line message box. It keeps the few Entry calls the
window already makes (get(), insert(0, text), delete(0, "end")) so code that
used a one-line entry still works. ScrollFrame holds a form that can be
taller than the window. ListView is a list with a rounded highlight that
answers the Listbox calls the window makes. PopupMenu draws a tk.Menu in the
window's own colours, because Windows draws a native menu in its own.
StatusDots is the three pulsing dots of a working line, Chip a one-tap
suggestion, and Tooltip a short label under the pointer.

Colours come from theme.colors, so every widget follows the colour scheme.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from fpfa import theme
from fpfa.theme import colors


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
        look: "theme.Theme | None" = None,
        **kwargs,
    ):
        kwargs.setdefault("height", min_lines)
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("undo", True)
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bg", colors.raised)
        kwargs.setdefault("fg", colors.ink)
        kwargs.setdefault("insertbackground", colors.ink)
        kwargs.setdefault("selectbackground", colors.select)
        kwargs.setdefault("selectforeground", colors.ink)
        super().__init__(master, **kwargs)
        self._on_submit = on_submit
        self._min_lines = max(1, min_lines)
        self._max_lines = max(self._min_lines, max_lines)
        self._placeholder = tk.Label(
            self,
            text=placeholder,
            fg=colors.ink_faint,
            bg=colors.raised,
            font=placeholder_font or kwargs.get("font"),
            anchor="w",
            cursor="xterm",
            borderwidth=0,
            padx=0,
            pady=0,
        )
        if look is not None:
            look.paint(
                self, bg="raised", fg="ink", insertbackground="ink",
                selectbackground="select", selectforeground="ink",
            )
            look.paint(self._placeholder, bg="raised", fg="ink_faint")
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


_SURFACE_STYLE = {"bg": "", "surface": "OnSide.", "raised": "OnCard.", "paper": "OnPaper."}


def on(surface: str, style: str) -> str:
    """The style name for a widget that sits on surface: on("surface", "TLabel") is "OnSide.TLabel"."""
    return _SURFACE_STYLE.get(surface, "") + style


class ScrollFrame(ttk.Frame):
    """A frame whose inner area scrolls vertically. Put children in .inner."""

    def __init__(self, master, *, surface: str = "bg", look: "theme.Theme | None" = None, **kwargs):
        kwargs.setdefault("style", on(surface, "TFrame"))
        super().__init__(master, **kwargs)
        look = look or theme.theme_of(master)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background=getattr(colors, surface))
        if look is not None:
            look.paint(self.canvas, background=surface)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview, style=on(surface, "Vertical.TScrollbar")
        )
        self.inner = ttk.Frame(self.canvas, style=on(surface, "TFrame"))
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
        self.canvas.yview_scroll(wheel_steps(event) * 3, "units")
        return None


def wheel_steps(event) -> int:
    """Lines to scroll for one wheel event: negative is up. X11 sends buttons 4 and 5."""
    number = getattr(event, "num", None)
    if number == 4:
        return -1
    if number == 5:
        return 1
    delta = getattr(event, "delta", 0) or 0
    step = -1 if delta > 0 else 1
    if abs(delta) >= 120:
        step *= max(1, abs(delta) // 120)
    return step


class ListView(ttk.Treeview):
    """A one-column list drawn as a ttk tree, answering the Listbox calls the window makes.

    A tk.Listbox cannot pad its rows or round its highlight. This list can,
    and it cuts a long row with an ellipsis. get() returns the full text of a
    row, whatever is shown. A click or an arrow key sends <<ListboxSelect>>,
    as a Listbox does; a selection set in code does not.
    """

    def __init__(
        self,
        master,
        *,
        look: "theme.Theme",
        style: str = "Jobs.Treeview",
        rows: int = 8,
        selectable: bool = True,
        font: str = "list",
        inset: int = 16,
        **kwargs,
    ):
        super().__init__(
            master,
            style=style,
            show="tree",
            selectmode="browse" if selectable else "none",
            height=rows,
            takefocus=1 if selectable else 0,
            **kwargs,
        )
        self._look = look
        self._font = look.fonts[font]
        self._inset = look.px(inset)
        self._rows: list[str] = []
        self._full: list[str] = []
        self._shown: list[str] = []
        self._hover: str | None = None
        self._selectable = selectable
        self.column("#0", stretch=True, width=look.px(150), minwidth=look.px(60))
        self._tag_colors()
        look.on_change(self._tag_colors)
        self.bind("<Configure>", lambda _event: self._fit(), add="+")
        if selectable:
            self.configure(cursor="hand2")
            self.bind("<Motion>", self._on_motion, add="+")
            self.bind("<Leave>", lambda _event: self._set_hover(None), add="+")
            self.bind("<ButtonRelease-1>", lambda _event: self._announce(), add="+")
            for key in ("<KeyRelease-Up>", "<KeyRelease-Down>", "<KeyRelease-Home>", "<KeyRelease-End>",
                        "<KeyRelease-Prior>", "<KeyRelease-Next>"):
                self.bind(key, lambda _event: self._announce(), add="+")

    def _tag_colors(self) -> None:
        try:
            self.tag_configure("hover", foreground=colors.ink)
            self.tag_configure("accent", foreground=colors.accent)
            self.tag_configure("ok", foreground=colors.ink_faint)
            self.tag_configure("warn", foreground=colors.warn)
            self.tag_configure("err", foreground=colors.err)
        except tk.TclError:
            pass

    def _announce(self) -> None:
        try:
            self.event_generate("<<ListboxSelect>>")
        except tk.TclError:
            pass

    # Listbox calls. Index is a row number or "end".
    def _position(self, index, *, for_insert: bool = False) -> int:
        count = len(self._rows)
        if index in ("end", tk.END):
            return count if for_insert else count - 1
        try:
            value = int(index)
        except (TypeError, ValueError):
            return count if for_insert else count - 1
        limit = count if for_insert else count - 1
        return max(0, min(value, limit)) if limit >= 0 else 0

    def size(self) -> int:
        return len(self._rows)

    def get(self, first, last=None):
        if last is None:
            position = self._position(first)
            return self._full[position] if 0 <= position < len(self._full) else ""
        start = self._position(first)
        stop = self._position(last)
        return tuple(self._full[start:stop + 1])

    def insert(self, index, *elements, display: str | None = None, tags: tuple = ()):  # type: ignore[override]
        position = self._position(index, for_insert=True)
        for offset, element in enumerate(elements):
            text = str(element)
            shown = display if display is not None and len(elements) == 1 else text
            row = ttk.Treeview.insert(self, "", position + offset, text=shown, tags=tags)
            self._rows.insert(position + offset, row)
            self._full.insert(position + offset, text)
            self._shown.insert(position + offset, shown)
        self._fit()

    def delete(self, first, last=None):  # type: ignore[override]
        if not self._rows:
            return
        start = self._position(first)
        stop = start if last is None else self._position(last)
        doomed = self._rows[start:stop + 1]
        if not doomed:
            return
        if self._hover in doomed:
            self._hover = None
        ttk.Treeview.delete(self, *doomed)
        del self._rows[start:stop + 1]
        del self._full[start:stop + 1]
        del self._shown[start:stop + 1]

    def selection_set(self, first, last=None):  # type: ignore[override]
        if not self._rows:
            return
        position = self._position(first)
        if 0 <= position < len(self._rows):
            ttk.Treeview.selection_set(self, self._rows[position])

    def selection_clear(self, first=None, last=None):
        chosen = ttk.Treeview.selection(self)
        if chosen:
            self.selection_remove(*chosen)

    def curselection(self) -> tuple:
        chosen = set(ttk.Treeview.selection(self))
        return tuple(index for index, row in enumerate(self._rows) if row in chosen)

    def see(self, index):  # type: ignore[override]
        if not self._rows:
            return
        position = self._position(index)
        if 0 <= position < len(self._rows):
            ttk.Treeview.see(self, self._rows[position])

    def nearest(self, y: int) -> int:
        """The row under y, or -1 when y is below the last row."""
        row = self.identify_row(y)
        return self._rows.index(row) if row in self._rows else -1

    def set_tags(self, index: int, tags: tuple) -> None:
        if 0 <= index < len(self._rows):
            self.item(self._rows[index], tags=tags)

    def _set_hover(self, row: str | None) -> None:
        if row == self._hover:
            return
        for item, add in ((self._hover, False), (row, True)):
            if not item or item not in self._rows:
                continue
            try:
                tags = [tag for tag in self.item(item, "tags") if tag != "hover"]
                if add:
                    tags.append("hover")
                self.item(item, tags=tags)
            except tk.TclError:
                pass
        self._hover = row

    def _on_motion(self, event) -> None:
        self._set_hover(self.identify_row(event.y) or None)

    def _fit(self) -> None:
        """Cut each row to the width with an ellipsis. The full text stays in get()."""
        try:
            room = self.winfo_width() - self._inset
        except tk.TclError:
            return
        if room <= self._look.px(24):
            return
        measure = self._font.measure
        for row, text in zip(self._rows, self._shown):
            shown = text
            if measure(text) > room:
                low, high = 0, len(text)
                while low < high:
                    middle = (low + high + 1) // 2
                    if measure(text[:middle].rstrip() + "…") <= room:
                        low = middle
                    else:
                        high = middle - 1
                shown = text[:low].rstrip() + "…"
            try:
                if self.item(row, "text") != shown:
                    self.item(row, text=shown)
            except tk.TclError:
                return


def desktop_bounds(widget: tk.Misc) -> tuple[int, int, int, int]:
    """Left, top, right, and bottom of the whole desktop, every monitor included.

    A second monitor to the left of the first has negative coordinates, so a
    drop-down opened there must not be pushed back onto the first screen.
    """
    try:
        left, top = widget.winfo_vrootx(), widget.winfo_vrooty()
        width, height = widget.winfo_vrootwidth(), widget.winfo_vrootheight()
        if width > 1 and height > 1:
            return left, top, left + width, top + height
    except tk.TclError:
        pass
    return 0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight()


class PopupMenu:
    """Shows a tk.Menu as a drop-down in the window's colours.

    The tk.Menu stays the model: its labels, accelerators, check marks, and
    commands. Windows draws a native menu in the system's colours whatever
    the app asks for, so the window draws its own. Choosing a row calls
    invoke() on the model, so a check entry toggles its variable as usual.
    """

    def __init__(self, look: "theme.Theme"):
        self._look = look
        self._top: tk.Toplevel | None = None
        self._rows: list[tuple[int, list[tk.Widget]]] = []
        self._active: int | None = None
        self._model: tk.Menu | None = None
        # A drop-down belongs to where the window was. Moving or resizing the window closes it.
        look.root.bind("<Configure>", self._on_window_change, add="+")

    def _on_window_change(self, event) -> None:
        if self._top is not None and event.widget is self._look.root:
            self.close()

    @property
    def showing(self) -> bool:
        return self._top is not None

    def entries(self, model: tk.Menu) -> list[dict]:
        """The model's rows as plain data. Separate so a test can read a menu without a pointer."""
        last = model.index("end")
        out = []
        for index in range(0 if last is None else last + 1):
            kind = model.type(index)
            if kind == "separator":
                out.append({"index": index, "kind": kind})
                continue
            if kind == "tearoff":
                continue
            row = {
                "index": index,
                "kind": kind,
                "label": str(model.entrycget(index, "label")),
                "accelerator": str(model.entrycget(index, "accelerator") or ""),
                "disabled": str(model.entrycget(index, "state")) == "disabled",
                "checked": False,
            }
            if kind in ("checkbutton", "radiobutton"):
                try:
                    current = str(model.getvar(str(model.entrycget(index, "variable"))))
                    wanted = model.entrycget(index, "onvalue" if kind == "checkbutton" else "value")
                    row["checked"] = current == str(wanted)
                except tk.TclError:
                    pass
            out.append(row)
        return out

    def show(self, model: tk.Menu, x: int, y: int, *, align: str = "left") -> None:
        """Open the menu with its top corner at screen point (x, y). align="right" hangs it leftward."""
        self.close()
        look = self._look
        px = look.px
        root = look.root
        top = tk.Toplevel(root)
        top.withdraw()
        top.overrideredirect(True)
        try:
            top.attributes("-topmost", True)
        except tk.TclError:
            pass
        frame = tk.Frame(top, bg=colors.raised, highlightthickness=1,
                         highlightbackground=colors.edge, highlightcolor=colors.edge, bd=0)
        frame.pack(fill="both", expand=True)
        body = tk.Frame(frame, bg=colors.raised, bd=0)
        body.pack(fill="both", expand=True, padx=px(5), pady=px(5))
        self._rows = []
        self._model = model
        self._active = None
        for entry in self.entries(model):
            if entry["kind"] == "separator":
                tk.Frame(body, bg=colors.edge, height=1).pack(fill="x", padx=px(8), pady=px(5))
                continue
            row = tk.Frame(body, bg=colors.raised, bd=0, cursor="arrow" if entry["disabled"] else "hand2")
            row.pack(fill="x")
            ink = colors.disabled_ink if entry["disabled"] else colors.ink
            mark = tk.Label(row, text="✓" if entry["checked"] else "", width=2, bg=colors.raised,
                            fg=colors.accent, font=look.fonts["small_bold"], bd=0)
            mark.pack(side="left", padx=(px(4), 0), pady=px(5))
            label = tk.Label(row, text=entry["label"], bg=colors.raised, fg=ink, anchor="w",
                             font=look.fonts["ui"], bd=0)
            label.pack(side="left", fill="x", expand=True, pady=px(5))
            hint = tk.Label(row, text=entry["accelerator"], bg=colors.raised, fg=colors.ink_faint,
                            anchor="e", font=look.fonts["small"], bd=0)
            hint.pack(side="right", padx=(px(22), px(10)), pady=px(5))
            parts = [row, mark, label, hint]
            position = len(self._rows)
            self._rows.append((entry["index"], parts))
            if entry["disabled"]:
                continue
            for part in parts:
                part.bind("<Enter>", lambda _event, at=position: self._highlight(at), add="+")
                part.bind("<ButtonRelease-1>", lambda _event, at=position: self._choose(at), add="+")
        top.update_idletasks()
        width, height = top.winfo_reqwidth(), top.winfo_reqheight()
        if align == "right":
            x -= width
        left, upper, right, lower = desktop_bounds(top)
        x = max(left + 4, min(x, right - width - 4))
        y = max(upper + 4, min(y, lower - height - 4))
        top.geometry(f"+{int(x)}+{int(y)}")
        top.deiconify()
        top.lift()
        self._top = top
        top.bind("<Escape>", lambda _event: self.close())
        top.bind("<FocusOut>", self._on_focus_out)
        top.bind("<Button-1>", self._on_press, add="+")
        top.bind("<Down>", lambda _event: self._step(1))
        top.bind("<Up>", lambda _event: self._step(-1))
        top.bind("<Return>", lambda _event: self._choose(self._active))
        try:
            top.focus_force()
            top.grab_set()
        except tk.TclError:
            pass

    def _on_focus_out(self, event) -> None:
        if self._top is not None and event.widget is self._top:
            self.close()

    def _on_press(self, event) -> None:
        top = self._top
        if top is None:
            return
        # With the grab held, a press anywhere else in the app is reported here, outside the box.
        x, y = event.x_root - top.winfo_rootx(), event.y_root - top.winfo_rooty()
        if x < 0 or y < 0 or x >= top.winfo_width() or y >= top.winfo_height():
            self.close()

    def _highlight(self, position: int | None) -> None:
        for at, (_index, parts) in enumerate(self._rows):
            tone = colors.accent_soft if at == position else colors.raised
            for part in parts:
                try:
                    part.configure(bg=tone)
                except tk.TclError:
                    pass
        self._active = position

    def _step(self, change: int) -> None:
        if not self._rows:
            return
        position = -1 if self._active is None else self._active
        self._highlight((position + change) % len(self._rows))

    def _choose(self, position: int | None) -> None:
        if position is None or not (0 <= position < len(self._rows)):
            return
        index = self._rows[position][0]
        model = self._model
        self.close()
        if model is None:
            return
        try:
            self._look.root.after_idle(lambda: self._invoke(model, index))
        except tk.TclError:
            pass

    @staticmethod
    def _invoke(model: tk.Menu, index: int) -> None:
        try:
            model.invoke(index)
        except tk.TclError:
            pass

    def close(self) -> None:
        top, self._top = self._top, None
        self._rows = []
        self._active = None
        if top is None:
            return
        try:
            top.grab_release()
        except tk.TclError:
            pass
        try:
            top.destroy()
        except tk.TclError:
            pass


class Tooltip:
    """A short label under the pointer after a pause. Attach with Tooltip(widget, text, look)."""

    DELAY_MS = 550

    def __init__(self, widget: tk.Widget, text: str | Callable[[], str], look: "theme.Theme"):
        self._widget = widget
        self._text = text
        self._look = look
        self._after: str | None = None
        self._top: tk.Toplevel | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        widget.bind("<Destroy>", self._hide, add="+")

    def _schedule(self, _event=None) -> None:
        self._cancel()
        try:
            self._after = self._widget.after(self.DELAY_MS, self._show)
        except tk.TclError:
            self._after = None

    def _cancel(self) -> None:
        if self._after is not None:
            try:
                self._widget.after_cancel(self._after)
            except tk.TclError:
                pass
            self._after = None

    def _show(self) -> None:
        self._after = None
        text = self._text() if callable(self._text) else self._text
        if not text or self._top is not None:
            return
        look = self._look
        px = look.px
        try:
            top = tk.Toplevel(self._widget)
            top.overrideredirect(True)
            try:
                top.attributes("-topmost", True)
            except tk.TclError:
                pass
            tk.Label(
                top, text=text, bg=colors.raised, fg=colors.ink, font=look.fonts["small"],
                padx=px(8), pady=px(4), justify="left", wraplength=px(320),
                highlightthickness=1, highlightbackground=colors.edge, bd=0,
            ).pack()
            top.update_idletasks()
            x = self._widget.winfo_rootx() + px(4)
            y = self._widget.winfo_rooty() + self._widget.winfo_height() + px(6)
            left, _upper, right, lower = desktop_bounds(top)
            x = max(left + 4, min(x, right - top.winfo_reqwidth() - 4))
            if y + top.winfo_reqheight() > lower - 4:
                y = self._widget.winfo_rooty() - top.winfo_reqheight() - px(6)
            top.geometry(f"+{int(x)}+{int(y)}")
            self._top = top
        except tk.TclError:
            self._top = None

    def _hide(self, _event=None) -> None:
        self._cancel()
        top, self._top = self._top, None
        if top is not None:
            try:
                top.destroy()
            except tk.TclError:
                pass


class StatusDots(ttk.Frame):
    """Three dots that pulse one after another while a job works: the app-is-not-frozen sign."""

    STEP_MS = 110
    # One dot's strength through a cycle; the second and third dots run behind it.
    _WAVE = (0, 1, 2, 3, 4, 4, 3, 2, 1, 0, 0, 0)

    def __init__(self, master, look: "theme.Theme", *, surface: str = "bg", animate: bool = True):
        super().__init__(master, style=on(surface, "TFrame"))
        self._look = look
        self._phase = 0
        self._after: str | None = None
        self._animate = animate
        self._dots = []
        for _ in range(3):
            dot = ttk.Label(self, image=look.image("dot_1"), style=on(surface, "TLabel"), padding=0)
            dot.pack(side="left", padx=(0, look.px(3)))
            self._dots.append(dot)
        self.bind("<Destroy>", lambda _event: self.stop(), add="+")
        self._draw()
        if animate:
            self.start()

    def _draw(self) -> None:
        wave = self._WAVE
        for index, dot in enumerate(self._dots):
            level = wave[(self._phase - 2 * index) % len(wave)]
            try:
                dot.configure(image=self._look.image(f"dot_{level}"))
            except tk.TclError:
                return

    def _tick(self) -> None:
        self._after = None
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        self._phase = (self._phase + 1) % len(self._WAVE)
        self._draw()
        self.start()

    def start(self) -> None:
        if self._after is None:
            try:
                self._after = self.after(self.STEP_MS, self._tick)
            except tk.TclError:
                self._after = None

    def stop(self) -> None:
        if self._after is not None:
            try:
                self.after_cancel(self._after)
            except tk.TclError:
                pass
            self._after = None


class Chip(ttk.Label):
    """A one-tap suggestion: a rounded outline that fills on hover and runs command on a click."""

    def __init__(self, master, text: str, command: Callable[[], object], *, surface: str = "bg", **kwargs):
        super().__init__(master, text=text, style=on(surface, "Chip.TLabel"), cursor="hand2", **kwargs)
        self._command = command
        self.bind("<Enter>", lambda _event: self.state(["active"]), add="+")
        self.bind("<Leave>", lambda _event: self.state(["!active"]), add="+")
        self.bind("<ButtonRelease-1>", self._click, add="+")

    def _click(self, event) -> None:
        # A release outside the chip is a drag away, not a click.
        if 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height():
            self._command()


def hoverable(widget: ttk.Widget) -> ttk.Widget:
    """Give a ttk label or frame the active state while the pointer is over it."""
    widget.bind("<Enter>", lambda _event: widget.state(["active"]), add="+")
    widget.bind("<Leave>", lambda _event: widget.state(["!active"]), add="+")
    return widget


class Wordmark(tk.Canvas):
    """The app's name in the display face, its leading plus sign in the accent colour.

    Two labels side by side leave a gap between the plus and the word. One
    canvas sets them at the font's own spacing.
    """

    def __init__(self, master, look: "theme.Theme", name: str, *, surface: str = "bg", font: str = "wordmark"):
        self._look = look
        # tkinter keeps the widget's own path name in _name, so the wordmark's text is _wording.
        self._wording = name
        self._surface = surface
        self._font = look.fonts[font]
        height = self._font.metrics("linespace")
        super().__init__(
            master, width=self._font.measure(name) + look.px(2), height=height,
            highlightthickness=0, bd=0, background=getattr(colors, surface),
        )
        self._draw()
        look.on_change(self._draw)

    def _draw(self) -> None:
        try:
            self.configure(background=getattr(colors, self._surface))
            self.delete("all")
            lead, rest = self._wording[:1], self._wording[1:]
            self.create_text(0, 0, text=lead, anchor="nw", font=self._font, fill=colors.accent)
            self.create_text(self._font.measure(lead), 0, text=rest, anchor="nw", font=self._font, fill=colors.ink)
        except tk.TclError:
            pass
