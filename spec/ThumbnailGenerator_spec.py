from unittest import TestCase
from thumbnail import ThumbnailGenerator
from PIL import Image
import os
import shutil


class ThumbnailGeneratorTest(TestCase):

    def test_generate(self):

        generator = ThumbnailGenerator(300)
        # Original image is 420x315
        generator.generate("test_folder/sample_1.jpg", "test_thumb1.jpg", "image/JPEG")

        img = Image.open("test_thumb1.jpg")
        width, height = img.size
        img.close()

        self.assertEqual(300, width)
        self.assertEqual(225, height)

        if os.path.isfile("test_thumb1.jpg"):
            os.remove("test_thumb1.jpg")

    def test_generate_all(self):
        shutil.rmtree("test_thumbnails")

        generator = ThumbnailGenerator(300)

        docs = [{'_source': {'path': 'test_folder', 'name': 'books.csv'}, '_id': 'books.csv-ID'},
                {'_source': {'path': 'test_folder', 'name': 'sample_3.jpg'}, '_id': 'sample_3.jpg-ID'},
                {'_source': {'path': 'test_folder', 'name': 'sample_5.png'}, '_id': 'sample_5.png-ID'},
                {'_source': {'path': 'test_folder', 'name': 'sample_6.gif'}, '_id': 'sample_6.gif-ID'},
                {'_source': {'path': 'test_folder', 'name': 'sample_7.bmp'}, '_id': 'sample_7.bmp-ID'},
                {'_source': {'path': 'test_folder', 'name': 'sample_2.jpeg'}, '_id': 'sample_2.jpeg-ID'}]

        generator.generate_all(docs, "test_thumbnails")

        self.assertFalse(os.path.isfile("test_thumbnails/books.csv-ID") and
                         os.path.getsize("test_thumbnails/books.csv-ID") > 0)
        self.assertTrue(os.path.isfile("test_thumbnails/sample_3.jpg-ID") and
                        os.path.getsize("test_thumbnails/sample_3.jpg-ID") > 0)
        self.assertTrue(os.path.isfile("test_thumbnails/sample_2.jpeg-ID") and
                        os.path.getsize("test_thumbnails/sample_2.jpeg-ID") > 0)
        self.assertTrue(os.path.isfile("test_thumbnails/sample_5.png-ID") and
                        os.path.getsize("test_thumbnails/sample_5.png-ID") > 0)
        self.assertTrue(os.path.isfile("test_thumbnails/sample_6.gif-ID") and
                        os.path.getsize("test_thumbnails/sample_6.gif-ID") > 0)
        self.assertTrue(os.path.isfile("test_thumbnails/sample_7.bmp-ID") and
                        os.path.getsize("test_thumbnails/sample_7.bmp-ID") > 0)






