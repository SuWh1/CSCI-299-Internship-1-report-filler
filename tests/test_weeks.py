import unittest
from datetime import date

from reportlib import weeks


class TestWeekBounds(unittest.TestCase):
    START = date(2026, 6, 1)  # a Monday

    def test_should_compute_week1_bounds_mon_to_sun(self):
        self.assertEqual(weeks.week_bounds(self.START, 1), (date(2026, 6, 1), date(2026, 6, 7)))

    def test_should_compute_week2_bounds(self):
        self.assertEqual(weeks.week_bounds(self.START, 2), (date(2026, 6, 8), date(2026, 6, 14)))

    def test_should_compute_week5_bounds_crossing_into_july(self):
        self.assertEqual(weeks.week_bounds(self.START, 5), (date(2026, 6, 29), date(2026, 7, 5)))

    def test_should_reject_week_number_below_one(self):
        with self.assertRaises(ValueError):
            weeks.week_bounds(self.START, 0)


class TestCurrentWeek(unittest.TestCase):
    START = date(2026, 6, 1)

    def test_should_return_week1_on_last_day_of_week1(self):
        self.assertEqual(weeks.current_week_number(self.START, date(2026, 6, 7)), 1)

    def test_should_return_week2_on_first_day_of_week2(self):
        self.assertEqual(weeks.current_week_number(self.START, date(2026, 6, 8)), 2)

    def test_should_clamp_to_week1_before_internship_starts(self):
        self.assertEqual(weeks.current_week_number(self.START, date(2026, 5, 30)), 1)


class TestLatestCompletedWeek(unittest.TestCase):
    START = date(2026, 6, 1)

    def test_should_report_week1_completed_when_week1_just_ended(self):
        self.assertEqual(weeks.latest_completed_week(self.START, date(2026, 6, 7)), 1)

    def test_should_report_zero_before_first_week_finishes(self):
        self.assertEqual(weeks.latest_completed_week(self.START, date(2026, 6, 6)), 0)

    def test_should_report_week1_completed_during_week2(self):
        self.assertEqual(weeks.latest_completed_week(self.START, date(2026, 6, 10)), 1)


class TestFormatRange(unittest.TestCase):
    def test_should_format_same_month_range(self):
        self.assertEqual(weeks.format_range(date(2026, 6, 1), date(2026, 6, 7)), "June 1 – 7, 2026")

    def test_should_format_cross_month_range(self):
        self.assertEqual(weeks.format_range(date(2026, 6, 29), date(2026, 7, 5)), "June 29 – July 5, 2026")

    def test_should_format_cross_year_range(self):
        self.assertEqual(
            weeks.format_range(date(2026, 12, 28), date(2027, 1, 3)),
            "December 28, 2026 – January 3, 2027",
        )


if __name__ == "__main__":
    unittest.main()
