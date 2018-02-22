import os


class Crawler:

    def __init__(self, enabled_parsers: list):
        self.documents = []
        self.enabled_parsers = enabled_parsers

    def crawl(self, root_dir: str):
        for root, dirs, files in os.walk(root_dir):

            for filename in files:
                full_path = os.path.join(root, filename)

                parser = self.get_parser_by_ext(os.path.splitext(filename)[1])

                doc = parser.parse(full_path)

                self.documents.append(doc)

    def get_parser_by_ext(self, ext: str):

        for parser in self.enabled_parsers:

            if ext in parser.extensions:
                return parser

        for parser in self.enabled_parsers:
            if parser.is_default:
                return parser


