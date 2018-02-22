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

            time.sleep(5)

    @staticmethod
    def run_elasticsearch():
        subprocess.Popen(["elasticsearch/bin/elasticsearch"])

    @staticmethod
    def create_bulk_index_string(docs: list, index_name: str):
        """
        Creates a insert string for sending to elasticsearch
        """

        result = ""

        action_string = '{"index":{"_index":"' + index_name + '","_type":"file"}}\n'

        for doc in docs:
            result += action_string
            result += json.dumps(doc) + "\n"

        return result

    def index(self, docs: list):

        index_string = self.create_bulk_index_string(docs, self.index_name)
        self.es.bulk(index_string)

    def clear(self):

        self.es.indices.delete(self.index_name)
        self.es.indices.create(self.index_name)
