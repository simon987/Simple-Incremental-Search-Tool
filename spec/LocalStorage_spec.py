from unittest import TestCase
from storage import LocalStorage, Directory, DuplicateDirectoryException, User, DuplicateUserException, Option, Task
import os


class LocalStorageTest(TestCase):

    def setUp(self):
        if os.path.exists("test_database.db"):
            os.remove("test_database.db")

        s = LocalStorage("test_database.db")
        s.init_db("../database.sql")

    def test_save_and_retrieve_dir(self):

        storage = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")

        dir_id = storage.save_directory(d)

        self.assertEqual(storage.dirs()[dir_id].enabled, True)
        self.assertEqual(storage.dirs()[dir_id].options[0].key, "key1")
        self.assertEqual(storage.dirs()[dir_id].options[0].value, "val1")
        self.assertEqual(storage.dirs()[dir_id].options[0].dir_id, 1)


    def test_save_and_retrieve_dir_persistent(self):

        s1 = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")

        dir_id = s1.save_directory(d)

        s2 = LocalStorage("test_database.db")
        self.assertEqual(s2.dirs()[dir_id].enabled, True)

        self.assertEqual(s2.dirs()[dir_id].options[0].key, "key1")
        self.assertEqual(s2.dirs()[dir_id].options[0].value, "val1")
        self.assertEqual(s2.dirs()[dir_id].options[0].dir_id, 1)

    def test_reject_duplicate_path(self):

        s = LocalStorage("test_database.db")

        d1 = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")
        d2 = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")

        s.save_directory(d1)

        with self.assertRaises(DuplicateDirectoryException) as e:
            s.save_directory(d2)

    def test_remove_dir(self):
        s = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val3")], "An excellent name")
        dir_id = s.save_directory(d)

        s.remove_directory(dir_id)

        with self.assertRaises(KeyError):
            _ = s.dirs()[dir_id]

    def test_save_and_retrieve_user(self):

        s = LocalStorage("test_database.db")

        u = User("bob", b"anHashedPassword", True)

        s.save_user(u)

        self.assertEqual(s.users()["bob"].username, "bob")
        self.assertEqual(s.users()["bob"].admin, True)

    def test_return_none_with_unknown_user(self):

        s = LocalStorage("test_database.db")

        with self.assertRaises(KeyError) as e:
            _ = s.users()["unknown_user"]

    def test_auth_user(self):

        s = LocalStorage("test_database.db")

        u = User("bob", b'$2b$10$RakMb.3n/tl76sK7iVahJuklNYkR7f2Y4dsf73tPANwYBkp4VuJ7.', True)

        s.save_user(u)

        self.assertTrue(s.auth_user("bob", "test"))
        self.assertFalse(s.auth_user("bob", "wrong"))

        pass

    def test_reject_duplicate_user(self):

        s = LocalStorage("test_database.db")

        u1 = User("user1", b"anHashedPassword", True)
        u2 = User("user1", b"anotherHashedPassword", True)

        s.save_user(u1)

        with self.assertRaises(DuplicateUserException) as e:
            s.save_user(u2)

    def test_update_user(self):
        s = LocalStorage("test_database.db")

        u = User("neil", b"anHashedPassword", True)

        s.save_user(u)

        u.admin = False
        s.update_user(u)

        self.assertFalse(s.users()["neil"].admin)

    def test_remove_user(self):

        s = LocalStorage("test_database.db")

        u = User("martin", b"anHashedPassword", True)
        s.save_user(u)

        s.remove_user(u.username)

        with self.assertRaises(KeyError):
            _ = s.users()["martin"]

    def test_update_directory(self):

        s = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")

        dir_id = s.save_directory(d)

        d.name = "A modified name"
        d.path = "/another/directory"
        d.id = dir_id

        s.update_directory(d)

        s2 = LocalStorage("test_database.db")

        self.assertEqual(s2.dirs()[dir_id].name, "A modified name")
        self.assertEqual(len(s2.dirs()[dir_id].options), 2)
        self.assertEqual(s2.dirs()[dir_id].path, "/another/directory")

    def test_save_option(self):

        s = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")
        dir_id = s.save_directory(d)

        opt_id = s.save_option(Option("key3", "val3", dir_id))

        self.assertEqual(s.dirs()[dir_id].options[2].key, "key3")
        self.assertEqual(s.dirs()[dir_id].options[2].value, "val3")
        self.assertEqual(s.dirs()[dir_id].options[2].dir_id, dir_id)
        self.assertEqual(opt_id, 3)

    def test_del_option(self):

        s = LocalStorage("test_database.db")

        d = Directory("/some/directory", True, [Option("key1", "val1"), Option("key2", "val2")], "An excellent name")
        dir_id = s.save_directory(d)
        s.del_option(1)

        self.assertEqual(len(s.dirs()[dir_id].options), 1)
        self.assertEqual(s.dirs()[dir_id].options[0].key, "key2")
        self.assertEqual(s.dirs()[dir_id].options[0].value, "val2")
        self.assertEqual(s.dirs()[dir_id].options[0].dir_id, 1)

    def test_save_task(self):

        s = LocalStorage("test_database.db")

        dir_id = s.save_directory(Directory("/some/dir", True, [], "my dir"))
        task_id = s.save_task(Task(0, dir_id))

        self.assertEqual(s.tasks()[task_id].dir_id, dir_id)
        self.assertEqual(task_id, 1)

    def test_del_task(self):
        s = LocalStorage("test_database.db")

        dir_id = s.save_directory(Directory("/some/dir", True, [], "my dir"))
        task_id = s.save_task(Task(0, dir_id))

        s.del_task(task_id)

        with self.assertRaises(KeyError):
            _ = s.tasks()[task_id]


