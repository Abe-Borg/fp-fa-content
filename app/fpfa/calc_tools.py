"""Claude tool schemas. Every number comes from calcs/fp, loaded from the content pack."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from fpfa.corpus_search import search_corpus
from fpfa.fa_calc import run_fa_calc
from fpfa.modes_loader import list_modes, read_mode
from fpfa.record import CALC_TOOLS, LABELS, Record, RecordError
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
        "description": "Trapped gallons for one zone. Pipe volume is formulas.pipe_volume. Fittings and trim are added here, not in your head.",
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
            "Pipe timing, NFPA size cap, and optimistic trip-to-water screen from formulas.dry_delivery_screen. "
            "Not a listed water-delivery calculation. Timing stays on pipe volume. "
            "Pass trim_gal and fittings_percent when the zone has them. "
            "nfpa_delivery_time_exempt then uses the zone total (pipe + fittings + trim) "
            "through the same rule as /run. Omitted fittings_percent counts as 0 when trim_gal is passed. "
            "Double-interlock has a 500 gal cap; a quick-opening device does not raise it."
        ),
        "input_schema": _obj(
            {
                "segments": {"type": "array"},
                "q_fill_gpm": {"type": "number"},
                "qod": {"type": "boolean"},
                "t_detect_s": {"type": "number"},
                "t_release_s": {"type": "number"},
                "t_exhaust_s": {"type": "number"},
                "basis": {"type": "string", "description": "FM or NFPA-OH"},
                "system_type": {"type": "string", "description": "dry or di"},
                "trim_gal": {"type": "number", "description": "Trim gallons to include in the size exemption. Omit for a pipe-only screen."},
                "fittings_percent": {"type": "number", "description": "Fittings allowance percent. Used with trim_gal for the zone-total exemption."},
            },
            ["segments", "q_fill_gpm", "system_type"],
        ),
    },
    {
        "name": "di_trip_to_water",
        "description": "Optimistic t = t_detect + t_release + t_exhaust + 60*V/Q from formulas.di_trip_to_water. Pass the zone total gallons, including trim. Not a listed delivery-time proof.",
        "input_schema": _obj(
            {
                "v_gal": {"type": "number"},
                "q_fill_gpm": {"type": "number"},
                "t_detect_s": {"type": "number"},
                "t_release_s": {"type": "number"},
                "t_exhaust_s": {"type": "number"},
                "basis": {"type": "string"},
            },
            ["v_gal", "q_fill_gpm"],
        ),
    },
    {
        "name": "density_area",
        "description": "Sprinkler demand from formulas.density_area. design area = base * (1 + increase); demand adds hose.",
        "input_schema": _obj(
            {
                "density_gpm_ft2": {"type": "number"},
                "base_area_ft2": {"type": "number"},
                "area_increase": {"type": "number"},
                "hose_gpm": {"type": "number"},
                "duration_min": {"type": "number"},
            },
            ["density_gpm_ft2", "base_area_ft2"],
        ),
    },
    {
        "name": "hose_duration",
        "description": "Hose stream and duration from formulas.hose_duration (NFPA 13-2025 Table 19.2.3.1.2 screen).",
        "input_schema": _obj(
            {"hazard": {"type": "string"}, "supervised": {"type": "boolean"}},
            ["hazard"],
        ),
    },
    {
        "name": "nitrogen_gate",
        "description": (
            "Design C is 100. Fill scfm is formulas.air_fill_scfm. "
            "The result states the gauge-basis rate and the absolute-basis rate. Quote both. "
            "Do not emit C=120 as the design value."
        ),
        "input_schema": _obj(
            {"v_gal": {"type": "number"}, "p_psig": {"type": "number"}, "t_min": {"type": "number"}},
            ["v_gal"],
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
        "description": "Build the double-interlock solenoid truth table in code. solenoid = (detection OR manual) AND low air AND NOT isolated. A second smoke zone must not change the result.",
        "input_schema": _obj(
            {"manual_station": {"type": "boolean"}, "insurer": {"type": "string"}},
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
                "lfl": {"type": "object", "description": "Gas name to component LFL vol%. Use null for an inert."},
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
        "description": "Run any other op in calcs/fp/formulas.py by name (hazen_williams, pump_envelope, k_factor, and the rest). Pass op and inputs. Do not compute the formula yourself.",
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
            "Write one basis-of-design fact to this job's project record: AHJ, adopted code and edition, "
            "insurer, owner standard, or an assumption. label is calculated, ASSUMED, use best judgment, "
            "or a cite class (CODE, OWNER, PRACTICE, PARA, HB). The record is the source for the export."
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
            "Write one finding to the project record with its label and the ids of the calc records or "
            "evidence rows that support it. A figure with no calc record id is not calculated."
        ),
        "input_schema": _obj(
            {
                "text": {"type": "string"},
                "label": {"type": "string", "description": "One of: " + ", ".join(LABELS)},
                "supports": {"type": "array", "description": "Record ids this finding rests on.", "items": {"type": "string"}},
            },
            ["text", "label"],
        ),
    },
    {
        "name": "open_question",
        "description": "Write an open question or RFI for the engineer of record to the project record.",
        "input_schema": _obj({"text": {"type": "string"}}, ["text"]),
    },
    {
        "name": "record_decision",
        "description": (
            "Write an election or a judgment to the project record, with its basis and label. "
            "A decision the tools did not return is use best judgment."
        ),
        "input_schema": _obj(
            {
                "text": {"type": "string"},
                "label": {"type": "string", "description": "One of: " + ", ".join(LABELS)},
                "basis": {"type": "string", "description": "Cites or calc record ids behind the decision. Optional."},
            },
            ["text", "label"],
        ),
    },
    {
        "name": "read_record",
        "description": (
            "Show this job's project record with row ids: facts, calc records with inputs and outputs, "
            "evidence, findings, decisions, open questions, and pending handoffs. Pass kind for the full "
            "rows of one table (calcs, evidence, facts, findings, questions, decisions, handoffs, tasks, agents, jobs), "
            "and id for one row."
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

    @property
    def recording(self) -> bool:
        return self.record is not None and self.project_id is not None

    def execute(self, name: str, arguments: dict | None) -> dict:
        args = dict(arguments or {})
        if name in RECORD_TOOLS:
            return self._record_tool(name, args)
        if name in CALC_TOOLS and self.recording:
            found = self.record.find_calc(self.project_id, name, args, self.calc_identity)
            if found is not None:
                # Same tool, inputs, calc code, and project: count the replay and return the recorded output.
                row = self.record.record_calc(
                    self.project_id, tool=name, inputs=args, outputs=found["outputs"],
                    agent=self.agent, calc_identity=self.calc_identity,
                )
                return self._with_record_id(found["outputs"], row["id"])
            output = self._run(name, args)
            row = self.record.record_calc(
                self.project_id, tool=name, inputs=args, outputs=output,
                agent=self.agent, pack_version=self.pack_version, calc_identity=self.calc_identity,
            )
            return self._with_record_id(output, row["id"])
        return self._run(name, args)

    def _with_record_id(self, output: dict, record_id: str) -> dict:
        """A model-facing result carries the calc record id so a finding can cite it.

        The fixed tool plan (agent tool-plan) gets the bare output, so its
        tables and export stay byte-identical to a run with no record.
        """
        if self.agent in ("", "tool-plan") or not isinstance(output, dict):
            return output
        shown = dict(output)
        shown["record_id"] = record_id
        return shown

    def _record_tool(self, name: str, args: dict) -> dict:
        if not self.recording:
            raise RecordError("The project record is not open on this turn, so nothing was written.")
        record = self.record
        project_id = self.project_id
        if name == "read_record":
            kind = str(args.get("kind") or "").strip()
            if kind:
                rows = record.detail(project_id, kind, str(args.get("id") or "").strip() or None)
                return {"kind": kind, "rows": rows}
            snap = record.snapshot(project_id)
            return {
                "summary": record.summary_text(project_id),
                "counts": {key: len(value) for key, value in snap.items() if isinstance(value, list)},
            }
        if name == "record_fact":
            row = record.record_fact(
                project_id, kind=args.get("kind"), key=args.get("key"), value=args.get("value"),
                label=args.get("label"), source=args.get("source") or "", agent=self.agent,
            )
            return {"id": row["id"], "kind": row["kind"], "key": row["key"], "label": row["label"]}
        if name == "record_evidence":
            row = record.record_evidence(
                project_id, document=args.get("document"), edition=args.get("edition") or "",
                section=args.get("section") or "", note=args.get("note") or "",
                applicability=args.get("applicability") or "", status=args.get("status") or "held",
                agent=self.agent,
            )
            return {"id": row["id"], "document": row["document"], "section": row["section"], "status": row["status"]}
        if name == "record_finding":
            row = record.record_finding(
                project_id, agent=self.agent or "lead", text=args.get("text"), label=args.get("label"),
                supports=args.get("supports"),
            )
            return {"id": row["id"], "label": row["label"]}
        if name == "open_question":
            row = record.open_question(project_id, raised_by=self.agent or "lead", text=args.get("text"))
            return {"id": row["id"], "status": row["status"]}
        if name == "record_decision":
            row = record.record_decision(
                project_id, text=args.get("text"), decided_by=self.agent or "lead",
                label=args.get("label"), basis=args.get("basis") or "",
            )
            return {"id": row["id"], "label": row["label"]}
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

    def _run(self, name: str, args: dict) -> dict:
        if name == "list_skills":
            return {"skills": list_skills(self.root)}
        if name == "read_skill":
            text = read_skill(self.root, str(args.get("slug", "")))
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
        if name == "dry_delivery_screen":
            screen = self.formulas.dry_delivery_screen(
                args.get("segments"),
                args.get("q_fill_gpm"),
                qod=args.get("qod", False),
                t_detect_s=args.get("t_detect_s", 0),
                t_release_s=args.get("t_release_s", 0),
                t_exhaust_s=args.get("t_exhaust_s", 0),
                basis=args.get("basis") or "FM",
                system_type=args.get("system_type") or "di",
            )
            return _govern_delivery_exemption(self.formulas, screen, args)
        if name == "di_trip_to_water":
            return self.formulas.di_trip_to_water(
                args.get("v_gal"),
                args.get("q_fill_gpm"),
                t_detect_s=args.get("t_detect_s", 0),
                t_release_s=args.get("t_release_s", 0),
                t_exhaust_s=args.get("t_exhaust_s", 0),
                basis=args.get("basis") or "FM",
            )
        if name == "density_area":
            return self.formulas.density_area(
                args.get("density_gpm_ft2"),
                args.get("base_area_ft2"),
                area_increase=args.get("area_increase") or 0,
                hose_gpm=args.get("hose_gpm") or 0,
                duration_min=args.get("duration_min"),
            )
        if name == "hose_duration":
            return self.formulas.hose_duration(args.get("hazard") or "ordinary", args.get("supervised", False))
        if name == "nitrogen_gate":
            return self.di.nitrogen_gate(args.get("v_gal"), args.get("p_psig") or 40, args.get("t_min") or 30)
        if name == "elect_di_trim":
            return self.di.elect_di_trim(
                args.get("system_type") or "",
                prime_held_by=args.get("prime_held_by") or "unknown",
                failsafe_on_total_power_loss=args.get("failsafe_on_total_power_loss", False),
                supervisory_psi=args.get("supervisory_psi"),
                medium=args.get("medium") or "unelected",
                insurer=args.get("insurer") or "",
            )
        if name == "releasing_truth_table":
            return self.di.releasing_truth_table(
                manual_station=args.get("manual_station", True),
                insurer=args.get("insurer") or "FM",
            )
        if name == "lfl_setpoints":
            return _lfl_setpoints(self.root, args)
        if name == "fp_calc":
            return self.formulas.dispatch(str(args.get("op") or ""), dict(args.get("inputs") or {}))
        if name == "fa_calc":
            return run_fa_calc(self.root, args)
        if name == "search_corpus":
            return search_corpus(self.root, args)
        raise KeyError(f"unknown tool {name}")


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
    clean_lfl = {}
    for key, value in table.items():
        if value is None or value == "":
            clean_lfl[str(key)] = None
        else:
            clean_lfl[str(key)] = float(value)
    clean_mix = {str(key): float(value) for key, value in mix.items()}
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


def _number_was_passed(args: dict, key: str) -> bool:
    if key not in args:
        return False
    value = args[key]
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _govern_delivery_exemption(formulas, screen: dict, args: dict) -> dict:
    """Size exemption follows the zone total when trim or fittings were passed.

    Timing on the pipe-only screen stays. ``govern_nfpa_exemption`` is the same
    helper ``/run`` uses. A call with neither trim nor fittings stays pipe-only.
    """
    trim_passed = _number_was_passed(args, "trim_gal")
    fittings_passed = _number_was_passed(args, "fittings_percent")
    if not trim_passed and not fittings_passed:
        return screen
    trim = formulas._require_non_negative("trim_gal", args["trim_gal"]) if trim_passed else 0.0
    fittings = (
        formulas._require_non_negative("fittings_percent", args["fittings_percent"])
        if fittings_passed else 0.0
    )
    pipe = float(screen["volume_gal"])
    zone_gal = pipe * (1.0 + fittings / 100.0) + trim
    # Local import: workflow imports this module at load time.
    from fpfa.workflow import govern_nfpa_exemption

    return govern_nfpa_exemption(screen, zone_gal)


_IDENTITY_CACHE: dict[str, str] = {}


def calc_identity(content_root: Path) -> str:
    """Short hash of the calc kernel files under the content root.

    calcs/fp/*.py and calcs/fa/lib/*.py, by path and bytes. Any change to the
    code that produces a figure changes this value, and with it the replay
    key, so a pack update computes fresh instead of replaying.
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
            digest.update(path.read_bytes())
        except OSError:
            continue
    value = digest.hexdigest()[:16]
    _IDENTITY_CACHE[key] = value
    return value


def _pack_version() -> str:
    """Content version label for calc records. Empty when it cannot be read."""
    try:
        from fpfa.content_update import content_version_text

        return content_version_text()
    except Exception:
        return ""
