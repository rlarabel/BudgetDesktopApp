from datetime import datetime
import numpy_financial as npf


def makeSavingsSheet(conn, cursor, pov):
    with conn:
        table = []
        
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
            
            amount = getRealAmount(cursor, name, pov)
            month_deposit, total_deposit, actual_apy, i_amount, total_i = calcSavingsData(cursor, pov, name, amount)
            table.append([name, month_deposit, total_deposit, amount, desired_apy, actual_apy, i_amount, total_i])
        if not table:
            return [['','','','','', '', '']]
        else:
            return table

def calcSavingsData(cursor, pov, name, real_value):
    total_deposit = 0
    month_deposit = 0
    actual_apy = 0 
    i_amount = 0 
    total_i = 0
    n_years = 0
    oldest_date = None

    cursor.execute("SELECT date, total FROM transactions WHERE account=:account AND date<:date", 
                   {'account': name, 'date': pov.getNextMonthStr()})
    for date, total in cursor.fetchall():
        date = datetime.strptime(date, '%Y-%m-%d')

        # Find the total deposit amount and the current viewing month's deposit amount
        total_deposit += total
        if date.month == pov.getViewDate().month and date.year == pov.getViewDate().year: 
            month_deposit += total

        # Find the oldest date to calc number of years
        if not oldest_date:
            oldest_date = date
        elif oldest_date > date:
            oldest_date = date
    if oldest_date:
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
            
def makeAssetSheet(conn, cursor):
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'asset'})
        asset_accounts = cursor.fetchall()
        for account in asset_accounts:
            name = account[0]
            cursor.execute("SELECT initial_amount FROM assets WHERE name=:name", {'name': name})
            amt = cursor.fetchone()[0]
            pw1, pw2 = calcAssetData(cursor, name)
            table.append([name, amt, pw1, pw2])
    if table:
        return table
    else:
        return [['','','','']]

def getRealAmount(cursor, name, pov):
    # Select this months real value if there is one
    cursor.execute("SELECT amount FROM track_savings WHERE account=:account AND date=:date",
                    {'account': name, 'date': pov.getViewDateStr()})
    amount = cursor.fetchone()
    if amount:
        amount = amount[0]
    else:
        # Select the last months real value if there is one
        cursor.execute("SELECT amount FROM track_savings WHERE account=:account AND date<=:date ORDER BY date DESC",
                    {'account': name, 'date': pov.getViewDateStr()})
        amount = cursor.fetchone()
        if amount:
            amount = amount[0]
        else:
            # Select the total deposit amount if nothing
            cursor.execute("SELECT total FROM transactions WHERE account=:account AND date<:date",
                           {'account': name, 'date': pov.getNextMonthStr()})
            transactions = cursor.fetchall()
            amount = 0
            if transactions:
                for trans in transactions:
                    amount += trans[0]
    return amount


def calcAssetData(cursor, name):
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

def makeLoanSheet(conn, cursor):
    with conn:
        table = []

        cursor.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'loan'})

        for account in cursor.fetchall():
            name = account[0]
            cursor.execute("SELECT interest, end_date, present_amt FROM loans WHERE name=:name", {'name': name})
            interest, end_date, present_loan_amount = cursor.fetchone()
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            initial_loan_amt, monthly_pmt = calculateLoanData(cursor, name, interest, end_date, present_loan_amount)
            table.append([name, initial_loan_amt, present_loan_amount, interest, end_date.strftime('%m-%d-%Y'), monthly_pmt])
        if table:
            return table
        else:
            return [['','','','','','']]

def calculateLoanData(cursor, name, interest, end_date, present_loan_amount):
    cursor.execute("SELECT initial_amount, start_date FROM loans WHERE name=:name", {"name": name})
    initial_loan_amt = cursor.fetchone()[0]

    delta = end_date - datetime.today()
    n_months = (delta.days / 365.25) * 12
    monthly_pmt = npf.pmt(interest / (100 * 12), n_months, present_loan_amount, 0)
    return initial_loan_amt, round(monthly_pmt, 2)
