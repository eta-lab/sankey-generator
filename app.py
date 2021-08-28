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

# Reading metadata to memory
sensor_metadata = pd.read_csv("./metadata/sensorMetadata.csv")
building_metadata = pd.read_csv("./metadata/BuildingMetadataAll.csv")

# Database connection
influx_client = DataFrameClient(host='206.12.88.106', port=8086,
                                username='root', password='root',
                                database='sankey-generator')

# Color and metric dictionnaries
color_dict = {'node': {1: 'rgba(0, 172, 0, 1.0)',
                       2: 'rgba(224, 0, 188, 1.0)',
                       'real': 'rgba(100, 100, 100, 1.0)',
                       'simulation': 'rgba(100, 100, 100, 0.5)',
                       'building': 'rgba(177, 177, 177, 1.0)',
                       'category': 'rgba(85, 85, 85, 1.0)',
                       'group': 'rgba(85, 85, 85, 1.0)',
                       'Elec': 'rgba(205, 52, 181, 1.0)',
                       'HotWater': 'rgba(255, 177, 78, 1.0)',
                       'Gas': 'rgba(0, 0, 255, 1.0)',
                       },
              'link': {'Elec': 'rgba(205, 52, 181, 0.2)',
                       'HotWater': 'rgba(255, 177, 78, 0.2)',
                       'Gas': 'rgba(0, 0, 255, 0.2)',
                       1: {'real': 'rgba(177, 177, 177, 0.4)',
                           'simulation': 'rgba(0, 172, 0, 0.1)'},
                       2: {'real': 'rgba(224, 0, 188, 0.4)',
                           'simulation': 'rgba(224, 0, 188, 0.1)'},
                       'green': 'rgba(0, 172, 0, 0.4)',
                       'red': 'rgba(224, 0, 30, 0.4)'}}

max_nodes = 20

# Setting up default dates
default_start_date = "2020-10-01"
default_end_date = "2020-10-31"
min_date = dt(2015, 1, 1)
max_date = dt(2020, 12, 1)
initial_date = dt(2020, 9, 30)

# Generating categories from the metadata
category_columns = sensor_metadata.filter(regex='category', axis=1).columns
category_options = utilities.generate_category_options(category_columns)

# Generating metric list
metric_dict = {"ref": ['Elec', 'Gas', 'HotWater'],
               "label": ['Electricity', 'Gas', 'Hot Water']}

metric_list = metric_dict['ref']


app.layout = html.Div([
    html.H2(children='EnergyFlowVis'),
    html.H5(children='Visualizing energy use flows',
            style={'font-style': 'italic', 'fontSize': '12'}),
    html.Div([
        html.Div([
            html.P(children='For more information see the code and'
                            ' paper presented at Building Simulation 2021 on github'),
            html.A("BS2021 Sankey Generator Github",
                   href='https://github.com/eta-lab/sankey-generator',
                   target="_blank"),
            dcc.Dropdown(id='building-grouping-selection',
                         options=[
                             {'label': 'Building use', 'value': 'building_type_mod'},
                             {'label': 'Year of construction', 'value': 'year_built_grouping'},
                             {'label': 'Floor area (m^2)', 'value': 'area_grouping'}],
                         searchable=False,
                         placeholder='Select building grouping',
                         value='building_type_mod',
                         clearable=False,
                         style={'margin-bottom': '10px', 'margin-top': '10px'})
            ,
            dcc.Dropdown(id='group-selection',
                         searchable=False,
                         placeholder='Select group',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            dcc.Dropdown(id='building-filter',
                         placeholder='Filter building',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            html.P(children='Building breakdown viewer',
                   style={'margin-top': '10px'})
            ,

            dcc.Dropdown(id='building-selection',
                         placeholder='Select building',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            dcc.Dropdown(id='category-type-selection',
                         options=category_options,
                         placeholder='Select category type',
                         value='category_end_use',
                         clearable=False,
                         style={'margin-bottom': '10px', 'margin-top': '10px'}
                         )
            ,
            dcc.Dropdown(id='category-selection',
                         searchable=False,
                         placeholder='Select category',
                         multi=True,
                         style={'margin-bottom': '10px'}),

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

            ], id='comp-container',
                style={'display': 'block'}
            ),

        ], style={'height': '700'})
    ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),
    html.Div([
        html.Div([
            dcc.Graph(id='sankey-diagram')
        ], className='row', style={'height': '100%'})
    ], id='graph-container',
        style={'width': '78%',
               'margin-left': '10px',
               'display': 'inline-block',
               'height': 580}
    ),
])


@app.callback(
    Output(component_id='category-selection', component_property='options'),
    [Input(component_id='category-type-selection', component_property='value')]
)
def generate_cluster_list_campus(category_type):
    category_list = sensor_metadata[category_type].unique()

    if len(category_list) > 0:
        options = utilities.generate_option_array_from_list(np.sort(category_list))

    else:
        options = [{'label': 'Not Found', 'value': 'nan'}]

    return options


@app.callback(
    Output(component_id='building-selection', component_property='options'),
    [Input(component_id='category-type-selection', component_property='value'),
     Input(component_id='category-selection', component_property='value')]
)
def generate_cluster_list_campus(category_type, category_selection):
    if category_selection:
        building_list = sensor_metadata.loc[
            sensor_metadata[category_type].isin(category_selection), 'building'].unique()
    else:
        building_list = sensor_metadata['building'].unique()
    options = utilities.generate_option_array_from_list(np.sort(building_list))

    return options


# enable of disable the date compare
@app.callback(
    [Output(component_id='date-picker-comparison', component_property='disabled'),
     Output(component_id='date-picker-comparison', component_property='style'),
     Output(component_id='date-picker-comparison', component_property='start_date'),
     Output(component_id='date-picker-comparison', component_property='end_date')],
    [Input(component_id='comparison-date-on-off', component_property='value'),
     Input(component_id='date-picker', component_property='start_date'),
     Input(component_id='date-picker', component_property='end_date')]
)
def enable_date_comparison(on_off, start_date, end_date):
    if on_off:
        disabled_date = False
        start_date_compare = dt.strftime(dt.strptime(start_date, "%Y-%m-%d") -
                                         timedelta(days=30), "%Y-%m-%d")
        end_date_compare = dt.strftime(dt.strptime(end_date, "%Y-%m-%d") -
                                       timedelta(days=30), "%Y-%m-%d")
        date_style = {'margin-bottom': '30px', 'border': '2px black solid'}
    else:
        disabled_date = True
        start_date_compare = start_date
        end_date_compare = end_date
        date_style = {}

    return disabled_date, date_style, start_date_compare, end_date_compare


# Generate the list of building group to filter campus sankey
@app.callback(Output(component_id='group-selection', component_property='options'),
              [Input(component_id='building-grouping-selection', component_property='value')])
def building_group_list(building_grouping):
    group_list = building_metadata[building_grouping].unique()
    options = utilities.generate_option_array_from_list(group_list)
    return options


# Generate the list of buildings from the group filtered
@app.callback(Output(component_id='building-filter', component_property='options'),
              [Input(component_id='building-grouping-selection', component_property='value'),
               Input(component_id='group-selection', component_property='value')])
def building_filter_list(building_grouping, group_selection):
    if group_selection:
        building_list = building_metadata[
            building_metadata[building_grouping].isin(group_selection)].building
    else:
        building_list = building_metadata.building

    options = utilities.generate_option_array_from_list(building_list)
    return options


# Lock second date when building is selected
@app.callback(Output(component_id='comparison-date-on-off', component_property='options'),
              [Input(component_id='building-selection', component_property='value')])
def turn_off_date_compare(building_selection):
    if building_selection:
        options = [{'label': 'Add another time period for comparison',
                    'value': 'comp',
                    'disabled': True}]
    else:
        options = [{'label': 'Add another time period for comparison',
                    'value': 'comp'}]

    return options


# Generate Campus Sankey Figure
@app.callback(Output(component_id='sankey-diagram', component_property='figure'),
              [Input(component_id='building-grouping-selection', component_property='value'),
               Input(component_id='group-selection', component_property='value'),
               Input(component_id='building-filter', component_property='value'),
               Input(component_id='category-type-selection', component_property='value'),
               Input(component_id='category-selection', component_property='value'),
               Input(component_id='building-selection', component_property='value'),
               Input(component_id='date-picker', component_property='start_date'),
               Input(component_id='date-picker', component_property='end_date'),
               Input(component_id='date-picker-comparison', component_property='start_date'),
               Input(component_id='date-picker-comparison', component_property='end_date')])
def display_and_update_building_sankey_diagram(grouping_type, group_selection, building_filter,
                                               category_type, category_selection, building_selection,
                                               start_date_1, end_date_1,
                                               start_date_2, end_date_2):
    if building_selection:
        if category_selection:
            metadata = sensor_metadata[sensor_metadata[category_type].isin(category_selection)]
        else:
            metadata = sensor_metadata

        metadata = metadata[metadata['building'].isin(building_selection)]
        building_list = metadata['building'].unique()
        building_list_sim = utilities.generate_building_list_sim(building_list)

        query_result_dates = generate_graph.generate_dates_query(influx_client,
                                                                 building_list_sim,
                                                                 start_date_1, end_date_1,
                                                                 start_date_2, end_date_2)

        element_dict = generate_graph.generate_sankey_elements_simulation(query_result_dates,
                                                                        metadata,
                                                                        category_type,
                                                                        color_dict)

    else:
        if group_selection:
            building_metadata_filtered = building_metadata[
                building_metadata[grouping_type].isin(group_selection)]
        else:
            building_metadata_filtered = building_metadata

        if building_filter:
            building_metadata_filtered = building_metadata_filtered[
                building_metadata_filtered.building.isin(building_filter)]

        query_result_dates = generate_graph.generate_dates_query(influx_client,
                                                                 metric_list,
                                                                 start_date_1, end_date_1,
                                                                 start_date_2, end_date_2)

        element_dict = generate_graph.generate_sankey_elements_campus(query_result_dates, metric_list,
                                                                      building_metadata_filtered,
                                                                      grouping_type, max_nodes,
                                                                      color_dict)

    sankey_figure = generate_graph.generate_sankey_figure(element_dict)

    return sankey_figure


if __name__ == '__main__':
    app.run_server(debug=True)
