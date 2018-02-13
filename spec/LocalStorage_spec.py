from unittest import TestCase

from storage import LocalStorage, Directory, DuplicateDirectoryException


class LocalStorageTest(TestCase):

    def setUp(self):

        s = LocalStorage()
        s.init_db("../database.sql")

    def test_save_and_retrieve_dir(self):

        storage = LocalStorage()

        d = Directory("/some/directory", True, ["opt1", "opt2", "opt3"])

        storage.save_directory(d)

        self.assertEqual(storage.dirs()["/some/directory"].enabled, True)
        self.assertEqual(storage.dirs()["/some/directory"].options[0], "opt1")

    def test_save_and_retrieve_dir_persistent(self):

        s1 = LocalStorage()

        d = Directory("/some/directory", True, ["opt1", "opt2", "opt3"])

        s1.save_directory(d)

        s2 = LocalStorage()
        self.assertEqual(s2.dirs()["/some/directory"].enabled, True)
        self.assertEqual(s2.dirs()["/some/directory"].options[0], "opt1")

    def test_reject_duplicate_path(self):

        s = LocalStorage()

        d1 = Directory("/some/directory", True, ["opt1", "opt2"])
        d2 = Directory("/some/directory", True, ["opt1", "opt2"])

        s.save_directory(d1)

        with self.assertRaises(DuplicateDirectoryException) as e:
            s.save_directory(d2)

