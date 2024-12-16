from datetime import datetime
from dateutil import relativedelta
import numpy_financial as npf


# Description: (In the works) Retirement planner
# Input: 
# Output:
def make_track_sheet(conn, cursor, track_date, months):
    with conn:
    	# Gets all saved accounts from DB
        cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': 'investment'})
        table = []
        
        # Goes through each account,
        for account in cursor.fetchall():
            if account:
            	# Gets the internal movement set by the user
                cursor.execute("SELECT * FROM track_categories WHERE account=:name", {'name': account[0]})
                track_internal = cursor.fetchall()
                # Gets the transactions described by the user
                cursor.execute("SELECT * FROM transactions WHERE account=:name", {'name': account[0]})
                transactions = cursor.fetchall()
                account_monthly, _, _, funded_total = get_monthly_total(track_internal, transactions, track_date)

                account_monthly = round(account_monthly, 2)
                funded_total = round(funded_total, 2)
                by_date = '-'
                suggested_amount = '-'

                account_total = '-'
                if account[2]:
                    account_total = str(round(account[2], 2))

                if account[3] and account[4]:
                    date_format = '%Y-%m-%d'
                    goal_date = datetime.strptime(account[4], date_format)
                    goal_month = goal_date.month
                    goal_year = goal_date.year
                    delta_month = goal_month - datetime.now().month
                    user_date = track_date + '-1'
                    user_date = datetime.strptime(user_date, date_format)
                    if user_date < goal_date:
                        delta_money = account[3] - account_monthly
                        if delta_month > 0:
                            if account_total != '-':
                                suggested_amount = round(delta_money - float(account_total), 2)
                            else:
                                suggested_amount = round(delta_money - float(funded_total), 2)
                            by_date = months[goal_month - 1] + ' ' + str(goal_year)
                            if suggested_amount > 0:
                                suggested_amount = '{:+}'.format(suggested_amount)
                            else:
                                suggested_amount = 'Goal Met'
                        else:
                            suggested_amount = 'Update your goal'
                            by_date = 'Passed'

                table.append([account[0], str(account_monthly), str(funded_total), account_total, suggested_amount, by_date])

        if not table:
            table = [['', '', '', '', '', '']]

        return table

# Description: Creates the budget sheet based on the information the user has provided
# Inputs: conn - test DB connection, cursor - to access DB, and budget_date - specifies what data to show 
# Outputs: table - A 2D list with each inside table having 7 elements (id, name, monthly budget, upcoming monthly expenses, monthly spending, monthly progress, total [available]),
#			unallocated_cash_info - a list of dictionary for all the accounts that contains different flags (over allocated, under allocated, uncategorized spending) for the program to warn the user
#           about 
def make_budget_sheet(conn, cursor, budget_date):
    with conn:
        # Initalize variables
        table = []
        unallocated_cash_info = []
        budget_date = budget_date + '-01'
        todays_date = datetime.today().strftime("%Y-%m-%d")
        
        # Loop through all accounts 
        cursor.execute("SELECT * FROM accounts WHERE type=:spending OR type=:bills", {'spending': 'spending', 'bills': 'bills'})
        for account in cursor.fetchall():
            uncat_spending_flag = False
            
            # Gets the total of all previous transactions for an account selected from the DB
            cursor.execute("SELECT total, category_id FROM transactions WHERE account=:name AND date<=:date", {'name': account[0], 'date': todays_date})
            account_transactions = cursor.fetchall()
            account_total = 0
            for single_trans in account_transactions:
                cursor.execute("SELECT name FROM categories WHERE id=:id", {'id': single_trans[1]})
                account_total += single_trans[0]
            unallocated_cash =  account_total       
            
            # Creates account row in budget sheet
            table.append(['',account[0], '', '', '', '', str(round(account_total, 2))])

			# Subtract the budget values for future months from the unallocated money
            date_selected = budget_date
            if datetime.strptime(budget_date, '%Y-%m-%d') < datetime.today().replace(day=1):
                date_selected = datetime.today().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute("SELECT total FROM track_categories WHERE account=:account AND date>:date", {'account': account[0], 'date': date_selected})
            for allocated_money in cursor.fetchall():
                unallocated_cash -= allocated_money[0]
            
            # Loop through all categories
            cursor.execute("SELECT * FROM categories WHERE account=:name", {'name': account[0]})
            all_categories = cursor.fetchall()      
            for category in all_categories:
                under_allocated_flag = False
                over_allocated_flag = False
                category_id = category[0]
                category_name = category[1]
                
                # Gets the monthly budget, budget progress, montly spending, and upcoming expenses for each category selected from the DB
                if category_name != 'Unallocated Cash':
                    month_budget, month_progress, month_spending, category_total, upcoming_expenses = get_monthly_category_data(cursor, todays_date, budget_date, category_name, category_id, account[0])
                    unallocated_cash -= float(category_total)
                    table.append([category_id, category_name, month_budget, upcoming_expenses, month_spending, month_progress, category_total])
                    
                else: 
                    unallocated_id = category_id
            
            # The unallocated category is the last row added for an account
            unallocated_category = [unallocated_id,'Unallocated Cash', '', '', '', '', str(round(unallocated_cash, 2))]
            table.append(unallocated_category)
            
            # Flags for over or under budgeting and spending
            cursor.execute("SELECT id FROM transactions WHERE account=:name AND category_id=:category_id AND total<:total AND notes!=:notes ", 
                              {'name': account[0], 'category_id': unallocated_id, 'notes':'TRANSFER', 'total': 0})
            if cursor.fetchall():
                uncat_spending_flag = True
            if unallocated_cash > 25:
                under_allocated_flag = True
            elif unallocated_cash < 0 and not uncat_spending_flag:
                over_allocated_flag = True
            
            unallocated_cash_info.append({'account': account[0],'over allocated': over_allocated_flag, 'under allocated': under_allocated_flag, 'uncategorized spending': uncat_spending_flag})
        if not table:
            table = [['','', '', '', '', '', '']]
        
        return table, unallocated_cash_info

# Description: Gets the monthly data for each category 
# Input:
# Output:
def get_monthly_category_data(cursor, todays_date, budget_date, category_name, category_id, account):
    spending = 0
    total = 0 
    upcoming_expenses = 0
    last_months_total = 0
    next_month_date = datetime.strptime(budget_date, '%Y-%m-%d') + relativedelta.relativedelta(months=1)
    next_month_date_str = next_month_date.strftime("%Y-%m-%d")
    user_year, user_month, _ = budget_date.split('-')
    todays_year, todays_month, _ = todays_date.split('-')
    user_year = int(user_year)
    user_month = int(user_month)
    todays_year = int(todays_year)
    todays_month = int(todays_month)
     
    # Budget 
    cursor.execute("SELECT total FROM track_categories WHERE category_id=:category_id AND account=:account AND date=:date", 
                    {'category_id': category_id, 'account': account, 'date': budget_date})
    budget = cursor.fetchone()
    if budget:
    	budget = budget[0]
    else:
    	budget = 0
    
    # Upcoming Expenses and Spendings
    cursor.execute("SELECT date, total FROM transactions WHERE category_id=:category_id AND account=:account AND date>=:start_date AND date<:end_date", 
                    {'category_id': category_id, 'account': account, 'start_date': budget_date, 'end_date': next_month_date_str})
    month_transactions = cursor.fetchall()
		
    if user_year < todays_year or (user_year == todays_year and user_month < todays_month):			# Past
        if month_transactions:
            for trans in month_transactions:
                spending -= trans[1]
    elif user_year == todays_year and user_month == todays_month:									# Current
        if month_transactions:
            for trans in month_transactions:
                if datetime.strptime(trans[0], '%Y-%m-%d') > datetime.today():
                	upcoming_expenses -= trans[1]
                else:
                    spending -= trans[1] 
    else:																							# Future
        if month_transactions:
            for trans in month_transactions:
                upcoming_expenses -= trans[1]
	         
    # Budget Progress
    if budget > 0:
        progress = ((budget - (upcoming_expenses + spending)) / budget) * 100
    else: 
	    progress = '-'
	 
	# Total Available
    cursor.execute("SELECT total FROM transactions WHERE category_id=:category_id AND account=:account AND date<=:date", 
                    {'category_id': category_id, 'account': account, 'date': todays_date})
    all_prev_transactions = cursor.fetchall()
    if all_prev_transactions:
        for trans in all_prev_transactions:
             total += trans[0]
    cursor.execute("SELECT total FROM track_categories WHERE category_id=:category_id AND account=:account", 
                    {'category_id': category_id, 'account': account})
    amount_budgeted = cursor.fetchall()
    if amount_budgeted:
         for months_budget in amount_budgeted:
             total += months_budget[0]
             
    # Formatting
    if progress != '-':    
        progress = str(round(progress)) + '%'
    budget = str(round(budget, 2))
    spending = str(round(spending, 2))
    total = str(round(total, 2))    
               
    if upcoming_expenses == 0:
        upcoming_expenses = '-'
                        
    else:
        upcoming_expenses = str(round(upcoming_expenses, 2)) 
     
    return budget, progress, spending, total, upcoming_expenses  

def set_transaction_row_colors(conn, cursor):
    with conn:
        row_color = []
        i = 0
        cursor.execute("SELECT category_id, total, notes FROM transactions ORDER BY date DESC")
        for category_id, total, notes in cursor.fetchall():
            cursor.execute("SELECT name FROM categories WHERE id=:id", {'id': category_id})
            category_name = cursor.fetchone()[0]
            if(notes != 'TRANSFER'):
                if(category_name == 'Unallocated Cash' and total < 0):
                    row_color.append((i, 'navy blue', 'red'))
                elif(i % 2 == 0):
                    row_color.append((i, 'white', '#7f8f9f'))
                i += 1

        return row_color

def set_row_colors(conn, cursor, unallocated_cash_info):
    with conn:
        account_color = []
        i = 0
        cursor.execute("SELECT * FROM accounts WHERE type=:spending OR type=:bills ", {'spending': 'spending', 'bills': 'bills'})
        for account in cursor.fetchall():
            color_info = None
            j = 0
            while not color_info and len(unallocated_cash_info) > j:
               if account[0] == unallocated_cash_info[j]['account']:
                   color_info = unallocated_cash_info[j]
               else:
                   j += 1
             
            if color_info['over allocated']:
                account_color.append((i, 'navy blue', 'red'))
            else:
                account_color.append((i, 'navy blue', 'grey'))
            i += 1
            cursor.execute("SELECT name FROM categories WHERE account=:name", {'name': account[0]})
            for cat in cursor.fetchall():
                if cat[0] != 'Unallocated Cash':
                    if(i % 2 == 0):
                        account_color.append((i, 'white', '#7f8f9f'))
                i += 1
            if color_info['over allocated'] or color_info['uncategorized spending']:
                account_color.append((i-1, 'navy blue', 'red'))
            elif color_info['under allocated']:
                account_color.append((i-1, 'navy blue', 'yellow'))
            else:
                account_color.append((i-1, 'navy blue', 'green')) 
        return account_color


def set_track_row_colors(conn, cursor):
    with conn:
        account_color = []
        cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': 'budget'})
        for i, account in enumerate(cursor.fetchall()):
            account_color.append((i, 'navy blue', 'grey'))

        return account_color


def make_transaction_sheet(conn, cursor):
    with conn:
        table = []
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        all_transactions = cursor.fetchall()
        for transaction in all_transactions:
            id_num, date, payee, notes, total, account, category_id = transaction
            date = datetime.strptime(date, '%Y-%m-%d')
            date = date.strftime('%m-%d-%Y')
            cursor.execute("SELECT name FROM categories WHERE id=:category_id", {'category_id': category_id})
            category_name = cursor.fetchone()[0]
            if category_name == 'Unallocated Cash':
                category_name = '-' 
            if notes != 'TRANSFER':
                ordered_transaction = [id_num, date, account, category_name, payee,
                           notes, total]
                table.append(ordered_transaction)
        if not table:
            table = [['', '', '', '', '', '', '']]
        return table

def make_savings_sheet(conn, cursor, view_date):
    with conn:
        table = []
        view_date = datetime.strptime(view_date, '%Y-%m')

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'savings'})
        savings_accounts = cursor.fetchall()
        for account in savings_accounts:
            name = account[0]
            cursor.execute("SELECT interest, real_value FROM savings WHERE name=:name", {'name': name})
            desired_apy, real_value = cursor.fetchone()
            # TODO: Calculate the avg apy with the total deposit, real value, and basis
            # TODO: Actual apy, total interest earned, total interest growth 
            month_deposit, total_deposit, actual_apy, i_amount, total_i = calc_savings_data(cursor, view_date, name, real_value)
            table.append([name, month_deposit, total_deposit, real_value, desired_apy, actual_apy, i_amount, total_i])
        if not table:
            return [['','','','','', '', '']]
        else:
            return table

def calc_savings_data(cursor, view_date, name, real_value):
    total_deposit = 0
    month_deposit = 0
    actual_apy = 0 
    i_amount = 0 
    total_i = 0
    n_years = 0
    oldest_date = None

    cursor.execute("SELECT date, total FROM transactions WHERE account=:account", {'account': name})
    for date, total in cursor.fetchall():
        date = datetime.strptime(date, '%Y-%m-%d')

        # Find the total deposit amount and the current viewing month's deposit amount
        total_deposit += total
        if date.month == view_date.month and date.year == view_date.year: 
            month_deposit += total

        # Find the oldest date to calc number of years
        if not oldest_date:
            oldest_date = date
        elif oldest_date > date:
            oldest_date = date
        
    delta = datetime.today() - oldest_date
    n_years = delta.days / 365.25
    
    # Find the actual apy
    if n_years < 0.002 or total_deposit < 0.01:
        actual_apy = 0.0 
    else:
        actual_apy = round((((real_value/total_deposit)**(1/n_years)) - 1) * 100, 3)
    
    # Find the total amount earned from interest
    i_amount = round(real_value - total_deposit, 2) 
    
    # Find the total interest growth
    if total_deposit < 0.01:
        total_i = 0.0
    else:
        total_i = round((i_amount / total_deposit) * 100, 1)

    return round(month_deposit, 2), round(total_deposit, 2), actual_apy, i_amount, total_i 
            
def make_asset_sheet(conn, cursor):
    # TODO: do calculations with the given value to find present worth of the asset and check where you are at with your loan,
    # Take initial loan amount (<= 0) and calculate the payment amount needed to reach desired payoff date.
    # To calculate payment amount grab initial loan amount and all payments so far from transactions, and the loan interest and desired payoff date from assets  
    # Find the present worth of the asset - initial value? (pv), MARR (i), estimated yearly expenses/profits (pyt), Estimated sell value (fv), estimated years to own (n)
    # Headers: 'Account', 'Present Loan Amount ($)', 'total interest paid ($)', 'monthly payments needed ($)' 'Desired Pay Off Date', ' Calculated Present Worth ($)'
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'asset'})
        asset_accounts = cursor.fetchall()
        for account in asset_accounts:
            name = account[0]
            cursor.execute("SELECT total FROM transactions WHERE account=:name", {'name': name})
            amt = cursor.fetchone()[0]
            pw1, pw2 = calc_asset_data(cursor, name)
            table.append([name, -amt, pw1, pw2])
    if table:
        return table
    else:
        return [['','','','']]

def calc_asset_data(cursor, name):
    pw1 = 0
    pw2 = 0
    cursor.execute("SELECT * FROM assets WHERE name=:name", {'name': name})
    _, _, i_1, amt_1, pv_1, fv_1, date_1, i_2, amt_2, pv_2, fv_2, date_2 = cursor.fetchone()
    # Calculate Present Worth 1
    if i_1 and pv_1 and fv_1 and date_1:
        cursor.execute("SELECT date FROM transactions WHERE account=:name", {'name': name})
        date = cursor.fetchone()[0]
        start_date = datetime.strptime(date, '%Y-%m-%d')
        end_date = datetime.strptime(date_1, '%Y-%m-%d')
        delta = end_date - start_date
        n_years = delta.days / 365.25
        pw1 += pv_1
        if not amt_1:
            amt_1 = 0
        pw1 += npf.pv(i_1/100, n_years, -amt_1, -fv_1)
        pw1 = round(pw1, 2)
    else:
        pw1 = None

    # Calculate Present Worth 2
    if i_2 and pv_2 and fv_2 and date_2:
        cursor.execute("SELECT date FROM transactions WHERE account=:name", {'name': name})
        date = cursor.fetchone()[0]
        start_date = datetime.strptime(date, '%Y-%m-%d')
        end_date = datetime.strptime(date_2, '%Y-%m-%d')
        delta = end_date - start_date
        n_years = delta.days / 365.25
        pw2 += pv_2
        if not amt_2:
            amt_2 = 0
        pw2 += npf.pv(i_2/100, n_years, -amt_2, -fv_2)
        pw2 = round(pw2, 2)
    else:
        pw2 = None

    return pw1, pw2

def make_loan_sheet(conn, cursor, view_date):
    # TODO: do calculations with the given value to find present worth of the asset and check where you are at with your loan,
    # Take initial loan amount (<= 0) and calculate the payment amount needed to reach desired payoff date.
    # To calculate payment amount grab initial loan amount and all payments so far from transactions, and the loan interest and desired payoff date from assets  
    # Find the present worth of the asset - initial value? (pv), MARR (i), estimated yearly expenses/profits (pyt), Estimated sell value (fv), estimated years to own (n)
    # Headers: 'Account', 'Present Loan Amount ($)', 'total interest paid ($)', 'monthly payments needed ($)' 'Desired Pay Off Date', ' Calculated Present Worth ($)'
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'loan'})

        for account in cursor.fetchall():
            name = account[0]
            cursor.execute("SELECT interest, end_date, present_amt FROM loans WHERE name=:name", {'name': name})
            interest, end_date, present_loan_amount = cursor.fetchone()
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            initial_loan_amt, monthly_pmt = calculate_loan_data(cursor, name, interest, end_date)
            table.append([initial_loan_amt, present_loan_amount, interest, end_date.strftime('%m-%d-%Y'), monthly_pmt])
    return [['','','','','']]

def calculate_loan_data(cursor, name, interest, end_date, present_loan_amount):
    cursor.execute("SELECT total, date FROM transactions WHERE account=:account", {"account": name})
    initial_date = None
    total_pmt = 0
    initial_loan_amt = 0
    
    # total interest paid: (initial loan amount - present loan amount) + sum(total pmt)
    # monthly pmt: present_loan_amount = pv, payoff date - today date (in years) = n, loan_i = i, monthly_pmt = pmt
    for total, t_date in cursor.fetchall():
        t_date = datetime.strptime(t_date, '%Y-%m-%d')
        if not initial_date:
            initial_date = t_date
            initial_loan_amt = total
        elif initial_date > t_date:
            initial_date = t_date
            initial_loan_amt = total
        total_pmt += total
    # TODO: incorporate later
    # total_pmt = total_pmt - initial_loan_amt 
    # total_interest_paid = (initial_loan_amt - present_loan_amount) + total_pmt
    delta = end_date - datetime.today()
    n_months = (delta.days / 365.25) * 12
    monthly_pmt = npf.amt(interest / (100 * 12), n_months, present_loan_amount, 0)
    return initial_loan_amt, monthly_pmt
