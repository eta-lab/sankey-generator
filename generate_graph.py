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


def generate_sankey_elements_simulation(query_result_dates, sensor_metadata, category_type,
                                        color_dict):
    category_list = sensor_metadata[category_type].unique()
    building_list = sensor_metadata.building.unique()
    building_sim_list = utilities.generate_building_list_sim(building_list)
    date_ranges = list(query_result_dates.keys())

    element_dict = {'labels': np.concatenate((building_sim_list,
                                              category_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': [],
                    'x_values': [],
                    'y_values': []}
    date_range = date_ranges[0]
    query_result = query_result_dates[date_range]
    for building in building_list:
        for category in category_list:
            simulation_label = 'simulation_' + building
            sensor_category_list = sensor_metadata[
                sensor_metadata[category_type] == category].sensor_short_id
            category_df = (query_result.loc[[building, simulation_label],
                                            query_result.columns.isin(
                                                sensor_category_list)])
            sum_category = category_df.sum(axis=1)
            real_value = sum_category[building]
            simulation_error = real_value - sum_category[simulation_label]
            if simulation_error > 0:
                temp_color = 'green'
            else:
                temp_color = 'red'
            element_dict['sources'].append(np.where(element_dict['labels']
                                                    == building)[0][0])
            element_dict['targets'].append(np.where(element_dict['labels']
                                                    == category)[0][0])
            element_dict['values'].append(real_value)
            element_dict['color_links'].append(color_dict['link'][1]['real'])

            element_dict['sources'].append(np.where(element_dict['labels']
                                                    == simulation_label)[0][0])

            element_dict['targets'].append(np.where(element_dict['labels']
                                                    == category)[0][0])

            element_dict['values'].append(np.abs(simulation_error))
            element_dict['color_links'].append(color_dict['link'][temp_color])

    for j in range(len(element_dict['labels'])):
        element = element_dict['labels'][j]
        if element in building_list:
            color = color_dict['node']['real']
        elif 'simulation' in element:
            color = color_dict['node']['simulation']
        elif element in category_list:
            color = color_dict['node']['category']
        else:
            color = color_dict['node']['category']

        element_dict['color_nodes'].append(color)

    return element_dict

def generate_sankey_elements_building(query_result_dates, sensor_metadata, category_type,
                                      color_dict):

    category_list = sensor_metadata[category_type].unique()
    category_sim_list = utilities.generate_simulation_labels(category_list)
    date_ranges = list(query_result_dates.keys())
    sensor_list = sensor_metadata.sensor_short_id
    building_list = sensor_metadata.building.unique()
    building_list_sim = utilities.generate_building_list_sim(building_list)

    element_dict = {'labels': np.concatenate((building_list_sim,
                                              category_sim_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': [],
                    'x_values': [],
                    'y_values': []}

    i = 0
    for date_range in date_ranges:
        i += 1
        query_result = query_result_dates[date_range]
        for building in building_list_sim:
            if 'simulation' in building:
                real_simulation = 'simulation'
                suffix = '_SIMULATION'
            else:
                real_simulation = 'real'
                suffix = ''

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
                                                            == building)[0][0])

                    element_dict['targets'].append(np.where(element_dict['labels']
                                                            == (category+suffix))[0][0])

                    category_value = temp_df_category.sum()

                    element_dict['values'].append(category_value)
                    element_dict['color_links'].append(color_dict['link'][i][real_simulation])
    y_temp = 0.0
    delta_y = 1 / len(category_list)
    for j in range(len(element_dict['labels'])):
        element = element_dict['labels'][j]
        if element in building_list:
            color = color_dict['node']['real']
            x = 0.0
            y = 0.5
        elif element in category_list:
            color = color_dict['node']['category']
            x = 0.9
            y = y_temp
        elif 'simulation' in element.lower():
            color = color_dict['node']['simulation']
            if element[11:] in building_list:
                x = 0.05
                y = 0.5
            else:
                x = 1.0
                y = y_temp
                y_temp = y_temp + delta_y
                element_dict['labels'][j] = ''
        else:
            color = color_dict['node']['category']
            x = 0.0
            y = 0.0

        element_dict['color_nodes'].append(color)
        element_dict['x_values'].append(x)
        element_dict['y_values'].append(y)

    return element_dict


def generate_sankey_elements_campus(query_result_dates, metric_list, building_metadata,
                                    grouping_type, max_nodes,
                                    color_dict):

    group_list = building_metadata[grouping_type].unique()
    date_ranges = list(query_result_dates.keys())
    building_list = building_metadata.building.unique()
    if len(building_list) > max_nodes:
        top_n_building = utilities.generate_top_n_list(query_result_dates, building_list, max_nodes)
    else:
        top_n_building = building_list

    element_dict = {'labels': np.concatenate((metric_list,
                                              date_ranges,
                                              group_list,
                                              building_list), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'color_nodes': [],
                    'color_links': [],
                    'x_values': [],
                    'y_values': []}

    for date_range in date_ranges:
        query_result = query_result_dates[date_range]
        for metric in metric_list:

            if len(date_ranges) > 1:
                element_dict['sources'].append(np.where(element_dict['labels'] == metric)[0][0])
                element_dict['targets'].append(np.where(element_dict['labels'] == date_range)[0][0])
                temp_df_date = query_result.loc[metric, query_result.columns.isin(building_list)]
                element_dict['values'].append(temp_df_date.sum())
                element_dict['color_links'].append(color_dict['link'][metric])

            for group in group_list:
                building_group_list = building_metadata[building_metadata[
                                                            grouping_type] == group].building
                temp_df_group = query_result.loc[metric, query_result.columns.isin(building_group_list)]
                if temp_df_group.sum() > 0:
                    if len(date_ranges) > 1:
                        source_lvl2 = date_range

                    else:
                        source_lvl2 = metric

                    element_dict['sources'].append(
                        np.where(element_dict['labels'] == source_lvl2)[0][0])
                    element_dict['targets'].append(np.where(element_dict['labels'] == group)[0][0])
                    group_value = temp_df_group.sum()
                    element_dict['values'].append(group_value)
                    element_dict['color_links'].append(color_dict['link'][metric])
                    for col in temp_df_group.index:
                        if (col in top_n_building) & (temp_df_group[col] > 0):

                            element_dict['sources'].append(
                                np.where(element_dict['labels'] == group)[0][0])
                            element_dict['targets'].append(
                                np.where(element_dict['labels'] == col)[0][0])
                            element_dict['values'].append(temp_df_group[col])
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
            color=element_dict['color_nodes'],
            x=element_dict['x_values'],
            y=element_dict['y_values']
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

