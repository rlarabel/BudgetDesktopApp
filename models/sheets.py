from datetime import datetime
from itertools import zip_longest


def make_track_sheet(conn, cursor, track_date, months):
    with conn:
        cursor.execute("SELECT * FROM account ORDER BY type=:type", {'type': 'track'})
        table = []
        for account in cursor.fetchall():
            # adds account total to table
            cursor.execute("SELECT * FROM track_categories WHERE account=:name", {'name': account[0]})
            track_internal = cursor.fetchall()
            cursor.execute("SELECT * FROM money_flow WHERE account=:name", {'name': account[0]})
            external_income = cursor.fetchall()
            account_monthly, _, _, funded_total = get_monthly_total(track_internal, external_income, track_date)

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
        cursor.execute("SELECT * FROM account WHERE type=:type", {'type': 'budget'})
        table = []
        for account in cursor.fetchall():
            # Finds the account name
            cursor.execute("SELECT * FROM category WHERE trackaccount=:name", {'name': account[0]})
            all_categories = cursor.fetchall()

            # adds account total to table
            cursor.execute("SELECT * FROM track_categories WHERE account=:name", {'name': account[0]})
            account_incomes = cursor.fetchall()
            cursor.execute("SELECT * FROM money_flow WHERE account=:name", {'name': account[0]})
            account_outcomes = cursor.fetchall()
            _, _, account_total, _ = get_monthly_total(account_incomes, account_outcomes, budget_date)

            table.append([account[0], '', '', '', '', str(round(account_total, 2))])

            for category in all_categories:
                cursor.execute("SELECT * FROM track_categories WHERE category=:name", {'name': category[0]})
                category_incomes = cursor.fetchall()
                cursor.execute("SELECT * FROM money_flow WHERE category=:name", {'name': category[0]})
                category_outcomes = cursor.fetchall()
                month_budget, month_spending, category_total, _ = get_monthly_total(category_incomes, category_outcomes,
                                                                                    budget_date)
                month_progress = '-'
                if category[1]:
                    month_progress = round((month_budget / category[1]) * 100)
                    month_progress = str(month_progress) + '%'

                month_budget = round(month_budget, 2)
                month_spending = round(month_spending, 2)
                category_total = round(category_total, 2)
                set_budget = '-'
                if category[1]:
                    set_budget = str(category[1])

                table.append([category[0], set_budget, str(month_budget), month_progress, str(month_spending),
                              str(category_total)])
        if not table:
            table = [['', '', '', '', '', '']]

        return table


def get_monthly_total(incomes, outcomes, user_date):
    total = 0
    budget = 0
    spending = 0
    final_total = 0

    user_year, user_month = user_date.split('-')
    user_year = int(user_year)
    user_month = int(user_month)
    if user_month == 12:
        next_month = 1
        next_year = user_year + 1
    else:
        next_month = user_month + 1
        next_year = user_year

    for income, outcome in zip_longest(incomes, outcomes, fillvalue=0):
        if income:
            income_date = income[0]
            income_year, income_month = income_date.split('-')
            income_year = int(income_year)
            income_month = int(income_month)

            final_total += income[1]

            if datetime(datetime.now().year, datetime.now().month, 1) <= datetime(user_year, user_month, 1):
                if datetime(next_year, next_month, 1) > datetime(income_year, income_month, 1):
                    total += income[1]
            if datetime(datetime.now().year, datetime.now().month, 1) == datetime(user_year, user_month, 1):
                if datetime(next_year, next_month, 1) > datetime(income_year, income_month, 1):
                    budget += income[1]
            elif datetime(datetime.now().year, datetime.now().month, 1) < datetime(user_year, user_month, 1):
                if datetime(user_year, user_month, 1) == datetime(income_year, income_month, 1):
                    budget += income[1]

        if outcome:
            outcome_date = outcome[1]
            outcome_year, outcome_month, _ = outcome_date.split('-')
            outcome_year = int(outcome_year)
            outcome_month = int(outcome_month)

            final_total -= outcome[4]

            if datetime(next_year, next_month, 1) > datetime(outcome_year, outcome_month, 1):
                total -= outcome[4]
            if datetime(datetime.now().year, datetime.now().month, 1) == datetime(user_year, user_month, 1):
                if datetime(user_year, user_month, 1) > datetime(outcome_year, outcome_month, 1):
                    budget -= outcome[4]
            if datetime(user_year, user_month, 1) == datetime(outcome_year, outcome_month, 1):
                spending += outcome[4]

    return budget, spending, total, final_total


def set_row_colors(conn, cursor):
    with conn:
        account_color = []
        i = 0
        cursor.execute("SELECT * FROM account WHERE type=:type", {'type': 'budget'})
        for account in cursor.fetchall():
            account_color.append((i, 'navy blue', 'grey'))
            i += 1
            cursor.execute("SELECT * FROM category WHERE trackaccount=:name", {'name': account[0]})
            for _ in cursor.fetchall():
                i += 1

        return account_color


def set_track_row_colors(conn, cursor):
    with conn:
        account_color = []
        cursor.execute("SELECT * FROM account WHERE type=:type", {'type': 'budget'})
        for i, account in enumerate(cursor.fetchall()):
            account_color.append((i, 'navy blue', 'grey'))

        return account_color


def make_transaction_sheet(conn, cursor):
    with conn:
        table = []
        cursor.execute("SELECT * FROM money_flow ORDER BY date DESC")
        all_transactions = cursor.fetchall()
        for transaction in all_transactions:
            transaction = [transaction[0], transaction[1], transaction[6], transaction[7], transaction[2],
                           transaction[3], transaction[5], transaction[4]]
            table.append(transaction)
        if not table:
            table = [['', '', '', '', '', '', '', '']]
        return table
