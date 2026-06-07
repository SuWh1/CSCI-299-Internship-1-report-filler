"""Load and validate report.config.json — the one file a new student edits.

Everything that varies between students (name, company, supervisor, dates,
which repositories to read) lives in the config so the rest of the tool stays
generic and reusable.
"""

import json
import os
from datetime import date

REQUIRED_KEYS = ["student", "company", "supervisor", "internship", "report", "tracking"]

# Nested fields the report actually reads — validated up front so a half-filled
# config fails with a clear message instead of a KeyError mid-run. (location is
# optional; the header renders fine without it.)
REQUIRED_FIELDS = [
    ("student", "name"),
    ("company", "name"),
    ("supervisor", "name"),
    ("supervisor", "position"),
    ("supervisor", "email"),
    ("supervisor", "phone"),
    ("report", "docxFile"),
]


class ConfigError(Exception):
    """Raised when the config is missing or malformed — surfaced to the user."""


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"Config not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config is not valid JSON: {exc}") from exc
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict) -> bool:
    for key in REQUIRED_KEYS:
        if key not in cfg:
            raise ConfigError(f"Missing required config key: '{key}'")
    for section, field in REQUIRED_FIELDS:
        value = cfg.get(section)
        if not isinstance(value, dict) or not value.get(field):
            raise ConfigError(f"Missing required config field: {section}.{field}")
    for field in ("startDate", "endDate"):
        value = cfg["internship"].get(field)
        try:
            date.fromisoformat(value)
        except (TypeError, ValueError):
            raise ConfigError(f"internship.{field} must be YYYY-MM-DD, got {value!r}")
    # An empty list is allowed: a non-coding internship can report from notes only.
    repos = cfg["tracking"].get("repos")
    if not isinstance(repos, list):
        raise ConfigError("tracking.repos must be a list of paths (it may be empty)")
    search_dirs = cfg["tracking"].get("searchDirs")
    if search_dirs is not None and not isinstance(search_dirs, list):
        raise ConfigError("tracking.searchDirs must be a list of paths")
    return True


# Strings the shipped example config uses; their presence means it's unedited.
_PLACEHOLDER_TOKENS = (
    "your full name",
    "your company",
    "yyyy-mm-dd",
    "your-git-username",
    "supervisor name",
    "path/to/your",
)


def looks_unfilled(cfg: dict) -> bool:
    """True if the config still contains example placeholder values."""
    blob = json.dumps(cfg, ensure_ascii=False).lower()
    return any(token in blob for token in _PLACEHOLDER_TOKENS)


def expand_path(path: str) -> str:
    return os.path.expanduser(path)


def start_date(cfg: dict) -> date:
    return date.fromisoformat(cfg["internship"]["startDate"])


def end_date(cfg: dict) -> date:
    return date.fromisoformat(cfg["internship"]["endDate"])
