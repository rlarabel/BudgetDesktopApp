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
        cursor.execute("""UPDATE income SET funds =:funds, budget=:budget WHERE id=:id""", update_row)
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
        error_flag = 1
        user_date = data['-Date-']
        if user_date == None or data['-Trans total-'] == None:
            error_flag = -1
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
            error_flag == -2
        user_date = date_object.strftime('%Y-%m-%d')
        user_total = round(float(data['-Trans total-']), 2)        
        category_id = None
        cursor.execute("SELECT type FROM accounts WHERE name=:name", {'name': account_name})
        try:
            account_type = cursor.fetchone()[0]
        except:
            error_flag = -4
        if account_type == 'spending' or account_type == 'bills':
            if user_total < 0:
                error_flag = sql_trans_update(cursor, row_id, user_date, data, 
                                            user_total, account_name, category_id, data['-Selected Category-'])
            else:
                error_flag = sql_trans_update(cursor, row_id, user_date, data, 
                                            user_total, account_name, category_id, 'Unallocated Cash')
        elif account_type == 'savings' or account_type == 'asset':
                error_flag = sql_trans_update(cursor, row_id, user_date, data, 
                                            user_total, account_name, category_id, 'Not Available')
        else:
            error_flag = -5
        
        if error_flag < 0:
            conn.rollback()
        else:
            conn.commit()
        
        return error_flag


def sql_trans_update(cursor, row_id, user_date, data, user_total, account_name, category_id, cat_name):
    cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", {'name': cat_name, 'account': account_name})
    category_id = cursor.fetchone()
    if category_id:
        category_id = category_id[0]
        cursor.execute("""UPDATE transactions SET date=:date, payee=:payee, notes=:notes, total=:total, 
                    account=:account, category_id=:category_id
                            WHERE id=:id""",
                    {'id': row_id, 'date': user_date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                    'total': user_total, 'account': account_name, 'category_id': category_id})
    else: 
        return -3
    
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

def update_savings_acc(c, conn, sg, values, savings_acc_name, desired_i, real_value, state):
    # Initial Variables
    base_str = "was updated"
    i_flag = 0
    rv_flag = 0
    check_state = ('ACTIVE', 'ARCHIVE')
    state_flag = 0
    
    # Validate User Input
    try:
        new_i = float(values['-Interest-'])
    except ValueError:
        i_flag = -1
    try:
        new_rv = float(values['-Real Value-'])
    except ValueError:
        rv_flag = -1
    if values['-State-'] not in check_state:
        state_flag = -1

    # Updating Values for Savings Account DB
    if i_flag == 0 and desired_i != new_i:
        c.execute("UPDATE savings SET interest=:interest WHERE name=:name", 
                    {"interest": values['-Interest-'],"name": savings_acc_name})
        i_flag = 1
        base_str = "Interest " + base_str
    if rv_flag == 0 and real_value != new_rv:
        c.execute("UPDATE savings SET real_value=:real_value WHERE name=:name", 
                    {"real_value": values['-Real Value-'],"name": savings_acc_name})
        rv_flag = 1
        base_str = "Real Value, " + base_str
    if state_flag == 0 and state != values['-State-']:
        c.execute("UPDATE savings SET basis=:basis WHERE name=:name", 
                    {"basis": values['-Basis-'],"name": savings_acc_name})
        state_flag = 1
        base_str = "State, " + base_str

    if i_flag == -1 or rv_flag == -1 or state_flag == -1:
        sg.popup("Error updating values")
        conn.rollback
    elif i_flag == 1 or rv_flag == 1 or state_flag == 1:
        sg.popup(base_str)
        conn.commit()

def update_asset(c, conn, sg, values, data, set):
    name = data[0]
    if set == 0:
        i = data[2]
        amt = data[3]
        fv = data[5]
        date = data[6]
    else:
        i = data[7]
        amt = data[8]
        fv = data[10]
        date = data[11]

    # Initial Variables
    base_str = "was updated"
    i_flag = 0
    fv_flag = 0
    amt_flag = 0
    date_flag = 0
    
    # Validate User Input
    try:
        new_i = float(values['-Rate-'])
    except ValueError:
        i_flag = -1
    try:
        new_fv = float(values['-FV-'])
    except ValueError:
        fv_flag = -1
    try:
        new_amt = float(values['-AMT-'])
    except ValueError:
        amt_flag = -1
    try:
        date_obj = datetime.strptime(values['-Date-'], '%m-%d-%Y')
        new_date = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        date_flag = -1


    # Updating Values for Asset DB
    if i_flag == 0 and i != new_i:
        if set == 0:
            c.execute("UPDATE assets SET interest_1=:interest WHERE name=:name", 
                        {"interest": new_i,"name": name})
        else:
            c.execute("UPDATE assets SET i_2=:interest WHERE name=:name", 
                        {"interest": new_i,"name": name})
        i_flag = 1
        base_str = "Interest " + base_str
    if fv_flag == 0 and fv != new_fv:
        if set == 0:
            c.execute("UPDATE assets SET future_value_1=:fv WHERE name=:name", {"fv": new_fv, "name": name})
        else:
            c.execute("UPDATE assets SET future_value_2=:fv WHERE name=:name", {"fv": new_fv, "name": name})
        fv_flag = 1
        base_str = "Future Value, " + base_str
    if amt_flag == 0 and amt != new_amt:
        if set == 0:
            c.execute("UPDATE assets SET payment_1=:amt WHERE name=:name", {"amt": new_amt, "name": name})
        else:
            c.execute("UPDATE assets SET payment_2=:amt WHERE name=:name", {"amt": new_amt, "name": name})
        amt_flag = 1
        base_str = "Payment, " + base_str
    if date_flag == 0 and date != new_date:
        if set == 0:
            c.execute("UPDATE assets SET date_1=:date WHERE name=:name", {"date": new_date, "name": name})
        else:
            c.execute("UPDATE assets SET date_2=:date WHERE name=:name", {"date": new_date, "name": name})
        date_flag = 1
        base_str = "End date, " + base_str

    if i_flag == -1 or fv_flag == -1 or amt_flag == -1 or date_flag == -1:
        sg.popup("Error updating values")
        conn.rollback
    elif i_flag == 1 or fv_flag == 1 or amt_flag == 1 or date_flag == 1:
        sg.popup(base_str)
        conn.commit()