from logic.update_items import update_savings_acc, update_loan, update_asset, update_asset_2
from views.investments import edit_savings_win, edit_loan_win, edit_asset_win, edit_pw_win
from datetime import datetime
import events.pov as pov_event


def savings(sg, conn, c, budget_wc, savings_wc, all_months, year_combo):
    budget_wc.hide()
    savings_wc.create(sg, conn, c, view_date, all_months, year_combo)
    savings_wc.activate()

    while savings_wc.get_active_flag():
        savings_wc.wait()
        event = savings_wc.get_event()
        values = savings_wc.get_values()

        if event in ('Back To Accounts', None):
            savings_wc.close()
            budget_wc.unhide()
        elif event in ('-Year-', '-Month-'):
            view_date = pov_event.change_pov(values, all_months, view_date)
        elif event == '-Savings table-' and values['-Savings table-']:
            edit_savings(sg, conn, c, view_date, values, savings_wc.get_sheet()) 
        if savings_wc.get_active_flag():
            savings_wc.update(conn, c, view_date, all_months)


def edit_savings(sg, conn, c, view_date, values, savings_sheet):
    row_int = values['-Savings table-'][0]
    account = savings_sheet[row_int][0]
    track_date = view_date + '-01'
    c.execute("SELECT * FROM savings WHERE name=:name", {"name" : account})
    _, state, desired_i = c.fetchone()
    c.execute("SELECT amount FROM track_savings WHERE account=:account and date=:date", 
                {'account': account, 'date': track_date}) 
    amount = c.fetchone()
    if amount:
        amount = amount[0]
    else:
        amount = 0
    event, values = edit_savings_win(sg, account, desired_i, amount).read(close=True)
    if event == 'Save':
        update_savings_acc(c, conn, sg, values, account, desired_i, amount, track_date, state)
    if event == 'Archive':
        # TODO: Add logic for archive
        pass


def loan_asset(sg, conn, c, budget_wc, loan_asset_wc):
    budget_wc.hide()
    loan_asset_wc.create(sg, conn, c)
    loan_asset_wc.activate()

    while loan_asset_wc.get_active_flag():
        loan_asset_wc.wait()
        event = loan_asset_wc.get_event()
        values = loan_asset_wc.get_values()
        
        if event in ('Back To Accounts', None):
            loan_asset_wc.close()
            budget_wc.unhide()
        # TODO: Add back in for month to month tracking
        # elif event in (values, all_months, view_date):
            # view_date = pov_event()
        elif event == '-Loans table-' and values['-Loans table-']:
            edit_loan(sg, conn, c, values, loan_asset_wc.get_loan_sheet())
        elif event == '-Assets table-' and values['-Assets table-']:
            edit_asset(sg, conn, c, values, loan_asset_wc.get_asset_sheet())

        if loan_asset_wc.get_active_flag():
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
    event, values = edit_loan_win(sg, loan_name, interest, start_date, end_date, initial_amount, present_amt).read(close=True)
    if event == 'Save':
        update_loan(c, conn, sg, values, loan_name, interest, start_date_obj, end_date_obj, initial_amount, present_amt)
    elif event == 'Archive':
        # TODO: Add an Archive
        pass


def edit_asset(sg, conn, c, values, asset_sheet):
    row_int = values['-Assets table-'][0]
    assets_name = asset_sheet[row_int][0]
    c.execute("SELECT * FROM assets WHERE name=:name", {"name" : assets_name})
    data = c.fetchone()
    event, values = edit_asset_win(sg, data[0:4]).read(close=True)
    if event == 'Edit Present Worth 1':
        event, values = edit_pw_win(sg, data, 0).read(close=True)
        if event == 'Save':
            update_asset_2(c, conn, sg, values, data, 0)
    elif event == 'Edit Present Worth 2':
        event, values = edit_pw_win(sg, data, 1).read(close=True)
        if event == 'Save':
            update_asset_2(c, conn, sg, values, data, 1)
    elif event == 'Archive':
        # TODO: Add an archive
        pass
    elif event == 'Save':
        update_asset(c, conn, sg, values, data, assets_name)
