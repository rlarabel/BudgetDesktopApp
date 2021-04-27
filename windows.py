def create_transaction_window(sg, table):
    layout = [[sg.Text('Transaction window'), sg.Button('Back To Budget')],
              [sg.Button('New Transaction')],
              [sg.Table(table, key='-Trans table-',
                        headings=['Date', 'Account', 'Category', 'Payee',
                                  'Description', 'IN/OUT', 'total'])]]

    window = sg.Window('Transaction Window', layout, finalize=True)

    return window


def create_new_transaction(sg, category_menu):
    month = 4
    day = 20
    year = 2021

    layout = [[sg.Column([[sg.Text('Date')],
                          [sg.Text('Month'), sg.Spin([i for i in range(1, 12)], initial_value=month, k='-Month-')],
                          [sg.Text('Day'), sg.Spin([i for i in range(1, 31)], initial_value=day, k='-Day-')],
                          [sg.Text('Year'), sg.Spin([i for i in range(2000, 2200)], initial_value=year, k='-Year-')]]),
               sg.Column([[sg.Text('Payee')], [sg.Input(key='-Payee-', s=(20, 5))]]),
               sg.Column([[sg.Text('Notes')], [sg.Input(key='-Notes-', s=(35, 5))]]),
               sg.Column([[sg.Text('IN/OUT')],
                          [sg.Radio('Income', "IN/OUT", default=True, k='-Income-'),
                           sg.Radio('Outcome', "IN/OUT", default=True, k='-Outcome-')],
                          [sg.Text('Select an an category for outcome')], [sg.OptionMenu(values=category_menu, k='-Trans menu-')]]),
               sg.Column([[sg.Text('Total')], [sg.Input(key='-Trans total-', s=(15, 5))]])],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True)

    return window


def create_new_account_window(sg):
    layout = [[sg.Text('Type the Account to Add/Delete', font='Any 15')],
              [sg.Input(key='-Account-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add/Delete Account', layout, keep_on_top=True, finalize=True)

    return window


def create_new_category_window(conn, cursor, sg):
    with conn:
        cursor.execute("SELECT * FROM account")
        menu = []
        for row in cursor.fetchall():
            menu.append(row[0])

        layout = [[sg.Text('Type the Category to Add/Delete', font='Any 15')],
                  [sg.Text('Pick the account to add to'), sg.OptionMenu(values=menu, k='-Account name-')],
                  [sg.Input(key='-Category-')],
                  [sg.Button('Save'), sg.Button('Exit')]]

        window = sg.Window('Add/Delete Category', layout, keep_on_top=True, finalize=True)

    return window
