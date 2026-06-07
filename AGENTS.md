# AGENTS.md — instructions for any AI coding assistant

This repository fills in a university **weekly internship report** (a Word `.docx`).
It works with any assistant that can run shell commands — Codex, Cursor, Claude
Code, Gemini CLI, Aider, Copilot, etc. The full instructions and writing rules
live in **[weekly-report.md](weekly-report.md)** — read it before writing a report.

## Setup (first time)
If `report.config.json` is missing, copy `report.config.example.json` to it and
fill in the student's details. Everything personal is in that file — never
hardcode names, companies, or dates.

## Generating one week's report
```bash
python3 report.py status            # which week is due + its dates
python3 report.py gather --week N   # that week's commits + notes + prior weeks
# …write the prose to a file, e.g. .week-draft-N.md…
python3 report.py fill --week N --content-file .week-draft-N.md
```
`fill` saves the prose and generates the cumulative `reports/Week-N.docx`
(Weeks 1..N, header filled). The template form is never modified.

## The rules that matter
- **Only** report on the projects in `report.config.json` → `tracking.repos`.
- **One week only.** Use `report.py gather --week N` for commit data — its window is
  already fixed to that week's 7 days. Don't run your own `git log` or reach into
  other weeks. If a task continues from a previous week, write only *this week's*
  progress (earlier weeks are shown under "do NOT repeat").
- **Never invent work.** If a week has no commits and no notes, stop and ask the
  student what they did (or have them write `notes/week-N.md`).
- Write in a **plain student voice** — concrete, first person, no AI clichés
  ("rewarding", "a lot to take in", "valuable experience", generic role openers),
  no company/role boilerplate (it's already in the header), don't list commits.
- One week per run; don't touch other weeks. Never `git push` for the student.

See [weekly-report.md](weekly-report.md) for the complete step-by-step and the
full writing-style do/don't list.
