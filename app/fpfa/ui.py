"""Desktop shell. The chat thread is the main pane. The zone form is optional.

Long zone runs and chat turns are jobs on the inbox. Workers run them so the
composer stays usable. A result is labeled with its job and stored on the
project that started it.

Run from the app directory: python -m fpfa
"""

from __future__ import annotations

import argparse
import copy
import json
import queue
import re
import threading
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from fpfa import sample_data
from fpfa.calc_tools import ToolSession
from fpfa.claude_client import MODEL_ID, AnthropicMessages, run_tool_loop, safe_error
from fpfa.everyday import run_everyday
from fpfa.jobs import JobInbox, label_result
from fpfa.keystore import clear_api_key, key_status, key_storage_help, load_api_key, save_api_key
from fpfa.modes_loader import DEFAULT_MODE, MODE_SLUGS, list_modes, normalize_mode
from fpfa.paths import content_root, read_config, write_config
from fpfa.projects import delete_project, list_projects, load_project, new_project, save_project
from fpfa.spec_docx import DRAFT_SECTION, write_docx
from fpfa.workflow import (
    form_assumption_lines,
    format_transcript,
    govern_note,
    judgment_label_line,
    run_di_zone,
    screen_limit_assumption_text,
    trim_assumption_text,
)


def format_chat_request(prior_turns: list[dict], basis: dict, di: dict, latest: str) -> str:
    """One user message that carries the form and the project's earlier chat turns."""
    lines = []
    for turn in prior_turns:
        who = "Designer" if turn.get("role") == "user" else "Assistant"
        lines.append(f"{who}: {turn.get('text') or ''}")
    history = "\n\n".join(lines) if lines else "(none)"
    return (
        "Project basis and the current zone form follow. "
        "Use tools for any gallons, seconds, gpm, or releasing logic. "
        "Earlier chat turns are included so a follow-up can refer to them.\n"
        f"basis={basis}\nzone={di}\n\n"
        f"Earlier turns:\n{history}\n\n"
        f"Designer: {latest}"
    )


def chat_request_text(
    prior_turns: list[dict],
    basis: dict,
    di: dict,
    latest: str,
    last_run: dict | None = None,
    mode: str | None = None,
) -> str:
    """Everyday-path request. A finished tool plan is repeated so chat cannot replace it."""
    text = format_chat_request(prior_turns, basis, di, latest)
    slug = normalize_mode(mode)
    head = f"Active mode: {slug}."
    note = govern_note(last_run)
    parts = [head, text]
    if note:
        parts.append(note)
    return "\n\n".join(parts)


_SLASH_ALIASES = {
    "sample_di": "sample-di",
    "sampledi": "sample-di",
}

THREAD_HINT = (
    "This thread is the main surface. Ask a question, or start from the sample zone.\n\n"
    "Sample DI (the chip below, or /sample-di) loads the sample data-hall double-interlock "
    "zone and runs the tool plan on this machine. That run does not need an API key.\n"
    "/run uses the optional zone form. /new Job name opens a job. /help lists commands.\n"
    "Ctrl+S saves the open job. Closing the window saves it too.\n"
    "Settings holds your Anthropic key. Export writes draft Section 21 13 19 after a run.\n"
    "Blank trim and the screen-limit seconds stay labeled ASSUMED. "
    "Pipe gallons and trip time come from the calc tools.\n"
    "A typed question uses the everyday path. Specialist roles, modes, and skills are files "
    "in the content pack, and numbers come from the calc tools.\n"
    "The Mode menu points at modes/<slug>/MODE.md "
    "(brainstorm, calculator, synthesis, mixed). "
    "Calculated, ASSUMED, and use best judgment stay three different labels.\n"
    "The inbox beside Projects lists zone runs and chat turns. "
    "A long job runs on a worker, so this composer stays usable. "
    "A result is labeled with the job it belongs to and is saved on that project."
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
        "The chat thread is the main surface. The zone form is optional.\n"
        "/sample-di — load the sample data-hall double-interlock zone and run the tool plan\n"
        "/run — run the DI zone from the optional form\n"
        "/new Job name — open a job\n"
        "/help — show these commands\n"
        "Ctrl+S saves the open job. Closing the window saves it too.\n"
        "Settings holds your Anthropic key. Export writes draft Section "
        f"{DRAFT_SECTION} after a run.\n"
        "/mode — show the active mode\n"
        "/mode brainstorm — use that mode file (also calculator, synthesis, mixed)\n"
        "Blank trim and the screen-limit seconds stay labeled ASSUMED. "
        "Pipe gallons and trip time come from the calc tools.\n"
        "A designer judgment the tools did not return is use best judgment. "
        "That label is not ASSUMED and it is not a calculated figure.\n"
        "A typed question uses the everyday path. Specialist roles, modes, and skills are files "
        "in the content pack, and numbers come from the calc tools.\n"
        "The inbox beside Projects lists zone runs and chat turns. "
        "A long job runs on a worker. The composer stays usable. "
        "A finished result is labeled with the job it belongs to and is saved on that project."
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
        self.project: dict | None = None
        self.chat_log: list[dict] = []
        self._ids: list[str] = []
        self._announce_runs: set[str] = set()
        self.jobs: JobInbox | None = None
        self._build()
        self.jobs = JobInbox(worker_count=2, on_change=self._on_jobs_changed)
        try:
            self._pristine_basis = self.collect_basis()
            self._pristine_di = self.collect_di()
        except ValueError:
            self._pristine_basis = None
            self._pristine_di = None
        self.refresh_projects()
        self.root.bind("<Destroy>", self._cancel_afters, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        for sequence in ("<Control-s>", "<Control-S>", "<Command-s>", "<Command-S>"):
            self.root.bind_all(sequence, self._on_save_key)
        self.root.after(100, self._poll)

    def _cancel_afters(self, event=None) -> None:
        if event is not None and event.widget is not self.root:
            return
        for sequence in ("<Control-s>", "<Control-S>", "<Command-s>", "<Command-S>"):
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
            jobs.close()

    def _on_save_key(self, event=None):
        try:
            if event is not None and event.widget.winfo_toplevel() is not self.root:
                return
        except tk.TclError:
            return
        self.save_current()
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
        default = tkfont.nametofont("TkDefaultFont")
        default.configure(size=11)
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=11)
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        header = tk.Frame(self.root, bg="#1f3b4d")
        header.pack(fill="x")
        titles = tk.Frame(header, bg="#1f3b4d")
        titles.pack(side="left", fill="x", expand=True)
        tk.Label(
            titles,
            text="FP/FA Design Assistant",
            bg="#1f3b4d",
            fg="white",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(
            titles,
            text=f"Chat first    ·    wet, dry, and double-interlock    ·    {MODEL_ID}",
            bg="#1f3b4d",
            fg="#d6e2ea",
            font=("TkDefaultFont", 10),
        ).pack(anchor="w", padx=14, pady=(0, 10))
        actions = tk.Frame(header, bg="#1f3b4d")
        actions.pack(side="right", padx=12, pady=10)
        ttk.Button(actions, text="Settings", command=self.open_settings).pack(side="left", padx=4)
        ttk.Button(actions, text=f"Export {DRAFT_SECTION}", command=self.export_docx).pack(side="left", padx=4)

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, padding=8)
        body.add(left, weight=0)
        ttk.Label(left, text="Projects").pack(anchor="w")
        self.project_list = tk.Listbox(left, width=26, height=18, exportselection=False)
        self.project_list.pack(fill="both", expand=True, pady=6)
        self.project_list.bind("<<ListboxSelect>>", self._on_select)
        buttons = ttk.Frame(left)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="New", command=self.new_job).pack(side="left", padx=(0, 4))
        ttk.Button(buttons, text="Delete", command=self.delete_job).pack(side="left", padx=4)
        ttk.Label(left, text="Inbox").pack(anchor="w", pady=(10, 0))
        self.inbox_list = tk.Listbox(left, width=26, height=7, exportselection=False)
        self.inbox_list.pack(fill="x", pady=(4, 0))
        ttk.Label(
            left,
            text="Workers run long jobs. A result stays on the job that started it.",
            wraplength=210,
        ).pack(anchor="w", pady=(4, 0))

        right = ttk.Panedwindow(body, orient="vertical")
        body.add(right, weight=1)
        self.main_pane = right

        chat_wrap = ttk.Frame(right, padding=(4, 8, 8, 4))
        right.add(chat_wrap, weight=4)
        self._build_chat(chat_wrap)

        zone_wrap = ttk.Frame(right, padding=(4, 0, 8, 8))
        right.add(zone_wrap, weight=1)
        ttk.Label(
            zone_wrap,
            text="Optional zone form. Chat, Sample DI, and /sample-di do not require filling this in.",
        ).pack(anchor="w")
        self.assumption_text = tk.StringVar()
        ttk.Label(
            zone_wrap,
            textvariable=self.assumption_text,
            wraplength=980,
            justify="left",
        ).pack(anchor="w", pady=(2, 4))
        self.tabs = ttk.Notebook(zone_wrap)
        self.tabs.pack(fill="both", expand=True)
        self._build_basis()
        self._build_zone()
        self._build_results()
        self.tabs.select(1)

        bar = ttk.Frame(self.root, padding=(10, 4))
        bar.pack(fill="x")
        self.status = tk.StringVar(value=key_status())
        ttk.Label(bar, textvariable=self.status).pack(anchor="w")
        self._sync_claude_default()
        self.root.after(200, self._prefer_chat)

    def _labeled(self, parent, text, variable, width=18, row=0, column=0):
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=4, pady=3)
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=4, pady=3)
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
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=4, pady=3)
        box = ttk.Combobox(parent, textvariable=variable, values=values, width=width, state="readonly")
        box.grid(row=row, column=column + 1, sticky="ew", padx=4, pady=3)
        return box

    def _build_basis(self) -> None:
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Basis")
        self.ahj = tk.StringVar()
        self.nfpa_13 = tk.StringVar(value="2025")
        self.nfpa_72 = tk.StringVar(value="2025")
        self.insurer = tk.StringVar(value="FM")
        self._labeled(tab, "AHJ", self.ahj, width=42, row=0, column=0)
        self._labeled(tab, "NFPA 13 edition", self.nfpa_13, row=1, column=0)
        self._labeled(tab, "NFPA 72 edition", self.nfpa_72, row=2, column=0)
        self._labeled(tab, "Insurer", self.insurer, row=3, column=0)
        ttk.Label(tab, text="Hazard notes").grid(row=4, column=0, sticky="nw", padx=4, pady=3)
        self.hazard_notes = tk.Text(tab, height=8, wrap="word")
        self.hazard_notes.grid(row=4, column=1, sticky="nsew", padx=4, pady=3)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(4, weight=1)
        ttk.Label(
            tab,
            text="Scope of this prototype: wet, dry, and double-interlock preaction, plus the detection and releasing that trip them.",
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def _build_zone(self) -> None:
        tab = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(tab, text="DI zone")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        for column in (1, 3, 5):
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

        self._labeled(form, "Zone", self.zone_id, width=16, row=0, column=0)
        self._combo(form, "System", self.system_label, [label for label, _ in SYSTEM_CHOICES], 0, 2, width=16)
        self._combo(form, "Hazard", self.hazard, HAZARDS, 0, 4, width=12)
        self._labeled(form, "Density", self.density, width=10, row=1, column=0)
        self._labeled(form, "Base area ft2", self.base_area, width=10, row=1, column=2)
        self._labeled(form, "Area increase", self.area_increase, width=8, row=1, column=4)
        self._labeled(form, "Hose gpm", self.hose, width=10, row=2, column=0)
        self._labeled(form, "Fill gpm", self.q_fill, width=10, row=2, column=2)
        self._combo(form, "Time basis", self.delivery_basis, BASES, 2, 4, width=12)
        self._labeled(form, "t detect s", self.t_detect, width=10, row=3, column=0)
        self._labeled(form, "t release s", self.t_release, width=10, row=3, column=2)
        self._labeled(form, "t exhaust s", self.t_exhaust, width=8, row=3, column=4)
        self._combo(form, "Medium", self.medium, MEDIA, 4, 0, width=16)
        self._combo(form, "Prime held by", self.prime, PRIMES, 4, 2, width=18)
        self._labeled(form, "Low-air psi", self.supervisory_psi, width=8, row=4, column=4)
        self._combo(form, "Lengths", self.length_label, [label for label, _ in LENGTHS], 5, 0, width=18)
        self._labeled(form, "Fittings %", self.fittings, width=10, row=5, column=2)
        self._labeled(form, "Trim gal", self.trim_gal, width=8, row=5, column=4)
        self.trim_gal.trace_add("write", lambda *_args: self._refresh_assumptions())
        self.delivery_basis.trace_add("write", lambda *_args: self._refresh_assumptions())
        self._refresh_assumptions()
        self._labeled(form, "Supervisory psig", self.supervisory_psig, width=10, row=6, column=0)
        self._labeled(form, "Fill minutes", self.fill_minutes, width=10, row=6, column=2)
        checks = ttk.Frame(form)
        checks.grid(row=7, column=0, columnspan=6, sticky="w", padx=4)
        ttk.Checkbutton(checks, text="Supervised waterflow", variable=self.supervised).pack(side="left")
        ttk.Checkbutton(checks, text="Quick-opening device", variable=self.qod).pack(side="left", padx=8)
        ttk.Checkbutton(checks, text="Manual station", variable=self.manual_station).pack(side="left", padx=8)
        ttk.Checkbutton(checks, text="Failsafe on total power loss", variable=self.failsafe).pack(side="left", padx=8)

        pipes = ttk.LabelFrame(tab, text="Pipe segments", padding=6)
        pipes.pack(fill="both", expand=True, pady=(8, 0))
        columns = ("role", "nps", "schedule", "length_ft", "d_in")
        self.pipes = ttk.Treeview(pipes, columns=columns, show="headings", height=8)
        headings = {
            "role": "Role",
            "nps": "NPS",
            "schedule": "Schedule",
            "length_ft": "Length ft",
            "d_in": "ID in",
        }
        widths = {"role": 90, "nps": 70, "schedule": 90, "length_ft": 90, "d_in": 80}
        for key, title in headings.items():
            self.pipes.heading(key, text=title)
            self.pipes.column(key, width=widths[key], minwidth=60, anchor="w", stretch=True)
        self.pipes.pack(fill="both", expand=True)
        add = ttk.Frame(pipes)
        add.pack(fill="x", pady=6)
        self.seg_role = tk.StringVar(value="branch")
        self.seg_nps = tk.StringVar()
        self.seg_schedule = tk.StringVar()
        self.seg_length = tk.StringVar()
        ttk.Label(add, text="Role").pack(side="left")
        ttk.Combobox(
            add, textvariable=self.seg_role, width=10, state="readonly",
            values=("branch", "drop", "cross", "main", "feed", "riser"),
        ).pack(side="left", padx=4)
        ttk.Label(add, text="NPS").pack(side="left")
        ttk.Entry(add, textvariable=self.seg_nps, width=8).pack(side="left", padx=4)
        ttk.Label(add, text="Schedule").pack(side="left")
        ttk.Entry(add, textvariable=self.seg_schedule, width=8).pack(side="left", padx=4)
        ttk.Label(add, text="Length ft").pack(side="left")
        ttk.Entry(add, textvariable=self.seg_length, width=8).pack(side="left", padx=4)
        ttk.Button(add, text="Add segment", command=self.add_segment).pack(side="left", padx=6)
        ttk.Button(add, text="Remove", command=self.remove_segment).pack(side="left")
        ttk.Label(
            pipes,
            text=(
                "Blank schedule uses the shop default (branch and under 2 in = sch 40, mains and cross 2 in and up = sch 10). "
                "The ID comes from the calc pack. Blank fittings follow the length basis. "
                "Blank trim is ASSUMED 5 gal (no valve data sheet), not calculated. "
                "The screen-limit seconds are ASSUMED from the time basis lookup, not calculated. "
                "A judgment the tools did not return is use best judgment, not ASSUMED and not calculated."
            ),
            wraplength=720,
        ).pack(anchor="w")

    def _build_results(self) -> None:
        tab = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(tab, text="Results")
        ttk.Label(
            tab,
            text=(
                "Figures in this view come from the tool plan on the form. "
                "Pipe gallons and t_total are calculated. "
                "Blank trim and the screen-limit seconds are marked ASSUMED. "
                "A judgment the tools did not return is use best judgment. "
                "A delivery time here is an optimistic screen, not a listed water-delivery-time calculation."
            ),
            wraplength=900,
        ).pack(anchor="w", pady=(0, 6))
        self.results = tk.Text(tab, wrap="word")
        scroll = ttk.Scrollbar(tab, command=self.results.yview)
        self.results.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.results.pack(fill="both", expand=True)

    def _build_chat(self, parent) -> None:
        chips = ttk.Frame(parent)
        chips.pack(side="bottom", fill="x", pady=(4, 0))
        row = ttk.Frame(parent)
        row.pack(side="bottom", fill="x", pady=(6, 0))
        self.chat_entry = ttk.Entry(row)
        self.chat_entry.pack(side="left", fill="x", expand=True)
        self.chat_entry.bind("<Return>", lambda _event: self.send_chat())
        self.send_button = ttk.Button(row, text="Send", command=self.send_chat)
        self.send_button.pack(side="left", padx=6)
        self.chat_view = tk.Text(parent, wrap="word", state="disabled", padx=8, pady=8, height=16)
        self.chat_view.tag_configure("hint", foreground="#5c6b76")
        scroll = ttk.Scrollbar(parent, command=self.chat_view.yview)
        self.chat_view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat_view.pack(side="left", fill="both", expand=True)
        self.sample_di_button = ttk.Button(chips, text="Sample DI", command=self.start_sample_di)
        self.sample_di_button.pack(side="left")
        ttk.Label(chips, text="Mode").pack(side="left", padx=(12, 4))
        self.mode_slug = tk.StringVar(value=DEFAULT_MODE)
        self.mode_box = ttk.Combobox(
            chips,
            textvariable=self.mode_slug,
            width=12,
            state="readonly",
        )
        self.mode_box.pack(side="left")
        self._apply_mode(DEFAULT_MODE)
        ttk.Label(chips, text="/sample-di    /run    /mode    /help").pack(side="left", padx=8)
        self.ask_claude = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            chips,
            text="Ask Claude after the tool plan (your key; numbers stay from the calcs)",
            variable=self.ask_claude,
        ).pack(side="right")
        self._render_chat()

    def _prefer_chat(self) -> None:
        """Keep the thread larger than the optional zone form and ready to type into."""
        try:
            self.chat_entry.focus_set()
            height = self.main_pane.winfo_height()
            if height > 160:
                self.main_pane.sashpos(0, int(height * 0.68))
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
            lines = [job.inbox_line() for job in jobs.snapshot()]
            if tuple(listing.get(0, "end")) == tuple(lines):
                return
            listing.delete(0, "end")
            for line in lines:
                listing.insert("end", line)
            if lines:
                listing.see("end")
        except tk.TclError:
            return

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
        self.ask_claude.set(bool(load_api_key()))

    def refresh_projects(self, select_id: str | None = None) -> None:
        self.project_list.delete(0, "end")
        self._ids = []
        for row in list_projects():
            self.project_list.insert("end", row.get("name") or "Untitled job")
            self._ids.append(row["id"])
        if select_id and select_id in self._ids:
            index = self._ids.index(select_id)
            self.project_list.selection_set(index)
            self.project_list.see(index)

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
        self._show_saved_run(project.get("last_run"))
        self._apply_mode(project.get("mode"))

    def _known_modes(self) -> list[str]:
        try:
            found = [item["slug"] for item in list_modes(content_root())]
        except FileNotFoundError:
            found = []
        return found or list(MODE_SLUGS)

    def _apply_mode(self, slug: str | None) -> None:
        known = self._known_modes()
        self.mode_box["values"] = known
        chosen = normalize_mode(slug)
        if chosen not in known:
            chosen = DEFAULT_MODE if DEFAULT_MODE in known else known[0]
        self.mode_slug.set(chosen)

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

    def new_job(self) -> None:
        name = simpledialog.askstring("New job", "Job name", parent=self.root)
        if not name:
            return
        self._start_named_job(name)

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
        self._announce_runs.add(self.project["id"])
        self.run_zone()

    def start_zone_run(self, typed: str | None = None) -> None:
        raw = (typed or "/run").strip() or "/run"
        self._keep_composer_open()
        self._ensure_project()
        self._append_chat("user", raw)
        self._announce_runs.add(self.project["id"])
        self.run_zone()

    def _slash_new(self, raw: str, name: str) -> None:
        name = name.strip()
        if not name:
            self._local_exchange(raw, "Usage: /new Job name")
            return
        self._start_named_job(name)
        self._append_chat("user", raw)
        self._append_chat(
            "assistant",
            f"Opened {self.project['name']}. The zone form is optional. /sample-di loads the sample zone and runs it.",
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
        elif command == "run":
            self.start_zone_run(raw)
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

    def delete_job(self) -> None:
        project_id = self._selected_id()
        if not project_id:
            return
        if not messagebox.askyesno("Delete", "Delete this project from this machine?"):
            return
        delete_project(project_id)
        if self.project and self.project.get("id") == project_id:
            self.project = None
        self.refresh_projects()

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

    def run_zone(self) -> None:
        self._keep_composer_open()
        if not self.project:
            self._report_run_problem(None, "Open a project, or use /sample-di.")
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        try:
            self._write_form(self.project)
        except ValueError as exc:
            self._report_run_problem(origin_id, str(exc))
            return
        di = copy.deepcopy(self.project["di"])
        basis = copy.deepcopy(self.project["basis"])
        mode = self.mode_slug.get()
        try:
            pack = content_root()
        except FileNotFoundError as exc:
            self._report_run_problem(origin_id, str(exc))
            return
        use_claude = bool(self.ask_claude.get()) and bool(load_api_key())
        if use_claude:
            self._enqueue_zone(origin_id, project_name, pack, di, basis, mode, load_api_key())
            return
        self._run_zone_here(origin_id, project_name, pack, di, basis, mode)

    def _run_zone_here(self, origin_id, project_name, pack, di, basis, mode) -> None:
        """Tool plan with no model call. It finishes before the composer returns."""
        job = self.jobs.record(
            project_id=origin_id,
            project_name=project_name,
            kind="zone",
            title="Zone tool plan",
            status="running",
        )
        try:
            result = run_di_zone(pack, di, basis, narrator=None, mode=mode)
        except Exception as exc:
            self.jobs.mark(job.id, "error", safe_error(exc))
            self._report_run_problem(origin_id, safe_error(exc), job_id=job.id)
            return
        self.jobs.mark(job.id, "done")
        self._finish_run(origin_id, result, None, job_id=job.id)

    def _enqueue_zone(self, origin_id, project_name, pack, di, basis, mode, key) -> None:
        """Queue a zone run that calls the model. The composer stays usable."""

        def work(job_id: str) -> None:
            def narrator(system, user_text, tools, execute):
                client = AnthropicMessages(key)
                return run_tool_loop(
                    client.create,
                    system=system,
                    user_text=user_text,
                    tools=tools,
                    execute=execute,
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
                result = run_di_zone(pack, di, basis, narrator=narrator, mode=mode)
                error = None
            except Exception as exc:
                result = None
                error = safe_error(exc)
                self.jobs.mark(job_id, "error", error)
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
        self._keep_composer_open()
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def _report_run_problem(self, origin_id: str | None, message: str, job_id: str | None = None) -> None:
        self._keep_composer_open()
        announced_id = origin_id
        if origin_id:
            origin_id = self._destination_id(origin_id, job_id)
        announce = bool(announced_id) and announced_id in self._announce_runs
        if announced_id:
            self._announce_runs.discard(announced_id)
        if origin_id and origin_id != announced_id:
            announce = announce or origin_id in self._announce_runs
            self._announce_runs.discard(origin_id)
        message = self._with_job_label(job_id, message)
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

    def _take_announce(self, origin_id: str) -> bool:
        announce = origin_id in self._announce_runs
        self._announce_runs.discard(origin_id)
        return announce

    def _finish_run(
        self,
        origin_id: str,
        result: dict | None,
        error: str | None,
        job_id: str | None = None,
    ) -> None:
        self._keep_composer_open()
        announced_id = origin_id
        origin_id = self._destination_id(origin_id, job_id)
        announce = self._take_announce(announced_id)
        if origin_id != announced_id:
            announce = announce or self._take_announce(origin_id)
        still_here = self.project is not None and self.project.get("id") == origin_id
        if error or result is None:
            message = self._with_job_label(job_id, error or "The zone did not run.")
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
        summary = self._with_job_label(job_id, chat_run_summary(result)) if announce else ""
        if still_here:
            self.project["last_run"] = result
            if summary:
                self.chat_log.append(self._assistant_turn(summary, job_id))
                self._render_chat()
            form_error = self._save_form_or_chat(self.project)
            save_project(self.project)
            self._show_result(result)
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
        elif result["source"] == "claude":
            note = f"Tool plan plus {MODEL_ID}. Tables and Section {DRAFT_SECTION} use the tool plan."
            if result.get("warnings"):
                note = note + " " + result["warnings"][0]
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
        if result:
            self._show_result(result)
        else:
            self.results.insert(
                "1.0",
                "The thread is where a zone run shows up. "
                "This panel keeps the tool-plan figures after /sample-di or /run, for export.",
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

    def export_to(self, path: Path) -> Path:
        if not self.project or not self.project.get("last_run"):
            raise RuntimeError("Run /sample-di or /run before exporting.")
        return write_docx(path, self.project, self.project["last_run"])

    def export_docx(self) -> None:
        if not self.project or not self.project.get("last_run"):
            messagebox.showinfo("Export", "Use /sample-di or /run before exporting.")
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Export draft Section {DRAFT_SECTION}",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx")],
            initialfile=f"{self.project.get('name', 'di-zone')}.docx",
        )
        if not path:
            return
        try:
            written = self.export_to(Path(path))
        except Exception as exc:
            messagebox.showerror("Export", safe_error(exc))
            return
        self.status.set(f"Exported {written}")

    def _render_chat(self) -> None:
        self.chat_view.configure(state="normal")
        self.chat_view.delete("1.0", "end")
        if not self.chat_log:
            self.chat_view.insert("end", THREAD_HINT + "\n", "hint")
        for turn in self.chat_log:
            who = "You" if turn.get("role") == "user" else "Assistant"
            self.chat_view.insert("end", f"{who}\n{turn.get('text') or ''}\n\n")
        self.chat_view.configure(state="disabled")
        self.chat_view.see("end")

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
        origin_id = self.project["id"]
        project_name = self.project.get("name") or "Untitled job"
        self._append_chat("user", text)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass
        key = load_api_key()
        if not key:
            self._append_chat(
                "assistant",
                "Save an Anthropic API key in Settings to talk with Claude. "
                "/sample-di still loads the sample zone and runs the tool plan on this machine without a key.",
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
        request = chat_request_text(prior, basis, di, text, self.project.get("last_run"), mode)
        if form_note:
            request = form_note + "\n\n" + request

        def work(job_id: str) -> None:
            try:
                pack = content_root()
                client = AnthropicMessages(key)
                out = run_everyday(pack, client.create, request, mode=mode)
                reply = out.get("text") or "(Claude returned no text.)"
            except Exception as exc:
                reply = safe_error(exc)
                self.jobs.mark(job_id, "error", reply)
            self.queue.put(
                lambda oid=origin_id, answer=reply, jid=job_id: self._finish_chat(oid, answer, job_id=jid)
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

    def _finish_chat(self, origin_id: str, reply: str, job_id: str | None = None) -> None:
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
            self.status.set(form_error or self._with_job_label(job_id, note))
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

    def open_settings(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.geometry("680x460")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=f"Model  {MODEL_ID}").pack(anchor="w")
        ttk.Label(
            frame,
            text="Paste your own Anthropic API key. It stays on this machine and is not written into the project.",
            wraplength=580,
        ).pack(anchor="w", pady=(8, 4))
        ttk.Label(frame, text=key_storage_help(), wraplength=580).pack(anchor="w", pady=(0, 4))
        key_var = tk.StringVar()
        ttk.Entry(frame, textvariable=key_var, show="•", width=60).pack(anchor="w", fill="x")
        status = tk.StringVar(value=key_status())
        ttk.Label(frame, textvariable=status, wraplength=580).pack(anchor="w", pady=6)

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
            self.status.set(key_status())

        def clear():
            clear_api_key()
            key_var.set("")
            status.set(key_status())
            self.ask_claude.set(False)
            self.status.set(key_status())

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

        row = ttk.Frame(frame)
        row.pack(anchor="w", pady=4)
        ttk.Button(row, text="Save key", command=save).pack(side="left")
        ttk.Button(row, text="Clear key", command=clear).pack(side="left", padx=6)
        ttk.Button(row, text="Check key", command=check).pack(side="left")

        ttk.Label(
            frame,
            text="Content pack folder (skills/, roles/, modes/, and calcs/ at the top level)",
        ).pack(anchor="w", pady=(16, 4))
        try:
            current = str(content_root())
        except FileNotFoundError:
            current = read_config().get("content_root") or ""
        root_var = tk.StringVar(value=current)
        ttk.Entry(frame, textvariable=root_var, width=70).pack(anchor="w", fill="x")

        def save_root():
            folder = root_var.get().strip()
            write_config({"content_root": folder})
            try:
                resolved = content_root()
            except FileNotFoundError as exc:
                status.set(str(exc))
                return
            status.set(f"Content pack: {resolved}")

        ttk.Button(frame, text="Save content pack", command=save_root).pack(anchor="w", pady=8)

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
    root = tk.Tk()
    app = App(root)
    if args.demo:
        def finish_demo():
            app.load_demo()
            root.update_idletasks()
            root.update()
            shot = Path(args.screenshot_dir) if args.screenshot_dir else None
            if shot:
                app.tabs.select(1)
                root.update()
                capture_window(root, shot / "di_zone_inputs.png")
                app.tabs.select(2)
                root.update()
                capture_window(root, shot / "di_zone_results.png")
            if args.export:
                app.export_to(Path(args.export))
            if args.quit:
                root.destroy()

        root.after(200, finish_demo)
    root.mainloop()


if __name__ == "__main__":
    main()
