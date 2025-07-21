# TODO: Add folder and break functions into different files
# TODO: Turn menus into models
from logic.create_items import makeAccountMenu, makeCategoryMenu
from views.visuals import selWin
from datetime import datetime
from matplotlib.dates import DateFormatter
from dateutil.relativedelta import relativedelta

def addFig(sg, conn, c, plt, np, chart, timeframe, start_date=None, end_date=None):
    acc_menu = makeAccountMenu(conn, c)
    today = datetime.now()
    flag = 1

    if timeframe == 'YTD':
        start_date = datetime.strptime(f'01-{today.year}', '%m-%Y')
        end_date = today
    elif timeframe == 'Last month':
        start_date = today - relativedelta(months=1)
        end_date = start_date
    elif timeframe == 'Last year':
        start_date = datetime.strptime(f'01-{today.year-1}', '%m-%Y')
        end_date = datetime.strptime(f'12-{today.year-1}', '%m-%Y')
    elif timeframe == '1 year':
        start_date = today - relativedelta(years=1)
        end_date = today
    elif timeframe == '2 years':
        start_date = today - relativedelta(years=2)
        end_date = today
    elif timeframe == '5 years':
        start_date = today - relativedelta(years=5)
        end_date = today
    elif timeframe == '10 years':
        start_date = today - relativedelta(years=10)
        end_date = today
    elif timeframe == 'Custom Time Frame':
        if start_date == None:
            start_date = end_date
        elif end_date == None:
            end_date = start_date

    # Where money is at right now
    if chart == 'Pie Chart - Account Overview':
        total_savings = 0
        total_wants = 0
        total_needs = 0
        total_income = 0
        c.execute("SELECT total, account, notes FROM transactions")
        for total, acc, notes in c.fetchall():
            c.execute("SELECT type FROM accounts WHERE name=:name", {'name': acc})
            acc_type = c.fetchone()[0]
            if acc_type:
                if acc_type == 'savings':
                    total_savings += total
                elif acc_type == 'bills':
                    total_needs += total
                elif acc_type == 'spending':
                    total_wants += total
                elif acc_type == 'income':
                    total_income += total
        final_total = total_income + total_savings + total_needs + total_wants
        if final_total > 0.009:
            per_income = round(total_income / final_total * 100, 2)
            per_savings = round(total_savings / final_total * 100, 2)
            per_needs = round(total_needs / final_total * 100, 2)
            per_wants = round(total_wants / final_total * 100, 2)
        x = [total_needs, total_savings, total_wants, total_income]
        colors = ['r','g','b','y']
        labels = [f'Needs: {per_needs}%', f'Savings: {per_savings}%', f'Wants: {per_wants}%', f'Income: {per_income}%']
        title = 'Account Overview'
        flag = makePieChart(plt, x, labels, title, colors)
        
    elif chart == 'Pie Chart - Allocation (50/%-30/%-20/% Rule)':
        # If a transfer is not recorded as 'TRANSFER' in notes, it will mess with these #'s
        # If new account doesn't add previous transaction, enter the current value of an account as a transaction and in the notes label 'Initial Value'   
        total_savings = 0
        total_wants = 0
        total_needs = 0
        c.execute("SELECT total, account, notes FROM transactions")
        for total, acc, notes in c.fetchall():
            c.execute("SELECT type FROM accounts WHERE name=:name", {'name': acc})
            acc_type = c.fetchone()[0]
            if acc_type and total > 0 or notes == 'TRANSFER' or notes == 'Initial Value':
                if acc_type == 'savings':
                    total_savings += total
                elif acc_type == 'bills':
                    total_needs += total
                elif acc_type == 'spending':
                    total_wants += total
        total_amt = total_savings + total_needs + total_wants
        per_savings = round(total_savings / total_amt * 100, 2)
        per_needs = round(total_needs / total_amt * 100, 2)
        per_wants = round(total_wants / total_amt * 100, 2)
        
        x = [total_needs, total_savings, total_wants]
        colors = ['r','g','b','y']
        labels = [f'Needs: {per_needs}%', f'Savings: {per_savings}%', f'Wants: {per_wants}%']
        
        title = 'Allocation'

        flag = makePieChart(plt, x, labels, title, colors)

    elif chart == 'Pie Chart - Account Spending':
        acc_spending = accountSpending(c, start_date, end_date)
        
        x = []
        total_amt = 0
        for key in acc_spending:
            total_amt += acc_spending[key]                
            x.append(acc_spending[key])
        
        labels = []
        for key in acc_spending:
            percentage = round(acc_spending[key] / total_amt * 100, 2)
            labels.append(f'{key}: {percentage}%')
        
        if not (start_date or end_date):
            title = 'Account Spending'
        else:
            start_date = start_date.strftime('%m-%d-%Y')
            end_date = end_date.strftime('%m-%d-%Y')
            title = f'Account Spending from {start_date} to {end_date}'

        flag = makePieChart(plt, x, labels, title)

    elif chart == 'Pie Chart - Category Spending':
        event, values = selWin(sg, acc_menu, 'account').read(close=True)
        account = values['-Selection-'] 
        if event == 'Go' and account:
            cat_spending = categorySpending(c, account, start_date, end_date)
            
            x = []
            total_amt = 0
            for key in cat_spending:
                total_amt += cat_spending[key]                
                x.append(cat_spending[key])
            
            labels = []
            for key in cat_spending:
                percentage = round(cat_spending[key] / total_amt * 100, 2)
                labels.append(f'{key}: {percentage}%')

            if not (start_date or end_date):
                title = 'Category Spending'
            else:
                start_date = start_date.strftime('%m-%d-%Y')
                end_date = end_date.strftime('%m-%d-%Y')
                title = f'Category Spending from {start_date} to {end_date}'

            flag = makePieChart(plt, x, labels, title)

    elif chart == 'Bar Graph - Account Budgeting & Spending':   
        acc_spending = accountSpending(c, start_date, end_date)
        acc_total = accountTotal(c, start_date, end_date)
        if acc_total:
            spend_list = []
            budget_list = []
            accounts = []

            # Total months difference
            total_months = None
            # If timeframe == max give a start and end date
            if not (start_date and end_date):
                c.execute("SELECT date FROM transactions ORDER BY date ASC")
                start_date = c.fetchone()
                if start_date:
                    start_date = start_date[0]
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = today
                else: 
                    flag == -1
            if start_date and end_date and not (start_date.month == end_date.month and start_date.year == end_date.year):
                year_diff = end_date.year - start_date.year
                month_diff = end_date.month - start_date.month
                total_months = year_diff * 12 + month_diff


            for i, key in enumerate(acc_total, 1):
                try:
                    if total_months:
                        spend_list.append(round(acc_spending[key]/total_months, 2))
                    else:
                        spend_list.append(acc_spending[key])
                except KeyError:
                    spend_list.append(0)
                if total_months:
                    budget_list.append(round(acc_total[key]/total_months, 2))
                else:
                    budget_list.append(acc_total[key])
                accounts.append(key)

            money = {
                'Spent': np.array(spend_list),
                'Budget Left': np.array(budget_list),
            }

            if start_date.month == end_date.month and start_date.year == end_date.year:
                title = f'Budgeting & Spending by Account for {start_date}'
            else:
                start_date = start_date.strftime('%m-%d-%Y')
                end_date = end_date.strftime('%m-%d-%Y')
                title = f'Monthly Avg. Budgeting & Spending by Account from {start_date} to {end_date}'

            flag = makeBarGraph(np, plt, i, title, money, accounts)

    elif chart == 'Bar Graph - Category Budgeting & Spending':
        event, values = selWin(sg, acc_menu, 'account').read(close=True)
        account = values['-Selection-'] 
        if event == 'Go' and account:
            cat_spending = categorySpending(c, account, start_date, end_date)
            cat_budget = categoryBudget(c, account, start_date, end_date)
            if cat_budget:
                spend_list = []
                budget_list = []
                categories = []

                # Total months difference
                total_months = None
                # If timeframe == max give a start and end date
                if not (start_date and end_date):
                    c.execute("SELECT date FROM transactions ORDER BY date ASC")
                    start_date = c.fetchone()
                    if start_date:
                        start_date = start_date[0]
                        start_date = datetime.strptime(start_date, '%Y-%m-%d')
                        end_date = today
                    else: 
                        flag == -1
                if start_date and end_date and not (start_date.month == end_date.month and start_date.year == end_date.year):
                    year_diff = end_date.year - start_date.year
                    month_diff = end_date.month - start_date.month
                    total_months = year_diff * 12 + month_diff
               
                for i, key in enumerate(cat_budget, 1):
                    try:
                        if total_months:
                            spend_list.append(round(cat_spending[key] / total_months, 2))
                            budget_list.append(round((cat_budget[key] - cat_spending[key]) / total_months, 2))
                        else:
                            spend_list.append(cat_spending[key])
                            budget_list.append(cat_budget[key] - cat_spending[key])
                    except KeyError:
                        if total_months:
                            budget_list.append(round(cat_budget[key] / total_months, 2))
                        else:
                            budget_list.append(cat_budget[key])
                        spend_list.append(0)
                    categories.append(key)

                money = {
                    'Spent': np.array(spend_list),
                    'Budget Left': np.array(budget_list),
                }

                if start_date.month == end_date.month and start_date.year == end_date.year:
                    title = f'Category Budgeting & Spending for {start_date}'
                else:
                    start_date = start_date.strftime('%m-%d-%Y')
                    end_date = end_date.strftime('%m-%d-%Y')
                    title = f'Monthly Avg. Category Budgeting & Spending from {start_date} to {end_date}'

                flag = makeBarGraph(np, plt, i, title, money, categories)

    elif chart == "Bar Graph - Saving's Earnings & Deposits":
        # Add in average if given a time frame
        saving_acc_deposit = savingsDeposit(c, start_date, end_date)
        saving_acc_price = savingAccountPrice(c, end=end_date)
        if saving_acc_deposit:
            deposit_list = []
            earnings_list = []
            accounts = []

            # Total months difference
            total_months = None
            # If timeframe == max give a start and end date
            if not (start_date and end_date):
                c.execute("SELECT date FROM transactions ORDER BY date ASC")
                start_date = c.fetchone()
                if start_date:
                    start_date = start_date[0]
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = today
                else: 
                    flag == -1
            if start_date and end_date and not (start_date.month == end_date.month and start_date.year == end_date.year):
                year_diff = end_date.year - start_date.year
                month_diff = end_date.month - start_date.month
                total_months = year_diff * 12 + month_diff

        for i, key in enumerate(saving_acc_deposit, 1):
            if total_months:
                deposit_list.append(round(saving_acc_deposit[key] / total_months, 2))
            else:
                deposit_list.append(saving_acc_deposit[key])
            try:
                if total_months:
                    earnings_list.append(round((saving_acc_price[key] - saving_acc_deposit[key]) / total_months, 2))
                else:
                    earnings_list.append(saving_acc_price[key] - saving_acc_deposit[key])
            except KeyError:
                earnings_list.append(0)
            accounts.append(key)
        data = {
            'Deposit Amount': np.array(deposit_list),
            'Earnings': np.array(earnings_list)
        }
        if not (start_date or end_date):
            title = 'Monthly Avg. Saving Account Deposit & Total Earnings'
        else:
            start_date = start_date.strftime('%m-%d-%Y')
            end_date = end_date.strftime('%m-%d-%Y')
            title = f'Monthly Avg. Saving Account Deposit & Total Earnings from {start_date} to {end_date}'

        flag = makeBarGraph(np, plt, i, title, data, accounts)

    elif chart == 'Line Graph - Total Savings':
        # TODO: Needs to have a track_savings DB
        pass
    elif chart == 'Line Graph - Total Wants Spending':
        wants_spend = accountSpending(c, start_date, end_date, ('spending',), 'date')
        flag = makeLineChart(c, plt, 'USD ($)', 'Total Wants Spending', wants_spend, 'Wants', start_date, end_date, timeframe)

    elif chart == 'Line Graph - Total Needs Spending':
        needs_spend = accountSpending(c, start_date, end_date, ('bills',), 'date')
        flag = makeLineChart(c, plt, 'USD ($)', 'Total Needs Spending', needs_spend, 'Needs', start_date, end_date, timeframe)

    elif chart == 'Line Graph - Total Account Spending':
        # Get user input
        event, values = selWin(sg, acc_menu, 'account').read(close=True)
        account = values['-Selection-']
        # Check user input
        c.execute("SELECT name FROM accounts")
        all_accounts = c.fetchall()
        if (account,) in all_accounts:
            # Find graph's data
            acc_spend = accountSpending(c, start_date, end_date, ('bills','spending'), 'date', account)
            # Make graph
            flag = makeLineChart(c, plt, 'USD ($)', f'Total {account} Spending', acc_spend, account, start_date, end_date, timeframe)
    
    elif chart == 'Line Graph - Total Category Spending':
        # Get user input
        event, values = selWin(sg, acc_menu, 'account').read(close=True)
        account = values['-Selection-']
        # Check user input
        c.execute("SELECT name FROM accounts")
        all_accounts = c.fetchall()
        if (account,) in all_accounts:
            # Get more user input
            cat_menu = makeCategoryMenu(conn, c, account, True)
            event, values = selWin(sg, cat_menu, 'category').read(close=True)
            category = values['-Selection-']
            c.execute("SELECT id FROM categories WHERE name=:name AND account=:account", 
                      {'name': category, 'account': account})
            category_id = c.fetchone()
            if category_id:
                category_id = category_id[0]
                # Find graph's data
                cat_spend = categorySpending(c, account, start_date, end_date, category_id, 'date')
                # Make graph
                flag = makeLineChart(c, plt, 'USD ($)', f'Total {category} Spending', cat_spend, category, start_date, end_date, timeframe)
    return flag

def accountSpending(c, start, end, include_type=('spending', 'bills'), key_type='account', account='all'):
    acc_spending = {}

    if account == 'all':
        c.execute("SELECT date, total, account, notes FROM transactions")
    else:
        c.execute("""SELECT date, total, account, notes FROM transactions 
                  WHERE account=:account""", {'account': account})
    for date, total, acc, notes in c.fetchall():
        date_obj = datetime.strptime(date, '%Y-%m-%d')    
        if key_type == 'account':
            key = acc
        else:
            date = date_obj.strftime('%m-%Y')
            key = date
        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': acc})
        acc_type = c.fetchone()
        if acc_type and total < 0 and notes != 'TRANSFER':
            acc_type = acc_type[0]
            if acc_type in include_type:
                if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
                    if acc in acc_spending:
                        acc_spending[key] -= total
                    else:
                        acc_spending[key] = 0 - total

    return acc_spending


def accountTotal(c, start, end, include_type=('spending', 'bills')):
    acc_total = {}
    c.execute("SELECT date, total, account FROM transactions")
    for date, total, acc in c.fetchall():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': acc})
        acc_type = c.fetchone()
        if acc_type:
            acc_type = acc_type[0]
            if acc_type in include_type:
                if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
                    if acc in acc_total:
                        acc_total[acc] += total
                    else:
                        acc_total[acc] = 0 + total
    return acc_total

def categorySpending(c, account, start, end, given_id=None, key_type='category'):
    cat_spending = {}
    if not given_id:
        c.execute("SELECT total, category_id, date FROM transactions WHERE account=:account", {'account': account})
    else:
        c.execute("SELECT total, category_id, date FROM transactions WHERE account=:account AND category_id=:cat_id", 
                  {'account': account, 'cat_id': given_id})
    for total, cat_id, date in c.fetchall():
        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': account})
        acc_type = c.fetchone()        
        if acc_type and total < 0:
            acc_type = acc_type[0]
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if acc_type in ('bills', 'spending'):
                if key_type == 'category':
                    c.execute("SELECT name FROM categories WHERE id=:id", {'id': cat_id})
                    cat_name = c.fetchone()
                    if cat_name and cat_name[0] != 'Unallocated Cash':
                        key = cat_name[0]
                    else:
                        key = None
                else:
                    
                    date = date_obj.strftime('%m-%Y')
                    key = date
                if key:
                    if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
                        if key in cat_spending:
                            cat_spending[key] -= total
                        else:
                            cat_spending[key] = 0 - total
    return cat_spending

def categoryBudget(c, account, start, end):
    cat_budget = {}
    c.execute("SELECT date, total, category_id FROM track_categories WHERE account=:account", {'account': account})
    for date, total, cat_id in c.fetchall():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        c.execute("SELECT type FROM accounts WHERE name=:name", {'name': account})
        acc_type = c.fetchone()        
        if acc_type:
            acc_type = acc_type[0]
            if acc_type in ('bills', 'spending'):
                c.execute("SELECT name FROM categories WHERE id=:id", {'id': cat_id})
                cat_name = c.fetchone()
                if cat_name:
                    cat_name = cat_name[0]
                    if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
                        if cat_name in cat_budget and cat_name != 'Unallocated Cash':
                            cat_budget[cat_name] += total
                        else:
                            cat_budget[cat_name] = 0 + total
    return cat_budget

def savingsDeposit(c, start, end):
    acc_deposit = {}
    c.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'savings'})
    saving_accounts = c.fetchall()
    for account in saving_accounts:
        account = account[0]
        acc_deposit[account] = 0
        c.execute("SELECT total, date FROM transactions WHERE account=:account", {'account': account})
        deposits = c.fetchall()
        for deposit, date in deposits:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
                acc_deposit[account] += deposit
    return acc_deposit

def savingAccountPrice(c, start=None, end=None, key_type='name'):
    acc_price = {}
    c.execute("SELECT name FROM savings")
    for name in c.fetchall():
        name=name[0]
        if key_type == 'name':
            key = name
            if not end:
                end = datetime.now()
            c.execute("SELECT amount FROM track_savings WHERE account=:account AND date<=:end ORDER BY date DESC",
                      {'end': end, 'account': name})
            price =  c.fetchone()
            if price:
                acc_price[key] = price[0]
            else:
                acc_price[key] = 0
        # date_obj = datetime.strptime(date, '%Y-%m-%d')
        # acc_price[key] = price
        # if (start == None and end == None) or ((start <= date_obj) and (end >= date_obj)):
        #     if name in acc_price:
        #         acc_price[key] += price
        #     else:
        #         acc_price[key] = 0 + price
    return acc_price

def fillInData(data, start_date, end_date):
    if data and start_date and end_date:
        check_date_obj = start_date
        end_date = end_date.strftime('%m-%Y')
        check_date = check_date_obj.strftime('%m-%Y')
        while check_date != end_date:
            check_date = check_date_obj.strftime('%m-%Y')
            if check_date not in data:
                data[check_date] = 0
            check_date_obj += relativedelta(months=1)
        
    return data

def makePieChart(plt, x, labels, title, colors=None):
    if x:
        plt.style.use('_mpl-gallery-nogrid')
        _, ax = plt.subplots()
        ax.pie(x, labels=labels, colors=colors, radius=10, center=(20, 20), 
                wedgeprops={"linewidth": 1, "edgecolor": "white"}, labeldistance=1.3)
        ax.set(xlim=(0,40), xticks=[0,40], ylim=(0, 40), yticks=[0,40])
        ax.set_title(title)
        return 1
    else:
        return -1

def makeBarGraph(np, plt, N, title, data, x_labels):
    if data:        
        width = 0.6  

        _, ax = plt.subplots()
        bottom = np.zeros(N)

        for labels, amount in data.items():
            p = ax.bar(x_labels, amount, width, label=labels, bottom=bottom)
            bottom += amount

            ax.bar_label(p, label_type='center')

        ax.set_title(title)
        ax.legend()
        return 1
    else:
        return -1

def makeLineChart(c, plt, y_label, title, data, key, start_date, end_date, timeframe='total'):
    if data:
        # Initializing data
        date_list = []
        y_list = []
        today = datetime.now()
        
        ### Prepping Data ###        
        # Max timeframe uses 1 year start and end dates for line graphs, if not > 1 year
        if start_date == None or end_date == None or start_date == end_date:
            c.execute("SELECT date FROM transactions ORDER BY date ASC")
            start_date = c.fetchone()
            one_year_start = today - relativedelta(years=10)
            end_date = today
            if start_date:
                start_date = start_date[0]
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                if (end_date - start_date) > (end_date - one_year_start):
                    start_date = one_year_start
            else:
                start_date = one_year_start
            
        data = fillInData(data, start_date, end_date)
        # Turn dictionary into two list
        for date, amount in data.items():
            date_list.append(date)
            y_list.append(amount)
        # Text to date obj
        dates = [datetime.strptime(date, "%m-%Y") for date in date_list]
        # Sort both lists based on date_list
        dates, y_list = zip(*sorted(zip(dates, y_list)))

        # Convert the results back to lists
        dates = list(dates)
        y_list = list(y_list)

        # Create a figure and axis
        _, ax = plt.subplots()

        # Plot the data
        ax.plot(dates, y_list, marker=None, label=key)

        # Format the x-axis for dates
        ax.xaxis.set_major_formatter(DateFormatter("%m-%Y"))

        # Rotate date labels for better readability
        plt.xticks(rotation=45)
        if len(dates) < 12:
            ax.set_xticks(dates)

        # Add labels, title, and legend
        ax.set_xlabel("Date")
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.legend()

        # Add grid for better visualization
        ax.grid(True)
        return 1
    else:
        return -1
