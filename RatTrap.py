import FreeSimpleGUI as sg
from logic.make_db import create_db_tables, delete_savings_db, delete_assets_db, delete_loans_db
from storage.db import initialize_db
from models.ui_controller import budget_window, transaction_window, savings_window, loan_asset_window, visual_window
from events.menu import menu as menu_event
from events.budget import edit_budget as edit_budget_event
from events.transactions import transaction as transaction_event
import events.pov as pov_event
from events.investments import savings as savings_event
from events.investments import loan_asset as loan_asset_event
from events.visual import visual as visual_event

from datetime import datetime

def main():
    year_combo = []
    for i in range(datetime.now().year - 3, datetime.now().year + 5):
        year_combo.append(str(i))
    
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Connecting to the Database
    conn, c = initialize_db('linux')
    
    create_db_tables(conn, c)
	    
    today = datetime.now()
    view_date = today.strftime("%Y-%m")

    # Create window controllers
    budget_wc = budget_window()
    transaction_wc = transaction_window()
    savings_wc = savings_window()
    loan_asset_wc = loan_asset_window()
    visual_wc = visual_window()
    
    budget_wc.create(sg, conn, c, view_date, year_combo, all_months)

    # Event Loop
    while True:
        budget_wc.wait()
        event = budget_wc.get_event()

        if not event:
            break

        elif event in ('Add Account', 'Add Category'):
            menu_event()

        elif event in ('-Year-', '-Month-'):
            # TODO: Change pov to a model and use OOP
            view_date = pov_event.change_pov(budget_wc.get_values(), all_months, view_date)

        elif event == 'Loans\\Assets' and not loan_asset_wc.get_active_flag():
            loan_asset_event(sg, conn, c, budget_wc, loan_asset_wc)

        elif event == 'Savings' and not savings_wc.get_active_flag():
            savings_event(sg, conn, c, budget_wc, savings_wc)

        elif event == 'Transactions' and not transaction_wc.get_active_flag():
            transaction_event(sg, conn, c, budget_wc, transaction_wc)

        elif event == 'Visualize' and not visual_wc.get_active_flag():
            visual_event(sg, conn, c, budget_wc, visual_wc)

        elif event == '-Table-':
            edit_budget_event(sg, conn, c, view_date, budget_wc)

        budget_wc.update(conn, c, view_date, all_months)

    budget_wc.close()
    conn.close()


if __name__ == '__main__':
    main()
