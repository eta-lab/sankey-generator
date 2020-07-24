# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from influxdb import DataFrameClient
import generate_graph

# Stylesheet from plotly website
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ETA Lab Sankey Generator"
'''client = DataFrameClient(host='206.12.92.81', port=8086,
                         username='public', password='public',
                         database='ION')
'''
client = DataFrameClient(host='206.12.88.106', port=8086,
                         username='root', password='root',
                         database='sankey-gen-wide')
# Default Values
building_list = list(pd.DataFrame(client.get_list_measurements()).name)

default_start_date = (dt.today() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
default_end_date = dt.today().strftime('%Y-%m-%dT%H:%M:%S')


app.layout = html.Div(children=[
    html.H1(children='UBC Campus Energy Visualization Prototype',
            style={
                'textAlign': 'center'
            }),
    html.Div(children='This page is used to prototype a Sankey Diagram generator web app'),
    html.Div(),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(2019, 12, 1),
        max_date_allowed=dt.today(),
        start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
        end_date=dt.today().strftime('%Y-%m-%d'),
        initial_visible_month=dt.today()
    ),
    dcc.Dropdown(
        id='metric_selection',
        options=[
            {'label': 'Electricity Consumption', 'value': 'elec_energy'},
            {'label': 'Electric Power', 'value': 'elec_power'},
            {'label': 'Gas Consumption', 'value': 'gas_volume'},
            {'label': 'Water Consumption', 'value': 'water_volume'}
        ],
        value=['elec_energy'],
        multi=True,
        searchable=False
    ),
    html.Div(id='output-container-date-picker-range'),
    dcc.Graph(id='sankey_diagram')
])


@app.callback(
    dash.dependencies.Output('sankey_diagram', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('metric_selection', 'value')])
def update_figure(start_date, end_date, value):
    if value is not None:
        metric_list = value
    else:
        metric_list = ['elec_energy']

    if start_date is not None:
        start_date = start_date + "T00:00:00"
    else:
        start_date = default_start_date

    if end_date is not None:
        end_date = end_date + "T00:00:00"
    else:
        end_date = default_end_date

    sankey_figure = generate_graph.generate_sankey(client, start_date, end_date, building_list, metric_list)

    return sankey_figure


if __name__ == '__main__':
    app.run_server(debug=True)

