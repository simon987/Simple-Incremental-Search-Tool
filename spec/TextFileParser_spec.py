from unittest import TestCase
from parsing import TextFileParser


class TextFileParserTest(TestCase):

    def test_parse_csv(self):

        parser = TextFileParser([], 12345)

        info = parser.parse("test_files/text.csv")

        self.assertTrue(info["content"].startswith("rosbagTimestamp,header,seq,stamp,secs,nsecs,"))
        self.assertEqual(len(info["content"]), 12345)
        self.assertEqual(info["encoding"], "ascii")
