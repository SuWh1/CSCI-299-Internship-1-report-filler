"""Read the student's free-form notes for a week.

Notes hold what git cannot show — meetings, things learned, non-code tasks, and
personal impressions (which the form explicitly asks for every week). Template
guidance is written as HTML comments so an untouched notes file reads as empty.
"""

import os
import re

_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def read_notes(path: str) -> str:
    """Return the note text with comment guidance stripped, or '' if absent."""
    if not path or not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return _COMMENT.sub("", text).strip()
