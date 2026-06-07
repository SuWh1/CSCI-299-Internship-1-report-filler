# GitHub Copilot instructions

This repository fills in a university weekly internship report (a Word `.docx`).

Follow the shared instructions in [weekly-report.md](../weekly-report.md) (full
steps and writing rules) — summarized in [AGENTS.md](../AGENTS.md).

Workflow:
```bash
python3 report.py status
python3 report.py gather --week N
python3 report.py fill --week N --content-file .week-draft-N.md
```

Always: report only on the repos listed in `report.config.json`; never invent work
(no commits + no notes → ask the student); write in a plain student voice with no
AI clichés; never hardcode personal details (they live in `report.config.json`).
