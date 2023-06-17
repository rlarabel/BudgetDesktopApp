import PySimpleGUI as sg
from views.transaction_windows import create_transaction_window, create_new_transaction, edit_transaction_window, select_account, select_category
from views.budget_windows import move_funds_win, edit_track_acc_win, edit_account_win, edit_category_win, create_account_win, create_category_win, move_funds_acc_win
from models.create_items import make_category_menu, add_new_account, add_new_category, add_transaction, make_account_menu, make_total_funds
from models.sheets import set_row_colors, make_track_sheet, make_transaction_sheet, make_budget_sheet, set_track_row_colors
from models.update_items import update_funds, update_category_budget, update_transaction, update_account_track, pretty_print_date, update_month_combo
from models.make_db import create_db_tables
from models.delete_items import delete_account, delete_category
import sqlite3

from datetime import datetime
import os

BUDGET = '-Budget-'
FUNDS = '-Funds-'


def main():
    year_combo = []
    for i in range(datetime.now().year - 3, datetime.now().year + 5):
        year_combo.append(str(i))
    
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Connecting to the Database
    
    # ***** Uncomment for WINDOWS **********
    # user_path = os.environ['USERPROFILE']
    # **************************************
    
    # ***** Uncomment for Linux ************
    user_path = os.path.expanduser( '~' )
    # **************************************
    app_data_path = user_path + '/AppData/Local/RatTrap'
    location_exist = os.path.exists(app_data_path)
    app_path = app_data_path + '/app.db'
    #db_exist = os.path.exists(app_path)
    if not location_exist:
        os.makedirs(app_data_path)
    conn = sqlite3.connect(app_path)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    create_db_tables(conn, c)
	    
    visible_columns_transactions = [False, True, True, True, True, True, True]
    visible_columns_budget = [False, True, True, True, True, True, True]
    
    view_date = datetime.now().strftime("%Y-%m")
    
    account_menu = make_account_menu(conn, c)
    track_menu = make_account_menu(conn, c, 'track')
    budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
    track_sheet = make_track_sheet(conn, c, view_date, all_months)
    menu_def = [['&New', ['Add Account', 'Add Category']],
                ['&Views', ['&Transactions']]]

    # Layout definition
    budget_layout = [
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text('Account Window', justification='center', size=(67, 1), font='Any 15')],
        [sg.Text(size=(55, 1), key='View date', font='Any 11'),
         sg.Combo(values=year_combo, k='-Year-', enable_events=True, pad=((160, 1), (1, 1)), bind_return_key=True),
         sg.Combo(values=all_months, readonly=True, k='-Month-', enable_events=True)],
        [sg.Button('Categorize Funds'), sg.Button('Move Funds To Different Account')],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=False,
                  headings=['Category ID','Name', 'Budget', 'Upcoming Expenses', 'Spendings' , 'Budget left', 'Available'],
                  row_colors=set_row_colors(conn, c, unallocated_cash_info), enable_events=True, justification='left',
                  col_widths=[0, 30, 12, 13, 13, 13, 12], font='Any 11', num_rows=13, visible_column_map=visible_columns_budget)]]
        
        #TODO: Make another view for investment accounts
        #[sg.Table(track_sheet, key='-Track table-', auto_size_columns=False,
        #          headings=['Account Name', 'Monthly Funds', 'Total Funds', 'Total', 'To Reach Goal', 'By Date'],
        #          enable_events=True, col_widths=[20, 16, 13, 10, 13, 11], font='Any 11', num_rows=8,
        #          row_colors=set_track_row_colors(conn, c))]]

    # Create windows
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True, resizable=True)
    transaction_win_active = False
    
    # Updates the window with default Values
    budget_win['View date'].update(pretty_print_date(view_date, all_months))

    # Event Loop
    while True:
        event, values = budget_win.read()

        if not event:
            break
        if event == 'Add Account':
            event, values = create_account_win(sg).read(close=True)
            if event == 'Save':
                create_acc = values['-New account-']
                c.execute("SELECT * FROM accounts WHERE name=:name", {'name': create_acc})
                existing_acc = c.fetchone()
                if values['-Spending account-']:
                    account_type = 'spending'
                else:
                	#TODO: Set up investment accounts
                    #account_type = 'investment'
                    account_type = 'spending' 
                if not existing_acc and create_acc:
                    add_new_account(conn, c, [create_acc, account_type])
                    sg.popup(f'Successfully created {create_acc}')
                elif existing_acc:
                    sg.popup(f'There is already an existing {create_acc}')
                elif not create_acc:
                    sg.popup(f'There is missing info needed to create the account')

        elif event == 'Add Category':
            #TODO: Add user checking, so no one can add same account name and category name
            event, values = create_category_win(sg, account_menu).read(close=True)
            if event == 'Save':
                create_cat = values['-New category-']
                c.execute("SELECT * FROM categories WHERE name=:name AND account=:account", {'name': create_cat, 'account':values['-Account name-']})
                existing_cat = c.fetchone()
                if not existing_cat and create_cat and values['-Account name-']:
                    add_new_category(conn, c, values)
                    sg.popup(f'Successfully created {create_cat}')
                elif existing_cat:
                    sg.popup(f'There is already an existing {create_cat}')
                elif not create_cat or not values['-Account name-']:
                    sg.popup(f'There is missing info needed to open a category')

        elif event in ('-Year-', '-Month-'):
            set_year, month_int = view_date.split('-')
            if values['-Month-']:
                for i, month in enumerate(all_months, 1):
                    if values['-Month-'] == month:
                        if i < 10:
                            month_int = '0' + str(i)
                        else:
                            month_int = str(i)
            # Checks if the year given is an int and between 1800 - 2500
            try:
                int_user_year = int(values['-Year-'])
            except ValueError:
                int_user_year = None                
            
            if int_user_year and int_user_year < 2500 and int_user_year > 1800: 
                set_year = values['-Year-']
            view_date = set_year + '-' + month_int

        elif event == 'Transactions' and not transaction_win_active:
            transaction_win_active = True
            budget_win.Hide()
            transaction_sheet = make_transaction_sheet(conn, c)
            transaction_win = create_transaction_window(sg, transaction_sheet, visible_columns_transactions)
            keys_to_validate = ['-Year-', '-Month-', '-Day-', '-Trans total-']
            total_funds = make_total_funds(conn, c)
            transaction_win[FUNDS].update(total_funds)
            
            while transaction_win_active:
                event, values = transaction_win.Read()
                if event in ('Back To Accounts', None):
                    transaction_win.Close()
                    transaction_win_active = False
                    budget_win.UnHide()
                elif event == 'New Transaction':
                    # Gets desired account info before the next window
                    acc_event, acc_values = select_account(sg, account_menu).read(close=True)
                    if acc_event == 'OK' and acc_values['-Account menu-']:
                        selected_account = acc_values['-Account menu-']
                        category_menu = make_category_menu(conn, c, selected_account)
                    	# New Transaction Window
                        event, values = create_new_transaction(sg, category_menu).read(close=True)
                        if event == 'Save':
                            set_transaction = True
                            for validate in keys_to_validate:
                                if not values[validate]:
                                    set_transaction = False
                            if set_transaction:
                                year = values['-Year-']
                                month = values['-Month-']
                                day = values['-Day-']
                                add_transaction(conn, c, values, selected_account)
                                sg.popup(f"New transaction for {year}-{month}-{day}")
                            else:
                                sg.popup('Missing info: unable to update the transaction')
                elif event == '-Trans table-':
                    transaction_row = None
                    if values['-Trans table-']:
                        row_int = values['-Trans table-'][0]
                        trans_id = transaction_sheet[row_int][0]
                        selected_account = transaction_sheet[row_int][2]
                        c.execute("SELECT * FROM transactions WHERE id=:id", {'id': trans_id})
                        transaction_row = c.fetchone()
                    if transaction_row:

                        category_menu = make_category_menu(conn, c, selected_account)
                        c.execute("SELECT name FROM categories WHERE id=:id", {'id': transaction_row[6]})
                        
                        event, values = edit_transaction_window(sg, transaction_row, c.fetchone()[0] ,category_menu).read(close=True)
                        if event == 'Save':
                            set_transaction = True

                            for validate in keys_to_validate:
                                if not values[validate]:
                                    set_transaction = False

                            if set_transaction:      # This is where the transaction is updated
                                update_transaction(conn, c, values, trans_id, selected_account)
                                sg.popup('Transaction was updated')
                            else:
                                sg.popup('Missing info: unable to update the transaction')
                        elif event == 'Delete':
                            c.execute("DELETE FROM transactions WHERE id=:id", {'id': trans_id})
                            conn.commit()
                            sg.popup('Transaction was delete')

                if transaction_win_active:
                    transaction_win.BringToFront()
                    transaction_sheet = make_transaction_sheet(conn, c)
                    transaction_win['-Trans table-'].update(transaction_sheet)
                    total_funds = make_total_funds(conn, c)
                    transaction_win[FUNDS].update(total_funds)

        elif event == 'Categorize Funds':
            # Gets desired account info before the next window
            event = None
            acc_event, acc_values = select_account(sg, account_menu).read(close=True)
            if acc_event == 'OK' and acc_values['-Account menu-']:
                selected_account = acc_values['-Account menu-']
                category_menu = make_category_menu(conn, c, selected_account, True)
                event, values = move_funds_win(sg, category_menu).read(close=True)
            if event == 'Update':
                if values['-Menu-'] not in (None, 'No Categories Yet') and values['-Move Funds-']:
                    math_operator = values['-Math Ops-']
                    category_name = values['-Menu-']
                    move_funds = 0
                    
                    # Format view date for DB
                    input_year, input_month = view_date.split('-')
                    input_month = int(input_month)
                    if input_month < 10:
                        input_month = '0' + str(input_month)
                    else: 
                        input_month = str(input_month)
                    track_date = input_year + '-' + input_month + '-01'
                    
                    # Error Checking for User Input
                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        math_operator = ''


                    with conn:
                    	# Checking for entry for a certain category and month, if not add one
                        c.execute("SELECT * FROM categories WHERE name=:name AND account=:account",
                                  {'name': category_name, 'account': selected_account})
                        #category_info = 
                        category_id = c.fetchone()[0]           
                        c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                                  {'category_id': category_id, 'date': track_date})
                        category_transaction = c.fetchone()
                        if not category_transaction:
                            c.execute("""INSERT INTO track_categories VALUES (:id, :date, :total, :account, :category_id)""",
                                      {'id': None, 'date': track_date, 'total': 0, 'account': selected_account,
                                       'category_id': category_id})
                            conn.commit()
                        
                        # Selects an account and category
                        c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                                  {'category_id': category_id, 'date': track_date})
                        tracking_funds = c.fetchone()
                    
                    # moves funds from a selected category to anohter selectred category 
                    if tracking_funds:
                        tracking_funds = list(tracking_funds)
                        move_flag = True
                        
                        if math_operator == '-':
                            tracking_funds[2] -= move_funds
                        elif math_operator == '+':
                            tracking_funds[2] += move_funds
                        elif math_operator == '*':
                            tracking_funds[2] *= move_funds
                        elif math_operator == '/':
                            try:
                                tracking_funds[2] /= move_funds
                            except ZeroDivisionError:
                                move_flag = False
                        elif math_operator == '=':
                            tracking_funds[2] = move_funds
                        else:
                            move_flag = False

                        if move_flag:
                            update_category_budget(conn, c, tracking_funds)
                            sg.popup(f'Successful\n{category_name} {math_operator} {move_funds} ')
                        else:
                            sg.popup(f'Unsuccessful transfer')

        elif event == 'Move Funds To Different Account':
            event, values = move_funds_acc_win(sg, account_menu).read(close=True)
            if event == 'Update':
                # Adds a new transaction to a category unless same date
                if values['-From-'] not in (None, 'No Account Yet') and values['-To-'] not in (None, 'No Account Yet') and values['-To-'] != values['-From-']:
                    move_funds = 0
                    account_from = values['-From-']
                    account_to = values['-To-']
                    
                    # Error Checking     
                    move_flag = False
                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        move_flag = True

                   # Inserting two new transaction into the Database
                    with conn:
                        if not move_flag:
                            c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  account_from})
                            category_id_from = c.fetchone()[0]
                            c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  account_to})
                            category_id_to = c.fetchone()[0]
                            c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                      {'id': None, 'date': datetime.now().strftime('%Y-%m-%d'), 'payee': None, 'notes': 'TRANSFER', 'total': 0-move_funds, 'account': account_from,
                                       'category_id': category_id_from})
                            c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                      {'id': None, 'date': datetime.now().strftime('%Y-%m-%d'), 'payee': None, 'notes': 'TRANSFER', 'total': move_funds, 'account': account_to,
                                       'category_id': category_id_to})
                            conn.commit()
                            sg.popup(f'Successful\n{move_funds} from {account_from} to {account_to}')
                        else:
                            sg.popup(f'Unsuccessful transfer')

        elif event == '-Table-':
            # Getting info of the row clicked on
            if values['-Table-']:
                row_int = values['-Table-'][0]
                row = budget_sheet[row_int]
                row_name = row[1]
                try:
                    row_cat_id = int(row[0])
                except ValueError:
                    row_cat_id = None
                c.execute("SELECT * FROM accounts WHERE name=:name", {'name': row_name})
                account_row = c.fetchone()
            if account_row and not row_cat_id:
                # Edit Account
                event, values = edit_account_win(sg, account_row, account_menu).read(close=True)
                if event == 'Update' and values['-Edit account-'] not in (None, row_name):
                    c.execute("SELECT name FROM accounts")
                    all_acccount_names = c.fetchall()
                    new_acc_name = values['-Edit account-']
                    if new_acc_name not in all_account_names:
                        # Change Name of Account
                        c.execute("UPDATE accounts SET name=:new_account WHERE name=:old_account",
                                  {'new_account': new_acc_name, 'old_account': row_name})
                        conn.commit()
                        sg.popup(f'{row_name} account name was changed to {new_acc_name}')
                    else:
                        # Move data to another account and then delete
                        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': row_name}) 
                        account_from_type = c.fetchone()[0]
                        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': new_acc_name}) 
                        account_to_type = c.fetchone()[0]
                        if account_from_type == account_to_type:   
                            delete_account(conn, c, new_acc_name, row_name)
                            sg.popup(f'{row_name} was delete\nfunds were moved to account {new_acc_name}')
                        else:
                            sg.popup('Cannot Move data to different types of accounts')
            else:
                # Edit Category
                c.execute("SELECT * FROM categories WHERE id=:id", {'id': row_cat_id})
                category_row = c.fetchone()
                if category_row:
                    old_cat_name = category_row[1] 
                    old_acc = category_row[2]
                    
                    event, values = edit_category_win(sg, category_row, account_menu).read(close=True)
                    
                    if event == "Move" and old_cat_name != 'Unallocated Cash':
                        # Move Data and Delete old Category
                        new_acc = values['-Edit account-']
                        category_menu = make_category_menu(conn, c, new_acc, True)
                        cat_event, cat_values = select_category(sg, category_menu).read(close=True)
                        new_cat_id = None
                        
                        if cat_event == "OK" and cat_values:
                            new_category = cat_values["-Selected Category-"]
                            c.execute('SELECT id FROM categories WHERE account=:account AND name=:name', {'name': new_category, 'account': new_acc})
                            new_cat_id = c.fetchone()[0]
                            if new_cat_id:
                                c.execute("""UPDATE track_categories SET account=:new_account, category_id=:new_cat_id
                                                    WHERE category_id=:old_cat_id AND account=:old_account""",
                                      {'new_account': new_acc, 'old_account': old_acc, 'new_cat_id': new_cat_id, 'old_cat_id': row_cat_id})
                                c.execute("""UPDATE transactions SET account=:new_account, category_id=:new_cat_id
                                                    WHERE category_id=:old_cat_id AND account=:old_account""",
                                      {'new_account': new_acc, 'old_account': old_acc, 'new_cat_id': new_cat_id, 'old_cat_id': row_cat_id})
                                c.execute("DELETE FROM categories WHERE id=:old_cat_id", {'old_cat_id': row_cat_id})
                                conn.commit()
                                #delete_category(conn, c, old_cat_id)
                                sg.popup(f'{row_name} was moved from {old_acc} to {new_acc}')
                            else:
                                sg.popup(f'failed to move and delete category')
                    elif event == 'Update Name' and old_cat_name != 'Unallocated Cash':
                        # Change category name
                        new_cat = values['-Edit Category-']
                        c.execute("SELECT name FROM categories WHERE name=:name AND account=:account", {'name': new_cat, 'account': old_acc})
                        category_flag = c.fetchall()
                        
                        if not category_flag and new_cat and row_cat_id:
                            c.execute("""UPDATE categories SET name=:new_category
                                                        WHERE id=:id""",
                                          {'id': row_cat_id, 'new_category': new_cat})
                            conn.commit()
                            sg.popup(f'{row_name} category name was changed to {new_cat}')
                        else:
                            sg.popup(f'Could not change name for category')



        budget_win.BringToFront()
        account_menu = make_account_menu(conn, c)
        track_menu = make_account_menu(conn, c, 'track')
        budget_win['View date'].update(pretty_print_date(view_date, all_months))
        budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c, unallocated_cash_info))
        track_sheet = make_track_sheet(conn, c, view_date, all_months)
        #budget_win['-Month-'].update(values=update_month_combo(all_months, view_date))

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
