from datetime import datetime
from dateutil import relativedelta

class pov_controller:
    def __init__(self):
        self.year_combo = []
        for i in range(datetime.now().year - 3, datetime.now().year + 5):
            self.year_combo.append(str(i))
        self.all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        self.today = datetime.now().replace(day=1) 
        self.view_date = self.today
        self.next_month = self.view_date + relativedelta.relativedelta(months=1)

    def change_view_date(self, values):
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
    
    def get_view_date_full_str(self):
        return self.view_date.strftime('%Y-%m-%d')
    
    def get_today_str(self):
        return self.today.strftime('%Y-%m-%d')
    
    def pretty_view_date(self):
        return self.view_date.strftime('%b %Y')
    
    def get_scope(self):
        if self.today.date() == self.view_date.date():
            scope = 'present'
        elif self.today.date() < self.view_date.date():
            scope = 'future'
        else:
            scope = 'past'
        return scope
    
    def get_next_month_str(self):
        return self.next_month.strftime('%Y-%m-%d')
    
    def get_view_date(self):
        return self.view_date
    
    def get_next_month(self):
        return self.next_month
    
    def get_today(self):
        return self.today
    
    def get_all_months(self):
        return self.all_months
    
    def get_year_combo(self):
        return self.year_combo