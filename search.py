import elasticsearch
from elasticsearch import helpers
import requests
import json


class Search:

    def __init__(self, index: str):
        self.index_name = index
        self.es = elasticsearch.Elasticsearch()

        try:
            requests.head("http://localhost:9200")
            print("elasticsearch is already running")
        except:
            print("elasticsearch is not running")

        self.search_iterator = None

    def get_all_documents(self, dir_id: int):

        return helpers.scan(client=self.es,
                            query={"_source": {"includes": ["path", "name"]},
                                   "query": {"term": {"directory": dir_id}}},
                            index=self.index_name)

    def get_index_size(self):

        try:
            info = requests.get("http://localhost:9200/" + self.index_name + "/_stats")

            if info.status_code == 200:

                parsed_info = json.loads(info.text)

                return int(parsed_info["indices"][self.index_name]["primaries"]["store"]["size_in_bytes"])
        except:
            return 0

    def get_doc_count(self):

        try:
            info = requests.get("http://localhost:9200/" + self.index_name + "/_stats")

            if info.status_code == 200:
                parsed_info = json.loads(info.text)

                return int(parsed_info["indices"][self.index_name]["primaries"]["indexing"]["index_total"])
        except:
            return 0

    def search(self):
        page = self.es.search(body={"query": {"term": {"directory": 1}}, "size": 40},
                              index=self.index_name, scroll="3m")

        return page

    def scroll(self, scroll_id):

        page = self.es.scroll(scroll_id=scroll_id, scroll="3m")

        return page

    def get_doc(self, doc_id):

        return self.es.get(index=self.index_name, id=doc_id, doc_type="file")
