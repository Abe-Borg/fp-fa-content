"""Whether the record still hangs together after something changed.

Two jobs, both read-only on the engineering:

1. When a calc tool runs on a job, work out what the call followed: which
   project inputs it used at their current values, which earlier calcs it
   took a result from, and where it departed from the project inputs. The
   record stores that beside the calc (depends, varies).

2. Given a record snapshot, say which rows are no longer current. An input
   that changed after a calc used it makes that calc out of date. A calc
   that took its volume from an out-of-date takeoff is out of date too. A
   finding or a decision resting on either is out of date, as is a cite
   whose edition changed. Nothing is deleted and nothing is recomputed
   here: the rows are marked with the reason, and they stay marked until
   the calc is run again or the finding is replaced or withdrawn.

The link between a tool argument and a project input is plumbing, the same
plumbing workflow.run_tool_plan uses to fill the arguments from the form.
It is not a method: this module never computes or defaults a figure. The
defaults listed here are the ones calc_tools passes when a caller leaves an
argument out, so a call that omits an argument is compared on what the tool
actually used.

A tool with no entry here (fp_calc, fa_calc, lfl_setpoints, resolve_pipe_id)
is not tracked. Its rows are never marked out of date by an input change.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from fpfa import inputs
from fpfa.record import WITHDRAWN

# tool -> argument -> (project input it is filled from, what the tool uses when it is left out)
BINDINGS: dict[str, dict[str, tuple[str, Any]]] = {
    "zone_trapped_volume": {
        "segments": ("segments", None),
        "length_basis": ("length_basis", "center_to_center"),
        "fittings_percent": ("fittings_percent", None),
        "trim_gal": ("trim_gal", None),
    },
    "dry_delivery_screen": {
        "segments": ("segments", None),
        "q_fill_gpm": ("q_fill_gpm", None),
        "qod": ("qod", False),
        "t_detect_s": ("t_detect_s", 0),
        "t_release_s": ("t_release_s", 0),
        "t_exhaust_s": ("t_exhaust_s", 0),
        "basis": ("delivery_basis", "FM"),
        "system_type": ("system_type", "di"),
    },
    "di_trip_to_water": {
        "q_fill_gpm": ("q_fill_gpm", None),
        "t_detect_s": ("t_detect_s", 0),
        "t_release_s": ("t_release_s", 0),
        "t_exhaust_s": ("t_exhaust_s", 0),
        "basis": ("delivery_basis", "FM"),
    },
    "density_area": {
        "density_gpm_ft2": ("density_gpm_ft2", None),
        "base_area_ft2": ("base_area_ft2", None),
        "area_increase": ("area_increase", 0),
        "hose_gpm": ("hose_gpm", 0),
    },
    "hose_duration": {
        "hazard": ("hazard", "ordinary"),
        "supervised": ("supervised", False),
    },
    "nitrogen_gate": {
        "p_psig": ("supervisory_psig", 40),
        "t_min": ("fill_minutes", 30),
    },
    "elect_di_trim": {
        "system_type": ("system_type", ""),
        "prime_held_by": ("prime_held_by", "unknown"),
        "failsafe_on_total_power_loss": ("failsafe_on_total_power_loss", False),
        "supervisory_psi": ("supervisory_psi", None),
        "medium": ("medium", "unelected"),
        "insurer": ("insurer", ""),
    },
    "releasing_truth_table": {
        "manual_station": ("manual_station", True),
        "insurer": ("insurer", "FM"),
    },
}
# Arguments the screen only applies when the caller passes them. Left out, nothing was used.
_ONLY_WHEN_PASSED = {"dry_delivery_screen": ("trim_gal", "fittings_percent")}
# tool -> argument -> (the tool whose result it is taken from, that result's key)
DERIVED: dict[str, dict[str, tuple[str, str]]] = {
    "di_trip_to_water": {"v_gal": ("zone_trapped_volume", "zone_gal")},
    "nitrogen_gate": {"v_gal": ("zone_trapped_volume", "zone_gal")},
    "density_area": {"duration_min": ("hose_duration", "duration_min")},
}
TRACKED_TOOLS = frozenset(BINDINGS) | frozenset(DERIVED)
# A cite follows the edition the job names for its document.
_EDITION_OF = (
    (re.compile(r"\bNFPA\s*13\b(?!\s*[DR])", re.I), "nfpa_13"),
    (re.compile(r"\bNFPA\s*72\b", re.I), "nfpa_72"),
    (re.compile(r"\bFM\b"), "insurer"),
)
CURRENT = "current"
STALE = "stale"
ALTERNATIVE = "alternative"
_ID = re.compile(r"\b[0-9a-f]{16}\b")


def given_value(row: dict | None) -> Any:
    """The value of an input fact row. Zone inputs are JSON text; basis fields are plain text."""
    if row is None:
        return None
    if row.get("kind") == inputs.INPUT_KIND:
        return inputs.decode(row.get("value"))
    return row.get("value")


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _effective(value: Any, default: Any) -> Any:
    return default if _blank(value) else value


def _segments_same(used: Any, given: Any, resolve_id: Callable | None) -> bool:
    """Whether two segment lists are the same pipe: the same lengths and diameters, in order."""
    if not isinstance(used, list) or not isinstance(given, list) or len(used) != len(given):
        return False
    return all(_segment_same(a, b, resolve_id) for a, b in zip(used, given))


def _diameter(row: dict, resolve_id: Callable | None) -> float | None:
    value = row.get("d_in")
    if value not in (None, ""):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    if resolve_id is None or row.get("nps") in (None, ""):
        return None
    try:
        return float(resolve_id(row.get("nps"), row.get("schedule"), row.get("role"))["d_in"])
    except Exception:
        return None


def _segment_same(used: Any, given: Any, resolve_id: Callable | None) -> bool:
    if not isinstance(used, dict) or not isinstance(given, dict):
        return False
    try:
        a_len = float(used.get("length_ft", used.get("length")))
        b_len = float(given.get("length_ft", given.get("length")))
    except (TypeError, ValueError):
        return False
    if abs(a_len - b_len) > 1e-6:
        return False
    a_d, b_d = _diameter(used, resolve_id), _diameter(given, resolve_id)
    if a_d is not None and b_d is not None:
        return abs(a_d - b_d) <= 5e-4
    return str(used.get("nps") or "") == str(given.get("nps") or "") and \
        str(used.get("schedule") or "") == str(given.get("schedule") or "")


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _result_matches(used: Any, result: Any) -> bool:
    """A figure a caller passed against a recorded result. A model often passes the figure rounded."""
    a, b = _number(used), _number(result)
    if a is None or b is None:
        return False
    return abs(a - b) <= max(0.05, 0.002 * abs(b))


def call_basis(
    tool: str,
    args: dict | None,
    givens: dict[str, dict] | None,
    calcs: list[dict] | None = None,
    *,
    resolve_id: Callable | None = None,
    stale: set[str] | None = None,
    alternative: set[str] | None = None,
) -> tuple[list[str], dict]:
    """What one calc call followed, and where it departed from the project inputs.

    Returns (depends, varies). depends holds the ids of the input facts whose
    current values the call used and of the earlier calcs it took a figure
    from. varies maps an argument to {"used", "project", "input"} when the
    call used another value than the project input, or to {"used", "from",
    "note"} when a figure that should come from an earlier calc matches none.
    With no inputs on the record there is nothing to follow and both are empty.

    stale and alternative are the ids of the recorded calcs that are out of
    date or ran on another case (analyze). A figure that matches more than one
    recorded result is tied to one that ran on the project inputs when there
    is one, so a call is not marked as an alternative on a coincidence.
    """
    args = args if isinstance(args, dict) else {}
    givens = givens or {}
    depends: list[str] = []
    varies: dict[str, dict] = {}
    for arg, (name, default) in (BINDINGS.get(tool) or {}).items():
        row = givens.get(name)
        if row is None:
            continue
        used = _effective(args.get(arg), default)
        project = _effective(given_value(row), default)
        if name == "segments":
            matches = _segments_same(used, project, resolve_id)
        else:
            matches = inputs.same(used, project)
        if matches:
            depends.append(row["id"])
        else:
            varies[arg] = {"used": _plain(used), "project": _plain(project), "input": name}
    for arg in _ONLY_WHEN_PASSED.get(tool, ()):
        row = givens.get(arg)
        if row is None or _blank(args.get(arg)):
            continue
        if inputs.same(args.get(arg), given_value(row)):
            depends.append(row["id"])
        else:
            varies[arg] = {"used": _plain(args.get(arg)), "project": _plain(given_value(row)), "input": arg}
    for arg, (source_tool, key) in (DERIVED.get(tool) or {}).items():
        if _blank(args.get(arg)):
            continue
        candidates = [row for row in (calcs or []) if row.get("tool") == source_tool
                      and isinstance(row.get("outputs"), dict)]
        matching = [row for row in candidates if _result_matches(args.get(arg), row["outputs"].get(key))]
        if matching:
            # The newest matching result that ran on the project inputs; failing that, the newest that is not
            # out of date; failing that, the newest.
            fresh = [row for row in matching if row["id"] not in (stale or set())]
            design = [row for row in fresh if row["id"] not in (alternative or set())]
            depends.append((design or fresh or matching)[-1]["id"])
        else:
            note = (f"matches no recorded {source_tool} result" if candidates
                    else f"no {source_tool} result is on the record")
            varies[arg] = {"used": _plain(args.get(arg)), "from": source_tool, "note": note}
    return depends, varies


def _plain(value: Any) -> Any:
    """A value small enough to keep in the varies column and to print in one line."""
    if isinstance(value, list):
        return f"{len(value)} segment{'s' if len(value) != 1 else ''}"
    return value


def evidence_basis(document: str, givens: dict[str, dict] | None) -> list[str]:
    """The edition fact a cite follows: NFPA 13 cites follow the job's NFPA 13 edition, and so on."""
    found: list[str] = []
    for pattern, name in _EDITION_OF:
        if pattern.search(document or "") and (givens or {}).get(name) is not None:
            found.append(givens[name]["id"])
    return found


def varies_text(varies: dict | None) -> str:
    """One sentence on where a call departed from the project inputs. Empty when it did not."""
    parts = []
    for arg, item in (varies or {}).items():
        if not isinstance(item, dict):
            continue
        if "project" in item:
            name = item.get("input") or arg
            shown = "blank" if _blank(item.get("project")) else item.get("project")
            parts.append(f"{arg} {item.get('used')} where the project input {name} is {shown}")
        else:
            parts.append(f"{arg} {item.get('used')}: {item.get('note')}")
    return "; ".join(parts)


def _carried_text(tool: str, calc_id: str, note: str) -> str:
    """How a calc that took a figure from an alternative says so. It reads after "ran on" like varies_text."""
    return f"a figure from {tool} [{calc_id}], which ran on {note}"


def departure_text(depends: list | None, varies: dict | None, calcs: dict[str, dict] | None,
                   standing: dict[str, dict] | None) -> str:
    """Where a call departs from the project inputs: its own arguments, then what it took from an alternative.

    calcs and standing are the recorded calcs by id and analyze()'s answer for
    them. This is the note analyze() gives the call's row once it is recorded,
    worked out beforehand so the tool result can carry it. Empty when the call
    is the design case.
    """
    parts = [varies_text(varies)]
    for ident in depends or []:
        item = (standing or {}).get(ident)
        if item is not None and ident in (calcs or {}) and item.get("state") == ALTERNATIVE:
            parts.append(_carried_text(calcs[ident]["tool"], ident, item["note"]))
    return "; ".join(part for part in parts if part)


# -- what is still current ----------------------------------------------------------------

def _fact_changes(history: list[dict]) -> dict[str, dict]:
    """For every fact row, whether its value was since replaced by a different one.

    A row replaced by a row with the same value (a re-confirmed input) did not change.
    An input the designer emptied on the form (Record.clear_given) changed, to
    nothing, until it is stated again; then it is compared with what states it now.
    """
    by_id = {row["id"]: row for row in history}
    stated = {(row.get("kind"), row.get("key")): row for row in history if not row.get("superseded_by")}
    out: dict[str, dict] = {}
    for row in history:
        current = row
        seen = set()
        while current.get("superseded_by") and current["superseded_by"] in by_id and current["id"] not in seen:
            seen.add(current["id"])
            current = by_id[current["superseded_by"]]
        if current.get("superseded_by") == WITHDRAWN:
            later = stated.get((row.get("kind"), row.get("key")))
            if later is None:
                held = given_value(row)
                held = inputs.show(row["key"], held) if row.get("kind") == inputs.INPUT_KIND else held
                name = row["key"] if row.get("kind") == inputs.INPUT_KIND else f"{row['kind']}/{row['key']}"
                out[row["id"]] = {"changed": True, "reason": f"{name} was emptied on the form; it was {held}",
                                  "key": row.get("key"), "current_id": "", "emptied": True}
                continue
            current = later
        if current is row:
            out[row["id"]] = {"changed": False, "reason": ""}
            continue
        if row.get("kind") == inputs.INPUT_KIND:
            old, new = given_value(row), given_value(current)
            changed = not inputs.same(old, new)
            reason = f"{row['key']} changed from {inputs.show(row['key'], old)} to {inputs.show(row['key'], new)}"
        else:
            old, new = row.get("value"), current.get("value")
            changed = str(old).strip() != str(new).strip()
            reason = f"{row['kind']}/{row['key']} changed from {old} to {new}"
        if changed:
            who = current.get("source") or current.get("agent") or ""
            reason += f" ({who}, {str(current.get('created') or '')[:16].replace('T', ' ')})" if who else ""
        out[row["id"]] = {"changed": changed, "reason": reason if changed else "", "key": row.get("key"),
                          "current_id": current["id"]}
    return out


def analyze(snapshot: dict | None) -> dict:
    """Which rows of a record snapshot are current, out of date, or an alternative, and why.

    States. A calc is "stale" when an input it used has since changed, or a
    calc it took a figure from is stale; "alternative" when it ran on another
    value than a project input, or took a figure from a calc that did; else
    "current". A cite is stale when the edition it follows changed. A finding
    or a decision is stale when a row it rests on is stale, was replaced, or
    was withdrawn.
    """
    snap = snapshot or {}
    history = list(snap.get("fact_history") or snap.get("facts") or [])
    facts = _fact_changes(history)
    calcs = {row["id"]: row for row in snap.get("calcs") or []}
    evidence = {row["id"]: row for row in snap.get("evidence") or []}
    findings = {row["id"]: row for row in snap.get("findings") or []}
    retired = {row["id"]: row for row in snap.get("retired_findings") or []}
    decisions = {row["id"]: row for row in snap.get("decisions") or []}
    calc_state: dict[str, dict] = {}

    def calc_standing(calc_id: str, trail: tuple = ()) -> dict:
        if calc_id in calc_state:
            return calc_state[calc_id]
        row = calcs[calc_id]
        reasons: list[str] = []
        carried: list[str] = []
        for ident in row.get("depends") or []:
            if ident in facts and facts[ident]["changed"]:
                reasons.append(facts[ident]["reason"])
            elif ident in calcs and ident not in trail and ident != calc_id:
                upstream = calc_standing(ident, trail + (calc_id,))
                if upstream["state"] == STALE:
                    reasons.append(f"it took a figure from {calcs[ident]['tool']} [{ident}], which is out of date: "
                                   + "; ".join(upstream["reasons"]))
                elif upstream["state"] == ALTERNATIVE:
                    # A figure worked out for another case carries that case into whatever is built on it.
                    carried.append(_carried_text(calcs[ident]["tool"], ident, upstream["note"]))
        note = "; ".join(part for part in [varies_text(row.get("varies")), *carried] if part)
        if reasons:
            state = STALE
        elif note:
            state = ALTERNATIVE
        else:
            state = CURRENT
        calc_state[calc_id] = {
            "state": state, "reasons": reasons, "note": note,
            "tracked": bool(row.get("depends") or row.get("varies")),
        }
        return calc_state[calc_id]

    for calc_id in calcs:
        calc_standing(calc_id)
    evidence_state: dict[str, dict] = {}
    for ident, row in evidence.items():
        reasons = [facts[dep]["reason"] + ("; the job states no edition for this cite now"
                                           if facts[dep].get("emptied") else "; verify the section in that edition")
                   for dep in row.get("depends") or [] if dep in facts and facts[dep]["changed"]]
        evidence_state[ident] = {"state": STALE if reasons else CURRENT, "reasons": reasons}
    finding_state: dict[str, dict] = {}

    def rests_on(supports: list, own_id: str, trail: tuple = ()) -> tuple[list[str], list[str]]:
        reasons: list[str] = []
        notes: list[str] = []
        for ident in supports or []:
            if ident in calcs:
                standing = calc_state[ident]
                if standing["state"] == STALE:
                    reasons.append(f"{calcs[ident]['tool']} [{ident}] is out of date: " + "; ".join(standing["reasons"]))
                elif standing["state"] == ALTERNATIVE:
                    notes.append(f"{calcs[ident]['tool']} [{ident}] ran on {standing['note']}")
            elif ident in evidence:
                if evidence_state[ident]["state"] == STALE:
                    reasons.append(f"the cite [{ident}] follows an edition that changed: "
                                   + "; ".join(evidence_state[ident]["reasons"]))
            elif ident in facts:
                if facts[ident]["changed"]:
                    reasons.append(facts[ident]["reason"])
            elif ident in retired:
                how = "withdrawn" if retired[ident].get("superseded_by") == WITHDRAWN else "replaced"
                reasons.append(f"it rests on finding [{ident}], which was {how}")
            elif ident in findings and ident != own_id and ident not in trail:
                upstream = finding_standing(ident, trail + (own_id,))
                if upstream["state"] == STALE:
                    reasons.append(f"it rests on finding [{ident}], which is out of date")
        return reasons, notes

    def finding_standing(finding_id: str, trail: tuple = ()) -> dict:
        if finding_id in finding_state:
            return finding_state[finding_id]
        reasons, notes = rests_on(findings[finding_id].get("supports") or [], finding_id, trail)
        finding_state[finding_id] = {"state": STALE if reasons else CURRENT, "reasons": reasons, "notes": notes}
        return finding_state[finding_id]

    for finding_id in findings:
        finding_standing(finding_id)
    decision_state: dict[str, dict] = {}
    for ident, row in decisions.items():
        supports = list(row.get("supports") or [])
        # Older rows name their basis in prose; an id written there counts as a support.
        for token in _ID.findall(str(row.get("basis") or "")):
            if token not in supports:
                supports.append(token)
        reasons, notes = rests_on(supports, ident)
        decision_state[ident] = {"state": STALE if reasons else CURRENT, "reasons": reasons, "notes": notes}

    changes = []
    seen_change = set()
    for row in history:
        info = facts.get(row["id"]) or {}
        if not info.get("changed") or row.get("kind") not in (inputs.INPUT_KIND, inputs.BASIS_KIND):
            continue
        key = (row.get("kind"), row.get("key"))
        if key in seen_change:
            continue
        seen_change.add(key)
        affected_calcs = [cid for cid, item in calc_state.items() if item["state"] == STALE
                          and any(str(row.get("key")) in reason for reason in item["reasons"])]
        changes.append({"key": row.get("key"), "kind": row.get("kind"), "reason": info["reason"],
                        "calcs": len(affected_calcs)})
    conflicts = []
    by_key: dict[tuple, list[dict]] = {}
    for row in snap.get("facts") or []:
        if row.get("kind") in (inputs.INPUT_KIND, inputs.BASIS_KIND):
            continue
        by_key.setdefault((row.get("kind"), row.get("key")), []).append(row)
    for (kind, key), rows in by_key.items():
        values = {str(row.get("value")).strip() for row in rows}
        agents = {row.get("agent") for row in rows}
        if len(values) > 1 and len(agents) > 1:
            conflicts.append({"kind": kind, "key": key, "rows": [
                {"id": row["id"], "agent": row.get("agent") or "", "value": row.get("value"), "label": row.get("label")}
                for row in rows
            ]})
    stale = {
        "calcs": [ident for ident, item in calc_state.items() if item["state"] == STALE],
        "evidence": [ident for ident, item in evidence_state.items() if item["state"] == STALE],
        "findings": [ident for ident, item in finding_state.items() if item["state"] == STALE],
        "decisions": [ident for ident, item in decision_state.items() if item["state"] == STALE],
    }
    return {
        "facts": facts, "calcs": calc_state, "evidence": evidence_state, "findings": finding_state,
        "decisions": decision_state, "stale": stale, "changes": [item for item in changes],
        "conflicts": conflicts,
        "any_stale": any(stale.values()),
    }


def backfill(record: Any, project_id: str, *, resolve_id: Callable | None = None) -> int:
    """Give the calcs recorded before the record kept a basis one, from the inputs as they are now.

    A row with no basis that follows the current inputs becomes a tracked,
    current row. One that does not is marked as an alternative, which is the
    honest reading: nothing ties it to the inputs on the form. Returns the
    number of rows written. A second pass finds nothing to do.
    """
    givens = record.givens(project_id)
    if not givens:
        return 0
    calcs = record.calcs(project_id)
    written = 0
    for row in calcs:
        if row.get("depends") or row.get("varies") or row.get("tool") not in TRACKED_TOOLS:
            continue
        depends, varies = call_basis(row["tool"], row.get("inputs"), givens, calcs, resolve_id=resolve_id)
        if depends or varies:
            record.set_calc_basis(project_id, row["id"], depends=depends, varies=varies)
            row["depends"], row["varies"] = depends, varies
            written += 1
    return written
