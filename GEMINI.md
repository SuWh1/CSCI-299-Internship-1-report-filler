# GEMINI.md

This repository fills in a university weekly internship report. Follow the shared
instructions in **[weekly-report.md](weekly-report.md)** (full step-by-step and
writing rules) — also summarized in [AGENTS.md](AGENTS.md).

```bash
python3 report.py status
python3 report.py gather --week N
python3 report.py fill --week N --content-file .week-draft-N.md
```

Rules: only report on the repos in `report.config.json`; never invent work (no
commits + no notes → ask the student); plain student voice, no AI clichés; never
hardcode personal details (they live in `report.config.json`).
