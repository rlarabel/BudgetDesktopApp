from logic.create_items import add_new_account, add_new_category
from views.menu import create_account_win, create_savings_win, create_asset_win, create_loan_win, create_category_win

def add_account(sg, conn, c):
    event, values = create_account_win(sg).read(close=True)
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
            savings_event, savings_values = create_savings_win(sg).read(close=True)
            if savings_event == 'OK':
                data = [create_acc, account_type, savings_values['-Initial Deposit-'], 
                        savings_values['-Interest-'], savings_values['-Date-']]
            else:
                data = None
        elif values['-Asset account-']:
            account_type = 'asset'
            asset_event, asset_values = create_asset_win(sg).read(close=True)
            if asset_event == 'OK':
                data = [create_acc, account_type, asset_values['-amt-'], asset_values['-Date-']]
            else:
                data = None
        else:
            account_type = 'loan'
            loan_event, loan_values = create_loan_win(sg).read(close=True)
            if loan_event == 'OK':
                data = [create_acc, account_type, loan_values['-Loan-'], loan_values['-Interest-'], 
                        loan_values['-Start Date-'], loan_values['-End Date-']]
            else:
                data = None
        
        if not existing_acc and create_acc and data:
            if add_new_account(conn, c, data) == 1:
                sg.popup(f'Successfully created {create_acc}')
            else: 
                sg.popup(f'There is missing info needed to create the account')    
        elif existing_acc:
            sg.popup(f'There is already an existing {create_acc}')
        elif not create_acc:
            sg.popup(f'There is missing info needed to create the account')

def add_category(sg, conn, c, account_menu, ):
    event, values = create_category_win(sg, account_menu).read(close=True)
    if event == 'Save':
        create_cat = values['-New category-']
        c.execute("SELECT * FROM categories WHERE name=:name AND account=:account", 
                    {'name': create_cat, 'account':values['-Account name-']})
        existing_cat = c.fetchone()
        if not existing_cat and create_cat and values['-Account name-']:
            add_new_category(conn, c, values)
            sg.popup(f'Successfully created {create_cat}')
        elif existing_cat:
            sg.popup(f'There is already an existing {create_cat}')
        elif not create_cat or not values['-Account name-']:
            sg.popup(f'There is missing info needed to open a category')