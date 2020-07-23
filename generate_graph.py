import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta

def generate_sankey(influx_client, start_date, end_date, building_list, metric_list):

    df_all_buildings = pd.DataFrame(index=metric_list)

    string_building = ''
    for element in building_list:
        string_building = string_building + '"' + element + '"' + ', '
    string_building = string_building[:-2]
    end_date_query = (dt.strptime(end_date[:10],  "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    where_params = {'t0': (start_date+"Z"),
                    't1': (end_date_query+"Z")}

    query_influx = 'select sum(*) from {} where time >= $t0 and time < $t1'.format(string_building)
    query_result = influx_client.query(query_influx, bind_params=where_params)

    for element in query_result.keys():
        query_result[element].columns = [col_name.replace('sum_', '')
                                         for col_name in query_result[element].columns]
        df_all_buildings[element] = query_result[element].iloc[0]

    # Creating Labels, Target and values for Sankey diagram
    labels, sources, targets, values = generate_sankey_elements(df_all_buildings)

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
        ))])
    sankey_figure.update_layout(title_text="Energy flow from {} to {}".format(
        dt.strptime(start_date[:10], "%Y-%m-%d").strftime("%b %d %Y"),
        dt.strptime(end_date[:10],  "%Y-%m-%d").strftime("%b %d %Y")))
    sankey_figure.update_layout(height=800)

    return sankey_figure

def generate_sankey_elements(df):
    labels = []
    labels.extend(list(df.index))
    labels.extend(list(df.columns))
    sources = []
    targets = []
    values = []
    n_metrics = len(df.index)
    for i in range(n_metrics):
        sources.extend([i] * len(df.columns))
        targets.extend(range(n_metrics, len(labels)))
        values.extend(list(df.iloc[i,:]))
    return labels, sources, targets, values