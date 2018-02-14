PRAGMA FOREIGN_KEYS = ON;

-- Represents a directory and its sub-directories
CREATE TABLE Directory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT UNIQUE,
  enabled BOOLEAN
);

-- Represents a queued task for crawling a Directory or generating thumnails
CREATE TABLE Task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  directory_id INTEGER,
  task_type INTEGER,
  completed BOOLEAN DEFAULT 0,
  completed_time DATETIME,
  FOREIGN KEY (directory_id) REFERENCES Directory(id)
);

-- You can set an option on a directory to change the crawler's behavior
CREATE TABLE Option (
  name STRING,
  directory_id INTEGER,
  FOREIGN KEY (directory_id) REFERENCES Directory(id),
  PRIMARY KEY (name, directory_id)
);

-- User accounts
CREATE TABLE User (
  username TEXT PRIMARY KEY,
  password TEXT,
  is_admin BOOLEAN
);

CREATE TABLE User_canRead_Directory (
  username TEXT,
  directory_id INTEGER,
  PRIMARY KEY (username, directory_id),
  FOREIGN KEY (username) REFERENCES User(username),
  FOREIGN KEY (directory_id) REFERENCES Directory(id)

)
