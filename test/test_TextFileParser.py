from unittest import TestCase
from parsing import TextFileParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class TextFileParserTest(TestCase):

    def test_parse_csv(self):

        parser = TextFileParser([], 1234, "test_files/")

        info = parser.parse(dir_name + "/test_files/text.csv")

        self.assertTrue(info["content"].startswith("rosbagTimestamp,header,seq,stamp,secs,nsecs,"))
        self.assertEqual(len(info["content"]), 1234)
        self.assertEqual(info["encoding"], "ascii")
