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
is not tracked. Its rows are never marked out of date by an input change,
because nothing here knows which input its arguments came from. The record
does not pretend otherwise: such a row's standing carries "tracked": False,
and when a project input changed after the row was written it also carries
"unchecked", the sentence every view prints beside it. Reconciling that row
is a person's job or its author's; the application will not do it and does
not say it did.

A calc is also out of date when the calc code changed. Every calc row
keeps the identity of the kernel files that produced it. When the snapshot
says which identity is installed now (Record.context) and a row carries a
different one, the row is out of date: the figure was produced by code that
is no longer the code that would run. Running it again computes it afresh.
A row with no identity, or a snapshot with no context, is not judged.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from fpfa import inputs
from fpfa.record import WITHDRAWN

# What the kernels write for a choice that was not made. A blank project input is matched by these.
_NO_ELECTION = frozenset({"unelected", "unknown"})
# tool -> argument -> (project input it is filled from, what the tool uses when it is left out). None where the
# tool refuses a call that leaves the argument out (calc_tools._missing): no time, basis, hazard, fill pressure,
# or fill time is put in its place. A default here describes the call only, never the project input: a blank
# project input is matched only by a call that left the argument blank too (call_basis).
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
        "t_detect_s": ("t_detect_s", None),
        "t_release_s": ("t_release_s", None),
        "t_exhaust_s": ("t_exhaust_s", None),
        "basis": ("delivery_basis", None),
        # Required: the tool refuses a call without one, and no "di" stands in for a blank.
        "system_type": ("system_type", None),
    },
    "di_trip_to_water": {
        "q_fill_gpm": ("q_fill_gpm", None),
        "t_detect_s": ("t_detect_s", None),
        "t_release_s": ("t_release_s", None),
        "t_exhaust_s": ("t_exhaust_s", None),
        "basis": ("delivery_basis", None),
        "system_type": ("system_type", None),
    },
    "density_area": {
        "density_gpm_ft2": ("density_gpm_ft2", None),
        "base_area_ft2": ("base_area_ft2", None),
        "area_increase": ("area_increase", 0),
        "hose_gpm": ("hose_gpm", 0),
    },
    "hose_duration": {
        "hazard": ("hazard", None),
        "supervised": ("supervised", False),
    },
    "nitrogen_gate": {
        "p_psig": ("supervisory_psig", None),
        "t_min": ("fill_minutes", None),
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
        "insurer": ("insurer", ""),
    },
}
# Arguments the screen only applies when the caller passes them. Left out, nothing was used.
_ONLY_WHEN_PASSED = {"dry_delivery_screen": ("trim_gal", "fittings_percent")}
# tool -> (argument, basis field): the delivery rows' edition follows the job's NFPA 13 field (edition_follows). A
# call that passed no edition withheld its cites and used none, so it follows any value of the field, and a change
# to the field still puts it out of date.
EDITION_ARGS: dict[str, tuple[str, str]] = {
    "dry_delivery_screen": ("edition", "nfpa_13"),
    "di_trip_to_water": ("edition", "nfpa_13"),
}
# tool -> argument -> (the tool whose result it is taken from, that result's key)
DERIVED: dict[str, dict[str, tuple[str, str]]] = {
    # The size exemption is judged on the zone total, which the screen takes from the takeoff.
    "dry_delivery_screen": {"zone_gal": ("zone_trapped_volume", "zone_gal")},
    "di_trip_to_water": {"v_gal": ("zone_trapped_volume", "zone_gal")},
    "nitrogen_gate": {"v_gal": ("zone_trapped_volume", "zone_gal")},
    "density_area": {"duration_min": ("hose_duration", "duration_min")},
}
TRACKED_TOOLS = frozenset(BINDINGS) | frozenset(DERIVED)
UNTRACKED_NOTE = (
    "Not tied to the project inputs: the application cannot tell which input this calculation used, "
    "so it is never marked out of date by a change."
)
UNCHECKED_NOTE = (
    "A project input changed after this calculation last ran, and the application cannot tell whether it used "
    "that input. Check it by hand or run it again."
)
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
        project = given_value(row)
        if _blank(project):
            # The project input is blank. A call follows it only when what the tool used is blank too: a value the
            # call passed, or a default the tool put in for one left out (hose_duration's unsupervised, the truth
            # table's manual station), is not the project's, and no default is read into the project's blank. The
            # kernel's own words for no election ("unelected", "unknown") are a blank.
            used = _effective(args.get(arg), default)
            matches = _blank(used) or (isinstance(used, str) and used in _NO_ELECTION)
        else:
            used = _effective(args.get(arg), default)
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
    if tool in EDITION_ARGS:
        arg, name = EDITION_ARGS[tool]
        row = givens.get(name)
        if row is not None:
            if edition_follows(args.get(arg), row):
                depends.append(row["id"])
            else:
                varies[arg] = {"used": _plain(args.get(arg)), "project": _plain(given_value(row)), "input": name}
    for arg, (source_tool, _key) in (DERIVED.get(tool) or {}).items():
        if _blank(args.get(arg)):
            continue
        found = matched_source(tool, arg, args.get(arg), calcs, stale=stale, alternative=alternative)
        if found is not None:
            depends.append(found["id"])
        else:
            candidates = [row for row in (calcs or []) if row.get("tool") == source_tool
                          and isinstance(row.get("outputs"), dict)]
            note = (f"matches no recorded {source_tool} result" if candidates
                    else f"no {source_tool} result is on the record")
            varies[arg] = {"used": _plain(args.get(arg)), "from": source_tool, "note": note}
    return depends, varies


def matched_source(
    tool: str,
    arg: str,
    value: Any,
    calcs: list[dict] | None,
    *,
    stale: set[str] | None = None,
    alternative: set[str] | None = None,
) -> dict | None:
    """The recorded calc a figure passed as an argument was taken from. None when it matches none.

    A caller often passes the figure rounded, so the match has a tolerance
    (_result_matches). Of the results that match, the newest that ran on the
    project inputs is taken; failing that, the newest that is not out of
    date; failing that, the newest.
    """
    source = (DERIVED.get(tool) or {}).get(arg)
    if source is None or _blank(value):
        return None
    source_tool, key = source
    matching = [row for row in (calcs or []) if row.get("tool") == source_tool
                and isinstance(row.get("outputs"), dict) and _result_matches(value, row["outputs"].get(key))]
    if not matching:
        return None
    fresh = [row for row in matching if row["id"] not in (stale or set())]
    design = [row for row in fresh if row["id"] not in (alternative or set())]
    return (design or fresh or matching)[-1]


# Arguments a calculation takes from an earlier one and that the tool is handed as recorded, not as the
# caller rounded them (ToolSession.execute). The match that ties a passed figure to its source has a
# tolerance, and that tolerance must not decide a yes or no at a threshold: a takeoff of 500.4 gal passed
# as 500 would read as exempt on the size screen, and would pass a 30 s trip-time screen it fails by
# 0.01 s. The gas fill decides nothing at a threshold; it is here so one zone total gives one recorded
# fill, and a specialist that repeats the tool plan's call with the volume rounded replays that row.
EXACT_FROM_SOURCE: dict[str, tuple[str, ...]] = {
    "dry_delivery_screen": ("zone_gal",),
    "di_trip_to_water": ("v_gal",),
    "nitrogen_gate": ("v_gal",),
}


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


# -- the edition a calculation's cites carry ------------------------------------------------------------

# A standard, the basis field that names the job's edition of it, and how a calc output's own strings name one.
_CITED_EDITION = (
    ("NFPA 13", "nfpa_13", re.compile(r"\bNFPA\s*13[-\s](\d{4})\b")),
    ("NFPA 72", "nfpa_72", re.compile(r"\bNFPA\s*72[-\s](\d{4})\b")),
)
_YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
EDITION_HOLD = "EDITION NOT RECONCILED"
EDITION_OPEN = (
    "Whether the rule and the section apply in the edition the job states was not resolved here. "
    "The engineer of record confirms it."
)
# The same open sentence where the job's edition is the form's starting value, which the designer has not stated.
EDITION_OPEN_STARTING = (
    "Whether the rule and the section apply in the job's edition was not resolved here, and the designer has not "
    "stated that edition. The engineer of record confirms it."
)


def cited_editions(outputs: Any) -> dict[str, list[str]]:
    """The editions a calc output's own cites name, by standard: {"NFPA 13": ["2025"]}. Read, never inferred."""
    found: dict[str, set[str]] = {}

    def walk(value: Any) -> None:
        if isinstance(value, str):
            for document, _field, pattern in _CITED_EDITION:
                for match in pattern.finditer(value):
                    found.setdefault(document, set()).add(match.group(1))
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child)

    walk(outputs)
    return {document: sorted(years) for document, years in found.items()}


def pinned_edition(row: dict | None) -> str | None:
    """The year a basis fact pins: None when it is blank, names no one year, is ASSUMED, or is an unconfirmed start."""
    if not isinstance(row, dict):
        return None
    if str(row.get("label") or "") == inputs.ASSUMED or inputs.UNCONFIRMED_MARK in str(row.get("source") or ""):
        return None
    return stated_edition(given_value(row))


def edition_follows(used: Any, row: dict | None) -> bool:
    """Whether a delivery row's edition argument follows the job's NFPA 13 fact (EDITION_ARGS).

    No edition passed: the cites were withheld and no edition was used, so it
    follows. An edition passed: only the year the job pins.
    """
    if _blank(used):
        return True
    pinned = pinned_edition(row)
    return pinned is not None and stated_edition(used) == pinned


def stated_edition(value: Any) -> str | None:
    """The year a basis field states: 2022 from "2022", "NFPA 13-2022", or "2022 edition".

    None when the field names no year, or more than one: neither can be compared with a cite.
    """
    years = sorted(set(_YEAR.findall(str(value or ""))))
    return years[0] if len(years) == 1 else None


def edition_gaps(outputs: Any, basis: dict | None, assumed: Any = (), unconfirmed: Any = ()) -> list[dict]:
    """Where a calc output's cites name an edition of a standard that is not the edition the job states.

    basis maps a basis field to its value ({"nfpa_13": "2022"}). Returns
    [{"document", "cited", "job", "starting"}]: cited is the cites' own edition
    in words ("NFPA 13-2025"), job is what the job states, as a clause, and
    "starting" is True when the designer has not stated the edition at all.

    A field that is blank or not on the job at all is a gap: the edition is
    not pinned (the record keeps no fact for a blank field, so the two are
    one case). A field that does not name one year is a gap too. So is a
    field in assumed (an edition the designer took from its hint, ASSUMED)
    or in unconfirmed (an earlier form's starting value left on an older
    record): neither pins an edition, whatever year it names, so even an
    edition that matches the cites is a gap. In every case the cites name an
    edition the job does not state, and no edition is taken in its place.

    This compares two labels and nothing else. It does not know whether the
    rule reads the same in both editions and never says it does. A
    calculation is not run again for it. The delivery rows are told the
    job's edition (calc_tools), so their cites follow it or are withheld;
    every other calculation's cites are its own, and running it again does
    not change them. The gap closes when the job states the edition the
    cites carry, or when the content pack's calculation cites the job's.
    """
    basis = basis if isinstance(basis, dict) else {}
    assumed = set(assumed or ())
    unconfirmed = set(unconfirmed or ())
    cited = cited_editions(outputs)
    gaps: list[dict] = []
    for document, field, _pattern in _CITED_EDITION:
        years = cited.get(document)
        if not years:
            continue
        job = stated_edition(basis.get(field))
        if field not in assumed and field not in unconfirmed and job is not None and years == [job]:
            continue
        raw = " ".join(str(basis.get(field) or "").split())
        if field in assumed:
            states = (f"the job's {document} edition {raw[:60] or ''} is ASSUMED, a hint the designer used "
                      f"({inputs.EDITION_NOT_PINNED})").replace("  ", " ")
        elif raw and field in unconfirmed:
            # An earlier form's starting value left on an older record. Nobody stated it, so it pins nothing.
            states = (f"the job's {document} edition is the form's starting value \"{raw[:60]}\", "
                      f"not confirmed by the designer ({inputs.EDITION_NOT_PINNED})")
        elif job is not None:
            states = f"the job states {document}-{job}"
        elif raw:
            states = f'the job\'s {document} edition reads "{raw[:60]}", which does not name one edition'
        else:
            states = f"the job states no {document} edition ({inputs.EDITION_NOT_PINNED})"
        gaps.append({"document": document, "cited": " and ".join(f"{document}-{year}" for year in years), "job": states,
                     "starting": field in assumed or bool(raw and field in unconfirmed)})
    return gaps


def edition_open(gaps: list[dict]) -> str:
    """The open sentence a hold ends with: EDITION_OPEN_STARTING when every gap is on a starting value."""
    if gaps and all(gap.get("starting") for gap in gaps):
        return EDITION_OPEN_STARTING
    return EDITION_OPEN


def edition_hold_text(gaps: list[dict], subject: str = "This calculation's cites are") -> str:
    """The hold as a reader sees it. Empty when there is no gap."""
    if not gaps:
        return ""
    parts = "; ".join(f"{subject} {gap['cited']} and {gap['job']}" for gap in gaps)
    return f"{EDITION_HOLD}. {parts}. {edition_open(gaps)}"


def edition_flags(outputs_by_tool: dict | None, basis: dict | None, assumed: Any = (), unconfirmed: Any = ()) -> list[str]:
    """The same hold for a zone run's flags: one line for the tools that share a gap, naming them."""
    grouped: dict[tuple[str, str, bool], list[str]] = {}
    for tool, outputs in (outputs_by_tool or {}).items():
        for gap in edition_gaps(outputs, basis, assumed, unconfirmed):
            grouped.setdefault((gap["cited"], gap["job"], gap["starting"]), []).append(str(tool))
    lines = []
    for (cited, job, starting), tools in grouped.items():
        cites = "cites are" if len(tools) > 1 else "cite is"
        lines.append(f"{EDITION_HOLD}. The {', '.join(tools)} {cites} {cited} and {job}. "
                     f"{edition_open([{'starting': starting}])}")
    return lines


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


def _change_times(history: list[dict], facts: dict[str, dict]) -> list[str]:
    """When each project input changed: the time the row that replaced it was written.

    An input the designer emptied has no later row and no time of its own; it
    counts as changed after everything, which is the careful reading.
    """
    by_id = {row["id"]: row for row in history}
    times: list[str] = []
    for row in history:
        if row.get("kind") not in (inputs.INPUT_KIND, inputs.BASIS_KIND) or not facts.get(row["id"], {}).get("changed"):
            continue
        later = by_id.get(str(row.get("superseded_by") or ""))
        times.append(str(later.get("created") or "") if later else "9999")
    return times


def analyze(snapshot: dict | None) -> dict:
    """Which rows of a record snapshot are current, out of date, or an alternative, and why.

    States. A calc is "stale" when an input it used has since changed, a
    calc it took a figure from is stale, or the calc code changed after it
    ran; "alternative" when it ran on another value than a project input, or
    took a figure from a calc that did; else "current". A current calc on a
    tool the record does not track carries "unchecked" when an input changed
    after it last ran: the record cannot say whether it still holds. Running
    it again clears that, with the same arguments (a replay) or with others
    (a new row; the old one is then history once nothing current rests on it). A cite is stale when the edition it follows changed. A finding
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
    retired_decisions = {row["id"]: row for row in snap.get("retired_decisions") or []}
    decisions = {row["id"]: row for row in snap.get("decisions") or []}
    calc_state: dict[str, dict] = {}
    # The basis fields as the job states them now, for the edition a calculation's cites are held to.
    stated_basis = {row.get("key"): row.get("value") for row in snap.get("facts") or []
                    if row.get("kind") == inputs.BASIS_KIND}
    # A basis field the designer took from its hint is ASSUMED, and one an earlier form put there is a starting
    # value nobody stated. Neither pins an edition: both hold, whatever year they name.
    assumed_basis = {row.get("key") for row in snap.get("facts") or []
                     if row.get("kind") == inputs.BASIS_KIND and row.get("label") == inputs.ASSUMED}
    starting_basis = {row.get("key") for row in snap.get("facts") or []
                      if row.get("kind") == inputs.BASIS_KIND
                      and inputs.UNCONFIRMED_MARK in str(row.get("source") or "")}
    code_now = str((snap.get("context") or {}).get("calc_identity") or "")
    # When each input change was written. A calc on a tool the record does not track, recorded before one
    # of them, may or may not have used the input that changed.
    changed_at = _change_times(history, facts)

    def calc_standing(calc_id: str, trail: tuple = ()) -> dict:
        if calc_id in calc_state:
            return calc_state[calc_id]
        row = calcs[calc_id]
        reasons: list[str] = []
        carried: list[str] = []
        code_then = str(row.get("calc_identity") or "")
        if code_now and code_then and code_then != code_now:
            reasons.append(f"the calc code changed after it ran (it was computed by calc code {code_then}; "
                           f"the installed content pack's is {code_now})")
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
        tracked = bool(row.get("depends") or row.get("varies"))
        unchecked = ""
        if not tracked and state == CURRENT and row.get("tool") not in TRACKED_TOOLS:
            # When it last ran, not when it first ran: a calculation run again after the change, with the
            # same arguments, replays its row and is the author saying those arguments still hold.
            ran = max(str(row.get("created") or ""), str(row.get("last_used") or ""))
            later = [when for when in changed_at if when > ran]
            if later:
                unchecked = UNCHECKED_NOTE
        # An out-of-date row is not read for its cites: it is waiting to be run again as it is.
        gaps = edition_gaps(row.get("outputs"), stated_basis, assumed_basis, starting_basis) if state != STALE else []
        calc_state[calc_id] = {
            "state": state, "reasons": reasons, "note": note, "tracked": tracked, "unchecked": unchecked,
            "edition_gaps": gaps, "edition_hold": edition_hold_text(gaps),
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
    # By finding or decision id: the untracked calcs it rests on that an input change may have left behind.
    unchecked: dict[str, list[str]] = {}

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
                elif standing.get("unchecked"):
                    unchecked.setdefault(own_id, []).append(f"{calcs[ident]['tool']} [{ident}]: {standing['unchecked']}")
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
            elif ident in retired_decisions:
                how = "withdrawn" if retired_decisions[ident].get("superseded_by") == WITHDRAWN else "replaced"
                reasons.append(f"it rests on decision [{ident}], which was {how}")
            elif ident in findings and ident != own_id and ident not in trail:
                upstream = finding_standing(ident, trail + (own_id,))
                if upstream["state"] == STALE:
                    reasons.append(f"it rests on finding [{ident}], which is out of date")
        return reasons, notes

    def finding_standing(finding_id: str, trail: tuple = ()) -> dict:
        if finding_id in finding_state:
            return finding_state[finding_id]
        reasons, notes = rests_on(findings[finding_id].get("supports") or [], finding_id, trail)
        finding_state[finding_id] = {"state": STALE if reasons else CURRENT, "reasons": reasons, "notes": notes,
                                     "unchecked": unchecked.get(finding_id, [])}
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
        decision_state[ident] = {"state": STALE if reasons else CURRENT, "reasons": reasons, "notes": notes,
                                 "unchecked": unchecked.get(ident, [])}

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
        # Calcs the record cannot reconcile by itself, by id: untracked, with an input changed since.
        "unchecked": [ident for ident, item in calc_state.items() if item.get("unchecked")],
        # Calcs whose cites name another edition of a standard than the job states, by id.
        "edition_holds": [ident for ident, item in calc_state.items() if item.get("edition_hold")],
        "code_changed": bool(code_now) and any(
            str(row.get("calc_identity") or "") not in ("", code_now) for row in calcs.values()),
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
