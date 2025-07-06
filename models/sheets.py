from datetime import datetime
from dateutil import relativedelta
import numpy_financial as npf


# Description: Creates the budget sheet based on the information the user has provided
# Inputs: conn - test DB connection, cursor - to access DB, and budget_date - specifies what data to show 
# Outputs: table - A 2D list with each inside table having 7 elements (id, name, monthly budget, upcoming monthly expenses, monthly spending, monthly progress, total [available]),
#			unallocated_cash_info - a list of dictionary for all the accounts that contains different flags (over allocated, under allocated, uncategorized spending) for the program to warn the user
#           about 
def make_budget_sheet(conn, cursor, budget_date):
    with conn:
        # Initialize variables
        table = []
        unallocated_cash_info = []
        budget_date = budget_date + '-01'
        budget_date_obj = datetime.strptime(budget_date, "%Y-%m-%d")
        todays_date_obj = datetime.today().replace(day=1) 
        todays_date = todays_date_obj.strftime("%Y-%m-%d")
        next_month_date = datetime.strptime(budget_date, '%Y-%m-%d') + relativedelta.relativedelta(months=1)
        next_month_date_str = next_month_date.strftime("%Y-%m-%d")
        

        # Setting the pov, so the user can see the correct data
        
        if todays_date_obj.date() == budget_date_obj.date():
            pov = 'present'
        elif todays_date_obj.date() < budget_date_obj.date():
            pov = 'future'
        else:
            pov = 'past'
        
        # Loop through all accounts 
        cursor.execute("SELECT * FROM accounts WHERE type=:spending OR type=:bills OR type=:income", {'spending': 'spending', 'bills': 'bills', 'income': 'income'})
        for account in cursor.fetchall():
            uncat_spending_flag = False
            
            # Gets the total of all previous transactions for an account selected from the DB
            cursor.execute("SELECT total FROM transactions WHERE account=:name AND date<=:date", {'name': account[0], 'date': todays_date})
            account_transactions = cursor.fetchall()
            account_total = 0
            for single_trans in account_transactions:
                account_total += single_trans[0]       
            
            # Creates account row in budget sheet
            table.append(['',account[0], '', '', '', '', str(round(account_total, 2))])
            
            # Loop through all categories
            cursor.execute("SELECT * FROM categories WHERE account=:name", {'name': account[0]})
            all_categories = cursor.fetchall()      
            for category in all_categories:
                under_allocated_flag = False
                over_allocated_flag = False
                category_id = category[0]
                category_name = category[1]
                pre_set = category[3]
                
                # Gets the name, pre-set budget, money spent the view month, budget, budget left  for each category selected from the DB
                if category_name != 'Unallocated Cash':
                    spent, budget, budget_left = get_monthly_category_data(cursor, todays_date, budget_date, category_id, account[0], pov, next_month_date_str)
                    spent = str(round(spent, 2))
                    budget = str(round(budget, 2))
                    if type(budget_left) != str:
                        budget_left = str(round(budget_left, 2))
                    table.append([category_id, category_name, pre_set, budget, spent, budget_left])
                    
                else:
                    available = get_available(cursor, category_id, account[0])  
                    unallocated_id = category_id
            
            # The unallocated category is the last row added for an account
            unallocated_category = [unallocated_id,'Available Cash', '', '', '', str(round(available, 2))]
            table.append(unallocated_category)
            
            # Flags for over or under budgeting and spending
            cursor.execute("SELECT id FROM transactions WHERE account=:name AND category_id=:category_id AND total<:total AND notes!=:notes ", 
                              {'name': account[0], 'category_id': unallocated_id, 'notes':'TRANSFER', 'total': 0})
            if cursor.fetchall():
                uncat_spending_flag = True
            if available > 25:
                under_allocated_flag = True
            elif available < 0 and not uncat_spending_flag:
                over_allocated_flag = True
            
            budget_flag, flagged_dates = check_prev_months(conn, cursor, budget_date, account[0], next_month_date_str, todays_date_obj)
            
            unallocated_cash_info.append({'account': account[0],'over allocated': over_allocated_flag, 'under allocated': under_allocated_flag, 'uncategorized spending': uncat_spending_flag, 'insufficient budget': budget_flag})
        if not table:
            table = [['','', '', '', '', '']]
        
        return table, unallocated_cash_info

# Description: Gets the monthly data for each category 
# Input:
# Output:
def get_monthly_category_data(cursor, todays_date, budget_date, category_id, account, pov, next_month_date_str):
    total_spending = get_spendings(cursor, category_id, account, 'total', todays_date)
    
    if pov == 'past':
        spent = get_spendings(cursor, category_id, account, 'past', budget_date, next_month_date_str)
        budget = get_budget(cursor, category_id, account, budget_date, todays_date, 'past')
        budget_left = get_budget_left(spent, budget)
    elif pov == 'present':
        spent = get_spendings(cursor, category_id, account, 'present', budget_date, next_month_date_str)
        budget = get_budget(cursor, category_id, account, budget_date, todays_date, 'present')
        budget_left = get_budget_left(spent, budget)
    else:
        spent = 0
        budget = get_budget(cursor, category_id, account, budget_date, todays_date, 'future') - total_spending
        budget_left = '-'    
    
    return spent, budget, budget_left

def get_spendings(cursor, category_id, account, pov, start_date=None, end_date=None):
    spending = 0.0
    if pov == 'past' or pov == 'present':
        cursor.execute("SELECT total FROM transactions WHERE category_id=:category_id AND account=:account AND date>=:start_date AND date<:end_date", 
                    {'category_id': category_id, 'account': account, 'start_date': start_date, 'end_date': end_date})
        month_transactions = cursor.fetchall()
        if month_transactions:
            if pov == 'past':
                for trans in month_transactions:
                    spending -= trans[0]
            elif pov == 'present':
                for trans in month_transactions:
                    if datetime.strptime(trans[0], '%Y-%m-%d') < datetime.today():
                        spending -= trans[0] 
    else:
        cursor.execute("SELECT total FROM transactions WHERE category_id=:category_id AND account=:account AND date=:date",
                       {'category_id': category_id, 'account': account, 'date': start_date})
        all_transactions = cursor.fetchall()
        if all_transactions:
            for trans in all_transactions:
                spending -= trans[0]
    
    return spending



def get_budget(cursor, category_id, account, budget_date, todays_date, pov):
    budget = 0.0
    
    if pov == 'past' or pov == 'present':
        cursor.execute("SELECT total FROM track_categories WHERE category_id=:category_id AND account=:account AND date=:date", 
                {'category_id': category_id, 'account': account, 'date': budget_date})
        past_budget = cursor.fetchone()
        if past_budget:
            budget = past_budget[0]
    else:
        cursor.execute("SELECT total FROM track_categories WHERE category_id=:id AND account=:account AND date>=:start_date AND date<=:end_date",
                       {'id': category_id, 'account': account, 'start_date':todays_date,'end_date': budget_date})
        budget_log = cursor.fetchall()
        if budget_log:
            budget_lump_sum = 0
            for monthly_budget in budget_log:
                budget_lump_sum += monthly_budget[0]
            budget = budget_lump_sum
    
    return budget


def get_budget_left(spent, budget):
    # Budget left (current) or spendings covered (Past)
    if budget and budget > 0:
        progress = ((budget - spent) / budget) * 100
    else: 
        progress = '-'
    
    return progress


def get_available(cursor, id, account):
    # Total Available
    total = 0
    cursor.execute("SELECT total FROM transactions WHERE category_id=:id AND account=:account",
                   {'id': id, 'account': account})
    amount_unbudgeted = cursor.fetchall()
    if amount_unbudgeted:
        for transaction in amount_unbudgeted:
            total += transaction[0]
    
    cursor.execute("SELECT total FROM track_categories WHERE account=:account", 
                    {'account': account})
    amount_budgeted = cursor.fetchall()
    if amount_budgeted:
         for months_budget in amount_budgeted:
            total -= months_budget[0]
    
    return total 


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
        # Loop through all accounts
        cursor.execute("SELECT * FROM accounts WHERE type=:spending OR type=:bills OR type=:income ", {'spending': 'spending', 'bills': 'bills', 'income': 'income'})
        for account in cursor.fetchall():
            # Check if the account has any flags, if so store the flags in color_info and update the row color
            color_info = None
            j = 0 
            while not color_info and len(unallocated_cash_info) > j:
               if account[0] == unallocated_cash_info[j]['account']:
                   color_info = unallocated_cash_info[j]
               else:
                   j += 1
            # If user bugets more many than in the account turn the account row red
            if color_info['over allocated']:
                account_color.append((i, 'navy blue', 'red'))
            else:
                account_color.append((i, 'navy blue', 'grey'))
            i += 1

            # Alternate between slightly different row colors
            cursor.execute("SELECT name FROM categories WHERE account=:name", {'name': account[0]})
            for cat in cursor.fetchall():
                if cat[0] != 'Unallocated Cash':
                    if(i % 2 == 0):
                        account_color.append((i, 'white', '#7f8f9f'))
                i += 1
            
            # Turn the available cash row red if:
            # The user bugets more many than in the account
            # User spend money without categorizing it
            # User doesn't budget enough in a previous month 
            if color_info['over allocated'] or color_info['uncategorized spending'] or color_info['insufficient budget']:
                account_color.append((i-1, 'navy blue', 'red'))
            elif color_info['under allocated']:
                account_color.append((i-1, 'navy blue', 'yellow'))
            else:
                account_color.append((i-1, 'navy blue', 'green'))
         
        return account_color

def check_prev_months(conn, cursor, budget_date, account, next_month_date_str, todays_date_obj):
    flagged_dates = []
    todays_date = todays_date_obj.strftime('%Y-%m-%d')
    budget_flag = False
    past_flag = False

    cursor.execute("SELECT id FROM categories WHERE name!='Unallocated Cash'")
    all_categories = cursor.fetchall()
    for category_id in all_categories:
        category_id = category_id[0]
        cursor.execute("""SELECT id, date, total, category_id FROM track_categories WHERE date<=:date AND account=:account 
                    AND category_id=:category_id ORDER BY date DESC""", 
                    {'date': budget_date, 'account': account, 'category_id': category_id})
        budget_log = cursor.fetchall()
        cursor.execute("""SELECT date, total FROM transactions WHERE date<:date AND total<0 AND notes!=:note 
                    AND account=:account AND category_id=:category_id ORDER BY date DESC""", 
                    {'date': next_month_date_str, 'note': 'TRASNFER', 'account': account, 'category_id': category_id})
        spendings = cursor.fetchall()
        if spendings:
            if budget_log:
                # Loop through budget log to see if all spendings are covered
                i = 0
                for budget_id, date, budget, category_id in budget_log:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    spendings_total = 0
                    year, month, _ = spendings[i][0].split('-')
                    loop_date = year + '-' + month + '-01'
                    while loop_date and loop_date == date :
                        spendings_total -= spendings[i][1]
                        i += 1
                        if i < len(spendings):
                            year, month, _ = spendings[i][0].split('-')
                            loop_date = year + '-' + month + '-01'
                        else:
                            loop_date = None

                    if date_obj.date() < todays_date_obj.date():
                        past_flag = True

                    if spendings_total > budget:
                        flagged_dates.append(date)
                        budget_flag = True
                    elif spendings_total < budget and past_flag:
                        rollover = budget - spendings_total
                        cursor.execute("UPDATE track_categories SET total=:total WHERE id=:id", 
                                        {'total':spendings_total, 'id': budget_id})
                        cursor.execute("SELECT id, total FROM track_categories WHERE date=:date AND category_id=:category_id AND account=:account", 
                                       {'date': todays_date, 'account': account, 'category_id': category_id})
                        category_transaction = cursor.fetchone()
                        if not category_transaction:
                            cursor.execute("""INSERT INTO track_categories VALUES (:id, :date, :total, :account, :category_id)""",
                                            {'id': None, 'date': todays_date, 'total': rollover, 'account': account, 'category_id': category_id})
                        else:
                            budget_id, total = category_transaction
                            total = total + rollover
                            cursor.execute("UPDATE track_categories SET total=:total WHERE id=:id",
                                            {'total': total, 'id': budget_id})
                        conn.commit()
                        past_flag = False
                # When there no more budget left but still unbudgeted spendings left 
                if i != len(spendings):
                    budget_flag = True
                    flagged_dates = flag_dates(i, 1, spendings, flagged_dates)
            else:
                # When there is spendings but no budget it cause a flag 
                budget_flag = True
                flagged_dates = flag_dates(0, 0, spendings, flagged_dates)

    
    return budget_flag, flagged_dates


def flag_dates(i, offset, spendings, flagged_dates):
    for j in range(i + offset, len(spendings)):
        date = spendings[i][0]
        year, month, _ = date.split('-')
        search_date = year + '-' + month
        if not search_date in flagged_dates:
            flagged_dates.append(search_date)
    return flagged_dates


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
        str_date = view_date + '-01'
        view_date = datetime.strptime(view_date, '%Y-%m')
        
        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'savings'})
        savings_accounts = cursor.fetchall()
        for account in savings_accounts:
            name = account[0]
            cursor.execute("SELECT interest FROM savings WHERE name=:name", {'name': name})
            desired_apy = cursor.fetchone()
            if desired_apy:
                desired_apy = desired_apy[0]
            else:
                desired_apy = 5.0
            cursor.execute("SELECT amount FROM track_savings WHERE account=:account AND date=:date",
                           {'account': name, 'date': str_date})
            amount = cursor.fetchone()
            if amount:
                amount = amount[0]
            else:
                amount = 0
            month_deposit, total_deposit, actual_apy, i_amount, total_i = calc_savings_data(cursor, view_date, name, amount)
            table.append([name, month_deposit, total_deposit, amount, desired_apy, actual_apy, i_amount, total_i])
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
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'asset'})
        asset_accounts = cursor.fetchall()
        for account in asset_accounts:
            name = account[0]
            cursor.execute("SELECT initial_amount FROM assets WHERE name=:name", {'name': name})
            amt = cursor.fetchone()[0]
            pw1, pw2 = calc_asset_data(cursor, name)
            table.append([name, amt, pw1, pw2])
    if table:
        return table
    else:
        return [['','','','']]

def calc_asset_data(cursor, name):
    pw1 = 0
    pw2 = 0
    cursor.execute("SELECT * FROM assets WHERE name=:name", {'name': name})
    _, _, initial_date, _, i_1, amt_1, pv_1, fv_1, date_1, i_2, amt_2, pv_2, fv_2, date_2 = cursor.fetchone()
    # Calculate Present Worth 1
    if initial_date and i_1 and pv_1 and fv_1 and date_1:
        start_date = datetime.strptime(initial_date, '%Y-%m-%d')
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
    if initial_date and i_2 and pv_2 and fv_2 and date_2:
        start_date = datetime.strptime(initial_date, '%Y-%m-%d')
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

def make_loan_sheet(conn, cursor):
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'loan'})

        for account in cursor.fetchall():
            name = account[0]
            cursor.execute("SELECT interest, end_date, present_amt FROM loans WHERE name=:name", {'name': name})
            interest, end_date, present_loan_amount = cursor.fetchone()
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            initial_loan_amt, monthly_pmt = calculate_loan_data(cursor, name, interest, end_date, present_loan_amount)
            table.append([name, initial_loan_amt, present_loan_amount, interest, end_date.strftime('%m-%d-%Y'), monthly_pmt])
        if table:
            return table
        else:
            return [['','','','','','']]

def calculate_loan_data(cursor, name, interest, end_date, present_loan_amount):
    cursor.execute("SELECT initial_amount, start_date FROM loans WHERE name=:name", {"name": name})
    initial_loan_amt = cursor.fetchone()[0]

    delta = end_date - datetime.today()
    n_months = (delta.days / 365.25) * 12
    monthly_pmt = npf.pmt(interest / (100 * 12), n_months, present_loan_amount, 0)
    return initial_loan_amt, round(monthly_pmt, 2)
