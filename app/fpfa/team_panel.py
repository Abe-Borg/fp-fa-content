"""The Team tab. Roster, blockers, and the handoff log, read from the project record.

The panel renders a Record.snapshot(). It holds no state of its own beyond
the last snapshot, so a refresh after any job is one call. Specialist
activity stays collapsed: the handoff table shows one line per exchange,
and the detail pane opens the brief, the payload, and the result for the
selected row.
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from fpfa import theme as palette

STATUS_GLYPH = {
    "working": "●",
    "done": "✓",
    "error": "!",
    "interrupted": "!",
    "idle": "·",
}
HANDOFF_GLYPH = {
    "pending": "…",
    "delivered": "→",
    "returned": "✓",
    "cancelled": "✕",
}
NO_TEAM_LINE = "No team activity on this job yet. Ask a question and the lead will delegate as needed."


def roster_lines(snapshot: dict | None) -> list[str]:
    """One line per agent: glyph, name, role, status, and what it has written."""
    snap = snapshot or {}
    agents = list(snap.get("agents") or [])
    if not agents:
        return []
    findings = {}
    questions = {}
    for row in snap.get("findings") or []:
        findings[row.get("agent")] = findings.get(row.get("agent"), 0) + 1
    for row in snap.get("questions") or []:
        questions[row.get("raised_by")] = questions.get(row.get("raised_by"), 0) + 1
    lines = []
    for row in agents:
        slug = row.get("role_slug") or ""
        glyph = STATUS_GLYPH.get(row.get("status") or "", "·")
        parts = [f"{glyph} {row.get('name') or slug} ({slug}) {row.get('status') or ''}"]
        count = findings.get(slug, 0)
        asked = questions.get(slug, 0)
        if count:
            parts.append(f"{count} finding{'s' if count != 1 else ''}")
        if asked:
            parts.append(f"{asked} question{'s' if asked != 1 else ''}")
        lines.append(" · ".join(parts))
    return lines


def blocker_lines(snapshot: dict | None) -> list[str]:
    snap = snapshot or {}
    lines = []
    for row in snap.get("questions") or []:
        if row.get("status") == "open":
            lines.append(f"? {row.get('text')} (raised by {row.get('raised_by')})")
    for row in snap.get("handoffs") or []:
        if row.get("status") == "pending":
            lines.append(f"… handoff waiting for {row.get('to_agent')}: {row.get('brief')}")
    for row in snap.get("findings") or []:
        if row.get("status") in ("Not supported", "Source not found"):
            lines.append(f"! finding {row.get('status').lower()}: {row.get('text')}")
    return lines


def check_line(snapshot: dict | None) -> str:
    snap = snapshot or {}
    latest = None
    for row in snap.get("events") or []:
        if row.get("kind") == "record_check":
            latest = row
    if latest is None:
        if snap.get("findings"):
            return "Blind check: not run on the current findings."
        return "Blind check: nothing to check yet."
    payload = latest.get("payload") or {}
    return str(payload.get("status_line") or "Blind check ran.")


def _short(text: Any, limit: int = 90) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _time(text: Any) -> str:
    text = str(text or "")
    return text[11:16] if len(text) >= 16 else text


class TeamPanel(ttk.Frame):
    def __init__(
        self,
        master,
        theme,
        *,
        on_cancel: Callable[[], None],
        on_check: Callable[[], None],
        on_export: Callable[[], None],
    ):
        px = theme.px
        super().__init__(master, padding=px(10))
        self.theme = theme
        self.snapshot: dict | None = None
        self._rows: dict[str, dict] = {}

        ttk.Label(
            self,
            text=(
                "The lead delegates to specialists. Each exchange is a row below. "
                "Select a row for its brief, payload, and result. Findings and questions live on the record, "
                "not in the thread."
            ),
            style="Small.TLabel",
            wraplength=px(400),
            justify="left",
        ).pack(anchor="w", pady=(0, px(6)))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", pady=(0, px(6)))
        self.cancel_button = ttk.Button(buttons, text="Cancel running job", command=on_cancel, state="disabled")
        self.cancel_button.pack(side="left")
        self.check_button = ttk.Button(buttons, text="Run blind check", command=on_check)
        self.check_button.pack(side="left", padx=(px(6), 0))
        ttk.Button(buttons, text="Export design basis…", command=on_export).pack(side="left", padx=(px(6), 0))

        ttk.Label(self, text="TEAM", style="Section.TLabel").pack(anchor="w")
        self.roster_text = self._text(height=4)
        self.roster_text.pack(fill="x", pady=(px(2), px(6)))

        ttk.Label(self, text="BLOCKERS AND OPEN QUESTIONS", style="Section.TLabel").pack(anchor="w")
        self.blockers_text = self._text(height=4)
        self.blockers_text.pack(fill="x", pady=(px(2), px(6)))

        ttk.Label(self, text="HANDOFFS", style="Section.TLabel").pack(anchor="w")
        columns = ("when", "from", "to", "status", "brief")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6, selectmode="browse")
        for name, title, width in (
            ("when", "When", 52), ("from", "From", 92), ("to", "To", 92), ("status", "Status", 70), ("brief", "Brief", 220),
        ):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=px(width), anchor="w", stretch=(name == "brief"))
        self.tree.pack(fill="x", pady=(px(2), px(4)))
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        ttk.Label(self, text="DETAIL", style="Section.TLabel").pack(anchor="w")
        self.detail = self._text(height=8)
        self.detail.pack(fill="both", expand=True, pady=(px(2), 0))

    def _text(self, *, height: int) -> tk.Text:
        px = self.theme.px
        widget = tk.Text(
            self,
            wrap="word",
            height=height,
            bd=0,
            relief="flat",
            highlightthickness=0,
            bg=palette.SURFACE,
            fg=palette.TEXT,
            padx=px(8),
            pady=px(6),
            font=self.theme.fonts["small"],
        )
        widget.configure(state="disabled")
        return widget

    def _set(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def render(self, snapshot: dict | None, *, running: bool = False) -> None:
        """Draw the snapshot. running enables the cancel button."""
        self.snapshot = snapshot
        roster = roster_lines(snapshot)
        self._set(self.roster_text, "\n".join(roster) if roster else NO_TEAM_LINE)
        blockers = blocker_lines(snapshot)
        text = "\n".join(blockers) if blockers else "None open."
        self._set(self.blockers_text, text + "\n" + check_line(snapshot))
        selected = self.tree.selection()
        keep = selected[0] if selected else None
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rows = {}
        for row in (snapshot or {}).get("handoffs") or []:
            glyph = HANDOFF_GLYPH.get(row.get("status") or "", "")
            item = self.tree.insert(
                "", "end", iid=row["id"],
                values=(_time(row.get("created")), row.get("from_agent"), row.get("to_agent"),
                        f"{glyph} {row.get('status')}", _short(row.get("brief"))),
            )
            self._rows[item] = row
        if keep and keep in self._rows:
            self.tree.selection_set(keep)
            self._show_detail(self._rows[keep])
        else:
            self._set(self.detail, "Select a handoff to read it.")
        self.cancel_button.configure(state="normal" if running else "disabled")

    def _on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        row = self._rows.get(selected[0])
        if row is not None:
            self._show_detail(row)

    def _show_detail(self, row: dict) -> None:
        payload = row.get("payload")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                pass
        lines = [
            f"[{row.get('id')}] {row.get('from_agent')} → {row.get('to_agent')}: {row.get('status')}",
            f"Created {row.get('created') or ''}. Delivered {row.get('delivered') or '—'}. Returned {row.get('returned') or '—'}.",
            "",
            "Brief:",
            str(row.get("brief") or ""),
        ]
        if payload:
            lines += ["", "Payload:", json.dumps(payload, indent=2, sort_keys=True, default=str)]
        if row.get("result"):
            lines += ["", "Result:", str(row.get("result"))]
        self._set(self.detail, "\n".join(lines))
