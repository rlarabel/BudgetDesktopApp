from tests.parent_class import ParentClass
from logic.create_items import addNewAccount, addNewCategory, addTransaction
from logic.delete_items import deleteAccount, deleteCategory

############################## Test functions in create_items.py #######################################
### Function not tested: make_total_funds, make_category_menu, make_account_menu
class TestBudget(ParentClass):
    def testAddNewAccount(self):
        # TODO: add all account types 
        addNewAccount(self.conn, self.c, ['test_acc_1', 'spending'])
        self.c.execute("SELECT name FROM accounts WHERE type=:type", {'type': 'spending'})
        name = self.c.fetchone()[0]
        assert name == 'test_acc_1'

    def testAddNewCategorySuccess(self):
        addNewAccount(self.conn, self.c, ['test_acc_2', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_2', '-Account name-': 'test_acc_2'}, 10)
        self.c.execute("SELECT name FROM categories WHERE id=:id", {'id': 10})
        name = self.c.fetchone()[0]
        assert name == 'test_cat_2'
    
    def testAddNewCategoryDup(self):
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_2.11', '-Account name-': 'invalid_acc'}, 14)
        self.c.execute("SELECT id FROM categories WHERE name=:name", {'name': 'test_cat_2.11'})
        assert self.c.fetchone() == False

    # Can not add two categories with the same name under the same account even if different ids
    def testAddNewCategoryDup(self):
        dup_flag = False
        addNewAccount(self.conn, self.c, ['test_acc_2.1', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_2.1', '-Account name-': 'test_acc_2.1'}, 15)
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_2.1', '-Account name-': 'test_acc_2.1'}, 16)
        self.c.execute("SELECT id FROM categories WHERE name=:name", {'name': 'test_cat_2.1'})
        for i, id in enumerate(self.c.fetchall()):
            print(id[0])
            print(i)
            if id[0] != 15:
                dup_flag = True
            if i > 0:
                dup_flag = True
        assert dup_flag == False

  

########################################################################################################

############################## Test functions in delete_items.py #######################################
    # TODO: add track_categories
    def testDeleteAccount(self):
        # Set up a detailed account to try to delete it
        deleted_account = None  
        addNewAccount(self.conn, self.c, ['delete_acc', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'delete_cat', '-Account name-': 'delete_acc'}, 70)
        values = {'-Date-': '07-02-2024', '-Selected Category-': 'delete_cat', '-Notes-': None, '-Payee-': None, '-Trans total-': '50'}
        addTransaction(self.conn, self.c, values, 'delete_acc', 6)
        addNewAccount(self.conn, self.c, ['move_acc', 'spending'])
        deleteAccount(self.conn, self.c, 'move_acc', 'delete_acc')
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

    def testDeleteCategory(self):
        # Set up a detailed category to try to delete it
        deleted_category = None  
        addNewAccount(self.conn, self.c, ['test_acc_4', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'delete_cat', '-Account name-': 'test_acc_4'}, 80)
        values = {'-Date-': '07-02-2024', '-Selected Category-': 'delete_cat', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        addTransaction(self.conn, self.c, values, 'test_acc_4', 7)
        addNewCategory(self.conn, self.c, {'-New category-': 'move_cat', '-Account name-': 'test_acc_4'}, 81)
        deleteCategory(self.conn, self.c, 'move_cat', 'test_acc_4', 80)
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
    def close(self):
        self.conn.close()