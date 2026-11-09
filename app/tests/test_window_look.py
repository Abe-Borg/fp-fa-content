"""The thread renderer and the small widgets: bubbles, paper blocks, the working line, lists, menus, dialogs.

Every test here needs a display and skips without one.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

REPLY = (
    "Job 6b34e02bf8dc | Sample | chat\n"
    "## Design basis\n\n"
    "The zone is **double-interlock** with `t_total` on the tool plan.\n\n"
    "| Item | Value |\n| --- | --- |\n| Pipe | 276.3 gal |\n| Trim | 5.0 gal |\n\n"
    "- First point\n- Second point\n\n"
    "```\nzone_gal = 281.3\n\nt_total = 38.1\n```\n\n"
    "1. Confirm the trim.\n2. Confirm the AHJ."
)


def _isolate_data() -> None:
    os.environ["FPFA_DATA_DIR"] = tempfile.mkdtemp(prefix="fpfa-look-")
    os.environ["FPFA_CONTENT_UPDATES"] = "0"
    os.environ.pop("FPFA_THEME", None)
    os.environ.pop("FPFA_REDUCE_MOTION", None)
    from fpfa.paths import write_config

    write_config({"key_backend": "file"})


class _Window(unittest.TestCase):
    def _root(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("no display")
        try:
            import tkinter as tk
        except ImportError:
            self.skipTest("tkinter is not installed")
        _isolate_data()
        root = tk.Tk()
        root.geometry("900x700+0+0")
        self.addCleanup(root.destroy)
        return root

    def _thread(self):
        import tkinter as tk

        from fpfa import theme
        from fpfa.thread_view import ThreadView

        root = self._root()
        look = theme.apply_theme(root, "clay")
        view = tk.Text(root, wrap="word", state="disabled", width=90, height=30)
        view.pack(fill="both", expand=True)
        copied = []
        thread = ThreadView(view, look, links={"link_sample_di": lambda: copied.append("link")}, on_copy=copied.append)
        root.update()
        return root, view, thread, copied

    def _app(self, **options):
        from fpfa.ui import App

        root = self._root()
        app = App(root, **options)
        root.update()
        return app

    def _wheel(self, widget, *, up: bool) -> None:
        """One turn of the wheel over widget, as this display sends it."""
        # Tk 9 uses MouseWheel on X11 too; generating Button-4 there reaches
        # the handler as button 8 instead of a wheel turn.
        tk_major = int(str(widget.tk.call("package", "provide", "Tk")).split(".")[0])
        if str(widget.tk.call("tk", "windowingsystem")) == "x11" and tk_major < 9:
            widget.event_generate("<Button-4>" if up else "<Button-5>")
        else:
            widget.event_generate("<MouseWheel>", delta=120 if up else -120)

    def _focus(self, widget) -> None:
        """Give widget the keyboard. Tk sends a key to whatever holds the focus, so a key test needs it."""
        widget.focus_force()
        widget.update()
        if widget.focus_get() is not widget:
            self.skipTest("this display gives no keyboard focus")


class ThreadViewTests(_Window):
    def test_a_message_is_a_bubble_and_its_words_stay_in_the_text(self):
        root, view, thread, copied = self._thread()
        thread.render([{"role": "user", "text": "Which trim family?"}, {"role": "assistant", "text": REPLY}])
        root.update()
        text = view.get("1.0", "end")
        self.assertIn("You\nWhich trim family?\n", text)
        # The words are hidden beside the bubble that shows them.
        start = text.index("Which trim family?")
        self.assertIn("user_hidden", view.tag_names(f"1.0 + {start} chars"))
        self.assertEqual(str(view.tag_cget("user_hidden", "elide")), "1")
        bubbles = [child for child in view.winfo_children() if "Bubble" in str(child.cget("style"))]
        self.assertEqual(len(bubbles), 1)
        self.assertEqual(str(bubbles[0].winfo_children()[0].cget("text")), "Which trim family?")
        self.assertTrue(bubbles[0].winfo_ismapped())
        bubbles[0].event_generate("<Button-3>")
        self.assertEqual(copied, ["Which trim family?"])
        # A second render replaces the bubble instead of piling another on top.
        thread.render([{"role": "user", "text": "Which trim family?"}])
        root.update()
        self.assertEqual(len([c for c in view.winfo_children() if "Bubble" in str(c.cget("style"))]), 1)

    def test_a_reply_is_drawn_from_markdown_with_blocks_on_paper(self):
        from fpfa.chat_render import plain_text
        from fpfa.theme import colors

        root, view, thread, _copied = self._thread()
        thread.render([{"role": "assistant", "text": REPLY}])
        root.update()
        text = view.get("1.0", "end")
        self.assertIn(plain_text(REPLY), text)
        self.assertNotIn("**", text)
        self.assertNotIn("##", text)

        def tags_at(needle: str) -> tuple:
            return view.tag_names(f"1.0 + {text.index(needle)} chars")

        self.assertIn("meta", tags_at("Job 6b34e02bf8dc"))
        self.assertIn("heading", tags_at("Design basis"))
        self.assertIn("bold", tags_at("double-interlock"))
        self.assertIn("code", tags_at("t_total"))
        self.assertIn("bullet", tags_at("First point"))
        # The table and the code are one block each: paper colour, padded at its first and last line.
        self.assertIn("pre", tags_at("Item"))
        self.assertIn("pre_first", tags_at("Item"))
        self.assertIn("pre_last", tags_at("Trim  5.0 gal"))
        self.assertNotIn("pre_first", tags_at("Pipe  276.3 gal"))
        self.assertIn("pre_first", tags_at("zone_gal = 281.3"))
        self.assertIn("pre_last", tags_at("t_total = 38.1"))
        self.assertEqual(str(view.tag_cget("pre", "background")), colors.paper)
        self.assertEqual(str(view.tag_cget("pre", "foreground")), colors.paper_ink)
        # A blank line between paragraphs is a short gap, not a full line.
        gap_at = text.index("Design basis") + len("Design basis") + 1
        self.assertIn("gap", view.tag_names(f"1.0 + {gap_at} chars"))

    def test_the_welcome_has_its_title_and_links(self):
        root, view, thread, copied = self._thread()
        thread.render([], welcome={
            "title": "What are we working on?",
            "lines": ["Ask about a zone."],
            "links": [("Try the sample zone", "link_sample_di")],
            "footnote": "The sample is optional.",
        })
        root.update()
        text = view.get("1.0", "end")
        for part in ("What are we working on?", "Ask about a zone.", "Try the sample zone", "The sample is optional."):
            self.assertIn(part, text)
        self.assertTrue(view.tag_ranges("link_sample_di"))
        self.assertTrue(view.image_names())

    def test_a_reply_drawn_piece_by_piece_ends_as_the_reply_drawn_whole(self):
        root, view, thread, _copied = self._thread()
        earlier = [{"role": "user", "text": "Give me the basis."}]
        thread.render(earlier + [{"role": "assistant", "text": REPLY}])
        root.update()
        whole = view.get("1.0", "end")

        thread.render(earlier, live=[{"key": "job", "text": "", "caret": True, "fades": [], "settled": 0}])
        seen_caret = False
        for end in list(range(1, len(REPLY), 7)) + [len(REPLY)]:
            shown = REPLY[:end]
            # Everything but the newest forty characters has settled, and the newest are fading in.
            item = {"key": "job", "text": shown, "caret": True, "settled": max(0, end - 40),
                    "fades": [(min(end, 8), 0), (min(end, 20), 2), (min(end, 40), 4)]}
            thread.render_live([item])
            now = view.get("1.0", "end")
            seen_caret = seen_caret or "▍" in now
            self.assertIn("Give me the basis.", now)
        self.assertTrue(seen_caret)
        self.assertTrue(any(view.tag_ranges(f"fade{step}") for step in range(6)))
        thread.render_live([{"key": "job", "text": REPLY, "caret": False, "fades": [], "settled": None}])
        thread.commit_live()
        root.update()
        self.assertEqual(view.get("1.0", "end"), whole)
        for step in range(6):
            self.assertEqual(view.tag_ranges(f"fade{step}"), ())
        self.assertEqual(view.tag_ranges("caret"), ())
        # Committed text is part of the thread: an empty live list leaves it in place.
        thread.render_live([])
        self.assertEqual(view.get("1.0", "end"), whole)

    def test_a_reply_that_starts_over_is_redrawn_from_its_start(self):
        root, view, thread, _copied = self._thread()
        thread.render([], live=[{"key": "job", "text": "First paragraph.\n\nSecond one grows", "caret": True,
                                 "fades": [], "settled": None}])
        self.assertIn("First paragraph.", view.get("1.0", "end"))
        thread.render_live([{"key": "job", "text": "A different answer.", "caret": True, "fades": [], "settled": None}])
        text = view.get("1.0", "end")
        self.assertIn("A different answer.", text)
        self.assertNotIn("First paragraph.", text)

    def test_the_working_line_comes_and_goes_under_the_live_reply(self):
        root, view, thread, _copied = self._thread()
        thread.render([{"role": "user", "text": "q"}], pending={"label": "Working on it…", "detail": "thinking"})
        root.update()
        text = view.get("1.0", "end")
        self.assertIn("Working on it… thinking", text)
        self.assertEqual(len([c for c in view.winfo_children() if c.winfo_class() == "TFrame"
                              and "Bubble" not in str(c.cget("style"))]), 1)
        thread.render_pending({"label": "Working on it…", "detail": "running zone_trapped_volume"})
        self.assertIn("Working on it… running zone_trapped_volume", view.get("1.0", "end"))
        self.assertNotIn("thinking", view.get("1.0", "end"))
        # Words arrive above the line, never below it.
        thread.render_live([{"key": "job", "text": "The zone total", "caret": True, "fades": [], "settled": None}])
        text = view.get("1.0", "end")
        self.assertLess(text.index("The zone total"), text.index("Working on it…"))
        thread.render_pending(None)
        root.update()
        text = view.get("1.0", "end")
        self.assertNotIn("Working on it…", text)
        self.assertIn("The zone total", text)

    def test_a_reader_who_scrolled_up_is_left_where_they_are(self):
        root, view, thread, _copied = self._thread()
        long_thread = [{"role": "assistant", "text": f"Paragraph {n}. " + "words " * 60} for n in range(30)]
        thread.render(long_thread)
        root.update()
        self.assertTrue(thread.follow)
        self.assertGreater(view.yview()[1], 0.99)
        view.yview_moveto(0.0)
        root.update()
        thread.user_moved()
        root.update()
        self.assertFalse(thread.follow)
        thread.render_live([{"key": "job", "text": "New words arrive. " * 40, "caret": True, "fades": [],
                             "settled": None}])
        root.update()
        self.assertLess(view.yview()[0], 0.05)
        # Back at the end, the thread follows again.
        view.yview_moveto(1.0)
        root.update()
        thread.user_moved()
        root.update()
        self.assertTrue(thread.follow)

    def test_a_thread_drawn_again_with_bubbles_still_ends_at_its_end(self):
        # A bubble has no height until it is on screen, so the end of the thread moves down
        # after the thread has scrolled to it. The last line has to be on screen all the same.
        root, view, thread, _copied = self._thread()

        def last_line_shown() -> bool:
            line = view.dlineinfo("end-1c")
            return line is not None and line[1] + line[3] <= view.winfo_height()

        turns = []
        for n in range(1, 9):
            turns.append({"role": "user", "text": f"Question {n}: what is the zone total, and what does the trim add?"})
            turns.append({"role": "assistant", "text": f"Answer {n}. " + "words " * 90})
            thread.render(turns)
            for _ in range(4):
                root.update()
            self.assertTrue(last_line_shown(), n)
            self.assertGreater(view.yview()[1], 0.995, n)
            self.assertTrue(thread.follow, n)
        # A reader who went up is not brought back: not by the bubbles up there finding their
        # size as they come on screen, and not by every bubble wrapping to a narrower column.
        view.yview_moveto(0.0)
        thread.user_moved()
        for _ in range(4):
            root.update()
        self.assertFalse(thread.follow)
        self.assertLess(view.yview()[0], 0.05)
        thread.set_column(thread._column - 120)
        for _ in range(4):
            root.update()
        self.assertFalse(last_line_shown())
        self.assertLess(view.yview()[0], 0.05)
        # Back at the end and following, the narrower column's taller thread is followed too.
        view.yview_moveto(1.0)
        thread.user_moved()
        root.update()
        self.assertTrue(thread.follow)
        thread.set_column(thread._column - 120)
        for _ in range(4):
            root.update()
        self.assertTrue(last_line_shown())

    def test_the_wheel_over_a_bubble_is_the_reader_moving(self):
        # A bubble is a widget of its own, so a wheel turned over one never reaches the
        # thread's own wheel binding. It has to count all the same.
        root, view, thread, _copied = self._thread()
        turns = []
        for n in range(14):
            turns.append({"role": "user", "text": f"Question {n}: what is the zone total?"})
            turns.append({"role": "assistant", "text": f"Answer {n}. " + "words " * 80})
        thread.render(turns)
        for _ in range(4):
            root.update()
        self.assertTrue(thread.follow)
        self.assertGreater(view.yview()[1], 0.99)
        bubble = thread._embedded[-1]

        def turn(times: int, *, up: bool) -> None:
            for _ in range(times):
                self._wheel(bubble, up=up)
                root.update()
            root.update()

        turn(3, up=True)
        self.assertLess(view.yview()[1], 0.99)
        self.assertFalse(thread.follow)
        # Wheeled back to the end over the same bubble, the thread follows again.
        turn(6, up=False)
        self.assertGreater(view.yview()[1], 0.99)
        self.assertTrue(thread.follow)
        # New words under a reader who wheeled away do not pull them back down.
        turn(3, up=True)
        self.assertFalse(thread.follow)
        thread.render_live([{"key": "job", "text": "New words arrive. " * 40, "caret": True, "fades": [],
                             "settled": None}])
        root.update()
        self.assertLess(view.yview()[1], 0.99)


class WidgetTests(_Window):
    def test_the_list_answers_the_listbox_calls_the_window_makes(self):
        from fpfa import theme
        from fpfa.widgets import ListView

        root = self._root()
        look = theme.apply_theme(root, "clay")
        listing = ListView(root, look=look)
        listing.pack(fill="both", expand=True)
        heard = []
        listing.bind("<<ListboxSelect>>", lambda _event: heard.append(listing.curselection()))
        for name in ("Sample data hall DI zone", "Hall 2 zoning", "BESS room"):
            listing.insert("end", name)
        root.update()
        self.assertEqual(listing.size(), 3)
        self.assertEqual(listing.get(0, "end"), ("Sample data hall DI zone", "Hall 2 zoning", "BESS room"))
        self.assertEqual(listing.get(1), "Hall 2 zoning")
        # A selection made in code is not announced. A click or a key is.
        listing.selection_set(1)
        root.update()
        self.assertEqual(listing.curselection(), (1,))
        self.assertEqual(heard, [])
        listing.event_generate("<ButtonRelease-1>", x=5, y=5)
        root.update()
        self.assertEqual(heard, [(1,)])
        listing.selection_clear(0, "end")
        self.assertEqual(listing.curselection(), ())
        box = listing.bbox(listing.get_children()[2])
        self.assertEqual(listing.nearest(box[1] + 2), 2)
        self.assertEqual(listing.nearest(box[1] + box[3] + 400), -1)
        listing.delete(1)
        self.assertEqual(listing.get(0, "end"), ("Sample data hall DI zone", "BESS room"))
        listing.insert(0, "First", display="1st", tags=("accent",))
        self.assertEqual(listing.get(0), "First")
        self.assertEqual(listing.item(listing.get_children()[0], "text"), "1st")
        listing.delete(0, "end")
        self.assertEqual((listing.size(), listing.get(0, "end")), (0, ()))
        listing.see("end")
        listing.selection_set(0)

    def test_a_long_row_is_cut_with_an_ellipsis_and_get_keeps_the_full_text(self):
        from fpfa import theme
        from fpfa.widgets import ListView

        root = self._root()
        root.geometry("260x300+0+0")
        look = theme.apply_theme(root, "clay")
        listing = ListView(root, look=look)
        listing.pack(fill="both", expand=True)
        name = "How should I split a 40,000 ft2 data hall into double-interlock zones"
        listing.insert("end", name)
        root.update()
        root.update()
        shown = listing.item(listing.get_children()[0], "text")
        self.assertTrue(shown.endswith("…"))
        self.assertTrue(name.startswith(shown[:-1].rstrip()))
        self.assertEqual(listing.get(0), name)

    def test_the_menu_is_read_from_its_model_and_a_choice_invokes_it(self):
        app = self._app()
        entries = app.popup.entries(app.more_menu)
        labels = [entry.get("label") for entry in entries if entry["kind"] != "separator"]
        self.assertIn("Sample DI zone", labels)
        self.assertIn("About and versions", labels)
        self.assertEqual(sum(1 for entry in entries if entry["kind"] == "separator"), 3)
        sample = next(entry for entry in entries if entry.get("label") == "Sample DI zone")
        self.assertEqual(sample["accelerator"], "/sample-di")
        narrate = next(entry for entry in entries if entry.get("label") == "Narrate zone runs with Claude")
        self.assertFalse(narrate["checked"])
        app.ask_claude.set(True)
        narrate = next(e for e in app.popup.entries(app.more_menu) if e.get("label") == "Narrate zone runs with Claude")
        self.assertTrue(narrate["checked"])
        modes = app.popup.entries(app.mode_menu)
        self.assertEqual([entry["label"] for entry in modes if entry["checked"]], ["Mixed"])

        app._drop_menu(app.more_button, app.more_menu, align="right")
        app.root.update()
        self.assertTrue(app.popup.showing)
        rows = [index for index, _parts in app.popup._rows]
        team = next(entry["index"] for entry in entries if entry.get("label") == "Team panel")
        app.popup._choose(rows.index(team))
        app.root.update()
        app.root.update()
        self.assertFalse(app.popup.showing)
        self.assertTrue(app.details_open.get())
        # The mode menu sets the mode, as the native menu did.
        app._drop_menu(app.mode_button, app.mode_menu, align="right")
        app.root.update()
        calculator = next(i for i, entry in enumerate(app.popup.entries(app.mode_menu)) if entry["label"] == "Calculator")
        app.popup._choose(calculator)
        app.root.update()
        app.root.update()
        self.assertEqual(app.mode_slug.get(), "calculator")
        self.assertEqual(str(app.mode_button.cget("text")), "Mode: calculator")
        app._drop_menu(app.more_button, app.more_menu)
        app.popup.close()
        self.assertFalse(app.popup.showing)

    def test_the_menu_buttons_open_from_the_keyboard(self):
        # The window draws these menus itself, so the buttons carry no "menu" option and
        # ttk's own Space does nothing. The keys a menu button answers to are bound here.
        app = self._app()
        root = app.root
        for button, menu in ((app.mode_button, app.mode_menu), (app.more_button, app.more_menu)):
            usable = [entry for entry in app.popup.entries(menu) if entry["kind"] != "separator"
                      and not entry["disabled"]]
            for sequence in ("<Key-space>", "<Key-Return>", "<Key-Down>", "<<Invoke>>"):
                self._focus(button)
                button.event_generate(sequence)
                root.update()
                self.assertTrue(app.popup.showing, sequence)
                # Opened from the keys, the first row is chosen already, so Return works at once.
                self.assertEqual(app.popup._rows[app.popup._active][0], usable[0]["index"], sequence)
                self.assertTrue(app.theme.keyboard)
                app.popup._top.event_generate("<Key-Escape>")
                root.update()
                self.assertFalse(app.popup.showing, sequence)
                # Escape chose nothing and the keys are back on the button.
                self.assertIs(root.focus_get(), button, sequence)
        self.assertEqual(app.mode_slug.get(), "mixed")
        self.assertFalse(app.details_open.get())
        # Home, Down, Return picks the second mode.
        labels = [entry["label"] for entry in app.popup.entries(app.mode_menu)]
        self._focus(app.mode_button)
        app.mode_button.event_generate("<Key-space>")
        root.update()
        for sequence in ("<Key-End>", "<Key-Home>", "<Key-Down>"):
            app.popup._top.event_generate(sequence)
            root.update()
        self.assertEqual(labels[app.popup._rows[app.popup._active][0]], "Calculator")
        app.popup._top.event_generate("<Key-Return>")
        root.update()
        root.update()
        self.assertFalse(app.popup.showing)
        self.assertEqual(app.mode_slug.get(), "calculator")
        self.assertIs(root.focus_get(), app.mode_button)
        # A click still opens the menu, with no row chosen until the pointer is over one.
        app.mode_button.event_generate("<Button-1>", x=4, y=4)
        root.update()
        self.assertTrue(app.popup.showing)
        self.assertIsNone(app.popup._active)
        self.assertFalse(app.theme.keyboard)
        app.popup.close()

    def test_the_keys_pass_over_a_row_that_cannot_be_chosen(self):
        import tkinter as tk

        app = self._app()
        root = app.root
        picked = []
        model = tk.Menu(root, tearoff=0)
        model.add_command(label="Off", state="disabled", command=lambda: picked.append("off"))
        model.add_command(label="One", command=lambda: picked.append("one"))
        model.add_separator()
        model.add_command(label="Also off", state="disabled", command=lambda: picked.append("also off"))
        model.add_command(label="Two", command=lambda: picked.append("two"))

        def chosen() -> str:
            return str(model.entrycget(app.popup._rows[app.popup._active][0], "label"))

        app.popup.show(model, 40, 40, keyboard=True)
        root.update()
        self.assertEqual(chosen(), "One")
        app.popup._step(1)
        self.assertEqual(chosen(), "Two")
        app.popup._step(1)
        self.assertEqual(chosen(), "One")
        app.popup._step(-1)
        self.assertEqual(chosen(), "Two")
        app.popup._edge(0)
        self.assertEqual(chosen(), "One")
        app.popup._edge(-1)
        app.popup._choose(app.popup._active)
        root.update()
        root.update()
        self.assertEqual(picked, ["two"])
        # A menu with nothing to choose opens, takes the keys, and chooses nothing.
        empty = tk.Menu(root, tearoff=0)
        empty.add_command(label="Off", state="disabled", command=lambda: picked.append("off"))
        app.popup.show(empty, 40, 40, keyboard=True)
        root.update()
        self.assertIsNone(app.popup._active)
        app.popup._step(1)
        app.popup._step(-1)
        self.assertIsNone(app.popup._active)
        app.popup._choose(app.popup._active)
        root.update()
        self.assertTrue(app.popup.showing)
        app.popup.close()
        self.assertEqual(picked, ["two"])

    def test_dialogs_answer_like_the_stock_ones(self):
        import tkinter as tk

        from fpfa import dialogs, theme

        root = self._root()
        theme.apply_theme(root, "clay")

        def press(label: str) -> None:
            def find(widget):
                for child in widget.winfo_children():
                    if child.winfo_class() == "TButton" and str(child.cget("text")) == label:
                        return child
                    found = find(child)
                    if found is not None:
                        return found
                return None

            for window in root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    button = find(window)
                    if button is not None:
                        button.invoke()
                        return
            raise AssertionError(f"no {label} button is showing")

        root.after(150, lambda: press("Yes"))
        self.assertTrue(dialogs.askyesno("Delete", "Delete this job?", parent=root))
        root.after(150, lambda: press("Cancel"))
        self.assertFalse(dialogs.askyesno("Delete", "Delete this job?", parent=root))
        root.after(150, lambda: press("Save"))
        self.assertEqual(dialogs.askstring("Rename job", "Job name", initialvalue="Hall 2", parent=root), "Hall 2")
        root.after(150, lambda: press("Cancel"))
        self.assertIsNone(dialogs.askstring("Rename job", "Job name", initialvalue="Hall 2", parent=root))
        root.after(150, lambda: press("OK"))
        self.assertEqual(dialogs.showinfo("Export", "A zone run is needed first.", parent=root), "ok")
        root.after(150, lambda: press("OK"))
        self.assertEqual(dialogs.showerror("Save", "A value is not a number.", parent=root), "ok")
        # With no themed window behind it, the stock dialog is used.
        bare = tk.Tk()
        self.addCleanup(bare.destroy)
        with patch("fpfa.dialogs._stock_message.showerror", return_value="ok") as stock:
            dialogs.showerror("+Cynosure", "Already open.", parent=bare)
        stock.assert_called_once()

    def test_about_license_and_notices_open_from_settings(self):
        app = self._app()
        with patch("fpfa.ui.dialogs.showtext") as shown:
            app.show_license()
            app.show_notices()
        license_call, notices_call = shown.call_args_list
        self.assertEqual(license_call.args[0], "+Cynosure license")
        self.assertIn("# PolyForm Shield License 1.0.0", license_call.args[1])
        self.assertIn("Required Notice: Copyright (c) 2026 Abraham Borg", license_call.args[1])
        self.assertIn("engineer of record", license_call.kwargs["note"])
        self.assertEqual(notices_call.args[0], "Third-party notices")
        app.open_settings()
        app.root.update()
        labels = []

        def walk(widget):
            for child in widget.winfo_children():
                if child.winfo_class() == "TButton":
                    labels.append(str(child.cget("text")))
                walk(child)

        walk(app._settings_window)
        for label in ("License", "Third-party notices", "About and versions", "Save key", "Check for updates"):
            self.assertIn(label, labels)
        # A second click on Settings brings the same window forward.
        first = app._settings_window
        app.open_settings()
        self.assertIs(app._settings_window, first)

    def test_a_long_text_opens_on_a_paper_sheet(self):
        import tkinter as tk

        from fpfa import dialogs, theme

        root = self._root()
        theme.apply_theme(root, "clay")
        top = dialogs.showtext("License", "Line one.\nLine two.", parent=root, heading="Terms", wait=False)
        root.update()
        self.assertIsInstance(top, tk.Toplevel)
        texts = []

        def walk(widget):
            for child in widget.winfo_children():
                if child.winfo_class() == "Text":
                    texts.append(child)
                walk(child)

        walk(top)
        self.assertEqual(texts[0].get("1.0", "end-1c"), "Line one.\nLine two.")
        self.assertEqual(str(texts[0].cget("bg")), theme.colors.paper)
        top.destroy()


if __name__ == "__main__":
    unittest.main()
