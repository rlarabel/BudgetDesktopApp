from models.update_items import update_funds


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


def make_account_menu(conn, cursor, acc_type='budget'):
    with conn:
        cursor.execute("SELECT * FROM account WHERE type=:type", {'type': acc_type})
        menu = []
        for row in cursor.fetchall():
            menu.append(row[0])
        if not menu:
            menu = ['No Account Yet']

        return tuple(menu)


def add_new_category(conn, cursor, data):
    with conn:
        cursor.execute("SELECT * FROM account WHERE name=:name", {'name': data['-Account name-']})
        parent_account = cursor.fetchone()

        new_row = {
            'name': data['-New category-'],
            'monthly_budget': 0,
            'trackaccount': parent_account[0]
        }
        cursor.execute("INSERT INTO category VALUES (:name, :monthly_budget, :trackaccount)", new_row)
        conn.commit()


def add_transaction(conn, cursor, data):
    with conn:
        user_date = str(data['-Year-']) + '-' + str(data['-Month-']) + '-' + str(data['-Day-'])
        user_total = round(float(data['-Trans total-']), 2)
        if data['-Outcome-'] and data['-Trans menu-']:
            cursor.execute("SELECT * FROM category WHERE name=:name", {'name': data['-Trans menu-']})
            category = cursor.fetchone()
            if category:
                cursor.execute("""INSERT INTO money_flow  VALUES 
                                (:id, :date, :payee, :notes, :total, :flow, :account, :category)""",
                               {'id': None, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'flow': 'out', 'account': category[2], 'category': category[0]})
        else:
            cursor.execute("""INSERT INTO money_flow  VALUES 
                                            (:id, :date, :payee, :notes, :total, :flow, :account, :category)""",
                           {'id': None, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'flow': 'in', 'account': None, 'category': None})

        conn.commit()
