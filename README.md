# 📄 Internship Weekly Report Filler

Writing the weekly internship report by hand is tedious. This tool does it for you:
your AI assistant reads what you actually did that week (your git commits + any
notes you add), writes a short report in **plain student voice**, and drops it into
the university's Word form — one new file per week, no repetition.

It's **zero-install** (Python standard library only) and **reusable by any student**:
everything personal lives in one config file. Clone, fill it in, go.

---

## 🚀 Quick start

```bash
# 1. Get the code
git clone <this-repo-url>
cd <this-repo>

# 2. Make your config (this file is git-ignored, so your details stay private)
cp report.config.example.json report.config.json
#    …then open report.config.json and fill in every value (see below)

# 3. Put your university form in the folder and set its name in the config
#    (report.docxFile). The included Summer-Internship-Report-Form.docx is the
#    default template — replace it with yours if different.

# 4. Check it's set up
python3 report.py status
```

Then, each week, tell your AI assistant: **"make this week's internship report."**
(In Claude Code, run `/weekly-report`.) It does the rest and shows you the result.

> You need Python 3 (`python3 --version`) and git. That's it.

---

## 🤖 Works with any AI assistant

The tool itself (`report.py`) is just Python — any assistant that can run shell
commands drives it the same way. Each assistant auto-reads its own instructions
file, and they **all point to the same `weekly-report.md`**, so there's one source
of truth:

| Assistant | File it reads (already included) |
|---|---|
| OpenAI Codex, and most agents | `AGENTS.md` |
| Claude Code | `.claude/skills/weekly-report/` (`/weekly-report`) + `CLAUDE.md` |
| Cursor | `.cursor/rules/weekly-report.mdc` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` |
| Aider / anything else | point it at `weekly-report.md` (e.g. `aider --read weekly-report.md`) |

Just open the project in your assistant and say **"make this week's internship
report."** (A plain chat bot with no terminal can't run the script — use a coding
assistant with shell access.)

---

## ✍️ What to fill in `report.config.json`

| Field | What to put |
|---|---|
| `student.name` | Your full name |
| `company.name` / `company.location` | Where you're interning, and its address |
| `position.department` / `title` / `employmentType` | Your team, role, full/part-time |
| `supervisor.name` / `position` / `email` / `phone` | Your supervisor's details (the form requires email **and** phone) |
| `internship.startDate` / `endDate` | `YYYY-MM-DD`. Weeks are counted from the start date |
| `report.docxFile` | The filename of your university Word form (kept in this folder) |
| `tracking.repos` | Folders of the projects to report on — **only these are read**. Leave `[]` if your internship isn't coding |
| `tracking.authorFilter` | Your git author name, so only **your** commits count. Find it with `git config user.name`. Leave `""` to include everyone |

---

## 🔁 How a week works

Your AI assistant runs these for you, but you can run them yourself too:

```bash
python3 report.py status            # which week is due + its dates
python3 report.py gather --week N   # your commits + your notes + earlier weeks
python3 report.py fill   --week N --content-file <draft>   # generate the .docx
python3 report.py rebuild           # regenerate all weeks (after editing an old one)
```

Output lands in **`reports/Week-N.docx`** — a *cumulative* file (Weeks 1..N all filled,
header included), so the newest file is always your complete, submittable form. The
template at the repo root is never modified.

---

## 🗒️ Adding your own notes (important)

Git only shows code. For everything else — meetings, what you learned, non-code
tasks, blockers, and your **personal impressions** (the form asks for these every
week) — write a few plain sentences in **`notes/week-N.md`**, or just paste them to
your assistant. That file is created for you the first time you gather a week.

If a week has **no commits and no notes**, the tool will not invent anything — your
assistant will ask you what you did.

---

## ❓ FAQ / good to know

- **Will it make things up?** No. It writes only from your commits and notes; with
  no data it asks you.
- **It sounds like a robot.** It's tuned against that (see `weekly-report.md`), but
  the best fix is one honest sentence in your notes — the report builds from it.
- **My internship started later than June 1 / isn't 5 weeks.** Set your real dates in
  the config; weeks beyond the form's 5 slots are added automatically.
- **Is my data safe?** `report.config.json`, your notes, and generated reports are
  **git-ignored** — they won't be pushed. Only the clean template is shared.
- **Non-coding internship?** Set `tracking.repos: []` and work entirely from notes.

---

## 🗂️ What's in here

| Path | What it is |
|---|---|
| `report.config.example.json` | Copy to `report.config.json` and fill in |
| `Summer-Internship-Report-Form.docx` | The Word template (never edited) |
| `reports/Week-N.docx` | Your generated reports (git-ignored) |
| `notes/week-N.md` | Your free-form input per week (git-ignored) |
| `report.py`, `reportlib/` | The tool (stdlib only) |
| `weekly-report.md` | The instructions + writing style — single source of truth |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/`, `.github/` | Per-assistant entry points that point to `weekly-report.md` |
| `.claude/skills/weekly-report/` | `/weekly-report` command for Claude Code |
| `tests/` | `python3 -m unittest discover -s tests -t .` |

MIT licensed — use it, fork it, share it with the next cohort.
