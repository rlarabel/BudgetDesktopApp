def create_db_tables(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()

        if ('accounts',) not in tables_list:
            make_account_db(conn, cursor)
        if ('categories',) not in tables_list:
            make_category_db(conn, cursor)
        if ('transactions',) not in tables_list:
            make_money_flow_db(conn, cursor)
        if ('track_categories',) not in tables_list:
            make_track_categories_db(conn, cursor)
        if ('savings',) not in tables_list:
            make_savings_db(conn, cursor)
        if ('assets',) not in tables_list:
            make_assets_db(conn, cursor)
        if ('loans',) not in tables_list:
            make_loans_db(conn, cursor)


def make_money_flow_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE transactions (
                        id INTEGER PRIMARY KEY, 
                        date TEXT NOT NULL,
                        payee TEXT,
                        notes TEXT,
                        total REAL NOT NULL,
                        account TEXT NOT NULL,
                        category_id INTEGER NOT NULL,
                        FOREIGN KEY (account) REFERENCES accounts(name)
                            ON UPDATE CASCADE,
                        FOREIGN KEY(category_id) REFERENCES categories(id)
                            ON UPDATE CASCADE
                        )""")

        conn.commit()


def make_track_categories_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE track_categories (
                    id INTEGER PRIMARY KEY, 
                    date TEXT NOT NULL,
                    total REAL NOT NULL,
                    account TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    FOREIGN KEY(category_id) REFERENCES categories(id)
                        ON UPDATE CASCADE,
                    FOREIGN KEY (account) REFERENCES accounts(name)
                        ON UPDATE CASCADE
                    )""")

        conn.commit()

def make_category_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT ,
                    account TEXT,
                    FOREIGN KEY(account) REFERENCES accounts(name)
                        ON UPDATE CASCADE
                    )""")

        conn.commit()


def make_account_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE accounts (
                    name TEXT PRIMARY KEY,
                    type TEXT NOT NULL
        )""")

        conn.commit()

def make_savings_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE savings (
                    name TEXT PRIMARY KEY,
                    state TEXT,
                    interest REAL NOT NULL,
                    real_value REAL,
                    FOREIGN KEY(name)REFERENCES accounts(name)
                       ON UPDATE CASCADE
        )""")

        conn.commit()

def make_assets_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE assets (
                    name TEXT PRIMARY KEY,
                    state TEXT,
                    interest_1 REAL, 
                    payment_1 REAL,
                    present_value_1 REAL,
                    future_value_1 REAL,
                    date_1 TEXT,
                    interest_2 REAL, 
                    payment_2 REAL,
                    present_value_2 REAL,
                    future_value_2 REAL,
                    date_2 TEXT,
                    FOREIGN KEY(name)REFERENCES accounts(name)
                       ON UPDATE CASCADE
        )""")

        conn.commit()

def make_loans_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE loans (
                    state INTEGER,
                    name TEXT PRIMARY KEY,
                    interest REAL,
                    end_date TEXT, 
                    FOREIGN KEY(name)REFERENCES accounts(name)
                       ON UPDATE CASCADE
        )""")

        conn.commit()

def delete_savings_db(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()
        if ('savings',) in tables_list:
            cursor.execute("DROP TABLE savings")
        cursor.execute("SELECT name FROM accounts WHERE type=:type", {"type": "savings"})
        accounts = cursor.fetchall()

        if accounts:
                
            for name in accounts:
                print(name[0])
                cursor.execute("DELETE FROM transactions WHERE account=:account", {'account': name[0]})
                cursor.execute("DELETE FROM categories WHERE account=:account", {'account': name[0]})
            cursor.execute("DELETE FROM accounts WHERE type=:type", {"type": "savings"})
        conn.commit()

def delete_assets_db(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()
        if ('assets',) in tables_list:
            cursor.execute("DROP TABLE assets")
        cursor.execute("SELECT name FROM accounts WHERE type=:type", {"type": "asset"})
        accounts = cursor.fetchall()

        if accounts:
                
            for name in accounts:
                print(name[0])
                cursor.execute("DELETE FROM transactions WHERE account=:account", {'account': name[0]})
                cursor.execute("DELETE FROM categories WHERE account=:account", {'account': name[0]})
            cursor.execute("DELETE FROM accounts WHERE type=:type", {"type": "asset"})
        conn.commit()

def delete_loans_db(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()
        if ('loans',) in tables_list:
            cursor.execute("DROP TABLE loans")
        cursor.execute("SELECT name FROM accounts WHERE type=:type", {"type": "loan"})
        accounts = cursor.fetchall()

        if accounts:
                
            for name in accounts:
                print(name[0])
                cursor.execute("DELETE FROM transactions WHERE account=:account", {'account': name[0]})
                cursor.execute("DELETE FROM categories WHERE account=:account", {'account': name[0]})
            cursor.execute("DELETE FROM accounts WHERE type=:type", {"type": "loan"})
        conn.commit()