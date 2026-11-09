"""Message, question, and text dialogs in the window's own colours.

The functions carry the names and arguments of tkinter.messagebox and
tkinter.simpledialog (askstring, askyesno, showinfo, showerror, showwarning),
so ui.py imports this module under both names and a test patches
fpfa.ui.messagebox.askyesno as before. A call with no themed window behind
it, such as the one that reports a second window before the first window
exists, falls back to the stock dialog.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox as _stock_message
from tkinter import simpledialog as _stock_simple
from tkinter import ttk

from fpfa import theme
from fpfa.theme import colors


def _owner(parent: tk.Misc | None) -> tk.Misc | None:
    return parent if parent is not None else getattr(tk, "_default_root", None)


class Modal:
    """A dialog window over its parent. run() shows it and returns after it closes."""

    def __init__(self, parent: tk.Misc, look: "theme.Theme", title: str, *, width: int = 440):
        self.look = look
        self.result = None
        px = look.px
        top = tk.Toplevel(parent)
        top.withdraw()
        top.title(title)
        # A hairline around the dialog, for a desktop that draws no frame of its own.
        top.configure(bg=colors.bg, highlightthickness=1)
        look.paint(top, bg="bg", highlightbackground="edge", highlightcolor="edge")
        try:
            top.transient(parent.winfo_toplevel())
        except tk.TclError:
            pass
        top.resizable(False, False)
        self.top = top
        self.parent = parent
        self.width = px(width)
        self.body = ttk.Frame(top, padding=(px(24), px(20), px(24), px(8)))
        self.body.pack(fill="both", expand=True)
        self.buttons = ttk.Frame(top, padding=(px(24), px(8), px(24), px(18)))
        self.buttons.pack(fill="x")
        top.protocol("WM_DELETE_WINDOW", self.cancel)
        top.bind("<Escape>", lambda _event: self.cancel())

    def heading(self, text: str) -> None:
        ttk.Label(self.body, text=text, style="Heading.TLabel", wraplength=self.width, justify="left").pack(
            anchor="w", pady=(0, self.look.px(8))
        )

    def message(self, text: str, *, style: str = "Dim.TLabel") -> None:
        ttk.Label(self.body, text=text, style=style, wraplength=self.width, justify="left").pack(anchor="w")

    def button(self, text: str, command, *, primary: bool = False) -> ttk.Button:
        made = ttk.Button(self.buttons, text=text, command=command, style="Accent.TButton" if primary else "TButton")
        made.pack(side="right", padx=(self.look.px(8), 0))
        return made

    def close(self, result=None) -> None:
        self.result = result
        try:
            self.top.grab_release()
        except tk.TclError:
            pass
        try:
            self.top.destroy()
        except tk.TclError:
            pass

    def cancel(self) -> None:
        self.close(None)

    def run(self, focus: tk.Misc | None = None):
        top = self.top
        try:
            top.update_idletasks()
            owner = self.parent.winfo_toplevel()
            x = owner.winfo_rootx() + max(0, (owner.winfo_width() - top.winfo_reqwidth()) // 2)
            y = owner.winfo_rooty() + max(0, (owner.winfo_height() - top.winfo_reqheight()) // 3)
            top.geometry(f"+{x}+{y}")
            top.deiconify()
            theme.style_title_bar(top)
            top.lift()
            (focus or top).focus_set()
            top.grab_set()
            top.wait_window()
        except tk.TclError:
            pass
        return self.result


def _notice(title, message, parent, *, heading_style: str, stock) -> str:
    owner = _owner(parent)
    look = theme.theme_of(owner)
    if look is None or owner is None:
        return stock(title, message) if parent is None else stock(title, message, parent=parent)
    box = Modal(owner, look, title or "")
    ttk.Label(box.body, text=title or "", style=heading_style, wraplength=box.width, justify="left").pack(
        anchor="w", pady=(0, look.px(8))
    )
    box.message(str(message or ""))
    ok = box.button("OK", lambda: box.close("ok"), primary=True)
    box.top.bind("<Return>", lambda _event: box.close("ok"))
    box.run(focus=ok)
    return "ok"


def showinfo(title=None, message=None, parent=None, **_options) -> str:
    return _notice(title, message, parent, heading_style="Heading.TLabel", stock=_stock_message.showinfo)


def showwarning(title=None, message=None, parent=None, **_options) -> str:
    return _notice(title, message, parent, heading_style="Heading.TLabel", stock=_stock_message.showwarning)


def showerror(title=None, message=None, parent=None, **_options) -> str:
    return _notice(title, message, parent, heading_style="Heading.TLabel", stock=_stock_message.showerror)


def askyesno(title=None, message=None, parent=None, *, yes: str = "Yes", no: str = "Cancel", **_options) -> bool:
    owner = _owner(parent)
    look = theme.theme_of(owner)
    if look is None or owner is None:
        if parent is None:
            return bool(_stock_message.askyesno(title, message))
        return bool(_stock_message.askyesno(title, message, parent=parent))
    box = Modal(owner, look, title or "")
    box.heading(title or "")
    box.message(str(message or ""))
    confirm = box.button(yes, lambda: box.close(True), primary=True)
    box.button(no, lambda: box.close(False))
    box.top.bind("<Return>", lambda _event: box.close(True))
    return bool(box.run(focus=confirm))


def askstring(title, prompt, initialvalue=None, parent=None, **_options) -> str | None:
    owner = _owner(parent)
    look = theme.theme_of(owner)
    if look is None or owner is None:
        return _stock_simple.askstring(title, prompt, initialvalue=initialvalue, parent=parent)
    box = Modal(owner, look, title or "")
    box.heading(title or "")
    box.message(str(prompt or ""))
    value = tk.StringVar(value=initialvalue or "")
    entry = ttk.Entry(box.body, textvariable=value, width=40)
    entry.pack(fill="x", pady=(look.px(10), 0))
    entry.selection_range(0, "end")
    entry.icursor("end")
    box.button("Save", lambda: box.close(value.get()), primary=True)
    box.button("Cancel", box.cancel)
    box.top.bind("<Return>", lambda _event: box.close(value.get()))
    return box.run(focus=entry)


def showtext(
    title: str,
    text: str,
    parent: tk.Misc | None = None,
    *,
    heading: str | None = None,
    note: str = "",
    width: int = 720,
    height: int = 520,
    mono: bool = False,
    wait: bool = True,
):
    """A long text on a paper sheet that scrolls: the license, the notices, the versions."""
    owner = _owner(parent)
    look = theme.theme_of(owner)
    if look is None or owner is None:
        return _stock_message.showinfo(title, text)
    px = look.px
    top = tk.Toplevel(owner)
    top.withdraw()
    top.title(title)
    top.configure(highlightthickness=1)
    look.paint(top, bg="bg", highlightbackground="edge", highlightcolor="edge")
    try:
        top.transient(owner.winfo_toplevel())
    except tk.TclError:
        pass
    top.geometry(f"{px(width)}x{px(height)}")
    top.minsize(px(420), px(320))
    frame = ttk.Frame(top, padding=(px(22), px(18), px(22), px(16)))
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=heading or title, style="Job.TLabel").pack(anchor="w")
    if note:
        ttk.Label(frame, text=note, style="Dim.TLabel", wraplength=px(width - 60), justify="left").pack(
            anchor="w", pady=(px(4), 0)
        )
    buttons = ttk.Frame(frame)
    buttons.pack(side="bottom", fill="x", pady=(px(12), 0))

    def copy() -> None:
        try:
            top.clipboard_clear()
            top.clipboard_append(text)
            copied.configure(text="Copied")
        except tk.TclError:
            pass

    ttk.Button(buttons, text="Close", style="Accent.TButton", command=top.destroy).pack(side="right")
    copied = ttk.Button(buttons, text="Copy", command=copy)
    copied.pack(side="right", padx=(0, px(8)))
    sheet = ttk.Frame(frame, style="Paper.TFrame", padding=(px(4), px(4), px(4), px(4)))
    sheet.pack(fill="both", expand=True, pady=(px(12), 0))
    view = tk.Text(
        sheet, wrap="word", bd=0, relief="flat", highlightthickness=0,
        padx=px(16), pady=px(12), font=look.fonts["mono" if mono else "ui"], spacing2=px(2),
    )
    look.paint(view, bg="paper", fg="paper_ink", selectbackground="paper_select",
               selectforeground="paper_ink", insertbackground="paper")
    scroll = ttk.Scrollbar(sheet, command=view.yview, style="OnPaper.Vertical.TScrollbar")
    view.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y", pady=px(6))
    view.pack(side="left", fill="both", expand=True)
    view.insert("1.0", text)
    view.configure(state="disabled")
    top.bind("<Escape>", lambda _event: top.destroy())
    try:
        top.update_idletasks()
        host = owner.winfo_toplevel()
        x = host.winfo_rootx() + max(0, (host.winfo_width() - px(width)) // 2)
        y = host.winfo_rooty() + max(0, (host.winfo_height() - px(height)) // 3)
        top.geometry(f"+{x}+{y}")
        top.deiconify()
        theme.style_title_bar(top)
        top.lift()
        view.focus_set()
        if wait:
            top.grab_set()
            top.wait_window()
    except tk.TclError:
        pass
    return top
