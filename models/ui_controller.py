from logic.create_items import makeTotalFunds, makeGoldenRatio
from logic.sheets.budget import makeBudgetSheet, setRowColors
from logic.sheets.transactions import makeTransactionSheet, setTransactionRowColors
from logic.sheets.investments import  makeSavingsSheet, makeAssetSheet, makeLoanSheet 
from views.budget import createBudgetWin
from views.investments import createLoansAssetsWindow, createSavingsWindow
from views.transactions import createTransactionWindow
from views.visuals import createVisualWin

class WindowController:
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
    
    def getEvent(self):
        return self.event
    
    def getValues(self):
        return self.values
    
    def getSheet(self):
        return self.sheet
    
    def activate(self):
        self.active = True
    
    def getActiveFlag(self):
        return self.active
    
    def close(self):
        self.active = False
        self.window.close()


# Controller for the budget window
class BudgetWindow(WindowController):
    def __init__(self):
        super().__init__()
        self.show_archived = 'False'

    def create(self, sg, conn, c, pov):
        menu_def = [
            ['&New', ['Add Account', 'Add Category']],
            ['&Views', ['&Transactions', 'Savings', 'Loans\\Assets', 'Visualize']],
            ['Settings',['&Show Archived']]
        ]
        self.sheet, unallocated_cash_info = makeBudgetSheet(conn, c, pov, self.show_archived)
        colors = setRowColors(conn, c, unallocated_cash_info, self.show_archived)
        layout = createBudgetWin(sg, menu_def, pov, self.sheet, colors)
        self.window = sg.Window('Rat Trap - Money Tracker', layout, finalize=True, resizable=True)
        golden_ratio = makeGoldenRatio(conn, c)
        self.window['-GOLDEN RATIO-'].update(golden_ratio)
        self.window['View date'].update(pov.prettyViewDate())
    
    def update(self, conn, c, pov):
        self.window.BringToFront()
        self.window['View date'].update(pov.prettyViewDate()) 
        self.sheet, unallocated_cash_info = makeBudgetSheet(conn, c, pov, self.show_archived)
        colors = setRowColors(conn, c, unallocated_cash_info, self.show_archived)
        self.window['-Table-'].update(self.sheet, row_colors=colors)
    
    def hide(self):
        self.window.Hide()
    
    def unhide(self):
        self.window.UnHide()
    
    def getRowName(self):
        row_name = None  
        if self.values['-Table-']:
            row_int = self.values['-Table-'][0]
            row = self.sheet[row_int]
            row_name = row[1]
        return row_name

    def getCategoryId(self):
        category_id = None
        if self.values['-Table-']:
            row_int = self.values['-Table-'][0]
            row = self.sheet[row_int]
            category_id = row[0]
        return category_id

    def toggleArchive(self):
        if self.show_archived == 'False':
            self.show_archived = 'True'
        else:
            self.show_archived = 'False'
        

class TransactionWindow(WindowController):
    def __init__(self):
        self.__validate_keys = ['-Date-', '-Trans total-']
        super().__init__()
   
    def create(self, sg, conn, c):
        self.sheet = makeTransactionSheet(conn, c)
        colors = setTransactionRowColors(conn, c)
        self.window = createTransactionWindow(sg, self.sheet, colors)
        total_funds, total_funds_2 = makeTotalFunds(conn, c)
        self.window['-Funds-'].update(total_funds)
        self.window['-Funds 2-'].update(total_funds_2)
    
    def update(self, conn, c):
        self.window.BringToFront()
        self.sheet = makeTransactionSheet(conn, c)
        row_colors = setTransactionRowColors(conn, c)
        self.window['-Trans table-'].update(self.sheet, row_colors=row_colors)
        total_funds, total_funds_2 = makeTotalFunds(conn, c)
        self.window['-Funds-'].update(total_funds)
        self.window['-Funds 2-'].update(total_funds_2)
    
    def getValidateKeys(self):
        return self.__validate_keys
    
    def getTransIdFromClick(self):
        if self.values['-Trans table-']:
            row_int = self.values['-Trans table-'][0]
            trans_id = self.sheet[row_int][0]
            account = self.sheet[row_int][2]
            return trans_id, account


class SavingsWindow(WindowController):
    def __init__(self):
        super().__init__()
   
    def create(self, sg, conn, c, pov):
        self.sheet = makeSavingsSheet(conn, c, pov)
        self.window = createSavingsWindow(sg, self.sheet, pov)
        self.window['View date'].update(pov.prettyViewDate())
    
    def update(self, conn, c, pov):
        self.window.BringToFront()
        self.sheet = makeSavingsSheet(conn, c, pov)
        self.window['-Savings table-'].update(self.sheet)
        self.window['View date'].update(pov.prettyViewDate())


class LoanAssetWindow(WindowController):
    def __init__(self):
        self.loan_sheet = None
        self.asset_sheet = None
        super().__init__()
   
    def create(self, sg, conn, c):
        self.loan_sheet = makeLoanSheet(conn, c)
        self.asset_sheet = makeAssetSheet(conn, c)
        self.window = createLoansAssetsWindow(sg, self.loan_sheet, self.asset_sheet)
        # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
    
    def update(self, conn, c):
        self.window.BringToFront()
        self.loan_sheet = makeLoanSheet(conn, c)
        self.asset_sheet = makeAssetSheet(conn, c)
        self.window['-Loans table-'].update(self.loan_sheet)
        self.window['-Assets table-'].update(self.asset_sheet)
        # loan_asset_win['View date'].update(pretty_print_date(view_date, all_months))
    def getLoanSheet(self):
        return self.loan_sheet
    
    def getAssetSheet(self):
        return self.asset_sheet
    
class VisualWindow(WindowController):
    def __init__(self):
        super().__init__()
    def create(self, sg):
        self.window = createVisualWin(sg)
    def update(self):
        self.window.BringToFront()