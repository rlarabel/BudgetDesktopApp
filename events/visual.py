from logic.visualize_data import addFig
import numpy as np
import matplotlib.pyplot as plt


def visual(sg, conn, c, budget_wc, visual_wc):
    visual_wc.activate()
    budget_wc.hide()
    visual_wc.create(sg)
    
    while visual_wc.getActiveFlag():
        visual_wc.wait()
        event = visual_wc.getEvent()
        values = visual_wc.getValues()

        if event in ('Back', None):
            visual_wc.close()
            budget_wc.unhide()
        elif event == 'Show':
            show(sg, conn, c, plt, np, values)

        if visual_wc.getActiveFlag():
            visual_wc.update()
            


def show(sg, conn, c, plt, np, values):
    show_flag = 0
    if values['-Timeframe-'] != 'Custom Time Frame':
        show_flag = addFig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'])
    else:
        # TODO: change hardcoded text dates to user inputs as date objects
        # TODO: validate dates
        show_flag = addFig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'], '4-2020', '12-2024')
    if show_flag == 1:
        plt.subplots_adjust(left=.1, bottom=.2, right=.9, top=.9)
        plt.show()
    elif show_flag == -1:
        sg.popup('Not Enough Data')