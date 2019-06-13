from unittest import TestCase
from parsing import TikaFileParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class EbookParserTest(TestCase):

    def test_parse_content(self):

        parser = TikaFileParser([], dir_name + "/test_files/", 1000)

        info = parser.parse(dir_name + "/test_files/epub1.epub")

        self.assertEqual(len(info["content"]), 1000)
