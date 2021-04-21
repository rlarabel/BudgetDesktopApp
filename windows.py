import PySimpleGUI as sg

def create_budget_window():
    pass

def create_new_account_window():
    layout = [[sg.Text('Type the Account to Add/Delete', font='Any 15')],
              [sg.Input(key='-Account-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    return window


def create_new_category_window(c):
    c.execute("SELECT * FROM account")
    menu = []
    for row in c.fetchall():
        menu.append(row[1])

    layout = [[sg.Text('Type the Category to Add/Delete', font='Any 15')],
              [sg.Text('Pick the account to add to'), sg.OptionMenu(values=menu, k='-Account name-')],
              [sg.Input(key='-Category-')],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    return window
