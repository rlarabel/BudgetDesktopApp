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

        return round(available_budget, 2), round(gross_funds, 2)


def update_category_budget(conn, cursor, row):
    with conn:
        update_row = {
            'id': row[0],
            'total': row[2]
        }
        cursor.execute("""UPDATE track_categories SET total =:total
                                    WHERE id=:id""", update_row)
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


def update_transaction(conn, cursor, data, row_id, account_name):
    with conn:
        user_date = data['-Date-']
        if user_date == None or data['-Trans total-'] == None:
            return -1
        # Checks to make sure date is accurate
        formats = [
            '%m-%d-%Y',
            '%m/%d/%Y',
            '%m-%d-%y',
            '%m/%d/%y',
        ]
        date_object = None
        for fmts in formats:
            try:
                date_object = datetime.strptime(user_date, fmts)
            except ValueError:
                continue
        if not date_object:
            # Return error for improper date
            return -2
        user_date = date_object.strftime('%Y-%m-%d')
        user_total = round(float(data['-Trans total-']), 2)        
        category_id = None
        
        if user_total < 0:
            cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", {'name': data['-Selected Category-'], 'account': account_name})
            category_id = cursor.fetchone()[0]
            if category_id:
                cursor.execute("""UPDATE transactions SET date=:date, payee=:payee, notes=:notes, total=:total, 
                                account=:account, category_id=:category_id
                                        WHERE id=:id""",
                               {'id': row_id, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'account': account_name, 'category_id': category_id})
        else:
            cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", {'name': 'Unallocated Cash', 'account': account_name})
            category_id = cursor.fetchone()[0]
            if category_id:
                cursor.execute("""UPDATE transactions SET date=:date, payee=:payee, notes=:notes, total=:total, 
                            account=:account, category_id=:category_id
                                    WHERE id=:id""",
                           {'id': row_id, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'account': account_name, 'category_id': category_id})

        conn.commit()
        return 1


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
