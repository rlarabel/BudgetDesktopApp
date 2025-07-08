def delete_account(conn, cursor, new_account, old_account):
	# Update 'Unallocated Cash' categort's ID in transactions and track_categories tables and delete in categories table 
    category = 'Unallocated Cash'
    cursor.execute("SELECT id FROM categories WHERE account=:account AND name=:name", 
                    {'account': new_account, 'name': category})
    new_cat_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM categories WHERE account=:account AND name=:name", 
                    {'account': old_account, 'name': category})
    old_cat_id = cursor.fetchone()[0]
    cursor.execute("UPDATE track_categories SET category_id=:new_category WHERE category_id=:old_category",
                    {'new_category': new_cat_id, 'old_category': old_cat_id})
    cursor.execute("UPDATE transactions SET category_id=:new_category WHERE category_id=:old_category",
                 {'new_category': new_cat_id, 'old_category': old_cat_id})
    cursor.execute("DELETE FROM categories WHERE id=:old_category", {'old_category': old_cat_id})
                 
    # Update old accounts name in transactions, track_categories, and categories tables and delete in accounts table 
    cursor.execute("UPDATE track_categories SET account=:new_account WHERE account=:old_account",
                 {'new_account': new_account, 'old_account': old_account})
    cursor.execute("UPDATE transactions SET account=:new_account WHERE account=:old_account",
                 {'new_account': new_account, 'old_account': old_account})
    cursor.execute("UPDATE categories SET account=:new_account WHERE account=:old_account",
                 {'new_account': new_account, 'old_account': old_account})
    cursor.execute("DELETE FROM accounts WHERE name=:old_account", {'old_account': old_account})
    conn.commit()


def delete_category(conn, cursor, new_category, account, cat_id):
    new_cat_id = None
    cursor.execute('SELECT id FROM categories WHERE account=:account AND name=:name', {'name': new_category, 'account': account})
    new_cat_id = cursor.fetchone()[0]
    
    if new_cat_id:
        cursor.execute("""UPDATE track_categories SET category_id=:new_cat_id
                 WHERE category_id=:old_cat_id AND account=:account""",
                 {'account': account, 'new_cat_id': new_cat_id, 'old_cat_id': cat_id})
        cursor.execute("""UPDATE transactions SET category_id=:new_cat_id
                 WHERE category_id=:old_cat_id AND account=:account""",
                 {'account': account, 'new_cat_id': new_cat_id, 'old_cat_id': cat_id})
        cursor.execute("DELETE FROM categories WHERE id=:old_cat_id", {'old_cat_id': cat_id})
        conn.commit()
