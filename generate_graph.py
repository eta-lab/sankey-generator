import pandas as pd
import plotly.graph_objects as go
import numpy as np
import utilities


def generate_influx_query(influx_client, start_date, end_date, building_list):
    where_parameters = {'t0': start_date,
                        't1': end_date}

    building_string = utilities.generate_string_from_array(building_list)

    query_influx = 'select sum(*) from {} where time>=$t0 and time<=$t1'. \
        format(building_string)

    query_result = influx_client.query(query_influx, bind_params=where_parameters)

    for building in building_list:
        query_result[building].columns = [col_name.replace('sum_', '')
                                          for col_name in query_result[building].columns]

    return query_result


def generate_dates_query(influx_client, building_list,
                         start_date_1, end_date_1,
                         start_date_2, end_date_2):
    query_result_dates = {}
    query_result_1 = generate_influx_query(influx_client,
                                           start_date_1, end_date_1,
                                           building_list)
    query_result_2 = generate_influx_query(influx_client,
                                           start_date_2, end_date_2,
                                           building_list)

    date_range_1 = start_date_1[:10] + ' to ' + end_date_1[:10]
    date_range_2 = start_date_2[:10] + ' to ' + end_date_2[:10]

    query_result_dates[date_range_1] = query_result_1
    query_result_dates[date_range_2] = query_result_2

    return query_result_dates


def generate_sankey_elements(query_result_dates, sensor_metadata, category_type,
                             color_dict):

    category_list = sensor_metadata[category_type].unique()
    date_ranges = list(query_result_dates.keys())
    sensor_list = sensor_metadata.sensor_short_id
    building_list = sensor_metadata.building.unique()

    element_dict = {'labels': np.concatenate((date_ranges,
                                              building_list,
                                              category_list,
                                              sensor_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': []}

    i = 0
    for date_range in date_ranges:
        i += 1
        query_result = query_result_dates[date_range]
        element_dict['color_nodes'].append(color_dict['node'][i])
        for building in building_list:
            element_dict['sources'].append(np.where(element_dict['labels'] == date_range)[0][0])
            element_dict['targets'].append(np.where(element_dict['labels'] == building)[0][0])
            temp_df_building = query_result[building].loc[:, query_result[building].columns.isin(sensor_list)]
            element_dict['values'].append(temp_df_building.sum(axis=1)[0])
            element_dict['color_links'].append(color_dict['link'][i])
            for category in category_list:
                sensor_category_list = sensor_metadata[
                    sensor_metadata[category_type] == category].sensor_short_id

                temp_df_category = (query_result[building].
                                        loc[:,
                                    query_result[building].columns.isin(sensor_category_list)])

                if len(temp_df_category) > 0:
                    # Add the values for the end_use
                    element_dict['sources'].append(np.where(element_dict['labels'] == building)[0][0])

                    element_dict['targets'].append(np.where(element_dict['labels'] == category)[0][0])

                    category_value = temp_df_category.sum(axis=1)[0]

                    element_dict['values'].append(category_value)
                    element_dict['color_links'].append(color_dict['link'][i])
    for j in range(len(element_dict['labels'])):
        element = element_dict['labels'][j]
        if j < 2:
            color = color_dict['node'][j+1]
        elif element in building_list:
            color = color_dict['node']['building']
        elif element in category_list:
            color = color_dict['node']['category']
        else:
            color = color_dict['node']['cluster']

        element_dict['color_nodes'].append(color)

        return element_dict


def generate_sankey_figure(query_result_dates, sensor_metadata,
                           category_type, color_dict):

    element_dict = generate_sankey_elements(query_result_dates,
                                            sensor_metadata,
                                            category_type, color_dict)

    sankey_data = go.Sankey(
        valuesuffix=" kWh",
        node=dict(
            pad=15,
            thickness=20,

            line=dict(color="black", width=0.5),
            label=element_dict['labels'],
            color=element_dict['color_nodes']
        ),
        link=dict(
            source=element_dict['sources'],  # indices correspond to labels, eg A1, A2, A2, B1, ...
            target=element_dict['targets'],
            value=element_dict['values'],
            color=element_dict['color_links']
        )
    )

    sankey_figure = go.Figure(data=[sankey_data])
    sankey_figure.update_layout(margin=dict(l=10, r=100, b=30, t=0, pad=0))

    return sankey_figure

