from unittest import TestCase
from parsing import PictureFileParser


class PictureFileParserTest(TestCase):

    def test_parse_jpg(self):

        parser = PictureFileParser([], "test_files/")

        info = parser.parse("test_folder/sample_1.jpg")

        self.assertEqual(info["mode"], "RGB")
        self.assertEqual(info["width"], 420)
        self.assertEqual(info["height"], 315)
        self.assertEqual(info["format_name"], "JPEG")

    def test_parse_png(self):

        parser = PictureFileParser([], "test_files/")

        info = parser.parse("test_folder/sample_5.png")

        self.assertEqual(info["mode"], "RGBA")
        self.assertEqual(info["width"], 288)
        self.assertEqual(info["height"], 64)
        self.assertEqual(info["format_name"], "PNG")

    def test_parse_gif(self):

        parser = PictureFileParser([], "test_files/")

        info = parser.parse("test_folder/sample_6.gif")

        self.assertEqual(info["mode"], "P")
        self.assertEqual(info["width"], 420)
        self.assertEqual(info["height"], 315)
        self.assertEqual(info["format_name"], "GIF")

    def test_parse_bmp(self):

        parser = PictureFileParser([], "test_files/")

        info = parser.parse("test_folder/sample_7.bmp")

        self.assertEqual(info["mode"], "RGB")
        self.assertEqual(info["width"], 150)
        self.assertEqual(info["height"], 200)
        self.assertEqual(info["format_name"], "BMP")
