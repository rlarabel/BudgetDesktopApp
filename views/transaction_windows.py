from datetime import datetime


ICON = 'images/rat.ico'


def create_transaction_window(sg, table):
    layout = [[sg.Text('Transaction Window', justification='center', font='Any 15', size=(44, 1))],
              [sg.Text('Gross Amount:'), sg.Text(size=(15, 1), key='-Funds-'),
               sg.Button('New Transaction', pad=((150, 1), (1, 1)))],
              [sg.Table(table, key='-Trans table-',
                        headings=['ID', 'Date', 'Account', 'Category', 'Payee',
                                  'Description', 'IN/OUT', 'total'], enable_events=True)],
              [sg.Button('Back To Accounts', button_color='grey')]]

    window = sg.Window('Transaction Window', layout, finalize=True, icon=ICON)

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

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True, icon=ICON)

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

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True, icon=ICON)

    return window
