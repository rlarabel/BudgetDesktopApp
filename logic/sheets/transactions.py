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

def makeTransferSheet(conn, cursor):
    with conn:
        table = []
        row_color = []
        matched_id = []
        i = 0
        
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        all_transactions = cursor.fetchall()
        for transaction in all_transactions:
            transfer_match = False
            id_num, db_date, payee, notes, total, account, category_id = transaction
            date = datetime.strptime(db_date, '%Y-%m-%d')
            date = date.strftime('%m-%d-%Y')
            cursor.execute("SELECT name FROM categories WHERE id=:category_id", {'category_id': category_id})
            db_category_name = cursor.fetchone()[0]
            if db_category_name == 'Unallocated Cash' or db_category_name == 'Not Available':
                category_name = '-'
            else:
                category_name = db_category_name 
            if notes != 'TRANSFER':
                # Search db for matching transaction in opposite amount, if one found mark yellow
                cursor.execute("""
                            SELECT t.id 
                            FROM transactions t
                            JOIN categories c ON t.category_id = c.id
                            WHERE t.total>=:total-0.01 AND t.total<=:total+0.01 
                            AND t.date=:date AND t.account<>:account AND c.name=:category_name
                            """,
                            {'total': -total, 'date': db_date, 'account': account, 'category_name': db_category_name}
                )
                transfer_match = cursor.fetchone()
                if transfer_match:
                    ordered_transaction = [id_num, date, account, category_name, payee, notes, total]
                    table.append(ordered_transaction)
                    row_color.append((i, 'navy blue', 'yellow'))
                    i += 1
            else:
                # Match all transaction with note TRANSFER, if cannot match mark red
                transfer_match, matched_id = matchTransfers(cursor, id_num, matched_id, total, db_date, account, db_category_name)
                
                if not transfer_match:
                    row_color.append((i, 'navy blue', 'red'))
                else:
                    if(i % 2 == 0):
                        row_color.append((i, 'white', '#7f8f9f'))
                ordered_transaction = [id_num, date, account, category_name, payee, notes, total]
                table.append(ordered_transaction)
                i += 1

        if not table:
            table = [['', '', '', '', '', '', '']]
        return table, row_color


def matchTransfers(cursor, id_num, matched_id, total, db_date, account, db_category_name):
    #TODO: Find error
    transfer_match = False
    # Transfer need to be in unallocated cash for budget accounts
    if not (db_category_name == 'Unallocated Cash' or db_category_name == 'Not Available'):
        transfer_match = False
    elif id_num in matched_id:
        transfer_match = True
    else:
        cursor.execute("""
                    SELECT t.id 
                    FROM transactions t 
                    JOIN categories c ON t.category_id = c.id
                    WHERE t.total>=:total-0.01 AND t.total<=:total+0.01 
                    AND t.date=:date AND t.account<>:account 
                    AND (c.name='Unallocated Cash' OR c.name='Not Available')
                    """,
                    {'total': -total, 'date': db_date, 'account': account}
        )
        possible_matches = cursor.fetchall()
        j = 0
        while (not transfer_match) and len(possible_matches) > j:
            if possible_matches[j][0] not in matched_id:
                matched_id.append(id_num)
                matched_id.append(possible_matches[j][0])
                transfer_match = True
            j += 1
    return transfer_match, matched_id