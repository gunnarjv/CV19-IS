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

Internal Iceland infections from here
https://github.com/pallih/covid19-IS/blob/master/covid-19-is-sitrep.csv
and from March 13th reports from Landlaeknir

'extr_from_day' and 'extr_to_day' variables to decide what date range to use for extrapolation.
Then 'end_day_extrapolation' for number of days after first case to extrapolate towards.

See:
https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly

np.polyfit example results:
    array([ 0.10502711, -0.40116352])
    y ≈ exp(-0.401) * exp(0.105 * x) = 0.670 * exp(0.105 * x)
'''


first_case_date = datetime.date(2020, 2, 28)
'''
first_internal_infection_date = datetime.date(2020, 2, 6)
first_unknown_origin_date = datetime.date(2020, 3, 13)
'''

# Daily new confirmed cases (total)
d = [1, 0, 3, 6, 5, 15, 8,
     9, 7, 5, 9, 14, 24, 16,
     20, 24, 20, 22, 53, 78, 77,
     60, 91, 22, 67, 106, 41, 87]

# Cumulative (total) case count
c = list(itertools.accumulate(d, lambda x,y : x+y))

# Cumulative internal Iceland infections (innanlandssmit)
i = [0, 0, 0, 0, 0, 0, 0,
     6, 7, 10, 10, 16, 20, 22,
     30, 0, 0, 44, 55, 67, 86,
     114, 0, 0, 249, 270, 323, 459,
     550]

# Cumulative infections of unknown origin
u = [4, 0, 0, 6, 34, 55, 108,
     146, 0, 0, 144, 172, 194, 90,
    69]


def extrapolate(from_day, to_day, end_day_extrapolation, data):
    # Extrapolate using data from date range from_day-to_day
    # end_day_extrapolation is the last day no. to extrapolate value for

    x = [x for x in range(from_day, to_day+1)]
    y = data[from_day:to_day+1]

    fit = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))

    extrapolation = [np.exp(fit[1])*np.exp(fit[0]*x) for x  in range(end_day_extrapolation+1)]

    return extrapolation


def make_chart(data, chart_info=None, trace_name=None,
               extr_from_day=None, extr_to_day=None,
               end_day_extrapolation=None, log=True,
               days_to_label=[], y_axis_upper=1500):

    cp = go.Figure()

    extrapolation = extrapolate(extr_from_day, extr_to_day, end_day_extrapolation, data)
    # Select which part of the extrapolated data we will show
    extrapolation_x = [x for x in range(extr_from_day, end_day_extrapolation+1)]
    extrapolation_y = extrapolation[extr_from_day:]


    def add_labels():
        # Label particular dates on chart with reference to
        # Chart creation date with today as T+0.

        # Calculate y-position of labels as extrapolation[d] (good enough)
        days_to_label_y = [extrapolation[d] for d in days_to_label]

        def get_label_text(days_from_zero):
            label_form = '(T{0:+d}, {1:d} greind smit)'
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

        labels_text = [get_label_text(x) for x in days_to_label]

        cp.add_trace(go.Scatter(
            x=days_to_label,
            y=days_to_label_y,
            mode="markers+text",
            text=labels_text,
            textposition="top left",
            showlegend=False
        ))


    cp.add_scatter(y=c, name=trace_name, mode='lines+markers',)
    cp.add_scatter(y=extrapolation_y, x=extrapolation_x,
                   mode='lines+markers', line=dict(color='red'),
                   name='Framreikningur')

    add_labels()


    if log is True:
        cp.update_yaxes(type="log", range=[np.log10(1), np.log10(y_axis_upper)])


    cp.update_layout(
        **chart_info,
        font=dict(
            family="Courier New, monospace",
            size=12,
        )
    )

    return cp


def main():
    c_inf = {'title':"Greind smit Covid-19 á Íslandi",
                   'xaxis_title':"Dagar frá fyrsta staðfesta smiti",
                   'yaxis_title':"Fjöldi",
            }

    trace_name = 'Staðfest smit'

    cp = make_chart(data=c, chart_info=c_inf, trace_name=trace_name,
                    extr_from_day=16, extr_to_day=19,
                    end_day_extrapolation=27, log=False,
                    days_to_label=[25]
                    )

    cp.show()

if __name__ == "__main__":
    main()

