"""A job part-way through a team's work, written through the same tools the agents use.

The browser test and the screenshots open this state. Nothing here is a
model's output: the rows are a script, and the trace check is given a
stand-in that says Supported to everything, so the tiers shown are the ones
the application's own rules leave standing. It shows what the window does
with a record like this. It does not show what a live team would write.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[2]


def yes_to_everything(**kwargs):
    claims = kwargs["messages"][0]["content"].split("sources.md")[0]
    count = len([line for line in claims.splitlines() if line[:1].isdigit()])
    text = "\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, count + 1))
    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)], usage=None)


def seed_team_state(desk) -> dict:
    """Put a reconciled-in-part design basis on the open job's record. Returns the ids a test needs."""
    from fpfa.calc_tools import ToolSession
    from fpfa.checker import check_record

    record = desk.record
    project_id = desk.project["id"]
    fp = ToolSession(REPO, record=record, project_id=project_id, agent="fp-sprinkler")
    fa = ToolSession(REPO, record=record, project_id=project_id, agent="fa-releasing")
    givens = record.givens(project_id)
    calcs = {row["tool"]: row["id"] for row in record.calcs(project_id) if row["agent"] == "tool-plan"}

    record.log_event(project_id, "plan", {"objective": "Design basis for zone DH-1, with the releasing sequence that trips it", "steps": [
        {"title": "Volume, delivery screen, and trim", "owner": "fp-sprinkler", "status": "done"},
        {"title": "Releasing sequence and supervisory points", "owner": "fa-releasing", "status": "done"},
        {"title": "Settle the releasing time in the screen", "owner": "lead", "status": "doing"},
        {"title": "Trace check", "owner": "checker", "status": "done"},
    ]}, agent="lead")
    for name, slug in (("Lead", "lead"), ("Sprinkler specialist", "fp-sprinkler"), ("Releasing specialist", "fa-releasing")):
        record.set_agent(project_id, name=name, role_slug=slug, status="done")

    first = record.create_handoff(project_id, from_agent="lead", to_agent="fp-sprinkler", kind="delegation",
                                  brief="Size zone DH-1 and screen its water delivery. Record the trim family and the pressures first.")
    asked = record.create_handoff(project_id, from_agent="fp-sprinkler", to_agent="fa-releasing", kind="consult",
                                  brief="What releasing time does the sequence carry from the first detection signal to the solenoid?",
                                  payload={"context": "The form holds 2 s. The screen adds it to the fill time."})
    record.set_handoff(project_id, asked["id"], status="returned", by="fa-releasing",
                       result="Nothing on the record gives it a basis. 2 s is the form's value. Carry it as ASSUMED.")
    second = record.create_handoff(project_id, from_agent="lead", to_agent="fa-releasing", kind="delegation",
                                   brief="Write the releasing sequence for DH-1. Review the sprinkler findings that touch detection or release.")

    cap = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                         "note": "Double-interlock at or under 500 gal carries no delivery-time proof"})
    owner = fp.execute("record_evidence", {"document": "Owner standard", "edition": "2024", "section": "4.3.7",
                                           "note": "The owner wants a dedicated test header on each preaction zone."})
    volume = fp.execute("record_finding", {
        "text": "Zone total is 281.3 gal, inside the 500 gal double-interlock cap, so NFPA 13 asks for no delivery-time proof",
        "label": "calculated", "supports": [calcs["zone_trapped_volume"], calcs["dry_delivery_screen"], cap["id"]]})
    screen = fp.execute("record_finding", {
        "text": "The FM 30 s screen is missed: t_total is 38.1 s at 600 gpm, with 8 s detection and 2 s releasing time",
        "label": "calculated", "supports": [calcs["di_trip_to_water"], givens["t_detect_s"]["id"], givens["t_release_s"]["id"]]})
    trim = fp.execute("record_finding", {
        "text": "Trim family is El/El, provisional. A normally closed solenoid holds the prime",
        "label": "calculated", "supports": [calcs["elect_di_trim"]]})
    header = fp.execute("record_finding", {"text": "Each preaction zone gets its own test header", "label": "OWNER",
                                           "supports": [owner["id"]]})
    old_pressure = fp.execute("record_finding", {"text": "Supervisory pressure is 40 psig", "label": "calculated",
                                                 "supports": [calcs["nitrogen_gate"]]})
    releasing = fa.execute("record_finding", {
        "text": "Release is the detection leg AND P, the pressure drop from sprinkler operation, and not isolated. "
                "Low air is supervisory only",
        "label": "calculated", "supports": [calcs["releasing_truth_table"], trim["id"]]})
    assumed = fa.execute("record_finding", {
        "text": "The 2 s releasing time is the form's value. Nothing on the record gives it a basis",
        "label": "ASSUMED", "supports": [givens["t_release_s"]["id"]]})

    fa.execute("review_finding", {"id": trim["id"], "position": "agree", "note": "The sequence is written for El/El."})
    fp.execute("review_finding", {"id": releasing["id"], "position": "agree"})
    objection = fa.execute("review_finding", {
        "id": screen["id"], "position": "object",
        "note": "The 2 s in this screen has no stated basis. Say it is ASSUMED, or get the releasing panel's output delay."})
    settled = fa.execute("review_finding", {
        "id": old_pressure["id"], "position": "object",
        "note": "State where 40 psig comes from. The trim skill's electric/electric band is lower."})
    pressure = fp.execute("record_finding", {
        "text": "Supervisory fill pressure is 40 psig on the form. The elected trim's listed band has to confirm it",
        "label": "ASSUMED", "supports": [givens["supervisory_psig"]["id"]], "replaces": old_pressure["id"]})

    record.set_handoff(project_id, first["id"], status="returned", by="fp-sprinkler",
                       result="Sized and screened. The 30 s insurer screen is missed. Trim is El/El, provisional.")
    record.set_handoff(project_id, second["id"], status="returned", by="fa-releasing",
                       result="Sequence written for El/El. I object to the 2 s releasing time in the screen: no basis.")

    ask = fp.execute("open_question", {"text": "What is the trim volume on the elected valve's data sheet?", "to": "designer"})
    rfi = fa.execute("open_question", {"text": "Does the owner accept one detection zone for the detection leg?"})
    fp.execute("open_question", {"text": "Which listed program, or a witnessed test, proves the 30 s delivery?"})

    check_record(REPO, record, project_id, yes_to_everything)
    desk._refresh_team()
    return {
        "project": project_id, "ask": ask["id"], "rfi": rfi["id"], "objection": objection["id"], "settled": settled["id"],
        "findings": {"volume": volume["id"], "screen": screen["id"], "trim": trim["id"], "header": header["id"],
                     "releasing": releasing["id"], "assumed": assumed["id"], "pressure": pressure["id"]},
    }
