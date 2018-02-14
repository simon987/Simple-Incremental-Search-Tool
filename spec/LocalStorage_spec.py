from unittest import TestCase
from storage import LocalStorage, Directory, DuplicateDirectoryException, User


class LocalStorageTest(TestCase):

    def setUp(self):

        s = LocalStorage("test_database.db")
        s.init_db("../database.sql")

    def test_save_and_retrieve_dir(self):

        storage = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, ["opt1", "opt2", "opt3"])

        storage.save_directory(d)

        self.assertEqual(storage.dirs()["/some/directory"].enabled, True)
        self.assertEqual(storage.dirs()["/some/directory"].options[0], "opt1")

    def test_save_and_retrieve_dir_persistent(self):

        s1 = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, ["opt1", "opt2", "opt3"])

        s1.save_directory(d)

        s2 = LocalStorage("test_database.db")
        self.assertEqual(s2.dirs()["/some/directory"].enabled, True)
        self.assertEqual(s2.dirs()["/some/directory"].options[0], "opt1")

    def test_reject_duplicate_path(self):

        s = LocalStorage("test_database.db")

        d1 = Directory("/some/directory", True, ["opt1", "opt2"])
        d2 = Directory("/some/directory", True, ["opt1", "opt2"])

        s.save_directory(d1)

        with self.assertRaises(DuplicateDirectoryException) as e:
            s.save_directory(d2)

    def test_save_and_retrieve_user(self):

        s = LocalStorage("test_database.db")

        u = User("bob", "anHashedPassword", True)

        s.save_user(u)

        self.assertEqual(s.users()["bob"].username, "bob")
        self.assertEqual(s.users()["bob"].admin, True)

    def test_return_none_with_unknown_user(self):

        s = LocalStorage("test_database.db")

        with self.assertRaises(KeyError) as e:
            _ = s.users()["unknown_user"]

    def test_auth_user(self):

        s = LocalStorage("test_database.db")

        u = User("bob", b'$2b$14$VZEMbwAdy/HvLL/zh0.Iv.8XYnoZMz/LU9V4VKXLiuS.pthcUly2O', True)

        s.save_user(u)

        self.assertTrue(s.auth_user("bob", "test"))
        self.assertFalse(s.auth_user("bob", "wrong"))
        self.assertFalse(s.auth_user("wrong", "test"))

        pass
