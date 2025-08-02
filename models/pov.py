from datetime import datetime
from dateutil import relativedelta

class PovController:
    def __init__(self):
        self.year_combo = []
        for i in range(datetime.now().year - 3, datetime.now().year + 5):
            self.year_combo.append(str(i))
        self.all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        self.today = datetime.now()
        self.this_month = self.today.replace(day=1) 
        self.view_date = self.this_month
        self.next_month = self.view_date + relativedelta.relativedelta(months=1)

    def changeViewDate(self, values):
        error_flag = 1
        if values['-Month-']:
            try:
                month_int = self.all_months.index(values['-Month-']) + 1
                self.view_date = self.view_date.replace(month=month_int)
            except ValueError:
                error_flag = -1 
        if values['-Year-']:
            try:
                year_int = int(values['-Year-'])
                self.view_date = self.view_date.replace(year=year_int)
            except ValueError:
                error_flag = -1
            
        self.next_month = self.view_date + relativedelta.relativedelta(months=1)
        
        return error_flag
    
    def getViewDateStr(self):
        return self.view_date.strftime('%Y-%m-%d')
    
    def getTodayStr(self):
        return self.today.strftime('%Y-%m-%d')
    
    def prettyViewDate(self):
        return self.view_date.strftime('%b %Y')
    
    def getScope(self):
        if self.this_month.date() == self.view_date.date():
            scope = 'present'
        elif self.this_month.date() < self.view_date.date():
            scope = 'future'
        else:
            scope = 'past'
        return scope
    
    def getNextMonthStr(self):
        return self.next_month.strftime('%Y-%m-%d')
    
    def getThisMonthStr(self):
        return self.this_month.strftime('%Y-%m-%d')

    def getViewDate(self):
        return self.view_date
    
    def getNextMonth(self):
        return self.next_month
    
    def getToday(self):
        return self.today
    
    def getAllMonths(self):
        return self.all_months
    
    def getYearCombo(self):
        return self.year_combo
    
    def getThisMonth(self):
        return self.this_month