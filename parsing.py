import hashlib
import magic
import os
import mimetypes


class MimeGuesser:

    def guess_mime(self, full_path):
        raise NotImplementedError()


class ContentMimeGuesser(MimeGuesser):

    def __init__(self):
        self.libmagic = magic.Magic(mime=True)

    def guess_mime(self, full_path):
        return self.libmagic.from_file(full_path)


class ExtensionMimeGuesser(MimeGuesser):

    def guess_mime(self, full_path):
        return mimetypes.guess_type(full_path, strict=False)[0]


class FileParser:
    extensions = []
    is_default = False
    pass


class FileCheckSumCalculator:

    def checksum(self, path: str) -> str:
        """
        Calculate the checksum of a file
        :param path: path of the file
        :return: checksum
        """
        raise NotImplementedError()


class Md5CheckSumCalculator(FileCheckSumCalculator):

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


class Sha1CheckSumCalculator(FileCheckSumCalculator):

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


class Sha256CheckSumCalculator(FileCheckSumCalculator):

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

    extensions = []
    is_default = True

    def __init__(self, checksum_calculators: list, mime_guesser: MimeGuesser):

        self.checksum_calculators = checksum_calculators
        self.mime_guesser = mime_guesser

    def parse(self, full_path: str) -> dict:
        """
        Parse a generic file
        :param full_path: path of the file to parse
        :return: dict information about the file
        """

        info = dict()

        file_stat = os.stat(full_path)
        path, name = os.path.split(full_path)

        info["size"] = file_stat.st_size
        info["path"] = path
        info["name"] = name
        info["mtime"] = file_stat.st_mtime
        info["mime"] = self.mime_guesser.guess_mime(full_path)

        for calculator in self.checksum_calculators:
            info[calculator.name] = calculator.checksum(full_path)

        return info

