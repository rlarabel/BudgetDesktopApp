from datetime import datetime


def update_funds(conn, cursor):
    with conn:
        cursor.execute("SELECT * FROM money_flow")
        gross_funds = 0
        available_budget = 0
        for a_transaction in cursor.fetchall():
            if datetime.strptime(a_transaction[1], '%Y-%m-%d') < datetime.now():
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
            'budget': available_budget
        }
        cursor.execute("""UPDATE income SET funds =:funds, budget=:budget
                                            WHERE id=:id""", update_row)
        conn.commit()

        return available_budget, gross_funds


def update_category_budget(conn, cursor, row):
    with conn:
        update_row = {
            'date': row[0],
            'total': row[1],
            'category': row[3]
        }
        cursor.execute("""UPDATE track_categories SET total =:total
                                    WHERE category=:category AND date=:date""", update_row)
        conn.commit()


def update_account_track(conn, cursor, row):
    with conn:
        update_row = {
            'date': row[0],
            'total': row[1],
            'account': row[2]
        }
        cursor.execute("""UPDATE track_categories SET total =:total
                                    WHERE date=:date AND account=:account""", update_row)
        conn.commit()


def update_transaction(conn, cursor, data, row_id):
    with conn:
        user_date = str(data['-Year-']) + '-' + str(data['-Month-']) + '-' + str(data['-Day-'])
        user_total = round(float(data['-Trans total-']), 2)
        if data['-Outcome-']:
            cursor.execute("SELECT * FROM category WHERE name=:name", {'name': data['-Trans menu-']})
            category = cursor.fetchone()
            if category:
                cursor.execute("""UPDATE money_flow SET date=:date, payee=:payee, notes=:notes, total=:total, 
                                flow=:flow, account=:account, category=:category
                                        WHERE id=:id""",
                               {'id': row_id, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'flow': 'out', 'account': category[2], 'category': category[0]})
        else:
            cursor.execute("""UPDATE money_flow SET date=:date, payee=:payee, notes=:notes, total=:total, 
                            flow=:flow, account=:account, category=:category
                                    WHERE id=:id""",
                           {'id': row_id, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'flow': 'in', 'account': None, 'category': None})

        conn.commit()


def pretty_print_date(user_date, months):
    user_year, user_month = user_date.split('-')
    str_month = months[int(user_month)-1]
    return str_month + ' ' + user_year


def update_month_combo(months, user_date):
    combo = []
    user_year, user_month = user_date.split('-')
    current_year = int(datetime.now().year)

    if current_year < int(user_year):
        combo = months
    else:
        for i in range(datetime.now().month - 1, 12):
            combo.append(months[i])

    return combo
