from unittest import TestCase
from parsing import EbookParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class EbookParserTest(TestCase):

    def test_parse_content(self):

        parser = EbookParser([], 1000, dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/epub1.epub")

        self.assertEqual(len(info["content"]), 1000)
