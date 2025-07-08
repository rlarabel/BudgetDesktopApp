def change_pov(values, all_months, view_date):
    
    set_year, month_int = view_date.split('-')
    if values['-Month-']:
        for i, month in enumerate(all_months, 1):
            if values['-Month-'] == month:
                if i < 10:
                    month_int = '0' + str(i)
                else:
                    month_int = str(i)
    # Checks if the year given is an int and between 1800 - 2500
    try:
        int_user_year = int(values['-Year-'])
    except ValueError:
        int_user_year = None                
    
    if int_user_year and int_user_year < 2500 and int_user_year > 1800: 
        set_year = values['-Year-']
    view_date = set_year + '-' + month_int
    return view_date