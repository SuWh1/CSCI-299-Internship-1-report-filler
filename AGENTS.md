# AGENTS.md — instructions for any AI coding assistant

This repository fills in a university **weekly internship report** (a Word `.docx`).
It works with any assistant that can run shell commands — Codex, Cursor, Claude
Code, Gemini CLI, Aider, Copilot, etc. The full instructions and writing rules
live in **[weekly-report.md](weekly-report.md)** — read it before writing a report.

## Setup (first time)
If `report.config.json` is missing, copy `report.config.example.json` to it and
fill in the student's details (never hardcode them elsewhere). For `tracking.repos`,
the student may have many repos but only the internship's belong there — if it's
empty or unclear, run `python3 report.py discover` to list repos where they
committed during the internship, **show the list, and ask which are this
internship's** before writing those paths to the config. Never add them all.

## Generating one week's report
```bash
python3 report.py status            # which week is due + its dates
python3 report.py gather --week N   # that week's commits + notes + prior weeks
# …write the prose into reports/content/week-N.md…
python3 report.py fill --week N     # builds reports/Week-N.docx from that file
```
`fill` generates the cumulative `reports/Week-N.docx` (Weeks 1..N, header filled)
from `reports/content/week-N.md`. The template form is never modified. (You may
also pass `--content-file <path>` to import prose from elsewhere.)

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
