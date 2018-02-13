import sqlite3
import os


class DuplicateDirectoryException(Exception):
    pass


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

    cache_outdated = True
    """Static variable that indicates that the database was changed since the last time it was cached in memory"""

    db_path = "../local_storage.db"

    def __init__(self):
        self.cached_dirs = {}
        pass

    @staticmethod
    def init_db(script_path):
        """Creates a blank database. Overwrites the old one"""
        if os.path.isfile(LocalStorage.db_path):
            os.remove(LocalStorage.db_path)

        conn = sqlite3.connect(LocalStorage.db_path)
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

        LocalStorage.cache_outdated = True

        conn = sqlite3.connect(LocalStorage.db_path)
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

        if LocalStorage.cache_outdated:

            self.cached_dirs = {}

            conn = sqlite3.connect(LocalStorage.db_path)
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
                LocalStorage.cache_outdated = False
                return self.cached_dirs

        else:
            return self.cached_dirs
