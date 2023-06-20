from datetime import datetime, timedelta
from itertools import zip_longest

# Getting the data for the time period selected by the user
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


def make_budget_sheet(conn, cursor, budget_date):
    with conn:
        cursor.execute("SELECT * FROM accounts WHERE type=:type", {'type': 'spending'})
        table = []
        unallocated_cash_info = []
        for account in cursor.fetchall():
            # Finds the account name
            cursor.execute("SELECT * FROM categories WHERE account=:name", {'name': account[0]})
            all_categories = cursor.fetchall()
            
            # Edit dates to get desired results
            user_year, user_month = budget_date.split('-')
            user_year = int(user_year)
            user_month = int(user_month)
            
            # Calculating Next Month date
            if user_month == 12:
                next_month = 1
                next_months_year = user_year + 1
            else:
                next_month = user_month + 1
                next_months_year = user_year
            if next_month < 10:
                next_month = '0' + str(next_month)
            else:
                next_month = str(next_month)
            next_month_date = str(next_months_year) + '-' + next_month + '-01'
            
            tomorrows_date = datetime.today() + timedelta(1) 
            tomorrows_date = tomorrows_date.strftime("%Y-%m-%d")    
            # Calculating the date needed to select the right enteries in the DB
            # If its this month or the future, use tomorrow's date. Else, for the past months, use the next months first date. 
            # Use the date to search the transaction table    
            if (user_month >= datetime.now().month and user_year == datetime.now().year) or user_year > datetime.now().year: 
                slt_budget_date = tomorrows_date

            else:

                slt_budget_date = next_month_date
            
            # Gets the total of all transactions for an account selected from the DB
            cursor.execute("SELECT total, category_id FROM transactions WHERE account=:name AND date<:date", {'name': account[0], 'date': tomorrows_date})
            account_transactions = cursor.fetchall()
            
            account_total = 0
            for single_trans in account_transactions:
                cursor.execute("SELECT name FROM categories WHERE id=:id", {'id': single_trans[1]})
                account_total += single_trans[0]
                unallocated_cash =  account_total       
            table.append(['',account[0], '', '', '', '', str(round(account_total, 2))])

            cursor.execute("SELECT total FROM track_categories WHERE account=:account", {'account': account[0]})
            for allocated_money in cursor.fetchall():
                unallocated_cash -= allocated_money[0]
                  
            for category in all_categories:
                under_allocated_flag = False
                over_allocated_flag = False
                category_id = category[0]
                category_name = category[1]
                # Gets user allocated data of the category for the selected month
                cursor.execute("SELECT * FROM track_categories WHERE category_id=:category_id AND account=:account AND date<:date", {'category_id': category_id, 'account': account[0], 'date': next_month_date})
                category_budget = cursor.fetchall()
                cursor.execute("SELECT * FROM transactions WHERE category_id=:category_id AND account=:account", {'category_id': category_id, 'account': account[0]})
                category_transactions = cursor.fetchall()
                
                # Gets the monthly budget, budget progress, montly spending, and upcoming expenses for each category selected from the DB
                month_budget, month_progress, month_spending, category_total, upcoming_expenses, uncat_spending_flag, cat_spending = get_monthly_category_data(category_transactions, category_budget, next_month_date, category_name)
                if category_name != 'Unallocated Cash':
                    
                    month_progress = str(round(month_progress)) + '%'
                   
                    unallocated_cash -= cat_spending
                    month_budget = str(round(month_budget, 2))
                    month_spending = str(round(month_spending, 2))
               
                    if upcoming_expenses == 0:
                        upcoming_expenses = '-'
                        
                    else:
                        upcoming_expenses = str(round(upcoming_expenses, 2)) 
                    category_total = str(round(category_total, 2))    
                    
                    table.append([category_id, category_name, month_budget, upcoming_expenses, month_spending, month_progress, category_total])
                else: 
                    unallocated_id = category_id
            unallocated_category = [unallocated_id,'Unallocated Cash', '-', '-', '-', '-', unallocated_cash]
            table.append(unallocated_category)
            if unallocated_cash > 25:
                under_allocated_flag = True
            elif unallocated_cash < 0 and not uncat_spending_flag:
                over_allocated_flag = True
            
            unallocated_cash_info.append({'account': account[0],'over allocated': over_allocated_flag, 'under allocated': under_allocated_flag, 'uncategorized spending': uncat_spending_flag})
        if not table:
            table = [['','', '', '', '', '', '']]
        
        return table, unallocated_cash_info


def get_monthly_category_data(transactions, budget_data, budget_date, category_name):
    spending = 0
    total_spending = 0
    budget = 0 
    total_budget = 0
    upcoming_expenses = 0
    categorized_spending = 0
    last_months_total = 0
    
    uncat_spending_flag = False
    if budget_date:
        slt_sel_date = datetime.strptime(budget_date, '%Y-%m-%d')
        eq_sel_date = slt_sel_date - timedelta(1)
    if budget_data and budget_date:
        for month_budget in budget_data:
            budget_data_date = datetime.strptime(month_budget[1], '%Y-%m-%d')
            if eq_sel_date.month == budget_data_date.month and eq_sel_date.year == budget_data_date.year:
                budget = month_budget[2]
            total_budget += month_budget[2]
    if transactions and budget_date:
        for single_trans in transactions:
            trans_date = datetime.strptime(single_trans[1], '%Y-%m-%d')
            if single_trans[4] < 0 and category_name != "Unallocated Cash":
                categorized_spending += single_trans[4]
            # Check if a transaction is less than 0, is uncategorized, and isn't a transfer
            if single_trans[4] < 0 and category_name == "Unallocated Cash" and single_trans[3] != "TRANSFER":
                uncat_spending_flag = True
                
            # Checks the date and determines if a transaction should be added to already spent money or upcoming expenses
            if single_trans[1] < budget_date:
                # Gets only the selected months spending
                if trans_date.month == eq_sel_date.month and eq_sel_date.year == trans_date.year:
                    spending -= single_trans[4]
                total_spending -= single_trans[4]
            # Checks if budget date is greater than today and selects only transactions with the same year and month the user slected
            elif budget_date > datetime.today().strftime("%Y-%m-%d") and eq_sel_date.month == trans_date.month and trans_date.year == eq_sel_date.year:
                upcoming_expenses -= single_trans[4]
            
    total = total_budget - total_spending
    budget = total_budget - total_spending + spending
    if budget == 0:
        progress = 0
    else:
        progress = ((total - upcoming_expenses) / budget) * 100
    return budget, progress, spending, total, upcoming_expenses, uncat_spending_flag, categorized_spending 


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
            cursor.execute("SELECT * FROM categories WHERE account=:name", {'name': account[0]})
            for _ in cursor.fetchall():
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
