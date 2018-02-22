import sqlite3
import os
import flask_bcrypt


class CheckSumCalculator:

    def checksum(self, string: str):

        return flask_bcrypt.generate_password_hash(string, 14)  # todo load from config


class DuplicateDirectoryException(Exception):
    pass


class DuplicateUserException(Exception):
    pass


class User:
    """
    Data structure to hold user information
    """

    def __init__(self, username: str, hashed_password: bytes, admin: bool):
        self.username = username
        self.hashed_password = hashed_password
        self.admin = admin


class Option:
    """
    Data structure to hold a directory option
    """

    def __init__(self, key: str, value: str, dir_id: int=None, opt_id: int = None):
        self.key = key
        self.value = value
        self.id = opt_id
        self.dir_id = dir_id


class Directory:
    """
    Data structure to hold directory information
    """
    def __init__(self, path: str, enabled: bool, options: list, name: str):
        self.id = None
        self.path = path
        self.enabled = enabled
        self.options = options
        self.name = name

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
        :return: id
        """

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO Directory (path, enabled, name) VALUES (?, ?, ?)", (directory.path, directory.enabled, directory.name))
            c.execute("SELECT last_insert_rowid()")

            dir_id = c.fetchone()[0]
            c.close()
            conn.commit()
            conn.close()

            for opt in directory.options:
                opt.dir_id = dir_id
                self.save_option(opt)

            return dir_id
        except sqlite3.IntegrityError:
            c.close()
            conn.close()
            raise DuplicateDirectoryException("Duplicate directory path: " + directory.path)

    def remove_directory(self, dir_id: int):
        """Remove a directory from the database"""

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("DELETE FROM Option WHERE directory_id=?", (dir_id,))
        c.execute("DELETE FROM Task WHERE directory_id=?", (dir_id,))
        c.execute("DELETE FROM Directory WHERE id=?", (dir_id,))

        c.close()
        conn.commit()
        conn.close()

    def dirs(self) -> dict:

        if self.dir_cache_outdated:

            self.cached_dirs = {}

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, path, enabled, name FROM Directory")
            db_directories = c.fetchall()
            c.execute("SELECT key, value, directory_id, id FROM Option")
            db_options = c.fetchall()

            for db_dir in db_directories:

                options = []
                directory = Directory(db_dir[1], db_dir[2], options, db_dir[3])

                for db_opt in db_options:
                    if db_opt[2] == db_dir[0]:
                        options.append(Option(db_opt[0], db_opt[1], db_opt[2], db_opt[3]))

                directory.id = db_dir[0]

                self.cached_dirs[directory.id] = directory

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
            c.execute("INSERT INTO User (username, password, is_admin) VALUES (?,?,?)",
                      (user.username, user.hashed_password, user.admin))
            c.close()
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            raise DuplicateUserException("Duplicate username: " + user.username)

    def users(self) -> dict:
        """Get user list"""

        if self.user_cache_outdated:

            self.cached_users = {}

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT username, is_admin FROM User")

            db_users = c.fetchall()

            for db_user in db_users:
                self.cached_users[db_user[0]] = User(db_user[0], b"", bool(db_user[1]))

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

    def update_user(self, user: User) -> None:
        """Updates an user. Will have no effect if the user does not exist"""

        self.user_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE User SET is_admin=? WHERE username=?", (user.admin, user.username))

        c.close()
        conn.commit()
        conn.close()

    def remove_user(self, username: str):
        """Remove an user from the database"""

        self.user_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM User WHERE username=?", (username,))

        c.close()
        conn.commit()
        conn.close()

    def update_directory(self, directory):
        """Updated a directory (Options are left untouched). Will have no effect if the directory does not exist"""

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE Directory SET name=?, path=? WHERE id=?", (directory.name, directory.path, directory.id))

        c.close()
        conn.commit()
        conn.close()

    def save_option(self, option: Option):

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO Option (key, value, directory_id) VALUES (?, ?, ?)", (option.key, option.value, option.dir_id))
        c.execute("SELECT last_insert_rowid()")

        opt_id = c.fetchone()[0]
        c.close()
        conn.commit()
        conn.close()

        return opt_id

    def del_option(self, opt_id):
        """Delete an option from the database"""

        self.dir_cache_outdated = True

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM Option WHERE id=?", (opt_id, ))

        conn.commit()
        conn.close()



