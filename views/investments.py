from datetime import datetime


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

def create_loans_assets_window(sg, loans_sheet, assets_sheet):
    layout = [
        [sg.Text('Loans', justification='center', size=(83, 1), font='Any 15')],
        [sg.Table(loans_sheet, key='-Loans table-', auto_size_columns=False,
                  headings=['Account', 'Initial amt ($)', 'Present amt ($)', 'APY (%)', 'Payoff Date', 'Monthly Pmt ($)'],
                  enable_events=True, justification='left',
                  col_widths=[10, 21, 19, 11, 13, 10, 15], font='Any 11', num_rows=8)],
        [sg.Text('Assets', justification='center', size=(45, 1), font='Any 15')],
        [sg.Table(assets_sheet, key='-Assets table-', auto_size_columns=False,
                  headings=['Name', 'Purchase amt', 'present worth 1', 'present worth 2'],
                  enable_events=True, justification='left',
                  col_widths=[12, 13, 12, 13], font='Any 11', num_rows=8)],
        [sg.Button('Back To Accounts', button_color='grey')]
    ]

    window = sg.Window('Loans & Assets Window', layout, finalize=True)

    return window

def edit_savings_win(sg, name, desired_i, real_value):
    layout = [
        [
            sg.Column([[sg.Text('Name')], [sg.Input(k='-Name-', size=(10, 1), default_text=name)]]),
            sg.Column([[sg.Text('Desired Interest')],
                       [sg.Input(k='-Interest-', size=(10, 1), default_text=desired_i)]]),
            sg.Column([[sg.Text('Real Value')], [sg.Input(real_value, k='-Real Value-', s=(20, 5))]])
        ],      
        [
            sg.Button('Save'), sg.Button('Archive'), sg.Button('Exit')
        ]
    ]

    window = sg.Window('Edit Savings Account', layout, keep_on_top=True, finalize=True)

    return window


def edit_asset_win(sg, data):
    name = data[0]
    initial_date = data[2]
    initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
    initial_date = initial_date.strftime('%m-%d-%Y')
    initial_amount = data[3]
    
    layout = [
                [
                    sg.Column([
                        [
                            sg.Text('Name')
                        ], 
                        [
                            sg.Input(name, k='-Name-', size=(10,1))
                        ]
                    ]), 
                    sg.Column([
                        [
                            sg.Text('Start Date')
                        ], 
                        [
                            sg.Input(initial_date, k='-Start Date-', size=(10, 1)), 
                            sg.CalendarButton('Choose Date', target='-Start Date-', format='%m-%d-%Y')
                        ]
                    ]), 
                    sg.Column([
                        [
                            sg.Text('Initial Amount')
                        ], 
                        [
                            sg.Input(initial_amount, k='-Initial Amount-', size=(10,1))
                        ]
                    ]), 
                    sg.Button('Edit Present Worth 1'), 
                    sg.Button('Edit Present Worth 2')
                ],
                
                [
                    sg.Button('Save'), 
                    sg.Button('Archive'), 
                    sg.Button('Exit')
                ]
            ]

    window = sg.Window('Edit Asset', layout, keep_on_top=True, finalize=True)

    return window

def edit_pw_win(sg, data, set):
    if set == 0:
        i = data[4]
        amt = data[5]
        fv = data[7]
        date = data[8]
    else:
        i = data[9]
        amt = data[10]
        fv = data[12]
        date = data[13]
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime('%m-%d-%Y')
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
        [
            sg.Button('Save'), sg.Button('Exit')
        ]
    ]

    window = sg.Window("Edit the Asset's PW", layout, keep_on_top=True, finalize=True)

    return window

def edit_loan_win(sg, name, interest, start_date, end_date, initial_amount, present_amt):
    layout = [
        [
            sg.Column([[sg.Text('Name')], [sg.Input(name, k='-Name-', size=(10,1))]]), 
            sg.Column([[sg.Text('Interest')], [sg.Input(interest, k='-Interest-', size=(10,1))]]),
            [
                [sg.Text('Initial Date')],
                [
                    sg.Input(start_date, k='-Start Date-', size=(10, 1)), 
                    sg.CalendarButton('Choose Date', target='-Start Date-', format='%m-%d-%Y')
                ]
            ],
            [
                [sg.Text('Payoff Date')],
                [
                    sg.Input(end_date, k='-End Date-', size=(10, 1)), 
                    sg.CalendarButton('Choose Date', target='-End Date-', format='%m-%d-%Y')
                ]
            ],
            sg.Column([[sg.Text('Initial Loan Amount')], [sg.Input(initial_amount, k='-Initial Amount-', size=(10,1))]]),
            sg.Column([[sg.Text('Present Loan Amount')], [sg.Input(present_amt, k='-AMT-', size=(10,1))]])
        ],      
        [
            sg.Button('Save'), sg.Button('Archive'), sg.Button('Exit')
        ]
    ]

    window = sg.Window('Edit Loan', layout, keep_on_top=True, finalize=True)

    return window