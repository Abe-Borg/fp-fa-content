"""Inbox, queue, and workers for long desktop jobs.

A zone run that calls the model, a typed chat turn, an explosion-control
starter that calls the model, a blind claim check, and a heavy job are jobs.
submit() returns as soon as the job is on the queue. Worker threads run the
callable. The window thread stays free, so the composer can take another
message.

A heavy job is the only kind that may call the hosted runtime. A claim check
uses the Messages path. The worker still posts the result back through the
same inbox. Each job keeps the project id it was started with. A result is
labeled with that job. Callers write the result onto that project, including
when a later job finishes first.
"""

from __future__ import annotations

import logging
import queue
import re
import threading
import uuid
from dataclasses import dataclass
from typing import Callable

KINDS = ("zone", "chat", "bess", "heavy", "claim")
STATUSES = ("queued", "running", "done", "error", "cancelled")
_KEY_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")
_log = logging.getLogger("fpfa.jobs")
_hooks_lock = threading.Lock()
_close_hooks: list[Callable[[], None]] = []
# Backstop so a hook cannot hold the window thread on a hosted HTTP call.
# The hosted sweep uses a shorter budget and should finish inside this join.
CLOSE_HOOK_DEADLINE = 1.25


def register_inbox_close_hook(hook: Callable[[], None]) -> None:
    """Run hook from JobInbox.close before the worker join.

    The hosted client registers a hook that deletes in-flight heavy sessions.
    A hook that raises is logged. It does not stop the other hooks or the join.
    """
    with _hooks_lock:
        if hook not in _close_hooks:
            _close_hooks.append(hook)


def _run_close_hooks() -> None:
    """Run close hooks off the caller thread and wait at most CLOSE_HOOK_DEADLINE.

    The window calls close() on the Tk thread. A hosted DELETE uses a long
    HTTP timeout, so the hook runs on a daemon thread. The join is the bound.
    A hook still running when the join ends stays tracked by the hosted
    client for process exit; it is not treated as finished.
    """
    with _hooks_lock:
        hooks = list(_close_hooks)
    if not hooks:
        return

    def run() -> None:
        for hook in hooks:
            try:
                hook()
            except Exception:
                _log.exception("inbox close hook failed")

    thread = threading.Thread(target=run, name="fpfa-close-hooks", daemon=True)
    thread.start()
    thread.join(CLOSE_HOOK_DEADLINE)
    if thread.is_alive():
        _log.error(
            "inbox close hooks still running after %.2fs",
            CLOSE_HOOK_DEADLINE,
        )


def _scrub(text: str) -> str:
    return _KEY_RE.sub("[key]", text)[:800]


def _clean_name(name: str | None) -> str:
    text = " ".join((name or "").split())
    return text or "Untitled job"


def _short(text: str, limit: int = 80) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


@dataclass
class Job:
    id: str
    project_id: str
    project_name: str
    kind: str
    title: str
    status: str = "queued"
    error: str = ""

    def heading(self) -> str:
        """Visible label so a finished result names the job it belongs to."""
        name = _clean_name(self.project_name)
        base = f"Job {self.id} | {name} | {self.kind}"
        title = _short(self.title)
        if not title:
            return base
        return f"{base} | {title}"

    def inbox_line(self) -> str:
        name = _clean_name(self.project_name)
        return f"{self.status:<7} {self.kind:<5} {name}  {self.id}"


def label_result(heading: str, body: str) -> str:
    """Put the job heading on its own line above the result body."""
    heading = (heading or "").strip()
    body = body or ""
    if not heading:
        return body
    if not body:
        return heading
    return f"{heading}\n{body}"


class JobInbox:
    """In-memory inbox plus a worker queue.

    work(job_id) runs on a worker thread. It must not touch Tk widgets.
    Post window updates from work() onto the UI queue instead.
    """

    def __init__(self, worker_count: int = 2, on_change=None):
        if worker_count < 1:
            raise ValueError("worker_count must be at least 1")
        self.worker_count = worker_count
        self._on_change = on_change
        self._lock = threading.Lock()
        self._jobs: dict[str, Job] = {}
        self._order: list[str] = []
        self._queue: queue.Queue = queue.Queue()
        self._closed = False
        self._threads: list[threading.Thread] = []
        for index in range(worker_count):
            thread = threading.Thread(
                target=self._worker,
                name=f"fpfa-worker-{index + 1}",
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)

    def submit(
        self,
        *,
        project_id: str,
        project_name: str,
        kind: str,
        title: str,
        work,
    ) -> Job:
        """Queue work and return the job. The caller does not wait for work()."""
        if kind not in KINDS:
            raise ValueError(f"Unknown job kind {kind}")
        job = self._new(project_id, project_name, kind, title, "queued")
        with self._lock:
            if self._closed:
                raise RuntimeError("The inbox is closed.")
            self._jobs[job.id] = job
            self._order.append(job.id)
            self._queue.put((job.id, work))
        self._notify()
        return self._copy(job)

    def record(
        self,
        *,
        project_id: str,
        project_name: str,
        kind: str,
        title: str,
        status: str = "done",
        error: str = "",
    ) -> Job:
        """Remember a job that ran on the caller. No worker is used."""
        if kind not in KINDS:
            raise ValueError(f"Unknown job kind {kind}")
        if status not in STATUSES:
            raise ValueError(f"Unknown job status {status}")
        job = self._new(project_id, project_name, kind, title, status)
        job.error = _scrub(error) if error else ""
        with self._lock:
            if self._closed:
                raise RuntimeError("The inbox is closed.")
            self._jobs[job.id] = job
            self._order.append(job.id)
        self._notify()
        return self._copy(job)

    def mark(self, job_id: str, status: str, error: str = "") -> None:
        if status not in STATUSES:
            raise ValueError(f"Unknown job status {status}")
        self._set_status(job_id, status, error)

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return self._copy(job)

    def snapshot(self) -> list[Job]:
        """Jobs in submission order."""
        with self._lock:
            return [self._copy(self._jobs[job_id]) for job_id in self._order]

    def close(self) -> None:
        """Stop taking work, run close hooks, then join workers for about a second.

        Workers are daemons. The join does not cancel a job that is already
        running. Close hooks run on a side thread and are joined for
        CLOSE_HOOK_DEADLINE, so a slow hosted DELETE cannot hold this caller
        for the HTTP timeout. Process exit repeats that delete for any
        session the hook did not finish, including one whose DELETE is still
        on the network.
        """
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for _ in self._threads:
                self._queue.put(None)
        _run_close_hooks()
        for thread in self._threads:
            thread.join(timeout=1.0)

    def _new(self, project_id: str, project_name: str, kind: str, title: str, status: str) -> Job:
        return Job(
            id=uuid.uuid4().hex[:12],
            project_id=project_id,
            project_name=_clean_name(project_name),
            kind=kind,
            title=_short(title, limit=240),
            status=status,
        )

    def _copy(self, job: Job) -> Job:
        return Job(
            id=job.id,
            project_id=job.project_id,
            project_name=job.project_name,
            kind=job.kind,
            title=job.title,
            status=job.status,
            error=job.error,
        )

    def _set_status(self, job_id: str, status: str, error: str = "") -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.status = status
            if error:
                job.error = _scrub(error)
        self._notify()

    def _notify(self) -> None:
        callback = self._on_change
        if callback is None:
            return
        try:
            callback()
        except Exception:
            return

    def _worker(self) -> None:
        while True:
            item = self._queue.get()
            try:
                if item is None:
                    return
                job_id, work = item
                self._set_status(job_id, "running")
                try:
                    work(job_id)
                except Exception as exc:
                    self._set_status(job_id, "error", _scrub(f"{type(exc).__name__}: {exc}"))
                else:
                    with self._lock:
                        current = self._jobs.get(job_id)
                        if current is not None and current.status == "running":
                            current.status = "done"
                    self._notify()
            finally:
                self._queue.task_done()
