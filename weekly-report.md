# Weekly report — instructions for the AI

You are helping a student write **one** weekly internship report and write it into
their Word form. Everything personal is in `report.config.json` — read it, never
hardcode names, dates, or companies.

## Steps

1. **Find the week:** `python3 report.py status` — it prints which week is due, its
   dates, which weeks are already written, and how many commits exist. Report the
   *latest completed* week unless the student names another.

2. **Gather the facts (read-only):** `python3 report.py gather --week N`. This gives
   you, for that week only: the student's commits in the tracked repos (the *only*
   projects to write about), their notes (`notes/week-N.md`), and the text of weeks
   already written (so you don't repeat them). Use **only** this command for commit
   data — its window is already limited to the one reporting week. Do not run your
   own `git log` or pull history beyond that week.

3. **If there is no data** (no commits AND no notes), STOP. Do not invent anything.
   Ask the student what they did that week — meetings, learning, non-code work — or
   ask them to write it in `notes/week-N.md`, then gather again.

4. **Ask the student for impressions** if the notes don't already have them. The form
   requires a personal impression every week and git can't supply it. Offer to save
   what they say into `notes/week-N.md`.

5. **Write the report** (~150–300 words) and save it to a scratch file, e.g.
   `.week-draft-N.md`. Follow the writing style below.

6. **Write it into the form:** `python3 report.py fill --week N --content-file .week-draft-N.md`.
   This saves the prose and generates `reports/Week-N.docx` (cumulative: weeks 1..N,
   header filled from config). The template form is never touched.

7. **Show the student** the final week text and stop. Never push or commit for them.

## Writing style (read this — it's the whole point)

Write like the student actually wrote it: plain, specific, first person. The reader
should not be able to tell an AI helped.

**Do:**
- Open with the **actual work**, e.g. "My main task this week was…", not a role summary.
- Be **concrete**: name the real thing you built or fixed and what it does.
- Give a **real** impression: one honest, specific thing — something that was hard,
  something that finally worked, something you learned. Pull it from the notes.
- Vary sentence length. Short sentences are fine. Three short paragraphs is plenty.

**Don't:**
- Don't open with "I worked as a [role] across the backend and frontend of…".
- Don't restate the company/role — that's already in the form header.
- Don't list commits or mention git, branches, or commit messages.
- Don't use AI-tell clichés: "a lot to take in", "rewarding", "valuable experience",
  "steep learning curve", "eager to", "deepened my understanding", "honed my skills",
  "delve", "leverage", "seamless", "robust", "I'm excited to".
- Don't pad to hit a word count. If the week was light, a short honest report is better.

**Rules of substance:**
- Only the tracked projects. Never invent tasks, numbers, or feelings.
- Report only the one week from `status`/`--week`; its commit window is fixed to
  those 7 days. Don't reach into other weeks' work.
- If a task continues from a previous week, write only **this week's progress** on
  it — don't re-describe what an earlier week already covered (you're shown earlier
  weeks under "do NOT repeat").
- If a note contradicts the commits, trust the note and mention the mismatch to the student.
- One week per run; leave other weeks alone.
