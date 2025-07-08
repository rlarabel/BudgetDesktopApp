from logic.visualize_data import add_fig
from views.visuals import create_visual_win
import numpy as np
import matplotlib.pyplot as plt


def visualize(sg, conn, c, values, budget_win):
    visual_win_active = True
    budget_win.Hide()
    visual_win = create_visual_win(sg)
    
    while visual_win_active:
        event, values = visual_win.Read()
        if event in ('Back', None):
            visual_win.Close()
            visual_win_active = False
            budget_win.UnHide()
        elif event == 'Show':
            show(sg, conn, c, plt, np, values)

        if visual_win_active:
            visual_win.BringToFront()


def show(sg, conn, c, plt, np, values):
    show_flag = 0
    if values['-Timeframe-'] != 'Custom Time Frame':
        show_flag = add_fig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'])
    else:
        # TODO: change hardcoded text dates to user inputs as date objects
        # TODO: validate dates
        show_flag = add_fig(sg, conn, c, plt, np, values['-Chart-'], values['-Timeframe-'], '4-2020', '12-2024')
    if show_flag == 1:
        plt.subplots_adjust(left=.1, bottom=.2, right=.9, top=.9)
        plt.show()
    elif show_flag == -1:
        sg.popup('Not Enough Data')