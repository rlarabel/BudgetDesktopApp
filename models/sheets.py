from datetime import datetime, timedelta
from dateutil import relativedelta
from itertools import zip_longest

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
        cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': 'spending'})
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
        cursor.execute("SELECT * FROM accounts WHERE type=:spending OR type=:income ", {'spending': 'spending', 'income': 'income'})
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
