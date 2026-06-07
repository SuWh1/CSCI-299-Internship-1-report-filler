import unittest
from datetime import date

import report

CFG = {
    "student": {"name": "X"},
    "company": {"name": "C", "location": "L"},
    "position": {"department": "D", "title": "T", "employmentType": "Full-time"},
    "supervisor": {"name": "S", "position": "P", "email": "e@e.com", "phone": "+1"},
    "internship": {"startDate": "2026-06-01", "endDate": "2026-07-31"},
    "report": {"docxFile": "f.docx"},
    "tracking": {"repos": ["~/x"], "authorFilter": "dauren"},
    "style": {},
}


class TestRepoLabel(unittest.TestCase):
    def test_should_label_repo_as_parent_over_base(self):
        self.assertEqual(report._repo_label("/a/service-both/backend"), "service-both/backend")

    def test_should_tolerate_trailing_slash(self):
        self.assertEqual(report._repo_label("/a/service-both/frontend/"), "service-both/frontend")


class TestRangeFor(unittest.TestCase):
    def test_should_make_end_day_inclusive_via_next_day_until(self):
        first, last, since, until = report._range_for(CFG, 1)
        self.assertEqual((first, last), (date(2026, 6, 1), date(2026, 6, 7)))
        self.assertEqual(since, "2026-06-01")
        self.assertEqual(until, "2026-06-08")


if __name__ == "__main__":
    unittest.main()
