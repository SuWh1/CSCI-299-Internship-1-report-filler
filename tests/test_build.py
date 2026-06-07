import os
import tempfile
import unittest

from reportlib import build, docxfill

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "blank-form.docx")

CFG = {
    "student": {"name": "Dauren Apas"},
    "company": {"name": "ESEP", "location": "Astana"},
    "position": {"department": "Eng", "title": "Dev", "employmentType": "Full-time"},
    "supervisor": {"name": "Bekzhan Skakov", "position": "Product Owner", "email": "b@esep.su", "phone": "+7"},
    "internship": {"startDate": "2026-06-01", "endDate": "2026-07-31"},
    "report": {"docxFile": "Summer-Internship-Report-Form.docx"},
    "tracking": {"repos": [], "authorFilter": "dauren"},
    "style": {},
}


class TestWeekDates(unittest.TestCase):
    def test_should_compute_week_dates_from_config_start(self):
        self.assertEqual(build.week_dates(CFG, 1), "June 1 – 7, 2026")
        self.assertEqual(build.week_dates(CFG, 2), "June 8 – 14, 2026")


class TestBuildReport(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.out = os.path.join(self.dir, "Week-2.docx")

    def test_should_generate_cumulative_doc_with_all_provided_weeks(self):
        build.build_report(TEMPLATE, CFG, {1: ["Week one body."], 2: ["Week two body."]}, self.out)
        texts = docxfill.docx_paragraph_texts(self.out)
        self.assertIn("Week one body.", texts)
        self.assertIn("Week two body.", texts)
        self.assertTrue(any(t.strip() == "Dates: June 1 – 7, 2026" for t in texts))
        self.assertTrue(any(t.strip() == "Dates: June 8 – 14, 2026" for t in texts))

    def test_should_fill_header_in_generated_doc(self):
        build.build_report(TEMPLATE, CFG, {1: ["x."]}, self.out)
        texts = docxfill.docx_paragraph_texts(self.out)
        self.assertTrue(any("Dauren Apas" in t for t in texts))
        self.assertTrue(any("b@esep.su" in t for t in texts))

    def test_should_create_output_file_when_missing(self):
        self.assertFalse(os.path.exists(self.out))
        build.build_report(TEMPLATE, CFG, {1: ["x."]}, self.out)
        self.assertTrue(os.path.exists(self.out))

    def test_should_not_modify_the_template(self):
        before = docxfill.read_document_xml(TEMPLATE)
        build.build_report(TEMPLATE, CFG, {1: ["x."]}, self.out)
        self.assertEqual(docxfill.read_document_xml(TEMPLATE), before)

    def test_should_produce_a_valid_openable_docx(self):
        import zipfile

        build.build_report(TEMPLATE, CFG, {1: ["x."]}, self.out)
        with zipfile.ZipFile(self.out) as z:
            self.assertIsNone(z.testzip())
            self.assertIn("word/document.xml", z.namelist())

    def test_should_regenerate_idempotently(self):
        build.build_report(TEMPLATE, CFG, {1: ["First."]}, self.out)
        build.build_report(TEMPLATE, CFG, {1: ["Second."]}, self.out)
        texts = docxfill.docx_paragraph_texts(self.out)
        self.assertIn("Second.", texts)
        self.assertNotIn("First.", texts)


class TestBuildAll(unittest.TestCase):
    def setUp(self):
        from reportlib import contentstore as cs

        self.dir = tempfile.mkdtemp()
        self.content = os.path.join(self.dir, "content")
        self.reports = self.dir
        for w in (1, 2, 3):
            cs.write_content(self.content, w, [f"Week {w} body."])

    def test_should_build_one_cumulative_file_per_week(self):
        build.build_all(TEMPLATE, CFG, self.content, self.reports)
        for w in (1, 2, 3):
            self.assertTrue(os.path.exists(os.path.join(self.reports, f"Week-{w}.docx")))
        t3 = docxfill.docx_paragraph_texts(os.path.join(self.reports, "Week-3.docx"))
        self.assertEqual([x for x in ("Week 1 body.", "Week 2 body.", "Week 3 body.") if x in t3],
                         ["Week 1 body.", "Week 2 body.", "Week 3 body."])
        t1 = docxfill.docx_paragraph_texts(os.path.join(self.reports, "Week-1.docx"))
        self.assertIn("Week 1 body.", t1)
        self.assertNotIn("Week 2 body.", t1)

    def test_should_refresh_later_files_when_an_earlier_week_changes(self):
        from reportlib import contentstore as cs

        build.build_all(TEMPLATE, CFG, self.content, self.reports)
        cs.write_content(self.content, 1, ["Week 1 EDITED."])
        build.build_all(TEMPLATE, CFG, self.content, self.reports)
        t3 = docxfill.docx_paragraph_texts(os.path.join(self.reports, "Week-3.docx"))
        self.assertIn("Week 1 EDITED.", t3)
        self.assertNotIn("Week 1 body.", t3)


class TestHeaderMapping(unittest.TestCase):
    """Regression: loose 'address' token must not steal the contact row."""

    def _cells(self):
        root = docxfill.parse_xml(docxfill.read_document_xml(TEMPLATE))
        docxfill.fill_header(root, build.header_mapping(CFG))
        table = root.find(docxfill.qn("body")).find(docxfill.qn("tbl"))
        out = {}
        for row in table.findall(docxfill.qn("tr")):
            cells = row.findall(docxfill.qn("tc"))
            out[docxfill._cell_text(cells[0]).lower()] = docxfill._cell_text(cells[-1])
        return out

    def test_should_put_email_in_contact_row(self):
        contact = next(v for k, v in self._cells().items() if "contact information" in k)
        self.assertIn("b@esep.su", contact)

    def test_should_put_location_in_work_location_row(self):
        loc = next(v for k, v in self._cells().items() if "work location" in k)
        self.assertEqual(loc, "Astana")


if __name__ == "__main__":
    unittest.main()
