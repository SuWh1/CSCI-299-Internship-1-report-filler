import os
import tempfile
import unittest

from reportlib import contentstore as cs


class TestSplitParagraphs(unittest.TestCase):
    def test_should_split_on_blank_lines_and_trim(self):
        self.assertEqual(cs.split_paragraphs("a\n\nb\n\n  c  "), ["a", "b", "c"])

    def test_should_return_empty_for_blank_text(self):
        self.assertEqual(cs.split_paragraphs("\n   \n"), [])


class TestContentStore(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_should_round_trip_week_content(self):
        cs.write_content(self.dir, 1, ["First para.", "Second para."])
        self.assertEqual(cs.read_content(self.dir, 1), ["First para.", "Second para."])

    def test_should_return_empty_for_missing_week(self):
        self.assertEqual(cs.read_content(self.dir, 9), [])

    def test_should_list_existing_weeks_sorted_numerically(self):
        cs.write_content(self.dir, 2, ["b"])
        cs.write_content(self.dir, 1, ["a"])
        cs.write_content(self.dir, 10, ["c"])
        self.assertEqual(cs.existing_weeks(self.dir), [1, 2, 10])

    def test_should_return_no_weeks_for_missing_dir(self):
        self.assertEqual(cs.existing_weeks(os.path.join(self.dir, "nope")), [])

    def test_should_collect_weeks_content_up_to_limit(self):
        for w in (1, 2, 3):
            cs.write_content(self.dir, w, [f"week {w}"])
        collected = cs.weeks_content(self.dir, upto=2)
        self.assertEqual(set(collected.keys()), {1, 2})
        self.assertEqual(collected[1], ["week 1"])

    def test_should_collect_all_weeks_when_no_limit(self):
        for w in (1, 2, 3):
            cs.write_content(self.dir, w, [f"week {w}"])
        self.assertEqual(set(cs.weeks_content(self.dir).keys()), {1, 2, 3})


if __name__ == "__main__":
    unittest.main()
