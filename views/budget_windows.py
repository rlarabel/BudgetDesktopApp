def edit_account_win(sg, account_info, menu):
    layout = [[sg.Column([[sg.Text('Rename Or Move account', font='Any 15')],
                          [sg.Combo(values=menu, k='-Edit account-', default_value=account_info[0])],
                          [sg.Button('Update')]]),
               sg.Button('Exit')]]

    window = sg.Window('Edit/Delete Account', layout, keep_on_top=True, finalize=True)

    return window


def create_account_win(sg):
    layout = [[sg.Text('New Account Info', font='Any 15')],
              [sg.Text('Account Type:'), sg.Radio('Budget Funds', "Account Type:", default=True, k='-Budget account-'),
               sg.Radio('Track Funds', "Account Type:", default=False, k='-Track account-')],
              [sg.Input(key='-New account-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add Account', layout, keep_on_top=True, finalize=True)

    return window


def edit_category_win(sg, category_info, acc_menu, cat_menu):
    layout = [[sg.Column([[sg.Text('Edit Category Name\nor\nMove to delete', font='Any 15')],
                          [sg.Combo(values=cat_menu, k='-Edit category-',
                                    default_value=category_info[0])],
                          [sg.Button('Update')]]),
               sg.Column([[sg.Text('Move accounts', font='Any 15')],
                          [sg.Combo(values=acc_menu, k='-Edit account name-', readonly=True,
                                    default_value=category_info[2])],
                          [sg.Button('Move Accounts')]]),
               sg.Column([[sg.Text('Set a monthly budget', font='Any 15')],
                          [sg.Input(category_info[1], k='-Category budget-', size=(6, 1))],
                          [sg.Button('Set')]]),
               sg.Button('Exit')]]

    window = sg.Window('Edit/Delete Category', layout, keep_on_top=True, finalize=True)

    return window


def create_category_win(sg, menu):
    layout = [[sg.Text('New Category', font='Any 15')],
              [sg.Text('Pick the account to add to'), sg.Combo(values=menu, readonly=True, k='-Account name-')],
              [sg.Input(key='-New category-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Add Category', layout, keep_on_top=True, finalize=True)

    return window


def move_funds_win(sg, menu):
    layout = [[sg.Combo(values=menu, readonly=True, k='-Menu-'),
               sg.Combo(values=('+', '-', '*', '/', '='), readonly=True, k='-Math Ops-'),
               sg.Input(key='-Move Funds-')], [sg.Button('Update'), sg.Button('Exit')]]

    window = sg.Window('Budget Funds Transaction', layout, keep_on_top=True, finalize=True)
    return window


def edit_track_acc_win(sg, account_info, menu):
    if account_info[4]:
        year, month, day = account_info[4].split('-')
    else:
        year, month = ['-', '-']
    layout = [[sg.Column([[sg.Text('Edit this account Name', font='Any 15')],
                          [sg.Combo(values=menu, k='-Edit track-',
                                    default_value=account_info[0])],
                          [sg.Button('Update')]]),
               sg.Column([[sg.Text('Total:'), sg.Input(account_info[2], k='-Track total-', size=(6, 1))],
                          [sg.Button('Set Total')]]),
               sg.Column([[sg.Text('Goal:'), sg.Input(account_info[3], k='-Track goal-', size=(6, 1))],
                          [sg.Text('Month'), sg.Input(month, k='-Goal month-', size=(2, 1))],
                          [sg.Text('Year'), sg.Input(year, k='-Goal year-', size=(4, 1))],
                          [sg.Button('Set Goal')]]),
               sg.Column([[sg.Text('Close and receive funds', font='Any 15')],
                          [sg.Checkbox('Check this box first', default=False, k='-Close track-')],
                          [sg.Button('Close Account')]]),
               sg.Button('Exit')]]

    window = sg.Window('Edit/Delete Tracking Account', layout, keep_on_top=True, finalize=True)

    return window
