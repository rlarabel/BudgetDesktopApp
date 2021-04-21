import PySimpleGUI as sg
from windows import create_new_account_window, create_new_category_window
from models import update_account_funds, update_category_funds
import sqlite3


def main():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()

    c.execute("SELECT * FROM category")
    category_menu = []
    for temp in c.fetchall():
        category_menu.append(temp[1])

    if not category_menu:
        category_menu = 'None'
    # Layout definition
    layout = [[sg.Text('Budgeting App')],
              [sg.Button('Add/Delete Account'), sg.Button('Add/Delete Category'), sg.Text('Total Budget:'),
               sg.Text(size=(15, 1), key='-Funds-')],
              [sg.OptionMenu(values=category_menu, k='-Category menu-'),
               sg.OptionMenu(values=('+', '-', '*', '/', '='), k='-Math Ops-'),
               sg.Input(key='-Move Funds-'), sg.Button('Move Funds')]]
    # Creates Accounts to track in the layout
    c.execute("SELECT * FROM account")
    layout_accounts = c.fetchall()
    layout_accounts.pop(0)
    for account in layout_accounts:
        layout.append([sg.Text(account[1], font=('Helvetica', 20))])
        c.execute("SELECT * FROM category WHERE trackaccount=:variable", {'variable': account[0]})
        layout_categories = c.fetchall()
        for category in layout_categories:
            layout.append([sg.Text(category[1]), sg.Text('Avg spend /month'), sg.Text('spent this month'),
                           sg.Text(size=(10, 1), key=category[0])])

    # Create window
    window = sg.Window('Rat Trap - Money Tracker', layout, finalize=True)
    # Updates the window with default Values
    c.execute("SELECT * FROM account WHERE variable='-Funds-'")
    funds = c.fetchone()

    window['-Funds-'].update(funds[2])
    c.execute("SELECT * FROM account")
    for account in c.fetchall():
        #TODO Add vaiables for my accounts updating funds should be in here as well
        c.execute("SELECT * FROM category WHERE trackaccount=:variable", {'variable': account[0]})
        for category in c.fetchall():
            window[category[0]].update(category[2])

    # Event Loop
    while True:
        event, values = window.read()
        print(event, values)

        if not event:
            break
        if event == 'Add/Delete Account':
            event, values = create_new_account_window().read(close=True)
            if event in (None, 'Exit'):
                pass
            if event == 'Save':
                c.execute("SELECT * FROM account WHERE name=:name", {'name': values['-Account-']})
                if c.fetchone():
                    pass  # TODO: Delete
                else:
                    temp = '-' + values['-Account-'] + '-'
                    new_row = {
                        'name': values['-Account-'],
                        'total': 0,
                        'variable': temp
                    }
                    c.execute("INSERT INTO account VALUES (:variable, :name, :total)", new_row)
                    conn.commit()

        if event == 'Add/Delete Category':
            event, values = create_new_category_window(c).read(close=True)
            if event in (None, 'Exit'):
                pass
            if event == 'Save':
                c.execute("SELECT * FROM category WHERE name=:name", {'name': values['-Category-']})
                existing_cat = c.fetchone()
                if existing_cat:
                    pass  # TODO: Delete
                else:
                    c.execute("SELECT * FROM account WHERE name=:name", {'name': values['-Account name-']})
                    parent_account = c.fetchone()

                    temp = '-' + values['-Category-'] + '-'
                    new_row = {
                        'name': values['-Category-'],
                        'money': 0,
                        'variable': temp,
                        'trackaccount': parent_account[0]
                    }
                    c.execute("INSERT INTO category VALUES (:variable, :name, :money, :trackaccount)", new_row)
                    conn.commit()

        if event == 'Move Funds':
            math_operator = values['-Math Ops-']
            move_funds, selected_account, selected_category = 0, 0, 0

            try:
                move_funds = float(values['-Move Funds-'])
            except ValueError:
                math_operator = ''

            with conn:
                c.execute("SELECT * FROM category WHERE name=:menu", {'menu': values['-Category menu-']})
                selected_category = list(c.fetchone())
                c.execute("SELECT * FROM account WHERE variable=:trackaccount", {'trackaccount': selected_category[3]})
                selected_account = list(c.fetchone())
                c.execute("SELECT * FROM account WHERE variable=:variable", {'variable': '-Funds-'})
                funds_acc = list(c.fetchone())

            #TODO update accounts
            if not (selected_account or selected_category):
                pass
            elif math_operator == '-':
                funds_acc[2] += move_funds
                update_account_funds(c, tuple(funds_acc))

                selected_category[2] -= move_funds
                update_category_funds(c, tuple(selected_category))
            elif math_operator == '+':
                funds_acc[2] -= move_funds
                update_account_funds(c, tuple(funds_acc))
                selected_category[2] += move_funds
                update_category_funds(c, tuple(selected_category))
            elif math_operator == '*':
                try:
                    funds_acc[2] /= move_funds
                    selected_category[2] *= move_funds
                except ZeroDivisionError:
                    pass
                else:
                    update_account_funds(c, tuple(funds_acc))
                    update_category_funds(c, tuple(selected_category))
            elif math_operator == '/':
                try:
                    selected_category[2] /= move_funds
                    funds_acc[2] *= move_funds
                except ZeroDivisionError:
                    pass
                else:
                    update_account_funds(c, tuple(funds_acc))
                    update_category_funds(c, tuple(selected_category))
            elif math_operator == '=':
                funds_acc[2] -= move_funds - selected_category[2]
                selected_category[2] = move_funds
                update_account_funds(c, tuple(funds_acc))
                update_category_funds(c, tuple(selected_category))

            if not (selected_account or selected_category):
                pass
            else:
                conn.commit()
                window[selected_category[0]].update(selected_category[2])
                window['-Funds-'].update(funds_acc[2])

    window.close()
    conn.close()


if __name__ == '__main__':
    main()
