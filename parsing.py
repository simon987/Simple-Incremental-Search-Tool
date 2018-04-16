import hashlib
import magic
import os
import mimetypes
import subprocess
import json
import chardet
import html
import warnings
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
import html2text
from ebooklib import epub
import ebooklib
from PIL import Image
from fontTools.ttLib import TTFont, TTLibError


class MimeGuesser:
    def guess_mime(self, full_path):
        raise NotImplementedError()


class ContentMimeGuesser(MimeGuesser):
    def __init__(self):
        self.libmagic = magic.Magic(mime=True)

    def guess_mime(self, full_path):
        try:
            return self.libmagic.from_file(full_path)
        except FileNotFoundError:
            return None


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
        name, extension = os.path.splitext(name)

        info["size"] = file_stat.st_size
        info["path"] = path  # todo save relative path
        info["name"] = name
        info["extension"] = extension[1:]
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
            "video/3gpp", "video/mp4", "video/mpeg", "video/ogg", "video/quicktime",
            "video/webm", "video/x-flv", "video/x-mng", "video/x-ms-asf",
            "video/x-ms-wmv", "video/x-msvideo", "audio/basic", "auido/L24",
            "audio/mid", "audio/mpeg", "audio/mp4", "audio/x-aiff",
            "audio/ogg", "audio/vorbis" "audio/x-realaudio", "audio/x-wav",
            "audio/flac", "audio/x-monkeys-audio", "audio/wav", "audio/wave",
            "audio/x-wav", "audio/x-ms-wma"
        ]

    def parse(self, full_path: str):
        info = super().parse(full_path)

        p = subprocess.Popen(["ffprobe", "-v", "quiet", "-print_format", "json=c=1", "-show_format", full_path],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()

        try:
            metadata = json.loads(out.decode("utf-8"))

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

                if "tags" in metadata["format"]:
                    if "genre" in metadata["format"]["tags"]:
                        info["genre"] = metadata["format"]["tags"]["genre"]
                    if "title" in metadata["format"]["tags"]:
                        info["title"] = metadata["format"]["tags"]["title"]
                    if "album" in metadata["format"]["tags"]:
                        info["album"] = metadata["format"]["tags"]["album"]
                    if "album_artist" in metadata["format"]["tags"]:
                        info["album_artist"] = metadata["format"]["tags"]["album_artist"]

        except json.decoder.JSONDecodeError:
            print("json decode error:" + full_path)
            pass

        return info


class PictureFileParser(GenericFileParser):
    is_default = False

    def __init__(self, checksum_calculators: list):
        super().__init__(checksum_calculators)

        self.mime_types = [
            "image/bmp", "image/cgm", "image/cis-cod", "image/g3fax", "image/gif",
            "image/ief", "image/jpeg", "image/ktx", "image/pipeg", "image/pjpeg",
            "image/png", "image/prs.btif", "image/svg+xml", "image/tiff",
            "image/vnd.adobe.photoshop", "image/vnd.dece.graphic", "image/vnd.djvu",
            "image/vnd.dvb.subtitle", "image/vnd.dwg", "image/vnd.dxf",
            "image/vnd.fastbidsheet", "image/vnd.fpx", "image/vnd.fst",
            "image/vnd.fujixerox.edmics-mmr", "image/vnd.fujixerox.edmics-rlc",
            "image/vnd.ms-modi", "image/vnd.net-fpx", "image/vnd.wap.wbmp",
            "image/vnd.xiff", "image/webp", "image/x-citrix-jpeg", "image/x-citrix-png",
            "image/x-cmu-raster", "image/x-cmx", "image/x-icon",
            "image/x-pcx", "image/x-pict", "image/x-png", "image/x-portable-bitmap",
            "image/x-portable-graymap", "image/x-portable-pixmap",
            "image/x-rgb", "image/x-xbitmap", "image/x-xpixmap", "image/x-xwindowdump"
        ]

    def parse(self, full_path: str):

        info = super().parse(full_path)

        try:
            with open(full_path, "rb") as image_file:
                with Image.open(image_file) as image:
                    info["mode"] = image.mode
                    info["format"] = image.format
                    info["width"] = image.width
                    info["height"] = image.height
        except (OSError, ValueError) as e:
            pass

        return info


class TextFileParser(GenericFileParser):
    is_default = False

    def __init__(self, checksum_calculators: list, content_length: int):
        super().__init__(checksum_calculators)
        self.content_length = content_length

        self.mime_types = [
            "text/asp", "text/css", "text/ecmascript", "text/html", "text/javascript",
            "text/mcf", "text/pascal", "text/plain", "text/richtext", "text/scriplet",
            "text/sgml", "text/tab-separated-values", "text/uri-list", "text/vnd.abc",
            "text/vnd.fmi.flexstor", "text/vnd.rn-realtext", "text/vnd.wap.wml",
            "text/vnd.wap.wmlscript", "text/webviewhtml", "text/x-asm", "text/x-audiosoft-intra",
            "text/x-c", "text/x-component", "text/x-fortran", "text/x-h", "text/x-java-source",
            "text/x-la-asf", "text/x-m", "text/x-pascal", "text/x-script",
            "text/x-script.csh", "text/x-script.elisp", "text/x-script.guile",
            "text/x-script.ksh", "text/x-script.lisp", "text/x-script.perl",
            "text/x-script.perl-module", "text/x-script.phyton", "text/x-script.rexx",
            "text/x-script.scheme", "text/x-script.sh", "text/x-script.tcl",
            "text/x-script.tcsh", "text/x-script.zsh", "text/x-server-parsed-html",
            "text/x-setext", "text/x-sgml", "text/x-speech", "text/x-uil",
            "text/x-uuencode", "text/x-vcalendar", "text/xml", "text/x-csrc", "text/csv",
            "text/x-c++src", "text/x-chdr", "text/markdown", "text/x-sh", "text/x-java",
            "text/x-python", "text/x-c++hdr", "text/x-tex", "text/x-diff", "text/x-haskell",
            "text/x-perl", "text/x-dsrc", "text/scriptlet", "text/x-scala", "text/calendar",
            "text/x-bibtex", "text/x-tcl", "text/x-c++", "text/x-shellscript", "text/x-msdos-batch",
            "text/x-makefile", "text/rtf", "text/x-objective-c", "text/troff", "text/x-m4",
            "text/x-lisp", "text/x-php", "text/x-gawk", "text/x-awk", "text/x-ruby", "text/x-po"
        ]

        self.encodings = [
            'ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437',
            'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855',
            'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863',
            'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932',
            'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 'cp1140',
            'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255',
            'cp1256', 'cp1257', 'cp1258', 'cp65001', 'euc_jp', 'euc_jis_2004',
            'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
            'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3',
            'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3',
            'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
            'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14',
            'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u',
            'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
            'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004',
            'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be',
            'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig'
        ]

    def parse(self, full_path: str):
        info = super().parse(full_path)

        with open(full_path, "rb") as text_file:
            raw_content = text_file.read(self.content_length)

            chardet.detect(raw_content)
            encoding = chardet.detect(raw_content)["encoding"]

            if encoding is not None and encoding in self.encodings:
                info["encoding"] = encoding
                content = raw_content.decode(encoding, "ignore")

                info["content"] = html.escape(content)

        return info


class FontParser(GenericFileParser):
    is_default = False

    def __init__(self, checksum_calculators: list):
        super().__init__(checksum_calculators)

        self.mime_types = [
            "application/font-sfnt", "application/font-woff", "application/vdn.ms-fontobject",
            "application/x-font-ttf"
        ]

    def parse(self, full_path: str):

        info = super().parse(full_path)

        with open(full_path, "rb") as f:

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                try:

                    font = TTFont(f)

                    if "name" in font:
                        try:
                            for name in font["name"].names:
                                if name.nameID == 4:
                                    info["content"] = name.toUnicode("replace")
                                    break
                        except AssertionError:
                            print("Could not read font name for " + full_path)
                except TTLibError:
                    print("Could not read font for " + full_path)

        return info


class PdfFileParser(GenericFileParser):
    is_default = False

    def __init__(self, checksum_calculators: list, content_length: int):
        super().__init__(checksum_calculators)

        self.content_length = content_length

        self.mime_types = [
            "application/pdf", "application/x-pdf"
        ]

    def parse(self, full_path: str):
        info = super().parse(full_path)

        with open(full_path, "rb") as f:

            info["content"] = ""

            parser = PDFParser(f)
            document = PDFDocument(parser)

            if len(document.info) > 0 and "Title" in document.info[0] and document.info[0]["Title"] != b"":
                info["content"] += document.info[0]["Title"].decode("utf-8", "replace") + "\n"

            try:
                if document.is_extractable:
                    resource_manager = PDFResourceManager()
                    la_params = LAParams()

                    device = PDFPageAggregator(resource_manager, laparams=la_params)
                    interpreter = PDFPageInterpreter(resource_manager, device)

                    for page in PDFPage.create_pages(document):

                        interpreter.process_page(page)
                        layout = device.get_result()

                        for lt_obj in layout:
                            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):

                                text = lt_obj.get_text()

                                if len(info["content"]) + len(text) <= self.content_length:
                                    info["content"] += text
                                else:
                                    info["content"] += text[0:self.content_length - len(info["content"])]
                                    break
                        else:
                            continue
                        break
                else:
                    print("PDF is not extractable: " + full_path)
            except ValueError:
                print("Couldn't parse page for " + full_path)

        return info


class EbookParser(GenericFileParser):
    is_default = False

    def __init__(self, checksum_calculators: list, content_length: int):
        super().__init__(checksum_calculators)

        self.content_length = content_length

        self.mime_types = [
            "application/epub+zip"
        ]

        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_images = True
        self.html2text.ignore_emphasis = True

    def parse(self, full_path: str):
        info = super().parse(full_path)

        book = epub.read_epub(full_path)

        info["content"] = ""

        for text in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):

            text = self.html2text.handle(text.content.decode("utf-8"))

            if len(info["content"]) + len(text) <= self.content_length:
                info["content"] += text
            else:
                info["content"] += text[0:self.content_length - len(info["content"])]
                break

        return info


