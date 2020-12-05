import pandas as pd
import plotly.graph_objects as go
import numpy as np
import utilities


def generate_sankey_elements(query_result, metric_dict,
                             building_metadata, cluster_type,
                             color_dict):
    # Initialize lists
    cluster_list = building_metadata[cluster_type].unique()
    metric_list = metric_dict['ref']
    element_dict = {'labels': np.append(metric_list, cluster_list),
                    'labels_display': np.append(metric_dict['label'], cluster_list),
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
        element_dict['color_nodes'].append(color_dict['node']['Others'])

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
                                         color_dict):

    building_list = building_metadata.building
    cluster_list = building_metadata[cluster_type].unique()
    building_long_name = building_metadata.long_name
    metric_list = metric_dict['ref']

    element_dict = {'labels': np.concatenate((metric_list,
                                              cluster_list,
                                              building_list), axis=None),
                    'labels_display': np.concatenate((metric_dict['label'],
                                                      cluster_list,
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

                element_dict['values'].\
                    append(temp_df.sum(axis=1)[0])
                element_dict['color_links'].\
                    append(color_dict['link'][metric])

                # Add the values for the individual building
                for col in temp_df.columns:
                    element_dict['sources'].\
                        append(np.where(element_dict['labels'] == cluster)[0][0])
                    element_dict['targets'].\
                        append(np.where(element_dict['labels'] == col)[0][0])
                    element_dict['values'].append(temp_df[col][0])

                    element_dict['color_links'].append(color_dict['link'][metric])

    for i in range(len(element_dict['labels'])-3):
        element_dict['color_nodes'].append(color_dict['node']['Others'])

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        indices = [j for j, x in enumerate(element_dict['targets']) if x == i]
        if element in metric_list:
            normalized_value = 'N/A'
        elif element in cluster_list:
            area = element_dict['element_area'][element]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)
        else:
            area = building_metadata.loc[
                building_metadata.building == element, 'area'].iloc[0]
            value = np.sum(np.array(element_dict['values'])[indices])
            normalized_value = round(value/area, 2)
        element_dict['normalized_values'].append(normalized_value)

    return element_dict


def generate_sankey_building_elements(query_result,
                                      metric_dict,
                                      building_metadata,
                                      color_dict):

    building_list = building_metadata.building.unique()
    building_long_name = building_metadata.long_name.unique()
    metric_list = metric_dict['ref']

    # Initialize lists
    element_dict = {'labels': np.append(metric_list, building_list),
                    'labels_display': np.append(metric_dict['label'],
                                                building_long_name),
                    'sources': [],
                    'targets': [],
                    'values': [],
                    'normalized_values': [],
                    'color_nodes': [],
                    'color_links': []}

    for metric in metric_list:
        element_dict['color_nodes'].append(color_dict['node'][metric])

        for building in building_list:

            temp_df = (query_result[metric].loc[:,
                       query_result[metric].columns == building])

            if len(temp_df) > 0:
                element_dict['values'].append(temp_df.sum(axis=1)[0])

                element_dict['sources'].append(np.where(
                    element_dict['labels'] == metric)[0][0])

                element_dict['targets'].append(np.where(
                    element_dict['labels'] == building)[0][0])

                element_dict['color_links'].append(color_dict['link'][metric])
    for i in range(len(element_dict['labels'])-3):
        element_dict['color_nodes'].append(color_dict['node']['Others'])

    for i in range(len(element_dict['labels'])):
        element = element_dict['labels'][i]
        indices = [j for j, x in enumerate(element_dict['targets']) if x == i]
        if element in metric_list:
            normalized_value = 'N/A'
        else:
            area = building_metadata.loc[building_metadata.building == element,
                                         'area'].iloc[0]
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


def generate_sankey(query_result, metric_dict,
                    building_metadata, color_dict,
                    cluster_type='building_type_mod',
                    is_multi_level=True,
                    is_building=False,):

    if is_multi_level:
        element_dict = generate_multi_level_sankey_elements(query_result=query_result,
                                                            metric_dict=metric_dict,
                                                            cluster_type=cluster_type,
                                                            building_metadata=building_metadata,
                                                            color_dict=color_dict
                                                            )
    elif is_building:
        element_dict = generate_sankey_building_elements(query_result=query_result,
                                                         metric_dict=metric_dict,
                                                         building_metadata=building_metadata,
                                                         color_dict=color_dict)
    else:
        element_dict = generate_sankey_elements(query_result=query_result,
                                                metric_dict=metric_dict,
                                                building_metadata=building_metadata,
                                                cluster_type=cluster_type,
                                                color_dict=color_dict,
                                                )

    sankey_figure = go.Figure(
        data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=element_dict['labels_display'],
                color=element_dict['color_nodes'],
                customdata=element_dict['normalized_values'],
                hovertemplate=' %{label} total = %{customdata} kWh/m2'
            ),
            link=dict(
                source=element_dict['sources'],  # indices correspond to labels, eg A1, A2, A2, B1, ...
                target=element_dict['targets'],
                value=element_dict['values'],
                color=element_dict['color_links']
            )
        )]
    )

    return sankey_figure
