"""Read commits from a git repository for a date range.

Splitting the raw `git log` output on a control character (instead of a normal
delimiter) keeps commit subjects intact even when they contain commas, pipes, or
dashes. The argument builder and parser are pure so they can be tested without a
real repository; `run_log` is the thin I/O wrapper around them.
"""

import os
import shutil
import subprocess

# ASCII unit separator — will never appear inside a commit subject.
SEP = "\x1f"


def log_args(since: str, until: str, author=None):
    """git-log flags for [since, until) across all refs, excluding merges."""
    args = [
        "log",
        "--all",
        "--no-merges",
        f"--since={since}",
        f"--until={until}",
        f"--pretty=format:%H{SEP}%ad{SEP}%an{SEP}%s",
        "--date=short",
    ]
    if author:
        args.append(f"--author={author}")
    return args


def parse_log(raw: str):
    """Parse raw `git log` output into a list of commit dicts."""
    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split(SEP)
        if len(parts) < 4:
            continue
        commits.append(
            {
                "hash": parts[0],
                "date": parts[1],
                "author": parts[2],
                # rejoin in the unlikely event SEP slipped into the subject
                "subject": SEP.join(parts[3:]),
            }
        )
    return commits


def dedupe(commits):
    """Drop commits with a repeated hash, preserving first-seen order."""
    seen = set()
    out = []
    for c in commits:
        h = c.get("hash")
        if h in seen:
            continue
        seen.add(h)
        out.append(c)
    return out


def _git_bin():
    # Prefer PATH; fall back to the known macOS path only if it exists, since
    # the sandbox occasionally strips PATH.
    found = shutil.which("git")
    if found:
        return found
    if os.path.exists("/usr/bin/git"):
        return "/usr/bin/git"
    return None


def run_log(repo: str, since: str, until: str, author=None):
    """Return (commits, error). On any failure, commits is [] and error is set."""
    git = _git_bin()
    if git is None:
        return [], "git executable not found (install git or add it to PATH)"
    try:
        result = subprocess.run(
            [git, "-C", repo] + log_args(since, until, author),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return [], f"{repo}: git log timed out (>30s)"
    except Exception as exc:  # missing/unreadable repo path, etc.
        return [], f"{repo}: {exc}"
    if result.returncode != 0:
        return [], f"{repo}: {result.stderr.strip() or 'git log failed (is this a git repo?)'}"
    return dedupe(parse_log(result.stdout)), None
