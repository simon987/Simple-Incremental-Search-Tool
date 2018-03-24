import hashlib
import magic
import os
import mimetypes
import subprocess
import json
import chardet
from PIL import Image

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
    mime_types = []
    is_default = False

    def parse(self, full_path: str):
        raise NotImplemented


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

    mime_types = []
    is_default = True

    def __init__(self, checksum_calculators: list):

        self.checksum_calculators = checksum_calculators

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
        info["path"] = path  # todo save relative path
        info["name"] = name
        info["mtime"] = file_stat.st_mtime

        for calculator in self.checksum_calculators:
            info[calculator.name] = calculator.checksum(full_path)

        return info


class MediaFileParser(GenericFileParser):

    is_default = False
    relevant_properties = ["bit_rate", "nb_streams", "duration", "format_name", "format_long_name"]

    def __init__(self, checksum_calculators: list):
        super().__init__(checksum_calculators)

        self.mime_types = [
            "video/3gpp",
            "video/mp4",
            "video/mpeg",
            "video/ogg",
            "video/quicktime",
            "video/webm",
            "video/x-flv",
            "video/x-mng",
            "video/x-ms-asf",
            "video/x-ms-wmv",
            "video/x-msvideo",
            "audio/basic",
            "auido/L24",
            "audio/mid",
            "audio/mpeg",
            "audio/mp4",
            "audio/x-aiff",
            "audio/ogg",
            "audio/vorbis"
            "audio/x-realaudio",
            "audio/x-wav"
        ]

    def parse(self, full_path: str):
        info = super().parse(full_path)

        print("video/audio : " + full_path)

        result = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", full_path],
                                stdout=subprocess.PIPE)

        metadata = json.loads(result.stdout.decode("utf-8"))

        if "format" in metadata:

            if "bit_rate" in metadata["format"]:
                info["bit_rate"] = int(metadata["format"]["bit_rate"])

            if "nb_streams" in metadata["format"]:
                info["nb_streams"] = int(metadata["format"]["nb_streams"])

            if "duration" in metadata["format"]:
                info["duration"] = float(metadata["format"]["duration"])

            if "format_name" in metadata["format"]:
                info["format_name"] = metadata["format"]["format_name"]

            if "format_long_name" in metadata["format"]:
                info["format_long_name"] = metadata["format"]["format_long_name"]

        return info


class PictureFileParser(GenericFileParser):

    is_default = False

    def __init__(self, checksum_calculators: list):
        super().__init__(checksum_calculators)

        self.mime_types = [
            "image/bmp",
            "image/cgm",
            "image/cis-cod",
            "image/g3fax",
            "image/gif",
            "image/ief",
            "image/jpeg",
            "image/ktx",
            "image/pipeg",
            "image/pjpeg",
            "image/png",
            "image/prs.btif",
            "image/svg+xml",
            "image/tiff",
            "image/vnd.adobe.photoshop",
            "image/vnd.dece.graphic",
            "image/vnd.djvu",
            "image/vnd.dvb.subtitle",
            "image/vnd.dwg",
            "image/vnd.dxf",
            "image/vnd.fastbidsheet",
            "image/vnd.fpx",
            "image/vnd.fst",
            "image/vnd.fujixerox.edmics-mmr",
            "image/vnd.fujixerox.edmics-rlc",
            "image/vnd.ms-modi",
            "image/vnd.net-fpx",
            "image/vnd.wap.wbmp",
            "image/vnd.xiff",
            "image/webp",
            "image/x-citrix-jpeg",
            "image/x-citrix-png",
            "image/x-cmu-raster",
            "image/x-cmx",
            "image/x-freehand",
            "image/x-icon",
            "image/x-pcx",
            "image/x-pict",
            "image/x-png",
            "image/x-portable-anymap",
            "image/x-portable-bitmap",
            "image/x-portable-graymap",
            "image/x-portable-pixmap",
            "image/x-rgb",
            "image/x-xbitmap",
            "image/x-xpixmap",
            "image/x-xwindowdump"
        ]

    def parse(self, full_path: str):

        info = super().parse(full_path)

        print("picture")

        with open(full_path, "rb") as image_file:
            with Image.open(image_file) as image:

                info["mode"] = image.mode
                info["format"] = image.format
                info["width"] = image.width
                info["height"] = image.height

        return info


class TextFileParser(GenericFileParser):

    is_default = False

    def __init__(self, checksum_calculators: list, content_lenght: int):
        super().__init__(checksum_calculators)
        self.content_lenght = content_lenght

        self.mime_types = [
            "text/asp",
            "text/css",
            "text/ecmascript",
            "text/html",
            "text/javascript",
            "text/mcf",
            "text/pascal",
            "text/plain",
            "text/richtext",
            "text/scriplet",
            "text/sgml",
            "text/tab-separated-values",
            "text/uri-list",
            "text/vnd.abc",
            "text/vnd.fmi.flexstor",
            "text/vnd.rn-realtext",
            "text/vnd.wap.wml",
            "text/vnd.wap.wmlscript",
            "text/webviewhtml",
            "text/x-asm",
            "text/x-audiosoft-intra",
            "text/x-c",
            "text/x-component",
            "text/x-fortran",
            "text/x-h",
            "text/x-java-source",
            "text/x-la-asf",
            "text/x-m",
            "text/x-pascal",
            "text/x-script",
            "text/x-script.csh",
            "text/x-script.elisp",
            "text/x-script.guile",
            "text/x-script.ksh",
            "text/x-script.lisp",
            "text/x-script.perl",
            "text/x-script.perl-module",
            "text/x-script.phyton",
            "text/x-script.rexx",
            "text/x-script.scheme",
            "text/x-script.sh",
            "text/x-script.tcl",
            "text/x-script.tcsh",
            "text/x-script.zsh",
            "text/x-server-parsed-html",
            "text/x-setext",
            "text/x-sgml",
            "text/x-speech",
            "text/x-uil",
            "text/x-uuencode",
            "text/x-vcalendar",
            "text/xml"
        ]

    def parse(self, full_path: str):

        info = super().parse(full_path)

        with open(full_path, "rb") as text_file:

            raw_content = text_file.read(self.content_lenght)

            chardet.detect(raw_content)
            encoding = chardet.detect(raw_content)["encoding"]

            if encoding is not None:

                print(full_path)
                print(encoding)

                info["encoding"] = encoding
                info["content"] = raw_content.decode(encoding, "ignore")

        return info
