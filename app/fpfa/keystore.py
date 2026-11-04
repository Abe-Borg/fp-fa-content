"""Store the user's Anthropic API key on this machine.

Windows uses Credential Manager through the keyring package (install pywin32).
Other desktops store a user-only file unless FPFA_USE_KEYRING=1, because a
missing system keyring can open a blocking password dialog. The key is never
written into a project.

A source run calls keyring in a short-lived child Python process. A packaged
(PyInstaller) app cannot do that, because sys.executable is fpfa.exe, not
Python. It calls keyring in-process on one worker thread with the same
timeout. That thread runs calls in the order they were made, so a call that
timed out cannot land after a later save.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

from fpfa.paths import data_dir, read_config, write_config

SERVICE = "fpfa-assistant"
ACCOUNT = "anthropic-api-key"


def _key_file() -> Path:
    return data_dir() / "anthropic-api-key"


def _read_file() -> str:
    path = _key_file()
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _write_file(key: str) -> None:
    path = _key_file()
    path.write_text(key.strip(), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _delete_file() -> None:
    path = _key_file()
    if path.is_file():
        path.unlink()


def _is_frozen() -> bool:
    """True in a PyInstaller build, where sys.executable is the app, not Python."""
    return bool(getattr(sys, "frozen", False))


def _keyring_call(action: str, secret: str | None = None, timeout: float = 2.0) -> str:
    """Run one keyring action without letting a stuck backend hang the app.

    Raises subprocess.TimeoutExpired, RuntimeError, or OSError on failure.
    """
    if _is_frozen():
        return _keyring_in_process(action, secret, timeout)
    return _keyring_subprocess(action, secret, timeout)


def _keyring_action(action: str, secret: str | None) -> str:
    """The same work as the child script in _keyring_subprocess, in this process."""
    import keyring

    if sys.platform == "win32":
        try:
            # Registers WinVaultKeyring even if the bundle lost keyring's entry points.
            import keyring.backends.Windows  # noqa: F401
        except ImportError:
            pass
    if action == "set":
        keyring.set_password(SERVICE, ACCOUNT, secret or "")
        return "ok"
    if action == "get":
        value = keyring.get_password(SERVICE, ACCOUNT)
        return "" if value is None else value
    if action == "delete":
        try:
            keyring.delete_password(SERVICE, ACCOUNT)
        except Exception:
            pass
        return "ok"
    raise ValueError("unknown action")


_keyring_jobs: queue.SimpleQueue = queue.SimpleQueue()
_keyring_worker: threading.Thread | None = None
_keyring_worker_lock = threading.Lock()


def _run_keyring_jobs() -> None:
    """Run keyring calls one at a time, in the order they were queued."""
    while True:
        action, secret, outcome, done = _keyring_jobs.get()
        try:
            outcome["value"] = _keyring_action(action, secret)
        except BaseException as exc:  # noqa: BLE001 - reported to the caller
            outcome["error"] = exc
        finally:
            done.set()


def _keyring_in_process(action: str, secret: str | None, timeout: float) -> str:
    """Queue one keyring call on the worker thread and wait up to timeout for it.

    A call that times out stays queued and still runs. Later calls wait behind
    it, so a slow delete cannot remove a key saved after it.
    """
    global _keyring_worker
    with _keyring_worker_lock:
        if _keyring_worker is None or not _keyring_worker.is_alive():
            _keyring_worker = threading.Thread(target=_run_keyring_jobs, name="fpfa-keyring", daemon=True)
            _keyring_worker.start()
    outcome: dict[str, object] = {}
    done = threading.Event()
    _keyring_jobs.put((action, secret, outcome, done))
    if not done.wait(timeout):
        raise subprocess.TimeoutExpired(cmd="keyring", timeout=timeout)
    error = outcome.get("error")
    if error is not None:
        detail = str(error).strip() or type(error).__name__
        raise RuntimeError(detail.splitlines()[-1][:300])
    return str(outcome.get("value") or "").strip()


def _keyring_subprocess(action: str, secret: str | None, timeout: float) -> str:
    """Run keyring in a child Python so a missing secret service cannot hang the app."""
    script = r"""
import sys
import keyring
action, service, account = sys.argv[1:4]
if action == "set":
    keyring.set_password(service, account, sys.stdin.read())
    print("ok")
elif action == "get":
    value = keyring.get_password(service, account)
    sys.stdout.write("" if value is None else value)
elif action == "delete":
    try:
        keyring.delete_password(service, account)
    except Exception:
        pass
    print("ok")
else:
    raise SystemExit("unknown action")
"""
    proc = subprocess.run(
        [sys.executable, "-c", script, action, SERVICE, ACCOUNT],
        input=secret or "",
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "keyring failed").strip()
        raise RuntimeError(detail.splitlines()[-1][:300])
    return (proc.stdout or "").strip()


def _use_os_keyring() -> bool:
    """Windows Credential Manager is the default store.

    Other desktops often pop a blocking "create a keyring password" dialog
    when no keyring exists. Those builds use the user-only file unless
    FPFA_USE_KEYRING=1.
    """
    flag = os.environ.get("FPFA_USE_KEYRING")
    if flag == "1":
        return True
    if flag == "0":
        return False
    return sys.platform == "win32"


def key_backend() -> str:
    return read_config().get("key_backend") or ""


def load_api_key() -> str:
    backend = key_backend()
    if backend == "file" or (not _use_os_keyring() and backend != "keyring"):
        return _read_file()
    if backend == "keyring" or _use_os_keyring():
        try:
            value = _keyring_call("get", timeout=8 if sys.platform == "win32" else 2)
            if value:
                return value
        except (subprocess.TimeoutExpired, RuntimeError, OSError):
            pass
        return _read_file()
    # First lookup. Prefer the OS keyring, and remember a file fallback.
    try:
        value = _keyring_call("get", timeout=8 if sys.platform == "win32" else 2)
        if value:
            write_config({"key_backend": "keyring"})
            return value
    except (subprocess.TimeoutExpired, RuntimeError, OSError):
        write_config({"key_backend": "file"})
    return _read_file()


def save_api_key(key: str) -> str:
    """Return 'keyring' or 'file' depending on where the key was stored."""
    cleaned = key.strip()
    if not cleaned:
        raise ValueError("API key is empty")
    if not _use_os_keyring() and key_backend() != "keyring":
        _write_file(cleaned)
        write_config({"key_backend": "file"})
        return "file"
    timeout = 8 if sys.platform == "win32" else 2
    try:
        _keyring_call("set", cleaned, timeout=timeout)
        _delete_file()
        write_config({"key_backend": "keyring"})
        return "keyring"
    except (subprocess.TimeoutExpired, RuntimeError, OSError):
        _write_file(cleaned)
        write_config({"key_backend": "file"})
        return "file"


def clear_api_key() -> None:
    try:
        _keyring_call("delete", timeout=2)
    except (subprocess.TimeoutExpired, RuntimeError, OSError):
        pass
    _delete_file()


def key_storage_help() -> str:
    """Shown in Settings so a designer can see where Save key will put the key."""
    return (
        "On Windows the key is stored in Credential Manager when keyring and pywin32 are available. "
        "The packaged Windows app bundles keyring and its Credential Manager support. "
        "If Credential Manager cannot store it, the key is stored in a user-only file under "
        "%APPDATA%\\fpfa-assistant. On other computers that user-only file is the default unless "
        "FPFA_USE_KEYRING=1. The key is not written into the project, the chat, or the exported section."
    )


def key_status() -> str:
    """One line for the status bar and Settings. Names the store that holds the key."""
    if not load_api_key():
        return "No API key saved."
    backend = key_backend() or "file"
    if backend == "keyring" and sys.platform == "win32":
        return "API key stored in Windows Credential Manager (this PC only)."
    if backend == "keyring":
        return "API key stored in the system keyring (this computer only)."
    if sys.platform == "win32" and _is_frozen():
        return (
            "API key stored in a user-only file. Credential Manager did not take it in this "
            "packaged app. Save the key again; if it still lands here, reinstall the app."
        )
    if sys.platform == "win32":
        return (
            "API key stored in a user-only file. Credential Manager did not take it. "
            "Install pywin32 if it is missing, then save the key again."
        )
    return "API key stored in a user-only file on this computer (not in the project)."
