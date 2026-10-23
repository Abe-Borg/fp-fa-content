"""Desktop shell. Projects, basis of design, one DI zone, chat, and settings.

Run from the app directory: python -m fpfa
"""

from __future__ import annotations

import argparse
import copy
import queue
import threading
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from fpfa import sample_data
from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import MODEL_ID, AnthropicMessages, run_tool_loop, safe_error
from fpfa.keystore import clear_api_key, key_status, load_api_key, save_api_key
from fpfa.paths import content_root, read_config, write_config
from fpfa.projects import delete_project, list_projects, load_project, new_project, save_project
from fpfa.spec_docx import write_docx
from fpfa.workflow import format_transcript, run_di_zone, system_prompt

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
            pass
        self.queue: queue.Queue = queue.Queue()
        self.project: dict | None = None
        self.chat_log: list[dict] = []
        self._ids: list[str] = []
        self._busy = False
        self._build()
        self.refresh_projects()
        self.root.after(100, self._poll)

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
        tk.Label(
            header,
            text="FP/FA Design Assistant",
            bg="#1f3b4d",
            fg="white",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(
            header,
            text=f"Wet, dry, and double-interlock preaction    ·    {MODEL_ID}",
            bg="#1f3b4d",
            fg="#d6e2ea",
            font=("TkDefaultFont", 10),
        ).pack(anchor="w", padx=14, pady=(0, 10))

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, padding=8)
        body.add(left, weight=0)
        ttk.Label(left, text="Projects").pack(anchor="w")
        self.project_list = tk.Listbox(left, width=32, height=24, exportselection=False)
        self.project_list.pack(fill="both", expand=True, pady=6)
        self.project_list.bind("<<ListboxSelect>>", self._on_select)
        buttons = ttk.Frame(left)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="New", command=self.new_job).pack(side="left", padx=(0, 4))
        ttk.Button(buttons, text="Sample DI job", command=self.new_sample).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete", command=self.delete_job).pack(side="left", padx=4)
        ttk.Button(buttons, text="Settings", command=self.open_settings).pack(side="right")

        right = ttk.Frame(body, padding=(4, 8, 8, 8))
        body.add(right, weight=1)
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)
        self._build_basis()
        self._build_zone()
        self._build_results()
        self._build_chat()

        bar = ttk.Frame(self.root, padding=(10, 6))
        bar.pack(fill="x")
        self.ask_claude = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            bar,
            text="Ask Claude after the tool plan",
            variable=self.ask_claude,
        ).pack(side="left")
        ttk.Button(bar, text="Run DI zone", command=self.run_zone).pack(side="left", padx=8)
        ttk.Button(bar, text="Export .docx", command=self.export_docx).pack(side="left")
        ttk.Button(bar, text="Save project", command=self.save_current).pack(side="left", padx=8)
        self.status = tk.StringVar(value=key_status())
        ttk.Label(bar, textvariable=self.status).pack(side="left", padx=12)
        self._sync_claude_default()

    def _labeled(self, parent, text, variable, width=18, row=0, column=0):
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=4, pady=3)
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=4, pady=3)
        return entry

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
                "The ID comes from the calc pack. Blank fittings follow the length basis. Blank trim is 5 gal, assumed."
            ),
            wraplength=720,
        ).pack(anchor="w")

    def _build_results(self) -> None:
        tab = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(tab, text="Results")
        ttk.Label(
            tab,
            text="Figures in this view come from the tool plan on the form. A delivery time here is an optimistic screen, not a listed water-delivery-time calculation.",
            wraplength=900,
        ).pack(anchor="w", pady=(0, 6))
        self.results = tk.Text(tab, wrap="word")
        scroll = ttk.Scrollbar(tab, command=self.results.yview)
        self.results.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.results.pack(fill="both", expand=True)

    def _build_chat(self) -> None:
        tab = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(tab, text="Chat")
        self.chat_view = tk.Text(tab, wrap="word", state="disabled")
        scroll = ttk.Scrollbar(tab, command=self.chat_view.yview)
        self.chat_view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat_view.pack(fill="both", expand=True)
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=(6, 0))
        self.chat_entry = ttk.Entry(row)
        self.chat_entry.pack(side="left", fill="x", expand=True)
        self.chat_entry.bind("<Return>", lambda _event: self.send_chat())
        ttk.Button(row, text="Send", command=self.send_chat).pack(side="left", padx=6)

    def _poll(self) -> None:
        try:
            while True:
                callback = self.queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

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
        if self.project and self.project.get("id") != project_id:
            self._write_form(self.project)
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

    def _write_form(self, project: dict) -> None:
        project["basis"] = self.collect_basis()
        project["di"] = self.collect_di()
        project["chat"] = self.chat_log

    def save_current(self) -> None:
        if not self.project:
            messagebox.showinfo("Save", "Create or open a project first.")
            return
        try:
            self._write_form(self.project)
        except ValueError as exc:
            messagebox.showerror("Save", str(exc))
            return
        save_project(self.project)
        self.refresh_projects(self.project["id"])
        self.status.set(f"Saved {self.project['name']}.")

    def new_job(self) -> None:
        name = simpledialog.askstring("New job", "Job name", parent=self.root)
        if not name:
            return
        if self.project:
            self._write_form(self.project)
            save_project(self.project)
        project = new_project(name)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])

    def new_sample(self) -> None:
        if self.project:
            self._write_form(self.project)
            save_project(self.project)
        project = new_project("Sample data hall DI zone", copy.deepcopy(sample_data.EXAMPLE_BASIS))
        project["di"] = copy.deepcopy(sample_data.EXAMPLE_DI)
        save_project(project)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])
        self.tabs.select(1)
        self.status.set("Sample DI zone loaded. Run DI zone to compute it.")

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
        if self._busy:
            return
        if not self.project:
            messagebox.showinfo("DI zone", "Create or open a project first.")
            return
        try:
            self._write_form(self.project)
        except ValueError as exc:
            messagebox.showerror("DI zone", str(exc))
            return
        di = self.project["di"]
        basis = self.project["basis"]
        try:
            root = content_root()
        except FileNotFoundError as exc:
            messagebox.showerror("Content pack", str(exc))
            return
        use_claude = bool(self.ask_claude.get()) and bool(load_api_key())
        narrator = None
        if use_claude:
            key = load_api_key()

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
                )

        if use_claude:
            self._busy = True
            self.status.set("Running the tool plan, then Claude…")

            def work():
                try:
                    result = run_di_zone(root, di, basis, narrator=narrator)
                    error = None
                except Exception as exc:
                    result = None
                    error = safe_error(exc)
                self.queue.put(lambda: self._finish_run(result, error))

            threading.Thread(target=work, daemon=True).start()
            return
        try:
            result = run_di_zone(root, di, basis, narrator=None)
        except Exception as exc:
            messagebox.showerror("DI zone", safe_error(exc))
            self.status.set("The zone did not run.")
            return
        self._finish_run(result, None)

    def _finish_run(self, result: dict | None, error: str | None) -> None:
        self._busy = False
        if error or result is None:
            messagebox.showerror("DI zone", error or "The zone did not run.")
            self.status.set("The zone did not run.")
            return
        if self.project is not None:
            self.project["last_run"] = result
            self._write_form(self.project)
            save_project(self.project)
        self._show_result(result)
        self.tabs.select(2)
        if result["source"] == "claude":
            self.status.set(f"Tool plan plus {MODEL_ID}. Tables use the tool plan.")
        else:
            note = "Tool plan only."
            if self.ask_claude.get() and not load_api_key():
                note = "Tool plan only. Save an API key in Settings to ask Claude."
            elif result.get("warnings"):
                note = "Tool plan only. " + result["warnings"][0]
            self.status.set(note)

    def _show_saved_run(self, result: dict | None) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        if result:
            self._show_result(result)
        else:
            self.results.insert("1.0", "Run the DI zone to see the volume, delivery screen, trim, and releasing table.")
        self.results.configure(state="disabled")

    def _show_result(self, result: dict) -> None:
        tools = result["tools"]
        volume = tools["zone_trapped_volume"]
        trip = tools["di_trip_to_water"]
        trim = tools["elect_di_trim"]
        lines = [
            result.get("narrative") or "",
            "",
            "— Tool plan —",
            f"Zone {volume['zone_gal']:.1f} gal    t_total {trip['t_total_s']:.1f} s    "
            f"passes screen: {'yes' if trip['passes_screen'] else 'no'}    "
            f"trim: {trim.get('family') or trim.get('status')}",
            "",
            "Flags",
        ]
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
            raise RuntimeError("Run the DI zone before exporting.")
        return write_docx(path, self.project, self.project["last_run"])

    def export_docx(self) -> None:
        if not self.project or not self.project.get("last_run"):
            messagebox.showinfo("Export", "Run the DI zone before exporting.")
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export draft section",
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
        if not self.project:
            messagebox.showinfo("Chat", "Create or open a project first.")
            return
        self.chat_entry.delete(0, "end")
        self._append_chat("user", text)
        key = load_api_key()
        if not key:
            self._append_chat(
                "assistant",
                "Save an Anthropic API key in Settings to use chat. "
                "The DI zone tab still runs the tool plan on this machine without a key.",
            )
            self._write_form(self.project)
            save_project(self.project)
            return
        self.status.set(f"Asking {MODEL_ID}…")
        basis = self.collect_basis()
        di = self.collect_di()

        def work():
            try:
                root = content_root()
                client = AnthropicMessages(key)
                session = ToolSession(root)
                context = (
                    "Project basis and the current zone form follow. "
                    "Use tools for any gallons, seconds, gpm, or releasing logic.\n"
                    f"basis={basis}\nzone={di}\n\n{text}"
                )
                out = run_tool_loop(
                    client.create,
                    system=system_prompt(root),
                    user_text=context,
                    tools=SCHEMAS,
                    execute=session.execute,
                    required=[],
                )
                reply = out.get("text") or "(Claude returned no text.)"
            except Exception as exc:
                reply = safe_error(exc)
            self.queue.put(lambda: self._finish_chat(reply))

        threading.Thread(target=work, daemon=True).start()

    def _finish_chat(self, reply: str) -> None:
        self._append_chat("assistant", reply)
        if self.project:
            self._write_form(self.project)
            save_project(self.project)
        self.status.set("Chat updated.")

    def open_settings(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.geometry("640x360")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=f"Model  {MODEL_ID}").pack(anchor="w")
        ttk.Label(
            frame,
            text="Paste your own Anthropic API key. It stays on this machine and is not written into the project.",
            wraplength=580,
        ).pack(anchor="w", pady=(8, 4))
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

        ttk.Label(frame, text="Content pack folder (skills/ and calcs/ at the top level)").pack(anchor="w", pady=(16, 4))
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
        project = new_project("Sample data hall DI zone", copy.deepcopy(sample_data.EXAMPLE_BASIS))
        project["di"] = copy.deepcopy(sample_data.EXAMPLE_DI)
        save_project(project)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])
        self.run_zone()


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
