"""Project record. One SQLite database in the data directory.

Every row carries a project id. Agents never open the database. They call
an app tool, the tool validates one row, writes it in one transaction, and
appends an event. Documents are exports of this record.

A calc tool records itself here with a hash of its inputs. A second call
with the same inputs on the same project returns the recorded output and
counts a replay instead of writing a second row. That is the duplicate
prevention the recovery phase relies on.

Connections are opened per call. SQLite connections are bound to the thread
that opened them, and the inbox runs jobs on worker threads, so a shared
connection would break. A process-wide lock serializes writes.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fpfa.inputs import BASIS_KIND, GIVEN, INPUT_KIND
from fpfa.paths import data_dir

DB_NAME = "fpfa.db"
SCHEMA_VERSION = 4

# The three figure labels the app already uses, plus the cite classes the
# content pack uses on a sentence that quotes a source.
LABELS = (
    "calculated",
    "ASSUMED",
    "use best judgment",
    "CODE",
    "OWNER",
    "PRACTICE",
    "PARA",
    "HB",
    # Where a value came from, not what kind of figure it is: the designer supplied it,
    # on the form or to the lead in chat. Only the form and the lead may write it.
    GIVEN,
)
EVIDENCE_STATUSES = ("held", "NOT PULLED", "NEEDS HOLD", "PACKAGE ASSERTION")
QUESTION_STATUSES = ("open", "answered", "withdrawn")
# Who a question is for. "designer": the team needs the answer from the person using the app.
# "engineer": an RFI for the engineer of record, the owner, or the authority; it goes in the document.
QUESTION_AUDIENCES = ("designer", "engineer")
HANDOFF_STATUSES = ("pending", "delivered", "returned", "cancelled")
# delegation: the lead's brief to a specialist. handoff: work one agent leaves for another,
# delivered at the receiver's next delegation. consult: one specialist's question to another,
# answered inside the asker's turn.
HANDOFF_KINDS = ("delegation", "handoff", "consult")
# Event kinds whose newest row a snapshot always carries: the lead's plan and the last trace check.
LATEST_KINDS = ("plan", "record_check")
# Written when a lead turn has read the job's status, so the next one can tell what is new since.
TURN_START = "turn_start"
# Who closed a question: the designer on the panel, or the lead passing on what the designer said in chat.
ANSWERED_ON_PANEL = "designer"
ANSWERED_IN_CHAT = "designer, in chat"
# Agents that write an input because the form held it. Any other agent set it on the designer's word.
FORM_AGENTS = ("job form", "migration")
REVIEW_POSITIONS = ("agree", "object")
REVIEW_STATUSES = ("open", "resolved", "escalated", "withdrawn")
# How a finding leaves the current set: a newer finding replaced it, or its author withdrew it.
WITHDRAWN = "withdrawn"
FINDING_STATUSES = ("open", "Supported", "Not supported", "Source not found")
TASK_STATUSES = ("open", "working", "done", "blocked", "cancelled")
AGENT_STATUSES = ("idle", "working", "done", "error", "interrupted")
# Window jobs as the record keeps them. "interrupted" is set only by recover(): the app
# was not running when the job would have ended.
JOB_STATUSES = ("queued", "running", "done", "error", "cancelled", "interrupted")
_JOB_RANK = {"queued": 0, "running": 1, "done": 2, "error": 2, "cancelled": 2, "interrupted": 2}
# Result text on a handoff that recovery put back on the queue.
REQUEUED_NOTE = "Re-queued after a relaunch. The receiver was interrupted before it returned."
INTERRUPTED_NOTE = "Interrupted. The app was not running when this job would have ended. Run it again; recorded calcs replay."

# Tools whose outputs are calculation records. Content and record tools are not.
CALC_TOOLS = frozenset({
    "resolve_pipe_id",
    "zone_trapped_volume",
    "dry_delivery_screen",
    "di_trip_to_water",
    "density_area",
    "hose_duration",
    "nitrogen_gate",
    "elect_di_trim",
    "releasing_truth_table",
    "lfl_setpoints",
    "fp_calc",
    "fa_calc",
})

_WRITE_LOCK = threading.RLock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created TEXT NOT NULL,
    migrated_at TEXT
);
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    label TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    agent TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL,
    superseded_by TEXT
);
CREATE INDEX IF NOT EXISTS facts_project ON facts(project_id, kind, key);
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    document TEXT NOT NULL,
    edition TEXT NOT NULL DEFAULT '',
    section TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    applicability TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    agent TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL,
    depends TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS evidence_project ON evidence(project_id);
CREATE TABLE IF NOT EXISTS calc_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    tool TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    inputs TEXT NOT NULL,
    outputs TEXT NOT NULL,
    pack_version TEXT NOT NULL DEFAULT '',
    calc_identity TEXT NOT NULL DEFAULT '',
    agent TEXT NOT NULL DEFAULT '',
    replay_count INTEGER NOT NULL DEFAULT 0,
    created TEXT NOT NULL,
    last_used TEXT NOT NULL,
    depends TEXT NOT NULL DEFAULT '[]',
    varies TEXT NOT NULL DEFAULT '{}',
    UNIQUE (project_id, input_hash)
);
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    text TEXT NOT NULL,
    label TEXT NOT NULL,
    supports TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'open',
    created TEXT NOT NULL,
    superseded_by TEXT,
    retire_note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS findings_project ON findings(project_id);
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    raised_by TEXT NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL,
    answer TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL,
    answered TEXT,
    audience TEXT NOT NULL DEFAULT 'engineer',
    answered_by TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS questions_project ON questions(project_id, status);
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    text TEXT NOT NULL,
    basis TEXT NOT NULL DEFAULT '',
    decided_by TEXT NOT NULL,
    label TEXT NOT NULL,
    created TEXT NOT NULL,
    supports TEXT NOT NULL DEFAULT '[]',
    superseded_by TEXT,
    retire_note TEXT NOT NULL DEFAULT '',
    review_id TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS decisions_project ON decisions(project_id);
CREATE TABLE IF NOT EXISTS handoffs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    brief TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL,
    result TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL,
    delivered TEXT,
    returned TEXT,
    kind TEXT NOT NULL DEFAULT 'handoff'
);
CREATE INDEX IF NOT EXISTS handoffs_project ON handoffs(project_id, status);
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    position TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    resolution TEXT NOT NULL DEFAULT '',
    resolved_by TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL,
    updated TEXT NOT NULL,
    UNIQUE (project_id, finding_id, agent)
);
CREATE INDEX IF NOT EXISTS reviews_project ON reviews(project_id, status);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    owner TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    created TEXT NOT NULL,
    updated TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tasks_project ON tasks(project_id, status);
CREATE TABLE IF NOT EXISTS agents (
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role_slug TEXT NOT NULL,
    status TEXT NOT NULL,
    last_active TEXT NOT NULL,
    PRIMARY KEY (project_id, name)
);
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    error TEXT NOT NULL DEFAULT '',
    started TEXT NOT NULL,
    updated TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS jobs_project ON jobs(project_id, status);
CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    ts TEXT NOT NULL,
    kind TEXT NOT NULL,
    agent TEXT NOT NULL DEFAULT '',
    payload TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS events_project ON events(project_id, seq);
"""


class RecordError(ValueError):
    """A row the record refuses. The message says which field."""


def now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id() -> str:
    return uuid.uuid4().hex[:16]


def canonical_json(value: Any) -> str:
    """Stable text for hashing and storage. Keys sorted, no stray whitespace."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str, ensure_ascii=False)


def input_hash(tool: str, inputs: Any, calc_identity: str = "") -> str:
    """Hash of the tool, its inputs, and the identity of the calc code that ran it.

    A replay is only valid when the same code would produce the same output,
    so a content-pack update that changes a kernel file changes the hash and
    the next call computes fresh. The old row stays as history.
    """
    return hashlib.sha256(
        canonical_json({"tool": tool, "inputs": inputs, "calc": calc_identity or ""}).encode("utf-8")
    ).hexdigest()


def _text(value: Any, field: str, *, required: bool = True, limit: int = 20_000) -> str:
    if value is None:
        text = ""
    elif isinstance(value, str):
        text = value.strip()
    else:
        text = str(value).strip()
    if required and not text:
        raise RecordError(f"{field} is required")
    if len(text) > limit:
        raise RecordError(f"{field} is longer than {limit} characters")
    return text


def _choice(value: Any, field: str, allowed: tuple[str, ...]) -> str:
    text = _text(value, field)
    if text not in allowed:
        raise RecordError(f"{field} must be one of: " + ", ".join(allowed))
    return text


def _label(value: Any) -> str:
    """One of the three figure labels or a cite class. Case is kept as the pack writes it."""
    text = _text(value, "label")
    for allowed in LABELS:
        if text.lower() == allowed.lower():
            return allowed
    raise RecordError("label must be one of: " + ", ".join(LABELS))


def _ids(value: Any, field: str) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        value = [part for part in value.replace(",", " ").split() if part]
    if not isinstance(value, (list, tuple)):
        raise RecordError(f"{field} must be a list of record ids")
    out = []
    for item in value:
        text = _text(item, field, limit=64)
        out.append(text)
    return out


def default_path() -> Path:
    return data_dir() / DB_NAME


class Record:
    """The project record. One instance per app; safe to call from any thread."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _WRITE_LOCK:
            with self._connect() as conn:
                conn.executescript(_SCHEMA)
                _add_missing_columns(conn)
                conn.execute(
                    "INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)",
                    (str(SCHEMA_VERSION),),
                )

    # -- connections -----------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10.0, isolation_level="DEFERRED")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _write(self, work) -> Any:
        """Run work(conn) inside one transaction under the process lock."""
        with _WRITE_LOCK:
            conn = self._connect()
            try:
                with conn:
                    return work(conn)
            finally:
                conn.close()

    def _read(self, sql: str, params: tuple = ()) -> list[dict]:
        conn = self._connect()
        try:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()

    def _event(self, conn: sqlite3.Connection, project_id: str, kind: str, agent: str, payload: dict) -> None:
        conn.execute(
            "INSERT INTO events (project_id, ts, kind, agent, payload) VALUES (?, ?, ?, ?, ?)",
            (project_id, now_text(), kind, agent or "", canonical_json(payload)),
        )

    # -- projects --------------------------------------------------------

    def ensure_project(self, project_id: str, name: str = "") -> None:
        project_id = _text(project_id, "project_id", limit=64)
        name = _text(name, "name", required=False, limit=300) or "Untitled job"

        def work(conn):
            conn.execute(
                "INSERT INTO projects (id, name, created) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET name = excluded.name",
                (project_id, name, now_text()),
            )

        self._write(work)

    def project_row(self, project_id: str) -> dict | None:
        rows = self._read("SELECT * FROM projects WHERE id = ?", (project_id,))
        return rows[0] if rows else None

    def delete_project(self, project_id: str) -> None:
        def work(conn):
            for table in (
                "facts", "evidence", "calc_records", "findings", "questions",
                "decisions", "handoffs", "tasks", "agents", "jobs", "events", "reviews",
            ):
                conn.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        self._write(work)

    # -- facts, evidence, findings, questions, decisions -----------------

    def record_fact(self, project_id: str, *, kind: str, key: str, value: Any, label: str,
                    source: str = "", agent: str = "", supersede: bool | str = False) -> dict:
        """Write one fact. supersede=True marks earlier rows with the same kind and key as replaced.

        supersede="own" replaces only the rows this agent wrote, so two agents that
        disagree on a key both stay current and the disagreement shows.
        """
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "kind": _text(kind, "kind", limit=80),
            "key": _text(key, "key", limit=200),
            "value": _text(value, "value"),
            "label": _label(label),
            "source": _text(source, "source", required=False, limit=2000),
            "agent": _text(agent, "agent", required=False, limit=80),
            "created": now_text(),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO facts (id, project_id, kind, key, value, label, source, agent, created) "
                "VALUES (:id, :project_id, :kind, :key, :value, :label, :source, :agent, :created)",
                row,
            )
            if supersede == "own":
                conn.execute(
                    "UPDATE facts SET superseded_by = ? WHERE project_id = ? AND kind = ? AND key = ? "
                    "AND id != ? AND superseded_by IS NULL AND agent = ?",
                    (row["id"], row["project_id"], row["kind"], row["key"], row["id"], row["agent"]),
                )
            elif supersede:
                conn.execute(
                    "UPDATE facts SET superseded_by = ? WHERE project_id = ? AND kind = ? AND key = ? "
                    "AND id != ? AND superseded_by IS NULL",
                    (row["id"], row["project_id"], row["kind"], row["key"], row["id"]),
                )
            self._event(conn, row["project_id"], "fact", row["agent"], {"id": row["id"], "kind": row["kind"], "key": row["key"]})
            return row

        return self._write(work)

    def sync_basis(self, project_id: str, basis: dict | None, *, agent: str = "job form") -> list[dict]:
        """Bring the form's basis fields onto the record. A changed value supersedes the old row.

        Returns the rows written. An unchanged value writes nothing, so calling
        this on every open, run, and turn is cheap.
        """
        project_id = _text(project_id, "project_id", limit=64)
        basis = basis if isinstance(basis, dict) else {}
        current = {row["key"]: row for row in self.facts(project_id, "basis")}
        written: list[dict] = []
        for key, label in BASIS_LABELS:
            value = str(basis.get(key) or "").strip()
            if not value:
                continue
            row = current.get(key)
            if row is not None and row["value"] == value and row["label"] == label:
                continue
            written.append(self.record_fact(
                project_id, kind="basis", key=key, value=value, label=label,
                source=agent, agent=agent, supersede=True,
            ))
        return written

    def sync_form(self, project_id: str, kind: str, values: dict | None, *, labels: Any = GIVEN,
                  sources: dict | None = None, shown_before: dict | None = None,
                  agent: str = "job form") -> dict:
        """Bring one group of form fields and the record into step, in both directions.

        The form is one editor of the job's inputs and the lead is the other
        (set_input, when the designer states a value in chat). values is what
        the form holds now, by input name, as the text the fact stores.
        shown_before is what the form held the last time it was synced.

        For each input: with no row yet, the form's value is written. When the
        designer changed the field since the last sync, the form's value is
        written and replaces whatever was current. When the field did not
        change and an agent has set the input since, the record's value stands
        and is returned in "pulled" for the caller to put on the form. A
        form-owned row is rewritten when its value or its source changed.

        Returns {"written": rows, "pulled": {name: value text}}. Each written
        row carries "previous", the value it replaced or None. An
        input_changed event is logged for every value that actually changed.
        """
        project_id = _text(project_id, "project_id", limit=64)
        kind = _text(kind, "kind", limit=80)
        values = values if isinstance(values, dict) else {}
        sources = sources if isinstance(sources, dict) else {}
        before = shown_before if isinstance(shown_before, dict) else {}
        current = {row["key"]: row for row in self.facts(project_id, kind)}
        written: list[dict] = []
        pulled: dict[str, str] = {}
        for key, value in values.items():
            text = str(value)
            source = str(sources.get(key) or agent)
            label = labels.get(key, GIVEN) if isinstance(labels, dict) else labels
            row = current.get(key)
            if row is not None:
                agent_set = (row.get("agent") or "") not in FORM_AGENTS
                form_changed = key in before and before[key] != text
                if agent_set and not form_changed:
                    if row["value"] != text:
                        pulled[key] = row["value"]
                    continue
                if not agent_set and row["value"] == text and row["source"] == source and row["label"] == label:
                    continue
                if agent_set and row["value"] == text:
                    # The designer typed the value the lead had already recorded. Nothing changed.
                    continue
            new = self.record_fact(
                project_id, kind=kind, key=key, value=text, label=label,
                source=source, agent=agent, supersede=True,
            )
            new["previous"] = row["value"] if row is not None else None
            if row is not None and row["value"] != text:
                self.log_event(project_id, "input_changed", {
                    "kind": kind, "key": key, "old": row["value"], "new": text, "by": agent,
                    "source": source, "id": new["id"],
                }, agent=agent)
            written.append(new)
        return {"written": written, "pulled": pulled}

    def set_given(self, project_id: str, *, kind: str, key: str, value: str, label: str,
                  source: str, agent: str) -> dict:
        """An agent records an input the designer stated. Returns the row with "previous" and "changed"."""
        current = next((row for row in self.facts(project_id, kind) if row["key"] == key), None)
        row = self.record_fact(
            project_id, kind=kind, key=key, value=value, label=label, source=source, agent=agent, supersede=True,
        )
        row["previous"] = current["value"] if current is not None else None
        row["changed"] = current is None or current["value"] != row["value"]
        if current is not None and row["changed"]:
            self.log_event(project_id, "input_changed", {
                "kind": kind, "key": key, "old": current["value"], "new": row["value"], "by": agent,
                "source": source, "id": row["id"],
            }, agent=agent)
        return row

    def givens(self, project_id: str) -> dict[str, dict]:
        """The current project inputs by name: zone inputs and the basis fields."""
        found: dict[str, dict] = {}
        for row in self.facts(project_id, BASIS_KIND):
            found[row["key"]] = row
        for row in self.facts(project_id, INPUT_KIND):
            found[row["key"]] = row
        return found

    def record_evidence(self, project_id: str, *, document: str, edition: str = "", section: str = "",
                        note: str = "", applicability: str = "", status: str = "held", agent: str = "",
                        depends: Any = None) -> dict:
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "document": _text(document, "document", limit=200),
            "edition": _text(edition, "edition", required=False, limit=40),
            "section": _text(section, "section", required=False, limit=120),
            "note": _text(note, "note", required=False, limit=2000),
            "applicability": _text(applicability, "applicability", required=False, limit=2000),
            "status": _choice(status, "status", EVIDENCE_STATUSES),
            "agent": _text(agent, "agent", required=False, limit=80),
            "created": now_text(),
            "depends": canonical_json(_ids(depends, "depends")),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO evidence (id, project_id, document, edition, section, note, applicability, status, agent, created, depends) "
                "VALUES (:id, :project_id, :document, :edition, :section, :note, :applicability, :status, :agent, :created, :depends)",
                row,
            )
            self._event(conn, row["project_id"], "evidence", row["agent"], {"id": row["id"], "document": row["document"], "section": row["section"]})
            return row

        return self._write(work)

    def record_finding(self, project_id: str, *, agent: str, text: str, label: str,
                       supports: Any = None, replaces: Any = None, may_replace_any: bool = False) -> dict:
        """Write one finding. replaces names an earlier finding this one takes the place of.

        The earlier row stays as history with superseded_by set, and an objection
        still open on it is closed as answered by the revision. Only the author of
        a finding, or the lead (may_replace_any), may replace it.
        """
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "agent": _text(agent, "agent", limit=80),
            "text": _text(text, "text"),
            "label": _label(label),
            "supports": canonical_json(_ids(supports, "supports")),
            "status": "open",
            "created": now_text(),
        }
        old_id = _text(replaces, "replaces", required=False, limit=64)

        def work(conn):
            if old_id:
                old = conn.execute(
                    "SELECT * FROM findings WHERE id = ? AND project_id = ?", (old_id, row["project_id"])
                ).fetchone()
                if old is None:
                    raise RecordError(f"no finding {old_id} on this project to replace")
                if old["superseded_by"]:
                    raise RecordError(f"finding {old_id} was already replaced or withdrawn")
                if old["agent"] != row["agent"] and not may_replace_any:
                    raise RecordError(
                        f"finding {old_id} was written by {old['agent']}. Only its author or the lead replaces it; "
                        "review_finding records an objection."
                    )
            conn.execute(
                "INSERT INTO findings (id, project_id, agent, text, label, supports, status, created) "
                "VALUES (:id, :project_id, :agent, :text, :label, :supports, :status, :created)",
                row,
            )
            self._event(conn, row["project_id"], "finding", row["agent"], {"id": row["id"], "label": row["label"]})
            if old_id:
                conn.execute("UPDATE findings SET superseded_by = ? WHERE id = ?", (row["id"], old_id))
                self._event(conn, row["project_id"], "finding_replaced", row["agent"], {"id": old_id, "by": row["id"]})
                self._close_objections(conn, row["project_id"], old_id,
                                       f"The finding was revised by {row['agent']}: see [{row['id']}].", row["agent"])
                self._close_rulings(conn, row["project_id"], old_id, f"The finding it ruled on was revised: see [{row['id']}].")
                row["replaces"] = old_id
            return row

        return self._write(work)

    def retire_finding(self, project_id: str, finding_id: str, *, by: str, reason: str,
                       may_retire_any: bool = False) -> dict:
        """Withdraw a finding. It stays on the record as history and leaves the current set."""
        finding_id = _text(finding_id, "finding_id", limit=64)
        by = _text(by, "by", limit=80)
        note = _text(reason, "reason", limit=2000)

        def work(conn):
            old = conn.execute(
                "SELECT * FROM findings WHERE id = ? AND project_id = ?", (finding_id, project_id)
            ).fetchone()
            if old is None:
                raise RecordError(f"no finding {finding_id} on this project")
            if old["superseded_by"]:
                raise RecordError(f"finding {finding_id} was already replaced or withdrawn")
            if old["agent"] != by and not may_retire_any:
                raise RecordError(f"finding {finding_id} was written by {old['agent']}. Only its author or the lead withdraws it.")
            conn.execute(
                "UPDATE findings SET superseded_by = ?, retire_note = ? WHERE id = ?", (WITHDRAWN, note, finding_id)
            )
            self._event(conn, project_id, "finding_withdrawn", by, {"id": finding_id})
            self._close_objections(conn, project_id, finding_id, f"The finding was withdrawn by {by}: {note}", by)
            self._close_rulings(conn, project_id, finding_id, f"The finding it ruled on was withdrawn by {by}.")
            row = dict(conn.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone())
            row["supports"] = json.loads(row["supports"] or "[]")
            return row

        return self._write(work)

    def _close_objections(self, conn: sqlite3.Connection, project_id: str, finding_id: str,
                          resolution: str, by: str) -> None:
        rows = conn.execute(
            "SELECT id FROM reviews WHERE project_id = ? AND finding_id = ? AND position = 'object' "
            "AND status IN ('open', 'escalated')",
            (project_id, finding_id),
        ).fetchall()
        for item in rows:
            conn.execute(
                "UPDATE reviews SET status = 'resolved', resolution = ?, resolved_by = ?, updated = ? WHERE id = ?",
                (resolution, by, now_text(), item["id"]),
            )
            self._event(conn, project_id, "review_resolved", by, {"id": item["id"], "finding": finding_id})

    def _close_rulings(self, conn: sqlite3.Connection, project_id: str, finding_id: str, note: str) -> None:
        """A ruling on an objection is over when the finding it ruled on leaves the current set.

        Only a decision written to settle a review (review_id set) closes this
        way. Any other decision that rests on the finding stays, and is out of
        date until its author replaces or withdraws it.
        """
        rows = conn.execute(
            "SELECT id, supports FROM decisions WHERE project_id = ? AND review_id != '' AND superseded_by IS NULL",
            (project_id,),
        ).fetchall()
        for item in rows:
            if finding_id not in _json_list(item["supports"]):
                continue
            conn.execute("UPDATE decisions SET superseded_by = ?, retire_note = ? WHERE id = ?", (WITHDRAWN, note, item["id"]))
            self._event(conn, project_id, "decision_closed", "", {"id": item["id"], "finding": finding_id})

    # -- reviews: one agent's position on another agent's finding ------------------------

    def put_review(self, project_id: str, *, finding_id: str, agent: str, position: str, note: str = "") -> dict:
        """Record agent's position on a finding it did not write. A later call replaces the earlier position.

        An objection is open until its finding is revised or withdrawn, the
        lead resolves it, or the objector changes its position to agree.
        """
        finding_id = _text(finding_id, "finding_id", limit=64)
        agent = _text(agent, "agent", limit=80)
        position = _choice(position, "position", REVIEW_POSITIONS)
        note = _text(note, "note", required=(position == "object"), limit=4000)
        stamp = now_text()

        def work(conn):
            finding = conn.execute(
                "SELECT * FROM findings WHERE id = ? AND project_id = ?", (finding_id, project_id)
            ).fetchone()
            if finding is None:
                raise RecordError(f"no finding {finding_id} on this project")
            if finding["superseded_by"]:
                raise RecordError(f"finding {finding_id} was replaced or withdrawn. Review the current finding.")
            if finding["agent"] == agent:
                raise RecordError("an agent does not review its own finding. Replace it or withdraw it instead.")
            status = "open" if position == "object" else "resolved"
            found = conn.execute(
                "SELECT id FROM reviews WHERE project_id = ? AND finding_id = ? AND agent = ?",
                (project_id, finding_id, agent),
            ).fetchone()
            if found is not None:
                review_id = found["id"]
                conn.execute(
                    "UPDATE reviews SET position = ?, note = ?, status = ?, resolution = '', resolved_by = '', updated = ? "
                    "WHERE id = ?",
                    (position, note, status, stamp, review_id),
                )
            else:
                review_id = new_id()
                conn.execute(
                    "INSERT INTO reviews (id, project_id, finding_id, agent, position, note, status, created, updated) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (review_id, project_id, finding_id, agent, position, note, status, stamp, stamp),
                )
            self._event(conn, project_id, "review_" + position, agent,
                        {"id": review_id, "finding": finding_id, "author": finding["agent"]})
            return dict(conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone())

        return self._write(work)

    def close_review(self, project_id: str, review_id: str, *, status: str, resolution: str, by: str) -> dict:
        """The lead settles an objection (resolved) or sends it to the designer or the engineer (escalated)."""
        review_id = _text(review_id, "review_id", limit=64)
        status = _choice(status, "status", ("resolved", "escalated"))
        resolution = _text(resolution, "resolution", limit=4000)
        by = _text(by, "by", limit=80)

        def work(conn):
            row = conn.execute(
                "SELECT * FROM reviews WHERE id = ? AND project_id = ?", (review_id, project_id)
            ).fetchone()
            if row is None:
                raise RecordError(f"no review {review_id} on this project")
            if row["position"] != "object":
                raise RecordError(f"review {review_id} is not an objection")
            conn.execute(
                "UPDATE reviews SET status = ?, resolution = ?, resolved_by = ?, updated = ? WHERE id = ?",
                (status, resolution, by, now_text(), review_id),
            )
            self._event(conn, project_id, "review_" + status, by, {"id": review_id, "finding": row["finding_id"]})
            return dict(conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone())

        return self._write(work)

    def reviews(self, project_id: str) -> list[dict]:
        return self._read("SELECT * FROM reviews WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def set_finding_status(self, project_id: str, finding_id: str, *, status: str, by: str = "") -> dict:
        """Mark a finding after a check: open, Supported, Not supported, or Source not found."""
        finding_id = _text(finding_id, "finding_id", limit=64)
        status = _choice(status, "status", FINDING_STATUSES)

        def work(conn):
            cur = conn.execute(
                "UPDATE findings SET status = ? WHERE id = ? AND project_id = ?",
                (status, finding_id, project_id),
            )
            if cur.rowcount != 1:
                raise RecordError(f"no finding {finding_id} on this project")
            self._event(conn, project_id, "finding_" + status.replace(" ", "_").lower(), by, {"id": finding_id})
            row = dict(conn.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone())
            row["supports"] = json.loads(row["supports"] or "[]")
            return row

        return self._write(work)

    def open_question(self, project_id: str, *, raised_by: str, text: str, audience: str = "engineer") -> dict:
        """Write a question. audience "designer" is one the team needs answered by the person using the app."""
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "raised_by": _text(raised_by, "raised_by", limit=80),
            "text": _text(text, "text"),
            "status": "open",
            "answer": "",
            "created": now_text(),
            "answered": None,
            "audience": _choice(audience or "engineer", "audience", QUESTION_AUDIENCES),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO questions (id, project_id, raised_by, text, status, answer, created, answered, audience) "
                "VALUES (:id, :project_id, :raised_by, :text, :status, :answer, :created, :answered, :audience)",
                row,
            )
            self._event(conn, row["project_id"], "question", row["raised_by"], {"id": row["id"]})
            return row

        return self._write(work)

    def answer_question(self, project_id: str, question_id: str, *, answer: str, by: str = "") -> dict:
        question_id = _text(question_id, "question_id", limit=64)
        answer_text = _text(answer, "answer")
        by = _text(by, "by", required=False, limit=80)

        def work(conn):
            cur = conn.execute(
                "UPDATE questions SET status = 'answered', answer = ?, answered = ?, answered_by = ? "
                "WHERE id = ? AND project_id = ?",
                (answer_text, now_text(), by, question_id, project_id),
            )
            if cur.rowcount != 1:
                raise RecordError(f"no question {question_id} on this project")
            self._event(conn, project_id, "answer", by, {"id": question_id})
            return dict(conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone())

        return self._write(work)

    def record_decision(self, project_id: str, *, text: str, decided_by: str, label: str,
                        basis: str = "", supports: Any = None, replaces: Any = None,
                        may_replace_any: bool = False, review_id: str = "") -> dict:
        """Write one decision. replaces names an earlier decision this one takes the place of.

        The earlier row stays as history. Only its author, or the lead
        (may_replace_any), may replace it. review_id marks a ruling the lead
        made on an objection; such a ruling closes by itself when the finding
        it ruled on is revised or withdrawn.
        """
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "text": _text(text, "text"),
            "basis": _text(basis, "basis", required=False, limit=4000),
            "decided_by": _text(decided_by, "decided_by", limit=80),
            "label": _label(label),
            "created": now_text(),
            "supports": canonical_json(_ids(supports, "supports")),
            "review_id": _text(review_id, "review_id", required=False, limit=64),
        }
        old_id = _text(replaces, "replaces", required=False, limit=64)

        def work(conn):
            if old_id:
                old = conn.execute(
                    "SELECT * FROM decisions WHERE id = ? AND project_id = ?", (old_id, row["project_id"])
                ).fetchone()
                if old is None:
                    raise RecordError(f"no decision {old_id} on this project to replace")
                if old["superseded_by"]:
                    raise RecordError(f"decision {old_id} was already replaced or withdrawn")
                if old["decided_by"] != row["decided_by"] and not may_replace_any:
                    raise RecordError(f"decision {old_id} was made by {old['decided_by']}. Only its author or the lead replaces it.")
            conn.execute(
                "INSERT INTO decisions (id, project_id, text, basis, decided_by, label, created, supports, review_id) "
                "VALUES (:id, :project_id, :text, :basis, :decided_by, :label, :created, :supports, :review_id)",
                row,
            )
            self._event(conn, row["project_id"], "decision", row["decided_by"], {"id": row["id"], "label": row["label"]})
            if old_id:
                conn.execute("UPDATE decisions SET superseded_by = ? WHERE id = ?", (row["id"], old_id))
                self._event(conn, row["project_id"], "decision_replaced", row["decided_by"], {"id": old_id, "by": row["id"]})
                row["replaces"] = old_id
            row["supports"] = json.loads(row["supports"])
            return row

        return self._write(work)

    def retire_decision(self, project_id: str, decision_id: str, *, by: str, reason: str,
                        may_retire_any: bool = False) -> dict:
        """Withdraw a decision. It stays on the record as history and leaves the current set."""
        decision_id = _text(decision_id, "decision_id", limit=64)
        by = _text(by, "by", limit=80)
        note = _text(reason, "reason", limit=2000)

        def work(conn):
            old = conn.execute(
                "SELECT * FROM decisions WHERE id = ? AND project_id = ?", (decision_id, project_id)
            ).fetchone()
            if old is None:
                raise RecordError(f"no decision {decision_id} on this project")
            if old["superseded_by"]:
                raise RecordError(f"decision {decision_id} was already replaced or withdrawn")
            if old["decided_by"] != by and not may_retire_any:
                raise RecordError(f"decision {decision_id} was made by {old['decided_by']}. Only its author or the lead withdraws it.")
            conn.execute(
                "UPDATE decisions SET superseded_by = ?, retire_note = ? WHERE id = ?", (WITHDRAWN, note, decision_id)
            )
            self._event(conn, project_id, "decision_withdrawn", by, {"id": decision_id})
            row = dict(conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone())
            row["supports"] = _json_list(row.get("supports"))
            return row

        return self._write(work)

    def has_decision(self, project_id: str, decision_id: str) -> bool:
        return bool(self._read("SELECT id FROM decisions WHERE id = ? AND project_id = ?", (decision_id, project_id)))

    # -- calculation records --------------------------------------------

    def record_calc(self, project_id: str, *, tool: str, inputs: Any, outputs: Any,
                    agent: str = "", pack_version: str = "", calc_identity: str = "",
                    depends: Any = None, varies: dict | None = None) -> dict:
        """Store one calc. The same tool, inputs, and calc identity on the project counts a replay.

        calc_identity names the calc code that produced the output. A different
        identity is a different row, so a pack update never replays old results.

        depends lists the record rows this call followed: the input facts whose
        values it used and the earlier calcs whose results it took. varies names
        the arguments where it departed from the project inputs. Both are
        written again on a replay, because a replay is the same call checked
        against the inputs as they are now. None leaves them as they are.
        """
        project_id = _text(project_id, "project_id", limit=64)
        tool = _text(tool, "tool", limit=80)
        calc_identity = _text(calc_identity, "calc_identity", required=False, limit=80)
        digest = input_hash(tool, inputs, calc_identity)
        stamp = now_text()

        def work(conn):
            found = conn.execute(
                "SELECT * FROM calc_records WHERE project_id = ? AND input_hash = ?",
                (project_id, digest),
            ).fetchone()
            if found is not None:
                conn.execute(
                    "UPDATE calc_records SET replay_count = replay_count + 1, last_used = ? WHERE id = ?",
                    (stamp, found["id"]),
                )
                row = dict(found)
                if depends is not None or varies is not None:
                    row["depends"] = canonical_json(_ids(depends, "depends"))
                    row["varies"] = canonical_json(varies if isinstance(varies, dict) else {})
                    conn.execute(
                        "UPDATE calc_records SET depends = ?, varies = ? WHERE id = ?",
                        (row["depends"], row["varies"], found["id"]),
                    )
                self._event(conn, project_id, "calc_replay", agent, {"id": found["id"], "tool": tool})
                row["replay_count"] = int(found["replay_count"]) + 1
                row["last_used"] = stamp
                row["replayed"] = True
                return row
            row = {
                "id": new_id(),
                "project_id": project_id,
                "tool": tool,
                "input_hash": digest,
                "inputs": canonical_json(inputs),
                "outputs": canonical_json(outputs),
                "pack_version": _text(pack_version, "pack_version", required=False, limit=80),
                "calc_identity": calc_identity,
                "agent": _text(agent, "agent", required=False, limit=80),
                "replay_count": 0,
                "created": stamp,
                "last_used": stamp,
                "depends": canonical_json(_ids(depends, "depends")),
                "varies": canonical_json(varies if isinstance(varies, dict) else {}),
            }
            conn.execute(
                "INSERT INTO calc_records (id, project_id, tool, input_hash, inputs, outputs, pack_version, calc_identity, agent, replay_count, created, last_used, depends, varies) "
                "VALUES (:id, :project_id, :tool, :input_hash, :inputs, :outputs, :pack_version, :calc_identity, :agent, :replay_count, :created, :last_used, :depends, :varies)",
                row,
            )
            self._event(conn, project_id, "calc", row["agent"], {"id": row["id"], "tool": tool})
            row["replayed"] = False
            return row

        return self._write(work)

    def set_calc_basis(self, project_id: str, calc_id: str, *, depends: Any, varies: dict | None) -> None:
        """Write what a calc followed onto a row recorded before the record kept it. No event; nothing ran."""
        calc_id = _text(calc_id, "calc_id", limit=64)
        self._write(lambda conn: conn.execute(
            "UPDATE calc_records SET depends = ?, varies = ? WHERE id = ? AND project_id = ?",
            (canonical_json(_ids(depends, "depends")), canonical_json(varies if isinstance(varies, dict) else {}),
             calc_id, project_id),
        ))

    def find_calc(self, project_id: str, tool: str, inputs: Any, calc_identity: str = "") -> dict | None:
        """The row for this tool, these inputs, and this calc code, or None."""
        rows = self._read(
            "SELECT * FROM calc_records WHERE project_id = ? AND input_hash = ?",
            (project_id, input_hash(tool, inputs, calc_identity)),
        )
        if not rows:
            return None
        return _calc_row(rows[0])

    def calc(self, project_id: str, calc_id: str) -> dict | None:
        rows = self._read("SELECT * FROM calc_records WHERE project_id = ? AND id = ?", (project_id, calc_id))
        return _calc_row(rows[0]) if rows else None

    def detail(self, project_id: str, kind: str, row_id: str | None = None) -> list[dict]:
        """Full rows of one kind, or the one row with row_id. kind is a snapshot key."""
        readers = {
            "facts": lambda: self.facts(project_id),
            "evidence": lambda: self.evidence(project_id),
            "calcs": lambda: self.calcs(project_id),
            "findings": lambda: self.findings(project_id),
            "questions": lambda: self.questions(project_id),
            "decisions": lambda: self.decisions(project_id),
            "handoffs": lambda: self.handoffs(project_id),
            "tasks": lambda: self.tasks(project_id),
            "agents": lambda: self.agents(project_id),
            "jobs": lambda: self.jobs(project_id),
            "reviews": lambda: self.reviews(project_id),
        }
        if kind not in readers:
            raise RecordError("kind must be one of: " + ", ".join(sorted(readers)))
        rows = readers[kind]()
        if row_id:
            rows = [row for row in rows if row.get("id") == row_id]
        return rows

    # -- handoffs, tasks, agents ------------------------------------------

    def create_handoff(self, project_id: str, *, from_agent: str, to_agent: str, brief: str,
                       payload: Any = None, kind: str = "handoff") -> dict:
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "from_agent": _text(from_agent, "from_agent", limit=80),
            "to_agent": _text(to_agent, "to_agent", limit=80),
            "brief": _text(brief, "brief"),
            "payload": canonical_json(payload if payload is not None else {}),
            "status": "pending",
            "result": "",
            "created": now_text(),
            "delivered": None,
            "returned": None,
            "kind": _choice(kind or "handoff", "kind", HANDOFF_KINDS),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO handoffs (id, project_id, from_agent, to_agent, brief, payload, status, result, created, delivered, returned, kind) "
                "VALUES (:id, :project_id, :from_agent, :to_agent, :brief, :payload, :status, :result, :created, :delivered, :returned, :kind)",
                row,
            )
            self._event(conn, row["project_id"], "handoff", row["from_agent"],
                        {"id": row["id"], "to": row["to_agent"], "kind": row["kind"]})
            return row

        return self._write(work)

    def set_handoff(self, project_id: str, handoff_id: str, *, status: str, result: Any = None,
                    by: str = "") -> dict:
        handoff_id = _text(handoff_id, "handoff_id", limit=64)
        status = _choice(status, "status", HANDOFF_STATUSES)
        stamp = now_text()

        def work(conn):
            sets = ["status = ?"]
            params: list[Any] = [status]
            if status == "delivered":
                sets.append("delivered = ?")
                params.append(stamp)
            if status in ("returned", "cancelled"):
                sets.append("returned = ?")
                params.append(stamp)
            if result is not None:
                sets.append("result = ?")
                params.append(result if isinstance(result, str) else canonical_json(result))
            params.extend([handoff_id, project_id])
            cur = conn.execute(
                f"UPDATE handoffs SET {', '.join(sets)} WHERE id = ? AND project_id = ?",
                tuple(params),
            )
            if cur.rowcount != 1:
                raise RecordError(f"no handoff {handoff_id} on this project")
            self._event(conn, project_id, f"handoff_{status}", by, {"id": handoff_id})
            return dict(conn.execute("SELECT * FROM handoffs WHERE id = ?", (handoff_id,)).fetchone())

        return self._write(work)

    def pending_handoffs(self, project_id: str, to_agent: str | None = None) -> list[dict]:
        if to_agent:
            return self._read(
                "SELECT * FROM handoffs WHERE project_id = ? AND status = 'pending' AND to_agent = ? ORDER BY created, rowid",
                (project_id, to_agent),
            )
        return self._read(
            "SELECT * FROM handoffs WHERE project_id = ? AND status = 'pending' ORDER BY created, rowid",
            (project_id,),
        )

    def add_task(self, project_id: str, *, title: str, owner: str = "", status: str = "open") -> dict:
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "title": _text(title, "title", limit=500),
            "owner": _text(owner, "owner", required=False, limit=80),
            "status": _choice(status, "status", TASK_STATUSES),
            "created": now_text(),
            "updated": now_text(),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO tasks (id, project_id, title, owner, status, created, updated) "
                "VALUES (:id, :project_id, :title, :owner, :status, :created, :updated)",
                row,
            )
            self._event(conn, row["project_id"], "task", row["owner"], {"id": row["id"], "status": row["status"]})
            return row

        return self._write(work)

    def set_task(self, project_id: str, task_id: str, *, status: str, by: str = "") -> dict:
        task_id = _text(task_id, "task_id", limit=64)
        status = _choice(status, "status", TASK_STATUSES)

        def work(conn):
            cur = conn.execute(
                "UPDATE tasks SET status = ?, updated = ? WHERE id = ? AND project_id = ?",
                (status, now_text(), task_id, project_id),
            )
            if cur.rowcount != 1:
                raise RecordError(f"no task {task_id} on this project")
            self._event(conn, project_id, "task_" + status, by, {"id": task_id})
            return dict(conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

        return self._write(work)

    def set_agent(self, project_id: str, *, name: str, role_slug: str, status: str) -> dict:
        row = {
            "project_id": _text(project_id, "project_id", limit=64),
            "name": _text(name, "name", limit=80),
            "role_slug": _text(role_slug, "role_slug", limit=80),
            "status": _choice(status, "status", AGENT_STATUSES),
            "last_active": now_text(),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO agents (project_id, name, role_slug, status, last_active) "
                "VALUES (:project_id, :name, :role_slug, :status, :last_active) "
                "ON CONFLICT(project_id, name) DO UPDATE SET role_slug = excluded.role_slug, "
                "status = excluded.status, last_active = excluded.last_active",
                row,
            )
            self._event(conn, row["project_id"], "agent_" + row["status"], row["name"], {"role": row["role_slug"]})
            return row

        return self._write(work)

    def log_event(self, project_id: str, kind: str, payload: Any = None, agent: str = "") -> None:
        project_id = _text(project_id, "project_id", limit=64)
        kind = _text(kind, "kind", limit=80)
        self._write(lambda conn: self._event(conn, project_id, kind, agent, payload if isinstance(payload, dict) else {"value": payload}))

    # -- jobs and recovery ---------------------------------------------------

    def set_job(self, project_id: str, *, job_id: str, kind: str, title: str = "", status: str,
                error: str = "") -> dict:
        """Keep a window job on the record so a relaunch can tell what was in flight.

        A job never moves back: a late "queued" after "running" is ignored, and a
        finished job stays finished. An unchanged status writes no event.
        """
        row = {
            "id": _text(job_id, "job_id", limit=64),
            "project_id": _text(project_id, "project_id", limit=64),
            "kind": _text(kind, "kind", limit=40),
            "title": _text(title, "title", required=False, limit=500),
            "status": _choice(status, "status", JOB_STATUSES),
            "error": _text(error, "error", required=False, limit=2000),
            "started": now_text(),
            "updated": now_text(),
        }

        def work(conn):
            current = conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
            if current is not None:
                if _JOB_RANK[row["status"]] < _JOB_RANK[current["status"]]:
                    return dict(current)
                if current["status"] == row["status"] and (current["error"] == row["error"] or not row["error"]):
                    return dict(current)
                conn.execute(
                    "UPDATE jobs SET status = ?, error = ?, title = ?, updated = ? WHERE id = ?",
                    (row["status"], row["error"] or current["error"], row["title"] or current["title"],
                     row["updated"], row["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO jobs (id, project_id, kind, title, status, error, started, updated) "
                    "VALUES (:id, :project_id, :kind, :title, :status, :error, :started, :updated)",
                    row,
                )
            self._event(conn, row["project_id"], "job_" + row["status"], "", {"id": row["id"], "kind": row["kind"]})
            return dict(conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone())

        return self._write(work)

    def jobs(self, project_id: str, status: str | None = None) -> list[dict]:
        if status:
            return self._read(
                "SELECT * FROM jobs WHERE project_id = ? AND status = ? ORDER BY started, rowid", (project_id, status)
            )
        return self._read("SELECT * FROM jobs WHERE project_id = ? ORDER BY started, rowid", (project_id,))

    def recover(self) -> dict[str, dict]:
        """The launch pass. Nothing can still be running when the app starts, so every
        queued or running job and every working agent is marked interrupted, and every
        delivered handoff goes back to pending so the next delegation to its receiver
        delivers it again. The same rows are updated; no row is copied. One transaction.

        Returns, per project that changed, its name and the jobs, agents, and
        handoffs touched. A second call finds nothing and returns an empty dict.
        """
        stamp = now_text()

        def work(conn):
            report: dict[str, dict] = {}

            def entry(project_id: str) -> dict:
                if project_id not in report:
                    name_row = conn.execute("SELECT name FROM projects WHERE id = ?", (project_id,)).fetchone()
                    report[project_id] = {
                        "name": (name_row["name"] if name_row else "") or "Untitled job",
                        "jobs": [], "agents": [], "handoffs": [],
                    }
                return report[project_id]

            for row in conn.execute("SELECT * FROM jobs WHERE status IN ('queued', 'running') ORDER BY started").fetchall():
                conn.execute(
                    "UPDATE jobs SET status = 'interrupted', error = ?, updated = ? WHERE id = ?",
                    (INTERRUPTED_NOTE, stamp, row["id"]),
                )
                self._event(conn, row["project_id"], "job_interrupted", "", {"id": row["id"], "kind": row["kind"], "was": row["status"]})
                item = dict(row)
                item["status"] = "interrupted"
                item["error"] = INTERRUPTED_NOTE
                entry(row["project_id"])["jobs"].append(item)
            for row in conn.execute("SELECT * FROM agents WHERE status = 'working'").fetchall():
                conn.execute(
                    "UPDATE agents SET status = 'interrupted', last_active = ? WHERE project_id = ? AND name = ?",
                    (stamp, row["project_id"], row["name"]),
                )
                self._event(conn, row["project_id"], "agent_interrupted", row["name"], {"role": row["role_slug"], "by": "recovery"})
                entry(row["project_id"])["agents"].append(row["name"])
            for row in conn.execute("SELECT * FROM handoffs WHERE status = 'delivered' ORDER BY created").fetchall():
                conn.execute(
                    "UPDATE handoffs SET status = 'pending', delivered = NULL, result = ? WHERE id = ?",
                    (REQUEUED_NOTE, row["id"]),
                )
                self._event(conn, row["project_id"], "handoff_requeued", "", {"id": row["id"], "to": row["to_agent"]})
                entry(row["project_id"])["handoffs"].append(
                    {"id": row["id"], "from_agent": row["from_agent"], "to_agent": row["to_agent"], "brief": row["brief"]}
                )
            for project_id, item in report.items():
                # The whole item goes on the event, so a later launch can still say what
                # was in flight if the designer never opened the job this time.
                self._event(conn, project_id, "recovered", "", {
                    "jobs": [{"id": row["id"], "kind": row["kind"], "title": row["title"]} for row in item["jobs"]],
                    "agents": list(item["agents"]),
                    "handoffs": list(item["handoffs"]),
                })
            return report

        return self._write(work)

    def unnoted_recoveries(self) -> dict[str, dict]:
        """Recoveries whose note the designer has not seen, merged per project.

        A `recovered` event stays owed until a `recovery_noted` event follows it on
        that project. Items look like recover()'s report. Empty when nothing is owed.
        """
        rows = self._read(
            "SELECT project_id, kind, payload FROM events WHERE kind IN ('recovered', 'recovery_noted') ORDER BY seq"
        )
        owed: dict[str, dict] = {}
        for row in rows:
            project_id = row["project_id"]
            if row["kind"] == "recovery_noted":
                owed.pop(project_id, None)
                continue
            payload = json.loads(row["payload"] or "{}")
            item = owed.setdefault(project_id, {"name": "", "jobs": [], "agents": [], "handoffs": []})
            for key in ("jobs", "agents", "handoffs"):
                values = payload.get(key)
                if not isinstance(values, list):
                    continue
                for value in values:
                    if value not in item[key]:
                        item[key].append(value)
        for project_id, item in owed.items():
            project = self.project_row(project_id) or {}
            item["name"] = project.get("name") or "Untitled job"
        return owed

    def note_recovery(self, project_id: str) -> None:
        """The recovery note for this project reached its thread. Later launches owe nothing for it."""
        self.log_event(project_id, "recovery_noted", {})

    # -- reads --------------------------------------------------------------

    def facts(self, project_id: str, kind: str | None = None, *, include_superseded: bool = False) -> list[dict]:
        where = "project_id = ?"
        params: list[Any] = [project_id]
        if kind:
            where += " AND kind = ?"
            params.append(kind)
        if not include_superseded:
            where += " AND superseded_by IS NULL"
        return self._read(f"SELECT * FROM facts WHERE {where} ORDER BY created, rowid", tuple(params))

    def evidence(self, project_id: str) -> list[dict]:
        rows = self._read("SELECT * FROM evidence WHERE project_id = ? ORDER BY created, rowid", (project_id,))
        for row in rows:
            row["depends"] = _json_list(row.get("depends"))
        return rows

    def calcs(self, project_id: str) -> list[dict]:
        return [_calc_row(row) for row in self._read(
            "SELECT * FROM calc_records WHERE project_id = ? ORDER BY created, rowid", (project_id,)
        )]

    def findings(self, project_id: str, agent: str | None = None, *, include_retired: bool = False) -> list[dict]:
        """The current findings: those not replaced and not withdrawn. include_retired adds the history."""
        where = "project_id = ?"
        params: list[Any] = [project_id]
        if agent:
            where += " AND agent = ?"
            params.append(agent)
        if not include_retired:
            where += " AND superseded_by IS NULL"
        rows = self._read(f"SELECT * FROM findings WHERE {where} ORDER BY created, rowid", tuple(params))
        for row in rows:
            row["supports"] = json.loads(row["supports"] or "[]")
        return rows

    def questions(self, project_id: str, status: str | None = None) -> list[dict]:
        if status:
            return self._read("SELECT * FROM questions WHERE project_id = ? AND status = ? ORDER BY created, rowid", (project_id, status))
        return self._read("SELECT * FROM questions WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def decisions(self, project_id: str, *, include_retired: bool = False) -> list[dict]:
        """The current decisions: those not replaced and not withdrawn. include_retired adds the history."""
        where = "project_id = ?" + ("" if include_retired else " AND superseded_by IS NULL")
        rows = self._read(f"SELECT * FROM decisions WHERE {where} ORDER BY created, rowid", (project_id,))
        for row in rows:
            row["supports"] = _json_list(row.get("supports"))
        return rows

    def handoffs(self, project_id: str) -> list[dict]:
        rows = self._read("SELECT * FROM handoffs WHERE project_id = ? ORDER BY created, rowid", (project_id,))
        for row in rows:
            row["payload"] = json.loads(row["payload"] or "{}")
        return rows

    def tasks(self, project_id: str) -> list[dict]:
        return self._read("SELECT * FROM tasks WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def agents(self, project_id: str) -> list[dict]:
        return self._read("SELECT * FROM agents WHERE project_id = ? ORDER BY name", (project_id,))

    def latest_event(self, project_id: str, kind: str) -> dict | None:
        rows = self._read(
            "SELECT * FROM events WHERE project_id = ? AND kind = ? ORDER BY seq DESC LIMIT 1",
            (project_id, kind),
        )
        if not rows:
            return None
        row = rows[0]
        row["payload"] = json.loads(row["payload"] or "{}")
        return row

    def events_by_kind(self, project_id: str, kinds: tuple[str, ...] | list[str]) -> list[dict]:
        """Every event of these kinds on the project, oldest first, with no row limit.

        events() is a recent window for a screen. A total, such as the job's cost,
        has to read the whole history, so it comes here.
        """
        names = [str(kind) for kind in kinds if str(kind)]
        if not names:
            return []
        marks = ", ".join("?" for _ in names)
        rows = self._read(
            f"SELECT * FROM events WHERE project_id = ? AND kind IN ({marks}) ORDER BY seq",
            (project_id, *names),
        )
        for row in rows:
            row["payload"] = json.loads(row["payload"] or "{}")
        return rows

    def events(self, project_id: str, limit: int = 500) -> list[dict]:
        rows = self._read(
            "SELECT * FROM events WHERE project_id = ? ORDER BY seq DESC LIMIT ?", (project_id, int(limit))
        )
        rows.reverse()
        for row in rows:
            row["payload"] = json.loads(row["payload"] or "{}")
        return rows

    def unseen_answers(self, project_id: str) -> list[str]:
        """Questions the designer answered on the panel since a lead turn last read the job's status.

        Read by event order, not by clock, so an answer given while a turn was
        running is news to the next turn and an answer a turn has seen is not.
        """
        rows = self._read(
            "SELECT payload FROM events WHERE project_id = ? AND kind = 'answer' AND agent = ? AND seq > "
            "COALESCE((SELECT MAX(seq) FROM events WHERE project_id = ? AND kind = ?), 0) ORDER BY seq",
            (project_id, ANSWERED_ON_PANEL, project_id, TURN_START),
        )
        found: list[str] = []
        for row in rows:
            ident = json.loads(row["payload"] or "{}").get("id")
            if ident and ident not in found:
                found.append(ident)
        return found

    def snapshot(self, project_id: str) -> dict:
        """Every table for one project. The export reads this, not the database."""
        return {
            "project": self.project_row(project_id),
            "facts": self.facts(project_id),
            # Every fact row, replaced ones included: what a value was when a calc used it.
            "fact_history": self.facts(project_id, include_superseded=True),
            "evidence": self.evidence(project_id),
            "calcs": self.calcs(project_id),
            "findings": self.findings(project_id),
            # Findings that were replaced or withdrawn, kept as history.
            "retired_findings": [row for row in self.findings(project_id, include_retired=True) if row.get("superseded_by")],
            "reviews": self.reviews(project_id),
            "questions": self.questions(project_id),
            "retired_decisions": [row for row in self.decisions(project_id, include_retired=True) if row.get("superseded_by")],
            "decisions": self.decisions(project_id),
            "handoffs": self.handoffs(project_id),
            "tasks": self.tasks(project_id),
            "agents": self.agents(project_id),
            "jobs": self.jobs(project_id),
            "events": self.events(project_id),
            # The newest event of each kind a view reads whole. events is a recent window and
            # could miss one on a long job.
            "latest": {kind: self.latest_event(project_id, kind) for kind in LATEST_KINDS},
            "unseen_answers": self.unseen_answers(project_id),
        }

    def summary_text(self, project_id: str, *, max_rows: int = 40) -> str:
        """Short plain-text view of the record for a model turn, with row ids and each row's standing.

        Not the export. fpfa.status builds it, so a model reads the same view
        everywhere: out-of-date rows are marked, and a calc output is the
        reader's view of it.
        """
        from fpfa import status

        return status.record_text(self.snapshot(project_id), max_rows=max_rows)

    # -- migration from the JSON job files ---------------------------------

    def import_project(self, project: dict, *, agent: str = "migration") -> dict:
        """Bring a JSON job's basis and finished runs into the record, once.

        Returns counts. A second call on the same project does nothing.
        """
        project_id = _text(project.get("id"), "project id", limit=64)
        self.ensure_project(project_id, str(project.get("name") or "Untitled job"))
        row = self.project_row(project_id) or {}
        if row.get("migrated_at"):
            return {"migrated": False, "facts": 0, "calcs": 0}
        basis = project.get("basis") if isinstance(project.get("basis"), dict) else {}
        facts = len(self.sync_basis(project_id, basis, agent=agent))
        calcs = 0
        for run_key in ("last_run", "bess_run"):
            run = project.get(run_key)
            if not isinstance(run, dict):
                continue
            for call in run.get("transcript") or []:
                if not isinstance(call, dict) or call.get("is_error"):
                    continue
                name = str(call.get("name") or "")
                if name not in CALC_TOOLS:
                    continue
                self.record_calc(
                    project_id,
                    tool=name,
                    inputs=call.get("input"),
                    outputs=call.get("output"),
                    agent=str(call.get("by") or "tool-plan"),
                )
                calcs += 1

        def work(conn):
            conn.execute("UPDATE projects SET migrated_at = ? WHERE id = ?", (now_text(), project_id))
            self._event(conn, project_id, "migrated", agent, {"facts": facts, "calcs": calcs})

        self._write(work)
        return {"migrated": True, "facts": facts, "calcs": calcs}


# Form-owned basis fields and the label each one carries on the record.
BASIS_LABELS = (
    ("ahj", "use best judgment"),
    ("nfpa_13", "CODE"),
    ("nfpa_72", "CODE"),
    ("insurer", "OWNER"),
    ("hazard_notes", "use best judgment"),
)


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    """Columns added after the first schema. A fresh database already has them."""
    wanted = {
        "calc_records": [
            ("calc_identity", "TEXT NOT NULL DEFAULT ''"),
            ("depends", "TEXT NOT NULL DEFAULT '[]'"),
            ("varies", "TEXT NOT NULL DEFAULT '{}'"),
        ],
        "facts": [("superseded_by", "TEXT")],
        "evidence": [("depends", "TEXT NOT NULL DEFAULT '[]'")],
        "findings": [("superseded_by", "TEXT"), ("retire_note", "TEXT NOT NULL DEFAULT ''")],
        "questions": [("audience", "TEXT NOT NULL DEFAULT 'engineer'"), ("answered_by", "TEXT NOT NULL DEFAULT ''")],
        "decisions": [("supports", "TEXT NOT NULL DEFAULT '[]'"), ("superseded_by", "TEXT"),
                      ("retire_note", "TEXT NOT NULL DEFAULT ''"), ("review_id", "TEXT NOT NULL DEFAULT ''")],
        "handoffs": [("kind", "TEXT NOT NULL DEFAULT 'handoff'")],
    }
    for table, columns in wanted.items():
        present = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, spec in columns:
            if name not in present:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {spec}")


def _calc_row(row: dict) -> dict:
    out = dict(row)
    out["inputs"] = json.loads(row["inputs"]) if isinstance(row.get("inputs"), str) else row.get("inputs")
    out["outputs"] = json.loads(row["outputs"]) if isinstance(row.get("outputs"), str) else row.get("outputs")
    out["depends"] = _json_list(row.get("depends"))
    varies = row.get("varies")
    if isinstance(varies, str):
        try:
            varies = json.loads(varies or "{}")
        except json.JSONDecodeError:
            varies = {}
    out["varies"] = varies if isinstance(varies, dict) else {}
    return out


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if not isinstance(value, str) or not value:
        return []
    try:
        found = json.loads(value)
    except json.JSONDecodeError:
        return []
    return found if isinstance(found, list) else []
