"""Week numbering and date-range formatting for a fixed-length internship.

Weeks are 7-day blocks anchored to the internship start date: week 1 begins on
the start date, week 2 seven days later, and so on. The university form asks for
one report per completed week, so the helpers here answer "which week is it" and
"what dates does that week span".
"""

from datetime import date, timedelta

_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def week_bounds(start: date, week_number: int):
    """Return (first_day, last_day) for a 1-indexed week from the start date."""
    if week_number < 1:
        raise ValueError(f"week_number must be >= 1, got {week_number}")
    first = start + timedelta(days=7 * (week_number - 1))
    return first, first + timedelta(days=6)


def current_week_number(start: date, today: date) -> int:
    """Week that `today` falls in (1-indexed), clamped to 1 before the start."""
    if today < start:
        return 1
    return (today - start).days // 7 + 1


def latest_completed_week(start: date, today: date) -> int:
    """Highest week whose final day is on/before `today` (0 if none yet)."""
    n = current_week_number(start, today)
    _, last = week_bounds(start, n)
    return n if today >= last else n - 1


def _month(d: date) -> str:
    return _MONTHS[d.month - 1]


def format_range(first: date, last: date) -> str:
    """Human range, e.g. 'June 1 – 7, 2026' / 'June 29 – July 5, 2026'."""
    if first.year != last.year:
        return f"{_month(first)} {first.day}, {first.year} – {_month(last)} {last.day}, {last.year}"
    if first.month != last.month:
        return f"{_month(first)} {first.day} – {_month(last)} {last.day}, {last.year}"
    return f"{_month(first)} {first.day} – {last.day}, {last.year}"


def format_full(d: date) -> str:
    """Single date, e.g. 'June 1, 2026' — used for the header Start/End cell."""
    return f"{_month(d)} {d.day}, {d.year}"
