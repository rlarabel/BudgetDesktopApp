from datetime import datetime
from dateutil import relativedelta


# Description: Creates the budget sheet based on the information the user has provided
# Inputs: conn - test DB connection, cursor - to access DB, and budget_date - specifies what data to show 
# Outputs: table - A 2D list with each inside table having 7 elements (id, name, monthly budget, upcoming monthly expenses, monthly spending, monthly progress, total [available]),
#			unallocated_cash_info - a list of dictionary for all the accounts that contains different flags (over allocated, under allocated, uncategorized spending) for the program to warn the user
#           about 
def makeBudgetSheet(conn, cursor, pov):
    with conn:
        # Initialize variables
        table = []
        unallocated_cash_info = []
        flagged_date = None
        total_budget = 0
        
        # Loop through all accounts 
        cursor.execute("""
                       SELECT * 
                       FROM accounts 
                       WHERE type=:spending OR type=:bills OR type=:income
                       ORDER BY CASE WHEN type=:income THEN 1
                       ELSE 2 END
                       """, 
                       {'spending': 'spending', 'bills': 'bills', 'income': 'income'}
        )
        for account in cursor.fetchall():
            uncat_spending_flag = False
            budget_flag = False
            
            # Gets the total of all previous transactions for an account selected from the DB
            cursor.execute("SELECT total FROM transactions WHERE account=:name AND date<=:date", {'name': account[0], 'date': pov.getTodayStr()})
            account_transactions = cursor.fetchall()
            account_total = 0
            for single_trans in account_transactions:
                account_total += single_trans[0]       
            
            # Creates account row in budget sheet
            table.append(['',account[0], '', '', '', 'Account Total:', '$' + str(round(account_total, 2))])
            
            # Loop through all categories
            cursor.execute("SELECT * FROM categories WHERE account=:name", {'name': account[0]})
            all_categories = cursor.fetchall()      
            for category in all_categories:
                under_allocated_flag = False
                over_allocated_flag = False
                category_id = category[0]
                category_name = category[1]
                if pov.getScope() == 'past' or category[3] < 0.01:
                    pre_set = '-'
                else:
                    pre_set = '$' + str(round(category[3], 2))
                
                # Gets the name, pre-set budget, money spent the view month, budget, budget left  for each category selected from the DB
                if category_name != 'Unallocated Cash':
                    flagged_date = checkPrevMonths(conn, cursor, pov, account[0], category_id)
                    if flagged_date or budget_flag:
                        budget_flag = True
                    else:
                        budget_flag = False
                    spent, budget, budget_left = getMonthlyCategoryData(cursor, pov, category_id, account[0])
                    total_budget += budget
                    
                    spent = '$' + str(round(spent, 2))
                    budget = '$' + str(round(budget, 2))
                    
                    if type(budget_left) != str:
                        budget_left = str(round(budget_left, 2)) + '%'

                    table.append([category_id, category_name, pre_set, budget, spent, 'percent budget', budget_left])
                    
                else:
                    available = getAvailable(cursor, category_id, account[0])  
                    unallocated_id = category_id
            
            # The unallocated category is the last row added for an account
            if account[1] != 'income':
                unallocated_category = [unallocated_id,'Available Cash', '', '', '', '', '$' + str(round(available, 2))]
                table.append(unallocated_category)
            table.append(['','', '', '', '', '', ''])
            
            # Flags for over or under budgeting and spending
            cursor.execute("SELECT id FROM transactions WHERE account=:name AND category_id=:category_id AND total<:total AND notes!=:notes ", 
                              {'name': account[0], 'category_id': unallocated_id, 'notes':'TRANSFER', 'total': 0})
            if cursor.fetchall():
                uncat_spending_flag = True
            if available > 25:
                under_allocated_flag = True
            elif available < 0 and not uncat_spending_flag:
                over_allocated_flag = True

            unallocated_cash_info.append(
                {
                    'account': account[0],
                    'over allocated': over_allocated_flag, 
                    'under allocated': under_allocated_flag, 
                    'uncategorized spending': uncat_spending_flag, 
                    'insufficient budget': budget_flag
                }
            )

        if not table:
            table = [['','', '', '', '', '', '']]
        else:
            # go back and edit table to include percent of budget
            for row in table:
                if row[5] == 'percent budget':
                    temp_budget = float(row[3][1:])
                    if total_budget > 0 and temp_budget > 0:
                        percent_budget = temp_budget / total_budget * 100
                        row[5] = str(round(percent_budget, 1)) + '%'
                    else:
                        row[5] = '-'
        
        return table, unallocated_cash_info

# Description: Gets the monthly data for each category 
# Input:
# Output:
def getMonthlyCategoryData(cursor, pov, category_id, account):

    spent = getSpendings(cursor, pov, category_id, account)
    budget = getBudget(cursor, pov, category_id, account)
    budget_left = getBudgetLeft(spent, budget)
    
    return spent, budget, budget_left


def getSpendings(cursor, pov, category_id, account):
    start_date = pov.getViewDateStr()
    end_date = pov.getNextMonthStr()
    spending = 0

    cursor.execute("SELECT total, date FROM transactions WHERE category_id=:category_id AND account=:account AND date>=:start_date AND date<:end_date", 
                {'category_id': category_id, 'account': account, 'start_date': start_date, 'end_date': end_date})
    month_transactions = cursor.fetchall()
    if month_transactions:
        for trans in month_transactions:
            spending -= trans[0]
    
    return spending


def getBudget(cursor, pov, category_id, account):
    budget = 0.0
    scope = pov.getScope()
    budget_date = pov.getViewDateStr()
    
    if scope == 'past' or scope == 'present':
        cursor.execute("SELECT total FROM track_categories WHERE category_id=:category_id AND account=:account AND date=:date", 
                {'category_id': category_id, 'account': account, 'date': budget_date})
        month_budget = cursor.fetchone()
        if month_budget:
            budget = month_budget[0]
    else:
        # Get budget log from present month to the selected month
        cursor.execute("SELECT total FROM track_categories WHERE category_id=:id AND account=:account AND date>=:start_date AND date<=:end_date",
                       {'id': category_id, 'account': account, 'start_date':pov.getThisMonthStr(),'end_date': budget_date})
        budget_log = cursor.fetchall()
        if budget_log:
            budget_lump_sum = 0
            for monthly_budget in budget_log:
                budget_lump_sum += monthly_budget[0]
            # Get spending only for the current month
            cursor.execute("SELECT total FROM transactions WHERE category_id=:id AND account=:account AND date>=:start_date AND date<=:end_date",
                       {'id': category_id, 'account': account, 'start_date':pov.getThisMonthStr(),'end_date': pov.getTodayStr()})
            spendings = cursor.fetchall()
            if spendings:
                for total in spendings:
                    budget_lump_sum += total[0]
            budget = budget_lump_sum
    
    return budget


def getBudgetLeft(spent, budget):
    # Budget left (current) or spendings covered (Past)
    if budget and budget > 0:
        progress = ((budget - spent) / budget) * 100
    else: 
        progress = '-'
    
    return progress


def getAvailable(cursor, id, account):
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

def setRowColors(conn, cursor, unallocated_cash_info):
    with conn:
        account_color = []
        i = 0
        # Loop through all accounts
        cursor.execute("""
                        SELECT * 
                        FROM accounts 
                        WHERE type=:spending OR type=:bills OR type=:income 
                        ORDER BY CASE WHEN type=:income THEN 1
                        ELSE 2 END
                       """, 
                    {'spending': 'spending', 'bills': 'bills', 'income': 'income'}
        )
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
            if account[1] == 'income':
                i += 1
            else:
                i += 2
                # Turn the available cash row red if:
                # The user bugets more many than in the account
                # User spend money without categorizing it
                # User doesn't budget enough in a previous month 
                if color_info['over allocated'] or color_info['uncategorized spending'] or color_info['insufficient budget']:
                    account_color.append((i-2, 'navy blue', 'red'))
                elif color_info['under allocated']:
                    account_color.append((i-2, 'navy blue', 'yellow'))
                else:
                    account_color.append((i-2, 'navy blue', 'green'))
         
        return account_color

# Check the previous months of each category for the desired account
# Check if the budget for that month covers the spending for that month
# if it doesn't, flag the first date that it happens 
def checkPrevMonths(conn, cursor, pov, account, category_id):
    flagged_date = None
    # Get first transaction for a category
    cursor.execute("""SELECT date FROM transactions WHERE total<0 AND notes!=:note 
                AND account=:account AND category_id=:category_id ORDER BY date ASC""", 
                {'note': 'TRASNFER', 'account': account, 'category_id': category_id})
    spendings = cursor.fetchone()

    if spendings:
        start_date = spendings[0]
        date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(day=1)
        # Get the spendings and budget month by month up until the currently viewed month
        while date_obj.date() <= pov.getViewDate().date():
            next_month = date_obj + relativedelta.relativedelta(months=1)
            next_month_str = next_month.strftime('%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d')
            # Get spendings
            cursor.execute("""SELECT total FROM transactions WHERE date>=:start_date AND date<:end_date 
                           AND total<0 AND account=:account AND category_id=:category_id ORDER BY date ASC""", 
                           {'start_date': date_str, 'end_date': next_month_str, 'account': account, 'category_id': category_id})
            spendings = cursor.fetchall()
            if spendings:
                spent = 0
                for amount in spendings:
                    if amount:
                        spent += amount[0]
            else:
                spent = 0
            
            # Get budget
            cursor.execute("""SELECT total FROM track_categories 
                            WHERE date=:date AND account=:account AND category_id=:category_id""", 
                            {'date': date_str, 'account': account, 'category_id': category_id})
            past_budget = cursor.fetchone()
            if past_budget:
                past_budget = past_budget[0]
            else:
                past_budget = 0
            
            # Budget doesn't cover spendings, flag the date and warn user
            if -spent >= (past_budget + 0.01) and not flagged_date:
                flagged_date = date_str
            # Budget cover too much of spendings 
            elif -spent <= (past_budget - 0.01) and date_obj.date() < pov.getThisMonth().date():
                # Update the data base
                rollover = (past_budget + spent)
                cursor.execute("""SELECT total FROM track_categories 
                                WHERE date=:date AND account=:account AND category_id=:category_id""", 
                                {'date': pov.getThisMonthStr(), 'account': account, 'category_id': category_id}
                )
                present_budget = cursor.fetchone()
                if present_budget:
                    present_budget = present_budget[0]
                    cursor.execute("""UPDATE track_categories 
                                    SET total=:total 
                                    WHERE date=:date AND account=:account AND category_id=:category_id""", 
                                    {
                                        'total': present_budget + rollover, 
                                        'date': pov.getThisMonthStr(), 
                                        'account': account, 
                                        'category_id': category_id
                                    }
                    )
                else:
                    cursor.execute("""INSERT INTO track_categories VALUES (:id, :date, :total, :account, :category_id)""",
                                    {
                                        'id': None, 
                                        'date': pov.getThisMonthStr(), 
                                        'total': rollover, 
                                        'account': account, 
                                        'category_id': category_id
                                    }
                    )
                cursor.execute("""UPDATE track_categories SET total=:total 
                                WHERE date=:date AND account=:account AND category_id=:category_id""", 
                                {
                                    'total': past_budget - rollover, 
                                    'date': date_str,
                                    'account': account, 
                                    'category_id': category_id
                                }
                )
                conn.commit()
                                        
            date_obj = next_month

    return flagged_date
