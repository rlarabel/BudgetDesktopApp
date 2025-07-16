import FreeSimpleGUI as sg
from logic.make_db import create_db_tables, delete_savings_db, delete_assets_db, delete_loans_db
from storage.db import initialize_db
from models.ui_controller import budget_window, transaction_window, savings_window, loan_asset_window, visual_window
from events.menu import menu as menu_event
from events.budget import edit_budget as edit_budget_event
from events.transactions import transaction as transaction_event
from models.pov import pov_controller
from events.investments import savings as savings_event
from events.investments import loan_asset as loan_asset_event
from events.visual import visual as visual_event


def main():
    # Connecting to the Database
    conn, c = initialize_db('linux')
    pov = pov_controller()
    
    create_db_tables(conn, c)

    # Create window controllers
    budget_wc = budget_window()
    transaction_wc = transaction_window()
    savings_wc = savings_window()
    loan_asset_wc = loan_asset_window()
    visual_wc = visual_window()
    
    budget_wc.create(sg, conn, c, pov)

    # Event Loop
    while True:
        budget_wc.wait()
        event = budget_wc.get_event()

        if not event:
            break

        elif event in ('Add Account', 'Add Category'):
            menu_event()

        elif event in ('-Year-', '-Month-'):
            pov.change_view_date(budget_wc.get_values())

        elif event == 'Loans\\Assets' and not loan_asset_wc.get_active_flag():
            loan_asset_event(sg, conn, c, budget_wc, loan_asset_wc)

        elif event == 'Savings' and not savings_wc.get_active_flag():
            savings_event(sg, conn, c, budget_wc, savings_wc)

        elif event == 'Transactions' and not transaction_wc.get_active_flag():
            transaction_event(sg, conn, c, budget_wc, transaction_wc)

        elif event == 'Visualize' and not visual_wc.get_active_flag():
            visual_event(sg, conn, c, budget_wc, visual_wc)

        elif event == '-Table-':
            edit_budget_event(sg, conn, c, pov, budget_wc)

        budget_wc.update(conn, c, pov)

    budget_wc.close()
    conn.close()


if __name__ == '__main__':
    main()
