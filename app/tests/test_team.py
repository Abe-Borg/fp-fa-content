"""The team on the existing tool loop: lead, specialists, handoffs, and the record-fed checker.

Every model call is a stand-in. The fake create() looks at the system text
to tell a lead turn from a specialist turn from the checker.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def _record():
    from fpfa.record import Record

    return Record(Path(tempfile.mkdtemp(prefix="fpfa-team-")) / "fpfa.db")


def _system_text(kwargs) -> str:
    system = kwargs.get("system")
    if isinstance(system, str):
        return system
    return "".join(block.get("text", "") for block in system or [])


def _turn(stop_reason, *blocks, usage=None):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks), usage=usage)


def _usage(**kwargs):
    base = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    base.update(kwargs)
    return SimpleNamespace(**base)


class Scripted:
    """create() that plays one script per kind of turn, chosen by the system text."""

    def __init__(self, scripts: dict):
        self.scripts = {key: list(value) for key, value in scripts.items()}
        self.calls: list[dict] = []

    def kind(self, kwargs) -> str:
        system = _system_text(kwargs)
        if "Judge each numbered claim from the cites file alone" in system:
            return "checker"
        if "You are the design assistant inside a desktop application" in system:
            return "lead"
        for slug in ("fp-sprinkler", "fa-releasing", "spec-draft"):
            marker = {"fp-sprinkler": "# Sprinkler specialist", "fa-releasing": "# Releasing specialist",
                      "spec-draft": "# Draft narrative"}[slug]
            if system.startswith("---") and marker in system:
                return slug
        return "unknown"

    def __call__(self, **kwargs):
        kind = self.kind(kwargs)
        self.calls.append({"kind": kind, **kwargs})
        script = self.scripts.get(kind)
        if not script:
            raise AssertionError(f"no script for a {kind} turn")
        return script.pop(0)


class SpecialistRosterTests(unittest.TestCase):
    def test_specialists_exclude_the_shell_and_the_checker(self):
        from fpfa.team import list_specialists, specialist_slugs

        slugs = specialist_slugs(REPO)
        self.assertEqual(slugs, ["fa-releasing", "fp-sprinkler", "spec-draft"])
        self.assertTrue(all(row["description"] for row in list_specialists(REPO)))

    def test_specialist_system_is_the_role_file_plus_the_skill_index(self):
        from fpfa.record import RecordError
        from fpfa.roles_loader import read_role
        from fpfa.team import specialist_system

        system = specialist_system(REPO, "fp-sprinkler")
        self.assertTrue(system.startswith(read_role(REPO, "fp-sprinkler").strip()))
        self.assertIn("- sprinkler-system-volume-takeoff:", system)
        self.assertIn("Do not delegate; only the lead does.", system)
        self.assertNotIn("You are the design assistant inside a desktop application", system)
        self.assertNotIn("Spec notes from the content pack", system)
        self.assertIn("Spec notes from the content pack", specialist_system(REPO, "spec-draft"))
        for bad in ("everyday", "qa-specialist", "nobody"):
            with self.assertRaises(RecordError):
                specialist_system(REPO, bad)

    def test_team_schemas_add_three_tools_and_specialists_get_none_of_them(self):
        from fpfa.calc_tools import SCHEMAS
        from fpfa.team import SPECIALIST_SCHEMAS, TEAM_SCHEMAS, TEAM_TOOL_NAMES

        names = [item["name"] for item in TEAM_SCHEMAS]
        for tool in TEAM_TOOL_NAMES:
            self.assertIn(tool, names)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual([item["name"] for item in SPECIALIST_SCHEMAS], [item["name"] for item in SCHEMAS])
        self.assertIn("handoff", [item["name"] for item in SPECIALIST_SCHEMAS])


class DelegateTests(unittest.TestCase):
    def _fp_script(self):
        return [
            _turn("tool_use",
                  Block(type="tool_use", id="t1", name="zone_trapped_volume",
                        input={"segments": [{"nps": 1, "schedule": "sch40", "length_ft": 100, "role": "branch"}]}),
                  usage=_usage(input_tokens=900, output_tokens=40, cache_creation_input_tokens=3000)),
            _turn("tool_use",
                  Block(type="tool_use", id="t2", name="record_finding",
                        input={"text": "Zone total 9.4 gal on the test branch", "label": "calculated",
                               "supports": ["CALC_ID"]}),
                  Block(type="tool_use", id="t3", name="handoff",
                        input={"to": "fa-releasing", "brief": "Write the releasing boolean for this zone",
                               "payload": {"family": "El/El"}}),
                  Block(type="tool_use", id="t4", name="open_question",
                        input={"text": "Trim volume from the valve sheet?"}),
                  usage=_usage(input_tokens=50, output_tokens=120, cache_read_input_tokens=3900)),
            _turn("end_turn", Block(type="text", text="Sized the branch; handed releasing to fa-releasing."),
                  usage=_usage(input_tokens=20, output_tokens=60, cache_read_input_tokens=4000)),
        ]

    def test_delegate_runs_the_specialist_in_its_own_context_and_records_as_it(self):
        from fpfa.team import SPECIALIST_SCHEMAS, delegate

        record = _record()
        record.ensure_project("job1", "Team test")
        create = Scripted({"fp-sprinkler": self._fp_script()})
        # The finding cites a calc id the specialist does not know yet; patch it in after the calc runs.
        calc_holder = {}
        original_call = create.__call__

        def create_with_id(**kwargs):
            if calc_holder.get("id") and create.scripts["fp-sprinkler"]:
                nxt = create.scripts["fp-sprinkler"][0]
                for block in nxt.content:
                    if getattr(block, "name", "") == "record_finding":
                        block.input["supports"] = [calc_holder["id"]]
            return original_call(**kwargs)

        from fpfa import team as team_module
        real_session = team_module.ToolSession

        class Watch(real_session):
            def execute(self, name, arguments):
                out = super().execute(name, arguments)
                if name == "zone_trapped_volume":
                    calc_holder["id"] = record.calcs("job1")[-1]["id"]
                return out

        team_module.ToolSession = Watch
        try:
            contribution = delegate(
                REPO, record, "job1", create_with_id,
                specialist="fp-sprinkler", brief="Size the test branch and name the trim family.",
                inputs={"segments": [{"nps": 1, "schedule": "sch40", "length_ft": 100}]},
            )
        finally:
            team_module.ToolSession = real_session
        self.assertEqual(contribution["specialist"], "fp-sprinkler")
        self.assertEqual(contribution["summary"], "Sized the branch; handed releasing to fa-releasing.")
        self.assertEqual([row["text"] for row in contribution["findings"]], ["Zone total 9.4 gal on the test branch"])
        self.assertEqual(contribution["findings"][0]["supports"], [calc_holder["id"]])
        self.assertEqual([row["to"] for row in contribution["handoffs"]], ["fa-releasing"])
        self.assertEqual([row["text"] for row in contribution["questions"]], ["Trim volume from the valve sheet?"])
        self.assertEqual([row["tool"] for row in contribution["calc_records"]], ["zone_trapped_volume"])
        self.assertEqual(contribution["usage"]["rounds"], 3)
        self.assertEqual(contribution["usage"]["cache_read_input_tokens"], 7900)
        # Every call was a specialist turn with the specialist tool list and the brief in the user text.
        self.assertEqual({call["kind"] for call in create.calls}, {"fp-sprinkler"})
        for call in create.calls:
            self.assertIs(call["tools"], SPECIALIST_SCHEMAS)
        first_user = create.calls[0]["messages"][0]["content"]
        self.assertIn("The lead delegated this task:", first_user)
        self.assertIn("Size the test branch and name the trim family.", first_user)
        self.assertIn('"length_ft": 100', first_user)
        # Rows carry the specialist's slug. The lead's handoff is returned with the summary.
        self.assertEqual(record.findings("job1")[0]["agent"], "fp-sprinkler")
        self.assertEqual(record.calcs("job1")[0]["agent"], "fp-sprinkler")
        self.assertEqual(record.questions("job1")[0]["raised_by"], "fp-sprinkler")
        handoffs = record.handoffs("job1")
        lead_row = next(row for row in handoffs if row["from_agent"] == "lead")
        self.assertEqual(lead_row["to_agent"], "fp-sprinkler")
        self.assertEqual(lead_row["status"], "returned")
        self.assertIn("Sized the branch", lead_row["result"])
        peer_row = next(row for row in handoffs if row["from_agent"] == "fp-sprinkler")
        self.assertEqual(peer_row["status"], "pending")
        self.assertEqual(record.agents("job1")[0]["status"], "done")
        self.assertEqual(record.latest_event("job1", "delegation")["payload"]["findings"], 1)

    def test_pending_handoff_is_delivered_with_the_next_delegation_and_prior_work_is_shown(self):
        from fpfa.team import delegate

        record = _record()
        record.ensure_project("job1")
        record.record_finding("job1", agent="fa-releasing", text="Earlier releasing note", label="PRACTICE")
        peer = record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing",
                                     brief="Write the releasing boolean", payload={"family": "El/El"})
        create = Scripted({"fa-releasing": [
            _turn("tool_use", Block(type="tool_use", id="t1", name="releasing_truth_table",
                                    input={"manual_station": True, "insurer": "FM"})),
            _turn("end_turn", Block(type="text", text="Boolean written.")),
        ]})
        contribution = delegate(REPO, record, "job1", create, specialist="fa-releasing",
                                brief="Write the cause and effect.")
        user = create.calls[0]["messages"][0]["content"]
        self.assertIn("Handoffs waiting for you:", user)
        self.assertIn("from fp-sprinkler: Write the releasing boolean", user)
        self.assertIn('"family": "El/El"', user)
        self.assertIn("Your earlier contribution on this job:", user)
        self.assertIn("Earlier releasing note", user)
        self.assertIn("Project record so far", user)
        self.assertEqual(contribution["delivered_handoffs"], [peer["id"]])
        rows = {row["id"]: row for row in record.handoffs("job1")}
        self.assertEqual(rows[peer["id"]]["status"], "returned")
        self.assertIn("Handled in fa-releasing", rows[peer["id"]]["result"])

    def test_delegate_refuses_a_non_specialist_and_an_empty_brief(self):
        from fpfa.record import RecordError
        from fpfa.team import delegate

        record = _record()
        record.ensure_project("job1")
        create = Scripted({})
        for slug in ("everyday", "qa-specialist", "nobody"):
            with self.assertRaises(RecordError):
                delegate(REPO, record, "job1", create, specialist=slug, brief="x")
        with self.assertRaises(RecordError):
            delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="  ")
        self.assertEqual(create.calls, [])
        self.assertEqual(record.handoffs("job1"), [])

    def test_a_specialist_that_raises_leaves_the_handoff_cancelled(self):
        from fpfa.team import delegate

        record = _record()
        record.ensure_project("job1")

        def boom(**_kwargs):
            raise RuntimeError("network down")

        with self.assertRaises(RuntimeError):
            delegate(REPO, record, "job1", boom, specialist="fp-sprinkler", brief="Size it.")
        row = record.handoffs("job1")[0]
        self.assertEqual(row["status"], "cancelled")
        self.assertEqual(record.agents("job1")[0]["status"], "error")


class LeadTurnTests(unittest.TestCase):
    def test_everyday_turn_with_a_record_is_the_lead_and_sums_the_team_usage(self):
        from fpfa.everyday import assemble_system, run_everyday
        from fpfa.team import TEAM_PARAGRAPH, TEAM_SCHEMAS

        record = _record()
        record.ensure_project("job1")
        create = Scripted({
            "lead": [
                _turn("tool_use", Block(type="tool_use", id="l1", name="list_specialists", input={}),
                      usage=_usage(input_tokens=21000, output_tokens=30)),
                _turn("tool_use", Block(type="tool_use", id="l2", name="delegate",
                                        input={"specialist": "fp-sprinkler", "brief": "Size DH-1.",
                                               "inputs": {"zone": "DH-1"}}),
                      usage=_usage(input_tokens=100, output_tokens=80, cache_read_input_tokens=21000)),
                _turn("end_turn", Block(type="text", text="Design basis follows."),
                      usage=_usage(input_tokens=50, output_tokens=400, cache_read_input_tokens=22000)),
            ],
            "fp-sprinkler": [
                _turn("tool_use", Block(type="tool_use", id="s1", name="hose_duration",
                                        input={"hazard": "ordinary", "supervised": True}),
                      usage=_usage(input_tokens=5000, output_tokens=40)),
                _turn("end_turn", Block(type="text", text="Duration 60 min."),
                      usage=_usage(input_tokens=30, output_tokens=50, cache_read_input_tokens=5000)),
            ],
        })
        out = run_everyday(REPO, create, "Give me the design basis for zone DH-1.", record=record, project_id="job1")
        self.assertEqual(out["text"], "Design basis follows.")
        lead_calls = [call for call in create.calls if call["kind"] == "lead"]
        self.assertEqual(len(lead_calls), 3)
        for call in lead_calls:
            self.assertIs(call["tools"], TEAM_SCHEMAS)
            self.assertIn(TEAM_PARAGRAPH, _system_text(call))
        self.assertEqual(_system_text(lead_calls[0]), assemble_system(REPO, "mixed", team=True))
        self.assertEqual(len(out["delegations"]), 1)
        self.assertEqual(out["delegations"][0]["specialist"], "fp-sprinkler")
        self.assertEqual(out["lead_usage"]["rounds"], 3)
        self.assertEqual(out["usage"]["rounds"], 5)
        self.assertEqual(out["usage"]["input_tokens"], 21000 + 100 + 50 + 5000 + 30)
        self.assertEqual(out["usage"]["cache_read_input_tokens"], 21000 + 22000 + 5000)
        # The delegate tool result the lead saw carries the contribution. The stand-in
        # holds the loop's live message list, so find the tool_result block by its id.
        results = [
            block for message in lead_calls[2]["messages"] if isinstance(message.get("content"), list)
            for block in message["content"] if block.get("type") == "tool_result" and block.get("tool_use_id") == "l2"
        ]
        self.assertEqual(len(results), 1)
        self.assertIn('"specialist": "fp-sprinkler"', results[0]["content"])
        self.assertEqual(record.calcs("job1")[0]["agent"], "fp-sprinkler")
        self.assertEqual([row["from_agent"] for row in record.handoffs("job1")], ["lead"])

    def test_everyday_turn_without_a_record_keeps_the_plain_tools(self):
        from fpfa.calc_tools import SCHEMAS
        from fpfa.everyday import assemble_system, run_everyday
        from fpfa.team import TEAM_PARAGRAPH

        create = Scripted({"lead": [_turn("end_turn", Block(type="text", text="Plain."))]})
        out = run_everyday(REPO, create, "hello")
        self.assertEqual(out["text"], "Plain.")
        self.assertIs(create.calls[0]["tools"], SCHEMAS)
        self.assertNotIn(TEAM_PARAGRAPH, _system_text(create.calls[0]))
        self.assertNotIn("delegations", out)
        self.assertEqual(assemble_system(REPO), assemble_system(REPO, "mixed", team=False))


class RecordCheckTests(unittest.TestCase):
    def _seed(self, record):
        from fpfa.calc_tools import ToolSession

        record.ensure_project("job1")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        calc_id = record.calcs("job1")[0]["id"]
        cite = record.record_evidence("job1", document="NFPA 13", edition="2025", section="19.2.3.1.3",
                                      note="Duration for ordinary hazard is 60 to 90 minutes", status="held",
                                      agent="fp-sprinkler")
        pulled = record.record_evidence("job1", document="FM DS 5-32", edition="2026", section="2.4.3.2.1.2",
                                        note="", status="NOT PULLED", agent="fp-sprinkler")
        f_calc = record.record_finding("job1", agent="fp-sprinkler", text="Duration is 60 min",
                                       label="calculated", supports=[calc_id])
        f_cite = record.record_finding("job1", agent="fp-sprinkler", text="Ordinary hazard duration band is 60 to 90 minutes",
                                       label="CODE", supports=[cite["id"]])
        f_none = record.record_finding("job1", agent="fa-releasing", text="Low air alone never releases", label="PRACTICE")
        f_open = record.record_finding("job1", agent="fp-sprinkler", text="The FM clock is 30 s to design pressure",
                                       label="OWNER", supports=[pulled["id"]])
        f_wrong = record.record_finding("job1", agent="fp-sprinkler", text="Duration is 45 min",
                                        label="calculated", supports=[calc_id])
        return calc_id, [f_calc, f_cite, f_none, f_open, f_wrong]

    def test_check_builds_claims_from_findings_and_cites_from_their_supports(self):
        from fpfa.claim_check import OPEN_MARK, PACKAGE_MARK
        from fpfa.team import build_record_packet

        record = _record()
        calc_id, findings = self._seed(record)
        packet = build_record_packet(record, "job1")
        self.assertEqual(packet["claim_count"], 5)
        claims = packet["claims"].splitlines()
        sources = packet["sources"].splitlines()
        self.assertEqual(claims[0], "1. Duration is 60 min.")
        self.assertIn(PACKAGE_MARK, sources[0])
        self.assertIn("hose_duration", sources[0])
        self.assertIn("60", sources[0])
        self.assertIn("NFPA 13-2025 §19.2.3.1.3. Duration for ordinary hazard is 60 to 90 minutes [held]", sources[1])
        self.assertEqual(sources[2], f"3. {OPEN_MARK}")
        self.assertIn("[NOT PULLED]", sources[3])
        self.assertTrue(packet["meta"][3]["open"])
        self.assertTrue(packet["meta"][0]["calc_only"])
        self.assertFalse(packet["meta"][1]["calc_only"])

    def test_check_applies_the_blind_verdicts_with_the_package_rule(self):
        from fpfa.team import check_record, export_gate, latest_check

        record = _record()
        calc_id, findings = self._seed(record)
        create = Scripted({"checker": [_turn("end_turn", Block(type="text", text=(
            '1. Supported. Cite: "hose_duration 60"\n'
            '2. Supported. Cite: "NFPA 13-2025 §19.2.3.1.3"\n'
            '3. Supported. Cite: "none"\n'
            '4. Supported. Cite: "FM"\n'
            '5. Supported. Cite: "hose_duration 60"\n'
        )))]})
        self.assertIn("no blind check has judged", export_gate(record, "job1"))
        outcome = check_record(REPO, record, "job1", create)
        self.assertEqual(len(create.calls), 1)
        self.assertEqual(create.calls[0]["kind"], "checker")
        self.assertNotIn("tools", create.calls[0])
        user = create.calls[0]["messages"][0]["content"]
        self.assertIn("1. Duration is 60 min.", user)
        self.assertNotIn("Low air alone never releases.\n\n", user.split("sources.md")[0] + "x")
        verdicts = [row["verdict"] for row in outcome["rows"]]
        self.assertEqual(verdicts, ["Supported", "Supported", "Source not found", "Source not found", "Not supported"])
        self.assertFalse(outcome["all_supported"])
        self.assertIn("3, 4, 5", outcome["status_line"])
        statuses = {row["id"]: row["status"] for row in record.findings("job1")}
        self.assertEqual(statuses[findings[0]["id"]], "Supported")
        self.assertEqual(statuses[findings[2]["id"]], "Source not found")
        self.assertEqual(statuses[findings[4]["id"]], "Not supported")
        self.assertEqual(latest_check(record, "job1")["token"], outcome["token"])
        self.assertIn("not Supported", export_gate(record, "job1"))

    def test_gate_opens_on_an_all_supported_current_check_and_closes_when_findings_change(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.design_basis_docx import write_design_basis
        from fpfa.team import check_record, export_gate, latest_check

        record = _record()
        record.ensure_project("job1")
        self.assertEqual(export_gate(record, "job1"), "")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        calc_id = record.calcs("job1")[0]["id"]
        record.record_finding("job1", agent="fp-sprinkler", text="Duration is 60 min", label="calculated", supports=[calc_id])
        create = Scripted({"checker": [
            _turn("end_turn", Block(type="text", text='1. Supported. Cite: "hose_duration 60"')),
            _turn("end_turn", Block(type="text", text='1. Supported. Cite: "hose_duration 60"\n2. Supported. Cite: "x"')),
        ]})
        outcome = check_record(REPO, record, "job1", create)
        self.assertTrue(outcome["all_supported"])
        self.assertEqual(export_gate(record, "job1"), "")
        out = Path(tempfile.mkdtemp(prefix="fpfa-team-out-")) / "basis.docx"
        write_design_basis(out, {"name": "T"}, record.snapshot("job1"), claim_check=latest_check(record, "job1"))
        from docx import Document

        text = "\n".join(cell.text for table in Document(str(out)).tables for row in table.rows for cell in row.cells)
        self.assertIn("Supported", text)
        record.record_finding("job1", agent="fp-sprinkler", text="New claim with no cite", label="PRACTICE")
        self.assertIn("changed after the last blind check", export_gate(record, "job1"))
        second = check_record(REPO, record, "job1", create)
        self.assertFalse(second["all_supported"])
        self.assertEqual([row["verdict"] for row in second["rows"]], ["Supported", "Source not found"])

    def test_check_with_no_findings_says_so(self):
        from fpfa.team import check_record

        record = _record()
        record.ensure_project("job1")
        create = Scripted({})
        outcome = check_record(REPO, record, "job1", create)
        self.assertEqual(outcome["claim_count"], 0)
        self.assertFalse(outcome["all_supported"])
        self.assertEqual(create.calls, [])

    def test_lead_request_check_tool_runs_the_checker(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.team import TeamSession

        record = _record()
        record.ensure_project("job1")
        session = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        session.execute("hose_duration", {"hazard": "ordinary", "supervised": True})
        calc_id = record.calcs("job1")[0]["id"]
        record.record_finding("job1", agent="fp-sprinkler", text="Duration is 60 min", label="calculated", supports=[calc_id])
        create = Scripted({"checker": [_turn("end_turn", Block(type="text", text='1. Supported. Cite: "hose_duration 60"'))]})
        team = TeamSession(REPO, record, "job1", create)
        out = team.execute("request_check", {})
        self.assertTrue(out["all_supported"])
        self.assertEqual(len(team.checks), 1)
        self.assertEqual(team.execute("list_specialists", {})["specialists"][0]["slug"], "fa-releasing")
        self.assertEqual(team.execute("hose_duration", {"hazard": "ordinary", "supervised": True})["duration_min"], 60)
        self.assertEqual(record.calcs("job1")[0]["replay_count"], 1)


if __name__ == "__main__":
    unittest.main()
