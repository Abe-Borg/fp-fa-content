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

from fpfa.paths import data_dir

DB_NAME = "fpfa.db"
SCHEMA_VERSION = 1

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
)
EVIDENCE_STATUSES = ("held", "NOT PULLED", "NEEDS HOLD", "PACKAGE ASSERTION")
QUESTION_STATUSES = ("open", "answered", "withdrawn")
HANDOFF_STATUSES = ("pending", "delivered", "returned", "cancelled")
FINDING_STATUSES = ("open", "Supported", "Not supported", "Source not found")
TASK_STATUSES = ("open", "working", "done", "blocked", "cancelled")
AGENT_STATUSES = ("idle", "working", "done", "error", "interrupted")

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
    created TEXT NOT NULL
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
    created TEXT NOT NULL
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
    agent TEXT NOT NULL DEFAULT '',
    replay_count INTEGER NOT NULL DEFAULT 0,
    created TEXT NOT NULL,
    last_used TEXT NOT NULL,
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
    created TEXT NOT NULL
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
    answered TEXT
);
CREATE INDEX IF NOT EXISTS questions_project ON questions(project_id, status);
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    text TEXT NOT NULL,
    basis TEXT NOT NULL DEFAULT '',
    decided_by TEXT NOT NULL,
    label TEXT NOT NULL,
    created TEXT NOT NULL
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
    returned TEXT
);
CREATE INDEX IF NOT EXISTS handoffs_project ON handoffs(project_id, status);
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


def input_hash(tool: str, inputs: Any) -> str:
    return hashlib.sha256(canonical_json({"tool": tool, "inputs": inputs}).encode("utf-8")).hexdigest()


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
                conn.execute(
                    "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)",
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
                "decisions", "handoffs", "tasks", "agents", "events",
            ):
                conn.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        self._write(work)

    # -- facts, evidence, findings, questions, decisions -----------------

    def record_fact(self, project_id: str, *, kind: str, key: str, value: Any, label: str,
                    source: str = "", agent: str = "") -> dict:
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
            self._event(conn, row["project_id"], "fact", row["agent"], {"id": row["id"], "kind": row["kind"], "key": row["key"]})
            return row

        return self._write(work)

    def record_evidence(self, project_id: str, *, document: str, edition: str = "", section: str = "",
                        note: str = "", applicability: str = "", status: str = "held", agent: str = "") -> dict:
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
        }

        def work(conn):
            conn.execute(
                "INSERT INTO evidence (id, project_id, document, edition, section, note, applicability, status, agent, created) "
                "VALUES (:id, :project_id, :document, :edition, :section, :note, :applicability, :status, :agent, :created)",
                row,
            )
            self._event(conn, row["project_id"], "evidence", row["agent"], {"id": row["id"], "document": row["document"], "section": row["section"]})
            return row

        return self._write(work)

    def record_finding(self, project_id: str, *, agent: str, text: str, label: str,
                       supports: Any = None) -> dict:
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

        def work(conn):
            conn.execute(
                "INSERT INTO findings (id, project_id, agent, text, label, supports, status, created) "
                "VALUES (:id, :project_id, :agent, :text, :label, :supports, :status, :created)",
                row,
            )
            self._event(conn, row["project_id"], "finding", row["agent"], {"id": row["id"], "label": row["label"]})
            return row

        return self._write(work)

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

    def open_question(self, project_id: str, *, raised_by: str, text: str) -> dict:
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "raised_by": _text(raised_by, "raised_by", limit=80),
            "text": _text(text, "text"),
            "status": "open",
            "answer": "",
            "created": now_text(),
            "answered": None,
        }

        def work(conn):
            conn.execute(
                "INSERT INTO questions (id, project_id, raised_by, text, status, answer, created, answered) "
                "VALUES (:id, :project_id, :raised_by, :text, :status, :answer, :created, :answered)",
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
                "UPDATE questions SET status = 'answered', answer = ?, answered = ? "
                "WHERE id = ? AND project_id = ?",
                (answer_text, now_text(), question_id, project_id),
            )
            if cur.rowcount != 1:
                raise RecordError(f"no question {question_id} on this project")
            self._event(conn, project_id, "answer", by, {"id": question_id})
            return dict(conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone())

        return self._write(work)

    def record_decision(self, project_id: str, *, text: str, decided_by: str, label: str,
                        basis: str = "") -> dict:
        row = {
            "id": new_id(),
            "project_id": _text(project_id, "project_id", limit=64),
            "text": _text(text, "text"),
            "basis": _text(basis, "basis", required=False, limit=4000),
            "decided_by": _text(decided_by, "decided_by", limit=80),
            "label": _label(label),
            "created": now_text(),
        }

        def work(conn):
            conn.execute(
                "INSERT INTO decisions (id, project_id, text, basis, decided_by, label, created) "
                "VALUES (:id, :project_id, :text, :basis, :decided_by, :label, :created)",
                row,
            )
            self._event(conn, row["project_id"], "decision", row["decided_by"], {"id": row["id"], "label": row["label"]})
            return row

        return self._write(work)

    # -- calculation records --------------------------------------------

    def record_calc(self, project_id: str, *, tool: str, inputs: Any, outputs: Any,
                    agent: str = "", pack_version: str = "") -> dict:
        """Store one calc. A second identical call on the project counts a replay."""
        project_id = _text(project_id, "project_id", limit=64)
        tool = _text(tool, "tool", limit=80)
        digest = input_hash(tool, inputs)
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
                self._event(conn, project_id, "calc_replay", agent, {"id": found["id"], "tool": tool})
                row = dict(found)
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
                "agent": _text(agent, "agent", required=False, limit=80),
                "replay_count": 0,
                "created": stamp,
                "last_used": stamp,
            }
            conn.execute(
                "INSERT INTO calc_records (id, project_id, tool, input_hash, inputs, outputs, pack_version, agent, replay_count, created, last_used) "
                "VALUES (:id, :project_id, :tool, :input_hash, :inputs, :outputs, :pack_version, :agent, :replay_count, :created, :last_used)",
                row,
            )
            self._event(conn, project_id, "calc", row["agent"], {"id": row["id"], "tool": tool})
            row["replayed"] = False
            return row

        return self._write(work)

    def find_calc(self, project_id: str, tool: str, inputs: Any) -> dict | None:
        rows = self._read(
            "SELECT * FROM calc_records WHERE project_id = ? AND input_hash = ?",
            (project_id, input_hash(tool, inputs)),
        )
        if not rows:
            return None
        return _calc_row(rows[0])

    # -- handoffs, tasks, agents ------------------------------------------

    def create_handoff(self, project_id: str, *, from_agent: str, to_agent: str, brief: str,
                       payload: Any = None) -> dict:
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
        }

        def work(conn):
            conn.execute(
                "INSERT INTO handoffs (id, project_id, from_agent, to_agent, brief, payload, status, result, created, delivered, returned) "
                "VALUES (:id, :project_id, :from_agent, :to_agent, :brief, :payload, :status, :result, :created, :delivered, :returned)",
                row,
            )
            self._event(conn, row["project_id"], "handoff", row["from_agent"], {"id": row["id"], "to": row["to_agent"]})
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
                "SELECT * FROM handoffs WHERE project_id = ? AND status = 'pending' AND to_agent = ? ORDER BY created",
                (project_id, to_agent),
            )
        return self._read(
            "SELECT * FROM handoffs WHERE project_id = ? AND status = 'pending' ORDER BY created",
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

    # -- reads --------------------------------------------------------------

    def facts(self, project_id: str, kind: str | None = None) -> list[dict]:
        if kind:
            return self._read("SELECT * FROM facts WHERE project_id = ? AND kind = ? ORDER BY created, rowid", (project_id, kind))
        return self._read("SELECT * FROM facts WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def evidence(self, project_id: str) -> list[dict]:
        return self._read("SELECT * FROM evidence WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def calcs(self, project_id: str) -> list[dict]:
        return [_calc_row(row) for row in self._read(
            "SELECT * FROM calc_records WHERE project_id = ? ORDER BY created, rowid", (project_id,)
        )]

    def findings(self, project_id: str, agent: str | None = None) -> list[dict]:
        if agent:
            rows = self._read("SELECT * FROM findings WHERE project_id = ? AND agent = ? ORDER BY created, rowid", (project_id, agent))
        else:
            rows = self._read("SELECT * FROM findings WHERE project_id = ? ORDER BY created, rowid", (project_id,))
        for row in rows:
            row["supports"] = json.loads(row["supports"] or "[]")
        return rows

    def questions(self, project_id: str, status: str | None = None) -> list[dict]:
        if status:
            return self._read("SELECT * FROM questions WHERE project_id = ? AND status = ? ORDER BY created, rowid", (project_id, status))
        return self._read("SELECT * FROM questions WHERE project_id = ? ORDER BY created, rowid", (project_id,))

    def decisions(self, project_id: str) -> list[dict]:
        return self._read("SELECT * FROM decisions WHERE project_id = ? ORDER BY created, rowid", (project_id,))

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

    def events(self, project_id: str, limit: int = 500) -> list[dict]:
        rows = self._read(
            "SELECT * FROM events WHERE project_id = ? ORDER BY seq DESC LIMIT ?", (project_id, int(limit))
        )
        rows.reverse()
        for row in rows:
            row["payload"] = json.loads(row["payload"] or "{}")
        return rows

    def snapshot(self, project_id: str) -> dict:
        """Every table for one project. The export reads this, not the database."""
        return {
            "project": self.project_row(project_id),
            "facts": self.facts(project_id),
            "evidence": self.evidence(project_id),
            "calcs": self.calcs(project_id),
            "findings": self.findings(project_id),
            "questions": self.questions(project_id),
            "decisions": self.decisions(project_id),
            "handoffs": self.handoffs(project_id),
            "tasks": self.tasks(project_id),
            "agents": self.agents(project_id),
            "events": self.events(project_id),
        }

    def summary_text(self, project_id: str, *, max_rows: int = 40) -> str:
        """Short plain-text view of the record for a model turn. Not the export."""
        snap = self.snapshot(project_id)
        lines = []
        if snap["facts"]:
            lines.append("Facts:")
            for row in snap["facts"][:max_rows]:
                lines.append(f"- [{row['id']}] {row['kind']}/{row['key']}: {row['value']} ({row['label']})")
        if snap["calcs"]:
            lines.append("Calculation records:")
            for row in snap["calcs"][:max_rows]:
                lines.append(f"- [{row['id']}] {row['tool']} by {row['agent'] or 'tool'}; replays {row['replay_count']}")
        if snap["findings"]:
            lines.append("Findings:")
            for row in snap["findings"][:max_rows]:
                lines.append(f"- [{row['id']}] {row['agent']}: {row['text']} ({row['label']})")
        if snap["decisions"]:
            lines.append("Decisions:")
            for row in snap["decisions"][:max_rows]:
                lines.append(f"- [{row['id']}] {row['text']} ({row['label']}; {row['decided_by']})")
        open_questions = [row for row in snap["questions"] if row["status"] == "open"]
        if open_questions:
            lines.append("Open questions:")
            for row in open_questions[:max_rows]:
                lines.append(f"- [{row['id']}] {row['text']} (raised by {row['raised_by']})")
        pending = [row for row in snap["handoffs"] if row["status"] == "pending"]
        if pending:
            lines.append("Pending handoffs:")
            for row in pending[:max_rows]:
                lines.append(f"- [{row['id']}] {row['from_agent']} to {row['to_agent']}: {row['brief']}")
        return "\n".join(lines) if lines else "The project record is empty."

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
        facts = 0
        basis = project.get("basis") if isinstance(project.get("basis"), dict) else {}
        for key, label in (("ahj", "use best judgment"), ("nfpa_13", "CODE"), ("nfpa_72", "CODE"),
                           ("insurer", "OWNER"), ("hazard_notes", "use best judgment")):
            value = str(basis.get(key) or "").strip()
            if value:
                self.record_fact(project_id, kind="basis", key=key, value=value, label=label,
                                 source="job form", agent=agent)
                facts += 1
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


def _calc_row(row: dict) -> dict:
    out = dict(row)
    out["inputs"] = json.loads(row["inputs"]) if isinstance(row.get("inputs"), str) else row.get("inputs")
    out["outputs"] = json.loads(row["outputs"]) if isinstance(row.get("outputs"), str) else row.get("outputs")
    return out
