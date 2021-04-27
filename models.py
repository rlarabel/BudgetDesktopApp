from datetime import datetime
from itertools import zip_longest


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
                        FOREIGN KEY(category) REFERENCES category(name),
                        FOREIGN KEY (account) REFERENCES account(name)
                        )""")

        conn.commit()


def make_track_categories_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE track_categories (
                    date TEXT,
                    total REAL,
                    account TEXT,
                    category TEXT,
                    FOREIGN KEY(category) REFERENCES category(name),
                    FOREIGN KEY (account) REFERENCES account(name)
                    )""")

        conn.commit()


def make_category_db(conn, cursor):
    with conn:
        cursor.execute("""CREATE TABLE category (
                    name TEXT PRIMARY KEY,
                    monthly_budget REAL,
                    monthly_avg REAL,
                    trackaccount TEXT,
                    FOREIGN KEY(trackaccount) REFERENCES account(name)
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
                    total REAL
        )""")

        conn.commit()


def create_funds_income(conn, cursor):
    with conn:
        cursor.execute("SELECT * FROM income")
        funds_exist = cursor.fetchone()
        if not funds_exist:
            cursor.execute("INSERT INTO income VALUES (:id, :budget, :funds)",
                           {'id': '1', 'budget': 0, 'funds': 0})
            conn.commit()

        return update_funds(conn, cursor)


def make_category_menu(conn, cursor):
    with conn:
        cursor.execute("SELECT * FROM category")
        menu = []
        for temp in cursor.fetchall():
            menu.append(temp[0])

        if not menu:
            menu = ['No Categories Yet']

        return tuple(menu)


def make_budget_sheet(conn, cursor, budget_date):
    with conn:
        cursor.execute("SELECT * FROM account")
        table = []
        for account in cursor.fetchall():
            # Finds the account name
            cursor.execute("SELECT * FROM category WHERE trackaccount=:name", {'name': account[0]})
            all_categories = cursor.fetchall()

            # adds account total to table
            cursor.execute("SELECT * FROM track_categories WHERE account=:name", {'name': account[0]})
            account_incomes = cursor.fetchall()
            cursor.execute("SELECT * FROM money_flow WHERE account=:name", {'name': account[0]})
            account_outcomes = cursor.fetchall()
            account_total = get_monthly_total(account_incomes, account_outcomes, budget_date)

            table.append([account[0], str(account_total)])

            for category in all_categories:
                cursor.execute("SELECT * FROM track_categories WHERE category=:name", {'name': category[0]})
                category_incomes = cursor.fetchall()
                cursor.execute("SELECT * FROM money_flow WHERE category=:name", {'name': category[0]})
                category_outcomes = cursor.fetchall()
                category_total = get_monthly_total(category_incomes, category_outcomes, budget_date)

                table.append([category[0], str(category_total)])
        if not table:
            table = [['', '']]

        return table


def get_monthly_total(incomes, outcomes, user_date):
    total = 0
    year, month = user_date.split('-')
    for income, outcome in zip_longest(incomes, outcomes, fillvalue=0):
        if income:
            income_date = income[0]
            income_year, income_month = income_date.split('-')
            if datetime(int(year), int(month)+1, 1) > datetime(int(income_year), int(income_month), 1):
                total += income[1]
        if outcome:
            outcome_date = outcome[1]
            outcome_year, outcome_month, _ = outcome_date.split('-')
            if datetime(int(year), int(month)+1, 1) > datetime(int(outcome_year), int(outcome_month), 1):
                total -= outcome[4]

    return total


def add_new_category(conn, cursor, data):
    with conn:
        cursor.execute("SELECT * FROM account WHERE name=:name", {'name': data['-Account name-']})
        parent_account = cursor.fetchone()

        new_row = {
            'name': data['-Category-'],
            'monthly_budget': 0,
            'monthly_avg': 0,
            'trackaccount': parent_account[0]
        }
        cursor.execute("INSERT INTO category VALUES (:name, :monthly_budget, :monthly_avg, :trackaccount)", new_row)
        conn.commit()


def set_row_colors(conn, cursor):
    with conn:
        account_color = []
        i = 0
        cursor.execute("SELECT * FROM account")
        for account in cursor.fetchall():
            account_color.append((i, 'yellow', 'black'))
            i += 1
            cursor.execute("SELECT * FROM category WHERE trackaccount=:name", {'name': account[0]})
            for _ in cursor.fetchall():
                i += 1

        return account_color


def make_transaction_sheet(conn, cursor):
    with conn:
        table = []
        cursor.execute("SELECT * FROM money_flow")
        all_transactions = cursor.fetchall()
        for transaction in all_transactions:
            transaction = [transaction[1], transaction[6], transaction[7], transaction[2], transaction[3],
                           transaction[5], transaction[4]]
            table.append(transaction)
        if not table:
            table = [['', '', '', '', '', '', '']]
    return table


def add_transaction(conn, cursor, data):
    with conn:
        user_date = str(data['-Year-']) + '-' + str(data['-Month-']) + '-' + str(data['-Day-'])
        user_total = round(float(data['-Trans total-']), 2)
        if data['-Outcome-']:
            cursor.execute("SELECT * FROM category WHERE name=:name", {'name': data['-Trans menu-']})
            category = cursor.fetchone()
            if category:
                cursor.execute("""INSERT INTO money_flow  VALUES 
                                (:id, :date, :payee, :notes, :total, :flow, :account, :category)""",
                               {'id': None, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'flow': 'out', 'account': category[3], 'category': category[0]})
        else:
            cursor.execute("""INSERT INTO money_flow  VALUES 
                                            (:id, :date, :payee, :notes, :total, :flow, :account, :category)""",
                           {'id': None, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'flow': 'in', 'account': None, 'category': None})

        conn.commit()


def update_funds(conn, cursor):
    with conn:
        cursor.execute("SELECT * FROM money_flow")
        gross_funds = 0
        available_budget = 0
        for a_transaction in cursor.fetchall():
            if a_transaction[5] == 'in':
                gross_funds += a_transaction[4]
                available_budget += a_transaction[4]
            elif a_transaction[5] == 'out':
                gross_funds -= a_transaction[4]

        cursor.execute("SELECT * FROM track_categories")
        for budgeted_money in cursor.fetchall():
            available_budget -= budgeted_money[1]
        update_row = {
            'id': 1,
            'funds': gross_funds,
            'budget':  available_budget
        }
        cursor.execute("""UPDATE income SET funds =:funds AND budget=:budget
                                            WHERE id=:id""", update_row)

        return available_budget, gross_funds


def update_category_funds(conn, cursor, update_category):
    with conn:
        update_row = {
            'date': update_category[0],
            'total': update_category[1],
            'category': update_category[3]
        }
        cursor.execute("""UPDATE track_categories SET total =:total
                                    WHERE category=:category AND date=:date""", update_row)
        conn.commit()
