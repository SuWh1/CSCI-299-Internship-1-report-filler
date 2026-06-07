"""Edit the university .docx form in place using only the standard library.

A .docx is a zip of XML parts; the report text lives in word/document.xml. We
parse that part, fill the header table and the week sections, then rewrite the
zip leaving every other part byte-for-byte untouched. New week blocks are cloned
from the form's own existing paragraphs so appended weeks keep the original
fonts and spacing.

Zero third-party dependencies on purpose: any student can run this after a plain
`git pull`, with nothing to install.
"""

import copy
import os
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_DOC_PART = "word/document.xml"
_WEEK_HEADING = re.compile(r"^Interim Report Week \d+$")
_FINAL_HEADING = "Final Internship Report"
_DECLARATION = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'


def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"


# --------------------------------------------------------------------------- #
# XML (de)serialization
# --------------------------------------------------------------------------- #
def parse_xml(text: str):
    # Register declared namespace prefixes so serialization round-trips them
    # (otherwise ElementTree renames w: to ns0: and Word rejects the file).
    for prefix, uri in re.findall(r'xmlns:(\w+)="([^"]+)"', text):
        ET.register_namespace(prefix, uri)
    default = re.search(r'\sxmlns="([^"]+)"', text)
    if default:
        ET.register_namespace("", default.group(1))
    return ET.fromstring(text)


def serialize_xml(root) -> str:
    return _DECLARATION + ET.tostring(root, encoding="unicode")


# --------------------------------------------------------------------------- #
# Paragraph helpers
# --------------------------------------------------------------------------- #
def para_text(p) -> str:
    return "".join(t.text or "" for t in p.iter(qn("t")))


def set_para_text(p, text: str):
    """Replace a paragraph's text with `text`, keeping its first run's formatting."""
    runs = p.findall(qn("r"))
    if runs:
        first = runs[0]
        for extra in runs[1:]:
            p.remove(extra)
        for child in list(first):
            if child.tag in (qn("t"), qn("br"), qn("tab")):
                first.remove(child)
        run = first
    else:
        run = ET.SubElement(p, qn("r"))
    t = ET.SubElement(run, qn("t"))
    t.set(_XML_SPACE, "preserve")
    t.text = text
    return p


def clone_para(template, text: str):
    new = copy.deepcopy(template)
    set_para_text(new, text)
    return new


def _body(root):
    body = root.find(qn("body"))
    if body is None:
        raise ValueError("Document is malformed: missing <w:body>")
    return body


def body_children(root):
    return list(_body(root))


def all_texts(root):
    """Every paragraph's text in document order (includes table cells)."""
    return [para_text(p) for p in _body(root).iter(qn("p"))]


def _find_para(root, predicate):
    for p in _body(root).iter(qn("p")):
        if predicate(para_text(p).strip()):
            return p
    return None


# --------------------------------------------------------------------------- #
# Header table
# --------------------------------------------------------------------------- #
def _cell_text(tc) -> str:
    return " ".join(para_text(p) for p in tc.findall(qn("p"))).strip()


def _set_cell_text(tc, text: str):
    cells = tc.findall(qn("p"))
    if cells:
        set_para_text(cells[0], text)
    else:
        set_para_text(ET.SubElement(tc, qn("p")), text)


def header_value_texts(root):
    """Text of each header row's value cell (for status reporting)."""
    table = _body(root).find(qn("tbl"))
    if table is None:
        return []
    out = []
    for row in table.findall(qn("tr")):
        cells = row.findall(qn("tc"))
        if len(cells) >= 2:
            out.append(_cell_text(cells[-1]))
    return out


def fill_header(root, mapping) -> int:
    """Fill empty value cells of the header table.

    `mapping` is an ordered list of (label_substrings, value). For each table
    row, the first cell's text is matched (case-insensitively) against the
    substrings and the value is written into the last cell — but only if that
    cell is still empty, so re-running never clobbers existing answers.
    """
    table = _body(root).find(qn("tbl"))
    if table is None:
        return 0
    filled = 0
    for row in table.findall(qn("tr")):
        cells = row.findall(qn("tc"))
        if len(cells) < 2:
            continue
        label = _cell_text(cells[0]).lower()
        for substrings, value in mapping:
            if any(s in label for s in substrings):
                if not _cell_text(cells[-1]):
                    _set_cell_text(cells[-1], value)
                    filled += 1
                break
    return filled


# --------------------------------------------------------------------------- #
# Week sections
# --------------------------------------------------------------------------- #
def _is_para(e):
    return e.tag == qn("p")


def _heading_template(root):
    return _find_para(root, lambda t: bool(_WEEK_HEADING.match(t)))


def _dates_template(root):
    return _find_para(root, lambda t: t.startswith("Dates:"))


def _body_template(root):
    # A normal-body paragraph that the fill process never deletes, so it stays
    # available as a formatting template across repeated runs.
    for prefix in ("Write an overview", "Please submit", "Describe the tasks"):
        found = _find_para(root, lambda t, p=prefix: t.startswith(p))
        if found is not None:
            return found
    return None


def _content_paragraphs(root, content_paras):
    template = _body_template(root)
    if template is None:
        raise ValueError("Template has no normal paragraph to model body text on — is the .docx the right form?")
    paras = [clone_para(template, c) for c in content_paras]
    paras.append(clone_para(template, ""))  # trailing blank line for spacing
    return paras


def fill_or_append_week(root, n: int, dates: str, content_paras):
    """Fill week `n` if its heading exists, otherwise append a new week block."""
    body = _body(root)
    children = list(body)

    heading_idx = None
    for i, e in enumerate(children):
        if _is_para(e) and para_text(e).strip() == f"Interim Report Week {n}":
            heading_idx = i
            break

    if heading_idx is None:
        return _append_week(root, body, n, dates, content_paras)

    dates_para = None
    for i in range(heading_idx + 1, len(children)):
        if _is_para(children[i]) and para_text(children[i]).strip().startswith("Dates:"):
            dates_para = children[i]
            break
    if dates_para is None:
        raise ValueError(f"Week {n} has no 'Dates:' line to fill")

    next_idx = len(children)
    for i in range(children.index(dates_para) + 1, len(children)):
        e = children[i]
        if not _is_para(e):
            continue
        t = para_text(e).strip()
        if _WEEK_HEADING.match(t) or t == _FINAL_HEADING:
            next_idx = i
            break

    set_para_text(dates_para, f"Dates: {dates}")
    # Clear the prompt + any previously written content, then insert fresh.
    for e in children[children.index(dates_para) + 1:next_idx]:
        body.remove(e)

    insert_at = list(body).index(dates_para) + 1
    for offset, para in enumerate(_content_paragraphs(root, content_paras)):
        body.insert(insert_at + offset, para)
    return "filled"


def _append_week(root, body, n: int, dates: str, content_paras):
    heading_t = _heading_template(root)
    dates_t = _dates_template(root)
    if heading_t is None or dates_t is None:
        raise ValueError("Cannot append a week: form is missing template paragraphs")

    block = [
        clone_para(heading_t, f"Interim Report Week {n}"),
        clone_para(dates_t, f"Dates: {dates}"),
    ]
    block.extend(_content_paragraphs(root, content_paras))

    final = _find_para(root, lambda t: t == _FINAL_HEADING)
    children = list(body)
    insert_at = children.index(final) if final is not None else len(children)
    for offset, para in enumerate(block):
        body.insert(insert_at + offset, para)
    return "appended"


# --------------------------------------------------------------------------- #
# File I/O
# --------------------------------------------------------------------------- #
def read_document_xml(path: str) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            return z.read(_DOC_PART).decode("utf-8")
    except FileNotFoundError:
        raise ValueError(f"Document not found: {path}")
    except zipfile.BadZipFile:
        raise ValueError(f"Not a valid .docx file: {path}")
    except KeyError:
        raise ValueError(f"Document is missing {_DOC_PART}: {path}")


def write_docx(path: str, new_document_xml: str, make_backup: bool = True, source: str = None):
    """Write a .docx to `path`, copying all non-document parts from `source`
    (defaults to `path` itself for in-place edits).

    Passing a separate `source` lets us generate a brand-new report file from
    the pristine template without touching it. The new zip is built in a temp
    file and swapped in with an atomic os.replace, so a failure mid-write never
    leaves a half-written file.
    """
    src_path = source or path
    if make_backup and os.path.exists(path):
        shutil.copy(path, path + ".bak")
    tmp = path + ".tmp"
    try:
        with zipfile.ZipFile(src_path) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
            for item in src.infolist():
                data = src.read(item.filename)
                if item.filename == _DOC_PART:
                    data = new_document_xml.encode("utf-8")
                out.writestr(item, data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def docx_paragraph_texts(path: str):
    """All paragraph texts from a .docx on disk (used to verify a write)."""
    return all_texts(parse_xml(read_document_xml(path)))
