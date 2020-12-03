import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from influxdb import DataFrameClient
import numpy as np
import generate_graph
import utilities

# Stylesheet from plotly website
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ETA Lab Sankey Generator"

building_metadata = pd.read_csv("./metadata/BuildingMetadataAll.csv")
sensor_metadata = pd.read_csv("./metadata/energy_main_meter.csv")

influx_client = DataFrameClient(host='206.12.88.106', port=8086,
                                username='root', password='root',
                                database='cpsc-sankey')

color_dict = {'node': {'Elec': 'rgba(245, 230, 66, 1.0)',
                       'HotWater': 'rgba(17, 5, 240, 1.0)',
                       'Gas': 'rgba(0, 163, 65, 1.0)',
                       'Others': 'rgba(0, 247, 255, 1.0)'},
              'link': {'Elec': 'rgba(245, 230, 66, 0.2)',
                       'HotWater': 'rgba(17, 5, 240, 0.2)',
                       'Gas': ' rgba(0, 163, 65, 0.2)'}}

metric_list = ['Elec', 'Gas', 'HotWater']

default_start_date = "2020-10-01T00:00:00Z"
default_end_date = "2020-10-31T23:59:59Z"
min_date = dt(2015, 1, 1)
max_date = dt(2020, 12, 1)
initial_date = dt(2019, 10, 31)

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
                                dcc.Dropdown(id='cluster-type-selection-campus',
                                             options=[
                                                 {'label': 'Year Built', 'value': 'year_built_grouping'},
                                                 {'label': 'Building Type', 'value': 'building_type_mod'},
                                                 {'label': 'Size (m^2)', 'value': 'area_grouping'}],
                                             searchable=False,
                                             placeholder='Select cluster type',
                                             value='building_type_mod',
                                             style={'margin-bottom': '10px', 'margin-top': '10px'})
                                ,
                                dcc.Dropdown(id='cluster-selection-campus',
                                             searchable=False,
                                             placeholder='Select cluster',
                                             style={'margin-bottom': '10px'})
                                ,
                                html.P(children='Select time period',
                                       style={'margin-top': '10px'})
                                ,
                                dcc.DatePickerRange(
                                        id='date-picker-campus',
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        start_date=default_start_date,
                                        end_date=default_end_date,
                                        initial_visible_month=initial_date,
                                        style={'margin-bottom': '30px'})
                                ,
                                dcc.Checklist(
                                        id='cluster-comparison-on-off-campus',
                                        options=[
                                            {'label': 'Add another cluster for comparison',
                                             'value': 'comp',
                                             'disabled': True
                                             }
                                        ],
                                        style={'margin-bottom': '10px'}
                                                )
                                ,
                                dcc.Dropdown(id='cluster-comparison-selection-campus',
                                             searchable=False,
                                             placeholder='Select cluster',
                                             disabled=True,
                                             style={'margin-bottom': '10px'}
                                             )
                                ,
                                dcc.Checklist(
                                    id='comparison-date-campus-on-off',
                                    options=[
                                        {'label': 'Add another time period for comparison',
                                         'value': 'comp'}
                                        ])
                                ,
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='date-picker-campus-comparison',
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        start_date=default_start_date,
                                        end_date=default_end_date,
                                        initial_visible_month=initial_date)

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
                                         options=[{'label': 'Year Built', 'value': 'year_built_grouping'},
                                                  {'label': 'Building Type', 'value': 'building_type_mod'},
                                                  {'label': 'Size (m^2)', 'value': 'area_grouping'}],
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
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=default_start_date,
                                end_date=default_end_date,
                                initial_visible_month=initial_date,
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
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=default_start_date,
                                end_date=default_end_date,
                                initial_visible_month=initial_date,
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
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=default_start_date,
                                end_date=default_end_date,
                                initial_visible_month=initial_date,
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
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=default_start_date,
                                end_date=default_end_date,
                                initial_visible_month=initial_date,
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
                id='sankey_diagram_1',
                style={'height': '100%'}
            ),

    ], style={'width': '74%', 'display': 'inline-block',
              "border": "2px black solid", 'margin-left': '10px',
              'height': 680}
    ),
])


# Generate the cluster selection when selecting a cluster type
@app.callback(
    Output(component_id='cluster-selection-campus', component_property='options'),
    [Input(component_id='cluster-type-selection-campus', component_property='value')]
)
def generate_cluster_list_campus(cluster_type):
    cluster_list = building_metadata[cluster_type].unique()

    if len(cluster_list) > 0:
        options = utilities.generate_option_array_from_list(cluster_list)

    else:
        options = {'label': 'Not Found', 'value': 'nan'}

    return options

# TODO unable "add another cluster for comparison" when selecting one cluster

# TODO generating list whenever the "add another cluster for comparison" is checked

# Generate Graph when the cluster type or date is changed campus view
@app.callback(
    Output(component_id='sankey_diagram_1', component_property='figure'),
    [Input(component_id='cluster-type-selection-campus', component_property='value'),
     Input(component_id='date-picker-campus', component_property='start_date'),
     Input(component_id='date-picker-campus', component_property='end_date')])
def generate_campus_sankey(cluster_type, start_date, end_date):

    query_result = generate_graph.generate_influx_query(influx_client,
                                                        start_date,
                                                        end_date,
                                                        metric_list)

    sankey_figure = generate_graph.generate_sankey(query_result,
                                                   metric_list,
                                                   building_metadata,
                                                   color_dict,
                                                   cluster_type=cluster_type,
                                                   is_multi_level=False)

    return sankey_figure

# TODO Duplicating the behavior of the cluster tab for the tick selection


# Hide the cluster comparison if no cluster is selected
@app.callback(
    [Output(component_id='cluster-comparison-on-off-campus',
            component_property='options'),
     Output(component_id='cluster-comparison-selection-campus',
            component_property='disabled'),
     Output(component_id='cluster-comparison-selection-campus',
            component_property='options'),
     Output(component_id='date-picker-campus-comparison',
            component_property='disabled')],
    [Input(component_id='cluster-selection-campus', component_property='value'),
     Input(component_id='cluster-type-selection-campus', component_property='value'),
     Input(component_id='comparison-date-campus-on-off', component_property='value')])
def on_off_and_list_for_cluster_comparison(cluster_selection, cluster_type, date_compare):

    if date_compare:
        disabled_date = False
        options_on_off = {'label': 'Add another cluster for comparison',
                          'value': 'comp',
                          'disabled': True}
        disabled_cluster = True
        options_cluster = ''

    else:
        disabled_date = True
        if cluster_selection == 'None':
            options_on_off = {'label': 'Add another cluster for comparison',
                              'value': 'comp',
                              'disabled': True}
            disabled_cluster = True

            options_cluster = ''
        else:
            options_on_off = {'label': 'Add another cluster for comparison',
                              'value': 'comp'}
            disabled_cluster = False
            cluster_list_compare = building_metadata[cluster_type].unique()
            cluster_list_compare.remove(np.where(cluster_list_compare == cluster_selection))
            options_cluster = utilities.generate_option_array_from_list(cluster_list_compare)

    return options_on_off, disabled_cluster, options_cluster, disabled_date

# Show or hide campus selection
# TODO Generate Graph when comparing 2 date sets campus view



'''
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
        options = [{'label': 'Add another cluster for comparison', 'value': 'comp', 'disabled': True}]
    else:
        disabled = True
        options = [{'label': 'Add another cluster for comparison', 'value': 'comp'}]
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
'''

if __name__ == '__main__':
    app.run_server(debug=True)
