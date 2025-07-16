def create_budget_win(sg, menu_def, pov, budget_sheet, colors):
    # TODO: add a help menu
    # TODO: Add a dynamic 50/40/10 sg.Text
    visible_columns = [False, True, True, True, True, True] 
    layout = [
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text('Account Window', justification='center', size=(67, 1), font='Any 15')],
        [
            sg.Text(size=(55, 1), key='View date', font='Any 11'),
            sg.Combo(values=pov.get_year_combo(), k='-Year-', enable_events=True, pad=((160, 1), (1, 1)), bind_return_key=True),
            sg.Combo(values=pov.get_all_months(), readonly=True, k='-Month-', enable_events=True)
        ],
        [
            sg.Table(
                budget_sheet, 
                key='-Table-', 
                auto_size_columns=False,      
                headings=['Category ID', 'Name', 'Pre-Set', 'Budget', 'Spent', 'Budget Left'],
                row_colors=colors, 
                enable_events=True, 
                justification='left',
                col_widths=[0, 30, 15, 15, 15, 15], 
                font='Any 11', 
                num_rows=13, 
                visible_column_map=visible_columns
            )
        ]
    ]

    return layout

def edit_account_win(sg, account_info, menu):
    type_menu = ['spending', 'bills', 'income']

    layout = [
        [
            [
                sg.Column(
                    [
                        [sg.Text('Rename Or Move Account:', font='Any 15')],
                        [sg.Combo(values=menu, k='-Edit account-',
                                  default_value=account_info[0])]
                    ]
                ),
                sg.Column(
                    [
                        [sg.Text('Change Account Type:', font='Any 15')],
                        [sg.Combo(values=type_menu, k='-Edit type-',
                                  readonly=True, default_value=account_info[1])]
                    ]
                )
            ],
            [
                sg.Button('Update'),
                sg.Button('Exit')
            ]
        ]
    ]

    window = sg.Window('Edit/Delete Account', layout,
                       keep_on_top=True, finalize=True)

    return window


def edit_category_win(sg, category_info, menu):
    layout = [
        [
            sg.Column(
                [
                    [sg.Text('Rename Or Move Category', font='Any 15')],
                    [sg.Combo(values=menu, k='-Edit Category-',
                              default_value=category_info[1])],
                    [
                        sg.Button('Update'),
                        sg.Button('Exit')
                    ]
                ]
            ),
            sg.Column(
                [
                    [sg.Text('Pre-Set Budget', font='Any 15')],
                    [sg.Input(category_info[3], key='-Pre Set-')]
                ]
            )
        ]
    ]

    window = sg.Window('Edit or Delete Category', layout,
                       keep_on_top=True, finalize=True)

    return window


def move_funds_win(sg, category):
    layout = [
        [
            sg.Text(f"Move funds from Available Cash to {category}: "),
            sg.Input(key='-Move Funds-')
        ],
        [
            sg.Button('Update'),
            sg.Button('Edit Category'),
            sg.Button('Exit')
        ]
    ]

    window = sg.Window('Budget Funds Transaction', layout,
                       keep_on_top=True, finalize=True)
    return window


def move_funds_acc_win(sg, menu, account):
    layout = [
        [
            sg.Text(f"Move funds from {account} to "),
            sg.Combo(values=menu, readonly=True, k='-To-'),
            sg.Input(key='-Move Funds-')
        ],
        [
            sg.Button('Update'),
            sg.Button('Edit Account'),
            sg.Button('Exit')
        ]
    ]

    window = sg.Window('Budget Funds Transaction', layout,
                       keep_on_top=True, finalize=True)
    return window


def edit_track_acc_win(sg, account_info, menu):
    if account_info[4]:
        year, month, _ = account_info[4].split('-')
    else:
        year, month = ['-', '-']

    layout = [
        [
            sg.Column(
                [
                    [sg.Text('Edit this account Name', font='Any 15')],
                    [sg.Combo(values=menu, k='-Edit track-',
                              default_value=account_info[0])],
                    [sg.Button('Update')]
                ]
            ),
            sg.Column(
                [
                    [
                        sg.Text('Total:'),
                        sg.Input(account_info[2],
                                 k='-Track total-', size=(6, 1))
                    ],
                    [sg.Button('Set Total')]
                ]
            ),
            sg.Column(
                [
                    [
                        sg.Text('Goal:'),
                        sg.Input(account_info[3],
                                 k='-Track goal-', size=(6, 1))
                    ],
                    [sg.Text('Month'), sg.Input(
                        month, k='-Goal month-', size=(2, 1))],
                    [sg.Text('Year'), sg.Input(
                        year, k='-Goal year-', size=(4, 1))],
                    [sg.Button('Set Goal')]
                ]
            ),
            sg.Column(
                [
                    [sg.Text('Close and receive funds', font='Any 15')],
                    [sg.Checkbox('Check this box first',
                                 default=False, k='-Close track-')],
                    [sg.Button('Close Account')]
                ]
            ),
            sg.Button('Exit')
        ]
    ]

    window = sg.Window('Edit/Delete Tracking Account',
                       layout, keep_on_top=True, finalize=True)

    return window
