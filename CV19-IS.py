#!/usr/bin/env python3

import itertools
import datetime

import numpy as np
import plotly.graph_objects as go

'''
Case count from https://www.covid.is/tolulegar-upplysingar
Data is from the bar chart and then by manually keeping up with the confirmed cases number

The methodology for prediction here was simply to get some
exponential extrapolation that looks reasonable on the graph.

See:
https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly

np.polyfit example results:
    array([ 0.10502711, -0.40116352])
    y ≈ exp(-0.401) * exp(0.105 * x) = 0.670 * exp(0.105 * x)
'''

first_case_date = datetime.date(2020, 2, 28)

# Daily new confirmed cases (partial for March 14)
d = [1, 1, 2, 8, 5, 13, 9, 8, 6, 6, 9, 13, 23, 14, 20, 18]

# Cumulative (total) case count
c = list(itertools.accumulate(d,lambda x,y : x+y))

''' Extrapolation (Cumulative cases)  '''

def extrapolate():
    # Extrapolate from which days?
    from_day = 8
    to_day = 14
    # Last day (from zero) to extrapolate value for
    end_day_extrapolation = 50

    def _extrapolate():
        x = [x for x in range(from_day,to_day+1)]
        y = c[from_day:to_day+1]

        fit = np.polyfit(x, np.log(y), 1)

        extrapolation = [np.exp(fit[1])*np.exp(fit[0]*x) for x  in range(end_day_extrapolation+1)]
        return extrapolation

    return _extrapolate()

extrapolation = extrapolate()

''' Chart '''

# Cumulative case chart w. extrapolation
cp = go.Figure()
cp.add_scatter(y=c, name='Staðfest smit')
cp.add_scatter(y=extrapolation, name='Framreikningur')


def add_labels(cp):
    # Label particular dates on chart
    days_to_label = [15, 25, 35, 45]

    # Calculate y-position of labels as extrapolation[d] (good enough)
    days_to_label_y = [extrapolation[d] for d in days_to_label]

    def get_label_text(days_from_zero):
        label_form = '(T{0:+d}, {1:d})'
        today = datetime.datetime.now().date()

        d = datetime.timedelta(days_from_zero)
        days_from_today = (first_case_date + d - today).days

        if(days_from_today > 0):
            y_data_from = extrapolation
        elif(days_from_today < 0):
            y_data_from = c
        else:
            # If label is for today, we will return data if available,
            # else return label with no data
            if(len(c) > days_from_zero):
                y_data_from = c
            else:
                return '(T+0)'

        return label_form.format(days_from_today, int(y_data_from[days_from_zero]))

    labels_text = [get_label_text(x) for x in days_to_label_x]

    cp.add_trace(go.Scatter(
        x=days_to_label,
        y=days_to_label_y,
        mode="markers+text",
        text=labels_text,
        textposition="top left",
        showlegend=False
    ))

add_labels(cp)


y_axis_upper = 100000
cp.update_yaxes(type="log", range=[np.log10(1), np.log10(y_axis_upper)])
cp.update_xaxes(range=[0, end_date_extrapolation])

cp.update_layout(
    title="Staðfest smit CV-19 á Íslandi og framreikningur",
    xaxis_title="Dagar frá fyrsta staðfesta smiti",
    yaxis_title="Fjöldi",
    font=dict(
        family="Courier New, monospace",
        size=16,
    )
)

cp.show()


