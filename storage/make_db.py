def createDbTables(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()

        if ('accounts',) not in tables_list:
            makeAccountsDb(conn, cursor)
        if ('categories',) not in tables_list:
            makeCategoriesDb(conn, cursor)
        if ('transactions',) not in tables_list:
            makeTransactionsDb(conn, cursor)
        if ('track_categories',) not in tables_list:
            makeTrackCategoriesDb(conn, cursor)
        if ('savings',) not in tables_list:
            makeSavingsDb(conn, cursor)
        if ('assets',) not in tables_list:
            makeAssetsDb(conn, cursor)
        if ('loans',) not in tables_list:
            makeLoansDb(conn, cursor)
        if ('track_savings',) not in tables_list:
            makeTrackSavingsDb(conn, cursor)


def makeTransactionsDb(conn, cursor):
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


def makeTrackCategoriesDb(conn, cursor):
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

def makeCategoriesDb(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT ,
                    account TEXT,
                    pre_set REAL,
                    archive TEXT,
                    FOREIGN KEY(account) REFERENCES accounts(name)
                        ON UPDATE CASCADE
                    )""")

        conn.commit()


def makeAccountsDb(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE accounts (
                    name TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    archive TEXT
        )""")

        conn.commit()

def makeSavingsDb(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE savings (
                    name TEXT PRIMARY KEY,
                    state TEXT,
                    interest REAL NOT NULL,
                    FOREIGN KEY(name)REFERENCES accounts(name)
                       ON UPDATE CASCADE
        )""")

        conn.commit()

def makeAssetsDb(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE assets (
                    name TEXT PRIMARY KEY,
                    state TEXT,
                    initial_date TEXT NOT NULL,
                    initial_amount REAL NOT NULL,
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

def makeLoansDb(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE loans (
                    name TEXT PRIMARY KEY,
                    state INTEGER,
                    interest REAL,
                    start_date REAL NOT NULL,
                    end_date TEXT,
                    initial_amount NOT NULL,
                    present_amt REAL NOT NULL, 
                    FOREIGN KEY(name)REFERENCES accounts(name)
                       ON UPDATE CASCADE
        )""")

        conn.commit()

def makeTrackSavingsDb(conn, cursor):
    with conn:
        cursor.execute(
            """
                CREATE TABLE track_savings (
                    id INTEGER PRIMARY KEY,
                    account TEXT,
                    date TEXT,
                    amount REAL,
                    FOREIGN KEY(account)REFERENCES accounts(name)
                       ON UPDATE CASCADE 
                )
            """
        )

def deleteSavingsDb(conn, cursor):
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

def deleteAssetsDb(conn, cursor):
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

def deleteLoansDb(conn, cursor):
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