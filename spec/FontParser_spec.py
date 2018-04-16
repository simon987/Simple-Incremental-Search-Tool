from unittest import TestCase
from parsing import FontParser


class FontParserTest(TestCase):

    def test_parse_name_trueType(self):

        parser = FontParser([])

        info = parser.parse("test_files/truetype1.ttf")

        self.assertEqual(info["content"], "Liberation Mono Bold")

    def test_parse_name_openType(self):

        parser = FontParser([])

        info = parser.parse("test_files/opentype1.otf")

        self.assertEqual(info["content"], "Linux Biolinum Keyboard O")

    def test_parse_name_woff(self):

        parser = FontParser([])

        info = parser.parse("test_files/woff.woff")

        self.assertEqual(info["content"], "Heart of Gold")

    def test_parse_name_woff2(self):

        parser = FontParser([])

        info = parser.parse("test_files/woff2.woff2")

        self.assertEqual(info["content"], "Heart of Gold")
