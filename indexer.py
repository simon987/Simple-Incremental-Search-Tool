import json
import elasticsearch
from threading import Thread
import subprocess
import requests


class Indexer:

    def __init__(self, index: str):

        self.index_name = index
        self.es = elasticsearch.Elasticsearch()

        try:
            requests.head("http://localhost:9200")
            print("elasticsearch is already running")

        except requests.exceptions.ConnectionError:
            import time
            t = Thread(target=Indexer.run_elasticsearch)
            t.daemon = True
            t.start()

            time.sleep(10)
            self.init()

    @staticmethod
    def run_elasticsearch():
        subprocess.Popen(["elasticsearch/bin/elasticsearch"])

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
        self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name)
        self.es.indices.close(index=self.index_name)

        self.es.indices.put_settings(body={
            "analysis": {"tokenizer": {"path_tokenizer": {"type": "path_hierarchy"}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"tokenizer": {"my_nGram_tokenizer": {"type": "nGram", "min_gram": 3, "max_gram": 3}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"analyzer": {"path_analyser": {"tokenizer": "path_tokenizer", "filter": ["lowercase"]}}}},
            index=self.index_name)
        self.es.indices.put_settings(body={
            "analysis": {"analyzer": {"my_nGram": {"tokenizer": "my_nGram_tokenizer", "filter": ["lowercase",
                                                                                                 "asciifolding"]}}}},
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
            "directory": {"type": "short"},
            "name": {"analyzer": "my_nGram", "type": "text"},
            "album": {"analyzer": "my_nGram", "type": "text"},
            "artist": {"analyzer": "my_nGram", "type": "text"},
            "title": {"analyzer": "my_nGram", "type": "text"},
            "genre": {"analyzer": "my_nGram", "type": "text"},
            "album_artist": {"analyzer": "my_nGram", "type": "text"},
        }}, doc_type="file", index=self.index_name)

        self.es.indices.open(index=self.index_name)

        print("Initialised elesticsearch")
