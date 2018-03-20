from unittest import TestCase
from indexer import Indexer


class IndexerTest(TestCase):

    def test_create_bulk_query(self):

        docs = [{"name": "doc1"}, {"name": "doc2"}]

        result = Indexer.create_bulk_index_string(docs, 1)

        self.assertTrue(result == '{"index":{}}\n'
                                  '{"directory": 1, "name": "doc1"}\n'
                                  '{"index":{}}\n'
                                  '{"directory": 1, "name": "doc2"}\n'
                        or result == '{"index":{}}\n'
                                  '{"name": "doc1", "directory": 1}\n'
                                  '{"index":{}}\n'
                                  '{"name": "doc2", "directory": 1}\n')

