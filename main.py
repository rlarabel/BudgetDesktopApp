import PySimpleGUI as sg
from windows import create_new_account_window, create_new_category_window, create_transaction_window, \
    create_new_transaction, edit_account_window, edit_category_window, edit_transaction_window, move_funds_window, \
    edit_track_account_window
from models import update_funds, update_category_budget, make_budget_sheet, make_category_menu, set_row_colors, \
    create_funds_income, add_new_category, add_transaction, create_db_tables, make_transaction_sheet, \
    make_account_menu, delete_account, delete_category, update_transaction, make_track_sheet, update_account_track
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
                ['&Views', ['&Transactions']]]

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
        [sg.Text('Budgeting window')],
        [sg.Combo(values=year_combo, readonly=True, k='-Year-', enable_events=True),
         sg.Combo(values=month_combo, readonly=True, k='-Month-', enable_events=True),
         sg.Text(size=(7, 1), key='View date')],
        [sg.Button('Budget Funds'), sg.Button('Track Funds'), sg.Text('Funds Available:'),
         sg.Text(size=(15, 1), key=BUDGET)],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=True,
                  headings=['Name', 'Set Budget', 'This Months Budget', 'Budget Progress', 'Months spending', 'Total Available'],
                  row_colors=set_row_colors(conn, c), enable_events=True)],
        [sg.Table(track_sheet, key='-Track table-', auto_size_columns=True,
                  headings=['Name', 'Monthly money allocated', 'Total allocated', 'Total', 'Goal'], enable_events=True)]]

    # Create windows
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True)
    transaction_win_active = False
    
    # Updates the window with default Values
    budget_win[BUDGET].update(budget)
    budget_win['View date'].update(view_date)

    # Event Loop
    while True:
        event, values = budget_win.read()
        print(event, values)

        if not event:
            break
        if event == 'Add Account':
            event, values = create_new_account_window(sg).read(close=True)

            if event == 'Save':
                c.execute("SELECT * FROM account WHERE name=:name", {'name': values['-New account-']})
                existing_acc = c.fetchone()
                if values['-Budget account-']:
                    account_type = 'budget'
                else:
                    account_type = 'track'
                if not existing_acc and values['-New account-']:
                    new_row = {
                        'name': values['-New account-'],
                        'type': account_type,
                        'total': 0,
                        'goal': 0
                    }
                    c.execute("INSERT INTO account VALUES (:name, :type, :total, :goal)", new_row)
                    conn.commit()
        elif event == 'Add Category':
            event, values = create_new_category_window(sg, account_menu).read(close=True)
            if event == 'Save':
                c.execute("SELECT * FROM category WHERE name=:name", {'name': values['-New category-']})
                existing_cat = c.fetchone()
                if not existing_cat and values['-New category-'] and values['-Account name-']:
                    add_new_category(conn, c, values)

        elif event in ('-Year-', '-Month-'):
            set_year, month_int = view_date.split('-')
            if values['-Month-']:
                for i, month in enumerate(month_combo, 1):
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

            while transaction_win_active:
                event, values = transaction_win.Read()
                if not event:
                    exit()
                if event == 'Back To Budget':
                    transaction_win.Close()
                    transaction_win_active = False
                    budget_win.UnHide()
                elif event == 'New Transaction':
                    event, values = create_new_transaction(sg, category_menu).read(close=True)
                    if event in (None, 'Exit'):
                        pass
                    if event == 'Save':
                        add_transaction(conn, c, values)
                elif event == '-Trans table-':
                    row_int = values['-Trans table-'][0]
                    trans_id = transaction_sheet[row_int][0]
                    c.execute("SELECT * FROM money_flow WHERE id=:id", {'id': trans_id})
                    account_row = c.fetchone()
                    if account_row:
                        event, values = edit_transaction_window(sg, account_row, category_menu).read(close=True)
                        if event == 'Save':
                            update_transaction(conn, c, values, trans_id)
                        elif event == 'Delete':
                            c.execute("DELETE FROM money_flow WHERE id=:id", {'id': trans_id})
                        conn.commit()
                if event not in (None, 'Back To Budget'):
                    budget, funds = update_funds(conn, c)
                    transaction_win[FUNDS].update(funds)
                    transaction_sheet = make_transaction_sheet(conn, c)
                    transaction_win['-Trans table-'].update(transaction_sheet)

        elif event == 'Budget Funds':
            event, values = move_funds_window(sg, category_menu).read(close=True)
            if event in (None, 'Exit'):
                pass
            if event == 'Update':
                if values['-Menu-'] not in (None, 'No Categories Yet') and values['-Move Funds-']:
                    math_operator = values['-Math Ops-']
                    move_funds, selected_account = 0, 0

                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        math_operator = ''

                    with conn:
                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': values['-Menu-'], 'date': view_date})
                        category_transaction = c.fetchone()
                        if not category_transaction:
                            c.execute("SELECT * FROM category WHERE name=:name",
                                      {'name': values['-Menu-']})
                            category_info = c.fetchone()
                            c.execute("""INSERT INTO track_categories VALUES (:date, :total, :account, :category)""",
                                      {'date': view_date, 'total': 0, 'account': category_info[2],
                                       'category': category_info[0]})
                            conn.commit()
                        # Adds a new transaction to a category unless same date

                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': values['-Menu-'], 'date': view_date})
                        selected_account = c.fetchone()

                    if selected_account:
                        selected_account = list(selected_account)

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
        elif event == 'Track Funds':
            event, values = move_funds_window(sg, track_menu).read(close=True)
            if event in (None, 'Exit'):
                pass
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
        elif event == '-Table-':
            row_int = values['-Table-'][0]
            row = budget_sheet[row_int]
            row_name = row[0]
            c.execute("SELECT * FROM account WHERE name=:name", {'name': row_name})
            account_row = c.fetchone()
            if account_row:
                event, values = edit_account_window(sg, account_row, account_menu).read(close=True)
                if event in (None, 'Exit'):
                    pass
                else:
                    new_acc_name = values['-Edit account-']
                    if event == 'Update' and new_acc_name not in (None, row_name):
                        if new_acc_name not in account_menu or new_acc_name not in track_menu:
                            c.execute("UPDATE account SET name=:new_account WHERE name=:old_account",
                                      {'new_account': values['-Edit account-'], 'old_account': row_name})
                            conn.commit()
                        elif new_acc_name in account_menu:
                            delete_account(conn, c, values['-Edit account-'], row_name)
                        elif new_acc_name in track_menu:
                            sg.popup('This name is being used as a tracking account')

            else:
                c.execute("SELECT * FROM category WHERE name=:name", {'name': row_name})
                category_row = c.fetchone()
                if category_row:
                    event, values = edit_category_window(sg, category_row, account_menu, category_menu).read(close=True)
                    old_acc = category_row[2]
                    if event == 'Set':
                        new_budget = float(values['-Category budget-'])
                        if new_budget > 0:
                            c.execute("""UPDATE category SET monthly_budget=:new_budget
                                                WHERE name=:old_category AND trackaccount=:old_account""",
                                      {'new_budget': new_budget, 'old_account': old_acc, 'old_category': row_name})
                            conn.commit()
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
                            elif new_cat in category_menu:
                                delete_category(conn, c, values['-Edit category-'], category_row)
        elif event == '-Track table-':
            row_int = values['-Track table-'][0]
            row = track_sheet[row_int]
            row_name = row[0]
            c.execute("SELECT * FROM account WHERE name=:name", {'name': row_name})
            account_row = c.fetchone()
            if account_row:
                event, values = edit_track_account_window(sg, account_row, track_menu).read(close=True)
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

                    sg.popup(f'{row_name} updated')
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
                        add_transaction(conn, c, new_transaction)
                        sg.popup(f'{row_name} account has been closed')
        category_menu = make_category_menu(conn, c)
        account_menu = make_account_menu(conn, c)
        track_menu = make_account_menu(conn, c, 'track')
        budget_win['View date'].update(view_date)
        budget, funds = update_funds(conn, c)
        budget_sheet = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))
        track_sheet = make_track_sheet(conn, c, view_date)
        budget_win['-Track table-'].update(track_sheet)
        budget_win[BUDGET].update(budget)

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
