from unittest import TestCase
from parsing import MediaFileParser


class MediaFileParserTest(TestCase):

    def test_audio_wav(self):

        parser = MediaFileParser([])

        info = parser.parse("test_files/cat1.wav")

        self.assertEqual(info["bit_rate"], 256044)
        self.assertEqual(info["format_name"], "wav")
        self.assertEqual(info["format_long_name"], "WAV / WAVE (Waveform Audio)")
        self.assertEqual(info["duration"], 20.173875)

    def test_video_mov(self):
        parser = MediaFileParser([])

        info = parser.parse("test_files/vid1.mp4")

        self.assertEqual(info["bit_rate"], 513012)
        self.assertEqual(info["format_name"], "mov,mp4,m4a,3gp,3g2,mj2")
        self.assertEqual(info["format_long_name"], "QuickTime / MOV")
        self.assertEqual(info["duration"], 5.334)

    def test_video_webm(self):
        parser = MediaFileParser([])

        info = parser.parse("test_files/vid2.webm")

        self.assertEqual(info["bit_rate"], 343153)
        self.assertEqual(info["format_name"], "matroska,webm")
        self.assertEqual(info["format_long_name"], "Matroska / WebM")
        self.assertEqual(info["duration"], 10.619)

    def test_video_ogg(self):
        parser = MediaFileParser([])

        info = parser.parse("test_files/vid3.ogv")

        self.assertEqual(info["bit_rate"], 590261)
        self.assertEqual(info["format_name"], "ogg")
        self.assertEqual(info["format_long_name"], "Ogg")
        self.assertEqual(info["duration"], 10.618867)
