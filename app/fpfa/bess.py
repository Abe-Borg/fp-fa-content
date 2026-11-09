"""Generic Li-ion BESS explosion-control starter.

The skill file holds the method and the cite block. This module runs the LFL
tool and drafts after that plan. It does not recompute zone gallons or seconds.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from fpfa.calc_tools import SCHEMAS, ToolSession
from fpfa.claude_client import MODEL_ID, TurnCancelled, incomplete_notice, safe_error
from fpfa.modes_loader import normalize_mode
from fpfa.record import Record
from fpfa.skills_loader import read_starter_cites
from fpfa.workflow import NARRATION_CANCELLED, fmt1, judgment_label_line, system_prompt

BESS_SKILL = "ess-isolation-venting-and-duration"
BESS_MODE = "synthesis"


def fmt_vol(value: Any) -> str:
    return f"{float(value):.2f}"


def fmt_ppm(value: Any) -> str:
    return f"{float(value):.0f}"


def fmt_pct(value: Any) -> str:
    number = float(value)
    if number == int(number):
        return str(int(number))
    return f"{number:g}"


def zone_governing(zone_result: dict | None) -> dict[str, str] | None:
    """Exact zone-total and t_total texts from a zone tool plan, when one exists."""
    if not isinstance(zone_result, dict):
        return None
    tools = zone_result.get("tools") or {}
    volume = tools.get("zone_trapped_volume") or {}
    trip = tools.get("di_trip_to_water") or {}
    if "zone_gal" not in volume or "t_total_s" not in trip:
        return None
    return {
        "zone_gal_text": fmt1(volume["zone_gal"]),
        "t_total_s_text": fmt1(trip["t_total_s"]),
    }


def _edition_clause(screen: dict) -> str:
    edition = str(screen.get("edition") or "").strip()
    section = str(screen.get("section") or "").strip()
    if edition.lower() in {"", "unpinned", "assumed"}:
        return f"Edition year ASSUMED unpinned for {section}."
    return f"Edition {edition}."


def _screen_line(screen: dict, row: dict) -> str:
    section = str(screen.get("section") or "").strip()
    path = str(screen.get("path") or "").strip()
    path_bit = f"{path}, " if path else ""
    return (
        f"{fmt_pct(row['pct'])} percent of LFL, {path_bit}{section}. "
        f"{_edition_clause(screen)} "
        f"Setpoint {fmt_vol(row['vol_pct'])} vol% ({fmt_ppm(row['ppm'])} ppm) is calculated."
    )


def _zone_line(zone: dict[str, str]) -> str:
    return (
        f"Zone total {zone['zone_gal_text']} gal and t_total {zone['t_total_s_text']} s "
        "stay on the zone tool plan. This starter did not recompute them."
    )


def template_narrative(
    room: dict,
    tool: dict,
    cites: dict,
    basis: dict | None,
    zone: dict[str, str] | None,
) -> tuple[str, list[str]]:
    """Draft from tool rows and skill cites. Returns the draft and the exact texts it must keep."""
    rows = list(tool.get("setpoints") or [])
    screens = list(cites.get("screens") or [])
    if len(rows) != len(screens):
        raise ValueError("LFL tool row count does not match the skill screens")
    texts: list[str] = []
    fuel = (
        f"Mixture LFL {fmt_vol(tool['lfl_fuel_vol_pct'])} vol% is calculated (fuel-only)."
    )
    diluted = (
        f"Mixture LFL with diluent {fmt_vol(tool['lfl_diluted_vol_pct'])} vol% is calculated."
    )
    texts.extend((fuel, diluted))
    lines = [
        (
            f"Room {room.get('room_id') or '(unnumbered)'} generic Li-ion BESS room. "
            "Explosion-control starter. Draft for the engineer of record."
        ),
        "Synthesis mode. This draft follows the LFL tool plan and does not recompute it.",
    ]
    if room.get("composition_assumed"):
        why = str(room.get("composition_why") or "no cell test report").strip()
        lines.append(f"Off-gas composition ASSUMED ({why}).")
    else:
        lines.append("Off-gas composition was supplied with the room. Not assumed.")
    lines.append("Component LFL values are the sample input. The mixture LFL is calculated.")
    lines.extend((fuel, diluted))
    for screen, row in zip(screens, rows):
        line = _screen_line(screen, row)
        texts.append(line)
        lines.append(line)
    election = cites.get("election") or {}
    duration = cites.get("duration") or {}
    election_section = str(election.get("section") or "").strip()
    election_where = f" ({election_section})" if election_section else ""
    election_line = (
        f"Explosion-control election ASSUMED: {election.get('value')}{election_where}. "
        "No tool returned an election."
    )
    duration_section = str(duration.get("section") or "").strip()
    duration_where = f" ({duration_section})" if duration_section else ""
    duration_line = (
        f"Duration ASSUMED: {duration.get('value')}{duration_where}. "
        "No tool returned a duration."
    )
    texts.extend((election_line, duration_line))
    lines.extend((election_line, duration_line))
    for note in cites.get("notes") or []:
        lines.append(f"Cite: {note}")
    if zone:
        line = _zone_line(zone)
        texts.append(line)
        lines.append(line)
        lines.append(
            "The zone tool plan governs gallons and seconds when the narrative disagrees."
        )
    else:
        lines.append(
            "No zone tool plan is on this project. This starter did not invent gallons or seconds."
        )
    if str((basis or {}).get("hazard_notes") or "").strip():
        lines.append(
            "Hazard notes are a designer judgment the tools did not return. "
            "Label: use best judgment."
        )
    lines.append(judgment_label_line())
    return "\n".join(lines), texts


def bess_govern_note(result: dict | None) -> str:
    """Repeat the starter's exact texts so a later chat turn cannot replace them."""
    if not isinstance(result, dict):
        return ""
    texts = (result.get("governing") or {}).get("texts") or []
    if not texts:
        return ""
    lines = [
        "An explosion-control tool plan already ran. Those LFL figures govern when a narrative disagrees.",
        "Governing texts:",
    ]
    lines.extend(f"- {text}" for text in texts)
    lines.append("Do not replace a calculated vol% or ppm with a number you computed.")
    lines.append("An election or a duration the tool did not return stays ASSUMED.")
    return "\n".join(lines)


def bess_chat_summary(result: dict) -> str:
    narrative = (result.get("narrative") or "").strip()
    extra = (
        "Figures that name vol% or ppm are from the LFL tool plan. "
        "An election or a duration the tool did not return stays ASSUMED."
    )
    if extra in narrative:
        return narrative
    return "\n\n".join(part for part in (narrative, extra) if part)


def _user_message(
    room: dict,
    basis: dict,
    tool_input: dict,
    governing: dict,
    zone: dict[str, str] | None,
    mode: str,
) -> str:
    payload = {
        "skill_to_read": BESS_SKILL,
        "basis": basis,
        "inputs": room,
        "tool_plan_inputs": {"lfl_setpoints": tool_input},
        "governing_texts": governing["texts"],
        "zone": zone,
    }
    return (
        "The LFL tool plan already ran. Those figures govern the explosion-control starter.\n"
        f"Active mode: {mode}. Apply that mode file.\n"
        "The draft must contain each governing text below.\n"
        "Mixture LFL and setpoints are calculated. "
        "An election or a duration the tool did not return is ASSUMED. "
        "Do not describe an ASSUMED value as calculated. "
        "A designer judgment the tools did not return is use best judgment.\n"
        "If a zone total and a t_total are in the governing texts, quote them. "
        "Do not recompute the zone tables. "
        "The zone tool plan governs gallons and seconds when the narrative disagrees.\n"
        f"Read {BESS_SKILL} with read_skill before you apply that method. "
        "If you call lfl_setpoints, use tool_plan_inputs. Do not invent vol% or ppm.\n\n"
        + json.dumps(payload, indent=2, default=str)
    )


def _flags(room: dict, cites: dict, zone: dict[str, str] | None, extra: list[str]) -> list[str]:
    flags = []
    if room.get("composition_assumed"):
        why = str(room.get("composition_why") or "no cell test report").strip()
        flags.append(f"Off-gas composition ASSUMED ({why}).")
    flags.append(
        f"Explosion-control election ASSUMED: {(cites.get('election') or {}).get('value')}. "
        "No tool returned an election."
    )
    flags.append(
        f"Duration ASSUMED: {(cites.get('duration') or {}).get('value')}. "
        "No tool returned a duration."
    )
    for screen in cites.get("screens") or []:
        edition = str(screen.get("edition") or "").strip().lower()
        if edition in {"", "unpinned", "assumed"}:
            flags.append(f"Edition year ASSUMED unpinned for {screen.get('section')}.")
    if zone:
        flags.append("Zone gallons and t_total stay on the zone tool plan.")
    flags.append(judgment_label_line())
    flags.extend(extra)
    return flags


Narrator = Callable[[str, str, list, Callable[[str, dict], Any]], dict]


def run_bess_plan(
    content_root: Path,
    room: dict,
    basis: dict | None = None,
    zone_result: dict | None = None,
    narrator: Narrator | None = None,
    mode: str | None = None,
    *,
    record: Record | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Run the LFL tool, then draft. A model draft is kept only when it quotes the plan.

    With record and project_id, the LFL call is recorded as tool-plan and the
    narrator's calls as narrator.
    """
    basis = dict(basis or {})
    room = dict(room or {})
    selected = normalize_mode(mode or BESS_MODE)
    if selected != BESS_MODE:
        selected = BESS_MODE
    session = ToolSession(content_root, record=record, project_id=project_id, agent="tool-plan")
    narrator_session = ToolSession(content_root, record=record, project_id=project_id, agent="narrator")
    warnings: list[str] = []
    zone = zone_governing(zone_result)
    try:
        cites = read_starter_cites(content_root, BESS_SKILL)
    except (FileNotFoundError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    tool_input = {
        "mix": room.get("mix") or {},
        "lfl": room.get("lfl") or {},
        "screens": [
            {"name": screen["id"], "pct": screen["pct"], "basis": screen["basis"]}
            for screen in cites["screens"]
        ],
    }
    tool = session.execute("lfl_setpoints", tool_input)
    if tool.get("election") is not None or tool.get("duration") is not None:
        raise ValueError("lfl_setpoints returned an election or a duration")
    if session.recording:
        record.set_agent(project_id, name="Tool plan", role_slug="tool-plan", status="done")
    template, texts = template_narrative(room, tool, cites, basis, zone)
    governing = {"texts": texts}
    if zone:
        governing.update(zone)
    transcript = [{
        "name": "lfl_setpoints",
        "input": tool_input,
        "output": tool,
        "is_error": False,
        "by": "tool-plan",
    }]
    narrative = template
    source = "tool-plan"
    model = None
    usage = None
    cancelled = False
    if narrator is not None:
        model = MODEL_ID
        try:
            drafted = narrator(
                system_prompt(content_root, selected),
                _user_message(room, basis, tool_input, governing, zone, selected),
                SCHEMAS,
                narrator_session.execute,
            )
            usage = drafted.get("usage")
            unfinished = incomplete_notice(drafted.get("stop_reason"))
            if unfinished:
                warnings.append(unfinished + " The starter stays on the tool plan.")
            for call in drafted.get("tool_calls") or []:
                transcript.append({
                    "name": call.get("name"),
                    "input": call.get("input"),
                    "output": call.get("output"),
                    "is_error": bool(call.get("is_error")),
                    "by": "claude",
                })
            model_text = (drafted.get("text") or "").strip()
            if model_text and all(text in model_text for text in texts):
                narrative = model_text
                source = "claude"
            else:
                warnings.append(
                    "The model draft did not quote the LFL tool plan. The starter below uses the tool plan."
                )
                if model_text:
                    narrative = (
                        template
                        + "\n\nModel draft (the tool plan governs if the figures differ):\n"
                        + model_text
                    )
            have = {
                call["name"]
                for call in transcript
                if call.get("by") == "claude" and not call.get("is_error")
            }
            if "lfl_setpoints" not in have:
                warnings.append(
                    "Claude did not successfully call lfl_setpoints. The tool plan still ran it."
                )
            if "read_skill" not in have:
                warnings.append(
                    "Claude did not successfully call read_skill. The tool plan still used the skill file."
                )
        except TurnCancelled as exc:
            cancelled = True
            usage = getattr(exc, "usage", None)
            warnings.append(NARRATION_CANCELLED)
            source = "tool-plan"
            narrative = template
        except Exception as exc:
            warnings.append("Claude was not used. " + safe_error(exc))
            source = "tool-plan"
            narrative = template
        if narrator_session.recording:
            record.log_event(project_id, "narration", {
                "usage": dict(usage or {}), "source": source, "cancelled": cancelled, "kind": "bess",
            }, agent="narrator")
    checks = {
        "texts": texts,
        "quotes_all": all(text in (narrative or "") for text in texts),
    }
    return {
        "kind": "bess",
        "source": source,
        "model": model,
        "mode": selected,
        "tools": {"lfl_setpoints": tool},
        "transcript": transcript,
        "narrative": narrative,
        "narrative_checks": checks,
        "warnings": warnings,
        "flags": _flags(room, cites, zone, warnings),
        "governing": governing,
        "inputs": room,
        "basis": basis,
        "cites": cites,
        "zone_governing": zone,
        "usage": usage,
        "cancelled": cancelled,
    }
