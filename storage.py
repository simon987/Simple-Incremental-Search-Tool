import sqlite3
import os
import flask_bcrypt


class CheckSumCalculator:

    def checksum(self, string: str):

        return flask_bcrypt.generate_password_hash(string, 14)  # todo load from config


class DuplicateDirectoryException(Exception):
    pass


class DuplicateUsernameException(Exception):
    pass


class User:
    """
    Data structure to hold user information
    """

    def __init__(self, username: str, hashed_password: bytes, admin: bool):
        self.username = username
        self.hashed_password = hashed_password
        self.admin = admin


class Directory:
    """
    Data structure to hold directory information
    """
    def __init__(self, path: str, enabled: bool, options: list):
        self.path = path
        self.enabled = enabled
        self.options = options

    def __str__(self):
        return self.path + " | enabled: " + str(self.enabled) + " | opts: " + str(self.options)


class LocalStorage:
    """
    Manages storage of application data to disk.
    Could be refactored into a abstract class to switch from SQLite3 to something else
    """

    def __init__(self, db_path):
        self.cached_dirs = {}
        self.cached_users = {}
        self.db_path = db_path
        self.dir_cache_outdated = True  # Indicates that the database was changed since it was cached in memory
        self.user_cache_outdated = True
        pass

    def init_db(self, script_path):
        """Creates a blank database. Overwrites the old one"""
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        with open(script_path, "r") as f:
            c.executescript(f.read())

        conn.commit()
        c.close()
        conn.close()

    def save_directory(self, directory: Directory):
        """
        Save directory to storage
        :param directory: Directory to save
        :return: None
        """

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("PRAGMA FOREIGN_KEYS = ON;")
        try:
            c.execute("INSERT INTO Directory (path, enabled) VALUES (?, ?)", (directory.path, directory.enabled))
            c.execute("SELECT last_insert_rowid()")

            dir_id = c.fetchone()[0]

            for opt in directory.options:
                conn.execute("INSERT INTO Option (name, directory_id) VALUES (?, ?)", (opt, dir_id))

            conn.commit()
        except sqlite3.IntegrityError:
            raise DuplicateDirectoryException("Duplicate directory path: " + directory.path)

        finally:
            conn.close()

    def dirs(self):

        if self.dir_cache_outdated:

            self.cached_dirs = {}

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, path, enabled FROM Directory")
            db_directories = c.fetchall()
            c.execute("SELECT name, directory_id FROM Option")
            db_options = c.fetchall()

            for db_dir in db_directories:

                options = []
                directory = Directory(db_dir[1], db_dir[2], options)

                for db_opt in db_options:
                    if db_opt[1] == db_dir[0]:
                        options.append(db_opt[0])

                self.cached_dirs[directory.path] = directory
                self.dir_cache_outdated = False
                return self.cached_dirs

        else:
            return self.cached_dirs

    def save_user(self, user: User):
        """Save user to storage"""

        self.user_cache_outdated = True

        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("PRAGMA FOREIGN_KEYS = ON;")
            c.execute("INSERT INTO User (username, password, is_admin) VALUES (?,?,?)",
                      (user.username, user.hashed_password, user.admin))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            raise DuplicateDirectoryException("Duplicate username: " + user.username)

    def users(self):
        """Get user list"""

        if self.user_cache_outdated:

            self.cached_users = {}

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT username, is_admin FROM User")

            db_users = c.fetchall()

            for db_user in db_users:
                self.cached_users[db_user[0]] = User(db_user[0], "", db_user[1])

            conn.close()

            return self.cached_users

        else:
            return self.cached_users

    def auth_user(self, username: str, password: str) -> bool:
        """Authenticates an user"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT username, password FROM User WHERE username=?", (username,))

        db_user = c.fetchone()

        if db_user is not None:
            return flask_bcrypt.check_password_hash(db_user[1], password)

        return False


