"""Persisted per-week prose — the source of truth for report content.

Each week's approved text is stored as reports/content/week-N.md. Report .docx
files are regenerated from these, so editing an old week and rebuilding stays
consistent across every cumulative file.
"""

import os
import re


def split_paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def content_path(content_dir: str, n: int) -> str:
    return os.path.join(content_dir, f"week-{n}.md")


def write_content(content_dir: str, n: int, paragraphs):
    os.makedirs(content_dir, exist_ok=True)
    with open(content_path(content_dir, n), "w", encoding="utf-8") as f:
        f.write("\n\n".join(paragraphs) + "\n")


def read_content(content_dir: str, n: int):
    path = content_path(content_dir, n)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return split_paragraphs(f.read())


def existing_weeks(content_dir: str):
    if not os.path.isdir(content_dir):
        return []
    weeks = []
    for name in os.listdir(content_dir):
        m = re.match(r"week-(\d+)\.md$", name)
        if m:
            weeks.append(int(m.group(1)))
    return sorted(weeks)


def weeks_content(content_dir: str, upto: int = None) -> dict:
    return {
        w: read_content(content_dir, w)
        for w in existing_weeks(content_dir)
        if upto is None or w <= upto
    }
