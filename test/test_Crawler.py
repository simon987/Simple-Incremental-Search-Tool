from unittest import TestCase

from parsing import GenericFileParser, Sha1CheckSumCalculator, ExtensionMimeGuesser
from crawler import Crawler
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class CrawlerTest(TestCase):

    def test_dir_walk(self):

        c = Crawler([GenericFileParser([Sha1CheckSumCalculator()], "test_files/")])

        c.crawl(dir_name + "/test_folder")

        self.assertEqual(len(c.documents), 31)

    def test_file_count(self):

        c = Crawler([])

        self.assertEqual(c.countFiles(dir_name + "/test_folder"), 31)

    def test_path(self):

        c = Crawler([GenericFileParser([], dir_name + "/test_folder")])
        c.crawl(dir_name + "/test_folder")

        file_count_in_sub2 = 0

        for doc in c.documents:
            if doc["path"] == "sub2":
                file_count_in_sub2 += 1

        self.assertEqual(file_count_in_sub2, 2)
