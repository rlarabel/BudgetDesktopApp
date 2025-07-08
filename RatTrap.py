import FreeSimpleGUI as sg
from views.transactions import create_transaction_window
from views.budget import create_budget_win
from views.investments import create_savings_window, create_loans_assets_window
from logic.create_items import make_account_menu, make_total_funds
from logic.sheets import set_row_colors, make_transaction_sheet, make_budget_sheet, set_transaction_row_colors, make_savings_sheet, make_asset_sheet, make_loan_sheet
from logic.update_items import pretty_print_date
from logic.make_db import create_db_tables, delete_savings_db, delete_assets_db, delete_loans_db
from storage.db import initialize_db
import events.menu as menu_event
import events.budget as budget_event
import events.transactions as transaction_event
import events.pov as pov_event
import events.investments as investment_event
import events.visual as visual_event



from datetime import datetime


BUDGET = '-Budget-'
FUNDS = '-Funds-'


def main():
    year_combo = []
    for i in range(datetime.now().year - 3, datetime.now().year + 5):
        year_combo.append(str(i))
    
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Connecting to the Database
    conn, c = initialize_db('linux')
    
    #delete_assets_db(conn, c) # TODO: Delete after testing
    #delete_loans_db(conn, c) # TODO: Delete after testing
    create_db_tables(conn, c)
	    
    today = datetime.now()
    view_date = today.strftime("%Y-%m")
    
    # Budget Layout
    account_menu = make_account_menu(conn, c)
    budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
    colors=set_row_colors(conn, c, unallocated_cash_info)
    menu_def = [
        ['&New', ['Add Account', 'Add Category']],
        ['&Views', ['&Transactions', 'Savings', 'Loans\\Assets', 'Visualize']]
    ]

    # Create windows
    budget_layout = create_budget_win(sg, menu_def, year_combo, all_months, budget_sheet, colors)
    budget_win = sg.Window('Rat Trap - Money Tracker', budget_layout, finalize=True, resizable=True)
    
    # Initialize windows variables
    transaction_win_active = False
    savings_win_active = False
    loan_asset_win_active = False
    visual_win_active = False
    
    # Updates the window with default Values
    budget_win['View date'].update(pretty_print_date(view_date, all_months))

    # Event Loop
    while True:
        event, values = budget_win.read()

        if not event:
            break
        if event == 'Add Account':
            menu_event.add_account(sg, conn, c)
        elif event == 'Add Category':
            menu_event.add_category(sg, conn, c, account_menu)
        elif event in ('-Year-', '-Month-'):
            # TODO: Change pov to a model and use OOP
            view_date = pov_event.change_pov(values, all_months, view_date)
        
        elif event == 'Loans\\Assets' and not loan_asset_win_active:
            loan_asset_win_active = True
            budget_win.Hide()
            loan_sheet = make_loan_sheet(conn, c)
            asset_sheet = make_asset_sheet(conn, c)
            loan_asset_win = create_loans_assets_window(sg, loan_sheet, asset_sheet)
            # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
            
            while loan_asset_win_active:
                event, values = loan_asset_win.Read()
                if event in ('Back To Accounts', None):
                    loan_asset_win.Close()
                    loan_asset_win_active = False
                    budget_win.UnHide()
                # TODO: Add back in for month to month tracking
                # elif event in (values, all_months, view_date):
                    # view_date = pov_event()

                elif event == '-Loans table-' and values['-Loans table-']:
                    investment_event.edit_loan(sg, conn, c, loan_sheet)
                        
                elif event == '-Assets table-' and values['-Assets table-']:
                    investment_event.edit_asset()
                

                if loan_asset_win_active:
                    loan_asset_win.BringToFront()
                    loan_sheet = make_loan_sheet(conn, c)
                    asset_sheet = make_asset_sheet(conn, c)
                    loan_asset_win['-Loans table-'].update(loan_sheet)
                    loan_asset_win['-Assets table-'].update(asset_sheet)
                    # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))

        elif event == 'Savings' and not savings_win_active:
            savings_win_active = True
            budget_win.Hide()
            savings_sheet = make_savings_sheet(conn, c, view_date)
            savings_win = create_savings_window(sg, savings_sheet, year_combo, all_months)
            savings_win['View date'].update(pretty_print_date(view_date, all_months))
            # TODO: add a archive
            while savings_win_active:
                event, values = savings_win.Read()
                if event in ('Back To Accounts', None):
                    savings_win.Close()
                    savings_win_active = False
                    budget_win.UnHide()
                elif event in ('-Year-', '-Month-'):
                    view_date = pov_event.change_pov(values, all_months, view_date)
                elif event == '-Savings table-' and values['-Savings table-']:
                    investment_event.edit_savings(sg, conn, c, view_date, values, savings_sheet)
                        
                if savings_win_active:
                    savings_win.BringToFront()
                    savings_sheet = make_savings_sheet(conn, c, view_date)
                    savings_win['-Savings table-'].update(savings_sheet)
                    savings_win['View date'].update(pretty_print_date(view_date, all_months))
        elif event == 'Transactions' and not transaction_win_active:
            transaction_win_active = True
            budget_win.Hide()
            transaction_sheet = make_transaction_sheet(conn, c)
            transaction_row_colors = set_transaction_row_colors(conn, c)
            transaction_win = create_transaction_window(sg, transaction_sheet, transaction_row_colors)
            keys_to_validate = ['-Date-', '-Trans total-']
            total_funds = make_total_funds(conn, c)
            transaction_win[FUNDS].update(total_funds)
            
            while transaction_win_active:
                event, values = transaction_win.Read()
                if event in ('Back To Accounts', None):
                    transaction_win.Close()
                    transaction_win_active = False
                    budget_win.UnHide()
                elif event == 'New Transaction':
                    transaction_event.new_transaction(sg, conn, c, keys_to_validate)
                elif event == '-Trans table-':
                    transaction_event.edit_transaction(sg, conn, c, values, transaction_sheet, keys_to_validate)

                if transaction_win_active:
                    transaction_win.BringToFront()
                    transaction_sheet = make_transaction_sheet(conn, c)
                    transaction_row_colors = set_transaction_row_colors(conn, c)
                    transaction_win['-Trans table-'].update(transaction_sheet, row_colors=transaction_row_colors)
                    total_funds = make_total_funds(conn, c)
                    transaction_win[FUNDS].update(total_funds)
        elif event == 'Visualize' and not visual_win_active:
            visual_event.visualize(sg, conn, c, values, budget_win)
        elif event == '-Table-':
            # Getting info of the row clicked on
            row_cat_id = None
            account_row = None
            if values['-Table-']:
                row_int = values['-Table-'][0]
                row = budget_sheet[row_int]
                row_name = row[1]
                category_id = row[0]
                c.execute("SELECT * FROM accounts WHERE name=:name", {'name': row_name})
                account_row = c.fetchone()

            if account_row and not row_cat_id:
               # User clicked on an account row in the budget table 														
               budget_event.select_account(sg, conn, c, account_menu, row_name, account_row)
            
            else:
                # User clicked on a category row in the budget table																							
                budget_event.select_category(sg, conn, c, category_id)


        budget_win.BringToFront()
        account_menu = make_account_menu(conn, c)
        budget_win['View date'].update(pretty_print_date(view_date, all_months))
        budget_sheet, unallocated_cash_info = make_budget_sheet(conn, c, view_date)
        budget_win['-Table-'].update(budget_sheet, row_colors=set_row_colors(conn, c, unallocated_cash_info))

    budget_win.close()
    conn.close()


if __name__ == '__main__':
    main()
