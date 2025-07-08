from datetime import datetime

from logic.create_items import add_transaction, csv_entry, make_account_menu, make_category_menu
from logic.update_items import update_transaction
from views.transactions import create_new_transaction, edit_transaction_window, get_csv, select_account

def new_transaction(sg, conn, c, keys_to_validate):
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


def edit_transaction(sg, conn, c, values, transaction_sheet, keys_to_validate):
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