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

def update_savings_acc(c, conn, sg, values, name, desired_i, amount, date, state):
    # Initial Variables
    base_str = "was updated"
    i_flag = 0
    rv_flag = 0
    name_flag = 0
    new_name = values['-Name-']
    
    # Validate User Input
    try:
        new_i = float(values['-Interest-'])
    except ValueError:
        i_flag = -1
    try:
        new_rv = float(values['-Real Value-'])
    except ValueError:
        rv_flag = -1

    # Updating Values for Savings Account DB
    if i_flag == 0 and desired_i != new_i:
        c.execute("UPDATE savings SET interest=:interest WHERE name=:name", 
                    {"interest": values['-Interest-'],"name": name})
        i_flag = 1
        base_str = "Interest " + base_str
    if rv_flag == 0 and amount != new_rv:
        c.execute("UPDATE track_savings SET amount=:amount WHERE account=:account AND date=:date", 
                    {"amount": values['-Real Value-'], "account": name, "date": date})
        rv_flag = 1
        base_str = "Real Value, " + base_str
    if name != new_name:
        c.execute("SELECT name FROM accounts")
        taken_names = c.fetchall()
        if (new_name,) not in taken_names:
            c.execute("UPDATE accounts SET name=:new_name WHERE name=:name", {"new_name": new_name, "name": name})
            name_flag = 1
            base_str = "Name, " + base_str
        else:
            name_flag = -1

    if i_flag == -1 or rv_flag == -1 or name_flag == -1:
        sg.popup("Error updating values")
        conn.rollback()
    elif i_flag == 1 or rv_flag == 1 or name_flag == 1:
        sg.popup(base_str)
        conn.commit()

def update_asset(c, conn, sg, values, data, assets_name):
    c.execute("SELECT name FROM accounts")
    taken_names = c.fetchall()
    initial_flag = 0
    name_flag = 0
    date_flag = 0
    date = values['-Start Date-']
    
    try:
        date = datetime.strptime(date, '%m-%d-%Y')
    except ValueError:
        date_flag = -1
    date = date.strftime('%Y-%m-%d')
    if date != data[2] and date_flag == 0:
        c.execute("UPDATE assets SET initial_date=:date WHERE name=:name",
                  {'date': date, 'name': data[0]})
        date_flag = 1
    if values['-Initial Amount-'] != data[2]:
        c.execute("UPDATE assets SET initial_amount=:new_amt WHERE name=:name",
                  {'new_amt': values['-Initial Amount-'], 'name': data[0]})
        initial_flag = 1
    if values['-Name-'] == assets_name:
        pass
    elif (values['-Name-'],) in taken_names:
        sg.popup("Name already taken")
    else:
        c.execute("UPDATE accounts SET name=:new_name WHERE name=:name", 
                    {"new_name": values['-Name-'], "name": data[0]})        
        name_flag = 1

    if name_flag == -1 or initial_flag == -1 or date_flag == -1:
        conn.rollback()
        sg.popup('Error updating')
    if name_flag == 1 or initial_flag == 1 or date_flag == 1:
        conn.commit()
        sg.popup('Update Successful')
        #sg.popup(f"Changed {data[0]} to {values['-Name-']}")
    

def update_asset_2(c, conn, sg, values, data, set):
    name = data[0]
    if set == 0:
        i = data[4]
        amt = data[5]
        fv = data[7]
        date = data[8]
    else:
        i = data[9]
        amt = data[10]
        fv = data[12]
        date = data[13]

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
        conn.rollback()
    elif i_flag == 1 or fv_flag == 1 or amt_flag == 1 or date_flag == 1:
        sg.popup(base_str)
        conn.commit()

def update_loan(c, conn, sg, values, name, interest, start_date_obj, end_date_obj, initial_amount, present_amt):
    # Initial Variables
    base_str = "was updated"
    i_flag = 0
    amt_flag = 0
    date_flag = 0
    name_flag = 0
    initial_amt_flag = 0
    
    # Validate User Input
    try:
        new_i = float(values['-Interest-'])
    except ValueError:
        i_flag = -1
    try:
        new_amt = float(values['-AMT-'])
    except ValueError:
        amt_flag = -1
    try:
        date_obj = datetime.strptime(values['-End Date-'], '%m-%d-%Y')
        new_date = date_obj.strftime('%Y-%m-%d')
        date_obj = datetime.strptime(values['-Start Date-'], '%m-%d-%Y')
        new_start_date = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        date_flag = -1
    try:
        new_initial_amt = float(values['-Initial Amount-'])
    except ValueError:
        initial_amt_flag = -1

    new_name = values['-Name-']

    # Updating Values for Loan DB
    if i_flag == 0 and interest != new_i:
        c.execute("UPDATE loans SET interest=:interest WHERE name=:name", 
                        {"interest": new_i, "name": name})
        i_flag = 1
        base_str = "Interest " + base_str
    if amt_flag == 0 and present_amt != new_amt:
        c.execute("UPDATE loans SET present_amt=:amt WHERE name=:name", {"amt": new_amt, "name": name})
        amt_flag = 1
        base_str = "Present Loan Amt, " + base_str
    if date_flag == 0 and end_date_obj != date_obj:
        c.execute("UPDATE loans SET end_date=:date WHERE name=:name", {"date": new_date, "name": name})
        date_flag = 1
        base_str = "Payoff date, " + base_str
    if date_flag == 0 and end_date_obj != date_obj:
        c.execute("UPDATE loans SET start_date=:date WHERE name=:name", {"date": new_start_date, "name": name})
        date_flag = 1
        base_str = "Start date, " + base_str
    if name != new_name:
        c.execute("SELECT name FROM accounts")
        taken_names = c.fetchall()
        if (new_name,) not in taken_names:
            c.execute("UPDATE accounts SET name=:new_name WHERE name=:name", {"new_name": new_name, "name": name})
            name_flag = 1
            base_str = "Name, " + base_str
        else:
            name_flag = -1
    if initial_amt_flag == 0 and initial_amount != new_initial_amt:
        c.execute("UPDATE loans SET initial_amount=:amt WHERE name=:name", {"amt": new_initial_amt, "name": name})
        amt_flag = 1
        base_str = "Present Loan Amt, " + base_str

    if i_flag == -1 or amt_flag == -1 or date_flag == -1 or name_flag == -1 or initial_amt_flag == -1:
        sg.popup("Error updating values")
        conn.rollback()
    elif i_flag == 1 or amt_flag == 1 or date_flag == 1 or name_flag == 1 or initial_amt_flag == 1:
        sg.popup(base_str)
        conn.commit()
