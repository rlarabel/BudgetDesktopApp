import FreeSimpleGUI as sg
from logic.make_db import createDbTables, deleteSavingsDb, deleteAssetsDb, deleteLoansDb
from storage.db import initializeDb
from models.ui_controller import BudgetWindow, TransactionWindow, SavingsWindow, LoanAssetWindow, VisualWindow
from models.pov import PovController
from events.menu import menu as menu_event
from events.budget import edit_budget as edit_budget_event
from events.transactions import transaction as transaction_event
from events.investments import savings as savings_event
from events.investments import loan_asset as loan_asset_event
from events.visual import visual as visual_event


def main():
    # Connecting to the Database
    conn, c = initializeDb('linux')
    pov = PovController()
    
    createDbTables(conn, c)

    # Create window controllers
    budget_wc = BudgetWindow()
    transaction_wc = TransactionWindow()
    savings_wc = SavingsWindow()
    loan_asset_wc = LoanAssetWindow()
    visual_wc = VisualWindow()
    
    budget_wc.create(sg, conn, c, pov)

    # Event Loop
    while True:
        budget_wc.wait()
        event = budget_wc.getEvent()

        if not event:
            break

        elif event in ('Add Account', 'Add Category'):
            menu_event()

        elif event in ('-Year-', '-Month-'):
            pov.changeViewDate(budget_wc.getValues())

        elif event == 'Loans\\Assets' and not loan_asset_wc.getActiveFlag():
            loan_asset_event(sg, conn, c, budget_wc, loan_asset_wc)

        elif event == 'Savings' and not savings_wc.getActiveFlag():
            savings_event(sg, conn, c, pov, budget_wc, savings_wc)

        elif event == 'Transactions' and not transaction_wc.getActiveFlag():
            transaction_event(sg, conn, c, budget_wc, transaction_wc)

        elif event == 'Visualize' and not visual_wc.getActiveFlag():
            visual_event(sg, conn, c, budget_wc, visual_wc)

        elif event == '-Table-':
            edit_budget_event(sg, conn, c, pov, budget_wc)

        budget_wc.update(conn, c, pov)

    budget_wc.close()
    conn.close()


if __name__ == '__main__':
    main()
