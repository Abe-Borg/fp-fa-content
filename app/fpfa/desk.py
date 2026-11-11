"""What the +Cynosure window knows and does, with no window toolkit.

The window is a web page (fpfa/web) drawn by the system's WebView2 control.
Everything the page shows comes from Desk.snapshot(), and everything the page
does is a Desk method the local server calls. The rules live here, not in
the page: which project a result lands on, what a slash command does, when
the export waits for the trace check, what the working line may say.

Threads. The server calls a method while it holds Desk.lock. Workers on the
job inbox never touch the desk directly: they put a callback on Desk.queue,
and pump() runs those callbacks under the same lock. A test drives a Desk on
its own thread and calls pump() itself.

Change. Every change bumps Desk.revision and wakes Desk.changed, which the
server's event stream waits on. The thread has its own revision, so the page
is sent the conversation only when it changed, and a reply that is still
arriving is sent as live text (Desk.lives), word by word.

Run from the app directory: python -m fpfa
"""

from __future__ import annotations

import copy
import json
import os
import queue
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable

from fpfa import coherence, inputs, reply_audit, results_panel, sample_data
from fpfa import status as job_status
from fpfa import theme as palette
from fpfa.about import (
    APP_NAME,
    APP_STRAPLINE,
    APP_TAGLINE,
    COPYRIGHT,
    LICENSE_NAME,
    LICENSE_SUMMARY,
    USE_NOTICE,
)
from fpfa import __version__
from fpfa.bess import bess_chat_summary, bess_govern_note, run_bess_plan
from fpfa.calc_tools import ToolSession
from fpfa.chat_render import CARET, is_job_heading, plain_text, settle_inline
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
from fpfa.design_basis_docx import DESIGN_BASIS_TITLE, write_design_basis
from fpfa.everyday import everyday_reply, run_everyday
from fpfa.instance_lock import LOCK_NAME, ANOTHER_WINDOW_TEXT, InstanceLock, InstanceLockError
from fpfa.jobs import KINDS as JOB_KINDS, JobInbox, label_result
from fpfa.keystore import clear_api_key, key_status, key_storage_help, load_api_key, save_api_key
from fpfa.managed import anthropic_request, reply_with_delete_status, run_heavy_job, session_system
from fpfa.modes_loader import DEFAULT_MODE, MODE_SLUGS, list_modes, normalize_mode
from fpfa.paths import content_root, data_dir, is_content_pack, read_config, write_config
from fpfa.projects import delete_project, list_projects, load_project, new_project, save_project
from fpfa.checker import check_line, export_reason
from fpfa.record import ANSWERED_ON_PANEL, BASIS_LABELS, INTERRUPTED_NOTE, Record, RecordError
from fpfa.spec_docx import DRAFT_SECTION, write_docx
from fpfa.team import check_record, latest_check, team_summary
from fpfa.team_panel import recovery_text, team_view
from fpfa.usage_report import report_text
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

__all__ = ["Desk", "InstanceLockError", "ANOTHER_WINDOW_TEXT"]


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
# drawn by the page: an API-key link when no key is saved, and the optional
# sample zone. Neither is required before a question.
THREAD_HINT = (
    "What are we working on?\n"
    "Ask about a wet, dry, or double-interlock zone, the detection and releasing that trip it, "
    "a spec section, or a calc.\n"
    "Numbers come from the calc tools in your content pack."
)
WELCOME_KEY_LINK = "Add your Anthropic API key in Settings to start chatting →"
WELCOME_SAMPLE_LINK = "Try the sample double-interlock zone (/sample-di) →"
# Three ways to start, drawn as cards on the empty thread: (title, what it does, the action it runs).
# "ask" puts the cursor in the composer and "inputs" opens the Inputs tab; both are the page's own.
# Any other action is one the server runs.
WELCOME_CARDS = (
    ("Ask a question",
     "Type it below in plain words. The lead reads the method from your content pack and brings in "
     "the specialists it needs.",
     "ask"),
    ("Size a zone",
     "Enter the zone and its pipe on the Inputs tab and press Run zone. The calc tools do the arithmetic.",
     "inputs"),
    ("Try the sample",
     "A double-interlock data hall zone, run on this machine. It needs no API key.",
     "sample-di"),
)
WELCOME_FOOTNOTE = (
    "The sample is optional. It opens its own job and runs the zone tool plan on this machine.\n"
    "Type /help for commands."
)
STALE_RUN_NOTE = (
    "A tool plan ran for this zone before these inputs changed: {names}. Its figures are out of date. "
    "Do not quote them and do not treat them as governing. The Results tab and Section {section} still show "
    "that run until the zone is run again. Work from the project inputs as they are now, and tell the "
    "designer the zone has to be run again (/run) before the tables or that export are used."
)
EXPORT_STALE_RUN = (
    "The zone form changed after the last run ({names}). Section {section} would be written from the old "
    "run. Press Run zone (or type /run) and export again."
)
RESULTS_STALE_LINE = "These figures are from a run before the form changed ({names}). Run the zone again."
EXPORT_NEEDS_RUN = (
    f"Export of draft Section {DRAFT_SECTION} needs a zone run on this job first. "
    "Fill in the Inputs tab and press Run zone (or type /run). /sample-di loads a sample zone to try it."
)
COMPOSER_PLACEHOLDER = "Ask about a zone, a releasing sequence, a spec section, or a calc…"
# A gap between two ticks longer than this means the machine slept or the process was
# frozen. The pump ticks every 100 ms, so an awake machine never comes close.
WAKE_GAP_SECONDS = 90.0
CANCELLED_RUN_LINE = (
    "Cancelled. The designer stopped the narration before it finished. "
    "The tool plan had already run, so its figures stand below and in the tables."
)
COMPOSER_HINT = "Enter to send  ·  Shift+Enter for a new line  ·  /help for commands"
PENDING_LABEL = "Working on it…"
NO_RUN_TEXT = (
    "No zone run on this job yet.\n\n"
    "Fill in the Inputs tab and press Run zone (or type /run). "
    "The run is posted in the thread, and the tool-plan figures stay here for export."
)
# How the designer left the window: the sidebar shown or hidden, which tab of the job panel is open
# ("" is closed), and how wide the panel is in CSS pixels (0 is the page's own width). The page owns
# these; the app only remembers them between runs.
PANEL_TABS = ("inputs", "results", "team")
LAYOUT_DEFAULT = {"sidebar": True, "panel": "", "panel_width": 0}
PANEL_WIDTH_RANGE = (320, 2400)


def clean_layout(values: Any, base: dict | None = None) -> dict:
    """base with the layout values that can be read from values. Anything else is left as base has it."""
    layout = dict(LAYOUT_DEFAULT if base is None else base)
    if not isinstance(values, dict):
        return layout
    if "sidebar" in values:
        layout["sidebar"] = bool(values["sidebar"])
    if "panel" in values:
        tab = str(values["panel"] or "")
        layout["panel"] = tab if tab in PANEL_TABS else ""
    if "panel_width" in values:
        try:
            width = int(float(values["panel_width"]))
        except (TypeError, ValueError, OverflowError):
            width = 0
        layout["panel_width"] = 0 if width <= 0 else max(PANEL_WIDTH_RANGE[0], min(PANEL_WIDTH_RANGE[1], width))
    return layout


def saved_layout() -> dict:
    return clean_layout(read_config().get("layout"))


# Status glyph and tone for a job in the Activity list.
ACTIVITY_MARKS = {
    "queued": ("○", ""),
    "running": ("●", "accent"),
    "done": ("✓", "ok"),
    "error": ("!", "err"),
    "cancelled": ("✕", "warn"),
    "interrupted": ("!", "warn"),
}


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
        "The inputs are on the Inputs tab and the figures on the Results tab. "
        "Ask follow-up questions here and they use these figures."
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
        "- /run — run the zone on the Inputs tab\n"
        "- /mode — show the active mode. /mode brainstorm switches (also calculator, synthesis, mixed)\n"
        "- /new Job name — start a named job\n"
        "- /heavy task — text-only hosted reasoning on the zone packet already in the message. "
        "The reply comes back into this thread. It does not call read_role, read_skill, read_mode, "
        "or a calc tool, and it is the only path that uses the hosted runtime.\n"
        "- /status — where this job stands: the plan, who did what, what the team needs from you, "
        "what is out of date, and what is not settled. Read from the record; no model call\n"
        "- /usage — tokens, time, and estimated cost for this job, from the record\n"
        "- /help — this list\n\n"
        "## Keys and menus\n"
        "- Ctrl+S saves the open job. Closing the window saves it too. Ctrl+N starts a new chat.\n"
        "- Right-click a job in the sidebar, or use its ⋯ button, to rename or delete it.\n"
        f"- ⋯ menu: the samples, Run zone, Export draft Section {DRAFT_SECTION} "
        "(after a run and a blind claim check in this thread), Export Design Basis and Open Questions "
        "(from this job's project record, after a trace check), and Settings.\n\n"
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
HAZARDS = inputs.HAZARDS
BASES = inputs.BASES
MEDIA = inputs.MEDIA
PRIMES = inputs.PRIMES
LENGTHS = (("Center to center", "center_to_center"), ("Cut lengths", "cut"))
SEGMENT_ROLES = inputs.SEGMENT_ROLES
# The page's field names beside the project inputs they edit (fpfa.inputs).
FORM_TO_INPUT = {
    "ahj": "ahj", "nfpa_13": "nfpa_13", "nfpa_72": "nfpa_72", "insurer": "insurer", "hazard_notes": "hazard_notes",
    "zone_id": "zone_id", "system_label": "system_type", "hazard": "hazard", "delivery_basis": "delivery_basis",
    "density": "density_gpm_ft2", "base_area": "base_area_ft2", "area_increase": "area_increase", "hose": "hose_gpm",
    "q_fill": "q_fill_gpm", "t_detect": "t_detect_s", "t_release": "t_release_s", "t_exhaust": "t_exhaust_s",
    "supervisory_psi": "supervisory_psi", "fittings": "fittings_percent", "trim_gal": "trim_gal",
    "supervisory_psig": "supervisory_psig", "fill_minutes": "fill_minutes", "medium": "medium",
    "prime": "prime_held_by", "length_label": "length_basis", "supervised": "supervised", "qod": "qod",
    "failsafe": "failsafe_on_total_power_loss", "manual_station": "manual_station",
}

_INLINE_HEADING = re.compile(r"\s*Job [0-9a-f]{6,} \| .*$")
# What the working line says for a job that is not a chat turn.
KIND_ACTIVITY = {
    "zone": "narrating the zone run",
    "bess": "writing the explosion-control starter",
    "claim": "running the blind claim check",
    "heavy": "waiting on the hosted session",
}
_RECORD_TOOLS = frozenset({
    "record_fact", "record_evidence", "record_finding", "open_question", "record_decision", "handoff",
})
# The team's own moves, in a few words each. A line names the move, never what it carried.
_TEAM_ACTIVITY = {
    "list_specialists": "looking at the team",
    "request_check": "running the trace check",
    "set_input": "recording a project input",
    "answer_question": "recording your answer",
    "set_plan": "setting out the plan",
    "resolve_disagreement": "settling a disagreement",
    "review_finding": "reviewing another specialist's finding",
    "withdraw_finding": "withdrawing a finding",
}
_LISTING_TOOLS = frozenset({"list_skills", "list_roles", "list_modes"})


def describe_activity(event: dict) -> str | None:
    """A few plain words for the working line, from one tool-loop event. None leaves the line as it is.

    The words name the tool or the file being read. Nothing here reads the
    tool's result, and no figure is shown before the reply states it.
    """
    kind = event.get("type")
    agent = str(event.get("agent") or "")
    prefix = f"{agent}: " if agent else ""
    if kind == "retry":
        # The API refused or dropped a request and it is being sent again. Nothing was lost.
        return f"waiting to try again (attempt {event.get('attempt')} of {event.get('of')})"
    if kind == "round":
        return prefix + "thinking"
    if kind == "tool_end":
        return prefix + "thinking"
    if kind != "tool_start":
        return None
    name = str(event.get("name") or "")
    args = event.get("input") if isinstance(event.get("input"), dict) else {}
    slug = str(args.get("slug") or "").strip()
    if name == "read_skill":
        return prefix + (f"reading the {slug} skill" if slug else "reading a skill")
    if name == "read_role":
        return prefix + (f"reading the {slug} role" if slug else "reading a role")
    if name == "read_mode":
        return prefix + (f"reading the {slug} mode" if slug else "reading a mode")
    if name in _LISTING_TOOLS:
        return prefix + "looking through the content pack"
    if name == "search_corpus":
        return prefix + "searching the corpus"
    if name == "read_record":
        return prefix + "reading the project record"
    if name in _RECORD_TOOLS:
        return prefix + "writing to the project record"
    if name == "delegate":
        who = str(args.get("specialist") or "").strip()
        return prefix + (f"handing off to {who}" if who else "handing off to a specialist")
    if name == "consult":
        who = str(args.get("specialist") or "").strip()
        return prefix + (f"asking {who}" if who else "asking another specialist")
    if name in _TEAM_ACTIVITY:
        return prefix + _TEAM_ACTIVITY[name]
    if name:
        return prefix + f"running {name}"
    return None


def suggested_prompts(
    project: dict | None,
    chat_log: list[dict],
    *,
    key_saved: bool,
    busy: bool = False,
) -> list[tuple[str, str]]:
    """One-tap suggestions for the composer: (label, the message it sends).

    An empty thread offers the sample zone, and a question once a key is
    saved. A thread whose zone has run and has no typed question yet offers
    follow-ups on that zone. A typed question, or a job in flight, clears them.
    """
    if busy:
        return []
    asked = any(
        turn.get("role") == "user" and not str(turn.get("text") or "").lstrip().startswith("/")
        for turn in chat_log
    )
    if asked:
        return []
    if not chat_log:
        chips = [("Load the sample zone", "/sample-di")]
        if key_saved:
            chips.append((
                "What trips a double-interlock valve?",
                "Walk me through what has to happen, in order, for a double-interlock preaction valve to trip.",
            ))
        chips.append(("Show the commands", "/help"))
        return chips
    run = (project or {}).get("last_run") if project else None
    if not isinstance(run, dict) or not key_saved:
        return []
    zone = str(((project or {}).get("di") or {}).get("zone_id") or "").strip()
    name = f"zone {zone}" if zone else "this zone"
    return [
        ("Design basis", f"Give me the design basis for {name}."),
        ("Explain the screen", f"Explain the delivery-time screen result for {name} and what would change it."),
        ("Questions for the engineer", f"What should I ask the engineer of record about {name}?"),
    ]


def resume_prompts(team: dict | None, *, key_saved: bool, busy: bool, untouched: bool,
                   run_changes: list[str] | None = None) -> list[tuple[str, str]]:
    """One-tap next steps read from where the job stands. Shown only when something is waiting.

    team is team_view()'s result. untouched is true while the designer has
    not typed since the job was opened, which is when "where things stand"
    is worth offering. Nothing here calls a model; a chip sends a message.
    """
    if busy or not team:
        return []
    chips: list[tuple[str, str]] = []
    worked = bool(team.get("people")) or bool(team.get("findings"))
    if key_saved:
        if team.get("unseen_answers"):
            chips.append(("Continue with my answers",
                          "I answered your questions on the Team panel. Continue from there."))
        if team.get("stale") or run_changes:
            chips.append(("Bring it up to date",
                          "An input changed. Bring the affected work up to date and tell me what moved."))
        if team.get("interrupted"):
            chips.append(("Finish what was interrupted",
                          "The last run was interrupted. Finish what was in progress."))
        if team.get("disagreements") or team.get("conflicts"):
            chips.append(("Settle what is open",
                          "The specialists are not agreed. Settle it, or tell me what you need from me to settle it."))
    if worked and (untouched or chips):
        chips.append(("Where things stand", "/status"))
    return chips[:4]


def reduce_motion() -> bool:
    """True when replies should appear at once: the Settings choice, or FPFA_REDUCE_MOTION=1."""
    if reduce_motion_forced():
        return True
    return bool(read_config().get("reduce_motion"))


def reduce_motion_forced() -> bool:
    return os.environ.get("FPFA_REDUCE_MOTION", "").strip() in ("1", "true", "yes")


def short_status(text: str) -> str:
    """The footer's line: the status without the job heading the inbox needs, cut at 160 characters."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    kept = [line for line in lines if not is_job_heading(line)] or lines
    joined = " ".join(kept)
    # A job heading at the end of a note names the job for the inbox. The footer leaves it off.
    short = _INLINE_HEADING.sub("", joined).strip()
    joined = short or joined
    if len(joined) > 160:
        joined = joined[:157] + "…"
    return joined


def _blank_to_none(text: str):
    text = str(text).strip()
    return None if text == "" else text


class Var:
    """A value the page reads and the desk writes: what a tkinter variable was in the old window."""

    __slots__ = ("_value", "_on_change")

    def __init__(self, value: Any = "", on_change: Callable[[], None] | None = None):
        self._value = value
        self._on_change = on_change

    def get(self) -> Any:
        return self._value

    def set(self, value: Any) -> None:
        if value == self._value:
            return
        self._value = value
        if self._on_change is not None:
            self._on_change()


class Shell:
    """What the desk asks of the window around the page. The server's shell is pywebview or the browser.

    ask_save_path is called on a thread of its own, never with Desk.lock held:
    a native dialog waits for the designer.
    """

    def ask_save_path(self, title: str, filename: str) -> Path | None:
        return None

    def scheme_changed(self, scheme_id: str) -> None:
        return None


# Text fields of the form, with the value a blank form shows.
_TEXT_FIELDS = {
    # Basis
    "ahj": "", "nfpa_13": "2025", "nfpa_72": "2025", "insurer": "FM", "hazard_notes": "",
    # Zone
    "zone_id": "", "density": "0.20", "base_area": "1500", "area_increase": "0.30", "hose": "250",
    "q_fill": "600", "t_detect": "0", "t_release": "0", "t_exhaust": "0", "supervisory_psi": "15",
    "fittings": "", "trim_gal": "", "supervisory_psig": "40", "fill_minutes": "30",
}
_CHOICE_FIELDS = {
    "system_label": ("Double-interlock", tuple(label for label, _ in SYSTEM_CHOICES)),
    "hazard": ("ordinary", HAZARDS),
    "delivery_basis": ("FM", BASES),
    "medium": ("nitrogen", MEDIA),
    "prime": ("nc_solenoid", PRIMES),
    "length_label": ("Center to center", tuple(label for label, _ in LENGTHS)),
}
_BOOL_FIELDS = {"supervised": True, "qod": False, "failsafe": False, "manual_station": True}
FORM_FIELDS = tuple(_TEXT_FIELDS) + tuple(_CHOICE_FIELDS) + tuple(_BOOL_FIELDS)


class Desk:
    def __init__(self, *, shell: Shell | None = None, lock: bool = True):
        self.shell = shell or Shell()
        # One window per data directory. A second one would recover this one's live work.
        self.instance_lock = InstanceLock(data_dir() / LOCK_NAME)
        if lock and not self.instance_lock.acquire():
            raise InstanceLockError(ANOTHER_WINDOW_TEXT)
        self.lock = threading.RLock()
        self.changed = threading.Condition()
        self.revision = 0
        self.thread_rev = 0
        self.form_rev = 0
        self.live_rev = 0
        self._owner: int | None = None
        self._home = threading.get_ident()
        self.queue: queue.Queue = queue.Queue()
        self._content_check_running = False
        self.project: dict | None = None
        self.chat_log: list[dict] = []
        self.project_rows: list[dict] = []
        self.activity_rows: list[dict] = []
        self.team: dict = team_view(None)
        self.results_text = NO_RUN_TEXT
        # The same run as the Results tab draws it: figures, labels, flags (fpfa.results_panel).
        self.results_view: dict = results_panel.empty_view()
        # Counts the runs that landed on the open job while it was open. The page shows Results when it moves.
        self.run_rev = 0
        self.notices: list[dict] = []
        self._notice_seq = 0
        # One entry per submitted zone job. Two /run commands on one project
        # each post their own labeled result or error.
        self._announce_jobs: set[str] = set()
        # Sample runs put a short "what was loaded" note above their reply.
        self._seed_notes: dict[str, str] = {}
        self.jobs: JobInbox | None = None
        # The key is read once and kept, so a click never waits on the key store.
        # Settings refreshes it when the key is saved or cleared.
        self._key: str | None = None
        self._key_status = ""
        self.key_message = ""
        self.content_line = ""
        self.changelog = format_changelog(current_changelog())
        self._mode_list: list[str] = []
        self._settings: dict | None = None
        self._assumption_cache: tuple[tuple[str, str], str] | None = None
        # Replies in flight. Workers put stream events on this queue; pump() reads it.
        self._stream_events: queue.SimpleQueue = queue.SimpleQueue()
        self._stream_closed: set[str] = set()
        self._lives: dict[str, dict] = {}
        self._activity: dict[str, str] = {}
        # Inputs the designer typed since the form was last written to a job. Their source is the designer.
        self._typed: set[str] = set()
        # How long the thread was when the open job was opened, to tell a returning designer from a typing one.
        self._opened_len = 0

        touch = self._touch
        self.status = Var("", touch)
        self.content_status = Var(content_status_line(), touch)
        self.content_banner = Var("", touch)
        self.ask_claude = Var(False, touch)
        self.mode_slug = Var(DEFAULT_MODE, touch)
        for name, value in _TEXT_FIELDS.items():
            setattr(self, name, Var(value, touch))
        for name, (value, _choices) in _CHOICE_FIELDS.items():
            setattr(self, name, Var(value, touch))
        for name, value in _BOOL_FIELDS.items():
            setattr(self, name, Var(value, touch))
        self.segments: list[dict] = []

        self.scheme = palette.saved_scheme()
        self.layout = saved_layout()
        self._load_key()
        self.status.set(self._key_status)
        self.ask_claude.set(self._key_saved)
        self._apply_mode(DEFAULT_MODE)
        self.jobs = JobInbox(worker_count=2, on_change=self._on_jobs_changed)
        # The project record. Calc tools and record tools write to it by job id.
        self.record = Record()
        # Cancel flags for running jobs, by job id. Set from Stop or the Team tab.
        self._cancel_events: dict[str, threading.Event] = {}
        # Last (status, error) each job was written to the record with. Desk thread only.
        self._job_sync_seen: dict[str, tuple[str, str]] = {}
        # Per project, the thread note recovery owes it, posted once when the job opens.
        self._recovery_notes: dict[str, str] = {}
        # Wall clock at the last tick. A long gap is a sleep or a freeze.
        self._last_tick = time.time()
        self._recover_from_record()
        # Cached agent and cloud environment ids for later /heavy calls.
        # Not a session. Session cleanup does not delete these.
        self._managed_resources: dict = {}
        try:
            self._pristine_basis = self.collect_basis()
            self._pristine_di = self.collect_di()
        except ValueError:
            self._pristine_basis = None
            self._pristine_di = None
        self._refresh_assumptions()
        self.refresh_projects()
        self._closed = False

    # Threads and change ------------------------------------------------------

    def _touch(self, *_args) -> None:
        """The page's state changed. Desk thread only."""
        self.revision += 1
        self._wake()

    def _settings_changed(self) -> None:
        self._settings = None
        self._touch()

    def _wake(self) -> None:
        with self.changed:
            self.changed.notify_all()

    def _on_desk_thread(self) -> bool:
        ident = threading.get_ident()
        if self._owner is not None:
            return self._owner == ident
        return ident == self._home

    def call(self, method: Callable, *args, **kwargs):
        """Run one action under the desk's lock, as the desk's thread."""
        with self.lock:
            before = self._owner
            self._owner = threading.get_ident()
            try:
                return method(*args, **kwargs)
            finally:
                self._owner = before

    def pump(self) -> int:
        """Run what the workers left on the queue, take stream events, and tick. Returns the callbacks run."""
        with self.lock:
            before = self._owner
            self._owner = threading.get_ident()
            try:
                return self._pump()
            finally:
                self._owner = before

    def _pump(self) -> int:
        self._tick()
        ran = 0
        while True:
            try:
                callback = self.queue.get_nowait()
            except queue.Empty:
                break
            ran += 1
            try:
                callback()
            except Exception as exc:
                self.status.set("Update failed. " + safe_error(exc))
        self._drain_stream_events()
        return ran

    # The old window's poll. Kept as a name for the tests and the server loop.
    _poll = pump

    def _tick(self) -> None:
        now = time.time()
        gap = now - getattr(self, "_last_tick", now)
        self._last_tick = now
        if gap > WAKE_GAP_SECONDS:
            try:
                self._on_wake(gap)
            except Exception as exc:
                self.status.set("Resume check failed. " + safe_error(exc))

    def start(self) -> None:
        """What runs once the window is up: the content feed check on launch."""
        if updates_on_launch():
            self._start_content_check(manual=False)

    def close(self) -> None:
        """Save the open job, stop the inbox, and let the next window take the data directory."""
        if self._closed:
            return
        self._closed = True
        try:
            self._persist_open_work()
        except Exception:
            pass
        jobs = getattr(self, "jobs", None)
        if jobs is not None:
            # close() deletes a hosted session that is still polling.
            # The delete runs off this thread and is joined for a short bound.
            jobs.close()
        lock = getattr(self, "instance_lock", None)
        if lock is not None:
            lock.release()

    _on_close = close

    # The key ------------------------------------------------------------------

    def _load_key(self) -> None:
        before = self._key
        try:
            self._key = load_api_key() or ""
        except Exception:
            self._key = ""
        if self._key != before:
            # Settings shows whether a key is saved: read it again.
            self._settings = None
        try:
            self._key_status = key_status(self._key)
        except Exception as exc:
            self._key_status = "The key store did not answer. " + safe_error(exc)

    def _api_key(self) -> str:
        """The key, for an action that needs one now (a question, a narrated run, a check).

        A saved key is kept. With none kept, the store is read again, so a key saved
        since (by Settings or by hand) is found the next time one is needed.
        """
        if not self._key:
            self._load_key()
        return self._key or ""

    @property
    def _key_saved(self) -> bool:
        """Whether a key is kept. Never asks the store: the state is drawn often, under the lock,
        and on a Windows source run each ask is a child Python that can wait seconds."""
        return bool(self._key)

    def _sync_claude_default(self) -> None:
        self._load_key()
        self.ask_claude.set(self._key_saved)

    # Notices -------------------------------------------------------------------

    def notify(self, title: str, message: str, *, kind: str = "info") -> None:
        """A message the page shows in a dialog in the window's own colours."""
        self._notice_seq += 1
        self.notices.append({"id": self._notice_seq, "title": title, "message": message, "kind": kind})
        del self.notices[:-5]
        self._touch()

    def dismiss_notice(self, notice_id: int) -> None:
        self.notices = [item for item in self.notices if item["id"] != notice_id]
        self._touch()

    # Open work ------------------------------------------------------------------

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

    # The form ---------------------------------------------------------------

    def form_values(self) -> dict:
        return {name: getattr(self, name).get() for name in FORM_FIELDS}

    def patch_form(self, values: dict) -> None:
        """Fields the designer typed in the page. Unknown names are ignored."""
        for name, value in (values or {}).items():
            if name in _BOOL_FIELDS:
                getattr(self, name).set(bool(value))
            elif name in _CHOICE_FIELDS:
                if value in _CHOICE_FIELDS[name][1]:
                    getattr(self, name).set(value)
            elif name in _TEXT_FIELDS:
                getattr(self, name).set("" if value is None else str(value))
            else:
                continue
            # The designer supplied this input. The record says so beside its value.
            self._typed.add(FORM_TO_INPUT.get(name, name))
        self._refresh_assumptions()

    def _form_loaded(self) -> None:
        """The form changed under the page (a job opened, a segment added). The page reloads it."""
        self.form_rev += 1
        self._refresh_assumptions()
        self._touch()

    def _refresh_assumptions(self) -> None:
        trim = self.trim_gal.get()
        basis = self.delivery_basis.get() or "FM"
        key = (str(trim), str(basis))
        if self._assumption_cache is not None and self._assumption_cache[0] == key:
            return
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
        self._assumption_cache = (key, "\n".join(lines))
        self._touch()

    @property
    def assumption_text(self) -> Var:
        return Var(self._assumption_cache[1] if self._assumption_cache else "")

    def collect_basis(self) -> dict:
        return {
            "ahj": str(self.ahj.get()).strip(),
            "nfpa_13": str(self.nfpa_13.get()).strip() or "2025",
            "nfpa_72": str(self.nfpa_72.get()).strip() or "2025",
            "insurer": str(self.insurer.get()).strip() or "FM",
            "hazard_notes": str(self.hazard_notes.get()).strip(),
        }

    def collect_di(self) -> dict:
        code = next((value for name, value in SYSTEM_CHOICES if name == self.system_label.get()), "di")
        segments = []
        for row in self.segments:
            length = row.get("length_ft")
            segment = {
                "role": row.get("role") or "",
                "nps": row.get("nps"),
                "schedule": row.get("schedule") or "",
                "length_ft": float(length) if str(length if length is not None else "").strip() else None,
            }
            if str(row.get("d_in") or "").strip():
                segment["d_in"] = float(row["d_in"])
            segments.append(segment)

        def num(value):
            value = str(value).strip()
            return None if value == "" else float(value)

        return {
            "zone_id": str(self.zone_id.get()).strip(),
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

    def _apply_basis(self, basis: dict) -> None:
        self.ahj.set(basis.get("ahj") or "")
        self.nfpa_13.set(basis.get("nfpa_13") or "2025")
        self.nfpa_72.set(basis.get("nfpa_72") or "2025")
        self.insurer.set(basis.get("insurer") or "FM")
        self.hazard_notes.set(basis.get("hazard_notes") or "")

    def _apply_di(self, di: dict) -> None:
        def text(value, blank=""):
            return blank if value is None else str(value)

        self.zone_id.set(di.get("zone_id") or "")
        code = di.get("system_type") or "di"
        self.system_label.set(next((name for name, value in SYSTEM_CHOICES if value == code), "Double-interlock"))
        self.hazard.set(di.get("hazard") or "ordinary")
        self.supervised.set(bool(di.get("supervised", True)))
        self.density.set(text(di.get("density_gpm_ft2")))
        self.base_area.set(text(di.get("base_area_ft2")))
        self.area_increase.set(text(di.get("area_increase")))
        self.hose.set(text(di.get("hose_gpm")))
        self.q_fill.set(text(di.get("q_fill_gpm")))
        self.t_detect.set(text(di.get("t_detect_s"), "0"))
        self.t_release.set(text(di.get("t_release_s"), "0"))
        self.t_exhaust.set(text(di.get("t_exhaust_s"), "0"))
        self.qod.set(bool(di.get("qod")))
        self.delivery_basis.set(di.get("delivery_basis") or "FM")
        self.medium.set(di.get("medium") or "nitrogen")
        self.prime.set(di.get("prime_held_by") or "nc_solenoid")
        self.failsafe.set(bool(di.get("failsafe_on_total_power_loss")))
        self.supervisory_psi.set(text(di.get("supervisory_psi")))
        self.manual_station.set(bool(di.get("manual_station", True)))
        length_code = di.get("length_basis") or "center_to_center"
        self.length_label.set(next((name for name, value in LENGTHS if value == length_code), "Center to center"))
        self.fittings.set(text(di.get("fittings_percent")))
        self.trim_gal.set(text(di.get("trim_gal")))
        self.supervisory_psig.set(text(di.get("supervisory_psig"), "40"))
        self.fill_minutes.set(text(di.get("fill_minutes"), "30"))
        self.segments = []
        for segment in di.get("segments") or []:
            self._insert_segment(segment, loaded=False)
        self._form_loaded()

    def _insert_segment(self, segment: dict, *, loaded: bool = True) -> None:
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
        self.segments.append({
            "role": segment.get("role") or "",
            "nps": nps,
            "schedule": schedule,
            "length_ft": segment.get("length_ft") if segment.get("length_ft") is not None else "",
            "d_in": "" if d_in in (None, "") else f"{float(d_in):.3f}",
        })
        if loaded:
            self._typed.add("segments")
            self._form_loaded()

    def add_segment(self, role: str, nps: str, schedule: str, length: str) -> bool:
        """Resolve the pipe ID from the calc pack and add the row. False, with a notice, when it cannot."""
        nps = str(nps or "").strip()
        length = str(length or "").strip()
        role = role if role in SEGMENT_ROLES else "branch"
        if not nps or not length:
            self.notify("Segment", "Enter a nominal size and a length.")
            return False
        try:
            length_ft = float(length)
        except ValueError:
            self.notify("Segment", f"Length ft must be a number. Got {length!r}.", kind="error")
            return False
        try:
            resolved = ToolSession(content_root()).execute("resolve_pipe_id", {
                "nps": nps,
                "schedule": str(schedule or "").strip(),
                "role": role,
            })
        except Exception as exc:
            self.notify("Pipe ID", safe_error(exc), kind="error")
            return False
        self._insert_segment({
            "role": role,
            "nps": resolved.get("nps") or nps,
            "schedule": resolved.get("schedule") or "",
            "length_ft": length_ft,
            "d_in": resolved.get("d_in"),
        })
        flags = resolved.get("flags") or []
        if flags:
            self.status.set("; ".join(flags))
        return True

    def remove_segment(self, index: int) -> None:
        if 0 <= int(index) < len(self.segments):
            del self.segments[int(index)]
            self._typed.add("segments")
            self._form_loaded()

    def _selected_mode(self) -> str:
        return self.mode_slug.get() or DEFAULT_MODE

    def _write_form(self, project: dict) -> None:
        # Selected mode is stored even when a later numeric field is invalid.
        project["mode"] = self._selected_mode()
        project["basis"] = self.collect_basis()
        project["di"] = self.collect_di()
        project["chat"] = self.chat_log
        if self._typed:
            inputs.note_given(project, self._typed, inputs.SOURCE_DESIGNER)
            self._typed = set()

    def _capture_form(self, project: dict) -> str | None:
        """Copy the form onto project. A bad number does not drop the chat or the mode."""
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

    # Modes ----------------------------------------------------------------------

    def _known_modes(self) -> list[str]:
        try:
            found = [item["slug"] for item in list_modes(content_root())]
        except FileNotFoundError:
            found = []
        return found or list(MODE_SLUGS)

    def _apply_mode(self, slug: str | None) -> None:
        known = self._known_modes()
        self._mode_list = known
        chosen = normalize_mode(slug)
        if chosen not in known:
            chosen = DEFAULT_MODE if DEFAULT_MODE in known else known[0]
        self.mode_slug.set(chosen)
        self._touch()

    def mode_choices(self) -> list[str]:
        """Mode slugs listed on the Mode menu."""
        return list(self._mode_list)

    def set_mode(self, slug: str) -> None:
        """The Mode menu. The choice is saved on the open job."""
        if slug not in self._mode_list:
            return
        self.mode_slug.set(slug)
        if self.project is not None:
            self.project["mode"] = slug

    def set_narrate(self, on: bool) -> None:
        self.ask_claude.set(bool(on))

    # Projects ----------------------------------------------------------------------

    def refresh_projects(self, select_id: str | None = None) -> None:
        rows = []
        for row in list_projects():
            rows.append({"id": row["id"], "name": row.get("name") or UNTITLED_JOB})
        self.project_rows = rows
        self._touch()

    @property
    def _ids(self) -> list[str]:
        return [row["id"] for row in self.project_rows]

    def select_project(self, project_id: str) -> None:
        """A click on a job in the sidebar. The open job is saved first."""
        if not project_id or project_id not in self._ids:
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
        self.status.set(f"Opened {self.project.get('name')}. {self._key_status}")

    def _apply_project(self, project: dict) -> None:
        # What was typed on the last job's form does not follow the designer to this one.
        self._typed = set()
        self._apply_basis(project.get("basis") or {})
        self._apply_di(project.get("di") or {})
        self.chat_log = list(project.get("chat") or [])
        self._opened_len = len(self.chat_log)
        self._render_chat()
        self._show_saved_run(project.get("last_run") or project.get("bess_run"))
        self._apply_mode(project.get("mode"))
        self._open_record(project)
        self._post_recovery_note(project.get("id"))
        self._refresh_team()

    def _open_record(self, project: dict | None) -> None:
        """Make sure the job is in the project record. An older JSON job is imported once.

        The job's inputs and the record are then brought into step, both ways:
        a field the designer changed supersedes the record's row, and an input
        the lead recorded from the chat is put on the form.
        """
        if not project or not project.get("id"):
            return
        try:
            self.record.import_project(project)
        except Exception as exc:
            self.status.set("Project record is not available. " + safe_error(exc))
            return
        self._pull_inputs_onto_form(project)

    def _sync_inputs(self, project: dict) -> list[str]:
        """Sync one job's basis and zone inputs with the record. Returns the inputs the record put on the form."""
        project_id = project["id"]
        shown = project.get("synced") if isinstance(project.get("synced"), dict) else {}
        # Every basis field goes to the sync, an empty one too: the lead may have recorded it from the chat, and
        # one the designer emptied has to leave the record. A job with no basis block has nothing to compare.
        basis = project.get("basis") if isinstance(project.get("basis"), dict) else None
        basis_now = {key: str(basis.get(key) or "").strip() for key, _label in BASIS_LABELS} if basis is not None else {}
        zone = inputs.zone_values(project)
        zone_now = {name: inputs.encode(name, value) for name, value in zone.items()}
        sources = {name: inputs.source_text(inputs.provenance(project, name, zone[name])) for name in zone}
        # A basis field has no starting value, so one the job holds no note on was typed on the Inputs tab.
        noted = project.get("given") if isinstance(project.get("given"), dict) else {}
        basis_sources = {key: (inputs.source_text(noted[key]) if noted.get(key) in inputs.SOURCE_TEXT else "job form")
                         for key in basis_now}
        from_basis = self.record.sync_form(
            project_id, inputs.BASIS_KIND, basis_now, labels=dict(BASIS_LABELS),
            sources=basis_sources, shown_before=shown.get("basis"),
        )
        from_zone = self.record.sync_form(
            project_id, inputs.INPUT_KIND, zone_now, labels=inputs.GIVEN, sources=sources,
            shown_before=shown.get("zone"),
        )
        pulled: list[str] = []
        for key, text in from_basis["pulled"].items():
            project.setdefault("basis", {})[key] = text
            basis_now[key] = text
            pulled.append(key)
        for key, text in from_zone["pulled"].items():
            project.setdefault("di", {})[key] = inputs.decode(text)
            zone_now[key] = text
            pulled.append(key)
        if pulled:
            # The lead recorded these on the designer's word, in chat.
            inputs.note_given(project, pulled, inputs.SOURCE_CHAT)
        project["synced"] = {"basis": basis_now, "zone": zone_now}
        if from_zone["written"] or from_basis["written"] or pulled:
            # Calcs recorded before the record kept a basis get one from the inputs as they are now.
            try:
                session = ToolSession(content_root())
                coherence.backfill(self.record, project_id, resolve_id=session._resolve_id)
            except Exception:
                pass
        return pulled

    def _pull_inputs_onto_form(self, project: dict) -> list[str]:
        """Sync the job with the record and, when the record put an input on it and it is the open job, redraw the form.

        The form has to show what the sync pulled before it is read again: a
        field still showing the old value would be captured as the designer's
        change and would overrule what the lead recorded.
        """
        try:
            pulled = self._sync_inputs(project)
        except Exception as exc:
            self.status.set("Project record is not available. " + safe_error(exc))
            return []
        if pulled and self.project is not None and self.project.get("id") == project.get("id"):
            self._show_pulled(project, pulled)
        return pulled

    def _show_pulled(self, project: dict, pulled: list[str]) -> None:
        """Put the inputs the record supplied on the open form. The other fields stay as the designer has them.

        Not every caller saved the form first (/status, an answer on the
        panel), so a field typed since the last save is still only on the
        form. It is kept, with its mark that the designer typed it.
        """
        basis = dict(project.get("basis") or {})
        di = dict(project.get("di") or {})
        try:
            shown_basis, shown_di = self.collect_basis(), self.collect_di()
        except ValueError:
            # A number on the form does not parse, so the form cannot be read. The job's own values go back on it.
            self._apply_basis(basis)
            self._apply_di(di)
            self._typed = set()
            return
        for name in pulled:
            if name in basis and name in shown_basis:
                shown_basis[name] = basis[name]
            elif name in di:
                shown_di[name] = di[name]
        self._apply_basis(shown_basis)
        self._apply_di(shown_di)
        # Putting the record's values on the form is not the designer typing them.
        self._typed -= set(pulled)

    def save_current(self) -> None:
        self._ensure_project()
        if not self.project:
            return
        error = self._capture_form(self.project)
        save_project(self.project)
        self.refresh_projects(self.project["id"])
        self._open_record(self.project)
        # A saved field may have left calcs and findings behind. The panel says so at once.
        self._refresh_team()
        if error:
            self.notify("Save", error, kind="error")
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
        self.status.set(f"Opened {project.get('name')}. {self._key_status}")

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

    def rename_job(self, project_id: str | None, name: str) -> None:
        project_id = project_id or (self.project or {}).get("id")
        if not project_id:
            self.status.set("Start a chat first. A job is created with the first message.")
            return
        name = " ".join(str(name or "").split())
        if not name:
            return
        is_open = self.project is not None and self.project.get("id") == project_id
        try:
            target = self.project if is_open else load_project(project_id)
        except (OSError, json.JSONDecodeError):
            return
        target["name"] = name
        if is_open:
            self._capture_form(target)
        save_project(target)
        self.refresh_projects((self.project or {}).get("id"))
        self.status.set(f"Renamed to {target['name']}.")

    def delete_job(self, project_id: str | None = None) -> None:
        """Delete a job and its record rows. The page asks the designer first."""
        project_id = project_id or (self.project or {}).get("id")
        if not project_id:
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

    def _ensure_project(self) -> None:
        """Create the first job without painting an empty form over what is already typed."""
        if self.project:
            return
        project = new_project(UNTITLED_JOB)
        self._capture_form(project)
        save_project(project)
        self.project = project
        self.refresh_projects(project["id"])
        self.status.set(f"Opened {project.get('name')}. {self._key_status}")

    # Team and recovery ------------------------------------------------------------

    def _project_running(self, project_id: str | None) -> bool:
        if not project_id or self.jobs is None:
            return False
        return any(
            job.project_id == project_id and job.status in ("queued", "running")
            for job in self.jobs.snapshot()
        )

    def _refresh_team(self) -> None:
        """Read the Team tab and the sidebar roster from the record. Cheap; called after every job."""
        project_id = (self.project or {}).get("id") if self.project else None
        snapshot = None
        if project_id:
            try:
                snapshot = self.record.snapshot(project_id)
            except Exception as exc:
                self.status.set("Project record is not available. " + safe_error(exc))
                snapshot = None
        reason = None
        if snapshot is not None:
            try:
                reason = self._basis_reason(snapshot)
            except Exception:
                reason = None
        self.team = team_view(snapshot, export_reason=reason)
        self.team["unseen_answers"] = len((snapshot or {}).get("unseen_answers") or [])
        self._touch()

    def _basis_reason(self, snapshot: dict) -> str:
        """Why the Design Basis export waits, or "" when it is ready. From a snapshot already read."""
        if not snapshot.get("calcs") and not snapshot.get("findings") and not snapshot.get("decisions"):
            return (
                "Nothing is on this job's record yet. Run /sample-di or /run, or ask a question, "
                "then export the design basis."
            )
        return export_reason(snapshot)

    def run_changes(self) -> list[str]:
        """The inputs that changed after the last zone run on the open job. Empty when the run is current."""
        if not self.project or not isinstance(self.project.get("last_run"), dict):
            return []
        try:
            di = self.collect_di()
            basis = self.collect_basis()
        except ValueError:
            di = self.project.get("di") or {}
            basis = self.project.get("basis") or {}
        try:
            return inputs.changed_since(self.project.get("last_run"), di, basis)
        except Exception:
            return []

    def show_status(self, raw: str = "/status") -> None:
        """Post where the job stands into the thread, read from the record. No model call."""
        self._ensure_project()
        if not self.project:
            return
        self._open_record(self.project)
        try:
            snapshot = self.record.snapshot(self.project["id"])
            digest = job_status.build(snapshot, export_reason=self._basis_reason(snapshot))
            text = job_status.designer_text(digest, check_line(snapshot), self.project.get("name") or UNTITLED_JOB)
            changed = self.run_changes()
            if changed:
                text += "\n\n" + RESULTS_STALE_LINE.format(names=", ".join(changed))
        except Exception as exc:
            text = "Status could not be read. " + safe_error(exc)
        self._local_exchange(raw, text)
        self._refresh_team()

    def answer_question(self, question_id: str, answer: str) -> None:
        """The designer answers one of the team's questions on the Team panel. No model call.

        The answer goes on the record under the designer's name and into the
        thread, and the lead is told at the top of its next turn. Nothing runs
        until the designer says to go on, so several can be answered first.
        """
        if not self.project:
            self.notify("Answer", "Open a job first.")
            return
        text = (answer or "").strip()
        if not text:
            self.notify("Answer", "Type the answer first.")
            return
        project_id = self.project["id"]
        self._open_record(self.project)
        try:
            row = next((item for item in self.record.questions(project_id) if item["id"] == question_id), None)
            if row is None:
                raise RecordError("That question is not on this job any more.")
            if row["status"] != "open":
                raise RecordError("That question was already answered.")
            self.record.answer_question(project_id, question_id, answer=text, by=ANSWERED_ON_PANEL)
        except RecordError as exc:
            self.notify("Answer", str(exc))
            self._refresh_team()
            return
        except Exception as exc:
            self.notify("Answer", "The answer could not be saved. " + safe_error(exc))
            return
        self._local_exchange(
            f"Answer to the team's question \"{row['text']}\":\n{text}",
            "Recorded. The lead reads it at the start of its next turn. Answer what else you can on the Team panel, "
            "then press Continue with my answers, or say so in your own words.",
        )
        self._refresh_team()

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

    def _recover_from_record(self) -> None:
        """Launch pass. The inbox is in memory, so nothing survives a relaunch except the record.

        Every job the record still shows queued or running is marked interrupted there
        and listed in Activity under its original id. Working agents are marked
        interrupted and delivered handoffs go back to pending. Nothing is re-run.
        """
        try:
            self.record.recover()
            # Owed notes carry over launches until the job is opened and the note is read.
            report = self.record.unnoted_recoveries()
        except Exception as exc:
            self.status.set("Project record recovery did not run. " + safe_error(exc))
            return
        if not report:
            return
        jobs = handoffs = 0
        for project_id, item in report.items():
            for row in item.get("jobs") or []:
                if row.get("kind") not in JOB_KINDS or self.jobs.get(row["id"]) is not None:
                    continue
                try:
                    self.jobs.record(
                        project_id=project_id, project_name=item.get("name") or UNTITLED_JOB,
                        kind=row["kind"], title=row.get("title") or "", status="interrupted",
                        error=INTERRUPTED_NOTE, job_id=row["id"],
                    )
                except (ValueError, RuntimeError):
                    continue
                self._job_sync_seen[row["id"]] = ("interrupted", INTERRUPTED_NOTE)
                jobs += 1
            handoffs += len(item.get("handoffs") or [])
            note = recovery_text(item)
            if note:
                self._recovery_notes[project_id] = note
        self.status.set(
            f"Recovered after a relaunch: {jobs} job{'s' if jobs != 1 else ''} interrupted, "
            f"{handoffs} handoff{'s' if handoffs != 1 else ''} re-queued, "
            f"across {len(report)} job{'s' if len(report) != 1 else ''} in the sidebar. "
            "Open one to read what was in flight."
        )

    def _post_recovery_note(self, project_id: str | None) -> None:
        """Put the recovery note for this project into its thread, once."""
        notes = getattr(self, "_recovery_notes", None)
        if not project_id or not notes or project_id not in notes:
            return
        if not self.project or self.project.get("id") != project_id:
            return
        note = notes.pop(project_id)
        self._append_chat("assistant", note)
        self._save_form_or_chat(self.project)
        save_project(self.project)
        try:
            self.record.note_recovery(project_id)
        except Exception as exc:
            self.status.set("Project record is not available. " + safe_error(exc))

    def _sync_jobs_to_record(self) -> None:
        """Write each job's status to the record once per change. Desk thread, from the inbox refresh."""
        jobs = getattr(self, "jobs", None)
        record = getattr(self, "record", None)
        if jobs is None or record is None:
            return
        for job in jobs.snapshot():
            state = (job.status, job.error or "")
            if self._job_sync_seen.get(job.id) == state:
                continue
            try:
                record.set_job(
                    job.project_id, job_id=job.id, kind=job.kind, title=job.title,
                    status=job.status, error=job.error or "",
                )
            except Exception as exc:
                self.status.set("Project record is not available. " + safe_error(exc))
                return
            self._job_sync_seen[job.id] = state

    def _on_wake(self, gap: float) -> None:
        """The clock jumped between two ticks: the machine slept or the process was frozen.

        Running jobs are left alone. A model call that was on the network when the
        machine slept returns, times out, or fails on its own, and the job reports
        that in its thread. The record gets a wake event on the open job.
        """
        minutes = max(1, int(round(gap / 60.0)))
        running = [job.id for job in self.jobs.snapshot() if job.status in ("queued", "running")]
        project_id = (self.project or {}).get("id") if self.project else None
        if project_id:
            try:
                self.record.log_event(project_id, "wake", {"gap_seconds": int(gap), "running_jobs": running})
            except Exception:
                pass
        if running:
            self.status.set(
                f"Resumed after about {minutes} min. {len(running)} job{'s' if len(running) != 1 else ''} "
                "still running; one that lost its connection reports an error in its thread, "
                "or cancel it from the Team tab."
            )
        else:
            self.status.set(f"Resumed after about {minutes} min. No job was running.")
        self._refresh_team()

    def start_record_check(self) -> None:
        """Run the trace check over this job's findings as a claim job, without a chat turn."""
        if not self.project:
            self.notify("Trace check", "Open a job first.")
            return
        self._open_record(self.project)
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        if not self.record.findings(origin_id):
            self._local_exchange("Run trace check", "The record has no findings to check yet.")
            self._refresh_team()
            return
        key = self._api_key()
        if not key:
            self._local_exchange("Run trace check", "Save an Anthropic API key in Settings before running the trace check.")
            return

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)
            try:
                if cancel.is_set():
                    # Cancelled while it waited in the queue. No model call, no verdicts written.
                    text = "Cancelled before the trace check started. No model call was made."
                    self.jobs.mark(job_id, "cancelled", text)
                else:
                    outcome = check_record(content_root(), self.record, origin_id, AnthropicMessages(key).create)
                    text = outcome.get("status_line") or "Trace check ran."
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
            title="Trace check of the record",
            work=work,
        )
        self.status.set(f"Trace check… {job.heading()}")

    # The inbox ---------------------------------------------------------------------

    def _on_jobs_changed(self) -> None:
        """Refresh the inbox. A worker thread only enqueues the refresh."""
        if self._on_desk_thread():
            self._refresh_inbox()
            return
        self.queue.put(self._refresh_inbox)

    def _refresh_inbox(self) -> None:
        jobs = getattr(self, "jobs", None)
        if jobs is None:
            return
        self._sync_jobs_to_record()
        rows = []
        for job in jobs.snapshot():
            glyph, tone = ACTIVITY_MARKS.get(job.status, ("·", ""))
            rows.append({
                "id": job.id,
                "kind": job.kind,
                "status": job.status,
                "project_id": job.project_id,
                "project_name": job.project_name,
                "glyph": glyph,
                "tone": tone,
                # The full line names the job for a test and a tooltip; the row shows a mark, the kind, and the name.
                "line": job.inbox_line(),
                "heading": job.heading(),
                "error": job.error or "",
            })
        self.activity_rows = rows
        self._touch()

    @property
    def inbox_lines(self) -> list[str]:
        return [row["line"] for row in self.activity_rows]

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
        """A running job leaves the composer usable. The page never disables it."""
        return None

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

    # Samples, runs, and slash commands ------------------------------------------------

    def _open_sample_project(self) -> None:
        if self.project:
            self._capture_form(self.project)
            save_project(self.project)
        project = new_project("Sample data hall DI zone", copy.deepcopy(sample_data.EXAMPLE_BASIS))
        project["di"] = copy.deepcopy(sample_data.EXAMPLE_DI)
        project["mode"] = self._selected_mode()
        inputs.note_given(project, list(inputs.ZONE_FIELDS) + list(inputs.BASIS_FIELDS), inputs.SOURCE_SAMPLE)
        save_project(project)
        self.refresh_projects(project["id"])
        self.open_project(project["id"])

    def new_sample(self) -> None:
        """Load the sample job and run the DI zone path. Same as the Sample DI chip."""
        self.start_sample_di()

    def start_sample_di(self, typed: str | None = None) -> None:
        """Load the sample job and run the existing DI zone path."""
        raw = (typed or "/sample-di").strip() or "/sample-di"
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
        self._open_bess_project()
        self._append_chat("user", raw)
        self.run_bess(announce=True, seed=sample_bess_seed())

    def start_zone_run(self, typed: str | None = None) -> None:
        raw = (typed or "/run").strip() or "/run"
        self._ensure_project()
        self._append_chat("user", raw)
        self.run_zone(announce=True)

    def start_heavy(self, raw: str, task: str) -> None:
        """Queue one hosted job. The reply is written into this project's thread."""
        task = (task or "").strip()
        if not task:
            self._local_exchange(raw, "Usage: /heavy describe the heavy job")
            return
        self._ensure_project()
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        self._append_chat("user", raw)
        key = self._api_key()
        if not key:
            self._append_chat(
                "assistant",
                "Save an Anthropic API key in Settings before /heavy. "
                "/sample-di and /sample-bess still run on this machine without a key.",
            )
            self._save_form_or_chat(self.project)
            save_project(self.project)
            self.status.set(self._key_status)
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
            f"Started {self.project['name']}. Ask away. The Inputs tab is optional.",
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

    def _show_help(self) -> None:
        self._local_exchange("/help", slash_help_text())

    show_help = _show_help

    def show_usage(self, raw: str = "/usage") -> None:
        """Post the job's token use and estimated cost into the thread, read from the record."""
        if not self.project:
            self._local_exchange(raw, "Open a job first. Usage is read from that job's record.")
            return
        self._open_record(self.project)
        try:
            text = report_text(self.record, self.project["id"], name=self.project.get("name") or UNTITLED_JOB)
        except Exception as exc:
            text = "Usage could not be read. " + safe_error(exc)
        self._local_exchange(raw, "```\n" + text + "\n```")

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
        elif command == "usage":
            self.show_usage(raw)
        elif command == "status":
            self.show_status(raw)
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

    def run_zone(self, *, announce: bool = False, seed: str = "") -> None:
        if not self.project:
            self._report_run_problem(None, "Open a project, or use /sample-di.", announce=announce)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
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
        key = self._api_key()
        use_claude = bool(self.ask_claude.get()) and bool(key)
        if use_claude:
            self._enqueue_zone(
                origin_id, project_name, pack, di, basis, mode, key, announce=announce, seed=seed
            )
            return
        self._run_zone_here(origin_id, project_name, pack, di, basis, mode, announce=announce, seed=seed)

    def _run_zone_here(
        self, origin_id, project_name, pack, di, basis, mode, *, announce: bool = False, seed: str = ""
    ) -> None:
        """Tool plan with no model call. It finishes before the action returns."""
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
        # stays on the desk queue until this action returns and pump() runs.
        if announce:
            self._announce_jobs.add(job.id)
            self._remember_seed(job.id, seed)
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")

    def run_bess(self, *, announce: bool = False, seed: str = "") -> None:
        """Explosion-control starter. Does not read the optional zone form."""
        if not self.project:
            self._report_bess_problem(None, "Open a project, or use /sample-bess.", announce=announce)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
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
        key = self._api_key()
        use_claude = bool(self.ask_claude.get()) and bool(key)
        if use_claude:
            self._enqueue_bess(
                origin_id, project_name, pack, room, basis, zone_result, key,
                announce=announce, seed=seed,
            )
            return
        self._run_bess_here(
            origin_id, project_name, pack, room, basis, zone_result, announce=announce, seed=seed
        )

    def _run_bess_here(
        self, origin_id, project_name, pack, room, basis, zone_result, *, announce: bool = False, seed: str = ""
    ) -> None:
        """LFL tool plan with no model call. It finishes before the action returns."""
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
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")

    def _report_bess_problem(
        self,
        origin_id: str | None,
        message: str,
        job_id: str | None = None,
        *,
        announce: bool | None = None,
    ) -> None:
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
            self.notify("Explosion-control starter", message, kind="error")
        self.status.set(message or "The explosion-control starter did not run.")

    def _finish_bess(
        self,
        origin_id: str,
        result: dict | None,
        error: str | None,
        job_id: str | None = None,
    ) -> None:
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
                self.notify("Explosion-control starter", message, kind="error")
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
            self.run_rev += 1
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
            if self.ask_claude.get() and not self._key:
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
            self.notify("DI zone", message, kind="error")
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
                self.notify("DI zone", message, kind="error")
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
            self.run_rev += 1
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
            if self.ask_claude.get() and not self._key:
                note = "Tool plan only. Save an API key in Settings to ask Claude."
            elif result.get("warnings"):
                note = "Tool plan only. " + result["warnings"][0]
            self.status.set(self._with_job_label(job_id, note))

    # Results ------------------------------------------------------------------------------

    def _set_results(self, text: str, result: dict | None = None) -> None:
        self.results_text = text
        self.results_view = results_panel.results_view(result)
        self._touch()

    def _show_saved_run(self, result: dict | None) -> None:
        if result and result.get("kind") == "bess":
            self._show_bess_result(result)
        elif result:
            self._show_result(result)
        else:
            self._set_results(NO_RUN_TEXT)

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
        self._set_results("\n".join(lines), result)

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
        self._set_results("\n".join(lines), result)

    # Exports ---------------------------------------------------------------------------

    def export_to(self, path: Path, create=None) -> Path:
        """Run the blind claim check, post it here, then write the docx if it passes.

        create() is Messages.create. Without it, a saved key is used. With no
        key, the checker does not run and the file is not written.
        """
        if not self.project or not self.project.get("last_run"):
            raise RuntimeError("Run /sample-di or /run before exporting.")
        changed = self.run_changes()
        if changed:
            raise RuntimeError(EXPORT_STALE_RUN.format(names=", ".join(changed), section=DRAFT_SECTION))
        snapshot = copy.deepcopy(self.project["last_run"])
        outcome = self._claim_outcome(create, snapshot)
        job = self.jobs.record(
            project_id=self.project["id"],
            project_name=self.project.get("name") or UNTITLED_JOB,
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
            self.notify("Export", EXPORT_NEEDS_RUN)
            return
        self.start_claim_check(offer_export=True)

    def design_basis_ready(self) -> str:
        """Empty when the job has a record to export. Otherwise the reason it does not."""
        if not self.project:
            return "Open a job first."
        self._open_record(self.project)
        snapshot = self.record.snapshot(self.project["id"])
        # Basis facts alone come from the form defaults. A design basis needs at least one recorded
        # calculation, finding, or decision. Findings are model claims: the export prints the tier each one
        # earned, so it waits only for a trace check that judged the findings as they are now, and for
        # nothing on the record to be out of date.
        return self._basis_reason(snapshot)

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
            self.notify(DESIGN_BASIS_TITLE, reason)
            return
        project_id = self.project["id"]
        filename = f"{self.project.get('name', 'job')}-design-basis.docx"

        def write(path: Path) -> None:
            if not self.project or self.project.get("id") != project_id:
                self.status.set("Design basis export was not written: another job is open now.")
                return
            try:
                written = self.export_design_basis_to(path)
            except Exception as exc:
                self.notify(DESIGN_BASIS_TITLE, safe_error(exc), kind="error")
                return
            self.status.set(f"Exported {written}")

        self._ask_save(
            f"Export {DESIGN_BASIS_TITLE}", filename, write,
            cancelled=lambda: self.status.set("Design basis export was not written."),
        )

    def _ask_save(self, title: str, filename: str, write: Callable[[Path], None], *, cancelled) -> None:
        """Ask where to save on a thread of its own, then write on the desk's thread.

        The native dialog waits for the designer; the desk stays free meanwhile.
        """
        shell = self.shell

        def ask() -> None:
            try:
                path = shell.ask_save_path(title, filename)
            except Exception as exc:
                message = safe_error(exc)
                self.queue.put(lambda: self.notify(title, message, kind="error"))
                return
            if path:
                self.queue.put(lambda chosen=Path(path): write(chosen))
            else:
                self.queue.put(cancelled)

        threading.Thread(target=ask, daemon=True, name="fpfa-save-dialog").start()

    def start_claim_check(self, offer_export: bool = False) -> None:
        """Queue the blind claim check on this project. The composer stays usable."""
        self._ensure_project()
        if not self.project or not self.project.get("last_run"):
            self.notify("Export", EXPORT_NEEDS_RUN)
            return
        changed = self.run_changes()
        if changed:
            # The section is written from the last run. A run on other inputs is not this zone's section.
            self.notify("Export", EXPORT_STALE_RUN.format(names=", ".join(changed), section=DRAFT_SECTION))
            return
        snapshot = copy.deepcopy(self.project["last_run"])
        packet = build_packet(snapshot)
        stored = self.project.get("claim_check") or {}
        if offer_export and stored.get("all_supported") and same_packet(stored, packet):
            self._offer_export(stored)
            return
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        key = self._api_key()

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
        self.status.set(f"Claim check… {job.heading()}")

    def _claim_outcome(self, create, result=None) -> dict:
        packet = build_packet(result if result is not None else self.project["last_run"])
        if create is None:
            key = self._api_key()
            if not key:
                return unanswered(packet)
            create = AnthropicMessages(key).create
        return judge(content_root(), packet, create)

    def _store_claim(self, project: dict, outcome: dict, job_id: str | None) -> None:
        stored = dict(outcome)
        if job_id:
            stored["job_id"] = job_id
        project["claim_check"] = stored

    def _write_export(self, path: Path, outcome: dict, result=None, project: dict | None = None) -> Path:
        project = project or self.project
        written = write_docx(path, project, result if result is not None else project["last_run"])
        write_packet_files(written.parent, outcome)
        return written

    def _offer_export(self, outcome: dict, result=None) -> None:
        project = self.project
        snapshot = copy.deepcopy(result) if result is not None else None

        def write(path: Path) -> None:
            try:
                written = self._write_export(path, outcome, snapshot, project=project)
            except Exception as exc:
                self.notify("Export", safe_error(exc), kind="error")
                return
            self.status.set(f"Exported {written}")

        def cancelled() -> None:
            note = (outcome or {}).get("status_line") or PACKAGE_STATUS
            self.status.set(f"{note} Export of Section {DRAFT_SECTION} was not written.")

        self._ask_save(
            f"Export draft Section {DRAFT_SECTION}", f"{project.get('name', 'di-zone')}.docx", write,
            cancelled=cancelled,
        )

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

    # The thread ------------------------------------------------------------------------

    def _render_chat(self) -> None:
        """The conversation changed. The page is sent it again."""
        self.thread_rev += 1
        self._touch()

    def thread_text(self) -> str:
        """The open thread as the page shows it, without its styling: what Select all and Copy take."""
        parts = []
        if not self.chat_log:
            parts.append(THREAD_HINT)
        for turn in self.chat_log:
            text = str(turn.get("text") or "")
            if turn.get("role") == "user":
                parts.append("You\n" + text)
            else:
                parts.append(plain_text(text))
        for live in self.live_items():
            # A reply still arriving, as the page draws it: a half-written span closed, a caret after it.
            parts.append(plain_text(settle_inline(live["text"])) + CARET)
        pending = self._pending_spec()
        if pending:
            parts.append(f"{pending['label']} {pending['detail']}".strip())
        return "\n\n".join(parts) + "\n"

    def _pending_spec(self) -> dict | None:
        """The working line: None, or its label and what the newest running job is doing."""
        jobs = getattr(self, "jobs", None)
        if jobs is None or not self.project or not self.chat_log:
            return None
        project_id = self.project.get("id")
        running = [
            job for job in jobs.snapshot()
            if job.project_id == project_id and job.status in ("queued", "running")
        ]
        if not running:
            return None
        newest = running[-1]
        detail = self._activity.get(newest.id) or KIND_ACTIVITY.get(newest.kind, "")
        return {"label": PENDING_LABEL, "detail": detail}

    def _stream_listener(self, job_id: str):
        """What a chat worker reports while its turn runs: (on_event, observe).

        Both run on the worker thread and only put events on a queue; pump()
        reads it on the desk's thread. on_event hears the streamed reply
        (claude_client.AnthropicMessages.streaming) and observe hears the
        tool loop. While a tool runs, the model calls inside it belong to a
        specialist or the checker, so their words stay out of the thread.
        """
        inbox = self._stream_events
        depth = {"tools": 0}

        def on_event(event: dict) -> None:
            if depth["tools"]:
                return
            kind = event.get("type")
            if kind in ("text", "reset"):
                inbox.put((job_id, dict(event)))
            elif kind == "thinking":
                inbox.put((job_id, {"type": "activity", "text": "thinking"}))

        def observe(event: dict) -> None:
            kind = event.get("type")
            if kind == "tool_start":
                depth["tools"] += 1
            elif kind == "tool_end":
                depth["tools"] = max(0, depth["tools"] - 1)
            elif kind == "round" and not depth["tools"] and not event.get("agent"):
                # A new round of the lead. If it writes text, that text is the reply
                # and replaces what an earlier round wrote, as the tool loop keeps it.
                inbox.put((job_id, {"type": "round"}))
            text = describe_activity(event)
            if text is not None:
                inbox.put((job_id, {"type": "activity", "text": text}))

        return on_event, observe

    def _drain_stream_events(self) -> tuple[bool, bool]:
        """Take what the workers reported. Returns (reply text changed, working line changed)."""
        text_changed = False
        activity_changed = False
        while True:
            try:
                job_id, event = self._stream_events.get_nowait()
            except queue.Empty:
                break
            if job_id in self._stream_closed:
                continue
            job = self._job_record(job_id)
            if job is None:
                continue
            kind = event.get("type")
            if kind == "activity":
                if self._activity.get(job_id) != event.get("text"):
                    self._activity[job_id] = event.get("text") or ""
                    activity_changed = True
                continue
            live = self._lives.get(job_id)
            if kind == "round":
                if live is not None:
                    live["new_round"] = True
                continue
            if live is None:
                live = self._lives[job_id] = {
                    "project_id": job.project_id,
                    "heading": job.heading(),
                    "body": "",
                    "text": "",
                    "gen": 0,
                    "new_round": False,
                }
            if kind == "reset":
                live["body"] = ""
                live["gen"] += 1
            elif kind == "text":
                if live.get("new_round"):
                    if live["body"]:
                        live["gen"] += 1
                    live["body"] = ""
                    live["new_round"] = False
                live["body"] += event.get("text") or ""
                if self._activity.get(job_id) != "writing the reply":
                    self._activity[job_id] = "writing the reply"
                    activity_changed = True
            live["text"] = label_result(live["heading"], live["body"])
            text_changed = True
        if activity_changed:
            self._touch()
        if text_changed:
            self.live_rev += 1
            self._wake()
        return text_changed, activity_changed

    def _end_stream(self, job_id: str | None, project_id: str | None) -> None:
        """A chat job finished. Its live reply gives way to the turn that is about to be saved."""
        if not job_id:
            return
        self._stream_closed.add(job_id)
        self._activity.pop(job_id, None)
        if self._lives.pop(job_id, None) is not None:
            self.live_rev += 1
            self._touch()

    def live_items(self, project_id: str | None = None) -> list[dict]:
        """The replies still arriving for the open job (or project_id), oldest first."""
        key = project_id if project_id is not None else (self.project or {}).get("id") or ""
        items = []
        for job_id, live in self._lives.items():
            if live["project_id"] != key or not live["body"]:
                continue
            items.append({"job_id": job_id, "gen": live["gen"], "text": live["text"]})
        return items

    def _chat_jobs_running(self) -> bool:
        jobs = getattr(self, "jobs", None)
        if jobs is None:
            return False
        return any(job.kind == "chat" and job.status in ("queued", "running") for job in jobs.snapshot())

    def chips(self) -> list[dict]:
        try:
            busy = self._pending_here()
            found = suggested_prompts(self.project, self.chat_log, key_saved=self._key_saved, busy=busy)
            if not found and self.project is not None:
                found = resume_prompts(
                    self.team, key_saved=self._key_saved, busy=busy,
                    untouched=len(self.chat_log) <= self._opened_len, run_changes=self.run_changes(),
                )
        except Exception:
            found = []
        return [{"label": label, "action": action} for label, action in found]

    def _append_chat(self, role: str, text: str) -> None:
        self.chat_log.append({"role": role, "text": text})
        self._render_chat()

    def send_chat(self, text: str) -> None:
        """What the composer sends: a slash command, or a question for Claude."""
        text = (text or "").strip()
        if not text:
            return
        parsed = parse_slash_command(text)
        if parsed is not None:
            command, argument = parsed
            self._dispatch_slash(command, argument, text)
            return
        self._send_chat_message(text)

    def _use_chip(self, action: str) -> None:
        """A chip is a typed message sent for the designer: a slash command or a question."""
        self.send_chat(action)

    def _send_chat_message(self, text: str) -> None:
        """Ask Claude without blocking the window. The zone form is optional."""
        self._ensure_project()
        if self._takes_name_from(text):
            # A chat-first job is named after its first question.
            self.project["name"] = chat_title(text)
        origin_id = self.project["id"]
        project_name = self.project.get("name") or UNTITLED_JOB
        self._append_chat("user", text)
        key = self._api_key()
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
            self.status.set(self._key_status)
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
        # A run on inputs that have since changed does not govern anything. The lead is told so
        # in place of the note that would have repeated its figures.
        moved = inputs.changed_since(self.project.get("last_run"), di, basis)
        request = chat_request_text(
            prior,
            basis,
            di,
            text,
            None if moved else self.project.get("last_run"),
            mode,
            self.project.get("bess_run"),
        )
        if moved:
            request += "\n\n" + STALE_RUN_NOTE.format(names=", ".join(moved), section=DRAFT_SECTION)
        if form_note:
            request = form_note + "\n\n" + request
        said = [text] + [str(turn.get("text") or "") for turn in prior if turn.get("role") == "user"]
        earlier = [str(turn.get("text") or "") for turn in prior if turn.get("role") != "user"]

        def work(job_id: str) -> None:
            cancel = self._cancel_event(job_id)
            try:
                pack = content_root()
                client = AnthropicMessages(key)
                # The reply streams into the thread as it is written. A client with no
                # streaming call answers whole, and the page eases that in instead.
                on_event, observe = self._stream_listener(job_id)
                # A request the API asked to have sent again says so on the working line.
                try:
                    client.on_retry = observe
                except Exception:
                    pass
                streaming = getattr(client, "streaming", None)
                create = streaming(on_event) if callable(streaming) else client.create
                out = run_everyday(
                    pack, create, request, mode=mode,
                    record=self.record, project_id=origin_id, agent="lead", cancel=cancel,
                    observe=observe,
                )
                reply = everyday_reply(out)
                summary = team_summary(out, self._audit_reply(origin_id, pack, mode, out, said, earlier))
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
        self.status.set(f"Asking {MODEL_ID}… {job.heading()}")

    def _audit_reply(self, project_id: str, pack: Path, mode: str, out: dict, said: list[str],
                     earlier: list[str]) -> dict | None:
        """Look the reply's figures up in what the lead could have read them from. Runs on the worker.

        The result is kept on the record so a figure flagged once is not
        accepted later because the lead repeated it. A failure here never
        fails the turn: the reply is posted without the note.
        """
        try:
            from fpfa.everyday import assemble_system

            result = reply_audit.audit(
                out.get("text") or "", self.record.snapshot(project_id),
                tool_calls=out.get("tool_calls"), said=said,
                pack_text=assemble_system(pack, mode, team=True),
                earlier_replies=earlier, flagged_before=reply_audit.flagged_before(self.record, project_id),
            )
            if result["figures"]:
                self.record.log_event(project_id, reply_audit.AUDIT_EVENT, result, agent="app")
            return result
        except Exception:
            return None

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
        """Post the reply. usage is the token line from usage_summary, shown on the status line."""
        origin_id = self._destination_id(origin_id, job_id)
        reply = self._with_job_label(job_id, reply)
        self._end_stream(job_id, origin_id)
        if self.project is not None and self.project.get("id") == origin_id:
            self.chat_log.append(self._assistant_turn(reply, job_id))
            self._render_chat()
            form_error = self._save_form_or_chat(self.project)
            # An input the lead recorded from the chat goes onto the form before anything reads the form again.
            pulled = self._pull_inputs_onto_form(self.project)
            save_project(self.project)
            if self.project.get("last_run"):
                note = f"Chat updated. Tables and Section {DRAFT_SECTION} stay on the tool plan."
            else:
                note = "Chat updated."
            if pulled:
                note += " Inputs updated from the chat: " + ", ".join(pulled) + "."
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
        try:
            self._sync_inputs(project)
        except Exception:
            pass
        save_project(project)
        job = self._job_record(job_id)
        heading = job.heading() if job is not None else ""
        note = "Chat reply saved on another project."
        self.status.set(f"{heading}. {note}" if heading else note)

    def _finish_heavy(self, origin_id: str, reply: str, job_id: str | None = None) -> None:
        """Post a heavy-job reply into the thread on the project that started it."""
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

    # Content pack ----------------------------------------------------------------------

    def _set_content_banner(self, text: str) -> None:
        self.content_banner.set(text)

    def dismiss_banner(self) -> None:
        """A click dismisses the update note. The pack stays installed."""
        self._set_content_banner("")

    def _maybe_check_content_on_launch(self) -> None:
        if not updates_on_launch():
            return
        self._start_content_check(manual=False)

    def _start_content_check(self, *, manual: bool, url: str | None = None) -> None:
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
            self.queue.put(lambda result=result: self._finish_content_check(result, manual=manual))

        threading.Thread(target=work, daemon=True).start()

    def _finish_content_check(self, result, *, manual: bool) -> None:
        self._content_check_running = False
        version_line = content_status_line()
        if result.status == "updated":
            self._set_content_banner(update_banner(result.version, result.changelog or []))
            self.content_status.set(version_line)
            self._apply_mode(self.mode_slug.get())
        elif result.status in {"offline", "error", "rejected", "needs_app"} and not manual:
            self.content_status.set(f"{version_line} (still the last good pack)")
        else:
            self.content_status.set(version_line)
        if manual:
            self.content_line = result.message
        shown = result.changelog if result.changelog is not None else current_changelog()
        self.changelog = format_changelog(shown)
        self._assumption_cache = None
        self._refresh_assumptions()
        self._settings_changed()

    def check_content_updates(self, feed: str) -> None:
        """Settings, Check for updates. The typed feed is saved first."""
        try:
            used = remember_feed_url(str(feed or "").strip())
        except ContentUpdateError as exc:
            self.content_line = str(exc)
            self._settings_changed()
            return
        self.content_line = "Checking for a content pack…"
        self._settings_changed()
        self._start_content_check(manual=True, url=used)

    def save_content_root(self, folder: str) -> None:
        """Settings, Advanced: point the app at a content pack folder."""
        path = Path(str(folder or "").strip()).expanduser()
        if not str(folder or "").strip() or not is_content_pack(path):
            self.content_line = (
                "That folder needs skills/ and calcs/fp/formulas.py. The current pack was left as it is."
            )
            self._settings_changed()
            return
        remember_selected_root(str(path))
        try:
            resolved = content_root()
        except FileNotFoundError as exc:
            self.content_line = str(exc)
            self._settings_changed()
            return
        self.content_status.set(content_status_line())
        if os.environ.get("FPFA_CONTENT_ROOT"):
            self.content_line = f"Saved {path}. This run uses {resolved} because FPFA_CONTENT_ROOT is set."
        else:
            self.content_line = f"Content pack: {resolved}"
        self._assumption_cache = None
        self._refresh_assumptions()
        self._apply_mode(self.mode_slug.get())
        self._settings_changed()

    # Settings ------------------------------------------------------------------------

    def set_scheme(self, scheme_id: str) -> str:
        chosen = palette.remember_scheme(scheme_id)
        self.scheme = chosen
        self.status.set(f"Colour scheme: {palette.SCHEMES[chosen].name}.")
        try:
            self.shell.scheme_changed(chosen)
        except Exception:
            pass
        self._settings_changed()
        return chosen

    def set_layout(self, values: dict) -> dict:
        """Remember how the page is laid out. Nothing about a job changes."""
        layout = clean_layout(values, self.layout)
        if layout != self.layout:
            self.layout = layout
            write_config({"layout": layout})
            self._settings_changed()
        return layout

    def set_reduce_motion(self, on: bool) -> None:
        write_config({"reduce_motion": bool(on)})
        self._settings_changed()

    def _key_changed(self) -> None:
        self._load_key()
        self.status.set(self._key_status)
        self._settings_changed()

    def save_key(self, raw: str) -> None:
        raw = str(raw or "").strip()
        if not raw:
            self.key_message = "Paste a key, then save. The stored key was left as it is."
            self._settings_changed()
            return
        try:
            where = save_api_key(raw)
        except Exception as exc:
            self.key_message = safe_error(exc)
            self._settings_changed()
            return
        self._key_changed()
        self.key_message = self._key_status if where else "Key was not stored."
        self.ask_claude.set(True)
        self._settings_changed()

    def clear_key(self) -> None:
        clear_api_key()
        self._key_changed()
        self.key_message = self._key_status
        self.ask_claude.set(False)
        self._settings_changed()

    def check_key(self, raw: str = "") -> None:
        """Settings, Check key: ask the models endpoint for the model id. No text is generated."""
        key = str(raw or "").strip() or self._api_key()
        if not key:
            self.key_message = "No API key saved."
            self._settings_changed()
            return
        self.key_message = "Checking the model id…"
        self._settings_changed()

        def work():
            try:
                found = AnthropicMessages(key).check_model()
                message = f"The key can see model {found}."
            except Exception as exc:
                message = safe_error(exc)

            def done(text=message):
                self.key_message = text
                self._settings_changed()

            self.queue.put(done)

        threading.Thread(target=work, daemon=True).start()

    def load_demo(self) -> None:
        """Create the sample job and run the local tool plan. Does not call Claude."""
        write_config({"key_backend": "file"})
        self.ask_claude.set(False)
        self.start_sample_di()

    # What the page reads ------------------------------------------------------------------

    def settings_view(self) -> dict:
        """Settings, read once per change: the files behind it are not read on every frame."""
        if self._settings is None:
            self._settings = self._read_settings()
        return self._settings

    def _read_settings(self) -> dict:
        try:
            current_root = str(content_root())
        except FileNotFoundError:
            current_root = read_config().get("content_root") or ""
        return {
            "scheme": self.scheme,
            "layout": dict(self.layout),
            "schemes": [
                {"id": scheme.id, "name": scheme.name, "blurb": scheme.blurb, "dark": scheme.dark,
                 "colors": dict(scheme.colors)}
                for scheme in (palette.SCHEMES[item] for item in palette.SCHEME_ORDER)
            ],
            "reduce_motion": reduce_motion(),
            "reduce_motion_forced": reduce_motion_forced(),
            "key_saved": self._key_saved,
            "key_status": self._key_status,
            "key_message": self.key_message or self._key_status,
            "key_help": key_storage_help(),
            "content_version": f"Content version: {content_version_text()}",
            "content_line": self.content_line,
            "changelog": self.changelog,
            "feed_url": resolved_feed_url(),
            "content_root": current_root,
            "checking_content": self._content_check_running,
        }

    def welcome(self) -> dict | None:
        if self.chat_log:
            return None
        lines = THREAD_HINT.splitlines()
        links = []
        if not self._key_saved:
            links.append({"text": WELCOME_KEY_LINK, "action": "settings"})
        links.append({"text": WELCOME_SAMPLE_LINK, "action": "sample-di"})
        cards = [{"title": title, "text": text, "action": action} for title, text, action in WELCOME_CARDS]
        return {"title": lines[0], "lines": lines[1:], "links": links, "cards": cards, "footnote": WELCOME_FOOTNOTE}

    def snapshot(self, *, thread: bool = True) -> dict:
        """Everything the page draws. thread=False leaves the conversation out when the page has it."""
        project = self.project
        open_job = None
        if project is not None:
            open_job = {"id": project.get("id"), "name": project.get("name") or UNTITLED_JOB}
        changed = self.run_changes()
        state = {
            "revision": self.revision,
            "app": {
                "name": APP_NAME, "strapline": APP_STRAPLINE, "tagline": APP_TAGLINE, "version": __version__,
                "copyright": COPYRIGHT, "license_name": LICENSE_NAME,
                "license_summary": LICENSE_SUMMARY, "use_notice": USE_NOTICE, "model": MODEL_ID,
                "draft_section": DRAFT_SECTION, "design_basis_title": DESIGN_BASIS_TITLE,
                "placeholder": COMPOSER_PLACEHOLDER, "composer_hint": COMPOSER_HINT,
            },
            "status": short_status(self.status.get()),
            "status_full": self.status.get(),
            "content_status": self.content_status.get(),
            "banner": self.content_banner.get(),
            "projects": self.project_rows,
            "open": open_job,
            "title": (open_job or {}).get("name") or "New chat",
            "mode": {"slug": self.mode_slug.get(), "choices": self.mode_choices()},
            "narrate": bool(self.ask_claude.get()),
            "activity": self.activity_rows,
            "pending": self._pending_spec(),
            "running_here": self._pending_here(),
            "chips": self.chips(),
            "welcome": self.welcome(),
            "team": self.team,
            "form": {
                "rev": self.form_rev,
                "values": self.form_values(),
                "segments": [dict(row) for row in self.segments],
                "assumptions": self._assumption_cache[1] if self._assumption_cache else "",
                "choices": {name: list(choices) for name, (_value, choices) in _CHOICE_FIELDS.items()},
                "roles": list(SEGMENT_ROLES),
            },
            "results": self.results_text,
            "results_view": self.results_view,
            "run_rev": self.run_rev,
            # Inputs that changed after the run the Results tab and the Section export are showing.
            "run_changes": changed,
            "results_note": RESULTS_STALE_LINE.format(names=", ".join(changed)) if changed else "",
            "notices": list(self.notices),
            "settings": self.settings_view(),
            "live_rev": self.live_rev,
            "thread": {"rev": self.thread_rev, "project": (open_job or {}).get("id")},
        }
        if thread:
            state["thread"]["turns"] = [
                {key: turn[key] for key in ("role", "text", "job_id") if key in turn}
                for turn in self.chat_log
            ]
        return state
