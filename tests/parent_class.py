import os
import sqlite3
from storage.make_db import createDbTables


def connect_to_db():
    test_db = 'test_app.db'
    if os.path.isfile(test_db):
        os.remove(test_db)
    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    createDbTables(conn, c)
    return c, conn

class ParentClass:
        c,conn = connect_to_db()
