"""Run the evaluation path against the live model and write down what happened.

    python -m fpfa.live_eval --out <folder> [--max-usd 25] [--effort high] [--steps request,reopen,...]
    Cynosure.exe --live-eval <folder>            (the packaged app; same options)

This drives the same Desk the window runs, with no window, through the steps
in docs/live-evaluation.md: a plain request that names no specialist, a
relaunch, the designer's answers, an input that changes, a turn cancelled
part-way and picked up again, and the export. After each step it reads the
project record and writes what it found: which checks the run met, which it
did not, and which it could not observe. It writes the thread, the status,
the usage report, the Design Basis, and the record beside the report so a
person can read them.

What it is for. A scripted test can show that the application carries such
a job. Only a live run shows whether the model plans, asks, objects, and
revises when it is handed a plain objective. The checks here are the things
a program can tell from the record. They do not judge whether the
engineering is right or the reply is useful; the report lists what a person
has to read to decide that.

What it costs. Every step calls the model with the owner's key and is
billed. --max-usd stops the run between steps, and cancels a step from the
outside when the delegations it has closed so far already exceed what is
left. The cap is a guard, not a meter: a turn's own rounds are only priced
when the turn ends. Nothing here runs unless someone asks for it by name.

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

STEPS = ("request", "reopen", "answer", "change", "interrupt", "export")
REQUEST = (
    "We're laying out the preaction zone for data hall 1. Can it meet the insurer's water delivery time, "
    "and what releasing sequence goes with it? I need a design basis I can hand to the engineer."
)
CHANGE = (
    "One more thing: the pump test gave us 750 gpm at the riser, not the 600 on the form. "
    "Does that change the answer?"
)
CHANGED_INPUT = ("q_fill_gpm", 750.0)
INTERRUPTED = (
    "Write me a short summary of this design basis for the engineer's cover email, and say what is still open."
)
RESUME = "That was cut off before it finished. Pick it up and finish it."
DEFAULT_ANSWER = (
    "I do not have that yet. Carry your assumption, say that it is one, and keep the question open for the engineer."
)
PASS, FAIL, NOT_SEEN, INFO = "met", "NOT MET", "not observed", "info"
_LOW_AIR_AS_RELEASE = re.compile(
    r"AND\s+low[_ -]?air\b|low[- ]air\s+(?:is|as)\s+the\s+second\s+(?:leg|interlock|event|input)", re.IGNORECASE)


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
    ):
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
        """Dollars the delegations and checks closed since a turn began add up to. A lower bound."""
        from fpfa.usage_report import cost, normalize

        total = 0.0
        events = self.desk.call(self.desk.record.events_by_kind, self.project_id, ("delegation", "record_check"))
        for event in events:
            if int(event.get("seq") or 0) > since_seq:
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
        from fpfa import coherence
        from fpfa.checker import check_is_current, tier_counts

        desk = self.desk
        desk.call(lambda: desk.ask_claude.set(False))
        desk.call(desk.start_sample_di)
        desk.pump()
        self.project_id = desk.call(lambda: desk.project["id"])
        turn = self._turn("request", REQUEST)
        snap = self._snapshot()
        events = desk.call(desk.record.events_by_kind, self.project_id, ("plan", "delegation", "consult", "record_check", "reply_audit"))
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

        reviews = snap["reviews"]
        consults = [row for row in snap["handoffs"] if row.get("kind") == "consult"]
        authors = {row["id"]: row.get("agent") for row in snap["findings"] + snap["retired_findings"]}
        calc_by = {row["id"]: row.get("agent") for row in snap["calcs"]}
        crossed = [row for row in snap["findings"]
                   if any(authors.get(ident, calc_by.get(ident, row["agent"])) not in (row["agent"], "tool-plan", "", None)
                          for ident in row.get("supports") or [])]
        self.check("request", "B", "One specialist used the other's work: a question, or a finding that rests on the other's row",
                   PASS if consults or crossed else NOT_SEEN,
                   f"{len(consults)} consult{'s' if len(consults) != 1 else ''}, {len(crossed)} finding{'s' if len(crossed) != 1 else ''} citing the other's row")
        self.check("request", "B", "A specialist took a position on a finding it did not write",
                   PASS if reviews else NOT_SEEN,
                   f"{sum(1 for row in reviews if row['position'] == 'agree')} agree, "
                   f"{sum(1 for row in reviews if row['position'] == 'object')} object")
        objections = [row for row in reviews if row["position"] == "object"]
        still_open = [row for row in objections if row["status"] == "open"]
        if objections:
            self.check("request", "B", "Every objection has an end: revised, settled with a decision, or escalated as a question",
                       PASS if not still_open else FAIL,
                       "; ".join(f"{row['agent']}: {row['status']}" for row in objections)[:300])
        else:
            self.check("request", "B", "Every objection has an end", NOT_SEEN, "no objection was raised")
        analysis = coherence.analyze(snap)
        loose = [row for row in snap["findings"] if analysis["findings"][row["id"]].get("notes")]
        self.check("request", "B", "No finding rests on a value other than the project input without saying so", INFO,
                   f"{len(loose)} finding{'s' if len(loose) != 1 else ''} on an alternative value")

        self.check("request", "D", "A trace check judged the findings as they stand",
                   PASS if snap["findings"] and check_is_current(snap) else (NOT_SEEN if not snap["findings"] else FAIL),
                   json.dumps(tier_counts(snap)) if snap["findings"] else "no findings on the record")
        self._check_reply("request", turn)
        asks = [row for row in snap["questions"] if row["status"] == "open" and row.get("audience") == "designer"]
        self.check("request", "E", "What the team needs from the designer is asked as a question", INFO,
                   f"{len(asks)} for the designer, "
                   f"{sum(1 for row in snap['questions'] if row['status'] == 'open') - len(asks)} for the engineer")
        self._before_relaunch = desk.call(lambda: {key: desk.team.get(key) for key in ("plan", "asks", "rfis", "tiers", "strip")})
        self._before_relaunch["findings"] = desk.call(lambda: [row["text"] for row in desk.team.get("findings") or []])

    def _check_reply(self, step: str, turn: dict) -> None:
        """What the application found when it looked this turn's reply up, and the releasing wording."""
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
        hits = _LOW_AIR_AS_RELEASE.findall(reply or "")
        self.check(step, "D", "The reply does not name low air as a release input", PASS if not hits else FAIL,
                   "; ".join(hits)[:200])

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
        from fpfa import inputs

        desk = self.desk
        name, value = CHANGED_INPUT
        turn = self._turn("change", CHANGE)
        snap = self._snapshot()
        given = desk.call(desk.record.givens, self.project_id).get(name)
        recorded = given is not None and inputs.decode(given["value"]) == value
        self.check("change", "C", "The lead put the value the designer stated on the record",
                   PASS if recorded and given.get("agent") == "lead" else FAIL,
                   f"{name} is {inputs.show(name, inputs.decode(given['value'])) if given else 'missing'}"
                   f"{' (' + str(given.get('source')) + ')' if given else ''}")
        stale = desk.call(lambda: list(desk.team.get("stale") or []))
        by_agents = [row for row in stale if row["by"] not in ("tool-plan", "tool plan", "")]
        self.check("change", "C", "Nothing a specialist wrote is left resting on the old value",
                   PASS if recorded and not by_agents else FAIL,
                   "; ".join(f"{row['kind']} by {row['by']}: {row['text'][:60]}" for row in by_agents)[:400]
                   or f"{len(snap['retired_findings'])} finding{'s' if len(snap['retired_findings']) != 1 else ''} replaced or withdrawn so far")
        self._check_reply("change", turn)
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

    def step_export(self) -> None:
        """Run the zone again if the form moved, run the trace check if it is behind, and write the documents."""
        from fpfa.checker import NOT_STANDARD, check_is_current
        from fpfa.usage_report import report_text

        desk = self.desk
        if desk.call(desk.run_changes):
            self.log("export: the form changed after the last run; running the zone again (no model call)")
            desk.call(desk.start_zone_run)
            self._wait_idle()
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
                       PASS if NOT_STANDARD in text and "How far each statement was taken" in text else FAIL)
            hits = _LOW_AIR_AS_RELEASE.findall(text)
            self.check("export", "D", "The draft does not name low air as a release input", PASS if not hits else FAIL,
                       "; ".join(hits)[:200])
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
        report = {
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
            f"- App {report['app']}, content {report['content']}, model {report['model']}, effort {report['effort']}",
            f"- Machine: {report['platform']}, Python {report['python']}",
            f"- Steps run: {', '.join(steps)}",
            f"- Time: {clock(seconds) or '0 s'} in all. Estimated cost: ${spent:.2f} at the list prices of {RATES_DATE}. "
            "An estimate, not a bill.",
        ]
        if stopped:
            lines.append(f"- **The run stopped early:** {stopped}")
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
            "",
            "A check marked not observed means the run gave no chance to see it, or the model did not do it. "
            "Two specialists that never touch each other's work show up here as not observed, not as a failure of the app. "
            "That is the finding.",
        ]
        (self.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.log(f"report written to {self.out / 'report.md'}")
        return report


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
    parser.add_argument("--max-usd", type=float, default=25.0, help="Stop when the estimated spend reaches this. Default 25")
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
    sys.stdout.write(
        f"This calls the live model with your key and is billed. It stops at about ${args.max_usd:.2f}.\n"
        f"Steps: {', '.join(steps)}. Output: {out}\n"
    )
    if not args.yes:
        try:
            if input("Type yes to go on: ").strip().lower() != "yes":
                sys.stdout.write("Nothing was run.\n")
                return 1
        except EOFError:
            sys.stderr.write("No answer. Pass --yes to run without the question.\n")
            return 1
    runner = Runner(out, api_key=key, max_usd=args.max_usd, max_minutes=args.max_minutes,
                    cancel_after=args.cancel_after, log=lambda line: sys.stdout.write(line + "\n"))
    report = runner.run(steps)
    return 0 if not report["stopped"] and not report["counts"][FAIL] else 1


if __name__ == "__main__":
    raise SystemExit(main())
