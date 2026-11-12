"""Project files live in the per-user data directory, not in the content pack."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fpfa.inputs import BASIS_STARTING
from fpfa.paths import data_dir


def project_dir() -> Path:
    path = data_dir() / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_project(name: str, basis: dict | None = None) -> dict:
    """A new job. A basis field not given here holds its starting value (fpfa.inputs.BASIS_STARTING).

    Nobody stated a starting value: until the designer types or states one,
    the record and every view say it is not confirmed (inputs.provenance).
    """
    basis = dict(basis or {})
    data = {
        "id": uuid.uuid4().hex,
        "name": name.strip() or "Untitled job",
        "created": _now(),
        "updated": _now(),
        "basis": {
            "ahj": basis.get("ahj", ""),
            "nfpa_13": basis.get("nfpa_13", BASIS_STARTING["nfpa_13"]),
            "nfpa_72": basis.get("nfpa_72", BASIS_STARTING["nfpa_72"]),
            "insurer": basis.get("insurer", BASIS_STARTING["insurer"]),
            "hazard_notes": basis.get("hazard_notes", ""),
        },
        "di": {},
        "chat": [],
        "last_run": None,
    }
    save_project(data)
    return data


def list_projects() -> list[dict]:
    rows = []
    for path in project_dir().glob("*.json"):
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda row: row.get("updated", ""), reverse=True)
    return rows


def load_project(project_id: str) -> dict:
    path = project_dir() / f"{project_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def save_project(data: dict) -> dict:
    data["updated"] = _now()
    path = project_dir() / f"{data['id']}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def delete_project(project_id: str) -> None:
    path = project_dir() / f"{project_id}.json"
    if path.is_file():
        path.unlink()
