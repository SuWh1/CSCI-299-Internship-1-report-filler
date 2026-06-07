import json
import os
import tempfile
import unittest
from datetime import date

from reportlib import config


def _valid_config():
    return {
        "student": {"name": "Test Student"},
        "company": {"name": "ACME", "location": "Somewhere"},
        "position": {"department": "Eng", "title": "Intern", "employmentType": "Full-time"},
        "supervisor": {"name": "Boss", "position": "Lead", "email": "b@a.com", "phone": "+1"},
        "internship": {"startDate": "2026-06-01", "endDate": "2026-07-31"},
        "report": {"docxFile": "form.docx"},
        "tracking": {"sessionDataDir": "~/x", "repos": ["~/repo"], "authorFilter": "dauren"},
        "style": {},
    }


class TestConfig(unittest.TestCase):
    def test_should_load_and_validate_a_good_config(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "report.config.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_valid_config(), f)
        cfg = config.load_config(path)
        self.assertEqual(cfg["student"]["name"], "Test Student")

    def test_should_raise_on_missing_required_key(self):
        bad = _valid_config()
        del bad["supervisor"]
        with self.assertRaises(config.ConfigError):
            config.validate_config(bad)

    def test_should_raise_on_invalid_start_date(self):
        bad = _valid_config()
        bad["internship"]["startDate"] = "not-a-date"
        with self.assertRaises(config.ConfigError):
            config.validate_config(bad)

    def test_should_allow_empty_repo_list_for_notes_only_internships(self):
        cfg = _valid_config()
        cfg["tracking"]["repos"] = []
        self.assertTrue(config.validate_config(cfg))

    def test_should_raise_when_repos_is_not_a_list(self):
        bad = _valid_config()
        bad["tracking"]["repos"] = "not-a-list"
        with self.assertRaises(config.ConfigError):
            config.validate_config(bad)

    def test_should_flag_unfilled_placeholder_config(self):
        placeholder = _valid_config()
        placeholder["student"]["name"] = "Your Full Name"
        placeholder["internship"]["startDate"] = "YYYY-MM-DD"
        self.assertTrue(config.looks_unfilled(placeholder))

    def test_should_accept_a_filled_config(self):
        self.assertFalse(config.looks_unfilled(_valid_config()))

    def test_should_raise_on_missing_nested_supervisor_field(self):
        bad = _valid_config()
        del bad["supervisor"]["email"]
        with self.assertRaises(config.ConfigError):
            config.validate_config(bad)

    def test_should_raise_on_missing_docx_file_field(self):
        bad = _valid_config()
        del bad["report"]["docxFile"]
        with self.assertRaises(config.ConfigError):
            config.validate_config(bad)

    def test_should_expand_user_home_in_paths(self):
        self.assertTrue(config.expand_path("~/x").startswith(os.path.expanduser("~")))

    def test_should_parse_start_date_as_date(self):
        self.assertEqual(config.start_date(_valid_config()), date(2026, 6, 1))


if __name__ == "__main__":
    unittest.main()
