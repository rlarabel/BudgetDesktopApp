import PySimpleGUI as sg
from windows import create_new_account_window, create_new_category_window, create_transaction_window, \
    create_new_transaction, edit_account_window, edit_category_window, edit_transaction_window, move_funds_window
from models import update_funds, update_category_funds, make_budget_sheet, make_category_menu, set_row_colors, \
    create_funds_income, add_new_category, add_transaction, create_db_tables, make_transaction_sheet, \
    make_account_menu, delete_account, delete_category, update_transaction
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
    budget_sheet = make_budget_sheet(conn, c, view_date)
    menu_def = [['&New', ['Add Account', 'Add Category']],
                ['&Views', ['&Transactions']]]

    year_combo = []
    for i in range(datetime.now().year - 2, datetime.now().year + 5):
        year_combo.append(str(i))
    month_combo = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Layout definition
    budget_layout = [
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text('Budgeting window')],
        [sg.Button('Budget Funds'), sg.Text('Available to Budget:'), sg.Text(size=(15, 1), key=BUDGET)],
        [sg.Combo(values=year_combo, readonly=True, k='-Year-', enable_events=True),
         sg.Combo(values=month_combo, readonly=True, k='-Month-', enable_events=True),
         sg.Text(size=(7, 1), key='View date')],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=True,
                  headings=['Name', 'Set Budget', 'This Months Budget', 'Budget Progress', 'Months spending', 'Total Available'],
                  row_colors=set_row_colors(conn, c), enable_events=True)]]

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
                if not existing_acc and values['-New account-']:
                    new_row = {
                        'name': values['-New account-'],
                        'total': 0
                    }
                    c.execute("INSERT INTO account VALUES (:name, :total)", new_row)
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
                    transaction_row = c.fetchone()
                    if transaction_row:
                        event, values = edit_transaction_window(sg, transaction_row, category_menu).read(close=True)
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
                if values['-Category menu-'] not in (None, 'No categories yet') and values['-Move Funds-']:
                    math_operator = values['-Math Ops-']
                    move_funds, selected_category = 0, 0

                    try:
                        move_funds = round(float(values['-Move Funds-']), 2)
                    except ValueError:
                        math_operator = ''

                    with conn:
                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': values['-Category menu-'], 'date': view_date})
                        category_transaction = c.fetchone()
                        if not category_transaction:
                            c.execute("SELECT * FROM category WHERE name=:name",
                                      {'name': values['-Category menu-']})
                            category_info = c.fetchone()
                            c.execute("""INSERT INTO track_categories VALUES (:date, :total, :account, :category)""",
                                      {'date': view_date, 'total': 0, 'account': category_info[3],
                                       'category': category_info[0]})
                            conn.commit()
                        # Adds a new transaction to a category unless same date

                        c.execute("SELECT * FROM track_categories WHERE category=:category AND date=:date",
                                  {'category': values['-Category menu-'], 'date': view_date})
                        selected_category = c.fetchone()

                    if selected_category:
                        selected_category = list(selected_category)

                        if math_operator == '-':
                            selected_category[1] -= move_funds
                            update_category_funds(conn, c, selected_category)
                        elif math_operator == '+':
                            selected_category[1] += move_funds
                            update_category_funds(conn, c, selected_category)
                        elif math_operator == '*':
                            selected_category[1] *= move_funds
                            update_category_funds(conn, c, selected_category)
                        elif math_operator == '/':
                            try:
                                selected_category[1] /= move_funds
                            except ZeroDivisionError:
                                pass
                            else:
                                update_category_funds(conn, c, selected_category)
                        elif math_operator == '=':
                            selected_category[1] = move_funds
                            update_category_funds(conn, c, selected_category)
        elif event == '-Table-':
            row_int = values['-Table-'][0]
            row = budget_sheet[row_int]
            row_name = row[0]
            c.execute("SELECT * FROM account WHERE name=:name", {'name': row_name})
            transaction_row = c.fetchone()
            if transaction_row:
                event, values = edit_account_window(sg, transaction_row, account_menu).read(close=True)
                if event in (None, 'Exit'):
                    pass
                else:
                    if event == 'Update' and values['-Edit account-'] not in (None, row_name):
                        if values['-Edit account-'] not in account_menu:
                            c.execute("UPDATE account SET name=:new_account WHERE name=:old_account",
                                      {'new_account': values['-Edit account-'], 'old_account': row_name})
                            conn.commit()
                        elif values['-Edit account-'] in account_menu:
                            delete_account(conn, c, values['-Edit account-'], row_name)
            else:
                c.execute("SELECT * FROM category WHERE name=:name", {'name': row_name})
                category_row = c.fetchone()
                if category_row:
                    event, values = edit_category_window(sg, category_row, account_menu, category_menu).read(close=True)
                    old_acc = category_row[3]
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

        category_menu = make_category_menu(conn, c)
        account_menu = make_account_menu(conn, c)
        budget_win['View date'].update(view_date)
        budget, funds = update_funds(conn, c)
        budget_sheet = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))
        budget_win[BUDGET].update(budget)

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
