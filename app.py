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

app = dash.Dash(__name__)
app.title = "ETA Lab Sankey Generator"
server = app.server

building_metadata = pd.read_csv("./metadata/BuildingMetadataAll.csv")
sensor_metadata = pd.read_csv("./metadata/energy_main_meter.csv")

influx_client = DataFrameClient(host='206.12.88.106', port=8086,
                                username='root', password='root',
                                database='cpsc-sankey')

color_dict = {'node': {'Elec': 'rgba(205, 52, 181, 1.0)',
                       'HotWater': 'rgba(255, 177, 78, 1.0)',
                       'Gas': 'rgba(0, 0, 255, 1.0)',
                       'cluster': 'rgba(177, 177, 177, 1.0)',
                       'building': 'rgba(85, 85, 85, 1.0)'},
              'link': {'Elec': 'rgba(205, 52, 181, 0.2)',
                       'HotWater': 'rgba(255, 177, 78, 0.2)',
                       'Gas': ' rgba(0, 0, 255, 0.2)'}}

metric_dict = {"ref": ['Elec', 'Gas', 'HotWater'],
               "label": ['Electricity', 'Gas', 'Hot Water']}

metric_list = metric_dict['ref']

default_start_date = "2020-10-01T00:00:00Z"
default_end_date = "2020-10-31T23:59:59Z"
min_date = dt(2015, 1, 1)
max_date = dt(2020, 12, 1)
initial_date = dt(2019, 10, 31)

n_node_limit = 10

app.layout = html.Div([

    html.Div([
        html.H1(children='EnergyFlowVis'),
        html.H4(children='Visualizing energy use flows on UBC Campus',
                style={'font-style': 'italic', 'fontSize': '12'}),
        html.Div([
            dcc.Dropdown(id='cluster-type-selection-campus',
                         options=[
                             {'label': 'Building use', 'value': 'building_type_mod'},
                             {'label': 'Year of construction', 'value': 'year_built_grouping'},
                             {'label': 'Floor area (m^2)', 'value': 'area_grouping'}],
                         searchable=False,
                         placeholder='Select cluster type',
                         value='building_type_mod',
                         clearable=False,
                         style={'margin-bottom': '10px', 'margin-top': '10px'})
            ,
            dcc.Dropdown(id='cluster-selection-campus',
                         searchable=False,
                         placeholder='Select cluster',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            dcc.Dropdown(id='building-selection-campus',
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
                    id='date-picker-campus',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=default_start_date,
                    end_date=default_end_date,
                    initial_visible_month=initial_date,
                    with_portal=True,
                    number_of_months_shown=3,
                    updatemode='bothdates',
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
                    with_portal=True,
                    number_of_months_shown=3,
                    updatemode='bothdates',
                    initial_visible_month=initial_date)

            ], id='campus_comp_container',
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
            dcc.Graph(id='sankey_diagram_1'),
            dcc.Graph(id='sankey_diagram_2')
        ], className='row', style={'height': '100%'})
    ], id='graph-container',
        style={'width': '74%',
               'margin-left': '10px',
               'display': 'inline-block',
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
        options = utilities.generate_option_array_from_list(np.sort(cluster_list))

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

    query_result = generate_graph.generate_influx_query(influx_client,
                                                        start_date,
                                                        end_date,
                                                        metric_dict)
    is_multi_date = False
    if cluster_selection:
        if building_selection:
            metadata = building_metadata[building_metadata['building'].isin(building_selection)]
            is_multi_level = True
            is_building = True
        else:
            metadata = building_metadata[building_metadata[cluster_type].isin(cluster_selection)]
            is_building = False
            if len(metadata) < n_node_limit:
                is_multi_level = True
            else:
                building_list = metadata.building.unique()
                df = utilities.generate_df_from_query_result(query_result)
                top_n_building = (df
                                  .sum(axis=0)[building_list]
                                  .sort_values(ascending=False)[:n_node_limit]
                                  .index)
                metadata = building_metadata[
                    building_metadata['building'].isin(top_n_building)]
                is_multi_level = True
    else:
        is_multi_level = False
        is_building = False
        metadata = building_metadata

    sankey_data, title = generate_graph.generate_sankey_data(query_result,
                                                             metric_dict,
                                                             metadata,
                                                             color_dict,
                                                             start_date,
                                                             end_date,
                                                             cluster_type,
                                                             is_multi_level,
                                                             is_multi_date,
                                                             is_building)

    sankey_figure = generate_graph.generate_sankey_figure(sankey_data, title)

    return sankey_figure


# Hide the cluster comparison if no cluster is selected
@app.callback([Output(component_id='date-picker-campus-comparison',
                      component_property='disabled'),
               Output(component_id='date-picker-campus-comparison',
                      component_property='start_date'),
               Output(component_id='date-picker-campus-comparison',
                      component_property='end_date')],
              [Input(component_id='comparison-date-campus-on-off',
                     component_property='value'),
               Input(component_id='date-picker-campus',
                     component_property='start_date'),
               Input(component_id='date-picker-campus',
                     component_property='end_date')])
def on_off_and_list_for_cluster_comparison(date_compare,
                                           start_date_campus,
                                           end_date_campus):

    if date_compare:
        disabled_date = False
        start_date_compare = start_date_campus
        end_date_compare = end_date_campus

    else:
        disabled_date = True
        start_date_compare = default_start_date
        end_date_compare = default_end_date

    return disabled_date, start_date_compare, end_date_compare


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
@app.callback(
    [Output(component_id='sankey_diagram_2',
            component_property='figure'),
     Output(component_id='sankey_diagram_1',
            component_property='style'),
     Output(component_id='sankey_diagram_2',
            component_property='style')],
    [Input(component_id='comparison-date-campus-on-off',
           component_property='value'),
     Input(component_id='date-picker-campus',
           component_property='start_date'),
     Input(component_id='date-picker-campus',
           component_property='end_date'),
     Input(component_id='date-picker-campus-comparison',
           component_property='start_date'),
     Input(component_id='date-picker-campus-comparison',
           component_property='end_date'),
     Input(component_id='cluster-type-selection-campus',
           component_property='value'),
     Input(component_id='cluster-selection-campus',
           component_property='value'),
     Input(component_id='building-selection-campus',
           component_property='value')])
def generate_comparison_sankey(date_compare,
                               start_date, end_date,
                               start_date_2, end_date_2,
                               cluster_type,
                               cluster_selection,
                               building_selection):
    if date_compare:

        query_result_date_compare = (generate_graph
                                     .generate_date_comp_query(influx_client, metric_dict,
                                                               start_date, end_date,
                                                               start_date_2, end_date_2))
        if cluster_selection:
            metadata = building_metadata[
                building_metadata[cluster_type].isin(cluster_selection)]
            if building_selection:
                metadata = building_metadata[
                    building_metadata.building.isin(building_selection)]
                is_building = True
            else:
                is_building = False
            if len(metadata) > n_node_limit:
                building_list = metadata.building.unique()
                date_range = start_date[:10] + ' to ' + end_date[:10]
                df = utilities.generate_df_from_query_result(
                    query_result_date_compare[date_range])
                top_n_building = (df
                                  .sum(axis=0)[building_list]
                                  .sort_values(ascending=False)[:n_node_limit]
                                  .index)
                metadata = building_metadata[
                    building_metadata['building'].isin(top_n_building)]
            is_multi_level = True
        else:
            metadata = building_metadata
            is_multi_level = False
            is_building = False
        is_multi_date=True
        sankey_data, title = (generate_graph
                              .generate_sankey_data(query_result_date_compare,
                                                    metric_dict,
                                                    metadata, color_dict,
                                                    start_date, end_date,
                                                    cluster_type,
                                                    is_multi_level,
                                                    is_multi_date,
                                                    is_building))

        sankey_figure = generate_graph.generate_sankey_figure(sankey_data, title)
        primary_style = {'display': 'none'}
        secondary_style = {'height': '100%'}

    else:
        sankey_figure = {}
        primary_style = {'height': '100%'}
        secondary_style = {'display': 'none'}

    return sankey_figure, primary_style, secondary_style

@app.callback(
    Output(component_id='node_exceeded',
           component_property='displayed'),
    [Input(component_id='cluster-selection-campus',
           component_property='value'),
     Input(component_id='cluster-type-selection-campus',
           component_property='value'),
     Input(component_id='building-selection-campus',
           component_property='value')]
)
def generate_alert_when_node_capacity_exceeded(cluster_selection,
                                               cluster_type,
                                               building_selection):
    if cluster_selection:

        if building_selection:
            metadata = building_metadata[building_metadata['building']
                .isin(building_selection)]
        else:
            metadata = building_metadata[building_metadata[cluster_type]
                .isin(cluster_selection)]
        if len(metadata) > n_node_limit:
            displayed = True
        else:
            displayed = False
    else:
        displayed = False
    return displayed

if __name__ == '__main__':
    app.run_server(debug=True)
