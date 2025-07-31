from datetime import datetime
from tests.parent_class import ParentClass
from logic.create_items import addNewAccount, addNewCategory, addTransaction


class TestTransaction(ParentClass):
    # TODO
    ### Events
    ###
    ### Logic #############################################################
    def testAddTransactionSuccessOutcome(self):
        addNewAccount(self.conn, self.c, ['test_acc_3', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_3', '-Account name-': 'test_acc_3'}, 20)
        values = {'-Date-': '7/28/2024', '-Selected Category-': 'test_cat_3', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        date_in = datetime.strptime(values['-Date-'], '%m/%d/%Y')
        addTransaction(self.conn, self.c, values, 'test_acc_3', 1)
        self.c.execute("SELECT id, category_id, account, total, date FROM transactions WHERE id=:id", {'id': 1})
        id, cat_id, account, total, date_out = self.c.fetchone()
        date_out = datetime.strptime(date_out, '%Y-%m-%d')
        assert id == 1 and cat_id == 20 and account == 'test_acc_3' and total < -5.54 and total > -5.56 and date_in == date_out

    def testAddTransactionSuccessIncome(self):
        addNewAccount(self.conn, self.c, ['test_acc_3.11', 'spending'])
        # User interface can select any category, even though the desired category is unallocated cash
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_3.11', '-Account name-': 'test_acc_3.11'}, 60)
        values = {'-Date-': '07-02-2024', '-Selected Category-': 'test_cat_3.11', '-Notes-': None, '-Payee-': None, '-Trans total-': '5.55'}
        date_in = datetime.strptime(values['-Date-'], '%m-%d-%Y')
        addTransaction(self.conn, self.c, values, 'test_acc_3.11', 5)
        self.c.execute("SELECT id, category_id, total, date FROM transactions WHERE id=:id", {'id': 5})
        id, cat_id, total, date_out = self.c.fetchone()
        date_out = datetime.strptime(date_out, '%Y-%m-%d')
        self.c.execute("SELECT name, account FROM categories WHERE id=:id", {'id': cat_id})
        cat, acc = self.c.fetchone()
        assert id == 5 and cat == 'Unallocated Cash' and acc == 'test_acc_3.11' and total > 5.54 and total < 5.56 and date_in == date_out

    def testAddTransactionInvalidYear(self):
        # TODO: Add together with invalid month and day, make invalid date
        addNewAccount(self.conn, self.c, ['test_acc_3.1', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_3.1', '-Account name-': 'test_acc_3.1'}, 30)
        values = {'-Date-': '7-22-20244', '-Selected Category-': 'test_cat_3.1', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        addTransaction(self.conn, self.c, values, 'test_acc_3.1', 2)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 2})
        id = self.c.fetchone()
        assert id == None    

    def testAddTransactionInvalidMonth(self):
        addNewAccount(self.conn, self.c, ['test_acc_3.2', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_3.2', '-Account name-': 'test_acc_3.2'}, 40)
        values = {'-Date-': '13-3-2024', '-Selected Category-': 'test_cat_3.2', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        addTransaction(self.conn, self.c, values, 'test_acc_3.2', 3)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 3})
        id = self.c.fetchone()
        assert id == None

    def testAddTransactionInvalidDay(self):
        addNewAccount(self.conn, self.c, ['test_acc_3.3', 'spending'])
        addNewCategory(self.conn, self.c, {'-New category-': 'test_cat_3.3', '-Account name-': 'test_acc_3.3'}, 50)
        values = {'-Date-': '7-32-2024', '-Selected Category-': 'test_cat_3.3', '-Notes-': None, '-Payee-': None, '-Trans total-': '-5.55'}
        addTransaction(self.conn, self.c, values, 'test_acc_3.3', 4)
        self.c.execute("SELECT id FROM transactions WHERE id=:id", {'id': 4})
        id = self.c.fetchone()
        assert id == None
        ############################################################################################################