import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime as dt
from datetime import timedelta


def generate_sankey_elements(query_result, metric_list, building_metadata):
    # Initialize lists
    labels = np.append(metric_list, building_metadata.building)
    sources = []
    targets = []
    values = []

    for metric in metric_list:
        for col in query_result[metric].columns:
            sources.append(np.where(labels == metric)[0][0])
            targets.append(np.where(labels == col)[0][0])
            values.append(query_result[metric][col][0])

    return labels, sources, targets, values


def generate_string_from_array(array):
    array_string = ""

    for element in array:
        array_string = array_string + element + ', '

    return array_string[:-2]


def generate_influx_query(influx_client, start_date, end_date, metric_list):

    where_parameters = {'t0': start_date,
                        't1': end_date}

    metric_string = generate_string_from_array(metric_list)

    query_influx = 'select sum(*) from {} where time>=$t0 and time<=$t1'.format(metric_string)
    query_result = influx_client.query(query_influx, bind_params=where_parameters)

    for metric in metric_list:
        query_result[metric].columns = [col_name.replace('sum_', '')
                                        for col_name in query_result[metric].columns]

    return query_result


def generate_sankey(query_result, metric_list, building_metadata):

    labels, sources, targets, values = generate_sankey_elements(query_result,
                                                                metric_list,
                                                                building_metadata)

    sankey_figure = go.Figure(
        data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=sources,  # indices correspond to labels, eg A1, A2, A2, B1, ...
                target=targets,
                value=values
            )
        )]
    )

    return sankey_figure
