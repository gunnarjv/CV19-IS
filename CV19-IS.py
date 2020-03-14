import numpy as np
import itertools
import plotly.graph_objects as go

# Case count from https://www.covid.is/tolulegar-upplysingar
# From bar chart and then manually keeping up with the confirmed cases number

# Daily new confirmed cases
d = [1, 1, 2, 8, 5, 13, 9, 8, 6, 6, 9, 13, 23, 14, 20]

# Cumulative (total) case count
c = list(itertools.accumulate(d,lambda x,y : x+y))

# Cumulative case count extrapolation
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
x = [x for x in range(6,15)]
y = c[6:]

fit = np.polyfit(x, np.log(y), 1)
# polyfit example results:
#    array([ 0.10502711, -0.40116352])
#    y ≈ exp(-0.401) * exp(0.105 * x) = 0.670 * exp(0.105 * x)

extrapolation = [np.exp(fit[1])*np.exp(fit[0]*x) for x  in range(51)]


# Cumulative case chart w. extrapolation
cp = go.Figure()
cp.add_scatter(y=c)
cp.add_scatter(y=extrapolation)

cp.update_yaxes(type="log", range=[np.log10(1), np.log10(100000)])
cp.update_xaxes(range=[0, 50])


# Label particular dates on chart
cp.add_trace(go.Scatter(
    x=[14, 27, 37, 42, 46],
    y=[138, 1060, 5150, 11345, 21346],
    mode="markers+text",
    name="Markers and Text",
    text=["(T+0, 138)", "(T+13, 1060)", "(T+23, 5000)", "(T+28, 10.500)", "(T+32, 21.500)"],
    textposition="top left"
))


cp.update_layout(showlegend=False)
cp.show()
