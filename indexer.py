import json

import elasticsearch
import requests

import config


class Indexer:

    def __init__(self, index: str):

        self.index_name = index
        self.es = elasticsearch.Elasticsearch()

        requests.head(config.elasticsearch_url)
        if self.es.indices.exists(self.index_name):
            print("Index is already setup")
        else:
            print("First time setup...")
            self.init()

    @staticmethod
    def create_bulk_index_string(docs: list, directory: int):
        """
        Creates a insert string for sending to elasticsearch
        """

        result = ""

        action_string = '{"index":{}}\n'

        for doc in docs:
            doc["directory"] = directory
            result += action_string
            result += json.dumps(doc) + "\n"

        return result

    def index(self, docs: list, directory: int):
        print("Indexing " + str(len(docs)) + " docs")
        index_string = Indexer.create_bulk_index_string(docs, directory)
        self.es.bulk(body=index_string, index=self.index_name, doc_type="file", refresh="true")

    def clear(self):

        self.es.indices.delete(self.index_name)
        self.es.indices.create(self.index_name)

    def init(self):
        if self.es.indices.exists(self.index_name):
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name)
        self.es.indices.close(index=self.index_name)

        self.es.indices.put_settings(body={
            "analysis": {"tokenizer": {"path_tokenizer": {"type": "path_hierarchy"}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"tokenizer": {
                "my_nGram_tokenizer": {"type": "nGram", "min_gram": config.nGramMin, "max_gram": config.nGramMax}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"analyzer": {"path_analyser": {"tokenizer": "path_tokenizer", "filter": ["lowercase"]}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"analyzer": {"my_nGram": {"tokenizer": "my_nGram_tokenizer", "filter": ["lowercase",
                                                                                                 "asciifolding"]}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"analyzer": {"content_analyser": {"tokenizer": "standard", "filter": ["lowercase"]}}}},
            index=self.index_name)

        self.es.indices.put_mapping(body={"properties": {
            "path": {"type": "text", "analyzer": "path_analyser", "copy_to": "suggest-path"},
            "suggest-path": {"type": "completion", "analyzer": "keyword"},
            "mime": {"type": "keyword"},
            "encoding": {"type": "keyword"},
            "format_name": {"type": "keyword"},
            "format_long_name": {"type": "keyword"},
            "duration": {"type": "float"},
            "width": {"type": "integer"},
            "height": {"type": "integer"},
            "mtime": {"type": "integer"},
            "size": {"type": "long"},
            "directory": {"type": "short"},
            "name": {"analyzer": "content_analyser", "type": "text",
                     "fields": {"nGram": {"type": "text", "analyzer": "my_nGram"}}
                     },
            "album": {"analyzer": "my_nGram", "type": "text"},
            "artist": {"analyzer": "my_nGram", "type": "text"},
            "title": {"analyzer": "my_nGram", "type": "text"},
            "genre": {"analyzer": "my_nGram", "type": "text"},
            "album_artist": {"analyzer": "my_nGram", "type": "text"},
            "content": {"analyzer": "content_analyser", "type": "text"},
        }}, doc_type="file", index=self.index_name, include_type_name=True)

        self.es.indices.open(index=self.index_name)

        print("Initialised elesticsearch")
