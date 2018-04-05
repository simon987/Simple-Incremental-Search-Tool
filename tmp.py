from elasticsearch import Elasticsearch
from indexer import Indexer
import json
from crawler import Crawler
from indexer import Indexer
from parsing import GenericFileParser, Sha256CheckSumCalculator, ExtensionMimeGuesser

es = Elasticsearch()
1

# reset
es.indices.delete(index="test")
es.indices.create(index="test")
es.indices.close(index="test")


# # config
es.indices.put_settings(body='{"analysis": {"analyzer": {"path_analyser": {'
                             '"tokenizer": "path_tokenizer"}}, "tokenizer": {"path_tokenizer": {'
                             '"type": "path_hierarchy"}}}}', index="test")

es.indices.put_mapping(body='{"properties": {'
                            '"name": {"type": "text", "analyzer": "path_analyser", "copy_to": "suggest-path"},'
                            '"suggest-path": {"type": "completion", "analyzer": "keyword"},'
                            '"mime": {"type": "keyword"}'
                            '}}', index="test",doc_type="file" )

es.indices.open(index="test")


# add docs

# crawler = Crawler([GenericFileParser([Sha256CheckSumCalculator()], ExtensionMimeGuesser())])
# crawler.crawl("spec/test_folder")
#
# indexer = Indexer("test")
#
# indexer.index(crawler.documents)

# search
# print(es.search("test", "file", '{"query": {"term": {"name": "spec/test_folder/sub2/"}}}'))
# print(es.search("test", "file", '{"query": {"match_all": {}}, "aggs": {"test": {"terms": {"field": "mime"}}}}'))
# suggest = es.search("test", "file", '{"suggest": {"path-suggest": {"prefix": "spec/test_folder/sub", "completion": {"field": "suggest-path"}}}}')
#
# print(suggest["suggest"]["path-suggest"])
#
# for hit in suggest["suggest"]["path-suggest"][0]["options"]:
#     print(hit["text"])

# indexer = Indexer("test")

# import time
# time.sleep(10)

c = Crawler([])
c.countFiles("/")
