import os
import shutil
import tempfile
import unittest

from reportlib import docxfill

# Use a frozen blank copy, not the live form, so tests stay isolated from
# whatever has actually been filled into the working document.
FORM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "blank-form.docx")


class TestDocxFill(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "form.docx")
        shutil.copy(FORM, self.path)
        self.root = docxfill.parse_xml(docxfill.read_document_xml(self.path))

    # --- error handling ---
    def test_should_raise_friendly_error_for_non_docx_file(self):
        bad = os.path.join(self.dir, "not.docx")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("this is not a zip")
        with self.assertRaises(ValueError):
            docxfill.read_document_xml(bad)

    def test_should_raise_friendly_error_for_missing_file(self):
        with self.assertRaises(ValueError):
            docxfill.read_document_xml("/no/such/file.docx")

    # --- reading ---
    def test_should_read_week_headings_from_body(self):
        texts = docxfill.all_texts(self.root)
        for n in range(1, 6):
            self.assertIn(f"Interim Report Week {n}", texts)
        self.assertIn("Final Internship Report", texts)

    # --- header ---
    def test_should_fill_empty_header_value_cells(self):
        mapping = [(["student name"], "Dauren Apas"), (["company name"], "ESEP")]
        filled = docxfill.fill_header(self.root, mapping)
        self.assertEqual(filled, 2)
        texts = docxfill.all_texts(self.root)
        self.assertTrue(any("Dauren Apas" in t for t in texts))
        self.assertTrue(any("ESEP" in t for t in texts))

    def test_should_not_overwrite_already_filled_header_cell(self):
        mapping = [(["student name"], "First Name")]
        docxfill.fill_header(self.root, mapping)
        again = docxfill.fill_header(self.root, [(["student name"], "Second Name")])
        self.assertEqual(again, 0)
        texts = docxfill.all_texts(self.root)
        self.assertTrue(any("First Name" in t for t in texts))
        self.assertFalse(any("Second Name" in t for t in texts))

    # --- filling an existing week ---
    def test_should_set_dates_and_insert_content_and_remove_prompt(self):
        docxfill.fill_or_append_week(self.root, 1, "June 1 – 7, 2026", ["Para one.", "Para two."])
        texts = docxfill.all_texts(self.root)
        self.assertTrue(any(t.strip() == "Dates: June 1 – 7, 2026" for t in texts))
        self.assertIn("Para one.", texts)
        self.assertIn("Para two.", texts)
        # week 1's prompt is gone, the other four remain
        prompts = [t for t in texts if t.startswith("Describe the tasks")]
        self.assertEqual(len(prompts), 4)

    def test_should_be_idempotent_when_week_is_refilled(self):
        docxfill.fill_or_append_week(self.root, 1, "June 1 – 7, 2026", ["First version."])
        docxfill.fill_or_append_week(self.root, 1, "June 1 – 7, 2026", ["Second version."])
        texts = docxfill.all_texts(self.root)
        self.assertIn("Second version.", texts)
        self.assertNotIn("First version.", texts)

    # --- appending a brand new week ---
    def test_should_append_new_week_before_final_report(self):
        docxfill.fill_or_append_week(self.root, 6, "July 6 – 12, 2026", ["Brand new week."])
        texts = docxfill.all_texts(self.root)
        self.assertIn("Interim Report Week 6", texts)
        self.assertIn("Brand new week.", texts)
        self.assertLess(
            texts.index("Interim Report Week 6"),
            texts.index("Final Internship Report"),
        )

    # --- file round trip ---
    def test_should_write_backup_and_reextract_content(self):
        docxfill.fill_or_append_week(self.root, 1, "June 1 – 7, 2026", ["Hello world."])
        docxfill.write_docx(self.path, docxfill.serialize_xml(self.root), make_backup=True)
        self.assertTrue(os.path.exists(self.path + ".bak"))
        texts = docxfill.docx_paragraph_texts(self.path)
        self.assertIn("Hello world.", texts)
        self.assertTrue(any(t.strip() == "Dates: June 1 – 7, 2026" for t in texts))

    def test_should_produce_a_still_openable_docx(self):
        # a valid docx must keep its content-types part after rewrite
        docxfill.fill_or_append_week(self.root, 1, "June 1 – 7, 2026", ["Check."])
        docxfill.write_docx(self.path, docxfill.serialize_xml(self.root), make_backup=False)
        import zipfile

        with zipfile.ZipFile(self.path) as z:
            self.assertIn("[Content_Types].xml", z.namelist())
            self.assertIn("word/document.xml", z.namelist())
            self.assertIsNone(z.testzip())


if __name__ == "__main__":
    unittest.main()
