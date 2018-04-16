from unittest import TestCase
from parsing import PdfFileParser


class PdfParserTest(TestCase):

    def test_parse_content(self):

        parser = PdfFileParser([], 12488)

        info = parser.parse("test_files/pdf1.pdf")

        self.assertEqual(len(info["content"]), 12488)
        self.assertTrue(info["content"].startswith("Rabies\n03/11/2011\nRabies"))
