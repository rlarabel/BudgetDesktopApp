def create_account_win(sg):
    layout = [
        [sg.Text('New Account Info', font='Any 15')],
        [
            sg.Text('Account Type:'),
            sg.Radio('Spending', "Account Type:",
                     default=True, k='-Spending account-'),
            sg.Radio('Bills', "Account Type:",
                     default=False, k='-Bills account-'),
            sg.Radio('Savings', "Account Type:",
                     default=False, k='-Savings account-'),
            sg.Radio('Asset', "Account Type:",
                     default=False, k='-Asset account-'),
            sg.Radio('Loan', "Account Type:",
                     default=False, k='-Loan account-')
        ],
        [sg.Input(key='-New account-')],
        [
            sg.Button('Save'),
            sg.Button('Exit')
        ]
    ]

    window = sg.Window('Add Account', layout, keep_on_top=True, finalize=True)

    return window


def create_category_win(sg, menu):
    layout = [
        [sg.Text('New Category', font='Any 15')],
        [
            sg.Text('Pick the account to add to'),
            sg.Combo(values=menu, readonly=True, k='-Account name-')
        ],
        [sg.Input(key='-New category-')],
        [
            sg.Button('Save'),
            sg.Button('Exit')
        ]
    ]

    window = sg.Window('Add Category', layout, keep_on_top=True, finalize=True)

    return window


def create_savings_win(sg):
    layout = [
        [
            [sg.Text('Date')],
            [sg.Input(k='-Date-', size=(10, 1)), sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')]
        ],
        [
            sg.Text('Initial Deposit'), 
            sg.Input(key="-Initial Deposit-", size=(15, 1))
        ],
        [
            sg.Text('Interest'), 
            sg.Input(key="-Interest-", size=(10, 1))
        ],
        [
            sg.Button('OK'), 
            sg.Button('Cancel')
        ]
    ]

    window = sg.Window('Create Savings Account', layout, finalize=True)

    return window


def create_loan_win(sg):
    layout = [
        [
            [sg.Text('Start Date')],
            [
                sg.Input(k='-Start Date-', size=(10, 1)), 
                sg.CalendarButton('Choose Date', target='-Start Date-', format='%m-%d-%Y')
            ]
        ],
        [
            sg.Text('Initial Loan Amount'), 
            sg.Input(key="-Loan-", size=(15, 1))
        ],
        [
            sg.Text('Interest'), 
            sg.Input(key="-Interest-", size=(10, 1))
        ],
        [
            [sg.Text('End Date')],
            [
                sg.Input(k='-End Date-', size=(10, 1)), 
                sg.CalendarButton('Choose Date', target='-End Date-', format='%m-%d-%Y')
            ]
        ],
        [
            sg.Button('OK'), 
            sg.Button('Cancel')
        ]
    ]

    window = sg.Window('Create Loan Account', layout, finalize=True)

    return window


def create_asset_win(sg):
    layout = [
        [
            [sg.Text('Start Date')],
            [
                sg.Input(k='-Date-', size=(10, 1)), 
                sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')
            ]
        ],
        [
            sg.Text('Initial Purchase Amount'), 
            sg.Input(key="-amt-", size=(15, 1))
        ],
        [
            sg.Button('OK'), 
            sg.Button('Cancel')
        ]
    ]

    window = sg.Window('Create asset Account', layout, finalize=True)

    return window

