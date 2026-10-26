"""Inbox, queue, and workers for long desktop jobs.

A zone run that calls the model, and a typed chat turn, are jobs. submit()
returns as soon as the job is on the queue. Worker threads run the callable.
The window thread stays free, so the composer can take another message.

Each job keeps the project id it was started with. A result is labeled with
that job. Callers write the result onto that project, including when a later
job finishes first.
"""

from __future__ import annotations

import queue
import re
import threading
import uuid
from dataclasses import dataclass

KINDS = ("zone", "chat")
STATUSES = ("queued", "running", "done", "error")
_KEY_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")


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
        return f"{self.status:<7} {self.kind:<4} {name}  {self.id}"


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
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for _ in self._threads:
                self._queue.put(None)
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
