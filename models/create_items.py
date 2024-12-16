from datetime import datetime
import csv

def make_total_funds (conn, cursor):
    grand_total = 0
    with conn:    
        cursor.execute("SELECT total FROM transactions")
        for temp in cursor.fetchall():
           grand_total += temp[0]
    return round(grand_total, 2)

def make_category_menu(conn, cursor, account, edit_flag=False):
    with conn:
        cursor.execute("SELECT name FROM categories WHERE account=:account", {'account': account})
        menu = []
        for temp in cursor.fetchall():
            if not (edit_flag and temp[0] == 'Unallocated Cash'):
                menu.append(temp[0])

        if not menu:
            menu = ['No Categories Yet']

        return tuple(menu)


def make_account_menu(conn, cursor, acc_type=['spending', 'bills']):
    with conn:
        menu = []
        for type in acc_type:
            cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': type})
            for row in cursor.fetchall():
                menu.append(row[0])
            if not menu:
                menu = ['No Account Yet']

        return tuple(menu)


def add_new_account(conn, cursor, data):
    error_flag = 1
    with conn:
        cursor.execute('SELECT name from accounts WHERE name=:name', {'name': data[0]})
        if cursor.fetchone():
            error_flag = 0
        new_row_acc = {
            'name': data[0],
            'type': data[1],
        }
        
        new_row_cat = {
            'id': None,
            'name': 'Unallocated Cash',
            'account': data[0]
        }
        if error_flag == 1:
            cursor.execute("INSERT INTO accounts VALUES (:name, :type)", new_row_acc)
            if new_row_acc['type'] == 'spending' or new_row_acc['type'] == 'bills':
                cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", new_row_cat)

            elif new_row_acc['type'] == 'savings':
                # Check User Input
                savings_info = data[2:]
                for i, info in enumerate(savings_info):
                    if i != 2:
                        if info == None:
                            savings_info[i] = 0.0
                        else:
                            try:
                                savings_info[i] = float(info)
                            except TypeError:
                                error_flag = -1
                    else:
                        try:
                            date_object = datetime.strptime(savings_info[i], '%m-%d-%Y')
                        except ValueError:
                            error_flag = -2
                date = date_object.strftime('%Y-%m-%d')
                
                # Organize data
                savings_info_entry = {
                    'name': data[0],
                    'state': 'ACTIVE',
                    'interest': savings_info[1],
                    'real_value': savings_info[0],
                }
                
                # Insert basic info into savings
                cursor.execute("INSERT INTO savings VALUES (:name, :state ,:interest, :real_value)", savings_info_entry)
                # Get an unused category ID and create a category
                cursor.execute("SELECT id FROM categories ORDER BY ID DESC")
                category_id = cursor.fetchone()[0] + 1
                cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", 
                            {'id': category_id, 'name': 'Not Available', 'account': data[0]})
                # Insert initial deposit into transaction
                cursor.execute("""INSERT INTO transactions VALUES 
                                    (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                {'id': None, 'date': date, 'payee': None, 'notes': 'Initial Deposit',
                                    'total': savings_info[0], 'account': data[0], 'category_id': category_id})
                    
            elif new_row_acc['type'] == 'asset':
                # TODO: user check with a try except
                try:
                    trans_amt = float(data[2])
                except TypeError:
                    error_flag = -1
                try:
                    date_object = datetime.strptime(data[3], '%m-%d-%Y')
                except ValueError:
                    error_flag = -2
                date = date_object.strftime('%Y-%m-%d')

                # Insert basic info into assets
                cursor.execute("""INSERT INTO assets VALUES 
                            (:name, :state, :none, :none, :present_value, 
                            :none, :none, :none, :none, :present_value, :none, :none )""", 
                            {'name': data[0], 'state': 'ACTIVE', 'none': None, 'present_value': trans_amt})
                # Get an unused category ID and create a category
                cursor.execute("SELECT id FROM categories ORDER BY ID DESC")
                category_id = cursor.fetchone()[0] + 1
                cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", 
                            {'id': category_id, 'name': 'Not Available', 'account': data[0]})
                # Insert initial purchase amount into transaction
                cursor.execute("""INSERT INTO transactions VALUES 
                                    (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                {'id': None, 'date': date, 'payee': None, 'notes': 'Initial Purchase',
                                    'total': trans_amt, 'account': data[0], 'category_id': category_id})
                
            elif new_row_acc['type'] == 'loan':
                #check user input
                try:
                    loan_amt = float(data[2])
                    interest = float(data[3])
                except TypeError:
                    error_flag = -1
                try:
                    s_date_object = datetime.strptime(data[4], '%m-%d-%Y')
                    e_date_object = datetime.strptime(data[5], '%m-%d-%Y')
                except ValueError:
                    error_flag = -2
                start_date = s_date_object.strftime('%Y-%m-%d')
                end_date = e_date_object.strftime('%Y-%m-%d')
                cursor.execute("INSERT INTO loans VALUES (:name, :state, :interest, :end_date, :present_amt)", 
                               {'name': new_row_acc['name'], 'state': 'ACTIVE', 'interest': interest, 
                                'end_date': end_date, 'present_amt': loan_amt})
                cursor.execute("SELECT id FROM categories ORDER BY ID DESC")
                category_id = cursor.fetchone()[0] + 1
                cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", 
                            {'id': category_id, 'name': 'Not Available', 'account': data[0]})
                cursor.execute("""INSERT INTO transactions VALUES 
                                    (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                {'id': None, 'date': start_date, 'payee': None, 'notes': 'Initial Loan',
                                    'total': loan_amt, 'account': data[0], 'category_id': category_id})
            else:
                error_flag = -1
        if error_flag == 1:
            conn.commit()
            return error_flag
        else: 
            conn.rollback()
            return error_flag


def add_new_category(conn, cursor, data, category_id=None):
    with conn:
        # Checking for a parent account and duplicate categories 
        cursor.execute("SELECT * FROM accounts WHERE name=:name", {'name': data['-Account name-']})
        parent_account = cursor.fetchone()
        cursor.execute("SELECT * FROM categories WHERE name=:name AND account=:account", 
                       {'name': data['-New category-'], 'account': data['-Account name-']})
        duplicate_category = cursor.fetchone()
        if parent_account == None or duplicate_category != None:
            return
        
        # Adding the row if both checks pass
        new_row = {
            'id': category_id,
            'name': data['-New category-'],
            'account': parent_account[0]
        }
        cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", new_row)
        conn.commit()


def add_transaction(conn, cursor, data, sel_account, trans_id=None, commit_flag=True):
    with conn:
        error_flag = 1
        user_date = data['-Date-']
        if user_date == None or data['-Trans total-'] == None:
            error_flag = -1
            return error_flag
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
            error_flag = -2
            return error_flag
        date = date_object.strftime('%Y-%m-%d')
        user_total = round(float(data['-Trans total-']), 2)        
        category_id = None
        
        cursor.execute("SELECT type FROM accounts WHERE name=:name", {"name":sel_account})
        account_type = cursor.fetchone()[0]
        if account_type == "spending" or account_type == "bills":
            # Outcome Transaction
            if user_total < 0:
                # Selecting desired category_id
                cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", 
                               {'name': data['-Selected Category-'], 'account': sel_account})
                category_id = cursor.fetchone()
                if category_id:
                    category_id = category_id[0]
                    cursor.execute("""INSERT INTO transactions VALUES 
                                    (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                {'id': trans_id, 'date': date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                    'total': user_total, 'account': sel_account, 'category_id': category_id})
                else:
                    error_flag = -3
            # Income Transaction
            else:
                cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", 
                               {'name': 'Unallocated Cash', 'account': sel_account})
                category_id = cursor.fetchone()
                if category_id:
                    category_id = category_id[0]
                    cursor.execute("""INSERT INTO transactions  VALUES 
                                                (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                            {'id': trans_id, 'date': date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'account': sel_account, 'category_id': category_id})
                else: 
                    error_flag = -3
        if account_type == "savings":
            cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", 
                           {'name': 'Not Available', 'account': sel_account})
            category_id = cursor.fetchone()
            if category_id:
                category_id = category_id[0]
                cursor.execute("""INSERT INTO transactions VALUES 
                                            (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                        {'id': trans_id, 'date': date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'account': sel_account, 'category_id': category_id})
                cursor.execute("UPDATE savings SET real_value = real_value + :add_value WHERE name = :name", 
                               {'add_value': user_total, 'name': sel_account})
            else:
                error_flag = -3
        if commit_flag==True and error_flag==1:
            conn.commit()
            return error_flag
        else:
            conn.rollback()
            return error_flag

def csv_entry(conn, cursor, account, filename):
    date_column = -1 
    payee_column = -1
    notes_column = -1
    total_column = -1
    payee = None
    notes = None
    with open(filename, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        first_row = next(csv_reader)
        for i, header in enumerate(first_row):
            if header.lower() == 'date' or header.lower() == 'dates':
                date_column = i
            elif header.lower() == 'payee' or header.lower() == 'payees':
                payee_column = i
            elif header.lower() == 'note' or header.lower() == 'notes':
                notes_column = i
            elif header.lower() == 'total' or header.lower() == 'totals':
                total_column = i
        if date_column == -1 or total_column == -1:
            return -3
        for row in csv_reader:
            date = row[date_column]
            total = row[total_column]
            if payee_column > -1:
                payee = row[payee_column]
            if notes_column > -1:
                notes = row[notes_column]
            data = {'-Trans total-': total, 
                    '-Payee-': payee, 
                    '-Notes-': notes, 
                    '-Date-': date, 
                    '-Selected Category-': 'Unallocated Cash'}
            entry_flag = add_transaction(conn, cursor, data, account, None, False)
            if entry_flag != 1:
                return entry_flag

    conn.commit()        
    return 1    
            