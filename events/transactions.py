from datetime import datetime

from logic.create_items import addTransaction, csvEntry, makeAccountMenu, makeCategoryMenu
from logic.update_items import updateTransaction
from views.transactions import createNewTransaction, editTransactionWindow, getCsv, selectAccount

def transaction(sg, conn, c, budget_wc, transaction_wc):
    transaction_wc.activate()
    budget_wc.hide()
    transaction_wc.create(sg, conn, c)

    while transaction_wc.getActiveFlag():
        transaction_wc.wait()
        event = transaction_wc.getEvent()
        if event in ('Back To Accounts', None):
            transaction_wc.close()
            budget_wc.unhide()
        elif event == 'New Transaction':
            new_transaction(sg, conn, c, transaction_wc.getValidateKeys())
        elif event == '-Trans table-':
            edit_transaction(sg, conn, c, transaction_wc)

        if transaction_wc.getActiveFlag():
            transaction_wc.update(conn, c)

def new_transaction(sg, conn, c, keys_to_validate):
    # Gets desired account info before the next window
    trans_acc_menu = makeAccountMenu(conn, c, ['spending', 'bills', 'savings'])
    acc_event, acc_values = selectAccount(sg, trans_acc_menu).read(close=True)
    if acc_values:
        selected_account = acc_values['-Account menu-']
    else:
        selected_account = None
    if acc_event == 'Single Entry' and selected_account:
        category_menu = makeCategoryMenu(conn, c, selected_account)
        # New Transaction Window
        c.execute("SELECT date FROM transactions WHERE account=:account and notes<>:notes ORDER BY date DESC", {'account': selected_account, 'notes': 'TRANSFER'})
        latest_date = c.fetchone()
        if latest_date != None:
            latest_date = datetime.strptime(latest_date[0], '%Y-%m-%d')
            latest_date = latest_date.strftime('%m-%d-%Y')
        event, values = createNewTransaction(sg, category_menu, latest_date).read(close=True)
        if event == 'Save':
            #TODO: validate like csv entry
            set_transaction = True
            for validate in keys_to_validate:
                if not values[validate]:
                    set_transaction = False
            if set_transaction:
                user_date = values['-Date-']
                addTransaction(conn, c, values, selected_account)
                sg.popup(f"New transaction for {user_date}")
            else:
                sg.popup('Missing info: unable to add the transaction')
    elif acc_event == 'CSV Entry' and selected_account:
        #CSV Entry Window
        event, values = getCsv(sg).read(close=True)
        if event == 'OK':
            in_file = values['-IN-'] 
            csv_entry_flag = csvEntry(conn, c, selected_account, in_file)
            if csv_entry_flag == 1:
                sg.popup(f'CSV Entry Complete for {selected_account}')
            elif csv_entry_flag == -1: 
                sg.popup('Missing date or total: unable to add the transactions')
            elif csv_entry_flag == -2: 
                sg.popup('Inappropriate date: unable to add the transactions')
            elif csv_entry_flag == -3:
                sg.popup('Missing date and/or total header(s) in csv file: unable to add the transactions')


def edit_transaction(sg, conn, c, transaction_wc):
    transaction_row = None
    userClick = transaction_wc.getTransIdFromClick()
    if userClick:
        trans_id, account = userClick
    else:
        trans_id, account = None, None
    c.execute("SELECT * FROM transactions WHERE id=:id", {'id': trans_id})
    transaction_row = c.fetchone()
    if transaction_row:
        category_menu = makeCategoryMenu(conn, c, account)
        c.execute("SELECT name FROM categories WHERE id=:id", {'id': transaction_row[6]})
        
        event, values = editTransactionWindow(sg, transaction_row, c.fetchone()[0] ,category_menu).read(close=True)
        if event == 'Save':
            set_transaction = True

            for validate in transaction_wc.getValidateKeys():
                if not values[validate]:
                    set_transaction = False

            if set_transaction:      # This is where the transaction is updated
                check = updateTransaction(conn, c, values, trans_id, account)
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