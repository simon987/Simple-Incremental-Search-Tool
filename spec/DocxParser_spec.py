from unittest import TestCase
from parsing import DocxParser


class DocxParserTest(TestCase):

    def test_parse_content(self):

        parser = DocxParser([], 1000, "test_files/")

        info = parser.parse("test_files/docx1.docx")

        self.assertEqual(len(info["content"]), 1000)
