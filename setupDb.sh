#!/bin/bash

rm test.db
sqlite3 local_storage.db -init "database.sql"