from datetime import datetime


def makeTransactionSheet(conn, cursor):
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
    

def setTransactionRowColors(conn, cursor):
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
