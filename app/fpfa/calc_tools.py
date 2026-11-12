"""Claude tool schemas. Every number comes from calcs/fp, loaded from the content pack."""

from __future__ import annotations

import contextvars
import hashlib
import importlib.util
import json
import math
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from fpfa import coherence, quantities, units
from fpfa.corpus_search import search_corpus
from fpfa.fa_calc import run_fa_calc
from fpfa.modes_loader import list_modes, read_mode
from fpfa.inputs import BASIS_FIELDS, BASIS_KIND, GIVEN, INPUT_KIND
from fpfa.record import CALC_TOOLS, CONVERT_TOOL, LABELS, SKILL_READ, Record, RecordError
from fpfa.releasing import reader_view
from fpfa.roles_loader import list_roles, read_role
from fpfa.skills_loader import list_skills, read_skill

_MODULES: dict[str, object] = {}


def _load(path: Path):
    key = str(path.resolve())
    if key in _MODULES:
        return _MODULES[key]
    mod_name = "contentpack_" + key.replace("\\", "_").replace("/", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    _MODULES[key] = module
    return module


def _obj(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required}


# The SI figures in what the designer wrote this turn (units.foreign_figures). designer_words() sets them
# for the length of a turn. Delegations and consults run on the turn's own thread, so every tool session the
# turn opens, the specialists' too, reads the same ones. Outside a turn there are none.
_DESIGNER_SI: contextvars.ContextVar[tuple] = contextvars.ContextVar("fpfa_designer_si", default=())


@contextmanager
def designer_words(text: str) -> Iterator[None]:
    """For the length of a turn: the SI figures the designer gave, which no calc field in US units may take."""
    token = _DESIGNER_SI.set(units.foreign_figures(text))
    try:
        yield
    finally:
        _DESIGNER_SI.reset(token)


def _numbers_passed(value: Any, name: str | None = None) -> Iterator[tuple[str | None, float]]:
    """(field name, number) for every number a call passes: nested rows and an op's inputs too."""
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        yield name, float(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _numbers_passed(child, str(key))
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _numbers_passed(child, name)


def si_figure_problem(args: dict) -> str:
    """Why a calc call is refused before it runs: it passes the designer's SI figure into a US field. Else "".

    The designer wrote 12.2 mm/min and the call passes density_gpm_ft2=12.2,
    or 139 m² and base_area_ft2=139. The number would run and be recorded as
    gpm/ft² or ft², and a result in the wrong unit would follow with a right-
    looking record. A number the designer also gave in a US unit of the same
    kind is not refused.
    """
    said = _DESIGNER_SI.get()
    if not said:
        return ""
    for name, value in _numbers_passed(args):
        target = units.field_unit(name)
        if target is None:
            continue
        number = quantities.normal(str(value))
        for given, dimension, display in said:
            if dimension == target.dimension and given == number:
                return (
                    f"{name} takes {target.display}. {value:g} is the figure the designer gave in {display}. "
                    f"Convert it first with convert_units ({value:g} {display} to {target.display}) and pass the "
                    "result. Nothing was run or recorded."
                )
    return ""


# GIVEN says where a value came from. A finding or a decision is the team's own statement, so it never carries it.
FINDING_LABELS = tuple(label for label in LABELS if label != GIVEN)
LEAD = "lead"
# Said on every calc tool whose fields carry a unit. A metric figure passed as it stands is a wrong number
# with a right-looking record; the acceptance run of 0.3.0 saw 12.2 mm/min run as 12.2 gpm/ft².
# What the delivery tools say of a time and a basis: the application puts nothing in place of one not given.
TIME_NOTE = ("Seconds, from the releasing design. Leave it out when the job has none: a time not given is never "
             "taken as 0, and the result is then the fill time alone and its margin, with no pass or fail. A 0 you "
             "pass is used and flagged ASSUMED-ZERO (an optimistic screen, NEEDS PE REVIEW).")
BASIS_NOTE = ("Delivery time basis: FM, NFPA-LH, NFPA-OH, NFPA-EH, NFPA-HP, or NFPA-DU. Required: no basis is "
              "chosen for you, and a blank one is not taken as FM.")
SYSTEM_NOTE = ("dry or di. Required: no system type is taken for you. A wet zone has no delivery rows, so this tool "
               "refuses wet.")
EDITION_NOTE = ("The job's own NFPA 13 edition year, as the job states it. Leave it out when the job has not pinned "
                "one: the figures still run and every cite is withheld (EDITION NOT SET). No edition is taken for you.")
# The delivery inputs a call must give. Missing or blank, the tool refuses and names them (_missing). The
# detection, releasing, and exhaust times are not here: without all three the result is the fill time alone.
_DELIVERY_REQUIRED = ("q_fill_gpm", "basis", "system_type")
SUB_TIMES = ("t_detect_s", "t_release_s", "t_exhaust_s")
# The words a delivery row carries when a sub-time was not given, when one was typed as 0, and when its cites are
# withheld. The figures that would depend on a missing time (t_total, the pass or fail, the volume at the limit)
# are left out of the row, not computed on a 0 the application put there.
FILL_ONLY = "sub-times not provided; no pass or fail"
ASSUMED_ZERO = "ASSUMED-ZERO"
NEEDS_PE_REVIEW = "NEEDS PE REVIEW"
EDITION_NOT_SET = "EDITION NOT SET — cites withheld, VERIFY"
EDITION_NOT_HELD = "NFPA 13-{year} labels are not in this calc pack — cites withheld, VERIFY"
ASSUMED_NOT_FOR_RELEASE = "ASSUMED INPUT — not for release"
# A zone total this close to the size threshold, as a fraction of it, is flagged: the answer can turn on trim and
# fittings figures that are often ASSUMED. The owner's ruling of 2026-11-12 sets 1%; it decides no answer.
NEAR_THRESHOLD_FRACTION = 0.01
# Delivery rows whose cites are withheld: these keys hold the kernel's NFPA 13 cite strings.
_NFPA13_TEXT = re.compile(r"\bNFPA\s*13\b(?!\s*[DR])")
_YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
# Ops the model reaches through fp_calc that have a tool of their own, where the application's argument rules live.
_OWN_TOOL_OPS = {"dry_delivery_screen": "dry_delivery_screen", "di_trip_to_water": "di_trip_to_water"}
# The pressure fields a gas-law fill rate reads. An unmarked kPa or bar is refused for one (fpfa.units).
GAS_LAW_FIELDS = units.GAS_LAW_FIELDS
US_UNITS_NOTE = (
    " Every number is in the US unit its field name states. Convert an SI figure with convert_units first, "
    "and never put another unit on the result."
)


SCHEMAS = [
    {
        "name": "list_skills",
        "description": "List design methods in the content pack (skills/<slug>/SKILL.md). Read a skill before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_skill",
        "description": "Return the full SKILL.md for one slug. Use this instead of inventing a method.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "list_roles",
        "description": "List specialist roles in the content pack (roles/<slug>/ROLE.md). Read a role before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_role",
        "description": "Return the full ROLE.md for one specialist slug. Use this instead of inventing a role.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "list_modes",
        "description": "List everyday-path modes in the content pack (modes/<slug>/MODE.md). Read a mode before you apply it.",
        "input_schema": _obj({}, []),
    },
    {
        "name": "read_mode",
        "description": "Return the full MODE.md for one mode slug. Use this instead of inventing a mode.",
        "input_schema": _obj({"slug": {"type": "string"}}, ["slug"]),
    },
    {
        "name": "resolve_pipe_id",
        "description": "Shop-default inside diameter for a nominal pipe size. Do not invent an ID. A blank schedule uses the shop default and is flagged.",
        "input_schema": _obj(
            {
                "nps": {"type": "number", "description": "Nominal size in inches"},
                "schedule": {"type": "string", "description": "sch10 or sch40. Omit for the shop default."},
                "role": {"type": "string", "description": "branch, drop, cross, main, feed, or riser"},
            },
            ["nps"],
        ),
    },
    {
        "name": "zone_trapped_volume",
        "description": "Trapped gallons for one zone. Pipe volume is formulas.pipe_volume. Fittings and trim are added here, not in your head." + US_UNITS_NOTE,
        "input_schema": _obj(
            {
                "segments": {"type": "array", "description": "Each item has length_ft and either d_in or nps plus optional schedule and role."},
                "length_basis": {"type": "string", "description": "center_to_center or cut"},
                "fittings_percent": {"type": "number"},
                "trim_gal": {"type": "number"},
            },
            ["segments"],
        ),
    },
    {
        "name": "dry_delivery_screen",
        "description": (
            "Pipe timing, the NFPA size exemption, and optimistic trip-to-water screen from formulas.dry_delivery_screen. "
            "Not a listed water-delivery calculation. Timing stays on pipe volume. Each segment has length_ft and "
            "either d_in or nps with an optional schedule, as zone_trapped_volume takes them. The size exemption is judged on the zone total (pipe + fittings + trim), never on pipe "
            "alone: pass zone_gal, the zone total from zone_trapped_volume, and nfpa_delivery_time_exempt is then "
            "the zone-total answer. Without zone_gal (or trim_gal and fittings_percent) the result is a pipe-only "
            "screen: nfpa_delivery_time_exempt is null, exemption_status says it was not determined, and you must "
            "not state the exemption from it. The threshold is the result's nfpa_size_threshold_gal, an exemption "
            "threshold and not a cap; on double-interlock a quick-opening device does not raise it. Quote the "
            "result's note_60s_option and nfpa_basis as written. The application sends declared_interlock double for "
            "di and none for dry unless you pass it."
        ) + US_UNITS_NOTE,
        "input_schema": _obj(
            {
                "segments": {"type": "array"},
                "q_fill_gpm": {"type": "number"},
                "qod": {"type": "boolean"},
                "t_detect_s": {"type": "number", "description": TIME_NOTE},
                "t_release_s": {"type": "number", "description": TIME_NOTE},
                "t_exhaust_s": {"type": "number", "description": TIME_NOTE},
                "basis": {"type": "string", "description": BASIS_NOTE},
                "system_type": {"type": "string", "description": SYSTEM_NOTE},
                "edition": {"type": "string", "description": EDITION_NOTE},
                "declared_interlock": {"type": "string", "description": "double or none. Left out, double for di and none for dry."},
                "zone_gal": {"type": "number", "description": "Zone total gallons from zone_trapped_volume (zone_gal). The size exemption is judged on it."},
                "trim_gal": {"type": "number", "description": "Trim gallons, when zone_gal is not passed. Omit both for a pipe-only screen."},
                "fittings_percent": {"type": "number", "description": "Fittings allowance percent. Used with trim_gal when zone_gal is not passed; left out, the kernel's ASSUMED allowance for cut lengths applies, never 0."},
            },
            ["segments", "q_fill_gpm", "system_type", "basis"],
        ),
    },
    {
        "name": "di_trip_to_water",
        "description": (
            "Optimistic t = t_detect + t_release + t_exhaust + 60*V/Q from formulas.di_trip_to_water. Pass the zone "
            "total gallons, including trim, as v_gal: the application tells the kernel V is the caller's "
            "(v_basis caller). Not a listed delivery-time proof. Quote the result's note_60s_option as written."
        ) + US_UNITS_NOTE,
        "input_schema": _obj(
            {
                "v_gal": {"type": "number"},
                "q_fill_gpm": {"type": "number"},
                "t_detect_s": {"type": "number", "description": TIME_NOTE},
                "t_release_s": {"type": "number", "description": TIME_NOTE},
                "t_exhaust_s": {"type": "number", "description": TIME_NOTE},
                "basis": {"type": "string", "description": BASIS_NOTE},
                "system_type": {"type": "string", "description": SYSTEM_NOTE},
                "edition": {"type": "string", "description": EDITION_NOTE},
            },
            ["v_gal", "q_fill_gpm", "system_type", "basis"],
        ),
    },
    {
        "name": "density_area",
        "description": (
            "Sprinkler demand from formulas.density_area. design area = base * (1 + increase); demand adds hose. "
            "Density and base area must be greater than 0, and a duration greater than 0 when one is passed. "
            "area_increase and hose_gpm are required: pass 0 when none applies, never leave one out. A density or "
            "an area that is not the job's own is ASSUMED: name it in assumed, with assumed_reason, and only for a "
            "demand the designer asked for. The result is then labeled ASSUMED, NEEDS PE REVIEW, and "
            "'ASSUMED INPUT — not for release'. Never use a demand for the delivery or gas-fill screens."
        ) + US_UNITS_NOTE,
        "input_schema": _obj(
            {
                "density_gpm_ft2": {"type": "number"},
                "base_area_ft2": {"type": "number"},
                "area_increase": {"type": "number", "description": "A fraction: 0.30 is 30 percent. 0 when none applies."},
                "hose_gpm": {"type": "number", "description": "0 when no hose stream is included."},
                "duration_min": {"type": "number"},
                "assumed": {"type": "array", "items": {"type": "string"},
                            "description": "density_gpm_ft2 and/or base_area_ft2 when that value is ASSUMED."},
                "assumed_reason": {"type": "string", "description": "Why the ASSUMED value is used, and its source."},
            },
            ["density_gpm_ft2", "base_area_ft2", "area_increase", "hose_gpm"],
        ),
    },
    {
        "name": "hose_duration",
        "description": "Hose stream and duration from formulas.hose_duration. The result's basis key names the table and its edition; quote it as written.",
        "input_schema": _obj(
            {"hazard": {"type": "string"}, "supervised": {"type": "boolean"}},
            ["hazard"],
        ),
    },
    {
        "name": "nitrogen_gate",
        "description": (
            "Design C is 100. Fill scfm is formulas.air_fill_scfm. "
            "The result states the gauge-basis rate and the absolute-basis rate. Quote both, and size on the larger "
            "(the result's sizing_basis names it). "
            "Do not emit C=120 as the design value. p_psig is the supervisory fill pressure and t_min the fill "
            "time. Both are required: the application supplies neither. Pass the job's own, or a value you state "
            "as ASSUMED with its reason. A value passed is used as passed, a 0 included."
        ),
        "input_schema": _obj(
            {"v_gal": {"type": "number"}, "p_psig": {"type": "number"}, "t_min": {"type": "number"}},
            ["v_gal", "p_psig", "t_min"],
        ),
    },
    {
        "name": "convert_units",
        "description": (
            "Convert a figure from one unit to another by the exact definitions: 1 ft = 0.3048 m, 1 US gallon = "
            "3.785411784 L, 1 psi = 6.894757293 kPa, and a density in mm/min is L/min over each m². Every calc tool "
            "takes the US units its field names state (gpm, ft², gpm/ft², psi, gal, ft, in), so convert an SI "
            "figure before you pass it, and convert a result the designer wants in SI after. Never convert in your "
            "head, and never put another unit on a tool's result. The result is a calculation record: cite it for "
            "the converted figure. A figure that was ASSUMED stays ASSUMED. Gauge stays gauge; an absolute "
            "pressure, cubic feet, and a K-factor are not converted. A kPa or bar written without a gauge mark "
            "becomes ASSUMED gauge for a sprinkler-pressure field and is refused for a gas-law field "
            "(" + ", ".join(units.GAS_LAW_FIELDS) + "): name the field it is for, or write kPa(g) or barg."
        ),
        "input_schema": _obj(
            {
                "value": {"type": "number"},
                "field": {"type": "string", "description": "The calc field the figure is for, such as p_psig or p_psi. Needed for an unmarked kPa or bar going to psi."},
                "from_unit": {"type": "string", "description": "The unit the figure is in: mm/min, m², L/min, L/s, m³/h, kPa, bar, m, mm, L, or a US unit."},
                "to_unit": {"type": "string", "description": "The unit wanted: gpm/ft², ft², gpm, psi, gal, ft, in, or an SI unit."},
            },
            ["value", "from_unit", "to_unit"],
        ),
    },
    {
        "name": "elect_di_trim",
        "description": "Double-interlock trim-family screen. Elect El/El, El/Pn, or named-failsafe from what holds the prime. Do not invent a catalog number. Out-of-scope systems return RFI-variance.",
        "input_schema": _obj(
            {
                "system_type": {"type": "string"},
                "prime_held_by": {"type": "string", "description": "nc_solenoid, pneumatic_actuator, or unknown"},
                "failsafe_on_total_power_loss": {"type": "boolean"},
                "supervisory_psi": {"type": "number"},
                "medium": {"type": "string"},
                "insurer": {"type": "string"},
            },
            ["system_type"],
        ),
    },
    {
        "name": "releasing_truth_table",
        "description": (
            "Build the double-interlock solenoid truth table in code (electric/electric trim). "
            "solenoid = (detection OR manual) AND P AND NOT isolated. P is the second leg, the pressure "
            "drop from sprinkler operation (p_second_leg). Low air is supervisory only and is not a "
            "release input. Quote boolean_p. A second smoke zone must not change the result."
        ),
        "input_schema": _obj(
            {"manual_station": {"type": "boolean"},
             "insurer": {"type": "string", "description": "The job's insurer. Blank stays blank; it is not taken as FM."}},
            [],
        ),
    },
    {
        "name": "lfl_setpoints",
        "description": (
            "Mixture LFL and setpoints from calcs/fa/lib/lfl.py. "
            "Pass each percent. This tool does not choose a code threshold, an election, or a duration."
        ),
        "input_schema": _obj(
            {
                "mix": {"type": "object", "description": "Gas name to volume percent or fraction."},
                "lfl": {"type": "object", "description": "Gas name to component LFL vol%, for every gas in mix. Write \"inert\" for an inert gas. A blank, missing, or non-positive LFL holds the call."},
                "screens": {
                    "type": "array",
                    "description": "Each item has name, pct, and basis (fuel or diluted). pct is the caller's percent.",
                },
            },
            ["mix", "lfl"],
        ),
    },
    {
        "name": "fp_calc",
        "description": (
            "Run any other op in calcs/fp/formulas.py by name (hazen_williams, pump_envelope, k_factor, and the rest). "
            "Pass op and inputs. Do not compute the formula yourself. The delivery screens have tools of their own "
            "(dry_delivery_screen, di_trip_to_water) and are refused here. density_area here takes the same checks as "
            "its own tool. A k_factor result's k_si is a display figure, never a design input."
        ) + US_UNITS_NOTE,
        "input_schema": _obj(
            {"op": {"type": "string"}, "inputs": {"type": "object"}},
            ["op", "inputs"],
        ),
    },
    {
        "name": "fa_calc",
        "description": (
            "Run an op from calcs/fa/lib by module and function. "
            "Pass module (filename stem), op (function name), and inputs. "
            "Do not compute the formula yourself. list_ops returns the allowlist."
        ),
        "input_schema": _obj(
            {
                "module": {"type": "string", "description": "Filename stem under calcs/fa/lib."},
                "op": {"type": "string", "description": "Function name on that module."},
                "inputs": {"type": "object", "description": "Keyword arguments for the op."},
                "list_ops": {
                    "type": "boolean",
                    "description": "Return the allowlist instead of running an op.",
                },
            },
            [],
        ),
    },
    {
        "name": "search_corpus",
        "description": (
            "Search edition pins and decision notes in corpus/. "
            "Use before assuming an NFPA edition or AHJ pin."
        ),
        "input_schema": _obj(
            {
                "query": {"type": "string", "description": "Text to find. Match is case-insensitive."},
                "limit": {"type": "integer", "description": "Maximum hits. Default 8."},
            },
            ["query"],
        ),
    },
    {
        "name": "record_fact",
        "description": (
            "Write one basis-of-design fact to this job's project record: an owner standard, a confirmed "
            "authority or edition, or an assumption. label is calculated, ASSUMED, use best judgment, "
            "or a cite class (CODE, OWNER, PRACTICE, PARA, HB). GIVEN is for a value the designer stated, and "
            "only the lead writes it. A new value for a key you wrote before replaces your earlier one. "
            "A value that differs from another contributor's for the same key is kept beside it and shown as a "
            "conflict for the lead to settle. The zone inputs and the five basis fields are not written here: "
            "the lead changes those with set_input. The record is the source for the export."
        ),
        "input_schema": _obj(
            {
                "kind": {"type": "string", "description": "basis, assumption, edition, owner, or another short group name"},
                "key": {"type": "string", "description": "Short name, such as nfpa_13_enforced"},
                "value": {"type": "string"},
                "label": {"type": "string", "description": "One of: " + ", ".join(LABELS)},
                "source": {"type": "string", "description": "Where the value came from. Optional."},
            },
            ["kind", "key", "value", "label"],
        ),
    },
    {
        "name": "record_evidence",
        "description": (
            "Write one cite to the project record: document, edition, section, a short paraphrase, "
            "and where it applies. status is held, NOT PULLED, NEEDS HOLD, or PACKAGE ASSERTION. "
            "Do not paste the standard's text."
        ),
        "input_schema": _obj(
            {
                "document": {"type": "string", "description": "Such as NFPA 13 or FM DS 5-32"},
                "edition": {"type": "string"},
                "section": {"type": "string"},
                "note": {"type": "string", "description": "Short paraphrase, one or two sentences."},
                "applicability": {"type": "string"},
                "status": {"type": "string", "description": "held, NOT PULLED, NEEDS HOLD, or PACKAGE ASSERTION. Default held."},
            },
            ["document"],
        ),
    },
    {
        "name": "record_finding",
        "description": (
            "Write one finding to the project record with its label and the ids of the calc records, "
            "evidence rows, or facts that support it. A figure with no calc record id is not calculated. "
            "An earlier finding or a decision may be named too: it is the team's own statement and adds no source. "
            "One statement per finding, so each can be checked and reviewed on its own. To revise a finding "
            "you wrote earlier, pass its id in replaces: the old one is kept as history and leaves the current set."
        ),
        "input_schema": _obj(
            {
                "text": {"type": "string"},
                "label": {"type": "string", "description": "One of: " + ", ".join(FINDING_LABELS)},
                "supports": {"type": "array", "description": "Record ids this finding rests on.", "items": {"type": "string"}},
                "replaces": {"type": "string", "description": "Id of your earlier finding this one takes the place of. Optional."},
            },
            ["text", "label"],
        ),
    },
    {
        "name": "withdraw_finding",
        "description": (
            "Withdraw a finding or a decision you wrote that no longer holds and that you have nothing to put in "
            "the place of: its basis changed, or an objection to it was right. It stays on the record as history."
        ),
        "input_schema": _obj(
            {"id": {"type": "string", "description": "The finding's id, or the decision's."},
             "reason": {"type": "string", "description": "Why it no longer holds."}},
            ["id", "reason"],
        ),
    },
    {
        "name": "review_finding",
        "description": (
            "Record your position on another contributor's finding that touches your work: agree, or object. "
            "An objection needs a note that says what is wrong and what would settle it. It stays open until "
            "the author revises or withdraws the finding, or the lead settles it. You do not review your own finding."
        ),
        "input_schema": _obj(
            {
                "id": {"type": "string", "description": "The finding's id."},
                "position": {"type": "string", "description": "agree or object"},
                "note": {"type": "string", "description": "Required for object. Optional for agree."},
            },
            ["id", "position"],
        ),
    },
    {
        "name": "open_question",
        "description": (
            "Write a question to the project record. to is engineer (the default) for an RFI the engineer of "
            "record, the owner, or the authority must settle; it is listed in the design basis. to is designer "
            "when the team needs the answer from the person using the app before the work can go on: a missing "
            "input, or a choice only they can make. One question per call."
        ),
        "input_schema": _obj(
            {"text": {"type": "string"}, "to": {"type": "string", "description": "engineer or designer. Default engineer."}},
            ["text"],
        ),
    },
    {
        "name": "record_decision",
        "description": (
            "Write an election or a judgment to the project record, with its basis and label. "
            "A decision the tools did not return is use best judgment. To revise a decision you made earlier, "
            "pass its id in replaces."
        ),
        "input_schema": _obj(
            {
                "text": {"type": "string"},
                "label": {"type": "string", "description": "One of: " + ", ".join(FINDING_LABELS)},
                "basis": {"type": "string", "description": "The reasoning behind the decision, in a sentence. Optional."},
                "supports": {"type": "array", "description": "Record ids the decision rests on. Optional.", "items": {"type": "string"}},
                "replaces": {"type": "string", "description": "Id of your earlier decision this one takes the place of. Optional."},
            },
            ["text", "label"],
        ),
    },
    {
        "name": "read_record",
        "description": (
            "Show this job's project record with row ids: facts, calc records with inputs and outputs, "
            "evidence, findings, decisions, open questions, and pending handoffs. Pass kind for the full "
            "rows of one table (calcs, evidence, facts, findings, questions, decisions, handoffs, reviews, tasks, "
            "agents, jobs), and id for one row."
        ),
        "input_schema": _obj(
            {
                "kind": {"type": "string", "description": "A table name. Omit for the summary."},
                "id": {"type": "string", "description": "One row id. Needs kind."},
            },
            [],
        ),
    },
    {
        "name": "handoff",
        "description": (
            "Hand work to another agent on this job. The handoff is written to the project record as "
            "pending and is delivered when the lead next activates that agent. Name the specialist by its "
            "role slug (fp-sprinkler, fa-releasing, spec-draft) or the lead as lead."
        ),
        "input_schema": _obj(
            {
                "to": {"type": "string", "description": "Role slug of the receiving agent, or lead."},
                "brief": {"type": "string", "description": "What the receiver should do, in a few sentences."},
                "payload": {"type": "object", "description": "Figures, ids, or elections the receiver needs. Optional."},
            },
            ["to", "brief"],
        ),
    },
]

# Tools that write to or read the project record. They need an open record on the turn.
RECORD_TOOLS = frozenset({
    "record_fact",
    "record_evidence",
    "record_finding",
    "withdraw_finding",
    "review_finding",
    "open_question",
    "record_decision",
    "read_record",
    "handoff",
})

# The DI workflow refuses a narrative until these have run on the form.
REQUIRED_DI_TOOLS = [
    "zone_trapped_volume",
    "dry_delivery_screen",
    "di_trip_to_water",
    "elect_di_trim",
    "releasing_truth_table",
]


class ToolSession:
    """Runs one tool call. With a record and a project id, calc calls record themselves.

    agent names who is calling (lead, tool-plan, a specialist) on the rows it writes.
    Without a record, nothing is written and every tool behaves as before.
    """

    def __init__(
        self,
        content_root: Path,
        record: Record | None = None,
        project_id: str | None = None,
        agent: str = "",
    ):
        self.root = Path(content_root)
        di_path = self.root / "calcs" / "fp" / "di_zone.py"
        if not di_path.is_file():
            raise FileNotFoundError(di_path)
        self.di = _load(di_path)
        self.formulas = self.di.formulas
        self.record = record
        self.project_id = (project_id or "").strip() or None
        self.agent = (agent or "").strip()
        self.pack_version = _pack_version() if self.record is not None else ""
        # Identity of the calc code in this pack. A changed kernel file changes it,
        # so a recorded result is never replayed by different code.
        self.calc_identity = calc_identity(self.root) if self.record is not None else ""
        if self.record is not None:
            # The record is read against what is installed now: a calc computed by other code is out of date,
            # and a check or an export says which content it was written from.
            self.record.set_context(calc_identity=self.calc_identity, content_version=self.pack_version,
                                    content_fingerprint=content_fingerprint(self.root))

    @property
    def recording(self) -> bool:
        return self.record is not None and self.project_id is not None

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name in RECORD_TOOLS:
            return self._record_tool(name, args)
        if name in CALC_TOOLS and name != CONVERT_TOOL:
            # Before anything runs or is recorded: the designer's SI figure in a field that takes US units.
            problem = si_figure_problem(args)
            if problem:
                raise units.UnitError(problem)
        if name in CALC_TOOLS and self.recording:
            args, taken = self._exact_from_record(name, args)
            found = self.record.find_calc(self.project_id, name, args, self.calc_identity)
            if found is not None:
                # Same tool, inputs, calc code, and project: count the replay and return the recorded output.
                # A replay is the same call checked against the inputs as they are now, so its basis is rewritten.
                depends, varies, departs = self._basis(name, args)
                row = self.record.record_calc(
                    self.project_id, tool=name, inputs=args, outputs=found["outputs"],
                    agent=self.agent, calc_identity=self.calc_identity, depends=depends, varies=varies,
                )
                return self._with_record_id(name, found["outputs"], row["id"], departs, taken)
            output = self._run(name, args)
            depends, varies, departs = self._basis(name, args)
            row = self.record.record_calc(
                self.project_id, tool=name, inputs=args, outputs=output,
                agent=self.agent, pack_version=self.pack_version, calc_identity=self.calc_identity,
                depends=depends, varies=varies,
            )
            return self._with_record_id(name, output, row["id"], departs, taken)
        output = self._run(name, args)
        # A model never reads the kernel's deprecated names, with a record or without one.
        return reader_view(name, output) if self.model_facing else output

    @property
    def model_facing(self) -> bool:
        """True when a model reads this session's results. The fixed tool plan and a bare session do not."""
        return self.agent not in ("", "tool-plan")

    def _exact_from_record(self, name: str, args: dict) -> tuple[dict, list[str]]:
        """Hand a threshold-deciding argument the recorded figure it was taken from, not the caller's rounding.

        A model often passes a figure rounded, and the record ties it to the
        calculation it came from within a tolerance. That tolerance must not
        decide an answer: a takeoff of 500.4 gal passed as 500 would be judged
        exempt. For the arguments in coherence.EXACT_FROM_SOURCE the call runs,
        and is recorded, on the matched record's own figure. Returns the
        arguments to use and a sentence for each figure that was replaced. A
        figure that matches no record is left as passed; the record then marks
        the call as an alternative, as it always did.
        """
        names = coherence.EXACT_FROM_SOURCE.get(name) or ()
        if not names or not any(_number_was_passed(args, arg) for arg in names):
            return args, []
        notes: list[str] = []
        try:
            calcs = self.record.calcs(self.project_id)
            standing = coherence.analyze({
                "fact_history": self.record.facts(self.project_id, include_superseded=True), "calcs": calcs,
            })["calcs"]
            stale = {ident for ident, item in standing.items() if item["state"] == coherence.STALE}
            alternative = {ident for ident, item in standing.items() if item["state"] == coherence.ALTERNATIVE}
            used = dict(args)
            for arg in names:
                if not _number_was_passed(args, arg):
                    continue
                row = coherence.matched_source(name, arg, args[arg], calcs, stale=stale, alternative=alternative)
                if row is None:
                    continue
                source_tool, key = coherence.DERIVED[name][arg]
                exact = row["outputs"].get(key)
                if isinstance(exact, bool) or not isinstance(exact, (int, float)) or float(exact) == float(args[arg]):
                    continue
                used[arg] = exact
                notes.append(f"{arg} was passed as {args[arg]}. The calculation used the figure on the "
                             f"{source_tool} record [{row['id']}] itself, {exact:.4g}, so that rounding cannot "
                             "decide the answer.")
            return used, notes
        except Exception:
            # Bookkeeping. A failure here never fails the calculation; the figure is used as passed.
            return args, []

    def _with_record_id(self, name: str, output: dict, record_id: str, departs: str = "",
                        taken: list[str] | None = None) -> dict:
        """A model-facing result carries the calc record id so a finding can cite it.

        It also says, in one sentence, where the call departed from the project
        inputs, so a specialist sees at once that it ran an alternative and not
        the design case. departs is that sentence's middle (_basis): the call's
        own arguments, and a figure it took from a calc that was itself an
        alternative. The fixed tool plan (agent tool-plan) gets the bare
        output, so its tables and export stay byte-identical to a run with no record.
        """
        if not self.model_facing or not isinstance(output, dict):
            return output
        shown = dict(reader_view(name, output))
        shown["record_id"] = record_id
        if taken:
            shown["figure_taken_from_the_record"] = " ".join(taken)
        if name not in coherence.TRACKED_TOOLS:
            shown["not_tied_to_project_inputs"] = (
                coherence.UNTRACKED_NOTE + " If a project input it used changes, run it again and replace the "
                "finding that cites it; nothing will prompt you."
            )
        if departs:
            shown["differs_from_project_inputs"] = (
                f"This call used {departs}. It is recorded as an alternative, not the design case. "
                "If the project input is wrong, the lead changes it; do not present this result as the design case."
            )
        return shown

    def _resolve_id(self, nps, schedule, role) -> dict:
        return self.di.pipe_ids.resolve(nps, schedule, role)

    def _basis(self, name: str, args: dict) -> tuple[list[str], dict, str]:
        """What this call follows on the record: the inputs it used and the calcs it took a figure from.

        The third value says where the call departs from the project inputs,
        the way the record's own analysis will once the row is written: by its
        own arguments, or by taking a figure from a calc that ran on another
        case. It is empty for the design case.
        """
        if name not in coherence.TRACKED_TOOLS:
            return [], {}, ""
        try:
            givens = self.record.givens(self.project_id)
            if not givens:
                return [], {}, ""
            calcs = self.record.calcs(self.project_id) if name in coherence.DERIVED else []
            standing: dict[str, dict] = {}
            if calcs:
                standing = coherence.analyze({
                    "fact_history": self.record.facts(self.project_id, include_superseded=True), "calcs": calcs,
                })["calcs"]
            stale = {ident for ident, item in standing.items() if item["state"] == coherence.STALE}
            alternative = {ident for ident, item in standing.items() if item["state"] == coherence.ALTERNATIVE}
            depends, varies = coherence.call_basis(name, args, givens, calcs, resolve_id=self._resolve_id,
                                                   stale=stale, alternative=alternative)
            departs = coherence.departure_text(depends, varies, {row["id"]: row for row in calcs}, standing)
            return depends, varies, departs
        except Exception:
            # The basis is bookkeeping. A failure here never fails the calculation.
            return [], {}, ""

    def _record_tool(self, name: str, args: dict) -> dict:
        if not self.recording:
            raise RecordError("The project record is not open on this turn, so nothing was written.")
        record = self.record
        project_id = self.project_id
        if name == "read_record":
            kind = str(args.get("kind") or "").strip()
            if kind:
                rows = record.detail(project_id, kind, str(args.get("id") or "").strip() or None)
                if kind == "calcs":
                    # A model reads a recorded output the same way it reads a fresh one.
                    rows = [dict(row, outputs=reader_view(row.get("tool") or "", row.get("outputs"))) for row in rows]
                return {"kind": kind, "rows": rows}
            snap = record.snapshot(project_id)
            return {
                "summary": record.summary_text(project_id),
                "counts": {key: len(value) for key, value in snap.items() if isinstance(value, list)},
            }
        if name == "record_fact":
            return self._record_fact(args)
        if name == "record_evidence":
            document = args.get("document")
            row = record.record_evidence(
                project_id, document=document, edition=args.get("edition") or "",
                section=args.get("section") or "", note=args.get("note") or "",
                applicability=args.get("applicability") or "", status=args.get("status") or "held",
                agent=self.agent,
                # A cite follows the edition the job names for its document.
                depends=coherence.evidence_basis(str(document or ""), record.givens(project_id)),
            )
            return {"id": row["id"], "document": row["document"], "section": row["section"], "status": row["status"]}
        if name == "record_finding":
            self._no_given(args.get("label"), "A finding")
            row = record.record_finding(
                project_id, agent=self.agent or LEAD, text=args.get("text"), label=args.get("label"),
                supports=args.get("supports"), replaces=args.get("replaces"),
                may_replace_any=(self.agent or LEAD) == LEAD,
            )
            out = {"id": row["id"], "label": row["label"]}
            if row.get("replaces"):
                out["replaces"] = row["replaces"]
            return self._flag_unknown_supports(out, args.get("supports"), "finding")
        if name == "withdraw_finding":
            ident = str(args.get("id") or "").strip()
            is_lead = (self.agent or LEAD) == LEAD
            if record.has_decision(project_id, ident):
                row = record.retire_decision(project_id, ident, by=self.agent or LEAD, reason=args.get("reason"),
                                             may_retire_any=is_lead)
                return {"id": row["id"], "withdrawn": True, "kind": "decision"}
            row = record.retire_finding(project_id, ident, by=self.agent or LEAD, reason=args.get("reason"),
                                        may_retire_any=is_lead)
            return {"id": row["id"], "withdrawn": True, "kind": "finding"}
        if name == "review_finding":
            row = record.put_review(
                project_id, finding_id=str(args.get("id") or ""), agent=self.agent or LEAD,
                position=str(args.get("position") or "").strip().lower(), note=args.get("note") or "",
            )
            return {"id": row["id"], "finding": row["finding_id"], "position": row["position"], "status": row["status"]}
        if name == "open_question":
            audience = str(args.get("to") or "engineer").strip().lower()
            if audience in ("engineer of record", "eor", "owner", "ahj", "rfi"):
                audience = "engineer"
            if audience in ("user", "the designer"):
                audience = "designer"
            row = record.open_question(
                project_id, raised_by=self.agent or LEAD, text=args.get("text"), audience=audience,
            )
            return {"id": row["id"], "status": row["status"], "to": row["audience"]}
        if name == "record_decision":
            self._no_given(args.get("label"), "A decision")
            row = record.record_decision(
                project_id, text=args.get("text"), decided_by=self.agent or LEAD,
                label=args.get("label"), basis=args.get("basis") or "", supports=args.get("supports"),
                replaces=args.get("replaces"), may_replace_any=(self.agent or LEAD) == LEAD,
            )
            out = {"id": row["id"], "label": row["label"]}
            if row.get("replaces"):
                out["replaces"] = row["replaces"]
            return self._flag_unknown_supports(out, args.get("supports"), "decision")
        if name == "handoff":
            payload = args.get("payload")
            if payload is not None and not isinstance(payload, dict):
                raise RecordError("payload must be an object")
            row = record.create_handoff(
                project_id, from_agent=self.agent or "lead", to_agent=args.get("to"),
                brief=args.get("brief"), payload=payload,
            )
            return {"id": row["id"], "to": row["to_agent"], "status": row["status"]}
        raise KeyError(f"unknown tool {name}")

    def _flag_unknown_supports(self, out: dict, supports, what: str) -> dict:
        """Say in the tool result which support ids are on no table of this job's record.

        The row is written either way: the record never edits what a model
        wrote. But a mistyped id reads later as "not on the record", and the
        model that wrote it is the one that can put it right, in this turn.
        """
        if not isinstance(supports, (list, tuple)):
            return out
        ids = [str(item).strip() for item in supports if str(item or "").strip()]
        if not ids:
            return out
        try:
            record, project_id = self.record, self.project_id
            known = {row["id"] for row in record.calcs(project_id)}
            known |= {row["id"] for row in record.evidence(project_id)}
            known |= {row["id"] for row in record.facts(project_id, include_superseded=True)}
            known |= {row["id"] for row in record.findings(project_id, include_retired=True)}
            known |= {row["id"] for row in record.decisions(project_id, include_retired=True)}
        except Exception:
            # Bookkeeping. A failure here never fails the write that already happened.
            return out
        unknown = [ident for ident in ids if ident not in known]
        if unknown:
            out["not_on_the_record"] = unknown
            out["note"] = (
                "These ids are on no table of this job's record: " + ", ".join(unknown) + f". A {what} that rests "
                "on one has no source there, and the trace check will say so. Look the id up with read_record "
                f"and replace this {what} with one that names the right row."
            )
        return out

    def _no_given(self, label, what: str) -> None:
        if str(label or "").strip().upper() == GIVEN:
            raise RecordError(
                f"{what} is the team's own statement and cannot be labeled GIVEN. "
                "GIVEN marks a value the designer supplied."
            )

    def _record_fact(self, args: dict) -> dict:
        """One fact, with the rules on who may write what.

        The zone inputs and the basis fields are changed by the lead's set_input,
        so every agent keeps working from one set of inputs. GIVEN is the
        designer's own value and only the lead, who talks to the designer,
        writes it. Two contributors that disagree on a key both stay on the record.
        """
        record = self.record
        project_id = self.project_id
        agent = self.agent or LEAD
        kind = str(args.get("kind") or "").strip()
        key = str(args.get("key") or "").strip()
        label = str(args.get("label") or "").strip()
        if kind == INPUT_KIND or (kind == BASIS_KIND and key in BASIS_FIELDS):
            raise RecordError(
                f"{kind}/{key} is a project input. The lead changes it with set_input, so the whole team "
                "works from one value. If you think it is wrong, record an objection or a question."
            )
        if label.upper() == GIVEN and agent != LEAD:
            raise RecordError(
                "GIVEN marks a value the designer stated, and only the lead records it. "
                "Record your own reading with another label, or hand the point to the lead."
            )
        value = "" if args.get("value") is None else str(args.get("value")).strip()
        existing = [row for row in record.facts(project_id, kind) if row["key"] == key] if kind and key else []
        agreed = next((row for row in existing if row["agent"] != agent and str(row["value"]).strip() == value), None)
        if agreed is not None and agent != LEAD:
            return {
                "id": agreed["id"], "kind": kind, "key": key, "label": agreed["label"],
                "note": f"Already on the record with this value, written by {agreed['agent'] or 'the app'}. Nothing new was written.",
            }
        row = record.record_fact(
            project_id, kind=kind, key=key, value=args.get("value"), label=args.get("label"),
            source=args.get("source") or "", agent=agent, supersede=True if agent == LEAD else "own",
        )
        out = {"id": row["id"], "kind": row["kind"], "key": row["key"], "label": row["label"]}
        others = [item for item in existing if item["agent"] != agent and str(item["value"]).strip() != value]
        if others and agent != LEAD:
            out["conflicts_with"] = [
                {"id": item["id"], "by": item["agent"], "value": item["value"]} for item in others
            ]
            out["note"] = (
                "Another contributor recorded a different value for this key. Both stay on the record "
                "until the lead settles it. Say so in your summary."
            )
        return out

    def _fp_calc(self, args: dict) -> dict:
        """One kernel op by name. An op with a tool of its own is refused, and density_area takes its tool's checks."""
        op = str(args.get("op") or "")
        payload = dict(args.get("inputs") or {})
        key = op.strip().lower().replace(" ", "_")
        canonical = (getattr(self.formulas, "OPS", {}) or {}).get(key, key)
        if canonical in _OWN_TOOL_OPS:
            raise ValueError(
                f"fp_calc does not run {op!r}. Call the {_OWN_TOOL_OPS[canonical]} tool: it takes the system type, "
                "the job's edition, and the sub-times by the application's rules."
            )
        if canonical == "density_area":
            _check_density_area(payload, require_increase_and_hose=False)
        missing = _elevation_missing(canonical, payload)
        if missing:
            raise ValueError(
                f"fp_calc {op!r} needs every elevation given: " + ", ".join(missing) + ". Pass 0 where the run is "
                "level; a blank is not taken as 0."
            )
        return self.formulas.dispatch(op, payload)

    def _delivery(self, name: str, args: dict) -> dict:
        """dry_delivery_screen or di_trip_to_water, with the arguments the application owes the kernel.

        The system type is required and goes to the kernel as given (no "di"
        stands in for a blank, and wet has no delivery rows). The delivery
        screen is told the declared interlock (double for di, none for dry,
        unless the caller says). The trip screen is told V is the caller's
        (v_basis caller): the tool plan passes the zone total. The job's NFPA
        13 edition goes to the kernel when the kernel holds its labels; when the
        job pins none, or one the kernel does not hold, the figures run and
        every NFPA 13 cite is withheld, and the row says so. No edition is
        written for it. A sub-time not given leaves the row the fill time alone
        and its margin, with no pass or fail; a sub-time given as 0 is used and
        marked ASSUMED-ZERO.
        """
        _missing(name, args, _DELIVERY_REQUIRED)
        system = _delivery_system(name, args.get("system_type"))
        edition, withheld, requested = self._delivery_edition(args.get("edition"))
        given = [key for key in SUB_TIMES if _number_was_passed(args, key)]
        fill_only = len(given) < len(SUB_TIMES)
        # Fill time only: none of the times goes to the kernel, so no figure is computed on one the job lacks.
        times = {} if fill_only else {key: args[key] for key in SUB_TIMES}
        kwargs: dict[str, Any] = {"basis": args.get("basis"), "system_type": system, **times}
        if edition is not None:
            kwargs["edition"] = edition
        if name == "dry_delivery_screen":
            segments = args.get("segments")
            if isinstance(segments, list) and any(
                    isinstance(row, dict) and row.get("d_in") in (None, "") for row in segments):
                # A takeoff written by nominal size, as zone_trapped_volume takes it. The shop inside
                # diameters are the kernel's (pipe_ids), not a figure worked out here.
                rows, _flags = self.di._segments(segments)
                segments = [{"d_in": row["d_in"], "length_ft": row["length_ft"]} for row in rows]
            declared = args.get("declared_interlock")
            if _blank(declared):
                declared = "double" if system == "di" else "none"
            out = self.formulas.dry_delivery_screen(
                segments, args.get("q_fill_gpm"), qod=args.get("qod", False), declared_interlock=declared, **kwargs)
            out = _govern_delivery_exemption(self.formulas, out, args, self.di, segments)
        else:
            out = self.formulas.di_trip_to_water(args.get("v_gal"), args.get("q_fill_gpm"), v_basis="caller", **kwargs)
        if withheld:
            out = _withhold_cites(out, withheld, requested)
            stated = self._job_edition() if not requested else None
            if stated:
                # Said to the caller, never put in: the job states an edition this call did not pass.
                out["edition_note"] = (f"This call passed no edition. The job states NFPA 13-{stated}; pass edition "
                                       f"{stated} for the kernel's cites.")
        else:
            out = {**out, "edition_status": "pinned"}
        if fill_only:
            out = _fill_time_only(out, [key for key in SUB_TIMES if key not in given])
        else:
            out = _mark_assumed_zero(out, args)
        return _near_threshold(out) if name == "dry_delivery_screen" else out

    def _delivery_edition(self, value: Any) -> tuple[int | None, str, str]:
        """(the edition the kernel is told, why cites are withheld or "", the year the caller asked for).

        Blank: nothing is told and the cites are withheld, EDITION NOT SET. A
        year the kernel holds labels for goes to it. Any other year runs with
        its cites withheld until the kernel holds that edition's labels.
        """
        if _blank(value):
            return None, EDITION_NOT_SET, ""
        years = sorted(set(_YEAR.findall(str(value))))
        if len(years) != 1:
            raise ValueError(f"edition takes one NFPA 13 edition year, not {value!r}. Leave it out when the job "
                             "has not pinned one.")
        year = years[0]
        if self._kernel_holds_edition(int(year)):
            return int(year), "", year
        return None, EDITION_NOT_HELD.format(year=year), year

    def _job_edition(self) -> str | None:
        """The NFPA 13 edition the job pins, read from the record for a note to the caller. None without one."""
        if not self.recording:
            return None
        try:
            return coherence.pinned_edition(self.record.givens(self.project_id).get("nfpa_13"))
        except Exception:
            return None

    def _kernel_holds_edition(self, year: int) -> bool:
        """Whether the kernel's delivery screens carry this NFPA 13 edition's labels. Asked of the kernel."""
        cites = getattr(self.formulas, "nfpa13_cites", None)
        check = cites or getattr(self.formulas, "_parse_nfpa13_dry_edition", None)
        if check is None:
            return False
        try:
            check(year)
        except Exception:
            return False
        return True

    def _run(self, name: str, args: dict) -> dict:
        if name == "list_skills":
            return {"skills": list_skills(self.root)}
        if name == "read_skill":
            slug = str(args.get("slug", ""))
            text = read_skill(self.root, slug)
            if self.recording:
                # Which agent read which method, and exactly which text: the record of content actually used.
                # A read shows the method was in front of the agent. It does not show the agent applied it.
                self.record.log_event(self.project_id, SKILL_READ, {
                    "slug": slug, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
                    "chars": len(text), "content_version": self.pack_version,
                }, agent=self.agent)
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "list_roles":
            return {"roles": list_roles(self.root)}
        if name == "read_role":
            text = read_role(self.root, str(args.get("slug", "")))
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "list_modes":
            return {"modes": list_modes(self.root)}
        if name == "read_mode":
            text = read_mode(self.root, str(args.get("slug", "")))
            if len(text) > 100_000:
                text = text[:100_000] + "\n\n[truncated]"
            return {"slug": args.get("slug"), "text": text}
        if name == "resolve_pipe_id":
            return self.di.pipe_ids.resolve(args.get("nps"), args.get("schedule"), args.get("role"))
        if name == "zone_trapped_volume":
            return self.di.zone_trapped_volume(
                args.get("segments"),
                args.get("length_basis") or "center_to_center",
                args.get("fittings_percent"),
                args.get("trim_gal"),
            )
        if name in ("dry_delivery_screen", "di_trip_to_water"):
            return self._delivery(name, args)
        if name == "density_area":
            return _density_area(self.formulas, args)
        if name == "hose_duration":
            _missing(name, args, ("hazard",))
            return self.formulas.hose_duration(args.get("hazard"), args.get("supervised", False))
        if name == "nitrogen_gate":
            # The pressure and the time are the caller's. A figure that was passed goes to the kernel as passed:
            # a 0 is refused there, never replaced. One not passed is refused here: no starting value stands in.
            _missing(name, args, ("p_psig", "t_min"))
            return _sizing_basis(self.di.nitrogen_gate(args.get("v_gal"), args.get("p_psig"), args.get("t_min")))
        if name == CONVERT_TOOL:
            return units.convert(args.get("value"), args.get("from_unit"), args.get("to_unit"), field=args.get("field"))
        if name == "elect_di_trim":
            # A blank system type is not taken as anything: the call is refused, as a zone run is.
            _missing(name, args, ("system_type",))
            return self.di.elect_di_trim(
                args.get("system_type"),
                prime_held_by=args.get("prime_held_by") or "unknown",
                failsafe_on_total_power_loss=args.get("failsafe_on_total_power_loss", False),
                supervisory_psi=args.get("supervisory_psi"),
                medium=args.get("medium") or "unelected",
                insurer=args.get("insurer") or "",
            )
        if name == "releasing_truth_table":
            return self.di.releasing_truth_table(
                manual_station=args.get("manual_station", True),
                insurer=args.get("insurer") or "",
            )
        if name == "lfl_setpoints":
            return _lfl_setpoints(self.root, args)
        if name == "fp_calc":
            return self._fp_calc(args)
        if name == "fa_calc":
            return run_fa_calc(self.root, args)
        if name == "search_corpus":
            return search_corpus(self.root, args)
        raise KeyError(f"unknown tool {name}")


INERT = "inert"


def _lfl_setpoints(content_root: Path, args: dict) -> dict:
    """Run lfl.setpoints_for. Percents stay whatever the caller passed."""
    path = Path(content_root) / "calcs" / "fa" / "lib" / "lfl.py"
    if not path.is_file():
        raise FileNotFoundError(path)
    module = _load(path)
    mix = args.get("mix") or {}
    table = args.get("lfl") or {}
    screens = args.get("screens") or []
    if not isinstance(mix, dict) or not isinstance(table, dict):
        raise ValueError("mix and lfl must be objects")
    if not isinstance(screens, list):
        raise ValueError("screens must be a list")
    # Every gas in the mix has an LFL the caller gave, or is named inert. A blank, a missing one, a 0, or a negative
    # one holds the call: the kernel reads a gas with no LFL as inert, and the application picks no LFL for it.
    clean_lfl: dict[str, float | None] = {}
    holds = []
    for key, value in table.items():
        if isinstance(value, str) and value.strip().lower() == INERT:
            clean_lfl[str(key)] = None
            continue
        number = None if _blank(value) else _finite(value)
        if number is None or number <= 0:
            holds.append(f"{key} (LFL {value!r})")
            continue
        clean_lfl[str(key)] = number
    clean_mix = {str(key): float(value) for key, value in mix.items()}
    holds.extend(f"{key} (no LFL given)" for key in clean_mix if key not in clean_lfl
                 and not any(f"{key} (LFL" in item for item in holds))
    if holds:
        raise ValueError(
            "HOLD: lfl_setpoints needs a component LFL vol% greater than 0 for every gas in mix, or \"inert\": "
            + ", ".join(holds) + ". The application picks no LFL and no percent."
        )
    clean_screens = []
    for screen in screens:
        if not isinstance(screen, dict):
            raise ValueError("each screen must be an object")
        if "pct" not in screen:
            raise ValueError("each screen needs a pct")
        clean_screens.append({
            "name": str(screen.get("name") or screen.get("id") or ""),
            "pct": float(screen["pct"]),
            "basis": str(screen.get("basis") or ""),
        })
    return module.setpoints_for(clean_mix, clean_lfl, clean_screens)


def dumps(payload) -> str:
    return json.dumps(payload, indent=2, default=str)


def _missing(tool: str, args: dict, keys: tuple[str, ...]) -> None:
    """Refuse a call that leaves out an input the application will not supply, naming each one.

    Nothing is put in its place: no 0 for a time, no FM for a basis, no
    starting value for a fill pressure or a time (inputs.HINTS are hints,
    never inputs). A 0 that was passed is a value and goes on as passed.
    """
    gone = [key for key in keys if not _number_was_passed(args, key)]
    if gone:
        raise ValueError(
            f"{tool} needs {', '.join(gone)}. The application does not put a 0, FM, or a starting value in place "
            "of one that was not given. Pass the job's own value, or ask the designer, or pass a value you state "
            "as ASSUMED with its reason."
        )


def _number_was_passed(args: dict, key: str) -> bool:
    if key not in args:
        return False
    value = args[key]
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


# The elevation arguments of the kernel ops that take one. The kernel puts 0 in for one left out; the application
# does not let that stand: a 0 is allowed only when it is passed (typed).
_ELEVATION_TOP = {
    "electric_overpressure": ("elevation_ft",),
    "relief_check": ("elevation_adj_psi",),
    "bor_demand_pressure": ("dz_ft",),
}
_ELEVATION_SEGMENTS = ("tapered_branch", "cross_main_walk", "bor_demand_pressure")


def _elevation_missing(op: str, payload: dict) -> list[str]:
    """The elevations an fp_calc op would take as 0 because they were left out. Empty when every one was given."""
    missing = [key for key in _ELEVATION_TOP.get(op, ()) if not _number_was_passed(payload, key)]

    def walk(segments: Any, where: str) -> None:
        if not isinstance(segments, list):
            return
        for index, row in enumerate(segments, start=1):
            if isinstance(row, dict) and not _number_was_passed(row, "dz_ft"):
                missing.append(f"{where}[{index}].dz_ft")

    if op in _ELEVATION_SEGMENTS:
        walk(payload.get("segments"), "segments")
    if op == "cross_main_walk" and isinstance(payload.get("branches"), list):
        for index, branch in enumerate(payload["branches"], start=1):
            tapered = branch.get("tapered") if isinstance(branch, dict) else None
            if isinstance(tapered, dict):
                walk(tapered.get("segments"), f"branches[{index}].tapered.segments")
    return missing


def _delivery_system(tool: str, value: Any) -> str:
    """The system type a delivery row runs on: dry or di, as given. Wet has no delivery rows."""
    text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if text in ("wet", "wet_pipe"):
        raise ValueError(f"{tool} takes system_type dry or di. A wet zone has no delivery rows.")
    return str(value).strip()


def _withhold_cites(out: dict, why: str, requested: str) -> dict:
    """The row with every NFPA 13 cite the kernel wrote replaced by why. The figures are the kernel's, unchanged.

    The kernel ran without an edition, so its cites name the one it labels by
    default. That is not the job's edition, so none of them is kept: not on
    the record, not shown, not sent to a model.
    """
    shown = {}
    for key, value in out.items():
        if isinstance(value, str) and _NFPA13_TEXT.search(value):
            shown[key] = why
        else:
            shown[key] = value
    shown["edition"] = None
    shown["edition_status"] = "not set" if why == EDITION_NOT_SET else "not held"
    shown["cites_withheld"] = why
    if requested:
        shown["edition_requested"] = requested
    return shown


def _fill_time_only(out: dict, missing: list[str]) -> dict:
    """A delivery row with a sub-time not given: the fill time and its margin to the limit, and no verdict.

    The kernel ran with no sub-time passed. t_total, the pass or fail, and the
    volume that meets the limit would rest on times the job does not have, so
    they are left out. fill_margin_s is the limit less the fill time alone.
    """
    dropped = ("t_total_s", "passes_screen", "v_max_gal_at_limit", "margin_s")
    shown = {key: value for key, value in out.items() if key not in dropped}
    shown["formula"] = "t_fill = 60*V/Q_fill (fill time only; sub-times not provided)"
    if "margin_s" in out:
        shown["fill_margin_s"] = out["margin_s"]
        shown["fill_margin_basis"] = "the limit less the fill time alone; no detection, releasing, or exhaust time is in it"
    shown["fill_only"] = True
    shown["subtimes_missing"] = list(missing)
    shown["screen_status"] = FILL_ONLY
    return shown


def _mark_assumed_zero(out: dict, args: dict) -> dict:
    """A sub-time given as 0 is used as given, and the row says it is an optimistic assumption."""
    zeros = []
    for key in SUB_TIMES:
        try:
            if float(args.get(key)) == 0.0:
                zeros.append(key)
        except (TypeError, ValueError):
            continue
    if not zeros:
        return out
    return {**out, "assumed_zero": zeros,
            "assumed_zero_note": (", ".join(f"{key} = 0 s" for key in zeros) + f" as typed: {ASSUMED_ZERO}. "
                                  f"A zero sub-time makes the screen more optimistic. {NEEDS_PE_REVIEW}.")}


def _threshold_gal(screen: dict) -> float | None:
    """The size exemption threshold the kernel returned. nfpa_size_cap_gal is its legacy alias, on older rows."""
    for key in ("nfpa_size_threshold_gal", "nfpa_size_cap_gal"):
        value = screen.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _near_threshold(out: dict) -> dict:
    """Flag a zone total within NEAR_THRESHOLD_FRACTION of the exemption threshold. The answer is unchanged."""
    threshold = _threshold_gal(out)
    judged = out.get("exemption_volume_gal")
    if threshold is None or not isinstance(judged, (int, float)) or isinstance(judged, bool) or threshold <= 0:
        return out
    if abs(float(judged) - threshold) > NEAR_THRESHOLD_FRACTION * threshold:
        return out
    return {**out, "near_threshold": (
        f"The zone total of {float(judged):.1f} gal is within {NEAR_THRESHOLD_FRACTION:.0%} of the "
        f"{threshold:.0f} gal exemption threshold. The answer can turn on the trim and fittings figures. "
        f"{NEEDS_PE_REVIEW}.")}


def _sizing_basis(out: dict) -> dict:
    """Say which of the kernel's two fill rates is the larger, the one the owner's ruling sizes on. Both stay."""
    gauge, absolute = out.get("scfm_gauge_basis"), out.get("scfm_abs_basis")
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (gauge, absolute)):
        return out
    which = "absolute" if float(absolute) >= float(gauge) else "gauge"
    figure = float(absolute) if which == "absolute" else float(gauge)
    return {**out, "sizing_basis": which,
            "sizing_note": f"Both bases are quoted; size on the larger, the {which}-basis rate of {figure:.2f} scfm."}


_POSITIVE_DEMAND = ("density_gpm_ft2", "base_area_ft2")
_ASSUMABLE_DEMAND = ("density_gpm_ft2", "base_area_ft2")


def _check_density_area(args: dict, *, require_increase_and_hose: bool = True) -> None:
    """A demand the kernel would compute on a meaningless figure is refused, on every path that reaches it.

    Density and base area must be greater than 0, and a duration greater than
    0 when one is given. The area increase and the hose may be 0, but a blank
    one is not taken as 0 (the density_area tool requires both).
    """
    problems = []
    for key in _POSITIVE_DEMAND:
        if not _number_was_passed(args, key):
            problems.append(f"{key} is required")
            continue
        number = _finite(args[key])
        if number is None or number <= 0:
            problems.append(f"{key} must be a number greater than 0, not {args[key]!r}")
    if _number_was_passed(args, "duration_min"):
        number = _finite(args["duration_min"])
        if number is None or number <= 0:
            problems.append(f"duration_min must be a number greater than 0 when it is given, not {args['duration_min']!r}")
    for key in ("area_increase", "hose_gpm"):
        if not _number_was_passed(args, key):
            if require_increase_and_hose:
                problems.append(f"{key} is required: pass 0 when none applies; a blank is not taken as 0")
            continue
        number = _finite(args[key])
        if number is None or number < 0:
            problems.append(f"{key} must be 0 or more, not {args[key]!r}")
    if problems:
        raise ValueError("density_area: " + "; ".join(problems) + ".")


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _density_area(formulas, args: dict) -> dict:
    """density_area with its checks, and an ASSUMED density or area labeled on the result and everything after it."""
    _check_density_area(args)
    assumed = args.get("assumed") or []
    if isinstance(assumed, str):
        assumed = [assumed]
    if not isinstance(assumed, list) or any(item not in _ASSUMABLE_DEMAND for item in assumed):
        raise ValueError("density_area: assumed lists density_gpm_ft2 and/or base_area_ft2, the values that are ASSUMED.")
    reason = str(args.get("assumed_reason") or "").strip()
    if assumed and not reason:
        raise ValueError("density_area: an ASSUMED density or area needs assumed_reason, why it is used and its source.")
    out = formulas.density_area(
        args.get("density_gpm_ft2"),
        args.get("base_area_ft2"),
        area_increase=args.get("area_increase"),
        hose_gpm=args.get("hose_gpm"),
        duration_min=args.get("duration_min"),
    )
    if not assumed:
        return out
    units_of = {"density_gpm_ft2": "gpm/ft²", "base_area_ft2": "ft²"}
    lines = [f"{key} {float(args[key]):g} {units_of[key]} ASSUMED ({reason}). {NEEDS_PE_REVIEW}." for key in assumed]
    return {**out, "assumed_inputs": [{"name": key, "value": float(args[key]), "unit": units_of[key],
                                       "label": "ASSUMED", "reason": reason} for key in assumed],
            "assumed_note": " ".join(lines), "release_status": ASSUMED_NOT_FOR_RELEASE}


def _govern_delivery_exemption(formulas, screen: dict, args: dict, di=None, segments: Any = None) -> dict:
    """The size exemption on the screen's result follows the zone total, or it is not stated at all.

    The kernel screen compares pipe volume with the threshold. That is a
    lower-bound screen, and the kernel says it does not by itself claim the
    exemption: the comparison that counts uses the full system size. This
    stays until the kernel returns the zone-total exemption itself.

    - zone_gal passed: the exemption is that zone total against the threshold
      (the tool plan passes the takeoff's own zone_gal).
    - trim_gal or fittings_percent passed: the zone total is the kernel's own
      takeoff of these segments with those allowances. One left out takes the
      kernel's ASSUMED value (its cut-length fittings allowance, its trim), never
      0.
    - neither: the result is a pipe-only screen. It says "no" only when the
      pipe alone is already over the threshold, which settles it. Otherwise
      nfpa_delivery_time_exempt is None and exemption_status says why.

    Timing on the pipe-only screen stays in every case.
    """
    # Local import: workflow imports this module at load time.
    from fpfa.workflow import govern_nfpa_exemption, pipe_only_screen

    if _number_was_passed(args, "zone_gal"):
        zone_gal = formulas._require_non_negative("zone_gal", args["zone_gal"])
        return govern_nfpa_exemption(screen, zone_gal, "the zone total passed as zone_gal (pipe + fittings + trim)")
    trim_passed = _number_was_passed(args, "trim_gal")
    fittings_passed = _number_was_passed(args, "fittings_percent")
    if not trim_passed and not fittings_passed:
        return pipe_only_screen(screen)
    if di is None or segments is None:
        raise ValueError("dry_delivery_screen: the zone total needs the kernel's takeoff of the segments.")
    # The kernel's takeoff, cut lengths: an allowance left out is its ASSUMED one, and its flags say so.
    takeoff = di.zone_trapped_volume(
        segments, "cut",
        args["fittings_percent"] if fittings_passed else None,
        args["trim_gal"] if trim_passed else None,
    )
    parts = [f"fittings {float(takeoff['fittings_percent']):g}%"
             + ("" if fittings_passed else " (left out; the kernel's ASSUMED allowance)"),
             f"trim {float(takeoff['trim_gal']):g} gal"
             + ("" if trim_passed else " (left out; the kernel's ASSUMED trim)")]
    governed = govern_nfpa_exemption(screen, float(takeoff["zone_gal"]),
                                     "pipe plus the allowances on this call: " + ", ".join(parts))
    assumed = [flag for flag in takeoff.get("flags") or [] if isinstance(flag, str) and flag.startswith("ASSUMED")]
    if assumed:
        governed["exemption_assumptions"] = assumed
    return governed


_IDENTITY_CACHE: dict[str, str] = {}


def _identity_bytes(data: bytes) -> bytes:
    """A file's bytes as an identity hashes them: its line endings do not count.

    A checkout on Windows holds a text file with CRLF endings where the same
    commit on Linux holds LF, and the bundled seed is built on one and a
    content pack on the other. It is the same code and the same content. An
    identity that differed between them would mark every recorded calculation
    out of date after a content update that changed nothing, and would make a
    fingerprint read on one machine useless on another. A file that holds a
    NUL byte is binary and is hashed as it is.
    """
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def calc_identity(content_root: Path) -> str:
    """Short hash of the calc kernel files under the content root.

    calcs/fp/*.py and calcs/fa/lib/*.py, by path and content, line endings
    aside (_identity_bytes). Any change to the code that produces a figure
    changes this value, and with it the replay key, so a pack update computes
    fresh instead of replaying.
    """
    root = Path(content_root).resolve()
    key = str(root)
    if key in _IDENTITY_CACHE:
        return _IDENTITY_CACHE[key]
    digest = hashlib.sha256()
    files: list[Path] = []
    for folder in (root / "calcs" / "fp", root / "calcs" / "fa" / "lib"):
        if folder.is_dir():
            files.extend(sorted(path for path in folder.glob("*.py") if not path.name.startswith("test_")))
    for path in files:
        try:
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(_identity_bytes(path.read_bytes()))
        except OSError:
            continue
    value = digest.hexdigest()[:16]
    _IDENTITY_CACHE[key] = value
    return value


_FINGERPRINT_CACHE: dict[str, str] = {}
_CONTENT_FOLDERS = ("skills", "roles", "modes", "corpus", "specs", "calcs")


def content_fingerprint(content_root: Path) -> str:
    """Short hash of everything a model or a calc reads from the content pack.

    Every file under skills, roles, modes, corpus, specs, and calcs, by path
    and content, line endings aside (_identity_bytes). Two installs with the
    same fingerprint are working from the same content, whatever version
    label either carries and whichever system each was built on. It is the identity
    an evaluation report and an export print, so a result can be tied to the
    exact content that produced it.
    """
    root = Path(content_root).resolve()
    key = str(root)
    if key in _FINGERPRINT_CACHE:
        return _FINGERPRINT_CACHE[key]
    digest = hashlib.sha256()
    for folder in _CONTENT_FOLDERS:
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
                continue
            try:
                digest.update(path.relative_to(root).as_posix().encode("utf-8"))
                digest.update(_identity_bytes(path.read_bytes()))
            except OSError:
                continue
    value = digest.hexdigest()[:16]
    _FINGERPRINT_CACHE[key] = value
    return value


def _pack_version() -> str:
    """Content version label for calc records. Empty when it cannot be read."""
    try:
        from fpfa.content_update import content_version_text

        return content_version_text()
    except Exception:
        return ""
