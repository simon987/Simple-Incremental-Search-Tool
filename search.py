import elasticsearch
from elasticsearch import helpers
import requests


class Search:

    def __init__(self, index: str):
        self.index_name = index
        self.es = elasticsearch.Elasticsearch()

        try:
            requests.head("http://localhost:9200")
            print("elasticsearch is already running")
        except:
            print("elasticsearch is not running")

    def get_all_documents(self, dir_id: int):

        return helpers.scan(client=self.es,
                            query={"_source": {"includes": ["path", "name"]},
                                   "query": {"term": {"directory": dir_id}}},
                            index=self.index_name)

