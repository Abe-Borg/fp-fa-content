"""The team protocol: what each agent is told, what its tools do, and what the record keeps.

A lead that owns the objective. Specialists that ask one another, review one
another's findings, and revise. A record that says who said what to whom.

Every model call here is a stand-in that plays a script. So these tests show
the application's side of the protocol and nothing about what a live model
chooses to do with it. docs/live-evaluation.md is the path for that.
"""

from __future__ import annotations

import itertools
import json
import sys
import threading
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from test_coherence import _seed_inputs  # noqa: E402
from test_team import Block, _record, _system_text, _turn, _usage  # noqa: E402

_ids = itertools.count(1)
_MARKERS = (
    ("fp-sprinkler", "# Sprinkler specialist"),
    ("fa-releasing", "# Releasing specialist"),
    ("spec-draft", "# Draft narrative"),
)


def use(tool: str, /, **args) -> Block:
    return Block(type="tool_use", id=f"u{next(_ids)}", name=tool, input=args)


def call(*blocks, **usage):
    return _turn("tool_use", *blocks, usage=_usage(**(usage or {"input_tokens": 100, "output_tokens": 20})))


def say(text: str, **usage):
    return _turn("end_turn", Block(type="text", text=text), usage=_usage(**(usage or {"input_tokens": 10, "output_tokens": 10})))


class Play:
    """create() that plays one script per agent. A step may be a function of the request,
    so it can cite an id an earlier step wrote."""

    def __init__(self, scripts: dict):
        self.scripts = {key: list(value) for key, value in scripts.items()}
        self.calls: list[dict] = []

    def kind(self, kwargs) -> str:
        system = _system_text(kwargs)
        if "Judge each numbered claim from the cites file alone" in system:
            return "checker"
        if "# Team lead" in system:
            return "lead"
        for slug, marker in _MARKERS:
            if marker in system:
                return slug
        return "unknown"

    def __call__(self, **kwargs):
        kind = self.kind(kwargs)
        first = kwargs["messages"][0]["content"]
        self.calls.append({"kind": kind, "user": first if isinstance(first, str) else "", **kwargs})
        script = self.scripts.get(kind)
        if not script:
            raise AssertionError(f"no script left for a {kind} turn")
        step = script.pop(0)
        return step(kwargs) if callable(step) else step

    def of(self, kind: str) -> list[dict]:
        return [item for item in self.calls if item["kind"] == kind]

    def result(self, block: Block) -> dict:
        """The tool_result the model was handed for one tool_use."""
        for item in self.calls:
            for message in item["messages"]:
                if not isinstance(message.get("content"), list):
                    continue
                for part in message["content"]:
                    if part.get("type") == "tool_result" and part.get("tool_use_id") == block.id:
                        return part
        raise AssertionError(f"no result for {block.name}")


def _calc(record, tool: str, agent: str = "", project_id: str = "job1") -> dict:
    rows = [row for row in record.calcs(project_id) if row["tool"] == tool and (not agent or row["agent"] == agent)]
    if not rows:
        raise AssertionError(f"no {tool} calc on the record")
    return rows[-1]


def _finding(record, needle: str, project_id: str = "job1") -> dict:
    for row in record.findings(project_id, include_retired=True):
        if needle in row["text"]:
            return row
    raise AssertionError(f"no finding with {needle!r}")


SEGMENTS = [
    {"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 900},
    {"role": "branch", "nps": "2", "schedule": "sch40", "length_ft": 220},
    {"role": "cross", "nps": "4", "schedule": "sch10", "length_ft": 160},
    {"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 48},
]


def _screen_steps(record, *, t_release: float, text: str, replaces: str = "", before=None):
    """A sprinkler specialist's rounds: the volume, the trip-to-water screen, a finding on it, a summary."""

    def volume(_kwargs):
        return call(use("zone_trapped_volume", segments=SEGMENTS))

    def screen(_kwargs):
        gallons = _calc(record, "zone_trapped_volume", "fp-sprinkler")["outputs"]["zone_gal"]
        return call(use("di_trip_to_water", v_gal=gallons, q_fill_gpm=600, t_detect_s=8, t_release_s=t_release, basis="FM"))

    def finding(_kwargs):
        args = {"text": text, "label": "calculated", "supports": [_calc(record, "di_trip_to_water", "fp-sprinkler")["id"]]}
        if replaces:
            args["replaces"] = _finding(record, replaces)["id"]
        return call(use("record_finding", **args))

    steps = [volume, screen, finding, say("Screen recorded.")]
    return (list(before or []) + steps)


class ConsultTests(unittest.TestCase):
    def test_one_specialist_asks_another_and_gets_the_answer_inside_its_own_turn(self):
        from fpfa.team import SPECIALIST_SCHEMAS, delegate

        record = _record()
        _seed_inputs(record)
        ask = use("consult", specialist="fa-releasing",
                  question="What releasing time does the sequence carry for DH-1? I need it for the trip-to-water screen.",
                  context="Zone volume is on the record. The form holds 2 s.")
        note = use("record_finding", text="The releasing sequence carries 2 s from the first detection signal to the solenoid.",
                   label="PRACTICE")
        create = Play({
            "fp-sprinkler": [call(ask)] + _screen_steps(record, t_release=2, text="Trip to water screens against the 30 s clock with 2 s releasing time"),
            "fa-releasing": [call(note), say("2 s. It is on the record as my finding.")],
        })
        contribution = delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1 water delivery.")

        # The asked specialist ran in its own context, under its own role, with the question and who asked.
        asked = create.of("fa-releasing")
        self.assertEqual(len(asked), 2)
        self.assertIn("# Releasing specialist", _system_text(asked[0]))
        self.assertNotIn("# Sprinkler specialist", _system_text(asked[0]))
        self.assertIs(asked[0]["tools"], SPECIALIST_SCHEMAS)
        self.assertTrue(asked[0]["user"].startswith(
            "You are the specialist fa-releasing on this job. The specialist fp-sprinkler is in the middle of its task"))
        self.assertIn("What releasing time does the sequence carry for DH-1?", asked[0]["user"])
        self.assertIn("What fp-sprinkler has so far:\nZone volume is on the record. The form holds 2 s.", asked[0]["user"])
        self.assertIn("Project inputs. The whole team works from these.", asked[0]["user"])
        self.assertIn("You cannot consult in turn.", asked[0]["user"])

        # The asker got the answer as the tool's result, in the same turn, and went on.
        result = create.result(ask)
        self.assertFalse(result["is_error"])
        answer = json.loads(result["content"])
        self.assertEqual(answer["from"], "fa-releasing")
        self.assertEqual(answer["answer"], "2 s. It is on the record as my finding.")
        self.assertEqual([row["label"] for row in answer["findings"]], ["PRACTICE"])
        self.assertNotIn("usage", answer)
        self.assertEqual(len(create.of("fp-sprinkler")), 5)

        # The exchange is a record row with a sender, a receiver, the question, and the answer.
        rows = [row for row in record.handoffs("job1") if row["kind"] == "consult"]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["from_agent"], rows[0]["to_agent"], rows[0]["status"]), ("fp-sprinkler", "fa-releasing", "returned"))
        self.assertIn("What releasing time", rows[0]["brief"])
        self.assertEqual(rows[0]["result"], "2 s. It is on the record as my finding.")
        self.assertEqual(_finding(record, "releasing sequence carries 2 s")["agent"], "fa-releasing")
        event = record.latest_event("job1", "consult")["payload"]
        self.assertEqual((event["from"], event["to"], event["findings"]), ("fp-sprinkler", "fa-releasing", 1))
        self.assertEqual(event["usage"]["rounds"], 2)

        # The lead is told about it, and the delegation's cost includes the question it asked.
        self.assertEqual(len(contribution["consults"]), 1)
        self.assertEqual(contribution["consults"][0]["asked"], "fa-releasing")
        self.assertEqual(contribution["consults"][0]["answer"], "2 s. It is on the record as my finding.")
        self.assertEqual(contribution["handoffs"], [], "a consult is not work left for later")
        self.assertEqual(contribution["usage"]["rounds"], 5 + 2)
        self.assertEqual(record.latest_event("job1", "delegation")["payload"]["consults"], 1)
        agents = {row["role_slug"]: row["status"] for row in record.agents("job1")}
        self.assertEqual(agents, {"fp-sprinkler": "done", "fa-releasing": "done"})

    def test_a_consult_does_not_nest_is_bounded_and_refuses_a_wrong_target(self):
        from fpfa.record import RecordError
        from fpfa.team import MAX_CONSULTS, SpecialistSession, consult, delegate

        record = _record()
        _seed_inputs(record)
        ask = use("consult", specialist="fa-releasing", question="What releasing time?")
        back = use("consult", specialist="fp-sprinkler", question="What is the zone volume?")
        create = Play({
            "fp-sprinkler": [call(ask), say("Done.")],
            "fa-releasing": [call(back), say("I could not ask back. I need the zone volume.")],
        })
        delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1.")
        refused = create.result(back)
        self.assertTrue(refused["is_error"])
        self.assertIn("cannot consult in turn", refused["content"])
        self.assertEqual(len([row for row in record.handoffs("job1") if row["kind"] == "consult"]), 1)

        quiet = Play({})
        for slug in ("fp-sprinkler", "lead", "qa-specialist", "everyday", "nobody"):
            with self.assertRaises(RecordError, msg=slug):
                consult(REPO, record, "job1", quiet, asker="fp-sprinkler", specialist=slug, question="x")
        with self.assertRaises(RecordError):
            consult(REPO, record, "job1", quiet, asker="fp-sprinkler", specialist="fa-releasing", question="  ")
        self.assertEqual(quiet.calls, [])

        session = SpecialistSession(REPO, record, "job1", quiet, agent="fp-sprinkler")
        session.consults = [{}] * MAX_CONSULTS
        with self.assertRaises(RecordError) as caught:
            session.execute("consult", {"specialist": "fa-releasing", "question": "One more?"})
        self.assertIn(f"used its {MAX_CONSULTS} consults", str(caught.exception))

    def test_a_cancel_during_a_consult_closes_the_exchange_and_keeps_what_was_billed(self):
        from fpfa.claude_client import TurnCancelled
        from fpfa.team import delegate

        record = _record()
        _seed_inputs(record)
        cancel = threading.Event()

        def answer_then_cancel(_kwargs):
            cancel.set()
            return call(use("read_record"), input_tokens=700, output_tokens=30)

        create = Play({
            "fp-sprinkler": [call(use("consult", specialist="fa-releasing", question="What releasing time?"),
                                  input_tokens=900, output_tokens=40)],
            "fa-releasing": [answer_then_cancel],
        })
        with self.assertRaises(TurnCancelled) as caught:
            delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1.", cancel=cancel)
        # Both contexts ran one billed round. Both close on the record.
        self.assertEqual(caught.exception.usage["rounds"], 2)
        self.assertEqual(caught.exception.usage["input_tokens"], 1600)
        rows = {row["kind"]: row for row in record.handoffs("job1")}
        self.assertEqual(rows["consult"]["status"], "cancelled")
        self.assertEqual(rows["delegation"]["status"], "cancelled")
        self.assertTrue(record.latest_event("job1", "consult")["payload"]["cancelled"])
        closed = record.latest_event("job1", "delegation")["payload"]
        self.assertTrue(closed["cancelled"])
        self.assertEqual(closed["usage"]["input_tokens"], 1600)
        agents = {row["role_slug"]: row["status"] for row in record.agents("job1")}
        self.assertEqual(agents, {"fp-sprinkler": "interrupted", "fa-releasing": "interrupted"})


class ReconcileTests(unittest.TestCase):
    """A real dependency: the sprinkler screen uses a releasing time the releasing specialist owns."""

    def _first_pass(self, record):
        from fpfa.team import delegate

        create = Play({"fp-sprinkler": _screen_steps(
            record, t_release=0, text="Trip to water screens against the 30 s clock with no releasing delay")})
        return create, delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1 water delivery.")

    def test_the_application_sees_a_calc_that_left_the_project_inputs_before_any_model_does(self):
        from fpfa import status
        from fpfa.team import lead_status

        record = _record()
        _seed_inputs(record)
        create, contribution = self._first_pass(record)
        # The specialist was told at the tool result that it ran an alternative.
        screen = next(block for item in create.of("fp-sprinkler") for message in item["messages"]
                      if isinstance(message.get("content"), list) for block in message["content"]
                      if block.get("type") == "tool_result" and "differs_from_project_inputs" in str(block.get("content")))
        self.assertIn("t_release_s", screen["content"])
        self.assertIn("recorded as an alternative, not the design case", screen["content"])
        # The lead is told in the delegate result and again at the top of its next message.
        waiting = contribution["still_unsettled_on_the_record"]["on_another_value_than_the_project_input"]
        self.assertEqual(len(waiting), 1)
        self.assertIn("no releasing delay", waiting[0]["finding"])
        block = lead_status(record, "job1")
        self.assertIn("Findings that rest on a value other than the project input.", block)
        self.assertIn("t_release_s", block)
        digest = status.build(record.snapshot("job1"))
        self.assertEqual(status.needs_attention(digest), 0, "an alternative is a note for the lead, not a blocker by itself")
        self.assertEqual(len(digest["alternatives"]), 1)

    def test_one_specialist_objects_the_author_revises_and_the_objection_closes_itself(self):
        from fpfa import status
        from fpfa.team import delegate, lead_status, team_summary

        record = _record()
        _seed_inputs(record)
        self._first_pass(record)
        wrong = _finding(record, "no releasing delay")

        # The releasing specialist is shown the other contributor's finding and asked where it stands.
        def object_to_it(kwargs):
            return call(use("review_finding", id=wrong["id"], position="object",
                            note="The sequence carries 2 s to the solenoid. The screen has to include it. "
                                 "Run it on the project input and I will agree."))

        review = Play({"fa-releasing": [object_to_it, say("I object to the screen: it leaves out the 2 s releasing time.")]})
        second = delegate(REPO, record, "job1", review, specialist="fa-releasing", brief="Write the releasing sequence for DH-1.")
        brief = review.of("fa-releasing")[0]["user"]
        self.assertIn("What on the record needs you:", brief)
        self.assertIn("Other contributors' findings you have not reviewed.", brief)
        self.assertIn(f"- [{wrong['id']}] fp-sprinkler (calculated): Trip to water screens", brief)
        self.assertEqual([(row["position"], row["of"]) for row in second["reviews"]], [("object", "fp-sprinkler")])
        still = second["still_unsettled_on_the_record"]["objections"]
        self.assertEqual([(row["by"], row["against"], row["status"]) for row in still], [("fa-releasing", "fp-sprinkler", "open")])
        review_id = still[0]["review_id"]

        # It is open on the record, in the lead's status block, and it counts as waiting.
        block = lead_status(record, "job1")
        self.assertIn("Open objections. Each needs an end", block)
        self.assertIn(f"review [{review_id}]: fa-releasing objects to fp-sprinkler's finding [{wrong['id']}]", block)
        digest = status.build(record.snapshot("job1"))
        self.assertEqual(status.needs_attention(digest), 1)
        self.assertIn("fa-releasing agrees" if False else "fa-releasing objects", status.record_text(record.snapshot("job1")))

        # The author is told about the objection and revises. The old finding becomes history.
        fix = Play({"fp-sprinkler": _screen_steps(
            record, t_release=2, replaces="no releasing delay",
            text="Trip to water screens against the 30 s clock with the 2 s releasing time included")})
        third = delegate(REPO, record, "job1", fix, specialist="fp-sprinkler", brief="Answer the objection to your screen.")
        told = fix.of("fp-sprinkler")[0]["user"]
        self.assertIn("Objections to your findings. Revise the finding if the objection is right.", told)
        self.assertIn("fa-releasing objects: The sequence carries 2 s to the solenoid.", told)
        self.assertEqual(len(third["replaced_or_withdrawn"]), 1)
        self.assertEqual(third["replaced_or_withdrawn"][0]["id"], wrong["id"])
        self.assertEqual(third["still_unsettled_on_the_record"]["objections"], [])
        self.assertEqual(third["still_unsettled_on_the_record"]["on_another_value_than_the_project_input"], [])
        current = [row["text"] for row in record.findings("job1")]
        self.assertEqual(current, ["Trip to water screens against the 30 s clock with the 2 s releasing time included"])
        closed = record.reviews("job1")[0]
        self.assertEqual(closed["status"], "resolved")
        self.assertIn("The finding was revised by fp-sprinkler", closed["resolution"])
        self.assertEqual(closed["resolved_by"], "fp-sprinkler")
        self.assertNotIn("Open objections", lead_status(record, "job1"))
        history = record.findings("job1", include_retired=True)
        self.assertEqual(len(history), 2, "the replaced finding is kept")

        # The block under the lead's reply says what passed between them, in the application's words.
        summary = team_summary({"delegations": [second, third]})
        self.assertIn("Between the specialists:", summary)
        self.assertIn("- fa-releasing objected to a finding by fp-sprinkler: The sequence carries 2 s", summary)
        self.assertIn("- fp-sprinkler revised a finding", summary)
        self.assertNotIn("still open", summary)

    def test_agreement_is_recorded_and_a_review_follows_the_rules(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.record import RecordError
        from fpfa.team import team_summary

        record = _record()
        _seed_inputs(record)
        self._first_pass(record)
        finding = _finding(record, "no releasing delay")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        with self.assertRaises(RecordError):
            fp.execute("review_finding", {"id": finding["id"], "position": "agree"})
        with self.assertRaises(RecordError):
            fa.execute("review_finding", {"id": finding["id"], "position": "object"})
        with self.assertRaises(RecordError):
            fa.execute("review_finding", {"id": finding["id"], "position": "maybe", "note": "x"})
        with self.assertRaises(RecordError):
            fa.execute("review_finding", {"id": "nope", "position": "agree"})
        first = fa.execute("review_finding", {"id": finding["id"], "position": "object", "note": "Leaves out 2 s."})
        self.assertEqual((first["position"], first["status"]), ("object", "open"))
        # The objector changes its mind: one row per reviewer per finding, and the objection is gone.
        again = fa.execute("review_finding", {"id": finding["id"], "position": "agree", "note": "The 0 s case is labelled an alternative."})
        self.assertEqual(again["id"], first["id"])
        self.assertEqual((again["position"], again["status"]), ("agree", "resolved"))
        self.assertEqual(len(record.reviews("job1")), 1)
        # Another specialist cannot replace or withdraw a finding it did not write. The lead can.
        with self.assertRaises(RecordError):
            fa.execute("record_finding", {"text": "x", "label": "PRACTICE", "replaces": finding["id"]})
        with self.assertRaises(RecordError):
            fa.execute("withdraw_finding", {"id": finding["id"], "reason": "wrong"})
        lead = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        self.assertTrue(lead.execute("withdraw_finding", {"id": finding["id"], "reason": "Superseded by the 2 s case."})["withdrawn"])
        self.assertEqual(record.findings("job1"), [])
        with self.assertRaises(RecordError):
            fa.execute("review_finding", {"id": finding["id"], "position": "agree"})
        summary = team_summary({"delegations": [{
            "specialist": "fa-releasing", "findings": [], "reviews": [
                {"position": "agree", "of": "fp-sprinkler"}, {"position": "agree", "of": "fp-sprinkler"}],
        }]})
        self.assertIn("- fa-releasing reviewed and agreed with 2 findings by fp-sprinkler", summary)

    def test_two_contributors_that_record_different_values_for_one_fact_are_shown_to_the_lead(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.team import _unsettled, lead_status

        record = _record()
        _seed_inputs(record)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        lead = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        fp.execute("record_fact", {"kind": "election", "key": "trim_family", "value": "El/El", "label": "PRACTICE"})
        same = fa.execute("record_fact", {"kind": "election", "key": "trim_family", "value": "El/El", "label": "PRACTICE"})
        self.assertIn("Already on the record with this value", same["note"])
        other = fa.execute("record_fact", {"kind": "election", "key": "trim_family", "value": "El/Pn", "label": "PRACTICE"})
        self.assertEqual([row["by"] for row in other["conflicts_with"]], ["fp-sprinkler"])
        block = lead_status(record, "job1")
        self.assertIn("Conflicting facts. Two contributors recorded different values for one key:", block)
        self.assertIn("election/trim_family: fp-sprinkler: El/El", block)
        self.assertEqual(len(_unsettled(record, "job1")["conflicting_facts"]), 1)
        # The lead settles it by recording the value that stands. One value is left.
        lead.execute("record_fact", {"kind": "election", "key": "trim_family", "value": "El/El", "label": "use best judgment"})
        self.assertEqual(_unsettled(record, "job1")["conflicting_facts"], [])
        self.assertNotIn("Conflicting facts", lead_status(record, "job1"))
        # A specialist cannot write a project input or label its own reading as the designer's.
        from fpfa.record import RecordError

        for args in ({"kind": "input", "key": "q_fill_gpm", "value": "750", "label": "PRACTICE"},
                     {"kind": "basis", "key": "insurer", "value": "none", "label": "OWNER"},
                     {"kind": "election", "key": "medium", "value": "air", "label": "GIVEN"}):
            with self.assertRaises(RecordError, msg=str(args)):
                fp.execute("record_fact", args)


class LeadToolTests(unittest.TestCase):
    def _team(self, record, create=None):
        from fpfa.team import TeamSession

        return TeamSession(REPO, record, "job1", create or Play({}))

    def _worked(self, record):
        """A screen on the sample inputs with a finding on it, as a specialist leaves them."""
        from fpfa.team import delegate

        create = Play({"fp-sprinkler": _screen_steps(record, t_release=2, text="Trip to water screens against the 30 s clock")})
        delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1.")
        return _finding(record, "Trip to water screens")

    def test_set_input_records_what_the_designer_said_and_lists_what_it_made_out_of_date(self):
        from fpfa import inputs
        from fpfa.record import RecordError
        from fpfa.team import lead_status

        record = _record()
        _seed_inputs(record)
        finding = self._worked(record)
        team = self._team(record)
        out = team.execute("set_input", {"name": "q_fill_gpm", "value": "750 gpm", "why": "the pump acceptance test"})
        self.assertEqual((out["was"], out["now"], out["changed"]), ("600 gpm", "750 gpm", True))
        stale = {(row["kind"], row["id"]) for row in out["out_of_date"]}
        self.assertIn(("finding", finding["id"]), stale)
        self.assertIn(("calc", _calc(record, "di_trip_to_water")["id"]), stale)
        self.assertNotIn(("calc", _calc(record, "zone_trapped_volume")["id"]), stale, "the volume did not use the fill flow")
        self.assertIn("must be brought up to date by the author before you quote them", out["note"])
        fact = next(row for row in record.facts("job1", inputs.INPUT_KIND) if row["key"] == "q_fill_gpm")
        self.assertEqual((fact["label"], fact["agent"]), ("GIVEN", "lead"))
        self.assertEqual(fact["source"], "designer, in chat: the pump acceptance test")
        self.assertEqual(inputs.decode(fact["value"]), 750.0)
        self.assertEqual(team.inputs_set, [{"name": "q_fill_gpm", "was": "600 gpm", "now": "750 gpm"}])
        block = lead_status(record, "job1")
        self.assertIn("Inputs changed after work was done on them:", block)
        self.assertIn("Out of date. Their basis changed. Do not quote them", block)
        self.assertIn(f"finding [{finding['id']}] by fp-sprinkler", block)

        # Saying the same value again changes nothing and makes nothing out of date.
        again = team.execute("set_input", {"name": "q_fill_gpm", "value": "750"})
        self.assertFalse(again["changed"])
        self.assertNotIn("out_of_date", again)
        self.assertEqual(len(team.inputs_set), 1)

        # A basis field, the pipe list, and what is refused.
        basis = team.execute("set_input", {"name": "nfpa_13", "value": "2022", "why": "the adopted code"})
        self.assertEqual((basis["was"], basis["now"]), ("2025", "2022"))
        pipes = team.execute("set_input", {"name": "segments", "segments": [
            {"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 950}]})
        self.assertTrue(pipes["changed"])
        self.assertIn("950", pipes["now"])
        for args in ({"name": "flow", "value": "1"}, {"name": "q_fill_gpm", "value": "fast"},
                     {"name": "area_increase", "value": "30%"}, {"name": "insurer", "value": ""},
                     {"name": "segments", "value": "900 ft of 1 in."}, {"name": "system_type", "value": "deluge"}):
            with self.assertRaises(RecordError, msg=str(args)):
                team.execute("set_input", args)

    def test_a_specialist_is_told_its_findings_went_out_of_date_and_brings_them_up_to_date(self):
        from fpfa.team import _unsettled, delegate

        record = _record()
        _seed_inputs(record)
        old = self._worked(record)
        self._team(record).execute("set_input", {"name": "t_release_s", "value": "5", "why": "the panel submittal"})

        def volume(_kwargs):
            return call(use("zone_trapped_volume", segments=SEGMENTS))

        def screen(_kwargs):
            gallons = _calc(record, "zone_trapped_volume", "fp-sprinkler")["outputs"]["zone_gal"]
            return call(use("di_trip_to_water", v_gal=gallons, q_fill_gpm=600, t_detect_s=8, t_release_s=5, basis="FM"))

        def replace(_kwargs):
            calc = [row for row in record.calcs("job1") if row["tool"] == "di_trip_to_water"][-1]
            return call(use("record_finding", text="Trip to water screens against the 30 s clock with 5 s releasing time",
                            label="calculated", supports=[calc["id"]], replaces=old["id"]))

        create = Play({"fp-sprinkler": [volume, screen, replace, say("Brought up to date.")]})
        out = delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Bring the screen up to date.")
        told = create.of("fp-sprinkler")[0]["user"]
        self.assertIn("Your findings and decisions whose basis changed. Run the calcs again on the current inputs", told)
        self.assertIn(f"- [{old['id']}] Trip to water screens against the 30 s clock", told)
        self.assertIn("t_release_s", told)
        self.assertIn("Out-of-date calculation records (an input changed after they ran; do not cite them):", told)
        self.assertEqual(out["still_unsettled_on_the_record"]["out_of_date"], [])
        self.assertEqual(_unsettled(record, "job1")["out_of_date"], [])
        self.assertEqual([row["text"] for row in record.findings("job1")],
                         ["Trip to water screens against the 30 s clock with 5 s releasing time"])
        # The volume replayed: same inputs, same code, so nothing was computed twice.
        self.assertEqual(_calc(record, "zone_trapped_volume")["replay_count"], 1)

    def test_answer_question_closes_what_the_designer_answered(self):
        from fpfa.record import RecordError
        from fpfa.team import lead_status

        record = _record()
        _seed_inputs(record)
        asked = record.open_question("job1", raised_by="fp-sprinkler", audience="designer",
                                     text="What is the trim volume from the valve sheet?")
        rfi = record.open_question("job1", raised_by="fa-releasing", text="Does the owner accept one detection zone?")
        block = lead_status(record, "job1")
        self.assertIn("Waiting on the designer:", block)
        self.assertIn(f"- [{asked['id']}] What is the trim volume from the valve sheet? (asked by fp-sprinkler)", block)
        self.assertIn("Open for the engineer of record: 1 question on the record.", block)
        team = self._team(record)
        out = team.execute("answer_question", {"id": asked["id"], "answer": "6.5 gallons, from the submittal."})
        self.assertEqual(out["status"], "answered")
        self.assertIn("set_input", out["note"])
        row = next(item for item in record.questions("job1") if item["id"] == asked["id"])
        self.assertEqual((row["status"], row["answer"], row["answered_by"]),
                         ("answered", "6.5 gallons, from the submittal.", "designer, in chat"))
        self.assertEqual(team.answered[0]["id"], asked["id"])
        self.assertNotIn("Waiting on the designer:", lead_status(record, "job1"))
        with self.assertRaises(RecordError):
            team.execute("answer_question", {"id": asked["id"], "answer": "again"})
        with self.assertRaises(RecordError):
            team.execute("answer_question", {"id": "nope", "answer": "x"})
        self.assertEqual(next(item for item in record.questions("job1") if item["id"] == rfi["id"])["status"], "open")

    def test_an_answer_given_on_the_panel_reaches_the_lead_once_at_its_next_turn(self):
        from fpfa.everyday import run_everyday
        from fpfa.team import lead_status

        record = _record()
        _seed_inputs(record)
        asked = record.open_question("job1", raised_by="fp-sprinkler", audience="designer", text="Trim volume?")
        late = record.open_question("job1", raised_by="fp-sprinkler", audience="designer", text="Fittings allowance?")
        relayed = record.open_question("job1", raised_by="fa-releasing", audience="designer", text="One detection zone?")
        record.answer_question("job1", asked["id"], answer="6.5 gal", by="designer")
        block = lead_status(record, "job1")
        self.assertIn("The designer answered these on the panel. You have not acted on them yet. Act on each answer:", block)
        self.assertIn(f"- [{asked['id']}] Trim volume? Answer: 6.5 gal", block)

        # The designer answers a second question while the turn that read the first is still running.
        def mid_turn(_kwargs):
            record.answer_question("job1", late["id"], answer="5 percent", by="designer")
            return call(use("answer_question", id=relayed["id"], answer="Yes, one zone."))

        first = Play({"lead": [mid_turn, say("Noted the trim volume.")]})
        run_everyday(REPO, first, "Go on.", record=record, project_id="job1")
        self.assertIn("Trim volume? Answer: 6.5 gal", first.of("lead")[0]["user"])
        second = Play({"lead": [say("Noted the allowance.")]})
        run_everyday(REPO, second, "And now?", record=record, project_id="job1")
        opening = second.of("lead")[0]["user"]
        # The first answer was read by the first turn, so it is not news. The one given mid-turn is.
        self.assertNotIn("Trim volume? Answer", opening)
        self.assertIn(f"- [{late['id']}] Fittings allowance? Answer: 5 percent", opening)
        # An answer the lead itself passed on from the chat is not reported back to it as news.
        self.assertNotIn("One detection zone? Answer", opening)
        third = Play({"lead": [say("Nothing new.")]})
        run_everyday(REPO, third, "Anything else?", record=record, project_id="job1")
        self.assertNotIn("The designer answered these", third.of("lead")[0]["user"])

    def test_set_plan_is_what_the_panel_and_the_next_turn_show(self):
        from fpfa import status
        from fpfa.record import RecordError
        from fpfa.team import lead_status

        record = _record()
        _seed_inputs(record)
        self.assertIsNone(status.latest_plan(record.snapshot("job1")))
        self.assertIn("Plan: none set on this job yet.", lead_status(record, "job1"))
        team = self._team(record)
        out = team.execute("set_plan", {"objective": "Design basis for zone DH-1", "steps": [
            {"title": "Volume and delivery screen", "owner": "fp-sprinkler", "status": "done"},
            {"title": "Releasing sequence", "owner": "fa-releasing", "status": "doing"},
            {"title": "Trace check", "owner": "checker"},
        ]})
        self.assertEqual(out, {"objective": "Design basis for zone DH-1", "steps": 3, "done": 1})
        plan = status.latest_plan(record.snapshot("job1"))
        self.assertEqual(plan["objective"], "Design basis for zone DH-1")
        self.assertEqual([step["status"] for step in plan["steps"]], ["done", "doing", "todo"])
        block = lead_status(record, "job1")
        self.assertIn("Plan. Objective: Design basis for zone DH-1", block)
        self.assertIn("- ✓ Volume and delivery screen (fp-sprinkler): done", block)
        self.assertIn("- ○ Trace check (checker): todo", block)
        # A later plan replaces it. It survives however many events follow.
        team.execute("set_plan", {"objective": "Design basis for zone DH-1", "steps": [{"title": "Done", "status": "done"}]})
        for index in range(260):
            record.log_event("job1", "note", {"n": index})
        self.assertEqual([step["title"] for step in status.latest_plan(record.snapshot("job1"))["steps"]], ["Done"])
        for args in ({"objective": "", "steps": [{"title": "x"}]}, {"objective": "x", "steps": []},
                     {"objective": "x", "steps": [{"title": ""}]}, {"objective": "x", "steps": [{"title": "y", "status": "soon"}]}):
            with self.assertRaises(RecordError, msg=str(args)):
                team.execute("set_plan", args)

    def test_the_lead_ends_an_objection_it_does_not_send_back(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.record import RecordError
        from fpfa.team import lead_status, team_summary

        record = _record()
        _seed_inputs(record)
        finding = self._worked(record)
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        draft = ToolSession(REPO, record=record, project_id="job1", agent="spec-draft")
        first = fa.execute("review_finding", {"id": finding["id"], "position": "object", "note": "The clock should start at the second detector."})
        team = self._team(record)
        for args in ({"id": first["id"], "outcome": "upheld", "reason": "x"}, {"id": first["id"], "outcome": "stands", "reason": ""},
                     {"id": "nope", "outcome": "stands", "reason": "x"}):
            with self.assertRaises(RecordError, msg=str(args)):
                team.execute("resolve_disagreement", args)

        # stands: a decision on the record with the reason, and the objection closed against it.
        out = team.execute("resolve_disagreement", {"id": first["id"], "outcome": "stands",
                                                    "reason": "The designer's inputs put detection at the first signal."})
        decision = next(row for row in record.decisions("job1") if row["id"] == out["decision_id"])
        self.assertEqual((decision["decided_by"], decision["label"], decision["supports"]), ("lead", "use best judgment", [finding["id"]]))
        self.assertIn("is not upheld. The finding stands.", decision["text"])
        review = record.reviews("job1")[0]
        self.assertEqual((review["status"], review["resolved_by"]), ("resolved", "lead"))
        self.assertIn(f"[decision {decision['id']}]", review["resolution"])
        self.assertNotIn("Open objections", lead_status(record, "job1"))

        # escalated: a question for the person who can decide, and the objection stays visible as unresolved.
        second = draft.execute("review_finding", {"id": finding["id"], "position": "object", "note": "The owner standard may ask for 25 s."})
        third = fa.execute("review_finding", {"id": finding["id"], "position": "object", "note": "Still think the clock start is wrong."})
        with self.assertRaises(RecordError) as caught:
            team.execute("resolve_disagreement", {"id": finding["id"], "outcome": "escalated", "reason": "x"})
        self.assertIn(second["id"], str(caught.exception))
        self.assertIn(third["id"], str(caught.exception))
        sent = team.execute("resolve_disagreement", {"id": second["id"], "outcome": "escalated", "to": "engineer",
                                                     "reason": "Only the owner standard settles the clock."})
        self.assertEqual(sent["to"], "engineer")
        question = next(row for row in record.questions("job1") if row["id"] == sent["question_id"])
        self.assertEqual((question["audience"], question["raised_by"], question["status"]), ("engineer", "lead", "open"))
        self.assertIn("The team could not settle this.", question["text"])
        self.assertIn("The owner standard may ask for 25 s.", question["text"])
        block = lead_status(record, "job1")
        self.assertIn(f"review [{second['id']}] (escalated, waiting on an answer): spec-draft objects", block)
        self.assertIn(f"review [{third['id']}]: fa-releasing objects", block)
        self.assertEqual([item["outcome"] for item in team.resolved], ["stands", "escalated"])
        summary = team_summary({"resolved": team.resolved})
        self.assertIn("- the lead settled fa-releasing's objection: the finding stands", summary)
        self.assertIn("- the lead escalated spec-draft's objection as a question", summary)
        # One objection on a finding can be named by the finding's id.
        team.execute("resolve_disagreement", {"id": third["id"], "outcome": "escalated", "to": "designer", "reason": "Your call."})
        self.assertEqual(record.questions("job1")[-1]["audience"], "designer")


class BriefAndStatusTests(unittest.TestCase):
    def test_a_specialist_is_briefed_with_the_inputs_the_whole_team_works_from(self):
        from fpfa import inputs
        from fpfa.team import SPECIALIST_PARAGRAPH, specialist_request, specialist_system

        record = _record()
        _seed_inputs(record)
        text = specialist_request(record, "job1", "fp-sprinkler", "Screen DH-1.", {"zone": "DH-1"}, [])
        self.assertTrue(text.startswith("You are the specialist fp-sprinkler on this job. The lead delegated this task:\n\nScreen DH-1."))
        self.assertIn("Project inputs. The whole team works from these. Cite an input's id when a finding rests on it:", text)
        fill = next(row for row in record.facts("job1", inputs.INPUT_KIND) if row["key"] == "q_fill_gpm")
        self.assertIn(f"- [{fill['id']}] q_fill_gpm: 600 gpm", text)
        self.assertIn("- Blank on the form: fittings_percent, trim_gal", text)
        self.assertNotIn("What on the record needs you:", text, "nothing needs it on a job no one has worked on")
        empty = _record()
        empty.ensure_project("job1")
        bare = specialist_request(empty, "job1", "fp-sprinkler", "Screen DH-1.", None, [])
        self.assertIn("Project inputs: none on the record yet. Ask the lead for what you need; do not invent inputs.", bare)
        # A starting value the designer never confirmed is marked as one.
        loose = _record()
        loose.ensure_project("job1")
        loose.sync_form("job1", inputs.INPUT_KIND, {"q_fill_gpm": inputs.encode("q_fill_gpm", 600)},
                        sources={"q_fill_gpm": inputs.source_text(inputs.SOURCE_DEFAULT)})
        self.assertIn("q_fill_gpm: 600 gpm (starting value, not confirmed by the designer)",
                      specialist_request(loose, "job1", "fp-sprinkler", "Screen.", None, []))
        system = specialist_system(REPO, "fp-sprinkler")
        self.assertIn(SPECIALIST_PARAGRAPH, system)
        self.assertIn("The other specialists on this team: fa-releasing, spec-draft.", system)
        for phrase in ("ask that specialist with consult", "review_finding", "find it with search_corpus",
                       "do not put your own value in its place"):
            self.assertIn(phrase, SPECIALIST_PARAGRAPH)

    def test_list_specialists_says_what_each_owns_needs_and_reviews(self):
        from fpfa.team import list_specialists, team_notes

        rows = {row["slug"]: row for row in list_specialists(REPO)}
        self.assertEqual(sorted(rows), ["fa-releasing", "fp-sprinkler", "spec-draft"])
        for slug in ("fp-sprinkler", "fa-releasing"):
            notes = rows[slug]["works_with_the_team"]
            for word in ("you own", "do not own", "review", "project inputs", "consult"):
                self.assertIn(word, notes.lower(), f"{slug} {word}")
        self.assertIn("releasing specialist", rows["fp-sprinkler"]["works_with_the_team"])
        self.assertIn("sprinkler specialist", rows["fa-releasing"]["works_with_the_team"])
        self.assertEqual(team_notes("# A role\n\nNo team section."), "")
        self.assertEqual(team_notes("## Working with the team\n\nOwns x.\n\n## Next\n\nOther."), "Owns x.")

    def test_a_specialist_that_runs_out_of_rounds_is_reported_as_unfinished(self):
        from fpfa.team import delegate, lead_status

        record = _record()
        _seed_inputs(record)
        create = Play({"fp-sprinkler": [call(use("zone_trapped_volume", segments=SEGMENTS)), call(use("read_record"))]})
        out = delegate(REPO, record, "job1", create, specialist="fp-sprinkler", brief="Screen DH-1.", max_rounds=2)
        self.assertIs(out["complete"], False)
        self.assertIn("did not finish", out["note"])
        self.assertIn("Delegate to it again to finish; recorded calcs replay.", out["note"])
        self.assertEqual([row["tool"] for row in out["calc_records"]], ["zone_trapped_volume"], "what it recorded is kept")
        self.assertEqual(record.agents("job1")[0]["status"], "interrupted")
        self.assertIn("Interrupted before it finished: Sprinkler specialist.", lead_status(record, "job1"))

    def test_the_lead_role_is_content_and_says_how_the_team_is_run(self):
        from fpfa.everyday import assemble_system
        from fpfa.roles_loader import read_role
        from fpfa.team import TEAM_PARAGRAPH, has_lead_role

        self.assertTrue(has_lead_role(REPO))
        role = read_role(REPO, "lead")
        for phrase in ("set_plan", "set_input", "delegate", "request_check", "resolve_disagreement", "answer_question",
                       "trace check", "ASSUMED", "use best judgment"):
            self.assertIn(phrase, role)
        # The role names no specialist's method and no job. The team it leads is listed by the application.
        system = assemble_system(REPO, "mixed", team=True)
        self.assertTrue(system.startswith(role.strip()))
        self.assertIn("Specialists on this team. Delegate to them with delegate.", system)
        self.assertIn("The checker is qa-specialist. request_check runs it. You do not delegate to it.", system)
        self.assertIn(TEAM_PARAGRAPH, system)
        self.assertEqual(system, assemble_system(REPO, "mixed", team=True), "the cached system text is the same bytes every turn")
        # Without the team (no record on the turn) the everyday shell is used, as before.
        plain = assemble_system(REPO, "mixed")
        self.assertIn("You are the design assistant inside a desktop application", plain)
        self.assertNotIn("# Team lead", plain)

    def test_a_pack_without_a_lead_role_falls_back_to_the_shell_with_the_team_paragraph(self):
        import shutil
        import tempfile

        from fpfa.everyday import assemble_system
        from fpfa.team import TEAM_PARAGRAPH, TEAM_SCHEMAS, lead_schemas

        root = Path(tempfile.mkdtemp(prefix="fpfa-pack-")) / "pack"
        for folder in ("roles", "modes", "skills", "specs"):
            shutil.copytree(REPO / folder, root / folder)
        shutil.rmtree(root / "roles" / "lead")
        system = assemble_system(root, "mixed", team=True)
        self.assertIn("You are the design assistant inside a desktop application", system)
        self.assertIn(TEAM_PARAGRAPH, system)
        self.assertNotIn("# Team lead", system)
        self.assertIs(lead_schemas(root), TEAM_SCHEMAS)


class LeadTurnProtocolTests(unittest.TestCase):
    def test_one_lead_turn_runs_the_team_and_reports_what_it_did(self):
        """Plan, record what the designer said, delegate, reconcile, check, answer: one turn, on the record."""
        from fpfa.everyday import run_everyday
        from fpfa.team import team_summary

        record = _record()
        _seed_inputs(record)
        plan = use("set_plan", objective="Water delivery for DH-1 at the tested fill flow", steps=[
            {"title": "Delivery screen", "owner": "fp-sprinkler", "status": "doing"},
            {"title": "Releasing time", "owner": "fa-releasing"},
            {"title": "Trace check", "owner": "checker"}])
        given = use("set_input", name="q_fill_gpm", value="600", why="confirmed in chat")
        to_fp = use("delegate", specialist="fp-sprinkler", brief="Screen DH-1 water delivery. Ask fa-releasing for the releasing time.")
        check = use("request_check")
        ask = use("consult", specialist="fa-releasing", question="What releasing time does the sequence carry?")

        def checker(kwargs):
            count = len([line for line in kwargs["messages"][0]["content"].split("sources.md")[0].splitlines() if line[:1].isdigit()])
            return say("\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, count + 1)))

        create = Play({
            "lead": [call(plan, given), call(to_fp), call(check), say("Screen is on the record. One note is the releasing specialist's.")],
            "fp-sprinkler": [call(ask)] + _screen_steps(record, t_release=2, text="Trip to water screens against the 30 s clock"),
            "fa-releasing": [call(use("record_finding", text="The sequence carries 2 s to the solenoid", label="PRACTICE")),
                             say("2 s.")],
            "checker": [checker],
        })
        out = run_everyday(REPO, create, "Can DH-1 meet the delivery time at the fill flow we tested?", record=record, project_id="job1")
        self.assertEqual(out["text"], "Screen is on the record. One note is the releasing specialist's.")
        self.assertEqual([item["specialist"] for item in out["delegations"]], ["fp-sprinkler"])
        self.assertEqual(len(out["delegations"][0]["consults"]), 1)
        self.assertEqual(len(out["checks"]), 1)
        self.assertEqual(out["inputs_set"], [], "the same value again is not a change")
        self.assertGreaterEqual(out["seconds"], 0)
        # Lead 4 rounds, the specialist 5, the consult 2. The check closes on its own event.
        self.assertEqual(out["lead_usage"]["rounds"], 4)
        self.assertEqual(out["usage"]["rounds"], 4 + 5 + 2)
        turn = record.latest_event("job1", "turn")["payload"]
        self.assertEqual((turn["delegations"], turn["checks"], turn["cancelled"]), (1, 1, False))
        self.assertIn("seconds", turn)
        # The check judged both findings. The one that rests on nothing but its author's word is not supported.
        verdicts = {row["agent"]: row["status"] for row in record.findings("job1")}
        self.assertEqual(verdicts, {"fa-releasing": "Source not found", "fp-sprinkler": "Supported"})
        summary = team_summary(out)
        self.assertIn("- fp-sprinkler: 1 finding, 2 calc records", summary)
        self.assertIn("- fp-sprinkler asked fa-releasing: What releasing time does the sequence carry?", summary)
        self.assertIn("- trace check: 1 of 2 findings consistent with what they cite", summary)
        # The next turn opens with where the job stands.
        again = Play({"lead": [say("Nothing changed.")]})
        run_everyday(REPO, again, "Where are we?", record=record, project_id="job1")
        opening = again.of("lead")[0]["user"]
        self.assertIn("Plan. Objective: Water delivery for DH-1 at the tested fill flow", opening)
        self.assertIn("Contributors so far: fa-releasing (done, 1 finding); fp-sprinkler (done, 1 finding)", opening)
        self.assertIn("Trace check: 1 of 2 findings are consistent with the rows they cite", opening)
        self.assertTrue(opening.endswith("Where are we?"))

    def test_a_refused_team_tool_comes_back_to_the_lead_as_an_error_it_can_read(self):
        from fpfa.everyday import run_everyday

        record = _record()
        _seed_inputs(record)
        bad = use("set_input", name="area_increase", value="30%")
        create = Play({"lead": [call(bad), say("I will ask for the fraction.")]})
        run_everyday(REPO, create, "Area increase is 30%.", record=record, project_id="job1")
        result = create.result(bad)
        self.assertTrue(result["is_error"])
        self.assertIn("a fraction: 0.30 is a 30 percent increase", result["content"])


if __name__ == "__main__":
    unittest.main()
