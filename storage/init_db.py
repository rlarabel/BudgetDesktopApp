import sqlite3
import os

def initializeDb(op_sys):
    if op_sys == 'windows':
        user_path = os.environ['USERPROFILE']
    elif op_sys == 'linux':    
        user_path = os.path.expanduser( '~' )

    app_data_path = user_path + '/AppData/Local/RatTrap'
    location_exist = os.path.exists(app_data_path)
    app_path = app_data_path + '/app.db'
    if not location_exist:
        os.makedirs(app_data_path)
    conn = sqlite3.connect(app_path)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    return conn, c