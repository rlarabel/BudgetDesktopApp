from logic.create_items import make_account_menu, make_category_menu
from logic.delete_items import delete_account, delete_category
from logic.update_items import update_category_budget
from views.budget import edit_account_win, edit_category_win, move_funds_acc_win, move_funds_win 


def edit_budget(sg, conn, c, pov, budget_wc):
    account_menu = make_account_menu(conn, c)
    # Initial Variables needed 
    row_name = budget_wc.get_row_name()
    c.execute("SELECT * FROM accounts WHERE name=:name", {'name': row_name})
    account_data = c.fetchone()
    category_id = budget_wc.get_category_id()

    # Getting info of the row clicked on
    if account_data and not category_id:
        # User clicked on an account row in the budget table 														
        select_account(sg, conn, c, account_menu, row_name, account_data)
    else:
        # User clicked on a category row in the budget table																							
        select_category(sg, conn, c, category_id, row_name, pov)


def select_account(sg, conn, c, pov, account_menu, row_name, account_row): 
    event, values = move_funds_acc_win(sg, account_menu, row_name).read(close=True)
    if event == 'Update':																		# Transfer money to a different account
        transfer(sg, conn, c, pov, values, row_name)
    elif event == 'Edit Account':																# Edit Account
        edit_account(sg, conn, c, account_row, row_name)


def select_category(sg, conn, c, category_id, row_name, pov):
    c.execute("SELECT * FROM categories WHERE id=:id", {'id': category_id})
    category_row = c.fetchone()
    if category_row and row_name != "Available Cash":
        sel_category = category_row[1] 
        sel_account = category_row[2]        
        
        event, values = move_funds_win(sg, row_name).read(close=True)
        if event == 'Update':
            allocate(sg, conn, c, sel_account, sel_category, category_id, values, pov)
        if event == 'Edit Category':
           edit_category(sg, conn, c, sel_account, category_id, category_row, row_name)


def transfer(sg, conn, c, pov, values, row_name):
    if values['-To-'] not in (None, 'No Account Yet', row_name):
        move_funds = 0
        account_to = values['-To-']

        # Error Checking     
        move_flag = False
        try:
            move_funds = round(float(values['-Move Funds-']), 2)
        except ValueError:
            move_flag = True

        # Inserting two new transaction into the Database            
        if not move_flag:
            c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  row_name})
            category_id_from = c.fetchone()[0]
            c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  account_to})
            category_id_to = c.fetchone()[0]
            c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                    {'id': None, 'date': pov.get_today_str(), 'payee': None, 'notes': 'TRANSFER', 'total': 0-move_funds, 'account': row_name,
                    'category_id': category_id_from})
            c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                    {'id': None, 'date': pov.get_today_str(), 'payee': None, 'notes': 'TRANSFER', 'total': move_funds, 'account': account_to,
                    'category_id': category_id_to})
            conn.commit()
            sg.popup(f'Successful\n{move_funds} from {row_name} to {account_to}')
        else:
            sg.popup(f'Unsuccessful transfer')


def edit_account(sg, conn, c, account_row, account_menu, row_name):
    edit_event, edit_values = edit_account_win(sg, account_row, account_menu).read(close=True)
    if edit_event == 'Update' and edit_values['-Edit account-'] not in (None, row_name):
        new_acc_name = edit_values['-Edit account-']
        if new_acc_name not in account_menu:											# Change Name of Account
            c.execute("UPDATE accounts SET name=:new_account WHERE name=:old_account",
                    {'new_account': new_acc_name, 'old_account': row_name})
            conn.commit()
            sg.popup(f'{row_name} account name was changed to {new_acc_name}')
        else:																				# Move data to another account and then delete
            c.execute("SELECT type FROM accounts WHERE name=:name", {'name': row_name}) 
            account_from_type = c.fetchone()[0]
            c.execute("SELECT type FROM accounts WHERE name=:name", {'name': new_acc_name}) 
            account_to_type = c.fetchone()[0]
            if account_from_type == account_to_type:   
                delete_account(conn, c, new_acc_name, row_name)
                sg.popup(f'{row_name} was delete\nfunds were moved to account {new_acc_name}')
            else:
                sg.popup('Cannot Move data to different types of accounts')
    elif edit_event == 'Update' and edit_values['-Edit type-'] not in (None, account_row[1]) and edit_values['-Edit type-'] in ('income', 'spending','bills'):
        c.execute("Update accounts SET type=:type WHERE name=:name", {'type': edit_values['-Edit type-'], 'name': row_name})
        conn.commit()
        sg.popup(f"{row_name} changed from a {account_row[1]} to {edit_values['-Edit type-']} account")
    elif edit_values == 'Update':
        sg.popup("Was unable to update any information")


def allocate(sg, conn, c, sel_account, sel_category, category_id, values, pov):
    if values['-Move Funds-']:
        move_funds = 0
        track_date = pov.get_view_date_full_str()

        # Error Checking for User Input
        try:
            move_funds = round(float(values['-Move Funds-']), 2)
        except ValueError:
            move_funds = 0

        # TODO: Move this whole section into update_category_budget 
        with conn:
            # Checking for entry for a certain category and month, if not add one          
            c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                {'category_id': category_id, 'date': track_date})
            category_transaction = c.fetchone()
            if not category_transaction:
                c.execute("""INSERT INTO track_categories VALUES (:id, :date, :total, :account, :category_id)""",
                    {'id': None, 'date': track_date, 'total': 0, 'account': sel_account, 'category_id': category_id})
                conn.commit()
    
            # Selects an account and category
            c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                {'category_id': category_id, 'date': track_date})
            tracking_funds = c.fetchone()
            # moves funds from 'Available Cash' to desired category
            move_flag = True 
            if tracking_funds:
                tracking_funds = list(tracking_funds)
                tracking_funds[2] += move_funds 
            else:
                move_flag = False

            if move_flag:
                update_category_budget(conn, c, tracking_funds)
                sg.popup(f'Successful\n{sel_category} + {move_funds} ')
            else:
                sg.popup(f'Unsuccessful transfer')


def edit_category(sg, conn, c, sel_account, category_id, category_row, row_name):
    category_menu = make_category_menu(conn, c, sel_account, True)
    edit_event, values = edit_category_win(sg, category_row, category_menu).read(close=True)
    preset_budget = category_row[3]
    
    if edit_event == "Update":
        # User Input
        new_category = values['-Edit Category-']
        try:
            new_preset_budget = round(float(values['-Pre Set-']), 2)
        except ValueError:
            new_preset_budget = 0.0
        
        # Move Data and Delete old Category
        if not new_category or not category_id:
            sg.popup(f'failed to edit category')
        elif new_category in category_menu and new_category != row_name:
            delete_category(conn, c, new_category, sel_account, category_id)
            sg.popup(f'{row_name} was moved and deleted')
        elif row_name != new_category: 																		
            # Change category name
            c.execute("""UPDATE categories SET name=:new_category WHERE id=:id""",
                            {'id': category_id, 'new_category': new_category})
            conn.commit()
            sg.popup(f'{row_name} category name was changed to {new_category}')
        
        # Edit pre set budget
        if new_preset_budget != preset_budget:
            c.execute("""UPDATE categories SET pre_set=:pre_set WHERE id=:id""",
                            {'id': category_id, 'pre_set': new_preset_budget})
            conn.commit()
            sg.popup(f'{row_name} category pre-set budget was changed to {new_preset_budget}')
