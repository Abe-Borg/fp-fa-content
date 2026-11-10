"""Pack prose must not say low air releases the double-interlock valve.

Release is detection (D: Fire 1 or a manual station) and P, the pressure drop from
sprinkler operation (a separate pressure contact on electric/electric trim, the
pneumatic actuator at the valve on electric/pneumatic trim). Low air is a
supervisory input only and is never a release input.

This test reads corpus/ and specs/ in the repository checkout. It skips when those
folders are absent (for example, when calcs/fp is copied alone into a content pack).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("corpus", "specs")

LOW_AIR = re.compile(r"low[- ]air", re.I)
RELEASE_WORD = re.compile(r"\b(releas\w*|opens? the valve)\b", re.I)
NEGATION = re.compile(
    r"\b(not|never|no|cannot|can't|without|alone|only supervisory|supervisory only|"
    r"is supervisory|stays supervisory|keeps the low-air switch supervisory)\b",
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
)


def _sentences(text: str):
    for line_no, line in enumerate(text.splitlines(), 1):
        for part in re.split(r"(?<=[.;])\s+", line):
            if part.strip():
                yield line_no, part.strip()


def low_air_release_hits(text: str):
    hits = []
    for line_no, sentence in _sentences(text):
        if not LOW_AIR.search(sentence) and "loss of supervisory pressure" not in sentence.lower():
            continue
        if any(p.search(sentence) for p in BANNED):
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
        ):
            self.assertTrue(low_air_release_hits(bad), bad)

    def test_allows_the_supervisory_wording(self):
        for good in (
            "Low air is supervisory only and is never a release input.",
            "Low air alone is supervisory and does not release.",
            "Detection and P together release.",
            "FM DS 2-81 expects that loss of air does not trip the valve for the supply duration.",
            "Electric/electric trim uses a normally closed solenoid; supervisory air serves the low-air switch.",
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
            self.skipTest("corpus/ and specs/ are not beside calcs/")
        return files

    def test_no_low_air_release_wording_in_corpus_or_specs(self):
        found = []
        for path in self._files():
            for line_no, sentence in low_air_release_hits(path.read_text(encoding="utf-8")):
                found.append(f"{path.relative_to(ROOT)}:{line_no}: {sentence[:160]}")
        self.assertEqual(found, [], "low air is supervisory only; release is D and P:\n" + "\n".join(found))

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


if __name__ == "__main__":
    unittest.main()
