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

        self.es.indices.put_settings(body='{"analysis": {"analyzer": {"path_analyser": {'
                                     '"tokenizer": "path_tokenizer"}}, "tokenizer": {"path_tokenizer": {'
                                     '"type": "path_hierarchy"}}}}', index=self.index_name)

        self.es.indices.put_mapping(body='{"properties": {'
                                    '"name": {"type": "text", "analyzer": "path_analyser", "copy_to": "suggest-path"},'
                                    '"suggest-path": {"type": "completion", "analyzer": "keyword"},'
                                    '"mime": {"type": "keyword"},'
                                    '"directory": {"type": "keyword"}'
                                    '}}', doc_type="file", index=self.index_name)

        self.es.indices.open(index=self.index_name)

        print("Initialised elesticsearch")
