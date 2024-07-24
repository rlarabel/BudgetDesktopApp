from datetime import datetime

def make_total_funds (conn, cursor):
    grand_total = 0
    with conn:    
        cursor.execute("SELECT total FROM transactions")
        for temp in cursor.fetchall():
           grand_total += temp[0]
    return grand_total

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


def add_transaction(conn, cursor, data, sel_account, trans_id=None):
    with conn:
    	# Formatting User Input Date and Total
        input_month = int(data['-Month-'])
        input_day = int(data['-Day-'])
        if input_month < 10:
            input_month = '0' + str(input_month)
        else: 
            input_month = str(input_month)
        if input_day < 10:
            input_day =  '0' + str(data['-Day-'])
        else:
            input_day = str(data['-Day-'])
        user_date = str(data['-Year-']) + '-' + input_month + '-' + input_day
        # Checks to make sure date is accurate
        try:
            date_object = datetime.strptime(user_date, '%Y-%m-%d')
        except ValueError:
            # TODO: return error message
            return
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

        conn.commit()
