from logic.update_items import updateSavingsAcc, updateLoan, updateAsset, updateAsset2
from views.investments import editSavingsWin, editLoanWin, editAssetWin, editPresentWorthWin
from datetime import datetime


def savings(sg, conn, c, pov, budget_wc, savings_wc):
    budget_wc.hide()
    savings_wc.create(sg, conn, c, pov)
    savings_wc.activate()

    while savings_wc.getActiveFlag():
        savings_wc.wait()
        event = savings_wc.getEvent()
        values = savings_wc.getValues()

        if event in ('Back To Accounts', None):
            savings_wc.close()
            budget_wc.unhide()
        elif event in ('-Year-', '-Month-'):
            pov.change_view_date(values)
        elif event == '-Savings table-' and values['-Savings table-']:
            edit_savings(sg, conn, c, pov, values, savings_wc.getSheet()) 
        if savings_wc.getActiveFlag():
            savings_wc.update(conn, c, pov)


def edit_savings(sg, conn, c, pov, values, savings_sheet):
    row_int = values['-Savings table-'][0]
    account = savings_sheet[row_int][0]
    track_date = pov.getViewDateStr()
    c.execute("SELECT * FROM savings WHERE name=:name", {"name" : account})
    _, state, desired_i = c.fetchone()
    c.execute("SELECT amount FROM track_savings WHERE account=:account and date=:date", 
                {'account': account, 'date': track_date}) 
    amount = c.fetchone()
    if amount:
        amount = amount[0]
    else:
        amount = 0
    event, values = editSavingsWin(sg, account, desired_i, amount).read(close=True)
    if event == 'Save':
        updateSavingsAcc(c, conn, sg, values, account, desired_i, amount, track_date, state)
    if event == 'Archive':
        # TODO: Add logic for archive
        pass


def loan_asset(sg, conn, c, budget_wc, loan_asset_wc):
    budget_wc.hide()
    loan_asset_wc.create(sg, conn, c)
    loan_asset_wc.activate()

    while loan_asset_wc.getActiveFlag():
        loan_asset_wc.wait()
        event = loan_asset_wc.getEvent()
        values = loan_asset_wc.getValues()
        
        if event in ('Back To Accounts', None):
            loan_asset_wc.close()
            budget_wc.unhide()
        # TODO: Add back in for month to month tracking
        # elif event in (values, all_months, view_date):
            # view_date = pov_event()
        elif event == '-Loans table-' and values['-Loans table-']:
            edit_loan(sg, conn, c, values, loan_asset_wc.getLoanSheet())
        elif event == '-Assets table-' and values['-Assets table-']:
            edit_asset(sg, conn, c, values, loan_asset_wc.getAssetSheet())

        if loan_asset_wc.getActiveFlag():
            loan_asset_wc.update(conn, c)


def edit_loan(sg, conn, c, values, loan_sheet):
    row_int = values['-Loans table-'][0]
    loan_name = loan_sheet[row_int][0]
    c.execute("SELECT * FROM loans WHERE name=:name", {"name" : loan_name})
    _, state, interest, start_date, end_date, initial_amount, present_amt = c.fetchone() 
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date_obj.strftime('%m-%d-%Y')
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date_obj.strftime('%m-%d-%Y')
    event, values = editLoanWin(sg, loan_name, interest, start_date, end_date, initial_amount, present_amt).read(close=True)
    if event == 'Save':
        updateLoan(c, conn, sg, values, loan_name, interest, start_date_obj, end_date_obj, initial_amount, present_amt)
    elif event == 'Archive':
        # TODO: Add an Archive
        pass


def edit_asset(sg, conn, c, values, asset_sheet):
    row_int = values['-Assets table-'][0]
    assets_name = asset_sheet[row_int][0]
    c.execute("SELECT * FROM assets WHERE name=:name", {"name" : assets_name})
    data = c.fetchone()
    event, values = editAssetWin(sg, data[0:4]).read(close=True)
    if event == 'Edit Present Worth 1':
        event, values = editPresentWorthWin(sg, data, 0).read(close=True)
        if event == 'Save':
            updateAsset2(c, conn, sg, values, data, 0)
    elif event == 'Edit Present Worth 2':
        event, values = editPresentWorthWin(sg, data, 1).read(close=True)
        if event == 'Save':
            updateAsset2(c, conn, sg, values, data, 1)
    elif event == 'Archive':
        # TODO: Add an archive
        pass
    elif event == 'Save':
        updateAsset(c, conn, sg, values, data, assets_name)
