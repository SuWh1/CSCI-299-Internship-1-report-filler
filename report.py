#!/usr/bin/env python3
"""Weekly internship report tool.

Subcommands:
  status               Show which week to report and what's already written.
  gather  --week N     Print the facts for week N (your commits + your notes +
                       prior weeks) for an AI to turn into prose. Read-only.
  fill    --week N     Save a week's prose (from --content-file) and regenerate
                       reports/Week-N.docx (cumulative: weeks 1..N).
  rebuild              Regenerate every reports/Week-*.docx from saved prose
                       (use after editing the config or an earlier week).

The template form is never modified; every report is generated into reports/.
Stdlib only — nothing to install.
"""

import argparse
import os
import sys
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from reportlib import build, config, contentstore, discover, docxfill, gitlog, notes, weeks  # noqa: E402

CONFIG_PATH = os.path.join(BASE, "report.config.json")
EXAMPLE_PATH = os.path.join(BASE, "report.config.example.json")
NOTES_DIR = os.path.join(BASE, "notes")
REPORTS_DIR = os.path.join(BASE, "reports")
CONTENT_DIR = os.path.join(REPORTS_DIR, "content")

NOTES_TEMPLATE = (
    "<!--\n"
    "Week {n} notes. Type or paste anything you want included in this week's\n"
    "report that git can't show: meetings, what you learned, non-code tasks,\n"
    "blockers, and your honest personal impressions. Plain sentences are fine.\n"
    "Everything inside this comment block is ignored.\n"
    "-->\n"
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _template_path(cfg):
    return os.path.join(BASE, cfg["report"]["docxFile"])


def _report_path(n):
    return build.report_path(REPORTS_DIR, n)


def _notes_path(n):
    return os.path.join(NOTES_DIR, f"week-{n}.md")


def _ensure_notes_file(n):
    path = _notes_path(n)
    if not os.path.exists(path):
        os.makedirs(NOTES_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(NOTES_TEMPLATE.format(n=n))
    return path


def _repo_label(path):
    parent = os.path.basename(os.path.dirname(path.rstrip("/")))
    return f"{parent}/{os.path.basename(path.rstrip('/'))}" if parent else os.path.basename(path)


def _tilde(path):
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def _target_week(cfg, override):
    if override:
        return override
    return max(1, weeks.latest_completed_week(config.start_date(cfg), date.today()))


def _range_for(cfg, n):
    first, last = weeks.week_bounds(config.start_date(cfg), n)
    since = first.isoformat()
    until = (last + timedelta(days=1)).isoformat()  # make the end day inclusive
    return first, last, since, until


def _collect_commits(cfg, since, until):
    author = cfg["tracking"].get("authorFilter") or None
    sections, errors = [], []
    for repo in cfg["tracking"].get("repos", []):
        path = config.expand_path(repo)
        commits, err = gitlog.run_log(path, since, until, author=author)
        if err:
            errors.append(err)
        sections.append((_repo_label(path), commits))
    return sections, errors


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_status(cfg, args):
    n = _target_week(cfg, args.week)
    first, last, since, until = _range_for(cfg, n)
    written = contentstore.existing_weeks(CONTENT_DIR)

    print(f"Internship : {cfg['student']['name']} @ {cfg['company']['name']}")
    print(f"Dates      : {weeks.format_full(config.start_date(cfg))} – {weeks.format_full(config.end_date(cfg))}")
    print(f"Today      : {date.today().isoformat()}")
    print(f"Config     : {'⚠ still has placeholders — edit report.config.json' if config.looks_unfilled(cfg) else 'ready'}")
    print(f"Target week: Week {n}  ({weeks.format_range(first, last)})")
    print("Weeks written:")
    for w in range(1, max(5, written[-1] if written else 0) + 1):
        print(f"  Week {w}: {'written' if w in written else 'empty'}")
    generated = sorted(f for f in os.listdir(REPORTS_DIR) if f.endswith(".docx")) if os.path.isdir(REPORTS_DIR) else []
    print(f"Generated  : {', '.join(generated) if generated else '(none yet)'}")
    commits, errors = _collect_commits(cfg, since, until)
    total = sum(len(c) for _, c in commits)
    print(f"Commits in Week {n} range: {total} ({', '.join(f'{l}={len(c)}' for l, c in commits) or 'no repos configured'})")
    for e in errors:
        print(f"  ! {e}")


def cmd_gather(cfg, args):
    n = _target_week(cfg, args.week)
    first, last, since, until = _range_for(cfg, n)
    commits, errors = _collect_commits(cfg, since, until)
    note_text = notes.read_notes(_ensure_notes_file(n))

    out = [f"# Week {n} — {weeks.format_range(first, last)}"]
    out.append(f"(commit window {since} .. {until}, author filter: {cfg['tracking'].get('authorFilter') or 'all'})\n")

    out.append("## Your commits this week (tracked repos only)")
    any_commit = False
    for label, cs in commits:
        out.append(f"\n### {label} — {len(cs)} commit(s)")
        for c in cs:
            out.append(f"- {c['date']} {c['subject']}")
            any_commit = True
    if not commits:
        out.append("\n(No repositories configured — this is a notes-only internship.)")
    elif not any_commit:
        out.append("\n(No commits by you in the tracked repos this week.)")
    for e in errors:
        out.append(f"\n! repo error: {e}")

    out.append(f"\n## Your notes for this week (notes/week-{n}.md)")
    out.append(note_text if note_text else "(empty — nothing added)")

    prior = []
    for w in range(1, n):
        text = contentstore.read_content(CONTENT_DIR, w)
        if text:
            prior.append(f"\n### Week {w}\n" + "\n".join(text))
    out.append("\n## Already-written weeks (do NOT repeat these)")
    out.append("\n".join(prior) if prior else "(none yet)")

    if not any_commit and not note_text:
        out.append(
            "\n## STOP — no data for this week\n"
            "There are no commits and no notes for this week. Do NOT invent work. "
            f"Ask the student what they did, or have them write it in notes/week-{n}.md, "
            "then run gather again."
        )
    else:
        out.append(
            "\n## Instructions\n"
            "Write a ~150-300 word report: tasks worked on, progress made, and a short "
            "honest personal impression. Read weekly-report.md for the required writing "
            "style (plain student voice — NOT generic AI prose). Synthesize commits into "
            "themes (don't list them), blend in the notes, don't repeat earlier weeks, "
            "keep company/role boilerplate out (it's already in the header). Save plain "
            f"paragraphs to a file, then run:\n  python3 report.py fill --week {n} --content-file <file>"
        )
    print("\n".join(out))


def cmd_discover(cfg, args):
    search_dirs = [args.dir] if args.dir else (cfg["tracking"].get("searchDirs") or ["~"])
    author = cfg["tracking"].get("authorFilter") or None
    since = config.start_date(cfg).isoformat()
    until = (config.end_date(cfg) + timedelta(days=1)).isoformat()
    print(f"Scanning {', '.join(search_dirs)} for repos with your commits "
          f"({since}..{until}, author: {author or 'all'}) — this can take a moment…")

    rows = []
    for repo in discover.find_git_repos([config.expand_path(d) for d in search_dirs]):
        commits, _err = gitlog.run_log(repo, since, until, author=author)
        if commits:
            rows.append((len(commits), repo))
    rows.sort(reverse=True)

    if not rows:
        print("\nNo repositories with matching commits found.")
        print("  • Check tracking.authorFilter — yours is likely `git config user.name`.")
        print("  • Or point the scan at where your code lives: --dir ~/path  (or set tracking.searchDirs).")
        return 0

    print(f"\nFound {len(rows)} repo(s) where you committed during the internship:\n")
    for count, repo in rows:
        print(f"  {count:4d} commits  {_tilde(repo)}")
    print("\nWhich of these belong to THIS internship? Add only those paths to")
    print('tracking.repos in report.config.json — leave out personal or other-job projects.')
    return 0


def cmd_fill(cfg, args):
    n = args.week or _target_week(cfg, None)
    if args.content_file:
        try:
            with open(args.content_file, encoding="utf-8") as f:
                paragraphs = contentstore.split_paragraphs(f.read())
        except FileNotFoundError:
            print(f"ERROR: content file not found: {args.content_file}", file=sys.stderr)
            return 1
        if not paragraphs:
            print("ERROR: content file is empty", file=sys.stderr)
            return 1
        contentstore.write_content(CONTENT_DIR, n, paragraphs)
    else:
        paragraphs = contentstore.read_content(CONTENT_DIR, n)
        if not paragraphs:
            print(f"ERROR: no prose for week {n}. Write reports/content/week-{n}.md "
                  f"first, or pass --content-file.", file=sys.stderr)
            return 1
    # Rebuild every weekly file so all cumulative reports stay consistent.
    built = build.build_all(_template_path(cfg), cfg, CONTENT_DIR, REPORTS_DIR)
    out = _report_path(n)

    dates = build.week_dates(cfg, n)
    try:
        texts = docxfill.docx_paragraph_texts(out)
        verified = any(t.strip() == f"Dates: {dates}" for t in texts) and paragraphs[0] in texts
    except Exception as exc:
        verified = False
        print(f"WARNING: could not re-read generated file: {exc}", file=sys.stderr)
    if not verified:
        print("ERROR: verification failed (prose is saved; try `rebuild`)", file=sys.stderr)
        return 1

    print(f"Saved Week {n} prose and generated {os.path.relpath(out, BASE)}")
    print(f"Weeks included (cumulative): {', '.join(str(w) for w in range(1, n + 1) if w in built)}")
    print(f"Refreshed {len(built)} report file(s). Template left untouched.")
    return 0


def cmd_rebuild(cfg, args):
    built = build.build_all(_template_path(cfg), cfg, CONTENT_DIR, REPORTS_DIR)
    if not built:
        print("No saved weeks to rebuild.")
        return 0
    print(f"Rebuilt {len(built)} report file(s): {', '.join(f'Week-{n}.docx' for n in built)}")
    return 0


# --------------------------------------------------------------------------- #
def _greet_setup():
    print("👋 Welcome! This tool writes your weekly internship report into the Word form.")
    print()
    print("First-time setup:")
    print(f"  1. Copy {os.path.basename(EXAMPLE_PATH)} to report.config.json")
    print("  2. Fill in your details (name, company, supervisor, dates, your repos)")
    print("  3. Read README.md, then run: python3 report.py status")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Weekly internship report tool")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "gather"):
        p = sub.add_parser(name)
        p.add_argument("--week", type=int, default=None)
    p_fill = sub.add_parser("fill")
    p_fill.add_argument("--week", type=int, default=None)
    p_fill.add_argument("--content-file", default=None)  # optional: else read reports/content/week-N.md
    sub.add_parser("rebuild")
    p_disc = sub.add_parser("discover")
    p_disc.add_argument("--dir", default=None, help="directory to scan (overrides config searchDirs)")
    args = parser.parse_args(argv)

    if not os.path.exists(CONFIG_PATH):
        _greet_setup()
        return 2
    try:
        cfg = config.load_config(CONFIG_PATH)
    except config.ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2
    if config.looks_unfilled(cfg):
        print("⚠ report.config.json still has placeholder values — please edit it first.", file=sys.stderr)
        if args.command == "fill":
            return 2

    try:
        if args.command == "status":
            return cmd_status(cfg, args) or 0
        if args.command == "gather":
            return cmd_gather(cfg, args) or 0
        if args.command == "fill":
            return cmd_fill(cfg, args) or 0
        if args.command == "rebuild":
            return cmd_rebuild(cfg, args) or 0
        if args.command == "discover":
            return cmd_discover(cfg, args) or 0
    except (ValueError, OSError) as exc:  # malformed/missing template or file-system issue
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
