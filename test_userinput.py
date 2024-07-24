import os
import sqlite3
from models.make_db import create_db_tables
from models.create_items import add_new_account, add_new_category, add_transaction
from models.delete_items import delete_account, delete_category


# TODO: Connect to test db
def connect_to_db():
    test_db = 'test_app.db'
    if os.path.isfile(test_db):
        os.remove(test_db)
    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    create_db_tables(conn, c)
    return c, conn

class TestClass:
    c, conn = connect_to_db()

############################## Test functions in create_items.py #######################################
### Function not tested: make_total_funds, make_category_menu, make_account_menu
    def test_add_new_account(self):
        add_new_account(self.conn, self.c, ['test_acc_1', 'spending'])
        self.c.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'spending'})
        name = self.c.fetchone()[0]
        assert name == 'test_acc_1'

    def test_add_new_category_success(self):
        add_new_account(self.conn, self.c, ['test_acc_2', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_2', '-Account name-': 'test_acc_2'}, 10)
        self.c.execute("SELECT name FROM categories WHERE id=:id", {'id': 10})
        name = self.c.fetchone()[0]
        assert name == 'test_cat_2'
    
    def test_add_new_category_dup(self):
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_2.11', '-Account name-': 'invalid_acc'}, 14)
        self.c.execute("SELECT id FROM categories WHERE name=:name", {'name': 'test_cat_2.11'})
        assert self.c.fetchone() == False

    # Can not add two categories with the same name under the same account even if different ids
    def test_add_new_category_dup(self):
        dup_flag = False
        add_new_account(self.conn, self.c, ['test_acc_2.1', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_2.1', '-Account name-': 'test_acc_2.1'}, 15)
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_2.1', '-Account name-': 'test_acc_2.1'}, 16)
        self.c.execute("SELECT id FROM categories WHERE name=:name", {'name': 'test_cat_2.1'})
        for i, id in enumerate(self.c.fetchall()):
            print(id[0])
            print(i)
            if id[0] != 15:
                dup_flag = True
            if i > 0:
                dup_flag = True
        assert dup_flag == False

    def test_add_transaction_success_outcome(self):
        add_new_account(self.conn, self.c, ['test_acc_3', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_3', '-Account name-': 'test_acc_3'}, 20)
        values = {'-Year-': '2024', '-Month-': '7', '-Day-': '14', '-Selected Category-': 'test_cat_3', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_3', 1)
        self.c.execute("SELECT id, category_id, account, total FROM transactions WHERE id=:id", {'id': 1})
        id, cat_id, account, total = self.c.fetchone()
        assert id == 1 and cat_id == 20 and account == 'test_acc_3' and total < -5.54 and total > -5.56

    def test_add_transaction_success_income(self):
        add_new_account(self.conn, self.c, ['test_acc_3.11', 'spending'])
        # User interface can select any category, even though the desired category is unallocated cash
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_3.11', '-Account name-': 'test_acc_3.11'}, 60)
        values = {'-Year-': '2024', '-Month-': '7', '-Day-': '14', '-Selected Category-': 'test_cat_3.11', '-Notes-': None, '-Payee-': None, '-Trans total-': '5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_3.11', 5)
        self.c.execute("SELECT id, category_id, total FROM transactions WHERE id=:id", {'id': 5})
        id, cat_id, total = self.c.fetchone()
        self.c.execute("SELECT name, account FROM categories WHERE id=:id", {'id': cat_id})
        cat, acc = self.c.fetchone()
        assert id == 5 and cat == 'Unallocated Cash' and acc == 'test_acc_3.11' and total > 5.54 and total < 5.56

    def test_add_transaction_invalid_year(self):
        add_new_account(self.conn, self.c, ['test_acc_3.1', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_3.1', '-Account name-': 'test_acc_3.1'}, 30)
        values = {'-Year-': '22024', '-Month-': '7', '-Day-': '14', '-Selected Category-': 'test_cat_3.1', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_3.1', 2)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 2})
        id = self.c.fetchone()
        assert id == None    

    def test_add_transaction_invalid_month(self):
        add_new_account(self.conn, self.c, ['test_acc_3.2', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_3.2', '-Account name-': 'test_acc_3.2'}, 40)
        values = {'-Year-': '2024', '-Month-': '14', '-Day-': '14', '-Selected Category-': 'test_cat_3.2', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_3.2', 3)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 3})
        id = self.c.fetchone()
        assert id == None

    def test_add_transaction_invalid_day(self):
        add_new_account(self.conn, self.c, ['test_acc_3.3', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'test_cat_3.3', '-Account name-': 'test_acc_3.3'}, 50)
        values = {'-Year-': '2024', '-Month-': '7', '-Day-': '32', '-Selected Category-': 'test_cat_3.3', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_3.3', 4)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 4})
        id = self.c.fetchone()
        assert id == None

########################################################################################################

############################## Test functions in delete_items.py #######################################
    # TODO: add track_categories
    def test_delete_account(self):
        # Set up a detailed account to try to delete it
        deleted_account = None  
        add_new_account(self.conn, self.c, ['delete_acc', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'delete_cat', '-Account name-': 'delete_acc'}, 70)
        values = {'-Year-': '2024', '-Month-': '7', '-Day-': '14', '-Selected Category-': 'delete_cat', '-Notes-': None, '-Payee-': None, '-Trans total-': '50'}
        add_transaction(self.conn, self.c, values, 'delete_acc', 6)
        add_new_account(self.conn, self.c, ['move_acc', 'spending'])
        delete_account(self.conn, self.c, 'move_acc', 'delete_acc')
        # Check all db necessary for delete_acc
        self.c.execute("SELECT * FROM accounts WHERE name=:name", {'name': 'delete_acc'})
        if self.c.fetchone(): 
            deleted_account = 1
        self.c.execute("SELECT * FROM categories WHERE account=:account", {'account': 'delete_acc'})
        if self.c.fetchone(): 
            deleted_account = 1
        self.c.execute("SELECT * FROM transactions WHERE account=:account", {'account': 'delete_acc'})
        if self.c.fetchone(): 
            deleted_account = 1
        self.c.execute("SELECT account FROM transactions WHERE id=:id", {'id': 6})
        trans_account = self.c.fetchone()[0]
        self.c.execute("SELECT account FROM categories WHERE id=:id", {'id': 70})
        cat_account = self.c.fetchone()[0]
        assert deleted_account == None and cat_account == 'move_acc' and trans_account == 'move_acc' 

    def test_delete_category(self):
        # Set up a detailed category to try to delete it
        deleted_category = None  
        add_new_account(self.conn, self.c, ['test_acc_4', 'spending'])
        add_new_category(self.conn, self.c, {'-New category-': 'delete_cat', '-Account name-': 'test_acc_4'}, 80)
        values = {'-Year-': '2024', '-Month-': '7', '-Day-': '14', '-Selected Category-': 'delete_cat', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        add_transaction(self.conn, self.c, values, 'test_acc_4', 7)
        add_new_category(self.conn, self.c, {'-New category-': 'move_cat', '-Account name-': 'test_acc_4'}, 81)
        delete_category(self.conn, self.c, 'move_cat', 'test_acc_4', 80)
        # Check all db necessary for delete_cat
        self.c.execute("SELECT * FROM categories WHERE id=:id", {'id': 80})
        if self.c.fetchone(): 
            deleted_category = 1
        self.c.execute("SELECT * FROM transactions WHERE category_id=:category_id", {'category_id': 80})
        if self.c.fetchone(): 
            deleted_category = 1
        self.c.execute("SELECT category_id FROM transactions WHERE id=:id", {'id': 7})
        trans_cat_id = self.c.fetchone()[0]
        assert deleted_category == None and trans_cat_id == 81

########################################################################################################

############################## Test functions in update_items.py #######################################