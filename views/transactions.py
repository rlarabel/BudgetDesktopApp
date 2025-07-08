from datetime import datetime


def create_transaction_window(sg, table, transaction_row_colors):
    visible_columns = [False, True, True, True, True, True, True]
    layout = [[sg.Text('Transaction Window', justification='center', font='Any 15', size=(44, 1))],
              [sg.Text('Liquid Possessions:'), sg.Text(size=(15, 1), key='-Funds-'),
               sg.Button('New Transaction', pad=((150, 1), (1, 1)))],
              [sg.Table(table, key='-Trans table-',
                        headings=['ID', 'Date', 'Account', 'Category', 'Payee',
                                  'Description', 'total'], enable_events=True,
                        visible_column_map=visible_columns, row_colors=transaction_row_colors)],
              [sg.Button('Back To Accounts', button_color='grey')]]

    window = sg.Window('Transaction Window', layout, finalize=True)

    return window


def select_account(sg, account_menu):
    layout = [[sg.Column([[sg.Text('Select an account for the transaction')],
                          [sg.OptionMenu(values=account_menu, k='-Account menu-')]])],
              [sg.Button('Single Entry'), sg.Button('CSV Entry'), sg.Button('Exit')]]
    window = sg.Window('Select Account For Transaction', layout, keep_on_top=True, finalize=True)

    return window              


def select_category(sg, cat_menu):
    layout = [[sg.Column([[sg.Text('Select an Category for the transaction')],
                          [sg.OptionMenu(values=cat_menu, k='-Selected Category-')]])],
              [sg.Button('OK'), sg.Button('Exit')]]
    window = sg.Window('Select Category', layout, keep_on_top=True, finalize=True)

    return window   
    
def create_new_transaction(sg, category_menu, latest_date):
    layout = [[sg.Column([[sg.Text('Date')],
                          [sg.Input(k='-Date-', size=(10, 1), default_text=latest_date), sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')]]),
               sg.Column([[sg.Text('Payee')], [sg.Input(key='-Payee-', s=(20, 5))]]),
               sg.Column([[sg.Text('Notes')], [sg.Input(key='-Notes-', s=(35, 5))]]),
               sg.Column([[sg.Text('Select an an category for outcome transaction')],
                          [sg.OptionMenu(values=category_menu, k='-Selected Category-')]]),
               sg.Column([[sg.Text('Total')], [sg.Input(key='-Trans total-', s=(15, 5))]])],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add New Transaction', layout, keep_on_top=True, finalize=True)

    return window

def edit_transaction_window(sg, edit_row, category, category_menu):
    row_id, date, payee, notes, total, account, _ = edit_row
    date = datetime.strptime(date, '%Y-%m-%d')
    date = date.strftime('%m-%d-%Y')
    layout = [[sg.Column([[sg.Text('Date')],
                          [sg.Input(k='-Date-', size=(10, 1), default_text=date), sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')]]),
               sg.Column([[sg.Text('Payee')], [sg.Input(payee, k='-Payee-', s=(20, 5))]]),
               sg.Column([[sg.Text('Notes')], [sg.Input(notes, k='-Notes-', s=(35, 5))]]),
               sg.Column([[sg.Text('Select an an category for outcome transaction')],
                          [sg.Combo(values=category_menu, k='-Selected Category-', readonly=True, default_value=category)]]),
               sg.Column([[sg.Text('Total')], [sg.Input(total, key='-Trans total-', s=(15, 5))]])],
              [sg.Button('Save'), sg.Button('Delete'), sg.Button('Exit')]]

    window = sg.Window('Edit Transaction', layout, keep_on_top=True, finalize=True)

    return window


def get_csv(sg):
    layout =  [[sg.In(),sg.FileBrowse(file_types=(("CSV Files", "*.csv"), ), key='-IN-'),  sg.Button('OK'), sg.Button('Exit')]]
    window = sg.Window('Enter Transaction with CSV', layout, keep_on_top=True, finalize=True)
    return window