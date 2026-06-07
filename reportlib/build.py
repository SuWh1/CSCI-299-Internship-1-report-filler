"""Generate a weekly report .docx from the pristine template.

The template form is never edited. Each report is rendered fresh from three
inputs — the template (structure), the config (header), and the approved prose
per week — so output is fully reproducible and a cumulative file (Weeks 1..N)
is just "render every week up to N".
"""

import os

from . import config as config_mod
from . import contentstore, docxfill, weeks


def header_mapping(cfg: dict):
    """Ordered (label-substrings, value) pairs for the header table.

    Each row is matched on a phrase unique to its label. Loose tokens like
    'address' are avoided: 'address' also appears in 'corporate email address'
    and would otherwise steal the supervisor-contact row.
    """
    s = cfg["supervisor"]
    comp = cfg["company"]
    span = (
        f"{weeks.format_full(config_mod.start_date(cfg))} – "
        f"{weeks.format_full(config_mod.end_date(cfg))}"
    )
    return [
        (["student name"], cfg["student"]["name"]),
        (["company name"], comp["name"]),
        (["work location"], comp.get("location", "")),
        (["name and position"], f'{s["name"]}, {s["position"]}'),
        (["contact information"], f'{s["email"]}, {s["phone"]}'),
        (["start/end"], span),
    ]


def week_dates(cfg: dict, n: int) -> str:
    first, last = weeks.week_bounds(config_mod.start_date(cfg), n)
    return weeks.format_range(first, last)


def build_report(template_path: str, cfg: dict, weeks_content: dict, out_path: str) -> str:
    """Render `out_path` from the template with the header and every week in
    `weeks_content` ({week_number: [paragraphs]}) filled. Template untouched."""
    root = docxfill.parse_xml(docxfill.read_document_xml(template_path))
    docxfill.fill_header(root, header_mapping(cfg))
    for n in sorted(weeks_content):
        docxfill.fill_or_append_week(root, n, week_dates(cfg, n), weeks_content[n])
    docxfill.write_docx(
        out_path,
        docxfill.serialize_xml(root),
        make_backup=False,  # output is reproducible from sources; no backup needed
        source=template_path,
    )
    return out_path


def report_path(reports_dir: str, n: int) -> str:
    return os.path.join(reports_dir, f"Week-{n}.docx")


def build_all(template_path: str, cfg: dict, content_dir: str, reports_dir: str):
    """Regenerate every weekly report from the content store.

    Rebuilding all of them (not just the one just edited) keeps the cumulative
    files consistent: editing week 1 refreshes week 1's text inside Week-2.docx,
    Week-3.docx, and so on.
    """
    done = contentstore.existing_weeks(content_dir)
    if done:
        os.makedirs(reports_dir, exist_ok=True)
    for n in done:
        build_report(template_path, cfg, contentstore.weeks_content(content_dir, upto=n), report_path(reports_dir, n))
    return done
