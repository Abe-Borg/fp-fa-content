"""Desktop shell. The chat thread is where work happens.

The window is a sidebar of jobs, the thread with its composer, and a Zone
details drawer that stays closed until it is wanted. Sample DI and Sample
BESS are optional ways to seed a thread. A typed question never needs them.

Long zone runs, chat turns, the blind claim check, and heavy jobs are on the
inbox. Workers run them so the composer stays usable. A result is labeled
with its job and stored on the project that started it. Only /heavy uses the
hosted runtime.

Run from the app directory: python -m fpfa
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import queue
import re
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from fpfa import sample_data
from fpfa import theme as palette
from fpfa.bess import bess_chat_summary, bess_govern_note, run_bess_plan
from fpfa.calc_tools import ToolSession
from fpfa.chat_render import is_job_heading, markdown_segments
from fpfa.claim_check import (
    PACKAGE_STATUS,
    build_packet,
    claim_dir,
    judge,
    same_packet,
    unanswered,
    write_packet_files,
)
from fpfa.claude_client import MODEL_ID, AnthropicMessages, TurnCancelled, run_tool_loop, safe_error, usage_summary
from fpfa.design_basis_docx import DESIGN_BASIS_TITLE, write_design_basis
from fpfa.team import check_record, export_gate, latest_check, team_summary
from fpfa.team_panel import TeamPanel
from fpfa.content_update import (
    ContentUpdateError,
    UpdateResult,
    check_for_content_update,
    content_status_line,
    content_version_text,
    current_changelog,
    format_changelog,
    remember_feed_url,
    remember_selected_root,
    resolved_feed_url,
    update_banner,
    updates_on_launch,
)
from fpfa.everyday import everyday_reply, run_everyday
from fpfa.jobs import JobInbox, label_result
from fpfa.managed import anthropic_request, reply_with_delete_status, run_heavy_job, session_system
from fpfa.keystore import clear_api_key, key_status, key_storage_help, load_api_key, save_api_key
from fpfa.modes_loader import DEFAULT_MODE, MODE_SLUGS, list_modes, normalize_mode
from fpfa.paths import content_root, is_content_pack, read_config, write_config
from fpfa.projects import delete_project, list_projects, load_project, new_project, save_project
from fpfa.record import Record
from fpfa.spec_docx import DRAFT_SECTION, write_docx
from fpfa.theme import apply_theme, enable_windows_dpi_awareness
from fpfa.widgets import Composer, ScrollFrame
from fpfa.workflow import (
    NARRATION_CANCELLED,
    form_assumption_lines,
    format_transcript,
    govern_note,
    judgment_label_line,
    run_di_zone,
    screen_limit_assumption_text,
    trim_assumption_text,
)


def format_chat_request(
    prior_turns: list[dict],
    basis: dict,
    di: dict,
    latest: str,
    *,
    hosted: bool = False,
) -> str:
    """One user message that carries the form and the project's earlier chat turns.

    hosted is the text-only /heavy packet. It does not ask for desktop tools.
    """
    lines = []
    for turn in prior_turns:
        who = "Designer" if turn.get("role") == "user" else "Assistant"
        lines.append(f"{who}: {turn.get('text') or ''}")
    history = "\n\n".join(lines) if lines else "(none)"
    if hosted:
        lead = (
            "Project basis and the current zone form follow. "
            "This message is the already-computed zone packet. "
            "Reason from these figures only. "
            "Do not call read_role, read_skill, read_mode, or a calc tool. "
            "Earlier chat turns are included so a follow-up can refer to them.\n"
        )
    else:
        lead = (
            "Project basis and the current zone form follow. "
            "Use tools for any gallons, seconds, gpm, or releasing logic. "
            "Earlier chat turns are included so a follow-up can refer to them.\n"
        )
    return (
        lead
        + f"basis={basis}\nzone={di}\n\n"
        + f"Earlier turns:\n{history}\n\n"
        + f"Designer: {latest}"
    )


def chat_request_text(
    prior_turns: list[dict],
    basis: dict,
    di: dict,
    latest: str,
    last_run: dict | None = None,
    mode: str | None = None,
    bess_run: dict | None = None,
    *,
    hosted: bool = False,
) -> str:
    """Everyday-path request. A finished tool plan is repeated so chat cannot replace it.

    hosted=True is the /heavy packet: the same figures, without a request to
    call read_role, read_skill, read_mode, or a calc tool.
    """
    text = format_chat_request(prior_turns, basis, di, latest, hosted=hosted)
    slug = normalize_mode(mode)
    head = f"Active mode: {slug}."
    note = govern_note(last_run)
    explosion = bess_govern_note(bess_run)
    parts = [head, text]
    if note:
        parts.append(note)
    if explosion:
        parts.append(explosion)
    return "\n\n".join(parts)


_SLASH_ALIASES = {
    "sample_di": "sample-di",
    "sampledi": "sample-di",
    "sample_bess": "sample-bess",
    "samplebess": "sample-bess",
}

UNTITLED_JOB = "Untitled job"

# Empty-thread welcome. The first line is the title. The links under it are
# drawn by the window: an API-key link when no key is saved, and the optional
# sample zone. Neither is required before a question.
THREAD_HINT = (
    "What are we working on?\n"
    "Ask about a wet, dry, or double-interlock zone, the detection and releasing that trip it, "
    "a spec section, or a calc.\n"
    "Numbers come from the calc tools in your content pack."
)
WELCOME_KEY_LINK = "Add your Anthropic API key in Settings to start chatting →"
WELCOME_SAMPLE_LINK = "Try the sample double-interlock zone (/sample-di) →"
WELCOME_FOOTNOTE = (
    "The sample is optional. It opens its own job and runs the zone tool plan on this machine.\n"
    "Type /help for commands."
)
EXPORT_NEEDS_RUN = (
    f"Export of draft Section {DRAFT_SECTION} needs a zone run on this job first. "
    "Fill in Zone details and press Run zone (or type /run). /sample-di loads a sample zone to try it."
)
COMPOSER_PLACEHOLDER = "Ask about a zone, a releasing sequence, a spec section, or a calc…"
CANCELLED_RUN_LINE = (
    "Cancelled. The designer stopped the narration before it finished. "
    "The tool plan had already run, so its figures stand below and in the tables."
)
COMPOSER_HINT = "Enter to send  ·  Shift+Enter for a new line  ·  /help for commands"


def chat_title(text: str, limit: int = 48) -> str:
    """Job name taken from the first message: first line, trimmed at a word."""
    first = next((line.strip() for line in (text or "").splitlines() if line.strip()), "")
    first = " ".join(first.split())
    if not first:
        return UNTITLED_JOB
    if len(first) <= limit:
        return first
    cut = first[: limit - 1]
    if " " in cut[limit // 2:]:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:.-") + "…"


def sample_di_seed() -> str:
    """First lines of the Sample DI reply, so the thread says what was loaded."""
    di = sample_data.EXAMPLE_DI
    segments = len(di.get("segments") or [])
    return (
        f"Sample loaded: data-hall double-interlock zone {di.get('zone_id') or 'DH-1'} "
        f"({segments} pipe segments, {di.get('delivery_basis') or 'FM'} time basis). "
        "This is sample data, not a real building. "
        "The inputs are under Zone details. Ask follow-up questions here and they use these figures."
    )


def sample_bess_seed() -> str:
    room = sample_data.EXAMPLE_BESS
    return (
        f"Sample loaded: generic Li-ion BESS room {room.get('room_id') or 'BESS-1'}, "
        "explosion-control starter in synthesis mode. "
        "This is sample data, not a real building. Ask follow-up questions here."
    )


def parse_slash_command(text: str) -> tuple[str, str] | None:
    """Return (command, argument) when the composer text is a slash command.

    A normal question returns None and is sent to Claude. `/sample-di` and
    `/sample_di` both canonicalize to `sample-di`.
    """
    stripped = (text or "").strip()
    if len(stripped) < 2 or not stripped.startswith("/") or stripped.startswith("//"):
        return None
    parts = stripped[1:].split(maxsplit=1)
    token = parts[0].strip().lower()
    if not token or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", token):
        return None
    argument = parts[1].strip() if len(parts) > 1 else ""
    return _SLASH_ALIASES.get(token, token), argument


def slash_help_text() -> str:
    return (
        "Just type a question. These commands are optional.\n\n"
        "## Commands\n"
        "- /sample-di — load the sample data-hall double-interlock zone into its own job and run the tool plan\n"
        "- /sample-bess — load the sample Li-ion BESS room and run the explosion-control starter\n"
        "- /run — run the zone in Zone details\n"
        "- /mode — show the active mode. /mode brainstorm switches (also calculator, synthesis, mixed)\n"
        "- /new Job name — start a named job\n"
        "- /heavy task — text-only hosted reasoning on the zone packet already in the message. "
        "The reply comes back into this thread. It does not call read_role, read_skill, read_mode, "
        "or a calc tool, and it is the only path that uses the hosted runtime.\n"
        "- /help — this list\n\n"
        "## Keys and menus\n"
        "- Ctrl+S saves the open job. Closing the window saves it too. Ctrl+N starts a new chat.\n"
        "- Right-click a job in the sidebar to rename or delete it.\n"
        f"- ⋯ menu: the samples, Run zone, Export draft Section {DRAFT_SECTION} "
        "(after a run and a blind claim check in this thread), Export Design Basis and Open Questions "
        "(from this job's project record), and Settings.\n\n"
        "## Labels\n"
        "- Pipe gallons and trip time come from the calc tools. "
        "Blank trim and the screen-limit seconds stay labeled ASSUMED.\n"
        "- A designer judgment the tools did not return is use best judgment. "
        "That label is not ASSUMED and it is not a calculated figure."
    )


def describe_modes(root: Path, active: str) -> str:
    """Active mode plus the descriptions stored on each MODE.md."""
    slug = normalize_mode(active)
    lines = [
        f"Active mode: {slug}.",
        "Mode files live in the content pack as modes/<slug>/MODE.md.",
    ]
    found = list_modes(root)
    if not found:
        lines.append("This content pack has no mode files.")
    for item in found:
        mark = " (active)" if item["slug"] == slug else ""
        description = item["description"] or item["name"]
        lines.append(f"- {item['slug']}: {description}{mark}")
    lines.append("Usage: /mode brainstorm")
    return "\n".join(lines)


def unknown_slash_text(command: str) -> str:
    return f"/{command} is not a command.\n\n" + slash_help_text()


def chat_run_summary(result: dict) -> str:
    """Short thread reply for a finished zone run. Tables stay on the tool plan."""
    narrative = (result.get("narrative") or "").strip()
    tools = result.get("tools") or {}
    extras: list[str] = []
    volume = tools.get("zone_trapped_volume")
    trip = tools.get("di_trip_to_water")
    if isinstance(volume, dict):
        trim_line = trim_assumption_text(volume)
        if trim_line and trim_line not in narrative:
            extras.append(trim_line)
    if isinstance(trip, dict):
        limit_line = screen_limit_assumption_text(trip)
        if limit_line and limit_line not in narrative:
            extras.append(limit_line)
    judgment = judgment_label_line()
    if judgment not in narrative:
        extras.append(judgment)
    extras.append(f"Figures are from the tool plan. Draft export is Section {DRAFT_SECTION}.")
    return "\n\n".join(part for part in (narrative, *extras) if part)

SYSTEM_CHOICES = (
    ("Double-interlock", "di"),
    ("Dry", "dry"),
    ("Wet", "wet"),
)
HAZARDS = ("ordinary", "light", "extra")
BASES = ("FM", "NFPA-OH", "NFPA-LH", "NFPA-EH", "NFPA-HP", "NFPA-DU")
MEDIA = ("nitrogen", "air", "unelected")
PRIMES = ("nc_solenoid", "pneumatic_actuator", "unknown")
LENGTHS = (("Center to center", "center_to_center"), ("Cut lengths", "cut"))
_SAVE_KEYS = ("<Control-s>", "<Control-S>", "<Command-s>", "<Command-S>")
_NEW_KEYS = ("<Control-n>", "<Control-N>", "<Command-n>", "<Command-N>")


def _blank_to_none(text: str):
    text = text.strip()
    return None if text == "" else text


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FP/FA Design Assistant")
        self.root.geometry("1280x800+40+40")
        self.root.minsize(1020, 680)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                pass
        self.queue: queue.Queue = queue.Queue()
        self._content_check_running = False
        self._changelog_view = None
        self._settings_version = None
        self.project: dict | None = None
        self.chat_log: list[dict] = []
        self._ids: list[str] = []
        # One entry per submitted zone job. Two /run commands on one project
        # each post their own labeled result or error.
        self._announce_jobs: set[str] = set()
        # Sample runs put a short "what was loaded" note above their reply.
        self._seed_notes: dict[str, str] = {}
        self.jobs: JobInbox | None = None
        # Cached so drawing the welcome does not reread the key store.
        self._key_saved = False
        self._pending_shown = False
        self._activity_shown = False
        self._details_shown = False
        self._thread_margin = -1
        self._menu_project_id: str | None = None
        self._build()
        self.jobs = JobInbox(worker_count=2, on_change=self._on_jobs_changed)
        # The project record. Calc tools and record tools write to it by job id.
        self.record = Record()
        # Cancel flags for running jobs, by job id. Set from the Team tab.
        self._cancel_events: dict[str, threading.Event] = {}
        # Cached agent and cloud environment ids for later /heavy calls.
        # Not a session. Session cleanup does not delete these.
        self._managed_resources: dict = {}
        try:
            self._pristine_basis = self.collect_basis()
            self._pristine_di = self.collect_di()
        except ValueError:
            self._pristine_basis = None
            self._pristine_di = None
        self.refresh_projects()
        self.root.bind("<Destroy>", self._cancel_afters, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        for sequence in _SAVE_KEYS:
            self.root.bind_all(sequence, self._on_save_key)
        for sequence in _NEW_KEYS:
            self.root.bind_all(sequence, self._on_new_key)
        self.root.after(100, self._poll)
        self.root.after(600, self._maybe_check_content_on_launch)

    def _cancel_afters(self, event=None) -> None:
        if event is not None and event.widget is not self.root:
            return
        for sequence in _SAVE_KEYS + _NEW_KEYS:
            try:
                self.root.unbind_all(sequence)
            except tk.TclError:
                pass
        try:
            for after_id in list(self.root.tk.call("after", "info")):
                self.root.after_cancel(after_id)
        except tk.TclError:
            pass
        jobs = getattr(self, "jobs", None)
        if jobs is not None:
            # close() deletes a hosted session that is still polling.
            # The delete runs off this thread and is joined for a short bound.
            jobs.close()

    def _on_save_key(self, event=None):
        try:
            if event is not None and event.widget.winfo_toplevel() is not self.root:
                return
        except tk.TclError:
            return
        self.save_current()
        return "break"

    def _on_new_key(self, event=None):
        try:
            if event is not None and event.widget.winfo_toplevel() is not self.root:
                return
        except tk.TclError:
            return
        self.new_job()
        return "break"

    def _form_is_dirty(self) -> bool:
        if self.chat_log:
            return True
        if self._pristine_basis is None or self._pristine_di is None:
            return True
        try:
            return (
                self.collect_basis() != self._pristine_basis
                or self.collect_di() != self._pristine_di
            )
        except ValueError:
            return True

    def _persist_open_work(self) -> None:
        """Save an open job, or a form the designer typed before any job existed."""
        if self.project is None:
            if not self._form_is_dirty():
                return
            self._ensure_project()
        if self.project is None:
            return
        self._capture_form(self.project)
        save_project(self.project)

    def _on_close(self) -> None:
        try:
            self._persist_open_work()
        finally:
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def _build(self) -> None:
        self.theme = apply_theme(self.root)
        px = self.theme.px
        fonts = self.theme.fonts

        self.content_banner = tk.StringVar(value="")
        self.banner = tk.Label(
            self.root,
            textvariable=self.content_banner,
            justify="left",
            anchor="w",
            wraplength=px(1100),
            bg=palette.BANNER_BG,
            fg=palette.ACCENT,
            padx=px(18),
            pady=px(8),
            cursor="hand2",
        )
        # A click dismisses the update note. The pack stays installed.
        self.banner.bind("<Button-1>", lambda _event: self._set_content_banner(""))

        self.ask_claude = tk.BooleanVar(value=False)
        self.mode_slug = tk.StringVar(value=DEFAULT_MODE)
        self.details_open = tk.BooleanVar(value=False)
        self.job_title = tk.StringVar(value="New chat")
        self.status = tk.StringVar(value=key_status())
        self.content_status = tk.StringVar(value=content_status_line())

        body = tk.PanedWindow(
            self.root,
            orient="horizontal",
            sashwidth=px(3),
            sashpad=0,
            bd=0,
            relief="flat",
            bg=palette.BORDER,
            showhandle=False,
            opaqueresize=True,
        )
        body.pack(fill="both", expand=True)
        self.main_body = body

        sidebar = ttk.Frame(body, style="Surface.TFrame", padding=(px(12), px(14), px(12), px(12)))
        body.add(sidebar, minsize=px(190), width=px(250), stretch="never")
        self._build_sidebar(sidebar)

        chat = ttk.Frame(body)
        body.add(chat, minsize=px(420), stretch="always")
        self.chat_column = chat
        self._build_chat(chat)

        # Zone details is added to the paned window only while it is open.
        self.details = ttk.Frame(body, padding=(px(16), px(12), px(12), px(10)))
        self._build_details(self.details)

        self._sync_claude_default()
        self._render_chat()
        self.root.after(200, self._prefer_chat)

    def _build_sidebar(self, parent) -> None:
        px = self.theme.px
        ttk.Button(parent, text="+  New chat", style="Accent.TButton", command=self.new_job).pack(fill="x")
        ttk.Label(parent, text="JOBS", style="Section.TLabel").pack(anchor="w", pady=(px(18), px(4)))
        self.settings_button = ttk.Button(
            parent, text="Settings", style="Sidebar.TButton", command=self.open_settings
        )
        self.settings_button.pack(side="bottom", fill="x", pady=(px(8), 0))
        # Activity (the job inbox) is packed only while it has something in it.
        self.activity = ttk.Frame(parent, style="Surface.TFrame")
        ttk.Label(self.activity, text="ACTIVITY", style="Section.TLabel").pack(anchor="w", pady=(px(10), px(4)))
        self.inbox_list = tk.Listbox(
            self.activity,
            height=5,
            exportselection=False,
            activestyle="none",
            bd=0,
            highlightthickness=0,
            relief="flat",
            bg=palette.SURFACE,
            fg=palette.MUTED,
            selectbackground=palette.SURFACE,
            selectforeground=palette.MUTED,
            font=self.theme.fonts["small"],
        )
        self.inbox_list.pack(fill="x")
        # Team roster for the open job. Packed only while the job has agents.
        self.team_box = ttk.Frame(parent, style="Surface.TFrame")
        ttk.Label(self.team_box, text="TEAM", style="Section.TLabel").pack(anchor="w", pady=(px(10), px(4)))
        self.team_list = tk.Listbox(
            self.team_box,
            height=4,
            exportselection=False,
            activestyle="none",
            bd=0,
            highlightthickness=0,
            relief="flat",
            bg=palette.SURFACE,
            fg=palette.MUTED,
            selectbackground=palette.SURFACE,
            selectforeground=palette.MUTED,
            font=self.theme.fonts["small"],
        )
        self.team_list.pack(fill="x")
        self.team_list.bind("<Button-1>", lambda _event: self.show_team(), add="+")
        self._team_shown = False
        self.project_list = tk.Listbox(
            parent,
            width=24,
            exportselection=False,
            activestyle="none",
            bd=px(2),
            highlightthickness=0,
            relief="flat",
            bg=palette.SURFACE,
            fg=palette.TEXT,
            selectbackground=palette.ACCENT_SOFT,
            selectforeground=palette.ACCENT,
            font=self.theme.fonts["list"],
        )
        self.project_list.pack(fill="both", expand=True)
        self.project_list.bind("<<ListboxSelect>>", self._on_select)
        context = ("<Button-2>", "<Control-Button-1>") if sys.platform == "darwin" else ()
        for sequence in ("<Button-3>",) + context:
            self.project_list.bind(sequence, self._project_menu_popup)
        self.project_list.bind("<Delete>", lambda _event: self.delete_job())
        self.project_list.bind("<F2>", lambda _event: self.rename_job())
        self.project_menu = tk.Menu(self.project_list, tearoff=0)
        self.project_menu.add_command(label="Rename…", command=lambda: self.rename_job(self._menu_project_id))
        self.project_menu.add_command(label="Delete", command=lambda: self.delete_job(self._menu_project_id))

    def _build_chat(self, parent) -> None:
        px = self.theme.px
        fonts = self.theme.fonts

        top = ttk.Frame(parent, padding=(px(20), px(8), px(10), px(8)))
        top.pack(side="top", fill="x")
        self.more_button = ttk.Menubutton(top, text="⋯", style="Icon.TMenubutton")
        self.more_menu = tk.Menu(self.more_button, tearoff=0)
        self.more_button["menu"] = self.more_menu
        self.more_button.pack(side="right")
        self.details_toggle = ttk.Checkbutton(
            top,
            text="Zone details",
            variable=self.details_open,
            style="Toolbar.Toolbutton",
            command=lambda: self.show_details(bool(self.details_open.get())),
        )
        self.details_toggle.pack(side="right", padx=(0, px(2)))
        self.mode_button = ttk.Menubutton(top, style="Toolbar.TMenubutton")
        self.mode_menu = tk.Menu(self.mode_button, tearoff=0)
        self.mode_button["menu"] = self.mode_menu
        self.mode_button.pack(side="right", padx=(0, px(2)))
        # Packed last so a long job name is what gets shortened, not the controls.
        self._title_shown = tk.StringVar(value=self.job_title.get())
        self.title_label = ttk.Label(top, textvariable=self._title_shown, style="Job.TLabel")
        self.title_label.pack(side="left", fill="x", expand=True)
        self.title_label.bind("<Configure>", lambda _event: self._fit_title(), add="+")
        self.job_title.trace_add("write", lambda *_args: self._fit_title())
        self.mode_slug.trace_add("write", lambda *_args: self._sync_mode_label())
        self._apply_mode(DEFAULT_MODE)
        self._build_more_menu()
        ttk.Separator(parent, orient="horizontal").pack(side="top", fill="x")

        footer = ttk.Frame(parent, padding=(px(20), 0, px(14), px(6)))
        footer.pack(side="bottom", fill="x")
        ttk.Label(footer, textvariable=self.content_status, style="Footer.TLabel").pack(side="right")
        # The footer shows the short note. The full status (with the job
        # heading) stays on self.status for the inbox and the tests.
        self._status_line = tk.StringVar(value=self.status.get())
        self.status.trace_add("write", lambda *_args: self._sync_status_line())
        ttk.Label(footer, textvariable=self._status_line, style="Footer.TLabel").pack(
            side="left", fill="x", expand=True
        )

        self.composer_row = ttk.Frame(parent, padding=(px(24), px(6), px(24), px(2)))
        self.composer_row.pack(side="bottom", fill="x")
        self.composer_box = tk.Frame(
            self.composer_row,
            bg=palette.BG,
            highlightthickness=1,
            highlightbackground=palette.BORDER_STRONG,
            highlightcolor=palette.BORDER_STRONG,
            bd=0,
        )
        self.composer_box.pack(fill="x")
        self.send_button = ttk.Button(self.composer_box, text="Send", style="Accent.TButton", command=self.send_chat)
        self.send_button.pack(side="right", anchor="se", padx=px(8), pady=px(8))
        self.chat_entry = Composer(
            self.composer_box,
            on_submit=self.send_chat,
            placeholder=COMPOSER_PLACEHOLDER,
            font=fonts["chat"],
            bg=palette.BG,
            fg=palette.TEXT,
            insertbackground=palette.TEXT,
            selectbackground=palette.ACCENT_SOFT,
            padx=px(12),
            pady=px(10),
            min_lines=2,
            max_lines=8,
        )
        self.chat_entry.pack(side="left", fill="both", expand=True)
        self.chat_entry.bind("<FocusIn>", lambda _event: self._composer_focus(True), add="+")
        self.chat_entry.bind("<FocusOut>", lambda _event: self._composer_focus(False), add="+")
        ttk.Label(self.composer_row, text=COMPOSER_HINT, style="Footer.TLabel").pack(anchor="w", pady=(px(4), 0))

        thread = ttk.Frame(parent)
        thread.pack(side="top", fill="both", expand=True)
        self.chat_view = tk.Text(
            thread,
            wrap="word",
            state="disabled",
            bd=0,
            relief="flat",
            highlightthickness=0,
            bg=palette.BG,
            fg=palette.TEXT,
            font=fonts["chat"],
            padx=0,
            pady=px(10),
            spacing2=px(2),
            cursor="arrow",
            insertwidth=0,
            selectbackground=palette.ACCENT_SOFT,
            inactiveselectbackground=palette.ACCENT_SOFT,
            height=10,
        )
        scroll = ttk.Scrollbar(thread, command=self.chat_view.yview)
        self.chat_view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat_view.pack(side="left", fill="both", expand=True)
        self._thread_scrollbar = scroll
        self._configure_thread_tags()
        self.chat_view.bind("<Configure>", self._on_thread_resize, add="+")
        self.chat_view.bind("<Button-1>", lambda _event: self.chat_view.focus_set(), add="+")
        self.chat_view.bind("<Key>", self._thread_key)
        self.thread_menu = tk.Menu(self.chat_view, tearoff=0)
        self.thread_menu.add_command(label="Copy", command=self._copy_thread_selection)
        self.thread_menu.add_command(label="Select all", command=self._select_thread)
        for sequence in ("<Button-3>",) + (("<Button-2>",) if sys.platform == "darwin" else ()):
            self.chat_view.bind(sequence, self._thread_menu_popup)

    def _build_more_menu(self) -> None:
        menu = self.more_menu
        menu.add_command(label="Sample DI zone", accelerator="/sample-di", command=self.start_sample_di)
        menu.add_command(label="Sample BESS room", accelerator="/sample-bess", command=self.start_sample_bess)
        menu.add_separator()
        menu.add_command(label="Run zone from Zone details", accelerator="/run", command=self.start_zone_run)
        menu.add_command(label=f"Export draft Section {DRAFT_SECTION}…", command=self.export_docx)
        menu.add_command(label="Export Design Basis and Open Questions…", command=self.export_design_basis)
        menu.add_command(label="Team panel", command=self.show_team)
        menu.add_separator()
        menu.add_checkbutton(label="Narrate zone runs with Claude", variable=self.ask_claude)
        menu.add_separator()
        menu.add_command(label="Rename job…", command=self.rename_job)
        menu.add_command(label="Settings…", command=self.open_settings)
        menu.add_command(label="Commands", accelerator="/help", command=self._show_help)

    def _build_details(self, parent) -> None:
        px = self.theme.px
        ttk.Label(parent, text="Zone details", style="Job.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text="Optional. Chat works without it. /run and Run zone use these inputs.",
            style="Small.TLabel",
            wraplength=px(420),
            justify="left",
        ).pack(anchor="w", pady=(px(2), px(8)))
        self.assumption_text = tk.StringVar()
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True)
        self._build_basis()
        self._build_zone()
        self._build_results()
        self._build_team()
        self.tabs.select(1)

    def show_details(self, show: bool = True) -> None:
        """Open or close the Zone details drawer. The form keeps its values either way."""
        show = bool(show)
        try:
            if show and not self._details_shown:
                self.main_body.add(
                    self.details,
                    minsize=self.theme.px(360),
                    width=self.theme.px(470),
                    stretch="never",
                )
            elif not show and self._details_shown:
                self.main_body.forget(self.details)
        except tk.TclError:
            return
        self._details_shown = show
        if bool(self.details_open.get()) != show:
            self.details_open.set(show)

    def toggle_details(self) -> None:
        self.show_details(not self._details_shown)

    def _composer_focus(self, focused: bool) -> None:
        color = palette.LINK if focused else palette.BORDER_STRONG
        try:
            self.composer_box.configure(highlightbackground=color, highlightcolor=color)
        except tk.TclError:
            pass

    def _configure_thread_tags(self) -> None:
        view = self.chat_view
        fonts = self.theme.fonts
        px = self.theme.px
        # Creation order sets priority: later tags win, so margins on bullet
        # and pre override the plain body margins.
        view.tag_configure("body", font=fonts["chat"], foreground=palette.TEXT)
        view.tag_configure("who_user", font=fonts["who"], foreground=palette.MUTED, spacing1=px(18), spacing3=px(3))
        view.tag_configure("who_assistant", font=fonts["who"], foreground=palette.ACCENT, spacing1=px(18), spacing3=px(3))
        view.tag_configure("meta", font=fonts["small"], foreground=palette.MUTED, spacing3=px(4))
        view.tag_configure("heading", font=fonts["heading"], spacing1=px(10), spacing3=px(2))
        view.tag_configure("bullet")
        view.tag_configure("bullet2")
        # Margin colors keep a shaded block inside the text column.
        view.tag_configure(
            "pre", font=fonts["mono"], background=palette.CODE_BG,
            lmargincolor=palette.BG, rmargincolor=palette.BG,
        )
        view.tag_configure("pre_head", font=fonts["mono_bold"])
        view.tag_configure("rule", foreground=palette.BORDER_STRONG)
        view.tag_configure("bold", font=fonts["chat_bold"])
        view.tag_configure("code", font=fonts["mono"], background=palette.CODE_BG)
        view.tag_configure("pending", font=fonts["italic"], foreground=palette.MUTED, spacing1=px(16))
        view.tag_configure(
            "welcome_title", font=fonts["title"], foreground=palette.TEXT, justify="center",
            spacing1=px(110), spacing3=px(10),
        )
        view.tag_configure("welcome_sub", font=fonts["subtitle"], foreground=palette.MUTED, justify="center", spacing3=px(2))
        view.tag_configure("welcome_link", font=fonts["chat"], foreground=palette.LINK, justify="center", spacing1=px(22))
        view.tag_configure(
            "welcome_hint", font=fonts["small"], foreground=palette.MUTED, justify="center",
            spacing1=px(16), spacing3=px(2),
        )
        view.tag_configure("link_sample_di", underline=True)
        view.tag_configure("link_settings", underline=True)
        view.tag_bind("link_sample_di", "<Button-1>", lambda _event: self._follow_link(self.start_sample_di))
        view.tag_bind("link_settings", "<Button-1>", lambda _event: self._follow_link(self.open_settings))
        for tag in ("link_sample_di", "link_settings"):
            view.tag_bind(tag, "<Enter>", lambda _event: view.configure(cursor="hand2"))
            view.tag_bind(tag, "<Leave>", lambda _event: view.configure(cursor="arrow"))
        self._layout_thread(max(view.winfo_width(), px(900)))

    def _layout_thread(self, width: int) -> None:
        """Keep the thread in a readable centered column and line the composer up with it."""
        px = self.theme.px
        column = min(max(width - 2 * px(28), px(240)), px(780))
        margin = max(px(28), (width - column) // 2)
        if margin == self._thread_margin:
            return
        self._thread_margin = margin
        view = self.chat_view
        for tag in ("body", "who_user", "who_assistant", "meta", "heading", "pending",
                    "welcome_title", "welcome_sub", "welcome_link", "welcome_hint"):
            view.tag_configure(tag, lmargin1=margin, lmargin2=margin, rmargin=margin)
        view.tag_configure("bullet", lmargin1=margin + px(6), lmargin2=margin + px(22), rmargin=margin)
        view.tag_configure("bullet2", lmargin1=margin + px(26), lmargin2=margin + px(42), rmargin=margin)
        view.tag_configure("pre", lmargin1=margin + px(8), lmargin2=margin + px(8), rmargin=margin)
        try:
            bar = self._thread_scrollbar.winfo_width() if self._thread_scrollbar.winfo_ismapped() else 0
            self.composer_row.configure(padding=(margin, px(6), margin + bar, px(2)))
        except (tk.TclError, AttributeError):
            pass

    def _on_thread_resize(self, event) -> None:
        self._layout_thread(event.width)

    def _follow_link(self, action) -> str:
        # The link's own text is redrawn by the action, so run it after this click.
        self.root.after_idle(action)
        return "break"

    def _thread_key(self, event):
        """Typing while the thread has focus goes to the composer. Ctrl+C still copies."""
        # Control is 0x4 everywhere. Alt is 0x20000 on Windows (where 0x8 is NumLock) and 0x8 on X11.
        alt = 0x20000 if sys.platform == "win32" else 0x0008
        if event.state & (0x0004 | alt):
            return None
        if event.char and event.char.isprintable():
            self.chat_entry.focus_set()
            self.chat_entry.insert("insert", event.char)
            return "break"
        return None

    def _thread_menu_popup(self, event) -> str:
        try:
            self.thread_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.thread_menu.grab_release()
        return "break"

    def _copy_thread_selection(self) -> None:
        try:
            text = self.chat_view.get("sel.first", "sel.last")
        except tk.TclError:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def _select_thread(self) -> None:
        self.chat_view.tag_add("sel", "1.0", "end-1c")

    def _show_help(self) -> None:
        self._local_exchange("/help", slash_help_text())

    def _fit_title(self) -> None:
        """Show the job name, cut with an ellipsis when the top bar is narrow."""
        try:
            full = self.job_title.get()
            width = self.title_label.winfo_width()
            font = self.theme.fonts["job"]
        except (tk.TclError, AttributeError):
            return
        shown = full
        if width > 1 and font.measure(full) > width - self.theme.px(8):
            room = width - self.theme.px(8) - font.measure("…")
            cut = full
            while cut and font.measure(cut) > room:
                cut = cut[:-1]
            shown = cut.rstrip() + "…" if cut else ""
        if self._title_shown.get() != shown:
            self._title_shown.set(shown)

    def _sync_status_line(self) -> None:
        lines = [line.strip() for line in (self.status.get() or "").splitlines() if line.strip()]
        kept = [line for line in lines if not is_job_heading(line)] or lines
        text = " ".join(kept)
        if len(text) > 160:
            text = text[:157] + "…"
        try:
            self._status_line.set(text)
        except tk.TclError:
            pass

    def _sync_mode_label(self) -> None:
        try:
            self.mode_button.configure(text=f"Mode: {self.mode_slug.get() or DEFAULT_MODE}")
        except (tk.TclError, AttributeError):
            pass

    def _labeled(self, parent, text, variable, width=18, row=0, column=0):
        px = self.theme.px
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=(px(2), px(6)), pady=px(3))
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, px(10)), pady=px(3))
        return entry

    def _refresh_assumptions(self) -> None:
        trim = self.trim_gal.get()
        basis = self.delivery_basis.get() or "FM"
        try:
            lines = form_assumption_lines(trim, basis, content_root())
        except Exception as exc:
            if str(trim).strip():
                trim_line = f"Trim: {str(trim).strip()} gal entered on the form. Not assumed."
            else:
                trim_line = "Trim: ASSUMED 5 gal when Trim gal is blank (no valve data sheet). Not calculated."
            lines = [
                trim_line,
                "Screen limit: ASSUMED from the time basis lookup, not calculated. " + safe_error(exc),
                judgment_label_line(),
            ]
        self.assumption_text.set("\n".join(lines))

    def _combo(self, parent, text, variable, values, row, column, width=18):
        px = self.theme.px
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=(px(2), px(6)), pady=px(3))
        box = ttk.Combobox(parent, textvariable=variable, values=values, width=width, state="readonly")
        box.grid(row=row, column=column + 1, sticky="ew", padx=(0, px(10)), pady=px(3))
        return box

    def _build_basis(self) -> None:
        px = self.theme.px
        tab = ttk.Frame(self.tabs, padding=px(12))
        self.tabs.add(tab, text="Basis")
        self.ahj = tk.StringVar()
        self.nfpa_13 = tk.StringVar(value="2025")
        self.nfpa_72 = tk.StringVar(value="2025")
        self.insurer = tk.StringVar(value="FM")
        self._labeled(tab, "AHJ", self.ahj, width=28, row=0, column=0)
        self._labeled(tab, "NFPA 13 edition", self.nfpa_13, width=10, row=1, column=0)
        self._labeled(tab, "NFPA 72 edition", self.nfpa_72, width=10, row=2, column=0)
        self._labeled(tab, "Insurer", self.insurer, width=10, row=3, column=0)
        ttk.Label(tab, text="Hazard notes").grid(row=4, column=0, sticky="nw", padx=(px(2), px(6)), pady=px(3))
        self.hazard_notes = tk.Text(
            tab,
            height=8,
            wrap="word",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=palette.BORDER_STRONG,
            highlightcolor=palette.ACCENT,
            padx=px(6),
            pady=px(4),
            font=self.theme.fonts["list"],
        )
        self.hazard_notes.grid(row=4, column=1, sticky="nsew", padx=(0, px(10)), pady=px(3))
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(4, weight=1)
        ttk.Label(
            tab,
            text=(
                "Scope: wet, dry, and double-interlock preaction, plus the detection "
                "and releasing that trip them."
            ),
            style="Small.TLabel",
            wraplength=px(400),
            justify="left",
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(px(8), 0))

    def _build_zone(self) -> None:
        px = self.theme.px
        scroller = ScrollFrame(self.tabs)
        self.tabs.add(scroller, text="Zone")
        tab = scroller.inner
        tab.configure(padding=(px(10), px(10), px(4), px(10)))
        ttk.Label(
            tab,
            textvariable=self.assumption_text,
            style="Small.TLabel",
            wraplength=px(400),
            justify="left",
        ).pack(anchor="w", pady=(0, px(8)))
        form = ttk.Frame(tab)
        form.pack(fill="x")
        for column in (1, 3):
            form.columnconfigure(column, weight=1)
        self.zone_id = tk.StringVar()
        self.system_label = tk.StringVar(value="Double-interlock")
        self.hazard = tk.StringVar(value="ordinary")
        self.supervised = tk.BooleanVar(value=True)
        self.density = tk.StringVar(value="0.20")
        self.base_area = tk.StringVar(value="1500")
        self.area_increase = tk.StringVar(value="0.30")
        self.hose = tk.StringVar(value="250")
        self.q_fill = tk.StringVar(value="600")
        self.t_detect = tk.StringVar(value="0")
        self.t_release = tk.StringVar(value="0")
        self.t_exhaust = tk.StringVar(value="0")
        self.qod = tk.BooleanVar(value=False)
        self.delivery_basis = tk.StringVar(value="FM")
        self.medium = tk.StringVar(value="nitrogen")
        self.prime = tk.StringVar(value="nc_solenoid")
        self.failsafe = tk.BooleanVar(value=False)
        self.supervisory_psi = tk.StringVar(value="15")
        self.manual_station = tk.BooleanVar(value=True)
        self.length_label = tk.StringVar(value="Center to center")
        self.fittings = tk.StringVar()
        self.trim_gal = tk.StringVar()
        self.supervisory_psig = tk.StringVar(value="40")
        self.fill_minutes = tk.StringVar(value="30")

        self._labeled(form, "Zone", self.zone_id, width=10, row=0, column=0)
        self._combo(form, "System", self.system_label, [label for label, _ in SYSTEM_CHOICES], 0, 2, width=14)
        self._combo(form, "Hazard", self.hazard, HAZARDS, 1, 0, width=10)
        self._combo(form, "Time basis", self.delivery_basis, BASES, 1, 2, width=10)
        self._labeled(form, "Density", self.density, width=8, row=2, column=0)
        self._labeled(form, "Base area ft²", self.base_area, width=8, row=2, column=2)
        self._labeled(form, "Area increase", self.area_increase, width=8, row=3, column=0)
        self._labeled(form, "Hose gpm", self.hose, width=8, row=3, column=2)
        self._labeled(form, "Fill gpm", self.q_fill, width=8, row=4, column=0)
        self._labeled(form, "Trim gal", self.trim_gal, width=8, row=4, column=2)
        self._labeled(form, "t detect s", self.t_detect, width=8, row=5, column=0)
        self._labeled(form, "t release s", self.t_release, width=8, row=5, column=2)
        self._labeled(form, "t exhaust s", self.t_exhaust, width=8, row=6, column=0)
        self._labeled(form, "Fittings %", self.fittings, width=8, row=6, column=2)
        self._combo(form, "Medium", self.medium, MEDIA, 7, 0, width=10)
        self._combo(form, "Prime held by", self.prime, PRIMES, 7, 2, width=14)
        self._labeled(form, "Low-air psi", self.supervisory_psi, width=8, row=8, column=0)
        self._labeled(form, "Supervisory psig", self.supervisory_psig, width=8, row=8, column=2)
        self._combo(form, "Lengths", self.length_label, [label for label, _ in LENGTHS], 9, 0, width=14)
        self._labeled(form, "Fill minutes", self.fill_minutes, width=8, row=9, column=2)
        self.trim_gal.trace_add("write", lambda *_args: self._refresh_assumptions())
        self.delivery_basis.trace_add("write", lambda *_args: self._refresh_assumptions())
        self._refresh_assumptions()
        checks = ttk.Frame(form)
        checks.grid(row=10, column=0, columnspan=4, sticky="w", pady=(px(6), 0))
        ttk.Checkbutton(checks, text="Supervised waterflow", variable=self.supervised).grid(row=0, column=0, sticky="w", padx=(0, px(14)), pady=px(2))
        ttk.Checkbutton(checks, text="Quick-opening device", variable=self.qod).grid(row=0, column=1, sticky="w", pady=px(2))
        ttk.Checkbutton(checks, text="Manual station", variable=self.manual_station).grid(row=1, column=0, sticky="w", padx=(0, px(14)), pady=px(2))
        ttk.Checkbutton(checks, text="Failsafe on total power loss", variable=self.failsafe).grid(row=1, column=1, sticky="w", pady=px(2))

        pipes = ttk.LabelFrame(tab, text="PIPE SEGMENTS", padding=px(8))
        pipes.pack(fill="x", pady=(px(12), 0))
        columns = ("role", "nps", "schedule", "length_ft", "d_in")
        self.pipes = ttk.Treeview(pipes, columns=columns, show="headings", height=6)
        headings = {
            "role": "Role",
            "nps": "NPS",
            "schedule": "Schedule",
            "length_ft": "Length ft",
            "d_in": "ID in",
        }
        widths = {"role": 70, "nps": 50, "schedule": 72, "length_ft": 72, "d_in": 60}
        for key, title in headings.items():
            self.pipes.heading(key, text=title)
            self.pipes.column(key, width=px(widths[key]), minwidth=px(44), anchor="w", stretch=True)
        self.pipes.pack(fill="x")
        add = ttk.Frame(pipes)
        add.pack(fill="x", pady=(px(8), 0))
        self.seg_role = tk.StringVar(value="branch")
        self.seg_nps = tk.StringVar()
        self.seg_schedule = tk.StringVar()
        self.seg_length = tk.StringVar()
        for column, title in enumerate(("Role", "NPS", "Schedule", "Length ft")):
            ttk.Label(add, text=title, style="Small.TLabel").grid(row=0, column=column, sticky="w", padx=(0, px(6)))
            add.columnconfigure(column, weight=1)
        ttk.Combobox(
            add, textvariable=self.seg_role, width=8, state="readonly",
            values=("branch", "drop", "cross", "main", "feed", "riser"),
        ).grid(row=1, column=0, sticky="ew", padx=(0, px(6)))
        ttk.Entry(add, textvariable=self.seg_nps, width=6).grid(row=1, column=1, sticky="ew", padx=(0, px(6)))
        ttk.Entry(add, textvariable=self.seg_schedule, width=7).grid(row=1, column=2, sticky="ew", padx=(0, px(6)))
        ttk.Entry(add, textvariable=self.seg_length, width=7).grid(row=1, column=3, sticky="ew")
        buttons = ttk.Frame(pipes)
        buttons.pack(fill="x", pady=(px(8), 0))
        ttk.Button(buttons, text="Add segment", command=self.add_segment).pack(side="left")
        ttk.Button(buttons, text="Remove", command=self.remove_segment).pack(side="left", padx=px(6))
        ttk.Label(
            pipes,
            text=(
                "Blank schedule uses the shop default (branch and under 2 in = sch 40, mains and cross "
                "2 in and up = sch 10). The ID comes from the calc pack. Blank fittings follow the length "
                "basis. Blank trim is ASSUMED 5 gal (no valve data sheet), not calculated."
            ),
            style="Small.TLabel",
            wraplength=px(400),
            justify="left",
        ).pack(anchor="w", pady=(px(8), 0))
        ttk.Button(tab, text="Run zone", style="Accent.TButton", command=self.start_zone_run).pack(
            anchor="e", pady=(px(12), px(4))
        )

    def _build_results(self) -> None:
        px = self.theme.px
        tab = ttk.Frame(self.tabs, padding=px(10))
        self.tabs.add(tab, text="Results")
        ttk.Label(
            tab,
            text=(
                "Tool-plan figures for export. Pipe gallons and t_total are calculated. "
                "Blank trim and the screen-limit seconds are marked ASSUMED. "
                "A delivery time here is an optimistic screen, not a listed water-delivery-time calculation."
            ),
            style="Small.TLabel",
            wraplength=px(400),
            justify="left",
        ).pack(anchor="w", pady=(0, px(6)))
        self.results = tk.Text(
            tab,
            wrap="word",
            bd=0,
            relief="flat",
            highlightthickness=0,
            bg=palette.SURFACE,
            fg=palette.TEXT,
            padx=px(10),
            pady=px(8),
            font=self.theme.fonts["mono"],
        )
        scroll = ttk.Scrollbar(tab, command=self.results.yview)
        self.results.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.results.pack(fill="both", expand=True)

    def _build_team(self) -> None:
        self.team_panel = TeamPanel(
            self.tabs,
            self.theme,
            on_cancel=self.cancel_running_jobs,
            on_check=self.start_record_check,
            on_export=self.export_design_basis,
        )
        self.tabs.add(self.team_panel, text="Team")
        self.team_panel.render(None)

    def show_team(self) -> None:
        """Open the drawer on the Team tab."""
        self.show_details(True)
        try:
            self.tabs.select(self.team_panel)
        except tk.TclError:
            return
        self._refresh_team()

    def _project_running(self, project_id: str | None) -> bool:
        if not project_id:
            return False
        return any(
            job.project_id == project_id and job.status in ("queued", "running")
            for job in self.jobs.snapshot()
        )

    def _refresh_team(self) -> None:
        """Redraw the Team tab and the sidebar roster from the record. Cheap; called after every job."""
        panel = getattr(self, "team_panel", None)
        if panel is None:
            return
        project_id = (self.project or {}).get("id") if self.project else None
        snapshot = None
        if project_id:
            try:
                snapshot = self.record.snapshot(project_id)
            except Exception as exc:
                self.status.set("Project record is not available. " + safe_error(exc))
                snapshot = None
        try:
            panel.render(snapshot, running=self._project_running(project_id))
            from fpfa.team_panel import roster_lines

            lines = roster_lines(snapshot)
            self._show_team_box(bool(lines))
            if tuple(self.team_list.get(0, "end")) != tuple(lines):
                self.team_list.delete(0, "end")
                for line in lines:
                    self.team_list.insert("end", line)
        except tk.TclError:
            return

    def _show_team_box(self, show: bool) -> None:
        if show == self._team_shown:
            return
        try:
            if show:
                before = self.activity if self._activity_shown else self.project_list
                self.team_box.pack(side="bottom", fill="x", before=before)
            else:
                self.team_box.pack_forget()
        except tk.TclError:
            return
        self._team_shown = show

    def cancel_running_jobs(self) -> None:
        """Ask every queued or running job on the open job to stop at its next model round."""
        if not self.project:
            return
        project_id = self.project["id"]
        flagged = 0
        for job in self.jobs.snapshot():
            if job.project_id == project_id and job.status in ("queued", "running"):
                event = self._cancel_events.setdefault(job.id, threading.Event())
                event.set()
                flagged += 1
        if flagged:
            self.status.set(
                f"Cancel requested for {flagged} job{'s' if flagged != 1 else ''}. "
                "A turn stops before its next model round; a tool already running finishes."
            )
        else:
            self.status.set("No job is running on this project.")

    def _cancel_event(self, job_id: str) -> threading.Event:
        return self._cancel_events.setdefault(job_id, threading.Event())

    def start_record_check(self) -> None:
        """Run the blind checker over this job's findings as a claim job, without a chat turn."""
        self._keep_composer_open()
        if not self.project:
            messagebox.showinfo("Blind check", "Open a job first.")
            return
        self._open_record(self.project)
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        if not self.record.findings(origin_id):
            self._local_exchange("Run blind check", "The record has no findings to check yet.")
            self._refresh_team()
            return
        key = load_api_key()
        if not key:
            self._local_exchange("Run blind check", "Save an Anthropic API key in Settings before running the blind check.")
            return

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)
            try:
                if cancel.is_set():
                    # Cancelled while it waited in the queue. No model call, no verdicts written.
                    text = "Cancelled before the blind check started. No model call was made."
                    self.jobs.mark(job_id, "cancelled", text)
                else:
                    outcome = check_record(content_root(), self.record, origin_id, AnthropicMessages(key).create)
                    text = outcome.get("status_line") or "Blind check ran."
                    if outcome.get("verdict"):
                        text += "\n" + outcome["verdict"]
            except Exception as exc:
                text = safe_error(exc)
                self.jobs.mark(job_id, "error", text)
            finally:
                self._cancel_events.pop(job_id, None)
            self.queue.put(lambda oid=origin_id, body=text, jid=job_id: self._finish_chat(oid, body, job_id=jid))

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="claim",
            title="Blind check of the record",
            work=work,
        )
        self.status.set(f"Blind check… {job.heading()}")

    def _prefer_chat(self) -> None:
        """Put the cursor in the composer. The thread is the main surface."""
        try:
            self.chat_entry.focus_set()
        except tk.TclError:
            pass

    def _poll(self) -> None:
        try:
            while True:
                try:
                    callback = self.queue.get_nowait()
                except queue.Empty:
                    break
                try:
                    callback()
                except Exception as exc:
                    self.status.set("Update failed. " + safe_error(exc))
        finally:
            try:
                self.root.after(100, self._poll)
            except tk.TclError:
                pass

    def _on_jobs_changed(self) -> None:
        """Refresh the inbox. Worker threads only enqueue the refresh."""
        if threading.current_thread() is threading.main_thread():
            self._refresh_inbox()
            return
        self.queue.put(self._refresh_inbox)

    def _refresh_inbox(self) -> None:
        jobs = getattr(self, "jobs", None)
        listing = getattr(self, "inbox_list", None)
        if jobs is None or listing is None:
            return
        try:
            if self._pending_here() != self._pending_shown:
                self._render_chat()
            panel = getattr(self, "team_panel", None)
            if panel is not None:
                panel.cancel_button.configure(
                    state="normal" if self._project_running((self.project or {}).get("id")) else "disabled"
                )
            lines = [job.inbox_line() for job in jobs.snapshot()]
            self._show_activity(bool(lines))
            if tuple(listing.get(0, "end")) == tuple(lines):
                return
            listing.delete(0, "end")
            for line in lines:
                listing.insert("end", line)
            if lines:
                listing.see("end")
        except tk.TclError:
            return

    def _show_activity(self, show: bool) -> None:
        """The sidebar Activity list appears once there is a job to show."""
        if show == self._activity_shown:
            return
        try:
            if show:
                self.activity.pack(side="bottom", fill="x", before=self.project_list)
            else:
                self.activity.pack_forget()
        except tk.TclError:
            return
        self._activity_shown = show

    def _pending_here(self) -> bool:
        """True while a job for the open project is queued or running."""
        jobs = getattr(self, "jobs", None)
        if jobs is None or not self.project:
            return False
        project_id = self.project.get("id")
        return any(
            job.project_id == project_id and job.status in ("queued", "running")
            for job in jobs.snapshot()
        )

    def _keep_composer_open(self) -> None:
        """A running job must leave the composer usable."""
        try:
            self.chat_entry.configure(state="normal")
            self.send_button.configure(state="normal")
        except tk.TclError:
            return

    def _job_record(self, job_id: str | None):
        if not job_id or self.jobs is None:
            return None
        return self.jobs.get(job_id)

    def _destination_id(self, origin_id: str, job_id: str | None) -> str:
        """The job's project wins so a result cannot land on a different one."""
        job = self._job_record(job_id)
        if job is not None and job.project_id:
            return job.project_id
        return origin_id

    def _with_job_label(self, job_id: str | None, body: str) -> str:
        job = self._job_record(job_id)
        if job is None:
            return body
        return label_result(job.heading(), body)

    def _stamp_job(self, result: dict | None, job_id: str | None) -> dict | None:
        if not isinstance(result, dict):
            return result
        job = self._job_record(job_id)
        if job is None:
            return result
        stamped = dict(result)
        stamped["job_heading"] = job.heading()
        stamped["job_id"] = job.id
        return stamped

    def _assistant_turn(self, text: str, job_id: str | None) -> dict:
        turn = {"role": "assistant", "text": text}
        if job_id:
            turn["job_id"] = job_id
        return turn

    def _sync_claude_default(self) -> None:
        self._key_saved = bool(load_api_key())
        self.ask_claude.set(self._key_saved)

    def _update_title(self) -> None:
        name = (self.project or {}).get("name") if self.project else None
        try:
            self.job_title.set(name or "New chat")
        except (tk.TclError, AttributeError):
            pass

    def refresh_projects(self, select_id: str | None = None) -> None:
        self.project_list.delete(0, "end")
        self._ids = []
        for row in list_projects():
            self.project_list.insert("end", row.get("name") or UNTITLED_JOB)
            self._ids.append(row["id"])
        if select_id and select_id in self._ids:
            index = self._ids.index(select_id)
            self.project_list.selection_set(index)
            self.project_list.see(index)
        self._update_title()

    def _selected_id(self) -> str | None:
        selection = self.project_list.curselection()
        if not selection:
            return None
        return self._ids[selection[0]]

    def _on_select(self, _event=None) -> None:
        project_id = self._selected_id()
        if not project_id:
            return
        if self.project and self.project.get("id") == project_id:
            return
        if self.project:
            self._capture_form(self.project)
            save_project(self.project)
        self.open_project(project_id)

    def open_project(self, project_id: str) -> None:
        self.project = load_project(project_id)
        self._apply_project(self.project)
        self.status.set(f"Opened {self.project.get('name')}. {key_status()}")

    def _apply_project(self, project: dict) -> None:
        basis = project.get("basis") or {}
        self.ahj.set(basis.get("ahj") or "")
        self.nfpa_13.set(basis.get("nfpa_13") or "2025")
        self.nfpa_72.set(basis.get("nfpa_72") or "2025")
        self.insurer.set(basis.get("insurer") or "FM")
        self.hazard_notes.delete("1.0", "end")
        self.hazard_notes.insert("1.0", basis.get("hazard_notes") or "")
        self._apply_di(project.get("di") or {})
        self.chat_log = list(project.get("chat") or [])
        self._render_chat()
        self._show_saved_run(project.get("last_run") or project.get("bess_run"))
        self._apply_mode(project.get("mode"))
        self._open_record(project)
        self._refresh_team()

    def _open_record(self, project: dict | None) -> None:
        """Make sure the job is in the project record. An older JSON job is imported once."""
        if not project or not project.get("id"):
            return
        try:
            self.record.import_project(project)
            # Form-owned basis fields follow the form. A changed value supersedes the old row.
            self.record.sync_basis(project["id"], project.get("basis"))
        except Exception as exc:
            self.status.set("Project record is not available. " + safe_error(exc))

    def _known_modes(self) -> list[str]:
        try:
            found = [item["slug"] for item in list_modes(content_root())]
        except FileNotFoundError:
            found = []
        return found or list(MODE_SLUGS)

    def _apply_mode(self, slug: str | None) -> None:
        known = self._known_modes()
        self.mode_menu.delete(0, "end")
        for item in known:
            self.mode_menu.add_radiobutton(label=item.capitalize(), value=item, variable=self.mode_slug)
        chosen = normalize_mode(slug)
        if chosen not in known:
            chosen = DEFAULT_MODE if DEFAULT_MODE in known else known[0]
        self.mode_slug.set(chosen)
        self._sync_mode_label()

    def mode_choices(self) -> list[str]:
        """Mode slugs listed on the Mode menu."""
        last = self.mode_menu.index("end")
        if last is None:
            return []
        return [str(self.mode_menu.entrycget(index, "value")) for index in range(last + 1)]

    def _apply_di(self, di: dict) -> None:
        self.zone_id.set(di.get("zone_id") or "")
        code = di.get("system_type") or "di"
        label = next((name for name, value in SYSTEM_CHOICES if value == code), "Double-interlock")
        self.system_label.set(label)
        self.hazard.set(di.get("hazard") or "ordinary")
        self.supervised.set(bool(di.get("supervised", True)))
        self.density.set("" if di.get("density_gpm_ft2") is None else str(di.get("density_gpm_ft2")))
        self.base_area.set("" if di.get("base_area_ft2") is None else str(di.get("base_area_ft2")))
        self.area_increase.set("" if di.get("area_increase") is None else str(di.get("area_increase")))
        self.hose.set("" if di.get("hose_gpm") is None else str(di.get("hose_gpm")))
        self.q_fill.set("" if di.get("q_fill_gpm") is None else str(di.get("q_fill_gpm")))
        self.t_detect.set(str(di.get("t_detect_s") if di.get("t_detect_s") is not None else 0))
        self.t_release.set(str(di.get("t_release_s") if di.get("t_release_s") is not None else 0))
        self.t_exhaust.set(str(di.get("t_exhaust_s") if di.get("t_exhaust_s") is not None else 0))
        self.qod.set(bool(di.get("qod")))
        self.delivery_basis.set(di.get("delivery_basis") or "FM")
        self.medium.set(di.get("medium") or "nitrogen")
        self.prime.set(di.get("prime_held_by") or "nc_solenoid")
        self.failsafe.set(bool(di.get("failsafe_on_total_power_loss")))
        self.supervisory_psi.set("" if di.get("supervisory_psi") is None else str(di.get("supervisory_psi")))
        self.manual_station.set(bool(di.get("manual_station", True)))
        length_code = di.get("length_basis") or "center_to_center"
        self.length_label.set(next((name for name, value in LENGTHS if value == length_code), "Center to center"))
        self.fittings.set("" if di.get("fittings_percent") is None else str(di.get("fittings_percent")))
        self.trim_gal.set("" if di.get("trim_gal") is None else str(di.get("trim_gal")))
        self.supervisory_psig.set(str(di.get("supervisory_psig") if di.get("supervisory_psig") is not None else 40))
        self.fill_minutes.set(str(di.get("fill_minutes") if di.get("fill_minutes") is not None else 30))
        self.pipes.delete(*self.pipes.get_children())
        for segment in di.get("segments") or []:
            self._insert_segment(segment)

    def _insert_segment(self, segment: dict) -> None:
        d_in = segment.get("d_in")
        schedule = segment.get("schedule") or ""
        nps = "" if segment.get("nps") is None else segment.get("nps")
        if d_in in (None, "") and nps != "":
            try:
                resolved = ToolSession(content_root()).execute("resolve_pipe_id", {
                    "nps": nps,
                    "schedule": schedule,
                    "role": segment.get("role") or "",
                })
                d_in = resolved.get("d_in")
                schedule = resolved.get("schedule") or schedule
                nps = resolved.get("nps") or nps
            except Exception:
                d_in = ""
        shown = "" if d_in in (None, "") else f"{float(d_in):.3f}"
        self.pipes.insert("", "end", values=(
            segment.get("role") or "",
            nps,
            schedule,
            segment.get("length_ft") if segment.get("length_ft") is not None else "",
            shown,
        ))

    def collect_basis(self) -> dict:
        return {
            "ahj": self.ahj.get().strip(),
            "nfpa_13": self.nfpa_13.get().strip() or "2025",
            "nfpa_72": self.nfpa_72.get().strip() or "2025",
            "insurer": self.insurer.get().strip() or "FM",
            "hazard_notes": self.hazard_notes.get("1.0", "end").strip(),
        }

    def collect_di(self) -> dict:
        code = next((value for name, value in SYSTEM_CHOICES if name == self.system_label.get()), "di")
        segments = []
        for item in self.pipes.get_children():
            role, nps, schedule, length, d_in = self.pipes.item(item, "values")
            segment = {
                "role": role,
                "nps": nps,
                "schedule": schedule,
                "length_ft": float(length) if str(length).strip() else None,
            }
            if str(d_in).strip():
                segment["d_in"] = float(d_in)
            segments.append(segment)

        def num(value: str):
            value = value.strip()
            return None if value == "" else float(value)

        return {
            "zone_id": self.zone_id.get().strip(),
            "system_type": code,
            "hazard": self.hazard.get(),
            "supervised": bool(self.supervised.get()),
            "density_gpm_ft2": num(self.density.get()),
            "base_area_ft2": num(self.base_area.get()),
            "area_increase": num(self.area_increase.get()) or 0,
            "hose_gpm": num(self.hose.get()) or 0,
            "q_fill_gpm": num(self.q_fill.get()),
            "t_detect_s": num(self.t_detect.get()) or 0,
            "t_release_s": num(self.t_release.get()) or 0,
            "t_exhaust_s": num(self.t_exhaust.get()) or 0,
            "qod": bool(self.qod.get()),
            "delivery_basis": self.delivery_basis.get() or "FM",
            "medium": self.medium.get(),
            "prime_held_by": self.prime.get(),
            "failsafe_on_total_power_loss": bool(self.failsafe.get()),
            "supervisory_psi": _blank_to_none(self.supervisory_psi.get()),
            "manual_station": bool(self.manual_station.get()),
            "length_basis": next(
                (value for name, value in LENGTHS if name == self.length_label.get()),
                "center_to_center",
            ),
            "fittings_percent": _blank_to_none(self.fittings.get()),
            "trim_gal": _blank_to_none(self.trim_gal.get()),
            "supervisory_psig": num(self.supervisory_psig.get()) or 40,
            "fill_minutes": num(self.fill_minutes.get()) or 30,
            "segments": segments,
        }

    def _selected_mode(self) -> str:
        return self.mode_slug.get() or DEFAULT_MODE

    def _write_form(self, project: dict) -> None:
        # Selected mode is stored even when a later numeric field is invalid.
        project["mode"] = self._selected_mode()
        project["basis"] = self.collect_basis()
        project["di"] = self.collect_di()
        project["chat"] = self.chat_log

    def _capture_form(self, project: dict) -> str | None:
        """Copy the widgets onto project. A bad number does not drop the chat or the mode."""
        project["mode"] = self._selected_mode()
        try:
            self._write_form(project)
        except ValueError as exc:
            project["chat"] = self.chat_log
            project["mode"] = self._selected_mode()
            return str(exc)
        return None

    def _save_form_or_chat(self, project: dict) -> str | None:
        """Write the form onto the project. A bad number does not drop the chat or the run."""
        return self._capture_form(project)

    def save_current(self) -> None:
        self._ensure_project()
        if not self.project:
            return
        error = self._capture_form(self.project)
        save_project(self.project)
        self.refresh_projects(self.project["id"])
        self._open_record(self.project)
        if error:
            messagebox.showerror("Save", error)
            self.status.set(error)
            return
        self.status.set(f"Saved {self.project['name']}.")

    def _start_named_job(self, name: str) -> None:
        """Open a new job. A form with no project yet stays. An open project is saved and left behind."""
        if self.project:
            self._capture_form(self.project)
            save_project(self.project)
            project = new_project(name)
            project["mode"] = self._selected_mode()
            save_project(project)
            self.refresh_projects(project["id"])
            self.open_project(project["id"])
            return
        project = new_project(name)
        self._capture_form(project)
        save_project(project)
        self.project = project
        self.refresh_projects(project["id"])
        self.status.set(f"Opened {project.get('name')}. {key_status()}")

    def _is_blank_job(self, project: dict | None) -> bool:
        if not project:
            return False
        return (
            (project.get("name") or UNTITLED_JOB) == UNTITLED_JOB
            and not self.chat_log
            and not project.get("last_run")
            and not project.get("bess_run")
        )

    def new_job(self) -> None:
        """Start an empty chat. It takes its name from the first question."""
        if not self._is_blank_job(self.project):
            self._start_named_job(UNTITLED_JOB)
            self.chat_log = list((self.project or {}).get("chat") or [])
            self._render_chat()
            self._refresh_team()
        try:
            self.chat_entry.focus_set()
        except tk.TclError:
            pass

    def rename_job(self, project_id: str | None = None) -> None:
        project_id = project_id or (self.project or {}).get("id") or self._selected_id()
        if not project_id:
            self.status.set("Start a chat first. A job is created with the first message.")
            return
        is_open = self.project is not None and self.project.get("id") == project_id
        try:
            target = self.project if is_open else load_project(project_id)
        except (OSError, json.JSONDecodeError):
            return
        name = simpledialog.askstring(
            "Rename job",
            "Job name",
            initialvalue=target.get("name") or UNTITLED_JOB,
            parent=self.root,
        )
        if not name or not name.strip():
            return
        target["name"] = " ".join(name.split())
        if is_open:
            self._capture_form(target)
        save_project(target)
        self.refresh_projects((self.project or {}).get("id"))
        self.status.set(f"Renamed to {target['name']}.")

    def _project_menu_popup(self, event) -> str:
        index = self.project_list.nearest(event.y)
        box = self.project_list.bbox(index) if index >= 0 else None
        if not box or index >= len(self._ids) or not (box[1] <= event.y <= box[1] + box[3]):
            return "break"
        self._menu_project_id = self._ids[index]
        try:
            self.project_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.project_menu.grab_release()
        return "break"

    def _ensure_project(self) -> None:
        """Create the first job without painting an empty form over what is already typed."""
        if self.project:
            return
        project = new_project("Untitled job")
        self._capture_form(project)
        save_project(project)
        self.project = project
        self.refresh_projects(project["id"])
        self.status.set(f"Opened {project.get('name')}. {key_status()}")

    def _open_sample_project(self) -> None:
        if self.project:
            self._capture_form(self.project)
            save_project(self.project)
        project = new_project("Sample data hall DI zone", copy.deepcopy(sample_data.EXAMPLE_BASIS))
        project["di"] = copy.deepcopy(sample_data.EXAMPLE_DI)
        project["mode"] = self._selected_mode()
        save_project(project)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])

    def new_sample(self) -> None:
        """Load the sample job and run the DI zone path. Same as the Sample DI chip."""
        self.start_sample_di()

    def start_sample_di(self, typed: str | None = None) -> None:
        """Load the sample job and run the existing DI zone path."""
        raw = (typed or "/sample-di").strip() or "/sample-di"
        self._keep_composer_open()
        self._open_sample_project()
        self._append_chat("user", raw)
        self.run_zone(announce=True, seed=sample_di_seed())

    def _open_bess_project(self) -> None:
        if self.project:
            self._capture_form(self.project)
            save_project(self.project)
        project = new_project(
            "Sample Li-ion BESS room",
            copy.deepcopy(sample_data.EXAMPLE_BESS_BASIS),
        )
        project["mode"] = "synthesis"
        project["bess_inputs"] = copy.deepcopy(sample_data.EXAMPLE_BESS)
        save_project(project)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])
        self._apply_mode("synthesis")
        if self.project is not None:
            self.project["mode"] = "synthesis"

    def start_sample_bess(self, typed: str | None = None) -> None:
        """Load the generic BESS room and run the explosion-control starter."""
        raw = (typed or "/sample-bess").strip() or "/sample-bess"
        self._keep_composer_open()
        self._open_bess_project()
        self._append_chat("user", raw)
        self.run_bess(announce=True, seed=sample_bess_seed())

    def start_zone_run(self, typed: str | None = None) -> None:
        raw = (typed or "/run").strip() or "/run"
        self._keep_composer_open()
        self._ensure_project()
        self._append_chat("user", raw)
        self.run_zone(announce=True)

    def start_heavy(self, raw: str, task: str) -> None:
        """Queue one hosted job. The reply is written into this project's thread."""
        task = (task or "").strip()
        self._keep_composer_open()
        if not task:
            self._local_exchange(raw, "Usage: /heavy describe the heavy job")
            return
        self._ensure_project()
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        self._append_chat("user", raw)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass
        key = load_api_key()
        if not key:
            self._append_chat(
                "assistant",
                "Save an Anthropic API key in Settings before /heavy. "
                "/sample-di and /sample-bess still run on this machine without a key.",
            )
            self._save_form_or_chat(self.project)
            save_project(self.project)
            self.status.set(key_status())
            return
        try:
            basis = self.collect_basis()
            di = self.collect_di()
            form_note = ""
        except ValueError as exc:
            basis = dict(self.project.get("basis") or {})
            di = copy.deepcopy(self.project.get("di") or {})
            form_note = (
                "The optional zone form was not read because a value is not a number. "
                "This message uses the last saved zone. " + str(exc)
            )
        prior = [dict(turn) for turn in self.chat_log[:-1]]
        mode = self.mode_slug.get()
        request_text = chat_request_text(
            prior,
            basis,
            di,
            task,
            self.project.get("last_run"),
            mode,
            self.project.get("bess_run"),
            hosted=True,
        )
        if form_note:
            request_text = form_note + "\n\n" + request_text
        resources = self._managed_resources

        def work(job_id: str) -> None:
            try:
                out = run_heavy_job(
                    anthropic_request(key),
                    system=session_system(),
                    user_text=request_text,
                    resources=resources,
                )
                reply = reply_with_delete_status(out)
            except Exception as exc:
                reply = safe_error(exc)
                self.jobs.mark(job_id, "error", reply)
            self.queue.put(
                lambda oid=origin_id, answer=reply, jid=job_id: self._finish_heavy(
                    oid, answer, job_id=jid
                )
            )

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="heavy",
            title=task,
            work=work,
        )
        self._keep_composer_open()
        self.status.set(f"Heavy job on {MODEL_ID}… {job.heading()}")

    def _slash_new(self, raw: str, name: str) -> None:
        name = name.strip()
        if not name:
            self._local_exchange(raw, "Usage: /new Job name")
            return
        self._start_named_job(name)
        self._append_chat("user", raw)
        self._append_chat(
            "assistant",
            f"Started {self.project['name']}. Ask away. Zone details is optional.",
        )
        self._capture_form(self.project)
        save_project(self.project)
        self.status.set(f"Opened {self.project['name']}.")

    def _local_exchange(self, user_text: str, reply: str) -> None:
        self._ensure_project()
        self._append_chat("user", user_text)
        self._append_chat("assistant", reply)
        self._save_form_or_chat(self.project)
        save_project(self.project)
        self.refresh_projects(self.project["id"])

    def _dispatch_slash(self, command: str, argument: str, raw: str) -> None:
        if command == "sample-di":
            self.start_sample_di(raw)
        elif command == "sample-bess":
            self.start_sample_bess(raw)
        elif command == "run":
            self.start_zone_run(raw)
        elif command == "heavy":
            self.start_heavy(raw, argument)
        elif command == "new":
            self._slash_new(raw, argument)
        elif command == "help":
            self._local_exchange(raw, slash_help_text())
        elif command == "mode":
            self._slash_mode(raw, argument)
        else:
            self._local_exchange(raw, unknown_slash_text(command))

    def _slash_mode(self, raw: str, argument: str) -> None:
        argument = argument.strip().lower()
        if not argument:
            try:
                reply = describe_modes(content_root(), self.mode_slug.get())
            except FileNotFoundError as exc:
                reply = str(exc)
            self._local_exchange(raw, reply)
            return
        known = self._known_modes()
        if argument not in known:
            self._local_exchange(
                raw,
                f"No mode {argument}. Known modes: {', '.join(known) or '(none)'}.",
            )
            return
        self._apply_mode(argument)
        try:
            reply = describe_modes(content_root(), argument)
        except FileNotFoundError as exc:
            reply = str(exc)
        self._local_exchange(raw, reply)

    def delete_job(self, project_id: str | None = None) -> None:
        project_id = project_id or self._selected_id()
        if not project_id:
            return
        if not messagebox.askyesno("Delete", "Delete this job and its chat from this machine?"):
            return
        delete_project(project_id)
        try:
            self.record.delete_project(project_id)
        except Exception as exc:
            self.status.set("The job file was deleted. Its record rows were not. " + safe_error(exc))
        if self.project and self.project.get("id") == project_id:
            # Clear the thread too, so a deleted job's chat is not left on screen.
            self.project = None
            self.chat_log = []
            self._render_chat()
            self._show_saved_run(None)
            self._refresh_team()
        self.refresh_projects((self.project or {}).get("id"))

    def add_segment(self) -> None:
        nps = self.seg_nps.get().strip()
        length = self.seg_length.get().strip()
        if not nps or not length:
            messagebox.showinfo("Segment", "Enter a nominal size and a length.")
            return
        try:
            resolved = ToolSession(content_root()).execute("resolve_pipe_id", {
                "nps": nps,
                "schedule": self.seg_schedule.get().strip(),
                "role": self.seg_role.get(),
            })
        except Exception as exc:
            messagebox.showerror("Pipe ID", safe_error(exc))
            return
        self._insert_segment({
            "role": self.seg_role.get(),
            "nps": resolved.get("nps") or nps,
            "schedule": resolved.get("schedule") or "",
            "length_ft": float(length),
            "d_in": resolved.get("d_in"),
        })
        self.seg_nps.set("")
        self.seg_schedule.set("")
        self.seg_length.set("")
        flags = resolved.get("flags") or []
        if flags:
            self.status.set("; ".join(flags))

    def remove_segment(self) -> None:
        for item in self.pipes.selection():
            self.pipes.delete(item)

    def run_zone(self, *, announce: bool = False, seed: str = "") -> None:
        self._keep_composer_open()
        if not self.project:
            self._report_run_problem(None, "Open a project, or use /sample-di.", announce=announce)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        try:
            self._write_form(self.project)
        except ValueError as exc:
            self._report_run_problem(origin_id, str(exc), announce=announce)
            return
        di = copy.deepcopy(self.project["di"])
        basis = copy.deepcopy(self.project["basis"])
        mode = self.mode_slug.get()
        try:
            pack = content_root()
        except FileNotFoundError as exc:
            self._report_run_problem(origin_id, str(exc), announce=announce)
            return
        self._open_record(self.project)
        use_claude = bool(self.ask_claude.get()) and bool(load_api_key())
        if use_claude:
            self._enqueue_zone(
                origin_id, project_name, pack, di, basis, mode, load_api_key(), announce=announce, seed=seed
            )
            return
        self._run_zone_here(origin_id, project_name, pack, di, basis, mode, announce=announce, seed=seed)

    def _run_zone_here(
        self, origin_id, project_name, pack, di, basis, mode, *, announce: bool = False, seed: str = ""
    ) -> None:
        """Tool plan with no model call. It finishes before the composer returns."""
        job = self.jobs.record(
            project_id=origin_id,
            project_name=project_name,
            kind="zone",
            title="Zone tool plan",
            status="running",
        )
        if announce:
            self._announce_jobs.add(job.id)
            self._remember_seed(job.id, seed)
        try:
            result = run_di_zone(
                pack, di, basis, narrator=None, mode=mode, record=self.record, project_id=origin_id
            )
        except Exception as exc:
            self.jobs.mark(job.id, "error", safe_error(exc))
            self._report_run_problem(origin_id, safe_error(exc), job_id=job.id)
            return
        self.jobs.mark(job.id, "done")
        self._finish_run(origin_id, result, None, job_id=job.id)

    def _enqueue_zone(
        self, origin_id, project_name, pack, di, basis, mode, key, *, announce: bool = False, seed: str = ""
    ) -> None:
        """Queue a zone run that calls the model. The composer stays usable."""

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)

            def narrator(system, user_text, tools, execute):
                client = AnthropicMessages(key)
                return run_tool_loop(
                    client.create,
                    system=system,
                    user_text=user_text,
                    tools=tools,
                    execute=execute,
                    cancel=cancel,
                    required=[
                        "zone_trapped_volume",
                        "dry_delivery_screen",
                        "di_trip_to_water",
                        "elect_di_trim",
                        "releasing_truth_table",
                    ],
                    max_rounds=16,
                    max_tokens=16000,
                )

            try:
                result = run_di_zone(
                    pack, di, basis, narrator=narrator, mode=mode, record=self.record, project_id=origin_id
                )
                error = None
                if result.get("cancelled"):
                    self.jobs.mark(job_id, "cancelled", NARRATION_CANCELLED)
            except Exception as exc:
                result = None
                error = safe_error(exc)
                self.jobs.mark(job_id, "error", error)
            finally:
                self._cancel_events.pop(job_id, None)
            self.queue.put(
                lambda oid=origin_id, res=result, err=error, jid=job_id: self._finish_run(
                    oid, res, err, job_id=jid
                )
            )

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="zone",
            title="Zone tool plan",
            work=work,
        )
        # The worker may finish before submit returns, but the result callback
        # stays on the UI queue until this call returns to the event loop.
        if announce:
            self._announce_jobs.add(job.id)
            self._remember_seed(job.id, seed)
        self._keep_composer_open()
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def run_bess(self, *, announce: bool = False, seed: str = "") -> None:
        """Explosion-control starter. Does not read the optional zone form."""
        self._keep_composer_open()
        if not self.project:
            self._report_bess_problem(None, "Open a project, or use /sample-bess.", announce=announce)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        self._apply_mode("synthesis")
        self.project["mode"] = "synthesis"
        basis = dict(self.project.get("basis") or {})
        room = copy.deepcopy(self.project.get("bess_inputs") or sample_data.EXAMPLE_BESS)
        zone_result = self.project.get("last_run")
        try:
            pack = content_root()
        except FileNotFoundError as exc:
            self._report_bess_problem(origin_id, str(exc), announce=announce)
            return
        use_claude = bool(self.ask_claude.get()) and bool(load_api_key())
        if use_claude:
            self._enqueue_bess(
                origin_id, project_name, pack, room, basis, zone_result, load_api_key(),
                announce=announce, seed=seed,
            )
            return
        self._run_bess_here(
            origin_id, project_name, pack, room, basis, zone_result, announce=announce, seed=seed
        )

    def _run_bess_here(
        self, origin_id, project_name, pack, room, basis, zone_result, *, announce: bool = False, seed: str = ""
    ) -> None:
        """LFL tool plan with no model call. It finishes before the composer returns."""
        job = self.jobs.record(
            project_id=origin_id,
            project_name=project_name,
            kind="bess",
            title="Explosion-control starter",
            status="running",
        )
        if announce:
            self._announce_jobs.add(job.id)
            self._remember_seed(job.id, seed)
        try:
            result = run_bess_plan(
                pack, room, basis, zone_result=zone_result, narrator=None, mode="synthesis",
                record=self.record, project_id=origin_id,
            )
        except Exception as exc:
            self.jobs.mark(job.id, "error", safe_error(exc))
            self._report_bess_problem(origin_id, safe_error(exc), job_id=job.id)
            return
        self.jobs.mark(job.id, "done")
        self._finish_bess(origin_id, result, None, job_id=job.id)

    def _enqueue_bess(
        self, origin_id, project_name, pack, room, basis, zone_result, key, *, announce: bool = False,
        seed: str = "",
    ) -> None:
        """Queue a starter that calls the model. The composer stays usable."""

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)

            def narrator(system, user_text, tools, execute):
                client = AnthropicMessages(key)
                return run_tool_loop(
                    client.create,
                    system=system,
                    user_text=user_text,
                    tools=tools,
                    execute=execute,
                    cancel=cancel,
                    required=["lfl_setpoints", "read_skill"],
                    max_rounds=16,
                    max_tokens=16000,
                )

            try:
                result = run_bess_plan(
                    pack,
                    room,
                    basis,
                    zone_result=zone_result,
                    narrator=narrator,
                    mode="synthesis",
                    record=self.record,
                    project_id=origin_id,
                )
                error = None
                if result.get("cancelled"):
                    self.jobs.mark(job_id, "cancelled", NARRATION_CANCELLED)
            except Exception as exc:
                result = None
                error = safe_error(exc)
                self.jobs.mark(job_id, "error", error)
            finally:
                self._cancel_events.pop(job_id, None)
            self.queue.put(
                lambda oid=origin_id, res=result, err=error, jid=job_id: self._finish_bess(
                    oid, res, err, job_id=jid
                )
            )

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="bess",
            title="Explosion-control starter",
            work=work,
        )
        if announce:
            self._announce_jobs.add(job.id)
            self._remember_seed(job.id, seed)
        self._keep_composer_open()
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def _report_bess_problem(
        self,
        origin_id: str | None,
        message: str,
        job_id: str | None = None,
        *,
        announce: bool | None = None,
    ) -> None:
        self._keep_composer_open()
        if origin_id:
            origin_id = self._destination_id(origin_id, job_id)
        taken = self._take_announce(job_id)
        if announce is None:
            announce = taken
        else:
            announce = bool(announce) or taken
        message = self._with_job_label(job_id, self._with_seed(job_id, message))
        still_here = self.project is not None and (origin_id is None or self.project.get("id") == origin_id)
        if announce and still_here:
            self.chat_log.append(self._assistant_turn(message, job_id))
            self._render_chat()
            self.project["mode"] = "synthesis"
            self._save_form_or_chat(self.project)
            save_project(self.project)
        elif announce and origin_id:
            self._append_saved_chat(origin_id, message, job_id)
        elif still_here and origin_id:
            messagebox.showerror("Explosion-control starter", message)
        self.status.set(message or "The explosion-control starter did not run.")

    def _finish_bess(
        self,
        origin_id: str,
        result: dict | None,
        error: str | None,
        job_id: str | None = None,
    ) -> None:
        self._keep_composer_open()
        origin_id = self._destination_id(origin_id, job_id)
        announce = self._take_announce(job_id)
        still_here = self.project is not None and self.project.get("id") == origin_id
        if error or result is None:
            message = self._with_job_label(
                job_id, self._with_seed(job_id, error or "The explosion-control starter did not run.")
            )
            if announce and still_here:
                self.chat_log.append(self._assistant_turn(message, job_id))
                self._render_chat()
                self.project["mode"] = "synthesis"
                self._save_form_or_chat(self.project)
                save_project(self.project)
            elif announce:
                self._append_saved_chat(origin_id, message, job_id)
            elif still_here:
                messagebox.showerror("Explosion-control starter", message)
            self.status.set("The explosion-control starter did not run.")
            return
        result = self._stamp_job(result, job_id)
        body = bess_chat_summary(result)
        if result.get("cancelled"):
            body = CANCELLED_RUN_LINE + "\n\n" + body
        summary = self._with_job_label(job_id, self._with_seed(job_id, body)) if announce else ""
        if still_here:
            self.project["bess_run"] = result
            self.project["mode"] = "synthesis"
            if summary:
                self.chat_log.append(self._assistant_turn(summary, job_id))
                self._render_chat()
            self._save_form_or_chat(self.project)
            save_project(self.project)
            self._show_bess_result(result)
            self._refresh_team()
        else:
            try:
                project = load_project(origin_id)
            except (OSError, json.JSONDecodeError):
                self.status.set("The starter finished, and that project is no longer on this machine.")
                return
            project["bess_run"] = result
            project["mode"] = "synthesis"
            if summary:
                chat = list(project.get("chat") or [])
                chat.append(self._assistant_turn(summary, job_id))
                project["chat"] = chat
            save_project(project)
            heading = (result or {}).get("job_heading") or ""
            note = "Explosion-control starter finished on another project. Open it to see the draft."
            self.status.set(f"{heading}. {note}" if heading else note)
            return
        if result.get("cancelled"):
            self.status.set(self._with_job_label(job_id, CANCELLED_RUN_LINE))
        elif result.get("source") == "claude":
            note = f"LFL tool plan plus {MODEL_ID}. The starter uses the tool plan when the draft disagrees."
            if result.get("warnings"):
                note = note + " " + result["warnings"][0]
            used = usage_summary(result.get("usage"))
            if used:
                note = note + " " + used
            self.status.set(self._with_job_label(job_id, note))
        else:
            note = "LFL tool plan only."
            if self.ask_claude.get() and not load_api_key():
                note = "LFL tool plan only. Save an API key in Settings to ask Claude."
            elif result.get("warnings"):
                note = "LFL tool plan only. " + result["warnings"][0]
            self.status.set(self._with_job_label(job_id, note))

    def _report_run_problem(
        self,
        origin_id: str | None,
        message: str,
        job_id: str | None = None,
        *,
        announce: bool | None = None,
    ) -> None:
        self._keep_composer_open()
        if origin_id:
            origin_id = self._destination_id(origin_id, job_id)
        taken = self._take_announce(job_id)
        if announce is None:
            announce = taken
        else:
            announce = bool(announce) or taken
        message = self._with_job_label(job_id, self._with_seed(job_id, message))
        still_here = self.project is not None and (origin_id is None or self.project.get("id") == origin_id)
        if announce and still_here:
            self.chat_log.append(self._assistant_turn(message, job_id))
            self._render_chat()
            self._save_form_or_chat(self.project)
            save_project(self.project)
        elif announce and origin_id:
            self._append_saved_chat(origin_id, message, job_id)
        elif still_here and origin_id:
            messagebox.showerror("DI zone", message)
        self.status.set(message or "The zone did not run.")

    def _append_saved_chat(self, origin_id: str, text: str, job_id: str | None = None) -> None:
        try:
            project = load_project(origin_id)
        except (OSError, json.JSONDecodeError):
            self.status.set("The reply could not be saved.")
            return
        chat = list(project.get("chat") or [])
        chat.append(self._assistant_turn(text, job_id))
        project["chat"] = chat
        save_project(project)

    def _take_announce(self, job_id: str | None) -> bool:
        if not job_id:
            return False
        announce = job_id in self._announce_jobs
        self._announce_jobs.discard(job_id)
        return announce

    def _remember_seed(self, job_id: str, seed: str) -> None:
        if seed:
            self._seed_notes[job_id] = seed

    def _with_seed(self, job_id: str | None, body: str) -> str:
        """Put a sample's "what was loaded" note above its reply. The note is used once."""
        seed = self._seed_notes.pop(job_id, "") if job_id else ""
        if not seed:
            return body
        return f"{seed}\n\n{body}" if body else seed

    def _finish_run(
        self,
        origin_id: str,
        result: dict | None,
        error: str | None,
        job_id: str | None = None,
    ) -> None:
        self._keep_composer_open()
        origin_id = self._destination_id(origin_id, job_id)
        announce = self._take_announce(job_id)
        still_here = self.project is not None and self.project.get("id") == origin_id
        if error or result is None:
            message = self._with_job_label(job_id, self._with_seed(job_id, error or "The zone did not run."))
            if announce and still_here:
                self.chat_log.append(self._assistant_turn(message, job_id))
                self._render_chat()
                self._save_form_or_chat(self.project)
                save_project(self.project)
            elif announce:
                self._append_saved_chat(origin_id, message, job_id)
            elif still_here:
                messagebox.showerror("DI zone", message)
            self.status.set("The zone did not run.")
            return
        result = self._stamp_job(result, job_id)
        body = chat_run_summary(result)
        if result.get("cancelled"):
            body = CANCELLED_RUN_LINE + "\n\n" + body
        summary = self._with_job_label(job_id, self._with_seed(job_id, body)) if announce else ""
        if still_here:
            self.project["last_run"] = result
            if summary:
                self.chat_log.append(self._assistant_turn(summary, job_id))
                self._render_chat()
            form_error = self._save_form_or_chat(self.project)
            save_project(self.project)
            self._show_result(result)
            self._refresh_team()
        else:
            try:
                project = load_project(origin_id)
            except (OSError, json.JSONDecodeError):
                self.status.set("The zone finished, and that project is no longer on this machine.")
                return
            project["last_run"] = result
            if summary:
                chat = list(project.get("chat") or [])
                chat.append(self._assistant_turn(summary, job_id))
                project["chat"] = chat
            save_project(project)
            heading = (result or {}).get("job_heading") or ""
            note = "DI zone finished on another project. Open it to see the results."
            self.status.set(f"{heading}. {note}" if heading else note)
            return
        if form_error:
            self.status.set(self._with_job_label(job_id, form_error))
        elif result.get("cancelled"):
            self.status.set(self._with_job_label(job_id, CANCELLED_RUN_LINE))
        elif result["source"] == "claude":
            note = f"Tool plan plus {MODEL_ID}. Tables and Section {DRAFT_SECTION} use the tool plan."
            if result.get("warnings"):
                note = note + " " + result["warnings"][0]
            used = usage_summary(result.get("usage"))
            if used:
                note = note + " " + used
            self.status.set(self._with_job_label(job_id, note))
        else:
            note = "Tool plan only."
            if self.ask_claude.get() and not load_api_key():
                note = "Tool plan only. Save an API key in Settings to ask Claude."
            elif result.get("warnings"):
                note = "Tool plan only. " + result["warnings"][0]
            self.status.set(self._with_job_label(job_id, note))

    def _show_saved_run(self, result: dict | None) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        if result and result.get("kind") == "bess":
            self._show_bess_result(result)
        elif result:
            self._show_result(result)
        else:
            self.results.insert(
                "1.0",
                "No zone run on this job yet.\n\n"
                "Fill in the Zone tab and press Run zone (or type /run). "
                "The run is posted in the thread, and the tool-plan figures stay here for export.",
            )
        self.results.configure(state="disabled")

    def _show_result(self, result: dict) -> None:
        tools = result["tools"]
        volume = tools["zone_trapped_volume"]
        trip = tools["di_trip_to_water"]
        trim = tools["elect_di_trim"]
        source = result.get("source") or "tool-plan"
        if source == "claude":
            header = f"Narrative from {result.get('model') or MODEL_ID}. Tables use the tool plan."
        else:
            header = "Narrative from the tool plan."
        lines = []
        heading = result.get("job_heading")
        if heading:
            lines.append(str(heading))
            lines.append("")
        lines.extend([
            "Assumptions vs calculated",
            trim_assumption_text(volume),
            screen_limit_assumption_text(trip),
            judgment_label_line(),
            "",
            header,
            result.get("narrative") or "",
            "",
            "— Tool plan —",
            f"Zone {volume['zone_gal']:.1f} gal    t_total {trip['t_total_s']:.1f} s    "
            f"passes screen: {'yes' if trip['passes_screen'] else 'no'}    "
            f"trim family: {trim.get('family') or trim.get('status')}",
            "",
            "Flags",
        ])
        lines.extend(f"• {flag}" for flag in result.get("flags") or [])
        if result.get("warnings"):
            lines.append("")
            lines.append("Warnings")
            lines.extend(f"• {item}" for item in result["warnings"])
        lines.append("")
        lines.append("Transcript")
        lines.append(format_transcript(result.get("transcript") or []))
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", "\n".join(lines))
        self.results.configure(state="disabled")

    def _show_bess_result(self, result: dict) -> None:
        source = result.get("source") or "tool-plan"
        if source == "claude":
            header = f"Narrative from {result.get('model') or MODEL_ID}. The LFL tool plan governs."
        else:
            header = "Narrative from the LFL tool plan."
        lines = []
        heading = result.get("job_heading")
        if heading:
            lines.append(str(heading))
            lines.append("")
        lines.extend([
            "Explosion-control starter. vol% and ppm come from the LFL tool.",
            "An election or a duration the tool did not return is ASSUMED.",
            "Zone gallons and seconds stay on the zone tool plan when one has run.",
            "",
            header,
            result.get("narrative") or "",
            "",
            "Flags",
        ])
        lines.extend(f"• {flag}" for flag in result.get("flags") or [])
        if result.get("warnings"):
            lines.append("")
            lines.append("Warnings")
            lines.extend(f"• {item}" for item in result["warnings"])
        lines.append("")
        lines.append("Transcript")
        lines.append(format_transcript(result.get("transcript") or []))
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", "\n".join(lines))
        self.results.configure(state="disabled")

    def export_to(self, path: Path, create=None) -> Path:
        """Run the blind claim check, post it here, then write the docx if it passes.

        create() is Messages.create. Without it, a saved key is used. With no
        key, the checker does not run and the file is not written.
        """
        if not self.project or not self.project.get("last_run"):
            raise RuntimeError("Run /sample-di or /run before exporting.")
        snapshot = copy.deepcopy(self.project["last_run"])
        outcome = self._claim_outcome(create, snapshot)
        job = self.jobs.record(
            project_id=self.project["id"],
            project_name=self.project.get("name") or "Untitled job",
            kind="claim",
            title=f"Section {DRAFT_SECTION} claim check",
            status="done",
        )
        self._store_claim(self.project, outcome, job.id)
        write_packet_files(claim_dir(self.project["id"]), outcome)
        self.chat_log.append(self._assistant_turn(self._with_job_label(job.id, outcome["thread"]), job.id))
        self._render_chat()
        self._save_form_or_chat(self.project)
        save_project(self.project)
        if not outcome["all_supported"]:
            raise RuntimeError(outcome["block_reason"])
        return self._write_export(Path(path), outcome, snapshot)

    def export_docx(self) -> None:
        if not self.project or not self.project.get("last_run"):
            messagebox.showinfo("Export", EXPORT_NEEDS_RUN)
            return
        self.start_claim_check(offer_export=True)

    def design_basis_ready(self) -> str:
        """Empty when the job has a record to export. Otherwise the reason it does not."""
        if not self.project:
            return "Open a job first."
        self._open_record(self.project)
        snapshot = self.record.snapshot(self.project["id"])
        # Basis facts alone come from the form defaults. A design basis needs
        # at least one recorded calculation, finding, or decision.
        if not snapshot["calcs"] and not snapshot["findings"] and not snapshot["decisions"]:
            return (
                "Nothing is on this job's record yet. Run /sample-di or /run, or ask a question, "
                "then export the design basis."
            )
        # Findings are model claims. They need a current blind check that supports every one.
        return export_gate(self.record, self.project["id"])

    def export_design_basis_to(self, path: Path) -> Path:
        """Write the Design Basis and Open Questions document for the open job."""
        reason = self.design_basis_ready()
        if reason:
            raise RuntimeError(reason)
        snapshot = self.record.snapshot(self.project["id"])
        return write_design_basis(
            Path(path), self.project, snapshot, claim_check=latest_check(self.record, self.project["id"])
        )

    def export_design_basis(self) -> None:
        reason = self.design_basis_ready()
        if reason:
            messagebox.showinfo(DESIGN_BASIS_TITLE, reason)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Export {DESIGN_BASIS_TITLE}",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx")],
            initialfile=f"{self.project.get('name', 'job')}-design-basis.docx",
        )
        if not path:
            self.status.set("Design basis export was not written.")
            return
        try:
            written = self.export_design_basis_to(Path(path))
        except Exception as exc:
            messagebox.showerror(DESIGN_BASIS_TITLE, safe_error(exc))
            return
        self.status.set(f"Exported {written}")

    def start_claim_check(self, offer_export: bool = False) -> None:
        """Queue the blind claim check on this project. The composer stays usable."""
        self._keep_composer_open()
        self._ensure_project()
        if not self.project or not self.project.get("last_run"):
            messagebox.showinfo("Export", EXPORT_NEEDS_RUN)
            return
        snapshot = copy.deepcopy(self.project["last_run"])
        packet = build_packet(snapshot)
        stored = self.project.get("claim_check") or {}
        if offer_export and stored.get("all_supported") and same_packet(stored, packet):
            self._offer_export(stored)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        key = load_api_key()

        def work(job_id: str) -> None:
            try:
                if key:
                    outcome = judge(content_root(), packet, AnthropicMessages(key).create)
                else:
                    outcome = unanswered(packet)
            except Exception as exc:
                message = safe_error(exc)
                self.jobs.mark(job_id, "error", message)
                self.queue.put(
                    lambda oid=origin_id, err=message, jid=job_id, offer=offer_export: self._finish_claim(
                        oid, None, err, jid, offer
                    )
                )
                return
            self.queue.put(
                lambda oid=origin_id, found=outcome, jid=job_id, offer=offer_export, snap=snapshot: self._finish_claim(
                    oid, found, None, jid, offer, snap
                )
            )

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="claim",
            title=f"Section {DRAFT_SECTION} claim check",
            work=work,
        )
        self._keep_composer_open()
        self.status.set(f"Claim check… {job.heading()}")

    def _claim_outcome(self, create, result=None) -> dict:
        packet = build_packet(result if result is not None else self.project["last_run"])
        if create is None:
            key = load_api_key()
            if not key:
                return unanswered(packet)
            create = AnthropicMessages(key).create
        return judge(content_root(), packet, create)

    def _store_claim(self, project: dict, outcome: dict, job_id: str | None) -> None:
        stored = dict(outcome)
        if job_id:
            stored["job_id"] = job_id
        project["claim_check"] = stored

    def _write_export(self, path: Path, outcome: dict, result=None) -> Path:
        written = write_docx(path, self.project, result if result is not None else self.project["last_run"])
        write_packet_files(written.parent, outcome)
        return written

    def _offer_export(self, outcome: dict, result=None) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Export draft Section {DRAFT_SECTION}",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx")],
            initialfile=f"{self.project.get('name', 'di-zone')}.docx",
        )
        if not path:
            note = (outcome or {}).get("status_line") or PACKAGE_STATUS
            self.status.set(
                f"{note} Export of Section {DRAFT_SECTION} was not written."
            )
            return
        try:
            written = self._write_export(Path(path), outcome, result)
        except Exception as exc:
            messagebox.showerror("Export", safe_error(exc))
            return
        self.status.set(f"Exported {written}")

    def _finish_claim(
        self,
        origin_id: str,
        outcome: dict | None,
        error: str | None,
        job_id: str | None = None,
        offer_export: bool = False,
        export_result: dict | None = None,
    ) -> None:
        """Post the check into the project thread that started it."""
        self._keep_composer_open()
        origin_id = self._destination_id(origin_id, job_id)
        still_here = self.project is not None and self.project.get("id") == origin_id
        if error or outcome is None:
            message = self._with_job_label(job_id, error or "The claim check did not finish.")
            if still_here:
                self.chat_log.append(self._assistant_turn(message, job_id))
                self._render_chat()
                self._save_form_or_chat(self.project)
                save_project(self.project)
            else:
                self._append_saved_chat(origin_id, message, job_id)
            self.status.set(message)
            return
        message = self._with_job_label(job_id, outcome["thread"])
        if still_here:
            self._store_claim(self.project, outcome, job_id)
            write_packet_files(claim_dir(origin_id), outcome)
            self.chat_log.append(self._assistant_turn(message, job_id))
            self._render_chat()
            self._save_form_or_chat(self.project)
            save_project(self.project)
        else:
            try:
                project = load_project(origin_id)
            except (OSError, json.JSONDecodeError):
                self.status.set("The claim check finished, and that project is no longer on this machine.")
                return
            self._store_claim(project, outcome, job_id)
            write_packet_files(claim_dir(origin_id), outcome)
            chat = list(project.get("chat") or [])
            chat.append(self._assistant_turn(message, job_id))
            project["chat"] = chat
            save_project(project)
            heading = self._with_job_label(job_id, "")
            note = "Claim check saved on the project that started it."
            self.status.set(f"{heading} {note}".strip())
            return
        if outcome["all_supported"] and offer_export:
            self._offer_export(outcome, export_result)
            return
        if outcome["all_supported"]:
            self.status.set(self._with_job_label(job_id, outcome.get("status_line") or PACKAGE_STATUS))
            return
        self.status.set(self._with_job_label(job_id, outcome["block_reason"]))

    def _render_chat(self) -> None:
        view = self.chat_view
        view.configure(state="normal")
        view.delete("1.0", "end")
        if not self.chat_log:
            self._render_welcome()
        for turn in self.chat_log:
            text = turn.get("text") or ""
            if turn.get("role") == "user":
                view.insert("end", "You\n", ("who_user",))
                view.insert("end", text + "\n", ("body",))
                continue
            view.insert("end", "Assistant\n", ("who_assistant",))
            for chunk, tags in markdown_segments(text):
                view.insert("end", chunk, ("body",) + tags)
            view.insert("end", "\n", ("body",))
        pending = self._pending_here()
        if pending and self.chat_log:
            view.insert("end", "Working on it…\n", ("pending",))
        self._pending_shown = pending
        view.configure(state="disabled")
        view.see("end")
        self._update_title()

    def _render_welcome(self) -> None:
        """Empty-thread welcome. Asking a question needs nothing from this."""
        view = self.chat_view
        lines = THREAD_HINT.splitlines()
        view.insert("end", lines[0] + "\n", ("welcome_title",))
        for line in lines[1:]:
            view.insert("end", line + "\n", ("welcome_sub",))
        if not self._key_saved:
            view.insert("end", WELCOME_KEY_LINK + "\n", ("welcome_link", "link_settings"))
        view.insert("end", WELCOME_SAMPLE_LINK + "\n", ("welcome_link", "link_sample_di"))
        view.insert("end", WELCOME_FOOTNOTE + "\n", ("welcome_hint",))

    def _append_chat(self, role: str, text: str) -> None:
        self.chat_log.append({"role": role, "text": text})
        self._render_chat()

    def send_chat(self) -> None:
        text = self.chat_entry.get().strip()
        if not text:
            return
        self.chat_entry.delete(0, "end")
        parsed = parse_slash_command(text)
        if parsed is not None:
            command, argument = parsed
            self._dispatch_slash(command, argument, text)
            return
        self._send_chat_message(text)

    def _send_chat_message(self, text: str) -> None:
        """Ask Claude without blocking the window. The zone form is optional."""
        self._keep_composer_open()
        self._ensure_project()
        if self._takes_name_from(text):
            # A chat-first job is named after its first question.
            self.project["name"] = chat_title(text)
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        self._append_chat("user", text)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass
        key = load_api_key()
        self._key_saved = bool(key)
        if not key:
            self._append_chat(
                "assistant",
                "I need an Anthropic API key before I can answer. Add it in Settings "
                "(bottom of the sidebar). The key stays on this machine.\n\n"
                "/sample-di still loads the sample zone and runs the tool plan here without a key, "
                "and /sample-bess runs the explosion-control starter the same way.",
            )
            self._save_form_or_chat(self.project)
            save_project(self.project)
            self.refresh_projects(origin_id)
            self.status.set(key_status())
            return
        # Save the question now so the sidebar shows the job and its name
        # while the reply is on its way.
        self._save_form_or_chat(self.project)
        save_project(self.project)
        self.refresh_projects(origin_id)
        self._open_record(self.project)
        try:
            basis = self.collect_basis()
            di = self.collect_di()
            form_note = ""
        except ValueError as exc:
            basis = dict(self.project.get("basis") or {})
            di = copy.deepcopy(self.project.get("di") or {})
            form_note = (
                "The optional zone form was not read because a value is not a number. "
                "This message uses the last saved zone. " + str(exc)
            )
        prior = [dict(turn) for turn in self.chat_log[:-1]]
        mode = self.mode_slug.get()
        request = chat_request_text(
            prior,
            basis,
            di,
            text,
            self.project.get("last_run"),
            mode,
            self.project.get("bess_run"),
        )
        if form_note:
            request = form_note + "\n\n" + request

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)
            try:
                pack = content_root()
                client = AnthropicMessages(key)
                out = run_everyday(
                    pack, client.create, request, mode=mode,
                    record=self.record, project_id=origin_id, agent="lead", cancel=cancel,
                )
                reply = everyday_reply(out)
                summary = team_summary(out)
                if summary:
                    reply = reply + "\n\n" + summary
                used = usage_summary(out.get("usage"))
            except TurnCancelled as exc:
                reply = "Cancelled. " + str(exc) + " Nothing after that point was written."
                used = ""
                self.jobs.mark(job_id, "cancelled", str(exc))
            except Exception as exc:
                reply = safe_error(exc)
                used = ""
                self.jobs.mark(job_id, "error", reply)
            finally:
                self._cancel_events.pop(job_id, None)
            self.queue.put(
                lambda oid=origin_id, answer=reply, jid=job_id, tokens=used: self._finish_chat(
                    oid, answer, job_id=jid, usage=tokens
                )
            )

        job = self.jobs.submit(
            project_id=origin_id,
            project_name=project_name,
            kind="chat",
            title=text,
            work=work,
        )
        self._keep_composer_open()
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")

    def _takes_name_from(self, text: str) -> bool:
        """True for the first typed question in a job that still has the default name."""
        if not self.project or (self.project.get("name") or UNTITLED_JOB) != UNTITLED_JOB:
            return False
        return not any(
            turn.get("role") == "user" and not str(turn.get("text") or "").startswith("/")
            for turn in self.chat_log
        ) and bool((text or "").strip())

    def _finish_chat(
        self,
        origin_id: str,
        reply: str,
        job_id: str | None = None,
        usage: str = "",
    ) -> None:
        """Post the reply. usage is the token line from usage_summary, shown on the status bar."""
        self._keep_composer_open()
        origin_id = self._destination_id(origin_id, job_id)
        reply = self._with_job_label(job_id, reply)
        if self.project is not None and self.project.get("id") == origin_id:
            self.chat_log.append(self._assistant_turn(reply, job_id))
            self._render_chat()
            form_error = self._save_form_or_chat(self.project)
            save_project(self.project)
            if self.project.get("last_run"):
                note = f"Chat updated. Tables and Section {DRAFT_SECTION} stay on the tool plan."
            else:
                note = "Chat updated."
            if usage:
                note = f"{note} {usage}"
            self.status.set(form_error or self._with_job_label(job_id, note))
            self._refresh_team()
            return
        try:
            project = load_project(origin_id)
        except (OSError, json.JSONDecodeError):
            self.status.set("The chat reply could not be saved.")
            return
        chat = list(project.get("chat") or [])
        chat.append(self._assistant_turn(reply, job_id))
        project["chat"] = chat
        save_project(project)
        job = self._job_record(job_id)
        heading = job.heading() if job is not None else ""
        note = "Chat reply saved on another project."
        self.status.set(f"{heading}. {note}" if heading else note)

    def _finish_heavy(self, origin_id: str, reply: str, job_id: str | None = None) -> None:
        """Post a heavy-job reply into the thread on the project that started it."""
        self._keep_composer_open()
        origin_id = self._destination_id(origin_id, job_id)
        reply = self._with_job_label(job_id, reply)
        if self.project is not None and self.project.get("id") == origin_id:
            self.chat_log.append(self._assistant_turn(reply, job_id))
            self._render_chat()
            form_error = self._save_form_or_chat(self.project)
            save_project(self.project)
            if self.project.get("last_run"):
                note = (
                    f"Heavy job is back in this thread. "
                    f"Tables and Section {DRAFT_SECTION} stay on the tool plan."
                )
            else:
                note = "Heavy job is back in this thread."
            self.status.set(form_error or self._with_job_label(job_id, note))
            return
        try:
            project = load_project(origin_id)
        except (OSError, json.JSONDecodeError):
            self.status.set("The heavy-job reply could not be saved.")
            return
        chat = list(project.get("chat") or [])
        chat.append(self._assistant_turn(reply, job_id))
        project["chat"] = chat
        save_project(project)
        job = self._job_record(job_id)
        heading = job.heading() if job is not None else ""
        note = "Heavy job saved on the project that started it."
        self.status.set(f"{heading}. {note}" if heading else note)

    def _set_content_banner(self, text: str) -> None:
        self.content_banner.set(text)
        try:
            if text:
                if not self.banner.winfo_ismapped():
                    self.banner.pack(fill="x", before=self.main_body)
            elif self.banner.winfo_ismapped():
                self.banner.pack_forget()
        except tk.TclError:
            pass

    def _show_changelog(self, lines: list[str]) -> None:
        widget = getattr(self, "_changelog_view", None)
        if widget is None:
            return
        try:
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", format_changelog(lines))
            widget.configure(state="disabled")
        except tk.TclError:
            self._changelog_view = None

    def _maybe_check_content_on_launch(self) -> None:
        try:
            if not self.root.winfo_exists():
                return
        except tk.TclError:
            return
        if not updates_on_launch():
            return
        self._start_content_check(manual=False)

    def _start_content_check(self, *, manual: bool, url: str | None = None, status_var=None) -> None:
        if self._content_check_running:
            return
        self._content_check_running = True

        def work():
            try:
                result = check_for_content_update(url, apply=True)
            except Exception as exc:
                result = UpdateResult(
                    status="error",
                    message=safe_error(exc),
                    version=content_version_text(),
                )
            self.queue.put(
                lambda result=result: self._finish_content_check(
                    result, manual=manual, status_var=status_var
                )
            )

        threading.Thread(target=work, daemon=True).start()

    def _finish_content_check(self, result, *, manual: bool, status_var=None) -> None:
        self._content_check_running = False
        version_line = content_status_line()
        if result.status == "updated":
            self._set_content_banner(update_banner(result.version, result.changelog or []))
            self.content_status.set(version_line)
        elif result.status in {"offline", "error", "rejected", "needs_app"} and not manual:
            self.content_status.set(f"{version_line} (still the last good pack)")
        else:
            self.content_status.set(version_line)
        version_var = getattr(self, "_settings_version", None)
        if version_var is not None:
            try:
                version_var.set(f"Content version: {content_version_text()}")
            except tk.TclError:
                self._settings_version = None
        if status_var is not None:
            try:
                status_var.set(result.message)
            except tk.TclError:
                pass
        shown = result.changelog if result.changelog is not None else current_changelog()
        self._show_changelog(shown)

    def open_settings(self) -> None:
        px = self.theme.px
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.configure(bg=palette.BG)
        win.geometry(f"{px(640)}x{px(660)}")
        win.minsize(px(520), px(480))
        frame = ttk.Frame(win, padding=(px(22), px(18), px(22), px(16)))
        frame.pack(fill="both", expand=True)
        wrap = px(580)

        ttk.Label(frame, text="Anthropic API key", style="Job.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                f"Your own key, used with {MODEL_ID}. It stays on this machine and is never written "
                "into a job, the chat, or an export."
            ),
            style="Muted.TLabel",
            wraplength=wrap,
            justify="left",
        ).pack(anchor="w", pady=(px(2), px(8)))
        key_var = tk.StringVar()
        key_row = ttk.Frame(frame)
        key_row.pack(fill="x")
        key_entry = ttk.Entry(key_row, textvariable=key_var, show="•")
        key_entry.pack(side="left", fill="x", expand=True)
        status = tk.StringVar(value=key_status())

        def key_changed() -> None:
            self._key_saved = bool(load_api_key())
            self.status.set(key_status())
            if not self.chat_log:
                self._render_chat()

        def save():
            raw = key_var.get().strip()
            if not raw:
                status.set("Paste a key, then save. The stored key was left as it is.")
                return
            try:
                where = save_api_key(raw)
            except Exception as exc:
                status.set(safe_error(exc))
                return
            key_var.set("")
            status.set(key_status() if where else "Key was not stored.")
            self.ask_claude.set(True)
            key_changed()

        def clear():
            clear_api_key()
            key_var.set("")
            status.set(key_status())
            self.ask_claude.set(False)
            key_changed()

        def check():
            key = key_var.get().strip() or load_api_key()
            if not key:
                status.set("No API key saved.")
                return
            status.set("Checking the model id…")

            def work():
                try:
                    found = AnthropicMessages(key).check_model()
                    message = f"The key can see model {found}."
                except Exception as exc:
                    message = safe_error(exc)
                self.queue.put(lambda: status.set(message))

            threading.Thread(target=work, daemon=True).start()

        ttk.Button(key_row, text="Save key", style="Accent.TButton", command=save).pack(side="left", padx=(px(8), 0))
        key_entry.bind("<Return>", lambda _event: save())
        ttk.Label(frame, textvariable=status, wraplength=wrap, justify="left").pack(anchor="w", pady=(px(8), px(4)))
        key_tools = ttk.Frame(frame)
        key_tools.pack(anchor="w")
        ttk.Button(key_tools, text="Check key", command=check).pack(side="left")
        ttk.Button(key_tools, text="Clear key", command=clear).pack(side="left", padx=px(6))
        ttk.Label(frame, text=key_storage_help(), style="Small.TLabel", wraplength=wrap, justify="left").pack(
            anchor="w", pady=(px(8), 0)
        )

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=px(16))

        ttk.Label(frame, text="Content pack", style="Job.TLabel").pack(anchor="w")
        self._settings_version = tk.StringVar(value=f"Content version: {content_version_text()}")
        ttk.Label(frame, textvariable=self._settings_version, style="Muted.TLabel").pack(anchor="w", pady=(px(2), px(6)))
        content_line = tk.StringVar(value="")
        feed_var = tk.StringVar(value=resolved_feed_url())

        def check_updates():
            typed = feed_var.get().strip()
            try:
                used = remember_feed_url(typed)
            except ContentUpdateError as exc:
                content_line.set(str(exc))
                return
            feed_var.set(used)
            content_line.set("Checking for a content pack…")
            self._start_content_check(manual=True, url=used, status_var=content_line)

        update_row = ttk.Frame(frame)
        update_row.pack(fill="x")
        ttk.Button(update_row, text="Check for updates", command=check_updates).pack(side="left")
        ttk.Label(update_row, textvariable=content_line, style="Muted.TLabel", wraplength=px(400), justify="left").pack(
            side="left", padx=(px(10), 0)
        )
        ttk.Label(
            frame,
            text=(
                "A newer pack is used only after its sha256 matches. "
                "Your API key and jobs stay on this machine."
            ),
            style="Small.TLabel",
            wraplength=wrap,
            justify="left",
        ).pack(anchor="w", pady=(px(6), px(8)))
        ttk.Label(frame, text="WHAT'S NEW", style="Small.TLabel", font=self.theme.fonts["section"]).pack(anchor="w")
        self._changelog_view = tk.Text(
            frame,
            height=5,
            wrap="word",
            bd=0,
            relief="flat",
            highlightthickness=0,
            bg=palette.SURFACE,
            fg=palette.TEXT,
            padx=px(10),
            pady=px(6),
            font=self.theme.fonts["list"],
        )
        self._changelog_view.insert("1.0", format_changelog(current_changelog()))
        self._changelog_view.configure(state="disabled")
        self._changelog_view.pack(fill="x", pady=(px(4), px(10)))
        changelog_widget = self._changelog_view
        version_var = self._settings_version

        def close_settings():
            if getattr(self, "_changelog_view", None) is changelog_widget:
                self._changelog_view = None
            if getattr(self, "_settings_version", None) is version_var:
                self._settings_version = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close_settings)
        win.bind("<Escape>", lambda _event: close_settings())

        advanced_open = tk.BooleanVar(value=False)
        advanced = ttk.Frame(frame)

        def toggle_advanced():
            if advanced_open.get():
                advanced.pack(fill="x", pady=(px(6), 0))
            else:
                advanced.pack_forget()

        ttk.Checkbutton(
            frame,
            text="Advanced: content feed and content pack folder",
            variable=advanced_open,
            command=toggle_advanced,
        ).pack(anchor="w")
        ttk.Label(advanced, text="Content feed URL", style="Small.TLabel").pack(anchor="w", pady=(px(4), px(2)))
        ttk.Entry(advanced, textvariable=feed_var).pack(fill="x")
        ttk.Label(
            advanced,
            text="Content pack folder (skills/, roles/, modes/, and calcs/ at the top level)",
            style="Small.TLabel",
        ).pack(anchor="w", pady=(px(8), px(2)))
        try:
            current = str(content_root())
        except FileNotFoundError:
            current = read_config().get("content_root") or ""
        root_var = tk.StringVar(value=current)
        folder_row = ttk.Frame(advanced)
        folder_row.pack(fill="x")
        ttk.Entry(folder_row, textvariable=root_var).pack(side="left", fill="x", expand=True)

        def save_root():
            folder = root_var.get().strip()
            path = Path(folder).expanduser()
            if not is_content_pack(path):
                content_line.set(
                    "That folder needs skills/ and calcs/fp/formulas.py. The current pack was left as it is."
                )
                return
            remember_selected_root(str(path))
            try:
                resolved = content_root()
            except FileNotFoundError as exc:
                content_line.set(str(exc))
                return
            self.content_status.set(content_status_line())
            if self._settings_version is not None:
                self._settings_version.set(f"Content version: {content_version_text()}")
            if os.environ.get("FPFA_CONTENT_ROOT"):
                content_line.set(f"Saved {path}. This run uses {resolved} because FPFA_CONTENT_ROOT is set.")
            else:
                content_line.set(f"Content pack: {resolved}")

        ttk.Button(folder_row, text="Save content pack", command=save_root).pack(side="left", padx=(px(8), 0))
        key_entry.focus_set()

    def load_demo(self) -> None:
        """Create the sample job and run the local tool plan. Does not call Claude."""
        write_config({"key_backend": "file"})
        self.ask_claude.set(False)
        self.start_sample_di()


def capture_window(root: tk.Tk, path: Path) -> None:
    """Save a PNG of this window. Used by --demo where ImageMagick is installed."""
    import subprocess

    root.deiconify()
    root.lift()
    try:
        root.state("zoomed")
    except tk.TclError:
        pass
    root.update_idletasks()
    root.update()
    path.parent.mkdir(parents=True, exist_ok=True)
    window = hex(int(root.winfo_id()))
    try:
        subprocess.run(
            ["import", "-window", window, str(path)],
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="fpfa")
    parser.add_argument("--demo", action="store_true", help="Load the sample DI zone and run the tool plan")
    parser.add_argument("--quit", action="store_true", help="With --demo, exit after the run and screenshots")
    parser.add_argument("--screenshot-dir", default="", help="With --demo, write zone and results PNGs here")
    parser.add_argument("--export", default="", help="With --demo, write the draft .docx here")
    args = parser.parse_args(argv)

    if args.demo:
        # Skip the OS keyring probe. The demo never calls Claude.
        write_config({"key_backend": "file"})
    # Crisp text on a scaled Windows display. Must run before the first window.
    enable_windows_dpi_awareness()
    root = tk.Tk()
    app = App(root)
    if args.demo:
        def finish_demo():
            app.load_demo()
            root.update_idletasks()
            root.update()
            shot = Path(args.screenshot_dir) if args.screenshot_dir else None
            if shot:
                app.show_details(True)
                app.tabs.select(1)
                root.update()
                capture_window(root, shot / "di_zone_inputs.png")
                app.tabs.select(2)
                root.update()
                capture_window(root, shot / "di_zone_results.png")
            if args.export:
                try:
                    app.export_to(Path(args.export))
                except RuntimeError as exc:
                    sys.stderr.write(str(exc) + "\n")
            if args.quit:
                root.destroy()

        root.after(200, finish_demo)
    root.mainloop()


if __name__ == "__main__":
    main()
