"""Run the evaluation path against the live model and write down what happened.

    python -m fpfa.live_eval --out <folder> [--job dh1|dh2] [--max-usd 25] [--effort high] [--steps request,...]
    Cynosure.exe --live-eval <folder>            (the packaged app; same options)

This drives the same Desk the window runs, with no window, through the steps
in docs/live-evaluation.md: a plain request that names no specialist, a
relaunch, the designer's answers, an input that changes, a turn cancelled
part-way and picked up again, wrong claims planted for the trace check, and
the export. After each step it reads the project record and writes what it
found: which checks the run met, which it did not, and which it could not
observe. It writes the thread, the status, the usage report, the Design
Basis, and the record beside the report so a person can read them.

What it is for. A scripted test can show that the application carries such
a job. Only a live run shows whether the model plans, asks, objects, and
revises when it is handed a plain objective. The checks here are the things
a program can tell from the record. They do not judge whether the
engineering is right or the reply is useful; the report lists what a person
has to read to decide that.

What a check has to be able to do is fail. Each one here is written against
the thing that would fool it:

- Two specialists working together is not shown by one citing a
  calculation the other also ran. A repeated calculation replays the first
  one's record, so the row carries the other's name whether or not anyone
  read anyone's work. Only a question that was answered, a finding that
  rests on the other's finding, a calculation it cites and never ran
  itself, or a position taken with a reason counts (collaboration()).
- A check is not shown to work by a checker that approves everything. The
  probe step plants claims that are known to be wrong and reads what came
  back. Three are ones the application's own rules must catch. One is a
  claim no rule covers, which only the checker's judgment can catch.
- A change is not reconciled because it was noticed. The change step counts
  the findings that rested on the old value and asks what became of each.
- A skill was not used because it could have been read. The report lists
  who read what, and whether a cite in its work is one the skill holds.
- An export is not complete because it was written. The export step reads
  the record's own account of what the document is missing.

What it costs. Every step calls the model with the owner's key and is
billed. --max-usd is a guard, not a spending limit. It is looked at between
steps, and during a step against the delegations, consults, and checks
that have already closed. The lead's own rounds are only priced when its
turn ends, and a request in flight is never interrupted, so a run can pass
the figure before it stops. A request that fails reports no usage at all.
If a hard limit matters, set one on the API key in the provider's console.
Nothing here runs unless someone asks for it by name.

It never touches the owner's jobs. The run has its own data directory
under the output folder.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable

STEPS = ("request", "reopen", "answer", "change", "interrupt", "probe", "export")
REQUEST = (
    "We're laying out the preaction zone for data hall 1. Can it meet the insurer's water delivery time, "
    "and what releasing sequence goes with it? I need a design basis I can hand to the engineer."
)
CHANGE = (
    "One more thing: the pump test gave us 750 gpm at the riser, not the 600 on the form. "
    "Does that change the answer?"
)
CHANGED_INPUT = ("q_fill_gpm", 750.0)
# The jobs the runner knows. Each is a sample zone (sample_data.SAMPLE_ZONES), a plain request in words
# of its own, and the input the designer later corrects in chat. docs/known-answer-dh1.md and
# docs/known-answer-dh2.md are the expected basis and the pass criteria a person reads the run against.
JOBS = {
    "dh1": {"request": REQUEST, "change": CHANGE, "changed": CHANGED_INPUT, "known_answer": "docs/known-answer-dh1.md"},
    "dh2": {
        "request": (
            "Next one is data hall 2, same kind of system. The takeoff on the Inputs tab comes to about 475 gallons "
            "of pipe. Do we still get the small-system break on delivery time, and what does the fire alarm panel "
            "have to see before it lets water in? Put the basis together for the engineer."
        ),
        "change": (
            "The valve submittal came in: the trim holds 9.5 gallons, not the 6.6 on the form. "
            "What does that do to the answer?"
        ),
        "changed": ("trim_gal", 9.5),
        "known_answer": "docs/known-answer-dh2.md",
    },
}
# What stands between any run of this path and calling the milestone accepted. None of these is something
# the runner can settle, so every report prints them.
OWNER_GATES = (
    "docs/known-answer-dh1.md still has items marked OWNER TO CONFIRM. Until the owner confirms or edits them, "
    "a dh1 run is evidence about the application, not an acceptance result.",
    "The dh2 inputs were chosen for the test and are marked OWNER TO CONFIRM in docs/known-answer-dh2.md. "
    "The same applies.",
    "The releasing basis has not been checked against the primary standards or reviewed by a qualified "
    "engineer (docs/releasing-basis.md). A run that agrees with it shows consistency with the content pack only.",
)
PROBE_AGENT = "evaluation-probe"
PROBE_REASON = "Planted by the evaluation to test the trace check. It was never a finding of the team."
INTERRUPTED = (
    "Write me a short summary of this design basis for the engineer's cover email, and say what is still open."
)
RESUME = "That was cut off before it finished. Pick it up and finish it."
DEFAULT_ANSWER = (
    "I do not have that yet. Carry your assumption, say that it is one, and keep the question open for the engineer."
)
PASS, FAIL, NOT_SEEN, INFO, BLOCKED = "met", "NOT MET", "not observed", "info", "blocked"
# Roles whose rows are not a specialist's own work.
_NOT_A_SPECIALIST = ("lead", "tool-plan", "narrator", "", None, PROBE_AGENT, "qa-specialist")
_EMPTY_ANSWER = "(The specialist returned no answer.)"
# A sentence that says the zone has the size exemption. Read only on a job where it does not.
_CLAIMS_EXEMPTION = re.compile(
    r"\b(is|are|stays?|remains?|qualif\w+ (?:for|as))\s+(?:still\s+)?(?:size[- ])?exempt\w*|"
    r"\b(inside|within|under|below)\s+the\s+(?:500[- ]gal(?:lon)?s?\s+)?(?:nfpa\s+)?(?:size\s+)?(?:cap|threshold)\b|"
    r"\bno\s+(?:specific\s+)?(?:water[- ])?delivery[- ]time\s+(?:requirement|proof|test)\s+(?:is\s+)?(?:required|applies|needed)|"
    r"\b(?:still\s+)?gets?\s+the\s+(?:small[- ]system\s+)?(?:break|exemption)\b", re.IGNORECASE)
_DENIES_EXEMPTION = re.compile(
    r"\b(not|no longer|never|cannot|does not|doesn't|isn't|is not|over|exceeds?|above|loses?|lost|without)\b", re.IGNORECASE)


def _is_specialist(agent: Any) -> bool:
    return agent not in _NOT_A_SPECIALIST


def collaboration(snapshot: dict, replays: list[dict] | None = None) -> dict:
    """What on the record shows two specialists working on a shared problem, and what only looks like it.

    replays are the record's calc_replay events: who called a calculation
    that was already on the record. A calc row keeps the name of whoever ran
    it first, so a specialist that repeats the other's calculation and cites
    the result is citing "the other's row" without having read anything of
    the other's. Those citations are counted apart and never as evidence.

    Returns counts and short lists for the report:
    - answered: consults that came back with an answer of some substance.
    - used: of those, the ones after which the asker recorded a finding.
    - built_on: findings by one specialist that rest on another's finding,
      or on another's calculation that the citing specialist never ran.
    - replayed_only: findings whose only link to the other specialist is a
      calculation the citing specialist also ran itself.
    - objections, reasoned_agreements, bare_agreements: positions on a
      finding the reviewer did not write.
    - effects: exchanges that changed or settled something on the record.
    """
    snap = snapshot or {}
    every = {row["id"]: row for row in list(snap.get("findings") or []) + list(snap.get("retired_findings") or [])}
    calc_by = {row["id"]: row.get("agent") for row in snap.get("calcs") or []}
    ran_too: set[tuple[str, str]] = set()
    for event in replays or []:
        ran_too.add((str(event.get("agent") or ""), str((event.get("payload") or {}).get("id") or "")))
    consults = [row for row in snap.get("handoffs") or [] if (row.get("kind") or "") == "consult"]
    answered = [row for row in consults if row.get("status") == "returned"
                and len(str(row.get("result") or "").strip()) >= 20 and _EMPTY_ANSWER not in str(row.get("result") or "")]
    used = []
    for row in answered:
        asked_at = str(row.get("created") or "")
        later = [item for item in every.values()
                 if item.get("agent") == row.get("from_agent") and str(item.get("created") or "") >= asked_at]
        if later:
            used.append(row["id"])
    built_on, replayed_only = [], []
    for row in snap.get("findings") or []:
        author = row.get("agent")
        if not _is_specialist(author):
            continue
        real, repeat = False, False
        for ident in row.get("supports") or []:
            if ident in every and _is_specialist(every[ident].get("agent")) and every[ident].get("agent") != author:
                real = True
            elif ident in calc_by and _is_specialist(calc_by[ident]) and calc_by[ident] != author:
                if (str(author), ident) in ran_too:
                    repeat = True
                else:
                    real = True
        if real:
            built_on.append(row["id"])
        elif repeat:
            replayed_only.append(row["id"])
    reviews = [row for row in snap.get("reviews") or [] if _is_specialist(row.get("agent"))
               and (every.get(row.get("finding_id")) or {}).get("agent") != row.get("agent")]
    objections = [row for row in reviews if row.get("position") == "object"]
    agreed = [row for row in reviews if row.get("position") == "agree"]
    reasoned = [row for row in agreed if len(str(row.get("note") or "").strip()) >= 20]
    effects = []
    for row in objections:
        target = every.get(row.get("finding_id")) or {}
        if target.get("superseded_by"):
            effects.append(f"{row.get('agent')}'s objection: the author "
                           f"{'withdrew' if target.get('superseded_by') == 'withdrawn' else 'revised'} the finding")
        elif row.get("status") == "resolved":
            effects.append(f"{row.get('agent')}'s objection: settled ({str(row.get('resolution') or '')[:80]})")
        elif row.get("status") == "escalated":
            effects.append(f"{row.get('agent')}'s objection: escalated as a question, left open on the record")
    for ident in used:
        row = next(item for item in answered if item["id"] == ident)
        effects.append(f"{row.get('from_agent')} asked {row.get('to_agent')} and then recorded a finding")
    for row in reasoned:
        effects.append(f"{row.get('agent')} agreed with a reason: {str(row.get('note') or '')[:80]}")
    return {
        "consults": len(consults), "answered": [row["id"] for row in answered], "used": used,
        "built_on": built_on, "replayed_only": replayed_only,
        "objections": [row["id"] for row in objections], "open_objections": [row["id"] for row in objections if row.get("status") == "open"],
        "reasoned_agreements": [row["id"] for row in reasoned], "bare_agreements": len(agreed) - len(reasoned),
        "effects": effects,
    }


class Budget(RuntimeError):
    """The spend cap was reached. The run stops; what it wrote so far is kept."""


class Runner:
    """One evaluation run. client_factory stands in for the model in tests; a live run leaves it None."""

    def __init__(
        self,
        out_dir: Path | str,
        *,
        api_key: str = "",
        max_usd: float = 25.0,
        max_minutes: float = 30.0,
        client_factory: Callable | None = None,
        cancel_after: float = 25.0,
        log: Callable[[str], Any] | None = None,
        job: str = "dh1",
    ):
        if job not in JOBS:
            raise ValueError("job is one of: " + ", ".join(JOBS))
        self.job = job
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key
        self.max_usd = float(max_usd)
        self.max_minutes = float(max_minutes)
        self.client_factory = client_factory
        self.cancel_after = float(cancel_after)
        self.simulated = client_factory is not None
        self.checks: list[dict] = []
        self.turns: list[dict] = []
        self.notes: list[str] = []
        self.desk = None
        self.project_id = ""
        self._log_path = self.out / "progress.log"
        self._say = log
        self._before_relaunch: dict | None = None

    # -- plumbing ------------------------------------------------------------------------

    def log(self, text: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {text}"
        with self._log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if self._say is not None:
            self._say(line)

    def check(self, step: str, outcome: str, name: str, result: str, evidence: str = "") -> None:
        self.checks.append({"step": step, "outcome": outcome, "check": name, "result": result, "evidence": evidence})
        self.log(f"  [{result}] {name}" + (f" — {evidence}" if evidence else ""))

    def _open_desk(self):
        from fpfa.desk import Desk

        os.environ["FPFA_DATA_DIR"] = str(self.out / "data")
        os.environ["FPFA_CONTENT_UPDATES"] = "0"
        desk = Desk()
        if self.api_key:
            # The key was read before the data directory moved. The run's own directory holds none.
            desk._key = self.api_key
        self.desk = desk
        return desk

    def _patched(self):
        """The model client the desk builds: the real one, or the stand-in a test supplied."""
        from contextlib import nullcontext
        from unittest.mock import patch

        if self.client_factory is None:
            return nullcontext()
        return patch("fpfa.desk.AnthropicMessages", self.client_factory)

    def _snapshot(self) -> dict:
        return self.desk.call(self.desk.record.snapshot, self.project_id)

    def spent(self) -> float:
        from fpfa.usage_report import cost, job_totals, usage_events

        rows = self.desk.call(usage_events, self.desk.record, self.project_id)
        return float(cost(job_totals(rows))["total"])

    def _spent_in_flight(self, since_seq: int) -> float:
        """Dollars the delegations, consults, and checks closed since a turn began add up to. A lower bound.

        A delegation's event carries its consults' usage, so a consult counts
        only while its delegation is still open: after the newest delegation
        event. A failed one counts with what it had used before it failed.
        The lead's own rounds, and any request still in flight, are not here.
        """
        from fpfa.usage_report import cost, normalize

        total = 0.0
        events = self.desk.call(self.desk.record.events_by_kind, self.project_id,
                                ("delegation", "record_check", "check_failed", "check_incomplete", "consult"))
        closed = max((int(event.get("seq") or 0) for event in events if event["kind"] == "delegation"), default=0)
        for event in events:
            number = int(event.get("seq") or 0)
            if number <= since_seq or (event["kind"] == "consult" and number < closed):
                continue
            total += cost(normalize((event.get("payload") or {}).get("usage")))["total"]
        return total

    def _last_seq(self) -> int:
        events = self.desk.call(self.desk.record.events, self.project_id, 1)
        return int(events[-1]["seq"]) if events else 0

    def _turn(self, label: str, text: str, *, cancel_at: float | None = None) -> dict:
        """Send one message and wait for the job to end. Returns what the turn left behind."""
        desk = self.desk
        before = self.spent()
        if before >= self.max_usd:
            raise Budget(f"${before:.2f} spent before the {label} step; the cap is ${self.max_usd:.2f}.")
        self.log(f"{label}: sending the message ({len(text)} characters)")
        since = self._last_seq()
        started = time.time()
        cancelled = False
        with self._patched():
            desk.call(desk.send_chat, text)
            while True:
                desk.pump()
                if not desk.call(desk._pending_here):
                    desk.pump()
                    break
                waited = time.time() - started
                over_time = waited > self.max_minutes * 60
                over_budget = before + self._spent_in_flight(since) >= self.max_usd
                due = cancel_at is not None and waited >= cancel_at
                if not cancelled and (due or over_time or over_budget):
                    why = "as the step calls for" if due else ("the time limit" if over_time else "the spend cap")
                    self.log(f"{label}: cancelling ({why}) after {waited:.0f} s")
                    desk.call(desk.cancel_running_jobs)
                    cancelled = True
                    if over_time or over_budget:
                        self.notes.append(f"The {label} step was cancelled from outside: {why}.")
                time.sleep(0.05 if self.simulated else 0.5)
        seconds = round(time.time() - started, 1)
        turns = desk.call(lambda: list(desk.chat_log))
        reply = next((turn.get("text") or "" for turn in reversed(turns) if turn.get("role") != "user"), "")
        after = self.spent()
        row = {"label": label, "seconds": seconds, "usd": round(after - before, 4), "cancelled": cancelled, "reply": reply,
               "since": since}
        self.turns.append(row)
        self.log(f"{label}: finished in {seconds:.0f} s, about ${after - before:.2f}")
        return row

    # -- the steps -----------------------------------------------------------------------

    def step_request(self) -> None:
        """A plain objective. No specialist is named and no order is given."""
        from fpfa import coherence, content_use
        from fpfa.checker import check_is_current, tier_counts
        from fpfa.paths import content_root

        desk = self.desk
        desk.call(lambda: desk.ask_claude.set(False))
        desk.call(desk.start_sample_di, None, self.job)
        desk.pump()
        self.project_id = desk.call(lambda: desk.project["id"])
        turn = self._turn("request", JOBS[self.job]["request"])
        snap = self._snapshot()
        events = desk.call(desk.record.events_by_kind, self.project_id,
                           ("plan", "delegation", "consult", "record_check", "reply_audit", "calc_replay"))
        plans = [event for event in events if event["kind"] == "plan"]
        delegations = [event for event in events if event["kind"] == "delegation"]
        who = sorted({(event.get("payload") or {}).get("specialist") or "" for event in delegations} - {""})

        if not plans:
            self.check("request", "A", "The lead set out a plan", NOT_SEEN, "no plan on the record")
        else:
            first = delegations[0]["seq"] if delegations else 10 ** 12
            self.check("request", "A", "The lead set out a plan before it delegated",
                       PASS if plans[0]["seq"] < first else FAIL, (plans[-1]["payload"] or {}).get("objective", "")[:160])
        self.check("request", "A", "The lead brought in the specialists the request needs without being told which",
                   PASS if len(who) >= 2 else (NOT_SEEN if len(who) == 1 else FAIL),
                   f"delegated to: {', '.join(who) or 'nobody'} ({len(delegations)} delegation{'s' if len(delegations) != 1 else ''})")
        own_calcs = [row["tool"] for row in snap["calcs"] if row.get("agent") == "lead"]
        own_figures = [row for row in snap["findings"] if row.get("agent") == "lead" and row.get("label") == "calculated"]
        self.check("request", "A", "The lead did not do a specialist's calculation itself",
                   PASS if not own_calcs and not own_figures else FAIL,
                   ("lead ran: " + ", ".join(sorted(set(own_calcs)))) if own_calcs else "")
        authors = sorted({row.get("agent") for row in snap["findings"] if _is_specialist(row.get("agent"))})
        self.check("request", "A", "Each specialist that was brought in put a finding of its own on the record",
                   PASS if who and set(who) <= set(authors) else (NOT_SEEN if not who else FAIL),
                   "findings by: " + (", ".join(authors) or "nobody") + "; a role that was run and wrote nothing contributed nothing")

        found = collaboration(snap, [event for event in events if event["kind"] == "calc_replay"])
        self.check("request", "B", "One specialist asked the other for something it needed and got an answer",
                   PASS if found["answered"] else NOT_SEEN,
                   f"{found['consults']} question{'s' if found['consults'] != 1 else ''}, {len(found['answered'])} answered, "
                   f"{len(found['used'])} followed by a finding from the asker")
        self.check("request", "B", "A specialist's finding rests on the other's work, not on a repeat of its own calculation",
                   PASS if found["built_on"] else NOT_SEEN,
                   f"{len(found['built_on'])} finding{'s' if len(found['built_on']) != 1 else ''} rest on the other's finding or on a "
                   f"calculation only the other ran; {len(found['replayed_only'])} cite a calculation the citing specialist "
                   "also ran itself, which shows nothing and is not counted")
        self.check("request", "B", "A specialist took a position, with a reason, on a finding it did not write",
                   PASS if found["objections"] or found["reasoned_agreements"] else NOT_SEEN,
                   f"{len(found['objections'])} objection{'s' if len(found['objections']) != 1 else ''}, "
                   f"{len(found['reasoned_agreements'])} agreement{'s' if len(found['reasoned_agreements']) != 1 else ''} with a reason, "
                   f"{found['bare_agreements']} bare agreement{'s' if found['bare_agreements'] != 1 else ''} (not counted)")
        exchanged = found["answered"] or found["objections"] or found["reasoned_agreements"]
        if not exchanged:
            self.check("request", "B", "An exchange changed, supported, or left open a conclusion on the record", NOT_SEEN,
                       "there was no exchange to have an effect")
        else:
            self.check("request", "B", "An exchange changed, supported, or left open a conclusion on the record",
                       PASS if found["effects"] else FAIL, "; ".join(found["effects"])[:400] or
                       "questions and positions were recorded and nothing on the record followed from any of them")
        if found["objections"]:
            reviews = {row["id"]: row for row in snap["reviews"]}
            self.check("request", "B", "Every objection has an end: revised, settled with a decision, or escalated as a question",
                       PASS if not found["open_objections"] else FAIL,
                       "; ".join(f"{reviews[ident]['agent']}: {reviews[ident]['status']}" for ident in found["objections"])[:300])
        else:
            self.check("request", "B", "Every objection has an end", NOT_SEEN, "no objection was raised")
        analysis = coherence.analyze(snap)
        loose = [row for row in snap["findings"] if analysis["findings"][row["id"]].get("notes")]
        self.check("request", "B", "No finding rests on a value other than the project input without saying so", INFO,
                   f"{len(loose)} finding{'s' if len(loose) != 1 else ''} on an alternative value")

        used = content_use.skill_use(snap, content_root())
        unread = content_use.unread(snap)
        self.check("request", "D", "Which specialist read which method (skill)", INFO,
                   "; ".join(f"{row['agent']}: {row['slug']}" + ("" if row["before_findings"] else " (after its findings)")
                             for row in used)[:500] or "no skill was read by anyone")
        if not authors:
            self.check("request", "D", "Each specialist read a method before it recorded findings", NOT_SEEN,
                       "no specialist recorded a finding")
        else:
            late = sorted({row["agent"] for row in used if not row["before_findings"] and _is_specialist(row["agent"])}
                          - {row["agent"] for row in used if row["before_findings"]})
            none = [agent for agent in unread if _is_specialist(agent)]
            self.check("request", "D", "Each specialist read a method before it recorded findings",
                       PASS if not none and not late else FAIL,
                       ("read nothing: " + ", ".join(none) + ". " if none else "")
                       + ("read only after its findings: " + ", ".join(late) + ". " if late else "")
                       + "A read shows the method was in front of the specialist, not that it was followed.")
        carried = [row for row in used if row["carried"]]
        self.check("request", "D", "A cite a specialist recorded is one the method it read holds",
                   PASS if carried else NOT_SEEN,
                   "; ".join(f"{row['agent']} from {row['slug']}: " + ", ".join(str(item['section']) for item in row['carried'][:3])
                             for row in carried)[:400] or "no recorded cite traces to a skill that was read; read the findings to judge")

        self.check("request", "D", "A trace check judged the findings as they stand",
                   PASS if snap["findings"] and check_is_current(snap) else (NOT_SEEN if not snap["findings"] else FAIL),
                   json.dumps(tier_counts(snap)) if snap["findings"] else "no findings on the record")
        self._check_reply("request", turn)
        self._check_exemption("request", turn, snap)
        asks = [row for row in snap["questions"] if row["status"] == "open" and row.get("audience") == "designer"]
        self.check("request", "E", "What the team needs from the designer is asked as a question", INFO,
                   f"{len(asks)} for the designer, "
                   f"{sum(1 for row in snap['questions'] if row['status'] == 'open') - len(asks)} for the engineer")
        self._before_relaunch = desk.call(lambda: {key: desk.team.get(key) for key in ("plan", "asks", "rfis", "tiers", "strip")})
        self._before_relaunch["findings"] = desk.call(lambda: [row["text"] for row in desk.team.get("findings") or []])

    def _check_exemption(self, step: str, turn: dict, snap: dict) -> None:
        """On a zone whose pipe is under the cap and whose total is over it: nobody says the exemption is met."""
        from fpfa.workflow import exemption_answer

        screens = [row for row in snap["calcs"] if row.get("tool") == "dry_delivery_screen"
                   and (row.get("agent") or "") in ("tool-plan", "") and "exemption_volume_gal" in (row.get("outputs") or {})]
        if not screens:
            return
        out = screens[-1]["outputs"]
        if exemption_answer(out) != "no" or not out.get("pipe_only_nfpa_delivery_time_exempt"):
            return
        texts = [("the reply", turn.get("reply") or "")] + [
            (f"a finding by {row.get('agent')}", row.get("text") or "") for row in snap["findings"]]
        wrong = []
        for where, text in texts:
            for sentence in re.split(r"(?<=[.;])\s+", text):
                if _CLAIMS_EXEMPTION.search(sentence) and not _DENIES_EXEMPTION.search(sentence):
                    wrong.append(f"{where}: {sentence.strip()[:140]}")
        self.check(step, "D", "Nobody states the size exemption on the pipe alone when the zone total is over the cap",
                   PASS if not wrong else FAIL,
                   "; ".join(wrong)[:400] or f"the zone total is {out['exemption_volume_gal']:.1f} gal against "
                   f"{out['nfpa_size_cap_gal']:.0f}; no sentence in the reply or the findings claims the exemption. "
                   "A phrase match; read the reply to be sure.")

    def _check_reply(self, step: str, turn: dict) -> None:
        """What the application found when it looked this turn's reply up, and the releasing wording."""
        from fpfa.releasing import release_wording_hits

        desk = self.desk
        reply = turn.get("reply") or ""
        events = desk.call(desk.record.events_by_kind, self.project_id, ("reply_audit",))
        # Only the audit this turn wrote. A reply with no figure in it writes none.
        audits = [event for event in events if int(event.get("seq") or 0) > int(turn.get("since") or 0)]
        if audits:
            found = audits[-1]["payload"] or {}
            bad = list(found.get("unfound") or []) + list(found.get("stale") or [])
            self.check(step, "D", "Every figure in the lead's reply is on the record or in something it read",
                       PASS if not bad else FAIL,
                       f"{found.get('figures', 0)} figures; not found: {found.get('unfound') or 'none'}; out of date: {found.get('stale') or 'none'}")
        else:
            self.check(step, "D", "Every figure in the lead's reply is on the record or in something it read", INFO,
                       "this reply had no figure with a unit")
        hits = [sentence for _line, sentence in release_wording_hits(reply or "")]
        self.check(step, "D", "The reply does not name low air as a release input", PASS if not hits else FAIL,
                   "; ".join(hits)[:300] or "no sentence the detector knows; a paraphrase it does not know would pass")

    def step_reopen(self) -> None:
        """Close the window and open it again on the same data."""
        desk = self.desk
        desk.call(desk.close)
        desk = self._open_desk()
        desk.pump()
        desk.call(desk.select_project, self.project_id)
        desk.pump()
        after = desk.call(lambda: {key: desk.team.get(key) for key in ("plan", "asks", "rfis", "tiers", "strip")})
        after["findings"] = desk.call(lambda: [row["text"] for row in desk.team.get("findings") or []])
        before = self._before_relaunch or {}
        same = [key for key in after if after[key] == before.get(key)]
        self.check("reopen", "C", "After a relaunch the plan, the findings, and the open questions are as they were",
                   PASS if len(same) == len(after) else FAIL,
                   "differs: " + ", ".join(sorted(set(after) - set(same))) if len(same) != len(after) else "")
        desk.call(desk.send_chat, "/status")
        desk.pump()
        turns = desk.call(lambda: list(desk.chat_log))
        text = turns[-1].get("text") or "" if turns else ""
        (self.out / "status-after-reopen.md").write_text(text + "\n", encoding="utf-8")
        self.check("reopen", "C", "The app says where the job stands without a model call", PASS if text.startswith("**Where ") else FAIL,
                   "written to status-after-reopen.md")

    def step_answer(self) -> None:
        """The designer answers what the team asked. The stock answer says the value is not known yet."""
        desk = self.desk
        asks = desk.call(lambda: list(desk.team.get("asks") or []))
        if not asks:
            self.check("answer", "E", "The designer answers the team's questions on the panel", NOT_SEEN,
                       "the team asked the designer nothing")
            return
        for row in asks:
            desk.call(desk.answer_question, row["id"], DEFAULT_ANSWER)
            self.log(f"  answered: {row['text'][:100]}")
        left = desk.call(lambda: len(desk.team.get("asks") or []))
        self.check("answer", "E", "The designer answers the team's questions on the panel", PASS if left == 0 else FAIL,
                   f"{len(asks)} answered; the lead reads them at its next turn")

    def step_change(self) -> None:
        """The designer states a different value for an input in chat."""
        from fpfa import coherence, inputs

        desk = self.desk
        name, value = JOBS[self.job]["changed"]
        before = self._snapshot()
        was = desk.call(desk.record.givens, self.project_id).get(name)
        turn = self._turn("change", JOBS[self.job]["change"])
        snap = self._snapshot()
        given = desk.call(desk.record.givens, self.project_id).get(name)
        recorded = given is not None and inputs.same(inputs.decode(given["value"]), value)
        self.check("change", "C", "The lead put the value the designer stated on the record",
                   PASS if recorded and given.get("agent") == "lead" else FAIL,
                   f"{name} is {inputs.show(name, inputs.decode(given['value'])) if given else 'missing'}"
                   f"{' (' + str(given.get('source')) + ')' if given else ''}")
        # What rested on the old value: the specialists' findings, as they stood before the message, that cite a
        # calculation the change left out of date. Noticing the change is not reconciling it; each of these
        # has to have been replaced or withdrawn by its author.
        analysis = coherence.analyze(snap)
        old_calcs = {ident for ident in analysis["stale"]["calcs"]
                     if was is not None and was["id"] in _upstream_facts(ident, snap)}
        rested = [row for row in before["findings"] if _is_specialist(row.get("agent"))
                  and set(row.get("supports") or []) & old_calcs]
        now_current = {row["id"] for row in snap["findings"]}
        left = [row for row in rested if row["id"] in now_current]
        retired = {row["id"]: row for row in snap["retired_findings"]}
        replaced = [row for row in rested if (retired.get(row["id"]) or {}).get("superseded_by") not in (None, "", "withdrawn")]
        withdrawn = [row for row in rested if (retired.get(row["id"]) or {}).get("superseded_by") == "withdrawn"]
        if not recorded:
            self.check("change", "C", "Every finding that rested on the old value was replaced or withdrawn by its author", FAIL,
                       "the new value never reached the record, so nothing could be reconciled")
        elif not rested:
            self.check("change", "C", "Every finding that rested on the old value was replaced or withdrawn by its author", NOT_SEEN,
                       f"no specialist's finding rested on a calculation that used {name}; the run gave no reconciliation to see")
        else:
            self.check("change", "C", "Every finding that rested on the old value was replaced or withdrawn by its author",
                       PASS if not left else FAIL,
                       f"{len(rested)} rested on it: {len(replaced)} replaced, {len(withdrawn)} withdrawn, {len(left)} left standing"
                       + ("".join(f"; left: {row['agent']}: {row['text'][:70]}" for row in left[:3])))
        fresh = [row for row in snap["calcs"] if _is_specialist(row.get("agent"))
                 and analysis["calcs"][row["id"]]["state"] == coherence.CURRENT
                 and given is not None and given["id"] in (row.get("depends") or [])]
        self.check("change", "C", "What the specialists calculated again on the new value", INFO,
                   ", ".join(sorted({row["tool"] for row in fresh})) or "nothing was calculated again on it")
        stale = desk.call(lambda: list(desk.team.get("stale") or []))
        by_agents = [row for row in stale if row["by"] not in ("tool-plan", "tool plan", "")]
        self.check("change", "C", "Nothing a specialist wrote is still marked out of date",
                   PASS if recorded and not by_agents else FAIL,
                   "; ".join(f"{row['kind']} by {row['by']}: {row['text'][:60]}" for row in by_agents)[:400]
                   or "this alone shows nothing was left marked; the check above shows whether anything was reconciled")
        self._check_reply("change", turn)
        self._check_exemption("change", turn, snap)
        said = re.search(r"/run\b|run the zone again|re-?run the zone|Results tab", turn["reply"] or "", re.IGNORECASE)
        changed = desk.call(desk.run_changes)
        if changed:
            self.check("change", "C", "The lead told the designer the tables are from the earlier run",
                       PASS if said else NOT_SEEN, "the form changed after the run: " + ", ".join(changed))

    def step_interrupt(self) -> None:
        """Cancel a turn part-way, then ask for it to be finished."""
        desk = self.desk
        first = self._turn("interrupt", INTERRUPTED, cancel_at=self.cancel_after)
        jobs = desk.call(lambda: [(job.kind, job.status) for job in desk.jobs.snapshot() if job.project_id == self.project_id])
        last = jobs[-1][1] if jobs else ""
        if last != "cancelled":
            self.check("interrupt", "F", "A turn cancelled part-way stops and says so", NOT_SEEN,
                       f"the turn ended ({last}) before the cancel reached it")
        else:
            self.check("interrupt", "F", "A turn cancelled part-way stops and says so",
                       PASS if "Cancelled" in (first["reply"] or "") else FAIL, (first["reply"] or "")[:160])
        second = self._turn("resume", RESUME)
        jobs = desk.call(lambda: [(job.kind, job.status) for job in desk.jobs.snapshot() if job.project_id == self.project_id])
        self.check("interrupt", "F", "The next turn picks the job up from the record and finishes",
                   PASS if jobs and jobs[-1][1] == "done" and (second["reply"] or "").strip() else FAIL, f"job {jobs[-1][1] if jobs else 'missing'}")
        replays = sum(int(row.get("replay_count") or 0) for row in self._snapshot()["calcs"])
        self.check("interrupt", "F", "Calculations already on the record were replayed, not run again", INFO,
                   f"{replays} replay{'s' if replays != 1 else ''} on this job so far")
        self._check_reply("interrupt", second)

    def step_probe(self) -> None:
        """Plant claims that are known to be wrong, run the trace check, and read what came back.

        A check that approves everything looks exactly like a check that
        works until something wrong is put in front of it. Four findings are
        written to the record under the name evaluation-probe, each citing a
        real calculation record of this job:

        1. a figure the cited record does not hold (a 765 gal cap);
        2. a figure the cited record holds only as another quantity;
        3. a release claim that breaks the releasing rule;
        4. a trim family that is not the one the cited record elects.

        The application's own rules have to reject the first three whatever
        the checker says. No rule covers the fourth: only the checker's
        judgment can reject it, so it is the one that says something about
        the checker. Afterwards the four are withdrawn. They stay in the
        record's history, marked as planted, and are never current again.
        """
        from fpfa import coherence
        from fpfa.checker import latest_check

        desk = self.desk
        record = desk.record
        # The probes cite the tool plan's calculations. They have to be current, or the check would set the
        # probes aside as out of date and judge nothing.
        self._run_zone_if_behind("probe")
        snap = self._snapshot()
        standing = coherence.analyze(snap)["calcs"]
        by_tool: dict[str, dict] = {}
        for row in snap["calcs"]:
            if (row.get("agent") or "") in ("tool-plan", "") and standing[row["id"]]["state"] == coherence.CURRENT:
                by_tool[row["tool"]] = row
        need = ("zone_trapped_volume", "dry_delivery_screen", "elect_di_trim", "releasing_truth_table")
        if any(tool not in by_tool for tool in need):
            self.check("probe", "D", "The trace check was tested with planted wrong claims", NOT_SEEN,
                       "the tool plan's calculation records are not on this job")
            return
        zone = float(by_tool["zone_trapped_volume"]["outputs"]["zone_gal"])
        family = str(by_tool["elect_di_trim"]["outputs"].get("family") or "")
        other = "electric/pneumatic (El/Pn)" if family != "El/Pn" else "electric/electric (El/El)"
        planted = {
            "figure": ("A double-interlock zone of up to 765 gal needs no delivery-time proof.",
                       by_tool["dry_delivery_screen"]["id"]),
            "unit": (f"The trip-to-water time of this zone is {zone:.1f} s.", by_tool["zone_trapped_volume"]["id"]),
            # Written in two parts so the source scan for this wording does not find the probe itself.
            "release": ("The preaction valve releases on detection AND low" + " air.", by_tool["releasing_truth_table"]["id"]),
            "meaning": (f"The trim screen elects the {other} family for this zone.", by_tool["elect_di_trim"]["id"]),
        }
        ids: dict[str, str] = {}
        for key, (text, support) in planted.items():
            row = desk.call(lambda t=text, c=support: record.record_finding(
                self.project_id, agent=PROBE_AGENT, text=t, label="calculated", supports=[c]))
            ids[key] = row["id"]
        self.log("probe: four wrong claims planted; running the trace check (one model call)")
        verdicts: dict[str, dict] = {}
        try:
            with self._patched():
                desk.call(desk.start_record_check)
                self._wait_idle()
            check = desk.call(latest_check, record, self.project_id) or {}
            verdicts = {row.get("finding_id"): row for row in check.get("rows") or []}
            overruled = {row.get("finding_id"): row for row in check.get("overruled") or []}
        finally:
            for ident in ids.values():
                try:
                    desk.call(lambda i=ident: record.retire_finding(
                        self.project_id, i, by=PROBE_AGENT, reason=PROBE_REASON, may_retire_any=True))
                except Exception as exc:  # noqa: BLE001 - a probe left behind is said, not hidden
                    self.notes.append(f"A planted probe finding [{ident}] could not be withdrawn: {exc}. "
                                      "It is still on this run's record under the name evaluation-probe.")
        if not all(ident in verdicts and verdicts[ident].get("verdict") != "No verdict" for ident in ids.values()):
            # A check that was cut off, or that skipped a planted claim, tested nothing. Silence is not a rejection.
            self.check("probe", "D", "The trace check was tested with planted wrong claims", NOT_SEEN,
                       "the check did not return a verdict for the planted claims")
            return
        by_rule = ("figure", "unit", "release")
        passed_rule = [key for key in by_rule if verdicts[ids[key]].get("verdict") == "Supported"]
        self.check("probe", "D", "The application's own rules reject a wrong figure, a wrong unit, and a wrong releasing claim",
                   PASS if not passed_rule else FAIL,
                   "; ".join(f"{key}: {verdicts[ids[key]].get('verdict')} ({str(verdicts[ids[key]].get('reason') or '')[:70]})"
                             for key in by_rule))
        fooled = [key for key in by_rule if ids[key] in overruled]
        meaning = verdicts[ids["meaning"]]
        self.check("probe", "D", "The checker itself rejects a wrong claim that no rule covers",
                   PASS if meaning.get("verdict") != "Supported" else FAIL,
                   f"planted: \"{planted['meaning'][0]}\" against a record that elects {family or 'no family'}. "
                   f"Verdict: {meaning.get('verdict')}."
                   + ("" if meaning.get("verdict") != "Supported" else
                      " The checker approved a claim that contradicts the row it cites. Treat every "
                      "trace-consistent finding in this run as unproven."))
        self.check("probe", "D", "What the checker said about the three claims the rules caught", INFO,
                   (f"it approved {len(fooled)} of 3 ({', '.join(fooled)}) and was overruled; a checker that approves "
                    "these is a checker to distrust on the rest") if fooled else "it rejected all three itself")

    def step_export(self) -> None:
        """Run the zone again if the form moved, run the trace check if it is behind, and write the documents."""
        from fpfa.checker import COMPLETE_LINE, INCOMPLETE_HEAD, LADDER, NOT_STANDARD, check_is_current, coverage
        from fpfa.releasing import release_wording_hits
        from fpfa.usage_report import report_text

        desk = self.desk
        self._run_zone_if_behind("export")
        snap = self._snapshot()
        if snap["findings"] and not check_is_current(snap):
            self.log("export: the findings changed after the last trace check; running it (one model call)")
            with self._patched():
                desk.call(desk.start_record_check)
                self._wait_idle()
        reason = desk.call(desk.design_basis_ready)
        target = self.out / "design-basis.docx"
        if reason:
            self.check("export", "D", "The Design Basis can be exported", FAIL, reason[:300])
        else:
            desk.call(desk.export_design_basis_to, target)
            text = _docx_text(target)
            self.check("export", "D", "The Design Basis can be exported", PASS, target.name)
            self.check("export", "D", "The draft says how far each finding was taken and that no standard was opened",
                       PASS if NOT_STANDARD in text and "How far each statement was taken" in text
                       and all(name in text for name, _what, _where in LADDER) and "NOT PERFORMED" in text else FAIL,
                       "the kinds of assurance are listed, with verification against the standard and an engineer's "
                       "review named as not performed")
            # The planted probes are history by now. A sentence of theirs in the history section is not the draft's own.
            body = "\n".join(line for line in text.splitlines() if PROBE_AGENT not in line)
            hits = [sentence for _line, sentence in release_wording_hits(body)]
            self.check("export", "D", "The draft does not name low air as a release input", PASS if not hits else FAIL,
                       "; ".join(hits)[:300])
            found = coverage(self._snapshot())
            said = (COMPLETE_LINE in text) if found["complete"] else (INCOMPLETE_HEAD in text and all(gap in text for gap in found["gaps"]))
            self.check("export", "D", "The draft says at its head what it does not cover", PASS if said else FAIL,
                       "complete by the record's account" if found["complete"] else f"{len(found['gaps'])} gap{'s' if len(found['gaps']) != 1 else ''} listed")
            self.check("export", "D", "The record holds a specialist's finding for every calculation, and nothing is waiting on the team",
                       PASS if found["complete"] else FAIL, " ".join(found["gaps"])[:500])
        desk.call(desk.send_chat, "/status")
        desk.pump()
        turns = desk.call(lambda: list(desk.chat_log))
        (self.out / "status-at-end.md").write_text((turns[-1].get("text") or "") + "\n", encoding="utf-8")
        (self.out / "thread.md").write_text(
            "\n\n".join(f"### {'Designer' if turn.get('role') == 'user' else 'Assistant'}\n\n{turn.get('text') or ''}" for turn in turns) + "\n",
            encoding="utf-8")
        (self.out / "usage.txt").write_text(desk.call(report_text, desk.record, self.project_id) + "\n", encoding="utf-8")
        (self.out / "record.json").write_text(json.dumps(self._snapshot(), indent=2, default=str), encoding="utf-8")
        (self.out / "team-panel.json").write_text(json.dumps(desk.call(lambda: dict(desk.team)), indent=2, default=str), encoding="utf-8")

    def _run_zone_if_behind(self, step: str) -> None:
        """Run the fixed tool plan again when the form moved past the last run. No model call."""
        desk = self.desk
        if desk.call(desk.run_changes):
            self.log(f"{step}: the form changed after the last run; running the zone again (no model call)")
            desk.call(desk.start_zone_run)
            self._wait_idle()

    def _wait_idle(self, limit: float = 900.0) -> None:
        deadline = time.time() + limit
        desk = self.desk
        while time.time() < deadline:
            desk.pump()
            if not desk.call(desk._pending_here):
                desk.pump()
                return
            time.sleep(0.05 if self.simulated else 0.5)
        raise RuntimeError("a job did not finish in time")

    # -- the run -------------------------------------------------------------------------

    def run(self, steps: tuple[str, ...] | list[str] = STEPS) -> dict:
        wanted = [step for step in STEPS if step in steps]
        if "request" not in wanted:
            raise ValueError("the run starts with the request step")
        started = time.time()
        self._open_desk()
        self.desk.pump()
        stopped = ""
        try:
            for step in wanted:
                self.log(f"step: {step}")
                getattr(self, f"step_{step}")()
        except Budget as exc:
            stopped = str(exc)
            self.log("stopped: " + stopped)
        except Exception as exc:  # noqa: BLE001 - the report says what stopped the run
            from fpfa.claude_client import safe_error

            stopped = safe_error(exc)
            self.log("stopped: " + stopped)
        finally:
            report = self._report(wanted, stopped, round(time.time() - started, 1))
            try:
                self.desk.call(self.desk.close)
            except Exception:
                pass
        return report

    def _report(self, steps: list[str], stopped: str, seconds: float) -> dict:
        from fpfa import __version__
        from fpfa.claude_client import MODEL_ID, configured_effort
        from fpfa.content_update import content_version_text
        from fpfa.usage_report import RATES_DATE, clock

        try:
            spent = self.spent() if self.project_id else 0.0
        except Exception:
            spent = sum(turn["usd"] for turn in self.turns)
        try:
            pack = content_version_text()
        except Exception:
            pack = "unknown"
        counts = {word: sum(1 for item in self.checks if item["result"] == word) for word in (PASS, FAIL, NOT_SEEN, INFO)}
        try:
            context = dict(self.desk.record.context)
        except Exception:
            context = {}
        try:
            from fpfa.usage_report import failures, retries, usage_events

            rows = self.desk.call(usage_events, self.desk.record, self.project_id) if self.project_id else []
            failed = failures(rows)["count"]
            again = self.desk.call(retries, self.desk.record, self.project_id) if self.project_id else 0
        except Exception:
            failed, again = 0, 0
        report = {
            "job": self.job, "known_answer": JOBS[self.job]["known_answer"],
            "content_fingerprint": context.get("content_fingerprint", ""), "calc_identity": context.get("calc_identity", ""),
            "failed_contexts": failed, "retries": again, "owner_gates": list(OWNER_GATES),
            "simulated": self.simulated, "stopped": stopped, "steps": steps, "seconds": seconds, "usd": round(spent, 4),
            "turns": [{key: value for key, value in turn.items() if key not in ("reply", "since")} for turn in self.turns],
            "checks": self.checks, "counts": counts, "notes": self.notes,
            "app": __version__, "content": pack, "model": MODEL_ID, "effort": configured_effort() or "model default",
            "platform": f"{platform.system()} {platform.release()}", "python": platform.python_version(),
        }
        (self.out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        lines = ["# Live evaluation run", ""]
        if self.simulated:
            lines += ["**SIMULATED.** The model was a scripted stand-in. This run shows the runner works; it says nothing "
                      "about the live model.", ""]
        lines += [
            f"- When: {time.strftime('%Y-%m-%d %H:%M')}",
            f"- Job: {self.job}. Expected basis and pass criteria: {report['known_answer']}",
            f"- App {report['app']}, content {report['content']}, model {report['model']}, effort {report['effort']}",
            f"- Content fingerprint {report['content_fingerprint'] or 'unknown'}, calc code {report['calc_identity'] or 'unknown'}. "
            "Two runs with the same fingerprint used the same skills, roles, notes, and calcs.",
            f"- Machine: {report['platform']}, Python {report['python']}",
            f"- Steps run: {', '.join(steps)}",
            f"- Time: {clock(seconds) or '0 s'} in all. Estimated cost: ${spent:.2f} at the list prices of {RATES_DATE}. "
            "An estimate from the usage the API reported, not a bill.",
        ]
        if failed or again:
            lines.append(
                f"- Failures: {failed} model context{'s' if failed != 1 else ''} ended on an error and {again} "
                f"request{'s were' if again != 1 else ' was'} sent again. A failed request reports no usage, so the "
                "cost above is a floor. usage.txt marks each."
            )
        if stopped:
            lines.append(f"- **The run stopped early:** {stopped}")
        lines += ["", "**What this run cannot be, whatever its checks say:**", ""]
        lines += [f"- {gate}" for gate in OWNER_GATES]
        lines += ["", f"Checks: {counts[PASS]} met, {counts[FAIL]} not met, {counts[NOT_SEEN]} not observed, {counts[INFO]} for information.", ""]
        lines += ["| Step | Outcome | Check | Result | What the record shows |", "| --- | --- | --- | --- | --- |"]
        for item in self.checks:
            evidence = (item["evidence"] or "").replace("|", "/").replace("\n", " ")
            lines.append(f"| {item['step']} | {item['outcome']} | {item['check']} | {item['result']} | {evidence} |")
        lines += ["", "| Turn | Time | Estimated cost | Cancelled |", "| --- | --- | --- | --- |"]
        for turn in self.turns:
            lines.append(f"| {turn['label']} | {clock(turn['seconds']) or '0 s'} | ${turn['usd']:.2f} | {'yes' if turn['cancelled'] else ''} |")
        for note in self.notes:
            lines += ["", note]
        lines += [
            "",
            "## What a program cannot tell you",
            "",
            "Read these yourself. A check above says a thing happened. It does not say it was done well.",
            "",
            "- `thread.md`: was the plain request enough, and did the lead ask only what it needed?",
            "- `design-basis.docx`: would you hand this to the engineer? Is anything stated more firmly than its tier earns?",
            "- `team-panel.json` and `record.json`: were the objections about something real, and did the revisions answer them?",
            "- `status-after-reopen.md`: coming back cold, could you tell where the job stood?",
            "- `usage.txt`: is the time and the cost acceptable for what came out?",
            f"- `{report['known_answer']}`: the expected basis for this job, the wrong answers to look for, and the pass criteria.",
            "",
            "A check marked not observed means the run gave no chance to see it, or the model did not do it. "
            "Two specialists that never touch each other's work show up here as not observed, not as a failure of the app. "
            "That is the finding.",
        ]
        (self.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.log(f"report written to {self.out / 'report.md'}")
        return report


def _upstream_facts(calc_id: str, snapshot: dict) -> set[str]:
    """The ids of the input facts a calculation followed, directly or through a calculation it took a figure from."""
    calcs = {row["id"]: row for row in snapshot.get("calcs") or []}
    seen: set[str] = set()
    found: set[str] = set()
    queue = [calc_id]
    while queue:
        ident = queue.pop()
        if ident in seen or ident not in calcs:
            continue
        seen.add(ident)
        for dep in calcs[ident].get("depends") or []:
            if dep in calcs:
                queue.append(dep)
            else:
                found.add(dep)
    return found


def _docx_text(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    parts = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m fpfa.live_eval", description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", required=True, help="Folder for the report, the documents, and the run's own data")
    parser.add_argument("--job", default="dh1", help="Which sample job to run: " + ", ".join(JOBS) + ". Default dh1")
    parser.add_argument("--max-usd", type=float, default=25.0,
                        help="A guard, not a spending limit: checked between steps and against finished delegations. Default 25")
    parser.add_argument("--max-minutes", type=float, default=30.0, help="Cancel a single turn that runs longer. Default 30")
    parser.add_argument("--effort", default="", help="low, medium, high, xhigh, or max. Default: the model's own")
    parser.add_argument("--steps", default=",".join(STEPS), help="Comma-separated. Default: " + ",".join(STEPS))
    parser.add_argument("--cancel-after", type=float, default=25.0, help="Seconds into the interrupt step before the cancel. Default 25")
    parser.add_argument("--yes", action="store_true", help="Do not ask before spending")
    args = parser.parse_args(argv)
    out = Path(args.out).expanduser().resolve()
    if (out / "data").exists():
        sys.stderr.write(f"{out} already holds a run. Give a new folder, so two runs are never mixed.\n")
        return 2
    from fpfa.claude_client import EFFORT_ENV, EFFORTS
    from fpfa.keystore import load_api_key

    if args.effort:
        if args.effort.lower() not in EFFORTS:
            sys.stderr.write("--effort is one of: " + ", ".join(EFFORTS) + "\n")
            return 2
        os.environ[EFFORT_ENV] = args.effort.lower()
    # The key is read where the owner saved it, before the run moves to its own data directory.
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip() or (load_api_key() or "")
    if not key:
        sys.stderr.write("No Anthropic API key. Save one in the app's Settings, or set ANTHROPIC_API_KEY for this run.\n")
        return 2
    steps = tuple(part.strip() for part in args.steps.split(",") if part.strip())
    unknown = [step for step in steps if step not in STEPS]
    if unknown:
        sys.stderr.write("Unknown step: " + ", ".join(unknown) + ". Steps: " + ", ".join(STEPS) + "\n")
        return 2
    if args.job not in JOBS:
        sys.stderr.write("--job is one of: " + ", ".join(JOBS) + "\n")
        return 2
    sys.stdout.write(
        "This calls the live model with your key and is billed.\n"
        f"The run stops starting new work once the usage it can see reaches about ${args.max_usd:.2f}. That is a guard, "
        "not a spending limit: a turn already in flight finishes, the lead's own rounds are only counted when its turn "
        "ends, and a request that fails reports no usage. The bill can be higher. For a hard limit, set one on the key.\n"
        f"Job: {args.job}. Steps: {', '.join(steps)}. Output: {out}\n"
    )
    if not args.yes:
        try:
            if input("Type yes to go on: ").strip().lower() != "yes":
                sys.stdout.write("Nothing was run.\n")
                return 1
        except EOFError:
            sys.stderr.write("No answer. Pass --yes to run without the question.\n")
            return 1
    runner = Runner(out, api_key=key, max_usd=args.max_usd, max_minutes=args.max_minutes, job=args.job,
                    cancel_after=args.cancel_after, log=lambda line: sys.stdout.write(line + "\n"))
    report = runner.run(steps)
    return 0 if not report["stopped"] and not report["counts"][FAIL] else 1


if __name__ == "__main__":
    raise SystemExit(main())
