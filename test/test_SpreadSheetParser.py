from unittest import TestCase
from parsing import TikaFileParser

import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class PdfParserTest(TestCase):

    def test_parse_content_xls(self):

        parser = TikaFileParser([], "test_files/", 1500)

        info = parser.parse(dir_name + "/test_files/xls1.xls")

        self.assertEqual(len(info["content"]), 1500)

    def test_parse_content_xlsx(self):

        parser = TikaFileParser([], "test_files/", 1500)

        info = parser.parse(dir_name + "/test_files/xlsx1.xlsx")

        self.assertEqual(len(info["content"]), 1500)
