---
name: weekly-report
description: >-
  Generate one weekly internship report and write it into the Word form in this
  folder. Use when the user asks to "make this week's report", "do the weekly
  report", or "fill the internship report". Reads report.config.json + that
  week's commits in the tracked repos + the student's notes, and generates a
  cumulative reports/Week-N.docx without repeating previous weeks.
---

# Weekly Internship Report

Generate **one** week's report and write it into `reports/Week-N.docx`, using
`report.py` for the deterministic work (dates, git, docx) and your judgment for
the prose. The template form at the repo root is never modified.

## First run / setup
If `report.config.json` is missing or `python3 report.py status` says it still has
placeholders, help the student fill it (copy `report.config.example.json`, set
name/company/supervisor/dates/repos) before doing anything else.

## Workflow
1. `python3 report.py status` — find the week due and its dates.
2. `python3 report.py gather --week N` — that week's commits, notes, and prior weeks.
3. If there are **no commits and no notes**, STOP — ask the student what they did
   (or to fill `notes/week-N.md`). Never invent work.
4. Ask for a personal impression if the notes lack one (the form requires it).
5. Write ~150–300 words in a **plain student voice** (see `weekly-report.md` —
   concrete work first, no AI clichés, no company/role boilerplate, don't list
   commits, don't repeat earlier weeks). Save to `.week-draft-N.md`.
6. `python3 report.py fill --week N --content-file .week-draft-N.md` — saves the
   prose and generates the cumulative `reports/Week-N.docx`.
7. Show the student the final text. Don't push or commit.

## Guardrails
- Everything student-specific comes from `report.config.json` — never hardcode it.
- One week per run; the template stays untouched; reports go in `reports/`.

Full style rules and steps: `weekly-report.md` in this folder.
