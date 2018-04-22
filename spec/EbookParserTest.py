from unittest import TestCase
from parsing import EbookParser


class EbookParserTest(TestCase):

    def test_parse_content(self):

        parser = EbookParser([], 1000, "test_files/")

        info = parser.parse("test_files/epub1.epub")

        self.assertEqual(len(info["content"]), 1000)
