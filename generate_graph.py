import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta


def generate_sankey_elements(df):
    # Initialize lists
    labels = []
    sources = []
    targets = []
    values = []
    n_metrics = len(df.index)

    labels.extend(list(df.index))
    labels.extend(list(df.columns))

    for i in range(n_metrics):

        sources.extend([i] * len(df.columns))

        targets.extend(range(n_metrics, len(labels)))

        values.extend(list(df.iloc[i, :]))

    return labels, sources, targets, values


def generate_sankey_df(influx_client, start_date, end_date):

    #  include the data from the end date even if the day is not over
    end_date_query = (dt.strptime(end_date[:10],  "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')

    where_params = {'t0': (start_date+"Z"),
                    't1': (end_date_query+"Z")}
    # Initializing dataframe
    df = pd.DataFrame()
    metric_list = ['elec_energy', 'gas_volume', 'water_volume']
    for metric in metric_list:
        query_influx = 'select sum(*) from {} where time<=$t0 and time<=$t1'.format(metric, metric)
        metric_string = "sum_"

        query_result = influx_client.query(query_influx, bind_params=where_params)
        query_result[metric].columns = [col_name.replace(metric_string, '')
                                        for col_name in query_result[metric].columns]

        df = df.append(query_result[metric])
    df.index = metric_list

    return df, start_date, end_date

def generate_sankey(df, building_list, start_date, end_date, data_type):

    df = df.loc[:, df.columns.isin(building_list)]

    labels, sources, targets, values = generate_sankey_elements(df)

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

    formatted_start_date = dt.strptime(start_date[:10], "%Y-%m-%d").strftime("%b %d %Y")
    formatted_end_date = dt.strptime(end_date[:10],  "%Y-%m-%d").strftime("%b %d %Y")

    if data_type == 'energy':
        sankey_figure.update_layout(
            title_text="Energy Consumption flow from {} to {}".format(formatted_start_date, formatted_end_date))
    elif data_type == 'water':
        sankey_figure.update_layout(
            title_text="Water Consumption flow from {} to {}".format(formatted_start_date, formatted_end_date))


    return sankey_figure
