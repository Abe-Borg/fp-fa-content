"""One window per data directory.

The record is one SQLite file and the inbox is in memory. A second window on
the same data directory would, at its launch, mark the first window's live
jobs interrupted and re-queue handoffs that are still being worked. An OS
file lock on ``fpfa.lock`` in the data directory stops that: the first window
takes it, a second one is refused with a message, and the operating system
drops it when the process ends, kill included, so a crash never leaves a
stale lock behind.
"""

from __future__ import annotations

import os
from pathlib import Path

LOCK_NAME = "fpfa.lock"
ANOTHER_WINDOW_TEXT = (
    "FP/FA Design Assistant is already open on this data directory. "
    "Use that window, or close it and start again. Two windows on one record "
    "would each treat the other's running work as interrupted."
)


class InstanceLockError(RuntimeError):
    """Another process holds the data directory."""


class InstanceLock:
    """A non-blocking exclusive lock on one file, held for the life of the process."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._handle = None

    @property
    def held(self) -> bool:
        return self._handle is not None

    def acquire(self) -> bool:
        """Take the lock without waiting. True when this object now holds it."""
        if self._handle is not None:
            return True
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(self.path, "a+b")
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            return False
        self._handle = handle
        try:
            # The pid is for a person looking at the file. The lock itself is the OS's.
            handle.seek(0)
            handle.truncate()
            handle.write(f"{os.getpid()}\n".encode("ascii"))
            handle.flush()
        except OSError:
            pass
        return True

    def release(self) -> None:
        """Give the lock back. Safe to call twice. The OS does this at exit anyway."""
        handle = self._handle
        if handle is None:
            return
        self._handle = None
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            handle.close()
