def create_db_tables(conn, cursor):
    with conn:
        cursor.execute("select name from sqlite_master where type = 'table'")
        tables_list = cursor.fetchall()

        if ('account',) not in tables_list:
            make_account_db(conn, cursor)
        if ('category',) not in tables_list:
            make_category_db(conn, cursor)
        if ('money_flow',) not in tables_list:
            make_money_flow_db(conn, cursor)
        if ('track_categories',) not in tables_list:
            make_track_categories_db(conn, cursor)
        if ('income',) not in tables_list:
            make_income_db(conn, cursor)


def make_money_flow_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE money_flow (
                        id INTEGER PRIMARY KEY, 
                        date TEXT,
                        payee TEXT,
                        notes TEXT,
                        total REAL,
                        flow TEXT NOT NULL,
                        account TEXT,
                        category TEXT,
                        FOREIGN KEY(category) REFERENCES category(name)
                            ON UPDATE CASCADE,
                        FOREIGN KEY (account) REFERENCES account(name)
                            ON UPDATE CASCADE
                        )""")

        conn.commit()


def make_track_categories_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE track_categories (
                    date TEXT,
                    total REAL,
                    account TEXT,
                    category TEXT,
                    FOREIGN KEY(category) REFERENCES category(name)
                        ON UPDATE CASCADE,
                    FOREIGN KEY (account) REFERENCES account(name)
                        ON UPDATE CASCADE
                    )""")

        conn.commit()


def make_category_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE category (
                    name TEXT PRIMARY KEY,
                    monthly_budget REAL,
                    trackaccount TEXT,
                    FOREIGN KEY(trackaccount) REFERENCES account(name)
                        ON UPDATE CASCADE
                    )""")

        conn.commit()


def make_income_db(conn, cursor):
    with conn:
        cursor.execute(""" CREATE TABLE income (
                        id INTEGER PRIMARY KEY,
                        budget REAL,
                        funds REAL
                        )""")

        conn.commit()


def make_account_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE account (
                    name TEXT PRIMARY KEY,
                    type TEXT,
                    total REAL,
                    goal REAL,
                    goal_date TEXT
        )""")

        conn.commit()
