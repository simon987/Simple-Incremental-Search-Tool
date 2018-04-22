from unittest import TestCase
from parsing import FontParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class FontParserTest(TestCase):

    def test_parse_name_trueType(self):

        parser = FontParser([], dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/truetype1.ttf")

        self.assertEqual(info["content"], "Liberation Mono Bold")

    def test_parse_name_openType(self):

        parser = FontParser([], dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/opentype1.otf")

        self.assertEqual(info["content"], "Linux Biolinum Keyboard O")

    def test_parse_name_woff(self):

        parser = FontParser([], dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/woff.woff")

        self.assertEqual(info["content"], "Heart of Gold")

    def test_parse_name_woff2(self):

        parser = FontParser([], dir_name + "test_files/")

        info = parser.parse(dir_name + "/test_files/woff2.woff2")

        self.assertEqual(info["content"], "Heart of Gold")
