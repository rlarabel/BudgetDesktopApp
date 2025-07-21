def createVisualWin(sg):
    chart_menu = [
        'Pie Chart - Account Overview', 
        'Pie Chart - Allocation (50/%-30/%-20/% Rule)',
        'Pie Chart - Account Spending',
        'Pie Chart - Category Spending',
        'Bar Graph - Account Budgeting & Spending',
        'Bar Graph - Category Budgeting & Spending',
        "Bar Graph - Saving's Earnings & Deposits",
        'Line Graph - Total Wants Spending',
        'Line Graph - Total Needs Spending',
        'Line Graph - Total Account Spending',
        'Line Graph - Total Category Spending'
    ]
    timeframe_menu = [
        'Max',
        'YTD',
        'Last year',
        'Last month',
        '1 year',
        '2 years',
        '5 years',
        '10 years',
        'Custom Time Frame',
    ]
    # define the window layout
    layout = [
        [sg.Text('Dynamic Charts and Graphs')],
        [sg.Combo(values=chart_menu, k='-Chart-', readonly=True, default_value=chart_menu[0])],
        [sg.Text('Pie Charts: Account Overview and Allocation stay on max timeframe', font='Any 8')],
        [sg.Combo(values=timeframe_menu, k='-Timeframe-', readonly=True, default_value=timeframe_menu[0])],
        [sg.Button('Show'), sg.Button('Back')]
    ]

    # create the form and show it without the plot
    window = sg.Window('Data Visualization', layout, location=(0,0), finalize=True, element_justification='center', font='Helvetica 18')
    return window

def selWin(sg, menu, text):
    layout = [
        [sg.Text(f'Pick the {text} to view'), sg.Combo(values=menu, readonly=True, k='-Selection-')],
        [sg.Button('Go')]
    ]

    window = sg.Window(f'Select an {text}', layout, keep_on_top=True, finalize=True)

    return window