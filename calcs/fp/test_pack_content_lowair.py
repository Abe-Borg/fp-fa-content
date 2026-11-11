"""Pack prose must not say low air releases the double-interlock valve.

Release is detection (D: Fire 1 or a manual station) and P, the pressure drop from
sprinkler operation (a separate pressure contact, PSL-REL, on electric/electric trim;
the pneumatic actuator at the valve, PA-REL, on electric/pneumatic trim). Low air is a
supervisory input only (PSL-SUP) and is never a release input.

This test reads corpus/, specs/, skills/, roles/, and modes/ in the repository checkout:
every folder of prose a model reads. It skips a folder that is absent (for example, when
calcs/fp is copied alone into a content pack). The app suite runs the same detector over
docs/ and over what the app itself writes.

The detector is a guard against the wording coming back, not a proof. It flags a
sentence that names low air beside a release word with no negation, and the specific
phrasings the pack used to carry: low air as an operand of the release AND, low air as
the second interlock or gate, and a release that needs low air.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("corpus", "specs", "skills", "roles", "modes")

LOW_AIR = re.compile(r"low[- ]air", re.I)
RELEASE_WORD = re.compile(r"\b(releas\w*|opens? the (preaction )?valve)\b", re.I)
NEGATION = re.compile(
    r"\b(not|never|no|cannot|can't|without|alone|only supervisory|supervisory only|"
    r"is supervisory|stays supervisory|keeps the low-air switch supervisory)\b"
    # The supervisory point named as such: "low-air supervisory row", "supervisory low air".
    r"|low[- ]air supervisory|supervisory low[- ]air",
    re.I,
)
# Phrases that state or imply low air as a release leg, whatever the negation.
BANNED = (
    re.compile(r"low[- ]air release input", re.I),
    re.compile(r"panel low[- ]air interlock", re.I),
    re.compile(r"\band (same-zone )?low air\b.{0,40}\b(releas|not isolated)", re.I),
    re.compile(r"detection and low air together", re.I),
    re.compile(r"needs loss of supervisory pressure before the solenoid", re.I),
    re.compile(r"electric/electric trim uses an electric low[- ]air input", re.I),
    # Low air written as an operand of the release Boolean. The operator is upper case there.
    re.compile(r"\bAND\s+(?:same-zone\s+)?low[-_ ]air\b"),
    # Low air named as the second interlock, gate, or leg.
    re.compile(r"low[- ]air\b[^.;]{0,30}\bis the (second|2nd)\b[^.;]{0,30}\b(interlock|gate|leg)", re.I),
    re.compile(r"=\s*\**low[- ]air\b[^.;]{0,30}\b(sprinkler leg|second gate|second interlock)", re.I),
    # A release that waits for low air.
    re.compile(r"\b(together with|only with|still needs)\s+(same-zone\s+)?low[- ]air\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\b(is|as) (a|the) (trip|release) input\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\balso the\b[^.;]{0,40}\breleas", re.I),
)
# A banned phrase is allowed when the same sentence denies it ("is never a release input").
DENIAL = re.compile(r"\b(never|not)\b[^.;]{0,20}\b(a |the )?(trip|release) input\b", re.I)


def _sentences(text: str):
    for line_no, line in enumerate(text.splitlines(), 1):
        for part in re.split(r"(?<=[.;])\s+", line):
            if part.strip():
                yield line_no, part.strip()


def low_air_release_hits(text: str):
    hits = []
    for line_no, sentence in _sentences(text):
        if not LOW_AIR.search(sentence) and "loss of supervisory pressure" not in sentence.lower() \
                and "low_air" not in sentence:
            continue
        banned = [p for p in BANNED if p.search(sentence)]
        if banned:
            # "low air is never a release input" names the phrase in order to deny it.
            only_input_phrase = all("input" in p.pattern and "also" not in p.pattern for p in banned)
            if only_input_phrase and DENIAL.search(sentence):
                continue
            hits.append((line_no, sentence))
        elif LOW_AIR.search(sentence) and RELEASE_WORD.search(sentence) and not NEGATION.search(sentence):
            hits.append((line_no, sentence))
    return hits


class DetectorTests(unittest.TestCase):
    def test_flags_low_air_as_a_release_leg(self):
        for bad in (
            "The low-air release input is logic, not a second supervisory label.",
            "Detection and low air together release.",
            "Water opens without waiting for the panel low-air interlock.",
            "That input still needs loss of supervisory pressure before the solenoid releases water.",
            "Release is detection and same-zone low air and not isolated.",
            # The phrasings the skills carried before the relabel.
            "Solenoid = (Fire 1 OR FACU manual release) AND same-zone low air AND NOT isolated.",
            "preaction_trip := VEWFD_prealarm AND low_air",
            "Low air is the second double-interlock gate.",
            "It opens the preaction valve only together with low air.",
            "On El/El, Zone 2 = **low-air / sprinkler leg**.",
            "On a double-interlock valve, low air is supervisory and it is also the same-zone release input.",
            "Low air is alarm-only on SI and is a trip input on DI.",
            "Release still needs low air, and that may never come.",
        ):
            self.assertTrue(low_air_release_hits(bad), bad)

    def test_allows_the_supervisory_wording(self):
        for good in (
            "Low air is supervisory only and is never a release input.",
            "Low air alone is supervisory and does not release.",
            "Detection and P together release.",
            "FM DS 2-81 expects that loss of air does not trip the valve for the supply duration.",
            "Electric/electric trim uses a normally closed solenoid; supervisory air serves the low-air switch.",
            "Release Boolean (detection AND P) / low-air supervisory row / SI vs DI.",
            "Solenoid = (Fire 1 OR FACU manual release) AND P AND NOT isolated.",
            "P is the PSL-REL contact; its zone is typed LOW AIR ALARM, not the supervisory LOW AIR type.",
            "Low air stays a supervisory signal that is never a release input.",
            "The low-air supervisory switch (PSL-SUP) is supervisory only.",
        ):
            self.assertFalse(low_air_release_hits(good), good)


class PackProseTests(unittest.TestCase):
    def _files(self):
        files = []
        for name in SCAN_DIRS:
            folder = ROOT / name
            if folder.is_dir():
                files.extend(sorted(folder.rglob("*.md")))
        if not files:
            self.skipTest("the pack's prose folders are not beside calcs/")
        return files

    def test_no_low_air_release_wording_in_corpus_or_specs(self):
        """Every prose folder a model reads: corpus, specs, skills, roles, and modes."""
        found = []
        for path in self._files():
            for line_no, sentence in low_air_release_hits(path.read_text(encoding="utf-8")):
                found.append(f"{path.relative_to(ROOT)}:{line_no}: {sentence[:160]}")
        self.assertEqual(found, [], "low air is supervisory only; release is D and P:\n" + "\n".join(found))

    def test_the_scan_covers_the_skills_and_the_roles(self):
        self.assertIn("skills", SCAN_DIRS)
        self.assertIn("roles", SCAN_DIRS)
        if not (ROOT / "skills").is_dir():
            self.skipTest("skills/ is not beside calcs/")
        scanned = {path.relative_to(ROOT).parts[0] for path in self._files()}
        self.assertIn("skills", scanned)
        self.assertIn("roles", scanned)

    def test_supervisory_points_names_p_not_low_air_as_the_release_input(self):
        path = ROOT / "corpus" / "fa" / "supervisory-points.md"
        if not path.is_file():
            self.skipTest("corpus/ is not beside calcs/")
        text = path.read_text(encoding="utf-8")
        self.assertTrue("never a release input" in text, "missing: never a release input")
        self.assertTrue("PA-REL" in text, "missing: PA-REL")
        self.assertTrue("PSL-REL" in text, "missing: PSL-REL")

    def test_acceptance_testing_releases_on_detection_and_p(self):
        path = ROOT / "corpus" / "fa" / "acceptance-testing.md"
        if not path.is_file():
            self.skipTest("corpus/ is not beside calcs/")
        text = path.read_text(encoding="utf-8")
        self.assertTrue("Detection and P together release" in text, "missing: Detection and P together release")

    def test_the_releasing_skills_name_p_as_the_second_leg(self):
        """The two skills a releasing sequence is written from say what P is and what low air is."""
        for slug in ("fa-double-interlock-releasing-cause-and-effect", "preaction-releasing-c-and-e-soo"):
            path = ROOT / "skills" / slug / "SKILL.md"
            if not path.is_file():
                self.skipTest("skills/ is not beside calcs/")
            text = path.read_text(encoding="utf-8")
            self.assertIn("PSL-REL", text, slug)
            self.assertIn("PA-REL", text, slug)
            self.assertIn("pressure drop from sprinkler operation", text, slug)
            self.assertRegex(text, r"never a release input", slug)


if __name__ == "__main__":
    unittest.main()
