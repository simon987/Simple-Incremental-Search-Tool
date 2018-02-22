from unittest import TestCase
from indexer import Indexer


class IndexerTest(TestCase):

    def test_create_bulk_query(self):

        docs = [{"name": "doc1"}, {"name": "doc2"}]

        result = Indexer.create_bulk_index_string(docs, "indexName")

        self.assertEqual(result, '{"index":{"_index":"indexName","_type":"file"}}\n'
                                 '{"name": "doc1"}\n'
                                 '{"index":{"_index":"indexName","_type":"file"}}\n'
                                 '{"name": "doc2"}\n')
