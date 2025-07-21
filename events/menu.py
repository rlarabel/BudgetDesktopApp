from logic.create_items import addNewAccount, addNewCategory
from views.menu import createAccountWin, createSavingsWin, createAssetWin, createLoanWin, createCategoryWin


def menu(sg, conn, c, event, account_menu):
    if event == 'Add Account':
        add_account(sg, conn, c)
    elif event == 'Add Category':
        add_category(sg, conn, c, account_menu)


def add_account(sg, conn, c):
    event, values = createAccountWin(sg).read(close=True)
    if event == 'Save':
        create_acc = values['-New account-']
        c.execute("SELECT * FROM accounts WHERE name=:name", {'name': create_acc})
        existing_acc = c.fetchone()
        if values['-Spending account-']:
            account_type = 'spending'
            data =[create_acc, account_type]
        elif values['-Bills account-']:
            account_type = 'bills'
            data = [create_acc, account_type]
        elif values['-Savings account-']:
            account_type = 'savings'
            savings_event, savings_values = createSavingsWin(sg).read(close=True)
            if savings_event == 'OK':
                data = [create_acc, account_type, savings_values['-Initial Deposit-'], 
                        savings_values['-Interest-'], savings_values['-Date-']]
            else:
                data = None
        elif values['-Asset account-']:
            account_type = 'asset'
            asset_event, asset_values = createAssetWin(sg).read(close=True)
            if asset_event == 'OK':
                data = [create_acc, account_type, asset_values['-amt-'], asset_values['-Date-']]
            else:
                data = None
        else:
            account_type = 'loan'
            loan_event, loan_values = createLoanWin(sg).read(close=True)
            if loan_event == 'OK':
                data = [create_acc, account_type, loan_values['-Loan-'], loan_values['-Interest-'], 
                        loan_values['-Start Date-'], loan_values['-End Date-']]
            else:
                data = None
        
        if not existing_acc and create_acc and data:
            if addNewAccount(conn, c, data) == 1:
                sg.popup(f'Successfully created {create_acc}')
            else: 
                sg.popup(f'There is missing info needed to create the account')    
        elif existing_acc:
            sg.popup(f'There is already an existing {create_acc}')
        elif not create_acc:
            sg.popup(f'There is missing info needed to create the account')


def add_category(sg, conn, c, account_menu, ):
    event, values = createCategoryWin(sg, account_menu).read(close=True)
    if event == 'Save':
        create_cat = values['-New category-']
        c.execute("SELECT * FROM categories WHERE name=:name AND account=:account", 
                    {'name': create_cat, 'account':values['-Account name-']})
        existing_cat = c.fetchone()
        if not existing_cat and create_cat and values['-Account name-']:
            addNewCategory(conn, c, values)
            sg.popup(f'Successfully created {create_cat}')
        elif existing_cat:
            sg.popup(f'There is already an existing {create_cat}')
        elif not create_cat or not values['-Account name-']:
            sg.popup(f'There is missing info needed to open a category')