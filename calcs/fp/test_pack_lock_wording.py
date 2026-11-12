"""Pack prose must not give wet pipe C = 120 or credit nitrogen with a higher C.

The company lock is C = 100 for wet, dry, and double-interlock pipe, with no nitrogen C credit. A
C = 120 value may appear only as a labelled comparison. This test reads corpus/, specs/, skills/,
roles/, and modes/ in the repository checkout and skips a folder that is absent.

It is a guard against the phrasings the pack used to carry coming back: wet pipe reported at 120,
120 worded as permitted or earned, and C = 100 held only until 98 percent is earned. A paraphrase
nobody thought of still passes. A pass is a phrase check, not an engineering review.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("corpus", "specs", "skills", "roles", "modes")

BANNED = (
    ("wet pipe at C = 120", re.compile(r"C\s*=\s*120\s+for\s+wet|wet[ -]pipe[^.\n]{0,30}\bC\s*=\s*120", re.I)),
    ("120 worded as permitted", re.compile(r"C\s*=\s*120\s+permitted|\bwould permit 120\b|\bpermits 120\b", re.I)),
    ("120 worded as earned", re.compile(r"\bearned 120\b", re.I)),
    ("C = 100 only until nitrogen is earned", re.compile(r"C\s*=\s*100\s+until|until\s+98\s*%?\s+earned", re.I)),
)


def _prose_files():
    for name in SCAN_DIRS:
        folder = ROOT / name
        if folder.is_dir():
            yield from sorted(folder.rglob("*.md"))


class LockWordingTests(unittest.TestCase):
    def test_no_banned_c_factor_phrasing_in_pack_prose(self):
        hits = []
        for path in _prose_files():
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for label, pattern in BANNED:
                    if pattern.search(line):
                        hits.append(f"{path.relative_to(ROOT).as_posix()}:{number} ({label})")
        self.assertEqual(hits, [], "\n".join(hits))

    def test_detector_catches_each_phrasing(self):
        # Built from pieces so this file does not carry the phrasings it guards against.
        n = "12" + "0"
        samples = (
            f"Company reporting: C = {n} for wet pipe, C = 100 for dry.",
            f"UFC job, C={n} permitted at 98 % purity.",
            f"This holds even when the sources would permit {n}.",
            f"Hand off the C=100 vs earned {n} question.",
            "Generator + compressor; C = 100 until 98% earned.",
        )
        for sample in samples:
            self.assertTrue(any(pattern.search(sample) for _, pattern in BANNED), sample)

    def test_the_hydraulic_note_states_c100_for_wet_dry_and_di(self):
        note = ROOT / "corpus" / "fp" / "hydraulic-method.md"
        if not note.is_file():
            self.skipTest("corpus/fp/hydraulic-method.md is not in this tree")
        text = note.read_text(encoding="utf-8")
        self.assertIn("C = 100 for wet, dry, and double-interlock", text)
        self.assertIn("nitrogen is not a C credit", text)


if __name__ == "__main__":
    unittest.main()
