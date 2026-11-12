"""The trace check, the tier each finding earns, and what the Design Basis prints about them.

What these tests hold the application to:

- A cite to a standard is read in the content pack's own reviewed notes,
  not in the note its author wrote beside it. A wrong claim with a matching
  author's note is caught.
- A figure with a unit in a claim has to be in the rows the claim cites,
  whatever the checker said.
- The four tiers are derived from the record. The export prints them and
  never says a standard was opened.

Every model call is a stand-in. The checker here says Supported to every
claim, which is the worst case: only the application's own rules are left.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from test_coherence import _change, _run_plan, _seed_inputs  # noqa: E402
from test_design_basis import _docx_text  # noqa: E402
from test_team import _record  # noqa: E402


def yes_to_everything(**kwargs):
    """A checker that marks every claim Supported."""
    claims = kwargs["messages"][0]["content"].split("sources.md")[0]
    count = len([line for line in claims.splitlines() if line[:1].isdigit()])
    text = "\n".join(f'{n}. Supported. Cite: "row"' for n in range(1, count + 1))
    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)], usage=None)


def _pack(notes: dict[str, str]) -> Path:
    """A content pack with only the notes given, by path under the pack root."""
    root = Path(tempfile.mkdtemp(prefix="fpfa-pack-"))
    for rel, text in notes.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


NOTE = (
    "# Zone size\n\n"
    "Double-interlock size, NFPA 13-2025 §8.3.2.3.1.1: at most 500 gallons with no delivery-time proof. "
    "There is no 750 gallon path on double-interlock. A quick-opening device does not raise the cap (§8.3.2.3.2).\n\n"
    "The 2022 edition numbers the same rule NFPA 13-2022 §8.3.2.3.1.1 and holds it at 500 gallons.\n\n"
    "Releasing circuits, NFPA 72-2025 §23.11.5.2: supervised for opens and grounds. §14.2.10 is the test plan. "
    "FM DS 5-32 §2.4.1.1 ranks the system types.\n"
)


class TraceCiteTests(unittest.TestCase):
    def test_a_section_is_found_with_its_neighbours_its_file_and_its_line(self):
        from fpfa.corpus_search import trace_cite

        root = _pack({"corpus/fp/zone-size.md": NOTE, "corpus/README.md": "NFPA 13-2025 §8.3.2.3.1.1 is indexed here."})
        found = trace_cite(root, "NFPA 13", "2025", "8.3.2.3.1.1")
        self.assertEqual(len(found), 1, "a README is an index, not a note")
        self.assertEqual((found[0]["path"], found[0]["line"]), ("corpus/fp/zone-size.md", 3))
        self.assertIn("at most 500 gallons", found[0]["sentence"])
        # The reader is shown the sentences around it. The figures the cite can carry are only the ones the
        # note gives for this section: not the next sentence's, and not another section's in the same sentence.
        self.assertIn("There is no 750 gallon path", found[0]["text"])
        self.assertNotIn("750", found[0]["scope"])
        self.assertIn("500 gallons", found[0]["scope"])
        mixed = _pack({"corpus/fp/caps.md": (
            "Flags: double-interlock cap 500 gallons (NFPA 13-2025 §8.3.2.3.1.1); dry-pipe quick-opening path "
            "750 gallons (NFPA 13-2025 §8.2.4.2.2); neither is an exemption by itself.\n\n"
            "Hose and duration, NFPA 13-2025 Table 19.2.3.1.2: ordinary hazard 250 gpm for 60 or 90 minutes; "
            "extra hazard 500 gpm for 90 or 120 minutes.\n")})
        cap = trace_cite(mixed, "NFPA 13", "2025", "8.3.2.3.1.1")[0]
        self.assertIn("500 gallons", cap["scope"])
        self.assertNotIn("750", cap["scope"], "that figure is the pack's for another section")
        self.assertIn("neither is an exemption", cap["scope"], "a clause with no section of its own belongs to the sentence")
        table = trace_cite(mixed, "NFPA 13", "2025", "Table 19.2.3.1.2")[0]
        self.assertIn("extra hazard 500 gpm for 90 or 120 minutes", table["scope"])
        # However the caller writes the document and the section.
        for document, section in (("NFPA 13-2025", "§8.3.2.3.1.1"), ("nfpa 13", "8.3.2.3.1.1(A)"), ("NFPA13", "Section 8.3.2.3.1.1")):
            self.assertEqual(len(trace_cite(root, document, "2025", section)), 1, f"{document} {section}")

    def test_a_longer_section_another_edition_and_another_document_do_not_match(self):
        from fpfa.corpus_search import trace_cite

        root = _pack({"corpus/fp/zone-size.md": NOTE})
        # 8.3.2.3 is not 8.3.2.3.1.1, and 8.3.2.3.1.1 is not 8.3.2.3.1.12.
        self.assertEqual(trace_cite(root, "NFPA 13", "2025", "8.3.2.3"), [])
        self.assertEqual(trace_cite(root, "NFPA 13", "2025", "8.3.2.3.1"), [])
        # The 2022 line is found for 2022 and not handed over for 2019.
        self.assertEqual([item["line"] for item in trace_cite(root, "NFPA 13", "2022", "8.3.2.3.1.1")], [5])
        self.assertEqual(trace_cite(root, "NFPA 13", "2019", "8.3.2.3.1.1"), [])
        # NFPA 130 is not NFPA 13. A section belongs to the document named last in its paragraph.
        self.assertEqual(trace_cite(root, "NFPA 130", "2025", "8.3.2.3.1.1"), [])
        self.assertEqual(len(trace_cite(root, "NFPA 72", "2025", "23.11.5.2")), 1)
        self.assertEqual(len(trace_cite(root, "NFPA 72", "2025", "14.2.10")), 1, "the next sentence is still NFPA 72")
        self.assertEqual(trace_cite(root, "NFPA 72", "2025", "2.4.1.1"), [], "that sentence names the insurer sheet")
        self.assertEqual(len(trace_cite(root, "FM DS 5-32", "", "2.4.1.1")), 1)
        self.assertEqual(len(trace_cite(root, "FM Data Sheet 5-32", "2026", "2.4.1.1")), 1)
        # Nothing to look up is nothing found.
        self.assertEqual(trace_cite(root, "", "2025", "8.3.2.3.1.1"), [])
        self.assertEqual(trace_cite(root, "NFPA 13", "2025", ""), [])
        self.assertEqual(trace_cite(root, "NFPA 13", "2025", "chapter 8"), [])

    def test_the_lookup_follows_a_pack_update(self):
        from fpfa.corpus_search import trace_cite

        root = _pack({"corpus/fp/zone-size.md": NOTE})
        self.assertEqual(trace_cite(root, "NFPA 25", "2023", "13.4.3"), [])
        note = root / "corpus" / "fp" / "itm.md"
        note.write_text("Trip tests, NFPA 25-2023 §13.4.3: full flow every three years.\n", encoding="utf-8")
        stamp = time.time() + 5
        os.utime(note, (stamp, stamp))
        self.assertEqual(len(trace_cite(root, "NFPA 25", "2023", "13.4.3")), 1)

    def test_the_real_pack_holds_the_sections_the_sample_zone_leans_on(self):
        from fpfa.corpus_search import trace_cite

        cap = trace_cite(REPO, "NFPA 13", "2025", "8.3.2.3.1.1")
        self.assertTrue(cap)
        self.assertTrue(all(item["path"].startswith(("corpus/", "specs/")) for item in cap))
        self.assertTrue(any("500" in item["text"] for item in cap))
        self.assertTrue(trace_cite(REPO, "NFPA 13", "2025", "19.2.3.1.3"))
        self.assertEqual(trace_cite(REPO, "NFPA 13", "2025", "99.99.99"), [])


class FigureTests(unittest.TestCase):
    def test_a_figure_is_a_number_with_an_engineering_unit(self):
        from fpfa.checker import _missing_figures, figures

        self.assertEqual(figures("NFPA 13-2025 §8.3.2.3.1.1 caps a double-interlock zone at 500 gal"), ["500"])
        self.assertEqual(figures("Zone total 281.3 gal fills in 28.1 s at 600 gpm; t_total 38.1 s misses 30 s"),
                         ["281.3", "28.1", "600", "38.1", "30"])
        self.assertEqual(figures("Duration volume 38,400 gal over 60 min at 0.20 gpm/ft2 on 1,950 ft²"),
                         ["38400", "60", "0.2", "1950"])
        self.assertEqual(figures("Fill 3.41 scfm at 40 psig; the switch is 15 psi; area increase 30 percent"),
                         ["3.41", "40", "15", "30"])
        # Counts, sizes, section numbers, and record ids are not figures the check verifies.
        self.assertEqual(figures("6 true rows of 32; 4 in. cross main; FM DS 5-32 §2.4.1.1; see [4cde43d71dbb4e34]"), [])
        self.assertEqual(figures("Table 19.2.3.1.2 gives the band; s19.2.3.1.3 the supervision"), [])
        self.assertEqual(_missing_figures("The cap is 500 gal", ["500"]), [])
        self.assertEqual(_missing_figures("The cap is 750 gal", ["500"]), ["750 gal"])
        # A row may hold a share as a fraction.
        self.assertEqual(_missing_figures("Area increase is 30 percent", ["0.3"]), [])
        self.assertEqual(_missing_figures("Area increase is 30%", ["0.25"]), ["30 %"])


class TraceCheckTests(unittest.TestCase):
    def test_a_wrong_claim_is_not_supported_by_a_matching_note_its_author_wrote(self):
        """The planted error: 750 gallons, with a note beside the cite that says 750 too."""
        from fpfa.checker import PACK_MARK, assurance, check_record

        record = _record()
        _seed_inputs(record)
        cite = record.record_evidence(
            "job1", document="NFPA 13", edition="2025", section="8.3.2.3.1.1", status="held", agent="fp-sprinkler",
            note="A double-interlock zone of up to 750 gallons needs no delivery-time proof.",
        )
        wrong = record.record_finding("job1", agent="fp-sprinkler", label="CODE", supports=[cite["id"]],
                                      text="A double-interlock zone up to 750 gal needs no delivery-time proof")
        right_cite = record.record_evidence(
            "job1", document="NFPA 13", edition="2025", section="8.3.2.3.1.1", status="held", agent="fa-releasing",
            note="The cap is five hundred.",
        )
        right = record.record_finding("job1", agent="fa-releasing", label="CODE", supports=[right_cite["id"]],
                                      text="A double-interlock zone up to 500 gal needs no delivery-time proof")
        outcome = check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        # The checker was shown the pack's note, with where it is. It was not shown the author's.
        self.assertIn(PACK_MARK, rows[wrong["id"]]["cite"])
        self.assertIn("corpus/", rows[wrong["id"]]["cite"])
        self.assertNotIn("up to 750 gallons needs no delivery-time proof", rows[wrong["id"]]["cite"])
        self.assertEqual(rows[wrong["id"]]["verdict"], "Not supported")
        self.assertEqual(rows[wrong["id"]]["reason"], "figure not in the rows it cites: 750 gal")
        self.assertEqual(rows[right["id"]]["verdict"], "Supported")
        self.assertEqual(rows[right["id"]]["basis"], "source")
        self.assertEqual(rows[right["id"]]["sources"][0]["kind"], "pack")
        self.assertTrue(rows[right["id"]]["sources"][0]["where"][0].startswith("corpus/"))
        tiers = assurance(record.snapshot("job1"))
        self.assertEqual(tiers[wrong["id"]]["tier"], "open")
        self.assertIn("750 gal", tiers[wrong["id"]]["reasons"][0])
        self.assertEqual(tiers[right["id"]]["tier"], "source")

    def test_a_cite_the_pack_does_not_hold_rests_on_its_author_and_is_reported_that_way(self):
        from fpfa.checker import AUTHOR_MARK, assurance, check_record, tier_counts

        record = _record()
        _seed_inputs(record)
        said_back = record.record_evidence("job1", document="Owner standard", edition="2024", section="4.2.1",
                                           note="Releasing circuits are monitored at the panel", agent="fa-releasing")
        echo = record.record_finding("job1", agent="fa-releasing", label="OWNER", supports=[said_back["id"]],
                                     text="Releasing circuits are monitored at the panel")
        fuller = record.record_evidence("job1", document="Owner standard", edition="2024", section="4.3.7",
                                        note="The owner asks for a keyed bypass with a supervisory signal on every releasing zone.",
                                        agent="fa-releasing")
        real = record.record_finding("job1", agent="fa-releasing", label="OWNER", supports=[fuller["id"]],
                                     text="Each releasing zone has a keyed bypass that raises a supervisory signal")
        not_pulled = record.record_evidence("job1", document="Owner standard", edition="2024", section="9.1.1",
                                            note="", status="NOT PULLED", agent="fa-releasing")
        open_cite = record.record_finding("job1", agent="fa-releasing", label="OWNER", supports=[not_pulled["id"]],
                                          text="The owner limits a zone to one data hall")
        bare = record.record_finding("job1", agent="fa-releasing", label="PRACTICE", text="Low air alone never releases")
        outcome = check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        self.assertIn(AUTHOR_MARK, rows[echo["id"]]["cite"])
        self.assertEqual((rows[echo["id"]]["verdict"], rows[echo["id"]]["reason"]),
                         ("Not supported", "its author's note only repeats the claim"))
        self.assertEqual((rows[real["id"]]["verdict"], rows[real["id"]]["basis"]), ("Supported", "author"))
        self.assertEqual(rows[open_cite["id"]]["verdict"], "Source not found")
        self.assertEqual(rows[bare["id"]]["verdict"], "Source not found")
        self.assertEqual((outcome["supported"], outcome["on_source"], outcome["on_author"]), (1, 0, 1))
        self.assertIn("0 against a calculation record, a content-pack note, or a project input, 1 against a cite their author wrote",
                      outcome["status_line"])
        snapshot = record.snapshot("job1")
        tiers = assurance(snapshot)
        self.assertEqual(tiers[real["id"]]["tier"], "reviewed")
        self.assertEqual(tiers[echo["id"]]["tier"], "open")
        self.assertEqual(tiers[open_cite["id"]]["tier"], "open")
        self.assertEqual(tier_counts(snapshot), {"source": 0, "checker": 0, "reviewed": 1, "stated": 0, "open": 3})

    def test_calc_records_project_inputs_and_other_findings_as_sources(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import INPUT_MARK, assurance, check_record

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        givens = record.givens("job1")
        on_calc = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[screen["record_id"]],
                                        text="Fill takes 28.1 s at 600 gpm and t_total is 38.1 s against a 30 s limit")
        misquoted = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[screen["record_id"]],
                                          text="t_total is 29.5 s, inside the 30 s limit")
        on_input = record.record_finding("job1", agent="fp-sprinkler", label="calculated",
                                         supports=[givens["area_increase"]["id"], givens["base_area_ft2"]["id"]],
                                         text="The form carries a 30 percent increase on 1,500 ft2")
        assumed = record.record_finding("job1", agent="fa-releasing", label="ASSUMED", supports=[givens["t_release_s"]["id"]],
                                        text="The 2 s releasing time is the form's value and has no stated basis")
        chained = record.record_finding("job1", agent="lead", label="use best judgment", supports=[on_calc["id"]],
                                        text="The 30 s insurer screen is missed at this fill flow")
        outcome = check_record(REPO, record, "job1", yes_to_everything)
        rows = {row["finding_id"]: row for row in outcome["rows"]}
        self.assertEqual(rows[on_calc["id"]]["verdict"], "Supported")
        self.assertEqual(rows[on_calc["id"]]["sources"][0]["text"], "di_trip_to_water (calculation record)")
        self.assertEqual(rows[misquoted["id"]]["verdict"], "Not supported")
        self.assertIn("29.5 s", rows[misquoted["id"]]["reason"])
        self.assertIn(f"{INPUT_MARK} area_increase: 0.3", rows[on_input["id"]]["cite"])
        self.assertEqual((rows[on_input["id"]]["verdict"], rows[on_input["id"]]["basis"]), ("Supported", "source"))
        self.assertEqual(rows[assumed["id"]]["verdict"], "Supported")
        self.assertEqual((rows[chained["id"]]["verdict"], rows[chained["id"]]["basis"]), ("Supported", "author"),
                         "a finding that rests on a finding adds no independent source")
        tiers = assurance(record.snapshot("job1"))
        self.assertEqual(tiers[on_calc["id"]]["tier"], "source")
        self.assertEqual(tiers[on_input["id"]]["tier"], "source")
        # Consistent with what it cites, and still an assumption by its own label: the engineer confirms it.
        self.assertEqual(tiers[assumed["id"]]["tier"], "open")
        self.assertIn("It is an assumption.", tiers[assumed["id"]]["reasons"][0])
        self.assertEqual(tiers[chained["id"]]["tier"], "open")
        self.assertIn("a judgment the tools did not return", tiers[chained["id"]]["reasons"][0])

    def test_an_out_of_date_finding_is_not_judged_and_the_gate_waits_for_it(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import STALE_MARK, assurance, check_line, check_record, export_gate

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[screen["record_id"]],
                                        text="t_total is 38.1 s against a 30 s limit")
        self.assertIn("no trace check has judged", export_gate(record, "job1"))
        self.assertTrue(check_record(REPO, record, "job1", yes_to_everything)["all_supported"])
        self.assertEqual(export_gate(record, "job1"), "")
        self.assertTrue(check_line(record.snapshot("job1")).startswith("Trace check: all 1 findings"))

        _change(record, "q_fill_gpm", 750)
        gate = export_gate(record, "job1")
        self.assertIn("out of date", gate)
        self.assertIn("q_fill_gpm changed from 600 gpm to 750 gpm", gate)
        self.assertIn("/status lists them", gate)
        self.assertEqual(assurance(record.snapshot("job1"))[finding["id"]]["tier"], "open")
        self.assertIn("Out of date:", assurance(record.snapshot("job1"))[finding["id"]]["reasons"][0])
        again = check_record(REPO, record, "job1", yes_to_everything)
        self.assertIn(STALE_MARK, again["rows"][0]["cite"])
        self.assertEqual((again["rows"][0]["verdict"], again["rows"][0]["reason"]),
                         ("Source not found", "its basis changed; it is out of date"))
        self.assertIn("out of date", export_gate(record, "job1"), "a fresh check does not make an old figure current")

        # Run the zone again and replace the finding on the new screen: the gate asks for a check, then opens.
        _run_plan(record, dict(di, q_fill_gpm=750), basis)
        fresh = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 750, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[fresh["record_id"]],
                              text="t_total is 32.5 s against a 30 s limit", replaces=finding["id"])
        self.assertEqual(export_gate(record, "job1"), "Findings changed after the last trace check. Run it again.")
        self.assertTrue(check_record(REPO, record, "job1", yes_to_everything)["all_supported"])
        self.assertEqual(export_gate(record, "job1"), "")

    def test_an_objection_holds_a_supported_finding_open_until_it_ends(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import assurance, check_record

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        finding = fp.execute("record_finding", {"text": "t_total is 38.1 s against a 30 s limit", "label": "calculated",
                                                "supports": [screen["record_id"]]})
        check_record(REPO, record, "job1", yes_to_everything)
        self.assertEqual(assurance(record.snapshot("job1"))[finding["id"]]["tier"], "source")
        review = fa.execute("review_finding", {"id": finding["id"], "position": "object", "note": "The 2 s has no basis."})
        held = assurance(record.snapshot("job1"))[finding["id"]]
        self.assertEqual(held["tier"], "open")
        self.assertEqual(held["reasons"], ["fa-releasing objects: The 2 s has no basis."])
        record.close_review("job1", review["id"], status="escalated", resolution="Sent to the engineer.", by="lead")
        self.assertIn("(escalated)", assurance(record.snapshot("job1"))[finding["id"]]["reasons"][0])
        fa.execute("review_finding", {"id": finding["id"], "position": "agree", "note": "Carried as ASSUMED elsewhere."})
        settled = assurance(record.snapshot("job1"))[finding["id"]]
        self.assertEqual((settled["tier"], settled["agreed_by"]), ("source", ["fa-releasing"]))

    def test_the_checker_is_blind_and_is_never_called_for_what_the_application_can_decide(self):
        from fpfa.checker import check_record

        record = _record()
        _seed_inputs(record)
        record.record_finding("job1", agent="fp-sprinkler", label="PRACTICE", text="Nitrogen is a corrosion decision")
        seen = {}

        def create(**kwargs):
            seen.update(kwargs)
            return yes_to_everything(**kwargs)

        outcome = check_record(REPO, record, "job1", create)
        self.assertNotIn("tools", seen)
        user = seen["messages"][0]["content"]
        self.assertNotIn("fp-sprinkler", user, "the checker is not told who wrote a claim")
        self.assertNotIn("PRACTICE", user)
        self.assertIn("1. Nitrogen is a corrosion decision.", user)
        self.assertEqual(outcome["rows"][0]["verdict"], "Source not found")
        self.assertIs(outcome["checked_against_standard"], False)
        self.assertIn("The standards were not opened.", outcome["status_line"])
        self.assertIn("Kinds of cite on a project record", seen["system"] if isinstance(seen["system"], str) else str(seen["system"]))


class DesignBasisTierTests(unittest.TestCase):
    def test_the_export_sorts_findings_by_how_far_each_was_taken_and_shows_what_happened(self):
        from fpfa.calc_tools import ToolSession
        from fpfa.checker import NOT_STANDARD, TIER_TITLE, check_record
        from fpfa.design_basis_docx import STALE_CHECK_LINE, write_design_basis

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        record.log_event("job1", "plan", {"objective": "Design basis for zone DH-1", "steps": [{"title": "Screen", "status": "done"}]},
                         agent="lead")
        fp = ToolSession(REPO, record=record, project_id="job1", agent="fp-sprinkler")
        fa = ToolSession(REPO, record=record, project_id="job1", agent="fa-releasing")
        lead = ToolSession(REPO, record=record, project_id="job1", agent="lead")
        screen = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 600, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        what_if = fp.execute("di_trip_to_water", {"v_gal": 281.3, "q_fill_gpm": 900, "t_detect_s": 8, "t_release_s": 2, "t_exhaust_s": 0, "basis": "FM", "system_type": "di"})
        cap = fp.execute("record_evidence", {"document": "NFPA 13", "edition": "2025", "section": "8.3.2.3.1.1",
                                             "note": "DI at or under 500 gal needs no delivery-time proof"})
        owner = fp.execute("record_evidence", {"document": "Owner standard", "edition": "2024", "section": "4.3.7",
                                               "note": "The owner wants each zone to have its own test header."})
        first = fp.execute("record_finding", {"text": "t_total is 38.1 s against a 30 s limit, with no releasing delay checked",
                                              "label": "calculated", "supports": [screen["record_id"]]})
        on_pack = fp.execute("record_finding", {"text": "A double-interlock zone up to 500 gal needs no delivery-time proof",
                                                "label": "CODE", "supports": [cap["id"]]})
        on_author = fp.execute("record_finding", {"text": "Each zone gets a dedicated test header", "label": "OWNER",
                                                  "supports": [owner["id"]]})
        wrong = fp.execute("record_finding", {"text": "At 900 gpm t_total is 25.0 s", "label": "calculated",
                                              "supports": [what_if["record_id"]]})
        asked = fp.execute("open_question", {"text": "What is the trim volume from the valve sheet?", "to": "designer"})
        fp.execute("open_question", {"text": "Does the owner accept one detection zone?"})
        objection = fa.execute("review_finding", {"id": first["id"], "position": "object",
                                                  "note": "Say that the 2 s releasing time is the form's value."})
        fa.execute("review_finding", {"id": on_pack["id"], "position": "agree"})
        revised = fp.execute("record_finding", {"text": "t_total is 38.1 s against a 30 s limit, on the form's 2 s releasing time",
                                                "label": "calculated", "supports": [screen["record_id"]], "replaces": first["id"]})
        record.create_handoff("job1", from_agent="fp-sprinkler", to_agent="fa-releasing", kind="consult",
                              brief="What releasing time does the sequence carry?")
        check_record(REPO, record, "job1", yes_to_everything)
        late = lead.execute("record_finding", {"text": "The team recommends a listed calculation", "label": "use best judgment"})
        out = Path(tempfile.mkdtemp(prefix="fpfa-tier-out-")) / "basis.docx"
        write_design_basis(out, {"name": "DH-1"}, record.snapshot("job1"))
        text = _docx_text(out)

        self.assertIn("Objective the team worked to: Design basis for zone DH-1", text)
        self.assertIn(NOT_STANDARD, text)
        self.assertIn(STALE_CHECK_LINE, text, "a finding was written after the check")
        # The counts by tier, then each finding under the heading it earned.
        self.assertIn(f"{TIER_TITLE['source']} | 2 |", text)
        self.assertIn(f"{TIER_TITLE['reviewed']} | 1 |", text)
        self.assertIn(f"{TIER_TITLE['stated']} | 0 |", text)
        self.assertIn(f"{TIER_TITLE['open']} | 2 |", text)
        self.assertIn(f"{TIER_TITLE['source']} (2)", text)
        row = next(line for line in text.splitlines() if line.startswith("A double-interlock zone up to 500 gal"))
        self.assertIn("| CODE | fp-sprinkler | NFPA 13-2025 §8.3.2.3.1.1 [", row)
        self.assertIn("Trace check: Supported. Against content-pack note: NFPA 13-2025 §8.3.2.3.1.1 (corpus/", row)
        self.assertIn("| fa-releasing |", row, "who agreed with it")
        row = next(line for line in text.splitlines() if line.startswith("Each zone gets a dedicated test header"))
        self.assertIn("its author's own note; the section is not in the content pack: Owner standard-2024 §4.3.7", row)
        row = next(line for line in text.splitlines() if line.startswith("At 900 gpm t_total is 25.0 s"))
        self.assertIn("Trace check: Not supported.", row)
        self.assertIn("figure not in the rows it cites: 25 s", row)
        self.assertIn("Alternative: di_trip_to_water", row)
        row = next(line for line in text.splitlines() if line.startswith("The team recommends a listed calculation"))
        self.assertIn("No trace check has judged it. It is a judgment the tools did not return", row)
        # The alternative calc is marked where it is listed.
        self.assertIn("ALTERNATIVE: ran on q_fill_gpm", text)
        self.assertIn("Not the design case.", text)
        # The objection, and how it ended.
        row = next(line for line in text.splitlines() if "Say that the 2 s releasing time is the form's value." in line)
        self.assertIn("| fp-sprinkler | fa-releasing | objects |", row)
        self.assertIn(f"The finding was revised by fp-sprinkler: see [{revised['id']}].", row)
        self.assertIn("| fa-releasing | agrees |", text)
        # Questions are split by who has to answer.
        designer = text.index("The team needs these from the designer before the work they block can go on:")
        engineer = text.index("For the engineer of record, the owner, or the authority:")
        self.assertLess(designer, text.index("What is the trim volume from the valve sheet?"))
        self.assertLess(engineer, text.index("Does the owner accept one detection zone?"))
        self.assertLess(text.index("What is the trim volume from the valve sheet?"), engineer)
        # What passed between the agents, by kind.
        self.assertIn("consult | fp-sprinkler | fa-releasing | What releasing time does the sequence carry?", text)
        # History: the replaced finding is kept and shown as replaced, not as current.
        self.assertIn(f"Finding by fp-sprinkler, replaced by [{revised['id']}]: t_total is 38.1 s against a 30 s limit, "
                      "with no releasing delay checked", text)
        self.assertEqual(text.count("with no releasing delay checked"), 2, "once in the review log, once in the history")
        self.assertTrue(objection["id"] and asked["id"] and on_author["id"] and wrong["id"] and late["id"])

    def test_out_of_date_rows_are_history_and_never_shown_as_current(self):
        from fpfa.design_basis_docx import write_design_basis

        record = _record()
        di, basis = _seed_inputs(record)
        _run_plan(record, di, basis)
        old = {row["tool"]: row["id"] for row in record.calcs("job1")}
        finding = record.record_finding("job1", agent="fp-sprinkler", label="calculated", supports=[old["di_trip_to_water"]],
                                        text="t_total is 38.1 s against a 30 s limit")
        _change(record, "q_fill_gpm", 750)
        out = Path(tempfile.mkdtemp(prefix="fpfa-tier-out-")) / "stale.docx"
        write_design_basis(out, {"name": "DH-1"}, record.snapshot("job1"))
        text = _docx_text(out)
        self.assertIn("rows on this record are out of date because an input changed.", text)
        self.assertIn("Input changed: q_fill_gpm changed from 600 gpm to 750 gpm", text)
        self.assertIn(f"Calculation out of date: di_trip_to_water by tool plan [{old['di_trip_to_water']}].", text)
        self.assertIn(f"OUT OF DATE and still on the record as current: finding by fp-sprinkler [{finding['id']}]", text)
        # The out-of-date screen is not in the table of current calculations, and the current volume is.
        table = text[text.index("Tool | By | Recorded"):text.index("Finding | Label | By")]
        self.assertNotIn("di_trip_to_water", table)
        self.assertIn("zone_trapped_volume", table)
        row = next(line for line in text.splitlines() if line.startswith("t_total is 38.1 s against a 30 s limit |"))
        self.assertIn("Out of date:", row)
        self.assertIn("q_fill_gpm 750 gpm | GIVEN", text.replace("q_fill_gpm | 750 gpm | GIVEN", "q_fill_gpm 750 gpm | GIVEN"))


if __name__ == "__main__":
    unittest.main()
