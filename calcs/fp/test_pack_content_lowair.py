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
sentence that names low air beside a release word with no negation; the specific
phrasings the pack used to carry (low air as an operand of the release AND, low air as
the second interlock or gate, a release that needs low air); and the paraphrases a
reviewer's probe showed the first version missed: detection joined to low air in a
sentence about releasing, low air said to complete or confirm the release, and low air
mapped or used as P. A paraphrase nobody thought of still passes.

The rules below are the same rules as release_wording_hits in app/fpfa/releasing.py,
which the application runs on every finding, every lead reply, and the exported draft.
They are kept here as a copy so this file can travel with a bare content pack. The app
suite (app/tests/test_releasing_basis.py) holds the two to the same sentences; change
both together.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("corpus", "specs", "skills", "roles", "modes")

LOW_AIR = re.compile(r"low[- ]air", re.I)
_LA = r"(?:low[-_ ]air|low[- ]supervisory[- ](?:air|pressure)|loss of supervisory (?:air|pressure))"
_LOW_AIR = re.compile(_LA, re.I)
# The plain spelling, for the widest rule: a sentence that names low air beside a release word.
_LOW_AIR_PLAIN = re.compile(r"low[- ]air", re.I)
_RELEASE_WORD = re.compile(r"\b(releas\w*|opens? the (preaction )?valve)\b", re.I)
_NEGATION = re.compile(
    r"\b(not|never|no|cannot|can't|without|alone|only supervisory|supervisory only|"
    r"is supervisory|stays supervisory|keeps the low-air switch supervisory)\b"
    # The supervisory point named as such: "low-air supervisory row", "supervisory low air".
    r"|low[- ]air supervisory|supervisory low[- ]air",
    re.I,
)
_ACT = r"(?:releas\w*|trips?|tripped|opens?|opened|admit\w*|energi[sz]\w*|discharg\w*)"
# A release, or the release AND written as an operator.
_ACTION = re.compile(r"\b" + _ACT + r"\b|\bAND(?:s|ed)?\b")
# What may stand between a joining word and low air: "and the low-air switch", "plus a low-air signal".
_NEAR = r"\s+(?:(?:a|an|the|its|same-zone|with|on)\s+){0,2}"
# Phrases that state or imply low air as a release leg, whatever else the sentence says.
_BANNED = (
    re.compile(r"low[- ]air release input", re.I),
    re.compile(r"panel low[- ]air interlock", re.I),
    re.compile(r"\band (same-zone )?low air\b.{0,40}\b(releas|not isolated)", re.I),
    re.compile(r"detection and low air together", re.I),
    re.compile(r"needs loss of supervisory pressure before the solenoid", re.I),
    re.compile(r"electric/electric trim uses an electric low[- ]air input", re.I),
    # Low air written as an operand of the release Boolean. The operator is upper case there.
    re.compile(r"\bAND\s+(?:same-zone\s+)?low[-_ ]air\b"),
    # Low air named as the second interlock, gate, or leg, in either order.
    re.compile(r"low[- ]air\b[^.;]{0,30}\bis the (second|2nd)\b[^.;]{0,30}\b(interlock|gate|leg)", re.I),
    re.compile(r"=\s*\**low[- ]air\b[^.;]{0,30}\b(sprinkler leg|second gate|second interlock)", re.I),
    re.compile(r"\b(second|2nd)\s+(leg|interlock|gate|event|input|condition)\b[^.;]{0,50}\b(is|are|=|being)\b"
               r"[^.;]{0,25}" + _LA, re.I),
    # A release that waits for low air.
    re.compile(r"\b(together with|only with|still needs)\s+(same-zone\s+)?low[- ]air\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\b(is|as) (a|the) (trip|release) input\b", re.I),
    re.compile(r"low[- ]air\b[^.;]{0,60}\balso the\b[^.;]{0,40}\breleas", re.I),
)
# Detection joined to low air. Read as the release AND only in a sentence about releasing (_ACTION).
_JOINED = (
    re.compile(r"\b(detect\w*|smoke|alarm\w*|fire 1)\b[^.;]{0,50}(\band\b|\bplus\b|\+|&|\btogether with\b|"
               r"\bcombined with\b|\bwith\b|\bAND(?:s|ed)?\b)" + _NEAR.replace(r"\s+", r"\s*", 1) + _LA, re.I),
    re.compile(_LA + r"\b[^.;]{0,30}(\band\b|\bplus\b|\+|&|\btogether with\b)[^.;]{0,30}\b(detect\w*|smoke)\b", re.I),
)
# Shapes that read as low air in the release AND unless the same sentence denies it.
_UNLESS_DENIED = (
    # Low air said to finish, confirm, or stand for the release or the second leg.
    re.compile(_LA + r"\b[^.;]{0,60}\b(completes?|confirms?|satisf\w+|provides?|supplies|carries|serves as|acts as)\b"
               r"[^.;]{0,40}\b(releas\w*|interlock|second leg|sprinkler operation|sprinkler leg)\b", re.I),
    # Low air mapped, wired, or used as P.
    re.compile(r"\b(map|wire|use|program|assign|treat)\w*\b[^.;]{0,40}" + _LA + r"\b[^.;]{0,40}\bas\b[^.;]{0,25}"
               r"(\bP\b|\bthe release\b|\ba release\b|\bthe second\b|\bthe interlock\b)", re.I),
    # A release that needs, or happens on, low air.
    re.compile(r"\b" + _ACT + r"\b[^.;]{0,40}\b(needs?|requires?|on|when|upon|after|once)\b[^.;]{0,60}" + _LA, re.I),
    re.compile(r"\b(both|needs?|needed|requires?|required)\b[^.;]{0,80}" + _LA + r"\b[^.;]{0,60}\b" + _ACT + r"\b", re.I),
    re.compile(_LA + r"\b[^.;]{0,20}(->|→|=>)[^.;]{0,15}\breleas", re.I),
)
# The sentence itself says low air is not a release input, or is supervisory only.
_DENIAL = re.compile(r"\b(never|not)\b[^.;]{0,20}\b(a |the )?(trip|release) input\b", re.I)
_DENIES = re.compile(
    r"\b(never|not|no)\b[^.;]{0,25}\b(a |the )?(trip|release)\b|supervisory[- ]only|only supervisory|"
    r"\b(is|are|stays|remains) (a )?supervisory\b|"
    + _LA + r"\b[^.;]{0,45}\b(does not|do not|doesn't|never|cannot|can't|is not|isn't|alone|must not|shall not)\b|"
    r"\b(does not|do not|never|cannot|must not|shall not|not)\b[^.;]{0,60}" + _LA + r"|"
    r"\b(neither|nor)\b|\bwithout\b[^.;]{0,30}" + _LA,
    re.I,
)


def _sentences(text: str):
    for line_no, line in enumerate(str(text or "").splitlines(), 1):
        for part in re.split(r"(?<=[.;])\s+", line):
            if part.strip():
                yield line_no, part.strip()


def low_air_release_hits(text: str):
    """Sentences in text that depart from the releasing rule: (line number, sentence)."""
    hits = []
    for line_no, sentence in _sentences(text):
        if not _LOW_AIR.search(sentence):
            continue
        banned = [pattern for pattern in _BANNED if pattern.search(sentence)]
        if banned:
            # "low air is never a release input" names the phrase in order to deny it.
            only_input_phrase = all("input" in pattern.pattern and "also" not in pattern.pattern
                                    and "second" not in pattern.pattern for pattern in banned)
            if only_input_phrase and _DENIAL.search(sentence):
                continue
            hits.append((line_no, sentence))
        elif _DENIES.search(sentence):
            continue
        elif any(pattern.search(sentence) for pattern in _UNLESS_DENIED):
            hits.append((line_no, sentence))
        elif _ACTION.search(sentence) and any(pattern.search(sentence) for pattern in _JOINED):
            hits.append((line_no, sentence))
        elif _LOW_AIR_PLAIN.search(sentence) and _RELEASE_WORD.search(sentence) and not _NEGATION.search(sentence):
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
            # Paraphrases the first version of this detector let through.
            "Release requires detection AND low air.",
            "The solenoid opens when smoke is detected and the low-air switch has tripped.",
            "Low air pressure is the second interlock.",
            "The second leg of the release is the low air supervisory switch.",
            "Both detection and loss of supervisory air (low air) are needed to release.",
            "Water is admitted on detection plus a low-air signal.",
            "The panel ANDs the detection zone with the low-air alarm.",
            "The valve trips when the detector alarms together with low supervisory air pressure.",
            "Low air confirms sprinkler operation and completes the release.",
            "Map the low-air supervisory point as the release input P.",
            "detection + low_air -> release",
            "The second interlock is low air from the sprinkler piping.",
            "Use the low-air switch as P.",
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
            "Detection and low air both report to the panel; low air alone never releases.",
            "A slow nitrogen leak gives a low-air supervisory signal, never a release.",
            "Low air does not release the valve, and detection alone does not either.",
            "The releasing sequence is detection AND P; the low-air switch is a separate supervisory contact.",
            "Low air alarm at 15 psi; the valve trips on detection and P.",
            "Do not describe dry-pipe operation as detection plus low air.",
            "O_supervisory := low_air OR high_air OR valve_tamper OR release_disconnect OR panel_trouble",
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


    def test_the_c_and_e_skill_keeps_the_manual_station_in_the_detection_leg(self):
        """The controlling Boolean carries a panel manual station inside the detection leg, as the kernel does.

        The packaged copy once left it out while the kernel, the FA skill, and the corpus carried it. A content
        sync that brings the old line back fails here.
        """
        path = ROOT / "skills" / "preaction-releasing-c-and-e-soo" / "SKILL.md"
        if not path.is_file():
            self.skipTest("skills/ is not beside calcs/")
        text = path.read_text(encoding="utf-8")
        self.assertIn("preaction_trip := (VEWFD_prealarm OR manual_release_station) AND P", text)
        self.assertNotIn("preaction_trip := VEWFD_prealarm AND P", text)
        self.assertIn("It still needs P", text)
        self.assertIn("AND NOT release_disconnect", text)

    def test_the_electric_pneumatic_sentence_keeps_the_isolation_qualifier(self):
        """On electric/pneumatic trim the solenoid follows the detection leg only while the zone is not isolated."""
        for rel, needle in (
            ("roles/fa-releasing/ROLE.md", "follows the detection leg alone while the zone is not isolated"),
            ("corpus/fa/di-releasing.md", "follows the detection leg while the zone is not isolated"),
            ("skills/preaction-releasing-c-and-e-soo/SKILL.md", "follows the detection leg while the release disconnect is not operated"),
        ):
            path = ROOT / rel
            if not path.is_file():
                self.skipTest("the pack's prose folders are not beside calcs/")
            self.assertIn(needle, path.read_text(encoding="utf-8"), rel)


if __name__ == "__main__":
    unittest.main()
