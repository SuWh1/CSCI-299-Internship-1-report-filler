"""Find git repositories on disk so a student can pick their internship ones.

A student may have many repos — personal projects, coursework, other jobs. This
scanner lists candidate repos under the configured search directories; the report
tool then counts the student's commits in each so the AI can show the list and
ask which belong to *this* internship. The choice is the student's, never guessed.
"""

import os

# Directories never worth descending into when hunting for project repos.
_PRUNE = {
    "node_modules", "Library", "Applications", "Pods", ".Trash",
    "venv", ".venv", "dist", "build", "__pycache__", ".cache",
    "Movies", "Music", "Pictures",
}


def find_git_repos(search_dirs, max_depth: int = 6):
    """Return sorted paths of git repos under any of `search_dirs`.

    Stops descending once a repo is found (no nested-repo noise), prunes heavy
    folders, and bounds depth so a scan of a home directory stays reasonable.
    """
    repos = []
    for raw in search_dirs:
        base = os.path.expanduser(raw)
        if not os.path.isdir(base):
            continue
        base_depth = base.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(base):
            if ".git" in dirnames or ".git" in filenames:
                repos.append(dirpath)
                dirnames[:] = []  # don't descend into a repository
                continue
            if dirpath.count(os.sep) - base_depth >= max_depth:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in _PRUNE and not d.startswith(".")]
    return sorted(set(repos))
