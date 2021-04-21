
def update_account_funds(cursor, update_account):
    update_row = {
        'variable': update_account[0],
        'total': update_account[2]
    }
    cursor.execute("""UPDATE account SET total = :total
                                    WHERE variable =:variable""", update_row)


def update_category_funds(cursor, update_category):
    update_row = {
        'variable': update_category[0],
        'money': update_category[2]
    }
    cursor.execute("""UPDATE category SET money = :money
                                WHERE variable =:variable""", update_row)
