import pandas as pd
import plotly.graph_objects as go
import numpy as np
import utilities


def generate_sankey_elements(query_result, metric_dict,
                             building_metadata, cluster_type,
                             color_dict):
    # Initialize lists
    cluster_list = building_metadata[cluster_type].unique()
    cluster_label = [label[2:] for label in cluster_list]
    metric_list = metric_dict['ref']
    element_dict = {'labels': np.append(metric_list, cluster_list),
                    'labels_display': np.append(metric_dict['label'], cluster_label),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'element_area': {},
                    'normalized_values': [],
                    'color_nodes': [],
                    'color_links': []}

    for metric in metric_list:
        element_dict['color_nodes'].append(color_dict['node'][metric])
        for cluster in cluster_list:

            building_cluster_list = building_metadata[
                building_metadata[cluster_type] == cluster].building

            temp_value = (query_result[metric]
                          .loc[:,
                          query_result[metric].columns.isin(building_cluster_list)]
                          .sum(axis=1)[0])
            element_area = building_metadata[
                (building_metadata.building.isin(building_cluster_list))].area.sum()

            element_dict['element_area'][cluster] = element_area

            if temp_value > 0:
                element_dict['values'].append(temp_value)
                element_dict['sources'].append(np.where(
                    element_dict['labels'] == metric)[0][0])

                element_dict['targets'].append(np.where(
                    element_dict['labels'] == str(cluster))[0][0])

                element_dict['color_links'].append(color_dict['link'][metric])

    for i in range(len(element_dict['labels'])-3):
        element_dict['color_nodes'].append(color_dict['node']['cluster'])

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        if element in metric_list:
            normalized_value = 'N/A'
        else:
            indices = [j for j, x in enumerate(element_dict['targets']) if x == i]
            area = element_dict['element_area'][element]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)

        element_dict['normalized_values'].append(normalized_value)

    return element_dict


def generate_multi_level_sankey_elements(query_result, metric_dict,
                                         cluster_type, building_metadata,
                                         is_building,
                                         color_dict):

    building_list = building_metadata.building
    cluster_list = building_metadata[cluster_type].unique()
    building_long_name = building_metadata.long_name
    metric_list = metric_dict['ref']
    cluster_label = [label[2:] for label in cluster_list]

    element_dict = {'labels': np.concatenate((metric_list,
                                              cluster_list,
                                              building_list), axis=None),
                    'labels_display': np.concatenate((metric_dict['label'],
                                                      cluster_label,
                                                      building_long_name), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'element_area': {},
                    'normalized_values': [],
                    'color_nodes': [],
                    'color_links': []}

    for metric in metric_list:
        element_dict['color_nodes'].append(color_dict['node'][metric])
        element_dict['element_area'] = {metric: []}
        for cluster in cluster_list:
            building_cluster_list = building_metadata[
                building_metadata[cluster_type] == cluster].building
            element_area = building_metadata[
                (building_metadata.building.isin(building_cluster_list))].area.sum()

            element_dict['element_area'][cluster] = element_area

            temp_df = (query_result[metric].
                       loc[:, query_result[metric].
                       columns.isin(building_cluster_list)])

            if len(temp_df) > 0:
                # Add the values for the clusters
                element_dict['sources'].\
                    append(np.where(element_dict['labels'] == metric)[0][0])

                element_dict['targets'].\
                    append(np.where(element_dict['labels'] == cluster)[0][0])

                if is_building:
                    cluster_value = 0
                else:
                    cluster_value = temp_df.sum(axis=1)[0]

                element_dict['values'].\
                    append(cluster_value)
                element_dict['color_links'].\
                    append(color_dict['link'][metric])

                # Add the values for the individual building
                for col in temp_df.columns:
                    if is_building:
                        from_source = metric
                    else:
                        from_source = cluster
                    element_dict['sources'].\
                        append(np.where(element_dict['labels'] == from_source)[0][0])
                    element_dict['targets'].\
                        append(np.where(element_dict['labels'] == col)[0][0])
                    element_dict['values'].append(temp_df[col][0])

                    element_dict['color_links'].append(color_dict['link'][metric])

    for i in range(len(metric_list), len(element_dict['labels'])):
        element = element_dict['labels'][i]
        if element in cluster_list:
            color = color_dict['node']['cluster']
        else:
            color = color_dict['node']['building']
        element_dict['color_nodes'].append(color)

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        indices = [j for j, x in enumerate(element_dict['targets']) if x == i]
        if element in cluster_list:
            area = element_dict['element_area'][element]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)

        elif element in metric_list:
            normalized_value = 'N/A'
        else:
            area = building_metadata.loc[
                building_metadata.building == element, 'area'].iloc[0]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value / area, 2)
        element_dict['normalized_values'].append(normalized_value)

    return element_dict


def generate_sankey_date_compare_element(query_result_date_compare, metric_dict,
                                         cluster_type, building_metadata,
                                         is_multi_level, is_building,
                                         color_dict):

    building_list = building_metadata.building
    building_long_name = building_metadata.long_name
    cluster_list = building_metadata[cluster_type].unique()
    cluster_label = [label[2:] for label in cluster_list]
    metric_list = metric_dict['ref']
    date_range_list = list(query_result_date_compare.keys())

    element_dict = {'labels': np.concatenate((metric_list,
                                              date_range_list,
                                              cluster_list,
                                              building_list), axis=None),
                    'labels_display': np.concatenate((metric_dict['label'],
                                                      date_range_list,
                                                      cluster_label,
                                                      building_long_name), axis=None),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'element_area': {},
                    'normalized_values': [],
                    'color_nodes': [],
                    'color_links': []}

    for date_range in date_range_list:
        query_result = query_result_date_compare[date_range]
        for metric in metric_list:
            element_dict['element_area'] = {metric: []}
            element_dict['sources'].append(np.where(element_dict['labels'] == metric)[0][0])
            element_dict['targets'].append(np.where(element_dict['labels'] == date_range)[0][0])
            temp_df = query_result[metric].loc[:, query_result[metric].columns.isin(building_list)]
            element_dict['values'].append(temp_df.sum(axis=1)[0])
            element_dict['color_links']. \
                append(color_dict['link'][metric])

            for cluster in cluster_list:
                building_cluster_list = building_metadata[
                    building_metadata[cluster_type] == cluster].building
                element_area = building_metadata[
                    (building_metadata.building.isin(building_cluster_list))].area.sum()

                element_dict['element_area'][cluster] = element_area

                temp_df = (query_result[metric].
                               loc[:, query_result[metric].
                               columns.isin(building_cluster_list)])

                if len(temp_df) > 0:
                    # Add the values for the clusters
                    element_dict['sources']. \
                        append(np.where(element_dict['labels'] == date_range)[0][0])

                    element_dict['targets']. \
                        append(np.where(element_dict['labels'] == cluster)[0][0])
                    if is_building:
                        cluster_value = 0
                    else:
                        cluster_value = temp_df.sum(axis=1)[0]

                    element_dict['values']. \
                        append(cluster_value)
                    element_dict['color_links']. \
                        append(color_dict['link'][metric])

                    # Add the values for the individual building
                    if is_multi_level:
                        for col in temp_df.columns:

                            if is_building:
                                from_source = date_range
                            else:
                                from_source = cluster

                            element_dict['sources']. \
                                append(np.where(element_dict['labels'] == from_source)[0][0])
                            element_dict['targets']. \
                                append(np.where(element_dict['labels'] == col)[0][0])
                            element_dict['values'].append(temp_df[col][0])

                            element_dict['color_links'].append(color_dict['link'][metric])

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        if element in list(building_list):
            color = color_dict['node']['building']
        elif element in metric_list:
            color = color_dict['node'][element]
        else:
            color = color_dict['node']['cluster']
        element_dict['color_nodes'].append(color)

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        indices = [j for j, x in enumerate(element_dict['targets']) if x == i]

        if element in cluster_list:
            area = element_dict['element_area'][element]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)
        elif element in metric_list:
            normalized_value = 'N/A'
        elif element in date_range_list:
            normalized_value = 'N/A'
        else:
            area = building_metadata.loc[
                building_metadata.building == element, 'area'].iloc[0]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)

        element_dict['normalized_values'].append(normalized_value)

    return element_dict


def generate_influx_query(influx_client, start_date, end_date, metric_dict):

    where_parameters = {'t0': start_date,
                        't1': end_date}

    metric_list = metric_dict['ref']

    metric_string = utilities.generate_string_from_array(metric_list)

    query_influx = 'select sum(*) from {} where time>=$t0 and time<=$t1'.\
        format(metric_string)

    query_result = influx_client.query(query_influx, bind_params=where_parameters)

    for metric in metric_list:
        query_result[metric].columns = [col_name.replace('sum_', '')
                                        for col_name in query_result[metric].columns]

    return query_result


def generate_date_comp_query(influx_client, metric_dict,
                             start_date_1, end_date_1,
                             start_date_2, end_date_2):
    query_result_date_compare = {}
    query_result_1 = generate_influx_query(influx_client,
                                           start_date_1, end_date_1,
                                           metric_dict)
    query_result_2 = generate_influx_query(influx_client,
                                           start_date_2, end_date_2,
                                           metric_dict)

    date_range_1 = start_date_1[:10] + ' to ' + end_date_1[:10]
    date_range_2 = start_date_2[:10] + ' to ' + end_date_2[:10]

    query_result_date_compare[date_range_1] = query_result_1
    query_result_date_compare[date_range_2] = query_result_2

    return query_result_date_compare


def generate_sankey_data(query_result, metric_dict,
                         building_metadata, color_dict,
                         cluster_type='building_type_mod',
                         is_multi_level=True,
                         is_multi_date=False,
                         is_building=False):
    if is_multi_date:
        element_dict = generate_sankey_date_compare_element(query_result,
                                                            metric_dict,
                                                            cluster_type,
                                                            building_metadata,
                                                            is_multi_level,
                                                            is_building,
                                                            color_dict)

    elif is_multi_level:
        element_dict = generate_multi_level_sankey_elements(query_result=query_result,
                                                            metric_dict=metric_dict,
                                                            cluster_type=cluster_type,
                                                            building_metadata=building_metadata,
                                                            is_building=is_building,
                                                            color_dict=color_dict
                                                            )

    else:
        element_dict = generate_sankey_elements(query_result=query_result,
                                                metric_dict=metric_dict,
                                                building_metadata=building_metadata,
                                                cluster_type=cluster_type,
                                                color_dict=color_dict,
                                                )

    sankey_data = go.Sankey(
            valuesuffix=" kWh",
            node=dict(
                pad=15,
                thickness=20,

                line=dict(color="black", width=0.5),
                label=element_dict['labels_display'],
                color=element_dict['color_nodes'],
                customdata=element_dict['normalized_values'],
                hovertemplate=(' Total energy = %{value}<br />'
                               ' EUI = %{customdata} kWh/m2')
            ),
            link=dict(
                source=element_dict['sources'],  # indices correspond to labels, eg A1, A2, A2, B1, ...
                target=element_dict['targets'],
                value=element_dict['values'],
                color=element_dict['color_links']
            )
        )

    return sankey_data


def generate_sankey_figure(sankey_data):

    sankey_figure = go.Figure(data=[sankey_data])
    sankey_figure.update_layout(margin=dict(l=10, r=100, b=30, t=0, pad=0))

    return sankey_figure

