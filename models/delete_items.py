def delete_account(conn, cursor, transfer_name, old_name):
    with conn:
        cursor.execute("UPDATE money_flow SET account=:selected_account WHERE account=:old_account",
                       {'selected_account': transfer_name, 'old_account': old_name})
        cursor.execute("UPDATE category SET trackaccount=:selected_account WHERE trackaccount=:old_account",
                       {'selected_account': transfer_name, 'old_account': old_name})
        cursor.execute("SELECT * FROM track_categories WHERE account=:old_account",
                       {'old_account': old_name})
        for old_transaction in cursor.fetchall():
            date = old_transaction[0]
            cursor.execute("""SELECT * FROM track_categories 
                            WHERE account=:selected_account AND date=:date AND category=:category""",
                           {'selected_account': transfer_name, 'date': date, 'category': old_transaction[3]})
            transfer_exist = cursor.fetchone()
            if transfer_exist:
                new_total = old_transaction[1] + transfer_exist[1]
                cursor.execute("""UPDATE track_categories SET total=:total 
                                WHERE account=:new_account AND date=:date AND category=:category""",
                               {'total': new_total, 'new_account': transfer_name,
                                'date': date, 'category': old_transaction[3]})
                cursor.execute("""DELETE FROM track_categories
                                                        WHERE account=:account AND date=:date AND category=:category""",
                               {'account': old_name, 'date': date, 'category': old_transaction[3]})
            else:
                cursor.execute("""UPDATE track_categories SET account=:selected_account 
                                WHERE account=:old_account AND date=:date AND category=:category""",
                               {'date': date, 'selected_account': transfer_name,
                                'old_account': old_transaction[2], 'category': old_transaction[3]})
        conn.commit()
        cursor.execute("DELETE FROM account WHERE name=:old_account", {'old_account': old_name})
        conn.commit()


def delete_category(conn, cursor, transfer_name, old_info):
    with conn:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""SELECT * FROM category WHERE name=:name""", {'name': transfer_name})
        new_info = cursor.fetchone()
        if new_info:
            cursor.execute("""UPDATE money_flow SET account=:selected_account, category=:selected_category 
                                    WHERE account=:old_account AND category=:old_category""",
                           {'selected_category': transfer_name, 'selected_account': new_info[2],
                            'old_category': old_info[0], 'old_account': old_info[2]})
            cursor.execute("SELECT * FROM track_categories WHERE account=:old_account AND category=:old_category",
                           {'old_account': old_info[2], 'old_category': old_info[0]})
            # Every transaction is stripped from old and placed in the new category
            for old_transaction in cursor.fetchall():
                date = old_transaction[0]
                cursor.execute("""SELECT * FROM track_categories 
                                WHERE account=:selected_account AND date=:date AND category=:selected_category""",
                               {'selected_account': new_info[2], 'date': date, 'selected_category': transfer_name})
                transfer_exist = cursor.fetchone()
                # an existing transaction will only change in total and the other concurrent will be deleted
                if transfer_exist:
                    new_total = old_transaction[1] + transfer_exist[1]
                    cursor.execute("""UPDATE track_categories SET total=:total 
                                    WHERE account=:account AND date=:date AND category=:category""",
                                   {'total': new_total, 'account': new_info[2],
                                    'date': date, 'category': transfer_name})
                    cursor.execute("""DELETE FROM track_categories
                                        WHERE account=:account AND date=:date AND category=:category""",
                                   {'account': old_info[2], 'date': date, 'category': old_info[0]})
                else:
                    cursor.execute("""UPDATE track_categories SET account=:selected_account, category=:selected_category 
                                    WHERE account=:old_account AND date=:date AND category=:category""",
                                   {'date': date, 'selected_account': new_info[2], 'selected_category': transfer_name,
                                    'old_account': old_info[2], 'category': old_info[0]})
            cursor.execute("DELETE FROM category WHERE name=:old_category", {'old_category': old_info[0]})
            conn.commit()
