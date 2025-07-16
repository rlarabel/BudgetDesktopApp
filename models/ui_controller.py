from logic.create_items import make_total_funds
from logic.sheets import make_asset_sheet, make_budget_sheet, make_loan_sheet, make_savings_sheet, make_transaction_sheet, set_row_colors, set_transaction_row_colors
from views.budget import create_budget_win
from views.investments import create_loans_assets_window, create_savings_window
from views.transactions import create_transaction_window
from views.visuals import create_visual_win

class window_controller:
    def __init__(self):
        self.sheet = None
        self.window = None
        self.values = None
        self.event = None
        self.active = False

    def wait(self):
        self.event, self.values = self.window.read()
    
    def get(self):
        return self.window    
    
    def get_event(self):
        return self.event
    
    def get_values(self):
        return self.values
    
    def get_sheet(self):
        return self.sheet
    
    def activate(self):
        self.active = True
    
    def get_active_flag(self):
        return self.active
    
    def close(self):
        self.active = False
        self.window.close()


# Controller for the budget window
class budget_window(window_controller):
    def __init__(self):
        super().__init__()

    def create(self, sg, conn, c, pov):
        menu_def = [
            ['&New', ['Add Account', 'Add Category']],
            ['&Views', ['&Transactions', 'Savings', 'Loans\\Assets', 'Visualize']]
        ]
        self.sheet, unallocated_cash_info = make_budget_sheet(conn, c, pov)
        colors = set_row_colors(conn, c, unallocated_cash_info)
        layout = create_budget_win(sg, menu_def, pov, self.sheet, colors)
        self.window = sg.Window('Rat Trap - Money Tracker', layout, finalize=True, resizable=True)
        self.window['View date'].update(pov.pretty_view_date())
    
    def update(self, conn, c, pov):
        self.window.BringToFront()
        self.window['View date'].update(pov.pretty_view_date()) 
        self.sheet, unallocated_cash_info = make_budget_sheet(conn, c, pov)
        colors = set_row_colors(conn, c, unallocated_cash_info)
        self.window['-Table-'].update(self.sheet, row_colors=colors)
    
    def hide(self):
        self.window.Hide()
    
    def unhide(self):
        self.window.UnHide()
    
    def get_row_name(self):
        row_name = None  
        if self.values['-Table-']:
            row_int = self.values['-Table-'][0]
            row = self.sheet[row_int]
            row_name = row[1]
        return row_name

    def get_category_id(self):
        category_id = None
        if self.values['-Table-']:
            row_int = self.values['-Table-'][0]
            row = self.sheet[row_int]
            category_id = row[0]
        return category_id
        

class transaction_window(window_controller):
    def __init__(self):
        self.__validate_keys = ['-Date-', '-Trans total-']
        super().__init__()
   
    def create(self, sg, conn, c):
        self.sheet = make_transaction_sheet(conn, c)
        colors = set_transaction_row_colors(conn, c)
        self.window = create_transaction_window(sg, self.sheet, colors)
        total_funds = make_total_funds(conn, c)
        self.window['-Funds-'].update(total_funds)
    
    def update(self, conn, c):
        self.window.BringToFront()
        transaction_sheet = make_transaction_sheet(conn, c)
        transaction_row_colors = set_transaction_row_colors(conn, c)
        self.window['-Trans table-'].update(transaction_sheet, row_colors=transaction_row_colors)
        total_funds = make_total_funds(conn, c)
        self.window['-Funds-'].update(total_funds)
    
    def get_validate_keys(self):
        return self.__validate_keys


class savings_window(window_controller):
    def __init__(self):
        super().__init__()
   
    def create(self, sg, conn, c, pov):
        self.sheet = make_savings_sheet(conn, c, pov)
        self.window = create_savings_window(sg, self.sheet, pov)
        self.window['View date'].update(pov.pretty_view_date())
    
    def update(self, conn, c, pov):
        self.window.BringToFront()
        savings_sheet = make_savings_sheet(conn, c, pov)
        self.window['-Savings table-'].update(savings_sheet)
        self.window['View date'].update(pov.pretty_view_date())


class loan_asset_window(window_controller):
    def __init__(self):
        self.loan_sheet = None
        self.asset_sheet = None
        super().__init__()
   
    def create(self, sg, conn, c):
        self.loan_sheet = make_loan_sheet(conn, c)
        self.asset_sheet = make_asset_sheet(conn, c)
        self.window = create_loans_assets_window(sg, self.loan_sheet, self.asset_sheet)
        # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
    
    def update(self, conn, c):
        self.window.BringToFront()
        self.loan_sheet = make_loan_sheet(conn, c)
        self.asset_sheet = make_asset_sheet(conn, c)
        self.window['-Loans table-'].update(self.loan_sheet)
        self.window['-Assets table-'].update(self.asset_sheet)
        # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
    def get_loan_sheet(self):
        return self.loan_sheet
    
    def get_asset_sheet(self):
        return self.asset_sheet
    
class visual_window(window_controller):
    def __init__(self):
        super().__init__()
    def create(self, sg):
        self.window = create_visual_win(sg)
    def update(self):
        self.window.BringToFront()