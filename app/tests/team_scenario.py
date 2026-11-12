"""One job carried through the whole workflow, with every model call played from a script.

SIMULATED. No model is called. Each "agent" below is a list of moves written
in advance: the tools it calls and the words it says. The application's own
code does everything else for real: it builds each agent's message, runs the
calc kernels, writes the record, tracks what an input change leaves out of
date, runs the trace check's rules, audits the reply's figures, and writes
the export.

So this shows that the application can carry such a job, and what the
designer sees when it does. It does not show that a live model, handed the
same request, will plan, ask, object, and revise the way the script does.
docs/live-evaluation.md is the path for finding that out.

The request names no specialist and no sequence. The job then goes:

  turn 1  the lead plans and delegates; the sprinkler specialist asks the
          releasing specialist a question mid-task; the releasing specialist
          objects to a finding; the sprinkler specialist revises; trace check.
  (the window is closed and opened again)
  turn 2  the designer answers a question on the panel and says in chat that
          the fill flow is different from the form's; the lead records both;
          the first attempt to bring the work up to date fails mid-way; the
          second replays what was already computed and finishes; trace check.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[2]

REQUEST_ONE = (
    "We're laying out the preaction zone for data hall 1. Can it meet the insurer's water delivery time, "
    "and what releasing sequence goes with it? I need a design basis I can hand to the engineer."
)
REQUEST_TWO = (
    "I answered the trim question on the panel. One more thing: the pump test gave us 750 gpm at the riser, "
    "not the 600 on the form. Does that change the answer?"
)
ANSWER_TRIM = "6.5"
SEGMENTS = [
    {"role": "branch", "nps": "1", "schedule": "sch40", "length_ft": 900},
    {"role": "branch", "nps": "2", "schedule": "sch40", "length_ft": 220},
    {"role": "cross", "nps": "4", "schedule": "sch10", "length_ft": 160},
    {"role": "main", "nps": "6", "schedule": "sch10", "length_ft": 48},
]
_ids = itertools.count(1)
_MARKERS = (("fp-sprinkler", "# Sprinkler specialist"), ("fa-releasing", "# Releasing specialist"),
            ("spec-draft", "# Draft narrative"))


class Block:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, exclude_none=True):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def use(tool: str, /, **args) -> Block:
    return Block(type="tool_use", id=f"s{next(_ids)}", name=tool, input=args)


def _usage(fresh: int, out: int, read: int = 0, written: int = 0):
    return SimpleNamespace(input_tokens=fresh, output_tokens=out, cache_read_input_tokens=read,
                           cache_creation_input_tokens=written)


def call(*blocks, usage=None):
    return SimpleNamespace(stop_reason="tool_use", content=list(blocks), usage=usage or _usage(400, 120, read=9000))


def say(text: str, usage=None):
    return SimpleNamespace(stop_reason="end_turn", content=[Block(type="text", text=text)],
                           usage=usage or _usage(300, 260, read=9000))


def system_text(kwargs) -> str:
    system = kwargs.get("system")
    if isinstance(system, str):
        return system
    return "".join(block.get("text", "") for block in system or [])


class Players:
    """create() for the whole team: one script per agent, played in order. A step may read the record."""

    def __init__(self, scripts: dict):
        self.scripts = {key: list(value) for key, value in scripts.items()}
        self.calls: list[dict] = []

    def kind(self, kwargs) -> str:
        system = system_text(kwargs)
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
        self.calls.append({"kind": kind, "user": first if isinstance(first, str) else "", "system": system_text(kwargs),
                           "tools": [tool["name"] for tool in kwargs.get("tools") or []]})
        script = self.scripts.get(kind)
        if not script:
            raise AssertionError(f"no move left for a {kind} turn")
        step = script.pop(0)
        return step(kwargs) if callable(step) else step

    def of(self, kind: str) -> list[dict]:
        return [item for item in self.calls if item["kind"] == kind]

    def left(self) -> dict:
        return {kind: len(steps) for kind, steps in self.scripts.items() if steps}


def client_for(players):
    class Client:
        def __init__(self, _key):
            pass

        def create(self, **kwargs):
            return players(**kwargs)

    return Client


def _numbered(kwargs) -> list[tuple[int, str]]:
    claims = kwargs["messages"][0]["content"].split("sources.md")[0]
    found = []
    for line in claims.splitlines():
        head, _, rest = line.partition(". ")
        if head.isdigit():
            found.append((int(head), rest))
    return found


def discerning(kwargs):
    """A checker that reads: Supported, except a claim that the trim screen elects a family it does not.

    The stand-in for a checker that works, for the evaluation's planted
    claim that no rule of the application covers. It shows the runner reads
    such a verdict correctly. It shows nothing about the live checker.
    """
    lines = []
    for number, text in _numbered(kwargs):
        wrong = "The trim screen elects the" in text
        lines.append(f'{number}. {"Not supported" if wrong else "Supported"}. Cite: "row"')
    return say("\n".join(lines), usage=_usage(2600, 180))


def supported_by_default(kwargs):
    """The checker's part: Supported for every claim. The application's own rules decide the rest."""
    claims = kwargs["messages"][0]["content"].split("sources.md")[0]
    count = len([line for line in claims.splitlines() if line[:1].isdigit()])
    return say("\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, count + 1)), usage=_usage(2600, 180))


class Lookup:
    """Reads ids off the record, so a scripted move can cite what an earlier move wrote."""

    def __init__(self, record, project_id: str):
        self.record = record
        self.project_id = project_id

    def calc(self, tool: str, agent: str = "fp-sprinkler", **where) -> dict:
        """The newest record of a tool. agent "" takes anyone's: a call with the same inputs as an
        earlier one replays that row, which keeps the name of whoever ran it first."""
        rows = [row for row in self.record.calcs(self.project_id) if row["tool"] == tool
                and (not agent or row["agent"] == agent)
                and all(row["inputs"].get(key) == value for key, value in where.items())]
        if not rows:
            raise AssertionError(f"no {tool} calc by {agent or 'anyone'} with {where}")
        return rows[-1]

    def finding(self, needle: str) -> dict:
        for row in self.record.findings(self.project_id):
            if needle in row["text"]:
                return row
        raise AssertionError(f"no current finding with {needle!r}")

    def given(self, name: str) -> dict:
        return self.record.givens(self.project_id)[name]

    def question(self, needle: str) -> dict:
        for row in self.record.questions(self.project_id):
            if needle in row["text"]:
                return row
        raise AssertionError(f"no question with {needle!r}")

    def objection(self) -> dict:
        return next(row for row in self.record.reviews(self.project_id)
                    if row["position"] == "object" and row["status"] == "open")


def turn_one(record, project_id: str) -> Players:
    at = Lookup(record, project_id)

    def fp_volume(_k):
        return call(use("elect_di_trim", system_type="di", prime_held_by="nc_solenoid", supervisory_psi=15,
                        medium="nitrogen", insurer="FM"),
                    use("zone_trapped_volume", segments=SEGMENTS, length_basis="center_to_center"))

    def fp_ask(_k):
        return call(
            use("record_finding", text="Trim family is El/El, provisional. A normally closed solenoid holds the prime",
                label="calculated", supports=[at.calc("elect_di_trim")["id"]]),
            use("consult", specialist="fa-releasing",
                question="What releasing time does the sequence carry from the first detection signal to the solenoid? "
                         "I add it to the fill time in the delivery screen.",
                context="The form holds 8 s detection and 2 s release. Trim is El/El."))

    def fa_answer(_k):
        return call(use("record_finding",
                        text="The 2 s releasing time is the form's value. Nothing on the record gives it a basis",
                        label="ASSUMED", supports=[at.given("t_release_s")["id"]]))

    def fp_screen(_k):
        gallons = at.calc("zone_trapped_volume")["outputs"]["zone_gal"]
        return call(use("di_trip_to_water", v_gal=gallons, q_fill_gpm=600, t_detect_s=8, t_release_s=2, t_exhaust_s=0, basis="FM"))

    def fp_record(_k):
        trip = at.calc("di_trip_to_water")
        volume = at.calc("zone_trapped_volume")
        return call(
            use("record_evidence", document="NFPA 13", edition="2025", section="8.3.2.3.1.1",
                note="A double-interlock zone at or under 500 gal carries no delivery-time proof"),
            use("record_finding", text=f"Zone total is {volume['outputs']['zone_gal']:.1f} gal with the trim volume "
                                       "ASSUMED at 5 gal", label="calculated", supports=[volume["id"]]),
            use("record_finding", text=f"The FM 30 s screen is missed: t_total is {trip['outputs']['t_total_s']:.1f} s "
                                       "at 600 gpm", label="calculated", supports=[trip["id"]]),
            use("open_question", text="What is the trim volume on the elected valve's data sheet?", to="designer"))

    def fa_sequence(_k):
        return call(use("releasing_truth_table", manual_station=True, insurer="FM"))

    def fa_record(_k):
        return call(
            use("record_finding",
                text="Release is the detection leg AND P, the pressure drop from sprinkler operation, and not isolated. "
                     "Low air is supervisory only", label="calculated",
                supports=[at.calc("releasing_truth_table", "")["id"], at.finding("Trim family is El/El")["id"]]),
            use("review_finding", id=at.finding("Trim family is El/El")["id"], position="agree",
                note="The sequence is written for El/El."),
            use("review_finding", id=at.finding("The FM 30 s screen is missed")["id"], position="object",
                note="The screen adds 8 s and 2 s that are the form's values with no stated basis. Say they are ASSUMED "
                     "and cite the two inputs, or get the releasing panel's output delay."),
            use("open_question", text="Does the owner accept one detection zone for the detection leg?"))

    def fp_revise(_k):
        trip = at.calc("di_trip_to_water")
        return call(
            use("record_finding",
                text=f"The FM 30 s screen is missed: t_total is {trip['outputs']['t_total_s']:.1f} s at 600 gpm. "
                     "The 8 s detection and 2 s releasing allowances are the form's values and are ASSUMED",
                label="calculated", replaces=at.finding("The FM 30 s screen is missed")["id"],
                supports=[trip["id"], at.given("t_detect_s")["id"], at.given("t_release_s")["id"]]),
            use("review_finding", id=at.finding("Release is the detection leg AND P")["id"], position="agree"))

    def lead_reply(_k):
        trip = at.calc("di_trip_to_water")["outputs"]
        gallons = at.calc("zone_trapped_volume")["outputs"]["zone_gal"]
        return say(
            "## Where DH-1 stands\n\n"
            "The sprinkler specialist sized the zone and screened its delivery. The releasing specialist wrote the "
            "sequence and reviewed the screen.\n\n"
            f"- Zone total is {gallons:.1f} gal (calculated), with the trim volume ASSUMED at 5 gal.\n"
            f"- The insurer's 30 s screen is missed: t_total is {trip['t_total_s']:.1f} s at 600 gpm (calculated). "
            "It is an optimistic screen, not a listed calculation.\n"
            "- Release is the detection leg AND P, and not isolated. Low air is supervisory only.\n\n"
            "The releasing specialist objected that the 8 s and 2 s in the screen have no stated basis. The sprinkler "
            "specialist revised the finding to say they are ASSUMED. That is settled.\n\n"
            "I need one thing from you:\n\n1. The trim volume on the elected valve's data sheet.\n\n"
            "The trace check found the findings consistent with what they cite. The standards were not opened, and "
            "the engineer of record reviews this before it is issued.",
            usage=_usage(500, 420, read=23000))

    plan = [{"title": "Volume, delivery screen, and trim", "owner": "fp-sprinkler", "status": "doing"},
            {"title": "Releasing sequence and review of the screen", "owner": "fa-releasing", "status": "todo"},
            {"title": "Settle what the two disagree on", "owner": "lead", "status": "todo"},
            {"title": "Trace check", "owner": "checker", "status": "todo"}]
    done = [dict(step, status="done") for step in plan]
    return Players({
        "lead": [
            call(use("list_specialists"),
                 use("set_plan", objective="Delivery time and releasing sequence for the data hall 1 preaction zone", steps=plan),
                 usage=_usage(22000, 300, written=22000)),
            call(use("delegate", specialist="fp-sprinkler",
                     brief="Size the data hall 1 preaction zone and screen its water delivery against the insurer's time. "
                           "Record the trim family first; the releasing specialist needs it. Ask the releasing "
                           "specialist for anything about detection or release you need.")),
            call(use("delegate", specialist="fa-releasing",
                     brief="Write the releasing sequence for the zone on the trim family the sprinkler specialist recorded. "
                           "Review the sprinkler findings that rest on a detection or a release time.")),
            lambda _k: call(use("delegate", specialist="fp-sprinkler",
                                brief="The releasing specialist objects to your screen finding. Revise it if the objection "
                                      "is right, and review the releasing sequence where it states your trim family.")),
            call(use("request_check")),
            call(use("set_plan", objective="Delivery time and releasing sequence for the data hall 1 preaction zone", steps=done)),
            lead_reply,
        ],
        "fp-sprinkler": [
            call(use("read_skill", slug="dry-preaction-water-delivery-screen"), usage=_usage(5200, 90, written=5200)),
            fp_volume, fp_ask, fp_screen, fp_record,
            say("Sized and screened. The 30 s insurer screen is missed. Trim is El/El, provisional. One question for the designer."),
            fp_revise,
            say("Revised the screen finding to carry the two allowances as ASSUMED. I agree with the releasing sequence."),
        ],
        "fa-releasing": [
            # It reads its method before it answers, so what it then records can be traced to what it read.
            call(use("read_skill", slug="fa-double-interlock-releasing-cause-and-effect"), usage=_usage(4800, 80, written=4800)),
            fa_answer,
            say("Nothing on the record gives the releasing time a basis. Use the form's 2 s and carry it as ASSUMED."),
            fa_sequence, fa_record,
            say("Sequence written for El/El. I object to the screen: its 8 s and 2 s are not stated as ASSUMED."),
        ],
        "checker": [supported_by_default],
    })


def turn_two(record, project_id: str) -> Players:
    at = Lookup(record, project_id)

    def lead_inputs(_k):
        # The designer answered the trim question on the panel before this turn, so the lead acts on the
        # answer its status block showed it, and records the fill flow the designer just stated.
        return call(
            use("set_input", name="trim_gal", value=ANSWER_TRIM, why="answered on the Team panel"),
            use("set_input", name="q_fill_gpm", value="750 gpm", why="the pump test at the riser"))

    def fp_volume(_k):
        return call(use("zone_trapped_volume", segments=SEGMENTS, length_basis="center_to_center", trim_gal=6.5))

    def dropped(_k):
        raise ConnectionError("the connection dropped")

    def fp_screen(_k):
        gallons = at.calc("zone_trapped_volume", trim_gal=6.5)["outputs"]["zone_gal"]
        return call(use("di_trip_to_water", v_gal=gallons, q_fill_gpm=750, t_detect_s=8, t_release_s=2, t_exhaust_s=0, basis="FM"))

    def fp_replace(_k):
        volume = at.calc("zone_trapped_volume", trim_gal=6.5)
        trip = at.calc("di_trip_to_water", q_fill_gpm=750)
        return call(
            use("record_finding", text=f"Zone total is {volume['outputs']['zone_gal']:.1f} gal with the 6.5 gal trim volume "
                                       "the designer gave", label="calculated",
                supports=[volume["id"], at.given("trim_gal")["id"]], replaces=at.finding("Zone total is")["id"]),
            use("record_finding",
                text=f"The FM 30 s screen is still missed: t_total is {trip['outputs']['t_total_s']:.1f} s at 750 gpm. "
                     "The 8 s detection and 2 s releasing allowances are the form's values and are ASSUMED",
                label="calculated", replaces=at.finding("The FM 30 s screen is missed")["id"],
                supports=[trip["id"], at.given("t_detect_s")["id"], at.given("t_release_s")["id"]]))

    def fa_review(_k):
        return call(use("review_finding", id=at.finding("still missed")["id"], position="agree",
                        note="The allowances are carried as ASSUMED."))

    def lead_reply(_k):
        trip = at.calc("di_trip_to_water", q_fill_gpm=750)["outputs"]
        gallons = at.calc("zone_trapped_volume", trim_gal=6.5)["outputs"]["zone_gal"]
        return say(
            "## What 750 gpm changes\n\n"
            "I recorded the 750 gpm fill flow and the 6.5 gal trim volume. The sprinkler specialist ran the zone again "
            "on both and replaced its two findings. The releasing specialist reviewed the new screen and agrees.\n\n"
            f"- Zone total is {gallons:.1f} gal (calculated) on the trim volume you gave.\n"
            f"- The insurer's 30 s screen is still missed: t_total is {trip['t_total_s']:.1f} s at 750 gpm (calculated). "
            "The releasing sequence does not change.\n\n"
            "The first attempt to bring the work up to date failed part-way when the connection dropped. I ran it again; "
            "what had been computed was replayed, not computed twice.\n\n"
            "The tables on the Results tab are still the earlier run. Run the zone again before you use them.\n\n"
            "The trace check ran again on the new findings. The standards were not opened.",
            usage=_usage(500, 380, read=24000))

    brief = ("The designer gave a fill flow of 750 gpm and a trim volume of 6.5 gal. Your volume and screen findings are "
             "out of date. Run them again on the current inputs and replace them.")
    return Players({
        "lead": [
            lead_inputs,
            call(use("delegate", specialist="fp-sprinkler", brief=brief)),
            call(use("delegate", specialist="fp-sprinkler", brief=brief + " The first attempt was cut off; finish it.")),
            call(use("delegate", specialist="fa-releasing",
                     brief="The delivery screen was revised for a new fill flow. Review the revised finding.")),
            call(use("request_check")),
            lead_reply,
        ],
        "fp-sprinkler": [
            fp_volume, dropped,
            fp_volume, fp_screen, fp_replace,
            say("Both findings are up to date on 750 gpm and the 6.5 gal trim volume. The screen is still missed."),
        ],
        "fa-releasing": [fa_review, say("I agree with the revised screen.")],
        "checker": [supported_by_default],
    })
