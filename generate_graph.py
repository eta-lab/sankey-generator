import pandas as pd
import plotly.graph_objects as go
import numpy as np
import utilities


def generate_influx_query(influx_client, start_date, end_date, measurements_list):
    where_parameters = {'t0': start_date,
                        't1': end_date}

    measurements_string = utilities.generate_string_from_array(measurements_list)

    query_influx = 'select sum(*) from {} where time>=$t0 and time<=$t1'. \
        format(measurements_string)

    query_result = influx_client.query(query_influx, bind_params=where_parameters)
    query_result_df = pd.DataFrame()

    for measurement in measurements_list:
        query_result[measurement].columns = [col_name.replace('sum_', '')
                                             for col_name
                                             in query_result[measurement].columns]
        query_result_df = query_result_df.append(query_result[measurement])
    query_result_df.index = measurements_list

    return query_result_df


def generate_dates_query(influx_client, metric_list,
                         start_date_1, end_date_1,
                         start_date_2, end_date_2):
    query_result_dates = {}

    query_result_1 = generate_influx_query(influx_client,
                                           start_date_1, end_date_1,
                                           metric_list)
    query_result_2 = generate_influx_query(influx_client,
                                           start_date_2, end_date_2,
                                           metric_list)

    date_range_1 = start_date_1[:10] + ' to ' + end_date_1[:10]
    date_range_2 = start_date_2[:10] + ' to ' + end_date_2[:10]

    query_result_dates[date_range_1] = query_result_1
    query_result_dates[date_range_2] = query_result_2

    return query_result_dates


def generate_sankey_elements_building(query_result_dates, sensor_metadata, category_type,
                                      color_dict):

    category_list = sensor_metadata[category_type].unique()
    date_ranges = list(query_result_dates.keys())
    sensor_list = sensor_metadata.sensor_short_id
    building_list = sensor_metadata.building.unique()
    building_list_sim = utilities.generate_building_list_sim(building_list)

    element_dict = {'labels': np.concatenate((date_ranges,
                                              building_list_sim,
                                              category_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': []}

    i = 0
    for date_range in date_ranges:
        i += 1
        query_result = query_result_dates[date_range]
        # element_dict['color_nodes'].append(color_dict['node'][i])
        for building in building_list_sim:
            element_dict['sources'].append(np.where(element_dict['labels'] ==
                                                    building)[0][0])
            element_dict['targets'].append(np.where(element_dict['labels'] ==
                                                    date_range)[0][0])
            temp_df_building = query_result.loc[building,
                                                query_result.columns.isin(sensor_list)]
            element_dict['values'].append(temp_df_building.sum())
            if 'simulation' in building:
                real_simulation = 'simulation'
            else:
                real_simulation = 'real'

            element_dict['color_links'].append(color_dict['link'][i][real_simulation])
            for category in category_list:
                sensor_category_list = sensor_metadata[
                    sensor_metadata[category_type] == category].sensor_short_id

                temp_df_category = (query_result.loc[building,
                                                     query_result.columns.isin(
                                                         sensor_category_list)])

                if len(temp_df_category) > 0:
                    # Add the values for the end_use
                    element_dict['sources'].append(np.where(element_dict['labels']
                                                            == date_range)[0][0])

                    element_dict['targets'].append(np.where(element_dict['labels']
                                                            == category)[0][0])

                    category_value = temp_df_category.sum()

                    element_dict['values'].append(category_value)
                    element_dict['color_links'].append(color_dict['link'][i][real_simulation])

    for j in range(len(element_dict['labels'])):
        element = element_dict['labels'][j]
        if j < len(date_ranges):
            color = color_dict['node'][j+1]
        elif element in building_list:
            color = color_dict['node']['real']
        elif element in category_list:
            color = color_dict['node']['category']
        elif 'simulation' in element:
            color = color_dict['node']['simulation']
        else:
            color = color_dict['node']['cluster']

        element_dict['color_nodes'].append(color)

    return element_dict


def generate_sankey_elements_campus(query_result_dates, metric_list, building_metadata,
                                    grouping_type, max_nodes,
                                    color_dict):

    group_list = building_metadata[grouping_type].unique()
    date_ranges = list(query_result_dates.keys())
    building_list = building_metadata.building.unique()
    top_n_building = utilities.generate_top_n_list(query_result_dates, building_list, max_nodes)

    element_dict = {'labels': np.concatenate((metric_list,
                                              date_ranges,
                                              group_list,
                                              building_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': []}

    for date_range in date_ranges:
        query_result = query_result_dates[date_range]
        for metric in metric_list:
            element_dict['sources'].append(np.where(element_dict['labels'] == metric)[0][0])
            if len(date_ranges) > 1:
                element_dict['targets'].append(np.where(element_dict['labels'] == date_range[0][0]))
                temp_df_date = query_result.loc[metric, query_result.columns.isin(building_list)]
                element_dict['values'].append(temp_df_date.sum())
                element_dict['color_links'].append(color_dict['link'][metric])

            for group in group_list:
                building_group_list = building_metadata[building_metadata[
                                                            grouping_type] == group].building
                temp_df_group = query_result.loc[metric, query_result.columns.isin(building_group_list)]
                if len(temp_df_group) > 0:
                    if len(date_ranges) > 1:
                        element_dict['sources'].append(np.where(element_dict['labels'] == date_range))
                    element_dict['targets'].append(np.where(element_dict['labels'] == group))
                    group_value = temp_df_group.sum()
                    element_dict['values'].append(group_value)
                    element_dict['color_links'].append(color_dict['link'][metric])
                    for col in temp_df_group:
                        if col in top_n_building:

                            element_dict['sources'].append(
                                np.where(element_dict['labels'] == group))
                            element_dict['targets'].append(
                                np.where(element_dict['labels'] == col))
                            element_dict['value'].append(temp_df_group.loc[metric, col][0])
                            element_dict['color_links'].append(color_dict['link'][metric])

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        if element in list(building_list):
            color = color_dict['node']['building']
        elif element in metric_list:
            color = color_dict['node'][element]
        else:
            color = color_dict['node']['group']
        element_dict['color_nodes'].append(color)

    return element_dict


def generate_sankey_figure(element_dict):

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
            source=element_dict['sources'],
            target=element_dict['targets'],
            value=element_dict['values'],
            color=element_dict['color_links']
        )
    )

    sankey_figure = go.Figure(data=[sankey_data])
    sankey_figure.update_layout(margin=dict(l=10, r=100, b=30, t=0, pad=0))

    return sankey_figure

