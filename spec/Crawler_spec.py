from unittest import TestCase

from parsing import GenericFileParser, Sha1CheckSumCalculator, ExtensionMimeGuesser
from crawler import Crawler


class CrawlerTest(TestCase):

    def test_dir_walk(self):
        c = Crawler([GenericFileParser([Sha1CheckSumCalculator()], ExtensionMimeGuesser())])

        c.crawl("test_folder")

        self.assertEqual(len(c.documents), 28)

    def test_get_parser_by_ext(self):

        c = Crawler([GenericFileParser([Sha1CheckSumCalculator()], ExtensionMimeGuesser())])

        self.assertIsInstance(c.get_parser_by_ext("any"), GenericFileParser)

        # todo add more parsers here
