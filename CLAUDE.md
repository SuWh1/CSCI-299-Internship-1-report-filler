# CLAUDE.md

This repo fills in a university weekly internship report. In Claude Code you can
run the bundled skill **`/weekly-report`**, or follow the instructions directly.

Full instructions and writing rules: **[weekly-report.md](weekly-report.md)**
(shared by every assistant; also summarized in [AGENTS.md](AGENTS.md)).

Quick reference:
```bash
python3 report.py status
python3 report.py gather --week N
python3 report.py fill --week N --content-file .week-draft-N.md
```
Never invent work (no commits + no notes → ask the student). Plain student voice,
no AI clichés. Personal details live in `report.config.json` — never hardcode them.
