from unittest import TestCase
from parsing import TextFileParser


class TextFileParserTest(TestCase):

    def test_parse_csv(self):

        parser = TextFileParser([], 1234, "test_files/")

        info = parser.parse("test_files/text.csv")

        self.assertTrue(info["content"].startswith("rosbagTimestamp,header,seq,stamp,secs,nsecs,"))
        self.assertEqual(len(info["content"]), 1309)  # Size is larger because of html escaping
        self.assertEqual(info["encoding"], "ascii")
