from parsing import ContentMimeGuesser, ExtensionMimeGuesser
from unittest import TestCase
import os

dir_name = os.path.dirname(os.path.abspath(__file__))


class MimeGuesserTest(TestCase):

    def test_content_guesser(self):

        guesser = ContentMimeGuesser()

        self.assertEqual("text/x-shellscript", guesser.guess_mime(dir_name + "/test_folder/test_utf8.sh"))
        self.assertTrue(guesser.guess_mime(dir_name + "/test_folder/more_books.json") in ["application/json", "text/plain"])
        self.assertEqual("application/java-archive", guesser.guess_mime(dir_name + "/test_folder/post.jar"))
        self.assertEqual("image/jpeg", guesser.guess_mime(dir_name + "/test_folder/sample_1.jpg"))

    def test_extension_guesser(self):

        guesser = ExtensionMimeGuesser()

        self.assertTrue(guesser.guess_mime(dir_name + "/test_folder/test_utf8.sh") in ["text/x-sh", "application/x-sh"])
        self.assertEqual("application/json", guesser.guess_mime(dir_name + "/test_folder/more_books.json"))
        self.assertTrue(guesser.guess_mime(dir_name + "/test_folder/post.jar")
                        in ["application/java-archive", "application/x-java-archive"])
        self.assertEqual("image/jpeg", guesser.guess_mime(dir_name + "/test_folder/sample_1.jpg"))
