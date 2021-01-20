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

default_start_date = "2020-10-01"
default_end_date = "2020-10-31"
min_date = dt(2015, 1, 1)
max_date = dt(2020, 12, 1)
initial_date = dt(2020, 9, 30)

category_columns = sensor_metadata.filter(regex='category', axis=1).columns
category_options = utilities.generate_category_options(category_columns)

app.layout = html.Div([
    html.H2(children='EnergyFlowVis'),
    html.H5(children='Visualizing energy use flows',
            style={'font-style': 'italic', 'fontSize': '12'}),
    html.Div([
        html.Div([
            dcc.Dropdown(id='category-type-selection',
                         options=category_options,
                         searchable=False,
                         placeholder='Select category type',
                         value='category_end_use',
                         clearable=False,
                         style={'margin-bottom': '10px', 'margin-top': '10px'})
            ,
            dcc.Dropdown(id='category-selection',
                         searchable=False,
                         placeholder='Select category',
                         multi=True,
                         style={'margin-bottom': '10px'})
            ,
            dcc.Dropdown(id='building-selection',
                         placeholder='Select building',
                         multi=True,
                         style={'margin-bottom': '10px'})
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


@app.callback(
    Output(component_id='sankey-diagram', component_property='figure'),
    [Input(component_id='category-type-selection', component_property='value'),
     Input(component_id='category-selection', component_property='value'),
     Input(component_id='building-selection', component_property='value'),
     Input(component_id='date-picker', component_property='start_date'),
     Input(component_id='date-picker', component_property='end_date'),
     Input(component_id='date-picker-comparison', component_property='start_date'),
     Input(component_id='date-picker-comparison', component_property='end_date'),
     ]
)
def display_and_update_sankey_diagram(category_type,
                                      category_selection,
                                      building_selection,
                                      start_date_1, end_date_1,
                                      start_date_2, end_date_2):

    if category_selection:
        metadata = sensor_metadata[sensor_metadata[category_type].isin(category_selection)]
    else:
        metadata = sensor_metadata

    if building_selection:

        metadata = metadata[metadata['building'].isin(building_selection)]

    else:
        metadata = metadata

    building_list = metadata['building'].unique()

    query_result_dates = generate_graph.generate_dates_query(influx_client,
                                                             building_list,
                                                             start_date_1, end_date_1,
                                                             start_date_2, end_date_2)

    sankey_figure = generate_graph.generate_sankey_figure(query_result_dates,
                                                          metadata,
                                                          category_type,
                                                          color_dict)

    return sankey_figure

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


if __name__ == '__main__':
    app.run_server(debug=True)
