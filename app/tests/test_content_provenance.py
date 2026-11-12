"""Text guards for the corrections docs/content-provenance.md lists, and for the skills the roles name.

A text guard reads the packaged file itself, so it fails when a sync from another copy drops the sentence,
which a test of behaviour alone would not notice. Each guard checks a phrase the correction introduced; it
does not restate or rewrite the engineering sentence, and it is not a review of whether that sentence is right.

These tests live in app/tests, outside the content pack, so adding them does not move the content fingerprint.
No model is involved.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

P_LEG = "pressure drop from sprinkler operation"
# docs/content-provenance.md, section 2a: pull request #75 (bc14eae) wrote the second release leg as P in these files.
SECTION_2A = {
    "skills/dry-preaction-water-delivery-screen/SKILL.md": (P_LEG, "(detection AND P)"),
    "skills/fa-asd-vewfd-data-hall-sampling-layout/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-double-interlock-releasing-cause-and-effect/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-fire-pump-and-preaction-supervisory-points/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-hvac-door-and-lock-interfaces/SKILL.md": (P_LEG, "same-zone P"),
    "skills/fa-integrated-systems-test-matrix/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-pathway-survivability-election/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-supervising-station-signal-schedule/SKILL.md": (P_LEG, "AND P"),
    "skills/fa-two-level-detection-stagger-and-fm-mapping/SKILL.md": (P_LEG, "AND P"),
    "skills/nitrogen-inerting-and-c-factor-gate/SKILL.md": (P_LEG, "(detection AND P)"),
    "skills/preaction-el-el-trim-election/SKILL.md": (P_LEG, "P is the second release leg"),
    "skills/preaction-releasing-c-and-e-soo/SKILL.md": (P_LEG, "AND P"),
    "roles/fa-releasing/ROLE.md": (P_LEG, "Release is the detection leg AND P."),
    "roles/fp-sprinkler/ROLE.md": (P_LEG, "carries the second release leg"),
}
# docs/content-provenance.md, section 2b-0: the team milestone (3f6e07b) added these to the roles.
TEAM_MILESTONE = {
    "roles/fp-sprinkler/ROLE.md": (
        "## Working with the team",
        "You do not own the detection time or the release time in the delivery screen.",
        "Do not pick a time yourself.",
        "Only the lead changes a project input.",
    ),
    "roles/fa-releasing/ROLE.md": (
        "## Working with the team",
        "Do not assume electric/electric.",
        "An unsupported time is ASSUMED, and the design basis should say so.",
        "Only the lead changes a project input.",
    ),
    "roles/qa-specialist/ROLE.md": (
        "## Kinds of cite on a project record",
        "- PACKAGE ASSERTION is a calculation record",
        "- CONTENT-PACK NOTE is the content team's reviewed note",
        "- AUTHOR'S NOTE is a note the claim's own author wrote",
        "- PROJECT INPUT is a value the designer gave.",
        "A figure in a claim has to be in the cite",
    ),
    "roles/README.md": (
        "A chat turn on a job is the lead of a team.",
        "Keep that section when you edit the file",
    ),
}
# docs/content-provenance.md, section 2b-2: 0.3.2 (6021015) told the lead and both specialists that a change of
# unit comes from convert_units.
UNITS_SENTENCES = {
    "roles/lead/ROLE.md": ("convert_units",),
    "roles/fp-sprinkler/ROLE.md": ("`convert_units` for any change of unit.",),
    "roles/fa-releasing/ROLE.md": ("convert_units",),
}


def _text(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


class ProvenanceTextGuardTests(unittest.TestCase):
    def test_section_2a_files_still_name_p_as_the_second_leg(self):
        for rel, phrases in SECTION_2A.items():
            text = _text(rel)
            for phrase in phrases:
                self.assertIn(phrase, text, f"{rel} lost the P correction of pull request #75 ({phrase!r})")

    def test_the_team_milestone_role_additions_are_still_there(self):
        for rel, phrases in TEAM_MILESTONE.items():
            text = _text(rel)
            for phrase in phrases:
                self.assertIn(phrase, text, f"{rel} lost a 3f6e07b addition ({phrase!r})")

    def test_the_roles_still_send_a_change_of_unit_to_convert_units(self):
        for rel, phrases in UNITS_SENTENCES.items():
            text = _text(rel)
            for phrase in phrases:
                self.assertIn(phrase, text, f"{rel} lost the 0.3.2 units sentence ({phrase!r})")

    def test_the_provenance_page_names_these_guards(self):
        page = (REPO / "docs" / "content-provenance.md").read_text(encoding="utf-8")
        for name in ("test_section_2a_files_still_name_p_as_the_second_leg",
                     "test_the_team_milestone_role_additions_are_still_there",
                     "test_the_roles_still_send_a_change_of_unit_to_convert_units",
                     "test_every_skill_a_role_names_is_in_the_pack",
                     "test_the_parse_reads_the_qa_roles_own_line_exactly"):
            self.assertIn(name, page)
        self.assertIn("3f6e07b", page)


class HintCiteTests(unittest.TestCase):
    """A hint is shown only with its cite and edition and VERIFY, and its cite is one the content pack holds."""

    def test_every_hint_cite_is_in_the_pack_file_it_names(self):
        from fpfa import inputs

        self.assertTrue(inputs.HINTS)
        for name, hints in inputs.HINTS.items():
            for hint in hints:
                text = _text(hint.source)
                self.assertIn(hint.quote, text, f"{name}: {hint.source} does not hold the pin the hint cites")
                self.assertRegex(hint.cite, r"(?:NFPA \d+|FM DS [\d-]+)", name)
                self.assertRegex(hint.cite, r"(?:-20\d\d|\(\w+ 20\d\d\))", f"{name}: the cite names no edition")
                self.assertFalse(hint.source.startswith("corpus/"), "search_corpus is the only reader of corpus/")
            shown = inputs.hint_text(name)
            self.assertEqual(shown.count(inputs.VERIFY), len(hints), shown)
            for hint in hints:
                self.assertIn(hint.cite, shown)

    def test_hints_the_owner_removed_stay_removed_and_base_area_shows_fm(self):
        """The owner's review of 2026-11-12: no hint for the fill flow, the supervisory fill, or the low-air setting."""
        from fpfa import inputs

        for name in ("q_fill_gpm", "supervisory_psig", "supervisory_psi", "t_detect_s", "t_release_s", "t_exhaust_s"):
            self.assertEqual(inputs.hints_of(name), (), name)
        area = inputs.hint_text("base_area_ft2")
        self.assertIn("1,500 ft2 (ordinary hazard; NFPA 13-2025 Table 19.2.3.1.1) VERIFY", area)
        self.assertIn("3,500 ft2 (FM, dry or double-interlock; FM DS 5-32 (January 2026) §2.4.3.3.1.1.A) VERIFY", area)
        self.assertIsNone(inputs.hint_of("base_area_ft2"), "two hints: Use hints leaves the field for the designer")


class RoleSkillReferenceTests(unittest.TestCase):
    def test_every_skill_a_role_names_is_in_the_pack(self):
        """A role that sends a model to a skill the pack does not hold sends it nowhere."""
        roles = {path.name for path in (REPO / "roles").iterdir() if path.is_dir()}
        modes = {path.name for path in (REPO / "modes").iterdir() if path.is_dir()}
        named: dict[str, set[str]] = {}
        for path in sorted((REPO / "roles").glob("*/ROLE.md")):
            for slug in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", path.read_text(encoding="utf-8")):
                if slug not in roles and slug not in modes:
                    named.setdefault(slug, set()).add(path.parent.name)
        self.assertGreater(len(named), 10, "the roles name skills; the pattern found too few to be reading them")
        missing = {slug: sorted(by) for slug, by in named.items() if not (REPO / "skills" / slug / "SKILL.md").is_file()}
        self.assertEqual(missing, {}, "skills named by a role that the pack does not hold")


if __name__ == "__main__":
    unittest.main()
