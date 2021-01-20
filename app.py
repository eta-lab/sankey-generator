import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from influxdb import DataFrameClient
import numpy as np
import generate_graph
import utilities


app = dash.Dash(__name__)
app.title = "BDRG Sankey Generator"
server = app.server

sensor_metadata = pd.read_csv("./metadata/sensorMetadata.csv")

influx_client = DataFrameClient(host='206.12.88.106', port=8086,
                                username='root', password='root',
                                database='sankey-generator')


color_dict = {'node': {1: 'rgba(205, 52, 181, 1.0)',
                       2: 'rgba(255, 177, 78, 1.0)',
                       'building': 'rgba(177, 177, 177, 1.0)',
                       'category': 'rgba(85, 85, 85, 1.0)'},
              'link': {1: 'rgba(205, 52, 181, 0.2)',
                       2: 'rgba(255, 177, 78, 0.2)'}}

default_start_date = "2020-10-01T00:00:00Z"
default_end_date = "2020-10-31T23:59:59Z"
min_date = dt(2015, 1, 1)
max_date = dt(2020, 12, 1)
initial_date = dt(2020, 9, 30)

n_node_limit = 20

app.layout = html.Div([
    html.H2(children='EnergyFlowVis'),
    html.H5(children='Visualizing energy use flows on UBC Campus',
            style={'font-style': 'italic', 'fontSize': '12'}),
    html.Div([
        html.Div([
            dcc.Dropdown(id='category-type-selection',
                         options=[
                             {'label': 'End use', 'value': 'end_use_label'}],
                         searchable=False,
                         placeholder='Select category type',
                         value='end_use_label',
                         clearable=False,
                         style={'margin-bottom': '10px', 'margin-top': '10px'})
            ,
            dcc.Dropdown(id='cluster-selection',
                         searchable=False,
                         placeholder='Select category',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            dcc.Dropdown(id='building-selection',
                         placeholder='Select building',
                         disabled=True,
                         multi=True,
                         style={'margin-bottom': '10px',
                                'height': 200})
            ,
            html.P(children='Select time period',
                   style={'margin-top': '10px'})
            ,
            dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=default_start_date,
                    end_date=default_end_date,
                    initial_visible_month=initial_date,
                    with_portal=True,
                    number_of_months_shown=3,
                    updatemode='bothdates',
                    style={'margin-bottom': '30px', 'border': '2px black solid'})
            ,
            dcc.Checklist(
                id='comparison-date-on-off',
                options=[
                    {'label': 'Add another time period for comparison',
                     'value': 'comp'}
                    ])
            ,
            html.Div([
                dcc.DatePickerRange(
                    id='date-picker-comparison',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=default_start_date,
                    end_date=default_end_date,
                    with_portal=True,
                    number_of_months_shown=3,
                    reopen_calendar_on_clear=True,
                    updatemode='bothdates',
                    initial_visible_month=initial_date)

            ], id='comp_container',
                style={'display': 'block'}
            ),

        ], style={'height': '700'})
    ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),
    html.Div([
        html.Div([
            dcc.ConfirmDialog(
                id='node_exceeded',
                message='Number of node limited to the {} highest consumption  \n'
                        'Select specific buildings to have them displayed'.format(n_node_limit),
            ),
            dcc.Graph(id='sankey_diagram')
        ], className='row', style={'height': '100%'})
    ], id='graph-container',
        style={'width': '78%',
               'margin-left': '10px',
               'display': 'inline-block',
               'height': 580}
    ),
])


if __name__ == '__main__':
    app.run_server(debug=True)
