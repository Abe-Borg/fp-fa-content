"""The calc tree must not carry job, client, or place names."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from place_name_scan import assert_no_place_names, banned_words, place_name_hits


def _long_word() -> str:
    return next(word for word in banned_words() if len(word) >= 4)


def _interior(word: str, carrier: str) -> bool:
    hay = carrier.lower()
    needle = word.lower()
    start = hay.find(needle)
    if start < 0:
        return False
    end = start + len(needle)
    return start > 0 and end < len(hay) and hay[start - 1].isalpha() and hay[end].isalpha()


class PlaceNameTests(unittest.TestCase):
    def test_calcs_tree_has_no_job_client_or_place_names(self):
        assert_no_place_names()

    def test_snake_case_filename_is_a_hit(self):
        word = _long_word()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / f"test_{word}.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
            hits = place_name_hits(root)
        self.assertTrue(any(hit.endswith(" (filename)") for hit in hits))

    def test_snake_case_test_identifier_is_a_hit(self):
        word = _long_word()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_density.py").write_text(
                f"def test_{word}_density():\n    pass\n",
                encoding="utf-8",
            )
            hits = place_name_hits(root)
        self.assertTrue(any(hit.endswith(":1") for hit in hits))
        self.assertFalse(any(hit.endswith(" (filename)") for hit in hits))

    def test_short_entry_inside_ordinary_word_is_not_a_hit(self):
        shorts = [word for word in banned_words() if len(word) <= 3]
        self.assertTrue(shorts)
        # "labels" and "taxable" contain the short entries as interior
        # fragments. "table" and "axial" are ordinary tokens in this tree.
        carriers = ("table", "axial", "labels", "taxable")
        for word in shorts:
            self.assertTrue(any(_interior(word, carrier) for carrier in carriers))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lines = ["def test_ordinary_words():"]
            for carrier in carriers:
                lines.append(f"    value_{carrier} = {carrier!r}")
            (root / "test_ordinary.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(place_name_hits(root), [])

    def test_digit_separator_is_a_hit(self):
        word = _long_word()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.py").write_text(f"count = '{word}2'\n", encoding="utf-8")
            hits = place_name_hits(root)
        self.assertTrue(any(hit.endswith(":1") for hit in hits))


if __name__ == "__main__":
    unittest.main()
