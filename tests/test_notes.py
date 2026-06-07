import os
import tempfile
import unittest

from reportlib import notes


class TestReadNotes(unittest.TestCase):
    def _write(self, content):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "week-1.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_should_return_empty_string_for_missing_file(self):
        self.assertEqual(notes.read_notes("/no/such/path/week-1.md"), "")

    def test_should_strip_html_comment_only_template_to_empty(self):
        path = self._write("<!-- Type your notes for this week below this line. -->\n")
        self.assertEqual(notes.read_notes(path), "")

    def test_should_return_content_with_comments_removed(self):
        path = self._write("<!-- guidance -->\nMet the supervisor.\nLearned the CI pipeline.\n")
        self.assertEqual(notes.read_notes(path), "Met the supervisor.\nLearned the CI pipeline.")

    def test_should_trim_surrounding_whitespace(self):
        path = self._write("\n\n   onboarding day   \n\n")
        self.assertEqual(notes.read_notes(path), "onboarding day")


if __name__ == "__main__":
    unittest.main()
