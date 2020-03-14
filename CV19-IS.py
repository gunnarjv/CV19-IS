#!/usr/bin/env python3

import itertools
import datetime

import numpy as np
import plotly.graph_objects as go

# Case count from https://www.covid.is/tolulegar-upplysingar
# From bar chart and then manually keeping up with the confirmed cases number

# Daily new confirmed cases (partial for March 14)
d = [1, 1, 2, 8, 5, 13, 9, 8, 6, 6, 9, 13, 23, 14, 20]

# Dates corresponding to cases
first_case_date = datetime.date(2020, 2, 28)
dates = [ first_case_date+datetime.timedelta(days=x) for x in range(len(d)) ]

# Cumulative (total) case count
c = list(itertools.accumulate(d,lambda x,y : x+y))

# Cumulative case count extrapolation
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
# The methodology here was simply to get some exponential extrapolation that looks reasonable on the graph

# What days to use for extrapolation
extrapolate_from_date = 6
extrapolate_to_date = 14

x = [x for x in range(extrapolate_from_date,extrapolate_to_date+1)]
y = c[extrapolate_from_date:extrapolate_to_date+1]

fit = np.polyfit(x, np.log(y), 1)
# polyfit example results:
#    array([ 0.10502711, -0.40116352])
#    y ≈ exp(-0.401) * exp(0.105 * x) = 0.670 * exp(0.105 * x)

end_date_extrapolation = 50
extrapolation = [np.exp(fit[1])*np.exp(fit[0]*x) for x  in range(end_date_extrapolation+1)]

# Cumulative case chart w. extrapolation
cp = go.Figure()
cp.add_scatter(y=c)
cp.add_scatter(y=extrapolation)

y_axis_upper_cutoff = 100000
cp.update_yaxes(type="log", range=[np.log10(1), np.log10(y_axis_upper_cutoff)])
cp.update_xaxes(range=[0, end_date_extrapolation])

# Label particular dates on chart
# past_or_present_dates_to_label_x = [15]
dates_to_label_x = [15, 27, 37, 42, 46]

# Rest of label is calculated

def get_label(days_from_zero):
    label_form = '(T{0:+d}, {1:d})'
    today = datetime.datetime.now().date()

    d = datetime.timedelta(days_from_zero)
    days_from_today = (first_case_date + d - today).days

    if(days_from_today > 0):
        return label_form.format(days_from_today, int(extrapolation[days_from_zero]))
    elif(days_from_today < 0):
        return label_form.format(days_from_today, int(c[days_from_zero]))
    else:
        # If numbers for today have been added, we show that, else nothing for today
        if(len(c) > days_from_zero):
            return label_form.format(days_from_today, int(c[days_from_zero]))
        return '(T+0)'

# Let extrapolation[d] Y-pos be good enough, even for past dates
dates_to_label_y = [extrapolation[d] for d in dates_to_label_x]

labels = [get_label(x) for x in dates_to_label_x]


cp.add_trace(go.Scatter(
    x=dates_to_label_x,
    y=dates_to_label_y,
    mode="markers+text",
    name="Markers and Text",
    text=labels,
    textposition="top left"
))


cp.update_layout(showlegend=False)
cp.show()

