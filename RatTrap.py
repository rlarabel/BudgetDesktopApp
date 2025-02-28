import FreeSimpleGUI as sg
from views.transaction_windows import create_transaction_window, create_new_transaction, edit_transaction_window, select_account, get_csv
from views.budget_windows import move_funds_win, edit_account_win, edit_category_win, create_account_win, create_category_win, move_funds_acc_win
from views.investment_windows import create_savings_window, edit_asset_win, edit_pw_win, create_savings_acc_win, edit_savings_win, create_loan_acc_win, create_loans_assets_window, create_asset_acc_win, edit_loan_win
from views.visual_windows import create_visual_win
from models.create_items import make_category_menu, add_new_account, add_new_category, add_transaction, make_account_menu, make_total_funds, csv_entry
from models.sheets import set_row_colors, make_transaction_sheet, make_budget_sheet, set_transaction_row_colors, make_savings_sheet, make_asset_sheet, make_loan_sheet
from models.update_items import update_category_budget, update_transaction, pretty_print_date, update_savings_acc, update_asset, update_asset_2, update_loan
from models.make_db import create_db_tables, delete_savings_db, delete_assets_db, delete_loans_db
from models.delete_items import delete_account, delete_category
from models.visualize_data import add_fig
import sqlite3
import numpy as np
import matplotlib.pyplot as plt

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
    user_path = os.environ['USERPROFILE']
    # **************************************
    
    
    # ***** Uncomment for Linux ************
    # user_path = os.path.expanduser( '~' )
    # **************************************
    app_data_path = user_path + '/AppData/Local/RatTrap'
    location_exist = os.path.exists(app_data_path)
    app_path = app_data_path + '/app.db'
    if not location_exist:
        os.makedirs(app_data_path)
    conn = sqlite3.connect(app_path)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    #delete_assets_db(conn, c) # TODO: Delete after testing
    #delete_loans_db(conn, c) # TODO: Delete after testing
    create_db_tables(conn, c)
	    
    visible_columns_transactions = [False, True, True, True, True, True, True]
    visible_columns_budget = [False, True, True, True, True, True, True]
    
    view_date = datetime.now().strftime("%Y-%m")
    
    account_menu = make_account_menu(conn, c)
    budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
    menu_def = [['&New', ['Add Account', 'Add Category']],
                ['&Views', ['&Transactions', 'Savings', 'Loans\\Assets', 'Visualize']]]

    # Layout definition
    # TODO: add a help menu
    # TODO: Add a dynamic 50/40/10 sg.Text
    budget_layout = [
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text('Account Window', justification='center', size=(67, 1), font='Any 15')],
        [sg.Text(size=(55, 1), key='View date', font='Any 11'),
         sg.Combo(values=year_combo, k='-Year-', enable_events=True, pad=((160, 1), (1, 1)), bind_return_key=True),
         sg.Combo(values=all_months, readonly=True, k='-Month-', enable_events=True)],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=False,
                  headings=['Category ID','Name', 'Budget', 'Upcoming Expenses', 'Spendings' , 'Budget left', 'Available'],
                  row_colors=set_row_colors(conn, c, unallocated_cash_info), enable_events=True, justification='left',
                  col_widths=[0, 30, 12, 13, 13, 13, 12], font='Any 11', num_rows=13, visible_column_map=visible_columns_budget)]]

    # Create windows
    #TODO: put make budget window in views.budget_window in a function called create_budget_win 
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True, resizable=True)
    transaction_win_active = False
    savings_win_active = False
    loan_asset_win_active = False
    visual_win_active = False
    
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
                    data =[create_acc, account_type]
                elif values['-Bills account-']:
                    account_type = 'bills'
                    data = [create_acc, account_type]
                elif values['-Savings account-']:
                    account_type = 'savings'
                    savings_event, savings_values = create_savings_acc_win(sg).read(close=True)
                    if savings_event == 'OK':
                        data = [create_acc, account_type, savings_values['-Initial Deposit-'], 
                                savings_values['-Interest-'], savings_values['-Date-']]
                    else:
                        data = None
                elif values['-Asset account-']:
                    account_type = 'asset'
                    asset_event, asset_values = create_asset_acc_win(sg).read(close=True)
                    if asset_event == 'OK':
                        data = [create_acc, account_type, asset_values['-amt-'], asset_values['-Date-']]
                    else:
                        data = None
                else:
                    account_type = 'loan'
                    loan_event, loan_values = create_loan_acc_win(sg).read(close=True)
                    if loan_event == 'OK':
                        data = [create_acc, account_type, loan_values['-Loan-'], loan_values['-Interest-'], 
                                loan_values['-Start Date-'], loan_values['-End Date-']]
                    else:
                        data = None
                
                if not existing_acc and create_acc and data:
                    if add_new_account(conn, c, data) == 1:
                        sg.popup(f'Successfully created {create_acc}')
                    else: 
                        sg.popup(f'There is missing info needed to create the account')    
                elif existing_acc:
                    sg.popup(f'There is already an existing {create_acc}')
                elif not create_acc:
                    sg.popup(f'There is missing info needed to create the account')

        elif event == 'Add Category':
            event, values = create_category_win(sg, account_menu).read(close=True)
            if event == 'Save':
                create_cat = values['-New category-']
                c.execute("SELECT * FROM categories WHERE name=:name AND account=:account", 
                          {'name': create_cat, 'account':values['-Account name-']})
                existing_cat = c.fetchone()
                if not existing_cat and create_cat and values['-Account name-']:
                    add_new_category(conn, c, values)
                    sg.popup(f'Successfully created {create_cat}')
                elif existing_cat:
                    sg.popup(f'There is already an existing {create_cat}')
                elif not create_cat or not values['-Account name-']:
                    sg.popup(f'There is missing info needed to open a category')
        # TODO: make a function and use datetime
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
        
        elif event == 'Loans\\Assets' and not loan_asset_win_active:
            loan_asset_win_active = True
            budget_win.Hide()
            loan_sheet = make_loan_sheet(conn, c)
            asset_sheet = make_asset_sheet(conn, c)
            loan_asset_win = create_loans_assets_window(sg, loan_sheet, asset_sheet)
            # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
            
            while loan_asset_win_active:
                event, values = loan_asset_win.Read()
                if event in ('Back To Accounts', None):
                    loan_asset_win.Close()
                    loan_asset_win_active = False
                    budget_win.UnHide()
                # TODO: Add back in for month to month tracking
                # TODO: make a function and use datetime
                # elif event in ('-Year-', '-Month-'):
                    # set_year, month_int = view_date.split('-')
                    # if values['-Month-']:
                    #     for i, month in enumerate(all_months, 1):
                    #         if values['-Month-'] == month:
                    #             if i < 10:
                    #                 month_int = '0' + str(i)
                    #             else:
                    #                 month_int = str(i)
                    # # Checks if the year given is an int and between 1800 - 2500
                    # try:
                    #     int_user_year = int(values['-Year-'])
                    # except ValueError:
                    #     int_user_year = None                
            
                    # if int_user_year and int_user_year < 2500 and int_user_year > 1800: 
                    #     set_year = values['-Year-']
                    # view_date = set_year + '-' + month_int

                elif event == '-Loans table-' and values['-Loans table-']:
                    pass
                    row_int = values['-Loans table-'][0]
                    loan_name = loan_sheet[row_int][0]
                    c.execute("SELECT * FROM loans WHERE name=:name", {"name" : loan_name})
                    _, state, interest, start_date, end_date, initial_amount, present_amt = c.fetchone() 
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                    end_date = end_date_obj.strftime('%m-%d-%Y')
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                    start_date = start_date_obj.strftime('%m-%d-%Y')
                    event, values = edit_loan_win(sg, loan_name, interest, start_date, end_date, initial_amount, present_amt).read(close=True)
                    if event == 'Save':
                        update_loan(c, conn, sg, values, loan_name, interest, start_date_obj, end_date_obj, initial_amount, present_amt)
                    elif event == 'Archive':
                        # TODO: Add an Archive
                        pass
                        
                        
                elif event == '-Assets table-' and values['-Assets table-']:
                    row_int = values['-Assets table-'][0]
                    assets_name = asset_sheet[row_int][0]
                    c.execute("SELECT * FROM assets WHERE name=:name", {"name" : assets_name})
                    data = c.fetchone()
                    event, values = edit_asset_win(sg, data[0:4]).read(close=True)
                    if event == 'Edit Present Worth 1':
                        event, values = edit_pw_win(sg, data, 0).read(close=True)
                        if event == 'Save':
                            update_asset_2(c, conn, sg, values, data, 0)
                    elif event == 'Edit Present Worth 2':
                        event, values = edit_pw_win(sg, data, 1).read(close=True)
                        if event == 'Save':
                            update_asset_2(c, conn, sg, values, data, 1)
                    elif event == 'Archive':
                        # TODO: Add an archive
                        pass
                    elif event == 'Save':
                        update_asset(c, conn, sg, values, data, assets_name)
                

                if loan_asset_win_active:
                    loan_asset_win.BringToFront()
                    loan_sheet = make_loan_sheet(conn, c)
                    asset_sheet = make_asset_sheet(conn, c)
                    loan_asset_win['-Loans table-'].update(loan_sheet)
                    loan_asset_win['-Assets table-'].update(asset_sheet)
                    # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))

        elif event == 'Savings' and not savings_win_active:
            savings_win_active = True
            budget_win.Hide()
            savings_sheet = make_savings_sheet(conn, c, view_date)
            savings_win = create_savings_window(sg, savings_sheet, year_combo, all_months)
            savings_win['View date'].update(pretty_print_date(view_date, all_months))
            # TODO: add a archive
            while savings_win_active:
                event, values = savings_win.Read()
                if event in ('Back To Accounts', None):
                    savings_win.Close()
                    savings_win_active = False
                    budget_win.UnHide()
                #TODO: make a function and use datetime
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

                elif event == '-Savings table-' and values['-Savings table-']:
                    row_int = values['-Savings table-'][0]
                    acc_name = savings_sheet[row_int][0]
                    track_date = view_date + '-01'
                    c.execute("SELECT * FROM savings WHERE name=:name", {"name" : acc_name})
                    _, state, desired_i = c.fetchone()
                    c.execute("SELECT amount FROM track_savings WHERE account=:account and date=:date", 
                              {'account': acc_name, 'date': track_date}) 
                    amount = c.fetchone()
                    if amount:
                        amount = amount[0]
                    else:
                        amount = 0
                    event, values = edit_savings_win(sg, acc_name, desired_i, amount).read(close=True)
                    if event == 'Save':
                        update_savings_acc(c, conn, sg, values, acc_name, desired_i, amount, track_date, state)
                    if event == 'Archive':
                        # TODO: Add logic for archive
                        pass
                        
                if savings_win_active:
                    savings_win.BringToFront()
                    savings_sheet = make_savings_sheet(conn, c, view_date)
                    savings_win['-Savings table-'].update(savings_sheet)
                    savings_win['View date'].update(pretty_print_date(view_date, all_months))
        elif event == 'Transactions' and not transaction_win_active:
            transaction_win_active = True
            budget_win.Hide()
            transaction_sheet = make_transaction_sheet(conn, c)
            transaction_row_colors = set_transaction_row_colors(conn, c)
            transaction_win = create_transaction_window(sg, transaction_sheet, visible_columns_transactions, transaction_row_colors)
            keys_to_validate = ['-Date-', '-Trans total-']
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
                    trans_acc_menu = make_account_menu(conn, c, ['spending', 'bills', 'savings'])
                    acc_event, acc_values = select_account(sg, trans_acc_menu).read(close=True)
                    if acc_values:
                        selected_account = acc_values['-Account menu-']
                    else:
                        selected_account = None
                    if acc_event == 'Single Entry' and selected_account:
                        category_menu = make_category_menu(conn, c, selected_account)
                    	# New Transaction Window
                        c.execute("SELECT date FROM transactions WHERE account=:account and notes<>:notes ORDER BY date DESC", {'account': selected_account, 'notes': 'TRANSFER'})
                        latest_date = c.fetchone()
                        if latest_date != None:
                            latest_date = datetime.strptime(latest_date[0], '%Y-%m-%d')
                            latest_date = latest_date.strftime('%m-%d-%Y')
                        event, values = create_new_transaction(sg, category_menu, latest_date).read(close=True)
                        if event == 'Save':
                            #TODO: validate like csv entry
                            set_transaction = True
                            for validate in keys_to_validate:
                                if not values[validate]:
                                    set_transaction = False
                            if set_transaction:
                                user_date = values['-Date-']
                                add_transaction(conn, c, values, selected_account)
                                sg.popup(f"New transaction for {user_date}")
                            else:
                                sg.popup('Missing info: unable to add the transaction')
                    elif acc_event == 'CSV Entry' and selected_account:
                        #CSV Entry Window
                        event, values = get_csv(sg).read(close=True)
                        if event == 'OK':
                            in_file = values['-IN-'] 
                            csv_entry_flag = csv_entry(conn, c, selected_account, in_file)
                            if csv_entry_flag == 1:
                                sg.popup(f'CSV Entry Complete for {selected_account}')
                            elif csv_entry_flag == -1: 
                                sg.popup('Missing date or total: unable to add the transactions')
                            elif csv_entry_flag == -2: 
                                sg.popup('Inappropriate date: unable to add the transactions')
                            elif csv_entry_flag == -3:
                                sg.popup('Missing date and/or total header(s) in csv file: unable to add the transactions')
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
                                check = update_transaction(conn, c, values, trans_id, selected_account)
                                if check == 1:
                                    sg.popup('Transaction was updated')
                                else:
                                    sg.popup(f'{check}: unable to update the transaction')
                            else:
                                sg.popup('Missing info: unable to update the transaction')
                        elif event == 'Delete':
                            c.execute("DELETE FROM transactions WHERE id=:id", {'id': trans_id})
                            conn.commit()
                            sg.popup('Transaction was delete')

                if transaction_win_active:
                    transaction_win.BringToFront()
                    transaction_sheet = make_transaction_sheet(conn, c)
                    transaction_row_colors = set_transaction_row_colors(conn, c)
                    transaction_win['-Trans table-'].update(transaction_sheet, row_colors=transaction_row_colors)
                    total_funds = make_total_funds(conn, c)
                    transaction_win[FUNDS].update(total_funds)
        elif event == 'Visualize' and not visual_win_active:
            visual_win_active = True
            budget_win.Hide()
            visual_win = create_visual_win(sg)
            
            while visual_win_active:
                
                event, values = visual_win.Read()
                if event in ('Back', None):
                    visual_win.Close()
                    visual_win_active = False
                    budget_win.UnHide()
                elif event == 'Show':
                    show_flag = 0
                    if values['-Timeframe-'] != 'Custom Time Frame':
                        show_flag = add_fig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'])
                    else:
                        # TODO: change hardcoded text dates to user inputs as date objects
                        # TODO: validate dates
                        show_flag = add_fig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'], '4-2020', '12-2024')
                    if show_flag == 1:
                        plt.subplots_adjust(left=.1, bottom=.2, right=.9, top=.9)
                        plt.show()
                    elif show_flag == -1:
                        sg.popup('Not Enough Data')

                if visual_win_active:
                    visual_win.BringToFront()
        elif event == '-Table-':
            # Getting info of the row clicked on
            row_cat_id = None
            account_row = None
            if values['-Table-']:
                row_int = values['-Table-'][0]
                row = budget_sheet[row_int]
                row_name = row[1]
                row_cat_id = row[0]
                c.execute("SELECT * FROM accounts WHERE name=:name", {'name': row_name})
                account_row = c.fetchone()
                
            # User clicked on an account row in the budget table    
            if account_row and not row_cat_id:																
            	event, values = move_funds_acc_win(sg, account_menu, row_name).read(close=True)
            	if event == 'Update':																		# Transfer money to a different account
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
                        with conn:
                            if not move_flag:
                                c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  row_name})
                                category_id_from = c.fetchone()[0]
                                c.execute("""SELECT id FROM categories WHERE name=:name AND account=:account""", {'name': 'Unallocated Cash', 'account':  account_to})
                                category_id_to = c.fetchone()[0]
                                c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                      {'id': None, 'date': datetime.now().strftime('%Y-%m-%d'), 'payee': None, 'notes': 'TRANSFER', 'total': 0-move_funds, 'account': row_name,
                                       'category_id': category_id_from})
                                c.execute("""INSERT INTO transactions VALUES (:id, :date, :payee, :notes, :total, :account, :category_id)""",
                                      {'id': None, 'date': datetime.now().strftime('%Y-%m-%d'), 'payee': None, 'notes': 'TRANSFER', 'total': move_funds, 'account': account_to,
                                       'category_id': category_id_to})
                                conn.commit()
                                sg.popup(f'Successful\n{move_funds} from {row_name} to {account_to}')
                            else:
                                sg.popup(f'Unsuccessful transfer')
            	elif event == 'Edit Account':																# Edit Account
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
                        sg.popup(f"{row_name} changed from a {account_row[1]} to {edit_values['-Edit type-']} account")
                    elif edit_values == 'Update':
                        sg.popup("Was unable to update any information")
            
            # User clicked on a category row in the budget table
            else:																							
                c.execute("SELECT * FROM categories WHERE id=:id", {'id': row_cat_id})
                category_row = c.fetchone()
                if category_row and row_name != "Unallocated Cash":
                    selected_category = category_row[1] 
                    selected_account = category_row[2]
                    event, values = move_funds_win(sg, row_name).read(close=True)
                    if event == 'Update':
                        if values['-Move Funds-']:
                            # TODO: When moving funds if spending is not covered in previous month allocate there first
                            # TODO: Also if user try to subtract more than they have warn them 
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
                                move_funds = 0

                            # TODO: Move this whole section into update_category_budget 
                            with conn:
                    	        # Checking for entry for a certain category and month, if not add one          
                                c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                                  {'category_id': row_cat_id, 'date': track_date})
                                category_transaction = c.fetchone()
                                if not category_transaction:
                                    c.execute("""INSERT INTO track_categories VALUES (:id, :date, :total, :account, :category_id)""",
                                      {'id': None, 'date': track_date, 'total': 0, 'account': selected_account, 'category_id': row_cat_id})
                                    conn.commit()
                        
                                # Selects an account and category
                                c.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND date=:date",
                                  {'category_id': row_cat_id, 'date': track_date})
                                tracking_funds = c.fetchone()
                    
                                # moves funds from 'Unallocated Cash' to desired category
                                move_flag = True 
                                if tracking_funds:
                                    tracking_funds = list(tracking_funds)
                                    tracking_funds[2] += move_funds 
                                else:
                                    move_flag = False

                                if move_flag:
                                    update_category_budget(conn, c, tracking_funds)
                                    sg.popup(f'Successful\n{selected_category} + {move_funds} ')
                                else:
                                    sg.popup(f'Unsuccessful transfer')
                                    
                    if event == 'Edit Category':
                        category_menu = make_category_menu(conn, c, selected_account, True)
                        edit_event, values = edit_category_win(sg, category_row, category_menu).read(close=True)
                        
                        if edit_event == "Update":
                        	# Move Data and Delete old Category
                            new_category = values['-Edit Category-']
                            if new_category in (None, row_name) or not row_cat_id:
                                sg.popup(f'failed to edit category')
                            elif new_category in category_menu :
                                delete_category(conn, c, new_category, selected_account, row_cat_id)
                                sg.popup(f'{row_name} was moved and deleted')
                            else: 																		
                                # Change category name
                                c.execute("""UPDATE categories SET name=:new_category WHERE id=:id""",
                                               {'id': row_cat_id, 'new_category': new_category})
                                conn.commit()
                                sg.popup(f'{row_name} category name was changed to {new_category}')

        budget_win.BringToFront()
        account_menu = make_account_menu(conn, c)
        budget_win['View date'].update(pretty_print_date(view_date, all_months))
        budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c, unallocated_cash_info))

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
