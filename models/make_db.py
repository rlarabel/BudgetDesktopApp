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

#TODO: Fix primary key to be and id or account and name
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
