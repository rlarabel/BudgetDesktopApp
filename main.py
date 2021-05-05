import PySimpleGUI as sg
from views.transaction_windows import create_transaction_window, create_new_transaction, edit_transaction_window
from views.budget_windows import move_funds_win, edit_track_acc_win, edit_account_win, edit_category_win, create_account_win, create_category_win
from models.create_items import make_category_menu, create_funds_income, add_new_category, add_transaction, make_account_menu
from models.sheets import set_row_colors, make_track_sheet, make_transaction_sheet, make_budget_sheet
from models.update_items import update_funds, update_category_budget, update_transaction, update_account_track, pretty_print_date, update_month_combo
from models.make_db import create_db_tables
from models.delete_items import delete_account, delete_category
import sqlite3
from datetime import datetime

BUDGET = '-Budget-'
FUNDS = '-Funds-'


def main():
    conn = sqlite3.connect('app.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    create_db_tables(conn, c)
    view_date = str(datetime.now().year) + '-' + str(datetime.now().month)
    budget, funds = create_funds_income(conn, c)
    category_menu = make_category_menu(conn, c)
    account_menu = make_account_menu(conn, c)
    track_menu = make_account_menu(conn, c, 'track')
    budget_sheet = make_budget_sheet(conn, c, view_date)
    track_sheet = make_track_sheet(conn, c, view_date)
    menu_def = [['&New', ['Add Account', 'Add Category']],
                ['&Views', ['&Transactions']],
                ['&Help', ['Icon Info']]]

    year_combo = []
    for i in range(datetime.now().year, datetime.now().year + 11):
        year_combo.append(str(i))

    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_combo = []
    for i in range(datetime.now().month-1, 12):
        month_combo.append(all_months[i])

    # Layout definition
    budget_layout = [
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text('Account Window', justification='center', size=(67, 1), font='Any 15')],
        [sg.Text(size=(55, 1), key='View date', font='Any 11'),
         sg.Combo(values=year_combo, readonly=True, k='-Year-', enable_events=True, pad=((160, 1), (1, 1))),
         sg.Combo(values=month_combo, readonly=True, k='-Month-', enable_events=True)],
        [sg.Button('Budget Funds'), sg.Button('Track Funds'),
         sg.Text('Funds Available:', justification='right', s=(48, 1), font='Any 11'),
         sg.Text(size=(13, 1), key=BUDGET, font='Any 11')],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=False,
                  headings=['Name', 'Budget Goal', "Monthly Budget", 'Budget Progress', 'Monthly spending',
                            'Total Available'],
                  row_colors=set_row_colors(conn, c), enable_events=True,
                  col_widths=[20, 12, 13, 13, 13, 12], font='Any 11', num_rows=13)],
        [sg.Table(track_sheet, key='-Track table-', auto_size_columns=False,
                  headings=['Name', 'Monthly Funds', 'Total Funds', 'Total', 'Goal'],
                  enable_events=True, col_widths=[20, 16, 16, 16, 15], font='Any 11', num_rows=8)]]

    # Create windows
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True, resizable=True, icon='images/rat.ico')
    transaction_win_active = False
    
    # Updates the window with default Values
    budget_win[BUDGET].update(budget)
    budget_win['View date'].update(pretty_print_date(view_date, all_months))

    # Event Loop
    while True:
        event, values = budget_win.read()
        print(event, values)

        if not event:
            break
        if event == 'Add Account':
            budget_win.disable()
            event, values = create_account_win(sg).read(close=True)
            if event == 'Save':
                create_acc = values['-New account-']
                c.execute("SELECT * FROM account WHERE name=:name", {'name': create_acc})
                existing_acc = c.fetchone()
                if values['-Budget account-']:
                    account_type = 'budget'
                else:
                    account_type = 'track'
                if not existing_acc and create_acc:
                    new_row = {
                        'name': create_acc,
                        'type': account_type,
                        'total': 0,
                        'goal': 0
                    }
                    c.execute("INSERT INTO account VALUES (:name, :type, :total, :goal)", new_row)
                    conn.commit()
                    sg.popup(f'Successfully created {create_acc}')
                elif existing_acc:
                    sg.popup(f'There is already an existing {create_acc}')
                elif not create_acc:
                    sg.popup(f'There is missing info needed to create the account')

        elif event == 'Add Category':
            budget_win.disable()
            event, values = create_category_win(sg, account_menu).read(close=True)
            if event == 'Save':
                create_cat = values['-New category-']
                c.execute("SELECT * FROM category WHERE name=:name", {'name': create_cat})
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
                        month_int = str(i)
            if values['-Year-']:
                set_year = str(values['-Year-'])
            view_date = set_year + '-' + month_int

        elif event == 'Transactions' and not transaction_win_active:
            transaction_win_active = True
            budget_win.Hide()
            transaction_sheet = make_transaction_sheet(conn, c)
            transaction_win = create_transaction_window(sg, transaction_sheet)
            transaction_win[FUNDS].update(funds)
            keys_to_validate = ['-Year-', '-Month-', '-Day-', '-Trans total-']

            while transaction_win_active:
                event, values = transaction_win.Read()
                if not event:
                    exit()
                if event == 'Back To Accounts':
                    transaction_win.Close()
                    transaction_win_active = False
                    budget_win.UnHide()
                elif event == 'New Transaction':
                    transaction_win.disable()
                    event, values = create_new_transaction(sg, category_menu).read(close=True)
                    if event == 'Save':
                        set_transaction = True
                        for validate in keys_to_validate:
                            if not values[validate] or not (values['-Trans menu-'] or values['-Income-']):
                                set_transaction = False
                        if set_transaction:
                            year = values['-Year-']
                            month = values['-Month-']
                            day = values['-Day-']
                            add_transaction(conn, c, values)
                            sg.popup(f"New transaction for {year}-{month}-{day}")
                        else:
                            sg.popup('Missing info: unable to update the transaction')
                elif event == '-Trans table-':
                    row_int = values['-Trans table-'][0]
                    trans_id = transaction_sheet[row_int][0]
                    c.execute("SELECT * FROM money_flow WHERE id=:id", {'id': trans_id})
                    transaction_row = c.fetchone()
                    if transaction_row:
                        transaction_win.disable()
                        event, values = edit_transaction_window(sg, transaction_row, category_menu).read(close=True)
                        if event == 'Save':
                            set_transaction = True

                            for validate in keys_to_validate:
                                if not values[validate] or not (values['-Trans menu-'] or values['-Income-']):
                                    set_transaction = False

                            if set_transaction:                               # This is where the transaction is updated
                                update_transaction(conn, c, values, trans_id)
                                sg.popup('Transaction was updated')
                            else:
                                sg.popup('Missing info: unable to update the transaction')
                        elif event == 'Delete':
                            c.execute("DELETE FROM money_flow WHERE id=:id", {'id': trans_id})
                            conn.commit()
                            sg.popup('Transaction was delete')

                if transaction_win_active:
                    transaction_win.enable()
                    transaction_win.BringToFront()
                    budget, funds = update_funds(conn, c)
                    transaction_win[FUNDS].update(funds)
                    transaction_sheet = make_transaction_sheet(conn, c)
                    transaction_win['-Trans table-'].update(transaction_sheet)

        elif event == 'Budget Funds':
            budget_win.disable()
            event, values = move_funds_win(sg, category_menu).read(close=True)
            if event == 'Update':
                if values['-Menu-'] not in (None, 'No Categories Yet') and values['-Move Funds-']:
                    math_operator = values['-Math Ops-']
                    category_name = values['-Menu-']
                    move_funds, selected_account = 0, 0

                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        math_operator = ''

                    with conn:
                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': category_name, 'date': view_date})
                        category_transaction = c.fetchone()
                        if not category_transaction:
                            c.execute("SELECT * FROM category WHERE name=:name",
                                      {'name': category_name})
                            category_info = c.fetchone()
                            c.execute("""INSERT INTO track_categories VALUES (:date, :total, :account, :category)""",
                                      {'date': view_date, 'total': 0, 'account': category_info[2],
                                       'category': category_name})
                            conn.commit()
                        # Adds a new transaction to a category unless same date

                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': category_name, 'date': view_date})
                        selected_account = c.fetchone()

                    if selected_account:
                        selected_account = list(selected_account)
                        move_flag = True

                        if math_operator == '-':
                            selected_account[1] -= move_funds
                            update_category_budget(conn, c, selected_account)
                        elif math_operator == '+':
                            selected_account[1] += move_funds
                            update_category_budget(conn, c, selected_account)
                        elif math_operator == '*':
                            selected_account[1] *= move_funds
                            update_category_budget(conn, c, selected_account)
                        elif math_operator == '/':
                            try:
                                selected_account[1] /= move_funds
                            except ZeroDivisionError:
                                pass
                            else:
                                update_category_budget(conn, c, selected_account)
                        elif math_operator == '=':
                            selected_account[1] = move_funds
                            update_category_budget(conn, c, selected_account)
                        else:
                            move_flag = False

                        if move_flag:
                            sg.popup(f'Successful\n{category_name} {math_operator} {move_funds} ')
                        else:
                            sg.popup(f'Unsuccessful transfer')

        elif event == 'Track Funds':
            budget_win.disable()
            event, values = move_funds_win(sg, track_menu).read(close=True)
            if event == 'Update':
                if values['-Menu-'] not in (None, 'No Account Yet') and values['-Move Funds-']:
                    math_operator = values['-Math Ops-']
                    move_funds = 0
                    account_name = values['-Menu-']
                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        math_operator = ''

                    with conn:
                        c.execute("SELECT * FROM track_categories WHERE account=:account AND date=:date",
                                  {'account': account_name, 'date': view_date})
                        monthly_account_transaction = c.fetchone()

                        # Adds a new transaction to a category unless same date
                        if not monthly_account_transaction:
                            c.execute("""INSERT INTO track_categories VALUES (:date, :total, :account, :category)""",
                                      {'date': view_date, 'total': 0, 'account': account_name,
                                       'category': None})
                            conn.commit()

                        c.execute("""SELECT * FROM track_categories 
                                            WHERE account=:account AND date=:date""",
                                  {'account': account_name, 'date': view_date})
                        selected_account = c.fetchone()

                    if selected_account:
                        selected_account = list(selected_account)
                        move_flag = True
                        if math_operator == '-':
                            selected_account[1] -= move_funds
                            update_account_track(conn, c, selected_account)
                        elif math_operator == '+':
                            selected_account[1] += move_funds
                            update_account_track(conn, c, selected_account)
                        elif math_operator == '*':
                            selected_account[1] *= move_funds
                            update_account_track(conn, c, selected_account)
                        elif math_operator == '/':
                            try:
                                selected_account[1] /= move_funds
                            except ZeroDivisionError:
                                pass
                            else:
                                update_account_track(conn, c, selected_account)
                        elif math_operator == '=':
                            selected_account[1] = move_funds
                            update_account_track(conn, c, selected_account)
                        else:
                            move_flag = False

                        if move_flag:
                            sg.popup(f'Successful\n{account_name} {math_operator} {move_funds} ')
                        else:
                            sg.popup(f'Unsuccessful transfer')

        elif event == '-Table-':
            row_int = values['-Table-'][0]
            row = budget_sheet[row_int]
            row_name = row[0]
            c.execute("SELECT * FROM account WHERE name=:name", {'name': row_name})
            account_row = c.fetchone()
            if account_row:
                budget_win.disable()
                event, values = edit_account_win(sg, account_row, account_menu).read(close=True)
                new_acc_name = values['-Edit account-']
                if event == 'Update' and new_acc_name not in (None, row_name):
                    if new_acc_name not in account_menu or new_acc_name not in track_menu:
                        c.execute("UPDATE account SET name=:new_account WHERE name=:old_account",
                                  {'new_account': new_acc_name, 'old_account': row_name})
                        conn.commit()
                        sg.popup(f'{row_name} account name was changed to {new_acc_name}')
                    elif new_acc_name in account_menu:
                        delete_account(conn, c, new_acc_name, row_name)
                        sg.popup(f'{row_name} was delete\nfunds were moved to account {new_acc_name}')
                    elif new_acc_name in track_menu:
                        sg.popup('This name is being used as a tracking account')
            else:
                c.execute("SELECT * FROM category WHERE name=:name", {'name': row_name})
                category_row = c.fetchone()
                if category_row:
                    budget_win.disable()
                    event, values = edit_category_win(sg, category_row, account_menu, category_menu).read(close=True)
                    old_acc = category_row[2]
                    if event == 'Set':
                        new_budget = float(values['-Category budget-'])
                        if new_budget > 0:
                            c.execute("""UPDATE category SET monthly_budget=:new_budget
                                                WHERE name=:old_category AND trackaccount=:old_account""",
                                      {'new_budget': new_budget, 'old_account': old_acc, 'old_category': row_name})
                            conn.commit()
                            sg.popup(f'Budget was set to {new_budget}')
                    elif event == 'Move Accounts':
                        new_acc = values['-Edit account name-']
                        if new_acc != old_acc:
                            c.execute("""UPDATE category SET trackaccount=:new_account
                                                    WHERE name=:old_category AND trackaccount=:old_account""",
                                      {'new_account': new_acc, 'old_account': old_acc, 'old_category': row_name})
                            c.execute("""UPDATE track_categories SET account=:new_account
                                                    WHERE category=:old_category AND account=:old_account""",
                                      {'new_account': new_acc, 'old_account': old_acc, 'old_category': row_name})
                            c.execute("""UPDATE money_flow SET account=:new_account
                                                    WHERE category=:old_category AND account=:old_account""",
                                      {'new_account': new_acc, 'old_account': old_acc, 'old_category': row_name})
                            conn.commit()
                            sg.popup(f'{row_name} was moved from {old_acc} to {new_acc}')
                    elif event == 'Update':
                        new_cat = values['-Edit category-']
                        if new_cat not in (None, row_name):
                            if new_cat not in category_menu:
                                c.execute("""UPDATE category SET name=:new_category
                                                        WHERE name=:old_category AND trackaccount=:old_account""",
                                          {'old_account': old_acc, 'new_category': new_cat, 'old_category': row_name})
                                c.execute("""UPDATE track_categories SET category=:new_category
                                                        WHERE category=:old_category AND account=:old_account""",
                                          {'old_account': old_acc, 'new_category': new_cat, 'old_category': row_name})
                                c.execute("""UPDATE money_flow SET category=:new_category
                                                        WHERE category=:old_category AND account=:old_account""",
                                          {'old_account': old_acc, 'new_category': new_cat, 'old_category': row_name})
                                conn.commit()
                                sg.popup(f'{row_name} category name was changed to {new_cat}')
                            elif new_cat in category_menu:
                                delete_category(conn, c, new_cat, category_row)
                                sg.popup(f'{row_name} was delete\nfunds were moved to account {new_cat}')
        elif event == '-Track table-':
            row_int = values['-Track table-'][0]
            row = track_sheet[row_int]
            row_name = row[0]
            c.execute("SELECT * FROM account WHERE name=:name", {'name': row_name})
            account_row = c.fetchone()
            if account_row:
                budget_win.disable()
                event, values = edit_track_acc_win(sg, account_row, track_menu).read(close=True)
                if event == 'Update':
                    new_acc_name = values['-Edit track-']
                    if new_acc_name not in (None, row_name):
                        if new_acc_name not in account_menu and new_acc_name not in track_menu:
                            c.execute("UPDATE account SET name=:new_account WHERE name=:old_account",
                                      {'new_account': new_acc_name, 'old_account': row_name})
                            conn.commit()
                            sg.popup(f'Tracking account name was updated to {new_acc_name}')
                        elif new_acc_name in account_menu or new_acc_name in track_menu:
                            sg.popup(f'{new_acc_name} is being used by another account')
                        else:
                            sg.popup(f'Edit name: {new_acc_name} did not update')

                elif event == 'Set':
                    account_total = values['-Track total-']
                    account_goal = values['-Track goal-']
                    # Updates the account total
                    if float(account_total) > 0:
                        c.execute("""UPDATE account SET total=:total
                                                    WHERE name=:account""",
                                  {'total': account_total, 'account': row_name, })
                        conn.commit()
                    # Updates the account goal
                    if float(account_goal) > 0:
                        c.execute("""UPDATE account SET goal=:goal
                                                    WHERE name=:account""",
                                  {'goal': account_goal, 'account': row_name, })
                        conn.commit()

                    sg.popup(f'{row_name} updated the goals/total')
                elif event == 'Close Account':
                    if values['-Close track-']:
                        c.execute("""SELECT * FROM track_categories WHERE account=:account""",
                                  {'account': row_name})
                        past_acc_tracks = c.fetchall()

                        user_total = 0
                        for record in past_acc_tracks:
                            user_total += record[1]

                        return_total = account_row[2] - user_total

                        new_transaction = {
                            '-Year-': datetime.now().year,
                            '-Month-': datetime.now().month,
                            '-Day-': datetime.now().day,
                            '-Trans total-': return_total,
                            '-Income-': True,
                            '-Outcome-': False,
                            '-Payee-': row_name,
                            '-Notes-': 'Money received from closing the account'
                        }
                        c.execute("""DELETE FROM track_categories WHERE account=:account""",
                                  {'account': row_name})
                        conn.commit()
                        c.execute("""DELETE FROM account WHERE name=:account""",
                                  {'account': row_name})
                        conn.commit()
                        if return_total != 0:
                            add_transaction(conn, c, new_transaction)
                        sg.popup(f'{row_name} account has been closed\ncheck transaction table for the account closure')
        elif event == 'Icon Info':
            sg.popup("""Icon made by freepik from www.flaticon.com\n
                        Author URL: https://www.flaticon.com/authors/freepik""")

        budget_win.enable()
        budget_win.BringToFront()
        category_menu = make_category_menu(conn, c)
        account_menu = make_account_menu(conn, c)
        track_menu = make_account_menu(conn, c, 'track')
        budget_win['View date'].update(pretty_print_date(view_date, all_months))
        budget, funds = update_funds(conn, c)
        budget_sheet = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))
        track_sheet = make_track_sheet(conn, c, view_date)
        budget_win['-Track table-'].update(track_sheet)
        budget_win['-Month-'].update(values=update_month_combo(all_months, view_date))
        budget_win[BUDGET].update(budget)

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
