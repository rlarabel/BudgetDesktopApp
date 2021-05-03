from datetime import datetime


def create_transaction_window(sg, table):
    layout = [[sg.Text('Transaction window'), sg.Button('Back To Budget')],
              [sg.Button('New Transaction'), sg.Text('Gross Amount:'), sg.Text(size=(15, 1), key='-Funds-')],
              [sg.Table(table, key='-Trans table-',
                        headings=['ID', 'Date', 'Account', 'Category', 'Payee',
                                  'Description', 'IN/OUT', 'total'], enable_events=True)]]

    window = sg.Window('Transaction Window', layout, finalize=True)

    return window


def create_new_transaction(sg, category_menu):
    current_month = datetime.now().month
    current_day = datetime.now().day
    current_year = datetime.now().year

    layout = [[sg.Column([[sg.Text('Date')],
                          [sg.Text('Month'), sg.Input(current_month, k='-Month-', size=(2, 1))],
                          [sg.Text('Day'), sg.Input(current_day, k='-Day-', size=(2, 1))],
                          [sg.Text('Year'), sg.Input(current_year, k='-Year-', size=(4, 1))]]),
               sg.Column([[sg.Text('Payee')], [sg.Input(key='-Payee-', s=(20, 5))]]),
               sg.Column([[sg.Text('Notes')], [sg.Input(key='-Notes-', s=(35, 5))]]),
               sg.Column([[sg.Text('IN/OUT')],
                          [sg.Radio('Income', "IN/OUT", default=True, k='-Income-'),
                           sg.Radio('Outcome', "IN/OUT", default=True, k='-Outcome-')],
                          [sg.Text('Select an an category for outcome')],
                          [sg.OptionMenu(values=category_menu, k='-Trans menu-')]]),
               sg.Column([[sg.Text('Total')], [sg.Input(key='-Trans total-', s=(15, 5))]])],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True)

    return window


def edit_account_window(sg, account_info, menu):
    layout = [[sg.Column([[sg.Text('Rename Or Move account', font='Any 15')],
                          [sg.Combo(values=menu, k='-Edit account-', default_value=account_info[0])],
                          [sg.Button('Update')]]),
               sg.Column([[sg.Text('Account type', font='Any 15')],
                          [sg.Combo(values=['Edit'], k='-Move account-', readonly=True, default_value=['Edit'])],
                          [sg.Button('Delete')]]),
               sg.Button('Exit')]]

    window = sg.Window('Edit/Delete Account', layout, keep_on_top=True, finalize=True)

    return window


def create_new_account_window(sg):
    layout = [[sg.Text('Account Info', font='Any 15')],
              [sg.Input(key='-New account-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add Account', layout, keep_on_top=True, finalize=True)

    return window


def edit_category_window(sg, category_info, acc_menu, cat_menu):
    layout = [[sg.Column([[sg.Text('Edit Category Name or Move to delete', font='Any 15')],
                          [sg.Combo(values=cat_menu, k='-Edit category-',
                                    default_value=category_info[0])],
                          [sg.Button('Update')]]),
               sg.Column([[sg.Text('Move accounts', font='Any 15')],
                          [sg.Combo(values=acc_menu, k='-Edit account name-', readonly=True,
                                    default_value=category_info[3])],
                          [sg.Button('Move Accounts')]]),
               sg.Column([[sg.Text('Set a monthly budget', font='Any 15')],
                          [sg.Input(category_info[1], k='-Category budget-', size=(6, 1))],
                          [sg.Button('Set')]]),
               sg.Button('Exit')]]

    window = sg.Window('Edit/Delete Category', layout, keep_on_top=True, finalize=True)

    return window


def create_new_category_window(sg, menu):
    layout = [[sg.Text('New Category', font='Any 15')],
              [sg.Text('Pick the account to add to'), sg.Combo(values=menu, readonly=True, k='-Account name-')],
              [sg.Input(key='-New category-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add Category', layout, keep_on_top=True, finalize=True)

    return window


def edit_transaction_window(sg, edit_row, category_menu):
    row_id, date, payee, notes, total, flow, account, category = edit_row
    year, month, day = date.split('-')
    total = str(total)
    if flow == 'in':
        income = True
        outcome = False
    else:
        income = False
        outcome = True
    layout = [[sg.Column([[sg.Text('Date')],
                          [sg.Text('Month'), sg.Input(month, k='-Month-', s=(2, 1))],
                          [sg.Text('Day'), sg.Input(day, k='-Day-', s=(2, 1))],
                          [sg.Text('Year'), sg.Input(year, k='-Year-', s=(4, 1))]]),
               sg.Column([[sg.Text('Payee')], [sg.Input(payee, k='-Payee-', s=(20, 5))]]),
               sg.Column([[sg.Text('Notes')], [sg.Input(notes, k='-Notes-', s=(35, 5))]]),
               sg.Column([[sg.Text('IN/OUT')],
                          [sg.Radio('Income', "IN/OUT", default=income, k='-Income-'),
                           sg.Radio('Outcome', "IN/OUT", default=outcome, k='-Outcome-')],
                          [sg.Text('Select an an category for outcome')],
                          [sg.Combo(values=category_menu, k='-Trans menu-', readonly=True, default_value=category)]]),
               sg.Column([[sg.Text('Total')], [sg.Input(total, key='-Trans total-', s=(15, 5))]])],
              [sg.Button('Save'), sg.Button('Delete'), sg.Button('Exit')]]

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True)

    return window


def move_funds_window(sg, menu):
    layout = [[sg.Combo(values=menu, readonly=True, k='-Category menu-'),
               sg.Combo(values=('+', '-', '*', '/', '='), readonly=True, k='-Math Ops-'),
               sg.Input(key='-Move Funds-')], [sg.Button('Update'), sg.Button('Exit')]]

    window = sg.Window('Budget Funds Transaction', layout, keep_on_top=True, finalize=True)
    return window
