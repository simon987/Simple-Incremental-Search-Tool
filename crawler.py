import os

class Crawler:

    def __init__(self, enabled_parsers: list):
        self.documents = []
        self.enabled_parsers = enabled_parsers

        for parser in self.enabled_parsers:
            if parser.is_default:
                self.default_parser = parser

        self.ext_map = {}

        for parser in self.enabled_parsers:
            for ext in parser.extensions:
                self.ext_map[ext] = parser

    def crawl(self, root_dir: str):
        for root, dirs, files in os.walk(root_dir):

            for filename in files:
                full_path = os.path.join(root, filename)

                parser = self.ext_map.get(os.path.splitext(filename)[1], self.default_parser)

                doc = parser.parse(full_path)

                self.documents.append(doc)

    def countFiles(self, root_dir: str):
        count = 0

        for root, dirs, files in os.walk(root_dir):
            count += len(files)

        return count

