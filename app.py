import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd
from datetime import datetime as dt
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

metric_dict = {"ref": ['Elec', 'Gas', 'HotWater'],
               "label": ['Electricity', 'Gas', 'Hot Water']}

metric_list = metric_dict['ref']

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
                         multi=True,
                         style={'margin-bottom': '10px'}),
            dcc.Dropdown(id='building-selection-campus',
                         searchable=True,
                         placeholder='Select building',
                         disabled=True,
                         multi=True,
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
        options = [{'label': 'Not Found', 'value': 'nan'}]

    return options


# Generate Graph when the cluster type or date is changed campus view
@app.callback(
    Output(component_id='sankey_diagram_1', component_property='figure'),
    [Input(component_id='cluster-type-selection-campus', component_property='value'),
     Input(component_id='date-picker-campus', component_property='start_date'),
     Input(component_id='date-picker-campus', component_property='end_date'),
     Input(component_id='cluster-selection-campus', component_property='value'),
     Input(component_id='building-selection-campus', component_property='value')])
def generate_campus_sankey(cluster_type,
                           start_date, end_date,
                           cluster_selection,
                           building_selection):

    if cluster_selection:
        if building_selection:
            is_building = True
            metadata = building_metadata[building_metadata['building'].isin(building_selection)]
            is_multi_level = False
        else:
            metadata = building_metadata[building_metadata[cluster_type].isin(cluster_selection)]
            is_building = False
            if len(metadata) < 20:
                is_multi_level = True
            else:
                is_multi_level = False
    else:
        is_multi_level = False
        metadata = building_metadata
        is_building = False

    query_result = generate_graph.generate_influx_query(influx_client,
                                                        start_date,
                                                        end_date,
                                                        metric_dict)

    sankey_figure = generate_graph.generate_sankey(query_result,
                                                   metric_dict,
                                                   metadata,
                                                   color_dict,
                                                   cluster_type,
                                                   is_multi_level,
                                                   is_building)

    return sankey_figure


# Hide the cluster comparison if no cluster is selected
@app.callback(Output(component_id='date-picker-campus-comparison',
                     component_property='disabled'),
              [Input(component_id='comparison-date-campus-on-off',
                     component_property='value')])
def on_off_and_list_for_cluster_comparison(date_compare):

    if date_compare:
        disabled_date = False
    else:
        disabled_date = True

    return disabled_date


# Show or hide building selection and generate the list
@app.callback(
    [Output(component_id='building-selection-campus',
            component_property='options'),
     Output(component_id='building-selection-campus',
            component_property='disabled')],
    [Input(component_id='cluster-selection-campus',
           component_property='value'),
     Input(component_id='cluster-type-selection-campus',
           component_property='value')], )
def generate_building_list_from_cluster_selection(cluster_selection, cluster_type):
    if cluster_selection:
        disabled = False
        building_list = building_metadata.loc[
            building_metadata[cluster_type].isin(cluster_selection),
            ['building', 'long_name']]

        options_building = utilities.generate_option_array_from_list(building_list)
    else:
        disabled = True
        options_building = []

    return options_building, disabled

# Show or hide campus selection
# TODO Generate Graph when comparing 2 dates


if __name__ == '__main__':
    app.run_server(debug=True)
