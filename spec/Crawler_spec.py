from unittest import TestCase

from parsing import GenericFileParser, Sha1CheckSumCalculator, ExtensionMimeGuesser
from crawler import Crawler


class CrawlerTest(TestCase):

    def test_dir_walk(self):

        c = Crawler([GenericFileParser([Sha1CheckSumCalculator()])])

        c.crawl("test_folder")

        self.assertEqual(len(c.documents), 31)

    def test_file_count(self):

        c = Crawler([])

        self.assertEqual(c.countFiles("test_folder"), 31)
