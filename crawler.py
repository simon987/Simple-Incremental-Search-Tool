import os
import hashlib


class Crawler:
    pass


class FileParser:
    pass


class CheckSumCalculator:

    def checksum(self, path: str) -> str:
        """
        Calculate the checksum of a file
        :param path: path of the file
        :return: checksum
        """
        raise NotImplementedError()


class Md5CheckSumCalculator(CheckSumCalculator):

    def __init__(self):
        self.name = "md5"

    def checksum(self, path: str) -> str:
        """
        Calculate the md5 checksum of a file
        :param path: path of the file
        :return: md5 checksum
        """
        result = hashlib.md5()

        with open(path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                result.update(block)

        return result.hexdigest().upper()


class Sha1CheckSumCalculator(CheckSumCalculator):

    def __init__(self):
        self.name = "sha1"

    def checksum(self, path: str) -> str:
        """
        Calculate the sha1 checksum of a file
        :param path: path of the file
        :return: sha1 checksum
        """
        result = hashlib.sha1()

        with open(path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                result.update(block)

        return result.hexdigest().upper()


class Sha256CheckSumCalculator(CheckSumCalculator):

    def __init__(self):
        self.name = "sha256"

    def checksum(self, path: str) -> str:
        """
        Calculate the sha256 checksum of a file
        :param path: path of the file
        :return: sha256 checksum
        """
        result = hashlib.sha256()

        with open(path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                result.update(block)

        return result.hexdigest().upper()


class GenericFileParser(FileParser):

    def __init__(self, checksum_calculators: list):
        self.checksum_calculators = checksum_calculators

    def parse(self, path: str) -> dict:
        """
        Parse a generic file
        :param path: path of the file to parse
        :return: dict information about the file
        """

        info = dict()

        info["size"] = os.path.getsize(path)
        info["name"] = os.path.splitext(path)[0]

        for calculator in self.checksum_calculators:
            info[calculator.name] = calculator.checksum(path)

        return info




# def crawl(root_dir: str) -> None:
#     docs = []
#
#     for root, dirs, files in os.walk(root_dir):
#
#         print(root)
#
#         for filename in files:
#             full_path = os.path.join(root, filename)
#
#             doc = dict()
#
#             doc["md5"] = md5sum(full_path)
#             doc["path"] = root
#             doc["name"] = filename
#             doc["size"] = os.path.getsize(full_path)
#             doc["mtime"] = int(os.path.getmtime(full_path))
#
#             mime_type = mimetypes.guess_type(full_path)[0]
#
#             if mime_type is not None:
#
#                 doc["mime"] = mime_type
#
#                 if mime_type.startswith("image"):
#                     try:
#                         width, height = Image.open(full_path).size
#
#                         doc["width"] = width
#                         doc["height"] = height
#                     except OSError:
#                         doc.pop('mime', None)
#                         pass
#                     except ValueError:
#                         doc.pop('mime', None)
#                         pass
#
#             docs.append(doc)
#
#     file = open("crawler.json", "w")
#     file.write(simplejson.dumps(docs))
#     file.close()
#
#