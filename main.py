import PySimpleGUI as sg
from windows import create_new_account_window, create_new_category_window, create_transaction_window, \
    create_new_transaction
from models import update_funds, update_category_funds, make_budget_sheet, make_category_menu, set_row_colors, \
    create_funds_income, add_new_category, add_transaction, create_db_tables, make_transaction_sheet
import sqlite3
from datetime import datetime

BUDGET = '-Budget-'
FUNDS = '-FUNDS-'


def main():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    create_db_tables(conn, c)
    budget, funds = create_funds_income(conn, c)
    category_menu = make_category_menu(conn, c)
    view_date = str(datetime.now().year) + '-' + str(datetime.now().month)
    budget_sheet = make_budget_sheet(conn, c, view_date)

    year_combo = []
    for i in range(datetime.now().year - 2, datetime.now().year + 5):
        year_combo.append(str(i))
    month_combo = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Layout definition
    budget_layout = [
        [sg.Text('Budgeting window'), sg.OptionMenu(values=['Transaction'], key='-Window-'), sg.Button('Go'),
         sg.Combo(values=year_combo, readonly=True, k='-Year-', enable_events=True),
         sg.Combo(values=month_combo, readonly=True, k='-Month-', enable_events=True), sg.Text(size=(7, 1), key='View date')],
        [sg.Button('Add/Delete Account'), sg.Button('Add/Delete Category'), sg.Text('Available to Budget:'),
         sg.Text(size=(15, 1), key=BUDGET), sg.Text('Gross Amount:'), sg.Text(size=(15, 1), key=FUNDS)],
        [sg.Combo(values=category_menu, readonly=True, k='-Category menu-'),
         sg.OptionMenu(values=('+', '-', '*', '/', '='), k='-Math Ops-'),
         sg.Input(key='-Move Funds-'), sg.Button('Move Funds')],
        [sg.Table(budget_sheet, key='-Table-', auto_size_columns=True,
                  headings=['Budget list', 'Avialable Budgeted this month'],
                  row_colors=set_row_colors(conn, c))]]

    # Create windows
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True)
    transaction_win_active = False
    # Updates the window with default Values
    budget_win[BUDGET].update(budget)
    budget_win[FUNDS].update(funds)
    budget_win['View date'].update(view_date)

    # Event Loop
    while True:
        event, values = budget_win.read()
        print(event, values)

        if not event:
            break
        if event == 'Add/Delete Account':
            event, values = create_new_account_window(sg).read(close=True)
            if event in (None, 'Exit'):
                pass
            if event == 'Save':
                c.execute("SELECT * FROM account WHERE name=:name", {'name': values['-Account-']})
                if not c.fetchone():
                    new_row = {
                        'name': values['-Account-'],
                        'total': 0
                    }
                    c.execute("INSERT INTO account VALUES (:name, :total)", new_row)
                    conn.commit()
                    budget_sheet = make_budget_sheet(conn, c, view_date)
                    budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))

        elif event == 'Add/Delete Category':
            event, values = create_new_category_window(conn, c, sg).read(close=True)
            if event in (None, 'Exit'):
                pass
            if event == 'Save':
                c.execute("SELECT * FROM category WHERE name=:name", {'name': values['-Category-']})
                existing_cat = c.fetchone()
                if not existing_cat:
                    add_new_category(conn, c, values)
                    budget_sheet = make_budget_sheet(conn, c, view_date)
                    budget_win['-Category menu-'].update(values=make_category_menu(conn, c))
                    budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))
        elif event in ('-Year-', '-Month-'):
            set_year, month_int = view_date.split('-')
            if values['-Month-']:
                for i, month in enumerate(month_combo, 1):
                    if values['-Month-'] == month:
                        month_int = str(i)
            if values['-Year-']:
                set_year = str(values['-Year-'])
            view_date = set_year + '-' + month_int

            budget_sheet = make_budget_sheet(conn, c, view_date)
            budget_win['-Table-'].update(budget_sheet)
            budget_win['View date'].update(view_date)
        elif event == 'Go':
            if values['-Window-'] == 'Transaction' and not transaction_win_active:
                transaction_win_active = True
                budget_win.Hide()
                transaction_win = create_transaction_window(sg, make_transaction_sheet(conn, c))

                while transaction_win_active:
                    trans_event, trans_values = transaction_win.Read()
                    if not trans_event:
                        break
                    if trans_event == 'Back To Budget':
                        transaction_win.Close()
                        transaction_win_active = False
                        budget_win.UnHide()
                    if trans_event == 'New Transaction':
                        menu = make_category_menu(conn, c)
                        add_trans_event, add_trans_values = create_new_transaction(sg, menu).read(close=True)
                        if add_trans_event in (None, 'Exit'):
                            pass
                        if add_trans_event == 'Save':
                            add_transaction(conn, c, add_trans_values)
                        transaction_sheet = make_transaction_sheet(conn, c)
                        transaction_win['-Trans table-'].update(transaction_sheet)

        elif event == 'Move Funds':
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

                    budget, funds = update_funds(conn, c)
                    budget_sheet = make_budget_sheet(conn, c, view_date)
                    budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c))
                    budget_win[FUNDS].update(funds)
                    budget_win[BUDGET].update(budget)

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
