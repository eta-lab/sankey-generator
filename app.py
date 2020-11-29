import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
# from influxdb import DataFrameClient

import plotly.express as px

# Stylesheet from plotly website
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ETA Lab Sankey Generator"

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")


app.layout = html.Div([

    html.Div([
        html.H1(children='EnergyFlowVis'),
        html.H4(children='Visualizing energy use flows on UBC Campus',
                style={'font-style': 'italic', 'fontSize': '12'}),
        html.Div([
            dcc.Tabs(
                id="data-level",
                value="campus",
                children=[
                    dcc.Tab(
                        label="Campus",
                        value="campus",
                        children=[
                            html.Div([
                                html.P(children='Select time period',
                                       style={'margin-top': '10px'}),
                                dcc.DatePickerRange(
                                        id='date-picker-campus',
                                        min_date_allowed=dt(2019, 12, 1),
                                        max_date_allowed=dt.today(),
                                        start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                        end_date=dt.today().strftime('%Y-%m-%d'),
                                        initial_visible_month=dt.today(),
                                        style={'margin-bottom': '100px'}
                                    ),
                                dcc.Checklist(
                                    id='comparison-campus-on-off',
                                    options=[
                                        {'label': 'Add another time period for comparison',
                                         'value': 'comp'}
                                        ]
                                    ),
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='date-picker-campus-comparison',
                                        min_date_allowed=dt(2019, 12, 1),
                                        max_date_allowed=dt.today(),
                                        start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                        end_date=dt.today().strftime('%Y-%m-%d'),
                                        initial_visible_month=dt.today()
                                    )

                                ], id='campus_comp_container',
                                    style={'display': 'block'}
                                ),

                            ], style={'height': '700'})
                        ]),
                    dcc.Tab(
                        label="Cluster",
                        id="building_cluster",
                        children=[
                            dcc.Dropdown(id='cluster-type-selection',
                                         options=[
                                             {'label': 'Age', 'value': 'age'},
                                             {'label': 'Type', 'value': 'type'},
                                             {'label': 'Size (m^2)', 'value': 'area'}],
                                         searchable=False,
                                         placeholder='Select cluster type',
                                         style={'margin-bottom': '10px', 'margin-top': '10px'}),

                            dcc.Dropdown(id='cluster-selection',
                                         options=[{'label': 'placeholder 1', 'value': 'ph1'},
                                                  {'label': 'placeholder 2', 'value': 'ph2'}],
                                         searchable=False,
                                         placeholder='Select cluster',
                                         style={'margin-bottom': '10px'}),

                            html.P(children='Select time period',
                                   style={'margin-bottom': '10px'}),

                            dcc.DatePickerRange(
                                id='date-picker-cluster',
                                min_date_allowed=dt(2019, 12, 1),
                                max_date_allowed=dt.today(),
                                start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                end_date=dt.today().strftime('%Y-%m-%d'),
                                initial_visible_month=dt.today(),
                                style={'margin-bottom': '30px'}
                                                ),
                            dcc.Checklist(
                                id='cluster-comparison-on-off',
                                options=[
                                    {'label': 'Add another cluster for comparison',
                                     'value': 'comp'}
                                ],
                                style={'margin-bottom': '10px'}
                                        ),
                            dcc.Dropdown(id='cluster-comparison-selection',
                                         options=[{'label': 'placeholder 1', 'value': 'ph1'},
                                                  {'label': 'placeholder 2', 'value': 'ph2'}],
                                         searchable=False,
                                         placeholder='Select cluster',
                                         disabled=True,
                                         style={'margin-bottom': '10px'}
                                         ),

                            dcc.Checklist(
                                id='cluster-time-comparison-on-off',
                                options=[
                                    {'label': 'Add another time period for comparison',
                                     'value': 'comp'}
                                ],
                                style={'margin-bottom': '10px'}
                            ),
                            dcc.DatePickerRange(
                                id='date-picker-cluster-comparison',
                                min_date_allowed=dt(2019, 12, 1),
                                max_date_allowed=dt.today(),
                                start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                end_date=dt.today().strftime('%Y-%m-%d'),
                                initial_visible_month=dt.today(),
                                disabled=True,
                                style={'margin-bottom': '10px'}
                            ),

                        ]
                    ),
                    dcc.Tab(
                        label="Building",
                        id="building_level",
                        children=[
                            dcc.Dropdown(id='building_selection',
                                         options=[
                                             {'label': 'CIRS', 'value': 'cirs'},
                                             {'label': 'Pharmacy', 'value': 'pharmacy'},
                                             {'label': 'AMS Nest', 'value': 'ams_nest'}],
                                         placeholder='Select building',
                                         style={'margin-bottom': '10px', 'margin-top': '10px'}),
                            html.P(children='Select time period',
                                   style={'margin-bottom': '10px'}),

                            dcc.DatePickerRange(
                                id='date-picker-building',
                                min_date_allowed=dt(2019, 12, 1),
                                max_date_allowed=dt.today(),
                                start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                end_date=dt.today().strftime('%Y-%m-%d'),
                                initial_visible_month=dt.today(),
                                style={'margin-bottom': '30px'}
                                                ),
                            dcc.Checklist(
                                id='building-comparison-on-off',
                                options=[
                                    {'label': 'Add another building for comparison',
                                     'value': 'comp'}
                                ],
                                style={'margin-bottom': '10px'}
                                        ),
                            dcc.Dropdown(id='building-comparison-selection',
                                         options=[{'label': 'placeholder 1', 'value': 'ph1'},
                                                  {'label': 'placeholder 2', 'value': 'ph2'}],
                                         placeholder='Select building',
                                         disabled=True,
                                         style={'margin-bottom': '10px'}
                                         ),
                            dcc.Checklist(
                                id='building-time-comparison-on-off',
                                options=[
                                    {'label': 'Add another time period for comparison',
                                     'value': 'comp'}
                                ],
                                style={'margin-bottom': '10px'}
                            ),
                            dcc.DatePickerRange(
                                id='date-picker-building-comparison',
                                min_date_allowed=dt(2019, 12, 1),
                                max_date_allowed=dt.today(),
                                start_date=(dt.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                end_date=dt.today().strftime('%Y-%m-%d'),
                                initial_visible_month=dt.today(),
                                disabled=True,
                                style={'margin-bottom': '10px'}
                            ),
                        ]
                    )
                ]
            )
        ], style={'height': 400}),
        html.Button('Generate Diagram', id='generate_button', n_clicks=0,
                    style={'width': '100%', 'margin-top': '50px'}
                    )

    ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),
    html.Div([
            dcc.Graph(
                id='example-graph',
                figure=fig,
            ),

    ], style={'width': '74%', 'display': 'inline-block',
              "border": "2px black solid", 'margin-left': '10px',
              'height': 680}
    ),
])


# Show or hide campus level dates for comparison
@app.callback(
    Output(component_id='date-picker-campus-comparison', component_property='disabled'),
    [Input(component_id='comparison-campus-on-off', component_property='value')])
def enable_campus_comparison(display_campus_comparison):
    if display_campus_comparison:
        return False
    else:
        return True


# Enable the cluster selection for comparison
@app.callback([
    Output(component_id='cluster-comparison-selection', component_property='disabled'),
    Output(component_id='cluster-time-comparison-on-off', component_property='options')
    ],
    [Input(component_id='cluster-comparison-on-off', component_property='value')])
def enable_cluster_comparison_selection(cluster_comparison_selection):
    if cluster_comparison_selection:
        disabled = False
        options = [{'label': 'Add another time period for comparison', 'value': 'comp', 'disabled': True}]

    else:
        disabled = True
        options = [{'label': 'Add another time period for comparison', 'value': 'comp'}]

    return disabled, options


# Enable the cluster date comparison
@app.callback([
    Output(component_id='date-picker-cluster-comparison', component_property='disabled'),
    Output(component_id='cluster-comparison-on-off', component_property='options')
    ],
    [Input(component_id='cluster-time-comparison-on-off', component_property='value')])
def enable_cluster_time_comparison(cluster_comparison_time):
    if cluster_comparison_time:
        disabled = False
        options = [{'label': 'Add another building for comparison', 'value': 'comp', 'disabled': True}]
    else:
        disabled = True
        options = [{'label': 'Add another building for comparison', 'value': 'comp'}]
    return disabled, options


# Enable the building selection comparison
@app.callback([
    Output(component_id='building-comparison-selection', component_property='disabled'),
    Output(component_id='building-time-comparison-on-off', component_property='options')
    ],
    [Input(component_id='building-comparison-on-off', component_property='value')])
def enable_cluster_time_comparison(cluster_comparison_time):
    if cluster_comparison_time:
        disabled = False
        options = [{'label': 'Add another time period for comparison', 'value': 'comp', 'disabled': True}]
    else:
        disabled = True
        options = [{'label': 'Add another time period for comparison', 'value': 'comp'}]
    return disabled, options


# Enable the cluster date comparison
@app.callback([
    Output(component_id='date-picker-building-comparison', component_property='disabled'),
    Output(component_id='building-comparison-on-off', component_property='options')
    ],
    [Input(component_id='building-time-comparison-on-off', component_property='value')])
def enable_cluster_time_comparison(cluster_comparison_time):
    if cluster_comparison_time:
        disabled = False
        options = [{'label': 'Add another building for comparison', 'value': 'comp', 'disabled': True}]
    else:
        disabled = True
        options = [{'label': 'Add another building for comparison', 'value': 'comp'}]
    return disabled, options


if __name__ == '__main__':
    app.run_server(debug=True)
