from unittest import TestCase
from thumbnail import ThumbnailGenerator
from PIL import Image
import os


class ThumbnailGeneratorTest(TestCase):

    def test_generate(self):

        generator = ThumbnailGenerator(300)
        # Original image is 420x315
        generator.generate("test_folder/sample_1.jpg", "test_thumb1.jpg")

        img = Image.open("test_thumb1.jpg")
        width, height = img.size
        img.close()

        self.assertEqual(300, width)
        self.assertEqual(225, height)

        if os.path.isfile("test_thumb1.jpg"):
            os.remove("test_thumb1.jpg")

