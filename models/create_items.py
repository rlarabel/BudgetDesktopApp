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


def make_account_menu(conn, cursor, acc_type='spending'):
    with conn:
        cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': acc_type})
        menu = []
        for row in cursor.fetchall():
            menu.append(row[0])
        if not menu:
            menu = ['No Account Yet']

        return tuple(menu)


def add_new_account(conn, cursor, data):
    with conn:
        new_row_acc = {
            'name': data[0],
            'type': data[1],
        }
        
        new_row_cat = {
            'id': None,
            'name': 'Unallocated Cash',
            'account': data[0]
        }
        cursor.execute("INSERT INTO accounts VALUES (:name, :type)", new_row_acc)
        cursor.execute("INSERT INTO categories VALUES (:id, :name, :account)", new_row_cat)
        conn.commit()


def add_new_category(conn, cursor, data, category_id=None):
    with conn:
        # Checking for a parent account and duplicate categories 
        cursor.execute("SELECT * FROM accounts WHERE name=:name", {'name': data['-Account name-']})
        parent_account = cursor.fetchone()
        cursor.execute("SELECT * FROM categories WHERE name=:name AND account=:account", {'name': data['-New category-'], 'account': data['-Account name-']})
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
        date = date_object.strftime('%Y-%m-%d')
        user_total = round(float(data['-Trans total-']), 2)        
        category_id = None
        
        # Outcome Transaction
        if user_total < 0:
            # Selecting desired category_id
            cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", {'name': data['-Selected Category-'], 'account': sel_account})
            category_id = cursor.fetchone()[0]
            if category_id:
                cursor.execute("""INSERT INTO transactions VALUES 
                                (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                               {'id': trans_id, 'date': date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                                'total': user_total, 'account': sel_account, 'category_id': category_id})
        # Income Transaction
        else:
            cursor.execute("SELECT id FROM categories WHERE name=:name AND account=:account", {'name': 'Unallocated Cash', 'account': sel_account})
            category_id = cursor.fetchone()[0]
            if category_id:
                cursor.execute("""INSERT INTO transactions  VALUES 
                                            (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                           {'id': trans_id, 'date': date, 'payee': data['-Payee-'], 'notes': data['-Notes-'],
                            'total': user_total, 'account': sel_account, 'category_id': category_id})
        if(commit_flag==True):
            conn.commit()
        return 1

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
            data = {'-Trans total-': total, '-Payee-': payee, '-Notes-': notes, "-Date-": date, '-Selected Category-': 'Unallocated Cash'}
            entry_flag = add_transaction(conn, cursor, data, account, None, False)
            if entry_flag != 1:
                print(data['-Trans total-'])
                print(data['-Date-'])
                return entry_flag

    conn.commit()        
    return 1    
            