from unittest import TestCase
from parsing import TikaFileParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class PdfParserTest(TestCase):

    def test_parse_content(self):

        parser = TikaFileParser([], "test_files/", 12488)

        info = parser.parse(dir_name + "/test_files/pdf1.pdf")

        self.assertEqual(len(info["content"]), 12488)
