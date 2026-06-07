import unittest

from reportlib import gitlog


class TestLogArgs(unittest.TestCase):
    def test_should_build_args_with_range_and_no_merges_across_all_refs(self):
        args = gitlog.log_args("2026-06-01", "2026-06-08")
        self.assertIn("--no-merges", args)
        self.assertIn("--all", args)
        self.assertIn("--since=2026-06-01", args)
        self.assertIn("--until=2026-06-08", args)

    def test_should_add_author_filter_when_given(self):
        args = gitlog.log_args("2026-06-01", "2026-06-08", author="dauren")
        self.assertIn("--author=dauren", args)

    def test_should_omit_author_filter_when_not_given(self):
        args = gitlog.log_args("2026-06-01", "2026-06-08")
        self.assertFalse(any(a.startswith("--author=") for a in args))


class TestParseLog(unittest.TestCase):
    def test_should_parse_multiple_commit_lines(self):
        sep = gitlog.SEP
        raw = f"abc{sep}2026-06-05{sep}dauren{sep}feat: x\ndef{sep}2026-06-04{sep}dauren{sep}fix: y"
        commits = gitlog.parse_log(raw)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["hash"], "abc")
        self.assertEqual(commits[0]["date"], "2026-06-05")
        self.assertEqual(commits[0]["author"], "dauren")
        self.assertEqual(commits[0]["subject"], "feat: x")

    def test_should_skip_blank_and_malformed_lines(self):
        sep = gitlog.SEP
        raw = f"\nabc{sep}2026-06-05{sep}dauren{sep}feat: x\njunk-line\n"
        self.assertEqual(len(gitlog.parse_log(raw)), 1)

    def test_should_keep_subjects_that_contain_punctuation(self):
        sep = gitlog.SEP
        raw = f"abc{sep}2026-06-05{sep}dauren{sep}feat: a, b; c — done"
        self.assertEqual(gitlog.parse_log(raw)[0]["subject"], "feat: a, b; c — done")


class TestDedupe(unittest.TestCase):
    def test_should_remove_duplicate_hashes_preserving_order(self):
        commits = [
            {"hash": "a", "subject": "x"},
            {"hash": "a", "subject": "x"},
            {"hash": "b", "subject": "y"},
        ]
        result = gitlog.dedupe(commits)
        self.assertEqual([c["hash"] for c in result], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
