from unittest import TestCase
from parsing import DocxParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class DocxParserTest(TestCase):

    def test_parse_content(self):

        parser = DocxParser([], 1000, dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/docx1.docx")

        self.assertEqual(len(info["content"]), 1000)
