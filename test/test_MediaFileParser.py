from unittest import TestCase
from parsing import MediaFileParser
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class MediaFileParserTest(TestCase):

    def test_audio_wav(self):

        parser = MediaFileParser([], dir_name + "/test_files/")

        info = parser.parse(dir_name + "/test_files/cat1.wav")

        self.assertEqual(info["format_long_name"], "WAV / WAVE (Waveform Audio)")
        self.assertEqual(info["duration"], 20.173875)

    def test_video_mov(self):
        parser = MediaFileParser([], dir_name + "/test_files")

        info = parser.parse(dir_name + "/test_files/vid1.mp4")

        self.assertEqual(info["format_long_name"], "QuickTime / MOV")
        self.assertEqual(info["duration"], 5.334)

    def test_video_webm(self):
        parser = MediaFileParser([], "test_files/")

        info = parser.parse(dir_name + "/test_files/vid2.webm")

        self.assertEqual(info["format_long_name"], "Matroska / WebM")
        self.assertEqual(info["duration"], 10.619)

    def test_video_ogg(self):
        parser = MediaFileParser([], "test_files/")

        info = parser.parse(dir_name + "/test_files/vid3.ogv")

        self.assertEqual(info["format_long_name"], "Ogg")
        self.assertEqual(info["duration"], 10.618867)
