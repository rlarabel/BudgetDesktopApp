def create_savings_window(sg, savings_sheet, year_combo, all_months):
    #TODO: add a help menu
    layout = [
        [sg.Text(size=(55, 1), key='View date', font='Any 11'),
         sg.Combo(values=year_combo, k='-Year-', enable_events=True, pad=((400, 1), (1, 1)), bind_return_key=True),
         sg.Combo(values=all_months, readonly=True, k='-Month-', enable_events=True)],
        [sg.Text('Savings', justification='center', size=(83, 1), font='Any 15')],
        [sg.Table(savings_sheet, key='-Savings table-', auto_size_columns=False,
                  headings=['Account', 'Month Dep Amt ($)', 'Total Dep Amt ($)', 'Real Value ($)', 'Desired APY (%)', 'Real APY (%)', 'Interest Earned ($)', 'Total Growth (%)'],
                  enable_events=True, justification='left',
                  col_widths=[10, 15, 15, 11, 13, 10, 15, 13], font='Any 11', num_rows=8)],
        [sg.Button('Back To Accounts', button_color='grey')]
    ]

    window = sg.Window('Savings Window', layout, finalize=True)

    return window

def create_loans_assets_window(sg, loans_sheet, assets_sheet, year_combo, all_months):
    #TODO: add a help menu
    layout = [
        [sg.Text(size=(55, 1), key='View date', font='Any 11'),
         sg.Combo(values=year_combo, k='-Year-', enable_events=True, pad=((400, 1), (1, 1)), bind_return_key=True),
         sg.Combo(values=all_months, readonly=True, k='-Month-', enable_events=True)],
        [sg.Text('Loans', justification='center', size=(83, 1), font='Any 15')],
        [sg.Table(loans_sheet, key='-Loans table-', auto_size_columns=False,
                  headings=['Account', 'Monthly Pmt ($)', 'Total pmt ($)', 'Initial amt ($)', 'Present amt ($)', 'APY (%)', 'Est. Payoff Date'],
                  enable_events=True, justification='left',
                  col_widths=[10, 21, 19, 11, 13, 10, 15], font='Any 11', num_rows=8)],
        [sg.Text('Assets', justification='center', size=(45, 1), font='Any 15')],
        [sg.Table(assets_sheet, key='-Assets table-', auto_size_columns=False,
                  headings=['Name', 'Purchase amt', 'present worth 1', 'present worth 2'],
                  enable_events=True, justification='left',
                  col_widths=[12, 13, 12, 13], font='Any 11', num_rows=8)],
        [sg.Button('Back To Accounts', button_color='grey')]
    ]

    window = sg.Window('Savings Window', layout, finalize=True)

    return window

def edit_savings_win(sg, state, desired_i, real_value):
    layout = [[sg.Column([[sg.Text('Desired Interest')],
                          [sg.Input(k='-Interest-', size=(10, 1), default_text=desired_i)]]),
               sg.Column([[sg.Text('Real Value')], [sg.Input(real_value, k='-Real Value-', s=(20, 5))]]),
               sg.Column([[sg.Text('Basis')],
                          [sg.Combo(values=('ACTIVE', 'ARCHIVE'), 
                                    k='-State-', readonly=True, default_value=state)]])],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Edit Savings Account', layout, keep_on_top=True, finalize=True)

    return window

def create_savings_acc_win(sg):
    layout = [
        [
            [sg.Text('Date')],
            [sg.Input(k='-Date-', size=(10, 1)), sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')]
        ],
        [sg.Text('Initial Deposit'), sg.Input(key="-Initial Deposit-", size=(15, 1))],
        [sg.Text('Interest'), sg.Input(key="-Interest-", size=(10, 1))],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Create Savings Account', layout, finalize=True)

    return window

def create_loan_acc_win(sg):
    layout = [
        [
            [sg.Text('Start Date')],
            [sg.Input(k='-Start Date-', size=(10, 1)), sg.CalendarButton('Choose Date', target='-Start Date-', format='%m-%d-%Y')]
        ],
        [sg.Text('Initial Loan Amount'), sg.Input(key="-Loan-", size=(15, 1))],
        [sg.Text('Interest'), sg.Input(key="-Interest-", size=(10, 1))],
        [
            [sg.Text('End Date')],
            [sg.Input(k='-End Date-', size=(10, 1)), sg.CalendarButton('Choose Date', target='-End Date-', format='%m-%d-%Y')]
        ],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Create Loan Account', layout, finalize=True)

    return window

def create_asset_acc_win(sg):
    layout = [
        [
            [sg.Text('Start Date')],
            [sg.Input(k='-Date-', size=(10, 1)), sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')]
        ],
        [sg.Text('Initial Purchase Amount'), sg.Input(key="-amt-", size=(15, 1))],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Create asset Account', layout, finalize=True)

    return window

def edit_asset_win(sg, name):
    layout = [[sg.Column([[sg.Text('Name')], [sg.Input(name, k='-Name-', size=(10,1))]]), sg.Button('Edit Present Worth 1'), sg.Button('Edit Present Worth 2')],
              [sg.Button('Save'), sg.Button('Archive'), sg.Button('Exit')]]

    window = sg.Window('Edit Savings Account', layout, keep_on_top=True, finalize=True)

    return window

def edit_pw_win(sg, data, set):
    if set == 0:
        i = data[2]
        amt = data[3]
        fv = data[5]
        date = data[6]
    else:
        i = data[7]
        amt = data[8]
        fv = data[10]
        date = data[11]
    
    layout = [
        [
            sg.Column([[sg.Text('Discount Rate')], [sg.Input(i, k='-Rate-', s=(20, 5))]]),
            sg.Column([[sg.Text('Monthly Pay')], [sg.Input(amt, k='-AMT-', s=(20, 5))]]),
            sg.Column([[sg.Text('Est. Sell Price (FV)')], [sg.Input(fv, k='-FV-', s=(20, 5))]]),
            [
                [sg.Text('Est. Sell Date')],
                [
                    sg.Input(date, k='-Date-', size=(10, 1)), 
                    sg.CalendarButton('Choose Date', target='-Date-', format='%m-%d-%Y')
                ]
            ],
        ],
        [sg.Button('Save'), sg.Button('Exit')]
    ]

    window = sg.Window("Edit the Asset's PW", layout, keep_on_top=True, finalize=True)

    return window